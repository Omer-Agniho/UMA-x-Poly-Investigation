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

ALL_RELATED_YES_BUYERS_CSV = r"C:\Users\user\Documents\POLYMARKET CASE EVIDENCE\01_ORIGINAL_EVIDENCE\Trade History\step8_CROSS_MARKET_YES_BUYERS\cross_market_yes_buyer_outputs\03_all_related_market_yes_buyers.csv"
CROSS_MARKET_WALLET_SUMMARY_CSV = r"C:\Users\user\Documents\POLYMARKET CASE EVIDENCE\01_ORIGINAL_EVIDENCE\Trade History\step8_CROSS_MARKET_YES_BUYERS\cross_market_yes_buyer_outputs\04_cross_market_wallet_summary.csv"

OUTPUT_DIR = "step9_receipt_based_transfer_outputs"

CTF_CONTRACT = "0x4D97DCd97eC945f40cF65F87097ACe5EA0476045"

FINAL_SETTLEMENT_UTC = "2026-06-18T00:32:19+00:00"

RUN_MODE = "PRIORITY"

MIN_FUTURE_NOTIONAL_USDC = 100000
MIN_TOTAL_NOTIONAL_USDC = 100000

INCLUDE_ALL_TARGET_AND_FUTURE = True
INCLUDE_FUTURE_ONLY_ABOVE_THRESHOLD = True
INCLUDE_TARGET_ONLY_ABOVE_THRESHOLD = False

VALUE_DECIMALS_ASSUMPTION = 6

SELECTED_WALLETS_CSV = os.path.join(OUTPUT_DIR, "01_selected_wallets.csv")
SELECTED_TRADE_TXS_CSV = os.path.join(OUTPUT_DIR, "02_selected_trade_transactions.csv")
RAW_RECEIPTS_JSON = os.path.join(OUTPUT_DIR, "03_transaction_receipts_raw.json")
NORMALIZED_TRANSFERS_CSV = os.path.join(OUTPUT_DIR, "04_receipt_erc1155_transfers_normalized.csv")
WALLET_MARKET_SUMMARY_CSV = os.path.join(OUTPUT_DIR, "05_wallet_market_transfer_summary.csv")
SUMMARY_TXT = os.path.join(OUTPUT_DIR, "06_step9_receipt_transfer_summary.txt")
HASHES_CSV = os.path.join(OUTPUT_DIR, "07_step9_receipt_file_hashes.csv")


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
    df = pd.read_csv(CROSS_MARKET_WALLET_SUMMARY_CSV)

    selected = {}

    for _, row in df.iterrows():
        wallet = normalize_0x(row.get("proxyWallet", ""))

        if not valid_wallet(wallet):
            continue

        pattern = str(row.get("pattern", "")).strip()
        future_notional = safe_float(row.get("futureMarketYESNotionalUSDC", 0))
        total_notional = safe_float(row.get("totalYESNotionalUSDC", 0))

        include = False

        if RUN_MODE == "ALL":
            include = True

        if RUN_MODE == "PRIORITY":
            if INCLUDE_ALL_TARGET_AND_FUTURE and pattern == "BOUGHT_TARGET_AND_FUTURE_MARKETS":
                include = True

            if INCLUDE_FUTURE_ONLY_ABOVE_THRESHOLD and pattern == "BOUGHT_FUTURE_MARKETS_ONLY" and future_notional >= MIN_FUTURE_NOTIONAL_USDC:
                include = True

            if INCLUDE_TARGET_ONLY_ABOVE_THRESHOLD and pattern == "BOUGHT_TARGET_MARKET_ONLY" and total_notional >= MIN_TOTAL_NOTIONAL_USDC:
                include = True

        if not include:
            continue

        selected[wallet] = {
            "proxyWallet": wallet,
            "pattern": pattern,
            "uniqueMarketsBoughtYES": row.get("uniqueMarketsBoughtYES", ""),
            "targetMarketYESNotionalUSDC": row.get("targetMarketYESNotionalUSDC", ""),
            "futureMarketYESNotionalUSDC": row.get("futureMarketYESNotionalUSDC", ""),
            "totalYESNotionalUSDC": row.get("totalYESNotionalUSDC", ""),
            "earliestYESBuyUTC": row.get("earliestYESBuyUTC", ""),
            "latestYESBuyUTC": row.get("latestYESBuyUTC", ""),
            "names": row.get("names", ""),
            "pseudonyms": row.get("pseudonyms", ""),
        }

    return selected


