import csv
import hashlib
import json
import os
import time
from datetime import datetime, timezone

import pandas as pd
from web3 import Web3
from web3.middleware import ExtraDataToPOAMiddleware


POLYGON_RPC_URL = "https://polygon-mainnet.g.alchemy.com/v2/mmmIb7Xl00MQ4ZTp6g3A_"

ALL_RELATED_YES_BUYERS_CSV = "03_all_related_market_yes_buyers.csv"
CROSS_MARKET_WALLET_SUMMARY_CSV = "04_cross_market_wallet_summary.csv"

STEP8_ACTIVITY_FILES = [
    "04_user_activity_normalized.csv",
    "07_redeems_splits_merges.csv",
    "04_future_market_activity_normalized.csv",
    "06_future_redeems_splits_merges_v2.csv",
]

STEP9_SELECTED_WALLETS_CSV = "01_selected_wallets.csv"
STEP9_WALLET_MARKET_SUMMARY_CSV = "05_wallet_market_transfer_summary.csv"

OUTPUT_DIR = "step10_redemption_outputs"

CTF_CONTRACT = "0x4D97DCd97eC945f40cF65F87097ACe5EA0476045"

FINAL_SETTLEMENT_UTC = "2026-06-18T00:32:19+00:00"

VALUE_DECIMALS_ASSUMPTION = 6

REDEEM_ACTIVITY_ROWS_CSV = os.path.join(OUTPUT_DIR, "01_redeem_activity_rows.csv")
REDEEM_TXS_CSV = os.path.join(OUTPUT_DIR, "02_redeem_transactions_to_check.csv")
RAW_RECEIPTS_JSON = os.path.join(OUTPUT_DIR, "03_redeem_receipts_raw.json")
ERC1155_REDEEM_LOGS_CSV = os.path.join(OUTPUT_DIR, "04_redeem_erc1155_logs.csv")
ERC20_TRANSFER_LOGS_CSV = os.path.join(OUTPUT_DIR, "05_redeem_erc20_transfer_logs.csv")
WALLET_REDEEM_SUMMARY_CSV = os.path.join(OUTPUT_DIR, "06_wallet_redeem_summary.csv")
SUMMARY_TXT = os.path.join(OUTPUT_DIR, "07_step10_redemption_summary.txt")
HASHES_CSV = os.path.join(OUTPUT_DIR, "08_step10_file_hashes.csv")


ZERO_ADDRESS = "0x0000000000000000000000000000000000000000"

ERC1155_ABI = [
    {
        "anonymous": False,
        "inputs": [
            {"indexed": True, "internalType": "address", "name": "operator", "type": "address"},
            {"indexed": True, "internalType": "address", "name": "from", "type": "address"},
            {"indexed": True, "internalType": "address", "name": "to", "type": "address"},
            {"indexed": False, "internalType": "uint256", "name": "id", "type": "uint256"},
            {"indexed": False, "internalType": "uint256", "name": "value", "type": "uint256"},
        ],
        "name": "TransferSingle",
        "type": "event",
    },
    {
        "anonymous": False,
        "inputs": [
            {"indexed": True, "internalType": "address", "name": "operator", "type": "address"},
            {"indexed": True, "internalType": "address", "name": "from", "type": "address"},
            {"indexed": True, "internalType": "address", "name": "to", "type": "address"},
            {"indexed": False, "internalType": "uint256[]", "name": "ids", "type": "uint256[]"},
            {"indexed": False, "internalType": "uint256[]", "name": "values", "type": "uint256[]"},
        ],
        "name": "TransferBatch",
        "type": "event",
    },
]


ERC20_TRANSFER_TOPIC = Web3.to_hex(
    Web3.keccak(text="Transfer(address,address,uint256)")
).lower()


def ensure_output_dir():
    os.makedirs(OUTPUT_DIR, exist_ok=True)


def normalize_0x(value):
    if value is None:
        return ""

    value = str(value).strip().lower()

    if not value:
        return ""

    if not value.startswith("0x"):
        value = "0x" + value

    return value


def valid_wallet(value):
    value = normalize_0x(value)
    return len(value) == 42


def valid_tx(value):
    value = normalize_0x(value)
    return len(value) == 66


def safe_float(value):
    try:
        return float(value or 0)
    except Exception:
        return 0.0


def parse_iso_to_ts(value):
    return int(datetime.fromisoformat(value).timestamp())


def timestamp_to_iso(ts):
    return datetime.fromtimestamp(int(ts), tz=timezone.utc).isoformat()


