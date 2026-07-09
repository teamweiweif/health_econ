# ALB_2005 Consumption Component Source Search Audit

Status: fail-closed local source search. This audit searches local ALB_2005 raw-variable metadata, file inventory, questionnaire workbooks, and source-code-like files for the public-metadata consumption aggregate/component variables. It does not write `data/`, does not reconstruct consumption, does not construct CHE/SDG outcomes, and does not promote any row to harmonization, outcome construction, SDG 3.8.2, or climate linkage.

## Bottom Line

- The exact local raw-variable search finds only the already-known `totcons` target from the checked public metadata aggregate/component set.
- The missing public-metadata components and `totcons05` are still not found as exact local raw variables.
- Local module names and questionnaire text provide item-level leads for manual review, but no local construction-code hit proves the final aggregate formula, period, or price basis.
- SDG 3.8.2, recipe-ready, outcome-ready, and climate-linkage-ready rows from this audit: 0.
- Current decision: `blocked_alb2005_consumption_component_source_search_not_ready`.

## Summary

| Metric | Value | Interpretation |
|---|---:|---|
| alb2005_consumption_component_source_search_rows | 37 | Rows in the ALB_2005 consumption component source-search audit. |
| alb2005_consumption_component_source_search_target_variables | 9 | Public metadata aggregate/component variables searched locally. |
| alb2005_consumption_component_source_search_local_files_scanned | 46 | Local ALB_2005 raw/schema file rows scanned. |
| alb2005_consumption_component_source_search_local_variables_scanned | 1187 | Local ALB_2005 raw-variable rows scanned. |
| alb2005_consumption_component_source_search_questionnaire_workbooks_scanned | 2 | Local ALB_2005 questionnaire workbooks scanned for phrase leads. |
| alb2005_consumption_component_source_search_construction_code_files_found | 0 | Local source-code-like files found under the ALB_2005 extract. |
| alb2005_consumption_component_source_search_exact_target_variables_found | 1 | Target variables with exact local raw-variable hits. |
| alb2005_consumption_component_source_search_exact_target_variables_missing | 8 | Target variables without exact local raw-variable hits. |
| alb2005_consumption_component_source_search_label_phrase_targets_found | 5 | Target variables with local raw-label/phrase hits. |
| alb2005_consumption_component_source_search_questionnaire_phrase_targets_found | 5 | Target variables with questionnaire phrase leads. |
| alb2005_consumption_component_source_search_construction_code_targets_found | 0 | Target variables with local construction-code text hits. |
| alb2005_consumption_component_source_search_candidate_module_target_rows | 9 | Target variables with module-name leads only. |
| alb2005_consumption_component_source_search_recipe_ready_rows | 0 | Rows promoted to a harmonization recipe by this audit; intentionally zero. |
| alb2005_consumption_component_source_search_outcome_ready_rows | 0 | Rows promoted to outcome construction by this audit; intentionally zero. |
| alb2005_consumption_component_source_search_sdg382_ready_rows | 0 | Rows promoted to SDG 3.8.2 denominator readiness by this audit; intentionally zero. |
| alb2005_consumption_component_source_search_climate_linkage_ready_rows | 0 | Rows promoted to climate linkage by this audit; intentionally zero. |
| alb2005_consumption_component_source_search_current_decision | blocked_alb2005_consumption_component_source_search_not_ready | Current fail-closed decision for the ALB_2005 component source-search evidence. |

## Source Search Rows

