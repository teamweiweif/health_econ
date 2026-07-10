# Priority LSMS-ISA Threshold Download Sequence

Status: refocused threshold-oriented manual download sequence for the
19-wave LSMS/ISA acquisition queue. This replaces the older 13-wave threshold
campaign for the current dataset-promotion objective.

It does not download raw data, accept terms, verify values, create harmonized
datasets, or write `data/`.

## Summary

| Metric | Value | Interpretation |
|---|---:|---|
| priority_lsms_threshold_sequence_dataset_rows | 19 | Refocused LSMS/ISA country-waves ordered for threshold-oriented manual download. |
| priority_lsms_threshold_sequence_country_rows | 8 | Countries represented in the threshold download sequence. |
| priority_lsms_threshold_sequence_priority_country_rows | 16 | Rows from Ethiopia, Nigeria, Malawi, Tanzania, and Uganda. |
| priority_lsms_threshold_sequence_minimum_download_rows | 11 | Minimum manual downloads: 10 core waves plus the highest-ranked sixth-country candidate if every wave passes raw/value/climate gates. |
| priority_lsms_threshold_sequence_minimum_country_rows | 6 | Distinct countries represented by the minimum threshold batch. |
| priority_lsms_threshold_sequence_recommended_download_rows | 13 | Recommended threshold downloads: 10 core waves plus all sixth-country candidates to reduce failure risk. |
| priority_lsms_threshold_sequence_recommended_country_rows | 8 | Distinct countries represented by the recommended threshold batch. |
| priority_lsms_threshold_sequence_full_download_rows | 19 | Full refocused acquisition queue including same-country replacement backups. |
| priority_lsms_threshold_sequence_expected_file_rows | 1597 | Official DDI files expected across the full refocused queue. |
| priority_lsms_threshold_sequence_expected_file_matched_rows | 52 | Expected official files currently matched locally. |
| priority_lsms_threshold_sequence_core_file_rows | 629 | Core official file rows across the full refocused queue. |
| priority_lsms_threshold_sequence_core_file_matched_rows | 37 | Core official files currently matched locally. |
| priority_lsms_threshold_sequence_raw_package_received_rows | 1 | Rows with any non-blocked official file receipt status. |
| priority_lsms_threshold_sequence_promoted_analysis_ready_rows | 0 | Rows analysis-ready in the promoted registry. |
| priority_lsms_threshold_sequence_handoff_readmes_written | 19 | Per-wave threshold download sequence handoffs written. |
| priority_lsms_threshold_sequence_data_write_status | blocked_no_promoted_rows | Threshold sequencing never writes promoted data. |
| modeling_gate_status | blocked | Models remain blocked until 6 countries, 10 country-waves, and accepted CHIRPS/ERA5 linkage are value-verified. |
| priority_lsms_threshold_sequence_phase_phase_1_core_10_wave_double_failure_base | 10 | Threshold sequence row count by phase. |
| priority_lsms_threshold_sequence_phase_phase_2_sixth_country_financial_protection_candidate | 3 | Threshold sequence row count by phase. |
| priority_lsms_threshold_sequence_phase_phase_3_same_country_replacement_backup_after_primary_failure | 6 | Threshold sequence row count by phase. |
| priority_lsms_threshold_sequence_role_minimum_10_wave_core | 10 | Threshold sequence row count by download role. |
| priority_lsms_threshold_sequence_role_minimum_6th_country_financial_protection_candidate | 1 | Threshold sequence row count by download role. |
| priority_lsms_threshold_sequence_role_same_country_primary_failure_backup | 6 | Threshold sequence row count by download role. |
| priority_lsms_threshold_sequence_role_sixth_country_failure_backup | 2 | Threshold sequence row count by download role. |

## Minimum Threshold Batch

This is the smallest current download set that can plausibly reach the formal
pre-modeling thresholds if every wave passes raw receipt, raw-value, outcome,
and climate-linkage gates: 10 core waves plus one sixth-country candidate.

