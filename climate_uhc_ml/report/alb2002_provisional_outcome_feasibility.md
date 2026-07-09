# ALB_2002 Provisional Outcome Feasibility Audit

Status: provisional, temp-only, and fail-closed. This audit computes raw event-rate diagnostics from `temp/alb2002_household_core_candidate.csv` to see whether candidate ALB_2002 OOP/access fields have nonzero variation. It does not construct final UHC outcomes and does not write any file to `data/`.

## Summary

| Metric | Value | Interpretation |
|---|---:|---|
| alb2002_provisional_outcome_audit_rows | 30 | Rows in the provisional ALB_2002 outcome feasibility audit. |
| alb2002_provisional_financial_stress_test_rows | 8 | Financial-protection stress-test rows, none final. |
| alb2002_provisional_access_proxy_rows | 15 | Access proxy rows, none final. |
| alb2002_provisional_need_proxy_rows | 2 | Need proxy rows, none final. |
| alb2002_provisional_low_event_rate_rows | 9 | Outcome candidates with unweighted event rate below 3 percent. |
| alb2002_provisional_outcome_base_rows | 3599 | Rows in temp/alb2002_household_core_candidate.csv. |
| alb2002_provisional_positive_total_consumption_rows | 3599 | Rows with positive total_consumption. |
| alb2002_provisional_positive_household_weight_rows | 3599 | Rows with positive household_weight. |
| alb2002_provisional_consumption_weight_rows | 3599 | Rows with both positive total_consumption and positive household_weight. |
| alb2002_provisional_district_code_rows | 3599 | Rows with district_code_identification for future crosswalk review. |
| alb2002_provisional_survey_month_rows | 3599 | Rows with raw survey month for future climate window review. |
| alb2002_provisional_interview_date_rows | 3599 | Rows with constructed raw interview date for future climate window review. |
| alb2002_provisional_outcome_ready_rows | 0 | No provisional ALB_2002 diagnostic row is ready for data/ or outcome promotion. |
| alb2002_provisional_outcome_current_decision | not_final_outcomes_outcome_semantics_climate_crosswalk_blocked | Current fail-closed decision for ALB_2002 provisional outcome feasibility. |

## Candidate Diagnostics

