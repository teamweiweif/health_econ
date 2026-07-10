# Priority LSMS-ISA Official File Receipt Validator

Status: fail-closed official file receipt validation for the refocused
LSMS/ISA dataset-promotion campaign. This validator compares local direct files
and readable archive members against the official World Bank DDI file names.
It also records constrained same-basename format aliases when a DDI entry such
as `.NSDstat` corresponds to a real package member such as `.dta`. It does not
download, extract, convert, or promote data.

## Summary

| Metric | Value | Interpretation |
|---|---:|---|
| priority_lsms_official_file_receipt_dataset_rows | 19 | Refocused LSMS/ISA datasets checked against the official DDI file universe. |
| priority_lsms_official_file_receipt_expected_file_rows | 1597 | Official DDI file rows expected after complete package receipt. |
| priority_lsms_official_file_receipt_expected_file_matched_rows | 814 | Expected official files matched by direct files or archive members. |
| priority_lsms_official_file_receipt_expected_file_alias_matched_rows | 814 | Expected files matched through a constrained same-basename DDI format alias, most commonly NSDstat to Stata. |
| priority_lsms_official_file_receipt_expected_file_missing_rows | 783 | Official DDI file rows still not found locally. |
| priority_lsms_official_file_receipt_core_file_rows | 629 | Core requirement/file rows that must be present before raw-value review. |
| priority_lsms_official_file_receipt_core_file_matched_rows | 280 | Core expected files matched locally. |
| priority_lsms_official_file_receipt_core_file_alias_matched_rows | 280 | Core files matched through a constrained same-basename DDI format alias. |
| priority_lsms_official_file_receipt_core_file_missing_rows | 349 | Core expected files still missing locally. |
| priority_lsms_official_file_receipt_core_complete_dataset_rows | 6 | Datasets whose expected core files all match local package evidence. |
| priority_lsms_official_file_receipt_complete_dataset_rows | 5 | Datasets with all expected official file rows matched, pending schema and value checks. |
| priority_lsms_official_file_receipt_original_or_member_rows | 1024 | Non-generated direct original files plus archive member rows indexed. |
| priority_lsms_official_file_receipt_generated_handoff_rows | 483 | Generated handoff files ignored as raw receipt evidence. |
| priority_lsms_official_file_receipt_handoff_readmes_written | 19 | Per-wave official file receipt validator handoffs written. |
| priority_lsms_official_file_receipt_data_write_status | blocked_no_promoted_rows | Official file receipt alone never writes promoted data. |
| modeling_gate_status | blocked | Models remain blocked until raw value, climate linkage, and promoted-registry thresholds pass. |
| priority_lsms_official_file_receipt_queue_role_core_replacement_primary | 2 | Official file receipt validator row count by refocused queue role. |
| priority_lsms_official_file_receipt_queue_role_core_selected_lsms_isa_aligned | 8 | Official file receipt validator row count by refocused queue role. |
| priority_lsms_official_file_receipt_queue_role_replacement_backup_wave | 6 | Official file receipt validator row count by refocused queue role. |
| priority_lsms_official_file_receipt_queue_role_sixth_country_backup_candidate | 3 | Official file receipt validator row count by refocused queue role. |
| priority_lsms_official_file_receipt_status_blocked_core_official_files_missing | 4 | Official file receipt dataset status count. |
| priority_lsms_official_file_receipt_status_blocked_no_original_package | 9 | Official file receipt dataset status count. |
| priority_lsms_official_file_receipt_status_core_files_present_full_official_package_incomplete | 1 | Official file receipt dataset status count. |
| priority_lsms_official_file_receipt_status_official_file_receipt_complete_pending_schema_value_review | 5 | Official file receipt dataset status count. |

## Dataset Receipt Status

