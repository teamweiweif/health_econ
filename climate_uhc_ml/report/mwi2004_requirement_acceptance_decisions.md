# Malawi 2004 Requirement Acceptance Decisions

Dataset: `MWI_2004_IHS-II_v01_M` - Malawi 2004-2005

This file converts the focused raw-backed evidence into requirement-level
accept/block decisions. It does not export raw person IDs, does not write to
`data/`, and does not mark the country-wave as value-verified.

## Summary

| metric | value | interpretation |
| --- | --- | --- |
| country_wave | MWI_2004_IHS-II_v01_M | Country-wave adjudicated in this focused acceptance decision. |
| decision_rows | 8 | Requirement-level acceptance decision rows. |
| mechanical_raw_checks_pass_or_partial | 5 | Requirements with raw mechanical evidence that passes but still needs policy/documentation acceptance. |
| hard_blocked_requirements | 3 | Requirements still blocked even before final climate/data promotion. |
| final_verified_requirements | 5 | Requirements accepted as final raw-value verified for their stated scope. |
| health_person_unmatched_to_roster | 6 | Health-module person keys absent from roster; raw IDs intentionally not exported. |
| oop_component_diff_le_0_01_rows | 11280/11280 | OOP aggregate-component numeric agreement under tolerance. |
| financial_policy_status | che10_che25_financial_inputs_verified_sdg382_blocked | CHE10/CHE25 financial input policy status. |
| che10_che25_financial_inputs_ready | 1 | Whether financial-protection inputs are raw-value verified for CHE10/CHE25. |
| sdg382_ready | 0 | Whether SDG 3.8.2 discretionary-budget inputs are ready; remains zero. |
| che10_candidate_rows | 208 | Candidate CHE10 rows from the accepted financial input policy. |
| che25_candidate_rows | 17 | Candidate CHE25 rows from the accepted financial input policy. |
| timing_geography_policy_status | raw_timing_admin_ea_geography_verified_climate_route_blocked | Timing/geography raw-value policy status. |
| survey_timing_final_verified | 1 | Whether survey timing is raw-value verified for climate-window anchoring. |
| climate_geography_final_verified | 1 | Whether admin/EA geography is raw-value verified for route review. |
| timing_geography_ready_for_climate | 1 | Whether raw timing and geography are ready for climate-route review. |
| accepted_chirps_era5_route | 0 | Whether a CHIRPS/ERA5 route is accepted; remains zero. |
| health_access_construction_policy_status | candidate_policy_ready_active_skip_and_provider_blockers | Candidate health/access construction policy status; still not final verification. |
| health_access_policy_acute_need_denominator_rows | 14143 | Roster-matched d04==Yes rows under the candidate access denominator. |
| health_access_policy_no_money_rows | 631 | Candidate no-money forgone-care rows counted once per person row. |
| ... | ... | ... |

## Decisions

