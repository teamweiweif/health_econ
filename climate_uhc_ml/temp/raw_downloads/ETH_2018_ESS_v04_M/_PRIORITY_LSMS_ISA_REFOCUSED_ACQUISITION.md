# Priority LSMS-ISA Refocused Acquisition

Dataset: `ETH_2018_ESS_v04_M` - Ethiopia 2018-2019

Queue role: `core_selected_lsms_isa_aligned`

Official get-microdata URL: https://microdata.worldbank.org/catalog/3823/get-microdata

Target folder: `temp/raw_downloads/ETH_2018_ESS_v04_M/`

Current raw status: `not_received_no_original_raw_package`

## Manual Download Scope

Download the complete unchanged official raw package plus all documentation.
Do not download only selected modules, and do not write anything into `data/`
until the promotion gates pass.

## Requirement Gate Snapshot

| requirement | metadata_status | promotion_gate_status |
|---|---|---|
| household_person_keys | metadata_hit_raw_review_required | blocked_pending_raw_review |
| weights_and_design | metadata_hit_raw_review_required | blocked_pending_raw_review |
| consumption_or_income | metadata_hit_raw_review_required | blocked_pending_raw_review |
| oop_health_expenditure | metadata_weak_or_proxy_raw_review_required | blocked_pending_raw_review |
| health_need_and_access | metadata_hit_raw_review_required | blocked_pending_raw_review |
| survey_timing | metadata_hit_raw_review_required | blocked_pending_raw_review |
| climate_geography | metadata_hit_raw_review_required | blocked_pending_raw_review |
| missing_codes_units_recall_skip_patterns | raw_review_required | blocked_pending_raw_review |

## Post-Download Commands

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

Models remain blocked. This wave cannot enter the promoted registry until raw
receipt, schema inspection, value/unit/key review, outcome review, and
CHIRPS/ERA5 climate-linkage review all pass.
