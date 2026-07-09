# Current Design Scorecard Audit

Status: fail-closed design tournament refresh. This preserves the broad metadata scorecard and appends current-state design rows using the ALB_2002 temp-only outcome, climate, linkage, and descriptive-screen audits. It does not create analysis data, estimate models, or satisfy predictive, causal, robustness, or final descriptive criteria.

## Summary

| Metric | Value | Interpretation |
|---|---:|---|
| design_scorecard_rows | 38 | Total design scorecard rows after current fail-closed refresh. |
| design_scorecard_current_rows | 3 | Current-state design rows appended to the metadata scorecard. |
| design_scorecard_audit_rows | 4 | Audit rows for the current design scorecard refresh. |
| design_no_go_threshold_rows | 8 | Go/no-go threshold audit rows. |
| design_no_go_failed_or_not_estimable_rows | 8 | Threshold rows that are failed, candidate-only, or not estimable. |
| design_scorecard_data_write_ready_rows | 0 | Rows allowed for data/ write by this design scorecard; intentionally zero. |
| design_scorecard_current_decision | fail_closed_design_scorecard_currently_no_go_for_estimation_or_policy_learning | Current design scorecard decision. |

## Current-State Design Rows

| design_id | country_scope | outcome_validity | exposure_precision | sample_size | event_rate | climate_geography_linkage_quality | identifying_variation | pre-trend/placebo credibility | go/no-go | reason |
|---|---|---|---|---|---|---|---|---|---|---|
| current_alb2002_temp_linked_candidate_financial_access_climate | Albania ALB_2002 only | 3 | 1 | 3 | 4 | 1 | 1 | 0 | no-go for estimation; go for source/boundary/baseline/outcome-resolution work | Temp candidate is mechanically rich but not promoted: linked_rows=14396; households=3599; windows=4; combined_stress=3092; desc... |
| current_multi_country_financial_protection_main | multi-country | 1 | 0 | 2 | 0 | 0 | 0 | 0 | no-go for main multi-country paper under current evidence | Main go/no-go gates fail because promoted data_files=4, promoted_rows=4, failed_no_go_rules=3, and no value-verified six-countr... |
| current_alb2002_descriptive_resource_candidate | Albania ALB_2002 only | 2 | 1 | 3 | 4 | 1 | 0 | 0 | go for internal audit screen only; no-go for publishable descriptive estimates | Candidate screen has cell_rows=108, CHE10-or-access households=2004, CHE25-or-access households=1889, but descriptive_data_writ... |

## Go/No-Go Thresholds

| rule_id | rule | current_status | evidence | go_no_go | required_action |
|---|---|---|---|---|---|
| go_no_go_01_six_country_financial_sample | If fewer than 6 countries have consumption, OOP health expenditure, usable geography, and survey timing, do not proceed with th... | failed | promoted_data_files=4; promoted_rows=4; sample_gate_failed_rules=3 | no-go_main_multi_country_financial_protection | Promote at least six value-verified country household datasets with OOP, budget, timing, geography, and weights. |
| go_no_go_02_ten_double_failure_waves | If fewer than 10 country-waves support both financial hardship and forgone care, keep UHC double failure secondary. | failed | ALB_2002 has temp double-failure candidates only; linked_data_write_ready=0; outcome_ready=0 | no-go_double_failure_primary | Verify financial and access outcomes across at least ten country-waves before making double failure primary. |
| go_no_go_03_geolocation_precision | If geolocation is too weak for most countries, use admin aggregation and lower causal claims. | failed_for_causal_claims | ALB_2002 climate_ready=0; NASA centroid diagnostics exist but historical boundaries and GPS/EA maps are not accepted. | no-go_point_or_strong_causal_claims | Verify historical boundaries, GPS/EA maps, or accepted crosswalks; then build CHIRPS/ERA5 historical anomalies. |
| go_no_go_04_event_rates | If event rates are below 3%, expand outcomes or countries; do not force rare-event ML. | candidate_only_not_final | Candidate ALB_2002 CHE10-or-access households=2004; CHE25-or-access households=1889; final event rates remain unavailable. | no-go_final_event_rate_claims | Compute event rates only after promoted outcome and sample gates pass. |
| go_no_go_05_predictive_transportability | If leave-country-out predictive performance is poor, do not claim transportable targeting. | not_estimable | No promoted multi-country analysis data or predictive validation metrics exist. | no-go_transportable_targeting_claim | Estimate predictive models only after promoted multi-country outcome and climate-linked data exist. |
| go_no_go_06_climate_lead_placebo | If climate lead placebo predicts outcomes, treat causal design as weak. | not_estimable | No future climate lead variables or promoted reduced-form analysis data exist. | no-go_causal_claims | Construct future climate lead variables after primary exposure extraction and run placebo tests. |
| go_no_go_07_policy_learning_value | If CATE/policy learning does not beat simple rules out of sample, report null targeting value honestly. | rejected_until_reduced_form_passes | Causal ML/policy learning is explicitly rejected until reduced-form and placebo gates pass. | no-go_policy_learning_claim | Attempt CATE and policy learning only after credible reduced-form estimates and validation splits exist. |
| go_no_go_08_descriptive_fallback | If only descriptive evidence survives, write a descriptive data paper and do not claim causal effects. | not_yet_descriptive_paper_ready | Current descriptive screen is temp-only; descriptive_cells=108; promoted descriptive_data_write_ready=0. | go_audit_only_no_go_descriptive_manuscript | Promote harmonized outcomes and climate-linked data before final descriptive prevalence, maps, and sample-flow claims. |

## Audit

| check_id | status | rows_checked | passing_rows | evidence | blocking_reason |
|---|---|---|---|---|---|
| metadata_scorecard_preserved | complete | 38 | 35 | base_rows=38; preserved_non_current_rows=35; current_rows_added=3 | Metadata rows remain screening evidence only. |
| alb2002_current_candidate_design | complete_candidate_not_promoted | 14396 | 14396 | linked_rows=14396; households=3599; descriptive_cells=108; climate_ready=0; outcome_ready=0; data_write_ready=0 | Candidate rows are not analysis-ready and cannot be used for predictive, causal, or policy-learning claims. |
| go_no_go_thresholds | complete_fail_closed | 8 | 8 | threshold_rows=8; failed_or_not_estimable=8; decision=fail_closed_design_scorecard_currently_no_go_for_estimation_or_policy_lea... | All estimation and policy-learning thresholds remain no-go or not estimable. |
| promotion_guardrail | blocked | 38 | 0 | scorecard_rows=38; data_files=4; promoted_rows=4; current_decision=fail_closed_design_scorecard_currently_no_go_for_estimation_... | A design scorecard is planning and audit evidence, not empirical estimation. |

## Interpretation

- ALB_2002 is now the strongest inspected local candidate, but it remains temp-only.
- Candidate event rates and linked climate flags improve prioritization, not empirical identification.
- Main multi-country, predictive, causal, causal-ML, policy-learning, and robustness claims remain no-go until promoted outcomes, harmonized data, accepted climate exposure, and placebo-ready designs exist.

## Machine-Readable Outputs

- `result/design_scorecard.csv`
- `result/design_scorecard_current_audit.csv`
- `result/design_no_go_threshold_audit.csv`
- `result/design_scorecard_current_summary.csv`
