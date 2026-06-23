# Deep UMA x Polymarket Relation Miner Output

Generated: 2026-06-23T02:26:36+00:00

## Scope

This run searched for relation paths between Polymarket-side wallets, UMA vote-related wallets, UMA proposer or disputer wallets, resolver wallets, funders, and shared counterparties.

Configured depth: 4

Block window: 84940782 to 88863337

Time window requested: 2026-04-01T00:00:00Z to 2026-06-21T00:00:00Z

Seed wallet count: 45

Visited wallet count: 500

## Output files

1. `nodes.csv`: all addresses observed, with tags and degree counts.
2. `edges.csv`: every relation edge with source, destination, type, amount, transaction hash, and evidence source.
3. `paths_to_uma_vote.csv`: shortest paths from Polymarket-side source wallets to UMA vote-related wallets.
4. `high_priority_leads.csv`: best path per source wallet, ranked by lead score.
5. `cluster_summary.csv`: connected components that contain source wallets or UMA vote-related wallets.
6. `shared_counterparties.csv`: wallet pairs sharing non-common counterparties.
7. `protocol_interactions.csv`: suspected UMA, resolver, Safe, or protocol interactions.
8. `raw_transfers.jsonl`: raw Alchemy transfer responses preserved line by line.
9. `raw_transactions.jsonl`: raw inspected transaction or Polygonscan records.
10. `graph.graphml`: importable graph for Gephi, Cytoscape, or network analysis tools.
11. `file_hash_manifest.csv`: hashes of local evidence files processed.

## Important interpretation limits

A path is a lead, not proof of common ownership.

A shared funder is stronger than a shared common contract, but still requires manual review.

A 3 or 4 hop path is useful for discovery, but it should not be presented as direct proof unless the intermediate wallets, timing, and transaction purpose are independently verified.

Common infrastructure contracts, CTF, UMA contracts, routers, bridges, and burn addresses are not treated as strong identity links by default.

## Recommended lawyer-safe wording

Use:

1. appears transaction-linked
2. shared funding lead
3. common counterparty lead
4. multi-hop relation requiring review
5. possible conflict-of-interest relation
6. requires ownership discovery

Avoid:

1. proves fraud
2. proves same owner
3. definitely rigged
4. all wallets are one person

