# ALB_2005 Timing And Geography Exhaustive Audit

Status: raw-value timing/geography audit only. This report scans ALB_2005 raw SPSS files for timing and geography keyword hits and classifies whether they can support climate linkage. It does not construct climate exposures and does not write any file to `data/`.

## Summary

| Metric | Value | Interpretation |
|---|---:|---|
| alb2005_timing_geography_audit_rows | 234 | Timing/geography keyword rows scanned from ALB_2005 raw files. |
| alb2005_timing_geography_source_files_scanned | 44 | ALB_2005 .sav files scanned. |
| alb2005_timing_geography_read_failures | 0 | Raw files that could not be read by pyreadstat. |
| alb2005_interview_timing_candidate_rows | 0 | Rows with apparent interview/fieldwork timing wording requiring context. |
| alb2005_interview_timing_verified_rows | 0 | Verified household interview month/date rows available for climate linkage. |
| alb2005_rejected_non_interview_timing_rows | 65 | Rows rejected as birth, recall, duration, payment-period, or event-history timing. |
| alb2005_rejected_migration_history_rows | 18 | Rows rejected as migration or historical residence geography/timing. |
| alb2005_psu_cluster_key_rows | 44 | PSU/cluster-like key rows observed. |
| alb2005_coordinate_candidate_rows | 0 | GPS/latitude/longitude/coordinate candidate rows observed. |
| alb2005_partial_current_district_candidate_rows | 2 | Rows for current household district name/code candidates in filters.sav. |
| alb2005_partial_district_name_nonmissing_rows | 1899 | Nonmissing rows for P11_Q5A district name in filters.sav. |
| alb2005_partial_district_code_nonmissing_rows | 329 | Nonmissing rows for P11_Q5B district code in filters.sav. |
| alb2005_geography_verified_full_coverage_rows | 0 | Verified full-coverage geography rows ready for climate linkage. |
| alb2005_climate_linkage_ready_rows | 0 | Rows ready to support climate linkage input construction. |
| alb2005_timing_geography_current_decision | blocked_missing_interview_timing_partial_geography_no_gps | Current ALB_2005 timing/geography decision. |

## Priority Candidate Rows

