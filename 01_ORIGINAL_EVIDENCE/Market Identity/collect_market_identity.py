import csv
import hashlib
import json
import os
import re
from datetime import datetime, timezone

import requests
from web3 import Web3


MARKET_SLUG = "us-x-iran-permanent-peace-deal-by-june-15-2026-734-856-129"

EVENT_SLUG = "us-x-iran-permanent-peace-deal-by"

POLYGON_RPC_URL = "https://polygon-mainnet.g.alchemy.com/v2/bRzN_RjcHpGiBX3bLZjjU"

TARGET_CHILD_ANCILLARY_HASH = "0xfebefea9c50649e612e994415e1aade270fc67155c424bcef61618f5c5645be6"

CHILD_ORACLE_FROM_UMA_WRAPPER = "0xac60353a54873c446101216829a6a98cdbbc3f3d"
CHILD_REQUESTER_FROM_UMA_WRAPPER = "0x2c0367a9db231ddebd88a94b4f6461a6e47c58b1"
CHILD_CHAIN_ID_FROM_UMA_WRAPPER = "137"

OUTPUT_DIR = "step4_market_identity_outputs"

GAMMA_MARKET_BY_SLUG_FILE = os.path.join(OUTPUT_DIR, "01_gamma_market_by_slug_raw.json")
GAMMA_MARKETS_SEARCH_FILE = os.path.join(OUTPUT_DIR, "02_gamma_markets_search_raw.json")
GAMMA_EVENT_FILE = os.path.join(OUTPUT_DIR, "03_gamma_event_raw.json")
MARKET_IDENTITY_JSON = os.path.join(OUTPUT_DIR, "04_market_identity.json")
MARKET_IDENTITY_CSV = os.path.join(OUTPUT_DIR, "05_market_identity.csv")
POLYGON_GETQUESTION_JSON = os.path.join(OUTPUT_DIR, "06_polygon_getQuestion_result.json")
EVIDENCE_HASHES_CSV = os.path.join(OUTPUT_DIR, "07_file_hashes.csv")
SUMMARY_TXT = os.path.join(OUTPUT_DIR, "08_step4_summary.txt")


UMA_CTF_ADAPTER_ABI = [
    {
        "inputs": [
            {"internalType": "bytes32", "name": "questionID", "type": "bytes32"}
        ],
        "name": "getQuestion",
        "outputs": [
            {
                "components": [
                    {"internalType": "uint256", "name": "requestTimestamp", "type": "uint256"},
                    {"internalType": "uint256", "name": "reward", "type": "uint256"},
                    {"internalType": "uint256", "name": "proposalBond", "type": "uint256"},
                    {"internalType": "uint256", "name": "liveness", "type": "uint256"},
                    {"internalType": "uint256", "name": "manualResolutionTimestamp", "type": "uint256"},
                    {"internalType": "bool", "name": "resolved", "type": "bool"},
                    {"internalType": "bool", "name": "paused", "type": "bool"},
                    {"internalType": "bool", "name": "reset", "type": "bool"},
                    {"internalType": "bool", "name": "refund", "type": "bool"},
                    {"internalType": "address", "name": "rewardToken", "type": "address"},
                    {"internalType": "address", "name": "creator", "type": "address"},
                    {"internalType": "bytes", "name": "ancillaryData", "type": "bytes"},
                ],
                "internalType": "struct QuestionData",
                "name": "",
                "type": "tuple",
            }
        ],
        "stateMutability": "view",
        "type": "function",
    },
    {
        "inputs": [
            {"internalType": "bytes32", "name": "questionID", "type": "bytes32"}
        ],
        "name": "isInitialized",
        "outputs": [
            {"internalType": "bool", "name": "", "type": "bool"}
        ],
        "stateMutability": "view",
        "type": "function",
    },
]


def ensure_output_dir():
    os.makedirs(OUTPUT_DIR, exist_ok=True)


def save_json(path, data):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def read_jsonish(value):
    if value is None:
        return []

    if isinstance(value, list):
        return value

    if isinstance(value, str):
        value = value.strip()

        if not value:
            return []

        try:
            return json.loads(value)
        except Exception:
            return [value]

    return [value]


def sha256_file(path):
    h = hashlib.sha256()

    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)

    return h.hexdigest()


def normalize_0x(value):
    if not value:
        return ""

    value = str(value).strip().lower()

    if not value:
        return ""

    if not value.startswith("0x"):
        value = "0x" + value

    return value


