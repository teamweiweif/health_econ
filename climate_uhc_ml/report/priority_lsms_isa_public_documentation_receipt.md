# Priority LSMS-ISA Public Documentation Receipt

Status: public documentation and metadata receipt for the refocused 19-wave
LSMS/LSMS-ISA acquisition queue. This layer saves official get-microdata pages,
catalog JSON, variable JSON, DDI/XML, JSON metadata, data dictionaries, and
related-material pages where available. It does not download raw microdata and
does not bypass official account, registration, terms, or request gates.

## Summary

| Metric | Value | Interpretation |
|---|---:|---|
| priority_lsms_isa_public_documentation_dataset_rows | 19 | Refocused LSMS/ISA queue datasets with public documentation receipt rows. |
| priority_lsms_isa_public_documentation_resource_rows | 133 | Public documentation and metadata resources attempted or reused for the refocused queue. |
| priority_lsms_isa_public_documentation_saved_rows | 133 | Public documentation resources saved or reused locally. |
| priority_lsms_isa_public_documentation_failed_rows | 0 | Public documentation resource requests that failed. |
| priority_lsms_isa_public_documentation_core_complete_dataset_rows | 19 | Datasets with all required public documentation and metadata resource types saved. |
| priority_lsms_isa_public_documentation_access_gate_rows | 19 | Datasets whose official get-microdata page still shows account, registration, terms, or request language. |
| priority_lsms_isa_public_documentation_catalog_digest_rows | 19 | Compact official catalog metadata digest rows extracted from saved JSON snapshots. |
| priority_lsms_isa_public_documentation_file_inventory_rows | 1597 | Official DDI file-description rows extracted for Web-GPT-readable file planning. |
| priority_lsms_isa_public_documentation_saved_bytes | 114320665 | Total bytes in saved or reused public documentation snapshots. |
| priority_lsms_isa_public_documentation_handoff_readmes_written | 19 | Per-wave public documentation handoff files written. |
| priority_lsms_isa_public_documentation_data_write_status | blocked_no_promoted_rows | Public documentation receipt is not sufficient to write analysis datasets to data/. |
| modeling_gate_status | blocked | Models remain blocked until raw-backed promotion thresholds and accepted climate linkage pass. |
| priority_lsms_isa_public_documentation_receipt_status_saved_existing | 133 | Resource receipt status count. |
| priority_lsms_isa_public_documentation_resource_type_catalog_idno_json | 19 | Resource type count. |
| priority_lsms_isa_public_documentation_resource_type_data_dictionary_html | 19 | Resource type count. |
| priority_lsms_isa_public_documentation_resource_type_ddi_metadata | 19 | Resource type count. |
| priority_lsms_isa_public_documentation_resource_type_get_microdata_html | 19 | Resource type count. |
| priority_lsms_isa_public_documentation_resource_type_json_metadata | 19 | Resource type count. |
| priority_lsms_isa_public_documentation_resource_type_related_materials_html | 19 | Resource type count. |
| priority_lsms_isa_public_documentation_resource_type_variables_idno_json | 19 | Resource type count. |
| priority_lsms_isa_public_documentation_dataset_status_complete_core_public_documentation_receipt | 19 | Dataset-level public documentation receipt status count. |
| priority_lsms_isa_public_documentation_queue_role_core_replacement_primary | 2 | Dataset count by refocused queue role. |
| priority_lsms_isa_public_documentation_queue_role_core_selected_lsms_isa_aligned | 8 | Dataset count by refocused queue role. |
| priority_lsms_isa_public_documentation_queue_role_replacement_backup_wave | 6 | Dataset count by refocused queue role. |
| priority_lsms_isa_public_documentation_queue_role_sixth_country_backup_candidate | 3 | Dataset count by refocused queue role. |

## Dataset Receipt

