# First-Batch Raw Acquisition Checklist

Status: manual raw-data acquisition checklist only. It selects the smallest current batch that can test the first two Phase 13 no-go thresholds: 6 countries for financial protection and 10 country-waves for double-failure support. No dataset in this checklist is analysis-ready until raw files and raw variables are inspected.

## Summary

| Metric | Value | Interpretation |
|---|---:|---|
| first_batch_dataset_rows | 10 | Dataset rows selected for the first manual raw acquisition batch. |
| first_batch_country_count | 7 | Unique countries in the first batch. |
| financial_probe_dataset_rows | 6 | Rows testing the 6-country financial-protection no-go rule. |
| double_failure_probe_dataset_rows | 10 | Rows testing the 10-wave double-failure no-go rule. |
| first_batch_file_target_rows | 183 | File/module targets to inspect immediately after download. |
| first_batch_raw_tabular_file_rows | 0 | Raw tabular files currently present across first-batch folders. |
| first_batch_archive_file_rows | 1 | Raw archive files currently present across first-batch folders. |
| first_batch_intake_status_instructions_or_documentation_only | 9 | First-batch raw intake status count. |
| first_batch_intake_status_ready_for_raw_schema_inspection | 1 | First-batch raw intake status count. |
| first_batch_target_reason_financial_core_file | 35 | First-batch file target reason count. |
| first_batch_target_reason_geography_timing_design_file | 28 | First-batch file target reason count. |
| first_batch_target_reason_top_metadata-supported_module_to_inspect_first | 120 | First-batch file target reason count. |

## Intake Status

| Raw intake status | Count |
|---|---:|
| instructions_or_documentation_only | 9 |
| ready_for_raw_schema_inspection | 1 |

## Target Reason Counts

| Target reason | Count |
|---|---:|
| top metadata-supported module to inspect first | 120 |
| financial core file | 35 |
| geography/timing/design file | 28 |

## Dataset Checklist

| batch_rank | country | wave | idno | included_acquisition_sets | raw_intake_status | local_target_folder |
|---|---|---|---|---|---|---|
| 1 | Albania | 2005 | ALB_2005_LSMS_v01_M | financial_6_country_probe;double_failure_10_wave_probe | ready_for_raw_schema_inspection | temp/raw_downloads/ALB_2005_LSMS_v01_M/ |
| 2 | Ethiopia | 2021-2022 | ETH_2021_ESPS-W5_v02_M | financial_6_country_probe;double_failure_10_wave_probe;multi_wave_panel_sequence_probe | instructions_or_documentation_only | temp/raw_downloads/ETH_2021_ESPS-W5_v02_M/ |
| 3 | Ethiopia | 2018-2019 | ETH_2018_ESS_v04_M | double_failure_10_wave_probe;multi_wave_panel_sequence_probe | instructions_or_documentation_only | temp/raw_downloads/ETH_2018_ESS_v04_M/ |
| 4 | Jamaica | 1997 | JAM_1997_SLC_v01_M | financial_6_country_probe;double_failure_10_wave_probe | instructions_or_documentation_only | temp/raw_downloads/JAM_1997_SLC_v01_M/ |
| 5 | Kyrgyz Republic | 1993 | KGZ_1993_KMPS_v01_M | financial_6_country_probe;double_failure_10_wave_probe | instructions_or_documentation_only | temp/raw_downloads/KGZ_1993_KMPS_v01_M/ |
| 6 | Malawi | 2007-2009 | MWI_2007-2009_MTM_v01_M | financial_6_country_probe;double_failure_10_wave_probe;multi_wave_panel_sequence_probe | instructions_or_documentation_only | temp/raw_downloads/MWI_2007-2009_MTM_v01_M/ |
| 7 | Malawi | 2004-2005 | MWI_2004_IHS-II_v01_M | double_failure_10_wave_probe;multi_wave_panel_sequence_probe | instructions_or_documentation_only | temp/raw_downloads/MWI_2004_IHS-II_v01_M/ |
| 8 | Nepal | 2010-2011 | NPL_2010_LSS-III_v01_M | financial_6_country_probe;double_failure_10_wave_probe | instructions_or_documentation_only | temp/raw_downloads/NPL_2010_LSS-III_v01_M/ |
| 9 | Nigeria | 2012-2013 | NGA_2012_GHSP-W2_v02_M | double_failure_10_wave_probe;multi_wave_panel_sequence_probe | instructions_or_documentation_only | temp/raw_downloads/NGA_2012_GHSP-W2_v02_M/ |
| 10 | Nigeria | 2015-2016 | NGA_2015_GHSP-W3_v02_M | double_failure_10_wave_probe;multi_wave_panel_sequence_probe | instructions_or_documentation_only | temp/raw_downloads/NGA_2015_GHSP-W3_v02_M/ |

