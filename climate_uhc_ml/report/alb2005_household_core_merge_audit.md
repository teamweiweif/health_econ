# ALB_2005 Household Core Merge Audit

Status: temp-only candidate build. This audit tests whether ALB_2005 raw household/person modules can be merged into a reviewable household core. It does not write `data/harmonized_household.csv`, does not promote a harmonization recipe, and does not construct final outcomes.

## Summary

| Metric | Value | Interpretation |
|---|---:|---|
| alb2005_household_core_candidate_rows | 3840 | Rows in the temp-only household core candidate table. |
| alb2005_household_core_recipe_ready_rows | 0 | This audit never promotes analysis-ready harmonization rows. |
| alb2005_households_with_total_consumption | 3638 | Base households with poverty.sav total consumption merged. |
| alb2005_households_with_household_weight | 3840 | Base households with candidate household weight from poverty or PSU weight file. |
| alb2005_households_with_household_size | 3840 | Base households with roster-derived household size. |
| alb2005_households_with_oop_4w_positive | 2679 | Households with positive unreviewed four-week OOP item sum. |
| alb2005_households_with_oop_12m_positive | 2231 | Households with positive unreviewed twelve-month OOP item sum. |
| alb2005_households_with_partial_district_code | 329 | Base households with district code from filters.sav. |
| alb2005_households_with_survey_month | 0 | No interview month variable has been verified. |
| alb2005_merge_modules_audited | 8 | Raw modules assessed for merge key coverage. |
| alb2005_merge_modules_complete_base_coverage | 6 | Modules whose distinct keys cover all base households. |
| alb2005_merge_modules_partial_base_coverage | 2 | Modules covering only part of the base households. |
| alb2005_household_core_current_decision | temp_candidate_not_analysis_ready | ALB_2005 core candidate is useful for review but remains blocked from data/. |
| alb2005_total_consumption_nonmissing | 3638 | Nonmissing total_consumption rows. |
| alb2005_total_consumption_min | 42062 | Observed minimum for total_consumption. |
| alb2005_total_consumption_max | 5.45599e+06 | Observed maximum for total_consumption. |
| alb2005_total_consumption_mean | 421269 | Observed mean for total_consumption. |
| alb2005_household_weight_nonmissing | 3840 | Nonmissing household_weight rows. |
| alb2005_household_weight_min | 19.5547 | Observed minimum for household_weight. |
| alb2005_household_weight_max | 574.427 | Observed maximum for household_weight. |
| alb2005_household_weight_mean | 192.84 | Observed mean for household_weight. |
| alb2005_household_size_nonmissing | 3840 | Nonmissing household_size rows. |
| alb2005_household_size_min | 1 | Observed minimum for household_size. |
| alb2005_household_size_max | 16 | Observed maximum for household_size. |
| alb2005_household_size_mean | 4.50573 | Observed mean for household_size. |
| alb2005_oop_4w_sum_unreviewed_nonmissing | 3840 | Nonmissing oop_4w_sum_unreviewed rows. |
| alb2005_oop_4w_sum_unreviewed_min | 0 | Observed minimum for oop_4w_sum_unreviewed. |
| alb2005_oop_4w_sum_unreviewed_max | 1011000 | Observed maximum for oop_4w_sum_unreviewed. |
| alb2005_oop_4w_sum_unreviewed_mean | 18250.8 | Observed mean for oop_4w_sum_unreviewed. |
| alb2005_oop_12m_sum_unreviewed_nonmissing | 3840 | Nonmissing oop_12m_sum_unreviewed rows. |
| alb2005_oop_12m_sum_unreviewed_min | 0 | Observed minimum for oop_12m_sum_unreviewed. |
| alb2005_oop_12m_sum_unreviewed_max | 10600000 | Observed maximum for oop_12m_sum_unreviewed. |
| alb2005_oop_12m_sum_unreviewed_mean | 91644.7 | Observed mean for oop_12m_sum_unreviewed. |

