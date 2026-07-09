# Priority LSMS-ISA Credentialed Raw Acquisition Workbench

Dataset: `JAM_1997_SLC_v01_M` - Jamaica 1997

Official get-microdata URL: https://microdata.worldbank.org/catalog/2368/get-microdata

Target folder: `temp/raw_downloads/JAM_1997_SLC_v01_M/`

Current receipt status: `blocked_no_original_package`

## Manual Download Action

Open official_get_microdata_url, log in or register if required, accept official terms/Data Access Agreement, download the complete unchanged raw package plus all documentation, and place all files in local_target_folder.

Scope: Download the complete unchanged official World Bank package for this IDNO, including all raw microdata files, archives, documentation, questionnaires, codebooks, DDI/XML, and geography/timing supplements exposed after login.

## Core Files To Confirm After Download

| requirement | file_rank | file_name | candidate_variable_rows | top_variable_names |
|---|---|---|---|---|
| climate_geography | 1 | REC001.NSDstat | 4 | area;district;parish;region |
| climate_geography | 2 | HEADS.NSDstat | 2 | district;parish |
| climate_geography | 3 | HHSIZE.NSDstat | 2 | district;parish |
| climate_geography | 4 | EXP97.NSDstat | 1 | Cluster |
| climate_geography | 5 | REC034.NSDstat | 1 | xearn |
| climate_geography | 6 | REC041.NSDstat | 1 | year |
| climate_geography | 7 | ANNUAL.NSDstat | 1 | district |
| consumption_or_income | 1 | TOTGIFTS.NSDstat | 4 | t_gfood;serial;tcgift;totgift |
| consumption_or_income | 2 | FOOD.NSDstat | 3 | consgift;giftfood;hpfood |
| consumption_or_income | 3 | MEALS.NSDstat | 3 | consgift;giftfood;hpfood |
| consumption_or_income | 4 | ANNUAL.NSDstat | 1 | non_food |
| consumption_or_income | 5 | TOTFOOD.NSDstat | 1 | t_food |
| health_need_and_access | 1 | REC003.NSDstat | 7 | a09;a10;a17;a13;a16;a181;a182 |
| health_need_and_access | 2 | REC002.NSDstat | 4 | a03;a04;a05;a06 |
| health_need_and_access | 3 | REC004.NSDstat | 1 | a25 |
| household_person_keys | 1 | REC047.NSDstat | 10 | ind;member;age;assist;disabled;hhm1;indiv;marital;part_id;partner |
| household_person_keys | 2 | HEADS.NSDstat | 2 | ind;member |
| oop_health_expenditure | 1 | REC003.NSDstat | 10 | a19;a20;a09;a10;a11;a12;a13;a14;a15;a16 |
| oop_health_expenditure | 2 | REC033.NSDstat | 1 | m05b |
| survey_timing | 1 | REC001.NSDstat | 3 | int_date;ant_date;visits |

## Official File Manifest Preview

| file_id | file_name | file_description | case_quantity | variable_quantity | priority_core_target |
|---|---|---|---|---|---|
| F1 | REC001.NSDstat | Introduction section for questionnaire Jamaica Survey of Living Conditions 1997 | 2020 | 18 | 1 |
| F2 | REC002.NSDstat | Part A: Health, from the questionnaire Jamaica Survey of Living Conditions 1997 | 7282 | 18 | 1 |
| F3 | REC003.NSDstat | Part A: Health, from the questionnaire Jamaica Survey of Living Conditions 1997 | 448 | 17 | 1 |
| F4 | REC004.NSDstat | Part A: Health, from the questionnaire Jamaica Survey of Living Conditions 1997 | 2940 | 7 | 1 |
| F5 | REC005.NSDstat | Part B: Education, from the questionnaire Jamaica Survey of Living Conditions 1997 | 6788 | 16 | 0 |
| F6 | REC006.NSDstat | Part B: Education, from the questionnaire Jamaica Survey of Living Conditions 1997 | 6131 | 19 | 0 |
| F7 | REC007.NSDstat | Part C: For all children 0-59 months, from the questionnaire Jamaica Survey of Living Conditions 1997 | 815 | 23 | 0 |
| F8 | REC008.NSDstat | Part D: Employment and Earnings, from the questionnaire Jamaica Survey of Living Conditions 1997 | 4926 | 11 | 0 |
| F9 | REC009.NSDstat | Part D: Employment and Earnings, from the questionnaire Jamaica Survey of Living Conditions 1997 | 2847 | 21 | 0 |
| F10 | REC010.NSDstat | Part D: Employment and Earnings, from the questionnaire Jamaica Survey of Living Conditions 1997 | 2844 | 10 | 0 |
| F11 | REC011.NSDstat | Part D: Employment and Earnings, from the questionnaire Jamaica Survey of Living Conditions 1997 | 2840 | 10 | 0 |
| F12 | REC012.NSDstat | Part D: Employment and Earnings, from the questionnaire Jamaica Survey of Living Conditions 1997 | 195 | 21 | 0 |
| F13 | REC013.NSDstat | Part D: Employment and Earnings, from the questionnaire Jamaica Survey of Living Conditions 1997 | 195 | 10 | 0 |
| F14 | REC014.NSDstat | Part D: Employment and Earnings, from the questionnaire Jamaica Survey of Living Conditions 1997 | 4814 | 13 | 0 |
| F15 | REC015.NSDstat | Part D: Employment and Earnings, from the questionnaire Jamaica Survey of Living Conditions 1997 | 2015 | 22 | 0 |
| F16 | REC016.NSDstat | Part D: Employment and Earnings, from the questionnaire Jamaica Survey of Living Conditions 1997 | 41 | 16 | 0 |
| F17 | REC017.NSDstat | Part E: Daily Expenses, from the questionnaire Jamaica Survey of Living Conditions 1997 | 3036 | 4 | 0 |
| F18 | REC018.NSDstat | Part F: Food Expenses, from the questionnaire Jamaica Survey of Living Conditions 1997 | 2007 | 3 | 0 |
| F19 | REC019.NSDstat | Part F: Food Expenses, from the questionnaire Jamaica Survey of Living Conditions 1997 | 52026 | 6 | 0 |
| F20 | REC020.NSDstat | Part F: Food Expenses, from the questionnaire Jamaica Survey of Living Conditions 1997 | 925 | 6 | 0 |

## After Placing Files

Run:

`python script/17_audit_raw_downloads.py; python script/144_build_priority_lsms_isa_raw_package_intake_packet.py; python script/145_build_priority_lsms_isa_archive_member_preflight.py; python script/149_build_priority_lsms_isa_raw_value_verification_workbook.py; python script/150_build_priority_lsms_isa_raw_package_receipt_checklist.py; python script/152_build_priority_lsms_isa_credentialed_raw_acquisition_workbench.py; python script/132_build_priority_analysis_dataset_synthesis_blueprint.py; python script/148_build_priority_lsms_isa_country_wave_promotion_packets.py; python script/151_refresh_refocused_promoted_country_wave_registry.py; python script/127_enforce_promoted_data_gate.py; python script/36_build_direct_read_audit_bundle.py; python script/14_validate_workspace.py`

## Stop Rule

Do not mark receipt, raw-value verification, climate linkage, or analysis
readiness as passed until the complete official package is present and the raw
value workbook evidence fields are filled from original files.