def fetch_json(url, label):
    response = requests.get(url, timeout=60)

    print(label, response.status_code)

    if response.status_code != 200:
        print(response.text[:2000])
        raise RuntimeError(f"Request failed: {label}")

    return response.json()


def fetch_gamma_market():
    market_by_slug_url = f"https://gamma-api.polymarket.com/markets/slug/{MARKET_SLUG}"
    markets_search_url = f"https://gamma-api.polymarket.com/markets?slug={MARKET_SLUG}"
    event_url = f"https://gamma-api.polymarket.com/events?slug={EVENT_SLUG}"

    market_by_slug = fetch_json(market_by_slug_url, "market by slug")
    save_json(GAMMA_MARKET_BY_SLUG_FILE, market_by_slug)

    markets_search = fetch_json(markets_search_url, "markets search")
    save_json(GAMMA_MARKETS_SEARCH_FILE, markets_search)

    event_data = fetch_json(event_url, "event by slug")
    save_json(GAMMA_EVENT_FILE, event_data)

    candidates = []

    if isinstance(market_by_slug, dict):
        candidates.append(market_by_slug)

    if isinstance(markets_search, list):
        candidates.extend(markets_search)

    if isinstance(event_data, list):
        for event in event_data:
            for market in event.get("markets", []):
                candidates.append(market)

    exact = []

    for market in candidates:
        slug = market.get("slug", "")
        question = market.get("question", "") or market.get("title", "")

        if slug == MARKET_SLUG:
            exact.append(market)
        elif "iran" in question.lower() and "june 15" in question.lower():
            exact.append(market)

    if not exact:
        raise RuntimeError("No exact market candidate found. Check MARKET_SLUG and EVENT_SLUG.")

    return exact[0]


def extract_market_identity(market):
    outcomes = read_jsonish(market.get("outcomes"))
    clob_token_ids = read_jsonish(market.get("clobTokenIds"))
    outcome_prices = read_jsonish(market.get("outcomePrices"))

    yes_token_id = ""
    no_token_id = ""

    for index, outcome in enumerate(outcomes):
        outcome_text = str(outcome).strip().lower()

        if index < len(clob_token_ids):
            token_id = str(clob_token_ids[index])

            if outcome_text == "yes":
                yes_token_id = token_id

            if outcome_text == "no":
                no_token_id = token_id

    identity = {
        "collectedAtUTC": datetime.now(timezone.utc).isoformat(),
        "marketId": market.get("id", ""),
        "marketSlug": market.get("slug", ""),
        "question": market.get("question", ""),
        "description": market.get("description", ""),
        "conditionId": normalize_0x(market.get("conditionId", "")),
        "questionID": normalize_0x(market.get("questionID", "")),
        "endDate": market.get("endDate", ""),
        "endDateIso": market.get("endDateIso", ""),
        "umaEndDate": market.get("umaEndDate", ""),
        "umaEndDateIso": market.get("umaEndDateIso", ""),
        "closed": market.get("closed", ""),
        "active": market.get("active", ""),
        "resolvedBy": normalize_0x(market.get("resolvedBy", "")),
        "resolutionSource": market.get("resolutionSource", ""),
        "umaResolutionStatus": market.get("umaResolutionStatus", ""),
        "outcomesRaw": market.get("outcomes", ""),
        "outcomesParsed": outcomes,
        "clobTokenIdsRaw": market.get("clobTokenIds", ""),
        "clobTokenIdsParsed": clob_token_ids,
        "outcomePricesRaw": market.get("outcomePrices", ""),
        "outcomePricesParsed": outcome_prices,
        "yesTokenId": yes_token_id,
        "noTokenId": no_token_id,
        "targetChildAncillaryHashFromUma": TARGET_CHILD_ANCILLARY_HASH,
        "childOracleFromUmaWrapper": normalize_0x(CHILD_ORACLE_FROM_UMA_WRAPPER),
        "childRequesterFromUmaWrapper": normalize_0x(CHILD_REQUESTER_FROM_UMA_WRAPPER),
        "childChainIdFromUmaWrapper": CHILD_CHAIN_ID_FROM_UMA_WRAPPER,
    }

    return identity


def write_identity_csv(identity):
    rows = []

    for key, value in identity.items():
        if isinstance(value, list) or isinstance(value, dict):
            value = json.dumps(value, ensure_ascii=False)

        rows.append({
            "field": key,
            "value": value,
        })

    with open(MARKET_IDENTITY_CSV, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["field", "value"])
        writer.writeheader()
        writer.writerows(rows)


