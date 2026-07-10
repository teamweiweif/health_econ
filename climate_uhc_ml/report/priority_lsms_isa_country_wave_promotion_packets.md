# Priority LSMS-ISA Country-Wave Promotion Packets

Status: 19-wave refocused LSMS/ISA promotion-control layer. These packets
connect public documentation, official variable evidence, raw intake, archive
preflight, value-verification requirements, climate linkage, synthesis, and
registry gates for each target country-wave.

This layer does not write data into `data/`; it is deliberately fail-closed
until complete original raw packages and raw value checks pass.

## Summary

| Metric | Value | Interpretation |
|---|---:|---|
| priority_lsms_country_wave_packet_rows | 19 | Refocused LSMS/ISA country-wave promotion packets built. |
| priority_lsms_country_wave_packet_core_rows | 10 | Core selected/refocused replacement packets. |
| priority_lsms_country_wave_packet_backup_rows | 9 | Backup and sixth-country candidate packets. |
| priority_lsms_country_wave_packet_gate_rows | 361 | Gate rows across LSMS/ISA promotion packets. |
| priority_lsms_country_wave_packet_passed_gate_rows | 52 | Packet gates currently passing. |
| priority_lsms_country_wave_packet_failed_gate_rows | 309 | Packet gates still blocking promotion. |
| priority_lsms_country_wave_packet_public_documentation_ready_rows | 19 | Packets with complete public documentation receipt. |
| priority_lsms_country_wave_packet_variable_evidence_ready_rows | 19 | Packets with official variable evidence coverage ready for raw review. |
| priority_lsms_country_wave_packet_raw_package_ready_rows | 1 | Packets with complete original raw package receipt and documentation. |
| priority_lsms_country_wave_packet_archive_preflight_ready_rows | 1 | Packets with readable archive/direct raw preflight. |
| priority_lsms_country_wave_packet_raw_value_verified_rows | 1 | Packets with all required raw values verified. |
| priority_lsms_country_wave_packet_financial_ready_rows | 1 | Packets ready for financial-protection outcomes. |
| priority_lsms_country_wave_packet_access_ready_rows | 1 | Packets ready for access/forgone-care outcomes. |
| priority_lsms_country_wave_packet_climate_ready_rows | 0 | Packets with accepted CHIRPS/ERA5 climate-linkage route. |
| priority_lsms_country_wave_packet_analysis_synthesis_ready_rows | 0 | Packets ready for promoted dataset synthesis. |
| priority_lsms_country_wave_packet_analysis_ready_rows | 0 | Packets ready for promoted data writes. |
| priority_lsms_country_wave_packet_action_rows | 19 | Next blocking actions across LSMS/ISA packets. |
| priority_lsms_country_wave_packet_reports_written | 19 | Per-wave packet reports written. |
| priority_lsms_country_wave_packet_handoffs_written | 19 | Per-wave raw-folder packet handoffs written. |
| priority_lsms_country_wave_packet_data_write_status | blocked_no_promoted_rows | No LSMS/ISA country-wave may write to data/ from metadata-only packet evidence. |
| modeling_gate_status | blocked | Models remain blocked until raw-backed promotion thresholds and accepted climate linkage pass. |
| priority_lsms_country_wave_packet_status_blocked_fail_closed | 19 | Packet status count. |
| priority_lsms_country_wave_packet_next_action_download_or_place_complete_original_raw_package | 18 | Next blocking action count. |
| priority_lsms_country_wave_packet_next_action_extract_validate_chirps_adm2_exposures | 1 | Next blocking action count. |

## Packet Index

