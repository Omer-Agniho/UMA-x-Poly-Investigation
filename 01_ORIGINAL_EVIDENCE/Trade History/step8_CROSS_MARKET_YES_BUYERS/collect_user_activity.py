import csv
import hashlib
import json
import os
import time
from datetime import datetime, timezone

import pandas as pd
import requests


MARKET_IDENTITY_CSV = r"C:\Users\user\Documents\POLYMARKET CASE EVIDENCE\01_ORIGINAL_EVIDENCE\Market Identity\step4_market_identity_outputs\05_market_identity.csv"
UMA_VALIDATION_CSV = r"C:\Users\user\Documents\POLYMARKET CASE EVIDENCE\01_ORIGINAL_EVIDENCE\UMA Votes x Yes Shares\uma_vote_validation.csv"
CROSS_MARKET_WALLET_SUMMARY_CSV = "cross_market_yes_buyer_outputs/04_cross_market_wallet_summary.csv"
STEP7_YES_BUYS_CSV = "step7_trade_history_outputs/04_yes_buys_only.csv"
STEP7_LARGE_YES_BUYS_CSV = "step7_trade_history_outputs/05_large_yes_buys.csv"

GAMMA_EVENT_JSON = "03_gamma_event_raw.json"

MANUAL_WALLETS_TXT = "manual_suspected_wallets.txt"

OUTPUT_DIR = "step8_user_activity_outputs"

ACTIVITY_URL = "https://data-api.polymarket.com/activity"

LIMIT = 500
MAX_OFFSET = 10000

START_UTC = "2026-06-15T04:00:00+00:00"
END_UTC = "2026-06-19T04:00:00+00:00"

MARKET_DEADLINE_UTC = "2026-06-16T03:59:00+00:00"
FINAL_SETTLEMENT_UTC = "2026-06-18T00:32:19+00:00"

SUSPECTED_WALLETS_CSV = os.path.join(OUTPUT_DIR, "01_suspected_wallets.csv")
RELATED_MARKETS_CSV = os.path.join(OUTPUT_DIR, "02_related_markets.csv")
RAW_ACTIVITY_JSON = os.path.join(OUTPUT_DIR, "03_user_activity_raw.json")
NORMALIZED_ACTIVITY_CSV = os.path.join(OUTPUT_DIR, "04_user_activity_normalized.csv")
TARGET_ACTIVITY_CSV = os.path.join(OUTPUT_DIR, "05_target_market_activity.csv")
FUTURE_RELATED_ACTIVITY_CSV = os.path.join(OUTPUT_DIR, "06_future_related_market_activity.csv")
REDEEMS_SPLITS_MERGES_CSV = os.path.join(OUTPUT_DIR, "07_redeems_splits_merges.csv")
DIRECT_UMA_MATCHES_CSV = os.path.join(OUTPUT_DIR, "08_activity_wallets_vs_uma_wallets.csv")
SUMMARY_TXT = os.path.join(OUTPUT_DIR, "09_step8_user_activity_summary.txt")
HASHES_CSV = os.path.join(OUTPUT_DIR, "10_step8_file_hashes.csv")


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


def parse_iso_to_ts(value):
    return int(datetime.fromisoformat(value).timestamp())


def safe_float(value):
    try:
        return float(value or 0)
    except Exception:
        return 0.0


def sha256_file(path):
    h = hashlib.sha256()

    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)

    return h.hexdigest()


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


def write_csv(path, rows, fieldnames=None):
    if not fieldnames:
        if rows:
            fieldnames = list(rows[0].keys())
        else:
            fieldnames = ["empty"]

    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()

        for row in rows:
            writer.writerow(row)


def load_market_identity(path):
    df = pd.read_csv(path)

    if "field" not in df.columns or "value" not in df.columns:
        raise RuntimeError("05_market_identity.csv must have columns named field and value.")

    identity = dict(zip(df["field"].astype(str), df["value"].astype(str)))

    return {
        "conditionId": normalize_0x(identity.get("conditionId", "")),
        "questionID": normalize_0x(identity.get("questionID", "")),
        "marketSlug": str(identity.get("marketSlug", "")).strip(),
        "question": str(identity.get("question", "")).strip(),
        "yesTokenId": str(identity.get("yesTokenId", "")).strip(),
        "noTokenId": str(identity.get("noTokenId", "")).strip(),
    }


