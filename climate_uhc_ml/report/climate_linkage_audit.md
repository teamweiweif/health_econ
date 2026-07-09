# Climate Linkage Audit

Status: climate extraction scaffold is implemented. NASA POWER point fallback can run once harmonized coordinates and interview timing exist.

## Current Geography/Timing Evidence

Metadata schema inspection found geography, cluster, residence, or GPS label hits in the priority studies, but raw geolocation quality is not verified. GPS may be absent, displaced, restricted, or represented only through ancillary files depending on survey.

ALB_2002 raw household-core audit rows: 7. Households with observed survey month: 3599. Households with constructed interview date: 3599. Households with district code: 3599. District crosswalk template rows: 36; public boundary probe rows: 1; boundary-source reachable rows: 1; boundary ADM unit count: 37; public boundary name-match rows: 36; GeoJSON features: 37; exact name matches: 34; mojibake-repaired matches: 1; unmatched survey rows: 1; duplicate boundary-name keys: 2; parsed boundary-resource candidates: 3; complete-name-coverage resources: 1; exact-unit-count resources: 1; best resource lead: geoboundaries_2_0_1_adm2; geometry features parsed for that lead: 36; metadata boundary year: 2013; boundary-resource climate-linkage-ready rows: 0; geometry/provenance climate-linkage-ready rows: 0; boundary-name climate-linkage-ready rows: 0; ALB_2002 climate-linkage-ready rows: 0. Current decisions: household core temp_candidate_timing_geography_observed_outcome_semantics_pending; district crosswalk blocked_boundary_crosswalk_not_verified_no_gps; boundary name match blocked_current_boundary_name_match_incomplete_historical_crosswalk_no_gps; boundary resource search blocked_alb2002_boundary_resource_search_no_historical_climate_ready_source; boundary geometry/provenance blocked_geoboundaries_2_0_1_boundary_year_2013_not_verified_2002. These fields are candidate inputs only; no climate-linkage-ready rows are promoted until district polygons/crosswalk, fieldwork documentation, historical district definitions, no-GPS measurement error, and OOP/access semantics pass.

ALB_2002 boundary name-match status:

| ALB_2002 boundary name match method | Count |
|---|---:|
| exact_normalized_name_match | 34 |
| no_name_match | 1 |
| mojibake_euro_as_c_name_match | 1 |

| ALB_2002 boundary name match status | Count |
|---|---:|
| candidate_current_boundary_name_match_not_historical_or_geometric_verified | 35 |
| blocked_no_current_boundary_name_match | 1 |

ALB_2002 boundary source alternatives:

| ALB_2002 boundary source probe status | Count |
|---|---:|
| reachable_page_sampled | 3 |
| blocked_http_error | 2 |
| local_artifact_review | 1 |

| ALB_2002 boundary source suitability | Count |
|---|---:|
| blocked_complete_geometry_boundary_year_2013_not_verified_2002 | 1 |
| blocked_current_or_post2015_boundary_not_historical_2002_lsms | 1 |
| blocked_current_or_post2019_boundary_not_historical_2002_lsms | 1 |
| blocked_lsms_sampling_geography_documented_no_direct_gis_artifact_verified | 1 |
| blocked_official_census_context_no_public_district_gis_verified | 1 |
| blocked_historical_census_candidate_not_lsms_district_crosswalk_verified | 1 |

The boundary source-alternatives audit is `report/alb2002_boundary_source_alternative_audit.md`; machine-readable outputs are `temp/alb2002_boundary_source_alternative_audit.csv` and `result/alb2002_boundary_source_alternative_summary.csv`. It reviews 6 source leads, including current/post-2015 sources, the official ALB_2002 study page, INSTAT census context, and IHGIS historical census leads. LSMS map and GPS documentation flags are 1 and 1, but verified historical-boundary-ready and climate-linkage-ready rows remain 0 and 0; current decision is `blocked_no_public_2002_district_boundary_source_verified`.

ALB_2002 boundary resource search:

| ALB_2002 boundary resource status | Count |
|---|---:|
| local_geojson_snapshot_parsed | 1 |
| downloaded_geojson | 1 |
| downloaded_hdx_2019_gazetteer_adm2_sheet | 1 |

| ALB_2002 boundary resource suitability | Count |
|---|---:|
| blocked_current_boundary_name_or_unit_mismatch_not_historical | 1 |
| candidate_complete_name_coverage_but_boundary_vintage_not_verified | 1 |
| blocked_2019_municipality_units_not_2002_lsms_districts | 1 |

