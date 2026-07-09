# Sample Selection Audit

Status: final sample selection is blocked until raw microdata, raw values, merge keys, and harmonization recipes are verified. Metadata and raw-schema evidence are used only for prioritization and gate tracking.

## Gate Counts

- Country-wave screening rows: 1088
- Metadata-only main-sample candidates: 31
- Value-verified final-sample candidates: 0

| Sample gate status | Count |
|---|---:|
| excluded_or_low_priority_until_raw_evidence | 917 |
| metadata_secondary_access_candidate_not_selectable | 140 |
| metadata_main_sample_candidate_not_selectable | 30 |
| raw_schema_candidate_pending_value_harmonization_audit | 1 |

| Metadata feasibility score | Count |
|---|---:|
| 1 | 510 |
| 0 | 267 |
| 3 | 135 |
| 2 | 81 |
| 4 | 64 |
| 5 | 31 |

## No-Go Rules

| Rule | Status | Count/value | Threshold | Interpretation |
|---|---|---:|---|---|
| Main financial-protection sample has at least 6 value-verified countries with budget, OOP, geography, timing, and weights | fail | 0 | 6 countries | Do not proceed with main multi-country financial-protection paper until this passes. |
| At least 10 value-verified country-waves support both financial hardship and access/forgone-care outcomes | fail | 0 | 10 country-waves | Keep UHC double failure secondary until this passes. |
| Metadata-only main-sample candidates before raw inspection | informational | 31 waves; 18 countries | not a selection rule | Useful for download prioritization only; not valid for final analytical sample selection. |
| Raw value and verified harmonization gate | fail | 0 | at least 1 value-verified analytical row set before any final selection | Current final sample selection is blocked if this fails. |

## Guardrail

A survey with metadata hits for consumption, OOP health spending, timing, geography, and weights is not selected for analysis until raw files, raw variables, raw values, merge keys, and harmonization recipes are verified. This prevents result shopping and prevents final countries from being chosen from metadata-only or schema-only screens.

## Machine-Readable Outputs

- `result/sample_selection_gate_audit.csv`
- `result/sample_selection_gate_summary.csv`
