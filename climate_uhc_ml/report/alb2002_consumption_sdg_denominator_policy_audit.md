# ALB_2002 Consumption and SDG Denominator Policy Audit

Status: fail-closed denominator-policy audit. This report quantifies the observed ALB_2002 total-consumption denominator evidence and identifies the missing SDG 3.8.2 inputs. It does not write `data/`, does not construct CHE/SDG outcomes, and does not promote any row to harmonization, outcome construction, or climate linkage.

## Bottom Line

- `total_consumption` is observed for all ALB_2002 household-core candidate rows, but the accepted unit, period, price basis, and inclusion scope are still unresolved.
- CHE10/CHE25 ratios using unreviewed OOP sums are diagnostic stress tests only, not final outcome construction.
- SDG 3.8.2 is blocked because the societal poverty line, 2017 PPP/CPI handling, household discretionary budget, and benchmark validation are not accepted.
- Recipe-ready, outcome-ready, SDG 3.8.2-ready, and climate-linkage-ready rows from this audit: 0.
- Current decision: `blocked_alb2002_consumption_sdg_denominator_policy_not_sdg_ready`.

## Summary

| Metric | Value | Interpretation |
|---|---:|---|
| alb2002_consumption_sdg_denominator_policy_rows | 14 | Rows in the ALB_2002 consumption/SDG denominator policy audit. |
| alb2002_consumption_sdg_household_rows | 3599 | Household rows in the ALB_2002 temp core candidate. |
| alb2002_consumption_sdg_total_consumption_rows | 3599 | Rows with nonmissing total consumption. |
| alb2002_consumption_sdg_positive_total_consumption_rows | 3599 | Rows with positive total consumption. |
| alb2002_consumption_sdg_zero_total_consumption_rows | 0 | Rows with zero total consumption. |
| alb2002_consumption_sdg_negative_total_consumption_rows | 0 | Rows with negative total consumption. |
| alb2002_consumption_sdg_total_consumption_min | 2242.84 | Observed minimum total consumption. |
| alb2002_consumption_sdg_total_consumption_p50 | 30105.6 | Observed median total consumption. |
| alb2002_consumption_sdg_total_consumption_p95 | 64973 | Observed 95th percentile total consumption. |
| alb2002_consumption_sdg_total_consumption_max | 277177 | Observed maximum total consumption. |
| alb2002_consumption_sdg_household_weight_rows | 3599 | Rows with nonmissing household weight. |
| alb2002_consumption_sdg_positive_household_weight_rows | 3599 | Rows with positive household weight. |
| alb2002_consumption_sdg_household_size_rows | 3599 | Rows with nonmissing household size. |
| alb2002_consumption_sdg_positive_household_size_rows | 3599 | Rows with positive household size. |
| alb2002_consumption_sdg_che10_4w_unreviewed_rows | 626 | Diagnostic CHE10 rows using unreviewed four-week OOP over total consumption; not a final outcome. |
| alb2002_consumption_sdg_che10_4w_unreviewed_rate | 0.173937 | Diagnostic CHE10 rate using unreviewed four-week OOP over total consumption; not a final outcome. |
| alb2002_consumption_sdg_che25_4w_unreviewed_rows | 208 | Diagnostic CHE25 rows using unreviewed four-week OOP over total consumption; not a final outcome. |
| alb2002_consumption_sdg_che25_4w_unreviewed_rate | 0.0577938 | Diagnostic CHE25 rate using unreviewed four-week OOP over total consumption; not a final outcome. |
| alb2002_consumption_sdg_che10_12m_unreviewed_rows | 1076 | Diagnostic CHE10 rows using unreviewed twelve-month OOP over total consumption; not a final outcome. |
| alb2002_consumption_sdg_che10_12m_unreviewed_rate | 0.298972 | Diagnostic CHE10 rate using unreviewed twelve-month OOP over total consumption; not a final outcome. |
| alb2002_consumption_sdg_che25_12m_unreviewed_rows | 594 | Diagnostic CHE25 rows using unreviewed twelve-month OOP over total consumption; not a final outcome. |
| alb2002_consumption_sdg_che25_12m_unreviewed_rate | 0.165046 | Diagnostic CHE25 rate using unreviewed twelve-month OOP over total consumption; not a final outcome. |
| alb2002_consumption_sdg_policy_ready_rows | 0 | Audit components accepted for promotion by this audit; intentionally zero. |
| alb2002_consumption_sdg_blocked_component_rows | 14 | Audit components remaining blocked. |
| alb2002_consumption_sdg_spl_ready_rows | 0 | Rows with accepted societal poverty line inputs; intentionally zero. |
| alb2002_consumption_sdg_ppp_cpi_ready_rows | 0 | Rows with accepted PPP/CPI/price-basis inputs; intentionally zero. |
| alb2002_consumption_sdg_discretionary_budget_ready_rows | 0 | Rows with accepted household discretionary budget construction; intentionally zero. |
| alb2002_consumption_sdg_che_denominator_ready_rows | 0 | Rows with accepted CHE denominator construction; intentionally zero. |
| alb2002_consumption_sdg_recipe_ready_rows | 0 | Rows promoted to harmonization recipe by this audit; intentionally zero. |
| alb2002_consumption_sdg_outcome_ready_rows | 0 | Rows promoted to final outcome construction by this audit; intentionally zero. |
| alb2002_consumption_sdg_sdg382_ready_rows | 0 | Rows promoted to SDG 3.8.2 construction by this audit; intentionally zero. |
| alb2002_consumption_sdg_climate_linkage_ready_rows | 0 | Rows promoted to climate linkage by this audit; intentionally zero. |
| alb2002_consumption_sdg_current_decision | blocked_alb2002_consumption_sdg_denominator_policy_not_sdg_ready | Current fail-closed decision for the ALB_2002 consumption/SDG denominator policy audit. |

