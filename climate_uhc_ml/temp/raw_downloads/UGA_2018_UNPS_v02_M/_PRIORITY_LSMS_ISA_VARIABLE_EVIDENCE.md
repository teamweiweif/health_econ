# Priority LSMS-ISA Variable Evidence

Dataset: UGA_2018_UNPS_v02_M - Uganda 2018-2019

Status: official public metadata candidate variables only.

## Requirement Coverage

| Requirement | Candidate variables | Strong candidates | Candidate files | Status |
|---|---:|---:|---:|---|
| household_person_keys | 12 | 12 | 11 | official_metadata_strong_candidates_present_raw_review_required |
| weights_and_design | 12 | 0 | 7 | official_metadata_weak_candidates_present_raw_review_required |
| consumption_or_income | 12 | 8 | 4 | official_metadata_strong_candidates_present_raw_review_required |
| oop_health_expenditure | 2 | 0 | 1 | official_metadata_weak_candidates_present_raw_review_required |
| health_need_and_access | 12 | 12 | 6 | official_metadata_strong_candidates_present_raw_review_required |
| survey_timing | 12 | 12 | 4 | official_metadata_strong_candidates_present_raw_review_required |
| climate_geography | 12 | 12 | 4 | official_metadata_strong_candidates_present_raw_review_required |
| missing_codes_units_recall_skip_patterns | 0 | 0 | 0 | documentation_and_raw_review_required_no_variable_shortlist |

## File Shortlist

| Requirement | File | Candidate variables | Top variable names |
|---|---|---:|---|
| climate_geography | pov2018_19 | 4 | qurban;regurb;urban;district |
| climate_geography | GSEC1 | 4 | urban;district_code;s1aq07;regurb |
| climate_geography | WSEC1A | 2 | urban;regurb |
| climate_geography | AGSEC1 | 2 | region;urban |
| consumption_or_income | pov2018_19 | 7 | cpexp30;fcpexp30;nrrexp30;fnrfxp30;hpline;ctpline;spline |
| consumption_or_income | GSEC15B | 3 | CEB03;CEB04;CEB07 |
| consumption_or_income | GSEC15E | 1 | CEE02_1 |
| consumption_or_income | GSEC7_2 | 1 | IncomeSource |
| health_need_and_access | CSEC4B | 4 | s4bq23;s4bq26;s4bq27;s4bq28 |
| health_need_and_access | CSEC2B | 2 | s2bq09;s2bq10 |
| health_need_and_access | CSEC4C | 2 | healthservice_id;s4cq46 |
| health_need_and_access | CSEC4D | 2 | s4eq61;s4eq61_v2 |
| health_need_and_access | CSEC4L | 1 | health_water_id |
| health_need_and_access | CSEC4F | 1 | s4fq65 |
| household_person_keys | GSEC2 | 2 | hhid;t0_hhid |
| household_person_keys | GSEC1 | 1 | hhid |
| household_person_keys | GSEC2B | 1 | hhid |
| household_person_keys | GSEC4 | 1 | hhid |
| household_person_keys | GSEC5 | 1 | hhid |
| household_person_keys | GSEC6_1 | 1 | hhid |
| household_person_keys | GSEC6_3 | 1 | hhid |
| household_person_keys | GSEC6_5 | 1 | hhid |
| oop_health_expenditure | GSEC6_3 | 2 | t33;t34 |
| survey_timing | CSEC1B | 9 | s1bq3b_v2;s1bq4b_v2;s1bq2b;s1bq2c;s1bq3a_v2;s1bq3b;s1bq3c;s1bq4a_v2;s1bq4b |
| survey_timing | GSEC12_2 | 1 | t0_entStartYear |
| survey_timing | WSEC1A | 1 | month |
| survey_timing | GSEC1 | 1 | month |
| weights_and_design | GSEC15A | 5 | CEA01;CEA01A;CEA01B;CEA01C;CEA01D |
| weights_and_design | CSEC1A | 2 | EA_code;t0_EA_code |
| weights_and_design | WSEC1A | 1 | year |

Guardrail: these candidates are not raw value verification. Do not promote
this wave until the original raw package confirms values, labels, units,
recall periods, missing codes, skip patterns, merge keys, survey design,
timing/geography, and accepted climate linkage.
