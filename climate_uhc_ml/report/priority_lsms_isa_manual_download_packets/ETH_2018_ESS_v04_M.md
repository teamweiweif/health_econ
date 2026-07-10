# Manual Download Packet: ETH_2018_ESS_v04_M

Status: credentialed/manual official raw package acquisition packet.
This packet does not download raw data, accept terms, extract microdata,
write `data/`, or run models.

## Target

- Country: Ethiopia
- Wave: 2018-2019
- IDNO: ETH_2018_ESS_v04_M
- Official get-microdata URL: https://microdata.worldbank.org/catalog/3823/get-microdata
- Local target folder: `temp/raw_downloads/ETH_2018_ESS_v04_M/`
- Expected official files: 68
- Missing expected files: 68
- Requirement-linked core file rows: 35
- Missing core file rows: 35

## Manual Action

Login/register at the official World Bank Microdata get-microdata page, accept terms if required, download the complete unchanged official raw package and documentation, and place every file under the local target folder.

## Core Files To Confirm After Download

| requirement | file_id | expected_file_name | file_description | top_variable_names | official_core_file_match_status |
| --- | --- | --- | --- | --- | --- |
| climate_geography | F39 | sect_cover_ph_w4.dta | Holder location identification; household size, agriculture holding type: farming, livestock, or both, field staff identification. | saq19__Latitude;saq19__Longitude;ea_id | missing_expected_core_file |
| climate_geography | F44 | sect_cover_pp_w4.dta | Holder location identification; name of household head, name of holder, household size, type of agriculture holding type: farming, livestock, or both; field staff identification. | saq19__Latitude;saq19__Longitude | missing_expected_core_file |
| climate_geography | F34 | sect_cover_ls_w4.dta | Holder educational level and holding type | saq19__Latitude;saq19__Longitude | missing_expected_core_file |
| climate_geography | F47 | sect3_pp_w4.dta | Field Roster - Information on all fields (sub-parcels) owned and managed, including holder self-reported area, GPS and compass measured area, labor inputs, and other details about each field. | s3q09__Latitude;s3q09__Longitude | missing_expected_core_file |
| climate_geography | F73 | sect10a_com_w4.dta | Market Prices - Market prices in the first closest market center. | cs10q05__Latitude;cs10q05__Longitude | missing_expected_core_file |
| climate_geography | F1 | sect_cover_hh_w4.dta | Household identification; location; household size, and field staff identification | ea_id | missing_expected_core_file |
| consumption_or_income | F14 | sect7a_hh_w4.dta | Nonfood expenditure - Household monthly expenditures on nonfood items. | ea_id;household_id;item_cd_30day;pw_w4;s7q01;s7q02;saq01;saq02;saq03 | missing_expected_core_file |
| consumption_or_income | F63 | cons_agg_w4.dta |  | nom_nonfoodcons_aeq;nonfood_cons_ann;food_cons_ann | missing_expected_core_file |
| health_need_and_access | F4 | sect3_hh_w4.dta | Health - Health problems, types of injury/illness, medical assistance/consultation, health insurance, disabilities, vital registration (birth certificate), breast feeding, and anthropometrics (children and under). | s3q14;s3q15;s3q05;s3q17;s3q13;s3q18;s3q06_1;s3q06_2;s3q06_os;s3q09a;s3q09b | missing_expected_core_file |
| health_need_and_access | F56 | sect04_com_w4.dta | Access to Basic Services - Transportation, markets, proximity to the nearest town and major urban centers, electrification, bank and microfinance institutions, piped water | cs4q37 | missing_expected_core_file |
| household_person_keys | F2 | sect1_hh_w4.dta | Roster - List of individuals living in the household and basic demographics; for members younger than 18, parental education and occupation. | individual_id;household_id | missing_expected_core_file |
| household_person_keys | F25 | sect11b1_hh_w4.dta | Mobile phones - Individual disaggregated mobile phone ownership roster | individual_id;household_id | missing_expected_core_file |
| household_person_keys | F22 | sect10d1_hh_w4.dta | Livestock roster - Individual disaggregated livestock roster: Household ownership of different livestock by type and number. | household_id | missing_expected_core_file |
| household_person_keys | F40 | sect1_ph_w4.dta | Household Roster - Age, and gender of each household member and holding type: farming, livestock, or both. | household_id | missing_expected_core_file |
| household_person_keys | F45 | sect1_pp_w4.dta | Household Roster - Age, and gender of each household member, and holding type: farming, livestock, or both | household_id | missing_expected_core_file |
| household_person_keys | F20 | sect10b_hh_w4.dta | Land parcel roster - Individual disaggregated land roster | household_id | missing_expected_core_file |
| household_person_keys | F46 | sect2_pp_w4.dta | Parcel Roster - Information on all parcels owned or managed by the holder. | household_id | missing_expected_core_file |
| household_person_keys | F47 | sect3_pp_w4.dta | Field Roster - Information on all fields (sub-parcels) owned and managed, including holder self-reported area, GPS and compass measured area, labor inputs, and other details about each field. | household_id | missing_expected_core_file |
| oop_health_expenditure | F37 | sect8_3_ls_w4.dta | Livestock Breeding, Health, Shelter, Water, and Feed - Livestock breeding methods and costs; livestock shelter type and feed type and sources; livestock treatments and treatment expenses. | ls_s8_3q04;ls_s8_3q22;ls_s8_3q24;ls_s8_3q03;ls_s8_3q05;ls_s8_3q06;ls_s8_3q10a;ls_s8_3q10b;ls_s8_3q11;ls_s8_3q12_1 | missing_expected_core_file |
| oop_health_expenditure | F4 | sect3_hh_w4.dta | Health - Health problems, types of injury/illness, medical assistance/consultation, health insurance, disabilities, vital registration (birth certificate), breast feeding, and anthropometrics (children and under). | s3q17;s3q18 | missing_expected_core_file |
| survey_timing | F39 | sect_cover_ph_w4.dta | Holder location identification; household size, agriculture holding type: farming, livestock, or both, field staff identification. | InterviewDate;saq19__Timestamp | missing_expected_core_file |
| survey_timing | F44 | sect_cover_pp_w4.dta | Holder location identification; name of household head, name of holder, household size, type of agriculture holding type: farming, livestock, or both; field staff identification. | InterviewDate;saq19__Timestamp | missing_expected_core_file |
| survey_timing | F34 | sect_cover_ls_w4.dta | Holder educational level and holding type | InterviewDate;saq19__Timestamp | missing_expected_core_file |
| survey_timing | F28 | sect12b1_hh_w4.dta | Nonfarm enterprises - Characteristics of enterprises owned by the household: sector, employment, revenue, expenses and tax and fees related to the business. | s12bq08a;s12bq08b | missing_expected_core_file |
| survey_timing | F67 | ETH_HouseholdGeovariables_Y4.dta | Household geo-variables | wetQ_avgstart;h2018_wetQstart | missing_expected_core_file |
| survey_timing | F1 | sect_cover_hh_w4.dta | Household identification; location; household size, and field staff identification | InterviewStart | missing_expected_core_file |
| survey_timing | F33 | sect15b_hh_w4.dta | Credit (questions 2 to 10) - Loans or credit received by the household: source, repayment, collateral and challenges in accessing credit. | s15q06b | missing_expected_core_file |
| weights_and_design | F1 | sect_cover_hh_w4.dta | Household identification; location; household size, and field staff identification | ea_id | missing_expected_core_file |
| weights_and_design | F39 | sect_cover_ph_w4.dta | Holder location identification; household size, agriculture holding type: farming, livestock, or both, field staff identification. | ea_id | missing_expected_core_file |
| weights_and_design | F44 | sect_cover_pp_w4.dta | Holder location identification; name of household head, name of holder, household size, type of agriculture holding type: farming, livestock, or both; field staff identification. | ea_id | missing_expected_core_file |
| weights_and_design | F11 | sect6b2_hh_w4.dta | Meals shared with non-household members, last 7 days - Meal sharing with non-household members (number of persons and meals shared). | ea_id | missing_expected_core_file |
| weights_and_design | F14 | sect7a_hh_w4.dta | Nonfood expenditure - Household monthly expenditures on nonfood items. | ea_id | missing_expected_core_file |
| weights_and_design | F18 | sect9_hh_w4.dta | Shocks - Shocks during the last 12 months and their impact on income, assets, food production, shock and purchase. Strategies the household used to cope with the three worst shocks faced. | ea_id | missing_expected_core_file |
| weights_and_design | F2 | sect1_hh_w4.dta | Roster - List of individuals living in the household and basic demographics; for members younger than 18, parental education and occupation. | ea_id | missing_expected_core_file |
| weights_and_design | F22 | sect10d1_hh_w4.dta | Livestock roster - Individual disaggregated livestock roster: Household ownership of different livestock by type and number. | ea_id | missing_expected_core_file |

## Post-Download Validation

Run after the complete official package and documentation are placed locally:

```bash
python script/150_build_priority_lsms_isa_raw_package_receipt_checklist.py; python script/153_validate_priority_lsms_isa_official_file_receipt.py; python script/157_build_priority_lsms_isa_received_raw_schema_audit.py; python script/158_build_priority_lsms_isa_received_raw_value_profile.py; python script/159_build_priority_lsms_isa_received_raw_semantics_review.py
```

## Stop Rule

Do not write this country-wave into data/ until complete official file receipt, raw value verification, outcome construction, survey timing/geography, and accepted CHIRPS or ERA5 climate linkage all pass.
