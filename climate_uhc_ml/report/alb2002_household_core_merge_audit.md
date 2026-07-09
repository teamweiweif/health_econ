# ALB_2002 Household Core Merge Audit

Status: temp-only candidate build. This audit tests whether ALB_2002 raw household/person modules can be merged into a reviewable household core. It does not write `data/harmonized_household.csv`, does not promote a harmonization recipe, and does not construct final outcomes.

## Summary

| Metric | Value | Interpretation |
|---|---:|---|
| alb2002_household_core_candidate_rows | 3599 | Rows in the temp-only household core candidate table. |
| alb2002_household_core_recipe_ready_rows | 0 | This audit never promotes analysis-ready harmonization rows. |
| alb2002_households_with_total_consumption | 3599 | Base households with Poverty_2002.sav total consumption. |
| alb2002_households_with_household_weight | 3599 | Base households with candidate household weight. |
| alb2002_households_with_household_size | 3599 | Base households with roster-derived household size. |
| alb2002_households_with_oop_4w_positive | 2541 | Households with positive unreviewed four-week OOP item sum. |
| alb2002_households_with_oop_12m_positive | 2102 | Households with positive unreviewed twelve-month OOP item sum. |
| alb2002_households_with_district_code | 3599 | Base households with district code from Modul_0_identification.sav. |
| alb2002_households_with_survey_month | 3599 | Base households with raw interview month. |
| alb2002_households_with_interview_date | 3599 | Base households with constructed raw interview date. |
| alb2002_merge_modules_audited | 7 | Raw modules assessed for merge key coverage. |
| alb2002_merge_modules_complete_base_coverage | 7 | Modules whose distinct keys cover all base households. |
| alb2002_merge_modules_partial_base_coverage | 0 | Modules covering only part of the base households. |
| alb2002_household_core_current_decision | temp_candidate_timing_geography_observed_outcome_semantics_pending | ALB_2002 core candidate has observed timing/geography fields but remains blocked from data/. |
| alb2002_total_consumption_nonmissing | 3599 | Nonmissing total_consumption rows. |
| alb2002_total_consumption_min | 2242.84 | Observed minimum for total_consumption. |
| alb2002_total_consumption_max | 277177 | Observed maximum for total_consumption. |
| alb2002_total_consumption_mean | 33722.1 | Observed mean for total_consumption. |
| alb2002_household_weight_nonmissing | 3599 | Nonmissing household_weight rows. |
| alb2002_household_weight_min | 40.885 | Observed minimum for household_weight. |
| alb2002_household_weight_max | 412.2 | Observed maximum for household_weight. |
| alb2002_household_weight_mean | 201.959 | Observed mean for household_weight. |
| alb2002_household_size_nonmissing | 3599 | Nonmissing household_size rows. |
| alb2002_household_size_min | 1 | Observed minimum for household_size. |
| alb2002_household_size_max | 15 | Observed maximum for household_size. |
| alb2002_household_size_mean | 4.59044 | Observed mean for household_size. |
| alb2002_oop_4w_sum_unreviewed_nonmissing | 3599 | Nonmissing oop_4w_sum_unreviewed rows. |
| alb2002_oop_4w_sum_unreviewed_min | 0 | Observed minimum for oop_4w_sum_unreviewed. |
| alb2002_oop_4w_sum_unreviewed_max | 225000 | Observed maximum for oop_4w_sum_unreviewed. |
| alb2002_oop_4w_sum_unreviewed_mean | 1932.27 | Observed mean for oop_4w_sum_unreviewed. |
| alb2002_oop_12m_sum_unreviewed_nonmissing | 3599 | Nonmissing oop_12m_sum_unreviewed rows. |
| alb2002_oop_12m_sum_unreviewed_min | 0 | Observed minimum for oop_12m_sum_unreviewed. |
| alb2002_oop_12m_sum_unreviewed_max | 999997 | Observed maximum for oop_12m_sum_unreviewed. |
| alb2002_oop_12m_sum_unreviewed_mean | 6390.98 | Observed mean for oop_12m_sum_unreviewed. |

## Merge Key Audit