def load_wallets_from_csv(path, source_label):
    rows = []

    if not os.path.exists(path):
        return rows

    df = pd.read_csv(path)

    possible_cols = [
        "proxyWallet",
        "eventVoter",
        "eventCaller",
        "workbookStaker",
        "workbookDelegate",
    ]

    for col in possible_cols:
        if col not in df.columns:
            continue

        for value in df[col].dropna().astype(str):
            wallet = normalize_0x(value)

            if valid_wallet(wallet):
                rows.append({
                    "wallet": wallet,
                    "sourceFile": os.path.basename(path),
                    "sourceColumn": col,
                    "sourceLabel": source_label,
                })

    return rows


def load_manual_wallets(path):
    rows = []

    if not os.path.exists(path):
        return rows

    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            wallet = normalize_0x(line.strip())

            if valid_wallet(wallet):
                rows.append({
                    "wallet": wallet,
                    "sourceFile": os.path.basename(path),
                    "sourceColumn": "manual",
                    "sourceLabel": "Manual suspected wallet list",
                })

    return rows


def build_suspected_wallets():
    wallet_rows = []

    wallet_rows.extend(load_wallets_from_csv(
        STEP7_YES_BUYS_CSV,
        "YES buyers from Step 7"
    ))

    wallet_rows.extend(load_wallets_from_csv(
        STEP7_LARGE_YES_BUYS_CSV,
        "Large YES buyers from Step 7"
    ))

    wallet_rows.extend(load_wallets_from_csv(
        UMA_VALIDATION_CSV,
        "UMA validation wallets, direct comparison only"
    ))

    wallet_rows.extend(load_wallets_from_csv(
        CROSS_MARKET_WALLET_SUMMARY_CSV,
        "Cross-market YES buyers, including future-market-only buyers"
    ))

    wallet_rows.extend(load_manual_wallets(MANUAL_WALLETS_TXT))

    merged = {}

    for row in wallet_rows:
        wallet = row["wallet"]

        if wallet not in merged:
            merged[wallet] = {
                "wallet": wallet,
                "sources": set(),
                "sourceFiles": set(),
                "sourceColumns": set(),
            }

        merged[wallet]["sources"].add(row["sourceLabel"])
        merged[wallet]["sourceFiles"].add(row["sourceFile"])
        merged[wallet]["sourceColumns"].add(row["sourceColumn"])

    output = []

    for wallet, info in merged.items():
        output.append({
            "wallet": wallet,
            "sources": "; ".join(sorted(info["sources"])),
            "sourceFiles": "; ".join(sorted(info["sourceFiles"])),
            "sourceColumns": "; ".join(sorted(info["sourceColumns"])),
        })

    output.sort(key=lambda r: r["wallet"])

    return output


def load_related_markets_from_gamma_event(path, target_condition_id):
    markets = {}

    if not os.path.exists(path):
        return []

    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)

    event_rows = data if isinstance(data, list) else [data]

    for event in event_rows:
        for market in event.get("markets", []):
            question = str(market.get("question", "") or market.get("title", ""))
            slug = str(market.get("slug", ""))
            condition_id = normalize_0x(market.get("conditionId", ""))

            if not valid_condition_id(condition_id):
                continue

            question_l = question.lower()
            slug_l = slug.lower()

            looks_related = (
                "iran" in question_l
                and "peace" in question_l
            ) or (
                "iran" in slug_l
                and "peace" in slug_l
            ) or condition_id == target_condition_id.lower()

            if not looks_related:
                continue

            outcomes = read_jsonish(market.get("outcomes"))
            token_ids = read_jsonish(market.get("clobTokenIds"))

            yes_token_id = ""
            no_token_id = ""

            for index, outcome in enumerate(outcomes):
                if index >= len(token_ids):
                    continue

                outcome_text = str(outcome).strip().lower()

                if outcome_text == "yes":
                    yes_token_id = str(token_ids[index])

                if outcome_text == "no":
                    no_token_id = str(token_ids[index])

            end_date = str(market.get("endDate", "") or market.get("endDateIso", ""))

            relation_type = "TARGET_MARKET" if condition_id == target_condition_id.lower() else "RELATED_MARKET"

            markets[condition_id] = {
                "conditionId": condition_id,
                "relationType": relation_type,
                "question": question,
                "slug": slug,
                "marketId": market.get("id", ""),
                "questionID": normalize_0x(market.get("questionID", "")),
                "endDate": end_date,
                "outcomes": json.dumps(outcomes),
                "clobTokenIds": json.dumps(token_ids),
                "yesTokenId": yes_token_id,
                "noTokenId": no_token_id,
            }

    return list(markets.values())


