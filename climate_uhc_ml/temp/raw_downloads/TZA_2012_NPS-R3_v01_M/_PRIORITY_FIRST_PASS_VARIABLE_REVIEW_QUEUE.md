# Priority First-Pass Variable Review Queue

Dataset: `TZA_2012_NPS-R3_v01_M` - Tanzania 2012-2013

Campaign phase: phase_1_double_failure_10_wave_base

Threshold role: required_for_10_country_wave_double_failure_threshold

Current raw receipt: not_received_no_original_raw_package

This is a compact first-pass queue for post-download raw-value review. It does
not verify raw values, does not promote any dataset, and does not write to
`data/`.

## Selected Variables

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
