# Priority LSMS-ISA Country-Wave Promotion Packet

Dataset: `TZA_2008_NPS-R1_v03_M` - Tanzania 2008-2009

Survey: National Panel Survey 2008-2009, Wave 1

Official get-microdata URL: https://microdata.worldbank.org/catalog/76/get-microdata

Target raw folder: `temp/raw_downloads/TZA_2008_NPS-R1_v03_M/`

Current packet status: `blocked_fail_closed`

Analysis-ready status: `not_promoted`

Next blocking action: `download_or_place_complete_original_raw_package`

## Gate Matrix

| gate | status | evidence | required_action |
|---|---|---|---|
| official_public_documentation_receipt | pass | status=complete_core_public_documentation_receipt; saved=catalog_idno_json;data_dictionary_html;ddi_metadata;get_micr... |  |
| official_variable_evidence_coverage | pass | coverage_rows=8; matrix_rows=84; shortlist_rows=35; no_candidate_rows=0 |  |
| complete_original_raw_package | fail | intake_status=blocked_no_original_package; original_files=0; archives=0; raw_tabular=0; documentation=0 | Download/place the complete unchanged official raw package and all documentation in the target folder. |
| archive_or_direct_file_preflight | fail | status=blocked_no_original_archive_or_direct_files; direct_raw=0; direct_docs=0; archive_members=0 | Confirm readable archive/direct raw and documentation files before schema inspection. |
| raw_value_verification_household_person_keys | fail | metadata=official_metadata_strong_candidates_present_raw_review_required; candidates=12; files=11; raw_status=not_raw... | Verify this requirement against raw files, value labels, units, recall periods, skip patterns, and merge level. |
| raw_value_verification_weights_and_design | fail | metadata=official_metadata_strong_candidates_present_raw_review_required; candidates=12; files=7; raw_status=not_raw_... | Verify this requirement against raw files, value labels, units, recall periods, skip patterns, and merge level. |
| raw_value_verification_consumption_or_income | fail | metadata=official_metadata_strong_candidates_present_raw_review_required; candidates=12; files=3; raw_status=not_raw_... | Verify this requirement against raw files, value labels, units, recall periods, skip patterns, and merge level. |
| raw_value_verification_oop_health_expenditure | fail | metadata=official_metadata_strong_candidates_present_raw_review_required; candidates=12; files=2; raw_status=not_raw_... | Verify this requirement against raw files, value labels, units, recall periods, skip patterns, and merge level. |
| raw_value_verification_health_need_and_access | fail | metadata=official_metadata_weak_candidates_present_raw_review_required; candidates=12; files=2; raw_status=not_raw_va... | Verify this requirement against raw files, value labels, units, recall periods, skip patterns, and merge level. |
| raw_value_verification_survey_timing | fail | metadata=official_metadata_strong_candidates_present_raw_review_required; candidates=12; files=5; raw_status=not_raw_... | Verify this requirement against raw files, value labels, units, recall periods, skip patterns, and merge level. |
| raw_value_verification_climate_geography | fail | metadata=official_metadata_strong_candidates_present_raw_review_required; candidates=12; files=9; raw_status=not_raw_... | Verify this requirement against raw files, value labels, units, recall periods, skip patterns, and merge level. |
| raw_value_verification_missing_codes_units_recall_skip_patterns | fail | metadata=documentation_and_raw_review_required_no_variable_shortlist; candidates=0; files=0; raw_status=not_raw_value... | Verify this requirement against raw files, value labels, units, recall periods, skip patterns, and merge level. |
| all_required_raw_values_verified | fail | verified_requirement_rows=0/8 | Complete raw-backed verification for every required promotion requirement. |
| financial_protection_inputs_ready | fail | requires verified weights/design, total consumption or income, and OOP health expenditure. | Verify financial-protection inputs before CHE10/CHE25 or SDG 3.8.2 readiness can be claimed. |
| access_forgone_care_inputs_ready | fail | requires verified illness/need, care-seeking, and access-barrier raw variables. | Verify illness/need and care-seeking/access variables before double-failure readiness can be claimed. |
| timing_geography_ready_for_climate | fail | requires verified survey timing and GPS/cluster/EA/admin geography. | Verify timing and geography raw fields before accepting a climate linkage route. |
| accepted_chirps_or_era5_linkage_route | fail | accepted_route=not_accepted_raw_timing_geography_unverified; current_gate=blocked_raw_timing_geography_not_verified_s... | Accept a CHIRPS or ERA5 route only after timing/geography verification passes. |
| analysis_dataset_synthesis_ready | fail | join_status=blocked_required_schema_columns_not_verified; ready_columns=0; blocked_columns=22 | Complete promoted household-climate schema and join review. |
| promoted_registry_write_gate | fail | registry_analysis_ready=not_promoted; rows=0 | Write to data/ only when the promoted registry marks this country-wave as analysis-ready with nonzero rows. |

