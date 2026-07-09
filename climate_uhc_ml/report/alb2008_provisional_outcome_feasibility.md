# ALB_2008 Provisional Outcome Feasibility Audit

Status: provisional, temp-only, and fail-closed. This audit computes raw event-rate diagnostics from `temp/alb2008_household_core_candidate.csv` to see whether candidate ALB_2008 OOP/access fields have nonzero variation. It does not construct final UHC outcomes and does not write any file to `data/`.

## Summary

| Metric | Value | Interpretation |
|---|---:|---|
| alb2008_provisional_outcome_audit_rows | 24 | Rows in the provisional ALB_2008 outcome feasibility audit. |
| alb2008_provisional_financial_stress_test_rows | 8 | Financial-protection stress-test rows, none final. |
| alb2008_provisional_access_proxy_rows | 11 | Access proxy rows, none final. |
| alb2008_provisional_low_event_rate_rows | 6 | Outcome candidates with unweighted event rate below 3 percent. |
| alb2008_provisional_outcome_base_rows | 3599 | Rows in temp/alb2008_household_core_candidate.csv. |
| alb2008_provisional_positive_total_consumption_rows | 3599 | Rows with positive total_consumption. |
| alb2008_provisional_positive_household_weight_rows | 3599 | Rows with positive household_weight. |
| alb2008_provisional_consumption_weight_rows | 3599 | Rows with both positive total_consumption and positive household_weight. |
| alb2008_provisional_outcome_ready_rows | 0 | No provisional ALB_2008 diagnostic row is ready for data/ or outcome promotion. |
| alb2008_provisional_outcome_current_decision | not_final_outcomes_timing_geography_recall_blocked | Current fail-closed decision for ALB_2008 provisional outcome feasibility. |

## Candidate Diagnostics

| outcome_family | outcome_candidate | denominator_rows | numerator_rows | unweighted_rate | weighted_rate | low_event_rate_flag | promotion_status |
|---|---|---|---|---|---|---|---|
| financial_stress_test | oop_4w_unannualized_che10 | 3599 | 1435 | 0.398722 | 0.403718 | 0 | not_ready_provisional_only |
| financial_stress_test | oop_4w_annualized_13x_che10 | 3599 | 1880 | 0.522367 | 0.526626 | 0 | not_ready_provisional_only |
| financial_stress_test | oop_12m_che10 | 3599 | 1247 | 0.346485 | 0.366133 | 0 | not_ready_provisional_only |
| financial_stress_test | oop_4w_unannualized_che25 | 3599 | 1074 | 0.298416 | 0.297816 | 0 | not_ready_provisional_only |
| financial_stress_test | oop_4w_annualized_13x_che25 | 3599 | 1834 | 0.509586 | 0.515005 | 0 | not_ready_provisional_only |
| financial_stress_test | oop_12m_che25 | 3599 | 1116 | 0.310086 | 0.327083 | 0 | not_ready_provisional_only |
| financial_stress_test | oop_any_positive_4w | 3599 | 1895 | 0.526535 | 0.531031 | 0 | not_ready_provisional_only |
| financial_stress_test | oop_any_positive_12m | 3599 | 1284 | 0.356766 | 0.375501 | 0 | not_ready_provisional_only |
| access_proxy | difficulty_pay_health | 3599 | 403 | 0.111976 | 0.1091 | 0 | not_ready_provisional_only |
| access_proxy | delayed_help_any | 3599 | 3031 | 0.842178 | 0.855491 | 0 | not_ready_provisional_only |
| access_proxy | hospital_referral_not_gone_any | 3599 | 3031 | 0.842178 | 0.855491 | 0 | not_ready_provisional_only |
| access_proxy | delay_reason_cost | 3599 | 34 | 0.00944707 | 0.00678018 | 1 | not_ready_provisional_only |
| access_proxy | delay_reason_distance | 3599 | 36 | 0.0100028 | 0.00946926 | 1 | not_ready_provisional_only |
| access_proxy | not_gone_reason_cost | 3599 | 55 | 0.015282 | 0.0129204 | 1 | not_ready_provisional_only |
| access_proxy | not_gone_reason_distance | 3599 | 18 | 0.00500139 | 0.00264783 | 1 | not_ready_provisional_only |
| access_proxy | refused_health_services_any | 3599 | 215 | 0.0597388 | 0.0588667 | 0 | not_ready_provisional_only |
| access_proxy | delayed_referral_or_refusal_proxy | 3599 | 3047 | 0.846624 | 0.859892 | 0 | not_ready_provisional_only |
| access_proxy | access_cost_barrier_proxy | 3599 | 81 | 0.0225063 | 0.0180825 | 1 | not_ready_provisional_only |
| access_proxy | access_distance_barrier_proxy | 3599 | 53 | 0.0147263 | 0.0120104 | 1 | not_ready_provisional_only |
| need_proxy | illness_or_disability_any | 3599 | 1386 | 0.385107 | 0.389849 | 0 | not_ready_provisional_only |
| need_proxy | sudden_illness_4w_any | 3599 | 544 | 0.151153 | 0.142391 | 0 | not_ready_provisional_only |
| composite_proxy | uhc_proxy_oop12m_che10_or_access_proxy | 3599 | 3047 | 0.846624 | 0.859892 | 0 | not_ready_provisional_only |
| composite_proxy | uhc_proxy_oop12m_che25_or_access_proxy | 3599 | 3047 | 0.846624 | 0.859892 | 0 | not_ready_provisional_only |
| composite_proxy | uhc_proxy_oop12m_che10_or_cost_barrier | 3599 | 1287 | 0.357599 | 0.375481 | 0 | not_ready_provisional_only |

## Interpretation

- No SDG 3.8.2 outcome is constructed here: discretionary-budget inputs, societal poverty line adjustments, and official denominator handling are unresolved.
- No final CHE10/CHE25 outcome is constructed here: the four-week and twelve-month OOP sums are unreviewed stress tests, not harmonized OOP health expenditure.
- No climate exposure is linked here: ALB_2008 still lacks verified survey month/date and has only coarse area/stratum geography with no GPS.
- No descriptive prevalence, causal, ML, or policy-targeting claim can be made from this audit.
- All rows remain `not_ready_provisional_only`; promotion-ready rows are intentionally zero.

## Machine-Readable Outputs

- `temp/alb2008_provisional_outcome_feasibility_audit.csv`
- `result/alb2008_provisional_outcome_feasibility_summary.csv`
