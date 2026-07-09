# Priority Credentialed Raw Acquisition Handoff

Dataset: KGZ_1993_KMPS_v01_M - Kyrgyz Republic 1993

Official get-microdata URL: https://microdata.worldbank.org/catalog/280/get-microdata

Target folder: `temp/raw_downloads/KGZ_1993_KMPS_v01_M/`

Current status: ready_for_credentialed_manual_download

Required scope: download the complete unchanged official raw package and all
documentation available after the official login/register/terms workflow. Do
not download only the priority core files if the interface offers a full
package/archive.

Priority core files to confirm after download:

| core_file_rank | metadata_file_name | candidate_categories | candidate_harmonized_variables |
|---|---|---|---|
| 1 | CONADULT | demographics;survey_design | age;education;hhid;household_head_marker;pid;sex |
| 2 | CORE | geography;survey_design | admin1_or_admin2;hhid;interview_date_or_survey_month |
| 3 | INCEXP | consumption;demographics;geography;health_need_access;shocks;survey_design | admin1_or_admin2;agriculture_livelihood;asset_index_or_asset_variable;education;hhid;household_size;reason_not_sought... |
| 4 | KADULT | consumption;demographics;geography;health_expenditure;health_need_access;shocks;survey_design | admin1_or_admin2;age;agriculture_livelihood;asset_index_or_asset_variable;care_not_sought_reason;care_sought;coping_b... |
| 5 | KCHILD | demographics;health_expenditure;health_need_access;shocks;survey_design | age;agriculture_livelihood;care_sought;education;hhid;household_weight_or_person_weight;illness_or_injury_need;interv... |
| 6 | KCOMM | demographics;geography;health_need_access;shocks | admin1_or_admin2;reason_not_sought_distance;reason_not_sought_supply;sex;shock_module_variable |
| 7 | KHHLD | demographics;geography;health_expenditure;health_need_access;shocks;survey_design | admin1_or_admin2;agriculture_livelihood;asset_index_or_asset_variable;coping_borrowed;hhid;illness_or_injury_need;int... |
| 8 | KINDIV | demographics;survey_design | age;hhid;pid;sex |
| 9 | KINDIVH | demographics;survey_design | hhid;pid;sex |
| 10 | KPRICE2 | geography;shocks | admin1_or_admin2;shock_module_variable |
| 11 | KPRICE3 | geography;shocks | admin1_or_admin2;shock_module_variable |
| 12 | KYGPOV | geography;survey_design | admin1_or_admin2;hhid |

After placing files here, rerun:

`python script/17_audit_raw_downloads.py; python script/128_build_priority_archive_member_preflight.py; python script/130_build_priority_raw_package_receipt_ledger.py; python script/03_inspect_raw_schemas.py; python script/29_build_raw_variable_verification_protocol.py; python script/33_build_harmonization_recipe_gate.py; python script/125_build_priority_climate_linkage_preflight.py; python script/126_build_priority_raw_verification_workbook.py; python script/129_build_priority_manual_verification_decision_gate.py; python script/127_enforce_promoted_data_gate.py; python script/36_build_direct_read_audit_bundle.py; python script/14_validate_workspace.py`
