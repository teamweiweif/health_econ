# Priority Climate Linkage Preflight

Status: fail-closed climate-linkage preflight for the 10-wave priority raw
acquisition batch and sixth-country backup waves. This report does not extract
climate data, does not accept a CHIRPS/ERA5 route, and does not write any
climate-linked dataset into `data/`.

## Summary

| Metric | Value | Interpretation |
|---|---:|---|
| priority_climate_preflight_rows | 13 | Priority acquisition and backup waves with climate-linkage preflight rows. |
| priority_climate_preflight_priority_10_rows | 10 | Immediate priority waves covered by climate preflight. |
| priority_climate_preflight_priority_10_countries | 5 | Priority countries covered by climate preflight. |
| priority_climate_preflight_backup_rows | 3 | Sixth-country backup rows covered by climate preflight. |
| priority_climate_requirement_rows | 143 | Filtered climate linkage requirement rows for priority acquisition waves. |
| priority_chirps_era5_source_route_ready_rows | 13 | Rows where CHIRPS/ERA5 source probes are ready at source-documentation level. |
| priority_accepted_chirps_era5_route_rows | 0 | Rows with accepted CHIRPS/ERA5 linkage route after raw timing/geography and validation. Must remain zero until raw gates pass. |
| priority_route_preflight_ready_needs_extraction_rows | 0 | Rows where raw timing/geography and source route design are ready but climate extraction/validation is still pending. |
| priority_climate_blocked_raw_timing_geography_rows | 13 | Rows blocked because raw timing/geography have not been verified even though source probes are ready. |
| priority_climate_handoff_readmes_written | 13 | Per-wave climate handoff README files written under temp/raw_downloads. |
| climate_source_route_groups_ready | 3 | Ready source groups among CHIRPS, ERA5, and NASA POWER. |
| modeling_gate_status | blocked | Models remain blocked until promoted registry thresholds and accepted climate linkage pass. |

## Current Climate Gate Status

| Gate status | Waves |
|---|---:|
| `blocked_raw_timing_geography_not_verified_sources_ready` | 13 |

## Wave-Level Preflight

