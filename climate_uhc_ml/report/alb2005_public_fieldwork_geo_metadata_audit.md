# ALB_2005 Public Fieldwork and Geography Metadata Audit

Status: fail-closed public-metadata evidence audit. The saved World Bank DDI metadata confirms a May to early-July 2005 main fieldwork window, an October agriculture/community follow-up, sampling geography context, and a public claim that household longitude/latitude were recorded using GPS devices. This audit does not promote ALB_2005 to climate-linked data because row-level household interview timing and raw coordinate values remain unverified in the extracted files.

## Summary

| Metric | Value | Interpretation |
|---|---:|---|
| alb2005_public_fieldwork_geo_metadata_evidence_rows | 10 | Public fieldwork/geography metadata evidence rows audited from saved DDI XML. |
| alb2005_public_fieldwork_geo_metadata_verified_source_rows | 10 | Rows where the expected public-source snippet was found. |
| alb2005_public_fieldwork_geo_metadata_source_missing_rows | 0 | Rows where the expected public-source snippet or source file was missing. |
| alb2005_public_fieldwork_geo_metadata_fieldwork_period_evidence_rows | 5 | Rows documenting the wave-level fieldwork window or module-specific timing. |
| alb2005_public_fieldwork_geo_metadata_gps_claim_rows | 3 | Rows documenting public metadata claims about GPS/georeferencing. |
| alb2005_public_fieldwork_geo_metadata_sampling_geo_rows | 2 | Rows documenting public sampling/admin geography context. |
| alb2005_public_fieldwork_geo_metadata_household_timing_verified_rows | 0 | Verified row-level household timing rows from the raw timing/geography audit; must remain zero until timing is actually verified. |
| alb2005_public_fieldwork_geo_metadata_raw_coordinate_value_rows | 0 | Verified raw coordinate candidate rows from the raw timing/geography audit; must remain zero until coordinate values are actually located. |
| alb2005_public_fieldwork_geo_metadata_full_geography_rows | 0 | Verified full-coverage row-level geography rows from the raw timing/geography audit. |
| alb2005_public_fieldwork_geo_metadata_source_search_household_timing_ready_rows | 0 | Timing-ready rows from the source-search audit. |
| alb2005_public_fieldwork_geo_metadata_source_search_coordinate_rows | 0 | Coordinate candidate rows from the source-search audit. |
| alb2005_public_fieldwork_geo_metadata_source_search_climate_linkage_ready_rows | 0 | Climate-linkage-ready rows from the source-search audit. |
| alb2005_public_fieldwork_geo_metadata_climate_linkage_ready_rows | 0 | Rows ready for climate linkage after this metadata audit; intentionally zero. |
| alb2005_public_fieldwork_geo_metadata_current_decision | blocked_public_metadata_not_household_climate_linkage_ready | Current fail-closed decision for public fieldwork/geography metadata. |

## Evidence Rows

| evidence_id | evidence_domain | source_line | source_status | promotion_status | analysis_interpretation |
|---|---|---|---|---|---|
| fieldwork_period_ddi | fieldwork_period | 57 | public_source_snippet_verified | context_only_not_household_timing_ready | Wave-level fieldwork window is source-verified, but this is not household-level interview date or month. |
| fieldwork_start_ddi | fieldwork_period | 251 | public_source_snippet_verified | context_only_not_household_timing_ready | Wave start date is source-verified, but not enough to time each household's exposure window. |
| enumeration_end_ddi | fieldwork_period | 255 | public_source_snippet_verified | context_only_not_household_timing_ready | Wave end timing is source-verified, but the household row still lacks verified interview timing. |
| price_questionnaire_parallel_ddi | fieldwork_period | 211 | public_source_snippet_verified | context_only_not_household_timing_ready | Price-module timing supports the core fieldwork window but is not an individual household interview date. |
| agriculture_october_followup_ddi | fieldwork_period | 203 | public_source_snippet_verified | context_only_module_specific_not_core_timing_ready | October is a module-specific follow-up for agricultural households, not the default core household interview month. |
| gps_recorded_ddi | gps_metadata | 184 | public_source_snippet_verified | public_metadata_claim_not_raw_coordinate_ready | The public metadata claims GPS collection, but the current extracted/raw-value audits have not verified coordinate variabl... |
| gps_linkage_purpose_ddi | gps_metadata | 184 | public_source_snippet_verified | public_metadata_claim_not_raw_coordinate_ready | The metadata supports climate-linkage relevance, but does not itself provide usable coordinates. |
| sampling_frame_hierarchy_ddi | sampling_geography | 141 | public_source_snippet_verified | context_only_not_joinable_admin_ready | Administrative hierarchy is source-verified, but a joinable household/admin boundary key is still not accepted. |
| ea_classification_ddi | sampling_geography | 145 | public_source_snippet_verified | context_only_not_joinable_admin_ready | Sampling-frame geography exists in documentation, but the current household extract still has only partial usable geography. |
| gps_training_ddi | gps_metadata | 223 | public_source_snippet_verified | public_metadata_claim_not_raw_coordinate_ready | Training evidence corroborates GPS collection procedures but does not verify coordinate availability in the local raw files. |

## Interpretation

- Public metadata improves the source context for ALB_2005 timing and geography.
- The May to early-July fieldwork window is wave-level evidence, not household-level timing.
- The GPS statement is a public metadata claim, not verified coordinate values in the local raw files.
- October belongs to agriculture/community follow-up and must not be treated as the default core household interview month.
- Climate exposure extraction remains blocked until timing and geography are accepted through raw-value evidence or a reviewed sensitivity design.

## Machine-Readable Outputs

- `temp/alb2005_public_fieldwork_geo_metadata_audit.csv`
- `result/alb2005_public_fieldwork_geo_metadata_summary.csv`
