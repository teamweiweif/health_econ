# Priority LSMS-ISA Credentialed Raw Acquisition Workbench

Dataset: `NGA_2010_GHSP-W1_v03_M` - Nigeria 2010-2011

Official get-microdata URL: https://microdata.worldbank.org/catalog/1002/get-microdata

Target folder: `temp/raw_downloads/NGA_2010_GHSP-W1_v03_M/`

Current receipt status: `blocked_no_original_package`

## Manual Download Action

Open official_get_microdata_url, log in or register if required, accept official terms/Data Access Agreement, download the complete unchanged raw package plus all documentation, and place all files in local_target_folder.

Scope: Download the complete unchanged official World Bank package for this IDNO, including all raw microdata files, archives, documentation, questionnaires, codebooks, DDI/XML, and geography/timing supplements exposed after login.

## Core Files To Confirm After Download

| requirement | file_rank | file_name | candidate_variable_rows | top_variable_names |
|---|---|---|---|---|
| climate_geography | 1 | NGA_HouseholdGeovariables_Y1 | 10 | lat_dd_mod;lon_dd_mod;ea;eviarea_avg;grn_avg;h2010_eviarea;h2010_grn;h2010_sen;lga;sen_avg |
| climate_geography | 2 | cons_agg_wave1_visit1 | 1 | ea |
| climate_geography | 3 | cons_agg_wave1_visit2 | 1 | ea |
| consumption_or_income | 1 | cons_agg_wave1_visit1 | 7 | totcons;nfdfoth;fdfishpr;fdothpr;fdrestby;fdalcpr;fdbeanpr |
| consumption_or_income | 2 | cons_agg_wave1_visit2 | 5 | totcons;nfdfoth;fdfishpr;fdothpr;fdrestby |
| health_need_and_access | 1 | sect4a_harvestw1 | 10 | s4aq15;s4aq16;s4aq17;s4aq1;s4aq3;s4aq6a;s4aq6b;s4aq6c;s4aq20;s4aq20b |
| health_need_and_access | 2 | sect4b_harvestw1 | 1 | s4bq3 |
| health_need_and_access | 3 | sect3a_harvestw1 | 1 | s3aq17 |
| household_person_keys | 1 | secta7_harvestw1 | 1 | hhid |
| household_person_keys | 2 | secta8_harvestw1 | 1 | hhid |
| household_person_keys | 3 | secta9a1_harvestw1 | 1 | hhid |
| household_person_keys | 4 | secta9a2_harvestw1 | 1 | hhid |
| household_person_keys | 5 | secta9b1_harvestw1 | 1 | hhid |
| household_person_keys | 6 | secta9b2_harvestw1 | 1 | hhid |
| household_person_keys | 7 | secta10_harvestw1 | 1 | hhid |
| household_person_keys | 8 | secta41_harvestw1 | 1 | hhid |
| oop_health_expenditure | 1 | sect4a_harvestw1 | 5 | s4aq20;s4aq20b;s4aq19;s4aq13;s4aq17 |
| survey_timing | 1 | secta_harvestw1 | 11 | saq14ah;saq14am;saq14bh;saq14bm;saq18ah;saq18am;saq18bh;saq18bm;saq22ah;saq22am;saq22bh |
| survey_timing | 2 | sectc_plantingw1 | 1 | interview_date |
| weights_and_design | 1 | cons_agg_wave1_visit1 | 2 | ea;hhweight |

## Official File Manifest Preview

| file_id | file_name | file_description | case_quantity | variable_quantity | priority_core_target |
|---|---|---|---|---|---|
| F1 | w1agnsconversion |  | 2111 | 4 | 0 |
| F2 | NGA_HouseholdGeovariables_Y1 |  | 5000 | 47 | 1 |
| F3 | NGA_PlotGeovariables_Y1 |  | 5135 | 12 | 0 |
| F4 | secta1_harvestw1 |  | 6316 | 72 | 0 |
| F5 | secta2_harvestw1 |  | 5352 | 41 | 0 |
| F6 | secta3_harvestw1 |  | 13018 | 45 | 0 |
| F7 | secta5a_harvestw1 |  | 772 | 11 | 0 |
| F8 | secta5b_harvestw1 |  | 370 | 19 | 0 |
| F9 | secta6_harvestw1 |  | 4920 | 50 | 0 |
| F10 | secta7_harvestw1 |  | 1478 | 13 | 1 |
| F11 | secta8_harvestw1 |  | 291 | 15 | 1 |
| F12 | secta9a1_harvestw1 |  | 166 | 8 | 1 |
| F13 | secta9a2_harvestw1 |  | 61 | 50 | 1 |
| F14 | secta9b1_harvestw1 |  | 27 | 13 | 1 |
| F15 | secta9b2_harvestw1 |  | 10 | 38 | 1 |
| F16 | secta10_harvestw1 |  | 5701 | 11 | 1 |
| F17 | secta41_harvestw1 |  | 7326 | 11 | 1 |
| F18 | secta42_harvestw1 |  | 8661 | 18 | 0 |
| F19 | sectaa_harvestw1 |  | 3220 | 6 | 0 |
| F20 | sectc_harvestw1 |  | 494 | 12 | 0 |

## After Placing Files

Run:

`python script/17_audit_raw_downloads.py; python script/144_build_priority_lsms_isa_raw_package_intake_packet.py; python script/145_build_priority_lsms_isa_archive_member_preflight.py; python script/149_build_priority_lsms_isa_raw_value_verification_workbook.py; python script/150_build_priority_lsms_isa_raw_package_receipt_checklist.py; python script/152_build_priority_lsms_isa_credentialed_raw_acquisition_workbench.py; python script/153_validate_priority_lsms_isa_official_file_receipt.py; python script/132_build_priority_analysis_dataset_synthesis_blueprint.py; python script/148_build_priority_lsms_isa_country_wave_promotion_packets.py; python script/151_refresh_refocused_promoted_country_wave_registry.py; python script/127_enforce_promoted_data_gate.py; python script/36_build_direct_read_audit_bundle.py; python script/14_validate_workspace.py`

## Stop Rule

Do not mark receipt, raw-value verification, climate linkage, or analysis
readiness as passed until the complete official package is present and the raw
value workbook evidence fields are filled from original files.