| acquisition_batch_rank | batch_role | country | wave | idno | source_route_preflight_status | current_climate_linkage_gate_status | accepted_chirps_era5_route_status | handoff_readme |
|---|---|---|---|---|---|---|---|---|
| 1 | priority_10_wave_batch | Ethiopia | 2021-2022 | ETH_2021_ESPS-W5_v02_M | primary_chirps_era5_and_fallback_sources_probe_ready | blocked_raw_timing_geography_not_verified_sources_ready | not_accepted_raw_timing_geography_unverified | temp/raw_downloads/ETH_2021_ESPS-W5_v02_M/_PRIORITY_CLIMATE_LINKAGE_HANDOFF.md |
| 2 | priority_10_wave_batch | Ethiopia | 2018-2019 | ETH_2018_ESS_v04_M | primary_chirps_era5_and_fallback_sources_probe_ready | blocked_raw_timing_geography_not_verified_sources_ready | not_accepted_raw_timing_geography_unverified | temp/raw_downloads/ETH_2018_ESS_v04_M/_PRIORITY_CLIMATE_LINKAGE_HANDOFF.md |
| 3 | priority_10_wave_batch | Malawi | 2007-2009 | MWI_2007-2009_MTM_v01_M | primary_chirps_era5_and_fallback_sources_probe_ready | blocked_raw_timing_geography_not_verified_sources_ready | not_accepted_raw_timing_geography_unverified | temp/raw_downloads/MWI_2007-2009_MTM_v01_M/_PRIORITY_CLIMATE_LINKAGE_HANDOFF.md |
| 4 | priority_10_wave_batch | Nigeria | 2012-2013 | NGA_2012_GHSP-W2_v02_M | primary_chirps_era5_and_fallback_sources_probe_ready | blocked_raw_timing_geography_not_verified_sources_ready | not_accepted_raw_timing_geography_unverified | temp/raw_downloads/NGA_2012_GHSP-W2_v02_M/_PRIORITY_CLIMATE_LINKAGE_HANDOFF.md |
| 5 | priority_10_wave_batch | Nigeria | 2015-2016 | NGA_2015_GHSP-W3_v02_M | primary_chirps_era5_and_fallback_sources_probe_ready | blocked_raw_timing_geography_not_verified_sources_ready | not_accepted_raw_timing_geography_unverified | temp/raw_downloads/NGA_2015_GHSP-W3_v02_M/_PRIORITY_CLIMATE_LINKAGE_HANDOFF.md |
| 6 | priority_10_wave_batch | Nigeria | 2010-2011 | NGA_2010_GHSP-W1_v03_M | primary_chirps_era5_and_fallback_sources_probe_ready | blocked_raw_timing_geography_not_verified_sources_ready | not_accepted_raw_timing_geography_unverified | temp/raw_downloads/NGA_2010_GHSP-W1_v03_M/_PRIORITY_CLIMATE_LINKAGE_HANDOFF.md |
| 7 | priority_10_wave_batch | Tanzania | 2008-2009 | TZA_2008_NPS-R1_v03_M | primary_chirps_era5_and_fallback_sources_probe_ready | blocked_raw_timing_geography_not_verified_sources_ready | not_accepted_raw_timing_geography_unverified | temp/raw_downloads/TZA_2008_NPS-R1_v03_M/_PRIORITY_CLIMATE_LINKAGE_HANDOFF.md |
| 8 | priority_10_wave_batch | Tanzania | 2010-2011 | TZA_2010_NPS-R2_v03_M | primary_chirps_era5_and_fallback_sources_probe_ready | blocked_raw_timing_geography_not_verified_sources_ready | not_accepted_raw_timing_geography_unverified | temp/raw_downloads/TZA_2010_NPS-R2_v03_M/_PRIORITY_CLIMATE_LINKAGE_HANDOFF.md |
| 9 | priority_10_wave_batch | Tanzania | 2012-2013 | TZA_2012_NPS-R3_v01_M | primary_chirps_era5_and_fallback_sources_probe_ready | blocked_raw_timing_geography_not_verified_sources_ready | not_accepted_raw_timing_geography_unverified | temp/raw_downloads/TZA_2012_NPS-R3_v01_M/_PRIORITY_CLIMATE_LINKAGE_HANDOFF.md |
| 10 | priority_10_wave_batch | Uganda | 2014 | UGA_2014_SAGE-EL_v01_M | primary_chirps_era5_and_fallback_sources_probe_ready | blocked_raw_timing_geography_not_verified_sources_ready | not_accepted_raw_timing_geography_unverified | temp/raw_downloads/UGA_2014_SAGE-EL_v01_M/_PRIORITY_CLIMATE_LINKAGE_HANDOFF.md |
| 11 | sixth_country_backup_candidate | Jamaica | 1997 | JAM_1997_SLC_v01_M | primary_chirps_era5_and_fallback_sources_probe_ready | blocked_raw_timing_geography_not_verified_sources_ready | not_accepted_raw_timing_geography_unverified | temp/raw_downloads/JAM_1997_SLC_v01_M/_PRIORITY_CLIMATE_LINKAGE_HANDOFF.md |
| 12 | sixth_country_backup_candidate | Kyrgyz Republic | 1993 | KGZ_1993_KMPS_v01_M | primary_chirps_era5_and_fallback_sources_probe_ready | blocked_raw_timing_geography_not_verified_sources_ready | not_accepted_raw_timing_geography_unverified | temp/raw_downloads/KGZ_1993_KMPS_v01_M/_PRIORITY_CLIMATE_LINKAGE_HANDOFF.md |
| 13 | sixth_country_backup_candidate | Nepal | 2010-2011 | NPL_2010_LSS-III_v01_M | primary_chirps_era5_and_fallback_sources_probe_ready | blocked_raw_timing_geography_not_verified_sources_ready | not_accepted_raw_timing_geography_unverified | temp/raw_downloads/NPL_2010_LSS-III_v01_M/_PRIORITY_CLIMATE_LINKAGE_HANDOFF.md |

## Requirement Rows

