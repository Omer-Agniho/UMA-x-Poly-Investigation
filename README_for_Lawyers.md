# Final Read Me for Counsel

Polymarket “US x Iran permanent peace deal by June 15, 2026” disputed resolution

Prepared for initial law firm review

Date: 26 June 2026

Confidentiality: Attorney review and claimant group internal use

## Status update on authenticated evidence

As of this update, several evidence branches previously described as leads should now be treated as authenticated evidence at the source-record level. The authenticated materials include raw transaction receipts, decoded logs, Safe-related records, Discord HTML and JSON exports, screenshots, and SHA-256 hash records where preserved.

This update does not ask counsel to treat legal conclusions as proven. It means the underlying records now exist in preserved, hashable form. The remaining questions are legal significance, attribution, control, intent, causation, and available discovery.

## 1. Purpose of this note

This Read Me is intended to give counsel a clear first view of the dispute, the current evidence archive, the strongest authenticated evidence branches, the damages analysis, and the open issues that require legal review or discovery.

The claimant group is not asking counsel to rely on Discord messages as the primary evidence. Discord has been used as an intake location where participants submit files, screenshots, links, transaction hashes, market records, wallet records, and analysis. The underlying materials are being preserved separately, indexed in an evidence register, and hashed for integrity.

Counsel should treat this document as an intake and orientation note, not as a pleading. It separates documented records, claimant allegations, analytical inferences, and open questions.

## 2. Executive summary

The claimant group seeks legal review of the Polymarket market titled “US x Iran permanent peace deal by June 15, 2026.” The group’s position is that the written market rules required a qualifying permanent peace agreement between the United States and Iran by 11:59 PM Eastern Time on 15 June 2026. The group’s analysis has not identified a qualifying agreement by that deadline, yet the market resolved to YES after the UMA related resolution process.

The alleged harm is substantial. The disputed market pool was reported by the group as approximately USD 475 million. One organizer reports a personal loss of approximately USD 2.3 thousand. The claimant group has gathered approximately 200 or more affected or interested participants through Discord. Derived loss analysis currently estimates approximately USD 87.37 million in NO-holder losses across six related markets, including approximately USD 68.28 million attributed to the June 15 market. These loss figures should be treated as derived analysis until tied to primary snapshots, trade records, wallet ownership, and claimant-specific records.

The strongest current evidence themes are as follows. Several items previously described as leads are now supported by preserved raw receipts, exports, screenshots, and hash records. Legal attribution, intent, and ultimate liability remain for counsel and expert review.

1. The rule-based dispute: the group contends that no qualifying permanent peace deal existed by the deadline required by the written rules.

2. Market identity and oracle linkage: the investigation has preserved a chain linking the public Polymarket market to Polymarket metadata, question identifiers, token identifiers, Polygon resolution records, and UMA DVM voting round 10310.

3. UMA vote reconstruction: the available UMA evidence identifies voting round 10310, price identifier YES_OR_NO_QUERY, the relevant ancillary data hash, and substantial YES voting power with concentration.

4. Trading and redemption evidence: the investigation identified YES buyers, ERC1155 token movement, redemption activity, and post-resolution payout activity.

5. ARB authenticated resolution and benefit exhibit: an important authenticated evidence branch concerns the Polymarket profile or wallet associated with ArmageddonRewardsBilly, wallet `0xc8ab97a9089a9ff7e6ef0688e6e591a066946418`. The evidence supports that this Safe wallet held a material YES position, that the exact market was resolved YES through a transaction executed through that Safe, and that post-resolution proceeds were received or are strongly indicated by preserved transaction records.

6. Earlier wallet-link results: direct same address and simple funding link checks between UMA voters and Polymarket YES buyers or redeemers did not identify a simple transaction supported link in the tested data. This does not defeat the claim. It narrowed the wallet tracing branch and increased the importance of the rule interpretation, resolution process, conflict of interest, trading benefit, and discovery questions.

7. Authenticated targeted wallet findings: later depth-4 and suspect-profiler outputs identified stronger transaction-supported suspect-specific evidence branches, including direct ARB to tf2 transfers, a large shared funding network around `0xc417fd...`, GroyperFinance funding plus UMA oracle infrastructure interaction, and secretscent / RockSolidBond / intermediary flows involving UMA proposer address `0xc337...`.

## 3. Reported background

