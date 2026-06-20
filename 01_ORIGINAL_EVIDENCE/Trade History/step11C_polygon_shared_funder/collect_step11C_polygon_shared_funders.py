#!/usr/bin/env python3
"""
Step 11C: Shared funder screen on Polygon.

Purpose:
  Check whether the same funding/source wallet sent Polygon native/ERC20 transfers
  to both:
    1. UMA voter / staker / delegate addresses, and
    2. high-priority Polymarket / Step9B wallets.

Important:
  This is an investigative screen. A common funder is not proof of common control.
  Exchange, bridge, relayer, aggregator, and contract wallets must be reviewed manually.

Inputs expected in the same folder:
  01_uma_address_universe.csv
  05_step11B_priority_polymarket_wallets.csv

Environment:
  POLYGON_RPC_URL must be set to an Alchemy Polygon RPC endpoint.

Outputs:
  step11C_outputs/
    00_step11C_run_summary.txt
    01_uma_incoming_polygon_transfers.csv
    02_polymarket_incoming_polygon_transfers.csv
    03_common_funder_matches.csv
    04_common_funder_pair_edges.csv
    05_common_funder_summary_by_funder.csv
    06_priority_common_funder_leads.csv
    98_step11C_failed_queries.csv
"""

import csv
import json
import os
import time
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd
import requests


START_BLOCK_HEX = "0x546bdef"   # 88517743
END_BLOCK_HEX   = "0x54a43e9"   # 88748137

# Keep this conservative. Priority 1 and 2 are the core Step 10 / Step 9B wallets.
MAX_POLYMARKET_PRIORITY = int(os.environ.get("STEP11C_MAX_POLYMARKET_PRIORITY", "2"))

# Query categories. external = native MATIC/POL transfers; erc20 = token transfers.
TRANSFER_CATEGORIES = ["external", "erc20"]

# Alchemy pagination limit. Keep under 1000.
MAX_COUNT_HEX = "0x3e8"

# Avoid infinite pagination if something is unexpectedly huge.
MAX_PAGES_PER_WALLET_DIRECTION = int(os.environ.get("STEP11C_MAX_PAGES", "25"))

# Basic noise labels. These are not exclusions by default, only flags in the output.
KNOWN_NOISY_LABEL_KEYWORDS = [
    "exchange",
    "bridge",
    "router",
    "relayer",
    "aggregator",
    "contract",
]


def norm_addr(x):
    if pd.isna(x):
        return ""
    s = str(x).strip()
    return s.lower() if s.startswith("0x") and len(s) == 42 else s.lower()


def parse_block_hex_to_int(x):
    if pd.isna(x) or str(x).strip() == "":
        return None
    s = str(x).strip()
    try:
        return int(s, 16) if s.startswith("0x") else int(s)
    except Exception:
        return None


def alchemy_asset_transfers(rpc_url, params, retry=4, sleep_base=1.5):
    payload = {"jsonrpc": "2.0", "id": 1, "method": "alchemy_getAssetTransfers", "params": [params]}
    last_err = None
    for attempt in range(retry):
        try:
            r = requests.post(rpc_url, json=payload, timeout=60)
            if r.status_code == 429:
                time.sleep(sleep_base * (attempt + 1))
                continue
            r.raise_for_status()
            data = r.json()
            if "error" in data:
                last_err = data["error"]
                time.sleep(sleep_base * (attempt + 1))
                continue
            return data.get("result", {})
        except Exception as e:
            last_err = repr(e)
            time.sleep(sleep_base * (attempt + 1))
    raise RuntimeError(str(last_err))


