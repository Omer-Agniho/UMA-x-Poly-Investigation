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

OUTPUT_DIR = "step7_trade_history_outputs"

RAW_TRADES_JSON = os.path.join(OUTPUT_DIR, "01_polymarket_trades_raw.json")
NORMALIZED_TRADES_CSV = os.path.join(OUTPUT_DIR, "02_polymarket_trades_normalized.csv")
YES_TRADES_CSV = os.path.join(OUTPUT_DIR, "03_yes_trades_only.csv")
YES_BUYS_CSV = os.path.join(OUTPUT_DIR, "04_yes_buys_only.csv")
LARGE_YES_BUYS_CSV = os.path.join(OUTPUT_DIR, "05_large_yes_buys.csv")
UMA_WALLET_MATCH_CSV = os.path.join(OUTPUT_DIR, "06_trade_wallets_vs_uma_wallets.csv")
SUMMARY_TXT = os.path.join(OUTPUT_DIR, "07_step7_trade_history_summary.txt")
HASHES_CSV = os.path.join(OUTPUT_DIR, "08_step7_file_hashes.csv")

DATA_API_TRADES_URL = "https://data-api.polymarket.com/trades"

LIMIT = 10000

LARGE_YES_BUY_SIZE_THRESHOLD = 1000

MARKET_DEADLINE_UTC = "2026-06-16T03:59:00+00:00"
FINAL_SETTLEMENT_UTC = "2026-06-18T00:32:19+00:00"


def ensure_output_dir():
    os.makedirs(OUTPUT_DIR, exist_ok=True)


def sha256_file(path):
    h = hashlib.sha256()

    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)

    return h.hexdigest()


def normalize_0x(value):
    if value is None:
        return ""

    value = str(value).strip().lower()

    if not value:
        return ""

    if not value.startswith("0x"):
        value = "0x" + value

    return value


def load_market_identity(path):
    df = pd.read_csv(path)

    if "field" in df.columns and "value" in df.columns:
        identity = dict(zip(df["field"].astype(str), df["value"].astype(str)))
    else:
        raise RuntimeError("05_market_identity.csv must have columns named field and value.")

    condition_id = normalize_0x(identity.get("conditionId", ""))
    yes_token_id = str(identity.get("yesTokenId", "")).strip()
    no_token_id = str(identity.get("noTokenId", "")).strip()
    market_slug = str(identity.get("marketSlug", "")).strip()
    question = str(identity.get("question", "")).strip()
    question_id = normalize_0x(identity.get("questionID", ""))

    if not condition_id or len(condition_id) != 66:
        raise RuntimeError("Missing or invalid conditionId in market identity CSV.")

    if not yes_token_id:
        raise RuntimeError("Missing yesTokenId in market identity CSV.")

    return {
        "conditionId": condition_id,
        "yesTokenId": yes_token_id,
        "noTokenId": no_token_id,
        "marketSlug": market_slug,
        "question": question,
        "questionID": question_id,
    }


def fetch_trades_for_side(condition_id, side, taker_only):
    all_rows = []

    for offset in [0, 10000]:
        params = {
            "market": condition_id,
            "side": side,
            "limit": LIMIT,
            "offset": offset,
            "takerOnly": str(taker_only).lower(),
        }

        print(f"Fetching trades side={side}, takerOnly={taker_only}, offset={offset}")

        response = requests.get(DATA_API_TRADES_URL, params=params, timeout=60)

        if response.status_code != 200:
            print("HTTP status:", response.status_code)
            print(response.text[:2000])
            raise RuntimeError("Polymarket Data API trade request failed.")

        rows = response.json()

        if not isinstance(rows, list):
            print(rows)
            raise RuntimeError("Unexpected trade API response. Expected a list.")

        for row in rows:
            row["_apiSideFilter"] = side
            row["_apiTakerOnlyFilter"] = taker_only
            row["_apiOffset"] = offset
            row["_collectionTimeUTC"] = datetime.now(timezone.utc).isoformat()

        all_rows.extend(rows)

        print(f"Rows returned: {len(rows)}")

        if len(rows) < LIMIT:
            break

        time.sleep(0.5)

    return all_rows


def fetch_all_trades(condition_id):
    raw = []

    for taker_only in [False, True]:
        for side in ["BUY", "SELL"]:
            raw.extend(fetch_trades_for_side(condition_id, side, taker_only))
            time.sleep(0.5)

    return raw


