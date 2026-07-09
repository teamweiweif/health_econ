# Priority LSMS-ISA Variable Evidence

Dataset: TZA_2008_NPS-R1_v03_M - Tanzania 2008-2009

Status: official public metadata candidate variables only.

## Requirement Coverage

| Requirement | Candidate variables | Strong candidates | Candidate files | Status |
|---|---:|---:|---:|---|
| household_person_keys | 12 | 12 | 11 | official_metadata_strong_candidates_present_raw_review_required |
| weights_and_design | 12 | 12 | 7 | official_metadata_strong_candidates_present_raw_review_required |
| consumption_or_income | 12 | 12 | 3 | official_metadata_strong_candidates_present_raw_review_required |
| oop_health_expenditure | 12 | 12 | 2 | official_metadata_strong_candidates_present_raw_review_required |
| health_need_and_access | 12 | 0 | 2 | official_metadata_weak_candidates_present_raw_review_required |
| survey_timing | 12 | 3 | 5 | official_metadata_strong_candidates_present_raw_review_required |
| climate_geography | 12 | 12 | 9 | official_metadata_strong_candidates_present_raw_review_required |
| missing_codes_units_recall_skip_patterns | 0 | 0 | 0 | documentation_and_raw_review_required_no_variable_shortlist |

## File Shortlist

| Requirement | File | Candidate variables | Top variable names |
|---|---|---:|---|
| climate_geography | HH.Geovariables_Y1 | 3 | ea_id;lat_modified;lon_modified |
| climate_geography | SEC_A_T_English_Labels | 2 | clusterid;ea |
| climate_geography | SEC_A_T_Swahili_Labels | 1 | ea |
| climate_geography | SECTA1A2_Swahili_Labels | 1 | ea_id |
| climate_geography | SECTCB_Swahili_Labels | 1 | ea_id |
| climate_geography | SECTCEFG | 1 | ea_id |
| climate_geography | SECTCH | 1 | ea_id |
| climate_geography | SECTCI | 1 | ea_id |
| consumption_or_income | TZY1.HH.Consumption | 4 | hhexpenses;hhexpensesR;expm;expmR |
| consumption_or_income | SEC_L_Swahili_Labels | 4 | hhid;slcode;slq1;slq2 |
| consumption_or_income | SEC_M_Swahili_Labels | 4 | hhid;smcode;smq1;smq2 |
| health_need_and_access | SEC_B_C_D_E1_F_G1_U_English_Labels | 11 | sdq22;sdq4;sdq43_1;sdq43_2;sdq43_3;sdq55_1;sdq55_2;sdq55_3;sdq6;sdq8;sdq9 |
| health_need_and_access | SEC_I_English_Labels | 1 | siq8b |
| household_person_keys | Agriculture SEC_1_ALL_Swahili_Labels | 2 | hhid;rosterid |
| household_person_keys | SEC_B_C_D_E1_F_G1_U_Swahili_Labels | 1 | hhid |
| household_person_keys | SEC_2A_Swahili_Labels | 1 | hhid |
| household_person_keys | SEC_2B_Swahili_Labels | 1 | hhid |
| household_person_keys | SEC_B_C_D_E1_F_G1_U_English_Labels | 1 | hhid |
| household_person_keys | SEC_2A_English_Labels | 1 | hhid |
| household_person_keys | SEC_2B_English_Labels | 1 | hhid |
| household_person_keys | SEC_A_T_Swahili_Labels | 1 | hhid |
| oop_health_expenditure | SEC_B_C_D_E1_F_G1_U_English_Labels | 11 | scq14_fee;scq14_food;sdq6;sdq7;scq14_bks;scq14_contr;scq14_tot;scq14_trans;scq14_tui;scq14_unif;sdq5 |
| oop_health_expenditure | SEC_B_C_D_E1_F_G1_U_Swahili_Labels | 1 | scq14_fee |
| survey_timing | SEC_A_T_Swahili_Labels | 4 | endmin;sa2q17endhr;sa2q17starthr;sa2q17startmins |
| survey_timing | SEC_A_T_English_Labels | 3 | endmin;sa2q17endhr;sa2q17starthr |
| survey_timing | SECTA1A2_English_Labels | 2 | ca07m;ca07y |
| survey_timing | SEC_R_Swahili_Labels | 2 | srq5month;srq5year |
| survey_timing | TZY1.HH.Consumption | 1 | intmonth |
| weights_and_design | SEC_A_T_English_Labels | 4 | hh_weight;hh_weight_trimmed;ea;strataid |
| weights_and_design | nps_weights_oct2010 | 3 | hh_weight;hh_weight_trimmed;strataid |

Guardrail: these candidates are not raw value verification. Do not promote
this wave until the original raw package confirms values, labels, units,
recall periods, missing codes, skip patterns, merge keys, survey design,
timing/geography, and accepted climate linkage.
