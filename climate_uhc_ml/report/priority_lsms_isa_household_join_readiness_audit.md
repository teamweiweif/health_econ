# Priority LSMS-ISA Household Join Readiness Audit

Status: raw-backed household join audit for received priority LSMS/ISA
packages with configured join paths. This is a
promotion-control artifact; it does not write to `data/` and does not mark any
requirement as value-verified.

## Summary

| Metric | Value | Interpretation |
|---|---:|---|
| priority_lsms_household_join_dataset_rows | 5 | Received raw country-waves included in household join readiness audit. |
| priority_lsms_household_join_file_audit_rows | 23 | Core component files audited for household keys and required variables. |
| priority_lsms_household_join_pair_audit_rows | 23 | Base-to-component household join coverage rows. |
| priority_lsms_household_join_complete_join_path_rows | 5 | Country-waves with all required modules join-ready at household level. |
| priority_lsms_household_join_raw_value_verified_rows | 0 | Focused requirements already accepted as raw-value verified; should remain zero until reviewer acceptance. |
| priority_lsms_household_join_data_write_status | blocked_join_audit_only | Household join readiness audit does not write promoted data. |
| modeling_gate_status | blocked | Models remain blocked until promoted registry thresholds and accepted climate linkage pass. |
| priority_lsms_household_join_component_status_household_level_component_ready_for_join_audit | 18 | Core file component status count. |
| priority_lsms_household_join_component_status_person_or_item_level_component_ready_for_household_aggregation_review | 5 | Core file component status count. |
| priority_lsms_household_join_pair_status_join_ready_ge95_base_coverage | 23 | Household join pair status count. |

## Wave Readiness

| idno | best_base_file | base_households | complete_household_join_path_ready | focused_raw_value_verified_rows | household_join_readiness_status |
|---|---|---|---|---|---|
| NGA_2015_GHSP-W3_v02_M | cons_agg_wave3_visit1.dta | 4590 | 1 | 0 | household_join_path_ready_value_verification_and_climate_blocked |
| TZA_2010_NPS-R2_v03_M | TZY2.HH.Consumption.dta | 3846 | 1 | 0 | household_join_path_ready_value_verification_and_climate_blocked |
| TZA_2012_NPS-R3_v01_M | ConsumptionNPS3.dta | 4883 | 1 | 0 | household_join_path_ready_value_verification_and_climate_blocked |
| MWI_2016_IHS-IV_v04_M | IHS4 Consumption Aggregate.dta | 12447 | 1 | 0 | household_join_path_ready_value_verification_and_climate_blocked |
| MWI_2010_IHS-III_v01_M | Panel/Round 1 (2010) Consumption Aggregate.dta | 3246 | 1 | 0 | household_join_path_ready_value_verification_and_climate_blocked |

## Core File Audit

| idno | component | file_name | row_count | distinct_households | required_variables_missing | component_status |
|---|---|---|---|---|---|---|
| NGA_2015_GHSP-W3_v02_M | consumption_visit1 | cons_agg_wave3_visit1.dta | 4590 | 4590 |  | household_level_component_ready_for_join_audit |
| NGA_2015_GHSP-W3_v02_M | consumption_visit2 | cons_agg_wave3_visit2.dta | 4579 | 4579 |  | household_level_component_ready_for_join_audit |
| NGA_2015_GHSP-W3_v02_M | health_access_oop | sect4a_harvestw3.dta | 26176 | 4582 |  | person_or_item_level_component_ready_for_household_aggregation_review |
| NGA_2015_GHSP-W3_v02_M | survey_timing | secta_harvestw3.dta | 4592 | 4592 |  | household_level_component_ready_for_join_audit |
| NGA_2015_GHSP-W3_v02_M | climate_geography | NGA_HouseholdGeovars_Y3.dta | 4613 | 4613 |  | household_level_component_ready_for_join_audit |
| NGA_2015_GHSP-W3_v02_M | panel_weights | HHTrack.dta | 5000 | 5000 |  | household_level_component_ready_for_join_audit |
| TZA_2010_NPS-R2_v03_M | consumption_aggregate | TZY2.HH.Consumption.dta | 3846 | 3846 |  | household_level_component_ready_for_join_audit |
| TZA_2010_NPS-R2_v03_M | household_header_timing_design | HH_SEC_A.dta | 3924 | 3924 |  | household_level_component_ready_for_join_audit |
| TZA_2010_NPS-R2_v03_M | health_access_oop | HH_SEC_D.dta | 20562 | 3924 |  | person_or_item_level_component_ready_for_household_aggregation_review |
| TZA_2010_NPS-R2_v03_M | climate_geography | HH.Geovariables_Y2.dta | 3917 | 3917 |  | household_level_component_ready_for_join_audit |
| TZA_2012_NPS-R3_v01_M | consumption_aggregate | ConsumptionNPS3.dta | 4883 | 4883 |  | household_level_component_ready_for_join_audit |
| TZA_2012_NPS-R3_v01_M | household_header_timing_design | HH_SEC_A.dta | 5010 | 5010 |  | household_level_component_ready_for_join_audit |
| TZA_2012_NPS-R3_v01_M | health_access_oop | HH_SEC_D.dta | 25412 | 5010 |  | person_or_item_level_component_ready_for_household_aggregation_review |
| TZA_2012_NPS-R3_v01_M | climate_geography | HouseholdGeovars_Y3.dta | 4988 | 4988 |  | household_level_component_ready_for_join_audit |
| TZA_2012_NPS-R3_v01_M | panel_weights | Y3_weights.dta | 5010 | 5010 |  | household_level_component_ready_for_join_audit |
| MWI_2016_IHS-IV_v04_M | consumption_aggregate | IHS4 Consumption Aggregate.dta | 12447 | 12447 |  | household_level_component_ready_for_join_audit |
| MWI_2016_IHS-IV_v04_M | household_header_timing_design | HH_MOD_A_FILT.dta | 12447 | 12447 |  | household_level_component_ready_for_join_audit |
| MWI_2016_IHS-IV_v04_M | health_access_oop | HH_MOD_D.dta | 53885 | 12447 |  | person_or_item_level_component_ready_for_household_aggregation_review |
| MWI_2016_IHS-IV_v04_M | climate_geography | HouseholdGeovariables_stata11/HouseholdGeovariablesIHS4.dta | 12447 | 12447 |  | household_level_component_ready_for_join_audit |
| MWI_2010_IHS-III_v01_M | consumption_aggregate | Panel/Round 1 (2010) Consumption Aggregate.dta | 3246 | 3246 |  | household_level_component_ready_for_join_audit |

