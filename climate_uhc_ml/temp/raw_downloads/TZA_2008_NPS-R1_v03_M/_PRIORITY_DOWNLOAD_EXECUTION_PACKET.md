# Priority Download Execution Packet

Dataset: `TZA_2008_NPS-R1_v03_M` - Tanzania 2008-2009

Download order: 7

Official get-microdata URL: https://microdata.worldbank.org/catalog/76/get-microdata

Target folder: `temp/raw_downloads/TZA_2008_NPS-R1_v03_M/`

Current status: `ready_for_manual_credentialed_download_no_raw_receipt`

Raw receipt: `not_received_no_original_raw_package`

## Manual Download Scope

Download the complete unchanged official raw package plus all documentation
through the permitted World Bank account, terms, or Data Access Agreement
workflow. Do not assemble an incomplete analysis package from only the listed
core files.

## Minimum Acceptance Rule

Complete official package must be present; at least 12 priority core files/modules must be found directly or inside the official archive; all 8 promotion requirements and 37 selected first-pass variables must remain raw-backed before any data/ write.

## Core Files To Confirm

| core_file_rank | metadata_file_name | candidate_categories | expected_local_name_patterns | file_acceptance_status |
|---|---|---|---|---|
| 1 | HH.Geovariables_Y1 | geography;health_need_access;shocks;survey_design | HH.Geovariables_Y1;HH.*;*HH* | blocked_no_raw_or_archive_file |
| 2 | SECTCEFG | geography;shocks;survey_design | SECTCEFG;SECTCEFG.*;SECTCEFG.dta;SECTCEFG.sav;SECTCEFG.por;SECTCEFG.sas7bdat;SECTCEFG.xpt;SECTCEFG.csv;*SECTCEFG* | blocked_no_raw_or_archive_file |
| 3 | SECTCH | demographics;geography;shocks;survey_design | SECTCH;SECTCH.*;SECTCH.dta;SECTCH.sav;SECTCH.por;SECTCH.sas7bdat;SECTCH.xpt;SECTCH.csv;*SECTCH* | blocked_no_raw_or_archive_file |
| 4 | SEC_A_T_English_Labels | geography;shocks;survey_design | SEC_A_T_English_Labels;SEC_A_T_English_Labels.*;SEC_A_T_English_Labels.dta;SEC_A_T_English_Labels.sav;SEC_A_T_English... | blocked_no_raw_or_archive_file |
| 5 | SEC_B_C_D_E1_F_G1_U_English_Labels | demographics;geography;health_expenditure;health_need_access;shocks;survey_design | SEC_B_C_D_E1_F_G1_U_English_Labels;SEC_B_C_D_E1_F_G1_U_English_Labels.*;SEC_B_C_D_E1_F_G1_U_English_Labels.dta;SEC_B_... | blocked_no_raw_or_archive_file |
| 6 | SEC_H1_J_K2_O2_P1_Q1_S1_English_Labels | demographics;geography;shocks;survey_design | SEC_H1_J_K2_O2_P1_Q1_S1_English_Labels;SEC_H1_J_K2_O2_P1_Q1_S1_English_Labels.*;SEC_H1_J_K2_O2_P1_Q1_S1_English_Label... | blocked_no_raw_or_archive_file |
| 7 | SEC_P2_English_Labels | shocks;survey_design | SEC_P2_English_Labels;SEC_P2_English_Labels.*;SEC_P2_English_Labels.dta;SEC_P2_English_Labels.sav;SEC_P2_English_Labe... | blocked_no_raw_or_archive_file |
| 8 | SEC_S2_English_Labels | demographics;health_need_access;survey_design | SEC_S2_English_Labels;SEC_S2_English_Labels.*;SEC_S2_English_Labels.dta;SEC_S2_English_Labels.sav;SEC_S2_English_Labe... | blocked_no_raw_or_archive_file |
| 9 | SEC_3A_English_Labels | consumption;health_need_access;shocks;survey_design | SEC_3A_English_Labels;SEC_3A_English_Labels.*;SEC_3A_English_Labels.dta;SEC_3A_English_Labels.sav;SEC_3A_English_Labe... | blocked_no_raw_or_archive_file |
| 10 | SEC_3B_English_Labels | consumption;health_need_access;shocks;survey_design | SEC_3B_English_Labels;SEC_3B_English_Labels.*;SEC_3B_English_Labels.dta;SEC_3B_English_Labels.sav;SEC_3B_English_Labe... | blocked_no_raw_or_archive_file |
| 11 | SEC_4A_English_Labels | shocks;survey_design | SEC_4A_English_Labels;SEC_4A_English_Labels.*;SEC_4A_English_Labels.dta;SEC_4A_English_Labels.sav;SEC_4A_English_Labe... | blocked_no_raw_or_archive_file |
| 12 | TZY1.HH.Consumption | consumption;demographics;geography;health_need_access;survey_design | TZY1.HH.Consumption;TZY1.HH.*;*TZY1.HH* | blocked_no_raw_or_archive_file |

## First-Pass Variables To Inspect

