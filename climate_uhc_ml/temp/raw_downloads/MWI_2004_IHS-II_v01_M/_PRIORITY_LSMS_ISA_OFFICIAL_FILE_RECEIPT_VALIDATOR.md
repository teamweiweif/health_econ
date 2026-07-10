# Priority LSMS-ISA Official File Receipt Validator

IDNO: `MWI_2004_IHS-II_v01_M`

Country-wave: Malawi 2004-2005

Target folder: `temp/raw_downloads/MWI_2004_IHS-II_v01_M/`

Status: `official_file_receipt_complete_pending_schema_value_review`

## Counts

| Metric | Value |
|---|---:|
| Official expected file rows | 52 |
| Official expected matched rows | 52 |
| Official expected missing rows | 0 |
| Official core file rows | 37 |
| Official core matched rows | 37 |
| Official core missing rows | 0 |
| Local original file/archive-member rows | 53 |

## Missing Core Files

No missing core files were found.

## Missing Official Files

No missing official files were found.

## Required Next Action

Proceed to schema inspection and raw value/unit/key review; data write remains blocked until all promotion gates pass.

After changing files in this folder, rerun:

`python script/17_audit_raw_downloads.py; python script/144_build_priority_lsms_isa_raw_package_intake_packet.py; python script/145_build_priority_lsms_isa_archive_member_preflight.py; python script/150_build_priority_lsms_isa_raw_package_receipt_checklist.py; python script/152_build_priority_lsms_isa_credentialed_raw_acquisition_workbench.py; python script/153_validate_priority_lsms_isa_official_file_receipt.py; python script/154_build_priority_lsms_isa_threshold_download_sequence.py; python script/155_build_priority_lsms_isa_minimum_batch_raw_intake_guide.py; python script/156_probe_priority_lsms_isa_minimum_batch_endpoint_refresh.py; python script/149_build_priority_lsms_isa_raw_value_verification_workbook.py; python script/132_build_priority_analysis_dataset_synthesis_blueprint.py; python script/148_build_priority_lsms_isa_country_wave_promotion_packets.py; python script/151_refresh_refocused_promoted_country_wave_registry.py; python script/127_enforce_promoted_data_gate.py; python script/36_build_direct_read_audit_bundle.py; python script/14_validate_workspace.py`

This validator only proves expected file-name receipt against official DDI
metadata. It does not prove variable values, labels, units, recall periods,
survey-design fields, merge keys, climate linkage, or analysis-ready status.
