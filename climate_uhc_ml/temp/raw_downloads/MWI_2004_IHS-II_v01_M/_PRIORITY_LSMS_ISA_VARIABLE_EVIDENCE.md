# Priority LSMS-ISA Variable Evidence

Dataset: MWI_2004_IHS-II_v01_M - Malawi 2004-2005

Status: official public metadata candidate variables only.

## Requirement Coverage

| Requirement | Candidate variables | Strong candidates | Candidate files | Status |
|---|---:|---:|---:|---|
| household_person_keys | 12 | 12 | 12 | official_metadata_strong_candidates_present_raw_review_required |
| weights_and_design | 12 | 12 | 12 | official_metadata_strong_candidates_present_raw_review_required |
| consumption_or_income | 12 | 12 | 3 | official_metadata_strong_candidates_present_raw_review_required |
| oop_health_expenditure | 12 | 5 | 1 | official_metadata_strong_candidates_present_raw_review_required |
| health_need_and_access | 12 | 8 | 2 | official_metadata_strong_candidates_present_raw_review_required |
| survey_timing | 12 | 4 | 7 | official_metadata_strong_candidates_present_raw_review_required |
| climate_geography | 12 | 12 | 12 | official_metadata_strong_candidates_present_raw_review_required |
| missing_codes_units_recall_skip_patterns | 0 | 0 | 0 | documentation_and_raw_review_required_no_variable_shortlist |

## File Shortlist

| Requirement | File | Candidate variables | Top variable names |
|---|---|---:|---|
| climate_geography | sec_a.NSDstat | 1 | type |
| climate_geography | sec_f.NSDstat | 1 | type |
| climate_geography | sec_g.NSDstat | 1 | type |
| climate_geography | sec_h.NSDstat | 1 | type |
| climate_geography | sec_i.NSDstat | 1 | type |
| climate_geography | sec_j1.NSDstat | 1 | type |
| climate_geography | sec_j2.NSDstat | 1 | type |
| climate_geography | sec_k.NSDstat | 1 | type |
| consumption_or_income | sec_j1.NSDstat | 10 | add;case_id;dist;ea;hhid;hhsize;hhwght;j01a;j02a;j03a |
| consumption_or_income | sec_i.NSDstat | 1 | i03both |
| consumption_or_income | sec_aa.NSDstat | 1 | aa01 |
| health_need_and_access | sec_d.NSDstat | 7 | d05a;d05aoth;d05b;d05both;d27a;d27b;d04 |
| health_need_and_access | mod_d.NSDstat | 5 | cd51b;cd_51a;cd47;cd57a;cd_50 |
| household_person_keys | sec_b.NSDstat | 1 | hhid |
| household_person_keys | sec_a.NSDstat | 1 | hhid |
| household_person_keys | sec_f.NSDstat | 1 | hhid |
| household_person_keys | sec_g.NSDstat | 1 | hhid |
| household_person_keys | sec_h.NSDstat | 1 | hhid |
| household_person_keys | sec_i.NSDstat | 1 | hhid |
| household_person_keys | sec_j1.NSDstat | 1 | hhid |
| household_person_keys | sec_j2.NSDstat | 1 | hhid |
| oop_health_expenditure | sec_d.NSDstat | 12 | d13;d12;d14;d16;d19;add;case_id;d02;d03;d04;d05a;d05aoth |
| survey_timing | sec_z1.NSDstat | 4 | z08a;z08b;z10a;z10b |
| survey_timing | ihs2_household.NSDstat | 1 | idate |
| survey_timing | sec_c.NSDstat | 2 | c14;c16 |
| survey_timing | sec_v.NSDstat | 2 | v09a;v09b |
| survey_timing | ihs2_individ.NSDstat | 1 | age_months |
| survey_timing | sec_a.NSDstat | 1 | a14b |
| survey_timing | sec_q1.NSDstat | 1 | q03 |
| weights_and_design | sec_a.NSDstat | 1 | psu |

Guardrail: these candidates are not raw value verification. Do not promote
this wave until the original raw package confirms values, labels, units,
recall periods, missing codes, skip patterns, merge keys, survey design,
timing/geography, and accepted climate linkage.