def event_hash(value):
    if hasattr(value, "hex"):
        result = value.hex()
        if result.startswith("0x"):
            return result
        return "0x" + result

    return str(value)


def topic_to_address(topic):
    topic = event_hash(topic).lower()

    if not topic.startswith("0x"):
        topic = "0x" + topic

    return "0x" + topic[-40:]


def topic_to_int(topic):
    return int(event_hash(topic), 16)


def sha256_file(path):
    h = hashlib.sha256()

    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)

    return h.hexdigest()


def write_csv(path, rows, fieldnames=None):
    if fieldnames is None:
        if rows:
            fieldnames = list(rows[0].keys())
        else:
            fieldnames = ["empty"]

    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()

        for row in rows:
            writer.writerow(row)


def load_selected_wallets():
    wallets = {}

    if os.path.exists(STEP9_SELECTED_WALLETS_CSV):
        df = pd.read_csv(STEP9_SELECTED_WALLETS_CSV)

        for _, row in df.iterrows():
            wallet = normalize_0x(row.get("proxyWallet", "") or row.get("wallet", ""))

            if valid_wallet(wallet):
                wallets[wallet] = {
                    "proxyWallet": wallet,
                    "pattern": row.get("pattern", ""),
                    "source": "Step 9 selected wallets",
                }

    if wallets:
        return wallets

    df = pd.read_csv(CROSS_MARKET_WALLET_SUMMARY_CSV)

    for _, row in df.iterrows():
        wallet = normalize_0x(row.get("proxyWallet", ""))

        if not valid_wallet(wallet):
            continue

        pattern = str(row.get("pattern", ""))

        if pattern not in [
            "BOUGHT_TARGET_AND_FUTURE_MARKETS",
            "BOUGHT_FUTURE_MARKETS_ONLY",
        ]:
            continue

        wallets[wallet] = {
            "proxyWallet": wallet,
            "pattern": pattern,
            "source": "Cross-market wallet summary",
        }

    return wallets


def load_market_token_context():
    df = pd.read_csv(ALL_RELATED_YES_BUYERS_CSV)

    token_context = {}

    for _, row in df.iterrows():
        yes_token_id = str(row.get("yesTokenId", "")).strip()

        if not yes_token_id:
            continue

        token_context[yes_token_id] = {
            "conditionId": normalize_0x(row.get("conditionId", "")),
            "marketRelationType": row.get("marketRelationType", ""),
            "marketQuestion": row.get("marketQuestion", ""),
            "marketSlug": row.get("marketSlug", ""),
            "marketEndDate": row.get("marketEndDate", ""),
            "tokenSide": "YES",
        }

    return token_context


def load_redeem_activity_rows(selected_wallets):
    selected = set(selected_wallets.keys())
    rows = []
    seen = set()

    for path in STEP8_ACTIVITY_FILES:
        if not os.path.exists(path):
            continue

        df = pd.read_csv(path)

        if "type" not in df.columns:
            continue

        for _, row in df.iterrows():
            activity_type = str(row.get("type", "")).strip().upper()

            if activity_type != "REDEEM":
                continue

            wallet = normalize_0x(row.get("proxyWallet", "") or row.get("queriedWallet", ""))

            if wallet not in selected:
                continue

            tx_hash = normalize_0x(row.get("transactionHash", ""))

            if not valid_tx(tx_hash):
                continue

            key = (
                wallet,
                tx_hash,
                str(row.get("conditionId", "")),
                str(row.get("timestamp", "")),
                str(row.get("size", "")),
            )

            if key in seen:
                continue

            seen.add(key)

            rows.append({
                "proxyWallet": wallet,
                "walletPattern": selected_wallets[wallet].get("pattern", ""),
                "sourceFile": path,
                "transactionHash": tx_hash,
                "conditionId": normalize_0x(row.get("conditionId", "")),
                "activityTimeUTC": row.get("activityTimeUTC", ""),
                "timestamp": row.get("timestamp", ""),
                "deadlineBucket": row.get("deadlineBucket", ""),
                "type": activity_type,
                "size": row.get("size", ""),
                "usdcSize": row.get("usdcSize", ""),
                "price": row.get("price", ""),
                "outcome": row.get("outcome", ""),
                "asset": row.get("asset", ""),
                "marketRelationType": row.get("marketRelationType", ""),
                "marketQuestion": row.get("marketQuestion", ""),
                "marketSlug": row.get("marketSlug", ""),
                "name": row.get("name", ""),
                "pseudonym": row.get("pseudonym", ""),
            })

    rows.sort(key=lambda r: (r["activityTimeUTC"], r["proxyWallet"]))

    return rows


