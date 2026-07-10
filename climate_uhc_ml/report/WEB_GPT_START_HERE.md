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
6. `report/priority_lsms_isa_promotion_gate_dashboard.md`
   - Current raw-receipt-to-promotion gate dashboard for 19 LSMS/ISA country-waves.
7. `report/priority_lsms_isa_next_raw_package_action_packet.md`
   - Exact remaining raw-package acquisition actions for the minimum batch plus backups.
8. `report/priority_lsms_isa_incoming_raw_package_router.md`
   - Non-destructive route plan for files dropped into `temp/raw_downloads/_incoming/`.
9. `report/priority_lsms_isa_threshold_gap_control_panel.md`
   - Short control panel showing the current 5-country/9-wave gap, minimum-batch downloads, and country/wave buffer.
10. `report/priority_lsms_isa_manual_download_packets.md`
   - Per-wave manual download packet index for the 10 remaining minimum-batch raw packages.
11. `report/priority_lsms_isa_manual_download_progress_tracker.md`
   - Local tracker showing whether downloaded files are present and ready for validation.
12. `report/priority_lsms_isa_post_download_validation_runner.md`
   - Dry-run validation plan; explicit `--execute` only after target folders contain official raw files.
13. `report/priority_lsms_isa_manual_download_execution_board.md`
   - One-table board with official URLs, target folders, missing-file counts, and post-download validation commands.
14. `report/priority_lsms_isa_credentialed_download_handoff.md`
   - Local-only cookie/header handoff for probing or executing World Bank get-microdata downloads after browser login.
15. `report/priority_lsms_isa_resource_download_route_probe.md`
   - Bounded public file-route probe for the 10 manual packets.
16. `report/priority_lsms_isa_download_acceptance_matrix.md`
   - Expected-file and requirement-level acceptance matrix for downloaded packages.
17. `report/priority_lsms_isa_local_target_readmes.md`
   - Manifest of local target-folder README files written under ignored `temp/raw_downloads/<IDNO>/`.
18. `report/priority_lsms_isa_minimum_batch_raw_value_queue.md`
   - Requirement, file, and variable raw-value review queue for the 10 manual packets.
19. `report/priority_lsms_isa_target_folder_receipt_smoke_test.md`
   - Non-destructive smoke test showing whether target folders contain candidate raw files ready for receipt validation.
20. `report/priority_lsms_isa_threshold_replacement_plan.md`
   - Replacement plan explaining the sixth-country need and backup order if a minimum-batch package fails.
21. `report/priority_lsms_isa_minimum_batch_climate_linkage_review_queue.md`
   - Current 10-packet timing/geography review queue for CHIRPS/ERA5 linkage after raw receipt.
22. `report/priority_lsms_isa_local_stray_raw_package_locator.md`
   - Non-destructive local workspace scan for already-downloaded raw packages outside the expected target folders.
23. `report/priority_lsms_isa_country_wave_promotion_packets/`
   - Per-wave promotion packets for the refocused LSMS/ISA campaign.
24. `report/mwi2004_requirement_acceptance_decisions.md`
   - Malawi 2004 raw-backed requirement accept/block decisions.

## Current Status

- Refocused registry rows: 19 country-waves.
- Priority-country rows: 16 rows from Ethiopia, Nigeria, Malawi, Tanzania, and Uganda.
- Promoted analysis-ready rows: 1.
- Financial-protection-ready countries: 1.
- Double-failure-ready country-waves: 1.
- Raw-value-verified country-waves: 1.
- Accepted CHIRPS/ERA5 climate-linkage routes: 1.
- Data-write gate: open only for the promoted Malawi 2004 country-wave.
- Modeling gate: blocked.

## Malawi 2004 Status

Malawi 2004 is the only row with received official raw package evidence so far.

Verified or partially accepted:

- CHE10/CHE25 financial inputs are verified for the stated scope.
- Acute need and cost-barrier forgone-care inputs are verified for the stated scope.
- Missing, unit, recall-period, and skip-pattern policy is accepted for the current verified constructs.
- Household interview timing and EA/admin geography are verified for the accepted CHIRPS ADM2 linkage route.
- A promoted household-climate dataset exists at `data/mwi2004_household_climate_analysis.csv`.