The relevant market was “US x Iran permanent peace deal by June 15, 2026.” The claimant group reports that the challenged events occurred around 15 June through 18 June 2026. The market allegedly resolved YES despite the claimant group’s view that the written YES criteria were not met by the deadline.

The claimant group’s core concern is not merely that traders lost a prediction market. The central concern is that the resolution may have departed from the written criteria presented to market participants, and that certain actors may have had financial exposure or process roles that require investigation.

The group intends to organize claimant participation and litigation costs through a law firm trust account or another counsel supervised mechanism, rather than allowing one individual to personally hold group funds.

## 4. Market rule issue for counsel

The rule text supplied by the group states that the market would resolve YES if Iran and the United States agreed to a permanent peace deal by the specified date, 11:59 PM Eastern Time. A permanent peace deal was described as an agreement explicitly indicating that military hostilities between the United States and Iran had ended or would permanently cease, or equivalent language clearly signaling a lasting end to military hostilities. Temporary extensions or arrangements that did not definitively end hostilities on a lasting basis would not qualify.

The claimant group’s merits position is that the public record before 11:59 PM Eastern Time on 15 June 2026 did not satisfy the written criteria. Counsel should independently verify the following.

1. Whether any qualifying written agreement, official announcement, signed instrument, joint statement, formal confirmation, or equivalent source existed by the deadline.

2. Whether any source used language that clearly signaled a permanent end to United States and Iran military hostilities.

3. Whether any later event, temporary arrangement, disputed statement, or unrelated physical signing market was improperly treated as satisfying this market.

4. Whether the ultimate YES resolution was consistent with Polymarket’s own rules, public representations, and any applicable dispute process.

## 5. Current evidence organization

The evidence archive is being divided into original evidence and lawyer facing working material.

Original evidence is preserved in unmodified form where available. Working copies, summaries, extracted CSV files, screenshots, hash files, and explanatory notes are kept separately. The evidence register is intended to identify each item, its source, collection date, relevance, verification status, related evidence, hash value, and confidentiality level.

Important preservation principles already adopted are as follows.

1. Discord is treated as an intake and provenance location, not as the primary evidence.

2. Original files should not be edited, overwritten, annotated, or renamed as the only copy.

3. Each material file should receive a stable evidence ID and a SHA 256 hash.

4. Negative results should be preserved because they show what was tested and what was ruled out.

5. Legal conclusions such as fraud, collusion, manipulation, or theft should be avoided in file names and evidence descriptions unless counsel determines that the record supports those characterizations.

## 6. Market identity and UMA linkage evidence

The investigation has focused on proving the identity chain from the public Polymarket market to the UMA related vote and final on-chain resolution.

Key preserved or identified elements include the market title, final outcome as resolved YES, final settlement time reported as 18 June 2026 at 00:32:19 UTC, UMA DVM voting round 10310, price identifier YES_OR_NO_QUERY, question ID, condition ID, ancillary data hash, outcome order, CLOB token IDs, Polygon child request information, Polygon adapter information, Ethereum UMA VoteRevealed events, and YES voting concentration.

A key child ancillary data hash identified in the investigation is `0xfebefea9c50649e612e994415e1aade270fc67155c424bcef61618f5c5645be6`. The related child chain ID is 137. The child oracle identified was `0xac60353a54873c446101216829a6a98cdbbc3f3d`. The child requester identified was `0x2c0367a9db231ddebd88a94b4f6461a6e47c58b1`.

The exact market condition ID identified in the ARB resolution evidence is `0xd86a816093fcd0a0e1ca440bc5ce199bd3c5a8d6139e044b076958164f8c5423`. The corresponding question ID identified there is `0xb0bca505e898b79087fd5057f67c181f661d13ca1a5a091a3db0978a30de125b`.

This identity chain is important because counsel must be able to show that the vote records, resolution records, token records, trades, redemptions, and damages analysis all concern the same market or clearly identified related markets.

## 7. UMA vote evidence and current interpretation

The UMA side evidence supports that the relevant vote involved UMA round 10310, price identifier YES_OR_NO_QUERY, and the relevant ancillary data hash. The reconstructed vote materials showed substantial YES-side UMA voting power and concentration.

The current evidence should be framed carefully. It is appropriate to state that certain UMA voting records supported the YES outcome in the disputed round and that the vote appears highly consequential to the market result. It is not yet appropriate to state that specific UMA voters personally traded or profited on Polymarket unless that is supported by direct wallet evidence, high confidence wallet attribution, or discovery.

