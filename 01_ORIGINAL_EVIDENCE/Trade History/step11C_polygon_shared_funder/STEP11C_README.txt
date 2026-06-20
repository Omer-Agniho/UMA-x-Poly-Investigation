Step 11C Polygon Shared Funder Package

Purpose:
This package checks whether the same Polygon source wallet sent native/ERC20 transfers to both UMA addresses and high-priority Polymarket/Step9B wallets.

Why priority wallets only:
The full Step 9B universe contains thousands of counterparty leads. Running shared funder analysis against all of them would create too much noise and unnecessary RPC use. This package checks priority 1 and priority 2 Polymarket wallets first.

Files:
01_uma_address_universe.csv
05_step11B_priority_polymarket_wallets.csv
collect_step11C_polygon_shared_funders.py

How to run in PowerShell:
$env:POLYGON_RPC_URL="YOUR_POLYGON_ALCHEMY_RPC_URL"
python collect_step11C_polygon_shared_funders.py

Optional:
To include priority 3 wallets later, run:
$env:STEP11C_MAX_POLYMARKET_PRIORITY="3"
python collect_step11C_polygon_shared_funders.py

Do not start with priority 3 unless we decide it is necessary.

Outputs:
step11C_outputs/00_step11C_run_summary.txt
step11C_outputs/01_uma_incoming_polygon_transfers.csv
step11C_outputs/02_polymarket_incoming_polygon_transfers.csv
step11C_outputs/03_common_funder_matches.csv
step11C_outputs/04_common_funder_pair_edges.csv
step11C_outputs/05_common_funder_summary_by_funder.csv
step11C_outputs/06_priority_common_funder_leads.csv
step11C_outputs/98_step11C_failed_queries.csv

Most important output:
06_priority_common_funder_leads.csv

Legal limitation:
A common funder is an investigative lead only. It does not prove common control or identity. Exchange, bridge, relayer, aggregator, and contract wallets must be treated carefully.