def normalize_trade_rows(raw_rows, market_identity):
    seen = set()
    rows = []

    condition_id = market_identity["conditionId"].lower()
    yes_token_id = str(market_identity["yesTokenId"])
    no_token_id = str(market_identity["noTokenId"])

    for row in raw_rows:
        tx_hash = str(row.get("transactionHash", "")).lower()
        proxy_wallet = normalize_0x(row.get("proxyWallet", ""))
        asset = str(row.get("asset", "")).strip()
        side = str(row.get("side", "")).strip().upper()
        size = float(row.get("size") or 0)
        price = float(row.get("price") or 0)
        timestamp = int(row.get("timestamp") or 0)
        row_condition_id = normalize_0x(row.get("conditionId", ""))

        unique_key = (
            tx_hash,
            proxy_wallet,
            asset,
            side,
            timestamp,
            str(size),
            str(price),
        )

        if unique_key in seen:
            continue

        seen.add(unique_key)

        if row_condition_id.lower() != condition_id:
            continue

        if asset == yes_token_id:
            token_side_by_asset = "YES"
        elif asset == no_token_id:
            token_side_by_asset = "NO"
        else:
            token_side_by_asset = "UNKNOWN"

        outcome = str(row.get("outcome", "")).strip()

        if timestamp:
            trade_time_utc = datetime.fromtimestamp(timestamp, tz=timezone.utc).isoformat()
        else:
            trade_time_utc = ""

        notional_usdc = size * price

        rows.append({
            "proxyWallet": proxy_wallet,
            "side": side,
            "asset": asset,
            "tokenSideByAsset": token_side_by_asset,
            "conditionId": row_condition_id,
            "size": size,
            "price": price,
            "notionalUSDC": notional_usdc,
            "timestamp": timestamp,
            "tradeTimeUTC": trade_time_utc,
            "title": row.get("title", ""),
            "slug": row.get("slug", ""),
            "eventSlug": row.get("eventSlug", ""),
            "outcome": outcome,
            "outcomeIndex": row.get("outcomeIndex", ""),
            "name": row.get("name", ""),
            "pseudonym": row.get("pseudonym", ""),
            "bio": row.get("bio", ""),
            "transactionHash": row.get("transactionHash", ""),
            "_apiSideFilter": row.get("_apiSideFilter", ""),
            "_apiTakerOnlyFilter": row.get("_apiTakerOnlyFilter", ""),
            "_apiOffset": row.get("_apiOffset", ""),
            "_collectionTimeUTC": row.get("_collectionTimeUTC", ""),
        })

    rows.sort(key=lambda r: r["timestamp"])

    return rows


def load_uma_wallets(path):
    if not os.path.exists(path):
        return set()

    df = pd.read_csv(path)

    wallets = set()

    for col in ["eventVoter", "eventCaller", "workbookStaker", "workbookDelegate"]:
        if col in df.columns:
            for value in df[col].dropna().astype(str):
                value = normalize_0x(value)
                if len(value) == 42:
                    wallets.add(value)

    return wallets


def write_csv(path, rows):
    if not rows:
        with open(path, "w", newline="", encoding="utf-8") as f:
            f.write("")
        return

    fieldnames = list(rows[0].keys())

    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def compare_trade_wallets_to_uma(rows, uma_wallets):
    output = []

    for row in rows:
        proxy_wallet = normalize_0x(row.get("proxyWallet", ""))

        if proxy_wallet in uma_wallets:
            match_status = "DIRECT_PROXY_WALLET_MATCH_TO_UMA_WALLET"
        else:
            match_status = "NO_DIRECT_MATCH"

        output.append({
            "proxyWallet": proxy_wallet,
            "matchStatus": match_status,
            "tokenSideByAsset": row.get("tokenSideByAsset", ""),
            "side": row.get("side", ""),
            "size": row.get("size", ""),
            "price": row.get("price", ""),
            "notionalUSDC": row.get("notionalUSDC", ""),
            "tradeTimeUTC": row.get("tradeTimeUTC", ""),
            "transactionHash": row.get("transactionHash", ""),
            "name": row.get("name", ""),
            "pseudonym": row.get("pseudonym", ""),
        })

    return output


