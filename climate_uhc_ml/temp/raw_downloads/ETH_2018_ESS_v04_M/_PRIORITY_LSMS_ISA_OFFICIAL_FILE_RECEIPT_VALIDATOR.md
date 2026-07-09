# Priority LSMS-ISA Official File Receipt Validator

IDNO: `ETH_2018_ESS_v04_M`

Country-wave: Ethiopia 2018-2019

Target folder: `temp/raw_downloads/ETH_2018_ESS_v04_M/`

Status: `blocked_no_original_package`

## Counts

| Metric | Value |
|---|---:|
| Official expected file rows | 68 |
| Official expected matched rows | 0 |
| Official expected missing rows | 68 |
| Official core file rows | 35 |
| Official core matched rows | 0 |
| Official core missing rows | 35 |
| Local original file/archive-member rows | 0 |

## Missing Core Files

| requirement | file_rank | expected_file_name | top_variable_names | official_core_file_match_status |
|---|---|---|---|---|
| climate_geography | 1 | sect_cover_ph_w4.dta | saq19__Latitude;saq19__Longitude;ea_id | missing_expected_core_file |
| climate_geography | 2 | sect_cover_pp_w4.dta | saq19__Latitude;saq19__Longitude | missing_expected_core_file |
| climate_geography | 3 | sect_cover_ls_w4.dta | saq19__Latitude;saq19__Longitude | missing_expected_core_file |
| climate_geography | 4 | sect3_pp_w4.dta | s3q09__Latitude;s3q09__Longitude | missing_expected_core_file |
| climate_geography | 5 | sect10a_com_w4.dta | cs10q05__Latitude;cs10q05__Longitude | missing_expected_core_file |
| climate_geography | 6 | sect_cover_hh_w4.dta | ea_id | missing_expected_core_file |
| consumption_or_income | 1 | sect7a_hh_w4.dta | ea_id;household_id;item_cd_30day;pw_w4;s7q01;s7q02;saq01;saq02;saq03 | missing_expected_core_file |
| consumption_or_income | 2 | cons_agg_w4.dta | nom_nonfoodcons_aeq;nonfood_cons_ann;food_cons_ann | missing_expected_core_file |
| health_need_and_access | 1 | sect3_hh_w4.dta | s3q14;s3q15;s3q05;s3q17;s3q13;s3q18;s3q06_1;s3q06_2;s3q06_os;s3q09a;s3q09b | missing_expected_core_file |
| health_need_and_access | 2 | sect04_com_w4.dta | cs4q37 | missing_expected_core_file |
| household_person_keys | 1 | sect1_hh_w4.dta | individual_id;household_id | missing_expected_core_file |
| household_person_keys | 2 | sect11b1_hh_w4.dta | individual_id;household_id | missing_expected_core_file |
| household_person_keys | 3 | sect10d1_hh_w4.dta | household_id | missing_expected_core_file |
| household_person_keys | 4 | sect1_ph_w4.dta | household_id | missing_expected_core_file |
| household_person_keys | 5 | sect1_pp_w4.dta | household_id | missing_expected_core_file |
| household_person_keys | 6 | sect10b_hh_w4.dta | household_id | missing_expected_core_file |
| household_person_keys | 7 | sect2_pp_w4.dta | household_id | missing_expected_core_file |
| household_person_keys | 8 | sect3_pp_w4.dta | household_id | missing_expected_core_file |
| oop_health_expenditure | 1 | sect8_3_ls_w4.dta | ls_s8_3q04;ls_s8_3q22;ls_s8_3q24;ls_s8_3q03;ls_s8_3q05;ls_s8_3q06;ls_s8_3q10a;ls_s8_3q10b;ls_s8_3q11;ls_s8_3q12_1 | missing_expected_core_file |
| oop_health_expenditure | 2 | sect3_hh_w4.dta | s3q17;s3q18 | missing_expected_core_file |
| survey_timing | 1 | sect_cover_ph_w4.dta | InterviewDate;saq19__Timestamp | missing_expected_core_file |
| survey_timing | 2 | sect_cover_pp_w4.dta | InterviewDate;saq19__Timestamp | missing_expected_core_file |
| survey_timing | 3 | sect_cover_ls_w4.dta | InterviewDate;saq19__Timestamp | missing_expected_core_file |
| survey_timing | 4 | sect12b1_hh_w4.dta | s12bq08a;s12bq08b | missing_expected_core_file |
| survey_timing | 5 | ETH_HouseholdGeovariables_Y4.dta | wetQ_avgstart;h2018_wetQstart | missing_expected_core_file |
| survey_timing | 6 | sect_cover_hh_w4.dta | InterviewStart | missing_expected_core_file |
| survey_timing | 7 | sect15b_hh_w4.dta | s15q06b | missing_expected_core_file |
| weights_and_design | 1 | sect_cover_hh_w4.dta | ea_id | missing_expected_core_file |
| weights_and_design | 2 | sect_cover_ph_w4.dta | ea_id | missing_expected_core_file |
| weights_and_design | 3 | sect_cover_pp_w4.dta | ea_id | missing_expected_core_file |
| weights_and_design | 4 | sect6b2_hh_w4.dta | ea_id | missing_expected_core_file |
| weights_and_design | 5 | sect7a_hh_w4.dta | ea_id | missing_expected_core_file |
| weights_and_design | 6 | sect9_hh_w4.dta | ea_id | missing_expected_core_file |
| weights_and_design | 7 | sect1_hh_w4.dta | ea_id | missing_expected_core_file |
| weights_and_design | 8 | sect10d1_hh_w4.dta | ea_id | missing_expected_core_file |

