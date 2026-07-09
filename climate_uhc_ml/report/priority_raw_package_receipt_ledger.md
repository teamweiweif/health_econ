# Priority Raw Package Receipt Ledger

Status: fail-closed raw-package receipt layer. Generated placeholder and
handoff files are ignored as original package evidence.

## Summary

| Metric | Value | Interpretation |
|---|---:|---|
| priority_raw_receipt_dataset_rows | 13 | Priority and backup waves represented in the receipt ledger. |
| priority_raw_receipt_original_file_rows | 0 | Original package/documentation files counted after ignoring generated handoff files. |
| priority_raw_receipt_archive_files | 0 | Original archive packages present in priority target folders. |
| priority_raw_receipt_raw_tabular_files | 0 | Original raw tabular files present in priority target folders. |
| priority_raw_receipt_documentation_files | 0 | Original documentation files present in priority target folders. |
| priority_raw_receipt_total_original_bytes | 0 | Total bytes of original files counted in priority target folders. |
| priority_raw_receipt_priority_targets | 156 | Priority target file/module rows checked for receipt coverage. |
| priority_raw_receipt_priority_targets_covered | 0 | Priority targets covered by direct files or archive members. |
| priority_raw_receipt_priority_targets_missing | 156 | Priority targets still missing from direct/archive receipt coverage. |
| priority_raw_receipt_missing_target_rows | 156 | Missing target rows written for reviewer follow-up. |
| priority_raw_receipt_generated_files_ignored | 208 | Generated handoff/placeholder files ignored as original package evidence. |
| priority_raw_receipt_complete_package_candidates | 0 | Datasets with original raw/package receipt and all priority targets covered. |
| priority_raw_receipt_partial_package_candidates | 0 | Datasets with some original raw/package receipt but remaining receipt or documentation gaps. |
| priority_raw_receipt_missing_package_rows | 13 | Datasets with no original raw package/tabular receipt yet. |
| modeling_gate_status | blocked | Models remain blocked until promoted registry thresholds and accepted CHIRPS/ERA5 linkage pass. |
| priority_raw_receipt_status_not_received_no_original_raw_package | 13 | Receipt status count. |

## Dataset Receipt Status

| acquisition_batch_rank | idno | country | wave | original_file_count | archive_file_count | raw_tabular_file_count | priority_targets_covered_direct_or_archive | priority_targets_missing | receipt_status |
|---|---|---|---|---|---|---|---|---|---|
| 1 | ETH_2021_ESPS-W5_v02_M | Ethiopia | 2021-2022 | 0 | 0 | 0 | 0 | 12 | not_received_no_original_raw_package |
| 2 | ETH_2018_ESS_v04_M | Ethiopia | 2018-2019 | 0 | 0 | 0 | 0 | 12 | not_received_no_original_raw_package |
| 3 | MWI_2007-2009_MTM_v01_M | Malawi | 2007-2009 | 0 | 0 | 0 | 0 | 12 | not_received_no_original_raw_package |
| 4 | NGA_2012_GHSP-W2_v02_M | Nigeria | 2012-2013 | 0 | 0 | 0 | 0 | 12 | not_received_no_original_raw_package |
| 5 | NGA_2015_GHSP-W3_v02_M | Nigeria | 2015-2016 | 0 | 0 | 0 | 0 | 12 | not_received_no_original_raw_package |
| 6 | NGA_2010_GHSP-W1_v03_M | Nigeria | 2010-2011 | 0 | 0 | 0 | 0 | 12 | not_received_no_original_raw_package |
| 7 | TZA_2008_NPS-R1_v03_M | Tanzania | 2008-2009 | 0 | 0 | 0 | 0 | 12 | not_received_no_original_raw_package |
| 8 | TZA_2010_NPS-R2_v03_M | Tanzania | 2010-2011 | 0 | 0 | 0 | 0 | 12 | not_received_no_original_raw_package |
| 9 | TZA_2012_NPS-R3_v01_M | Tanzania | 2012-2013 | 0 | 0 | 0 | 0 | 12 | not_received_no_original_raw_package |
| 10 | UGA_2014_SAGE-EL_v01_M | Uganda | 2014 | 0 | 0 | 0 | 0 | 12 | not_received_no_original_raw_package |
| 11 | JAM_1997_SLC_v01_M | Jamaica | 1997 | 0 | 0 | 0 | 0 | 12 | not_received_no_original_raw_package |
| 12 | KGZ_1993_KMPS_v01_M | Kyrgyz Republic | 1993 | 0 | 0 | 0 | 0 | 12 | not_received_no_original_raw_package |
| 13 | NPL_2010_LSS-III_v01_M | Nepal | 2010-2011 | 0 | 0 | 0 | 0 | 12 | not_received_no_original_raw_package |

## Rule

Receipt is not promotion. A dataset can move toward promotion only after the
unchanged official raw package and documentation are present, priority target
coverage is checked through direct files or archive members, and downstream
manual value, unit, recall-period, missing-code, merge-key, weight, timing,
geography, and CHIRPS/ERA5 linkage gates pass.

## Machine-Readable Outputs

- `temp/priority_raw_package_receipt_ledger.csv`
- `temp/priority_raw_package_file_manifest.csv`
- `temp/priority_raw_package_missing_targets.csv`
- `result/priority_raw_package_receipt_summary.csv`
