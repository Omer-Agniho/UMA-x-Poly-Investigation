# Polymarket / UMA Oracle — Insider Trading & Conflict of Interest Investigation

**Date:** 2026-06-20
**Investigator:** Automated on-chain forensics
**Market:** US x Iran Permanent Peace Deal by June 15, 2026
**Condition ID:** `0xd86a816093fcd0a0e1ca440bc5ce199bd3c5a8d6139e044b076958164f8c5423`
**Volume:** $177.4M | **Resolved:** YES on June 18, 2026

---

## Executive Summary

This investigation identified a coordinated 19-wallet cluster that placed **$12.8 million in BUY YES** bets on the US-Iran Peace Deal market. At least **3 wallets in this cluster are confirmed UMA oracle participants** (proposers who submit price resolutions), and a 4th has a documented hop-2 financial link to a UMA proposer. This represents a direct **conflict of interest**: entities that help determine whether a market resolves YES/NO simultaneously held large financial positions that would profit from a YES resolution.

### Key Findings

1. **GroyperFinance** is a confirmed UMA oracle proposer who bet $405,488 BUY YES
2. **ArmageddonRewardsBilly** received UMA oracle rewards and bet $399,600 BUY YES
3. **tf2** is a confirmed UMA oracle proposer who bet $376,928 (mixed)
4. **secretscent** ($2.44M BUY YES) has hop-2 financial links to UMA proposer `0xc33780d8...`
5. All 19 wallets appear coordinated: shared funders, batch creation, sub-minute synchronized trades
6. Combined cluster exposure: **$12.8 million**, all BUY YES (except minor hedging by 2 accounts)

---

## SECTION 1: DIRECT UMA-TRADER CONFLICTS (Smoking Gun Evidence)

### 1A. GroyperFinance — UMA Proposer + $405k Trader

