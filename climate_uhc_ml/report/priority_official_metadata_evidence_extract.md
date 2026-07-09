# Priority Official Metadata Evidence Extract

Status: official DDI/XML metadata evidence extracted for the priority candidate
variables. This layer connects candidate variables to official file names,
variable labels, valid/invalid counts, ranges, and value categories where DDI
metadata expose them. It does not verify raw microdata values.

## Summary

| Metric | Value | Interpretation |
|---|---:|---|
| priority_official_metadata_dataset_rows | 13 | Priority datasets with official metadata evidence extracts. |
| priority_official_metadata_candidate_variable_rows | 1214 | Priority candidate variables checked against official DDI/XML metadata. |
| priority_official_metadata_category_rows | 4512 | Official DDI category/value-label rows extracted for candidate variables, capped per candidate. |
| priority_official_metadata_variable_match_rows | 1198 | Candidate variables with a DDI variable-name match. |
| priority_official_metadata_variable_file_match_rows | 1198 | Candidate variables matching both DDI variable name and file name. |
| priority_official_metadata_no_match_rows | 16 | Candidate variables not found in parsed DDI metadata. |
| priority_official_metadata_variables_with_categories | 717 | Candidate variables with official category/value-label metadata. |
| priority_official_metadata_variables_with_valid_counts | 1186 | Candidate variables with DDI valid-count metadata. |
| priority_official_metadata_variables_with_invalid_counts | 834 | Candidate variables with DDI invalid-count metadata. |
| priority_official_metadata_dataset_complete_rows | 3 | Datasets with complete official metadata evidence under current thresholds. |
| priority_official_metadata_handoff_readmes_written | 13 | Per-wave official metadata evidence handoff README files written. |
| modeling_gate_status | blocked | Official metadata evidence does not satisfy raw value verification or climate-linkage promotion gates. |
| priority_official_metadata_variable_status_official_ddi_variable_and_file_evidence_present | 1198 | Variable-level official metadata evidence status count. |
| priority_official_metadata_variable_status_official_ddi_variable_evidence_missing | 16 | Variable-level official metadata evidence status count. |
| priority_official_metadata_match_status_ddi_variable_and_file_match | 1198 | DDI match status count. |
| priority_official_metadata_match_status_no_ddi_variable_match | 16 | DDI match status count. |
| priority_official_metadata_dataset_status_complete_official_metadata_evidence_extract | 3 | Dataset-level official metadata evidence status count. |
| priority_official_metadata_dataset_status_partial_official_metadata_evidence_extract | 10 | Dataset-level official metadata evidence status count. |

## Dataset Evidence

| acquisition_batch_rank | idno | candidate_variable_rows | ddi_variable_match_rows | ddi_file_match_rows | ddi_no_match_rows | official_metadata_evidence_status |
|---|---|---|---|---|---|---|
| 1 | ETH_2021_ESPS-W5_v02_M | 107 | 107 | 107 | 0 | complete_official_metadata_evidence_extract |
| 2 | ETH_2018_ESS_v04_M | 102 | 102 | 102 | 0 | complete_official_metadata_evidence_extract |
| 3 | MWI_2007-2009_MTM_v01_M | 128 | 126 | 126 | 2 | partial_official_metadata_evidence_extract |
| 4 | NGA_2012_GHSP-W2_v02_M | 79 | 78 | 78 | 1 | partial_official_metadata_evidence_extract |
| 5 | NGA_2015_GHSP-W3_v02_M | 90 | 89 | 89 | 1 | partial_official_metadata_evidence_extract |
| 6 | NGA_2010_GHSP-W1_v03_M | 67 | 66 | 66 | 1 | partial_official_metadata_evidence_extract |
| 7 | TZA_2008_NPS-R1_v03_M | 105 | 104 | 104 | 1 | partial_official_metadata_evidence_extract |
| 8 | TZA_2010_NPS-R2_v03_M | 91 | 90 | 90 | 1 | partial_official_metadata_evidence_extract |
| 9 | TZA_2012_NPS-R3_v01_M | 115 | 115 | 115 | 0 | complete_official_metadata_evidence_extract |
| 10 | UGA_2014_SAGE-EL_v01_M | 96 | 93 | 93 | 3 | partial_official_metadata_evidence_extract |
| 11 | JAM_1997_SLC_v01_M | 66 | 65 | 65 | 1 | partial_official_metadata_evidence_extract |
| 12 | KGZ_1993_KMPS_v01_M | 62 | 59 | 59 | 3 | partial_official_metadata_evidence_extract |
| 13 | NPL_2010_LSS-III_v01_M | 106 | 104 | 104 | 2 | partial_official_metadata_evidence_extract |

## No-Match Candidate Variables

| candidate_row_id | idno | concept | candidate_files | candidate_raw_variable | template_raw_label |
|---|---|---|---|---|---|
| 280 | MWI_2007-2009_MTM_v01_M | insurance |  |  |  |
| 320 | MWI_2007-2009_MTM_v01_M | strata |  |  |  |
| 404 | NGA_2012_GHSP-W2_v02_M | strata |  |  |  |
| 489 | NGA_2015_GHSP-W3_v02_M | strata |  |  |  |
| 566 | NGA_2010_GHSP-W1_v03_M | strata |  |  |  |
| 627 | TZA_2008_NPS-R1_v03_M | insurance |  |  |  |
| 728 | TZA_2010_NPS-R2_v03_M | insurance |  |  |  |
| 938 | UGA_2014_SAGE-EL_v01_M | insurance |  |  |  |
| 952 | UGA_2014_SAGE-EL_v01_M | psu_cluster |  |  |  |
| 969 | UGA_2014_SAGE-EL_v01_M | strata |  |  |  |
| 1010 | JAM_1997_SLC_v01_M | household_id |  |  |  |
| 1077 | KGZ_1993_KMPS_v01_M | insurance |  |  |  |
| 1084 | KGZ_1993_KMPS_v01_M | psu_cluster |  |  |  |
| 1101 | KGZ_1993_KMPS_v01_M | strata |  |  |  |
| 1152 | NPL_2010_LSS-III_v01_M | household_id |  |  |  |
| 1153 | NPL_2010_LSS-III_v01_M | insurance |  |  |  |

## Guardrail

Official metadata is not raw value verification. Promotion still requires the
complete original raw package and manual checks of values, labels, units,
recall periods, missing codes, skip patterns, merge keys, sample levels, and
accepted CHIRPS/ERA5 linkage.

## Machine-Readable Outputs

- `temp/priority_official_metadata_variable_evidence.csv`
- `temp/priority_official_metadata_category_evidence.csv`
- `temp/priority_official_metadata_dataset_evidence.csv`
- `result/priority_official_metadata_evidence_summary.csv`
