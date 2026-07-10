# Priority LSMS-ISA Manual Download Execution Board

Status: one-table execution board for the remaining minimum-threshold
manual downloads. It converts packet URLs, target folders, missing-file
counts, core-file previews, and post-download commands into one checklist.

It does not download, copy, delete, extract, write promoted `data/`, or run models.

## Summary

- Board rows: 10
- Priority-country rows: 9
- Sixth-country rows: 1
- Validation-ready rows: 0
- Target-folder files now present: 0
- Incoming route rows now present: 0
- Missing full-file rows: 838
- Missing core-file rows: 323
- Countries if the board passes: 6
- Country-waves if the board passes: 11

## Execution Board

| download_rank | country | wave | idno | progress_status | target_file_count | expected_missing_file_rows | core_missing_file_rows | official_get_microdata_url | local_target_folder |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | Ethiopia | 2021-2022 | ETH_2021_ESPS-W5_v02_M | blocked_no_local_or_incoming_files | 0 | 68 | 36 | https://microdata.worldbank.org/catalog/6161/get-microdata | temp/raw_downloads/ETH_2021_ESPS-W5_v02_M/ |
| 2 | Ethiopia | 2018-2019 | ETH_2018_ESS_v04_M | blocked_no_local_or_incoming_files | 0 | 68 | 35 | https://microdata.worldbank.org/catalog/3823/get-microdata | temp/raw_downloads/ETH_2018_ESS_v04_M/ |
| 3 | Nigeria | 2012-2013 | NGA_2012_GHSP-W2_v02_M | blocked_no_local_or_incoming_files | 0 | 103 | 26 | https://microdata.worldbank.org/catalog/1952/get-microdata | temp/raw_downloads/NGA_2012_GHSP-W2_v02_M/ |
| 4 | Nigeria | 2015-2016 | NGA_2015_GHSP-W3_v02_M | blocked_no_local_or_incoming_files | 0 | 104 | 26 | https://microdata.worldbank.org/catalog/2734/get-microdata | temp/raw_downloads/NGA_2015_GHSP-W3_v02_M/ |
| 5 | Nigeria | 2010-2011 | NGA_2010_GHSP-W1_v03_M | blocked_no_local_or_incoming_files | 0 | 99 | 27 | https://microdata.worldbank.org/catalog/1002/get-microdata | temp/raw_downloads/NGA_2010_GHSP-W1_v03_M/ |
| 6 | Tanzania | 2008-2009 | TZA_2008_NPS-R1_v03_M | blocked_no_local_or_incoming_files | 0 | 61 | 35 | https://microdata.worldbank.org/catalog/76/get-microdata | temp/raw_downloads/TZA_2008_NPS-R1_v03_M/ |
| 7 | Tanzania | 2010-2011 | TZA_2010_NPS-R2_v03_M | blocked_no_local_or_incoming_files | 0 | 95 | 38 | https://microdata.worldbank.org/catalog/1050/get-microdata | temp/raw_downloads/TZA_2010_NPS-R2_v03_M/ |
| 8 | Tanzania | 2012-2013 | TZA_2012_NPS-R3_v01_M | blocked_no_local_or_incoming_files | 0 | 80 | 33 | https://microdata.worldbank.org/catalog/2252/get-microdata | temp/raw_downloads/TZA_2012_NPS-R3_v01_M/ |
| 9 | Uganda | 2019-2020 | UGA_2019_UNPS_v03_M | blocked_no_local_or_incoming_files | 0 | 109 | 39 | https://microdata.worldbank.org/catalog/3902/get-microdata | temp/raw_downloads/UGA_2019_UNPS_v03_M/ |
| 10 | Nepal | 2010-2011 | NPL_2010_LSS-III_v01_M | blocked_no_local_or_incoming_files | 0 | 51 | 28 | https://microdata.worldbank.org/catalog/1000/get-microdata | temp/raw_downloads/NPL_2010_LSS-III_v01_M/ |

## After Files Are Placed

1. Run `python script/177_build_priority_lsms_isa_manual_download_progress_tracker.py`.
2. Run `python script/178_build_priority_lsms_isa_post_download_validation_runner.py` first as a dry run.
3. If the plan marks a packet ready, run `python script/178_build_priority_lsms_isa_post_download_validation_runner.py --execute`.
4. Refresh the promotion gates only after receipt, schema, value-profile, and semantics checks pass.

## Outputs

- `temp/priority_lsms_isa_manual_download_execution_board.csv`
- `result/priority_lsms_isa_manual_download_execution_board_summary.csv`

## Stop Rule

This board is an acquisition-control artifact. Each country-wave still needs
complete official-file receipt, raw-value verification, outcome/timing/
geography checks, and accepted CHIRPS or ERA5 climate linkage before any
`data/` write or model rerun.
