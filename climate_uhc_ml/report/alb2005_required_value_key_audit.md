# ALB_2005 Required Value/Key Audit

Status: fail-closed raw value/key evidence audit. This audit reads ALB_2005 local raw SPSS files and records key coverage, candidate value distributions, value labels, and hard blockers for the minimum harmonization recipe. It does not write `data/`, does not construct validated outcomes, and does not promote any row to a recipe.

## Bottom Line

- Raw values are visible for household keys, total consumption, poverty weights, health payment items, selected access-barrier variables, and partial district codes.
- Recipe-ready rows from this audit: 0.
- Binding blockers remain: no verified household interview month/date, no GPS/coordinate variable, partial district coverage, unresolved OOP aggregation and recall semantics, unresolved consumption unit/period interpretation, and survey-design review.
- Current decision: `blocked_alb2005_required_values_seen_but_recipe_not_ready`.

## Summary

| Metric | Value | Interpretation |
|---|---:|---|
| alb2005_required_value_key_audit_rows | 26 | Rows in the ALB_2005 required value/key audit. |
| alb2005_required_value_key_recipe_ready_rows | 0 | Rows promoted to a harmonization recipe by this audit; intentionally zero. |
| alb2005_required_value_key_not_promoted_rows | 26 | Rows kept fail-closed after raw value/key inspection. |
| alb2005_required_value_key_base_households | 3840 | Base household rows from filters_cl.sav. |
| alb2005_required_value_key_total_consumption_nonmissing_rows | 3638 | Nonmissing totcons values in poverty.sav. |
| alb2005_required_value_key_oop_4w_household_positive_rows | 2679 | Audit-only households with positive four-week OOP sum. |
| alb2005_required_value_key_oop_12m_household_positive_rows | 2231 | Audit-only households with positive twelve-month OOP sum. |
| alb2005_required_value_key_district_code_nonmissing_rows | 329 | Nonmissing partial district-code rows in filters.sav. |
| alb2005_required_value_key_interview_timing_verified_rows | 0 | Verified household interview timing rows. |
| alb2005_required_value_key_coordinate_ready_rows | 0 | Verified GPS/coordinate rows ready for climate linkage; intentionally zero. |
| alb2005_required_value_key_climate_linkage_ready_rows | 0 | Rows ready for climate linkage after this audit; intentionally zero. |
| alb2005_required_value_key_current_decision | blocked_alb2005_required_values_seen_but_recipe_not_ready | Current fail-closed decision for ALB_2005 value/key evidence. |
| alb2005_value_decision_recipe_ready_rows_observed | 0 | Recipe-ready rows observed in the upstream value-decision audit. |
| alb2005_value_decision_required_blocked_rows_observed | 16 | Required blocked rows observed in the upstream value-decision audit. |
| alb2005_required_value_key_concept_care_or_barrier | 7 | Rows by audit concept. |
| alb2005_required_value_key_concept_climate_geography | 4 | Rows by audit concept. |
| alb2005_required_value_key_concept_household_id | 2 | Rows by audit concept. |
| alb2005_required_value_key_concept_oop_health_expenditure | 5 | Rows by audit concept. |
| alb2005_required_value_key_concept_survey_timing | 1 | Rows by audit concept. |
| alb2005_required_value_key_concept_survey_weight | 3 | Rows by audit concept. |
| alb2005_required_value_key_concept_total_consumption_or_income | 4 | Rows by audit concept. |
| alb2005_required_value_key_coverage_blocked_no_gps_or_coordinate_variable | 1 | Rows by coverage status. |
| alb2005_required_value_key_coverage_blocked_no_verified_household_interview_month_or_date | 1 | Rows by coverage status. |
| alb2005_required_value_key_coverage_blocked_no_verified_total_income_candidate | 1 | Rows by coverage status. |
| alb2005_required_value_key_coverage_complete_base_key_coverage_value_review_required | 4 | Rows by coverage status. |
| alb2005_required_value_key_coverage_household_aggregate_computed_for_audit_only | 2 | Rows by coverage status. |
| alb2005_required_value_key_coverage_household_module_complete_base_coverage | 6 | Rows by coverage status. |
| alb2005_required_value_key_coverage_partial_base_key_coverage_value_review_required | 2 | Rows by coverage status. |
| alb2005_required_value_key_coverage_partial_household_geography | 2 | Rows by coverage status. |
| alb2005_required_value_key_coverage_person_level_health_file_complete_base_coverage | 2 | Rows by coverage status. |
| alb2005_required_value_key_coverage_poverty_rows_partial_base_coverage | 4 | Rows by coverage status. |
| alb2005_required_value_key_coverage_psu_level_weight_file_seen | 1 | Rows by coverage status. |
| alb2005_required_value_key_value_status_absent_not_climate_exposure_ready | 1 | Rows by value status. |
| alb2005_required_value_key_value_status_absent_not_climate_ready | 1 | Rows by value status. |
| alb2005_required_value_key_value_status_absent_not_substitutable_with_consumption | 1 | Rows by value status. |
| alb2005_required_value_key_value_status_audit_only_household_sum_not_analysis_ready | 2 | Rows by value status. |
| alb2005_required_value_key_value_status_categorical_values_seen_skip_pattern_review_required | 6 | Rows by value status. |
| alb2005_required_value_key_value_status_key_values_seen_cardinality_review_required | 6 | Rows by value status. |
| alb2005_required_value_key_value_status_raw_component_seen_scope_review_required | 2 | Rows by value status. |
| alb2005_required_value_key_value_status_raw_partial_district_code_seen_not_climate_ready | 1 | Rows by value status. |
| alb2005_required_value_key_value_status_raw_partial_district_name_seen_not_climate_ready | 1 | Rows by value status. |
| alb2005_required_value_key_value_status_raw_person_payment_values_seen_aggregation_review_required | 2 | Rows by value status. |
| alb2005_required_value_key_value_status_raw_psu_weight_seen_design_review_required | 1 | Rows by value status. |
| alb2005_required_value_key_value_status_raw_total_consumption_seen_unit_period_review_required | 1 | Rows by value status. |
| alb2005_required_value_key_value_status_raw_weight_seen_design_review_required | 1 | Rows by value status. |