The absence of exact same address matches between UMA voting wallets and Polymarket trading wallets is not surprising. UMA voting occurs on Ethereum, while Polymarket trading and redemption activity occurs on Polygon, often through proxy wallets, Safe wallets, delegate arrangements, custodial flows, or separate addresses. A direct match would be strong, but lack of a direct match does not rule out beneficial ownership, coordination, conflict, delegation, or off-chain relationships.


## 7A. Authenticated Discord coordination and vote-influence evidence

The Discord coordination branch is no longer limited to isolated screenshots. The group has preserved and added authenticated source materials for relevant UMA and Polymarket Discord messages, including HTML exports, JSON exports, screenshots, source context, and hash records. For full dispute threads, the preserved materials include entire-thread HTML and JSON exports where available. For ordinary channels rather than threads, the preserved materials include date-bounded channel exports for the relevant periods.

The most important authenticated Discord materials currently concern borntoolate and related UMA voting-discussion or dispute-thread messages. The preserved screenshots and source exports include messages referring to consulting with other whales, keeping voters on the same page, not revealing a vote before reviewing YES-side materials, and presenting a united front for a vote. Additional attached screenshots concern dispute-thread arguments, vote-position statements, and allegations about vote choice or market incentives.

These records should be described as authenticated Discord coordination and vote-influence evidence, not merely as social-media leads. Their legal significance remains for counsel. The strongest use is to compare the message timestamps, authors, deleted-message context, quoted-message context, and channel/thread provenance against UMA voting records, Polymarket trading records, ARB/tf2 relations, shared-funding records, and post-resolution redemption records.

Counsel should request or review the following for each Discord exhibit: server name, channel or thread name, message link, message ID, author ID, timestamp, screenshot filename, export filename, export type, SHA-256 hash, surrounding context, and any relationship to wallet, transaction, or UMA vote records.

## 8. Trading, token movement, and redemption evidence

The investigation collected Polymarket YES buyer activity for the target market and related Iran peace deal markets. A cross market YES buyer review identified approximately 777 unique YES buyer wallets. The analysis grouped wallets into target only buyers, target plus future market buyers, and future market only buyers. Approximate notional totals were about USD 1.54 million for target only buyers, about USD 2.97 million for target and future buyers, and about USD 6.97 million for future market only buyers.

This finding matters because a narrow review of only the June 15 market would miss a large category of wallets that may have benefited from the same disputed resolution theory across related markets. It also shows that the dispute may have affected more than a single isolated market.

The ERC1155 transfer verification strategy shifted from broad block scanning to receipt based verification after RPC issues. The receipt based method used known Polymarket trade transaction hashes and decoded ERC1155 TransferSingle and TransferBatch events from those receipts. This created a more efficient and defensible method for showing token movement within known trade transactions. Approximately 2,320 incoming token movement rows were reported from this receipt based Step 9A process.

Redemption analysis identified 36 wallets with redemption activity, 103 redemption activity rows, 84 redemption transaction receipts, 1,324 ERC1155 burn to zero logs, and ERC20 transfer logs involving selected wallets. Redemption evidence is important because it can show post-resolution economic benefit, not merely pre resolution trading.

## 9. Wallet link analysis and results

The wallet-link branch tested whether UMA addresses could be connected to Polymarket YES buyers, token holders, transfer wallets, or redeemers through simple direct methods.

The current results are as follows.

1. Step 11A found no exact same address matches between UMA addresses and the Polymarket or Step 9B wallet universe.

2. Step 11B checked 108 UMA addresses against 2,563 prioritized Polymarket or Step 9B wallets and found zero direct UMA to priority Polymarket transfer links in the tested Polygon data.

3. Step 11C checked 108 UMA addresses and 36 high priority Polymarket wallets for common Polygon funders and found zero common funder addresses, zero common funder pair edges, zero priority leads, and zero failed queries.

4. Step 11E checked 107 YES buyer wallets and 101 UMA addresses. It reviewed 58,280 incoming transfer rows to YES buyer wallets and 7 incoming transfer rows to UMA addresses. It found zero direct UMA address to YES buyer funding edges, zero common funder addresses, zero common funder pair edges, zero priority funding leads, and zero failed queries.

