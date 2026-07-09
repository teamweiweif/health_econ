# ALB_2002 Boundary Source Alternatives Audit

Status: temp-only source-alternatives audit. This audit reviews local boundary evidence and probes public source landing pages for ALB_2002 historical district-boundary candidates. It does not download shapefiles, does not create centroids, does not write `data/`, and does not construct climate exposures.

## Summary

| Metric | Value | Interpretation |
|---|---:|---|
| alb2002_boundary_source_alternative_rows | 6 | Boundary/geography source alternatives audited for ALB_2002. |
| alb2002_boundary_source_alternative_reachable_rows | 4 | Rows with either a sampled web page or an existing local artifact review. |
| alb2002_boundary_source_alternative_current_or_post2015_rows | 2 | Sources that are current or post-2015/post-2019 boundary candidates rather than verified 2002 district sources. |
| alb2002_boundary_source_alternative_lsms_maps_documented_rows | 1 | Sources whose sampled page documents LSMS EA boundary maps. |
| alb2002_boundary_source_alternative_gps_documented_rows | 1 | Sources whose sampled page documents GPS or longitude/latitude evidence. |
| alb2002_boundary_source_alternative_historical_candidate_rows | 3 | Historical/census-context source candidates that still require boundary-level and join-key verification. |
| alb2002_boundary_source_alternative_historical_2002_boundary_ready_rows | 0 | Sources verified as ready 2001/2002 district boundary inputs after this audit; intentionally zero. |
| alb2002_boundary_source_alternative_climate_linkage_ready_rows | 0 | Sources ready for climate-linkage input promotion after this audit; intentionally zero. |
| alb2002_boundary_source_alternative_current_decision | blocked_no_public_2002_district_boundary_source_verified | Current fail-closed decision for ALB_2002 boundary-source alternatives. |

## Source Alternatives

| candidate_id | source_name | probe_status | http_status | source_year_claim | boundary_suitability_status | historical_2002_boundary_ready | climate_linkage_ready |
|---|---|---|---|---|---|---|---|
| geoboundaries_2_0_1_adm2 | geoBoundaries 2.0.1 Albania ADM2 geometry/provenance lead | local_artifact_review |  | 2013 boundary year per companion metadata | blocked_complete_geometry_boundary_year_2013_not_verified_2002 | 0 | 0 |
| hdx_cod_ab_alb | HDX COD-AB Albania subnational administrative boundaries | reachable_page_sampled | 202 | 2015 administrative boundaries per COD-AB catalog metadata/search result | blocked_current_or_post2015_boundary_not_historical_2002_lsms | 0 | 0 |
| asig_geoportal_current | ASIG Geoportal Albania data catalog | blocked_http_error | 302 | updated current administrative map / 2019 local-government division metadata | blocked_current_or_post2019_boundary_not_historical_2002_lsms | 0 | 0 |
| worldbank_alb2002_lsms_study | World Bank Microdata Library ALB_2002 LSMS study page | reachable_page_sampled | 200 | 2002 survey; sampling frame based on April 2001 census | blocked_lsms_sampling_geography_documented_no_direct_gis_artifact_verified | 0 | 0 |
| instat_census_2001 | INSTAT Census of Population and Housing page | reachable_page_sampled | 200 | 2001 census context present; no district GIS artifact verified by this audit | blocked_official_census_context_no_public_district_gis_verified | 0 | 0 |
| ipums_ihgis_alb2001 | IPUMS IHGIS Albania 2001 census GIS boundary files | blocked_http_error | 403 | Albania 2001 Population Census boundary context; level not verified as LSMS district by this audit | blocked_historical_census_candidate_not_lsms_district_crosswalk_verified | 0 | 0 |

## Evidence and Blocking Reasons

| candidate_id | page_evidence_flags | local_or_page_evidence | blocking_reason |
|---|---|---|---|
| geoboundaries_2_0_1_adm2 |  | Local geoBoundaries 2.0.1 geometry/provenance audit found 36 ADM2 features and 36 ALB_2002 survey district-key matche... | The candidate has complete 36-district name/key coverage, but its companion metadata reports a 2013 boundary year and... |
| hdx_cod_ab_alb |  | Candidate humanitarian COD-AB source; probed as an alternative public boundary catalog, not as an LSMS sampling-frame... | The audit did not verify a 2001/2002 LSMS district or EA boundary file from this source, and current/post-2015 admini... |
| asig_geoportal_current |  | Official national geospatial catalog candidate; probed only for landing-page evidence. Page text was not sampled beca... | The audit did not verify a public 2001/2002 LSMS district, EA, or GPS boundary artifact. Current official administrat... |
| worldbank_alb2002_lsms_study | lsms_ea_boundary_maps_documented;gps_or_coordinates_documented;official_2001_census_context;post_2002_2019_boundary_c... | Official study description documents the ALB_2002 sampling frame, fieldwork period, EA maps, and GPS intent, but the ... | Documentation evidence is not enough to construct climate exposure; the local audit still lacks a verified coordinate... |
| instat_census_2001 | official_2001_census_context | Official INSTAT census page documents the 2001 Census context but no directly audited 2001 district boundary file was... | The source is relevant to the LSMS sampling frame but does not by itself provide a verified district polygon or EA bo... |
| ipums_ihgis_alb2001 |  | IHGIS is a useful historical census GIS candidate, but the current audit has not verified that its available Albania ... | A historical census boundary catalog can still be unsuitable if it is only prefecture/tabulation geography, lacks dis... |

## Interpretation

- ALB_2002 remains the closest local wave for future analytical readiness because household timing, district code/name, consumption, weights, and OOP/access signals exist in temp-only audits.
    - Boundary evidence is still not climate-linkage ready. The strongest local geoBoundaries lead now has complete 36-district geometry/name coverage, but its companion metadata reports a 2013 boundary year rather than verified 2001/2002 LSMS district provenance.
- The official ALB_2002 study documentation is important because it points to EA maps and GPS recording, but this audit did not verify a directly usable GIS/GPS artifact in the current package.
- Historical census/GIS sources are candidate leads only until the boundary level, unit count, codes, names, projections, license, and join keys are manually verified against the 36 observed ALB_2002 district groups.
- Climate-linkage-ready rows remain zero.

## Machine-Readable Outputs

- `temp/alb2002_boundary_source_alternative_audit.csv`
- `result/alb2002_boundary_source_alternative_summary.csv`
