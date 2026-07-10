# Priority LSMS-ISA Raw Package Intake

Dataset: `NGA_2012_GHSP-W2_v02_M` - Nigeria 2012-2013

Queue role: `core_selected_lsms_isa_aligned`

Official get-microdata URL: https://microdata.worldbank.org/catalog/1952/get-microdata

Target folder: `temp/raw_downloads/NGA_2012_GHSP-W2_v02_M/`

Current intake status: `blocked_no_original_package`

Original files counted: 0

Generated handoff files ignored: 31

## Minimum Acceptance Rule

Complete unchanged official raw package plus all documentation must be present; generated handoff markdown does not count as raw receipt.

## Requirement Acceptance Snapshot

| requirement | metadata_status | requirement_acceptance_status |
|---|---|---|
| household_person_keys | metadata_hit_raw_review_required | blocked_no_original_package |
| weights_and_design | metadata_hit_raw_review_required | blocked_no_original_package |
| consumption_or_income | metadata_hit_raw_review_required | blocked_no_original_package |
| oop_health_expenditure | metadata_weak_or_proxy_raw_review_required | blocked_no_original_package |
| health_need_and_access | metadata_hit_raw_review_required | blocked_no_original_package |
| survey_timing | metadata_hit_raw_review_required | blocked_no_original_package |
| climate_geography | metadata_hit_raw_review_required | blocked_no_original_package |
| missing_codes_units_recall_skip_patterns | raw_review_required | blocked_no_original_package |

## Post-Intake Commands

- `python script/17_audit_raw_downloads.py`
- `python script/128_build_priority_archive_member_preflight.py`
- `python script/130_build_priority_raw_package_receipt_ledger.py`
- `python script/03_inspect_raw_schemas.py`
- `python script/29_build_raw_variable_verification_protocol.py`
- `python script/33_build_harmonization_recipe_gate.py`
- `python script/126_build_priority_raw_verification_workbook.py`
- `python script/129_build_priority_manual_verification_decision_gate.py`
- `python script/132_build_priority_analysis_dataset_synthesis_blueprint.py`
- `python script/134_build_priority_country_wave_promotion_packets.py`
- `python script/127_enforce_promoted_data_gate.py`
- `python script/36_build_direct_read_audit_bundle.py`
- `python script/14_validate_workspace.py`

## Stop Rule

Do not write this country-wave into `data/` until original package receipt,
schema inspection, manual value/unit/key review, outcome readiness, and
accepted CHIRPS/ERA5 climate linkage all pass.
