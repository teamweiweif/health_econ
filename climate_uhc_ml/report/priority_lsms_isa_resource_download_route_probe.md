# Priority LSMS-ISA Resource Download Route Probe

Status: bounded resource-level route-family smoke test for the 10 manual-download packets.

The probe constructs official World Bank catalog file-id download and data-dictionary URL patterns for up to four core files per dataset. It reads only a limited response sample, does not save raw payloads, does not use cookies or private headers, and does not write promoted `data/`.

This is not a substitute for official credentialed package acquisition. It is a fail-closed evidence layer showing whether common public resource routes expose accepted raw payloads.

## Summary

- Datasets covered: 10
- Sampled core files: 40
- Route rows probed: 240
- Raw payload candidates: 0
- Access-gate rows: 80
- Data-dictionary HTML rows: 80
- HTTP-error rows: 160
- Data-write gate: blocked_no_data_write
- Modeling gate: blocked

## Dataset Route Status

| download_rank | country | wave | idno | sampled_files | route_rows | raw_payload_candidates | access_gate_rows | data_dictionary_html_rows | http_error_rows |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 2 | Ethiopia | 2018-2019 | ETH_2018_ESS_v04_M | 4 | 24 | 0 | 8 | 8 | 16 |
| 1 | Ethiopia | 2021-2022 | ETH_2021_ESPS-W5_v02_M | 4 | 24 | 0 | 8 | 8 | 16 |
| 5 | Nigeria | 2010-2011 | NGA_2010_GHSP-W1_v03_M | 4 | 24 | 0 | 8 | 8 | 16 |
| 3 | Nigeria | 2012-2013 | NGA_2012_GHSP-W2_v02_M | 4 | 24 | 0 | 8 | 8 | 16 |
| 4 | Nigeria | 2015-2016 | NGA_2015_GHSP-W3_v02_M | 4 | 24 | 0 | 8 | 8 | 16 |
| 10 | Nepal | 2010-2011 | NPL_2010_LSS-III_v01_M | 4 | 24 | 0 | 8 | 8 | 16 |
| 6 | Tanzania | 2008-2009 | TZA_2008_NPS-R1_v03_M | 4 | 24 | 0 | 8 | 8 | 16 |
| 7 | Tanzania | 2010-2011 | TZA_2010_NPS-R2_v03_M | 4 | 24 | 0 | 8 | 8 | 16 |
| 8 | Tanzania | 2012-2013 | TZA_2012_NPS-R3_v01_M | 4 | 24 | 0 | 8 | 8 | 16 |
| 9 | Uganda | 2019-2020 | UGA_2019_UNPS_v03_M | 4 | 24 | 0 | 8 | 8 | 16 |

## Route Sample

