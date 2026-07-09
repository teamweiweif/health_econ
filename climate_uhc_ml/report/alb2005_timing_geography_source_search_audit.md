# ALB_2005 Timing/Geography Source Search Audit

Status: fail-closed climate-linkage source search. This audit searches local ALB_2005 raw schema, questionnaires, and upstream timing/geography summaries for household interview timing, current-location geography, coordinates, and PSU/cluster evidence. It does not write `data/`, does not construct climate exposures, and does not promote any row to geography crosswalk, interview timing, or climate linkage readiness.

## Bottom Line

- Local raw-schema and questionnaire wording provide leads, but upstream audits still verify zero household interview timing rows and zero coordinate/GPS candidate rows.
- Partial district variables exist in `filters.sav`, but they are not full-coverage verified geography and cannot support climate linkage without a defensible boundary/crosswalk strategy.
- PSU/cluster keys are observed, but no coordinate or admin crosswalk is verified for climate extraction.
- Geography-crosswalk-ready, interview-timing-ready, and climate-linkage-ready rows from this audit: 0.
- Current decision: `blocked_alb2005_timing_geography_source_search_not_ready`.

## Summary

| Metric | Value | Interpretation |
|---|---:|---|
| alb2005_timing_geography_source_search_rows | 11 | Rows in the ALB_2005 timing/geography source-search audit. |
| alb2005_timing_geography_source_search_target_concepts | 5 | Climate-linkage concepts searched locally. |
| alb2005_timing_geography_source_search_local_files_scanned | 46 | Local ALB_2005 raw/schema file rows scanned. |
| alb2005_timing_geography_source_search_local_variables_scanned | 1187 | Local ALB_2005 raw-variable rows scanned. |
| alb2005_timing_geography_source_search_questionnaire_workbooks_scanned | 2 | Local ALB_2005 questionnaire workbooks scanned. |
| alb2005_timing_geography_source_search_raw_targets_with_hits | 4 | Target concepts with raw-schema phrase hits. |
| alb2005_timing_geography_source_search_questionnaire_targets_with_hits | 5 | Target concepts with questionnaire phrase hits. |
| alb2005_timing_geography_source_search_legacy_questionnaire_timing_rows | 83 | Legacy questionnaire timing/control rows observed upstream. |
| alb2005_timing_geography_source_search_verified_household_timing_rows | 0 | Verified ALB_2005 household interview timing rows; should remain zero. |
| alb2005_timing_geography_source_search_coordinate_candidate_rows | 0 | Raw coordinate/GPS candidate rows; should remain zero. |
| alb2005_timing_geography_source_search_partial_district_variable_rows | 2 | Partial current district variables observed upstream. |
| alb2005_timing_geography_source_search_partial_district_name_nonmissing_rows | 1899 | Nonmissing partial district-name rows observed upstream. |
| alb2005_timing_geography_source_search_partial_district_code_nonmissing_rows | 329 | Nonmissing partial district-code rows observed upstream. |
| alb2005_timing_geography_source_search_required_value_key_timing_rows | 0 | Verified interview timing rows observed in required value/key audit; should remain zero. |
| alb2005_timing_geography_source_search_required_value_key_coordinate_rows | 0 | Coordinate-ready rows observed in required value/key audit; should remain zero. |
| alb2005_timing_geography_source_search_geography_crosswalk_ready_rows | 0 | Rows promoted to geography crosswalk readiness by this audit; intentionally zero. |
| alb2005_timing_geography_source_search_interview_timing_ready_rows | 0 | Rows promoted to interview timing readiness by this audit; intentionally zero. |
| alb2005_timing_geography_source_search_climate_linkage_ready_rows | 0 | Rows promoted to climate linkage after this audit; intentionally zero. |
| alb2005_timing_geography_source_search_current_decision | blocked_alb2005_timing_geography_source_search_not_ready | Current fail-closed decision for ALB_2005 timing/geography source-search evidence. |

## Source Search Rows

| audit_family | target_concept | raw_phrase_hit_count | questionnaire_phrase_hit_count | candidate_file_count | upstream_verified_household_timing_rows | upstream_coordinate_candidate_rows | upstream_climate_linkage_ready_rows | evidence_status |
|---|---|---|---|---|---|---|---|---|
| raw_schema_source_search | household_interview_timing | 1 | 75 | 4 | 0 | 0 | 0 | raw_schema_hits_seen_but_not_verified_climate_inputs |
| questionnaire_source_search | household_interview_timing | 1 | 75 | 4 | 0 | 0 | 0 | questionnaire_form_design_seen_raw_value_gap_remains |
| raw_schema_source_search | gps_or_coordinates | 0 | 1 | 0 | 0 | 0 | 0 | raw_schema_hits_not_found |
| questionnaire_source_search | gps_or_coordinates | 0 | 1 | 0 | 0 | 0 | 0 | questionnaire_form_design_seen_raw_value_gap_remains |
| raw_schema_source_search | current_admin_geography | 43 | 29 | 5 | 0 | 0 | 0 | raw_schema_hits_seen_but_not_verified_climate_inputs |
| questionnaire_source_search | current_admin_geography | 43 | 29 | 5 | 0 | 0 | 0 | questionnaire_form_design_seen_raw_value_gap_remains |
| raw_schema_source_search | psu_cluster_keys | 44 | 1 | 3 | 0 | 0 | 0 | raw_schema_hits_seen_but_not_verified_climate_inputs |
| questionnaire_source_search | psu_cluster_keys | 44 | 1 | 3 | 0 | 0 | 0 | questionnaire_form_design_seen_raw_value_gap_remains |
| raw_schema_source_search | fieldwork_control_forms | 31 | 16 | 4 | 0 | 0 | 0 | raw_schema_hits_seen_but_not_verified_climate_inputs |
| questionnaire_source_search | fieldwork_control_forms | 31 | 16 | 4 | 0 | 0 | 0 | questionnaire_form_design_seen_raw_value_gap_remains |
| upstream_crosscheck | upstream_timing_geography_audits | 0 | 0 | 0 | 0 | 0 | 0 | upstream_timing_geography_remains_fail_closed |

## Interpretation

- Questionnaire/control-form timing fields are design evidence only; they do not prove that the released raw files contain usable household interview dates or months.
- Partial district name/code rows require coverage, boundary, historical-definition, and current-location validation before admin-level climate aggregation.
- Without household interview timing and climate-ready geography, ALB_2005 cannot enter climate-linked outcome construction or any reduced-form/causal ML stage.

## Machine-Readable Outputs

- `temp/alb2005_timing_geography_source_search_audit.csv`
- `result/alb2005_timing_geography_source_search_summary.csv`