| download_priority_order | queue_role | country | wave | idno | official_expected_matched_rows | official_expected_file_rows | official_core_matched_rows | official_core_file_rows | official_file_receipt_status |
|---|---|---|---|---|---|---|---|---|---|
| 1 | core_selected_lsms_isa_aligned | Ethiopia | 2021-2022 | ETH_2021_ESPS-W5_v02_M | 0 | 68 | 0 | 36 | blocked_no_original_package |
| 2 | core_selected_lsms_isa_aligned | Ethiopia | 2018-2019 | ETH_2018_ESS_v04_M | 0 | 68 | 0 | 35 | blocked_no_original_package |
| 3 | core_replacement_primary | Malawi | 2004-2005 | MWI_2004_IHS-II_v01_M | 52 | 52 | 37 | 37 | official_file_receipt_complete_pending_schema_value_review |
| 4 | core_selected_lsms_isa_aligned | Nigeria | 2012-2013 | NGA_2012_GHSP-W2_v02_M | 100 | 103 | 20 | 26 | blocked_core_official_files_missing |
| 5 | core_selected_lsms_isa_aligned | Nigeria | 2015-2016 | NGA_2015_GHSP-W3_v02_M | 104 | 104 | 26 | 26 | official_file_receipt_complete_pending_schema_value_review |
| 6 | core_selected_lsms_isa_aligned | Nigeria | 2010-2011 | NGA_2010_GHSP-W1_v03_M | 97 | 99 | 21 | 27 | blocked_core_official_files_missing |
| 7 | core_selected_lsms_isa_aligned | Tanzania | 2008-2009 | TZA_2008_NPS-R1_v03_M | 2 | 61 | 4 | 35 | blocked_core_official_files_missing |
| 8 | core_selected_lsms_isa_aligned | Tanzania | 2010-2011 | TZA_2010_NPS-R2_v03_M | 94 | 95 | 38 | 38 | core_files_present_full_official_package_incomplete |
| 9 | core_selected_lsms_isa_aligned | Tanzania | 2012-2013 | TZA_2012_NPS-R3_v01_M | 80 | 80 | 33 | 33 | official_file_receipt_complete_pending_schema_value_review |
| 10 | core_replacement_primary | Uganda | 2019-2020 | UGA_2019_UNPS_v03_M | 0 | 109 | 0 | 39 | blocked_no_original_package |
| 11 | sixth_country_backup_candidate | Jamaica | 1997 | JAM_1997_SLC_v01_M | 0 | 68 | 0 | 32 | blocked_no_original_package |
| 12 | sixth_country_backup_candidate | Kyrgyz Republic | 1993 | KGZ_1993_KMPS_v01_M | 0 | 15 | 0 | 31 | blocked_no_original_package |
| 13 | sixth_country_backup_candidate | Nepal | 2010-2011 | NPL_2010_LSS-III_v01_M | 0 | 51 | 0 | 28 | blocked_no_original_package |
| 14 | replacement_backup_wave | Malawi | 2019-2020 | MWI_2019_IHS-V_v06_M | 0 | 108 | 0 | 35 | blocked_no_original_package |
| 15 | replacement_backup_wave | Malawi | 2016-2017 | MWI_2016_IHS-IV_v04_M | 99 | 99 | 35 | 35 | official_file_receipt_complete_pending_schema_value_review |
| 16 | replacement_backup_wave | Malawi | 2010-2011 | MWI_2010_IHS-III_v01_M | 85 | 85 | 36 | 36 | official_file_receipt_complete_pending_schema_value_review |
| 17 | replacement_backup_wave | Uganda | 2011-2012 | UGA_2011_UNPS_v02_M | 101 | 103 | 30 | 32 | blocked_core_official_files_missing |
| 18 | replacement_backup_wave | Uganda | 2018-2019 | UGA_2018_UNPS_v02_M | 0 | 109 | 0 | 34 | blocked_no_original_package |
| 19 | replacement_backup_wave | Uganda | 2015-2016 | UGA_2015_UNPS_v02_M | 0 | 120 | 0 | 34 | blocked_no_original_package |

## Blocked Targets

