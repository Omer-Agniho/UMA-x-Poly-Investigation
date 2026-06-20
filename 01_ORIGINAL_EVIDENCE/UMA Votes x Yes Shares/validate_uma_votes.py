import csv
from datetime import datetime, timezone
from web3 import Web3
import requests
import pandas as pd
import time
import json
import os
from collections import Counter
from collections import defaultdict

RAW_LOG_CACHE_FILE = "uma_yesorno_raw_logs_cache.json"
USE_RAW_LOG_CACHE = True
REFRESH_RAW_LOG_CACHE = False

RPC_URL = "https://eth-mainnet.g.alchemy.com/v2/bRzN_RjcHpGiBX3bLZjjU"

INPUT_XLSX = "UMA_Iran_VoteRecord_FULL.xlsx"
OUTPUT_CSV = "uma_vote_validation.csv"

UMA_VOTING_V2 = Web3.to_checksum_address("0x004395edb43EFca9885CEdad51EC9fAf93Bd34ac")

ROUND_ID_TARGET = 10310

TARGET_ANCILLARY_HASH_PREFIX = "0xfebefea9"
TARGET_ANCILLARY_HASH_SUFFIX = "5c5645be6"
TARGET_CHILD_ANCILLARY_HASH = "0xfebefea9c50649e612e994415e1aade270fc67155c424bcef61618f5c5645be6"

ANCILLARY_DISCOVERY_CSV = "round10310_ancillary_hash_discovery.csv"
YES_PRICE_RAW = 10 ** 18
NO_PRICE_RAW = 0
INT256_MIN = -(2 ** 255)

START_UTC = datetime(2026, 6, 17, 0, 0, 0, tzinfo=timezone.utc)
END_UTC = datetime(2026, 6, 18, 2, 0, 0, tzinfo=timezone.utc)

VOTE_REVEALED_ABI = {
    "anonymous": False,
    "inputs": [
        {"indexed": True, "internalType": "address", "name": "voter", "type": "address"},
        {"indexed": True, "internalType": "address", "name": "caller", "type": "address"},
        {"indexed": False, "internalType": "uint32", "name": "roundId", "type": "uint32"},
        {"indexed": True, "internalType": "bytes32", "name": "identifier", "type": "bytes32"},
        {"indexed": False, "internalType": "uint256", "name": "time", "type": "uint256"},
        {"indexed": False, "internalType": "bytes", "name": "ancillaryData", "type": "bytes"},
        {"indexed": False, "internalType": "int256", "name": "price", "type": "int256"},
        {"indexed": False, "internalType": "uint128", "name": "numTokens", "type": "uint128"},
    ],
    "name": "VoteRevealed",
    "type": "event",
}

import re

def extract_child_field(ancillary_text, field_name):
    if not ancillary_text:
        return ""

    pattern = rf"{field_name}:([^,]+)"
    match = re.search(pattern, str(ancillary_text))

    if not match:
        return ""

    return match.group(1).strip()


def normalize_hash(value):
    if not value:
        return ""

    value = str(value).strip().lower()

    if not value.startswith("0x"):
        value = "0x" + value

    return value

def safe_text_from_bytes(value):
    try:
        text = bytes(value).decode("utf-8", errors="replace")
    except Exception:
        return ""

    text = text.replace("\x00", "")
    text = " ".join(text.split())

    return text


def short_hash_match(hash_value):
    if not hash_value:
        return False

    value = hash_value.lower()

    return (
        value.startswith(TARGET_ANCILLARY_HASH_PREFIX.lower())
        and value.endswith(TARGET_ANCILLARY_HASH_SUFFIX.lower())
    )


def text_looks_like_target_market(text):
    if not text:
        return False

    value = text.lower()

    clues = [
        "iran",
        "united states",
        "peace",
        "permanent",
        "june 15",
        "military hostilities",
    ]

    return any(clue in value for clue in clues)

def event_hash(value):
    if value is None:
        return ""

    if isinstance(value, str):
        return value

    if hasattr(value, "hex"):
        result = value.hex()
        if result.startswith("0x"):
            return result
        return "0x" + result

    return str(value)


