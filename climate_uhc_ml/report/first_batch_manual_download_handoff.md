# First-Batch Manual Download Handoff

Status: manual-account handoff packet only. The official access probe found access-gate language for the first-batch datasets, and no raw file has been inspected. This packet tells a human exactly what to download and where to place it; it does not claim data access or raw verification.

## Summary

| Metric | Value | Interpretation |
|---|---:|---|
| first_batch_handoff_rows | 10 | Dataset-level manual download handoff rows. |
| first_batch_file_queue_rows | 143 | Deduplicated first-batch file/module queue rows. |
| first_batch_access_gate_rows | 10 | Dataset rows with official access-gate language. |
| first_batch_possible_direct_raw_route_rows | 0 | Dataset rows with possible ungated direct raw route signals. |
| first_batch_raw_file_inventory_rows | 46 | Raw file inventory rows currently linked to handoff datasets. |
| first_batch_raw_variable_catalog_rows | 1187 | Raw variable catalog rows currently linked to handoff datasets. |
| handoff_status_manual_account_terms_download_required | 9 | Manual download handoff status count. |
| handoff_status_ready_for_raw_schema_and_value_audit | 1 | Manual download handoff status count. |
| direct_raw_route_status_no_direct_raw_route_access_gate_detected | 10 | Direct raw route status count. |
| file_queue_reason_financial_core_file | 35 | Deduplicated file queue target-reason count. |
| file_queue_reason_geography_timing_design_file | 28 | Deduplicated file queue target-reason count. |
| file_queue_reason_top_metadata-supported_module_to_inspect_first | 120 | Deduplicated file queue target-reason count. |

## Handoff Status

| Handoff status | Count |
|---|---:|
| manual_account_terms_download_required | 9 |
| ready_for_raw_schema_and_value_audit | 1 |

## Direct Raw Route Status

| Direct raw route status | Count |
|---|---:|
| no_direct_raw_route_access_gate_detected | 10 |

## Dataset Actions

| batch_rank | country | wave | idno | handoff_status | local_target_folder |
|---|---|---|---|---|---|
| 1 | Albania | 2005 | ALB_2005_LSMS_v01_M | ready_for_raw_schema_and_value_audit | temp/raw_downloads/ALB_2005_LSMS_v01_M/ |
| 2 | Ethiopia | 2021-2022 | ETH_2021_ESPS-W5_v02_M | manual_account_terms_download_required | temp/raw_downloads/ETH_2021_ESPS-W5_v02_M/ |
| 3 | Ethiopia | 2018-2019 | ETH_2018_ESS_v04_M | manual_account_terms_download_required | temp/raw_downloads/ETH_2018_ESS_v04_M/ |
| 4 | Jamaica | 1997 | JAM_1997_SLC_v01_M | manual_account_terms_download_required | temp/raw_downloads/JAM_1997_SLC_v01_M/ |
| 5 | Kyrgyz Republic | 1993 | KGZ_1993_KMPS_v01_M | manual_account_terms_download_required | temp/raw_downloads/KGZ_1993_KMPS_v01_M/ |
| 6 | Malawi | 2007-2009 | MWI_2007-2009_MTM_v01_M | manual_account_terms_download_required | temp/raw_downloads/MWI_2007-2009_MTM_v01_M/ |
| 7 | Malawi | 2004-2005 | MWI_2004_IHS-II_v01_M | manual_account_terms_download_required | temp/raw_downloads/MWI_2004_IHS-II_v01_M/ |
| 8 | Nepal | 2010-2011 | NPL_2010_LSS-III_v01_M | manual_account_terms_download_required | temp/raw_downloads/NPL_2010_LSS-III_v01_M/ |
| 9 | Nigeria | 2012-2013 | NGA_2012_GHSP-W2_v02_M | manual_account_terms_download_required | temp/raw_downloads/NGA_2012_GHSP-W2_v02_M/ |
| 10 | Nigeria | 2015-2016 | NGA_2015_GHSP-W3_v02_M | manual_account_terms_download_required | temp/raw_downloads/NGA_2015_GHSP-W3_v02_M/ |

