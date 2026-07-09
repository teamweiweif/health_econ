# Priority Download Execution Packet

Status: manual credentialed-download execution layer for the 13-wave
priority/backup campaign. This packet does not download restricted microdata,
does not bypass account, terms, or Data Access Agreement gates, and does not
promote any data. It gives the exact official route, target folder, core-file
acceptance matrix, and post-download commands needed to move from metadata
candidates to raw-backed promotion review.

## Summary

| Metric | Value | Interpretation |
|---|---:|---|
| priority_download_execution_packet_rows | 13 | Dataset-level manual credentialed download execution packets. |
| priority_download_execution_priority_10_wave_rows | 10 | Phase-1 priority waves covered by execution packets. |
| priority_download_execution_backup_wave_rows | 3 | Sixth-country backup waves covered by execution packets. |
| priority_download_execution_distinct_countries | 8 | Distinct countries covered by execution packets. |
| priority_download_execution_core_file_rows | 156 | Core file/module acceptance rows across execution packets. |
| priority_download_execution_first_pass_requirement_rows | 104 | First-pass requirement rows carried into execution packets. |
| priority_download_execution_first_pass_variable_rows | 465 | First-pass selected variable rows carried into execution packets. |
| priority_download_execution_raw_package_received_rows | 0 | Execution-packet datasets with any original package receipt. |
| priority_download_execution_handoff_readmes_written | 13 | Per-wave download execution handoff files written. |
| modeling_gate_status | blocked | Models remain blocked until raw-backed promotion thresholds and accepted climate linkage pass. |
| download_execution_status_ready_for_manual_credentialed_download_no_raw_receipt | 13 | Dataset download execution status count. |
| download_file_acceptance_status_blocked_no_raw_or_archive_file | 156 | Core file acceptance status count. |

## Dataset Status

| Download execution status | Count |
|---|---:|
| `ready_for_manual_credentialed_download_no_raw_receipt` | 13 |

## Core File Acceptance Status

| Core file status | Count |
|---|---:|
| `blocked_no_raw_or_archive_file` | 156 |

## Execution Queue

