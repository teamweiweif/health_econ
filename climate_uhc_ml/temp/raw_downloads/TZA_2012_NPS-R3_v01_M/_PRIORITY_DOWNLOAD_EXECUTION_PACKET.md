# Priority Download Execution Packet

Dataset: `TZA_2012_NPS-R3_v01_M` - Tanzania 2012-2013

Download order: 9

Official get-microdata URL: https://microdata.worldbank.org/catalog/2252/get-microdata

Target folder: `temp/raw_downloads/TZA_2012_NPS-R3_v01_M/`

Current status: `ready_for_manual_credentialed_download_no_raw_receipt`

Raw receipt: `not_received_no_original_raw_package`

## Manual Download Scope

Download the complete unchanged official raw package plus all documentation
through the permitted World Bank account, terms, or Data Access Agreement
workflow. Do not assemble an incomplete analysis package from only the listed
core files.

## Minimum Acceptance Rule

Complete official package must be present; at least 12 priority core files/modules must be found directly or inside the official archive; all 8 promotion requirements and 40 selected first-pass variables must remain raw-backed before any data/ write.

## Core Files To Confirm

| core_file_rank | metadata_file_name | candidate_categories | expected_local_name_patterns | file_acceptance_status |
|---|---|---|---|---|
| 1 | AG_SEC_2A | geography;shocks;survey_design | AG_SEC_2A;AG_SEC_2A.*;AG_SEC_2A.dta;AG_SEC_2A.sav;AG_SEC_2A.por;AG_SEC_2A.sas7bdat;AG_SEC_2A.xpt;AG_SEC_2A.csv;*AG_SE... | blocked_no_raw_or_archive_file |
| 2 | AG_SEC_3A | consumption;health_need_access;shocks;survey_design | AG_SEC_3A;AG_SEC_3A.*;AG_SEC_3A.dta;AG_SEC_3A.sav;AG_SEC_3A.por;AG_SEC_3A.sas7bdat;AG_SEC_3A.xpt;AG_SEC_3A.csv;*AG_SE... | blocked_no_raw_or_archive_file |
| 3 | AG_SEC_3B | consumption;health_need_access;shocks;survey_design | AG_SEC_3B;AG_SEC_3B.*;AG_SEC_3B.dta;AG_SEC_3B.sav;AG_SEC_3B.por;AG_SEC_3B.sas7bdat;AG_SEC_3B.xpt;AG_SEC_3B.csv;*AG_SE... | blocked_no_raw_or_archive_file |
| 4 | AG_SEC_4A | shocks;survey_design | AG_SEC_4A;AG_SEC_4A.*;AG_SEC_4A.dta;AG_SEC_4A.sav;AG_SEC_4A.por;AG_SEC_4A.sas7bdat;AG_SEC_4A.xpt;AG_SEC_4A.csv;*AG_SE... | blocked_no_raw_or_archive_file |
| 5 | AG_SEC_4B | shocks;survey_design | AG_SEC_4B;AG_SEC_4B.*;AG_SEC_4B.dta;AG_SEC_4B.sav;AG_SEC_4B.por;AG_SEC_4B.sas7bdat;AG_SEC_4B.xpt;AG_SEC_4B.csv;*AG_SE... | blocked_no_raw_or_archive_file |
| 6 | AG_SEC_5A | health_need_access;shocks;survey_design | AG_SEC_5A;AG_SEC_5A.*;AG_SEC_5A.dta;AG_SEC_5A.sav;AG_SEC_5A.por;AG_SEC_5A.sas7bdat;AG_SEC_5A.xpt;AG_SEC_5A.csv;*AG_SE... | blocked_no_raw_or_archive_file |
| 7 | AG_SEC_5B | health_need_access;shocks;survey_design | AG_SEC_5B;AG_SEC_5B.*;AG_SEC_5B.dta;AG_SEC_5B.sav;AG_SEC_5B.por;AG_SEC_5B.sas7bdat;AG_SEC_5B.xpt;AG_SEC_5B.csv;*AG_SE... | blocked_no_raw_or_archive_file |
| 8 | COM_SEC_CE | demographics;geography;health_need_access;shocks;survey_design | COM_SEC_CE;COM_SEC_CE.*;COM_SEC_CE.dta;COM_SEC_CE.sav;COM_SEC_CE.por;COM_SEC_CE.sas7bdat;COM_SEC_CE.xpt;COM_SEC_CE.cs... | blocked_no_raw_or_archive_file |
| 9 | COM_SEC_CF_ID | geography;survey_design | COM_SEC_CF_ID;COM_SEC_CF_ID.*;COM_SEC_CF_ID.dta;COM_SEC_CF_ID.sav;COM_SEC_CF_ID.por;COM_SEC_CF_ID.sas7bdat;COM_SEC_CF... | blocked_no_raw_or_archive_file |
| 10 | HH_SEC_A | demographics;geography;survey_design | HH_SEC_A;HH_SEC_A.*;HH_SEC_A.dta;HH_SEC_A.sav;HH_SEC_A.por;HH_SEC_A.sas7bdat;HH_SEC_A.xpt;HH_SEC_A.csv;*HH_SEC_A* | blocked_no_raw_or_archive_file |
| 11 | HH_SEC_C | demographics;health_need_access;survey_design | HH_SEC_C;HH_SEC_C.*;HH_SEC_C.dta;HH_SEC_C.sav;HH_SEC_C.por;HH_SEC_C.sas7bdat;HH_SEC_C.xpt;HH_SEC_C.csv;*HH_SEC_C* | blocked_no_raw_or_archive_file |
| 12 | HouseholdGeovars_Y3 | geography;health_need_access;shocks | HouseholdGeovars_Y3;HouseholdGeovars_Y3.*;HouseholdGeovars_Y3.dta;HouseholdGeovars_Y3.sav;HouseholdGeovars_Y3.por;Hou... | blocked_no_raw_or_archive_file |

