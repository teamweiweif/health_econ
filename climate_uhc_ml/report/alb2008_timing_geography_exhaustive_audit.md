# ALB_2008 Timing And Geography Exhaustive Audit

Status: raw-value timing/geography audit only. This report scans ALB_2008 raw SPSS files for timing and geography keyword hits and classifies whether they can support climate linkage. It does not construct climate exposures and does not write any file to `data/`.

## Summary

| Metric | Value | Interpretation |
|---|---:|---|
| alb2008_timing_geography_audit_rows | 225 | Timing/geography keyword rows scanned from ALB_2008 raw files. |
| alb2008_timing_geography_source_files_scanned | 42 | ALB_2008 .sav files scanned. |
| alb2008_timing_geography_read_failures | 0 | Raw files that could not be read by pyreadstat. |
| alb2008_interview_timing_candidate_rows | 0 | Rows with apparent interview/fieldwork timing wording requiring context. |
| alb2008_interview_timing_verified_rows | 0 | Verified household interview month/date rows available for climate linkage. |
| alb2008_rejected_non_interview_timing_rows | 62 | Rows rejected as birth, recall, duration, payment-period, or event-history timing. |
| alb2008_rejected_migration_history_rows | 18 | Rows rejected as migration or historical residence geography/timing. |
| alb2008_context_review_geography_timing_rows | 99 | Rows with timing/geography keywords requiring context but not verified for climate linkage. |
| alb2008_psu_cluster_key_rows | 42 | PSU/cluster-like key rows observed. |
| alb2008_coordinate_candidate_rows | 0 | GPS/latitude/longitude/coordinate candidate rows observed. |
| alb2008_coarse_full_coverage_geography_candidate_rows | 4 | Rows for full-coverage coarse survey geography/design fields in poverty.sav. |
| alb2008_coarse_geography_household_rows | 3599 | Maximum nonmissing household rows across coarse poverty.sav geography/design fields. |
| alb2008_geography_verified_full_coverage_rows | 0 | Verified admin/GPS geography rows ready for climate linkage. |
| alb2008_climate_linkage_ready_rows | 0 | Rows ready to support climate linkage input construction. |
| alb2008_timing_geography_current_decision | blocked_missing_interview_timing_coarse_geography_no_gps | Current ALB_2008 timing/geography decision. |

## Priority Candidate Rows

