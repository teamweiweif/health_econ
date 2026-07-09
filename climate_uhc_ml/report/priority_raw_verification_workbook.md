# Priority Raw Verification Workbook

Status: fillable post-download verification workbook for the current priority
10-wave batch and sixth-country backups. It does not verify any dataset by
itself and does not promote any row into `data/`.

## Summary

| Metric | Value | Interpretation |
|---|---:|---|
| priority_dataset_verification_gate_rows | 13 | Dataset-level priority raw verification gate rows. |
| priority_verification_priority_10_rows | 10 | Immediate priority waves covered by the workbook. |
| priority_verification_priority_10_countries | 5 | Priority countries covered by the workbook. |
| priority_verification_backup_rows | 3 | Sixth-country backup rows covered by the workbook. |
| priority_requirement_checklist_rows | 104 | Explicit requirement checklist rows aligned to the dataset promotion objective. |
| priority_concept_template_rows | 169 | Concept-level raw verification template rows. |
| priority_variable_template_rows | 1214 | Variable-level raw verification template rows. |
| priority_datasets_ready_for_manual_value_audit | 0 | Datasets with all promotion evidence ready for harmonization recipe review. |
| priority_requirements_ready_for_manual_audit | 0 | Requirement rows ready for manual raw-backed review. |
| priority_concepts_ready_for_manual_value_audit | 0 | Concept rows ready for manual value/label/unit/key audit. |
| priority_variables_ready_for_manual_value_audit | 0 | Variable rows ready for manual value/label/unit/key audit. |
| priority_raw_verification_handoff_readmes_written | 13 | Per-wave raw verification workbook README files written. |
| modeling_gate_status | blocked | Models remain blocked until promoted registry thresholds and accepted climate linkage pass. |
| dataset_gate_blocked_raw_files_absent | 13 | Dataset gate status count. |
| requirement_gate_blocked_raw_package_required | 104 | Requirement gate status count. |
| concept_gate_blocked_missing_metadata_candidate | 16 | Concept gate status count. |
| concept_gate_blocked_raw_file_missing | 153 | Concept gate status count. |
| variable_status_raw_candidate_not_matched | 16 | Variable verification status count. |
| variable_status_raw_not_inspected | 1198 | Variable verification status count. |

## Dataset Gate Status

| Dataset gate | Count |
|---|---:|
| `blocked_raw_files_absent` | 13 |

## Requirement Gate Status

| Requirement gate | Count |
|---|---:|
| `blocked_raw_package_required` | 104 |

## Concept Gate Status

| Concept gate | Count |
|---|---:|
| `blocked_raw_file_missing` | 153 |
| `blocked_missing_metadata_candidate` | 16 |

## Variable Verification Status

| Variable status | Count |
|---|---:|
| `raw_not_inspected` | 1198 |
| `raw_candidate_not_matched` | 16 |

## Dataset Gate Rows

