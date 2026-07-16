# SIPP Longitudinal Products and Latest Panels Build Audit

## What a longitudinal SIPP product is

For the redesigned 2018+ SIPP, Census does not publish a separate copy of all microdata for every multi-year duration. It publishes person-level longitudinal weights. Those weights select the eligible multi-year cohort and are linked to the relevant annual primary files using:

`SSUID + PNUM + SPANEL`

The corresponding `FINYR2`, `FINYR3`, or `FINYR4` estimates the population represented continuously across the stated multi-year reference period. Matching longitudinal replicate files supply `REPWGT0` through `REPWGT240` for variance estimation.

## Historical product organization

All 17 published longitudinal-weight files and all 17 matching replicate files were converted to link-ready Parquet without changing raw values:

- `data/analysis_ready/longitudinal_weights/{file_year}/`
- `data/analysis_ready/longitudinal_replicate_weights/{file_year}/`

Only header case and the historical `PANEL` versus `SPANEL` spelling were normalized in the derivative files. The exact source headers remain in the untouched ZIPs, and every rename is recorded in `data/metadata/sipp_longitudinal_header_normalization_2019_2025.csv`.

For all 17 pairs:

- Longitudinal keys are unique.
- Replicate keys are unique.
- Key sets match exactly.
- Every `FINYR` weight is positive.
- `REPWGT0` reproduces the matching `FINYR` value within the observed CSV decimal-rounding tolerance of `0.00002`.
- Maximum observed absolute difference: `0.000010000076`.

See `data/metadata/sipp_longitudinal_product_audit_2019_2025.csv`.

## Latest usable panels

| Horizon | Reference period | Annual file years linked | Weight | Persons | Person-month rows | Columns |
|---|---|---|---|---:|---:|---:|
| 2-year | 2023-2024 | 2024-2025 | `FINYR2` | 18,207 | 436,267 | 98 |
| 3-year | 2022-2024 | 2023-2025 | `FINYR3` | 10,717 | 385,350 | 98 |
| 4-year | 2021-2024 | 2022-2025 | `FINYR4` | 6,122 | 293,630 | 98 |

Each output contains the base data-only panel's 97 columns plus exactly one official longitudinal weight. No outcome, exposure, transition, policy, or result variable was added.

## Source-faithful month handling

Every official weighted person was found in every required annual file year, all weight keys matched, and no duplicate person-month key was created. However, official longitudinal membership does not force each published person-year to contain 12 row records.

| Horizon | Incomplete person-years | Rows absent relative to a full 12-month grid |
|---|---:|---:|
| 2-year | 113 | 701 |
| 3-year | 69 | 462 |
| 4-year | 40 | 226 |

No synthetic rows were inserted. The exact people, years, observed months, and absent months are recorded in `data/sample_audits/sipp_latest_longitudinal_incomplete_person_years.csv`.

## Official 2021 four-year metadata inconsistency

The official 2021 `FINYR4` dictionary defines the date range as January 2017 through December 2020, although the text mistakenly calls it a three-year period. The matching official replicate CSV reports `INITIAL_YEAR=2017`, `CTL_DATE=DEC2020`, but `FINAL_YEAR=2021`.

The local build did not rewrite this source value. The expected analytic reference period remains 2017-2020 based on the actual four-year date range and 2021 SIPP reference year. The inconsistency is surfaced in the product audit rather than hidden.

## Reproduction

```powershell
python script/01_ingest/05_build_sipp_longitudinal_products.py
```
