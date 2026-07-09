# Priority LSMS-ISA Country-Wave Promotion Packet

Dataset: `UGA_2015_UNPS_v02_M` - Uganda 2015-2016

Survey: National Panel Survey 2015-2016

Official get-microdata URL: https://microdata.worldbank.org/catalog/3460/get-microdata

Target raw folder: `temp/raw_downloads/UGA_2015_UNPS_v02_M/`

Current packet status: `blocked_fail_closed`

Analysis-ready status: `not_promoted`

Next blocking action: `download_or_place_complete_original_raw_package`

## Gate Matrix

| gate | status | evidence | required_action |
|---|---|---|---|
| official_public_documentation_receipt | pass | status=complete_core_public_documentation_receipt; saved=catalog_idno_json;data_dictionary_html;ddi_metadata;get_micr... |  |
| official_variable_evidence_coverage | pass | coverage_rows=8; matrix_rows=75; shortlist_rows=34; no_candidate_rows=0 |  |
| complete_original_raw_package | fail | intake_status=blocked_no_original_package; original_files=0; archives=0; raw_tabular=0; documentation=0 | Download/place the complete unchanged official raw package and all documentation in the target folder. |
| archive_or_direct_file_preflight | fail | status=blocked_no_original_archive_or_direct_files; direct_raw=0; direct_docs=0; archive_members=0 | Confirm readable archive/direct raw and documentation files before schema inspection. |
| raw_value_verification_household_person_keys | fail | metadata=official_metadata_strong_candidates_present_raw_review_required; candidates=12; files=12; raw_status=not_raw... | Verify this requirement against raw files, value labels, units, recall periods, skip patterns, and merge level. |
| raw_value_verification_weights_and_design | fail | metadata=official_metadata_strong_candidates_present_raw_review_required; candidates=12; files=4; raw_status=not_raw_... | Verify this requirement against raw files, value labels, units, recall periods, skip patterns, and merge level. |
| raw_value_verification_consumption_or_income | fail | metadata=official_metadata_strong_candidates_present_raw_review_required; candidates=12; files=3; raw_status=not_raw_... | Verify this requirement against raw files, value labels, units, recall periods, skip patterns, and merge level. |
| raw_value_verification_oop_health_expenditure | fail | metadata=official_metadata_strong_candidates_present_raw_review_required; candidates=3; files=2; raw_status=not_raw_v... | Verify this requirement against raw files, value labels, units, recall periods, skip patterns, and merge level. |
| raw_value_verification_health_need_and_access | fail | metadata=official_metadata_strong_candidates_present_raw_review_required; candidates=12; files=5; raw_status=not_raw_... | Verify this requirement against raw files, value labels, units, recall periods, skip patterns, and merge level. |
| raw_value_verification_survey_timing | fail | metadata=official_metadata_strong_candidates_present_raw_review_required; candidates=12; files=9; raw_status=not_raw_... | Verify this requirement against raw files, value labels, units, recall periods, skip patterns, and merge level. |
| raw_value_verification_climate_geography | fail | metadata=official_metadata_strong_candidates_present_raw_review_required; candidates=12; files=4; raw_status=not_raw_... | Verify this requirement against raw files, value labels, units, recall periods, skip patterns, and merge level. |
| raw_value_verification_missing_codes_units_recall_skip_patterns | fail | metadata=documentation_and_raw_review_required_no_variable_shortlist; candidates=0; files=0; raw_status=not_raw_value... | Verify this requirement against raw files, value labels, units, recall periods, skip patterns, and merge level. |
| all_required_raw_values_verified | fail | verified_requirement_rows=0/8 | Complete raw-backed verification for every required promotion requirement. |
| financial_protection_inputs_ready | fail | requires verified weights/design, total consumption or income, and OOP health expenditure. | Verify financial-protection inputs before CHE10/CHE25 or SDG 3.8.2 readiness can be claimed. |
| access_forgone_care_inputs_ready | fail | requires verified illness/need, care-seeking, and access-barrier raw variables. | Verify illness/need and care-seeking/access variables before double-failure readiness can be claimed. |
| timing_geography_ready_for_climate | fail | requires verified survey timing and GPS/cluster/EA/admin geography. | Verify timing and geography raw fields before accepting a climate linkage route. |
| accepted_chirps_or_era5_linkage_route | fail | accepted_route=missing; current_gate=missing; planned_level= | Accept a CHIRPS or ERA5 route only after timing/geography verification passes. |
| analysis_dataset_synthesis_ready | fail | join_status=missing; ready_columns=0; blocked_columns=0 | Complete promoted household-climate schema and join review. |
| promoted_registry_write_gate | fail | registry_analysis_ready=missing; rows=0 | Write to data/ only when the promoted registry marks this country-wave as analysis-ready with nonzero rows. |

## Requirement Variable Evidence