def build_market_list(market_identity):
    target_condition_id = market_identity["conditionId"]

    markets = load_related_markets_from_gamma_event(
        GAMMA_EVENT_JSON,
        target_condition_id,
    )

    if not markets:
        markets = [{
            "conditionId": target_condition_id,
            "relationType": "TARGET_MARKET",
            "question": market_identity.get("question", ""),
            "slug": market_identity.get("marketSlug", ""),
            "marketId": "",
            "questionID": market_identity.get("questionID", ""),
            "endDate": "",
            "outcomes": "",
            "clobTokenIds": "",
            "yesTokenId": market_identity.get("yesTokenId", ""),
            "noTokenId": market_identity.get("noTokenId", ""),
        }]

    markets.sort(key=lambda r: (r["relationType"], r["endDate"], r["slug"]))

    return markets


def fetch_activity_for_wallet(wallet, condition_ids):
    start_ts = parse_iso_to_ts(START_UTC)
    end_ts = parse_iso_to_ts(END_UTC)

    all_rows = []

    market_param = ",".join(condition_ids)

    for offset in range(0, MAX_OFFSET + 1, LIMIT):
        params = {
            "user": wallet,
            "market": market_param,
            "start": start_ts,
            "end": end_ts,
            "limit": LIMIT,
            "offset": offset,
            "sortBy": "TIMESTAMP",
            "sortDirection": "ASC",
        }

        print(f"Fetching activity wallet={wallet} offset={offset}")

        response = requests.get(ACTIVITY_URL, params=params, timeout=60)

        if response.status_code != 200:
            print("HTTP status:", response.status_code)
            print(response.text[:2000])
            raise RuntimeError("Polymarket activity request failed.")

        rows = response.json()

        if not isinstance(rows, list):
            print(rows)
            raise RuntimeError("Unexpected activity API response. Expected list.")

        for row in rows:
            row["_queriedWallet"] = wallet
            row["_collectionTimeUTC"] = datetime.now(timezone.utc).isoformat()

        all_rows.extend(rows)

        if len(rows) < LIMIT:
            break

        time.sleep(0.25)

    return all_rows


def normalize_activity_rows(raw_rows, market_rows):
    market_map = {
        normalize_0x(row["conditionId"]): row
        for row in market_rows
    }

    seen = set()
    output = []

    deadline_ts = parse_iso_to_ts(MARKET_DEADLINE_UTC)
    settlement_ts = parse_iso_to_ts(FINAL_SETTLEMENT_UTC)

    for row in raw_rows:
        condition_id = normalize_0x(row.get("conditionId", ""))
        market_info = market_map.get(condition_id, {})

        timestamp = int(row.get("timestamp") or 0)

        if timestamp:
            time_utc = datetime.fromtimestamp(timestamp, tz=timezone.utc).isoformat()
        else:
            time_utc = ""

        tx_hash = str(row.get("transactionHash", ""))
        wallet = normalize_0x(row.get("proxyWallet", "") or row.get("_queriedWallet", ""))
        activity_type = str(row.get("type", "")).upper()
        side = str(row.get("side", "")).upper()

        unique_key = (
            wallet,
            condition_id,
            tx_hash,
            timestamp,
            activity_type,
            side,
            str(row.get("asset", "")),
            str(row.get("size", "")),
        )

        if unique_key in seen:
            continue

        seen.add(unique_key)

        if timestamp and timestamp < deadline_ts:
            deadline_bucket = "Before market deadline"
        elif timestamp and timestamp < settlement_ts:
            deadline_bucket = "After deadline, before final settlement"
        elif timestamp:
            deadline_bucket = "After final settlement"
        else:
            deadline_bucket = "Unknown time"

        output.append({
            "proxyWallet": wallet,
            "queriedWallet": normalize_0x(row.get("_queriedWallet", "")),
            "timestamp": timestamp,
            "activityTimeUTC": time_utc,
            "deadlineBucket": deadline_bucket,
            "conditionId": condition_id,
            "marketRelationType": market_info.get("relationType", ""),
            "marketQuestion": market_info.get("question", ""),
            "marketSlug": market_info.get("slug", ""),
            "marketEndDate": market_info.get("endDate", ""),
            "type": activity_type,
            "side": side,
            "outcome": row.get("outcome", ""),
            "outcomeIndex": row.get("outcomeIndex", ""),
            "asset": str(row.get("asset", "")),
            "size": safe_float(row.get("size")),
            "usdcSize": safe_float(row.get("usdcSize")),
            "price": safe_float(row.get("price")),
            "transactionHash": tx_hash,
            "title": row.get("title", ""),
            "slug": row.get("slug", ""),
            "eventSlug": row.get("eventSlug", ""),
            "name": row.get("name", ""),
            "pseudonym": row.get("pseudonym", ""),
            "bio": row.get("bio", ""),
            "isCombo": row.get("isCombo", ""),
            "_collectionTimeUTC": row.get("_collectionTimeUTC", ""),
        })

    output.sort(key=lambda r: (r["timestamp"], r["proxyWallet"], r["conditionId"]))

    return output


