# Country-Wave Promotion Packet: Malawi 2004-2005

Dataset: `Second Integrated Household Survey 2004-2005`

IDNO: `MWI_2004_IHS-II_v01_M`

Official URL: https://microdata.worldbank.org/catalog/2307/get-microdata

Local target folder: `temp/raw_downloads/MWI_2004_IHS-II_v01_M/`

Current registry status: `not_promoted`

## Gate Summary

| Gate | Status | Evidence | Required action |
|---|---|---|---|
| complete_original_raw_package | fail | intake_status=instructions_or_documentation_only; tabular=0; archives=0; docs=1 | Place complete original raw archive/tabular package and documentation in the local target folder. |
| raw_value_unit_recall_missing_verification | fail | raw_not_inspected=81 | Inspect raw labels/values, merge keys, units, recall periods, skip patterns, and missing codes. |
| financial_protection_che10_che25 | fail | climate_geography:raw_not_inspected; household_id:raw_not_inspected; oop_health_expenditure:raw_not_inspected; survey_timing:raw_not_inspected; survey_weight:raw_not_inspected; total_consumption_or_income:raw_not_inspected | Verify total consumption/income, OOP health expenditure, weights, timing, geography, and merge keys. |
| access_forgone_care | fail | care_or_barrier:raw_not_inspected; health_need:raw_not_inspected | Verify illness/need denominator, care seeking, and cost/distance/supply barrier semantics. |
| climate_linkage | fail | survey_timing:raw_not_inspected; climate_geography:raw_not_inspected | Verify survey month/date, usable admin/GPS/cluster geography, and accepted CHIRPS/ERA5 extraction route. |
| double_failure | fail | financial_ready=0; access_ready=0 | Pass both financial-protection and access/forgone-care value verification gates. |

## Expected Files or Modules

- `ihs2_ag`: not_present; concepts=agriculture_livelihood;household_size;household_weight_or_person_weight;rural;shock_module_variable
- `ihs2_household`: not_present; concepts=admin1_or_admin2;age;agriculture_livelihood;asset_index_or_asset_variable;education;household_head_marker;household_size;household_weight_or_person_weight;interview_date_or_survey_month;nonfood_consumption;pid;psu_or_cluster_id;reason_not_sought_distance;rural;sex;strata
- `sec_r`: not_present; concepts=admin1_or_admin2;agriculture_livelihood;hhid;household_size;household_weight_or_person_weight;psu_or_cluster_id;rural;strata
- `sec_d`: not_present; concepts=admin1_or_admin2;asset_index_or_asset_variable;coping_borrowed;coping_sold_assets;hhid;household_size;household_weight_or_person_weight;illness_or_injury_need;oop_health_expenditure;psu_or_cluster_id;rural;strata
- `sec_o`: not_present; concepts=admin1_or_admin2;agriculture_livelihood;hhid;household_size;household_weight_or_person_weight;psu_or_cluster_id;rural;strata
- `mod_f`: not_present; concepts=admin1_or_admin2;agriculture_livelihood;coping_borrowed;psu_or_cluster_id;reason_not_sought_distance;rural;shock_module_variable
- `sec_g`: not_present; concepts=admin1_or_admin2;asset_index_or_asset_variable;hhid;household_size;household_weight_or_person_weight;psu_or_cluster_id;rural;strata
- `sec_s`: not_present; concepts=admin1_or_admin2;agriculture_livelihood;hhid;household_size;household_weight_or_person_weight;psu_or_cluster_id;rural;strata
- `sec_ac`: not_present; concepts=admin1_or_admin2;age;asset_index_or_asset_variable;hhid;household_head_marker;household_size;household_weight_or_person_weight;illness_or_injury_need;psu_or_cluster_id;rural;sex;strata
- `sec_ab`: not_present; concepts=admin1_or_admin2;asset_index_or_asset_variable;education;hhid;household_size;household_weight_or_person_weight;psu_or_cluster_id;rural;shock_module_variable;strata
- `sec_p`: not_present; concepts=admin1_or_admin2;agriculture_livelihood;hhid;household_size;household_weight_or_person_weight;psu_or_cluster_id;rural;strata
- `sec_q1`: not_present; concepts=admin1_or_admin2;agriculture_livelihood;care_not_sought_reason;coping_borrowed;hhid;household_size;household_weight_or_person_weight;psu_or_cluster_id;reason_not_sought_distance;rural;strata

