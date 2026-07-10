# Malawi 2004 CHIRPS ADM2 Route Policy

Dataset: `MWI_2004_IHS-II_v01_M` - Malawi 2004-2005

This artifact selects and verifies a district-month CHIRPS route design for
Malawi 2004. It does not download CHIRPS rasters, does not extract climate
values, does not accept the promoted CHIRPS/ERA5 linkage gate, and does not
write promoted data.

## Summary

| metric | value | interpretation |
| --- | --- | --- |
| country_wave | MWI_2004_IHS-II_v01_M | Country-wave covered by the CHIRPS ADM2 route policy. |
| climate_route_policy_status | chirps_admin2_district_month_route_design_ready_extraction_validation_pending | Route design status before climate raster extraction. |
| route_design_ready | 1 | Whether raw timing, raw district labels, ADM2 boundary names, and CHIRPS download manifest form a coherent route design. |
| accepted_chirps_era5_route | 0 | The promoted climate gate remains closed until CHIRPS extraction and validation pass. |
| current_climate_linkage_gate_status | route_preflight_ready_needs_extraction_validation | Updated preflight status for Malawi 2004 climate linkage. |
| raw_district_rows | 26 | Raw Malawi 2004 district labels observed in household data. |
| boundary_adm2_features | 28 | ADM2 features in the local geoBoundaries Malawi boundary file. |
| raw_district_boundary_matches | 26 | Raw district labels matched to ADM2 boundary names after normalization. |
| raw_district_boundary_unmatched | 0 | Raw district labels not matched to ADM2 boundary names; must be zero before extraction. |
| boundary_no_sample_rows | 2 | ADM2 boundary districts with no sampled households in Malawi 2004. |
| boundary_no_sample_names | Likoma;Neno | Boundary districts present but absent from the raw sample. |
| interview_month_count | 13 | Distinct raw interview months. |
| interview_month_min | 2004-03 | Earliest raw interview month. |
| interview_month_max | 2005-03 | Latest raw interview month. |
| required_chirps_months | 24 | CHIRPS monthly files needed for 1, 3, 6, and 12 complete-month windows. |
| required_chirps_month_min | 2003-03 | Earliest required CHIRPS month. |
| required_chirps_month_max | 2005-02 | Latest required CHIRPS month. |
| boundary_file_sha256 | 5fe9b6313ee3eaf6d2b8a4579b7a7fa75dc1b16b9324a436f5a359da23527ea6 | Checksum of the local boundary file used for route validation; raw boundary file is not intended for GitHub publication. |
| data_write_gate_status | closed | No promoted household-climate data are written by this route policy. |

## Policy Rows

| policy_component | route_decision | route_status | next_action |
| --- | --- | --- | --- |
| rainfall_source | select_chirps_v2_africa_monthly_geotiff_for_precipitation | source_route_selected | Download listed monthly GeoTIFF files into temp/raw_downloads/climate_chirps/africa_monthly and compute checksums. |
| spatial_boundary_source | use_geoboundaries_mwi_adm2_as_district_boundary_candidate | boundary_file_cached_for_local_validation | Run zonal or raster extraction once geospatial dependencies and CHIRPS GeoTIFFs are available. |
| raw_district_crosswalk | map_raw_dist_labels_to_adm2_district_names_after_city_suffix_normalization | crosswalk_ready | Keep city/district combined labels assigned to parent district; keep Likoma and Neno as boundary districts with no sampled households. |
| temporal_window_plan | use_1_3_6_12_complete_month_windows_before_interview_month | download_manifest_ready | After CHIRPS download, aggregate district rainfall and build lag-window exposure columns. |
| promotion_stop_rule | keep_accepted_chirps_era5_route_closed_until_extraction_validation_passes | not_accepted_extraction_and_validation_pending | Do not write promoted household-climate data until CHIRPS values are extracted, units checked, district coverage validated, and lag windows reviewed. |

## District Crosswalk

