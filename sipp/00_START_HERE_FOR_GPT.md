# SIPP Audit: Start Here for GPT

This folder is a lightweight review export. It does not contain person-level Census microdata, raw ZIP payloads, or analysis-ready Parquet panels.

## Current verdict

- Modern 2018-2025 canonical raw archive: **PASS**.
- Current official products: 8 primary files, 8 annual replicate files, 17 longitudinal weight files, and 17 matching longitudinal replicate files.
- Live verification: 50/50 local canonical ZIPs matched the current Census remotes byte for byte; 7,537,185,902 bytes were compared.
- Release versions: 2018-2021 v1.1; 2022-2025 v1.0.
- Formal analysis readiness: **CONDITIONAL PASS** because health-insurance corrections, weight choice, Fay-BRR variance, and attrition must be handled explicitly.
- ARPA 400% FPL design: **CONDITIONAL GO**, not a final causal result.
- Historical 1984-2014 legacy heavy raw: not downloaded; official metadata and 1,413 links are cataloged.

## Read in this order

1. `report/108_sipp_official_sources_versions_weights_raw_reaudit.md`
2. `report/109_sipp_raw_data_issue_register.md`
3. `report/107_arpa400_raw_data_quality_sensitivity.md`
4. `data_metadata/sample_audits/sipp_reaudit_final_checks_20260716.csv`
5. `data_metadata/sample_audits/sipp_raw_and_weight_issue_register_20260716.csv`
6. `data_metadata/metadata/sipp_release_version_ledger_2018_2025.csv`
7. `data_metadata/metadata/sipp_weight_product_use_ledger.csv`
8. `data_metadata/metadata/sipp_2025_response_and_attrition_summary.csv`
9. `data_metadata/publication_self_check_20260716.csv`

## Important open issues

- The Census monthly health-insurance user note affects selected 2018-2023 records. An additive local correction patch exists, but the Parquet patch is excluded from GitHub; its counts and logic are fully documented here.
- The Census web correction table contains an apparent private-recode formula inconsistency. The audit preserves both original and interpreted corrected results.
- Thirty-five idea-screen scripts previously used `TSSSAMT` as an invalid fallback weight. All source instances are repaired; historical outputs used in a paper must be regenerated.
- Final inference has not yet used the matching 240 Census replicate weights with Fay-BRR.
- `RMARKTPLACE` is not a clean insurance-type variable and cannot alone identify nongroup private Marketplace enrollment.

## GitHub path mapping

Reports and scripts keep their local relative paths. Local data paths are remapped:

| Local source path | GitHub review path |
|---|---|
| `data/metadata/` | `data_metadata/metadata/` |
| `data/sample_audits/` | `data_metadata/sample_audits/` |
| `data/policy/` | `data_metadata/policy/` |
| `result/` | `result/` for lightweight files only |

The full included/excluded boundary is machine-readable in:

- `data_metadata/local_file_inventory.csv`
- `data_metadata/excluded_file_inventory.csv`

## Official Census anchors

- SIPP datasets: https://www.census.gov/programs-surveys/sipp/data/datasets.html
- Guide to selecting 2018+ SIPP weights: https://www2.census.gov/programs-surveys/sipp/Select_weights_2018_SIPP_JUN24.pdf
- 2025 Users Guide: https://www2.census.gov/programs-surveys/sipp/tech-documentation/methodology/2025_SIPP_Users_Guide.pdf
- 2025 Source and Accuracy Statement: https://www2.census.gov/programs-surveys/sipp/tech-documentation/source-accuracy-statements/2025/SIPP-2025-SA.pdf
- Monthly health-insurance error note: https://www.census.gov/programs-surveys/sipp/tech-documentation/user-notes/2023-usernotes/2023-monthly-hi-variables-error.html
