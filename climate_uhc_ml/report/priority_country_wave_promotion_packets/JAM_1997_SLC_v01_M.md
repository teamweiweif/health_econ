# Priority Country-Wave Promotion Packet

Dataset: JAM_1997_SLC_v01_M - Jamaica 1997

Survey: Survey of Living Conditions 1997

Official URL: https://microdata.worldbank.org/catalog/2368/get-microdata

Target raw folder: `temp/raw_downloads/JAM_1997_SLC_v01_M/`

Current packet status: `blocked_fail_closed`

Analysis-ready status: `not_promoted`

Next blocking action: download_or_place_complete_original_raw_package

## Gate Matrix

| gate | status | evidence | required_action |
|---|---|---|---|
| official_public_documentation_receipt | pass | status=complete_full_public_documentation_receipt; saved=data_dictionary_html;ddi_metadata;get_microdata_html;json_me... |  |
| official_metadata_variable_evidence_extract | pass | status=partial_official_metadata_evidence_extract; candidates=66; ddi_matches=65; file_matches=65; no_matches=1 |  |
| credentialed_raw_acquisition_ledger | pass | status=ready_for_credentialed_manual_download; full_files=68; core_files=12; target_folder=temp/raw_downloads/JAM_199... |  |
| complete_original_raw_package | fail | receipt_status=not_received_no_original_raw_package; original_files=0; archives=0; raw_tabular=0; missing_targets=12 | Download/place the complete unchanged original raw package and documentation in the target folder. |
| priority_raw_module_coverage | fail | targets=12; covered=0; missing=12 | Ensure every priority target module is present directly or inside the received archive. |
| manual_requirement_verification | fail | requirements_passed=0/8 | Verify merge keys, survey design, consumption/income, OOP, access, timing, geography, missing codes, units, and recal... |
| manual_concept_verification | fail | concepts_passed=0/13 | Promote all required concepts only after raw variable value and level checks pass. |
| manual_variable_verification | fail | variables_passed=0/66 | Manually verify selected raw variables before harmonization recipe review. |
| financial_protection_value_ready | fail | financial_requirements_passed=0; financial_concepts_passed=0 | Verify total consumption/income, OOP health expenditure, weights/design, and denominator semantics for CHE10/CHE25 an... |
| access_forgone_care_value_ready | fail | double_failure_requirements_passed=0; double_failure_concepts_passed=0 | Verify illness/need, care seeking, forgone-care, and barrier variables with raw values and skip patterns. |
| accepted_chirps_era5_climate_linkage | fail | accepted_route=not_accepted_raw_timing_geography_unverified; gate=blocked_raw_timing_geography_not_verified_sources_r... | Verify timing/geography raw fields and accept a CHIRPS or ERA5 linkage route. |
| analysis_dataset_synthesis_join | fail | join_status=blocked_required_schema_columns_not_verified; required_columns=25; ready_columns=0; blocked_columns=22 | Complete required schema-column verification and join readiness before any promoted dataset build. |
| promoted_data_registry_write_gate | fail | registry_analysis_ready=not_promoted; rows=0 | Write to data/ only after the promoted registry marks this wave as analysis-ready. |

## Public Documentation Receipt

| resource_type | receipt_status | saved_path |
|---|---|---|
| get_microdata_html | saved_existing_access_probe | temp/source_snapshots/priority_official_raw_access/11_JAM_1997_SLC_v01_M/get_microdata.html |
| pdf_documentation | saved_existing | temp/source_snapshots/priority_public_documentation/11_JAM_1997_SLC_v01_M/pdf_documentation.pdf |
| ddi_metadata | saved_existing | temp/source_snapshots/priority_public_documentation/11_JAM_1997_SLC_v01_M/ddi_metadata.xml |
| json_metadata | saved_existing | temp/source_snapshots/priority_public_documentation/11_JAM_1997_SLC_v01_M/json_metadata.json |
| data_dictionary_html | saved_existing | temp/source_snapshots/priority_public_documentation/11_JAM_1997_SLC_v01_M/data_dictionary_html.html |
| related_materials_html | saved_existing | temp/source_snapshots/priority_public_documentation/11_JAM_1997_SLC_v01_M/related_materials_html.html |

## Priority Raw File Queue

| file_rank | file_name | candidate_categories | candidate_harmonized_variables |
|---|---|---|---|
| 1 | LABORF | demographics;geography;health_need_access;shocks;survey_design | admin1_or_admin2;age;asset_index_or_asset_variable;care_not_sought_reason;education;pid;sex;shock_module_variable |
| 2 | REC003 | health_expenditure;health_need_access | care_sought;health_insurance;illness_or_injury_need;oop_health_expenditure |
| 3 | ANNUAL | consumption;demographics;geography;survey_design | admin1_or_admin2;asset_index_or_asset_variable;food_consumption;household_size;household_weight_or_person_weight;nonf... |
| 4 | EDTOTALS | consumption;demographics;geography;survey_design | admin1_or_admin2;asset_index_or_asset_variable;food_consumption;household_weight_or_person_weight;nonfood_consumption... |
| 5 | HHSIZE | demographics;geography | admin1_or_admin2;age;asset_index_or_asset_variable;household_size;sex |
| 6 | NUTR97 | demographics;survey_design | age;household_weight_or_person_weight;sex |
| 7 | REC001 | demographics;geography;survey_design | admin1_or_admin2;asset_index_or_asset_variable;household_weight_or_person_weight;interview_date_or_survey_month |
| 8 | HEADS | demographics;geography;survey_design | admin1_or_admin2;age;household_head_marker;pid;sex |
| 9 | REC007 | demographics;survey_design | age;household_weight_or_person_weight |
| 10 | EXP97 | consumption;geography;survey_design | admin1_or_admin2;food_consumption;psu_or_cluster_id |
| 11 | REC006 | geography;health_need_access | admin1_or_admin2;reason_not_sought_distance |
| 12 | REC025 | consumption | nonfood_consumption |