## Key Coverage Rows

| concept | harmonized_variable | source_file | raw_variables | row_count | distinct_key_count | duplicate_key_rows | base_rows_matched | base_match_rate | coverage_status |
|---|---|---|---|---|---|---|---|---|---|
| household_id | hhid | filters_cl.sav | M0_Q00;M0_Q01;HHID | 3840 | 3840 | 0 | 3840 | 1.000000 | complete_base_key_coverage_value_review_required |
| household_id | hhid | poverty.sav | PSU;hh | 3638 | 3638 | 0 | 3638 | 0.947396 | partial_base_key_coverage_value_review_required |
| survey_weight | household_weight | Weight_retro_2005.sav | psu;weight_retro | 480 | 480 | 0 | 480 | 1.000000 | complete_base_key_coverage_value_review_required |
| oop_health_expenditure | oop_health_expenditure | Modul_9A_healtha_cl.sav | hhid | 17302 | 3840 | 13462 | 3840 | 1.000000 | complete_base_key_coverage_value_review_required |
| care_or_barrier | care_access_barriers | Modul_9B_healthb_cl.sav | hhid | 3840 | 3840 | 0 | 3840 | 1.000000 | complete_base_key_coverage_value_review_required |
| climate_geography | admin2 | filters.sav | P0_Q00;P0_Q01;P11_Q5A;P11_Q5B | 1899 | 1899 | 0 | 1899 | 0.494531 | partial_base_key_coverage_value_review_required |

## Value Evidence Rows

