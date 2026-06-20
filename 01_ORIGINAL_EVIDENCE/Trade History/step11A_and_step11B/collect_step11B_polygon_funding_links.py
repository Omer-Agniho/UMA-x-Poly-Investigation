#!/usr/bin/env python3
"""
Step 11B: Targeted Polygon funding / transfer link screen.

Purpose:
- Checks whether UMA staker/delegate/event wallets have direct Polygon native or ERC20 transfers with the prioritized Polymarket wallet universe.
- Uses Alchemy's indexed alchemy_getAssetTransfers endpoint.
- Does not use eth_getLogs.

Inputs in the same folder:
- 01_uma_address_universe.csv
- 05_step11B_priority_polymarket_wallets.csv

Required environment variable:
- POLYGON_RPC_URL

Outputs:
- step11B_outputs/00_step11B_run_summary.txt
- step11B_outputs/01_uma_polygon_transfers_touching_polymarket_wallets.csv
- step11B_outputs/02_all_uma_polygon_transfers_sampled.csv
- step11B_outputs/98_step11B_failed_queries.csv
"""
import csv, os, sys, json, time, urllib.request, urllib.error
from datetime import datetime, timezone

START_BLOCK = 88517743
END_BLOCK = 88748137
MAX_COUNT = "0x3e8"
SLEEP_SECONDS = 0.18
RETRY_COUNT = 3
CATEGORIES = ["external", "erc20"]

RPC_URL = "https://polygon-mainnet.g.alchemy.com/v2/mmmIb7Xl00MQ4ZTp6g3A_"
if not RPC_URL:
    raise SystemExit("Missing POLYGON_RPC_URL environment variable.")

BASE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(BASE, "step11B_outputs")
os.makedirs(OUT, exist_ok=True)


def read_csv(path):
    with open(path, newline="", encoding="utf-8-sig") as f:
        return list(csv.DictReader(f))


def write_csv(path, fields, rows):
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fields, extrasaction="ignore")
        w.writeheader()
        for r in rows:
            w.writerow(r)


def rpc(method, params):
    payload = json.dumps({"jsonrpc": "2.0", "id": 1, "method": method, "params": params}).encode("utf-8")
    req = urllib.request.Request(RPC_URL, data=payload, headers={"Content-Type": "application/json"}, method="POST")
    last_err = None
    for attempt in range(RETRY_COUNT):
        try:
            with urllib.request.urlopen(req, timeout=60) as resp:
                data = json.loads(resp.read().decode("utf-8"))
            if "error" in data:
                raise RuntimeError(str(data["error"]))
            return data.get("result", {})
        except Exception as e:
            last_err = e
            time.sleep(1.5 * (attempt + 1))
    raise RuntimeError(str(last_err))


def get_asset_transfers(address, direction):
    assert direction in {"from", "to"}
    params = {
        "fromBlock": hex(START_BLOCK),
        "toBlock": hex(END_BLOCK),
        "category": CATEGORIES,
        "withMetadata": True,
        "excludeZeroValue": True,
        "maxCount": MAX_COUNT,
    }
    if direction == "from":
        params["fromAddress"] = address
    else:
        params["toAddress"] = address

    page_key = None
    out = []
    while True:
        if page_key:
            params["pageKey"] = page_key
        elif "pageKey" in params:
            del params["pageKey"]
        result = rpc("alchemy_getAssetTransfers", [params])
        out.extend(result.get("transfers", []))
        page_key = result.get("pageKey")
        if not page_key:
            break
        time.sleep(SLEEP_SECONDS)
    return out

uma_rows = read_csv(os.path.join(BASE, "01_uma_address_universe.csv"))
pm_rows = read_csv(os.path.join(BASE, "05_step11B_priority_polymarket_wallets.csv"))
pm_by_lower = {r["addressLower"].lower(): r for r in pm_rows}
pm_set = set(pm_by_lower)

all_sampled = []
links = []
failures = []

print(f"Step 11B: checking {len(uma_rows)} UMA addresses against {len(pm_rows)} prioritized Polymarket/Step9B wallets")
print(f"Block window: {START_BLOCK} to {END_BLOCK}")

