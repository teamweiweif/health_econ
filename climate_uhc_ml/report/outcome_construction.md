# Outcome Construction

Status: limited ALB_2002 CHE-only financial-protection outcomes constructed and audited. SDG 3.8.2, access, composite UHC, climate-linked, and model-ready outcomes remain blocked.

Input for final outcomes: `data/harmonized_household.csv` or equivalent harmonized analytical data.

Final outcome rows currently present: 3599

## Official Financial-Protection Definitions

| Outcome | Formula | Current status |
|---|---|---|
| `sdg382_discretionary_40` | OOP health expenditure > 40% of household discretionary budget | blocked until OOP, household discretionary budget, poverty-line/PPP/CPI handling, units, and recall periods are verified |
| `che10_total_budget` | OOP health expenditure > 10% of total consumption/income | limited ALB_2002 CHE-only outcome promoted from period-aligned OOP and documented monthly total-budget candidate |
| `che25_total_budget` | OOP health expenditure > 25% of total consumption/income | limited ALB_2002 CHE-only outcome promoted from period-aligned OOP and documented monthly total-budget candidate |
| `capacity_to_pay_40` | OOP health expenditure > 40% of capacity to pay | blocked until capacity-to-pay denominator is verified |
| `impoverishing_health_spending` | household is above poverty line before OOP and below after OOP | blocked until poverty-line denominator and OOP timing are verified |

## Constructed Outcomes

| Outcome | Current status |
|---|---|
| `che10_total_budget` | limited CHE-only ALB_2002 outcome; rows=3599; CHE10 rows=824; weighted rate=0.23666 |
| `che25_total_budget` | limited CHE-only ALB_2002 outcome; rows=3599; CHE25 rows=290; weighted rate=0.0859036 |
| `oop_share_total` and `log_oop_plus_one` | limited ALB_2002 continuous financial-protection outcomes |
| SDG 3.8.2, access, composite, and coping outcomes | blocked; SDG/access/composite-ready rows=0/0/0 |

The limited outcome file is `data/household_outcomes.csv`; every row carries guardrail markers showing that climate-linkage-ready and final-analysis-ready rows remain 0 and 0.

## Provisional Raw Diagnostics

| Wave | Audit rows | Financial stress-test rows | Access proxy rows | Low-event rows | Promotion-ready rows | Decision |
|---|---:|---:|---:|---:|---:|---|
| ALB_2002 | 30 | 8 | 15 | 9 | 0 | not_final_outcomes_outcome_semantics_climate_crosswalk_blocked |
| ALB_2012 | 33 | 8 | 15 | 9 | 0 | not_final_outcomes_timing_geography_recall_semantics_blocked |
| ALB_2005 | 23 | 8 | 10 | 6 | 0 | not_final_outcomes_timing_geography_recall_blocked |
| ALB_2008 | 24 | 8 | 11 | 6 | 0 | not_final_outcomes_timing_geography_recall_blocked |

Machine-readable provisional diagnostics:

- `temp/alb2002_provisional_outcome_feasibility_audit.csv`
- `temp/alb2002_outcome_semantics_raw_value_audit.csv`
- `temp/alb2002_health_questionnaire_semantics_audit.csv`
- `temp/alb2012_provisional_outcome_feasibility_audit.csv`
- `temp/alb2012_outcome_semantics_raw_value_audit.csv`
- `temp/alb2005_provisional_outcome_feasibility_audit.csv`
- `temp/alb2005_outcome_semantics_raw_value_audit.csv`
- `temp/alb2005_oop_aggregation_policy_audit.csv`
- `temp/alb2005_skip_missing_semantics_audit.csv`
- `temp/alb2005_consumption_oop_unit_period_audit.csv`
- `temp/alb2005_consumption_aggregate_metadata_crosswalk_audit.csv`
- `temp/alb2005_consumption_component_source_search_audit.csv`
- `temp/alb2005_timing_geography_source_search_audit.csv`
- `temp/alb2008_provisional_outcome_feasibility_audit.csv`
- `temp/alb2008_outcome_semantics_raw_value_audit.csv`

## ALB_2002 Raw Outcome Semantics Audit

| Metric | Value |
|---|---:|
| Raw value/semantics rows | 42 |
| Source health modules scanned | 2 |
| Financial OOP candidate rows | 25 |
| Access candidate rows | 8 |
| Need proxy rows | 2 |
| Rows with value labels | 12 |
| Conditional reason rows | 3 |
| Outcome-ready rows | 0 |
| SDG 3.8.2-ready rows | 0 |
| Decision | blocked_outcome_semantics_units_recall_skip_patterns_unreviewed |

`report/alb2002_outcome_semantics_raw_value_audit.md` documents raw labels, observed values, value-label examples, merge-key coverage, and skip-pattern blockers for ALB_2002 health OOP/access candidates. It strengthens the raw evidence trail but does not promote CHE, SDG 3.8.2, forgone-care, composite, climate-linked, descriptive, causal, ML, or policy outcomes.

## ALB_2002 Health Questionnaire Semantics Audit