| concept | harmonized_variable | source_file | raw_variables | nonmissing_rows | positive_numeric_rows | max_value | top_values | value_status |
|---|---|---|---|---|---|---|---|---|
| total_consumption_or_income | total_consumption | poverty.sav | totcons | 3638 | 3638 | 5.45599e+06 | 328946:2; 429120:2; 354944:2; 287612:2; 299979:2; 451099:2; 358640:2; 395105:2 | raw_total_consumption_seen_unit_period_review_required |
| total_consumption_or_income | food_consumption | poverty.sav | rfood | 3638 | 3638 | 33028.9 | 3407.36:2; 3193.31:2; 2260.23:2; 11266.8:2; 4331.65:2; 3054.65:2; 7316.44:2; 9430.61:1 | raw_component_seen_scope_review_required |
| total_consumption_or_income | nonfood_consumption | poverty.sav | rnfood | 3638 | 3634 | 45311.8 | 0:4; 2010.76:2; 1220.34:2; 1352.45:2; 3312.82:2; 438.084:2; 3203.05:2; 2015.86:2 | raw_component_seen_scope_review_required |
| survey_weight | household_weight | poverty.sav | weight_retro | 3638 | 3638 | 574.427 | 153.462:32; 234.425:16; 233.791:16; 253.493:16; 152.442:16; 182.93:8; 133.387:8; 149.72:8 | raw_weight_seen_design_review_required |
| survey_weight | household_weight | Weight_retro_2005.sav | weight_retro | 480 | 480 | 574.427 | 81.6401:4; 153.462:4; 71.4351:3; 253.493:2; 234.425:2; 233.791:2; 152.442:2; 267.271:1 | raw_psu_weight_seen_design_review_required |
| oop_health_expenditure | oop_health_expenditure_4w_component_sum | Modul_9A_healtha_cl.sav | m9a_q16; m9a_q17; m9a_q20; m9a_q22; m9a_q23; m9a_q28; m9a_q29; m9a_q32; m9a_q34; m9a_q35; m9a_q38; m9a_q39; m9a_q41; ... | 17302 | 4220 | 620000 | 0:13082; 2000:477; 1000:338; 3000:281; 5000:268; 10000:147; 4000:145; 6000:132 | raw_person_payment_values_seen_aggregation_review_required |
| oop_health_expenditure | oop_health_expenditure_4w_household_sum_unreviewed | Modul_9A_healtha_cl.sav | m9a_q16; m9a_q17; m9a_q20; m9a_q22; m9a_q23; m9a_q28; m9a_q29; m9a_q32; m9a_q34; m9a_q35; m9a_q38; m9a_q39; m9a_q41; ... | 3840 | 2679 | 1011000 | 0:1161; 2000:207; 3000:144; 5000:136; 1000:123; 4000:99; 6000:65; 7000:65 | audit_only_household_sum_not_analysis_ready |
| oop_health_expenditure | oop_health_expenditure_12m_component_sum | Modul_9A_healtha_cl.sav | m9a_q68; m9a_q69; m9a_q71; m9a_q72; m9a_q73; m9a_q76; m9a_q77; m9a_q79; m9a_q80; m9a_q81 | 17302 | 3937 | 10600000 | 0:13365; 10000:241; 30000:209; 20000:207; 2000:159; 15000:151; 12000:146; 5000:145 | raw_person_payment_values_seen_aggregation_review_required |
| oop_health_expenditure | oop_health_expenditure_12m_household_sum_unreviewed | Modul_9A_healtha_cl.sav | m9a_q68; m9a_q69; m9a_q71; m9a_q72; m9a_q73; m9a_q76; m9a_q77; m9a_q79; m9a_q80; m9a_q81 | 3840 | 2231 | 10600000 | 0:1609; 10000:75; 20000:70; 30000:65; 50000:56; 4000:49; 15000:48; 40000:46 | audit_only_household_sum_not_analysis_ready |
| care_or_barrier | difficulty_paying_for_health | Modul_9B_healthb_cl.sav | m9b_q01 | 3840 | 3840 | 4 | 3:2174; 2:744; 1:545; 4:377 | categorical_values_seen_skip_pattern_review_required |
| care_or_barrier | delayed_help_reason | Modul_9B_healthb_cl.sav | m9b_q04 | 268 | 268 | 6 | <missing>:3572; 1:92; 4:64; 3:52; 5:51; 2:5; 6:4 | categorical_values_seen_skip_pattern_review_required |
| care_or_barrier | hospital_referral_not_gone_count | Modul_9B_healthb_cl.sav | m9b_q05 | 3463 | 3463 | 5 | 1:3281; <missing>:377; 2:137; 3:32; 5:8; 4:5 | categorical_values_seen_skip_pattern_review_required |
| care_or_barrier | hospital_referral_not_gone_reason | Modul_9B_healthb_cl.sav | m9b_q06 | 182 | 182 | 7 | <missing>:3658; 2:88; 1:56; 6:15; 5:7; 3:7; 7:5; 4:4 | categorical_values_seen_skip_pattern_review_required |
| care_or_barrier | refused_health_services | Modul_9B_healthb_cl.sav | m9b_q07 | 3840 | 3840 | 2 | 2:3697; 1:143 | categorical_values_seen_skip_pattern_review_required |
| care_or_barrier | refused_health_services_reason | Modul_9B_healthb_cl.sav | m9b_q08 | 143 | 143 | 5 | <missing>:3697; 1:85; 2:52; 4:4; 5:2 | categorical_values_seen_skip_pattern_review_required |
| climate_geography | admin2_name | filters.sav | P11_Q5A | 343 | 0 |  | <missing>:1556; LIBRAZHD:52; DIBER:32; KORCE:24; ELBASAN:24; KUKES:23; GRAMSH:21; FIER:19 | raw_partial_district_name_seen_not_climate_ready |
| climate_geography | admin2_code | filters.sav | P11_Q5B | 329 | 329 | 36 | <missing>:1570; 20:52; 5:31; 14:24; 17:23; 9:21; 7:21; 8:18 | raw_partial_district_code_seen_not_climate_ready |

