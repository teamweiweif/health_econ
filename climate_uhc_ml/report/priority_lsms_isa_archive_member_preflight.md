# Priority LSMS-ISA Archive Member Preflight

Status: archive/direct-file preflight for the refocused LSMS/ISA raw package
targets. This script does not extract, convert, or promote data; it only checks
whether direct original files or readable archive members exist.

## Summary

| Metric | Value | Interpretation |
|---|---:|---|
| priority_lsms_archive_preflight_dataset_rows | 19 | Refocused LSMS/ISA targets checked by archive/direct-file preflight. |
| priority_lsms_archive_preflight_direct_file_rows | 972 | Direct non-generated original candidate files found under target folders. |
| priority_lsms_archive_preflight_direct_archive_rows | 1 | Direct archive/compressed package candidates found. |
| priority_lsms_archive_preflight_direct_raw_tabular_rows | 956 | Direct raw tabular/workbook candidates found. |
| priority_lsms_archive_preflight_direct_documentation_rows | 15 | Direct documentation candidates found. |
| priority_lsms_archive_preflight_public_documentation_snapshot_rows | 133 | Saved official public documentation snapshots accepted as documentation evidence. |
| priority_lsms_archive_preflight_archive_member_rows | 52 | Readable archive member rows found without extraction. |
| priority_lsms_archive_preflight_archive_raw_tabular_member_rows | 52 | Raw tabular-like archive members found. |
| priority_lsms_archive_preflight_archive_documentation_member_rows | 0 | Documentation-like archive members found. |
| priority_lsms_archive_preflight_ready_dataset_rows | 10 | Targets ready for schema and manual raw review. |
| priority_lsms_archive_preflight_blocked_dataset_rows | 9 | Targets still blocked before schema/manual raw review. |
| priority_lsms_archive_preflight_requirement_rows | 152 | Requirement rows covered by archive/direct-file preflight. |
| priority_lsms_archive_preflight_blocked_requirement_rows | 72 | Requirement rows blocked because no archive/direct raw evidence is available. |
| priority_lsms_archive_preflight_handoff_readmes_written | 19 | Per-target archive preflight handoff files written. |
| priority_lsms_archive_preflight_data_write_status | blocked_no_promoted_rows | No country-wave may write to data/ from archive preflight alone. |
| modeling_gate_status | blocked | Models remain blocked until raw-backed promotion thresholds and accepted climate linkage pass. |
| priority_lsms_archive_preflight_queue_role_core_replacement_primary | 2 | Archive preflight target count by refocused queue role. |
| priority_lsms_archive_preflight_queue_role_core_selected_lsms_isa_aligned | 8 | Archive preflight target count by refocused queue role. |
| priority_lsms_archive_preflight_queue_role_replacement_backup_wave | 6 | Archive preflight target count by refocused queue role. |
| priority_lsms_archive_preflight_queue_role_sixth_country_backup_candidate | 3 | Archive preflight target count by refocused queue role. |
| priority_lsms_archive_preflight_status_blocked_no_original_archive_or_direct_files | 9 | Archive preflight dataset status count. |
| priority_lsms_archive_preflight_status_ready_for_raw_receipt_schema_and_manual_review | 10 | Archive preflight dataset status count. |

## Dataset Preflight

