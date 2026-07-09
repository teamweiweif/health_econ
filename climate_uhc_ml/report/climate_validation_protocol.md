# Climate Validation Protocol

Status: climate linkage and exposure validation are planned but blocked until raw survey timing and geography are verified. This report does not construct climate exposures.

## Purpose

This protocol converts Phase 5 climate requirements into fail-closed country-wave checks for timing, geolocation quality, source units, historical baselines, spatial plausibility, and cross-source validation.

## Counts

| Metric | Value | Interpretation |
|---|---:|---|
| requirement_rows | 253 | Country-wave climate linkage requirement rows. |
| country_wave_rows | 23 | Priority bundle country-waves assessed. |
| source_matrix_rows | 9 | Climate source/method rows. |
| validation_protocol_rows | 9 | Climate exposure validation check rows. |
| ready_country_wave_rows | 0 | Country-waves ready for climate linkage value audit. |
| blocked_country_wave_rows | 23 | Country-waves blocked by raw timing/geography or validation inputs. |
| requirement_gate_metadata_ready_raw_unverified | 253 | Requirement gate status count. |
| readiness_status_blocked_until_raw_timing_geography_and_validation_inputs | 23 | Country-wave readiness status count. |
| source_status_pass_api_parameters_present | 1 | Climate source probe status count. |
| source_status_reachable_snapshot_saved | 8 | Climate source probe status count. |
| validation_status_blocked_until_verified_geography_and_timing | 9 | Validation protocol status count. |

## Requirement Gates

| Requirement gate status | Count |
|---|---:|
| metadata_ready_raw_unverified | 253 |

## Country-Wave Readiness

| Readiness status | Count |
|---|---:|
| blocked_until_raw_timing_geography_and_validation_inputs | 23 |

| bundle_rank | country | wave | idno | blocked_requirement_rows | readiness_status |
|---|---|---|---|---|---|
| 1 | Albania | 2005 | ALB_2005_LSMS_v01_M | 11 | blocked_until_raw_timing_geography_and_validation_inputs |
| 2 | Ethiopia | 2021-2022 | ETH_2021_ESPS-W5_v02_M | 11 | blocked_until_raw_timing_geography_and_validation_inputs |
| 3 | Ethiopia | 2018-2019 | ETH_2018_ESS_v04_M | 11 | blocked_until_raw_timing_geography_and_validation_inputs |
| 4 | Jamaica | 1997 | JAM_1997_SLC_v01_M | 11 | blocked_until_raw_timing_geography_and_validation_inputs |
| 5 | Kyrgyz Republic | 1993 | KGZ_1993_KMPS_v01_M | 11 | blocked_until_raw_timing_geography_and_validation_inputs |
| 6 | Malawi | 2007-2009 | MWI_2007-2009_MTM_v01_M | 11 | blocked_until_raw_timing_geography_and_validation_inputs |
| 7 | Malawi | 2004-2005 | MWI_2004_IHS-II_v01_M | 11 | blocked_until_raw_timing_geography_and_validation_inputs |
| 8 | Nepal | 2010-2011 | NPL_2010_LSS-III_v01_M | 11 | blocked_until_raw_timing_geography_and_validation_inputs |
| 9 | Nigeria | 2012-2013 | NGA_2012_GHSP-W2_v02_M | 11 | blocked_until_raw_timing_geography_and_validation_inputs |
| 10 | Nigeria | 2015-2016 | NGA_2015_GHSP-W3_v02_M | 11 | blocked_until_raw_timing_geography_and_validation_inputs |
| 11 | Nigeria | 2010-2011 | NGA_2010_GHSP-W1_v03_M | 11 | blocked_until_raw_timing_geography_and_validation_inputs |
| 12 | Tanzania | 2008-2009 | TZA_2008_NPS-R1_v03_M | 11 | blocked_until_raw_timing_geography_and_validation_inputs |
| 13 | Tanzania | 2010-2011 | TZA_2010_NPS-R2_v03_M | 11 | blocked_until_raw_timing_geography_and_validation_inputs |
| 14 | Tanzania | 2012-2013 | TZA_2012_NPS-R3_v01_M | 11 | blocked_until_raw_timing_geography_and_validation_inputs |
| 15 | Uganda | 2014 | UGA_2014_SAGE-EL_v01_M | 11 | blocked_until_raw_timing_geography_and_validation_inputs |

## Validation Checks

| Validation status | Count |
|---|---:|
| blocked_until_verified_geography_and_timing | 9 |

## Source Status

| Source probe status | Count |
|---|---:|
| reachable_snapshot_saved | 8 |
| pass_api_parameters_present | 1 |

## Guardrails

- Do not extract climate values until raw timing and geography are verified.
- Do not use post-interview climate in treatment windows; future climate is only for placebo checks.
- Do not treat displaced or admin-only geography as exact household exposure.
- Do not use ERA5-Land temperature without documenting Kelvin/Celsius handling.
- Do not use CHIRPS, TerraClimate, SPEI, or NASA POWER without recording units/scales and extraction metadata.

## Outputs

- `temp/climate_linkage_requirements.csv`
- `result/climate_source_method_matrix.csv`
- `result/climate_exposure_validation_protocol.csv`
- `result/climate_linkage_readiness.csv`
- `result/climate_validation_protocol_summary.csv`
