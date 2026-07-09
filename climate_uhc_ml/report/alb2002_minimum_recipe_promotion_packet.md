# ALB_2002 Minimum Recipe Promotion Packet

Status: fail-closed promotion packet. ALB_2002 is the current top-ranked Albania first-analysis lead, but this packet does not promote any dataset to `data/`. It records what must pass before the temp household-core candidate can become a harmonized household dataset, outcome dataset, or climate-linked dataset.

## Summary

| Metric | Value | Interpretation |
|---|---:|---|
| alb2002_minimum_recipe_promotion_action_rows | 6 | Action rows needed before ALB_2002 can become a minimum harmonized household dataset. |
| alb2002_minimum_recipe_promotion_gate_rows | 10 | Pass/fail promotion gates for ALB_2002 harmonization, outcome, and climate linkage. |
| alb2002_minimum_recipe_promotion_blocked_gates | 7 | Promotion gates still blocked. |
| alb2002_minimum_recipe_promotion_candidate_gates | 3 | Gates with candidate evidence that still needs acceptance review. |
| alb2002_minimum_recipe_promotion_weight_design_audit_rows | 6 | ALB_2002 weight/design evidence audit rows observed upstream. |
| alb2002_minimum_recipe_promotion_weight_design_source_flag_rows | 9 | Official source-context flags detected by the ALB_2002 weight/design audit. |
| alb2002_minimum_recipe_promotion_weight_design_positive_weight_rows | 3599 | ALB_2002 positive household-weight rows observed in the readable weight file. |
| alb2002_minimum_recipe_promotion_weight_design_key_match_rows | 3599 | ALB_2002 readable weight-file keys matching the temp household core. |
| alb2002_minimum_recipe_promotion_weight_design_distinct_psu_rows | 450 | ALB_2002 distinct PSU values observed in the readable weight file. |
| alb2002_minimum_recipe_promotion_weight_design_distinct_stratum_rows | 4 | ALB_2002 distinct strata observed in the readable weight file. |
| alb2002_minimum_recipe_promotion_weight_design_weighted_inference_ready_rows | 0 | ALB_2002 rows ready for promoted weighted inference; intentionally zero. |
| alb2002_minimum_recipe_promotion_weight_design_harmonized_ready_rows | 0 | ALB_2002 rows ready for harmonized promotion after weight/design audit; intentionally zero. |
| alb2002_minimum_recipe_promotion_weight_design_decision | blocked_alb2002_weight_design_semantics_not_promotion_ready | Current ALB_2002 weight/design fail-closed decision observed by the minimum recipe packet. |
| alb2002_minimum_recipe_promotion_sample_design_pdf_pages | 66 | Pages extracted from the ALB_2002 Basic Information PDF sample-design source. |
| alb2002_minimum_recipe_promotion_sample_design_official_design_rows | 1 | Official 450 PSU by 8 household sample-design evidence observed upstream. |
| alb2002_minimum_recipe_promotion_sample_design_official_final_rows | 1 | Official 3,599 final household sample-size evidence observed upstream. |
| alb2002_minimum_recipe_promotion_sample_design_raw_concordance_rows | 1 | Raw weight and candidate counts concordant with the official sample-design evidence. |
| alb2002_minimum_recipe_promotion_sample_design_documentation_ready_rows | 1 | ALB_2002 sample-design documentation evidence ready; not a data-promotion gate pass. |
| alb2002_minimum_recipe_promotion_sample_design_weighted_inference_ready_rows | 0 | ALB_2002 rows ready for promoted weighted inference after sample-design audit; intentionally zero. |
| alb2002_minimum_recipe_promotion_sample_design_decision | candidate_alb2002_sample_design_documented_not_promoted_due_downstream_gates | Current ALB_2002 sample-design documentation decision observed by the minimum recipe packet. |
| alb2002_minimum_recipe_promotion_oop_policy_rows | 11 | ALB_2002 OOP aggregation policy stress-test rows observed upstream. |
| alb2002_minimum_recipe_promotion_oop_policy_outcome_ready_rows | 0 | ALB_2002 OOP policy rows ready for outcome promotion; intentionally zero. |
| alb2002_minimum_recipe_promotion_oop_policy_sdg382_ready_rows | 0 | ALB_2002 OOP policy rows ready for SDG 3.8.2 promotion; intentionally zero. |
| alb2002_minimum_recipe_promotion_period_aligned_che_policy_rows | 3 | ALB_2002 period-aligned CHE stress-test policy rows observed upstream. |
| alb2002_minimum_recipe_promotion_period_aligned_che_denominator_rows | 3599 | ALB_2002 rows with a positive monthly total-budget denominator in the period-aligned CHE audit. |
| alb2002_minimum_recipe_promotion_period_aligned_che_period_ready_rows | 3 | ALB_2002 period-aligned CHE policies with denominator, zero-skip, and period-alignment checks passing for stress testing. |
| alb2002_minimum_recipe_promotion_period_aligned_che_combined_che10_rate | 0.228952 | Combined monthly-equivalent CHE10 stress-test rate; not a final outcome. |
| alb2002_minimum_recipe_promotion_period_aligned_che_combined_che25_rate | 0.0805779 | Combined monthly-equivalent CHE25 stress-test rate; not a final outcome. |
| alb2002_minimum_recipe_promotion_period_aligned_che_outcome_ready_rows | 0 | ALB_2002 period-aligned CHE rows ready for outcome promotion; intentionally zero. |
| alb2002_minimum_recipe_promotion_period_aligned_che_recipe_ready_rows | 0 | ALB_2002 period-aligned CHE rows ready for recipe promotion; intentionally zero. |
| alb2002_minimum_recipe_promotion_period_aligned_che_sdg382_ready_rows | 0 | ALB_2002 period-aligned CHE rows ready for SDG 3.8.2 promotion; intentionally zero. |
| alb2002_minimum_recipe_promotion_period_aligned_che_climate_ready_rows | 0 | ALB_2002 period-aligned CHE rows ready for climate linkage; intentionally zero. |
| alb2002_minimum_recipe_promotion_period_aligned_che_decision | blocked_alb2002_period_aligned_che_policy_not_outcome_ready | Current ALB_2002 period-aligned CHE fail-closed decision observed by the minimum recipe packet. |
| alb2002_minimum_recipe_promotion_skip_missing_rows | 12 | ALB_2002 skip/missing semantics audit rows observed upstream. |
| alb2002_minimum_recipe_promotion_skip_positive_rows | 0 | ALB_2002 positive skipped-payment rows observed upstream; should remain zero. |
| alb2002_minimum_recipe_promotion_skip_zero_cells | 11 | ALB_2002 zero-only skipped-payment cells observed upstream. |
| alb2002_minimum_recipe_promotion_skip_outcome_ready_rows | 0 | ALB_2002 skip/missing rows ready for outcome promotion; intentionally zero. |
| alb2002_minimum_recipe_promotion_oop_skip_value_decision_rows | 5 | ALB_2002 OOP skip-value decision audit rows observed upstream. |
| alb2002_minimum_recipe_promotion_oop_skip_value_zero_ready_rows | 4 | ALB_2002 skip-value rows supporting the no-positive-leakage skipped-payment decision. |
| alb2002_minimum_recipe_promotion_oop_skip_value_positive_rows | 0 | ALB_2002 positive skipped-payment rows after the skip-value decision; should remain zero. |
| alb2002_minimum_recipe_promotion_oop_skip_value_positive_cells | 0 | ALB_2002 positive skipped-payment cells after the skip-value decision; should remain zero. |
| alb2002_minimum_recipe_promotion_oop_skip_value_recall_ready_rows | 0 | ALB_2002 OOP recall-scope rows accepted by the skip-value audit; intentionally zero. |
| alb2002_minimum_recipe_promotion_oop_skip_value_inclusion_ready_rows | 0 | ALB_2002 OOP inclusion-scope rows accepted by the skip-value audit; intentionally zero. |
| alb2002_minimum_recipe_promotion_oop_skip_value_decision | documented_alb2002_oop_skipped_values_zero_only_but_oop_policy_not_ready | Current ALB_2002 OOP skip-value decision observed by the minimum recipe packet. |
| alb2002_minimum_recipe_promotion_access_need_policy_rows | 24 | ALB_2002 access/need denominator policy rows observed upstream. |
| alb2002_minimum_recipe_promotion_access_need_q01_need_rows | 3247 | ALB_2002 q01 need-denominator rows observed upstream. |
| alb2002_minimum_recipe_promotion_access_need_any_barrier_rows | 1861 | ALB_2002 composite any-access-barrier candidate rows observed upstream. |
| alb2002_minimum_recipe_promotion_access_need_outcome_ready_rows | 0 | ALB_2002 access/need rows ready for outcome promotion; intentionally zero. |
| alb2002_minimum_recipe_promotion_access_candidate_household_rows | 3599 | ALB_2002 temp-only household access candidate rows observed upstream. |
| alb2002_minimum_recipe_promotion_access_candidate_any_barrier_rows | 1861 | ALB_2002 temp-only composite any-access-barrier candidate rows observed upstream. |
| alb2002_minimum_recipe_promotion_access_candidate_cost_barrier_rows | 1661 | ALB_2002 temp-only composite cost-barrier candidate rows observed upstream. |
| alb2002_minimum_recipe_promotion_access_candidate_outcome_ready_rows | 0 | ALB_2002 household access candidate rows ready for final outcome promotion; intentionally zero. |
| alb2002_minimum_recipe_promotion_uhc_composite_rows | 3599 | ALB_2002 temp-only composite UHC candidate rows observed upstream. |
| alb2002_minimum_recipe_promotion_uhc_composite_che10_or_access_rows | 2004 | ALB_2002 temp-only CHE10-or-access candidate rows observed upstream. |
| alb2002_minimum_recipe_promotion_uhc_composite_che25_or_access_rows | 1889 | ALB_2002 temp-only CHE25-or-access candidate rows observed upstream. |
| alb2002_minimum_recipe_promotion_uhc_composite_both_che10_access_rows | 681 | ALB_2002 temp-only both CHE10 and access-barrier candidate rows observed upstream. |
| alb2002_minimum_recipe_promotion_uhc_composite_coping_rows | 1476 | ALB_2002 temp-only health-cost coping candidate rows observed upstream. |
| alb2002_minimum_recipe_promotion_uhc_composite_outcome_ready_rows | 0 | ALB_2002 composite UHC candidate rows ready for final outcome promotion; intentionally zero. |
| alb2002_minimum_recipe_promotion_consumption_sdg_policy_rows | 14 | ALB_2002 consumption/SDG denominator policy rows observed upstream. |
| alb2002_minimum_recipe_promotion_consumption_sdg_positive_total_rows | 3599 | ALB_2002 positive total-consumption denominator rows observed upstream. |
| alb2002_minimum_recipe_promotion_consumption_aggregate_crosswalk_rows | 11 | ALB_2002 consumption aggregate metadata/local evidence crosswalk rows observed upstream. |
| alb2002_minimum_recipe_promotion_consumption_aggregate_metadata_rows | 0 | ALB_2002 local master metadata catalog rows for the aggregate audit. |
| alb2002_minimum_recipe_promotion_consumption_aggregate_totcons_match_rows | 3599 | ALB_2002 candidate total-consumption rows exactly matching raw `totcons`. |
| alb2002_minimum_recipe_promotion_consumption_aggregate_documentation_ready_rows | 9 | ALB_2002 rows with accepted public aggregate documentation. |
| alb2002_minimum_recipe_promotion_consumption_aggregate_recipe_ready_rows | 0 | ALB_2002 aggregate crosswalk rows ready for recipe promotion; intentionally zero. |
| alb2002_minimum_recipe_promotion_consumption_aggregate_outcome_ready_rows | 0 | ALB_2002 aggregate crosswalk rows ready for outcome promotion; intentionally zero. |
| alb2002_minimum_recipe_promotion_consumption_aggregate_sdg382_ready_rows | 0 | ALB_2002 aggregate crosswalk rows ready for SDG 3.8.2 promotion; intentionally zero. |
| alb2002_minimum_recipe_promotion_consumption_sdg_spl_ready_rows | 0 | ALB_2002 consumption/SDG rows with SPL inputs accepted; intentionally zero. |
| alb2002_minimum_recipe_promotion_consumption_sdg_ppp_cpi_ready_rows | 0 | ALB_2002 consumption/SDG rows with PPP/CPI inputs accepted; intentionally zero. |
| alb2002_minimum_recipe_promotion_consumption_sdg_discretionary_ready_rows | 0 | ALB_2002 rows with household discretionary budget accepted; intentionally zero. |
| alb2002_minimum_recipe_promotion_consumption_sdg_che_ready_rows | 0 | ALB_2002 rows with CHE denominator accepted; intentionally zero. |
| alb2002_minimum_recipe_promotion_consumption_sdg_outcome_ready_rows | 0 | ALB_2002 consumption/SDG rows ready for outcome promotion; intentionally zero. |
| alb2002_minimum_recipe_promotion_consumption_sdg_sdg382_ready_rows | 0 | ALB_2002 consumption/SDG rows ready for SDG 3.8.2 promotion; intentionally zero. |
| alb2002_minimum_recipe_promotion_harmonized_ready_rows | 0 | Rows ready for harmonized dataset promotion after this packet; intentionally zero. |
| alb2002_minimum_recipe_promotion_outcome_ready_rows | 0 | Existing ALB_2002 outcome-ready rows observed from raw semantics audits. |
| alb2002_minimum_recipe_promotion_sdg382_ready_rows | 0 | Existing ALB_2002 SDG 3.8.2-ready rows observed from raw semantics audits. |
| alb2002_minimum_recipe_promotion_climate_shock_rows | 384 | ALB_2002 temp-only climate shock diagnostic rows observed upstream. |
| alb2002_minimum_recipe_promotion_climate_shock_reference_groups | 16 | ALB_2002 survey-month/window diagnostic climate shock reference groups. |
| alb2002_minimum_recipe_promotion_climate_shock_precip_z_rows | 384 | ALB_2002 diagnostic rainfall z-score rows observed upstream. |
| alb2002_minimum_recipe_promotion_climate_shock_temp_z_rows | 384 | ALB_2002 diagnostic temperature z-score rows observed upstream. |
| alb2002_minimum_recipe_promotion_climate_shock_combined_stress_rows | 73 | ALB_2002 diagnostic combined climate-stress rows; not accepted treatment variables. |
| alb2002_minimum_recipe_promotion_climate_shock_climate_ready_rows | 0 | ALB_2002 shock diagnostic rows ready for climate linkage; intentionally zero. |
| alb2002_minimum_recipe_promotion_climate_shock_data_write_ready_rows | 0 | ALB_2002 shock diagnostic rows allowed for data/ write; intentionally zero. |
| alb2002_minimum_recipe_promotion_climate_outcome_linked_rows | 14396 | ALB_2002 temp-only household-window climate/outcome linked candidate rows observed upstream. |
| alb2002_minimum_recipe_promotion_climate_outcome_linked_households | 3599 | ALB_2002 households represented in the linked diagnostic candidate. |
| alb2002_minimum_recipe_promotion_climate_outcome_linked_windows | 4 | Diagnostic exposure windows per household in the linked candidate. |
| alb2002_minimum_recipe_promotion_climate_outcome_linked_precip_z_rows | 14396 | ALB_2002 linked diagnostic rainfall z-score rows. |
| alb2002_minimum_recipe_promotion_climate_outcome_linked_temp_z_rows | 14396 | ALB_2002 linked diagnostic temperature z-score rows. |
| alb2002_minimum_recipe_promotion_climate_outcome_linked_combined_stress_rows | 3092 | ALB_2002 linked diagnostic combined climate-stress rows; not accepted treatment variables. |
| alb2002_minimum_recipe_promotion_climate_outcome_linked_climate_ready_rows | 0 | ALB_2002 linked rows ready for promoted climate linkage; intentionally zero. |
| alb2002_minimum_recipe_promotion_climate_outcome_linked_data_write_ready_rows | 0 | ALB_2002 linked rows allowed for data/ write; intentionally zero. |
| alb2002_minimum_recipe_promotion_climate_linkage_ready_rows | 0 | Existing ALB_2002 climate-linkage-ready rows observed from geography audits. |
| alb2002_minimum_recipe_promotion_current_decision | blocked_alb2002_minimum_recipe_not_ready_for_promotion | Current fail-closed ALB_2002 minimum recipe promotion decision. |

