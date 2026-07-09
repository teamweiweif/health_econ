# ALB_2002 Limited Climate-Linked Promotion

Status: limited household-window climate-linked file promoted. This writes `data/climate_linked_household.csv` by joining the limited ALB_2002 harmonized core, limited CHE10/CHE25 outcomes, and limited NASA POWER admin2-centroid exposure windows.

The file is not descriptive-ready, model-ready, causal-ready, policy-ready, or final-analysis-ready.

## Summary

| metric | value | interpretation |
|---|---|---|
| alb2002_limited_climate_linked_promotion_audit_rows | 5 | Rows in the limited climate-linked promotion audit. |
| alb2002_limited_climate_linked_rows | 14396 | Rows written to data/climate_linked_household.csv. |
| alb2002_limited_climate_linked_household_rows | 3599 | Distinct households represented. |
| alb2002_limited_climate_linked_window_rows | 4 | Distinct exposure windows per household. |
| alb2002_limited_climate_linked_expected_rows | 14396 | Expected rows from household rows times windows. |
| alb2002_limited_climate_linked_source_household_rows | 3599 | Rows in the limited harmonized household core. |
| alb2002_limited_climate_linked_source_climate_rows | 384 | Rows in the limited climate exposure file. |
| alb2002_limited_climate_linked_climate_value_rows | 14396 | Rows with nonmissing precipitation and temperature values. |
| alb2002_limited_climate_linked_unmatched_rows | 0 | Rows without linked climate values. |
| alb2002_limited_climate_linked_che10_rows | 3296 | Long rows carrying CHE10 outcome. |
| alb2002_limited_climate_linked_che25_rows | 1160 | Long rows carrying CHE25 outcome. |
| alb2002_limited_climate_linked_combined_stress_rows | 3092 | Long rows with diagnostic combined climate-stress flag. |
| alb2002_limited_climate_linked_limited_data_write_ready_rows | 14396 | Rows allowed in data/ only under limited climate-linked scope. |
| alb2002_limited_climate_linked_sdg382_ready_rows | 0 | Rows ready for SDG 3.8.2. |
| alb2002_limited_climate_linked_access_ready_rows | 0 | Rows ready for access outcomes. |
| alb2002_limited_climate_linked_primary_chirps_ready_rows | 0 | Rows with primary CHIRPS extraction. |
| alb2002_limited_climate_linked_primary_era5_ready_rows | 0 | Rows with primary ERA5 extraction. |
| alb2002_limited_climate_linked_historical_baseline_ready_rows | 0 | Rows with historical climate baseline. |
| alb2002_limited_climate_linked_climate_linkage_ready_rows | 0 | Rows ready for final climate linkage. |
| alb2002_limited_climate_linked_descriptive_ready_rows | 0 | Rows ready for promoted descriptive diagnostics. |
| alb2002_limited_climate_linked_predictive_ml_ready_rows | 0 | Rows ready for predictive ML. |
| alb2002_limited_climate_linked_reduced_form_ready_rows | 0 | Rows ready for reduced-form estimation. |
| alb2002_limited_climate_linked_robustness_ready_rows | 0 | Rows ready for robustness checks. |
| alb2002_limited_climate_linked_final_analysis_ready_rows | 0 | Rows ready for final empirical analysis. |
| alb2002_limited_climate_linked_current_decision | limited_che_outcome_nasa_admin2_climate_linked_promoted_models_still_blocked | Current limited climate-linked promotion decision. |
| alb2002_limited_climate_linked_data_use_limit | climate_linked_che_diagnostic_only_not_for_promoted_descriptive_ml_causal_or_policy_analysis | Guardrail embedded in every output row. |

## Gate Audit

| gate_id | status | rows_passing | rows_blocked | next_action |
|---|---|---|---|---|
| limited_inputs | complete_limited_inputs | 14396 | 0 | Use only as a limited linkage diagnostic. |
| linkage_coverage | complete_limited_linkage | 14396 | 0 | Verify historical boundaries/GPS before final climate linkage. |
| outcome_scope | blocked_sdg_access_composite | 0 | 14396 | Resolve SDG/access/composite outcome gates before UHC-failure claims. |
| climate_source_baseline | blocked_primary_sources_and_baseline | 0 | 14396 | Extract CHIRPS/ERA5 and accepted historical baselines before shock interpretation. |
| downstream_models | blocked_not_analysis_ready | 0 | 14396 | Keep descriptive diagnostics and models blocked until final linked inputs pass. |

## Guardrails

- Every row carries `climate_linked_scope=alb2002_limited_che_admin2_centroid_nasa_power_window_linkage_not_final`.
- Every row carries `data_use_limit=climate_linked_che_diagnostic_only_not_for_promoted_descriptive_ml_causal_or_policy_analysis`.
- `climate_linkage_ready`, `descriptive_ready`, `predictive_ml_ready`, `reduced_form_ready`, `robustness_ready`, and `final_analysis_ready` remain zero.

## Machine-Readable Outputs

- `data/climate_linked_household.csv`
- `temp/climate_merge_audit.csv`
- `temp/alb2002_limited_climate_linked_promotion_audit.csv`
- `result/alb2002_limited_climate_linked_promotion_summary.csv`
