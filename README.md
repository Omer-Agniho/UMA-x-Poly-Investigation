# Polymarket Iran Peace Deal Market Evidence Repository

## Purpose

This repository organizes evidence and analysis related to the Polymarket market:

`US x Iran permanent peace deal by June 15`

The purpose of this repository is to preserve files, document the investigation, and prepare materials for legal review. The central allegation being investigated is that the market resolved to `YES` even though the written market rules may have required a `NO` outcome by the stated deadline.

This repository is not a final legal conclusion. It is an evidence organization and analysis workspace.

## Plain English summary

A Polymarket market asked whether the United States and Iran would agree to a permanent peace deal by June 15.

Many users believed the written rules required a permanent peace deal by the deadline. The market later resolved to `YES`. NO holders lost money because of that result.

This repository collects the evidence needed to answer several questions:

- What exactly did the market rules require?
- What was the deadline?
- What public evidence existed before the deadline?
- How did UMA voting resolve the market?
- Which wallets bought YES?
- Which wallets redeemed after the YES result?
- Are any UMA YES voters linked to Polymarket YES buyers or redeemers?
- Were there suspicious YES side trades before resolution?
- What evidence should be preserved for lawyers?

## Important caution

The files in this repository should be treated as investigative evidence.

Do not claim that any wallet, person, company, or group committed fraud unless a lawyer confirms that the evidence supports that claim.

Use careful wording:

- `appears`
- `may indicate`
- `requires further review`
- `transaction linked`
- `not yet proven`
- `subject to legal review`

Avoid wording such as:

- `this proves fraud`
- `these wallets are definitely the same person`
- `the market was definitely rigged by these wallets`

## Main case theory being investigated

The core issue is the market result.

The market rules required a permanent US Iran peace deal by June 15 at 11:59 PM ET. The investigation is reviewing whether that condition was actually met by the deadline.

If the condition was not met, the key claim for affected NO holders is that the market resolved contrary to its written rules.

Wallet analysis is supporting evidence. It may help identify who benefited, whether suspicious YES side trading occurred, and whether any YES traders were linked to the resolution process.

## Timeline assumptions

The working timeline uses:

- Market deadline: June 15, 2026 at 11:59 PM ET
- Equivalent UTC time: June 16, 2026 at 03:59 UTC
- Final settlement time used in the investigation: June 18, 2026 at 00:32:19 UTC
- Relevant UMA voting round: 10310
- Relevant UMA price identifier: `YES_OR_NO_QUERY`
- Target child ancillary hash: `0xfebefea9c50649e612e994415e1aade270fc67155c424bcef61618f5c5645be6`

Use UTC for blockchain records. Use ET or New York time for the market deadline.

## Repository structure

Recommended structure:

```text
/00_originals
    Raw files exactly as received or downloaded. Do not edit.

/01_market_rules
    Market rules, screenshots, market metadata, condition ID, question ID, token IDs.

/02_uma_vote
    UMA vote records, whale vote workbook, validation files, round 10310 records.

/03_trades
    Polymarket trade history, YES buyer files, cross market buyer summaries.

/04_activity
    Polymarket user activity records such as trades, redeems, splits, and merges.

/05_erc1155_transfers
    Polygon ERC1155 outcome token transfer evidence.

/06_redemptions
    Redeem activity, transaction receipts, burn logs, collateral transfer logs.

/07_wallet_links
    Wallet matching, shared funder checks, two hop checks, token path analysis.

/08_suspicious_trading
    Bloomberg style suspicious YES buyer analysis and ranking.

/09_timelines
    Master timeline and event sequence.

/10_lawyer_packet
    Clean summaries, evidence indexes, legal review memos, open questions.

/scripts
    Python scripts used to collect, normalize, or analyze data.

/hashes
    SHA256 hash lists for file integrity.
```

## Completed work

The investigation has completed or substantially completed the following:

### Step 4: Market to UMA link

The UMA vote was tied to the relevant Polymarket market through the target child ancillary hash and UMA round 10310.

Important fields preserved:

- UMA round: 10310
- Identifier: `YES_OR_NO_QUERY`
- Target child ancillary hash: `0xfebefea9c50649e612e994415e1aade270fc67155c424bcef61618f5c5645be6`

### Step 7: YES buyer analysis

The analysis identified wallets that bought YES in:

- the target June 15 market
- related future Iran peace markets
- both the target and related future markets

This helps identify wallets with financial interest in a YES resolution.

### Step 8: User activity

Polymarket activity files were collected and repaired to include future related market activity.

Activity types include:

- TRADE
- REDEEM
- SPLIT
- MERGE

### Step 9: ERC1155 transfer analysis

The investigation reviewed Polygon ERC1155 outcome token movement using safer receipt based and indexed transfer methods.

This helps verify whether tokens actually moved on chain.

### Step 10: Redemption analysis

Redemption activity was reviewed to identify wallets that benefited after the YES result.

Current summary:

- 103 redeem activity rows
- 84 redemption transaction receipts fetched
- 36 wallets with redemption activity
- ERC1155 burn logs and ERC20 transfer logs reviewed

Redemption is important because it can show financial benefit after the challenged result.

### Step 11A: Exact wallet match

The investigation checked whether the same exact address appeared as both a UMA voter or delegate and a Polymarket wallet.