| outcome_family | outcome_candidate | denominator_rows | numerator_rows | unweighted_rate | weighted_rate | low_event_rate_flag | promotion_status |
|---|---|---|---|---|---|---|---|
| financial_stress_test | oop_4w_unannualized_che10 | 3599 | 626 | 0.173937 | 0.185105 | 0 | not_ready_provisional_only |
| financial_stress_test | oop_4w_annualized_13x_che10 | 3599 | 2095 | 0.582106 | 0.596781 | 0 | not_ready_provisional_only |
| financial_stress_test | oop_12m_che10 | 3599 | 1076 | 0.298972 | 0.292566 | 0 | not_ready_provisional_only |
| financial_stress_test | oop_4w_unannualized_che25 | 3599 | 208 | 0.0577938 | 0.0620981 | 0 | not_ready_provisional_only |
| financial_stress_test | oop_4w_annualized_13x_che25 | 3599 | 1607 | 0.446513 | 0.45867 | 0 | not_ready_provisional_only |
| financial_stress_test | oop_12m_che25 | 3599 | 594 | 0.165046 | 0.161771 | 0 | not_ready_provisional_only |
| financial_stress_test | oop_any_positive_4w | 3599 | 2541 | 0.706029 | 0.732323 | 0 | not_ready_provisional_only |
| financial_stress_test | oop_any_positive_12m | 3599 | 2102 | 0.584051 | 0.573382 | 0 | not_ready_provisional_only |
| access_proxy | difficulty_pay_health | 3599 | 1623 | 0.450959 | 0.467311 | 0 | not_ready_provisional_only |
| access_proxy | delayed_help_any | 3599 | 144 | 0.0400111 | 0.0353799 | 0 | not_ready_provisional_only |
| access_proxy | hospital_referral_not_gone_any | 3599 | 161 | 0.0447346 | 0.0404396 | 0 | not_ready_provisional_only |
| access_proxy | delay_reason_cost | 3599 | 64 | 0.0177827 | 0.0125203 | 1 | not_ready_provisional_only |
| access_proxy | delay_reason_distance | 3599 | 13 | 0.00361211 | 0.00406597 | 1 | not_ready_provisional_only |
| access_proxy | not_gone_reason_cost | 3599 | 102 | 0.0283412 | 0.0235506 | 1 | not_ready_provisional_only |
| access_proxy | not_gone_reason_distance | 3599 | 8 | 0.00222284 | 0.00298483 | 1 | not_ready_provisional_only |
| access_proxy | refused_health_services_any | 3599 | 68 | 0.0188941 | 0.0176393 | 1 | not_ready_provisional_only |
| access_proxy | refused_reason_cost | 3599 | 46 | 0.0127813 | 0.0121689 | 1 | not_ready_provisional_only |
| access_proxy | refused_reason_distance | 3599 | 15 | 0.00416782 | 0.0031588 | 1 | not_ready_provisional_only |
| access_proxy | medicine_discount_cost_barrier | 3599 | 45 | 0.0125035 | 0.0109185 | 1 | not_ready_provisional_only |
| coping_proxy | health_payment_money_raising_any_unreviewed | 3599 | 1476 | 0.410114 | 0.434768 | 0 | not_ready_provisional_only |
| access_proxy | delayed_referral_or_refusal_proxy | 3599 | 318 | 0.0883579 | 0.080829 | 0 | not_ready_provisional_only |
| access_proxy | access_cost_barrier_proxy | 3599 | 219 | 0.0608502 | 0.052068 | 0 | not_ready_provisional_only |
| access_proxy | access_distance_barrier_proxy | 3599 | 34 | 0.00944707 | 0.00951398 | 1 | not_ready_provisional_only |
| access_proxy | access_affordability_or_coping_proxy | 3599 | 1661 | 0.461517 | 0.476346 | 0 | not_ready_provisional_only |
| need_proxy | illness_or_disability_any | 3599 | 1728 | 0.480133 | 0.492065 | 0 | not_ready_provisional_only |
| need_proxy | sudden_illness_4w_any | 3599 | 1152 | 0.320089 | 0.330622 | 0 | not_ready_provisional_only |
| composite_proxy | uhc_proxy_oop12m_che10_or_access_affordability | 3599 | 2062 | 0.572937 | 0.58241 | 0 | not_ready_provisional_only |
| composite_proxy | uhc_proxy_oop12m_che25_or_access_affordability | 3599 | 1843 | 0.512087 | 0.524121 | 0 | not_ready_provisional_only |
| composite_proxy | uhc_proxy_oop4w_annualized_che10_or_access_affordability | 3599 | 2496 | 0.693526 | 0.709366 | 0 | not_ready_provisional_only |
| composite_proxy | uhc_proxy_oop12m_che10_or_distance_barrier | 3599 | 1096 | 0.304529 | 0.298516 | 0 | not_ready_provisional_only |

## Interpretation

- No SDG 3.8.2 outcome is constructed here: discretionary-budget inputs, societal poverty line adjustments, PPP/CPI handling, and official denominator handling are unresolved.
- No final CHE10/CHE25 outcome is constructed here: the four-week and twelve-month OOP sums are unreviewed stress tests, not harmonized OOP health expenditure.
- No final forgone-care outcome is constructed here: illness/need, delayed care, referral nonuse, refusal, cost, distance, medicine-discount, and money-raising proxies still require skip-pattern and denominator validation.
- No climate exposure is linked here: ALB_2002 has observed interview date/month and district fields, but district boundary/crosswalk, no-GPS measurement error, and climate extraction are unresolved.
- No descriptive prevalence, causal, ML, or policy-targeting claim can be made from this audit.
- All rows remain `not_ready_provisional_only`; promotion-ready rows are intentionally zero.

## Machine-Readable Outputs

- `temp/alb2002_provisional_outcome_feasibility_audit.csv`
- `result/alb2002_provisional_outcome_feasibility_summary.csv`
