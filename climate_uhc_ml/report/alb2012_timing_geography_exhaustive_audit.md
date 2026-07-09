# ALB_2012 Timing And Geography Exhaustive Audit

Status: raw-value timing/geography audit only. This report scans ALB_2012 raw SPSS files for timing and geography keyword hits and classifies whether they can support climate linkage. It does not construct climate exposures and does not write any file to `data/`.

## Summary

| Metric | Value | Interpretation |
|---|---:|---|
| alb2012_timing_geography_audit_rows | 212 | Timing/geography keyword rows scanned from ALB_2012 raw files. |
| alb2012_timing_geography_source_files_scanned | 34 | ALB_2012 .sav files scanned. |
| alb2012_timing_geography_read_failures | 0 | Raw files that could not be read by pyreadstat. |
| alb2012_interview_timing_candidate_rows | 0 | Rows with apparent interview/fieldwork timing wording requiring context. |
| alb2012_interview_timing_verified_rows | 0 | Verified household interview month/date rows available for climate linkage. |
| alb2012_rejected_non_interview_timing_rows | 54 | Rows rejected as birth, recall, duration, payment-period, or event-history timing. |
| alb2012_rejected_migration_history_rows | 15 | Rows rejected as migration or historical residence geography/timing. |
| alb2012_context_review_geography_timing_rows | 106 | Rows with timing/geography keywords requiring context but not verified for climate linkage. |
| alb2012_psu_cluster_key_rows | 34 | PSU/cluster-like key rows observed. |
| alb2012_coordinate_candidate_rows | 0 | GPS/latitude/longitude/coordinate candidate rows observed. |
| alb2012_coarse_full_coverage_geography_candidate_rows | 3 | Rows for full-coverage coarse geography/design fields in poverty.sav. |
| alb2012_coarse_geography_household_rows | 6671 | Maximum nonmissing household rows across coarse poverty.sav geography/design fields. |
| alb2012_geography_verified_full_coverage_rows | 0 | Verified admin/GPS geography rows ready for climate linkage. |
| alb2012_climate_linkage_ready_rows | 0 | Rows ready to support climate linkage input construction. |
| alb2012_timing_geography_current_decision | blocked_missing_interview_timing_coarse_prefecture_region_no_gps | Current ALB_2012 timing/geography decision. |

## Priority Candidate Rows

