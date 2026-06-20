import csv
import hashlib
import json
import os
import time
from datetime import datetime, timezone

import pandas as pd
import requests


ALL_RELATED_YES_BUYERS_CSV = r"C:\Users\user\Documents\POLYMARKET CASE EVIDENCE\01_ORIGINAL_EVIDENCE\Trade History\step8_CROSS_MARKET_YES_BUYERS\cross_market_yes_buyer_outputs\03_all_related_market_yes_buyers.csv"
CROSS_MARKET_WALLET_SUMMARY_CSV = r"C:\Users\user\Documents\POLYMARKET CASE EVIDENCE\01_ORIGINAL_EVIDENCE\Trade History\step8_CROSS_MARKET_YES_BUYERS\cross_market_yes_buyer_outputs\04_cross_market_wallet_summary.csv"

OUTPUT_DIR = "step8_future_activity_repair_outputs"

ACTIVITY_URL = "https://data-api.polymarket.com/activity"

LIMIT = 500
MAX_OFFSET = 10000

START_UTC = "2026-06-15T04:00:00+00:00"
END_UTC = "2026-06-19T04:00:00+00:00"

MARKET_DEADLINE_UTC = "2026-06-16T03:59:00+00:00"
FINAL_SETTLEMENT_UTC = "2026-06-18T00:32:19+00:00"

RELATED_MARKETS_USED_CSV = os.path.join(OUTPUT_DIR, "01_related_markets_used.csv")
WALLETS_USED_CSV = os.path.join(OUTPUT_DIR, "02_wallets_used.csv")
RAW_ACTIVITY_JSON = os.path.join(OUTPUT_DIR, "03_future_market_activity_raw.json")
NORMALIZED_ACTIVITY_CSV = os.path.join(OUTPUT_DIR, "04_future_market_activity_normalized.csv")
FUTURE_ACTIVITY_ONLY_CSV = os.path.join(OUTPUT_DIR, "05_future_related_market_activity_v2.csv")
REDEEMS_SPLITS_MERGES_CSV = os.path.join(OUTPUT_DIR, "06_future_redeems_splits_merges_v2.csv")
SUMMARY_TXT = os.path.join(OUTPUT_DIR, "07_future_activity_repair_summary.txt")
HASHES_CSV = os.path.join(OUTPUT_DIR, "08_future_activity_repair_hashes.csv")


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


def load_related_markets():
    df = pd.read_csv(ALL_RELATED_YES_BUYERS_CSV)

    required = ["conditionId", "marketRelationType", "marketQuestion", "marketSlug"]

    for col in required:
        if col not in df.columns:
            raise RuntimeError(f"Missing required column in {ALL_RELATED_YES_BUYERS_CSV}: {col}")

    markets = {}

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
                "yesTokenId": str(row.get("yesTokenId", "")),
            }

    output = list(markets.values())
    output.sort(key=lambda r: (r["marketRelationType"], r["marketEndDate"], r["marketSlug"]))

    return output