| threshold_sequence_rank | threshold_download_role | country | wave | idno | official_expected_file_rows | official_core_file_rows | official_file_receipt_status |
|---|---|---|---|---|---|---|---|
| 1 | minimum_10_wave_core | Ethiopia | 2021-2022 | ETH_2021_ESPS-W5_v02_M | 68 | 36 | blocked_no_original_package |
| 2 | minimum_10_wave_core | Ethiopia | 2018-2019 | ETH_2018_ESS_v04_M | 68 | 35 | blocked_no_original_package |
| 3 | minimum_10_wave_core | Malawi | 2004-2005 | MWI_2004_IHS-II_v01_M | 52 | 37 | official_file_receipt_complete_pending_schema_value_review |
| 4 | minimum_10_wave_core | Nigeria | 2012-2013 | NGA_2012_GHSP-W2_v02_M | 103 | 26 | blocked_no_original_package |
| 5 | minimum_10_wave_core | Nigeria | 2015-2016 | NGA_2015_GHSP-W3_v02_M | 104 | 26 | blocked_no_original_package |
| 6 | minimum_10_wave_core | Nigeria | 2010-2011 | NGA_2010_GHSP-W1_v03_M | 99 | 27 | blocked_no_original_package |
| 7 | minimum_10_wave_core | Tanzania | 2008-2009 | TZA_2008_NPS-R1_v03_M | 61 | 35 | blocked_no_original_package |
| 8 | minimum_10_wave_core | Tanzania | 2010-2011 | TZA_2010_NPS-R2_v03_M | 95 | 38 | blocked_no_original_package |
| 9 | minimum_10_wave_core | Tanzania | 2012-2013 | TZA_2012_NPS-R3_v01_M | 80 | 33 | blocked_no_original_package |
| 10 | minimum_10_wave_core | Uganda | 2019-2020 | UGA_2019_UNPS_v03_M | 109 | 39 | blocked_no_original_package |
| 11 | minimum_6th_country_financial_protection_candidate | Nepal | 2010-2011 | NPL_2010_LSS-III_v01_M | 51 | 28 | blocked_no_original_package |

## Full Refocused Download Sequence

