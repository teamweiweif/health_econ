# Climate UHC ML

This is the current dataset-promotion workspace for the climate shocks and UHC
failure project.

The active objective is not to run more ML. The active objective is to promote
country-waves from metadata-only candidates into verified household by climate
analysis datasets. Modeling remains blocked until the promotion registry passes
the required thresholds.

## Read First

- `report/WEB_GPT_START_HERE.md` - shortest entry point for Web GPT / GitHub review.
- `report/README.md` - current reproduction instructions and active guardrails.
- `report/country_wave_promotion_registry.md` - human-readable promotion status.
- `result/promoted_country_wave_registry.csv` - machine-readable gate registry.
- `result/priority_country_wave_download_queue.csv` - priority raw-data action queue.
- `report/priority_lsms_isa_next_raw_package_action_packet.md` - exact remaining raw-package actions.
- `report/priority_lsms_isa_promotion_gate_dashboard.md` - current raw-receipt-to-promotion gate dashboard.
- `report/country_wave_promotion_packets/` - one packet per target country-wave.
- `report/direct_read_audit_bundle.md` - compact Web-GPT-readable audit bundle.

## Current Status

- Registry rows: 19 country-waves.
- Priority-country rows: 16 rows from Ethiopia, Nigeria, Malawi, Tanzania, and Uganda.
- Promoted analysis-ready rows: 1.
- Financial-protection-ready countries: 1 of 6 required.
- Double-failure-ready country-waves: 1 of 10 required.
- Raw-value-verified country-waves: 1.
- Accepted CHIRPS/ERA5 climate-linkage routes: 1 of 1 required.

Malawi 2004 is the current raw-backed audit row. CHE10/CHE25 financial inputs and
cost-barrier forgone-care/access inputs have been verified for their stated
scope. Survey timing and admin/EA geography are verified for the accepted
CHIRPS ADM2 linkage route, and a promoted household-climate dataset exists for
this one country-wave. SDG 3.8.2 and multi-country dataset synthesis remain
blocked until additional raw packages pass the same gates.

Albania remains a diagnostic template only. It is not the main empirical case
unless its timing, geography, and outcome gates are resolved.

## Included

- `script/` - reusable pipeline and promotion-gate scripts.
- `report/` - human-readable audit reports and country-wave packets.
- `result/` - machine-readable registries, queues, validation, and summaries.
- `data/` - promoted analysis-ready datasets only; currently Malawi 2004.

## Excluded

Raw downloads, extracted archives, web/API caches, Stata/SPSS/SAS files, and
temporary scratch files are deliberately excluded from the GitHub-readable
package. Put manual raw packages under `temp/raw_downloads/` locally, then rerun
the promotion pipeline.
