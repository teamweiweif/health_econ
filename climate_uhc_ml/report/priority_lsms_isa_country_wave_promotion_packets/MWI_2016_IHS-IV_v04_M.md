# Priority LSMS-ISA Country-Wave Promotion Packet

Dataset: `MWI_2016_IHS-IV_v04_M` - Malawi 2016-2017

Survey: Fourth Integrated Household Survey 2016-2017

Official get-microdata URL: https://microdata.worldbank.org/catalog/2936/get-microdata

Target raw folder: `temp/raw_downloads/MWI_2016_IHS-IV_v04_M/`

Current packet status: `blocked_fail_closed`

Analysis-ready status: `not_promoted`

Next blocking action: `download_or_place_complete_original_raw_package`

## Gate Matrix

| gate | status | evidence | required_action |
|---|---|---|---|
| official_public_documentation_receipt | pass | status=complete_core_public_documentation_receipt; saved=catalog_idno_json;data_dictionary_html;ddi_metadata;get_micr... |  |
| official_variable_evidence_coverage | pass | coverage_rows=8; matrix_rows=82; shortlist_rows=35; no_candidate_rows=0 |  |
| complete_original_raw_package | fail | intake_status=blocked_no_original_package; original_files=0; archives=0; raw_tabular=0; package_docs=0; public_docs=c... | Download/place the complete unchanged official raw package and all documentation in the target folder. |
| archive_or_direct_file_preflight | fail | status=blocked_no_original_archive_or_direct_files; direct_raw=0; direct_docs=0; archive_members=0 | Confirm readable archive/direct raw and documentation files before schema inspection. |
| raw_value_verification_household_person_keys | fail | metadata=official_metadata_strong_candidates_present_raw_review_required; candidates=12; files=12; raw_status=not_raw... | Verify this requirement against raw files, value labels, units, recall periods, skip patterns, and merge level. |
| raw_value_verification_weights_and_design | fail | metadata=official_metadata_strong_candidates_present_raw_review_required; candidates=12; files=12; raw_status=not_raw... | Verify this requirement against raw files, value labels, units, recall periods, skip patterns, and merge level. |
| raw_value_verification_consumption_or_income | fail | metadata=official_metadata_strong_candidates_present_raw_review_required; candidates=12; files=5; raw_status=not_raw_... | Verify this requirement against raw files, value labels, units, recall periods, skip patterns, and merge level. |
| raw_value_verification_oop_health_expenditure | fail | metadata=official_metadata_strong_candidates_present_raw_review_required; candidates=10; files=1; raw_status=not_raw_... | Verify this requirement against raw files, value labels, units, recall periods, skip patterns, and merge level. |
| raw_value_verification_health_need_and_access | fail | metadata=official_metadata_strong_candidates_present_raw_review_required; candidates=12; files=3; raw_status=not_raw_... | Verify this requirement against raw files, value labels, units, recall periods, skip patterns, and merge level. |
| raw_value_verification_survey_timing | fail | metadata=official_metadata_strong_candidates_present_raw_review_required; candidates=12; files=3; raw_status=not_raw_... | Verify this requirement against raw files, value labels, units, recall periods, skip patterns, and merge level. |
| raw_value_verification_climate_geography | fail | metadata=official_metadata_strong_candidates_present_raw_review_required; candidates=12; files=7; raw_status=not_raw_... | Verify this requirement against raw files, value labels, units, recall periods, skip patterns, and merge level. |
| raw_value_verification_missing_codes_units_recall_skip_patterns | fail | metadata=documentation_and_raw_review_required_no_variable_shortlist; candidates=0; files=0; raw_status=not_raw_value... | Verify this requirement against raw files, value labels, units, recall periods, skip patterns, and merge level. |
| all_required_raw_values_verified | fail | verified_requirement_rows=0/8 | Complete raw-backed verification for every required promotion requirement. |
| financial_protection_inputs_ready | fail | requires verified weights/design, total consumption or income, and OOP health expenditure. | Verify financial-protection inputs before CHE10/CHE25 or SDG 3.8.2 readiness can be claimed. |
| access_forgone_care_inputs_ready | fail | requires verified illness/need, care-seeking, and access-barrier raw variables. | Verify illness/need and care-seeking/access variables before double-failure readiness can be claimed. |
| timing_geography_ready_for_climate | fail | requires verified survey timing and GPS/cluster/EA/admin geography. | Verify timing and geography raw fields before accepting a climate linkage route. |
| accepted_chirps_or_era5_linkage_route | fail | accepted_route=missing; current_gate=missing; planned_level= | Accept a CHIRPS or ERA5 route only after timing/geography verification passes. |
| analysis_dataset_synthesis_ready | fail | join_status=missing; ready_columns=0; blocked_columns=0 | Complete promoted household-climate schema and join review. |
| promoted_registry_write_gate | fail | registry_analysis_ready=not_promoted; rows=0 | Write to data/ only when the promoted registry marks this country-wave as analysis-ready with nonzero rows. |