| source_file | variable_name | variable_label | candidate_role | nonmissing_rows | household_base_match_rows | geography_timing_status |
|---|---|---|---|---|---|---|
| filters_and_single.sav | psu | psu | psu_cluster_key | 3599 | 3599 | cluster_key_no_coordinate |
| Modul_10_fertility.sav | psu | psu | psu_cluster_key | 369 | 342 | cluster_key_no_coordinate |
| Modul_12A_non_food_expenditures_a.sav | psu | psu | psu_cluster_key | 53985 | 3599 | cluster_key_no_coordinate |
| Modul_12B_non_food_expenditures_b.sav | psu | psu | psu_cluster_key | 64782 | 3599 | cluster_key_no_coordinate |
| Modul_12C_non_food_expenditures_c.sav | psu | psu | psu_cluster_key | 64782 | 3599 | cluster_key_no_coordinate |
| Modul_13A_dwelling.sav | psu | psu | psu_cluster_key | 3599 | 3599 | cluster_key_no_coordinate |
| Modul_13B_dwelling_b.sav | psu | psu | psu_cluster_key | 3599 | 3599 | cluster_key_no_coordinate |
| Modul_13C1_dwelling.sav | psu | psu | psu_cluster_key | 89975 | 3599 | cluster_key_no_coordinate |
| Modul_13C2_dwelling.sav | psu | psu | psu_cluster_key | 21878 | 3582 | cluster_key_no_coordinate |
| Modul_13C3_dwelling.sav | psu | psu | psu_cluster_key | 28792 | 3599 | cluster_key_no_coordinate |
| Modul_14_social_assistance.sav | psu | psu | psu_cluster_key | 53985 | 3599 | cluster_key_no_coordinate |
| Modul_15_other_income.sav | psu | psu | psu_cluster_key | 53985 | 3599 | cluster_key_no_coordinate |
| Modul_16_social_capital.sav | psu | psu | psu_cluster_key | 3599 | 3599 | cluster_key_no_coordinate |
| Modul_17_id_of_agric_household.sav | psu | psu | psu_cluster_key | 3977 | 1661 | cluster_key_no_coordinate |
| Modul_17_id_of_agric_household_animals.sav | psu | psu | psu_cluster_key | 13860 | 1386 | cluster_key_no_coordinate |
| Modul_1A_household_roster.sav | psu | psu | psu_cluster_key | 14869 | 3599 | cluster_key_no_coordinate |
| Modul_1B_household_roster.sav | psu | psu | psu_cluster_key | 14869 | 3599 | cluster_key_no_coordinate |
| Modul_2A_education.sav | psu | psu | psu_cluster_key | 14869 | 3599 | cluster_key_no_coordinate |
| Modul_2B_education.sav | psu | PSU | psu_cluster_key | 14875 | 0 | cluster_key_no_coordinate |
| Modul_2C_education.sav | psu | psu | psu_cluster_key | 10199 | 2009 | cluster_key_no_coordinate |
| Modul_2D_education.sav | psu | psu | psu_cluster_key | 1632 | 1632 | cluster_key_no_coordinate |
| Modul_3_communication.sav | psu | psu | psu_cluster_key | 14869 | 3599 | cluster_key_no_coordinate |
| Modul_3_communication_mobile_phones.sav | psu | psu | psu_cluster_key | 13229 | 3086 | cluster_key_no_coordinate |
| Modul_4A_labour.sav | psu | psu | psu_cluster_key | 14869 | 3599 | cluster_key_no_coordinate |
| Modul_4B_labour.sav | psu | psu | psu_cluster_key | 5189 | 2811 | cluster_key_no_coordinate |
| Modul_4C_labour.sav | psu | psu | psu_cluster_key | 5044 | 2810 | cluster_key_no_coordinate |
| Modul_4D_labour.sav | psu | psu | psu_cluster_key | 951 | 369 | cluster_key_no_coordinate |
| Modul_5_non_farm_business.sav | psu | psu | psu_cluster_key | 483 | 454 | cluster_key_no_coordinate |
| Modul_5_non_farm_business_first.sav | psu | psu | psu_cluster_key | 3599 | 3599 | cluster_key_no_coordinate |
| Modul_6A_migration.sav | psu | psu | psu_cluster_key | 14869 | 3599 | cluster_key_no_coordinate |
| Modul_6B_migration.sav | psu | psu | psu_cluster_key | 14869 | 3599 | cluster_key_no_coordinate |
| Modul_6B_migration_b2.sav | psu | psu | psu_cluster_key | 1057 | 881 | cluster_key_no_coordinate |
| Modul_6C_migration_c.sav | psu | psu | psu_cluster_key | 4612 | 1710 | cluster_key_no_coordinate |
| Modul_6D_migration_d.sav | psu | psu | psu_cluster_key | 3599 | 3599 | cluster_key_no_coordinate |
| Modul_6D_migration_d2.sav | psu | psu | psu_cluster_key | 22842 | 3428 | cluster_key_no_coordinate |
| Modul_6E_migration_e.sav | psu | psu | psu_cluster_key | 53985 | 3599 | cluster_key_no_coordinate |
| Modul_7_subjective_poverty.sav | psu | psu | psu_cluster_key | 3599 | 3599 | cluster_key_no_coordinate |
| Modul_9A_health.sav | psu | psu | psu_cluster_key | 14869 | 3599 | cluster_key_no_coordinate |
| Modul_9B_health.sav | psu | psu | psu_cluster_key | 3599 | 3599 | cluster_key_no_coordinate |
| Modul_9C_health.sav | psu | psu | psu_cluster_key | 3599 | 3599 | cluster_key_no_coordinate |

