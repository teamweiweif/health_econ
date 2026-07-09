# ALB_2002 Outcome Blocker Resolution Matrix

Status: fail-closed outcome-promotion matrix. This consolidates ALB_2002 financial-protection, access, composite UHC, and coping outcome candidates into one promotion decision. It does not write `data/`, does not promote `data/household_outcomes.csv`, and does not treat SDG 3.8.2, CHE, access, composite, descriptive, predictive, causal, or policy-learning outcomes as complete.

## Summary

| Metric | Value | Interpretation |
|---|---:|---|
| alb2002_outcome_blocker_resolution_rows | 12 | Outcome blocker rows consolidated. |
| alb2002_outcome_blocker_financial_rows | 4 | Financial-protection outcome rows in the matrix. |
| alb2002_outcome_blocker_access_rows | 5 | Access outcome rows in the matrix. |
| alb2002_outcome_blocker_composite_rows | 3 | Composite UHC/coping outcome rows in the matrix. |
| alb2002_outcome_blocker_candidate_not_promoted_rows | 11 | Candidate outcome rows with evidence but no final promotion. |
| alb2002_outcome_blocker_low_event_candidate_rows | 1 | Sparse candidate outcome rows flagged as low-event. |
| alb2002_outcome_blocker_hard_blocked_rows | 1 | Outcome rows hard-blocked by missing required inputs. |
| alb2002_outcome_blocker_outcome_ready_rows | 0 | Rows ready for final outcome promotion; intentionally zero. |
| alb2002_outcome_blocker_sdg382_ready_rows | 0 | Rows ready for SDG 3.8.2 promotion; intentionally zero. |
| alb2002_outcome_blocker_climate_linkage_ready_rows | 0 | Rows ready for climate-linked outcome promotion; intentionally zero. |
| alb2002_outcome_blocker_data_write_ready_rows | 0 | Rows allowed for data/ writes by this outcome matrix; intentionally zero. |
| alb2002_outcome_blocker_current_decision | blocked_no_alb2002_outcome_ready_for_promotion | Current consolidated ALB_2002 outcome promotion decision. |

## Outcome Matrix

| outcome_id | outcome_family | candidate_event_rows | candidate_event_rate | candidate_weighted_rate | promotion_status | outcome_ready_rows | data_write_ready_rows |
|---|---|---|---|---|---|---|---|
| che10_total_budget_candidate | financial_protection | 824 | 0.228952 | 0.23666 | candidate_not_promoted | 0 | 0 |
| che25_total_budget_candidate | financial_protection | 290 | 0.0805779 | 0.0859036 | candidate_not_promoted | 0 | 0 |
| oop_share_total_candidate | financial_protection | 3038 | 0.852605 | 0.852605 | candidate_not_promoted | 0 | 0 |
| sdg382_discretionary_40 | financial_protection | 0 | 0 | 0 | hard_blocked_sdg_denominator | 0 | 0 |
| forgone_or_barrier_any_candidate | access | 1861 | 0.517088 | 0.528953 | candidate_not_promoted | 0 | 0 |
| forgone_or_barrier_cost_candidate | access | 1661 | 0.461517 | 0.476346 | candidate_not_promoted | 0 | 0 |
| forgone_or_barrier_distance_candidate | access | 34 |  |  | low_event_candidate_not_promoted | 0 | 0 |
| forgone_or_barrier_supply_admin_candidate | access | 405 |  |  | candidate_not_promoted | 0 | 0 |
| delayed_or_nonuse_candidate | access | 318 |  |  | candidate_not_promoted | 0 | 0 |
| uhc_che10_or_access_candidate | composite_uhc_failure | 2004 | 0.556821 | 0.570531 | candidate_not_promoted | 0 | 0 |
| uhc_che25_or_access_candidate | composite_uhc_failure | 1889 | 0.524868 | 0.537554 | candidate_not_promoted | 0 | 0 |
| coping_failure_candidate | composite_uhc_failure | 1476 |  |  | candidate_not_promoted | 0 | 0 |

## Interpretation

- CHE10 and CHE25 total-budget candidates have useful period-aligned stress-test rates, but final OOP recall and inclusion policies are not accepted.
- SDG 3.8.2 remains hard-blocked because SPL, PPP/CPI or price-basis handling, and discretionary-budget construction are not accepted.
- Access outcomes have several candidate signals, but the need denominator, barrier scope, low-event flags, and climate-geography gate are unresolved.
- Composite UHC outcomes are mechanical combinations of non-promoted CHE and access candidates, so they cannot be promoted independently.

## Required Resolution

Before any final outcome write, a future step must promote a numerator policy, denominator policy, skip/missing policy, SDG denominator if used, access denominator/barrier rules, event-rate/missingness audit, benchmark comparison where feasible, and climate-geography gate. Until then, outcome-ready, climate-linkage-ready, and data-write-ready rows remain zero.

## Machine-Readable Outputs

- `temp/alb2002_outcome_blocker_resolution_matrix.csv`
- `result/alb2002_outcome_blocker_resolution_summary.csv`