## Requirement Variable Evidence

| requirement | coverage_status | candidate_variable_rows | strong_candidate_variable_rows | raw_value_verification_status |
|---|---|---|---|---|
| household_person_keys | official_metadata_strong_candidates_present_raw_review_required | 12 | 12 | not_raw_value_verified |
| weights_and_design | official_metadata_strong_candidates_present_raw_review_required | 12 | 12 | not_raw_value_verified |
| consumption_or_income | official_metadata_strong_candidates_present_raw_review_required | 12 | 12 | not_raw_value_verified |
| oop_health_expenditure | official_metadata_strong_candidates_present_raw_review_required | 12 | 12 | not_raw_value_verified |
| health_need_and_access | official_metadata_weak_candidates_present_raw_review_required | 12 | 0 | not_raw_value_verified |
| survey_timing | official_metadata_strong_candidates_present_raw_review_required | 12 | 3 | not_raw_value_verified |
| climate_geography | official_metadata_strong_candidates_present_raw_review_required | 12 | 12 | not_raw_value_verified |
| missing_codes_units_recall_skip_patterns | documentation_and_raw_review_required_no_variable_shortlist | 0 | 0 | not_raw_value_verified |

## Official Public Documentation

| resource_type | receipt_status | saved_path |
|---|---|---|
| get_microdata_html | saved_existing | temp/source_snapshots/priority_lsms_isa_public_documentation/7_TZA_2008_NPS-R1_v03_M/get_microdata_html.html |
| catalog_idno_json | saved_existing | temp/source_snapshots/priority_lsms_isa_public_documentation/7_TZA_2008_NPS-R1_v03_M/catalog_idno_json.json |
| variables_idno_json | saved_existing | temp/source_snapshots/priority_lsms_isa_public_documentation/7_TZA_2008_NPS-R1_v03_M/variables_idno_json.json |
| ddi_metadata | saved_existing | temp/source_snapshots/priority_lsms_isa_public_documentation/7_TZA_2008_NPS-R1_v03_M/ddi_metadata.xml |
| json_metadata | saved_existing | temp/source_snapshots/priority_lsms_isa_public_documentation/7_TZA_2008_NPS-R1_v03_M/json_metadata.json |
| data_dictionary_html | saved_existing | temp/source_snapshots/priority_lsms_isa_public_documentation/7_TZA_2008_NPS-R1_v03_M/data_dictionary_html.html |
| related_materials_html | saved_existing | temp/source_snapshots/priority_lsms_isa_public_documentation/7_TZA_2008_NPS-R1_v03_M/related_materials_html.html |

## Concept File Shortlist

| requirement | file_name | candidate_variable_rows | top_variable_names |
|---|---|---|---|
| climate_geography | HH.Geovariables_Y1 | 3 | ea_id;lat_modified;lon_modified |
| climate_geography | SEC_A_T_English_Labels | 2 | clusterid;ea |
| climate_geography | SEC_A_T_Swahili_Labels | 1 | ea |
| climate_geography | SECTA1A2_Swahili_Labels | 1 | ea_id |
| climate_geography | SECTCB_Swahili_Labels | 1 | ea_id |
| climate_geography | SECTCEFG | 1 | ea_id |
| climate_geography | SECTCH | 1 | ea_id |
| climate_geography | SECTCI | 1 | ea_id |
| consumption_or_income | TZY1.HH.Consumption | 4 | hhexpenses;hhexpensesR;expm;expmR |
| consumption_or_income | SEC_L_Swahili_Labels | 4 | hhid;slcode;slq1;slq2 |
| consumption_or_income | SEC_M_Swahili_Labels | 4 | hhid;smcode;smq1;smq2 |
| health_need_and_access | SEC_B_C_D_E1_F_G1_U_English_Labels | 11 | sdq22;sdq4;sdq43_1;sdq43_2;sdq43_3;sdq55_1;sdq55_2;sdq55_3;sdq6;sdq8;sdq9 |
| health_need_and_access | SEC_I_English_Labels | 1 | siq8b |
| household_person_keys | Agriculture SEC_1_ALL_Swahili_Labels | 2 | hhid;rosterid |
| household_person_keys | SEC_B_C_D_E1_F_G1_U_Swahili_Labels | 1 | hhid |
| household_person_keys | SEC_2A_Swahili_Labels | 1 | hhid |

