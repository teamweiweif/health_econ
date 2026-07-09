# Priority Country-Wave Promotion Packet

Dataset: ETH_2018_ESS_v04_M - Ethiopia 2018-2019

Survey: Socioeconomic Survey 2018-2019

Official URL: https://microdata.worldbank.org/catalog/3823/get-microdata

Target raw folder: `temp/raw_downloads/ETH_2018_ESS_v04_M/`

Current packet status: `blocked_fail_closed`

Analysis-ready status: `not_promoted`

Next blocking action: download_or_place_complete_original_raw_package

## Gate Matrix

| gate | status | evidence | required_action |
|---|---|---|---|
| official_public_documentation_receipt | pass | status=complete_full_public_documentation_receipt; saved=data_dictionary_html;ddi_metadata;get_microdata_html;json_me... |  |
| complete_original_raw_package | fail | receipt_status=not_received_no_original_raw_package; original_files=0; archives=0; raw_tabular=0; missing_targets=12 | Download/place the complete unchanged original raw package and documentation in the target folder. |
| priority_raw_module_coverage | fail | targets=12; covered=0; missing=12 | Ensure every priority target module is present directly or inside the received archive. |
| manual_requirement_verification | fail | requirements_passed=0/8 | Verify merge keys, survey design, consumption/income, OOP, access, timing, geography, missing codes, units, and recal... |
| manual_concept_verification | fail | concepts_passed=0/13 | Promote all required concepts only after raw variable value and level checks pass. |
| manual_variable_verification | fail | variables_passed=0/102 | Manually verify selected raw variables before harmonization recipe review. |
| financial_protection_value_ready | fail | financial_requirements_passed=0; financial_concepts_passed=0 | Verify total consumption/income, OOP health expenditure, weights/design, and denominator semantics for CHE10/CHE25 an... |
| access_forgone_care_value_ready | fail | double_failure_requirements_passed=0; double_failure_concepts_passed=0 | Verify illness/need, care seeking, forgone-care, and barrier variables with raw values and skip patterns. |
| accepted_chirps_era5_climate_linkage | fail | accepted_route=not_accepted_raw_timing_geography_unverified; gate=blocked_raw_timing_geography_not_verified_sources_r... | Verify timing/geography raw fields and accept a CHIRPS or ERA5 linkage route. |
| analysis_dataset_synthesis_join | fail | join_status=blocked_required_schema_columns_not_verified; required_columns=25; ready_columns=0; blocked_columns=22 | Complete required schema-column verification and join readiness before any promoted dataset build. |
| promoted_data_registry_write_gate | fail | registry_analysis_ready=not_promoted; rows=0 | Write to data/ only after the promoted registry marks this wave as analysis-ready. |

## Public Documentation Receipt

| resource_type | receipt_status | saved_path |
|---|---|---|
| get_microdata_html | saved_existing_access_probe | temp/source_snapshots/priority_official_raw_access/2_ETH_2018_ESS_v04_M/get_microdata.html |
| pdf_documentation | saved_existing | temp/source_snapshots/priority_public_documentation/2_ETH_2018_ESS_v04_M/pdf_documentation.pdf |
| ddi_metadata | saved_existing | temp/source_snapshots/priority_public_documentation/2_ETH_2018_ESS_v04_M/ddi_metadata.xml |
| json_metadata | saved_existing | temp/source_snapshots/priority_public_documentation/2_ETH_2018_ESS_v04_M/json_metadata.json |
| data_dictionary_html | saved_existing | temp/source_snapshots/priority_public_documentation/2_ETH_2018_ESS_v04_M/data_dictionary_html.html |
| related_materials_html | saved_existing | temp/source_snapshots/priority_public_documentation/2_ETH_2018_ESS_v04_M/related_materials_html.html |

## Priority Raw File Queue

| file_rank | file_name | candidate_categories | candidate_harmonized_variables |
|---|---|---|---|
| 1 | sect8_3_ls_w4.dta | geography;health_expenditure;health_need_access;shocks;survey_design | admin1_or_admin2;agriculture_livelihood;care_sought;hhid;household_weight_or_person_weight;oop_health_expenditure;psu... |
| 2 | sect10c_hh_w4.dta | demographics;geography;shocks;survey_design | admin1_or_admin2;agriculture_livelihood;asset_index_or_asset_variable;hhid;household_weight_or_person_weight;pid;psu_... |
| 3 | sect11_ph_w4.dta | geography;health_need_access;shocks;survey_design | admin1_or_admin2;agriculture_livelihood;hhid;household_weight_or_person_weight;psu_or_cluster_id;reason_not_sought_di... |
| 4 | sect04_com_w4.dta | demographics;geography;health_need_access;shocks;survey_design | admin1_or_admin2;asset_index_or_asset_variable;care_sought;psu_or_cluster_id;reason_not_sought_distance;rural;sex;sho... |
| 5 | sect06_com_w4.dta | geography;health_need_access;shocks;survey_design | admin1_or_admin2;agriculture_livelihood;coping_borrowed;psu_or_cluster_id;reason_not_sought_distance;rural;shock_modu... |
| 6 | sect3_pp_w4.dta | geography;shocks;survey_design | admin1_or_admin2;agriculture_livelihood;coping_borrowed;hhid;household_weight_or_person_weight;latitude_or_longitude;... |
| 7 | sect5b2_hh_w4.dta | demographics;geography;survey_design | admin1_or_admin2;age;asset_index_or_asset_variable;hhid;household_weight_or_person_weight;pid;psu_or_cluster_id;rural... |
| 8 | sect4_pp_w4.dta | geography;shocks;survey_design | admin1_or_admin2;agriculture_livelihood;hhid;household_weight_or_person_weight;psu_or_cluster_id;rural |
| 9 | sect3_hh_w4.dta | demographics;geography;health_expenditure;health_need_access;survey_design | admin1_or_admin2;age;care_not_sought_reason;care_sought;health_insurance;hhid;household_weight_or_person_weight;illne... |
| 10 | sect8_2_ls_w4.dta | consumption;geography;health_need_access;shocks;survey_design | admin1_or_admin2;agriculture_livelihood;hhid;household_weight_or_person_weight;psu_or_cluster_id;reason_not_sought_di... |
| 11 | sect9_ph_w4.dta | geography;shocks;survey_design | admin1_or_admin2;agriculture_livelihood;hhid;household_weight_or_person_weight;psu_or_cluster_id;rural |
| 12 | sect8_4_ls_w4.dta | geography;shocks;survey_design | admin1_or_admin2;agriculture_livelihood;hhid;household_weight_or_person_weight;psu_or_cluster_id;rural |

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