def receipt_to_jsonable(receipt):
    output = {}

    for key, value in dict(receipt).items():
        if key == "logs":
            output["logs"] = []
            for log in value:
                output["logs"].append({
                    "address": log["address"],
                    "topics": [event_hash(t) for t in log["topics"]],
                    "data": event_hash(log["data"]),
                    "blockNumber": int(log["blockNumber"]),
                    "transactionHash": event_hash(log["transactionHash"]),
                    "transactionIndex": int(log["transactionIndex"]),
                    "blockHash": event_hash(log["blockHash"]),
                    "logIndex": int(log["logIndex"]),
                    "removed": bool(log.get("removed", False)),
                })
        else:
            if hasattr(value, "hex"):
                output[key] = event_hash(value)
            elif isinstance(value, int):
                output[key] = value
            else:
                output[key] = str(value)

    return output


def get_receipt_with_retry(w3, tx_hash):
    for attempt in range(1, 8):
        try:
            return w3.eth.get_transaction_receipt(tx_hash)
        except Exception as e:
            error_text = repr(e)

            print("")
            print("Receipt request failed.")
            print("tx:", tx_hash)
            print("attempt:", attempt, "of 7")
            print("error:", error_text)

            if "429" in error_text or "rate" in error_text.lower():
                time.sleep(min(10 * attempt, 60))
                continue

            if "503" in error_text or "Service Unavailable" in error_text:
                time.sleep(min(5 * attempt, 30))
                continue

            time.sleep(3)

    raise RuntimeError(f"Could not fetch receipt after retries: {tx_hash}")


def get_block_time(w3, block_number, cache):
    block_number = int(block_number)

    if block_number not in cache:
        block = w3.eth.get_block(block_number)
        cache[block_number] = int(block["timestamp"])

    return cache[block_number]


def decode_erc1155_redeem_logs(w3, receipt, redeem_contexts, token_context, block_cache):
    contract = w3.eth.contract(
        address=Web3.to_checksum_address(CTF_CONTRACT),
        abi=ERC1155_ABI,
    )

    transfer_single_topic = Web3.to_hex(
        Web3.keccak(text="TransferSingle(address,address,address,uint256,uint256)")
    ).lower()

    transfer_batch_topic = Web3.to_hex(
        Web3.keccak(text="TransferBatch(address,address,address,uint256[],uint256[])")
    ).lower()

    selected_wallets = set(ctx["proxyWallet"] for ctx in redeem_contexts)

    rows = []

    for log in receipt["logs"]:
        if normalize_0x(log["address"]) != normalize_0x(CTF_CONTRACT):
            continue

        topic0 = event_hash(log["topics"][0]).lower()

        try:
            if topic0 == transfer_single_topic:
                event = contract.events.TransferSingle().process_log(log)
                args = event["args"]

                token_id = str(args["id"])
                value_raw = int(args["value"])

                if token_id not in token_context:
                    continue

                rows.append(build_erc1155_row(
                    w3,
                    event,
                    redeem_contexts,
                    token_context[token_id],
                    selected_wallets,
                    "TransferSingle",
                    token_id,
                    value_raw,
                    block_cache,
                ))

            elif topic0 == transfer_batch_topic:
                event = contract.events.TransferBatch().process_log(log)
                args = event["args"]

                ids = [str(x) for x in args["ids"]]
                values = [int(x) for x in args["values"]]

                for token_id, value_raw in zip(ids, values):
                    if token_id not in token_context:
                        continue

                    rows.append(build_erc1155_row(
                        w3,
                        event,
                        redeem_contexts,
                        token_context[token_id],
                        selected_wallets,
                        "TransferBatch",
                        token_id,
                        value_raw,
                        block_cache,
                    ))

        except Exception as e:
            print("ERC1155 decode failed:", event_hash(log.get("transactionHash", "")), log.get("logIndex", ""))
            print("error:", repr(e))

    return rows


