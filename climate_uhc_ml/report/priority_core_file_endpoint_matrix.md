# Priority Core File Endpoint Matrix

Status: file-level official endpoint probe for priority raw acquisition. This
checks core file data-dictionary references and common World Bank/NADA
file-download route patterns. It reads only small response samples and does not
download raw microdata.

## Summary

| Metric | Value | Interpretation |
|---|---:|---|
| priority_core_file_endpoint_dataset_rows | 13 | Priority and backup datasets with core file endpoint matrices. |
| priority_core_file_endpoint_core_file_rows | 156 | Priority core file rows covered by the file endpoint matrix. |
| priority_core_file_endpoint_matrix_rows | 780 | File-level metadata references and download route probes. |
| priority_core_file_endpoint_metadata_reference_rows | 156 | Official data-dictionary source rows carried as metadata references. |
| priority_core_file_endpoint_probed_download_rows | 624 | Constructed file-level download routes probed without downloading raw files. |
| priority_core_file_endpoint_http_error_rows | 312 | File download routes returning HTTP errors rather than public raw payloads. |
| priority_core_file_endpoint_empty_download_rows | 312 | File download routes returning empty non-raw responses. |
| priority_core_file_endpoint_request_failed_rows | 0 | File download route probes that need retry. |
| priority_core_file_endpoint_raw_candidate_rows | 0 | Potential public raw file candidates detected; zero is required before treating credentialed route as necessary. |
| priority_core_file_endpoint_download_routes_without_public_raw_rows | 624 | Probed download route rows that did not expose public raw payloads. |
| priority_core_file_endpoint_credentialed_download_required_rows | 13 | Datasets whose core file route probes still require official credentialed raw acquisition. |
| priority_core_file_endpoint_handoff_readmes_written | 13 | Per-wave core file endpoint handoffs written. |
| modeling_gate_status | blocked | File endpoint evidence does not satisfy raw receipt, raw value verification, or climate-linkage gates. |
| priority_core_file_endpoint_classification_file_download_route_empty_not_raw_package | 312 | File endpoint classification count. |
| priority_core_file_endpoint_classification_file_download_route_http_error_not_public_raw | 312 | File endpoint classification count. |
| priority_core_file_endpoint_classification_public_file_metadata_reference_not_raw_package | 156 | File endpoint classification count. |

## Dataset Matrix

| acquisition_batch_rank | idno | core_file_rows | endpoint_rows | probed_download_endpoint_rows | raw_download_candidate_rows | download_routes_without_public_raw_rows | credentialed_download_required | core_file_endpoint_matrix_status |
|---|---|---|---|---|---|---|---|---|
| 1 | ETH_2021_ESPS-W5_v02_M | 12 | 60 | 48 | 0 | 48 | 1 | core_file_routes_confirmed_non_public_raw |
| 2 | ETH_2018_ESS_v04_M | 12 | 60 | 48 | 0 | 48 | 1 | core_file_routes_confirmed_non_public_raw |
| 3 | MWI_2007-2009_MTM_v01_M | 12 | 60 | 48 | 0 | 48 | 1 | core_file_routes_confirmed_non_public_raw |
| 4 | NGA_2012_GHSP-W2_v02_M | 12 | 60 | 48 | 0 | 48 | 1 | core_file_routes_confirmed_non_public_raw |
| 5 | NGA_2015_GHSP-W3_v02_M | 12 | 60 | 48 | 0 | 48 | 1 | core_file_routes_confirmed_non_public_raw |
| 6 | NGA_2010_GHSP-W1_v03_M | 12 | 60 | 48 | 0 | 48 | 1 | core_file_routes_confirmed_non_public_raw |
| 7 | TZA_2008_NPS-R1_v03_M | 12 | 60 | 48 | 0 | 48 | 1 | core_file_routes_confirmed_non_public_raw |
| 8 | TZA_2010_NPS-R2_v03_M | 12 | 60 | 48 | 0 | 48 | 1 | core_file_routes_confirmed_non_public_raw |
| 9 | TZA_2012_NPS-R3_v01_M | 12 | 60 | 48 | 0 | 48 | 1 | core_file_routes_confirmed_non_public_raw |
| 10 | UGA_2014_SAGE-EL_v01_M | 12 | 60 | 48 | 0 | 48 | 1 | core_file_routes_confirmed_non_public_raw |
| 11 | JAM_1997_SLC_v01_M | 12 | 60 | 48 | 0 | 48 | 1 | core_file_routes_confirmed_non_public_raw |
| 12 | KGZ_1993_KMPS_v01_M | 12 | 60 | 48 | 0 | 48 | 1 | core_file_routes_confirmed_non_public_raw |
| 13 | NPL_2010_LSS-III_v01_M | 12 | 60 | 48 | 0 | 48 | 1 | core_file_routes_confirmed_non_public_raw |