## Requirement Variable Evidence

| requirement | coverage_status | candidate_variable_rows | strong_candidate_variable_rows | raw_value_verification_status |
|---|---|---|---|---|
| household_person_keys | official_metadata_strong_candidates_present_raw_review_required | 12 | 12 | not_raw_value_verified |
| weights_and_design | official_metadata_strong_candidates_present_raw_review_required | 12 | 12 | not_raw_value_verified |
| consumption_or_income | official_metadata_strong_candidates_present_raw_review_required | 12 | 12 | not_raw_value_verified |
| oop_health_expenditure | official_metadata_strong_candidates_present_raw_review_required | 10 | 10 | not_raw_value_verified |
| health_need_and_access | official_metadata_strong_candidates_present_raw_review_required | 12 | 8 | not_raw_value_verified |
| survey_timing | official_metadata_strong_candidates_present_raw_review_required | 12 | 12 | not_raw_value_verified |
| climate_geography | official_metadata_strong_candidates_present_raw_review_required | 12 | 12 | not_raw_value_verified |
| missing_codes_units_recall_skip_patterns | documentation_and_raw_review_required_no_variable_shortlist | 0 | 0 | not_raw_value_verified |

## Official Public Documentation

| resource_type | receipt_status | saved_path |
|---|---|---|
| get_microdata_html | saved_existing | temp/source_snapshots/priority_lsms_isa_public_documentation/15_MWI_2016_IHS-IV_v04_M/get_microdata_html.html |
| catalog_idno_json | saved_existing | temp/source_snapshots/priority_lsms_isa_public_documentation/15_MWI_2016_IHS-IV_v04_M/catalog_idno_json.json |
| variables_idno_json | saved_existing | temp/source_snapshots/priority_lsms_isa_public_documentation/15_MWI_2016_IHS-IV_v04_M/variables_idno_json.json |
| ddi_metadata | saved_existing | temp/source_snapshots/priority_lsms_isa_public_documentation/15_MWI_2016_IHS-IV_v04_M/ddi_metadata.xml |
| json_metadata | saved_existing | temp/source_snapshots/priority_lsms_isa_public_documentation/15_MWI_2016_IHS-IV_v04_M/json_metadata.json |
| data_dictionary_html | saved_existing | temp/source_snapshots/priority_lsms_isa_public_documentation/15_MWI_2016_IHS-IV_v04_M/data_dictionary_html.html |
| related_materials_html | saved_existing | temp/source_snapshots/priority_lsms_isa_public_documentation/15_MWI_2016_IHS-IV_v04_M/related_materials_html.html |

## Concept File Shortlist

