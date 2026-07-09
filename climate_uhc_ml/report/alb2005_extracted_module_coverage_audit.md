# ALB_2005 Extracted Module Coverage Audit

Status: fail-closed extracted-module coverage audit. This compares the ALB_2005 public DDI/schema module list with both the local archive manifest and the extracted local `.sav` files under `temp/raw_extracted/lsms2005en_1e7f1965c4a5/lsms2005en/Data_2005/`.

## Summary

| Metric | Value | Interpretation |
|---|---:|---|
| alb2005_extracted_module_coverage_ddi_module_rows | 68 | DDI/schema modules checked against the extracted ALB_2005 package. |
| alb2005_archive_member_rows | 61 | Members listed directly from the local ALB_2005 RAR archive. |
| alb2005_archive_sav_member_rows | 44 | SPSS .sav members listed directly from the local ALB_2005 RAR archive. |
| alb2005_archive_questionnaire_member_rows | 2 | Questionnaire workbook members listed directly from the local ALB_2005 RAR archive. |
| alb2005_archive_ddi_module_present_rows | 41 | DDI/schema modules present in the local archive manifest. |
| alb2005_archive_ddi_module_absent_rows | 27 | DDI/schema modules absent from the local archive manifest. |
| alb2005_archive_critical_module_absent_rows | 8 | Critical timing/food-diary/design DDI modules absent from the local archive manifest. |
| alb2005_archive_listing_status | tar_listing_available | Whether the local ALB_2005 archive member list was readable. |
| alb2005_extracted_module_coverage_present_rows | 41 | DDI modules with a normalized extracted file match. |
| alb2005_extracted_module_coverage_missing_rows | 27 | DDI modules missing from the extracted ALB_2005 package. |
| alb2005_extracted_module_coverage_extracted_file_rows | 44 | Extracted .sav files under the ALB_2005 Data_2005 folder. |
| alb2005_extracted_module_coverage_extra_extracted_rows | 2 | Extracted .sav files not matched to a normalized DDI file name. |
| alb2005_extracted_module_coverage_bookmetadata_missing_rows | 1 | Whether DDI `bookmetadata_cl` is missing from the extracted package. |
| alb2005_extracted_module_coverage_food_diary_missing_rows | 5 | Missing DDI food-diary modules relevant to consumption component reconstruction. |
| alb2005_extracted_module_coverage_critical_missing_rows | 8 | Missing timing/food-diary/design modules that require follow-up before recipe promotion. |
| alb2005_extracted_module_coverage_coordinate_metadata_variable_rows | 0 | Coordinate/GPS variable candidates found in the ALB_2005 metadata variable catalog. |
| alb2005_extracted_module_coverage_coordinate_extracted_file_rows | 0 | Extracted files whose names suggest coordinate/GPS content. |
| alb2005_extracted_module_coverage_harmonized_ready_rows | 0 | Rows promoted to harmonized analytical data by this audit; intentionally zero. |
| alb2005_extracted_module_coverage_household_timing_ready_rows | 0 | Rows promoted to verified household timing by this audit; intentionally zero. |
| alb2005_extracted_module_coverage_climate_linkage_ready_rows | 0 | Rows ready for climate linkage after this audit; intentionally zero. |
| alb2005_extracted_module_coverage_current_decision | blocked_extracted_package_missing_bookmetadata_and_coordinate_values | Current fail-closed decision for ALB_2005 extracted module coverage. |

## Critical Missing Modules

| fid | ddi_file_name | module_role | expected_for | coverage_status | archive_coverage_status | blocking_implication |
|---|---|---|---|---|---|---|
| F92 | bookbread_cl | food_diary_consumption | consumption denominator reconstruction review | ddi_module_missing_from_extracted_package | absent_from_local_archive_manifest | Food diary source module is absent locally, limiting component-level consumption reconstruction from r... |
| F93 | bookchecklist_cl | food_diary_consumption | consumption denominator reconstruction review | ddi_module_missing_from_extracted_package | absent_from_local_archive_manifest | Food diary source module is absent locally, limiting component-level consumption reconstruction from r... |
| F94 | bookdaily_cl | food_diary_consumption | consumption denominator reconstruction review | ddi_module_missing_from_extracted_package | absent_from_local_archive_manifest | Food diary source module is absent locally, limiting component-level consumption reconstruction from r... |
| F95 | bookfoodeaten_cl | food_diary_consumption | consumption denominator reconstruction review | ddi_module_missing_from_extracted_package | absent_from_local_archive_manifest | Food diary source module is absent locally, limiting component-level consumption reconstruction from r... |
| F96 | bookmetadata_cl | diary_timing | household timing candidate merge review | ddi_module_missing_from_extracted_package | absent_from_local_archive_manifest | Diary beginning/finishing date candidates are in public metadata but the raw bookmetadata file is abse... |
| F97 | booknonpurchased_cl | food_diary_consumption | consumption denominator reconstruction review | ddi_module_missing_from_extracted_package | absent_from_local_archive_manifest | Food diary source module is absent locally, limiting component-level consumption reconstruction from r... |
| F141 | weights_cl | survey_design | survey design/weight review | ddi_module_missing_from_extracted_package | absent_from_local_archive_manifest | DDI-listed design/weight module is absent under this exact module name; alternate local weight files r... |
| F142 | weights_psu | survey_design | survey design/PSU review | ddi_module_missing_from_extracted_package | absent_from_local_archive_manifest | DDI-listed design/weight module is absent under this exact module name; alternate local weight files r... |