## Rejected Timing/Geography Keyword Rows

| source_file | variable_name | variable_label | candidate_role | nonmissing_rows | geography_timing_status |
|---|---|---|---|---|---|
| filters_and_single.sav | m10_q01 | woman in hh given birth in last 3 years | not_survey_timing_birth_date | 3599 | rejected_not_interview_timing |
| Modul_10_fertility.sav | m10_q5d | date of birth - day | not_survey_timing_birth_date | 369 | rejected_not_interview_timing |
| Modul_10_fertility.sav | m10_q5m | date of birth - month | not_survey_timing_birth_date | 369 | rejected_not_interview_timing |
| Modul_10_fertility.sav | m10_q5y | date of birth - year | not_survey_timing_birth_date | 369 | rejected_not_interview_timing |
| Modul_10_fertility.sav | m10_q09 | period of 1st visit | not_survey_timing_visit_count | 345 | rejected_not_interview_timing |
| Modul_10_fertility.sav | m10_q16 | months breastfed | not_survey_timing_duration_or_payment_period | 140 | rejected_not_interview_timing |
| Modul_10_fertility.sav | m10_q18 | gave birth in last 3 years | not_survey_timing_birth_date | 369 | rejected_not_interview_timing |
| Modul_12A_non_food_expenditures_a.sav | m12a_q02 | bought item in past 30 days | not_survey_timing_recall_period | 53985 | rejected_not_interview_timing |
| Modul_12A_non_food_expenditures_a.sav | m12a_q03 | amount spent in past 30 days | not_survey_timing_recall_period | 16935 | rejected_not_interview_timing |
| Modul_12B_non_food_expenditures_b.sav | m12b_q02 | bought any in last 6 months | not_survey_timing_recall_period | 64782 | rejected_not_interview_timing |
| Modul_12C_non_food_expenditures_c.sav | m12c_q02 | bought item in past 12 months | not_survey_timing_recall_period | 64782 | rejected_not_interview_timing |
| Modul_12C_non_food_expenditures_c.sav | m12c_q03 | amount spent in past 12 months | not_survey_timing_recall_period | 10139 | rejected_not_interview_timing |
| Modul_13A_dwelling.sav | m13a_q27 | monthly rent | not_survey_timing_duration_or_payment_period | 125 | rejected_not_interview_timing |
| Modul_13A_dwelling.sav | m13a_q31 | month inhabit this dwelling | not_survey_timing_event_history | 32 | rejected_not_interview_timing |
| Modul_13A_dwelling.sav | m13a_q32 | year inhabit this dwelling | not_survey_timing_event_history | 32 | rejected_not_interview_timing |
| Modul_13A_dwelling.sav | m13a_q60 | months of process | not_survey_timing_duration_or_payment_period | 1420 | rejected_not_interview_timing |
| Modul_13B_dwelling_b.sav | m13b_q28 | months covered in payment | not_survey_timing_duration_or_payment_period | 3258 | rejected_not_interview_timing |
| Modul_13B_dwelling_b.sav | m13b_q53 | months covered in payment | not_survey_timing_duration_or_payment_period | 1148 | rejected_not_interview_timing |
| Modul_14_social_assistance.sav | m14_q5m | month started receiving assistance | not_survey_timing_event_history | 2335 | rejected_not_interview_timing |
| Modul_14_social_assistance.sav | m14_q5y | year started receiving assistance | not_survey_timing_event_history | 2335 | rejected_not_interview_timing |
| Modul_14_social_assistance.sav | m14_q07 | number of months | not_survey_timing_duration_or_payment_period | 2335 | rejected_not_interview_timing |
| Modul_14_social_assistance.sav | m14_q13m | month started receiving assistance | not_survey_timing_event_history | 504 | rejected_not_interview_timing |
| Modul_14_social_assistance.sav | m14_q13y | year started receiving assistance | not_survey_timing_event_history | 504 | rejected_not_interview_timing |
| Modul_14_social_assistance.sav | m14_q15 | number of months | not_survey_timing_duration_or_payment_period | 504 | rejected_not_interview_timing |
| Modul_14_social_assistance.sav | m14_q21m | month started receiving assistance | not_survey_timing_event_history | 4 | rejected_not_interview_timing |
| Modul_14_social_assistance.sav | m14_q21y | year started receiving assistance | not_survey_timing_event_history | 4 | rejected_not_interview_timing |
| Modul_14_social_assistance.sav | m14_q23 | number of months | not_survey_timing_duration_or_payment_period | 4 | rejected_not_interview_timing |
| Modul_1A_household_roster.sav | m1a_q4d | date of birth - day | not_survey_timing_birth_date | 14869 | rejected_not_interview_timing |
| Modul_1A_household_roster.sav | m1a_q4m | date of birth - month | not_survey_timing_birth_date | 14869 | rejected_not_interview_timing |
| Modul_1A_household_roster.sav | m1a_q4y | date of birth - year | not_survey_timing_birth_date | 14869 | rejected_not_interview_timing |
| Modul_2A_education.sav | m2a_q05 | amount per month | not_survey_timing_duration_or_payment_period | 223 | rejected_not_interview_timing |
| Modul_2B_education.sav | m2b_q46 | Received any private tutoring during current academic year | not_survey_timing_event_history | 3270 | rejected_not_interview_timing |
| Modul_2C_education.sav | m2c_q12 | times visited school {2008} | not_survey_timing_visit_count | 2856 | rejected_not_interview_timing |
| Modul_3_communication.sav | m3_q06 | used internet past month | not_survey_timing_recall_period | 1183 | rejected_not_interview_timing |
| Modul_3_communication_mobile_phones.sav | m3_q10 | year of acquisition | not_survey_timing_event_history | 5361 | rejected_not_interview_timing |
| Modul_4B_labour.sav | m4b_q04 | number of weeks worked in past 12 months | not_survey_timing_recall_period | 5189 | rejected_not_interview_timing |
| Modul_4C_labour.sav | m4c_q21m | month started job | not_survey_timing_event_history | 5044 | rejected_not_interview_timing |
| Modul_4C_labour.sav | m4c_q21y | year started job | not_survey_timing_event_history | 5044 | rejected_not_interview_timing |
| Modul_4D_labour.sav | m4d_q2m | month began | not_survey_timing_event_history | 951 | rejected_not_interview_timing |
| Modul_4D_labour.sav | m4d_q2y | year began | not_survey_timing_event_history | 951 | rejected_not_interview_timing |

## Interpretation

- No verified household interview month/date variable was found, so pre-interview 1, 3, 6, or 12 month climate windows remain blocked.
- `area`, `stratum`, `urbrur`, and `tirana_o` in `poverty.sav` have broad household coverage but are coarse survey geography/design fields, not verified admin/GPS climate-linkage locations.
- No GPS, latitude, longitude, or coordinate candidates were found in the public ALB_2008 SPSS files.
- PSU variables are merge/cluster keys, not climate locations, unless an official PSU-coordinate or admin crosswalk is obtained.
- Many date/month/year hits are birth dates, migration history, event history, illness durations, payment periods, or recall windows. They cannot substitute for survey fieldwork timing.
- ALB_2008 remains unusable for climate linkage until fieldwork timing and valid geography are documented.

## Machine-Readable Outputs

- `temp/alb2008_timing_geography_exhaustive_audit.csv`
- `result/alb2008_timing_geography_exhaustive_summary.csv`