| source_file | variable_name | variable_label | candidate_role | nonmissing_rows | household_base_match_rows | geography_timing_status |
|---|---|---|---|---|---|---|
| Modul_10_Fertility.sav | M0_Q00 | PSU | psu_cluster_key | 6754 | 0 | cluster_key_no_coordinate |
| Modul_12A_Purchases_past30_days.sav | psu | PSU | psu_cluster_key | 100065 | 6671 | cluster_key_no_coordinate |
| Modul_12B_Purchases_past6_months.sav | psu | PSU | psu_cluster_key | 120078 | 6671 | cluster_key_no_coordinate |
| Modul_12C_Purchases_past12_months.sav | psu | PSU | psu_cluster_key | 120078 | 6671 | cluster_key_no_coordinate |
| Modul_13A_Description_of_Dwelling.sav | psu | PSU | psu_cluster_key | 6671 | 6671 | cluster_key_no_coordinate |
| Modul_13B_Utilities.sav | psu | PSU | psu_cluster_key | 6671 | 6671 | cluster_key_no_coordinate |
| Modul_13C1_Household_Durables.sav | psu | PSU | psu_cluster_key | 193459 | 6671 | cluster_key_no_coordinate |
| Modul_13C2_Household_Durables.sav | psu | PSU | psu_cluster_key | 61289 | 6663 | cluster_key_no_coordinate |
| Modul_14_Social_Protection.sav | psu | PSU | psu_cluster_key | 120078 | 6671 | cluster_key_no_coordinate |
| Modul_15_Other_Income.sav | psu | PSU | psu_cluster_key | 106736 | 6671 | cluster_key_no_coordinate |
| Modul_16A_Social_Participation.sav | psu | PSU | psu_cluster_key | 6671 | 6671 | cluster_key_no_coordinate |
| Modul_16B_Social_Capital.sav | psu | PSU | psu_cluster_key | 6671 | 6671 | cluster_key_no_coordinate |
| Modul_17_Identification_of_Agriculture_Hh_Q1-2.sav | psu | PSU | psu_cluster_key | 6671 | 6671 | cluster_key_no_coordinate |
| Modul_17_Identification_of_Agriculture_Hh_Q10-11.sav | psu | PSU | psu_cluster_key | 6671 | 6671 | cluster_key_no_coordinate |
| Modul_17_Identification_of_Agriculture_Hh_Q3-9.sav | psu | PSU | psu_cluster_key | 4661 | 3028 | cluster_key_no_coordinate |
| Modul_1A_householdroster.sav | psu | PSU | psu_cluster_key | 25335 | 6671 | cluster_key_no_coordinate |
| Modul_1B_householdroster.sav | psu | PSU | psu_cluster_key | 25335 | 6671 | cluster_key_no_coordinate |
| Modul_2A_education.sav | psu | PSU | psu_cluster_key | 1123 | 992 | cluster_key_no_coordinate |
| Modul_2B_education.sav | psu | PSU | psu_cluster_key | 23740 | 6671 | cluster_key_no_coordinate |
| Modul_2C_education.sav | PSU | PSU | psu_cluster_key | 4212 | 2612 | cluster_key_no_coordinate |
| Modul_3_Communication_Mobile_Phones_1.sav | psu | PSU | psu_cluster_key | 24763 | 6671 | cluster_key_no_coordinate |
| Modul_3_internet.sav | psu | PSU | psu_cluster_key | 25335 | 6671 | cluster_key_no_coordinate |
| Modul_4A_labor.sav | psu | PSU | psu_cluster_key | 25335 | 6671 | cluster_key_no_coordinate |
| Modul_4B_labor.sav | psu | PSU | psu_cluster_key | 25335 | 6671 | cluster_key_no_coordinate |
| Modul_5_Non-Farm_Enterprises.sav | psu | PSU | psu_cluster_key | 6680 | 6670 | cluster_key_no_coordinate |
| Modul_6A_Internal_Migration_of_household_Members.sav | psu | PSU | psu_cluster_key | 20435 | 6671 | cluster_key_no_coordinate |
| Modul_6B_International_Migration_of_household_Members.sav | psu | PSU | psu_cluster_key | 20435 | 6671 | cluster_key_no_coordinate |
| Modul_6C_Sons_and_Doughter_living_away.sav | psu | PSU | psu_cluster_key | 3487 | 1727 | cluster_key_no_coordinate |
| Modul_6D_Shocks to the household.sav | psu | PSU | psu_cluster_key | 60054 | 6671 | cluster_key_no_coordinate |
| Modul_7_Subjective_Poverty.sav | psu | PSU | psu_cluster_key | 6671 | 6671 | cluster_key_no_coordinate |
| modul_9A_health.sav | psu | PSU | psu_cluster_key | 25335 | 6671 | cluster_key_no_coordinate |
| Modul_9B_Access_to_Health_Care.sav | psu | PSU | psu_cluster_key | 6671 | 6671 | cluster_key_no_coordinate |
| poverty.sav | psu | PSU | psu_cluster_key | 6671 | 6671 | cluster_key_no_coordinate |
| poverty.sav | prefecture | Prefecture | coarse_full_coverage_geography_candidate | 6671 | 6671 | coarse_geography_candidate_not_admin_or_gps |
| poverty.sav | urban | Urban=1, rural=2 | coarse_full_coverage_geography_candidate | 6671 | 6671 | coarse_geography_candidate_not_admin_or_gps |
| poverty.sav | region | Regions | coarse_full_coverage_geography_candidate | 6671 | 6671 | coarse_geography_candidate_not_admin_or_gps |
| Weight_lsms2012_retro.sav | psu |  | psu_cluster_key | 6671 | 6671 | cluster_key_no_coordinate |

## Rejected Timing/Geography Keyword Rows

