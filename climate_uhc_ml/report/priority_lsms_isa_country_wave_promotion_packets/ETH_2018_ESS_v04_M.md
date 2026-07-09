# Priority LSMS-ISA Country-Wave Promotion Packet

Dataset: `ETH_2018_ESS_v04_M` - Ethiopia 2018-2019

Survey: Socioeconomic Survey 2018-2019

Official get-microdata URL: https://microdata.worldbank.org/catalog/3823/get-microdata

Target raw folder: `temp/raw_downloads/ETH_2018_ESS_v04_M/`

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
| raw_value_verification_household_person_keys | fail | metadata=official_metadata_strong_candidates_present_raw_review_required; candidates=12; files=10; raw_status=not_raw... | Verify this requirement against raw files, value labels, units, recall periods, skip patterns, and merge level. |
| raw_value_verification_weights_and_design | fail | metadata=official_metadata_strong_candidates_present_raw_review_required; candidates=12; files=12; raw_status=not_raw... | Verify this requirement against raw files, value labels, units, recall periods, skip patterns, and merge level. |
| raw_value_verification_consumption_or_income | fail | metadata=official_metadata_strong_candidates_present_raw_review_required; candidates=12; files=2; raw_status=not_raw_... | Verify this requirement against raw files, value labels, units, recall periods, skip patterns, and merge level. |
| raw_value_verification_oop_health_expenditure | fail | metadata=official_metadata_strong_candidates_present_raw_review_required; candidates=12; files=2; raw_status=not_raw_... | Verify this requirement against raw files, value labels, units, recall periods, skip patterns, and merge level. |
| raw_value_verification_health_need_and_access | fail | metadata=official_metadata_strong_candidates_present_raw_review_required; candidates=12; files=2; raw_status=not_raw_... | Verify this requirement against raw files, value labels, units, recall periods, skip patterns, and merge level. |
| raw_value_verification_survey_timing | fail | metadata=official_metadata_strong_candidates_present_raw_review_required; candidates=12; files=7; raw_status=not_raw_... | Verify this requirement against raw files, value labels, units, recall periods, skip patterns, and merge level. |
| raw_value_verification_climate_geography | fail | metadata=official_metadata_strong_candidates_present_raw_review_required; candidates=12; files=6; raw_status=not_raw_... | Verify this requirement against raw files, value labels, units, recall periods, skip patterns, and merge level. |
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
| health_need_and_access | official_metadata_strong_candidates_present_raw_review_required | 12 | 12 | not_raw_value_verified |
| survey_timing | official_metadata_strong_candidates_present_raw_review_required | 12 | 9 | not_raw_value_verified |
| climate_geography | official_metadata_strong_candidates_present_raw_review_required | 12 | 12 | not_raw_value_verified |
| missing_codes_units_recall_skip_patterns | documentation_and_raw_review_required_no_variable_shortlist | 0 | 0 | not_raw_value_verified |

## Official Public Documentation

| resource_type | receipt_status | saved_path |
|---|---|---|
| get_microdata_html | saved_existing | temp/source_snapshots/priority_lsms_isa_public_documentation/2_ETH_2018_ESS_v04_M/get_microdata_html.html |
| catalog_idno_json | saved_existing | temp/source_snapshots/priority_lsms_isa_public_documentation/2_ETH_2018_ESS_v04_M/catalog_idno_json.json |
| variables_idno_json | saved_existing | temp/source_snapshots/priority_lsms_isa_public_documentation/2_ETH_2018_ESS_v04_M/variables_idno_json.json |
| ddi_metadata | saved_existing | temp/source_snapshots/priority_lsms_isa_public_documentation/2_ETH_2018_ESS_v04_M/ddi_metadata.xml |
| json_metadata | saved_existing | temp/source_snapshots/priority_lsms_isa_public_documentation/2_ETH_2018_ESS_v04_M/json_metadata.json |
| data_dictionary_html | saved_existing | temp/source_snapshots/priority_lsms_isa_public_documentation/2_ETH_2018_ESS_v04_M/data_dictionary_html.html |
| related_materials_html | saved_existing | temp/source_snapshots/priority_lsms_isa_public_documentation/2_ETH_2018_ESS_v04_M/related_materials_html.html |

## Concept File Shortlist

