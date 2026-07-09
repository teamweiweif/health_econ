# ALB_2012 Provisional Outcome Feasibility Audit

Status: provisional, temp-only, and fail-closed. This audit computes raw event-rate diagnostics from `temp/alb2012_household_core_candidate.csv` to see whether candidate ALB_2012 OOP/access/need fields have nonzero variation. It does not construct final UHC outcomes and does not write any file to `data/`.

## Summary

| Metric | Value | Interpretation |
|---|---:|---|
| alb2012_provisional_outcome_audit_rows | 33 | Rows in the provisional ALB_2012 outcome feasibility audit. |
| alb2012_provisional_financial_stress_test_rows | 8 | Financial-protection stress-test rows, none final. |
| alb2012_provisional_access_proxy_rows | 15 | Access proxy rows, none final. |
| alb2012_provisional_need_proxy_rows | 4 | Need proxy rows, none final. |
| alb2012_provisional_coping_proxy_rows | 1 | Health-payment coping proxy rows, none final. |
| alb2012_provisional_shock_proxy_rows | 1 | Raw household shock proxy rows, not climate exposure rows. |
| alb2012_provisional_low_event_rate_rows | 9 | Outcome candidates with unweighted event rate below 3 percent. |
| alb2012_provisional_outcome_base_rows | 6671 | Rows in temp/alb2012_household_core_candidate.csv. |
| alb2012_provisional_positive_total_consumption_rows | 6671 | Rows with positive total_consumption. |
| alb2012_provisional_positive_household_weight_rows | 6671 | Rows with positive household_weight. |
| alb2012_provisional_consumption_weight_rows | 6671 | Rows with both positive total_consumption and positive household_weight. |
| alb2012_provisional_prefecture_rows | 6671 | Rows with coarse prefecture field for future geography review. |
| alb2012_provisional_region_rows | 6671 | Rows with coarse region field for future geography review. |
| alb2012_provisional_survey_month_rows | 0 | Rows with raw survey month for future climate window review. |
| alb2012_provisional_interview_date_rows | 0 | Rows with raw interview date for future climate window review. |
| alb2012_provisional_oop_4w_positive_rows | 2794 | Rows with positive unreviewed four-week OOP. |
| alb2012_provisional_oop_12m_positive_rows | 2093 | Rows with positive unreviewed twelve-month OOP. |
| alb2012_provisional_access_affordability_proxy_rows | 2750 | Rows with difficulty paying health care proxy. |
| alb2012_provisional_distance_barrier_proxy_rows | 36 | Rows with any unreviewed distance-barrier proxy. |
| alb2012_provisional_need_signal_rows | 5691 | Rows with any unreviewed health-need proxy. |
| alb2012_provisional_outcome_ready_rows | 0 | No provisional ALB_2012 diagnostic row is ready for data/ or outcome promotion. |
| alb2012_provisional_climate_linkage_ready_rows | 0 | No ALB_2012 provisional diagnostic row is ready for climate linkage. |
| alb2012_provisional_outcome_current_decision | not_final_outcomes_timing_geography_recall_semantics_blocked | Current fail-closed decision for ALB_2012 provisional outcome feasibility. |

## Candidate Diagnostics

