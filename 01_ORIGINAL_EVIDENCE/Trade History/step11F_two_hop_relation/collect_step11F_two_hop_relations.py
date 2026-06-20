#!/usr/bin/env python3
"""
Step 11F: focused two-hop Polygon relation screen.

Purpose:
    Test whether priority UMA YES voter/delegate addresses and priority Polymarket YES buyer/redeemer/token-path wallets
    touch the same intermediary/counterparty wallet on Polygon during the relevant window.

This is an investigative screen. A common counterparty is not proof of common ownership.
Exchange, bridge, router, relayer, aggregator, and high-volume addresses must be treated as weak unless other facts support the link.
"""
import os, time, json, csv, re, hashlib
from pathlib import Path
from datetime import datetime, timezone
from collections import defaultdict
import requests
import pandas as pd

RPC_URL = os.getenv('POLYGON_RPC_URL')
if not RPC_URL:
    raise SystemExit('Missing POLYGON_RPC_URL. In PowerShell: $env:POLYGON_RPC_URL="YOUR_POLYGON_ALCHEMY_RPC_URL"')

START_BLOCK = int(os.getenv('START_BLOCK', '88500000'))
END_BLOCK = int(os.getenv('END_BLOCK', '88753129'))
MAX_UMA = int(os.getenv('MAX_UMA', '125'))
MAX_POLY = int(os.getenv('MAX_POLY', '125'))
PRIORITY_THRESHOLD = int(os.getenv('PRIORITY_THRESHOLD', '2'))
SLEEP_SECONDS = float(os.getenv('SLEEP_SECONDS', '0.15'))
MAX_PAGES_PER_QUERY = int(os.getenv('MAX_PAGES_PER_QUERY', '25'))
MAX_PAIR_ROWS = int(os.getenv('MAX_PAIR_ROWS', '100000'))
CLOSE_TIMING_SECONDS = int(os.getenv('CLOSE_TIMING_SECONDS', str(72*3600)))

OUT = Path('step11F_outputs')
OUT.mkdir(exist_ok=True)

ADDR_RE = re.compile(r'^0x[a-fA-F0-9]{40}$')
ZERO = '0x0000000000000000000000000000000000000000'
CATEGORIES = ['external','erc20']

# Known public / system addresses that should not be treated as strong intermediaries.
KNOWN_WEAK_COUNTERPARTIES = {
    ZERO,
    '0x4d97dcd97ec945f40cf65f87097ace5ea0476045',  # Polymarket CTF ERC1155, included as caution if ever seen
    '0x0000000000000000000000000000000000001010',  # Polygon native token pseudo address in some tooling
}

def norm(a):
    if pd.isna(a): return ''
    s=str(a).strip()
    return s.lower() if ADDR_RE.match(s) else ''

def hexblock(n):
    return hex(int(n))

def rpc(method, params):
    payload={'jsonrpc':'2.0','id':1,'method':method,'params':params}
    for attempt in range(6):
        try:
            r=requests.post(RPC_URL, json=payload, timeout=60)
            if r.status_code in (429, 500, 502, 503, 504):
                time.sleep((2 ** attempt) * 0.75)
                continue
            r.raise_for_status()
            data=r.json()
            if 'error' in data:
                msg=str(data['error'])
                if attempt < 5 and any(x in msg.lower() for x in ['rate', 'timeout', 'busy', 'temporar']):
                    time.sleep((2 ** attempt) * 0.75)
                    continue
                raise RuntimeError(msg)
            return data['result']
        except Exception:
            if attempt == 5:
                raise
            time.sleep((2 ** attempt) * 0.75)

