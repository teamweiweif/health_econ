# Priority LSMS/ISA External Local Raw Staging

Status: controlled staging plan/execution log for copying external local raw-folder candidates into `temp/raw_downloads/`.

This script never writes clean `data/`, never accepts official provenance, and never opens modeling. Raw staging is only a prerequisite for the existing receipt, schema, value, and promotion gates.

## Summary

| metric | value | interpretation |
| --- | --- | --- |
| external_local_raw_staging_mode | execute | Whether this run copied files or only produced a plan. |
| external_local_raw_staging_plan_rows | 3 | Copy-review-ready rows considered for external local staging. |
| external_local_raw_staging_file_manifest_rows | 304 | Source files covered by the staging plan or execution manifest. |
| external_local_raw_staging_executed_dataset_rows | 3 | Datasets copied into temp/raw_downloads by this run. |
| external_local_raw_staging_copied_file_rows | 304 | Files copied into temp/raw_downloads by this run. |
| external_local_raw_staging_skipped_existing_file_rows | 0 | Destination files already present with the same size. |
| external_local_raw_staging_blocked_file_rows | 0 | Files not copied because of safety or copy errors. |
| external_local_raw_staging_provenance_accepted_rows | 0 | Staging does not accept external local provenance as official receipt. |
| data_write_gate_status | blocked_no_data_write | Staging writes only temp/raw_downloads raw files and audit manifests, never clean data. |
| modeling_gate_status | blocked | No predictive, reduced-form, causal ML, or policy learning is opened. |

## Plan

| country | wave | idno | source_file_rows | source_total_bytes | target_preexisting_payload_rows | staging_status |
| --- | --- | --- | --- | --- | --- | --- |
| Nigeria | 2015-2016 | NGA_2015_GHSP-W3_v02_M | 117 | 463063214 | 0 | executed_copy_complete_provenance_not_accepted |
| Tanzania | 2010-2011 | TZA_2010_NPS-R2_v03_M | 100 | 74580242 | 0 | executed_copy_complete_provenance_not_accepted |
| Tanzania | 2012-2013 | TZA_2012_NPS-R3_v01_M | 87 | 98840263 | 0 | executed_copy_complete_provenance_not_accepted |

## Follow-Up

After any executed copy, rerun the raw intake, archive/direct-file preflight, receipt checklist, and official-file receipt validator before any schema/value or promotion decision.