## Missing Module Preview

| fid | ddi_file_name | module_role | ddi_cases | ddi_variable_count | coverage_status | archive_coverage_status | required_next_evidence |
|---|---|---|---|---|---|---|---|
| F75 | agriculture_hhlevel | other | 1849 | 225 | ddi_module_missing_from_extracted_package | absent_from_local_archive_manifest | Obtain the module or document exclusion from analytical recipes. |
| F77 | identification | other | 1899 | 15 | ddi_module_missing_from_extracted_package | absent_from_local_archive_manifest | Obtain the module or document exclusion from analytical recipes. |
| F78 | part1_roster_a | household_frame | 5456 | 23 | ddi_module_missing_from_extracted_package | absent_from_local_archive_manifest | Obtain the module or document exclusion from analytical recipes. |
| F79 | part1_roster_b | household_frame | 210 | 23 | ddi_module_missing_from_extracted_package | absent_from_local_archive_manifest | Obtain the module or document exclusion from analytical recipes. |
| F80 | part2_roster | household_frame | 39 | 18 | ddi_module_missing_from_extracted_package | absent_from_local_archive_manifest | Obtain the module or document exclusion from analytical recipes. |
| F81 | part3_roster | household_frame | 49720 | 16 | ddi_module_missing_from_extracted_package | absent_from_local_archive_manifest | Obtain the module or document exclusion from analytical recipes. |
| F82 | part4_roster | household_frame | 28587 | 18 | ddi_module_missing_from_extracted_package | absent_from_local_archive_manifest | Obtain the module or document exclusion from analytical recipes. |
| F83 | part5_roster | household_frame | 31634 | 13 | ddi_module_missing_from_extracted_package | absent_from_local_archive_manifest | Obtain the module or document exclusion from analytical recipes. |
| F84 | part6_roster | household_frame | 39876 | 16 | ddi_module_missing_from_extracted_package | absent_from_local_archive_manifest | Obtain the module or document exclusion from analytical recipes. |
| F85 | part7_roster | household_frame | 36101 | 8 | ddi_module_missing_from_extracted_package | absent_from_local_archive_manifest | Obtain the module or document exclusion from analytical recipes. |
| F86 | part8_roster_a | household_frame | 5009 | 6 | ddi_module_missing_from_extracted_package | absent_from_local_archive_manifest | Obtain the module or document exclusion from analytical recipes. |
| F87 | part8_roster_b | household_frame | 5009 | 6 | ddi_module_missing_from_extracted_package | absent_from_local_archive_manifest | Obtain the module or document exclusion from analytical recipes. |
| F88 | part9_roster_a | household_frame | 13293 | 8 | ddi_module_missing_from_extracted_package | absent_from_local_archive_manifest | Obtain the module or document exclusion from analytical recipes. |
| F89 | part9_roster_b | household_frame | 39879 | 7 | ddi_module_missing_from_extracted_package | absent_from_local_archive_manifest | Obtain the module or document exclusion from analytical recipes. |
| F90 | part10_roster | household_frame | 11369 | 9 | ddi_module_missing_from_extracted_package | absent_from_local_archive_manifest | Obtain the module or document exclusion from analytical recipes. |
| F91 | part11_roster | household_frame | 483 | 8 | ddi_module_missing_from_extracted_package | absent_from_local_archive_manifest | Obtain the module or document exclusion from analytical recipes. |
| F92 | bookbread_cl | food_diary_consumption | 3840 | 8 | ddi_module_missing_from_extracted_package | absent_from_local_archive_manifest | Obtain the missing food diary module or document why the survey-provided aggregate can be used without... |
| F93 | bookchecklist_cl | food_diary_consumption | 53760 | 12 | ddi_module_missing_from_extracted_package | absent_from_local_archive_manifest | Obtain the missing food diary module or document why the survey-provided aggregate can be used without... |
| F94 | bookdaily_cl | food_diary_consumption | 196964 | 13 | ddi_module_missing_from_extracted_package | absent_from_local_archive_manifest | Obtain the missing food diary module or document why the survey-provided aggregate can be used without... |
| F95 | bookfoodeaten_cl | food_diary_consumption | 19744 | 10 | ddi_module_missing_from_extracted_package | absent_from_local_archive_manifest | Obtain the missing food diary module or document why the survey-provided aggregate can be used without... |
| F96 | bookmetadata_cl | diary_timing | 3840 | 18 | ddi_module_missing_from_extracted_package | absent_from_local_archive_manifest | Obtain the raw bookmetadata_cl file or official equivalent, then verify hhid/PSU merge coverage and di... |
| F97 | booknonpurchased_cl | food_diary_consumption | 57245 | 13 | ddi_module_missing_from_extracted_package | absent_from_local_archive_manifest | Obtain the missing food diary module or document why the survey-provided aggregate can be used without... |
| F98 | community_all | community_context | 458 | 424 | ddi_module_missing_from_extracted_package | absent_from_local_archive_manifest | Obtain the module or document exclusion from analytical recipes. |
| F99 | community_dups | other | 49 | 424 | ddi_module_missing_from_extracted_package | absent_from_local_archive_manifest | Obtain the module or document exclusion from analytical recipes. |
| F119 | identification_cl | other | 3840 | 23 | ddi_module_missing_from_extracted_package | absent_from_local_archive_manifest | Obtain the module or document exclusion from analytical recipes. |
| ... | 2 additional rows omitted from report preview |  |  |  |  |  |  |