| download_order | idno | country | wave | campaign_phase | official_get_microdata_url | local_target_folder | download_execution_status |
|---|---|---|---|---|---|---|---|
| 1 | ETH_2021_ESPS-W5_v02_M | Ethiopia | 2021-2022 | phase_1_double_failure_10_wave_base | https://microdata.worldbank.org/catalog/6161/get-microdata | temp/raw_downloads/ETH_2021_ESPS-W5_v02_M/ | ready_for_manual_credentialed_download_no_raw_receipt |
| 2 | ETH_2018_ESS_v04_M | Ethiopia | 2018-2019 | phase_1_double_failure_10_wave_base | https://microdata.worldbank.org/catalog/3823/get-microdata | temp/raw_downloads/ETH_2018_ESS_v04_M/ | ready_for_manual_credentialed_download_no_raw_receipt |
| 3 | MWI_2007-2009_MTM_v01_M | Malawi | 2007-2009 | phase_1_double_failure_10_wave_base | https://microdata.worldbank.org/catalog/3462/get-microdata | temp/raw_downloads/MWI_2007-2009_MTM_v01_M/ | ready_for_manual_credentialed_download_no_raw_receipt |
| 4 | NGA_2012_GHSP-W2_v02_M | Nigeria | 2012-2013 | phase_1_double_failure_10_wave_base | https://microdata.worldbank.org/catalog/1952/get-microdata | temp/raw_downloads/NGA_2012_GHSP-W2_v02_M/ | ready_for_manual_credentialed_download_no_raw_receipt |
| 5 | NGA_2015_GHSP-W3_v02_M | Nigeria | 2015-2016 | phase_1_double_failure_10_wave_base | https://microdata.worldbank.org/catalog/2734/get-microdata | temp/raw_downloads/NGA_2015_GHSP-W3_v02_M/ | ready_for_manual_credentialed_download_no_raw_receipt |
| 6 | NGA_2010_GHSP-W1_v03_M | Nigeria | 2010-2011 | phase_1_double_failure_10_wave_base | https://microdata.worldbank.org/catalog/1002/get-microdata | temp/raw_downloads/NGA_2010_GHSP-W1_v03_M/ | ready_for_manual_credentialed_download_no_raw_receipt |
| 7 | TZA_2008_NPS-R1_v03_M | Tanzania | 2008-2009 | phase_1_double_failure_10_wave_base | https://microdata.worldbank.org/catalog/76/get-microdata | temp/raw_downloads/TZA_2008_NPS-R1_v03_M/ | ready_for_manual_credentialed_download_no_raw_receipt |
| 8 | TZA_2010_NPS-R2_v03_M | Tanzania | 2010-2011 | phase_1_double_failure_10_wave_base | https://microdata.worldbank.org/catalog/1050/get-microdata | temp/raw_downloads/TZA_2010_NPS-R2_v03_M/ | ready_for_manual_credentialed_download_no_raw_receipt |
| 9 | TZA_2012_NPS-R3_v01_M | Tanzania | 2012-2013 | phase_1_double_failure_10_wave_base | https://microdata.worldbank.org/catalog/2252/get-microdata | temp/raw_downloads/TZA_2012_NPS-R3_v01_M/ | ready_for_manual_credentialed_download_no_raw_receipt |
| 10 | UGA_2014_SAGE-EL_v01_M | Uganda | 2014 | phase_1_double_failure_10_wave_base | https://microdata.worldbank.org/catalog/2654/get-microdata | temp/raw_downloads/UGA_2014_SAGE-EL_v01_M/ | ready_for_manual_credentialed_download_no_raw_receipt |
| 11 | JAM_1997_SLC_v01_M | Jamaica | 1997 | phase_2_sixth_country_financial_protection_backup | https://microdata.worldbank.org/catalog/2368/get-microdata | temp/raw_downloads/JAM_1997_SLC_v01_M/ | ready_for_manual_credentialed_download_no_raw_receipt |
| 12 | KGZ_1993_KMPS_v01_M | Kyrgyz Republic | 1993 | phase_2_sixth_country_financial_protection_backup | https://microdata.worldbank.org/catalog/280/get-microdata | temp/raw_downloads/KGZ_1993_KMPS_v01_M/ | ready_for_manual_credentialed_download_no_raw_receipt |
| 13 | NPL_2010_LSS-III_v01_M | Nepal | 2010-2011 | phase_2_sixth_country_financial_protection_backup | https://microdata.worldbank.org/catalog/1000/get-microdata | temp/raw_downloads/NPL_2010_LSS-III_v01_M/ | ready_for_manual_credentialed_download_no_raw_receipt |

## Core File Preview

