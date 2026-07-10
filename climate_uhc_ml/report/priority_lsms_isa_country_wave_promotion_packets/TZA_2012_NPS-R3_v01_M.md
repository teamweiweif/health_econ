# Priority LSMS-ISA Country-Wave Promotion Packet

Dataset: `TZA_2012_NPS-R3_v01_M` - Tanzania 2012-2013

Survey: National Panel Survey 2012-2013, Wave 3

Official get-microdata URL: https://microdata.worldbank.org/catalog/2252/get-microdata

Target raw folder: `temp/raw_downloads/TZA_2012_NPS-R3_v01_M/`

Current packet status: `blocked_fail_closed`

Analysis-ready status: `not_promoted`

Next blocking action: `complete_raw_value_key_unit_verification`

## Gate Matrix

| gate | status | evidence | required_action |
|---|---|---|---|
| official_public_documentation_receipt | pass | status=complete_core_public_documentation_receipt; saved=catalog_idno_json;data_dictionary_html;ddi_metadata;get_micr... |  |
| official_variable_evidence_coverage | pass | coverage_rows=8; matrix_rows=84; shortlist_rows=33; no_candidate_rows=0 |  |
| complete_original_raw_package | pass | intake_status=ready_for_schema_and_manual_value_review; original_files=87; archives=0; raw_tabular=85; package_docs=2... |  |
| archive_or_direct_file_preflight | pass | status=ready_for_raw_receipt_schema_and_manual_review; direct_raw=85; direct_docs=2; archive_members=0 |  |
| raw_value_verification_household_person_keys | fail | metadata=official_metadata_strong_candidates_present_raw_review_required; candidates=12; files=11; raw_status=not_raw... | Use the focused variable-decision rows and original PDF documentation to make a reviewer acceptance decision; rerun p... |
| raw_value_verification_weights_and_design | fail | metadata=official_metadata_strong_candidates_present_raw_review_required; candidates=12; files=6; raw_status=not_raw_... | Use the focused variable-decision rows and original PDF documentation to make a reviewer acceptance decision; rerun p... |
| raw_value_verification_consumption_or_income | fail | metadata=official_metadata_strong_candidates_present_raw_review_required; candidates=12; files=2; raw_status=not_raw_... | Use the focused variable-decision rows and original PDF documentation to make a reviewer acceptance decision; rerun p... |
| raw_value_verification_oop_health_expenditure | fail | metadata=official_metadata_strong_candidates_present_raw_review_required; candidates=12; files=1; raw_status=not_raw_... | Use the focused variable-decision rows and original PDF documentation to make a reviewer acceptance decision; rerun p... |
| raw_value_verification_health_need_and_access | fail | metadata=official_metadata_strong_candidates_present_raw_review_required; candidates=12; files=6; raw_status=not_raw_... | Use the focused variable-decision rows and original PDF documentation to make a reviewer acceptance decision; rerun p... |
| raw_value_verification_survey_timing | fail | metadata=official_metadata_strong_candidates_present_raw_review_required; candidates=12; files=5; raw_status=not_raw_... | Use the focused variable-decision rows and original PDF documentation to make a reviewer acceptance decision; rerun p... |
| raw_value_verification_climate_geography | fail | metadata=official_metadata_strong_candidates_present_raw_review_required; candidates=12; files=5; raw_status=not_raw_... | Use the focused variable-decision rows and original PDF documentation to make a reviewer acceptance decision; rerun p... |
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
| health_need_and_access | official_metadata_strong_candidates_present_raw_review_required | 12 | 2 | not_raw_value_verified |
| survey_timing | official_metadata_strong_candidates_present_raw_review_required | 12 | 12 | not_raw_value_verified |
| climate_geography | official_metadata_strong_candidates_present_raw_review_required | 12 | 12 | not_raw_value_verified |
| missing_codes_units_recall_skip_patterns | documentation_and_raw_review_required_no_variable_shortlist | 0 | 0 | not_raw_value_verified |

## Official Public Documentation

