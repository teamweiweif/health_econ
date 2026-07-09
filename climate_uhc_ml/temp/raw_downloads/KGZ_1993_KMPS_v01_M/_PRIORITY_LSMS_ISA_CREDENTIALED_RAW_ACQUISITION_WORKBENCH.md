# Priority LSMS-ISA Credentialed Raw Acquisition Workbench

Dataset: `KGZ_1993_KMPS_v01_M` - Kyrgyz Republic 1993

Official get-microdata URL: https://microdata.worldbank.org/catalog/280/get-microdata

Target folder: `temp/raw_downloads/KGZ_1993_KMPS_v01_M/`

Current receipt status: `blocked_no_original_package`

## Manual Download Action

Open official_get_microdata_url, log in or register if required, accept official terms/Data Access Agreement, download the complete unchanged raw package plus all documentation, and place all files in local_target_folder.

Scope: Download the complete unchanged official World Bank package for this IDNO, including all raw microdata files, archives, documentation, questionnaires, codebooks, DDI/XML, and geography/timing supplements exposed after login.

## Core Files To Confirm After Download

| requirement | file_rank | file_name | candidate_variable_rows | top_variable_names |
|---|---|---|---|---|
| climate_geography | 1 | KPRICE2 | 5 | aye1_12a;aye1_12b;aye1_12c;aye1_12d;aye1_12e |
| climate_geography | 2 | KHHLD | 4 | ae2_1a;ae2_1b;ae3_1a;ae3_1b |
| climate_geography | 3 | KPRICE3 | 1 | ayeaid |
| climate_geography | 4 | CORE | 1 | region |
| climate_geography | 5 | CONADULT | 1 | hhead |
| consumption_or_income | 1 | INCEXP | 9 | khomcx;khomcy;kfoodx;khousex;kotherx;kothery;kothousx;kselfemy;ktothhy |
| consumption_or_income | 2 | KHHLD | 2 | ad141_1d;ad141_2d |
| consumption_or_income | 3 | KADULT | 1 | a1o16 |
| health_need_and_access | 1 | KYGPOV | 8 | hcsblne;lcsblne;poor3e;poor4e;rhcsblne;rlcsblne;rpoor3e;rpoor4e |
| health_need_and_access | 2 | KADULT | 2 | a1l16;a1j98 |
| health_need_and_access | 3 | INCEXP | 1 | khealthx |
| health_need_and_access | 4 | KCHILD | 1 | a1l16 |
| household_person_keys | 1 | KINDIVH | 4 | hid;pid;ab10_9_1;ab10_9_2 |
| household_person_keys | 2 | KADIET | 2 | pid;hhid |
| household_person_keys | 3 | KCHDIET | 2 | pid;hhid |
| household_person_keys | 4 | KINDIV | 1 | pid |
| household_person_keys | 5 | CONADULT | 1 | pid |
| household_person_keys | 6 | KADULT | 1 | pid |
| household_person_keys | 7 | KCHILD | 1 | pid |
| oop_health_expenditure | 1 | KHHLD | 3 | ae15_1b;ae20_6a;ae20_6b |

## Official File Manifest Preview

| file_id | file_name | file_description | case_quantity | variable_quantity | priority_core_target |
|---|---|---|---|---|---|
| F1 | CONADULT | adult characteristics | 5647 | 11 | 1 |
| F2 | CORE | household characteristics | 1937 | 15 | 1 |
| F3 | INCEXP | income and expenditure | 1937 | 57 | 1 |
| F4 | KADIET | adult nutrition data (module P of Questionnaire for Adults) | 18284 | 23 | 1 |
| F5 | KADULT | Questionnaire for Adults (excluding module P) | 5647 | 434 | 1 |
| F6 | KCHDIET | child nutrition data (module P of Questionnaire for Children) | 12860 | 27 | 1 |
| F7 | KCHILD | Questionnaire for Children (excluding module P) | 3421 | 246 | 1 |
| F8 | KCOMM | Survey of Community and Social Infrastructure | 213 | 273 | 0 |
| F9 | KHHLD | Household Questionnaire (excluding module B) | 1937 | 901 | 1 |
| F10 | KINDIV | household demographic and relationship variables (individual level) | 9547 | 24 | 1 |
| F11 | KINDIVH | household roster (module B of Household Questionnaire) | 1937 | 234 | 1 |
| F12 | KPRICE1 | Survey of Availability and Prices of Food Products and Fuel | 212 | 568 | 0 |
| F13 | KPRICE2 | Survey of Availability and Prices of Food Products and Fuel (continued) | 212 | 886 | 1 |
| F14 | KPRICE3 | Survey of Availability and Prices of Food Products and Fuel (continued) | 212 | 1000 | 1 |
| F15 | KYGPOV | poverty line and poverty indicators | 1937 | 13 | 1 |

## After Placing Files

Run:

`python script/17_audit_raw_downloads.py; python script/144_build_priority_lsms_isa_raw_package_intake_packet.py; python script/145_build_priority_lsms_isa_archive_member_preflight.py; python script/149_build_priority_lsms_isa_raw_value_verification_workbook.py; python script/150_build_priority_lsms_isa_raw_package_receipt_checklist.py; python script/152_build_priority_lsms_isa_credentialed_raw_acquisition_workbench.py; python script/153_validate_priority_lsms_isa_official_file_receipt.py; python script/154_build_priority_lsms_isa_threshold_download_sequence.py; python script/132_build_priority_analysis_dataset_synthesis_blueprint.py; python script/148_build_priority_lsms_isa_country_wave_promotion_packets.py; python script/151_refresh_refocused_promoted_country_wave_registry.py; python script/127_enforce_promoted_data_gate.py; python script/36_build_direct_read_audit_bundle.py; python script/14_validate_workspace.py`

## Stop Rule

Do not mark receipt, raw-value verification, climate linkage, or analysis
readiness as passed until the complete official package is present and the raw
value workbook evidence fields are filled from original files.
