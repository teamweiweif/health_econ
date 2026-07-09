# ALB_2005 Harmonization Value Decision Audit

Status: fail-closed interpretation layer. This audit classifies ALB_2005 gate blockers from source-derived evidence but does not pass any value audit row or write any analytical data to `data/`.

## Bottom Line

- Recipe-ready rows from this audit: 0.
- Required rows still blocked: 16 of 16.
- Binding blockers: no verified household interview month/date, no GPS or full-coverage climate-ready geography, unresolved OOP aggregation/recall/skip patterns, unresolved denominator units for consumption components, and unresolved key/design review.
- Specific correction: `m10_q13a/m10_q13b` remain rejected as birth-weight variables; `weight_retro` is a future household-weight candidate only after design and merge review.

## Summary Metrics

| Metric | Value | Interpretation |
|---|---:|---|
| alb2005_harmonization_value_decision_rows | 43 | Rows in the ALB_2005 harmonization value decision audit. |
| alb2005_harmonization_value_decision_required_rows | 16 | Gate rows marked required for the minimum recipe. |
| alb2005_harmonization_value_decision_recommended_rows | 21 | Gate rows marked recommended but not minimum requirements. |
| alb2005_harmonization_value_decision_optional_rows | 6 | Gate rows marked optional or not required. |
| alb2005_harmonization_value_decision_recipe_ready_rows | 0 | Rows promoted to a verified harmonization recipe by this decision audit. |
| alb2005_harmonization_value_decision_required_blocked_rows | 16 | Required rows that remain blocked after source-derived ALB_2005 review. |
| alb2005_harmonization_value_decision_manual_future_candidate_rows | 4 | Rows that may become recipe candidates only after manual key, unit, period, or design review. |
| alb2005_harmonization_value_decision_false_positive_rows | 2 | Rows explicitly blocked because current gate candidates include known false positives. |
| alb2005_harmonization_value_decision_timing_geography_hard_blocker_rows | 10 | Rows blocked by missing interview timing or insufficient geography/GPS evidence. |
| alb2005_harmonization_value_decision_current_decision | blocked_no_alb2005_value_decision_ready_for_recipe | Fail-closed decision for ALB_2005 value interpretation and recipe promotion. |
| alb2005_documented_evidence_rows_used | 44 | Rows read from the documented ALB_2005 harmonization review. |
| alb2005_household_core_recipe_ready_rows_observed | 0 | Recipe-ready rows observed in the temp-only household-core audit. |
| alb2005_provisional_outcome_ready_rows_observed | 0 | Outcome-ready rows observed in the provisional outcome audit. |
| alb2005_outcome_semantics_outcome_ready_rows_observed | 0 | Outcome-ready rows observed in the raw semantics audit. |
| alb2005_outcome_semantics_sdg382_ready_rows_observed | 0 | SDG 3.8.2-ready rows observed in the raw semantics audit. |
| alb2005_timing_geography_climate_linkage_ready_rows_observed | 0 | Climate-linkage-ready rows observed in the ALB_2005 timing/geography audit. |
| alb2005_legacy_questionnaire_verified_timing_rows_observed | 0 | ALB_2005 raw household interview timing rows observed by the legacy questionnaire timing audit. |
| alb2005_harmonization_value_decision_concept_care_or_barrier | 6 | ALB_2005 value-decision rows by concept. |
| alb2005_harmonization_value_decision_concept_climate_geography | 7 | ALB_2005 value-decision rows by concept. |
| alb2005_harmonization_value_decision_concept_demographics | 9 | ALB_2005 value-decision rows by concept. |
| alb2005_harmonization_value_decision_concept_health_need | 1 | ALB_2005 value-decision rows by concept. |
| alb2005_harmonization_value_decision_concept_household_id | 1 | ALB_2005 value-decision rows by concept. |
| alb2005_harmonization_value_decision_concept_insurance | 1 | ALB_2005 value-decision rows by concept. |
| alb2005_harmonization_value_decision_concept_oop_health_expenditure | 1 | ALB_2005 value-decision rows by concept. |
| alb2005_harmonization_value_decision_concept_psu_cluster | 2 | ALB_2005 value-decision rows by concept. |
| alb2005_harmonization_value_decision_concept_shocks_or_livelihood | 5 | ALB_2005 value-decision rows by concept. |
| alb2005_harmonization_value_decision_concept_strata | 1 | ALB_2005 value-decision rows by concept. |
| alb2005_harmonization_value_decision_concept_survey_timing | 3 | ALB_2005 value-decision rows by concept. |
| alb2005_harmonization_value_decision_concept_survey_weight | 2 | ALB_2005 value-decision rows by concept. |
| alb2005_harmonization_value_decision_concept_total_consumption_or_income | 4 | ALB_2005 value-decision rows by concept. |
| alb2005_harmonization_value_decision_role_optional_not_minimum_recipe | 6 | ALB_2005 value-decision rows by minimum recipe role. |
| alb2005_harmonization_value_decision_role_recommended_quality_or_design_item | 21 | ALB_2005 value-decision rows by minimum recipe role. |
| alb2005_harmonization_value_decision_role_required_hard_blocker | 16 | ALB_2005 value-decision rows by minimum recipe role. |
| alb2005_harmonization_value_decision_status_blocked_access_denominator_skip_patterns | 6 | ALB_2005 value-decision rows by decision status. |
| alb2005_harmonization_value_decision_status_blocked_component_scope_not_verified | 2 | ALB_2005 value-decision rows by decision status. |
| alb2005_harmonization_value_decision_status_blocked_false_positive_birth_weight_no_person_weight_ready | 1 | ALB_2005 value-decision rows by decision status. |
| alb2005_harmonization_value_decision_status_blocked_false_positive_gate_candidate_weight_retro_requires_design_review | 1 | ALB_2005 value-decision rows by decision status. |
| alb2005_harmonization_value_decision_status_blocked_income_variable_not_verified | 1 | ALB_2005 value-decision rows by decision status. |
| alb2005_harmonization_value_decision_status_blocked_missing_interview_timing | 3 | ALB_2005 value-decision rows by decision status. |
| alb2005_harmonization_value_decision_status_blocked_need_denominator_skip_patterns | 1 | ALB_2005 value-decision rows by decision status. |
| alb2005_harmonization_value_decision_status_blocked_oop_aggregation_recall_skip_patterns | 1 | ALB_2005 value-decision rows by decision status. |
| alb2005_harmonization_value_decision_status_blocked_partial_geography_no_gps_or_timing | 7 | ALB_2005 value-decision rows by decision status. |
| alb2005_harmonization_value_decision_status_candidate_for_manual_cluster_design_review_not_climate_linkage | 2 | ALB_2005 value-decision rows by decision status. |
| alb2005_harmonization_value_decision_status_candidate_for_manual_key_review_not_recipe_ready | 1 | ALB_2005 value-decision rows by decision status. |
| alb2005_harmonization_value_decision_status_candidate_for_manual_unit_period_review_not_recipe_ready | 1 | ALB_2005 value-decision rows by decision status. |
| alb2005_harmonization_value_decision_status_optional_absent_not_minimum_recipe_blocker | 1 | ALB_2005 value-decision rows by decision status. |
| alb2005_harmonization_value_decision_status_optional_mechanism_covariate_review_not_minimum_recipe | 5 | ALB_2005 value-decision rows by decision status. |
| alb2005_harmonization_value_decision_status_recommended_absent_not_minimum_recipe_blocker | 1 | ALB_2005 value-decision rows by decision status. |
| alb2005_harmonization_value_decision_status_recommended_demographics_absent_not_minimum_recipe_blocker | 9 | ALB_2005 value-decision rows by decision status. |

