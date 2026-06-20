import csv
import json
import os
import sys
import time
from datetime import datetime, timezone
from decimal import Decimal, getcontext
from itertools import count

import requests
from web3 import Web3

try:
    from eth_abi import decode
except Exception:
    from eth_abi import decode_abi as decode

getcontext().prec = 80

INPUT_WALLETS_CSV = "step9b_selected_wallets.csv"
OUTPUT_DIR = "step9b_outputs_asset_transfers"

CTF_CONTRACT = Web3.to_checksum_address("0x4D97DCd97eC945f40cF65F87097ACe5EA0476045")
ZERO_ADDRESS = "0x0000000000000000000000000000000000000000"

# These are the blocks your prior script already resolved for 2026-06-15 00:00 UTC to 2026-06-19 00:00 UTC.
# Override with STEP9B_START_BLOCK and STEP9B_END_BLOCK if needed.
DEFAULT_START_BLOCK = 88517743
DEFAULT_END_BLOCK = 88748137

MAX_PAGES_PER_QUERY = int(os.environ.get("STEP9B_MAX_PAGES", "200"))
REQUEST_SLEEP_SECONDS = float(os.environ.get("STEP9B_SLEEP", "0.15"))
MAX_RETRIES = int(os.environ.get("STEP9B_MAX_RETRIES", "3"))
TIMEOUT_SECONDS = int(os.environ.get("STEP9B_TIMEOUT", "45"))

TRANSFER_SINGLE_SIG = Web3.keccak(text="TransferSingle(address,address,address,uint256,uint256)").hex()
TRANSFER_BATCH_SIG = Web3.keccak(text="TransferBatch(address,address,address,uint256[],uint256[])").hex()


def amount_6(raw):
    return str(Decimal(int(raw)) / Decimal(1_000_000))


def norm_hash(value):
    if hasattr(value, "hex"):
        return value.hex()
    return str(value)


def hex_block(n):
    return hex(int(n))


def parse_block_num(value):
    if value is None or value == "":
        return ""
    if isinstance(value, int):
        return value
    s = str(value)
    if s.startswith("0x"):
        return int(s, 16)
    return int(s)


def data_to_bytes(data):
    if isinstance(data, (bytes, bytearray)):
        return bytes(data)
    if hasattr(data, "hex"):
        h = data.hex()
    else:
        h = str(data)
    h = h[2:] if h.startswith("0x") else h
    return bytes.fromhex(h)


def addr_from_topic(topic):
    h = topic.hex() if hasattr(topic, "hex") else str(topic)
    h = h[2:] if h.startswith("0x") else h
    return Web3.to_checksum_address("0x" + h[-40:])


