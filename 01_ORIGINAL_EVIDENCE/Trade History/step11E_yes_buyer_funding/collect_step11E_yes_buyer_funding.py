#!/usr/bin/env python3
"""
Step 11E: YES buyer funding analysis.

Purpose:
    Trace incoming Polygon native/ERC20 transfers into YES buyer wallets, not only redeemer wallets.
    Then compare funding sources against UMA voter/delegate addresses and UMA funding sources.

Important legal limitation:
    A funding edge is transaction evidence only. It does not prove common ownership or control.
    Exchange, bridge, relayer, aggregator, and high-volume contract wallets must be treated as weak leads.

Inputs expected in the same folder:
    01_uma_address_universe.csv
    02_step11E_yes_buyer_wallets.csv
    03_step11E_yes_buy_transactions.csv

Environment:
    POLYGON_RPC_URL must be set to an Alchemy Polygon RPC URL.

Defaults:
    MAX_PRIORITY=2 processes all target buyers and high-notional future-only buyers first.
    START_BLOCK / END_BLOCK may be overridden with environment variables.
"""

import csv
import hashlib
import json
import os
import sys
import time
from collections import defaultdict
from datetime import datetime, timezone
from decimal import Decimal, InvalidOperation
from pathlib import Path

import requests

ZERO = "0x0000000000000000000000000000000000000000"

THIS_DIR = Path(__file__).resolve().parent
OUT_DIR = THIS_DIR / "step11E_outputs"
OUT_DIR.mkdir(exist_ok=True)

UMA_FILE = THIS_DIR / "01_uma_address_universe.csv"
BUYER_FILE = THIS_DIR / "02_step11E_yes_buyer_wallets.csv"
BUY_TX_FILE = THIS_DIR / "03_step11E_yes_buy_transactions.csv"

RPC_URL = "https://polygon-mainnet.g.alchemy.com/v2/mmmIb7Xl00MQ4ZTp6g3A_"
if not RPC_URL:
    print("ERROR: Set POLYGON_RPC_URL first.")
    print('PowerShell example: $env:POLYGON_RPC_URL="YOUR_POLYGON_ALCHEMY_RPC_URL"')
    sys.exit(1)

START_BLOCK = int(os.environ.get("START_BLOCK", "88500000"))
END_BLOCK = int(os.environ.get("END_BLOCK", "88753129"))
MAX_PRIORITY = int(os.environ.get("MAX_PRIORITY", "2"))
MAX_WALLETS = int(os.environ.get("MAX_WALLETS", "0"))  # 0 = no cap after priority filtering
REQUEST_SLEEP_SECONDS = float(os.environ.get("REQUEST_SLEEP_SECONDS", "0.10"))
MAX_RETRIES = int(os.environ.get("MAX_RETRIES", "4"))
HIGH_VOLUME_FUNDER_BUYER_COUNT = int(os.environ.get("HIGH_VOLUME_FUNDER_BUYER_COUNT", "10"))

CATEGORIES = ["external", "erc20"]


def norm_addr(x):
    if x is None:
        return ""
    s = str(x).strip()
    if not s or s.lower() == "nan":
        return ""
    s = s.lower()
    if s.startswith("0x") and len(s) == 42:
        return s
    return ""


def parse_dt(x):
    if not x:
        return None
    s = str(x).strip()
    if not s or s.lower() == "nan":
        return None
    try:
        if s.endswith("Z"):
            s = s[:-1] + "+00:00"
        return datetime.fromisoformat(s)
    except Exception:
        return None


def dt_to_iso(dt):
    if not dt:
        return ""
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc).isoformat()


def to_decimal(x):
    try:
        if x is None or str(x).strip() == "":
            return Decimal("0")
        return Decimal(str(x))
    except (InvalidOperation, ValueError):
        return Decimal("0")


def read_csv_rows(path):
    with open(path, "r", newline="", encoding="utf-8-sig") as f:
        return list(csv.DictReader(f))


def write_csv(path, rows, fieldnames):
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
        w.writeheader()
        for r in rows:
            w.writerow(r)


def sha256_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def rpc_call(method, params):
    payload = {"jsonrpc": "2.0", "id": 1, "method": method, "params": params}
    last_err = None
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            r = requests.post(RPC_URL, json=payload, timeout=60)
            if r.status_code in (429, 500, 502, 503, 504):
                last_err = f"HTTP {r.status_code}: {r.text[:300]}"
                time.sleep(min(2 ** attempt, 20))
                continue
            r.raise_for_status()
            data = r.json()
            if "error" in data:
                last_err = json.dumps(data["error"])[:500]
                time.sleep(min(2 ** attempt, 20))
                continue
            return data.get("result")
        except Exception as e:
            last_err = repr(e)
            time.sleep(min(2 ** attempt, 20))
    raise RuntimeError(last_err or "unknown RPC failure")