| Metric | Value |
|---|---:|
| Questionnaire/skip-path rows | 65 |
| OOP item rows | 25 |
| Gift/payment-scope rows | 6 |
| NEW LEKS unit rows | 31 |
| Four-week OOP rows | 17 |
| Twelve-month OOP rows | 8 |
| Exclusion-note rows | 6 |
| Zero-instruction rows | 10 |
| Access-barrier rows | 8 |
| Cost-barrier rows | 5 |
| Distance-barrier rows | 2 |
| Supply-barrier rows | 3 |
| Payment skip-path rows | 7 |
| Nonmissing downstream payment rows when not triggered | 11 |
| Positive downstream payment rows when not triggered | 0 |
| Zero-or-missing downstream payment rows when triggered | 274 |
| Conditional skip rows | 5 |
| Conditional nonmissing rows when not triggered | 0 |
| Conditional missing rows when triggered | 0 |
| Recipe-ready rows | 0 |
| Outcome-ready rows | 0 |
| SDG 3.8.2-ready rows | 0 |
| Climate-linkage-ready rows | 0 |
| Decision | blocked_alb2002_questionnaire_semantics_seen_but_outcome_not_ready |

| ALB_2002 health questionnaire audit family | Count |
|---|---:|
| health_a_questionnaire | 39 |
| health_b_questionnaire | 14 |
| payment_skip_path | 7 |
| conditional_skip_path | 5 |

| ALB_2002 health questionnaire semantic evidence status | Count |
|---|---:|
| questionnaire_confirms_new_lek_payment_item_but_recall_scope_not_ready | 19 |
| questionnaire_confirms_visit_selection_skip_path_but_denominator_not_ready | 8 |
| questionnaire_confirms_provider_payment_excludes_gifts_medicines_lab_transport | 6 |
| questionnaire_confirms_gift_value_item_scope_policy_required | 6 |
| questionnaire_confirms_access_barrier_codes_but_denominator_not_ready | 5 |
| questionnaire_confirms_health_financing_coping_item_but_denominator_not_ready | 5 |
| raw_skip_path_consistent_no_downstream_values_when_not_triggered | 5 |
| raw_conditional_skip_path_consistent | 5 |
| questionnaire_context_seen_not_recipe_ready | 3 |
| raw_skip_path_positive_values_absent_when_not_triggered_but_zero_nonmissing_review_required | 2 |
| questionnaire_confirms_medicine_discount_entitlement_but_not_failure_outcome | 1 |

| ALB_2002 health questionnaire concept | Count |
|---|---:|
| oop_health_expenditure_item | 25 |
| care_visit_selection_or_denominator | 8 |
| oop_payment_skip_path | 7 |
| gift_payment_scope | 6 |
| care_or_barrier | 6 |
| coping_or_health_financing | 5 |
| access_or_coping_skip_path | 5 |
| access_affordability | 1 |
| medicine_discount_coverage | 1 |
| medicine_discount_access | 1 |

`report/alb2002_health_questionnaire_semantics_audit.md` documents questionnaire-backed NEW LEKS payment-unit evidence, mixed four-week and twelve-month OOP recall, gift/payment-scope rows, access-barrier codes, and raw skip-path consistency. It confirms no positive downstream payment values when visit triggers are negative, but keeps ALB_2002 outcome promotion blocked because denominator semantics, the separate OOP skip-value decision, SDG 3.8.2 construction, and district climate linkage are still unresolved.

## ALB_2002 OOP Aggregation Policy Audit

| Metric | Value |
|---|---:|
| Policy stress-test rows | 11 |
| Household rows | 3599 |
| Positive total-consumption rows | 3599 |
| Four-week policy rows | 4 |
| Twelve-month policy rows | 4 |
| Annualized stress rows | 3 |
| Maximum CHE10 stress-test rate | 0.707697 |
| Maximum CHE25 stress-test rate | 0.56738 |
| Core four-week OOP match rows | 3599 |
| Core twelve-month OOP match rows | 3599 |
| Outcome-ready rows | 0 |
| Recipe-ready rows | 0 |
| SDG 3.8.2-ready rows | 0 |
| Climate-linkage-ready rows | 0 |
| Decision | blocked_alb2002_oop_aggregation_policy_stress_test_not_outcome_ready |

| ALB_2002 OOP policy recall scope | Count |
|---|---:|
| past_4_weeks | 4 |
| past_12_months_hospital_dentist | 4 |
| stress_annualized_four_week_plus_12m_hospital_dentist | 3 |

| ALB_2002 OOP policy promotion status | Count |
|---|---:|
| not_promoted_oop_policy_stress_test_only | 11 |

`report/alb2002_oop_aggregation_policy_audit.md` stress-tests four-week, twelve-month, and annualized ALB_2002 OOP inclusion policies against the verified household denominator. It confirms the recomputed four-week and twelve-month core sums match the existing candidate rows, but it is explicitly not final outcome construction. Outcome, recipe, SDG 3.8.2, and climate-linkage promotion remain blocked until OOP scope, recall comparability, skipped-payment semantics, denominator construction, and district climate geography are resolved.

## ALB_2002 Skip And Missing-Code Semantics Audit

| Metric | Value |
|---|---:|
| Skip/missing audit rows | 12 |
| Payment skip blocks | 7 |
| Access/financing condition blocks | 5 |
| Nonmissing skipped-payment rows | 11 |
| Positive skipped-payment rows | 0 |
| Nonmissing skipped-payment cells | 11 |
| Zero skipped-payment cells | 11 |
| Positive skipped-payment cells | 0 |
| Zero-only payment skip blocks | 2 |
| No-skipped-value payment blocks | 5 |
| Access/financing nonmissing rows when not triggered | 0 |
| Access/financing missing rows when triggered | 0 |
| Outcome-ready rows | 0 |
| Recipe-ready rows | 0 |
| SDG 3.8.2-ready rows | 0 |
| Climate-linkage-ready rows | 0 |
| Decision | blocked_alb2002_skip_missing_semantics_seen_but_recipe_not_ready |

