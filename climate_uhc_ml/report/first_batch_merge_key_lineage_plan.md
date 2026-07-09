# First-Batch Merge-Key Lineage Plan

Status: metadata-only planning layer. This file identifies candidate household/person keys, survey design variables, timing variables, geography variables, and core file relationships for the first manual raw-download batch. It does not verify raw values, labels, merge cardinality, units, missing codes, or sample levels.

## Summary

| Metric | Value | Interpretation |
|---|---:|---|
| first_batch_merge_key_lineage_plan_rows | 10 | Dataset-level merge-key lineage planning rows. |
| first_batch_merge_key_lineage_dataset_rows | 10 | First-batch datasets represented in the merge-key lineage plan. |
| first_batch_merge_key_candidate_variable_rows | 5112 | Long candidate key/design/timing/geography variable rows. |
| first_batch_merge_key_lineage_planned_rows | 8 | Datasets with metadata-supported household key, design, timing, and geography candidates. |
| first_batch_merge_key_lineage_incomplete_rows | 2 | Datasets missing one or more metadata key-lineage domains or file support checks. |
| first_batch_merge_key_raw_ready_rows | 1 | Datasets with raw files and variables present for value/key audit. |
| first_batch_merge_key_metadata_unsupported_file_rows | 0 | Unsupported first-batch file-source trace rows within merge-key planning. |
| first_batch_merge_key_candidate_household_id_rows | 771 | Candidate key-lineage variable rows by role. |
| first_batch_merge_key_candidate_person_id_rows | 193 | Candidate key-lineage variable rows by role. |
| first_batch_merge_key_candidate_survey_weight_rows | 379 | Candidate key-lineage variable rows by role. |
| first_batch_merge_key_candidate_psu_cluster_rows | 1129 | Candidate key-lineage variable rows by role. |
| first_batch_merge_key_candidate_strata_rows | 161 | Candidate key-lineage variable rows by role. |
| first_batch_merge_key_candidate_survey_timing_rows | 63 | Candidate key-lineage variable rows by role. |
| first_batch_merge_key_candidate_geography_rows | 2416 | Candidate key-lineage variable rows by role. |
| merge_key_lineage_status_metadata_key_lineage_incomplete_no_household_id_raw_unverified | 2 | Dataset-level merge-key lineage status count. |
| merge_key_lineage_status_metadata_key_lineage_planned_raw_unverified | 8 | Dataset-level merge-key lineage status count. |
| merge_key_raw_gate_status_blocked_raw_microdata | 9 | Dataset-level raw gate status count. |
| merge_key_raw_gate_status_raw_files_present_requires_value_key_audit | 1 | Dataset-level raw gate status count. |

## Dataset Status

| Merge-key lineage status | Count |
|---|---:|
| metadata_key_lineage_planned_raw_unverified | 8 |
| metadata_key_lineage_incomplete_no_household_id_raw_unverified | 2 |

## Raw Gate Status

| Raw gate status | Count |
|---|---:|
| blocked_raw_microdata | 9 |
| raw_files_present_requires_value_key_audit | 1 |

## Candidate Roles

| Candidate variable role | Count |
|---|---:|
| geography | 2416 |
| psu_cluster | 1129 |
| household_id | 771 |
| survey_weight | 379 |
| person_id | 193 |
| strata | 161 |
| survey_timing | 63 |

## Dataset-Level Plan

| batch_rank | idno | household_id_candidate_count | person_id_candidate_count | survey_weight_candidate_count | psu_candidate_count | strata_candidate_count | timing_candidate_count | geography_candidate_count | merge_key_lineage_status | raw_gate_status |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | ALB_2005_LSMS_v01_M | 188 | 14 | 13 | 124 | 6 | 6 | 79 | metadata_key_lineage_planned_raw_unverified | raw_files_present_requires_value_key_audit |
| 2 | ETH_2021_ESPS-W5_v02_M | 72 | 13 | 79 | 172 | 10 | 6 | 233 | metadata_key_lineage_planned_raw_unverified | blocked_raw_microdata |
| 3 | ETH_2018_ESS_v04_M | 74 | 16 | 82 | 166 | 10 | 8 | 200 | metadata_key_lineage_planned_raw_unverified | blocked_raw_microdata |
| 4 | JAM_1997_SLC_v01_M | 0 | 4 | 18 | 2 | 2 | 2 | 19 | metadata_key_lineage_incomplete_no_household_id_raw_unverified | blocked_raw_microdata |
| 5 | KGZ_1993_KMPS_v01_M | 32 | 9 | 12 | 0 | 0 | 8 | 970 | metadata_key_lineage_planned_raw_unverified | blocked_raw_microdata |
| 6 | MWI_2007-2009_MTM_v01_M | 137 | 83 | 12 | 185 | 0 | 20 | 67 | metadata_key_lineage_planned_raw_unverified | blocked_raw_microdata |
| 7 | MWI_2004_IHS-II_v01_M | 55 | 1 | 75 | 198 | 59 | 4 | 345 | metadata_key_lineage_planned_raw_unverified | blocked_raw_microdata |
| 8 | NPL_2010_LSS-III_v01_M | 0 | 2 | 18 | 32 | 74 | 3 | 49 | metadata_key_lineage_incomplete_no_household_id_raw_unverified | blocked_raw_microdata |
| 9 | NGA_2012_GHSP-W2_v02_M | 112 | 35 | 30 | 123 | 0 | 2 | 224 | metadata_key_lineage_planned_raw_unverified | blocked_raw_microdata |
| 10 | NGA_2015_GHSP-W3_v02_M | 101 | 16 | 40 | 127 | 0 | 4 | 230 | metadata_key_lineage_planned_raw_unverified | blocked_raw_microdata |