Still blocked:

- SDG 3.8.2 discretionary-budget construction.
- Multi-country promoted dataset synthesis.
- All additional country-waves until complete official raw packages pass receipt, value, semantics, timing/geography, and climate-linkage gates.

## Manual Download Routing

For the shortest current view of what must be downloaded before modeling can
resume, read:

- `report/priority_lsms_isa_threshold_gap_control_panel.md`
- `temp/priority_lsms_isa_threshold_gap_download_panel.csv`
- `report/priority_lsms_isa_manual_download_packets.md`
- `report/priority_lsms_isa_manual_download_progress_tracker.md`
- `report/priority_lsms_isa_post_download_validation_runner.md`
- `report/priority_lsms_isa_manual_download_execution_board.md`
- `report/priority_lsms_isa_credentialed_download_handoff.md`
- `report/priority_lsms_isa_resource_download_route_probe.md`
- `report/priority_lsms_isa_download_acceptance_matrix.md`
- `report/priority_lsms_isa_local_target_readmes.md`
- `report/priority_lsms_isa_minimum_batch_raw_value_queue.md`
- `report/priority_lsms_isa_target_folder_receipt_smoke_test.md`
- `report/priority_lsms_isa_threshold_replacement_plan.md`
- `report/priority_lsms_isa_minimum_batch_climate_linkage_review_queue.md`
- `report/priority_lsms_isa_local_stray_raw_package_locator.md`

If a new official raw package has been downloaded but the target IDNO folder is
uncertain, place it under `temp/raw_downloads/_incoming/` and run:

```bash
python script/174_build_priority_lsms_isa_incoming_raw_package_router.py
```

Then review `temp/priority_lsms_isa_incoming_raw_package_route_plan.csv`. The
router only writes suggested copy commands; it does not move, delete, extract,
or promote files.

If a logged-in World Bank Microdata browser session has accepted the required
terms, put a cookie export or raw `Cookie:` header in
`temp/private/worldbank_session_cookies.txt` and run:

```bash
python script/180_build_priority_lsms_isa_credentialed_download_handoff.py --probe
```

Use `--execute` only after the probe indicates a raw payload; the handoff saves
raw files under packet target folders but still does not extract, promote, or
run models.

To confirm whether common public file-id resource routes expose raw payloads
without using cookies or saving data, run:

```bash
python script/181_probe_priority_lsms_isa_resource_download_routes.py
```

After packages are placed locally, regenerate the expected-file and requirement
acceptance checklist:

```bash
python script/182_build_priority_lsms_isa_download_acceptance_matrix.py
```

To refresh the local target-folder README files under ignored
`temp/raw_downloads/<IDNO>/`, run:

```bash
python script/183_build_priority_lsms_isa_local_target_readmes.py
```

To refresh the 10-packet raw-value review queue after package placement, run:

```bash
python script/184_build_priority_lsms_isa_minimum_batch_raw_value_queue.py
```

To smoke-test known target folders before receipt/schema/value validation, run:

```bash
python script/185_build_priority_lsms_isa_target_folder_receipt_smoke_test.py
```

To refresh the threshold replacement and backup plan, run:

```bash
python script/186_build_priority_lsms_isa_threshold_replacement_plan.py
```

To refresh the current 10-packet timing/geography queue for CHIRPS/ERA5 review,
run:

```bash
python script/187_build_priority_lsms_isa_minimum_batch_climate_linkage_review_queue.py
```

To scan the local workspace for already-downloaded packages that were not placed
in the expected target folders, run:

```bash
python script/188_build_priority_lsms_isa_local_stray_raw_package_locator.py
```

## Excluded From GitHub

The GitHub copy intentionally excludes raw downloads, extracted raw archives,
Stata/SPSS/SAS files, large climate rasters, web caches, and Python bytecode.
Those files stay local under `temp/` or `temp/raw_downloads/`.
