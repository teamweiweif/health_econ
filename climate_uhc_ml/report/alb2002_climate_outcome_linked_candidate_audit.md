# ALB_2002 Climate Outcome Linked Candidate Audit

Status: temp-only household-window linkage audit. This joins the ALB_2002 analysis and composite UHC outcome candidates to the within-candidate climate shock diagnostics by district and survey month. It does not write `data/`, does not create an accepted climate-linked analytical dataset, and does not support descriptive, predictive, or causal claims.

## Summary

| Metric | Value | Interpretation |
|---|---:|---|
| alb2002_climate_outcome_linked_candidate_rows | 14396 | Temp-only long household-window climate/outcome candidate rows. |
| alb2002_climate_outcome_linked_candidate_household_rows | 3599 | Distinct ALB_2002 households represented. |
| alb2002_climate_outcome_linked_candidate_window_rows | 4 | Distinct diagnostic exposure windows linked per household. |
| alb2002_climate_outcome_linked_candidate_district_month_cells | 96 | District-month cells represented after linkage. |
| alb2002_climate_outcome_linked_candidate_lineage_rows | 7 | Lineage rows for the linked climate/outcome candidate. |
| alb2002_climate_outcome_linked_candidate_audit_rows | 7 | Audit rows for linkage integrity and promotion gates. |
| alb2002_climate_outcome_linked_candidate_source_analysis_rows | 3599 | Source joined analysis-candidate rows consumed. |
| alb2002_climate_outcome_linked_candidate_source_uhc_rows | 3599 | Source composite UHC candidate rows consumed. |
| alb2002_climate_outcome_linked_candidate_source_shock_rows | 384 | Source climate shock diagnostic rows consumed. |
| alb2002_climate_outcome_linked_candidate_expected_rows | 14396 | Expected rows if every household has all diagnostic windows. |
| alb2002_climate_outcome_linked_candidate_unmatched_rows | 0 | Rows with no linked climate window; should remain zero. |
| alb2002_climate_outcome_linked_candidate_precip_z_rows | 14396 | Linked rows with diagnostic rainfall z-scores. |
| alb2002_climate_outcome_linked_candidate_temp_z_rows | 14396 | Linked rows with diagnostic temperature z-scores. |
| alb2002_climate_outcome_linked_candidate_low_rain_rows | 1008 | Linked household-window rows with diagnostic low-rain flag. |
| alb2002_climate_outcome_linked_candidate_extreme_wet_rows | 1398 | Linked household-window rows with diagnostic extreme-wet flag. |
| alb2002_climate_outcome_linked_candidate_extreme_heat_rows | 1694 | Linked household-window rows with diagnostic extreme-heat flag. |
| alb2002_climate_outcome_linked_candidate_combined_stress_rows | 3092 | Linked household-window rows with any diagnostic combined-stress flag. |
| alb2002_climate_outcome_linked_candidate_che10_or_access_rows | 8016 | Long rows carrying CHE10-or-access UHC candidate flag. |
| alb2002_climate_outcome_linked_candidate_che25_or_access_rows | 7556 | Long rows carrying CHE25-or-access UHC candidate flag. |
| alb2002_climate_outcome_linked_candidate_both_che10_access_rows | 2724 | Long rows carrying both CHE10 and access-barrier candidate flag. |
| alb2002_climate_outcome_linked_candidate_coping_rows | 5904 | Long rows carrying health-cost coping candidate flag. |
| alb2002_climate_outcome_linked_candidate_primary_chirps_ready_rows | 0 | Rows with primary CHIRPS accepted; intentionally zero. |
| alb2002_climate_outcome_linked_candidate_primary_era5_ready_rows | 0 | Rows with primary ERA5 accepted; intentionally zero. |
| alb2002_climate_outcome_linked_candidate_historical_baseline_ready_rows | 0 | Rows with historical baseline accepted; intentionally zero. |
| alb2002_climate_outcome_linked_candidate_climate_linkage_ready_rows | 0 | Rows ready for promoted climate linkage; intentionally zero. |
| alb2002_climate_outcome_linked_candidate_outcome_promotion_ready_rows | 0 | Rows ready for promoted outcomes; intentionally zero. |
| alb2002_climate_outcome_linked_candidate_harmonized_recipe_ready_rows | 0 | Rows ready for harmonized recipe promotion; intentionally zero. |
| alb2002_climate_outcome_linked_candidate_data_write_ready_rows | 0 | Rows allowed to be written to data/; intentionally zero. |
| alb2002_climate_outcome_linked_candidate_current_decision | blocked_alb2002_climate_outcome_linked_candidate_not_promoted_due_recipe_outcome_geography_source_baseline_gates | Current fail-closed linked climate/outcome candidate decision. |

