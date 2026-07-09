# Country-Wave Promotion Packet: Nigeria 2011-2016

Dataset: `Youth Enterprise With Innovation in Nigeria (YouWiN!) Program Impact Evaluation 2011-2016`

IDNO: `NGA_2011-2016_YouWiNIE_v02_M`

Official URL: https://microdata.worldbank.org/catalog/2329/get-microdata

Local target folder: `temp/raw_downloads/NGA_2011-2016_YouWiNIE_v02_M/`

Current registry status: `not_promoted`

## Gate Summary

| Gate | Status | Evidence | Required action |
|---|---|---|---|
| complete_original_raw_package | fail | intake_status=instructions_or_documentation_only; tabular=0; archives=0; docs=1 | Place complete original raw archive/tabular package and documentation in the local target folder. |
| raw_value_unit_recall_missing_verification | fail | raw_not_inspected=70 | Inspect raw labels/values, merge keys, units, recall periods, skip patterns, and missing codes. |
| financial_protection_che10_che25 | fail | climate_geography:raw_not_inspected; household_id:raw_not_inspected; oop_health_expenditure:raw_not_inspected; survey_timing:raw_not_inspected; survey_weight:raw_not_inspected; total_consumption_or_income:raw_not_inspected | Verify total consumption/income, OOP health expenditure, weights, timing, geography, and merge keys. |
| access_forgone_care | fail | care_or_barrier:raw_not_inspected; health_need:raw_not_inspected | Verify illness/need denominator, care seeking, and cost/distance/supply barrier semantics. |
| climate_linkage | fail | survey_timing:raw_not_inspected; climate_geography:raw_not_inspected | Verify survey month/date, usable admin/GPS/cluster geography, and accepted CHIRPS/ERA5 extraction route. |
| double_failure | fail | financial_ready=0; access_ready=0 | Pass both financial-protection and access/forgone-care value verification gates. |

## Expected Files or Modules

- `BaselineandFirstFollowup`: not_present; concepts=admin1_or_admin2;age;agriculture_livelihood;care_sought;coping_borrowed;education;interview_date_or_survey_month;reason_not_sought_supply;sex;shock_module_variable;total_consumption_or_income
- `nigeriayouwinr4public`: not_present; concepts=admin1_or_admin2;agriculture_livelihood;asset_index_or_asset_variable;coping_borrowed;illness_or_injury_need;interview_date_or_survey_month;reason_not_sought_supply;sex;shock_module_variable;total_consumption_or_income
- `ThirdFollowup`: not_present; concepts=admin1_or_admin2;age;agriculture_livelihood;asset_index_or_asset_variable;coping_borrowed;education;interview_date_or_survey_month;reason_not_sought_supply;sex;total_consumption_or_income
- `SecondFollowup`: not_present; concepts=admin1_or_admin2;age;agriculture_livelihood;asset_index_or_asset_variable;coping_borrowed;education;illness_or_injury_need;interview_date_or_survey_month;reason_not_sought_supply;sex;total_consumption_or_income
- `regionuid`: not_present; concepts=admin1_or_admin2
- `VariablesRestrictedData`: not_present; concepts=reason_not_sought_distance

## Raw Variable Verification Queue

- `BaselineandFirstFollowup` / `assigntreat`: care_or_barrier; raw_not_inspected; action=inspect raw values, labels, merge keys, units, recall period, and missing codes before harmonization
- `BaselineandFirstFollowup` / `a2_deceased`: climate_geography; raw_not_inspected; action=inspect raw values, labels, merge keys, units, recall period, and missing codes before harmonization
- `BaselineandFirstFollowup` / `a_disqualified`: climate_geography; raw_not_inspected; action=inspect raw values, labels, merge keys, units, recall period, and missing codes before harmonization
- `BaselineandFirstFollowup` / `a_withdrawn`: climate_geography; raw_not_inspected; action=inspect raw values, labels, merge keys, units, recall period, and missing codes before harmonization
- `BaselineandFirstFollowup` / `m_region`: climate_geography; raw_not_inspected; action=inspect raw values, labels, merge keys, units, recall period, and missing codes before harmonization
- `BaselineandFirstFollowup` / `northcentral`: climate_geography; raw_not_inspected; action=inspect raw values, labels, merge keys, units, recall period, and missing codes before harmonization
- `BaselineandFirstFollowup` / `northeastern`: climate_geography; raw_not_inspected; action=inspect raw values, labels, merge keys, units, recall period, and missing codes before harmonization
- `BaselineandFirstFollowup` / `northwestern`: climate_geography; raw_not_inspected; action=inspect raw values, labels, merge keys, units, recall period, and missing codes before harmonization
- `BaselineandFirstFollowup` / `region`: climate_geography; raw_not_inspected; action=inspect raw values, labels, merge keys, units, recall period, and missing codes before harmonization
- `BaselineandFirstFollowup` / `southeastern`: climate_geography; raw_not_inspected; action=inspect raw values, labels, merge keys, units, recall period, and missing codes before harmonization
- `BaselineandFirstFollowup` / `southsouth`: climate_geography; raw_not_inspected; action=inspect raw values, labels, merge keys, units, recall period, and missing codes before harmonization
- `BaselineandFirstFollowup` / `southwestern`: climate_geography; raw_not_inspected; action=inspect raw values, labels, merge keys, units, recall period, and missing codes before harmonization
- `SecondFollowup` / `s_region`: climate_geography; raw_not_inspected; action=inspect raw values, labels, merge keys, units, recall period, and missing codes before harmonization
- `ThirdFollowup` / `t_d19`: climate_geography; raw_not_inspected; action=inspect raw values, labels, merge keys, units, recall period, and missing codes before harmonization
- `ThirdFollowup` / `t_region`: climate_geography; raw_not_inspected; action=inspect raw values, labels, merge keys, units, recall period, and missing codes before harmonization
- `nigeriayouwinr4public` / `D19`: climate_geography; raw_not_inspected; action=inspect raw values, labels, merge keys, units, recall period, and missing codes before harmonization

## Promotion Rule

Do not write this country-wave into `data/` until the raw package is complete,
merge keys and survey design are verified, financial-protection and access
variables pass value/unit/recall/missing-code checks, and a CHIRPS or ERA5
climate-linkage route is accepted.
