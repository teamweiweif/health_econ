# First-Batch Public Documentation Audit

Status: public documentation coverage audit only. This checks whether official World Bank catalog pages, metadata exports, data dictionaries, related-material pages, and PDF documentation are saved locally for first-batch datasets. It does not download raw microdata and does not bypass account, request, registration, or terms workflows.

## Summary

| Metric | Value | Interpretation |
|---|---:|---|
| first_batch_documentation_dataset_rows | 10 | First-batch datasets audited for public documentation coverage. |
| first_batch_documentation_resource_rows | 60 | Dataset-resource documentation rows. |
| first_batch_documentation_saved_rows | 58 | Documentation resources saved or reused as local snapshots. |
| first_batch_documentation_failed_rows | 2 | Documentation resources that failed to fetch. |
| first_batch_documentation_complete_dataset_rows | 8 | Datasets with all six public documentation resource types saved or reused. |
| first_batch_documentation_pdf_missing_dataset_rows | 2 | Datasets without a saved PDF documentation endpoint. |
| first_batch_documentation_access_gate_rows | 10 | Datasets with access-gate language on the get-microdata HTML page. |
| coverage_status_failed_http | 2 | Documentation coverage status count. |
| coverage_status_saved | 29 | Documentation coverage status count. |
| coverage_status_saved_existing_worldbank_public_documentation | 29 | Documentation coverage status count. |
| resource_type_data_dictionary_html | 10 | Documentation resource type count. |
| resource_type_get_microdata_html | 10 | Documentation resource type count. |
| resource_type_metadata_ddi_xml | 10 | Documentation resource type count. |
| resource_type_metadata_json | 10 | Documentation resource type count. |
| resource_type_pdf_documentation | 10 | Documentation resource type count. |
| resource_type_related_materials_html | 10 | Documentation resource type count. |

## Coverage Status

| Coverage status | Count |
|---|---:|
| saved | 29 |
| saved_existing_worldbank_public_documentation | 29 |
| failed_http | 2 |

## Resource Types

| Resource type | Count |
|---|---:|
| get_microdata_html | 10 |
| metadata_ddi_xml | 10 |
| metadata_json | 10 |
| pdf_documentation | 10 |
| data_dictionary_html | 10 |
| related_materials_html | 10 |

## Dataset Coverage

| batch_rank | country | wave | idno | public_documentation_status | missing_resource_types |
|---|---|---|---|---|---|
| 1 | Albania | 2005 | ALB_2005_LSMS_v01_M | complete_public_documentation_snapshot |  |
| 2 | Ethiopia | 2021-2022 | ETH_2021_ESPS-W5_v02_M | complete_public_documentation_snapshot |  |
| 3 | Ethiopia | 2018-2019 | ETH_2018_ESS_v04_M | complete_public_documentation_snapshot |  |
| 4 | Jamaica | 1997 | JAM_1997_SLC_v01_M | complete_public_documentation_snapshot |  |
| 5 | Kyrgyz Republic | 1993 | KGZ_1993_KMPS_v01_M | incomplete_public_documentation_snapshot | pdf_documentation |
| 6 | Malawi | 2007-2009 | MWI_2007-2009_MTM_v01_M | incomplete_public_documentation_snapshot | pdf_documentation |
| 7 | Malawi | 2004-2005 | MWI_2004_IHS-II_v01_M | complete_public_documentation_snapshot |  |
| 8 | Nepal | 2010-2011 | NPL_2010_LSS-III_v01_M | complete_public_documentation_snapshot |  |
| 9 | Nigeria | 2012-2013 | NGA_2012_GHSP-W2_v02_M | complete_public_documentation_snapshot |  |
| 10 | Nigeria | 2015-2016 | NGA_2015_GHSP-W3_v02_M | complete_public_documentation_snapshot |  |

## Failed Or Missing Public Resources

| batch_rank | idno | resource_type | coverage_status | http_status | notes |
|---|---|---|---|---|---|
| 5 | KGZ_1993_KMPS_v01_M | pdf_documentation | failed_http | 500 | HTTP 500 |
| 6 | MWI_2007-2009_MTM_v01_M | pdf_documentation | failed_http | 500 | HTTP 500 |

## Guardrails

- Saved public documentation can support metadata and planning audits only.
- Raw survey files still must be obtained through the listed account/terms workflow and placed in `temp/raw_downloads/<IDNO>/`.
- Do not promote harmonization, outcomes, climate linkage, models, causal claims, or policy simulations from this documentation audit alone.

## Machine-Readable Outputs

- `temp/first_batch_public_documentation_audit.csv`
- `result/first_batch_public_documentation_summary.csv`
