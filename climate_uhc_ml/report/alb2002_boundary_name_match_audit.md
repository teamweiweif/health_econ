# ALB_2002 Boundary Name Match Audit

Status: temp-only public boundary name audit. This audit downloads a public current ADM2 GeoJSON snapshot to `temp/source_snapshots/`, compares boundary names with observed ALB_2002 district labels, and keeps promotion blocked. It does not create centroids, does not construct climate-linkage input, does not write `data/`, and does not construct climate exposures.

## Summary

| Metric | Value | Interpretation |
|---|---:|---|
| alb2002_boundary_name_match_survey_district_rows | 36 | ALB_2002 survey district rows compared to public boundary names. |
| alb2002_boundary_name_match_geojson_feature_rows | 37 | Features parsed from the public boundary GeoJSON snapshot. |
| alb2002_boundary_name_match_exact_rows | 34 | Survey rows matching boundary names by normalized exact match. |
| alb2002_boundary_name_match_euro_repaired_rows | 1 | Survey rows matching only after treating euro-sign mojibake as C. |
| alb2002_boundary_name_match_high_similarity_rows | 0 | Survey rows with high-similarity candidate matches requiring manual review. |
| alb2002_boundary_name_match_unmatched_survey_rows | 1 | Survey district rows without a candidate boundary-name match. |
| alb2002_boundary_name_match_unmatched_boundary_name_rows | 0 | Boundary-name keys not matched to an observed ALB_2002 district row. |
| alb2002_boundary_name_match_duplicate_boundary_name_keys | 2 | Distinct boundary-name keys appearing in more than one GeoJSON feature. |
| alb2002_boundary_name_match_duplicate_boundary_feature_rows | 4 | GeoJSON feature rows belonging to duplicate boundary-name keys. |
| alb2002_boundary_name_match_download_status | downloaded_geojson_snapshot | Public boundary GeoJSON download/parse status. |
| alb2002_boundary_name_match_download_error |  | Download or parse error if any. |
| alb2002_boundary_name_match_boundary_source_url | https://github.com/wmgeolab/geoBoundaries/raw/9469f09/releaseData/gbOpen/ALB/ADM2/geoBoundaries-ALB-ADM2.geojson | Public boundary GeoJSON source URL. |
| alb2002_boundary_name_match_boundary_year_represented | 2021 | Boundary year represented by the public source metadata. |
| alb2002_boundary_name_match_historical_year_ready_rows | 0 | Rows ready for 2002 historical boundary validity after this audit; intentionally zero. |
| alb2002_boundary_name_match_climate_linkage_ready_rows | 0 | Rows ready for climate-linkage input promotion after this audit; intentionally zero. |
| alb2002_boundary_name_match_current_decision | blocked_current_boundary_name_match_incomplete_historical_crosswalk_no_gps | Current fail-closed decision for ALB_2002 boundary name matching. |

## Survey-to-Boundary Name Match Preview