| ALB_2002 skip/missing audit family | Count |
|---|---:|
| person_payment_visit_skip | 7 |
| household_access_condition_skip | 5 |

| ALB_2002 skip/missing evidence status | Count |
|---|---:|
| raw_skip_path_consistent_no_downstream_values_when_not_triggered | 5 |
| raw_conditional_skip_path_consistent | 5 |
| raw_skip_path_nonmissing_values_when_not_triggered_are_zero_only | 2 |

| ALB_2002 zero/missing semantics status | Count |
|---|---:|
| no_skipped_downstream_values_seen | 5 |
| conditional_denominator_manual_policy_required | 5 |
| zero_only_skipped_values_seen_manual_policy_required | 2 |

`report/alb2002_skip_missing_semantics_audit.md` documents that nonmissing skipped downstream payment values are zero-only and that positive skipped-payment rows/cells remain zero. The downstream skip-value decision audit records the no-positive-leakage decision before any OOP, CHE, SDG 3.8.2, access, recipe, or climate-linked outcome can be promoted.

## ALB_2002 OOP Skip-Value Decision Audit

| Metric | Value |
|---|---:|
| Decision audit rows | 5 |
| Payment skip blocks | 7 |
| Access condition blocks | 5 |
| Nonmissing skipped-payment rows | 11 |
| Nonmissing skipped-payment cells | 11 |
| Zero skipped-payment cells | 11 |
| Positive skipped-payment rows | 0 |
| Positive skipped-payment cells | 0 |
| Zero-skip policy-ready rows | 4 |
| OOP recall-scope-ready rows | 0 |
| OOP inclusion-scope-ready rows | 0 |
| Recipe-ready rows | 0 |
| Outcome-ready rows | 0 |
| SDG 3.8.2-ready rows | 0 |
| Climate-linkage-ready rows | 0 |
| Decision | documented_alb2002_oop_skipped_values_zero_only_but_oop_policy_not_ready |

| ALB_2002 OOP skip-value decision family | Count |
|---|---:|
| payment_skip_values | 2 |
| access_condition_boundary | 1 |
| oop_policy_boundary | 1 |
| promotion_boundary | 1 |

| ALB_2002 OOP skip-value promotion status | Count |
|---|---:|
| not_promoted_skip_value_decision_only | 5 |

`report/alb2002_oop_skip_value_decision_audit.md` documents the narrow skipped-payment decision: nontriggered downstream payment cells have no positive leakage, so zero-coded skipped cells do not add positive OOP in stress-test aggregation. It does not choose the final OOP recall period, gift/transport inclusion scope, annualization rule, or household aggregation policy, so all recipe, outcome, SDG 3.8.2, and climate-linkage readiness rows remain zero.

## ALB_2002 Access And Need Denominator Policy Audit

| Metric | Value |
|---|---:|
| Access/need policy rows | 24 |
| Household rows | 3599 |
| Person-level illness/need households | 2202 |
| q01 broad need rows | 3247 |
| q01 cost difficulty rows | 1623 |
| Delayed help rows | 144 |
| Referral not gone rows | 161 |
| Refused service rows | 68 |
| Medicine discount any-barrier rows | 493 |
| Composite cost-barrier rows | 1661 |
| Composite distance-barrier rows | 34 |
| Composite supply/admin-barrier rows | 405 |
| Composite any-access-barrier rows | 1861 |
| Low-event-rate policy rows | 3 |
| Outcome-ready rows | 0 |
| Recipe-ready rows | 0 |
| SDG 3.8.2-ready rows | 0 |
| Climate-linkage-ready rows | 0 |
| Decision | blocked_alb2002_access_need_denominator_policy_not_outcome_ready |

| ALB_2002 access/need outcome family | Count |
|---|---:|
| cost_barrier | 6 |
| forgone_or_delayed_care | 4 |
| distance_barrier | 4 |
| supply_or_admin_barrier | 3 |
| need_denominator | 2 |
| coping_barrier | 1 |
| supply_or_acceptability_barrier | 1 |
| coverage_denominator | 1 |
| medicine_access_barrier | 1 |
| access_failure_composite | 1 |

| ALB_2002 access/need denominator status | Count |
|---|---:|
| conditional_referral_reason_denominator_candidate | 3 |
| conditional_refusal_reason_denominator_candidate | 3 |
| conditional_reason_denominator_candidate | 2 |
| person_level_need_proxy_household_aggregation_required | 1 |
| household_need_denominator_candidate_no_one_needed_care_code_seen | 1 |
| cost_affordability_denominator_candidate | 1 |
| coping_denominator_candidate | 1 |
| delayed_care_denominator_candidate | 1 |
| referral_nonuse_denominator_candidate | 1 |
| refusal_denominator_candidate | 1 |
| coverage_denominator_candidate_not_failure_outcome | 1 |
| medicine_access_denominator_candidate | 1 |
| medicine_cost_denominator_candidate | 1 |
| medicine_supply_admin_denominator_candidate | 1 |
| composite_cost_denominator_candidate | 1 |
| composite_distance_denominator_candidate | 1 |
| composite_supply_admin_denominator_candidate | 1 |
| composite_nonuse_denominator_candidate | 1 |
| composite_access_denominator_candidate | 1 |

