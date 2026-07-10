# Manual Download Packet: NGA_2012_GHSP-W2_v02_M

Status: credentialed/manual official raw package acquisition packet.
This packet does not download raw data, accept terms, extract microdata,
write `data/`, or run models.

## Target

- Country: Nigeria
- Wave: 2012-2013
- IDNO: NGA_2012_GHSP-W2_v02_M
- Official get-microdata URL: https://microdata.worldbank.org/catalog/1952/get-microdata
- Local target folder: `temp/raw_downloads/NGA_2012_GHSP-W2_v02_M/`
- Expected official files: 103
- Missing expected files: 103
- Requirement-linked core file rows: 26
- Missing core file rows: 26

## Manual Action

Login/register at the official World Bank Microdata get-microdata page, accept terms if required, download the complete unchanged official raw package and documentation, and place every file under the local target folder.

## Core Files To Confirm After Download

| requirement | file_id | expected_file_name | file_description | top_variable_names | official_core_file_match_status |
| --- | --- | --- | --- | --- | --- |
| climate_geography | F121 | HHTrack | This data contains household interview status for wave 1 and wave 2, wave 1 and wave 2 population weights, and combined wave 1 and wave 2 population weights. | ea;lga;state;zone | missing_expected_core_file |
| climate_geography | F122 | secta_harvestw2 | Data collected using Post Harvest Agriculture Questionnaire, Section A (Household Identification). The data also contains geographic area identification variables. | ea;lga;state;zone | missing_expected_core_file |
| climate_geography | F18 | NGA_HouseholdGeovars_Y2 |  | LAT_DD_MOD;LON_DD_MOD | missing_expected_core_file |
| climate_geography | F119 | cons_agg_wave2_visit1 | Consumption aggregate data (visit 1) | ea | missing_expected_core_file |
| climate_geography | F120 | cons_agg_wave2_visit2 | Consumption aggregate data (visit 2) | ea | missing_expected_core_file |
| consumption_or_income | F119 | cons_agg_wave2_visit1 | Consumption aggregate data (visit 1) | totcons;nfdfoth;fdfishpr;fdothpr;fdrestby | missing_expected_core_file |
| consumption_or_income | F120 | cons_agg_wave2_visit2 | Consumption aggregate data (visit 2) | totcons;nfdfoth;fdfishpr;fdothpr;fdrestby | missing_expected_core_file |
| consumption_or_income | F38 | sect8e_plantingw2 | Data collected using Post Planting Household Questionnaire, Section 8e (Non-Food Expenditure - 12 months recall, non-food items that may not have been purchased). The data also contains geographic area identification variables. | s8q10 | missing_expected_core_file |
| consumption_or_income | F34 | sect8a_plantingw2 | Data collected using Post Planting Household Questionnaire, Section 8A (Non-Food Expenditure - 7 days). The data also contains geographic area identification variables. | ea | missing_expected_core_file |
| health_need_and_access | F73 | sect4a_harvestw2 | Data collected using Post Harvest Household Questionnaire, Section 4A (Health). The data also contains geographic area identification variables. | s4aq15;s4aq16;s4aq17;s4aq1;s4aq3;s4aq20;s4aq6a;s4aq6b;s4aq6c | missing_expected_core_file |
| health_need_and_access | F103 | secta7_harvestw2 | Data collected using Post Harvest Agriculture Questionnaire, Section A7 (Animal Costs). The data also contains geographic area identification variables. | cost_cd;cost_desc | missing_expected_core_file |
| health_need_and_access | F74 | sect4b_harvestw2 | Data collected using Post Harvest Household Questionnaire, Section 4B (Child Immunization). The data also contains geographic area identification variables. | s4bq3 | missing_expected_core_file |
| household_person_keys | F20 | sect1_plantingw2 | Data collected using Post Planting Household Questionnaire, Section 1 (Household Roster). The data also contains geographic area identification variables. | hhid | missing_expected_core_file |
| household_person_keys | F68 | sect1_harvestw2 | Data collected using Post Harvest Household Questionnaire, Section 1 (Household Roster). The data also contains geographic area identification variables. | hhid | missing_expected_core_file |
| household_person_keys | F110 | secta10_harvestw2 | Data collected using Post Harvest Agriculture Questionnaire, Section A10 (Network Roster). The data also contains geographic area identification variables. | hhid | missing_expected_core_file |
| household_person_keys | F42 | sect11a_plantingw2 | Data collected using Post Planting Agriculture Questionnaire, Section 11A (Plot Roster). The data also contains geographic area identification variables. | hhid | missing_expected_core_file |
| household_person_keys | F43 | sect11a1_plantingw2 | Data collected using Post Planting Agriculture Questionnaire, Section 11A (Plot Roster) and questions 4 to 6. The data also contains geographic area identification variables. | hhid | missing_expected_core_file |
| household_person_keys | F58 | sect12_plantingw2 | Data collected using Post Planting Agriculture Questionnaire, Section 12 (Network Roster). The data also contains geographic area identification variables. | hhid | missing_expected_core_file |
| household_person_keys | F121 | HHTrack | This data contains household interview status for wave 1 and wave 2, wave 1 and wave 2 population weights, and combined wave 1 and wave 2 population weights. | hhid | missing_expected_core_file |
| household_person_keys | F122 | secta_harvestw2 | Data collected using Post Harvest Agriculture Questionnaire, Section A (Household Identification). The data also contains geographic area identification variables. | hhid | missing_expected_core_file |
| oop_health_expenditure | F73 | sect4a_harvestw2 | Data collected using Post Harvest Household Questionnaire, Section 4A (Health). The data also contains geographic area identification variables. | s4aq20;s4aq20b;s4aq13;s4aq35a;s4aq35b;s4aq35c | missing_expected_core_file |
| survey_timing | F122 | secta_harvestw2 | Data collected using Post Harvest Agriculture Questionnaire, Section A (Household Identification). The data also contains geographic area identification variables. | saq14ah;saq14am;saq14bh;saq14bm;saq18ah;saq18am;saq18bh;saq18bm;saq22ah;saq22am;saq22bh;saq22bm | missing_expected_core_file |
| weights_and_design | F121 | HHTrack | This data contains household interview status for wave 1 and wave 2, wave 1 and wave 2 population weights, and combined wave 1 and wave 2 population weights. | wt_combined;wt_w1v1;wt_w1v2;wt_w2v1;wt_w2v2;wt_wave1;wt_wave2 | missing_expected_core_file |
| weights_and_design | F119 | cons_agg_wave2_visit1 | Consumption aggregate data (visit 1) | ea;hhweight | missing_expected_core_file |
| weights_and_design | F120 | cons_agg_wave2_visit2 | Consumption aggregate data (visit 2) | ea;hhweight | missing_expected_core_file |
| weights_and_design | F122 | secta_harvestw2 | Data collected using Post Harvest Agriculture Questionnaire, Section A (Household Identification). The data also contains geographic area identification variables. | wt_combined | missing_expected_core_file |

## Post-Download Validation

Run after the complete official package and documentation are placed locally:

```bash
python script/150_build_priority_lsms_isa_raw_package_receipt_checklist.py; python script/153_validate_priority_lsms_isa_official_file_receipt.py; python script/157_build_priority_lsms_isa_received_raw_schema_audit.py; python script/158_build_priority_lsms_isa_received_raw_value_profile.py; python script/159_build_priority_lsms_isa_received_raw_semantics_review.py
```

## Stop Rule

Do not write this country-wave into data/ until complete official file receipt, raw value verification, outcome construction, survey timing/geography, and accepted CHIRPS or ERA5 climate linkage all pass.
