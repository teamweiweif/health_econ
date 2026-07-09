# Priority LSMS-ISA Country-Wave Promotion Packet

Dataset: `UGA_2011_UNPS_v02_M` - Uganda 2011-2012

Survey: National Panel Survey 2011-2012

Official get-microdata URL: https://microdata.worldbank.org/catalog/2059/get-microdata

Target raw folder: `temp/raw_downloads/UGA_2011_UNPS_v02_M/`

Current packet status: `blocked_fail_closed`

Analysis-ready status: `not_promoted`

Next blocking action: `download_or_place_complete_original_raw_package`

## Gate Matrix

| gate | status | evidence | required_action |
|---|---|---|---|
| official_public_documentation_receipt | pass | status=complete_core_public_documentation_receipt; saved=catalog_idno_json;data_dictionary_html;ddi_metadata;get_micr... |  |
| official_variable_evidence_coverage | pass | coverage_rows=8; matrix_rows=77; shortlist_rows=32; no_candidate_rows=0 |  |
| complete_original_raw_package | fail | intake_status=blocked_no_original_package; original_files=0; archives=0; raw_tabular=0; documentation=0 | Download/place the complete unchanged official raw package and all documentation in the target folder. |
| archive_or_direct_file_preflight | fail | status=blocked_no_original_archive_or_direct_files; direct_raw=0; direct_docs=0; archive_members=0 | Confirm readable archive/direct raw and documentation files before schema inspection. |
| raw_value_verification_household_person_keys | fail | metadata=official_metadata_strong_candidates_present_raw_review_required; candidates=12; files=11; raw_status=not_raw... | Verify this requirement against raw files, value labels, units, recall periods, skip patterns, and merge level. |
| raw_value_verification_weights_and_design | fail | metadata=official_metadata_weak_candidates_present_raw_review_required; candidates=12; files=4; raw_status=not_raw_va... | Verify this requirement against raw files, value labels, units, recall periods, skip patterns, and merge level. |
| raw_value_verification_consumption_or_income | fail | metadata=official_metadata_strong_candidates_present_raw_review_required; candidates=12; files=4; raw_status=not_raw_... | Verify this requirement against raw files, value labels, units, recall periods, skip patterns, and merge level. |
| raw_value_verification_oop_health_expenditure | fail | metadata=official_metadata_strong_candidates_present_raw_review_required; candidates=5; files=3; raw_status=not_raw_v... | Verify this requirement against raw files, value labels, units, recall periods, skip patterns, and merge level. |
| raw_value_verification_health_need_and_access | fail | metadata=official_metadata_strong_candidates_present_raw_review_required; candidates=12; files=9; raw_status=not_raw_... | Verify this requirement against raw files, value labels, units, recall periods, skip patterns, and merge level. |
| raw_value_verification_survey_timing | fail | metadata=official_metadata_strong_candidates_present_raw_review_required; candidates=12; files=4; raw_status=not_raw_... | Verify this requirement against raw files, value labels, units, recall periods, skip patterns, and merge level. |
| raw_value_verification_climate_geography | fail | metadata=official_metadata_strong_candidates_present_raw_review_required; candidates=12; files=1; raw_status=not_raw_... | Verify this requirement against raw files, value labels, units, recall periods, skip patterns, and merge level. |
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
| weights_and_design | official_metadata_weak_candidates_present_raw_review_required | 12 | 0 | not_raw_value_verified |
| consumption_or_income | official_metadata_strong_candidates_present_raw_review_required | 12 | 12 | not_raw_value_verified |
| oop_health_expenditure | official_metadata_strong_candidates_present_raw_review_required | 5 | 3 | not_raw_value_verified |
| health_need_and_access | official_metadata_strong_candidates_present_raw_review_required | 12 | 12 | not_raw_value_verified |
| survey_timing | official_metadata_strong_candidates_present_raw_review_required | 12 | 12 | not_raw_value_verified |
| climate_geography | official_metadata_strong_candidates_present_raw_review_required | 12 | 12 | not_raw_value_verified |
| missing_codes_units_recall_skip_patterns | documentation_and_raw_review_required_no_variable_shortlist | 0 | 0 | not_raw_value_verified |

## Official Public Documentation

| resource_type | receipt_status | saved_path |
|---|---|---|
| get_microdata_html | saved_existing | temp/source_snapshots/priority_lsms_isa_public_documentation/17_UGA_2011_UNPS_v02_M/get_microdata_html.html |
| catalog_idno_json | saved_existing | temp/source_snapshots/priority_lsms_isa_public_documentation/17_UGA_2011_UNPS_v02_M/catalog_idno_json.json |
| variables_idno_json | saved_existing | temp/source_snapshots/priority_lsms_isa_public_documentation/17_UGA_2011_UNPS_v02_M/variables_idno_json.json |
| ddi_metadata | saved_existing | temp/source_snapshots/priority_lsms_isa_public_documentation/17_UGA_2011_UNPS_v02_M/ddi_metadata.xml |
| json_metadata | saved_existing | temp/source_snapshots/priority_lsms_isa_public_documentation/17_UGA_2011_UNPS_v02_M/json_metadata.json |
| data_dictionary_html | saved_existing | temp/source_snapshots/priority_lsms_isa_public_documentation/17_UGA_2011_UNPS_v02_M/data_dictionary_html.html |
| related_materials_html | saved_existing | temp/source_snapshots/priority_lsms_isa_public_documentation/17_UGA_2011_UNPS_v02_M/related_materials_html.html |

