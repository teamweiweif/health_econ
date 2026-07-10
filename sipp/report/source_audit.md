# SIPP Source Audit

Audit date: 2026-07-09

## Scope

This workspace contains the Census SIPP public-use primary CSV microdata for survey years 2018 through 2024.

Primary files populated:

- `pu2018_csv.zip`
- `pu2019_csv.zip`
- `pu2020_csv.zip`
- `pu2021_csv.zip`
- `pu2022_csv.zip`
- `pu2023_csv.zip`
- `pu2024_csv.zip`

Each zip contains one primary CSV file: `puYYYY.csv`.

## Source Verification

Primary zip files were copied from the existing local project:

`C:\Users\PC\GlobalHealthPolicy Dropbox\Fan Bowei\US Insurance Project`

Before copying, each local primary zip was checked against the official Census URL by HTTP HEAD `Content-Length`. All seven local files matched the official file sizes.

Official primary file URL pattern:

`https://www2.census.gov/programs-surveys/sipp/data/datasets/YYYY/puYYYY_csv.zip`

Official Census landing pages:

- https://www.census.gov/programs-surveys/sipp/data/datasets.html
- https://www.census.gov/programs-surveys/sipp/data/datasets/2018-data/2018.html
- https://www.census.gov/programs-surveys/sipp/data/datasets/2019-data/2019.html
- https://www.census.gov/programs-surveys/sipp/data/datasets/2020-data/2020.html
- https://www.census.gov/programs-surveys/sipp/data/datasets/2021-data/2021.html
- https://www.census.gov/programs-surveys/sipp/data/datasets/2022-data/2022.html
- https://www.census.gov/programs-surveys/sipp/data/datasets/2023-data/2023.html
- https://www.census.gov/programs-surveys/sipp/data/datasets/2024-data/2024.html

## Metadata

The workspace also contains official Census metadata for each year:

- `puYYYY_schema.json`
- `puYYYY_validate.xlsx`
- SIPP data dictionary or metadata PDF
- SIPP release notes
- SIPP users guide
- Census input example scripts where available

Schema files were copied from the prior local project after checking their byte size against the official Census schema URLs. Other metadata files were downloaded from official Census URLs.

## Manifests

Generated audit files:

- `temp/source_metadata/primary_zip_copy_audit.csv`
- `temp/source_metadata/schema_copy_audit.csv`
- `temp/source_metadata/metadata_download_status_2019_2024.csv`
- `temp/source_metadata/source_inventory.csv`
- `temp/source_metadata/file_manifest_sha256.csv`
- `temp/source_metadata/zip_contents_manifest.csv`

The zip contents manifest confirms that all seven primary zip files are readable.

## Current Boundary

This is a source-data staging workspace, not an analysis dataset.

Not yet populated:

- Full replicate weight files.
- Full longitudinal weight files.
- Extracted CSV files.
- Harmonized person-month files.
- Clean analysis-ready panels.
- Derived outputs from the prior US Insurance Project.