The boundary resource-search audit is `report/alb2002_boundary_source_resource_search_audit.md`; machine-readable outputs are `temp/alb2002_boundary_source_resource_search_audit.csv` and `result/alb2002_boundary_source_resource_search_summary.csv`. It directly parses 3 public boundary/gazetteer resources. The best name-coverage lead is `geoboundaries_2_0_1_adm2`, with 33 exact matches, 2 encoding-repaired matches, and 1 documented alias matches. Complete-name-coverage and exact-unit-count resources are 1 and 1, but verified 2002 historical-boundary-ready and climate-linkage-ready rows remain 0 and 0; current decision is `blocked_alb2002_boundary_resource_search_no_historical_climate_ready_source`.

ALB_2002 boundary geometry and provenance:

| ALB_2002 boundary geometry structure status | Count |
|---|---:|
| coordinate_structure_parse_ok_topology_not_validated | 36 |

| ALB_2002 boundary geometry survey match method | Count |
|---|---:|
| exact_normalized_survey_name | 33 |
| encoding_repaired_survey_name | 2 |
| documented_alias_survey_name | 1 |

| ALB_2002 boundary metadata evidence status | Count |
|---|---:|
| metadata_present | 8 |
| source_metadata_present | 3 |
| blocked_boundary_year_2013_not_2002 | 1 |

The boundary geometry/provenance audit is `report/alb2002_boundary_geometry_provenance_audit.md`; machine-readable outputs are `temp/alb2002_boundary_geometry_provenance_audit.csv`, `temp/alb2002_boundary_metadata_provenance_probe.csv`, and `result/alb2002_boundary_geometry_provenance_summary.csv`. It finds 36 parsed ADM2 features, 36 coordinate-structure-ok features, and 36 survey-key matches. The companion metadata reports boundary year 2013, update 2020-01-16, and source OpenStreetMap; Wambacher. Boundary-year-matches-2002, topology-validated, historical-boundary-ready, and climate-linkage-ready rows are 0, 0, 0, and 0; current decision is `blocked_geoboundaries_2_0_1_boundary_year_2013_not_verified_2002`.

ALB_2002 boundary manual verification packet:

| ALB_2002 boundary manual action status | Count |
|---|---:|
| blocked_official_geography_artifact_not_obtained | 1 |
| blocked_official_2001_boundary_file_not_verified | 1 |
| blocked_prefecture_g1_not_36_lsms_districts | 1 |
| blocked_boundary_year_2013_not_verified_2002 | 1 |
| blocked_geoportal_historical_2002_layer_not_verified | 1 |
| blocked_2019_municipality_units_not_2002_lsms_districts | 1 |
| blocked_pre2011_digital_boundary_source_absence_documented | 1 |

| ALB_2002 boundary manual gate status | Count |
|---|---:|
| candidate_evidence_present_not_sufficient_for_climate_linkage | 1 |
| candidate_evidence_present_not_sufficient_for_promotion | 1 |
| candidate_evidence_present_topology_not_validated | 1 |
| blocked_boundary_year_not_2002 | 1 |
| blocked_osm_wambacher_not_official_2002_source | 1 |
| blocked_no_official_code_crosswalk | 1 |
| blocked_raw_coordinate_or_ea_artifact_absent | 1 |
| blocked_until_boundary_and_crosswalk_pass | 1 |
| blocked_not_ready_for_climate_linkage | 1 |

The boundary manual verification packet is `report/alb2002_boundary_manual_verification_packet.md`; machine-readable outputs are `temp/alb2002_boundary_manual_verification_action_queue.csv`, `temp/alb2002_boundary_promotion_gate_checklist.csv`, and `result/alb2002_boundary_manual_verification_packet_summary.csv`. It turns the ALB_2002 boundary blocker into 7 source-specific actions and 9 promotion gates. Candidate-evidence gates are 3, blocked gates are 6, high-priority actions are 3, pre-2011 digital-map absence evidence rows are 1, and climate-linkage-ready rows remain 0; current decision is `blocked_manual_boundary_verification_required_before_alb2002_climate_linkage`.

ALB_2002 boundary manual source follow-up:

| ALB_2002 boundary follow-up blocker | Count |
|---|---:|
| blocked_artifact_access_not_level_proven | 1 |
| blocked_context_without_boundary_file | 1 |
| blocked_prefecture_g1_not_36_lsms_districts | 1 |
| blocked_boundary_year_2013_not_verified_2002 | 1 |
| blocked_historical_layer_not_verified | 1 |
| blocked_2019_units_not_2002_lsms_districts | 1 |
| blocked_pre2011_digital_boundary_source_absence_documented | 1 |

