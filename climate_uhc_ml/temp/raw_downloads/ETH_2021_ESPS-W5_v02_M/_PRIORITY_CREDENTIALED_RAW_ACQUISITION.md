# Priority Credentialed Raw Acquisition Handoff

Dataset: ETH_2021_ESPS-W5_v02_M - Ethiopia 2021-2022

Official get-microdata URL: https://microdata.worldbank.org/catalog/6161/get-microdata

Target folder: `temp/raw_downloads/ETH_2021_ESPS-W5_v02_M/`

Current status: ready_for_credentialed_manual_download

Required scope: download the complete unchanged official raw package and all
documentation available after the official login/register/terms workflow. Do
not download only the priority core files if the interface offers a full
package/archive.

Priority core files to confirm after download:

| core_file_rank | metadata_file_name | candidate_categories | candidate_harmonized_variables |
|---|---|---|---|
| 1 | sect3_hh_w5.dta | demographics;geography;health_expenditure;health_need_access;survey_design | admin1_or_admin2;age;care_not_sought_reason;care_sought;health_insurance;hhid;household_weight_or_person_weight;illne... |
| 2 | sect04_com_w5.dta | demographics;geography;health_need_access;shocks;survey_design | admin1_or_admin2;asset_index_or_asset_variable;care_sought;psu_or_cluster_id;reason_not_sought_distance;rural;sex;sho... |
| 3 | sect06_com_w5.dta | geography;health_need_access;shocks;survey_design | admin1_or_admin2;agriculture_livelihood;coping_borrowed;psu_or_cluster_id;reason_not_sought_distance;rural;shock_modu... |
| 4 | sect11_com_w5.dta | demographics;geography;shocks;survey_design | admin1_or_admin2;agriculture_livelihood;education;psu_or_cluster_id;rural |
| 5 | sect3_pp_w5.dta | geography;health_need_access;shocks;survey_design | admin1_or_admin2;agriculture_livelihood;coping_borrowed;hhid;household_weight_or_person_weight;latitude_or_longitude;... |
| 6 | sect4_pp_w5.dta | geography;shocks;survey_design | admin1_or_admin2;agriculture_livelihood;hhid;household_weight_or_person_weight;psu_or_cluster_id;rural;shock_module_v... |
| 7 | sect7_pp_w5.dta | demographics;geography;health_need_access;shocks;survey_design | admin1_or_admin2;agriculture_livelihood;care_not_sought_reason;coping_borrowed;education;household_weight_or_person_w... |
| 8 | sect9_ph_w5.dta | geography;shocks;survey_design | admin1_or_admin2;agriculture_livelihood;hhid;household_weight_or_person_weight;psu_or_cluster_id;rural;shock_module_v... |
| 9 | sect11_ph_w5.dta | geography;health_need_access;shocks;survey_design | admin1_or_admin2;agriculture_livelihood;hhid;household_weight_or_person_weight;psu_or_cluster_id;reason_not_sought_di... |
| 10 | sect8_2_ls_w5.dta | consumption;geography;health_need_access;shocks;survey_design | admin1_or_admin2;agriculture_livelihood;hhid;household_weight_or_person_weight;psu_or_cluster_id;reason_not_sought_di... |
| 11 | sect8_3_ls_w5.dta | geography;health_expenditure;health_need_access;shocks;survey_design | admin1_or_admin2;agriculture_livelihood;care_sought;hhid;household_weight_or_person_weight;oop_health_expenditure;psu... |
| 12 | eth_householdgeovariables_y5.dta | geography;health_need_access;shocks;survey_design | admin1_or_admin2;agriculture_livelihood;hhid;latitude_or_longitude;psu_or_cluster_id;reason_not_sought_distance;rural... |

After placing files here, rerun:

`python script/17_audit_raw_downloads.py; python script/128_build_priority_archive_member_preflight.py; python script/130_build_priority_raw_package_receipt_ledger.py; python script/03_inspect_raw_schemas.py; python script/29_build_raw_variable_verification_protocol.py; python script/33_build_harmonization_recipe_gate.py; python script/125_build_priority_climate_linkage_preflight.py; python script/126_build_priority_raw_verification_workbook.py; python script/129_build_priority_manual_verification_decision_gate.py; python script/127_enforce_promoted_data_gate.py; python script/36_build_direct_read_audit_bundle.py; python script/14_validate_workspace.py`
