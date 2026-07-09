# ALB_2002 OOP Aggregation Policy Audit

Status: fail-closed outcome-construction stress test. This audit uses ALB_2002 raw Health A payment values and questionnaire-derived payment-scope evidence to compare OOP aggregation policies. It does not write `data/`, does not construct final CHE/SDG outcomes, and does not promote any row to harmonization, outcome, SDG 3.8.2, or climate linkage.

## Bottom Line

- The audit separates provider charges, gifts, medicines, laboratory work, transport, own-purchased drugs, and hospital/dentist 12-month items instead of blindly accepting the existing temp sums.
- It compares four-week, 12-month hospital/dentist, and annualized stress-test OOP policies against the available total-consumption denominator.
- These are stress tests only. They remain blocked by final OOP inclusion policy, SDG 3.8.2 discretionary-budget inputs, recall-period comparability, zero/nonmissing skipped-payment review, and climate-ready district geography.
- Outcome-ready, recipe-ready, SDG 3.8.2-ready, and climate-linkage-ready rows from this audit: 0.
- Current decision: `blocked_alb2002_oop_aggregation_policy_stress_test_not_outcome_ready`.

## Summary

| Metric | Value | Interpretation |
|---|---:|---|
| alb2002_oop_aggregation_policy_rows | 11 | Rows in the ALB_2002 OOP aggregation policy audit. |
| alb2002_oop_aggregation_policy_household_rows | 3599 | Base household rows included in the stress test. |
| alb2002_oop_aggregation_policy_total_consumption_rows | 3599 | Households with positive total consumption denominator. |
| alb2002_oop_aggregation_policy_four_week_policy_rows | 4 | Four-week OOP aggregation policies. |
| alb2002_oop_aggregation_policy_twelve_month_policy_rows | 4 | Twelve-month hospital/dentist OOP aggregation policies. |
| alb2002_oop_aggregation_policy_annual_stress_rows | 3 | Annualized stress-test policies combining four-week and 12-month items. |
| alb2002_oop_aggregation_policy_max_che10_rate | 0.707697 | Maximum unweighted CHE10 stress-test rate across policies. |
| alb2002_oop_aggregation_policy_max_che25_rate | 0.56738 | Maximum unweighted CHE25 stress-test rate across policies. |
| alb2002_oop_aggregation_policy_core_4w_match_rows | 3599 | Rows where recomputed four-week no-gifts-with-transport OOP equals the existing core candidate sum. |
| alb2002_oop_aggregation_policy_core_12m_match_rows | 3599 | Rows where recomputed 12-month no-gifts-with-transport OOP equals the existing core candidate sum. |
| alb2002_oop_aggregation_policy_questionnaire_oop_item_rows_observed | 25 | Questionnaire OOP item rows observed upstream. |
| alb2002_oop_aggregation_policy_questionnaire_gift_item_rows_observed | 6 | Questionnaire gift/payment-scope rows observed upstream. |
| alb2002_oop_aggregation_policy_questionnaire_new_lek_rows_observed | 31 | Questionnaire NEW LEKS unit rows observed upstream. |
| alb2002_oop_aggregation_policy_questionnaire_payment_positive_skip_leaks_observed | 0 | Positive skipped-payment downstream rows observed upstream. |
| alb2002_oop_aggregation_policy_questionnaire_payment_nonmissing_skip_review_observed | 11 | Nonmissing skipped-payment downstream rows requiring review upstream. |
| alb2002_oop_aggregation_policy_minimum_recipe_harmonized_ready_observed | 0 | Harmonized-ready rows observed in the ALB_2002 minimum recipe packet. |
| alb2002_oop_aggregation_policy_minimum_recipe_outcome_ready_observed | 0 | Outcome-ready rows observed in the ALB_2002 minimum recipe packet. |
| alb2002_oop_aggregation_policy_climate_ready_rows_observed | 0 | Climate-linkage-ready rows observed in the district crosswalk audit. |
| alb2002_oop_aggregation_policy_outcome_ready_rows | 0 | Rows promoted to final outcome construction by this audit; intentionally zero. |
| alb2002_oop_aggregation_policy_recipe_ready_rows | 0 | Rows promoted to harmonization recipe by this audit; intentionally zero. |
| alb2002_oop_aggregation_policy_sdg382_ready_rows | 0 | Rows promoted to SDG 3.8.2 construction by this audit; intentionally zero. |
| alb2002_oop_aggregation_policy_climate_linkage_ready_rows | 0 | Rows promoted to climate linkage by this audit; intentionally zero. |
| alb2002_oop_aggregation_policy_current_decision | blocked_alb2002_oop_aggregation_policy_stress_test_not_outcome_ready | Current fail-closed decision for ALB_2002 OOP aggregation stress tests. |