| ALB_2002 boundary follow-up level compatibility | Count |
|---|---:|
| not_compatible_with_alb2002_district_climate_linkage | 4 |
| potentially_compatible_if_restricted_ancillary_artifacts_obtained | 1 |
| potentially_compatible_if_boundary_file_obtained | 1 |
| name_coverage_candidate_but_historical_vintage_blocked | 1 |

The boundary manual source follow-up is `report/alb2002_boundary_manual_source_followup.md`; machine-readable outputs are `temp/alb2002_boundary_manual_source_followup_audit.csv` and `result/alb2002_boundary_manual_source_followup_summary.csv`. It records 7 source follow-up rows and 7 source-specific blockers. The IHGIS lead is now `blocked_prefecture_g1_not_36_lsms_districts` in the reviewed catalog evidence, so it is not a 36-district ALB_2002 boundary solution unless a separate district/g2 file is found. The UNECE/INSTAT pre-2011 map status is `blocked_pre2011_digital_boundary_source_absence_documented`, which blocks treating current or post-2011 public GIS layers as historical 2002 boundaries without separate crosswalk proof. District-level-ready and climate-linkage-ready rows remain 0 and 0; current decision is `blocked_followup_confirms_no_public_2002_district_boundary_source`.

ALB_2002 GADM boundary lead audit:

| ALB_2002 GADM suitability status | Count |
|---|---:|
| candidate_name_coverage_but_duplicate_key_and_provenance_blocked | 1 |
| candidate_name_coverage_but_not_historical_or_typed_district_ready | 1 |

| ALB_2002 GADM name-match status | Count |
|---|---:|
| matched_normalized_key | 74 |
| duplicate_boundary_key | 4 |

The GADM boundary lead audit is `report/alb2002_gadm_boundary_lead_audit.md`; machine-readable outputs are `temp/alb2002_gadm_boundary_lead_audit.csv`, `temp/alb2002_gadm_boundary_name_match_audit.csv`, and `result/alb2002_gadm_boundary_lead_summary.csv`. It audits 2 public GADM Albania ADM2 snapshots. GADM 3.6 has 37 ADM2 rows, 36 normalized keys, and 37 rows labeled District/Rreth-compatible, but it has 1 duplicate normalized key and no verified official 2001/2002 historical provenance. Historical-ready and climate-linkage-ready rows remain 0 and 0; current decision is `blocked_gadm_boundary_lead_no_verified_2002_historical_provenance`.

ALB_2002 local geography artifacts:

| ALB_2002 local geography evidence role | Count |
|---|---:|
| raw_or_documentation_file | 44 |
| raw_psu_or_ea_variable | 43 |
| questionnaire_admin_geography_text | 13 |
| raw_district_or_commune_variable | 9 |
| raw_admin_geography_variable | 3 |
| questionnaire_coordinate_field | 2 |

| ALB_2002 local geography value status | Count |
|---|---:|
| file_exists | 44 |
| admin_sampling_identifier_observed | 43 |
| questionnaire_design_field_observed | 15 |
| admin_label_or_code_observed | 12 |

The local geography artifact audit is `report/alb2002_local_geography_artifact_audit.md`; machine-readable outputs are `temp/alb2002_local_geography_artifact_audit.csv` and `result/alb2002_local_geography_artifact_summary.csv`. It scans 44 local extracted files plus the raw schema/questionnaire evidence. Questionnaire coordinate fields are 2 and official GPS/EA-map documentation flags are 1 and 1, but raw coordinate-variable rows, recognized local GIS/boundary file candidates, local-coordinate-ready rows, local-boundary-ready rows, and climate-linkage-ready rows are 0, 0, 0, 0, and 0; current decision is `blocked_questionnaire_gps_fields_not_present_as_raw_coordinate_artifacts`.