def fetch_incoming_transfers(rpc_url, target_address, side, display_address, meta):
    rows = []
    failures = []
    page_key = None
    page = 0

    while True:
        page += 1
        params = {
            "fromBlock": START_BLOCK_HEX,
            "toBlock": END_BLOCK_HEX,
            "toAddress": target_address,
            "category": TRANSFER_CATEGORIES,
            "withMetadata": True,
            "excludeZeroValue": True,
            "maxCount": MAX_COUNT_HEX,
            "order": "desc",
        }
        if page_key:
            params["pageKey"] = page_key

        try:
            result = alchemy_asset_transfers(rpc_url, params)
            transfers = result.get("transfers", []) or []
            for t in transfers:
                raw_contract = ""
                raw_value = ""
                erc1155_meta = ""

                raw_contract_obj = t.get("rawContract") or {}
                if isinstance(raw_contract_obj, dict):
                    raw_contract = norm_addr(raw_contract_obj.get("address", ""))
                    raw_value = raw_contract_obj.get("value", "")

                row = {
                    "side": side,
                    "targetAddressLower": target_address,
                    "targetDisplayAddress": display_address,
                    "targetMeta": meta,
                    "sourceAddressLower": norm_addr(t.get("from", "")),
                    "toAddressLower": norm_addr(t.get("to", "")),
                    "txHash": t.get("hash", ""),
                    "blockNum": t.get("blockNum", ""),
                    "blockInt": parse_block_hex_to_int(t.get("blockNum", "")),
                    "blockTimestampUTC": ((t.get("metadata") or {}).get("blockTimestamp", "")),
                    "asset": t.get("asset", ""),
                    "category": t.get("category", ""),
                    "value": t.get("value", ""),
                    "rawContractAddress": raw_contract,
                    "rawValue": raw_value,
                    "uniqueId": t.get("uniqueId", ""),
                }
                rows.append(row)

            page_key = result.get("pageKey")
            if not page_key:
                break
            if page >= MAX_PAGES_PER_WALLET_DIRECTION:
                failures.append({
                    "targetAddressLower": target_address,
                    "side": side,
                    "direction": "incoming",
                    "error": f"pagination stopped at max page limit {MAX_PAGES_PER_WALLET_DIRECTION}",
                })
                break

            time.sleep(0.15)
        except Exception as e:
            failures.append({
                "targetAddressLower": target_address,
                "side": side,
                "direction": "incoming",
                "error": repr(e),
            })
            break

    return rows, failures


def value_float(x):
    try:
        if x is None or str(x).strip() == "":
            return None
        return float(x)
    except Exception:
        return None


def time_to_ts(x):
    try:
        return pd.to_datetime(x, utc=True)
    except Exception:
        return pd.NaT