| resource_type | receipt_status | saved_path |
|---|---|---|
| get_microdata_html | saved_existing | temp/source_snapshots/priority_lsms_isa_public_documentation/9_TZA_2012_NPS-R3_v01_M/get_microdata_html.html |
| catalog_idno_json | saved_existing | temp/source_snapshots/priority_lsms_isa_public_documentation/9_TZA_2012_NPS-R3_v01_M/catalog_idno_json.json |
| variables_idno_json | saved_existing | temp/source_snapshots/priority_lsms_isa_public_documentation/9_TZA_2012_NPS-R3_v01_M/variables_idno_json.json |
| ddi_metadata | saved_existing | temp/source_snapshots/priority_lsms_isa_public_documentation/9_TZA_2012_NPS-R3_v01_M/ddi_metadata.xml |
| json_metadata | saved_existing | temp/source_snapshots/priority_lsms_isa_public_documentation/9_TZA_2012_NPS-R3_v01_M/json_metadata.json |
| data_dictionary_html | saved_existing | temp/source_snapshots/priority_lsms_isa_public_documentation/9_TZA_2012_NPS-R3_v01_M/data_dictionary_html.html |
| related_materials_html | saved_existing | temp/source_snapshots/priority_lsms_isa_public_documentation/9_TZA_2012_NPS-R3_v01_M/related_materials_html.html |

## Concept File Shortlist

| requirement | file_name | candidate_variable_rows | top_variable_names |
|---|---|---|---|
| climate_geography | COM_SEC_A1A2.NSDstat | 4 | cm_lon_g;cm_lon_m;cm_lon_s;y3_cluster |
| climate_geography | AG_SEC_2A.NSDstat | 2 | ag2a_06_3;ag2a_06_4 |
| climate_geography | AG_SEC_A.NSDstat | 2 | ag_a04_1;ag_a04_2 |
| climate_geography | HH_SEC_A.NSDstat | 2 | hh_a04_1;hh_a04_2 |
| climate_geography | LF_SEC_A.NSDstat | 2 | lf_a04_1;lf_a04_2 |
| consumption_or_income | HH_SEC_K.NSDstat | 6 | hh_k01;hh_k02;hh_k03;itemcode;occ;y3_hhid |
| consumption_or_income | HH_SEC_L.NSDstat | 6 | hh_l01;hh_l02;hh_l03;itemcode;occ;y3_hhid |
| health_need_and_access | HH_SEC_D.NSDstat | 5 | hh_d12_1;hh_d12_2;hh_d02;hh_d13;hh_d23 |
| health_need_and_access | ConsumptionNPS3.NSDstat | 2 | health;healthR |
| health_need_and_access | LF_SEC_13B.NSDstat | 2 | costcode;costname |
| health_need_and_access | HH_SEC_G.NSDstat | 1 | hh_g03_5 |
| health_need_and_access | AG_SEC_11.NSDstat | 1 | ag11_05 |
| health_need_and_access | COM_SEC_CB.NSDstat | 1 | cm_b02 |
| household_person_keys | HH_SEC_B.NSDstat | 2 | y2_hhid;y3_hhid |
| household_person_keys | AG_SEC_01.NSDstat | 1 | y3_hhid |
| household_person_keys | AG_SEC_2A.NSDstat | 1 | y3_hhid |

## Candidate Variable Preview