def get_asset_transfers(to_address, label):
    rows = []
    page_key = None
    while True:
        params = {
            "fromBlock": hex(START_BLOCK),
            "toBlock": hex(END_BLOCK),
            "toAddress": to_address,
            "category": CATEGORIES,
            "excludeZeroValue": True,
            "withMetadata": True,
            "maxCount": "0x3e8",
            "order": "asc",
        }
        if page_key:
            params["pageKey"] = page_key
        result = rpc_call("alchemy_getAssetTransfers", [params])
        for t in result.get("transfers", []):
            raw_contract = t.get("rawContract") or {}
            metadata = t.get("metadata") or {}
            rows.append({
                "queriedAddress": to_address,
                "queriedLabel": label,
                "category": t.get("category", ""),
                "blockNumHex": t.get("blockNum", ""),
                "blockNumber": int(str(t.get("blockNum", "0x0")), 16) if str(t.get("blockNum", "")).startswith("0x") else "",
                "blockTimestampUTC": metadata.get("blockTimestamp", ""),
                "txHash": t.get("hash", ""),
                "from": norm_addr(t.get("from", "")),
                "to": norm_addr(t.get("to", "")),
                "asset": t.get("asset", ""),
                "value": t.get("value", ""),
                "rawContractAddress": norm_addr(raw_contract.get("address", "")),
                "rawValue": raw_contract.get("value", ""),
                "rawDecimal": raw_contract.get("decimal", ""),
            })
        page_key = result.get("pageKey")
        if not page_key:
            break
        time.sleep(REQUEST_SLEEP_SECONDS)
    return rows


