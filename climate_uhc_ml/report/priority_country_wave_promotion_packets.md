# Priority Country-Wave Promotion Packets

Status: fail-closed packet layer for the priority dataset-promotion batch. This
is the packet handoff for moving from metadata-only candidates toward verified
analysis-ready household x climate datasets. It does not write data into
`data/`.

## Summary

| Metric | Value | Interpretation |
|---|---:|---|
| priority_country_wave_packet_rows | 13 | Priority and backup country-wave promotion packets built. |
| priority_country_wave_packet_priority_batch_rows | 10 | Immediate priority wave packets. |
| priority_country_wave_packet_backup_rows | 3 | Sixth-country backup wave packets. |
| priority_country_wave_packet_gate_rows | 169 | Gate rows across priority promotion packets. |
| priority_country_wave_packet_passed_gate_rows | 39 | Packet gates currently passing. |
| priority_country_wave_packet_failed_gate_rows | 130 | Packet gates still blocking promotion. |
| priority_country_wave_packet_public_documentation_ready_rows | 13 | Packets with complete core public documentation receipt. |
| priority_country_wave_packet_official_metadata_ready_rows | 13 | Packets with official DDI/XML variable evidence extracted. |
| priority_country_wave_packet_credentialed_acquisition_ready_rows | 13 | Packets with credentialed raw-package acquisition ledger prepared. |
| priority_country_wave_packet_raw_package_ready_rows | 0 | Packets with a non-empty original raw package receipt. |
| priority_country_wave_packet_financial_ready_rows | 0 | Packets ready for financial-protection outcomes. |
| priority_country_wave_packet_access_ready_rows | 0 | Packets ready for access/forgone-care outcomes. |
| priority_country_wave_packet_climate_ready_rows | 0 | Packets with accepted CHIRPS/ERA5 climate-linkage route. |
| priority_country_wave_packet_analysis_ready_rows | 0 | Packets ready for promoted data writes. |
| priority_country_wave_packet_action_rows | 13 | Next blocking actions across packets. |
| priority_country_wave_packet_reports_written | 13 | Per-wave packet markdown reports written. |
| priority_country_wave_packet_handoffs_written | 13 | Per-wave raw-folder packet handoffs written. |
| modeling_gate_status | blocked | Models remain blocked until promoted registry thresholds and accepted climate linkage pass. |
| priority_country_wave_packet_status_blocked_fail_closed | 13 | Packet status count. |
| priority_country_wave_packet_next_action_download_or_place_complete_original_raw_package | 13 | Next blocking action count. |

## Packet Index

| acquisition_batch_rank | idno | country | wave | public_documentation_status | official_metadata_evidence_status | credentialed_acquisition_status | raw_package_status | financial_protection_status | access_forgone_care_status | climate_linkage_status | packet_status | next_blocking_action |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | ETH_2021_ESPS-W5_v02_M | Ethiopia | 2021-2022 | ready | ready | ready | not_received_no_original_raw_package | blocked | blocked | blocked | blocked_fail_closed | download_or_place_complete_original_raw_package |
| 2 | ETH_2018_ESS_v04_M | Ethiopia | 2018-2019 | ready | ready | ready | not_received_no_original_raw_package | blocked | blocked | blocked | blocked_fail_closed | download_or_place_complete_original_raw_package |
| 3 | MWI_2007-2009_MTM_v01_M | Malawi | 2007-2009 | ready | ready | ready | not_received_no_original_raw_package | blocked | blocked | blocked | blocked_fail_closed | download_or_place_complete_original_raw_package |
| 4 | NGA_2012_GHSP-W2_v02_M | Nigeria | 2012-2013 | ready | ready | ready | not_received_no_original_raw_package | blocked | blocked | blocked | blocked_fail_closed | download_or_place_complete_original_raw_package |
| 5 | NGA_2015_GHSP-W3_v02_M | Nigeria | 2015-2016 | ready | ready | ready | not_received_no_original_raw_package | blocked | blocked | blocked | blocked_fail_closed | download_or_place_complete_original_raw_package |
| 6 | NGA_2010_GHSP-W1_v03_M | Nigeria | 2010-2011 | ready | ready | ready | not_received_no_original_raw_package | blocked | blocked | blocked | blocked_fail_closed | download_or_place_complete_original_raw_package |
| 7 | TZA_2008_NPS-R1_v03_M | Tanzania | 2008-2009 | ready | ready | ready | not_received_no_original_raw_package | blocked | blocked | blocked | blocked_fail_closed | download_or_place_complete_original_raw_package |
| 8 | TZA_2010_NPS-R2_v03_M | Tanzania | 2010-2011 | ready | ready | ready | not_received_no_original_raw_package | blocked | blocked | blocked | blocked_fail_closed | download_or_place_complete_original_raw_package |
| 9 | TZA_2012_NPS-R3_v01_M | Tanzania | 2012-2013 | ready | ready | ready | not_received_no_original_raw_package | blocked | blocked | blocked | blocked_fail_closed | download_or_place_complete_original_raw_package |
| 10 | UGA_2014_SAGE-EL_v01_M | Uganda | 2014 | ready | ready | ready | not_received_no_original_raw_package | blocked | blocked | blocked | blocked_fail_closed | download_or_place_complete_original_raw_package |
| 11 | JAM_1997_SLC_v01_M | Jamaica | 1997 | ready | ready | ready | not_received_no_original_raw_package | blocked | blocked | blocked | blocked_fail_closed | download_or_place_complete_original_raw_package |
| 12 | KGZ_1993_KMPS_v01_M | Kyrgyz Republic | 1993 | ready | ready | ready | not_received_no_original_raw_package | blocked | blocked | blocked | blocked_fail_closed | download_or_place_complete_original_raw_package |
| 13 | NPL_2010_LSS-III_v01_M | Nepal | 2010-2011 | ready | ready | ready | not_received_no_original_raw_package | blocked | blocked | blocked | blocked_fail_closed | download_or_place_complete_original_raw_package |