def load_uma_wallets(path):
    wallets = set()

    if not os.path.exists(path):
        return wallets

    df = pd.read_csv(path)

    for col in ["eventVoter", "eventCaller", "workbookStaker", "workbookDelegate"]:
        if col not in df.columns:
            continue

        for value in df[col].dropna().astype(str):
            wallet = normalize_0x(value)

            if valid_wallet(wallet):
                wallets.add(wallet)

    return wallets


def build_direct_uma_matches(activity_rows, uma_wallets):
    output = []

    for row in activity_rows:
        wallet = normalize_0x(row.get("proxyWallet", ""))

        if wallet in uma_wallets:
            status = "DIRECT_MATCH_TO_UMA_WALLET"
        else:
            status = "NO_DIRECT_MATCH"

        output.append({
            "proxyWallet": wallet,
            "matchStatus": status,
            "activityTimeUTC": row.get("activityTimeUTC", ""),
            "deadlineBucket": row.get("deadlineBucket", ""),
            "conditionId": row.get("conditionId", ""),
            "marketRelationType": row.get("marketRelationType", ""),
            "type": row.get("type", ""),
            "side": row.get("side", ""),
            "outcome": row.get("outcome", ""),
            "size": row.get("size", ""),
            "usdcSize": row.get("usdcSize", ""),
            "price": row.get("price", ""),
            "transactionHash": row.get("transactionHash", ""),
            "name": row.get("name", ""),
            "pseudonym": row.get("pseudonym", ""),
        })

    return output