| ALB_2002 access/need skip-path status | Count |
|---|---:|
| conditional_reason_denominator_requires_trigger_policy | 6 |
| discount_entitlement_and_need_scope_require_manual_review | 3 |
| composite_union_mixes_conditional_reason_denominators | 2 |
| person_module_not_a_direct_forgone_care_denominator | 1 |
| questionnaire_skip_to_access_items_requires_policy_review | 1 |
| broad_affordability_question_not_forgone_care_by_itself | 1 |
| multi_response_method_semantics_require_manual_review | 1 |
| count_coding_and_need_scope_require_manual_review | 1 |
| referral_need_scope_requires_manual_review | 1 |
| category_scope_requires_manual_supply_acceptability_policy | 1 |
| ever_refusal_scope_requires_period_policy | 1 |
| category_scope_requires_manual_supply_admin_policy | 1 |
| entitlement_scope_not_a_direct_access_failure | 1 |
| composite_union_mixes_broad_affordability_and_conditional_reason_denominators | 1 |
| composite_union_mixes_delay_referral_and_ever_refusal_scopes | 1 |
| composite_union_too_broad_for_final_outcome_without_policy_review | 1 |

`report/alb2002_access_need_denominator_policy_audit.md` separates broad household need, person-level illness need, delayed care, referral nonuse, refusal, medicine-discount access, and cost/distance/supply-admin barrier candidates. It records usable event-rate diagnostics but keeps every access, recipe, SDG 3.8.2, and climate-linkage promotion flag at zero until a denominator policy is explicitly accepted.

## ALB_2002 Consumption And SDG Denominator Policy Audit

| Metric | Value |
|---|---:|
| Denominator policy rows | 14 |
| Household rows | 3599 |
| Positive total-consumption rows | 3599 |
| Positive household-weight rows | 3599 |
| Positive household-size rows | 3599 |
| Median total consumption | 30105.6 |
| 95th percentile total consumption | 64973 |
| Diagnostic CHE10 rate, four-week unreviewed OOP | 0.173937 |
| Diagnostic CHE25 rate, four-week unreviewed OOP | 0.0577938 |
| Diagnostic CHE10 rate, twelve-month unreviewed OOP | 0.298972 |
| Diagnostic CHE25 rate, twelve-month unreviewed OOP | 0.165046 |
| SPL-ready rows | 0 |
| PPP/CPI-ready rows | 0 |
| Discretionary-budget-ready rows | 0 |
| CHE denominator-ready rows | 0 |
| Outcome-ready rows | 0 |
| Recipe-ready rows | 0 |
| SDG 3.8.2-ready rows | 0 |
| Climate-linkage-ready rows | 0 |
| Decision | blocked_alb2002_consumption_sdg_denominator_policy_not_sdg_ready |

| ALB_2002 consumption/SDG component family | Count |
|---|---:|
| sdg382_discretionary_budget | 3 |
| che_total_budget_stress_test | 2 |
| total_welfare_measure | 1 |
| household_size_and_daily_pc_conversion | 1 |
| survey_weights_and_population_basis | 1 |
| oop_health_expenditure_scope | 1 |
| impoverishing_health_spending | 1 |
| validation_reference | 1 |
| promotion_gate | 1 |
| composite_uhc_failure | 1 |
| climate_linkage | 1 |

| ALB_2002 consumption/SDG evidence status | Count |
|---|---:|
| diagnostic_only_not_outcome_ready | 2 |
| candidate_values_observed_unit_period_blocked | 1 |
| candidate_values_observed_period_days_blocked | 1 |
| candidate_values_observed_design_semantics_blocked | 1 |
| candidate_oop_observed_recall_alignment_blocked | 1 |
| missing_spl_policy_inputs | 1 |
| missing_ppp_cpi_price_basis | 1 |
| blocked_no_household_spl_same_period_currency | 1 |
| blocked_no_pre_post_oop_poverty_line | 1 |
| blocked_no_alb2002_household_outcome_benchmark | 1 |
| blocked_minimum_recipe_gate | 1 |
| blocked_access_denominator_not_outcome_ready | 1 |
| blocked_no_verified_geography | 1 |

`report/alb2002_consumption_sdg_denominator_policy_audit.md` quantifies observed `totcons`, household-weight, and household-size coverage, but treats CHE10/CHE25 ratios as diagnostics only. It keeps financial-protection outcome promotion blocked because total-consumption unit/period/price basis, OOP recall alignment, SPL, PPP/CPI, household discretionary budget, benchmark validation, and climate-geography gates have not passed together.

## ALB_2002 Consumption Construction Source Audit

| Metric | Value |
|---|---:|
| Source audit rows | 9 |
| Public method PDF present | 1 |
| Public Stata program ZIP present | 1 |
| Extracted `.do` files | 19 |
| `totcons.do` present | 1 |
| `poverty.do` present | 1 |
| Public metadata JSON present | 1 |
| Documentation-ready rows | 9 |
| Released-variable mapping-ready rows | 3 |
| Denominator-variant-ready rows | 8 |
| Recipe-ready rows | 0 |
| Outcome-ready rows | 0 |
| SDG 3.8.2-ready rows | 0 |
| Climate-linkage-ready rows | 0 |
| Decision | documented_alb2002_consumption_aggregate_but_not_outcome_sdg_climate_ready |

