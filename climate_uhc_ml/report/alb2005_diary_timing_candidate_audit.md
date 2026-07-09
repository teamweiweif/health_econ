# ALB_2005 Diary Timing Candidate Audit

Status: fail-closed timing-candidate audit. The saved DDI and metadata schema expose `bookmetadata_cl` date variables for diary beginning and finishing, with May-July 2005 metadata categories and 3,840 F96 metadata rows. These are useful timing candidates, but they are not promoted as household interview timing or climate-linkage inputs because no raw `bookmetadata_cl` file is present under `temp/raw_downloads` or `temp/raw_extracted`, merge coverage is not verified, and diary beginning/finishing dates are not automatically the household interview date.

## Summary

| Metric | Value | Interpretation |
|---|---:|---|
| alb2005_diary_timing_candidate_audit_rows | 11 | Bookmetadata timing/key variable rows audited from metadata and DDI. |
| alb2005_diary_timing_candidate_metadata_found_rows | 11 | Rows found in both the metadata variable catalog and saved DDI XML. |
| alb2005_diary_timing_candidate_schema_file_rows | 3840 | F96 bookmetadata_cl row count from schema inventory metadata. |
| alb2005_diary_timing_candidate_schema_variable_rows | 18 | F96 bookmetadata_cl variable count from schema inventory metadata. |
| alb2005_diary_timing_candidate_raw_bookmetadata_files_present | 0 | Whether a raw bookmetadata file was found under temp/raw_downloads or temp/raw_extracted. |
| alb2005_diary_timing_candidate_key_candidate_rows | 3 | PSU/household key candidates with nonzero DDI valid counts. |
| alb2005_diary_timing_candidate_date_candidate_rows | 6 | Diary beginning/finishing day/month/year candidates with nonzero DDI valid counts. |
| alb2005_diary_timing_candidate_max_valid_count | 57245 | Largest DDI valid count across candidate variables. |
| alb2005_diary_timing_candidate_rejected_all_missing_rows | 2 | Verification date fields rejected because DDI summary shows all missing or zero valid. |
| alb2005_diary_timing_candidate_household_timing_promoted_rows | 0 | Rows promoted as household interview timing after this audit; intentionally zero. |
| alb2005_diary_timing_candidate_climate_linkage_ready_rows | 0 | Rows ready for climate linkage after this audit; intentionally zero. |
| alb2005_diary_timing_candidate_public_fieldwork_verified_rows | 10 | Verified public fieldwork/geography source rows from the upstream public metadata audit. |
| alb2005_diary_timing_candidate_current_decision | blocked_diary_timing_metadata_candidate_no_raw_merge_semantics | Current fail-closed decision for diary timing candidates. |

## Candidate Variables

| variable_name | concept_role | ddi_valid_count | ddi_min | ddi_max | promotion_status | candidate_use |
|---|---|---|---|---|---|---|
| ma_q00 | psu_key | 57245 | 1 | 480 | candidate_key_not_merge_verified | Potential PSU key for linking diary timing metadata to the household frame. |
| ma_q01 | household_id_component | 57245 | 1 | 12 | candidate_key_not_merge_verified | Potential household ID component in bookmetadata_cl. |
| hhid | household_identifier | 3840 | 101 | 48008 | candidate_key_not_merge_verified | Potential household identifier in bookmetadata_cl. |
| ma_q04d | diary_beginning_day | 3840 | 1 | 31 | candidate_diary_timing_not_interview_verified | Diary beginning day candidate, not automatically the household interview day. |
| ma_q04m | diary_beginning_month | 3840 | 5 | 7 | candidate_diary_timing_not_interview_verified | Diary beginning month candidate with May-July metadata categories. |
| ma_q04y | diary_beginning_year | 3840 | 2005 | 2005 | candidate_diary_timing_not_interview_verified | Diary beginning year candidate. |
| ma_q05d | diary_finishing_day | 3840 | 1 | 31 | candidate_diary_timing_not_interview_verified | Diary finishing day candidate, not automatically the household interview day. |
| ma_q05m | diary_finishing_month | 3840 | 5 | 7 | candidate_diary_timing_not_interview_verified | Diary finishing month candidate with May-July metadata categories. |
| ma_q05y | diary_finishing_year | 3840 | 2005 | 2005 | candidate_diary_timing_not_interview_verified | Diary finishing year candidate. |
| ma_q08 | verification_month | 0 |  |  | rejected_all_missing_not_interview_timing | Verification month is all missing in DDI summary and is not a timing source. |
| ma_q09 | verification_day | 0 |  |  | rejected_all_missing_not_interview_timing | Verification day is all missing in DDI summary and is not a timing source. |

## Interpretation

- `ma_q04d`, `ma_q04m`, and `ma_q04y` are diary beginning date candidates.
- `ma_q05d`, `ma_q05m`, and `ma_q05y` are diary finishing date candidates.
- `ma_q00`, `ma_q01`, and `hhid` are key candidates needed to merge diary timing to the household frame.
- `ma_q08` and `ma_q09` are rejected for this purpose because the DDI summary shows zero valid verification-date values.
- No timing variable is promoted until raw values, merge cardinality, diary protocol semantics, and exposure-window implications are reviewed.

## Machine-Readable Outputs

- `temp/alb2005_diary_timing_candidate_audit.csv`
- `result/alb2005_diary_timing_candidate_summary.csv`
