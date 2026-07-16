# SIPP Dataset Workspace

This is the GitHub-readable export of the local modern 2018+ Census SIPP workspace. It publishes metadata, audit evidence, scripts, reports, and lightweight aggregate results for GPT and collaborator review. The verified raw ZIP archive and analysis-ready Parquet panels remain in the local source workspace and are intentionally excluded from GitHub.

Start with `00_START_HERE_FOR_GPT.md` for the current evidence boundary and reading order.

## Current coverage

- SIPP file years: 2018-2025; reference years: 2017-2024.
- Latest release: 2025 SIPP version 1.0, released July 15, 2026, covering January-December 2024.
- Canonical official CSV products: 50/50 archived locally.
- Product count: 8 primary files, 8 annual replicate-weight files, 17 longitudinal-weight files, and 17 longitudinal replicate-weight files.
- Alternative official SAS, Stata, and GZIP encodings are cataloged but not downloaded as redundant data copies.

This is complete for the redesigned 2018+ annual SIPP through file year 2025. It does not claim to archive the legacy 1984-2014 panel/wave system.

## Official longitudinal availability

| SIPP file year | Reference end year | Published multi-year weights |
|---|---:|---|
| 2018 | 2017 | None |
| 2019 | 2018 | 2-year |
| 2020 | 2019 | 2-year, 3-year |
| 2021 | 2020 | 2-year, 3-year, 4-year |
| 2022 | 2021 | 2-year, 3-year |
| 2023 | 2022 | 2-year, 3-year, 4-year |
| 2024 | 2023 | 2-year, 3-year, 4-year |
| 2025 | 2024 | 2-year, 3-year, 4-year |

## Default data-only panel

`data/analysis_ready/sipp_2018_2025_person_month_panel.parquet`

- 4,430,670 person-month rows.
- 97 columns: 90 official Census source variables plus 7 harmonization identifiers/time fields.
- Includes `RPRITYPE1` for employer-related private coverage.
- Contains no newly constructed outcome, exposure, or result variables.

Use this file for open-ended idea development or simple Web GPT analysis. The older `sipp_2018_2024_person_month_panel.parquet` remains frozen for reproducing existing 2017-2023 analyses.

This pooled panel is not itself a single cross-section and is not automatically a longitudinal-weighted sample. It stacks annual person-month files. Formal multi-year analysis should use one of the official longitudinal cohorts below.

## Latest longitudinal panels

| Reference period | Rows | Persons | Official weight | File |
|---|---:|---:|---|---|
| 2023-2024 | 436,267 | 18,207 | `FINYR2` | `data/analysis_ready/longitudinal/sipp_2023_2024_longitudinal_2y_person_month.parquet` |
| 2022-2024 | 385,350 | 10,717 | `FINYR3` | `data/analysis_ready/longitudinal/sipp_2022_2024_longitudinal_3y_person_month.parquet` |
| 2021-2024 | 293,630 | 6,122 | `FINYR4` | `data/analysis_ready/longitudinal/sipp_2021_2024_longitudinal_4y_person_month.parquet` |

Each file has the same 97 columns as the default data-only panel plus exactly one official `FINYR` weight. No outcome, exposure, or result variable was constructed. A small number of officially weighted person-years have fewer than 12 published month records; those records were preserved without imputation and are listed in `data/sample_audits/sipp_latest_longitudinal_incomplete_person_years.csv`.

## Storage layout

- `temp/raw_downloads/census_sipp/{year}/`: official compressed survey payloads.
- `temp/source_metadata/census_sipp/{year}/`: official directory snapshots, schemas, validation files, dictionaries, and examples.
- `data/analysis_ready/longitudinal_weights/{year}/`: all 17 normalized person-level longitudinal-weight Parquets.
- `data/analysis_ready/longitudinal_replicate_weights/{year}/`: all 17 normalized person-level replicate-weight Parquets.
- `data/analysis_ready/longitudinal/`: latest usable 2-, 3-, and 4-year person-month panels.
- `data/metadata/`: variable inventories, schema comparisons, and source manifests.
- `data/sample_audits/`: row counts, missingness, key checks, and completion checks.
- `script/`: reproducible ingest, construction, analysis, and reporting code.
- `report/` and `result/`: research memos, model tables, figures, and diagnostics.

Annual replicate weights and longitudinal replicate weights are intentionally not repeated across every primary-panel row. They retain their official person or person-month layouts and should be linked only for the variance estimator being run.

## Current raw-data and inference status

- Live official re-audit on 2026-07-16: all 50 canonical ZIPs match the current Census remote files byte for byte (7,537,185,902 bytes compared).
- Current release versions: 2018-2021 v1.1; 2022-2025 v1.0. The selected panel exactly reproduces all audited v1.1 income/poverty fields.
- A Census monthly health-insurance user note affects selected 2018-2023 records. The original panel is preserved; an additive 19,625-row correction patch is at `data/analysis_ready/sipp_2018_2023_health_insurance_official_usernote_correction_patch.parquet`.
- Thirty-five idea-screen scripts formerly used `TSSSAMT` as an invalid fallback weight. The source code is repaired; paper-bound historical outputs still require regeneration.
- Final survey inference must use the appropriate `WPFINWGT` or `FINYR2/3/4` point weight and matching 240 Fay-BRR replicate weights.
- The 2025 Source and Accuracy Statement reports a 42.63% cross-sectional weighted household response rate; longitudinal person response declines to 25.75% for `FINYR4`.

## Verification

- 2025 update audit: `report/102_sipp_2025_update_and_merge_audit.md`.
- All-product source/download audit: `report/104_sipp_all_versions_source_and_download_audit.md`.
- Longitudinal build audit: `report/105_sipp_longitudinal_panels_build_audit.md`.
- Independent all-version completion check: `report/106_sipp_all_versions_completion_check.md`.
- ARPA raw/weight/health sensitivity: `report/107_arpa400_raw_data_quality_sensitivity.md`.
- Current official-source/version/weight re-audit: `report/108_sipp_official_sources_versions_weights_raw_reaudit.md`.
- Prioritized issue register: `report/109_sipp_raw_data_issue_register.md`.
- Archive result: 11/11 completion checks, 50/50 deep raw-product checks, 50/50 current-remote byte comparisons, and 15/15 final re-audit checks passed.

Raw ZIPs and analysis-ready parquet files remain local and are excluded from the lightweight GitHub package.