| ALB_2002 consumption construction audit family | Count |
|---|---:|
| code_formula | 2 |
| public_catalog_evidence | 1 |
| official_method_pdf | 1 |
| official_program_files | 1 |
| code_sequence | 1 |
| public_metadata_json | 1 |
| released_spSS_mapping | 1 |
| policy_boundary | 1 |

| ALB_2002 consumption construction evidence status | Count |
|---|---:|
| source_page_downloaded | 1 |
| official_method_pdf_downloaded | 1 |
| official_program_zip_downloaded_and_extracted | 1 |
| pipeline_sequence_seen | 1 |
| denominator_variants_defined | 1 |
| final_poverty_denominator_variant_seen | 1 |
| public_metadata_variable_seen | 1 |
| local_totcons_matches_totcons3_metadata | 1 |
| health_rent_exclusion_documented | 1 |

`report/alb2002_consumption_construction_source_audit.md` records public IHSN source evidence for the ALB_2002 aggregate: the method PDF, released Stata program ZIP, metadata JSON, and local SPSS statistic match. The narrow denominator blocker is resolved: local `totcons` is documented as the public `totcons3` total-budget variant, with durables and without rent and health. Promotion remains blocked because this does not settle the OOP numerator, SPL/PPP/CPI, discretionary-budget, benchmark, or climate-geography gates.

## ALB_2002 Consumption Aggregate Metadata Crosswalk Audit

| Metric | Value |
|---|---:|
| Aggregate crosswalk rows | 11 |
| Local `Poverty_2002.sav` rows | 3599 |
| Local metadata catalog rows | 0 |
| Raw `totcons` positive rows | 3599 |
| Candidate `total_consumption`/raw `totcons` match rows | 3599 |
| Questionnaire New Lek string hits | 8 |
| Questionnaire aggregate-formula hits | 0 |
| Construction-source rows | 9 |
| Construction `.do` file rows | 19 |
| Metadata unit/period-ready rows | 8 |
| Official documentation-ready rows | 9 |
| Released-variable mapping-ready rows | 3 |
| Denominator-variant-ready rows | 8 |
| Recipe-ready rows | 0 |
| Outcome-ready rows | 0 |
| SDG 3.8.2-ready rows | 0 |
| Climate-linkage-ready rows | 0 |
| Decision | documented_alb2002_consumption_aggregate_but_not_outcome_sdg_climate_ready |

| ALB_2002 consumption aggregate audit family | Count |
|---|---:|
| raw_aggregate_metadata_crosswalk | 5 |
| candidate_lineage_crosscheck | 1 |
| scale_plausibility_diagnostic | 1 |
| questionnaire_source_scan | 1 |
| metadata_inventory_gap | 1 |
| public_construction_source_evidence | 1 |
| upstream_sdg_policy_crosscheck | 1 |

| ALB_2002 consumption aggregate readiness status | Count |
|---|---:|
| local_component_seen_not_household_denominator | 4 |
| local_totcons_documented_as_public_totcons3_total_budget_candidate | 1 |
| candidate_copy_verified_but_denominator_semantics_blocked | 1 |
| scale_check_supports_review_not_promotion | 1 |
| questionnaire_item_evidence_seen_aggregate_formula_absent | 1 |
| metadata_inventory_gap_blocks_denominator_acceptance | 1 |
| official_construction_source_documents_total_budget_denominator | 1 |
| upstream_denominator_policy_remains_fail_closed | 1 |

`report/alb2002_consumption_aggregate_metadata_crosswalk_audit.md` verifies that candidate `total_consumption` exactly copies raw `totcons`, and that raw `totcons` is positive for all local poverty-file rows. The updated crosswalk imports the public source audit: `totcons.do`, `poverty.do`, and the IHSN metadata JSON document local `totcons` as public `totcons3`. This is accepted as total-budget denominator provenance only; recipe, outcome, SDG 3.8.2, and climate-linkage promotion remain blocked.

## ALB_2012 Raw Outcome Semantics Audit

| Metric | Value |
|---|---:|
| Raw value/semantics rows | 61 |
| Source health modules scanned | 2 |
| Financial OOP candidate rows | 37 |
| Gift/payment candidate rows | 7 |
| Access candidate rows | 8 |
| Service-quality proxy rows | 7 |
| Need proxy rows | 2 |
| Coping candidate rows | 5 |
| Rows with value labels | 24 |
| Conditional reason rows | 4 |
| Outcome-ready rows | 0 |
| SDG 3.8.2-ready rows | 0 |
| Climate-linkage-ready rows | 0 |
| Decision | blocked_timing_geography_outcome_semantics_units_recall_skip_patterns |

| ALB_2012 raw semantics domain | Count |
|---|---:|
| financial_oop_4w | 26 |
| financial_oop_12m | 11 |
| service_quality_cost_supply_proxy | 7 |
| coping_proxy | 5 |
| access_proxy | 3 |
| access_cost_or_distance_reason | 3 |
| need_proxy | 2 |
| coverage_proxy | 2 |
| access_affordability_proxy | 2 |

| ALB_2012 raw semantics promotion status | Count |
|---|---:|
| not_ready_raw_semantics_only | 61 |

`report/alb2012_outcome_semantics_raw_value_audit.md` documents raw payment, gift, access, need, coping, and service-quality labels and observed values for ALB_2012. It keeps all outcome, SDG 3.8.2, and climate-linkage promotion blocked pending gift-policy, unit, recall-period, missing-code, skip-pattern denominator, timing, geography, and service-quality proxy review.

