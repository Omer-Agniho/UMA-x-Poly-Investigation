Step 9B safe package

Use this instead of collect_step9B_targeted_erc1155_traces.py.

Why this version exists:
The previous script used eth_getLogs in many block chunks for each wallet and direction. That can create many failed or invalid RPC requests on Alchemy. This safer version uses alchemy_getAssetTransfers, which is indexed and should require far fewer requests.

Files:
collect_step9B_alchemy_asset_transfers.py
step9b_selected_wallets.csv

Run:
1. Put both files in the same folder.
2. Open PowerShell in that folder.
3. Set your Polygon RPC:
   $env:POLYGON_RPC_URL="YOUR_POLYGON_ALCHEMY_RPC_URL"
4. Run:
   python collect_step9B_alchemy_asset_transfers.py

Do not run the old broad eth_getLogs version.

Outputs:
step9b_outputs_asset_transfers/00_step9b_run_summary.txt
step9b_outputs_asset_transfers/01_step9b_alchemy_asset_transfers.csv
step9b_outputs_asset_transfers/02_step9b_redeem_receipt_erc1155_logs.csv
step9b_outputs_asset_transfers/03_step9b_wallet_token_flow_summary.csv
step9b_outputs_asset_transfers/04_step9b_counterparty_summary.csv
step9b_outputs_asset_transfers/05_step9b_incoming_nonzero_edges_for_review.csv
step9b_outputs_asset_transfers/98_step9b_failed_asset_transfer_queries.csv
step9b_outputs_asset_transfers/99_step9b_failed_receipts.csv

Upload the output folder files after the run.
