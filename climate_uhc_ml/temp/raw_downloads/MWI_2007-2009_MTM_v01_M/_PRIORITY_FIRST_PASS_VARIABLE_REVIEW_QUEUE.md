# Priority First-Pass Variable Review Queue

Dataset: `MWI_2007-2009_MTM_v01_M` - Malawi 2007-2009

Campaign phase: phase_1_double_failure_10_wave_base

Threshold role: required_for_10_country_wave_double_failure_threshold

Current raw receipt: not_received_no_original_raw_package

This is a compact first-pass queue for post-download raw-value review. It does
not verify raw values, does not promote any dataset, and does not write to
`data/`.

## Selected Variables

| requirement_id | concept | candidate_files | candidate_raw_variable | metadata_confidence | first_pass_review_status |
|---|---|---|---|---|---|
| household_person_merge_keys | household_id | hh2p1_cs;hh2p1_s1;hh2p1_s2;hh2p1_s3;hh2p1_s4;hh2p1_s5;hh2p1_s6;hh2p1_s7;hh2p1_s8;hh2p2_cs;hh2p2_s10;hh2p2_s11;hh2p2_s... | hhid | high | blocked_raw_package_not_received |
| household_person_merge_keys | household_id | p1_cs;p1_s1;p1_s2;p1_s3;p1_s4;p1_s5;p1_s6;p1_s7;p1_s8;p2_cs;p2_s10;p2_s11;p2_s12;p2_s13;p2_s14;p2_s14a;p2_s15;p2_s9;p... | ea | high | blocked_raw_package_not_received |
| household_person_merge_keys | demographics | hh2_cmty;hh3_cmty | caq14 | high | blocked_raw_package_not_received |
| household_person_merge_keys | demographics | hh2_cmty;hh3_cmty | caq16_l | high | blocked_raw_package_not_received |
| weights_and_survey_design | survey_weight | hh2_mortality;pi_mortality | mq18 | high | blocked_raw_package_not_received |
| weights_and_survey_design | survey_weight | hh2_mortality;pi_mortality | mq19 | high | blocked_raw_package_not_received |
| weights_and_survey_design | psu_cluster | hh2_mkts_location;mkts_location | q7_1 | high | blocked_raw_package_not_received |
| weights_and_survey_design | psu_cluster | hh2_mkts_location;mkts_location | q7_10 | high | blocked_raw_package_not_received |
| weights_and_survey_design | strata |  |  | metadata_candidate_from_concept_checklist | blocked_raw_package_not_received |
| consumption_or_income_aggregate | total_consumption_or_income | hh2p1_s4;p1_s4 | s4q03 | high | blocked_raw_package_not_received |
| consumption_or_income_aggregate | total_consumption_or_income | hh2p1_s4;p1_s4 | s4q03u | high | blocked_raw_package_not_received |
| oop_health_expenditure | oop_health_expenditure | hh2p2_s9 | s9q22b | high | blocked_raw_package_not_received |
| oop_health_expenditure | oop_health_expenditure | hh2p3_s16 | s16q35b | high | blocked_raw_package_not_received |
| illness_need_care_access | health_need | hh2_mortality;pi_mortality | mq04 | high | blocked_raw_package_not_received |
| illness_need_care_access | health_need | hh2_mortality;pi_mortality | mq06_1 | high | blocked_raw_package_not_received |
| illness_need_care_access | care_or_barrier | hh2_cmty | ccq42_n | high | blocked_raw_package_not_received |
| illness_need_care_access | care_or_barrier | hh2_cmty | ccq42_u | high | blocked_raw_package_not_received |
| illness_need_care_access | insurance |  |  | metadata_candidate_from_concept_checklist | blocked_raw_package_not_received |
| survey_timing | survey_timing | hh2_mortality | mq25c | high | blocked_raw_package_not_received |
| survey_timing | survey_timing | hh2_tf | tfq6_c1 | high | blocked_raw_package_not_received |
| geography_climate_linkage | climate_geography | hh2_mkts_hlthfac | cq5e1 | high | blocked_raw_package_not_received |
| geography_climate_linkage | climate_geography | hh2_mkts_hlthfac | cq5e2 | high | blocked_raw_package_not_received |
| missing_skip_units_recall | household_id | hh2p1_cs;hh2p1_s1;hh2p1_s2;hh2p1_s3;hh2p1_s4;hh2p1_s5;hh2p1_s6;hh2p1_s7;hh2p1_s8;hh2p2_cs;hh2p2_s10;hh2p2_s11;hh2p2_s... | hhid | high | blocked_raw_package_not_received |
| missing_skip_units_recall | household_id | p1_cs;p1_s1;p1_s2;p1_s3;p1_s4;p1_s5;p1_s6;p1_s7;p1_s8;p2_cs;p2_s10;p2_s11;p2_s12;p2_s13;p2_s14;p2_s14a;p2_s15;p2_s9;p... | ea | high | blocked_raw_package_not_received |
| missing_skip_units_recall | survey_weight | hh2_mortality;pi_mortality | mq18 | high | blocked_raw_package_not_received |
| missing_skip_units_recall | survey_weight | hh2_mortality;pi_mortality | mq19 | high | blocked_raw_package_not_received |
| missing_skip_units_recall | total_consumption_or_income | hh2p1_s4;p1_s4 | s4q03 | high | blocked_raw_package_not_received |
| missing_skip_units_recall | total_consumption_or_income | hh2p1_s4;p1_s4 | s4q03u | high | blocked_raw_package_not_received |
| missing_skip_units_recall | oop_health_expenditure | hh2p2_s9 | s9q22b | high | blocked_raw_package_not_received |
| missing_skip_units_recall | oop_health_expenditure | hh2p3_s16 | s16q35b | high | blocked_raw_package_not_received |
| missing_skip_units_recall | health_need | hh2_mortality;pi_mortality | mq04 | high | blocked_raw_package_not_received |
| missing_skip_units_recall | health_need | hh2_mortality;pi_mortality | mq06_1 | high | blocked_raw_package_not_received |
| missing_skip_units_recall | care_or_barrier | hh2_cmty | ccq42_n | high | blocked_raw_package_not_received |
| missing_skip_units_recall | care_or_barrier | hh2_cmty | ccq42_u | high | blocked_raw_package_not_received |
| missing_skip_units_recall | survey_timing | hh2_mortality | mq25c | high | blocked_raw_package_not_received |
| missing_skip_units_recall | survey_timing | hh2_tf | tfq6_c1 | high | blocked_raw_package_not_received |
| missing_skip_units_recall | climate_geography | hh2_mkts_hlthfac | cq5e1 | high | blocked_raw_package_not_received |
| missing_skip_units_recall | climate_geography | hh2_mkts_hlthfac | cq5e2 | high | blocked_raw_package_not_received |

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
