# SIPP 2018-2025 All-Product Source and Download Audit

> **Subsequent verification:** The 2026-07-16 live re-audit compared all 50 local canonical ZIPs with the current Census remotes byte for byte and found 50/50 exact matches. See `report/108_sipp_official_sources_versions_weights_raw_reaudit.md`.

## Scope

This audit covers every official data-product type published for the redesigned annual SIPP from file year 2018 through file year 2025:

- Primary public-use data.
- Annual/cross-sectional replicate weights.
- Every published 2-, 3-, and 4-year longitudinal weight file.
- Every matching longitudinal replicate-weight file.

This scope is complete for the modern 2018+ system through the latest 2025 release. It is not an archive of the separate legacy 1984-2014 panel/wave system.

## Official discovery method

The build crawled the official Census directory for each file year and saved the returned HTML as a provenance snapshot:

`https://www2.census.gov/programs-surveys/sipp/data/datasets/{year}/`

The crawl catalog contains 371 unique official directory entries and no duplicate URLs. A fixed expected-product matrix was then compared with the crawl, so a missing official product could not be silently replaced by a guessed filename.

## Verified product matrix

| File year | Primary | Annual replicate | Longitudinal weights | Longitudinal replicate weights | Total canonical CSV products |
|---|---:|---:|---|---|---:|
| 2018 | Yes | Yes | None | None | 2 |
| 2019 | Yes | Yes | 2-year | 2-year | 4 |
| 2020 | Yes | Yes | 2-, 3-year | 2-, 3-year | 6 |
| 2021 | Yes | Yes | 2-, 3-, 4-year | 2-, 3-, 4-year | 8 |
| 2022 | Yes | Yes | 2-, 3-year | 2-, 3-year | 6 |
| 2023 | Yes | Yes | 2-, 3-, 4-year | 2-, 3-, 4-year | 8 |
| 2024 | Yes | Yes | 2-, 3-, 4-year | 2-, 3-, 4-year | 8 |
| 2025 | Yes | Yes | 2-, 3-, 4-year | 2-, 3-, 4-year | 8 |
| **Total** | **8** | **8** | **17** | **17** | **50** |

There is no 2018 multi-year product because a second annual file was not yet available. The absence of a 2022 four-year file is also an observed official-directory fact, not a local omission.

## Format boundary

The canonical archived payload for each unique product is the official pipe-delimited CSV inside the official ZIP. SAS, Stata, and standalone GZIP versions are alternative encodings of the same product. Their official URLs remain in `data/metadata/sipp_official_file_catalog_2018_2025.csv`, but they were not downloaded as redundant copies.

No raw ZIP was extracted and recompressed, edited, renamed internally, or converted in place. Analysis-ready Parquets are separate derivative files.

## Local archive

- Canonical raw products: 50 files.
- Compressed bytes: 7,537,185,902 (7.020 GiB).
- Uncompressed CSV bytes represented by the ZIPs: 44.679 GiB.
- Catalog-selected lightweight source files: 136 schemas, validations, dictionaries, examples, and metadata documents.
- Saved official directory snapshots: 8.
- Interrupted `.part` downloads: 0.

Key inventories:

- `data/metadata/sipp_official_file_catalog_2018_2025.csv`
- `data/metadata/sipp_official_product_matrix_2018_2025.csv`
- `data/metadata/sipp_raw_download_manifest_2018_2025.csv`

## Deep source verification

Every one of the 50 canonical ZIPs was read to the end without extracting it to disk. This simultaneously checked:

1. Recorded SHA-256 against a fresh local hash.
2. ZIP CRC while fully streaming the CSV.
3. One expected CSV entry and exact uncompressed byte size.
4. Raw header against the matching official JSON schema.
5. Direct CSV row count against the matching official validation workbook.

Result: **50/50 raw products passed all five checks**.

The direct verification table is `data/sample_audits/sipp_all_raw_products_verification.csv`.

## Reproduction

```powershell
python script/01_ingest/04_crawl_download_all_sipp_products.py
python script/01_ingest/06_verify_all_sipp_products.py
```
