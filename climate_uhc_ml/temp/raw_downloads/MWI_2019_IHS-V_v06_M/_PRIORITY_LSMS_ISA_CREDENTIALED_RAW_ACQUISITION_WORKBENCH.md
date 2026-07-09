# Priority LSMS-ISA Credentialed Raw Acquisition Workbench

Dataset: `MWI_2019_IHS-V_v06_M` - Malawi 2019-2020

Official get-microdata URL: https://microdata.worldbank.org/catalog/3818/get-microdata

Target folder: `temp/raw_downloads/MWI_2019_IHS-V_v06_M/`

Current receipt status: `blocked_no_original_package`

## Manual Download Action

Open official_get_microdata_url, log in or register if required, accept official terms/Data Access Agreement, download the complete unchanged raw package plus all documentation, and place all files in local_target_folder.

Scope: Download the complete unchanged official World Bank package for this IDNO, including all raw microdata files, archives, documentation, questionnaires, codebooks, DDI/XML, and geography/timing supplements exposed after login.

## Core Files To Confirm After Download

| requirement | file_rank | file_name | candidate_variable_rows | top_variable_names |
|---|---|---|---|---|
| climate_geography | 1 | householdgeovariables_ihs5.dta | 3 | ea_id;ea_lat_mod;ea_lon_mod |
| climate_geography | 2 | ihs5_consumption_aggregate.dta | 2 | area;ea_id |
| climate_geography | 3 | ag_mod_j.dta | 2 | ag_j06e;ag_j06e_oth |
| climate_geography | 4 | ag_mod_o2.dta | 2 | ag_o05e;ag_o05e_oth |
| climate_geography | 5 | hh_mod_a_filt.dta | 1 | ea_id |
| climate_geography | 6 | ag_mod_c.dta | 1 | ag_c05e_oth |
| climate_geography | 7 | HH_MOD_F1.dta | 1 | hh_f102e |
| consumption_or_income | 1 | HH_MOD_I1.dta | 5 | case_id;hh_i01;hh_i02;hh_i03;HHID |
| consumption_or_income | 2 | HH_MOD_G1.dta | 2 | hh_g00_2;hh_g00_1 |
| consumption_or_income | 3 | HH_MOD_I2.dta | 2 | case_id;hh_i04 |
| consumption_or_income | 4 | HH_MOD_K1.dta | 1 | hh_k03 |
| consumption_or_income | 5 | HH_MOD_K2.dta | 1 | hh_k03 |
| consumption_or_income | 6 | HH_MOD_T.dta | 1 | hh_t01 |
| health_need_and_access | 1 | HH_MOD_D.dta | 8 | hh_d34a;hh_d34b;hh_d04;hh_d05_oth;hh_d11;hh_d13;hh_d14;hh_d05a |
| health_need_and_access | 2 | com_cd.dta | 4 | com_cd60a;com_cd53;com_cd54;com_cd51a |
| household_person_keys | 1 | HH_MOD_B.dta | 1 | case_id |
| household_person_keys | 2 | ag_mod_c.dta | 1 | case_id |
| household_person_keys | 3 | ag_mod_j.dta | 1 | case_id |
| household_person_keys | 4 | ag_mod_o2.dta | 1 | case_id |
| household_person_keys | 5 | HH_MOD_F1.dta | 1 | case_id |

## Official File Manifest Preview