## Manual Requirement Review Queue

| item_id | manual_decision_status | missing_or_failed_fields |
|---|---|---|
| household_person_merge_keys | blocked_source_gate_not_ready | fill_evidence_file_or_module; fill_raw_variables_used; fill_value_label_pass; fill_unit_or_recall_pass; fill_merge_ke... |
| weights_and_survey_design | blocked_source_gate_not_ready | fill_evidence_file_or_module; fill_raw_variables_used; fill_value_label_pass; fill_unit_or_recall_pass; fill_merge_ke... |
| consumption_or_income_aggregate | blocked_source_gate_not_ready | fill_evidence_file_or_module; fill_raw_variables_used; fill_value_label_pass; fill_unit_or_recall_pass; fill_merge_ke... |
| oop_health_expenditure | blocked_source_gate_not_ready | fill_evidence_file_or_module; fill_raw_variables_used; fill_value_label_pass; fill_unit_or_recall_pass; fill_merge_ke... |
| illness_need_care_access | blocked_source_gate_not_ready | fill_evidence_file_or_module; fill_raw_variables_used; fill_value_label_pass; fill_unit_or_recall_pass; fill_merge_ke... |
| survey_timing | blocked_source_gate_not_ready | fill_evidence_file_or_module; fill_raw_variables_used; fill_value_label_pass; fill_unit_or_recall_pass; fill_merge_ke... |
| geography_climate_linkage | blocked_source_gate_not_ready | fill_evidence_file_or_module; fill_raw_variables_used; fill_value_label_pass; fill_unit_or_recall_pass; fill_merge_ke... |
| missing_skip_units_recall | blocked_source_gate_not_ready | fill_evidence_file_or_module; fill_raw_variables_used; fill_value_label_pass; fill_unit_or_recall_pass; fill_merge_ke... |

## Manual Concept Review Queue

| item_id | manual_decision_status | missing_or_failed_fields |
|---|---|---|
| care_or_barrier | blocked_source_gate_not_ready | fill_raw_file_used; fill_raw_variable_used; fill_value_label_pass; fill_unit_or_recall_pass; fill_merge_key_pass; fil... |
| climate_geography | blocked_source_gate_not_ready | fill_raw_file_used; fill_raw_variable_used; fill_value_label_pass; fill_unit_or_recall_pass; fill_merge_key_pass; fil... |
| demographics | blocked_source_gate_not_ready | fill_raw_file_used; fill_raw_variable_used; fill_value_label_pass; fill_unit_or_recall_pass; fill_merge_key_pass; fil... |
| health_need | blocked_source_gate_not_ready | fill_raw_file_used; fill_raw_variable_used; fill_value_label_pass; fill_unit_or_recall_pass; fill_merge_key_pass; fil... |
| household_id | blocked_source_gate_not_ready | fill_raw_file_used; fill_raw_variable_used; fill_value_label_pass; fill_unit_or_recall_pass; fill_merge_key_pass; fil... |
| insurance | blocked_source_gate_not_ready | fill_raw_file_used; fill_raw_variable_used; fill_value_label_pass; fill_unit_or_recall_pass; fill_merge_key_pass; fil... |
| oop_health_expenditure | blocked_source_gate_not_ready | fill_raw_file_used; fill_raw_variable_used; fill_value_label_pass; fill_unit_or_recall_pass; fill_merge_key_pass; fil... |
| psu_cluster | blocked_source_gate_not_ready | fill_raw_file_used; fill_raw_variable_used; fill_value_label_pass; fill_unit_or_recall_pass; fill_merge_key_pass; fil... |
| shocks_or_livelihood | blocked_source_gate_not_ready | fill_raw_file_used; fill_raw_variable_used; fill_value_label_pass; fill_unit_or_recall_pass; fill_merge_key_pass; fil... |
| strata | blocked_source_gate_not_ready | fill_raw_file_used; fill_raw_variable_used; fill_value_label_pass; fill_unit_or_recall_pass; fill_merge_key_pass; fil... |
| survey_timing | blocked_source_gate_not_ready | fill_raw_file_used; fill_raw_variable_used; fill_value_label_pass; fill_unit_or_recall_pass; fill_merge_key_pass; fil... |
| survey_weight | blocked_source_gate_not_ready | fill_raw_file_used; fill_raw_variable_used; fill_value_label_pass; fill_unit_or_recall_pass; fill_merge_key_pass; fil... |
| total_consumption_or_income | blocked_source_gate_not_ready | fill_raw_file_used; fill_raw_variable_used; fill_value_label_pass; fill_unit_or_recall_pass; fill_merge_key_pass; fil... |

## Stop Rule

Do not write this country-wave into `data/` until the complete original raw
package is received, priority raw modules are covered, required raw values and
merge keys are manually verified, financial/access outcomes are verified, and
an accepted CHIRPS or ERA5 linkage route exists.

Failed gates currently blocking promotion: 10.
