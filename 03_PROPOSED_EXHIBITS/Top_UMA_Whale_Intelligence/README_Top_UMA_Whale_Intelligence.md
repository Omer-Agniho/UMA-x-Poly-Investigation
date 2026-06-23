# Top UMA Whale Intelligence Profiler Output

Generated at: 2026-06-23T10:20:05.945110+00:00

## Scope

Top N rows analyzed: 60
Window: 2026-04-01T00:00:00+00:00 to 2026-06-21T00:00:00+00:00

This package profiles UMA whale voters. It does not prove common ownership or wrongdoing. It identifies leads for manual transaction review.

## Key outputs

- `00_clean_top_whales.csv` cleaned Top UMA whale data.
- `01_voting_power_concentration.csv` concentration and vote-power totals.
- `02_delegate_hot_wallet_operator_matrix.csv` delegate / hot wallet reuse across stakers.
- `03_ethereum_uma_token_flows.csv` UMA token movements in the review window.
- `04_top_whale_gas_funders.csv` first incoming native gas funders in the review window.
- `05_shared_gas_funder_candidates.csv` repeated gas funders across whale wallets.
- `06_top_whale_known_target_contacts.csv` contacts with known YES wallets, UMA oracle actors, or relevant protocol contracts.
- `07_one_hop_conflict_counterparty_matches.csv` direct one-hop matches between Top UMA whale wallets and known YES / oracle actor addresses.
- `08_top_whale_conflict_abnormality_matrix.csv` scored review matrix. Scores are leads, not conclusions.
- `09_top_whale_timeline_correlation.csv` vote reveal times plus known target contacts.
- `10_local_repo_mentions_of_tracked_addresses.csv` repository files mentioning tracked addresses.
- `raw_asset_transfers_flat.csv` normalized transfer rows.
- `raw_asset_transfers.jsonl` raw Alchemy transfer responses.
- `99_output_file_hash_manifest.csv` SHA-256 hashes for generated files.

## Interpretation rules

Use direct, non-spam, non-generic wallet transfers as higher-priority leads.
Treat spam token transfers, exchange / bridge / router activity, zero-value native calls, and protocol-contract-only paths as weak until manually verified.
A shared gas funder is a lead, not proof of common control.