| module | source_file | merge_key | row_count | distinct_key_count | base_rows_matched | base_match_rate | merge_status |
|---|---|---|---|---|---|---|---|
| base_poverty_aggregate | Poverty_2002.sav | psu_hh_key | 3599 | 3599 | 3599 | 1.000000 | base_coverage_complete_merge_review_required |
| household_weights | weights_1.sav | psu_hh_key | 3599 | 3599 | 3599 | 1.000000 | base_coverage_complete_merge_review_required |
| identification_timing_geography | Modul_0_identification.sav | psu_hh_key | 3599 | 3599 | 3599 | 1.000000 | base_coverage_complete_merge_review_required |
| filters_household_screeners | filters.sav | psu_hh_key | 3599 | 3599 | 3599 | 1.000000 | base_coverage_complete_merge_review_required |
| person_roster | Modul_1_hhroster.sav | psu_hh_key | 16521 | 3599 | 3599 | 1.000000 | base_coverage_complete_merge_review_required |
| person_health_a | Modul_5A_Health.sav | psu_hh_key | 16521 | 3599 | 3599 | 1.000000 | base_coverage_complete_merge_review_required |
| household_health_b | Modul_5B_Health.sav | psu_hh_key | 3599 | 3599 | 3599 | 1.000000 | base_coverage_complete_merge_review_required |

## Candidate Lineage

| candidate_column | source_file | raw_variables | transformation | status | blocking_reason |
|---|---|---|---|---|---|
| total_consumption | Poverty_2002.sav | totcons | copy survey aggregate | candidate_unit_period_review_required | unit and period require documentation review |
| household_weight | weights_1.sav | weight | copy household-level weight by PSU-household key | candidate_design_review_required | survey design use and population require documentation review |
| survey_month;interview_date | Modul_0_identification.sav | m0_q08d;m0_q08m;m0_q08y;m0_q08d2;m0_q08m2;m0_q08y2 | construct ISO date from raw interview day/month/year, primary then secondary fallback | candidate_timing_observed_requires_fieldwork_documentation | raw interview date is observed but fieldwork calendar and comparability require documentation review before... |
| district_code_identification;district_name_identification | Modul_0_identification.sav | m0_q1a;m0_q1b | copy district code/name candidate | candidate_admin_geography_requires_crosswalk | district fields need official boundary/crosswalk and no GPS is available |
| oop_4w_sum_unreviewed | Modul_5A_Health.sav | m5a_q14;m5a_q18;m5a_q20;m5a_q21;m5a_q24;m5a_q27;m5a_q28;m5a_q29;m5a_q32;m5a_q35;m5a_q36;m5a_q37;m5a_q40;m5a... | person-level payment item sum by household | candidate_aggregation_review_required | care-context, skip-pattern, missing-code, gift, transport, and recall comparability require review |
| oop_12m_sum_unreviewed | Modul_5A_Health.sav | m5a_q53;m5a_q56;m5a_q57;m5a_q58;m5a_q61;m5a_q64;m5a_q65;m5a_q66 | person-level annual hospital/dentist payment item sum by household | candidate_aggregation_review_required | annual inpatient/dentist payment items must not be pooled with four-week items without a documented rule |
| difficulty_pay_health;delayed_help_any;cost/distance/refusal proxies | Modul_5B_Health.sav | m5b_q01;m5b_q03;m5b_q04;m5b_q05;m5b_q06;m5b_q07;m5b_q08;m5b_q10 | derive household-level unreviewed access and affordability proxies from labelled response codes | candidate_skip_pattern_review_required | access outcomes require skip-pattern and denominator validation before promotion |

## Interpretation

- A temp household core can be assembled for review from the ALB_2002 raw files, with base rows from `Poverty_2002.sav`.
- Consumption, weights, household roster demographics, health module OOP items, health access proxies, district fields, and interview date/month fields have complete base merge coverage.
- The observed interview date/month fields are promising for future climate windows, but fieldwork documentation and cross-wave comparability still require review.
- District fields are candidate admin geography only; no GPS is available and a validated district boundary/crosswalk is still required before climate linkage.
- The OOP variables are deliberately named `*_unreviewed`; they mix care contexts and recall periods and are not final outcome variables.
- The candidate table stays in `temp/`; it is not an analysis-ready `data/` deliverable.

## Machine-Readable Outputs

- `temp/alb2002_household_core_candidate.csv`
- `temp/alb2002_household_core_merge_audit.csv`
- `temp/alb2002_household_core_lineage.csv`
- `result/alb2002_household_core_candidate_summary.csv`
