# Priority Official Endpoint Matrix

Status: official endpoint matrix for priority raw acquisition. This probes
World Bank catalog/API/metadata/get-microdata routes and classifies whether
they provide metadata, access-gated raw acquisition pages, empty/non-raw routes,
or possible raw download candidates. It does not download raw microdata.

## Summary

| Metric | Value | Interpretation |
|---|---:|---|
| priority_endpoint_matrix_dataset_rows | 13 | Priority and backup datasets with endpoint matrix rows. |
| priority_endpoint_matrix_endpoint_rows | 104 | Official endpoint probes across priority and backup datasets. |
| priority_endpoint_matrix_public_metadata_endpoint_rows | 52 | Dataset-level count of successful public metadata endpoint hits. |
| priority_endpoint_matrix_variable_api_dataset_rows | 12 | Datasets with a public variable metadata API endpoint. |
| priority_endpoint_matrix_get_microdata_gate_dataset_rows | 13 | Datasets whose official get-microdata endpoint shows an access gate. |
| priority_endpoint_matrix_raw_download_candidate_rows | 0 | Raw download candidate endpoints detected without accepting them as usable. |
| priority_endpoint_matrix_credentialed_download_required_rows | 13 | Datasets requiring credentialed download after endpoint matrix review. |
| priority_endpoint_matrix_handoff_readmes_written | 13 | Per-wave official endpoint matrix handoffs written. |
| modeling_gate_status | blocked | Endpoint matrix evidence does not satisfy raw receipt, raw value verification, or climate-linkage gates. |
| priority_endpoint_matrix_classification_empty_download_route_not_raw_package | 13 | Endpoint classification count. |
| priority_endpoint_matrix_classification_http_error_not_public_endpoint | 13 | Endpoint classification count. |
| priority_endpoint_matrix_classification_idno_route_returns_catalog_or_search_html_not_raw_package | 13 | Endpoint classification count. |
| priority_endpoint_matrix_classification_official_get_microdata_access_gate | 13 | Endpoint classification count. |
| priority_endpoint_matrix_classification_public_metadata_endpoint_not_raw_package | 52 | Endpoint classification count. |

## Dataset Matrix

| acquisition_batch_rank | idno | endpoint_rows | successful_public_metadata_endpoints | successful_variable_api_endpoints | get_microdata_gate_endpoints | raw_download_candidate_endpoints | credentialed_download_required | endpoint_matrix_status |
|---|---|---|---|---|---|---|---|---|
| 1 | ETH_2021_ESPS-W5_v02_M | 8 | 4 | 1 | 1 | 0 | 1 | metadata_api_confirmed_raw_access_gate_confirmed |
| 2 | ETH_2018_ESS_v04_M | 8 | 4 | 1 | 1 | 0 | 1 | metadata_api_confirmed_raw_access_gate_confirmed |
| 3 | MWI_2007-2009_MTM_v01_M | 8 | 4 | 0 | 1 | 0 | 1 | metadata_api_confirmed_raw_access_gate_confirmed |
| 4 | NGA_2012_GHSP-W2_v02_M | 8 | 4 | 1 | 1 | 0 | 1 | metadata_api_confirmed_raw_access_gate_confirmed |
| 5 | NGA_2015_GHSP-W3_v02_M | 8 | 4 | 1 | 1 | 0 | 1 | metadata_api_confirmed_raw_access_gate_confirmed |
| 6 | NGA_2010_GHSP-W1_v03_M | 8 | 4 | 1 | 1 | 0 | 1 | metadata_api_confirmed_raw_access_gate_confirmed |
| 7 | TZA_2008_NPS-R1_v03_M | 8 | 4 | 1 | 1 | 0 | 1 | metadata_api_confirmed_raw_access_gate_confirmed |
| 8 | TZA_2010_NPS-R2_v03_M | 8 | 4 | 1 | 1 | 0 | 1 | metadata_api_confirmed_raw_access_gate_confirmed |
| 9 | TZA_2012_NPS-R3_v01_M | 8 | 4 | 1 | 1 | 0 | 1 | metadata_api_confirmed_raw_access_gate_confirmed |
| 10 | UGA_2014_SAGE-EL_v01_M | 8 | 4 | 1 | 1 | 0 | 1 | metadata_api_confirmed_raw_access_gate_confirmed |
| 11 | JAM_1997_SLC_v01_M | 8 | 4 | 1 | 1 | 0 | 1 | metadata_api_confirmed_raw_access_gate_confirmed |
| 12 | KGZ_1993_KMPS_v01_M | 8 | 4 | 1 | 1 | 0 | 1 | metadata_api_confirmed_raw_access_gate_confirmed |
| 13 | NPL_2010_LSS-III_v01_M | 8 | 4 | 1 | 1 | 0 | 1 | metadata_api_confirmed_raw_access_gate_confirmed |

