import json
import csv
from collections import defaultdict
from web3 import Web3

RAW_LOG_CACHE_FILE = "uma_yesorno_raw_logs_cache.json"
OUTPUT_CSV = "round10310_request_inspection.csv"

ROUND_ID_TARGET = 10310

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

def decode_identifier(identifier_bytes):
    raw = bytes(identifier_bytes)
    return raw.rstrip(b"\x00").decode("utf-8", errors="replace")

def decode_vote(price):
    if price == 10 ** 18:
        return "YES"
    if price == 0:
        return "NO"
    if price == -(2 ** 255):
        return "SENTINEL_OR_OTHER"
    return "OTHER"

def safe_text_from_bytes(value):
    try:
        text = bytes(value).decode("utf-8", errors="replace")
    except Exception:
        return ""

    text = text.replace("\x00", "")
    return " ".join(text.split())

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

def contains_target_clues(text):
    value = text.lower()

    clues = [
        "b0bca505",
        "d86a8160",
        "iran",
        "united states",
        "peace",
        "permanent",
        "june 15",
        "military hostilities",
    ]

    return any(clue in value for clue in clues)

w3 = Web3()
contract = w3.eth.contract(
    address="0x004395edb43EFca9885CEdad51EC9fAf93Bd34ac",
    abi=[VOTE_REVEALED_ABI],
)

with open(RAW_LOG_CACHE_FILE, "r", encoding="utf-8") as f:
    cache = json.load(f)

raw_logs = cache["logs"]

requests = defaultdict(lambda: {
    "roundId": "",
    "identifier": "",
    "requestTime": "",
    "ancillaryHashRawVoteRevealed": "",
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
    "containsTargetClues": False,
    "ancillaryText": "",
    "ancillaryHex": "",
})

for raw_log in raw_logs:
    event = contract.events.VoteRevealed().process_log(raw_log)
    args = event["args"]

    round_id = int(args["roundId"])

    if round_id != ROUND_ID_TARGET:
        continue

    identifier = decode_identifier(args["identifier"])
    price_raw = int(args["price"])
    decoded_vote = decode_vote(price_raw)
    num_tokens_uma = int(args["numTokens"]) / 10 ** 18

    ancillary_bytes = bytes(args["ancillaryData"])
    ancillary_hex = "0x" + ancillary_bytes.hex()
    ancillary_text = safe_text_from_bytes(ancillary_bytes)
    ancillary_hash = Web3.to_hex(Web3.keccak(ancillary_bytes))

    request_time = int(args["time"])

    key = (round_id, identifier, request_time, ancillary_hash)

    row = requests[key]

    row["roundId"] = round_id
    row["identifier"] = identifier
    row["requestTime"] = request_time
    row["ancillaryHashRawVoteRevealed"] = ancillary_hash
    row["count"] += 1
    row["containsTargetClues"] = contains_target_clues(ancillary_text)
    row["ancillaryText"] = ancillary_text[:5000]
    row["ancillaryHex"] = ancillary_hex[:5000]

    if decoded_vote == "YES":
        row["yesCount"] += 1
        row["yesTokensUMA"] += num_tokens_uma
    elif decoded_vote == "NO":
        row["noCount"] += 1
        row["noTokensUMA"] += num_tokens_uma
    else:
        row["otherCount"] += 1
        row["otherTokensUMA"] += num_tokens_uma

    if not row["exampleTxHash"]:
        row["exampleTxHash"] = event_hash(event["transactionHash"])
        row["exampleBlockNumber"] = event_int(event["blockNumber"])
        row["exampleLogIndex"] = event_int(event["logIndex"])

rows = list(requests.values())

rows.sort(
    key=lambda row: (
        not row["containsTargetClues"],
        -row["count"],
        -row["yesTokensUMA"],
    )
)

fieldnames = [
    "roundId",
    "identifier",
    "requestTime",
    "ancillaryHashRawVoteRevealed",
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
    "containsTargetClues",
    "ancillaryText",
    "ancillaryHex",
]

with open(OUTPUT_CSV, "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(rows)

print(f"Saved: {OUTPUT_CSV}")
print(f"Unique round 10310 requests found: {len(rows)}")

print("\nRows containing target clues:")
matches = [r for r in rows if r["containsTargetClues"]]

if not matches:
    print("No rows contained target clues.")
else:
    for row in matches[:20]:
        print(
            row["ancillaryHashRawVoteRevealed"],
            "count:",
            row["count"],
            "YES tokens:",
            round(row["yesTokensUMA"], 2),
            "NO tokens:",
            round(row["noTokensUMA"], 2),
        )
        print(row["ancillaryText"][:500])
        print()