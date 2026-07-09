# Priority First-Pass Variable Review Queue

Dataset: `TZA_2010_NPS-R2_v03_M` - Tanzania 2010-2011

Campaign phase: phase_1_double_failure_10_wave_base

Threshold role: required_for_10_country_wave_double_failure_threshold

Current raw receipt: not_received_no_original_raw_package

This is a compact first-pass queue for post-download raw-value review. It does
not verify raw values, does not promote any dataset, and does not write to
`data/`.

## Selected Variables

| requirement_id | concept | candidate_files | candidate_raw_variable | metadata_confidence | first_pass_review_status |
|---|---|---|---|---|---|
| household_person_merge_keys | household_id | AG_SEC10B;AG_SEC7A;AG_SEC7B | y2_hhid | high | blocked_raw_package_not_received |
| household_person_merge_keys | household_id | FS_J1;FS_J3;HH_SEC_H1;TZY1.HH.Consumption | hhid | high | blocked_raw_package_not_received |
| household_person_merge_keys | demographics | AG_SEC01 | ag1a_02 | high | blocked_raw_package_not_received |
| household_person_merge_keys | demographics | AG_SEC01 | ag1a_03 | high | blocked_raw_package_not_received |
| weights_and_survey_design | survey_weight | COMSEC_CJ | cm_j01b | high | blocked_raw_package_not_received |
| weights_and_survey_design | survey_weight | COMSEC_CJ | cm_j02b | high | blocked_raw_package_not_received |
| weights_and_survey_design | psu_cluster | COMSEC_CA;COMSEC_CB;COMSEC_CD;COMSEC_CE;COMSEC_CF;COMSEC_CG;COMSEC_CH;COMSEC_CI;COMSEC_CJ;comsec_cc | id_04 | high | blocked_raw_package_not_received |
| weights_and_survey_design | psu_cluster | COMSEC_CI | cm_i15d | high | blocked_raw_package_not_received |
| weights_and_survey_design | strata | HH_SEC_A | strataid | high | blocked_raw_package_not_received |
| weights_and_survey_design | strata | TZY1.HH.Consumption;TZY2.HH.Consumption | strata | high | blocked_raw_package_not_received |
| consumption_or_income_aggregate | total_consumption_or_income | AG_SEC3A | ag3a_04 | high | blocked_raw_package_not_received |
| consumption_or_income_aggregate | total_consumption_or_income | AG_SEC3B | ag3b_04 | high | blocked_raw_package_not_received |
| oop_health_expenditure | oop_health_expenditure | HH_SEC_D | hh_d13 | high | blocked_raw_package_not_received |
| oop_health_expenditure | oop_health_expenditure | HH_SEC_D | hh_d15 | high | blocked_raw_package_not_received |
| illness_need_care_access | health_need | HH_SEC_D | hh_d12_1 | high | blocked_raw_package_not_received |
| illness_need_care_access | health_need | HH_SEC_D | hh_d12_2 | high | blocked_raw_package_not_received |
| illness_need_care_access | care_or_barrier | HH_SEC_D | hh_d04_1 | high | blocked_raw_package_not_received |
| illness_need_care_access | care_or_barrier | HH_SEC_D | hh_d04_2 | high | blocked_raw_package_not_received |
| illness_need_care_access | insurance |  |  | metadata_candidate_from_concept_checklist | blocked_raw_package_not_received |
| survey_timing | survey_timing | TZY1.HH.Consumption;TZY2.HH.Consumption | intmonth | high | blocked_raw_package_not_received |
| survey_timing | survey_timing | TZY1.HH.Consumption;TZY2.HH.Consumption | quarter | high | blocked_raw_package_not_received |
| geography_climate_linkage | climate_geography | AG_SEC2A | ag2a_09 | high | blocked_raw_package_not_received |
| geography_climate_linkage | climate_geography | AG_SEC2A | ag2a_10 | high | blocked_raw_package_not_received |
| missing_skip_units_recall | household_id | AG_SEC10B;AG_SEC7A;AG_SEC7B | y2_hhid | high | blocked_raw_package_not_received |
| missing_skip_units_recall | household_id | FS_J1;FS_J3;HH_SEC_H1;TZY1.HH.Consumption | hhid | high | blocked_raw_package_not_received |
| missing_skip_units_recall | survey_weight | COMSEC_CJ | cm_j01b | high | blocked_raw_package_not_received |
| missing_skip_units_recall | survey_weight | COMSEC_CJ | cm_j02b | high | blocked_raw_package_not_received |
| missing_skip_units_recall | total_consumption_or_income | AG_SEC3A | ag3a_04 | high | blocked_raw_package_not_received |
| missing_skip_units_recall | total_consumption_or_income | AG_SEC3B | ag3b_04 | high | blocked_raw_package_not_received |
| missing_skip_units_recall | oop_health_expenditure | HH_SEC_D | hh_d13 | high | blocked_raw_package_not_received |
| missing_skip_units_recall | oop_health_expenditure | HH_SEC_D | hh_d15 | high | blocked_raw_package_not_received |
| missing_skip_units_recall | health_need | HH_SEC_D | hh_d12_1 | high | blocked_raw_package_not_received |
| missing_skip_units_recall | health_need | HH_SEC_D | hh_d12_2 | high | blocked_raw_package_not_received |
| missing_skip_units_recall | care_or_barrier | HH_SEC_D | hh_d04_1 | high | blocked_raw_package_not_received |
| missing_skip_units_recall | care_or_barrier | HH_SEC_D | hh_d04_2 | high | blocked_raw_package_not_received |
| missing_skip_units_recall | survey_timing | TZY1.HH.Consumption;TZY2.HH.Consumption | intmonth | high | blocked_raw_package_not_received |
| missing_skip_units_recall | survey_timing | TZY1.HH.Consumption;TZY2.HH.Consumption | quarter | high | blocked_raw_package_not_received |
| missing_skip_units_recall | climate_geography | AG_SEC2A | ag2a_09 | high | blocked_raw_package_not_received |
| missing_skip_units_recall | climate_geography | AG_SEC2A | ag2a_10 | high | blocked_raw_package_not_received |

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
