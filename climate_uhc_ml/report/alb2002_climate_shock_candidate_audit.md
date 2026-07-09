# ALB_2002 Climate Shock Candidate Audit

Status: temp-only diagnostic climate-shock audit. This derives within-candidate rainfall and temperature z-scores from the ALB_2002 NASA POWER centroid exposure stress test. It does not create historical anomalies, accepted shock treatments, or any `data/` output.

## Summary

| Metric | Value | Interpretation |
|---|---:|---|
| alb2002_climate_shock_candidate_exposure_rows | 384 | Temp-only climate shock diagnostic rows derived from centroid exposures. |
| alb2002_climate_shock_candidate_source_centroid_rows | 384 | Source centroid exposure rows consumed. |
| alb2002_climate_shock_candidate_lineage_rows | 7 | Lineage rows for diagnostic shock fields. |
| alb2002_climate_shock_candidate_audit_rows | 8 | Audit rows for diagnostic shock construction and promotion gates. |
| alb2002_climate_shock_candidate_distinct_district_rows | 36 | Distinct districts represented. |
| alb2002_climate_shock_candidate_survey_month_rows | 4 | Distinct survey months represented. |
| alb2002_climate_shock_candidate_window_rows | 4 | Distinct lag windows represented. |
| alb2002_climate_shock_candidate_reference_group_rows | 16 | Survey-month-by-window diagnostic reference groups. |
| alb2002_climate_shock_candidate_min_reference_group_size | 3 | Smallest within-candidate reference group size. |
| alb2002_climate_shock_candidate_max_reference_group_size | 34 | Largest within-candidate reference group size. |
| alb2002_climate_shock_candidate_precip_z_nonmissing_rows | 384 | Rows with diagnostic rainfall z-scores. |
| alb2002_climate_shock_candidate_temp_z_nonmissing_rows | 384 | Rows with diagnostic temperature z-scores. |
| alb2002_climate_shock_candidate_low_rain_rows | 37 | Rows with diagnostic low-rain z <= -1. |
| alb2002_climate_shock_candidate_severe_low_rain_rows | 0 | Rows with diagnostic low-rain z <= -1.5. |
| alb2002_climate_shock_candidate_extreme_wet_rows | 44 | Rows with diagnostic wet z >= 1.5. |
| alb2002_climate_shock_candidate_heat_rows | 66 | Rows with diagnostic heat z >= 1. |
| alb2002_climate_shock_candidate_extreme_heat_rows | 29 | Rows with diagnostic heat z >= 1.5. |
| alb2002_climate_shock_candidate_cold_rows | 13 | Rows with diagnostic cold z <= -1.5. |
| alb2002_climate_shock_candidate_combined_stress_rows | 73 | Rows with any severe low-rain, extreme-wet, or extreme-heat diagnostic flag. |
| alb2002_climate_shock_candidate_primary_chirps_ready_rows | 0 | Rows with primary CHIRPS rainfall accepted; intentionally zero. |
| alb2002_climate_shock_candidate_primary_era5_ready_rows | 0 | Rows with primary ERA5-Land temperature accepted; intentionally zero. |
| alb2002_climate_shock_candidate_historical_baseline_ready_rows | 0 | Rows with local historical baselines accepted; intentionally zero. |
| alb2002_climate_shock_candidate_climate_linkage_ready_rows | 0 | Rows ready for promoted climate linkage; intentionally zero. |
| alb2002_climate_shock_candidate_data_write_ready_rows | 0 | Rows allowed to be written to data/; intentionally zero. |
| alb2002_climate_shock_candidate_current_decision | blocked_alb2002_climate_shock_candidate_not_promoted_due_geography_baseline_primary_source_gates | Current fail-closed climate shock diagnostic decision. |

## Readiness Audit