def get_transfers(address, direction, label, role):
    # direction: incoming uses toAddress; outgoing uses fromAddress
    rows=[]
    page_key=None
    pages=0
    while True:
        params={
            'fromBlock': hexblock(START_BLOCK),
            'toBlock': hexblock(END_BLOCK),
            'category': CATEGORIES,
            'withMetadata': True,
            'excludeZeroValue': True,
            'maxCount': hex(1000),
            'order': 'asc',
        }
        if direction == 'incoming':
            params['toAddress']=address
        else:
            params['fromAddress']=address
        if page_key:
            params['pageKey']=page_key
        result=rpc('alchemy_getAssetTransfers', [params])
        transfers=result.get('transfers', []) if isinstance(result, dict) else []
        for t in transfers:
            frm=norm(t.get('from',''))
            to=norm(t.get('to',''))
            counterparty = frm if direction == 'incoming' else to
            if not counterparty or counterparty == address.lower():
                continue
            raw_contract=''
            raw_value=''
            raw_decimal=''
            raw=t.get('rawContract') or {}
            if isinstance(raw, dict):
                raw_contract=norm(raw.get('address',''))
                raw_value=raw.get('value','')
                raw_decimal=raw.get('decimal','')
            meta=t.get('metadata') or {}
            rows.append({
                'queriedAddress': address,
                'queriedLabel': label,
                'queriedRole': role,
                'direction': direction,
                'counterparty': counterparty,
                'category': t.get('category',''),
                'blockNumber': int(str(t.get('blockNum','0x0')),16) if isinstance(t.get('blockNum'), str) and t.get('blockNum','').startswith('0x') else t.get('blockNum',''),
                'blockTimestampUTC': meta.get('blockTimestamp',''),
                'txHash': t.get('hash',''),
                'from': frm,
                'to': to,
                'asset': t.get('asset',''),
                'value': t.get('value',''),
                'rawContractAddress': raw_contract,
                'rawValue': raw_value,
                'rawDecimal': raw_decimal,
                'uniqueId': t.get('uniqueId',''),
            })
        page_key = result.get('pageKey') if isinstance(result, dict) else None
        pages += 1
        if not page_key or pages >= MAX_PAGES_PER_QUERY:
            break
        time.sleep(SLEEP_SECONDS)
    return rows

def parse_time(s):
    if not isinstance(s,str) or not s:
        return None
    try:
        return datetime.fromisoformat(s.replace('Z','+00:00'))
    except Exception:
        return None

def parse_float(x):
    try:
        if x is None or x == '': return None
        return float(x)
    except Exception:
        return None

def closest_seconds(times_a, times_b):
    a=[t for t in times_a if t is not None]
    b=[t for t in times_b if t is not None]
    if not a or not b:
        return None
    a=sorted(a); b=sorted(b)
    i=j=0; best=None
    while i < len(a) and j < len(b):
        diff=abs((a[i]-b[j]).total_seconds())
        best=diff if best is None or diff < best else best
        if a[i] < b[j]: i+=1
        else: j+=1
    return int(best) if best is not None else None

def val_sum(vals):
    total=0.0; count=0
    for v in vals:
        f=parse_float(v)
        if f is not None:
            total += f; count += 1
    return total if count else ''

def uniq_join(vals, limit=15):
    out=[]
    for v in vals:
        if pd.isna(v): continue
        s=str(v)
        if s and s not in out:
            out.append(s)
    return '; '.join(out[:limit])

