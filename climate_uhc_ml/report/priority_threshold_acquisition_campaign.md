# Priority Threshold Acquisition Campaign

Status: acquisition campaign for the promoted dataset thresholds. This file
maps the current 13 priority/backup waves to the actual modeling guardrails:
10 value-verified country-waves for double failure, 6 value-verified countries
for financial protection, and at least one accepted CHIRPS/ERA5 linkage route.

## Summary

| Metric | Value | Interpretation |
|---|---:|---|
| priority_threshold_campaign_dataset_rows | 13 | Priority and backup country-waves in the threshold acquisition campaign. |
| priority_threshold_campaign_phase1_10_wave_rows | 10 | Core campaign rows needed for the 10 country-wave double-failure threshold. |
| priority_threshold_campaign_phase2_sixth_country_backup_rows | 3 | Backup rows kept to reach a sixth financial-protection country. |
| priority_threshold_campaign_distinct_countries | 8 | Distinct countries represented in the campaign. |
| priority_threshold_campaign_core_country_rows | 5 | Core countries represented by the first 10 waves. |
| priority_threshold_campaign_backup_country_rows | 3 | Backup countries available as sixth-country candidates. |
| priority_threshold_campaign_core_wave_rows | 10 | Wave rows in the core five-country base. |
| priority_threshold_campaign_backup_wave_rows | 3 | Wave rows in the sixth-country backup set. |
| priority_threshold_campaign_minimum_download_rows_for_formal_thresholds | 11 | Ten phase-1 waves plus at least one backup-country wave are the minimum raw downloads if every selected wave verifies. |
| priority_threshold_campaign_recommended_download_rows | 13 | Recommended downloads include all three backup countries to reduce sixth-country failure risk. |
| priority_threshold_campaign_current_promoted_analysis_ready_rows | 0 | Campaign rows currently promoted analysis-ready. |
| priority_threshold_campaign_raw_package_received_rows | 0 | Campaign rows with any original raw/package receipt. |
| priority_threshold_campaign_raw_package_missing_rows | 13 | Campaign rows still missing original raw/package receipt. |
| priority_threshold_campaign_core_file_endpoint_ready_rows | 13 | Campaign rows with core-file endpoint probes confirming public routes do not expose accepted raw payloads. |
| priority_threshold_campaign_handoff_readmes_written | 13 | Per-wave threshold acquisition handoffs written. |
| modeling_gate_status | blocked | Models remain blocked until 6 countries, 10 country-waves, and accepted CHIRPS/ERA5 linkage are value-verified. |

## Country Coverage

| country | country_role | planned_country_wave_rows | phase1_10_wave_rows | phase2_backup_rows | raw_package_received_rows | promoted_analysis_ready_rows | threshold_contribution |
|---|---|---|---|---|---|---|---|
| Ethiopia | core_five_country_base | 2 | 2 | 0 | 0 | 0 | core_5_country_base_for_10_wave_double_failure_threshold |
| Malawi | core_five_country_base | 1 | 1 | 0 | 0 | 0 | core_5_country_base_for_10_wave_double_failure_threshold |
| Nigeria | core_five_country_base | 3 | 3 | 0 | 0 | 0 | core_5_country_base_for_10_wave_double_failure_threshold |
| Tanzania | core_five_country_base | 3 | 3 | 0 | 0 | 0 | core_5_country_base_for_10_wave_double_failure_threshold |
| Uganda | core_five_country_base | 1 | 1 | 0 | 0 | 0 | core_5_country_base_for_10_wave_double_failure_threshold |
| Jamaica | sixth_country_backup_option | 1 | 0 | 1 | 0 | 0 | backup_option_for_6th_financial_protection_country |
| Kyrgyz Republic | sixth_country_backup_option | 1 | 0 | 1 | 0 | 0 | backup_option_for_6th_financial_protection_country |
| Nepal | sixth_country_backup_option | 1 | 0 | 1 | 0 | 0 | backup_option_for_6th_financial_protection_country |

