# Priority LSMS-ISA Credentialed Raw Acquisition Workbench

Dataset: `NGA_2012_GHSP-W2_v02_M` - Nigeria 2012-2013

Official get-microdata URL: https://microdata.worldbank.org/catalog/1952/get-microdata

Target folder: `temp/raw_downloads/NGA_2012_GHSP-W2_v02_M/`

Current receipt status: `blocked_no_original_package`

## Manual Download Action

Open official_get_microdata_url, log in or register if required, accept official terms/Data Access Agreement, download the complete unchanged raw package plus all documentation, and place all files in local_target_folder.

Scope: Download the complete unchanged official World Bank package for this IDNO, including all raw microdata files, archives, documentation, questionnaires, codebooks, DDI/XML, and geography/timing supplements exposed after login.

## Core Files To Confirm After Download

| requirement | file_rank | file_name | candidate_variable_rows | top_variable_names |
|---|---|---|---|---|
| climate_geography | 1 | HHTrack | 4 | ea;lga;state;zone |
| climate_geography | 2 | secta_harvestw2 | 4 | ea;lga;state;zone |
| climate_geography | 3 | NGA_HouseholdGeovars_Y2 | 2 | LAT_DD_MOD;LON_DD_MOD |
| climate_geography | 4 | cons_agg_wave2_visit1 | 1 | ea |
| climate_geography | 5 | cons_agg_wave2_visit2 | 1 | ea |
| consumption_or_income | 1 | cons_agg_wave2_visit1 | 5 | totcons;nfdfoth;fdfishpr;fdothpr;fdrestby |
| consumption_or_income | 2 | cons_agg_wave2_visit2 | 5 | totcons;nfdfoth;fdfishpr;fdothpr;fdrestby |
| consumption_or_income | 3 | sect8e_plantingw2 | 1 | s8q10 |
| consumption_or_income | 4 | sect8a_plantingw2 | 1 | ea |
| health_need_and_access | 1 | sect4a_harvestw2 | 9 | s4aq15;s4aq16;s4aq17;s4aq1;s4aq3;s4aq20;s4aq6a;s4aq6b;s4aq6c |
| health_need_and_access | 2 | secta7_harvestw2 | 2 | cost_cd;cost_desc |
| health_need_and_access | 3 | sect4b_harvestw2 | 1 | s4bq3 |
| household_person_keys | 1 | sect1_plantingw2 | 1 | hhid |
| household_person_keys | 2 | sect1_harvestw2 | 1 | hhid |
| household_person_keys | 3 | secta10_harvestw2 | 1 | hhid |
| household_person_keys | 4 | sect11a_plantingw2 | 1 | hhid |
| household_person_keys | 5 | sect11a1_plantingw2 | 1 | hhid |
| household_person_keys | 6 | sect12_plantingw2 | 1 | hhid |
| household_person_keys | 7 | HHTrack | 1 | hhid |
| household_person_keys | 8 | secta_harvestw2 | 1 | hhid |

## Official File Manifest Preview

