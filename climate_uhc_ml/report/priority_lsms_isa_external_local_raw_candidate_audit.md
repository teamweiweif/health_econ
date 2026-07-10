# Priority LSMS/ISA External Local Raw Candidate Audit

Status: filesystem-only audit of local raw-data candidates found outside the `climate_uhc_ml` workspace.

This audit checks whether an existing local health-expenditure data folder contains filenames matching the expected World Bank LSMS/ISA files for the refocused queue. It does not read raw data contents, copy raw files, accept provenance, write `data/`, or open modeling.

## Summary

| metric | value | interpretation |
| --- | --- | --- |
| external_local_raw_candidate_queue_rows | 19 | Refocused LSMS/ISA queue rows audited against the external local raw candidate root. |
| external_local_raw_candidate_root_exists | 1 | Whether the external health-expenditure raw-data root exists on this machine. |
| external_local_raw_candidate_folder_exists_rows | 10 | Queue rows with a mapped external local folder. |
| external_local_raw_candidate_expected_match_rows | 814 | Expected official file-name rows matched by external local candidates. |
| external_local_raw_candidate_core_match_rows | 280 | Requirement-linked core file-name rows matched by external local candidates. |
| external_local_raw_candidate_locked_target_rows | 13 | Rows selected in the current refocused plan. |
| external_local_raw_candidate_locked_target_with_matches_rows | 7 | Selected rows with external local expected-file matches. |
| external_local_raw_candidate_locked_core_complete_rows | 4 | Selected rows whose requirement-linked core file names are complete in the external local candidate folder. |
| external_local_raw_candidate_backup_with_matches_rows | 3 | Backup rows with external local expected-file matches. |
| external_local_raw_candidate_provenance_accepted_rows | 0 | External local candidates are not accepted as official receipt until provenance and unchanged package status are revi... |
| data_write_gate_status | blocked_no_data_write | The audit does not copy raw files or write promoted data. |
| modeling_gate_status | blocked | No predictive, reduced-form, causal ML, or policy learning is opened. |

## Candidate Rows

| download_priority_order | country | wave | idno | current_plan_status | external_candidate_folder_exists | external_file_rows | expected_file_rows | external_expected_file_match_rows | core_file_rows | external_core_file_match_rows | candidate_receipt_status |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | Ethiopia | 2021-2022 | ETH_2021_ESPS-W5_v02_M | selected_in_refocused_plan | 0 | 0 | 68 | 0 | 36 | 0 | no_external_candidate_folder |
| 2 | Ethiopia | 2018-2019 | ETH_2018_ESS_v04_M | selected_in_refocused_plan | 0 | 0 | 68 | 0 | 35 | 0 | no_external_candidate_folder |
| 3 | Malawi | 2004-2005 | MWI_2004_IHS-II_v01_M | selected_in_refocused_plan | 1 | 58 | 52 | 52 | 37 | 37 | external_candidate_core_file_names_complete_pending_provenance |
| 4 | Nigeria | 2012-2013 | NGA_2012_GHSP-W2_v02_M | selected_in_refocused_plan | 1 | 122 | 103 | 100 | 26 | 20 | external_candidate_partial_core_file_name_matches_pending_provenance |
| 5 | Nigeria | 2015-2016 | NGA_2015_GHSP-W3_v02_M | selected_in_refocused_plan | 1 | 117 | 104 | 104 | 26 | 26 | external_candidate_core_file_names_complete_pending_provenance |
| 6 | Nigeria | 2010-2011 | NGA_2010_GHSP-W1_v03_M | selected_in_refocused_plan | 1 | 111 | 99 | 97 | 27 | 21 | external_candidate_partial_core_file_name_matches_pending_provenance |
| 7 | Tanzania | 2008-2009 | TZA_2008_NPS-R1_v03_M | selected_in_refocused_plan | 1 | 67 | 61 | 2 | 35 | 4 | external_candidate_partial_core_file_name_matches_pending_provenance |
| 8 | Tanzania | 2010-2011 | TZA_2010_NPS-R2_v03_M | selected_in_refocused_plan | 1 | 100 | 95 | 94 | 38 | 38 | external_candidate_core_file_names_complete_pending_provenance |
| 9 | Tanzania | 2012-2013 | TZA_2012_NPS-R3_v01_M | selected_in_refocused_plan | 1 | 87 | 80 | 80 | 33 | 33 | external_candidate_core_file_names_complete_pending_provenance |
| 10 | Uganda | 2019-2020 | UGA_2019_UNPS_v03_M | selected_in_refocused_plan | 0 | 0 | 109 | 0 | 39 | 0 | no_external_candidate_folder |
| 11 | Jamaica | 1997 | JAM_1997_SLC_v01_M | selected_in_refocused_plan | 0 | 0 | 68 | 0 | 32 | 0 | no_external_candidate_folder |
| 12 | Kyrgyz Republic | 1993 | KGZ_1993_KMPS_v01_M | selected_in_refocused_plan | 0 | 0 | 15 | 0 | 31 | 0 | no_external_candidate_folder |
| 13 | Nepal | 2010-2011 | NPL_2010_LSS-III_v01_M | selected_in_refocused_plan | 0 | 0 | 51 | 0 | 28 | 0 | no_external_candidate_folder |
| 14 | Malawi | 2019-2020 | MWI_2019_IHS-V_v06_M | backup_not_selected_in_refocused_13_wave_plan | 0 | 0 | 108 | 0 | 35 | 0 | no_external_candidate_folder |
| 15 | Malawi | 2016-2017 | MWI_2016_IHS-IV_v04_M | backup_not_selected_in_refocused_13_wave_plan | 1 | 105 | 99 | 99 | 35 | 35 | external_candidate_core_file_names_complete_pending_provenance |
| 16 | Malawi | 2010-2011 | MWI_2010_IHS-III_v01_M | backup_not_selected_in_refocused_13_wave_plan | 1 | 157 | 85 | 85 | 36 | 36 | external_candidate_core_file_names_complete_pending_provenance |
| 17 | Uganda | 2011-2012 | UGA_2011_UNPS_v02_M | backup_not_selected_in_refocused_13_wave_plan | 1 | 105 | 103 | 101 | 32 | 30 | external_candidate_partial_core_file_name_matches_pending_provenance |
| 18 | Uganda | 2018-2019 | UGA_2018_UNPS_v02_M | backup_not_selected_in_refocused_13_wave_plan | 0 | 0 | 109 | 0 | 34 | 0 | no_external_candidate_folder |
| 19 | Uganda | 2015-2016 | UGA_2015_UNPS_v02_M | backup_not_selected_in_refocused_13_wave_plan | 0 | 0 | 120 | 0 | 34 | 0 | no_external_candidate_folder |

## Stop Rule

External local matches are only acquisition leads. They cannot be treated as official raw package receipt until provenance, completeness, unchanged-file status, schema, value, semantics, timing/geography, and climate-linkage gates pass.
