# Raw Download Intake Plan

Status: this package prepares target folders and file-level expectations for manual raw-data intake. It does not claim raw microdata are present unless raw tabular files or archives are detected.

## Intake Status

| Intake status | Count |
|---|---:|
| instructions_or_documentation_only | 36 |
| ready_for_raw_schema_inspection | 1 |

## Expected File Status

| Expected file status | Count |
|---|---:|
| archive_present_needs_schema_extraction | 68 |
| not_present | 1547 |

## Summary Metrics

| Metric | Value | Interpretation |
|---|---:|---|
| raw_download_intake_targets | 37 | Target folders with dataset-level intake instructions. |
| target_readmes_written | 37 | Per-target README files written under temp/raw_downloads. |
| expected_module_rows | 1615 | Metadata-derived module/file rows to check after download. |
| ready_for_raw_schema_inspection_targets | 1 | Targets with raw tabular or archive files currently present. |
| instructions_or_documentation_only_targets | 36 | Targets containing only README/documentation files. |
| waiting_for_download_targets | 0 | Targets with no files yet. |
| expected_file_status_archive_present_needs_schema_extraction | 68 | Expected module/file matching status. |
| expected_file_status_not_present | 1547 | Expected module/file matching status. |

## First Target Folders

| action_rank | dataset_idno | intake_status | raw_tabular_file_count | archive_file_count | expected_core_module_rows | local_target_folder |
|---|---|---|---|---|---|---|
| 1 | ALB_2005_LSMS_v01_M | ready_for_raw_schema_inspection | 0 | 1 | 68 | temp/raw_downloads/ALB_2005_LSMS_v01_M/ |
| 2 | BEN_2021_EHCVM-2_v01_M | instructions_or_documentation_only | 0 | 0 | 0 | temp/raw_downloads/BEN_2021_EHCVM-2_v01_M/ |
| 3 | BGR_1995_IHS_v01_M | instructions_or_documentation_only | 0 | 0 | 69 | temp/raw_downloads/BGR_1995_IHS_v01_M/ |
| 4 | BGR_1997_IHS_v01_M | instructions_or_documentation_only | 0 | 0 | 67 | temp/raw_downloads/BGR_1997_IHS_v01_M/ |
| 5 | CIV_2021_EHCVM-2_v01_M | instructions_or_documentation_only | 0 | 0 | 0 | temp/raw_downloads/CIV_2021_EHCVM-2_v01_M/ |
| 6 | ETH_2016-2020_FJW_v01_M | instructions_or_documentation_only | 0 | 0 | 3 | temp/raw_downloads/ETH_2016-2020_FJW_v01_M/ |
| 7 | ETH_2021_ESPS-W5_v02_M | instructions_or_documentation_only | 0 | 0 | 66 | temp/raw_downloads/ETH_2021_ESPS-W5_v02_M/ |
| 8 | ETH_2018_ESS_v04_M | instructions_or_documentation_only | 0 | 0 | 66 | temp/raw_downloads/ETH_2018_ESS_v04_M/ |
| 9 | GNB_2021_EHCVM-2_v01_M | instructions_or_documentation_only | 0 | 0 | 0 | temp/raw_downloads/GNB_2021_EHCVM-2_v01_M/ |
| 9 | TZA_2008_NPS-R1_v03_M | instructions_or_documentation_only | 0 | 0 | 61 | temp/raw_downloads/TZA_2008_NPS-R1_v03_M/ |
| 10 | JAM_1997_SLC_v01_M | instructions_or_documentation_only | 0 | 0 | 12 | temp/raw_downloads/JAM_1997_SLC_v01_M/ |
| 10 | TZA_2010_NPS-R2_v03_M | instructions_or_documentation_only | 0 | 0 | 27 | temp/raw_downloads/TZA_2010_NPS-R2_v03_M/ |
| 11 | KGZ_1993_KMPS_v01_M | instructions_or_documentation_only | 0 | 0 | 14 | temp/raw_downloads/KGZ_1993_KMPS_v01_M/ |
| 11 | TZA_2012_NPS-R3_v01_M | instructions_or_documentation_only | 0 | 0 | 79 | temp/raw_downloads/TZA_2012_NPS-R3_v01_M/ |
| 12 | MWI_2007-2009_MTM_v01_M | instructions_or_documentation_only | 0 | 0 | 102 | temp/raw_downloads/MWI_2007-2009_MTM_v01_M/ |

## Required Action

1. Complete the access, login, or terms workflow at the dataset URL.
2. Download the full available raw package and documentation where permitted.
3. Place original files in the listed target folder without renaming them.
4. Run `powershell -ExecutionPolicy Bypass -File script/run_all.ps1`.
5. Inspect `temp/raw_schema_inventory/raw_file_inventory.csv`, `temp/raw_schema_inventory/raw_variable_catalog.csv`, and `temp/harmonization_audit.csv` before building a harmonization recipe.

## Machine-Readable Outputs

- `temp/raw_download_intake_manifest.csv`
- `temp/raw_download_expected_files.csv`
- `result/raw_download_intake_summary.csv`
- `temp/raw_downloads/README_RAW_DATA_INTAKE.md`