## Decision Status Counts

| Decision status | Count |
|---|---:|
| recommended_demographics_absent_not_minimum_recipe_blocker | 9 |
| blocked_partial_geography_no_gps_or_timing | 7 |
| blocked_access_denominator_skip_patterns | 6 |
| optional_mechanism_covariate_review_not_minimum_recipe | 5 |
| blocked_missing_interview_timing | 3 |
| blocked_component_scope_not_verified | 2 |
| candidate_for_manual_cluster_design_review_not_climate_linkage | 2 |
| candidate_for_manual_key_review_not_recipe_ready | 1 |
| blocked_oop_aggregation_recall_skip_patterns | 1 |
| candidate_for_manual_unit_period_review_not_recipe_ready | 1 |
| blocked_income_variable_not_verified | 1 |
| blocked_need_denominator_skip_patterns | 1 |
| optional_absent_not_minimum_recipe_blocker | 1 |
| recommended_absent_not_minimum_recipe_blocker | 1 |
| blocked_false_positive_gate_candidate_weight_retro_requires_design_review | 1 |
| blocked_false_positive_birth_weight_no_person_weight_ready | 1 |

## Concept Counts

| Concept | Count |
|---|---:|
| demographics | 9 |
| climate_geography | 7 |
| care_or_barrier | 6 |
| shocks_or_livelihood | 5 |
| total_consumption_or_income | 4 |
| survey_timing | 3 |
| psu_cluster | 2 |
| survey_weight | 2 |
| household_id | 1 |
| oop_health_expenditure | 1 |
| health_need | 1 |
| insurance | 1 |
| strata | 1 |

## Required Gate Rows