## File Queue By Dataset

### 1. ALB_2005_LSMS_v01_M

- Official URL: https://microdata.worldbank.org/catalog/64/get-microdata
- Local target folder: `temp/raw_downloads/ALB_2005_LSMS_v01_M/`
- Access status: `ready_for_raw_schema_and_value_audit`; direct route: `no_direct_raw_route_access_gate_detected`

| file_name | target_reasons | candidate_categories | candidate_variable_count |
|---|---|---|---|
| poverty | financial core file;geography/timing/design file;top metadata-supported module to inspect first | consumption;demographics;geography;survey_design | 19 |
| healthA_cl | financial core file;top metadata-supported module to inspect first | demographics;health_expenditure;health_need_access;shocks;survey_design | 49 |
| agriculture_hhlevel | geography/timing/design file;top metadata-supported module to inspect first | demographics;geography;health_need_access;shocks;survey_design | 91 |
| identification_cl | geography/timing/design file | geography;survey_design | 9 |
| community_all | top metadata-supported module to inspect first | demographics;geography;health_need_access;shocks;survey_design | 135 |
| community_dups | top metadata-supported module to inspect first | demographics;geography;health_need_access;shocks;survey_design | 135 |
| dwellingA_cl | top metadata-supported module to inspect first | demographics;health_need_access;shocks;survey_design | 31 |
| dwellingB_cl | top metadata-supported module to inspect first | demographics;health_need_access;shocks;survey_design | 26 |

### 2. ETH_2021_ESPS-W5_v02_M

- Official URL: https://microdata.worldbank.org/catalog/6161/get-microdata
- Local target folder: `temp/raw_downloads/ETH_2021_ESPS-W5_v02_M/`
- Access status: `manual_account_terms_download_required`; direct route: `no_direct_raw_route_access_gate_detected`

| file_name | target_reasons | candidate_categories | candidate_variable_count |
|---|---|---|---|
| sect8_3_ls_w5.dta | financial core file;geography/timing/design file;top metadata-supported module to inspect first | geography;health_expenditure;health_need_access;shocks;survey_design | 94 |
| sect8_2_ls_w5.dta | financial core file;top metadata-supported module to inspect first | consumption;geography;health_need_access;shocks;survey_design | 32 |
| sect3_hh_w5.dta | financial core file;top metadata-supported module to inspect first | demographics;geography;health_expenditure;health_need_access;survey_design | 31 |
| sect9_hh_w5.dta | geography/timing/design file | demographics;geography;shocks;survey_design | 23 |
| sect11_ph_w5.dta | top metadata-supported module to inspect first | geography;health_need_access;shocks;survey_design | 59 |
| sect3_pp_w5.dta | top metadata-supported module to inspect first | geography;health_need_access;shocks;survey_design | 48 |
| sect06_com_w5.dta | top metadata-supported module to inspect first | geography;health_need_access;shocks;survey_design | 44 |
| sect04_com_w5.dta | top metadata-supported module to inspect first | demographics;geography;health_need_access;shocks;survey_design | 42 |

### 3. ETH_2018_ESS_v04_M

- Official URL: https://microdata.worldbank.org/catalog/3823/get-microdata
- Local target folder: `temp/raw_downloads/ETH_2018_ESS_v04_M/`
- Access status: `manual_account_terms_download_required`; direct route: `no_direct_raw_route_access_gate_detected`