5. Step 11D identified Polymarket side ERC1155 token path leads between certain direct target and future buyer or redeemer wallets and future only redeemer wallets. These are transaction-level token movement leads inside the Polymarket side wallet universe. They should not be described as proof of common ownership without further evidence.

The lawyer-safe conclusion is that the investigation has not yet found a transaction supported direct or simple funding link between UMA YES voters and Polymarket YES buyers or redeemers in the tested datasets. This is not a concession that no relationship exists. It means the simple on-chain branches tested so far did not identify a direct link. More complex relationships may involve intermediaries, bridges, exchanges, Safe owner structures, delegate authority, custody services, side agreements, or off-chain coordination. Those issues are better suited for legal discovery and professional forensic review.

## 10. ArmageddonRewardsBilly authenticated resolution and conflict exhibit

A separate actor-specific authenticated evidence branch concerns the Polymarket profile or wallet associated with ArmageddonRewardsBilly, referred to in the evidence packet as ARB. The wallet address is `0xc8ab97a9089a9ff7e6ef0688e6e591a066946418`.

The ARB evidence should now be framed as authenticated transaction, log, Safe execution, market identity, YES position, and redemption evidence that raises a serious resolution-process and conflict-of-interest issue. It should not be overstated as final proof of fraud or as proof that UMA DVM voters and YES traders were the same people, but it should no longer be presented as a mere lead.

The strongest ARB points currently preserved and authenticated at the record-level are as follows.

1. Exact market resolution transaction: transaction `0x4594120f7b93d7eadd56e53594f208a3fe3e7b83f715871e59742eac796e017e` was reviewed. Its raw receipt showed a successful transaction routed to the ARB Safe. The receipt contained the target condition ID `0xd86a816093fcd0a0e1ca440bc5ce199bd3c5a8d6139e044b076958164f8c5423`, the target question ID `0xb0bca505e898b79087fd5057f67c181f661d13ca1a5a091a3db0978a30de125b`, and a Resolver event showing price `1e18`, meaning YES.

2. Material YES position: prior activity files and submitted cluster trade material identify a 400,000 BUY YES transaction by ARB on the exact June 15 market. The transaction hash is `0x26e1b61200dacad0e83790468fae4b1fe4de25a7526e410a87298b592e6bcceb`. The records show a purchase of 400,000 YES shares at a price of 0.999, with notional value of approximately USD 399,600.

3. Redemption and payout evidence: a known ARB redemption transaction, `0x4c315e0cd4d9c1e42a90801fa9bf4248a69314cb93aec880d96e5f3110d80eb0`, showed target market redemption activity after the YES resolution. Incoming transfer records also identified a second large payout transaction, `0x4edcecea43e58319eb0bcf61546ed025b6aefd43de31459419fdc7114f6782c5`, for approximately 200,328.309676 USDCE. The combined benefit evidence is approximately USD 604,750.90 where the redemption and payout records are preserved with raw receipts, logs, screenshots, and hashes. Counsel should still verify final accounting treatment and beneficial ownership.

4. Safe execution evidence: Safe Transaction Service API files and related screenshots were preserved to show transaction execution through the Safe. The evidence currently supports execution through the Safe. Signer identity, owner attribution, and beneficial control remain follow up issues.

5. Related market UMA proposal activity: two UMA related transactions involving the ARB Safe, the UMA bond contract, the Polymarket resolver, the YES_OR_NO_QUERY identifier, and proposed YES values were reviewed: `0x4e78e8c3c2108c832549d835f53e9b5c49405da9ddbb4e471b87f596dac199d8` and `0x1f9b73e61e15dc3777a839993087b687792d8eba25c713e163e550fc9bade067`. These appear to relate to later physical signing markets dated June 19 and June 30, not exact June 15 permanent peace deal proposal proof. They should be used as related market pattern evidence unless counsel or technical experts verify a closer connection.

This ARB evidence creates a central counsel review question: whether a wallet with material YES exposure participated in or executed a resolution transaction for the exact market and then received post-resolution proceeds. That question is central to conflict, process fairness, disclosure, platform responsibility, and discovery strategy.

## 11. New targeted wallet findings from depth 4 and PolyAudit suspect profiler

This section records new targeted forensic outputs generated after the earlier wallet-link tests. These outputs should be treated as authenticated transaction-supported evidence where raw rows, receipts, exports, and hash records are present. They materially strengthen the conflict-of-interest and shared-funding branches, but they do not by themselves prove fraud, collusion, or common beneficial ownership without legal attribution, timing analysis, and discovery.