## Explicit Absence Rows

| concept | harmonized_variable | coverage_status | value_status | blocking_reason |
|---|---|---|---|---|
| total_consumption_or_income | total_income | blocked_no_verified_total_income_candidate | absent_not_substitutable_with_consumption | No verified ALB_2005 total income aggregate is identified; consumption evidence must not be relabeled as income. |
| climate_geography | latitude;longitude | blocked_no_gps_or_coordinate_variable | absent_not_climate_ready | No ALB_2005 latitude, longitude, GPS, or coordinate raw variable is verified in the local extracted files. |
| survey_timing | survey_month;interview_date | blocked_no_verified_household_interview_month_or_date | absent_not_climate_exposure_ready | No verified raw household interview month/date exists for ALB_2005; recall-period and birth/event dates cannot define... |

## Interpretation

- `totcons`, `rfood`, and `rnfood` are observed in `poverty.sav`, but documentation must still verify unit, period, and household-total interpretation before financial-protection denominators are constructed.
- Health payment items are observed in `Modul_9A_healtha_cl.sav`, but four-week and twelve-month recall items must remain separate until a documented aggregation rule exists.
- Access-barrier value labels in `Modul_9B_healthb_cl.sav` contain cost and distance categories, but the denominator is conditional and must be reconstructed from questionnaire skip paths.
- `P11_Q5A/P11_Q5B` in `filters.sav` provide partial district evidence only; they are not full-coverage geography and are not a substitute for GPS or a verified 2005 boundary crosswalk.
- No verified ALB_2005 household interview timing exists, so climate exposure windows remain blocked.

## Machine-Readable Outputs

- `temp/alb2005_required_value_key_audit.csv`
- `result/alb2005_required_value_key_summary.csv`
