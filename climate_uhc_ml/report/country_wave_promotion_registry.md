# Country-Wave Promotion Registry

Status: fail-closed promoted registry refreshed to the 19-wave LSMS/ISA
refocused acquisition queue. This is the controlling registry for promoted
multi-country household-climate data writes.

Albania is excluded from the main promoted registry and remains a diagnostic
template only unless its historical boundary, timing, and outcome gates are
resolved.

## Summary

| Metric | Value | Interpretation |
|---|---:|---|
| registry_rows | 19 | Country-waves currently tracked in the promoted registry. |
| refocused_queue_rows | 19 | Refocused LSMS/ISA acquisition queue rows that should be represented in the registry. |
| refocused_registry_coverage_rows | 19 | Refocused queue rows covered by the promoted registry. |
| refocused_missing_from_registry_rows | 0 | Refocused queue rows missing from the promoted registry; must be zero. |
| registry_extra_non_refocused_rows | 0 | Registry rows outside the current refocused LSMS/ISA target; should be zero for this campaign. |
| priority_country_rows | 16 | Rows from Ethiopia, Nigeria, Malawi, Tanzania, and Uganda. |
| refocused_core_country_wave_rows | 10 | Core country-waves in the refocused LSMS/ISA plan. |
| refocused_backup_country_wave_rows | 9 | Backup waves retained for raw-review failure risk and sixth-country coverage. |
| promoted_analysis_ready_rows | 0 | Rows allowed into promoted analysis data. |
| financial_protection_ready_countries | 1 | Countries meeting value-verified CHE financial-protection requirements. |
| double_failure_ready_country_waves | 0 | Country-waves with both financial protection and access/forgone-care ready. |
| accepted_chirps_era5_climate_linkage_rows | 0 | Country-waves with accepted CHIRPS or ERA5 linkage route. |
| raw_package_received_rows | 1 | Registry rows with some non-generated raw package receipt evidence. |
| raw_value_verified_rows | 0 | Registry rows with accepted raw-value verification. |
| gate_pass_rows | 47 | Promotion gate rows passing in the refocused packet matrix. |
| gate_fail_rows | 314 | Promotion gate rows failing in the refocused packet matrix. |
| albania_main_case_rows | 0 | Albania rows in the main refocused promoted registry; should remain zero. |
| promoted_registry_data_write_status | blocked_no_promoted_rows | Data write gate implied by the promoted registry. |
| modeling_gate_status | blocked | Do not run predictive, reduced-form, causal ML, or policy-learning models until registry thresholds pass. |

## Registry Preview