def decode_ancillary_text(ancillary_bytes):
    try:
        text = bytes(ancillary_bytes).decode("utf-8", errors="replace")
    except Exception:
        return ""

    text = text.replace("\x00", "")
    return " ".join(text.split())


def try_get_question(identity):
    if not POLYGON_RPC_URL or "PASTE_" in POLYGON_RPC_URL:
        return {
            "status": "SKIPPED_NO_POLYGON_RPC_URL",
            "message": "Paste a Polygon RPC URL into POLYGON_RPC_URL and rerun.",
        }

    w3 = Web3(Web3.HTTPProvider(POLYGON_RPC_URL))

    if not w3.is_connected():
        return {
            "status": "FAILED_RPC_CONNECTION",
            "message": "Could not connect to Polygon RPC.",
        }

    question_id = normalize_0x(identity.get("questionID", ""))

    if not question_id or len(question_id) != 66:
        question_id = normalize_0x(TARGET_CHILD_ANCILLARY_HASH)

    candidate_addresses = []

    for value in [
        identity.get("resolvedBy", ""),
        identity.get("childRequesterFromUmaWrapper", ""),
        "0x71392E133063CC0D16F40E1F9B60227404Bc03f7",
        "0x6A9D222616C90FcA5754cd1333cFD9b7fb6a4F74",
        "0xB97455fcF78eb37375e8be6f26df895341CA073d",
        "0xCB1822859cEF82Cd2Eb4E6276C7916e692995130",
    ]:
        value = normalize_0x(value)

        if value and value not in candidate_addresses:
            candidate_addresses.append(value)

    results = {
        "status": "NO_WORKING_ADAPTER_FOUND_YET",
        "questionIDUsed": question_id,
        "candidateAddressesTried": candidate_addresses,
        "successfulAdapter": "",
        "attempts": [],
    }

    for address in candidate_addresses:
        attempt = {
            "adapterAddress": address,
            "ok": False,
            "error": "",
            "isInitialized": None,
        }

        try:
            contract = w3.eth.contract(
                address=Web3.to_checksum_address(address),
                abi=UMA_CTF_ADAPTER_ABI,
            )

            qid_bytes = Web3.to_bytes(hexstr=question_id)

            try:
                initialized = contract.functions.isInitialized(qid_bytes).call()
                attempt["isInitialized"] = initialized
            except Exception as e:
                attempt["isInitialized"] = f"isInitialized call failed: {e}"

            question_data = contract.functions.getQuestion(qid_bytes).call()

            ancillary_bytes = question_data[11]
            ancillary_hex = "0x" + bytes(ancillary_bytes).hex()
            ancillary_text = decode_ancillary_text(ancillary_bytes)
            computed_hash = Web3.to_hex(Web3.keccak(ancillary_bytes))

            attempt.update({
                "ok": True,
                "requestTimestamp": question_data[0],
                "reward": str(question_data[1]),
                "proposalBond": str(question_data[2]),
                "liveness": question_data[3],
                "manualResolutionTimestamp": question_data[4],
                "resolved": question_data[5],
                "paused": question_data[6],
                "reset": question_data[7],
                "refund": question_data[8],
                "rewardToken": question_data[9],
                "creator": question_data[10],
                "ancillaryDataHex": ancillary_hex,
                "ancillaryDataText": ancillary_text,
                "computedKeccakAncillaryData": computed_hash,
                "computedHashMatchesQuestionID": computed_hash.lower() == question_id.lower(),
                "computedHashMatchesTargetChildAncillaryHash": computed_hash.lower() == TARGET_CHILD_ANCILLARY_HASH.lower(),
            })

            results["status"] = "FOUND_GETQUESTION_RESULT"
            results["successfulAdapter"] = address
            results["attempts"].append(attempt)
            return results

        except Exception as e:
            attempt["error"] = str(e)
            results["attempts"].append(attempt)

    return results


def write_hashes():
    files = [
        GAMMA_MARKET_BY_SLUG_FILE,
        GAMMA_MARKETS_SEARCH_FILE,
        GAMMA_EVENT_FILE,
        MARKET_IDENTITY_JSON,
        MARKET_IDENTITY_CSV,
        POLYGON_GETQUESTION_JSON,
        SUMMARY_TXT,
    ]

    rows = []

    for path in files:
        if os.path.exists(path):
            rows.append({
                "filename": os.path.basename(path),
                "sha256": sha256_file(path),
            })

    with open(EVIDENCE_HASHES_CSV, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["filename", "sha256"])
        writer.writeheader()
        writer.writerows(rows)