## Raw Variable Verification Queue

- `mod_d` / `cd51b`: care_or_barrier; raw_not_inspected; action=inspect raw values, labels, merge keys, units, recall period, and missing codes before harmonization
- `mod_d` / `cd_51a`: care_or_barrier; raw_not_inspected; action=inspect raw values, labels, merge keys, units, recall period, and missing codes before harmonization
- `Filters;ihs2_anthro;ihs2_ea_data;ihs2_exp;ihs2_household;ihs2_individ;ihs2_pov;mod_a;mod_b;mod_f;mod_g50better;mod_g50worse;mod_h;sec_a;sec_aa;sec_ab;sec_ac;sec_ad;sec_b;sec_c` / `dist`: climate_geography; raw_not_inspected; action=inspect raw values, labels, merge keys, units, recall period, and missing codes before harmonization
- `Filters;ihs2_anthro;ihs2_exp;ihs2_household;ihs2_pov;sec_a;sec_aa;sec_ab;sec_ac;sec_ad;sec_b;sec_c;sec_d;sec_e;sec_f;sec_g;sec_h;sec_i;sec_j1;sec_j2` / `region`: climate_geography; raw_not_inspected; action=inspect raw values, labels, merge keys, units, recall period, and missing codes before harmonization
- `Filters;ihs2_exp;ihs2_household;ihs2_pov;sec_a;sec_aa;sec_ab;sec_ac;sec_ad;sec_b;sec_c;sec_d;sec_e;sec_f;sec_g;sec_h;sec_i;sec_j1;sec_j2;sec_k` / `add`: climate_geography; raw_not_inspected; action=inspect raw values, labels, merge keys, units, recall period, and missing codes before harmonization
- `Filters;ihs2_exp;ihs2_household;ihs2_individ;ihs2_pov;sec_a;sec_aa;sec_ab;sec_ac;sec_ad;sec_b;sec_c;sec_d;sec_e;sec_f;sec_g;sec_h;sec_i;sec_j1;sec_j2` / `strata`: climate_geography; raw_not_inspected; action=inspect raw values, labels, merge keys, units, recall period, and missing codes before harmonization
- `mod_d` / `cd10a`: climate_geography; raw_not_inspected; action=inspect raw values, labels, merge keys, units, recall period, and missing codes before harmonization
- `mod_d` / `cd10b`: climate_geography; raw_not_inspected; action=inspect raw values, labels, merge keys, units, recall period, and missing codes before harmonization
- `mod_d` / `cd9`: climate_geography; raw_not_inspected; action=inspect raw values, labels, merge keys, units, recall period, and missing codes before harmonization
- `sec_b` / `b12b`: climate_geography; raw_not_inspected; action=inspect raw values, labels, merge keys, units, recall period, and missing codes before harmonization
- `Filters;ihs2_ag;ihs2_exp;ihs2_household;ihs2_pov;sec_a;sec_aa;sec_ab;sec_ac;sec_ad;sec_b;sec_c;sec_d;sec_e;sec_f;sec_g;sec_h;sec_i;sec_j1;sec_j2` / `hhsize`: demographics; raw_not_inspected; action=inspect raw values, labels, merge keys, units, recall period, and missing codes before harmonization
- `ihs2_anthro` / `anthroage`: demographics; raw_not_inspected; action=inspect raw values, labels, merge keys, units, recall period, and missing codes before harmonization
- `ihs2_anthro;ihs2_individ;sec_b` / `b03`: demographics; raw_not_inspected; action=inspect raw values, labels, merge keys, units, recall period, and missing codes before harmonization
- `ihs2_anthro` / `haz`: demographics; raw_not_inspected; action=inspect raw values, labels, merge keys, units, recall period, and missing codes before harmonization
- `ihs2_anthro` / `waz`: demographics; raw_not_inspected; action=inspect raw values, labels, merge keys, units, recall period, and missing codes before harmonization
- `ihs2_exp` / `exp_cat101`: demographics; raw_not_inspected; action=inspect raw values, labels, merge keys, units, recall period, and missing codes before harmonization

## Promotion Rule

Do not write this country-wave into `data/` until the raw package is complete,
merge keys and survey design are verified, financial-protection and access
variables pass value/unit/recall/missing-code checks, and a CHIRPS or ERA5
climate-linkage route is accepted.