for idx, u in enumerate(uma_rows, start=1):
    uma_addr = u["addressLower"].lower()
    print(f"UMA {idx}/{len(uma_rows)} {uma_addr}")
    for direction in ["from", "to"]:
        try:
            transfers = get_asset_transfers(uma_addr, direction)
        except Exception as e:
            failures.append({"umaAddressLower": uma_addr, "direction": direction, "error": repr(e)})
            print(f"  failed {direction}: {e}")
            continue
        print(f"  {direction}: {len(transfers)} transfers")
        for t in transfers:
            from_l = (t.get("from") or "").lower()
            to_l = (t.get("to") or "").lower()
            counterparty_l = to_l if direction == "from" else from_l
            row = {
                "umaAddressLower": uma_addr,
                "umaDisplayAddress": u.get("displayAddress", ""),
                "umaRoles": u.get("umaRoles", ""),
                "umaRanks": u.get("umaRanks", ""),
                "directionQueried": direction,
                "counterpartyLower": counterparty_l,
                "txHash": t.get("hash", ""),
                "blockNum": t.get("blockNum", ""),
                "blockTimestampUTC": (t.get("metadata") or {}).get("blockTimestamp", ""),
                "from": t.get("from", ""),
                "to": t.get("to", ""),
                "asset": t.get("asset", ""),
                "category": t.get("category", ""),
                "value": t.get("value", ""),
                "rawContractAddress": ((t.get("rawContract") or {}).get("address") or ""),
                "rawValue": ((t.get("rawContract") or {}).get("value") or ""),
            }
            if len(all_sampled) < 50000:
                all_sampled.append(row)
            if counterparty_l in pm_set:
                p = pm_by_lower[counterparty_l]
                link = dict(row)
                link.update({
                    "polymarketAddressLower": p["addressLower"],
                    "polymarketDisplayAddress": p.get("displayAddress", ""),
                    "polymarketPriority": p.get("priority", ""),
                    "polymarketCategories": p.get("categories", ""),
                    "polymarketNotes": p.get("notes", ""),
                    "relationshipType": "DIRECT_POLYGON_NATIVE_OR_ERC20_TRANSFER_WITH_PRIORITY_POLYMARKET_WALLET",
                    "lawyerSafeNote": "Direct Polygon native/ERC20 transfer involving a UMA address and prioritized Polymarket/Step9B wallet. This is a transaction link, not proof of common ownership by itself."
                })
                links.append(link)
        time.sleep(SLEEP_SECONDS)

fields = ["umaAddressLower","umaDisplayAddress","umaRoles","umaRanks","directionQueried","counterpartyLower","txHash","blockNum","blockTimestampUTC","from","to","asset","category","value","rawContractAddress","rawValue"]
link_fields = fields + ["polymarketAddressLower","polymarketDisplayAddress","polymarketPriority","polymarketCategories","polymarketNotes","relationshipType","lawyerSafeNote"]
write_csv(os.path.join(OUT, "01_uma_polygon_transfers_touching_polymarket_wallets.csv"), link_fields, links)
write_csv(os.path.join(OUT, "02_all_uma_polygon_transfers_sampled.csv"), fields, all_sampled)
write_csv(os.path.join(OUT, "98_step11B_failed_queries.csv"), ["umaAddressLower","direction","error"], failures)

summary = f"""Step 11B Polygon funding / transfer link screen
Collected at UTC: {datetime.now(timezone.utc).isoformat()}
UMA addresses checked: {len(uma_rows)}
Prioritized Polymarket/Step9B wallets checked against: {len(pm_rows)}
Block window: {START_BLOCK} to {END_BLOCK}
Transfer categories: {', '.join(CATEGORIES)}
Direct UMA-to-priority-Polymarket transfer links found: {len(links)}
Failed queries: {len(failures)}

Interpretation:
This script checks direct Polygon native/ERC20 transfer links between UMA addresses and prioritized Polymarket/Step9B wallets.
A link is transaction evidence only. It does not prove common ownership by itself.
If links are found, review transaction receipts and timing before assigning proof level B.
"""
with open(os.path.join(OUT, "00_step11B_run_summary.txt"), "w", encoding="utf-8") as f:
    f.write(summary)
print(summary)
