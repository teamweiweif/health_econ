# ALB_2012 Raw Core Feasibility Audit

Status: temp-only raw feasibility audit. This audit reads locally extracted ALB_2012 SPSS files, checks household merge coverage for core modules, and creates a review candidate in `temp/`. It does not write `data/harmonized_household.csv`, does not create final outcomes, and does not create climate-linkage inputs.

## Summary

| Metric | Value | Interpretation |
|---|---:|---|
| alb2012_household_core_candidate_rows | 6671 | Rows in the ALB_2012 temp-only household core candidate. |
| alb2012_household_core_recipe_ready_rows | 0 | Rows ready for harmonization recipe promotion after this audit. |
| alb2012_climate_linkage_ready_rows | 0 | Rows ready for climate-linkage input promotion after this audit. |
| alb2012_households_with_total_consumption | 6671 | Households with survey-team total consumption aggregate. |
| alb2012_households_with_household_weight | 6671 | Households with retro household weight candidate. |
| alb2012_households_with_prefecture | 6671 | Households with coarse prefecture field. |
| alb2012_households_with_region | 6671 | Households with coarse region field. |
| alb2012_households_with_survey_month | 0 | Households with raw interview month; none identified. |
| alb2012_households_with_interview_date | 0 | Households with raw interview date; none identified. |
| alb2012_households_with_oop_4w_positive | 2794 | Households with positive unreviewed four-week OOP item sum. |
| alb2012_households_with_oop_12m_positive | 2093 | Households with positive unreviewed twelve-month OOP item sum. |
| alb2012_households_with_access_affordability_proxy | 2750 | Households with difficulty paying health care proxy. |
| alb2012_households_with_shock_any_2008_2012 | 1306 | Households with any unreviewed shock-module positive signal. |
| alb2012_raw_core_audit_rows | 10 | Rows in the ALB_2012 raw core feasibility audit. |
| alb2012_merge_modules_complete_base_coverage | 6 | Merge-audit rows with complete base household key coverage. |
| alb2012_timing_signal_rows | 0 | Raw interview timing rows identified for climate windows. |
| alb2012_coordinate_signal_rows | 0 | Raw coordinate/GPS rows identified for climate linkage. |
| alb2012_raw_core_current_decision | temp_candidate_no_interview_timing_coarse_geography_outcome_semantics_pending | Current fail-closed decision for ALB_2012 raw core feasibility. |

## Audit Rows

| audit_domain | audit_item | source_file | row_count | distinct_key_count | base_rows_matched | audit_status |
|---|---|---|---|---|---|---|
| merge_key | base_consumption_poverty | poverty.sav | 6671 | 6671 | 6671 | base_coverage_complete_merge_review_required |
| merge_key | household_weight_retro | Weight_lsms2012_retro.sav | 6671 | 6671 | 6671 | base_coverage_complete_merge_review_required |
| merge_key | household_roster | Modul_1A_householdroster.sav | 25335 | 6671 | 6671 | base_coverage_complete_merge_review_required |
| merge_key | person_health_oop_need | modul_9A_health.sav | 25335 | 6671 | 6671 | base_coverage_complete_merge_review_required |
| merge_key | household_access_to_health | Modul_9B_Access_to_Health_Care.sav | 6671 | 6671 | 6671 | base_coverage_complete_merge_review_required |
| merge_key | household_shock_module | Modul_6D_Shocks to the household.sav | 60054 | 6671 | 6671 | base_coverage_complete_merge_review_required |
| value_timing_geography | interview_timing | all_2012_sav_files |  |  |  | blocked_no_interview_month_or_date_signal |
| value_timing_geography | current_geography | poverty.sav |  |  |  | blocked_coarse_prefecture_region_only_no_gps |
| value_timing_geography | gps_coordinates | all_2012_sav_files |  |  |  | blocked_no_coordinate_signal |
| value_timing_geography | oop_access_value_semantics | modul_9A_health.sav;Modul_9B_Access_to_Health_Care.sav |  |  |  | blocked_units_recall_skip_patterns_unreviewed |

## Candidate Lineage

| candidate_column | source_file | raw_variables | transformation | status | blocking_reason |
|---|---|---|---|---|---|
| hhid;psu;hh;total_consumption;real_consumption;food/nonfood utility components | poverty.sav | hhid;psu;hh;totcons;rcons;rfood;rtotnfood;rtotutil | household-level base frame and survey-team consumption aggregates | candidate_value_review_required | consumption units and cross-wave comparability require review before harmonization |
| household_weight | Weight_lsms2012_retro.sav | pesha10tetor | merge retro household weight on psu-hh key | candidate_design_review_required | weight meaning, scaling, and survey design variables require documentation review |
| prefecture;region;urban_rural_code | poverty.sav | prefecture;region;urban | carry coarse current geography fields from poverty file | candidate_geography_blocked | coarse geography only; no GPS/admin2 and no interview timing for climate linkage |
| household_size;children/elderly/head demographics | Modul_1A_householdroster.sav | idcode;m1a_q02;m1a_q03;m1a_q05y | aggregate roster age and head fields by household | candidate_value_review_required | roster member universe and head coding require review |
| oop_4w_sum_unreviewed;oop_12m_sum_unreviewed;need/license proxies | modul_9A_health.sav | M9A_Q18;M9A_Q19;M9A_Q22;M9A_Q24;M9A_Q25;M9A_Q30;M9A_Q31;M9A_Q34;M9A_Q36;M9A_Q37;M9A_Q40;M9A_Q41;M9A_Q43;M9A... | person-level OOP payment item sums and need/license proxies by household | candidate_aggregation_review_required | OOP items mix care contexts and recall periods; units, missing codes, and aggregation require review |
| difficulty/access/coping proxies | Modul_9B_Access_to_Health_Care.sav | psu;hh;M9B_Q01;Q02_A;Q02_B;Q02_C;Q02_D;Q02_E;M9B_Q03;M9B_Q04;M9B_Q05;M9B_Q06;M9B_Q07;M9B_Q08;M9B_Q10 | derive household-level unreviewed affordability, access, refusal, and coping proxies | candidate_skip_pattern_review_required | access outcomes require skip-pattern, reason-code, and denominator validation |
| shock_any_2008_2012 | Modul_6D_Shocks to the household.sav | psu;hh;M6D_Q00;M6D_Q01;M6D_2008;M6D_2009;M6D_2010;M6D_2011;M6D_2012 | derive any-shock diagnostic across reported 2008-2012 shock columns | candidate_mechanism_review_required | shock type semantics and timing are not climate exposure variables |

## Interpretation

- ALB_2012 has a reviewable household base with total consumption, retro weights, roster demographics, health OOP/access proxies, and shock-module signals.
- The base frame has 6,671 household rows from `poverty.sav`.
- This is not a harmonized dataset: OOP units, recall periods, missing codes, skip patterns, survey design semantics, and access denominators are not verified.
- Climate linkage remains blocked because no raw interview month/date or GPS/coordinate field is identified, and current geography is coarse prefecture/region/urban only.
- All outputs stay in `temp/`, `result/`, and `report/`; `data/` remains untouched.

## Machine-Readable Outputs

- `temp/alb2012_household_core_candidate.csv`
- `temp/alb2012_raw_core_feasibility_audit.csv`
- `temp/alb2012_raw_core_lineage.csv`
- `result/alb2012_raw_core_feasibility_summary.csv`
