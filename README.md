# Polymarket Iran Peace Deal Market Evidence Repository

## Purpose

This repository organizes evidence and analysis related to the Polymarket market:

`US x Iran permanent peace deal by June 15, 2026`

The purpose is to preserve source files, document the investigation, support legal review, and maintain a clear record of what has been collected, tested, verified, and left open.

The central issue being investigated is whether the market resolved to `YES` even though the written market rules may have required a `NO` outcome by the stated deadline.

This repository is not a pleading and does not contain final legal conclusions. It is an evidence organization and analysis workspace for counsel, technical reviewers, and claimant group coordination.

## Plain English summary

The market asked whether the United States and Iran would agree to a permanent peace deal by June 15, 2026.

Many affected users believe the written rules required a definitive permanent peace deal by the deadline. The market later resolved to `YES`. NO holders lost money because of that result.

The investigation is focused on four pillars:

1. Market rule proof: what the written rules required.
2. Real world outcome proof: whether a qualifying permanent peace deal existed by the deadline.
3. Resolution process proof: how the market resolved `YES` and whether the process involved conflicts, concentration, or irregular activity.
4. Damages proof: which NO holders were harmed and what payout they were deprived of.

## Important caution

The files in this repository should be treated as investigative evidence.

Do not claim that any wallet, person, company, or group committed fraud unless counsel confirms that the evidence supports that claim.

Use careful wording:

1. `appears`
2. `may indicate`
3. `requires further review`
4. `transaction linked`
5. `not yet proven`
6. `subject to legal review`
7. `conflict of interest lead`
8. `resolution process concern`
9. `forensic review target`

Avoid wording such as:

1. `this proves fraud`
2. `these wallets are definitely the same person`
3. `the market was definitely rigged by these wallets`
4. `all UMA voters were insiders`
5. `the cluster is conclusively one owner`

## Main case theory being investigated

The strongest current theory is rule based and process based:

NO holders purchased shares under written market rules. Those rules required a permanent United States and Iran peace deal by June 15, 2026 at 11:59 PM ET. The claimant group has not identified a qualifying permanent peace deal by that deadline. The market nevertheless resolved `YES` through the UMA and Polymarket resolution process. As a result, NO holders were deprived of the payout they would have received if the market resolved according to the claimant group’s reading of the written rules.

Wallet analysis is supporting evidence. It may help identify who benefited from the challenged resolution, whether suspicious YES side trading occurred, whether financially interested wallets participated in the resolution process, and whether further discovery is needed.

## Timeline assumptions

The working timeline uses:

1. Market deadline: June 15, 2026 at 11:59 PM ET.
2. Equivalent UTC time: June 16, 2026 at 03:59 UTC.
3. Final settlement time used in investigation: June 18, 2026 at 00:32:19 UTC.
4. Relevant UMA voting round: `10310`.
5. Relevant UMA price identifier: `YES_OR_NO_QUERY`.
6. Target child ancillary hash: `0xfebefea9c50649e612e994415e1aade270fc67155c424bcef61618f5c5645be6`.
7. Target condition ID: `0xd86a816093fcd0a0e1ca440bc5ce199bd3c5a8d6139e044b076958164f8c5423`.
8. Target question ID: `0xb0bca505e898b79087fd5057f67c181f661d13ca1a5a091a3db0978a30de125b`.

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

The folder name `News and Goverment Sources` appears to contain a spelling typo. Do not rename it unless all references in the evidence register, scripts, and file paths are updated.

## Folder guide

### Insider Trading News

Contains screenshots, public reporting, outside commentary, and investigation summaries concerning suspicious trading or possible insider trading in Polymarket markets.

Examples may include:

1. Bloomberg related screenshots or excerpts.
2. Public reporting about unusual Iran market trading.
3. Screenshots concerning UMA dispute arguments.
4. Screenshots concerning resolver or oracle pages.
5. PolyAudit report exports or investigation summaries.

Purpose:

This folder supports the suspicious trading and market integrity branch. These materials may show that outside observers or investigators identified unusual YES side trading. They should be treated as supporting material unless they include raw transaction files, reproducible scripts, or independently preserved source records.

### Market Identity

Contains files used to identify the exact Polymarket market and connect it to UMA and Polygon resolution data.

