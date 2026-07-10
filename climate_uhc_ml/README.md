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
- `report/priority_lsms_isa_incoming_raw_package_router.md` - route plan for manual downloads dropped into `_incoming`.
- `report/priority_lsms_isa_threshold_gap_control_panel.md` - shortest current country/wave gap and minimum-batch download panel.
- `report/priority_lsms_isa_manual_download_packets.md` - per-wave manual download packets for the 10 remaining minimum-batch packages.
- `report/priority_lsms_isa_manual_download_progress_tracker.md` - local tracker showing whether packet folders contain files ready for validation.
- `report/priority_lsms_isa_post_download_validation_runner.md` - dry-run/explicit-execute plan for post-download receipt/schema/value checks.
- `report/priority_lsms_isa_manual_download_execution_board.md` - one-table download URL, target-folder, missing-file, and validation command board.
- `report/priority_lsms_isa_credentialed_download_handoff.md` - local-only World Bank session handoff for credentialed get-microdata downloads.
- `report/priority_lsms_isa_resource_download_route_probe.md` - bounded public resource-route probe for the 10 manual packets.
- `report/priority_lsms_isa_download_acceptance_matrix.md` - expected-file and requirement-level acceptance matrix for downloaded packages.
- `report/priority_lsms_isa_local_target_readmes.md` - manifest of local target-folder download acceptance README files.
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
the promotion pipeline. If the target folder is uncertain, put files under
`temp/raw_downloads/_incoming/` first and run the incoming raw package router.
Credential/session files belong only under `temp/private/` and must never be
committed.
