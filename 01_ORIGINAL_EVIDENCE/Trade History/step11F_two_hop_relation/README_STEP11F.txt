# Step 11F focused two-hop relation screen

This package checks whether priority UMA YES voter/delegate addresses and priority Polymarket YES buyer/redeemer/token-path wallets touch the same Polygon intermediary/counterparty.

Run from PowerShell:

```powershell
$env:POLYGON_RPC_URL="YOUR_POLYGON_ALCHEMY_RPC_URL"
python collect_step11F_two_hop_relations.py
```

Optional safe test:

```powershell
$env:MAX_UMA="25"
$env:MAX_POLY="25"
python collect_step11F_two_hop_relations.py
```

Full run after test:

```powershell
Remove-Item Env:MAX_UMA
Remove-Item Env:MAX_POLY
python collect_step11F_two_hop_relations.py
```

Outputs will be in `step11F_outputs`.

Review first:

1. `00_step11F_run_summary.txt`
2. `05_priority_two_hop_leads.csv`
3. `04_two_hop_pair_edges.csv`
4. `03_common_counterparty_summary.csv`
5. `98_step11F_failed_queries.csv`

Legal caution:
A two-hop shared counterparty is only an investigative lead. Do not describe it as proof of common ownership or coordination unless further facts support it. Exchange, bridge, router, relayer, aggregator, public contract, and high-volume counterparties are weak leads.
