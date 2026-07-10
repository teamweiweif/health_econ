# Minimum Batch Endpoint Refresh

IDNO: `ETH_2018_ESS_v04_M`

Country-wave: Ethiopia 2018-2019

Official get-microdata URL: https://microdata.worldbank.org/catalog/3823/get-microdata

Endpoint refresh status: `metadata_confirmed_raw_access_gate_confirmed`

Credentialed download required: `1`

## Endpoint Results

| endpoint_name | http_status | endpoint_classification | raw_download_candidate | access_gate_detected |
|---|---|---|---|---|
| catalog_numeric_api | 400 | http_error_not_public_endpoint | 0 | 0 |
| catalog_idno_api | 200 | public_metadata_endpoint_not_raw_package | 0 | 0 |
| variables_idno_api | 200 | public_metadata_endpoint_not_raw_package | 0 | 1 |
| metadata_ddi_export | 200 | public_metadata_endpoint_not_raw_package | 0 | 1 |
| metadata_json_export | 200 | public_metadata_endpoint_not_raw_package | 0 | 0 |
| numeric_get_microdata_page | 200 | official_get_microdata_access_gate | 0 | 1 |
| numeric_download_page | 200 | empty_download_route_not_raw_package | 0 | 0 |
| idno_get_microdata_page | 200 | idno_route_returns_catalog_or_search_html_not_raw_package | 0 | 1 |

## Stop Rule

Endpoint evidence can prove public metadata and access gates, but it does not
prove raw package receipt. Do not write `data/` or run ML until the complete
official package is locally received, official DDI file names match, raw values
are verified, and timing/geography/climate linkage gates pass.
