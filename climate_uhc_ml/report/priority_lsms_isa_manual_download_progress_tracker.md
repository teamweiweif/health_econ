# Priority LSMS-ISA Manual Download Progress Tracker

Status: local progress tracker for the 10 remaining minimum-batch manual
download packets. It scans packet target folders and incoming-route rows.

It does not download, copy, delete, extract, promote, write `data/`, or run models.

## Summary

- Packets tracked: 10
- Packets with target files ready for validation: 0
- Packets still blocked with no local or incoming files: 10
- Incoming copy candidates: 0
- Target-folder non-generated files: 0

## Packet Progress

| download_rank | country | wave | idno | progress_status | target_file_count | incoming_route_rows | packet_report_path |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | Ethiopia | 2021-2022 | ETH_2021_ESPS-W5_v02_M | blocked_no_local_or_incoming_files | 0 | 0 | report/priority_lsms_isa_manual_download_packets/ETH_2021_ESPS-W5_v02_M.md |
| 2 | Ethiopia | 2018-2019 | ETH_2018_ESS_v04_M | blocked_no_local_or_incoming_files | 0 | 0 | report/priority_lsms_isa_manual_download_packets/ETH_2018_ESS_v04_M.md |
| 3 | Nigeria | 2012-2013 | NGA_2012_GHSP-W2_v02_M | blocked_no_local_or_incoming_files | 0 | 0 | report/priority_lsms_isa_manual_download_packets/NGA_2012_GHSP-W2_v02_M.md |
| 4 | Nigeria | 2015-2016 | NGA_2015_GHSP-W3_v02_M | blocked_no_local_or_incoming_files | 0 | 0 | report/priority_lsms_isa_manual_download_packets/NGA_2015_GHSP-W3_v02_M.md |
| 5 | Nigeria | 2010-2011 | NGA_2010_GHSP-W1_v03_M | blocked_no_local_or_incoming_files | 0 | 0 | report/priority_lsms_isa_manual_download_packets/NGA_2010_GHSP-W1_v03_M.md |
| 6 | Tanzania | 2008-2009 | TZA_2008_NPS-R1_v03_M | blocked_no_local_or_incoming_files | 0 | 0 | report/priority_lsms_isa_manual_download_packets/TZA_2008_NPS-R1_v03_M.md |
| 7 | Tanzania | 2010-2011 | TZA_2010_NPS-R2_v03_M | blocked_no_local_or_incoming_files | 0 | 0 | report/priority_lsms_isa_manual_download_packets/TZA_2010_NPS-R2_v03_M.md |
| 8 | Tanzania | 2012-2013 | TZA_2012_NPS-R3_v01_M | blocked_no_local_or_incoming_files | 0 | 0 | report/priority_lsms_isa_manual_download_packets/TZA_2012_NPS-R3_v01_M.md |
| 9 | Uganda | 2019-2020 | UGA_2019_UNPS_v03_M | blocked_no_local_or_incoming_files | 0 | 0 | report/priority_lsms_isa_manual_download_packets/UGA_2019_UNPS_v03_M.md |
| 10 | Nepal | 2010-2011 | NPL_2010_LSS-III_v01_M | blocked_no_local_or_incoming_files | 0 | 0 | report/priority_lsms_isa_manual_download_packets/NPL_2010_LSS-III_v01_M.md |

## Outputs

- `temp/priority_lsms_isa_manual_download_progress_tracker.csv`
- `result/priority_lsms_isa_manual_download_progress_summary.csv`

## Stop Rule

This tracker only reports local acquisition progress. Each country-wave still
needs complete official-file receipt, raw-value verification, outcome/timing/
geography checks, and accepted climate linkage before any `data/` write.
