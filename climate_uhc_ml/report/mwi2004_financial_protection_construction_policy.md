# Malawi 2004 Financial-Protection Construction Policy

Dataset: `MWI_2004_IHS-II_v01_M` - Malawi 2004-2005

This artifact accepts the raw-value policy for CHE10/CHE25 financial inputs
only. It does not construct SDG 3.8.2, does not write rows to `data/`, does not
resolve health/access gates, and does not accept a climate-linkage route.

## Summary

| metric | value | interpretation |
| --- | --- | --- |
| country_wave | MWI_2004_IHS-II_v01_M | Country-wave covered by this financial-protection construction policy. |
| household_financial_rows | 11280 | Rows meeting verified household financial input requirements for CHE10/CHE25 candidates. |
| household_case_id_duplicate_rows | 0 | Duplicate household keys across household, poverty, and expenditure files. |
| positive_household_weight_rows | 11280 | Rows with positive hhwght in the poverty/consumption file. |
| strata_distinct | 30 | Distinct survey strata in the household financial universe. |
| psu_distinct | 564 | Distinct V51 household EA/PSU identifiers after join. |
| rexpagg_positive_rows | 11280 | Positive total annual household expenditure rows. |
| rexp_cat06_nonmissing_rows | 11280 | Nonmissing annual household health OOP aggregate rows. |
| oop_component_diff_le_0_01_rows | 11280/11280 | OOP aggregate-component agreement under 0.01 local currency tolerance. |
| che10_candidate_rows | 208 | Candidate CHE10 rows among verified household financial inputs. |
| che10_candidate_weighted_rate | 0.0185338 | Weighted CHE10 candidate rate; audit statistic only, not promoted data. |
| che25_candidate_rows | 17 | Candidate CHE25 rows among verified household financial inputs. |
| che25_candidate_weighted_rate | 0.0014615 | Weighted CHE25 candidate rate; audit statistic only, not promoted data. |
| weights_design_final_verified_for_financial | 1 | Weight, strata, and household PSU fields are accepted for household financial CHE candidates. |
| consumption_or_income_final_verified_for_che | 1 | rexpagg is accepted as CHE10/CHE25 total-budget denominator. |
| oop_health_expenditure_final_verified_for_che | 1 | rexp_cat06 is accepted as annual household health OOP aggregate for CHE10/CHE25. |
| che10_che25_financial_inputs_ready | 1 | Financial-protection inputs are raw-value verified for CHE10/CHE25 only. |
| sdg382_ready | 0 | SDG 3.8.2 remains blocked by discretionary-budget/societal-poverty-line policy. |
| financial_policy_status | che10_che25_financial_inputs_verified_sdg382_blocked | CHE10/CHE25 financial inputs accepted; SDG 3.8.2 and data writes remain blocked. |
| data_write_gate_status | closed | No promoted dataset may be written from this policy artifact alone. |

## Policy Rows

| policy_component | accepted_rule | raw_variables | aggregate_count | acceptance_status | remaining_blocker |
| --- | --- | --- | --- | --- | --- |
| household_financial_universe | Use one row per household case_id from ihs2_pov.dta after exact case_id joins to ihs2_household.dta and ihs2_exp.dta. | case_id | 11280 | raw_value_verified_for_che10_che25 | This verifies the household financial universe only; person-level access and climate-linked data remain blocked. |
| survey_weight_and_design | Use hhwght as household weight, strata as district-by-urban/rural stratum, and V51/V13 as the household EA/PSU identifier for household-level financial estimates. | hhwght;strata;V51;V13;dist;ta;ea | 11280 | raw_value_verified_for_che10_che25 | Survey design is verified for household financial estimates; cluster choice must be rechecked for person-level access and future cross-country modeling. |
| che_denominator_total_consumption | Use rexpagg as total annual household expenditure denominator for CHE10/CHE25. | rexpagg | 11280 | raw_value_verified_for_che10_che25 | This accepts CHE10/CHE25 total-budget denominator only; SDG 3.8.2 discretionary-budget denominator remains blocked. |
| oop_health_spending | Use rexp_cat06 as annual real household health OOP aggregate; use rexp_cat061-063 only as component consistency evidence. | rexp_cat06;rexp_cat061;rexp_cat062;rexp_cat063 | 11280 | raw_value_verified_for_che10_che25 | Health-module recall-period spending remains context only; promoted CHE uses the survey-team annual household aggregate. |
| che10_candidate | Construct CHE10 as rexp_cat06 / rexpagg > 0.10 among verified household financial rows. | rexp_cat06;rexpagg;hhwght;strata;V51 | 208 | candidate_outcome_ready_after_data_write_gate | Do not write the outcome to data/ until missing-code policy, synthesis, and registry write gate pass. |
| che25_candidate | Construct CHE25 as rexp_cat06 / rexpagg > 0.25 among verified household financial rows. | rexp_cat06;rexpagg;hhwght;strata;V51 | 17 | candidate_outcome_ready_after_data_write_gate | Do not write the outcome to data/ until missing-code policy, synthesis, and registry write gate pass. |
| sdg382_discretionary_budget | Do not construct SDG 3.8.2 yet; the current raw file poverty line is documented but not accepted as the current societal poverty-line input. | povline;price_index;hhsize;rexpagg;rexp_cat06 | 0 | blocked_sdg382_discretionary_budget_policy_required | Need PPP/CPI/societal poverty-line policy before SDG 3.8.2 can be marked ready. |

## Accepted For CHE10/CHE25

- Household universe: unique `case_id` rows from `ihs2_pov.dta`, joined to
  `ihs2_household.dta` and `ihs2_exp.dta`.
- Survey design: `hhwght`, `strata`, and household EA/PSU identifier `V51`
  with `V13` as the same PSU-style field in the poverty file.
- Denominator: `rexpagg`, labeled total annual household expenditure.
- OOP: `rexp_cat06`, labeled health real annual household expenditure, checked
  against `rexp_cat061 + rexp_cat062 + rexp_cat063`.

## Still Blocked

- SDG 3.8.2 remains blocked until the discretionary-budget denominator and
  current societal poverty-line/PPP/CPI policy are accepted.
- Person-level health/access, missing/skip policy, climate linkage, synthesis,
  and registry write gates remain closed.
- Candidate CHE10/CHE25 counts in this artifact are audit statistics, not
  promoted analysis data.
