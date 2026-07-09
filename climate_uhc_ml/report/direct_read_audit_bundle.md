# Direct-Read Audit Bundle

Status: reviewer/GPT-facing index only. Raw schemas and first-batch value/key summaries exist, but no harmonized analytical dataset has been promoted.

## Bottom Line

- Allowed evidence: official-source verification, public metadata/schema inventory, manual-download planning, public raw archive/schema evidence where present, first-batch raw value/key summaries, metadata-derived candidate maps, and fail-closed analysis protocols.
- Not allowed evidence yet: constructed UHC outcomes, climate-linked household data, descriptive prevalence, predictive ML, reduced-form causal estimates, mechanism analysis, causal ML, policy learning, or robustness results.
- Binding blocker: complete manual unit, recall-period, missing-code, skip-pattern, merge-key, and documentation review before promoting any country-wave into a harmonization recipe.

## Summary Metrics

| Metric | Value | Interpretation |
|---|---:|---|
| bundle_rows | 124 | Rows in result/direct_read_audit_bundle.csv. |
| manifest_rows | 492 | Curated artifact rows in result/direct_read_artifact_manifest.csv. |
| manifest_present_nonempty | 488 | Curated artifacts present and non-empty. |
| manifest_missing_or_empty | 4 | Curated artifacts missing or empty. |
| raw_file_inventory_rows | 209 | Raw tabular files inspected. |
| raw_variable_catalog_rows | 5410 | Raw variables inspected. |
| analysis_ready_data_files | 0 | Dataset-like files currently present in data/, excluding README/.gitkeep. |
| promoted_data_gate_status | closed_no_promoted_rows | Current promoted-data write gate status. |
| promoted_data_gate_registry_promoted_rows | 0 | Registry rows currently allowed to write promoted datasets into data/. |
| promoted_data_gate_quarantined_files | 4 | Pre-promotion diagnostic files moved from data/ to temp/. |
| priority_archive_preflight_targets | 156 | Priority file targets checked against direct files and archive members. |
| priority_archive_preflight_missing_targets | 156 | Priority file targets still missing after direct/archive member preflight. |
| analysis_dataset_promotion_audit_rows | 6 | Analysis dataset promotion targets checked. |
| analysis_dataset_promotion_blocked_rows | 2 | Promotion targets blocked from data/. |
| analysis_dataset_promotion_promoted_rows | 4 | Promotion targets allowed for data/ writes; limited core/outcome/exposure/linked diagnostic files are allowed while model-ready data remain blocked. |
| analysis_dataset_promotion_data_file_count | 4 | Files currently present under data/. |
| analysis_dataset_promotion_verified_recipe_candidates | 0 | Verified recipe candidates carried into the promotion-barrier audit. |
| analysis_dataset_promotion_ready_country_waves | 0 | Ready country-waves carried into the promotion-barrier audit. |
| analysis_dataset_promotion_alb2002_temp_core_rows | 3599 | ALB_2002 temp core rows carried into the promotion-barrier audit. |
| analysis_dataset_promotion_alb2002_weight_positive_rows | 3599 | ALB_2002 positive household-weight rows carried into the promotion-barrier audit. |
| analysis_dataset_promotion_alb2002_weight_key_match_rows | 3599 | ALB_2002 weight-file key matches carried into the promotion-barrier audit. |
| analysis_dataset_promotion_alb2002_weighted_inference_ready_rows | 0 | ALB_2002 rows ready for promoted weighted inference; should remain zero. |
| analysis_dataset_promotion_alb2002_harmonized_ready_rows | 0 | ALB_2002 harmonized rows ready for promotion; should remain zero. |
| analysis_dataset_promotion_alb2002_outcome_ready_rows | 0 | ALB_2002 outcome rows ready for promotion; should remain zero. |
| analysis_dataset_promotion_alb2002_climate_linkage_ready_rows | 0 | ALB_2002 climate-linkage rows ready for promotion; should remain zero. |
| analysis_dataset_promotion_limited_harmonized_core_rows | 3599 | Rows written to data/harmonized_household.csv under limited scope. |
| analysis_dataset_promotion_limited_harmonized_core_data_write_ready_rows | 3599 | Rows allowed for data/ write only as limited harmonized household core. |
| analysis_dataset_promotion_limited_harmonized_core_final_outcome_ready_rows | 0 | Rows ready for final outcomes; should remain zero. |
| analysis_dataset_promotion_limited_harmonized_core_climate_linkage_ready_rows | 0 | Rows ready for climate linkage; should remain zero. |
| analysis_dataset_promotion_limited_financial_outcome_rows | 3599 | Rows written to data/household_outcomes.csv under limited CHE-only scope. |
| analysis_dataset_promotion_limited_financial_outcome_data_write_ready_rows | 3599 | Rows allowed for data/ write only as limited CHE10/CHE25 outcomes. |
| analysis_dataset_promotion_limited_financial_outcome_che10_rows | 824 | Limited CHE10 outcome rows. |
| analysis_dataset_promotion_limited_financial_outcome_che25_rows | 290 | Limited CHE25 outcome rows. |
| analysis_dataset_promotion_limited_financial_outcome_sdg382_ready_rows | 0 | Rows ready for SDG 3.8.2; should remain zero. |
| analysis_dataset_promotion_limited_financial_outcome_access_ready_rows | 0 | Rows ready for access outcomes; should remain zero. |
| analysis_dataset_promotion_limited_financial_outcome_composite_ready_rows | 0 | Rows ready for composite outcomes; should remain zero. |
| analysis_dataset_promotion_limited_financial_outcome_climate_linkage_ready_rows | 0 | Rows ready for climate linkage; should remain zero. |
| analysis_dataset_promotion_limited_climate_exposure_rows | 384 | Rows written to data/climate_exposures_nasa_power.csv under limited fallback scope. |
| analysis_dataset_promotion_limited_climate_exposure_data_write_ready_rows | 384 | Rows allowed for data/ write only as limited fallback climate exposures. |
| analysis_dataset_promotion_limited_climate_exposure_climate_linkage_ready_rows | 0 | Rows ready for final climate linkage; should remain zero. |
| analysis_dataset_promotion_limited_climate_linked_rows | 14396 | Rows written to data/climate_linked_household.csv under limited diagnostic scope. |
| analysis_dataset_promotion_limited_climate_linked_data_write_ready_rows | 14396 | Rows allowed for data/ write only as a limited linked diagnostic. |
| analysis_dataset_promotion_limited_climate_linked_descriptive_ready_rows | 0 | Limited linked rows ready for descriptive diagnostics; should remain zero. |
| analysis_dataset_promotion_limited_climate_linked_predictive_ml_ready_rows | 0 | Limited linked rows ready for predictive ML; should remain zero. |
| analysis_dataset_promotion_limited_climate_linked_reduced_form_ready_rows | 0 | Limited linked rows ready for reduced-form estimation; should remain zero. |
| analysis_dataset_promotion_limited_climate_linked_robustness_ready_rows | 0 | Limited linked rows ready for robustness checks; should remain zero. |
| analysis_dataset_promotion_limited_climate_linked_analysis_ready_rows | 0 | Limited linked rows ready for final analysis; should remain zero. |
| analysis_dataset_promotion_current_decision | limited_core_financial_outcomes_climate_exposures_and_linked_diagnostics_promoted_models_still_blocked | Current fail-closed analysis dataset promotion decision. |
| alb2002_harmonized_household_core_rows | 3599 | Rows in the limited ALB_2002 harmonized household core. |
| alb2002_harmonized_household_core_final_outcome_ready_rows | 0 | Limited-core rows ready for final outcomes; should remain zero. |
| alb2002_harmonized_household_core_climate_linkage_ready_rows | 0 | Limited-core rows ready for climate linkage; should remain zero. |
| alb2002_limited_financial_outcome_rows | 3599 | Rows in the limited ALB_2002 CHE-only outcome file. |
| alb2002_limited_financial_outcome_che10_rows | 824 | Limited CHE10 rows. |
| alb2002_limited_financial_outcome_che25_rows | 290 | Limited CHE25 rows. |
| alb2002_limited_financial_outcome_climate_linkage_ready_rows | 0 | Limited-outcome rows ready for climate linkage; should remain zero. |
| alb2002_limited_climate_exposure_rows | 384 | Rows in the limited ALB_2002 NASA POWER exposure file. |
| alb2002_limited_climate_exposure_climate_linkage_ready_rows | 0 | Limited-exposure rows ready for final climate linkage; should remain zero. |
| alb2002_limited_climate_linked_rows | 14396 | Rows in the limited ALB_2002 climate-linked diagnostic file. |
| alb2002_limited_climate_linked_household_rows | 3599 | Households in the limited climate-linked diagnostic file. |
| alb2002_limited_climate_linked_window_rows | 4 | Exposure windows per household in the limited linked file. |
| alb2002_limited_climate_linked_final_analysis_ready_rows | 0 | Limited linked rows ready for final analysis; should remain zero. |
| design_scorecard_rows | 38 | Rows in result/design_scorecard.csv after the current fail-closed refresh. |
| design_scorecard_current_rows | 3 | Current-state design rows appended to the broad metadata scorecard. |
| design_no_go_threshold_rows | 8 | Current design no-go threshold rows. |
| design_scorecard_data_write_ready_rows | 0 | Rows allowed for data/ write by the design scorecard; should remain zero. |
| design_scorecard_current_decision | fail_closed_design_scorecard_currently_no_go_for_estimation_or_policy_learning | Current fail-closed design scorecard decision. |
| alb2002_promotion_gate_delta_rows | 10 | ALB_2002 promotion gate delta rows. |
| alb2002_promotion_gate_delta_hard_blocked_rows | 4 | ALB_2002 hard-blocked promotion gates. |
| alb2002_promotion_gate_delta_data_write_ready_rows | 0 | Rows allowed for data/ write by the ALB_2002 promotion delta audit; should remain zero. |
| alb2002_promotion_gate_delta_decision | partial_gate_delta_documented_keep_data_empty_until_outcome_sdg_geography_gates_pass | Current ALB_2002 promotion-gate delta decision. |
| alb2002_boundary_blocker_resolution_rows | 11 | ALB_2002 boundary blocker resolution rows. |
| alb2002_boundary_blocker_candidate_name_coverage_rows | 3 | Public boundary leads with complete candidate name coverage but no promotion. |
| alb2002_boundary_blocker_climate_linkage_ready_rows | 0 | Rows ready for ALB_2002 boundary climate-linkage promotion; should remain zero. |
| alb2002_boundary_blocker_current_decision | blocked_no_alb2002_boundary_source_ready_for_climate_linkage | Current consolidated ALB_2002 boundary-source decision. |
| alb2002_outcome_blocker_resolution_rows | 12 | ALB_2002 outcome blocker resolution rows. |
| alb2002_outcome_blocker_candidate_not_promoted_rows | 11 | Candidate ALB_2002 outcome rows with evidence but no final promotion. |
| alb2002_outcome_blocker_outcome_ready_rows | 0 | Rows ready for final ALB_2002 outcome promotion; should remain zero. |
| alb2002_outcome_blocker_current_decision | blocked_no_alb2002_outcome_ready_for_promotion | Current consolidated ALB_2002 outcome promotion decision. |
| alb2012_timing_geography_blocker_resolution_rows | 10 | ALB_2012 fallback blocker rows. |
| alb2012_timing_geography_blocker_hard_blocked_rows | 10 | ALB_2012 rows hard-blocked from fallback promotion. |
| alb2012_timing_geography_blocker_climate_linkage_ready_rows | 0 | Rows ready for ALB_2012 climate-linkage fallback; should remain zero. |
| alb2012_timing_geography_blocker_current_decision | blocked_alb2012_no_timing_geography_fallback_ready | Current consolidated ALB_2012 fallback decision. |
| alb2005_fallback_blocker_resolution_rows | 12 | ALB_2005 fallback blocker rows. |
| alb2005_fallback_blocker_hard_blocked_rows | 12 | ALB_2005 rows hard-blocked from fallback promotion. |
| alb2005_fallback_blocker_harmonized_ready_rows | 0 | Rows ready for ALB_2005 harmonized-data fallback; should remain zero. |
| alb2005_fallback_blocker_outcome_ready_rows | 0 | Rows ready for ALB_2005 outcome fallback; should remain zero. |
| alb2005_fallback_blocker_interview_timing_ready_rows | 0 | Rows with verified ALB_2005 fallback interview timing; should remain zero. |
| alb2005_fallback_blocker_geography_ready_rows | 0 | Rows with promoted ALB_2005 fallback geography; should remain zero. |
| alb2005_fallback_blocker_climate_linkage_ready_rows | 0 | Rows ready for ALB_2005 climate-linkage fallback; should remain zero. |
| alb2005_fallback_blocker_data_write_ready_rows | 0 | Rows allowed for ALB_2005 fallback data/ writes; should remain zero. |
| alb2005_fallback_blocker_current_decision | blocked_alb2005_no_fallback_ready | Current consolidated ALB_2005 fallback decision. |
| alb2008_fallback_blocker_resolution_rows | 10 | ALB_2008 fallback blocker rows. |
| alb2008_fallback_blocker_hard_blocked_rows | 10 | ALB_2008 rows hard-blocked from fallback promotion. |
| alb2008_fallback_blocker_interview_timing_ready_rows | 0 | Rows with verified ALB_2008 fallback interview timing; should remain zero. |
| alb2008_fallback_blocker_geography_ready_rows | 0 | Rows with promoted ALB_2008 fallback geography; should remain zero. |
| alb2008_fallback_blocker_outcome_ready_rows | 0 | Rows ready for ALB_2008 outcome fallback; should remain zero. |
| alb2008_fallback_blocker_climate_linkage_ready_rows | 0 | Rows ready for ALB_2008 climate-linkage fallback; should remain zero. |
| alb2008_fallback_blocker_data_write_ready_rows | 0 | Rows allowed for ALB_2008 fallback data/ writes; should remain zero. |
| alb2008_fallback_blocker_current_decision | blocked_alb2008_no_timing_geography_fallback_ready | Current consolidated ALB_2008 fallback decision. |
| no_go_pass_rows | 2 | Pre-specified no-go rows passing. |
| no_go_blocked_rows | 6 | Pre-specified no-go rows blocked or failing. |
| alb2002_household_core_recipe_ready_rows | 0 | ALB_2002 household core rows ready for data promotion. |
| alb2002_weight_design_positive_weight_rows | 3599 | ALB_2002 readable positive household-weight rows. |
| alb2002_weight_design_candidate_key_match_rows | 3599 | ALB_2002 readable weight-file key matches to the temp core. |
| alb2002_weight_design_weighted_inference_ready_rows | 0 | ALB_2002 rows ready for promoted weighted inference; should remain zero. |
| alb2002_che_candidate_household_rows | 3599 | ALB_2002 temp-only household CHE candidate rows. |
| alb2002_che_candidate_che10_rows | 824 | ALB_2002 candidate CHE10 rows under the period-aligned combined OOP policy. |
| alb2002_che_candidate_che10_weighted_rate | 0.23666 | ALB_2002 candidate weighted CHE10 rate; audit only. |
| alb2002_che_candidate_che25_rows | 290 | ALB_2002 candidate CHE25 rows under the period-aligned combined OOP policy. |
| alb2002_che_candidate_che25_weighted_rate | 0.0859036 | ALB_2002 candidate weighted CHE25 rate; audit only. |
| alb2002_che_candidate_outcome_promotion_ready_rows | 0 | ALB_2002 candidate outcome rows ready for final promotion; should remain zero. |
| alb2002_access_candidate_household_rows | 3599 | ALB_2002 temp-only household access candidate rows. |
| alb2002_access_candidate_composite_any_rows | 1861 | ALB_2002 temp-only composite any-access-barrier rows. |
| alb2002_access_candidate_composite_any_weighted_rate | 0.528953 | ALB_2002 candidate weighted composite any-access-barrier rate; audit only. |
| alb2002_access_candidate_outcome_promotion_ready_rows | 0 | ALB_2002 access candidate rows ready for final promotion; should remain zero. |
| alb2002_uhc_composite_candidate_household_rows | 3599 | ALB_2002 temp-only composite UHC candidate rows. |
| alb2002_uhc_composite_candidate_che10_or_access_rows | 2004 | ALB_2002 temp-only CHE10-or-access candidate rows. |
| alb2002_uhc_composite_candidate_che10_or_access_weighted_rate | 0.570531 | ALB_2002 candidate weighted CHE10-or-access rate; audit only. |
| alb2002_uhc_composite_candidate_che25_or_access_rows | 1889 | ALB_2002 temp-only CHE25-or-access candidate rows. |
| alb2002_uhc_composite_candidate_outcome_promotion_ready_rows | 0 | ALB_2002 composite UHC candidate rows ready for final promotion; should remain zero. |
| alb2002_analysis_candidate_rows | 3599 | ALB_2002 temp-only joined analysis-candidate household rows. |
| alb2002_analysis_candidate_complete_candidate_gates | 9 | ALB_2002 candidate field families with complete observed coverage, still not promoted. |
| alb2002_analysis_candidate_missing_gates | 1 | ALB_2002 candidate field families with missing required coverage. |
| alb2002_analysis_candidate_harmonized_ready_rows | 0 | ALB_2002 analysis-candidate rows ready for harmonized data promotion; should remain zero. |
| alb2002_analysis_candidate_data_write_ready_rows | 0 | ALB_2002 analysis-candidate rows allowed to be written to data/; should remain zero. |
| alb2002_climate_centroid_input_rows | 96 | ALB_2002 observed district-month cells used for the temp-only climate centroid stress test. |
| alb2002_climate_centroid_exposure_rows | 384 | ALB_2002 temp-only NASA POWER centroid exposure rows. |
| alb2002_climate_centroid_nasa_api_rows | 36 | ALB_2002 district centroid API/cache manifest rows. |
| alb2002_climate_centroid_nasa_failed_rows | 0 | ALB_2002 NASA POWER district centroid requests that failed. |
| alb2002_climate_centroid_climate_linkage_ready_rows | 0 | ALB_2002 centroid exposure rows ready for promoted climate linkage; should remain zero. |
| alb2002_climate_centroid_data_write_ready_rows | 0 | ALB_2002 centroid exposure rows allowed for data/ write; should remain zero. |
| alb2002_climate_shock_candidate_exposure_rows | 384 | ALB_2002 temp-only climate shock diagnostic rows. |
| alb2002_climate_shock_candidate_reference_group_rows | 16 | ALB_2002 survey-month/window diagnostic reference groups. |
| alb2002_climate_shock_candidate_precip_z_nonmissing_rows | 384 | ALB_2002 diagnostic rainfall z-score rows. |
| alb2002_climate_shock_candidate_temp_z_nonmissing_rows | 384 | ALB_2002 diagnostic temperature z-score rows. |
| alb2002_climate_shock_candidate_combined_stress_rows | 73 | ALB_2002 diagnostic combined climate-stress rows; not accepted treatments. |
| alb2002_climate_shock_candidate_climate_linkage_ready_rows | 0 | ALB_2002 shock diagnostic rows ready for promoted climate linkage; should remain zero. |
| alb2002_climate_shock_candidate_data_write_ready_rows | 0 | ALB_2002 shock diagnostic rows allowed for data/ write; should remain zero. |
| alb2002_climate_outcome_linked_candidate_rows | 14396 | ALB_2002 temp-only household-window climate/outcome linked candidate rows. |
| alb2002_climate_outcome_linked_candidate_household_rows | 3599 | ALB_2002 households represented in the linked candidate. |
| alb2002_climate_outcome_linked_candidate_window_rows | 4 | Diagnostic exposure windows per household in the linked candidate. |
| alb2002_climate_outcome_linked_candidate_unmatched_rows | 0 | Linked rows without diagnostic climate windows; should remain zero. |
| alb2002_climate_outcome_linked_candidate_combined_stress_rows | 3092 | ALB_2002 linked diagnostic combined climate-stress rows; not accepted treatment variables. |
| alb2002_climate_outcome_linked_candidate_climate_linkage_ready_rows | 0 | ALB_2002 linked rows ready for promoted climate linkage; should remain zero. |
| alb2002_climate_outcome_linked_candidate_data_write_ready_rows | 0 | ALB_2002 linked rows allowed for data/ write; should remain zero. |
| alb2002_linked_candidate_descriptive_input_rows | 14396 | ALB_2002 temp-only linked household-window rows screened descriptively. |
| alb2002_linked_candidate_descriptive_household_rows | 3599 | Deduplicated ALB_2002 households used for candidate outcome rates. |
| alb2002_linked_candidate_descriptive_cell_rows | 108 | Temp-only descriptive screen cell rows; not promoted descriptive diagnostics. |
| alb2002_linked_candidate_descriptive_combined_stress_rows | 3092 | Long rows with diagnostic combined climate-stress flag in the descriptive screen. |
| alb2002_linked_candidate_descriptive_climate_linkage_ready_rows | 0 | Rows ready for promoted climate linkage in the descriptive screen; should remain zero. |
| alb2002_linked_candidate_descriptive_data_write_ready_rows | 0 | Rows allowed for data/ write from the descriptive screen; should remain zero. |
| alb2002_provisional_outcome_ready_rows | 0 | ALB_2002 provisional outcome rows ready for final outcome promotion. |
| alb2002_outcome_semantics_outcome_ready_rows | 0 | ALB_2002 raw semantics rows ready for final outcome promotion. |
| alb2002_outcome_semantics_sdg382_ready_rows | 0 | ALB_2002 raw semantics rows ready for SDG 3.8.2 construction. |
| alb2002_health_questionnaire_semantics_rows | 65 | ALB_2002 questionnaire-backed health semantics and skip-path rows. |
| alb2002_health_questionnaire_new_lek_unit_rows | 31 | ALB_2002 questionnaire rows explicitly recording NEW LEKS payment units. |
| alb2002_health_questionnaire_four_week_oop_rows | 17 | ALB_2002 OOP item rows with past-four-week recall. |
| alb2002_health_questionnaire_twelve_month_oop_rows | 8 | ALB_2002 OOP item rows with past-12-month recall. |
| alb2002_health_questionnaire_payment_positive_when_not_triggered_rows | 0 | ALB_2002 skipped payment downstream rows with positive values; should remain zero. |
| alb2002_health_questionnaire_outcome_ready_rows | 0 | ALB_2002 questionnaire rows ready for final outcome promotion; should remain zero. |
| alb2002_health_questionnaire_sdg382_ready_rows | 0 | ALB_2002 questionnaire rows ready for SDG 3.8.2 construction; should remain zero. |
| alb2002_health_questionnaire_climate_linkage_ready_rows | 0 | ALB_2002 questionnaire rows ready for climate linkage; should remain zero. |
| alb2002_oop_aggregation_policy_rows | 11 | ALB_2002 OOP aggregation policy stress-test rows. |
| alb2002_oop_aggregation_policy_max_che10_rate | 0.707697 | Maximum unweighted CHE10 rate across ALB_2002 stress-test policies; not a final estimate. |
| alb2002_oop_aggregation_policy_max_che25_rate | 0.56738 | Maximum unweighted CHE25 rate across ALB_2002 stress-test policies; not a final estimate. |
| alb2002_oop_aggregation_policy_core_4w_match_rows | 3599 | ALB_2002 rows where recomputed four-week OOP matches the existing core candidate sum. |
| alb2002_oop_aggregation_policy_core_12m_match_rows | 3599 | ALB_2002 rows where recomputed 12-month OOP matches the existing core candidate sum. |
| alb2002_oop_aggregation_policy_outcome_ready_rows | 0 | ALB_2002 OOP policy rows ready for outcome promotion; should remain zero. |
| alb2002_oop_aggregation_policy_sdg382_ready_rows | 0 | ALB_2002 OOP policy rows ready for SDG 3.8.2 promotion; should remain zero. |
| alb2002_oop_aggregation_policy_climate_linkage_ready_rows | 0 | ALB_2002 OOP policy rows ready for climate linkage; should remain zero. |
| alb2002_skip_missing_semantics_rows | 12 | ALB_2002 skip/missing semantics audit rows. |
| alb2002_skip_missing_payment_positive_when_not_triggered_rows | 0 | ALB_2002 skipped payment rows with positive downstream values; should remain zero. |
| alb2002_skip_missing_payment_zero_cells_when_not_triggered | 11 | ALB_2002 skipped payment downstream cells equal zero; downstream decision audit records no positive leakage. |
| alb2002_skip_missing_payment_positive_cells_when_not_triggered | 0 | ALB_2002 skipped payment downstream cells positive; should remain zero. |
| alb2002_skip_missing_outcome_ready_rows | 0 | ALB_2002 skip/missing rows ready for outcome promotion; should remain zero. |
| alb2002_skip_missing_sdg382_ready_rows | 0 | ALB_2002 skip/missing rows ready for SDG 3.8.2 promotion; should remain zero. |
| alb2002_skip_missing_climate_linkage_ready_rows | 0 | ALB_2002 skip/missing rows ready for climate linkage; should remain zero. |
| alb2002_oop_skip_value_decision_rows | 5 | ALB_2002 OOP skip-value decision audit rows. |
| alb2002_oop_skip_value_payment_zero_skipped_cells | 11 | ALB_2002 zero-valued downstream payment cells when payment block was not triggered. |
| alb2002_oop_skip_value_payment_positive_skipped_rows | 0 | ALB_2002 rows with positive downstream payment values when payment block was not triggered; should remain zero. |
| alb2002_oop_skip_value_payment_positive_skipped_cells | 0 | ALB_2002 positive downstream payment cells when payment block was not triggered; should remain zero. |
| alb2002_oop_skip_value_zero_skip_policy_ready_rows | 4 | ALB_2002 rows supporting the narrow no-positive-leakage skipped-payment decision. |
| alb2002_oop_skip_value_oop_recall_scope_ready_rows | 0 | ALB_2002 OOP recall scope rows accepted by skip-value audit; should remain zero. |
| alb2002_oop_skip_value_oop_inclusion_scope_ready_rows | 0 | ALB_2002 OOP inclusion scope rows accepted by skip-value audit; should remain zero. |
| alb2002_oop_skip_value_outcome_ready_rows | 0 | ALB_2002 OOP skip-value rows ready for outcome promotion; should remain zero. |
| alb2002_access_need_denominator_policy_rows | 24 | ALB_2002 access/need denominator policy audit rows. |
| alb2002_access_need_q01_need_rows | 3247 | ALB_2002 households not coded as no-one-needed-health-care in m5b_q01. |
| alb2002_access_need_person_need_household_rows | 2202 | ALB_2002 households with any Health A chronic/disability or sudden-illness proxy. |
| alb2002_access_need_composite_any_access_barrier_rows | 1861 | ALB_2002 composite any-access-barrier candidate rows; not a final outcome. |
| alb2002_access_need_low_event_rate_rows | 3 | ALB_2002 access/need policies with event rate below 3 percent. |
| alb2002_access_need_outcome_ready_rows | 0 | ALB_2002 access/need rows ready for outcome promotion; should remain zero. |
| alb2002_access_need_climate_linkage_ready_rows | 0 | ALB_2002 access/need rows ready for climate linkage; should remain zero. |
| alb2002_consumption_sdg_denominator_policy_rows | 14 | ALB_2002 consumption/SDG denominator policy audit rows. |
| alb2002_consumption_sdg_positive_total_consumption_rows | 3599 | ALB_2002 rows with positive total consumption in the temp candidate. |
| alb2002_consumption_sdg_che10_4w_unreviewed_rate | 0.173937 | Diagnostic ALB_2002 CHE10 rate using unreviewed four-week OOP; not a final outcome. |
| alb2002_consumption_sdg_che25_12m_unreviewed_rate | 0.165046 | Diagnostic ALB_2002 CHE25 rate using unreviewed 12-month OOP; not a final outcome. |
| alb2002_consumption_sdg_spl_ready_rows | 0 | ALB_2002 rows with SPL inputs accepted; should remain zero. |
| alb2002_consumption_sdg_ppp_cpi_ready_rows | 0 | ALB_2002 rows with PPP/CPI inputs accepted; should remain zero. |
| alb2002_consumption_sdg_discretionary_budget_ready_rows | 0 | ALB_2002 rows with discretionary-budget construction accepted; should remain zero. |
| alb2002_consumption_sdg_outcome_ready_rows | 0 | ALB_2002 consumption/SDG rows ready for outcome promotion; should remain zero. |
| alb2002_consumption_sdg_sdg382_ready_rows | 0 | ALB_2002 rows ready for SDG 3.8.2 construction; should remain zero. |
| alb2002_consumption_sdg_climate_linkage_ready_rows | 0 | ALB_2002 consumption/SDG rows ready for climate linkage; should remain zero. |
| alb2002_consumption_construction_source_audit_rows | 9 | ALB_2002 public consumption-construction source audit rows. |
| alb2002_consumption_construction_do_file_rows | 19 | Extracted public ALB_2002 Stata do-files documenting consumption construction. |
| alb2002_consumption_construction_documentation_ready_rows | 9 | ALB_2002 source-audit rows with accepted public construction documentation. |
| alb2002_consumption_construction_released_variable_mapping_ready_rows | 3 | ALB_2002 source-audit rows supporting local `totcons` to public `totcons3` mapping. |
| alb2002_consumption_construction_denominator_variant_ready_rows | 8 | ALB_2002 source-audit rows documenting the final total-budget denominator variant. |
| alb2002_consumption_construction_outcome_ready_rows | 0 | ALB_2002 source-audit rows ready for outcome promotion; should remain zero. |
| alb2002_consumption_construction_sdg382_ready_rows | 0 | ALB_2002 source-audit rows ready for SDG 3.8.2 promotion; should remain zero. |
| alb2002_consumption_construction_climate_linkage_ready_rows | 0 | ALB_2002 source-audit rows ready for climate linkage; should remain zero. |
| alb2002_consumption_aggregate_crosswalk_rows | 11 | ALB_2002 consumption aggregate metadata/local evidence crosswalk rows. |
| alb2002_consumption_aggregate_crosswalk_metadata_catalog_rows | 0 | Local master metadata rows available for ALB_2002 aggregate verification; public source evidence now sits in the construction-source audit instead. |
| alb2002_consumption_aggregate_crosswalk_candidate_totcons_match_rows | 3599 | ALB_2002 candidate total_consumption rows exactly matching raw `totcons`. |
| alb2002_consumption_aggregate_crosswalk_construction_source_rows | 9 | Rows imported from the upstream ALB_2002 public consumption-construction source audit. |
| alb2002_consumption_aggregate_crosswalk_construction_do_file_rows | 19 | Extracted public Stata do-files used as ALB_2002 denominator-construction evidence. |
| alb2002_consumption_aggregate_crosswalk_official_documentation_ready_rows | 9 | ALB_2002 rows with accepted public aggregate-construction documentation. |
| alb2002_consumption_aggregate_crosswalk_released_variable_mapping_ready_rows | 3 | ALB_2002 rows supporting the local `totcons` to public `totcons3` mapping. |
| alb2002_consumption_aggregate_crosswalk_denominator_variant_ready_rows | 8 | ALB_2002 rows documenting the total-budget denominator variant. |
| alb2002_consumption_aggregate_crosswalk_sdg382_ready_rows | 0 | ALB_2002 aggregate crosswalk rows ready for SDG 3.8.2 promotion; should remain zero. |
| alb2002_period_aligned_che_policy_rows | 3 | ALB_2002 period-aligned CHE stress-test policy rows. |
| alb2002_period_aligned_che_period_alignment_ready_rows | 3 | ALB_2002 period-aligned CHE rows ready for stress testing, not outcome promotion. |
| alb2002_period_aligned_che_combined_che10_rate | 0.228952 | Combined monthly-equivalent unweighted CHE10 rate for ALB_2002 no-gifts-with-transport stress test. |
| alb2002_period_aligned_che_combined_che25_rate | 0.0805779 | Combined monthly-equivalent unweighted CHE25 rate for ALB_2002 no-gifts-with-transport stress test. |
| alb2002_period_aligned_che_outcome_ready_rows | 0 | ALB_2002 period-aligned CHE rows promoted to final outcomes; should remain zero. |
| alb2002_period_aligned_che_current_decision | blocked_alb2002_period_aligned_che_policy_not_outcome_ready | Current ALB_2002 period-aligned CHE policy decision. |
| alb2002_minimum_recipe_promotion_action_rows | 6 | ALB_2002 minimum recipe promotion action rows. |
| alb2002_minimum_recipe_promotion_gate_rows | 10 | ALB_2002 minimum recipe promotion gate rows. |
| alb2002_minimum_recipe_promotion_blocked_gates | 7 | ALB_2002 minimum recipe gates still blocked. |
| alb2002_minimum_recipe_promotion_harmonized_ready_rows | 0 | ALB_2002 rows ready for harmonized data promotion; should remain zero. |
| alb2002_minimum_recipe_promotion_outcome_ready_rows | 0 | ALB_2002 rows ready for outcome promotion; should remain zero. |
| alb2002_minimum_recipe_promotion_sdg382_ready_rows | 0 | ALB_2002 rows ready for SDG 3.8.2 promotion; should remain zero. |
| alb2002_minimum_recipe_promotion_climate_linkage_ready_rows | 0 | ALB_2002 rows ready for climate linkage after minimum recipe gates; should remain zero. |
| alb2002_climate_linkage_ready_rows | 0 | ALB_2002 district crosswalk rows ready for climate linkage. |
| alb2002_boundary_name_match_unmatched_survey_rows | 1 | ALB_2002 survey district rows unmatched to public current boundary names. |
| alb2002_boundary_name_match_duplicate_boundary_name_keys | 2 | Duplicate public current boundary-name keys in the ALB_2002 boundary audit. |
| alb2002_boundary_name_match_historical_year_ready_rows | 0 | ALB_2002 boundary-name rows ready for 2002 historical boundary validation. |
| alb2002_boundary_name_match_climate_linkage_ready_rows | 0 | ALB_2002 boundary-name rows ready for climate-linkage promotion. |
| alb2002_boundary_resource_search_complete_name_coverage_rows | 1 | ALB_2002 boundary resources with complete district-name coverage after documented repairs. |
| alb2002_boundary_resource_search_exact_unit_count_rows | 1 | ALB_2002 boundary resources whose feature and distinct-key counts match the 36 district groups. |
| alb2002_boundary_resource_search_2002_historical_ready_rows | 0 | ALB_2002 boundary resources verified as 2002 historical inputs. |
| alb2002_boundary_resource_search_climate_linkage_ready_rows | 0 | ALB_2002 boundary resources ready for climate-linkage promotion. |
| alb2002_boundary_geometry_feature_rows | 36 | Features parsed in the best ALB_2002 boundary lead. |
| alb2002_boundary_geometry_metadata_boundary_year | 2013 | Boundary year reported by the candidate boundary metadata. |
| alb2002_boundary_geometry_boundary_year_matches_2002_rows | 0 | Candidate geometry rows whose metadata verifies a 2002 boundary vintage. |
| alb2002_boundary_geometry_historical_2002_boundary_ready_rows | 0 | Geometry/provenance rows ready as verified 2002 boundary inputs. |
| alb2002_boundary_geometry_climate_linkage_ready_rows | 0 | Geometry/provenance rows ready for climate-linkage promotion. |
| alb2002_boundary_manual_verification_action_rows | 7 | Manual source/action rows for resolving ALB_2002 boundary verification. |
| alb2002_boundary_manual_verification_gate_rows | 9 | Manual boundary promotion-gate checklist rows. |
| alb2002_boundary_manual_verification_blocked_gates | 6 | Manual boundary verification gates still blocked. |
| alb2002_boundary_manual_verification_pre2011_digital_map_absence_rows | 1 | Negative-evidence rows documenting pre-2011 national digital map absence. |
| alb2002_boundary_manual_verification_climate_linkage_ready_rows | 0 | Manual verification packet rows ready for climate-linkage promotion. |
| alb2002_boundary_manual_source_followup_rows | 7 | Manual-source follow-up rows for ALB_2002 boundary leads. |
| alb2002_boundary_manual_source_followup_conclusive_blocker_rows | 7 | ALB_2002 source leads with documented blockers after follow-up. |
| alb2002_boundary_manual_source_followup_district_level_ready_rows | 0 | ALB_2002 source leads verified as district-level-ready after follow-up. |
| alb2002_boundary_manual_source_followup_climate_linkage_ready_rows | 0 | ALB_2002 source leads ready for climate-linkage promotion after follow-up. |
| alb2002_boundary_manual_source_followup_unece_pre2011_map_status | blocked_pre2011_digital_boundary_source_absence_documented | UNECE/INSTAT pre-2011 national digital map availability blocker status. |
| alb2002_gadm_boundary_lead_candidate_rows | 2 | GADM Albania ADM2 source candidates audited for ALB_2002 boundary linkage. |
| alb2002_gadm36_adm2_row_count | 37 | GADM 3.6 Albania ADM2 feature rows. |
| alb2002_gadm36_distinct_normalized_key_count | 36 | GADM 3.6 normalized district keys after documented name repairs. |
| alb2002_gadm36_complete_name_coverage_rows | 1 | Whether GADM 3.6 covers all ALB_2002 district keys by normalized name. |
| alb2002_gadm36_duplicate_boundary_key_count | 1 | Duplicated GADM 3.6 normalized district keys that block automatic promotion. |
| alb2002_gadm_boundary_lead_climate_linkage_ready_rows | 0 | GADM boundary lead rows ready for ALB_2002 climate-linkage promotion; should remain zero. |
| alb2012_household_core_recipe_ready_rows | 0 | ALB_2012 household core rows ready for data promotion. |
| alb2012_climate_linkage_ready_rows | 0 | ALB_2012 rows ready for climate linkage. |
| alb2012_provisional_outcome_ready_rows | 0 | ALB_2012 provisional outcome rows ready for final outcome promotion. |
| alb2012_outcome_semantics_outcome_ready_rows | 0 | ALB_2012 raw semantics rows ready for final outcome promotion. |
| alb2012_outcome_semantics_sdg382_ready_rows | 0 | ALB_2012 raw semantics rows ready for SDG 3.8.2 construction. |
| alb2012_outcome_semantics_climate_linkage_ready_rows | 0 | ALB_2012 raw semantics rows ready for climate linkage. |
| alb2012_timing_geography_climate_linkage_ready_rows | 0 | ALB_2012 timing/geography rows ready for climate linkage. |
| alb2012_questionnaire_timing_field_rows | 29 | ALB_2012 questionnaire timing/control field rows. |
| alb2012_questionnaire_timing_raw_verified_interview_timing_rows | 0 | ALB_2012 raw household interview timing rows verified after questionnaire review. |
| alb2012_questionnaire_timing_climate_linkage_ready_rows | 0 | ALB_2012 questionnaire timing rows ready for climate linkage. |
| albania_legacy_questionnaire_present_files | 5 | ALB_2002/2005/2008 legacy questionnaire files present locally. |
| albania_legacy_questionnaire_read_ok_files | 5 | Legacy questionnaire files readable in the current environment. |
| albania_legacy_questionnaire_climate_linkage_ready_rows | 0 | Legacy questionnaire rows ready for climate linkage. |
| albania_legacy_questionnaire_timing_field_rows | 83 | Legacy questionnaire timing/control field rows. |
| albania_legacy_questionnaire_timing_raw_verified_interview_timing_rows | 3599 | Verified raw household interview timing rows across legacy Albania waves. |
| albania_legacy_questionnaire_timing_climate_linkage_ready_rows | 0 | Legacy questionnaire timing rows ready for climate linkage. |
| alb2005_recipe_ready_rows | 0 | ALB_2005 documented review rows ready for recipe promotion. |
| alb2005_household_core_recipe_ready_rows | 0 | ALB_2005 household core rows ready for data promotion. |
| alb2005_provisional_outcome_ready_rows | 0 | ALB_2005 provisional outcome rows ready for final outcome promotion. |
| alb2005_outcome_semantics_outcome_ready_rows | 0 | ALB_2005 raw semantics rows ready for final outcome promotion. |
| alb2005_outcome_semantics_sdg382_ready_rows | 0 | ALB_2005 raw semantics rows ready for SDG 3.8.2 construction. |
| alb2005_outcome_semantics_climate_linkage_ready_rows | 0 | ALB_2005 raw semantics rows ready for climate linkage. |
| alb2005_climate_linkage_ready_rows | 0 | ALB_2005 timing/geography rows ready for climate linkage. |
| alb2005_timing_geography_source_search_rows | 11 | ALB_2005 timing/geography source-search audit rows. |
| alb2005_timing_geography_source_search_local_files_scanned | 46 | Local ALB_2005 file rows scanned for timing/geography source evidence. |
| alb2005_timing_geography_source_search_local_variables_scanned | 1187 | Local ALB_2005 raw-variable rows scanned for timing/geography source evidence. |
| alb2005_timing_geography_source_search_verified_household_timing_rows | 0 | Verified ALB_2005 household interview timing rows in source-search evidence. |
| alb2005_timing_geography_source_search_coordinate_candidate_rows | 0 | ALB_2005 coordinate/GPS candidate rows in source-search evidence. |
| alb2005_timing_geography_source_search_climate_linkage_ready_rows | 0 | ALB_2005 timing/geography source-search rows ready for climate linkage; should remain zero. |
| alb2005_harmonization_value_decision_recipe_ready_rows | 0 | ALB_2005 value-decision rows ready for recipe promotion. |
| alb2005_harmonization_value_decision_required_blocked_rows | 16 | ALB_2005 required value-decision rows still blocked. |
| alb2005_required_value_key_rows | 26 | ALB_2005 required value/key audit rows. |
| alb2005_required_value_key_recipe_ready_rows | 0 | ALB_2005 required value/key rows ready for recipe promotion. |
| alb2005_required_value_key_climate_linkage_ready_rows | 0 | ALB_2005 required value/key rows ready for climate linkage. |
| alb2005_health_questionnaire_semantics_rows | 58 | ALB_2005 health questionnaire semantics audit rows. |
| alb2005_health_questionnaire_oop_item_rows | 36 | ALB_2005 questionnaire-backed OOP item rows. |
| alb2005_health_questionnaire_recipe_ready_rows | 0 | ALB_2005 questionnaire-semantics rows ready for recipe promotion. |
| alb2005_health_questionnaire_outcome_ready_rows | 0 | ALB_2005 questionnaire-semantics rows ready for outcome construction. |
| alb2005_health_questionnaire_climate_linkage_ready_rows | 0 | ALB_2005 questionnaire-semantics rows ready for climate linkage. |
| alb2005_oop_aggregation_policy_rows | 11 | ALB_2005 OOP aggregation policy stress-test rows. |
| alb2005_oop_aggregation_policy_total_consumption_rows | 3638 | ALB_2005 stress-test rows with positive total-consumption denominator. |
| alb2005_oop_aggregation_policy_outcome_ready_rows | 0 | ALB_2005 OOP policy rows ready for final outcome promotion. |
| alb2005_oop_aggregation_policy_recipe_ready_rows | 0 | ALB_2005 OOP policy rows ready for recipe promotion. |
| alb2005_oop_aggregation_policy_climate_linkage_ready_rows | 0 | ALB_2005 OOP policy rows ready for climate linkage. |
| alb2005_skip_missing_semantics_rows | 13 | ALB_2005 skip/missing semantics audit rows. |
| alb2005_skip_missing_payment_nonmissing_when_not_triggered_rows | 0 | Payment downstream nonmissing rows when trigger is negative. |
| alb2005_skip_missing_payment_zero_or_missing_when_triggered_rows | 326 | Triggered payment rows with no positive payment. |
| alb2005_skip_missing_recipe_ready_rows | 0 | ALB_2005 skip/missing rows ready for recipe promotion. |
| alb2005_skip_missing_outcome_ready_rows | 0 | ALB_2005 skip/missing rows ready for outcome promotion. |
| alb2005_skip_missing_climate_linkage_ready_rows | 0 | ALB_2005 skip/missing rows ready for climate linkage. |
| alb2005_consumption_aggregate_crosswalk_rows | 16 | ALB_2005 aggregate metadata/local raw crosswalk audit rows. |
| alb2005_consumption_aggregate_crosswalk_metadata_present_local_rows | 1 | Public metadata aggregate/component variables present locally. |
| alb2005_consumption_aggregate_crosswalk_metadata_absent_local_rows | 8 | Public metadata aggregate/component variables absent locally. |
| alb2005_consumption_aggregate_crosswalk_totcons_positive_rows | 3638 | Positive local totcons rows in the crosswalk audit. |
| alb2005_consumption_aggregate_crosswalk_totcons05_local_rows | 0 | Local totcons05 rows in poverty.sav; should remain zero in current extract. |
| alb2005_consumption_aggregate_crosswalk_component_formula_reconstructable_rows | 0 | Whether checked public aggregate formula components are locally reconstructable; should remain zero. |
| alb2005_consumption_aggregate_crosswalk_sdg382_ready_rows | 0 | ALB_2005 aggregate crosswalk rows ready for SDG 3.8.2 construction; should remain zero. |
| alb2005_consumption_aggregate_crosswalk_recipe_ready_rows | 0 | ALB_2005 aggregate crosswalk rows ready for recipe promotion; should remain zero. |
| alb2005_consumption_aggregate_crosswalk_outcome_ready_rows | 0 | ALB_2005 aggregate crosswalk rows ready for outcome promotion; should remain zero. |
| alb2005_consumption_aggregate_crosswalk_climate_linkage_ready_rows | 0 | ALB_2005 aggregate crosswalk rows ready for climate linkage; should remain zero. |
| alb2005_consumption_component_source_search_rows | 37 | ALB_2005 consumption component source-search audit rows. |
| alb2005_consumption_component_source_search_exact_target_variables_found | 1 | Public metadata target variables found exactly in local raw schema. |
| alb2005_consumption_component_source_search_exact_target_variables_missing | 8 | Public metadata target variables missing from local raw schema. |
| alb2005_consumption_component_source_search_construction_code_files_found | 0 | Local source-code-like files found under the ALB_2005 extract. |
| alb2005_consumption_component_source_search_construction_code_targets_found | 0 | Target variables with local construction-code text hits. |
| alb2005_consumption_component_source_search_sdg382_ready_rows | 0 | ALB_2005 source-search rows ready for SDG 3.8.2 construction; should remain zero. |
| alb2005_consumption_component_source_search_recipe_ready_rows | 0 | ALB_2005 source-search rows ready for recipe promotion; should remain zero. |
| alb2005_consumption_component_source_search_outcome_ready_rows | 0 | ALB_2005 source-search rows ready for outcome promotion; should remain zero. |
| alb2005_consumption_component_source_search_climate_linkage_ready_rows | 0 | ALB_2005 source-search rows ready for climate linkage; should remain zero. |
| alb2005_minimum_recipe_promotion_action_rows | 6 | ALB_2005 minimum recipe promotion action rows. |
| alb2005_minimum_recipe_promotion_gate_rows | 10 | ALB_2005 minimum recipe promotion gate rows. |
| alb2005_minimum_recipe_promotion_blocked_gates | 8 | ALB_2005 minimum recipe gates still blocked. |
| alb2005_minimum_recipe_promotion_harmonized_ready_rows | 0 | ALB_2005 rows ready for harmonized data promotion; should remain zero. |
| alb2005_minimum_recipe_promotion_climate_linkage_ready_rows | 0 | ALB_2005 rows ready for climate linkage after minimum recipe gates; should remain zero. |
| alb2005_public_fieldwork_geo_metadata_evidence_rows | 10 | ALB_2005 public fieldwork/geography metadata evidence rows. |
| alb2005_public_fieldwork_geo_metadata_verified_source_rows | 10 | ALB_2005 public fieldwork/geography metadata rows with source snippets verified. |
| alb2005_public_fieldwork_geo_metadata_source_missing_rows | 0 | ALB_2005 public fieldwork/geography metadata rows with missing source evidence; should remain zero. |
| alb2005_public_fieldwork_geo_metadata_household_timing_verified_rows | 0 | ALB_2005 household timing rows verified after public metadata audit; should remain zero. |
| alb2005_public_fieldwork_geo_metadata_raw_coordinate_value_rows | 0 | ALB_2005 raw coordinate rows verified after public metadata audit; should remain zero. |
| alb2005_public_fieldwork_geo_metadata_climate_linkage_ready_rows | 0 | ALB_2005 climate-linkage rows ready after public metadata audit; should remain zero. |
| alb2005_diary_timing_candidate_audit_rows | 11 | ALB_2005 bookmetadata diary timing candidate rows. |
| alb2005_diary_timing_candidate_metadata_found_rows | 11 | ALB_2005 diary timing candidates found in metadata catalog and DDI. |
| alb2005_diary_timing_candidate_raw_bookmetadata_files_present | 0 | Raw bookmetadata files present under temp/raw_downloads; should remain zero in current metadata-only state. |
| alb2005_diary_timing_candidate_date_candidate_rows | 6 | Diary beginning/finishing date candidate variables with nonzero DDI valid counts. |
| alb2005_diary_timing_candidate_household_timing_promoted_rows | 0 | ALB_2005 household timing rows promoted after diary candidate audit; should remain zero. |
| alb2005_diary_timing_candidate_climate_linkage_ready_rows | 0 | ALB_2005 climate-linkage rows ready after diary candidate audit; should remain zero. |
| alb2005_extracted_module_coverage_ddi_module_rows | 68 | ALB_2005 DDI/schema modules checked against extracted files. |
| alb2005_archive_member_rows | 61 | Members listed directly from the local ALB_2005 archive. |
| alb2005_archive_sav_member_rows | 44 | SPSS .sav members listed directly from the local ALB_2005 archive. |
| alb2005_archive_ddi_module_absent_rows | 27 | ALB_2005 DDI/schema modules absent from the local archive manifest. |
| alb2005_archive_critical_module_absent_rows | 8 | Critical ALB_2005 timing, food-diary, and design DDI modules absent from the local archive manifest. |
| alb2005_archive_listing_status | tar_listing_available | Whether the local ALB_2005 archive member list was readable. |
| alb2005_extracted_module_coverage_present_rows | 41 | ALB_2005 DDI modules present in extracted files. |
| alb2005_extracted_module_coverage_missing_rows | 27 | ALB_2005 DDI modules missing from extracted files. |
| alb2005_extracted_module_coverage_bookmetadata_missing_rows | 1 | ALB_2005 bookmetadata_cl missing rows. |
| alb2005_extracted_module_coverage_critical_missing_rows | 8 | ALB_2005 critical missing timing/food-diary/design modules. |
| alb2005_extracted_module_coverage_coordinate_metadata_variable_rows | 0 | ALB_2005 coordinate/GPS metadata variable rows. |
| alb2005_extracted_module_coverage_coordinate_extracted_file_rows | 0 | ALB_2005 coordinate/GPS extracted file rows. |
| alb2005_extracted_module_coverage_climate_linkage_ready_rows | 0 | ALB_2005 climate-linkage rows ready after extracted-module audit; should remain zero. |
| albania_first_analysis_promotion_wave_rows | 4 | Local Albania raw waves compared for first analysis promotion. |
| albania_first_analysis_promotion_gate_rows | 40 | First-analysis promotion gate rows. |
| albania_first_analysis_promotion_blocked_gate_rows | 19 | First-analysis promotion gates still blocked. |
| albania_first_analysis_promotion_ready_wave_rows | 0 | Albania waves ready for first analytical-sample promotion; should remain zero. |
| albania_first_analysis_promotion_top_ranked_idno | ALB_2002_LSMS_v01_M | Top-ranked local Albania wave for next manual evidence work. |
| albania_first_analysis_promotion_current_decision | blocked_no_albania_wave_ready_for_first_analysis_promotion | Current first-analysis promotion decision. |
| albania_existing_raw_wave_harmonization_ready_rows | 0 | Existing Albania raw waves ready for harmonized data promotion. |
| albania_existing_raw_wave_climate_linkage_ready_rows | 0 | Existing Albania raw waves ready for climate-linkage input promotion. |
| alb2008_household_core_recipe_ready_rows | 0 | ALB_2008 household core rows ready for data promotion. |
| alb2008_provisional_outcome_ready_rows | 0 | ALB_2008 provisional outcome rows ready for final outcome promotion. |
| alb2008_outcome_semantics_outcome_ready_rows | 0 | ALB_2008 raw semantics rows ready for final outcome promotion. |
| alb2008_outcome_semantics_sdg382_ready_rows | 0 | ALB_2008 raw semantics rows ready for SDG 3.8.2 construction. |
| alb2008_outcome_semantics_climate_linkage_ready_rows | 0 | ALB_2008 raw semantics rows ready for climate linkage. |
| alb2008_climate_linkage_ready_rows | 0 | ALB_2008 timing/geography rows ready for climate linkage. |
| bundle_section_artifact_manifest | 1 | Direct-read bundle section count. |
| bundle_section_climate_outcome_gate | 50 | Direct-read bundle section count. |
| bundle_section_coverage | 5 | Direct-read bundle section count. |
| bundle_section_design_gate | 4 | Direct-read bundle section count. |
| bundle_section_go_no_go | 1 | Direct-read bundle section count. |
| bundle_section_go_no_go_rule | 8 | Direct-read bundle section count. |
| bundle_section_priority_bundle | 15 | Direct-read bundle section count. |
| bundle_section_raw_access_gate | 5 | Direct-read bundle section count. |
| bundle_section_raw_acquisition_gate | 1 | Direct-read bundle section count. |
| bundle_section_raw_verification_gate | 22 | Direct-read bundle section count. |
| bundle_section_readiness | 6 | Direct-read bundle section count. |
| bundle_section_state | 3 | Direct-read bundle section count. |
| bundle_section_traceability | 3 | Direct-read bundle section count. |
| bundle_status_available | 2 | Direct-read bundle status count. |
| bundle_status_blocked_alb2002_access_candidate_not_promoted_due_denominator_skip_climate_gates | 1 | Direct-read bundle status count. |
| bundle_status_blocked_alb2002_access_need_denominator_policy_not_outcome_ready | 1 | Direct-read bundle status count. |
| bundle_status_blocked_alb2002_analysis_candidate_not_promoted_due_recipe_outcome_climate_gates | 1 | Direct-read bundle status count. |
| bundle_status_blocked_alb2002_boundary_resource_search_no_historical_climate_ready_source | 1 | Direct-read bundle status count. |
| bundle_status_blocked_alb2002_che_candidate_not_promoted_due_recipe_sdg_climate_gates | 1 | Direct-read bundle status count. |
| bundle_status_blocked_alb2002_climate_centroid_exposures_not_promoted_due_boundary_vintage_source_and_baseline_gates | 1 | Direct-read bundle status count. |
| bundle_status_blocked_alb2002_climate_outcome_linked_candidate_not_promoted_due_recipe_outcome_geography_source_baseline_gates | 1 | Direct-read bundle status count. |
| bundle_status_blocked_alb2002_climate_shock_candidate_not_promoted_due_geography_baseline_primary_source_gates | 1 | Direct-read bundle status count. |
| bundle_status_blocked_alb2002_consumption_sdg_denominator_policy_not_sdg_ready | 1 | Direct-read bundle status count. |
| bundle_status_blocked_alb2002_linked_candidate_descriptive_screen_not_promoted_due_unpromoted_inputs | 1 | Direct-read bundle status count. |
| bundle_status_blocked_alb2002_minimum_recipe_not_ready_for_promotion | 1 | Direct-read bundle status count. |
| bundle_status_blocked_alb2002_oop_aggregation_policy_stress_test_not_outcome_ready | 1 | Direct-read bundle status count. |
| bundle_status_blocked_alb2002_period_aligned_che_policy_not_outcome_ready | 1 | Direct-read bundle status count. |
| bundle_status_blocked_alb2002_questionnaire_semantics_seen_but_outcome_not_ready | 1 | Direct-read bundle status count. |
| bundle_status_blocked_alb2002_skip_missing_semantics_seen_but_recipe_not_ready | 1 | Direct-read bundle status count. |
| bundle_status_blocked_alb2002_uhc_composite_candidate_not_promoted_due_outcome_recipe_climate_gates | 1 | Direct-read bundle status count. |
| bundle_status_blocked_alb2002_weight_design_semantics_not_promotion_ready | 1 | Direct-read bundle status count. |
| bundle_status_blocked_alb2005_consumption_aggregate_metadata_crosswalk_not_ready | 1 | Direct-read bundle status count. |
| bundle_status_blocked_alb2005_consumption_component_source_search_not_ready | 1 | Direct-read bundle status count. |
| bundle_status_blocked_alb2005_consumption_oop_unit_period_not_ready | 1 | Direct-read bundle status count. |
| bundle_status_blocked_alb2005_minimum_recipe_not_ready_for_promotion | 1 | Direct-read bundle status count. |
| bundle_status_blocked_alb2005_no_fallback_ready | 1 | Direct-read bundle status count. |
| bundle_status_blocked_alb2005_oop_aggregation_policy_stress_test_not_outcome_ready | 1 | Direct-read bundle status count. |
| bundle_status_blocked_alb2005_questionnaire_semantics_seen_but_recipe_not_ready | 1 | Direct-read bundle status count. |
| bundle_status_blocked_alb2005_required_values_seen_but_recipe_not_ready | 1 | Direct-read bundle status count. |
| bundle_status_blocked_alb2005_skip_missing_semantics_seen_but_recipe_not_ready | 1 | Direct-read bundle status count. |
| bundle_status_blocked_alb2005_timing_geography_source_search_not_ready | 1 | Direct-read bundle status count. |
| bundle_status_blocked_alb2008_no_timing_geography_fallback_ready | 1 | Direct-read bundle status count. |
| bundle_status_blocked_alb2012_no_timing_geography_fallback_ready | 1 | Direct-read bundle status count. |
| bundle_status_blocked_boundary_crosswalk_not_verified_no_gps | 1 | Direct-read bundle status count. |
| bundle_status_blocked_current_boundary_name_match_incomplete_historical_crosswalk_no_gps | 1 | Direct-read bundle status count. |
| bundle_status_blocked_diary_timing_metadata_candidate_no_raw_merge_semantics | 1 | Direct-read bundle status count. |
| bundle_status_blocked_extracted_package_missing_bookmetadata_and_coordinate_values | 1 | Direct-read bundle status count. |
| bundle_status_blocked_followup_confirms_no_public_2002_district_boundary_source | 1 | Direct-read bundle status count. |
| bundle_status_blocked_gadm_boundary_lead_no_verified_2002_historical_provenance | 1 | Direct-read bundle status count. |
| bundle_status_blocked_geoboundaries_2_0_1_boundary_year_2013_not_verified_2002 | 1 | Direct-read bundle status count. |
| bundle_status_blocked_legacy_questionnaire_form_design_not_sufficient_for_climate_linkage | 1 | Direct-read bundle status count. |
| bundle_status_blocked_manual_boundary_verification_required_before_alb2002_climate_linkage | 1 | Direct-read bundle status count. |
| bundle_status_blocked_missing_interview_timing_coarse_geography_no_gps | 1 | Direct-read bundle status count. |
| bundle_status_blocked_missing_interview_timing_coarse_prefecture_region_no_gps | 1 | Direct-read bundle status count. |
| bundle_status_blocked_missing_interview_timing_partial_geography_no_gps | 1 | Direct-read bundle status count. |
| bundle_status_blocked_no_alb2002_boundary_source_ready_for_climate_linkage | 1 | Direct-read bundle status count. |
| bundle_status_blocked_no_alb2002_outcome_ready_for_promotion | 1 | Direct-read bundle status count. |
| bundle_status_blocked_no_albania_wave_ready_for_first_analysis_promotion | 1 | Direct-read bundle status count. |
| bundle_status_blocked_no_public_2002_district_boundary_source_verified | 1 | Direct-read bundle status count. |
| bundle_status_blocked_no_raw_or_archive_file | 1 | Direct-read bundle status count. |
| bundle_status_blocked_outcome_semantics_units_recall_skip_patterns_unreviewed | 1 | Direct-read bundle status count. |
| bundle_status_blocked_public_metadata_not_household_climate_linkage_ready | 1 | Direct-read bundle status count. |
| bundle_status_blocked_questionnaire_gps_fields_not_present_as_raw_coordinate_artifacts | 1 | Direct-read bundle status count. |
| bundle_status_blocked_questionnaire_timing_fields_not_in_raw_household_values | 1 | Direct-read bundle status count. |
| bundle_status_blocked_raw_files_absent | 1 | Direct-read bundle status count. |
| bundle_status_blocked_raw_microdata | 14 | Direct-read bundle status count. |
| bundle_status_blocked_raw_timing_geography_not_verified | 1 | Direct-read bundle status count. |
| bundle_status_blocked_timing_geography_outcome_semantics_units_recall_skip_patterns | 3 | Direct-read bundle status count. |
| bundle_status_closed_no_promoted_rows | 1 | Direct-read bundle status count. |
| bundle_status_complete | 4 | Direct-read bundle status count. |
| bundle_status_documented_alb2002_consumption_aggregate_but_not_outcome_sdg_climate_ready | 2 | Direct-read bundle status count. |
| bundle_status_documented_alb2002_oop_skipped_values_zero_only_but_oop_policy_not_ready | 1 | Direct-read bundle status count. |
| bundle_status_fail_closed_design_scorecard_currently_no_go_for_estimation_or_policy_learning | 1 | Direct-read bundle status count. |
| bundle_status_harmonization_value_audit_required | 1 | Direct-read bundle status count. |
| bundle_status_incomplete | 1 | Direct-read bundle status count. |
| bundle_status_legacy_questionnaires_readable_content_audit_required | 1 | Direct-read bundle status count. |
| bundle_status_limited_che10_che25_financial_outcomes_promoted_sdg_access_climate_still_blocked | 1 | Direct-read bundle status count. |
| bundle_status_limited_che_outcome_nasa_admin2_climate_linked_promoted_models_still_blocked | 1 | Direct-read bundle status count. |
| bundle_status_limited_core_financial_outcomes_climate_exposures_and_linked_diagnostics_promoted_models_still_blocked | 1 | Direct-read bundle status count. |
| bundle_status_limited_harmonized_household_core_promoted_outcome_climate_still_blocked | 1 | Direct-read bundle status count. |
| bundle_status_limited_nasa_admin2_centroid_climate_exposures_promoted_linkage_still_blocked | 1 | Direct-read bundle status count. |
| bundle_status_manual_download_required | 1 | Direct-read bundle status count. |
| bundle_status_manual_raw_download_required | 10 | Direct-read bundle status count. |
| bundle_status_manual_raw_package_required | 1 | Direct-read bundle status count. |
| bundle_status_manual_review_required | 1 | Direct-read bundle status count. |
| bundle_status_metadata_only_requires_raw_verification | 4 | Direct-read bundle status count. |
| bundle_status_not_available | 1 | Direct-read bundle status count. |
| bundle_status_not_final_outcomes_outcome_semantics_climate_crosswalk_blocked | 1 | Direct-read bundle status count. |
| bundle_status_not_final_outcomes_timing_geography_recall_blocked | 2 | Direct-read bundle status count. |
| bundle_status_not_final_outcomes_timing_geography_recall_semantics_blocked | 1 | Direct-read bundle status count. |
| bundle_status_not_ready_for_verified_recipe | 1 | Direct-read bundle status count. |
| bundle_status_partial_gate_delta_documented_keep_data_empty_until_outcome_sdg_geography_gates_pass | 1 | Direct-read bundle status count. |
| bundle_status_pass | 2 | Direct-read bundle status count. |
| bundle_status_present_raw_waves_require_wave_specific_schema_value_key_timing_audits | 1 | Direct-read bundle status count. |
| bundle_status_raw_archives_available_requires_value_verification | 1 | Direct-read bundle status count. |
| bundle_status_raw_schema_claims_only_no_analysis_dataset_claims | 1 | Direct-read bundle status count. |
| bundle_status_raw_schema_inspected_harmonization_pending | 1 | Direct-read bundle status count. |
| bundle_status_raw_value_summary_available_manual_review_required | 1 | Direct-read bundle status count. |
| bundle_status_ready | 1 | Direct-read bundle status count. |
| bundle_status_temp_candidate_no_interview_timing_coarse_geography_outcome_semantics_pending | 1 | Direct-read bundle status count. |
| bundle_status_temp_candidate_not_analysis_ready | 2 | Direct-read bundle status count. |
| bundle_status_temp_candidate_timing_geography_observed_outcome_semantics_pending | 1 | Direct-read bundle status count. |