## First-Pass Variables To Inspect

| requirement_id | concept | candidate_files | candidate_raw_variable | metadata_confidence | first_pass_review_status |
|---|---|---|---|---|---|
| household_person_merge_keys | household_id | AG_NETWORK;AG_SEC_01;AG_SEC_08;AG_SEC_10;AG_SEC_11;AG_SEC_12A;AG_SEC_12B;AG_SEC_2A;AG_SEC_2B;AG_SEC_3A;AG_SEC_3B;AG_S... | y3_hhid | high | blocked_raw_package_not_received |
| household_person_merge_keys | household_id | AG_SEC_A | ag_a09 | high | blocked_raw_package_not_received |
| household_person_merge_keys | demographics | AG_SEC_01 | ag01_02 | high | blocked_raw_package_not_received |
| household_person_merge_keys | demographics | AG_SEC_01 | ag01_03 | high | blocked_raw_package_not_received |
| weights_and_survey_design | survey_weight | COM_SEC_CF | cm_f06wght | high | blocked_raw_package_not_received |
| weights_and_survey_design | survey_weight | COM_SEC_CF | cm_f06wght2 | high | blocked_raw_package_not_received |
| weights_and_survey_design | psu_cluster | AG_SEC_A | ag_a04_1 | high | blocked_raw_package_not_received |
| weights_and_survey_design | psu_cluster | AG_SEC_A | ag_a04_2 | high | blocked_raw_package_not_received |
| weights_and_survey_design | strata | HH_SEC_A | strataid | high | blocked_raw_package_not_received |
| weights_and_survey_design | strata | LF_SEC_04 | lf04_12 | high | blocked_raw_package_not_received |
| consumption_or_income_aggregate | total_consumption_or_income | AG_SEC_3A | ag3a_04 | high | blocked_raw_package_not_received |
| consumption_or_income_aggregate | total_consumption_or_income | AG_SEC_3B | ag3b_04 | high | blocked_raw_package_not_received |
| oop_health_expenditure | oop_health_expenditure | HH_SEC_D | hh_d13 | high | blocked_raw_package_not_received |
| oop_health_expenditure | oop_health_expenditure | HH_SEC_D | hh_d15 | high | blocked_raw_package_not_received |
| illness_need_care_access | health_need | HH_SEC_D | hh_d12_1 | high | blocked_raw_package_not_received |
| illness_need_care_access | health_need | HH_SEC_D | hh_d12_2 | high | blocked_raw_package_not_received |
| illness_need_care_access | care_or_barrier | HH_SEC_D | hh_d04_1 | high | blocked_raw_package_not_received |
| illness_need_care_access | care_or_barrier | HH_SEC_D | hh_d04_2 | high | blocked_raw_package_not_received |
| illness_need_care_access | insurance | HH_SEC_E | hh_e35 | high | blocked_raw_package_not_received |
| illness_need_care_access | insurance | HH_SEC_E | hh_e53 | high | blocked_raw_package_not_received |
| survey_timing | survey_timing | AG_SEC_A | ag_a13 | high | blocked_raw_package_not_received |
| survey_timing | survey_timing | COM_SEC_A1A2 | cm_a07 | high | blocked_raw_package_not_received |
| geography_climate_linkage | climate_geography | AG_SEC_2A | ag2a_06_1 | high | blocked_raw_package_not_received |
| geography_climate_linkage | climate_geography | AG_SEC_2A | ag2a_06_2 | high | blocked_raw_package_not_received |
| missing_skip_units_recall | household_id | AG_NETWORK;AG_SEC_01;AG_SEC_08;AG_SEC_10;AG_SEC_11;AG_SEC_12A;AG_SEC_12B;AG_SEC_2A;AG_SEC_2B;AG_SEC_3A;AG_SEC_3B;AG_S... | y3_hhid | high | blocked_raw_package_not_received |
| missing_skip_units_recall | household_id | AG_SEC_A | ag_a09 | high | blocked_raw_package_not_received |
| missing_skip_units_recall | survey_weight | COM_SEC_CF | cm_f06wght | high | blocked_raw_package_not_received |
| missing_skip_units_recall | survey_weight | COM_SEC_CF | cm_f06wght2 | high | blocked_raw_package_not_received |
| missing_skip_units_recall | total_consumption_or_income | AG_SEC_3A | ag3a_04 | high | blocked_raw_package_not_received |
| missing_skip_units_recall | total_consumption_or_income | AG_SEC_3B | ag3b_04 | high | blocked_raw_package_not_received |
| missing_skip_units_recall | oop_health_expenditure | HH_SEC_D | hh_d13 | high | blocked_raw_package_not_received |
| missing_skip_units_recall | oop_health_expenditure | HH_SEC_D | hh_d15 | high | blocked_raw_package_not_received |
| missing_skip_units_recall | health_need | HH_SEC_D | hh_d12_1 | high | blocked_raw_package_not_received |
| missing_skip_units_recall | health_need | HH_SEC_D | hh_d12_2 | high | blocked_raw_package_not_received |
| missing_skip_units_recall | care_or_barrier | HH_SEC_D | hh_d04_1 | high | blocked_raw_package_not_received |
| missing_skip_units_recall | care_or_barrier | HH_SEC_D | hh_d04_2 | high | blocked_raw_package_not_received |
| missing_skip_units_recall | survey_timing | AG_SEC_A | ag_a13 | high | blocked_raw_package_not_received |
| missing_skip_units_recall | survey_timing | COM_SEC_A1A2 | cm_a07 | high | blocked_raw_package_not_received |
| missing_skip_units_recall | climate_geography | AG_SEC_2A | ag2a_06_1 | high | blocked_raw_package_not_received |
| missing_skip_units_recall | climate_geography | AG_SEC_2A | ag2a_06_2 | high | blocked_raw_package_not_received |

## Post-Download Commands

- `python script/17_audit_raw_downloads.py`
- `python script/128_build_priority_archive_member_preflight.py`
- `python script/130_build_priority_raw_package_receipt_ledger.py`
- `python script/03_inspect_raw_schemas.py`
- `python script/29_build_raw_variable_verification_protocol.py`
- `python script/33_build_harmonization_recipe_gate.py`
- `python script/125_build_priority_climate_linkage_preflight.py`
- `python script/126_build_priority_raw_verification_workbook.py`
- `python script/140_build_priority_first_pass_variable_review_queue.py`
- `python script/129_build_priority_manual_verification_decision_gate.py`
- `python script/132_build_priority_analysis_dataset_synthesis_blueprint.py`
- `python script/134_build_priority_country_wave_promotion_packets.py`
- `python script/127_enforce_promoted_data_gate.py`
- `python script/36_build_direct_read_audit_bundle.py`
- `python script/14_validate_workspace.py`

## Stop Rule

Do not write this country-wave into data/ until original package receipt, core-file coverage, raw schema inspection, manual value/unit/key review, outcome readiness, and accepted CHIRPS/ERA5 linkage all pass.
