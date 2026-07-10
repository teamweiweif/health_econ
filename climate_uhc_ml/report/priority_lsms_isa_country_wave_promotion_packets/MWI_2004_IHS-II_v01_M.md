# Priority LSMS-ISA Country-Wave Promotion Packet

Dataset: `MWI_2004_IHS-II_v01_M` - Malawi 2004-2005

Survey: Second Integrated Household Survey 2004-2005

Official get-microdata URL: https://microdata.worldbank.org/catalog/2307/get-microdata

Target raw folder: `temp/raw_downloads/MWI_2004_IHS-II_v01_M/`

Current packet status: `blocked_fail_closed`

Analysis-ready status: `not_promoted`

Next blocking action: `complete_analysis_dataset_synthesis_join_review`

## Gate Matrix

| gate | status | evidence | required_action |
|---|---|---|---|
| official_public_documentation_receipt | pass | status=complete_core_public_documentation_receipt; saved=catalog_idno_json;data_dictionary_html;ddi_metadata;get_micr... |  |
| official_variable_evidence_coverage | pass | coverage_rows=8; matrix_rows=84; shortlist_rows=37; no_candidate_rows=0 |  |
| complete_original_raw_package | pass | intake_status=blocked_missing_documentation; original_files=1; archives=1; raw_tabular=0; package_docs=0; public_docs... |  |
| archive_or_direct_file_preflight | pass | status=ready_for_raw_receipt_schema_and_manual_review; direct_raw=0; direct_docs=0; archive_members=52 |  |
| raw_value_verification_household_person_keys | pass | metadata=official_metadata_strong_candidates_present_raw_review_required; candidates=12; files=12; raw_status=not_raw... |  |
| raw_value_verification_weights_and_design | pass | metadata=official_metadata_strong_candidates_present_raw_review_required; candidates=12; files=12; raw_status=not_raw... |  |
| raw_value_verification_consumption_or_income | pass | metadata=official_metadata_strong_candidates_present_raw_review_required; candidates=12; files=3; raw_status=not_raw_... |  |
| raw_value_verification_oop_health_expenditure | pass | metadata=official_metadata_strong_candidates_present_raw_review_required; candidates=12; files=1; raw_status=not_raw_... |  |
| raw_value_verification_health_need_and_access | pass | metadata=official_metadata_strong_candidates_present_raw_review_required; candidates=12; files=2; raw_status=not_raw_... |  |
| raw_value_verification_survey_timing | pass | metadata=official_metadata_strong_candidates_present_raw_review_required; candidates=12; files=7; raw_status=not_raw_... |  |
| raw_value_verification_climate_geography | pass | metadata=official_metadata_strong_candidates_present_raw_review_required; candidates=12; files=12; raw_status=not_raw... |  |
| raw_value_verification_missing_codes_units_recall_skip_patterns | pass | metadata=documentation_and_raw_review_required_no_variable_shortlist; candidates=0; files=0; raw_status=not_raw_value... |  |
| all_required_raw_values_verified | pass | verified_requirement_rows=8/8 |  |
| financial_protection_inputs_ready | pass | requires verified weights/design, total consumption or income, and OOP health expenditure. |  |
| access_forgone_care_inputs_ready | pass | requires verified illness/need, care-seeking, and access-barrier raw variables. |  |
| timing_geography_ready_for_climate | pass | requires verified survey timing and GPS/cluster/EA/admin geography. |  |
| accepted_chirps_or_era5_linkage_route | pass | accepted_route=accepted_chirps_admin2_extraction_validated; current_gate=accepted_chirps_admin2_extraction_validated;... |  |
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
| household_person_keys | metadata_hit_raw_review_required | ready_for_schema_and_manual_requirement_review |
| weights_and_design | metadata_hit_raw_review_required | ready_for_schema_and_manual_requirement_review |
| consumption_or_income | metadata_hit_raw_review_required | ready_for_schema_and_manual_requirement_review |
| oop_health_expenditure | metadata_weak_or_proxy_raw_review_required | ready_for_schema_and_manual_requirement_review |
| health_need_and_access | metadata_hit_raw_review_required | ready_for_schema_and_manual_requirement_review |
| survey_timing | metadata_hit_raw_review_required | ready_for_schema_and_manual_requirement_review |
| climate_geography | metadata_hit_raw_review_required | ready_for_schema_and_manual_requirement_review |
| missing_codes_units_recall_skip_patterns | raw_review_required | ready_for_schema_and_manual_requirement_review |

## Focused Raw Acceptance Decisions

| requirement | mechanical_raw_check_decision | final_verification_decision | remaining_blocker |
|---|---|---|---|
| household_person_keys | raw_value_verified_access_person_key_exclusion_policy_accepted | raw_value_verified_for_access_person_universe_with_documented_exclusions | Accepted for the stated access person-universe scope only; raw IDs are not exported and no access outcomes are impute... |
| weights_and_design | raw_value_verified_financial_policy_accepted | raw_value_verified_for_che10_che25 | Household financial survey design is accepted for CHE10/CHE25; recheck person-level design and cross-country modeling... |
| consumption_or_income | raw_value_verified_che_denominator_sdg_policy_blocked | raw_value_verified_for_che10_che25 | rexpagg is accepted as CHE10/CHE25 total-budget denominator; SDG 3.8.2 societal poverty-line/discretionary-budget map... |
| oop_health_expenditure | raw_value_verified_oop_aggregate_policy_accepted | raw_value_verified_for_che10_che25 | rexp_cat06 is accepted as annual household health OOP aggregate for CHE10/CHE25; health-module recall spending remain... |
| health_need_and_access | raw_value_verified_access_person_key_policy_accepted | raw_value_verified_for_cost_barrier_forgone_care | Cost-barrier forgone care is accepted only for roster-matched d04==Yes rows with documented exclusions; distance/supp... |
| survey_timing | raw_value_verified_interview_month_policy_accepted | raw_value_verified_for_climate_timing | Interview-month timing is accepted for climate-window review; climate values still require an accepted CHIRPS/ERA5 ro... |
| climate_geography | raw_value_verified_admin_ea_geography_route_blocked | raw_value_verified_for_admin_ea_geography | Raw admin/EA geography is accepted, but CHIRPS/ERA5 route remains blocked until boundary/crosswalk and aggregation po... |
| missing_codes_units_recall_skip_patterns | raw_value_verified_missing_units_recall_skip_policy_accepted | raw_value_verified_for_missing_units_recall_skip_patterns | Accepted for CHE10/CHE25, cost-barrier access, timing, and admin/EA geography scope; SDG 3.8.2 and CHIRPS/ERA5 route ... |


## Stop Rule

This packet is a promotion-control artifact, not an analysis dataset. Do not
write this country-wave into `data/` until the complete original raw package,
all raw value/key/unit/skip-pattern checks, outcome gates, and an accepted
CHIRPS or ERA5 linkage route pass.

Failed gates currently blocking promotion: 2.
