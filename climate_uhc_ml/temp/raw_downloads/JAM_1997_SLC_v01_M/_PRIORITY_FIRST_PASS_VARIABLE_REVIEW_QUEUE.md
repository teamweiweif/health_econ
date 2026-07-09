# Priority First-Pass Variable Review Queue

Dataset: `JAM_1997_SLC_v01_M` - Jamaica 1997

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
| household_person_merge_keys | demographics | ANNUAL;HHSIZE | hhsize1 | high | blocked_raw_package_not_received |
| household_person_merge_keys | demographics | ANNUAL;HHSIZE | hhsize2 | high | blocked_raw_package_not_received |
| weights_and_survey_design | survey_weight | ANNUAL;EDTOTALS;REC001 | edwght | high | blocked_raw_package_not_received |
| weights_and_survey_design | survey_weight | NUTR97 | waz | high | blocked_raw_package_not_received |
| weights_and_survey_design | psu_cluster | EXP97 | Cluster | high | blocked_raw_package_not_received |
| weights_and_survey_design | strata | REC033 | strat | high | blocked_raw_package_not_received |
| consumption_or_income_aggregate | total_consumption_or_income | ANNUAL | cons | moderate | blocked_raw_package_not_received |
| oop_health_expenditure | oop_health_expenditure | REC003 | a11 | moderate | blocked_raw_package_not_received |
| oop_health_expenditure | oop_health_expenditure | REC003 | a12 | moderate | blocked_raw_package_not_received |
| illness_need_care_access | health_need | REC002 | a01 | high | blocked_raw_package_not_received |
| illness_need_care_access | health_need | REC002 | a02 | high | blocked_raw_package_not_received |
| illness_need_care_access | care_or_barrier | REC003 | a09 | high | blocked_raw_package_not_received |
| illness_need_care_access | care_or_barrier | REC003 | a10 | high | blocked_raw_package_not_received |
| illness_need_care_access | insurance | REC003 | a21 | high | blocked_raw_package_not_received |
| survey_timing | survey_timing | REC001 | int_date | high | blocked_raw_package_not_received |
| geography_climate_linkage | climate_geography | ANNUAL;EDTOTALS;HEADS;HHSIZE;REC001 | district | high | blocked_raw_package_not_received |
| geography_climate_linkage | climate_geography | EDTOTALS;REC001 | region | high | blocked_raw_package_not_received |
| missing_skip_units_recall | household_id |  |  | metadata_candidate_from_concept_checklist | blocked_raw_package_not_received |
| missing_skip_units_recall | survey_weight | ANNUAL;EDTOTALS;REC001 | edwght | high | blocked_raw_package_not_received |
| missing_skip_units_recall | survey_weight | NUTR97 | waz | high | blocked_raw_package_not_received |
| missing_skip_units_recall | total_consumption_or_income | ANNUAL | cons | moderate | blocked_raw_package_not_received |
| missing_skip_units_recall | oop_health_expenditure | REC003 | a11 | moderate | blocked_raw_package_not_received |
| missing_skip_units_recall | oop_health_expenditure | REC003 | a12 | moderate | blocked_raw_package_not_received |
| missing_skip_units_recall | health_need | REC002 | a01 | high | blocked_raw_package_not_received |
| missing_skip_units_recall | health_need | REC002 | a02 | high | blocked_raw_package_not_received |
| missing_skip_units_recall | care_or_barrier | REC003 | a09 | high | blocked_raw_package_not_received |
| missing_skip_units_recall | care_or_barrier | REC003 | a10 | high | blocked_raw_package_not_received |
| missing_skip_units_recall | survey_timing | REC001 | int_date | high | blocked_raw_package_not_received |
| missing_skip_units_recall | climate_geography | ANNUAL;EDTOTALS;HEADS;HHSIZE;REC001 | district | high | blocked_raw_package_not_received |
| missing_skip_units_recall | climate_geography | EDTOTALS;REC001 | region | high | blocked_raw_package_not_received |

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