| download_priority_order | country | idno | local_target_folder | official_file_receipt_status | next_action |
|---|---|---|---|---|---|
| 1 | Ethiopia | ETH_2021_ESPS-W5_v02_M | temp/raw_downloads/ETH_2021_ESPS-W5_v02_M/ | blocked_no_original_package | Place the complete unchanged official raw package and documentation in the target folder. |
| 2 | Ethiopia | ETH_2018_ESS_v04_M | temp/raw_downloads/ETH_2018_ESS_v04_M/ | blocked_no_original_package | Place the complete unchanged official raw package and documentation in the target folder. |
| 4 | Nigeria | NGA_2012_GHSP-W2_v02_M | temp/raw_downloads/NGA_2012_GHSP-W2_v02_M/ | blocked_core_official_files_missing | Download the complete package or locate missing core files before raw-value verification. |
| 6 | Nigeria | NGA_2010_GHSP-W1_v03_M | temp/raw_downloads/NGA_2010_GHSP-W1_v03_M/ | blocked_core_official_files_missing | Download the complete package or locate missing core files before raw-value verification. |
| 7 | Tanzania | TZA_2008_NPS-R1_v03_M | temp/raw_downloads/TZA_2008_NPS-R1_v03_M/ | blocked_core_official_files_missing | Download the complete package or locate missing core files before raw-value verification. |
| 8 | Tanzania | TZA_2010_NPS-R2_v03_M | temp/raw_downloads/TZA_2010_NPS-R2_v03_M/ | core_files_present_full_official_package_incomplete | Core files are present, but the full official file receipt is incomplete; review before promotion. |
| 10 | Uganda | UGA_2019_UNPS_v03_M | temp/raw_downloads/UGA_2019_UNPS_v03_M/ | blocked_no_original_package | Place the complete unchanged official raw package and documentation in the target folder. |
| 11 | Jamaica | JAM_1997_SLC_v01_M | temp/raw_downloads/JAM_1997_SLC_v01_M/ | blocked_no_original_package | Place the complete unchanged official raw package and documentation in the target folder. |
| 12 | Kyrgyz Republic | KGZ_1993_KMPS_v01_M | temp/raw_downloads/KGZ_1993_KMPS_v01_M/ | blocked_no_original_package | Place the complete unchanged official raw package and documentation in the target folder. |
| 13 | Nepal | NPL_2010_LSS-III_v01_M | temp/raw_downloads/NPL_2010_LSS-III_v01_M/ | blocked_no_original_package | Place the complete unchanged official raw package and documentation in the target folder. |
| 14 | Malawi | MWI_2019_IHS-V_v06_M | temp/raw_downloads/MWI_2019_IHS-V_v06_M/ | blocked_no_original_package | Place the complete unchanged official raw package and documentation in the target folder. |
| 17 | Uganda | UGA_2011_UNPS_v02_M | temp/raw_downloads/UGA_2011_UNPS_v02_M/ | blocked_core_official_files_missing | Download the complete package or locate missing core files before raw-value verification. |
| 18 | Uganda | UGA_2018_UNPS_v02_M | temp/raw_downloads/UGA_2018_UNPS_v02_M/ | blocked_no_original_package | Place the complete unchanged official raw package and documentation in the target folder. |
| 19 | Uganda | UGA_2015_UNPS_v02_M | temp/raw_downloads/UGA_2015_UNPS_v02_M/ | blocked_no_original_package | Place the complete unchanged official raw package and documentation in the target folder. |

## Missing Core Files

