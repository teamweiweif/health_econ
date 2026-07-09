# First-Batch File Source Traceability

Status: metadata-source audit only. This checks whether first-batch manual file/module targets are backed by the public World Bank schema file inventory, metadata variable catalog, and public documentation snapshots. It does not verify raw files, raw values, labels, units, recall periods, missing codes, or merge keys.

## Summary

| Metric | Value | Interpretation |
|---|---:|---|
| first_batch_file_source_traceability_rows | 143 | First-batch queued file/module source traceability rows. |
| first_batch_file_source_traceability_dataset_rows | 10 | Datasets represented in file-source traceability. |
| first_batch_file_source_traceability_unsupported_rows | 0 | Queued files missing from public schema inventory. |
| first_batch_candidate_variable_examples_checked | 1431 | Candidate raw-variable examples checked against metadata variable catalog. |
| first_batch_candidate_variable_examples_found | 1431 | Candidate examples found in metadata variable catalog. |
| source_trace_status_metadata_file_and_examples_supported | 143 | File-source trace status count. |
| metadata_file_status_metadata_file_found | 143 | Metadata file status count. |
| metadata_variable_status_metadata_variables_found | 143 | Metadata variable status count. |

## Source Trace Status

| Source trace status | Count |
|---|---:|
| metadata_file_and_examples_supported | 143 |

## Metadata File Status

| Metadata file status | Count |
|---|---:|
| metadata_file_found | 143 |

## Rows Needing Review

All queued files have public schema and candidate-example support.

## Guardrails

- A supported source trace means the module name and example variables appear in public metadata only.
- This audit does not prove the raw file was downloaded or that values, labels, units, recall periods, missing codes, or merge keys are valid.
- Do not promote harmonization, outcomes, climate linkage, models, causal claims, or policy simulations from this audit alone.

## Machine-Readable Outputs

- `temp/first_batch_file_source_traceability.csv`
- `result/first_batch_file_source_traceability_summary.csv`