| download_priority_order | queue_role | country | wave | idno | direct_archive_file_rows | archive_member_rows | public_documentation_snapshot_rows | archive_preflight_status |
|---|---|---|---|---|---|---|---|---|
| 1 | core_selected_lsms_isa_aligned | Ethiopia | 2021-2022 | ETH_2021_ESPS-W5_v02_M | 0 | 0 | 7 | blocked_no_original_archive_or_direct_files |
| 2 | core_selected_lsms_isa_aligned | Ethiopia | 2018-2019 | ETH_2018_ESS_v04_M | 0 | 0 | 7 | blocked_no_original_archive_or_direct_files |
| 3 | core_replacement_primary | Malawi | 2004-2005 | MWI_2004_IHS-II_v01_M | 1 | 52 | 7 | ready_for_raw_receipt_schema_and_manual_review |
| 4 | core_selected_lsms_isa_aligned | Nigeria | 2012-2013 | NGA_2012_GHSP-W2_v02_M | 0 | 0 | 7 | ready_for_raw_receipt_schema_and_manual_review |
| 5 | core_selected_lsms_isa_aligned | Nigeria | 2015-2016 | NGA_2015_GHSP-W3_v02_M | 0 | 0 | 7 | ready_for_raw_receipt_schema_and_manual_review |
| 6 | core_selected_lsms_isa_aligned | Nigeria | 2010-2011 | NGA_2010_GHSP-W1_v03_M | 0 | 0 | 7 | ready_for_raw_receipt_schema_and_manual_review |
| 7 | core_selected_lsms_isa_aligned | Tanzania | 2008-2009 | TZA_2008_NPS-R1_v03_M | 0 | 0 | 7 | ready_for_raw_receipt_schema_and_manual_review |
| 8 | core_selected_lsms_isa_aligned | Tanzania | 2010-2011 | TZA_2010_NPS-R2_v03_M | 0 | 0 | 7 | ready_for_raw_receipt_schema_and_manual_review |
| 9 | core_selected_lsms_isa_aligned | Tanzania | 2012-2013 | TZA_2012_NPS-R3_v01_M | 0 | 0 | 7 | ready_for_raw_receipt_schema_and_manual_review |
| 10 | core_replacement_primary | Uganda | 2019-2020 | UGA_2019_UNPS_v03_M | 0 | 0 | 7 | blocked_no_original_archive_or_direct_files |
| 11 | sixth_country_backup_candidate | Jamaica | 1997 | JAM_1997_SLC_v01_M | 0 | 0 | 7 | blocked_no_original_archive_or_direct_files |
| 12 | sixth_country_backup_candidate | Kyrgyz Republic | 1993 | KGZ_1993_KMPS_v01_M | 0 | 0 | 7 | blocked_no_original_archive_or_direct_files |
| 13 | sixth_country_backup_candidate | Nepal | 2010-2011 | NPL_2010_LSS-III_v01_M | 0 | 0 | 7 | blocked_no_original_archive_or_direct_files |
| 14 | replacement_backup_wave | Malawi | 2019-2020 | MWI_2019_IHS-V_v06_M | 0 | 0 | 7 | blocked_no_original_archive_or_direct_files |
| 15 | replacement_backup_wave | Malawi | 2016-2017 | MWI_2016_IHS-IV_v04_M | 0 | 0 | 7 | ready_for_raw_receipt_schema_and_manual_review |
| 16 | replacement_backup_wave | Malawi | 2010-2011 | MWI_2010_IHS-III_v01_M | 0 | 0 | 7 | ready_for_raw_receipt_schema_and_manual_review |
| 17 | replacement_backup_wave | Uganda | 2011-2012 | UGA_2011_UNPS_v02_M | 0 | 0 | 7 | ready_for_raw_receipt_schema_and_manual_review |
| 18 | replacement_backup_wave | Uganda | 2018-2019 | UGA_2018_UNPS_v02_M | 0 | 0 | 7 | blocked_no_original_archive_or_direct_files |
| 19 | replacement_backup_wave | Uganda | 2015-2016 | UGA_2015_UNPS_v02_M | 0 | 0 | 7 | blocked_no_original_archive_or_direct_files |

## Blocked Targets

| download_priority_order | country | idno | local_target_folder | archive_preflight_status | next_action |
|---|---|---|---|---|---|
| 1 | Ethiopia | ETH_2021_ESPS-W5_v02_M | temp/raw_downloads/ETH_2021_ESPS-W5_v02_M/ | blocked_no_original_archive_or_direct_files | Place the complete official archive/raw package and documentation in the target folder. |
| 2 | Ethiopia | ETH_2018_ESS_v04_M | temp/raw_downloads/ETH_2018_ESS_v04_M/ | blocked_no_original_archive_or_direct_files | Place the complete official archive/raw package and documentation in the target folder. |
| 10 | Uganda | UGA_2019_UNPS_v03_M | temp/raw_downloads/UGA_2019_UNPS_v03_M/ | blocked_no_original_archive_or_direct_files | Place the complete official archive/raw package and documentation in the target folder. |
| 11 | Jamaica | JAM_1997_SLC_v01_M | temp/raw_downloads/JAM_1997_SLC_v01_M/ | blocked_no_original_archive_or_direct_files | Place the complete official archive/raw package and documentation in the target folder. |
| 12 | Kyrgyz Republic | KGZ_1993_KMPS_v01_M | temp/raw_downloads/KGZ_1993_KMPS_v01_M/ | blocked_no_original_archive_or_direct_files | Place the complete official archive/raw package and documentation in the target folder. |
| 13 | Nepal | NPL_2010_LSS-III_v01_M | temp/raw_downloads/NPL_2010_LSS-III_v01_M/ | blocked_no_original_archive_or_direct_files | Place the complete official archive/raw package and documentation in the target folder. |
| 14 | Malawi | MWI_2019_IHS-V_v06_M | temp/raw_downloads/MWI_2019_IHS-V_v06_M/ | blocked_no_original_archive_or_direct_files | Place the complete official archive/raw package and documentation in the target folder. |
| 18 | Uganda | UGA_2018_UNPS_v02_M | temp/raw_downloads/UGA_2018_UNPS_v02_M/ | blocked_no_original_archive_or_direct_files | Place the complete official archive/raw package and documentation in the target folder. |
| 19 | Uganda | UGA_2015_UNPS_v02_M | temp/raw_downloads/UGA_2015_UNPS_v02_M/ | blocked_no_original_archive_or_direct_files | Place the complete official archive/raw package and documentation in the target folder. |