| file_id | file_name | file_description | case_quantity | variable_quantity | priority_core_target |
|---|---|---|---|---|---|
| F1 | HH_MOD_META.dta | Household questionnaire metadata | 11434 | 119 | 1 |
| F2 | hh_mod_a_filt.dta | Data collected through Household Questionnaire, Module A: Household Identification (household level data) - This modu... | 11434 | 21 | 1 |
| F3 | HH_MOD_B.dta | Data collected through Household Questionnaire, Module B: Household Roster ( individual level data) - This module con... | 50476 | 53 | 1 |
| F4 | HH_MOD_C.dta | Data collected through Household Questionnaire, Module C: Education (individual level data) - The education module is... | 50476 | 57 | 0 |
| F5 | HH_MOD_D.dta | Data collected through Household Questionnaire, Module D: Health (individual level data) - The health module is admin... | 50476 | 60 | 1 |
| F6 | HH_MOD_E.dta | Data collected through Household Questionnaire, Module E: Time Use and Labour – individual level data - The module is... | 50476 | 159 | 0 |
| F7 | HH_MOD_F.dta | Data collected through Household Questionnaire, Module F: Housing - household level data - This module on housing is ... | 11434 | 115 | 0 |
| F8 | HH_MOD_F1.dta | Data collected through Household Questionnaire, Module F1: Land Roster - This is a new module and it collects informa... | 27121 | 111 | 1 |
| F9 | HH_MOD_G1.dta | Data collected through Household Questionnaire, Module G: Food Consumption Over Past One Week – consumption item leve... | 1623628 | 32 | 1 |
| F10 | HH_MOD_G2.dta | Data collected through Household Questionnaire, Module G: Food Consumption Over Past One Week – food group (aggregate) | 11433 | 12 | 0 |
| F11 | HH_MOD_G3.dta | Data collected through Household Questionnaire, Module G: Food Consumption Over Past One Week – age group (aggregate) | 23071 | 6 | 0 |
| F12 | HH_MOD_H.dta | Data collected through Household Questionnaire, Module H: Food security – household level - This module collects info... | 11434 | 41 | 0 |
| F13 | HH_MOD_I1.dta | Data collected through Household Questionnaire, Module I: Non-food Expenditures Over Past One Week and One Month – co... | 102906 | 5 | 1 |
| F14 | HH_MOD_I2.dta | Data collected through Household Questionnaire, Module I: Non-food Expenditures Over Past One Week and One Month – co... | 228680 | 5 | 1 |
| F15 | HH_MOD_J.dta | Data collected through Household Questionnaire, Module J: Non-food Expenditures Over Past Three Months – consumption ... | 480228 | 5 | 0 |
| F16 | HH_MOD_K1.dta | Data collected through Household Questionnaire, Module K: Non-food Expenditures Over Past 12 Months – consumption ite... | 205812 | 5 | 1 |
| F17 | HH_MOD_K2.dta | Data collected through Household Questionnaire, Module K: Non-food Expenditures Over Past 12 Months - consumption ite... | 22868 | 6 | 1 |
| F18 | HH_MOD_L.dta | Data collected through Household Questionnaire, Module L: Durable Goods - durable item level - This module collects i... | 388756 | 9 | 0 |
| F19 | HH_MOD_M.dta | Data collected through Household Questionnaire, Module M: Farm Implements, Machinery, and Structures - This module co... | 285850 | 20 | 0 |
| F20 | HH_MOD_N1.dta | Data collected through Household Questionnaire, Module N: Household Enterprises – household level data (questions 1 t... | 11434 | 10 | 0 |

## After Placing Files

Run:

`python script/17_audit_raw_downloads.py; python script/144_build_priority_lsms_isa_raw_package_intake_packet.py; python script/145_build_priority_lsms_isa_archive_member_preflight.py; python script/149_build_priority_lsms_isa_raw_value_verification_workbook.py; python script/150_build_priority_lsms_isa_raw_package_receipt_checklist.py; python script/152_build_priority_lsms_isa_credentialed_raw_acquisition_workbench.py; python script/132_build_priority_analysis_dataset_synthesis_blueprint.py; python script/148_build_priority_lsms_isa_country_wave_promotion_packets.py; python script/151_refresh_refocused_promoted_country_wave_registry.py; python script/127_enforce_promoted_data_gate.py; python script/36_build_direct_read_audit_bundle.py; python script/14_validate_workspace.py`

## Stop Rule

Do not mark receipt, raw-value verification, climate linkage, or analysis
readiness as passed until the complete official package is present and the raw
value workbook evidence fields are filled from original files.
