# Country-Wave Promotion Packet: Jamaica 1997

Dataset: `Survey of Living Conditions 1997`

IDNO: `JAM_1997_SLC_v01_M`

Official URL: https://microdata.worldbank.org/catalog/2368/get-microdata

Local target folder: `temp/raw_downloads/JAM_1997_SLC_v01_M/`

Current registry status: `not_promoted`

## Gate Summary

| Gate | Status | Evidence | Required action |
|---|---|---|---|
| complete_original_raw_package | fail | intake_status=instructions_or_documentation_only; tabular=0; archives=0; docs=1 | Place complete original raw archive/tabular package and documentation in the local target folder. |
| raw_value_unit_recall_missing_verification | fail | raw_not_inspected=66 | Inspect raw labels/values, merge keys, units, recall periods, skip patterns, and missing codes. |
| financial_protection_che10_che25 | fail | climate_geography:raw_not_inspected; household_id:raw_not_inspected; oop_health_expenditure:raw_not_inspected; survey_timing:raw_not_inspected; survey_weight:raw_not_inspected; total_consumption_or_income:raw_not_inspected | Verify total consumption/income, OOP health expenditure, weights, timing, geography, and merge keys. |
| access_forgone_care | fail | care_or_barrier:raw_not_inspected; health_need:raw_not_inspected | Verify illness/need denominator, care seeking, and cost/distance/supply barrier semantics. |
| climate_linkage | fail | survey_timing:raw_not_inspected; climate_geography:raw_not_inspected | Verify survey month/date, usable admin/GPS/cluster geography, and accepted CHIRPS/ERA5 extraction route. |
| double_failure | fail | financial_ready=0; access_ready=0 | Pass both financial-protection and access/forgone-care value verification gates. |

## Expected Files or Modules

- `LABORF`: not_present; concepts=admin1_or_admin2;age;asset_index_or_asset_variable;care_not_sought_reason;education;pid;sex;shock_module_variable
- `REC003`: not_present; concepts=care_sought;health_insurance;illness_or_injury_need;oop_health_expenditure
- `ANNUAL`: not_present; concepts=admin1_or_admin2;asset_index_or_asset_variable;food_consumption;household_size;household_weight_or_person_weight;nonfood_consumption;total_consumption_or_income
- `EDTOTALS`: not_present; concepts=admin1_or_admin2;asset_index_or_asset_variable;food_consumption;household_weight_or_person_weight;nonfood_consumption;sex
- `HHSIZE`: not_present; concepts=admin1_or_admin2;age;asset_index_or_asset_variable;household_size;sex
- `NUTR97`: not_present; concepts=age;household_weight_or_person_weight;sex
- `REC001`: not_present; concepts=admin1_or_admin2;asset_index_or_asset_variable;household_weight_or_person_weight;interview_date_or_survey_month
- `HEADS`: not_present; concepts=admin1_or_admin2;age;household_head_marker;pid;sex
- `REC007`: not_present; concepts=age;household_weight_or_person_weight
- `EXP97`: not_present; concepts=admin1_or_admin2;food_consumption;psu_or_cluster_id
- `REC006`: not_present; concepts=admin1_or_admin2;reason_not_sought_distance
- `REC025`: not_present; concepts=nonfood_consumption

## Raw Variable Verification Queue

- `REC003` / `a09`: care_or_barrier; raw_not_inspected; action=inspect raw values, labels, merge keys, units, recall period, and missing codes before harmonization
- `REC003` / `a10`: care_or_barrier; raw_not_inspected; action=inspect raw values, labels, merge keys, units, recall period, and missing codes before harmonization
- `REC004` / `a25`: care_or_barrier; raw_not_inspected; action=inspect raw values, labels, merge keys, units, recall period, and missing codes before harmonization
- `ANNUAL;EDTOTALS;HEADS;HHSIZE;REC001` / `district`: climate_geography; raw_not_inspected; action=inspect raw values, labels, merge keys, units, recall period, and missing codes before harmonization
- `EDTOTALS;REC001` / `region`: climate_geography; raw_not_inspected; action=inspect raw values, labels, merge keys, units, recall period, and missing codes before harmonization
- `EXP97` / `Edsize`: climate_geography; raw_not_inspected; action=inspect raw values, labels, merge keys, units, recall period, and missing codes before harmonization
- `LABORF` / `Enumdis`: climate_geography; raw_not_inspected; action=inspect raw values, labels, merge keys, units, recall period, and missing codes before harmonization
- `ANNUAL;HHSIZE` / `hhsize1`: demographics; raw_not_inspected; action=inspect raw values, labels, merge keys, units, recall period, and missing codes before harmonization
- `ANNUAL;HHSIZE` / `hhsize2`: demographics; raw_not_inspected; action=inspect raw values, labels, merge keys, units, recall period, and missing codes before harmonization
- `EDTOTALS` / `edfem`: demographics; raw_not_inspected; action=inspect raw values, labels, merge keys, units, recall period, and missing codes before harmonization
- `EDTOTALS` / `edmale`: demographics; raw_not_inspected; action=inspect raw values, labels, merge keys, units, recall period, and missing codes before harmonization
- `HEADS;REC047` / `age`: demographics; raw_not_inspected; action=inspect raw values, labels, merge keys, units, recall period, and missing codes before harmonization
- `HEADS;REC047` / `relation`: demographics; raw_not_inspected; action=inspect raw values, labels, merge keys, units, recall period, and missing codes before harmonization
- `HEADS;NUTR97;REC047` / `sex`: demographics; raw_not_inspected; action=inspect raw values, labels, merge keys, units, recall period, and missing codes before harmonization
- `HHSIZE` / `adfem`: demographics; raw_not_inspected; action=inspect raw values, labels, merge keys, units, recall period, and missing codes before harmonization
- `HHSIZE` / `admale`: demographics; raw_not_inspected; action=inspect raw values, labels, merge keys, units, recall period, and missing codes before harmonization

## Promotion Rule

Do not write this country-wave into `data/` until the raw package is complete,
merge keys and survey design are verified, financial-protection and access
variables pass value/unit/recall/missing-code checks, and a CHIRPS or ERA5
climate-linkage route is accepted.
