# Priority LSMS-ISA Credentialed Raw Acquisition Workbench

Dataset: `ETH_2021_ESPS-W5_v02_M` - Ethiopia 2021-2022

Official get-microdata URL: https://microdata.worldbank.org/catalog/6161/get-microdata

Target folder: `temp/raw_downloads/ETH_2021_ESPS-W5_v02_M/`

Current receipt status: `blocked_no_original_package`

## Manual Download Action

Open official_get_microdata_url, log in or register if required, accept official terms/Data Access Agreement, download the complete unchanged raw package plus all documentation, and place all files in local_target_folder.

Scope: Download the complete unchanged official World Bank package for this IDNO, including all raw microdata files, archives, documentation, questionnaires, codebooks, DDI/XML, and geography/timing supplements exposed after login.

## Core Files To Confirm After Download

| requirement | file_rank | file_name | candidate_variable_rows | top_variable_names |
|---|---|---|---|---|
| climate_geography | 1 | sect_cover_hh_w5.dta | 2 | saq19__Latitude;saq19__Longitude |
| climate_geography | 2 | sect10a_com_w5.dta | 2 | cs10q05__Latitude;cs10q05__Longitude |
| climate_geography | 3 | sect_cover_pp_w5.dta | 2 | saq19__Latitude;saq19__Longitude |
| climate_geography | 4 | sect_cover_ph_w5.dta | 2 | saq19__Latitude;saq19__Longitude |
| climate_geography | 5 | sect_cover_ls_w5.dta | 2 | saq19__Latitude;saq19__Longitude |
| climate_geography | 6 | sect3_pp_w5.dta | 2 | s3q09__Latitude;s3q09__Longitude |
| consumption_or_income | 1 | cons_agg_w5.dta | 12 | nonfood_cons2;nom_nonfoodcons_aeq;nonfood_cons_ann;food_cons2;food_cons_ann;nom_foodcons_aeq;fafh_cons_ann;spat_totco... |
| health_need_and_access | 1 | sect3_hh_w5.dta | 6 | s3q14;s3q15;s3q05;s3q17;s3q13;s3q18 |
| health_need_and_access | 2 | sect04_com_w5.dta | 4 | cs4q37;cs4q34;cs4q35;cs4q28 |
| health_need_and_access | 3 | sect3_pp_w5.dta | 2 | s3q15_1;s3q15_2 |
| household_person_keys | 1 | sect1_hh_w5.dta | 2 | individual_id;household_id |
| household_person_keys | 2 | sect12b1_hh_w5.dta | 1 | household_id |
| household_person_keys | 3 | sect1_pp_w5.dta | 1 | household_id |
| household_person_keys | 4 | sect1_ph_w5.dta | 1 | household_id |
| household_person_keys | 5 | sect2_pp_w5.dta | 1 | household_id |
| household_person_keys | 6 | sect3_pp_w5.dta | 1 | household_id |
| household_person_keys | 7 | sect4_pp_w5.dta | 1 | household_id |
| household_person_keys | 8 | sect6c_hh_w5.dta | 1 | individual_id |
| oop_health_expenditure | 1 | sect8_3_ls_w5.dta | 10 | ls_s8_3q04;ls_s8_3q22;ls_s8_3q24;ls_s8_3q03;ls_s8_3q05;ls_s8_3q06;ls_s8_3q10a;ls_s8_3q10b;ls_s8_3q11;ls_s8_3q12_1 |
| oop_health_expenditure | 2 | sect3_hh_w5.dta | 2 | s3q17;s3q18 |

## Official File Manifest Preview

| file_id | file_name | file_description | case_quantity | variable_quantity | priority_core_target |
|---|---|---|---|---|---|
| F1 | sect_cover_hh_w5.dta | Household Data - Cover page | 4959 | 25 | 1 |
| F2 | sect1_hh_w5.dta | Household Data - Roster | 25374 | 63 | 1 |
| F3 | sect2_hh_w5.dta | Household Data - Education | 22688 | 43 | 0 |
| F4 | sect3_hh_w5.dta | Household Data - Health | 22688 | 69 | 1 |
| F5 | sect3b_hh_w5.dta | Household Data - COVID-19 | 22688 | 23 | 0 |
| F6 | sect4_hh_w5.dta | Household Data - Labor and time use | 22688 | 82 | 0 |
| F7 | sect5a_hh_w5.dta | Banking and financial inclusion | 22688 | 91 | 0 |
| F8 | sect5b_hh_w5.dta | Digital financial services | 22688 | 60 | 0 |
| F9 | sect6a_hh_w5.dta | Household Data - Food consumption last 7 days | 366966 | 28 | 0 |
| F10 | sect6b2_hh_w5.dta | Household Data - Food shared by non-household members (Filter Question) | 4959 | 13 | 1 |
| F11 | sect6b3_hh_w5.dta | Household Data - Food shared by non-household members | 7692 | 15 | 1 |
| F12 | sect6b4_hh_w5.dta | Household Data - Food consumed outside home | 39672 | 19 | 1 |
| F13 | sect6c_hh_w5.dta | Household Data - Dietary quality | 22688 | 47 | 1 |
| F14 | sect7a_hh_w5.dta | Household Data - Nonfood expenditure, one month | 59508 | 15 | 1 |
| F15 | sect7b_hh_w5.dta | Household Data - Nonfood expenditure, 12 months | 64467 | 15 | 1 |
| F16 | sect8_hh_w5.dta | Household Data - Food insecurity experience scale | 4959 | 24 | 1 |
| F17 | sect9_hh_w5.dta | Household Data - Shocks | 94221 | 25 | 0 |
| F18 | sect10a_hh_w5.dta | Household Data - Housing | 4959 | 69 | 0 |
| F19 | sect11_hh_w5.dta | Household Data - Assets | 183483 | 17 | 0 |
| F20 | sect12a_hh_w5.dta | Household Data - Nonfarm enterprises participation filter question | 4959 | 20 | 0 |

## After Placing Files

Run:

`python script/17_audit_raw_downloads.py; python script/144_build_priority_lsms_isa_raw_package_intake_packet.py; python script/145_build_priority_lsms_isa_archive_member_preflight.py; python script/149_build_priority_lsms_isa_raw_value_verification_workbook.py; python script/150_build_priority_lsms_isa_raw_package_receipt_checklist.py; python script/152_build_priority_lsms_isa_credentialed_raw_acquisition_workbench.py; python script/153_validate_priority_lsms_isa_official_file_receipt.py; python script/154_build_priority_lsms_isa_threshold_download_sequence.py; python script/132_build_priority_analysis_dataset_synthesis_blueprint.py; python script/148_build_priority_lsms_isa_country_wave_promotion_packets.py; python script/151_refresh_refocused_promoted_country_wave_registry.py; python script/127_enforce_promoted_data_gate.py; python script/36_build_direct_read_audit_bundle.py; python script/14_validate_workspace.py`

## Stop Rule

Do not mark receipt, raw-value verification, climate linkage, or analysis
readiness as passed until the complete official package is present and the raw
value workbook evidence fields are filled from original files.
