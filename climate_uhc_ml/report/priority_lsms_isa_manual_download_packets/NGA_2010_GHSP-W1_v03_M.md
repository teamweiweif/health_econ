# Manual Download Packet: NGA_2010_GHSP-W1_v03_M

Status: credentialed/manual official raw package acquisition packet.
This packet does not download raw data, accept terms, extract microdata,
write `data/`, or run models.

## Target

- Country: Nigeria
- Wave: 2010-2011
- IDNO: NGA_2010_GHSP-W1_v03_M
- Official get-microdata URL: https://microdata.worldbank.org/catalog/1002/get-microdata
- Local target folder: `temp/raw_downloads/NGA_2010_GHSP-W1_v03_M/`
- Expected official files: 99
- Missing expected files: 99
- Requirement-linked core file rows: 27
- Missing core file rows: 27

## Manual Action

Login/register at the official World Bank Microdata get-microdata page, accept terms if required, download the complete unchanged official raw package and documentation, and place every file under the local target folder.

## Core Files To Confirm After Download

| requirement | file_id | expected_file_name | file_description | top_variable_names | official_core_file_match_status |
| --- | --- | --- | --- | --- | --- |
| climate_geography | F2 | NGA_HouseholdGeovariables_Y1 |  | lat_dd_mod;lon_dd_mod;ea;eviarea_avg;grn_avg;h2010_eviarea;h2010_grn;h2010_sen;lga;sen_avg | missing_expected_core_file |
| climate_geography | F98 | cons_agg_wave1_visit1 | Consumption aggregate data (visit 1) | ea | missing_expected_core_file |
| climate_geography | F99 | cons_agg_wave1_visit2 | Consumption aggregate data (visit 2) | ea | missing_expected_core_file |
| consumption_or_income | F98 | cons_agg_wave1_visit1 | Consumption aggregate data (visit 1) | totcons;nfdfoth;fdfishpr;fdothpr;fdrestby;fdalcpr;fdbeanpr | missing_expected_core_file |
| consumption_or_income | F99 | cons_agg_wave1_visit2 | Consumption aggregate data (visit 2) | totcons;nfdfoth;fdfishpr;fdothpr;fdrestby | missing_expected_core_file |
| health_need_and_access | F34 | sect4a_harvestw1 |  | s4aq15;s4aq16;s4aq17;s4aq1;s4aq3;s4aq6a;s4aq6b;s4aq6c;s4aq20;s4aq20b | missing_expected_core_file |
| health_need_and_access | F35 | sect4b_harvestw1 |  | s4bq3 | missing_expected_core_file |
| health_need_and_access | F32 | sect3a_harvestw1 |  | s3aq17 | missing_expected_core_file |
| household_person_keys | F10 | secta7_harvestw1 |  | hhid | missing_expected_core_file |
| household_person_keys | F11 | secta8_harvestw1 |  | hhid | missing_expected_core_file |
| household_person_keys | F12 | secta9a1_harvestw1 |  | hhid | missing_expected_core_file |
| household_person_keys | F13 | secta9a2_harvestw1 |  | hhid | missing_expected_core_file |
| household_person_keys | F14 | secta9b1_harvestw1 |  | hhid | missing_expected_core_file |
| household_person_keys | F15 | secta9b2_harvestw1 |  | hhid | missing_expected_core_file |
| household_person_keys | F16 | secta10_harvestw1 |  | hhid | missing_expected_core_file |
| household_person_keys | F17 | secta41_harvestw1 |  | hhid | missing_expected_core_file |
| oop_health_expenditure | F34 | sect4a_harvestw1 |  | s4aq20;s4aq20b;s4aq19;s4aq13;s4aq17 | missing_expected_core_file |
| survey_timing | F57 | secta_harvestw1 |  | saq14ah;saq14am;saq14bh;saq14bm;saq18ah;saq18am;saq18bh;saq18bm;saq22ah;saq22am;saq22bh | missing_expected_core_file |
| survey_timing | F73 | sectc_plantingw1 |  | interview_date | missing_expected_core_file |
| weights_and_design | F98 | cons_agg_wave1_visit1 | Consumption aggregate data (visit 1) | ea;hhweight | missing_expected_core_file |
| weights_and_design | F99 | cons_agg_wave1_visit2 | Consumption aggregate data (visit 2) | ea;hhweight | missing_expected_core_file |
| weights_and_design | F2 | NGA_HouseholdGeovariables_Y1 |  | ea;eviarea_avg;h2010_eviarea | missing_expected_core_file |
| weights_and_design | F10 | secta7_harvestw1 |  | ea | missing_expected_core_file |
| weights_and_design | F11 | secta8_harvestw1 |  | ea | missing_expected_core_file |
| weights_and_design | F12 | secta9a1_harvestw1 |  | ea | missing_expected_core_file |
| weights_and_design | F13 | secta9a2_harvestw1 |  | ea | missing_expected_core_file |
| weights_and_design | F14 | secta9b1_harvestw1 |  | ea | missing_expected_core_file |

## Post-Download Validation

Run after the complete official package and documentation are placed locally:

```bash
python script/150_build_priority_lsms_isa_raw_package_receipt_checklist.py; python script/153_validate_priority_lsms_isa_official_file_receipt.py; python script/157_build_priority_lsms_isa_received_raw_schema_audit.py; python script/158_build_priority_lsms_isa_received_raw_value_profile.py; python script/159_build_priority_lsms_isa_received_raw_semantics_review.py
```

## Stop Rule

Do not write this country-wave into data/ until complete official file receipt, raw value verification, outcome construction, survey timing/geography, and accepted CHIRPS or ERA5 climate linkage all pass.