| file_id | file_name | file_description | case_quantity | variable_quantity | priority_core_target |
|---|---|---|---|---|---|
| F18 | NGA_HouseholdGeovars_Y2 |  | 4803 | 48 | 1 |
| F19 | NGA_PlotGeovariables_Y2 |  | 5340 | 12 | 0 |
| F20 | sect1_plantingw2 | Data collected using Post Planting Household Questionnaire, Section 1 (Household Roster). The data also contains geog... | 29315 | 66 | 1 |
| F21 | sect2_plantingw2 | Data collected using Post Planting Household Questionnaire, Section 2 (Education). The data also contains geographic ... | 27165 | 47 | 0 |
| F22 | sect3a_plantingw2 | Data collected using Post Planting Household Questionnaire, Section 3A (Labor - 7 days). The data also contains geogr... | 26529 | 67 | 0 |
| F23 | sect3b_plantingw2 | Data collected using Post Planting Household Questionnaire, Section 3B (Labor - 12 months). The data also contains ge... | 6295 | 29 | 0 |
| F24 | sect3c_plantingw2 | Data collected using Post Planting Household Questionnaire, Section 3C (Labor - 6 months). The data also contains geo... | 4930 | 29 | 0 |
| F25 | sect3d_plantingw2 | Data collected using Post Planting Household Questionnaire, Section 3D (Labor Activity Table). The data also contains... | 6712 | 43 | 0 |
| F26 | sect3e_plantingw2 | Data collected using Post Planting Household Questionnaire, Section 3E (Labor Activity Summary). The data also contai... | 7056 | 30 | 0 |
| F27 | sect4a_plantingw2 | Data collected using Post Planting Household Questionnaire, Section 4A (Credit and Savings). The data also contains g... | 16200 | 46 | 0 |
| F28 | sect4b_plantingw2 | Data collected using Post Planting Household Questionnaire, Section 4B (Financial Capability). The data also contains... | 18055 | 38 | 0 |
| F29 | sect5a_plantingw2 | Data collected using Post Planting Household Questionnaire, Section 5a (Household Assets). The data also contains geo... | 161364 | 10 | 0 |
| F30 | sect5b_plantingw2 | Data collected using Post Planting Household Questionnaire, Section 5b (Household Assets). The data also contains geo... | 54171 | 12 | 0 |
| F31 | sect6_plantingw2 | Data collected using Post Planting Household Questionnaire, Section 6 (Non-Farm Enterprises and Income Generating Act... | 5367 | 75 | 0 |
| F32 | sect7a_plantingw2 | Data collected using Post Planting Household Questionnaire, Section 7A (Meals away from home). The data also contains... | 42273 | 11 | 0 |
| F33 | sect7b_plantingw2 | Data collected using Post Planting Household Questionnaire, Section 7B (Food Expenditure). The data also contains geo... | 450906 | 21 | 0 |
| F34 | sect8a_plantingw2 | Data collected using Post Planting Household Questionnaire, Section 8A (Non-Food Expenditure - 7 days). The data also... | 18788 | 11 | 1 |
| F35 | sect8b_plantingw2 | Data collected using Post Planting Household Questionnaire, Section 8B (Non-Food Expenditure - One month recall). The... | 136213 | 11 | 0 |
| F36 | sect8c_plantingw2 | Data collected using Post Planting Household Questionnaire, Section 8C (Non-Food Expenditure - 6 months recall). The ... | 140910 | 11 | 0 |
| F37 | sect8d_plantingw2 | Data collected using Post Planting Household Questionnaire, Section 8d (Non-Food Expenditure - 12 months recall). The... | 79849 | 11 | 0 |

## After Placing Files

Run:

`python script/17_audit_raw_downloads.py; python script/144_build_priority_lsms_isa_raw_package_intake_packet.py; python script/145_build_priority_lsms_isa_archive_member_preflight.py; python script/149_build_priority_lsms_isa_raw_value_verification_workbook.py; python script/150_build_priority_lsms_isa_raw_package_receipt_checklist.py; python script/152_build_priority_lsms_isa_credentialed_raw_acquisition_workbench.py; python script/153_validate_priority_lsms_isa_official_file_receipt.py; python script/154_build_priority_lsms_isa_threshold_download_sequence.py; python script/132_build_priority_analysis_dataset_synthesis_blueprint.py; python script/148_build_priority_lsms_isa_country_wave_promotion_packets.py; python script/151_refresh_refocused_promoted_country_wave_registry.py; python script/127_enforce_promoted_data_gate.py; python script/36_build_direct_read_audit_bundle.py; python script/14_validate_workspace.py`

## Stop Rule

Do not mark receipt, raw-value verification, climate linkage, or analysis
readiness as passed until the complete official package is present and the raw
value workbook evidence fields are filled from original files.
