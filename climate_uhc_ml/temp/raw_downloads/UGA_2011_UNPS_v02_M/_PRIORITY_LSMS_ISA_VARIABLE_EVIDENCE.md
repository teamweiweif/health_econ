# Priority LSMS-ISA Variable Evidence

Dataset: UGA_2011_UNPS_v02_M - Uganda 2011-2012

Status: official public metadata candidate variables only.

## Requirement Coverage

| Requirement | Candidate variables | Strong candidates | Candidate files | Status |
|---|---:|---:|---:|---|
| household_person_keys | 12 | 12 | 11 | official_metadata_strong_candidates_present_raw_review_required |
| weights_and_design | 12 | 0 | 4 | official_metadata_weak_candidates_present_raw_review_required |
| consumption_or_income | 12 | 12 | 4 | official_metadata_strong_candidates_present_raw_review_required |
| oop_health_expenditure | 5 | 3 | 3 | official_metadata_strong_candidates_present_raw_review_required |
| health_need_and_access | 12 | 12 | 9 | official_metadata_strong_candidates_present_raw_review_required |
| survey_timing | 12 | 12 | 4 | official_metadata_strong_candidates_present_raw_review_required |
| climate_geography | 12 | 12 | 1 | official_metadata_strong_candidates_present_raw_review_required |
| missing_codes_units_recall_skip_patterns | 0 | 0 | 0 | documentation_and_raw_review_required_no_variable_shortlist |

## File Shortlist

| Requirement | File | Candidate variables | Top variable names |
|---|---|---:|---|
| climate_geography | CSEC1.NSDstat | 12 | GPS_Manual_Health;cgpsdlg2;cgpsdlg3;cgpsdlg4;cgpsdlg5;cgpsdlt2;cgpsdlt3;cgpsdlt4;cgpsdlt5;cgpsmlg2_min;cgpsmlg2_sec;cgpsmlg3_min |
| consumption_or_income | GSEC15B.NSDstat | 8 | h15bq14;h15bq15;h15bq2d;h15bq3a;h15bq3b;h15bq4;h15bq5;itmcd |
| consumption_or_income | UNPS 2011-12 Consumption Aggregate.NSDstat | 2 | welfare;cpexp30 |
| consumption_or_income | GSEC15BB.NSDstat | 1 | h15bq14 |
| consumption_or_income | GSEC15C.NSDstat | 1 | h15cq2 |
| health_need_and_access | CSEC4l.NSDstat | 2 | c4lq102;c4lq102_other |
| health_need_and_access | CSEC2b.NSDstat | 2 | c2bq10;c2bq9 |
| health_need_and_access | CSEC4c.NSDstat | 2 | c4cq46;c4cq48 |
| health_need_and_access | CSEC4n.NSDstat | 1 | End_sup_health |
| health_need_and_access | CSEC4ab.NSDstat | 1 | c4bq23 |
| health_need_and_access | CSEC4d.NSDstat | 1 | End_Diseases |
| health_need_and_access | CSEC4e.NSDstat | 1 | c4e61 |
| health_need_and_access | CSEC4f.NSDstat | 1 | c4fq72 |
| household_person_keys | GSEC2.NSDstat | 2 | PID;HHID |
| household_person_keys | UNPS 2011-12 Consumption Aggregate.NSDstat | 1 | HHID |
| household_person_keys | GSEC1.NSDstat | 1 | HHID |
| household_person_keys | GSEC3.NSDstat | 1 | PID |
| household_person_keys | GSEC4.NSDstat | 1 | PID |
| household_person_keys | GSEC5.NSDstat | 1 | PID |
| household_person_keys | GSEC6A.NSDstat | 1 | PID |
| household_person_keys | GSEC6B.NSDstat | 1 | PID |
| oop_health_expenditure | GSEC6A.NSDstat | 2 | h6q7;h6q8 |
| oop_health_expenditure | AGSEC7B.NSDstat | 2 | a7bq7c;a7bq8c |
| oop_health_expenditure | GSEC5.NSDstat | 1 | h5q12 |
| survey_timing | CSEC1.NSDstat | 8 | End_Time;c1bq2a;c1bq2c;c1bq4c;c1bq5a;c1bq5c;c1bq6a;c1bq6c |
| survey_timing | AGSEC1.NSDstat | 2 | a1bq2;a1bq2s |
| survey_timing | AGSEC9.NSDstat | 1 | a9q7 |
| survey_timing | CSEC3i.NSDstat | 1 | c3iq46a |
| weights_and_design | CSEC1.NSDstat | 8 | End_health_accountability;GPS_Manual_Health;Health_Visit;Number_Satellites_Health;Reason_Comm_Org_Not_Done;Reason_Edu_Not_Done;Reason_Health_Not_Done;Reason_Road_Inf_Not_Done |
| weights_and_design | GSEC1.NSDstat | 2 | reason;year |

Guardrail: these candidates are not raw value verification. Do not promote
this wave until the original raw package confirms values, labels, units,
recall periods, missing codes, skip patterns, merge keys, survey design,
timing/geography, and accepted climate linkage.
