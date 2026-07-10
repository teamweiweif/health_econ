# Priority LSMS-ISA Country-Wave Promotion Packet

Dataset: `MWI_2010_IHS-III_v01_M` - Malawi 2010-2011

Survey: Third Integrated Household Survey 2010-2011

Official get-microdata URL: https://microdata.worldbank.org/catalog/1003/get-microdata

Target raw folder: `temp/raw_downloads/MWI_2010_IHS-III_v01_M/`

Current packet status: `blocked_fail_closed`

Analysis-ready status: `not_promoted`

Next blocking action: `download_or_place_complete_original_raw_package`

## Gate Matrix

| gate | status | evidence | required_action |
|---|---|---|---|
| official_public_documentation_receipt | pass | status=complete_core_public_documentation_receipt; saved=catalog_idno_json;data_dictionary_html;ddi_metadata;get_micr... |  |
| official_variable_evidence_coverage | pass | coverage_rows=8; matrix_rows=77; shortlist_rows=36; no_candidate_rows=0 |  |
| complete_original_raw_package | fail | intake_status=blocked_no_original_package; original_files=0; archives=0; raw_tabular=0; package_docs=0; public_docs=c... | Download/place the complete unchanged official raw package and all documentation in the target folder. |
| archive_or_direct_file_preflight | fail | status=blocked_no_original_archive_or_direct_files; direct_raw=0; direct_docs=0; archive_members=0 | Confirm readable archive/direct raw and documentation files before schema inspection. |
| raw_value_verification_household_person_keys | fail | metadata=official_metadata_strong_candidates_present_raw_review_required; candidates=12; files=12; raw_status=not_raw... | Verify this requirement against raw files, value labels, units, recall periods, skip patterns, and merge level. |
| raw_value_verification_weights_and_design | fail | metadata=official_metadata_strong_candidates_present_raw_review_required; candidates=12; files=11; raw_status=not_raw... | Verify this requirement against raw files, value labels, units, recall periods, skip patterns, and merge level. |
| raw_value_verification_consumption_or_income | fail | metadata=official_metadata_strong_candidates_present_raw_review_required; candidates=12; files=3; raw_status=not_raw_... | Verify this requirement against raw files, value labels, units, recall periods, skip patterns, and merge level. |
| raw_value_verification_oop_health_expenditure | fail | metadata=official_metadata_strong_candidates_present_raw_review_required; candidates=5; files=1; raw_status=not_raw_v... | Verify this requirement against raw files, value labels, units, recall periods, skip patterns, and merge level. |
| raw_value_verification_health_need_and_access | fail | metadata=official_metadata_strong_candidates_present_raw_review_required; candidates=12; files=2; raw_status=not_raw_... | Verify this requirement against raw files, value labels, units, recall periods, skip patterns, and merge level. |
| raw_value_verification_survey_timing | fail | metadata=official_metadata_strong_candidates_present_raw_review_required; candidates=12; files=6; raw_status=not_raw_... | Verify this requirement against raw files, value labels, units, recall periods, skip patterns, and merge level. |
| raw_value_verification_climate_geography | fail | metadata=official_metadata_strong_candidates_present_raw_review_required; candidates=12; files=10; raw_status=not_raw... | Verify this requirement against raw files, value labels, units, recall periods, skip patterns, and merge level. |
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
| oop_health_expenditure | official_metadata_strong_candidates_present_raw_review_required | 5 | 4 | not_raw_value_verified |
| health_need_and_access | official_metadata_strong_candidates_present_raw_review_required | 12 | 11 | not_raw_value_verified |
| survey_timing | official_metadata_strong_candidates_present_raw_review_required | 12 | 12 | not_raw_value_verified |
| climate_geography | official_metadata_strong_candidates_present_raw_review_required | 12 | 12 | not_raw_value_verified |
| missing_codes_units_recall_skip_patterns | documentation_and_raw_review_required_no_variable_shortlist | 0 | 0 | not_raw_value_verified |

## Official Public Documentation