| file_name | target_reasons | candidate_categories | candidate_variable_count |
|---|---|---|---|
| sect8_3_ls_w4.dta | financial core file;geography/timing/design file;top metadata-supported module to inspect first | geography;health_expenditure;health_need_access;shocks;survey_design | 69 |
| sect3_hh_w4.dta | financial core file;top metadata-supported module to inspect first | demographics;geography;health_expenditure;health_need_access;survey_design | 32 |
| sect8_2_ls_w4.dta | financial core file;top metadata-supported module to inspect first | consumption;geography;health_need_access;shocks;survey_design | 32 |
| sect9_hh_w4.dta | geography/timing/design file | demographics;geography;shocks;survey_design | 23 |
| sect10c_hh_w4.dta | top metadata-supported module to inspect first | demographics;geography;shocks;survey_design | 64 |
| sect11_ph_w4.dta | top metadata-supported module to inspect first | geography;health_need_access;shocks;survey_design | 56 |
| sect04_com_w4.dta | top metadata-supported module to inspect first | demographics;geography;health_need_access;shocks;survey_design | 42 |
| sect06_com_w4.dta | top metadata-supported module to inspect first | geography;health_need_access;shocks;survey_design | 42 |

### 4. JAM_1997_SLC_v01_M

- Official URL: https://microdata.worldbank.org/catalog/2368/get-microdata
- Local target folder: `temp/raw_downloads/JAM_1997_SLC_v01_M/`
- Access status: `manual_account_terms_download_required`; direct route: `no_direct_raw_route_access_gate_detected`

| file_name | target_reasons | candidate_categories | candidate_variable_count |
|---|---|---|---|
| REC003 | financial core file;top metadata-supported module to inspect first | health_expenditure;health_need_access | 12 |
| ANNUAL | financial core file | consumption;demographics;geography;survey_design | 11 |
| REC033 | geography/timing/design file;top metadata-supported module to inspect first | health_need_access;shocks;survey_design | 4 |
| LABORF | top metadata-supported module to inspect first | demographics;geography;health_need_access;shocks;survey_design | 22 |
| REC038 | top metadata-supported module to inspect first | health_need_access;shocks | 10 |
| REC027 | top metadata-supported module to inspect first | demographics;health_need_access | 7 |
| REC002 | top metadata-supported module to inspect first | health_need_access | 5 |
| REC005 | top metadata-supported module to inspect first | health_need_access | 3 |

### 5. KGZ_1993_KMPS_v01_M

- Official URL: https://microdata.worldbank.org/catalog/280/get-microdata
- Local target folder: `temp/raw_downloads/KGZ_1993_KMPS_v01_M/`
- Access status: `manual_account_terms_download_required`; direct route: `no_direct_raw_route_access_gate_detected`

| file_name | target_reasons | candidate_categories | candidate_variable_count |
|---|---|---|---|
| KHHLD | financial core file;top metadata-supported module to inspect first | demographics;geography;health_expenditure;health_need_access;shocks;survey_design | 102 |
| KADULT | financial core file;top metadata-supported module to inspect first | consumption;demographics;geography;health_expenditure;health_need_access;shocks;survey_design | 39 |
| KCHILD | financial core file;top metadata-supported module to inspect first | demographics;health_expenditure;health_need_access;shocks;survey_design | 26 |
| INCEXP | financial core file;top metadata-supported module to inspect first | consumption;demographics;geography;health_need_access;shocks;survey_design | 11 |
| KPRICE2 | top metadata-supported module to inspect first | geography;shocks | 909 |
| KPRICE3 | top metadata-supported module to inspect first | geography;shocks | 90 |
| KCOMM | top metadata-supported module to inspect first | demographics;geography;health_need_access;shocks | 37 |
| KINDIVH | top metadata-supported module to inspect first | demographics;survey_design | 17 |

### 6. MWI_2007-2009_MTM_v01_M

- Official URL: https://microdata.worldbank.org/catalog/3462/get-microdata
- Local target folder: `temp/raw_downloads/MWI_2007-2009_MTM_v01_M/`
- Access status: `manual_account_terms_download_required`; direct route: `no_direct_raw_route_access_gate_detected`