def load_wallets(path):
    wallets = []
    tx_to_wallets = {}
    original_rows = []
    with open(path, newline="", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        for row in reader:
            wallet = row.get("proxyWallet", "").strip()
            if not wallet:
                continue
            wallet = Web3.to_checksum_address(wallet)
            row["proxyWallet"] = wallet
            wallets.append(wallet)
            original_rows.append(row)
            txs = row.get("sampleRedeemTxs", "") or ""
            for tx in txs.split(";"):
                tx = tx.strip()
                if tx.startswith("0x") and len(tx) == 66:
                    tx_to_wallets.setdefault(tx.lower(), set()).add(wallet)
    wallets = sorted(set(wallets), key=lambda x: x.lower())
    tx_to_wallets = {k: sorted(v, key=lambda x: x.lower()) for k, v in tx_to_wallets.items()}
    return wallets, tx_to_wallets, original_rows


def rpc_url():
    url = "https://polygon-mainnet.g.alchemy.com/v2/mmmIb7Xl00MQ4ZTp6g3A_"
    if not url:
        raise RuntimeError("Missing POLYGON_RPC_URL environment variable.")
    return url


def rpc_call(url, method, params):
    payload = {"jsonrpc": "2.0", "id": 1, "method": method, "params": params}
    last_error = None
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            r = requests.post(url, json=payload, timeout=TIMEOUT_SECONDS)
            if r.status_code in (429, 500, 502, 503, 504):
                last_error = f"HTTP {r.status_code}: {r.text[:500]}"
                time.sleep(min(12, 2 * attempt))
                continue
            r.raise_for_status()
            data = r.json()
            if "error" in data:
                # Do not hammer Alchemy on invalid request errors.
                raise RuntimeError(json.dumps(data["error"], ensure_ascii=False))
            return data.get("result")
        except Exception as e:
            last_error = repr(e)
            if attempt >= MAX_RETRIES:
                raise
            time.sleep(min(12, 2 * attempt))
    raise RuntimeError(last_error or "Unknown RPC error")


def query_asset_transfers(url, wallet, direction, start_block, end_block, failed_queries):
    rows = []
    page_key = None
    page_count = 0

    while True:
        page_count += 1
        if page_count > MAX_PAGES_PER_QUERY:
            failed_queries.append({
                "contextWallet": wallet,
                "direction": direction,
                "fromBlock": start_block,
                "toBlock": end_block,
                "error": f"Stopped after {MAX_PAGES_PER_QUERY} pages. Increase STEP9B_MAX_PAGES only if needed.",
            })
            break

        params = {
            "fromBlock": hex_block(start_block),
            "toBlock": hex_block(end_block),
            "category": ["erc1155"],
            "contractAddresses": [CTF_CONTRACT],
            "withMetadata": True,
            "excludeZeroValue": False,
            "maxCount": "0x3e8",
            "order": "asc",
        }
        if direction == "in":
            params["toAddress"] = wallet
        elif direction == "out":
            params["fromAddress"] = wallet
        else:
            raise ValueError("direction must be in or out")
        if page_key:
            params["pageKey"] = page_key

        try:
            result = rpc_call(url, "alchemy_getAssetTransfers", [params])
        except Exception as e:
            failed_queries.append({
                "contextWallet": wallet,
                "direction": direction,
                "fromBlock": start_block,
                "toBlock": end_block,
                "error": repr(e),
            })
            break

        transfers = result.get("transfers", []) if isinstance(result, dict) else []
        for t in transfers:
            base = {
                "source": "alchemy_getAssetTransfers",
                "contextWallet": wallet,
                "matchedDirection": direction,
                "txHash": t.get("hash", ""),
                "blockNumber": parse_block_num(t.get("blockNum", "")),
                "blockTimestampUTC": ((t.get("metadata") or {}).get("blockTimestamp") or ""),
                "from": Web3.to_checksum_address(t.get("from")) if t.get("from") else "",
                "to": Web3.to_checksum_address(t.get("to")) if t.get("to") else "",
                "contractAddress": Web3.to_checksum_address(((t.get("rawContract") or {}).get("address") or CTF_CONTRACT)),
                "asset": t.get("asset", ""),
                "category": t.get("category", ""),
                "uniqueId": t.get("uniqueId", ""),
            }

            meta = t.get("erc1155Metadata") or []
            if isinstance(meta, list) and meta:
                for i, item in enumerate(meta):
                    token_id = item.get("tokenId", "")
                    value = item.get("value", "0")
                    raw = int(value, 16) if isinstance(value, str) and value.startswith("0x") else int(value or 0)
                    token_dec = int(token_id, 16) if isinstance(token_id, str) and token_id.startswith("0x") else token_id
                    rows.append({
                        **base,
                        "batchIndex": i,
                        "tokenId": str(token_dec),
                        "rawAmount": str(raw),
                        "amountAssuming6Decimals": amount_6(raw),
                    })
            else:
                raw_contract = t.get("rawContract") or {}
                token_id = raw_contract.get("tokenId", "") or t.get("tokenId", "")
                value = raw_contract.get("value", "0") or t.get("value", "0")
                try:
                    raw = int(value, 16) if isinstance(value, str) and value.startswith("0x") else int(Decimal(str(value or 0)))
                except Exception:
                    raw = 0
                token_dec = int(token_id, 16) if isinstance(token_id, str) and token_id.startswith("0x") else token_id
                rows.append({
                    **base,
                    "batchIndex": 0,
                    "tokenId": str(token_dec),
                    "rawAmount": str(raw),
                    "amountAssuming6Decimals": amount_6(raw),
                })

        page_key = result.get("pageKey") if isinstance(result, dict) else None
        if not page_key:
            break
        time.sleep(REQUEST_SLEEP_SECONDS)

    return rows


def connect_web3(url):
    w3 = Web3(Web3.HTTPProvider(url, request_kwargs={"timeout": TIMEOUT_SECONDS}))
    try:
        from web3.middleware import ExtraDataToPOAMiddleware
        w3.middleware_onion.inject(ExtraDataToPOAMiddleware, layer=0)
    except Exception:
        try:
            from web3.middleware import geth_poa_middleware
            w3.middleware_onion.inject(geth_poa_middleware, layer=0)
        except Exception:
            pass
    return w3


def decode_erc1155_log(log):
    topics = log.get("topics", [])
    if not topics:
        return []
    sig = topics[0].hex() if hasattr(topics[0], "hex") else str(topics[0])
    tx_hash = norm_hash(log.get("transactionHash", ""))
    rows = []

    if sig.lower() == TRANSFER_SINGLE_SIG.lower():
        operator = addr_from_topic(topics[1])
        from_addr = addr_from_topic(topics[2])
        to_addr = addr_from_topic(topics[3])
        token_id, value = decode(["uint256", "uint256"], data_to_bytes(log.get("data", b"")))
        rows.append({
            "txHash": tx_hash,
            "blockNumber": int(log.get("blockNumber")),
            "logIndex": int(log.get("logIndex")),
            "batchIndex": 0,
            "eventType": "TransferSingle",
            "operator": operator,
            "from": from_addr,
            "to": to_addr,
            "tokenId": str(int(token_id)),
            "rawAmount": str(int(value)),
            "amountAssuming6Decimals": amount_6(value),
        })

    elif sig.lower() == TRANSFER_BATCH_SIG.lower():
        operator = addr_from_topic(topics[1])
        from_addr = addr_from_topic(topics[2])
        to_addr = addr_from_topic(topics[3])
        ids, values = decode(["uint256[]", "uint256[]"], data_to_bytes(log.get("data", b"")))
        for i, (token_id, value) in enumerate(zip(ids, values)):
            rows.append({
                "txHash": tx_hash,
                "blockNumber": int(log.get("blockNumber")),
                "logIndex": int(log.get("logIndex")),
                "batchIndex": i,
                "eventType": "TransferBatch",
                "operator": operator,
                "from": from_addr,
                "to": to_addr,
                "tokenId": str(int(token_id)),
                "rawAmount": str(int(value)),
                "amountAssuming6Decimals": amount_6(value),
            })
    return rows


def add_timestamp(w3, rows, block_cache):
    for row in rows:
        block_number = int(row["blockNumber"])
        if block_number not in block_cache:
            block_cache[block_number] = int(w3.eth.get_block(block_number)["timestamp"])
        row["blockTimestampUTC"] = datetime.fromtimestamp(block_cache[block_number], tz=timezone.utc).isoformat()
    return rows


def fetch_redeem_receipts(w3, tx_to_wallets, ctf_contract):
    receipt_rows = []
    failed = []
    block_cache = {}
    ctf_lower = ctf_contract.lower()
    for i, tx_hash in enumerate(sorted(tx_to_wallets), 1):
        print(f"Fetching redemption receipt {i}/{len(tx_to_wallets)}: {tx_hash}")
        try:
            receipt = w3.eth.get_transaction_receipt(tx_hash)
        except Exception as e:
            failed.append({"txHash": tx_hash, "error": repr(e)})
            continue
        activity_wallets = ";".join(tx_to_wallets.get(tx_hash.lower(), []))
        for log in receipt.get("logs", []):
            if str(log.get("address", "")).lower() != ctf_lower:
                continue
            decoded_rows = decode_erc1155_log(log)
            decoded_rows = add_timestamp(w3, decoded_rows, block_cache)
            for row in decoded_rows:
                row["activityWallet"] = activity_wallets
                row["source"] = "sample_redeem_receipt"
                receipt_rows.append(row)
    return receipt_rows, failed


def write_csv(path, rows, fieldnames):
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        for row in rows:
            writer.writerow(row)


def summarize_wallet_token_flows(rows, wallets):
    groups = {}
    for row in rows:
        wallet = row.get("contextWallet", "")
        token_id = row.get("tokenId", "")
        key = (wallet, token_id)
        g = groups.setdefault(key, {
            "contextWallet": wallet,
            "tokenId": token_id,
            "incomingRaw": 0,
            "outgoingRaw": 0,
            "directBurnRaw": 0,
            "directMintRaw": 0,
            "incomingRows": 0,
            "outgoingRows": 0,
            "directBurnRows": 0,
            "directMintRows": 0,
            "firstSeenUTC": "",
            "lastSeenUTC": "",
            "sampleTxs": [],
        })
        raw = int(row.get("rawAmount") or 0)
        from_addr = row.get("from", "").lower()
        to_addr = row.get("to", "").lower()
        wl = wallet.lower()
        ts = row.get("blockTimestampUTC", "")
        if ts:
            if not g["firstSeenUTC"] or ts < g["firstSeenUTC"]:
                g["firstSeenUTC"] = ts
            if not g["lastSeenUTC"] or ts > g["lastSeenUTC"]:
                g["lastSeenUTC"] = ts
        tx = row.get("txHash", "")
        if tx and tx not in g["sampleTxs"] and len(g["sampleTxs"]) < 5:
            g["sampleTxs"].append(tx)
        if to_addr == wl:
            g["incomingRaw"] += raw
            g["incomingRows"] += 1
            if from_addr == ZERO_ADDRESS.lower():
                g["directMintRaw"] += raw
                g["directMintRows"] += 1
        if from_addr == wl:
            g["outgoingRaw"] += raw
            g["outgoingRows"] += 1
            if to_addr == ZERO_ADDRESS.lower():
                g["directBurnRaw"] += raw
                g["directBurnRows"] += 1

    out = []
    for g in groups.values():
        net = g["incomingRaw"] - g["outgoingRaw"]
        labels = []
        if g["incomingRows"]:
            labels.append("received")
        if g["outgoingRows"]:
            labels.append("sent_or_redeemed")
        if g["directBurnRows"]:
            labels.append("direct_burn")
        if g["directMintRows"]:
            labels.append("direct_mint")
        if not labels:
            labels.append("no_wallet_side_flow")
        out.append({
            "contextWallet": g["contextWallet"],
            "tokenId": g["tokenId"],
            "incomingRaw": str(g["incomingRaw"]),
            "incomingAssuming6Decimals": amount_6(g["incomingRaw"]),
            "outgoingRaw": str(g["outgoingRaw"]),
            "outgoingAssuming6Decimals": amount_6(g["outgoingRaw"]),
            "directBurnRaw": str(g["directBurnRaw"]),
            "directBurnAssuming6Decimals": amount_6(g["directBurnRaw"]),
            "directMintRaw": str(g["directMintRaw"]),
            "directMintAssuming6Decimals": amount_6(g["directMintRaw"]),
            "netRaw": str(net),
            "netAssuming6Decimals": amount_6(net),
            "incomingRows": g["incomingRows"],
            "outgoingRows": g["outgoingRows"],
            "directBurnRows": g["directBurnRows"],
            "directMintRows": g["directMintRows"],
            "firstSeenUTC": g["firstSeenUTC"],
            "lastSeenUTC": g["lastSeenUTC"],
            "flowLabel": ";".join(labels),
            "sampleTxs": "; ".join(g["sampleTxs"]),
        })
    out.sort(key=lambda r: (r["contextWallet"].lower(), r["tokenId"]))
    return out


def summarize_counterparties(rows):
    groups = {}
    for row in rows:
        wallet = row.get("contextWallet", "")
        wl = wallet.lower()
        from_addr = row.get("from", "")
        to_addr = row.get("to", "")
        raw = int(row.get("rawAmount") or 0)
        if to_addr.lower() == wl:
            direction = "in"
            counterparty = from_addr
        elif from_addr.lower() == wl:
            direction = "out"
            counterparty = to_addr
        else:
            continue
        key = (wallet, row.get("tokenId", ""), direction, counterparty)
        g = groups.setdefault(key, {
            "contextWallet": wallet,
            "tokenId": row.get("tokenId", ""),
            "direction": direction,
            "counterparty": counterparty,
            "totalRaw": 0,
            "rows": 0,
            "firstUTC": "",
            "lastUTC": "",
            "sampleTxs": [],
        })
        g["totalRaw"] += raw
        g["rows"] += 1
        ts = row.get("blockTimestampUTC", "")
        if ts:
            if not g["firstUTC"] or ts < g["firstUTC"]:
                g["firstUTC"] = ts
            if not g["lastUTC"] or ts > g["lastUTC"]:
                g["lastUTC"] = ts
        tx = row.get("txHash", "")
        if tx and tx not in g["sampleTxs"] and len(g["sampleTxs"]) < 5:
            g["sampleTxs"].append(tx)
    out = []
    for g in groups.values():
        out.append({
            "contextWallet": g["contextWallet"],
            "tokenId": g["tokenId"],
            "direction": g["direction"],
            "counterparty": g["counterparty"],
            "totalRaw": str(g["totalRaw"]),
            "totalAssuming6Decimals": amount_6(g["totalRaw"]),
            "rows": g["rows"],
            "firstUTC": g["firstUTC"],
            "lastUTC": g["lastUTC"],
            "sampleTxs": "; ".join(g["sampleTxs"]),
        })
    out.sort(key=lambda r: (r["contextWallet"].lower(), r["tokenId"], r["direction"], r["counterparty"].lower()))
    return out


def incoming_nonzero_edges(rows):
    out = []
    for row in rows:
        wallet = row.get("contextWallet", "")
        if row.get("to", "").lower() == wallet.lower() and row.get("from", "").lower() != ZERO_ADDRESS.lower():
            r = dict(row)
            r["reviewNote"] = "Selected wallet received ERC1155 tokens from a nonzero address. Review as possible token source before redemption."
            out.append(r)
    out.sort(key=lambda r: (r.get("contextWallet", "").lower(), int(r.get("blockNumber") or 0), r.get("txHash", ""), int(r.get("batchIndex") or 0)))
    return out


def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    input_path = os.path.join(script_dir, INPUT_WALLETS_CSV)
    output_dir = os.path.join(script_dir, OUTPUT_DIR)
    os.makedirs(output_dir, exist_ok=True)

    if not os.path.exists(input_path):
        raise FileNotFoundError(f"Missing input wallet file: {input_path}")

    url = rpc_url()
    wallets, tx_to_wallets, original_rows = load_wallets(input_path)
    if not wallets:
        raise RuntimeError("No wallets found in input file.")

    start_block = int(os.environ.get("STEP9B_START_BLOCK", str(DEFAULT_START_BLOCK)))
    end_block = int(os.environ.get("STEP9B_END_BLOCK", str(DEFAULT_END_BLOCK)))

    print("Step 9B safe mode: using alchemy_getAssetTransfers instead of eth_getLogs.")
    print(f"CTF contract: {CTF_CONTRACT}")
    print(f"Block range: {start_block} to {end_block}")
    print(f"Selected wallets: {len(wallets)}")
    print(f"Sample redemption transactions: {len(tx_to_wallets)}")

    failed_queries = []
    transfer_rows = []
    for i, wallet in enumerate(wallets, 1):
        print(f"Wallet {i}/{len(wallets)} incoming transfers: {wallet}")
        transfer_rows.extend(query_asset_transfers(url, wallet, "in", start_block, end_block, failed_queries))
        time.sleep(REQUEST_SLEEP_SECONDS)
        print(f"Wallet {i}/{len(wallets)} outgoing transfers: {wallet}")
        transfer_rows.extend(query_asset_transfers(url, wallet, "out", start_block, end_block, failed_queries))
        time.sleep(REQUEST_SLEEP_SECONDS)

    w3 = connect_web3(url)
    receipt_rows, failed_receipts = fetch_redeem_receipts(w3, tx_to_wallets, CTF_CONTRACT)

    transfer_fields = [
        "source", "contextWallet", "matchedDirection", "txHash", "blockNumber", "blockTimestampUTC", "batchIndex", "from", "to", "contractAddress", "tokenId", "rawAmount", "amountAssuming6Decimals", "asset", "category", "uniqueId"
    ]
    receipt_fields = [
        "source", "activityWallet", "txHash", "blockNumber", "blockTimestampUTC", "logIndex", "batchIndex", "eventType", "operator", "from", "to", "tokenId", "rawAmount", "amountAssuming6Decimals"
    ]
    flow_fields = [
        "contextWallet", "tokenId", "incomingRaw", "incomingAssuming6Decimals", "outgoingRaw", "outgoingAssuming6Decimals", "directBurnRaw", "directBurnAssuming6Decimals", "directMintRaw", "directMintAssuming6Decimals", "netRaw", "netAssuming6Decimals", "incomingRows", "outgoingRows", "directBurnRows", "directMintRows", "firstSeenUTC", "lastSeenUTC", "flowLabel", "sampleTxs"
    ]
    counterparty_fields = ["contextWallet", "tokenId", "direction", "counterparty", "totalRaw", "totalAssuming6Decimals", "rows", "firstUTC", "lastUTC", "sampleTxs"]

    flow_summary = summarize_wallet_token_flows(transfer_rows, wallets)
    counterparty_summary = summarize_counterparties(transfer_rows)
    source_edges = incoming_nonzero_edges(transfer_rows)

    write_csv(os.path.join(output_dir, "01_step9b_alchemy_asset_transfers.csv"), transfer_rows, transfer_fields)
    write_csv(os.path.join(output_dir, "02_step9b_redeem_receipt_erc1155_logs.csv"), receipt_rows, receipt_fields)
    write_csv(os.path.join(output_dir, "03_step9b_wallet_token_flow_summary.csv"), flow_summary, flow_fields)
    write_csv(os.path.join(output_dir, "04_step9b_counterparty_summary.csv"), counterparty_summary, counterparty_fields)
    write_csv(os.path.join(output_dir, "05_step9b_incoming_nonzero_edges_for_review.csv"), source_edges, transfer_fields + ["reviewNote"])
    write_csv(os.path.join(output_dir, "98_step9b_failed_asset_transfer_queries.csv"), failed_queries, ["contextWallet", "direction", "fromBlock", "toBlock", "error"])
    write_csv(os.path.join(output_dir, "99_step9b_failed_receipts.csv"), failed_receipts, ["txHash", "error"])

    with open(os.path.join(output_dir, "00_step9b_run_summary.txt"), "w", encoding="utf-8") as f:
        f.write("Step 9B safe ERC1155 transfer trace using alchemy_getAssetTransfers\n")
        f.write(f"Collected at UTC: {datetime.now(timezone.utc).isoformat()}\n")
        f.write(f"CTF contract: {CTF_CONTRACT}\n")
        f.write(f"Start block: {start_block}\n")
        f.write(f"End block: {end_block}\n")
        f.write(f"Selected wallets: {len(wallets)}\n")
        f.write(f"Asset transfer rows: {len(transfer_rows)}\n")
        f.write(f"Redemption receipt decoded ERC1155 rows: {len(receipt_rows)}\n")
        f.write(f"Wallet token flow summary rows: {len(flow_summary)}\n")
        f.write(f"Counterparty summary rows: {len(counterparty_summary)}\n")
        f.write(f"Incoming nonzero edges for review: {len(source_edges)}\n")
        f.write(f"Failed asset transfer queries: {len(failed_queries)}\n")
        f.write(f"Failed redemption receipts: {len(failed_receipts)}\n")
        f.write("\nInterpretation guide:\n")
        f.write("This version avoids eth_getLogs and uses Alchemy's indexed asset transfer endpoint.\n")
        f.write("The incoming nonzero edge file is the first file to review for possible token source wallets before redemption.\n")
        f.write("The redemption receipt file decodes CTF logs inside known redemption transactions, including adapter flows.\n")
        f.write("Amounts assuming 6 decimals are helper values. Preserve rawAmount for evidence.\n")

    print("Done. Outputs written to:", output_dir)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("Stopped by user.")
        sys.exit(130)
    except Exception as e:
        print("ERROR:", repr(e))
        sys.exit(1)
