# Priority Credentialed Raw Acquisition Handoff

Dataset: ETH_2018_ESS_v04_M - Ethiopia 2018-2019

Official get-microdata URL: https://microdata.worldbank.org/catalog/3823/get-microdata

Target folder: `temp/raw_downloads/ETH_2018_ESS_v04_M/`

Current status: ready_for_credentialed_manual_download

Required scope: download the complete unchanged official raw package and all
documentation available after the official login/register/terms workflow. Do
not download only the priority core files if the interface offers a full
package/archive.

Priority core files to confirm after download:

| core_file_rank | metadata_file_name | candidate_categories | candidate_harmonized_variables |
|---|---|---|---|
| 1 | sect3_hh_w4.dta | demographics;geography;health_expenditure;health_need_access;survey_design | admin1_or_admin2;age;care_not_sought_reason;care_sought;health_insurance;hhid;household_weight_or_person_weight;illne... |
| 2 | sect5b2_hh_w4.dta | demographics;geography;survey_design | admin1_or_admin2;age;asset_index_or_asset_variable;hhid;household_weight_or_person_weight;pid;psu_or_cluster_id;rural... |
| 3 | sect10c_hh_w4.dta | demographics;geography;shocks;survey_design | admin1_or_admin2;agriculture_livelihood;asset_index_or_asset_variable;hhid;household_weight_or_person_weight;pid;psu_... |
| 4 | sect8_2_ls_w4.dta | consumption;geography;health_need_access;shocks;survey_design | admin1_or_admin2;agriculture_livelihood;hhid;household_weight_or_person_weight;psu_or_cluster_id;reason_not_sought_di... |
| 5 | sect8_3_ls_w4.dta | geography;health_expenditure;health_need_access;shocks;survey_design | admin1_or_admin2;agriculture_livelihood;care_sought;hhid;household_weight_or_person_weight;oop_health_expenditure;psu... |
| 6 | sect8_4_ls_w4.dta | geography;shocks;survey_design | admin1_or_admin2;agriculture_livelihood;hhid;household_weight_or_person_weight;psu_or_cluster_id;rural |
| 7 | sect9_ph_w4.dta | geography;shocks;survey_design | admin1_or_admin2;agriculture_livelihood;hhid;household_weight_or_person_weight;psu_or_cluster_id;rural |
| 8 | sect11_ph_w4.dta | geography;health_need_access;shocks;survey_design | admin1_or_admin2;agriculture_livelihood;hhid;household_weight_or_person_weight;psu_or_cluster_id;reason_not_sought_di... |
| 9 | sect3_pp_w4.dta | geography;shocks;survey_design | admin1_or_admin2;agriculture_livelihood;coping_borrowed;hhid;household_weight_or_person_weight;latitude_or_longitude;... |
| 10 | sect4_pp_w4.dta | geography;shocks;survey_design | admin1_or_admin2;agriculture_livelihood;hhid;household_weight_or_person_weight;psu_or_cluster_id;rural |
| 11 | sect04_com_w4.dta | demographics;geography;health_need_access;shocks;survey_design | admin1_or_admin2;asset_index_or_asset_variable;care_sought;psu_or_cluster_id;reason_not_sought_distance;rural;sex;sho... |
| 12 | sect06_com_w4.dta | geography;health_need_access;shocks;survey_design | admin1_or_admin2;agriculture_livelihood;coping_borrowed;psu_or_cluster_id;reason_not_sought_distance;rural;shock_modu... |

After placing files here, rerun:

`python script/17_audit_raw_downloads.py; python script/128_build_priority_archive_member_preflight.py; python script/130_build_priority_raw_package_receipt_ledger.py; python script/03_inspect_raw_schemas.py; python script/29_build_raw_variable_verification_protocol.py; python script/33_build_harmonization_recipe_gate.py; python script/125_build_priority_climate_linkage_preflight.py; python script/126_build_priority_raw_verification_workbook.py; python script/140_build_priority_first_pass_variable_review_queue.py; python script/141_build_priority_download_execution_packet.py; python script/129_build_priority_manual_verification_decision_gate.py; python script/127_enforce_promoted_data_gate.py; python script/36_build_direct_read_audit_bundle.py; python script/14_validate_workspace.py`
