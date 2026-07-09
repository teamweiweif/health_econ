# Priority Threshold Acquisition Campaign

Dataset: TZA_2010_NPS-R2_v03_M - Tanzania 2010-2011

Campaign phase: phase_1_double_failure_10_wave_base

Threshold role: required_for_10_country_wave_double_failure_threshold

Country role: core_five_country_base

Official URL: https://microdata.worldbank.org/catalog/1050/get-microdata

Target folder: `temp/raw_downloads/TZA_2010_NPS-R2_v03_M/`

Current raw receipt: not_received_no_original_raw_package

Current promoted registry status: not_promoted

Next action: Open official get-microdata URL with an authorized account, complete terms/Data Access Agreement, download the complete unchanged package plus documentation, and place it in the target folder.

Post-download validation commands:

- `python script/17_audit_raw_downloads.py`
- `python script/128_build_priority_archive_member_preflight.py`
- `python script/130_build_priority_raw_package_receipt_ledger.py`
- `python script/03_inspect_raw_schemas.py`
- `python script/29_build_raw_variable_verification_protocol.py`
- `python script/33_build_harmonization_recipe_gate.py`
- `python script/125_build_priority_climate_linkage_preflight.py`
- `python script/126_build_priority_raw_verification_workbook.py`
- `python script/129_build_priority_manual_verification_decision_gate.py`
- `python script/140_build_priority_first_pass_variable_review_queue.py`
- `python script/141_build_priority_download_execution_packet.py`
- `python script/132_build_priority_analysis_dataset_synthesis_blueprint.py`
- `python script/134_build_priority_country_wave_promotion_packets.py`
- `python script/127_enforce_promoted_data_gate.py`
- `python script/36_build_direct_read_audit_bundle.py`
- `python script/14_validate_workspace.py`

Promotion stop rule: Do not write this country-wave into data/ until the complete original package, raw value verification, outcome readiness, and CHIRPS/ERA5 linkage gates pass.