Visible examples from the repository structure include:

```text
step4_market_identity_outputs/
collect_market_identity.py
README.txt
```

Purpose:

This folder supports the chain from the public Polymarket market to the exact condition ID, question ID, outcome token IDs, CLOB token IDs, and UMA ancillary hash.

### Market Page

Contains screenshots or saved records of the market page.

Purpose:

This folder preserves what users saw on Polymarket, including title, rules, prices, outcome display, resolution state, volume, and relevant page context.

### Market Rules

Contains the market rules and rule screenshots.

Purpose:

This folder is central to the case. It should show the actual written condition for resolving `YES` or `NO`, including the deadline and the definition of a permanent peace deal.

### News and Goverment Sources

Contains public news, official statements, government materials, and other sources relevant to whether the market condition was met before the deadline.

Purpose:

This folder helps answer whether a qualifying permanent peace deal existed before June 15, 2026 at 11:59 PM ET.

### Polymarket Statements

Contains statements, screenshots, or records from Polymarket or Polymarket related sources.

Purpose:

This folder supports review of what Polymarket said publicly or through its platform about the market, the resolution, the rules, and the dispute process.

### Resolution Evidence

Contains evidence related to the final market result and resolution process.

Purpose:

This folder should preserve final resolution status, timing, dispute records, UMA request identity, resolver records, Safe records, transaction receipts, and platform level resolution evidence.

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

This folder contains the main trading, token movement, redemption, and wallet analysis work.

The main investigation flow inside this folder is:

1. Step 7: collect and summarize Polymarket YES buyer history.
2. Step 8: collect user activity records.
3. Step 9: verify ERC1155 token transfers using transaction receipts.
4. Step 9B: trace token movement using indexed asset transfers.
5. Step 10: analyze redemptions after the YES result.
6. Step 11A and Step 11B: exact address and direct transfer checks.
7. Step 11C: shared Polygon funder checks.
8. Step 11D: ERC1155 token path checks.
9. Step 11E: YES buyer funding checks.
10. Step 11F: two hop relation checks.

### Trading and Position Records

Contains trading records and position records that may not be part of the main Step 7 to Step 11 workflow.

Purpose:

This folder should preserve raw or exported position information, holder snapshots, user balances, market level position records, and claimant related position evidence.

### UMA Votes x Yes Shares

Contains UMA vote records, scripts, and validation files.

Visible examples from the repository structure include:

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

1. Top UMA whale voters.
2. Validated UMA YES vote records.
3. Raw UMA VoteRevealed data.
4. Round 10310 request inspection.
5. Ancillary hash discovery.
6. Scripts used to validate UMA vote records.

Important distinction:

The UMA staker wallet is the wallet with voting power. The UMA delegate or caller wallet may be the wallet that actually cast or revealed the vote. Both should be preserved. Do not assume they are the same person unless the evidence supports it.

### Wallets and Blockchain Records

Contains blockchain records, wallet files, transaction records, wallet analysis outputs, Safe records, raw transaction receipts, and wallet link materials.

Purpose:

This folder preserves wallet related evidence that may not belong only to trade history, including raw transaction records, wallet labels, blockchain screenshots, Safe Transaction Service records, and evidence used for wallet link review.

## Completed work and current findings

### Step 4: Market to UMA link

The UMA vote was tied to the relevant Polymarket market through the target child ancillary hash and UMA round 10310.

Important fields preserved:

1. UMA round: `10310`.
2. Identifier: `YES_OR_NO_QUERY`.
3. Target child ancillary hash: `0xfebefea9c50649e612e994415e1aade270fc67155c424bcef61618f5c5645be6`.
4. Child chain ID: `137`.
5. Child oracle: `0xac60353a54873c446101216829a6a98cdbbc3f3d`.
6. Child requester: `0x2c0367a9db231ddebd88a94b4f6461a6e47c58b1`.

### Step 7: YES buyer analysis

The analysis identified wallets that bought YES in:

1. The target June 15 market.
2. Related future Iran peace markets.
3. Both the target and related future markets.

Approximate investigation summary:

1. Unique YES buyer wallets across related markets: `777`.
2. Future market only YES buyers: `700`.
3. Target market only YES buyers: `45`.
4. Wallets buying both target and future markets: `32`.
5. Future market only YES notional: about USD `6.97 million`.
6. Target and future YES notional: about USD `2.97 million`.
7. Target only YES notional: about USD `1.54 million`.

