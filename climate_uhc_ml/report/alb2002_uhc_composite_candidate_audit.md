# ALB_2002 UHC Composite Candidate Outcome Audit

Status: temp-only household-level composite UHC outcome audit. This combines the ALB_2002 CHE10/CHE25 candidate outcomes with access-barrier candidates to inspect double-failure, financial-only, access-only, both-failure, and coping candidates. It does not write `data/` outputs and does not promote any final outcome.

## Summary

| Metric | Value | Interpretation |
|---|---:|---|
| alb2002_uhc_composite_candidate_household_rows | 3599 | Temp-only ALB_2002 composite UHC candidate rows. |
| alb2002_uhc_composite_candidate_lineage_rows | 6 | Lineage rows for composite UHC candidate fields. |
| alb2002_uhc_composite_candidate_audit_rows | 10 | Outcome audit rows for composite UHC candidate fields. |
| alb2002_uhc_composite_candidate_source_che10_rows | 824 | Upstream CHE10 candidate rows consumed. |
| alb2002_uhc_composite_candidate_source_che25_rows | 290 | Upstream CHE25 candidate rows consumed. |
| alb2002_uhc_composite_candidate_source_access_any_rows | 1861 | Upstream any-access-barrier candidate rows consumed. |
| alb2002_uhc_composite_candidate_che10_or_access_rows | 2004 | CHE10 or any access-barrier candidate rows. |
| alb2002_uhc_composite_candidate_che10_or_access_rate | 0.556821 | CHE10-or-access unweighted candidate rate. |
| alb2002_uhc_composite_candidate_che10_or_access_weighted_rate | 0.570531 | CHE10-or-access weighted candidate rate. |
| alb2002_uhc_composite_candidate_che25_or_access_rows | 1889 | CHE25 or any access-barrier candidate rows. |
| alb2002_uhc_composite_candidate_che25_or_access_rate | 0.524868 | CHE25-or-access unweighted candidate rate. |
| alb2002_uhc_composite_candidate_che25_or_access_weighted_rate | 0.537554 | CHE25-or-access weighted candidate rate. |
| alb2002_uhc_composite_candidate_financial_only_che10_rows | 143 | CHE10-only candidate rows. |
| alb2002_uhc_composite_candidate_access_only_vs_che10_rows | 1180 | Access-only versus CHE10 candidate rows. |
| alb2002_uhc_composite_candidate_both_che10_access_rows | 681 | Both CHE10 and access-barrier candidate rows. |
| alb2002_uhc_composite_candidate_financial_only_che25_rows | 28 | CHE25-only candidate rows. |
| alb2002_uhc_composite_candidate_access_only_vs_che25_rows | 1599 | Access-only versus CHE25 candidate rows. |
| alb2002_uhc_composite_candidate_both_che25_access_rows | 262 | Both CHE25 and access-barrier candidate rows. |
| alb2002_uhc_composite_candidate_coping_rows | 1476 | Money-raising/coping candidate rows. |
| alb2002_uhc_composite_candidate_low_event_rate_rows | 1 | Composite candidate outcomes with event rate below 3 percent. |
| alb2002_uhc_composite_candidate_outcome_promotion_ready_rows | 0 | Rows ready for final composite outcome promotion; intentionally zero. |
| alb2002_uhc_composite_candidate_recipe_ready_rows | 0 | Rows ready for harmonized recipe promotion; intentionally zero. |
| alb2002_uhc_composite_candidate_sdg382_ready_rows | 0 | Rows ready for SDG 3.8.2 construction; intentionally zero. |
| alb2002_uhc_composite_candidate_climate_linkage_ready_rows | 0 | Rows ready for climate linkage; intentionally zero. |
| alb2002_uhc_composite_candidate_current_decision | blocked_alb2002_uhc_composite_candidate_not_promoted_due_outcome_recipe_climate_gates | Current fail-closed composite UHC candidate decision. |

