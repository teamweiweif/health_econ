# ALB_2002 Linked Candidate Descriptive Diagnostics

Status: temp-only descriptive screen over the blocked ALB_2002 climate/outcome linked candidate. This report is for audit readability only. It does not create a promoted descriptive diagnostic, accepted prevalence estimate, map, missingness heatmap, analysis sample, predictive feature table, or causal input.

## Summary

| Metric | Value | Interpretation |
|---|---:|---|
| alb2002_linked_candidate_descriptive_input_rows | 14396 | Input temp-only household-window rows screened. |
| alb2002_linked_candidate_descriptive_household_rows | 3599 | Deduplicated households used for household-level candidate outcome rates. |
| alb2002_linked_candidate_descriptive_window_rows | 4 | Diagnostic exposure windows represented. |
| alb2002_linked_candidate_descriptive_audit_rows | 7 | Audit rows for temp-only descriptive screen guardrails. |
| alb2002_linked_candidate_descriptive_cell_rows | 108 | Readable diagnostic cell rows written. |
| alb2002_linked_candidate_descriptive_household_outcome_cell_rows | 4 | Overall deduplicated-household candidate outcome cells. |
| alb2002_linked_candidate_descriptive_subgroup_outcome_cell_rows | 24 | Subgroup candidate outcome cells. |
| alb2002_linked_candidate_descriptive_climate_flag_cell_rows | 16 | Window-specific diagnostic climate flag cells. |
| alb2002_linked_candidate_descriptive_outcome_by_climate_flag_cell_rows | 64 | Candidate outcome-by-diagnostic-climate-flag cells. |
| alb2002_linked_candidate_descriptive_che10_or_access_households | 2004 | Deduplicated households with CHE10-or-access candidate flag. |
| alb2002_linked_candidate_descriptive_che25_or_access_households | 1889 | Deduplicated households with CHE25-or-access candidate flag. |
| alb2002_linked_candidate_descriptive_both_che10_access_households | 681 | Deduplicated households with both CHE10 and access candidate flag. |
| alb2002_linked_candidate_descriptive_coping_households | 1476 | Deduplicated households with health-cost coping candidate flag. |
| alb2002_linked_candidate_descriptive_low_rain_rows | 1008 | Long rows with diagnostic low-rain flag. |
| alb2002_linked_candidate_descriptive_extreme_wet_rows | 1398 | Long rows with diagnostic extreme-wet flag. |
| alb2002_linked_candidate_descriptive_extreme_heat_rows | 1694 | Long rows with diagnostic extreme-heat flag. |
| alb2002_linked_candidate_descriptive_combined_stress_rows | 3092 | Long rows with any diagnostic combined-stress flag. |
| alb2002_linked_candidate_descriptive_climate_linkage_ready_rows | 0 | Rows ready for promoted climate linkage; should remain zero. |
| alb2002_linked_candidate_descriptive_outcome_promotion_ready_rows | 0 | Rows ready for promoted outcomes; should remain zero. |
| alb2002_linked_candidate_descriptive_harmonized_recipe_ready_rows | 0 | Rows ready for harmonized recipe promotion; should remain zero. |
| alb2002_linked_candidate_descriptive_data_write_ready_rows | 0 | Rows allowed to be written to data/; should remain zero. |
| alb2002_linked_candidate_descriptive_source_linked_decision | blocked_alb2002_climate_outcome_linked_candidate_not_promoted_due_recipe_outcome_geography_source_baseline_gates | Upstream linked-candidate decision consumed. |
| alb2002_linked_candidate_descriptive_current_decision | blocked_alb2002_linked_candidate_descriptive_screen_not_promoted_due_unpromoted_inputs | Current temp-only descriptive screen decision. |

## Guardrail Audit