def write_summary(identity, polygon_result):
    lines = []

    lines.append("Step 4 Market Identity Summary")
    lines.append("")
    lines.append(f"Collected at UTC: {identity.get('collectedAtUTC')}")
    lines.append(f"Market ID: {identity.get('marketId')}")
    lines.append(f"Market slug: {identity.get('marketSlug')}")
    lines.append(f"Question: {identity.get('question')}")
    lines.append(f"Condition ID: {identity.get('conditionId')}")
    lines.append(f"Question ID: {identity.get('questionID')}")
    lines.append(f"YES token ID: {identity.get('yesTokenId')}")
    lines.append(f"NO token ID: {identity.get('noTokenId')}")
    lines.append(f"Outcomes parsed: {identity.get('outcomesParsed')}")
    lines.append(f"CLOB token IDs parsed: {identity.get('clobTokenIdsParsed')}")
    lines.append("")
    lines.append("UMA child-chain bridge fields from Ethereum VoteRevealed wrapper:")
    lines.append(f"Target child ancillaryDataHash: {identity.get('targetChildAncillaryHashFromUma')}")
    lines.append(f"childChainId: {identity.get('childChainIdFromUmaWrapper')}")
    lines.append(f"childOracle: {identity.get('childOracleFromUmaWrapper')}")
    lines.append(f"childRequester: {identity.get('childRequesterFromUmaWrapper')}")
    lines.append("")
    lines.append("Polygon getQuestion status:")
    lines.append(polygon_result.get("status", ""))
    lines.append(f"Successful adapter: {polygon_result.get('successfulAdapter', '')}")
    lines.append("")

    if polygon_result.get("status") == "FOUND_GETQUESTION_RESULT":
        successful = polygon_result["attempts"][-1]
        lines.append(f"Request timestamp: {successful.get('requestTimestamp')}")
        lines.append(f"Resolved: {successful.get('resolved')}")
        lines.append(f"Paused: {successful.get('paused')}")
        lines.append(f"Reset: {successful.get('reset')}")
        lines.append(f"Creator: {successful.get('creator')}")
        lines.append(f"Computed keccak ancillaryData: {successful.get('computedKeccakAncillaryData')}")
        lines.append(f"Computed hash matches questionID: {successful.get('computedHashMatchesQuestionID')}")
        lines.append(f"Computed hash matches target child ancillary hash: {successful.get('computedHashMatchesTargetChildAncillaryHash')}")
        lines.append("")
        lines.append("Ancillary text excerpt:")
        lines.append(successful.get("ancillaryDataText", "")[:2000])

    with open(SUMMARY_TXT, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))


def main():
    ensure_output_dir()

    print("Fetching Gamma market metadata...")
    market = fetch_gamma_market()

    print("Extracting market identity...")
    identity = extract_market_identity(market)

    save_json(MARKET_IDENTITY_JSON, identity)
    write_identity_csv(identity)

    print("Trying Polygon getQuestion...")
    polygon_result = try_get_question(identity)
    save_json(POLYGON_GETQUESTION_JSON, polygon_result)

    write_summary(identity, polygon_result)
    write_hashes()

    print("")
    print("Saved outputs:")
    print(GAMMA_MARKET_BY_SLUG_FILE)
    print(GAMMA_MARKETS_SEARCH_FILE)
    print(GAMMA_EVENT_FILE)
    print(MARKET_IDENTITY_JSON)
    print(MARKET_IDENTITY_CSV)
    print(POLYGON_GETQUESTION_JSON)
    print(EVIDENCE_HASHES_CSV)
    print(SUMMARY_TXT)
    print("")
    print("Key extracted values:")
    print("Market ID:", identity.get("marketId"))
    print("Question ID:", identity.get("questionID"))
    print("Condition ID:", identity.get("conditionId"))
    print("YES token ID:", identity.get("yesTokenId"))
    print("NO token ID:", identity.get("noTokenId"))
    print("Polygon getQuestion status:", polygon_result.get("status"))
    print("Successful adapter:", polygon_result.get("successfulAdapter"))


if __name__ == "__main__":
    main()