## Bundle Sections

| Section | Count |
|---|---:|
| climate_outcome_gate | 50 |
| raw_verification_gate | 22 |
| priority_bundle | 15 |
| go_no_go_rule | 8 |
| readiness | 6 |
| coverage | 5 |
| raw_access_gate | 5 |
| design_gate | 4 |
| state | 3 |
| traceability | 3 |
| raw_acquisition_gate | 1 |
| go_no_go | 1 |
| artifact_manifest | 1 |

## Bundle Status

| Status | Count |
|---|---:|
| blocked_raw_microdata | 14 |
| manual_raw_download_required | 10 |
| complete | 4 |
| metadata_only_requires_raw_verification | 4 |
| blocked_timing_geography_outcome_semantics_units_recall_skip_patterns | 3 |
| documented_alb2002_consumption_aggregate_but_not_outcome_sdg_climate_ready | 2 |
| temp_candidate_not_analysis_ready | 2 |
| not_final_outcomes_timing_geography_recall_blocked | 2 |
| pass | 2 |
| available | 2 |
| raw_schema_claims_only_no_analysis_dataset_claims | 1 |
| raw_schema_inspected_harmonization_pending | 1 |
| not_available | 1 |
| manual_download_required | 1 |
| manual_review_required | 1 |
| manual_raw_package_required | 1 |
| blocked_no_raw_or_archive_file | 1 |
| blocked_raw_timing_geography_not_verified | 1 |
| blocked_raw_files_absent | 1 |
| closed_no_promoted_rows | 1 |
| raw_archives_available_requires_value_verification | 1 |
| raw_value_summary_available_manual_review_required | 1 |
| temp_candidate_timing_geography_observed_outcome_semantics_pending | 1 |
| blocked_alb2002_weight_design_semantics_not_promotion_ready | 1 |
| blocked_alb2002_che_candidate_not_promoted_due_recipe_sdg_climate_gates | 1 |
| blocked_alb2002_access_candidate_not_promoted_due_denominator_skip_climate_gates | 1 |
| blocked_alb2002_uhc_composite_candidate_not_promoted_due_outcome_recipe_climate_gates | 1 |
| blocked_alb2002_analysis_candidate_not_promoted_due_recipe_outcome_climate_gates | 1 |
| blocked_alb2002_climate_centroid_exposures_not_promoted_due_boundary_vintage_source_and_baseline_gates | 1 |
| blocked_alb2002_climate_shock_candidate_not_promoted_due_geography_baseline_primary_source_gates | 1 |
| blocked_alb2002_climate_outcome_linked_candidate_not_promoted_due_recipe_outcome_geography_source_baseline_gates | 1 |
| blocked_alb2002_linked_candidate_descriptive_screen_not_promoted_due_unpromoted_inputs | 1 |
| not_final_outcomes_outcome_semantics_climate_crosswalk_blocked | 1 |
| blocked_outcome_semantics_units_recall_skip_patterns_unreviewed | 1 |
| blocked_alb2002_questionnaire_semantics_seen_but_outcome_not_ready | 1 |
| blocked_alb2002_oop_aggregation_policy_stress_test_not_outcome_ready | 1 |
| blocked_alb2002_skip_missing_semantics_seen_but_recipe_not_ready | 1 |
| documented_alb2002_oop_skipped_values_zero_only_but_oop_policy_not_ready | 1 |
| blocked_alb2002_access_need_denominator_policy_not_outcome_ready | 1 |
| blocked_alb2002_consumption_sdg_denominator_policy_not_sdg_ready | 1 |
| blocked_alb2002_period_aligned_che_policy_not_outcome_ready | 1 |
| blocked_alb2002_minimum_recipe_not_ready_for_promotion | 1 |
| limited_harmonized_household_core_promoted_outcome_climate_still_blocked | 1 |
| limited_che10_che25_financial_outcomes_promoted_sdg_access_climate_still_blocked | 1 |
| limited_nasa_admin2_centroid_climate_exposures_promoted_linkage_still_blocked | 1 |
| limited_che_outcome_nasa_admin2_climate_linked_promoted_models_still_blocked | 1 |
| limited_core_financial_outcomes_climate_exposures_and_linked_diagnostics_promoted_models_still_blocked | 1 |
| fail_closed_design_scorecard_currently_no_go_for_estimation_or_policy_learning | 1 |
| partial_gate_delta_documented_keep_data_empty_until_outcome_sdg_geography_gates_pass | 1 |
| blocked_no_alb2002_boundary_source_ready_for_climate_linkage | 1 |
| blocked_no_alb2002_outcome_ready_for_promotion | 1 |
| blocked_boundary_crosswalk_not_verified_no_gps | 1 |
| blocked_current_boundary_name_match_incomplete_historical_crosswalk_no_gps | 1 |
| blocked_no_public_2002_district_boundary_source_verified | 1 |
| blocked_alb2002_boundary_resource_search_no_historical_climate_ready_source | 1 |
| blocked_geoboundaries_2_0_1_boundary_year_2013_not_verified_2002 | 1 |
| blocked_manual_boundary_verification_required_before_alb2002_climate_linkage | 1 |
| blocked_followup_confirms_no_public_2002_district_boundary_source | 1 |
| blocked_gadm_boundary_lead_no_verified_2002_historical_provenance | 1 |
| blocked_questionnaire_gps_fields_not_present_as_raw_coordinate_artifacts | 1 |
| temp_candidate_no_interview_timing_coarse_geography_outcome_semantics_pending | 1 |
| not_final_outcomes_timing_geography_recall_semantics_blocked | 1 |
| blocked_missing_interview_timing_coarse_prefecture_region_no_gps | 1 |
| blocked_questionnaire_timing_fields_not_in_raw_household_values | 1 |
| blocked_alb2012_no_timing_geography_fallback_ready | 1 |
| legacy_questionnaires_readable_content_audit_required | 1 |
| blocked_legacy_questionnaire_form_design_not_sufficient_for_climate_linkage | 1 |
| not_ready_for_verified_recipe | 1 |
| blocked_missing_interview_timing_partial_geography_no_gps | 1 |
| blocked_alb2005_timing_geography_source_search_not_ready | 1 |
| blocked_alb2005_required_values_seen_but_recipe_not_ready | 1 |
| blocked_alb2005_questionnaire_semantics_seen_but_recipe_not_ready | 1 |
| blocked_alb2005_oop_aggregation_policy_stress_test_not_outcome_ready | 1 |
| blocked_alb2005_skip_missing_semantics_seen_but_recipe_not_ready | 1 |
| blocked_alb2005_consumption_oop_unit_period_not_ready | 1 |
| blocked_alb2005_consumption_aggregate_metadata_crosswalk_not_ready | 1 |
| blocked_alb2005_consumption_component_source_search_not_ready | 1 |
| blocked_alb2005_minimum_recipe_not_ready_for_promotion | 1 |
| blocked_public_metadata_not_household_climate_linkage_ready | 1 |
| blocked_diary_timing_metadata_candidate_no_raw_merge_semantics | 1 |
| blocked_extracted_package_missing_bookmetadata_and_coordinate_values | 1 |
| blocked_alb2005_no_fallback_ready | 1 |
| blocked_no_albania_wave_ready_for_first_analysis_promotion | 1 |
| present_raw_waves_require_wave_specific_schema_value_key_timing_audits | 1 |
| blocked_missing_interview_timing_coarse_geography_no_gps | 1 |
| blocked_alb2008_no_timing_geography_fallback_ready | 1 |
| ready | 1 |
| incomplete | 1 |
| harmonization_value_audit_required | 1 |