## Component Families

| Component family | Count |
|---|---:|
| che_total_budget_stress_test | 2 |
| climate_linkage | 1 |
| composite_uhc_failure | 1 |
| household_size_and_daily_pc_conversion | 1 |
| impoverishing_health_spending | 1 |
| oop_health_expenditure_scope | 1 |
| promotion_gate | 1 |
| sdg382_discretionary_budget | 3 |
| survey_weights_and_population_basis | 1 |
| total_welfare_measure | 1 |
| validation_reference | 1 |

## Evidence Status

| Evidence status | Count |
|---|---:|
| blocked_access_denominator_not_outcome_ready | 1 |
| blocked_minimum_recipe_gate | 1 |
| blocked_no_alb2002_household_outcome_benchmark | 1 |
| blocked_no_household_spl_same_period_currency | 1 |
| blocked_no_pre_post_oop_poverty_line | 1 |
| blocked_no_verified_geography | 1 |
| candidate_oop_observed_recall_alignment_blocked | 1 |
| candidate_values_observed_design_semantics_blocked | 1 |
| candidate_values_observed_period_days_blocked | 1 |
| candidate_values_observed_unit_period_blocked | 1 |
| diagnostic_only_not_outcome_ready | 2 |
| missing_ppp_cpi_price_basis | 1 |
| missing_spl_policy_inputs | 1 |

## Component Audit

