# ALB_2002 Boundary Manual Source Follow-Up

Status: fail-closed follow-up audit. This report records source-specific evidence for the manual boundary verification queue. It does not download restricted files, does not create boundary centroids, and does not promote ALB_2002 to climate linkage.

## Summary

| Metric | Value | Interpretation |
|---|---:|---|
| alb2002_boundary_manual_source_followup_rows | 7 | Manual-source follow-up rows for ALB_2002 boundary verification leads. |
| alb2002_boundary_manual_source_followup_reachable_page_rows | 4 | Rows whose source page was reachable during the local follow-up probe. |
| alb2002_boundary_manual_source_followup_conclusive_blocker_rows | 7 | Rows with a source-specific blocker documented. |
| alb2002_boundary_manual_source_followup_district_level_ready_rows | 0 | Rows verified as 36-district or lower ALB_2002-compatible geography sources after follow-up; intentionally zero. |
| alb2002_boundary_manual_source_followup_climate_linkage_ready_rows | 0 | Rows ready for ALB_2002 climate-linkage promotion after follow-up; intentionally zero. |
| alb2002_boundary_manual_source_followup_ipums_level_status | blocked_prefecture_g1_not_36_lsms_districts | IHGIS follow-up status after browser-visible catalog review. |
| alb2002_boundary_manual_source_followup_unece_pre2011_map_status | blocked_pre2011_digital_boundary_source_absence_documented | UNECE/INSTAT follow-up status on pre-2011 national digital map availability. |
| alb2002_boundary_manual_source_followup_current_decision | blocked_followup_confirms_no_public_2002_district_boundary_source | Current fail-closed decision after manual-source follow-up. |

## Source Follow-Up Rows

| candidate_id | page_probe_status | verified_blocker_status | boundary_level_claim | next_action |
|---|---|---|---|---|
| worldbank_alb2002_lsms_study | reachable_page_sampled | blocked_artifact_access_not_level_proven | survey ancillary geography may exist, artifact not obtained | Request or download official ALB_2002 geography/GPS/EA-map files through the Microdata Library access route... |
| instat_census_2001 | reachable_page_sampled | blocked_context_without_boundary_file | official census context only | Search or request official 2001 cartography/boundary artifacts; do not promote census context alone. |
| ipums_ihgis_alb2001 | blocked_http_error | blocked_prefecture_g1_not_36_lsms_districts | prefectures g1 only in visible catalog evidence | Treat IHGIS as non-sufficient unless a separate Albania 2001 district/g2 boundary file or crosswalk is found. |
| geoboundaries_2_0_1_adm2 | reachable_page_sampled | blocked_boundary_year_2013_not_verified_2002 | ADM2 geometry with boundaryYear 2013 | Use only as a name-coverage and geometry lead until historical vintage/continuity and code crosswalk eviden... |
| asig_geoportal_current | blocked_http_error | blocked_historical_layer_not_verified | official current geoportal lead | Manually search/request historical administrative or census cartography layers, not current-only local-gove... |
| hdx_cod_ab_alb_2019_gazetteer_adm2 | reachable_page_sampled | blocked_2019_units_not_2002_lsms_districts | 2019 municipality-style ADM2 reference | Use only as a current reference unless a historical district-to-municipality crosswalk is documented. |
| unece_instat_2011_gis_paper | static_official_pdf_evidence_recorded | blocked_pre2011_digital_boundary_source_absence_documented | negative evidence on pre-2011 national digital map availability | Treat current/post-2011 public GIS layers as non-sufficient for ALB_2002 unless separate historical continu... |

## Interpretation

- IHGIS is no longer just an unresolved high-priority district candidate in this workspace. The browser-visible catalog evidence reviewed on 2026-07-09 shows Albania 2001 Population Census GIS only at prefecture (`g1`) level, so it does not satisfy the 36-district ALB_2002 linkage requirement unless a separate district/g2 source is found.
- The UNECE/INSTAT GIS implementation paper is direct negative evidence for easy public historical GIS substitution: it reports paper-based 2001 census maps and no national digital maps/spatial database before the 2011 census GIS build.
- World Bank and INSTAT remain potentially relevant because they are official survey/census channels, but they still require actual geography/GPS/EA-map/boundary artifacts.
- geoBoundaries 2.0.1 remains useful for name coverage but blocked by 2013 vintage/provenance.
- HDX and ASIG remain current or unverified historical leads only.
- Climate-linkage-ready rows remain zero.

## Machine-Readable Outputs

- `temp/alb2002_boundary_manual_source_followup_audit.csv`
- `result/alb2002_boundary_manual_source_followup_summary.csv`