## Concept File Shortlist

| requirement | file_name | candidate_variable_rows | top_variable_names |
|---|---|---|---|
| climate_geography | CSEC1.NSDstat | 12 | GPS_Manual_Health;cgpsdlg2;cgpsdlg3;cgpsdlg4;cgpsdlg5;cgpsdlt2;cgpsdlt3;cgpsdlt4;cgpsdlt5;cgpsmlg2_min;cgpsmlg2_sec;c... |
| consumption_or_income | GSEC15B.NSDstat | 8 | h15bq14;h15bq15;h15bq2d;h15bq3a;h15bq3b;h15bq4;h15bq5;itmcd |
| consumption_or_income | UNPS 2011-12 Consumption Aggregate.NSDstat | 2 | welfare;cpexp30 |
| consumption_or_income | GSEC15BB.NSDstat | 1 | h15bq14 |
| consumption_or_income | GSEC15C.NSDstat | 1 | h15cq2 |
| health_need_and_access | CSEC4l.NSDstat | 2 | c4lq102;c4lq102_other |
| health_need_and_access | CSEC2b.NSDstat | 2 | c2bq10;c2bq9 |
| health_need_and_access | CSEC4c.NSDstat | 2 | c4cq46;c4cq48 |
| health_need_and_access | CSEC4n.NSDstat | 1 | End_sup_health |
| health_need_and_access | CSEC4ab.NSDstat | 1 | c4bq23 |
| health_need_and_access | CSEC4d.NSDstat | 1 | End_Diseases |
| health_need_and_access | CSEC4e.NSDstat | 1 | c4e61 |
| health_need_and_access | CSEC4f.NSDstat | 1 | c4fq72 |
| household_person_keys | GSEC2.NSDstat | 2 | PID;HHID |
| household_person_keys | UNPS 2011-12 Consumption Aggregate.NSDstat | 1 | HHID |
| household_person_keys | GSEC1.NSDstat | 1 | HHID |

## Candidate Variable Preview

| requirement | variable_name | variable_label | file_name | match_score |
|---|---|---|---|---|
| household_person_keys | HHID | Unique Household Identifier Across Waves | UNPS 2011-12 Consumption Aggregate.NSDstat | 34 |
| household_person_keys | PID | PERSON IDENTIFIER | GSEC2.NSDstat | 34 |
| household_person_keys | HHID | HOUSEHOLD CODE | GSEC2.NSDstat | 27 |
| household_person_keys | HHID | Unique identifier in 2005/06 | GSEC1.NSDstat | 25 |
| household_person_keys | PID | PERSON IDENTIFIER | GSEC3.NSDstat | 25 |
| household_person_keys | PID | PERSON IDENTIFIER | GSEC4.NSDstat | 25 |
| household_person_keys | PID | PERSON IDENTIFIER | GSEC5.NSDstat | 25 |
| household_person_keys | PID | PERSON IDENTIFIER | GSEC6A.NSDstat | 25 |
| household_person_keys | PID | PERSON IDENTIFIER | GSEC6B.NSDstat | 25 |
| household_person_keys | PID | PERSON IDENTIFIER | GSEC6C.NSDstat | 25 |
| household_person_keys | PID | PERSON IDENTIFIER | GSEC8.NSDstat | 25 |
| household_person_keys | PID | PERSON IDENTIFIER | WSEC2B_1.NSDstat | 23 |
| weights_and_design | Weather_Condition | Weather Condition | AGSEC2B.NSDstat | 10 |
| weights_and_design | reason | Reason for not completing interview | GSEC1.NSDstat | 10 |
| weights_and_design | year | Year when the interview was completed | GSEC1.NSDstat | 10 |
| weights_and_design | Weather_Condition | Weather Condition | AGSEC2A.NSDstat | 8 |

## Archive/Direct-File Requirement Preflight

| requirement | metadata_status | requirement_preflight_status |
|---|---|---|
| household_person_keys | metadata_hit_raw_review_required | blocked_no_archive_or_direct_raw_evidence |
| weights_and_design | metadata_hit_raw_review_required | blocked_no_archive_or_direct_raw_evidence |
| consumption_or_income | metadata_hit_raw_review_required | blocked_no_archive_or_direct_raw_evidence |
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
