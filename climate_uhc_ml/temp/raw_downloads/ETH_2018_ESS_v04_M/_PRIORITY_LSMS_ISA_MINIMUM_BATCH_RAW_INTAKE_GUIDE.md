# Minimum Batch Raw Intake Guide

IDNO: `ETH_2018_ESS_v04_M`

Country-wave: Ethiopia 2018-2019

Threshold rank: 2

Role: minimum_10_wave_core

Official World Bank microdata URL: https://microdata.worldbank.org/catalog/3823/get-microdata

Target folder: `temp/raw_downloads/ETH_2018_ESS_v04_M/`

## Current Receipt Status

- Expected full official files: 68
- Matched full official files: 0
- Missing full official files: 68
- Expected core files: 35
- Matched core files: 0
- Missing core files: 35
- Official receipt status: `blocked_no_original_package`

## Core Files To Confirm

| requirement | file_rank | file_id | expected_file_name | top_variable_names | official_core_file_match_status |
|---|---|---|---|---|---|
| climate_geography | 1 | F39 | sect_cover_ph_w4.dta | saq19__Latitude;saq19__Longitude;ea_id | missing_expected_core_file |
| climate_geography | 2 | F44 | sect_cover_pp_w4.dta | saq19__Latitude;saq19__Longitude | missing_expected_core_file |
| climate_geography | 3 | F34 | sect_cover_ls_w4.dta | saq19__Latitude;saq19__Longitude | missing_expected_core_file |
| climate_geography | 4 | F47 | sect3_pp_w4.dta | s3q09__Latitude;s3q09__Longitude | missing_expected_core_file |
| climate_geography | 5 | F73 | sect10a_com_w4.dta | cs10q05__Latitude;cs10q05__Longitude | missing_expected_core_file |
| climate_geography | 6 | F1 | sect_cover_hh_w4.dta | ea_id | missing_expected_core_file |
| consumption_or_income | 1 | F14 | sect7a_hh_w4.dta | ea_id;household_id;item_cd_30day;pw_w4;s7q01;s7q02;saq01;saq02;saq03 | missing_expected_core_file |
| consumption_or_income | 2 | F63 | cons_agg_w4.dta | nom_nonfoodcons_aeq;nonfood_cons_ann;food_cons_ann | missing_expected_core_file |
| health_need_and_access | 1 | F4 | sect3_hh_w4.dta | s3q14;s3q15;s3q05;s3q17;s3q13;s3q18;s3q06_1;s3q06_2;s3q06_os;s3q09a;s3q09b | missing_expected_core_file |
| health_need_and_access | 2 | F56 | sect04_com_w4.dta | cs4q37 | missing_expected_core_file |
| household_person_keys | 1 | F2 | sect1_hh_w4.dta | individual_id;household_id | missing_expected_core_file |
| household_person_keys | 2 | F25 | sect11b1_hh_w4.dta | individual_id;household_id | missing_expected_core_file |
| household_person_keys | 3 | F22 | sect10d1_hh_w4.dta | household_id | missing_expected_core_file |
| household_person_keys | 4 | F40 | sect1_ph_w4.dta | household_id | missing_expected_core_file |
| household_person_keys | 5 | F45 | sect1_pp_w4.dta | household_id | missing_expected_core_file |
| household_person_keys | 6 | F20 | sect10b_hh_w4.dta | household_id | missing_expected_core_file |
| household_person_keys | 7 | F46 | sect2_pp_w4.dta | household_id | missing_expected_core_file |
| household_person_keys | 8 | F47 | sect3_pp_w4.dta | household_id | missing_expected_core_file |
| oop_health_expenditure | 1 | F37 | sect8_3_ls_w4.dta | ls_s8_3q04;ls_s8_3q22;ls_s8_3q24;ls_s8_3q03;ls_s8_3q05;ls_s8_3q06;ls_s8_3q10a;ls_s8_3q10b;ls_s8_3q11;ls_s8_3q12_1 | missing_expected_core_file |
| oop_health_expenditure | 2 | F4 | sect3_hh_w4.dta | s3q17;s3q18 | missing_expected_core_file |
| survey_timing | 1 | F39 | sect_cover_ph_w4.dta | InterviewDate;saq19__Timestamp | missing_expected_core_file |
| survey_timing | 2 | F44 | sect_cover_pp_w4.dta | InterviewDate;saq19__Timestamp | missing_expected_core_file |
| survey_timing | 3 | F34 | sect_cover_ls_w4.dta | InterviewDate;saq19__Timestamp | missing_expected_core_file |
| survey_timing | 4 | F28 | sect12b1_hh_w4.dta | s12bq08a;s12bq08b | missing_expected_core_file |
| survey_timing | 5 | F67 | ETH_HouseholdGeovariables_Y4.dta | wetQ_avgstart;h2018_wetQstart | missing_expected_core_file |
| survey_timing | 6 | F1 | sect_cover_hh_w4.dta | InterviewStart | missing_expected_core_file |
| survey_timing | 7 | F33 | sect15b_hh_w4.dta | s15q06b | missing_expected_core_file |
| weights_and_design | 1 | F1 | sect_cover_hh_w4.dta | ea_id | missing_expected_core_file |
| weights_and_design | 2 | F39 | sect_cover_ph_w4.dta | ea_id | missing_expected_core_file |
| weights_and_design | 3 | F44 | sect_cover_pp_w4.dta | ea_id | missing_expected_core_file |

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