## Core File Targets

| batch_rank | idno | file_name | target_reason | expected_file_status | candidate_categories |
|---|---|---|---|---|---|
| 1 | ALB_2005_LSMS_v01_M | healthA_cl | financial core file | archive_present_needs_schema_extraction | demographics;health_expenditure;health_need_access;shocks;survey_design |
| 1 | ALB_2005_LSMS_v01_M | poverty | financial core file | archive_present_needs_schema_extraction | consumption;demographics;geography;survey_design |
| 1 | ALB_2005_LSMS_v01_M | agriculture_hhlevel | geography/timing/design file | archive_present_needs_schema_extraction | demographics;geography;health_need_access;shocks;survey_design |
| 1 | ALB_2005_LSMS_v01_M | poverty | geography/timing/design file | archive_present_needs_schema_extraction | consumption;demographics;geography;survey_design |
| 1 | ALB_2005_LSMS_v01_M | identification_cl | geography/timing/design file | archive_present_needs_schema_extraction | geography;survey_design |
| 2 | ETH_2021_ESPS-W5_v02_M | sect8_3_ls_w5.dta | financial core file | not_present | geography;health_expenditure;health_need_access;shocks;survey_design |
| 2 | ETH_2021_ESPS-W5_v02_M | sect8_2_ls_w5.dta | financial core file | not_present | consumption;geography;health_need_access;shocks;survey_design |
| 2 | ETH_2021_ESPS-W5_v02_M | sect3_hh_w5.dta | financial core file | not_present | demographics;geography;health_expenditure;health_need_access;survey_design |
| 2 | ETH_2021_ESPS-W5_v02_M | sect8_3_ls_w5.dta | geography/timing/design file | not_present | geography;health_expenditure;health_need_access;shocks;survey_design |
| 2 | ETH_2021_ESPS-W5_v02_M | sect9_hh_w5.dta | geography/timing/design file | not_present | demographics;geography;shocks;survey_design |
| 3 | ETH_2018_ESS_v04_M | sect8_3_ls_w4.dta | financial core file | not_present | geography;health_expenditure;health_need_access;shocks;survey_design |
| 3 | ETH_2018_ESS_v04_M | sect3_hh_w4.dta | financial core file | not_present | demographics;geography;health_expenditure;health_need_access;survey_design |
| 3 | ETH_2018_ESS_v04_M | sect8_2_ls_w4.dta | financial core file | not_present | consumption;geography;health_need_access;shocks;survey_design |
| 3 | ETH_2018_ESS_v04_M | sect8_3_ls_w4.dta | geography/timing/design file | not_present | geography;health_expenditure;health_need_access;shocks;survey_design |
| 3 | ETH_2018_ESS_v04_M | sect9_hh_w4.dta | geography/timing/design file | not_present | demographics;geography;shocks;survey_design |
| 4 | JAM_1997_SLC_v01_M | REC003 | financial core file | not_present | health_expenditure;health_need_access |
| 4 | JAM_1997_SLC_v01_M | ANNUAL | financial core file | not_present | consumption;demographics;geography;survey_design |
| 4 | JAM_1997_SLC_v01_M | REC033 | geography/timing/design file | not_present | health_need_access;shocks;survey_design |
| 5 | KGZ_1993_KMPS_v01_M | KHHLD | financial core file | not_present | demographics;geography;health_expenditure;health_need_access;shocks;survey_design |
| 5 | KGZ_1993_KMPS_v01_M | KADULT | financial core file | not_present | consumption;demographics;geography;health_expenditure;health_need_access;shocks;survey_design |
| 5 | KGZ_1993_KMPS_v01_M | KCHILD | financial core file | not_present | demographics;health_expenditure;health_need_access;shocks;survey_design |
| 5 | KGZ_1993_KMPS_v01_M | INCEXP | financial core file | not_present | consumption;demographics;geography;health_need_access;shocks;survey_design |
| 6 | MWI_2007-2009_MTM_v01_M | p2_s10 | financial core file | not_present | demographics;health_expenditure;health_need_access;shocks;survey_design |
| 6 | MWI_2007-2009_MTM_v01_M | p2_s11 | financial core file | not_present | demographics;health_expenditure;health_need_access;shocks;survey_design |
| 6 | MWI_2007-2009_MTM_v01_M | hh2p3_s17 | financial core file | not_present | demographics;health_expenditure;health_need_access;shocks;survey_design |
| 6 | MWI_2007-2009_MTM_v01_M | hh2p3_s16 | financial core file | not_present | demographics;health_expenditure;health_need_access;shocks;survey_design |
| 6 | MWI_2007-2009_MTM_v01_M | hh2p2_s11 | financial core file | not_present | demographics;health_expenditure;health_need_access;shocks;survey_design |
| 6 | MWI_2007-2009_MTM_v01_M | hh2p2_s9 | financial core file | not_present | demographics;health_expenditure;health_need_access;survey_design |
| 6 | MWI_2007-2009_MTM_v01_M | p1_s4 | financial core file | not_present | consumption;survey_design |
| 6 | MWI_2007-2009_MTM_v01_M | hh2p1_s4 | financial core file | not_present | consumption;survey_design |
| 6 | MWI_2007-2009_MTM_v01_M | hh3p1_s4b | financial core file | not_present | demographics;health_expenditure;health_need_access;survey_design |
| 7 | MWI_2004_IHS-II_v01_M | sec_d | financial core file | not_present | demographics;geography;health_expenditure;health_need_access;shocks;survey_design |
| 7 | MWI_2004_IHS-II_v01_M | sec_i | financial core file | not_present | consumption;demographics;geography;survey_design |
| 7 | MWI_2004_IHS-II_v01_M | ihs2_household | geography/timing/design file | not_present | consumption;demographics;geography;health_need_access;shocks;survey_design |
| 7 | MWI_2004_IHS-II_v01_M | sec_r | geography/timing/design file | not_present | demographics;geography;shocks;survey_design |
| 7 | MWI_2004_IHS-II_v01_M | sec_d | geography/timing/design file | not_present | demographics;geography;health_expenditure;health_need_access;shocks;survey_design |
| 7 | MWI_2004_IHS-II_v01_M | sec_o | geography/timing/design file | not_present | demographics;geography;shocks;survey_design |
| 7 | MWI_2004_IHS-II_v01_M | sec_g | geography/timing/design file | not_present | demographics;geography;survey_design |
| 7 | MWI_2004_IHS-II_v01_M | sec_s | geography/timing/design file | not_present | demographics;geography;shocks;survey_design |
| 7 | MWI_2004_IHS-II_v01_M | sec_ac | geography/timing/design file | not_present | demographics;geography;health_need_access;survey_design |
| 7 | MWI_2004_IHS-II_v01_M | sec_ab | geography/timing/design file | not_present | demographics;geography;shocks;survey_design |
| 7 | MWI_2004_IHS-II_v01_M | sec_p | geography/timing/design file | not_present | demographics;geography;shocks;survey_design |
| 7 | MWI_2004_IHS-II_v01_M | sec_q1 | geography/timing/design file | not_present | demographics;geography;health_need_access;shocks;survey_design |
| 8 | NPL_2010_LSS-III_v01_M | FINAL_PREF | financial core file | not_present | consumption;demographics;geography;shocks;survey_design |
| 8 | NPL_2010_LSS-III_v01_M | S08 | financial core file | not_present | health_expenditure;health_need_access;survey_design |
| 8 | NPL_2010_LSS-III_v01_M | S19 | financial core file | not_present | consumption;demographics;health_need_access;shocks;survey_design |
| 8 | NPL_2010_LSS-III_v01_M | S13E2 | financial core file | not_present | consumption;survey_design |
| 8 | NPL_2010_LSS-III_v01_M | FINAL_PREF | geography/timing/design file | not_present | consumption;demographics;geography;shocks;survey_design |
| 8 | NPL_2010_LSS-III_v01_M | S00 | geography/timing/design file | not_present | demographics;geography;health_need_access;shocks;survey_design |
| 8 | NPL_2010_LSS-III_v01_M | S08 | geography/timing/design file | not_present | health_expenditure;health_need_access;survey_design |
| 8 | NPL_2010_LSS-III_v01_M | S13A1 | geography/timing/design file | not_present | geography;shocks;survey_design |
| 8 | NPL_2010_LSS-III_v01_M | anthro | geography/timing/design file | not_present | demographics;survey_design |
| 8 | NPL_2010_LSS-III_v01_M | S21 | geography/timing/design file | not_present | demographics;geography;survey_design |
| 8 | NPL_2010_LSS-III_v01_M | S19 | geography/timing/design file | not_present | consumption;demographics;health_need_access;shocks;survey_design |
| 8 | NPL_2010_LSS-III_v01_M | sample | geography/timing/design file | not_present | demographics;geography;survey_design |
| 8 | NPL_2010_LSS-III_v01_M | S16 | geography/timing/design file | not_present | demographics;geography;survey_design |
| 8 | NPL_2010_LSS-III_v01_M | S20 | geography/timing/design file | not_present | demographics;survey_design |
| 9 | NGA_2012_GHSP-W2_v02_M | sect4a_harvestw2 | financial core file | not_present | demographics;geography;health_expenditure;health_need_access;survey_design |
| 9 | NGA_2012_GHSP-W2_v02_M | cons_agg_wave2_visit1 | financial core file | not_present | consumption;demographics;geography;health_need_access;shocks;survey_design |
| 9 | NGA_2012_GHSP-W2_v02_M | cons_agg_wave2_visit2 | financial core file | not_present | consumption;demographics;geography;health_need_access;shocks;survey_design |

## Post-Download Verification

After placing complete original raw packages in the target folders, run:

```bash
python script/17_audit_raw_downloads.py
python script/03_inspect_raw_schemas.py
python script/29_build_raw_variable_verification_protocol.py
python script/33_build_harmonization_recipe_gate.py
python script/35_build_empirical_readiness_dashboard.py
python script/37_build_first_batch_raw_acquisition_checklist.py
```

Pass evidence for each dataset is raw file inventory rows and raw variable catalog rows linked to the dataset ID. Metadata-only module names are not enough.

## Stop Rules

- Do not create or promote `temp/harmonization_recipe.csv` from metadata-only hits.
- Do not write clean analytical data into `data/` until raw keys, levels, units, recall periods, missing codes, and labels are audited.
- Do not construct SDG 3.8.2 unless the discretionary-budget denominator can be verified from raw values.
- Do not estimate prediction, reduced-form, causal ML, policy learning, mechanisms, or robustness checks from this checklist alone.

## Machine-Readable Outputs

- `temp/first_batch_raw_acquisition_checklist.csv`
- `temp/first_batch_raw_file_targets.csv`
- `result/first_batch_raw_acquisition_summary.csv`