## ALB_2005 Raw Outcome Semantics Audit

| Metric | Value |
|---|---:|
| Raw value/semantics rows | 53 |
| Source health modules scanned | 2 |
| Financial OOP candidate rows | 36 |
| Gift/payment candidate rows | 7 |
| Access candidate rows | 8 |
| Need proxy rows | 2 |
| Coping candidate rows | 5 |
| Rows with value labels | 17 |
| Conditional reason rows | 3 |
| Outcome-ready rows | 0 |
| SDG 3.8.2-ready rows | 0 |
| Climate-linkage-ready rows | 0 |
| Decision | blocked_timing_geography_outcome_semantics_units_recall_skip_patterns |

| ALB_2005 raw semantics domain | Count |
|---|---:|
| financial_oop_4w | 26 |
| financial_oop_12m | 10 |
| coping_proxy | 5 |
| access_proxy | 3 |
| access_cost_or_distance_reason | 3 |
| need_proxy | 2 |
| coverage_proxy | 2 |
| access_affordability_proxy | 2 |

| ALB_2005 raw semantics promotion status | Count |
|---|---:|
| not_ready_raw_semantics_only | 53 |

`report/alb2005_outcome_semantics_raw_value_audit.md` documents raw labels, observed values, value-label examples, and household merge coverage for ALB_2005 health OOP/access candidates. It shows raw payment/gift/access/coping evidence, but keeps all outcome, SDG 3.8.2, and climate-linkage promotion blocked pending gift-policy, unit, recall-period, missing-code, skip-pattern, timing, and geography review.

## ALB_2005 OOP Aggregation Policy Stress Test

| Metric | Value |
|---|---:|
| Policy stress-test rows | 11 |
| Household rows | 3840 |
| Positive total-consumption denominator rows | 3638 |
| Four-week policy rows | 4 |
| Twelve-month policy rows | 4 |
| Annual stress-test rows | 3 |
| Maximum CHE10 stress-test rate | 0.693788 |
| Maximum CHE25 stress-test rate | 0.532161 |
| Questionnaire OOP rows observed | 36 |
| Questionnaire old-lek rows observed | 36 |
| Outcome-ready rows | 0 |
| Recipe-ready rows | 0 |
| Climate-linkage-ready rows | 0 |
| Decision | blocked_alb2005_oop_aggregation_policy_stress_test_not_outcome_ready |

| ALB_2005 OOP policy recall scope | Count |
|---|---:|
| past_4_weeks | 4 |
| past_12_months_hospital_dentist | 4 |
| stress_annualized_four_week_plus_12m_hospital_dentist | 3 |

| ALB_2005 OOP policy promotion status | Count |
|---|---:|
| not_promoted_oop_policy_stress_test_only | 11 |

`report/alb2005_oop_aggregation_policy_audit.md` compares provider charges, gifts, medicines, laboratory work, transport, and own-purchased drugs across four-week, 12-month, and annualized stress-test policies. These CHE10/CHE25 rates are event-rate and aggregation-policy diagnostics only, not final outcome estimates.

## ALB_2005 Skip/Missing Semantics Audit

| Metric | Value |
|---|---:|
| Skip/missing audit rows | 13 |
| Payment block rows | 8 |
| Access condition rows | 4 |
| Financing multi-response rows | 1 |
| Payment downstream nonmissing when not triggered | 0 |
| Payment downstream positive when not triggered | 0 |
| Triggered payment rows with no positive payment | 326 |
| Conditional reason nonmissing when not triggered | 0 |
| Conditional reason missing when triggered | 0 |
| Financing method nonmissing when not triggered | 0 |
| Financing method missing when triggered | 0 |
| Recipe-ready rows | 0 |
| Outcome-ready rows | 0 |
| Climate-linkage-ready rows | 0 |
| Decision | blocked_alb2005_skip_missing_semantics_seen_but_recipe_not_ready |

| ALB_2005 skip/missing audit family | Count |
|---|---:|
| person_payment_visit_skip | 8 |
| household_access_reason_skip | 4 |
| household_financing_multiselect_skip | 1 |

| ALB_2005 skip/missing evidence status | Count |
|---|---:|
| raw_skip_path_consistent_no_downstream_values_when_not_triggered | 8 |
| raw_conditional_reason_skip_path_consistent | 5 |

`report/alb2005_skip_missing_semantics_audit.md` checks raw trigger/downstream consistency for person-level payment blocks, household access reasons, and health-financing multi-response methods. It documents zero downstream skip leaks in the audited rows, but leaves 326 triggered payment rows with no positive payment for explicit zero/missing-code review and does not promote outcomes.

## ALB_2005 Consumption/OOP Unit and Period Audit

| Metric | Value |
|---|---:|
| Unit-period audit rows | 12 |
| Positive total-consumption rows | 3638 |
| Positive per-capita consumption rows | 3638 |
| Metadata old-lek rows | 6 |
| Questionnaire OOP old-lek rows | 36 |
| Four-week OOP recall rows | 26 |
| Twelve-month OOP recall rows | 10 |
| Nonhealth questionnaire old-lek rows | 15 |
| Median `totcons/rcons/12` diagnostic | 3.76601 |
| Median roster household size | 4 |
| SDG 3.8.2-ready rows | 0 |
| Recipe-ready rows | 0 |
| Outcome-ready rows | 0 |
| Climate-linkage-ready rows | 0 |
| Decision | blocked_alb2005_consumption_oop_unit_period_not_ready |