## Action Queue

| action_rank | gate_id | blocker_domain | blocking_status | required_resolution |
|---|---|---|---|---|
| 1 | official_geography_artifacts | climate_geography | blocked_no_verified_2002_boundary_or_gps_artifact | Obtain or verify official ALB_2002 geography/GPS/EA-map files, district/commune codebooks, or a 2001/2002 distri... |
| 2 | historical_boundary_crosswalk | climate_geography | blocked_name_coverage_without_historical_provenance | Resolve duplicate/ambiguous boundary keys and verify the source as a 2001/2002 district layer or document a loss... |
| 3 | oop_aggregation | financial_protection_outcome | blocked_mixed_recall_gift_scope_period_alignment_and_aggregation_review | Use the no-positive-leakage skipped-payment decision and monthly-equivalent CHE stress tests, then choose and do... |
| 4 | consumption_sdg_denominator | financial_protection_denominator | blocked_sdg_discretionary_budget_inputs_not_ready | Use the documented total-budget denominator, then add SPL, PPP/CPI, and discretionary-budget handling before SDG... |
| 5 | access_need_denominator | access_outcome | blocked_need_access_denominator_and_barrier_scope | Verify illness/need denominator, care-seeking/referral denominator, reason-not-sought coding, and cost/distance/... |
| 6 | keys_weights_merge | household_merge_and_survey_design | blocked_recipe_promotion_review_not_complete | Promote household frame, key uniqueness, survey weight, timing, denominator, OOP, and access/need decisions only... |

