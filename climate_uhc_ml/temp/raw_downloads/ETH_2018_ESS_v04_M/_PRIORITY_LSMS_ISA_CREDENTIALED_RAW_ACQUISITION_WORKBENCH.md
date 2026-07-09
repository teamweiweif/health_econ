# Priority LSMS-ISA Credentialed Raw Acquisition Workbench

Dataset: `ETH_2018_ESS_v04_M` - Ethiopia 2018-2019

Official get-microdata URL: https://microdata.worldbank.org/catalog/3823/get-microdata

Target folder: `temp/raw_downloads/ETH_2018_ESS_v04_M/`

Current receipt status: `blocked_no_original_package`

## Manual Download Action

Open official_get_microdata_url, log in or register if required, accept official terms/Data Access Agreement, download the complete unchanged raw package plus all documentation, and place all files in local_target_folder.

Scope: Download the complete unchanged official World Bank package for this IDNO, including all raw microdata files, archives, documentation, questionnaires, codebooks, DDI/XML, and geography/timing supplements exposed after login.

## Core Files To Confirm After Download

| requirement | file_rank | file_name | candidate_variable_rows | top_variable_names |
|---|---|---|---|---|
| climate_geography | 1 | sect_cover_ph_w4.dta | 3 | saq19__Latitude;saq19__Longitude;ea_id |
| climate_geography | 2 | sect_cover_pp_w4.dta | 2 | saq19__Latitude;saq19__Longitude |
| climate_geography | 3 | sect_cover_ls_w4.dta | 2 | saq19__Latitude;saq19__Longitude |
| climate_geography | 4 | sect3_pp_w4.dta | 2 | s3q09__Latitude;s3q09__Longitude |
| climate_geography | 5 | sect10a_com_w4.dta | 2 | cs10q05__Latitude;cs10q05__Longitude |
| climate_geography | 6 | sect_cover_hh_w4.dta | 1 | ea_id |
| consumption_or_income | 1 | sect7a_hh_w4.dta | 9 | ea_id;household_id;item_cd_30day;pw_w4;s7q01;s7q02;saq01;saq02;saq03 |
| consumption_or_income | 2 | cons_agg_w4.dta | 3 | nom_nonfoodcons_aeq;nonfood_cons_ann;food_cons_ann |
| health_need_and_access | 1 | sect3_hh_w4.dta | 11 | s3q14;s3q15;s3q05;s3q17;s3q13;s3q18;s3q06_1;s3q06_2;s3q06_os;s3q09a;s3q09b |
| health_need_and_access | 2 | sect04_com_w4.dta | 1 | cs4q37 |
| household_person_keys | 1 | sect1_hh_w4.dta | 2 | individual_id;household_id |
| household_person_keys | 2 | sect11b1_hh_w4.dta | 2 | individual_id;household_id |
| household_person_keys | 3 | sect10d1_hh_w4.dta | 1 | household_id |
| household_person_keys | 4 | sect1_ph_w4.dta | 1 | household_id |
| household_person_keys | 5 | sect1_pp_w4.dta | 1 | household_id |
| household_person_keys | 6 | sect10b_hh_w4.dta | 1 | household_id |
| household_person_keys | 7 | sect2_pp_w4.dta | 1 | household_id |
| household_person_keys | 8 | sect3_pp_w4.dta | 1 | household_id |
| oop_health_expenditure | 1 | sect8_3_ls_w4.dta | 10 | ls_s8_3q04;ls_s8_3q22;ls_s8_3q24;ls_s8_3q03;ls_s8_3q05;ls_s8_3q06;ls_s8_3q10a;ls_s8_3q10b;ls_s8_3q11;ls_s8_3q12_1 |
| oop_health_expenditure | 2 | sect3_hh_w4.dta | 2 | s3q17;s3q18 |

## Official File Manifest Preview