| ALB_2005 unit-period audit family | Count |
|---|---:|
| consumption_denominator | 5 |
| oop_unit_recall | 3 |
| remaining_blockers | 3 |
| questionnaire_consumption_period | 1 |

| ALB_2005 unit-period evidence status | Count |
|---|---:|
| raw_total_consumption_seen_old_lek_metadata_period_unresolved | 1 |
| raw_per_capita_consumption_seen_scope_review_required | 1 |
| raw_per_capita_components_seen_not_household_totals | 1 |
| metadata_old_lek_formula_labels_seen_period_unresolved | 1 |
| internal_scaling_inference_not_denominator_documentation | 1 |
| questionnaire_old_lek_oop_items_seen_recall_mixed | 1 |
| four_week_oop_recall_seen_not_annual_denominator_ready | 1 |
| twelve_month_oop_recall_seen_partial_scope_not_total_oop_ready | 1 |
| questionnaire_consumption_period_units_seen_aggregate_recipe_missing | 1 |
| skip_missing_semantics_seen_but_zero_review_remains | 1 |
| sdg382_denominator_inputs_missing_or_unverified | 1 |
| climate_timing_geography_not_ready | 1 |

`report/alb2005_consumption_oop_unit_period_audit.md` documents positive `totcons` and `rcons` values, public metadata old-lek labels, questionnaire-backed OOP old-lek rows, and mixed four-week/12-month OOP recall periods. It still promotes zero rows to SDG 3.8.2, harmonization recipes, outcome construction, or climate linkage because total-consumption period/price basis, OOP annualization, PPP/SPL/CPI handling, timing, and geography remain unresolved.

## ALB_2005 Consumption Aggregate Metadata Crosswalk Audit

| Metric | Value |
|---|---:|
| Crosswalk audit rows | 16 |
| Public metadata aggregate/component rows checked | 9 |
| Local poverty.sav columns | 16 |
| Metadata variables present locally | 1 |
| Metadata variables absent locally | 8 |
| Local per-capita diagnostic components | 6 |
| Positive local `totcons` rows | 3638 |
| Local `totcons05` rows | 0 |
| Formula reconstructable rows | 0 |
| SDG 3.8.2-ready rows | 0 |
| Recipe-ready rows | 0 |
| Outcome-ready rows | 0 |
| Climate-linkage-ready rows | 0 |
| Decision | blocked_alb2005_consumption_aggregate_metadata_crosswalk_not_ready |

| ALB_2005 aggregate crosswalk audit family | Count |
|---|---:|
| metadata_aggregate_crosswalk | 9 |
| local_per_capita_aggregate | 6 |
| upstream_blocker_crosscheck | 1 |

| ALB_2005 aggregate crosswalk readiness status | Count |
|---|---:|
| public_metadata_variable_absent_from_local_raw_extract | 8 |
| local_per_capita_component_seen_not_household_denominator | 6 |
| local_totcons_available_but_formula_components_absent | 1 |
| upstream_unit_period_audit_remains_fail_closed | 1 |

`report/alb2005_consumption_aggregate_metadata_crosswalk_audit.md` shows that public metadata lists old-lek aggregate/component variables, but local `poverty.sav` exposes only `totcons` from the checked formula set plus per-capita diagnostics. The `totcons05` variant and formula components are absent locally, so denominator reconstruction, variant choice, SDG 3.8.2, recipes, outcomes, and climate linkage remain blocked.

## ALB_2005 Consumption Component Source Search Audit

| Metric | Value |
|---|---:|
| Source-search audit rows | 37 |
| Target variables searched | 9 |
| Local file rows scanned | 46 |
| Local variable rows scanned | 1187 |
| Questionnaire workbooks scanned | 2 |
| Construction-code files found | 0 |
| Exact target variables found | 1 |
| Exact target variables missing | 8 |
| Label/phrase target leads | 5 |
| Questionnaire phrase target leads | 5 |
| Construction-code target hits | 0 |
| SDG 3.8.2-ready rows | 0 |
| Recipe-ready rows | 0 |
| Outcome-ready rows | 0 |
| Climate-linkage-ready rows | 0 |
| Decision | blocked_alb2005_consumption_component_source_search_not_ready |

| ALB_2005 component source-search audit family | Count |
|---|---:|
| schema_exact_variable_search | 9 |
| schema_label_phrase_search | 9 |
| questionnaire_and_module_search | 9 |
| construction_code_search | 9 |
| upstream_crosscheck | 1 |

| ALB_2005 component source-search evidence status | Count |
|---|---:|
| item_module_or_questionnaire_lead_seen_not_aggregate_recipe | 9 |
| construction_code_hit_not_found | 9 |
| exact_local_raw_variable_not_found | 8 |
| local_label_phrase_hit_seen_not_recipe | 5 |
| local_label_phrase_hit_not_found | 4 |
| exact_local_raw_variable_seen | 1 |
| upstream_aggregate_crosswalk_remains_fail_closed | 1 |

`report/alb2005_consumption_component_source_search_audit.md` searches the local raw schema, file inventory, questionnaires, and source-code-like files for the public-metadata aggregate components. It finds only `totcons` as an exact target-variable hit, no local construction-code files, and zero SDG 3.8.2, recipe, outcome, or climate-linkage promotion. Module and questionnaire phrase hits remain manual-review leads, not denominator recipes.

