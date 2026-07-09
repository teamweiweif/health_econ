# Priority Climate Linkage Handoff: UGA_2014_SAGE-EL_v01_M

This is a fail-closed climate-linkage preflight for `Uganda`
`2014`. It does not extract climate data and does not accept a
CHIRPS/ERA5 route until raw timing, geography, geolocation quality, units, and
validation checks pass.

Current climate gate: `blocked_raw_timing_geography_not_verified_sources_ready`

Accepted CHIRPS/ERA5 route: `not_accepted_raw_timing_geography_unverified`

Planned geography level: gps_or_cluster_if_raw_verified_else_admin_fallback

Candidate timing files: int_access_fin;int_cohesion;int_facilities1;int_markets1;int_welfare_hh;sage_labourintermed

Candidate geography files: SAGE_HHWEIGHTSV2;int_access_educ18plus;int_access_fin;int_access_health;int_access_health_hh;int_access_school;int_asset_index;int_ben_characteristics;int_cohesion;int_cohesion_dec1

Required raw fields to verify: interview date or interview month/year; household or cluster identifier; survey wave/year linkage key; survey weight/design keys for later analysis linkage; admin1/admin2 or EA/cluster geography; admin code/name crosswalk; geography vintage and boundary source; geolocation quality flag; raw missing codes and skip patterns

Next action: After raw package placement, verify timing/geography variables and geolocation quality, then build climate linkage input.

## Climate Route Status

- Rainfall route: `chirps_source_probe_ready`
- Temperature route: `era5_source_probe_ready`
- Fallback route: `nasa_power_source_probe_ready`

## Requirement Gate Rows

| requirement_component | metadata_support_status | raw_verification_status | source_status | current_gate_status |
|---|---|---|---|---|
| cross_source_validation | metadata_supported | raw_not_verified | source_ready | metadata_ready_raw_unverified |
| exposure_window_construction | metadata_supported | raw_not_verified | not_required | metadata_ready_raw_unverified |
| geography_or_coordinates | metadata_supported | raw_not_verified | not_required | metadata_ready_raw_unverified |
| geolocation_quality_and_displacement | metadata_supported | raw_not_verified | not_required | metadata_ready_raw_unverified |
| historical_baseline_construction | metadata_supported | raw_not_verified | source_ready | metadata_ready_raw_unverified |
| nasa_power_fallback_and_crosscheck | metadata_supported | raw_not_verified | source_ready | metadata_ready_raw_unverified |
| rainfall_primary_chirps | metadata_supported | raw_not_verified | source_ready | metadata_ready_raw_unverified |
| spatial_qc_mapping | metadata_supported | raw_not_verified | not_required | metadata_ready_raw_unverified |
| survey_timing_for_lags | metadata_supported | raw_not_verified | not_required | metadata_ready_raw_unverified |
| temperature_primary_era5_land | metadata_supported | raw_not_verified | source_ready | metadata_ready_raw_unverified |
| water_balance_robustness | metadata_supported | raw_not_verified | source_ready | metadata_ready_raw_unverified |

## Post-Raw Verification Commands

```powershell
python script/17_audit_raw_downloads.py
python script/03_inspect_raw_schemas.py
python script/29_build_raw_variable_verification_protocol.py
python script/32_build_climate_validation_protocol.py
python script/125_build_priority_climate_linkage_preflight.py
python script/121_build_country_wave_promotion_registry.py
python script/36_build_direct_read_audit_bundle.py
python script/14_validate_workspace.py
```
