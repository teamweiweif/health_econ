# ALB_2002 Climate Centroid Exposure Candidate Audit

Status: temp-only climate stress-test. This audit uses candidate district bounding-box centroids from the local geoBoundaries 2.0.1 ADM2 snapshot and NASA POWER daily point API fallback data to compute 1, 3, 6, and 12 month exposure summaries for observed ALB_2002 district-month cells. It does not write `data/`, does not replace CHIRPS/ERA5 primary extraction, and does not promote climate linkage.

## Summary

| metric | value | interpretation |
|---|---|---|
| alb2002_climate_centroid_input_rows | 96 | Observed ALB_2002 district-month rows with candidate centroid inputs. |
| alb2002_climate_centroid_distinct_district_rows | 36 | Distinct ALB_2002 districts represented in the centroid stress test. |
| alb2002_climate_centroid_household_rows_covered | 3599 | Household rows represented across district-month input cells. |
| alb2002_climate_centroid_exposure_rows | 384 | Temp-only NASA POWER district-centroid exposure candidate rows. |
| alb2002_climate_centroid_window_rows | 4 | Exposure window definitions computed per district-month. |
| alb2002_climate_centroid_nasa_api_rows | 36 | NASA POWER API/cache manifest rows. |
| alb2002_climate_centroid_nasa_downloaded_rows | 0 | NASA POWER responses downloaded in this run. |
| alb2002_climate_centroid_nasa_cached_rows | 36 | NASA POWER responses reused from local cache. |
| alb2002_climate_centroid_nasa_failed_rows | 0 | NASA POWER responses that failed. |
| alb2002_climate_centroid_precip_nonmissing_rows | 384 | Exposure rows with nonmissing precipitation totals. |
| alb2002_climate_centroid_temp_nonmissing_rows | 384 | Exposure rows with nonmissing mean temperature. |
| alb2002_climate_centroid_boundary_year | 2013 | Boundary year from candidate geoBoundaries companion metadata. |
| alb2002_climate_centroid_historical_boundary_ready_rows | 0 | Rows ready as historical 2002 boundaries; should remain zero. |
| alb2002_climate_centroid_primary_chirps_ready_rows | 0 | Rows with primary CHIRPS rainfall extraction accepted; intentionally zero. |
| alb2002_climate_centroid_primary_era5_ready_rows | 0 | Rows with primary ERA5-Land temperature extraction accepted; intentionally zero. |
| alb2002_climate_centroid_historical_baseline_ready_rows | 0 | Rows with historical climate anomaly baselines accepted; intentionally zero. |
| alb2002_climate_centroid_climate_linkage_ready_rows | 0 | Rows ready for promoted climate linkage; intentionally zero. |
| alb2002_climate_centroid_data_write_ready_rows | 0 | Rows allowed to be written to data/ by this audit; intentionally zero. |
| alb2002_climate_centroid_current_decision | blocked_alb2002_climate_centroid_exposures_not_promoted_due_boundary_vintage_source_and_baseline_gates | Current fail-closed climate centroid exposure decision. |

## Readiness Audit

| check_id | status | rows_checked | passing_rows | promotion_ready_rows | evidence | blocking_reason |
|---|---|---|---|---|---|---|
| input_join | complete_candidate_not_promoted | 96 | 96 | 0 | input_rows=96; districts=36 | NASA POWER daily point summaries are computed at candidate district bounding-box centroids from a geoBoundaries 2.0.1 ADM2 snapshot, but the bounda... |
| nasa_power_api | complete_candidate_not_promoted | 36 | 36 | 0 | api_manifest_rows=36; ok=36; failed=0 | NASA POWER is a fallback source and point centroid extraction is not the primary CHIRPS/ERA5 climate specification. |
| window_exposures | complete_candidate_not_promoted | 384 | 384 | 0 | exposure_rows=384; precip_nonmissing=384; temp_nonmissing=384; windows=1;3;6;12 | Historical anomaly baselines, CHIRPS/ERA5 primary metrics, and verified geography are missing. |
| boundary_vintage | blocked | 1 | 0 | 0 | boundary_year=2013; historical_2002_boundary_ready_rows=0 | Candidate geometry metadata reports boundaryYear 2013, not verified 2002 LSMS district geography. |
| promotion | blocked | 384 | 0 | 0 | temp_exposure_rows=384; data_write_ready_rows=0; decision=blocked_alb2002_climate_centroid_exposures_not_promoted_due_boundary_vintage_source_and_b... | NASA POWER daily point summaries are computed at candidate district bounding-box centroids from a geoBoundaries 2.0.1 ADM2 snapshot, but the bounda... |