| download_priority_order | queue_role | idno | country | wave | public_documentation_status | variable_evidence_status | raw_package_status | archive_preflight_status | raw_value_verification_status | climate_linkage_status | packet_status | next_blocking_action |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | core_selected_lsms_isa_aligned | ETH_2021_ESPS-W5_v02_M | Ethiopia | 2021-2022 | ready_metadata_only | ready_metadata_only_raw_review_required | not_received_no_original_raw_package | blocked_no_original_archive_or_direct_files | blocked_not_raw_value_verified | blocked | blocked_fail_closed | download_or_place_complete_original_raw_package |
| 2 | core_selected_lsms_isa_aligned | ETH_2018_ESS_v04_M | Ethiopia | 2018-2019 | ready_metadata_only | ready_metadata_only_raw_review_required | not_received_no_original_raw_package | blocked_no_original_archive_or_direct_files | blocked_not_raw_value_verified | blocked | blocked_fail_closed | download_or_place_complete_original_raw_package |
| 3 | core_replacement_primary | MWI_2004_IHS-II_v01_M | Malawi | 2004-2005 | ready_metadata_only | ready_metadata_only_raw_review_required | raw_archive_plus_official_public_documentation_ready_for_raw_review | ready_for_raw_receipt_schema_and_manual_review | all_verified | blocked | blocked_fail_closed | extract_validate_chirps_adm2_exposures |
| 4 | core_selected_lsms_isa_aligned | NGA_2012_GHSP-W2_v02_M | Nigeria | 2012-2013 | ready_metadata_only | ready_metadata_only_raw_review_required | not_received_no_original_raw_package | blocked_no_original_archive_or_direct_files | blocked_not_raw_value_verified | blocked | blocked_fail_closed | download_or_place_complete_original_raw_package |
| 5 | core_selected_lsms_isa_aligned | NGA_2015_GHSP-W3_v02_M | Nigeria | 2015-2016 | ready_metadata_only | ready_metadata_only_raw_review_required | not_received_no_original_raw_package | blocked_no_original_archive_or_direct_files | blocked_not_raw_value_verified | blocked | blocked_fail_closed | download_or_place_complete_original_raw_package |
| 6 | core_selected_lsms_isa_aligned | NGA_2010_GHSP-W1_v03_M | Nigeria | 2010-2011 | ready_metadata_only | ready_metadata_only_raw_review_required | not_received_no_original_raw_package | blocked_no_original_archive_or_direct_files | blocked_not_raw_value_verified | blocked | blocked_fail_closed | download_or_place_complete_original_raw_package |
| 7 | core_selected_lsms_isa_aligned | TZA_2008_NPS-R1_v03_M | Tanzania | 2008-2009 | ready_metadata_only | ready_metadata_only_raw_review_required | not_received_no_original_raw_package | blocked_no_original_archive_or_direct_files | blocked_not_raw_value_verified | blocked | blocked_fail_closed | download_or_place_complete_original_raw_package |
| 8 | core_selected_lsms_isa_aligned | TZA_2010_NPS-R2_v03_M | Tanzania | 2010-2011 | ready_metadata_only | ready_metadata_only_raw_review_required | not_received_no_original_raw_package | blocked_no_original_archive_or_direct_files | blocked_not_raw_value_verified | blocked | blocked_fail_closed | download_or_place_complete_original_raw_package |
| 9 | core_selected_lsms_isa_aligned | TZA_2012_NPS-R3_v01_M | Tanzania | 2012-2013 | ready_metadata_only | ready_metadata_only_raw_review_required | not_received_no_original_raw_package | blocked_no_original_archive_or_direct_files | blocked_not_raw_value_verified | blocked | blocked_fail_closed | download_or_place_complete_original_raw_package |
| 10 | core_replacement_primary | UGA_2019_UNPS_v03_M | Uganda | 2019-2020 | ready_metadata_only | ready_metadata_only_raw_review_required | not_received_no_original_raw_package | blocked_no_original_archive_or_direct_files | blocked_not_raw_value_verified | blocked | blocked_fail_closed | download_or_place_complete_original_raw_package |
| 11 | sixth_country_backup_candidate | JAM_1997_SLC_v01_M | Jamaica | 1997 | ready_metadata_only | ready_metadata_only_raw_review_required | not_received_no_original_raw_package | blocked_no_original_archive_or_direct_files | blocked_not_raw_value_verified | blocked | blocked_fail_closed | download_or_place_complete_original_raw_package |
| 12 | sixth_country_backup_candidate | KGZ_1993_KMPS_v01_M | Kyrgyz Republic | 1993 | ready_metadata_only | ready_metadata_only_raw_review_required | not_received_no_original_raw_package | blocked_no_original_archive_or_direct_files | blocked_not_raw_value_verified | blocked | blocked_fail_closed | download_or_place_complete_original_raw_package |
| 13 | sixth_country_backup_candidate | NPL_2010_LSS-III_v01_M | Nepal | 2010-2011 | ready_metadata_only | ready_metadata_only_raw_review_required | not_received_no_original_raw_package | blocked_no_original_archive_or_direct_files | blocked_not_raw_value_verified | blocked | blocked_fail_closed | download_or_place_complete_original_raw_package |
| 14 | replacement_backup_wave | MWI_2019_IHS-V_v06_M | Malawi | 2019-2020 | ready_metadata_only | ready_metadata_only_raw_review_required | not_received_no_original_raw_package | blocked_no_original_archive_or_direct_files | blocked_not_raw_value_verified | blocked | blocked_fail_closed | download_or_place_complete_original_raw_package |
| 15 | replacement_backup_wave | MWI_2016_IHS-IV_v04_M | Malawi | 2016-2017 | ready_metadata_only | ready_metadata_only_raw_review_required | not_received_no_original_raw_package | blocked_no_original_archive_or_direct_files | blocked_not_raw_value_verified | blocked | blocked_fail_closed | download_or_place_complete_original_raw_package |
| 16 | replacement_backup_wave | MWI_2010_IHS-III_v01_M | Malawi | 2010-2011 | ready_metadata_only | ready_metadata_only_raw_review_required | not_received_no_original_raw_package | blocked_no_original_archive_or_direct_files | blocked_not_raw_value_verified | blocked | blocked_fail_closed | download_or_place_complete_original_raw_package |
| 17 | replacement_backup_wave | UGA_2011_UNPS_v02_M | Uganda | 2011-2012 | ready_metadata_only | ready_metadata_only_raw_review_required | not_received_no_original_raw_package | blocked_no_original_archive_or_direct_files | blocked_not_raw_value_verified | blocked | blocked_fail_closed | download_or_place_complete_original_raw_package |
| 18 | replacement_backup_wave | UGA_2018_UNPS_v02_M | Uganda | 2018-2019 | ready_metadata_only | ready_metadata_only_raw_review_required | not_received_no_original_raw_package | blocked_no_original_archive_or_direct_files | blocked_not_raw_value_verified | blocked | blocked_fail_closed | download_or_place_complete_original_raw_package |
| 19 | replacement_backup_wave | UGA_2015_UNPS_v02_M | Uganda | 2015-2016 | ready_metadata_only | ready_metadata_only_raw_review_required | not_received_no_original_raw_package | blocked_no_original_archive_or_direct_files | blocked_not_raw_value_verified | blocked | blocked_fail_closed | download_or_place_complete_original_raw_package |

