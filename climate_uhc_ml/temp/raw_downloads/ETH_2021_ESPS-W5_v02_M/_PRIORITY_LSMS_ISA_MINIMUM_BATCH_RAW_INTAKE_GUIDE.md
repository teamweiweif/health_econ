# Minimum Batch Raw Intake Guide

IDNO: `ETH_2021_ESPS-W5_v02_M`

Country-wave: Ethiopia 2021-2022

Threshold rank: 1

Role: minimum_10_wave_core

Official World Bank microdata URL: https://microdata.worldbank.org/catalog/6161/get-microdata

Target folder: `temp/raw_downloads/ETH_2021_ESPS-W5_v02_M/`

## Current Receipt Status

- Expected full official files: 68
- Matched full official files: 0
- Missing full official files: 68
- Expected core files: 36
- Matched core files: 0
- Missing core files: 36
- Official receipt status: `blocked_no_original_package`

## Core Files To Confirm

| requirement | file_rank | file_id | expected_file_name | top_variable_names | official_core_file_match_status |
|---|---|---|---|---|---|
| climate_geography | 1 | F1 | sect_cover_hh_w5.dta | saq19__Latitude;saq19__Longitude | missing_expected_core_file |
| climate_geography | 2 | F42 | sect10a_com_w5.dta | cs10q05__Latitude;cs10q05__Longitude | missing_expected_core_file |
| climate_geography | 3 | F46 | sect_cover_pp_w5.dta | saq19__Latitude;saq19__Longitude | missing_expected_core_file |
| climate_geography | 4 | F54 | sect_cover_ph_w5.dta | saq19__Latitude;saq19__Longitude | missing_expected_core_file |
| climate_geography | 5 | F59 | sect_cover_ls_w5.dta | saq19__Latitude;saq19__Longitude | missing_expected_core_file |
| climate_geography | 6 | F49 | sect3_pp_w5.dta | s3q09__Latitude;s3q09__Longitude | missing_expected_core_file |
| consumption_or_income | 1 | F66 | cons_agg_w5.dta | nonfood_cons2;nom_nonfoodcons_aeq;nonfood_cons_ann;food_cons2;food_cons_ann;nom_foodcons_aeq;fafh_cons_ann;spat_totco... | missing_expected_core_file |
| health_need_and_access | 1 | F4 | sect3_hh_w5.dta | s3q14;s3q15;s3q05;s3q17;s3q13;s3q18 | missing_expected_core_file |
| health_need_and_access | 2 | F36 | sect04_com_w5.dta | cs4q37;cs4q34;cs4q35;cs4q28 | missing_expected_core_file |
| health_need_and_access | 3 | F49 | sect3_pp_w5.dta | s3q15_1;s3q15_2 | missing_expected_core_file |
| household_person_keys | 1 | F2 | sect1_hh_w5.dta | individual_id;household_id | missing_expected_core_file |
| household_person_keys | 2 | F21 | sect12b1_hh_w5.dta | household_id | missing_expected_core_file |
| household_person_keys | 3 | F47 | sect1_pp_w5.dta | household_id | missing_expected_core_file |
| household_person_keys | 4 | F55 | sect1_ph_w5.dta | household_id | missing_expected_core_file |
| household_person_keys | 5 | F48 | sect2_pp_w5.dta | household_id | missing_expected_core_file |
| household_person_keys | 6 | F49 | sect3_pp_w5.dta | household_id | missing_expected_core_file |
| household_person_keys | 7 | F50 | sect4_pp_w5.dta | household_id | missing_expected_core_file |
| household_person_keys | 8 | F13 | sect6c_hh_w5.dta | individual_id | missing_expected_core_file |
| oop_health_expenditure | 1 | F62 | sect8_3_ls_w5.dta | ls_s8_3q04;ls_s8_3q22;ls_s8_3q24;ls_s8_3q03;ls_s8_3q05;ls_s8_3q06;ls_s8_3q10a;ls_s8_3q10b;ls_s8_3q11;ls_s8_3q12_1 | missing_expected_core_file |
| oop_health_expenditure | 2 | F4 | sect3_hh_w5.dta | s3q17;s3q18 | missing_expected_core_file |
| survey_timing | 1 | F46 | sect_cover_pp_w5.dta | InterviewDate | missing_expected_core_file |
| survey_timing | 2 | F54 | sect_cover_ph_w5.dta | InterviewDate | missing_expected_core_file |
| survey_timing | 3 | F59 | sect_cover_ls_w5.dta | InterviewDate | missing_expected_core_file |
| survey_timing | 4 | F21 | sect12b1_hh_w5.dta | s12bq08a;s12bq08b | missing_expected_core_file |
| survey_timing | 5 | F15 | sect7b_hh_w5.dta | item_cd_12months;s7q04 | missing_expected_core_file |
| survey_timing | 6 | F64 | eth_householdgeovariables_y5.dta | wetQ_avgstart | missing_expected_core_file |
| survey_timing | 7 | F1 | sect_cover_hh_w5.dta | saq19__Timestamp | missing_expected_core_file |
| survey_timing | 8 | F65 | eth_plotgeovariables_y5.dta | wetQ_avgstart | missing_expected_core_file |
| weights_and_design | 1 | F1 | sect_cover_hh_w5.dta | pw_w5;ea_id | missing_expected_core_file |
| weights_and_design | 2 | F10 | sect6b2_hh_w5.dta | pw_w5 | missing_expected_core_file |

## Intake Steps

1. Use the official World Bank link above after login, terms, or Data Access Agreement acceptance.
2. Download the complete official package and documentation. Keep original archive names where possible.
3. Place the unchanged package or extracted original files under the target folder.
4. Rerun the post-download commands below.
5. Review raw-value, outcome, timing, geography, and climate-linkage gates before any promotion.

```bash
python script/17_audit_raw_downloads.py; python script/144_build_priority_lsms_isa_raw_package_intake_packet.py; python script/145_build_priority_lsms_isa_archive_member_preflight.py; python script/150_build_priority_lsms_isa_raw_package_receipt_checklist.py; python script/152_build_priority_lsms_isa_credentialed_raw_acquisition_workbench.py; python script/153_validate_priority_lsms_isa_official_file_receipt.py; python script/154_build_priority_lsms_isa_threshold_download_sequence.py; python script/155_build_priority_lsms_isa_minimum_batch_raw_intake_guide.py; python script/149_build_priority_lsms_isa_raw_value_verification_workbook.py; python script/132_build_priority_analysis_dataset_synthesis_blueprint.py; python script/148_build_priority_lsms_isa_country_wave_promotion_packets.py; python script/151_refresh_refocused_promoted_country_wave_registry.py; python script/127_enforce_promoted_data_gate.py; python script/36_build_direct_read_audit_bundle.py; python script/14_validate_workspace.py
```

## Stop Rule

Do not write this country-wave into data/ or run ML until complete official file receipt, raw-value verification, outcome construction, survey timing/geography, and accepted CHIRPS or ERA5 climate linkage all pass.
