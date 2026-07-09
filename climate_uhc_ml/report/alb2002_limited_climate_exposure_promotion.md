# ALB_2002 Limited Climate Exposure Promotion

Status: limited fallback exposure promoted. This writes `data/climate_exposures_nasa_power.csv` from existing NASA POWER admin2-centroid exposure candidates. It does not promote final climate linkage, causal shocks, CHIRPS rainfall, ERA5-Land temperature, historical anomaly baselines, or household-level GPS exposure.

## Summary

| metric | value | interpretation |
|---|---|---|
| alb2002_limited_climate_exposure_promotion_audit_rows | 6 | Rows in the limited climate exposure promotion audit. |
| alb2002_limited_climate_exposure_rows | 384 | Rows written to data/climate_exposures_nasa_power.csv. |
| alb2002_limited_climate_exposure_distinct_district_rows | 36 | Distinct ALB_2002 admin2 district codes. |
| alb2002_limited_climate_exposure_window_rows | 4 | Exposure lag windows. |
| alb2002_limited_climate_exposure_precip_nonmissing_rows | 384 | Rows with nonmissing precipitation totals. |
| alb2002_limited_climate_exposure_temp_nonmissing_rows | 384 | Rows with nonmissing mean temperature. |
| alb2002_limited_climate_exposure_precip_z_rows | 384 | Rows with within-candidate diagnostic rainfall z-scores. |
| alb2002_limited_climate_exposure_temp_z_rows | 384 | Rows with within-candidate diagnostic temperature z-scores. |
| alb2002_limited_climate_exposure_limited_data_write_ready_rows | 384 | Rows allowed in data/ only under limited fallback exposure scope. |
| alb2002_limited_climate_exposure_primary_chirps_ready_rows | 0 | Rows ready with primary CHIRPS rainfall extraction. |
| alb2002_limited_climate_exposure_primary_era5_ready_rows | 0 | Rows ready with primary ERA5-Land temperature extraction. |
| alb2002_limited_climate_exposure_historical_baseline_ready_rows | 0 | Rows with accepted historical local climate baseline. |
| alb2002_limited_climate_exposure_climate_linkage_ready_rows | 0 | Rows ready for final climate-linked household data. |
| alb2002_limited_climate_exposure_final_analysis_ready_rows | 0 | Rows ready for final empirical analysis. |
| alb2002_limited_climate_exposure_current_decision | limited_nasa_admin2_centroid_climate_exposures_promoted_linkage_still_blocked | Current limited climate exposure promotion decision. |
| alb2002_limited_climate_exposure_data_use_limit | climate_exposure_admin2_centroid_only_not_for_final_climate_linkage | Guardrail embedded in every output row. |

## Gate Audit

| gate_id | status | rows_passing | rows_blocked | next_action |
|---|---|---|---|---|
| source_rows | complete_limited_fallback | 384 | 0 | Use as fallback exposure evidence only; do not treat as final climate-linked analysis input. |
| value_coverage | complete_limited_fallback | 384 | 0 | Compare against CHIRPS and ERA5-Land before final exposure claims. |
| diagnostic_zscores | complete_limited_diagnostic | 384 | 0 | Replace with local historical baselines before interpreting shocks as anomalies. |
| primary_source_gate | blocked_primary_sources_not_extracted | 0 | 384 | Extract and compare CHIRPS/ERA5-Land or document why NASA fallback remains the only feasible source. |
| historical_baseline_gate | blocked_no_historical_baseline | 0 | 384 | Build historical local climatology before final drought/heat anomaly treatment definitions. |
| climate_linkage_gate | blocked_not_linkage_ready | 0 | 384 | Verify geography and outcomes before writing climate-linked household data. |

## Guardrails

- Every row carries `climate_exposure_scope=alb2002_admin2_centroid_nasa_power_fallback_no_historical_baseline`.
- Every row carries `data_use_limit=climate_exposure_admin2_centroid_only_not_for_final_climate_linkage`.
- `primary_chirps_ready`, `primary_era5_ready`, `historical_baseline_ready`, `climate_linkage_ready`, and `final_analysis_ready` remain zero.
- The file supports audit and fallback exposure inspection only; it is not sufficient for climate-linked household analysis.

## Machine-Readable Outputs

- `data/climate_exposures_nasa_power.csv`
- `temp/climate_extraction_audit.csv`
- `temp/alb2002_limited_climate_exposure_promotion_audit.csv`
- `result/alb2002_limited_climate_exposure_promotion_summary.csv`