| acquisition_batch_rank | idno | requirement_component | metadata_support_status | raw_verification_status | source_status | current_gate_status |
|---|---|---|---|---|---|---|
| 1 | ETH_2021_ESPS-W5_v02_M | cross_source_validation | metadata_supported | raw_not_verified | source_ready | metadata_ready_raw_unverified |
| 1 | ETH_2021_ESPS-W5_v02_M | exposure_window_construction | metadata_supported | raw_not_verified | not_required | metadata_ready_raw_unverified |
| 1 | ETH_2021_ESPS-W5_v02_M | geography_or_coordinates | metadata_supported | raw_not_verified | not_required | metadata_ready_raw_unverified |
| 1 | ETH_2021_ESPS-W5_v02_M | geolocation_quality_and_displacement | metadata_supported | raw_not_verified | not_required | metadata_ready_raw_unverified |
| 1 | ETH_2021_ESPS-W5_v02_M | historical_baseline_construction | metadata_supported | raw_not_verified | source_ready | metadata_ready_raw_unverified |
| 1 | ETH_2021_ESPS-W5_v02_M | nasa_power_fallback_and_crosscheck | metadata_supported | raw_not_verified | source_ready | metadata_ready_raw_unverified |
| 1 | ETH_2021_ESPS-W5_v02_M | rainfall_primary_chirps | metadata_supported | raw_not_verified | source_ready | metadata_ready_raw_unverified |
| 1 | ETH_2021_ESPS-W5_v02_M | spatial_qc_mapping | metadata_supported | raw_not_verified | not_required | metadata_ready_raw_unverified |
| 1 | ETH_2021_ESPS-W5_v02_M | survey_timing_for_lags | metadata_supported | raw_not_verified | not_required | metadata_ready_raw_unverified |
| 1 | ETH_2021_ESPS-W5_v02_M | temperature_primary_era5_land | metadata_supported | raw_not_verified | source_ready | metadata_ready_raw_unverified |
| 1 | ETH_2021_ESPS-W5_v02_M | water_balance_robustness | metadata_supported | raw_not_verified | source_ready | metadata_ready_raw_unverified |
| 2 | ETH_2018_ESS_v04_M | cross_source_validation | metadata_supported | raw_not_verified | source_ready | metadata_ready_raw_unverified |
| 2 | ETH_2018_ESS_v04_M | exposure_window_construction | metadata_supported | raw_not_verified | not_required | metadata_ready_raw_unverified |
| 2 | ETH_2018_ESS_v04_M | geography_or_coordinates | metadata_supported | raw_not_verified | not_required | metadata_ready_raw_unverified |
| 2 | ETH_2018_ESS_v04_M | geolocation_quality_and_displacement | metadata_supported | raw_not_verified | not_required | metadata_ready_raw_unverified |
| 2 | ETH_2018_ESS_v04_M | historical_baseline_construction | metadata_supported | raw_not_verified | source_ready | metadata_ready_raw_unverified |
| 2 | ETH_2018_ESS_v04_M | nasa_power_fallback_and_crosscheck | metadata_supported | raw_not_verified | source_ready | metadata_ready_raw_unverified |
| 2 | ETH_2018_ESS_v04_M | rainfall_primary_chirps | metadata_supported | raw_not_verified | source_ready | metadata_ready_raw_unverified |
| 2 | ETH_2018_ESS_v04_M | spatial_qc_mapping | metadata_supported | raw_not_verified | not_required | metadata_ready_raw_unverified |
| 2 | ETH_2018_ESS_v04_M | survey_timing_for_lags | metadata_supported | raw_not_verified | not_required | metadata_ready_raw_unverified |
| 2 | ETH_2018_ESS_v04_M | temperature_primary_era5_land | metadata_supported | raw_not_verified | source_ready | metadata_ready_raw_unverified |
| 2 | ETH_2018_ESS_v04_M | water_balance_robustness | metadata_supported | raw_not_verified | source_ready | metadata_ready_raw_unverified |
| 3 | MWI_2007-2009_MTM_v01_M | cross_source_validation | metadata_supported | raw_not_verified | source_ready | metadata_ready_raw_unverified |
| 3 | MWI_2007-2009_MTM_v01_M | exposure_window_construction | metadata_supported | raw_not_verified | not_required | metadata_ready_raw_unverified |
| 3 | MWI_2007-2009_MTM_v01_M | geography_or_coordinates | metadata_supported | raw_not_verified | not_required | metadata_ready_raw_unverified |
| 3 | MWI_2007-2009_MTM_v01_M | geolocation_quality_and_displacement | metadata_supported | raw_not_verified | not_required | metadata_ready_raw_unverified |
| 3 | MWI_2007-2009_MTM_v01_M | historical_baseline_construction | metadata_supported | raw_not_verified | source_ready | metadata_ready_raw_unverified |
| 3 | MWI_2007-2009_MTM_v01_M | nasa_power_fallback_and_crosscheck | metadata_supported | raw_not_verified | source_ready | metadata_ready_raw_unverified |
| 3 | MWI_2007-2009_MTM_v01_M | rainfall_primary_chirps | metadata_supported | raw_not_verified | source_ready | metadata_ready_raw_unverified |
| 3 | MWI_2007-2009_MTM_v01_M | spatial_qc_mapping | metadata_supported | raw_not_verified | not_required | metadata_ready_raw_unverified |

## Machine-Readable Outputs

- `temp/priority_climate_linkage_preflight.csv`
- `temp/priority_climate_linkage_requirements.csv`
- `result/priority_climate_linkage_preflight_summary.csv`
- per-wave `temp/raw_downloads/<IDNO>/_PRIORITY_CLIMATE_LINKAGE_HANDOFF.md`