| file_id | file_name | file_description | case_quantity | variable_quantity | priority_core_target |
|---|---|---|---|---|---|
| F1 | sect_cover_hh_w4.dta | Household identification; location; household size, and field staff identification | 6770 | 20 | 1 |
| F2 | sect1_hh_w4.dta | Roster - List of individuals living in the household and basic demographics; for members younger than 18, parental ed... | 29503 | 42 | 1 |
| F3 | sect2_hh_w4.dta | Education - Educational attainment, enrollment, attendance, school characteristics, and expenditures for the 2018‒19 ... | 29503 | 39 | 0 |
| F4 | sect3_hh_w4.dta | Health - Health problems, types of injury/illness, medical assistance/consultation, health insurance, disabilities, v... | 29503 | 69 | 1 |
| F5 | sect4_hh_w4.dta | Labor and time use - Time use, labor market participation in the last 7 days and the last 12 months, unpaid apprentic... | 29503 | 82 | 0 |
| F6 | sect5a_hh_w4.dta | Banking and financial inclusion - Saving, financial literacy, insurance, and financial practices. | 29503 | 84 | 0 |
| F7 | sect5b1_hh_w4.dta | Financial assets - Individual disaggregated financial asset module: Ownership of financial asset accounts (exclusivel... | 74550 | 17 | 0 |
| F8 | sect5b2_hh_w4.dta | Financial assets - Individual disaggregated financial asset module: Value of financial assets owned privately or join... | 6433 | 37 | 0 |
| F9 | sect6a_hh_w4.dta | Food consumption, last 7 days - Household food consumption (quantity and value) in the last 7 days and source of food... | 494210 | 28 | 0 |
| F10 | sect6b1_hh_w4.dta | Food aggregate, last 7 days - Summary on consumption of food in the last 7 days. Dietary diversification. | 108320 | 15 | 0 |
| F11 | sect6b2_hh_w4.dta | Meals shared with non-household members, last 7 days - Meal sharing with non-household members (number of persons and... | 6770 | 13 | 1 |
| F12 | sect6b3_hh_w4.dta | Food consumed away from home, last 7 days - Total number of days and total number of meals shared with people (groupe... | 7376 | 15 | 0 |
| F13 | sect6b4_hh_w4.dta | Food consumed away from home, last 7 days - Type and value of meals consumed away from home om the last 7 days. | 54160 | 15 | 0 |
| F14 | sect7a_hh_w4.dta | Nonfood expenditure - Household monthly expenditures on nonfood items. | 88010 | 15 | 1 |
| F74 | sect7b_hh_w4.dta | Nonfood expenditure - Household 12 months expenditures on nonfood items. | 88010 | 15 | 0 |
| F17 | sect8_hh_w4.dta | Food security - Food Insecurity Experience Scale (FIES) for the last 7 days and food shortage experience for the last... | 6770 | 46 | 0 |
| F18 | sect9_hh_w4.dta | Shocks - Shocks during the last 12 months and their impact on income, assets, food production, shock and purchase. St... | 135400 | 25 | 1 |
| F19 | sect10a_hh_w4.dta | Housing - Dwelling ownership and property tax, characteristics of the dwelling and utilities, including WASH indicato... | 6770 | 68 | 0 |
| F20 | sect10b_hh_w4.dta | Land parcel roster - Individual disaggregated land roster | 12832 | 24 | 1 |
| F21 | sect10c_hh_w4.dta | Land and dwelling assets - Individual disaggregated land ownership and right | 29363 | 213 | 0 |

## After Placing Files

Run:

`python script/17_audit_raw_downloads.py; python script/144_build_priority_lsms_isa_raw_package_intake_packet.py; python script/145_build_priority_lsms_isa_archive_member_preflight.py; python script/149_build_priority_lsms_isa_raw_value_verification_workbook.py; python script/150_build_priority_lsms_isa_raw_package_receipt_checklist.py; python script/152_build_priority_lsms_isa_credentialed_raw_acquisition_workbench.py; python script/153_validate_priority_lsms_isa_official_file_receipt.py; python script/154_build_priority_lsms_isa_threshold_download_sequence.py; python script/132_build_priority_analysis_dataset_synthesis_blueprint.py; python script/148_build_priority_lsms_isa_country_wave_promotion_packets.py; python script/151_refresh_refocused_promoted_country_wave_registry.py; python script/127_enforce_promoted_data_gate.py; python script/36_build_direct_read_audit_bundle.py; python script/14_validate_workspace.py`

## Stop Rule

Do not mark receipt, raw-value verification, climate linkage, or analysis
readiness as passed until the complete official package is present and the raw
value workbook evidence fields are filled from original files.