| download_priority_order | queue_role | idno | country | wave | public_documentation_receipt_status | missing_core_resource_types | access_gate_detected |
|---|---|---|---|---|---|---|---|
| 1 | core_selected_lsms_isa_aligned | ETH_2021_ESPS-W5_v02_M | Ethiopia | 2021-2022 | complete_core_public_documentation_receipt |  | 1 |
| 2 | core_selected_lsms_isa_aligned | ETH_2018_ESS_v04_M | Ethiopia | 2018-2019 | complete_core_public_documentation_receipt |  | 1 |
| 3 | core_replacement_primary | MWI_2004_IHS-II_v01_M | Malawi | 2004-2005 | complete_core_public_documentation_receipt |  | 1 |
| 4 | core_selected_lsms_isa_aligned | NGA_2012_GHSP-W2_v02_M | Nigeria | 2012-2013 | complete_core_public_documentation_receipt |  | 1 |
| 5 | core_selected_lsms_isa_aligned | NGA_2015_GHSP-W3_v02_M | Nigeria | 2015-2016 | complete_core_public_documentation_receipt |  | 1 |
| 6 | core_selected_lsms_isa_aligned | NGA_2010_GHSP-W1_v03_M | Nigeria | 2010-2011 | complete_core_public_documentation_receipt |  | 1 |
| 7 | core_selected_lsms_isa_aligned | TZA_2008_NPS-R1_v03_M | Tanzania | 2008-2009 | complete_core_public_documentation_receipt |  | 1 |
| 8 | core_selected_lsms_isa_aligned | TZA_2010_NPS-R2_v03_M | Tanzania | 2010-2011 | complete_core_public_documentation_receipt |  | 1 |
| 9 | core_selected_lsms_isa_aligned | TZA_2012_NPS-R3_v01_M | Tanzania | 2012-2013 | complete_core_public_documentation_receipt |  | 1 |
| 10 | core_replacement_primary | UGA_2019_UNPS_v03_M | Uganda | 2019-2020 | complete_core_public_documentation_receipt |  | 1 |
| 11 | sixth_country_backup_candidate | JAM_1997_SLC_v01_M | Jamaica | 1997 | complete_core_public_documentation_receipt |  | 1 |
| 12 | sixth_country_backup_candidate | KGZ_1993_KMPS_v01_M | Kyrgyz Republic | 1993 | complete_core_public_documentation_receipt |  | 1 |
| 13 | sixth_country_backup_candidate | NPL_2010_LSS-III_v01_M | Nepal | 2010-2011 | complete_core_public_documentation_receipt |  | 1 |
| 14 | replacement_backup_wave | MWI_2019_IHS-V_v06_M | Malawi | 2019-2020 | complete_core_public_documentation_receipt |  | 1 |
| 15 | replacement_backup_wave | MWI_2016_IHS-IV_v04_M | Malawi | 2016-2017 | complete_core_public_documentation_receipt |  | 1 |
| 16 | replacement_backup_wave | MWI_2010_IHS-III_v01_M | Malawi | 2010-2011 | complete_core_public_documentation_receipt |  | 1 |
| 17 | replacement_backup_wave | UGA_2011_UNPS_v02_M | Uganda | 2011-2012 | complete_core_public_documentation_receipt |  | 1 |
| 18 | replacement_backup_wave | UGA_2018_UNPS_v02_M | Uganda | 2018-2019 | complete_core_public_documentation_receipt |  | 1 |
| 19 | replacement_backup_wave | UGA_2015_UNPS_v02_M | Uganda | 2015-2016 | complete_core_public_documentation_receipt |  | 1 |

## Catalog Digest

