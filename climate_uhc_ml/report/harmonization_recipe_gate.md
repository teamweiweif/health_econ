# Harmonization Recipe Gate

Status: fail-closed. Metadata scaffold rows are not executable harmonization recipes. A row becomes a verified recipe candidate only after the raw file is present, the raw variable is found in the inspected schema, and a value/unit/recall/key/missing-code/lineage audit passes.

## Counts

| Metric | Value | Interpretation |
|---|---:|---|
| gate_rows | 1204 | Scaffold rows assessed by raw-file, raw-variable, and value-audit gates. |
| value_audit_template_rows | 7153 | Rows in the post-download value-audit template. |
| verified_candidate_rows | 0 | Rows that can be copied into a real harmonization recipe after all gates pass. |
| country_wave_rows | 28 | Country-waves assessed for minimum harmonization readiness. |
| ready_country_wave_rows | 0 | Country-waves ready for verified recipe assembly. |
| blocked_country_wave_rows | 28 | Country-waves still blocked by required raw evidence. |
| raw_file_inventory_rows | 209 | Raw file inventory rows available to the gate. |
| raw_variable_catalog_rows | 5410 | Raw variable catalog rows available to the gate. |
| value_audit_rows | 431 | Manually or programmatically completed value-audit rows. |
| recipe_gate_status_blocked_raw_file_missing | 1174 | Recipe gate status count. |
| recipe_gate_status_blocked_raw_variable_missing | 1 | Recipe gate status count. |
| recipe_gate_status_blocked_value_audit_missing | 29 | Recipe gate status count. |
| readiness_status_blocked_until_required_raw_value_audits_pass | 28 | Country-wave readiness status count. |
| required_flag_no | 168 | Required/recommended/optional scaffold row count. |
| required_flag_recommended | 588 | Required/recommended/optional scaffold row count. |
| required_flag_yes | 448 | Required/recommended/optional scaffold row count. |
| value_audit_status_raw_value_summary_available_manual_interpretation_required | 27 | Value-audit status count. |
| value_audit_status_raw_variable_rejected_false_survey_weight_birth_measure | 2 | Value-audit status count. |
| value_audit_status_value_audit_blocked_until_raw_variable_seen | 1175 | Value-audit status count. |

## Gate Status

| Recipe gate status | Count |
|---|---:|
| blocked_raw_file_missing | 1174 |
| blocked_value_audit_missing | 29 |
| blocked_raw_variable_missing | 1 |

## Raw File Status

| Raw file status | Count |
|---|---:|
| raw_file_not_matched | 1174 |
| raw_file_seen | 30 |

## Raw Variable Status

| Raw variable status | Count |
|---|---:|
| raw_variable_not_matched | 1175 |
| raw_variable_seen | 29 |

## Value Audit Status

| Value audit status | Count |
|---|---:|
| value_audit_blocked_until_raw_variable_seen | 1175 |
| raw_value_summary_available_manual_interpretation_required | 27 |
| raw_variable_rejected_false_survey_weight_birth_measure | 2 |

## Country-Wave Readiness

| Readiness status | Count |
|---|---:|
| blocked_until_required_raw_value_audits_pass | 28 |

| bundle_rank | country | wave | idno | required_variable_rows | recipe_ready_required_rows | blocked_required_rows | readiness_status |
|---|---|---|---|---|---|---|---|
| 1 | Ethiopia | 2021-2022 | ETH_2021_ESPS-W5_v02_M | 16 | 0 | 16 | blocked_until_required_raw_value_audits_pass |
| 2 | Ethiopia | 2018-2019 | ETH_2018_ESS_v04_M | 16 | 0 | 16 | blocked_until_required_raw_value_audits_pass |
| 3 | Malawi | 2007-2009 | MWI_2007-2009_MTM_v01_M | 16 | 0 | 16 | blocked_until_required_raw_value_audits_pass |
| 4 | Nigeria | 2012-2013 | NGA_2012_GHSP-W2_v02_M | 16 | 0 | 16 | blocked_until_required_raw_value_audits_pass |
| 5 | Nigeria | 2015-2016 | NGA_2015_GHSP-W3_v02_M | 16 | 0 | 16 | blocked_until_required_raw_value_audits_pass |
| 6 | Nigeria | 2010-2011 | NGA_2010_GHSP-W1_v03_M | 16 | 0 | 16 | blocked_until_required_raw_value_audits_pass |
| 7 | Tanzania | 2008-2009 | TZA_2008_NPS-R1_v03_M | 16 | 0 | 16 | blocked_until_required_raw_value_audits_pass |
| 8 | Tanzania | 2010-2011 | TZA_2010_NPS-R2_v03_M | 16 | 0 | 16 | blocked_until_required_raw_value_audits_pass |
| 9 | Tanzania | 2012-2013 | TZA_2012_NPS-R3_v01_M | 16 | 0 | 16 | blocked_until_required_raw_value_audits_pass |
| 10 | Tanzania | 2014-2015 | TZA_2014_NPS-R4_v03_M | 16 | 0 | 16 | blocked_until_required_raw_value_audits_pass |
| 11 | Tanzania | 2020-2022 | TZA_2020_NPS-R5_v02_M | 16 | 0 | 16 | blocked_until_required_raw_value_audits_pass |
| 12 | Uganda | 2014 | UGA_2014_SAGE-EL_v01_M | 16 | 0 | 16 | blocked_until_required_raw_value_audits_pass |
| 13 | Uganda | 2012 | UGA_2012_SAGE-BL_v01_M | 16 | 0 | 16 | blocked_until_required_raw_value_audits_pass |
| 14 | Uganda | 2013 | UGA_2013_SAGE-ML_v01_M | 16 | 0 | 16 | blocked_until_required_raw_value_audits_pass |
| 15 | Malawi | 2004-2005 | MWI_2004_IHS-II_v01_M | 16 | 0 | 16 | blocked_until_required_raw_value_audits_pass |
| 16 | Albania | 2005 | ALB_2005_LSMS_v01_M | 16 | 0 | 16 | blocked_until_required_raw_value_audits_pass |
| 17 | Jamaica | 1997 | JAM_1997_SLC_v01_M | 16 | 0 | 16 | blocked_until_required_raw_value_audits_pass |
| 18 | Kyrgyz Republic | 1993 | KGZ_1993_KMPS_v01_M | 16 | 0 | 16 | blocked_until_required_raw_value_audits_pass |
| 19 | Nepal | 2010-2011 | NPL_2010_LSS-III_v01_M | 16 | 0 | 16 | blocked_until_required_raw_value_audits_pass |
| 20 | Sierra Leone | 2011 | SLE_2011_SLIHS_v01_M | 16 | 0 | 16 | blocked_until_required_raw_value_audits_pass |

## Guardrails

- Do not create `temp/harmonization_recipe.csv` from `temp/harmonization_recipe_scaffold.csv`.
- Do not promote a row based only on metadata labels or a raw variable-name match.
- Do not construct `data/harmonized_household.csv` until required variables pass value, unit, recall-period, key, missing-code, and lineage checks.
- Use `temp/harmonization_value_audit_template.csv` as the checklist after raw downloads, then save completed checks as `temp/harmonization_value_audit.csv`.

## Outputs

- `temp/harmonization_recipe_gate.csv`
- `temp/harmonization_value_audit_template.csv`
- `temp/first_batch_harmonization_value_audit_auto.csv` when first-batch raw value summaries exist
- `temp/harmonization_recipe_verified_candidates.csv`
- `result/harmonization_readiness_matrix.csv`
- `result/harmonization_recipe_gate_summary.csv`