ALB_2012 raw core feasibility rows: 6671. Provisional outcome diagnostic rows: 33. Raw outcome-semantics rows: 61. Timing/geography audit rows: 212. Questionnaire timing/control field rows: 29; questionnaire raw-gap rows: 12; raw verified questionnaire-derived interview timing rows: 0. Fallback blocker rows: 10; fallback hard-blocked rows: 10. Households with survey month: 0; interview date: 0; prefecture: 6671; region: 6671; raw-core climate-linkage-ready rows: 0; semantics climate-linkage-ready rows: 0; timing/geography climate-linkage-ready rows: 0; questionnaire timing climate-linkage-ready rows: 0; fallback climate-linkage-ready rows: 0. Current decisions: raw core temp_candidate_no_interview_timing_coarse_geography_outcome_semantics_pending; provisional outcomes not_final_outcomes_timing_geography_recall_semantics_blocked; raw semantics blocked_timing_geography_outcome_semantics_units_recall_skip_patterns; timing/geography blocked_missing_interview_timing_coarse_prefecture_region_no_gps; questionnaire timing blocked_questionnaire_timing_fields_not_in_raw_household_values; fallback blocker blocked_alb2012_no_timing_geography_fallback_ready. This wave has questionnaire form-design evidence for date/begin/end/status/visit fields, but no verified raw household interview timing or GPS, so it cannot yet support climate exposure windows.

ALB_2005 raw timing/geography audit rows: 234. Source files scanned: 44. Verified interview timing rows: 0. Coordinate candidate rows: 0. Partial district name rows: 1899; partial district code rows: 329. Climate-linkage-ready rows: 0. Current decision: blocked_missing_interview_timing_partial_geography_no_gps.

ALB_2005 timing/geography source-search rows: 11. Local file rows scanned: 46; raw-variable rows scanned: 1187; raw targets with hits: 4; questionnaire targets with hits: 5. Verified household timing rows: 0; coordinate candidate rows: 0; geography-crosswalk-ready rows: 0; climate-linkage-ready rows: 0. Current decision: blocked_alb2005_timing_geography_source_search_not_ready.

Legacy Albania questionnaire readability: 5 ALB_2002/2005/2008 `.xls` questionnaire files are present and 5 have legacy OLE signatures; readable files are 5 because `xlrd` installed=1 and `soffice` available=0. Timing-content-ready files and climate-linkage-ready rows are 5 and 0. Current decision: legacy_questionnaires_readable_content_audit_required. The report is `report/albania_legacy_questionnaire_readability_audit.md`.

Legacy Albania questionnaire timing/control audit: questionnaire timing/control field rows=83; visit rows=18; date/begin/end/status rows=41; raw timing-gap rows=58; verified raw household interview timing rows across ALB_2002/2005/2008=3599 (ALB_2002=3599, ALB_2005=0, ALB_2008=0). Climate-linkage-ready rows remain 0. Current decision: blocked_legacy_questionnaire_form_design_not_sufficient_for_climate_linkage. The report is `report/albania_legacy_questionnaire_timing_field_audit.md`.

## Current Extraction Audit

| Climate extraction status | Count |
|---|---:|
| complete_limited_admin2_centroid_input | 1 |
| complete_limited_nasa_power_fallback | 1 |
| blocked_final_linkage | 1 |

## Climate Source Probe

| Climate source probe status | Count |
|---|---:|
| reachable_snapshot_saved | 8 |
| pass_api_parameters_present | 1 |

| Climate source role | Count |
|---|---:|
| primary_rainfall_documentation | 1 |
| primary_rainfall_data_directory | 1 |
| primary_temperature_documentation | 1 |
| primary_daily_temperature_documentation | 1 |
| rapid_point_fallback_documentation | 1 |
| rapid_point_fallback_api | 1 |
| water_balance_robustness_documentation | 1 |
| water_balance_robustness_catalog | 1 |
| drought_robustness_documentation | 1 |

The endpoint-level source probe is `temp/climate_source_probe.csv`; the human-readable report is `report/climate_source_probe.md`. These are source-readiness checks only, not exposure construction.

Climate exposure rows currently present: 384

Climate-linked household rows currently present: 14396

## Planned Source Hierarchy

| Domain | Primary source | Fallback/robustness |
|---|---|---|
| Rainfall | CHIRPS daily/monthly precipitation | ERA5-Land or NASA POWER subset checks |
| Temperature | ERA5-Land daily statistics | NASA POWER daily API |
| Drought/water balance | SPEI and TerraClimate | CHIRPS rainfall anomaly/deficit proxies |

## No-Go Until

- raw data or official ancillary geography files are available;
- interview month/date is verified;
- geolocation quality and displacement/restriction are documented;
- auditable point/admin exposure files are produced from verified inputs.

## Implemented Fallback

`script/06_extract_climate.py` validates `data/climate_linkage_input.*`, `data/harmonized_household.*`, or `data/household_panel.*`, then extracts 1, 3, 6, and 12 month pre-interview NASA POWER daily point summaries. It does not claim CHIRPS/ERA5 primary exposure construction, z-scores, percentiles, or heatwave metrics until historical baselines and geospatial extraction are implemented.
