# ALB_2002 District Climate Crosswalk Audit

Status: temp-only boundary-readiness audit. This audit builds an ALB_2002 district crosswalk template and probes public ADM2 boundary metadata. It does not download polygons, does not geocode, does not assign centroids, does not write `data/climate_linkage_input.csv`, and does not construct climate exposures.

## Summary

| Metric | Value | Interpretation |
|---|---:|---|
| alb2002_district_crosswalk_household_rows | 3599 | Rows in temp/alb2002_household_core_candidate.csv. |
| alb2002_district_crosswalk_households_with_district | 3599 | Households with observed ALB_2002 district code. |
| alb2002_district_crosswalk_district_rows | 36 | Observed district code/name groups in the crosswalk template. |
| alb2002_district_crosswalk_survey_month_rows | 3599 | Households with raw survey month for climate windows. |
| alb2002_district_crosswalk_interview_date_rows | 3599 | Households with constructed interview date for climate windows. |
| alb2002_district_crosswalk_name_encoding_review_rows | 2 | District names with non-ASCII characters requiring raw-label encoding review. |
| alb2002_district_crosswalk_boundary_source_rows | 1 | Public boundary metadata sources probed. |
| alb2002_district_crosswalk_boundary_source_reachable_rows | 1 | Public boundary metadata sources reachable and saved. |
| alb2002_district_crosswalk_boundary_source_adm_unit_count | 37 | ADM unit count reported by the probed public boundary source. |
| alb2002_district_crosswalk_boundary_unit_count_match_rows | 0 | Template district rows where observed district count matches boundary unit count. |
| alb2002_district_crosswalk_template_ready_rows | 0 | Rows ready for crosswalk or data promotion after this audit. |
| alb2002_climate_linkage_ready_rows | 0 | ALB_2002 rows ready for climate-linkage input promotion after this audit. |
| alb2002_district_crosswalk_current_decision | blocked_boundary_crosswalk_not_verified_no_gps | Current fail-closed decision for ALB_2002 district climate crosswalk readiness. |

## Public Boundary Metadata Probe

| source_name | probe_status | boundary_type | boundary_year_represented | boundary_canonical | adm_unit_count | review_status |
|---|---|---|---|---|---|---|
| geoBoundaries gbOpen Albania ADM2 current API | reachable_metadata_saved | ADM2 | 2021 | rrethe | 37 | candidate_boundary_metadata_only_not_crosswalk_verified |

## District Template Preview

