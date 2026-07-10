# Priority LSMS-ISA Country-Wave Promotion Packet

Dataset: `KGZ_1993_KMPS_v01_M` - Kyrgyz Republic 1993

Survey: Multipurpose Poverty Survey 1993

Official get-microdata URL: https://microdata.worldbank.org/catalog/280/get-microdata

Target raw folder: `temp/raw_downloads/KGZ_1993_KMPS_v01_M/`

Current packet status: `blocked_fail_closed`

Analysis-ready status: `not_promoted`

Next blocking action: `download_or_place_complete_original_raw_package`

## Gate Matrix

| gate | status | evidence | required_action |
|---|---|---|---|
| official_public_documentation_receipt | pass | status=complete_core_public_documentation_receipt; saved=catalog_idno_json;data_dictionary_html;ddi_metadata;get_micr... |  |
| official_variable_evidence_coverage | pass | coverage_rows=8; matrix_rows=84; shortlist_rows=31; no_candidate_rows=0 |  |
| complete_original_raw_package | fail | intake_status=blocked_no_original_package; original_files=0; archives=0; raw_tabular=0; package_docs=0; public_docs=c... | Download/place the complete unchanged official raw package and all documentation in the target folder. |
| archive_or_direct_file_preflight | fail | status=blocked_no_original_archive_or_direct_files; direct_raw=0; direct_docs=0; archive_members=0 | Confirm readable archive/direct raw and documentation files before schema inspection. |
| raw_value_verification_household_person_keys | fail | metadata=official_metadata_strong_candidates_present_raw_review_required; candidates=12; files=7; raw_status=not_raw_... | Verify this requirement against raw files, value labels, units, recall periods, skip patterns, and merge level. |
| raw_value_verification_weights_and_design | fail | metadata=official_metadata_strong_candidates_present_raw_review_required; candidates=12; files=2; raw_status=not_raw_... | Verify this requirement against raw files, value labels, units, recall periods, skip patterns, and merge level. |
| raw_value_verification_consumption_or_income | fail | metadata=official_metadata_strong_candidates_present_raw_review_required; candidates=12; files=3; raw_status=not_raw_... | Verify this requirement against raw files, value labels, units, recall periods, skip patterns, and merge level. |
| raw_value_verification_oop_health_expenditure | fail | metadata=official_metadata_strong_candidates_present_raw_review_required; candidates=12; files=4; raw_status=not_raw_... | Verify this requirement against raw files, value labels, units, recall periods, skip patterns, and merge level. |
| raw_value_verification_health_need_and_access | fail | metadata=official_metadata_weak_candidates_present_raw_review_required; candidates=12; files=4; raw_status=not_raw_va... | Verify this requirement against raw files, value labels, units, recall periods, skip patterns, and merge level. |
| raw_value_verification_survey_timing | fail | metadata=official_metadata_strong_candidates_present_raw_review_required; candidates=12; files=6; raw_status=not_raw_... | Verify this requirement against raw files, value labels, units, recall periods, skip patterns, and merge level. |
| raw_value_verification_climate_geography | fail | metadata=official_metadata_strong_candidates_present_raw_review_required; candidates=12; files=5; raw_status=not_raw_... | Verify this requirement against raw files, value labels, units, recall periods, skip patterns, and merge level. |
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
| weights_and_design | official_metadata_strong_candidates_present_raw_review_required | 12 | 1 | not_raw_value_verified |
| consumption_or_income | official_metadata_strong_candidates_present_raw_review_required | 12 | 4 | not_raw_value_verified |
| oop_health_expenditure | official_metadata_strong_candidates_present_raw_review_required | 12 | 4 | not_raw_value_verified |
| health_need_and_access | official_metadata_weak_candidates_present_raw_review_required | 12 | 0 | not_raw_value_verified |
| survey_timing | official_metadata_strong_candidates_present_raw_review_required | 12 | 8 | not_raw_value_verified |
| climate_geography | official_metadata_strong_candidates_present_raw_review_required | 12 | 1 | not_raw_value_verified |
| missing_codes_units_recall_skip_patterns | documentation_and_raw_review_required_no_variable_shortlist | 0 | 0 | not_raw_value_verified |

## Official Public Documentation