Purpose:

This helps identify wallets with financial interest in a YES resolution and shows that the economic exposure was broader than only the June 15 market.

### Step 8: User activity

Polymarket activity files were collected and repaired to include future related market activity.

Activity types include:

1. `TRADE`
2. `REDEEM`
3. `SPLIT`
4. `MERGE`

### Step 9: ERC1155 transfer analysis

The investigation reviewed Polygon ERC1155 outcome token movement using receipt based and indexed transfer methods.

Step 9A produced approximately `2,320` `IN` rows, which supports receipt level evidence that wallets received YES tokens in known trade transactions.

Purpose:

This moves the evidence from platform activity records into blockchain transaction receipt verification.

### Step 10: Redemption analysis

Redemption activity was reviewed to identify wallets that benefited after the YES result.

Current summary:

1. Redeem activity rows: `103`.
2. Redemption transaction receipts fetched: `84`.
3. Wallets with redemption activity: `36`.
4. ERC1155 burn to zero logs: `1,324`.

Redemption is important because it can show financial benefit after the challenged result.

### Step 11A: Exact wallet match

The investigation checked whether the same exact address appeared as both a UMA voter or delegate and a Polymarket wallet.

Current result:

No exact address match was found.

This does not prove there is no relationship. It only means the same exact address was not found in both datasets.

### Step 11B: Direct UMA to Polymarket transfer link

The investigation checked direct Polygon native or ERC20 transfers between UMA addresses and prioritized Polymarket wallets.

Current result:

No direct Polygon transfer link was found in the tested data.

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

1. YES buyer wallets queried: `107`.
2. UMA addresses queried: `101`.
3. Incoming transfer rows to YES buyers: `58,280`.
4. Incoming transfer rows to UMA addresses: `7`.
5. Direct UMA address to YES buyer funding edges: `0`.
6. Common funder addresses found: `0`.
7. Failed queries: `0`.

This means no direct Polygon funding link or shared Polygon funder was found in the tested data. It does not prove there are no relationships.

## ARB conflict of interest and resolution process lead

This is one of the strongest actor specific leads currently identified.

The relevant wallet or profile is associated with ArmageddonRewardsBilly, referred to as ARB:

`0xc8ab97a9089a9ff7e6ef0688e6e591a066946418`

### ARB evidence status

The ARB evidence should be described as technically supported at the transaction, log, Safe execution, market identity, YES position, and redemption record level, while legal attribution and interpretation remain open for counsel.

The remaining questions are not whether the reviewed records exist. The remaining questions are who controlled the Safe, what role the Safe had in the resolution process, whether the financial exposure created a legally relevant conflict of interest, and whether discovery can identify the responsible persons or entities.

### ARB exact market resolution transaction

Key transaction:

`0x4594120f7b93d7eadd56e53594f208a3fe3e7b83f715871e59742eac796e017e`

Reviewed transaction and log evidence supports that:

1. The transaction was successful.
2. The exact June 15 market was resolved `YES`.
3. The logs included the target condition ID:

`0xd86a816093fcd0a0e1ca440bc5ce199bd3c5a8d6139e044b076958164f8c5423`

4. The logs included the target question ID:

`0xb0bca505e898b79087fd5057f67c181f661d13ca1a5a091a3db0978a30de125b`

5. The Resolver event showed price `1e18`, meaning `YES`.
6. The transaction was routed or executed through the ARB Safe based on the preserved raw transaction details and Safe Transaction Service files.

Important legal framing:

`resolve()` may be a mechanical finalization call after UMA’s oracle process accepts a proposal. It should not be described as proof that ARB alone controlled the outcome. The safer and stronger framing is that ARB appears to have been a financially interested wallet that participated in or finalized the resolution process while holding a profitable YES position.

### ARB YES position evidence

Key transaction:

`0x26e1b61200dacad0e83790468fae4b1fe4de25a7526e410a87298b592e6bcceb`

The activity evidence links ARB to a `400,000` BUY YES transaction on the exact June 15 market at approximately `0.999`, with approximate notional value of USD `399,600`.

