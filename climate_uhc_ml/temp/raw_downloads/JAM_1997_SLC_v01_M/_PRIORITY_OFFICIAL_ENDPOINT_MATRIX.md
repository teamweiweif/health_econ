# Priority Official Endpoint Matrix

Dataset: JAM_1997_SLC_v01_M - Jamaica 1997

Status: metadata_api_confirmed_raw_access_gate_confirmed

Endpoint rows: 8

Public metadata endpoints: 4

Variable API endpoints: 1

Get-microdata access gates: 1

Raw download candidate endpoints: 0

Credentialed download required: 1

## Endpoint Preview

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

Guardrail: public API/metadata endpoints are metadata evidence only. They do
not replace the complete unchanged official raw package.