def event_int(value):
    if value is None:
        return ""

    if isinstance(value, int):
        return value

    if isinstance(value, str):
        if value.startswith("0x"):
            return int(value, 16)
        return int(value)

    return int(value)

def normalize_address(value):
    if not value:
        return ""
    value = value.strip()
    try:
        return Web3.to_checksum_address(value)
    except Exception:
        return ""

def decode_identifier(identifier_bytes):
    raw = bytes(identifier_bytes)
    return raw.rstrip(b"\x00").decode("utf-8", errors="replace")

def same_address(a, b):
    if not a or not b:
        return False

    return str(a).strip().lower() == str(b).strip().lower()

def decode_vote(price):
    if price == YES_PRICE_RAW:
        return "YES"
    if price == NO_PRICE_RAW:
        return "NO"
    if price == INT256_MIN:
        return "SENTINEL_OR_OTHER"
    return "OTHER"

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



def load_whales(path):
    df = pd.read_excel(
        path,
        sheet_name="Whales (Top 60)",
        header=3
    )

    df.columns = [
        str(col).replace("\n", " ").strip()
        for col in df.columns
    ]

    print("Loaded columns:")
    print(list(df.columns))

    whales = []

    for _, row in df.iterrows():
        staker = normalize_address(str(row.get("Wallet address", "")).strip())
        delegate = normalize_address(str(row.get("Delegate / hot wallet", "")).strip())

        if not staker:
            continue

        whales.append({
            "rank": row.get("Rank", ""),
            "staker": staker,
            "delegate": delegate,
            "workbook_vote": row.get("Vote", ""),
            "workbook_voting_power": row.get("Voting power (at vote, UMA)", ""),
            "workbook_reveal_time": row.get("Reveal time (UTC)", ""),
        })

    print(f"Whales loaded from workbook: {len(whales)}")

    if whales:
        print("First whale loaded:")
        print(whales[0])

    return whales

