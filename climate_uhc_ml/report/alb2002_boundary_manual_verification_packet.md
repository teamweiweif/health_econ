# ALB_2002 Boundary Manual Verification Packet

Status: manual verification packet only. This packet turns the ALB_2002 geography blocker into source-specific actions and pass/fail promotion gates. It does not download new restricted files, does not write `data/`, does not construct centroids or climate exposures, and does not promote any ALB_2002 boundary to analysis-ready status.

## Summary

| Metric | Value | Interpretation |
|---|---:|---|
| alb2002_boundary_manual_verification_action_rows | 7 | Manual source/action rows for resolving the ALB_2002 geography blocker. |
| alb2002_boundary_manual_verification_gate_rows | 9 | Promotion-gate checklist rows for ALB_2002 boundary verification. |
| alb2002_boundary_manual_verification_candidate_evidence_gates | 3 | Gates with candidate evidence that is useful but insufficient for promotion. |
| alb2002_boundary_manual_verification_blocked_gates | 6 | Gates still blocked before any ALB_2002 climate linkage. |
| alb2002_boundary_manual_verification_high_priority_actions | 3 | Top-priority manual actions: World Bank geography artifacts, INSTAT 2001 boundary files, and IHGIS historical GIS. |
| alb2002_boundary_manual_verification_pre2011_digital_map_absence_rows | 1 | Negative-evidence source rows documenting that pre-2011 national digital maps were absent. |
| alb2002_boundary_manual_verification_climate_linkage_ready_rows | 0 | Rows ready for climate-linkage promotion after this packet; intentionally zero. |
| alb2002_boundary_manual_verification_current_decision | blocked_manual_boundary_verification_required_before_alb2002_climate_linkage | Current fail-closed decision for ALB_2002 manual boundary verification. |

## Manual Action Queue

| action_rank | candidate_id | source_role | blocking_status | manual_verification_action |
|---|---|---|---|---|
| 1 | worldbank_alb2002_lsms_study | official_survey_geography_and_raw_ancillary_artifacts | blocked_official_geography_artifact_not_obtained | Use the Microdata Library terms/account workflow or study contact route to request/download all ALB_2002 geography an... |
| 2 | instat_census_2001 | official_2001_census_boundary_or_cartography_source | blocked_official_2001_boundary_file_not_verified | Search/request 2001 census district, commune, EA, or cartography boundary files from INSTAT, including documentation ... |
| 3 | ipums_ihgis_alb2001 | historical_census_gis_candidate | blocked_prefecture_g1_not_36_lsms_districts | Treat the visible IHGIS catalog evidence as non-sufficient for ALB_2002 district climate linkage; revisit only if a s... |
| 4 | geoboundaries_2_0_1_adm2 | best_public_name_coverage_lead_not_historical_verified | blocked_boundary_year_2013_not_verified_2002 | Investigate source history and external official documentation to determine whether the 2013 OSM/Wambacher ADM2 geome... |
| 5 | asig_geoportal_current | official_current_geoportal_possible_historical_catalog | blocked_geoportal_historical_2002_layer_not_verified | Manually search ASIG/official geoportal for historical administrative or census cartography layers around 2001/2002, ... |
| 6 | hdx_cod_ab_alb_2019_gazetteer_adm2 | current_2019_administrative_reference_only | blocked_2019_municipality_units_not_2002_lsms_districts | Use only as a current reference unless a documented historical crosswalk maps 2002 districts to 2019 municipality uni... |
| 7 | unece_instat_2011_gis_paper | official_statistical_system_evidence_on_pre2011_digital_map_absence | blocked_pre2011_digital_boundary_source_absence_documented | Use this source as negative evidence when evaluating whether current or post-2011 public GIS layers can be treated as... |

## Promotion Gate Checklist

| gate_id | current_status | current_evidence | required_evidence_to_pass |
|---|---|---|---|
| survey_timing_and_admin_keys | candidate_evidence_present_not_sufficient_for_climate_linkage | district_groups=36; survey_month_rows=3599; interview_date_rows=3599 | Raw household IDs, district codes/names, survey month/date, weights, and codebook meanings are verified and preserved... |
| boundary_name_coverage | candidate_evidence_present_not_sufficient_for_promotion | candidate_features=36; survey_key_matched_rows=36 | All observed district names/codes match boundary features with documented encoding and alias decisions. |
| boundary_geometry_structure | candidate_evidence_present_topology_not_validated | coordinate_structure_ok_rows=36; topology_validated_rows=0 | A GIS/topology validator confirms valid polygons, no overlaps/gaps relevant to aggregation, correct CRS, and reproduc... |
| boundary_vintage | blocked_boundary_year_not_2002 | candidate metadata boundaryYear=2013 | Metadata or official documentation proves 2001/2002 boundary vintage, or proves the 2013 geometry exactly reproduces ... |
| official_provenance | blocked_osm_wambacher_not_official_2002_source | candidate source=OpenStreetMap; Wambacher | Source provenance is official census/LSMS/government geography or a defensible historical GIS source with compatible ... |
| raw_code_crosswalk | blocked_no_official_code_crosswalk | name matches exist=36; official code crosswalk rows=0 | A district-code/name crosswalk joins every raw ALB_2002 district code to one boundary feature, with encoding decision... |
| coordinate_or_ea_artifact | blocked_raw_coordinate_or_ea_artifact_absent | raw coordinate variable rows=0; local boundary-ready rows=0 | Raw coordinate file, EA map, or EA-to-boundary/centroid crosswalk is obtained, checksummed, and joined to raw IDs. |
| admin_measurement_error | blocked_until_boundary_and_crosswalk_pass | Only district-level candidate geography is available; no GPS displacement/buffer evidence exists. | If district aggregation is used, the report specifies exposure misclassification, area aggregation method, sensitivit... |
| climate_linkage_promotion | blocked_not_ready_for_climate_linkage | At least one upstream gate remains blocked: boundary vintage, official provenance, topology validation, raw code cros... | All required gates above pass with machine-readable evidence and reviewer-readable documentation. |

## Interpretation

- ALB_2002 remains the strongest local geography lead because survey timing and district keys exist and the geoBoundaries 2.0.1 lead has complete name coverage.
- The current blocker is narrower and harder: boundary vintage/provenance, official 2001/2002 source status, topology validation, raw district-code crosswalk, and missing GPS/EA artifacts.
- The packet prioritizes World Bank ALB_2002 geography/GPS/EA-map artifacts, official INSTAT 2001 census boundary/cartography sources, and IHGIS Albania 2001 historical GIS verification.
- The UNECE/INSTAT GIS implementation paper is negative evidence: it documents the absence of national digital maps/spatial database before the 2011 census GIS build, so current or post-2011 layers need separate historical crosswalk proof before any ALB_2002 use.
- Climate-linkage-ready rows remain zero.

## Machine-Readable Outputs

- `temp/alb2002_boundary_manual_verification_action_queue.csv`
- `temp/alb2002_boundary_promotion_gate_checklist.csv`
- `result/alb2002_boundary_manual_verification_packet_summary.csv`