def build_erc1155_row(w3, event, redeem_contexts, market_ctx, selected_wallets, event_type, token_id, value_raw, block_cache):
    args = event["args"]

    from_address = normalize_0x(args["from"])
    to_address = normalize_0x(args["to"])
    operator = normalize_0x(args["operator"])

    block_number = int(event["blockNumber"])
    block_ts = get_block_time(w3, block_number, block_cache)
    block_time_utc = timestamp_to_iso(block_ts)

    settlement_ts = parse_iso_to_ts(FINAL_SETTLEMENT_UTC)

    if block_ts < settlement_ts:
        settlement_bucket = "Before final settlement"
    else:
        settlement_bucket = "After final settlement"

    burn_status = "BURN_TO_ZERO_ADDRESS" if to_address == ZERO_ADDRESS else "NOT_BURN"

    selected_wallet_role = []

    if from_address in selected_wallets:
        selected_wallet_role.append("FROM_SELECTED_WALLET")

    if to_address in selected_wallets:
        selected_wallet_role.append("TO_SELECTED_WALLET")

    if operator in selected_wallets:
        selected_wallet_role.append("OPERATOR_SELECTED_WALLET")

    if not selected_wallet_role:
        selected_wallet_role.append("NO_SELECTED_WALLET_DIRECTLY_IN_THIS_LOG")

    proxy_wallets = "; ".join(sorted(set(ctx["proxyWallet"] for ctx in redeem_contexts)))

    return {
        "proxyWalletsFromRedeemActivity": proxy_wallets,
        "selectedWalletRole": "; ".join(selected_wallet_role),
        "burnStatus": burn_status,
        "from": from_address,
        "to": to_address,
        "operator": operator,
        "eventType": event_type,
        "conditionId": market_ctx.get("conditionId", ""),
        "marketRelationType": market_ctx.get("marketRelationType", ""),
        "marketQuestion": market_ctx.get("marketQuestion", ""),
        "marketSlug": market_ctx.get("marketSlug", ""),
        "tokenSide": market_ctx.get("tokenSide", ""),
        "tokenId": token_id,
        "valueRaw": str(value_raw),
        "valueAssuming6Decimals": value_raw / (10 ** VALUE_DECIMALS_ASSUMPTION),
        "blockNumber": block_number,
        "blockTimestampUTC": block_time_utc,
        "settlementBucket": settlement_bucket,
        "transactionHash": event_hash(event["transactionHash"]),
        "logIndex": int(event["logIndex"]),
    }


def decode_erc20_transfer_logs(w3, receipt, redeem_contexts, block_cache):
    selected_wallets = set(ctx["proxyWallet"] for ctx in redeem_contexts)
    rows = []

    for log in receipt["logs"]:
        topics = log["topics"]

        if len(topics) < 3:
            continue

        topic0 = event_hash(topics[0]).lower()

        if topic0 != ERC20_TRANSFER_TOPIC:
            continue

        token_contract = normalize_0x(log["address"])
        from_address = normalize_0x(topic_to_address(topics[1]))
        to_address = normalize_0x(topic_to_address(topics[2]))

        try:
            value_raw = int(event_hash(log["data"]), 16)
        except Exception:
            value_raw = 0

        if from_address not in selected_wallets and to_address not in selected_wallets:
            continue

        block_number = int(log["blockNumber"])
        block_ts = get_block_time(w3, block_number, block_cache)

        role = []

        if from_address in selected_wallets:
            role.append("FROM_SELECTED_WALLET")

        if to_address in selected_wallets:
            role.append("TO_SELECTED_WALLET")

        rows.append({
            "proxyWalletsFromRedeemActivity": "; ".join(sorted(selected_wallets)),
            "selectedWalletRole": "; ".join(role),
            "tokenContract": token_contract,
            "from": from_address,
            "to": to_address,
            "valueRaw": str(value_raw),
            "valueAssuming6Decimals": value_raw / (10 ** VALUE_DECIMALS_ASSUMPTION),
            "blockNumber": block_number,
            "blockTimestampUTC": timestamp_to_iso(block_ts),
            "transactionHash": event_hash(log["transactionHash"]),
            "logIndex": int(log["logIndex"]),
        })

    return rows