| check_id | status | rows_checked | passing_rows | promotion_ready_rows | evidence | blocking_reason |
|---|---|---|---|---|---|---|
| input_profile | complete_candidate_not_promoted | 14396 | 14396 | 0 | linked_rows=14396; deduplicated_households=3599; distinct_households=3599; windows=4 | This descriptive screen uses the temp-only ALB_2002 climate/outcome linked candidate. The linked inputs remain unpromoted becau... |
| household_window_structure | complete_candidate_not_promoted | 3599 | 3599 | 0 | min_windows_per_household=4; max_windows_per_household=4; expected_long_rows=14396 | Repeated household-window rows must not be treated as independent final observations. |
| household_outcome_screen | complete_candidate_not_promoted | 3599 | 3599 | 0 | che10_or_access_households=2004; che25_or_access_households=1889; both_che10_access_households=681; coping_households=1476 | Outcome fields are candidate screens, not final SDG/UHC outcomes. |
| climate_window_screen | complete_candidate_not_promoted | 14396 | 14396 | 0 | low_rain_rows=1008; extreme_wet_rows=1398; extreme_heat_rows=1694; combined_stress_rows=3092 | Climate flags are within-candidate NASA POWER centroid diagnostics, not accepted historical anomalies. |
| cell_output_screen | complete_candidate_not_promoted | 108 | 108 | 0 | cell_rows=108; output_cells=result/alb2002_linked_candidate_descriptive_cells.csv; output_report=report/alb2002_linked_candidat... | The cell table is a readability screen over blocked inputs. |
| weight_design_guardrail | blocked | 14396 | 0 | 0 | positive_candidate_weight_rows=14396; weight_field=household_weight; survey_design_status=not_accepted_for_inference | Weights are carried for audit visibility only; the accepted survey design and promoted analysis sample are absent. |
| promotion_gate | blocked | 14396 | 0 | 0 | readiness_positive_rows=0; decision=blocked_alb2002_linked_candidate_descriptive_screen_not_promoted_due_unpromoted_inputs | This descriptive screen uses the temp-only ALB_2002 climate/outcome linked candidate. The linked inputs remain unpromoted becau... |

## Example Diagnostic Cells

