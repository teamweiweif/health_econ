# Priority First-Pass Variable Review Queue

Dataset: `UGA_2014_SAGE-EL_v01_M` - Uganda 2014

Campaign phase: phase_1_double_failure_10_wave_base

Threshold role: required_for_10_country_wave_double_failure_threshold

Current raw receipt: not_received_no_original_raw_package

This is a compact first-pass queue for post-download raw-value review. It does
not verify raw values, does not promote any dataset, and does not write to
`data/`.

## Selected Variables

| requirement_id | concept | candidate_files | candidate_raw_variable | metadata_confidence | first_pass_review_status |
|---|---|---|---|---|---|
| household_person_merge_keys | household_id | SAGE_HHWEIGHTSV2;int_access_educ18plus;int_access_fin;int_access_health;int_access_health_hh;int_access_school;int_as... | hhid | high | blocked_raw_package_not_received |
| household_person_merge_keys | demographics | int_access_educ18plus | attended_school | high | blocked_raw_package_not_received |
| household_person_merge_keys | demographics | int_access_educ18plus | attended_school_female | high | blocked_raw_package_not_received |
| weights_and_survey_design | survey_weight | SAGE_HHWEIGHTSV2;int_access_educ18plus;int_access_fin;int_access_health;int_access_health_hh;int_access_school;int_as... | weightfinal2 | high | blocked_raw_package_not_received |
| weights_and_survey_design | survey_weight | int_consexp | hmult | high | blocked_raw_package_not_received |
| weights_and_survey_design | psu_cluster |  |  | metadata_candidate_from_concept_checklist | blocked_raw_package_not_received |
| weights_and_survey_design | strata |  |  | metadata_candidate_from_concept_checklist | blocked_raw_package_not_received |
| consumption_or_income_aggregate | total_consumption_or_income | int_consexp | cpexp30_pae | moderate | blocked_raw_package_not_received |
| consumption_or_income_aggregate | total_consumption_or_income | int_consexp | nrexp30 | moderate | blocked_raw_package_not_received |
| oop_health_expenditure | oop_health_expenditure | int_access_educ18plus;int_access_health;int_access_school;int_demographics_mem;int_welfare_memdata | hh3_q8 | high | blocked_raw_package_not_received |
| oop_health_expenditure | oop_health_expenditure | int_access_fin | credit_item_10 | high | blocked_raw_package_not_received |
| illness_need_care_access | health_need | int_access_educ18plus;int_access_health;int_access_school;int_demographics_mem;int_welfare_memdata | hh3_q1 | high | blocked_raw_package_not_received |
| illness_need_care_access | health_need | int_access_educ18plus;int_access_health;int_access_school;int_demographics_mem;int_welfare_memdata | hh3_q4 | high | blocked_raw_package_not_received |
| illness_need_care_access | care_or_barrier | int_access_educ18plus;int_access_fin;int_access_health;int_access_health_hh;int_access_school;int_asset_index;int_ben... | eligilitystatus | high | blocked_raw_package_not_received |
| illness_need_care_access | care_or_barrier | int_access_educ18plus;int_access_health;int_access_school;int_demographics_mem;int_welfare_memdata | hh3_q8 | high | blocked_raw_package_not_received |
| illness_need_care_access | insurance |  |  | metadata_candidate_from_concept_checklist | blocked_raw_package_not_received |
| survey_timing | survey_timing | int_access_fin;int_cohesion;int_welfare_hh;sage_labourintermed | doi | high | blocked_raw_package_not_received |
| survey_timing | survey_timing | int_access_fin;int_cohesion;int_welfare_hh;sage_labourintermed | intdate | high | blocked_raw_package_not_received |
| geography_climate_linkage | climate_geography | SAGE_HHWEIGHTSV2;int_access_educ18plus;int_access_fin;int_access_health;int_access_health_hh;int_access_school;int_as... | county | high | blocked_raw_package_not_received |
| geography_climate_linkage | climate_geography | SAGE_HHWEIGHTSV2;int_access_educ18plus;int_access_fin;int_access_health;int_access_health_hh;int_access_school;int_as... | district | high | blocked_raw_package_not_received |
| missing_skip_units_recall | household_id | SAGE_HHWEIGHTSV2;int_access_educ18plus;int_access_fin;int_access_health;int_access_health_hh;int_access_school;int_as... | hhid | high | blocked_raw_package_not_received |
| missing_skip_units_recall | survey_weight | SAGE_HHWEIGHTSV2;int_access_educ18plus;int_access_fin;int_access_health;int_access_health_hh;int_access_school;int_as... | weightfinal2 | high | blocked_raw_package_not_received |
| missing_skip_units_recall | survey_weight | int_consexp | hmult | high | blocked_raw_package_not_received |
| missing_skip_units_recall | total_consumption_or_income | int_consexp | cpexp30_pae | moderate | blocked_raw_package_not_received |
| missing_skip_units_recall | total_consumption_or_income | int_consexp | nrexp30 | moderate | blocked_raw_package_not_received |
| missing_skip_units_recall | oop_health_expenditure | int_access_educ18plus;int_access_health;int_access_school;int_demographics_mem;int_welfare_memdata | hh3_q8 | high | blocked_raw_package_not_received |
| missing_skip_units_recall | oop_health_expenditure | int_access_fin | credit_item_10 | high | blocked_raw_package_not_received |
| missing_skip_units_recall | health_need | int_access_educ18plus;int_access_health;int_access_school;int_demographics_mem;int_welfare_memdata | hh3_q1 | high | blocked_raw_package_not_received |
| missing_skip_units_recall | health_need | int_access_educ18plus;int_access_health;int_access_school;int_demographics_mem;int_welfare_memdata | hh3_q4 | high | blocked_raw_package_not_received |
| missing_skip_units_recall | care_or_barrier | int_access_educ18plus;int_access_fin;int_access_health;int_access_health_hh;int_access_school;int_asset_index;int_ben... | eligilitystatus | high | blocked_raw_package_not_received |
| missing_skip_units_recall | care_or_barrier | int_access_educ18plus;int_access_health;int_access_school;int_demographics_mem;int_welfare_memdata | hh3_q8 | high | blocked_raw_package_not_received |
| missing_skip_units_recall | survey_timing | int_access_fin;int_cohesion;int_welfare_hh;sage_labourintermed | doi | high | blocked_raw_package_not_received |
| missing_skip_units_recall | survey_timing | int_access_fin;int_cohesion;int_welfare_hh;sage_labourintermed | intdate | high | blocked_raw_package_not_received |
| missing_skip_units_recall | climate_geography | SAGE_HHWEIGHTSV2;int_access_educ18plus;int_access_fin;int_access_health;int_access_health_hh;int_access_school;int_as... | county | high | blocked_raw_package_not_received |
| missing_skip_units_recall | climate_geography | SAGE_HHWEIGHTSV2;int_access_educ18plus;int_access_fin;int_access_health;int_access_health_hh;int_access_school;int_as... | district | high | blocked_raw_package_not_received |

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