This is material because a wallet with a large profitable YES position also appears in the exact market resolution path.

### ARB redemption and payout evidence

Known redemption transaction:

`0x4c315e0cd4d9c1e42a90801fa9bf4248a69314cb93aec880d96e5f3110d80eb0`

This supports post resolution redemption activity of approximately USDCE `404,422.594999`.

Additional payout lead:

`0x4edcecea43e58319eb0bcf61546ed025b6aefd43de31459419fdc7114f6782c5`

This was identified as an additional incoming payout of approximately USDCE `200,328.309676`. If the raw receipt, logs, screenshots, and hash are preserved, it can be treated as verified payout evidence. If any of those materials are missing, keep it marked as a high priority payout lead until completed.

Combined, these records support a post resolution benefit lead of approximately USD `604,750.90`, subject to final receipt level preservation for all payout records.

### ARB related market UMA activity

Two UMA related transactions involving the ARB Safe were reviewed:

1. `0x4e78e8c3c2108c832549d835f53e9b5c49405da9ddbb4e471b87f596dac199d8`
2. `0x1f9b73e61e15dc3777a839993087b687792d8eba25c713e163e550fc9bade067`

These appear to involve related later physical signing markets dated June 19 and June 30, not the exact June 15 permanent peace deal market.

Use them as related market pattern evidence unless counsel or technical experts verify a closer exact market connection.

### Why ARB matters

The ARB evidence raises a central conflict question:

Did a wallet with material YES side exposure participate in or finalize the resolution transaction for the exact market and then receive post resolution proceeds?

If yes, counsel may want discovery into:

1. Safe owners and signers.
2. Safe transaction approvals.
3. Polymarket profile attribution.
4. Resolution authority and permissions.
5. Any Polymarket or UMA knowledge of the wallet’s financial exposure.
6. Whether the resolution mechanism permitted financially interested actors to affect the outcome.

## PolyAudit investigation summary

A PolyAudit investigation reviewed the same market and alleged a broader conflict of interest and coordinated YES side trading pattern.

### Evidence status

The uploaded PolyAudit package previously reviewed contained one substantive `REPORT.html` file and an empty `evidence/` folder. The report referenced raw files such as `trades_raw.json`, `resolution_window_report.json`, `sybil_sweep_report.json`, and other supporting files, but those raw files were not present in that uploaded package.

For that reason, the PolyAudit report should be classified as an investigation summary and discovery lead unless the referenced raw files are separately preserved and hashed in this repository.

If the raw transactions referenced by PolyAudit are independently preserved and verified, the PolyAudit findings materially strengthen the conflict of interest and coordinated trading branch.

### Main PolyAudit allegations and leads

The report alleged that ARB:

1. Held approximately `400,000` YES shares.
2. Had approximately USD `399,600` in YES notional exposure.
3. Participated in UMA proposal or resolution related activity.
4. Executed or finalized the final `resolve(questionID)` path through its Safe.
5. Caused or finalized the YES resolution.
6. Redeemed approximately USD `604,750` shortly after resolution.

The strongest safe framing is:

ARB appears to have been a financially interested wallet that participated in or finalized the resolution process while holding a profitable YES position and later receiving proceeds from the YES resolution.

### Claimed wallet cluster

The PolyAudit report also alleged a `12` or `19` wallet YES side cluster with approximately USD `12.8 million` in BUY YES exposure.

Reported cluster features included:

1. Shared funders.
2. Batch created wallets.
3. Synchronized trades.
4. Common contacts.
5. One market wallet behavior.
6. Links between some traders and UMA oracle participants.

This is strong circumstantial evidence if the raw data is verified. It should not be described as final proof of common ownership until the funding paths, wallet creation data, trade timing, and attribution evidence are independently reproduced.

### Other named PolyAudit leads

1. ArmageddonRewardsBilly: very strong if the raw transaction timeline is independently verified. Most important conflict lead because it combines YES position, resolution path involvement, and redemption.
2. GroyperFinance: strong conflict lead if raw data verifies UMA proposer activity and significant YES exposure.
3. tf2: moderate lead. Prior UMA proposer activity and market trading may be relevant, but older UMA activity is less direct.
4. secretscent: suspicious but indirect. Reported large BUY YES position and hop 2 links to UMA proposer through intermediaries require discovery.
5. Synchronized trading bursts: moderate to strong circumstantial evidence if raw trade timing is verified. Could also be defended as reaction to the same public signal unless combined with wallet links.

