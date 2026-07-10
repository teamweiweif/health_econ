# Manual Download Packet: TZA_2008_NPS-R1_v03_M

Status: credentialed/manual official raw package acquisition packet.
This packet does not download raw data, accept terms, extract microdata,
write `data/`, or run models.

## Target

- Country: Tanzania
- Wave: 2008-2009
- IDNO: TZA_2008_NPS-R1_v03_M
- Official get-microdata URL: https://microdata.worldbank.org/catalog/76/get-microdata
- Local target folder: `temp/raw_downloads/TZA_2008_NPS-R1_v03_M/`
- Expected official files: 61
- Missing expected files: 61
- Requirement-linked core file rows: 35
- Missing core file rows: 35

## Manual Action

Login/register at the official World Bank Microdata get-microdata page, accept terms if required, download the complete unchanged official raw package and documentation, and place every file under the local target folder.

## Core Files To Confirm After Download

| requirement | file_id | expected_file_name | file_description | top_variable_names | official_core_file_match_status |
| --- | --- | --- | --- | --- | --- |
| climate_geography | F27 | HH.Geovariables_Y1 |  | ea_id;lat_modified;lon_modified | missing_expected_core_file |
| climate_geography | F39 | SEC_A_T_English_Labels | SECTION A-1: Household Identification SECTION T-1: Household Recontact Information SECTION T-2: Filter Questions for Ag Module This file contains data with English labels | clusterid;ea | missing_expected_core_file |
| climate_geography | F1 | SEC_A_T_Swahili_Labels | SECTION A-1: Household Identification SECTION T-1: Household Recontact Information SECTION T-2: Filter Questions for Ag Module This file contains data with Swahili labels | ea | missing_expected_core_file |
| climate_geography | F29 | SECTA1A2_Swahili_Labels | Community Questionnaire Section CA: Identification This file contains data with Swahili labels | ea_id | missing_expected_core_file |
| climate_geography | F32 | SECTCB_Swahili_Labels | Community Questionnaire Section CB: Access to Basic Services This file contains data with Swahili labels | ea_id | missing_expected_core_file |
| climate_geography | F35 | SECTCEFG | Community Questionnaire Section CE: Agriculture Section CF: Demography and Family Issues Section CG: Governance | ea_id | missing_expected_core_file |
| climate_geography | F36 | SECTCH | Community Questionnaire Section CH: Roster of Community Leaders | ea_id | missing_expected_core_file |
| climate_geography | F37 | SECTCI | Community Questionnaire Section CI: Crime and Policing | ea_id | missing_expected_core_file |
| consumption_or_income | F69 | TZY1.HH.Consumption | Aggregated consumption expenditure data. | hhexpenses;hhexpensesR;expm;expmR | missing_expected_core_file |
| consumption_or_income | F10 | SEC_L_Swahili_Labels | SECTION L: Non-Food Expenditures - Past One Week and One Month This file contains data with Swahili labels | hhid;slcode;slq1;slq2 | missing_expected_core_file |
| consumption_or_income | F11 | SEC_M_Swahili_Labels | SECTION M: Non-Food Expenditures - Past Twelve Months This file contains data with Swahili labels | hhid;smcode;smq1;smq2 | missing_expected_core_file |
| health_need_and_access | F40 | SEC_B_C_D_E1_F_G1_U_English_Labels | SECTION B: Household Member Roster SECTION C: Education SECTION D: Health SECTION E: Labour SECTION F: Food Consumption Outside the HH SECTION G: Children Living Elsewhere SECTION U: Anthropometry This file contains data with English labels | sdq22;sdq4;sdq43_1;sdq43_2;sdq43_3;sdq55_1;sdq55_2;sdq55_3;sdq6;sdq8;sdq9 | missing_expected_core_file |
| health_need_and_access | F47 | SEC_I_English_Labels | SECTION J: Housing, Water and Sanitation This file contains data with English labels | siq8b | missing_expected_core_file |
| household_person_keys | F20 | Agriculture SEC_1_ALL_Swahili_Labels | AGRICULTURE QUESTIONNAIRE - 1. Household Roster This file contains data with Swahili labels | hhid;rosterid | missing_expected_core_file |
| household_person_keys | F2 | SEC_B_C_D_E1_F_G1_U_Swahili_Labels | SECTION B: Household Member Roster SECTION C: Education SECTION D: Health SECTION E: Labour SECTION F: Food Consumption Outside the HH SECTION G: Children Living Elsewhere SECTION U: Anthropometry This file contains data with Swahili labels | hhid | missing_expected_core_file |
| household_person_keys | F21 | SEC_2A_Swahili_Labels | Agriculture Questionnaire - Plot Roster Plots anyone in your household owned or cultivated during the 2008 long rainy season. This file contains data with Swahili labels | hhid | missing_expected_core_file |
| household_person_keys | F22 | SEC_2B_Swahili_Labels | Agriculture Questionnaire - Plot Roster Additional plots owned or cultivated by anyone in the household during the short rainy season This file contains data with Swahili labels | hhid | missing_expected_core_file |
| household_person_keys | F40 | SEC_B_C_D_E1_F_G1_U_English_Labels | SECTION B: Household Member Roster SECTION C: Education SECTION D: Health SECTION E: Labour SECTION F: Food Consumption Outside the HH SECTION G: Children Living Elsewhere SECTION U: Anthropometry This file contains data with English labels | hhid | missing_expected_core_file |
| household_person_keys | F59 | SEC_2A_English_Labels | Agriculture Questionnaire - Plot Roster Plots anyone in your household owned or cultivated during the 2008 long rainy season. This file contains data with English labels | hhid | missing_expected_core_file |
| household_person_keys | F60 | SEC_2B_English_Labels | Agriculture Questionnaire - Plot Roster Additional plots owned or cultivated by anyone in the household during the short rainy season This file contains data with English labels | hhid | missing_expected_core_file |
| household_person_keys | F1 | SEC_A_T_Swahili_Labels | SECTION A-1: Household Identification SECTION T-1: Household Recontact Information SECTION T-2: Filter Questions for Ag Module This file contains data with Swahili labels | hhid | missing_expected_core_file |
| oop_health_expenditure | F40 | SEC_B_C_D_E1_F_G1_U_English_Labels | SECTION B: Household Member Roster SECTION C: Education SECTION D: Health SECTION E: Labour SECTION F: Food Consumption Outside the HH SECTION G: Children Living Elsewhere SECTION U: Anthropometry This file contains data with English labels | scq14_fee;scq14_food;sdq6;sdq7;scq14_bks;scq14_contr;scq14_tot;scq14_trans;scq14_tui;scq14_unif;sdq5 | missing_expected_core_file |
| oop_health_expenditure | F2 | SEC_B_C_D_E1_F_G1_U_Swahili_Labels | SECTION B: Household Member Roster SECTION C: Education SECTION D: Health SECTION E: Labour SECTION F: Food Consumption Outside the HH SECTION G: Children Living Elsewhere SECTION U: Anthropometry This file contains data with Swahili labels | scq14_fee | missing_expected_core_file |
| survey_timing | F1 | SEC_A_T_Swahili_Labels | SECTION A-1: Household Identification SECTION T-1: Household Recontact Information SECTION T-2: Filter Questions for Ag Module This file contains data with Swahili labels | endmin;sa2q17endhr;sa2q17starthr;sa2q17startmins | missing_expected_core_file |
| survey_timing | F39 | SEC_A_T_English_Labels | SECTION A-1: Household Identification SECTION T-1: Household Recontact Information SECTION T-2: Filter Questions for Ag Module This file contains data with English labels | endmin;sa2q17endhr;sa2q17starthr | missing_expected_core_file |
| survey_timing | F65 | SECTA1A2_English_Labels | Community Questionnaire Section CA: Identification This file contains data with English labels | ca07m;ca07y | missing_expected_core_file |
| survey_timing | F18 | SEC_R_Swahili_Labels | SECTION R: Recent Shocks to Household Welfare This file contains data with Swahili labels | srq5month;srq5year | missing_expected_core_file |
| survey_timing | F69 | TZY1.HH.Consumption | Aggregated consumption expenditure data. | intmonth | missing_expected_core_file |
| weights_and_design | F39 | SEC_A_T_English_Labels | SECTION A-1: Household Identification SECTION T-1: Household Recontact Information SECTION T-2: Filter Questions for Ag Module This file contains data with English labels | hh_weight;hh_weight_trimmed;ea;strataid | missing_expected_core_file |
| weights_and_design | F26 | nps_weights_oct2010 |  | hh_weight;hh_weight_trimmed;strataid | missing_expected_core_file |
| weights_and_design | F69 | TZY1.HH.Consumption | Aggregated consumption expenditure data. | hhweight | missing_expected_core_file |
| weights_and_design | F1 | SEC_A_T_Swahili_Labels | SECTION A-1: Household Identification SECTION T-1: Household Recontact Information SECTION T-2: Filter Questions for Ag Module This file contains data with Swahili labels | ea | missing_expected_core_file |
| weights_and_design | F29 | SECTA1A2_Swahili_Labels | Community Questionnaire Section CA: Identification This file contains data with Swahili labels | ea | missing_expected_core_file |
| weights_and_design | F32 | SECTCB_Swahili_Labels | Community Questionnaire Section CB: Access to Basic Services This file contains data with Swahili labels | ea | missing_expected_core_file |
| weights_and_design | F35 | SECTCEFG | Community Questionnaire Section CE: Agriculture Section CF: Demography and Family Issues Section CG: Governance | ea | missing_expected_core_file |

## Post-Download Validation

Run after the complete official package and documentation are placed locally:

```bash
python script/150_build_priority_lsms_isa_raw_package_receipt_checklist.py; python script/153_validate_priority_lsms_isa_official_file_receipt.py; python script/157_build_priority_lsms_isa_received_raw_schema_audit.py; python script/158_build_priority_lsms_isa_received_raw_value_profile.py; python script/159_build_priority_lsms_isa_received_raw_semantics_review.py
```

## Stop Rule

Do not write this country-wave into data/ until complete official file receipt, raw value verification, outcome construction, survey timing/geography, and accepted CHIRPS or ERA5 climate linkage all pass.