| threshold_sequence_rank | threshold_phase | threshold_download_role | country | wave | idno | metadata_requirement_score | official_file_receipt_status |
|---|---|---|---|---|---|---|---|
| 1 | phase_1_core_10_wave_double_failure_base | minimum_10_wave_core | Ethiopia | 2021-2022 | ETH_2021_ESPS-W5_v02_M | 7 | blocked_no_original_package |
| 2 | phase_1_core_10_wave_double_failure_base | minimum_10_wave_core | Ethiopia | 2018-2019 | ETH_2018_ESS_v04_M | 7 | blocked_no_original_package |
| 3 | phase_1_core_10_wave_double_failure_base | minimum_10_wave_core | Malawi | 2004-2005 | MWI_2004_IHS-II_v01_M | 7 | official_file_receipt_complete_pending_schema_value_review |
| 4 | phase_1_core_10_wave_double_failure_base | minimum_10_wave_core | Nigeria | 2012-2013 | NGA_2012_GHSP-W2_v02_M | 7 | blocked_no_original_package |
| 5 | phase_1_core_10_wave_double_failure_base | minimum_10_wave_core | Nigeria | 2015-2016 | NGA_2015_GHSP-W3_v02_M | 7 | blocked_no_original_package |
| 6 | phase_1_core_10_wave_double_failure_base | minimum_10_wave_core | Nigeria | 2010-2011 | NGA_2010_GHSP-W1_v03_M | 7 | blocked_no_original_package |
| 7 | phase_1_core_10_wave_double_failure_base | minimum_10_wave_core | Tanzania | 2008-2009 | TZA_2008_NPS-R1_v03_M | 1 | blocked_no_original_package |
| 8 | phase_1_core_10_wave_double_failure_base | minimum_10_wave_core | Tanzania | 2010-2011 | TZA_2010_NPS-R2_v03_M | 7 | blocked_no_original_package |
| 9 | phase_1_core_10_wave_double_failure_base | minimum_10_wave_core | Tanzania | 2012-2013 | TZA_2012_NPS-R3_v01_M | 7 | blocked_no_original_package |
| 10 | phase_1_core_10_wave_double_failure_base | minimum_10_wave_core | Uganda | 2019-2020 | UGA_2019_UNPS_v03_M | 5 | blocked_no_original_package |
| 11 | phase_2_sixth_country_financial_protection_candidate | minimum_6th_country_financial_protection_candidate | Nepal | 2010-2011 | NPL_2010_LSS-III_v01_M | 7 | blocked_no_original_package |
| 12 | phase_2_sixth_country_financial_protection_candidate | sixth_country_failure_backup | Kyrgyz Republic | 1993 | KGZ_1993_KMPS_v01_M | 7 | blocked_no_original_package |
| 13 | phase_2_sixth_country_financial_protection_candidate | sixth_country_failure_backup | Jamaica | 1997 | JAM_1997_SLC_v01_M | 1 | blocked_no_original_package |
| 14 | phase_3_same_country_replacement_backup_after_primary_failure | same_country_primary_failure_backup | Malawi | 2019-2020 | MWI_2019_IHS-V_v06_M | 5 | blocked_no_original_package |
| 15 | phase_3_same_country_replacement_backup_after_primary_failure | same_country_primary_failure_backup | Malawi | 2016-2017 | MWI_2016_IHS-IV_v04_M | 5 | blocked_no_original_package |
| 16 | phase_3_same_country_replacement_backup_after_primary_failure | same_country_primary_failure_backup | Malawi | 2010-2011 | MWI_2010_IHS-III_v01_M | 5 | blocked_no_original_package |
| 17 | phase_3_same_country_replacement_backup_after_primary_failure | same_country_primary_failure_backup | Uganda | 2011-2012 | UGA_2011_UNPS_v02_M | 7 | blocked_no_original_package |
| 18 | phase_3_same_country_replacement_backup_after_primary_failure | same_country_primary_failure_backup | Uganda | 2018-2019 | UGA_2018_UNPS_v02_M | 5 | blocked_no_original_package |
| 19 | phase_3_same_country_replacement_backup_after_primary_failure | same_country_primary_failure_backup | Uganda | 2015-2016 | UGA_2015_UNPS_v02_M | 5 | blocked_no_original_package |

## Country Coverage

| country | priority_country | planned_country_wave_rows | minimum_threshold_batch_rows | recommended_threshold_batch_rows | threshold_contribution |
|---|---|---|---|---|---|
| Ethiopia | 1 | 2 | 2 | 2 | minimum_threshold_batch_country |
| Jamaica | 0 | 1 | 0 | 1 | recommended_sixth_country_backup |
| Kyrgyz Republic | 0 | 1 | 0 | 1 | recommended_sixth_country_backup |
| Malawi | 1 | 4 | 1 | 1 | minimum_threshold_batch_country |
| Nepal | 0 | 1 | 1 | 1 | minimum_threshold_batch_country |
| Nigeria | 1 | 3 | 3 | 3 | minimum_threshold_batch_country |
| Tanzania | 1 | 3 | 3 | 3 | minimum_threshold_batch_country |
| Uganda | 1 | 4 | 1 | 1 | minimum_threshold_batch_country |

## Outputs

- `temp/priority_lsms_isa_threshold_download_sequence.csv`
- `temp/priority_lsms_isa_threshold_minimum_batch.csv`
- `temp/priority_lsms_isa_threshold_country_coverage.csv`
- `result/priority_lsms_isa_threshold_download_sequence_summary.csv`

## Stop Rule

The sequence is only an acquisition ordering tool. Modeling and promoted
dataset writes remain blocked until the promoted registry contains at least
6 value-verified financial-protection countries, 10 value-verified
country-waves for double failure, and at least one accepted CHIRPS or ERA5
climate-linkage route.