| concept | harmonized_variable | candidate_evidence_status | decision_status | ready_for_recipe | blocking_reason |
|---|---|---|---|---|---|
| climate_geography | admin1 | partial_district_or_cluster_key_without_full_coverage_or_timing | blocked_partial_geography_no_gps_or_timing | 0 | ALB_2005 has partial current district evidence and cluster-like keys, but no GPS, no full-coverage climate-... |
| climate_geography | admin2 | partial_district_or_cluster_key_without_full_coverage_or_timing | blocked_partial_geography_no_gps_or_timing | 0 | ALB_2005 has partial current district evidence and cluster-like keys, but no GPS, no full-coverage climate-... |
| climate_geography | cluster_id | partial_district_or_cluster_key_without_full_coverage_or_timing | blocked_partial_geography_no_gps_or_timing | 0 | ALB_2005 has partial current district evidence and cluster-like keys, but no GPS, no full-coverage climate-... |
| climate_geography | geolocation_quality | partial_district_or_cluster_key_without_full_coverage_or_timing | blocked_partial_geography_no_gps_or_timing | 0 | ALB_2005 has partial current district evidence and cluster-like keys, but no GPS, no full-coverage climate-... |
| climate_geography | latitude | no_gps_or_coordinate_candidate | blocked_partial_geography_no_gps_or_timing | 0 | ALB_2005 has partial current district evidence and cluster-like keys, but no GPS, no full-coverage climate-... |
| climate_geography | longitude | no_gps_or_coordinate_candidate | blocked_partial_geography_no_gps_or_timing | 0 | ALB_2005 has partial current district evidence and cluster-like keys, but no GPS, no full-coverage climate-... |
| climate_geography | rural | partial_district_or_cluster_key_without_full_coverage_or_timing | blocked_partial_geography_no_gps_or_timing | 0 | ALB_2005 has partial current district evidence and cluster-like keys, but no GPS, no full-coverage climate-... |
| household_id | hhid | documented_household_key_candidate_requires_cardinality_review | candidate_for_manual_key_review_not_recipe_ready | 0 | Household ID variables are documented, but cross-file uniqueness, merge cardinality, and module coverage st... |
| oop_health_expenditure | oop_health_expenditure | documented_payment_items_require_aggregation_recall_skip_review | blocked_oop_aggregation_recall_skip_patterns | 0 | Payment variables exist, but item scope, gift inclusion, recall periods, missing/zero coding, person-to-hou... |
| survey_timing | interview_date | no_verified_raw_interview_month_or_date | blocked_missing_interview_timing | 0 | No verified ALB_2005 household interview month/date exists, and questionnaire form-design cells cannot defi... |
| survey_timing | survey_month | no_verified_raw_interview_month_or_date | blocked_missing_interview_timing | 0 | No verified ALB_2005 household interview month/date exists, and questionnaire form-design cells cannot defi... |
| survey_timing | survey_year | no_verified_raw_interview_month_or_date | blocked_missing_interview_timing | 0 | No verified ALB_2005 household interview month/date exists, and questionnaire form-design cells cannot defi... |
| total_consumption_or_income | food_consumption | component_or_per_capita_measure_requires_unit_scope_review | blocked_component_scope_not_verified | 0 | Food/nonfood components are not verified as direct household totals and cannot be promoted from the current... |
| total_consumption_or_income | nonfood_consumption | component_or_per_capita_measure_requires_unit_scope_review | blocked_component_scope_not_verified | 0 | Food/nonfood components are not verified as direct household totals and cannot be promoted from the current... |
| total_consumption_or_income | total_consumption | documented_totcons_candidate_requires_unit_period_review | candidate_for_manual_unit_period_review_not_recipe_ready | 0 | The survey total-consumption aggregate exists, but old/new lek scaling, period, household-total interpretat... |
| total_consumption_or_income | total_income | no_verified_total_income_candidate | blocked_income_variable_not_verified | 0 | The gate match reflects consumption evidence, not a verified income aggregate. |

## Manual Review Candidates

These rows are not ready. They only identify where future manual review could focus if the timing/geography blockers are later resolved.

| concept | harmonized_variable | candidate_evidence_status | decision_status | next_action |
|---|---|---|---|---|
| household_id | hhid | documented_household_key_candidate_requires_cardinality_review | candidate_for_manual_key_review_not_recipe_ready | Verify household uniqueness and joins across poverty, health, filters, roster, and weight files. |
| total_consumption_or_income | total_consumption | documented_totcons_candidate_requires_unit_period_review | candidate_for_manual_unit_period_review_not_recipe_ready | Confirm local-currency unit, price basis, period, missing rules, and household-total interpretation before ... |
| psu_cluster | cluster_id | psu_cluster_key_candidate_requires_design_review | candidate_for_manual_cluster_design_review_not_climate_linkage | Verify PSU meaning, merge consistency, variance-cluster suitability, and whether any official cluster geogr... |
| psu_cluster | psu | psu_cluster_key_candidate_requires_design_review | candidate_for_manual_cluster_design_review_not_climate_linkage | Verify PSU meaning, merge consistency, variance-cluster suitability, and whether any official cluster geogr... |

## Machine-Readable Outputs

- `temp/alb2005_harmonization_value_decision_audit.csv`
- `result/alb2005_harmonization_value_decision_summary.csv`