## Linkage Audit

| check_id | status | rows_checked | passing_rows | promotion_ready_rows | evidence | blocking_reason |
|---|---|---|---|---|---|---|
| household_inputs | complete_candidate_not_promoted | 3599 | 3599 | 0 | analysis_rows=3599; analysis_unique_hhid=3599; uhc_rows=3599; uhc_unique_hhid=3599 | Household and outcome candidates are temp-only and not promoted. |
| climate_input_keys | complete_candidate_not_promoted | 384 | 384 | 0 | shock_rows=384; district_month_cells=96; window_rows=4; duplicate_key_rows=0 | Climate shock rows are diagnostics from NASA POWER fallback centroids, not accepted climate exposures. |
| household_window_link | complete_candidate_not_promoted | 14396 | 14396 | 0 | linked_rows=14396; expected_rows=14396; distinct_households=3599; matched_rows=14396; unmatched_rows=0 | The join is mechanically complete but remains an unpromoted stress test. |
| outcome_coverage | complete_candidate_not_promoted | 14396 | 14396 | 0 | che10_or_access_long_rows=8016; che25_or_access_long_rows=7556; coping_long_rows=5904; composite_denominator_rows=14396 | Outcome fields are candidate screens and cannot be interpreted as final UHC failure outcomes. |
| climate_diagnostic_coverage | complete_candidate_not_promoted | 14396 | 14396 | 0 | precip_z_rows=14396; temp_z_rows=14396; low_rain_long_rows=1008; extreme_wet_long_rows=1398; extreme_heat_long_rows=1694; combi... | Climate diagnostics are within-candidate z-scores, not historical local anomalies or accepted treatments. |
| geography_source_baseline_gates | blocked | 14396 | 0 | 0 | primary_chirps_ready=0; primary_era5_ready=0; historical_baseline_ready=0; climate_linkage_ready=0 | Verified historical geography, primary CHIRPS/ERA5 extraction, and historical baselines are not accepted. |
| promotion | blocked | 14396 | 0 | 0 | outcome_promotion_ready=0; harmonized_recipe_ready=0; data_write_ready=0; decision=blocked_alb2002_climate_outcome_linked_candi... | This household-window linked candidate merges temp-only ALB_2002 analysis/outcome candidates with temp-only within-candidate cl... |

## Lineage

| derived_field | source_fields | formula_or_rule | status | blocking_reason |
|---|---|---|---|---|
| household_identity_design_covariates | hhid;survey_year;survey_month;interview_date;household_weight;strata;psu;demographic covariates | Direct carry-forward from the ALB_2002 joined analysis candidate. | candidate_not_promoted | Analysis candidate remains outside data/. |
| district_code_join_key | admin2_code;district_code;survey_month | Normalize analysis admin2_code to district_code and join climate shocks by district_code and survey_month. | candidate_not_promoted | Admin2 is not verified 2001/2002 geography. |
| window_months | window_months | Expand each household to one row for each linked diagnostic exposure window. | candidate_not_promoted | Long household-window rows are a stress-test structure only. |
| candidate_uhc_outcomes | CHE, access, double-failure, financial-only, access-only, both-failure, coping fields | Carry final temp-only composite UHC candidate fields by hhid. | candidate_not_promoted | Outcome promotion gates remain blocked. |
| diagnostic_climate_shock_fields | precip/temp within-candidate z-scores and diagnostic flags | Carry shock diagnostics by district-month-window. | candidate_not_promoted | Diagnostics are not historical anomalies or accepted treatment variables. |
| promotion_gate_fields | primary_chirps_ready;primary_era5_ready;historical_baseline_ready;climate_linkage_ready;data_write_ready | Force all promotion/data-write readiness fields to zero. | blocked | Linked candidate cannot be used as promoted analysis data. |
| blocking_reason | upstream gate decisions | Record fail-closed interpretation in every linked row. | blocked | Recipe, outcome, geography, source, and baseline gates have not passed together. |

## Interpretation

- The mechanical household-window linkage is complete for ALB_2002 candidate rows.
- The linked climate fields are diagnostic within-candidate z-scores, not historical anomalies or accepted climate-shock treatments.
- The linked outcome fields are temp-only UHC candidates, not promoted final outcomes.
- Harmonized-recipe-ready, outcome-promotion-ready, climate-linkage-ready, and data-write-ready rows remain zero.

## Machine-Readable Outputs

- `temp/alb2002_climate_outcome_linked_candidate.csv`
- `temp/alb2002_climate_outcome_linked_candidate_lineage.csv`
- `result/alb2002_climate_outcome_linked_candidate_audit.csv`
- `result/alb2002_climate_outcome_linked_candidate_summary.csv`