## API Manifest Preview

| district_code | district_name | centroid_lon | centroid_lat | start_date | end_date | api_status |
|---|---|---|---|---|---|---|
| 1 | BERAT | 19.955 | 40.6824 | 2001-04-15 | 2002-06-14 | cached |
| 2 | BULQIZE | 20.3348 | 41.4798 | 2001-04-15 | 2002-07-14 | cached |
| 3 | DELVINE | 20.0766 | 39.9654 | 2001-04-15 | 2002-06-14 | cached |
| 4 | DEVOLL | 20.9047 | 40.5919 | 2001-04-15 | 2002-05-14 | cached |
| 5 | DIBER | 20.3603 | 41.7299 | 2001-04-15 | 2002-06-14 | cached |
| 6 | DURRES | 19.5205 | 41.4234 | 2001-04-15 | 2002-06-14 | cached |
| 7 | ELBASAN | 20.0715 | 41.0659 | 2001-04-15 | 2002-06-14 | cached |
| 8 | FIER | 19.5652 | 40.7222 | 2001-04-15 | 2002-06-14 | cached |
| 9 | GRAMSH | 20.2464 | 40.8543 | 2001-04-15 | 2002-05-14 | cached |
| 10 | GJIROKASTER | 20.1598 | 40.0178 | 2001-04-15 | 2002-06-14 | cached |
| 11 | HAS | 20.3827 | 42.2023 | 2001-04-15 | 2002-06-14 | cached |
| 12 | KAVAJE | 19.5935 | 41.1371 | 2001-04-15 | 2002-06-14 | cached |
| 13 | KOLONJE | 20.6172 | 40.2847 | 2001-06-15 | 2002-06-14 | cached |
| 14 | KOR€E | 20.6389 | 40.6763 | 2001-04-15 | 2002-06-14 | cached |
| 15 | KRUJE | 19.745 | 41.5022 | 2001-04-15 | 2002-06-14 | cached |
| 16 | KU€OVE | 19.9102 | 40.8215 | 2001-04-15 | 2002-05-14 | cached |
| 17 | KUKES | 20.381 | 41.9979 | 2001-04-15 | 2002-07-14 | cached |
| 18 | KURBIN | 19.707 | 41.6392 | 2001-04-15 | 2002-06-14 | cached |
| 19 | LEZHE | 19.6566 | 41.8078 | 2001-04-15 | 2002-06-14 | cached |
| 20 | LIBRAZHD | 20.3421 | 41.1576 | 2001-04-15 | 2002-06-14 | cached |

## Interpretation

- The stress test confirms that climate summaries can be computed mechanically for the observed ALB_2002 district-month cells.
- The outputs remain candidate evidence only: the centroid geometry is not verified as 2001/2002 LSMS district geography, and NASA POWER is a fallback source.
- Primary CHIRPS rainfall, ERA5-Land temperature, historical z-score/percentile baselines, and climate-linkage promotion remain unresolved.

## Machine-Readable Outputs

- `temp/alb2002_climate_centroid_exposure_input.csv`
- `temp/alb2002_climate_centroid_exposure_candidates.csv`
- `temp/alb2002_climate_centroid_nasa_power_api_manifest.csv`
- `result/alb2002_climate_centroid_exposure_audit.csv`
- `result/alb2002_climate_centroid_exposure_summary.csv`
