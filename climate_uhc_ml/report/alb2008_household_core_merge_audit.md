# ALB_2008 Household Core Merge Audit

Status: temp-only candidate build. This audit tests whether ALB_2008 raw household/person modules can be merged into a reviewable household core. It does not write `data/harmonized_household.csv`, does not promote a harmonization recipe, and does not construct final outcomes.

## Summary

| Metric | Value | Interpretation |
|---|---:|---|
| alb2008_household_core_candidate_rows | 3599 | Rows in the temp-only household core candidate table. |
| alb2008_household_core_recipe_ready_rows | 0 | This audit never promotes analysis-ready harmonization rows. |
| alb2008_households_with_total_consumption | 3599 | Base households with poverty.sav total consumption. |
| alb2008_households_with_household_weight | 3599 | Base households with candidate household weight. |
| alb2008_households_with_household_size | 3599 | Base households with roster-derived household size. |
| alb2008_households_with_oop_4w_positive | 1895 | Households with positive unreviewed four-week OOP item sum. |
| alb2008_households_with_oop_12m_positive | 1284 | Households with positive unreviewed twelve-month OOP item sum. |
| alb2008_households_with_coarse_area | 3599 | Base households with coarse area code from poverty.sav. |
| alb2008_households_with_survey_month | 0 | No interview month variable has been verified. |
| alb2008_merge_modules_audited | 7 | Raw modules assessed for merge key coverage. |
| alb2008_merge_modules_complete_base_coverage | 7 | Modules whose distinct keys cover all base households. |
| alb2008_merge_modules_partial_base_coverage | 0 | Modules covering only part of the base households. |
| alb2008_household_core_current_decision | temp_candidate_not_analysis_ready | ALB_2008 core candidate is useful for review but remains blocked from data/. |
| alb2008_total_consumption_nonmissing | 3599 | Nonmissing total_consumption rows. |
| alb2008_total_consumption_min | 7543.52 | Observed minimum for total_consumption. |
| alb2008_total_consumption_max | 369641 | Observed maximum for total_consumption. |
| alb2008_total_consumption_mean | 43241.8 | Observed mean for total_consumption. |
| alb2008_household_weight_nonmissing | 3599 | Nonmissing household_weight rows. |
| alb2008_household_weight_min | 24.4286 | Observed minimum for household_weight. |
| alb2008_household_weight_max | 1822.27 | Observed maximum for household_weight. |
| alb2008_household_weight_mean | 204.63 | Observed mean for household_weight. |
| alb2008_household_size_nonmissing | 3599 | Nonmissing household_size rows. |
| alb2008_household_size_min | 1 | Observed minimum for household_size. |
| alb2008_household_size_max | 18 | Observed maximum for household_size. |
| alb2008_household_size_mean | 4.13143 | Observed mean for household_size. |
| alb2008_oop_4w_sum_unreviewed_nonmissing | 3599 | Nonmissing oop_4w_sum_unreviewed rows. |
| alb2008_oop_4w_sum_unreviewed_min | 0 | Observed minimum for oop_4w_sum_unreviewed. |
| alb2008_oop_4w_sum_unreviewed_max | 3860000 | Observed maximum for oop_4w_sum_unreviewed. |
| alb2008_oop_4w_sum_unreviewed_mean | 20862.1 | Observed mean for oop_4w_sum_unreviewed. |
| alb2008_oop_12m_sum_unreviewed_nonmissing | 3599 | Nonmissing oop_12m_sum_unreviewed rows. |
| alb2008_oop_12m_sum_unreviewed_min | 0 | Observed minimum for oop_12m_sum_unreviewed. |
| alb2008_oop_12m_sum_unreviewed_max | 20000000 | Observed maximum for oop_12m_sum_unreviewed. |
| alb2008_oop_12m_sum_unreviewed_mean | 61601.3 | Observed mean for oop_12m_sum_unreviewed. |

## Merge Key Audit

