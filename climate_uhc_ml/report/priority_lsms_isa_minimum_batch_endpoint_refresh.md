# Priority LSMS-ISA Minimum Batch Endpoint Refresh

Status: official endpoint refresh for the 11 country-waves in the minimum
threshold batch. This probes World Bank catalog/API/metadata/get-microdata
routes and classifies public metadata endpoints, access gates, empty/non-raw
routes, and possible raw candidates.

It does not download raw microdata, accept terms, bypass login, verify values,
create harmonized datasets, or write `data/`.

## Summary

| Metric | Value | Interpretation |
|---|---:|---|
| priority_lsms_minimum_endpoint_dataset_rows | 11 | Minimum threshold batch country-waves with refreshed official endpoint probes. |
| priority_lsms_minimum_endpoint_country_rows | 6 | Countries represented in the minimum endpoint refresh. |
| priority_lsms_minimum_endpoint_rows | 88 | Official endpoint probes across the minimum threshold batch. |
| priority_lsms_minimum_endpoint_public_metadata_endpoint_rows | 44 | Dataset-level count of successful public metadata endpoint hits. |
| priority_lsms_minimum_endpoint_variable_api_dataset_rows | 11 | Minimum-batch datasets with a public variable metadata API endpoint. |
| priority_lsms_minimum_endpoint_get_microdata_gate_dataset_rows | 11 | Minimum-batch datasets whose official get-microdata endpoint shows an access gate. |
| priority_lsms_minimum_endpoint_raw_download_candidate_rows | 0 | Raw download candidate endpoints detected without accepting them as usable. |
| priority_lsms_minimum_endpoint_credentialed_download_required_rows | 11 | Minimum-batch datasets requiring credentialed download after endpoint refresh. |
| priority_lsms_minimum_endpoint_handoff_readmes_written | 11 | Per-wave endpoint-refresh handoffs written. |
| priority_lsms_minimum_endpoint_data_write_status | blocked_no_raw_package_receipt | Endpoint refresh never writes promoted data. |
| modeling_gate_status | blocked | Models remain blocked until 6 countries, 10 country-waves, and accepted CHIRPS/ERA5 linkage are value-verified. |
| priority_lsms_minimum_endpoint_classification_empty_download_route_not_raw_package | 11 | Endpoint classification count. |
| priority_lsms_minimum_endpoint_classification_http_error_not_public_endpoint | 11 | Endpoint classification count. |
| priority_lsms_minimum_endpoint_classification_idno_route_returns_catalog_or_search_html_not_raw_package | 11 | Endpoint classification count. |
| priority_lsms_minimum_endpoint_classification_official_get_microdata_access_gate | 11 | Endpoint classification count. |
| priority_lsms_minimum_endpoint_classification_public_metadata_endpoint_not_raw_package | 44 | Endpoint classification count. |

## Dataset Status

| threshold_sequence_rank | country | wave | idno | endpoint_rows | successful_public_metadata_endpoints | get_microdata_gate_endpoints | raw_download_candidate_endpoints | credentialed_download_required | endpoint_refresh_status |
|---|---|---|---|---|---|---|---|---|---|
| 1 | Ethiopia | 2021-2022 | ETH_2021_ESPS-W5_v02_M | 8 | 4 | 1 | 0 | 1 | metadata_confirmed_raw_access_gate_confirmed |
| 2 | Ethiopia | 2018-2019 | ETH_2018_ESS_v04_M | 8 | 4 | 1 | 0 | 1 | metadata_confirmed_raw_access_gate_confirmed |
| 3 | Malawi | 2004-2005 | MWI_2004_IHS-II_v01_M | 8 | 4 | 1 | 0 | 1 | metadata_confirmed_raw_access_gate_confirmed |
| 4 | Nigeria | 2012-2013 | NGA_2012_GHSP-W2_v02_M | 8 | 4 | 1 | 0 | 1 | metadata_confirmed_raw_access_gate_confirmed |
| 5 | Nigeria | 2015-2016 | NGA_2015_GHSP-W3_v02_M | 8 | 4 | 1 | 0 | 1 | metadata_confirmed_raw_access_gate_confirmed |
| 6 | Nigeria | 2010-2011 | NGA_2010_GHSP-W1_v03_M | 8 | 4 | 1 | 0 | 1 | metadata_confirmed_raw_access_gate_confirmed |
| 7 | Tanzania | 2008-2009 | TZA_2008_NPS-R1_v03_M | 8 | 4 | 1 | 0 | 1 | metadata_confirmed_raw_access_gate_confirmed |
| 8 | Tanzania | 2010-2011 | TZA_2010_NPS-R2_v03_M | 8 | 4 | 1 | 0 | 1 | metadata_confirmed_raw_access_gate_confirmed |
| 9 | Tanzania | 2012-2013 | TZA_2012_NPS-R3_v01_M | 8 | 4 | 1 | 0 | 1 | metadata_confirmed_raw_access_gate_confirmed |
| 10 | Uganda | 2019-2020 | UGA_2019_UNPS_v03_M | 8 | 4 | 1 | 0 | 1 | metadata_confirmed_raw_access_gate_confirmed |
| 11 | Nepal | 2010-2011 | NPL_2010_LSS-III_v01_M | 8 | 4 | 1 | 0 | 1 | metadata_confirmed_raw_access_gate_confirmed |

## Endpoint Preview

| threshold_sequence_rank | idno | endpoint_name | http_status | endpoint_classification | raw_download_candidate | access_gate_detected |
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
| 3 | MWI_2004_IHS-II_v01_M | catalog_numeric_api | 400 | http_error_not_public_endpoint | 0 | 0 |
| 3 | MWI_2004_IHS-II_v01_M | catalog_idno_api | 200 | public_metadata_endpoint_not_raw_package | 0 | 1 |
| 3 | MWI_2004_IHS-II_v01_M | variables_idno_api | 200 | public_metadata_endpoint_not_raw_package | 0 | 1 |
| 3 | MWI_2004_IHS-II_v01_M | metadata_ddi_export | 200 | public_metadata_endpoint_not_raw_package | 0 | 1 |
| 3 | MWI_2004_IHS-II_v01_M | metadata_json_export | 200 | public_metadata_endpoint_not_raw_package | 0 | 1 |
| 3 | MWI_2004_IHS-II_v01_M | numeric_get_microdata_page | 200 | official_get_microdata_access_gate | 0 | 1 |
| 3 | MWI_2004_IHS-II_v01_M | numeric_download_page | 200 | empty_download_route_not_raw_package | 0 | 0 |
| 3 | MWI_2004_IHS-II_v01_M | idno_get_microdata_page | 200 | idno_route_returns_catalog_or_search_html_not_raw_package | 0 | 1 |
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

## Outputs

- `temp/priority_lsms_isa_minimum_batch_endpoint_refresh.csv`
- `temp/priority_lsms_isa_minimum_batch_endpoint_dataset_status.csv`
- `result/priority_lsms_isa_minimum_batch_endpoint_refresh_summary.csv`
- `temp/raw_downloads/<IDNO>/_PRIORITY_LSMS_ISA_MINIMUM_BATCH_ENDPOINT_REFRESH.md`

## Guardrail

Public catalog, variable, DDI, and JSON routes are metadata endpoints only.
The numeric `get-microdata` route remains the official credentialed raw
acquisition route when an access gate is detected. Endpoint evidence alone
cannot satisfy raw package receipt, raw-value verification, climate linkage, or
analysis-ready gates.
