# Metadata Candidate Quality Audit

Status: metadata-only variable hits have been scored for confidence. This is a download-prioritization audit only; it does not verify raw variables or select the final analytical sample.

## Counts

| Variable-row confidence | Count |
|---|---:|
| high | 11566 |
| moderate | 6751 |
| low | 6115 |
| likely_false_positive | 926 |

| Country-wave quality tier | Count |
|---|---:|
| tier_5_no_variable_map_evidence | 1053 |
| tier_1_quality_supported_financial_and_access_download | 22 |
| tier_4_metadata_present_but_noisy_or_incomplete | 7 |
| tier_3_quality_supported_access_only_download | 6 |

## Summary Metrics

| Metric | Value | Interpretation |
|---|---:|---|
| variable_map_rows | 25358 | Metadata-only variable-map rows scored for confidence; none are raw-verified. |
| high_confidence_variable_rows | 11566 | Strong label/name evidence, still requiring raw values, units, and merge-key checks. |
| moderate_confidence_variable_rows | 6751 | Useful for manual download targeting, not for final sample selection. |
| likely_false_positive_variable_rows | 926 | Metadata hits with context suggesting the keyword match is probably not the target concept. |
| quality_supported_financial_country_waves | 22 | Country-waves with moderate/high metadata support for budget, OOP, weights, timing, and geography. |
| quality_supported_double_failure_country_waves | 22 | Country-waves with quality-supported financial and access-core metadata. |
| sample_gate_metadata_main_candidates | 30 | Original sample-gate metadata candidates before this confidence screen. |
| sample_gate_main_candidates_with_quality_financial_core | 17 | Still metadata-only; this count is a better raw-download priority signal, not an analytical sample. |
| tier_count_tier_1_quality_supported_financial_and_access_download | 22 | Country-wave metadata-quality tier count. |
| tier_count_tier_3_quality_supported_access_only_download | 6 | Country-wave metadata-quality tier count. |
| tier_count_tier_4_metadata_present_but_noisy_or_incomplete | 7 | Country-wave metadata-quality tier count. |
| tier_count_tier_5_no_variable_map_evidence | 1053 | Country-wave metadata-quality tier count. |

## Quality-Supported Download Priorities

`temp/metadata_quality_download_priority.csv` contains 28 quality-supported country-waves from tiers 1-3. These are still metadata-only download priorities, not selected analytical samples.


## False-Positive Examples

| IDNO | Map | Raw variable | Raw label | Reason |
|---|---|---|---|---|
|  | consumption:food_consumption | `rtotnfood` | real non food consumption per capita | food consumption candidate contains non-food terms |
|  | consumption:food_consumption | `MODULE 12 : NON FOOD EXPENDITURES` |  | food consumption candidate contains non-food terms |
|  | consumption:food_consumption | `MODULE 12 : NON FOOD EXPENDITURES` |  | food consumption candidate contains non-food terms |
|  | consumption:food_consumption | `MODULE 12 : NON FOOD EXPENDITURES` |  | food consumption candidate contains non-food terms |
| ALB_2005_LSMS_v01_M | consumption:food_consumption | `nfood05` | Total non-food consumption, including maintenance and repair of vehicles, housin | food consumption candidate contains non-food terms |
| ALB_2005_LSMS_v01_M | consumption:food_consumption | `nfoodc` | Total non-food consumption component in Old Lek (new lek=old lek/10) | food consumption candidate contains non-food terms |
| BEN_2021_EHCVM-2_v01_M | consumption:food_consumption | `s09aq07` | 9A.07. Quel est le montant total des autres dépenses non alimentaires ? | food consumption candidate contains non-food terms |
| CIV_2021_EHCVM-2_v01_M | consumption:food_consumption | `s09aq07` | 9A.07. Quel est le montant total des autres dépenses non alimentaires ? | food consumption candidate contains non-food terms |
| ETH_2021_ESPS-W5_v02_M | consumption:food_consumption | `nonfood_cons2` | Non-food consumption | food consumption candidate contains non-food terms |
| GNB_2021_EHCVM-2_v01_M | consumption:food_consumption | `s09aq07` | 9A.07. Quel est le montant total des autres dépenses non alimentaires ? | food consumption candidate contains non-food terms |
| JAM_1997_SLC_v01_M | consumption:food_consumption | `non_food` | Annual Non-Food Expenditure | food consumption candidate contains non-food terms |
| JAM_1997_SLC_v01_M | consumption:food_consumption | `ednoncon` | Total Annual NonFood Exp. for E | food consumption candidate contains non-food terms |

## Guardrail

Moderate/high metadata evidence means the label or variable name is plausible enough to prioritize manual raw download. It is not proof of analyzable content, correct units, recall period, mergeability, household/person level, or final sample eligibility.

## Machine-Readable Outputs

- `temp/variable_map_confidence_audit.csv`
- `temp/metadata_quality_download_priority.csv`
- `result/metadata_candidate_quality_audit.csv`
- `result/metadata_candidate_quality_summary.csv`