## Endpoint Preview

| acquisition_batch_rank | idno | endpoint_name | http_status | endpoint_classification | raw_download_candidate | access_gate_detected |
|---|---|---|---|---|---|---|
| 1 | ETH_2021_ESPS-W5_v02_M | catalog_numeric_api | 400 | http_error_not_public_endpoint | 0 | 0 |
| 1 | ETH_2021_ESPS-W5_v02_M | catalog_idno_api | 200 | public_metadata_endpoint_not_raw_package | 0 | 0 |
| 1 | ETH_2021_ESPS-W5_v02_M | variables_idno_api | 200 | public_metadata_endpoint_not_raw_package | 0 | 1 |
| 1 | ETH_2021_ESPS-W5_v02_M | metadata_ddi_export | 200 | public_metadata_endpoint_not_raw_package | 0 | 1 |
| 1 | ETH_2021_ESPS-W5_v02_M | metadata_json_export | 200 | public_metadata_endpoint_not_raw_package | 0 | 0 |
| 1 | ETH_2021_ESPS-W5_v02_M | numeric_get_microdata_page | 200 | official_get_microdata_access_gate | 0 | 1 |
| 1 | ETH_2021_ESPS-W5_v02_M | numeric_download_page | 200 | empty_download_route_not_raw_package | 0 | 0 |
| 1 | ETH_2021_ESPS-W5_v02_M | idno_get_microdata_page | 200 | idno_route_returns_catalog_or_search_html_not_raw_package | 0 | 1 |
| 2 | ETH_2018_ESS_v04_M | catalog_numeric_api | 400 | http_error_not_public_endpoint | 0 | 0 |
| 2 | ETH_2018_ESS_v04_M | catalog_idno_api | 200 | public_metadata_endpoint_not_raw_package | 0 | 0 |
| 2 | ETH_2018_ESS_v04_M | variables_idno_api | 200 | public_metadata_endpoint_not_raw_package | 0 | 1 |
| 2 | ETH_2018_ESS_v04_M | metadata_ddi_export | 200 | public_metadata_endpoint_not_raw_package | 0 | 1 |
| 2 | ETH_2018_ESS_v04_M | metadata_json_export | 200 | public_metadata_endpoint_not_raw_package | 0 | 0 |
| 2 | ETH_2018_ESS_v04_M | numeric_get_microdata_page | 200 | official_get_microdata_access_gate | 0 | 1 |
| 2 | ETH_2018_ESS_v04_M | numeric_download_page | 200 | empty_download_route_not_raw_package | 0 | 0 |
| 2 | ETH_2018_ESS_v04_M | idno_get_microdata_page | 200 | idno_route_returns_catalog_or_search_html_not_raw_package | 0 | 1 |
| 3 | MWI_2007-2009_MTM_v01_M | catalog_numeric_api | 400 | http_error_not_public_endpoint | 0 | 0 |
| 3 | MWI_2007-2009_MTM_v01_M | catalog_idno_api | 200 | public_metadata_endpoint_not_raw_package | 0 | 0 |
| 3 | MWI_2007-2009_MTM_v01_M | variables_idno_api | 200 | public_metadata_endpoint_not_raw_package | 0 | 0 |
| 3 | MWI_2007-2009_MTM_v01_M | metadata_ddi_export | 200 | public_metadata_endpoint_not_raw_package | 0 | 0 |
| 3 | MWI_2007-2009_MTM_v01_M | metadata_json_export | 200 | public_metadata_endpoint_not_raw_package | 0 | 0 |
| 3 | MWI_2007-2009_MTM_v01_M | numeric_get_microdata_page | 200 | official_get_microdata_access_gate | 0 | 1 |
| 3 | MWI_2007-2009_MTM_v01_M | numeric_download_page | 200 | empty_download_route_not_raw_package | 0 | 0 |
| 3 | MWI_2007-2009_MTM_v01_M | idno_get_microdata_page | 200 | idno_route_returns_catalog_or_search_html_not_raw_package | 0 | 1 |
| 4 | NGA_2012_GHSP-W2_v02_M | catalog_numeric_api | 400 | http_error_not_public_endpoint | 0 | 0 |
| 4 | NGA_2012_GHSP-W2_v02_M | catalog_idno_api | 200 | public_metadata_endpoint_not_raw_package | 0 | 0 |
| 4 | NGA_2012_GHSP-W2_v02_M | variables_idno_api | 200 | public_metadata_endpoint_not_raw_package | 0 | 1 |
| 4 | NGA_2012_GHSP-W2_v02_M | metadata_ddi_export | 200 | public_metadata_endpoint_not_raw_package | 0 | 0 |
| 4 | NGA_2012_GHSP-W2_v02_M | metadata_json_export | 200 | public_metadata_endpoint_not_raw_package | 0 | 0 |
| 4 | NGA_2012_GHSP-W2_v02_M | numeric_get_microdata_page | 200 | official_get_microdata_access_gate | 0 | 1 |
| 4 | NGA_2012_GHSP-W2_v02_M | numeric_download_page | 200 | empty_download_route_not_raw_package | 0 | 0 |
| 4 | NGA_2012_GHSP-W2_v02_M | idno_get_microdata_page | 200 | idno_route_returns_catalog_or_search_html_not_raw_package | 0 | 1 |
| 5 | NGA_2015_GHSP-W3_v02_M | catalog_numeric_api | 400 | http_error_not_public_endpoint | 0 | 0 |
| 5 | NGA_2015_GHSP-W3_v02_M | catalog_idno_api | 200 | public_metadata_endpoint_not_raw_package | 0 | 0 |
| 5 | NGA_2015_GHSP-W3_v02_M | variables_idno_api | 200 | public_metadata_endpoint_not_raw_package | 0 | 1 |
| 5 | NGA_2015_GHSP-W3_v02_M | metadata_ddi_export | 200 | public_metadata_endpoint_not_raw_package | 0 | 0 |
| 5 | NGA_2015_GHSP-W3_v02_M | metadata_json_export | 200 | public_metadata_endpoint_not_raw_package | 0 | 0 |
| 5 | NGA_2015_GHSP-W3_v02_M | numeric_get_microdata_page | 200 | official_get_microdata_access_gate | 0 | 1 |
| 5 | NGA_2015_GHSP-W3_v02_M | numeric_download_page | 200 | empty_download_route_not_raw_package | 0 | 0 |
| 5 | NGA_2015_GHSP-W3_v02_M | idno_get_microdata_page | 200 | idno_route_returns_catalog_or_search_html_not_raw_package | 0 | 1 |

## Guardrail

Public IDNO catalog, variable, DDI, and JSON routes are metadata endpoints. They
are useful for variable screening and acquisition planning, but they are not the
complete original raw package. The official numeric get-microdata page remains
the credentialed raw acquisition route when an access gate is present.

## Machine-Readable Outputs

- `temp/priority_official_endpoint_matrix.csv`
- `temp/priority_official_endpoint_dataset_matrix.csv`
- `result/priority_official_endpoint_matrix_summary.csv`
