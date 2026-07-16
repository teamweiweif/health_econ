# 2025 SIPP Update and Merge Audit

## Release verified

- Census release: 2025 SIPP version 1.0, released July 15, 2026.
- Reference period: January-December 2024.
- Official release page: https://www.census.gov/programs-surveys/sipp/data/datasets/2025-data/2025.html
- Census cautions that the 2025 SIPP had increasing-cost collection complications and a lower-than-average national unit response rate.

## Downloaded and organized

- Official files and documents: 34
- Total downloaded/archived bytes represented in the manifest: 684,371,200
- Primary, replicate, longitudinal, and longitudinal-replicate ZIP CRC failures: 0
- Full provenance and SHA-256 checksums: `data/metadata/sipp_2025_official_download_manifest.csv`
- Raw survey payloads remain under `temp/raw_downloads/census_sipp/2025/` and are not mixed into `data/analysis_ready/`.

Replicate weights and longitudinal weights are stored as separate official files. They are not column-joined to the primary person-month panel because they have distinct weight layouts and should be merged only for the specific variance or longitudinal estimand being run.

## Schema compatibility

- 2024 primary variables: 5,203
- 2025 primary variables: 5,203
- Exact common variable names: 5,203
- Added in 2025: 0
- Removed in 2025: 0
- Dtype changes: 7
- Label changes: 210
- The 2025 raw pipe-delimited header exactly matches the official 2025 schema order.
- Parsed 2025 dictionary entries matched to schema variables: 2,967

The seven dtype changes are outside the 97-column analysis-ready panel. Every one of the panel's 90 Census source variables is present in the 2025 schema.

## New data-only panel

- Historical input: `data/analysis_ready/sipp_2018_2024_person_month_panel.parquet`
- New output: `data/analysis_ready/sipp_2018_2025_person_month_panel.parquet`
- Coverage: SIPP file years 2018-2025, reference years 2017-2024.
- Existing rows: 4,051,455
- Added 2025 rows: 379,215
- Added 2025 unique persons: 32,052
- Total merged rows: 4,430,670
- Columns: 97 (90 Census source variables plus 7 harmonization identifiers/time fields).
- 2025 duplicate `SSUID + PNUM + MONTHCODE` keys: 0
- `RPRITYPE1` is now integrated for 2018-2025; historical four-key alignment passed and missing rows are 0 historically and 0 in 2025.
- New panel bytes: 97,347,506
- Newly constructed outcome/result columns added: no.

The old 2018-2024 panel and all historical model outputs remain unchanged. This update prepares the new data input but does not silently rerun or overwrite the ARPA estimates.

## Use boundary

For open-ended idea development or simple Web GPT analysis, use `sipp_2018_2025_person_month_panel.parquet`. It is the broad cleaned source-variable panel. Do not substitute `coverage_transition_panel.parquet` or `exposure_temporary_crossing_panel.parquet` when the goal is to avoid preconstructed outcomes/exposures.

This 97-column panel is broad relative to the current research workflow, but it is not a dump of all 5,203 raw Census variables. The complete public-use payload remains in the official ZIP archives, with metadata in the updated 2018-2025 registries.