## Promotion Gates

| gate_id | required_for | current_status | current_evidence | minimum_evidence_to_pass |
|---|---|---|---|---|
| household_frame | harmonized_household_dataset | candidate_not_ready | temp candidate rows=3599; core decision=temp_candidate_timing_geography_observed_outcome_semantics_pending; reci... | Complete household frame, key uniqueness/cardinality, module coverage, and raw lineage are verified. |
| survey_weight | weighted_descriptive_and_modeling | candidate_not_ready | household weight rows=3599; candidate rows=3599; weight-design audit rows=6; raw positive weights=3599; key-matc... | Official household weight target population, normalization, and survey-design variance use are verified and pres... |
| interview_timing | climate_linkage | candidate_not_ready | survey month rows=3599; interview date rows=3599 | Interview month/date values are accepted for the analysis rows, with exposure-window implications documented. |
| consumption_denominator | CHE10_CHE25_and_SDG_denominator | blocked | total consumption rows=3599; positive total consumption rows=3599; raw totcons positive rows=3599; candidate tot... | Documented total-budget denominator is accepted with OOP alignment, missing rules, SPL/PPP/CPI, and SDG discreti... |
| oop_aggregation | CHE10_CHE25_and_OOP_outcomes | blocked | raw OOP candidates=25; questionnaire OOP rows=25; NEW LEKS rows=31; gift rows=6; policy stress rows=11; max CHE1... | OOP item scope, recall period, period alignment, annualization, gift/payment inclusion, residual missing rules, ... |
| health_need_access | forgone_care_and_double_failure_outcomes | blocked | raw access candidates=8; questionnaire access rows=8; denominator policy rows=24; q01 need rows=3247; person nee... | Illness/need, care-seeking, and barrier value labels and skip paths are verified. |
| climate_geography | climate_linkage | blocked | district groups=36; crosswalk climate-ready=0; GADM climate-ready=0; manual climate-ready=0; follow-up climate-r... | GPS/cluster coordinates or a verified 2001/2002 district boundary/crosswalk are available for the household geog... |
| outcome_promotion | household_outcomes | blocked | provisional outcome-ready rows=0; raw semantics outcome-ready rows=0; questionnaire outcome-ready rows=0; consum... | Key, weight, consumption, OOP, and access/need gates pass, with event-rate and missingness audits. |
| harmonized_dataset_promotion | data/harmonized_household.csv | blocked | core recipe-ready rows=0; questionnaire recipe-ready rows=0; OOP policy recipe-ready rows=0; period-aligned CHE ... | Required household frame, key, weight, denominator, OOP, and minimum outcome variables all pass value/key/unit r... |
| climate_dataset_promotion | data/climate_linked_household.csv | blocked | questionnaire climate-ready=0; consumption denominator climate-ready=0; period-aligned CHE climate-ready=0; acce... | Harmonized dataset, accepted outcomes, verified timing, and verified climate geography all pass. |

