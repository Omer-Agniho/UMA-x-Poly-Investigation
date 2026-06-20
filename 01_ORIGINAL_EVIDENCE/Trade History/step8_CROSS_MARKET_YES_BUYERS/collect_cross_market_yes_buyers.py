import csv
import hashlib
import json
import os
import time
from datetime import datetime, timezone

import pandas as pd
import requests


GAMMA_EVENT_JSON = r"C:\Users\user\Documents\POLYMARKET CASE EVIDENCE\01_ORIGINAL_EVIDENCE\Market Identity\step4_market_identity_outputs\03_gamma_event_raw.json"
MARKET_IDENTITY_CSV = r"C:\Users\user\Documents\POLYMARKET CASE EVIDENCE\01_ORIGINAL_EVIDENCE\Market Identity\step4_market_identity_outputs\05_market_identity.csv"
UMA_VALIDATION_CSV = r"C:\Users\user\Documents\POLYMARKET CASE EVIDENCE\01_ORIGINAL_EVIDENCE\UMA Votes x Yes Shares\uma_vote_validation.csv"

OUTPUT_DIR = "cross_market_yes_buyer_outputs"

RELATED_MARKETS_CSV = os.path.join(OUTPUT_DIR, "01_related_iran_peace_markets.csv")
RAW_TRADES_JSON = os.path.join(OUTPUT_DIR, "02_cross_market_trades_raw.json")
YES_BUYERS_CSV = os.path.join(OUTPUT_DIR, "03_all_related_market_yes_buyers.csv")
CROSS_MARKET_WALLETS_CSV = os.path.join(OUTPUT_DIR, "04_cross_market_wallet_summary.csv")
UMA_MATCH_CSV = os.path.join(OUTPUT_DIR, "05_cross_market_yes_buyers_vs_uma.csv")
SUMMARY_TXT = os.path.join(OUTPUT_DIR, "06_cross_market_summary.txt")
HASHES_CSV = os.path.join(OUTPUT_DIR, "07_cross_market_file_hashes.csv")

TRADES_URL = "https://data-api.polymarket.com/trades"

LIMIT = 10000
MAX_OFFSET = 10000

MARKET_DEADLINE_UTC = "2026-06-16T03:59:00+00:00"
FINAL_SETTLEMENT_UTC = "2026-06-18T00:32:19+00:00"


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


def valid_condition_id(value):
    value = normalize_0x(value)
    return len(value) == 66


def valid_wallet(value):
    value = normalize_0x(value)
    return len(value) == 42


def safe_float(value):
    try:
        return float(value or 0)
    except Exception:
        return 0.0


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


def load_market_identity():
    df = pd.read_csv(MARKET_IDENTITY_CSV)

    if "field" not in df.columns or "value" not in df.columns:
        raise RuntimeError("05_market_identity.csv must have columns named field and value.")

    identity = dict(zip(df["field"].astype(str), df["value"].astype(str)))

    return {
        "targetConditionId": normalize_0x(identity.get("conditionId", "")),
        "targetQuestion": str(identity.get("question", "")).strip(),
        "targetMarketSlug": str(identity.get("marketSlug", "")).strip(),
        "targetYesTokenId": str(identity.get("yesTokenId", "")).strip(),
        "targetNoTokenId": str(identity.get("noTokenId", "")).strip(),
    }


def parse_market_from_gamma(market, target_condition_id):
    question = str(market.get("question", "") or market.get("title", "")).strip()
    slug = str(market.get("slug", "")).strip()
    condition_id = normalize_0x(market.get("conditionId", ""))

    if not valid_condition_id(condition_id):
        return None

    text = (question + " " + slug).lower()

    looks_related = (
        "iran" in text
        and "peace" in text
    )

    if not looks_related and condition_id != target_condition_id:
        return None

    outcomes = read_jsonish(market.get("outcomes"))
    token_ids = read_jsonish(market.get("clobTokenIds"))

    yes_token_id = ""
    no_token_id = ""

    for i, outcome in enumerate(outcomes):
        if i >= len(token_ids):
            continue

        outcome_text = str(outcome).strip().lower()

        if outcome_text == "yes":
            yes_token_id = str(token_ids[i])

        if outcome_text == "no":
            no_token_id = str(token_ids[i])

    relation_type = "TARGET_JUNE_15_MARKET" if condition_id == target_condition_id else "RELATED_OR_FUTURE_MARKET"

    return {
        "conditionId": condition_id,
        "relationType": relation_type,
        "marketId": market.get("id", ""),
        "question": question,
        "slug": slug,
        "endDate": market.get("endDate", "") or market.get("endDateIso", ""),
        "questionID": normalize_0x(market.get("questionID", "")),
        "outcomes": json.dumps(outcomes),
        "clobTokenIds": json.dumps(token_ids),
        "yesTokenId": yes_token_id,
        "noTokenId": no_token_id,
    }