| component_id | component_family | evidence_status | observed_rows | ready_rows | diagnostic_value |
|---|---|---|---|---|---|
| source_team_total_consumption_candidate | total_welfare_measure | candidate_values_observed_unit_period_blocked | 3599 | 0 | source_file=Poverty_2002.sav; raw_variables=totcons; lineage_status=candidate_unit_period_review_required; positive=3599; zero=... |
| household_size_daily_pc_conversion_candidate | household_size_and_daily_pc_conversion | candidate_values_observed_period_days_blocked | 3599 | 0 | household_size_positive=3599; min=1; p50=4; p95=8; max=15; total_consumption_positive=3599 |
| survey_weight_population_basis_candidate | survey_weights_and_population_basis | candidate_values_observed_design_semantics_blocked | 3599 | 0 | positive_weight_rows=3599; min=40.885; p50=177.517; max=412.2; weighted_positive_total_consumption_denominator=726851 |
| oop_welfare_period_alignment | oop_health_expenditure_scope | candidate_oop_observed_recall_alignment_blocked | 3599 | 0 | oop_policy_rows=11; 4w_positive_rows=2541; 12m_positive_rows=2102; skipped_positive_rows=0; zero_skipped_cells=11 |
| che10_total_consumption_stress_denominator | che_total_budget_stress_test | diagnostic_only_not_outcome_ready | 3599 | 0 | 4w_unreviewed_che10_rows=626; 4w_unreviewed_che10_rate=0.173937; 12m_unreviewed_che10_rows=1076; 12m_unreviewed_che10_rate=0.29... |
| che25_total_consumption_stress_denominator | che_total_budget_stress_test | diagnostic_only_not_outcome_ready | 3599 | 0 | 4w_unreviewed_che25_rows=208; 4w_unreviewed_che25_rate=0.0577938; 12m_unreviewed_che25_rows=594; 12m_unreviewed_che25_rate=0.16... |
| societal_poverty_line_formula | sdg382_discretionary_budget | missing_spl_policy_inputs | 1 | 0 | global_sdg382_ready_rows=0; global_blocked_country_wave_rows=23 |
| ppp_2017_conversion_and_cpi_price_basis | sdg382_discretionary_budget | missing_ppp_cpi_price_basis | 1 | 0 | PPP 2017 conversion, survey currency year/month, and CPI/deflator assumptions are not accepted for this ALB_2002 denominator au... |
| household_discretionary_budget_construction | sdg382_discretionary_budget | blocked_no_household_spl_same_period_currency | 3599 | 0 | household_discretionary_budget cannot be computed because household SPL in the same period/currency as total_consumption is not... |
| impoverishment_denominator_and_poverty_line | impoverishing_health_spending | blocked_no_pre_post_oop_poverty_line | 3599 | 0 | Impoverishing health spending also needs a poverty line and pre/post-OOP welfare scale; no accepted ALB_2002 line exists in thi... |
| external_benchmark_validation | validation_reference | blocked_no_alb2002_household_outcome_benchmark | 1 | 0 | HEFPI/WDI/source roles exist for validation, but household ALB_2002 outcomes are not constructed; global SDG denominator countr... |
| minimum_recipe_consumption_gate_alignment | promotion_gate | blocked_minimum_recipe_gate | 1 | 0 | minimum_recipe_blocked_gates=7; harmonized_ready=0; outcome_ready=0; sdg382_ready=0 |
| access_and_double_failure_dependency | composite_uhc_failure | blocked_access_denominator_not_outcome_ready | 1 | 0 | access_policy_rows=24; access_outcome_ready=0; access_sdg382_ready=0 |
| climate_linkage_dependency | climate_linkage | blocked_no_verified_geography | 1 | 0 | district_crosswalk_climate_ready_rows=0 |

## Interpretation

- The observed `totcons` field is promising denominator evidence, but the audit deliberately preserves the distinction between a visible survey aggregate and an accepted financial-protection denominator.
- Household size and household weights are visible, yet SDG 3.8.2 also requires period, daily per-capita conversion, SPL, PPP/CPI, and price-basis decisions.
- The OOP numerator is still blocked by recall-period, gift/payment scope, skip/missing, and aggregation-policy choices.
- The climate-UHC analysis remains blocked even if the financial denominator improves, because geography and outcome promotion gates are separate.

## Machine-Readable Outputs

- `temp/alb2002_consumption_sdg_denominator_policy_audit.csv`
- `result/alb2002_consumption_sdg_denominator_policy_summary.csv`