## Endpoint Preview

| acquisition_batch_rank | idno | core_file_rank | metadata_file_name | endpoint_name | http_status | file_endpoint_classification | raw_download_candidate |
|---|---|---|---|---|---|---|---|
| 1 | ETH_2021_ESPS-W5_v02_M | 1 | sect3_hh_w5.dta | catalog_download_fid_path | 404 | file_download_route_http_error_not_public_raw | 0 |
| 1 | ETH_2021_ESPS-W5_v02_M | 1 | sect3_hh_w5.dta | catalog_download_fid_query | 200 | file_download_route_empty_not_raw_package | 0 |
| 1 | ETH_2021_ESPS-W5_v02_M | 1 | sect3_hh_w5.dta | catalog_download_file_query | 200 | file_download_route_empty_not_raw_package | 0 |
| 1 | ETH_2021_ESPS-W5_v02_M | 1 | sect3_hh_w5.dta | data_dictionary_source_url |  | public_file_metadata_reference_not_raw_package | 0 |
| 1 | ETH_2021_ESPS-W5_v02_M | 1 | sect3_hh_w5.dta | index_catalog_download_fid_path | 404 | file_download_route_http_error_not_public_raw | 0 |
| 1 | ETH_2021_ESPS-W5_v02_M | 2 | sect04_com_w5.dta | catalog_download_fid_path | 404 | file_download_route_http_error_not_public_raw | 0 |
| 1 | ETH_2021_ESPS-W5_v02_M | 2 | sect04_com_w5.dta | catalog_download_fid_query | 200 | file_download_route_empty_not_raw_package | 0 |
| 1 | ETH_2021_ESPS-W5_v02_M | 2 | sect04_com_w5.dta | catalog_download_file_query | 200 | file_download_route_empty_not_raw_package | 0 |
| 1 | ETH_2021_ESPS-W5_v02_M | 2 | sect04_com_w5.dta | data_dictionary_source_url |  | public_file_metadata_reference_not_raw_package | 0 |
| 1 | ETH_2021_ESPS-W5_v02_M | 2 | sect04_com_w5.dta | index_catalog_download_fid_path | 404 | file_download_route_http_error_not_public_raw | 0 |
| 1 | ETH_2021_ESPS-W5_v02_M | 3 | sect06_com_w5.dta | catalog_download_fid_path | 404 | file_download_route_http_error_not_public_raw | 0 |
| 1 | ETH_2021_ESPS-W5_v02_M | 3 | sect06_com_w5.dta | catalog_download_fid_query | 200 | file_download_route_empty_not_raw_package | 0 |
| 1 | ETH_2021_ESPS-W5_v02_M | 3 | sect06_com_w5.dta | catalog_download_file_query | 200 | file_download_route_empty_not_raw_package | 0 |
| 1 | ETH_2021_ESPS-W5_v02_M | 3 | sect06_com_w5.dta | data_dictionary_source_url |  | public_file_metadata_reference_not_raw_package | 0 |
| 1 | ETH_2021_ESPS-W5_v02_M | 3 | sect06_com_w5.dta | index_catalog_download_fid_path | 404 | file_download_route_http_error_not_public_raw | 0 |
| 1 | ETH_2021_ESPS-W5_v02_M | 4 | sect11_com_w5.dta | catalog_download_fid_path | 404 | file_download_route_http_error_not_public_raw | 0 |
| 1 | ETH_2021_ESPS-W5_v02_M | 4 | sect11_com_w5.dta | catalog_download_fid_query | 200 | file_download_route_empty_not_raw_package | 0 |
| 1 | ETH_2021_ESPS-W5_v02_M | 4 | sect11_com_w5.dta | catalog_download_file_query | 200 | file_download_route_empty_not_raw_package | 0 |
| 1 | ETH_2021_ESPS-W5_v02_M | 4 | sect11_com_w5.dta | data_dictionary_source_url |  | public_file_metadata_reference_not_raw_package | 0 |
| 1 | ETH_2021_ESPS-W5_v02_M | 4 | sect11_com_w5.dta | index_catalog_download_fid_path | 404 | file_download_route_http_error_not_public_raw | 0 |
| 1 | ETH_2021_ESPS-W5_v02_M | 5 | sect3_pp_w5.dta | catalog_download_fid_path | 404 | file_download_route_http_error_not_public_raw | 0 |
| 1 | ETH_2021_ESPS-W5_v02_M | 5 | sect3_pp_w5.dta | catalog_download_fid_query | 200 | file_download_route_empty_not_raw_package | 0 |
| 1 | ETH_2021_ESPS-W5_v02_M | 5 | sect3_pp_w5.dta | catalog_download_file_query | 200 | file_download_route_empty_not_raw_package | 0 |
| 1 | ETH_2021_ESPS-W5_v02_M | 5 | sect3_pp_w5.dta | data_dictionary_source_url |  | public_file_metadata_reference_not_raw_package | 0 |
| 1 | ETH_2021_ESPS-W5_v02_M | 5 | sect3_pp_w5.dta | index_catalog_download_fid_path | 404 | file_download_route_http_error_not_public_raw | 0 |
| 1 | ETH_2021_ESPS-W5_v02_M | 6 | sect4_pp_w5.dta | catalog_download_fid_path | 404 | file_download_route_http_error_not_public_raw | 0 |
| 1 | ETH_2021_ESPS-W5_v02_M | 6 | sect4_pp_w5.dta | catalog_download_fid_query | 200 | file_download_route_empty_not_raw_package | 0 |
| 1 | ETH_2021_ESPS-W5_v02_M | 6 | sect4_pp_w5.dta | catalog_download_file_query | 200 | file_download_route_empty_not_raw_package | 0 |
| 1 | ETH_2021_ESPS-W5_v02_M | 6 | sect4_pp_w5.dta | data_dictionary_source_url |  | public_file_metadata_reference_not_raw_package | 0 |
| 1 | ETH_2021_ESPS-W5_v02_M | 6 | sect4_pp_w5.dta | index_catalog_download_fid_path | 404 | file_download_route_http_error_not_public_raw | 0 |
| 1 | ETH_2021_ESPS-W5_v02_M | 7 | sect7_pp_w5.dta | catalog_download_fid_path | 404 | file_download_route_http_error_not_public_raw | 0 |
| 1 | ETH_2021_ESPS-W5_v02_M | 7 | sect7_pp_w5.dta | catalog_download_fid_query | 200 | file_download_route_empty_not_raw_package | 0 |
| 1 | ETH_2021_ESPS-W5_v02_M | 7 | sect7_pp_w5.dta | catalog_download_file_query | 200 | file_download_route_empty_not_raw_package | 0 |
| 1 | ETH_2021_ESPS-W5_v02_M | 7 | sect7_pp_w5.dta | data_dictionary_source_url |  | public_file_metadata_reference_not_raw_package | 0 |
| 1 | ETH_2021_ESPS-W5_v02_M | 7 | sect7_pp_w5.dta | index_catalog_download_fid_path | 404 | file_download_route_http_error_not_public_raw | 0 |
| 1 | ETH_2021_ESPS-W5_v02_M | 8 | sect9_ph_w5.dta | catalog_download_fid_path | 404 | file_download_route_http_error_not_public_raw | 0 |
| 1 | ETH_2021_ESPS-W5_v02_M | 8 | sect9_ph_w5.dta | catalog_download_fid_query | 200 | file_download_route_empty_not_raw_package | 0 |
| 1 | ETH_2021_ESPS-W5_v02_M | 8 | sect9_ph_w5.dta | catalog_download_file_query | 200 | file_download_route_empty_not_raw_package | 0 |
| 1 | ETH_2021_ESPS-W5_v02_M | 8 | sect9_ph_w5.dta | data_dictionary_source_url |  | public_file_metadata_reference_not_raw_package | 0 |
| 1 | ETH_2021_ESPS-W5_v02_M | 8 | sect9_ph_w5.dta | index_catalog_download_fid_path | 404 | file_download_route_http_error_not_public_raw | 0 |
| 1 | ETH_2021_ESPS-W5_v02_M | 9 | sect11_ph_w5.dta | catalog_download_fid_path | 404 | file_download_route_http_error_not_public_raw | 0 |
| 1 | ETH_2021_ESPS-W5_v02_M | 9 | sect11_ph_w5.dta | catalog_download_fid_query | 200 | file_download_route_empty_not_raw_package | 0 |
| 1 | ETH_2021_ESPS-W5_v02_M | 9 | sect11_ph_w5.dta | catalog_download_file_query | 200 | file_download_route_empty_not_raw_package | 0 |
| 1 | ETH_2021_ESPS-W5_v02_M | 9 | sect11_ph_w5.dta | data_dictionary_source_url |  | public_file_metadata_reference_not_raw_package | 0 |
| 1 | ETH_2021_ESPS-W5_v02_M | 9 | sect11_ph_w5.dta | index_catalog_download_fid_path | 404 | file_download_route_http_error_not_public_raw | 0 |
| 1 | ETH_2021_ESPS-W5_v02_M | 10 | sect8_2_ls_w5.dta | catalog_download_fid_path | 404 | file_download_route_http_error_not_public_raw | 0 |
| 1 | ETH_2021_ESPS-W5_v02_M | 10 | sect8_2_ls_w5.dta | catalog_download_fid_query | 200 | file_download_route_empty_not_raw_package | 0 |
| 1 | ETH_2021_ESPS-W5_v02_M | 10 | sect8_2_ls_w5.dta | catalog_download_file_query | 200 | file_download_route_empty_not_raw_package | 0 |
| 1 | ETH_2021_ESPS-W5_v02_M | 10 | sect8_2_ls_w5.dta | data_dictionary_source_url |  | public_file_metadata_reference_not_raw_package | 0 |
| 1 | ETH_2021_ESPS-W5_v02_M | 10 | sect8_2_ls_w5.dta | index_catalog_download_fid_path | 404 | file_download_route_http_error_not_public_raw | 0 |

## Guardrail

File-level public metadata and empty/404 download routes are not raw package
receipt. Promotion still requires complete original raw package placement,
archive/direct file coverage, raw values and labels, units and recall periods,
missing-code and skip-pattern review, merge-key and survey-design checks,
timing/geography verification, and an accepted CHIRPS or ERA5 linkage route.

## Machine-Readable Outputs

- `temp/priority_core_file_endpoint_matrix.csv`
- `temp/priority_core_file_endpoint_dataset_matrix.csv`
- `result/priority_core_file_endpoint_matrix_summary.csv`
