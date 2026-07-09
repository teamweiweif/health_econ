# Priority Analysis Dataset Synthesis Blueprint

Status: fail-closed promoted-dataset synthesis blueprint. This defines the
target household x climate schema and join plan, but does not write `data/`.

## Summary

| Metric | Value | Interpretation |
|---|---:|---|
| priority_synthesis_blueprint_schema_rows | 572 | Target output-column rows for priority analysis dataset synthesis. |
| priority_synthesis_blueprint_required_rows | 325 | Required output columns across priority and backup waves. |
| priority_synthesis_blueprint_ready_required_rows | 0 | Required output columns ready for synthesis review. |
| priority_synthesis_blueprint_blocked_required_rows | 325 | Required output columns still blocked. |
| priority_synthesis_blueprint_join_plan_rows | 13 | Dataset-level join plans. |
| priority_synthesis_blueprint_join_ready_rows | 0 | Dataset-level join plans ready for promoted dataset build. |
| priority_synthesis_blueprint_candidate_variable_rows | 2703 | Metadata candidate variable rows connected to target output columns. |
| priority_synthesis_blueprint_manual_verified_variable_rows | 0 | Candidate variable rows passing manual verification. |
| priority_synthesis_blueprint_handoff_readmes_written | 13 | Per-wave synthesis blueprint handoffs written. |
| modeling_gate_status | blocked | Models remain blocked until promoted registry thresholds and accepted CHIRPS/ERA5 linkage pass. |
| priority_synthesis_status_blocked_raw_package_absent | 533 | Output-column synthesis status count. |
| priority_synthesis_status_metadata_ready_not_sufficient_for_promotion | 39 | Output-column synthesis status count. |
| priority_synthesis_join_status_blocked_required_schema_columns_not_verified | 13 | Dataset-level join status count. |

## Join Plans

| acquisition_batch_rank | idno | country | wave | required_schema_columns | synthesis_ready_columns | blocked_columns | join_plan_status |
|---|---|---|---|---|---|---|---|
| 1 | ETH_2021_ESPS-W5_v02_M | Ethiopia | 2021-2022 | 25 | 0 | 22 | blocked_required_schema_columns_not_verified |
| 2 | ETH_2018_ESS_v04_M | Ethiopia | 2018-2019 | 25 | 0 | 22 | blocked_required_schema_columns_not_verified |
| 3 | MWI_2007-2009_MTM_v01_M | Malawi | 2007-2009 | 25 | 0 | 22 | blocked_required_schema_columns_not_verified |
| 4 | NGA_2012_GHSP-W2_v02_M | Nigeria | 2012-2013 | 25 | 0 | 22 | blocked_required_schema_columns_not_verified |
| 5 | NGA_2015_GHSP-W3_v02_M | Nigeria | 2015-2016 | 25 | 0 | 22 | blocked_required_schema_columns_not_verified |
| 6 | NGA_2010_GHSP-W1_v03_M | Nigeria | 2010-2011 | 25 | 0 | 22 | blocked_required_schema_columns_not_verified |
| 7 | TZA_2008_NPS-R1_v03_M | Tanzania | 2008-2009 | 25 | 0 | 22 | blocked_required_schema_columns_not_verified |
| 8 | TZA_2010_NPS-R2_v03_M | Tanzania | 2010-2011 | 25 | 0 | 22 | blocked_required_schema_columns_not_verified |
| 9 | TZA_2012_NPS-R3_v01_M | Tanzania | 2012-2013 | 25 | 0 | 22 | blocked_required_schema_columns_not_verified |
| 10 | UGA_2014_SAGE-EL_v01_M | Uganda | 2014 | 25 | 0 | 22 | blocked_required_schema_columns_not_verified |
| 11 | JAM_1997_SLC_v01_M | Jamaica | 1997 | 25 | 0 | 22 | blocked_required_schema_columns_not_verified |
| 12 | KGZ_1993_KMPS_v01_M | Kyrgyz Republic | 1993 | 25 | 0 | 22 | blocked_required_schema_columns_not_verified |
| 13 | NPL_2010_LSS-III_v01_M | Nepal | 2010-2011 | 25 | 0 | 22 | blocked_required_schema_columns_not_verified |

## Required Schema Examples

