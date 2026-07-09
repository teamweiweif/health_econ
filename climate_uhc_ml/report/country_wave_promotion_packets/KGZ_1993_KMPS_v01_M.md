# Country-Wave Promotion Packet: Kyrgyz Republic 1993

Dataset: `Multipurpose Poverty Survey 1993`

IDNO: `KGZ_1993_KMPS_v01_M`

Official URL: https://microdata.worldbank.org/catalog/280/get-microdata

Local target folder: `temp/raw_downloads/KGZ_1993_KMPS_v01_M/`

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

- `KPRICE2`: not_present; concepts=admin1_or_admin2;shock_module_variable
- `KHHLD`: not_present; concepts=admin1_or_admin2;agriculture_livelihood;asset_index_or_asset_variable;coping_borrowed;hhid;illness_or_injury_need;interview_date_or_survey_month;oop_health_expenditure;reason_not_sought_distance;shock_module_variable
- `KPRICE3`: not_present; concepts=admin1_or_admin2;shock_module_variable
- `KADULT`: not_present; concepts=admin1_or_admin2;age;agriculture_livelihood;asset_index_or_asset_variable;care_not_sought_reason;care_sought;coping_borrowed;education;hhid;household_weight_or_person_weight;illness_or_injury_need;interview_date_or_survey_month;nonfood_consumption;oop_health_expenditure;pid;reason_not_sought_distance;sex;shock_module_variable
- `KCOMM`: not_present; concepts=admin1_or_admin2;reason_not_sought_distance;reason_not_sought_supply;sex;shock_module_variable
- `KCHILD`: not_present; concepts=age;agriculture_livelihood;care_sought;education;hhid;household_weight_or_person_weight;illness_or_injury_need;interview_date_or_survey_month;oop_health_expenditure;pid;reason_not_sought_distance;sex
- `KINDIVH`: not_present; concepts=hhid;pid;sex
- `INCEXP`: not_present; concepts=admin1_or_admin2;agriculture_livelihood;asset_index_or_asset_variable;education;hhid;household_size;reason_not_sought_distance;shock_module_variable;total_consumption_or_income
- `KYGPOV`: not_present; concepts=admin1_or_admin2;hhid
- `CONADULT`: not_present; concepts=age;education;hhid;household_head_marker;pid;sex
- `KINDIV`: not_present; concepts=age;hhid;pid;sex
- `CORE`: not_present; concepts=admin1_or_admin2;hhid;interview_date_or_survey_month

## Raw Variable Verification Queue

- `KADULT;KCHILD` / `a1l15`: care_or_barrier; raw_not_inspected; action=inspect raw values, labels, merge keys, units, recall period, and missing codes before harmonization
- `KADULT;KCHILD` / `a1l16`: care_or_barrier; raw_not_inspected; action=inspect raw values, labels, merge keys, units, recall period, and missing codes before harmonization
- `KADULT;KCHILD` / `a1l21`: care_or_barrier; raw_not_inspected; action=inspect raw values, labels, merge keys, units, recall period, and missing codes before harmonization
- `CORE` / `region`: climate_geography; raw_not_inspected; action=inspect raw values, labels, merge keys, units, recall period, and missing codes before harmonization
- `KCOMM` / `a1x3`: climate_geography; raw_not_inspected; action=inspect raw values, labels, merge keys, units, recall period, and missing codes before harmonization
- `KCOMM` / `a1xc3`: climate_geography; raw_not_inspected; action=inspect raw values, labels, merge keys, units, recall period, and missing codes before harmonization
- `CONADULT;KINDIV` / `age`: demographics; raw_not_inspected; action=inspect raw values, labels, merge keys, units, recall period, and missing codes before harmonization
- `CONADULT` / `edlevel`: demographics; raw_not_inspected; action=inspect raw values, labels, merge keys, units, recall period, and missing codes before harmonization
- `CONADULT` / `gender`: demographics; raw_not_inspected; action=inspect raw values, labels, merge keys, units, recall period, and missing codes before harmonization
- `CONADULT` / `hhead`: demographics; raw_not_inspected; action=inspect raw values, labels, merge keys, units, recall period, and missing codes before harmonization
- `INCEXP` / `keduculx`: demographics; raw_not_inspected; action=inspect raw values, labels, merge keys, units, recall period, and missing codes before harmonization
- `INCEXP` / `khhsize`: demographics; raw_not_inspected; action=inspect raw values, labels, merge keys, units, recall period, and missing codes before harmonization
- `KADULT;KCHILD` / `a1h5`: demographics; raw_not_inspected; action=inspect raw values, labels, merge keys, units, recall period, and missing codes before harmonization
- `KADULT;KCHILD` / `a1i18`: demographics; raw_not_inspected; action=inspect raw values, labels, merge keys, units, recall period, and missing codes before harmonization
- `KADULT;KCHILD` / `a1i21`: demographics; raw_not_inspected; action=inspect raw values, labels, merge keys, units, recall period, and missing codes before harmonization
- `KADULT` / `a1m55`: demographics; raw_not_inspected; action=inspect raw values, labels, merge keys, units, recall period, and missing codes before harmonization

## Promotion Rule

Do not write this country-wave into `data/` until the raw package is complete,
merge keys and survey design are verified, financial-protection and access
variables pass value/unit/recall/missing-code checks, and a CHIRPS or ERA5
climate-linkage route is accepted.
