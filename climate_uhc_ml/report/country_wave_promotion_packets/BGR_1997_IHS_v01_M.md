# Country-Wave Promotion Packet: Bulgaria 1997

Dataset: `Integrated Household Survey 1997`

IDNO: `BGR_1997_IHS_v01_M`

Official URL: https://microdata.worldbank.org/catalog/2272/get-microdata

Local target folder: `temp/raw_downloads/BGR_1997_IHS_v01_M/`

Current registry status: `not_promoted`

## Gate Summary

| Gate | Status | Evidence | Required action |
|---|---|---|---|
| complete_original_raw_package | fail | intake_status=instructions_or_documentation_only; tabular=0; archives=0; docs=1 | Place complete original raw archive/tabular package and documentation in the local target folder. |
| raw_value_unit_recall_missing_verification | fail | raw_not_inspected=62 | Inspect raw labels/values, merge keys, units, recall periods, skip patterns, and missing codes. |
| financial_protection_che10_che25 | fail | climate_geography:raw_not_inspected; household_id:raw_not_inspected; oop_health_expenditure:raw_not_inspected; survey_timing:raw_not_inspected; survey_weight:raw_not_inspected; total_consumption_or_income:raw_not_inspected | Verify total consumption/income, OOP health expenditure, weights, timing, geography, and merge keys. |
| access_forgone_care | fail | care_or_barrier:raw_not_inspected; health_need:raw_not_inspected | Verify illness/need denominator, care seeking, and cost/distance/supply barrier semantics. |
| climate_linkage | fail | survey_timing:raw_not_inspected; climate_geography:raw_not_inspected | Verify survey month/date, usable admin/GPS/cluster geography, and accepted CHIRPS/ERA5 extraction route. |
| double_failure | fail | financial_ready=0; access_ready=0 | Pass both financial-protection and access/forgone-care value verification gates. |

## Expected Files or Modules

- `FILE52V0`: not_present; concepts=care_sought;hhid;illness_or_injury_need;oop_health_expenditure;reason_not_sought_distance
- `HHINCTL`: not_present; concepts=admin1_or_admin2;agriculture_livelihood;asset_index_or_asset_variable;hhid;reason_not_sought_distance;total_consumption_or_income
- `FILE10V0`: not_present; concepts=asset_index_or_asset_variable;hhid;reason_not_sought_distance;shock_module_variable
- `FILE32V0`: not_present; concepts=agriculture_livelihood;hhid
- `FILE31V0`: not_present; concepts=agriculture_livelihood;coping_borrowed;hhid;shock_module_variable
- `HHEXPTL`: not_present; concepts=asset_index_or_asset_variable;education;food_consumption;hhid;reason_not_sought_distance;shock_module_variable
- `FILE08V0`: not_present; concepts=age;asset_index_or_asset_variable;hhid
- `FILE04V0`: not_present; concepts=admin1_or_admin2;education;hhid;shock_module_variable
- `FILE09V0`: not_present; concepts=admin1_or_admin2;asset_index_or_asset_variable;hhid;shock_module_variable
- `HHEXPTLD`: not_present; concepts=asset_index_or_asset_variable;education;food_consumption;hhid;reason_not_sought_distance;shock_module_variable
- `HHEXPTLS`: not_present; concepts=asset_index_or_asset_variable;education;food_consumption;hhid;reason_not_sought_distance;shock_module_variable
- `FILE01V1`: not_present; concepts=admin1_or_admin2;hhid;interview_date_or_survey_month;psu_or_cluster_id;sex

## Raw Variable Verification Queue

- `FILE52V0` / `d_consul`: care_or_barrier; raw_not_inspected; action=inspect raw values, labels, merge keys, units, recall period, and missing codes before harmonization
- `FILE52V0` / `d_trans`: care_or_barrier; raw_not_inspected; action=inspect raw values, labels, merge keys, units, recall period, and missing codes before harmonization
- `FILE52V0` / `d_treat`: care_or_barrier; raw_not_inspected; action=inspect raw values, labels, merge keys, units, recall period, and missing codes before harmonization
- `FILE52V0` / `mc_treat`: care_or_barrier; raw_not_inspected; action=inspect raw values, labels, merge keys, units, recall period, and missing codes before harmonization
- `FILE52V0` / `min_trav`: care_or_barrier; raw_not_inspected; action=inspect raw values, labels, merge keys, units, recall period, and missing codes before harmonization
- `FILE52V0` / `place_co`: care_or_barrier; raw_not_inspected; action=inspect raw values, labels, merge keys, units, recall period, and missing codes before harmonization
- `FILE52V0` / `q_consul`: care_or_barrier; raw_not_inspected; action=inspect raw values, labels, merge keys, units, recall period, and missing codes before harmonization
- `FILE52V0` / `reason`: care_or_barrier; raw_not_inspected; action=inspect raw values, labels, merge keys, units, recall period, and missing codes before harmonization
- `FILE52V0` / `reason_c`: care_or_barrier; raw_not_inspected; action=inspect raw values, labels, merge keys, units, recall period, and missing codes before harmonization
- `FILE52V0` / `transp`: care_or_barrier; raw_not_inspected; action=inspect raw values, labels, merge keys, units, recall period, and missing codes before harmonization
- `FILE52V0` / `treatm`: care_or_barrier; raw_not_inspected; action=inspect raw values, labels, merge keys, units, recall period, and missing codes before harmonization
- `ADJUSTR;FILE01V1;STRATA` / `region`: climate_geography; raw_not_inspected; action=inspect raw values, labels, merge keys, units, recall period, and missing codes before harmonization
- `FILE01V1` / `distr`: climate_geography; raw_not_inspected; action=inspect raw values, labels, merge keys, units, recall period, and missing codes before harmonization
- `FILE09V0` / `hrs_heat`: climate_geography; raw_not_inspected; action=inspect raw values, labels, merge keys, units, recall period, and missing codes before harmonization
- `FILE01V1;FILE02V1;FILE35V1;FILE36V0;INDINCTL` / `gender`: demographics; raw_not_inspected; action=inspect raw values, labels, merge keys, units, recall period, and missing codes before harmonization
- `FILE02V1` / `age_mth`: demographics; raw_not_inspected; action=inspect raw values, labels, merge keys, units, recall period, and missing codes before harmonization

## Promotion Rule

Do not write this country-wave into `data/` until the raw package is complete,
merge keys and survey design are verified, financial-protection and access
variables pass value/unit/recall/missing-code checks, and a CHIRPS or ERA5
climate-linkage route is accepted.
