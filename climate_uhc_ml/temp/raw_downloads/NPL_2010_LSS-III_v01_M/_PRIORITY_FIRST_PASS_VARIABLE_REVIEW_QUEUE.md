# Priority First-Pass Variable Review Queue

Dataset: `NPL_2010_LSS-III_v01_M` - Nepal 2010-2011

Campaign phase: phase_2_sixth_country_financial_protection_backup

Threshold role: candidate_for_6th_financial_protection_country

Current raw receipt: not_received_no_original_raw_package

This is a compact first-pass queue for post-download raw-value review. It does
not verify raw values, does not promote any dataset, and does not write to
`data/`.

## Selected Variables

| requirement_id | concept | candidate_files | candidate_raw_variable | metadata_confidence | first_pass_review_status |
|---|---|---|---|---|---|
| household_person_merge_keys | household_id |  |  | metadata_candidate_from_concept_checklist | blocked_raw_package_not_received |
| household_person_merge_keys | demographics | FINAL_PREF | depratio3 | high | blocked_raw_package_not_received |
| household_person_merge_keys | demographics | FINAL_PREF | educatn | high | blocked_raw_package_not_received |
| weights_and_survey_design | survey_weight | S20 | v20_07 | high | blocked_raw_package_not_received |
| weights_and_survey_design | survey_weight | anthro | underwt | high | blocked_raw_package_not_received |
| weights_and_survey_design | psu_cluster | FINAL_PREF;anthro;sample;sys | xhpsu | high | blocked_raw_package_not_received |
| weights_and_survey_design | psu_cluster | S00 | v00_dist | high | blocked_raw_package_not_received |
| weights_and_survey_design | strata | FINAL_PREF;sample | stratum | high | blocked_raw_package_not_received |
| weights_and_survey_design | strata | FINAL_PREF;S00;S01;S02;S03;S04;S05;S06A;S06B;S06C;S06D;S07;S08;S09A;S09B;S09C;S09D;S10A;S10B;S11 | xstra | high | blocked_raw_package_not_received |
| consumption_or_income_aggregate | total_consumption_or_income | FINAL_PREF | sh_consdur_30 | high | blocked_raw_package_not_received |
| consumption_or_income_aggregate | total_consumption_or_income | FINAL_PREF | sh_consdur_7 | high | blocked_raw_package_not_received |
| oop_health_expenditure | oop_health_expenditure | S08 | v08_17a | high | blocked_raw_package_not_received |
| oop_health_expenditure | oop_health_expenditure | S08 | v08_17b | high | blocked_raw_package_not_received |
| illness_need_care_access | health_need | S08 | v08_04 | high | blocked_raw_package_not_received |
| illness_need_care_access | health_need | S08 | v08_05 | high | blocked_raw_package_not_received |
| illness_need_care_access | care_or_barrier | S08 | v08_14 | high | blocked_raw_package_not_received |
| illness_need_care_access | care_or_barrier | S08 | v08_15 | high | blocked_raw_package_not_received |
| illness_need_care_access | insurance |  |  | metadata_candidate_from_concept_checklist | blocked_raw_package_not_received |
| survey_timing | survey_timing | FINAL_PREF | Date | high | blocked_raw_package_not_received |
| geography_climate_linkage | climate_geography | FINAL_PREF;sample | district | high | blocked_raw_package_not_received |
| geography_climate_linkage | climate_geography | FINAL_PREF;sample | region | high | blocked_raw_package_not_received |
| missing_skip_units_recall | household_id |  |  | metadata_candidate_from_concept_checklist | blocked_raw_package_not_received |
| missing_skip_units_recall | survey_weight | S20 | v20_07 | high | blocked_raw_package_not_received |
| missing_skip_units_recall | survey_weight | anthro | underwt | high | blocked_raw_package_not_received |
| missing_skip_units_recall | total_consumption_or_income | FINAL_PREF | sh_consdur_30 | high | blocked_raw_package_not_received |
| missing_skip_units_recall | total_consumption_or_income | FINAL_PREF | sh_consdur_7 | high | blocked_raw_package_not_received |
| missing_skip_units_recall | oop_health_expenditure | S08 | v08_17a | high | blocked_raw_package_not_received |
| missing_skip_units_recall | oop_health_expenditure | S08 | v08_17b | high | blocked_raw_package_not_received |
| missing_skip_units_recall | health_need | S08 | v08_04 | high | blocked_raw_package_not_received |
| missing_skip_units_recall | health_need | S08 | v08_05 | high | blocked_raw_package_not_received |
| missing_skip_units_recall | care_or_barrier | S08 | v08_14 | high | blocked_raw_package_not_received |
| missing_skip_units_recall | care_or_barrier | S08 | v08_15 | high | blocked_raw_package_not_received |
| missing_skip_units_recall | survey_timing | FINAL_PREF | Date | high | blocked_raw_package_not_received |
| missing_skip_units_recall | climate_geography | FINAL_PREF;sample | district | high | blocked_raw_package_not_received |
| missing_skip_units_recall | climate_geography | FINAL_PREF;sample | region | high | blocked_raw_package_not_received |

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
