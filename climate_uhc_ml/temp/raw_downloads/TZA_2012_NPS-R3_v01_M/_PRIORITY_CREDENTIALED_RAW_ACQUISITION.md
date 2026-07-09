# Priority Credentialed Raw Acquisition Handoff

Dataset: TZA_2012_NPS-R3_v01_M - Tanzania 2012-2013

Official get-microdata URL: https://microdata.worldbank.org/catalog/2252/get-microdata

Target folder: `temp/raw_downloads/TZA_2012_NPS-R3_v01_M/`

Current status: ready_for_credentialed_manual_download

Required scope: download the complete unchanged official raw package and all
documentation available after the official login/register/terms workflow. Do
not download only the priority core files if the interface offers a full
package/archive.

Priority core files to confirm after download:

| core_file_rank | metadata_file_name | candidate_categories | candidate_harmonized_variables |
|---|---|---|---|
| 1 | AG_SEC_2A | geography;shocks;survey_design | agriculture_livelihood;hhid;latitude_or_longitude;shock_module_variable |
| 2 | AG_SEC_3A | consumption;health_need_access;shocks;survey_design | agriculture_livelihood;care_not_sought_reason;coping_borrowed;hhid;reason_not_sought_distance;shock_module_variable;t... |
| 3 | AG_SEC_3B | consumption;health_need_access;shocks;survey_design | agriculture_livelihood;care_not_sought_reason;coping_borrowed;hhid;reason_not_sought_distance;shock_module_variable;t... |
| 4 | AG_SEC_4A | shocks;survey_design | agriculture_livelihood;hhid;shock_module_variable |
| 5 | AG_SEC_4B | shocks;survey_design | agriculture_livelihood;hhid;shock_module_variable |
| 6 | AG_SEC_5A | health_need_access;shocks;survey_design | agriculture_livelihood;hhid;reason_not_sought_distance;shock_module_variable |
| 7 | AG_SEC_5B | health_need_access;shocks;survey_design | agriculture_livelihood;hhid;reason_not_sought_distance;shock_module_variable |
| 8 | COM_SEC_CE | demographics;geography;health_need_access;shocks;survey_design | admin1_or_admin2;agriculture_livelihood;psu_or_cluster_id;reason_not_sought_distance;sex;shock_module_variable |
| 9 | COM_SEC_CF_ID | geography;survey_design | admin1_or_admin2;latitude_or_longitude;psu_or_cluster_id |
| 10 | HH_SEC_A | demographics;geography;survey_design | admin1_or_admin2;hhid;household_head_marker;household_weight_or_person_weight;interview_date_or_survey_month;psu_or_c... |
| 11 | HH_SEC_C | demographics;health_need_access;survey_design | age;education;hhid;pid;reason_not_sought_distance |
| 12 | HouseholdGeovars_Y3 | geography;health_need_access;shocks | admin1_or_admin2;agriculture_livelihood;latitude_or_longitude;reason_not_sought_distance;shock_module_variable |

After placing files here, rerun:

`python script/17_audit_raw_downloads.py; python script/128_build_priority_archive_member_preflight.py; python script/130_build_priority_raw_package_receipt_ledger.py; python script/03_inspect_raw_schemas.py; python script/29_build_raw_variable_verification_protocol.py; python script/33_build_harmonization_recipe_gate.py; python script/125_build_priority_climate_linkage_preflight.py; python script/126_build_priority_raw_verification_workbook.py; python script/129_build_priority_manual_verification_decision_gate.py; python script/127_enforce_promoted_data_gate.py; python script/36_build_direct_read_audit_bundle.py; python script/14_validate_workspace.py`
