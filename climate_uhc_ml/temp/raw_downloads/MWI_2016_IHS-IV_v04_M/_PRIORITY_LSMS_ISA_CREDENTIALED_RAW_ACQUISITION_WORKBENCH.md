# Priority LSMS-ISA Credentialed Raw Acquisition Workbench

Dataset: `MWI_2016_IHS-IV_v04_M` - Malawi 2016-2017

Official get-microdata URL: https://microdata.worldbank.org/catalog/2936/get-microdata

Target folder: `temp/raw_downloads/MWI_2016_IHS-IV_v04_M/`

Current receipt status: `blocked_no_original_package`

## Manual Download Action

Open official_get_microdata_url, log in or register if required, accept official terms/Data Access Agreement, download the complete unchanged raw package plus all documentation, and place all files in local_target_folder.

Scope: Download the complete unchanged official World Bank package for this IDNO, including all raw microdata files, archives, documentation, questionnaires, codebooks, DDI/XML, and geography/timing supplements exposed after login.

## Core Files To Confirm After Download

| requirement | file_rank | file_name | candidate_variable_rows | top_variable_names |
|---|---|---|---|---|
| climate_geography | 1 | IHS4 Consumption Aggregate | 2 | ea_id;area |
| climate_geography | 2 | AG_MOD_J | 2 | ag_j06e;ag_j06e_oth |
| climate_geography | 3 | AG_MOD_B1 | 2 | ag_b105e;ag_b105e_oth |
| climate_geography | 4 | AG_MOD_I1 | 2 | ag_i106c;ag_i106c_oth |
| climate_geography | 5 | AG_MOD_O1 | 2 | ag_o105e;ag_o105e_oth |
| climate_geography | 6 | HH_MOD_A_FILT | 1 | ea_id |
| climate_geography | 7 | AG_MOD_C | 1 | ag_c05e |
| consumption_or_income | 1 | HH_MOD_I1 | 5 | case_id;hh_i01;hh_i02;hh_i03;HHID |
| consumption_or_income | 2 | HH_MOD_I2 | 3 | case_id;hh_i04;hh_i05 |
| consumption_or_income | 3 | HH_MOD_G1 | 2 | hh_g00_2;hh_g00_1 |
| consumption_or_income | 4 | HH_MOD_K1 | 1 | hh_k03 |
| consumption_or_income | 5 | HH_MOD_K2 | 1 | hh_k03 |
| health_need_and_access | 1 | HH_MOD_D | 7 | hh_d04;hh_d05_oth;hh_d34a;hh_d34b;hh_d11;hh_d13;hh_d14 |
| health_need_and_access | 2 | COM_CD | 4 | com_cd60a;com_cd53;com_cd54;com_cd51a |
| health_need_and_access | 3 | AG_MOD_D | 1 | ag_d25_2a |
| household_person_keys | 1 | HH_MOD_B | 1 | case_id |
| household_person_keys | 2 | AG_MOD_J | 1 | case_id |
| household_person_keys | 3 | AG_MOD_B1 | 1 | case_id |
| household_person_keys | 4 | AG_MOD_C | 1 | case_id |
| household_person_keys | 5 | AG_MOD_I1 | 1 | case_id |

## Official File Manifest Preview

| file_id | file_name | file_description | case_quantity | variable_quantity | priority_core_target |
|---|---|---|---|---|---|
| F1 | HH_METADATA | Household questionnaire metadata | 12447 | 113 | 1 |
| F2 | HH_MOD_A_FILT | Data collected through Household Questionnaire, Module A: Household Identification (household level data) | 12447 | 20 | 1 |
| F3 | HH_MOD_B | Data collected through Household Questionnaire, Module B: Household Roster ( individual level data) | 53885 | 53 | 1 |
| F4 | HH_MOD_C | Data collected through Household Questionnaire, Module C: Education (individual level data) | 53885 | 39 | 0 |
| F5 | HH_MOD_D | Data collected through Household Questionnaire, Module D: Health (individual level data) | 53885 | 49 | 1 |
| F6 | HH_MOD_E | Data collected through Household Questionnaire, Module E: Time Use and Labour – individual level data | 53885 | 132 | 0 |
| F7 | HH_MOD_F | Data collected through Household Questionnaire, Module F: Housing - household level data | 12447 | 116 | 0 |
| F8 | HH_MOD_G1 | Data collected through Household Questionnaire, Module G: Food Consumption Over Past One Week – consumption item level | 1755027 | 28 | 1 |
| F9 | HH_MOD_G2 | Data collected through Household Questionnaire, Module G: Food Consumption Over Past One Week – food group (aggregate) | 12447 | 12 | 0 |
| F10 | HH_MOD_G3 | Data collected through Household Questionnaire, Module G: Food Consumption Over Past One Week – age group (aggregate) | 24664 | 6 | 0 |
| F11 | HH_MOD_H | Data collected through Household Questionnaire, Module H: Food security – household level | 12447 | 41 | 0 |
| F12 | HH_MOD_I1 | Data collected through Household Questionnaire, Module I: Non-food Expenditures Over Past One Week and One Month – co... | 112023 | 5 | 1 |
| F13 | HH_MOD_I2 | Data collected through Household Questionnaire, Module I: Non-food Expenditures Over Past One Week and One Month – co... | 248940 | 5 | 1 |
| F14 | HH_MOD_J | Data collected through Household Questionnaire, Module J: Non-food Expenditures Over Past Three Months – consumption ... | 485433 | 5 | 0 |
| F15 | HH_MOD_K1 | Data collected through Household Questionnaire, Module K: Non-food Expenditures Over Past 12 Months – consumption ite... | 224046 | 5 | 1 |
| F16 | HH_MOD_K2 | Data collected through Household Questionnaire, Module K: Non-food Expenditures Over Past 12 Months - consumption ite... | 24894 | 6 | 1 |
| F17 | HH_MOD_L | Data collected through Household Questionnaire, Module L: Durable Goods - durable item level | 410751 | 9 | 0 |
| F18 | HH_MOD_M | Data collected through Household Questionnaire, Module M: Farm Implements, Machinery, and Structures | 311175 | 20 | 0 |
| F19 | HH_MOD_N1 | Data collected through Household Questionnaire, Module N: Household Enterprises – household level | 12447 | 10 | 0 |
| F20 | HH_MOD_N2 | Data collected through Household Questionnaire, Module N: Household Enterprises | 3693 | 119 | 0 |

## After Placing Files

Run:

`python script/17_audit_raw_downloads.py; python script/144_build_priority_lsms_isa_raw_package_intake_packet.py; python script/145_build_priority_lsms_isa_archive_member_preflight.py; python script/149_build_priority_lsms_isa_raw_value_verification_workbook.py; python script/150_build_priority_lsms_isa_raw_package_receipt_checklist.py; python script/152_build_priority_lsms_isa_credentialed_raw_acquisition_workbench.py; python script/153_validate_priority_lsms_isa_official_file_receipt.py; python script/132_build_priority_analysis_dataset_synthesis_blueprint.py; python script/148_build_priority_lsms_isa_country_wave_promotion_packets.py; python script/151_refresh_refocused_promoted_country_wave_registry.py; python script/127_enforce_promoted_data_gate.py; python script/36_build_direct_read_audit_bundle.py; python script/14_validate_workspace.py`

## Stop Rule

Do not mark receipt, raw-value verification, climate linkage, or analysis
readiness as passed until the complete official package is present and the raw
value workbook evidence fields are filled from original files.
