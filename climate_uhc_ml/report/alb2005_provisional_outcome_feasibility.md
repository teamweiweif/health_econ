# ALB_2005 Provisional Outcome Feasibility Audit

Status: provisional, temp-only, and fail-closed. This audit computes raw event-rate diagnostics from `temp/alb2005_household_core_candidate.csv` to see whether candidate ALB_2005 OOP/access fields have nonzero variation. It does not construct final UHC outcomes and does not write any file to `data/`.

## Summary

| Metric | Value | Interpretation |
|---|---:|---|
| alb2005_provisional_outcome_audit_rows | 23 | Rows in the provisional ALB_2005 outcome feasibility audit. |
| alb2005_provisional_financial_stress_test_rows | 8 | Financial-protection stress-test rows, none final. |
| alb2005_provisional_access_proxy_rows | 10 | Access proxy rows, none final. |
| alb2005_provisional_low_event_rate_rows | 6 | Outcome candidates with unweighted event rate below 3 percent. |
| alb2005_provisional_outcome_base_rows | 3840 | Rows in temp/alb2005_household_core_candidate.csv. |
| alb2005_provisional_positive_total_consumption_rows | 3638 | Rows with positive total_consumption. |
| alb2005_provisional_positive_household_weight_rows | 3840 | Rows with positive household_weight. |
| alb2005_provisional_consumption_weight_rows | 3638 | Rows with both positive total_consumption and positive household_weight. |
| alb2005_provisional_outcome_ready_rows | 0 | No provisional ALB_2005 diagnostic row is ready for data/ or outcome promotion. |
| alb2005_provisional_outcome_current_decision | not_final_outcomes_timing_geography_recall_blocked | Current fail-closed decision for ALB_2005 provisional outcome feasibility. |

## Candidate Diagnostics

| outcome_family | outcome_candidate | denominator_rows | numerator_rows | unweighted_rate | weighted_rate | low_event_rate_flag | promotion_status |
|---|---|---|---|---|---|---|---|
| financial_stress_test | oop_4w_unannualized_che10 | 3638 | 554 | 0.152281 | 0.168577 | 0 | not_ready_provisional_only |
| financial_stress_test | oop_4w_annualized_13x_che10 | 3638 | 1999 | 0.549478 | 0.571665 | 0 | not_ready_provisional_only |
| financial_stress_test | oop_12m_che10 | 3638 | 1136 | 0.312259 | 0.299306 | 0 | not_ready_provisional_only |
| financial_stress_test | oop_4w_unannualized_che25 | 3638 | 173 | 0.0475536 | 0.0523263 | 0 | not_ready_provisional_only |
| financial_stress_test | oop_4w_annualized_13x_che25 | 3638 | 1505 | 0.413689 | 0.429845 | 0 | not_ready_provisional_only |
| financial_stress_test | oop_12m_che25 | 3638 | 619 | 0.170148 | 0.16397 | 0 | not_ready_provisional_only |
| financial_stress_test | oop_any_positive_4w | 3840 | 2679 | 0.697656 | 0.715105 | 0 | not_ready_provisional_only |
| financial_stress_test | oop_any_positive_12m | 3840 | 2231 | 0.58099 | 0.566779 | 0 | not_ready_provisional_only |
| access_proxy | difficulty_pay_health | 3840 | 545 | 0.141927 | 0.146426 | 0 | not_ready_provisional_only |
| access_proxy | delayed_help_any | 3840 | 268 | 0.0697917 | 0.0522874 | 0 | not_ready_provisional_only |
| access_proxy | hospital_referral_not_gone_any | 3840 | 182 | 0.0473958 | 0.0480375 | 0 | not_ready_provisional_only |
| access_proxy | delay_reason_cost | 3840 | 5 | 0.00130208 | 0.0011886 | 1 | not_ready_provisional_only |
| access_proxy | delay_reason_distance | 3840 | 56 | 0.0145833 | 0.0120406 | 1 | not_ready_provisional_only |
| access_proxy | not_gone_reason_cost | 3840 | 88 | 0.0229167 | 0.0236292 | 1 | not_ready_provisional_only |
| access_proxy | not_gone_reason_distance | 3840 | 22 | 0.00572917 | 0.00363356 | 1 | not_ready_provisional_only |
| access_proxy | delayed_or_referral_nonuse_proxy | 3840 | 370 | 0.0963542 | 0.083941 | 0 | not_ready_provisional_only |
| access_proxy | access_cost_barrier_proxy | 3840 | 90 | 0.0234375 | 0.0239249 | 1 | not_ready_provisional_only |
| access_proxy | access_distance_barrier_proxy | 3840 | 75 | 0.0195312 | 0.0147931 | 1 | not_ready_provisional_only |
| need_proxy | illness_or_disability_any | 3840 | 1804 | 0.469792 | 0.479377 | 0 | not_ready_provisional_only |
| need_proxy | sudden_illness_4w_any | 3840 | 966 | 0.251563 | 0.241253 | 0 | not_ready_provisional_only |
| composite_proxy | uhc_proxy_oop12m_che10_or_access_proxy | 3638 | 1341 | 0.368609 | 0.351929 | 0 | not_ready_provisional_only |
| composite_proxy | uhc_proxy_oop12m_che25_or_access_proxy | 3638 | 882 | 0.242441 | 0.227615 | 0 | not_ready_provisional_only |
| composite_proxy | uhc_proxy_oop12m_che10_or_cost_barrier | 3638 | 1187 | 0.326278 | 0.31491 | 0 | not_ready_provisional_only |

## Interpretation

- No SDG 3.8.2 outcome is constructed here: discretionary-budget inputs, societal poverty line adjustments, and official denominator handling are unresolved.
- No final CHE10/CHE25 outcome is constructed here: the four-week and twelve-month OOP sums are unreviewed stress tests, not harmonized OOP health expenditure.
- No climate exposure is linked here: ALB_2005 still lacks verified survey month/date and has only partial district geography with no GPS.
- No causal, ML, descriptive-prevalence, or policy-targeting claim can be made from this audit.
- All rows remain `not_ready_provisional_only`; promotion-ready rows are intentionally zero.

## Machine-Readable Outputs

- `temp/alb2005_provisional_outcome_feasibility_audit.csv`
- `result/alb2005_provisional_outcome_feasibility_summary.csv`