| download_order | idno | core_file_rank | metadata_file_name | expected_local_name_patterns | file_acceptance_status |
|---|---|---|---|---|---|
| 1 | ETH_2021_ESPS-W5_v02_M | 1 | sect3_hh_w5.dta | sect3_hh_w5.dta;sect3_hh_w5.*;*sect3_hh_w5* | blocked_no_raw_or_archive_file |
| 1 | ETH_2021_ESPS-W5_v02_M | 2 | sect04_com_w5.dta | sect04_com_w5.dta;sect04_com_w5.*;*sect04_com_w5* | blocked_no_raw_or_archive_file |
| 1 | ETH_2021_ESPS-W5_v02_M | 3 | sect06_com_w5.dta | sect06_com_w5.dta;sect06_com_w5.*;*sect06_com_w5* | blocked_no_raw_or_archive_file |
| 1 | ETH_2021_ESPS-W5_v02_M | 4 | sect11_com_w5.dta | sect11_com_w5.dta;sect11_com_w5.*;*sect11_com_w5* | blocked_no_raw_or_archive_file |
| 1 | ETH_2021_ESPS-W5_v02_M | 5 | sect3_pp_w5.dta | sect3_pp_w5.dta;sect3_pp_w5.*;*sect3_pp_w5* | blocked_no_raw_or_archive_file |
| 1 | ETH_2021_ESPS-W5_v02_M | 6 | sect4_pp_w5.dta | sect4_pp_w5.dta;sect4_pp_w5.*;*sect4_pp_w5* | blocked_no_raw_or_archive_file |
| 1 | ETH_2021_ESPS-W5_v02_M | 7 | sect7_pp_w5.dta | sect7_pp_w5.dta;sect7_pp_w5.*;*sect7_pp_w5* | blocked_no_raw_or_archive_file |
| 1 | ETH_2021_ESPS-W5_v02_M | 8 | sect9_ph_w5.dta | sect9_ph_w5.dta;sect9_ph_w5.*;*sect9_ph_w5* | blocked_no_raw_or_archive_file |
| 1 | ETH_2021_ESPS-W5_v02_M | 9 | sect11_ph_w5.dta | sect11_ph_w5.dta;sect11_ph_w5.*;*sect11_ph_w5* | blocked_no_raw_or_archive_file |
| 1 | ETH_2021_ESPS-W5_v02_M | 10 | sect8_2_ls_w5.dta | sect8_2_ls_w5.dta;sect8_2_ls_w5.*;*sect8_2_ls_w5* | blocked_no_raw_or_archive_file |
| 1 | ETH_2021_ESPS-W5_v02_M | 11 | sect8_3_ls_w5.dta | sect8_3_ls_w5.dta;sect8_3_ls_w5.*;*sect8_3_ls_w5* | blocked_no_raw_or_archive_file |
| 1 | ETH_2021_ESPS-W5_v02_M | 12 | eth_householdgeovariables_y5.dta | eth_householdgeovariables_y5.dta;eth_householdgeovariables_y5.*;*eth_householdgeovariables_y5* | blocked_no_raw_or_archive_file |
| 2 | ETH_2018_ESS_v04_M | 1 | sect3_hh_w4.dta | sect3_hh_w4.dta;sect3_hh_w4.*;*sect3_hh_w4* | blocked_no_raw_or_archive_file |
| 2 | ETH_2018_ESS_v04_M | 2 | sect5b2_hh_w4.dta | sect5b2_hh_w4.dta;sect5b2_hh_w4.*;*sect5b2_hh_w4* | blocked_no_raw_or_archive_file |
| 2 | ETH_2018_ESS_v04_M | 3 | sect10c_hh_w4.dta | sect10c_hh_w4.dta;sect10c_hh_w4.*;*sect10c_hh_w4* | blocked_no_raw_or_archive_file |
| 2 | ETH_2018_ESS_v04_M | 4 | sect8_2_ls_w4.dta | sect8_2_ls_w4.dta;sect8_2_ls_w4.*;*sect8_2_ls_w4* | blocked_no_raw_or_archive_file |
| 2 | ETH_2018_ESS_v04_M | 5 | sect8_3_ls_w4.dta | sect8_3_ls_w4.dta;sect8_3_ls_w4.*;*sect8_3_ls_w4* | blocked_no_raw_or_archive_file |
| 2 | ETH_2018_ESS_v04_M | 6 | sect8_4_ls_w4.dta | sect8_4_ls_w4.dta;sect8_4_ls_w4.*;*sect8_4_ls_w4* | blocked_no_raw_or_archive_file |
| 2 | ETH_2018_ESS_v04_M | 7 | sect9_ph_w4.dta | sect9_ph_w4.dta;sect9_ph_w4.*;*sect9_ph_w4* | blocked_no_raw_or_archive_file |
| 2 | ETH_2018_ESS_v04_M | 8 | sect11_ph_w4.dta | sect11_ph_w4.dta;sect11_ph_w4.*;*sect11_ph_w4* | blocked_no_raw_or_archive_file |
| 2 | ETH_2018_ESS_v04_M | 9 | sect3_pp_w4.dta | sect3_pp_w4.dta;sect3_pp_w4.*;*sect3_pp_w4* | blocked_no_raw_or_archive_file |
| 2 | ETH_2018_ESS_v04_M | 10 | sect4_pp_w4.dta | sect4_pp_w4.dta;sect4_pp_w4.*;*sect4_pp_w4* | blocked_no_raw_or_archive_file |
| 2 | ETH_2018_ESS_v04_M | 11 | sect04_com_w4.dta | sect04_com_w4.dta;sect04_com_w4.*;*sect04_com_w4* | blocked_no_raw_or_archive_file |
| 2 | ETH_2018_ESS_v04_M | 12 | sect06_com_w4.dta | sect06_com_w4.dta;sect06_com_w4.*;*sect06_com_w4* | blocked_no_raw_or_archive_file |
| 3 | MWI_2007-2009_MTM_v01_M | 1 | hh2_cmty | hh2_cmty;hh2_cmty.*;hh2_cmty.dta;hh2_cmty.sav;hh2_cmty.por;hh2_cmty.sas7bdat;hh2_cmty.xpt;hh2_cmty.csv;*hh2_cmty* | blocked_no_raw_or_archive_file |
| 3 | MWI_2007-2009_MTM_v01_M | 2 | hh2p2_s10 | hh2p2_s10;hh2p2_s10.*;hh2p2_s10.dta;hh2p2_s10.sav;hh2p2_s10.por;hh2p2_s10.sas7bdat;hh2p2_s10.xpt;hh2p2_s10.csv;*hh2p2... | blocked_no_raw_or_archive_file |
| 3 | MWI_2007-2009_MTM_v01_M | 3 | hh2p2_s12 | hh2p2_s12;hh2p2_s12.*;hh2p2_s12.dta;hh2p2_s12.sav;hh2p2_s12.por;hh2p2_s12.sas7bdat;hh2p2_s12.xpt;hh2p2_s12.csv;*hh2p2... | blocked_no_raw_or_archive_file |
| 3 | MWI_2007-2009_MTM_v01_M | 4 | hh2p3_s15 | hh2p3_s15;hh2p3_s15.*;hh2p3_s15.dta;hh2p3_s15.sav;hh2p3_s15.por;hh2p3_s15.sas7bdat;hh2p3_s15.xpt;hh2p3_s15.csv;*hh2p3... | blocked_no_raw_or_archive_file |
| 3 | MWI_2007-2009_MTM_v01_M | 5 | hh2p3_s17 | hh2p3_s17;hh2p3_s17.*;hh2p3_s17.dta;hh2p3_s17.sav;hh2p3_s17.por;hh2p3_s17.sas7bdat;hh2p3_s17.xpt;hh2p3_s17.csv;*hh2p3... | blocked_no_raw_or_archive_file |
| 3 | MWI_2007-2009_MTM_v01_M | 6 | hh3p3_s15 | hh3p3_s15;hh3p3_s15.*;hh3p3_s15.dta;hh3p3_s15.sav;hh3p3_s15.por;hh3p3_s15.sas7bdat;hh3p3_s15.xpt;hh3p3_s15.csv;*hh3p3... | blocked_no_raw_or_archive_file |
| 3 | MWI_2007-2009_MTM_v01_M | 7 | p2_s9 | p2_s9;p2_s9.*;p2_s9.dta;p2_s9.sav;p2_s9.por;p2_s9.sas7bdat;p2_s9.xpt;p2_s9.csv;*p2_s9* | blocked_no_raw_or_archive_file |
| 3 | MWI_2007-2009_MTM_v01_M | 8 | p2_s10 | p2_s10;p2_s10.*;p2_s10.dta;p2_s10.sav;p2_s10.por;p2_s10.sas7bdat;p2_s10.xpt;p2_s10.csv;*p2_s10* | blocked_no_raw_or_archive_file |
| 3 | MWI_2007-2009_MTM_v01_M | 9 | p2_s11 | p2_s11;p2_s11.*;p2_s11.dta;p2_s11.sav;p2_s11.por;p2_s11.sas7bdat;p2_s11.xpt;p2_s11.csv;*p2_s11* | blocked_no_raw_or_archive_file |
| 3 | MWI_2007-2009_MTM_v01_M | 10 | p2_s13 | p2_s13;p2_s13.*;p2_s13.dta;p2_s13.sav;p2_s13.por;p2_s13.sas7bdat;p2_s13.xpt;p2_s13.csv;*p2_s13* | blocked_no_raw_or_archive_file |
| 3 | MWI_2007-2009_MTM_v01_M | 11 | p2_s14a | p2_s14a;p2_s14a.*;p2_s14a.dta;p2_s14a.sav;p2_s14a.por;p2_s14a.sas7bdat;p2_s14a.xpt;p2_s14a.csv;*p2_s14a* | blocked_no_raw_or_archive_file |
| 3 | MWI_2007-2009_MTM_v01_M | 12 | pi_s5a | pi_s5a;pi_s5a.*;pi_s5a.dta;pi_s5a.sav;pi_s5a.por;pi_s5a.sas7bdat;pi_s5a.xpt;pi_s5a.csv;*pi_s5a* | blocked_no_raw_or_archive_file |
| 4 | NGA_2012_GHSP-W2_v02_M | 1 | NGA_HouseholdGeovars_Y2 | NGA_HouseholdGeovars_Y2;NGA_HouseholdGeovars_Y2.*;NGA_HouseholdGeovars_Y2.dta;NGA_HouseholdGeovars_Y2.sav;NGA_Househo... | blocked_no_raw_or_archive_file |
| 4 | NGA_2012_GHSP-W2_v02_M | 2 | sect6_plantingw2 | sect6_plantingw2;sect6_plantingw2.*;sect6_plantingw2.dta;sect6_plantingw2.sav;sect6_plantingw2.por;sect6_plantingw2.s... | blocked_no_raw_or_archive_file |
| 4 | NGA_2012_GHSP-W2_v02_M | 3 | sect11b1_plantingw2 | sect11b1_plantingw2;sect11b1_plantingw2.*;sect11b1_plantingw2.dta;sect11b1_plantingw2.sav;sect11b1_plantingw2.por;sec... | blocked_no_raw_or_archive_file |
| 4 | NGA_2012_GHSP-W2_v02_M | 4 | sect11d_plantingw2 | sect11d_plantingw2;sect11d_plantingw2.*;sect11d_plantingw2.dta;sect11d_plantingw2.sav;sect11d_plantingw2.por;sect11d_... | blocked_no_raw_or_archive_file |