## Candidate Variables

| batch_rank | idno | lineage_role | file_name | raw_variable | harmonized_variable | source_trace_status |
|---|---|---|---|---|---|---|
| 1 | ALB_2005_LSMS_v01_M | household_id | agriculture_hhlevel | hh | hhid | metadata_file_and_examples_supported |
| 1 | ALB_2005_LSMS_v01_M | household_id | agriculture_hhlevel | hhid | hhid | metadata_file_and_examples_supported |
| 1 | ALB_2005_LSMS_v01_M | household_id | bookbread_cl | hhid | hhid | not_in_first_batch_file_source_trace |
| 1 | ALB_2005_LSMS_v01_M | household_id | bookbread_cl | ma_q01 | hhid | not_in_first_batch_file_source_trace |
| 1 | ALB_2005_LSMS_v01_M | household_id | bookchecklist_cl | hhid | hhid | not_in_first_batch_file_source_trace |
| 1 | ALB_2005_LSMS_v01_M | household_id | bookchecklist_cl | ma_q01 | hhid | not_in_first_batch_file_source_trace |
| 1 | ALB_2005_LSMS_v01_M | household_id | bookdaily_cl | hhid | hhid | not_in_first_batch_file_source_trace |
| 1 | ALB_2005_LSMS_v01_M | household_id | bookdaily_cl | ma_q01 | hhid | not_in_first_batch_file_source_trace |
| 1 | ALB_2005_LSMS_v01_M | household_id | bookfoodeaten_cl | hhid | hhid | not_in_first_batch_file_source_trace |
| 1 | ALB_2005_LSMS_v01_M | household_id | bookfoodeaten_cl | ma_q01 | hhid | not_in_first_batch_file_source_trace |
| 1 | ALB_2005_LSMS_v01_M | household_id | bookmetadata_cl | hhid | hhid | not_in_first_batch_file_source_trace |
| 1 | ALB_2005_LSMS_v01_M | household_id | bookmetadata_cl | ma_q01 | hhid | not_in_first_batch_file_source_trace |
| 1 | ALB_2005_LSMS_v01_M | household_id | booknonpurchased_cl | hhid | hhid | not_in_first_batch_file_source_trace |
| 1 | ALB_2005_LSMS_v01_M | household_id | booknonpurchased_cl | ma_q01 | hhid | not_in_first_batch_file_source_trace |
| 1 | ALB_2005_LSMS_v01_M | household_id | check_form_food_cl | hhid | hhid | not_in_first_batch_file_source_trace |
| 1 | ALB_2005_LSMS_v01_M | household_id | check_form_food_cl | m0_q01 | hhid | not_in_first_batch_file_source_trace |
| 1 | ALB_2005_LSMS_v01_M | household_id | communication_cl | hhid | hhid | not_in_first_batch_file_source_trace |
| 1 | ALB_2005_LSMS_v01_M | household_id | communication_cl | m0_q01 | hhid | not_in_first_batch_file_source_trace |
| 1 | ALB_2005_LSMS_v01_M | household_id | communication_mobile_cl | hhid | hhid | not_in_first_batch_file_source_trace |
| 1 | ALB_2005_LSMS_v01_M | household_id | communication_mobile_cl | m0_q01 | hhid | not_in_first_batch_file_source_trace |
| 1 | ALB_2005_LSMS_v01_M | household_id | dwellingA_cl | hhid | hhid | metadata_file_and_examples_supported |
| 1 | ALB_2005_LSMS_v01_M | household_id | dwellingA_cl | m0_q01 | hhid | metadata_file_and_examples_supported |
| 1 | ALB_2005_LSMS_v01_M | household_id | dwellingB_cl | hhid | hhid | metadata_file_and_examples_supported |
| 1 | ALB_2005_LSMS_v01_M | household_id | dwellingB_cl | m0_q01 | hhid | metadata_file_and_examples_supported |
| 1 | ALB_2005_LSMS_v01_M | household_id | dwellingC1_cl | hhid | hhid | not_in_first_batch_file_source_trace |
| 1 | ALB_2005_LSMS_v01_M | household_id | dwellingC1_cl | m0_q01 | hhid | not_in_first_batch_file_source_trace |
| 1 | ALB_2005_LSMS_v01_M | household_id | dwellingC2_cl | hhid | hhid | not_in_first_batch_file_source_trace |
| 1 | ALB_2005_LSMS_v01_M | household_id | dwellingC2_cl | m0_q01 | hhid | not_in_first_batch_file_source_trace |
| 1 | ALB_2005_LSMS_v01_M | household_id | dwellingC3_cl | hhid | hhid | not_in_first_batch_file_source_trace |
| 1 | ALB_2005_LSMS_v01_M | household_id | dwellingC3_cl | m0_q01 | hhid | not_in_first_batch_file_source_trace |

## Guardrails

- Candidate keys and design variables are metadata-derived only.
- A planned lineage row is not a verified merge plan until raw files are downloaded and raw values are inspected.
- Do not create `data/` outputs, harmonization recipes, outcomes, climate-linked data, models, causal estimates, or policy simulations from this plan alone.
- After manual download, verify ID uniqueness, person-household nesting, merge cardinality, PSU/strata/weight distributions, timing granularity, geography precision, and missing-code semantics before promotion.

## Machine-Readable Outputs

- `temp/first_batch_merge_key_lineage_plan.csv`
- `temp/first_batch_merge_key_candidate_variables.csv`
- `result/first_batch_merge_key_lineage_summary.csv`
