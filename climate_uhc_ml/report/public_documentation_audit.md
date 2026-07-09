# Public Documentation Audit

Status: public World Bank documentation and metadata were snapshotted for priority gated datasets. This does not download or bypass raw microdata access controls.

## Coverage

- Priority World Bank datasets attempted: 20
- Resource rows attempted: 120
- Datasets with login/register/terms gate detected on Get Microdata page: 20

## Resource Status

| Status | Count |
|---|---:|
| saved | 119 |
| failed_http | 1 |

## Resource Types

| Resource type | Count |
|---|---:|
| get_microdata_html | 20 |
| metadata_ddi_xml | 20 |
| metadata_json | 20 |
| pdf_documentation | 20 |
| data_dictionary_html | 20 |
| related_materials_html | 20 |

## Dataset Summary

| Rank | IDNO | Catalog | Saved resources | Failed | Oversize | Access gate |
|---:|---|---:|---:|---:|---:|---|
| 1 | `ETH_2021_ESPS-W5_v02_M` | 6161 | 6 | 0 | 0 | 1 |
| 2 | `ETH_2018_ESS_v04_M` | 3823 | 6 | 0 | 0 | 1 |
| 3 | `MWI_2007-2009_MTM_v01_M` | 3462 | 5 | 1 | 0 | 1 |
| 4 | `MLI_2021_EHCVM-2_v01_M` | 6275 | 6 | 0 | 0 | 1 |
| 5 | `NER_2021_EHCVM-2_v01_M` | 6276 | 6 | 0 | 0 | 1 |
| 6 | `NGA_2012_GHSP-W2_v02_M` | 1952 | 6 | 0 | 0 | 1 |
| 7 | `NGA_2015_GHSP-W3_v02_M` | 2734 | 6 | 0 | 0 | 1 |
| 8 | `NGA_2010_GHSP-W1_v03_M` | 1002 | 6 | 0 | 0 | 1 |
| 9 | `TZA_2008_NPS-R1_v03_M` | 76 | 6 | 0 | 0 | 1 |
| 10 | `TZA_2010_NPS-R2_v03_M` | 1050 | 6 | 0 | 0 | 1 |
| 11 | `TZA_2012_NPS-R3_v01_M` | 2252 | 6 | 0 | 0 | 1 |
| 12 | `TZA_2014_NPS-R4_v03_M_v03_A_EXT` | 3455 | 6 | 0 | 0 | 1 |
| 13 | `TZA_2014_NPS-R4_v03_M` | 2862 | 6 | 0 | 0 | 1 |
| 14 | `TZA_2020_NPS-R5_v02_M` | 5639 | 6 | 0 | 0 | 1 |
| 15 | `UGA_2014_SAGE-EL_v01_M` | 2654 | 6 | 0 | 0 | 1 |
| 16 | `UGA_2012_SAGE-BL_v01_M` | 2652 | 6 | 0 | 0 | 1 |
| 17 | `UGA_2013_SAGE-ML_v01_M` | 2653 | 6 | 0 | 0 | 1 |
| 18 | `BEN_2021_EHCVM-2_v01_M` | 6272 | 6 | 0 | 0 | 1 |
| 19 | `CIV_2021_EHCVM-2_v01_M` | 6273 | 6 | 0 | 0 | 1 |
| 20 | `GNB_2021_EHCVM-2_v01_M` | 6274 | 6 | 0 | 0 | 1 |

## Files

- Machine-readable resource audit: `temp/worldbank_public_documentation_audit.csv`
- Dataset access-gate summary: `temp/worldbank_access_gate_summary.csv`
- Snapshots: `temp/source_snapshots/worldbank_public_documentation/`

## Guardrail

Rows in this audit are documentation and metadata snapshots only. Raw survey microdata must still be manually downloaded under permitted account/terms workflows into `temp/raw_downloads/` before harmonization or analysis.