| file_name | target_reasons | candidate_categories | candidate_variable_count |
|---|---|---|---|
| p2_s10 | financial core file;top metadata-supported module to inspect first | demographics;health_expenditure;health_need_access;shocks;survey_design | 28 |
| p2_s11 | financial core file | demographics;health_expenditure;health_need_access;shocks;survey_design | 25 |
| hh2p3_s17 | financial core file | demographics;health_expenditure;health_need_access;shocks;survey_design | 23 |
| hh2p3_s16 | financial core file | demographics;health_expenditure;health_need_access;shocks;survey_design | 21 |
| hh2p2_s11 | financial core file | demographics;health_expenditure;health_need_access;shocks;survey_design | 17 |
| hh2p2_s9 | financial core file | demographics;health_expenditure;health_need_access;survey_design | 17 |
| p1_s4 | financial core file | consumption;survey_design | 6 |
| hh2p1_s4 | financial core file | consumption;survey_design | 5 |

### 7. MWI_2004_IHS-II_v01_M

- Official URL: https://microdata.worldbank.org/catalog/2307/get-microdata
- Local target folder: `temp/raw_downloads/MWI_2004_IHS-II_v01_M/`
- Access status: `manual_account_terms_download_required`; direct route: `no_direct_raw_route_access_gate_detected`

| file_name | target_reasons | candidate_categories | candidate_variable_count |
|---|---|---|---|
| sec_d | financial core file;geography/timing/design file;top metadata-supported module to inspect first | demographics;geography;health_expenditure;health_need_access;shocks;survey_design | 41 |
| sec_i | financial core file | consumption;demographics;geography;survey_design | 15 |
| ihs2_household | geography/timing/design file;top metadata-supported module to inspect first | consumption;demographics;geography;health_need_access;shocks;survey_design | 62 |
| sec_r | geography/timing/design file;top metadata-supported module to inspect first | demographics;geography;shocks;survey_design | 42 |
| sec_o | geography/timing/design file;top metadata-supported module to inspect first | demographics;geography;shocks;survey_design | 40 |
| sec_g | geography/timing/design file;top metadata-supported module to inspect first | demographics;geography;survey_design | 35 |
| sec_s | geography/timing/design file;top metadata-supported module to inspect first | demographics;geography;shocks;survey_design | 31 |
| sec_ac | geography/timing/design file;top metadata-supported module to inspect first | demographics;geography;health_need_access;survey_design | 30 |

### 8. NPL_2010_LSS-III_v01_M

- Official URL: https://microdata.worldbank.org/catalog/1000/get-microdata
- Local target folder: `temp/raw_downloads/NPL_2010_LSS-III_v01_M/`
- Access status: `manual_account_terms_download_required`; direct route: `no_direct_raw_route_access_gate_detected`

| file_name | target_reasons | candidate_categories | candidate_variable_count |
|---|---|---|---|
| FINAL_PREF | financial core file;geography/timing/design file;top metadata-supported module to inspect first | consumption;demographics;geography;shocks;survey_design | 106 |
| S08 | financial core file;geography/timing/design file;top metadata-supported module to inspect first | health_expenditure;health_need_access;survey_design | 19 |
| S19 | financial core file;geography/timing/design file | consumption;demographics;health_need_access;shocks;survey_design | 13 |
| S13E2 | financial core file | consumption;survey_design | 2 |
| S00 | geography/timing/design file;top metadata-supported module to inspect first | demographics;geography;health_need_access;shocks;survey_design | 32 |
| S13A1 | geography/timing/design file;top metadata-supported module to inspect first | geography;shocks;survey_design | 19 |
| anthro | geography/timing/design file;top metadata-supported module to inspect first | demographics;survey_design | 16 |
| S21 | geography/timing/design file;top metadata-supported module to inspect first | demographics;geography;survey_design | 14 |

### 9. NGA_2012_GHSP-W2_v02_M

