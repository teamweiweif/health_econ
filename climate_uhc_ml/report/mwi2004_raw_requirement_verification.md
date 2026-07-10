# Malawi 2004 Raw Requirement Verification Evidence

Dataset: `MWI_2004_IHS-II_v01_M` - Malawi 2004-2005

Purpose: move this country-wave from raw package receipt toward raw-value
verification by reading selected original Stata files and producing compact
evidence for keys, joins, weights/design, financial-protection inputs,
health-need/access variables, timing, and geography.

This is not a promoted analysis dataset. It does not write to `data/`, does
not mark Malawi 2004 as value-verified, and does not open the modeling gate.

## Summary

| metric | value | interpretation |
| --- | --- | --- |
| country_wave | MWI_2004_IHS-II_v01_M | Focused raw requirement verification evidence generated for this country-wave. |
| source_raw_package | temp\raw_downloads\MWI_2004_IHS-II_v01_M\MWI_2004_IHS-II_v01_M_Stata8.zip | Original raw package read locally; raw package itself remains excluded from Git. |
| members_read | 6 | Selected raw Stata members read from the received Malawi 2004 package. |
| requirements_with_raw_backed_evidence | 8 | Promotion requirements with focused raw-backed evidence rows. |
| key_or_join_checks_passing | 10/11 | Uniqueness and join checks whose mechanical raw-profile status passed. |
| missing_requested_columns | 0 | Requested audit variables not found in selected raw members. |
| raw_value_verification_decision | not_final_verified | This script strengthens evidence but does not promote the country-wave or open the data write gate. |
| data_write_gate_status | closed | No output from this script is an analysis-ready household-climate dataset. |

## Requirement Evidence

| requirement | raw_backed_evidence_status | verification_decision | evidence_summary | remaining_manual_review |
| --- | --- | --- | --- | --- |
| household_person_keys | raw_backed_key_join_evidence_ready | not_final_verified | Household, expenditure, and poverty files are profiled for case_id uniqueness; individual and health modules are profiled for case_id+memid; join coverage rows are in mwi2004_raw_module_join_evidence.csv. | Confirm official key definitions and any module-level exclusions in questionnaire/documentation before accepting full raw-value verification. |
| weights_and_design | raw_backed_weight_design_evidence_ready | not_final_verified | Household hhwght positive rows=11280; strata distinct=30; dist+ta+ea distinct=564; sec_d includes hhwght, psu, strata, and geography fields. | Confirm sample design documentation and whether PSU should be psu, V51/V13, or dist+ta+ea for each analytic file. |
| consumption_or_income | raw_backed_denominator_candidate_ready | not_final_verified | rexpagg candidate total annual household expenditure has positive rows=11280; poverty-line and price-index fields are present for policy review. | Accept denominator policy, units, household/person scaling, missing semantics, and current SDG 3.8.2 poverty-line mapping. |
| oop_health_expenditure | raw_backed_oop_aggregate_candidate_ready | not_final_verified | Annual household health aggregate rexp_cat06 nonmissing rows=11280; real health component rows=11280; health module has individual spending candidates for recall-period review. | Confirm exact OOP definition, exclusions, recall-to-annual handling, and whether survey-team aggregate is preferred over section D item sums. |
| health_need_and_access | raw_backed_health_need_access_candidate_ready | not_final_verified | Health module has illness/injury, action taken, hospitalization, borrowing/selling assets, chronic illness, maternal-care variables. Top values: d04: 2=No (36739); 1=Yes (14143); d07a: 9=Went to local grocery for medicine (5291); 5=Sought treatment at gvt health fac. (4298); 1=Did nothing, not serious (1260); 7=Sought treatment atpvt health facility (791); 2=Did nothing, no money (610); 10=Sought treatment with trad. healer (479); d07b: 99=No other action taken (443); 9=Went to local grocery for medicine (385); 5=Sought treatment at gvt health fac. (354); 1=Did nothing, not serious (92); 7=Sought treatment atpvt health facility (73); 2=Did nothing, no money (50); d15: 2=No (48835); 1=Yes (2051); d17: 2=No (1469); 1=Yes (458); d20: 2=No (230); 1=Yes (185); d26: 2=No (45961); 1=Yes (4918) | Map value labels into illness, care-seeking, forgone-care/no-action, hospitalization, chronic-need, and maternal-care constructs; confirm skip patterns. |
| survey_timing | raw_backed_interview_date_ready | not_final_verified | idate raw bounds=2004-03-08 to 2005-03-31; date interpretation=stata_days_since_1960. | Confirm fieldwork timing against official documentation and decide month-level climate exposure window. |
| climate_geography | raw_backed_admin_ea_geography_ready_not_climate_linkage_accepted | not_final_verified | Household dist+ta+ea distinct combinations=564; EA auxiliary data available; no GPS coordinate field is accepted in this script. | Choose and document CHIRPS or ERA5 linkage route using EA/admin geography; verify boundary crosswalk and exposure aggregation. |
| missing_codes_units_recall_skip_patterns | raw_labels_and_value_profiles_ready_manual_policy_required | not_final_verified | Raw value labels and numeric profiles are available for focused review; labels from sec_d are included in top-value evidence where present. | Finalize missing-code, skip-pattern, recall-period, unit, and construct-level inclusion rules before any analysis-ready promotion. |