| requirement | file_name | candidate_variable_rows | top_variable_names |
|---|---|---|---|
| climate_geography | sect_cover_ph_w4.dta | 3 | saq19__Latitude;saq19__Longitude;ea_id |
| climate_geography | sect_cover_pp_w4.dta | 2 | saq19__Latitude;saq19__Longitude |
| climate_geography | sect_cover_ls_w4.dta | 2 | saq19__Latitude;saq19__Longitude |
| climate_geography | sect3_pp_w4.dta | 2 | s3q09__Latitude;s3q09__Longitude |
| climate_geography | sect10a_com_w4.dta | 2 | cs10q05__Latitude;cs10q05__Longitude |
| climate_geography | sect_cover_hh_w4.dta | 1 | ea_id |
| consumption_or_income | sect7a_hh_w4.dta | 9 | ea_id;household_id;item_cd_30day;pw_w4;s7q01;s7q02;saq01;saq02;saq03 |
| consumption_or_income | cons_agg_w4.dta | 3 | nom_nonfoodcons_aeq;nonfood_cons_ann;food_cons_ann |
| health_need_and_access | sect3_hh_w4.dta | 11 | s3q14;s3q15;s3q05;s3q17;s3q13;s3q18;s3q06_1;s3q06_2;s3q06_os;s3q09a;s3q09b |
| health_need_and_access | sect04_com_w4.dta | 1 | cs4q37 |
| household_person_keys | sect1_hh_w4.dta | 2 | individual_id;household_id |
| household_person_keys | sect11b1_hh_w4.dta | 2 | individual_id;household_id |
| household_person_keys | sect10d1_hh_w4.dta | 1 | household_id |
| household_person_keys | sect1_ph_w4.dta | 1 | household_id |
| household_person_keys | sect1_pp_w4.dta | 1 | household_id |
| household_person_keys | sect10b_hh_w4.dta | 1 | household_id |

## Candidate Variable Preview

| requirement | variable_name | variable_label | file_name | match_score |
|---|---|---|---|---|
| household_person_keys | individual_id | Household member ID | sect1_hh_w4.dta | 37 |
| household_person_keys | individual_id | Household member ID | sect11b1_hh_w4.dta | 35 |
| household_person_keys | household_id | Unique Household Indentifier | sect1_hh_w4.dta | 33 |
| household_person_keys | household_id | Unique Household Indentifier | sect10d1_hh_w4.dta | 33 |
| household_person_keys | household_id | Unique Household Indentifier | sect1_ph_w4.dta | 33 |
| household_person_keys | household_id | Unique Household Indentifier | sect1_pp_w4.dta | 33 |
| household_person_keys | household_id | Unique Household Indentifier | sect10b_hh_w4.dta | 31 |
| household_person_keys | household_id | Unique Household Indentifier | sect11b1_hh_w4.dta | 31 |
| household_person_keys | household_id | Unique Household Indentifier | sect2_pp_w4.dta | 31 |
| household_person_keys | household_id | Unique Household Indentifier | sect3_pp_w4.dta | 31 |
| household_person_keys | household_id | Unique Household Indentifier | sect4_pp_w4.dta | 31 |
| household_person_keys | household_id | Unique Household Indentifier | sect5_pp_w4.dta | 31 |
| weights_and_design | ea_id | Unique Enumeration Area Indentifier | sect_cover_hh_w4.dta | 31 |
| weights_and_design | ea_id | Unique Enumeration Area Indentifier | sect_cover_ph_w4.dta | 31 |
| weights_and_design | ea_id | Unique Enumeration Area Indentifier | sect_cover_pp_w4.dta | 31 |
| weights_and_design | ea_id | Unique Enumeration Area Indentifier | sect6b2_hh_w4.dta | 29 |

## Archive/Direct-File Requirement Preflight

| requirement | metadata_status | requirement_preflight_status |
|---|---|---|
| household_person_keys | metadata_hit_raw_review_required | blocked_no_archive_or_direct_raw_evidence |
| weights_and_design | metadata_hit_raw_review_required | blocked_no_archive_or_direct_raw_evidence |
| consumption_or_income | metadata_hit_raw_review_required | blocked_no_archive_or_direct_raw_evidence |
| oop_health_expenditure | metadata_weak_or_proxy_raw_review_required | blocked_no_archive_or_direct_raw_evidence |
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
