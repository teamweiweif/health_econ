# Priority Credentialed Raw Acquisition Handoff

Dataset: NPL_2010_LSS-III_v01_M - Nepal 2010-2011

Official get-microdata URL: https://microdata.worldbank.org/catalog/1000/get-microdata

Target folder: `temp/raw_downloads/NPL_2010_LSS-III_v01_M/`

Current status: ready_for_credentialed_manual_download

Required scope: download the complete unchanged official raw package and all
documentation available after the official login/register/terms workflow. Do
not download only the priority core files if the interface offers a full
package/archive.

Priority core files to confirm after download:

| core_file_rank | metadata_file_name | candidate_categories | candidate_harmonized_variables |
|---|---|---|---|
| 1 | anthro | demographics;survey_design | age;household_weight_or_person_weight;psu_or_cluster_id;sex;strata |
| 2 | FINAL_PREF | consumption;demographics;geography;shocks;survey_design | admin1_or_admin2;age;agriculture_livelihood;asset_index_or_asset_variable;education;food_consumption;household_head_m... |
| 3 | S01 | demographics;geography;survey_design | admin1_or_admin2;age;rural;sex;strata |
| 4 | S04 | geography;survey_design | admin1_or_admin2;rural;strata |
| 5 | S08 | health_expenditure;health_need_access;survey_design | care_not_sought_reason;care_sought;illness_or_injury_need;oop_health_expenditure;reason_not_sought_distance;strata |
| 6 | S13A1 | geography;shocks;survey_design | admin1_or_admin2;agriculture_livelihood;strata |
| 7 | S16 | demographics;geography;survey_design | admin1_or_admin2;age;education;rural;sex;strata |
| 8 | S19 | consumption;demographics;health_need_access;shocks;survey_design | agriculture_livelihood;asset_index_or_asset_variable;care_sought;coping_borrowed;coping_sold_assets;education;food_co... |
| 9 | S20 | demographics;survey_design | age;household_weight_or_person_weight;strata |
| 10 | S21 | demographics;geography;survey_design | admin1_or_admin2;household_size;interview_date_or_survey_month;psu_or_cluster_id;strata |
| 11 | sample | demographics;geography;survey_design | admin1_or_admin2;household_size;household_weight_or_person_weight;psu_or_cluster_id;rural;strata |
| 12 | S00 | demographics;geography;health_need_access;shocks;survey_design | admin1_or_admin2;agriculture_livelihood;care_not_sought_reason;coping_borrowed;household_head_marker;psu_or_cluster_i... |

After placing files here, rerun:

`python script/17_audit_raw_downloads.py; python script/128_build_priority_archive_member_preflight.py; python script/130_build_priority_raw_package_receipt_ledger.py; python script/03_inspect_raw_schemas.py; python script/29_build_raw_variable_verification_protocol.py; python script/33_build_harmonization_recipe_gate.py; python script/125_build_priority_climate_linkage_preflight.py; python script/126_build_priority_raw_verification_workbook.py; python script/140_build_priority_first_pass_variable_review_queue.py; python script/141_build_priority_download_execution_packet.py; python script/129_build_priority_manual_verification_decision_gate.py; python script/127_enforce_promoted_data_gate.py; python script/36_build_direct_read_audit_bundle.py; python script/14_validate_workspace.py`
