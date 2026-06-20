import csv
import hashlib
import json
import os
import time
from datetime import datetime, timezone
from web3.middleware import ExtraDataToPOAMiddleware

import pandas as pd
from web3 import Web3


POLYGON_RPC_URL = "https://polygon-mainnet.g.alchemy.com/v2/bRzN_RjcHpGiBX3bLZjjU"

CROSS_MARKET_WALLET_SUMMARY_CSV = r"C:\Users\user\Documents\POLYMARKET CASE EVIDENCE\01_ORIGINAL_EVIDENCE\Trade History\step8_CROSS_MARKET_YES_BUYERS\cross_market_yes_buyer_outputs\04_cross_market_wallet_summary.csv"
ALL_RELATED_YES_BUYERS_CSV = r"C:\Users\user\Documents\POLYMARKET CASE EVIDENCE\01_ORIGINAL_EVIDENCE\Trade History\step8_CROSS_MARKET_YES_BUYERS\cross_market_yes_buyer_outputs\03_all_related_market_yes_buyers.csv"
RELATED_MARKETS_CSV = r"C:\Users\user\Documents\POLYMARKET CASE EVIDENCE\01_ORIGINAL_EVIDENCE\Trade History\step8_CROSS_MARKET_YES_BUYERS\cross_market_yes_buyer_outputs\01_related_iran_peace_markets.csv"

OUTPUT_DIR = "step9_erc1155_transfer_outputs"

CTF_CONTRACT = "0x4D97DCd97eC945f40cF65F87097ACe5EA0476045"

START_UTC = "2026-06-15T04:00:00+00:00"
END_UTC = "2026-06-20T04:00:00+00:00"

FINAL_SETTLEMENT_UTC = "2026-06-18T00:32:19+00:00"

CHUNK_SIZE = 10

RUN_MODE = "PRIORITY"

MIN_FUTURE_NOTIONAL_USDC = 100000
MIN_TOTAL_NOTIONAL_USDC = 100000

INCLUDE_ALL_TARGET_AND_FUTURE = True
INCLUDE_FUTURE_ONLY_ABOVE_THRESHOLD = True
INCLUDE_TARGET_ONLY_ABOVE_THRESHOLD = False

VALUE_DECIMALS_ASSUMPTION = 6

WALLETS_USED_CSV = os.path.join(OUTPUT_DIR, "01_wallets_used.csv")
MARKET_TOKENS_USED_CSV = os.path.join(OUTPUT_DIR, "02_market_tokens_used.csv")
RAW_LOGS_JSON = os.path.join(OUTPUT_DIR, "03_erc1155_transfer_logs_raw.json")
NORMALIZED_TRANSFERS_CSV = os.path.join(OUTPUT_DIR, "04_erc1155_transfers_normalized.csv")
WALLET_TOKEN_SUMMARY_CSV = os.path.join(OUTPUT_DIR, "05_wallet_token_transfer_summary.csv")
WALLET_MARKET_SUMMARY_CSV = os.path.join(OUTPUT_DIR, "06_wallet_market_transfer_summary.csv")
SUMMARY_TXT = os.path.join(OUTPUT_DIR, "07_step9_erc1155_transfer_summary.txt")
HASHES_CSV = os.path.join(OUTPUT_DIR, "08_step9_file_hashes.csv")


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


def valid_condition_id(value):
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


def address_to_topic(address):
    address = normalize_0x(address)

    if not address.startswith("0x"):
        raise RuntimeError(f"Address missing 0x prefix: {address}")

    if len(address) != 42:
        raise RuntimeError(f"Invalid address length for topic: {address}")

    return "0x" + "0" * 24 + address[2:]


def block_by_timestamp(w3, target_timestamp):
    low = 0
    high = w3.eth.block_number

    while low < high:
        mid = (low + high) // 2
        block = w3.eth.get_block(mid)
        block_timestamp = int(block["timestamp"])

        if block_timestamp < target_timestamp:
            low = mid + 1
        else:
            high = mid

    return low


def event_hash(value):
    if hasattr(value, "hex"):
        result = value.hex()
        if result.startswith("0x"):
            return result
        return "0x" + result

    return str(value)


