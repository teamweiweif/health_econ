# Priority LSMS-ISA Country-Wave Promotion Packet

Dataset: `MWI_2004_IHS-II_v01_M` - Malawi 2004-2005

Survey: Second Integrated Household Survey 2004-2005

Official get-microdata URL: https://microdata.worldbank.org/catalog/2307/get-microdata

Target raw folder: `temp/raw_downloads/MWI_2004_IHS-II_v01_M/`

Current packet status: `blocked_fail_closed`

Analysis-ready status: `not_promoted`

Next blocking action: `download_or_place_complete_original_raw_package`

## Gate Matrix

| gate | status | evidence | required_action |
|---|---|---|---|
| official_public_documentation_receipt | pass | status=complete_core_public_documentation_receipt; saved=catalog_idno_json;data_dictionary_html;ddi_metadata;get_micr... |  |
| official_variable_evidence_coverage | pass | coverage_rows=8; matrix_rows=84; shortlist_rows=37; no_candidate_rows=0 |  |
| complete_original_raw_package | fail | intake_status=blocked_no_original_package; original_files=0; archives=0; raw_tabular=0; documentation=0 | Download/place the complete unchanged official raw package and all documentation in the target folder. |
| archive_or_direct_file_preflight | fail | status=blocked_no_original_archive_or_direct_files; direct_raw=0; direct_docs=0; archive_members=0 | Confirm readable archive/direct raw and documentation files before schema inspection. |
| raw_value_verification_household_person_keys | fail | metadata=official_metadata_strong_candidates_present_raw_review_required; candidates=12; files=12; raw_status=not_raw... | Verify this requirement against raw files, value labels, units, recall periods, skip patterns, and merge level. |
| raw_value_verification_weights_and_design | fail | metadata=official_metadata_strong_candidates_present_raw_review_required; candidates=12; files=12; raw_status=not_raw... | Verify this requirement against raw files, value labels, units, recall periods, skip patterns, and merge level. |
| raw_value_verification_consumption_or_income | fail | metadata=official_metadata_strong_candidates_present_raw_review_required; candidates=12; files=3; raw_status=not_raw_... | Verify this requirement against raw files, value labels, units, recall periods, skip patterns, and merge level. |
| raw_value_verification_oop_health_expenditure | fail | metadata=official_metadata_strong_candidates_present_raw_review_required; candidates=12; files=1; raw_status=not_raw_... | Verify this requirement against raw files, value labels, units, recall periods, skip patterns, and merge level. |
| raw_value_verification_health_need_and_access | fail | metadata=official_metadata_strong_candidates_present_raw_review_required; candidates=12; files=2; raw_status=not_raw_... | Verify this requirement against raw files, value labels, units, recall periods, skip patterns, and merge level. |
| raw_value_verification_survey_timing | fail | metadata=official_metadata_strong_candidates_present_raw_review_required; candidates=12; files=7; raw_status=not_raw_... | Verify this requirement against raw files, value labels, units, recall periods, skip patterns, and merge level. |
| raw_value_verification_climate_geography | fail | metadata=official_metadata_strong_candidates_present_raw_review_required; candidates=12; files=12; raw_status=not_raw... | Verify this requirement against raw files, value labels, units, recall periods, skip patterns, and merge level. |
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
| oop_health_expenditure | official_metadata_strong_candidates_present_raw_review_required | 12 | 5 | not_raw_value_verified |
| health_need_and_access | official_metadata_strong_candidates_present_raw_review_required | 12 | 8 | not_raw_value_verified |
| survey_timing | official_metadata_strong_candidates_present_raw_review_required | 12 | 4 | not_raw_value_verified |
| climate_geography | official_metadata_strong_candidates_present_raw_review_required | 12 | 12 | not_raw_value_verified |
| missing_codes_units_recall_skip_patterns | documentation_and_raw_review_required_no_variable_shortlist | 0 | 0 | not_raw_value_verified |

## Official Public Documentation

