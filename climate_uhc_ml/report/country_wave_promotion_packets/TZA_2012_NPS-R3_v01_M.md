# Country-Wave Promotion Packet: Tanzania 2012-2013

Dataset: `National Panel Survey 2012-2013, Wave 3`

IDNO: `TZA_2012_NPS-R3_v01_M`

Official URL: https://microdata.worldbank.org/catalog/2252/get-microdata

Local target folder: `temp/raw_downloads/TZA_2012_NPS-R3_v01_M/`

Current registry status: `not_promoted`

## Gate Summary

| Gate | Status | Evidence | Required action |
|---|---|---|---|
| complete_original_raw_package | fail | intake_status=instructions_or_documentation_only; tabular=0; archives=0; docs=1 | Place complete original raw archive/tabular package and documentation in the local target folder. |
| raw_value_unit_recall_missing_verification | fail | raw_not_inspected=115 | Inspect raw labels/values, merge keys, units, recall periods, skip patterns, and missing codes. |
| financial_protection_che10_che25 | fail | climate_geography:raw_not_inspected; household_id:raw_not_inspected; oop_health_expenditure:raw_not_inspected; survey_timing:raw_not_inspected; survey_weight:raw_not_inspected; total_consumption_or_income:raw_not_inspected | Verify total consumption/income, OOP health expenditure, weights, timing, geography, and merge keys. |
| access_forgone_care | fail | care_or_barrier:raw_not_inspected; health_need:raw_not_inspected | Verify illness/need denominator, care seeking, and cost/distance/supply barrier semantics. |
| climate_linkage | fail | survey_timing:raw_not_inspected; climate_geography:raw_not_inspected | Verify survey month/date, usable admin/GPS/cluster geography, and accepted CHIRPS/ERA5 extraction route. |
| double_failure | fail | financial_ready=0; access_ready=0 | Pass both financial-protection and access/forgone-care value verification gates. |

## Expected Files or Modules

- `AG_SEC_3A`: not_present; concepts=agriculture_livelihood;care_not_sought_reason;coping_borrowed;hhid;reason_not_sought_distance;shock_module_variable;total_consumption_or_income
- `AG_SEC_3B`: not_present; concepts=agriculture_livelihood;care_not_sought_reason;coping_borrowed;hhid;reason_not_sought_distance;shock_module_variable;total_consumption_or_income
- `HouseholdGeovars_Y3`: not_present; concepts=admin1_or_admin2;agriculture_livelihood;latitude_or_longitude;reason_not_sought_distance;shock_module_variable
- `AG_SEC_5A`: not_present; concepts=agriculture_livelihood;hhid;reason_not_sought_distance;shock_module_variable
- `AG_SEC_5B`: not_present; concepts=agriculture_livelihood;hhid;reason_not_sought_distance;shock_module_variable
- `COM_SEC_CE`: not_present; concepts=admin1_or_admin2;agriculture_livelihood;psu_or_cluster_id;reason_not_sought_distance;sex;shock_module_variable
- `AG_SEC_4A`: not_present; concepts=agriculture_livelihood;hhid;shock_module_variable
- `AG_SEC_4B`: not_present; concepts=agriculture_livelihood;hhid;shock_module_variable
- `COM_SEC_CF_ID`: not_present; concepts=admin1_or_admin2;latitude_or_longitude;psu_or_cluster_id
- `HH_SEC_A`: not_present; concepts=admin1_or_admin2;hhid;household_head_marker;household_weight_or_person_weight;interview_date_or_survey_month;psu_or_cluster_id;rural;strata
- `HH_SEC_C`: not_present; concepts=age;education;hhid;pid;reason_not_sought_distance
- `AG_SEC_2A`: not_present; concepts=agriculture_livelihood;hhid;latitude_or_longitude;shock_module_variable

## Raw Variable Verification Queue

- `HH_SEC_D` / `hh_d04_1`: care_or_barrier; raw_not_inspected; action=inspect raw values, labels, merge keys, units, recall period, and missing codes before harmonization
- `HH_SEC_D` / `hh_d04_2`: care_or_barrier; raw_not_inspected; action=inspect raw values, labels, merge keys, units, recall period, and missing codes before harmonization
- `HH_SEC_D` / `hh_d33`: care_or_barrier; raw_not_inspected; action=inspect raw values, labels, merge keys, units, recall period, and missing codes before harmonization
- `HH_SEC_D` / `hh_d34_1`: care_or_barrier; raw_not_inspected; action=inspect raw values, labels, merge keys, units, recall period, and missing codes before harmonization
- `HH_SEC_D` / `hh_d34_2`: care_or_barrier; raw_not_inspected; action=inspect raw values, labels, merge keys, units, recall period, and missing codes before harmonization
- `HH_SEC_D` / `hh_d34_3`: care_or_barrier; raw_not_inspected; action=inspect raw values, labels, merge keys, units, recall period, and missing codes before harmonization
- `LF_SEC_03` / `lf03_07`: care_or_barrier; raw_not_inspected; action=inspect raw values, labels, merge keys, units, recall period, and missing codes before harmonization
- `LF_SEC_03` / `lf03_11`: care_or_barrier; raw_not_inspected; action=inspect raw values, labels, merge keys, units, recall period, and missing codes before harmonization
- `LF_SEC_03` / `lf03_13`: care_or_barrier; raw_not_inspected; action=inspect raw values, labels, merge keys, units, recall period, and missing codes before harmonization
- `LF_SEC_03` / `lf03_12`: care_or_barrier; raw_not_inspected; action=inspect raw values, labels, merge keys, units, recall period, and missing codes before harmonization
- `LF_SEC_03` / `lf03_14`: care_or_barrier; raw_not_inspected; action=inspect raw values, labels, merge keys, units, recall period, and missing codes before harmonization
- `AG_SEC_2A` / `ag2a_06_1`: climate_geography; raw_not_inspected; action=inspect raw values, labels, merge keys, units, recall period, and missing codes before harmonization
- `AG_SEC_2A` / `ag2a_06_2`: climate_geography; raw_not_inspected; action=inspect raw values, labels, merge keys, units, recall period, and missing codes before harmonization
- `AG_SEC_2A` / `ag2a_06_3`: climate_geography; raw_not_inspected; action=inspect raw values, labels, merge keys, units, recall period, and missing codes before harmonization
- `AG_SEC_2A` / `ag2a_06_4`: climate_geography; raw_not_inspected; action=inspect raw values, labels, merge keys, units, recall period, and missing codes before harmonization
- `AG_SEC_2A` / `ag2a_09`: climate_geography; raw_not_inspected; action=inspect raw values, labels, merge keys, units, recall period, and missing codes before harmonization

## Promotion Rule

Do not write this country-wave into `data/` until the raw package is complete,
merge keys and survey design are verified, financial-protection and access
variables pass value/unit/recall/missing-code checks, and a CHIRPS or ERA5
climate-linkage route is accepted.