def load_selected_trade_transactions(selected_wallets):
    df = pd.read_csv(ALL_RELATED_YES_BUYERS_CSV)

    required_cols = [
        "proxyWallet",
        "transactionHash",
        "conditionId",
        "marketRelationType",
        "marketQuestion",
        "marketSlug",
        "yesTokenId",
        "asset",
        "outcome",
        "size",
        "price",
        "notionalUSDC",
        "tradeTimeUTC",
    ]

    for col in required_cols:
        if col not in df.columns:
            raise RuntimeError(f"Missing required column in trade file: {col}")

    rows = []
    seen = set()

    for _, row in df.iterrows():
        wallet = normalize_0x(row.get("proxyWallet", ""))

        if wallet not in selected_wallets:
            continue

        tx_hash = normalize_0x(row.get("transactionHash", ""))

        if len(tx_hash) != 66:
            continue

        outcome = str(row.get("outcome", "")).strip().lower()
        asset = str(row.get("asset", "")).strip()
        yes_token_id = str(row.get("yesTokenId", "")).strip()

        if outcome != "yes" and asset != yes_token_id:
            continue

        key = (
            wallet,
            tx_hash,
            str(row.get("conditionId", "")),
            yes_token_id,
            str(row.get("size", "")),
            str(row.get("price", "")),
        )

        if key in seen:
            continue

        seen.add(key)

        rows.append({
            "proxyWallet": wallet,
            "walletPattern": selected_wallets[wallet].get("pattern", ""),
            "transactionHash": tx_hash,
            "conditionId": normalize_0x(row.get("conditionId", "")),
            "marketRelationType": row.get("marketRelationType", ""),
            "marketQuestion": row.get("marketQuestion", ""),
            "marketSlug": row.get("marketSlug", ""),
            "marketEndDate": row.get("marketEndDate", ""),
            "yesTokenId": yes_token_id,
            "asset": asset,
            "outcome": row.get("outcome", ""),
            "size": row.get("size", ""),
            "price": row.get("price", ""),
            "notionalUSDC": row.get("notionalUSDC", ""),
            "tradeTimeUTC": row.get("tradeTimeUTC", ""),
            "name": row.get("name", ""),
            "pseudonym": row.get("pseudonym", ""),
        })

    rows.sort(key=lambda r: (-safe_float(r["notionalUSDC"]), r["proxyWallet"]))

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


def decode_receipt_transfers(w3, receipt, trade_contexts, block_time_cache):
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

    selected_wallets = set(ctx["proxyWallet"] for ctx in trade_contexts)

    token_context = {}

    for ctx in trade_contexts:
        yes_token_id = str(ctx.get("yesTokenId", "")).strip()

        if yes_token_id:
            token_context[yes_token_id] = ctx

    decoded = []

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

                decoded.append(build_transfer_row(
                    w3,
                    event,
                    token_context[token_id],
                    selected_wallets,
                    "TransferSingle",
                    token_id,
                    value_raw,
                    block_time_cache,
                ))

            elif topic0 == transfer_batch_topic:
                event = contract.events.TransferBatch().process_log(log)
                args = event["args"]

                ids = [str(x) for x in args["ids"]]
                values = [int(x) for x in args["values"]]

                for token_id, value_raw in zip(ids, values):
                    if token_id not in token_context:
                        continue

                    decoded.append(build_transfer_row(
                        w3,
                        event,
                        token_context[token_id],
                        selected_wallets,
                        "TransferBatch",
                        token_id,
                        value_raw,
                        block_time_cache,
                    ))

        except Exception as e:
            print("Decode failed for tx:", event_hash(log.get("transactionHash", "")))
            print("logIndex:", log.get("logIndex", ""))
            print("error:", repr(e))

    return decoded


