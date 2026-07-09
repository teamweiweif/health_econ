# ALB_2002 Analysis Candidate Readiness Audit

Status: temp-only joined analysis-candidate audit. This creates `temp/alb2002_analysis_candidate_dataset.csv` from the ALB_2002 household core and temp CHE candidate outcomes. It does not write `data/`, does not declare a harmonized household dataset ready, and does not create climate-linked data.

## Summary

| metric | value | interpretation |
|---|---|---|
| alb2002_analysis_candidate_rows | 3599 | Temp-only joined ALB_2002 analysis-candidate household rows. |
| alb2002_analysis_candidate_columns | 49 | Columns in the temp-only ALB_2002 analysis-candidate dataset. |
| alb2002_analysis_candidate_lineage_rows | 6 | Lineage rows for carried or derived analysis-candidate fields. |
| alb2002_analysis_candidate_audit_rows | 12 | Readiness gate rows for the ALB_2002 analysis candidate. |
| alb2002_analysis_candidate_complete_candidate_gates | 9 | Field families with complete observed candidate coverage, still not promoted. |
| alb2002_analysis_candidate_missing_gates | 1 | Field families with missing required candidate coverage. |
| alb2002_analysis_candidate_blocked_promotion_gates | 2 | Promotion gates still blocked. |
| alb2002_analysis_candidate_household_core_rows | 3599 | Upstream household-core rows consumed. |
| alb2002_analysis_candidate_che10_rows | 824 | CHE10 candidate rows carried from the temp-only outcome audit. |
| alb2002_analysis_candidate_che25_rows | 290 | CHE25 candidate rows carried from the temp-only outcome audit. |
| alb2002_analysis_candidate_outcome_promotion_ready_rows | 0 | Rows ready for final outcome promotion; should remain zero. |
| alb2002_analysis_candidate_harmonized_ready_rows | 0 | Rows ready for harmonized dataset promotion; should remain zero. |
| alb2002_analysis_candidate_climate_linkage_ready_rows | 0 | Rows ready for climate linkage; should remain zero. |
| alb2002_analysis_candidate_data_write_ready_rows | 0 | Rows allowed to be written under data/ by this audit; intentionally zero. |
| alb2002_analysis_candidate_current_decision | blocked_alb2002_analysis_candidate_not_promoted_due_recipe_outcome_climate_gates | Current fail-closed decision for the ALB_2002 analysis candidate. |

## Readiness Gates

| gate_id | field_family | candidate_rows | complete_rows | missing_rows | candidate_status | promotion_ready_rows | blocking_reason |
|---|---|---|---|---|---|---|---|
| identity_keys | identity | 3599 | 3599 | 0 | candidate_complete | 0 |  |
| survey_design | weights_design | 3599 | 3599 | 0 | candidate_complete_not_promoted | 0 | Weight/design semantics and variance-use rules still need acceptance. |
| interview_timing | timing | 3599 | 3599 | 0 | candidate_complete_not_promoted | 0 | Timing values are observed, but exposure-window rules still need climate-linkage review. |
| admin_geography | admin_geography | 3599 | 3599 | 0 | candidate_complete_not_promoted | 0 | Admin geography is observed but no verified 2001/2002 district boundary or coordinates are accepted. |
| point_coordinates | coordinates | 3599 | 0 | 3599 | missing | 0 | No raw coordinate values are present in the local ALB_2002 artifacts. |
| demographics | covariates | 3599 | 3599 | 0 | candidate_complete_not_promoted | 0 | Covariates are visible but require final harmonization lineage acceptance. |
| consumption_denominator | financial_denominator | 3599 | 3599 | 0 | candidate_complete_not_promoted | 0 | Total-budget candidate is observed, but SDG 3.8.2 discretionary-budget and benchmark inputs remain unresolved. |
| oop_outcomes | financial_outcomes | 3599 | 3599 | 0 | candidate_complete_not_promoted | 0 | CHE outcomes are temp-only mixed-recall candidates, not final promoted outcomes. |
| access_outcomes | access_outcomes | 3599 | 3599 | 0 | candidate_complete_not_promoted | 0 | Access/need indicators are candidate composites with unresolved denominator and skip-path semantics. |
| composite_uhc | composite_outcomes | 3599 | 3599 | 0 | candidate_complete_not_promoted | 0 | Composite outcomes combine two unpromoted candidate families. |
| harmonized_dataset_promotion | promotion | 3599 | 3599 | 0 | blocked | 0 | This joined ALB_2002 candidate assembles household core, weights, timing, admin geography, access signals, and temp-only CHE10/CHE25 candidates, but it remai... |
| climate_dataset_promotion | promotion | 3599 | 3599 | 0 | blocked | 0 | This joined ALB_2002 candidate assembles household core, weights, timing, admin geography, access signals, and temp-only CHE10/CHE25 candidates, but it remai... |

## Lineage

| lineage_id | harmonized_field | source_fields | status | blocking_reason |
|---|---|---|---|---|
| lineage_001 | identity/timing/design fields | hhid;survey_year;survey_month;interview_date;household_weight;stratum;psu | candidate_not_promoted | Household core is temp-only until minimum recipe promotion passes. |
| lineage_002 | admin2/admin2_code | district_name_identification;district_code_identification | candidate_not_promoted | Boundary provenance and historical district crosswalk remain unresolved. |
| lineage_003 | demographic covariates | household_size;children_under5;children_under15;elderly_60plus;head_sex;head_age | candidate_not_promoted | Covariates are not promoted until the dataset recipe is accepted. |
| lineage_004 | financial protection candidates | oop_combined_monthly_equivalent;oop_share_total_budget_candidate;che10_total_budget_candidate;che25_total_budget_candidate | candidate_not_promoted | Outcome and benchmark gates remain unresolved. |
| lineage_005 | access outcome candidates | illness_or_disability_any;sudden_illness_4w_any;delayed_help_any;hospital_referral_not_gone_any;delay_reason_cost;not_gone_reason_cost;delay_reason_distance;... | candidate_not_promoted | Access/need denominator, skip semantics, and low-event-rate review remain unresolved. |
| lineage_006 | composite UHC candidates | che10_total_budget_candidate;che25_total_budget_candidate;delayed_or_unmet_care_candidate | candidate_not_promoted | Composite outcomes cannot be promoted while component outcomes remain unpromoted. |

## Interpretation

- The temp analysis candidate gives one joined ALB_2002 row per household for downstream inspection.
- Identity, timing, admin geography, weights, demographic covariates, total-budget denominator candidates, candidate CHE outcomes, and access composites are visible at household level.
- Point coordinates are absent, and admin geography remains blocked until historical district boundary or equivalent geography evidence is accepted.
- No row is promoted to `data/harmonized_household.csv`, `data/household_outcomes.csv`, or `data/climate_linked_household.csv`.

## Machine-Readable Outputs

- `temp/alb2002_analysis_candidate_dataset.csv`
- `temp/alb2002_analysis_candidate_lineage.csv`
- `result/alb2002_analysis_candidate_readiness_audit.csv`
- `result/alb2002_analysis_candidate_readiness_summary.csv`