## Next Blocking Actions

| action_rank | idno | blocking_stage | required_action | local_target_folder |
|---|---|---|---|---|
| 1 | ETH_2021_ESPS-W5_v02_M | download_or_place_complete_original_raw_package | Download/place the complete unchanged original raw package and documentation in local_target_folder. | temp/raw_downloads/ETH_2021_ESPS-W5_v02_M/ |
| 2 | ETH_2018_ESS_v04_M | download_or_place_complete_original_raw_package | Download/place the complete unchanged original raw package and documentation in local_target_folder. | temp/raw_downloads/ETH_2018_ESS_v04_M/ |
| 3 | MWI_2007-2009_MTM_v01_M | download_or_place_complete_original_raw_package | Download/place the complete unchanged original raw package and documentation in local_target_folder. | temp/raw_downloads/MWI_2007-2009_MTM_v01_M/ |
| 4 | NGA_2012_GHSP-W2_v02_M | download_or_place_complete_original_raw_package | Download/place the complete unchanged original raw package and documentation in local_target_folder. | temp/raw_downloads/NGA_2012_GHSP-W2_v02_M/ |
| 5 | NGA_2015_GHSP-W3_v02_M | download_or_place_complete_original_raw_package | Download/place the complete unchanged original raw package and documentation in local_target_folder. | temp/raw_downloads/NGA_2015_GHSP-W3_v02_M/ |
| 6 | NGA_2010_GHSP-W1_v03_M | download_or_place_complete_original_raw_package | Download/place the complete unchanged original raw package and documentation in local_target_folder. | temp/raw_downloads/NGA_2010_GHSP-W1_v03_M/ |
| 7 | TZA_2008_NPS-R1_v03_M | download_or_place_complete_original_raw_package | Download/place the complete unchanged original raw package and documentation in local_target_folder. | temp/raw_downloads/TZA_2008_NPS-R1_v03_M/ |
| 8 | TZA_2010_NPS-R2_v03_M | download_or_place_complete_original_raw_package | Download/place the complete unchanged original raw package and documentation in local_target_folder. | temp/raw_downloads/TZA_2010_NPS-R2_v03_M/ |
| 9 | TZA_2012_NPS-R3_v01_M | download_or_place_complete_original_raw_package | Download/place the complete unchanged original raw package and documentation in local_target_folder. | temp/raw_downloads/TZA_2012_NPS-R3_v01_M/ |
| 10 | UGA_2014_SAGE-EL_v01_M | download_or_place_complete_original_raw_package | Download/place the complete unchanged original raw package and documentation in local_target_folder. | temp/raw_downloads/UGA_2014_SAGE-EL_v01_M/ |
| 11 | JAM_1997_SLC_v01_M | download_or_place_complete_original_raw_package | Download/place the complete unchanged original raw package and documentation in local_target_folder. | temp/raw_downloads/JAM_1997_SLC_v01_M/ |
| 12 | KGZ_1993_KMPS_v01_M | download_or_place_complete_original_raw_package | Download/place the complete unchanged original raw package and documentation in local_target_folder. | temp/raw_downloads/KGZ_1993_KMPS_v01_M/ |
| 13 | NPL_2010_LSS-III_v01_M | download_or_place_complete_original_raw_package | Download/place the complete unchanged original raw package and documentation in local_target_folder. | temp/raw_downloads/NPL_2010_LSS-III_v01_M/ |