| audit_family | target_variable | exact_variable_hit_count | label_phrase_hit_count | questionnaire_phrase_hit_count | candidate_module_file_count | construction_code_file_count | evidence_status |
|---|---|---|---|---|---|---|---|
| schema_exact_variable_search | food | 0 | 1 | 1 | 4 | 0 | exact_local_raw_variable_not_found |
| schema_label_phrase_search | food | 0 | 1 | 1 | 4 | 0 | local_label_phrase_hit_seen_not_recipe |
| questionnaire_and_module_search | food | 0 | 1 | 1 | 4 | 0 | item_module_or_questionnaire_lead_seen_not_aggregate_recipe |
| construction_code_search | food | 0 | 1 | 1 | 4 | 0 | construction_code_hit_not_found |
| schema_exact_variable_search | edu | 0 | 1 | 0 | 3 | 0 | exact_local_raw_variable_not_found |
| schema_label_phrase_search | edu | 0 | 1 | 0 | 3 | 0 | local_label_phrase_hit_seen_not_recipe |
| questionnaire_and_module_search | edu | 0 | 1 | 0 | 3 | 0 | item_module_or_questionnaire_lead_seen_not_aggregate_recipe |
| construction_code_search | edu | 0 | 1 | 0 | 3 | 0 | construction_code_hit_not_found |
| schema_exact_variable_search | durcons | 0 | 1 | 6 | 9 | 0 | exact_local_raw_variable_not_found |
| schema_label_phrase_search | durcons | 0 | 1 | 6 | 9 | 0 | local_label_phrase_hit_seen_not_recipe |
| questionnaire_and_module_search | durcons | 0 | 1 | 6 | 9 | 0 | item_module_or_questionnaire_lead_seen_not_aggregate_recipe |
| construction_code_search | durcons | 0 | 1 | 6 | 9 | 0 | construction_code_hit_not_found |
| schema_exact_variable_search | nfoodc | 0 | 0 | 0 | 3 | 0 | exact_local_raw_variable_not_found |
| schema_label_phrase_search | nfoodc | 0 | 0 | 0 | 3 | 0 | local_label_phrase_hit_not_found |
| questionnaire_and_module_search | nfoodc | 0 | 0 | 0 | 3 | 0 | item_module_or_questionnaire_lead_seen_not_aggregate_recipe |
| construction_code_search | nfoodc | 0 | 0 | 0 | 3 | 0 | construction_code_hit_not_found |
| schema_exact_variable_search | nfood05 | 0 | 0 | 2 | 3 | 0 | exact_local_raw_variable_not_found |
| schema_label_phrase_search | nfood05 | 0 | 0 | 2 | 3 | 0 | local_label_phrase_hit_not_found |
| questionnaire_and_module_search | nfood05 | 0 | 0 | 2 | 3 | 0 | item_module_or_questionnaire_lead_seen_not_aggregate_recipe |
| construction_code_search | nfood05 | 0 | 0 | 2 | 3 | 0 | construction_code_hit_not_found |
| schema_exact_variable_search | totutil | 0 | 0 | 5 | 6 | 0 | exact_local_raw_variable_not_found |
| schema_label_phrase_search | totutil | 0 | 0 | 5 | 6 | 0 | local_label_phrase_hit_not_found |
| questionnaire_and_module_search | totutil | 0 | 0 | 5 | 6 | 0 | item_module_or_questionnaire_lead_seen_not_aggregate_recipe |
| construction_code_search | totutil | 0 | 0 | 5 | 6 | 0 | construction_code_hit_not_found |
| schema_exact_variable_search | totutil05 | 0 | 0 | 5 | 6 | 0 | exact_local_raw_variable_not_found |
| schema_label_phrase_search | totutil05 | 0 | 0 | 5 | 6 | 0 | local_label_phrase_hit_not_found |
| questionnaire_and_module_search | totutil05 | 0 | 0 | 5 | 6 | 0 | item_module_or_questionnaire_lead_seen_not_aggregate_recipe |
| construction_code_search | totutil05 | 0 | 0 | 5 | 6 | 0 | construction_code_hit_not_found |
| schema_exact_variable_search | totcons | 1 | 1 | 0 | 2 | 0 | exact_local_raw_variable_seen |
| schema_label_phrase_search | totcons | 1 | 1 | 0 | 2 | 0 | local_label_phrase_hit_seen_not_recipe |
| questionnaire_and_module_search | totcons | 1 | 1 | 0 | 2 | 0 | item_module_or_questionnaire_lead_seen_not_aggregate_recipe |
| construction_code_search | totcons | 1 | 1 | 0 | 2 | 0 | construction_code_hit_not_found |
| schema_exact_variable_search | totcons05 | 0 | 1 | 0 | 2 | 0 | exact_local_raw_variable_not_found |
| schema_label_phrase_search | totcons05 | 0 | 1 | 0 | 2 | 0 | local_label_phrase_hit_seen_not_recipe |
| questionnaire_and_module_search | totcons05 | 0 | 1 | 0 | 2 | 0 | item_module_or_questionnaire_lead_seen_not_aggregate_recipe |
| construction_code_search | totcons05 | 0 | 1 | 0 | 2 | 0 | construction_code_hit_not_found |
| upstream_crosscheck | all_targets | 0 | 0 | 0 | 0 | 0 | upstream_aggregate_crosswalk_remains_fail_closed |

## Interpretation

- A local item module or questionnaire phrase is not equivalent to a documented survey-team aggregate construction recipe.
- The denominator variant remains unresolved because `totcons05` and the public-metadata formula components are absent from local exact raw-variable evidence.
- This audit strengthens the no-promotion decision: any ALB_2005 CHE/SDG denominator would still require official aggregate construction documentation or a raw package version containing the missing component variables.
- Climate-linked analysis remains independently blocked by missing verified household interview timing and climate-ready geography.

## Machine-Readable Outputs

- `temp/alb2005_consumption_component_source_search_audit.csv`
- `result/alb2005_consumption_component_source_search_summary.csv`