def load_related_markets(identity):
    target_condition_id = identity["targetConditionId"]

    if not os.path.exists(GAMMA_EVENT_JSON):
        raise RuntimeError("Missing 03_gamma_event_raw.json. Run Step 4 first or provide the event JSON.")

    with open(GAMMA_EVENT_JSON, "r", encoding="utf-8") as f:
        data = json.load(f)

    event_rows = data if isinstance(data, list) else [data]

    markets = {}

    for event in event_rows:
        for market in event.get("markets", []):
            parsed = parse_market_from_gamma(market, target_condition_id)
            if parsed:
                markets[parsed["conditionId"]] = parsed

    if target_condition_id not in markets:
        markets[target_condition_id] = {
            "conditionId": target_condition_id,
            "relationType": "TARGET_JUNE_15_MARKET",
            "marketId": "",
            "question": identity["targetQuestion"],
            "slug": identity["targetMarketSlug"],
            "endDate": "",
            "questionID": "",
            "outcomes": "",
            "clobTokenIds": "",
            "yesTokenId": identity["targetYesTokenId"],
            "noTokenId": identity["targetNoTokenId"],
        }

    output = list(markets.values())
    output.sort(key=lambda r: (r["relationType"], r["endDate"], r["slug"]))

    return output


def fetch_trades_for_market(market):
    condition_id = market["conditionId"]
    yes_token_id = str(market.get("yesTokenId", ""))

    if not yes_token_id:
        print("Skipping market without YES token:", market.get("question"))
        return []

    all_rows = []

    for offset in range(0, MAX_OFFSET + 1, LIMIT):
        params = {
            "market": condition_id,
            "side": "BUY",
            "limit": LIMIT,
            "offset": offset,
            "takerOnly": "false",
        }

        print(f"Fetching YES BUY trades for market={condition_id} offset={offset}")

        response = requests.get(TRADES_URL, params=params, timeout=60)

        if response.status_code != 200:
            print("HTTP status:", response.status_code)
            print(response.text[:2000])
            raise RuntimeError("Polymarket trades API request failed.")

        rows = response.json()

        if not isinstance(rows, list):
            print(rows)
            raise RuntimeError("Unexpected API response. Expected list.")

        for row in rows:
            asset = str(row.get("asset", "")).strip()
            outcome = str(row.get("outcome", "")).strip().lower()

            is_yes = asset == yes_token_id or outcome == "yes"

            if not is_yes:
                continue

            timestamp = int(row.get("timestamp") or 0)
            if timestamp:
                trade_time_utc = datetime.fromtimestamp(timestamp, tz=timezone.utc).isoformat()
            else:
                trade_time_utc = ""

            size = safe_float(row.get("size"))
            price = safe_float(row.get("price"))
            notional = size * price

            enriched = {
                "proxyWallet": normalize_0x(row.get("proxyWallet", "")),
                "conditionId": normalize_0x(row.get("conditionId", "")),
                "marketRelationType": market.get("relationType", ""),
                "marketQuestion": market.get("question", ""),
                "marketSlug": market.get("slug", ""),
                "marketEndDate": market.get("endDate", ""),
                "yesTokenId": yes_token_id,
                "side": str(row.get("side", "")).upper(),
                "outcome": row.get("outcome", ""),
                "asset": asset,
                "size": size,
                "price": price,
                "notionalUSDC": notional,
                "timestamp": timestamp,
                "tradeTimeUTC": trade_time_utc,
                "transactionHash": row.get("transactionHash", ""),
                "name": row.get("name", ""),
                "pseudonym": row.get("pseudonym", ""),
                "title": row.get("title", ""),
                "slug": row.get("slug", ""),
                "eventSlug": row.get("eventSlug", ""),
                "_collectionTimeUTC": datetime.now(timezone.utc).isoformat(),
            }

            all_rows.append(enriched)

        print("Rows returned:", len(rows), "YES rows kept so far:", len(all_rows))

        if len(rows) < LIMIT:
            break

        time.sleep(0.4)

    return all_rows


