# Priority LSMS-ISA Variable Evidence

Dataset: JAM_1997_SLC_v01_M - Jamaica 1997

Status: official public metadata candidate variables only.

## Requirement Coverage

| Requirement | Candidate variables | Strong candidates | Candidate files | Status |
|---|---:|---:|---:|---|
| household_person_keys | 12 | 4 | 2 | official_metadata_strong_candidates_present_raw_review_required |
| weights_and_design | 12 | 1 | 10 | official_metadata_strong_candidates_present_raw_review_required |
| consumption_or_income | 12 | 12 | 5 | official_metadata_strong_candidates_present_raw_review_required |
| oop_health_expenditure | 11 | 10 | 2 | official_metadata_strong_candidates_present_raw_review_required |
| health_need_and_access | 12 | 7 | 3 | official_metadata_strong_candidates_present_raw_review_required |
| survey_timing | 12 | 4 | 5 | official_metadata_strong_candidates_present_raw_review_required |
| climate_geography | 12 | 1 | 7 | official_metadata_strong_candidates_present_raw_review_required |
| missing_codes_units_recall_skip_patterns | 0 | 0 | 0 | documentation_and_raw_review_required_no_variable_shortlist |

## File Shortlist

| Requirement | File | Candidate variables | Top variable names |
|---|---|---:|---|
| climate_geography | REC001.NSDstat | 4 | area;district;parish;region |
| climate_geography | HEADS.NSDstat | 2 | district;parish |
| climate_geography | HHSIZE.NSDstat | 2 | district;parish |
| climate_geography | EXP97.NSDstat | 1 | Cluster |
| climate_geography | REC034.NSDstat | 1 | xearn |
| climate_geography | REC041.NSDstat | 1 | year |
| climate_geography | ANNUAL.NSDstat | 1 | district |
| consumption_or_income | TOTGIFTS.NSDstat | 4 | t_gfood;serial;tcgift;totgift |
| consumption_or_income | FOOD.NSDstat | 3 | consgift;giftfood;hpfood |
| consumption_or_income | MEALS.NSDstat | 3 | consgift;giftfood;hpfood |
| consumption_or_income | ANNUAL.NSDstat | 1 | non_food |
| consumption_or_income | TOTFOOD.NSDstat | 1 | t_food |
| health_need_and_access | REC003.NSDstat | 7 | a09;a10;a17;a13;a16;a181;a182 |
| health_need_and_access | REC002.NSDstat | 4 | a03;a04;a05;a06 |
| health_need_and_access | REC004.NSDstat | 1 | a25 |
| household_person_keys | REC047.NSDstat | 10 | ind;member;age;assist;disabled;hhm1;indiv;marital;part_id;partner |
| household_person_keys | HEADS.NSDstat | 2 | ind;member |
| oop_health_expenditure | REC003.NSDstat | 10 | a19;a20;a09;a10;a11;a12;a13;a14;a15;a16 |
| oop_health_expenditure | REC033.NSDstat | 1 | m05b |
| survey_timing | REC001.NSDstat | 3 | int_date;ant_date;visits |
| survey_timing | LABORF.NSDstat | 6 | Q415;Q43;Q46m;Q46y;Q54m;Q54y |
| survey_timing | REC035.NSDstat | 1 | times |
| survey_timing | REC045.NSDstat | 1 | amtdue |
| survey_timing | REC041.NSDstat | 1 | year |
| weights_and_design | NUTR97.NSDstat | 1 | weight |
| weights_and_design | EXP97.NSDstat | 2 | Areatype;Cluster |
| weights_and_design | LABORF.NSDstat | 2 | Q46y;Q54y |
| weights_and_design | REC001.NSDstat | 1 | area |
| weights_and_design | REC034.NSDstat | 1 | xearn |
| weights_and_design | REC041.NSDstat | 1 | year |

Guardrail: these candidates are not raw value verification. Do not promote
this wave until the original raw package confirms values, labels, units,
recall periods, missing codes, skip patterns, merge keys, survey design,
timing/geography, and accepted climate linkage.