| district_code_identification | district_name_identification | household_rows | survey_month_values | interview_date_min | interview_date_max | crosswalk_status |
|---|---|---|---|---|---|---|
| 1 | BERAT | 120 | 4;5;6 | 2002-04-15 | 2002-06-22 | blocked_boundary_unit_count_mismatch_unverified |
| 10 | GJIROKASTER | 32 | 6;5;4 | 2002-04-17 | 2002-06-08 | blocked_boundary_unit_count_mismatch_unverified |
| 11 | HAS | 48 | 5;6;4 | 2002-04-30 | 2002-06-11 | blocked_boundary_unit_count_mismatch_unverified |
| 12 | KAVAJE | 88 | 4;5;6 | 2002-04-16 | 2002-06-04 | blocked_boundary_unit_count_mismatch_unverified |
| 13 | KOLONJE | 8 | 6 | 2002-06-10 | 2002-06-13 | blocked_boundary_unit_count_mismatch_unverified |
| 14 | KOR€E | 136 | 4;5;6 | 2002-04-01 | 2002-06-18 | blocked_boundary_unit_count_mismatch_unverified |
| 15 | KRUJE | 40 | 5;4;6 | 2002-04-17 | 2002-06-02 | blocked_boundary_unit_count_mismatch_unverified |
| 16 | KU€OVE | 32 | 5;4 | 2002-04-12 | 2002-05-28 | blocked_boundary_unit_count_mismatch_unverified |
| 17 | KUKES | 184 | 6;4;5;7 | 2002-04-17 | 2002-07-07 | blocked_boundary_unit_count_mismatch_unverified |
| 18 | KURBIN | 64 | 6;4;5 | 2002-04-15 | 2002-06-27 | blocked_boundary_unit_count_mismatch_unverified |
| 19 | LEZHE | 64 | 4;5;6 | 2002-04-15 | 2002-06-29 | blocked_boundary_unit_count_mismatch_unverified |
| 2 | BULQIZE | 128 | 4;5;6;7 | 2002-04-15 | 2002-07-01 | blocked_boundary_unit_count_mismatch_unverified |
| 20 | LIBRAZHD | 200 | 4;5;6 | 2002-04-15 | 2002-06-27 | blocked_boundary_unit_count_mismatch_unverified |
| 21 | LUSHNJE | 152 | 4;5 | 2002-04-16 | 2002-05-30 | blocked_boundary_unit_count_mismatch_unverified |
| 22 | MALESI E MADHE | 24 | 5;4 | 2002-04-22 | 2002-05-20 | blocked_boundary_unit_count_mismatch_unverified |
| 23 | MALLAKASTER | 32 | 5;4 | 2002-04-18 | 2002-05-18 | blocked_boundary_unit_count_mismatch_unverified |
| 24 | MAT | 32 | 4;5;6 | 2002-04-22 | 2002-06-14 | blocked_boundary_unit_count_mismatch_unverified |
| 25 | MIRDITE | 16 | 4;5 | 2002-04-24 | 2002-05-19 | blocked_boundary_unit_count_mismatch_unverified |
| 26 | PEQIN | 24 | 4;5 | 2002-04-18 | 2002-05-13 | blocked_boundary_unit_count_mismatch_unverified |
| 27 | PERMET | 16 | 5;4 | 2002-04-19 | 2002-05-11 | blocked_boundary_unit_count_mismatch_unverified |
| 28 | POGRADEC | 48 | 4;6;5 | 2002-04-17 | 2002-06-18 | blocked_boundary_unit_count_mismatch_unverified |
| 29 | PUKE | 24 | 6 | 2002-06-14 | 2002-06-28 | blocked_boundary_unit_count_mismatch_unverified |
| 3 | DELVINE | 16 | 4;6;5 | 2002-04-06 | 2002-06-19 | blocked_boundary_unit_count_mismatch_unverified |
| 30 | SARANDE | 48 | 6;5 | 2002-05-03 | 2002-06-29 | blocked_boundary_unit_count_mismatch_unverified |
| 31 | SKRAPAR | 16 | 4;5;6 | 2002-04-19 | 2002-06-23 | blocked_boundary_unit_count_mismatch_unverified |
| 32 | SHKODER | 143 | 4;5;6 | 2002-04-15 | 2002-06-15 | blocked_boundary_unit_count_mismatch_unverified |
| 33 | TEPELENE | 32 | 4;5 | 2002-04-18 | 2002-05-21 | blocked_boundary_unit_count_mismatch_unverified |
| 34 | TIRANE | 688 | 4;6;5;7 | 2002-04-15 | 2002-07-02 | blocked_boundary_unit_count_mismatch_unverified |
| 35 | TROPOJE | 88 | 4;6;5 | 2002-04-15 | 2002-06-05 | blocked_boundary_unit_count_mismatch_unverified |
| 36 | VLORE | 152 | 6;5;4 | 2002-04-15 | 2002-06-28 | blocked_boundary_unit_count_mismatch_unverified |
| 4 | DEVOLL | 16 | 4;5 | 2002-04-15 | 2002-05-20 | blocked_boundary_unit_count_mismatch_unverified |
| 5 | DIBER | 232 | 5;4;6 | 2002-04-17 | 2002-06-30 | blocked_boundary_unit_count_mismatch_unverified |
| 6 | DURRES | 160 | 5;4;6 | 2002-04-15 | 2002-06-20 | blocked_boundary_unit_count_mismatch_unverified |
| 7 | ELBASAN | 152 | 4;5;6 | 2002-04-15 | 2002-06-10 | blocked_boundary_unit_count_mismatch_unverified |
| 8 | FIER | 224 | 5;6;4 | 2002-04-15 | 2002-06-24 | blocked_boundary_unit_count_mismatch_unverified |
| 9 | GRAMSH | 120 | 4;5 | 2002-04-17 | 2002-05-31 | blocked_boundary_unit_count_mismatch_unverified |

## Interpretation

- ALB_2002 has observed district code/name groups plus survey month and interview date fields, which is useful for future admin-level climate windows.
- The probed public boundary metadata is candidate evidence only. It is not a verified survey-to-boundary crosswalk.
- The current metadata reports an ADM2 unit count that must be reconciled against the 36 observed ALB_2002 district groups before any aggregation.
- District names also need raw-label/encoding review before matching, because some labels contain non-ASCII or mojibake-like characters.
- No household or cluster GPS is available in the candidate, so any future climate linkage would be admin-level and must report measurement error.
- Climate-linkage-ready rows remain zero.

## Machine-Readable Outputs

- `temp/alb2002_district_climate_crosswalk_template.csv`
- `temp/alb2002_district_boundary_source_probe.csv`
- `temp/alb2002_geoboundaries_adm2_api.json` when the public API is reachable
- `result/alb2002_district_climate_crosswalk_summary.csv`
