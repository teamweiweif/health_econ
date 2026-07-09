# ALB_2002 OOP Skip-Value Decision Audit

Status: focused decision audit for skipped downstream OOP payment values. This report does not write `data/`, does not choose a final OOP recall/inclusion policy, and does not promote outcomes.

## Bottom Line

- The payment skip-path audit covers 7 person-level payment blocks.
- Nontriggered downstream payment cells are either missing or zero; no positive skipped-payment rows or cells are observed.
- The zero-coded skipped payment cells can be treated as no positive OOP contribution for stress-test aggregation.
- This resolves only the skipped-payment positive-leakage concern; OOP recall period, gift/transport scope, annualization, SDG denominator inputs, access denominators, and climate geography remain blocked.
- Current decision: `documented_alb2002_oop_skipped_values_zero_only_but_oop_policy_not_ready`.

## Summary

| Metric | Value | Interpretation |
|---|---:|---|
| alb2002_oop_skip_value_decision_rows | 5 | Rows in the ALB_2002 OOP skip-value decision audit. |
| alb2002_oop_skip_value_payment_block_rows | 7 | Person payment skip blocks checked for downstream skipped OOP values. |
| alb2002_oop_skip_value_access_condition_block_rows | 5 | Household access-condition skip blocks kept separate from OOP payment handling. |
| alb2002_oop_skip_value_payment_nonmissing_skipped_rows | 11 | Payment skip rows with any nonmissing downstream value when not triggered. |
| alb2002_oop_skip_value_payment_nonmissing_skipped_cells | 11 | Nonmissing downstream payment cells when the payment block was not triggered. |
| alb2002_oop_skip_value_payment_zero_skipped_cells | 11 | Zero-valued downstream payment cells when the payment block was not triggered. |
| alb2002_oop_skip_value_payment_positive_skipped_rows | 0 | Rows with positive downstream payment values when the payment block was not triggered; should remain zero. |
| alb2002_oop_skip_value_payment_positive_skipped_cells | 0 | Positive downstream payment cells when the payment block was not triggered; should remain zero. |
| alb2002_oop_skip_value_oop_policy_rows_observed | 11 | OOP aggregation policy rows observed upstream. |
| alb2002_oop_skip_value_oop_core_4w_match_rows | 3599 | Rows where recomputed four-week no-gifts-with-transport OOP matches the core candidate sum. |
| alb2002_oop_skip_value_oop_core_12m_match_rows | 3599 | Rows where recomputed 12-month no-gifts-with-transport OOP matches the core candidate sum. |
| alb2002_oop_skip_value_zero_skip_policy_ready_rows | 4 | Audit rows supporting the narrow no-positive-leakage skipped-payment decision. |
| alb2002_oop_skip_value_oop_recall_scope_ready_rows | 0 | Rows accepting a final OOP recall-period policy; intentionally zero. |
| alb2002_oop_skip_value_oop_inclusion_scope_ready_rows | 0 | Rows accepting final gift/transport/OOP inclusion scope; intentionally zero. |
| alb2002_oop_skip_value_recipe_ready_rows | 0 | Rows ready for harmonized recipe promotion; intentionally zero. |
| alb2002_oop_skip_value_outcome_ready_rows | 0 | Rows ready for outcome promotion; intentionally zero. |
| alb2002_oop_skip_value_sdg382_ready_rows | 0 | Rows ready for SDG 3.8.2 promotion; intentionally zero. |
| alb2002_oop_skip_value_climate_linkage_ready_rows | 0 | Rows ready for climate linkage; intentionally zero. |
| alb2002_oop_skip_value_current_decision | documented_alb2002_oop_skipped_values_zero_only_but_oop_policy_not_ready | Current decision for the ALB_2002 OOP skipped-payment-value audit. |

## Evidence Rows

| decision_family | decision_item | zero_skip_policy_ready | ready_for_recipe | ready_for_outcome | sdg382_ready | climate_linkage_ready |
|---|---|---:|---:|---:|---:|---:|
| payment_skip_values | payment_skip_positive_leak_check | 1 | 0 | 0 | 0 | 0 |
| payment_skip_values | zero_coded_skipped_payment_cells | 1 | 0 | 0 | 0 | 0 |
| access_condition_boundary | access_skip_paths_not_oop_payment_values | 0 | 0 | 0 | 0 | 0 |
| oop_policy_boundary | core_oop_recalculation_matches_existing_candidate | 1 | 0 | 0 | 0 | 0 |
| promotion_boundary | zero_skip_decision_not_outcome_promotion | 1 | 0 | 0 | 0 | 0 |

## Interpretation

This audit narrows the OOP blocker from `zero/nonmissing skipped-payment review` to a documented no-positive-leakage decision. It does not make ALB_2002 outcome-ready because the final OOP numerator still needs a recall-period and inclusion-scope decision, and financial-protection outcomes still require accepted denominator, SDG, access, and climate gates.