## Failed Gate Preview

| acquisition_batch_rank | idno | gate | status | evidence | required_action |
|---|---|---|---|---|---|
| 1 | ETH_2021_ESPS-W5_v02_M | complete_original_raw_package | fail | receipt_status=not_received_no_original_raw_package; original_files=0; archives=0; raw_tabular=0; missing_targets=12 | Download/place the complete unchanged original raw package and documentation in the target folder. |
| 1 | ETH_2021_ESPS-W5_v02_M | priority_raw_module_coverage | fail | targets=12; covered=0; missing=12 | Ensure every priority target module is present directly or inside the received archive. |
| 1 | ETH_2021_ESPS-W5_v02_M | manual_requirement_verification | fail | requirements_passed=0/8 | Verify merge keys, survey design, consumption/income, OOP, access, timing, geography, missing codes, units, and recal... |
| 1 | ETH_2021_ESPS-W5_v02_M | manual_concept_verification | fail | concepts_passed=0/13 | Promote all required concepts only after raw variable value and level checks pass. |
| 1 | ETH_2021_ESPS-W5_v02_M | manual_variable_verification | fail | variables_passed=0/107 | Manually verify selected raw variables before harmonization recipe review. |
| 1 | ETH_2021_ESPS-W5_v02_M | financial_protection_value_ready | fail | financial_requirements_passed=0; financial_concepts_passed=0 | Verify total consumption/income, OOP health expenditure, weights/design, and denominator semantics for CHE10/CHE25 an... |
| 1 | ETH_2021_ESPS-W5_v02_M | access_forgone_care_value_ready | fail | double_failure_requirements_passed=0; double_failure_concepts_passed=0 | Verify illness/need, care seeking, forgone-care, and barrier variables with raw values and skip patterns. |
| 1 | ETH_2021_ESPS-W5_v02_M | accepted_chirps_era5_climate_linkage | fail | accepted_route=not_accepted_raw_timing_geography_unverified; gate=blocked_raw_timing_geography_not_verified_sources_r... | Verify timing/geography raw fields and accept a CHIRPS or ERA5 linkage route. |
| 1 | ETH_2021_ESPS-W5_v02_M | analysis_dataset_synthesis_join | fail | join_status=blocked_required_schema_columns_not_verified; required_columns=25; ready_columns=0; blocked_columns=22 | Complete required schema-column verification and join readiness before any promoted dataset build. |
| 1 | ETH_2021_ESPS-W5_v02_M | promoted_data_registry_write_gate | fail | registry_analysis_ready=not_promoted; rows=0 | Write to data/ only after the promoted registry marks this wave as analysis-ready. |
| 2 | ETH_2018_ESS_v04_M | complete_original_raw_package | fail | receipt_status=not_received_no_original_raw_package; original_files=0; archives=0; raw_tabular=0; missing_targets=12 | Download/place the complete unchanged original raw package and documentation in the target folder. |
| 2 | ETH_2018_ESS_v04_M | priority_raw_module_coverage | fail | targets=12; covered=0; missing=12 | Ensure every priority target module is present directly or inside the received archive. |
| 2 | ETH_2018_ESS_v04_M | manual_requirement_verification | fail | requirements_passed=0/8 | Verify merge keys, survey design, consumption/income, OOP, access, timing, geography, missing codes, units, and recal... |
| 2 | ETH_2018_ESS_v04_M | manual_concept_verification | fail | concepts_passed=0/13 | Promote all required concepts only after raw variable value and level checks pass. |
| 2 | ETH_2018_ESS_v04_M | manual_variable_verification | fail | variables_passed=0/102 | Manually verify selected raw variables before harmonization recipe review. |
| 2 | ETH_2018_ESS_v04_M | financial_protection_value_ready | fail | financial_requirements_passed=0; financial_concepts_passed=0 | Verify total consumption/income, OOP health expenditure, weights/design, and denominator semantics for CHE10/CHE25 an... |
| 2 | ETH_2018_ESS_v04_M | access_forgone_care_value_ready | fail | double_failure_requirements_passed=0; double_failure_concepts_passed=0 | Verify illness/need, care seeking, forgone-care, and barrier variables with raw values and skip patterns. |
| 2 | ETH_2018_ESS_v04_M | accepted_chirps_era5_climate_linkage | fail | accepted_route=not_accepted_raw_timing_geography_unverified; gate=blocked_raw_timing_geography_not_verified_sources_r... | Verify timing/geography raw fields and accept a CHIRPS or ERA5 linkage route. |
| 2 | ETH_2018_ESS_v04_M | analysis_dataset_synthesis_join | fail | join_status=blocked_required_schema_columns_not_verified; required_columns=25; ready_columns=0; blocked_columns=22 | Complete required schema-column verification and join readiness before any promoted dataset build. |
| 2 | ETH_2018_ESS_v04_M | promoted_data_registry_write_gate | fail | registry_analysis_ready=not_promoted; rows=0 | Write to data/ only after the promoted registry marks this wave as analysis-ready. |
| 3 | MWI_2007-2009_MTM_v01_M | complete_original_raw_package | fail | receipt_status=not_received_no_original_raw_package; original_files=0; archives=0; raw_tabular=0; missing_targets=12 | Download/place the complete unchanged original raw package and documentation in the target folder. |
| 3 | MWI_2007-2009_MTM_v01_M | priority_raw_module_coverage | fail | targets=12; covered=0; missing=12 | Ensure every priority target module is present directly or inside the received archive. |
| 3 | MWI_2007-2009_MTM_v01_M | manual_requirement_verification | fail | requirements_passed=0/8 | Verify merge keys, survey design, consumption/income, OOP, access, timing, geography, missing codes, units, and recal... |
| 3 | MWI_2007-2009_MTM_v01_M | manual_concept_verification | fail | concepts_passed=0/13 | Promote all required concepts only after raw variable value and level checks pass. |
| 3 | MWI_2007-2009_MTM_v01_M | manual_variable_verification | fail | variables_passed=0/128 | Manually verify selected raw variables before harmonization recipe review. |
| 3 | MWI_2007-2009_MTM_v01_M | financial_protection_value_ready | fail | financial_requirements_passed=0; financial_concepts_passed=0 | Verify total consumption/income, OOP health expenditure, weights/design, and denominator semantics for CHE10/CHE25 an... |
| 3 | MWI_2007-2009_MTM_v01_M | access_forgone_care_value_ready | fail | double_failure_requirements_passed=0; double_failure_concepts_passed=0 | Verify illness/need, care seeking, forgone-care, and barrier variables with raw values and skip patterns. |
| 3 | MWI_2007-2009_MTM_v01_M | accepted_chirps_era5_climate_linkage | fail | accepted_route=not_accepted_raw_timing_geography_unverified; gate=blocked_raw_timing_geography_not_verified_sources_r... | Verify timing/geography raw fields and accept a CHIRPS or ERA5 linkage route. |
| 3 | MWI_2007-2009_MTM_v01_M | analysis_dataset_synthesis_join | fail | join_status=blocked_required_schema_columns_not_verified; required_columns=25; ready_columns=0; blocked_columns=22 | Complete required schema-column verification and join readiness before any promoted dataset build. |
| 3 | MWI_2007-2009_MTM_v01_M | promoted_data_registry_write_gate | fail | registry_analysis_ready=not_promoted; rows=0 | Write to data/ only after the promoted registry marks this wave as analysis-ready. |

## Machine-Readable Outputs

- `temp/priority_country_wave_promotion_packet_index.csv`
- `temp/priority_country_wave_promotion_packet_gate_matrix.csv`
- `temp/priority_country_wave_promotion_packet_action_queue.csv`
- `result/priority_country_wave_promotion_packet_summary.csv`
- `report/priority_country_wave_promotion_packets/`
