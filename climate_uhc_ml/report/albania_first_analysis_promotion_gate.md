# Albania First Analysis Promotion Gate

Status: fail-closed promotion gate. This packet compares local Albania raw waves and identifies the nearest path to the first harmonized, outcome-audited, climate-linked analytical dataset.

## Summary

| Metric | Value | Interpretation |
|---|---:|---|
| albania_first_analysis_promotion_wave_rows | 4 | Albania local raw waves compared for first analysis-sample promotion. |
| albania_first_analysis_promotion_gate_rows | 40 | Promotion gate checklist rows. |
| albania_first_analysis_promotion_action_rows | 4 | Prioritized action rows. |
| albania_first_analysis_promotion_candidate_or_ready_gate_rows | 21 | Gate rows with candidate or ready evidence. |
| albania_first_analysis_promotion_blocked_gate_rows | 19 | Promotion gates still blocked. |
| albania_first_analysis_promotion_ready_wave_rows | 0 | Waves ready for first analytical-sample promotion; should remain zero until gates pass. |
| albania_first_analysis_promotion_harmonized_ready_rows | 0 | Harmonized-ready rows across compared waves; should remain zero. |
| albania_first_analysis_promotion_outcome_ready_rows | 0 | Outcome-ready rows across compared waves; should remain zero. |
| albania_first_analysis_promotion_climate_linkage_ready_rows | 0 | Climate-linkage-ready rows across compared waves; should remain zero. |
| albania_first_analysis_promotion_top_ranked_idno | ALB_2002_LSMS_v01_M | Top local raw wave to investigate next. |
| albania_first_analysis_promotion_top_ranked_primary_blocker | verified_2002_district_boundary_absent_gadm_lead_blocked_and_outcome_semantics_unpromoted | Binding blocker for the top-ranked local wave. |
| albania_first_analysis_promotion_current_decision | blocked_no_albania_wave_ready_for_first_analysis_promotion | Current fail-closed first-analysis promotion decision. |

## Wave Ranking

| priority_rank | idno | wave | household_rows | timing_signal_rows | geography_signal_rows | outcome_ready_rows | climate_linkage_ready_rows | blocked_gate_rows | primary_blocker |
|---|---|---|---|---|---|---|---|---|---|
| 1 | ALB_2002_LSMS_v01_M | 2002 | 3599 | 3599 | 3599 | 0 | 0 | 4 | verified_2002_district_boundary_absent_gadm_lead_blocked_and_outcome_semantics_unpromoted |
| 2 | ALB_2005_LSMS_v01_M | 2005 | 3840 | 0 | 329 | 0 | 0 | 5 | missing_bookmetadata_food_diary_modules_no_household_timing_no_coordinates |
| 3 | ALB_2008_LSMS_v01_M | 2008 | 3599 | 0 | 3599 | 0 | 0 | 5 | missing_interview_timing_and_only_coarse_geography_no_gps |
| 4 | ALB_2012_LSMS_v01_M_v01_A_PUF | 2012 | 6671 | 0 | 6671 | 0 | 0 | 5 | missing_interview_timing_coarse_prefecture_region_no_gps |

## Action Queue

| priority_rank | idno | blocking_gate | action | success_condition |
|---|---|---|---|---|
| 1 | ALB_2002_LSMS_v01_M | verified_2002_district_boundary_absent_gadm_lead_blocked_and_outcome_semantics_unpromoted | review the GADM 3.6 district lead, resolve its duplicate SHKODER/provenance blocker or obtain an official 2... | harmonized_ready_rows>0, outcome_ready_rows>0, and climate_linkage_ready_rows>0 for the wave |
| 2 | ALB_2005_LSMS_v01_M | missing_bookmetadata_food_diary_modules_no_household_timing_no_coordinates | obtain missing bookmetadata/food-diary or official equivalent files, then verify household timing, geograph... | harmonized_ready_rows>0, outcome_ready_rows>0, and climate_linkage_ready_rows>0 for the wave |
| 3 | ALB_2008_LSMS_v01_M | missing_interview_timing_and_only_coarse_geography_no_gps | find official fieldwork/interview timing and a defensible admin geography crosswalk before revisiting OOP/a... | harmonized_ready_rows>0, outcome_ready_rows>0, and climate_linkage_ready_rows>0 for the wave |
| 4 | ALB_2012_LSMS_v01_M_v01_A_PUF | missing_interview_timing_coarse_prefecture_region_no_gps | link questionnaire timing fields to raw household dates or official fieldwork metadata and verify whether p... | harmonized_ready_rows>0, outcome_ready_rows>0, and climate_linkage_ready_rows>0 for the wave |

