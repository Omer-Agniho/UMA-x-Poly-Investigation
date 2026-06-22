# Evidence Index

**Investigation:** Polymarket / UMA Oracle Conflict of Interest
**Primary Market:** US x Iran Permanent Peace Deal by June 15, 2026
**Condition ID:** `0xd86a816093fcd0a0e1ca440bc5ce199bd3c5a8d6139e044b076958164f8c5423`
**Volume:** $177.4M (sub-market) / $478.9M (full event, 16 sub-markets)
**Date compiled:** 2026-06-21

---

## Scope

Files 01-08 and 11 focus on the **permanent peace deal market** (June 15 deadline, $177.4M).
Files 09-10 extend the investigation to two related market events:
- **US x Iran ceasefire extension** (22 sub-markets)
- **US x Iran sign agreement** (4 sub-markets)

---

## Files

| # | File | Description |
|---|------|-------------|
| 01 | `01_cluster_trades.csv` | All 3,100 trades on the peace deal market in the resolution window (June 15-19). Columns: wallet, name, side, outcome, size, price, timestamp. Cluster wallets flagged. Note: tx hashes mostly empty (API limitation). |
| 02 | `02_uma_proposer_reward_txs.csv` | 21 on-chain USDC.e transfers between cluster wallets and the UMA bond contract / OOv2. Shows 750 USDC.e bond deposits and 1,000 USDC.e reward payouts proving GroyperFinance, ArmageddonRewardsBilly, and tf2 are UMA proposers. |
| 03 | `03_decoded_proposePrice_calls.csv` | 210 proposePrice calls to UMA OOv2 on Polygon. Includes sender, timestamp, block, tx hash. Note: ancillaryData decoding is partial — identifier field shows raw hex. |
| 04 | `04_market_resolution_proof.json` | **Smoking gun.** Verified proof that ArmageddonRewardsBilly's wallet executed `resolve()` on the peace deal market while holding $399,600 BUY YES. Includes full timeline (UMA bond deposits at 23:59 -> resolution at 00:31 -> $604k payout at 00:37), call chain, event log topics with matching conditionID/questionID, and identity verification. |
| 05 | `05_shared_funder_edges.csv` | Wallet pairs that share the same funding source. Used to establish sybil cluster links (e.g., Erasmus.+debased share funder `0x0a16ff...`, yungstalin+Anghkooey share `0x4fac06...`). |
| 06 | `06_wallet_creation_timestamps.csv` | First transaction date, funding source, and wallet type (EOA vs Gnosis Safe) for all 19 cluster wallets. Shows batch creation patterns (3 wallets in 16 minutes on April 22). |
| 07 | `07_contract_exclusion_list.csv` | Public smart contracts excluded from link analysis to avoid false positives (DEX routers, bridge contracts, UMA system contracts, Polymarket exchange). |
| 08 | `08_address_types.csv` | Classification of all addresses encountered: Polymarket proxyWallet, EOA, smart contract, UMA system contract, or token counterparty. |
| 09 | `09_cross_market_cluster_activity.csv` | Cluster wallet activity on the ceasefire extension and sign agreement markets. Shows ArmageddonRewardsBilly active in 13/16 sub-markets ($697k), plus cluster members 0x90ca, 0x665d, 0x52e5, JAHODA, 033033033, debased also active. |
| 10 | `10_new_uma_traders_markets2_3.csv` | Two additional UMA-connected traders found in the ceasefire/sign agreement markets: AgricultureSecretary (confirmed UMA proposer, $341k, 20 UMA interactions) and elmcap2 ($3.05M, shares funder with cluster). |
| 11 | `11_resolution_comparison.json` | Comparison of how 6 peace deal sub-markets were resolved. Shows systemic pattern: all 3 user-wallet resolvers (ARB, Rex416, BenzoateOstylezeneBicarbonate) held positions on the markets they resolved, all in the profitable direction. 2 markets resolved by Polymarket's standard bot instead. |