### 11.1 Depth-4 Top UMA whale path test

A focused depth-4 on-chain path test was run against the Top 12 UMA whale rows from `Top_60_Whales.csv`, using both staker and delegate / hot wallet target addresses. The run used focused seed mode and known priority Polymarket-side source wallets rather than scanning the full repository address universe.

Key run metrics:

1. Top UMA whale target rows: `12`.
2. UMA target addresses: `24`.
3. Polymarket-side source addresses: `21`.
4. Seed addresses: `45`.
5. On-chain addresses visited: `500`.
6. Path rows produced: `21`.
7. Exact-overlap leads hidden: `true`.
8. Block window: Polygon blocks `84940782` through `88863337`.

The test is useful, but it does not currently prove a strong direct connection to the Top 12 UMA whale voters. Manual review of the 21 path rows indicates that most candidate paths pass through spam-token or generic-contract edges, especially address `0x6f8a06447ff6fcf75d803135a7de15ce88c1d4ec` and the Polygon USDC contract `0x3c499c542cef5e3811e1192ce70d8cc03d5c3359`. These paths should not be treated as evidence of ownership, coordination, or funding unless independently supported by meaningful transfers, timing, or non-generic intermediary behavior.

The lawyer-safe conclusion is that the Top 12 UMA whale path test did not establish a strong Top UMA whale connection. It did, however, provide useful filtering and helped redirect the investigation toward more promising suspect-specific leads involving known Polymarket / UMA actors, shared funders, and proposer wallets.

### 11.2 ARB and tf2 direct relationship

The suspect profiler identified repeated direct transfers between the ARB wallet and the tf2 wallet:

1. ARB / ArmageddonRewardsBilly: `0xc8ab97a9089a9ff7e6ef0688e6e591a066946418`.
2. tf2: `0xa102b434ce441a3119e146f75ed6276ee1a836d9`.

The direct relation file contains `11` transfer rows between these wallets. The meaningful transfers include:

1. tf2 to ARB: `100,000` USDC.e.
2. tf2 to ARB: `200,000` pUSD total.
3. ARB to tf2: approximately `280,571` pUSD total.
4. Multiple CTF / ERC1155 position-transfer rows in both directions.

This is an authenticated direct-relationship exhibit because both wallets are independently relevant to the Polymarket / UMA conflict analysis. ARB is already a key authenticated resolution-process evidence branch. tf2 appears in the investigation as a Polymarket trader with prior UMA oracle activity. The direct ARB to tf2 relationship should be reviewed transaction by transaction and the CTF / ERC1155 token IDs should be mapped to specific Polymarket condition IDs.

Careful wording: the current record supports an authenticated direct on-chain relationship between ARB and tf2. It does not yet prove common ownership, agreement, or collusion, but it is no longer merely a lead.

### 11.3 Shared funding network around `0xc417fd...`

The suspect profiler identified address `0xc417fd8e9661c0d2120b64a04bb3278c17e99db1` as a substantial USDC.e funding source for multiple known YES-side or investigation-relevant wallets.

Aggregated examples include:

1. Shirtybonds: approximately `6.05 million` USDC.e.
2. RockSolidBond: approximately `3.50 million` USDC.e.
3. secretscent: approximately `2.48 million` USDC.e.
4. GroyperFinance: approximately `1.21 million` USDC.e.
5. Anghkooey: approximately `432 thousand` USDC.e.
6. `0x52e5...`: approximately `276.7 thousand` USDC.e.
7. tf2: approximately `103.4 thousand` USDC.e.
8. Dripx: approximately `60 thousand` USDC.e.

This is an authenticated shared-funding exhibit where the underlying transfer rows and hashes are preserved. It may support an inference that multiple apparently separate YES-side or suspect wallets were financed by the same source. The next step is to compare the funding timestamps against each recipient's Polymarket YES purchases and redemptions.

Careful wording: this is funding-cluster evidence supported by transaction records. It does not by itself prove common beneficial ownership or an unlawful agreement, but it strongly supports discovery into wallet control, funding purpose, trading strategy, and account attribution.

### 11.4 GroyperFinance authenticated conflict and UMA-infrastructure exhibit

The GroyperFinance profile output shows both shared funding and UMA oracle infrastructure interaction.

Key findings include:

