# Country-Wave Promotion Packet: Nepal 2010-2011

Dataset: `Living Standards Survey 2010-2011, Third Round`

IDNO: `NPL_2010_LSS-III_v01_M`

Official URL: https://microdata.worldbank.org/catalog/1000/get-microdata

Local target folder: `temp/raw_downloads/NPL_2010_LSS-III_v01_M/`

Current registry status: `not_promoted`

## Gate Summary

| Gate | Status | Evidence | Required action |
|---|---|---|---|
| complete_original_raw_package | fail | intake_status=instructions_or_documentation_only; tabular=0; archives=0; docs=1 | Place complete original raw archive/tabular package and documentation in the local target folder. |
| raw_value_unit_recall_missing_verification | fail | raw_not_inspected=106 | Inspect raw labels/values, merge keys, units, recall periods, skip patterns, and missing codes. |
| financial_protection_che10_che25 | fail | climate_geography:raw_not_inspected; household_id:raw_not_inspected; oop_health_expenditure:raw_not_inspected; survey_timing:raw_not_inspected; survey_weight:raw_not_inspected; total_consumption_or_income:raw_not_inspected | Verify total consumption/income, OOP health expenditure, weights, timing, geography, and merge keys. |
| access_forgone_care | fail | care_or_barrier:raw_not_inspected; health_need:raw_not_inspected | Verify illness/need denominator, care seeking, and cost/distance/supply barrier semantics. |
| climate_linkage | fail | survey_timing:raw_not_inspected; climate_geography:raw_not_inspected | Verify survey month/date, usable admin/GPS/cluster geography, and accepted CHIRPS/ERA5 extraction route. |
| double_failure | fail | financial_ready=0; access_ready=0 | Pass both financial-protection and access/forgone-care value verification gates. |

## Expected Files or Modules

- `FINAL_PREF`: not_present; concepts=admin1_or_admin2;age;agriculture_livelihood;asset_index_or_asset_variable;education;food_consumption;household_head_marker;household_size;household_weight_or_person_weight;interview_date_or_survey_month;nonfood_consumption;psu_or_cluster_id;rural;sex;strata;total_consumption_or_income
- `S00`: not_present; concepts=admin1_or_admin2;agriculture_livelihood;care_not_sought_reason;coping_borrowed;household_head_marker;psu_or_cluster_id;rural;sex;strata
- `S08`: not_present; concepts=care_not_sought_reason;care_sought;illness_or_injury_need;oop_health_expenditure;reason_not_sought_distance;strata
- `S13A1`: not_present; concepts=admin1_or_admin2;agriculture_livelihood;strata
- `anthro`: not_present; concepts=age;household_weight_or_person_weight;psu_or_cluster_id;sex;strata
- `S21`: not_present; concepts=admin1_or_admin2;household_size;interview_date_or_survey_month;psu_or_cluster_id;strata
- `S19`: not_present; concepts=agriculture_livelihood;asset_index_or_asset_variable;care_sought;coping_borrowed;coping_sold_assets;education;food_consumption;strata;total_consumption_or_income
- `sample`: not_present; concepts=admin1_or_admin2;household_size;household_weight_or_person_weight;psu_or_cluster_id;rural;strata
- `S16`: not_present; concepts=admin1_or_admin2;age;education;rural;sex;strata
- `S20`: not_present; concepts=age;household_weight_or_person_weight;strata
- `S01`: not_present; concepts=admin1_or_admin2;age;rural;sex;strata
- `S04`: not_present; concepts=admin1_or_admin2;rural;strata

## Raw Variable Verification Queue

- `S08` / `v08_14`: care_or_barrier; raw_not_inspected; action=inspect raw values, labels, merge keys, units, recall period, and missing codes before harmonization
- `S08` / `v08_15`: care_or_barrier; raw_not_inspected; action=inspect raw values, labels, merge keys, units, recall period, and missing codes before harmonization
- `S08` / `v08_17a`: care_or_barrier; raw_not_inspected; action=inspect raw values, labels, merge keys, units, recall period, and missing codes before harmonization
- `S08` / `v08_17b`: care_or_barrier; raw_not_inspected; action=inspect raw values, labels, merge keys, units, recall period, and missing codes before harmonization
- `S08` / `v08_17c`: care_or_barrier; raw_not_inspected; action=inspect raw values, labels, merge keys, units, recall period, and missing codes before harmonization
- `S08` / `v08_23`: care_or_barrier; raw_not_inspected; action=inspect raw values, labels, merge keys, units, recall period, and missing codes before harmonization
- `S19` / `v19_09`: care_or_barrier; raw_not_inspected; action=inspect raw values, labels, merge keys, units, recall period, and missing codes before harmonization
- `FINAL_PREF;sample` / `district`: climate_geography; raw_not_inspected; action=inspect raw values, labels, merge keys, units, recall period, and missing codes before harmonization
- `FINAL_PREF;sample` / `region`: climate_geography; raw_not_inspected; action=inspect raw values, labels, merge keys, units, recall period, and missing codes before harmonization
- `S00` / `v00_dist`: climate_geography; raw_not_inspected; action=inspect raw values, labels, merge keys, units, recall period, and missing codes before harmonization
- `S01` / `v01_05a`: climate_geography; raw_not_inspected; action=inspect raw values, labels, merge keys, units, recall period, and missing codes before harmonization
- `S04` / `v04_03a`: climate_geography; raw_not_inspected; action=inspect raw values, labels, merge keys, units, recall period, and missing codes before harmonization
- `S04` / `v04_11a`: climate_geography; raw_not_inspected; action=inspect raw values, labels, merge keys, units, recall period, and missing codes before harmonization
- `S13A1` / `v13_05`: climate_geography; raw_not_inspected; action=inspect raw values, labels, merge keys, units, recall period, and missing codes before harmonization
- `S16` / `v16_08a`: climate_geography; raw_not_inspected; action=inspect raw values, labels, merge keys, units, recall period, and missing codes before harmonization
- `S17A` / `v17_07a`: climate_geography; raw_not_inspected; action=inspect raw values, labels, merge keys, units, recall period, and missing codes before harmonization

## Promotion Rule

Do not write this country-wave into `data/` until the raw package is complete,
merge keys and survey design are verified, financial-protection and access
variables pass value/unit/recall/missing-code checks, and a CHIRPS or ERA5
climate-linkage route is accepted.
