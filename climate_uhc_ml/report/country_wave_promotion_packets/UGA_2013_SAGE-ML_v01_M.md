# Country-Wave Promotion Packet: Uganda 2013

Dataset: `Social Assistance Grants for Empowerment Programme 2013, Evaluation Follow-Up Survey`

IDNO: `UGA_2013_SAGE-ML_v01_M`

Official URL: https://microdata.worldbank.org/catalog/2653/get-microdata

Local target folder: `temp/raw_downloads/UGA_2013_SAGE-ML_v01_M/`

Current registry status: `not_promoted`

## Gate Summary

| Gate | Status | Evidence | Required action |
|---|---|---|---|
| complete_original_raw_package | fail | intake_status=instructions_or_documentation_only; tabular=0; archives=0; docs=1 | Place complete original raw archive/tabular package and documentation in the local target folder. |
| raw_value_unit_recall_missing_verification | fail | raw_not_inspected=103 | Inspect raw labels/values, merge keys, units, recall periods, skip patterns, and missing codes. |
| financial_protection_che10_che25 | fail | climate_geography:raw_not_inspected; household_id:raw_not_inspected; oop_health_expenditure:raw_not_inspected; survey_timing:raw_not_inspected; survey_weight:raw_not_inspected; total_consumption_or_income:raw_not_inspected | Verify total consumption/income, OOP health expenditure, weights, timing, geography, and merge keys. |
| access_forgone_care | fail | care_or_barrier:raw_not_inspected; health_need:raw_not_inspected | Verify illness/need denominator, care seeking, and cost/distance/supply barrier semantics. |
| climate_linkage | fail | survey_timing:raw_not_inspected; climate_geography:raw_not_inspected | Verify survey month/date, usable admin/GPS/cluster geography, and accepted CHIRPS/ERA5 extraction route. |
| double_failure | fail | financial_ready=0; access_ready=0 | Pass both financial-protection and access/forgone-care value verification gates. |

## Expected Files or Modules

- `int_welfare_hh`: not_present; concepts=admin1_or_admin2;agriculture_livelihood;asset_index_or_asset_variable;care_not_sought_reason;care_sought;coping_borrowed;coping_sold_assets;education;hhid;household_weight_or_person_weight;illness_or_injury_need;interview_date_or_survey_month;oop_health_expenditure;reason_not_sought_distance;sex;shock_module_variable
- `int_access_fin`: not_present; concepts=admin1_or_admin2;agriculture_livelihood;asset_index_or_asset_variable;care_not_sought_reason;care_sought;coping_borrowed;education;hhid;household_weight_or_person_weight;interview_date_or_survey_month;oop_health_expenditure;reason_not_sought_distance;sex
- `int_operational`: not_present; concepts=admin1_or_admin2;agriculture_livelihood;asset_index_or_asset_variable;care_not_sought_reason;care_sought;coping_borrowed;education;hhid;household_weight_or_person_weight;oop_health_expenditure;reason_not_sought_cost;reason_not_sought_distance;reason_not_sought_supply;shock_module_variable
- `int_access_health`: not_present; concepts=admin1_or_admin2;age;care_sought;education;hhid;household_weight_or_person_weight;illness_or_injury_need;oop_health_expenditure;pid;reason_not_sought_cost;reason_not_sought_distance;reason_not_sought_supply;sex
- `int_cohesion`: not_present; concepts=admin1_or_admin2;asset_index_or_asset_variable;care_not_sought_reason;care_sought;coping_borrowed;hhid;household_weight_or_person_weight;interview_date_or_survey_month;reason_not_sought_distance;sex
- `int_access_educ18plus`: not_present; concepts=admin1_or_admin2;age;agriculture_livelihood;care_sought;education;hhid;household_weight_or_person_weight;illness_or_injury_need;oop_health_expenditure;pid;reason_not_sought_distance;sex
- `int_demographics_mem`: not_present; concepts=admin1_or_admin2;age;care_sought;education;hhid;household_head_marker;household_size;household_weight_or_person_weight;illness_or_injury_need;oop_health_expenditure;pid;reason_not_sought_distance;sex
- `int_access_school`: not_present; concepts=admin1_or_admin2;age;agriculture_livelihood;care_sought;education;hhid;household_weight_or_person_weight;illness_or_injury_need;oop_health_expenditure;pid;reason_not_sought_distance;sex
- `int_consexp`: not_present; concepts=admin1_or_admin2;asset_index_or_asset_variable;care_sought;education;food_consumption;hhid;household_size;household_weight_or_person_weight;nonfood_consumption;oop_health_expenditure;rural;total_consumption_or_income
- `sage_labourintermed`: not_present; concepts=admin1_or_admin2;age;agriculture_livelihood;care_sought;education;hhid;household_weight_or_person_weight;illness_or_injury_need;pid;reason_not_sought_distance;sex
- `int_community`: not_present; concepts=admin1_or_admin2;agriculture_livelihood;care_sought;reason_not_sought_distance;sex
- `int_migration`: not_present; concepts=admin1_or_admin2;age;care_sought;education;hhid;household_weight_or_person_weight;sex;shock_module_variable

