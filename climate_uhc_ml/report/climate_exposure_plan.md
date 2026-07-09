# Climate Exposure Plan

Status: exposure construction is planned but blocked until raw survey timing and geography are inspected. This report does not claim any climate exposure has been constructed.

## Dataset Gate Counts

| Climate linkage gate status | Count |
|---|---:|
| metadata_ready_raw_unverified | 27 |
| ready_for_climate_linkage_input_build | 1 |

## Exposure Specification Status

| Exposure spec status | Count |
|---|---:|
| blocked_until_verified_geography_and_timing | 28 |

## Summary Metrics

| Metric | Value | Interpretation |
|---|---:|---|
| climate_plan_country_waves | 28 | Quality-screened country-waves with dataset-level climate linkage plans. |
| climate_exposure_spec_rows | 28 | Pre-specified exposure family/window/source rows. |
| metadata_ready_raw_unverified_country_waves | 27 | Timing and geography appear plausible in metadata but raw files are not inspected. |
| ready_for_climate_linkage_input_build | 1 | Country-waves with raw-verified timing and geography. |
| blocked_until_verified_geography_and_timing_specs | 28 | Exposure specifications blocked by raw-data linkage inputs, not by source probing. |
| gate_count_metadata_ready_raw_unverified | 27 | Dataset-level climate linkage gate count. |
| gate_count_ready_for_climate_linkage_input_build | 1 | Dataset-level climate linkage gate count. |

## Source Hierarchy

| Domain | Primary | Fallback / robustness |
|---|---|---|
| Rainfall | CHIRPS daily/global precipitation | NASA POWER point checks; ERA5-Land precipitation checks if needed |
| Temperature | ERA5-Land daily statistics or reanalysis | NASA POWER point API |
| Drought/water balance | CHIRPS-derived anomalies plus TerraClimate/SPEI robustness | SPEI scale-specific drought robustness |

## Guardrail

Climate linkage requires raw-verified survey timing and raw-verified geography or coordinates. Metadata-supported timing/geography is useful for planning downloads only; it is not sufficient for exposure extraction or causal timing assumptions.

## Machine-Readable Outputs

- `temp/climate_exposure_plan.csv`
- `result/climate_exposure_specification.csv`
- `result/climate_exposure_plan_summary.csv`