def build_transfer_row(w3, event, ctx, selected_wallets, event_type, token_id, value_raw, block_time_cache):
    args = event["args"]

    from_address = normalize_0x(args["from"])
    to_address = normalize_0x(args["to"])
    operator = normalize_0x(args["operator"])
    proxy_wallet = normalize_0x(ctx["proxyWallet"])

    if to_address == proxy_wallet:
        directionForTradeWallet = "IN"
    elif from_address == proxy_wallet:
        directionForTradeWallet = "OUT"
    elif operator == proxy_wallet:
        directionForTradeWallet = "OPERATOR_ONLY"
    else:
        directionForTradeWallet = "TOKEN_TRANSFER_IN_TRADE_TX_BUT_NOT_PROXY_WALLET"

    any_selected_wallet_in_transfer = (
        from_address in selected_wallets
        or to_address in selected_wallets
        or operator in selected_wallets
    )

    block_number = int(event["blockNumber"])
    block_ts = get_block_time(w3, block_number, block_time_cache)
    block_time_utc = timestamp_to_iso(block_ts)

    settlement_ts = parse_iso_to_ts(FINAL_SETTLEMENT_UTC)

    if block_ts < settlement_ts:
        settlement_bucket = "Before final settlement"
    else:
        settlement_bucket = "After final settlement"

    value_assuming_decimals = value_raw / (10 ** VALUE_DECIMALS_ASSUMPTION)

    return {
        "proxyWalletFromTrade": proxy_wallet,
        "walletPattern": ctx.get("walletPattern", ""),
        "directionForTradeWallet": directionForTradeWallet,
        "anySelectedWalletInTransfer": any_selected_wallet_in_transfer,
        "from": from_address,
        "to": to_address,
        "operator": operator,
        "eventType": event_type,
        "conditionId": ctx.get("conditionId", ""),
        "marketRelationType": ctx.get("marketRelationType", ""),
        "marketQuestion": ctx.get("marketQuestion", ""),
        "marketSlug": ctx.get("marketSlug", ""),
        "yesTokenId": ctx.get("yesTokenId", ""),
        "tokenSide": "YES",
        "tokenId": token_id,
        "valueRaw": str(value_raw),
        "valueAssuming6Decimals": value_assuming_decimals,
        "tradeSize": ctx.get("size", ""),
        "tradePrice": ctx.get("price", ""),
        "tradeNotionalUSDC": ctx.get("notionalUSDC", ""),
        "tradeTimeUTC": ctx.get("tradeTimeUTC", ""),
        "blockNumber": block_number,
        "blockTimestampUTC": block_time_utc,
        "settlementBucket": settlement_bucket,
        "transactionHash": event_hash(event["transactionHash"]),
        "logIndex": int(event["logIndex"]),
        "name": ctx.get("name", ""),
        "pseudonym": ctx.get("pseudonym", ""),
    }


def build_wallet_market_summary(transfer_rows):
    summary = {}

    for row in transfer_rows:
        key = (
            row["proxyWalletFromTrade"],
            row["conditionId"],
            row["yesTokenId"],
        )

        if key not in summary:
            summary[key] = {
                "proxyWallet": row["proxyWalletFromTrade"],
                "walletPattern": row["walletPattern"],
                "conditionId": row["conditionId"],
                "marketRelationType": row["marketRelationType"],
                "marketQuestion": row["marketQuestion"],
                "marketSlug": row["marketSlug"],
                "yesTokenId": row["yesTokenId"],
                "yesIn": 0.0,
                "yesOut": 0.0,
                "transferCount": 0,
                "firstTransferUTC": "",
                "lastTransferUTC": "",
                "txHashes": set(),
            }

        item = summary[key]
        amount = safe_float(row["valueAssuming6Decimals"])

        if row["directionForTradeWallet"] == "IN":
            item["yesIn"] += amount

        if row["directionForTradeWallet"] == "OUT":
            item["yesOut"] += amount

        item["transferCount"] += 1

        t = row["blockTimestampUTC"]

        if t and (not item["firstTransferUTC"] or t < item["firstTransferUTC"]):
            item["firstTransferUTC"] = t

        if t and (not item["lastTransferUTC"] or t > item["lastTransferUTC"]):
            item["lastTransferUTC"] = t

        item["txHashes"].add(row["transactionHash"])

    rows = []

    for _, item in summary.items():
        net = item["yesIn"] - item["yesOut"]

        rows.append({
            "proxyWallet": item["proxyWallet"],
            "walletPattern": item["walletPattern"],
            "conditionId": item["conditionId"],
            "marketRelationType": item["marketRelationType"],
            "marketQuestion": item["marketQuestion"],
            "marketSlug": item["marketSlug"],
            "yesTokenId": item["yesTokenId"],
            "yesIn": item["yesIn"],
            "yesOut": item["yesOut"],
            "yesNet": net,
            "transferCount": item["transferCount"],
            "firstTransferUTC": item["firstTransferUTC"],
            "lastTransferUTC": item["lastTransferUTC"],
            "txHashCount": len(item["txHashes"]),
            "sampleTxHashes": "; ".join(sorted(list(item["txHashes"]))[:5]),
        })

    rows.sort(key=lambda r: (-abs(float(r["yesNet"])), r["proxyWallet"]))

    return rows


