# Web GPT Start Here

Use this file as the first GitHub entry point for the current `climate_uhc_ml`
workspace.

## Current Scope

This repository copy is a lightweight audit and dataset-promotion package. It is
not a raw-data mirror and it is not yet a modeling package.

The active task is to promote country-waves into verified household-by-climate
analysis datasets. Predictive ML, reduced-form causal models, causal ML, and
policy learning remain blocked until the promotion registry passes the required
data gates.

## Best Files To Read First

1. `report/direct_read_audit_bundle.md`
   - Compact narrative index of the current evidence, blockers, and gate status.
2. `result/direct_read_audit_bundle.csv`
   - Machine-readable version of the same GPT-facing bundle.
3. `result/direct_read_artifact_manifest.csv`
   - Manifest of curated reports, scripts, and result files.
4. `report/country_wave_promotion_registry.md`
   - Human-readable 19-wave promotion registry.
5. `result/promoted_country_wave_registry.csv`
   - Machine-readable promotion gate registry.
6. `report/priority_lsms_isa_country_wave_promotion_packets/`
   - Per-wave promotion packets for the refocused LSMS/ISA campaign.
7. `report/mwi2004_requirement_acceptance_decisions.md`
   - Malawi 2004 raw-backed requirement accept/block decisions.

## Current Status

- Refocused registry rows: 19 country-waves.
- Priority-country rows: 16 rows from Ethiopia, Nigeria, Malawi, Tanzania, and Uganda.
- Promoted analysis-ready rows: 0.
- Financial-protection-ready countries: 1.
- Double-failure-ready country-waves: 0.
- Accepted CHIRPS/ERA5 climate-linkage routes: 0.
- Data-write gate: closed because no country-wave is promoted.
- Modeling gate: blocked.

## Malawi 2004 Status

Malawi 2004 is the only row with received official raw package evidence so far.

Verified or partially accepted:

- CHE10/CHE25 financial inputs are verified for the stated scope.
- Household interview timing and EA/admin geography are verified for route review.

Still blocked:

- SDG 3.8.2 discretionary-budget construction.
- Final health-access/forgone-care construct.
- Accepted CHIRPS or ERA5 climate route.
- Promoted analysis dataset synthesis.

## Excluded From GitHub

The GitHub copy intentionally excludes raw downloads, extracted raw archives,
Stata/SPSS/SAS files, large climate rasters, web caches, and Python bytecode.
Those files stay local under `temp/` or `temp/raw_downloads/`.