def load_wallets():
    df = pd.read_csv(CROSS_MARKET_WALLET_SUMMARY_CSV)

    if "proxyWallet" not in df.columns:
        raise RuntimeError(f"Missing proxyWallet column in {CROSS_MARKET_WALLET_SUMMARY_CSV}")

    wallets = {}

    for _, row in df.iterrows():
        pattern = str(row.get("pattern", ""))

        if pattern not in [
            "BOUGHT_TARGET_AND_FUTURE_MARKETS",
            "BOUGHT_FUTURE_MARKETS_ONLY",
        ]:
            continue
        wallet = normalize_0x(row.get("proxyWallet", ""))

        if not valid_wallet(wallet):
            continue

        wallets[wallet] = {
            "proxyWallet": wallet,
            "pattern": str(row.get("pattern", "")),
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


def fetch_activity_for_wallet_market(wallet, market):
    condition_id = market["conditionId"]

    start_ts = parse_iso_to_ts(START_UTC)
    end_ts = parse_iso_to_ts(END_UTC)

    rows_all = []

    for offset in range(0, MAX_OFFSET + 1, LIMIT):
        params = {
            "user": wallet,
            "market": condition_id,
            "start": start_ts,
            "end": end_ts,
            "limit": LIMIT,
            "offset": offset,
            "sortBy": "TIMESTAMP",
            "sortDirection": "ASC",
        }

        print(f"Fetching activity wallet {wallet} market {condition_id} offset {offset}")

        response = requests.get(ACTIVITY_URL, params=params, timeout=60)

        if response.status_code != 200:
            print("HTTP status:", response.status_code)
            print(response.text[:2000])
            raise RuntimeError("Activity API request failed.")

        rows = response.json()

        if not isinstance(rows, list):
            print(rows)
            raise RuntimeError("Unexpected activity response. Expected list.")

        for row in rows:
            row["_queriedWallet"] = wallet
            row["_queriedConditionId"] = condition_id
            row["_marketRelationTypeFromTradeFile"] = market.get("marketRelationType", "")
            row["_marketQuestionFromTradeFile"] = market.get("marketQuestion", "")
            row["_marketSlugFromTradeFile"] = market.get("marketSlug", "")
            row["_marketEndDateFromTradeFile"] = market.get("marketEndDate", "")
            row["_collectionTimeUTC"] = datetime.now(timezone.utc).isoformat()

        rows_all.extend(rows)

        print(f"Rows returned: {len(rows)}")

        if len(rows) < LIMIT:
            break

        time.sleep(0.15)

    return rows_all


def normalize_activity(raw_rows, wallets_by_address):
    wallet_set = set(wallets_by_address.keys())

    deadline_ts = parse_iso_to_ts(MARKET_DEADLINE_UTC)
    settlement_ts = parse_iso_to_ts(FINAL_SETTLEMENT_UTC)

    seen = set()
    output = []

    for row in raw_rows:
        proxy_wallet = normalize_0x(row.get("proxyWallet", ""))

        if proxy_wallet not in wallet_set:
            continue

        condition_id = normalize_0x(row.get("conditionId", "") or row.get("_queriedConditionId", ""))

        timestamp = int(row.get("timestamp") or 0)

        if timestamp:
            activity_time_utc = datetime.fromtimestamp(timestamp, tz=timezone.utc).isoformat()
        else:
            activity_time_utc = ""

        if timestamp and timestamp < deadline_ts:
            deadline_bucket = "Before market deadline"
        elif timestamp and timestamp < settlement_ts:
            deadline_bucket = "After deadline, before final settlement"
        elif timestamp:
            deadline_bucket = "After final settlement"
        else:
            deadline_bucket = "Unknown time"

        tx_hash = str(row.get("transactionHash", ""))

        unique_key = (
            proxy_wallet,
            condition_id,
            tx_hash,
            timestamp,
            str(row.get("type", "")),
            str(row.get("side", "")),
            str(row.get("asset", "")),
            str(row.get("size", "")),
            str(row.get("usdcSize", "")),
        )

        if unique_key in seen:
            continue

        seen.add(unique_key)

        wallet_info = wallets_by_address.get(proxy_wallet, {})

        output.append({
            "proxyWallet": proxy_wallet,
            "walletPattern": wallet_info.get("pattern", ""),
            "walletTotalYESNotionalUSDC": wallet_info.get("totalYESNotionalUSDC", ""),
            "walletFutureYESNotionalUSDC": wallet_info.get("futureMarketYESNotionalUSDC", ""),
            "timestamp": timestamp,
            "activityTimeUTC": activity_time_utc,
            "deadlineBucket": deadline_bucket,
            "conditionId": condition_id,
            "marketRelationType": row.get("_marketRelationTypeFromTradeFile", ""),
            "marketQuestion": row.get("_marketQuestionFromTradeFile", ""),
            "marketSlug": row.get("_marketSlugFromTradeFile", ""),
            "marketEndDate": row.get("_marketEndDateFromTradeFile", ""),
            "type": str(row.get("type", "")).upper(),
            "side": str(row.get("side", "")).upper(),
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


def write_summary(markets, wallets, raw_rows, normalized, future_rows, special_rows):
    relation_counts = {}

    for row in future_rows:
        relation = row.get("marketRelationType", "")
        relation_counts[relation] = relation_counts.get(relation, 0) + 1

    type_counts = {}

    for row in normalized:
        t = row.get("type", "")
        type_counts[t] = type_counts.get(t, 0) + 1

    lines = []

    lines.append("Step 8 Future Activity Repair Summary")
    lines.append("")
    lines.append(f"Collected at UTC: {datetime.now(timezone.utc).isoformat()}")
    lines.append(f"Activity window UTC: {START_UTC} through {END_UTC}")
    lines.append(f"Markets queried: {len(markets)}")
    lines.append(f"Cross-market wallets used: {len(wallets)}")
    lines.append(f"Raw activity rows collected: {len(raw_rows)}")
    lines.append(f"Normalized activity rows for cross-market wallets: {len(normalized)}")
    lines.append(f"Future related market activity rows: {len(future_rows)}")
    lines.append(f"Redeem / split / merge rows: {len(special_rows)}")
    lines.append("")
    lines.append("Market relation counts:")
    for key, value in sorted(relation_counts.items()):
        lines.append(f"{key}: {value}")
    lines.append("")
    lines.append("Activity type counts:")
    for key, value in sorted(type_counts.items()):
        lines.append(f"{key}: {value}")
    lines.append("")
    lines.append("Interpretation:")
    lines.append("This repair run queries each related market one at a time, rather than using a comma-separated market list. It is intended to fill the missing future-related activity file from the earlier Step 8 run.")

    with open(SUMMARY_TXT, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))


def write_hashes():
    files = [
        RELATED_MARKETS_USED_CSV,
        WALLETS_USED_CSV,
        RAW_ACTIVITY_JSON,
        NORMALIZED_ACTIVITY_CSV,
        FUTURE_ACTIVITY_ONLY_CSV,
        REDEEMS_SPLITS_MERGES_CSV,
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


def build_wallet_market_pairs(wallets, market_by_condition):
    df = pd.read_csv(ALL_RELATED_YES_BUYERS_CSV)

    required = ["proxyWallet", "conditionId", "marketRelationType"]

    for col in required:
        if col not in df.columns:
            raise RuntimeError(f"Missing required column in {ALL_RELATED_YES_BUYERS_CSV}: {col}")

    wallet_set = set(wallets.keys())

    seen = set()
    pairs = []

    for _, row in df.iterrows():
        wallet = normalize_0x(row.get("proxyWallet", ""))
        condition_id = normalize_0x(row.get("conditionId", ""))

        if wallet not in wallet_set:
            continue

        if condition_id.lower() not in market_by_condition:
            continue

        key = (wallet, condition_id.lower())

        if key in seen:
            continue

        seen.add(key)

        pairs.append({
            "wallet": wallet,
            "conditionId": condition_id,
            "market": market_by_condition[condition_id.lower()],
        })

    pairs.sort(key=lambda r: (r["wallet"], r["conditionId"]))

    return pairs

def main():
    ensure_output_dir()

    markets = load_related_markets()
    wallets = load_wallets()

    write_csv(RELATED_MARKETS_USED_CSV, markets)
    write_csv(WALLETS_USED_CSV, list(wallets.values()))

    print("Markets loaded:", len(markets))
    print("Wallets loaded:", len(wallets))

    raw_rows = []

    market_by_condition = {
        market["conditionId"].lower(): market
        for market in markets
    }

    pairs = build_wallet_market_pairs(wallets, market_by_condition)

    print("")
    print("Wallet-market pairs to query:", len(pairs))

    for pair_index, pair in enumerate(pairs, start=1):
        wallet = pair["wallet"]
        market = pair["market"]

        print("")
        print(f"Pair {pair_index} of {len(pairs)}")
        print("Wallet:", wallet)
        print("Market:", market.get("marketQuestion", ""))
        print("Condition ID:", market.get("conditionId", ""))

        raw_rows.extend(fetch_activity_for_wallet_market(wallet, market))
        time.sleep(0.05)

    with open(RAW_ACTIVITY_JSON, "w", encoding="utf-8") as f:
        json.dump(raw_rows, f, indent=2, ensure_ascii=False)

    normalized = normalize_activity(raw_rows, wallets)

    write_csv(NORMALIZED_ACTIVITY_CSV, normalized)

    future_rows = [
        row for row in normalized
        if row["marketRelationType"] == "RELATED_OR_FUTURE_MARKET"
    ]

    write_csv(FUTURE_ACTIVITY_ONLY_CSV, future_rows)

    special_rows = [
        row for row in normalized
        if row["type"] in ["REDEEM", "SPLIT", "MERGE"]
    ]

    write_csv(REDEEMS_SPLITS_MERGES_CSV, special_rows)

    write_summary(markets, wallets, raw_rows, normalized, future_rows, special_rows)
    write_hashes()

    print("")
    print("Saved outputs:")
    print(RELATED_MARKETS_USED_CSV)
    print(WALLETS_USED_CSV)
    print(RAW_ACTIVITY_JSON)
    print(NORMALIZED_ACTIVITY_CSV)
    print(FUTURE_ACTIVITY_ONLY_CSV)
    print(REDEEMS_SPLITS_MERGES_CSV)
    print(SUMMARY_TXT)
    print(HASHES_CSV)
    print("")
    print("Done.")


if __name__ == "__main__":
    main()