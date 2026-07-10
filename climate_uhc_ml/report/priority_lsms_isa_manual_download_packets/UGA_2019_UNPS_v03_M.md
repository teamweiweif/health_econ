# Manual Download Packet: UGA_2019_UNPS_v03_M

Status: credentialed/manual official raw package acquisition packet.
This packet does not download raw data, accept terms, extract microdata,
write `data/`, or run models.

## Target

- Country: Uganda
- Wave: 2019-2020
- IDNO: UGA_2019_UNPS_v03_M
- Official get-microdata URL: https://microdata.worldbank.org/catalog/3902/get-microdata
- Local target folder: `temp/raw_downloads/UGA_2019_UNPS_v03_M/`
- Expected official files: 109
- Missing expected files: 109
- Requirement-linked core file rows: 39
- Missing core file rows: 39

## Manual Action

Login/register at the official World Bank Microdata get-microdata page, accept terms if required, download the complete unchanged official raw package and documentation, and place every file under the local target folder.

## Core Files To Confirm After Download

| requirement | file_id | expected_file_name | file_description | top_variable_names | official_core_file_match_status |
| --- | --- | --- | --- | --- | --- |
| climate_geography | F114 | pov2019_20.NSDstat | Consumption aggregate dataset | regurb;urban;district | missing_expected_core_file |
| climate_geography | F76 | GSEC1.NSDstat | Household Identification Particulars Level of observation:Household | urban | missing_expected_core_file |
| climate_geography | F23 | CSEC1A.NSDstat | Identification Particulars | Final_EA_code | missing_expected_core_file |
| climate_geography | F24 | CSEC2.NSDstat | Service Availability in LC1 Service type | Final_EA_code | missing_expected_core_file |
| climate_geography | F25 | CSEC2A.NSDstat | Land use and planning | Final_EA_code | missing_expected_core_file |
| climate_geography | F26 | CSEC2B.NSDstat | Client satisfaction with health facilities EA | Final_EA_code | missing_expected_core_file |
| climate_geography | F27 | CSEC2C.NSDstat | Water and Sanitation - toilets EA | Final_EA_code | missing_expected_core_file |
| climate_geography | F28 | CSEC2C_0.NSDstat | Water and Sanitation EA | Final_EA_code | missing_expected_core_file |
| consumption_or_income | F98 | GSEC15B.NSDstat | Household Consumption Expenditures – Food, Beverages and Tobacco (Last 7 days) Level of observation:Consumption Item | CEB03;CEB04;CEB07;CEB10;CEB11;CEB14a;CEB15;CEB16;coicop_2 | missing_expected_core_file |
| consumption_or_income | F114 | pov2019_20.NSDstat | Consumption aggregate dataset | cpexp30;nrrexp30;hpline | missing_expected_core_file |
| health_need_and_access | F26 | CSEC2B.NSDstat | Client satisfaction with health facilities EA | s2bq13__1;s2bq09;s2bq10;s2bq13__2;s2bq13__3;s2bq13__4 | missing_expected_core_file |
| health_need_and_access | F47 | CSEC4B.NSDstat | Health Facility - Availability of equipment/ services Level of observation: EA | s4bq23;s4bq26;s4bq27;s4bq28 | missing_expected_core_file |
| health_need_and_access | F57 | CSEC4L.NSDstat | Access to Water at the Health facility Level of observation: Water facility type | Health_Water_id | missing_expected_core_file |
| health_need_and_access | F82 | GSEC6_1.NSDstat | Child Nutrition and Health Level of observation:Individual | s6q15b | missing_expected_core_file |
| household_person_keys | F77 | GSEC2.NSDstat | Household Roster Level of observation:Individual | hhid | missing_expected_core_file |
| household_person_keys | F100 | GSEC15C.NSDstat | Household Consumption Expenditures – Non-Durable Goods and Frequently Purchased Services (Last 30 days) Level of observation:Consumption Item | hhid | missing_expected_core_file |
| household_person_keys | F101 | GSEC15D.NSDstat | Household Consumption Expenditures – Semi-durable and Durable Goods and Services (Last 365 days) & Non-Consumption Expenditures (Last 365 Days) Level of observation:Consumption Item | hhid | missing_expected_core_file |
| household_person_keys | F104 | GSEC17_1.NSDstat | Welfare and Food Security Level of observation:Household | hhid | missing_expected_core_file |
| household_person_keys | F105 | GSEC19.NSDstat | Link with the Agriculture Questionnaire Level of observation:Household | hhid | missing_expected_core_file |
| household_person_keys | F76 | GSEC1.NSDstat | Household Identification Particulars Level of observation:Household | hhid | missing_expected_core_file |
| household_person_keys | F87 | GSEC7_1.NSDstat | Savings Level of observation:Household | hhid | missing_expected_core_file |
| household_person_keys | F88 | GSEC7_2.NSDstat | Sources of income, financial decisions Level of observation:Household | hhid | missing_expected_core_file |
| oop_health_expenditure | F81 | GSEC5.NSDstat | Health Level of observation:Individual | h5q12a;h5q12b;h5q12f;h5q12f_1;h5q12g;h5q12c;h5q12d;h5q12e | missing_expected_core_file |
| oop_health_expenditure | F82 | GSEC6_1.NSDstat | Child Nutrition and Health Level of observation:Individual | h6q12h;s6q07_1;s6q07_3i | missing_expected_core_file |
| oop_health_expenditure | F84 | GSEC6_3.NSDstat | Child nutrition and health – feeding counselling Level of observation:Individual | t31 | missing_expected_core_file |
| survey_timing | F95 | GSEC12_2.NSDstat | Non-Agricultural Household Enterprises/Activities Level of observation:Enterprise | h12q04;h12q12;h12q13 | missing_expected_core_file |
| survey_timing | F76 | GSEC1.NSDstat | Household Identification Particulars Level of observation:Household | month;year | missing_expected_core_file |
| survey_timing | F10 | AGSEC5A.NSDstat | Quantification of Production – 1st Visit Parcel-Plot-Crop level | s5aq06f_1;s5aq06f_11;s5aq06f_1_1 | missing_expected_core_file |
| survey_timing | F77 | GSEC2.NSDstat | Household Roster Level of observation:Individual | h2q9b;h2q9c | missing_expected_core_file |
| survey_timing | F91 | GSEC9.NSDstat | Housing Conditions, Water and Sanitation Level of observation:Household | dwellingVisit | missing_expected_core_file |
| survey_timing | F19 | AGSEC9A.NSDstat | Extension Services Extension Source | h9q07a | missing_expected_core_file |
| weights_and_design | F23 | CSEC1A.NSDstat | Identification Particulars | Final_EA_code | missing_expected_core_file |
| weights_and_design | F24 | CSEC2.NSDstat | Service Availability in LC1 Service type | Final_EA_code | missing_expected_core_file |
| weights_and_design | F25 | CSEC2A.NSDstat | Land use and planning | Final_EA_code | missing_expected_core_file |
| weights_and_design | F26 | CSEC2B.NSDstat | Client satisfaction with health facilities EA | Final_EA_code | missing_expected_core_file |
| weights_and_design | F27 | CSEC2C.NSDstat | Water and Sanitation - toilets EA | Final_EA_code | missing_expected_core_file |
| weights_and_design | F28 | CSEC2C_0.NSDstat | Water and Sanitation EA | Final_EA_code | missing_expected_core_file |
| weights_and_design | F29 | CSEC3_0.NSDstat | Education (primary education) EA | Final_EA_code | missing_expected_core_file |
| weights_and_design | F30 | CSEC3A.NSDstat | Availability of Facilities at School Facility type | Final_EA_code | missing_expected_core_file |

## Post-Download Validation

Run after the complete official package and documentation are placed locally:

```bash
python script/150_build_priority_lsms_isa_raw_package_receipt_checklist.py; python script/153_validate_priority_lsms_isa_official_file_receipt.py; python script/157_build_priority_lsms_isa_received_raw_schema_audit.py; python script/158_build_priority_lsms_isa_received_raw_value_profile.py; python script/159_build_priority_lsms_isa_received_raw_semantics_review.py
```

## Stop Rule

Do not write this country-wave into data/ until complete official file receipt, raw value verification, outcome construction, survey timing/geography, and accepted CHIRPS or ERA5 climate linkage all pass.