| district_code_identification | district_name_identification | survey_review_key_euro_as_c | best_boundary_name | best_match_method | match_status |
|---|---|---|---|---|---|
| 1 | BERAT | BERAT | Berat | exact_normalized_name_match | candidate_current_boundary_name_match_not_historical_or_geometric_verified |
| 10 | GJIROKASTER | GJIROKASTER | Gjirokastër | exact_normalized_name_match | candidate_current_boundary_name_match_not_historical_or_geometric_verified |
| 11 | HAS | HAS | Has | exact_normalized_name_match | candidate_current_boundary_name_match_not_historical_or_geometric_verified |
| 12 | KAVAJE | KAVAJE | Kavajë | exact_normalized_name_match | candidate_current_boundary_name_match_not_historical_or_geometric_verified |
| 13 | KOLONJE | KOLONJE | Kolonjë | exact_normalized_name_match | candidate_current_boundary_name_match_not_historical_or_geometric_verified |
| 14 | KOR€E | KORCE | Krujë | no_name_match | blocked_no_current_boundary_name_match |
| 15 | KRUJE | KRUJE | Krujë | exact_normalized_name_match | candidate_current_boundary_name_match_not_historical_or_geometric_verified |
| 16 | KU€OVE | KUCOVE | Kuçovë | mojibake_euro_as_c_name_match | candidate_current_boundary_name_match_not_historical_or_geometric_verified |
| 17 | KUKES | KUKES | Kukës | exact_normalized_name_match | candidate_current_boundary_name_match_not_historical_or_geometric_verified |
| 18 | KURBIN | KURBIN | Kurbin | exact_normalized_name_match | candidate_current_boundary_name_match_not_historical_or_geometric_verified |
| 19 | LEZHE | LEZHE | Lezhë | exact_normalized_name_match | candidate_current_boundary_name_match_not_historical_or_geometric_verified |
| 2 | BULQIZE | BULQIZE | Bulqizë | exact_normalized_name_match | candidate_current_boundary_name_match_not_historical_or_geometric_verified |
| 20 | LIBRAZHD | LIBRAZHD | Librazhd | exact_normalized_name_match | candidate_current_boundary_name_match_not_historical_or_geometric_verified |
| 21 | LUSHNJE | LUSHNJE | Lushnjë | exact_normalized_name_match | candidate_current_boundary_name_match_not_historical_or_geometric_verified |
| 22 | MALESI E MADHE | MALESI E MADHE | Malësi e Madhe | exact_normalized_name_match | candidate_current_boundary_name_match_not_historical_or_geometric_verified |
| 23 | MALLAKASTER | MALLAKASTER | Mallakastër | exact_normalized_name_match | candidate_current_boundary_name_match_not_historical_or_geometric_verified |
| 24 | MAT | MAT | Mat | exact_normalized_name_match | candidate_current_boundary_name_match_not_historical_or_geometric_verified |
| 25 | MIRDITE | MIRDITE | Mirditë | exact_normalized_name_match | candidate_current_boundary_name_match_not_historical_or_geometric_verified |
| 26 | PEQIN | PEQIN | Peqin | exact_normalized_name_match | candidate_current_boundary_name_match_not_historical_or_geometric_verified |
| 27 | PERMET | PERMET | Përmet | exact_normalized_name_match | candidate_current_boundary_name_match_not_historical_or_geometric_verified |
| 28 | POGRADEC | POGRADEC | Pogradec | exact_normalized_name_match | candidate_current_boundary_name_match_not_historical_or_geometric_verified |
| 29 | PUKE | PUKE | Pukë | exact_normalized_name_match | candidate_current_boundary_name_match_not_historical_or_geometric_verified |
| 3 | DELVINE | DELVINE | Delvinë | exact_normalized_name_match | candidate_current_boundary_name_match_not_historical_or_geometric_verified |
| 30 | SARANDE | SARANDE | Sarandë | exact_normalized_name_match | candidate_current_boundary_name_match_not_historical_or_geometric_verified |
| 31 | SKRAPAR | SKRAPAR | Skrapar | exact_normalized_name_match | candidate_current_boundary_name_match_not_historical_or_geometric_verified |
| 32 | SHKODER | SHKODER | Shkodër | exact_normalized_name_match | candidate_current_boundary_name_match_not_historical_or_geometric_verified |
| 33 | TEPELENE | TEPELENE | Tepelenë | exact_normalized_name_match | candidate_current_boundary_name_match_not_historical_or_geometric_verified |
| 34 | TIRANE | TIRANE | Tiranë | exact_normalized_name_match | candidate_current_boundary_name_match_not_historical_or_geometric_verified |
| 35 | TROPOJE | TROPOJE | Tropojë | exact_normalized_name_match | candidate_current_boundary_name_match_not_historical_or_geometric_verified |
| 36 | VLORE | VLORE | Vlorë | exact_normalized_name_match | candidate_current_boundary_name_match_not_historical_or_geometric_verified |
| 4 | DEVOLL | DEVOLL | Devoll | exact_normalized_name_match | candidate_current_boundary_name_match_not_historical_or_geometric_verified |
| 5 | DIBER | DIBER | Dibër | exact_normalized_name_match | candidate_current_boundary_name_match_not_historical_or_geometric_verified |
| 6 | DURRES | DURRES | Durrës | exact_normalized_name_match | candidate_current_boundary_name_match_not_historical_or_geometric_verified |
| 7 | ELBASAN | ELBASAN | Elbasan | exact_normalized_name_match | candidate_current_boundary_name_match_not_historical_or_geometric_verified |
| 8 | FIER | FIER | Fier | exact_normalized_name_match | candidate_current_boundary_name_match_not_historical_or_geometric_verified |
| 9 | GRAMSH | GRAMSH | Gramsh | exact_normalized_name_match | candidate_current_boundary_name_match_not_historical_or_geometric_verified |

## Unmatched Survey Districts

| district_code_identification | district_name_identification | survey_review_key_euro_as_c | best_boundary_name | best_match_score |
|---|---|---|---|---|
| 14 | KOR€E | KORCE | Krujë | 0.600 |

## Boundary Names Not Observed in ALB_2002

No unmatched boundary-name keys after candidate name matching.

## Duplicate Boundary Name Keys

| duplicate_boundary_review_key | feature_count |
|---|---|
| KUCOVE | 2 |
| VLORE | 2 |

## Interpretation

- Name matches are candidate evidence only; they are not a historical boundary crosswalk.
- The public boundary source is represented as current ADM2 metadata, not verified 2002 LSMS fieldwork geography.
- Two ALB_2002 district labels require mojibake-style review before accepting any automated name match.
- The public boundary file has a different unit count from the observed survey district groups, and duplicate/missing name evidence must be explained before climate linkage.
- No household or cluster GPS exists in the ALB_2002 candidate; any future linkage would be admin-level and must report measurement error.
- Climate-linkage-ready rows remain zero.

## Machine-Readable Outputs

- `temp/alb2002_boundary_name_match_audit.csv`
- `temp/alb2002_boundary_geojson_inventory.csv`
- `temp/source_snapshots/alb2002_geoboundaries_alb_adm2_current.geojson`
- `result/alb2002_boundary_name_match_summary.csv`
