# ALB_2002 Limited Financial Outcome Promotion

Status: limited CHE-only outcome promotion. This writes `data/household_outcomes.csv` from existing ALB_2002 CHE candidate rows. It promotes only `che10_total_budget`, `che25_total_budget`, `oop_share_total`, and `log_oop_plus_one`.

It does not promote SDG 3.8.2, capacity-to-pay, impoverishment, access outcomes, composite UHC failure, climate linkage, weighted inference, descriptive diagnostics, predictive ML, reduced-form estimation, causal ML, policy learning, or robustness checks.

## Summary

| metric | value | interpretation |
|---|---|---|
| alb2002_limited_financial_outcome_promotion_audit_rows | 5 | Rows in the limited financial outcome promotion audit. |
| alb2002_limited_financial_outcome_rows | 3599 | Rows written to data/household_outcomes.csv. |
| alb2002_limited_financial_outcome_denominator_rows | 3599 | Rows with documented monthly total-budget candidate denominator. |
| alb2002_limited_financial_outcome_positive_oop_rows | 3038 | Rows with positive period-aligned OOP. |
| alb2002_limited_financial_outcome_positive_oop_weighted_rate | 0.852605 | Weighted positive-OOP rate, still not final weighted inference. |
| alb2002_limited_financial_outcome_che10_rows | 824 | Rows with CHE10 total-budget outcome. |
| alb2002_limited_financial_outcome_che10_rate | 0.228952 | Unweighted CHE10 rate. |
| alb2002_limited_financial_outcome_che10_weighted_rate | 0.23666 | Weighted CHE10 rate, still not final weighted inference. |
| alb2002_limited_financial_outcome_che25_rows | 290 | Rows with CHE25 total-budget outcome. |
| alb2002_limited_financial_outcome_che25_rate | 0.0805779 | Unweighted CHE25 rate. |
| alb2002_limited_financial_outcome_che25_weighted_rate | 0.0859036 | Weighted CHE25 rate, still not final weighted inference. |
| alb2002_limited_financial_outcome_oop_share_mean | 0.0893197 | Mean OOP share among rows with valid denominator. |
| alb2002_limited_financial_outcome_limited_data_write_ready_rows | 3599 | Rows allowed in data/ only under limited CHE-only outcome scope. |
| alb2002_limited_financial_outcome_sdg382_ready_rows | 0 | Rows ready for SDG 3.8.2 outcome. |
| alb2002_limited_financial_outcome_access_ready_rows | 0 | Rows ready for access outcomes. |
| alb2002_limited_financial_outcome_composite_ready_rows | 0 | Rows ready for composite UHC failure outcomes. |
| alb2002_limited_financial_outcome_climate_linkage_ready_rows | 0 | Rows ready for climate-linked household data. |
| alb2002_limited_financial_outcome_final_analysis_ready_rows | 0 | Rows ready for final empirical analysis. |
| alb2002_limited_financial_outcome_current_decision | limited_che10_che25_financial_outcomes_promoted_sdg_access_climate_still_blocked | Current limited outcome promotion decision. |
| alb2002_limited_financial_outcome_data_use_limit | outcome_che10_che25_only_not_for_final_sdg382_access_or_climate_analysis | Guardrail embedded in every output row. |

## Gate Audit

| gate_id | status | rows_passing | rows_blocked | next_action |
|---|---|---|---|---|
| source_candidate | complete_limited_financial_outcome_source | 3599 | 0 | Keep the output limited to CHE-only financial-protection outcomes. |
| financial_outcome_values | complete_limited_financial_outcomes | 3599 | 0 | Use these as CHE-only outcomes; do not infer SDG 3.8.2 or access failure. |
| weight_evidence | present_not_weighted_inference_ready | 3599 | 3599 | Resolve final survey-design and weighted-inference policy before using model estimates. |
| sdg382_access_composite | blocked_outside_limited_scope | 0 | 3599 | Resolve discretionary-budget, access denominator, and composite-outcome gates separately. |
| climate_model_readiness | blocked_not_climate_or_model_ready | 0 | 3599 | Do not use this file for descriptive, predictive, reduced-form, causal ML, policy learning, or robustness until clima... |

## Guardrails

- Every row carries `outcome_scope=alb2002_financial_protection_che10_che25_limited_no_sdg382_no_access`.
- Every row carries `data_use_limit=outcome_che10_che25_only_not_for_final_sdg382_access_or_climate_analysis`.
- `sdg382_ready`, `access_outcome_ready`, `composite_uhc_ready`, `climate_linkage_ready`, and `final_analysis_ready` remain zero.
- The file is sufficient only for CHE10/CHE25 financial-protection outcome inspection and audit.

## Machine-Readable Outputs

- `data/household_outcomes.csv`
- `result/outcome_audit.csv`
- `temp/outcome_construction_audit.csv`
- `temp/alb2002_limited_financial_outcome_promotion_audit.csv`
- `result/alb2002_limited_financial_outcome_promotion_summary.csv`
