# ALB_2005 Minimum Recipe Promotion Packet

Status: fail-closed promotion packet. ALB_2005 is the current raw-ready first-batch candidate, but this packet does not promote any dataset to `data/`. It records what must pass before the temp household-core candidate can become a harmonized household dataset, outcome dataset, or climate-linked dataset.

## Summary

| Metric | Value | Interpretation |
|---|---:|---|
| alb2005_minimum_recipe_promotion_action_rows | 6 | Action rows needed before ALB_2005 can become a minimum harmonized household dataset. |
| alb2005_minimum_recipe_promotion_gate_rows | 10 | Pass/fail promotion gates for ALB_2005 harmonization, outcome, and climate linkage. |
| alb2005_minimum_recipe_promotion_blocked_gates | 8 | Promotion gates still blocked. |
| alb2005_minimum_recipe_promotion_candidate_gates | 2 | Gates with candidate evidence that still needs acceptance review. |
| alb2005_minimum_recipe_promotion_harmonized_ready_rows | 0 | Rows ready for harmonized dataset promotion after this packet; intentionally zero. |
| alb2005_minimum_recipe_promotion_outcome_ready_rows | 0 | Existing ALB_2005 outcome-ready rows observed from semantics audits. |
| alb2005_minimum_recipe_promotion_climate_linkage_ready_rows | 0 | Existing ALB_2005 climate-linkage-ready rows observed from timing/geography audits. |
| alb2005_minimum_recipe_promotion_current_decision | blocked_alb2005_minimum_recipe_not_ready_for_promotion | Current fail-closed ALB_2005 minimum recipe promotion decision. |

## Action Queue

| action_rank | gate_id | blocker_domain | blocking_status | required_resolution |
|---|---|---|---|---|
| 1 | interview_timing | survey_timing | blocked_no_verified_household_interview_month_or_date | Find raw household interview month/date or official fieldwork-period metadata that can be linked to households o... |
| 2 | geography_for_climate | climate_geography | blocked_partial_geography_no_gps_or_full_admin_crosswalk | Resolve full-coverage admin geography or GPS/cluster geography, then document no-GPS/admin aggregation and bound... |
| 3 | oop_aggregation | financial_protection_outcome | blocked_oop_aggregation_recall_skip_gift_policy | Choose and document recall period, item scope, gift/payment inclusion, person-to-household aggregation, old/new ... |
| 4 | consumption_denominator | financial_protection_denominator | blocked_consumption_unit_period_component_scope_review | Confirm total-consumption unit, period, old/new lek basis, household-total interpretation, and whether `totcons`... |
| 5 | access_need_denominator | access_outcome | blocked_need_access_denominator_skip_patterns | Verify illness/need denominator, care-seeking/referral denominator, reason-not-sought coding, and cost/distance/... |
| 6 | keys_weights_merge | household_merge_and_survey_design | blocked_merge_key_weight_design_manual_review | Verify household ID uniqueness, cross-file merge cardinality, official weight variable use, and exclusion of bir... |

## Promotion Gates

| gate_id | required_for | current_status | current_evidence | minimum_evidence_to_pass |
|---|---|---|---|---|
| household_frame | harmonized_household_dataset | candidate_not_ready | temp candidate rows=3840; core decision=temp_candidate_not_analysis_ready | Complete household frame, key uniqueness/cardinality, and module coverage are verified. |
| survey_weight | weighted_descriptive_and_modeling | candidate_not_ready | household weight rows=3840; required value/key recipe-ready rows=0 | Official household weight use and population are verified; birth-weight false positives are excluded. |
| consumption_denominator | CHE10_CHE25_and_SDG_denominator | blocked | total consumption rows=3638; unit recipe-ready=0; component recipe-ready=0 | Total consumption has verified unit, period, price basis, missing rules, and household-total interpretation. |
| oop_aggregation | CHE10_CHE25_and_OOP_outcomes | blocked | positive unreviewed OOP rows: 4w=2679, 12m=2231; OOP policy recipe-ready=0 | OOP item scope, recall period, annualization policy, gift/payment inclusion, missing/zero rules, and household a... |
| health_need_access | forgone_care_and_double_failure_outcomes | blocked | semantics outcome-ready rows=0; questionnaire outcome-ready rows=0; skip/missing outcome-ready rows=0 | Illness/need, care-seeking, and barrier value labels and skip paths are verified. |
| interview_timing | climate_linkage | blocked | verified timing rows=0; household survey_month rows=0 | Interview month/date or defensible fieldwork-period timing is linked to analysis rows. |
| climate_geography | climate_linkage | blocked | coordinate candidates=0; full-coverage geography rows=0; climate-ready rows=0 | GPS/cluster coordinates or full-coverage admin geography with boundary/crosswalk evidence are available. |
| outcome_promotion | household_outcomes | blocked | outcome-ready rows=0; SDG 3.8.2-ready rows=0; value-decision ready rows=0 | Key, weight, consumption, OOP, and access/need gates pass, with event-rate and missingness audits. |
| harmonized_dataset_promotion | data/harmonized_household.csv | blocked | value-decision recipe-ready rows=0; required blocked rows=16; manual future candidate rows=4 | Required household frame, key, weight, denominator, OOP, and minimum outcome variables all pass value/key/unit r... |
| climate_dataset_promotion | data/climate_linked_household.csv | blocked | climate-linkage-ready rows=0; outcome-ready rows=0 | Harmonized dataset, accepted outcomes, verified timing, and verified climate geography all pass. |

## Interpretation

- ALB_2005 has a substantial temp household-core candidate and raw value evidence, but it is not analysis-ready.
- The minimum harmonized dataset is blocked by key/weight review, denominator and OOP semantics, access/need skip paths, and the absence of accepted value-decision rows.
- Climate linkage is separately blocked by zero verified interview timing rows and no full-coverage GPS/admin geography.
- This packet preserves the line between useful raw diagnostics and promoted analytical data.

## Machine-Readable Outputs

- `temp/alb2005_minimum_recipe_promotion_action_queue.csv`
- `temp/alb2005_minimum_recipe_promotion_gate_checklist.csv`
- `result/alb2005_minimum_recipe_promotion_summary.csv`