## Completion Gaps

No incomplete completion criteria were found.

## Go/No-Go Rules

| item | status | value | interpretation |
|---|---|---|---|
| main_financial_protection_minimum_countries | blocked_raw_microdata | 0 | If fewer than 6 countries have consumption, OOP health expenditure, usable geography, and survey timing, do not proce... |
| double_failure_minimum_country_waves | blocked_raw_microdata | 1 | If fewer than 10 country-waves support both financial hardship and forgone care, keep UHC double failure secondary. N... |
| climate_geography_precision | blocked_raw_microdata | 0 | If geolocation is too weak for most countries, use admin-level climate aggregation and lower causal claims. Next acti... |
| event_rate_minimum | blocked_raw_microdata | 3599 | If event rates are below 3%, expand outcomes or countries; do not force rare-event ML. Next action: run promoted desc... |
| transportable_prediction | pass | 30 | If leave-country-out predictive performance is poor, do not claim transportable targeting. Next action: run predictiv... |
| climate_lead_placebo | pass | 88 | If climate lead placebo predicts outcomes, treat causal design as weak. Next action: estimate main reduced-form model... |
| causal_ml_policy_value | blocked_raw_microdata | 0 | If CATE/policy learning does not beat simple targeting rules out of sample, report null targeting value honestly. Nex... |
| descriptive_fallback | blocked_raw_microdata | 3599 | If only descriptive evidence survives, write a descriptive data paper and do not claim causal effects. Next action: r... |

