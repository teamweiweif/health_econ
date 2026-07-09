# Priority Official Download Dossier

Dataset: UGA_2014_SAGE-EL_v01_M - Uganda 2014

Status: blocked_official_access_required_no_original_package

Official get-microdata URL: https://microdata.worldbank.org/catalog/2654/get-microdata

Target folder: temp/raw_downloads/UGA_2014_SAGE-EL_v01_M/

Current receipt:

- Original files received: 0
- Archive files: 0
- Raw tabular files: 0
- Priority targets missing: 12

Official links:

- register: https://microdata.worldbank.org/auth/register
- terms_or_request: https://microdata.worldbank.org/terms-of-use
- pdf_documentation: https://microdata.worldbank.org/catalog/2654/pdf-documentation
- ddi_metadata: https://microdata.worldbank.org/metadata/export/2654/ddi
- json_metadata: https://microdata.worldbank.org/metadata/export/2654/json
- data_dictionary: https://microdata.worldbank.org/catalog/2654/data-dictionary
- related_materials: https://microdata.worldbank.org/catalog/2654/related-materials

Metadata file inventory examples:

- No metadata file inventory rows available.

Download action: Use official account/login/terms workflow, download the complete unchanged raw package and all documentation, then place it in the target folder.

Post-download commands:

- `python script/17_audit_raw_downloads.py`
- `python script/128_build_priority_archive_member_preflight.py`
- `python script/130_build_priority_raw_package_receipt_ledger.py`
- `python script/03_inspect_raw_schemas.py`
- `python script/29_build_raw_variable_verification_protocol.py`
- `python script/33_build_harmonization_recipe_gate.py`
- `python script/125_build_priority_climate_linkage_preflight.py`
- `python script/126_build_priority_raw_verification_workbook.py`
- `python script/129_build_priority_manual_verification_decision_gate.py`
- `python script/127_enforce_promoted_data_gate.py`
- `python script/36_build_direct_read_audit_bundle.py`
- `python script/14_validate_workspace.py`

Stop rule: do not write this wave into `data/` until the original package,
manual raw value/unit/key verification, and CHIRPS/ERA5 linkage gates pass.
