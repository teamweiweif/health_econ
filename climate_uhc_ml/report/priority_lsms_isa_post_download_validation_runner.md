# Priority LSMS-ISA Post-Download Validation Runner

Status: safe runner plan for post-download receipt, schema, value-profile,
and semantics checks. Default mode is dry-run. Use `--execute` only after
official raw package files are present in packet target folders.

It does not download, copy, delete, extract, write promoted `data/`, or run models.

## Summary

- Mode: dry_run
- Progress packets considered: 10
- Validation-ready packets: 0
- Plan rows: 50
- Execute command rows: 0
- Attempted commands: 0
- Failed commands: 0

## Run Plan Preview

| download_rank | idno | progress_status | target_file_count | runner_decision | command_rank | command |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | ETH_2021_ESPS-W5_v02_M | blocked_no_local_or_incoming_files | 0 | blocked_packet_not_validation_ready | 1 | python script/150_build_priority_lsms_isa_raw_package_receipt_checklist.py |
| 1 | ETH_2021_ESPS-W5_v02_M | blocked_no_local_or_incoming_files | 0 | blocked_packet_not_validation_ready | 2 | python script/153_validate_priority_lsms_isa_official_file_receipt.py |
| 1 | ETH_2021_ESPS-W5_v02_M | blocked_no_local_or_incoming_files | 0 | blocked_packet_not_validation_ready | 3 | python script/157_build_priority_lsms_isa_received_raw_schema_audit.py |
| 1 | ETH_2021_ESPS-W5_v02_M | blocked_no_local_or_incoming_files | 0 | blocked_packet_not_validation_ready | 4 | python script/158_build_priority_lsms_isa_received_raw_value_profile.py |
| 1 | ETH_2021_ESPS-W5_v02_M | blocked_no_local_or_incoming_files | 0 | blocked_packet_not_validation_ready | 5 | python script/159_build_priority_lsms_isa_received_raw_semantics_review.py |
| 2 | ETH_2018_ESS_v04_M | blocked_no_local_or_incoming_files | 0 | blocked_packet_not_validation_ready | 1 | python script/150_build_priority_lsms_isa_raw_package_receipt_checklist.py |
| 2 | ETH_2018_ESS_v04_M | blocked_no_local_or_incoming_files | 0 | blocked_packet_not_validation_ready | 2 | python script/153_validate_priority_lsms_isa_official_file_receipt.py |
| 2 | ETH_2018_ESS_v04_M | blocked_no_local_or_incoming_files | 0 | blocked_packet_not_validation_ready | 3 | python script/157_build_priority_lsms_isa_received_raw_schema_audit.py |
| 2 | ETH_2018_ESS_v04_M | blocked_no_local_or_incoming_files | 0 | blocked_packet_not_validation_ready | 4 | python script/158_build_priority_lsms_isa_received_raw_value_profile.py |
| 2 | ETH_2018_ESS_v04_M | blocked_no_local_or_incoming_files | 0 | blocked_packet_not_validation_ready | 5 | python script/159_build_priority_lsms_isa_received_raw_semantics_review.py |
| 3 | NGA_2012_GHSP-W2_v02_M | blocked_no_local_or_incoming_files | 0 | blocked_packet_not_validation_ready | 1 | python script/150_build_priority_lsms_isa_raw_package_receipt_checklist.py |
| 3 | NGA_2012_GHSP-W2_v02_M | blocked_no_local_or_incoming_files | 0 | blocked_packet_not_validation_ready | 2 | python script/153_validate_priority_lsms_isa_official_file_receipt.py |
| 3 | NGA_2012_GHSP-W2_v02_M | blocked_no_local_or_incoming_files | 0 | blocked_packet_not_validation_ready | 3 | python script/157_build_priority_lsms_isa_received_raw_schema_audit.py |
| 3 | NGA_2012_GHSP-W2_v02_M | blocked_no_local_or_incoming_files | 0 | blocked_packet_not_validation_ready | 4 | python script/158_build_priority_lsms_isa_received_raw_value_profile.py |
| 3 | NGA_2012_GHSP-W2_v02_M | blocked_no_local_or_incoming_files | 0 | blocked_packet_not_validation_ready | 5 | python script/159_build_priority_lsms_isa_received_raw_semantics_review.py |
| 4 | NGA_2015_GHSP-W3_v02_M | blocked_no_local_or_incoming_files | 0 | blocked_packet_not_validation_ready | 1 | python script/150_build_priority_lsms_isa_raw_package_receipt_checklist.py |
| 4 | NGA_2015_GHSP-W3_v02_M | blocked_no_local_or_incoming_files | 0 | blocked_packet_not_validation_ready | 2 | python script/153_validate_priority_lsms_isa_official_file_receipt.py |
| 4 | NGA_2015_GHSP-W3_v02_M | blocked_no_local_or_incoming_files | 0 | blocked_packet_not_validation_ready | 3 | python script/157_build_priority_lsms_isa_received_raw_schema_audit.py |
| 4 | NGA_2015_GHSP-W3_v02_M | blocked_no_local_or_incoming_files | 0 | blocked_packet_not_validation_ready | 4 | python script/158_build_priority_lsms_isa_received_raw_value_profile.py |
| 4 | NGA_2015_GHSP-W3_v02_M | blocked_no_local_or_incoming_files | 0 | blocked_packet_not_validation_ready | 5 | python script/159_build_priority_lsms_isa_received_raw_semantics_review.py |
| 5 | NGA_2010_GHSP-W1_v03_M | blocked_no_local_or_incoming_files | 0 | blocked_packet_not_validation_ready | 1 | python script/150_build_priority_lsms_isa_raw_package_receipt_checklist.py |
| 5 | NGA_2010_GHSP-W1_v03_M | blocked_no_local_or_incoming_files | 0 | blocked_packet_not_validation_ready | 2 | python script/153_validate_priority_lsms_isa_official_file_receipt.py |
| 5 | NGA_2010_GHSP-W1_v03_M | blocked_no_local_or_incoming_files | 0 | blocked_packet_not_validation_ready | 3 | python script/157_build_priority_lsms_isa_received_raw_schema_audit.py |
| 5 | NGA_2010_GHSP-W1_v03_M | blocked_no_local_or_incoming_files | 0 | blocked_packet_not_validation_ready | 4 | python script/158_build_priority_lsms_isa_received_raw_value_profile.py |
| 5 | NGA_2010_GHSP-W1_v03_M | blocked_no_local_or_incoming_files | 0 | blocked_packet_not_validation_ready | 5 | python script/159_build_priority_lsms_isa_received_raw_semantics_review.py |
| 6 | TZA_2008_NPS-R1_v03_M | blocked_no_local_or_incoming_files | 0 | blocked_packet_not_validation_ready | 1 | python script/150_build_priority_lsms_isa_raw_package_receipt_checklist.py |
| 6 | TZA_2008_NPS-R1_v03_M | blocked_no_local_or_incoming_files | 0 | blocked_packet_not_validation_ready | 2 | python script/153_validate_priority_lsms_isa_official_file_receipt.py |
| 6 | TZA_2008_NPS-R1_v03_M | blocked_no_local_or_incoming_files | 0 | blocked_packet_not_validation_ready | 3 | python script/157_build_priority_lsms_isa_received_raw_schema_audit.py |
| 6 | TZA_2008_NPS-R1_v03_M | blocked_no_local_or_incoming_files | 0 | blocked_packet_not_validation_ready | 4 | python script/158_build_priority_lsms_isa_received_raw_value_profile.py |
| 6 | TZA_2008_NPS-R1_v03_M | blocked_no_local_or_incoming_files | 0 | blocked_packet_not_validation_ready | 5 | python script/159_build_priority_lsms_isa_received_raw_semantics_review.py |
| ... | ... | ... | ... | ... | ... | ... |

## Outputs

- `temp/priority_lsms_isa_post_download_validation_run_plan.csv`
- `temp/priority_lsms_isa_post_download_validation_command_log.csv`
- `result/priority_lsms_isa_post_download_validation_runner_summary.csv`

## Stop Rule

The runner only handles post-download validation scripts. Data writes and
models remain blocked until promoted registry thresholds pass.