| resource_type | receipt_status | saved_path |
|---|---|---|
| get_microdata_html | saved_existing | temp/source_snapshots/priority_lsms_isa_public_documentation/12_KGZ_1993_KMPS_v01_M/get_microdata_html.html |
| catalog_idno_json | saved_existing | temp/source_snapshots/priority_lsms_isa_public_documentation/12_KGZ_1993_KMPS_v01_M/catalog_idno_json.json |
| variables_idno_json | saved_existing | temp/source_snapshots/priority_lsms_isa_public_documentation/12_KGZ_1993_KMPS_v01_M/variables_idno_json.json |
| ddi_metadata | saved_existing | temp/source_snapshots/priority_lsms_isa_public_documentation/12_KGZ_1993_KMPS_v01_M/ddi_metadata.xml |
| json_metadata | saved_existing | temp/source_snapshots/priority_lsms_isa_public_documentation/12_KGZ_1993_KMPS_v01_M/json_metadata.json |
| data_dictionary_html | saved_existing | temp/source_snapshots/priority_lsms_isa_public_documentation/12_KGZ_1993_KMPS_v01_M/data_dictionary_html.html |
| related_materials_html | saved_existing | temp/source_snapshots/priority_lsms_isa_public_documentation/12_KGZ_1993_KMPS_v01_M/related_materials_html.html |

## Concept File Shortlist

| requirement | file_name | candidate_variable_rows | top_variable_names |
|---|---|---|---|
| climate_geography | KPRICE2 | 5 | aye1_12a;aye1_12b;aye1_12c;aye1_12d;aye1_12e |
| climate_geography | KHHLD | 4 | ae2_1a;ae2_1b;ae3_1a;ae3_1b |
| climate_geography | KPRICE3 | 1 | ayeaid |
| climate_geography | CORE | 1 | region |
| climate_geography | CONADULT | 1 | hhead |
| consumption_or_income | INCEXP | 9 | khomcx;khomcy;kfoodx;khousex;kotherx;kothery;kothousx;kselfemy;ktothhy |
| consumption_or_income | KHHLD | 2 | ad141_1d;ad141_2d |
| consumption_or_income | KADULT | 1 | a1o16 |
| health_need_and_access | KYGPOV | 8 | hcsblne;lcsblne;poor3e;poor4e;rhcsblne;rlcsblne;rpoor3e;rpoor4e |
| health_need_and_access | KADULT | 2 | a1l16;a1j98 |
| health_need_and_access | INCEXP | 1 | khealthx |
| health_need_and_access | KCHILD | 1 | a1l16 |
| household_person_keys | KINDIVH | 4 | hid;pid;ab10_9_1;ab10_9_2 |
| household_person_keys | KADIET | 2 | pid;hhid |
| household_person_keys | KCHDIET | 2 | pid;hhid |
| household_person_keys | KINDIV | 1 | pid |

## Candidate Variable Preview

| requirement | variable_name | variable_label | file_name | match_score |
|---|---|---|---|---|
| household_person_keys | hid | Household ID | KINDIVH | 22 |
| household_person_keys | pid | Individual ID | KINDIV | 21 |
| household_person_keys | pid | position on household roster | CONADULT | 19 |
| household_person_keys | pid |  | KINDIVH | 19 |
| household_person_keys | pid | Individual ID | KADIET | 19 |
| household_person_keys | pid | Individual ID | KADULT | 19 |
| household_person_keys | pid | Individual ID | KCHDIET | 19 |
| household_person_keys | pid | Individual ID | KCHILD | 19 |
| household_person_keys | hhid |  | KADIET | 16 |
| household_person_keys | hhid |  | KCHDIET | 16 |
| household_person_keys | ab10_9_1 | RELATION TO HH MEMBER #1 | KINDIVH | 15 |
| household_person_keys | ab10_9_2 | RELATION TO HH MEMBER #2 | KINDIVH | 15 |
| weights_and_design | ayeaid |  | KPRICE3 | 16 |
| weights_and_design | hhead | household head status | CONADULT | 8 |
| weights_and_design | ayea_10a | CHOCOLATE PRIV BREAD LOW AVAILA | KPRICE3 | 8 |
| weights_and_design | ayea_10b | CHOCOLATE PRIV BREAD LOW PRICE? | KPRICE3 | 8 |

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