## Next Blocking Actions

| action_rank | idno | blocking_stage | required_action | local_target_folder |
|---|---|---|---|---|
| 1 | ETH_2021_ESPS-W5_v02_M | download_or_place_complete_original_raw_package | Download/place the complete unchanged official raw package and all documentation in local_target_folder. | temp/raw_downloads/ETH_2021_ESPS-W5_v02_M/ |
| 2 | ETH_2018_ESS_v04_M | download_or_place_complete_original_raw_package | Download/place the complete unchanged official raw package and all documentation in local_target_folder. | temp/raw_downloads/ETH_2018_ESS_v04_M/ |
| 3 | MWI_2004_IHS-II_v01_M | extract_validate_chirps_adm2_exposures | Download/extract CHIRPS ADM2 monthly rasters, validate coverage/units/lag windows, then decide whether the climate li... | temp/raw_downloads/MWI_2004_IHS-II_v01_M/ |
| 4 | NGA_2012_GHSP-W2_v02_M | download_or_place_complete_original_raw_package | Download/place the complete unchanged official raw package and all documentation in local_target_folder. | temp/raw_downloads/NGA_2012_GHSP-W2_v02_M/ |
| 5 | NGA_2015_GHSP-W3_v02_M | download_or_place_complete_original_raw_package | Download/place the complete unchanged official raw package and all documentation in local_target_folder. | temp/raw_downloads/NGA_2015_GHSP-W3_v02_M/ |
| 6 | NGA_2010_GHSP-W1_v03_M | download_or_place_complete_original_raw_package | Download/place the complete unchanged official raw package and all documentation in local_target_folder. | temp/raw_downloads/NGA_2010_GHSP-W1_v03_M/ |
| 7 | TZA_2008_NPS-R1_v03_M | download_or_place_complete_original_raw_package | Download/place the complete unchanged official raw package and all documentation in local_target_folder. | temp/raw_downloads/TZA_2008_NPS-R1_v03_M/ |
| 8 | TZA_2010_NPS-R2_v03_M | download_or_place_complete_original_raw_package | Download/place the complete unchanged official raw package and all documentation in local_target_folder. | temp/raw_downloads/TZA_2010_NPS-R2_v03_M/ |
| 9 | TZA_2012_NPS-R3_v01_M | download_or_place_complete_original_raw_package | Download/place the complete unchanged official raw package and all documentation in local_target_folder. | temp/raw_downloads/TZA_2012_NPS-R3_v01_M/ |
| 10 | UGA_2019_UNPS_v03_M | download_or_place_complete_original_raw_package | Download/place the complete unchanged official raw package and all documentation in local_target_folder. | temp/raw_downloads/UGA_2019_UNPS_v03_M/ |
| 11 | JAM_1997_SLC_v01_M | download_or_place_complete_original_raw_package | Download/place the complete unchanged official raw package and all documentation in local_target_folder. | temp/raw_downloads/JAM_1997_SLC_v01_M/ |
| 12 | KGZ_1993_KMPS_v01_M | download_or_place_complete_original_raw_package | Download/place the complete unchanged official raw package and all documentation in local_target_folder. | temp/raw_downloads/KGZ_1993_KMPS_v01_M/ |
| 13 | NPL_2010_LSS-III_v01_M | download_or_place_complete_original_raw_package | Download/place the complete unchanged official raw package and all documentation in local_target_folder. | temp/raw_downloads/NPL_2010_LSS-III_v01_M/ |
| 14 | MWI_2019_IHS-V_v06_M | download_or_place_complete_original_raw_package | Download/place the complete unchanged official raw package and all documentation in local_target_folder. | temp/raw_downloads/MWI_2019_IHS-V_v06_M/ |
| 15 | MWI_2016_IHS-IV_v04_M | download_or_place_complete_original_raw_package | Download/place the complete unchanged official raw package and all documentation in local_target_folder. | temp/raw_downloads/MWI_2016_IHS-IV_v04_M/ |
| 16 | MWI_2010_IHS-III_v01_M | download_or_place_complete_original_raw_package | Download/place the complete unchanged official raw package and all documentation in local_target_folder. | temp/raw_downloads/MWI_2010_IHS-III_v01_M/ |
| 17 | UGA_2011_UNPS_v02_M | download_or_place_complete_original_raw_package | Download/place the complete unchanged official raw package and all documentation in local_target_folder. | temp/raw_downloads/UGA_2011_UNPS_v02_M/ |
| 18 | UGA_2018_UNPS_v02_M | download_or_place_complete_original_raw_package | Download/place the complete unchanged official raw package and all documentation in local_target_folder. | temp/raw_downloads/UGA_2018_UNPS_v02_M/ |
| 19 | UGA_2015_UNPS_v02_M | download_or_place_complete_original_raw_package | Download/place the complete unchanged official raw package and all documentation in local_target_folder. | temp/raw_downloads/UGA_2015_UNPS_v02_M/ |

