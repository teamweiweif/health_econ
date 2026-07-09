# Priority First-Pass Variable Review Queue

Dataset: `KGZ_1993_KMPS_v01_M` - Kyrgyz Republic 1993

Campaign phase: phase_2_sixth_country_financial_protection_backup

Threshold role: candidate_for_6th_financial_protection_country

Current raw receipt: not_received_no_original_raw_package

This is a compact first-pass queue for post-download raw-value review. It does
not verify raw values, does not promote any dataset, and does not write to
`data/`.

## Selected Variables

| requirement_id | concept | candidate_files | candidate_raw_variable | metadata_confidence | first_pass_review_status |
|---|---|---|---|---|---|
| household_person_merge_keys | household_id | CONADULT;CORE;KADIET;KADULT;KCHDIET;KCHILD;KHHLD;KINDIV;KINDIVH;KYGPOV | hid | high | blocked_raw_package_not_received |
| household_person_merge_keys | household_id | INCEXP | khid | high | blocked_raw_package_not_received |
| household_person_merge_keys | demographics | CONADULT;KINDIV | age | high | blocked_raw_package_not_received |
| household_person_merge_keys | demographics | CONADULT | edlevel | high | blocked_raw_package_not_received |
| weights_and_survey_design | survey_weight | KADULT;KCHILD | a1m1 | high | blocked_raw_package_not_received |
| weights_and_survey_design | survey_weight | KADULT;KCHILD | a1m37_2 | high | blocked_raw_package_not_received |
| weights_and_survey_design | psu_cluster |  |  | metadata_candidate_from_concept_checklist | blocked_raw_package_not_received |
| weights_and_survey_design | strata |  |  | metadata_candidate_from_concept_checklist | blocked_raw_package_not_received |
| consumption_or_income_aggregate | total_consumption_or_income | INCEXP | khomcx | moderate | blocked_raw_package_not_received |
| oop_health_expenditure | oop_health_expenditure | KADULT;KCHILD | a1l15 | high | blocked_raw_package_not_received |
| oop_health_expenditure | oop_health_expenditure | KADULT;KCHILD | a1l16 | high | blocked_raw_package_not_received |
| illness_need_care_access | health_need | KADULT;KCHILD | a1l24 | high | blocked_raw_package_not_received |
| illness_need_care_access | health_need | KHHLD | af14_4a | high | blocked_raw_package_not_received |
| illness_need_care_access | care_or_barrier | KADULT;KCHILD | a1l15 | high | blocked_raw_package_not_received |
| illness_need_care_access | care_or_barrier | KADULT;KCHILD | a1l16 | high | blocked_raw_package_not_received |
| illness_need_care_access | insurance |  |  | metadata_candidate_from_concept_checklist | blocked_raw_package_not_received |
| survey_timing | survey_timing | CORE | month | high | blocked_raw_package_not_received |
| survey_timing | survey_timing | KADULT;KCHILD | a1h7_2 | high | blocked_raw_package_not_received |
| geography_climate_linkage | climate_geography | CORE | region | high | blocked_raw_package_not_received |
| geography_climate_linkage | climate_geography | KCOMM | a1x3 | moderate | blocked_raw_package_not_received |
| missing_skip_units_recall | household_id | CONADULT;CORE;KADIET;KADULT;KCHDIET;KCHILD;KHHLD;KINDIV;KINDIVH;KYGPOV | hid | high | blocked_raw_package_not_received |
| missing_skip_units_recall | household_id | INCEXP | khid | high | blocked_raw_package_not_received |
| missing_skip_units_recall | survey_weight | KADULT;KCHILD | a1m1 | high | blocked_raw_package_not_received |
| missing_skip_units_recall | survey_weight | KADULT;KCHILD | a1m37_2 | high | blocked_raw_package_not_received |
| missing_skip_units_recall | total_consumption_or_income | INCEXP | khomcx | moderate | blocked_raw_package_not_received |
| missing_skip_units_recall | oop_health_expenditure | KADULT;KCHILD | a1l15 | high | blocked_raw_package_not_received |
| missing_skip_units_recall | oop_health_expenditure | KADULT;KCHILD | a1l16 | high | blocked_raw_package_not_received |
| missing_skip_units_recall | health_need | KADULT;KCHILD | a1l24 | high | blocked_raw_package_not_received |
| missing_skip_units_recall | health_need | KHHLD | af14_4a | high | blocked_raw_package_not_received |
| missing_skip_units_recall | care_or_barrier | KADULT;KCHILD | a1l15 | high | blocked_raw_package_not_received |
| missing_skip_units_recall | care_or_barrier | KADULT;KCHILD | a1l16 | high | blocked_raw_package_not_received |
| missing_skip_units_recall | survey_timing | CORE | month | high | blocked_raw_package_not_received |
| missing_skip_units_recall | survey_timing | KADULT;KCHILD | a1h7_2 | high | blocked_raw_package_not_received |
| missing_skip_units_recall | climate_geography | CORE | region | high | blocked_raw_package_not_received |
| missing_skip_units_recall | climate_geography | KCOMM | a1x3 | moderate | blocked_raw_package_not_received |

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