1. `0xc417fd...` to GroyperFinance: approximately `1.205 million` USDC.e.
2. GroyperFinance to UMA bond contract: approximately `4,500` USDC.e.
3. UMA bond contract to GroyperFinance: approximately `4,000` USDC.e.
4. GroyperFinance to UMA OOv2: approximately `750` USDC.e.
5. UMA OOv2 to GroyperFinance: approximately `1,000` USDC.e.

This makes GroyperFinance an important authenticated conflict and UMA-infrastructure exhibit because the wallet appears financially linked to the shared funding network and separately active around UMA oracle / bond infrastructure. Counsel should review whether the relevant transactions represent UMA proposal activity, rewards, bonds, or other oracle-related operations.

Careful wording: GroyperFinance is transaction-linked to UMA oracle infrastructure and to the `0xc417fd...` funding network. The exact legal significance depends on transaction receipts, market mapping, timing, and wallet attribution.

### 11.5 secretscent, RockSolidBond, intermediaries, and UMA proposer `0xc337...`

The secretscent / RockSolidBond profile output is significant. It shows large flows among secretscent, RockSolidBond, the shared funder `0xc417fd...`, reported intermediaries, and UMA proposer address `0xc33780d8841dd80fe3de83bff881218372c3d42c`.

Aggregated examples include:

1. `0xc417fd...` to secretscent: approximately `2.476 million` USDC.e.
2. `0xc417fd...` to RockSolidBond: approximately `3.495 million` USDC.e.
3. secretscent to RockSolidBond: approximately `4.950 million` USDC.e.
4. `0xc417fd...` to intermediary `0x245b...`: approximately `2.455 million` USDC.e.
5. `0xc417fd...` to intermediary `0xa4fc...`: approximately `1.314 million` USDC.e.
6. intermediary `0x245b...` to UMA proposer `0xc337...`: approximately `436,448` USDC.e.
7. UMA proposer `0xc337...` back to intermediary `0x245b...`: approximately `221,232` USDC.e.
8. intermediary `0xa4fc...` to UMA proposer `0xc337...`: approximately `106,500` USDC.e.
9. UMA proposer `0xc337...` back to intermediary `0xa4fc...`: approximately `53,362` USDC.e.

This is a strong to moderate transaction-supported conflict and funding-network exhibit. It is stronger than the Top 12 UMA whale path theory because it concerns a known UMA proposer address rather than generic Top UMA voting wallets.

Careful wording: the current authenticated record supports meaningful financial pathways among secretscent, RockSolidBond, intermediary wallets, the shared funder, and UMA proposer `0xc337...`. It does not yet prove common ownership or intent. It does justify transaction-level review, market-timing comparison, and discovery.

### 11.6 `0xacff32...` infrastructure / activator lead

The address `0xacff32f36054e039003c7925f7834360531f1f9a` appears repeatedly around multiple relevant wallets, including ARB, debased, HolyMoses7, RockSolidBond, yungstalin, JAHODA, `0x665d...`, secretscent, and GroyperFinance.

This remains an authenticated activity review with moderate legal significance, not a confirmed funding exhibit. Many rows are zero-value native MATIC calls, which may indicate activation, relayer, infrastructure, contract-call, or bot behavior rather than capital funding. The address should be reviewed for wallet-creation timing, proxy or Safe setup behavior, recurring contract-call patterns, and any non-zero asset transfers.

Careful wording: `0xacff32...` is an authenticated possible infrastructure or activator wallet. It should not currently be described as a confirmed funder.

### 11.7 Legal significance of the new findings

The authenticated transaction findings strengthen the process-integrity and conflict-of-interest branches. They point toward the following legal issues for counsel to evaluate:

1. Whether a financially interested wallet participated in, finalized, or benefited from the resolution process.
2. Whether wallets with market exposure were connected to UMA oracle participants or proposer infrastructure.
3. Whether multiple YES-side wallets were funded by a common source.
4. Whether the Polymarket / UMA resolution mechanism allowed conflicted actors to affect a high-value market outcome.
5. Whether NO-holders were deprived of the payout they would have received under the written market criteria.
6. Whether discovery should seek account metadata, Safe signer records, IP logs, device fingerprints, exchange withdrawal records, API keys, and internal Polymarket / UMA communications.

The strongest legal framing remains that this is a rule-based and process-based case. The new wallet evidence supports the argument that the disputed YES outcome may have arisen through a resolution process involving financially interested and interconnected actors. It should be presented as conflict and discovery evidence, not as final proof of fraud.