def load_wallets():
    df = pd.read_csv(CROSS_MARKET_WALLET_SUMMARY_CSV)

    if "proxyWallet" not in df.columns:
        raise RuntimeError("Missing proxyWallet column in wallet summary.")

    wallets = {}

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

        wallets[wallet] = {
            "wallet": wallet,
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

    return wallets


def load_market_tokens():
    markets = {}

    if os.path.exists(RELATED_MARKETS_CSV):
        df = pd.read_csv(RELATED_MARKETS_CSV)

        for _, row in df.iterrows():
            condition_id = normalize_0x(row.get("conditionId", ""))

            if not valid_condition_id(condition_id):
                continue

            yes_token_id = str(row.get("yesTokenId", "")).strip()
            no_token_id = str(row.get("noTokenId", "")).strip()

            markets[condition_id] = {
                "conditionId": condition_id,
                "marketRelationType": str(row.get("relationType", "")),
                "marketQuestion": str(row.get("question", "")),
                "marketSlug": str(row.get("slug", "")),
                "marketEndDate": str(row.get("endDate", "")),
                "yesTokenId": yes_token_id,
                "noTokenId": no_token_id,
            }

    if os.path.exists(ALL_RELATED_YES_BUYERS_CSV):
        df = pd.read_csv(ALL_RELATED_YES_BUYERS_CSV)

        for _, row in df.iterrows():
            condition_id = normalize_0x(row.get("conditionId", ""))

            if not valid_condition_id(condition_id):
                continue

            if condition_id not in markets:
                markets[condition_id] = {
                    "conditionId": condition_id,
                    "marketRelationType": str(row.get("marketRelationType", "")),
                    "marketQuestion": str(row.get("marketQuestion", "")),
                    "marketSlug": str(row.get("marketSlug", "")),
                    "marketEndDate": str(row.get("marketEndDate", "")),
                    "yesTokenId": str(row.get("yesTokenId", "")).strip(),
                    "noTokenId": "",
                }

            if not markets[condition_id].get("yesTokenId"):
                markets[condition_id]["yesTokenId"] = str(row.get("yesTokenId", "")).strip()

    token_map = {}

    market_rows = []

    for condition_id, market in markets.items():
        yes_token_id = str(market.get("yesTokenId", "")).strip()
        no_token_id = str(market.get("noTokenId", "")).strip()

        market_rows.append(market)

        if yes_token_id:
            token_map[yes_token_id] = {
                "conditionId": condition_id,
                "tokenSide": "YES",
                "marketRelationType": market.get("marketRelationType", ""),
                "marketQuestion": market.get("marketQuestion", ""),
                "marketSlug": market.get("marketSlug", ""),
                "marketEndDate": market.get("marketEndDate", ""),
            }

        if no_token_id:
            token_map[no_token_id] = {
                "conditionId": condition_id,
                "tokenSide": "NO",
                "marketRelationType": market.get("marketRelationType", ""),
                "marketQuestion": market.get("marketQuestion", ""),
                "marketSlug": market.get("marketSlug", ""),
                "marketEndDate": market.get("marketEndDate", ""),
            }

    return market_rows, token_map


def fetch_logs_for_wallet_direction(w3, start_block, end_block, event_topic, wallet, direction_topic_index):
    logs = []

    wallet_topic = address_to_topic(wallet)

    current = start_block
    chunk_size = CHUNK_SIZE

    while current <= end_block:
        to_block = min(current + chunk_size - 1, end_block)

        if direction_topic_index == "from":
            topics = [event_topic, None, wallet_topic]
        elif direction_topic_index == "to":
            topics = [event_topic, None, None, wallet_topic]
        else:
            raise RuntimeError("direction_topic_index must be from or to")

        params = {
            "fromBlock": current,
            "toBlock": to_block,
            "address": Web3.to_checksum_address(CTF_CONTRACT),
            "topics": topics,
        }

        success = False

        for attempt in range(1, 9):
            try:
                batch = w3.eth.get_logs(params)
                logs.extend(batch)

                success = True
                break

            except Exception as e:
                error_text = repr(e)

                print("")
                print("Log query failed.")
                print("wallet:", wallet)
                print("direction:", direction_topic_index)
                print("event topic:", event_topic)
                print("blocks:", current, "to", to_block)
                print("chunk size:", chunk_size)
                print("attempt:", attempt, "of 8")
                print("error:", error_text)

                if "503" in error_text or "Service Unavailable" in error_text:
                    sleep_seconds = min(5 * attempt, 30)
                    print("RPC service unavailable. Waiting seconds:", sleep_seconds)
                    time.sleep(sleep_seconds)
                    continue

                if "429" in error_text or "rate" in error_text.lower():
                    sleep_seconds = min(10 * attempt, 60)
                    print("Rate limit suspected. Waiting seconds:", sleep_seconds)
                    time.sleep(sleep_seconds)
                    continue

                if chunk_size > 10:
                    chunk_size = max(10, chunk_size // 2)
                    print("Retrying with smaller chunk size:", chunk_size)
                    time.sleep(2)
                    break

                raise

        if success:
            current = to_block + 1
            time.sleep(0.75)
            continue

        if chunk_size > 10:
            continue

        raise RuntimeError(
            f"Failed after retries. wallet={wallet}, direction={direction_topic_index}, blocks={current}-{to_block}"
        )

    return logs


def decode_logs(w3, raw_logs, wallet, token_map, block_timestamp_cache):
    contract = w3.eth.contract(
        address=Web3.to_checksum_address(CTF_CONTRACT),
        abi=ERC1155_ABI,
    )

    decoded_rows = []

    for log in raw_logs:
        try:
            if event_hash(log["topics"][0]).lower() == TRANSFER_SINGLE_TOPIC.lower():
                event = contract.events.TransferSingle().process_log(log)
                args = event["args"]

                token_id = str(args["id"])
                value_raw = int(args["value"])

                if token_id not in token_map:
                    continue

                decoded_rows.append(build_transfer_row(
                    w3,
                    event,
                    wallet,
                    token_map[token_id],
                    "TransferSingle",
                    token_id,
                    value_raw,
                    block_timestamp_cache,
                ))

            else:
                event = contract.events.TransferBatch().process_log(log)
                args = event["args"]

                ids = [str(x) for x in args["ids"]]
                values = [int(x) for x in args["values"]]

                for token_id, value_raw in zip(ids, values):
                    if token_id not in token_map:
                        continue

                    decoded_rows.append(build_transfer_row(
                        w3,
                        event,
                        wallet,
                        token_map[token_id],
                        "TransferBatch",
                        token_id,
                        value_raw,
                        block_timestamp_cache,
                    ))

        except Exception as e:
            print("Decode failed for log:", event_hash(log.get("transactionHash", "")), log.get("logIndex", ""))
            print("Error:", e)

    return decoded_rows


def get_block_time(w3, block_number, cache):
    block_number = int(block_number)

    if block_number not in cache:
        block = w3.eth.get_block(block_number)
        cache[block_number] = int(block["timestamp"])

    return cache[block_number]


def build_transfer_row(w3, event, queried_wallet, token_info, event_type, token_id, value_raw, block_timestamp_cache):
    args = event["args"]

    from_address = normalize_0x(args["from"])
    to_address = normalize_0x(args["to"])
    queried_wallet = normalize_0x(queried_wallet)

    if to_address == queried_wallet and from_address == queried_wallet:
        direction = "SELF"
    elif to_address == queried_wallet:
        direction = "IN"
    elif from_address == queried_wallet:
        direction = "OUT"
    else:
        direction = "RELATED_BUT_NOT_DIRECT"

    block_number = int(event["blockNumber"])
    block_ts = get_block_time(w3, block_number, block_timestamp_cache)
    block_time_utc = timestamp_to_iso(block_ts)

    settlement_ts = parse_iso_to_ts(FINAL_SETTLEMENT_UTC)

    if block_ts < settlement_ts:
        settlementBucket = "Before final settlement"
    else:
        settlementBucket = "After final settlement"

    value_assuming_decimals = value_raw / (10 ** VALUE_DECIMALS_ASSUMPTION)

    return {
        "queriedWallet": queried_wallet,
        "direction": direction,
        "from": from_address,
        "to": to_address,
        "operator": normalize_0x(args["operator"]),
        "eventType": event_type,
        "conditionId": token_info.get("conditionId", ""),
        "tokenSide": token_info.get("tokenSide", ""),
        "tokenId": token_id,
        "valueRaw": str(value_raw),
        "valueAssuming6Decimals": value_assuming_decimals,
        "blockNumber": block_number,
        "blockTimestampUTC": block_time_utc,
        "settlementBucket": settlementBucket,
        "transactionHash": event_hash(event["transactionHash"]),
        "logIndex": int(event["logIndex"]),
        "marketRelationType": token_info.get("marketRelationType", ""),
        "marketQuestion": token_info.get("marketQuestion", ""),
        "marketSlug": token_info.get("marketSlug", ""),
        "marketEndDate": token_info.get("marketEndDate", ""),
    }


def dedupe_transfer_rows(rows):
    seen = set()
    output = []

    for row in rows:
        key = (
            row["transactionHash"],
            row["logIndex"],
            row["queriedWallet"],
            row["tokenId"],
            row["direction"],
            row["valueRaw"],
        )

        if key in seen:
            continue

        seen.add(key)
        output.append(row)

    output.sort(key=lambda r: (r["blockNumber"], r["logIndex"], r["queriedWallet"]))

    return output


def build_wallet_token_summary(rows, wallets):
    summary = {}

    for row in rows:
        key = (row["queriedWallet"], row["conditionId"], row["tokenSide"], row["tokenId"])

        if key not in summary:
            wallet_info = wallets.get(row["queriedWallet"], {})

            summary[key] = {
                "wallet": row["queriedWallet"],
                "walletPattern": wallet_info.get("pattern", ""),
                "conditionId": row["conditionId"],
                "tokenSide": row["tokenSide"],
                "tokenId": row["tokenId"],
                "marketRelationType": row["marketRelationType"],
                "marketQuestion": row["marketQuestion"],
                "marketSlug": row["marketSlug"],
                "inRaw": 0,
                "outRaw": 0,
                "transferCount": 0,
                "firstTransferUTC": "",
                "lastTransferUTC": "",
                "txHashes": set(),
            }

        item = summary[key]
        value_raw = int(row["valueRaw"])

        if row["direction"] == "IN":
            item["inRaw"] += value_raw

        if row["direction"] == "OUT":
            item["outRaw"] += value_raw

        item["transferCount"] += 1

        t = row["blockTimestampUTC"]

        if not item["firstTransferUTC"] or t < item["firstTransferUTC"]:
            item["firstTransferUTC"] = t

        if not item["lastTransferUTC"] or t > item["lastTransferUTC"]:
            item["lastTransferUTC"] = t

        item["txHashes"].add(row["transactionHash"])

    output = []

    for key, item in summary.items():
        net_raw = item["inRaw"] - item["outRaw"]

        output.append({
            "wallet": item["wallet"],
            "walletPattern": item["walletPattern"],
            "conditionId": item["conditionId"],
            "tokenSide": item["tokenSide"],
            "tokenId": item["tokenId"],
            "marketRelationType": item["marketRelationType"],
            "marketQuestion": item["marketQuestion"],
            "marketSlug": item["marketSlug"],
            "inRaw": str(item["inRaw"]),
            "outRaw": str(item["outRaw"]),
            "netRaw": str(net_raw),
            "inAssuming6Decimals": item["inRaw"] / (10 ** VALUE_DECIMALS_ASSUMPTION),
            "outAssuming6Decimals": item["outRaw"] / (10 ** VALUE_DECIMALS_ASSUMPTION),
            "netAssuming6Decimals": net_raw / (10 ** VALUE_DECIMALS_ASSUMPTION),
            "transferCount": item["transferCount"],
            "firstTransferUTC": item["firstTransferUTC"],
            "lastTransferUTC": item["lastTransferUTC"],
            "txHashCount": len(item["txHashes"]),
            "sampleTxHashes": "; ".join(sorted(list(item["txHashes"]))[:5]),
        })

    output.sort(key=lambda r: (-abs(float(r["netAssuming6Decimals"])), r["wallet"]))

    return output


def build_wallet_market_summary(token_summary):
    summary = {}

    for row in token_summary:
        key = (row["wallet"], row["conditionId"])

        if key not in summary:
            summary[key] = {
                "wallet": row["wallet"],
                "walletPattern": row["walletPattern"],
                "conditionId": row["conditionId"],
                "marketRelationType": row["marketRelationType"],
                "marketQuestion": row["marketQuestion"],
                "marketSlug": row["marketSlug"],
                "yesNet": 0.0,
                "noNet": 0.0,
                "yesIn": 0.0,
                "yesOut": 0.0,
                "noIn": 0.0,
                "noOut": 0.0,
                "firstTransferUTC": "",
                "lastTransferUTC": "",
            }

        item = summary[key]

        if row["tokenSide"] == "YES":
            item["yesNet"] += safe_float(row["netAssuming6Decimals"])
            item["yesIn"] += safe_float(row["inAssuming6Decimals"])
            item["yesOut"] += safe_float(row["outAssuming6Decimals"])

        if row["tokenSide"] == "NO":
            item["noNet"] += safe_float(row["netAssuming6Decimals"])
            item["noIn"] += safe_float(row["inAssuming6Decimals"])
            item["noOut"] += safe_float(row["outAssuming6Decimals"])

        first = row.get("firstTransferUTC", "")
        last = row.get("lastTransferUTC", "")

        if first and (not item["firstTransferUTC"] or first < item["firstTransferUTC"]):
            item["firstTransferUTC"] = first

        if last and (not item["lastTransferUTC"] or last > item["lastTransferUTC"]):
            item["lastTransferUTC"] = last

    output = []

    for key, item in summary.items():
        output.append({
            "wallet": item["wallet"],
            "walletPattern": item["walletPattern"],
            "conditionId": item["conditionId"],
            "marketRelationType": item["marketRelationType"],
            "marketQuestion": item["marketQuestion"],
            "marketSlug": item["marketSlug"],
            "yesIn": item["yesIn"],
            "yesOut": item["yesOut"],
            "yesNet": item["yesNet"],
            "noIn": item["noIn"],
            "noOut": item["noOut"],
            "noNet": item["noNet"],
            "firstTransferUTC": item["firstTransferUTC"],
            "lastTransferUTC": item["lastTransferUTC"],
        })

    output.sort(key=lambda r: (-abs(float(r["yesNet"])), r["wallet"]))

    return output


def write_hashes():
    files = [
        WALLETS_USED_CSV,
        MARKET_TOKENS_USED_CSV,
        RAW_LOGS_JSON,
        NORMALIZED_TRANSFERS_CSV,
        WALLET_TOKEN_SUMMARY_CSV,
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


def write_summary(wallets, market_rows, token_map, transfer_rows, token_summary, market_summary, start_block, end_block):
    yes_transfer_rows = [r for r in transfer_rows if r["tokenSide"] == "YES"]
    after_settlement_rows = [r for r in transfer_rows if r["settlementBucket"] == "After final settlement"]

    wallets_with_yes_transfers = set(r["queriedWallet"] for r in yes_transfer_rows)

    lines = []

    lines.append("Step 9 ERC1155 Transfer Summary")
    lines.append("")
    lines.append(f"Collected at UTC: {datetime.now(timezone.utc).isoformat()}")
    lines.append(f"Polygon CTF contract: {CTF_CONTRACT}")
    lines.append(f"UTC window: {START_UTC} through {END_UTC}")
    lines.append(f"Polygon blocks: {start_block} through {end_block}")
    lines.append("")
    lines.append(f"Wallets queried: {len(wallets)}")
    lines.append(f"Markets loaded: {len(market_rows)}")
    lines.append(f"Token IDs tracked: {len(token_map)}")
    lines.append(f"Normalized transfer rows: {len(transfer_rows)}")
    lines.append(f"YES transfer rows: {len(yes_transfer_rows)}")
    lines.append(f"After-settlement transfer rows: {len(after_settlement_rows)}")
    lines.append(f"Wallets with YES transfer evidence: {len(wallets_with_yes_transfers)}")
    lines.append("")
    lines.append("Interpretation:")
    lines.append("This Step 9 export tracks ERC1155 Conditional Tokens transfers involving the selected wallets and the market token IDs. It can show receipt, sending, and net movement of YES or NO tokens. It does not by itself prove redemption or realized profit. Redemption is Step 10.")

    with open(SUMMARY_TXT, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))


def serialize_log(log):
    return {
        "address": log["address"],
        "topics": [event_hash(t) for t in log["topics"]],
        "data": event_hash(log["data"]),
        "blockNumber": int(log["blockNumber"]),
        "transactionHash": event_hash(log["transactionHash"]),
        "transactionIndex": int(log["transactionIndex"]),
        "blockHash": event_hash(log["blockHash"]),
        "logIndex": int(log["logIndex"]),
        "removed": bool(log.get("removed", False)),
    }


def main():
    ensure_output_dir()

    if not POLYGON_RPC_URL or "PASTE_" in POLYGON_RPC_URL:
        raise RuntimeError("Paste your Polygon RPC URL into POLYGON_RPC_URL first.")

    w3 = Web3(Web3.HTTPProvider(POLYGON_RPC_URL))
    w3.middleware_onion.inject(ExtraDataToPOAMiddleware, layer=0)

    if not w3.is_connected():
        raise RuntimeError("Could not connect to Polygon RPC.")

    start_ts = parse_iso_to_ts(START_UTC)
    end_ts = parse_iso_to_ts(END_UTC)

    print("Finding Polygon start block...")
    start_block = block_by_timestamp(w3, start_ts)

    print("Finding Polygon end block...")
    end_block = block_by_timestamp(w3, end_ts)

    print("Start block:", start_block)
    print("End block:", end_block)

    wallets = load_wallets()
    market_rows, token_map = load_market_tokens()

    if not wallets:
        raise RuntimeError("No wallets selected. Check wallet summary and priority filters.")

    if not token_map:
        raise RuntimeError("No token IDs loaded. Check related market files.")

    write_csv(WALLETS_USED_CSV, list(wallets.values()))
    write_csv(MARKET_TOKENS_USED_CSV, market_rows)

    print("Wallets selected:", len(wallets))
    print("Token IDs loaded:", len(token_map))

    global TRANSFER_SINGLE_TOPIC
    global TRANSFER_BATCH_TOPIC

    TRANSFER_SINGLE_TOPIC = Web3.to_hex(
        Web3.keccak(text="TransferSingle(address,address,address,uint256,uint256)")
    )

    TRANSFER_BATCH_TOPIC = Web3.to_hex(
        Web3.keccak(text="TransferBatch(address,address,address,uint256[],uint256[])")
    )

    raw_logs_serialized = []
    decoded_rows = []
    block_timestamp_cache = {}

    for index, wallet in enumerate(wallets.keys(), start=1):
        print("")
        print(f"Wallet {index} of {len(wallets)}: {wallet}")

        wallet_raw_logs = []

        for event_name, topic in [
            ("TransferSingle", TRANSFER_SINGLE_TOPIC),
            ("TransferBatch", TRANSFER_BATCH_TOPIC),
        ]:
            print("Fetching incoming", event_name)
            incoming = fetch_logs_for_wallet_direction(
                w3,
                start_block,
                end_block,
                topic,
                wallet,
                "to",
            )

            print("Fetching outgoing", event_name)
            outgoing = fetch_logs_for_wallet_direction(
                w3,
                start_block,
                end_block,
                topic,
                wallet,
                "from",
            )

            wallet_raw_logs.extend(incoming)
            wallet_raw_logs.extend(outgoing)

        for log in wallet_raw_logs:
            raw_logs_serialized.append(serialize_log(log))

        decoded_rows.extend(decode_logs(
            w3,
            wallet_raw_logs,
            wallet,
            token_map,
            block_timestamp_cache,
        ))

        time.sleep(0.5)

    with open(RAW_LOGS_JSON, "w", encoding="utf-8") as f:
        json.dump(raw_logs_serialized, f, indent=2, ensure_ascii=False)

    transfer_rows = dedupe_transfer_rows(decoded_rows)

    write_csv(NORMALIZED_TRANSFERS_CSV, transfer_rows)

    token_summary = build_wallet_token_summary(transfer_rows, wallets)
    write_csv(WALLET_TOKEN_SUMMARY_CSV, token_summary)

    market_summary = build_wallet_market_summary(token_summary)
    write_csv(WALLET_MARKET_SUMMARY_CSV, market_summary)

    write_summary(
        wallets,
        market_rows,
        token_map,
        transfer_rows,
        token_summary,
        market_summary,
        start_block,
        end_block,
    )

    write_hashes()

    print("")
    print("Saved outputs:")
    print(WALLETS_USED_CSV)
    print(MARKET_TOKENS_USED_CSV)
    print(RAW_LOGS_JSON)
    print(NORMALIZED_TRANSFERS_CSV)
    print(WALLET_TOKEN_SUMMARY_CSV)
    print(WALLET_MARKET_SUMMARY_CSV)
    print(SUMMARY_TXT)
    print(HASHES_CSV)
    print("")
    print("Done.")


if __name__ == "__main__":
    main()