## Campaign Queue

| acquisition_batch_rank | campaign_phase | country | wave | idno | raw_receipt_status | core_file_endpoint_matrix_status | promoted_registry_status |
|---|---|---|---|---|---|---|---|
| 1 | phase_1_double_failure_10_wave_base | Ethiopia | 2021-2022 | ETH_2021_ESPS-W5_v02_M | not_received_no_original_raw_package | core_file_routes_confirmed_non_public_raw | not_promoted |
| 2 | phase_1_double_failure_10_wave_base | Ethiopia | 2018-2019 | ETH_2018_ESS_v04_M | not_received_no_original_raw_package | core_file_routes_confirmed_non_public_raw | not_promoted |
| 3 | phase_1_double_failure_10_wave_base | Malawi | 2007-2009 | MWI_2007-2009_MTM_v01_M | not_received_no_original_raw_package | core_file_routes_confirmed_non_public_raw | not_promoted |
| 4 | phase_1_double_failure_10_wave_base | Nigeria | 2012-2013 | NGA_2012_GHSP-W2_v02_M | not_received_no_original_raw_package | core_file_routes_confirmed_non_public_raw | not_promoted |
| 5 | phase_1_double_failure_10_wave_base | Nigeria | 2015-2016 | NGA_2015_GHSP-W3_v02_M | not_received_no_original_raw_package | core_file_routes_confirmed_non_public_raw | not_promoted |
| 6 | phase_1_double_failure_10_wave_base | Nigeria | 2010-2011 | NGA_2010_GHSP-W1_v03_M | not_received_no_original_raw_package | core_file_routes_confirmed_non_public_raw | not_promoted |
| 7 | phase_1_double_failure_10_wave_base | Tanzania | 2008-2009 | TZA_2008_NPS-R1_v03_M | not_received_no_original_raw_package | core_file_routes_confirmed_non_public_raw | not_promoted |
| 8 | phase_1_double_failure_10_wave_base | Tanzania | 2010-2011 | TZA_2010_NPS-R2_v03_M | not_received_no_original_raw_package | core_file_routes_confirmed_non_public_raw | not_promoted |
| 9 | phase_1_double_failure_10_wave_base | Tanzania | 2012-2013 | TZA_2012_NPS-R3_v01_M | not_received_no_original_raw_package | core_file_routes_confirmed_non_public_raw | not_promoted |
| 10 | phase_1_double_failure_10_wave_base | Uganda | 2014 | UGA_2014_SAGE-EL_v01_M | not_received_no_original_raw_package | core_file_routes_confirmed_non_public_raw | not_promoted |
| 11 | phase_2_sixth_country_financial_protection_backup | Jamaica | 1997 | JAM_1997_SLC_v01_M | not_received_no_original_raw_package | core_file_routes_confirmed_non_public_raw | not_promoted |
| 12 | phase_2_sixth_country_financial_protection_backup | Kyrgyz Republic | 1993 | KGZ_1993_KMPS_v01_M | not_received_no_original_raw_package | core_file_routes_confirmed_non_public_raw | not_promoted |
| 13 | phase_2_sixth_country_financial_protection_backup | Nepal | 2010-2011 | NPL_2010_LSS-III_v01_M | not_received_no_original_raw_package | core_file_routes_confirmed_non_public_raw | not_promoted |

## Operational Rule

The first 10 waves are the base campaign for the 10 country-wave double-failure
threshold, but they represent only five countries. At least one backup-country
wave must pass financial-protection value verification to reach the sixth
country threshold. All three backup countries remain in the campaign because
any one backup may fail outcome, geography, timing, or climate-linkage checks
after raw receipt.

## Machine-Readable Outputs

- `temp/priority_threshold_acquisition_campaign.csv`
- `temp/priority_threshold_country_coverage.csv`
- `result/priority_threshold_acquisition_campaign_summary.csv`