| acquisition_batch_rank | batch_role | idno | country | wave | raw_file_inventory_rows | raw_variable_catalog_rows | current_gate_status | next_action |
|---|---|---|---|---|---|---|---|---|
| 1 | priority_10_wave_batch | ETH_2021_ESPS-W5_v02_M | Ethiopia | 2021-2022 | 0 | 0 | blocked_raw_files_absent | Download/place complete original raw package and documentation into the target folder. |
| 2 | priority_10_wave_batch | ETH_2018_ESS_v04_M | Ethiopia | 2018-2019 | 0 | 0 | blocked_raw_files_absent | Download/place complete original raw package and documentation into the target folder. |
| 3 | priority_10_wave_batch | MWI_2007-2009_MTM_v01_M | Malawi | 2007-2009 | 0 | 0 | blocked_raw_files_absent | Download/place complete original raw package and documentation into the target folder. |
| 4 | priority_10_wave_batch | NGA_2012_GHSP-W2_v02_M | Nigeria | 2012-2013 | 0 | 0 | blocked_raw_files_absent | Download/place complete original raw package and documentation into the target folder. |
| 5 | priority_10_wave_batch | NGA_2015_GHSP-W3_v02_M | Nigeria | 2015-2016 | 0 | 0 | blocked_raw_files_absent | Download/place complete original raw package and documentation into the target folder. |
| 6 | priority_10_wave_batch | NGA_2010_GHSP-W1_v03_M | Nigeria | 2010-2011 | 0 | 0 | blocked_raw_files_absent | Download/place complete original raw package and documentation into the target folder. |
| 7 | priority_10_wave_batch | TZA_2008_NPS-R1_v03_M | Tanzania | 2008-2009 | 0 | 0 | blocked_raw_files_absent | Download/place complete original raw package and documentation into the target folder. |
| 8 | priority_10_wave_batch | TZA_2010_NPS-R2_v03_M | Tanzania | 2010-2011 | 0 | 0 | blocked_raw_files_absent | Download/place complete original raw package and documentation into the target folder. |
| 9 | priority_10_wave_batch | TZA_2012_NPS-R3_v01_M | Tanzania | 2012-2013 | 0 | 0 | blocked_raw_files_absent | Download/place complete original raw package and documentation into the target folder. |
| 10 | priority_10_wave_batch | UGA_2014_SAGE-EL_v01_M | Uganda | 2014 | 0 | 0 | blocked_raw_files_absent | Download/place complete original raw package and documentation into the target folder. |
| 11 | sixth_country_backup_candidate | JAM_1997_SLC_v01_M | Jamaica | 1997 | 0 | 0 | blocked_raw_files_absent | Download/place complete original raw package and documentation into the target folder. |
| 12 | sixth_country_backup_candidate | KGZ_1993_KMPS_v01_M | Kyrgyz Republic | 1993 | 0 | 0 | blocked_raw_files_absent | Download/place complete original raw package and documentation into the target folder. |
| 13 | sixth_country_backup_candidate | NPL_2010_LSS-III_v01_M | Nepal | 2010-2011 | 0 | 0 | blocked_raw_files_absent | Download/place complete original raw package and documentation into the target folder. |

## Requirement Checklist Preview