def build_wallet_redeem_summary(redeem_rows, erc1155_rows, erc20_rows):
    summary = {}

    for row in redeem_rows:
        wallet = row["proxyWallet"]

        if wallet not in summary:
            summary[wallet] = {
                "proxyWallet": wallet,
                "walletPattern": row.get("walletPattern", ""),
                "redeemActivityRows": 0,
                "redeemTxCount": set(),
                "redeemActivityUSDCSize": 0.0,
                "firstRedeemUTC": "",
                "lastRedeemUTC": "",
                "erc1155BurnRows": 0,
                "erc1155BurnAmount": 0.0,
                "erc20IncomingRows": 0,
                "erc20IncomingAmountAssuming6Decimals": 0.0,
                "sampleRedeemTxs": set(),
            }

        item = summary[wallet]

        item["redeemActivityRows"] += 1
        item["redeemTxCount"].add(row["transactionHash"])
        item["sampleRedeemTxs"].add(row["transactionHash"])
        item["redeemActivityUSDCSize"] += safe_float(row.get("usdcSize", 0))

        t = row.get("activityTimeUTC", "")

        if t and (not item["firstRedeemUTC"] or t < item["firstRedeemUTC"]):
            item["firstRedeemUTC"] = t

        if t and (not item["lastRedeemUTC"] or t > item["lastRedeemUTC"]):
            item["lastRedeemUTC"] = t

    for row in erc1155_rows:
        if row["burnStatus"] != "BURN_TO_ZERO_ADDRESS":
            continue

        wallets = row["proxyWalletsFromRedeemActivity"].split("; ")

        for wallet in wallets:
            wallet = normalize_0x(wallet)

            if wallet not in summary:
                continue

            summary[wallet]["erc1155BurnRows"] += 1
            summary[wallet]["erc1155BurnAmount"] += safe_float(row["valueAssuming6Decimals"])

    for row in erc20_rows:
        if "TO_SELECTED_WALLET" not in row["selectedWalletRole"]:
            continue

        to_wallet = normalize_0x(row["to"])

        if to_wallet not in summary:
            continue

        summary[to_wallet]["erc20IncomingRows"] += 1
        summary[to_wallet]["erc20IncomingAmountAssuming6Decimals"] += safe_float(row["valueAssuming6Decimals"])

    output = []

    for wallet, item in summary.items():
        output.append({
            "proxyWallet": wallet,
            "walletPattern": item["walletPattern"],
            "redeemActivityRows": item["redeemActivityRows"],
            "redeemTxCount": len(item["redeemTxCount"]),
            "redeemActivityUSDCSize": item["redeemActivityUSDCSize"],
            "firstRedeemUTC": item["firstRedeemUTC"],
            "lastRedeemUTC": item["lastRedeemUTC"],
            "erc1155BurnRows": item["erc1155BurnRows"],
            "erc1155BurnAmountAssuming6Decimals": item["erc1155BurnAmount"],
            "erc20IncomingRows": item["erc20IncomingRows"],
            "erc20IncomingAmountAssuming6Decimals": item["erc20IncomingAmountAssuming6Decimals"],
            "sampleRedeemTxs": "; ".join(sorted(list(item["sampleRedeemTxs"]))[:5]),
        })

    output.sort(key=lambda r: (-safe_float(r["redeemActivityUSDCSize"]), r["proxyWallet"]))

    return output


def write_hashes():
    files = [
        REDEEM_ACTIVITY_ROWS_CSV,
        REDEEM_TXS_CSV,
        RAW_RECEIPTS_JSON,
        ERC1155_REDEEM_LOGS_CSV,
        ERC20_TRANSFER_LOGS_CSV,
        WALLET_REDEEM_SUMMARY_CSV,
        SUMMARY_TXT,
    ]

    rows = []

    for path in files:
        if os.path.exists(path):
            rows.append({
                "filename": os.path.basename(path),
                "sha256": sha256_file(path),
            })

    write_csv(HASHES_CSV, rows)


def write_summary(redeem_rows, receipts_count, erc1155_rows, erc20_rows, wallet_summary):
    burn_rows = [
        row for row in erc1155_rows
        if row["burnStatus"] == "BURN_TO_ZERO_ADDRESS"
    ]

    wallets_with_redeem = set(row["proxyWallet"] for row in redeem_rows)

    lines = []

    lines.append("Step 10 Redemption Summary")
    lines.append("")
    lines.append(f"Collected at UTC: {datetime.now(timezone.utc).isoformat()}")
    lines.append(f"Redeem activity rows: {len(redeem_rows)}")
    lines.append(f"Unique redemption transaction receipts fetched: {receipts_count}")
    lines.append(f"ERC1155 redeem-related logs: {len(erc1155_rows)}")
    lines.append(f"ERC1155 burn-to-zero logs: {len(burn_rows)}")
    lines.append(f"ERC20 transfer logs involving selected wallets: {len(erc20_rows)}")
    lines.append(f"Wallet summary rows: {len(wallet_summary)}")
    lines.append(f"Wallets with redemption activity: {len(wallets_with_redeem)}")
    lines.append("")
    lines.append("Interpretation:")
    lines.append("Step 10 uses Polymarket activity rows labeled REDEEM, then fetches the underlying Polygon transaction receipts. The output checks for ERC1155 CTF token burns and ERC20 transfers involving the redeeming wallets. Redemption activity is stronger evidence of financial benefit than a trade alone.")
    lines.append("")
    lines.append("Limitation:")
    lines.append("If redemption occurs through an adapter, the ERC1155 burn may happen from the adapter address rather than directly from the proxy wallet. In that case, the activity row and transaction hash remain important, and the receipt should be reviewed as a complete transaction flow.")

    with open(SUMMARY_TXT, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))