def load_uma_wallets():
    wallets = set()

    if not os.path.exists(UMA_VALIDATION_CSV):
        return wallets

    df = pd.read_csv(UMA_VALIDATION_CSV)

    for col in ["eventVoter", "eventCaller", "workbookStaker", "workbookDelegate"]:
        if col not in df.columns:
            continue

        for value in df[col].dropna().astype(str):
            wallet = normalize_0x(value)

            if valid_wallet(wallet):
                wallets.add(wallet)

    return wallets


def build_wallet_summary(yes_buys):
    wallets = {}

    for row in yes_buys:
        wallet = normalize_0x(row["proxyWallet"])

        if not valid_wallet(wallet):
            continue

        if wallet not in wallets:
            wallets[wallet] = {
                "proxyWallet": wallet,
                "marketsBoughtYES": set(),
                "targetMarketYESBuyCount": 0,
                "futureMarketYESBuyCount": 0,
                "targetMarketYESNotionalUSDC": 0.0,
                "futureMarketYESNotionalUSDC": 0.0,
                "totalYESNotionalUSDC": 0.0,
                "earliestYESBuyUTC": "",
                "latestYESBuyUTC": "",
                "names": set(),
                "pseudonyms": set(),
            }

        info = wallets[wallet]
        info["marketsBoughtYES"].add(row["conditionId"])

        notional = safe_float(row["notionalUSDC"])
        info["totalYESNotionalUSDC"] += notional

        if row["marketRelationType"] == "TARGET_JUNE_15_MARKET":
            info["targetMarketYESBuyCount"] += 1
            info["targetMarketYESNotionalUSDC"] += notional
        else:
            info["futureMarketYESBuyCount"] += 1
            info["futureMarketYESNotionalUSDC"] += notional

        trade_time = row["tradeTimeUTC"]

        if trade_time:
            if not info["earliestYESBuyUTC"] or trade_time < info["earliestYESBuyUTC"]:
                info["earliestYESBuyUTC"] = trade_time

            if not info["latestYESBuyUTC"] or trade_time > info["latestYESBuyUTC"]:
                info["latestYESBuyUTC"] = trade_time

        if row.get("name"):
            info["names"].add(str(row["name"]))

        if row.get("pseudonym"):
            info["pseudonyms"].add(str(row["pseudonym"]))

    output = []

    for wallet, info in wallets.items():
        if info["targetMarketYESBuyCount"] > 0 and info["futureMarketYESBuyCount"] > 0:
            pattern = "BOUGHT_TARGET_AND_FUTURE_MARKETS"
        elif info["targetMarketYESBuyCount"] > 0:
            pattern = "BOUGHT_TARGET_MARKET_ONLY"
        elif info["futureMarketYESBuyCount"] > 0:
            pattern = "BOUGHT_FUTURE_MARKETS_ONLY"
        else:
            pattern = "UNKNOWN"

        output.append({
            "proxyWallet": wallet,
            "pattern": pattern,
            "uniqueMarketsBoughtYES": len(info["marketsBoughtYES"]),
            "targetMarketYESBuyCount": info["targetMarketYESBuyCount"],
            "futureMarketYESBuyCount": info["futureMarketYESBuyCount"],
            "targetMarketYESNotionalUSDC": round(info["targetMarketYESNotionalUSDC"], 6),
            "futureMarketYESNotionalUSDC": round(info["futureMarketYESNotionalUSDC"], 6),
            "totalYESNotionalUSDC": round(info["totalYESNotionalUSDC"], 6),
            "earliestYESBuyUTC": info["earliestYESBuyUTC"],
            "latestYESBuyUTC": info["latestYESBuyUTC"],
            "names": "; ".join(sorted(info["names"])),
            "pseudonyms": "; ".join(sorted(info["pseudonyms"])),
        })

    output.sort(
        key=lambda r: (
            r["pattern"] != "BOUGHT_FUTURE_MARKETS_ONLY",
            -r["totalYESNotionalUSDC"],
        )
    )

    return output