| source_file | variable_name | variable_label | candidate_role | nonmissing_rows | geography_timing_status |
|---|---|---|---|---|---|
| Modul_10_Fertility.sav | M10_Q05 | Day of birth of child | not_survey_timing_birth_date | 804 | rejected_not_interview_timing |
| Modul_10_Fertility.sav | M10_Q5M | Month of birth | not_survey_timing_birth_date | 804 | rejected_not_interview_timing |
| Modul_10_Fertility.sav | M10_Q5Y | Year of birth | not_survey_timing_birth_date | 805 | rejected_not_interview_timing |
| Modul_10_Fertility.sav | M10_Q09 | Period of first prenatal visit | not_survey_timing_visit_count | 779 | rejected_not_interview_timing |
| Modul_10_Fertility.sav | M10_Q18 | Gave birth in last 3 years | not_survey_timing_birth_date | 805 | rejected_not_interview_timing |
| Modul_13A_Description_of_Dwelling.sav | m13a_q15 | Monthly rent | not_survey_timing_duration_or_payment_period | 260 | rejected_not_interview_timing |
| Modul_13A_Description_of_Dwelling.sav | m13a_q17 | Monthly payment for the building | not_survey_timing_duration_or_payment_period | 26 | rejected_not_interview_timing |
| Modul_13A_Description_of_Dwelling.sav | m13a_q18A | Potential monthly rent | not_survey_timing_duration_or_payment_period | 6243 | rejected_not_interview_timing |
| Modul_13B_Utilities.sav | m13b_q20 | Paid bill in past 12 months | not_survey_timing_recall_period | 6663 | rejected_not_interview_timing |
| Modul_13B_Utilities.sav | m13b_q22 | Number of months covered | not_survey_timing_duration_or_payment_period | 5741 | rejected_not_interview_timing |
| Modul_13B_Utilities.sav | m13b_q35 | Months covered | not_survey_timing_duration_or_payment_period | 1495 | rejected_not_interview_timing |
| Modul_14_Social_Protection.sav | M14_Q23 | Number of months | not_survey_timing_duration_or_payment_period | 13 | rejected_not_interview_timing |
| Modul_1A_householdroster.sav | m1a_q04 | Date of Birth | not_survey_timing_birth_date | 25335 | rejected_not_interview_timing |
| Modul_2A_education.sav | m2a_Q05 | Amount per month | not_survey_timing_duration_or_payment_period | 443 | rejected_not_interview_timing |
| Modul_2B_education.sav | M2B_Q08 | Enrollment in thisacademic year | not_survey_timing_event_history | 22808 | rejected_not_interview_timing |
| Modul_2B_education.sav | M2B_Q14 | Enroll in past academic year | not_survey_timing_event_history | 22808 | rejected_not_interview_timing |
| Modul_2B_education.sav | M2B_Q15 | Attend school in past academic year | not_survey_timing_event_history | 5640 | rejected_not_interview_timing |
| Modul_2B_education.sav | M2B_Q16 | Reason for not attending school in past academic year | not_survey_timing_event_history | 36 | rejected_not_interview_timing |
| Modul_2B_education.sav | M2B_Q17 | Reason for not enrolling school in past academic year | not_survey_timing_event_history | 17168 | rejected_not_interview_timing |
| Modul_2B_education.sav | M2B_Q21 | Grade enrolled in past academic year: Level | not_survey_timing_event_history | 5604 | rejected_not_interview_timing |
| Modul_2B_education.sav | M2B_Q22 | Grade enrolled in past academic year: Grade | not_survey_timing_event_history | 5604 | rejected_not_interview_timing |
| Modul_2B_education.sav | M2B_Q32 | Buy suplementar text books during this academic year | not_survey_timing_event_history | 5590 | rejected_not_interview_timing |
| Modul_2B_education.sav | M2B_Q33 | Cost of past academic year - School fees and tuition | not_survey_timing_event_history | 5532 | rejected_not_interview_timing |
| Modul_2B_education.sav | M2B_Q34 | Cost of past academic year - Uniforms | not_survey_timing_event_history | 5532 | rejected_not_interview_timing |
| Modul_2B_education.sav | M2B_Q35 | Cost of past academic year - Authorized text books | not_survey_timing_event_history | 5532 | rejected_not_interview_timing |
| Modul_2B_education.sav | M2B_Q36 | Cost of past academic year - Suplementary text books | not_survey_timing_event_history | 5530 | rejected_not_interview_timing |
| Modul_2B_education.sav | M2B_Q37 | Cost of past academic year - Other educational materials | not_survey_timing_event_history | 5531 | rejected_not_interview_timing |
| Modul_2B_education.sav | M2B_Q38 | Cost of past academic year - Meals and/or lodging | not_survey_timing_event_history | 5532 | rejected_not_interview_timing |
| Modul_2B_education.sav | M2B_Q39 | Cost of past academic year - School excursions | not_survey_timing_event_history | 5531 | rejected_not_interview_timing |
| Modul_2B_education.sav | M2B_Q40 | Cost of past academic year - Other | not_survey_timing_event_history | 5532 | rejected_not_interview_timing |
| Modul_2B_education.sav | M2B_Q41 | Cost of past academic year - Total | not_survey_timing_event_history | 5604 | rejected_not_interview_timing |
| Modul_4A_labor.sav | M4A_Q11 | Status began 12 months ago | not_survey_timing_event_history | 10151 | rejected_not_interview_timing |
| Modul_4A_labor.sav | M4A_Q13A | Time looking for a job - Years | not_survey_timing_event_history | 1990 | rejected_not_interview_timing |
| Modul_4A_labor.sav | M4A_Q16 | Status began 12 months ago | not_survey_timing_event_history | 4200 | rejected_not_interview_timing |
| Modul_4B_labor.sav | M4B_Q20A | Job start time - Month | not_survey_timing_event_history | 5669 | rejected_not_interview_timing |
| Modul_4B_labor.sav | M4B_Q20B | Job start time - Year | not_survey_timing_event_history | 6078 | rejected_not_interview_timing |
| Modul_4B_labor.sav | M4B_Q31 | Is month of start job after June 2011 | not_survey_timing_event_history | 147 | rejected_not_interview_timing |
| Modul_5_Non-Farm_Enterprises.sav | M5_Q18 | Business operate during past month | not_survey_timing_recall_period | 690 | rejected_not_interview_timing |
| Modul_5_Non-Farm_Enterprises.sav | M5_Q25 | Past month | not_survey_timing_recall_period | 612 | rejected_not_interview_timing |
| Modul_5_Non-Farm_Enterprises.sav | M5_Q26 | Profit of past month | not_survey_timing_recall_period | 488 | rejected_not_interview_timing |
| Modul_5_Non-Farm_Enterprises.sav | M5_Q27 | Lost past month | not_survey_timing_recall_period | 11 | rejected_not_interview_timing |
| Modul_6A_Internal_Migration_of_household_Members.sav | M6A_Q08 | Where was living in 1990: District/State | not_current_location_migration_history | 16839 | rejected_not_current_household_geography_or_timing |
| Modul_6A_Internal_Migration_of_household_Members.sav | M6A_Q10 | Where was living in 1990: Municipality/Commune | not_current_location_migration_history | 16824 | rejected_not_current_household_geography_or_timing |
| Modul_6B_International_Migration_of_household_Members.sav | M6B_Q01 | Migrate abroat for at least 3 months | not_current_location_migration_history | 20435 | rejected_not_current_household_geography_or_timing |
| Modul_6B_International_Migration_of_household_Members.sav | M6B_Q02M | Month of migration | not_current_location_migration_history | 1171 | rejected_not_current_household_geography_or_timing |
| Modul_6B_International_Migration_of_household_Members.sav | M6B_Q02Y | Year of migration | not_current_location_migration_history | 1171 | rejected_not_current_household_geography_or_timing |
| Modul_6B_International_Migration_of_household_Members.sav | M6B_Q04Y | Years away in last migration | not_current_location_migration_history | 1171 | rejected_not_current_household_geography_or_timing |
| Modul_6B_International_Migration_of_household_Members.sav | M6B_Q04M | Months away in last migration | not_current_location_migration_history | 1171 | rejected_not_current_household_geography_or_timing |
| Modul_6B_International_Migration_of_household_Members.sav | M6B_Q19 | Planning to migrate within next year | not_current_location_migration_history | 856 | rejected_not_current_household_geography_or_timing |
| Modul_6B_International_Migration_of_household_Members.sav | M6B_Q21 | Migrate abroad after 15 years | not_current_location_migration_history | 1171 | rejected_not_current_household_geography_or_timing |

## Interpretation

- No verified household interview month/date variable was found, so pre-interview 1, 3, 6, or 12 month climate windows remain blocked.
- `prefecture`, `region`, and `urban` in `poverty.sav` have broad household coverage but are coarse survey geography/design fields, not verified admin/GPS climate-linkage locations.
- No GPS, latitude, longitude, or coordinate candidates were found in the public ALB_2012 SPSS files.
- PSU variables are merge/cluster keys, not climate locations, unless an official PSU-coordinate or admin crosswalk is obtained.
- Many date/month/year hits are birth dates, migration history, event history, illness durations, payment periods, or recall windows. They cannot substitute for survey fieldwork timing.
- ALB_2012 remains unusable for climate linkage until fieldwork timing and valid geography are documented.

## Machine-Readable Outputs

- `temp/alb2012_timing_geography_exhaustive_audit.csv`
- `result/alb2012_timing_geography_exhaustive_summary.csv`
