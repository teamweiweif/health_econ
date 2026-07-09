# Climate UHC ML

This is the current dataset-promotion workspace for the climate shocks and UHC
failure project.

The active objective is not to run more ML. The active objective is to promote
country-waves from metadata-only candidates into verified household by climate
analysis datasets. Modeling remains blocked until the promotion registry passes
the required thresholds.

## Read First

- `report/README.md` - current reproduction instructions and active guardrails.
- `report/country_wave_promotion_registry.md` - human-readable promotion status.
- `result/promoted_country_wave_registry.csv` - machine-readable gate registry.
- `result/priority_country_wave_download_queue.csv` - priority raw-data action queue.
- `report/country_wave_promotion_packets/` - one packet per target country-wave.
- `report/direct_read_audit_bundle.md` - compact Web-GPT-readable audit bundle.

## Current Status

- Registry rows: 24 country-waves.
- Priority-country rows: 16 rows from Ethiopia, Nigeria, Malawi, Tanzania, and Uganda.
- Promoted analysis-ready rows: 0.
- Financial-protection-ready countries: 0 of 6 required.
- Double-failure-ready country-waves: 0 of 10 required.
- Accepted CHIRPS/ERA5 climate-linkage routes: 0 of 1 required.

Albania 2002 remains a diagnostic template only. It is not the main empirical
case unless its timing, geography, and outcome gates are resolved.

## Included

- `script/` - reusable pipeline and promotion-gate scripts.
- `report/` - human-readable audit reports and country-wave packets.
- `result/` - machine-readable registries, queues, validation, and summaries.
- `data/` - small legacy Albania diagnostic CSVs only.

## Excluded

Raw downloads, extracted archives, web/API caches, Stata/SPSS/SAS files, and
temporary scratch files are deliberately excluded from the GitHub-readable
package. Put manual raw packages under `temp/raw_downloads/` locally, then rerun
the promotion pipeline.