| source_file | variable_name | variable_label | candidate_role | nonmissing_rows | household_base_match_rows | geography_timing_status |
|---|---|---|---|---|---|---|
| filters.sav | P0_Q00 | psu | psu_cluster_key | 1899 | 1899 | cluster_key_no_coordinate |
| filters.sav | P11_Q5A | district_name | partial_current_district_candidate | 1899 | 1899 | partial_household_geography_candidate |
| filters.sav | P11_Q5B | district code | partial_current_district_candidate | 329 | 1899 | partial_household_geography_candidate |
| filters_cl.sav | M0_Q00 | PSU | psu_cluster_key | 3840 | 3840 | cluster_key_no_coordinate |
| Modul_10_fertility_cl.sav | psu | PSU | psu_cluster_key | 573 | 520 | cluster_key_no_coordinate |
| Modul_11_check_form_food_cl.sav | psu | PSU | psu_cluster_key | 3840 | 3840 | cluster_key_no_coordinate |
| Modul_12A_non_food_expendituresa_cl.sav | psu | PSU | psu_cluster_key | 57600 | 3840 | cluster_key_no_coordinate |
| Modul_12B_non_food_expendituresb_cl.sav | psu | PSU | psu_cluster_key | 69120 | 3840 | cluster_key_no_coordinate |
| Modul_12C_non_food_expendituresc_cl.sav | psu | PSU | psu_cluster_key | 69120 | 3840 | cluster_key_no_coordinate |
| Modul_13A_dwellinga_cl.sav | psu | PSU | psu_cluster_key | 3840 | 3840 | cluster_key_no_coordinate |
| Modul_13B_dwellingb_cl.sav | M0_Q00 | PSU | psu_cluster_key | 3840 | 3840 | cluster_key_no_coordinate |
| Modul_13C_dwellingc1_cl.sav | M0_Q00 | PSU | psu_cluster_key | 96000 | 3840 | cluster_key_no_coordinate |
| Modul_13C_dwellingc2_cl.sav | psu | PSU | psu_cluster_key | 23913 | 3816 | cluster_key_no_coordinate |
| Modul_13C_dwellingc3_cl.sav | psu | PSU | psu_cluster_key | 30720 | 3840 | cluster_key_no_coordinate |
| Modul_14_social_assistance_cl.sav | psu | PSU | psu_cluster_key | 57600 | 3840 | cluster_key_no_coordinate |
| Modul_15_other_income_cl.sav | psu | PSU | psu_cluster_key | 57600 | 3840 | cluster_key_no_coordinate |
| Modul_16_social_capital_cl.sav | psu | PSU | psu_cluster_key | 3840 | 3840 | cluster_key_no_coordinate |
| Modul_17_id_agric_household_animals_cl.sav | psu | PSU | psu_cluster_key | 15230 | 1523 | cluster_key_no_coordinate |
| Modul_17_id_agric_household_cl.sav | psu | PSU | psu_cluster_key | 4631 | 1821 | cluster_key_no_coordinate |
| Modul_1A_household_rostera_cl.sav | psu | PSU | psu_cluster_key | 17302 | 3840 | cluster_key_no_coordinate |
| Modul_1B_household_rosterb_cl.sav | psu | PSU | psu_cluster_key | 17302 | 3840 | cluster_key_no_coordinate |
| Modul_2A_educationa_cl.sav | psu | PSU | psu_cluster_key | 17302 | 3840 | cluster_key_no_coordinate |
| Modul_2B_dwellingb_cl.sav | psu | PSU | psu_cluster_key | 3840 | 3840 | cluster_key_no_coordinate |
| Modul_2B_educationb_cl.sav | psu | PSU | psu_cluster_key | 17302 | 3840 | cluster_key_no_coordinate |
| Modul_2C_educationc_cl.sav | psu | PSU | psu_cluster_key | 13412 | 2580 | cluster_key_no_coordinate |
| Modul_3_communication_cl.sav | psu | PSU | psu_cluster_key | 17302 | 3840 | cluster_key_no_coordinate |
| Modul_3_communication_mobile_cl.sav | psu | PSU | psu_cluster_key | 14012 | 2994 | cluster_key_no_coordinate |
| Modul_4A_laboura_cl.sav | psu | PSU | psu_cluster_key | 17302 | 3840 | cluster_key_no_coordinate |
| Modul_4B_labourb_cl.sav | psu | PSU | psu_cluster_key | 6010 | 3170 | cluster_key_no_coordinate |
| Modul_4C_labourc_cl.sav | psu | PSU | psu_cluster_key | 5803 | 3170 | cluster_key_no_coordinate |
| Modul_4D_labourd_cl.sav | psu | PSU | psu_cluster_key | 1923 | 698 | cluster_key_no_coordinate |
| Modul_5_non_farm_business_cl.sav | psu | PSU | psu_cluster_key | 741 | 687 | cluster_key_no_coordinate |
| Modul_5_non_farm_business_first_cl.sav | M0_Q00 | PSU | psu_cluster_key | 3840 | 3840 | cluster_key_no_coordinate |
| Modul_6A_migrationa_cl.sav | psu | PSU | psu_cluster_key | 17302 | 3840 | cluster_key_no_coordinate |
| Modul_6B_migrationb2_cl.sav | psu | PSU | psu_cluster_key | 1415 | 1174 | cluster_key_no_coordinate |
| Modul_6B_migrationb_cl.sav | psu | PSU | psu_cluster_key | 17302 | 3840 | cluster_key_no_coordinate |
| Modul_6C_migrationc_cl.sav | psu | PSU | psu_cluster_key | 4714 | 1745 | cluster_key_no_coordinate |
| Modul_6D_migrationd2_cl.sav | psu | PSU | psu_cluster_key | 27888 | 3736 | cluster_key_no_coordinate |
| Modul_6D_migrationd_cl.sav | psu | PSU | psu_cluster_key | 3840 | 3840 | cluster_key_no_coordinate |
| Modul_6E_migratione_cl.sav | psu | PSU | psu_cluster_key | 57600 | 3840 | cluster_key_no_coordinate |