## Join Coverage Preview

| idno | base_file | component_file | matched_households | base_coverage_rate | pair_status |
|---|---|---|---|---|---|
| MWI_2010_IHS-III_v01_M | Panel/Round 1 (2010) Consumption Aggregate.dta | Panel/Household/hh_mod_a_filt.dta | 3246 | 1.000000 | join_ready_ge95_base_coverage |
| MWI_2010_IHS-III_v01_M | Panel/Round 1 (2010) Consumption Aggregate.dta | Panel/Household/hh_mod_d.dta | 3246 | 1.000000 | join_ready_ge95_base_coverage |
| MWI_2010_IHS-III_v01_M | Panel/Round 1 (2010) Consumption Aggregate.dta | Panel/Geovariables/householdgeovariables_ihs3_rerelease.dta | 3246 | 1.000000 | join_ready_ge95_base_coverage |
| MWI_2016_IHS-IV_v04_M | IHS4 Consumption Aggregate.dta | HH_MOD_A_FILT.dta | 12447 | 1.000000 | join_ready_ge95_base_coverage |
| MWI_2016_IHS-IV_v04_M | IHS4 Consumption Aggregate.dta | HH_MOD_D.dta | 12447 | 1.000000 | join_ready_ge95_base_coverage |
| MWI_2016_IHS-IV_v04_M | IHS4 Consumption Aggregate.dta | HouseholdGeovariables_stata11/HouseholdGeovariablesIHS4.dta | 12447 | 1.000000 | join_ready_ge95_base_coverage |
| NGA_2015_GHSP-W3_v02_M | cons_agg_wave3_visit1.dta | cons_agg_wave3_visit2.dta | 4559 | 0.993246 | join_ready_ge95_base_coverage |
| NGA_2015_GHSP-W3_v02_M | cons_agg_wave3_visit1.dta | sect4a_harvestw3.dta | 4560 | 0.993464 | join_ready_ge95_base_coverage |
| NGA_2015_GHSP-W3_v02_M | cons_agg_wave3_visit1.dta | secta_harvestw3.dta | 4571 | 0.995861 | join_ready_ge95_base_coverage |
| NGA_2015_GHSP-W3_v02_M | cons_agg_wave3_visit1.dta | NGA_HouseholdGeovars_Y3.dta | 4590 | 1.000000 | join_ready_ge95_base_coverage |
| NGA_2015_GHSP-W3_v02_M | cons_agg_wave3_visit1.dta | HHTrack.dta | 4590 | 1.000000 | join_ready_ge95_base_coverage |
| NGA_2015_GHSP-W3_v02_M | cons_agg_wave3_visit2.dta | cons_agg_wave3_visit1.dta | 4559 | 0.995632 | join_ready_ge95_base_coverage |
| NGA_2015_GHSP-W3_v02_M | cons_agg_wave3_visit2.dta | sect4a_harvestw3.dta | 4579 | 1.000000 | join_ready_ge95_base_coverage |
| NGA_2015_GHSP-W3_v02_M | cons_agg_wave3_visit2.dta | secta_harvestw3.dta | 4579 | 1.000000 | join_ready_ge95_base_coverage |
| NGA_2015_GHSP-W3_v02_M | cons_agg_wave3_visit2.dta | NGA_HouseholdGeovars_Y3.dta | 4579 | 1.000000 | join_ready_ge95_base_coverage |
| NGA_2015_GHSP-W3_v02_M | cons_agg_wave3_visit2.dta | HHTrack.dta | 4579 | 1.000000 | join_ready_ge95_base_coverage |
| TZA_2010_NPS-R2_v03_M | TZY2.HH.Consumption.dta | HH_SEC_A.dta | 3846 | 1.000000 | join_ready_ge95_base_coverage |
| TZA_2010_NPS-R2_v03_M | TZY2.HH.Consumption.dta | HH_SEC_D.dta | 3846 | 1.000000 | join_ready_ge95_base_coverage |
| TZA_2010_NPS-R2_v03_M | TZY2.HH.Consumption.dta | HH.Geovariables_Y2.dta | 3839 | 0.998180 | join_ready_ge95_base_coverage |
| TZA_2012_NPS-R3_v01_M | ConsumptionNPS3.dta | HH_SEC_A.dta | 4883 | 1.000000 | join_ready_ge95_base_coverage |

## Stop Rule

Even when the household join path is ready, country-waves remain blocked from
promotion until reviewer acceptance verifies raw values, value labels, units,
recall periods, missing codes, skip patterns, merge levels, and an accepted
CHIRPS or ERA5 climate linkage route.
