# Priority LSMS-ISA Received Raw Schema Audit

Status: direct schema and selected value-stat audit of received LSMS/ISA raw
archives. The script extracts each Stata member to an operating-system temp
file, reads metadata and candidate-variable statistics, then discards the raw
copy. No raw microdata are written to `data/`.

## Summary

| Metric | Value | Interpretation |
|---|---:|---|
| priority_lsms_received_raw_schema_dataset_rows | 1 | Datasets with complete official-file receipt scanned directly from received raw archives. |
| priority_lsms_received_raw_schema_file_rows | 52 | Archive members attempted for schema extraction. |
| priority_lsms_received_raw_schema_readable_file_rows | 52 | Archive members readable by pyreadstat metadata scan. |
| priority_lsms_received_raw_schema_failed_file_rows | 0 | Archive members that could not be read for metadata. |
| priority_lsms_received_raw_schema_variable_rows | 1901 | Raw schema variable rows extracted without persisting raw microdata. |
| priority_lsms_received_raw_requirement_candidate_rows | 84 | Metadata candidate variables checked against readable raw schemas. |
| priority_lsms_received_raw_requirement_candidate_present_rows | 84 | Candidate variables present in the received raw schemas. |
| priority_lsms_received_raw_schema_handoff_readmes_written | 1 | Per-dataset raw schema audit handoff readmes written under temp/raw_downloads. |
| priority_lsms_received_raw_schema_data_write_status | blocked_schema_evidence_only | Schema evidence does not write analysis-ready data. |
| modeling_gate_status | blocked | Models remain blocked until promoted registry thresholds pass. |
| priority_lsms_received_raw_schema_status_raw_schema_variable_present_needs_unit_skip_review | 84 | Candidate variable schema evidence status count. |
| priority_lsms_received_raw_schema_requirement_present_climate_geography | 12 | Present raw-schema candidate variable count by requirement. |
| priority_lsms_received_raw_schema_requirement_present_consumption_or_income | 12 | Present raw-schema candidate variable count by requirement. |
| priority_lsms_received_raw_schema_requirement_present_health_need_and_access | 12 | Present raw-schema candidate variable count by requirement. |
| priority_lsms_received_raw_schema_requirement_present_household_person_keys | 12 | Present raw-schema candidate variable count by requirement. |
| priority_lsms_received_raw_schema_requirement_present_oop_health_expenditure | 12 | Present raw-schema candidate variable count by requirement. |
| priority_lsms_received_raw_schema_requirement_present_survey_timing | 12 | Present raw-schema candidate variable count by requirement. |
| priority_lsms_received_raw_schema_requirement_present_weights_and_design | 12 | Present raw-schema candidate variable count by requirement. |

## Dataset Coverage

| country | wave | idno | readable_files | file_rows | present_candidate_variables | candidate_variables |
|---|---|---|---|---|---|---|
| Malawi | 2004-2005 | MWI_2004_IHS-II_v01_M | 52 | 52 | 84 | 84 |

## Outputs

- `temp/priority_lsms_isa_received_raw_schema_file_inventory.csv`
- `temp/priority_lsms_isa_received_raw_variable_schema.csv`
- `temp/priority_lsms_isa_received_raw_requirement_evidence.csv`
- `result/priority_lsms_isa_received_raw_schema_audit_summary.csv`

## Interpretation

This is a schema-evidence layer between raw-package receipt and full
raw-value verification. It can show that candidate variables exist in the
received raw files and have nonmissing observations, but it cannot by itself
settle units, recall periods, skip patterns, missing codes, or promotion.
