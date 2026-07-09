# Priority Manual Verification Decision Gate

Status: fail-closed consumer of the priority workbook `fill_*` fields. This
report does not promote data by itself; it verifies whether the human raw-value
audit evidence is complete enough to allow harmonization-recipe review.

## Summary

| Metric | Value | Interpretation |
|---|---:|---|
| priority_manual_decision_dataset_rows | 13 | Priority waves with manual verification decision gates. |
| priority_manual_requirement_decision_rows | 104 | Requirement-level manual verification audit rows. |
| priority_manual_concept_decision_rows | 169 | Concept-level manual verification audit rows. |
| priority_manual_variable_decision_rows | 1214 | Variable-level manual verification audit rows. |
| priority_manual_requirements_verified | 0 | Requirement rows passing source and fill-field manual verification. |
| priority_manual_concepts_verified | 0 | Concept rows passing source and fill-field manual verification. |
| priority_manual_variables_verified | 0 | Variable rows passing source and fill-field manual verification. |
| priority_financial_protection_manual_ready_countries | 0 | Countries with financial-protection manual verification ready. |
| priority_double_failure_manual_ready_waves | 0 | Country-waves with double-failure manual verification ready. |
| priority_analysis_ready_candidates | 0 | Country-waves ready for harmonization recipe review and climate-linked data promotion. |
| priority_manual_handoff_readmes_written | 13 | Per-wave manual verification decision README files written. |
| modeling_gate_status | blocked | Models remain blocked until promoted registry thresholds and accepted climate linkage pass. |
| dataset_manual_status_blocked_raw_module_coverage_missing | 13 | Dataset manual verification status count. |
| requirement_manual_status_blocked_source_gate_not_ready | 104 | Requirement manual verification status count. |
| concept_manual_status_blocked_source_gate_not_ready | 169 | Concept manual verification status count. |
| variable_manual_status_blocked_source_gate_not_ready | 1214 | Variable manual verification status count. |

## Dataset Decisions

| acquisition_batch_rank | idno | country | wave | manual_verification_status | requirements_passed | concepts_passed | variables_passed | archive_or_direct_targets_covered | analysis_ready_candidate |
|---|---|---|---|---|---|---|---|---|---|
| 1 | ETH_2021_ESPS-W5_v02_M | Ethiopia | 2021-2022 | blocked_raw_module_coverage_missing | 0 | 0 | 0 | 0 | 0 |
| 2 | ETH_2018_ESS_v04_M | Ethiopia | 2018-2019 | blocked_raw_module_coverage_missing | 0 | 0 | 0 | 0 | 0 |
| 3 | MWI_2007-2009_MTM_v01_M | Malawi | 2007-2009 | blocked_raw_module_coverage_missing | 0 | 0 | 0 | 0 | 0 |
| 4 | NGA_2012_GHSP-W2_v02_M | Nigeria | 2012-2013 | blocked_raw_module_coverage_missing | 0 | 0 | 0 | 0 | 0 |
| 5 | NGA_2015_GHSP-W3_v02_M | Nigeria | 2015-2016 | blocked_raw_module_coverage_missing | 0 | 0 | 0 | 0 | 0 |
| 6 | NGA_2010_GHSP-W1_v03_M | Nigeria | 2010-2011 | blocked_raw_module_coverage_missing | 0 | 0 | 0 | 0 | 0 |
| 7 | TZA_2008_NPS-R1_v03_M | Tanzania | 2008-2009 | blocked_raw_module_coverage_missing | 0 | 0 | 0 | 0 | 0 |
| 8 | TZA_2010_NPS-R2_v03_M | Tanzania | 2010-2011 | blocked_raw_module_coverage_missing | 0 | 0 | 0 | 0 | 0 |
| 9 | TZA_2012_NPS-R3_v01_M | Tanzania | 2012-2013 | blocked_raw_module_coverage_missing | 0 | 0 | 0 | 0 | 0 |
| 10 | UGA_2014_SAGE-EL_v01_M | Uganda | 2014 | blocked_raw_module_coverage_missing | 0 | 0 | 0 | 0 | 0 |
| 11 | JAM_1997_SLC_v01_M | Jamaica | 1997 | blocked_raw_module_coverage_missing | 0 | 0 | 0 | 0 | 0 |
| 12 | KGZ_1993_KMPS_v01_M | Kyrgyz Republic | 1993 | blocked_raw_module_coverage_missing | 0 | 0 | 0 | 0 | 0 |
| 13 | NPL_2010_LSS-III_v01_M | Nepal | 2010-2011 | blocked_raw_module_coverage_missing | 0 | 0 | 0 | 0 | 0 |

## Rule

The decision gate requires source gates plus manual `fill_*` fields. A blank or
ambiguous fill value is treated as not passing. Manual evidence is preserved by
`script/126_build_priority_raw_verification_workbook.py` when templates are
rebuilt.

## Machine-Readable Outputs

- `temp/priority_manual_verification_decision_gate.csv`
- `temp/priority_manual_requirement_decision_audit.csv`
- `temp/priority_manual_concept_decision_audit.csv`
- `temp/priority_manual_variable_decision_audit.csv`
- `result/priority_manual_verification_decision_summary.csv`
