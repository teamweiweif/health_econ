# First-Batch Raw Verification Workbook

Status: fillable post-download verification workbook. It does not verify any dataset by itself. It converts the first-batch raw acquisition plan into dataset, concept, and variable rows that must be completed after raw files are downloaded and schema-inspected.

## Summary

| Metric | Value | Interpretation |
|---|---:|---|
| first_batch_dataset_gate_rows | 10 | Dataset-level verification gate rows. |
| first_batch_concept_template_rows | 130 | Concept-level verification template rows. |
| first_batch_variable_template_rows | 917 | Variable-level verification template rows. |
| datasets_ready_for_manual_value_audit | 0 | Datasets with raw schemas matched to critical concepts. |
| concepts_ready_for_manual_value_audit | 9 | Concept rows ready for value/label/unit/key audit. |
| variables_ready_for_manual_value_audit | 42 | Variable rows ready for value/label/unit/key audit. |
| dataset_gate_blocked_candidate_file_or_variable_not_matched | 1 | Dataset gate status count. |
| dataset_gate_blocked_raw_files_absent | 9 | Dataset gate status count. |
| concept_gate_blocked_missing_metadata_candidate | 12 | Concept gate status count. |
| concept_gate_blocked_raw_candidate_not_matched | 3 | Concept gate status count. |
| concept_gate_blocked_raw_file_missing | 106 | Concept gate status count. |
| concept_gate_ready_for_manual_value_label_unit_key_audit | 9 | Concept gate status count. |
| variable_status_raw_candidate_not_matched | 65 | Variable verification status count. |
| variable_status_raw_not_inspected | 810 | Variable verification status count. |
| variable_status_ready_for_manual_value_audit | 42 | Variable verification status count. |

## Dataset Gate Status

| Dataset gate | Count |
|---|---:|
| blocked_raw_files_absent | 9 |
| blocked_candidate_file_or_variable_not_matched | 1 |

## Concept Gate Status

| Concept gate | Count |
|---|---:|
| blocked_raw_file_missing | 106 |
| blocked_missing_metadata_candidate | 12 |
| ready_for_manual_value_label_unit_key_audit | 9 |
| blocked_raw_candidate_not_matched | 3 |

## Variable Verification Status

| Variable status | Count |
|---|---:|
| raw_not_inspected | 810 |
| raw_candidate_not_matched | 65 |
| ready_for_manual_value_audit | 42 |

## Dataset Gate Rows

| batch_rank | idno | country | wave | raw_file_inventory_rows | raw_variable_catalog_rows | current_gate_status | next_action |
|---|---|---|---|---|---|---|---|
| 1 | ALB_2005_LSMS_v01_M | Albania | 2005 | 46 | 1187 | blocked_candidate_file_or_variable_not_matched | map downloaded raw filenames/variables to candidate metadata and rerun workbook |
| 2 | ETH_2021_ESPS-W5_v02_M | Ethiopia | 2021-2022 | 0 | 0 | blocked_raw_files_absent | download complete original raw package into local target folder |
| 3 | ETH_2018_ESS_v04_M | Ethiopia | 2018-2019 | 0 | 0 | blocked_raw_files_absent | download complete original raw package into local target folder |
| 4 | JAM_1997_SLC_v01_M | Jamaica | 1997 | 0 | 0 | blocked_raw_files_absent | download complete original raw package into local target folder |
| 5 | KGZ_1993_KMPS_v01_M | Kyrgyz Republic | 1993 | 0 | 0 | blocked_raw_files_absent | download complete original raw package into local target folder |
| 6 | MWI_2007-2009_MTM_v01_M | Malawi | 2007-2009 | 0 | 0 | blocked_raw_files_absent | download complete original raw package into local target folder |
| 7 | MWI_2004_IHS-II_v01_M | Malawi | 2004-2005 | 0 | 0 | blocked_raw_files_absent | download complete original raw package into local target folder |
| 8 | NPL_2010_LSS-III_v01_M | Nepal | 2010-2011 | 0 | 0 | blocked_raw_files_absent | download complete original raw package into local target folder |
| 9 | NGA_2012_GHSP-W2_v02_M | Nigeria | 2012-2013 | 0 | 0 | blocked_raw_files_absent | download complete original raw package into local target folder |
| 10 | NGA_2015_GHSP-W3_v02_M | Nigeria | 2015-2016 | 0 | 0 | blocked_raw_files_absent | download complete original raw package into local target folder |

## How To Use

1. Download complete original raw packages into each first-batch target folder.
2. Run `python script/17_audit_raw_downloads.py` and `python script/03_inspect_raw_schemas.py`.
3. Rerun `python script/38_build_first_batch_raw_verification_workbook.py`.
4. Fill the blank `fill_*` columns in `temp/first_batch_concept_verification_template.csv` and `temp/first_batch_variable_verification_template.csv` only after inspecting raw values, labels, units, recall periods, missing codes, levels, and merge keys.
5. Promote a row toward `temp/harmonization_recipe.csv` only when all critical evidence fields pass.

## Guardrails

- Metadata-only candidate variables do not prove concept availability.
- A raw schema match still does not prove that values, units, recall periods, or skip patterns are usable.
- Do not construct outcomes, climate links, models, mechanisms, or policy simulations from this workbook alone.

## Machine-Readable Outputs

- `result/first_batch_dataset_verification_gate.csv`
- `temp/first_batch_concept_verification_template.csv`
- `temp/first_batch_variable_verification_template.csv`
- `result/first_batch_raw_verification_workbook_summary.csv`