## Failed Gate Preview

| download_priority_order | idno | gate | status | evidence | required_action |
|---|---|---|---|---|---|
| 1 | ETH_2021_ESPS-W5_v02_M | complete_original_raw_package | fail | intake_status=blocked_no_original_package; original_files=0; archives=0; raw_tabular=0; package_docs=0; public_docs=c... | Download/place the complete unchanged official raw package and all documentation in the target folder. |
| 1 | ETH_2021_ESPS-W5_v02_M | archive_or_direct_file_preflight | fail | status=blocked_no_original_archive_or_direct_files; direct_raw=0; direct_docs=0; archive_members=0 | Confirm readable archive/direct raw and documentation files before schema inspection. |
| 1 | ETH_2021_ESPS-W5_v02_M | raw_value_verification_household_person_keys | fail | metadata=official_metadata_strong_candidates_present_raw_review_required; candidates=12; files=11; raw_status=not_raw... | Verify this requirement against raw files, value labels, units, recall periods, skip patterns, and merge level. |
| 1 | ETH_2021_ESPS-W5_v02_M | raw_value_verification_weights_and_design | fail | metadata=official_metadata_strong_candidates_present_raw_review_required; candidates=12; files=11; raw_status=not_raw... | Verify this requirement against raw files, value labels, units, recall periods, skip patterns, and merge level. |
| 1 | ETH_2021_ESPS-W5_v02_M | raw_value_verification_consumption_or_income | fail | metadata=official_metadata_strong_candidates_present_raw_review_required; candidates=12; files=1; raw_status=not_raw_... | Verify this requirement against raw files, value labels, units, recall periods, skip patterns, and merge level. |
| 1 | ETH_2021_ESPS-W5_v02_M | raw_value_verification_oop_health_expenditure | fail | metadata=official_metadata_strong_candidates_present_raw_review_required; candidates=12; files=2; raw_status=not_raw_... | Verify this requirement against raw files, value labels, units, recall periods, skip patterns, and merge level. |
| 1 | ETH_2021_ESPS-W5_v02_M | raw_value_verification_health_need_and_access | fail | metadata=official_metadata_strong_candidates_present_raw_review_required; candidates=12; files=3; raw_status=not_raw_... | Verify this requirement against raw files, value labels, units, recall periods, skip patterns, and merge level. |
| 1 | ETH_2021_ESPS-W5_v02_M | raw_value_verification_survey_timing | fail | metadata=official_metadata_strong_candidates_present_raw_review_required; candidates=12; files=10; raw_status=not_raw... | Verify this requirement against raw files, value labels, units, recall periods, skip patterns, and merge level. |
| 1 | ETH_2021_ESPS-W5_v02_M | raw_value_verification_climate_geography | fail | metadata=official_metadata_strong_candidates_present_raw_review_required; candidates=12; files=6; raw_status=not_raw_... | Verify this requirement against raw files, value labels, units, recall periods, skip patterns, and merge level. |
| 1 | ETH_2021_ESPS-W5_v02_M | raw_value_verification_missing_codes_units_recall_skip_patterns | fail | metadata=documentation_and_raw_review_required_no_variable_shortlist; candidates=0; files=0; raw_status=not_raw_value... | Verify this requirement against raw files, value labels, units, recall periods, skip patterns, and merge level. |
| 1 | ETH_2021_ESPS-W5_v02_M | all_required_raw_values_verified | fail | verified_requirement_rows=0/8 | Complete raw-backed verification for every required promotion requirement. |
| 1 | ETH_2021_ESPS-W5_v02_M | financial_protection_inputs_ready | fail | requires verified weights/design, total consumption or income, and OOP health expenditure. | Verify financial-protection inputs before CHE10/CHE25 or SDG 3.8.2 readiness can be claimed. |
| 1 | ETH_2021_ESPS-W5_v02_M | access_forgone_care_inputs_ready | fail | requires verified illness/need, care-seeking, and access-barrier raw variables. | Verify illness/need and care-seeking/access variables before double-failure readiness can be claimed. |
| 1 | ETH_2021_ESPS-W5_v02_M | timing_geography_ready_for_climate | fail | requires verified survey timing and GPS/cluster/EA/admin geography. | Verify timing and geography raw fields before accepting a climate linkage route. |
| 1 | ETH_2021_ESPS-W5_v02_M | accepted_chirps_or_era5_linkage_route | fail | accepted_route=not_accepted_raw_timing_geography_unverified; current_gate=blocked_raw_timing_geography_not_verified_s... | Accept a CHIRPS or ERA5 route only after timing/geography verification passes. |
| 1 | ETH_2021_ESPS-W5_v02_M | analysis_dataset_synthesis_ready | fail | join_status=blocked_required_schema_columns_not_verified; ready_columns=0; blocked_columns=22 | Complete promoted household-climate schema and join review. |
| 1 | ETH_2021_ESPS-W5_v02_M | promoted_registry_write_gate | fail | registry_analysis_ready=not_promoted; rows=0 | Write to data/ only when the promoted registry marks this country-wave as analysis-ready with nonzero rows. |
| 2 | ETH_2018_ESS_v04_M | complete_original_raw_package | fail | intake_status=blocked_no_original_package; original_files=0; archives=0; raw_tabular=0; package_docs=0; public_docs=c... | Download/place the complete unchanged official raw package and all documentation in the target folder. |
| 2 | ETH_2018_ESS_v04_M | archive_or_direct_file_preflight | fail | status=blocked_no_original_archive_or_direct_files; direct_raw=0; direct_docs=0; archive_members=0 | Confirm readable archive/direct raw and documentation files before schema inspection. |
| 2 | ETH_2018_ESS_v04_M | raw_value_verification_household_person_keys | fail | metadata=official_metadata_strong_candidates_present_raw_review_required; candidates=12; files=10; raw_status=not_raw... | Verify this requirement against raw files, value labels, units, recall periods, skip patterns, and merge level. |
| 2 | ETH_2018_ESS_v04_M | raw_value_verification_weights_and_design | fail | metadata=official_metadata_strong_candidates_present_raw_review_required; candidates=12; files=12; raw_status=not_raw... | Verify this requirement against raw files, value labels, units, recall periods, skip patterns, and merge level. |
| 2 | ETH_2018_ESS_v04_M | raw_value_verification_consumption_or_income | fail | metadata=official_metadata_strong_candidates_present_raw_review_required; candidates=12; files=2; raw_status=not_raw_... | Verify this requirement against raw files, value labels, units, recall periods, skip patterns, and merge level. |
| 2 | ETH_2018_ESS_v04_M | raw_value_verification_oop_health_expenditure | fail | metadata=official_metadata_strong_candidates_present_raw_review_required; candidates=12; files=2; raw_status=not_raw_... | Verify this requirement against raw files, value labels, units, recall periods, skip patterns, and merge level. |
| 2 | ETH_2018_ESS_v04_M | raw_value_verification_health_need_and_access | fail | metadata=official_metadata_strong_candidates_present_raw_review_required; candidates=12; files=2; raw_status=not_raw_... | Verify this requirement against raw files, value labels, units, recall periods, skip patterns, and merge level. |
| 2 | ETH_2018_ESS_v04_M | raw_value_verification_survey_timing | fail | metadata=official_metadata_strong_candidates_present_raw_review_required; candidates=12; files=7; raw_status=not_raw_... | Verify this requirement against raw files, value labels, units, recall periods, skip patterns, and merge level. |
| 2 | ETH_2018_ESS_v04_M | raw_value_verification_climate_geography | fail | metadata=official_metadata_strong_candidates_present_raw_review_required; candidates=12; files=6; raw_status=not_raw_... | Verify this requirement against raw files, value labels, units, recall periods, skip patterns, and merge level. |
| 2 | ETH_2018_ESS_v04_M | raw_value_verification_missing_codes_units_recall_skip_patterns | fail | metadata=documentation_and_raw_review_required_no_variable_shortlist; candidates=0; files=0; raw_status=not_raw_value... | Verify this requirement against raw files, value labels, units, recall periods, skip patterns, and merge level. |
| 2 | ETH_2018_ESS_v04_M | all_required_raw_values_verified | fail | verified_requirement_rows=0/8 | Complete raw-backed verification for every required promotion requirement. |
| 2 | ETH_2018_ESS_v04_M | financial_protection_inputs_ready | fail | requires verified weights/design, total consumption or income, and OOP health expenditure. | Verify financial-protection inputs before CHE10/CHE25 or SDG 3.8.2 readiness can be claimed. |
| 2 | ETH_2018_ESS_v04_M | access_forgone_care_inputs_ready | fail | requires verified illness/need, care-seeking, and access-barrier raw variables. | Verify illness/need and care-seeking/access variables before double-failure readiness can be claimed. |
| 2 | ETH_2018_ESS_v04_M | timing_geography_ready_for_climate | fail | requires verified survey timing and GPS/cluster/EA/admin geography. | Verify timing and geography raw fields before accepting a climate linkage route. |
| 2 | ETH_2018_ESS_v04_M | accepted_chirps_or_era5_linkage_route | fail | accepted_route=not_accepted_raw_timing_geography_unverified; current_gate=blocked_raw_timing_geography_not_verified_s... | Accept a CHIRPS or ERA5 route only after timing/geography verification passes. |
| 2 | ETH_2018_ESS_v04_M | analysis_dataset_synthesis_ready | fail | join_status=blocked_required_schema_columns_not_verified; ready_columns=0; blocked_columns=22 | Complete promoted household-climate schema and join review. |
| 2 | ETH_2018_ESS_v04_M | promoted_registry_write_gate | fail | registry_analysis_ready=not_promoted; rows=0 | Write to data/ only when the promoted registry marks this country-wave as analysis-ready with nonzero rows. |
| 3 | MWI_2004_IHS-II_v01_M | accepted_chirps_or_era5_linkage_route | fail | accepted_route=not_accepted_extraction_and_validation_pending; current_gate=route_preflight_ready_needs_extraction_va... | Download/extract CHIRPS ADM2 monthly rasters and validate units, spatial coverage, and lag windows. |
| 3 | MWI_2004_IHS-II_v01_M | analysis_dataset_synthesis_ready | fail | join_status=missing; ready_columns=0; blocked_columns=0 | Complete promoted household-climate schema and join review. |
| 3 | MWI_2004_IHS-II_v01_M | promoted_registry_write_gate | fail | registry_analysis_ready=not_promoted; rows=0 | Write to data/ only when the promoted registry marks this country-wave as analysis-ready with nonzero rows. |
| 4 | NGA_2012_GHSP-W2_v02_M | complete_original_raw_package | fail | intake_status=blocked_no_original_package; original_files=0; archives=0; raw_tabular=0; package_docs=0; public_docs=c... | Download/place the complete unchanged official raw package and all documentation in the target folder. |
| 4 | NGA_2012_GHSP-W2_v02_M | archive_or_direct_file_preflight | fail | status=blocked_no_original_archive_or_direct_files; direct_raw=0; direct_docs=0; archive_members=0 | Confirm readable archive/direct raw and documentation files before schema inspection. |
| 4 | NGA_2012_GHSP-W2_v02_M | raw_value_verification_household_person_keys | fail | metadata=official_metadata_strong_candidates_present_raw_review_required; candidates=12; files=12; raw_status=not_raw... | Verify this requirement against raw files, value labels, units, recall periods, skip patterns, and merge level. |

## Machine-Readable Outputs

- `temp/priority_lsms_isa_country_wave_promotion_packet_index.csv`
- `temp/priority_lsms_isa_country_wave_promotion_packet_gate_matrix.csv`
- `temp/priority_lsms_isa_country_wave_promotion_packet_action_queue.csv`
- `result/priority_lsms_isa_country_wave_promotion_packet_summary.csv`
- `report/priority_lsms_isa_country_wave_promotion_packets/`

## Guardrail

Public metadata coverage is not raw value verification. Every packet remains
blocked from promoted-data writes until complete raw packages, requirement-level
raw checks, and an accepted CHIRPS or ERA5 linkage route pass.