| idno | promoted_dataset_layer | output_column | source_concepts | candidate_variable_rows | manual_verified_variable_rows | current_synthesis_status |
|---|---|---|---|---|---|---|
| ETH_2021_ESPS-W5_v02_M | household_core | country | metadata | 0 | 0 | metadata_ready_not_sufficient_for_promotion |
| ETH_2021_ESPS-W5_v02_M | household_core | wave | metadata | 0 | 0 | metadata_ready_not_sufficient_for_promotion |
| ETH_2021_ESPS-W5_v02_M | household_core | idno | metadata | 0 | 0 | metadata_ready_not_sufficient_for_promotion |
| ETH_2021_ESPS-W5_v02_M | household_core | household_id | household_id | 2 | 0 | blocked_raw_package_absent |
| ETH_2021_ESPS-W5_v02_M | survey_design | survey_weight | survey_weight | 5 | 0 | blocked_raw_package_absent |
| ETH_2021_ESPS-W5_v02_M | survey_design | psu_cluster | psu_cluster | 4 | 0 | blocked_raw_package_absent |
| ETH_2021_ESPS-W5_v02_M | timing | survey_year | survey_timing | 0 | 0 | blocked_raw_package_absent |
| ETH_2021_ESPS-W5_v02_M | timing | survey_month | survey_timing | 0 | 0 | blocked_raw_package_absent |
| ETH_2021_ESPS-W5_v02_M | climate_geography | cluster_id | climate_geography | 0 | 0 | blocked_raw_package_absent |
| ETH_2021_ESPS-W5_v02_M | climate_geography | geolocation_quality | climate_geography | 0 | 0 | blocked_raw_package_absent |
| ETH_2021_ESPS-W5_v02_M | financial_inputs | total_consumption | total_consumption_or_income | 0 | 0 | blocked_raw_package_absent |
| ETH_2021_ESPS-W5_v02_M | financial_inputs | oop_health_expenditure | oop_health_expenditure | 16 | 0 | blocked_raw_package_absent |
| ETH_2021_ESPS-W5_v02_M | financial_outcomes | che10 | oop_health_expenditure;total_consumption_or_income | 18 | 0 | blocked_raw_package_absent |
| ETH_2021_ESPS-W5_v02_M | financial_outcomes | che25 | oop_health_expenditure;total_consumption_or_income | 18 | 0 | blocked_raw_package_absent |
| ETH_2021_ESPS-W5_v02_M | financial_outcomes | sdg382_indicator | oop_health_expenditure;total_consumption_or_income | 18 | 0 | blocked_raw_package_absent |
| ETH_2021_ESPS-W5_v02_M | access_inputs | illness_or_injury_need | health_need | 9 | 0 | blocked_raw_package_absent |
| ETH_2021_ESPS-W5_v02_M | access_inputs | care_sought | care_or_barrier | 11 | 0 | blocked_raw_package_absent |
| ETH_2021_ESPS-W5_v02_M | access_outcomes | forgone_care_access_failure | health_need;care_or_barrier | 23 | 0 | blocked_raw_package_absent |
| ETH_2021_ESPS-W5_v02_M | access_outcomes | double_failure_indicator | oop_health_expenditure;total_consumption_or_income;health_need;care_or_barrier | 41 | 0 | blocked_raw_package_absent |
| ETH_2021_ESPS-W5_v02_M | climate_linked | climate_source | survey_timing;climate_geography | 17 | 0 | blocked_raw_package_absent |
| ETH_2021_ESPS-W5_v02_M | climate_linked | climate_window_start | survey_timing | 1 | 0 | blocked_raw_package_absent |
| ETH_2021_ESPS-W5_v02_M | climate_linked | climate_window_end | survey_timing | 1 | 0 | blocked_raw_package_absent |
| ETH_2021_ESPS-W5_v02_M | climate_linked | chirps_precip_anomaly | survey_timing;climate_geography | 17 | 0 | blocked_raw_package_absent |
| ETH_2021_ESPS-W5_v02_M | climate_linked | era5_heat_anomaly | survey_timing;climate_geography | 17 | 0 | blocked_raw_package_absent |
| ETH_2021_ESPS-W5_v02_M | climate_linked | climate_shock_indicator | survey_timing;climate_geography | 17 | 0 | blocked_raw_package_absent |
| ETH_2018_ESS_v04_M | household_core | country | metadata | 0 | 0 | metadata_ready_not_sufficient_for_promotion |
| ETH_2018_ESS_v04_M | household_core | wave | metadata | 0 | 0 | metadata_ready_not_sufficient_for_promotion |
| ETH_2018_ESS_v04_M | household_core | idno | metadata | 0 | 0 | metadata_ready_not_sufficient_for_promotion |
| ETH_2018_ESS_v04_M | household_core | household_id | household_id | 2 | 0 | blocked_raw_package_absent |
| ETH_2018_ESS_v04_M | survey_design | survey_weight | survey_weight | 6 | 0 | blocked_raw_package_absent |

## Rule

A country-wave may be written to `data/` only after every required schema
column has raw package receipt, source variable verification, manual
value/unit/key review, outcome readiness, and accepted CHIRPS/ERA5 climate
linkage. Metadata-only candidates remain blocked.

## Machine-Readable Outputs

- `temp/priority_analysis_dataset_synthesis_blueprint.csv`
- `temp/priority_analysis_dataset_join_plan.csv`
- `result/priority_analysis_dataset_synthesis_blueprint_summary.csv`