def main():
    w3 = Web3(Web3.HTTPProvider(RPC_URL))

    if not w3.is_connected():
        raise RuntimeError("Could not connect to Ethereum RPC.")

    start_block = block_by_timestamp(w3, int(START_UTC.timestamp()))
    end_block = block_by_timestamp(w3, int(END_UTC.timestamp()))

    print(f"Connected.")
    print(f"Start block: {start_block}")
    print(f"End block: {end_block}")

    whales = load_whales(INPUT_XLSX)

    if len(whales) == 0:
        raise RuntimeError("No whales loaded. The workbook or header row is not being read correctly.")

    staker_to_whale = {w["staker"].lower(): w for w in whales}
    delegate_to_whale = {
        w["delegate"].lower(): w
        for w in whales
        if w["delegate"]
    }

    contract = w3.eth.contract(
        address=UMA_VOTING_V2,
        abi=[VOTE_REVEALED_ABI],
    )

    yes_or_no_identifier = Web3.to_bytes(text="YES_OR_NO_QUERY").ljust(32, b"\x00")

    topic0 = Web3.to_hex(
        Web3.keccak(
            text="VoteRevealed(address,address,uint32,bytes32,uint256,bytes,int256,uint128)"
        )
    )

    topic3 = Web3.to_hex(
        Web3.to_bytes(text="YES_OR_NO_QUERY").ljust(32, b"\x00")
    )

    raw_logs = []

    if USE_RAW_LOG_CACHE and os.path.exists(RAW_LOG_CACHE_FILE) and not REFRESH_RAW_LOG_CACHE:
        print(f"Loading cached raw logs from {RAW_LOG_CACHE_FILE}")

        with open(RAW_LOG_CACHE_FILE, "r", encoding="utf-8") as f:
            cache = json.load(f)

        raw_logs = cache["logs"]

        print(f"Loaded cached raw logs: {len(raw_logs)}")

    else:
        print("No cache found, or cache refresh requested. Fetching logs from RPC.")

        raw_logs = []

        CHUNK_SIZE = 10

        headers = {
            "Content-Type": "application/json"
        }

        total_chunks = ((end_block - start_block) // CHUNK_SIZE) + 1

        for index, chunk_start in enumerate(range(start_block, end_block + 1, CHUNK_SIZE), start=1):
            chunk_end = min(chunk_start + CHUNK_SIZE - 1, end_block)

            if index == 1 or index % 50 == 0 or chunk_end == end_block:
                print(f"Reading logs chunk {index}/{total_chunks}: blocks {chunk_start} to {chunk_end}")

            payload = {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "eth_getLogs",
                "params": [
                    {
                        "fromBlock": hex(chunk_start),
                        "toBlock": hex(chunk_end),
                        "address": str(UMA_VOTING_V2),
                        "topics": [
                            topic0,
                            None,
                            None,
                            topic3
                        ]
                    }
                ]
            }

            response = requests.post(
                RPC_URL,
                json=payload,
                headers=headers,
                timeout=60
            )

            if response.status_code != 200:
                print("RPC HTTP error")
                print("Status:", response.status_code)
                print("Response:", response.text[:2000])
                raise RuntimeError("RPC rejected the eth_getLogs request.")

            data = response.json()

            if "error" in data:
                print("RPC JSON error")
                print(data["error"])
                raise RuntimeError("RPC returned a JSON-RPC error.")

            raw_logs.extend(data.get("result", []))

            time.sleep(0.05)

        cache = {
            "startBlock": start_block,
            "endBlock": end_block,
            "contract": str(UMA_VOTING_V2),
            "topic0": topic0,
            "topic3": topic3,
            "logs": raw_logs,
        }

        with open(RAW_LOG_CACHE_FILE, "w", encoding="utf-8") as f:
            json.dump(cache, f, indent=2)

        print(f"Saved raw log cache: {RAW_LOG_CACHE_FILE}")
        print(f"Cached raw logs: {len(raw_logs)}")

    events = []

    for raw_log in raw_logs:
        decoded_event = contract.events.VoteRevealed().process_log(raw_log)
        events.append(decoded_event)

    print(f"VoteRevealed events found for YES_OR_NO_QUERY: {len(events)}")
    output_rows = []

    matched_stakers = set()

    ancillary_hash_counts = Counter()

    hash_stats = defaultdict(lambda: {
        "ancillaryDataHash": "",
        "requestTime": "",
        "count": 0,
        "yesCount": 0,
        "noCount": 0,
        "otherCount": 0,
        "yesTokensUMA": 0,
        "noTokensUMA": 0,
        "otherTokensUMA": 0,
        "exampleTxHash": "",
        "exampleBlockNumber": "",
        "exampleLogIndex": "",
        "exampleDecodedVote": "",
        "exampleAncillaryText": "",
        "matchesWorkbookShortHash": False,
        "textLooksLikeTargetMarket": False,
    })

    for event in events:
        args = event["args"]

        voter = Web3.to_checksum_address(args["voter"])
        caller = Web3.to_checksum_address(args["caller"])
        round_id = int(args["roundId"])
        identifier_text = decode_identifier(args["identifier"])
        price_raw = int(args["price"])
        decoded_vote = decode_vote(price_raw)

        if round_id != ROUND_ID_TARGET:
            continue

        num_tokens_raw = int(args["numTokens"])
        num_tokens_uma = num_tokens_raw / 10 ** 18
        ancillary_bytes = bytes(args["ancillaryData"])
        ancillary_hash = Web3.to_hex(Web3.keccak(ancillary_bytes))
        ancillary_hash_counts[ancillary_hash] += 1

        ancillary_bytes = bytes(args["ancillaryData"])
        ancillary_hex = "0x" + ancillary_bytes.hex()
        ancillary_text = safe_text_from_bytes(ancillary_bytes)

        child_ancillary_hash = normalize_hash(
            extract_child_field(ancillary_text, "ancillaryDataHash")
        )

        child_block_number = extract_child_field(ancillary_text, "childBlockNumber")
        child_oracle = extract_child_field(ancillary_text, "childOracle")
        child_requester = extract_child_field(ancillary_text, "childRequester")
        child_chain_id = extract_child_field(ancillary_text, "childChainId")

        if child_ancillary_hash != TARGET_CHILD_ANCILLARY_HASH.lower():
            continue

        request_time = int(args["time"])

        if round_id == ROUND_ID_TARGET:
            key = (ancillary_hash, request_time)

            stats = hash_stats[key]

            stats["ancillaryDataHash"] = ancillary_hash
            stats["requestTime"] = request_time
            stats["count"] += 1
            stats["matchesWorkbookShortHash"] = short_hash_match(ancillary_hash)
            stats["textLooksLikeTargetMarket"] = text_looks_like_target_market(ancillary_text)

            if decoded_vote == "YES":
                stats["yesCount"] += 1
                stats["yesTokensUMA"] += num_tokens_uma
            elif decoded_vote == "NO":
                stats["noCount"] += 1
                stats["noTokensUMA"] += num_tokens_uma
            else:
                stats["otherCount"] += 1
                stats["otherTokensUMA"] += num_tokens_uma

            if not stats["exampleTxHash"]:
                stats["exampleTxHash"] = event_hash(event["transactionHash"])
                stats["exampleBlockNumber"] = event_int(event["blockNumber"])
                stats["exampleLogIndex"] = event_int(event["logIndex"])
                stats["exampleDecodedVote"] = decoded_vote
                stats["exampleAncillaryText"] = ancillary_text[:2000]

        voter_key = voter.lower()
        caller_key = caller.lower()

        whale = None
        match_type = ""

        if voter_key in staker_to_whale:
            candidate = staker_to_whale[voter_key]

            workbook_delegate = candidate.get("delegate", "")

            if workbook_delegate and same_address(caller, workbook_delegate):
                whale = candidate
                match_type = "EXACT_STAKER_AND_DELEGATE_MATCH"
            elif not workbook_delegate:
                whale = candidate
                match_type = "STAKER_MATCH_NO_WORKBOOK_DELEGATE"
            else:
                whale = candidate
                match_type = "STAKER_MATCH_CALLER_DIFFERS_FROM_WORKBOOK_DELEGATE"

        else:
            continue

        if whale is None:
            continue

        block_number = event_int(event["blockNumber"])
        block = w3.eth.get_block(block_number)
        block_time_utc = datetime.fromtimestamp(block["timestamp"], tz=timezone.utc).isoformat()

        validated = (
            round_id == ROUND_ID_TARGET
            and identifier_text == "YES_OR_NO_QUERY"
            and decoded_vote == "YES"
            and child_ancillary_hash == TARGET_CHILD_ANCILLARY_HASH.lower()
            and same_address(voter, whale["staker"])
        )

        if whale["delegate"]:
            validated = validated and same_address(caller, whale["delegate"])

        status = "VALIDATED_YES_UMA_REVEAL" if validated else "REVIEW"

        matched_stakers.add(whale["staker"].lower())

        output_rows.append({
            "rank": whale["rank"],
            "workbookStaker": whale["staker"],
            "workbookDelegate": whale["delegate"],
            "workbookVote": whale["workbook_vote"],
            "workbookVotingPowerUMA": whale["workbook_voting_power"],
            "workbookRevealTimeUTC": whale["workbook_reveal_time"],

            "txHash": event_hash(event["transactionHash"]),
            "blockNumber": event_int(event["blockNumber"]),
            "logIndex": event_int(event["logIndex"]),
            "eventContract": event["address"],
            "eventVoter": voter,
            "eventCaller": caller,

            "roundId": round_id,
            "identifierText": identifier_text,
            "requestTime": int(args["time"]),

            "ancillaryDataHash": ancillary_hash,
            "rawDvmAncillaryHash": ancillary_hash,
            "childAncillaryDataHash": child_ancillary_hash,
            "childBlockNumber": child_block_number,
            "childOracle": child_oracle,
            "childRequester": child_requester,
            "childChainId": child_chain_id,
            "matchesTargetAncillaryHash": child_ancillary_hash == TARGET_CHILD_ANCILLARY_HASH.lower(),

            "ancillaryDataHex": ancillary_hex,
            "priceRaw": str(price_raw),
            "decodedVote": decoded_vote,
            "numTokensRaw": str(num_tokens_raw),
            "numTokensUMA": num_tokens_uma,
            "blockTimestampUTC": block_time_utc,
            "matchType": match_type,
            "status": status,
        })

    discovery_rows = list(hash_stats.values())
    discovery_rows.sort(
        key=lambda row: (
            not row["matchesWorkbookShortHash"],
            not row["textLooksLikeTargetMarket"],
            -row["count"]
        )
    )

    with open(ANCILLARY_DISCOVERY_CSV, "w", newline="", encoding="utf-8") as f:
        fieldnames = [
            "rawDvmAncillaryHash",
            "childAncillaryDataHash",
            "childBlockNumber",
            "childOracle",
            "childRequester",
            "childChainId",
            "ancillaryDataHash",
            "requestTime",
            "count",
            "yesCount",
            "noCount",
            "otherCount",
            "yesTokensUMA",
            "noTokensUMA",
            "otherTokensUMA",
            "exampleTxHash",
            "exampleBlockNumber",
            "exampleLogIndex",
            "exampleDecodedVote",
            "matchesWorkbookShortHash",
            "textLooksLikeTargetMarket",
            "exampleAncillaryText",
        ]

        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(discovery_rows)

    print(f"Saved hash discovery CSV: {ANCILLARY_DISCOVERY_CSV}")

    short_matches = [
        row for row in discovery_rows
        if row["matchesWorkbookShortHash"]
    ]

    text_matches = [
        row for row in discovery_rows
        if row["textLooksLikeTargetMarket"]
    ]

    print("\nHashes matching workbook short hash:")
    if short_matches:
        for row in short_matches:
            print(row["ancillaryDataHash"], "count:", row["count"], "requestTime:", row["requestTime"])
    else:
        print("No hash matched 0xfebefea9...5c5645be6")

    print("\nHashes whose ancillary text looks like the Iran market:")
    if text_matches:
        for row in text_matches[:20]:
            print(row["ancillaryDataHash"], "count:", row["count"], "requestTime:", row["requestTime"])
    else:
        print("No decoded ancillary text matched Iran / peace / June 15 clues")

    for whale in whales:
        if whale["staker"].lower() not in matched_stakers:
            output_rows.append({
                "rank": whale["rank"],
                "workbookStaker": whale["staker"],
                "workbookDelegate": whale["delegate"],
                "workbookVote": whale["workbook_vote"],
                "workbookVotingPowerUMA": whale["workbook_voting_power"],
                "workbookRevealTimeUTC": whale["workbook_reveal_time"],

                "txHash": "",
                "blockNumber": "",
                "logIndex": "",
                "eventContract": "",
                "eventVoter": "",
                "eventCaller": "",

                "roundId": "",
                "identifierText": "",
                "requestTime": "",

                "ancillaryDataHash": "",
                "rawDvmAncillaryHash": "",
                "childAncillaryDataHash": "",
                "childBlockNumber": "",
                "childOracle": "",
                "childRequester": "",
                "childChainId": "",
                "matchesTargetAncillaryHash": "",

                "ancillaryDataHex": "",
                "priceRaw": "",
                "decodedVote": "",
                "numTokensRaw": "",
                "numTokensUMA": "",
                "blockTimestampUTC": "",
                "matchType": "",
                "status": "NO_MATCH_FOUND_IN_SELECTED_BLOCK_RANGE",
            })

    fieldnames = [
        "rank",
        "workbookStaker",
        "workbookDelegate",
        "workbookVote",
        "workbookVotingPowerUMA",
        "workbookRevealTimeUTC",
        "txHash",
        "blockNumber",
        "logIndex",
        "eventContract",
        "eventVoter",
        "eventCaller",
        "roundId",
        "identifierText",
        "requestTime",
        "ancillaryDataHash",
        "rawDvmAncillaryHash",
        "childAncillaryDataHash",
        "childBlockNumber",
        "childOracle",
        "childRequester",
        "childChainId",
        "matchesTargetAncillaryHash",
        "ancillaryDataHex",
        "priceRaw",
        "decodedVote",
        "numTokensRaw",
        "numTokensUMA",
        "blockTimestampUTC",
        "matchType",
        "status",
    ]

    print("\nAncillary hashes found after roundId filtering:")
    for hash_value, count in ancillary_hash_counts.most_common(20):
        print(hash_value, count)

    with open(OUTPUT_CSV, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(output_rows)

    print(f"Saved: {OUTPUT_CSV}")
    print(f"Matched rows: {len([r for r in output_rows if r['txHash']])}")

if __name__ == "__main__":
    main()