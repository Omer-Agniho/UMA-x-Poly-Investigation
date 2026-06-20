# Polymarket Iran Peace Deal Market Evidence Repository

## Purpose

This repository organizes evidence and analysis related to the Polymarket market:

`US x Iran permanent peace deal by June 15`

The purpose is to preserve files, document the investigation, and prepare materials for legal review. The central issue being investigated is whether the market resolved to `YES` even though the written rules may have required a `NO` outcome by the stated deadline.

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

Do not claim that any wallet, person, company, or group committed fraud unless counsel confirms that the evidence supports that claim.

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

The market rules required a permanent United States and Iran peace deal by June 15 at 11:59 PM ET. The investigation is reviewing whether that condition was actually met by the deadline.

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

## Actual repository structure

The current repository is organized under:

```text
POLYMARKET CASE EVIDENCE/
└── 01_ORIGINAL_EVIDENCE/
    ├── Insider Trading News/
    ├── Market Identity/
    ├── Market Page/
    ├── Market Rules/
    ├── News and Goverment Sources/
    ├── Polymarket Statements/
    ├── Resolution Evidence/
    ├── Trade History/
    ├── Trading and Position Records/
    ├── UMA Votes x Yes Shares/
    └── Wallets and Blockchain Records/
```

The folder name `News and Goverment Sources` appears to contain a spelling typo. It should not be renamed without updating references in the evidence index.

## Folder guide

### Insider Trading News

Contains screenshots and source material about suspicious trading, public reporting, and related outside commentary.

Examples visible in this folder include:

- Bloomberg insider trading chart screenshots
- Bloomberg quote screenshot
- Bloomberg article screenshot
- screenshots related to UMA dispute arguments
- screenshots related to UMA or resolver pages
- screenshots of Polymarket related chat or public discussion

Purpose:

This folder supports the suspicious trading branch of the investigation. These materials may help show that outside observers or reporters identified unusual YES side trading. They should be treated as supporting material, not as proof by themselves.

### Market Identity

Contains files used to identify the exact Polymarket market and connect it to UMA resolution data.

Visible files include:

```text
step4_market_identity_outputs/
collect_market_identity.py
README.txt
```

Purpose:

This folder supports the chain from the Polymarket market to the exact condition ID, question ID, token IDs, and UMA ancillary hash.

### Market Page

Contains screenshots or saved records of the market page.

Purpose:

This folder should preserve what users saw on Polymarket, including title, rules, prices, outcome display, resolution state, and relevant page context.

### Market Rules

Contains the market rules and rule screenshots.

Purpose:

This folder is central to the case. It should show the actual written condition for resolving YES or NO, including the deadline and definition of a permanent peace deal.

### News and Goverment Sources

Contains public news, official statements, government materials, and other outside sources relevant to whether the market condition was met before the deadline.

Purpose:

This folder helps answer whether a qualifying permanent peace deal existed before June 15 at 11:59 PM ET.

### Polymarket Statements

Contains statements, screenshots, or records from Polymarket or Polymarket related sources.

Purpose:

This folder supports review of what Polymarket said publicly or through its platform about the market, resolution, rules, or dispute process.

### Resolution Evidence

Contains evidence related to the final market result and resolution process.

Purpose:

This folder should preserve final resolution status, timing, dispute records, UMA request identity, and any platform level resolution evidence.

### Trade History

Contains trade history, user activity, ERC1155 transfer work, redemption analysis, wallet link analysis, and scripts.

Visible structure:

```text
Trade History/
├── step7_TRADE_HISTORY_OUTPUTS/
├── step8_CROSS_MARKET_YES_BUYERS/
├── step9_ERC1155_TRANSFERS/
├── step9b_asset_transfer/
├── step10/
├── step11A and step11B/
├── step11C_polygon_shared_funder/
├── step11D_token_path_outputs/
├── step11E_yes_buyer_funding/
├── step11F_two_hop_relation/
└── collect_polymarket_trades.py
```

Purpose:

This folder contains the main trading and wallet analysis work.

The main investigation flow inside this folder is:

- Step 7: collect and summarize Polymarket YES buyer history
- Step 8: collect user activity records
- Step 9: verify ERC1155 token transfers
- Step 9B: trace token movement using indexed asset transfers
- Step 10: analyze redemptions after the YES result
- Step 11A and Step 11B: exact address and direct transfer checks
- Step 11C: shared Polygon funder checks
- Step 11D: ERC1155 token path checks
- Step 11E: YES buyer funding checks
- Step 11F: two hop relation checks

### Trading and Position Records

Contains trading records and position records that may not be part of the main Step 7 to Step 11 workflow.

Purpose:

This folder should preserve raw or exported position information, market holder records, or trading snapshots.

### UMA Votes x Yes Shares

Contains UMA vote records, scripts, and validation files.

Visible files include:

```text
inspect_round10310_requests.py
round10310_request_inspection.csv
Top_60_Whales.csv
uma_vote_validation.csv
UMA-001_UMA_Iran_VoteRecord_FULL_original.xlsx
UMA-002_raw_UMA_VoteRevealed_YES.json
UMA-003_round10310_ancillary_hash_discovery.csv
validate_uma_votes.py
```

Purpose:

This folder supports the UMA voting branch of the investigation.

It preserves:

- top UMA whale voters
- validated UMA YES vote records
- raw UMA VoteRevealed data
- round 10310 request inspection
- ancillary hash discovery
- scripts used to validate UMA vote records

Important distinction:

The UMA staker wallet is the wallet with voting power.

The UMA delegate or caller wallet may be the wallet that actually cast or revealed the vote.

Both should be preserved. Do not assume they are the same person unless the evidence supports it.

### Wallets and Blockchain Records

Contains blockchain records, wallet files, transaction records, and wallet analysis outputs.

Purpose:

This folder should preserve wallet related evidence that may not belong only to trade history, including raw transaction records, wallet labels, blockchain screenshots, and evidence used for wallet link review.

## Completed work

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