## Gate Checklist Preview

| idno | gate_id | gate_status | evidence_metric | evidence_value | required_next_evidence |
|---|---|---|---|---|---|
| ALB_2002_LSMS_v01_M | household_frame | candidate_evidence_not_promoted | alb2002_household_core_candidate_rows | 3599 | Keep lineage and merge-key evidence attached to any future harmonization recipe. |
| ALB_2002_LSMS_v01_M | consumption_denominator | candidate_evidence_not_promoted | alb2002_households_with_total_consumption | 3599 | Verify unit, period, price basis, and denominator variant against official documentation. |
| ALB_2002_LSMS_v01_M | survey_weight | candidate_evidence_not_promoted | alb2002_households_with_household_weight | 3599 | Verify weight, stratum, PSU, and merge semantics. |
| ALB_2002_LSMS_v01_M | oop_health_spending | candidate_evidence_not_promoted | alb2002_households_with_oop_4w_positive;alb2002_households_with_oop_12m_positive | 2541;2102 | Manually accept or reject OOP item scope, gift handling, recall-period standardization, and missing-code tr... |
| ALB_2002_LSMS_v01_M | interview_timing | candidate_evidence_not_promoted | alb2002_households_with_interview_date | 3599 | Verify raw household interview date/month or official fieldwork period usable for exposure windows. |
| ALB_2002_LSMS_v01_M | geography_or_gps | candidate_evidence_not_promoted | alb2002_households_with_district_code | 3599 | Verify GPS/coordinate values or a historically valid admin boundary/crosswalk. |
| ALB_2002_LSMS_v01_M | outcome_semantics | blocked_missing_required_evidence | alb2002_outcome_semantics_current_decision | blocked_outcome_semantics_units_recall_skip_patterns_unreviewed | Resolve units, recall periods, missing codes, conditional denominators, and skip patterns. |
| ALB_2002_LSMS_v01_M | sdg382_denominator | blocked_missing_required_evidence | alb2002_outcome_semantics_sdg382_ready_rows | 0 | Verify SPL/PPP/CPI inputs and household discretionary-budget denominator construction. |
| ALB_2002_LSMS_v01_M | climate_linkage | blocked_missing_required_evidence | alb2002_boundary_manual_source_followup_climate_linkage_ready_rows | 0 | Pass timing and geography gates, then construct and audit climate exposures. |
| ALB_2002_LSMS_v01_M | harmonized_dataset | blocked_missing_required_evidence | alb2002_household_core_recipe_ready_rows;alb2002_outcome_semantics_outcome_ready_rows;alb2002_boundary_manu... | 0;0;0 | Create data outputs only after all upstream gates are satisfied. |
| ALB_2005_LSMS_v01_M | household_frame | candidate_evidence_not_promoted | alb2005_household_core_candidate_rows | 3840 | Keep lineage and merge-key evidence attached to any future harmonization recipe. |
| ALB_2005_LSMS_v01_M | consumption_denominator | candidate_evidence_not_promoted | alb2005_households_with_total_consumption | 3638 | Verify unit, period, price basis, and denominator variant against official documentation. |
| ALB_2005_LSMS_v01_M | survey_weight | candidate_evidence_not_promoted | alb2005_households_with_household_weight | 3840 | Verify weight, stratum, PSU, and merge semantics. |
| ALB_2005_LSMS_v01_M | oop_health_spending | candidate_evidence_not_promoted | alb2005_households_with_oop_4w_positive;alb2005_households_with_oop_12m_positive | 2679;2231 | Manually accept or reject OOP item scope, gift handling, recall-period standardization, and missing-code tr... |
| ALB_2005_LSMS_v01_M | interview_timing | blocked_missing_required_evidence | alb2005_interview_timing_verified_rows | 0 | Verify raw household interview date/month or official fieldwork period usable for exposure windows. |
| ALB_2005_LSMS_v01_M | geography_or_gps | candidate_evidence_not_promoted | alb2005_households_with_partial_district_code | 329 | Verify GPS/coordinate values or a historically valid admin boundary/crosswalk. |
| ALB_2005_LSMS_v01_M | outcome_semantics | blocked_missing_required_evidence | alb2005_outcome_semantics_current_decision | blocked_timing_geography_outcome_semantics_units_recall_skip_patterns | Resolve units, recall periods, missing codes, conditional denominators, and skip patterns. |
| ALB_2005_LSMS_v01_M | sdg382_denominator | blocked_missing_required_evidence | alb2005_outcome_semantics_sdg382_ready_rows | 0 | Verify SPL/PPP/CPI inputs and household discretionary-budget denominator construction. |
| ALB_2005_LSMS_v01_M | climate_linkage | blocked_missing_required_evidence | alb2005_extracted_module_coverage_climate_linkage_ready_rows | 0 | Pass timing and geography gates, then construct and audit climate exposures. |
| ALB_2005_LSMS_v01_M | harmonized_dataset | blocked_missing_required_evidence | alb2005_household_core_recipe_ready_rows;alb2005_outcome_semantics_outcome_ready_rows;alb2005_extracted_mod... | 0;0;0 | Create data outputs only after all upstream gates are satisfied. |
| ALB_2008_LSMS_v01_M | household_frame | candidate_evidence_not_promoted | alb2008_household_core_candidate_rows | 3599 | Keep lineage and merge-key evidence attached to any future harmonization recipe. |
| ALB_2008_LSMS_v01_M | consumption_denominator | candidate_evidence_not_promoted | alb2008_households_with_total_consumption | 3599 | Verify unit, period, price basis, and denominator variant against official documentation. |
| ALB_2008_LSMS_v01_M | survey_weight | candidate_evidence_not_promoted | alb2008_households_with_household_weight | 3599 | Verify weight, stratum, PSU, and merge semantics. |
| ALB_2008_LSMS_v01_M | oop_health_spending | candidate_evidence_not_promoted | alb2008_households_with_oop_4w_positive;alb2008_households_with_oop_12m_positive | 1895;1284 | Manually accept or reject OOP item scope, gift handling, recall-period standardization, and missing-code tr... |
| ALB_2008_LSMS_v01_M | interview_timing | blocked_missing_required_evidence | alb2008_interview_timing_verified_rows | 0 | Verify raw household interview date/month or official fieldwork period usable for exposure windows. |
| ALB_2008_LSMS_v01_M | geography_or_gps | candidate_evidence_not_promoted | alb2008_coarse_geography_household_rows | 3599 | Verify GPS/coordinate values or a historically valid admin boundary/crosswalk. |
| ALB_2008_LSMS_v01_M | outcome_semantics | blocked_missing_required_evidence | alb2008_outcome_semantics_current_decision | blocked_timing_geography_outcome_semantics_units_recall_skip_patterns | Resolve units, recall periods, missing codes, conditional denominators, and skip patterns. |
| ALB_2008_LSMS_v01_M | sdg382_denominator | blocked_missing_required_evidence | alb2008_outcome_semantics_sdg382_ready_rows | 0 | Verify SPL/PPP/CPI inputs and household discretionary-budget denominator construction. |
| ALB_2008_LSMS_v01_M | climate_linkage | blocked_missing_required_evidence | alb2008_climate_linkage_ready_rows | 0 | Pass timing and geography gates, then construct and audit climate exposures. |
| ALB_2008_LSMS_v01_M | harmonized_dataset | blocked_missing_required_evidence | alb2008_household_core_recipe_ready_rows;alb2008_outcome_semantics_outcome_ready_rows;alb2008_climate_linka... | 0;0;0 | Create data outputs only after all upstream gates are satisfied. |
| ... | 10 additional rows omitted |  |  |  |  |

## Interpretation

- `ALB_2002_LSMS_v01_M` remains the nearest local raw-data path because it has household rows, consumption, weights, OOP candidates, interview date/month, and district-code signals.
- It still cannot be promoted because the public boundary follow-up found no conclusive 2002-compatible 36-district boundary source; the GADM 3.6 lead has duplicate `SHKODER` features and no verified official 2001/2002 provenance, and outcome semantics remain unpromoted.
- `ALB_2005_LSMS_v01_M` has useful household/OOP/consumption signals but is blocked by missing `bookmetadata_cl`/food-diary modules, no verified household timing, and no coordinate values.
- `ALB_2008_LSMS_v01_M` and `ALB_2012_LSMS_v01_M_v01_A_PUF` have usable household/value signals but lack verified interview timing and have only coarse/non-GPS geography in the current extracts.
- This packet writes no `data/` files and promotes zero harmonized, outcome, or climate-linkage rows.

## Machine-Readable Outputs

- `temp/albania_first_analysis_promotion_gate_checklist.csv`
- `temp/albania_first_analysis_promotion_action_queue.csv`
- `result/albania_first_analysis_promotion_wave_ranking.csv`
- `result/albania_first_analysis_promotion_summary.csv`
