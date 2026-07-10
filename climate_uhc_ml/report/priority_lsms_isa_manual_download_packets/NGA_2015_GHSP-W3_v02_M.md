# Manual Download Packet: NGA_2015_GHSP-W3_v02_M

Status: credentialed/manual official raw package acquisition packet.
This packet does not download raw data, accept terms, extract microdata,
write `data/`, or run models.

## Target

- Country: Nigeria
- Wave: 2015-2016
- IDNO: NGA_2015_GHSP-W3_v02_M
- Official get-microdata URL: https://microdata.worldbank.org/catalog/2734/get-microdata
- Local target folder: `temp/raw_downloads/NGA_2015_GHSP-W3_v02_M/`
- Expected official files: 104
- Missing expected files: 104
- Requirement-linked core file rows: 26
- Missing core file rows: 26

## Manual Action

Login/register at the official World Bank Microdata get-microdata page, accept terms if required, download the complete unchanged official raw package and documentation, and place every file under the local target folder.

## Core Files To Confirm After Download

| requirement | file_id | expected_file_name | file_description | top_variable_names | official_core_file_match_status |
| --- | --- | --- | --- | --- | --- |
| climate_geography | F40 | sect1_harvestw3 | Individual level data on relationship to the household, gender, year of birth, age, marital status, polygamous marriages, spouse identification, parental status, place of birth, date joined household if new, migration - collected through Post-Harvest Household Questionnaire, Section 1 (Household Roster) | s1q31a;s1q31b;s1q31c;s1q31d | missing_expected_core_file |
| climate_geography | F97 | NGA_HouseholdGeovars_Y3 | Household level geospatial data | LAT_DD_MOD;LON_DD_MOD | missing_expected_core_file |
| climate_geography | F104 | sectc1_harvestw3 | Community data on respondent characteristics - collected through Post Harvest Community Questionnaire, Section C1 (Respondent Characteristics) | ea;lga | missing_expected_core_file |
| climate_geography | F109 | sectc2_harvestw3 | Data on community infrastructure and transportation - collected through Post Harvest Community Questionnaire, Section C2 (Community Infrastructure and Transportation) | ea;lga | missing_expected_core_file |
| climate_geography | F113 | cons_agg_wave3_visit1 | Consumption aggregate data (visit 1) | ea | missing_expected_core_file |
| climate_geography | F114 | cons_agg_wave3_visit2 | Consumption aggregate data (visit 2) | ea | missing_expected_core_file |
| consumption_or_income | F113 | cons_agg_wave3_visit1 | Consumption aggregate data (visit 1) | totcons;nfdfoth;fdfishpr;fdothpr;fdrestby | missing_expected_core_file |
| consumption_or_income | F114 | cons_agg_wave3_visit2 | Consumption aggregate data (visit 2) | totcons;nfdfoth;fdfishpr;fdothpr;fdrestby | missing_expected_core_file |
| consumption_or_income | F12 | sect8a_plantingw3 | Data on non-food expenditure within the household (in the past 7 days) - collected through Post Planting Household Questionnaire, Section 8 (Non-food Expenditure), questions 1 and 2 | ea;hhid | missing_expected_core_file |
| health_need_and_access | F43 | sect4a_harvestw3 | Household member/ individual level health data - collected through Post-Harvest Household Questionnaire, Section 4 (Health) | s4aq15;s4aq16;s4aq17;s4aq1;s4aq6a;s4aq6a_os;s4aq6b;s4aq6b_os;s4aq3;s4aq3b;s4aq3b_os | missing_expected_core_file |
| health_need_and_access | F3 | sect3_plantingw3 | Individual level data on labor market participation during the last seven days, wage work, and domestic activities within the home (all individuals 5 years and above) - collected through Post Planting Household Questionnaire, Section 3 (Labor) | s3q9b | missing_expected_core_file |
| household_person_keys | F19 | sect11a_plantingw3 | Plot level data on all plots owned and/or managed by the Household - collected through Post Planting Agriculture Questionnaire, Section 11A (Plot Roster), questions 1 and 2 | hhid | missing_expected_core_file |
| household_person_keys | F2 | sect1_plantingw3 | Individual level data on relationship to the household, gender, year of birth, age, marital status, spouse identification, parental status, and place of birth - collected through Post Planting Household Questionnaire, Section 1 (Household Roster) | hhid | missing_expected_core_file |
| household_person_keys | F20 | sect11a1_plantingw3 | Plot level data on all plots owned and/or managed by the Household - collected through Post Planting Agriculture Questionnaire, Section 11A (Plot Roster), questions 4 to 6 | hhid | missing_expected_core_file |
| household_person_keys | F30 | sect12_plantingw3 | Roster of places or businesses where the household sells and purchases agricultural produce and/or supplies - collected through Post Planting Agriculture Questionnaire, Section 12 (Network Roster) | hhid | missing_expected_core_file |
| household_person_keys | F40 | sect1_harvestw3 | Individual level data on relationship to the household, gender, year of birth, age, marital status, polygamous marriages, spouse identification, parental status, place of birth, date joined household if new, migration - collected through Post-Harvest Household Questionnaire, Section 1 (Household Roster) | hhid | missing_expected_core_file |
| household_person_keys | F81 | secta10_harvestw3 | Roster of places or businesses where the household sells and purchases agricultural produce and/or supplies - collected through Post Harvest Agriculture Questionnaire, Section A9b (Fishing Capital and Revenu) | hhid | missing_expected_core_file |
| household_person_keys | F10 | sect7a_plantingw3 | Data on meals prepared and consumed outside home (in the past 7 days) - collected through Post Planting Household Questionnaire, Section 7A (Meals Away from Home) | hhid | missing_expected_core_file |
| household_person_keys | F107 | sect7b_plantingw3 | Data on food expenditure within the household (in the past 7 days) - collected through Post Planting Household Questionnaire, Section 7B (Food Expenditure) | hhid | missing_expected_core_file |
| oop_health_expenditure | F43 | sect4a_harvestw3 | Household member/ individual level health data - collected through Post-Harvest Household Questionnaire, Section 4 (Health) | s4aq20;s4aq20b;s4aq13;s4aq35a;s4aq35b;s4aq35c | missing_expected_core_file |
| survey_timing | F115 | secta_harvestw3 | Data on household identifier variables, enumerator, supervisor, and data entry clerk identifiers, date and time of interview and data entry, and observation notes by enumerator regarding the interview - collected through Post-Harvest Household Questionnaire, Section A-1 (Household Identification) | saq14ah;saq14am;saq14bh;saq14bm;saq17ah;saq17am;saq17bh;saq17bm;saq20ah;saq20am;saq20bh;saq20bm | missing_expected_core_file |
| weights_and_design | F110 | HHTrack | Data on status of households across all six visits of the three waves. The data also contains the full set of survey weights. | wt_combined;wt_w1_w2_w3;wt_w1_w3;wt_w1v1;wt_w1v2;wt_w2_w3 | missing_expected_core_file |
| weights_and_design | F113 | cons_agg_wave3_visit1 | Consumption aggregate data (visit 1) | ea;hhweight | missing_expected_core_file |
| weights_and_design | F114 | cons_agg_wave3_visit2 | Consumption aggregate data (visit 2) | ea;hhweight | missing_expected_core_file |
| weights_and_design | F104 | sectc1_harvestw3 | Community data on respondent characteristics - collected through Post Harvest Community Questionnaire, Section C1 (Respondent Characteristics) | ea | missing_expected_core_file |
| weights_and_design | F109 | sectc2_harvestw3 | Data on community infrastructure and transportation - collected through Post Harvest Community Questionnaire, Section C2 (Community Infrastructure and Transportation) | ea | missing_expected_core_file |

## Post-Download Validation

Run after the complete official package and documentation are placed locally:

```bash
python script/150_build_priority_lsms_isa_raw_package_receipt_checklist.py; python script/153_validate_priority_lsms_isa_official_file_receipt.py; python script/157_build_priority_lsms_isa_received_raw_schema_audit.py; python script/158_build_priority_lsms_isa_received_raw_value_profile.py; python script/159_build_priority_lsms_isa_received_raw_semantics_review.py
```

## Stop Rule

Do not write this country-wave into data/ until complete official file receipt, raw value verification, outcome construction, survey timing/geography, and accepted CHIRPS or ERA5 climate linkage all pass.