## Policy Stress Tests

| policy_name | recall_scope | included_components | positive_oop_rows | che10_rows | che10_rate | che25_rows | che25_rate | p95_oop_share |
|---|---|---|---|---|---|---|---|---|
| oop_4w_provider_base_only | past_4_weeks | provider charges excluding gifts/medicines/lab/transport | 801 | 69 | 0.019172 | 29 | 0.00805779 | 0.0456601 |
| oop_4w_no_gifts_with_transport | past_4_weeks | provider charges; medicines; lab; transport; own-purchased drugs | 2541 | 626 | 0.173937 | 208 | 0.0577938 | 0.280913 |
| oop_4w_all_observed_with_gifts_transport | past_4_weeks | provider charges; gifts; medicines; lab; transport; own-purchased drugs | 2548 | 657 | 0.182551 | 224 | 0.0622395 | 0.29087 |
| oop_4w_no_gifts_no_transport | past_4_weeks | provider charges; medicines; lab; own-purchased drugs | 2539 | 573 | 0.159211 | 184 | 0.0511253 | 0.250979 |
| oop_12m_provider_base_only | past_12_months_hospital_dentist | hospital-stay and dentist provider charges excluding gifts/medicines/lab/transport | 1942 | 812 | 0.225618 | 429 | 0.1192 | 0.607138 |
| oop_12m_no_gifts_with_transport | past_12_months_hospital_dentist | hospital/dentist provider charges; medicines; lab; transport | 2102 | 1076 | 0.298972 | 594 | 0.165046 | 0.844578 |
| oop_12m_all_observed_with_gifts_transport | past_12_months_hospital_dentist | hospital/dentist provider charges; gifts; medicines; lab; transport | 2122 | 1143 | 0.317588 | 688 | 0.191164 | 1.08934 |
| oop_12m_no_gifts_no_transport | past_12_months_hospital_dentist | hospital/dentist provider charges; medicines; lab | 2079 | 996 | 0.276744 | 538 | 0.149486 | 0.791428 |
| oop_annual_stress_no_gifts_with_transport | stress_annualized_four_week_plus_12m_hospital_dentist | annualized four-week provider/medicine/lab/transport/own-drugs plus 12-month hospital/dentist provider/medicine/lab/transport | 3038 | 2526 | 0.701862 | 1987 | 0.552098 | 4.33181 |
| oop_annual_stress_all_observed_with_gifts_transport | stress_annualized_four_week_plus_12m_hospital_dentist | annualized four-week all observed payment items plus 12-month hospital/dentist all observed payment items | 3047 | 2547 | 0.707697 | 2042 | 0.56738 | 4.63914 |
| oop_annual_stress_no_gifts_no_transport | stress_annualized_four_week_plus_12m_hospital_dentist | annualized four-week provider/medicine/lab/own-drugs plus 12-month hospital/dentist provider/medicine/lab | 3028 | 2505 | 0.696027 | 1958 | 0.54404 | 3.85598 |

## Interpretation

- Four-week policies are not directly comparable to annual total consumption unless an annualization rule is explicitly justified.
- The 12-month hospital/dentist policies omit four-week outpatient, provider, and self-medication spending unless combined in a documented stress-test rule.
- Gift and transport inclusion materially define the policy estimand and must be chosen before any financial-protection outcome is promoted.
- The available positive rates and CHE rates are useful for event-rate screening, not for manuscript claims.

## Machine-Readable Outputs

- `temp/alb2002_oop_aggregation_policy_audit.csv`
- `result/alb2002_oop_aggregation_policy_summary.csv`
