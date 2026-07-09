# ALB_2002 Boundary Blocker Resolution Matrix

Status: fail-closed boundary-source resolution matrix. This consolidates ALB_2002 raw geography, official source leads, public boundary leads, current-boundary references, and negative evidence into one climate-linkage decision. It does not write `data/`, does not promote any boundary source, and does not relax the ALB_2002 climate-geography gate.

## Summary

| Metric | Value | Interpretation |
|---|---:|---|
| alb2002_boundary_blocker_resolution_rows | 11 | Boundary-source resolution rows consolidated. |
| alb2002_boundary_blocker_official_or_primary_lead_rows | 4 | Official or primary institutional leads represented in the matrix. |
| alb2002_boundary_blocker_candidate_name_coverage_rows | 3 | Public boundary leads with complete candidate name coverage but no promotion. |
| alb2002_boundary_blocker_incompatible_or_negative_rows | 4 | Rows that are current-unit, wrong-level, or negative-evidence sources. |
| alb2002_boundary_blocker_historical_2002_ready_rows | 0 | Rows verified as 2001/2002 historical boundary-ready. |
| alb2002_boundary_blocker_climate_linkage_ready_rows | 0 | Rows ready for promoted ALB_2002 climate linkage. |
| alb2002_boundary_blocker_data_write_ready_rows | 0 | Rows allowed for data/ writes by this boundary matrix; intentionally zero. |
| alb2002_boundary_blocker_hard_blocked_rows | 11 | Rows still blocked from promoted climate linkage. |
| alb2002_boundary_blocker_required_source_action_rows | 7 | Rows with an explicit source-search, request, or verification action. |
| alb2002_boundary_blocker_current_decision | blocked_no_alb2002_boundary_source_ready_for_climate_linkage | Current consolidated ALB_2002 boundary-source decision. |

## Boundary Source Matrix

| source_id | source_family | name_coverage_status | historical_vintage_status | blocker_class | climate_linkage_ready_rows | data_write_ready_rows |
|---|---|---|---|---|---|---|
| alb2002_raw_survey_geography | raw_microdata | observed_raw_district_keys_not_boundary_coverage | survey_year_2002_observed_but_no_boundary_artifact | raw_artifact_absence | 0 | 0 |
| worldbank_alb2002_lsms_study | official_survey_lead | potentially_compatible_if_artifacts_obtained | survey_context_2002_but_artifact_not_obtained | artifact_access_blocker | 0 | 0 |
| instat_census_2001 | official_census_lead | not_boundary_name_coverage | official_2001_context_without_boundary_file | official_context_without_file | 0 | 0 |
| geoboundaries_2_0_1_adm2 | public_boundary_lead | complete_name_coverage_candidate | blocked_boundary_year_2013_not_verified_2002 | historical_vintage_blocker | 0 | 0 |
| gadm36_alb_adm2 | public_boundary_lead | complete_name_coverage_candidate | blocked_no_verified_official_2001_2002_boundary_provenance | duplicate_key_and_provenance_blocker | 0 | 0 |
| gadm41_alb_adm2 | public_boundary_lead | complete_name_coverage_candidate | blocked_no_verified_official_2001_2002_boundary_provenance | provenance_and_type_blocker | 0 | 0 |
| geoboundaries_current_pinned_adm2 | current_boundary_reference | incomplete_or_duplicate_name_coverage_current_boundary | current_2021_not_historical_2002 | current_boundary_not_historical | 0 | 0 |
| ipums_ihgis_alb2001 | historical_census_gis_lead | not_36_district_name_coverage | historical_2001_context_but_wrong_visible_level | level_mismatch | 0 | 0 |
| asig_geoportal_current | official_geoportal_lead | not_verified | historical_2001_2002_layer_not_verified | historical_layer_not_verified | 0 | 0 |
| hdx_cod_ab_alb_2019_gazetteer_adm2 | current_boundary_reference | not_36_district_name_coverage | post_2015_or_2019_units_not_historical_2002 | current_unit_mismatch | 0 | 0 |
| unece_instat_2011_gis_paper | official_statistical_system_evidence | not_boundary_source | negative_evidence_against_assuming_public_pre2011_digital_boundary | negative_pre2011_digital_map_evidence | 0 | 0 |

## Interpretation

- ALB_2002 household files expose district keys and survey timing, but no GPS, EA-map, official historical boundary, or accepted district-code-to-geometry crosswalk has been obtained.
- geoBoundaries 2.0.1 is the cleanest 36-feature public name-coverage lead, but its companion metadata reports boundary year 2013 and OpenStreetMap/Wambacher provenance, so it cannot be treated as a verified 2002 district layer.
- GADM 3.6 is a useful comparison lead because it is typed as Rreth/District and covers the 36 normalized keys, but duplicate `SHKODER` rows and missing official 2001/2002 provenance keep it blocked.
- IHGIS, HDX/COD-AB, current geoBoundaries, ASIG-current evidence, and the UNECE/INSTAT GIS paper all narrow the search space but do not provide a promoted ALB_2002 climate-linkage source.

## Required Resolution

The gate can move only if a future artifact supplies one of these with checksums and documentation: official ALB_2002 GPS/EA-map files, official 2001/2002 district or commune boundaries with codes, or a defensible continuity/crosswalk proof tying a public geometry to the 2002 LSMS district groups. Until then, climate-linkage-ready and data-write-ready rows remain zero.

## Machine-Readable Outputs

- `temp/alb2002_boundary_blocker_resolution_matrix.csv`
- `result/alb2002_boundary_blocker_resolution_summary.csv`
