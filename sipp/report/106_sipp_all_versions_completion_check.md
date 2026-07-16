# SIPP 2018-2025 All-Versions Completion Check

> **Subsequent verification:** The 2026-07-16 live re-audit confirmed that all 50 canonical ZIPs still match the current Census remotes byte for byte. Analysis-level official user notes, weight-use limits, and response/attrition risks are tracked separately in `report/108_sipp_official_sources_versions_weights_raw_reaudit.md`.

## Final status

**PASS for the modern 2018+ SIPP through file year 2025.**

- Independent completion checks: 11/11 passed.
- Deep raw-product checks: 50/50 passed.
- Canonical official CSV products downloaded: 50/50.
- Longitudinal weight Parquets: 17/17.
- Longitudinal replicate-weight Parquets: 17/17.
- Latest usable longitudinal person-month panels: 3/3.
- Remaining partial downloads: 0.

## Completion checks

| Check | Result |
|---|---|
| Official directory snapshot for 2018-2025 | PASS |
| Official file catalog has all years and unique URLs | PASS |
| Exact 50-product matrix and official listing coverage | PASS |
| Local manifest covers all products | PASS |
| No `.part` downloads remain | PASS |
| SHA-256, full CRC, ZIP size, schema, and row N for all raw products | PASS |
| All 17 + 17 longitudinal derivative Parquets exist | PASS |
| Longitudinal and replicate keys/weights agree | PASS |
| 2021 four-year official period-label inconsistency is surfaced | PASS |
| Latest 2/3/4-year panels have only base columns plus `FINYR` | PASS |
| Canonical raw archive byte total recorded | PASS |

Machine-readable evidence: `data/sample_audits/sipp_all_versions_completion_checks.csv`.

## Annual primary and replicate row counts

| File year | Primary rows | Annual replicate rows |
|---|---:|---:|
| 2018 | 763,186 | 759,402 |
| 2019 | 593,604 | 591,804 |
| 2020 | 622,339 | 620,820 |
| 2021 | 670,678 | 669,078 |
| 2022 | 487,736 | 486,238 |
| 2023 | 476,744 | 475,526 |
| 2024 | 437,168 | 435,883 |
| 2025 | 379,215 | 378,291 |

These counts were obtained directly by streaming the raw official CSVs and match the official validation workbooks. Annual replicate files can contain fewer rows than primary files because their eligible weighted record universe is not identical; this is not treated as corruption.

## Boundaries and residual caveats

1. "All versions" here means all data-product versions published within the redesigned 2018+ annual SIPP for 2018-2025. Legacy 1984-2014 panel/wave releases are a different archive and are not included.
2. SAS, Stata, and standalone GZIP encodings are cataloged but not duplicated locally. The official pipe-delimited CSV ZIP is the canonical raw copy.
3. Annual replicate files remain in canonical raw ZIP form because expanding 241 replicate columns into the default panel would create unnecessary duplication. Their schemas and validations are local and verified.
4. A small number of weighted person-years have fewer than 12 official month records. They remain unaltered and explicitly audited.
5. The official 2021 four-year replicate period label is internally inconsistent. Raw values are preserved and the inconsistency is documented.

## Core evidence files

- `data/metadata/sipp_official_file_catalog_2018_2025.csv`
- `data/metadata/sipp_official_product_matrix_2018_2025.csv`
- `data/metadata/sipp_raw_download_manifest_2018_2025.csv`
- `data/sample_audits/sipp_all_raw_products_verification.csv`
- `data/sample_audits/sipp_all_versions_completion_checks.csv`
- `data/metadata/sipp_longitudinal_product_audit_2019_2025.csv`
- `data/sample_audits/sipp_latest_longitudinal_panel_counts.csv`