| resource_type | receipt_status | saved_path |
|---|---|---|
| get_microdata_html | saved_existing | temp/source_snapshots/priority_lsms_isa_public_documentation/16_MWI_2010_IHS-III_v01_M/get_microdata_html.html |
| catalog_idno_json | saved_existing | temp/source_snapshots/priority_lsms_isa_public_documentation/16_MWI_2010_IHS-III_v01_M/catalog_idno_json.json |
| variables_idno_json | saved_existing | temp/source_snapshots/priority_lsms_isa_public_documentation/16_MWI_2010_IHS-III_v01_M/variables_idno_json.json |
| ddi_metadata | saved_existing | temp/source_snapshots/priority_lsms_isa_public_documentation/16_MWI_2010_IHS-III_v01_M/ddi_metadata.xml |
| json_metadata | saved_existing | temp/source_snapshots/priority_lsms_isa_public_documentation/16_MWI_2010_IHS-III_v01_M/json_metadata.json |
| data_dictionary_html | saved_existing | temp/source_snapshots/priority_lsms_isa_public_documentation/16_MWI_2010_IHS-III_v01_M/data_dictionary_html.html |
| related_materials_html | saved_existing | temp/source_snapshots/priority_lsms_isa_public_documentation/16_MWI_2010_IHS-III_v01_M/related_materials_html.html |

## Concept File Shortlist

| requirement | file_name | candidate_variable_rows | top_variable_names |
|---|---|---|---|
| climate_geography | HouseholdGeovariables.NSDstat | 3 | ea_id;lat_modified;lon_modified |
| climate_geography | PlotGeovariables.NSDstat | 1 | ea_id |
| climate_geography | HH_MOD_A_FILT.NSDstat | 1 | ea_id |
| climate_geography | HH_MOD_H.NSDstat | 1 | ea_id |
| climate_geography | HH_MOD_I1.NSDstat | 1 | ea_id |
| climate_geography | HH_MOD_I2.NSDstat | 1 | ea_id |
| climate_geography | HH_MOD_J.NSDstat | 1 | ea_id |
| climate_geography | HH_MOD_K.NSDstat | 1 | ea_id |
| consumption_or_income | Round 1 (2010) Consumption Aggregate.NSDstat | 7 | rexp_cat01;rexp_cat011;epoor;pcrexpagg;poor;rexp_cat012;rexp_cat02 |
| consumption_or_income | ihs3fc2M_consumption.NSDstat | 4 | exp_cat01;exp_cat011;rexp_cat01;rexp_cat011 |
| consumption_or_income | HH_MOD_T.NSDstat | 1 | hh_t01 |
| health_need_and_access | COM_CD.NSDstat | 6 | com_cd60a;com_cd60b;com_cd53;com_cd54;com_cd51a;com_cd51b |
| health_need_and_access | HH_MOD_D.NSDstat | 6 | hh_d04;hh_d05a;hh_d05a_os;hh_d05b;hh_d05b_os;hh_d34a |
| household_person_keys | HouseholdGeovariables.NSDstat | 1 | case_id |
| household_person_keys | HH_MOD_A_FILT.NSDstat | 1 | case_id |
| household_person_keys | HH_MOD_H.NSDstat | 1 | case_id |

## Candidate Variable Preview

| requirement | variable_name | variable_label | file_name | match_score |
|---|---|---|---|---|
| household_person_keys | case_id | Unique HH Identifier | HouseholdGeovariables.NSDstat | 18 |
| household_person_keys | case_id | Unique HH Identifier | HH_MOD_A_FILT.NSDstat | 16 |
| household_person_keys | case_id | Unique HH Identifier | HH_MOD_H.NSDstat | 16 |
| household_person_keys | case_id | Unique HH Identifier | HH_MOD_I1.NSDstat | 16 |
| household_person_keys | case_id | Unique HH Identifier | HH_MOD_I2.NSDstat | 16 |
| household_person_keys | case_id | Unique HH Identifier | HH_MOD_J.NSDstat | 16 |
| household_person_keys | case_id | Unique HH Identifier | HH_MOD_K.NSDstat | 16 |
| household_person_keys | case_id | Unique HH Identifier | HH_MOD_L.NSDstat | 16 |
| household_person_keys | case_id | Unique HH Identifier | HH_MOD_M.NSDstat | 16 |
| household_person_keys | case_id | Unique HH Identifier | HH_MOD_N1.NSDstat | 16 |
| household_person_keys | case_id | Unique HH Identifier | HH_MOD_N2.NSDstat | 16 |
| household_person_keys | case_id | Unique HH Identifier | HH_MOD_O.NSDstat | 16 |
| weights_and_design | hhweight | Baseline Sampling Weight | Round 1 (2010) Consumption Aggregate.NSDstat | 25 |
| weights_and_design | strata | Baseline Stratum - Region x Urban/Rural | Round 1 (2010) Consumption Aggregate.NSDstat | 19 |
| weights_and_design | ea_id | Unique EA Identifier | HouseholdGeovariables.NSDstat | 18 |
| weights_and_design | ea_id | Unique EA Identifier | HH_MOD_A_FILT.NSDstat | 16 |

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