| acquisition_batch_rank | idno | requirement_id | current_requirement_gate | minimum_evidence |
|---|---|---|---|---|
| 1 | ETH_2021_ESPS-W5_v02_M | household_person_merge_keys | blocked_raw_package_required | Household/person IDs and module-level keys match across raw files; key cardinality and duplicates are documented. |
| 1 | ETH_2021_ESPS-W5_v02_M | weights_and_survey_design | blocked_raw_package_required | Household/person weights, PSU/cluster, strata, and any design notes are verified from raw values and documentation. |
| 1 | ETH_2021_ESPS-W5_v02_M | consumption_or_income_aggregate | blocked_raw_package_required | Survey-team consumption/income aggregate or documented reconstruction variables are verified with units and period. |
| 1 | ETH_2021_ESPS-W5_v02_M | oop_health_expenditure | blocked_raw_package_required | OOP health spending variables are verified with payer scope, units, recall period, zero/missing semantics, and aggreg... |
| 1 | ETH_2021_ESPS-W5_v02_M | illness_need_care_access | blocked_raw_package_required | Illness/need denominator, care-seeking, forgone care, barrier categories, and insurance variables are verified. |
| 1 | ETH_2021_ESPS-W5_v02_M | survey_timing | blocked_raw_package_required | Interview date/month/year or fieldwork timing is verified and can support pre-interview lag windows. |
| 1 | ETH_2021_ESPS-W5_v02_M | geography_climate_linkage | blocked_raw_package_required | GPS, cluster, EA, or admin geography is verified with geolocation quality, displacement/suppression, and boundary/cro... |
| 1 | ETH_2021_ESPS-W5_v02_M | missing_skip_units_recall | blocked_raw_package_required | Missing codes, skip patterns, units, recall periods, valid ranges, and outlier handling are documented for all critic... |
| 2 | ETH_2018_ESS_v04_M | household_person_merge_keys | blocked_raw_package_required | Household/person IDs and module-level keys match across raw files; key cardinality and duplicates are documented. |
| 2 | ETH_2018_ESS_v04_M | weights_and_survey_design | blocked_raw_package_required | Household/person weights, PSU/cluster, strata, and any design notes are verified from raw values and documentation. |
| 2 | ETH_2018_ESS_v04_M | consumption_or_income_aggregate | blocked_raw_package_required | Survey-team consumption/income aggregate or documented reconstruction variables are verified with units and period. |
| 2 | ETH_2018_ESS_v04_M | oop_health_expenditure | blocked_raw_package_required | OOP health spending variables are verified with payer scope, units, recall period, zero/missing semantics, and aggreg... |
| 2 | ETH_2018_ESS_v04_M | illness_need_care_access | blocked_raw_package_required | Illness/need denominator, care-seeking, forgone care, barrier categories, and insurance variables are verified. |
| 2 | ETH_2018_ESS_v04_M | survey_timing | blocked_raw_package_required | Interview date/month/year or fieldwork timing is verified and can support pre-interview lag windows. |
| 2 | ETH_2018_ESS_v04_M | geography_climate_linkage | blocked_raw_package_required | GPS, cluster, EA, or admin geography is verified with geolocation quality, displacement/suppression, and boundary/cro... |
| 2 | ETH_2018_ESS_v04_M | missing_skip_units_recall | blocked_raw_package_required | Missing codes, skip patterns, units, recall periods, valid ranges, and outlier handling are documented for all critic... |
| 3 | MWI_2007-2009_MTM_v01_M | household_person_merge_keys | blocked_raw_package_required | Household/person IDs and module-level keys match across raw files; key cardinality and duplicates are documented. |
| 3 | MWI_2007-2009_MTM_v01_M | weights_and_survey_design | blocked_raw_package_required | Household/person weights, PSU/cluster, strata, and any design notes are verified from raw values and documentation. |
| 3 | MWI_2007-2009_MTM_v01_M | consumption_or_income_aggregate | blocked_raw_package_required | Survey-team consumption/income aggregate or documented reconstruction variables are verified with units and period. |
| 3 | MWI_2007-2009_MTM_v01_M | oop_health_expenditure | blocked_raw_package_required | OOP health spending variables are verified with payer scope, units, recall period, zero/missing semantics, and aggreg... |
| 3 | MWI_2007-2009_MTM_v01_M | illness_need_care_access | blocked_raw_package_required | Illness/need denominator, care-seeking, forgone care, barrier categories, and insurance variables are verified. |
| 3 | MWI_2007-2009_MTM_v01_M | survey_timing | blocked_raw_package_required | Interview date/month/year or fieldwork timing is verified and can support pre-interview lag windows. |
| 3 | MWI_2007-2009_MTM_v01_M | geography_climate_linkage | blocked_raw_package_required | GPS, cluster, EA, or admin geography is verified with geolocation quality, displacement/suppression, and boundary/cro... |
| 3 | MWI_2007-2009_MTM_v01_M | missing_skip_units_recall | blocked_raw_package_required | Missing codes, skip patterns, units, recall periods, valid ranges, and outlier handling are documented for all critic... |
| 4 | NGA_2012_GHSP-W2_v02_M | household_person_merge_keys | blocked_raw_package_required | Household/person IDs and module-level keys match across raw files; key cardinality and duplicates are documented. |
| 4 | NGA_2012_GHSP-W2_v02_M | weights_and_survey_design | blocked_raw_package_required | Household/person weights, PSU/cluster, strata, and any design notes are verified from raw values and documentation. |
| 4 | NGA_2012_GHSP-W2_v02_M | consumption_or_income_aggregate | blocked_raw_package_required | Survey-team consumption/income aggregate or documented reconstruction variables are verified with units and period. |
| 4 | NGA_2012_GHSP-W2_v02_M | oop_health_expenditure | blocked_raw_package_required | OOP health spending variables are verified with payer scope, units, recall period, zero/missing semantics, and aggreg... |
| 4 | NGA_2012_GHSP-W2_v02_M | illness_need_care_access | blocked_raw_package_required | Illness/need denominator, care-seeking, forgone care, barrier categories, and insurance variables are verified. |
| 4 | NGA_2012_GHSP-W2_v02_M | survey_timing | blocked_raw_package_required | Interview date/month/year or fieldwork timing is verified and can support pre-interview lag windows. |

## How To Use

1. Download complete original raw packages into each priority target folder.
2. Run `python script/17_audit_raw_downloads.py` and `python script/03_inspect_raw_schemas.py`.
3. Rerun `python script/126_build_priority_raw_verification_workbook.py`.
4. Fill the blank `fill_*` columns in the requirement, concept, and variable templates only after inspecting raw values, labels, units, recall periods, missing codes, levels, skip patterns, and merge keys.
5. Promote a wave only when all requirement rows, critical concept rows, selected variable rows, and accepted CHIRPS/ERA5 linkage gates pass.

## Machine-Readable Outputs

- `result/priority_dataset_verification_gate.csv`
- `temp/priority_promotion_verification_checklist.csv`
- `temp/priority_concept_verification_template.csv`
- `temp/priority_variable_verification_template.csv`
- `result/priority_raw_verification_workbook_summary.csv`