## Outcome Audit

| outcome_id | outcome_family | denominator_rows | event_rows | event_rate | weighted_event_rate | low_event_rate_flag | ready_for_outcome |
|---|---|---|---|---|---|---|---|
| uhc_double_failure_che10_or_access_candidate | double_failure | 3599 | 2004 | 0.556821 | 0.570531 | 0 | 0 |
| uhc_double_failure_che25_or_access_candidate | double_failure | 3599 | 1889 | 0.524868 | 0.537554 | 0 | 0 |
| financial_only_che10_candidate | financial_only | 3599 | 143 | 0.0397333 | 0.0415783 | 0 | 0 |
| access_only_vs_che10_candidate | access_only | 3599 | 1180 | 0.327869 | 0.333871 | 0 | 0 |
| both_che10_access_candidate | both_financial_and_access | 3599 | 681 | 0.189219 | 0.195082 | 0 | 0 |
| financial_only_che25_candidate | financial_only | 3599 | 28 | 0.00777994 | 0.00860196 | 1 | 0 |
| access_only_vs_che25_candidate | access_only | 3599 | 1599 | 0.44429 | 0.451651 | 0 | 0 |
| both_che25_access_candidate | both_financial_and_access | 3599 | 262 | 0.072798 | 0.0773017 | 0 | 0 |
| composite_cost_barrier_candidate | access_cost | 3599 | 1661 | 0.461517 | 0.476346 | 0 | 0 |
| coping_health_cost_candidate | coping_failure | 3599 | 1476 | 0.410114 | 0.434768 | 0 | 0 |

## Lineage

| derived_field | source_fields | formula_or_rule | status | blocking_reason |
|---|---|---|---|---|
| uhc_double_failure_che10_or_access_candidate | che10_total_budget_candidate;composite_any_access_barrier_candidate | CHE10 candidate OR composite any-access-barrier candidate. | candidate_not_promoted | Composite mixes temp-only financial and access candidates. |
| uhc_double_failure_che25_or_access_candidate | che25_total_budget_candidate;composite_any_access_barrier_candidate | CHE25 candidate OR composite any-access-barrier candidate. | candidate_not_promoted | Composite mixes temp-only financial and access candidates. |
| financial_only_*_candidate | che10_total_budget_candidate;che25_total_budget_candidate;composite_any_access_barrier_candidate | Financial hardship candidate present and access barrier absent. | candidate_not_promoted | Absence of observed access barrier is not proof of no access failure. |
| access_only_vs_che*_candidate | che10_total_budget_candidate;che25_total_budget_candidate;composite_any_access_barrier_candidate | Access barrier candidate present and financial hardship candidate absent. | candidate_not_promoted | Absence of CHE is threshold- and denominator-dependent. |
| both_che*_access_candidate | che10_total_budget_candidate;che25_total_budget_candidate;composite_any_access_barrier_candidate | Financial hardship and access barrier candidates both present. | candidate_not_promoted | Both components remain unpromoted. |
| coping_health_cost_candidate | money_raising_any_candidate | Any Health B money-raising method for health care. | candidate_not_promoted | Coping proxy requires final source-scope review. |

## Interpretation

- Composite UHC candidates are available in `temp/alb2002_uhc_composite_candidate_outcomes.csv`.
- The CHE10-or-access and CHE25-or-access candidates are screening diagnostics, not final UHC failure outcomes.
- Access-only and financial-only categories depend on unresolved threshold, denominator, and skip-path decisions.
- Outcome-promotion-ready, recipe-ready, SDG 3.8.2-ready, and climate-linkage-ready rows remain zero.

## Machine-Readable Outputs

- `temp/alb2002_uhc_composite_candidate_outcomes.csv`
- `temp/alb2002_uhc_composite_candidate_lineage.csv`
- `result/alb2002_uhc_composite_candidate_audit.csv`
- `result/alb2002_uhc_composite_candidate_summary.csv`
