# ALB_2012 Timing/Geography Blocker Resolution Matrix

Status: fail-closed fallback-resolution matrix. This consolidates ALB_2012 timing, geography, outcome, and first-analysis promotion evidence into one decision. It does not write `data/`, does not promote ALB_2012 as a fallback analysis wave, and does not treat questionnaire control-sheet fields as raw household interview timing.

## Summary

| Metric | Value | Interpretation |
|---|---:|---|
| alb2012_timing_geography_blocker_resolution_rows | 10 | ALB_2012 fallback blocker rows consolidated. |
| alb2012_timing_geography_blocker_timing_rows | 3 | Timing blocker rows in the matrix. |
| alb2012_timing_geography_blocker_geography_rows | 3 | Geography blocker rows in the matrix. |
| alb2012_timing_geography_blocker_outcome_rows | 2 | Outcome blocker rows in the matrix. |
| alb2012_timing_geography_blocker_promotion_gate_rows | 2 | Promotion-gate rows in the matrix. |
| alb2012_timing_geography_blocker_hard_blocked_rows | 10 | Rows hard-blocked from fallback promotion. |
| alb2012_timing_geography_blocker_interview_timing_ready_rows | 0 | Rows with verified interview timing; intentionally zero. |
| alb2012_timing_geography_blocker_geography_ready_rows | 0 | Rows with promoted geography; intentionally zero. |
| alb2012_timing_geography_blocker_outcome_ready_rows | 0 | Rows with promoted outcomes; intentionally zero. |
| alb2012_timing_geography_blocker_climate_linkage_ready_rows | 0 | Rows ready for climate linkage; intentionally zero. |
| alb2012_timing_geography_blocker_data_write_ready_rows | 0 | Rows allowed for data/ writes by this matrix; intentionally zero. |
| alb2012_timing_geography_blocker_current_decision | blocked_alb2012_no_timing_geography_fallback_ready | Current consolidated ALB_2012 fallback decision. |

## Blocker Matrix

| blocker_id | blocker_family | evidence_rows | promotion_status | interview_timing_ready_rows | geography_ready_rows | outcome_ready_rows | climate_linkage_ready_rows | data_write_ready_rows |
|---|---|---|---|---|---|---|---|---|
| raw_household_interview_timing_values | timing | 0 | hard_blocked_missing_raw_interview_timing | 0 | 0 | 0 | 0 | 0 |
| questionnaire_control_sheet_timing_fields | timing | 29 | hard_blocked_questionnaire_design_not_raw_value | 0 | 0 | 0 | 0 | 0 |
| official_fieldwork_period_metadata | timing | 0 | hard_blocked_no_official_fieldwork_period | 0 | 0 | 0 | 0 | 0 |
| psu_cluster_keys_without_coordinates | geography | 34 | hard_blocked_cluster_keys_no_coordinates | 0 | 0 | 0 | 0 | 0 |
| coarse_prefecture_region_geography | geography | 3 | hard_blocked_coarse_geography_no_timing_no_gps | 0 | 0 | 0 | 0 | 0 |
| gps_coordinate_candidates | geography | 0 | hard_blocked_no_coordinate_candidates | 0 | 0 | 0 | 0 | 0 |
| provisional_outcome_candidates | outcome | 33 | hard_blocked_outcome_not_final_no_timing_geography | 0 | 0 | 0 | 0 | 0 |
| raw_outcome_semantics_candidates | outcome | 61 | hard_blocked_semantics_units_recall_skip_patterns | 0 | 0 | 0 | 0 | 0 |
| climate_linkage_promotion_gate | promotion_gate | 0 | hard_blocked_no_climate_linkage_ready_rows | 0 | 0 | 0 | 0 | 0 |
| first_analysis_fallback_promotion_gate | promotion_gate | 4 | hard_blocked_not_fallback_promoted | 0 | 0 | 0 | 0 | 0 |

## Interpretation

- ALB_2012 has household consumption, weights, OOP payment signals, access proxies, and coarse geography, but it has no verified raw household interview timing.
- Questionnaire control sheets expose date/time/visit fields, but those fields are not verified in raw household values.
- PSU keys and prefecture/region fields are useful for review, but no GPS, official PSU crosswalk, or promoted admin climate-linkage source is available.
- Provisional outcomes and raw health semantics remain diagnostic because timing, geography, units, recall periods, skip patterns, and payment-scope rules are unresolved.

## Required Resolution

ALB_2012 can become a fallback analysis wave only after a source supplies linkable household timing or defensible fieldwork-period metadata, a climate-linkage geography source, and accepted outcome policies. Until then, interview-timing-ready, geography-ready, outcome-ready, climate-linkage-ready, and data-write-ready rows remain zero.

## Machine-Readable Outputs

- `temp/alb2012_timing_geography_blocker_resolution_matrix.csv`
- `result/alb2012_timing_geography_blocker_resolution_summary.csv`
