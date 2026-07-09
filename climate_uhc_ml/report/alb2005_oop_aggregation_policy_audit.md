# ALB_2005 OOP Aggregation Policy Audit

Status: fail-closed outcome-construction stress test. This audit uses ALB_2005 raw health-payment values and questionnaire-derived payment-scope evidence to compare OOP aggregation policies. It does not write `data/`, does not construct final CHE/SDG outcomes, and does not promote any row to harmonization, outcome, or climate linkage.

## Bottom Line

- The audit separates provider charges, gifts, medicines, laboratory work, transport, and own-purchased drugs instead of blindly summing all health-module payment fields.
- It compares four-week, 12-month hospital/dentist, and annualized stress-test OOP policies against the available `totcons` denominator.
- These are stress tests only. They remain blocked by final OOP inclusion policy, missing-code semantics, recall-period comparability, verified household interview timing, and climate-ready geography.
- Outcome-ready, recipe-ready, and climate-linkage-ready rows from this audit: 0.
- Current decision: `blocked_alb2005_oop_aggregation_policy_stress_test_not_outcome_ready`.

## Summary

| Metric | Value | Interpretation |
|---|---:|---|
| alb2005_oop_aggregation_policy_rows | 11 | Rows in the ALB_2005 OOP aggregation policy audit. |
| alb2005_oop_aggregation_policy_household_rows | 3840 | Base household rows included in the stress test. |
| alb2005_oop_aggregation_policy_total_consumption_rows | 3638 | Households with positive total consumption denominator. |
| alb2005_oop_aggregation_policy_four_week_policy_rows | 4 | Four-week OOP aggregation policies. |
| alb2005_oop_aggregation_policy_twelve_month_policy_rows | 4 | Twelve-month hospital/dentist OOP aggregation policies. |
| alb2005_oop_aggregation_policy_annual_stress_rows | 3 | Annualized stress-test policies combining four-week and 12-month items. |
| alb2005_oop_aggregation_policy_max_che10_rate | 0.693788 | Maximum unweighted CHE10 stress-test rate across policies. |
| alb2005_oop_aggregation_policy_max_che25_rate | 0.532161 | Maximum unweighted CHE25 stress-test rate across policies. |
| alb2005_oop_aggregation_policy_questionnaire_oop_item_rows_observed | 36 | Questionnaire OOP item rows observed upstream. |
| alb2005_oop_aggregation_policy_questionnaire_old_lek_rows_observed | 36 | Questionnaire old-lek unit rows observed upstream. |
| alb2005_oop_aggregation_policy_required_value_key_recipe_ready_observed | 0 | Recipe-ready rows observed in the required value/key audit. |
| alb2005_oop_aggregation_policy_timing_verified_rows_observed | 0 | Verified interview-timing rows observed in the required value/key audit. |
| alb2005_oop_aggregation_policy_climate_ready_rows_observed | 0 | Climate-linkage-ready rows observed in the timing/geography audit. |
| alb2005_oop_aggregation_policy_outcome_ready_rows | 0 | Rows promoted to final outcome construction by this audit; intentionally zero. |
| alb2005_oop_aggregation_policy_recipe_ready_rows | 0 | Rows promoted to harmonization recipe by this audit; intentionally zero. |
| alb2005_oop_aggregation_policy_climate_linkage_ready_rows | 0 | Rows promoted to climate linkage by this audit; intentionally zero. |
| alb2005_oop_aggregation_policy_current_decision | blocked_alb2005_oop_aggregation_policy_stress_test_not_outcome_ready | Current fail-closed decision for ALB_2005 OOP aggregation stress tests. |

## Policy Stress Tests

| policy_name | recall_scope | included_components | positive_oop_rows | che10_rows | che10_rate | che25_rows | che25_rate | p95_oop_share |
|---|---|---|---|---|---|---|---|---|
| oop_4w_provider_base_only | past_4_weeks | provider charges excluding gifts/medicines/lab/transport | 935 | 64 | 0.0175921 | 16 | 0.00439802 | 0.0496326 |
| oop_4w_no_gifts_with_transport | past_4_weeks | provider charges; medicines; lab; transport; own-purchased drugs | 2535 | 533 | 0.146509 | 159 | 0.0437053 | 0.232009 |
| oop_4w_all_observed_with_gifts_transport | past_4_weeks | provider charges; gifts; medicines; lab; transport; own-purchased drugs | 2540 | 554 | 0.152281 | 173 | 0.0475536 | 0.240369 |
| oop_4w_no_gifts_no_transport | past_4_weeks | provider charges; medicines; lab; own-purchased drugs | 2533 | 499 | 0.137163 | 132 | 0.0362837 | 0.214049 |
| oop_12m_provider_base_only | past_12_months_hospital_dentist | hospital-stay and dentist provider charges excluding gifts/medicines/lab/transport | 1956 | 863 | 0.237218 | 412 | 0.113249 | 0.60252 |
| oop_12m_no_gifts_with_transport | past_12_months_hospital_dentist | hospital/dentist provider charges; medicines; lab; transport | 2082 | 1051 | 0.288895 | 534 | 0.146784 | 0.745048 |
| oop_12m_all_observed_with_gifts_transport | past_12_months_hospital_dentist | hospital/dentist provider charges; gifts; medicines; lab; transport | 2106 | 1136 | 0.312259 | 619 | 0.170148 | 0.948134 |
| oop_12m_no_gifts_no_transport | past_12_months_hospital_dentist | hospital/dentist provider charges; medicines; lab | 2058 | 1003 | 0.275701 | 498 | 0.136888 | 0.705116 |
| oop_annual_stress_no_gifts_with_transport | stress_annualized_four_week_plus_12m_hospital_dentist | annualized four-week provider/medicine/lab/transport/own-drugs plus 12-month hospital/dentist provider/medicine/lab/transport | 3034 | 2487 | 0.683617 | 1868 | 0.513469 | 3.55773 |
| oop_annual_stress_all_observed_with_gifts_transport | stress_annualized_four_week_plus_12m_hospital_dentist | annualized four-week all observed payment items plus 12-month hospital/dentist all observed payment items | 3042 | 2524 | 0.693788 | 1936 | 0.532161 | 3.91181 |
| oop_annual_stress_no_gifts_no_transport | stress_annualized_four_week_plus_12m_hospital_dentist | annualized four-week provider/medicine/lab/own-drugs plus 12-month hospital/dentist provider/medicine/lab | 3027 | 2458 | 0.675646 | 1839 | 0.505498 | 3.32772 |

## Interpretation

- Four-week policies are not directly comparable to annual total consumption unless an annualization rule is explicitly justified.
- The 12-month hospital/dentist policies omit four-week outpatient, provider, and self-medication spending unless combined in a documented stress-test rule.
- Gift and transport inclusion materially define the policy estimand and must be chosen before any financial-protection outcome is promoted.
- The available positive rates and CHE rates are useful for event-rate screening, not for manuscript claims.

## Machine-Readable Outputs

- `temp/alb2005_oop_aggregation_policy_audit.csv`
- `result/alb2005_oop_aggregation_policy_summary.csv`