def main():
    collected_at = datetime.now(timezone.utc).isoformat()

    uma_rows_raw = read_csv_rows(UMA_FILE)
    buyer_rows_raw = read_csv_rows(BUYER_FILE)
    buy_tx_rows = read_csv_rows(BUY_TX_FILE)

    uma_addresses = set()
    uma_meta_by_addr = defaultdict(list)
    for r in uma_rows_raw:
        addr = norm_addr(r.get("address"))
        if not addr:
            continue
        uma_addresses.add(addr)
        uma_meta_by_addr[addr].append(r)

    buyers = []
    for r in buyer_rows_raw:
        addr = norm_addr(r.get("proxyWallet"))
        if not addr:
            continue
        try:
            prio = int(float(r.get("step11E_priority", "99")))
        except Exception:
            prio = 99
        if prio <= MAX_PRIORITY:
            rr = dict(r)
            rr["proxyWallet"] = addr
            buyers.append(rr)

    buyers.sort(key=lambda r: (int(float(r.get("step11E_priority", 99))), -float(r.get("totalYESNotionalUSDC", 0) or 0)))
    if MAX_WALLETS > 0:
        buyers = buyers[:MAX_WALLETS]

    buyer_addresses = {r["proxyWallet"] for r in buyers}
    buyer_by_addr = {r["proxyWallet"]: r for r in buyers}

    first_buy_dt_by_addr = {}
    relevant_buy_count_by_addr = defaultdict(int)
    for r in buy_tx_rows:
        addr = norm_addr(r.get("proxyWallet"))
        if addr not in buyer_addresses:
            continue
        relevant_buy_count_by_addr[addr] += 1
        dt = parse_dt(r.get("tradeTimeUTC")) or parse_dt(r.get("activityTimeUTC"))
        if dt and (addr not in first_buy_dt_by_addr or dt < first_buy_dt_by_addr[addr]):
            first_buy_dt_by_addr[addr] = dt

    failures = []
    buyer_transfers = []
    uma_transfers = []

    print("Step 11E YES buyer funding analysis")
    print(f"Priority threshold: <= {MAX_PRIORITY}")
    print(f"Block window: {START_BLOCK} to {END_BLOCK}")
    print(f"YES buyer wallets to query: {len(buyers)}")
    print(f"UMA addresses to query: {len(uma_addresses)}")

    for i, r in enumerate(buyers, 1):
        addr = r["proxyWallet"]
        print(f"Buyer {i}/{len(buyers)}: {addr}")
        try:
            rows = get_asset_transfers(addr, "YES_BUYER")
            for x in rows:
                br = buyer_by_addr.get(addr, {})
                first_dt = first_buy_dt_by_addr.get(addr)
                transfer_dt = parse_dt(x.get("blockTimestampUTC"))
                seconds_before = ""
                within_72h_before = False
                before_first_buy = False
                if first_dt and transfer_dt:
                    seconds = (first_dt - transfer_dt).total_seconds()
                    seconds_before = int(seconds)
                    before_first_buy = seconds >= 0
                    within_72h_before = 0 <= seconds <= 72 * 3600
                x.update({
                    "buyerPattern": br.get("pattern", ""),
                    "buyerPriority": br.get("step11E_priority", ""),
                    "buyerPriorityReason": br.get("step11E_priority_reason", ""),
                    "buyerTotalYESNotionalUSDC": br.get("totalYESNotionalUSDC", ""),
                    "buyerTargetYESNotionalUSDC": br.get("targetMarketYESNotionalUSDC", ""),
                    "buyerFutureYESNotionalUSDC": br.get("futureMarketYESNotionalUSDC", ""),
                    "buyerFirstRelevantYESBuyUTC": dt_to_iso(first_dt),
                    "secondsBeforeFirstRelevantYESBuy": seconds_before,
                    "isBeforeFirstRelevantYESBuy": before_first_buy,
                    "isWithin72hBeforeFirstRelevantYESBuy": within_72h_before,
                    "isFundingSourceUmaAddress": x.get("from") in uma_addresses,
                    "relevantYESBuyTxCount": relevant_buy_count_by_addr.get(addr, 0),
                })
                buyer_transfers.append(x)
        except Exception as e:
            failures.append({"queryType": "buyer_incoming", "address": addr, "error": repr(e)})
        time.sleep(REQUEST_SLEEP_SECONDS)

    for i, addr in enumerate(sorted(uma_addresses), 1):
        print(f"UMA {i}/{len(uma_addresses)}: {addr}")
        try:
            rows = get_asset_transfers(addr, "UMA_ADDRESS")
            for x in rows:
                x["umaAddress"] = addr
                x["umaRoles"] = ";".join(sorted({m.get("addressRole", "") for m in uma_meta_by_addr.get(addr, []) if m.get("addressRole")}))
                x["umaRanks"] = ";".join(sorted({m.get("rank", "") for m in uma_meta_by_addr.get(addr, []) if m.get("rank")}))
                x["umaDecodedVotes"] = ";".join(sorted({m.get("decodedVote", "") for m in uma_meta_by_addr.get(addr, []) if m.get("decodedVote")}))
                x["umaVotingPowerUMA"] = ";".join(sorted({m.get("numTokensUMA", "") for m in uma_meta_by_addr.get(addr, []) if m.get("numTokensUMA")}))
                uma_transfers.append(x)
        except Exception as e:
            failures.append({"queryType": "uma_incoming", "address": addr, "error": repr(e)})
        time.sleep(REQUEST_SLEEP_SECONDS)

    # Build direct UMA -> buyer funding edges.
    direct_uma_funding_edges = [r for r in buyer_transfers if r.get("from") in uma_addresses]

    # Common funder matches: source funds both buyer and UMA address.
    uma_funders = defaultdict(list)
    for r in uma_transfers:
        src = norm_addr(r.get("from"))
        if src and src != ZERO:
            uma_funders[src].append(r)

    buyer_funders = defaultdict(list)
    for r in buyer_transfers:
        src = norm_addr(r.get("from"))
        if src and src != ZERO:
            buyer_funders[src].append(r)

    common_sources = sorted(set(uma_funders).intersection(set(buyer_funders)))

    common_matches = []
    common_pair_edges = []
    priority_leads = []

    for src in common_sources:
        b_edges = buyer_funders[src]
        u_edges = uma_funders[src]
        unique_buyers = sorted({e.get("to") for e in b_edges if e.get("to")})
        unique_uma = sorted({e.get("to") for e in u_edges if e.get("to")})
        assets_b = sorted({e.get("asset", "") for e in b_edges if e.get("asset", "")})
        assets_u = sorted({e.get("asset", "") for e in u_edges if e.get("asset", "")})
        high_volume = len(unique_buyers) >= HIGH_VOLUME_FUNDER_BUYER_COUNT or len(unique_uma) >= 5
        common_matches.append({
            "commonFunder": src,
            "buyerWalletsFundedCount": len(unique_buyers),
            "umaAddressesFundedCount": len(unique_uma),
            "buyerTransferRows": len(b_edges),
            "umaTransferRows": len(u_edges),
            "buyerAssets": ";".join(assets_b),
            "umaAssets": ";".join(assets_u),
            "highVolumeFunderFlag": high_volume,
            "interpretation": "WEAK_IF_EXCHANGE_OR_HIGH_VOLUME" if high_volume else "REVIEW_NON_EXCHANGE_SOURCE",
        })
        for b in b_edges:
            bdt = parse_dt(b.get("blockTimestampUTC"))
            for u in u_edges:
                udt = parse_dt(u.get("blockTimestampUTC"))
                seconds_apart = ""
                if bdt and udt:
                    seconds_apart = abs(int((bdt - udt).total_seconds()))
                edge = {
                    "commonFunder": src,
                    "buyerWallet": b.get("to", ""),
                    "buyerPattern": b.get("buyerPattern", ""),
                    "buyerPriority": b.get("buyerPriority", ""),
                    "buyerTotalYESNotionalUSDC": b.get("buyerTotalYESNotionalUSDC", ""),
                    "buyerFirstRelevantYESBuyUTC": b.get("buyerFirstRelevantYESBuyUTC", ""),
                    "buyerFundingTxHash": b.get("txHash", ""),
                    "buyerFundingTimeUTC": b.get("blockTimestampUTC", ""),
                    "buyerFundingAsset": b.get("asset", ""),
                    "buyerFundingValue": b.get("value", ""),
                    "buyerFundingBeforeFirstBuy": b.get("isBeforeFirstRelevantYESBuy", ""),
                    "buyerFundingWithin72hBeforeFirstBuy": b.get("isWithin72hBeforeFirstRelevantYESBuy", ""),
                    "umaAddress": u.get("to", ""),
                    "umaRoles": u.get("umaRoles", ""),
                    "umaRanks": u.get("umaRanks", ""),
                    "umaDecodedVotes": u.get("umaDecodedVotes", ""),
                    "umaFundingTxHash": u.get("txHash", ""),
                    "umaFundingTimeUTC": u.get("blockTimestampUTC", ""),
                    "umaFundingAsset": u.get("asset", ""),
                    "umaFundingValue": u.get("value", ""),
                    "secondsBetweenBuyerAndUmaFunding": seconds_apart,
                    "highVolumeFunderFlag": high_volume,
                    "legalUseCaution": "Shared funder lead only; confirm source type and timing before drawing conclusions.",
                }
                common_pair_edges.append(edge)
                if not high_volume and str(b.get("isWithin72hBeforeFirstRelevantYESBuy")) == "True":
                    priority_leads.append(edge)

    # Include direct UMA funding as priority leads regardless of common-source logic.
    for d in direct_uma_funding_edges:
        priority_leads.append({
            "commonFunder": d.get("from", ""),
            "buyerWallet": d.get("to", ""),
            "buyerPattern": d.get("buyerPattern", ""),
            "buyerPriority": d.get("buyerPriority", ""),
            "buyerTotalYESNotionalUSDC": d.get("buyerTotalYESNotionalUSDC", ""),
            "buyerFirstRelevantYESBuyUTC": d.get("buyerFirstRelevantYESBuyUTC", ""),
            "buyerFundingTxHash": d.get("txHash", ""),
            "buyerFundingTimeUTC": d.get("blockTimestampUTC", ""),
            "buyerFundingAsset": d.get("asset", ""),
            "buyerFundingValue": d.get("value", ""),
            "buyerFundingBeforeFirstBuy": d.get("isBeforeFirstRelevantYESBuy", ""),
            "buyerFundingWithin72hBeforeFirstBuy": d.get("isWithin72hBeforeFirstRelevantYESBuy", ""),
            "umaAddress": d.get("from", ""),
            "umaRoles": "DIRECT_UMA_ADDRESS_FUNDER",
            "umaRanks": "",
            "umaDecodedVotes": "",
            "umaFundingTxHash": "",
            "umaFundingTimeUTC": "",
            "umaFundingAsset": "",
            "umaFundingValue": "",
            "secondsBetweenBuyerAndUmaFunding": "",
            "highVolumeFunderFlag": False,
            "legalUseCaution": "Direct UMA-address-to-buyer funding edge; review transaction and wallet context before assigning proof level.",
        })

    buyer_fields = [
        "queriedAddress", "queriedLabel", "category", "blockNumber", "blockTimestampUTC", "txHash", "from", "to",
        "asset", "value", "rawContractAddress", "rawValue", "rawDecimal", "buyerPattern", "buyerPriority",
        "buyerPriorityReason", "buyerTotalYESNotionalUSDC", "buyerTargetYESNotionalUSDC", "buyerFutureYESNotionalUSDC",
        "buyerFirstRelevantYESBuyUTC", "secondsBeforeFirstRelevantYESBuy", "isBeforeFirstRelevantYESBuy",
        "isWithin72hBeforeFirstRelevantYESBuy", "isFundingSourceUmaAddress", "relevantYESBuyTxCount"
    ]
    uma_fields = [
        "queriedAddress", "queriedLabel", "category", "blockNumber", "blockTimestampUTC", "txHash", "from", "to",
        "asset", "value", "rawContractAddress", "rawValue", "rawDecimal", "umaAddress", "umaRoles", "umaRanks",
        "umaDecodedVotes", "umaVotingPowerUMA"
    ]
    direct_fields = buyer_fields
    common_match_fields = [
        "commonFunder", "buyerWalletsFundedCount", "umaAddressesFundedCount", "buyerTransferRows", "umaTransferRows",
        "buyerAssets", "umaAssets", "highVolumeFunderFlag", "interpretation"
    ]
    pair_fields = [
        "commonFunder", "buyerWallet", "buyerPattern", "buyerPriority", "buyerTotalYESNotionalUSDC", "buyerFirstRelevantYESBuyUTC",
        "buyerFundingTxHash", "buyerFundingTimeUTC", "buyerFundingAsset", "buyerFundingValue",
        "buyerFundingBeforeFirstBuy", "buyerFundingWithin72hBeforeFirstBuy", "umaAddress", "umaRoles", "umaRanks",
        "umaDecodedVotes", "umaFundingTxHash", "umaFundingTimeUTC", "umaFundingAsset", "umaFundingValue",
        "secondsBetweenBuyerAndUmaFunding", "highVolumeFunderFlag", "legalUseCaution"
    ]

    write_csv(OUT_DIR / "01_incoming_to_yes_buyer_wallets.csv", buyer_transfers, buyer_fields)
    write_csv(OUT_DIR / "02_incoming_to_uma_addresses.csv", uma_transfers, uma_fields)
    write_csv(OUT_DIR / "03_direct_uma_to_yes_buyer_funding_edges.csv", direct_uma_funding_edges, direct_fields)
    write_csv(OUT_DIR / "04_common_funder_matches.csv", common_matches, common_match_fields)
    write_csv(OUT_DIR / "05_common_funder_pair_edges.csv", common_pair_edges, pair_fields)
    write_csv(OUT_DIR / "06_priority_yes_buyer_funding_leads.csv", priority_leads, pair_fields)
    write_csv(OUT_DIR / "98_step11E_failed_queries.csv", failures, ["queryType", "address", "error"])

    hash_rows = []
    for p in [UMA_FILE, BUYER_FILE, BUY_TX_FILE]:
        hash_rows.append({"filename": p.name, "sha256": sha256_file(p)})
    for p in sorted(OUT_DIR.glob("*.csv")):
        hash_rows.append({"filename": "step11E_outputs/" + p.name, "sha256": sha256_file(p)})
    write_csv(OUT_DIR / "99_step11E_file_hashes.csv", hash_rows, ["filename", "sha256"])

    summary = f"""Step 11E YES buyer funding analysis
Collected at UTC: {collected_at}
Block window: {START_BLOCK} to {END_BLOCK}
Transfer categories: {', '.join(CATEGORIES)}
Priority threshold processed: <= {MAX_PRIORITY}
YES buyer wallets queried: {len(buyers)}
UMA addresses queried: {len(uma_addresses)}
Incoming transfer rows to YES buyers: {len(buyer_transfers)}
Incoming transfer rows to UMA addresses: {len(uma_transfers)}
Direct UMA-address-to-YES-buyer funding edges: {len(direct_uma_funding_edges)}
Common funder addresses found: {len(common_sources)}
Common funder pair edges produced: {len(common_pair_edges)}
Priority lead rows produced: {len(priority_leads)}
Failed queries: {len(failures)}

Interpretation:
This step checks funding sources for YES buyer wallets, including wallets that bought YES but did not redeem. It does not assume the buyer wallet and redeemer wallet are the same. A funding edge is transaction evidence only. It does not prove common ownership. Shared exchange, bridge, relayer, aggregator, or high-volume contract sources must be treated as weak unless supported by additional facts.

Recommended review order:
1. 03_direct_uma_to_yes_buyer_funding_edges.csv
2. 06_priority_yes_buyer_funding_leads.csv
3. 04_common_funder_matches.csv
4. 05_common_funder_pair_edges.csv
5. 01_incoming_to_yes_buyer_wallets.csv for manual source review
"""
    (OUT_DIR / "00_step11E_run_summary.txt").write_text(summary, encoding="utf-8")
    print(summary)


if __name__ == "__main__":
    main()
