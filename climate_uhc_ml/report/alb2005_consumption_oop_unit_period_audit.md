# ALB_2005 Consumption/OOP Unit and Period Audit

Status: fail-closed denominator evidence audit. This audit reviews ALB_2005 total-consumption, per-capita consumption, OOP payment-unit, and recall-period evidence. It does not write `data/`, does not construct CHE/SDG outcomes, and does not promote any row to harmonization, outcome construction, SDG 3.8.2, or climate linkage.

## Bottom Line

- `poverty.sav` contains positive `totcons` and `rcons` values for 3,638 households, and public metadata labels document old-lek aggregate variables.
- Health questionnaire payment items explicitly use old lek, but their recall periods are mixed: four-week outpatient/self-medication rows and 12-month hospital/dentist rows.
- Item-level nonhealth questionnaire sections contain old-lek and period wording, but the available local evidence still lacks the final aggregate construction note needed to certify total-consumption period, price basis, and denominator use.
- The internal `totcons / rcons / 12` check is household-size-like, but it does not match raw roster counts closely enough to serve as documentation.
- SDG 3.8.2, recipe-ready, outcome-ready, and climate-linkage-ready rows from this audit: 0.
- Current decision: `blocked_alb2005_consumption_oop_unit_period_not_ready`.

## Summary

| Metric | Value | Interpretation |
|---|---:|---|
| alb2005_consumption_oop_unit_period_rows | 12 | Rows in the ALB_2005 consumption/OOP unit-period audit. |
| alb2005_consumption_oop_unit_period_total_consumption_nonmissing_rows | 3638 | Nonmissing ALB_2005 total-consumption rows observed upstream. |
| alb2005_consumption_oop_unit_period_total_consumption_positive_rows | 3638 | Positive total-consumption rows in poverty.sav. |
| alb2005_consumption_oop_unit_period_rcons_positive_rows | 3638 | Positive per-capita consumption rows in poverty.sav. |
| alb2005_consumption_oop_unit_period_metadata_old_lek_rows_observed | 6 | Public metadata aggregate labels mentioning old lek. |
| alb2005_consumption_oop_unit_period_oop_old_lek_questionnaire_rows_observed | 36 | Questionnaire OOP payment rows explicitly recorded in old lek. |
| alb2005_consumption_oop_unit_period_four_week_oop_rows_observed | 26 | Questionnaire OOP rows with past-four-week recall. |
| alb2005_consumption_oop_unit_period_twelve_month_oop_rows_observed | 10 | Questionnaire OOP rows with past-12-month recall. |
| alb2005_consumption_oop_unit_period_questionnaire_nonfood_old_lek_rows_observed | 15 | Nonhealth consumption/expenditure questionnaire rows with old-lek text. |
| alb2005_consumption_oop_unit_period_questionnaire_consumption_period_rows_observed | 9 | Nonhealth consumption/expenditure questionnaire rows with 12-month, monthly, or 30-day period text. |
| alb2005_consumption_oop_unit_period_totcons_rcons_roster_join_rows | 3638 | Poverty rows joined to raw roster household counts for scaling diagnostics. |
| alb2005_consumption_oop_unit_period_totcons_rcons_implied_scale_median | 3.76601 | Median of totcons/rcons/12, used only as an internal scaling diagnostic. |
| alb2005_consumption_oop_unit_period_roster_hhsize_median | 4 | Median raw roster household member count. |
| alb2005_consumption_oop_unit_period_totcons_rcons_abs_diff_le_0_1_rows | 439 | Rows where totcons/rcons/12 is within 0.1 of raw roster size. |
| alb2005_consumption_oop_unit_period_value_decision_recipe_ready_observed | 0 | Recipe-ready rows observed in upstream value-decision audit. |
| alb2005_consumption_oop_unit_period_required_value_key_recipe_ready_observed | 0 | Recipe-ready rows observed in upstream required value/key audit. |
| alb2005_consumption_oop_unit_period_oop_policy_rows_observed | 11 | OOP aggregation stress-test rows observed upstream. |
| alb2005_consumption_oop_unit_period_skip_missing_rows_observed | 13 | Skip/missing audit rows observed upstream. |
| alb2005_consumption_oop_unit_period_sdg382_ready_rows | 0 | Rows promoted to SDG 3.8.2 denominator readiness by this audit; intentionally zero. |
| alb2005_consumption_oop_unit_period_recipe_ready_rows | 0 | Rows promoted to harmonization recipe by this audit; intentionally zero. |
| alb2005_consumption_oop_unit_period_outcome_ready_rows | 0 | Rows promoted to outcome construction by this audit; intentionally zero. |
| alb2005_consumption_oop_unit_period_climate_linkage_ready_rows | 0 | Rows promoted to climate linkage by this audit; intentionally zero. |
| alb2005_consumption_oop_unit_period_current_decision | blocked_alb2005_consumption_oop_unit_period_not_ready | Current fail-closed decision for ALB_2005 denominator unit/period evidence. |

## Evidence Rows