| check_id | status | rows_checked | passing_rows | promotion_ready_rows | evidence | blocking_reason |
|---|---|---|---|---|---|---|
| source_centroid_exposures | complete_candidate_not_promoted | 384 | 384 | 0 | shock_rows=384; source_centroid_rows=384 | Within-candidate rainfall and temperature z-scores are computed only for diagnostic screening from NASA POWER fallback point su... |
| reference_groups | complete_candidate_not_promoted | 16 | 16 | 0 | reference_groups=16; min_group_rows=3; max_group_rows=34 | Reference groups are cross-sectional candidate districts, not historical local climatology. |
| diagnostic_zscores | complete_candidate_not_promoted | 384 | 384 | 0 | precip_z_nonmissing=384; temp_z_nonmissing=384 | These z-scores are diagnostic distributional flags only and cannot be interpreted as historical anomalies. |
| diagnostic_shock_flags | complete_candidate_not_promoted | 384 | 73 | 0 | low_rain_z_le_m1=37; severe_low_rain_z_le_m15=0; extreme_wet_z_ge_15=44; heat_z_ge_1=66; extreme_heat_z_ge_15=29; combined_stre... | Diagnostic flags show candidate variation only; they are not accepted treatment variables. |
| primary_sources | blocked | 2 | 0 | 0 | primary_chirps_ready=0; primary_era5_ready=0 | NASA POWER fallback diagnostics do not satisfy the primary climate-source requirement. |
| historical_baseline | blocked | 384 | 0 | 0 | historical_baseline_ready_rows=0 | No accepted local historical baseline exists for rainfall or temperature z-scores/percentiles. |
| geography_vintage | blocked | 384 | 0 | 0 | boundary_year=2013; climate_linkage_ready_rows=0 | Candidate centroids use a current/2013 boundary source rather than verified 2001/2002 LSMS geography or GPS. |
| promotion | blocked | 384 | 0 | 0 | data_write_ready_rows=0; decision=blocked_alb2002_climate_shock_candidate_not_promoted_due_geography_baseline_primary_source_gates | Within-candidate rainfall and temperature z-scores are computed only for diagnostic screening from NASA POWER fallback point su... |

## Lineage

| derived_field | source_fields | formula_or_rule | status | blocking_reason |
|---|---|---|---|---|
| reference_group | survey_month;window_months | Survey-month-by-lag-window group used only for within-candidate diagnostics. | candidate_not_promoted | Reference group is not historical climatology. |
| precip_within_candidate_z | precip_total_mm;survey_month;window_months | (precip_total_mm - reference-group mean) / reference-group population SD. | candidate_not_promoted | Rainfall z-score is not a CHIRPS or historical anomaly. |
| temp_within_candidate_z | temp_mean_c;survey_month;window_months | (temp_mean_c - reference-group mean) / reference-group population SD. | candidate_not_promoted | Temperature z-score is not an ERA5-Land or historical anomaly. |
| diagnostic_low_rain/wet_flags | precip_within_candidate_z | Low-rain flag <= -1; severe low-rain flag <= -1.5; extreme-wet flag >= 1.5. | candidate_not_promoted | Flags are prioritization diagnostics only. |
| diagnostic_heat/cold_flags | temp_within_candidate_z | Heat flag >= 1; extreme-heat flag >= 1.5; cold flag <= -1.5. | candidate_not_promoted | Flags are prioritization diagnostics only. |
| diagnostic_combined_climate_stress | diagnostic_severe_low_rain_z_le_m15;diagnostic_extreme_wet_z_ge_15;diagnostic_extreme_heat_z_ge_15 | Any severe low-rain, extreme-wet, or extreme-heat diagnostic flag. | candidate_not_promoted | Combined flag is not a treatment variable. |
| promotion_status | primary_chirps_ready;primary_era5_ready;historical_baseline_ready;climate_linkage_ready | Promotion remains zero until all climate-source, baseline, and geography gates pass. | candidate_not_promoted | No data/ write is allowed. |

## Interpretation

- The diagnostic z-scores compare districts within the same survey month and lag window; they are not local historical anomalies.
- NASA POWER remains a fallback source. CHIRPS rainfall and ERA5-Land temperature remain the primary climate-source requirement.
- Boundary vintage, historical geography/GPS, primary-source extraction, and historical baseline gates remain blocked.
- Climate-linkage-ready and data-write-ready rows remain zero.

## Machine-Readable Outputs

- `temp/alb2002_climate_shock_candidate_exposures.csv`
- `temp/alb2002_climate_shock_candidate_lineage.csv`
- `result/alb2002_climate_shock_candidate_audit.csv`
- `result/alb2002_climate_shock_candidate_summary.csv`
