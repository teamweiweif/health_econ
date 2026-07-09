# Priority LSMS-ISA Variable Evidence

Dataset: KGZ_1993_KMPS_v01_M - Kyrgyz Republic 1993

Status: official public metadata candidate variables only.

## Requirement Coverage

| Requirement | Candidate variables | Strong candidates | Candidate files | Status |
|---|---:|---:|---:|---|
| household_person_keys | 12 | 12 | 7 | official_metadata_strong_candidates_present_raw_review_required |
| weights_and_design | 12 | 1 | 2 | official_metadata_strong_candidates_present_raw_review_required |
| consumption_or_income | 12 | 4 | 3 | official_metadata_strong_candidates_present_raw_review_required |
| oop_health_expenditure | 12 | 4 | 4 | official_metadata_strong_candidates_present_raw_review_required |
| health_need_and_access | 12 | 0 | 4 | official_metadata_weak_candidates_present_raw_review_required |
| survey_timing | 12 | 8 | 6 | official_metadata_strong_candidates_present_raw_review_required |
| climate_geography | 12 | 1 | 5 | official_metadata_strong_candidates_present_raw_review_required |
| missing_codes_units_recall_skip_patterns | 0 | 0 | 0 | documentation_and_raw_review_required_no_variable_shortlist |

## File Shortlist

| Requirement | File | Candidate variables | Top variable names |
|---|---|---:|---|
| climate_geography | KPRICE2 | 5 | aye1_12a;aye1_12b;aye1_12c;aye1_12d;aye1_12e |
| climate_geography | KHHLD | 4 | ae2_1a;ae2_1b;ae3_1a;ae3_1b |
| climate_geography | KPRICE3 | 1 | ayeaid |
| climate_geography | CORE | 1 | region |
| climate_geography | CONADULT | 1 | hhead |
| consumption_or_income | INCEXP | 9 | khomcx;khomcy;kfoodx;khousex;kotherx;kothery;kothousx;kselfemy;ktothhy |
| consumption_or_income | KHHLD | 2 | ad141_1d;ad141_2d |
| consumption_or_income | KADULT | 1 | a1o16 |
| health_need_and_access | KYGPOV | 8 | hcsblne;lcsblne;poor3e;poor4e;rhcsblne;rlcsblne;rpoor3e;rpoor4e |
| health_need_and_access | KADULT | 2 | a1l16;a1j98 |
| health_need_and_access | INCEXP | 1 | khealthx |
| health_need_and_access | KCHILD | 1 | a1l16 |
| household_person_keys | KINDIVH | 4 | hid;pid;ab10_9_1;ab10_9_2 |
| household_person_keys | KADIET | 2 | pid;hhid |
| household_person_keys | KCHDIET | 2 | pid;hhid |
| household_person_keys | KINDIV | 1 | pid |
| household_person_keys | CONADULT | 1 | pid |
| household_person_keys | KADULT | 1 | pid |
| household_person_keys | KCHILD | 1 | pid |
| oop_health_expenditure | KHHLD | 3 | ae15_1b;ae20_6a;ae20_6b |
| oop_health_expenditure | KADULT | 4 | a1l14;a1l15;a1l16;a1l9 |
| oop_health_expenditure | KCHILD | 4 | a1l14;a1l15;a1l16;a1l9 |
| oop_health_expenditure | INCEXP | 1 | khealthx |
| survey_timing | KADULT | 5 | a1o10;a1o14;a1o16;a1o18;a1h7_2 |
| survey_timing | KCHILD | 3 | a1o10;a1o14;a1h7_2 |
| survey_timing | CORE | 1 | month |
| survey_timing | KHHLD | 1 | aa4_2 |
| survey_timing | CONADULT | 1 | gender |
| survey_timing | INCEXP | 1 | ktothhx |
| weights_and_design | KPRICE3 | 11 | ayeaid;ayea_10a;ayea_10b;ayea_10c;ayea_10d;ayea_10e;ayea_11a;ayea_11b;ayea_11c;ayea_11d;ayea_11e |

Guardrail: these candidates are not raw value verification. Do not promote
this wave until the original raw package confirms values, labels, units,
recall periods, missing codes, skip patterns, merge keys, survey design,
timing/geography, and accepted climate linkage.
