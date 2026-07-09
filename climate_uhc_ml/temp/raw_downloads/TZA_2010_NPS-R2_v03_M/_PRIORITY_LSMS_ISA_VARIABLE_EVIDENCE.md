# Priority LSMS-ISA Variable Evidence

Dataset: TZA_2010_NPS-R2_v03_M - Tanzania 2010-2011

Status: official public metadata candidate variables only.

## Requirement Coverage

| Requirement | Candidate variables | Strong candidates | Candidate files | Status |
|---|---:|---:|---:|---|
| household_person_keys | 12 | 12 | 11 | official_metadata_strong_candidates_present_raw_review_required |
| weights_and_design | 12 | 12 | 11 | official_metadata_strong_candidates_present_raw_review_required |
| consumption_or_income | 12 | 12 | 3 | official_metadata_strong_candidates_present_raw_review_required |
| oop_health_expenditure | 8 | 8 | 1 | official_metadata_strong_candidates_present_raw_review_required |
| health_need_and_access | 12 | 2 | 6 | official_metadata_strong_candidates_present_raw_review_required |
| survey_timing | 12 | 4 | 6 | official_metadata_strong_candidates_present_raw_review_required |
| climate_geography | 12 | 12 | 6 | official_metadata_strong_candidates_present_raw_review_required |
| missing_codes_units_recall_skip_patterns | 0 | 0 | 0 | documentation_and_raw_review_required_no_variable_shortlist |

## File Shortlist

| Requirement | File | Candidate variables | Top variable names |
|---|---|---:|---|
| climate_geography | HH_SEC_A | 6 | clusterid;district;ea;hh_a18_year;region;ward |
| climate_geography | TZY2.EA.Offsets | 2 | clusterid;rum |
| climate_geography | Plot.Geovariables_Y2 | 1 | ea_id |
| climate_geography | TZY1.HH.Consumption | 1 | urban |
| climate_geography | TZY2.HH.Consumption | 1 | urban |
| climate_geography | HH.Geovariables_Y2 | 1 | ea_id |
| consumption_or_income | TZY1.HH.Consumption | 4 | hhexpenses;hhexpensesR;expm;expmR |
| consumption_or_income | TZY2.HH.Consumption | 4 | hhexpenses;hhexpensesR;expm;expmR |
| consumption_or_income | HH_SEC_L | 4 | hh_l01_2;hh_l02;itemcode;y2_hhid |
| health_need_and_access | HH_SEC_D | 5 | hh_d12_1;hh_d12_2;hh_d02;hh_d13;hh_d38 |
| health_need_and_access | FS_H2 | 2 | costid;costitem |
| health_need_and_access | TZY1.HH.Consumption | 2 | health;healthR |
| health_need_and_access | FS_N2 | 1 | costid |
| health_need_and_access | HH_SEC_G | 1 | hh_g03_5 |
| health_need_and_access | TZY2.HH.Consumption | 1 | health |
| household_person_keys | HH_SEC_B | 2 | hhid_2008;y2_hhid |
| household_person_keys | AG_SEC10B | 1 | y2_hhid |
| household_person_keys | AG_SEC7A | 1 | y2_hhid |
| household_person_keys | AG_SEC7B | 1 | y2_hhid |
| household_person_keys | TZY2.HH.Consumption | 1 | hhid_2008 |
| household_person_keys | FS_J1 | 1 | hhid_2008 |
| household_person_keys | FS_J3 | 1 | hhid_2008 |
| household_person_keys | FS_C1 | 1 | y2_hhid |
| oop_health_expenditure | HH_SEC_D | 8 | hh_d05_1;hh_d05_2;hh_d07;hh_d08;hh_d09;hh_d13;hh_d15;hh_d29_1 |
| survey_timing | HH_SEC_C | 3 | hh_c08;hh_c10;hh_c30 |
| survey_timing | HH_SEC_E1 | 3 | hh_e44;hh_e67;hh_e68 |
| survey_timing | HH_SEC_A | 2 | hh_a18_month;hh_a18_year |
| survey_timing | HH_SEC_D | 2 | hh_d05_1;hh_d05_2 |
| survey_timing | TZY1.HH.Consumption | 1 | intmonth |
| survey_timing | TZY2.HH.Consumption | 1 | intmonth |

Guardrail: these candidates are not raw value verification. Do not promote
this wave until the original raw package confirms values, labels, units,
recall periods, missing codes, skip patterns, merge keys, survey design,
timing/geography, and accepted climate linkage.