| requirement | variable_name | variable_label | file_name | match_score |
|---|---|---|---|---|
| household_person_keys | y2_hhid | Unique Household Identification NPS Y2 | HH_SEC_B.NSDstat | 52 |
| household_person_keys | y3_hhid | Unique Household Identification NPS Y3 | HH_SEC_B.NSDstat | 52 |
| household_person_keys | y3_hhid | Unique Household Identification NPS Y3 | AG_SEC_01.NSDstat | 45 |
| household_person_keys | y3_hhid | Unique Household Identification NPS Y3 | AG_SEC_2A.NSDstat | 45 |
| household_person_keys | y3_hhid | Unique Household Identification NPS Y3 | AG_SEC_2B.NSDstat | 45 |
| household_person_keys | y3_hhid | Unique Household Identification NPS Y3 | LF_NETWORK.NSDstat | 45 |
| household_person_keys | y3_hhid | Unique Household Identification NPS Y3 | LF_SEC_01.NSDstat | 45 |
| household_person_keys | y3_hhid | Unique Household Identification NPS Y3 | AG_SEC_08.NSDstat | 36 |
| household_person_keys | y3_hhid | Unique Household Identification NPS Y3 | AG_SEC_11.NSDstat | 36 |
| household_person_keys | y3_hhid | Unique Household Identification NPS Y3 | AG_SEC_12A.NSDstat | 36 |
| household_person_keys | y3_hhid | Unique Household Identification NPS Y3 | AG_SEC_12B.NSDstat | 36 |
| household_person_keys | y3_hhid | Unique Household Identification NPS Y3 | AG_SEC_A.NSDstat | 36 |
| weights_and_design | y3_weight | (mean) y3_panelweight | HH_SEC_A.NSDstat | 28 |
| weights_and_design | strataid | Unique ID for sampling stratum | HH_SEC_A.NSDstat | 25 |
| weights_and_design | y3_panelweight | (mean) y3_panelweight | Y3_weights.NSDstat | 24 |
| weights_and_design | ag_a04_1 | Village / Enumeration Area Code | AG_SEC_A.NSDstat | 21 |

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
| household_person_keys | mechanical_raw_profile_available_documentation_crosscheck_missing | blocked_manual_acceptance_required | reviewer must confirm raw file, variable, value labels, units, recall periods, missing codes, skip patterns, merge le... |
| weights_and_design | mechanical_raw_profile_plus_documentation_hits_needs_reviewer_acceptance | blocked_manual_acceptance_required | reviewer must confirm raw file, variable, value labels, units, recall periods, missing codes, skip patterns, merge le... |
| consumption_or_income | mechanical_raw_profile_plus_documentation_hits_needs_reviewer_acceptance | blocked_manual_acceptance_required | reviewer must confirm raw file, variable, value labels, units, recall periods, missing codes, skip patterns, merge le... |
| oop_health_expenditure | mechanical_raw_profile_plus_documentation_hits_needs_reviewer_acceptance | blocked_manual_acceptance_required | reviewer must confirm raw file, variable, value labels, units, recall periods, missing codes, skip patterns, merge le... |
| health_need_and_access | mechanical_raw_profile_plus_documentation_hits_needs_reviewer_acceptance | blocked_manual_acceptance_required | reviewer must confirm raw file, variable, value labels, units, recall periods, missing codes, skip patterns, merge le... |
| survey_timing | mechanical_raw_profile_plus_documentation_hits_needs_reviewer_acceptance | blocked_manual_acceptance_required | reviewer must confirm raw file, variable, value labels, units, recall periods, missing codes, skip patterns, merge le... |
| climate_geography | mechanical_raw_profile_plus_documentation_hits_needs_reviewer_acceptance | blocked_manual_acceptance_required | reviewer must confirm raw file, variable, value labels, units, recall periods, missing codes, skip patterns, merge le... |


## Household Join Readiness

| best_base_file | consumption_or_income | weights_and_design | oop_health_expenditure | health_need_and_access | survey_timing | climate_geography | complete_join_path | status | remaining_blockers |
|---|---|---|---|---|---|---|---|---|---|
| ConsumptionNPS3.dta | 1 | 1 | 1 | 1 | 1 | 1 | 1 | household_join_path_ready_value_verification_and_climate_blocked | raw_value_verification_still_requires_reviewer_acceptance; climate_exposure_route_not_accepted_for_this_wave |

This join audit is raw-backed structural evidence only. It does not verify raw
values, accept climate linkage, write to `data/`, or open modeling.


## Stop Rule

This packet is a promotion-control artifact, not an analysis dataset. Do not
write this country-wave into `data/` until the complete original raw package,
all raw value/key/unit/skip-pattern checks, outcome gates, and an accepted
CHIRPS or ERA5 linkage route pass.

Failed gates currently blocking promotion: 15.
