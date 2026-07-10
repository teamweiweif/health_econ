# Manual Download Packet: TZA_2010_NPS-R2_v03_M

Status: credentialed/manual official raw package acquisition packet.
This packet does not download raw data, accept terms, extract microdata,
write `data/`, or run models.

## Target

- Country: Tanzania
- Wave: 2010-2011
- IDNO: TZA_2010_NPS-R2_v03_M
- Official get-microdata URL: https://microdata.worldbank.org/catalog/1050/get-microdata
- Local target folder: `temp/raw_downloads/TZA_2010_NPS-R2_v03_M/`
- Expected official files: 95
- Missing expected files: 95
- Requirement-linked core file rows: 38
- Missing core file rows: 38

## Manual Action

Login/register at the official World Bank Microdata get-microdata page, accept terms if required, download the complete unchanged official raw package and documentation, and place every file under the local target folder.

## Core Files To Confirm After Download

| requirement | file_id | expected_file_name | file_description | top_variable_names | official_core_file_match_status |
| --- | --- | --- | --- | --- | --- |
| climate_geography | F157 | HH_SEC_A | This file contains data related to section A of the Household questionnaire - household identifier variables, weights, cluster identification strata identification, 2008/09 household id, enumerator, supervisor, data entry clerk identifiers and data and time of interview. | clusterid;district;ea;hh_a18_year;region;ward | missing_expected_core_file |
| climate_geography | F130 | TZY2.EA.Offsets | This file contains the GPS coordinates for the Enumeration Area Center. | clusterid;rum | missing_expected_core_file |
| climate_geography | F120 | Plot.Geovariables_Y2 |  | ea_id | missing_expected_core_file |
| climate_geography | F187 | TZY1.HH.Consumption | Household consumption aggregate from year 1 (2008-2009). | urban | missing_expected_core_file |
| climate_geography | F188 | TZY2.HH.Consumption | Household consumption aggregate from year 2. | urban | missing_expected_core_file |
| climate_geography | F189 | HH.Geovariables_Y2 |  | ea_id | missing_expected_core_file |
| consumption_or_income | F187 | TZY1.HH.Consumption | Household consumption aggregate from year 1 (2008-2009). | hhexpenses;hhexpensesR;expm;expmR | missing_expected_core_file |
| consumption_or_income | F188 | TZY2.HH.Consumption | Household consumption aggregate from year 2. | hhexpenses;hhexpensesR;expm;expmR | missing_expected_core_file |
| consumption_or_income | F176 | HH_SEC_L | This file contains data related to section L of the Household questionnaire - non-food expenditure during the last week or last month. | hh_l01_2;hh_l02;itemcode;y2_hhid | missing_expected_core_file |
| health_need_and_access | F160 | HH_SEC_D | This file contains data related to section D of the Household questionnaire - general health status and utilization of health services. | hh_d12_1;hh_d12_2;hh_d02;hh_d13;hh_d38 | missing_expected_core_file |
| health_need_and_access | F143 | FS_H2 | This file contains data related to module H from the Fishery questionnaire - fish trading costs during the high season. | costid;costitem | missing_expected_core_file |
| health_need_and_access | F187 | TZY1.HH.Consumption | Household consumption aggregate from year 1 (2008-2009). | health;healthR | missing_expected_core_file |
| health_need_and_access | F155 | FS_N2 | This file contains data related to module N from the Fishery questionnaire - fish trading costs during the low season. | costid | missing_expected_core_file |
| health_need_and_access | F165 | HH_SEC_G | This file contains data related to section G of the Household questionnaire - subjective welfare assessment of standard of living. | hh_g03_5 | missing_expected_core_file |
| health_need_and_access | F188 | TZY2.HH.Consumption | Household consumption aggregate from year 2. | health | missing_expected_core_file |
| household_person_keys | F158 | HH_SEC_B | This file contains data related to section B of the Household questionnaire - roster of individuals living in the household, relationship to the household, gender, year of birth, variable to link individuals between survey rounds, marital status, spouse identificaiton, parental status, and place of birth. | hhid_2008;y2_hhid | missing_expected_core_file |
| household_person_keys | F115 | AG_SEC10B | This file contains data related to section 10B of the Agriculture questionnaire - quantity and value of livestock byproducts produced by the household during the last 12 months. | y2_hhid | missing_expected_core_file |
| household_person_keys | F108 | AG_SEC7A | This file contains data related to section 7A of the Agriculture questionnaire - quantity and value of crop sole, post-procudeion losses and storage for fruit crops. | y2_hhid | missing_expected_core_file |
| household_person_keys | F109 | AG_SEC7B | This file contains data related to section 7B of the Agriculture questionnaire - quantity and value of crop sole, post-procudeion losses and storage for permanent crops. | y2_hhid | missing_expected_core_file |
| household_person_keys | F188 | TZY2.HH.Consumption | Household consumption aggregate from year 2. | hhid_2008 | missing_expected_core_file |
| household_person_keys | F146 | FS_J1 | This file contains data related to module J of the Fishery questionnaire - questions 1 through 5 on shared labor/expenses during the low season. | hhid_2008 | missing_expected_core_file |
| household_person_keys | F148 | FS_J3 | This file contains data related to module J of the Fishery questionnaire - questions 7 through 13 on hired labor during the low season. | hhid_2008 | missing_expected_core_file |
| household_person_keys | F132 | FS_C1 | This file contains data related to module C of the Fishery questionnaire - listing of every member of the household who was engaged in fishing activities during the high season. | y2_hhid | missing_expected_core_file |
| oop_health_expenditure | F160 | HH_SEC_D | This file contains data related to section D of the Household questionnaire - general health status and utilization of health services. | hh_d05_1;hh_d05_2;hh_d07;hh_d08;hh_d09;hh_d13;hh_d15;hh_d29_1 | missing_expected_core_file |
| survey_timing | F159 | HH_SEC_C | This file contains data from section C of the Household questionnaire - educational attainment, school characteristics, and expenditures. | hh_c08;hh_c10;hh_c30 | missing_expected_core_file |
| survey_timing | F161 | HH_SEC_E1 | This file contains data related to section E of the Household questionnaire - labor market participation during the last seven days, wage work, non-farm enterprise activity, and domestic activities within the home. | hh_e44;hh_e67;hh_e68 | missing_expected_core_file |
| survey_timing | F157 | HH_SEC_A | This file contains data related to section A of the Household questionnaire - household identifier variables, weights, cluster identification strata identification, 2008/09 household id, enumerator, supervisor, data entry clerk identifiers and data and time of interview. | hh_a18_month;hh_a18_year | missing_expected_core_file |
| survey_timing | F160 | HH_SEC_D | This file contains data related to section D of the Household questionnaire - general health status and utilization of health services. | hh_d05_1;hh_d05_2 | missing_expected_core_file |
| survey_timing | F187 | TZY1.HH.Consumption | Household consumption aggregate from year 1 (2008-2009). | intmonth | missing_expected_core_file |
| survey_timing | F188 | TZY2.HH.Consumption | Household consumption aggregate from year 2. | intmonth | missing_expected_core_file |
| weights_and_design | F157 | HH_SEC_A | This file contains data related to section A of the Household questionnaire - household identifier variables, weights, cluster identification strata identification, 2008/09 household id, enumerator, supervisor, data entry clerk identifiers and data and time of interview. | strataid;y2_weight | missing_expected_core_file |
| weights_and_design | F187 | TZY1.HH.Consumption | Household consumption aggregate from year 1 (2008-2009). | hhweight | missing_expected_core_file |
| weights_and_design | F188 | TZY2.HH.Consumption | Household consumption aggregate from year 2. | hhweight | missing_expected_core_file |
| weights_and_design | F120 | Plot.Geovariables_Y2 |  | ea_id | missing_expected_core_file |
| weights_and_design | F189 | HH.Geovariables_Y2 |  | ea_id | missing_expected_core_file |
| weights_and_design | F121 | COMSEC_CA | This file contains data related to section A of the Community questionnaire - presence of community information sharing items. | id_04 | missing_expected_core_file |
| weights_and_design | F122 | COMSEC_CB | This file contains data related to section B of the Community questionnaire - availability of basic services, the name of the nearest provider and the distance to the location. | id_04 | missing_expected_core_file |
| weights_and_design | F123 | COMSEC_CD | This file contains data related to section D of the Community questionnaire - land use practices in the village and any notable changes in land ownership/appropriation. | id_04 | missing_expected_core_file |

## Post-Download Validation

Run after the complete official package and documentation are placed locally:

```bash
python script/150_build_priority_lsms_isa_raw_package_receipt_checklist.py; python script/153_validate_priority_lsms_isa_official_file_receipt.py; python script/157_build_priority_lsms_isa_received_raw_schema_audit.py; python script/158_build_priority_lsms_isa_received_raw_value_profile.py; python script/159_build_priority_lsms_isa_received_raw_semantics_review.py
```

## Stop Rule

Do not write this country-wave into data/ until complete official file receipt, raw value verification, outcome construction, survey timing/geography, and accepted CHIRPS or ERA5 climate linkage all pass.