## Missing Official Files

| file_id | expected_file_name | file_description | priority_core_target | official_file_match_status |
|---|---|---|---|---|
| F1 | sect_cover_hh_w4.dta | Household identification; location; household size, and field staff identification | 1 | missing_expected_official_file |
| F2 | sect1_hh_w4.dta | Roster - List of individuals living in the household and basic demographics; for members younger than 18, parental ed... | 1 | missing_expected_official_file |
| F3 | sect2_hh_w4.dta | Education - Educational attainment, enrollment, attendance, school characteristics, and expenditures for the 2018‒19 ... | 0 | missing_expected_official_file |
| F4 | sect3_hh_w4.dta | Health - Health problems, types of injury/illness, medical assistance/consultation, health insurance, disabilities, v... | 1 | missing_expected_official_file |
| F5 | sect4_hh_w4.dta | Labor and time use - Time use, labor market participation in the last 7 days and the last 12 months, unpaid apprentic... | 0 | missing_expected_official_file |
| F6 | sect5a_hh_w4.dta | Banking and financial inclusion - Saving, financial literacy, insurance, and financial practices. | 0 | missing_expected_official_file |
| F7 | sect5b1_hh_w4.dta | Financial assets - Individual disaggregated financial asset module: Ownership of financial asset accounts (exclusivel... | 0 | missing_expected_official_file |
| F8 | sect5b2_hh_w4.dta | Financial assets - Individual disaggregated financial asset module: Value of financial assets owned privately or join... | 0 | missing_expected_official_file |
| F9 | sect6a_hh_w4.dta | Food consumption, last 7 days - Household food consumption (quantity and value) in the last 7 days and source of food... | 0 | missing_expected_official_file |
| F10 | sect6b1_hh_w4.dta | Food aggregate, last 7 days - Summary on consumption of food in the last 7 days. Dietary diversification. | 0 | missing_expected_official_file |
| F11 | sect6b2_hh_w4.dta | Meals shared with non-household members, last 7 days - Meal sharing with non-household members (number of persons and... | 1 | missing_expected_official_file |
| F12 | sect6b3_hh_w4.dta | Food consumed away from home, last 7 days - Total number of days and total number of meals shared with people (groupe... | 0 | missing_expected_official_file |
| F13 | sect6b4_hh_w4.dta | Food consumed away from home, last 7 days - Type and value of meals consumed away from home om the last 7 days. | 0 | missing_expected_official_file |
| F14 | sect7a_hh_w4.dta | Nonfood expenditure - Household monthly expenditures on nonfood items. | 1 | missing_expected_official_file |
| F74 | sect7b_hh_w4.dta | Nonfood expenditure - Household 12 months expenditures on nonfood items. | 0 | missing_expected_official_file |
| F17 | sect8_hh_w4.dta | Food security - Food Insecurity Experience Scale (FIES) for the last 7 days and food shortage experience for the last... | 0 | missing_expected_official_file |
| F18 | sect9_hh_w4.dta | Shocks - Shocks during the last 12 months and their impact on income, assets, food production, shock and purchase. St... | 1 | missing_expected_official_file |
| F19 | sect10a_hh_w4.dta | Housing - Dwelling ownership and property tax, characteristics of the dwelling and utilities, including WASH indicato... | 0 | missing_expected_official_file |
| F20 | sect10b_hh_w4.dta | Land parcel roster - Individual disaggregated land roster | 1 | missing_expected_official_file |
| F21 | sect10c_hh_w4.dta | Land and dwelling assets - Individual disaggregated land ownership and right | 0 | missing_expected_official_file |
| F22 | sect10d1_hh_w4.dta | Livestock roster - Individual disaggregated livestock roster: Household ownership of different livestock by type and ... | 1 | missing_expected_official_file |
| F23 | sect10d2_hh_w4.dta | Livestock assets - Individual disaggregated livestock ownership and rights: Reported personal and economic ownership ... | 0 | missing_expected_official_file |
| F24 | sect11_hh_w4.dta | Assets - Ownership and number of listed assets | 0 | missing_expected_official_file |
| F25 | sect11b1_hh_w4.dta | Mobile phones - Individual disaggregated mobile phone ownership roster | 1 | missing_expected_official_file |
| F26 | sect11b2_hh_w4.dta | Mobile phones - Individual-level and Mobile Phone disaggregated Ownership Right and operation | 0 | missing_expected_official_file |
| F27 | sect12a_hh_w4.dta | Nonfarm enterprises - Ownership | 0 | missing_expected_official_file |
| F28 | sect12b1_hh_w4.dta | Nonfarm enterprises - Characteristics of enterprises owned by the household: sector, employment, revenue, expenses an... | 1 | missing_expected_official_file |
| F29 | sect12b2_hh_w4.dta | Nonfarm enterprises - Business operation and start-up challenges. | 0 | missing_expected_official_file |
| F65 | sect13_hh_w4_v2.dta | Other income sources - Other sources of household income in the last 12 months, and any taxes related to the income. | 0 | missing_expected_official_file |
| F31 | sect14_hh_w4.dta | Assistance - Assistance provided to the household by governmental and nongovernmental agencies. | 0 | missing_expected_official_file |
| F32 | sect15a_hh_w4.dta | Credit (questions 11 to 18) - Loans or credit received by the household: source, repayment, collateral and challenges... | 0 | missing_expected_official_file |
| F33 | sect15b_hh_w4.dta | Credit (questions 2 to 10) - Loans or credit received by the household: source, repayment, collateral and challenges ... | 1 | missing_expected_official_file |
| F34 | sect_cover_ls_w4.dta | Holder educational level and holding type | 1 | missing_expected_official_file |
| F35 | sect8_1_ls_w4.dta | Ownership - Characteristics of livestock owned and their purpose. | 0 | missing_expected_official_file |
| F36 | sect8_2_ls_w4.dta | Change in stock - Total number of livestock by type; stock changes over the year due to birth, purchase, gifts given ... | 0 | missing_expected_official_file |
| F37 | sect8_3_ls_w4.dta | Livestock Breeding, Health, Shelter, Water, and Feed - Livestock breeding methods and costs; livestock shelter type a... | 1 | missing_expected_official_file |
| F38 | sect8_4_ls_w4.dta | Milk and Egg Production, Animal Power, and Dung - Quantity of milk and egg production; production, disposition and in... | 0 | missing_expected_official_file |
| F39 | sect_cover_ph_w4.dta | Holder location identification; household size, agriculture holding type: farming, livestock, or both, field staff id... | 1 | missing_expected_official_file |
| F40 | sect1_ph_w4.dta | Household Roster - Age, and gender of each household member and holding type: farming, livestock, or both. | 1 | missing_expected_official_file |
| F41 | sect9_ph_w4.dta | Crop Harvest by Field - Harvest information for all crops: crop use, area harvested, amount harvested, and any damage... | 0 | missing_expected_official_file |
| F42 | sect10_ph_w4.dta | Harvest Labor - Hired and household member labor used in harvesting each crop on each field, excluding permanent tree... | 0 | missing_expected_official_file |
| F43 | sect11_ph_w4.dta | Crop Disposition/ Sales - Information on crop disposition or sale. | 0 | missing_expected_official_file |
| F44 | sect_cover_pp_w4.dta | Holder location identification; name of household head, name of holder, household size, type of agriculture holding t... | 1 | missing_expected_official_file |
| F45 | sect1_pp_w4.dta | Household Roster - Age, and gender of each household member, and holding type: farming, livestock, or both | 1 | missing_expected_official_file |
| F46 | sect2_pp_w4.dta | Parcel Roster - Information on all parcels owned or managed by the holder. | 1 | missing_expected_official_file |
| F47 | sect3_pp_w4.dta | Field Roster - Information on all fields (sub-parcels) owned and managed, including holder self-reported area, GPS an... | 1 | missing_expected_official_file |
| F48 | sect4_pp_w4.dta | Crop Roster - Crop planting and management information for each crop on each field. | 0 | missing_expected_official_file |
| F49 | sect5_pp_w4.dta | Seeds Roster - Seed related information for each crop planted on each field. | 0 | missing_expected_official_file |
| F50 | sect7_pp_w4.dta | Miscellaneous - Information on holder including use of chemical fertilizer use, and access and use of credit, extensi... | 0 | missing_expected_official_file |
| F51 | sect9a_pp_w4.dta | Crop Cut - Crop cut information for selected fields including fresh and dry weight (from a 4mX4m crop cut), excluding... | 0 | missing_expected_official_file |
| F52 | sect01a_com_w4.dta | Community identification | 0 | missing_expected_official_file |
| F53 | sect01b_com_w4.dta | Community characteristics | 0 | missing_expected_official_file |
| F54 | sect02_com_w4.dta | Roster of Informants - Respondent characteristics | 0 | missing_expected_official_file |
| F55 | sect03_com_w4.dta | Community Basic Information - Mobility, population, religion, marriage types, common land use | 0 | missing_expected_official_file |
| F56 | sect04_com_w4.dta | Access to Basic Services - Transportation, markets, proximity to the nearest town and major urban centers, electrific... | 1 | missing_expected_official_file |
| F57 | sect05_com_w4.dta | Economic Activities - Main sources of employment, migration to and from the locality for work, cooperatives and micro... | 0 | missing_expected_official_file |
| F58 | sect06_com_w4.dta | Agriculture - Agricultural activities, including major crops, main planting and harvesting seasons, rain seasons, inp... | 0 | missing_expected_official_file |
| F59 | sect07_com_w4.dta | Changes - Important events in the community in the last five years | 0 | missing_expected_official_file |
| F60 | sect08_com_w4.dta | Community Needs and Actions - Initiation, participation and mobilization of resources for community projects includin... | 0 | missing_expected_official_file |
| F61 | sect09_com_w4.dta | Productive Safety nets Program - Participation in the productive safety nets program; management and performance of t... | 0 | missing_expected_official_file |

## Required Next Action

Place the complete unchanged official raw package and documentation in the target folder.

After changing files in this folder, rerun:

`python script/17_audit_raw_downloads.py; python script/144_build_priority_lsms_isa_raw_package_intake_packet.py; python script/145_build_priority_lsms_isa_archive_member_preflight.py; python script/150_build_priority_lsms_isa_raw_package_receipt_checklist.py; python script/152_build_priority_lsms_isa_credentialed_raw_acquisition_workbench.py; python script/153_validate_priority_lsms_isa_official_file_receipt.py; python script/149_build_priority_lsms_isa_raw_value_verification_workbook.py; python script/132_build_priority_analysis_dataset_synthesis_blueprint.py; python script/148_build_priority_lsms_isa_country_wave_promotion_packets.py; python script/151_refresh_refocused_promoted_country_wave_registry.py; python script/127_enforce_promoted_data_gate.py; python script/36_build_direct_read_audit_bundle.py; python script/14_validate_workspace.py`

This validator only proves expected file-name receipt against official DDI
metadata. It does not prove variable values, labels, units, recall periods,
survey-design fields, merge keys, climate linkage, or analysis-ready status.
