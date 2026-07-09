# Country-Wave Promotion Packet: Uganda 2012

Dataset: `Social Assistance Grants for Empowerment Programme 2012, Evaluation Baseline Survey`

IDNO: `UGA_2012_SAGE-BL_v01_M`

Official URL: https://microdata.worldbank.org/catalog/2652/get-microdata

Local target folder: `temp/raw_downloads/UGA_2012_SAGE-BL_v01_M/`

Current registry status: `not_promoted`

## Gate Summary

| Gate | Status | Evidence | Required action |
|---|---|---|---|
| complete_original_raw_package | fail | intake_status=instructions_or_documentation_only; tabular=0; archives=0; docs=1 | Place complete original raw archive/tabular package and documentation in the local target folder. |
| raw_value_unit_recall_missing_verification | fail | raw_not_inspected=105 | Inspect raw labels/values, merge keys, units, recall periods, skip patterns, and missing codes. |
| financial_protection_che10_che25 | fail | climate_geography:raw_not_inspected; household_id:raw_not_inspected; oop_health_expenditure:raw_not_inspected; survey_timing:raw_not_inspected; survey_weight:raw_not_inspected; total_consumption_or_income:raw_not_inspected | Verify total consumption/income, OOP health expenditure, weights, timing, geography, and merge keys. |
| access_forgone_care | fail | care_or_barrier:raw_not_inspected; health_need:raw_not_inspected | Verify illness/need denominator, care seeking, and cost/distance/supply barrier semantics. |
| climate_linkage | fail | survey_timing:raw_not_inspected; climate_geography:raw_not_inspected | Verify survey month/date, usable admin/GPS/cluster geography, and accepted CHIRPS/ERA5 extraction route. |
| double_failure | fail | financial_ready=0; access_ready=0 | Pass both financial-protection and access/forgone-care value verification gates. |

## Expected Files or Modules

- `int_welfare_hh`: not_present; concepts=admin1_or_admin2;agriculture_livelihood;asset_index_or_asset_variable;care_sought;coping_borrowed;coping_sold_assets;education;hhid;household_weight_or_person_weight;illness_or_injury_need;interview_date_or_survey_month;oop_health_expenditure;reason_not_sought_distance;sex;shock_module_variable
- `int_consexp`: not_present; concepts=admin1_or_admin2;agriculture_livelihood;asset_index_or_asset_variable;care_sought;coping_borrowed;education;food_consumption;hhid;household_size;household_weight_or_person_weight;interview_date_or_survey_month;nonfood_consumption;oop_health_expenditure;reason_not_sought_distance;rural;sex;shock_module_variable;total_consumption_or_income
- `int_access_fin`: not_present; concepts=admin1_or_admin2;agriculture_livelihood;asset_index_or_asset_variable;care_sought;coping_borrowed;education;hhid;household_weight_or_person_weight;interview_date_or_survey_month;oop_health_expenditure;sex
- `int_access_health`: not_present; concepts=admin1_or_admin2;age;care_not_sought_reason;care_sought;education;hhid;household_weight_or_person_weight;illness_or_injury_need;interview_date_or_survey_month;oop_health_expenditure;pid;reason_not_sought_cost;reason_not_sought_distance;reason_not_sought_supply;sex
- `int_access_educ18plus`: not_present; concepts=admin1_or_admin2;age;agriculture_livelihood;care_sought;education;hhid;household_weight_or_person_weight;illness_or_injury_need;interview_date_or_survey_month;oop_health_expenditure;pid;reason_not_sought_distance;sex
- `int_demographics_mem`: not_present; concepts=admin1_or_admin2;age;care_sought;education;hhid;household_head_marker;household_size;household_weight_or_person_weight;illness_or_injury_need;interview_date_or_survey_month;oop_health_expenditure;pid;sex
- `int_access_school`: not_present; concepts=admin1_or_admin2;age;agriculture_livelihood;care_sought;education;hhid;household_weight_or_person_weight;illness_or_injury_need;interview_date_or_survey_month;oop_health_expenditure;pid;reason_not_sought_distance;sex
- `int_cohesion`: not_present; concepts=admin1_or_admin2;agriculture_livelihood;asset_index_or_asset_variable;care_sought;coping_borrowed;hhid;household_weight_or_person_weight;interview_date_or_survey_month;sex
- `sage_labourintermed`: not_present; concepts=admin1_or_admin2;age;agriculture_livelihood;care_sought;education;hhid;household_weight_or_person_weight;illness_or_injury_need;interview_date_or_survey_month;pid;reason_not_sought_distance;sex
- `int_welfare_memdata`: not_present; concepts=admin1_or_admin2;age;care_sought;education;hhid;household_weight_or_person_weight;illness_or_injury_need;interview_date_or_survey_month;oop_health_expenditure;pid;sex
- `int_migration`: not_present; concepts=admin1_or_admin2;age;care_sought;education;hhid;household_weight_or_person_weight;pid;sex;shock_module_variable
- `int_demographics_hh`: not_present; concepts=admin1_or_admin2;age;care_sought;education;hhid;household_head_marker;household_size;household_weight_or_person_weight;sex