| resource_type | receipt_status | saved_path |
|---|---|---|
| get_microdata_html | saved_existing | temp/source_snapshots/priority_lsms_isa_public_documentation/3_MWI_2004_IHS-II_v01_M/get_microdata_html.html |
| catalog_idno_json | saved_existing | temp/source_snapshots/priority_lsms_isa_public_documentation/3_MWI_2004_IHS-II_v01_M/catalog_idno_json.json |
| variables_idno_json | saved_existing | temp/source_snapshots/priority_lsms_isa_public_documentation/3_MWI_2004_IHS-II_v01_M/variables_idno_json.json |
| ddi_metadata | saved_existing | temp/source_snapshots/priority_lsms_isa_public_documentation/3_MWI_2004_IHS-II_v01_M/ddi_metadata.xml |
| json_metadata | saved_existing | temp/source_snapshots/priority_lsms_isa_public_documentation/3_MWI_2004_IHS-II_v01_M/json_metadata.json |
| data_dictionary_html | saved_existing | temp/source_snapshots/priority_lsms_isa_public_documentation/3_MWI_2004_IHS-II_v01_M/data_dictionary_html.html |
| related_materials_html | saved_existing | temp/source_snapshots/priority_lsms_isa_public_documentation/3_MWI_2004_IHS-II_v01_M/related_materials_html.html |

## Concept File Shortlist

| requirement | file_name | candidate_variable_rows | top_variable_names |
|---|---|---|---|
| climate_geography | sec_a.NSDstat | 1 | type |
| climate_geography | sec_f.NSDstat | 1 | type |
| climate_geography | sec_g.NSDstat | 1 | type |
| climate_geography | sec_h.NSDstat | 1 | type |
| climate_geography | sec_i.NSDstat | 1 | type |
| climate_geography | sec_j1.NSDstat | 1 | type |
| climate_geography | sec_j2.NSDstat | 1 | type |
| climate_geography | sec_k.NSDstat | 1 | type |
| consumption_or_income | sec_j1.NSDstat | 10 | add;case_id;dist;ea;hhid;hhsize;hhwght;j01a;j02a;j03a |
| consumption_or_income | sec_i.NSDstat | 1 | i03both |
| consumption_or_income | sec_aa.NSDstat | 1 | aa01 |
| health_need_and_access | sec_d.NSDstat | 7 | d05a;d05aoth;d05b;d05both;d27a;d27b;d04 |
| health_need_and_access | mod_d.NSDstat | 5 | cd51b;cd_51a;cd47;cd57a;cd_50 |
| household_person_keys | sec_b.NSDstat | 1 | hhid |
| household_person_keys | sec_a.NSDstat | 1 | hhid |
| household_person_keys | sec_f.NSDstat | 1 | hhid |

## Candidate Variable Preview

| requirement | variable_name | variable_label | file_name | match_score |
|---|---|---|---|---|
| household_person_keys | hhid | Household ID | sec_b.NSDstat | 38 |
| household_person_keys | hhid | Household ID | sec_a.NSDstat | 29 |
| household_person_keys | hhid | Household ID | sec_f.NSDstat | 29 |
| household_person_keys | hhid | Household ID | sec_g.NSDstat | 29 |
| household_person_keys | hhid | Household ID | sec_h.NSDstat | 29 |
| household_person_keys | hhid | Household ID | sec_i.NSDstat | 29 |
| household_person_keys | hhid | Household ID | sec_j1.NSDstat | 29 |
| household_person_keys | hhid | Household ID | sec_j2.NSDstat | 29 |
| household_person_keys | hhid | Household ID | sec_k.NSDstat | 29 |
| household_person_keys | hhid | Household ID | sec_l.NSDstat | 29 |
| household_person_keys | hhid | Household ID | sec_m1.NSDstat | 29 |
| household_person_keys | hhid | Household ID | sec_m2.NSDstat | 29 |
| weights_and_design | psu | Enumeration Area/PSU (564 total) | sec_a.NSDstat | 25 |
| weights_and_design | psu | Enumeration Area/PSU (564 total) | sec_f.NSDstat | 25 |
| weights_and_design | psu | Enumeration Area/PSU (564 total) | sec_g.NSDstat | 25 |
| weights_and_design | psu | Enumeration Area/PSU (564 total) | sec_h.NSDstat | 25 |

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