## Merge Key Audit

| module | source_file | merge_key | row_count | distinct_key_count | base_rows_matched | base_match_rate | merge_status |
|---|---|---|---|---|---|---|---|
| base_filters_cl | filters_cl.sav | hhid_key | 3840 | 3840 | 3840 | 1.000000 | base_coverage_complete_merge_review_required |
| poverty_aggregate | poverty.sav | psu_hh_key | 3638 | 3638 | 3638 | 0.947396 | partial_base_coverage_review_required |
| retro_weight_by_psu | Weight_retro_2005.sav | psu_key | 480 | 480 | 480 | 1.000000 | base_coverage_complete_merge_review_required |
| person_roster | Modul_1A_household_rostera_cl.sav | hhid_key | 17302 | 3840 | 3840 | 1.000000 | base_coverage_complete_merge_review_required |
| person_health_a | Modul_9A_healtha_cl.sav | hhid_key | 17302 | 3840 | 3840 | 1.000000 | base_coverage_complete_merge_review_required |
| household_health_b | Modul_9B_healthb_cl.sav | hhid_key | 3840 | 3840 | 3840 | 1.000000 | base_coverage_complete_merge_review_required |
| filters_geography | filters.sav | psu_hh_key | 1899 | 1899 | 1899 | 0.494531 | partial_base_coverage_review_required |
| shock_module | Modul_6E_migratione_cl.sav | hhid_key | 57600 | 3840 | 3840 | 1.000000 | base_coverage_complete_merge_review_required |

## Candidate Lineage

| candidate_column | source_file | raw_variables | transformation | status | blocking_reason |
|---|---|---|---|---|---|
| total_consumption | poverty.sav | totcons | copy survey aggregate | candidate_unit_period_review_required | unit and period require documentation review |
| household_weight | poverty.sav;Weight_retro_2005.sav | weight_retro | poverty weight with PSU-file fallback | candidate_design_review_required | survey design use and population require documentation review |
| oop_4w_sum_unreviewed | Modul_9A_healtha_cl.sav | m9a_q16;m9a_q17;m9a_q20;m9a_q22;m9a_q23;m9a_q28;m9a_q29;m9a_q32;m9a_q34;m9a_q35;m9a_q38;m9a_q39;m9a_q41;m9a... | person-level payment item sum by household | candidate_aggregation_review_required | care-context, skip-pattern, missing-code, gift, transport, and recall comparability require review |
| oop_12m_sum_unreviewed | Modul_9A_healtha_cl.sav | m9a_q68;m9a_q69;m9a_q71;m9a_q72;m9a_q73;m9a_q76;m9a_q77;m9a_q79;m9a_q80;m9a_q81 | person-level annual payment item sum by household | candidate_aggregation_review_required | annual inpatient/dentist payment items must not be pooled with four-week items without a documented rule |
| district_code_partial | filters.sav | P11_Q5B | merge by PSU and household ID | blocked_partial_geography | district code covers only a subset of base households and no GPS is available |
| survey_month;interview_date |  |  | not constructed | blocked_missing_timing | no interview month/date variable has been verified |

## Interpretation

- A temp household core can be assembled for review from the ALB_2005 raw files, with base rows from `filters_cl.sav`.
- Consumption, roster demographics, health module OOP items, and health access proxies have meaningful merge coverage.
- The OOP variables are deliberately named `*_unreviewed`; they mix care contexts and recall periods and are not final outcome variables.
- District code coverage is partial and no GPS variables are available, so climate linkage remains blocked.
- No interview month/date has been verified, so reduced-form climate exposure timing remains blocked.
- The candidate table stays in `temp/`; it is not an analysis-ready `data/` deliverable.

## Machine-Readable Outputs

- `temp/alb2005_household_core_candidate.csv`
- `temp/alb2005_household_core_merge_audit.csv`
- `temp/alb2005_household_core_lineage.csv`
- `result/alb2005_household_core_candidate_summary.csv`
