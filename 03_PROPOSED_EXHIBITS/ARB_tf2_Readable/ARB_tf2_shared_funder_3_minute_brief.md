# ARB / tf2 / Shared Funder 3-Minute Brief

Prepared from uploaded ARB files and raw transfer relation files. This is a counsel-facing summary, not a final legal conclusion.

## One paragraph conclusion

The uploaded files support an authenticated transaction exhibit showing that ARB is not an isolated market participant. The records tie the ARB-linked Safe to the target market resolution and payout chain, show direct two-way asset transfers between ARB and tf2 before the dispute window, and show a large shared-funder cluster sending USDCE to multiple investigation-relevant YES-side or UMA-related wallets. This is strong conflict and discovery evidence because it connects financial exposure, resolution activity, redemption activity, and relationship/funding signals in one compact record.

## Relationship map

```text
tf2 0xa102...6d9  <->  ARB Safe 0xc8ab...6418
  11 direct rows, 6 tf2 to ARB and 5 ARB to tf2
  100,000 USDCE + 480,571 pUSD + 4 ERC1155/CTF rows

ARB Safe 0xc8ab...6418
  -> 400,000 YES buy on target market
  -> appears in final YES resolution path
  -> post-resolution redemption flow includes 404,422.594999 USDCE

Shared funder 0xc417...9db1
  -> 65 USDCE transfers totaling 14,100,383.498527 USDCE
  -> recipients include Shirtybonds, RockSolidBond, secretscent, GroyperFinance, tf2, 0x52e5, Anghkooey, Dripx
```

## Critical timeline

| Time UTC | Event | Key fact | Source |
|---|---|---|---|
| 2026-06-17 21:16:53 UTC | ARB 400k YES buy | 400,000 YES on target market, ARB Safe and CTF mentioned | 01_tx_evidence_summary.csv and raw receipt |
| 2026-06-17 23:59:49 UTC | UMA bond/proposal related tx 1 | Contains YES 1e18 data and mentions ARB Safe/Resolver in summary file | 01_tx_evidence_summary.csv and raw receipt |
| 2026-06-17 23:59:58 UTC | UMA bond/proposal related tx 2 | Same pattern, 9 seconds after tx 1 | 01_tx_evidence_summary.csv and raw receipt |
| 2026-06-18 00:31:59 UTC | Final market resolution | Transaction contains condition ID, question ID, YES 1e18, ARB Safe, Resolver, CTF | 01_tx_evidence_summary.csv and raw receipt |
| 2026-06-18 00:36:22 UTC | ARB redemption | Raw logs include 404,422.594999 USDCE redemption flow after YES result | 01_tx_evidence_summary.csv and raw receipt |

## Key authenticated facts

- **ARB-01:** Resolution tx set market result to YES
- **ARB-02:** ARB-linked Safe appears in transaction for 400,000 YES purchase on target market
- **ARB-03:** ARB-linked address received redemption flow after YES resolution, including 404,422.594999 USDCE in raw logs
- **ARB-04:** Two claimed UMA bond/proposal related transactions occurred shortly before resolution and contain YES resolution data
- **ARB-05:** 11 direct transfer rows between tf2 and ARB: 6 tf2 to ARB, 5 ARB to tf2, including 100,000 USDCE and 480,571 pUSD
- **ARB-06:** 0xc417fd sent 65 USDCE transfers totaling 14,100,383.498527 USDCE to several relevant wallets, including tf2, RockSolidBond, secretscent, GroyperFinance and others
- **ARB-07:** Direct suspect relations include large USDCE movements among c417, secretscent, intermediaries, RockSolidBond, and UMA proposer lead c337

## C417 shared funder recipients

| Recipient | Rows | Total USDCE | First | Last |
|---|---:|---:|---|---|
| Shirtybonds | 3 | 6,051,017.190969 | 2026-05-27T15:20:57.000Z | 2026-06-05T08:25:13.000Z |
| RockSolidBond | 19 | 3,495,215.340113 | 2026-06-04T04:53:33.000Z | 2026-06-20T17:16:02.000Z |
| secretscent | 4 | 2,476,082.344810 | 2026-06-04T04:55:31.000Z | 2026-06-20T04:31:19.000Z |
| GroyperFinance | 27 | 1,205,486.151365 | 2026-05-17T13:54:49.000Z | 2026-06-18T12:14:59.000Z |
| Anghkooey | 4 | 432,477.790410 | 2026-06-04T00:46:37.000Z | 2026-06-18T06:05:55.000Z |
| 0x52e5_anon | 3 | 276,703.036820 | 2026-06-06T23:41:33.000Z | 2026-06-10T00:44:19.000Z |
| tf2 | 3 | 103,401.644040 | 2026-05-05T13:27:02.000Z | 2026-05-22T08:25:03.000Z |
| Dripx | 2 | 60,000.000000 | 2026-06-15T21:47:06.000Z | 2026-06-15T21:52:01.000Z |

## What counsel can say now

These files establish authenticated transaction records and transfer relationships. They support a conflict and discovery theory: ARB had market-side activity and redemption exposure, ARB had direct pre-dispute transfers with tf2, and a shared funding cluster connects multiple relevant YES-side or UMA-related actors. The records should be used to seek identity attribution, communications, internal platform review records, wallet control evidence, and UMA proposal/vote relationship evidence.

## Limits

The records prove transactions and relationships between addresses. They do not, by themselves, prove common ownership, an agreement, or intent. Those are the next discovery targets.