| requirement | file_name | candidate_variable_rows | top_variable_names |
|---|---|---|---|
| climate_geography | IHS4 Consumption Aggregate | 2 | ea_id;area |
| climate_geography | AG_MOD_J | 2 | ag_j06e;ag_j06e_oth |
| climate_geography | AG_MOD_B1 | 2 | ag_b105e;ag_b105e_oth |
| climate_geography | AG_MOD_I1 | 2 | ag_i106c;ag_i106c_oth |
| climate_geography | AG_MOD_O1 | 2 | ag_o105e;ag_o105e_oth |
| climate_geography | HH_MOD_A_FILT | 1 | ea_id |
| climate_geography | AG_MOD_C | 1 | ag_c05e |
| consumption_or_income | HH_MOD_I1 | 5 | case_id;hh_i01;hh_i02;hh_i03;HHID |
| consumption_or_income | HH_MOD_I2 | 3 | case_id;hh_i04;hh_i05 |
| consumption_or_income | HH_MOD_G1 | 2 | hh_g00_2;hh_g00_1 |
| consumption_or_income | HH_MOD_K1 | 1 | hh_k03 |
| consumption_or_income | HH_MOD_K2 | 1 | hh_k03 |
| health_need_and_access | HH_MOD_D | 7 | hh_d04;hh_d05_oth;hh_d34a;hh_d34b;hh_d11;hh_d13;hh_d14 |
| health_need_and_access | COM_CD | 4 | com_cd60a;com_cd53;com_cd54;com_cd51a |
| health_need_and_access | AG_MOD_D | 1 | ag_d25_2a |
| household_person_keys | HH_MOD_B | 1 | case_id |

## Candidate Variable Preview

| requirement | variable_name | variable_label | file_name | match_score |
|---|---|---|---|---|
| household_person_keys | case_id | Unique Household Identifier | HH_MOD_B | 37 |
| household_person_keys | case_id | Unique Household Identifier | AG_MOD_J | 35 |
| household_person_keys | case_id | Unique Household Identifier | AG_MOD_B1 | 35 |
| household_person_keys | case_id | Unique Household Identifier | AG_MOD_C | 35 |
| household_person_keys | case_id | Unique Household Identifier | AG_MOD_I1 | 35 |
| household_person_keys | case_id | Unique Household Identifier | AG_MOD_O1 | 35 |
| household_person_keys | case_id | Unique Household Identifier | AG_MOD_O2 | 35 |
| household_person_keys | case_id | Unique Household Identifier | HH_METADATA | 28 |
| household_person_keys | case_id | Unique Household Identifier | HH_MOD_G3 | 28 |
| household_person_keys | case_id | Unique Household Identifier | ag_mod_e3 | 28 |
| household_person_keys | case_id | Unique Household Identifier | HH_MOD_H | 28 |
| household_person_keys | case_id | Unique Household Identifier | HH_MOD_I1 | 28 |
| weights_and_design | ea_id | Unique Enumeration Area Code | HH_MOD_A_FILT | 29 |
| weights_and_design | ea_id | Unique Enumeration Area Code | IHS4 Consumption Aggregate | 27 |
| weights_and_design | ea_id | Unique EA Identifier | com_ch | 16 |
| weights_and_design | ea_id | Unique EA Identifier | COM_CA | 16 |

## Archive/Direct-File Requirement Preflight

| requirement | metadata_status | requirement_preflight_status |
|---|---|---|
| household_person_keys | metadata_hit_raw_review_required | blocked_no_archive_or_direct_raw_evidence |
| weights_and_design | metadata_hit_raw_review_required | blocked_no_archive_or_direct_raw_evidence |
| consumption_or_income | not_found_in_public_metadata_raw_review_required | blocked_no_archive_or_direct_raw_evidence |
| oop_health_expenditure | not_found_in_public_metadata_raw_review_required | blocked_no_archive_or_direct_raw_evidence |
| health_need_and_access | metadata_hit_raw_review_required | blocked_no_archive_or_direct_raw_evidence |
| survey_timing | metadata_hit_raw_review_required | blocked_no_archive_or_direct_raw_evidence |
| climate_geography | metadata_hit_raw_review_required | blocked_no_archive_or_direct_raw_evidence |
| missing_codes_units_recall_skip_patterns | raw_review_required | blocked_no_archive_or_direct_raw_evidence |

## Stop Rule

This packet is a promotion-control artifact, not an analysis dataset. Do not
write this country-wave into `data/` until the complete original raw package,
all raw value/key/unit/skip-pattern checks, outcome gates, and an accepted
CHIRPS or ERA5 linkage route pass.

Failed gates currently blocking promotion: 17.
