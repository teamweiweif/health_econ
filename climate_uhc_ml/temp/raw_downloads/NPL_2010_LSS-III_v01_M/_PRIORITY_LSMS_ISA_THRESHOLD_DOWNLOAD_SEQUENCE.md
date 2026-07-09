# Priority LSMS-ISA Threshold Download Sequence

IDNO: `NPL_2010_LSS-III_v01_M`

Country-wave: Nepal 2010-2011

Threshold sequence rank: 11

Threshold phase: `phase_2_sixth_country_financial_protection_candidate`

Threshold download role: `minimum_6th_country_financial_protection_candidate`

Minimum threshold batch: `1`

Recommended threshold batch: `1`

Official URL: https://microdata.worldbank.org/catalog/1000/get-microdata

Target folder: `temp/raw_downloads/NPL_2010_LSS-III_v01_M/`

Official file receipt status: `blocked_no_original_package`

Expected official files: 51

Expected matched files: 0

Core files: 28

Core matched files: 0

## Next Action

Download the complete unchanged official World Bank package and documentation, then place it in the target folder.

## Post-Download Validation

`python script/17_audit_raw_downloads.py; python script/144_build_priority_lsms_isa_raw_package_intake_packet.py; python script/145_build_priority_lsms_isa_archive_member_preflight.py; python script/150_build_priority_lsms_isa_raw_package_receipt_checklist.py; python script/152_build_priority_lsms_isa_credentialed_raw_acquisition_workbench.py; python script/153_validate_priority_lsms_isa_official_file_receipt.py; python script/154_build_priority_lsms_isa_threshold_download_sequence.py; python script/149_build_priority_lsms_isa_raw_value_verification_workbook.py; python script/132_build_priority_analysis_dataset_synthesis_blueprint.py; python script/148_build_priority_lsms_isa_country_wave_promotion_packets.py; python script/151_refresh_refocused_promoted_country_wave_registry.py; python script/127_enforce_promoted_data_gate.py; python script/36_build_direct_read_audit_bundle.py; python script/14_validate_workspace.py`

## Stop Rule

Do not write this country-wave into data/ until complete official file receipt, raw value verification, outcome construction, survey timing/geography, and accepted CHIRPS or ERA5 climate linkage all pass.