## Candidate Variable Preview

| requirement | variable_name | variable_label | file_name | match_score |
|---|---|---|---|---|
| household_person_keys | hhid | Unique HH Identifier | SEC_B_C_D_E1_F_G1_U_Swahili_Labels | 27 |
| household_person_keys | hhid | Unique HH Identifier | Agriculture SEC_1_ALL_Swahili_Labels | 27 |
| household_person_keys | hhid | Unique HH Identifier | SEC_2A_Swahili_Labels | 27 |
| household_person_keys | hhid | Unique HH Identifier | SEC_2B_Swahili_Labels | 27 |
| household_person_keys | hhid | Unique HH Identifier | SEC_B_C_D_E1_F_G1_U_English_Labels | 27 |
| household_person_keys | hhid | Unique HH Identifier | SEC_2A_English_Labels | 27 |
| household_person_keys | hhid | Unique HH Identifier | SEC_2B_English_Labels | 27 |
| household_person_keys | hhid | Unique HH Identifier | SEC_A_T_Swahili_Labels | 25 |
| household_person_keys | hhid | Unique HH Identifier | SEC_A_T_English_Labels | 25 |
| household_person_keys | rosterid | Namba ya Mwanakaya | Agriculture SEC_1_ALL_Swahili_Labels | 19 |
| household_person_keys | hhid | Unique HH Identifier | SEC_N_Swahili_Labels | 18 |
| household_person_keys | hhid | Unique HH Identifier | SEC_R_Swahili_Labels | 18 |
| weights_and_design | hh_weight | Household weight for national-level estimates | nps_weights_oct2010 | 27 |
| weights_and_design | hh_weight_trimmed | Household weight for national-level estimates, trimmed | nps_weights_oct2010 | 27 |
| weights_and_design | hh_weight | Household weight for national-level estimates | SEC_A_T_English_Labels | 27 |
| weights_and_design | hh_weight_trimmed | Household weight for national-level estimates, trimmed | SEC_A_T_English_Labels | 27 |

## Archive/Direct-File Requirement Preflight

| requirement | metadata_status | requirement_preflight_status |
|---|---|---|
| household_person_keys | not_found_in_public_metadata_raw_review_required | blocked_no_archive_or_direct_raw_evidence |
| weights_and_design | not_found_in_public_metadata_raw_review_required | blocked_no_archive_or_direct_raw_evidence |
| consumption_or_income | not_found_in_public_metadata_raw_review_required | blocked_no_archive_or_direct_raw_evidence |
| oop_health_expenditure | not_found_in_public_metadata_raw_review_required | blocked_no_archive_or_direct_raw_evidence |
| health_need_and_access | not_found_in_public_metadata_raw_review_required | blocked_no_archive_or_direct_raw_evidence |
| survey_timing | metadata_hit_raw_review_required | blocked_no_archive_or_direct_raw_evidence |
| climate_geography | not_found_in_public_metadata_raw_review_required | blocked_no_archive_or_direct_raw_evidence |
| missing_codes_units_recall_skip_patterns | raw_review_required | blocked_no_archive_or_direct_raw_evidence |

## Stop Rule

This packet is a promotion-control artifact, not an analysis dataset. Do not
write this country-wave into `data/` until the complete original raw package,
all raw value/key/unit/skip-pattern checks, outcome gates, and an accepted
CHIRPS or ERA5 linkage route pass.

Failed gates currently blocking promotion: 17.
