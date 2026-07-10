# Priority LSMS/ISA Target Folder Receipt Smoke Test

Status: non-destructive target-folder audit for the 10 minimum-batch manual downloads.

This smoke test scans each `temp/raw_downloads/<IDNO>/` target folder from the
manual execution board and separates generated instructions from candidate raw
data packages, candidate documentation, and unknown files. It also performs a
filename/member-name match against the official expected-file matrix where
possible. It does not move, delete, extract, promote, or write `data/` files.

## Summary

| metric | value | interpretation |
| --- | --- | --- |
| priority_lsms_target_smoke_dataset_rows | 10 | Manual-download packet target folders audited by the receipt smoke test. |
| priority_lsms_target_smoke_target_folders_present | 10 | Target folders currently present under temp/raw_downloads. |
| priority_lsms_target_smoke_file_inventory_rows | 312 | Files found under the target folders, including generated instructions. |
| priority_lsms_target_smoke_placeholder_instruction_rows | 312 | Generated readmes or instruction files that do not count as raw receipt. |
| priority_lsms_target_smoke_candidate_raw_file_rows | 0 | Non-placeholder files with raw data or archive extensions. |
| priority_lsms_target_smoke_candidate_documentation_file_rows | 0 | Non-placeholder files with documentation extensions. |
| priority_lsms_target_smoke_ready_for_receipt_validation_rows | 0 | Target folders with candidate raw files matching expected/core filenames. |
| priority_lsms_target_smoke_blocked_no_candidate_raw_rows | 10 | Target folders that still contain no candidate raw or documentation files. |
| priority_lsms_target_smoke_documentation_only_rows | 0 | Target folders with documentation but no candidate raw files. |
| priority_lsms_target_smoke_manual_review_rows | 0 | Target folders with candidate raw files that need manual identity review before receipt... |
| priority_lsms_target_smoke_expected_name_match_rows | 0 | Target folders with at least one expected filename match. |
| priority_lsms_target_smoke_core_name_match_rows | 0 | Target folders with at least one core expected filename match. |
| priority_lsms_target_smoke_data_write_status | blocked_no_data_write | Receipt smoke testing never writes promoted data. |
| modeling_gate_status | blocked | No predictive, reduced-form, causal ML, or policy learning until registry thresholds pass. |

## Target Folder Status

| download_rank | idno | target_file_rows | candidate_raw_file_rows | candidate_documentation_file_rows | expected_file_name_matches | expected_core_file_name_matches | receipt_smoke_status |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | ETH_2021_ESPS-W5_v02_M | 33 | 0 | 0 | 0 | 0 | blocked_no_candidate_raw_or_documentation_files |
| 2 | ETH_2018_ESS_v04_M | 33 | 0 | 0 | 0 | 0 | blocked_no_candidate_raw_or_documentation_files |
| 3 | NGA_2012_GHSP-W2_v02_M | 33 | 0 | 0 | 0 | 0 | blocked_no_candidate_raw_or_documentation_files |
| 4 | NGA_2015_GHSP-W3_v02_M | 33 | 0 | 0 | 0 | 0 | blocked_no_candidate_raw_or_documentation_files |
| 5 | NGA_2010_GHSP-W1_v03_M | 33 | 0 | 0 | 0 | 0 | blocked_no_candidate_raw_or_documentation_files |
| 6 | TZA_2008_NPS-R1_v03_M | 33 | 0 | 0 | 0 | 0 | blocked_no_candidate_raw_or_documentation_files |
| 7 | TZA_2010_NPS-R2_v03_M | 33 | 0 | 0 | 0 | 0 | blocked_no_candidate_raw_or_documentation_files |
| 8 | TZA_2012_NPS-R3_v01_M | 33 | 0 | 0 | 0 | 0 | blocked_no_candidate_raw_or_documentation_files |
| 9 | UGA_2019_UNPS_v03_M | 15 | 0 | 0 | 0 | 0 | blocked_no_candidate_raw_or_documentation_files |
| 10 | NPL_2010_LSS-III_v01_M | 33 | 0 | 0 | 0 | 0 | blocked_no_candidate_raw_or_documentation_files |

## Candidate File Preview

_No rows._

## Stop Rule

If `candidate_raw_file_rows` is zero, the country-wave remains blocked at raw
receipt. If candidate raw files are present but no expected filenames match,
manual identity review is required before running the receipt/schema/value
audit chain. Passing this smoke test is not analysis readiness; it only starts
official receipt validation.
