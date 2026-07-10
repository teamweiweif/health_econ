# Manual Download Packet: ETH_2021_ESPS-W5_v02_M

Status: credentialed/manual official raw package acquisition packet.
This packet does not download raw data, accept terms, extract microdata,
write `data/`, or run models.

## Target

- Country: Ethiopia
- Wave: 2021-2022
- IDNO: ETH_2021_ESPS-W5_v02_M
- Official get-microdata URL: https://microdata.worldbank.org/catalog/6161/get-microdata
- Local target folder: `temp/raw_downloads/ETH_2021_ESPS-W5_v02_M/`
- Expected official files: 68
- Missing expected files: 68
- Requirement-linked core file rows: 36
- Missing core file rows: 36

## Manual Action

Login/register at the official World Bank Microdata get-microdata page, accept terms if required, download the complete unchanged official raw package and documentation, and place every file under the local target folder.

## Core Files To Confirm After Download

| requirement | file_id | expected_file_name | file_description | top_variable_names | official_core_file_match_status |
| --- | --- | --- | --- | --- | --- |
| climate_geography | F1 | sect_cover_hh_w5.dta | Household Data - Cover page | saq19__Latitude;saq19__Longitude | missing_expected_core_file |
| climate_geography | F42 | sect10a_com_w5.dta | Community - Market prices: market location | cs10q05__Latitude;cs10q05__Longitude | missing_expected_core_file |
| climate_geography | F46 | sect_cover_pp_w5.dta | Post-planting - Cover page | saq19__Latitude;saq19__Longitude | missing_expected_core_file |
| climate_geography | F54 | sect_cover_ph_w5.dta | Post-harvest - Cover page | saq19__Latitude;saq19__Longitude | missing_expected_core_file |
| climate_geography | F59 | sect_cover_ls_w5.dta | Livestock - Cover page | saq19__Latitude;saq19__Longitude | missing_expected_core_file |
| climate_geography | F49 | sect3_pp_w5.dta | Post-planting - Field roster | s3q09__Latitude;s3q09__Longitude | missing_expected_core_file |
| consumption_or_income | F66 | cons_agg_w5.dta | Household Data - Consumption aggregate | nonfood_cons2;nom_nonfoodcons_aeq;nonfood_cons_ann;food_cons2;food_cons_ann;nom_foodcons_aeq;fafh_cons_ann;spat_totcons_aeq;educ_cons_ann;nom_educcons_aeq;nom_totcons_aeq;total_cons_ann | missing_expected_core_file |
| health_need_and_access | F4 | sect3_hh_w5.dta | Household Data - Health | s3q14;s3q15;s3q05;s3q17;s3q13;s3q18 | missing_expected_core_file |
| health_need_and_access | F36 | sect04_com_w5.dta | Community - Access to basic services and infrastructure | cs4q37;cs4q34;cs4q35;cs4q28 | missing_expected_core_file |
| health_need_and_access | F49 | sect3_pp_w5.dta | Post-planting - Field roster | s3q15_1;s3q15_2 | missing_expected_core_file |
| household_person_keys | F2 | sect1_hh_w5.dta | Household Data - Roster | individual_id;household_id | missing_expected_core_file |
| household_person_keys | F21 | sect12b1_hh_w5.dta | Household Data - Nonfarm enterprises roster | household_id | missing_expected_core_file |
| household_person_keys | F47 | sect1_pp_w5.dta | Post-planting - Household roster | household_id | missing_expected_core_file |
| household_person_keys | F55 | sect1_ph_w5.dta | Post-harvest - Household roster | household_id | missing_expected_core_file |
| household_person_keys | F48 | sect2_pp_w5.dta | Post-planting - Parcel roster | household_id | missing_expected_core_file |
| household_person_keys | F49 | sect3_pp_w5.dta | Post-planting - Field roster | household_id | missing_expected_core_file |
| household_person_keys | F50 | sect4_pp_w5.dta | Post-planting - Crop field roster | household_id | missing_expected_core_file |
| household_person_keys | F13 | sect6c_hh_w5.dta | Household Data - Dietary quality | individual_id | missing_expected_core_file |
| oop_health_expenditure | F62 | sect8_3_ls_w5.dta | Livestock - Livestock breeding, health, shelter, water, and feed | ls_s8_3q04;ls_s8_3q22;ls_s8_3q24;ls_s8_3q03;ls_s8_3q05;ls_s8_3q06;ls_s8_3q10a;ls_s8_3q10b;ls_s8_3q11;ls_s8_3q12_1 | missing_expected_core_file |
| oop_health_expenditure | F4 | sect3_hh_w5.dta | Household Data - Health | s3q17;s3q18 | missing_expected_core_file |
| survey_timing | F46 | sect_cover_pp_w5.dta | Post-planting - Cover page | InterviewDate | missing_expected_core_file |
| survey_timing | F54 | sect_cover_ph_w5.dta | Post-harvest - Cover page | InterviewDate | missing_expected_core_file |
| survey_timing | F59 | sect_cover_ls_w5.dta | Livestock - Cover page | InterviewDate | missing_expected_core_file |
| survey_timing | F21 | sect12b1_hh_w5.dta | Household Data - Nonfarm enterprises roster | s12bq08a;s12bq08b | missing_expected_core_file |
| survey_timing | F15 | sect7b_hh_w5.dta | Household Data - Nonfood expenditure, 12 months | item_cd_12months;s7q04 | missing_expected_core_file |
| survey_timing | F64 | eth_householdgeovariables_y5.dta | Household geo-variables | wetQ_avgstart | missing_expected_core_file |
| survey_timing | F1 | sect_cover_hh_w5.dta | Household Data - Cover page | saq19__Timestamp | missing_expected_core_file |
| survey_timing | F65 | eth_plotgeovariables_y5.dta | Plot geo-variables | wetQ_avgstart | missing_expected_core_file |
| weights_and_design | F1 | sect_cover_hh_w5.dta | Household Data - Cover page | pw_w5;ea_id | missing_expected_core_file |
| weights_and_design | F10 | sect6b2_hh_w5.dta | Household Data - Food shared by non-household members (Filter Question) | pw_w5 | missing_expected_core_file |
| weights_and_design | F11 | sect6b3_hh_w5.dta | Household Data - Food shared by non-household members | pw_w5 | missing_expected_core_file |
| weights_and_design | F12 | sect6b4_hh_w5.dta | Household Data - Food consumed outside home | pw_w5 | missing_expected_core_file |
| weights_and_design | F13 | sect6c_hh_w5.dta | Household Data - Dietary quality | pw_w5 | missing_expected_core_file |
| weights_and_design | F14 | sect7a_hh_w5.dta | Household Data - Nonfood expenditure, one month | pw_w5 | missing_expected_core_file |
| weights_and_design | F15 | sect7b_hh_w5.dta | Household Data - Nonfood expenditure, 12 months | pw_w5 | missing_expected_core_file |
| weights_and_design | F16 | sect8_hh_w5.dta | Household Data - Food insecurity experience scale | pw_w5 | missing_expected_core_file |

## Post-Download Validation

Run after the complete official package and documentation are placed locally:

```bash
python script/150_build_priority_lsms_isa_raw_package_receipt_checklist.py; python script/153_validate_priority_lsms_isa_official_file_receipt.py; python script/157_build_priority_lsms_isa_received_raw_schema_audit.py; python script/158_build_priority_lsms_isa_received_raw_value_profile.py; python script/159_build_priority_lsms_isa_received_raw_semantics_review.py
```

## Stop Rule

Do not write this country-wave into data/ until complete official file receipt, raw value verification, outcome construction, survey timing/geography, and accepted CHIRPS or ERA5 climate linkage all pass.