### PolyAudit strength assessment

If raw data is verified, the current assessment is:

1. Conflict of interest: very strong.
2. Resolution process failure: strong.
3. Coordinated trading: moderate to strong.
4. Common ownership of wallet cluster: moderate, requires discovery.
5. Insider trading: plausible, not proven.
6. Fraud or manipulation: plausible, requires proof of intent, causation, damages, and responsibility.
7. Claims against Polymarket or UMA: stronger if the system allowed financially conflicted participants to influence or finalize outcomes affecting user funds.

### Discovery value

PolyAudit is valuable because it points counsel toward records that may not be available publicly, including:

1. IP addresses.
2. Account metadata.
3. API keys.
4. Device fingerprints.
5. Exchange withdrawal and KYC records.
6. Internal Polymarket records.
7. UMA proposer, disputer, delegate, and voter records.
8. Safe signer and owner attribution.

## Why negative wallet link results still matter

A negative result is still useful evidence.

It tells lawyers what was tested and what was not found.

Correct wording:

`The current analysis did not identify a direct Polygon funding link or shared Polygon funder between the tested UMA address set and tested YES buyer wallet set.`

Incorrect wording:

`There were no relationships between UMA voters and YES buyers.`

The second statement is too broad because relationships can be hidden through exchanges, bridges, intermediaries, different wallets, delegates, token transfers, custody structures, or off chain arrangements.

## Why suspicious YES trading still matters

Even if no direct UMA wallet link is found, suspicious YES trading can still help the case.

It can show:

1. Who benefited from the challenged YES result.
2. Whether some traders had unusual timing.
3. Whether large YES positions were bought at low prices before public information.
4. Whether clusters of wallets were funded or created in related ways.
5. Whether further discovery is needed.
6. Whether the resolution created profits for unusually positioned traders.

This is different from proving that a UMA voter and a YES buyer are the same person. Both questions matter, but they are separate.

## Damages analysis

Two damages analysis files were added to the evidence register under the LOSS series.

LOSS 001:

1. File: `polymarket_no_holder_losses_by_date.csv`.
2. Description: market level NO holder loss summary by date across six related US x Iran permanent peace deal markets.
3. Approximate total loss across six related markets: USD `87.37 million`.
4. Approximate June 15 market loss: USD `68.28 million`.
5. SHA256 hash: `ab80777b9148c656bc2d66360b8d24c0a6cdc337f8dc2720735d117c66e26cee`.

LOSS 002:

1. File: `polymarket_no_holder_losses_wallet_details.csv`.
2. Description: wallet level NO holder loss detail.
3. Rows: `10,570`.
4. Unique proxy wallets: `8,214`.
5. Total loss amount matches LOSS 001.
6. SHA256 hash: `9fa3f8971dcd21fa6bd7359f638be4f5a55b77fae57bd9ed4bd6641750ec3712`.

These files are high relevance derived analysis. They should not be treated as final claimant proof until each claimant is matched to wallet ownership, transaction history, platform account data where available, and any amounts already recovered.

The basic damages theory for an affected NO holder is:

```text
NO shares held at resolution × $1.00 minus any amount already recovered or received
```

## Current strongest evidence map

1. Written market rules: the case starts with whether the stated criteria were satisfied by the deadline.
2. Final YES resolution: the alleged harm flows from a single uniform resolution event.
3. Market identity chain: links the market page, Polymarket metadata, UMA round, token IDs, condition ID, question ID, and resolution records.
4. UMA round 10310: gives counsel a specific oracle vote and process to review.
5. YES vote concentration: relevant to process fairness, incentives, and discovery.
6. YES buyer and redemption records: helps identify who benefited from the disputed result.
7. ARB conflict lead: actor specific evidence connecting YES exposure, resolution path involvement, and proceeds.
8. PolyAudit cluster lead: potential coordination and common funding evidence, subject to raw data verification.
9. Damages files: supports scale, claimant identification, and potential recovery theory.
10. Hash manifest and evidence register: supports integrity, organization, and legal review.

## How to read the wallet evidence

Wallet evidence should be classified by strength.