- Official URL: https://microdata.worldbank.org/catalog/1952/get-microdata
- Local target folder: `temp/raw_downloads/NGA_2012_GHSP-W2_v02_M/`
- Access status: `manual_account_terms_download_required`; direct route: `no_direct_raw_route_access_gate_detected`

| file_name | target_reasons | candidate_categories | candidate_variable_count |
|---|---|---|---|
| sect4a_harvestw2 | financial core file;top metadata-supported module to inspect first | demographics;geography;health_expenditure;health_need_access;survey_design | 40 |
| cons_agg_wave2_visit1 | financial core file | consumption;demographics;geography;health_need_access;shocks;survey_design | 14 |
| cons_agg_wave2_visit2 | financial core file | consumption;demographics;geography;health_need_access;shocks;survey_design | 14 |
| secta1_harvestw2 | top metadata-supported module to inspect first | geography;shocks;survey_design | 69 |
| sect11b1_plantingw2 | top metadata-supported module to inspect first | geography;shocks;survey_design | 58 |
| sect11h_plantingw2 | top metadata-supported module to inspect first | geography;health_need_access;shocks;survey_design | 50 |
| secta3_harvestw2 | top metadata-supported module to inspect first | geography;health_need_access;shocks;survey_design | 33 |
| sect11d_plantingw2 | top metadata-supported module to inspect first | geography;health_need_access;shocks;survey_design | 31 |

### 10. NGA_2015_GHSP-W3_v02_M

- Official URL: https://microdata.worldbank.org/catalog/2734/get-microdata
- Local target folder: `temp/raw_downloads/NGA_2015_GHSP-W3_v02_M/`
- Access status: `manual_account_terms_download_required`; direct route: `no_direct_raw_route_access_gate_detected`

| file_name | target_reasons | candidate_categories | candidate_variable_count |
|---|---|---|---|
| sect4a_harvestw3 | financial core file;top metadata-supported module to inspect first | demographics;geography;health_expenditure;health_need_access;survey_design | 37 |
| cons_agg_wave3_visit1 | financial core file | consumption;demographics;geography;health_need_access;shocks;survey_design | 14 |
| cons_agg_wave3_visit2 | financial core file | consumption;demographics;geography;health_need_access;shocks;survey_design | 14 |
| sect11b1_plantingw3 | top metadata-supported module to inspect first | geography;shocks;survey_design | 66 |
| secta3ii_harvestw3 | top metadata-supported module to inspect first | demographics;geography;shocks;survey_design | 55 |
| secta1_harvestw3 | top metadata-supported module to inspect first | geography;shocks;survey_design | 49 |
| secta11d_harvestw3 | top metadata-supported module to inspect first | geography;health_need_access;shocks;survey_design | 47 |
| secta2_harvestw3 | top metadata-supported module to inspect first | geography;shocks;survey_design | 37 |


## Manual Procedure

1. Open the official URL for a dataset and complete the required World Bank account, registration, request, or terms workflow.
2. Download the complete original raw package plus all questionnaires, codebooks, data dictionaries, survey-design files, and geography/GPS files if offered.
3. Place the original archives or files in the listed `temp/raw_downloads/<IDNO>/` folder. Keep source filenames intact.
4. Run the post-download commands listed in `temp/first_batch_manual_download_handoff.csv`.
5. Promote no country-wave until raw schemas, values, labels, units, recall periods, missing codes, merge keys, geography, and timing have passed the verification workbook.

## Guardrails

- Candidate files are metadata-derived inspection targets, not verified raw files.
- Access-page snapshots are evidence of the access workflow, not raw microdata.
- Do not create `temp/harmonization_recipe.csv`, clean `data/` outputs, outcomes, climate links, models, causal estimates, or policy simulations from this packet alone.

## Machine-Readable Outputs

- `temp/first_batch_manual_download_handoff.csv`
- `temp/first_batch_manual_download_file_queue.csv`
- `result/first_batch_manual_download_handoff_summary.csv`