def write_hashes():
    files = [
        SELECTED_WALLETS_CSV,
        SELECTED_TRADE_TXS_CSV,
        RAW_RECEIPTS_JSON,
        NORMALIZED_TRANSFERS_CSV,
        WALLET_MARKET_SUMMARY_CSV,
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


def write_summary(selected_wallets, trade_rows, receipt_count, transfer_rows, wallet_market_summary):
    wallets_with_transfers = set(
        row["proxyWalletFromTrade"]
        for row in transfer_rows
        if row["directionForTradeWallet"] in ["IN", "OUT"]
    )

    lines = []

    lines.append("Step 9 Receipt-Based ERC1155 Transfer Summary")
    lines.append("")
    lines.append(f"Collected at UTC: {datetime.now(timezone.utc).isoformat()}")
    lines.append(f"Polygon CTF contract: {CTF_CONTRACT}")
    lines.append(f"Selected wallets: {len(selected_wallets)}")
    lines.append(f"Selected trade rows: {len(trade_rows)}")
    lines.append(f"Unique receipts fetched: {receipt_count}")
    lines.append(f"Decoded ERC1155 YES transfer rows: {len(transfer_rows)}")
    lines.append(f"Wallet-market summary rows: {len(wallet_market_summary)}")
    lines.append(f"Wallets with direct IN or OUT YES transfer evidence: {len(wallets_with_transfers)}")
    lines.append("")
    lines.append("Interpretation:")
    lines.append("This file verifies ERC1155 YES-token movement from the transaction receipts of selected Polymarket YES trades. This is a targeted receipt-based verification and does not attempt to scan every transfer by every wallet across the full date window.")
    lines.append("")
    lines.append("Limitation:")
    lines.append("This method verifies transfer logs inside known trade transactions. It may not capture later manual transfers, unrelated transfers, or redemptions. Those are handled in Step 10 or a later targeted wallet-link review.")

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
    trade_rows = load_selected_trade_transactions(selected_wallets)

    if not selected_wallets:
        raise RuntimeError("No selected wallets. Check priority filters.")

    if not trade_rows:
        raise RuntimeError("No selected trade transactions. Check input CSV paths and filters.")

    write_csv(SELECTED_WALLETS_CSV, list(selected_wallets.values()))
    write_csv(SELECTED_TRADE_TXS_CSV, trade_rows)

    print("Selected wallets:", len(selected_wallets))
    print("Selected trade rows:", len(trade_rows))

    tx_to_contexts = {}

    for row in trade_rows:
        tx = row["transactionHash"]
        tx_to_contexts.setdefault(tx, []).append(row)

    print("Unique transaction receipts to fetch:", len(tx_to_contexts))

    raw_receipts = []
    transfer_rows = []
    block_time_cache = {}

    for index, tx_hash in enumerate(tx_to_contexts.keys(), start=1):
        print(f"Receipt {index} of {len(tx_to_contexts)}: {tx_hash}")

        receipt = get_receipt_with_retry(w3, tx_hash)
        raw_receipts.append(receipt_to_jsonable(receipt))

        decoded = decode_receipt_transfers(
            w3,
            receipt,
            tx_to_contexts[tx_hash],
            block_time_cache,
        )

        transfer_rows.extend(decoded)

        time.sleep(0.15)

    with open(RAW_RECEIPTS_JSON, "w", encoding="utf-8") as f:
        json.dump(raw_receipts, f, indent=2, ensure_ascii=False)

    transfer_rows.sort(key=lambda r: (r["blockNumber"], r["logIndex"], r["proxyWalletFromTrade"]))

    write_csv(NORMALIZED_TRANSFERS_CSV, transfer_rows)

    wallet_market_summary = build_wallet_market_summary(transfer_rows)
    write_csv(WALLET_MARKET_SUMMARY_CSV, wallet_market_summary)

    write_summary(
        selected_wallets,
        trade_rows,
        len(tx_to_contexts),
        transfer_rows,
        wallet_market_summary,
    )

    write_hashes()

    print("")
    print("Saved outputs:")
    print(SELECTED_WALLETS_CSV)
    print(SELECTED_TRADE_TXS_CSV)
    print(RAW_RECEIPTS_JSON)
    print(NORMALIZED_TRANSFERS_CSV)
    print(WALLET_MARKET_SUMMARY_CSV)
    print(SUMMARY_TXT)
    print(HASHES_CSV)
    print("")
    print("Done.")


if __name__ == "__main__":
    main()