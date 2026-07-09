# Priority LSMS-ISA Variable Evidence

Dataset: UGA_2019_UNPS_v03_M - Uganda 2019-2020

Status: official public metadata candidate variables only.

## Requirement Coverage

| Requirement | Candidate variables | Strong candidates | Candidate files | Status |
|---|---:|---:|---:|---|
| household_person_keys | 12 | 12 | 12 | official_metadata_strong_candidates_present_raw_review_required |
| weights_and_design | 12 | 12 | 12 | official_metadata_strong_candidates_present_raw_review_required |
| consumption_or_income | 12 | 12 | 2 | official_metadata_strong_candidates_present_raw_review_required |
| oop_health_expenditure | 12 | 12 | 3 | official_metadata_strong_candidates_present_raw_review_required |
| health_need_and_access | 12 | 12 | 4 | official_metadata_strong_candidates_present_raw_review_required |
| survey_timing | 12 | 3 | 6 | official_metadata_strong_candidates_present_raw_review_required |
| climate_geography | 12 | 12 | 10 | official_metadata_strong_candidates_present_raw_review_required |
| missing_codes_units_recall_skip_patterns | 0 | 0 | 0 | documentation_and_raw_review_required_no_variable_shortlist |

## File Shortlist

| Requirement | File | Candidate variables | Top variable names |
|---|---|---:|---|
| climate_geography | pov2019_20.NSDstat | 3 | regurb;urban;district |
| climate_geography | GSEC1.NSDstat | 1 | urban |
| climate_geography | CSEC1A.NSDstat | 1 | Final_EA_code |
| climate_geography | CSEC2.NSDstat | 1 | Final_EA_code |
| climate_geography | CSEC2A.NSDstat | 1 | Final_EA_code |
| climate_geography | CSEC2B.NSDstat | 1 | Final_EA_code |
| climate_geography | CSEC2C.NSDstat | 1 | Final_EA_code |
| climate_geography | CSEC2C_0.NSDstat | 1 | Final_EA_code |
| consumption_or_income | GSEC15B.NSDstat | 9 | CEB03;CEB04;CEB07;CEB10;CEB11;CEB14a;CEB15;CEB16;coicop_2 |
| consumption_or_income | pov2019_20.NSDstat | 3 | cpexp30;nrrexp30;hpline |
| health_need_and_access | CSEC2B.NSDstat | 6 | s2bq13__1;s2bq09;s2bq10;s2bq13__2;s2bq13__3;s2bq13__4 |
| health_need_and_access | CSEC4B.NSDstat | 4 | s4bq23;s4bq26;s4bq27;s4bq28 |
| health_need_and_access | CSEC4L.NSDstat | 1 | Health_Water_id |
| health_need_and_access | GSEC6_1.NSDstat | 1 | s6q15b |
| household_person_keys | GSEC2.NSDstat | 1 | hhid |
| household_person_keys | GSEC15C.NSDstat | 1 | hhid |
| household_person_keys | GSEC15D.NSDstat | 1 | hhid |
| household_person_keys | GSEC17_1.NSDstat | 1 | hhid |
| household_person_keys | GSEC19.NSDstat | 1 | hhid |
| household_person_keys | GSEC1.NSDstat | 1 | hhid |
| household_person_keys | GSEC7_1.NSDstat | 1 | hhid |
| household_person_keys | GSEC7_2.NSDstat | 1 | hhid |
| oop_health_expenditure | GSEC5.NSDstat | 8 | h5q12a;h5q12b;h5q12f;h5q12f_1;h5q12g;h5q12c;h5q12d;h5q12e |
| oop_health_expenditure | GSEC6_1.NSDstat | 3 | h6q12h;s6q07_1;s6q07_3i |
| oop_health_expenditure | GSEC6_3.NSDstat | 1 | t31 |
| survey_timing | GSEC12_2.NSDstat | 3 | h12q04;h12q12;h12q13 |
| survey_timing | GSEC1.NSDstat | 2 | month;year |
| survey_timing | AGSEC5A.NSDstat | 3 | s5aq06f_1;s5aq06f_11;s5aq06f_1_1 |
| survey_timing | GSEC2.NSDstat | 2 | h2q9b;h2q9c |
| survey_timing | GSEC9.NSDstat | 1 | dwellingVisit |

Guardrail: these candidates are not raw value verification. Do not promote
this wave until the original raw package confirms values, labels, units,
recall periods, missing codes, skip patterns, merge keys, survey design,
timing/geography, and accepted climate linkage.