## Extra Extracted Files

| extracted_file | normalized_name | bytes | coverage_status | notes |
|---|---|---|---|---|
| Modul_8_section2_cl.sav | section2_cl | 92395 | extracted_file_not_matched_to_ddi_schema_file_name | Useful local raw file but not matched by normalized DDI file name; review before using as official sub... |
| Weight_retro_2005.sav | weight_retro_2005 | 8110 | extracted_file_not_matched_to_ddi_schema_file_name | Useful local raw file but not matched by normalized DDI file name; review before using as official sub... |

## Archive File Members

| member_path | member_ext | normalized_name | archive_member_type |
|---|---|---|---|
| lsms2005en/Data_2005/filters.sav | .sav | filters | candidate_data_or_document_file |
| lsms2005en/Data_2005/filters_cl.sav | .sav | filters_cl | candidate_data_or_document_file |
| lsms2005en/Data_2005/Modul_10_fertility_cl.sav | .sav | fertility_cl | candidate_data_or_document_file |
| lsms2005en/Data_2005/Modul_11_check_form_food_cl.sav | .sav | check_form_food_cl | candidate_data_or_document_file |
| lsms2005en/Data_2005/Modul_12A_non_food_expendituresa_cl.sav | .sav | non_food_expendituresa_cl | candidate_data_or_document_file |
| lsms2005en/Data_2005/Modul_12B_non_food_expendituresb_cl.sav | .sav | non_food_expendituresb_cl | candidate_data_or_document_file |
| lsms2005en/Data_2005/Modul_12C_non_food_expendituresc_cl.sav | .sav | non_food_expendituresc_cl | candidate_data_or_document_file |
| lsms2005en/Data_2005/Modul_13A_dwellinga_cl.sav | .sav | dwellinga_cl | candidate_data_or_document_file |
| lsms2005en/Data_2005/Modul_13B_dwellingb_cl.sav | .sav | dwellingb_cl | candidate_data_or_document_file |
| lsms2005en/Data_2005/Modul_13C_dwellingc1_cl.sav | .sav | dwellingc1_cl | candidate_data_or_document_file |
| lsms2005en/Data_2005/Modul_13C_dwellingc2_cl.sav | .sav | dwellingc2_cl | candidate_data_or_document_file |
| lsms2005en/Data_2005/Modul_13C_dwellingc3_cl.sav | .sav | dwellingc3_cl | candidate_data_or_document_file |
| lsms2005en/Data_2005/Modul_14_social_assistance_cl.sav | .sav | social_assistance_cl | candidate_data_or_document_file |
| lsms2005en/Data_2005/Modul_15_other_income_cl.sav | .sav | other_income_cl | candidate_data_or_document_file |
| lsms2005en/Data_2005/Modul_16_social_capital_cl.sav | .sav | social_capital_cl | candidate_data_or_document_file |
| lsms2005en/Data_2005/Modul_17_id_agric_household_animals_cl.sav | .sav | id_agric_household_animals_cl | candidate_data_or_document_file |
| lsms2005en/Data_2005/Modul_17_id_agric_household_cl.sav | .sav | id_agric_household_cl | candidate_data_or_document_file |
| lsms2005en/Data_2005/Modul_1A_household_rostera_cl.sav | .sav | household_rostera_cl | candidate_data_or_document_file |
| lsms2005en/Data_2005/Modul_1B_household_rosterb_cl.sav | .sav | household_rosterb_cl | candidate_data_or_document_file |
| lsms2005en/Data_2005/Modul_2A_educationa_cl.sav | .sav | educationa_cl | candidate_data_or_document_file |
| lsms2005en/Data_2005/Modul_2B_dwellingb_cl.sav | .sav | dwellingb_cl | candidate_data_or_document_file |
| lsms2005en/Data_2005/Modul_2B_educationb_cl.sav | .sav | educationb_cl | candidate_data_or_document_file |
| lsms2005en/Data_2005/Modul_2C_educationc_cl.sav | .sav | educationc_cl | candidate_data_or_document_file |
| lsms2005en/Data_2005/Modul_3_communication_cl.sav | .sav | communication_cl | candidate_data_or_document_file |
| lsms2005en/Data_2005/Modul_3_communication_mobile_cl.sav | .sav | communication_mobile_cl | candidate_data_or_document_file |
| lsms2005en/Data_2005/Modul_4A_laboura_cl.sav | .sav | laboura_cl | candidate_data_or_document_file |
| lsms2005en/Data_2005/Modul_4B_labourb_cl.sav | .sav | labourb_cl | candidate_data_or_document_file |
| lsms2005en/Data_2005/Modul_4C_labourc_cl.sav | .sav | labourc_cl | candidate_data_or_document_file |
| lsms2005en/Data_2005/Modul_4D_labourd_cl.sav | .sav | labourd_cl | candidate_data_or_document_file |
| lsms2005en/Data_2005/Modul_5_non_farm_business_cl.sav | .sav | non_farm_business_cl | candidate_data_or_document_file |
| lsms2005en/Data_2005/Modul_5_non_farm_business_first_cl.sav | .sav | non_farm_business_first_cl | candidate_data_or_document_file |
| lsms2005en/Data_2005/Modul_6A_migrationa_cl.sav | .sav | migrationa_cl | candidate_data_or_document_file |
| lsms2005en/Data_2005/Modul_6B_migrationb2_cl.sav | .sav | migrationb2_cl | candidate_data_or_document_file |
| lsms2005en/Data_2005/Modul_6B_migrationb_cl.sav | .sav | migrationb_cl | candidate_data_or_document_file |
| lsms2005en/Data_2005/Modul_6C_migrationc_cl.sav | .sav | migrationc_cl | candidate_data_or_document_file |
| lsms2005en/Data_2005/Modul_6D_migrationd2_cl.sav | .sav | migrationd2_cl | candidate_data_or_document_file |
| lsms2005en/Data_2005/Modul_6D_migrationd_cl.sav | .sav | migrationd_cl | candidate_data_or_document_file |
| lsms2005en/Data_2005/Modul_6E_migratione_cl.sav | .sav | migratione_cl | candidate_data_or_document_file |
| lsms2005en/Data_2005/Modul_7_subjective_poverty_cl.sav | .sav | subjective_poverty_cl | candidate_data_or_document_file |
| lsms2005en/Data_2005/Modul_8_section2_cl.sav | .sav | section2_cl | candidate_data_or_document_file |
| lsms2005en/Data_2005/Modul_9A_healtha_cl.sav | .sav | healtha_cl | candidate_data_or_document_file |
| lsms2005en/Data_2005/Modul_9B_healthb_cl.sav | .sav | healthb_cl | candidate_data_or_document_file |
| lsms2005en/Data_2005/poverty.sav | .sav | poverty | candidate_data_or_document_file |
| lsms2005en/Data_2005/Weight_retro_2005.sav | .sav | weight_retro_2005 | candidate_data_or_document_file |
| lsms2005en/Questionnaire 2005/LSMS05_questionnaire_part1.xls | .xls | lsms05_questionnaire_part1 | candidate_data_or_document_file |
| lsms2005en/Questionnaire 2005/LSMS05_Questionnaire_part2.xls | .xls | lsms05_questionnaire_part2 | candidate_data_or_document_file |

## Interpretation

- The local archive manifest and extracted package both contain many core household, health, expenditure, poverty, and weight files, but they do not contain the DDI `bookmetadata_cl` module needed to verify diary beginning/finishing dates from raw values.
- The missing critical DDI modules are therefore not only an extraction-folder mismatch in the current workspace; they are also absent from the local archive member list.
- Public metadata therefore remains useful for identifying timing leads, but cannot be used to promote household interview timing.
- No extracted file name or metadata variable currently verifies household coordinates, despite the public DDI GPS statement.
- This audit does not write to `data/` and does not promote harmonized, household-timing, outcome, or climate-linkage rows.

## Machine-Readable Outputs

- `temp/alb2005_extracted_module_coverage_audit.csv`
- `temp/alb2005_extracted_extra_files_audit.csv`
- `temp/alb2005_archive_member_manifest.csv`
- `result/alb2005_extracted_module_coverage_summary.csv`
