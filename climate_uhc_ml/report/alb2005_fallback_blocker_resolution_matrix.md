# ALB_2005 Fallback Blocker Resolution Matrix

Status: fail-closed fallback-resolution matrix. This consolidates ALB_2005 raw-package, timing, geography, outcome, and first-analysis promotion evidence into one decision. It does not write `data/`, does not promote ALB_2005 as a fallback analysis wave, and does not treat public fieldwork/GPS claims or diary-date metadata as household-level climate-linkage evidence.

## Summary

| Metric | Value | Interpretation |
|---|---:|---|
| alb2005_fallback_blocker_resolution_rows | 12 | ALB_2005 fallback blocker rows consolidated. |
| alb2005_fallback_blocker_raw_package_rows | 1 | Raw-package blocker rows in the matrix. |
| alb2005_fallback_blocker_timing_rows | 3 | Timing blocker rows in the matrix. |
| alb2005_fallback_blocker_geography_rows | 2 | Geography blocker rows in the matrix. |
| alb2005_fallback_blocker_outcome_rows | 3 | Outcome blocker rows in the matrix. |
| alb2005_fallback_blocker_promotion_gate_rows | 3 | Promotion-gate rows in the matrix. |
| alb2005_fallback_blocker_hard_blocked_rows | 12 | Rows hard-blocked from fallback promotion. |
| alb2005_fallback_blocker_harmonized_ready_rows | 0 | Rows ready for harmonized data promotion; intentionally zero. |
| alb2005_fallback_blocker_outcome_ready_rows | 0 | Rows ready for outcome promotion; intentionally zero. |
| alb2005_fallback_blocker_interview_timing_ready_rows | 0 | Rows with verified interview timing; intentionally zero. |
| alb2005_fallback_blocker_geography_ready_rows | 0 | Rows with promoted geography; intentionally zero. |
| alb2005_fallback_blocker_climate_linkage_ready_rows | 0 | Rows ready for climate linkage; intentionally zero. |
| alb2005_fallback_blocker_data_write_ready_rows | 0 | Rows allowed for data/ writes by this matrix; intentionally zero. |
| alb2005_fallback_blocker_current_decision | blocked_alb2005_no_fallback_ready | Current consolidated ALB_2005 fallback decision. |

## Blocker Matrix

| blocker_id | blocker_family | evidence_rows | promotion_status | harmonized_ready_rows | outcome_ready_rows | interview_timing_ready_rows | geography_ready_rows | climate_linkage_ready_rows | data_write_ready_rows |
|---|---|---|---|---|---|---|---|---|---|
| minimum_recipe_gate_checklist | promotion_gate | 10 | hard_blocked_minimum_recipe_not_ready | 0 | 0 | 0 | 0 | 0 | 0 |
| missing_critical_modules | raw_package | 8 | hard_blocked_missing_bookmetadata_food_diary | 0 | 0 | 0 | 0 | 0 | 0 |
| public_fieldwork_period_metadata | timing | 5 | hard_blocked_context_only_not_household_timing | 0 | 0 | 0 | 0 | 0 | 0 |
| diary_timing_metadata_candidates | timing | 11 | hard_blocked_diary_metadata_without_raw_bookmetadata | 0 | 0 | 0 | 0 | 0 | 0 |
| raw_household_interview_timing | timing | 0 | hard_blocked_no_verified_interview_timing | 0 | 0 | 0 | 0 | 0 | 0 |
| public_gps_claims | geography | 3 | hard_blocked_public_gps_claim_no_raw_values | 0 | 0 | 0 | 0 | 0 | 0 |
| partial_current_geography | geography | 329 | hard_blocked_partial_geography_no_crosswalk | 0 | 0 | 0 | 0 | 0 | 0 |
| consumption_denominator | outcome | 3638 | hard_blocked_denominator_unit_component_scope | 0 | 0 | 0 | 0 | 0 | 0 |
| oop_aggregation_policy | outcome | 11 | hard_blocked_oop_recall_skip_gift | 0 | 0 | 0 | 0 | 0 | 0 |
| access_need_denominator | outcome | 58 | hard_blocked_need_access_skip_patterns | 0 | 0 | 0 | 0 | 0 | 0 |
| first_analysis_fallback_promotion | promotion_gate | 4 | hard_blocked_not_fallback_promoted | 0 | 0 | 0 | 0 | 0 | 0 |
| dataset_promotion | promotion_gate | 0 | hard_blocked_no_harmonized_or_climate_dataset | 0 | 0 | 0 | 0 | 0 | 0 |

## Interpretation

- ALB_2005 has household rows, positive total-consumption values, positive OOP sums, weights, public fieldwork metadata, public GPS-collection claims, and diary-date metadata leads.
- The local archive and extracted package are missing `bookmetadata_cl`, five food-diary modules, and coordinate evidence, so the diary and GPS leads cannot be promoted.
- Household interview timing remains unverified, current geography is partial/no-GPS, and denominator/OOP/access semantics still need manual unit, recall-period, skip-pattern, and payment-scope review.
- First-analysis fallback promotion remains blocked because harmonized-ready, outcome-ready, timing-ready, geography-ready, climate-linkage-ready, and data-write-ready rows are all zero.

## Required Resolution

ALB_2005 can become a fallback analysis wave only after the missing module/source evidence is obtained or officially substituted, household timing is verified, geography/GPS or an accepted admin crosswalk is promoted, and outcome policies pass. Until then, no `data/` artifact, final UHC outcome, climate exposure, descriptive diagnostic, model, or policy-learning step should use ALB_2005.

## Machine-Readable Outputs

- `temp/alb2005_fallback_blocker_resolution_matrix.csv`
- `result/alb2005_fallback_blocker_resolution_summary.csv`