| download_rank | idno | file_id | file_name | route_name | http_status | route_classification | raw_payload_candidate |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | ETH_2021_ESPS-W5_v02_M | F1 | sect_cover_hh_w5.dta | catalog_download_file_id_path | 404 | resource_http_error | 0 |
| 1 | ETH_2021_ESPS-W5_v02_M | F1 | sect_cover_hh_w5.dta | index_catalog_download_file_id_path | 404 | resource_http_error | 0 |
| 1 | ETH_2021_ESPS-W5_v02_M | F1 | sect_cover_hh_w5.dta | catalog_download_file_id_filename_query | 404 | resource_http_error | 0 |
| 1 | ETH_2021_ESPS-W5_v02_M | F1 | sect_cover_hh_w5.dta | index_catalog_download_file_id_filename_query | 404 | resource_http_error | 0 |
| 1 | ETH_2021_ESPS-W5_v02_M | F1 | sect_cover_hh_w5.dta | catalog_data_dictionary_file_id_filename_query | 200 | resource_data_dictionary_html_not_raw | 0 |
| 1 | ETH_2021_ESPS-W5_v02_M | F1 | sect_cover_hh_w5.dta | index_catalog_data_dictionary_file_id_filename_query | 200 | resource_data_dictionary_html_not_raw | 0 |
| 1 | ETH_2021_ESPS-W5_v02_M | F66 | cons_agg_w5.dta | catalog_download_file_id_path | 404 | resource_http_error | 0 |
| 1 | ETH_2021_ESPS-W5_v02_M | F66 | cons_agg_w5.dta | index_catalog_download_file_id_path | 404 | resource_http_error | 0 |
| 1 | ETH_2021_ESPS-W5_v02_M | F66 | cons_agg_w5.dta | catalog_download_file_id_filename_query | 404 | resource_http_error | 0 |
| 1 | ETH_2021_ESPS-W5_v02_M | F66 | cons_agg_w5.dta | index_catalog_download_file_id_filename_query | 404 | resource_http_error | 0 |
| 1 | ETH_2021_ESPS-W5_v02_M | F66 | cons_agg_w5.dta | catalog_data_dictionary_file_id_filename_query | 200 | resource_data_dictionary_html_not_raw | 0 |
| 1 | ETH_2021_ESPS-W5_v02_M | F66 | cons_agg_w5.dta | index_catalog_data_dictionary_file_id_filename_query | 200 | resource_data_dictionary_html_not_raw | 0 |
| 1 | ETH_2021_ESPS-W5_v02_M | F4 | sect3_hh_w5.dta | catalog_download_file_id_path | 404 | resource_http_error | 0 |
| 1 | ETH_2021_ESPS-W5_v02_M | F4 | sect3_hh_w5.dta | index_catalog_download_file_id_path | 404 | resource_http_error | 0 |
| 1 | ETH_2021_ESPS-W5_v02_M | F4 | sect3_hh_w5.dta | catalog_download_file_id_filename_query | 404 | resource_http_error | 0 |
| 1 | ETH_2021_ESPS-W5_v02_M | F4 | sect3_hh_w5.dta | index_catalog_download_file_id_filename_query | 404 | resource_http_error | 0 |
| 1 | ETH_2021_ESPS-W5_v02_M | F4 | sect3_hh_w5.dta | catalog_data_dictionary_file_id_filename_query | 200 | resource_data_dictionary_html_not_raw | 0 |
| 1 | ETH_2021_ESPS-W5_v02_M | F4 | sect3_hh_w5.dta | index_catalog_data_dictionary_file_id_filename_query | 200 | resource_data_dictionary_html_not_raw | 0 |
| 1 | ETH_2021_ESPS-W5_v02_M | F2 | sect1_hh_w5.dta | catalog_download_file_id_path | 404 | resource_http_error | 0 |
| 1 | ETH_2021_ESPS-W5_v02_M | F2 | sect1_hh_w5.dta | index_catalog_download_file_id_path | 404 | resource_http_error | 0 |
| 1 | ETH_2021_ESPS-W5_v02_M | F2 | sect1_hh_w5.dta | catalog_download_file_id_filename_query | 404 | resource_http_error | 0 |
| 1 | ETH_2021_ESPS-W5_v02_M | F2 | sect1_hh_w5.dta | index_catalog_download_file_id_filename_query | 404 | resource_http_error | 0 |
| 1 | ETH_2021_ESPS-W5_v02_M | F2 | sect1_hh_w5.dta | catalog_data_dictionary_file_id_filename_query | 200 | resource_data_dictionary_html_not_raw | 0 |
| 1 | ETH_2021_ESPS-W5_v02_M | F2 | sect1_hh_w5.dta | index_catalog_data_dictionary_file_id_filename_query | 200 | resource_data_dictionary_html_not_raw | 0 |
| 2 | ETH_2018_ESS_v04_M | F39 | sect_cover_ph_w4.dta | catalog_download_file_id_path | 404 | resource_http_error | 0 |
| 2 | ETH_2018_ESS_v04_M | F39 | sect_cover_ph_w4.dta | index_catalog_download_file_id_path | 404 | resource_http_error | 0 |
| 2 | ETH_2018_ESS_v04_M | F39 | sect_cover_ph_w4.dta | catalog_download_file_id_filename_query | 404 | resource_http_error | 0 |
| 2 | ETH_2018_ESS_v04_M | F39 | sect_cover_ph_w4.dta | index_catalog_download_file_id_filename_query | 404 | resource_http_error | 0 |
| 2 | ETH_2018_ESS_v04_M | F39 | sect_cover_ph_w4.dta | catalog_data_dictionary_file_id_filename_query | 200 | resource_data_dictionary_html_not_raw | 0 |
| 2 | ETH_2018_ESS_v04_M | F39 | sect_cover_ph_w4.dta | index_catalog_data_dictionary_file_id_filename_query | 200 | resource_data_dictionary_html_not_raw | 0 |
| 2 | ETH_2018_ESS_v04_M | F14 | sect7a_hh_w4.dta | catalog_download_file_id_path | 404 | resource_http_error | 0 |
| 2 | ETH_2018_ESS_v04_M | F14 | sect7a_hh_w4.dta | index_catalog_download_file_id_path | 404 | resource_http_error | 0 |
| 2 | ETH_2018_ESS_v04_M | F14 | sect7a_hh_w4.dta | catalog_download_file_id_filename_query | 404 | resource_http_error | 0 |
| 2 | ETH_2018_ESS_v04_M | F14 | sect7a_hh_w4.dta | index_catalog_download_file_id_filename_query | 404 | resource_http_error | 0 |
| 2 | ETH_2018_ESS_v04_M | F14 | sect7a_hh_w4.dta | catalog_data_dictionary_file_id_filename_query | 200 | resource_data_dictionary_html_not_raw | 0 |
| 2 | ETH_2018_ESS_v04_M | F14 | sect7a_hh_w4.dta | index_catalog_data_dictionary_file_id_filename_query | 200 | resource_data_dictionary_html_not_raw | 0 |
| 2 | ETH_2018_ESS_v04_M | F4 | sect3_hh_w4.dta | catalog_download_file_id_path | 404 | resource_http_error | 0 |
| 2 | ETH_2018_ESS_v04_M | F4 | sect3_hh_w4.dta | index_catalog_download_file_id_path | 404 | resource_http_error | 0 |
| 2 | ETH_2018_ESS_v04_M | F4 | sect3_hh_w4.dta | catalog_download_file_id_filename_query | 404 | resource_http_error | 0 |
| 2 | ETH_2018_ESS_v04_M | F4 | sect3_hh_w4.dta | index_catalog_download_file_id_filename_query | 404 | resource_http_error | 0 |
| 2 | ETH_2018_ESS_v04_M | F4 | sect3_hh_w4.dta | catalog_data_dictionary_file_id_filename_query | 200 | resource_data_dictionary_html_not_raw | 0 |
| 2 | ETH_2018_ESS_v04_M | F4 | sect3_hh_w4.dta | index_catalog_data_dictionary_file_id_filename_query | 200 | resource_data_dictionary_html_not_raw | 0 |
| 2 | ETH_2018_ESS_v04_M | F2 | sect1_hh_w4.dta | catalog_download_file_id_path | 404 | resource_http_error | 0 |
| 2 | ETH_2018_ESS_v04_M | F2 | sect1_hh_w4.dta | index_catalog_download_file_id_path | 404 | resource_http_error | 0 |
| 2 | ETH_2018_ESS_v04_M | F2 | sect1_hh_w4.dta | catalog_download_file_id_filename_query | 404 | resource_http_error | 0 |
| 2 | ETH_2018_ESS_v04_M | F2 | sect1_hh_w4.dta | index_catalog_download_file_id_filename_query | 404 | resource_http_error | 0 |
| 2 | ETH_2018_ESS_v04_M | F2 | sect1_hh_w4.dta | catalog_data_dictionary_file_id_filename_query | 200 | resource_data_dictionary_html_not_raw | 0 |
| 2 | ETH_2018_ESS_v04_M | F2 | sect1_hh_w4.dta | index_catalog_data_dictionary_file_id_filename_query | 200 | resource_data_dictionary_html_not_raw | 0 |
| 3 | NGA_2012_GHSP-W2_v02_M | F121 | HHTrack | catalog_download_file_id_path | 404 | resource_http_error | 0 |
| 3 | NGA_2012_GHSP-W2_v02_M | F121 | HHTrack | index_catalog_download_file_id_path | 404 | resource_http_error | 0 |
| 3 | NGA_2012_GHSP-W2_v02_M | F121 | HHTrack | catalog_download_file_id_filename_query | 404 | resource_http_error | 0 |
| 3 | NGA_2012_GHSP-W2_v02_M | F121 | HHTrack | index_catalog_download_file_id_filename_query | 404 | resource_http_error | 0 |
| 3 | NGA_2012_GHSP-W2_v02_M | F121 | HHTrack | catalog_data_dictionary_file_id_filename_query | 200 | resource_data_dictionary_html_not_raw | 0 |
| 3 | NGA_2012_GHSP-W2_v02_M | F121 | HHTrack | index_catalog_data_dictionary_file_id_filename_query | 200 | resource_data_dictionary_html_not_raw | 0 |
| 3 | NGA_2012_GHSP-W2_v02_M | F119 | cons_agg_wave2_visit1 | catalog_download_file_id_path | 404 | resource_http_error | 0 |
| 3 | NGA_2012_GHSP-W2_v02_M | F119 | cons_agg_wave2_visit1 | index_catalog_download_file_id_path | 404 | resource_http_error | 0 |
| 3 | NGA_2012_GHSP-W2_v02_M | F119 | cons_agg_wave2_visit1 | catalog_download_file_id_filename_query | 404 | resource_http_error | 0 |
| 3 | NGA_2012_GHSP-W2_v02_M | F119 | cons_agg_wave2_visit1 | index_catalog_download_file_id_filename_query | 404 | resource_http_error | 0 |
| 3 | NGA_2012_GHSP-W2_v02_M | F119 | cons_agg_wave2_visit1 | catalog_data_dictionary_file_id_filename_query | 200 | resource_data_dictionary_html_not_raw | 0 |
| 3 | NGA_2012_GHSP-W2_v02_M | F119 | cons_agg_wave2_visit1 | index_catalog_data_dictionary_file_id_filename_query | 200 | resource_data_dictionary_html_not_raw | 0 |
| ... | ... | ... | ... | ... | ... | ... | ... |

## Guardrails

- No raw files are saved.
- No cookies, tokens, private headers, or user credentials are read.
- No promoted dataset is written.
- The result cannot promote a wave; it can only support the access-route decision.