| outcome_family | outcome_candidate | denominator_rows | numerator_rows | unweighted_rate | weighted_rate | low_event_rate_flag | promotion_status |
|---|---|---|---|---|---|---|---|
| financial_stress_test | oop_4w_unannualized_che10 | 6671 | 1099 | 0.164743 | 0.160845 | 0 | not_ready_provisional_only |
| financial_stress_test | oop_4w_annualized_13x_che10 | 6671 | 2583 | 0.387198 | 0.369892 | 0 | not_ready_provisional_only |
| financial_stress_test | oop_12m_che10 | 6671 | 1317 | 0.197422 | 0.171195 | 0 | not_ready_provisional_only |
| financial_stress_test | oop_4w_unannualized_che25 | 6671 | 469 | 0.0703043 | 0.0655612 | 0 | not_ready_provisional_only |
| financial_stress_test | oop_4w_annualized_13x_che25 | 6671 | 2194 | 0.328886 | 0.314923 | 0 | not_ready_provisional_only |
| financial_stress_test | oop_12m_che25 | 6671 | 624 | 0.0935392 | 0.0850915 | 0 | not_ready_provisional_only |
| financial_stress_test | oop_any_positive_4w | 6671 | 2794 | 0.418828 | 0.399001 | 0 | not_ready_provisional_only |
| financial_stress_test | oop_any_positive_12m | 6671 | 2093 | 0.313746 | 0.282287 | 0 | not_ready_provisional_only |
| access_proxy | difficulty_pay_health | 6671 | 2750 | 0.412232 | 0.408104 | 0 | not_ready_provisional_only |
| access_proxy | delayed_help_any | 6671 | 4673 | 0.700495 | 0.690923 | 0 | not_ready_provisional_only |
| access_proxy | hospital_referral_not_gone_any | 6671 | 4673 | 0.700495 | 0.690923 | 0 | not_ready_provisional_only |
| access_proxy | delay_reason_cost | 6671 | 126 | 0.0188877 | 0.0196517 | 1 | not_ready_provisional_only |
| access_proxy | delay_reason_distance | 6671 | 8 | 0.00119922 | 0.000791141 | 1 | not_ready_provisional_only |
| access_proxy | not_gone_reason_cost | 6671 | 122 | 0.0182881 | 0.0167354 | 1 | not_ready_provisional_only |
| access_proxy | not_gone_reason_distance | 6671 | 13 | 0.00194873 | 0.00134593 | 1 | not_ready_provisional_only |
| access_proxy | refused_health_services_any | 6671 | 176 | 0.0263829 | 0.0245727 | 1 | not_ready_provisional_only |
| access_proxy | refused_reason_cost | 6671 | 137 | 0.0205367 | 0.0189287 | 1 | not_ready_provisional_only |
| access_proxy | refused_reason_distance | 6671 | 17 | 0.00254834 | 0.00229737 | 1 | not_ready_provisional_only |
| access_proxy | medicine_discount_cost_barrier | 6671 | 104 | 0.0155899 | 0.016954 | 1 | not_ready_provisional_only |
| coping_proxy | health_payment_money_raising_any_unreviewed | 6671 | 2340 | 0.350772 | 0.337563 | 0 | not_ready_provisional_only |
| access_proxy | delayed_referral_or_refusal_proxy | 6671 | 4678 | 0.701244 | 0.691268 | 0 | not_ready_provisional_only |
| access_proxy | access_cost_barrier_proxy | 6671 | 368 | 0.0551641 | 0.0541319 | 0 | not_ready_provisional_only |
| access_proxy | access_distance_barrier_proxy | 6671 | 36 | 0.00539649 | 0.00434153 | 1 | not_ready_provisional_only |
| access_proxy | access_affordability_or_coping_proxy | 6671 | 2787 | 0.417778 | 0.413432 | 0 | not_ready_provisional_only |
| need_proxy | chronic_illness_any | 6671 | 2277 | 0.341328 | 0.338514 | 0 | not_ready_provisional_only |
| need_proxy | sudden_illness_4w_any | 6671 | 1273 | 0.190826 | 0.181867 | 0 | not_ready_provisional_only |
| need_proxy | health_license_any | 6671 | 5182 | 0.776795 | 0.77318 | 0 | not_ready_provisional_only |
| shock_proxy | shock_any_2008_2012 | 6671 | 1306 | 0.195773 | 0.192158 | 0 | not_ready_provisional_only |
| need_proxy | need_or_shock_proxy | 6671 | 5800 | 0.869435 | 0.872303 | 0 | not_ready_provisional_only |
| composite_proxy | uhc_proxy_oop12m_che10_or_access_affordability | 6671 | 3434 | 0.514765 | 0.495373 | 0 | not_ready_provisional_only |
| composite_proxy | uhc_proxy_oop12m_che25_or_access_affordability | 6671 | 3040 | 0.455704 | 0.447789 | 0 | not_ready_provisional_only |
| composite_proxy | uhc_proxy_oop4w_annualized_che10_or_access_affordability | 6671 | 3930 | 0.589117 | 0.571134 | 0 | not_ready_provisional_only |
| composite_proxy | uhc_proxy_oop12m_che10_or_distance_barrier | 6671 | 1343 | 0.201319 | 0.174347 | 0 | not_ready_provisional_only |

## Interpretation

- No SDG 3.8.2 outcome is constructed here: discretionary-budget inputs, societal poverty line adjustments, PPP/CPI handling, and official denominator handling are unresolved.
- No final CHE10/CHE25 outcome is constructed here: four-week and twelve-month OOP sums are unreviewed stress tests, not harmonized OOP health expenditure.
- No final forgone-care outcome is constructed here: illness/need, delayed care, referral nonuse, refusal, cost, distance, medicine-discount, and money-raising proxies still require skip-pattern and denominator validation.
- No climate exposure is linked here: ALB_2012 has no observed interview date/month, no GPS, and only coarse prefecture/region geography.
- No descriptive prevalence, causal, ML, or policy-targeting claim can be made from this audit.
- All rows remain `not_ready_provisional_only`; promotion-ready rows are intentionally zero.

## Machine-Readable Outputs

- `temp/alb2012_provisional_outcome_feasibility_audit.csv`
- `result/alb2012_provisional_outcome_feasibility_summary.csv`