1. Level A: same wallet match plus YES holding or redemption.
2. Level B: direct transaction link plus YES holding or redemption.
3. Level C: shared funder or strong two hop link.
4. Level D: circumstantial lead only.
5. Level X: no useful link found or unclear.

Current wallet link status:

1. No Level A exact match found yet.
2. No Level B direct Polygon funding link found yet.
3. No shared Polygon funder found in tested sets.
4. Polymarket side ERC1155 token path leads found.
5. ARB resolution process lead identified.
6. PolyAudit cluster and common funding leads require raw file verification or independent reproduction.
7. Further two hop and suspicious trading analysis remains useful.

## Recommended lawyer package

The first package to counsel should include:

1. This README.
2. Evidence Register.
3. Hash Manifest.
4. Market Rules folder.
5. Market Identity folder.
6. Resolution Evidence folder.
7. UMA Votes x Yes Shares folder.
8. Trade History summary outputs.
9. ARB exhibit packet.
10. PolyAudit report and any raw files supporting it.
11. LOSS 001 and LOSS 002 damages files.
12. Known gaps and open questions.

Do not send an unorganized Discord dump as the first package. Discord should be treated as intake and provenance context. The primary evidence should be the underlying source material, transaction records, screenshots, files, hashes, and source links.

## Open questions for counsel

1. Was the written YES condition met by June 15, 2026 at 11:59 PM ET?
2. Which exact market rules and platform terms governed users at the time they traded?
3. What was the full path from Polymarket market creation to UMA request, vote, resolution, and payout?
4. Who proposed, disputed, voted, relayed, signed, or executed each resolution related transaction?
5. Who controlled the ARB Safe?
6. Did ARB or any related actor have a legally relevant conflict of interest?
7. Did any financially interested actor influence or finalize the market result?
8. Did Polymarket or UMA know or have reason to know about conflicts, irregular activity, or rule inconsistency?
9. Can PolyAudit wallet clusters be independently reproduced from raw data?
10. What primary records are needed to convert derived loss analysis into claimant specific proof?
11. What claims, venues, arbitration procedures, class mechanisms, or group action strategies are available?

## Evidence handling rules

Keep three versions of important files:

1. Original file: preserve exactly as received. Do not edit.
2. Working copy: use for analysis, notes, classifications, and added columns.
3. Lawyer exhibit copy: clean version containing only verified claims and necessary context.

For each important file, record:

1. Original filename.
2. Standardized filename.
3. Source.
4. Collection date.
5. Relevant time zone.
6. SHA256 hash.
7. Short neutral description.
8. Verification status.
9. Related evidence IDs.
10. Confidentiality level.

## Contributing notes

When adding files:

1. Preserve raw files.
2. Avoid renaming originals unless a copy is made.
3. Add a short neutral description.
4. Include source and collection time.
5. Record the SHA256 hash.
6. Avoid accusations in filenames.
7. Use UTC for blockchain records.
8. Use ET for the market deadline.
9. Separate claimant identity materials from public or shared repository materials.
10. Add negative findings as evidence when they show what was tested.

## Lawyer safe summary

The evidence collected so far identifies the market rules, relevant UMA vote materials, YES side trade activity, redemption activity, ERC1155 token movement, ARB resolution process evidence, PolyAudit conflict and cluster leads, damages analysis, and several wallet link tests.

The strongest current case theory remains the alleged inconsistency between the written market rules and the final `YES` resolution. The strongest actor specific lead is ARB, where the reviewed records support material YES exposure, exact market resolution path involvement through a Safe, and post resolution proceeds.

The current wallet link tests have not identified a direct same address match, direct Polygon funding link, or shared Polygon funder between the tested UMA address set and tested YES buyer wallet set. These results do not rule out indirect, exchange mediated, bridge mediated, delegated, custodial, or off chain relationships.

The evidence does not need to be framed as final proof of fraud to be significant. It supports a substantial rule based and process based challenge, a conflict of interest inquiry, significant damages analysis, and a focused request for legal preservation, discovery, and forensic review.

## Disclaimer

This repository is for evidence organization and legal review preparation. It is not legal advice and does not contain final legal conclusions. All claims should be reviewed by qualified counsel before being used in litigation, public statements, or fundraising materials.