| requirement | coverage_status | candidate_variable_rows | strong_candidate_variable_rows | raw_value_verification_status |
|---|---|---|---|---|
| household_person_keys | official_metadata_strong_candidates_present_raw_review_required | 12 | 12 | not_raw_value_verified |
| weights_and_design | official_metadata_strong_candidates_present_raw_review_required | 12 | 3 | not_raw_value_verified |
| consumption_or_income | official_metadata_strong_candidates_present_raw_review_required | 12 | 7 | not_raw_value_verified |
| oop_health_expenditure | official_metadata_strong_candidates_present_raw_review_required | 3 | 1 | not_raw_value_verified |
| health_need_and_access | official_metadata_strong_candidates_present_raw_review_required | 12 | 12 | not_raw_value_verified |
| survey_timing | official_metadata_strong_candidates_present_raw_review_required | 12 | 8 | not_raw_value_verified |
| climate_geography | official_metadata_strong_candidates_present_raw_review_required | 12 | 11 | not_raw_value_verified |
| missing_codes_units_recall_skip_patterns | documentation_and_raw_review_required_no_variable_shortlist | 0 | 0 | not_raw_value_verified |

## Official Public Documentation

| resource_type | receipt_status | saved_path |
|---|---|---|
| get_microdata_html | saved_existing | temp/source_snapshots/priority_lsms_isa_public_documentation/19_UGA_2015_UNPS_v02_M/get_microdata_html.html |
| catalog_idno_json | saved_existing | temp/source_snapshots/priority_lsms_isa_public_documentation/19_UGA_2015_UNPS_v02_M/catalog_idno_json.json |
| variables_idno_json | saved_existing | temp/source_snapshots/priority_lsms_isa_public_documentation/19_UGA_2015_UNPS_v02_M/variables_idno_json.json |
| ddi_metadata | saved_existing | temp/source_snapshots/priority_lsms_isa_public_documentation/19_UGA_2015_UNPS_v02_M/ddi_metadata.xml |
| json_metadata | saved_existing | temp/source_snapshots/priority_lsms_isa_public_documentation/19_UGA_2015_UNPS_v02_M/json_metadata.json |
| data_dictionary_html | saved_existing | temp/source_snapshots/priority_lsms_isa_public_documentation/19_UGA_2015_UNPS_v02_M/data_dictionary_html.html |
| related_materials_html | saved_existing | temp/source_snapshots/priority_lsms_isa_public_documentation/19_UGA_2015_UNPS_v02_M/related_materials_html.html |

## Concept File Shortlist

| requirement | file_name | candidate_variable_rows | top_variable_names |
|---|---|---|---|
| climate_geography | AGSEC2B | 3 | GPS_Manual;GPS_Not_Captured;Visit_GPS_Parcel |
| climate_geography | gsec1 | 4 | urban;ea;sregion;h1aq5 |
| climate_geography | AGSEC1 | 3 | urban;sregion;h1aq5 |
| climate_geography | pov2015_16 | 2 | regurb;urban |
| consumption_or_income | pov2015_16 | 10 | cpexp30;nrrexp30;hpline;ctpline;spline;district;equiv;hh;hsize;plinen |
| consumption_or_income | AGSEC1 | 1 | interview |
| consumption_or_income | gsec1 | 1 | interview |
| health_need_and_access | gsec5 | 4 | h5q4;h5q5;h5q8;h5q9 |
| health_need_and_access | CSEC4B_1 | 3 | C4BQ23;C4BQ19;C4BQ20 |
| health_need_and_access | CSEC2B_1 | 2 | C2BQ10;C2BQ9 |
| health_need_and_access | CSEC4A_1 | 2 | C4AQ8;C4Q7 |
| health_need_and_access | CSEC4M | 1 | End_sup_health |
| household_person_keys | unps_geovars_2015_16 | 1 | HHID |
| household_person_keys | gsec2 | 1 | pid |
| household_person_keys | gsec3 | 1 | pid |
| household_person_keys | gsec4 | 1 | pid |

## Candidate Variable Preview

| requirement | variable_name | variable_label | file_name | match_score |
|---|---|---|---|---|
| household_person_keys | HHID | Household Identifier 2015/16 | unps_geovars_2015_16 | 27 |
| household_person_keys | pid | PERSON IDENTIFIER | gsec2 | 25 |
| household_person_keys | pid | PERSON IDENTIFIER | gsec3 | 25 |
| household_person_keys | pid | PERSON IDENTIFIER | gsec4 | 25 |
| household_person_keys | pid | PERSON IDENTIFIER | gsec5 | 25 |
| household_person_keys | pid | PERSON IDENTIFIER | gsec6_1 | 25 |
| household_person_keys | pid | PERSON IDENTIFIER | gsec6_3 | 25 |
| household_person_keys | pid | PERSON IDENTIFIER | gsec8 | 25 |
| household_person_keys | pid | PERSON IDENTIFIER | gsec15bb_3 | 25 |
| household_person_keys | PID | PERSON IDENTIFIER | WSEC1A | 23 |
| household_person_keys | PID | PERSON IDENTIFIER | WSEC2 | 23 |
| household_person_keys | PID | PERSON IDENTIFIER | WSEC3 | 23 |
| weights_and_design | ea | Enumeration area | gsec1 | 21 |
| weights_and_design | h1aq5 | Enumeration Area ( EA) | gsec1 | 17 |
| weights_and_design | h1aq5 | Enumeration Area ( EA) | AGSEC1 | 15 |
| weights_and_design | mult | Household weight | AGSEC1 | 11 |

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