| download_priority_order | idno | requirement | expected_file_name | top_variable_names | official_core_file_match_status |
|---|---|---|---|---|---|
| 1 | ETH_2021_ESPS-W5_v02_M | climate_geography | sect_cover_hh_w5.dta | saq19__Latitude;saq19__Longitude | missing_expected_core_file |
| 1 | ETH_2021_ESPS-W5_v02_M | climate_geography | sect10a_com_w5.dta | cs10q05__Latitude;cs10q05__Longitude | missing_expected_core_file |
| 1 | ETH_2021_ESPS-W5_v02_M | climate_geography | sect_cover_pp_w5.dta | saq19__Latitude;saq19__Longitude | missing_expected_core_file |
| 1 | ETH_2021_ESPS-W5_v02_M | climate_geography | sect_cover_ph_w5.dta | saq19__Latitude;saq19__Longitude | missing_expected_core_file |
| 1 | ETH_2021_ESPS-W5_v02_M | climate_geography | sect_cover_ls_w5.dta | saq19__Latitude;saq19__Longitude | missing_expected_core_file |
| 1 | ETH_2021_ESPS-W5_v02_M | climate_geography | sect3_pp_w5.dta | s3q09__Latitude;s3q09__Longitude | missing_expected_core_file |
| 1 | ETH_2021_ESPS-W5_v02_M | consumption_or_income | cons_agg_w5.dta | nonfood_cons2;nom_nonfoodcons_aeq;nonfood_cons_ann;food_cons2;food_cons_ann;nom_foodcons_aeq;fafh_cons_ann;spat_totco... | missing_expected_core_file |
| 1 | ETH_2021_ESPS-W5_v02_M | health_need_and_access | sect3_hh_w5.dta | s3q14;s3q15;s3q05;s3q17;s3q13;s3q18 | missing_expected_core_file |
| 1 | ETH_2021_ESPS-W5_v02_M | health_need_and_access | sect04_com_w5.dta | cs4q37;cs4q34;cs4q35;cs4q28 | missing_expected_core_file |
| 1 | ETH_2021_ESPS-W5_v02_M | health_need_and_access | sect3_pp_w5.dta | s3q15_1;s3q15_2 | missing_expected_core_file |
| 1 | ETH_2021_ESPS-W5_v02_M | household_person_keys | sect1_hh_w5.dta | individual_id;household_id | missing_expected_core_file |
| 1 | ETH_2021_ESPS-W5_v02_M | household_person_keys | sect12b1_hh_w5.dta | household_id | missing_expected_core_file |
| 1 | ETH_2021_ESPS-W5_v02_M | household_person_keys | sect1_pp_w5.dta | household_id | missing_expected_core_file |
| 1 | ETH_2021_ESPS-W5_v02_M | household_person_keys | sect1_ph_w5.dta | household_id | missing_expected_core_file |
| 1 | ETH_2021_ESPS-W5_v02_M | household_person_keys | sect2_pp_w5.dta | household_id | missing_expected_core_file |
| 1 | ETH_2021_ESPS-W5_v02_M | household_person_keys | sect3_pp_w5.dta | household_id | missing_expected_core_file |
| 1 | ETH_2021_ESPS-W5_v02_M | household_person_keys | sect4_pp_w5.dta | household_id | missing_expected_core_file |
| 1 | ETH_2021_ESPS-W5_v02_M | household_person_keys | sect6c_hh_w5.dta | individual_id | missing_expected_core_file |
| 1 | ETH_2021_ESPS-W5_v02_M | oop_health_expenditure | sect8_3_ls_w5.dta | ls_s8_3q04;ls_s8_3q22;ls_s8_3q24;ls_s8_3q03;ls_s8_3q05;ls_s8_3q06;ls_s8_3q10a;ls_s8_3q10b;ls_s8_3q11;ls_s8_3q12_1 | missing_expected_core_file |
| 1 | ETH_2021_ESPS-W5_v02_M | oop_health_expenditure | sect3_hh_w5.dta | s3q17;s3q18 | missing_expected_core_file |
| 1 | ETH_2021_ESPS-W5_v02_M | survey_timing | sect_cover_pp_w5.dta | InterviewDate | missing_expected_core_file |
| 1 | ETH_2021_ESPS-W5_v02_M | survey_timing | sect_cover_ph_w5.dta | InterviewDate | missing_expected_core_file |
| 1 | ETH_2021_ESPS-W5_v02_M | survey_timing | sect_cover_ls_w5.dta | InterviewDate | missing_expected_core_file |
| 1 | ETH_2021_ESPS-W5_v02_M | survey_timing | sect12b1_hh_w5.dta | s12bq08a;s12bq08b | missing_expected_core_file |
| 1 | ETH_2021_ESPS-W5_v02_M | survey_timing | sect7b_hh_w5.dta | item_cd_12months;s7q04 | missing_expected_core_file |
| 1 | ETH_2021_ESPS-W5_v02_M | survey_timing | eth_householdgeovariables_y5.dta | wetQ_avgstart | missing_expected_core_file |
| 1 | ETH_2021_ESPS-W5_v02_M | survey_timing | sect_cover_hh_w5.dta | saq19__Timestamp | missing_expected_core_file |
| 1 | ETH_2021_ESPS-W5_v02_M | survey_timing | eth_plotgeovariables_y5.dta | wetQ_avgstart | missing_expected_core_file |
| 1 | ETH_2021_ESPS-W5_v02_M | weights_and_design | sect_cover_hh_w5.dta | pw_w5;ea_id | missing_expected_core_file |
| 1 | ETH_2021_ESPS-W5_v02_M | weights_and_design | sect6b2_hh_w5.dta | pw_w5 | missing_expected_core_file |
| 1 | ETH_2021_ESPS-W5_v02_M | weights_and_design | sect6b3_hh_w5.dta | pw_w5 | missing_expected_core_file |
| 1 | ETH_2021_ESPS-W5_v02_M | weights_and_design | sect6b4_hh_w5.dta | pw_w5 | missing_expected_core_file |
| 1 | ETH_2021_ESPS-W5_v02_M | weights_and_design | sect6c_hh_w5.dta | pw_w5 | missing_expected_core_file |
| 1 | ETH_2021_ESPS-W5_v02_M | weights_and_design | sect7a_hh_w5.dta | pw_w5 | missing_expected_core_file |
| 1 | ETH_2021_ESPS-W5_v02_M | weights_and_design | sect7b_hh_w5.dta | pw_w5 | missing_expected_core_file |
| 1 | ETH_2021_ESPS-W5_v02_M | weights_and_design | sect8_hh_w5.dta | pw_w5 | missing_expected_core_file |
| 2 | ETH_2018_ESS_v04_M | climate_geography | sect_cover_ph_w4.dta | saq19__Latitude;saq19__Longitude;ea_id | missing_expected_core_file |
| 2 | ETH_2018_ESS_v04_M | climate_geography | sect_cover_pp_w4.dta | saq19__Latitude;saq19__Longitude | missing_expected_core_file |
| 2 | ETH_2018_ESS_v04_M | climate_geography | sect_cover_ls_w4.dta | saq19__Latitude;saq19__Longitude | missing_expected_core_file |
| 2 | ETH_2018_ESS_v04_M | climate_geography | sect3_pp_w4.dta | s3q09__Latitude;s3q09__Longitude | missing_expected_core_file |
| 2 | ETH_2018_ESS_v04_M | climate_geography | sect10a_com_w4.dta | cs10q05__Latitude;cs10q05__Longitude | missing_expected_core_file |
| 2 | ETH_2018_ESS_v04_M | climate_geography | sect_cover_hh_w4.dta | ea_id | missing_expected_core_file |
| 2 | ETH_2018_ESS_v04_M | consumption_or_income | sect7a_hh_w4.dta | ea_id;household_id;item_cd_30day;pw_w4;s7q01;s7q02;saq01;saq02;saq03 | missing_expected_core_file |
| 2 | ETH_2018_ESS_v04_M | consumption_or_income | cons_agg_w4.dta | nom_nonfoodcons_aeq;nonfood_cons_ann;food_cons_ann | missing_expected_core_file |
| 2 | ETH_2018_ESS_v04_M | health_need_and_access | sect3_hh_w4.dta | s3q14;s3q15;s3q05;s3q17;s3q13;s3q18;s3q06_1;s3q06_2;s3q06_os;s3q09a;s3q09b | missing_expected_core_file |
| 2 | ETH_2018_ESS_v04_M | health_need_and_access | sect04_com_w4.dta | cs4q37 | missing_expected_core_file |
| 2 | ETH_2018_ESS_v04_M | household_person_keys | sect1_hh_w4.dta | individual_id;household_id | missing_expected_core_file |
| 2 | ETH_2018_ESS_v04_M | household_person_keys | sect11b1_hh_w4.dta | individual_id;household_id | missing_expected_core_file |
| 2 | ETH_2018_ESS_v04_M | household_person_keys | sect10d1_hh_w4.dta | household_id | missing_expected_core_file |
| 2 | ETH_2018_ESS_v04_M | household_person_keys | sect1_ph_w4.dta | household_id | missing_expected_core_file |
| 2 | ETH_2018_ESS_v04_M | household_person_keys | sect1_pp_w4.dta | household_id | missing_expected_core_file |
| 2 | ETH_2018_ESS_v04_M | household_person_keys | sect10b_hh_w4.dta | household_id | missing_expected_core_file |
| 2 | ETH_2018_ESS_v04_M | household_person_keys | sect2_pp_w4.dta | household_id | missing_expected_core_file |
| 2 | ETH_2018_ESS_v04_M | household_person_keys | sect3_pp_w4.dta | household_id | missing_expected_core_file |
| 2 | ETH_2018_ESS_v04_M | oop_health_expenditure | sect8_3_ls_w4.dta | ls_s8_3q04;ls_s8_3q22;ls_s8_3q24;ls_s8_3q03;ls_s8_3q05;ls_s8_3q06;ls_s8_3q10a;ls_s8_3q10b;ls_s8_3q11;ls_s8_3q12_1 | missing_expected_core_file |
| 2 | ETH_2018_ESS_v04_M | oop_health_expenditure | sect3_hh_w4.dta | s3q17;s3q18 | missing_expected_core_file |
| 2 | ETH_2018_ESS_v04_M | survey_timing | sect_cover_ph_w4.dta | InterviewDate;saq19__Timestamp | missing_expected_core_file |
| 2 | ETH_2018_ESS_v04_M | survey_timing | sect_cover_pp_w4.dta | InterviewDate;saq19__Timestamp | missing_expected_core_file |
| 2 | ETH_2018_ESS_v04_M | survey_timing | sect_cover_ls_w4.dta | InterviewDate;saq19__Timestamp | missing_expected_core_file |
| 2 | ETH_2018_ESS_v04_M | survey_timing | sect12b1_hh_w4.dta | s12bq08a;s12bq08b | missing_expected_core_file |
| 2 | ETH_2018_ESS_v04_M | survey_timing | ETH_HouseholdGeovariables_Y4.dta | wetQ_avgstart;h2018_wetQstart | missing_expected_core_file |
| 2 | ETH_2018_ESS_v04_M | survey_timing | sect_cover_hh_w4.dta | InterviewStart | missing_expected_core_file |
| 2 | ETH_2018_ESS_v04_M | survey_timing | sect15b_hh_w4.dta | s15q06b | missing_expected_core_file |
| 2 | ETH_2018_ESS_v04_M | weights_and_design | sect_cover_hh_w4.dta | ea_id | missing_expected_core_file |
| 2 | ETH_2018_ESS_v04_M | weights_and_design | sect_cover_ph_w4.dta | ea_id | missing_expected_core_file |
| 2 | ETH_2018_ESS_v04_M | weights_and_design | sect_cover_pp_w4.dta | ea_id | missing_expected_core_file |
| 2 | ETH_2018_ESS_v04_M | weights_and_design | sect6b2_hh_w4.dta | ea_id | missing_expected_core_file |
| 2 | ETH_2018_ESS_v04_M | weights_and_design | sect7a_hh_w4.dta | ea_id | missing_expected_core_file |
| 2 | ETH_2018_ESS_v04_M | weights_and_design | sect9_hh_w4.dta | ea_id | missing_expected_core_file |
| 2 | ETH_2018_ESS_v04_M | weights_and_design | sect1_hh_w4.dta | ea_id | missing_expected_core_file |
| 2 | ETH_2018_ESS_v04_M | weights_and_design | sect10d1_hh_w4.dta | ea_id | missing_expected_core_file |
| 4 | NGA_2012_GHSP-W2_v02_M | climate_geography | cons_agg_wave2_visit1 | ea | missing_expected_core_file |
| 4 | NGA_2012_GHSP-W2_v02_M | climate_geography | cons_agg_wave2_visit2 | ea | missing_expected_core_file |
| 4 | NGA_2012_GHSP-W2_v02_M | consumption_or_income | cons_agg_wave2_visit1 | totcons;nfdfoth;fdfishpr;fdothpr;fdrestby | missing_expected_core_file |
| 4 | NGA_2012_GHSP-W2_v02_M | consumption_or_income | cons_agg_wave2_visit2 | totcons;nfdfoth;fdfishpr;fdothpr;fdrestby | missing_expected_core_file |
| 4 | NGA_2012_GHSP-W2_v02_M | weights_and_design | cons_agg_wave2_visit1 | ea;hhweight | missing_expected_core_file |
| 4 | NGA_2012_GHSP-W2_v02_M | weights_and_design | cons_agg_wave2_visit2 | ea;hhweight | missing_expected_core_file |
| 6 | NGA_2010_GHSP-W1_v03_M | climate_geography | cons_agg_wave1_visit1 | ea | missing_expected_core_file |
| 6 | NGA_2010_GHSP-W1_v03_M | climate_geography | cons_agg_wave1_visit2 | ea | missing_expected_core_file |
| 6 | NGA_2010_GHSP-W1_v03_M | consumption_or_income | cons_agg_wave1_visit1 | totcons;nfdfoth;fdfishpr;fdothpr;fdrestby;fdalcpr;fdbeanpr | missing_expected_core_file |
| 6 | NGA_2010_GHSP-W1_v03_M | consumption_or_income | cons_agg_wave1_visit2 | totcons;nfdfoth;fdfishpr;fdothpr;fdrestby | missing_expected_core_file |
| 6 | NGA_2010_GHSP-W1_v03_M | weights_and_design | cons_agg_wave1_visit1 | ea;hhweight | missing_expected_core_file |
| 6 | NGA_2010_GHSP-W1_v03_M | weights_and_design | cons_agg_wave1_visit2 | ea;hhweight | missing_expected_core_file |
| 7 | TZA_2008_NPS-R1_v03_M | climate_geography | SEC_A_T_English_Labels | clusterid;ea | missing_expected_core_file |
| 7 | TZA_2008_NPS-R1_v03_M | climate_geography | SEC_A_T_Swahili_Labels | ea | missing_expected_core_file |
| 7 | TZA_2008_NPS-R1_v03_M | climate_geography | SECTA1A2_Swahili_Labels | ea_id | missing_expected_core_file |
| 7 | TZA_2008_NPS-R1_v03_M | climate_geography | SECTCB_Swahili_Labels | ea_id | missing_expected_core_file |
| 7 | TZA_2008_NPS-R1_v03_M | climate_geography | SECTCEFG | ea_id | missing_expected_core_file |
| 7 | TZA_2008_NPS-R1_v03_M | climate_geography | SECTCH | ea_id | missing_expected_core_file |
| 7 | TZA_2008_NPS-R1_v03_M | climate_geography | SECTCI | ea_id | missing_expected_core_file |
| 7 | TZA_2008_NPS-R1_v03_M | consumption_or_income | SEC_L_Swahili_Labels | hhid;slcode;slq1;slq2 | missing_expected_core_file |
| 7 | TZA_2008_NPS-R1_v03_M | consumption_or_income | SEC_M_Swahili_Labels | hhid;smcode;smq1;smq2 | missing_expected_core_file |
| 7 | TZA_2008_NPS-R1_v03_M | health_need_and_access | SEC_B_C_D_E1_F_G1_U_English_Labels | sdq22;sdq4;sdq43_1;sdq43_2;sdq43_3;sdq55_1;sdq55_2;sdq55_3;sdq6;sdq8;sdq9 | missing_expected_core_file |
| 7 | TZA_2008_NPS-R1_v03_M | health_need_and_access | SEC_I_English_Labels | siq8b | missing_expected_core_file |
| 7 | TZA_2008_NPS-R1_v03_M | household_person_keys | Agriculture SEC_1_ALL_Swahili_Labels | hhid;rosterid | missing_expected_core_file |
| 7 | TZA_2008_NPS-R1_v03_M | household_person_keys | SEC_B_C_D_E1_F_G1_U_Swahili_Labels | hhid | missing_expected_core_file |
| 7 | TZA_2008_NPS-R1_v03_M | household_person_keys | SEC_2A_Swahili_Labels | hhid | missing_expected_core_file |
| 7 | TZA_2008_NPS-R1_v03_M | household_person_keys | SEC_2B_Swahili_Labels | hhid | missing_expected_core_file |
| 7 | TZA_2008_NPS-R1_v03_M | household_person_keys | SEC_B_C_D_E1_F_G1_U_English_Labels | hhid | missing_expected_core_file |
| 7 | TZA_2008_NPS-R1_v03_M | household_person_keys | SEC_2A_English_Labels | hhid | missing_expected_core_file |

## Outputs

- `temp/priority_lsms_isa_official_file_receipt_validation.csv`
- `temp/priority_lsms_isa_official_file_receipt_file_match.csv`
- `temp/priority_lsms_isa_official_file_receipt_core_match.csv`
- `result/priority_lsms_isa_official_file_receipt_validator_summary.csv`

## Interpretation

This is a receipt gate, not a value gate. A matched official file name only
means that a local file or archive member has the same basename as the official
DDI file entry. Promotion still requires schema inspection, raw-value checks,
units, missing codes, skip patterns, recall periods, survey-design variables,
merge keys, and accepted climate linkage.

Generated Markdown handoffs are excluded from raw receipt evidence.