## Priority Raw-Data Bundles

| item | status | value | interpretation |
|---|---|---|---|
| priority_raw_intake_gate | manual_raw_package_required | gate_rows=13; priority_10_rows=10; backup_rows=3; file_targets=156; manual_blocked=13; schema_ready=0; handoffs=13 | Priority 10-wave and backup raw-intake gate converts the acquisition plan into per-folder handoff files and fail-clos... |
| priority_archive_member_preflight | blocked_no_raw_or_archive_file | datasets=13; targets=156; archives=0; members=0; direct_covered=0; archive_covered=0; missing=156 | Archive/direct-file preflight checks whether placed raw archives or tabular files cover priority modules before any r... |
| priority_climate_linkage_preflight | blocked_raw_timing_geography_not_verified | preflight_rows=13; priority_10_rows=10; backup_rows=3; requirements=143; source_ready=13; accepted_routes=0; handoffs=13 | Priority climate preflight keeps CHIRPS/ERA5 linkage fail-closed until raw timing/geography, geolocation quality, uni... |
| priority_raw_verification_workbook | blocked_raw_files_absent | dataset_gates=13; requirements=104; concepts=169; variables=1214; dataset_ready=0; requirements_ready=0; handoffs=13 | Priority raw verification workbook converts the objective's required checks into fillable dataset, requirement, conce... |
| promoted_data_gate | closed_no_promoted_rows | promoted_rows=0; data_before=4; data_after=0; quarantined=4 | Promoted data gate keeps data/ reserved for registry-approved datasets and moves pre-promotion diagnostic CSVs to tem... |
| 1: Albania 2005 ALB_2005_LSMS_v01_M | harmonization_value_audit_required | raw_schema_claims_only_no_analysis_dataset_claims | complete harmonization value/unit/recall/key audits and assemble verified recipe candidates |
| 2: Ethiopia 2021-2022 ETH_2021_ESPS-W5_v02_M | manual_raw_download_required | metadata_protocol_only_no_empirical_claims | place original raw archives/files in the target folder, then run raw-download and schema inspection |
| 3: Ethiopia 2018-2019 ETH_2018_ESS_v04_M | manual_raw_download_required | metadata_protocol_only_no_empirical_claims | place original raw archives/files in the target folder, then run raw-download and schema inspection |
| 4: Jamaica 1997 JAM_1997_SLC_v01_M | manual_raw_download_required | metadata_protocol_only_no_empirical_claims | place original raw archives/files in the target folder, then run raw-download and schema inspection |
| 5: Kyrgyz Republic 1993 KGZ_1993_KMPS_v01_M | manual_raw_download_required | metadata_protocol_only_no_empirical_claims | place original raw archives/files in the target folder, then run raw-download and schema inspection |