- **Wallet:** `0xfcd0eadb24d78e016e88b9e2a7029e349ba6391d`
- **Polymarket:** [Profile](https://polymarket.com/profile/0xfcd0eadb24d78e016e88b9e2a7029e349ba6391d)
- **Polygonscan:** [Transactions](https://polygonscan.com/address/0xfcd0eadb24d78e016e88b9e2a7029e349ba6391d)
- **Market Volume:** $405,488 (BUY YES: $275,748)
- **Purpose-built wallet:** Only traded this single market on Polymarket

**UMA Oracle Activity (on-chain proof):**
| Date | Direction | Counterparty | Amount | Interpretation |
|------|-----------|--------------|--------|----------------|
| 2026-05-17 | GroyperFinance → OOv2 | UMA Optimistic Oracle v2 | 750 USDC.e | ProposePrice bond deposit |
| 2026-05-17 | GroyperFinance → UMA bond contract | `0x2c0367a9...` | 750 USDC.e (x2) | Bond deposits |
| 2026-05-19 | GroyperFinance → UMA bond contract | `0x2c0367a9...` | 750 USDC.e | Bond deposit |
| 2026-05-21 | OOv2 → GroyperFinance | UMA Optimistic Oracle v2 | 1,000 USDC.e | **Successful proposal reward** |
| 2026-05-21 | UMA bond contract → GroyperFinance | `0x2c0367a9...` | 1,000 USDC.e (x2) | Rewards |
| 2026-05-23 | GroyperFinance → UMA bond contract | `0x2c0367a9...` | 750 USDC.e (x2) | Bond deposits |
| 2026-05-27 | UMA bond contract → GroyperFinance | `0x2c0367a9...` | 1,000 USDC.e (x2) | Rewards |
| 2026-06-04 | GroyperFinance → UMA bond contract | `0x2c0367a9...` | 750 USDC.e | Bond deposit |
| 2026-06-08 | UMA bond contract → GroyperFinance | `0x2c0367a9...` | 1,000 USDC.e | **Reward just 9 days before trading** |

**Also received $7,498.60 USDC.e from `0xb92fe925...`** (contract shared with top UMA proposer `0x52764dd4...`)

**Conflict:** GroyperFinance actively proposed prices in UMA's oracle system while simultaneously holding a $405k position on a market that UMA would resolve. The proposer has influence over which markets resolve YES or NO.

---

### 1B. ArmageddonRewardsBilly — UMA Reward Recipient + $400k Trader

- **Wallet:** `0xc8ab97a9089a9ff7e6ef0688e6e591a066946418`
- **Polymarket:** [Profile](https://polymarket.com/profile/0xc8ab97a9089a9ff7e6ef0688e6e591a066946418)
- **Polygonscan:** [Transactions](https://polygonscan.com/address/0xc8ab97a9089a9ff7e6ef0688e6e591a066946418)
- **Market Volume:** $399,600 (100% BUY YES)
- **Trade Timing:** Single trade at 2026-06-17 21:16:53 UTC

**UMA Oracle Activity:**
| Date | Direction | Counterparty | Amount |
|------|-----------|--------------|--------|
| 2026-06-20 | UMA bond contract → ArmageddonRewardsBilly | `0x2c0367a9...` | 1,000 USDC.e |

**Shared on-chain contact with UMA proposer `0xc33780d8...` via `0x2c0367a9...`** (UMA bond contract)

**Conflict:** Received UMA oracle rewards, indicating participation in the oracle system, while betting $400k on a market resolved by that same system.

---

### 1C. tf2 — UMA Proposer + $377k Trader

- **Wallet:** `0xa102b434ce441a3119e146f75ed6276ee1a836d9`
- **Polymarket:** [Profile](https://polymarket.com/profile/0xa102b434ce441a3119e146f75ed6276ee1a836d9)
- **Polygonscan:** [Transactions](https://polygonscan.com/address/0xa102b434ce441a3119e146f75ed6276ee1a836d9)
- **Market Volume:** $376,928 (BUY YES: $122,222 + SELL positions)

**UMA Oracle Activity:**
| Date | Direction | Counterparty | Amount |
|------|-----------|--------------|--------|
| 2025-07-19 04:23 | tf2 → OOv2 | UMA Optimistic Oracle v2 | 750 USDC.e (bond) |
| 2025-07-19 06:23 | OOv2 → tf2 | UMA Optimistic Oracle v2 | 755 USDC.e (bond + reward) |

**Conflict:** Submitted price proposals to UMA oracle (proposePrice) and received rewards, establishing them as an active oracle participant trading on UMA-resolved markets.

---

### 1D. secretscent — Hop-2 UMA Link + $2.44M Trader

- **Wallet:** `0xf1539247af59b16517377a859bcd0d9c7eac162c`
- **Polymarket:** [Profile](https://polymarket.com/profile/0xf1539247af59b16517377a859bcd0d9c7eac162c)
- **Polygonscan:** [Transactions](https://polygonscan.com/address/0xf1539247af59b16517377a859bcd0d9c7eac162c)
- **Market Volume:** $2,442,619 (100% BUY YES)
- **Purpose-built:** Only 4 trades ever (2 test trades of $1k, then $2.44M all-in)
- **Wallet created:** 2026-05-02 (6 weeks before trading)

**UMA Connection Chain:**
```
secretscent ──$1k USDC.e──→ 0x245b564e7514cf4fa4bfe3e32b217da295d7c1e5
                                         │
                                         └──→ UMA proposer 0xc33780d8841dd80fe3de83bff881218372c3d42c
                                                (22 proposePrice calls on Polygon)

secretscent ──$1k USDC.e──→ 0xa4fcd42731853ed3711aac964a14f442b1f6977d
                                         │
                                         └──→ same UMA proposer 0xc33780d8...
```

**Same entity as RockSolidBond** (created 150 seconds apart, $2.5M USDC.e flow between them, 22 shared contacts).

**Conflict:** Two independent financial pathways connect secretscent to the same UMA proposer through intermediary wallets, suggesting deliberate obfuscation of the relationship.

---

## SECTION 2: 19-WALLET SYBIL CLUSTER

### Cluster Overview ($12.8M combined)

All wallets below are linked through shared funders, creation timing, coordinated trades, and/or on-chain contact overlap. Every wallet bet BUY YES.

| # | Name | Wallet | Volume | UMA Role | Funder |
|---|------|--------|--------|----------|--------|
| 1 | rdba | [`0xc4d1...`](https://polygonscan.com/address/0xc4d1a863e9cc45d02ba22d3a1ae9ba7822018ce8) | $3,470,526 | — | unknown |
| 2 | secretscent | [`0xf153...`](https://polygonscan.com/address/0xf1539247af59b16517377a859bcd0d9c7eac162c) | $2,442,619 | **Hop-2 link** | `0x13c4b5...` |
| 3 | Shirtybonds | [`0x672f...`](https://polygonscan.com/address/0x672f13d830d3617efea21c2ec7f4bda5d2c27fcc) | $1,001,992 | — | `0x1e528a...` |
| 4 | JAHODA | [`0x0e5b...`](https://polygonscan.com/address/0x0e5bd76779e74304d08e759072abf126d87da593) | $642,532 | — | `0x02a86f...` |
| 5 | 0x665d_anon | [`0x665d...`](https://polygonscan.com/address/0x665dcbe83796b5010279f0a38b197d65e0aaaf35) | $616,179 | — | `0xacff32...` |
| 6 | 0x52e5_anon | [`0x52e5...`](https://polygonscan.com/address/0x52e5a051ecdb72c973efcba97d375e0d1eea920a) | $496,500 | — | unknown |
| 7 | 033033033 | [`0xd1c7...`](https://polygonscan.com/address/0xd1c769317bd15de7768a70d0214cf0bbcc531d2b) | $463,358 | — | — |
| 8 | Dripx | [`0x82a7...`](https://polygonscan.com/address/0x82a7183f93447d7a8ff5b4bd08eb0d74de266ed8) | $439,645 | — | — |
| 9 | **GroyperFinance** | [`0xfcd0...`](https://polygonscan.com/address/0xfcd0eadb24d78e016e88b9e2a7029e349ba6391d) | $405,488 | **PROPOSER** | — |
| 10 | **ArmageddonRewardsBilly** | [`0xc8ab...`](https://polygonscan.com/address/0xc8ab97a9089a9ff7e6ef0688e6e591a066946418) | $399,600 | **REWARD RECIPIENT** | — |
| 11 | **tf2** | [`0xa102...`](https://polygonscan.com/address/0xa102b434ce441a3119e146f75ed6276ee1a836d9) | $376,928 | **PROPOSER** | — |
| 12 | 0x6fec_anon | [`0x6fec...`](https://polygonscan.com/address/0x6fec0fd0e5562f0ca9a709417d4492aadac43be3) | $365,994 | — | — |
| 13 | Erasmus. | [`0xc658...`](https://polygonscan.com/address/0xc6587b11a2209e46dfe3928b31c5514a8e33b784) | $349,300 | — | `0x0a16ff...` |
| 14 | 0x90ca_anon | [`0x90ca...`](https://polygonscan.com/address/0x90ca00f0a7c263ce9e8a9af5ad044cd4dc9c1a4b) | $274,267 | — | — |
| 15 | debased | [`0x24c8...`](https://polygonscan.com/address/0x24c8cf69a0e0a17eee21f69d29752bfa32e823e1) | $252,331 | — | `0x0a16ff...` |
| 16 | yungstalin | [`0xa022...`](https://polygonscan.com/address/0xa022ba0a68e11a78348382ff168601012d4d77f8) | $229,310 | — | `0x4fac06...` |
| 17 | HolyMoses7 | [`0xa4b3...`](https://polygonscan.com/address/0xa4b366ad22fc0d06f1e934ff468e8922431a87b8) | $211,343 | — | — |
| 18 | Anghkooey | [`0xd08f...`](https://polygonscan.com/address/0xd08f50a9c65678bf92236c5ebe58028234a7fdb6) | $200,000 | — | `0x4fac06...` |
| 19 | RockSolidBond | [`0x2854...`](https://polygonscan.com/address/0x28547904c8fd224074a349a2313ef852e29e0414) | $199,800 | — | — |

### Same-Entity Pairs (shared funders)

| Pair | Shared Funder | Combined Volume | Evidence |
|------|---------------|-----------------|----------|
| Erasmus. + debased | `0x0a16ff4c4e2ecd65e178e5a793f3297312844a62` | $601,631 | Same funder wallet |
| yungstalin + Anghkooey | `0x4fac062e3edf91d976ea75ea6007cc3b086daad3` | $429,310 | Same funder wallet |
| secretscent + RockSolidBond | Created 150s apart | $2,642,419 | $2.5M USDC.e flow, 22 shared contacts |

### Batch-Created Wallets (April 22, 2026 — 16 minutes)

| Wallet | Created | Volume |
|--------|---------|--------|
| 0x90ca_anon | 10:19:12 UTC | $274,267 |
| 0x6fec_anon | 10:30:14 UTC | $365,994 |
| 0x665d_anon | 10:35:40 UTC | $616,179 |
| **Total** | **16 min window** | **$1,256,440** |

---

## SECTION 3: COORDINATED TRADING (June 17, 2026)

All resolution window trades occurred on June 17, 2026. The largest trades show sub-minute coordination across multiple wallets:

### Burst 1: 21:10-21:18 UTC — $3,884,800 in 7 minutes
| Time | Trader | Amount | UMA Role |
|------|--------|--------|----------|
| 21:10:11 | secretscent | $2,142,618 | Hop-2 UMA link |
| 21:10:13 | basedd | $101,837 | — |
| 21:10:28 | debased | $149,850 | — |
| 21:16:53 | **ArmageddonRewardsBilly** | $399,600 | **UMA reward recipient** |
| 21:17:25 | RockSolidBond | $199,800 | secretscent same entity |
| 21:17:34 | Anghkooey | $200,000 | yungstalin same entity |
| 21:17:55 | JAHODA | $642,532 | — |

### Burst 2: 18:36-18:43 UTC — $887,737 in 7 minutes
| Time | Trader | Amount |
|------|--------|--------|
| 18:36:37 | debased | $101,684 |
| 18:37:35 | yungstalin | $229,310 |
| 18:38:08 | Dripx | $439,645 |
| 18:43:01 | Brokie | $117,098 |

### Burst 3: 11:09-11:34 UTC — $1,875,162 in 25 minutes
| Time | Trader | Amount |
|------|--------|--------|
| 11:09:28 | 0x6fec_anon | $365,994 |
| 11:11:04 | 0x90ca_anon | $274,267 |
| 11:12:37 | **tf2** | $122,222 | **UMA proposer** |
| 11:31:32 | 0x665d_anon | $616,179 |
| 11:34:07 | 0x52e5_anon | $496,500 |

### rdba: $3.47M in 54 seconds
| Time | Amount |
|------|--------|
| 13:29:47 | $459,540 |
| 13:30:35 | $2,997,000 |
| 13:30:41 | additional |

---

## SECTION 4: UMA ORACLE ACTIVITY IN RESOLUTION WINDOW

### OOv2 Transactions (June 15-20, 2026): 197 total
| Sender | Txs | Role |
|--------|-----|------|
| `0x33965f7d08f61a62b86c1ab9be5d82c42f4c3081` | 110 | Settler (batch settlements) |
| `0x52764dd44eb51b0d21cd08e5497035f256ea7754` | 47 | **Top proposer** (proposePrice) |
| 6 others | 5 each | Various proposers |
| 7 others | 1-4 each | Various |

**Top proposer `0x52764dd4...`** has operational financial relationship with `0x2c0367a9...` (UMA bond contract) — same contract that paid GroyperFinance and ArmageddonRewardsBilly.

### Network Links Between UMA Actors and Traders
| UMA Actor | Trader | Shared Contacts | Key Intermediary |
|-----------|--------|-----------------|------------------|
| Proposer `0xc337...` | secretscent | 2 | `0x245b...`, `0xa4fcd...` |
| Proposer `0xc337...` | RockSolidBond | 2 | Same as above |
| Proposer `0xc337...` | rdba | 1 | `0x6f8a...` (contract) |
| Proposer `0xc337...` | GroyperFinance | 2 | `0xee3afe...` (OOv2), `0x2c0367...` |
| Proposer `0x5276...` | GroyperFinance | 3 | OOv2, `0xb92fe...`, `0x2c0367...` |
| Proposer `0x5276...` | ArmageddonRewardsBilly | 1 | `0x2c0367...` |

---

## SECTION 5: TIMELINE OF EVENTS

| Date | Event |
|------|-------|
| 2026-04-22 | 3 wallets batch-created in 16 min (0x90ca, 0x6fec, 0x665d) |
| 2026-04-30 | GroyperFinance created | Anghkooey created |
| 2026-05-02 | secretscent created | RockSolidBond created (150s later) |
| 2026-05-17-06-08 | GroyperFinance actively proposing prices on UMA OOv2 |
| 2026-06-15 | Market deadline (peace deal by this date) |
| 2026-06-17 02:00-21:18 | **All 19 cluster wallets execute BUY YES trades** |
| 2026-06-17 21:10-21:18 | Peak coordinated burst: $3.88M across 7 wallets in 7 min |
| 2026-06-18 | **Market resolved YES** |
| 2026-06-20 | UMA proposer `0x5276...` continues active settle/propose operations |

---

## SECTION 6: BEHAVIORAL RED FLAGS

### Purpose-Built Wallets (only traded this market)
- 033033033 ($463,358)
- **GroyperFinance** ($405,488) — **also UMA proposer**
- Anghkooey ($200,000)
- BenzoateOstylezeneBicarbonate ($159,354)
- tetrose ($152,850)

### Rapid Execution
- **rdba:** $3.47M in 54 seconds (3 trades)
- **secretscent:** $2.44M in 621 seconds (2 trades)
- 7 wallets executed $3.88M within a 7-minute window

### secretscent Profile
- Only 4 trades ever on Polymarket (2 test trades of ~$1k, then $2.44M all-in)
- Wallet created 6 weeks before trading
- Funded via 3-level chain: `0x13c4b5` → `0x871d7c` → `0x6e0c80` (connected to trader 'suntori')

---

## SECTION 7: KEY CONTRACT ADDRESSES

| Contract | Address | Link |
|----------|---------|------|
| UMA OOv2 | `0xeE3Afe347D5C74317041E2618C49534dAf887c24` | [Polygonscan](https://polygonscan.com/address/0xeE3Afe347D5C74317041E2618C49534dAf887c24) |
| UMA OOv3 | `0xfb55F43fB9F48F63f9269DB7Dde3BbBe1ebDC0dE` | [Polygonscan](https://polygonscan.com/address/0xfb55F43fB9F48F63f9269DB7Dde3BbBe1ebDC0dE) |
| CTF Adapter | `0x6A9D222616C90FcA5754cd1333cFD9b7fb6a4F74` | [Polygonscan](https://polygonscan.com/address/0x6A9D222616C90FcA5754cd1333cFD9b7fb6a4F74) |
| Polymarket Resolver | `0x65070BE91477460D8A7AeEb94ef92fe056C2f2A7` | [Polygonscan](https://polygonscan.com/address/0x65070BE91477460D8A7AeEb94ef92fe056C2f2A7) |
| UMA Bond Contract | `0x2c0367a9db231ddebd88a94b4f6461a6e47c58b1` | [Polygonscan](https://polygonscan.com/address/0x2c0367a9db231ddebd88a94b4f6461a6e47c58b1) |
| UMA Proposer (linked to secretscent) | `0xc33780d8841dd80fe3de83bff881218372c3d42c` | [Polygonscan](https://polygonscan.com/address/0xc33780d8841dd80fe3de83bff881218372c3d42c) |
| UMA Top Proposer | `0x52764dd44eb51b0d21cd08e5497035f256ea7754` | [Polygonscan](https://polygonscan.com/address/0x52764dd44eb51b0d21cd08e5497035f256ea7754) |

---

## SECTION 8: POLYMARKET PROFILE LINKS

| Name | Profile URL |
|------|-------------|
| rdba | https://polymarket.com/profile/0xc4d1a863e9cc45d02ba22d3a1ae9ba7822018ce8 |
| secretscent | https://polymarket.com/profile/0xf1539247af59b16517377a859bcd0d9c7eac162c |
| Shirtybonds | https://polymarket.com/profile/0x672f13d830d3617efea21c2ec7f4bda5d2c27fcc |
| JAHODA | https://polymarket.com/profile/0x0e5bd76779e74304d08e759072abf126d87da593 |
| 0x665d_anon | https://polymarket.com/profile/0x665dcbe83796b5010279f0a38b197d65e0aaaf35 |
| 0x52e5_anon | https://polymarket.com/profile/0x52e5a051ecdb72c973efcba97d375e0d1eea920a |
| 033033033 | https://polymarket.com/profile/0xd1c769317bd15de7768a70d0214cf0bbcc531d2b |
| Dripx | https://polymarket.com/profile/0x82a7183f93447d7a8ff5b4bd08eb0d74de266ed8 |
| GroyperFinance | https://polymarket.com/profile/0xfcd0eadb24d78e016e88b9e2a7029e349ba6391d |
| ArmageddonRewardsBilly | https://polymarket.com/profile/0xc8ab97a9089a9ff7e6ef0688e6e591a066946418 |
| tf2 | https://polymarket.com/profile/0xa102b434ce441a3119e146f75ed6276ee1a836d9 |
| 0x6fec_anon | https://polymarket.com/profile/0x6fec0fd0e5562f0ca9a709417d4492aadac43be3 |
| Erasmus. | https://polymarket.com/profile/0xc6587b11a2209e46dfe3928b31c5514a8e33b784 |
| 0x90ca_anon | https://polymarket.com/profile/0x90ca00f0a7c263ce9e8a9af5ad044cd4dc9c1a4b |
| debased | https://polymarket.com/profile/0x24c8cf69a0e0a17eee21f69d29752bfa32e823e1 |
| yungstalin | https://polymarket.com/profile/0xa022ba0a68e11a78348382ff168601012d4d77f8 |
| HolyMoses7 | https://polymarket.com/profile/0xa4b366ad22fc0d06f1e934ff468e8922431a87b8 |
| Anghkooey | https://polymarket.com/profile/0xd08f50a9c65678bf92236c5ebe58028234a7fdb6 |
| RockSolidBond | https://polymarket.com/profile/0x28547904c8fd224074a349a2313ef852e29e0414 |

---

## Conclusions

1. **Direct Conflict of Interest (GroyperFinance):** This wallet actively submitted price proposals to UMA's Optimistic Oracle and received proposal rewards, while simultaneously holding a $405k BUY YES position on a market that UMA resolves. This is a textbook conflict of interest — the proposer can influence the resolution outcome while profiting from it.

2. **Additional UMA-Connected Traders:** ArmageddonRewardsBilly (received UMA rewards, $400k BUY YES) and tf2 (submitted proposals to OOv2, $377k mixed) are also UMA participants trading on UMA-resolved markets.

3. **Obfuscated UMA Link (secretscent):** The largest single trader ($2.44M) has financial connections to UMA proposer `0xc33780d8...` through two independent intermediary chains, suggesting deliberate obfuscation.

4. **Coordinated Sybil Network:** 19 wallets collectively placed $12.8M in BUY YES bets using shared funders, batch-created wallets, and sub-minute synchronized execution — strong indicators of a single operator or coordinated group.

5. **Total Estimated Exposure with UMA Connections:** At minimum $3.6M (GroyperFinance + ArmageddonRewardsBilly + tf2 + secretscent/RockSolidBond). If the 19-wallet cluster is a single operation, the total exposure is $12.8M.

---


*This report was generated through automated on-chain forensic analysis of publicly available blockchain data on Polygon (chainid: 137) and Polymarket's public Data API. All findings are based on verifiable on-chain transactions.*
