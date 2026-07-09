# Priority Official Download Dossier

Status: official-source download and documentation dossier. This does not
download restricted microdata and does not bypass login, registration, terms,
or data-access agreement gates.

## Summary

| Metric | Value | Interpretation |
|---|---:|---|
| priority_official_download_dossier_rows | 13 | Priority and backup waves with official download dossiers. |
| priority_official_full_file_inventory_rows | 965 | Full official metadata file rows for priority and backup waves. |
| priority_official_priority_core_file_rows | 156 | Rows from the full metadata inventory that also appear in the core priority file queue. |
| priority_official_documentation_link_rows | 100 | Official metadata/documentation/access workflow links captured for the dossiers. |
| priority_official_pdf_documentation_links | 11 | PDF documentation links captured. |
| priority_official_ddi_metadata_links | 13 | DDI metadata export links captured. |
| priority_official_json_metadata_links | 13 | JSON metadata export links captured. |
| priority_official_data_dictionary_links | 13 | Data dictionary links captured. |
| priority_official_no_original_package_rows | 13 | Dossiers still blocked because no original raw package is present. |
| priority_official_receipt_candidates | 0 | Dossiers with receipt candidates ready for downstream audits. |
| modeling_gate_status | blocked | Models remain blocked until promoted registry thresholds and accepted CHIRPS/ERA5 linkage pass. |
| priority_official_dossier_status_blocked_official_access_required_no_original_package | 13 | Download dossier status count. |

## Dataset Dossiers

| acquisition_batch_rank | idno | country | wave | metadata_full_file_rows | priority_core_file_rows | receipt_original_file_rows | receipt_priority_targets_missing | complete_package_dossier_status |
|---|---|---|---|---|---|---|---|---|
| 1 | ETH_2021_ESPS-W5_v02_M | Ethiopia | 2021-2022 | 68 | 12 | 0 | 12 | blocked_official_access_required_no_original_package |
| 2 | ETH_2018_ESS_v04_M | Ethiopia | 2018-2019 | 68 | 12 | 0 | 12 | blocked_official_access_required_no_original_package |
| 3 | MWI_2007-2009_MTM_v01_M | Malawi | 2007-2009 | 118 | 12 | 0 | 12 | blocked_official_access_required_no_original_package |
| 4 | NGA_2012_GHSP-W2_v02_M | Nigeria | 2012-2013 | 103 | 12 | 0 | 12 | blocked_official_access_required_no_original_package |
| 5 | NGA_2015_GHSP-W3_v02_M | Nigeria | 2015-2016 | 104 | 12 | 0 | 12 | blocked_official_access_required_no_original_package |
| 6 | NGA_2010_GHSP-W1_v03_M | Nigeria | 2010-2011 | 99 | 12 | 0 | 12 | blocked_official_access_required_no_original_package |
| 7 | TZA_2008_NPS-R1_v03_M | Tanzania | 2008-2009 | 61 | 12 | 0 | 12 | blocked_official_access_required_no_original_package |
| 8 | TZA_2010_NPS-R2_v03_M | Tanzania | 2010-2011 | 95 | 12 | 0 | 12 | blocked_official_access_required_no_original_package |
| 9 | TZA_2012_NPS-R3_v01_M | Tanzania | 2012-2013 | 80 | 12 | 0 | 12 | blocked_official_access_required_no_original_package |
| 10 | UGA_2014_SAGE-EL_v01_M | Uganda | 2014 | 35 | 12 | 0 | 12 | blocked_official_access_required_no_original_package |
| 11 | JAM_1997_SLC_v01_M | Jamaica | 1997 | 68 | 12 | 0 | 12 | blocked_official_access_required_no_original_package |
| 12 | KGZ_1993_KMPS_v01_M | Kyrgyz Republic | 1993 | 15 | 12 | 0 | 12 | blocked_official_access_required_no_original_package |
| 13 | NPL_2010_LSS-III_v01_M | Nepal | 2010-2011 | 51 | 12 | 0 | 12 | blocked_official_access_required_no_original_package |

## Rule

Use these dossiers to obtain complete unchanged official raw packages and
documentation through the permitted access workflow. After files are placed
under `temp/raw_downloads/<IDNO>/`, rerun the receipt, archive, schema, manual
verification, climate-linkage, promoted-data, bundle, and validation gates.

## Machine-Readable Outputs

- `temp/priority_official_download_dossier.csv`
- `temp/priority_official_full_file_inventory.csv`
- `temp/priority_official_documentation_links.csv`
- `result/priority_official_download_dossier_summary.csv`