## Raw Variable Verification Queue

- `int_access_educ18plus;int_access_fin;int_access_health;int_access_health_hh;int_access_school;int_cohesion;int_cohesion_dec1;int_cohesion_dec2;int_cohesion_dec3;int_cohesion_empow;int_demographics_hh;int_demographics_mem;int_migration;int_migration_HH;int_welfare_hh;int_welfare_hhassets_productive;int_welfare_hhlivestock;int_welfare_memdata;sage_fcsexpanded;sage_foodsecintermed` / `aeligibility`: care_or_barrier; raw_not_inspected; action=inspect raw values, labels, merge keys, units, recall period, and missing codes before harmonization
- `int_access_educ18plus;int_access_fin;int_access_health;int_access_health_hh;int_access_school;int_cohesion;int_cohesion_dec1;int_cohesion_dec2;int_cohesion_dec3;int_cohesion_empow;int_demographics_hh;int_demographics_mem;int_migration;int_migration_HH;int_welfare_hh;int_welfare_hhassets_productive;int_welfare_hhlivestock;int_welfare_memdata;sage_fcsexpanded;sage_foodsecintermed` / `eligilitystatus`: care_or_barrier; raw_not_inspected; action=inspect raw values, labels, merge keys, units, recall period, and missing codes before harmonization
- `int_access_educ18plus;int_access_health;int_access_school;int_demographics_mem;int_welfare_memdata` / `hh3_q7`: care_or_barrier; raw_not_inspected; action=inspect raw values, labels, merge keys, units, recall period, and missing codes before harmonization
- `int_access_educ18plus;int_access_health;int_access_school;int_demographics_mem;int_welfare_memdata` / `hh3_q8`: care_or_barrier; raw_not_inspected; action=inspect raw values, labels, merge keys, units, recall period, and missing codes before harmonization
- `int_access_fin;int_cohesion;int_consexp;int_welfare_hh` / `hh15_q28`: care_or_barrier; raw_not_inspected; action=inspect raw values, labels, merge keys, units, recall period, and missing codes before harmonization
- `int_access_fin;int_cohesion;int_consexp;int_welfare_hh` / `hh15_q6`: care_or_barrier; raw_not_inspected; action=inspect raw values, labels, merge keys, units, recall period, and missing codes before harmonization
- `int_access_health` / `consult_distance_km`: care_or_barrier; raw_not_inspected; action=inspect raw values, labels, merge keys, units, recall period, and missing codes before harmonization
- `int_access_health` / `consult_distance_min`: care_or_barrier; raw_not_inspected; action=inspect raw values, labels, merge keys, units, recall period, and missing codes before harmonization
- `int_access_health` / `cost_consultation`: care_or_barrier; raw_not_inspected; action=inspect raw values, labels, merge keys, units, recall period, and missing codes before harmonization
- `int_access_educ18plus;int_access_health;int_access_school;int_demographics_mem;int_welfare_memdata` / `hh3_q5`: care_or_barrier; raw_not_inspected; action=inspect raw values, labels, merge keys, units, recall period, and missing codes before harmonization
- `int_access_educ18plus;int_access_health;int_access_school;int_demographics_mem;int_welfare_memdata` / `hh3_q5oth`: care_or_barrier; raw_not_inspected; action=inspect raw values, labels, merge keys, units, recall period, and missing codes before harmonization
- `int_access_educ18plus;int_access_health;int_access_school;int_demographics_mem;int_welfare_memdata` / `hh3_q5other`: care_or_barrier; raw_not_inspected; action=inspect raw values, labels, merge keys, units, recall period, and missing codes before harmonization
- `int_access_educ18plus;int_access_health;int_access_school;int_demographics_mem;int_welfare_memdata` / `hh3_q6a`: care_or_barrier; raw_not_inspected; action=inspect raw values, labels, merge keys, units, recall period, and missing codes before harmonization
- `int_access_educ18plus;int_access_health;int_access_school;int_demographics_mem;int_welfare_memdata` / `hh3_q6b`: care_or_barrier; raw_not_inspected; action=inspect raw values, labels, merge keys, units, recall period, and missing codes before harmonization
- `int_access_health` / `reason_noconsultation_10`: care_or_barrier; raw_not_inspected; action=inspect raw values, labels, merge keys, units, recall period, and missing codes before harmonization
- `int_access_health` / `reason_noconsultation_11`: care_or_barrier; raw_not_inspected; action=inspect raw values, labels, merge keys, units, recall period, and missing codes before harmonization

## Promotion Rule

Do not write this country-wave into `data/` until the raw package is complete,
merge keys and survey design are verified, financial-protection and access
variables pass value/unit/recall/missing-code checks, and a CHIRPS or ERA5
climate-linkage route is accepted.
