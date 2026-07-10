# Priority LSMS-ISA Raw Package Intake Packet

Status: refocused LSMS/ISA manual-download intake gate. This packet tells where
each complete official raw package should be placed, scans the target folders,
and separates generated handoff files from actual original raw/documentation
receipt evidence.

## Summary

| Metric | Value | Interpretation |
|---|---:|---|
| priority_lsms_raw_intake_dataset_rows | 19 | Refocused LSMS/ISA acquisition targets with raw-package intake ledger rows. |
| priority_lsms_raw_intake_file_manifest_rows | 779 | Files found under target folders, including generated handoffs and original candidates. |
| priority_lsms_raw_intake_generated_handoff_files | 474 | Generated markdown handoffs ignored as raw receipt evidence. |
| priority_lsms_raw_intake_original_file_rows | 305 | Non-generated candidate original files found in refocused target folders. |
| priority_lsms_raw_intake_archive_file_rows | 1 | Archive/compressed package candidates found. |
| priority_lsms_raw_intake_raw_tabular_file_rows | 299 | Raw tabular/workbook candidates found. |
| priority_lsms_raw_intake_documentation_file_rows | 5 | Documentation candidates found. |
| priority_lsms_raw_intake_missing_package_rows | 15 | Targets with no original package or documentation files yet. |
| priority_lsms_raw_intake_acceptance_requirement_rows | 152 | Requirement rows carried into raw-package acceptance matrix. |
| priority_lsms_raw_intake_blocked_requirement_rows | 128 | Requirement rows blocked because no original package is present. |
| priority_lsms_raw_intake_handoff_readmes_written | 19 | Per-target raw-package intake handoff files written. |
| priority_lsms_raw_intake_data_write_status | blocked_no_promoted_rows | No country-wave may write to data/ from this intake packet. |
| modeling_gate_status | blocked | Models remain blocked until raw-backed promotion thresholds and accepted climate linkage pass. |
| priority_lsms_raw_intake_queue_role_core_replacement_primary | 2 | Raw-package intake row count by refocused queue role. |
| priority_lsms_raw_intake_queue_role_core_selected_lsms_isa_aligned | 8 | Raw-package intake row count by refocused queue role. |
| priority_lsms_raw_intake_queue_role_replacement_backup_wave | 6 | Raw-package intake row count by refocused queue role. |
| priority_lsms_raw_intake_queue_role_sixth_country_backup_candidate | 3 | Raw-package intake row count by refocused queue role. |
| priority_lsms_raw_intake_status_blocked_missing_documentation | 1 | Raw-package intake acceptance status count. |
| priority_lsms_raw_intake_status_blocked_no_original_package | 15 | Raw-package intake acceptance status count. |
| priority_lsms_raw_intake_status_ready_for_schema_and_manual_value_review | 3 | Raw-package intake acceptance status count. |

## Current Intake Queue

| download_priority_order | queue_role | country | wave | idno | original_file_count | archive_file_count | raw_tabular_file_count | documentation_file_count | intake_acceptance_status |
|---|---|---|---|---|---|---|---|---|---|
| 1 | core_selected_lsms_isa_aligned | Ethiopia | 2021-2022 | ETH_2021_ESPS-W5_v02_M | 0 | 0 | 0 | 0 | blocked_no_original_package |
| 2 | core_selected_lsms_isa_aligned | Ethiopia | 2018-2019 | ETH_2018_ESS_v04_M | 0 | 0 | 0 | 0 | blocked_no_original_package |
| 3 | core_replacement_primary | Malawi | 2004-2005 | MWI_2004_IHS-II_v01_M | 1 | 1 | 0 | 0 | blocked_missing_documentation |
| 4 | core_selected_lsms_isa_aligned | Nigeria | 2012-2013 | NGA_2012_GHSP-W2_v02_M | 0 | 0 | 0 | 0 | blocked_no_original_package |
| 5 | core_selected_lsms_isa_aligned | Nigeria | 2015-2016 | NGA_2015_GHSP-W3_v02_M | 117 | 0 | 115 | 2 | ready_for_schema_and_manual_value_review |
| 6 | core_selected_lsms_isa_aligned | Nigeria | 2010-2011 | NGA_2010_GHSP-W1_v03_M | 0 | 0 | 0 | 0 | blocked_no_original_package |
| 7 | core_selected_lsms_isa_aligned | Tanzania | 2008-2009 | TZA_2008_NPS-R1_v03_M | 0 | 0 | 0 | 0 | blocked_no_original_package |
| 8 | core_selected_lsms_isa_aligned | Tanzania | 2010-2011 | TZA_2010_NPS-R2_v03_M | 100 | 0 | 99 | 1 | ready_for_schema_and_manual_value_review |
| 9 | core_selected_lsms_isa_aligned | Tanzania | 2012-2013 | TZA_2012_NPS-R3_v01_M | 87 | 0 | 85 | 2 | ready_for_schema_and_manual_value_review |
| 10 | core_replacement_primary | Uganda | 2019-2020 | UGA_2019_UNPS_v03_M | 0 | 0 | 0 | 0 | blocked_no_original_package |
| 11 | sixth_country_backup_candidate | Jamaica | 1997 | JAM_1997_SLC_v01_M | 0 | 0 | 0 | 0 | blocked_no_original_package |
| 12 | sixth_country_backup_candidate | Kyrgyz Republic | 1993 | KGZ_1993_KMPS_v01_M | 0 | 0 | 0 | 0 | blocked_no_original_package |
| 13 | sixth_country_backup_candidate | Nepal | 2010-2011 | NPL_2010_LSS-III_v01_M | 0 | 0 | 0 | 0 | blocked_no_original_package |
| 14 | replacement_backup_wave | Malawi | 2019-2020 | MWI_2019_IHS-V_v06_M | 0 | 0 | 0 | 0 | blocked_no_original_package |
| 15 | replacement_backup_wave | Malawi | 2016-2017 | MWI_2016_IHS-IV_v04_M | 0 | 0 | 0 | 0 | blocked_no_original_package |
| 16 | replacement_backup_wave | Malawi | 2010-2011 | MWI_2010_IHS-III_v01_M | 0 | 0 | 0 | 0 | blocked_no_original_package |
| 17 | replacement_backup_wave | Uganda | 2011-2012 | UGA_2011_UNPS_v02_M | 0 | 0 | 0 | 0 | blocked_no_original_package |
| 18 | replacement_backup_wave | Uganda | 2018-2019 | UGA_2018_UNPS_v02_M | 0 | 0 | 0 | 0 | blocked_no_original_package |
| 19 | replacement_backup_wave | Uganda | 2015-2016 | UGA_2015_UNPS_v02_M | 0 | 0 | 0 | 0 | blocked_no_original_package |