| requirement | mechanical_raw_check_decision | final_verification_decision | acceptance_evidence | remaining_blocker | next_action |
| --- | --- | --- | --- | --- | --- |
| household_person_keys | blocked_person_join_exception_review_required | not_final_verified | household/exp/pov case_id joins pass; health->roster unmatched=6; roster->health unmatched=2; exception_status=policy_pending_exception_unresolved. | Resolve or document health-module person keys absent from the roster before full double-failure person-level verification; raw IDs are not exported. | Use the health exception audit to decide whether nonroster health rows can be excluded, reconciled, or documented as valid exceptions. |
| weights_and_design | raw_value_verified_financial_policy_accepted | raw_value_verified_for_che10_che25 | hhwght positive=11280/11280; strata=30; health psu=564; household_financial_rows=11280; financial_policy_status=che10_che25_financial_inputs_verified_sdg382_blocked. | Household financial survey design is accepted for CHE10/CHE25; recheck person-level design and cross-country modeling design before access, double-failure, or ML use. | Keep household financial design fixed for CHE10/CHE25; verify person-level/access design separately before double-failure promotion. |
| consumption_or_income | raw_value_verified_che_denominator_sdg_policy_blocked | raw_value_verified_for_che10_che25 | rexpagg positive=11280/11280; povline and price_index are present; household_financial_rows=11280; che10_rows=208; che25_rows=17; sdg382_ready=0. | rexpagg is accepted as CHE10/CHE25 total-budget denominator; SDG 3.8.2 societal poverty-line/discretionary-budget mapping remains blocked. | Resolve SDG 3.8.2 discretionary-budget policy separately; do not use SDG status for promotion yet. |
| oop_health_expenditure | raw_value_verified_oop_aggregate_policy_accepted | raw_value_verified_for_che10_che25 | rexp_cat06 nonmissing=11280/11280; component diff<=0.01 rows=11280/11280; max diff=0.00294495; financial_policy_status=che10_che25_financial_inputs_verified_sdg382_blocked. | rexp_cat06 is accepted as annual household health OOP aggregate for CHE10/CHE25; health-module recall spending remains context only. | Keep rexp_cat06 as the CHE OOP input; do not substitute person-level health-module recall sums for household CHE. |
| health_need_and_access | blocked_health_access_policy_ready_active_exceptions | not_final_verified | d04 illness yes rows=14143; d07 no-money label hits=660; label_decision_rows=127; no_money_rows=660; policy_denominator=14143; policy_no_money_rows=631; formal_core=5130; formal_extended=5593; skip_leakage_rows=6; policy_skip_exceptions=6; d07a_leak_overlap_with_nonroster=0; explained_by_nonroster=0; d15/d17/d20/d26 are present. | Health/access construction policy status=candidate_policy_ready_active_skip_and_provider_blockers; final_health_access_verified=0; label-skip status=label_skip_mapping_has_skip_or_manual_review_blockers; exception_status=policy_pending_exception_unresolved; manual_review_rows=88; d07 skip leakage is not resolved by person-join exceptions unless explained_by_nonroster=1. | Review the candidate construction policy, then resolve d07a skip leakage, classify remaining manual-review care-action labels, and accept double-count/formal-care/provider-grouping rules. |
| survey_timing | raw_value_verified_interview_month_policy_accepted | raw_value_verified_for_climate_timing | idate converts to 2004-03-08 through 2005-03-31; policy_dates=2004-03-08 through 2005-03-31; interview_month_count=13; timing_geography_status=raw_timing_admin_ea_geography_verified_climate_route_blocked. | Interview-month timing is accepted for climate-window review; climate values still require an accepted CHIRPS/ERA5 route. | Use interview-month anchors when defining CHIRPS/ERA5 exposure windows; do not run extraction until geography route is accepted. |
| climate_geography | raw_value_verified_admin_ea_geography_route_blocked | raw_value_verified_for_admin_ea_geography | household dist+ta+ea keys=564; matched to EA file=564; policy_household_ea_match=564/564; no GPS coordinate field accepted; accepted_chirps_era5_route=0. | Raw admin/EA geography is accepted, but CHIRPS/ERA5 route remains blocked until boundary/crosswalk and aggregation policy are documented. | Define the boundary/crosswalk and exposure aggregation route for CHIRPS/ERA5 without treating EA/admin fields as coordinates. |
| missing_codes_units_recall_skip_patterns | blocked_manual_policy_required | not_final_verified | Raw value labels and profiles exist, but construct-level missing/skip/unit/recall rules are not finalized. | Missing-code, skip-pattern, recall-period, and unit policy must be accepted before any data write. | Write variable-level policy table and rerun requirement acceptance. |

## Metrics

| metric | value | status | interpretation |
| --- | --- | --- | --- |
| household_case_id_distinct | 11280 | pass | Distinct household case_id keys in ihs2_household.dta. |
| exp_case_id_unmatched_to_household | 0 | pass | Expenditure case_id keys absent from household file. |
| pov_case_id_unmatched_to_household | 0 | pass | Poverty/consumption case_id keys absent from household file. |
| health_person_keys_unmatched_to_roster | 6 | blocker | Health module case_id+memid keys absent from individual roster; raw IDs are intentionally not exported. |
| roster_person_keys_unmatched_to_health | 2 | review | Individual roster case_id+memid keys absent from health module; raw IDs are intentionally not exported. |
| household_hhwght_positive_rows | 11280/11280 | pass | Positive household weight coverage. |
| household_strata_distinct | 30 | pass | Distinct household strata values. |
| health_psu_distinct | 564 | pass | Distinct health-module PSU values. |
| household_ea_keys_matched_to_ea_file | 564 | pass | Household dist+ta+ea keys matched to EA auxiliary file. |
| household_interview_date_min | 2004-03-08 | pass | Earliest raw household interview date from idate. |
| household_interview_date_max | 2005-03-31 | pass | Latest raw household interview date from idate. |
| rexpagg_positive_rows | 11280/11280 | pass | Positive total annual household expenditure rows. |
| rexp_cat06_nonmissing_rows | 11280/11280 | pass | Nonmissing annual household health expenditure aggregate rows. |
| oop_aggregate_component_max_abs_diff | 0.00294495 | pass | Max absolute difference between rexp_cat06 and the sum of real health components. |
| oop_aggregate_component_diff_le_0_01_rows | 11280/11280 | pass | Rows whose OOP aggregate-component difference is within 0.01 local currency units. |
| candidate_che10_rows | 208 | diagnostic_not_final | Candidate CHE10 count from rexp_cat06/rexpagg; not final indicator. |
| candidate_che25_rows | 17 | diagnostic_not_final | Candidate CHE25 count from rexp_cat06/rexpagg; not final indicator. |
| illness_injury_past_2_weeks_yes_rows | 14143 | pass | Rows with d04 illness/injury yes. |
| care_action_no_money_label_hits | 660 | review | Rows where d07a/d07b labels indicate no-money non-care action; requires skip and double-count review. |

## Gate Decision

The current decision remains fail-closed: `final_verified_requirements=5`
and `data_write_gate_status=closed`. Malawi 2004 now has CHE10/CHE25
financial-protection inputs accepted where the financial construction policy
supports them, but full promotion still requires person-join exception review,
health/access construct mapping, missing/skip/unit/recall policy, SDG 3.8.2
denominator policy, and an accepted CHIRPS or ERA5 climate-linkage route.
