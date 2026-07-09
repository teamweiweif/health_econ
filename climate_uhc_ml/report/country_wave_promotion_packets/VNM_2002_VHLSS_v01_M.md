# Country-Wave Promotion Packet: Viet Nam 2002

Dataset: `Household Living Standards Survey 2002`

IDNO: `VNM_2002_VHLSS_v01_M`

Official URL: https://microdata.worldbank.org/catalog/2306/get-microdata

Local target folder: `temp/raw_downloads/VNM_2002_VHLSS_v01_M/`

Current registry status: `not_promoted`

## Gate Summary

| Gate | Status | Evidence | Required action |
|---|---|---|---|
| complete_original_raw_package | fail | intake_status=instructions_or_documentation_only; tabular=0; archives=0; docs=1 | Place complete original raw archive/tabular package and documentation in the local target folder. |
| raw_value_unit_recall_missing_verification | fail | raw_not_inspected=108 | Inspect raw labels/values, merge keys, units, recall periods, skip patterns, and missing codes. |
| financial_protection_che10_che25 | fail | climate_geography:raw_not_inspected; household_id:raw_not_inspected; oop_health_expenditure:raw_not_inspected; survey_timing:raw_not_inspected; survey_weight:raw_not_inspected; total_consumption_or_income:raw_not_inspected | Verify total consumption/income, OOP health expenditure, weights, timing, geography, and merge keys. |
| access_forgone_care | fail | care_or_barrier:raw_not_inspected; health_need:raw_not_inspected | Verify illness/need denominator, care seeking, and cost/distance/supply barrier semantics. |
| climate_linkage | fail | survey_timing:raw_not_inspected; climate_geography:raw_not_inspected | Verify survey month/date, usable admin/GPS/cluster geography, and accepted CHIRPS/ERA5 extraction route. |
| double_failure | fail | financial_ready=0; access_ready=0 | Pass both financial-protection and access/forgone-care value verification gates. |

## Expected Files or Modules

- `k000`: not_present; concepts=admin1_or_admin2;age;agriculture_livelihood;coping_borrowed;education;oop_health_expenditure;sex;shock_module_variable
- `h000`: not_present; concepts=admin1_or_admin2;asset_index_or_asset_variable;care_not_sought_reason;education;illness_or_injury_need;oop_health_expenditure;reason_not_sought_distance;shock_module_variable
- `d000`: not_present; concepts=admin1_or_admin2;age;education;sex
- `muc8`: not_present; concepts=admin1_or_admin2;asset_index_or_asset_variable;coping_borrowed;household_head_marker
- `muc5b4`: not_present; concepts=admin1_or_admin2;agriculture_livelihood;asset_index_or_asset_variable;care_sought;coping_borrowed;oop_health_expenditure;total_consumption_or_income
- `muc5b32`: not_present; concepts=admin1_or_admin2;agriculture_livelihood;asset_index_or_asset_variable;coping_borrowed;oop_health_expenditure
- `hhexpe02`: not_present; concepts=admin1_or_admin2;asset_index_or_asset_variable;education;food_consumption;household_size;nonfood_consumption;psu_or_cluster_id;rural
- `muc9`: not_present; concepts=admin1_or_admin2;agriculture_livelihood;coping_borrowed;health_insurance;household_head_marker;illness_or_injury_need
- `muc5b5`: not_present; concepts=admin1_or_admin2;agriculture_livelihood;asset_index_or_asset_variable;coping_borrowed;total_consumption_or_income
- `muc5b1`: not_present; concepts=admin1_or_admin2;agriculture_livelihood;coping_borrowed
- `muc5b61`: not_present; concepts=admin1_or_admin2;agriculture_livelihood;total_consumption_or_income
- `muc5b2ho`: not_present; concepts=admin1_or_admin2;agriculture_livelihood;household_head_marker;shock_module_variable;total_consumption_or_income

## Raw Variable Verification Queue

- `muc4` / `m4c3_1`: care_or_barrier; raw_not_inspected; action=inspect raw values, labels, merge keys, units, recall period, and missing codes before harmonization
- `muc4` / `m4c3_2`: care_or_barrier; raw_not_inspected; action=inspect raw values, labels, merge keys, units, recall period, and missing codes before harmonization
- `muc4;muc4ho` / `m4c5`: care_or_barrier; raw_not_inspected; action=inspect raw values, labels, merge keys, units, recall period, and missing codes before harmonization
- `muc4;muc4ho` / `m4c6`: care_or_barrier; raw_not_inspected; action=inspect raw values, labels, merge keys, units, recall period, and missing codes before harmonization
- `muc4ho` / `m4c7`: care_or_barrier; raw_not_inspected; action=inspect raw values, labels, merge keys, units, recall period, and missing codes before harmonization
- `muc5b4` / `m5b41c2t4`: care_or_barrier; raw_not_inspected; action=inspect raw values, labels, merge keys, units, recall period, and missing codes before harmonization
- `muc5b4` / `m5b41c3t4`: care_or_barrier; raw_not_inspected; action=inspect raw values, labels, merge keys, units, recall period, and missing codes before harmonization
- `muc5b4` / `m5b41c4t4`: care_or_barrier; raw_not_inspected; action=inspect raw values, labels, merge keys, units, recall period, and missing codes before harmonization
- `muc5b4` / `m5b41c5t4`: care_or_barrier; raw_not_inspected; action=inspect raw values, labels, merge keys, units, recall period, and missing codes before harmonization
- `muc5b4` / `m5b42c10t4`: care_or_barrier; raw_not_inspected; action=inspect raw values, labels, merge keys, units, recall period, and missing codes before harmonization
- `muc5b4` / `m5b42c13t4`: care_or_barrier; raw_not_inspected; action=inspect raw values, labels, merge keys, units, recall period, and missing codes before harmonization
- `muc5b4` / `m5b42c14t4`: care_or_barrier; raw_not_inspected; action=inspect raw values, labels, merge keys, units, recall period, and missing codes before harmonization
- `muc5b4` / `m5b42c15t4`: care_or_barrier; raw_not_inspected; action=inspect raw values, labels, merge keys, units, recall period, and missing codes before harmonization
- `muc5b4` / `m5b42c16t4`: care_or_barrier; raw_not_inspected; action=inspect raw values, labels, merge keys, units, recall period, and missing codes before harmonization
- `muc5b4` / `m5b42c17t4`: care_or_barrier; raw_not_inspected; action=inspect raw values, labels, merge keys, units, recall period, and missing codes before harmonization
- `muc5b4` / `m5b42c6t4`: care_or_barrier; raw_not_inspected; action=inspect raw values, labels, merge keys, units, recall period, and missing codes before harmonization

## Promotion Rule

Do not write this country-wave into `data/` until the raw package is complete,
merge keys and survey design are verified, financial-protection and access
variables pass value/unit/recall/missing-code checks, and a CHIRPS or ERA5
climate-linkage route is accepted.