def main():
    rpc_url = "https://polygon-mainnet.g.alchemy.com/v2/mmmIb7Xl00MQ4ZTp6g3A_"
    if not rpc_url:
        raise SystemExit("Set POLYGON_RPC_URL first.")

    here = Path(".")
    out = here / "step11C_outputs"
    out.mkdir(exist_ok=True)

    uma_path = here / "01_uma_address_universe.csv"
    pm_path = here / "05_step11B_priority_polymarket_wallets.csv"
    if not uma_path.exists():
        raise SystemExit("Missing 01_uma_address_universe.csv")
    if not pm_path.exists():
        raise SystemExit("Missing 05_step11B_priority_polymarket_wallets.csv")

    uma = pd.read_csv(uma_path)
    pm = pd.read_csv(pm_path)

    uma["addressLower"] = uma["addressLower"].map(norm_addr)
    uma = uma[uma["addressLower"].str.startswith("0x")].drop_duplicates("addressLower").copy()

    pm["addressLower"] = pm["addressLower"].map(norm_addr)
    pm["priority"] = pd.to_numeric(pm.get("priority", 99), errors="coerce").fillna(99).astype(int)
    pm_selected = pm[
        (pm["addressLower"].str.startswith("0x")) &
        (pm["priority"] <= MAX_POLYMARKET_PRIORITY)
    ].drop_duplicates("addressLower").copy()

    print("Step 11C shared funder screen")
    print(f"UMA addresses: {len(uma)}")
    print(f"Polymarket priority <= {MAX_POLYMARKET_PRIORITY} wallets: {len(pm_selected)}")
    print("Using alchemy_getAssetTransfers incoming-only queries.")

    all_failures = []
    uma_rows = []
    pm_rows = []

    for idx, r in uma.iterrows():
        addr = r["addressLower"]
        display = r.get("displayAddress", addr)
        meta = f"roles={r.get('umaRoles','')}; ranks={r.get('umaRanks','')}; votes={r.get('decodedVotes','')}; votingPower={r.get('maxWorkbookVotingPowerUMA','')}"
        print(f"UMA {len(uma_rows)} rows collected | query {idx+1}/{len(uma)} {addr}")
        rows, fails = fetch_incoming_transfers(rpc_url, addr, "UMA", display, meta)
        uma_rows.extend(rows)
        all_failures.extend(fails)
        time.sleep(0.2)

    for j, r in pm_selected.reset_index(drop=True).iterrows():
        addr = r["addressLower"]
        display = r.get("displayAddress", addr)
        meta = f"priority={r.get('priority','')}; categories={r.get('categories','')}; notes={r.get('notes','')}"
        print(f"POLYMARKET {len(pm_rows)} rows collected | query {j+1}/{len(pm_selected)} {addr}")
        rows, fails = fetch_incoming_transfers(rpc_url, addr, "POLYMARKET", display, meta)
        pm_rows.extend(rows)
        all_failures.extend(fails)
        time.sleep(0.2)

    uma_df = pd.DataFrame(uma_rows)
    pm_df = pd.DataFrame(pm_rows)
    fail_df = pd.DataFrame(all_failures)

    if uma_df.empty:
        uma_df = pd.DataFrame(columns=[
            "side","targetAddressLower","targetDisplayAddress","targetMeta","sourceAddressLower",
            "toAddressLower","txHash","blockNum","blockInt","blockTimestampUTC","asset",
            "category","value","rawContractAddress","rawValue","uniqueId"
        ])
    if pm_df.empty:
        pm_df = pd.DataFrame(columns=uma_df.columns)
    if fail_df.empty:
        fail_df = pd.DataFrame(columns=["targetAddressLower","side","direction","error"])

    uma_df.to_csv(out / "01_uma_incoming_polygon_transfers.csv", index=False)
    pm_df.to_csv(out / "02_polymarket_incoming_polygon_transfers.csv", index=False)
    fail_df.to_csv(out / "98_step11C_failed_queries.csv", index=False)

    # Common funder screen.
    uma_sources = set(uma_df["sourceAddressLower"].dropna().map(norm_addr))
    pm_sources = set(pm_df["sourceAddressLower"].dropna().map(norm_addr))
    common_sources = sorted(x for x in (uma_sources & pm_sources) if x and x != "0x0000000000000000000000000000000000000000")

    common_rows = []
    pair_rows = []
    summary_rows = []

    for src in common_sources:
        u = uma_df[uma_df["sourceAddressLower"].map(norm_addr) == src].copy()
        p = pm_df[pm_df["sourceAddressLower"].map(norm_addr) == src].copy()

        u_targets = sorted(set(u["targetAddressLower"].dropna()))
        p_targets = sorted(set(p["targetAddressLower"].dropna()))
        u_assets = sorted(set(str(x) for x in u["asset"].dropna()))
        p_assets = sorted(set(str(x) for x in p["asset"].dropna()))
        u_contracts = sorted(set(str(x) for x in u["rawContractAddress"].dropna() if str(x)))
        p_contracts = sorted(set(str(x) for x in p["rawContractAddress"].dropna() if str(x)))

        summary_rows.append({
            "commonFunderLower": src,
            "umaTargetsCount": len(u_targets),
            "polymarketTargetsCount": len(p_targets),
            "umaTransferRows": len(u),
            "polymarketTransferRows": len(p),
            "umaTargetsSample": "; ".join(u_targets[:10]),
            "polymarketTargetsSample": "; ".join(p_targets[:10]),
            "assetOverlap": "; ".join(sorted(set(u_assets) & set(p_assets))),
            "contractOverlap": "; ".join(sorted(set(u_contracts) & set(p_contracts))),
            "firstUmaUTC": str(pd.to_datetime(u["blockTimestampUTC"], utc=True, errors="coerce").min()),
            "lastUmaUTC": str(pd.to_datetime(u["blockTimestampUTC"], utc=True, errors="coerce").max()),
            "firstPolymarketUTC": str(pd.to_datetime(p["blockTimestampUTC"], utc=True, errors="coerce").min()),
            "lastPolymarketUTC": str(pd.to_datetime(p["blockTimestampUTC"], utc=True, errors="coerce").max()),
            "lawyerSafeNote": "Common incoming source on Polygon. Investigative lead only; does not prove common ownership."
        })

        # Pair edges. Limit by choosing most relevant rows:
        # rows with overlapping contract or asset first, then larger values.
        def prep(df):
            df = df.copy()
            df["valueFloat"] = df["value"].map(value_float)
            df["ts"] = pd.to_datetime(df["blockTimestampUTC"], utc=True, errors="coerce")
            return df.sort_values(["valueFloat"], ascending=False, na_position="last").head(25)

        u2 = prep(u)
        p2 = prep(p)

        for _, ur in u2.iterrows():
            for _, pr in p2.iterrows():
                same_contract = bool(str(ur.get("rawContractAddress","")) and str(ur.get("rawContractAddress","")) == str(pr.get("rawContractAddress","")))
                same_asset = bool(str(ur.get("asset","")) and str(ur.get("asset","")) == str(pr.get("asset","")))
                uv = value_float(ur.get("value"))
                pv = value_float(pr.get("value"))
                amount_ratio = ""
                amount_close_20pct = False
                if uv is not None and pv is not None and max(abs(uv), abs(pv)) > 0:
                    amount_ratio_val = min(abs(uv), abs(pv)) / max(abs(uv), abs(pv))
                    amount_ratio = amount_ratio_val
                    amount_close_20pct = amount_ratio_val >= 0.8
                uts = time_to_ts(ur.get("blockTimestampUTC"))
                pts = time_to_ts(pr.get("blockTimestampUTC"))
                hours_apart = ""
                within_72h = False
                if not pd.isna(uts) and not pd.isna(pts):
                    hours_apart_val = abs((uts - pts).total_seconds()) / 3600
                    hours_apart = hours_apart_val
                    within_72h = hours_apart_val <= 72

                score = 0
                if same_contract: score += 3
                if same_asset: score += 1
                if amount_close_20pct: score += 2
                if within_72h: score += 2

                pair_rows.append({
                    "commonFunderLower": src,
                    "umaTargetLower": ur.get("targetAddressLower",""),
                    "umaTargetMeta": ur.get("targetMeta",""),
                    "umaTxHash": ur.get("txHash",""),
                    "umaUTC": ur.get("blockTimestampUTC",""),
                    "umaAsset": ur.get("asset",""),
                    "umaCategory": ur.get("category",""),
                    "umaValue": ur.get("value",""),
                    "umaRawContract": ur.get("rawContractAddress",""),
                    "polymarketTargetLower": pr.get("targetAddressLower",""),
                    "polymarketTargetMeta": pr.get("targetMeta",""),
                    "polymarketTxHash": pr.get("txHash",""),
                    "polymarketUTC": pr.get("blockTimestampUTC",""),
                    "polymarketAsset": pr.get("asset",""),
                    "polymarketCategory": pr.get("category",""),
                    "polymarketValue": pr.get("value",""),
                    "polymarketRawContract": pr.get("rawContractAddress",""),
                    "sameContract": same_contract,
                    "sameAsset": same_asset,
                    "amountSimilarityRatio": amount_ratio,
                    "amountCloseWithin20pct": amount_close_20pct,
                    "hoursApart": hours_apart,
                    "within72Hours": within_72h,
                    "leadScore": score,
                    "lawyerSafeNote": "Common funder pair edge. Review whether source is exchange/bridge/contract and whether timing/amount supports any inference."
                })

    summary_df = pd.DataFrame(summary_rows)
    pair_df = pd.DataFrame(pair_rows)

    if summary_df.empty:
        summary_df = pd.DataFrame(columns=[
            "commonFunderLower","umaTargetsCount","polymarketTargetsCount","umaTransferRows",
            "polymarketTransferRows","umaTargetsSample","polymarketTargetsSample","assetOverlap",
            "contractOverlap","firstUmaUTC","lastUmaUTC","firstPolymarketUTC","lastPolymarketUTC",
            "lawyerSafeNote"
        ])
    if pair_df.empty:
        pair_df = pd.DataFrame(columns=[
            "commonFunderLower","umaTargetLower","umaTargetMeta","umaTxHash","umaUTC","umaAsset",
            "umaCategory","umaValue","umaRawContract","polymarketTargetLower","polymarketTargetMeta",
            "polymarketTxHash","polymarketUTC","polymarketAsset","polymarketCategory","polymarketValue",
            "polymarketRawContract","sameContract","sameAsset","amountSimilarityRatio",
            "amountCloseWithin20pct","hoursApart","within72Hours","leadScore","lawyerSafeNote"
        ])

    summary_df.to_csv(out / "05_common_funder_summary_by_funder.csv", index=False)
    pair_df.to_csv(out / "04_common_funder_pair_edges.csv", index=False)

    common_match_rows = []
    for src in common_sources:
        common_match_rows.append({"commonFunderLower": src})
    common_df = pd.DataFrame(common_match_rows)
    if common_df.empty:
        common_df = pd.DataFrame(columns=["commonFunderLower"])
    common_df.to_csv(out / "03_common_funder_matches.csv", index=False)

    priority_df = pair_df.sort_values(["leadScore"], ascending=False).head(250).copy() if not pair_df.empty else pair_df.copy()
    priority_df.to_csv(out / "06_priority_common_funder_leads.csv", index=False)

    collected = datetime.now(timezone.utc).isoformat()
    with open(out / "00_step11C_run_summary.txt", "w", encoding="utf-8") as f:
        f.write("Step 11C Polygon shared funder screen\n")
        f.write(f"Collected at UTC: {collected}\n")
        f.write(f"UMA addresses checked: {len(uma)}\n")
        f.write(f"Polymarket priority threshold: <= {MAX_POLYMARKET_PRIORITY}\n")
        f.write(f"Polymarket wallets checked: {len(pm_selected)}\n")
        f.write(f"Block window: {int(START_BLOCK_HEX, 16)} to {int(END_BLOCK_HEX, 16)}\n")
        f.write(f"Transfer categories: {', '.join(TRANSFER_CATEGORIES)}\n")
        f.write(f"UMA incoming transfer rows: {len(uma_df)}\n")
        f.write(f"Polymarket incoming transfer rows: {len(pm_df)}\n")
        f.write(f"Common funder addresses found: {len(common_sources)}\n")
        f.write(f"Common funder pair edges produced: {len(pair_df)}\n")
        f.write(f"Priority lead rows produced: {len(priority_df)}\n")
        f.write(f"Failed queries: {len(fail_df)}\n\n")
        f.write("Interpretation:\n")
        f.write("This script checks whether the same Polygon source wallet funded both a UMA address and a high-priority Polymarket/Step9B wallet.\n")
        f.write("A common funder is an investigative lead only. It does not prove common ownership.\n")
        f.write("Exchange, bridge, relayer, aggregator, contract, and high-volume wallets must be treated as weak unless other facts support the link.\n")
        f.write("For legal analysis, prioritize common funder pair edges with matching contracts/assets, close timing, similar values, and non-exchange source wallets.\n")

    print("Done. Outputs written to step11C_outputs")


if __name__ == "__main__":
    main()