def build_uma_match_rows(wallet_summary, uma_wallets):
    rows = []

    for row in wallet_summary:
        wallet = normalize_0x(row["proxyWallet"])

        if wallet in uma_wallets:
            status = "DIRECT_MATCH_TO_UMA_WALLET"
        else:
            status = "NO_DIRECT_MATCH"

        out = dict(row)
        out["umaDirectMatchStatus"] = status
        rows.append(out)

    return rows


def write_summary(markets, yes_buys, wallet_summary, uma_matches):
    future_only = [r for r in wallet_summary if r["pattern"] == "BOUGHT_FUTURE_MARKETS_ONLY"]
    target_and_future = [r for r in wallet_summary if r["pattern"] == "BOUGHT_TARGET_AND_FUTURE_MARKETS"]
    target_only = [r for r in wallet_summary if r["pattern"] == "BOUGHT_TARGET_MARKET_ONLY"]
    direct_uma = [r for r in uma_matches if r["umaDirectMatchStatus"] == "DIRECT_MATCH_TO_UMA_WALLET"]

    lines = []

    lines.append("Cross-Market YES Buyer Summary")
    lines.append("")
    lines.append(f"Collected at UTC: {datetime.now(timezone.utc).isoformat()}")
    lines.append(f"Markets scanned: {len(markets)}")
    lines.append(f"YES BUY trade rows collected: {len(yes_buys)}")
    lines.append(f"Unique YES buyer proxyWallets: {len(wallet_summary)}")
    lines.append("")
    lines.append(f"Wallets that bought target June 15 market only: {len(target_only)}")
    lines.append(f"Wallets that bought target and future related markets: {len(target_and_future)}")
    lines.append(f"Wallets that bought future related markets only: {len(future_only)}")
    lines.append(f"Direct matches to UMA wallets: {len(direct_uma)}")
    lines.append("")
    lines.append("Interpretation note:")
    lines.append("Future-market-only YES buyers are not proof of wrongdoing. They are a lead category for review because they may show cross-market positioning that would not appear if the investigation only starts from June 15 YES buyers.")
    lines.append("")
    lines.append("Suggested legal wording:")
    lines.append("The cross-market export identifies wallets that purchased YES on related future-date Iran peace-deal markets, including wallets that did not appear as YES buyers on the June 15 market. These records should be reviewed for timing, size, wallet links, and whether the later markets depended on the same disputed factual premise.")

    with open(SUMMARY_TXT, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))


def write_hashes():
    files = [
        RELATED_MARKETS_CSV,
        RAW_TRADES_JSON,
        YES_BUYERS_CSV,
        CROSS_MARKET_WALLETS_CSV,
        UMA_MATCH_CSV,
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


def main():
    ensure_output_dir()

    identity = load_market_identity()
    markets = load_related_markets(identity)

    write_csv(RELATED_MARKETS_CSV, markets)

    print("Related markets found:", len(markets))

    all_yes_buys = []
    raw_by_market = []

    for market in markets:
        rows = fetch_trades_for_market(market)

        raw_by_market.append({
            "conditionId": market["conditionId"],
            "relationType": market["relationType"],
            "question": market["question"],
            "rows": rows,
        })

        all_yes_buys.extend(rows)
        time.sleep(0.5)

    with open(RAW_TRADES_JSON, "w", encoding="utf-8") as f:
        json.dump(raw_by_market, f, indent=2, ensure_ascii=False)

    write_csv(YES_BUYERS_CSV, all_yes_buys)

    wallet_summary = build_wallet_summary(all_yes_buys)
    write_csv(CROSS_MARKET_WALLETS_CSV, wallet_summary)

    uma_wallets = load_uma_wallets()
    uma_matches = build_uma_match_rows(wallet_summary, uma_wallets)
    write_csv(UMA_MATCH_CSV, uma_matches)

    write_summary(markets, all_yes_buys, wallet_summary, uma_matches)
    write_hashes()

    print("")
    print("Saved outputs:")
    print(RELATED_MARKETS_CSV)
    print(RAW_TRADES_JSON)
    print(YES_BUYERS_CSV)
    print(CROSS_MARKET_WALLETS_CSV)
    print(UMA_MATCH_CSV)
    print(SUMMARY_TXT)
    print(HASHES_CSV)
    print("")
    print("Done.")


if __name__ == "__main__":
    main()