| download_priority_order | idno | title | year_start | year_end | repositoryid | varcount | data_access_type | metadata_status |
|---|---|---|---|---|---|---|---|---|
| 1 | ETH_2021_ESPS-W5_v02_M | Socio-Economic Panel Survey 2021-2022 | 2021 | 2022 | lsms | 2587 | public | catalog_json_parsed |
| 2 | ETH_2018_ESS_v04_M | Socioeconomic Survey 2018-2019 | 2018 | 2019 | lsms | 2550 | public | catalog_json_parsed |
| 3 | MWI_2004_IHS-II_v01_M | Second Integrated Household Survey 2004-2005 | 2004 | 2005 | lsms | 1901 | public | catalog_json_parsed |
| 4 | NGA_2012_GHSP-W2_v02_M | General Household Survey, Panel 2012-2013, Wave 2 | 2012 | 2013 | lsms | 3016 | public | catalog_json_parsed |
| 5 | NGA_2015_GHSP-W3_v02_M | General Household Survey, Panel 2015-2016, Wave 3 | 2015 | 2016 | lsms | 2907 | public | catalog_json_parsed |
| 6 | NGA_2010_GHSP-W1_v03_M | General Household Survey, Panel 2010-2011, Wave 1 | 2010 | 2011 | lsms | 2596 | public | catalog_json_parsed |
| 7 | TZA_2008_NPS-R1_v03_M | National Panel Survey 2008-2009, Wave 1 | 2008 | 2009 | lsms | 2198 | public | catalog_json_parsed |
| 8 | TZA_2010_NPS-R2_v03_M | National Panel Survey 2010-2011, Wave 2 | 2010 | 2011 | lsms | 2062 | public | catalog_json_parsed |
| 9 | TZA_2012_NPS-R3_v01_M | National Panel Survey 2012-2013, Wave 3 | 2012 | 2013 | lsms | 2139 | public | catalog_json_parsed |
| 10 | UGA_2019_UNPS_v03_M | National Panel Survey 2019-2020 | 2019 | 2020 | lsms | 1963 | public | catalog_json_parsed |
| 11 | JAM_1997_SLC_v01_M | Survey of Living Conditions 1997 | 1997 | 1997 | lsms | 881 | remote | catalog_json_parsed |
| 12 | KGZ_1993_KMPS_v01_M | Multipurpose Poverty Survey 1993 | 1993 | 1993 | lsms | 4712 | public | catalog_json_parsed |
| 13 | NPL_2010_LSS-III_v01_M | Living Standards Survey 2010-2011, Third Round | 2010 | 2011 | lsms | 1361 | remote | catalog_json_parsed |
| 14 | MWI_2019_IHS-V_v06_M | Fifth Integrated Household Survey 2019-2020 | 2019 | 2020 | lsms | 3500 | public | catalog_json_parsed |
| 15 | MWI_2016_IHS-IV_v04_M | Fourth Integrated Household Survey 2016-2017 | 2016 | 2017 | lsms | 3363 | public | catalog_json_parsed |
| 16 | MWI_2010_IHS-III_v01_M | Third Integrated Household Survey 2010-2011 | 2010 | 2011 | lsms | 3144 | public | catalog_json_parsed |
| 17 | UGA_2011_UNPS_v02_M | National Panel Survey 2011-2012 | 2011 | 2012 | lsms | 1836 | public | catalog_json_parsed |
| 18 | UGA_2018_UNPS_v02_M | Uganda National Panel Survey 2018-2019 | 2018 | 2019 | lsms | 1934 | public | catalog_json_parsed |
| 19 | UGA_2015_UNPS_v02_M | National Panel Survey 2015-2016 | 2015 | 2016 | lsms | 1890 | public | catalog_json_parsed |

## Official DDI File Inventory Preview

