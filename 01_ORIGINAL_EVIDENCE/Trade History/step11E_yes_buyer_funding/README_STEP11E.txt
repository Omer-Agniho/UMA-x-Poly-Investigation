Step 11E YES Buyer Funding Analysis

Goal:
Check funding sources for wallets that bought YES shares, including wallets that did not redeem.

Files:
- collect_step11E_yes_buyer_funding.py
- 01_uma_address_universe.csv
- 02_step11E_yes_buyer_wallets.csv
- 03_step11E_yes_buy_transactions.csv
- 00_step11E_input_summary.txt

Run from PowerShell in this folder:
$env:POLYGON_RPC_URL="YOUR_POLYGON_ALCHEMY_RPC_URL"
python collect_step11E_yes_buyer_funding.py

Default behavior:
The script checks priority 1 and priority 2 YES buyers first.
This includes all target-market YES buyers and higher-notional future-only YES buyers.

Optional settings:
$env:MAX_PRIORITY="1"  # smaller first run
$env:MAX_PRIORITY="4"  # all relevant YES buyers, more API usage
$env:MAX_WALLETS="50"  # cap number of buyer wallets for a test run
$env:START_BLOCK="88500000"
$env:END_BLOCK="88753129"

Upload these outputs after running:
step11E_outputs/00_step11E_run_summary.txt
step11E_outputs/03_direct_uma_to_yes_buyer_funding_edges.csv
step11E_outputs/04_common_funder_matches.csv
step11E_outputs/05_common_funder_pair_edges.csv
step11E_outputs/06_priority_yes_buyer_funding_leads.csv
step11E_outputs/98_step11E_failed_queries.csv

Legal caution:
A direct or shared funder is transaction evidence only. It does not prove common ownership or control by itself.
Exchange, bridge, relayer, aggregator, public contract, or high-volume funding sources must be treated as weak leads unless supported by additional evidence.