## Raw Variable Verification Queue

- `int_access_educ18plus;int_access_fin;int_access_health;int_access_health_hh;int_access_school;int_asset_index;int_ben_characteristics;int_cohesion;int_cohesion_dec1;int_cohesion_dec2;int_cohesion_dec3;int_cohesion_empow;int_consexp;int_demographics_hh;int_demographics_mem;int_migration;int_migration_HH;int_operational;int_tracking;int_treatment_status` / `aeligibility`: care_or_barrier; raw_not_inspected; action=inspect raw values, labels, merge keys, units, recall period, and missing codes before harmonization
- `int_access_educ18plus;int_access_fin;int_access_health;int_access_health_hh;int_access_school;int_asset_index;int_ben_characteristics;int_cohesion;int_cohesion_dec1;int_cohesion_dec2;int_cohesion_dec3;int_cohesion_empow;int_consexp;int_demographics_hh;int_demographics_mem;int_migration;int_migration_HH;int_operational;int_tracking;int_treatment_status` / `eligilitystatus`: care_or_barrier; raw_not_inspected; action=inspect raw values, labels, merge keys, units, recall period, and missing codes before harmonization
- `int_access_educ18plus;int_access_health;int_access_school;int_demographics_mem;int_welfare_memdata` / `hh3_q8`: care_or_barrier; raw_not_inspected; action=inspect raw values, labels, merge keys, units, recall period, and missing codes before harmonization
- `int_access_fin;int_cohesion;int_operational;int_welfare_hh` / `hh15_q18`: care_or_barrier; raw_not_inspected; action=inspect raw values, labels, merge keys, units, recall period, and missing codes before harmonization
- `int_access_fin;int_cohesion;int_operational;int_welfare_hh` / `hh15_q53`: care_or_barrier; raw_not_inspected; action=inspect raw values, labels, merge keys, units, recall period, and missing codes before harmonization
- `int_community;int_facilities2` / `dist_fac_govt_healthunit`: care_or_barrier; raw_not_inspected; action=inspect raw values, labels, merge keys, units, recall period, and missing codes before harmonization
- `int_community;int_facilities2` / `dist_fac_govt_hospital`: care_or_barrier; raw_not_inspected; action=inspect raw values, labels, merge keys, units, recall period, and missing codes before harmonization
- `int_community;int_facilities2` / `dist_fac_private_clinic`: care_or_barrier; raw_not_inspected; action=inspect raw values, labels, merge keys, units, recall period, and missing codes before harmonization
- `int_community` / `treatment`: care_or_barrier; raw_not_inspected; action=inspect raw values, labels, merge keys, units, recall period, and missing codes before harmonization
- `int_operational` / `V173`: care_or_barrier; raw_not_inspected; action=inspect raw values, labels, merge keys, units, recall period, and missing codes before harmonization
- `int_treatment_status` / `aelitab2`: care_or_barrier; raw_not_inspected; action=inspect raw values, labels, merge keys, units, recall period, and missing codes before harmonization
- `int_access_health` / `reason_noconsultation_1`: care_or_barrier; raw_not_inspected; action=inspect raw values, labels, merge keys, units, recall period, and missing codes before harmonization
- `int_access_health` / `reason_noconsultation_13`: care_or_barrier; raw_not_inspected; action=inspect raw values, labels, merge keys, units, recall period, and missing codes before harmonization
- `int_access_health` / `reason_noconsultation_2`: care_or_barrier; raw_not_inspected; action=inspect raw values, labels, merge keys, units, recall period, and missing codes before harmonization
- `SAGE_HHWEIGHTSV2;int_access_educ18plus;int_access_fin;int_access_health;int_access_health_hh;int_access_school;int_asset_index;int_ben_characteristics;int_cohesion;int_cohesion_dec1;int_cohesion_dec2;int_cohesion_dec3;int_cohesion_empow;int_consexp;int_demographics_hh;int_demographics_mem;int_migration;int_migration_HH;int_operational;int_welfare_hh` / `county`: climate_geography; raw_not_inspected; action=inspect raw values, labels, merge keys, units, recall period, and missing codes before harmonization
- `SAGE_HHWEIGHTSV2;districts2010_SCG;districts2010_VFSG;districts_SCG;districts_VFSG;int_access_educ18plus;int_access_fin;int_access_health;int_access_health_hh;int_access_school;int_asset_index;int_ben_characteristics;int_cohesion;int_cohesion_dec1;int_cohesion_dec2;int_cohesion_dec3;int_cohesion_empow;int_consexp;int_demographics_hh;int_demographics_mem` / `district`: climate_geography; raw_not_inspected; action=inspect raw values, labels, merge keys, units, recall period, and missing codes before harmonization

## Promotion Rule

Do not write this country-wave into `data/` until the raw package is complete,
merge keys and survey design are verified, financial-protection and access
variables pass value/unit/recall/missing-code checks, and a CHIRPS or ERA5
climate-linkage route is accepted.