| download_priority_order | idno | file_id | file_name | case_quantity | variable_quantity |
|---|---|---|---|---|---|
| 1 | ETH_2021_ESPS-W5_v02_M | F1 | sect_cover_hh_w5.dta | 4959 | 25 |
| 1 | ETH_2021_ESPS-W5_v02_M | F2 | sect1_hh_w5.dta | 25374 | 63 |
| 1 | ETH_2021_ESPS-W5_v02_M | F3 | sect2_hh_w5.dta | 22688 | 43 |
| 1 | ETH_2021_ESPS-W5_v02_M | F4 | sect3_hh_w5.dta | 22688 | 69 |
| 1 | ETH_2021_ESPS-W5_v02_M | F5 | sect3b_hh_w5.dta | 22688 | 23 |
| 1 | ETH_2021_ESPS-W5_v02_M | F6 | sect4_hh_w5.dta | 22688 | 82 |
| 1 | ETH_2021_ESPS-W5_v02_M | F7 | sect5a_hh_w5.dta | 22688 | 91 |
| 1 | ETH_2021_ESPS-W5_v02_M | F8 | sect5b_hh_w5.dta | 22688 | 60 |
| 1 | ETH_2021_ESPS-W5_v02_M | F9 | sect6a_hh_w5.dta | 366966 | 28 |
| 1 | ETH_2021_ESPS-W5_v02_M | F10 | sect6b2_hh_w5.dta | 4959 | 13 |
| 1 | ETH_2021_ESPS-W5_v02_M | F11 | sect6b3_hh_w5.dta | 7692 | 15 |
| 1 | ETH_2021_ESPS-W5_v02_M | F12 | sect6b4_hh_w5.dta | 39672 | 19 |
| 1 | ETH_2021_ESPS-W5_v02_M | F13 | sect6c_hh_w5.dta | 22688 | 47 |
| 1 | ETH_2021_ESPS-W5_v02_M | F14 | sect7a_hh_w5.dta | 59508 | 15 |
| 1 | ETH_2021_ESPS-W5_v02_M | F15 | sect7b_hh_w5.dta | 64467 | 15 |
| 1 | ETH_2021_ESPS-W5_v02_M | F16 | sect8_hh_w5.dta | 4959 | 24 |
| 1 | ETH_2021_ESPS-W5_v02_M | F17 | sect9_hh_w5.dta | 94221 | 25 |
| 1 | ETH_2021_ESPS-W5_v02_M | F18 | sect10a_hh_w5.dta | 4959 | 69 |
| 1 | ETH_2021_ESPS-W5_v02_M | F19 | sect11_hh_w5.dta | 183483 | 17 |
| 1 | ETH_2021_ESPS-W5_v02_M | F20 | sect12a_hh_w5.dta | 4959 | 20 |
| 1 | ETH_2021_ESPS-W5_v02_M | F21 | sect12b1_hh_w5.dta | 1551 | 68 |
| 1 | ETH_2021_ESPS-W5_v02_M | F22 | sect12b2_hh_w5.dta | 3518 | 16 |
| 1 | ETH_2021_ESPS-W5_v02_M | F23 | sect12c_hh_w5.dta | 1096 | 32 |
| 1 | ETH_2021_ESPS-W5_v02_M | F24 | sect12c_q1_hh_w5.dta | 2875 | 13 |
| 1 | ETH_2021_ESPS-W5_v02_M | F25 | sect12d_hh_w5.dta | 46000 | 21 |
| 1 | ETH_2021_ESPS-W5_v02_M | F26 | sect12e_hh_w5.dta | 49590 | 27 |
| 1 | ETH_2021_ESPS-W5_v02_M | F27 | sect12f_hh_w5.dta | 4959 | 17 |
| 1 | ETH_2021_ESPS-W5_v02_M | F28 | sect13_hh_w5.dta | 69426 | 21 |
| 1 | ETH_2021_ESPS-W5_v02_M | F29 | sect14_hh_w5.dta | 14877 | 30 |
| 1 | ETH_2021_ESPS-W5_v02_M | F30 | sect15a_hh_w5.dta | 4959 | 29 |
| 1 | ETH_2021_ESPS-W5_v02_M | F31 | sect15b_hh_w5.dta | 1033 | 30 |
| 1 | ETH_2021_ESPS-W5_v02_M | F32 | sect01a_com_w5.dta | 433 | 11 |
| 1 | ETH_2021_ESPS-W5_v02_M | F33 | sect01b_com_w5.dta | 433 | 23 |
| 1 | ETH_2021_ESPS-W5_v02_M | F34 | sect02_com_w5.dta | 2335 | 19 |
| 1 | ETH_2021_ESPS-W5_v02_M | F35 | sect03_com_w5.dta | 433 | 36 |
| 1 | ETH_2021_ESPS-W5_v02_M | F36 | sect04_com_w5.dta | 433 | 106 |
| 1 | ETH_2021_ESPS-W5_v02_M | F37 | sect05_com_w5.dta | 433 | 27 |
| 1 | ETH_2021_ESPS-W5_v02_M | F38 | sect06_com_w5.dta | 433 | 69 |
| 1 | ETH_2021_ESPS-W5_v02_M | F39 | sect07_com_w5.dta | 668 | 18 |
| 1 | ETH_2021_ESPS-W5_v02_M | F40 | sect08_com_w5.dta | 4763 | 34 |

## Failed Or Missing Required Resources

No failed or missing required public documentation resources.

## Guardrails

- These snapshots support acquisition, file mapping, and pre-review only.
- They are not raw package receipts and do not verify values or row-level data.
- `data/` remains closed for these waves until complete original raw packages,
  manual value/key/unit/skip-pattern checks, survey-design checks,
  timing/geography checks, and accepted CHIRPS/ERA5 linkage pass.

## Machine-Readable Outputs

- `temp/priority_lsms_isa_public_documentation_receipt.csv`
- `temp/priority_lsms_isa_public_documentation_dataset_receipt.csv`
- `temp/priority_lsms_isa_public_documentation_catalog_digest.csv`
- `temp/priority_lsms_isa_public_documentation_file_inventory.csv`
- `result/priority_lsms_isa_public_documentation_receipt_summary.csv`