## Blocked Targets

| download_priority_order | country | idno | local_target_folder | intake_acceptance_status | next_action |
|---|---|---|---|---|---|
| 1 | Ethiopia | ETH_2021_ESPS-W5_v02_M | temp/raw_downloads/ETH_2021_ESPS-W5_v02_M/ | blocked_no_original_package | Place the complete unchanged official raw package and all documentation in the target folder. |
| 2 | Ethiopia | ETH_2018_ESS_v04_M | temp/raw_downloads/ETH_2018_ESS_v04_M/ | blocked_no_original_package | Place the complete unchanged official raw package and all documentation in the target folder. |
| 3 | Malawi | MWI_2004_IHS-II_v01_M | temp/raw_downloads/MWI_2004_IHS-II_v01_M/ | blocked_missing_documentation | Add questionnaires, codebooks, basic information documents, and data dictionaries before schema/value review. |
| 4 | Nigeria | NGA_2012_GHSP-W2_v02_M | temp/raw_downloads/NGA_2012_GHSP-W2_v02_M/ | blocked_no_original_package | Place the complete unchanged official raw package and all documentation in the target folder. |
| 6 | Nigeria | NGA_2010_GHSP-W1_v03_M | temp/raw_downloads/NGA_2010_GHSP-W1_v03_M/ | blocked_no_original_package | Place the complete unchanged official raw package and all documentation in the target folder. |
| 7 | Tanzania | TZA_2008_NPS-R1_v03_M | temp/raw_downloads/TZA_2008_NPS-R1_v03_M/ | blocked_no_original_package | Place the complete unchanged official raw package and all documentation in the target folder. |
| 10 | Uganda | UGA_2019_UNPS_v03_M | temp/raw_downloads/UGA_2019_UNPS_v03_M/ | blocked_no_original_package | Place the complete unchanged official raw package and all documentation in the target folder. |
| 11 | Jamaica | JAM_1997_SLC_v01_M | temp/raw_downloads/JAM_1997_SLC_v01_M/ | blocked_no_original_package | Place the complete unchanged official raw package and all documentation in the target folder. |
| 12 | Kyrgyz Republic | KGZ_1993_KMPS_v01_M | temp/raw_downloads/KGZ_1993_KMPS_v01_M/ | blocked_no_original_package | Place the complete unchanged official raw package and all documentation in the target folder. |
| 13 | Nepal | NPL_2010_LSS-III_v01_M | temp/raw_downloads/NPL_2010_LSS-III_v01_M/ | blocked_no_original_package | Place the complete unchanged official raw package and all documentation in the target folder. |
| 14 | Malawi | MWI_2019_IHS-V_v06_M | temp/raw_downloads/MWI_2019_IHS-V_v06_M/ | blocked_no_original_package | Place the complete unchanged official raw package and all documentation in the target folder. |
| 15 | Malawi | MWI_2016_IHS-IV_v04_M | temp/raw_downloads/MWI_2016_IHS-IV_v04_M/ | blocked_no_original_package | Place the complete unchanged official raw package and all documentation in the target folder. |
| 16 | Malawi | MWI_2010_IHS-III_v01_M | temp/raw_downloads/MWI_2010_IHS-III_v01_M/ | blocked_no_original_package | Place the complete unchanged official raw package and all documentation in the target folder. |
| 17 | Uganda | UGA_2011_UNPS_v02_M | temp/raw_downloads/UGA_2011_UNPS_v02_M/ | blocked_no_original_package | Place the complete unchanged official raw package and all documentation in the target folder. |
| 18 | Uganda | UGA_2018_UNPS_v02_M | temp/raw_downloads/UGA_2018_UNPS_v02_M/ | blocked_no_original_package | Place the complete unchanged official raw package and all documentation in the target folder. |
| 19 | Uganda | UGA_2015_UNPS_v02_M | temp/raw_downloads/UGA_2015_UNPS_v02_M/ | blocked_no_original_package | Place the complete unchanged official raw package and all documentation in the target folder. |

## File Manifest Status

Generated handoff files are useful instructions but do not count as raw receipt.
Current file manifest rows: 779.

## Machine-Readable Outputs

- `temp/priority_lsms_isa_raw_package_intake_ledger.csv`
- `temp/priority_lsms_isa_raw_package_file_manifest.csv`
- `temp/priority_lsms_isa_raw_package_acceptance_matrix.csv`
- `result/priority_lsms_isa_raw_package_intake_summary.csv`

## Guardrail

This intake packet does not download restricted microdata, does not bypass
credentialed World Bank access, and does not write any promoted data. `data/`
remains closed until all raw, outcome, and climate-linkage gates pass.