## Rejected Timing/Geography Keyword Rows

| source_file | variable_name | variable_label | candidate_role | nonmissing_rows | geography_timing_status |
|---|---|---|---|---|---|
| filters.sav | P8_Q01 | extension visit | not_survey_timing_visit_count | 1899 | rejected_not_interview_timing |
| filters.sav | P8_Q03 | visit number | not_survey_timing_visit_count | 589 | rejected_not_interview_timing |
| filters_cl.sav | M10_Q01 | Woman in HH Given birth in last 3 years | not_survey_timing_birth_date | 3840 | rejected_not_interview_timing |
| Modul_10_fertility_cl.sav | m10_q5d | Date of Birth - Day | not_survey_timing_birth_date | 573 | rejected_not_interview_timing |
| Modul_10_fertility_cl.sav | m10_q5m | Date of Birth - Month | not_survey_timing_birth_date | 573 | rejected_not_interview_timing |
| Modul_10_fertility_cl.sav | m10_q5y | Date of Birth - Year | not_survey_timing_birth_date | 573 | rejected_not_interview_timing |
| Modul_10_fertility_cl.sav | m10_q09 | Period of 1st visit | not_survey_timing_visit_count | 551 | rejected_not_interview_timing |
| Modul_10_fertility_cl.sav | m10_q16 | Months breastfed | not_survey_timing_duration_or_payment_period | 232 | rejected_not_interview_timing |
| Modul_10_fertility_cl.sav | m10_q18 | Gave birth in last 3 years | not_survey_timing_birth_date | 573 | rejected_not_interview_timing |
| Modul_12A_non_food_expendituresa_cl.sav | m12a_q02 | Bought item in past 30 days | not_survey_timing_recall_period | 57600 | rejected_not_interview_timing |
| Modul_12A_non_food_expendituresa_cl.sav | m12a_q03 | Amount spent in past 30 days | not_survey_timing_recall_period | 18503 | rejected_not_interview_timing |
| Modul_12B_non_food_expendituresb_cl.sav | m12b_q02 | Bought any in last 6 months | not_survey_timing_recall_period | 69120 | rejected_not_interview_timing |
| Modul_12C_non_food_expendituresc_cl.sav | m12c_q02 | Bought item in past 12 months | not_survey_timing_recall_period | 69120 | rejected_not_interview_timing |
| Modul_12C_non_food_expendituresc_cl.sav | m12c_q03 | Amount spent in past 12 months | not_survey_timing_recall_period | 11420 | rejected_not_interview_timing |
| Modul_13A_dwellinga_cl.sav | v11 | Monthly Rent | not_survey_timing_duration_or_payment_period | 165 | rejected_not_interview_timing |
| Modul_13A_dwellinga_cl.sav | m13a_q19 | Month inhabit this dwelling | not_survey_timing_event_history | 62 | rejected_not_interview_timing |
| Modul_13A_dwellinga_cl.sav | v15 | Year inhabit this dwelling | not_survey_timing_event_history | 62 | rejected_not_interview_timing |
| Modul_13A_dwellinga_cl.sav | m13a_q32 | Months of process | not_survey_timing_duration_or_payment_period | 880 | rejected_not_interview_timing |
| Modul_13B_dwellingb_cl.sav | M13B_Q22 | Months covered in payment | not_survey_timing_duration_or_payment_period | 3294 | rejected_not_interview_timing |
| Modul_13B_dwellingb_cl.sav | M13B_Q35_duplicated1 | Months covered in payment | not_survey_timing_duration_or_payment_period | 0 | rejected_not_interview_timing |
| Modul_14_social_assistance_cl.sav | m14_q4m | Month started receiving assistance | not_survey_timing_event_history | 2692 | rejected_not_interview_timing |
| Modul_14_social_assistance_cl.sav | m14_q4y | Year started receiving assistance | not_survey_timing_event_history | 2692 | rejected_not_interview_timing |
| Modul_14_social_assistance_cl.sav | m14_q06 | Number of months | not_survey_timing_duration_or_payment_period | 2692 | rejected_not_interview_timing |
| Modul_14_social_assistance_cl.sav | m14_q12m | Month started receiving assistance | not_survey_timing_event_history | 514 | rejected_not_interview_timing |
| Modul_14_social_assistance_cl.sav | m14_q12y | Year started receiving assistance | not_survey_timing_event_history | 514 | rejected_not_interview_timing |
| Modul_14_social_assistance_cl.sav | m14_q14 | Number of months | not_survey_timing_duration_or_payment_period | 514 | rejected_not_interview_timing |
| Modul_14_social_assistance_cl.sav | m14_q20m | Month started receiving assistance | not_survey_timing_event_history | 9 | rejected_not_interview_timing |
| Modul_14_social_assistance_cl.sav | m14_q20y | Year started receiving assistance | not_survey_timing_event_history | 9 | rejected_not_interview_timing |
| Modul_14_social_assistance_cl.sav | m14_q22 | Number of months | not_survey_timing_duration_or_payment_period | 9 | rejected_not_interview_timing |
| Modul_1A_household_rostera_cl.sav | m1a_q4d | Date of Birth - Day | not_survey_timing_birth_date | 17302 | rejected_not_interview_timing |
| Modul_1A_household_rostera_cl.sav | m1a_q4m | Date of Birth - Month | not_survey_timing_birth_date | 17302 | rejected_not_interview_timing |
| Modul_1A_household_rostera_cl.sav | m1a_q4y | Date of Birth - Year | not_survey_timing_birth_date | 17302 | rejected_not_interview_timing |
| Modul_2A_educationa_cl.sav | m2a_q05 | Amount per month | not_survey_timing_duration_or_payment_period | 324 | rejected_not_interview_timing |
| Modul_2B_dwellingb_cl.sav | m13b_q22 | Months covered in payment | not_survey_timing_duration_or_payment_period | 3294 | rejected_not_interview_timing |
| Modul_2B_dwellingb_cl.sav | v15 | Months covered in payment | not_survey_timing_duration_or_payment_period | 1151 | rejected_not_interview_timing |
| Modul_3_communication_cl.sav | m3_q06 | Used internet past month | not_survey_timing_recall_period | 708 | rejected_not_interview_timing |
| Modul_3_communication_mobile_cl.sav | m3_q10 | Year of acquisition | not_survey_timing_event_history | 4572 | rejected_not_interview_timing |
| Modul_4B_labourb_cl.sav | m4b_q04 | Number of weeks worked in past 12 months | not_survey_timing_recall_period | 6010 | rejected_not_interview_timing |
| Modul_4C_labourc_cl.sav | m4c_q21m | Month started job | not_survey_timing_event_history | 5803 | rejected_not_interview_timing |
| Modul_4C_labourc_cl.sav | m4c_q21y | Year started job | not_survey_timing_event_history | 5803 | rejected_not_interview_timing |

## Interpretation

- No verified household interview month/date variable was found, so pre-interview 1, 3, 6, or 12 month climate windows remain blocked.
- `P11_Q5B` in `filters.sav` is the main current district-code candidate, but it is partial coverage only and has no GPS or coordinate information.
- PSU variables are merge/cluster keys, not climate locations, unless an official PSU-coordinate or admin crosswalk is obtained.
- Many date/month/year hits are birth dates, migration history, event history, illness durations, payment periods, or recall windows. They cannot substitute for survey fieldwork timing.
- ALB_2005 remains unusable for climate linkage until fieldwork timing and valid geography are documented.

## Machine-Readable Outputs

- `temp/alb2005_timing_geography_exhaustive_audit.csv`
- `result/alb2005_timing_geography_exhaustive_summary.csv`
