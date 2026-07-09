# Raw Ingestion Plan

Status: raw ingestion is planned but not executed. These artifacts organize what must be checked after manual downloads; they do not verify raw data or select an analytical sample.

## Gate Counts

| Gate status | Count |
|---|---:|
| ready_for_raw_schema_inspection | 1 |
| waiting_for_manual_download | 27 |

## Summary Metrics

| Metric | Value | Interpretation |
|---|---:|---|
| raw_ingestion_plan_rows | 28 | Quality-screened country-waves with explicit target folders and next checks. |
| raw_ingestion_concept_rows | 364 | Dataset-concept verification checklist rows. |
| raw_ingestion_module_rows | 1615 | Candidate module/file rows to inspect after download. |
| metadata_supported_concept_rows | 315 | Concept rows supported by moderate/high metadata evidence, still raw-unverified. |
| raw_verified_concept_rows | 13 | Concept rows where raw variables have been inspected. |
| gate_count_ready_for_raw_schema_inspection | 1 | Raw ingestion gate status count. |
| gate_count_waiting_for_manual_download | 27 | Raw ingestion gate status count. |

## First Download Targets

| quality_rank | country | wave | idno | raw_download_status | main_required_concepts_supported | double_required_concepts_supported | local_target_folder |
|---|---|---|---|---|---|---|---|
| 1 | Ethiopia | 2021-2022 | ETH_2021_ESPS-W5_v02_M | documentation_only_present | 6 | 8 | temp/raw_downloads/ETH_2021_ESPS-W5_v02_M/ |
| 2 | Ethiopia | 2018-2019 | ETH_2018_ESS_v04_M | documentation_only_present | 6 | 8 | temp/raw_downloads/ETH_2018_ESS_v04_M/ |
| 3 | Malawi | 2007-2009 | MWI_2007-2009_MTM_v01_M | documentation_only_present | 6 | 8 | temp/raw_downloads/MWI_2007-2009_MTM_v01_M/ |
| 4 | Nigeria | 2012-2013 | NGA_2012_GHSP-W2_v02_M | documentation_only_present | 6 | 8 | temp/raw_downloads/NGA_2012_GHSP-W2_v02_M/ |
| 5 | Nigeria | 2015-2016 | NGA_2015_GHSP-W3_v02_M | documentation_only_present | 6 | 8 | temp/raw_downloads/NGA_2015_GHSP-W3_v02_M/ |
| 6 | Nigeria | 2010-2011 | NGA_2010_GHSP-W1_v03_M | documentation_only_present | 6 | 8 | temp/raw_downloads/NGA_2010_GHSP-W1_v03_M/ |
| 7 | Tanzania | 2008-2009 | TZA_2008_NPS-R1_v03_M | documentation_only_present | 6 | 8 | temp/raw_downloads/TZA_2008_NPS-R1_v03_M/ |
| 8 | Tanzania | 2010-2011 | TZA_2010_NPS-R2_v03_M | documentation_only_present | 6 | 8 | temp/raw_downloads/TZA_2010_NPS-R2_v03_M/ |
| 9 | Tanzania | 2012-2013 | TZA_2012_NPS-R3_v01_M | documentation_only_present | 6 | 8 | temp/raw_downloads/TZA_2012_NPS-R3_v01_M/ |
| 10 | Tanzania | 2014-2015 | TZA_2014_NPS-R4_v03_M | documentation_only_present | 6 | 8 | temp/raw_downloads/TZA_2014_NPS-R4_v03_M/ |
| 11 | Tanzania | 2020-2022 | TZA_2020_NPS-R5_v02_M | documentation_only_present | 6 | 8 | temp/raw_downloads/TZA_2020_NPS-R5_v02_M/ |
| 12 | Uganda | 2014 | UGA_2014_SAGE-EL_v01_M | documentation_only_present | 6 | 8 | temp/raw_downloads/UGA_2014_SAGE-EL_v01_M/ |

## Supported Concepts From Metadata

| Concept | Supported rows |
|---|---:|
| total_consumption_or_income | 28 |
| survey_timing | 28 |
| climate_geography | 28 |
| health_need | 28 |
| care_or_barrier | 28 |
| demographics | 28 |
| shocks_or_livelihood | 28 |
| oop_health_expenditure | 25 |
| survey_weight | 23 |
| psu_cluster | 22 |
| household_id | 21 |
| strata | 15 |
| insurance | 13 |

## Required Action After Manual Download

1. Place original archives/files in the listed `temp/raw_downloads/<IDNO>/` folder.
2. Run `python script/17_audit_raw_downloads.py` to checksum and classify files.
3. Run `python script/03_inspect_raw_schemas.py` to create raw file and variable inventories.
4. Re-run `python script/22_build_raw_ingestion_plan.py` and inspect whether raw verification status changes.
5. Build `temp/harmonization_recipe.csv` only from raw-inspected variables with verified units, recall periods, missing values, levels, and merge keys.

## Machine-Readable Outputs

- `temp/raw_ingestion_plan.csv`
- `temp/raw_ingestion_concept_checklist.csv`
- `temp/raw_ingestion_module_checklist.csv`
- `result/raw_ingestion_plan_summary.csv`