## 12. Loss analysis and claimant identification

Two damages analysis files were added to the evidence register under the LOSS series.

LOSS 001 is `polymarket_no_holder_losses_by_date.csv`. It summarizes aggregate NO-holder losses across six related US x Iran permanent peace deal markets. The total NO position loss shown across the file is approximately USD 87.37 million, including approximately USD 68.28 million attributed to the June 15 market. Its SHA 256 hash is `ab80777b9148c656bc2d66360b8d24c0a6cdc337f8dc2720735d117c66e26cee`.

LOSS 002 is `polymarket_no_holder_losses_wallet_details.csv`. It provides wallet-level detail for the same loss analysis. It includes 10,570 rows and 8,214 unique proxy wallets. It supports claimant identification, wallet-level damages review, and distribution analysis. Its total loss amount matches the market-level summary in LOSS 001. Its SHA 256 hash is `9fa3f8971dcd21fa6bd7359f638be4f5a55b77fae57bd9ed4bd6641750ec3712`.

Both files should be treated as high relevance derived analysis. They should not be treated as final claimant proof until each claimant is matched to wallet ownership, transaction history, position records, deposits, withdrawals, and any platform account identifiers available through lawful means.

## 13. Current strongest evidence map

The strongest evidence for immediate counsel review is summarized below.

Authenticated evidence branch 1: written rules versus YES resolution. The group alleges that the written rule condition required a permanent peace deal by 15 June 2026 at 11:59 PM Eastern Time and that the public record did not satisfy that requirement. This is the central merits question.

Authenticated evidence branch 2: market identity chain. The investigation has preserved or identified the market title, question ID, condition ID, token IDs, UMA round 10310, price identifier YES_OR_NO_QUERY, ancillary hash, Polygon resolution record, and Ethereum UMA vote records.

Authenticated evidence branch 3: concentrated YES outcome in UMA. The UMA evidence shows substantial YES voting power in the relevant voting round. Counsel should examine whether the process, incentives, disclosures, dispute timing, and voting power concentration support claims or equitable relief.

Authenticated evidence branch 4: ARB conflict and resolution process. The ARB Safe appears to have both material YES exposure and a role in the exact market’s YES resolution transaction, followed by redemption or payout activity. This is the most important actor-specific authenticated evidence branch currently identified.

Authenticated evidence branch 5: post-resolution benefit evidence. Redemption records, ERC1155 burn logs, ERC20 transfer logs, and ARB payout evidence support analysis of who economically benefited from the disputed YES resolution.

Authenticated evidence branch 6: shared funding and suspect-network evidence. New suspect-profiler outputs identify `0xc417fd...` as a substantial USDC.e funding source for multiple known YES-side or investigation-relevant wallets, repeated direct ARB to tf2 transfers, GroyperFinance funding plus UMA oracle infrastructure interaction, and secretscent / RockSolidBond / intermediary flows involving UMA proposer address `0xc337...`.

Authenticated evidence branch 7: damages scale. Derived loss analysis identifies approximately USD 87.37 million in NO-holder losses across six related markets, with approximately USD 68.28 million attributed to the June 15 market. These figures support the seriousness and potential class scale of the dispute, subject to validation.

## 14. Issues requiring counsel or expert review

Counsel should prioritize the following questions.

1. Was the written YES condition met by 11:59 PM Eastern Time on 15 June 2026?

2. Which exact Polymarket rule documents, market page versions, clarifications, and terms governed the market at the time users traded?

3. What was the precise path from market outcome to UMA question, UMA vote, Polygon resolution, and final payout?

4. Who proposed, disputed, voted, relayed, signed, or executed the resolution transactions?

5. Who controlled or benefited from the ARB Safe and any related cluster wallets?

6. Did any person or entity involved in resolution have a financial interest in the YES outcome?

7. What information did Polymarket, UMA, resolvers, proposers, voters, delegates, market makers, or large traders have before, during, and after the resolution window?

8. Were disclosures, conflicts, incentives, rules, or appeal mechanisms adequate under applicable law and platform terms?

9. What primary records are needed to convert derived damages analysis into claimant-specific proof?

10. What claims, venues, arbitration issues, class mechanisms, or group action strategies are available?

## 15. Recommended first package for counsel

The first law firm package should include the following materials.

1. This Read Me.

