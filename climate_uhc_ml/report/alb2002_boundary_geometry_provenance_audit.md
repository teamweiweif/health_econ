# ALB_2002 Boundary Geometry and Provenance Audit

Status: temp-only geometry/provenance audit for the geoBoundaries 2.0.1 ADM2 lead. This audit parses the candidate GeoJSON and companion metadata but does not validate topology with GIS libraries, does not create centroids for analysis, does not write `data/`, and does not construct climate exposures.

## Summary

| Metric | Value | Interpretation |
|---|---:|---|
| alb2002_boundary_geometry_candidate_resource_id | geoboundaries_2_0_1_adm2 | Resource selected from the prior public resource-search audit for geometry/provenance review. |
| alb2002_boundary_geometry_geojson_status | local_geojson_snapshot_parsed | GeoJSON snapshot parse/download status. |
| alb2002_boundary_geometry_metadata_status | downloaded_json | Companion metadata download/parse status. |
| alb2002_boundary_geometry_feature_rows | 36 | Boundary features in the candidate GeoJSON. |
| alb2002_boundary_geometry_adm2_feature_rows | 36 | Features whose shapeType property is ADM2. |
| alb2002_boundary_geometry_multipolygon_rows | 36 | Features represented as MultiPolygon geometry. |
| alb2002_boundary_geometry_coordinate_structure_ok_rows | 36 | Features with parseable polygon coordinate structure, closed rings, coordinate ranges, and a broad Albania bounding box; this is not topology validation. |
| alb2002_boundary_geometry_survey_key_matched_rows | 36 | Features matched back to ALB_2002 survey district keys after documented name repairs/aliases. |
| alb2002_boundary_geometry_closed_ring_failure_rows | 0 | Features with at least one unclosed ring. |
| alb2002_boundary_geometry_out_of_range_coordinate_rows | 0 | Features with any longitude/latitude outside global valid ranges. |
| alb2002_boundary_geometry_within_broad_albania_bbox_rows | 36 | Features whose coordinates fall inside a broad Albania bounding box. |
| alb2002_boundary_geometry_metadata_boundary_year | 2013 | Boundary year reported by the geoBoundaries 2.0.1 companion metadata. |
| alb2002_boundary_geometry_metadata_boundary_update | 2020-01-16 | Boundary update date reported by companion metadata. |
| alb2002_boundary_geometry_metadata_boundary_source | OpenStreetMap; Wambacher | Boundary source fields reported by companion metadata. |
| alb2002_boundary_geometry_metadata_source_url | https://wambachers-osm.website/boundaries/ | Boundary source URL reported by companion metadata. |
| alb2002_boundary_geometry_boundary_year_matches_2002_rows | 0 | Whether the candidate metadata directly supports a 2002 boundary vintage. |
| alb2002_boundary_geometry_topology_validated_rows | 0 | Rows with real topology validation; zero because shapely/geopandas is not required or available in this pipeline step. |
| alb2002_boundary_geometry_historical_2002_boundary_ready_rows | 0 | Rows ready as verified 2002 historical district boundaries after this audit; intentionally zero. |
| alb2002_boundary_geometry_climate_linkage_ready_rows | 0 | Rows ready for climate-linkage promotion after this audit; intentionally zero. |
| alb2002_boundary_geometry_current_decision | blocked_geoboundaries_2_0_1_boundary_year_2013_not_verified_2002 | Current fail-closed decision for ALB_2002 boundary geometry/provenance. |

## Metadata Provenance Fields

| field | value | evidence_status | interpretation |
|---|---|---|---|
| boundaryYear | 2013 | blocked_boundary_year_2013_not_2002 | Companion metadata boundaryYear; this is the main vintage gate for ALB_2002. |
| boundaryUpdate | 2020-01-16 | metadata_present | Companion metadata field captured for provenance review. |
| boundarySource-1 | OpenStreetMap | source_metadata_present | Companion metadata source field; provenance still requires source-history review against 2002 LSMS geography. |
| boundarySource-2 | Wambacher | source_metadata_present | Companion metadata source field; provenance still requires source-history review against 2002 LSMS geography. |
| boundarySourceURL | https://wambachers-osm.website/boundaries/ | source_metadata_present | Companion metadata source field; provenance still requires source-history review against 2002 LSMS geography. |
| boundaryLicense | Open Data Commons Open Database License 1.0 | metadata_present | Companion metadata field captured for provenance review. |
| licenseSource | https://www.openstreetmap.org/copyright | metadata_present | Companion metadata field captured for provenance review. |

