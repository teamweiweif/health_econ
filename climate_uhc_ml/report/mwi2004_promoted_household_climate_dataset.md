# Malawi 2004 Promoted Household-Climate Dataset

Dataset: `MWI_2004_IHS-II_v01_M` - Malawi 2004-2005

This artifact synthesizes the first controlled household-level analysis dataset
for the climate-UHC workspace. It joins verified CHE10/CHE25 financial inputs,
verified cost-barrier forgone-care access inputs, and validated CHIRPS ADM2
rainfall lag windows.

It does not construct SDG 3.8.2 and does not open predictive ML, reduced-form,
causal ML, or policy-learning gates.

## Summary

| metric | value | interpretation |
| --- | --- | --- |
| country_wave | MWI_2004_IHS-II_v01_M | Country-wave covered by this promoted household-climate synthesis. |
| analysis_ready_status | promoted_analysis_ready | Promotion status after household financial/access/climate synthesis validation. |
| promoted_rows | 11280 | Household rows in the promoted analysis-ready dataset. |
| data_path | data/mwi2004_household_climate_analysis.csv | Local promoted dataset path; raw/household-level data may remain local for publication control. |
| data_sha256 | bef48328a2953c1400edd0deaf27d01bf95da2ab50bdf303e06aa138cddd3d45 | SHA-256 of the local promoted household-climate dataset. |
| data_bytes | 3155221 | Size of the local promoted household-climate dataset. |
| financial_rows | 11280 | Rows from the verified financial-protection household universe. |
| che10_rows | 208 | Households with CHE10 total-budget financial hardship. |
| che25_rows | 17 | Households with CHE25 total-budget financial hardship. |
| sdg382_ready | 0 | SDG 3.8.2 remains blocked by discretionary-budget/societal-poverty-line policy. |
| health_person_rows_matched | 51286 | Roster-matched health-module person rows aggregated to households. |
| acute_need_persons | 14143 | Roster-matched acute need persons in promoted households. |
| cost_barrier_forgone_care_persons | 631 | Acute-need persons with no-money forgone care. |
| households_any_acute_need | 7749 | Households with at least one acute-need person. |
| households_any_cost_barrier_forgone_care | 519 | Households with at least one cost-barrier forgone-care person. |
| uhc_failure_che10_or_cost_barrier_rows | 721 | Households with CHE10 or cost-barrier forgone care. |
| uhc_failure_che25_or_cost_barrier_rows | 534 | Households with CHE25 or cost-barrier forgone care. |
| both_che10_and_cost_barrier_rows | 6 | Households with both CHE10 and cost-barrier forgone care. |
| both_che25_and_cost_barrier_rows | 2 | Households with both CHE25 and cost-barrier forgone care. |
| climate_exposure_complete_rows | 11280 | Household rows with complete CHIRPS 1/3/6/12 month exposure windows. |
| adm2_districts_linked | 26 | Matched ADM2 districts represented in the promoted household dataset. |
| validation_pass_rows | 12 | Promotion validation checks passing. |
| validation_fail_rows | 0 | Promotion validation checks failing. |
| upstream_financial_che10_che25_ready | 1 | Financial input gate consumed by this synthesis. |
| upstream_access_cost_barrier_ready | 1 | Access input gate consumed by this synthesis. |
| upstream_missing_units_recall_skip_ready | 1 | Missing/unit/recall/skip gate consumed by this synthesis. |
| upstream_climate_chirps_admin2_ready | 1 | CHIRPS ADM2 extraction gate consumed by this synthesis. |
| data_write_gate_status | open_promoted_dataset_written | Controlled data/ write gate outcome for this synthesis. |
| modeling_gate_status | blocked | No predictive ML, reduced-form, causal ML, or policy learning is opened by one promoted country-wave. |

## Validation

| validation_component | status | evidence | required_action |
| --- | --- | --- | --- |
| upstream_financial_gate | pass | che10_che25_financial_inputs_ready=1 |  |
| upstream_access_gate | pass | access_forgone_care_inputs_ready=1 |  |
| upstream_missing_units_gate | pass | missing_units_recall_skip_policy_final_verified=1 |  |
| upstream_climate_gate | pass | accepted_chirps_era5_route=1 |  |
| row_count_matches_financial_universe | pass | rows=11280; expected_financial_rows=11280 |  |
| case_id_unique | pass | unique_case_ids=11280; rows=11280 |  |
| financial_outcomes_complete | pass | che10_rows=208; che25_rows=17 |  |
| access_household_aggregation_complete | pass | matched_persons=51286; acute_need_persons=14143; cost_barrier_persons=631 |  |
| climate_lag_windows_complete | pass | household_rows=11280; complete_climate_rows=11280 |  |
| admin2_crosswalk_complete | pass | mapped_adm2_rows=11280; rows=11280 |  |
| data_file_written | pass | path=data\mwi2004_household_climate_analysis.csv; exists=1; bytes=3155221 |  |
| dictionary_written | pass | path=result\mwi2004_promoted_household_climate_dataset_dictionary.csv; exists=1 |  |

## Dictionary Preview

| column_name | source | definition |
| --- | --- | --- |
| country | constant | Country name. |
| wave | constant | Survey wave/year label. |
| idno | constant | World Bank Microdata Library study identifier. |
| case_id | ihs2_pov.dta/ihs2_household.dta/sec_d.dta | Household identifier used for promoted household-level joins. |
| household_weight | ihs2_pov.dta hhwght | Household survey weight. |
| strata | ihs2_pov.dta strata | Survey stratum code. |
| psu | ihs2_household.dta V51 | Household EA/PSU code accepted for this household-level dataset. |
| raw_dist_code | ihs2_pov.dta dist | Raw district code in the Malawi 2004 microdata. |
| raw_dist_label | ihs2_household.dta dist label | Raw district value label from the household file. |
| adm2_name | mwi2004_chirps_admin2_crosswalk.csv | Matched Malawi ADM2 boundary name used for CHIRPS aggregation. |
| ta | ihs2_pov.dta ta | Traditional authority code. |
| ea | ihs2_pov.dta ea | Enumeration area code. |
| interview_date | ihs2_household.dta idate | Interview date converted from Stata days since 1960-01-01. |
| interview_month | ihs2_household.dta idate | Interview month used as the lag-window anchor. |
| total_consumption_rexpagg | ihs2_pov.dta rexpagg | Survey-team total annual household expenditure denominator for CHE10/CHE25. |
| oop_health_rexp_cat06 | ihs2_pov.dta rexp_cat06 | Annual real household health OOP expenditure aggregate. |
| oop_health_share_total | constructed | oop_health_rexp_cat06 divided by total_consumption_rexpagg. |
| che10_total_budget | constructed | Indicator for OOP health share of total consumption greater than 10 percent. |
| che25_total_budget | constructed | Indicator for OOP health share of total consumption greater than 25 percent. |
| sdg382_ready | policy flag | Always 0 in this release; SDG 3.8.2 discretionary-budget denominator remains blocked. |
| ... | ... | ... |

## Publication Control

The local data file is written to `data/mwi2004_household_climate_analysis.csv`.
For repository publication, prefer the script, dictionary, validation, summary,
and this report unless household-level derived microdata redistribution is
explicitly approved.
