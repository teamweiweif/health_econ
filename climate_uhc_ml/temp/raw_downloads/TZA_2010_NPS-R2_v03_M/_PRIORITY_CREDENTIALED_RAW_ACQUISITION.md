# Priority Credentialed Raw Acquisition Handoff

Dataset: TZA_2010_NPS-R2_v03_M - Tanzania 2010-2011

Official get-microdata URL: https://microdata.worldbank.org/catalog/1050/get-microdata

Target folder: `temp/raw_downloads/TZA_2010_NPS-R2_v03_M/`

Current status: ready_for_credentialed_manual_download

Required scope: download the complete unchanged official raw package and all
documentation available after the official login/register/terms workflow. Do
not download only the priority core files if the interface offers a full
package/archive.

Priority core files to confirm after download:

| core_file_rank | metadata_file_name | candidate_categories | candidate_harmonized_variables |
|---|---|---|---|
| 1 | AG_SEC2A | geography;shocks | agriculture_livelihood;latitude_or_longitude;shock_module_variable |
| 2 | AG_SEC3A | consumption;health_need_access;shocks | agriculture_livelihood;care_not_sought_reason;coping_borrowed;reason_not_sought_distance;shock_module_variable;total_... |
| 3 | AG_SEC3B | consumption;health_need_access;shocks | agriculture_livelihood;care_not_sought_reason;coping_borrowed;reason_not_sought_distance;shock_module_variable;total_... |
| 4 | COMSEC_CD | geography;shocks;survey_design | admin1_or_admin2;agriculture_livelihood;psu_or_cluster_id |
| 5 | COMSEC_CE | demographics;geography;shocks;survey_design | admin1_or_admin2;agriculture_livelihood;psu_or_cluster_id;sex;shock_module_variable |
| 6 | COMSEC_CI | demographics;geography;shocks;survey_design | admin1_or_admin2;agriculture_livelihood;asset_index_or_asset_variable;education;psu_or_cluster_id;sex;shock_module_va... |
| 7 | COMSEC_CJ | geography;survey_design | admin1_or_admin2;household_weight_or_person_weight;psu_or_cluster_id |
| 8 | HH_SEC_B | demographics;geography;survey_design | admin1_or_admin2;age;hhid;household_head_marker;pid;sex |
| 9 | HH_SEC_D | demographics;health_expenditure;health_need_access;survey_design | age;care_sought;education;illness_or_injury_need;oop_health_expenditure;pid |
| 10 | TZY1.HH.Consumption | consumption;demographics;geography;health_need_access;survey_design | admin1_or_admin2;education;hhid;household_size;household_weight_or_person_weight;interview_date_or_survey_month;psu_o... |
| 11 | TZY2.HH.Consumption | consumption;demographics;geography;health_need_access;survey_design | admin1_or_admin2;education;hhid;household_size;household_weight_or_person_weight;interview_date_or_survey_month;reaso... |
| 12 | HH.Geovariables_Y2 | geography;health_need_access;shocks;survey_design | admin1_or_admin2;agriculture_livelihood;latitude_or_longitude;psu_or_cluster_id;reason_not_sought_distance;shock_modu... |

After placing files here, rerun:

`python script/17_audit_raw_downloads.py; python script/128_build_priority_archive_member_preflight.py; python script/130_build_priority_raw_package_receipt_ledger.py; python script/03_inspect_raw_schemas.py; python script/29_build_raw_variable_verification_protocol.py; python script/33_build_harmonization_recipe_gate.py; python script/125_build_priority_climate_linkage_preflight.py; python script/126_build_priority_raw_verification_workbook.py; python script/129_build_priority_manual_verification_decision_gate.py; python script/127_enforce_promoted_data_gate.py; python script/36_build_direct_read_audit_bundle.py; python script/14_validate_workspace.py`