## Post-Download Commands

- `python script/17_audit_raw_downloads.py`
- `python script/128_build_priority_archive_member_preflight.py`
- `python script/130_build_priority_raw_package_receipt_ledger.py`
- `python script/03_inspect_raw_schemas.py`
- `python script/29_build_raw_variable_verification_protocol.py`
- `python script/33_build_harmonization_recipe_gate.py`
- `python script/125_build_priority_climate_linkage_preflight.py`
- `python script/126_build_priority_raw_verification_workbook.py`
- `python script/140_build_priority_first_pass_variable_review_queue.py`
- `python script/129_build_priority_manual_verification_decision_gate.py`
- `python script/132_build_priority_analysis_dataset_synthesis_blueprint.py`
- `python script/134_build_priority_country_wave_promotion_packets.py`
- `python script/127_enforce_promoted_data_gate.py`
- `python script/36_build_direct_read_audit_bundle.py`
- `python script/14_validate_workspace.py`

## Machine-Readable Outputs

- `temp/priority_download_execution_packet.csv`
- `temp/priority_download_file_acceptance_matrix.csv`
- `result/priority_download_execution_packet_summary.csv`

## Guardrail

The listed core files are an acceptance matrix, not permission to build an
incomplete dataset. Download and preserve the complete unchanged official
package plus documentation for each wave. `data/` remains closed until all
promotion gates pass.