Current result:

No exact address match was found.

This does not prove there is no relationship. It only means the same exact address was not found in both datasets.

### Step 11B: Direct UMA to Polymarket transfer link

The investigation checked direct Polygon native or ERC20 transfers between UMA addresses and prioritized Polymarket wallets.

Current result:

No direct Polygon transfer link was found.

### Step 11C: Shared Polygon funder

The investigation checked whether the same Polygon source wallet funded both UMA addresses and priority Polymarket wallets.

Current result:

No shared Polygon funder was found in that tested set.

### Step 11D: Token path analysis

The investigation found Polymarket side ERC1155 token paths between direct target and future buyer or redeemer wallets and future only redeemer wallets.

This is useful because some wallets that looked future only may have received tokens from wallets already classified as target and future buyer or redeemer wallets.

This does not prove common ownership. It is transaction level token path evidence.

### Step 11E: YES buyer funding analysis

The investigation checked funding sources for YES buyer wallets, including wallets that bought YES but did not redeem.

Current result:

- 107 YES buyer wallets queried
- 101 UMA addresses queried
- 58,280 incoming transfer rows to YES buyers
- 7 incoming transfer rows to UMA addresses
- 0 direct UMA address to YES buyer funding edges
- 0 common funder addresses found
- 0 failed queries

This means no direct Polygon funding link or shared Polygon funder was found in the tested data. It does not prove there are no relationships.

## Why negative wallet link results still matter

A negative result is still useful evidence.

It tells lawyers what was tested and what was not found.

However, these results should be described narrowly.

Correct wording:

`The current analysis did not identify a direct Polygon funding link or shared Polygon funder between the tested UMA address set and tested YES buyer wallet set.`

Incorrect wording:

`There were no relationships between UMA voters and YES buyers.`

The second statement is too broad because relationships can be hidden through exchanges, bridges, intermediaries, different wallets, delegates, token transfers, or off chain arrangements.

## Why suspicious YES trading still matters

Even if no UMA wallet link is found, suspicious YES trading can still help the case.

It can show:

- who benefited from the challenged YES result
- whether some traders had unusual timing
- whether large YES positions were bought at low prices before public information
- whether further discovery is needed
- whether the resolution created profits for unusually positioned traders

This is different from proving that a UMA voter and a YES buyer are the same person.

Both questions matter, but they are separate.

## Next planned work

### Step 11F: Two hop relation analysis

This checks whether UMA wallets and Polymarket wallets are linked through an intermediary.

Examples:

```text
UMA wallet to intermediary to Polymarket wallet
Polymarket wallet to intermediary to UMA wallet
```

This step should be focused on priority wallets only.

### Step 11H: Suspicious YES buyer ranking

This is a Bloomberg style analysis.

It should rank YES buyers by suspicious trading features:

- new or low history accounts
- large YES buys
- low price YES buys
- purchases shortly before market moving information
- concentrated exposure across related markets
- funding shortly before first trade
- redemption or profit after resolution

### Step 12: Lawyer ready evidence packet

This step packages the evidence into a clean legal review format.

It should include:

- market rules summary
- timeline
- UMA vote summary
- trade summary
- redemption summary
- wallet link findings
- suspicious trading summary
- damages intake structure
- evidence index
- hash list
- open questions for counsel

## Evidence handling rules

Keep three versions of important files:

1. Original file
    - Do not edit.
    - Preserve exactly as received.

2. Working copy
    - Used for analysis, notes, classifications, and added columns.

3. Lawyer exhibit copy
    - Clean version containing only verified claims and necessary context.

For each important file, record:

- original filename
- standardized filename
- source
- collection date
- relevant time zone
- SHA256 hash
- short neutral description

## How to read the wallet evidence

Wallet evidence should be classified by strength.

| Level | Meaning |
|---|---|
| A | Same wallet match plus YES holding or redemption |
| B | Direct transaction link plus YES holding or redemption |
| C | Shared funder or strong two hop link |
| D | Circumstantial lead only |
| X | No useful link found or unclear |

Current wallet link status:

- No Level A exact match found yet
- No Level B direct Polygon funding link found yet
- No shared Polygon funder found in tested sets
- Polymarket side ERC1155 token path leads found
- Further two hop and suspicious trading analysis still pending

## Lawyer safe summary

The evidence collected so far identifies the market rules, relevant UMA vote materials, YES side trade activity, redemption activity, ERC1155 token movement, and several wallet link tests. The current wallet link tests have not identified a direct Polygon funding connection or shared Polygon funder between UMA YES voters and tested YES buyer wallets. These results do not rule out indirect, exchange mediated, bridge mediated, delegated, or off chain relationships. The strongest current case theory remains the alleged inconsistency between the market rules and the final YES resolution, with wallet analysis serving as supporting evidence regarding benefit, motive, and potential discovery targets.

## Contributing notes

When adding files:

- preserve raw files
- avoid renaming originals unless a copy is made
- add a short description
- include source and collection time
- record the SHA256 hash
- avoid accusations in filenames
- use UTC for blockchain records
- use ET for the market deadline

## Disclaimer

This repository is for evidence organization and legal review preparation. It is not legal advice and does not contain final legal conclusions. All claims should be reviewed by qualified counsel before being used in litigation, public statements, or fundraising materials.
