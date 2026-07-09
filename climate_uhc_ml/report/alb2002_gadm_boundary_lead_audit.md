# ALB_2002 GADM Boundary Lead Audit

Status: fail-closed source audit. This checks whether public GADM Albania ADM2 shapefiles can resolve the ALB_2002 district-boundary blocker.

## Summary

| Metric | Value | Interpretation |
|---|---:|---|
| alb2002_gadm_boundary_lead_candidate_rows | 2 | GADM source candidates audited. |
| alb2002_gadm36_adm2_row_count | 37 | GADM 3.6 ADM2 feature rows. |
| alb2002_gadm36_distinct_normalized_key_count | 36 | GADM 3.6 distinct normalized ADM2 keys. |
| alb2002_gadm36_engtype_district_rows | 37 | GADM 3.6 rows labeled as District. |
| alb2002_gadm36_type_rreth_rows | 37 | GADM 3.6 rows labeled as Rreth. |
| alb2002_gadm36_complete_name_coverage_rows | 1 | Whether GADM 3.6 covers all 36 normalized ALB_2002 district keys with no extra keys. |
| alb2002_gadm36_duplicate_boundary_key_count | 1 | Distinct duplicated normalized GADM 3.6 boundary keys. |
| alb2002_gadm36_duplicate_boundary_feature_rows | 2 | GADM 3.6 feature rows belonging to duplicated keys. |
| alb2002_gadm41_adm2_row_count | 37 | GADM 4.1 ADM2 feature rows. |
| alb2002_gadm41_engtype_district_rows | 0 | GADM 4.1 rows labeled as District; expected zero because type fields are NA. |
| alb2002_gadm_boundary_lead_historical_2002_ready_rows | 0 | Rows ready as verified 2001/2002 historical district boundaries after this audit; intentionally zero. |
| alb2002_gadm_boundary_lead_climate_linkage_ready_rows | 0 | Rows ready for ALB_2002 climate-linkage promotion after this audit; intentionally zero. |
| alb2002_gadm_boundary_lead_current_decision | blocked_gadm_boundary_lead_no_verified_2002_historical_provenance | Current fail-closed decision for the GADM boundary lead. |

## Source Status

| Suitability status | Count |
|---|---:|
| candidate_name_coverage_but_duplicate_key_and_provenance_blocked | 1 |
| candidate_name_coverage_but_not_historical_or_typed_district_ready | 1 |

## Candidate Rows

| candidate_id | download_status | adm2_row_count | adm2_distinct_normalized_key_count | adm2_engtype_district_rows | complete_name_coverage | duplicate_boundary_key_count | climate_linkage_ready | suitability_status |
|---|---|---|---|---|---|---|---|---|
| gadm36_alb_adm2 | already_exists | 37 | 36 | 37 | 1 | 1 | 0 | candidate_name_coverage_but_duplicate_key_and_provenance_blocked |
| gadm41_alb_adm2 | already_exists | 37 | 36 | 0 | 1 | 1 | 0 | candidate_name_coverage_but_not_historical_or_typed_district_ready |

## Duplicate Boundary Keys

| candidate_id | survey_district_key | boundary_gid | boundary_name_1 | boundary_name_2 | boundary_type_2 | boundary_engtype_2 | notes |
|---|---|---|---|---|---|---|---|
| gadm36_alb_adm2 | SHKODER | ALB.9.4_1 | Lezhë | Shkodrës | Rreth | District | Multiple GADM ADM2 features normalize to this district key. |
| gadm36_alb_adm2 | SHKODER | ALB.10.3_1 | Shkodër | Shkodrës | Rreth | District | Multiple GADM ADM2 features normalize to this district key. |
| gadm41_alb_adm2 | SHKODER | ALB.9.4_1 | Lezhë | Shkodrës | NA | NA | Multiple GADM ADM2 features normalize to this district key. |
| gadm41_alb_adm2 | SHKODER | ALB.10.3_1 | Shkodër | Shkodrës | NA | NA | Multiple GADM ADM2 features normalize to this district key. |

## Interpretation

- GADM 3.6 is a stronger public lead than current-boundary sources because its ADM2 rows are labeled `Rreth` / `District` and the normalized names cover the ALB_2002 district keys after documented encoding and genitive-name repairs.
- The GADM 3.6 ADM2 table still has 37 feature rows and 36 normalized keys because `SHKODER` appears twice under different parent counties.
- GADM 4.1 also has 37 ADM2 rows, but its ADM2 type fields are `NA`, so it is not a clearer historical district source.
- Neither GADM snapshot provides verified official 2001/2002 boundary provenance, LSMS join-key documentation, or geometry validation in this audit.
- Historical-boundary-ready rows and climate-linkage-ready rows remain zero.

## Machine-Readable Outputs

- `temp/alb2002_gadm_boundary_lead_audit.csv`
- `temp/alb2002_gadm_boundary_name_match_audit.csv`
- `result/alb2002_gadm_boundary_lead_summary.csv`
- `temp/source_snapshots/gadm36_ALB_shp.zip`
- `temp/source_snapshots/gadm41_ALB_shp.zip`