## Artifact Manifest

| Artifact status | Count |
|---|---:|
| present_nonempty | 488 |
| missing_or_empty | 4 |

Missing or empty curated artifacts:

| artifact_group | relative_path | current_status | role |
|---|---|---|---|
| climate_outcome | data/harmonized_household.csv | missing_or_empty | ALB_2002 limited harmonized household core |
| climate_outcome | data/household_outcomes.csv | missing_or_empty | ALB_2002 limited CHE-only household outcome file |
| climate_outcome | data/climate_exposures_nasa_power.csv | missing_or_empty | ALB_2002 limited NASA POWER admin2-centroid exposure file |
| climate_outcome | data/climate_linked_household.csv | missing_or_empty | ALB_2002 limited CHE and NASA POWER climate-linked household-window file |

## Reproduction Notes

The deterministic downstream audit layer can be refreshed with:

```bash
python script/54_audit_alb2002_household_core_merge.py
python script/55_audit_alb2002_provisional_outcome_feasibility.py
python script/60_audit_alb2002_outcome_semantics_raw_values.py
python script/89_audit_alb2002_health_questionnaire_semantics.py
python script/91_audit_alb2002_oop_aggregation_policy.py
python script/92_audit_alb2002_skip_missing_semantics.py
python script/97_audit_alb2002_oop_skip_value_decision.py
python script/93_audit_alb2002_access_need_denominator_policy.py
python script/105_build_alb2002_access_candidate_outcomes.py
python script/94_audit_alb2002_consumption_sdg_denominator_policy.py
python script/96_audit_alb2002_consumption_construction_sources.py
python script/95_audit_alb2002_consumption_aggregate_metadata_crosswalk.py
python script/99_audit_alb2002_period_aligned_che_policy.py
python script/100_audit_alb2002_weight_design_evidence.py
python script/56_audit_alb2002_district_climate_crosswalk.py
python script/64_audit_alb2002_boundary_name_match.py
python script/79_audit_alb2002_boundary_source_resource_search.py
python script/80_audit_alb2002_boundary_geometry_provenance.py
python script/69_audit_alb2002_boundary_source_alternatives.py
python script/70_audit_alb2002_local_geography_artifacts.py
python script/82_audit_alb2002_boundary_manual_source_followup.py
python script/88_audit_alb2002_gadm_boundary_lead.py
python script/81_build_alb2002_boundary_manual_verification_packet.py
python script/90_build_alb2002_minimum_recipe_promotion_packet.py
python script/101_build_alb2002_che_candidate_outcomes.py
python script/106_build_alb2002_uhc_composite_candidate_outcomes.py
python script/102_build_alb2002_analysis_candidate_dataset.py
python script/117_promote_alb2002_harmonized_household_core.py
python script/05_construct_outcomes.py
python script/119_promote_alb2002_limited_financial_outcomes.py
python script/103_build_alb2002_climate_centroid_exposure_candidates.py
python script/107_build_alb2002_climate_shock_candidate_audit.py
python script/118_promote_alb2002_limited_climate_exposures.py
python script/07_merge_microdata_climate.py
python script/120_promote_alb2002_limited_climate_linked.py
python script/108_build_alb2002_climate_outcome_linked_candidate_audit.py
python script/109_build_alb2002_linked_candidate_descriptive_diagnostics.py
python script/90_build_alb2002_minimum_recipe_promotion_packet.py
python script/98_audit_analysis_dataset_promotion_barriers.py
python script/110_build_current_design_scorecard.py
python script/111_audit_alb2002_promotion_gate_delta.py
python script/112_build_alb2002_boundary_blocker_resolution_matrix.py
python script/113_build_alb2002_outcome_blocker_resolution_matrix.py
python script/57_audit_alb2012_raw_core_feasibility.py
python script/58_audit_alb2012_provisional_outcome_feasibility.py
python script/63_audit_alb2012_outcome_semantics_raw_values.py
python script/59_audit_alb2012_timing_geography_exhaustive.py
python script/65_audit_alb2012_questionnaire_timing_fields.py
python script/114_build_alb2012_timing_geography_blocker_resolution_matrix.py
python script/66_audit_albania_legacy_questionnaire_readability.py
python script/67_audit_albania_legacy_questionnaire_timing_fields.py
python script/48_audit_alb2005_provisional_outcome_feasibility.py
python script/61_audit_alb2005_outcome_semantics_raw_values.py
python script/49_audit_alb2005_timing_geography_exhaustive.py
python script/71_audit_alb2005_required_value_key_evidence.py
python script/72_audit_alb2005_health_questionnaire_semantics.py
python script/73_audit_alb2005_oop_aggregation_policy.py
python script/74_audit_alb2005_skip_missing_semantics.py
python script/75_audit_alb2005_consumption_oop_unit_period.py
python script/76_audit_alb2005_consumption_aggregate_metadata_crosswalk.py
python script/77_audit_alb2005_consumption_component_source_search.py
python script/78_audit_alb2005_timing_geography_source_search.py
python script/83_build_alb2005_minimum_recipe_promotion_packet.py
python script/84_audit_alb2005_public_fieldwork_geo_metadata.py
python script/85_audit_alb2005_diary_timing_candidates.py
python script/86_audit_alb2005_extracted_module_coverage.py
python script/87_build_albania_first_analysis_promotion_gate.py
python script/115_build_alb2005_fallback_blocker_resolution_matrix.py
python script/51_audit_alb2008_household_core_merge.py
python script/52_audit_alb2008_provisional_outcome_feasibility.py
python script/62_audit_alb2008_outcome_semantics_raw_values.py
python script/53_audit_alb2008_timing_geography_exhaustive.py
python script/116_build_alb2008_fallback_blocker_resolution_matrix.py
python script/50_audit_existing_albania_raw_waves.py
python script/33_build_harmonization_recipe_gate.py
python script/68_build_alb2005_harmonization_value_decision_audit.py
python script/35_build_empirical_readiness_dashboard.py
python script/36_build_direct_read_audit_bundle.py
python script/28_audit_python_environment.py
python script/26_build_objective_traceability_audit.py
python script/13_write_reports.py
python script/14_validate_workspace.py
```

The full `script/run_all.ps1`, `script/run_all.sh`, and `Makefile` runners include acquisition/probe stages and may take longer. Empirical estimation remains blocked until raw files are manually obtained and inspected.

## Machine-Readable Outputs

- `result/direct_read_audit_bundle.csv`
- `result/direct_read_artifact_manifest.csv`
- `result/direct_read_audit_bundle_summary.csv`