| country | wave | idno | priority_country | raw_package_status | raw_value_verification_status | climate_linkage_ready_status | analysis_ready_status | remaining_blockers |
|---|---|---|---|---|---|---|---|---|
| Ethiopia | 2021-2022 | ETH_2021_ESPS-W5_v02_M | 1 | blocked_no_original_package | blocked_not_raw_value_verified | blocked_timing_geography_or_chirps_era5_route_not_verified | not_promoted | complete original raw package not received; failed_gates=17 (complete_original_raw_package; archive_or_direct_file_pr... |
| Ethiopia | 2018-2019 | ETH_2018_ESS_v04_M | 1 | blocked_no_original_package | blocked_not_raw_value_verified | blocked_timing_geography_or_chirps_era5_route_not_verified | not_promoted | complete original raw package not received; failed_gates=17 (complete_original_raw_package; archive_or_direct_file_pr... |
| Malawi | 2004-2005 | MWI_2004_IHS-II_v01_M | 1 | ready_for_raw_value_review | blocked_not_raw_value_verified | blocked_timing_geography_or_chirps_era5_route_not_verified | not_promoted | failed_gates=8 (raw_value_verification_household_person_keys; raw_value_verification_health_need_and_access; raw_valu... |
| Nigeria | 2012-2013 | NGA_2012_GHSP-W2_v02_M | 1 | blocked_no_original_package | blocked_not_raw_value_verified | blocked_timing_geography_or_chirps_era5_route_not_verified | not_promoted | complete original raw package not received; failed_gates=17 (complete_original_raw_package; archive_or_direct_file_pr... |
| Nigeria | 2015-2016 | NGA_2015_GHSP-W3_v02_M | 1 | blocked_no_original_package | blocked_not_raw_value_verified | blocked_timing_geography_or_chirps_era5_route_not_verified | not_promoted | complete original raw package not received; failed_gates=17 (complete_original_raw_package; archive_or_direct_file_pr... |
| Nigeria | 2010-2011 | NGA_2010_GHSP-W1_v03_M | 1 | blocked_no_original_package | blocked_not_raw_value_verified | blocked_timing_geography_or_chirps_era5_route_not_verified | not_promoted | complete original raw package not received; failed_gates=17 (complete_original_raw_package; archive_or_direct_file_pr... |
| Tanzania | 2008-2009 | TZA_2008_NPS-R1_v03_M | 1 | blocked_no_original_package | blocked_not_raw_value_verified | blocked_timing_geography_or_chirps_era5_route_not_verified | not_promoted | complete original raw package not received; failed_gates=17 (complete_original_raw_package; archive_or_direct_file_pr... |
| Tanzania | 2010-2011 | TZA_2010_NPS-R2_v03_M | 1 | blocked_no_original_package | blocked_not_raw_value_verified | blocked_timing_geography_or_chirps_era5_route_not_verified | not_promoted | complete original raw package not received; failed_gates=17 (complete_original_raw_package; archive_or_direct_file_pr... |
| Tanzania | 2012-2013 | TZA_2012_NPS-R3_v01_M | 1 | blocked_no_original_package | blocked_not_raw_value_verified | blocked_timing_geography_or_chirps_era5_route_not_verified | not_promoted | complete original raw package not received; failed_gates=17 (complete_original_raw_package; archive_or_direct_file_pr... |
| Uganda | 2019-2020 | UGA_2019_UNPS_v03_M | 1 | blocked_no_original_package | blocked_not_raw_value_verified | blocked_timing_geography_or_chirps_era5_route_not_verified | not_promoted | complete original raw package not received; failed_gates=17 (complete_original_raw_package; archive_or_direct_file_pr... |
| Jamaica | 1997 | JAM_1997_SLC_v01_M | 0 | blocked_no_original_package | blocked_not_raw_value_verified | blocked_timing_geography_or_chirps_era5_route_not_verified | not_promoted | complete original raw package not received; failed_gates=17 (complete_original_raw_package; archive_or_direct_file_pr... |
| Kyrgyz Republic | 1993 | KGZ_1993_KMPS_v01_M | 0 | blocked_no_original_package | blocked_not_raw_value_verified | blocked_timing_geography_or_chirps_era5_route_not_verified | not_promoted | complete original raw package not received; failed_gates=17 (complete_original_raw_package; archive_or_direct_file_pr... |
| Nepal | 2010-2011 | NPL_2010_LSS-III_v01_M | 0 | blocked_no_original_package | blocked_not_raw_value_verified | blocked_timing_geography_or_chirps_era5_route_not_verified | not_promoted | complete original raw package not received; failed_gates=17 (complete_original_raw_package; archive_or_direct_file_pr... |
| Malawi | 2019-2020 | MWI_2019_IHS-V_v06_M | 1 | blocked_no_original_package | blocked_not_raw_value_verified | blocked_timing_geography_or_chirps_era5_route_not_verified | not_promoted | complete original raw package not received; failed_gates=17 (complete_original_raw_package; archive_or_direct_file_pr... |
| Malawi | 2016-2017 | MWI_2016_IHS-IV_v04_M | 1 | blocked_no_original_package | blocked_not_raw_value_verified | blocked_timing_geography_or_chirps_era5_route_not_verified | not_promoted | complete original raw package not received; failed_gates=17 (complete_original_raw_package; archive_or_direct_file_pr... |
| Malawi | 2010-2011 | MWI_2010_IHS-III_v01_M | 1 | blocked_no_original_package | blocked_not_raw_value_verified | blocked_timing_geography_or_chirps_era5_route_not_verified | not_promoted | complete original raw package not received; failed_gates=17 (complete_original_raw_package; archive_or_direct_file_pr... |
| Uganda | 2011-2012 | UGA_2011_UNPS_v02_M | 1 | blocked_no_original_package | blocked_not_raw_value_verified | blocked_timing_geography_or_chirps_era5_route_not_verified | not_promoted | complete original raw package not received; failed_gates=17 (complete_original_raw_package; archive_or_direct_file_pr... |
| Uganda | 2018-2019 | UGA_2018_UNPS_v02_M | 1 | blocked_no_original_package | blocked_not_raw_value_verified | blocked_timing_geography_or_chirps_era5_route_not_verified | not_promoted | complete original raw package not received; failed_gates=17 (complete_original_raw_package; archive_or_direct_file_pr... |
| Uganda | 2015-2016 | UGA_2015_UNPS_v02_M | 1 | blocked_no_original_package | blocked_not_raw_value_verified | blocked_timing_geography_or_chirps_era5_route_not_verified | not_promoted | complete original raw package not received; failed_gates=17 (complete_original_raw_package; archive_or_direct_file_pr... |

## Gate Audit Preview

| country | wave | idno | gate | status | required_action |
|---|---|---|---|---|---|
| Ethiopia | 2021-2022 | ETH_2021_ESPS-W5_v02_M | official_public_documentation_receipt | pass |  |
| Ethiopia | 2021-2022 | ETH_2021_ESPS-W5_v02_M | official_variable_evidence_coverage | pass |  |
| Ethiopia | 2021-2022 | ETH_2021_ESPS-W5_v02_M | complete_original_raw_package | fail | Download/place the complete unchanged official raw package and all documentation in the target folder. |
| Ethiopia | 2021-2022 | ETH_2021_ESPS-W5_v02_M | archive_or_direct_file_preflight | fail | Confirm readable archive/direct raw and documentation files before schema inspection. |
| Ethiopia | 2021-2022 | ETH_2021_ESPS-W5_v02_M | raw_value_verification_household_person_keys | fail | Verify this requirement against raw files, value labels, units, recall periods, skip patterns, and merge level. |
| Ethiopia | 2021-2022 | ETH_2021_ESPS-W5_v02_M | raw_value_verification_weights_and_design | fail | Verify this requirement against raw files, value labels, units, recall periods, skip patterns, and merge level. |
| Ethiopia | 2021-2022 | ETH_2021_ESPS-W5_v02_M | raw_value_verification_consumption_or_income | fail | Verify this requirement against raw files, value labels, units, recall periods, skip patterns, and merge level. |
| Ethiopia | 2021-2022 | ETH_2021_ESPS-W5_v02_M | raw_value_verification_oop_health_expenditure | fail | Verify this requirement against raw files, value labels, units, recall periods, skip patterns, and merge level. |
| Ethiopia | 2021-2022 | ETH_2021_ESPS-W5_v02_M | raw_value_verification_health_need_and_access | fail | Verify this requirement against raw files, value labels, units, recall periods, skip patterns, and merge level. |
| Ethiopia | 2021-2022 | ETH_2021_ESPS-W5_v02_M | raw_value_verification_survey_timing | fail | Verify this requirement against raw files, value labels, units, recall periods, skip patterns, and merge level. |
| Ethiopia | 2021-2022 | ETH_2021_ESPS-W5_v02_M | raw_value_verification_climate_geography | fail | Verify this requirement against raw files, value labels, units, recall periods, skip patterns, and merge level. |
| Ethiopia | 2021-2022 | ETH_2021_ESPS-W5_v02_M | raw_value_verification_missing_codes_units_recall_skip_patterns | fail | Verify this requirement against raw files, value labels, units, recall periods, skip patterns, and merge level. |
| Ethiopia | 2021-2022 | ETH_2021_ESPS-W5_v02_M | all_required_raw_values_verified | fail | Complete raw-backed verification for every required promotion requirement. |
| Ethiopia | 2021-2022 | ETH_2021_ESPS-W5_v02_M | financial_protection_inputs_ready | fail | Verify financial-protection inputs before CHE10/CHE25 or SDG 3.8.2 readiness can be claimed. |
| Ethiopia | 2021-2022 | ETH_2021_ESPS-W5_v02_M | access_forgone_care_inputs_ready | fail | Verify illness/need and care-seeking/access variables before double-failure readiness can be claimed. |
| Ethiopia | 2021-2022 | ETH_2021_ESPS-W5_v02_M | timing_geography_ready_for_climate | fail | Verify timing and geography raw fields before accepting a climate linkage route. |
| Ethiopia | 2021-2022 | ETH_2021_ESPS-W5_v02_M | accepted_chirps_or_era5_linkage_route | fail | Accept a CHIRPS or ERA5 route only after timing/geography verification passes. |
| Ethiopia | 2021-2022 | ETH_2021_ESPS-W5_v02_M | analysis_dataset_synthesis_ready | fail | Complete promoted household-climate schema and join review. |
| Ethiopia | 2021-2022 | ETH_2021_ESPS-W5_v02_M | promoted_registry_write_gate | fail | Write to data/ only when the promoted registry marks this country-wave as analysis-ready with nonzero rows. |
| Ethiopia | 2018-2019 | ETH_2018_ESS_v04_M | official_public_documentation_receipt | pass |  |
| Ethiopia | 2018-2019 | ETH_2018_ESS_v04_M | official_variable_evidence_coverage | pass |  |
| Ethiopia | 2018-2019 | ETH_2018_ESS_v04_M | complete_original_raw_package | fail | Download/place the complete unchanged official raw package and all documentation in the target folder. |
| Ethiopia | 2018-2019 | ETH_2018_ESS_v04_M | archive_or_direct_file_preflight | fail | Confirm readable archive/direct raw and documentation files before schema inspection. |
| Ethiopia | 2018-2019 | ETH_2018_ESS_v04_M | raw_value_verification_household_person_keys | fail | Verify this requirement against raw files, value labels, units, recall periods, skip patterns, and merge level. |
| Ethiopia | 2018-2019 | ETH_2018_ESS_v04_M | raw_value_verification_weights_and_design | fail | Verify this requirement against raw files, value labels, units, recall periods, skip patterns, and merge level. |
| Ethiopia | 2018-2019 | ETH_2018_ESS_v04_M | raw_value_verification_consumption_or_income | fail | Verify this requirement against raw files, value labels, units, recall periods, skip patterns, and merge level. |
| Ethiopia | 2018-2019 | ETH_2018_ESS_v04_M | raw_value_verification_oop_health_expenditure | fail | Verify this requirement against raw files, value labels, units, recall periods, skip patterns, and merge level. |
| Ethiopia | 2018-2019 | ETH_2018_ESS_v04_M | raw_value_verification_health_need_and_access | fail | Verify this requirement against raw files, value labels, units, recall periods, skip patterns, and merge level. |
| Ethiopia | 2018-2019 | ETH_2018_ESS_v04_M | raw_value_verification_survey_timing | fail | Verify this requirement against raw files, value labels, units, recall periods, skip patterns, and merge level. |
| Ethiopia | 2018-2019 | ETH_2018_ESS_v04_M | raw_value_verification_climate_geography | fail | Verify this requirement against raw files, value labels, units, recall periods, skip patterns, and merge level. |
| Ethiopia | 2018-2019 | ETH_2018_ESS_v04_M | raw_value_verification_missing_codes_units_recall_skip_patterns | fail | Verify this requirement against raw files, value labels, units, recall periods, skip patterns, and merge level. |
| Ethiopia | 2018-2019 | ETH_2018_ESS_v04_M | all_required_raw_values_verified | fail | Complete raw-backed verification for every required promotion requirement. |
| Ethiopia | 2018-2019 | ETH_2018_ESS_v04_M | financial_protection_inputs_ready | fail | Verify financial-protection inputs before CHE10/CHE25 or SDG 3.8.2 readiness can be claimed. |
| Ethiopia | 2018-2019 | ETH_2018_ESS_v04_M | access_forgone_care_inputs_ready | fail | Verify illness/need and care-seeking/access variables before double-failure readiness can be claimed. |
| Ethiopia | 2018-2019 | ETH_2018_ESS_v04_M | timing_geography_ready_for_climate | fail | Verify timing and geography raw fields before accepting a climate linkage route. |
| Ethiopia | 2018-2019 | ETH_2018_ESS_v04_M | accepted_chirps_or_era5_linkage_route | fail | Accept a CHIRPS or ERA5 route only after timing/geography verification passes. |
| Ethiopia | 2018-2019 | ETH_2018_ESS_v04_M | analysis_dataset_synthesis_ready | fail | Complete promoted household-climate schema and join review. |
| Ethiopia | 2018-2019 | ETH_2018_ESS_v04_M | promoted_registry_write_gate | fail | Write to data/ only when the promoted registry marks this country-wave as analysis-ready with nonzero rows. |
| Malawi | 2004-2005 | MWI_2004_IHS-II_v01_M | official_public_documentation_receipt | pass |  |
| Malawi | 2004-2005 | MWI_2004_IHS-II_v01_M | official_variable_evidence_coverage | pass |  |

## Machine-Readable Outputs

- `result/promoted_country_wave_registry.csv`
- `result/country_wave_promotion_gate_audit.csv`
- `result/country_wave_promotion_summary.csv`
- `result/priority_country_wave_download_queue.csv`

## Stop Rules

- No row may write to `data/` until `analysis_ready_status` is `promoted_analysis_ready`.
- Modeling remains blocked until the registry contains at least 6 value-verified financial-protection countries, 10 value-verified double-failure country-waves, and at least one accepted CHIRPS or ERA5 linkage route.
