# Priority LSMS/ISA External Local Raw Staging

Status: controlled staging plan/execution log for copying external local raw-folder candidates into `temp/raw_downloads/`.

This script never writes clean `data/`, never accepts official provenance, and never opens modeling. Raw staging is only a prerequisite for the existing receipt, schema, value, and promotion gates.

## Summary

| metric | value | interpretation |
| --- | --- | --- |
| external_local_raw_staging_mode | execute | Whether this run copied files or only produced a plan. |
| external_local_raw_staging_plan_rows | 6 | Explicitly selected intake-decision rows considered for external local staging. |
| external_local_raw_staging_file_manifest_rows | 667 | Source files covered by the staging plan or execution manifest. |
| external_local_raw_staging_executed_dataset_rows | 6 | Datasets copied into temp/raw_downloads by this run. |
| external_local_raw_staging_copied_file_rows | 667 | Files copied into temp/raw_downloads by this run. |
| external_local_raw_staging_skipped_existing_file_rows | 0 | Destination files already present with the same size. |
| external_local_raw_staging_blocked_file_rows | 0 | Files not copied because of safety or copy errors. |
| external_local_raw_staging_provenance_accepted_rows | 0 | Staging does not accept external local provenance as official receipt. |
| data_write_gate_status | blocked_no_data_write | Staging writes only temp/raw_downloads raw files and audit manifests, never clean data. |
| modeling_gate_status | blocked | No predictive, reduced-form, causal ML, or policy learning is opened. |

## Plan

| country | wave | idno | intake_decision | source_file_rows | source_total_bytes | target_preexisting_payload_rows | staging_status |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Nigeria | 2012-2013 | NGA_2012_GHSP-W2_v02_M | selected_partial_intake_review_required | 122 | 299272329 | 0 | executed_copy_complete_provenance_not_accepted |
| Nigeria | 2010-2011 | NGA_2010_GHSP-W1_v03_M | selected_partial_intake_review_required | 111 | 95590399 | 0 | executed_copy_complete_provenance_not_accepted |
| Tanzania | 2008-2009 | TZA_2008_NPS-R1_v03_M | selected_partial_intake_review_required | 67 | 40757836 | 0 | executed_copy_complete_provenance_not_accepted |
| Malawi | 2016-2017 | MWI_2016_IHS-IV_v04_M | backup_intake_review_after_selected_batch | 105 | 1497441481 | 0 | executed_copy_complete_provenance_not_accepted |
| Malawi | 2010-2011 | MWI_2010_IHS-III_v01_M | backup_intake_review_after_selected_batch | 157 | 878651851 | 0 | executed_copy_complete_provenance_not_accepted |
| Uganda | 2011-2012 | UGA_2011_UNPS_v02_M | backup_intake_review_after_selected_batch | 105 | 58604903 | 0 | executed_copy_complete_provenance_not_accepted |

## Follow-Up

After any executed copy, rerun the raw intake, archive/direct-file preflight, receipt checklist, and official-file receipt validator before any schema/value or promotion decision.
