# Priority LSMS-ISA Variable Evidence

Dataset: UGA_2015_UNPS_v02_M - Uganda 2015-2016

Status: official public metadata candidate variables only.

## Requirement Coverage

| Requirement | Candidate variables | Strong candidates | Candidate files | Status |
|---|---:|---:|---:|---|
| household_person_keys | 12 | 12 | 12 | official_metadata_strong_candidates_present_raw_review_required |
| weights_and_design | 12 | 3 | 4 | official_metadata_strong_candidates_present_raw_review_required |
| consumption_or_income | 12 | 7 | 3 | official_metadata_strong_candidates_present_raw_review_required |
| oop_health_expenditure | 3 | 1 | 2 | official_metadata_strong_candidates_present_raw_review_required |
| health_need_and_access | 12 | 12 | 5 | official_metadata_strong_candidates_present_raw_review_required |
| survey_timing | 12 | 8 | 9 | official_metadata_strong_candidates_present_raw_review_required |
| climate_geography | 12 | 11 | 4 | official_metadata_strong_candidates_present_raw_review_required |
| missing_codes_units_recall_skip_patterns | 0 | 0 | 0 | documentation_and_raw_review_required_no_variable_shortlist |

## File Shortlist

| Requirement | File | Candidate variables | Top variable names |
|---|---|---:|---|
| climate_geography | AGSEC2B | 3 | GPS_Manual;GPS_Not_Captured;Visit_GPS_Parcel |
| climate_geography | gsec1 | 4 | urban;ea;sregion;h1aq5 |
| climate_geography | AGSEC1 | 3 | urban;sregion;h1aq5 |
| climate_geography | pov2015_16 | 2 | regurb;urban |
| consumption_or_income | pov2015_16 | 10 | cpexp30;nrrexp30;hpline;ctpline;spline;district;equiv;hh;hsize;plinen |
| consumption_or_income | AGSEC1 | 1 | interview |
| consumption_or_income | gsec1 | 1 | interview |
| health_need_and_access | gsec5 | 4 | h5q4;h5q5;h5q8;h5q9 |
| health_need_and_access | CSEC4B_1 | 3 | C4BQ23;C4BQ19;C4BQ20 |
| health_need_and_access | CSEC2B_1 | 2 | C2BQ10;C2BQ9 |
| health_need_and_access | CSEC4A_1 | 2 | C4AQ8;C4Q7 |
| health_need_and_access | CSEC4M | 1 | End_sup_health |
| household_person_keys | unps_geovars_2015_16 | 1 | HHID |
| household_person_keys | gsec2 | 1 | pid |
| household_person_keys | gsec3 | 1 | pid |
| household_person_keys | gsec4 | 1 | pid |
| household_person_keys | gsec5 | 1 | pid |
| household_person_keys | gsec6_1 | 1 | pid |
| household_person_keys | gsec6_3 | 1 | pid |
| household_person_keys | gsec8 | 1 | pid |
| oop_health_expenditure | AGSEC7B | 2 | a7bq7c;a7bq8c |
| oop_health_expenditure | gsec5 | 1 | h5q12 |
| survey_timing | CSEC3I | 2 | C3IQ46A;C3IQ46B |
| survey_timing | CSEC4M | 2 | C4MQ111A;C4MQ111B |
| survey_timing | CSEC6A_1 | 1 | Endtime_Community |
| survey_timing | CSEC6F_1 | 1 | Endtime_Works |
| survey_timing | GSEC16 | 2 | h16q02a;h16q2y |
| survey_timing | gsec1 | 1 | month |
| survey_timing | WSEC5 | 1 | w5q13a |
| survey_timing | gsec2 | 1 | h2q9c |

Guardrail: these candidates are not raw value verification. Do not promote
this wave until the original raw package confirms values, labels, units,
recall periods, missing codes, skip patterns, merge keys, survey design,
timing/geography, and accepted climate linkage.