2. The evidence register with current IDs, descriptions, source fields, verification status, related IDs, hash values, and confidentiality labels.

3. Market rule exhibits, including the full market title, rules, deadline, clarifications, screenshots, and archived market metadata.

4. Public source timeline concerning events before the 15 June 2026 deadline.

5. Market identity package linking Polymarket metadata, question ID, condition ID, token IDs, Polygon resolution records, and UMA round 10310.

6. UMA vote package, including vote validation files, reveal event data, voting power summaries, and concentration notes.

7. Authenticated Discord coordination packet, including borntoolate-related materials, relevant voting-discussion and dispute-thread exports, HTML and JSON files, screenshots, message context, message IDs where available, and hash records.

8. Trading and redemption package, including YES buyer summaries, ERC1155 receipt based token movement, Step 10 redemption outputs, ERC20 transfer outputs, and Step 11 wallet-link outputs.

9. ARB exhibit packet, including the exact resolution receipt, Safe Transaction Service files, Safe screenshots, YES buy proof, redemption proof, payout proof, related market UMA activity, and hash manifest.

10. Depth-4 Top UMA whale path test packet, including run summary, path rows, high-priority outputs, key target edges, Top 12 UMA focus targets, and filtering notes that explain why the Top 12 direct whale-link theory is currently weak.

11. PolyAudit suspect profiler packet, including tracked wallets, all suspect transfers, direct suspect relations, ARB to tf2 direct transfers, `0xc417fd...` funding cluster, `0xacff32...` infrastructure review, GroyperFinance profile, secretscent / RockSolidBond profile, CTF / ERC1155 review, and summary findings.

12. Damages package, including LOSS 001, LOSS 002, claimant intake templates, wallet ownership proof requirements, and current limitations.

13. Known gaps and open questions list.

## 16. Current limitations and careful wording

The investigation has important strengths, but counsel should avoid overstating certain points.

The evidence currently supports a serious challenge to the YES resolution, a material damages theory, an authenticated ARB conflict and resolution process evidence branch, and extensive trading and redemption analysis. It does not yet conclusively prove fraud, market manipulation, collusion, personal control of all wallets, or that UMA DVM voters and YES traders were the same people.

The proper current language is that the evidence raises serious questions requiring legal review, preservation demands, discovery, and expert forensic analysis. Where direct proof exists, such as specific transactions, receipts, token movements, resolution records, Discord exports, screenshots, and hashes, the note identifies those records directly. Discord records are authenticated as to preservation source, export context, and hash records where those materials are present. Where the evidence is inferential, such as beneficial ownership, intent, agreement, or ultimate coordination, the note frames those matters as counsel-review issues rather than final conclusions.

## 17. Proposed legal and discovery focus

The immediate focus for counsel should be preservation and discovery concerning the rule interpretation, resolution decision path, conflict of interest issues, actor identities, wallet control, and damages.

Key discovery targets may include Polymarket market creation records, market rule version history, internal resolution communications, API and database records, dispute and escalation records, UMA oracle question mapping, proposer and resolver records, voter and delegate records, Safe owner and signer records where legally obtainable, large trader records, settlement records, and claimant account records.

The group should continue preserving original files, maintaining hashes, recording source context, and separating claimant identity information for counsel only review.

## 18. Short summary for counsel

The claimant group is organizing a potential legal action concerning the Polymarket market “US x Iran permanent peace deal by June 15, 2026.” The group alleges that the written YES criteria required a qualifying permanent peace agreement by 15 June 2026 at 11:59 PM Eastern Time, that no qualifying agreement existed by that deadline, and that the market nevertheless resolved YES after the UMA related resolution process.

The evidence archive now includes market identity records, UMA voting materials, Polymarket trade records, ERC1155 token movement records, redemption and payout records, wallet-link analysis, ARB resolution process evidence, depth-4 Top UMA whale path testing, PolyAudit suspect-profiler outputs, damages analysis, evidence register rows, and SHA 256 hash manifests. The strongest actor-specific authenticated evidence branch concerns the ARB Safe, which appears to have had a material YES position, participated in the exact market’s YES resolution transaction, and received post-resolution proceeds.

The current evidence does not need to be framed as final proof of fraud to be significant. It supports a substantial rule-based and process-based challenge, authenticated conflict-of-interest evidence branches, authenticated Discord coordination and vote-influence materials, significant damages analysis, and a focused request for legal preservation, discovery, and forensic review.
