# Priority Credentialed Raw Acquisition Handoff

Dataset: UGA_2014_SAGE-EL_v01_M - Uganda 2014

Official get-microdata URL: https://microdata.worldbank.org/catalog/2654/get-microdata

Target folder: `temp/raw_downloads/UGA_2014_SAGE-EL_v01_M/`

Current status: ready_for_credentialed_manual_download

Required scope: download the complete unchanged official raw package and all
documentation available after the official login/register/terms workflow. Do
not download only the priority core files if the interface offers a full
package/archive.

Priority core files to confirm after download:

| core_file_rank | metadata_file_name | candidate_categories | candidate_harmonized_variables |
|---|---|---|---|
| 1 | sage_labourintermed | demographics;geography;health_need_access;shocks;survey_design | admin1_or_admin2;age;agriculture_livelihood;asset_index_or_asset_variable;care_not_sought_reason;care_sought;coping_b... |
| 2 | int_operational | demographics;geography;health_expenditure;health_need_access;shocks;survey_design | admin1_or_admin2;agriculture_livelihood;asset_index_or_asset_variable;care_not_sought_reason;care_sought;coping_borro... |
| 3 | int_demographics_mem | demographics;geography;health_expenditure;health_need_access;survey_design | admin1_or_admin2;age;care_sought;education;hhid;household_head_marker;household_size;household_weight_or_person_weigh... |
| 4 | int_migration | demographics;geography;health_need_access;shocks;survey_design | admin1_or_admin2;age;care_sought;education;hhid;household_weight_or_person_weight;sex;shock_module_variable |
| 5 | int_welfare_hh | demographics;geography;health_expenditure;health_need_access;shocks;survey_design | admin1_or_admin2;agriculture_livelihood;asset_index_or_asset_variable;care_not_sought_reason;care_sought;coping_borro... |
| 6 | int_consexp | consumption;demographics;geography;health_expenditure;health_need_access;survey_design | admin1_or_admin2;asset_index_or_asset_variable;care_sought;education;food_consumption;hhid;household_size;household_w... |
| 7 | int_cohesion | demographics;geography;health_need_access;shocks;survey_design | admin1_or_admin2;asset_index_or_asset_variable;care_not_sought_reason;care_sought;coping_borrowed;hhid;household_weig... |
| 8 | int_access_educ18plus | demographics;geography;health_expenditure;health_need_access;shocks;survey_design | admin1_or_admin2;age;agriculture_livelihood;care_sought;education;hhid;household_weight_or_person_weight;illness_or_i... |
| 9 | int_access_fin | demographics;geography;health_expenditure;health_need_access;shocks;survey_design | admin1_or_admin2;agriculture_livelihood;asset_index_or_asset_variable;care_not_sought_reason;care_sought;coping_borro... |
| 10 | int_access_health | demographics;geography;health_expenditure;health_need_access;survey_design | admin1_or_admin2;age;care_sought;education;hhid;household_weight_or_person_weight;illness_or_injury_need;oop_health_e... |
| 11 | int_access_school | demographics;geography;health_expenditure;health_need_access;shocks;survey_design | admin1_or_admin2;age;agriculture_livelihood;care_sought;education;hhid;household_weight_or_person_weight;illness_or_i... |
| 12 | int_community | demographics;geography;health_need_access;shocks | admin1_or_admin2;agriculture_livelihood;care_sought;reason_not_sought_distance;sex |

After placing files here, rerun:

`python script/17_audit_raw_downloads.py; python script/128_build_priority_archive_member_preflight.py; python script/130_build_priority_raw_package_receipt_ledger.py; python script/03_inspect_raw_schemas.py; python script/29_build_raw_variable_verification_protocol.py; python script/33_build_harmonization_recipe_gate.py; python script/125_build_priority_climate_linkage_preflight.py; python script/126_build_priority_raw_verification_workbook.py; python script/129_build_priority_manual_verification_decision_gate.py; python script/127_enforce_promoted_data_gate.py; python script/36_build_direct_read_audit_bundle.py; python script/14_validate_workspace.py`
