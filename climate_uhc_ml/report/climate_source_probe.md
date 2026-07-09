# Climate Source Probe

Status: official climate source endpoints were probed with small documentation/API snapshots. This is source-readiness evidence only; it does not construct household climate exposure data.

## Status Counts

| Status | Count |
|---|---:|
| reachable_snapshot_saved | 8 |
| pass_api_parameters_present | 1 |

## Source Roles

| Source role | Count |
|---|---:|
| primary_rainfall_documentation | 1 |
| primary_rainfall_data_directory | 1 |
| primary_temperature_documentation | 1 |
| primary_daily_temperature_documentation | 1 |
| rapid_point_fallback_documentation | 1 |
| rapid_point_fallback_api | 1 |
| water_balance_robustness_documentation | 1 |
| water_balance_robustness_catalog | 1 |
| drought_robustness_documentation | 1 |

## Sources

| Source | Role | Status | Saved snapshot | Unit notes |
|---|---|---|---|---|
| CHIRPS precipitation documentation | primary_rainfall_documentation | reachable_snapshot_saved | `temp/source_snapshots/climate_sources/chirps_precipitation_documentation.html` | CHIRPS precipitation is used as rainfall in mm; confirm file-level units during extraction. |
| CHIRPS 2.0 global daily directory | primary_rainfall_data_directory | reachable_snapshot_saved | `temp/source_snapshots/climate_sources/chirps_2.0_global_daily_directory.html` | Do not download bulk files in this probe; verify daily file units before analysis. |
| ERA5-Land reanalysis | primary_temperature_documentation | reachable_snapshot_saved | `temp/source_snapshots/climate_sources/era5-land_reanalysis.html` | ERA5-family temperatures are commonly Kelvin in raw products; convert only after metadata verification. |
| ERA5-Land daily statistics | primary_daily_temperature_documentation | reachable_snapshot_saved | `temp/source_snapshots/climate_sources/era5-land_daily_statistics.html` | Daily-statistics units depend on selected variable/statistic; verify request metadata. |
| NASA POWER daily API documentation | rapid_point_fallback_documentation | reachable_snapshot_saved | `temp/source_snapshots/climate_sources/nasa_power_daily_api_documentation.html` | API response metadata must be recorded with extracted variables. |
| NASA POWER daily API smoke test | rapid_point_fallback_api | pass_api_parameters_present | `temp/source_snapshots/climate_sources/nasa_power_daily_api_smoke_test.json` | PRECTOTCORR, T2M, T2M_MAX, and T2M_MIN are validated from a small JSON response only. |
| TerraClimate documentation | water_balance_robustness_documentation | reachable_snapshot_saved | `temp/source_snapshots/climate_sources/terraclimate_documentation.html` | Water-balance variables require variable-specific unit checks before use. |
| TerraClimate Earth Engine catalog | water_balance_robustness_catalog | reachable_snapshot_saved | `temp/source_snapshots/climate_sources/terraclimate_earth_engine_catalog.html` | Catalog units/scales must be honored when extracting from Earth Engine or mirrored data. |
| SPEI Global Drought Monitor | drought_robustness_documentation | reachable_snapshot_saved | `temp/source_snapshots/climate_sources/spei_global_drought_monitor.html` | SPEI is standardized drought index; use only after temporal scale and baseline are documented. |

## Guardrail

CHIRPS, ERA5-Land, TerraClimate, SPEI, and NASA POWER are not interchangeable. The analytical pipeline must still verify variable-specific units, temporal aggregation, historical baselines, and point/admin geospatial linkage after raw household geography and timing are available.