## Key And Join Evidence

| evidence_type | left_member | right_member | key_variables | left_distinct_keys | right_distinct_keys | matched_left_distinct_keys | unmatched_left_distinct_keys | evidence_status |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| household_key_uniqueness | ihs2_household.dta |  | case_id | 11280 |  |  |  | unique_at_expected_level |
| expenditure_key_uniqueness | ihs2_exp.dta |  | case_id | 11280 |  |  |  | unique_at_expected_level |
| poverty_consumption_key_uniqueness | ihs2_pov.dta |  | case_id | 11280 |  |  |  | unique_at_expected_level |
| person_key_uniqueness | ihs2_individ.dta |  | case_id;memid | 51288 |  |  |  | unique_at_expected_level |
| health_module_person_key_uniqueness | sec_d.dta |  | case_id;memid | 51292 |  |  |  | unique_at_expected_level |
| household_to_expenditure_join | ihs2_household.dta | ihs2_exp.dta | case_id | 11280 | 11280 | 11280 | 0 | all_left_distinct_keys_matched |
| household_to_poverty_consumption_join | ihs2_household.dta | ihs2_pov.dta | case_id | 11280 | 11280 | 11280 | 0 | all_left_distinct_keys_matched |
| individual_households_to_household_join | ihs2_individ.dta | ihs2_household.dta | case_id | 11280 | 11280 | 11280 | 0 | all_left_distinct_keys_matched |
| health_module_households_to_household_join | sec_d.dta | ihs2_household.dta | case_id | 11280 | 11280 | 11280 | 0 | all_left_distinct_keys_matched |
| health_module_to_individual_join | sec_d.dta | ihs2_individ.dta | case_id;memid | 51292 | 51288 | 51286 | 6 | unmatched_keys_require_review |
| household_admin_ea_to_ea_file_join | ihs2_household.dta | ihs2_ea_data.dta | dist;ta;ea | 564 | 564 | 564 | 0 | all_left_distinct_keys_matched |

## Financial And OOP Profiles

| metric | source_member | variables | nonmissing_count | positive_count | min | median | max | evidence_status |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| total_annual_household_expenditure_real | ihs2_pov.dta | rexpagg | 11280 | 11280 | 6544.07 | 70396.9 | 1.69055e+06 | raw_numeric_profile_available |
| health_oop_annual_household_expenditure_real | ihs2_pov.dta | rexp_cat06 | 11280 | 7765 | 0 | 268.336 | 92343.3 | raw_numeric_profile_available |
| health_oop_real_component_sum | ihs2_exp.dta | rexp_cat061;rexp_cat062;rexp_cat063 | 11280 | 7765 | 0 | 268.336 | 92343.3 | raw_numeric_profile_available |
| poverty_line_local_currency_per_person_year | ihs2_pov.dta | povline | 11280 | 11280 | 16165 | 16165 | 16165 | raw_numeric_profile_available |
| oop_aggregate_matches_real_component_sum | ihs2_pov.dta;ihs2_exp.dta | rexp_cat06;rexp_cat061;rexp_cat062;rexp_cat063 | 11280 | 9596 | 0 | 0 | 0.00294495 | raw_oop_aggregate_component_consistency_profile_available |
| candidate_che_oop_share_of_total_consumption | ihs2_pov.dta | rexp_cat06;rexpagg | 11280 | 7765 | 0 | 0.00381479 | 0.569895 | candidate_che10_che25_share_profile_not_final_indicator |
| individual_health_spend_past_4_weeks_all | sec_d.dta | d12 | 50854 | 2095 | 0 | 0 | 12000 | raw_numeric_profile_available |
| individual_medicine_spend_past_4_weeks_components | sec_d.dta | d13;d14 | 50855 | 13657 | 0 | 0 | 14000 | raw_numeric_profile_available |
| individual_hospitalization_cost_last_12_months | sec_d.dta | d16 | 2036 | 981 | 0 | 0 | 47000 | raw_numeric_profile_available |
| individual_traditional_healer_cost_last_12_months | sec_d.dta | d19 | 418 | 384 | 0 | 250 | 10000 | raw_numeric_profile_available |

## Gate Decision

The correct gate decision remains `not_final_verified`. The next review step is
manual construct acceptance using these raw-backed profiles plus questionnaire
and DDI evidence:

- accept household/person key and module-level exclusions;
- accept survey design variables and weighting policy;
- accept CHE denominator and OOP aggregate definition;
- map illness/care-seeking/no-action labels into a double-failure outcome;
- accept interview-date to climate exposure timing;
- choose a CHIRPS or ERA5 linkage route from EA/admin geography;
- finalize missing-code, skip-pattern, unit, and recall-period rules.
