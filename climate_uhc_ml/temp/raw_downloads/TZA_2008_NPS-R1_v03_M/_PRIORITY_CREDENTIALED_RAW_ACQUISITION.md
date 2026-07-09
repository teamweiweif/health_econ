# Priority Credentialed Raw Acquisition Handoff

Dataset: TZA_2008_NPS-R1_v03_M - Tanzania 2008-2009

Official get-microdata URL: https://microdata.worldbank.org/catalog/76/get-microdata

Target folder: `temp/raw_downloads/TZA_2008_NPS-R1_v03_M/`

Current status: ready_for_credentialed_manual_download

Required scope: download the complete unchanged official raw package and all
documentation available after the official login/register/terms workflow. Do
not download only the priority core files if the interface offers a full
package/archive.

Priority core files to confirm after download:

| core_file_rank | metadata_file_name | candidate_categories | candidate_harmonized_variables |
|---|---|---|---|
| 1 | HH.Geovariables_Y1 | geography;health_need_access;shocks;survey_design | admin1_or_admin2;agriculture_livelihood;hhid;latitude_or_longitude;psu_or_cluster_id;reason_not_sought_distance;shock... |
| 2 | SECTCEFG | geography;shocks;survey_design | admin1_or_admin2;agriculture_livelihood;psu_or_cluster_id;shock_module_variable |
| 3 | SECTCH | demographics;geography;shocks;survey_design | admin1_or_admin2;agriculture_livelihood;asset_index_or_asset_variable;education;psu_or_cluster_id;sex |
| 4 | SEC_A_T_English_Labels | geography;shocks;survey_design | admin1_or_admin2;agriculture_livelihood;hhid;household_weight_or_person_weight;psu_or_cluster_id;rural;shock_module_v... |
| 5 | SEC_B_C_D_E1_F_G1_U_English_Labels | demographics;geography;health_expenditure;health_need_access;shocks;survey_design | admin1_or_admin2;age;agriculture_livelihood;asset_index_or_asset_variable;care_sought;education;hhid;household_weight... |
| 6 | SEC_H1_J_K2_O2_P1_Q1_S1_English_Labels | demographics;geography;shocks;survey_design | admin1_or_admin2;age;asset_index_or_asset_variable;coping_borrowed;hhid;shock_module_variable |
| 7 | SEC_P2_English_Labels | shocks;survey_design | coping_borrowed;hhid |
| 8 | SEC_S2_English_Labels | demographics;health_need_access;survey_design | age;asset_index_or_asset_variable;hhid;illness_or_injury_need;sex |
| 9 | SEC_3A_English_Labels | consumption;health_need_access;shocks;survey_design | agriculture_livelihood;care_not_sought_reason;coping_borrowed;hhid;reason_not_sought_distance;shock_module_variable;t... |
| 10 | SEC_3B_English_Labels | consumption;health_need_access;shocks;survey_design | agriculture_livelihood;care_not_sought_reason;coping_borrowed;hhid;reason_not_sought_distance;shock_module_variable;t... |
| 11 | SEC_4A_English_Labels | shocks;survey_design | agriculture_livelihood;hhid;shock_module_variable |
| 12 | TZY1.HH.Consumption | consumption;demographics;geography;health_need_access;survey_design | admin1_or_admin2;education;hhid;household_size;household_weight_or_person_weight;interview_date_or_survey_month;psu_o... |

After placing files here, rerun:

`python script/17_audit_raw_downloads.py; python script/128_build_priority_archive_member_preflight.py; python script/130_build_priority_raw_package_receipt_ledger.py; python script/03_inspect_raw_schemas.py; python script/29_build_raw_variable_verification_protocol.py; python script/33_build_harmonization_recipe_gate.py; python script/125_build_priority_climate_linkage_preflight.py; python script/126_build_priority_raw_verification_workbook.py; python script/140_build_priority_first_pass_variable_review_queue.py; python script/141_build_priority_download_execution_packet.py; python script/129_build_priority_manual_verification_decision_gate.py; python script/127_enforce_promoted_data_gate.py; python script/36_build_direct_read_audit_bundle.py; python script/14_validate_workspace.py`