## Direct File Preview

| download_priority_order | idno | file_name | file_role | direct_file_acceptance_status |
|---|---|---|---|---|
| 3 | MWI_2004_IHS-II_v01_M | MWI_2004_IHS-II_v01_M_Stata8.zip | official_archive_or_compressed_package_candidate | direct_file_present_pending_schema_or_documentation_review |
| 4 | NGA_2012_GHSP-W2_v02_M | AGHS_Panel_PP_Household.pdf | documentation_candidate | direct_file_present_pending_schema_or_documentation_review |
| 4 | NGA_2012_GHSP-W2_v02_M | anthroN.dta | raw_tabular_or_workbook_candidate | direct_file_present_pending_schema_or_documentation_review |
| 4 | NGA_2012_GHSP-W2_v02_M | aux2.dta | raw_tabular_or_workbook_candidate | direct_file_present_pending_schema_or_documentation_review |
| 4 | NGA_2012_GHSP-W2_v02_M | aux3.dta | raw_tabular_or_workbook_candidate | direct_file_present_pending_schema_or_documentation_review |
| 4 | NGA_2012_GHSP-W2_v02_M | aux4.dta | raw_tabular_or_workbook_candidate | direct_file_present_pending_schema_or_documentation_review |
| 4 | NGA_2012_GHSP-W2_v02_M | auxround_1.dta | raw_tabular_or_workbook_candidate | direct_file_present_pending_schema_or_documentation_review |
| 4 | NGA_2012_GHSP-W2_v02_M | auxyear_1.dta | raw_tabular_or_workbook_candidate | direct_file_present_pending_schema_or_documentation_review |
| 4 | NGA_2012_GHSP-W2_v02_M | AW2_PH_HH_Questionnaire.pdf | documentation_candidate | direct_file_present_pending_schema_or_documentation_review |
| 4 | NGA_2012_GHSP-W2_v02_M | cons_agg_w2.dta | raw_tabular_or_workbook_candidate | direct_file_present_pending_schema_or_documentation_review |
| 4 | NGA_2012_GHSP-W2_v02_M | secta10_harvestw2.dta | raw_tabular_or_workbook_candidate | direct_file_present_pending_schema_or_documentation_review |
| 4 | NGA_2012_GHSP-W2_v02_M | secta1_harvestw2.dta | raw_tabular_or_workbook_candidate | direct_file_present_pending_schema_or_documentation_review |
| 4 | NGA_2012_GHSP-W2_v02_M | secta2_harvestw2.dta | raw_tabular_or_workbook_candidate | direct_file_present_pending_schema_or_documentation_review |
| 4 | NGA_2012_GHSP-W2_v02_M | secta3_harvestw2.dta | raw_tabular_or_workbook_candidate | direct_file_present_pending_schema_or_documentation_review |
| 4 | NGA_2012_GHSP-W2_v02_M | secta41_harvestw2.dta | raw_tabular_or_workbook_candidate | direct_file_present_pending_schema_or_documentation_review |
| 4 | NGA_2012_GHSP-W2_v02_M | secta42_harvestw2.dta | raw_tabular_or_workbook_candidate | direct_file_present_pending_schema_or_documentation_review |
| 4 | NGA_2012_GHSP-W2_v02_M | secta5a_harvestw2.dta | raw_tabular_or_workbook_candidate | direct_file_present_pending_schema_or_documentation_review |
| 4 | NGA_2012_GHSP-W2_v02_M | secta5b_harvestw2.dta | raw_tabular_or_workbook_candidate | direct_file_present_pending_schema_or_documentation_review |
| 4 | NGA_2012_GHSP-W2_v02_M | secta6_harvestw2.dta | raw_tabular_or_workbook_candidate | direct_file_present_pending_schema_or_documentation_review |
| 4 | NGA_2012_GHSP-W2_v02_M | secta7_harvestw2.dta | raw_tabular_or_workbook_candidate | direct_file_present_pending_schema_or_documentation_review |

## Archive Member Preview