## Geometry Structure Preview

| shape_name | survey_district_code | survey_match_method | geometry_type | polygon_parts | ring_count | coordinate_pair_count | within_broad_albania_bbox | geometry_structure_status |
|---|---|---|---|---|---|---|---|---|
| Durrës | 6 | exact_normalized_survey_name | MultiPolygon | 1 | 1 | 2708 | 1 | coordinate_structure_parse_ok_topology_not_validated |
| Bulqizë | 2 | exact_normalized_survey_name | MultiPolygon | 1 | 1 | 1455 | 1 | coordinate_structure_parse_ok_topology_not_validated |
| Gramsh | 9 | exact_normalized_survey_name | MultiPolygon | 1 | 1 | 1806 | 1 | coordinate_structure_parse_ok_topology_not_validated |
| Kurbin | 18 | exact_normalized_survey_name | MultiPolygon | 1 | 1 | 1772 | 1 | coordinate_structure_parse_ok_topology_not_validated |
| Shkodër | 32 | exact_normalized_survey_name | MultiPolygon | 1 | 1 | 2753 | 1 | coordinate_structure_parse_ok_topology_not_validated |
| Lezhë | 19 | exact_normalized_survey_name | MultiPolygon | 2 | 2 | 2865 | 1 | coordinate_structure_parse_ok_topology_not_validated |
| Peqin | 26 | exact_normalized_survey_name | MultiPolygon | 1 | 1 | 506 | 1 | coordinate_structure_parse_ok_topology_not_validated |
| Librazhd | 20 | exact_normalized_survey_name | MultiPolygon | 1 | 1 | 1692 | 1 | coordinate_structure_parse_ok_topology_not_validated |
| Mat | 24 | exact_normalized_survey_name | MultiPolygon | 1 | 1 | 744 | 1 | coordinate_structure_parse_ok_topology_not_validated |
| Berat District | 1 | exact_normalized_survey_name | MultiPolygon | 1 | 1 | 1838 | 1 | coordinate_structure_parse_ok_topology_not_validated |
| Skrapar | 31 | exact_normalized_survey_name | MultiPolygon | 1 | 1 | 1307 | 1 | coordinate_structure_parse_ok_topology_not_validated |
| Përmet | 27 | exact_normalized_survey_name | MultiPolygon | 1 | 1 | 519 | 1 | coordinate_structure_parse_ok_topology_not_validated |
| Pukë | 29 | exact_normalized_survey_name | MultiPolygon | 1 | 1 | 838 | 1 | coordinate_structure_parse_ok_topology_not_validated |
| Kolonjë | 13 | exact_normalized_survey_name | MultiPolygon | 1 | 1 | 683 | 1 | coordinate_structure_parse_ok_topology_not_validated |
| Tepelenë | 33 | exact_normalized_survey_name | MultiPolygon | 1 | 1 | 511 | 1 | coordinate_structure_parse_ok_topology_not_validated |
| Fier District | 8 | exact_normalized_survey_name | MultiPolygon | 1 | 1 | 1327 | 1 | coordinate_structure_parse_ok_topology_not_validated |
| Korçë | 14 | encoding_repaired_survey_name | MultiPolygon | 2 | 2 | 2358 | 1 | coordinate_structure_parse_ok_topology_not_validated |
| Kavajë | 12 | exact_normalized_survey_name | MultiPolygon | 1 | 1 | 1382 | 1 | coordinate_structure_parse_ok_topology_not_validated |
| Sarandë | 30 | exact_normalized_survey_name | MultiPolygon | 1 | 1 | 3942 | 1 | coordinate_structure_parse_ok_topology_not_validated |
| Mirditë | 25 | exact_normalized_survey_name | MultiPolygon | 1 | 1 | 378 | 1 | coordinate_structure_parse_ok_topology_not_validated |
| Mallakastër | 23 | exact_normalized_survey_name | MultiPolygon | 1 | 1 | 321 | 1 | coordinate_structure_parse_ok_topology_not_validated |
| Kuçovë | 16 | encoding_repaired_survey_name | MultiPolygon | 1 | 1 | 268 | 1 | coordinate_structure_parse_ok_topology_not_validated |
| Has | 11 | exact_normalized_survey_name | MultiPolygon | 1 | 1 | 369 | 1 | coordinate_structure_parse_ok_topology_not_validated |
| Devoll | 4 | exact_normalized_survey_name | MultiPolygon | 1 | 1 | 441 | 1 | coordinate_structure_parse_ok_topology_not_validated |
| Delvinë | 3 | exact_normalized_survey_name | MultiPolygon | 1 | 1 | 319 | 1 | coordinate_structure_parse_ok_topology_not_validated |
| Dibër | 5 | exact_normalized_survey_name | MultiPolygon | 1 | 1 | 1164 | 1 | coordinate_structure_parse_ok_topology_not_validated |
| Kukës | 17 | exact_normalized_survey_name | MultiPolygon | 1 | 1 | 1046 | 1 | coordinate_structure_parse_ok_topology_not_validated |
| Malësi e Madhe | 22 | exact_normalized_survey_name | MultiPolygon | 1 | 1 | 2462 | 1 | coordinate_structure_parse_ok_topology_not_validated |
| Vlorë | 36 | exact_normalized_survey_name | MultiPolygon | 2 | 2 | 5336 | 1 | coordinate_structure_parse_ok_topology_not_validated |
| Gjirokastër | 10 | exact_normalized_survey_name | MultiPolygon | 1 | 1 | 837 | 1 | coordinate_structure_parse_ok_topology_not_validated |
| Krujë | 15 | exact_normalized_survey_name | MultiPolygon | 1 | 1 | 841 | 1 | coordinate_structure_parse_ok_topology_not_validated |
| Lushnjë | 21 | exact_normalized_survey_name | MultiPolygon | 1 | 2 | 2388 | 1 | coordinate_structure_parse_ok_topology_not_validated |
| Elbasan | 7 | exact_normalized_survey_name | MultiPolygon | 1 | 1 | 1001 | 1 | coordinate_structure_parse_ok_topology_not_validated |
| Tirana | 34 | documented_alias_survey_name | MultiPolygon | 1 | 1 | 1781 | 1 | coordinate_structure_parse_ok_topology_not_validated |
| Tropojë | 35 | exact_normalized_survey_name | MultiPolygon | 1 | 1 | 1811 | 1 | coordinate_structure_parse_ok_topology_not_validated |
| Pogradec | 28 | exact_normalized_survey_name | MultiPolygon | 1 | 1 | 1444 | 1 | coordinate_structure_parse_ok_topology_not_validated |

## Interpretation

- The candidate geoBoundaries 2.0.1 ADM2 file has complete ALB_2002 district-name coverage and parseable coordinate structure.
- The companion metadata reports `boundaryYear` as 2013, with OpenStreetMap/Wambacher provenance, not a 2001/2002 LSMS or census boundary source.
- The audit therefore tightens the blocker: this source is a useful lead for manual review, but it is not verified as the ALB_2002 historical district boundary layer.
- No topology validation, official 2002 district-definition validation, raw district-code crosswalk validation, or climate-linkage promotion is performed here.
- Historical-boundary-ready and climate-linkage-ready rows remain zero.

## Machine-Readable Outputs

- `temp/alb2002_boundary_geometry_provenance_audit.csv`
- `temp/alb2002_boundary_metadata_provenance_probe.csv`
- `result/alb2002_boundary_geometry_provenance_summary.csv`
- `temp/source_snapshots/alb2002_geoboundaries_2_0_1_alb_adm2_metadata.json`