def main():
    uma=pd.read_csv('01_step11F_uma_priority_addresses.csv')
    poly=pd.read_csv('02_step11F_polymarket_priority_wallets.csv')
    uma['addressLower']=uma['address'].map(norm)
    poly['walletLower']=poly['wallet'].map(norm)
    uma=uma[(uma['addressLower']!='') & (pd.to_numeric(uma['step11F_priority'], errors='coerce') <= PRIORITY_THRESHOLD)].copy()
    poly=poly[(poly['walletLower']!='') & (pd.to_numeric(poly['step11F_priority'], errors='coerce') <= PRIORITY_THRESHOLD)].copy()
    uma=uma.drop_duplicates('addressLower').head(MAX_UMA)
    poly=poly.drop_duplicates('walletLower').head(MAX_POLY)

    failures=[]
    uma_edges=[]
    poly_edges=[]

    print('Step 11F focused two-hop relation screen')
    print(f'UMA addresses to query: {len(uma)}')
    print(f'Polymarket wallets to query: {len(poly)}')
    print(f'Block window: {START_BLOCK} to {END_BLOCK}')

    for idx,r in enumerate(uma.itertuples(index=False), start=1):
        address=getattr(r,'addressLower')
        label=f"roles={getattr(r,'addressRoles','')}; ranks={getattr(r,'ranks','')}; vote={getattr(r,'decodedVotes','')}"
        print(f'UMA {idx}/{len(uma)} {address}')
        for direction in ['incoming','outgoing']:
            try:
                rows=get_transfers(address, direction, label, 'UMA_YES_ADDRESS')
                uma_edges.extend(rows)
            except Exception as e:
                failures.append({'querySide':'UMA','address':address,'direction':direction,'error':repr(e)})
            time.sleep(SLEEP_SECONDS)

    for idx,r in enumerate(poly.itertuples(index=False), start=1):
        address=getattr(r,'walletLower')
        label=f"groups={getattr(r,'sourceGroups','')}; patterns={getattr(r,'patterns','')}; priority={getattr(r,'step11F_priority','')}"
        print(f'POLY {idx}/{len(poly)} {address}')
        for direction in ['incoming','outgoing']:
            try:
                rows=get_transfers(address, direction, label, 'POLYMARKET_PRIORITY_WALLET')
                poly_edges.extend(rows)
            except Exception as e:
                failures.append({'querySide':'POLYMARKET','address':address,'direction':direction,'error':repr(e)})
            time.sleep(SLEEP_SECONDS)

    uma_df=pd.DataFrame(uma_edges)
    poly_df=pd.DataFrame(poly_edges)
    if uma_df.empty:
        uma_df=pd.DataFrame(columns=['queriedAddress','queriedLabel','queriedRole','direction','counterparty','category','blockNumber','blockTimestampUTC','txHash','from','to','asset','value','rawContractAddress','rawValue','rawDecimal','uniqueId'])
    if poly_df.empty:
        poly_df=pd.DataFrame(columns=['queriedAddress','queriedLabel','queriedRole','direction','counterparty','category','blockNumber','blockTimestampUTC','txHash','from','to','asset','value','rawContractAddress','rawValue','rawDecimal','uniqueId'])

    uma_df.to_csv(OUT/'01_uma_polygon_counterparty_edges.csv', index=False)
    poly_df.to_csv(OUT/'02_polymarket_polygon_counterparty_edges.csv', index=False)

    common=set(uma_df['counterparty'].dropna().astype(str).str.lower()) & set(poly_df['counterparty'].dropna().astype(str).str.lower())
    common={c for c in common if c and c not in KNOWN_WEAK_COUNTERPARTIES}

    cp_summary=[]
    pair_rows=[]
    for cp in sorted(common):
        u=uma_df[uma_df['counterparty'].str.lower()==cp].copy()
        p=poly_df[poly_df['counterparty'].str.lower()==cp].copy()
        uma_addrs=sorted(set(u['queriedAddress'].astype(str).str.lower()))
        poly_addrs=sorted(set(p['queriedAddress'].astype(str).str.lower()))
        high_volume = (len(uma_addrs) > 5 or len(poly_addrs) > 10 or len(u)+len(p) > 250)
        cp_summary.append({
            'commonCounterparty': cp,
            'umaAddressesTouchedCount': len(uma_addrs),
            'polymarketWalletsTouchedCount': len(poly_addrs),
            'umaTransferRows': len(u),
            'polymarketTransferRows': len(p),
            'umaDirections': uniq_join(u['direction']),
            'polymarketDirections': uniq_join(p['direction']),
            'umaAssets': uniq_join(u['asset']),
            'polymarketAssets': uniq_join(p['asset']),
            'highVolumeCounterpartyFlag': 'YES' if high_volume else 'NO',
            'legalUseCaution': 'Treat as weak if this is an exchange, bridge, router, relayer, aggregator, public contract, or high-volume wallet.'
        })
        # Skip exhaustive pair expansion on very broad counterparties, but still keep summary.
        if high_volume and len(uma_addrs)*len(poly_addrs) > 5000:
            continue
        for ua in uma_addrs:
            uu=u[u['queriedAddress'].astype(str).str.lower()==ua]
            for pw in poly_addrs:
                pp=p[p['queriedAddress'].astype(str).str.lower()==pw]
                utimes=[parse_time(x) for x in uu['blockTimestampUTC']]
                ptimes=[parse_time(x) for x in pp['blockTimestampUTC']]
                close=closest_seconds(utimes, ptimes)
                same_asset=bool(set(uu['asset'].dropna().astype(str)) & set(pp['asset'].dropna().astype(str)))
                score=0
                if not high_volume: score+=2
                if close is not None and close <= CLOSE_TIMING_SECONDS: score+=2
                if same_asset: score+=1
                if len(uu) > 1 and len(pp) > 1: score+=1
                pair_rows.append({
                    'commonCounterparty': cp,
                    'umaAddress': ua,
                    'umaAddressLabels': uniq_join(uu['queriedLabel']),
                    'polymarketWallet': pw,
                    'polymarketWalletLabels': uniq_join(pp['queriedLabel']),
                    'umaTransferRows': len(uu),
                    'polymarketTransferRows': len(pp),
                    'umaDirections': uniq_join(uu['direction']),
                    'polymarketDirections': uniq_join(pp['direction']),
                    'umaAssets': uniq_join(uu['asset']),
                    'polymarketAssets': uniq_join(pp['asset']),
                    'sameAssetFlag': 'YES' if same_asset else 'NO',
                    'closestTimingSeconds': close if close is not None else '',
                    'closestTimingWithin72hFlag': 'YES' if close is not None and close <= CLOSE_TIMING_SECONDS else 'NO',
                    'umaValueSumHelper': val_sum(uu['value']),
                    'polymarketValueSumHelper': val_sum(pp['value']),
                    'sampleUmaTxs': uniq_join(uu['txHash'], limit=5),
                    'samplePolymarketTxs': uniq_join(pp['txHash'], limit=5),
                    'highVolumeCounterpartyFlag': 'YES' if high_volume else 'NO',
                    'leadScore': score,
                    'legalUseCaution': 'Two-hop transaction lead only. Do not state common ownership without additional proof. Exchange/bridge/router/public-contract overlap is weak.'
                })
                if len(pair_rows) >= MAX_PAIR_ROWS:
                    break
            if len(pair_rows) >= MAX_PAIR_ROWS:
                break
        if len(pair_rows) >= MAX_PAIR_ROWS:
            break

    cp_df=pd.DataFrame(cp_summary)
    pair_df=pd.DataFrame(pair_rows)
    if cp_df.empty:
        cp_df=pd.DataFrame(columns=['commonCounterparty','umaAddressesTouchedCount','polymarketWalletsTouchedCount','umaTransferRows','polymarketTransferRows','umaDirections','polymarketDirections','umaAssets','polymarketAssets','highVolumeCounterpartyFlag','legalUseCaution'])
    if pair_df.empty:
        pair_df=pd.DataFrame(columns=['commonCounterparty','umaAddress','umaAddressLabels','polymarketWallet','polymarketWalletLabels','umaTransferRows','polymarketTransferRows','umaDirections','polymarketDirections','umaAssets','polymarketAssets','sameAssetFlag','closestTimingSeconds','closestTimingWithin72hFlag','umaValueSumHelper','polymarketValueSumHelper','sampleUmaTxs','samplePolymarketTxs','highVolumeCounterpartyFlag','leadScore','legalUseCaution'])

    cp_df.to_csv(OUT/'03_common_counterparty_summary.csv', index=False)
    pair_df.to_csv(OUT/'04_two_hop_pair_edges.csv', index=False)
    leads=pair_df.copy()
    if not leads.empty:
        leads=leads[(leads['highVolumeCounterpartyFlag']!='YES') & ((leads['closestTimingWithin72hFlag']=='YES') | (leads['sameAssetFlag']=='YES') | (pd.to_numeric(leads['leadScore'], errors='coerce') >= 3))].copy()
        leads=leads.sort_values(['leadScore','closestTimingSeconds'], ascending=[False, True])
    leads.to_csv(OUT/'05_priority_two_hop_leads.csv', index=False)
    pd.DataFrame(failures).to_csv(OUT/'98_step11F_failed_queries.csv', index=False)

    # hashes
    hashes=[]
    for path in sorted(OUT.glob('*.csv')):
        h=hashlib.sha256(path.read_bytes()).hexdigest()
        hashes.append({'filename': path.name, 'sha256': h})
    pd.DataFrame(hashes).to_csv(OUT/'99_step11F_file_hashes.csv', index=False)

    summary = f"""Step 11F focused two-hop Polygon relation screen
Collected at UTC: {datetime.now(timezone.utc).isoformat()}
Block window: {START_BLOCK} to {END_BLOCK}
Transfer categories: {', '.join(CATEGORIES)}
Priority threshold processed: <= {PRIORITY_THRESHOLD}
UMA addresses queried: {len(uma)}
Polymarket wallets queried: {len(poly)}
UMA counterparty transfer rows: {len(uma_df)}
Polymarket counterparty transfer rows: {len(poly_df)}
Common counterparties found: {len(cp_df)}
Two-hop pair edges produced: {len(pair_df)}
Priority two-hop lead rows produced: {len(leads)}
Failed queries: {len(failures)}

Interpretation:
This step checks whether a priority UMA YES voter/delegate address and a priority Polymarket YES buyer/redeemer/token-path wallet touched the same Polygon counterparty in the relevant block window.
A common counterparty is only an investigative lead. It does not prove common ownership, coordination, or beneficial interest.
Exchange, bridge, router, relayer, aggregator, public contract, and high-volume addresses should be treated as weak unless supported by additional facts.

Recommended review order:
1. 05_priority_two_hop_leads.csv
2. 04_two_hop_pair_edges.csv
3. 03_common_counterparty_summary.csv
4. 01_uma_polygon_counterparty_edges.csv and 02_polymarket_polygon_counterparty_edges.csv for raw transaction support
"""
    (OUT/'00_step11F_run_summary.txt').write_text(summary, encoding='utf-8')
    print(summary)

if __name__ == '__main__':
    main()