def main():
    ensure_output_dir()

    if not POLYGON_RPC_URL:
        raise RuntimeError("Set POLYGON_RPC_URL as an environment variable first.")

    w3 = Web3(Web3.HTTPProvider(POLYGON_RPC_URL))
    w3.middleware_onion.inject(ExtraDataToPOAMiddleware, layer=0)

    if not w3.is_connected():
        raise RuntimeError("Could not connect to Polygon RPC.")

    selected_wallets = load_selected_wallets()
    token_context = load_market_token_context()

    if not selected_wallets:
        raise RuntimeError("No selected wallets loaded.")

    if not token_context:
        raise RuntimeError("No token context loaded.")

    redeem_rows = load_redeem_activity_rows(selected_wallets)

    write_csv(REDEEM_ACTIVITY_ROWS_CSV, redeem_rows)

    if not redeem_rows:
        print("No redemption activity rows found for selected wallets.")
        write_summary([], 0, [], [], [])
        write_hashes()
        return

    tx_to_contexts = {}

    for row in redeem_rows:
        tx = row["transactionHash"]
        tx_to_contexts.setdefault(tx, []).append(row)

    redeem_tx_rows = []

    for tx, rows in tx_to_contexts.items():
        redeem_tx_rows.append({
            "transactionHash": tx,
            "contextRows": len(rows),
            "proxyWallets": "; ".join(sorted(set(row["proxyWallet"] for row in rows))),
            "conditionIds": "; ".join(sorted(set(row["conditionId"] for row in rows))),
        })

    write_csv(REDEEM_TXS_CSV, redeem_tx_rows)

    raw_receipts = []
    erc1155_rows = []
    erc20_rows = []
    block_cache = {}

    print("Redemption transactions to fetch:", len(tx_to_contexts))

    for index, tx_hash in enumerate(tx_to_contexts.keys(), start=1):
        print(f"Receipt {index} of {len(tx_to_contexts)}: {tx_hash}")

        receipt = get_receipt_with_retry(w3, tx_hash)
        raw_receipts.append(receipt_to_jsonable(receipt))

        contexts = tx_to_contexts[tx_hash]

        erc1155_rows.extend(decode_erc1155_redeem_logs(
            w3,
            receipt,
            contexts,
            token_context,
            block_cache,
        ))

        erc20_rows.extend(decode_erc20_transfer_logs(
            w3,
            receipt,
            contexts,
            block_cache,
        ))

        time.sleep(0.15)

    with open(RAW_RECEIPTS_JSON, "w", encoding="utf-8") as f:
        json.dump(raw_receipts, f, indent=2, ensure_ascii=False)

    erc1155_rows.sort(key=lambda r: (r["blockNumber"], r["logIndex"]))
    erc20_rows.sort(key=lambda r: (r["blockNumber"], r["logIndex"]))

    write_csv(ERC1155_REDEEM_LOGS_CSV, erc1155_rows)
    write_csv(ERC20_TRANSFER_LOGS_CSV, erc20_rows)

    wallet_summary = build_wallet_redeem_summary(
        redeem_rows,
        erc1155_rows,
        erc20_rows,
    )

    write_csv(WALLET_REDEEM_SUMMARY_CSV, wallet_summary)

    write_summary(
        redeem_rows,
        len(tx_to_contexts),
        erc1155_rows,
        erc20_rows,
        wallet_summary,
    )

    write_hashes()

    print("")
    print("Saved outputs:")
    print(REDEEM_ACTIVITY_ROWS_CSV)
    print(REDEEM_TXS_CSV)
    print(RAW_RECEIPTS_JSON)
    print(ERC1155_REDEEM_LOGS_CSV)
    print(ERC20_TRANSFER_LOGS_CSV)
    print(WALLET_REDEEM_SUMMARY_CSV)
    print(SUMMARY_TXT)
    print(HASHES_CSV)
    print("")
    print("Done.")


if __name__ == "__main__":
    main()