def write_hashes():
    files = [
        SUSPECTED_WALLETS_CSV,
        RELATED_MARKETS_CSV,
        RAW_ACTIVITY_JSON,
        NORMALIZED_ACTIVITY_CSV,
        TARGET_ACTIVITY_CSV,
        FUTURE_RELATED_ACTIVITY_CSV,
        REDEEMS_SPLITS_MERGES_CSV,
        DIRECT_UMA_MATCHES_CSV,
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


def write_summary(wallets, markets, activity_rows, target_rows, future_rows, special_rows, direct_matches):
    direct_match_count = len([
        row for row in direct_matches
        if row["matchStatus"] == "DIRECT_MATCH_TO_UMA_WALLET"
    ])

    yes_future_rows = [
        row for row in future_rows
        if str(row.get("outcome", "")).lower() == "yes"
    ]

    yes_future_usdc = sum(safe_float(row.get("usdcSize")) for row in yes_future_rows)

    lines = []

    lines.append("Step 8 User Activity Summary")
    lines.append("")
    lines.append(f"Collected at UTC: {datetime.now(timezone.utc).isoformat()}")
    lines.append(f"Activity window UTC: {START_UTC} through {END_UTC}")
    lines.append(f"Market deadline UTC: {MARKET_DEADLINE_UTC}")
    lines.append(f"Final settlement UTC: {FINAL_SETTLEMENT_UTC}")
    lines.append("")
    lines.append(f"Suspected wallets queried: {len(wallets)}")
    lines.append(f"Related markets checked: {len(markets)}")
    lines.append(f"Total normalized activity rows: {len(activity_rows)}")
    lines.append(f"Target market activity rows: {len(target_rows)}")
    lines.append(f"Future or related market activity rows: {len(future_rows)}")
    lines.append(f"Redeem / split / merge rows: {len(special_rows)}")
    lines.append(f"Direct activity-wallet to UMA-wallet matches: {direct_match_count}")
    lines.append("")
    lines.append("Future-pool review:")
    lines.append(f"YES activity rows on related non-target markets: {len(yes_future_rows)}")
    lines.append(f"Approximate USDC size for YES activity on related non-target markets: {yes_future_usdc}")
    lines.append("")
    lines.append("Important limitation:")
    lines.append("This output shows public activity for queried Polymarket profile wallets. It does not prove that a Polymarket proxy wallet is controlled by a UMA voter unless there is direct wallet equality or additional wallet-link evidence.")

    with open(SUMMARY_TXT, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))


def main():
    ensure_output_dir()

    market_identity = load_market_identity(MARKET_IDENTITY_CSV)

    if not valid_condition_id(market_identity["conditionId"]):
        raise RuntimeError("Invalid or missing target conditionId.")

    suspected_wallets = build_suspected_wallets()
    write_csv(SUSPECTED_WALLETS_CSV, suspected_wallets)

    markets = build_market_list(market_identity)
    write_csv(RELATED_MARKETS_CSV, markets)

    condition_ids = [row["conditionId"] for row in markets if valid_condition_id(row["conditionId"])]

    print("Suspected wallets:", len(suspected_wallets))
    print("Markets checked:", len(condition_ids))

    raw_activity = []

    for wallet_row in suspected_wallets:
        wallet = wallet_row["wallet"]

        if not valid_wallet(wallet):
            continue

        raw_activity.extend(fetch_activity_for_wallet(wallet, condition_ids))
        time.sleep(0.25)

    with open(RAW_ACTIVITY_JSON, "w", encoding="utf-8") as f:
        json.dump(raw_activity, f, indent=2, ensure_ascii=False)

    normalized = normalize_activity_rows(raw_activity, markets)
    write_csv(NORMALIZED_ACTIVITY_CSV, normalized)

    target_condition_id = market_identity["conditionId"].lower()

    target_rows = [
        row for row in normalized
        if row["conditionId"].lower() == target_condition_id
    ]
    write_csv(TARGET_ACTIVITY_CSV, target_rows)

    future_rows = [
        row for row in normalized
        if row["conditionId"].lower() != target_condition_id
    ]
    write_csv(FUTURE_RELATED_ACTIVITY_CSV, future_rows)

    special_rows = [
        row for row in normalized
        if row["type"] in ["REDEEM", "SPLIT", "MERGE"]
    ]
    write_csv(REDEEMS_SPLITS_MERGES_CSV, special_rows)

    uma_wallets = load_uma_wallets(UMA_VALIDATION_CSV)
    direct_matches = build_direct_uma_matches(normalized, uma_wallets)
    write_csv(DIRECT_UMA_MATCHES_CSV, direct_matches)

    write_summary(
        suspected_wallets,
        markets,
        normalized,
        target_rows,
        future_rows,
        special_rows,
        direct_matches,
    )

    write_hashes()

    print("")
    print("Saved outputs:")
    print(SUSPECTED_WALLETS_CSV)
    print(RELATED_MARKETS_CSV)
    print(RAW_ACTIVITY_JSON)
    print(NORMALIZED_ACTIVITY_CSV)
    print(TARGET_ACTIVITY_CSV)
    print(FUTURE_RELATED_ACTIVITY_CSV)
    print(REDEEMS_SPLITS_MERGES_CSV)
    print(DIRECT_UMA_MATCHES_CSV)
    print(SUMMARY_TXT)
    print(HASHES_CSV)
    print("")
    print("Done.")


if __name__ == "__main__":
    main()