def write_summary(market_identity, normalized, yes_trades, yes_buys, large_yes_buys, direct_matches):
    unique_traders = len(set(r["proxyWallet"] for r in normalized if r["proxyWallet"]))
    unique_yes_buyers = len(set(r["proxyWallet"] for r in yes_buys if r["proxyWallet"]))

    total_yes_buy_size = sum(float(r["size"]) for r in yes_buys)
    total_yes_buy_notional = sum(float(r["notionalUSDC"]) for r in yes_buys)

    lines = []

    lines.append("Step 7 Trade History Summary")
    lines.append("")
    lines.append(f"Collected at UTC: {datetime.now(timezone.utc).isoformat()}")
    lines.append(f"Market question: {market_identity.get('question')}")
    lines.append(f"Market slug: {market_identity.get('marketSlug')}")
    lines.append(f"Condition ID: {market_identity.get('conditionId')}")
    lines.append(f"YES token ID: {market_identity.get('yesTokenId')}")
    lines.append(f"NO token ID: {market_identity.get('noTokenId')}")
    lines.append("")
    lines.append(f"Normalized trade rows: {len(normalized)}")
    lines.append(f"YES trade rows: {len(yes_trades)}")
    lines.append(f"YES BUY rows: {len(yes_buys)}")
    lines.append(f"Large YES BUY rows, threshold {LARGE_YES_BUY_SIZE_THRESHOLD}: {len(large_yes_buys)}")
    lines.append(f"Unique proxyWallets in normalized trades: {unique_traders}")
    lines.append(f"Unique YES BUY proxyWallets: {unique_yes_buyers}")
    lines.append(f"Total YES BUY size: {total_yes_buy_size}")
    lines.append(f"Approximate YES BUY notional USDC: {total_yes_buy_notional}")
    lines.append("")
    lines.append(f"Market deadline UTC: {MARKET_DEADLINE_UTC}")
    lines.append(f"Final settlement UTC: {FINAL_SETTLEMENT_UTC}")
    lines.append("")
    lines.append(f"Direct proxyWallet to UMA-wallet matches found: {len([r for r in direct_matches if r['matchStatus'] != 'NO_DIRECT_MATCH'])}")
    lines.append("")
    lines.append("Important limitation:")
    lines.append("The Polymarket Data API trade endpoint may be limited by pagination. If a request returns the maximum limit at the highest offset, the output may be incomplete and should be supplemented with additional API queries or on-chain transfer analysis.")

    with open(SUMMARY_TXT, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))


def write_hashes():
    files = [
        RAW_TRADES_JSON,
        NORMALIZED_TRADES_CSV,
        YES_TRADES_CSV,
        YES_BUYS_CSV,
        LARGE_YES_BUYS_CSV,
        UMA_WALLET_MATCH_CSV,
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

    market_identity = load_market_identity(MARKET_IDENTITY_CSV)

    print("Market identity loaded:")
    print("Condition ID:", market_identity["conditionId"])
    print("YES token ID:", market_identity["yesTokenId"])
    print("NO token ID:", market_identity["noTokenId"])

    raw_trades = fetch_all_trades(market_identity["conditionId"])

    with open(RAW_TRADES_JSON, "w", encoding="utf-8") as f:
        json.dump(raw_trades, f, indent=2, ensure_ascii=False)

    print("Raw trade rows saved:", len(raw_trades))

    normalized = normalize_trade_rows(raw_trades, market_identity)
    write_csv(NORMALIZED_TRADES_CSV, normalized)

    yes_trades = [
        row for row in normalized
        if row["tokenSideByAsset"] == "YES"
    ]
    write_csv(YES_TRADES_CSV, yes_trades)

    yes_buys = [
        row for row in yes_trades
        if row["side"] == "BUY"
    ]
    write_csv(YES_BUYS_CSV, yes_buys)

    large_yes_buys = [
        row for row in yes_buys
        if float(row["size"]) >= LARGE_YES_BUY_SIZE_THRESHOLD
    ]
    write_csv(LARGE_YES_BUYS_CSV, large_yes_buys)

    uma_wallets = load_uma_wallets(UMA_VALIDATION_CSV)
    direct_matches = compare_trade_wallets_to_uma(yes_buys, uma_wallets)
    write_csv(UMA_WALLET_MATCH_CSV, direct_matches)

    write_summary(
        market_identity,
        normalized,
        yes_trades,
        yes_buys,
        large_yes_buys,
        direct_matches,
    )

    write_hashes()

    print("")
    print("Saved outputs:")
    print(RAW_TRADES_JSON)
    print(NORMALIZED_TRADES_CSV)
    print(YES_TRADES_CSV)
    print(YES_BUYS_CSV)
    print(LARGE_YES_BUYS_CSV)
    print(UMA_WALLET_MATCH_CSV)
    print(SUMMARY_TXT)
    print(HASHES_CSV)
    print("")
    print("Done.")


if __name__ == "__main__":
    main()