| requirement_id | concept | candidate_files | candidate_raw_variable | metadata_confidence | first_pass_review_status |
|---|---|---|---|---|---|
| household_person_merge_keys | household_id | Agriculture SEC_1_ALL_Swahili_Labels;HH.Geovariables_Y1;SEC_2A_English_Labels;SEC_2A_Swahili_Labels;SEC_2B_English_La... | hhid | high | blocked_raw_package_not_received |
| household_person_merge_keys | demographics | SECTCH | ch12 | high | blocked_raw_package_not_received |
| household_person_merge_keys | demographics | SECTCH | ch19d | high | blocked_raw_package_not_received |
| weights_and_survey_design | survey_weight | SECTCJ_S | cj06wght | high | blocked_raw_package_not_received |
| weights_and_survey_design | survey_weight | SEC_A_T_English_Labels;nps_weights_oct2010 | hh_weight | high | blocked_raw_package_not_received |
| weights_and_survey_design | psu_cluster | HH.Geovariables_Y1;SECTA1A2_English_Labels;SECTA1A2_Swahili_Labels;SECTCB;SECTCB_Swahili_Labels;SECTCC;SECTCD;SECTCEF... | ea_id | high | blocked_raw_package_not_received |
| weights_and_survey_design | psu_cluster | HH.Geovariables_Y1 | lat_modified | high | blocked_raw_package_not_received |
| weights_and_survey_design | strata | SEC_A_T_English_Labels;nps_weights_oct2010 | strataid | high | blocked_raw_package_not_received |
| weights_and_survey_design | strata | TZY1.HH.Consumption | strata | high | blocked_raw_package_not_received |
| consumption_or_income_aggregate | total_consumption_or_income | SEC_3A_English_Labels | s3aq4 | high | blocked_raw_package_not_received |
| consumption_or_income_aggregate | total_consumption_or_income | SEC_3B_English_Labels | s3bq4 | high | blocked_raw_package_not_received |
| oop_health_expenditure | oop_health_expenditure | SEC_B_C_D_E1_F_G1_U_English_Labels;SEC_B_C_D_E1_F_G1_U_Swahili_Labels | scq14_fee | high | blocked_raw_package_not_received |
| oop_health_expenditure | oop_health_expenditure | SEC_B_C_D_E1_F_G1_U_English_Labels | scq14_food | high | blocked_raw_package_not_received |
| illness_need_care_access | health_need | SEC_B_C_D_E1_F_G1_U_English_Labels | sdq39 | high | blocked_raw_package_not_received |
| illness_need_care_access | health_need | SEC_B_C_D_E1_F_G1_U_English_Labels | sdq40 | high | blocked_raw_package_not_received |
| illness_need_care_access | care_or_barrier | SEC_B_C_D_E1_F_G1_U_English_Labels | scq14_trans | high | blocked_raw_package_not_received |
| illness_need_care_access | care_or_barrier | SEC_B_C_D_E1_F_G1_U_English_Labels | sdq3_1 | high | blocked_raw_package_not_received |
| illness_need_care_access | insurance |  |  | metadata_candidate_from_concept_checklist | blocked_raw_package_not_received |
| survey_timing | survey_timing | SECTA1A2_English_Labels | ca07m | high | blocked_raw_package_not_received |
| survey_timing | survey_timing | SECTA1A2_English_Labels | ca07y | high | blocked_raw_package_not_received |
| geography_climate_linkage | climate_geography | HH.Geovariables_Y1 | lat_modified | high | blocked_raw_package_not_received |
| geography_climate_linkage | climate_geography | HH.Geovariables_Y1 | lon_modified | high | blocked_raw_package_not_received |
| missing_skip_units_recall | household_id | Agriculture SEC_1_ALL_Swahili_Labels;HH.Geovariables_Y1;SEC_2A_English_Labels;SEC_2A_Swahili_Labels;SEC_2B_English_La... | hhid | high | blocked_raw_package_not_received |
| missing_skip_units_recall | survey_weight | SECTCJ_S | cj06wght | high | blocked_raw_package_not_received |
| missing_skip_units_recall | survey_weight | SEC_A_T_English_Labels;nps_weights_oct2010 | hh_weight | high | blocked_raw_package_not_received |
| missing_skip_units_recall | total_consumption_or_income | SEC_3A_English_Labels | s3aq4 | high | blocked_raw_package_not_received |
| missing_skip_units_recall | total_consumption_or_income | SEC_3B_English_Labels | s3bq4 | high | blocked_raw_package_not_received |
| missing_skip_units_recall | oop_health_expenditure | SEC_B_C_D_E1_F_G1_U_English_Labels;SEC_B_C_D_E1_F_G1_U_Swahili_Labels | scq14_fee | high | blocked_raw_package_not_received |
| missing_skip_units_recall | oop_health_expenditure | SEC_B_C_D_E1_F_G1_U_English_Labels | scq14_food | high | blocked_raw_package_not_received |
| missing_skip_units_recall | health_need | SEC_B_C_D_E1_F_G1_U_English_Labels | sdq39 | high | blocked_raw_package_not_received |
| missing_skip_units_recall | health_need | SEC_B_C_D_E1_F_G1_U_English_Labels | sdq40 | high | blocked_raw_package_not_received |
| missing_skip_units_recall | care_or_barrier | SEC_B_C_D_E1_F_G1_U_English_Labels | scq14_trans | high | blocked_raw_package_not_received |
| missing_skip_units_recall | care_or_barrier | SEC_B_C_D_E1_F_G1_U_English_Labels | sdq3_1 | high | blocked_raw_package_not_received |
| missing_skip_units_recall | survey_timing | SECTA1A2_English_Labels | ca07m | high | blocked_raw_package_not_received |
| missing_skip_units_recall | survey_timing | SECTA1A2_English_Labels | ca07y | high | blocked_raw_package_not_received |
| missing_skip_units_recall | climate_geography | HH.Geovariables_Y1 | lat_modified | high | blocked_raw_package_not_received |
| missing_skip_units_recall | climate_geography | HH.Geovariables_Y1 | lon_modified | high | blocked_raw_package_not_received |

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
