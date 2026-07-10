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
| final_verified_requirements | 0 | Requirements accepted as final raw-value verified; remains zero. |
| health_person_unmatched_to_roster | 6 | Health-module person keys absent from roster; raw IDs intentionally not exported. |
| oop_component_diff_le_0_01_rows | 11280/11280 | OOP aggregate-component numeric agreement under tolerance. |
| data_write_gate_status | closed | No promoted dataset may be written from this decision artifact. |

## Decisions

| requirement | mechanical_raw_check_decision | final_verification_decision | acceptance_evidence | remaining_blocker | next_action |
| --- | --- | --- | --- | --- | --- |
| household_person_keys | blocked_person_join_exception_review_required | not_final_verified | household/exp/pov case_id joins pass; health->roster unmatched=6; roster->health unmatched=2; exception_status=policy_pending_exception_unresolved. | Resolve or document health-module person keys absent from the roster before full double-failure person-level verification; raw IDs are not exported. | Use the health exception audit to decide whether nonroster health rows can be excluded, reconciled, or documented as valid exceptions. |
| weights_and_design | mechanical_raw_check_pass_documentation_policy_pending | not_final_verified | hhwght positive=11280/11280; strata=30; health psu=564. | Confirm official survey-design guidance and PSU choice across household, poverty, expenditure, and health files. | Record accepted survey design variables and sensitivity plan. |
| consumption_or_income | mechanical_raw_check_pass_sdg_policy_pending | not_final_verified | rexpagg positive=11280/11280; povline and price_index are present. | CHE10/CHE25 denominator is mechanically ready, but SDG 3.8.2 societal poverty-line/discretionary-budget mapping is not accepted. | Write denominator policy for CHE10/CHE25 and separate SDG 3.8.2 capacity-to-pay review. |
| oop_health_expenditure | mechanical_raw_check_pass_construct_policy_pending | not_final_verified | rexp_cat06 nonmissing=11280/11280; component diff<=0.01 rows=11280/11280; max diff=0.00294495. | Accept OOP construct scope and whether survey-team annual aggregate is preferred over health-module recall items. | Document OOP inclusion/exclusion and annual aggregate preference. |
| health_need_and_access | blocked_health_access_label_skip_or_manual_review_required | not_final_verified | d04 illness yes rows=14143; d07 no-money label hits=660; label_decision_rows=127; no_money_rows=660; skip_leakage_rows=6; d07a_leak_overlap_with_nonroster=0; explained_by_nonroster=0; d15/d17/d20/d26 are present. | Health/access label-skip artifact status=label_skip_mapping_has_skip_or_manual_review_blockers; exception_status=policy_pending_exception_unresolved; manual_review_rows=88; d07 skip leakage is not resolved by person-join exceptions unless explained_by_nonroster=1. | Resolve d07a skip leakage as a separate issue from person-key exceptions, classify remaining manual-review care-action labels, and set double-count/formal-care policy. |
| survey_timing | mechanical_raw_check_pass_climate_window_pending | not_final_verified | idate converts to 2004-03-08 through 2005-03-31. | Climate exposure window and aggregation month are not accepted. | Choose interview-month exposure windows for rainfall/heat measures. |
| climate_geography | admin_ea_raw_check_pass_climate_route_pending | not_final_verified | household dist+ta+ea keys=564; matched to EA file=564; no GPS coordinate field accepted. | Accepted CHIRPS/ERA5 route is still missing; admin/EA geography needs boundary/crosswalk and exposure aggregation decision. | Define EA/admin climate linkage route and required boundary/crosswalk source. |
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

The current decision remains fail-closed: `final_verified_requirements=0` and
`data_write_gate_status=closed`. Malawi 2004 has strong financial-protection
raw evidence, but full promotion still requires person-join exception review,
health/access construct mapping, missing/skip/unit/recall policy, and an
accepted CHIRPS or ERA5 climate-linkage route.
