# Minimum Batch Raw Intake Guide

IDNO: `TZA_2008_NPS-R1_v03_M`

Country-wave: Tanzania 2008-2009

Threshold rank: 7

Role: minimum_10_wave_core

Official World Bank microdata URL: https://microdata.worldbank.org/catalog/76/get-microdata

Target folder: `temp/raw_downloads/TZA_2008_NPS-R1_v03_M/`

## Current Receipt Status

- Expected full official files: 61
- Matched full official files: 0
- Missing full official files: 61
- Expected core files: 35
- Matched core files: 0
- Missing core files: 35
- Official receipt status: `blocked_no_original_package`

## Core Files To Confirm

| requirement | file_rank | file_id | expected_file_name | top_variable_names | official_core_file_match_status |
|---|---|---|---|---|---|
| climate_geography | 1 | F27 | HH.Geovariables_Y1 | ea_id;lat_modified;lon_modified | missing_expected_core_file |
| climate_geography | 2 | F39 | SEC_A_T_English_Labels | clusterid;ea | missing_expected_core_file |
| climate_geography | 3 | F1 | SEC_A_T_Swahili_Labels | ea | missing_expected_core_file |
| climate_geography | 4 | F29 | SECTA1A2_Swahili_Labels | ea_id | missing_expected_core_file |
| climate_geography | 5 | F32 | SECTCB_Swahili_Labels | ea_id | missing_expected_core_file |
| climate_geography | 6 | F35 | SECTCEFG | ea_id | missing_expected_core_file |
| climate_geography | 7 | F36 | SECTCH | ea_id | missing_expected_core_file |
| climate_geography | 8 | F37 | SECTCI | ea_id | missing_expected_core_file |
| consumption_or_income | 1 | F69 | TZY1.HH.Consumption | hhexpenses;hhexpensesR;expm;expmR | missing_expected_core_file |
| consumption_or_income | 2 | F10 | SEC_L_Swahili_Labels | hhid;slcode;slq1;slq2 | missing_expected_core_file |
| consumption_or_income | 3 | F11 | SEC_M_Swahili_Labels | hhid;smcode;smq1;smq2 | missing_expected_core_file |
| health_need_and_access | 1 | F40 | SEC_B_C_D_E1_F_G1_U_English_Labels | sdq22;sdq4;sdq43_1;sdq43_2;sdq43_3;sdq55_1;sdq55_2;sdq55_3;sdq6;sdq8;sdq9 | missing_expected_core_file |
| health_need_and_access | 2 | F47 | SEC_I_English_Labels | siq8b | missing_expected_core_file |
| household_person_keys | 1 | F20 | Agriculture SEC_1_ALL_Swahili_Labels | hhid;rosterid | missing_expected_core_file |
| household_person_keys | 2 | F2 | SEC_B_C_D_E1_F_G1_U_Swahili_Labels | hhid | missing_expected_core_file |
| household_person_keys | 3 | F21 | SEC_2A_Swahili_Labels | hhid | missing_expected_core_file |
| household_person_keys | 4 | F22 | SEC_2B_Swahili_Labels | hhid | missing_expected_core_file |
| household_person_keys | 5 | F40 | SEC_B_C_D_E1_F_G1_U_English_Labels | hhid | missing_expected_core_file |
| household_person_keys | 6 | F59 | SEC_2A_English_Labels | hhid | missing_expected_core_file |
| household_person_keys | 7 | F60 | SEC_2B_English_Labels | hhid | missing_expected_core_file |
| household_person_keys | 8 | F1 | SEC_A_T_Swahili_Labels | hhid | missing_expected_core_file |
| oop_health_expenditure | 1 | F40 | SEC_B_C_D_E1_F_G1_U_English_Labels | scq14_fee;scq14_food;sdq6;sdq7;scq14_bks;scq14_contr;scq14_tot;scq14_trans;scq14_tui;scq14_unif;sdq5 | missing_expected_core_file |
| oop_health_expenditure | 2 | F2 | SEC_B_C_D_E1_F_G1_U_Swahili_Labels | scq14_fee | missing_expected_core_file |
| survey_timing | 1 | F1 | SEC_A_T_Swahili_Labels | endmin;sa2q17endhr;sa2q17starthr;sa2q17startmins | missing_expected_core_file |
| survey_timing | 2 | F39 | SEC_A_T_English_Labels | endmin;sa2q17endhr;sa2q17starthr | missing_expected_core_file |
| survey_timing | 3 | F65 | SECTA1A2_English_Labels | ca07m;ca07y | missing_expected_core_file |
| survey_timing | 4 | F18 | SEC_R_Swahili_Labels | srq5month;srq5year | missing_expected_core_file |
| survey_timing | 5 | F69 | TZY1.HH.Consumption | intmonth | missing_expected_core_file |
| weights_and_design | 1 | F39 | SEC_A_T_English_Labels | hh_weight;hh_weight_trimmed;ea;strataid | missing_expected_core_file |
| weights_and_design | 2 | F26 | nps_weights_oct2010 | hh_weight;hh_weight_trimmed;strataid | missing_expected_core_file |

## Intake Steps

1. Use the official World Bank link above after login, terms, or Data Access Agreement acceptance.
2. Download the complete official package and documentation. Keep original archive names where possible.
3. Place the unchanged package or extracted original files under the target folder.
4. Rerun the post-download commands below.
5. Review raw-value, outcome, timing, geography, and climate-linkage gates before any promotion.

```bash
python script/17_audit_raw_downloads.py; python script/144_build_priority_lsms_isa_raw_package_intake_packet.py; python script/145_build_priority_lsms_isa_archive_member_preflight.py; python script/150_build_priority_lsms_isa_raw_package_receipt_checklist.py; python script/152_build_priority_lsms_isa_credentialed_raw_acquisition_workbench.py; python script/153_validate_priority_lsms_isa_official_file_receipt.py; python script/154_build_priority_lsms_isa_threshold_download_sequence.py; python script/155_build_priority_lsms_isa_minimum_batch_raw_intake_guide.py; python script/156_probe_priority_lsms_isa_minimum_batch_endpoint_refresh.py; python script/149_build_priority_lsms_isa_raw_value_verification_workbook.py; python script/132_build_priority_analysis_dataset_synthesis_blueprint.py; python script/148_build_priority_lsms_isa_country_wave_promotion_packets.py; python script/151_refresh_refocused_promoted_country_wave_registry.py; python script/127_enforce_promoted_data_gate.py; python script/36_build_direct_read_audit_bundle.py; python script/14_validate_workspace.py
```

## Stop Rule

Do not write this country-wave into data/ or run ML until complete official file receipt, raw-value verification, outcome construction, survey timing/geography, and accepted CHIRPS or ERA5 climate linkage all pass.
