# Manual Download Packet: NPL_2010_LSS-III_v01_M

Status: credentialed/manual official raw package acquisition packet.
This packet does not download raw data, accept terms, extract microdata,
write `data/`, or run models.

## Target

- Country: Nepal
- Wave: 2010-2011
- IDNO: NPL_2010_LSS-III_v01_M
- Official get-microdata URL: https://microdata.worldbank.org/catalog/1000/get-microdata
- Local target folder: `temp/raw_downloads/NPL_2010_LSS-III_v01_M/`
- Expected official files: 51
- Missing expected files: 51
- Requirement-linked core file rows: 28
- Missing core file rows: 28

## Manual Action

Login/register at the official World Bank Microdata get-microdata page, accept terms if required, download the complete unchanged official raw package and documentation, and place every file under the local target folder.

## Core Files To Confirm After Download

| requirement | file_id | expected_file_name | file_description | top_variable_names | official_core_file_match_status |
| --- | --- | --- | --- | --- | --- |
| climate_geography | F52 | S00 | This file contains household-level information such as date of interview, data entry and edit, religion of the household head, language spoken at the household, whether the household own any agricultural land, own any livestock, whether the household borrowed any loan in the last 12 months or has any outstanding loans, any member absent from the household, etc. | v00_zone;v00_headn;v00_team;v00_ward | missing_expected_core_file |
| climate_geography | F2 | FINAL_PREF |  | district;district_name;Eastern;HEAD___ | missing_expected_core_file |
| climate_geography | F7 | S04 | This file contains household-level information from Section 3 - Migration of the questionnaire. It contains the following information: First time in migration to the place of enumeration, out migration over the past five years. | v04_03b;v04_11b | missing_expected_core_file |
| climate_geography | F4 | S01 | This file contains household-member information from Section 1 - Household Roster of the questionnaire. It contains the following information: Demographic characteristics (including name, sex, age, relationship to the household head, birth place, marital status for persons aged 10 years or over, and caste/ethnicity), and identification of household members, and parents of household members (whe... | v01_05b | missing_expected_core_file |
| climate_geography | F48 | S21 | The file contains data for Section 21. Panel Sample Household Tracking Q (21.01 - 21.05) of the NLSS III (2010/11) questionnaire. | v21_ward | missing_expected_core_file |
| consumption_or_income | F2 | FINAL_PREF |  | sh_nonfood_30;sh_nonfood_7;nonfood_30;nonfood_7;nonfood_pc_30;nonfood_pc_7;nonfood_pc_7_tadj;nfood | missing_expected_core_file |
| consumption_or_income | F10 | S06B | This file contains household-level information from Section 6 - Non-food Expenditures and Inventory of Durable Goods, Section B - Infrequent Non-Food Expenditures of the questionnaire. | v06b_idc;v06b_itm | missing_expected_core_file |
| consumption_or_income | F9 | S06A | This file contains household-level information from Section 6 - Non-food Expenditures and Inventory of Durable Goods, Section A - Frequent non-food expenditures of the questionnaire. | v06a_idc;v06a_itm | missing_expected_core_file |
| health_need_and_access | F14 | S08 | The file contains data for Section 8. Health of the NLSS III (2010/11) questionnaire. | v08_12;v08_17b;v08_14;v08_16;v08_17a;v08_17c | missing_expected_core_file |
| health_need_and_access | F46 | S19 | The file contains data for Section 19. Adequacy of Consumption and Government Facilities of the NLSS III (2010/11) questionnaire. | v19_09;v19_05 | missing_expected_core_file |
| health_need_and_access | F16 | S09B | The file contains data for Part B. Pre- and Post-Natal Care of Section 9. Marriage and Maternity History of the NLSS III (2010/11) questionnaire. | v09_18;v09_24 | missing_expected_core_file |
| health_need_and_access | F6 | S03 | This file contains household-level information from Section 3 - Access to Facilities of the questionnaire. It contains the following information: Distance to the various (24) public facilities and services, mode of transport and travel time required to reach the facility. | v03_03a;v03_03b | missing_expected_core_file |
| household_person_keys | F4 | S01 | This file contains household-member information from Section 1 - Household Roster of the questionnaire. It contains the following information: Demographic characteristics (including name, sex, age, relationship to the household head, birth place, marital status for persons aged 10 years or over, and caste/ethnicity), and identification of household members, and parents of household members (whe... | v01_10;REC_TYPE;v01_01;v01_02;v01_03;v01_04;v01_05a;v01_05b | missing_expected_core_file |
| household_person_keys | F49 | S21x | The file contains data for Section 21. Panel Sample Household Tracking Q (21.06 - 21.14) of the NLSS III (2010/11) questionnaire. | v21_10;v21_11 | missing_expected_core_file |
| household_person_keys | F20 | S10B | The file contains data for Part B. Jobs during the past 12 Months of Section 10. Jobs and Time Use of the NLSS III (2010/11) questionnaire. | v10_02 | missing_expected_core_file |
| household_person_keys | F22 | S12 | The file contains data for Section 12. Wage Jobs of the NLSS III (2010/11) questionnaire. | v12_01 | missing_expected_core_file |
| oop_health_expenditure | F14 | S08 | The file contains data for Section 8. Health of the NLSS III (2010/11) questionnaire. | v08_17a;v08_07a;v08_07b;v08_17b;v08_18;v08_17c | missing_expected_core_file |
| survey_timing | F52 | S00 | This file contains household-level information such as date of interview, data entry and edit, religion of the household head, language spoken at the household, whether the household own any agricultural land, own any livestock, whether the household borrowed any loan in the last 12 months or has any outstanding loans, any member absent from the household, etc. | v00_int1_m;v00_int1_y;v00_int2_m;v00_int2_y;v00_int3_m;v00_int3_y;v00_sup_m | missing_expected_core_file |
| survey_timing | F51 | sys |  | hsys_c1date;hsys_u1date;hsys_c2date;hsys_u2date | missing_expected_core_file |
| survey_timing | F2 | FINAL_PREF |  | Date | missing_expected_core_file |
| weights_and_design | F1 | anthro |  | weight | missing_expected_core_file |
| weights_and_design | F10 | S06B | This file contains household-level information from Section 6 - Non-food Expenditures and Inventory of Durable Goods, Section B - Infrequent Non-Food Expenditures of the questionnaire. | xhpsu | missing_expected_core_file |
| weights_and_design | F11 | S06C | This file contains household-level information from Section 6 - Non-food Expenditures and Inventory of Durable Goods, Section C - Inventory of Durable Goods of the questionnaire. | xhpsu | missing_expected_core_file |
| weights_and_design | F12 | S06D | This file contains household-level information from Section 6 - Non-food Expenditures and Inventory of Durable Goods, Section D - Own Account Production of Goods of the questionnaire. | xhpsu | missing_expected_core_file |
| weights_and_design | F18 | S09D | The file contains data for Part D. Household Decisions of Section 9. Marriage and Maternity History of the NLSS III (2010/11) questionnaire. | xhpsu | missing_expected_core_file |
| weights_and_design | F39 | S15D | The file contains data for Part D. Household Decisions of Section 15. Credit and Savings of the NLSS III (2010/11) questionnaire. | xhpsu | missing_expected_core_file |
| weights_and_design | F4 | S01 | This file contains household-member information from Section 1 - Household Roster of the questionnaire. It contains the following information: Demographic characteristics (including name, sex, age, relationship to the household head, birth place, marital status for persons aged 10 years or over, and caste/ethnicity), and identification of household members, and parents of household members (whe... | xhpsu | missing_expected_core_file |
| weights_and_design | F48 | S21 | The file contains data for Section 21. Panel Sample Household Tracking Q (21.01 - 21.05) of the NLSS III (2010/11) questionnaire. | xhpsu | missing_expected_core_file |

## Post-Download Validation

Run after the complete official package and documentation are placed locally:

```bash
python script/150_build_priority_lsms_isa_raw_package_receipt_checklist.py; python script/153_validate_priority_lsms_isa_official_file_receipt.py; python script/157_build_priority_lsms_isa_received_raw_schema_audit.py; python script/158_build_priority_lsms_isa_received_raw_value_profile.py; python script/159_build_priority_lsms_isa_received_raw_semantics_review.py
```

## Stop Rule

Do not write this country-wave into data/ until complete official file receipt, raw value verification, outcome construction, survey timing/geography, and accepted CHIRPS or ERA5 climate linkage all pass.
