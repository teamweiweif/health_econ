# Priority First-Pass Variable Review Queue

Dataset: `TZA_2008_NPS-R1_v03_M` - Tanzania 2008-2009

Campaign phase: phase_1_double_failure_10_wave_base

Threshold role: required_for_10_country_wave_double_failure_threshold

Current raw receipt: not_received_no_original_raw_package

This is a compact first-pass queue for post-download raw-value review. It does
not verify raw values, does not promote any dataset, and does not write to
`data/`.

## Selected Variables

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

## Post-Download Rule

Use the queue only after the complete original raw package and documentation
are present. For each selected variable, inspect labels, raw values, missing and
skip codes, units, recall periods, merge level, and denominator semantics.
Then fill:

- `temp/priority_promotion_verification_checklist.csv`
- `temp/priority_concept_verification_template.csv`
- `temp/priority_variable_verification_template.csv`

Do not promote this wave until the manual verification decision gate, synthesis
blueprint, country-wave packet, promoted-data gate, and accepted CHIRPS/ERA5
linkage all pass.
