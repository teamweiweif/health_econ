# Priority Raw Package Receipt Ledger

Dataset: TZA_2008_NPS-R1_v03_M - Tanzania 2008-2009

Status: not_received_no_original_raw_package

Official URL: https://microdata.worldbank.org/catalog/76/get-microdata

Target folder: temp/raw_downloads/TZA_2008_NPS-R1_v03_M/

Current evidence:

- Original files counted: 0
- Archive packages: 0
- Raw tabular files: 0
- Documentation files: 0
- Priority targets covered: 0 / 12
- Missing priority targets: 12
- Manual verification status: blocked_raw_module_coverage_missing

Next action: Complete the official access workflow, download the unchanged raw package plus documentation, and place original files in this folder.

Missing target examples:

- SEC_3A_English_Labels
- SEC_3B_English_Labels
- SEC_B_C_D_E1_F_G1_U_English_Labels
- HH.Geovariables_Y1
- SEC_4A_English_Labels
- SEC_A_T_English_Labels
- SEC_H1_J_K2_O2_P1_Q1_S1_English_Labels
- TZY1.HH.Consumption
- SEC_S2_English_Labels
- SECTCEFG
- SEC_P2_English_Labels
- SECTCH

Post-receipt commands:

- `python script/17_audit_raw_downloads.py`
- `python script/128_build_priority_archive_member_preflight.py`
- `python script/03_inspect_raw_schemas.py`
- `python script/29_build_raw_variable_verification_protocol.py`
- `python script/33_build_harmonization_recipe_gate.py`
- `python script/125_build_priority_climate_linkage_preflight.py`
- `python script/126_build_priority_raw_verification_workbook.py`
- `python script/129_build_priority_manual_verification_decision_gate.py`
- `python script/130_build_priority_raw_package_receipt_ledger.py`
- `python script/127_enforce_promoted_data_gate.py`
- `python script/36_build_direct_read_audit_bundle.py`
- `python script/14_validate_workspace.py`

Promotion stop rule: Do not write this wave into data/ until original package receipt, raw target coverage, manual value/unit/key review, and CHIRPS/ERA5 linkage gates pass.