| audit_family | evidence_item | source_file | source_variable | nonmissing_rows | positive_rows | unit_evidence | period_evidence | evidence_status |
|---|---|---|---|---|---|---|---|---|
| consumption_denominator | survey_total_consumption_raw_value | poverty.sav | totcons | 3638 | 3638 | food: Total food consumption in old lek (new lek=old lek/10); nfoodc: Total non-food consumption component in Old Lek (new lek=old lek/10); nfood05... | Raw poverty.sav label does not state recall or annual/monthly period; public metadata gives components but not enough period/price-basis detail for... | raw_total_consumption_seen_old_lek_metadata_period_unresolved |
| consumption_denominator | per_capita_consumption_raw_value | poverty.sav | rcons | 3638 | 3638 | Raw label indicates per-capita consumption but not currency conversion. | Internal scaling against totcons is informative but not documentation. | raw_per_capita_consumption_seen_scope_review_required |
| consumption_denominator | per_capita_component_values | poverty.sav | rcons;rfood;rnfood;rutility;reduexp;rdurable | 3638 | 2164 | rcons positive=3638 p50=8605.78; rfood positive=3638 p50=4909.32; rnfood positive=3634 p50=1838.87; rutility positive=3638 p50=1065.94; reduexp pos... | Component labels are per-capita aggregates and do not independently document the household denominator period. | raw_per_capita_components_seen_not_household_totals |
| consumption_denominator | metadata_old_lek_aggregate_labels | metadata_variable_catalog.csv | food;nfoodc;nfood05;totutil;totutil05;totcons;totcons05 | 7 | 6 | Public metadata labels state old lek and new lek equals old lek divided by 10 for several aggregate variables. | Metadata labels identify formula components but still do not resolve recall-period harmonization or price-basis requirements for SDG 3.8.2. | metadata_old_lek_formula_labels_seen_period_unresolved |
| consumption_denominator | totcons_rcons_roster_scaling_check | poverty.sav;Modul_1A_household_rostera_cl.sav | totcons;rcons;psu;hh | 3638 | 439 | The ratio is household-size-like but does not equal raw roster counts for most households. | The ratio is consistent with possible annual/monthly scaling, but this remains an inference from values, not documentation. | internal_scaling_inference_not_denominator_documentation |
| oop_unit_recall | health_oop_old_lek_payment_items | LSMS05_Questionnaire_part2.xls;Modul_9A_healtha_cl.sav | health payment item variables | 36 | 36 | Health questionnaire payment items explicitly use OLD LEKS. | Payment items split between past 4 weeks and past 12 months. | questionnaire_old_lek_oop_items_seen_recall_mixed |
| oop_unit_recall | four_week_oop_recall_items | LSMS05_Questionnaire_part2.xls;Modul_9A_healtha_cl.sav | m9a_q16-m9a_q61 | 26 | 26 | Four-week OOP rows use old-lek payment units. | Questionnaire rows explicitly refer to past 4 weeks for outpatient, provider, medicine, lab, transport, and own-drug payment items. | four_week_oop_recall_seen_not_annual_denominator_ready |
| oop_unit_recall | twelve_month_oop_recall_items | LSMS05_Questionnaire_part2.xls;Modul_9A_healtha_cl.sav | m9a_q68-m9a_q81 | 10 | 10 | Twelve-month hospital/dentist OOP rows use old-lek payment units. | Questionnaire rows explicitly refer to past 12 months for hospital-stay and dentist payment items. | twelve_month_oop_recall_seen_partial_scope_not_total_oop_ready |
| questionnaire_consumption_period | nonhealth_consumption_questionnaire_period_units | LSMS05_Questionnaire_part2.xls | nonfood/dwelling/social-assistance rows | 5 | 15 | Workbook scan status=read_ok; old-lek rows in nonhealth consumption sheets=15. | Questionnaire nonhealth expenditure sections contain 12-month and monthly wording, but this does not document the final aggregate construction. | questionnaire_consumption_period_units_seen_aggregate_recipe_missing |
| remaining_blockers | zero_missing_and_skip_semantics | result/alb2005_skip_missing_semantics_summary.csv | skip/missing summary | 0 | 0 | Skip-leak checks reduce missing-code ambiguity for downstream variables under negative triggers. | They do not address recall-period harmonization or denominator period. | skip_missing_semantics_seen_but_zero_review_remains |
| remaining_blockers | sdg382_discretionary_budget_inputs | source_audit;sdg382_denominator_plan;ALB_2005 audits | societal_poverty_line;PPP;CPI;discretionary_budget | 0 | 0 | Local-currency old-lek evidence exists, but not an audited PPP/CPI/SPL conversion. | Total-consumption period and OOP annualization are unresolved. | sdg382_denominator_inputs_missing_or_unverified |
| remaining_blockers | climate_timing_geography_linkage | result/alb2005_timing_geography_exhaustive_summary.csv | interview_timing;coordinates;admin geography | 0 | 0 | Not a currency-unit issue. | No verified household interview month/date exists for climate exposure windows. | climate_timing_geography_not_ready |

## Interpretation

- Old-lek evidence is stronger than before, but old/new lek scaling alone is not sufficient for financial-protection outcomes.
- A valid CHE denominator still needs a documented total-consumption period, household-total scope, price basis, missing-code handling, and survey design treatment.
- SDG 3.8.2 additionally needs societal poverty line, PPP/CPI alignment, and discretionary-budget construction.
- Climate-linked analysis remains blocked independently by missing verified household interview timing and climate-ready geography.

## Machine-Readable Outputs

- `temp/alb2005_consumption_oop_unit_period_audit.csv`
- `result/alb2005_consumption_oop_unit_period_summary.csv`