| download_priority_order | idno | archive_file_name | member_name | member_role | member_acceptance_status |
|---|---|---|---|---|---|
| 3 | MWI_2004_IHS-II_v01_M | MWI_2004_IHS-II_v01_M_Stata8.zip | sec_aa.dta | raw_tabular_candidate | archive_member_candidate_pending_schema_or_documentation_review |
| 3 | MWI_2004_IHS-II_v01_M | MWI_2004_IHS-II_v01_M_Stata8.zip | sec_ab.dta | raw_tabular_candidate | archive_member_candidate_pending_schema_or_documentation_review |
| 3 | MWI_2004_IHS-II_v01_M | MWI_2004_IHS-II_v01_M_Stata8.zip | sec_ac.dta | raw_tabular_candidate | archive_member_candidate_pending_schema_or_documentation_review |
| 3 | MWI_2004_IHS-II_v01_M | MWI_2004_IHS-II_v01_M_Stata8.zip | sec_ad.dta | raw_tabular_candidate | archive_member_candidate_pending_schema_or_documentation_review |
| 3 | MWI_2004_IHS-II_v01_M | MWI_2004_IHS-II_v01_M_Stata8.zip | sec_b.dta | raw_tabular_candidate | archive_member_candidate_pending_schema_or_documentation_review |
| 3 | MWI_2004_IHS-II_v01_M | MWI_2004_IHS-II_v01_M_Stata8.zip | sec_c.dta | raw_tabular_candidate | archive_member_candidate_pending_schema_or_documentation_review |
| 3 | MWI_2004_IHS-II_v01_M | MWI_2004_IHS-II_v01_M_Stata8.zip | sec_d.dta | raw_tabular_candidate | archive_member_candidate_pending_schema_or_documentation_review |
| 3 | MWI_2004_IHS-II_v01_M | MWI_2004_IHS-II_v01_M_Stata8.zip | sec_e.dta | raw_tabular_candidate | archive_member_candidate_pending_schema_or_documentation_review |
| 3 | MWI_2004_IHS-II_v01_M | MWI_2004_IHS-II_v01_M_Stata8.zip | sec_f.dta | raw_tabular_candidate | archive_member_candidate_pending_schema_or_documentation_review |
| 3 | MWI_2004_IHS-II_v01_M | MWI_2004_IHS-II_v01_M_Stata8.zip | sec_g.dta | raw_tabular_candidate | archive_member_candidate_pending_schema_or_documentation_review |
| 3 | MWI_2004_IHS-II_v01_M | MWI_2004_IHS-II_v01_M_Stata8.zip | sec_h.dta | raw_tabular_candidate | archive_member_candidate_pending_schema_or_documentation_review |
| 3 | MWI_2004_IHS-II_v01_M | MWI_2004_IHS-II_v01_M_Stata8.zip | sec_i.dta | raw_tabular_candidate | archive_member_candidate_pending_schema_or_documentation_review |
| 3 | MWI_2004_IHS-II_v01_M | MWI_2004_IHS-II_v01_M_Stata8.zip | sec_j1.dta | raw_tabular_candidate | archive_member_candidate_pending_schema_or_documentation_review |
| 3 | MWI_2004_IHS-II_v01_M | MWI_2004_IHS-II_v01_M_Stata8.zip | sec_j2.dta | raw_tabular_candidate | archive_member_candidate_pending_schema_or_documentation_review |
| 3 | MWI_2004_IHS-II_v01_M | MWI_2004_IHS-II_v01_M_Stata8.zip | sec_k.dta | raw_tabular_candidate | archive_member_candidate_pending_schema_or_documentation_review |
| 3 | MWI_2004_IHS-II_v01_M | MWI_2004_IHS-II_v01_M_Stata8.zip | sec_l.dta | raw_tabular_candidate | archive_member_candidate_pending_schema_or_documentation_review |
| 3 | MWI_2004_IHS-II_v01_M | MWI_2004_IHS-II_v01_M_Stata8.zip | sec_m1.dta | raw_tabular_candidate | archive_member_candidate_pending_schema_or_documentation_review |
| 3 | MWI_2004_IHS-II_v01_M | MWI_2004_IHS-II_v01_M_Stata8.zip | sec_m2.dta | raw_tabular_candidate | archive_member_candidate_pending_schema_or_documentation_review |
| 3 | MWI_2004_IHS-II_v01_M | MWI_2004_IHS-II_v01_M_Stata8.zip | sec_n.dta | raw_tabular_candidate | archive_member_candidate_pending_schema_or_documentation_review |
| 3 | MWI_2004_IHS-II_v01_M | MWI_2004_IHS-II_v01_M_Stata8.zip | sec_o.dta | raw_tabular_candidate | archive_member_candidate_pending_schema_or_documentation_review |

## Machine-Readable Outputs

- `temp/priority_lsms_isa_archive_member_preflight.csv`
- `temp/priority_lsms_isa_archive_member_manifest.csv`
- `temp/priority_lsms_isa_direct_file_preflight.csv`
- `temp/priority_lsms_isa_archive_requirement_preflight.csv`
- `result/priority_lsms_isa_archive_member_preflight_summary.csv`

## Guardrail

Readable archive members, direct raw files, and saved official public
documentation snapshots are only preflight evidence. A wave still cannot enter
`data/` until raw schema inspection, manual value/unit/key review, outcome
readiness, and accepted CHIRPS/ERA5 linkage all pass.