## Interpretation

- ALB_2002 has the strongest local candidate evidence because household timing, district codes, weights, consumption, and OOP/access signals are visible in raw audits.
- The minimum harmonized dataset is still blocked by weight/design inference semantics, OOP aggregation policy, gift/payment scope, mixed recall periods, SDG denominator handling, access-denominator policy acceptance, and recipe promotion review. The skipped-payment positive-leakage check is documented separately as zero-only, and the period-aligned CHE audit supplies monthly-equivalent stress-test rates for downstream temp-only CHE candidate outcomes without promoting final outcomes.
- Climate linkage is separately blocked by the absence of a verified 2001/2002 district boundary, official GPS/EA-map artifact, or accepted historical crosswalk. GADM 3.6 is a useful lead with complete name coverage, but it has duplicate SHKODER rows and no verified 2002 provenance in this workspace. The household-window climate/outcome linked candidate is mechanical diagnostic evidence only and remains outside `data/`.
- This packet preserves the line between a promising temp candidate and promoted analytical data.

## Machine-Readable Outputs

- `temp/alb2002_minimum_recipe_promotion_action_queue.csv`
- `temp/alb2002_minimum_recipe_promotion_gate_checklist.csv`
- `result/alb2002_minimum_recipe_promotion_summary.csv`
