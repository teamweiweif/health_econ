# Priority LSMS-ISA Official File Receipt Validator

IDNO: `KGZ_1993_KMPS_v01_M`

Country-wave: Kyrgyz Republic 1993

Target folder: `temp/raw_downloads/KGZ_1993_KMPS_v01_M/`

Status: `blocked_no_original_package`

## Counts

| Metric | Value |
|---|---:|
| Official expected file rows | 15 |
| Official expected matched rows | 0 |
| Official expected missing rows | 15 |
| Official core file rows | 31 |
| Official core matched rows | 0 |
| Official core missing rows | 31 |
| Local original file/archive-member rows | 0 |

## Missing Core Files

| requirement | file_rank | expected_file_name | top_variable_names | official_core_file_match_status |
|---|---|---|---|---|
| climate_geography | 1 | KPRICE2 | aye1_12a;aye1_12b;aye1_12c;aye1_12d;aye1_12e | missing_expected_core_file |
| climate_geography | 2 | KHHLD | ae2_1a;ae2_1b;ae3_1a;ae3_1b | missing_expected_core_file |
| climate_geography | 3 | KPRICE3 | ayeaid | missing_expected_core_file |
| climate_geography | 4 | CORE | region | missing_expected_core_file |
| climate_geography | 5 | CONADULT | hhead | missing_expected_core_file |
| consumption_or_income | 1 | INCEXP | khomcx;khomcy;kfoodx;khousex;kotherx;kothery;kothousx;kselfemy;ktothhy | missing_expected_core_file |
| consumption_or_income | 2 | KHHLD | ad141_1d;ad141_2d | missing_expected_core_file |
| consumption_or_income | 3 | KADULT | a1o16 | missing_expected_core_file |
| health_need_and_access | 1 | KYGPOV | hcsblne;lcsblne;poor3e;poor4e;rhcsblne;rlcsblne;rpoor3e;rpoor4e | missing_expected_core_file |
| health_need_and_access | 2 | KADULT | a1l16;a1j98 | missing_expected_core_file |
| health_need_and_access | 3 | INCEXP | khealthx | missing_expected_core_file |
| health_need_and_access | 4 | KCHILD | a1l16 | missing_expected_core_file |
| household_person_keys | 1 | KINDIVH | hid;pid;ab10_9_1;ab10_9_2 | missing_expected_core_file |
| household_person_keys | 2 | KADIET | pid;hhid | missing_expected_core_file |
| household_person_keys | 3 | KCHDIET | pid;hhid | missing_expected_core_file |
| household_person_keys | 4 | KINDIV | pid | missing_expected_core_file |
| household_person_keys | 5 | CONADULT | pid | missing_expected_core_file |
| household_person_keys | 6 | KADULT | pid | missing_expected_core_file |
| household_person_keys | 7 | KCHILD | pid | missing_expected_core_file |
| oop_health_expenditure | 1 | KHHLD | ae15_1b;ae20_6a;ae20_6b | missing_expected_core_file |
| oop_health_expenditure | 2 | KADULT | a1l14;a1l15;a1l16;a1l9 | missing_expected_core_file |
| oop_health_expenditure | 3 | KCHILD | a1l14;a1l15;a1l16;a1l9 | missing_expected_core_file |
| oop_health_expenditure | 4 | INCEXP | khealthx | missing_expected_core_file |
| survey_timing | 1 | KADULT | a1o10;a1o14;a1o16;a1o18;a1h7_2 | missing_expected_core_file |
| survey_timing | 2 | KCHILD | a1o10;a1o14;a1h7_2 | missing_expected_core_file |
| survey_timing | 3 | CORE | month | missing_expected_core_file |
| survey_timing | 4 | KHHLD | aa4_2 | missing_expected_core_file |
| survey_timing | 5 | CONADULT | gender | missing_expected_core_file |
| survey_timing | 6 | INCEXP | ktothhx | missing_expected_core_file |
| weights_and_design | 1 | KPRICE3 | ayeaid;ayea_10a;ayea_10b;ayea_10c;ayea_10d;ayea_10e;ayea_11a;ayea_11b;ayea_11c;ayea_11d;ayea_11e | missing_expected_core_file |
| weights_and_design | 2 | CONADULT | hhead | missing_expected_core_file |

## Missing Official Files

| file_id | expected_file_name | file_description | priority_core_target | official_file_match_status |
|---|---|---|---|---|
| F1 | CONADULT | adult characteristics | 1 | missing_expected_official_file |
| F2 | CORE | household characteristics | 1 | missing_expected_official_file |
| F3 | INCEXP | income and expenditure | 1 | missing_expected_official_file |
| F4 | KADIET | adult nutrition data (module P of Questionnaire for Adults) | 1 | missing_expected_official_file |
| F5 | KADULT | Questionnaire for Adults (excluding module P) | 1 | missing_expected_official_file |
| F6 | KCHDIET | child nutrition data (module P of Questionnaire for Children) | 1 | missing_expected_official_file |
| F7 | KCHILD | Questionnaire for Children (excluding module P) | 1 | missing_expected_official_file |
| F8 | KCOMM | Survey of Community and Social Infrastructure | 0 | missing_expected_official_file |
| F9 | KHHLD | Household Questionnaire (excluding module B) | 1 | missing_expected_official_file |
| F10 | KINDIV | household demographic and relationship variables (individual level) | 1 | missing_expected_official_file |
| F11 | KINDIVH | household roster (module B of Household Questionnaire) | 1 | missing_expected_official_file |
| F12 | KPRICE1 | Survey of Availability and Prices of Food Products and Fuel | 0 | missing_expected_official_file |
| F13 | KPRICE2 | Survey of Availability and Prices of Food Products and Fuel (continued) | 1 | missing_expected_official_file |
| F14 | KPRICE3 | Survey of Availability and Prices of Food Products and Fuel (continued) | 1 | missing_expected_official_file |
| F15 | KYGPOV | poverty line and poverty indicators | 1 | missing_expected_official_file |

## Required Next Action

Place the complete unchanged official raw package and documentation in the target folder.

After changing files in this folder, rerun:

`python script/17_audit_raw_downloads.py; python script/144_build_priority_lsms_isa_raw_package_intake_packet.py; python script/145_build_priority_lsms_isa_archive_member_preflight.py; python script/150_build_priority_lsms_isa_raw_package_receipt_checklist.py; python script/152_build_priority_lsms_isa_credentialed_raw_acquisition_workbench.py; python script/153_validate_priority_lsms_isa_official_file_receipt.py; python script/154_build_priority_lsms_isa_threshold_download_sequence.py; python script/149_build_priority_lsms_isa_raw_value_verification_workbook.py; python script/132_build_priority_analysis_dataset_synthesis_blueprint.py; python script/148_build_priority_lsms_isa_country_wave_promotion_packets.py; python script/151_refresh_refocused_promoted_country_wave_registry.py; python script/127_enforce_promoted_data_gate.py; python script/36_build_direct_read_audit_bundle.py; python script/14_validate_workspace.py`

This validator only proves expected file-name receipt against official DDI
metadata. It does not prove variable values, labels, units, recall periods,
survey-design fields, merge keys, climate linkage, or analysis-ready status.