| module | source_file | merge_key | row_count | distinct_key_count | base_rows_matched | base_match_rate | merge_status |
|---|---|---|---|---|---|---|---|
| base_poverty_aggregate | poverty.sav | psu_hh_key | 3599 | 3599 | 3599 | 1.000000 | base_coverage_complete_merge_review_required |
| filters_and_single | filters_and_single.sav | psu_hh_key | 3599 | 3599 | 3599 | 1.000000 | base_coverage_complete_merge_review_required |
| retro_weight_household | Weight_retro_2008.sav | psu_hh_key | 3600 | 3600 | 3599 | 1.000000 | base_coverage_complete_merge_review_required |
| person_roster | Modul_1A_household_roster.sav | psu_hh_key | 14869 | 3599 | 3599 | 1.000000 | base_coverage_complete_merge_review_required |
| person_health_a | Modul_9A_health.sav | psu_hh_key | 14869 | 3599 | 3599 | 1.000000 | base_coverage_complete_merge_review_required |
| household_health_b | Modul_9B_health.sav | psu_hh_key | 3599 | 3599 | 3599 | 1.000000 | base_coverage_complete_merge_review_required |
| shock_module | Modul_6E_migration_e.sav | psu_hh_key | 53985 | 3599 | 3599 | 1.000000 | base_coverage_complete_merge_review_required |

## Candidate Lineage

| candidate_column | source_file | raw_variables | transformation | status | blocking_reason |
|---|---|---|---|---|---|
| total_consumption | poverty.sav | totcons | copy survey aggregate | candidate_unit_period_review_required | unit and period require documentation review |
| household_weight | Weight_retro_2008.sav | Weight_retro | copy household-level retrospective weight by PSU-household key | candidate_design_review_required | survey design use and population require documentation review |
| oop_4w_sum_unreviewed | Modul_9A_health.sav | m9a_q16;m9a_q17;m9a_q20;m9a_q22;m9a_q23;m9a_q28;m9a_q29;m9a_q32;m9a_q34;m9a_q35;m9a_q38;m9a_q39;m9a_q41;m9a... | person-level payment item sum by household | candidate_aggregation_review_required | care-context, skip-pattern, missing-code, gift, transport, and recall comparability require review |
| oop_12m_sum_unreviewed | Modul_9A_health.sav | m9a_q68;m9a_q69;m9a_q71;m9a_q72;m9a_q73;m9a_q76;m9a_q77;m9a_q79;m9a_q80;m9a_q81 | person-level annual payment item sum by household | candidate_aggregation_review_required | annual inpatient/dentist payment items must not be pooled with four-week items without a documented rule |
| area_code;stratum;urban_rural_code | poverty.sav | area;stratum;urbrur | copy coarse survey geography/design fields | blocked_coarse_geography_no_gps | coarse area/stratum fields are not verified admin/GPS climate-linkage geography |
| survey_month;interview_date |  |  | not constructed | blocked_missing_timing | no interview month/date variable has been verified |

## Interpretation

- A temp household core can be assembled for review from the ALB_2008 raw files, with base rows from `poverty.sav`.
- Consumption, weights, roster demographics, health module OOP items, health access proxies, and shock variables have meaningful merge coverage.
- The OOP variables are deliberately named `*_unreviewed`; they mix care contexts and recall periods and are not final outcome variables.
- `area`, `stratum`, and `urbrur` are coarse survey geography/design fields, not verified admin/GPS climate-linkage locations.
- No interview month/date has been verified, so reduced-form climate exposure timing remains blocked.
- The candidate table stays in `temp/`; it is not an analysis-ready `data/` deliverable.

## Machine-Readable Outputs

- `temp/alb2008_household_core_candidate.csv`
- `temp/alb2008_household_core_merge_audit.csv`
- `temp/alb2008_household_core_lineage.csv`
- `result/alb2008_household_core_candidate_summary.csv`