| raw_dist_code | raw_dist_label | normalized_adm2_name | household_rows | boundary_match_status |
| --- | --- | --- | --- | --- |
| 101 | Chitipa | Chitipa | 240 | matched_to_geoboundaries_adm2 |
| 102 | Karonga | Karonga | 240 | matched_to_geoboundaries_adm2 |
| 103 | Nkhata Bay | Nkhata Bay | 240 | matched_to_geoboundaries_adm2 |
| 104 | Rumphi | Rumphi | 240 | matched_to_geoboundaries_adm2 |
| 105 | Mzimba/Mzuzu City | Mzimba | 720 | matched_to_geoboundaries_adm2 |
| 201 | Kasungu | Kasungu | 480 | matched_to_geoboundaries_adm2 |
| 202 | Nkhotakota | Nkhotakota | 240 | matched_to_geoboundaries_adm2 |
| 203 | Ntchisi | Ntchisi | 240 | matched_to_geoboundaries_adm2 |
| 204 | Dowa | Dowa | 480 | matched_to_geoboundaries_adm2 |
| 205 | Salima | Salima | 240 | matched_to_geoboundaries_adm2 |
| 206 | Lilongwe/Lilongwe City | Lilongwe | 1440 | matched_to_geoboundaries_adm2 |
| 207 | Mchinji | Mchinji | 240 | matched_to_geoboundaries_adm2 |
| 208 | Dedza | Dedza | 480 | matched_to_geoboundaries_adm2 |
| 209 | Ntcheu | Ntcheu | 480 | matched_to_geoboundaries_adm2 |
| 301 | Mangochi | Mangochi | 720 | matched_to_geoboundaries_adm2 |
| 302 | Machinga | Machinga | 480 | matched_to_geoboundaries_adm2 |
| 303 | Zomba/Zomba City | Zomba | 720 | matched_to_geoboundaries_adm2 |
| 304 | Chiradzulu | Chiradzulu | 240 | matched_to_geoboundaries_adm2 |
| 305 | Blantyre/Blantyre City | Blantyre | 720 | matched_to_geoboundaries_adm2 |
| 306 | Mwanza | Mwanza | 240 | matched_to_geoboundaries_adm2 |
| 307 | Thyolo | Thyolo | 480 | matched_to_geoboundaries_adm2 |
| 308 | Mulanje | Mulanje | 480 | matched_to_geoboundaries_adm2 |
| 309 | Phalombe | Phalombe | 240 | matched_to_geoboundaries_adm2 |
| 310 | Chikwawa | Chikwawa | 480 | matched_to_geoboundaries_adm2 |
| 311 | Nsanje | Nsanje | 240 | matched_to_geoboundaries_adm2 |
| 312 | Balaka | Balaka | 240 | matched_to_geoboundaries_adm2 |
|  |  | Likoma | 0 | boundary_present_no_raw_sample |
|  |  | Neno | 0 | boundary_present_no_raw_sample |

## CHIRPS Download Manifest Preview

| chirps_month | chirps_file | download_status |
| --- | --- | --- |
| 2003-03 | chirps-v2.0.2003.03.tif.gz | not_downloaded_source_url_verified |
| 2003-04 | chirps-v2.0.2003.04.tif.gz | not_downloaded_source_url_verified |
| 2003-05 | chirps-v2.0.2003.05.tif.gz | not_downloaded_source_url_verified |
| 2003-06 | chirps-v2.0.2003.06.tif.gz | not_downloaded_source_url_verified |
| 2003-07 | chirps-v2.0.2003.07.tif.gz | not_downloaded_source_url_verified |
| 2003-08 | chirps-v2.0.2003.08.tif.gz | not_downloaded_source_url_verified |
| 2003-09 | chirps-v2.0.2003.09.tif.gz | not_downloaded_source_url_verified |
| 2003-10 | chirps-v2.0.2003.10.tif.gz | not_downloaded_source_url_verified |
| 2003-11 | chirps-v2.0.2003.11.tif.gz | not_downloaded_source_url_verified |
| 2003-12 | chirps-v2.0.2003.12.tif.gz | not_downloaded_source_url_verified |
| 2004-01 | chirps-v2.0.2004.01.tif.gz | not_downloaded_source_url_verified |
| 2004-02 | chirps-v2.0.2004.02.tif.gz | not_downloaded_source_url_verified |
| 2004-03 | chirps-v2.0.2004.03.tif.gz | not_downloaded_source_url_verified |
| 2004-04 | chirps-v2.0.2004.04.tif.gz | not_downloaded_source_url_verified |
| 2004-05 | chirps-v2.0.2004.05.tif.gz | not_downloaded_source_url_verified |
| 2004-06 | chirps-v2.0.2004.06.tif.gz | not_downloaded_source_url_verified |
| 2004-07 | chirps-v2.0.2004.07.tif.gz | not_downloaded_source_url_verified |
| 2004-08 | chirps-v2.0.2004.08.tif.gz | not_downloaded_source_url_verified |
| 2004-09 | chirps-v2.0.2004.09.tif.gz | not_downloaded_source_url_verified |
| 2004-10 | chirps-v2.0.2004.10.tif.gz | not_downloaded_source_url_verified |
| 2004-11 | chirps-v2.0.2004.11.tif.gz | not_downloaded_source_url_verified |
| 2004-12 | chirps-v2.0.2004.12.tif.gz | not_downloaded_source_url_verified |
| 2005-01 | chirps-v2.0.2005.01.tif.gz | not_downloaded_source_url_verified |
| 2005-02 | chirps-v2.0.2005.02.tif.gz | not_downloaded_source_url_verified |

## Source Route

- Rainfall: CHIRPS v2.0 Africa monthly GeoTIFF files under `https://data.chc.ucsb.edu/products/CHIRPS-2.0/africa_monthly/tifs`.
- Boundary: geoBoundaries Malawi ADM2 GeoJSON from `https://www.geoboundaries.org/api/current/gbOpen/MWI/ADM2/`.
- Spatial unit: ADM2 district. Raw combined city labels are assigned to the
  parent district name before matching.
- Temporal unit: interview month, with 1, 3, 6, and 12 complete-month
  rainfall windows before the interview month.

## Still Blocked

- CHIRPS monthly rasters are not downloaded in this artifact.
- District rainfall values and lag-window exposures are not extracted.
- The promoted `accepted_chirps_era5_route` gate remains closed until raster
  extraction, unit checks, spatial coverage checks, and lag-window validation
  pass.
