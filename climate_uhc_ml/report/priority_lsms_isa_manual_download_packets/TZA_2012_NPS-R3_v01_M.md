# Manual Download Packet: TZA_2012_NPS-R3_v01_M

Status: credentialed/manual official raw package acquisition packet.
This packet does not download raw data, accept terms, extract microdata,
write `data/`, or run models.

## Target

- Country: Tanzania
- Wave: 2012-2013
- IDNO: TZA_2012_NPS-R3_v01_M
- Official get-microdata URL: https://microdata.worldbank.org/catalog/2252/get-microdata
- Local target folder: `temp/raw_downloads/TZA_2012_NPS-R3_v01_M/`
- Expected official files: 80
- Missing expected files: 80
- Requirement-linked core file rows: 33
- Missing core file rows: 33

## Manual Action

Login/register at the official World Bank Microdata get-microdata page, accept terms if required, download the complete unchanged official raw package and documentation, and place every file under the local target folder.

## Core Files To Confirm After Download

| requirement | file_id | expected_file_name | file_description | top_variable_names | official_core_file_match_status |
| --- | --- | --- | --- | --- | --- |
| climate_geography | F24 | COM_SEC_A1A2.NSDstat | Community identification information including region, district, ward, regional capital identifier, location of market price information, and enumeration area, as well as survey staff information such as interviewers ID code, supervisor, and direct observation questions. | cm_lon_g;cm_lon_m;cm_lon_s;y3_cluster | missing_expected_core_file |
| climate_geography | F3 | AG_SEC_2A.NSDstat | Roster of all plots owned or cultivated by the household, including measurement information as calculated by GPS and farmer’s estimate, GPS coordinates, weather conditions at measurement, and reason for missing GPS. | ag2a_06_3;ag2a_06_4 | missing_expected_core_file |
| climate_geography | F23 | AG_SEC_A.NSDstat | Household location variables, unique within panel round household identification variables, date and time of interview, analytic weights, cluster identification, sampling strata identification, enumerator identification, supervisor identification, and data entry clerk identification. | ag_a04_1;ag_a04_2 | missing_expected_core_file |
| climate_geography | F34 | HH_SEC_A.NSDstat | SECTION A: HOUSEHOLD IDENTIFICATION / SURVEY STAFF DETAILS Household location variables, unique within panel round household identification variables, date and time of interview, analytic weights, cluster identification, sampling strata identification, enumerator identification,supervisor identification, and data entry clerk identification. | hh_a04_1;hh_a04_2 | missing_expected_core_file |
| climate_geography | F76 | LF_SEC_A.NSDstat | SECTION A: HOUSEHOLD IDENTIFICATION / SURVEY STAFF DETAILS Household location variables, unique within panel round household identification variables, date and time of interview, analytic weights, cluster identification, sampling strata identification, enumerator identification, supervisor identification, and data entry clerk identification. | lf_a04_1;lf_a04_2 | missing_expected_core_file |
| consumption_or_income | F47 | HH_SEC_K.NSDstat | SECTION K: NON-FOOD EXPENDITURES – PAST ONE WEEK & ONE MONTH Total expenditure on non-food items during the last week or last month, including; public transportation, fuels, cellular phone credits, personal hygiene items, etc. | hh_k01;hh_k02;hh_k03;itemcode;occ;y3_hhid | missing_expected_core_file |
| consumption_or_income | F48 | HH_SEC_L.NSDstat | SECTION L: NON-FOOD EXPENDITURES – PAST TWELVE MONTHS Total expenditure on non-food items during the past 12 months, including; household items, community contributions, fees and fines, marriage costs, clothing, etc. | hh_l01;hh_l02;hh_l03;itemcode;occ;y3_hhid | missing_expected_core_file |
| health_need_and_access | F37 | HH_SEC_D.NSDstat | SECTION D: HEALTH General health status and utilization of health services; source and financing of health treatments /hospitalization, disaggregated health expenditures, bednet use, pregnancy, prenatal care and births, child health and ailments / diarrhea. | hh_d12_1;hh_d12_2;hh_d02;hh_d13;hh_d23 | missing_expected_core_file |
| health_need_and_access | F32 | ConsumptionNPS3.NSDstat |  | health;healthR | missing_expected_core_file |
| health_need_and_access | F75 | LF_SEC_13B.NSDstat | SECTION 13B: FISH TRADING Costs associated with the fish trading are collected in this section, including amount spent by household on hired labour, transport, packaging, ice, and taxes. | costcode;costname | missing_expected_core_file |
| health_need_and_access | F40 | HH_SEC_G.NSDstat | SECTION G: SUBJECTIVE WELFARE Self-reported level of satisfaction with health, financial status, housing, job, services, and safety. Also includes perceived status at present, and as of 1 and 10 years ago. | hh_g03_5 | missing_expected_core_file |
| health_need_and_access | F20 | AG_SEC_11.NSDstat | Detailed information on the number of farm implements and machinery used or owned by the household in the past 12 months along with associated value if sold, whether the item was used, reasons for no usage, whether any of these items were rented or borrowed for use in the last twelve months and associated rents paid. | ag11_05 | missing_expected_core_file |
| health_need_and_access | F25 | COM_SEC_CB.NSDstat | Information on access to basic services in terms of distance and associated transportation costs for these services. | cm_b02 | missing_expected_core_file |
| household_person_keys | F35 | HH_SEC_B.NSDstat | SECTION B: HOUSEHOLD MEMBER ROSTER Roster of household members, individual characteristics including: sex, age, relationship to the household head, panel member identification, presence in household, general occupation, parental status, place of birth, marital status, and spouse identification. | y2_hhid;y3_hhid | missing_expected_core_file |
| household_person_keys | F2 | AG_SEC_01.NSDstat | Key roster information only, including name, age, sex of household members as well as which member is the key respondent for the agricultural questionnaire. | y3_hhid | missing_expected_core_file |
| household_person_keys | F3 | AG_SEC_2A.NSDstat | Roster of all plots owned or cultivated by the household, including measurement information as calculated by GPS and farmer’s estimate, GPS coordinates, weather conditions at measurement, and reason for missing GPS. | y3_hhid | missing_expected_core_file |
| household_person_keys | F4 | AG_SEC_2B.NSDstat | Roster of all plots owned or cultivated by the household, including measurement information as calculated by GPS and farmer’s estimate, GPS coordinates, weather conditions at measurement, and reason for missing GPS. | y3_hhid | missing_expected_core_file |
| household_person_keys | F60 | LF_NETWORK.NSDstat | SECTION NETWORK Throughout the various sections of the agricultural questionnaire, there are questions that refer to persons outside the household that are involved in the agricultural process. Examples include landlords, suppliers of inputs, harvest purchasers, outgrower partners, etc.. The network roster file contains the location and category of each of these persons. | y3_hhid | missing_expected_core_file |
| household_person_keys | F61 | LF_SEC_01.NSDstat | SECTION 01: HOUSEHOLD ROSTER Key roster information only, including name, age, sex of household members as well as which member is the key respondent for the agricultural questionnaire. | y3_hhid | missing_expected_core_file |
| household_person_keys | F15 | AG_SEC_08.NSDstat | Information is asked about amount of inputs redeemed from vouchers, household members that received the vouchers and how the inputs redeemed from vouchers were used by the household. | y3_hhid | missing_expected_core_file |
| household_person_keys | F20 | AG_SEC_11.NSDstat | Detailed information on the number of farm implements and machinery used or owned by the household in the past 12 months along with associated value if sold, whether the item was used, reasons for no usage, whether any of these items were rented or borrowed for use in the last twelve months and associated rents paid. | y3_hhid | missing_expected_core_file |
| oop_health_expenditure | F37 | HH_SEC_D.NSDstat | SECTION D: HEALTH General health status and utilization of health services; source and financing of health treatments /hospitalization, disaggregated health expenditures, bednet use, pregnancy, prenatal care and births, child health and ailments / diarrhea. | hh_d05_1;hh_d05_2;hh_d07;hh_d08;hh_d09;hh_d13;hh_d15;hh_d20;hh_d01;hh_d02;hh_d03_1;hh_d03_2 | missing_expected_core_file |
| survey_timing | F34 | HH_SEC_A.NSDstat | SECTION A: HOUSEHOLD IDENTIFICATION / SURVEY STAFF DETAILS Household location variables, unique within panel round household identification variables, date and time of interview, analytic weights, cluster identification, sampling strata identification, enumerator identification,supervisor identification, and data entry clerk identification. | hh_a18;hh_a18_1;hh_a18_2;hh_a18_3 | missing_expected_core_file |
| survey_timing | F24 | COM_SEC_A1A2.NSDstat | Community identification information including region, district, ward, regional capital identifier, location of market price information, and enumeration area, as well as survey staff information such as interviewers ID code, supervisor, and direct observation questions. | cm_a07;cm_a07_1;cm_a07_2;cm_a07_3 | missing_expected_core_file |
| survey_timing | F23 | AG_SEC_A.NSDstat | Household location variables, unique within panel round household identification variables, date and time of interview, analytic weights, cluster identification, sampling strata identification, enumerator identification, supervisor identification, and data entry clerk identification. | ag_a13;ag_a12_1 | missing_expected_core_file |
| survey_timing | F76 | LF_SEC_A.NSDstat | SECTION A: HOUSEHOLD IDENTIFICATION / SURVEY STAFF DETAILS Household location variables, unique within panel round household identification variables, date and time of interview, analytic weights, cluster identification, sampling strata identification, enumerator identification, supervisor identification, and data entry clerk identification. | lf_a13 | missing_expected_core_file |
| survey_timing | F21 | AG_SEC_12A.NSDstat | Any extension services or advice that the household received for agricultural or livestock activities in the past 12 months through government extension, NGOs, Cooperative/Farmer’s Association, or Large Scale Farmers, including what activity advice was sought for, subjective rating for advice received, and price paid for receiving advice. | ag12a_07 | missing_expected_core_file |
| weights_and_design | F34 | HH_SEC_A.NSDstat | SECTION A: HOUSEHOLD IDENTIFICATION / SURVEY STAFF DETAILS Household location variables, unique within panel round household identification variables, date and time of interview, analytic weights, cluster identification, sampling strata identification, enumerator identification,supervisor identification, and data entry clerk identification. | y3_weight;strataid;hh_a04_1;hh_a04_2 | missing_expected_core_file |
| weights_and_design | F23 | AG_SEC_A.NSDstat | Household location variables, unique within panel round household identification variables, date and time of interview, analytic weights, cluster identification, sampling strata identification, enumerator identification, supervisor identification, and data entry clerk identification. | ag_a04_1;ag_a04_2 | missing_expected_core_file |
| weights_and_design | F76 | LF_SEC_A.NSDstat | SECTION A: HOUSEHOLD IDENTIFICATION / SURVEY STAFF DETAILS Household location variables, unique within panel round household identification variables, date and time of interview, analytic weights, cluster identification, sampling strata identification, enumerator identification, supervisor identification, and data entry clerk identification. | lf_a04_1;lf_a04_2 | missing_expected_core_file |
| weights_and_design | F31 | COM_SEC_CG.NSDstat | Records the local units used for certain items in the surveyed communities. Similar to Section CF, the information is collected both at the village level and the district capital area. The kilogram or liter equivalent for the local units is collected, in addition to the price of the item in that local unit. | cm_g_weight;cm_g_weight2 | missing_expected_core_file |
| weights_and_design | F80 | Y3_weights.NSDstat | Weights | y3_panelweight | missing_expected_core_file |
| weights_and_design | F27 | COM_SEC_CD.NSDstat | Land use related issues with estimated percentages of how different types of village land are used (cultivation, forest, pasture, wetland, residential, business), as well as reasons for re-allocation of land (if any), number of households affected, and associated compensation. | id_04 | missing_expected_core_file |

## Post-Download Validation

Run after the complete official package and documentation are placed locally:

```bash
python script/150_build_priority_lsms_isa_raw_package_receipt_checklist.py; python script/153_validate_priority_lsms_isa_official_file_receipt.py; python script/157_build_priority_lsms_isa_received_raw_schema_audit.py; python script/158_build_priority_lsms_isa_received_raw_value_profile.py; python script/159_build_priority_lsms_isa_received_raw_semantics_review.py
```

## Stop Rule

Do not write this country-wave into data/ until complete official file receipt, raw value verification, outcome construction, survey timing/geography, and accepted CHIRPS or ERA5 climate linkage all pass.
