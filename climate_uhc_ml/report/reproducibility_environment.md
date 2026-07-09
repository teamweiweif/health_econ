# Reproducibility Environment

Status: Python runtime and package availability have been audited. Missing optional causal/geospatial/ML packages are planning gaps, not evidence that the metadata pipeline is invalid.

## Runtime

- Python: `3.14.0`
- Executable: `C:\Python314\python.exe`
- Platform: `Windows-11-10.0.26200-SP0`

## Package Availability

| Package import status | Count |
|---|---:|
| missing | 16 |
| installed | 11 |

## Requirement Levels

| Requirement level | Count |
|---|---:|
| recommended_after_raw_download | 3 |
| recommended_for_chirps_era5_terraclimate | 3 |
| optional_predictive_ml | 3 |
| optional_causal_ml_after_identification | 3 |
| required_for_metadata_pipeline | 2 |
| required_for_empirical_pipeline | 2 |
| optional_scaling | 2 |
| recommended_for_admin_climate_linkage | 2 |
| required_for_climate_fallback | 1 |
| required_after_raw_download_for_dta_sav_sas | 1 |
| recommended_for_era5_terraclimate | 1 |
| optional_for_era5_download | 1 |
| required_after_outcomes_for_predictive_ml | 1 |
| recommended_for_reduced_form | 1 |
| optional_prediction_explanation | 1 |

## Audit Status

| Audit status | Count |
|---|---:|
| complete | 4 |

## Missing Tracked Packages

| package | import_name | requirement_level | role |
|---|---|---|---|
| polars | polars | optional_scaling | large tabular data exploration and joins |
| geopandas | geopandas | recommended_for_admin_climate_linkage | admin boundary linkage and geospatial validation |
| shapely | shapely | recommended_for_admin_climate_linkage | geometry operations for admin climate linkage |
| xarray | xarray | recommended_for_chirps_era5_terraclimate | gridded climate data handling |
| rasterio | rasterio | recommended_for_chirps_era5_terraclimate | raster climate/geospatial extraction |
| rioxarray | rioxarray | recommended_for_chirps_era5_terraclimate | xarray/raster geospatial climate extraction |
| netCDF4 | netCDF4 | recommended_for_era5_terraclimate | NetCDF climate data support |
| cdsapi | cdsapi | optional_for_era5_download | Copernicus ERA5-Land download API |
| statsmodels | statsmodels | recommended_for_reduced_form | reduced-form regression and robust inference helpers |
| xgboost | xgboost | optional_predictive_ml | candidate gradient-boosting model |
| lightgbm | lightgbm | optional_predictive_ml | candidate gradient-boosting model |
| catboost | catboost | optional_predictive_ml | candidate gradient-boosting model |
| shap | shap | optional_prediction_explanation | prediction explanation only, not causal interpretation |
| econml | econml | optional_causal_ml_after_identification | causal ML estimators after identification gate |
| doubleml | doubleml | optional_causal_ml_after_identification | double/debiased ML after identification gate |
| causalml | causalml | optional_causal_ml_after_identification | causal ML estimators after identification gate |

## Machine-Readable Outputs

- `temp/python_package_inventory.csv`
- `temp/python_package_freeze.txt`
- `result/python_environment_audit.csv`
- `result/python_environment_summary.csv`

## Guardrail

This audit documents runtime readiness only. It does not bypass the raw-microdata gate, and it does not justify estimating outcomes, predictive models, reduced-form models, causal ML, or policy simulations before analytical data exist.
