# Priority First-Pass Variable Review Queue

Dataset: `NGA_2010_GHSP-W1_v03_M` - Nigeria 2010-2011

Campaign phase: phase_1_double_failure_10_wave_base

Threshold role: required_for_10_country_wave_double_failure_threshold

Current raw receipt: not_received_no_original_raw_package

This is a compact first-pass queue for post-download raw-value review. It does
not verify raw values, does not promote any dataset, and does not write to
`data/`.

## Selected Variables

| requirement_id | concept | candidate_files | candidate_raw_variable | metadata_confidence | first_pass_review_status |
|---|---|---|---|---|---|
| household_person_merge_keys | household_id | NGA_HouseholdGeovariables_Y1;NGA_PlotGeovariables_Y1;cons_agg_wave1_visit1;cons_agg_wave1_visit2;sect10_plantingw1;se... | hhid | high | blocked_raw_package_not_received |
| household_person_merge_keys | demographics | cons_agg_wave1_visit1;cons_agg_wave1_visit2 | edtexp | high | blocked_raw_package_not_received |
| household_person_merge_keys | demographics | cons_agg_wave1_visit1;cons_agg_wave1_visit2 | nfdinsur | high | blocked_raw_package_not_received |
| weights_and_survey_design | survey_weight | cons_agg_wave1_visit1;cons_agg_wave1_visit2 | hhweight | high | blocked_raw_package_not_received |
| weights_and_survey_design | survey_weight | sect4a_harvestw1 | s4aq52 | high | blocked_raw_package_not_received |
| weights_and_survey_design | psu_cluster | NGA_HouseholdGeovariables_Y1;NGA_PlotGeovariables_Y1;cons_agg_wave1_visit1;cons_agg_wave1_visit2;sect10_plantingw1;se... | ea | high | blocked_raw_package_not_received |
| weights_and_survey_design | psu_cluster | NGA_HouseholdGeovariables_Y1 | lat_dd_mod | high | blocked_raw_package_not_received |
| weights_and_survey_design | strata |  |  | metadata_candidate_from_concept_checklist | blocked_raw_package_not_received |
| consumption_or_income_aggregate | total_consumption_or_income | cons_agg_wave1_visit1;cons_agg_wave1_visit2 | totcons | high | blocked_raw_package_not_received |
| oop_health_expenditure | oop_health_expenditure | sect4a_harvestw1 | s4aq20 | high | blocked_raw_package_not_received |
| oop_health_expenditure | oop_health_expenditure | sect4a_harvestw1 | s4aq20b | high | blocked_raw_package_not_received |
| illness_need_care_access | health_need | sect4a_harvestw1 | s4aq3 | high | blocked_raw_package_not_received |
| illness_need_care_access | health_need | sect4a_harvestw1 | s4aq6a | high | blocked_raw_package_not_received |
| illness_need_care_access | care_or_barrier | sect4a_harvestw1 | s4aq15 | high | blocked_raw_package_not_received |
| illness_need_care_access | care_or_barrier | sect4a_harvestw1 | s4aq16 | high | blocked_raw_package_not_received |
| illness_need_care_access | insurance | sect3_plantingw1 | s3q36 | high | blocked_raw_package_not_received |
| illness_need_care_access | insurance | sect3a_harvestw1 | s3aq35 | high | blocked_raw_package_not_received |
| survey_timing | survey_timing | sectc_plantingw1 | interview_date | high | blocked_raw_package_not_received |
| geography_climate_linkage | climate_geography | NGA_HouseholdGeovariables_Y1 | lat_dd_mod | high | blocked_raw_package_not_received |
| geography_climate_linkage | climate_geography | NGA_HouseholdGeovariables_Y1 | lon_dd_mod | high | blocked_raw_package_not_received |
| missing_skip_units_recall | household_id | NGA_HouseholdGeovariables_Y1;NGA_PlotGeovariables_Y1;cons_agg_wave1_visit1;cons_agg_wave1_visit2;sect10_plantingw1;se... | hhid | high | blocked_raw_package_not_received |
| missing_skip_units_recall | survey_weight | cons_agg_wave1_visit1;cons_agg_wave1_visit2 | hhweight | high | blocked_raw_package_not_received |
| missing_skip_units_recall | survey_weight | sect4a_harvestw1 | s4aq52 | high | blocked_raw_package_not_received |
| missing_skip_units_recall | total_consumption_or_income | cons_agg_wave1_visit1;cons_agg_wave1_visit2 | totcons | high | blocked_raw_package_not_received |
| missing_skip_units_recall | oop_health_expenditure | sect4a_harvestw1 | s4aq20 | high | blocked_raw_package_not_received |
| missing_skip_units_recall | oop_health_expenditure | sect4a_harvestw1 | s4aq20b | high | blocked_raw_package_not_received |
| missing_skip_units_recall | health_need | sect4a_harvestw1 | s4aq3 | high | blocked_raw_package_not_received |
| missing_skip_units_recall | health_need | sect4a_harvestw1 | s4aq6a | high | blocked_raw_package_not_received |
| missing_skip_units_recall | care_or_barrier | sect4a_harvestw1 | s4aq15 | high | blocked_raw_package_not_received |
| missing_skip_units_recall | care_or_barrier | sect4a_harvestw1 | s4aq16 | high | blocked_raw_package_not_received |
| missing_skip_units_recall | survey_timing | sectc_plantingw1 | interview_date | high | blocked_raw_package_not_received |
| missing_skip_units_recall | climate_geography | NGA_HouseholdGeovariables_Y1 | lat_dd_mod | high | blocked_raw_package_not_received |
| missing_skip_units_recall | climate_geography | NGA_HouseholdGeovariables_Y1 | lon_dd_mod | high | blocked_raw_package_not_received |

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
