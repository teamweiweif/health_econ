# ALB_2002 Boundary Source Resource Search Audit

Status: temp-only public resource search. This audit parses public boundary or gazetteer resources and compares their names to the 36 observed ALB_2002 district groups. It does not create centroids, does not validate polygons, does not write `data/`, and does not construct climate exposures.

## Summary

| Metric | Value | Interpretation |
|---|---:|---|
| alb2002_boundary_resource_search_candidate_rows | 3 | Public boundary/gazetteer resources directly parsed or probed for ALB_2002. |
| alb2002_boundary_resource_search_parseable_resource_rows | 3 | Rows with a parsed GeoJSON or gazetteer name list. |
| alb2002_boundary_resource_search_complete_name_coverage_rows | 1 | Resources with no unmatched ALB_2002 survey district keys after documented repairs/aliases. |
| alb2002_boundary_resource_search_exact_unit_count_rows | 1 | Resources whose feature and distinct-key counts both equal the 36 observed survey district groups. |
| alb2002_boundary_resource_search_korce_available_rows | 2 | Resources whose parsed names include a canonical KORCE boundary key. |
| alb2002_boundary_resource_search_2002_historical_ready_rows | 0 | Resources verified as 2002 historical boundary inputs after this audit; intentionally zero. |
| alb2002_boundary_resource_search_climate_linkage_ready_rows | 0 | Resources ready for climate-linkage input promotion after this audit; intentionally zero. |
| alb2002_boundary_resource_search_best_candidate_id | geoboundaries_2_0_1_adm2 | Best current lead by name coverage only; not a promoted analytical input. |
| alb2002_boundary_resource_search_best_candidate_exact_matches | 33 | Exact normalized matches for the best name-coverage candidate. |
| alb2002_boundary_resource_search_best_candidate_repaired_matches | 2 | Mojibake/encoding-repaired matches for the best name-coverage candidate. |
| alb2002_boundary_resource_search_best_candidate_alias_matches | 1 | Documented alias matches for the best name-coverage candidate. |
| alb2002_boundary_resource_search_current_decision | blocked_alb2002_boundary_resource_search_no_historical_climate_ready_source | Current fail-closed decision for ALB_2002 public boundary resource search. |

## Resource-Level Results

| candidate_id | resource_status | source_year_claim | feature_count | distinct_boundary_key_count | exact_name_match_rows | repaired_encoding_match_rows | documented_alias_match_rows | unmatched_survey_rows | suitability_status |
|---|---|---|---|---|---|---|---|---|---|
| geoboundaries_current_pinned_adm2 | local_geojson_snapshot_parsed | 2021/current boundary source in prior ALB_2002 audit | 37 | 35 | 33 | 1 | 1 | 1 | blocked_current_boundary_name_or_unit_mismatch_not_historical |
| geoboundaries_2_0_1_adm2 | downloaded_geojson | geoBoundaries 2.0.1 public ADM2 release; 2002 historical boundary vintage not verified | 36 | 36 | 33 | 2 | 1 | 0 | candidate_complete_name_coverage_but_boundary_vintage_not_verified |
| hdx_cod_ab_alb_2019_gazetteer_adm2 | downloaded_hdx_2019_gazetteer_adm2_sheet | 2019 COD-AB administrative gazetteer; municipality units, not verified 2002 LSMS districts | 61 | 61 | 32 | 2 | 1 | 1 | blocked_2019_municipality_units_not_2002_lsms_districts |

## Name Gaps and Duplicate Keys

| candidate_id | has_korce | has_kucove | has_vlore | unmatched_survey_keys | unmatched_boundary_keys | duplicate_boundary_keys |
|---|---|---|---|---|---|---|
| geoboundaries_current_pinned_adm2 | 0 | 1 | 1 | KORCE |  | KUCOVE;VLORE |
| geoboundaries_2_0_1_adm2 | 1 | 1 | 1 |  |  |  |
| hdx_cod_ab_alb_2019_gazetteer_adm2 | 1 | 1 | 1 | HAS | BELSH;CERRIK;DIVJAKE;DROPULL;FINIQ;FUSHE ARREZ;HIMARE;KAMEZ;KELCYRE;KLOS;KONISPOL;KRUME;LIBOHOVE;MALIQ;MEMALIAJ;PATOS... |  |

## Interpretation

- The older geoBoundaries 2.0.1 ADM2 GeoJSON is the strongest public lead by name coverage: it has 36 parsed features, 36 distinct normalized boundary keys, and no unmatched ALB_2002 survey district keys after documented repairs.
- That lead is not an analytical input yet. The audit has not verified represented boundary year, source provenance, geometry quality, official 2001/2002 district definitions, or join keys to raw ALB_2002 district codes.
- The current pinned geoBoundaries snapshot remains blocked as a current-boundary comparison with incomplete name/unit evidence.
- HDX COD-AB is useful context for current administrative geography but is a 2019 municipality-style gazetteer and is not a 2002 district boundary layer.
- Historical-boundary-ready and climate-linkage-ready rows remain zero.

## Machine-Readable Outputs

- `temp/alb2002_boundary_source_resource_search_audit.csv`
- `result/alb2002_boundary_source_resource_search_summary.csv`
- `temp/source_snapshots/alb2002_geoboundaries_2_0_1_alb_adm2.geojson`
- `temp/source_snapshots/hdx_cod_ab_alb_package_show.json`
- `temp/source_snapshots/hdx_alb_adm_gazetteer_2019.xlsx`
