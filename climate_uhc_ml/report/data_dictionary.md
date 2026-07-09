# Harmonized Data Dictionary

Status: metadata-backed draft only. These fields are candidate mappings from official World Bank catalog/data-dictionary metadata and variable labels. They are not yet verified against raw microdata files.

## Metadata Coverage

| Item | Count |
|---|---:|
| Priority studies with metadata schema extraction | 35 |
| Data files/modules parsed from data dictionaries | 2137 |
| Variables parsed from API labels | 82281 |
| Studies with metadata hits for both consumption/income and OOP health expenditure | 33 |
| Studies with metadata hits for health need plus care/access | 35 |
| Studies with some geography/cluster/residence metadata hit | 35 |

## Candidate Variable Map Rows

| Map file | Candidate rows |
|---|---:|
| `variable_map_consumption.csv` | 414 |
| `variable_map_demographics.csv` | 4107 |
| `variable_map_geography.csv` | 4204 |
| `variable_map_health_expenditure.csv` | 528 |
| `variable_map_health_need_access.csv` | 2665 |
| `variable_map_shocks.csv` | 8734 |
| `variable_map_survey_design.csv` | 4706 |

## Top Metadata Concepts

| Concept | Variable-label hits |
|---|---:|
| agriculture_livelihood | 5767 |
| admin_geography | 3401 |
| shock_module | 1615 |
| psu_cluster | 1554 |
| household_id | 1286 |
| distance_barrier | 1211 |
| coping_borrowed | 1190 |
| sex | 998 |
| assets_wealth | 909 |
| education | 873 |
| age | 794 |
| care_sought | 576 |
| weights | 540 |
| illness_need | 465 |
| rural_urban | 451 |
| strata | 382 |
| person_id | 349 |
| oop_health_expenditure | 347 |
| gps | 295 |
| reason_not_sought | 197 |

## Harmonized Minimum Fields

The intended harmonized fields remain those in the project objective: country, survey metadata, IDs, weights, survey design, timing, geography, household demographics, total consumption/income, OOP health expenditure, insurance, illness/need, care seeking, access barriers, coping, food insecurity, and livelihood variables.

Every current row in `temp/variable_map_*.csv` has quality flag `metadata_only_requires_raw_verification`. Raw Stata/SPSS/SAS/CSV files must be inspected before any harmonized analytical dataset is built.