| diagnostic_scope | population | group_variable | group_value | window_months | climate_flag | outcome | rows | households | events | event_rate | candidate_weighted_rate_not_inference |
|---|---|---|---|---|---|---|---|---|---|---|---|
| household_outcome_rate | deduplicated_households | all | all |  |  | uhc_double_failure_che10_or_access_candidate | 3599 | 3599 | 2004 | 0.556821 | 0.570531 |
| household_outcome_rate | deduplicated_households | all | all |  |  | uhc_double_failure_che25_or_access_candidate | 3599 | 3599 | 1889 | 0.524868 | 0.537554 |
| household_outcome_rate | deduplicated_households | all | all |  |  | both_che10_access_candidate | 3599 | 3599 | 681 | 0.189219 | 0.195082 |
| household_outcome_rate | deduplicated_households | all | all |  |  | coping_health_cost_candidate | 3599 | 3599 | 1476 | 0.410114 | 0.434768 |
| household_outcome_rate_by_subgroup | deduplicated_households | rural | 1 |  |  | uhc_double_failure_che10_or_access_candidate | 1959 | 1959 | 924 | 0.471669 | 0.476709 |
| household_outcome_rate_by_subgroup | deduplicated_households | rural | 1 |  |  | uhc_double_failure_che25_or_access_candidate | 1959 | 1959 | 858 | 0.437979 | 0.443646 |
| household_outcome_rate_by_subgroup | deduplicated_households | rural | 1 |  |  | both_che10_access_candidate | 1959 | 1959 | 264 | 0.134763 | 0.135419 |
| household_outcome_rate_by_subgroup | deduplicated_households | rural | 1 |  |  | coping_health_cost_candidate | 1959 | 1959 | 603 | 0.30781 | 0.327039 |
| household_outcome_rate_by_subgroup | deduplicated_households | rural | 2 |  |  | uhc_double_failure_che10_or_access_candidate | 1640 | 1640 | 1080 | 0.658537 | 0.649157 |
| household_outcome_rate_by_subgroup | deduplicated_households | rural | 2 |  |  | uhc_double_failure_che25_or_access_candidate | 1640 | 1640 | 1031 | 0.628659 | 0.616253 |
| household_outcome_rate_by_subgroup | deduplicated_households | rural | 2 |  |  | both_che10_access_candidate | 1640 | 1640 | 417 | 0.254268 | 0.245081 |
| household_outcome_rate_by_subgroup | deduplicated_households | rural | 2 |  |  | coping_health_cost_candidate | 1640 | 1640 | 873 | 0.532317 | 0.525048 |
| household_outcome_rate_by_subgroup | deduplicated_households | agriculture_livelihood | 1 |  |  | uhc_double_failure_che10_or_access_candidate | 1675 | 1675 | 1087 | 0.648955 | 0.638899 |
| household_outcome_rate_by_subgroup | deduplicated_households | agriculture_livelihood | 1 |  |  | uhc_double_failure_che25_or_access_candidate | 1675 | 1675 | 1040 | 0.620896 | 0.607175 |
| household_outcome_rate_by_subgroup | deduplicated_households | agriculture_livelihood | 1 |  |  | both_che10_access_candidate | 1675 | 1675 | 415 | 0.247761 | 0.240918 |
| household_outcome_rate_by_subgroup | deduplicated_households | agriculture_livelihood | 1 |  |  | coping_health_cost_candidate | 1675 | 1675 | 859 | 0.512836 | 0.509357 |
| household_outcome_rate_by_subgroup | deduplicated_households | agriculture_livelihood | 2 |  |  | uhc_double_failure_che10_or_access_candidate | 1924 | 1924 | 917 | 0.476611 | 0.491358 |
| household_outcome_rate_by_subgroup | deduplicated_households | agriculture_livelihood | 2 |  |  | uhc_double_failure_che25_or_access_candidate | 1924 | 1924 | 849 | 0.441268 | 0.456931 |
| household_outcome_rate_by_subgroup | deduplicated_households | agriculture_livelihood | 2 |  |  | both_che10_access_candidate | 1924 | 1924 | 266 | 0.138254 | 0.142002 |
| household_outcome_rate_by_subgroup | deduplicated_households | agriculture_livelihood | 2 |  |  | coping_health_cost_candidate | 1924 | 1924 | 617 | 0.320686 | 0.34839 |
| household_outcome_rate_by_subgroup | deduplicated_households | health_insurance_candidate | 0 |  |  | uhc_double_failure_che10_or_access_candidate | 1435 | 1435 | 827 | 0.576307 | 0.601792 |
| household_outcome_rate_by_subgroup | deduplicated_households | health_insurance_candidate | 0 |  |  | uhc_double_failure_che25_or_access_candidate | 1435 | 1435 | 793 | 0.552613 | 0.576728 |
| household_outcome_rate_by_subgroup | deduplicated_households | health_insurance_candidate | 0 |  |  | both_che10_access_candidate | 1435 | 1435 | 290 | 0.202091 | 0.217562 |
| household_outcome_rate_by_subgroup | deduplicated_households | health_insurance_candidate | 0 |  |  | coping_health_cost_candidate | 1435 | 1435 | 651 | 0.453659 | 0.487017 |
| household_outcome_rate_by_subgroup | deduplicated_households | health_insurance_candidate | 1 |  |  | uhc_double_failure_che10_or_access_candidate | 2164 | 2164 | 1177 | 0.5439 | 0.550362 |
| household_outcome_rate_by_subgroup | deduplicated_households | health_insurance_candidate | 1 |  |  | uhc_double_failure_che25_or_access_candidate | 2164 | 2164 | 1096 | 0.50647 | 0.51228 |
| household_outcome_rate_by_subgroup | deduplicated_households | health_insurance_candidate | 1 |  |  | both_che10_access_candidate | 2164 | 2164 | 391 | 0.180684 | 0.180578 |
| household_outcome_rate_by_subgroup | deduplicated_households | health_insurance_candidate | 1 |  |  | coping_health_cost_candidate | 2164 | 2164 | 825 | 0.381238 | 0.401057 |
| household_window_climate_flag_rate | household_window_rows | window_months | 1 | 1 | diagnostic_low_rain_z_le_m1 |  | 3599 | 3599 | 287 | 0.0797444 | 0.0833368 |
| household_window_climate_flag_rate | household_window_rows | window_months | 1 | 1 | diagnostic_extreme_wet_z_ge_15 |  | 3599 | 3599 | 370 | 0.102806 | 0.0385881 |

## Interpretation

- Household outcome rates are computed on one deduplicated row per household.
- Climate flag rates and outcome-by-flag screens use repeated household-window rows and are not final analysis observations.
- Candidate weighted rates use `household_weight` only as a plausibility screen; survey design and promoted analysis-sample gates remain blocked.
- The underlying climate fields are within-candidate NASA POWER centroid diagnostics, not CHIRPS/ERA5 historical anomalies.
- Harmonized-recipe-ready, outcome-promotion-ready, climate-linkage-ready, and data-write-ready rows remain zero.

## Machine-Readable Outputs

- `result/alb2002_linked_candidate_descriptive_audit.csv`
- `result/alb2002_linked_candidate_descriptive_cells.csv`
- `result/alb2002_linked_candidate_descriptive_summary.csv`