## ALB_2005 Timing/Geography Source Search Audit

| Metric | Value |
|---|---:|
| Source-search audit rows | 11 |
| Target concepts searched | 5 |
| Local file rows scanned | 46 |
| Local variable rows scanned | 1187 |
| Questionnaire workbooks scanned | 2 |
| Raw targets with hits | 4 |
| Questionnaire targets with hits | 5 |
| Legacy questionnaire timing rows | 83 |
| Verified household timing rows | 0 |
| Coordinate candidate rows | 0 |
| Partial district variable rows | 2 |
| Partial district-name rows | 1899 |
| Partial district-code rows | 329 |
| Required value/key timing rows | 0 |
| Required value/key coordinate rows | 0 |
| Geography-crosswalk-ready rows | 0 |
| Interview-timing-ready rows | 0 |
| Climate-linkage-ready rows | 0 |
| Decision | blocked_alb2005_timing_geography_source_search_not_ready |

| ALB_2005 timing/geography source-search audit family | Count |
|---|---:|
| raw_schema_source_search | 5 |
| questionnaire_source_search | 5 |
| upstream_crosscheck | 1 |

| ALB_2005 timing/geography source-search evidence status | Count |
|---|---:|
| questionnaire_form_design_seen_raw_value_gap_remains | 5 |
| raw_schema_hits_seen_but_not_verified_climate_inputs | 4 |
| raw_schema_hits_not_found | 1 |
| upstream_timing_geography_remains_fail_closed | 1 |

| ALB_2005 timing/geography source-search promotion status | Count |
|---|---:|
| not_promoted_timing_geography_source_search_audit_only | 11 |

`report/alb2005_timing_geography_source_search_audit.md` searches the local raw schema, file inventory, questionnaires, and upstream timing/geography summaries for household interview timing, current-location geography, coordinates, and PSU/cluster evidence. It finds raw and questionnaire leads plus partial district evidence, but verifies zero household interview timing rows, zero coordinate candidates, and zero geography-crosswalk, interview-timing, or climate-linkage promotion.

## ALB_2008 Raw Outcome Semantics Audit

| Metric | Value |
|---|---:|
| Raw value/semantics rows | 61 |
| Source health modules scanned | 3 |
| Financial OOP candidate rows | 36 |
| Gift/payment candidate rows | 9 |
| Access candidate rows | 8 |
| Facility/service-quality proxy rows | 8 |
| Need proxy rows | 2 |
| Coping candidate rows | 5 |
| Rows with value labels | 61 |
| Conditional reason rows | 4 |
| Outcome-ready rows | 0 |
| SDG 3.8.2-ready rows | 0 |
| Climate-linkage-ready rows | 0 |
| Decision | blocked_timing_geography_outcome_semantics_units_recall_skip_patterns |

| ALB_2008 raw semantics domain | Count |
|---|---:|
| financial_oop_4w | 26 |
| financial_oop_12m | 10 |
| service_quality_cost_supply_proxy | 6 |
| coping_proxy | 5 |
| access_proxy | 3 |
| access_cost_or_distance_reason | 3 |
| need_proxy | 2 |
| coverage_proxy | 2 |
| access_affordability_proxy | 2 |
| facility_access_proxy | 2 |

| ALB_2008 raw semantics promotion status | Count |
|---|---:|
| not_ready_raw_semantics_only | 61 |

`report/alb2008_outcome_semantics_raw_value_audit.md` documents raw labels, observed values, value-label examples, and household merge coverage for ALB_2008 health OOP/access candidates. It adds service-quality and facility proxy evidence from module 9C, but keeps all outcome, SDG 3.8.2, and climate-linkage promotion blocked pending gift-policy, unit, recall-period, missing-code, skip-pattern, timing, geography, and proxy-interpretation review.

## Caveats

- These provisional diagnostics are not final outcomes and are not written to `data/`.
- Four-week and twelve-month OOP fields are not pooled unless a documented recall-period rule is verified.
- SDG 3.8.2 is not inferred without a verified discretionary-budget denominator.
- Access proxies require skip-pattern, need-denominator, and missing-code review before any forgone-care outcome can be promoted.
- ALB_2002 has observed interview date/month and district fields, but climate linkage still requires a validated district crosswalk, boundary-name mismatch review, historical boundary verification, and no-GPS measurement-error handling.
- ALB_2005 has raw payment, gift, access, and coping evidence, but survey timing and full climate-ready geography are still unverified.
- ALB_2008 has raw payment, gift, access, coping, and facility/service-quality evidence, but survey timing and climate-ready geography are still unverified.
- ALB_2012 has raw payment, gift, access, coping, service-quality, questionnaire timing-field, and fallback blocker-resolution evidence, but raw household interview timing and climate-ready geography are still unverified.
- ALB_2002/2005/2008 legacy `.xls` questionnaires are present and readable in the current environment, but readable form text is not enough: raw skip paths, payment-scope policy, missing-code semantics, fieldwork timing, and climate-ready geography still need verification before outcome promotion.
- No descriptive prevalence, predictive ML, causal, causal ML, or policy-targeting claim can be made from these diagnostics.

## Audit Files

- `result/outcome_audit.csv`
- `temp/outcome_construction_audit.csv`
