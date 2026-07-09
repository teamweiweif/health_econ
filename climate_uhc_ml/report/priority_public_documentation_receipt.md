# Priority Public Documentation Receipt

Status: public documentation and metadata receipt for priority acquisition
waves. This step downloads or reuses official public pages, DDI/XML exports,
JSON metadata, data dictionaries, related-material pages, and listed PDF
documentation. It does not download raw microdata and does not bypass account,
terms, registration, or data-access agreement gates.

## Summary

| Metric | Value | Interpretation |
|---|---:|---|
| priority_public_documentation_dataset_rows | 13 | Priority and backup waves with public documentation receipt rows. |
| priority_public_documentation_resource_rows | 78 | Public documentation or metadata resources attempted or reused. |
| priority_public_documentation_saved_rows | 76 | Public documentation resources saved or reused locally. |
| priority_public_documentation_failed_rows | 0 | Public documentation resources that failed to fetch. |
| priority_public_documentation_core_complete_dataset_rows | 13 | Datasets with all core public documentation resource types saved. |
| priority_public_documentation_full_complete_dataset_rows | 11 | Datasets with core public resources plus PDF documentation saved. |
| priority_public_documentation_optional_pdf_missing_dataset_rows | 2 | Datasets where the optional PDF documentation resource was not listed or not saved. |
| priority_public_documentation_access_gate_rows | 13 | Datasets whose get-microdata page still shows login/register/terms gate language. |
| priority_public_documentation_saved_bytes | 92998600 | Total bytes in saved or reused public documentation snapshots. |
| priority_public_documentation_handoff_readmes_written | 13 | Per-wave public documentation receipt handoff README files written. |
| modeling_gate_status | blocked | Public documentation receipt does not satisfy raw value verification or climate-linkage promotion gates. |
| priority_public_documentation_receipt_status_missing_optional_url | 2 | Public documentation resource receipt status count. |
| priority_public_documentation_receipt_status_saved_existing | 63 | Public documentation resource receipt status count. |
| priority_public_documentation_receipt_status_saved_existing_access_probe | 13 | Public documentation resource receipt status count. |
| priority_public_documentation_resource_type_data_dictionary_html | 13 | Public documentation resource type count. |
| priority_public_documentation_resource_type_ddi_metadata | 13 | Public documentation resource type count. |
| priority_public_documentation_resource_type_get_microdata_html | 13 | Public documentation resource type count. |
| priority_public_documentation_resource_type_json_metadata | 13 | Public documentation resource type count. |
| priority_public_documentation_resource_type_pdf_documentation | 13 | Public documentation resource type count. |
| priority_public_documentation_resource_type_related_materials_html | 13 | Public documentation resource type count. |
| priority_public_documentation_dataset_status_complete_core_public_documentation_receipt_optional_pdf_unlisted_or_missing | 2 | Dataset-level public documentation receipt status count. |
| priority_public_documentation_dataset_status_complete_full_public_documentation_receipt | 11 | Dataset-level public documentation receipt status count. |

## Dataset Receipt

| acquisition_batch_rank | idno | country | wave | public_documentation_receipt_status | missing_core_resource_types | missing_optional_resource_types |
|---|---|---|---|---|---|---|
| 1 | ETH_2021_ESPS-W5_v02_M | Ethiopia | 2021-2022 | complete_full_public_documentation_receipt |  |  |
| 2 | ETH_2018_ESS_v04_M | Ethiopia | 2018-2019 | complete_full_public_documentation_receipt |  |  |
| 3 | MWI_2007-2009_MTM_v01_M | Malawi | 2007-2009 | complete_core_public_documentation_receipt_optional_pdf_unlisted_or_missing |  | pdf_documentation |
| 4 | NGA_2012_GHSP-W2_v02_M | Nigeria | 2012-2013 | complete_full_public_documentation_receipt |  |  |
| 5 | NGA_2015_GHSP-W3_v02_M | Nigeria | 2015-2016 | complete_full_public_documentation_receipt |  |  |
| 6 | NGA_2010_GHSP-W1_v03_M | Nigeria | 2010-2011 | complete_full_public_documentation_receipt |  |  |
| 7 | TZA_2008_NPS-R1_v03_M | Tanzania | 2008-2009 | complete_full_public_documentation_receipt |  |  |
| 8 | TZA_2010_NPS-R2_v03_M | Tanzania | 2010-2011 | complete_full_public_documentation_receipt |  |  |
| 9 | TZA_2012_NPS-R3_v01_M | Tanzania | 2012-2013 | complete_full_public_documentation_receipt |  |  |
| 10 | UGA_2014_SAGE-EL_v01_M | Uganda | 2014 | complete_full_public_documentation_receipt |  |  |
| 11 | JAM_1997_SLC_v01_M | Jamaica | 1997 | complete_full_public_documentation_receipt |  |  |
| 12 | KGZ_1993_KMPS_v01_M | Kyrgyz Republic | 1993 | complete_core_public_documentation_receipt_optional_pdf_unlisted_or_missing |  | pdf_documentation |
| 13 | NPL_2010_LSS-III_v01_M | Nepal | 2010-2011 | complete_full_public_documentation_receipt |  |  |

## Failed Or Missing Required Resources

No failed or missing required public documentation resources.

## Guardrails

- Public documentation snapshots support planning and variable verification only.
- A complete public documentation receipt is not a raw package receipt.
- Keep all priority country-waves out of `data/` until original raw packages,
  manual value/key/unit/skip-pattern verification, and CHIRPS/ERA5 linkage pass.

## Machine-Readable Outputs

- `temp/priority_public_documentation_receipt.csv`
- `temp/priority_public_documentation_dataset_receipt.csv`
- `result/priority_public_documentation_receipt_summary.csv`
