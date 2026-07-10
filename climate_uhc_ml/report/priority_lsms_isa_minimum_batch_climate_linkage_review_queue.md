# Priority LSMS/ISA Minimum-Batch Climate Linkage Review Queue

Status: raw-blocked climate linkage review queue for the current 10 manual-download packets.

This queue aligns the current minimum-batch download board with official
metadata timing and geography candidates. It does not extract climate data,
accept a CHIRPS/ERA5 route, write `data/`, or run models. It tells the raw
review step which timing and geography files/variables must be verified once
the official packages are placed locally.

## Summary

| metric | value | interpretation |
| --- | --- | --- |
| priority_lsms_minimum_climate_review_dataset_rows | 10 | Current manual-download minimum-batch rows covered by the climate linkage review queue. |
| priority_lsms_minimum_climate_review_file_rows | 102 | Timing/geography candidate file rows to inspect after raw receipt. |
| priority_lsms_minimum_climate_review_timing_ready_metadata_rows | 10 | Rows with strong official metadata timing candidates. |
| priority_lsms_minimum_climate_review_geography_ready_metadata_rows | 10 | Rows with strong official metadata geography candidates. |
| priority_lsms_minimum_climate_review_point_route_rows | 8 | Rows whose metadata suggest coordinate or cluster-point linkage after raw verification. |
| priority_lsms_minimum_climate_review_admin_route_rows | 2 | Rows whose metadata suggest admin/EA aggregation after raw verification. |
| priority_lsms_minimum_climate_review_manual_route_rows | 0 | Rows needing manual route choice after raw review. |
| priority_lsms_minimum_climate_review_raw_blocked_rows | 10 | Rows still blocked because target folders contain no candidate raw files. |
| priority_lsms_minimum_climate_review_source_ready_rows | 10 | Rows with CHIRPS/ERA5/NASA source plan ready but not accepted. |
| priority_lsms_minimum_climate_review_accepted_route_rows | 0 | Rows with accepted climate linkage routes after raw timing/geography verification. |
| priority_lsms_minimum_climate_review_data_write_status | blocked_no_data_write | Climate linkage review does not write promoted data. |
| modeling_gate_status | blocked | No predictive, reduced-form, causal ML, or policy learning until registry thresholds pass. |

## Country-Wave Queue

| download_rank | idno | target_receipt_smoke_status | planned_temporal_route | planned_geography_route | timing_strong_candidate_variable_rows | geography_strong_candidate_variable_rows | climate_linkage_gate_status |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | ETH_2021_ESPS-W5_v02_M | blocked_no_candidate_raw_or_documentation_files | interview_date_route_raw_unverified | point_or_cluster_coordinate_route_raw_unverified | 8 | 12 | blocked_raw_timing_geography_not_verified |
| 2 | ETH_2018_ESS_v04_M | blocked_no_candidate_raw_or_documentation_files | interview_date_route_raw_unverified | point_or_cluster_coordinate_route_raw_unverified | 9 | 12 | blocked_raw_timing_geography_not_verified |
| 3 | NGA_2012_GHSP-W2_v02_M | blocked_no_candidate_raw_or_documentation_files | fieldwork_period_route_raw_unverified_manual_review | point_or_cluster_coordinate_route_raw_unverified | 12 | 4 | blocked_raw_timing_geography_not_verified |
| 4 | NGA_2015_GHSP-W3_v02_M | blocked_no_candidate_raw_or_documentation_files | fieldwork_period_route_raw_unverified_manual_review | point_or_cluster_coordinate_route_raw_unverified | 12 | 12 | blocked_raw_timing_geography_not_verified |
| 5 | NGA_2010_GHSP-W1_v03_M | blocked_no_candidate_raw_or_documentation_files | interview_date_route_raw_unverified | point_or_cluster_coordinate_route_raw_unverified | 12 | 12 | blocked_raw_timing_geography_not_verified |
| 6 | TZA_2008_NPS-R1_v03_M | blocked_no_candidate_raw_or_documentation_files | interview_month_year_route_raw_unverified | point_or_cluster_coordinate_route_raw_unverified | 3 | 12 | blocked_raw_timing_geography_not_verified |
| 7 | TZA_2010_NPS-R2_v03_M | blocked_no_candidate_raw_or_documentation_files | interview_month_year_route_raw_unverified | point_or_cluster_coordinate_route_raw_unverified | 4 | 12 | blocked_raw_timing_geography_not_verified |
| 8 | TZA_2012_NPS-R3_v01_M | blocked_no_candidate_raw_or_documentation_files | fieldwork_period_route_raw_unverified_manual_review | point_or_cluster_coordinate_route_raw_unverified | 12 | 12 | blocked_raw_timing_geography_not_verified |
| 9 | UGA_2019_UNPS_v03_M | blocked_no_candidate_raw_or_documentation_files | interview_month_year_route_raw_unverified | admin_or_ea_geography_route_raw_unverified | 3 | 12 | blocked_raw_timing_geography_not_verified |
| 10 | NPL_2010_LSS-III_v01_M | blocked_no_candidate_raw_or_documentation_files | interview_date_route_raw_unverified | admin_or_ea_geography_route_raw_unverified | 12 | 1 | blocked_raw_timing_geography_not_verified |

## File Review Queue

| idno | requirement | file_rank | file_name | strong_candidate_variable_rows | top_variable_names |
| --- | --- | --- | --- | --- | --- |
| ETH_2021_ESPS-W5_v02_M | survey_timing | 1 | sect_cover_pp_w5.dta | 1 | InterviewDate |
| ETH_2021_ESPS-W5_v02_M | survey_timing | 2 | sect_cover_ph_w5.dta | 1 | InterviewDate |
| ETH_2021_ESPS-W5_v02_M | survey_timing | 3 | sect_cover_ls_w5.dta | 1 | InterviewDate |
| ETH_2021_ESPS-W5_v02_M | survey_timing | 4 | sect12b1_hh_w5.dta | 2 | s12bq08a;s12bq08b |
| ETH_2021_ESPS-W5_v02_M | survey_timing | 5 | sect7b_hh_w5.dta | 0 | item_cd_12months;s7q04 |
| ETH_2021_ESPS-W5_v02_M | survey_timing | 6 | eth_householdgeovariables_y5.dta | 1 | wetQ_avgstart |
| ETH_2021_ESPS-W5_v02_M | survey_timing | 7 | sect_cover_hh_w5.dta | 1 | saq19__Timestamp |
| ETH_2021_ESPS-W5_v02_M | survey_timing | 8 | eth_plotgeovariables_y5.dta | 1 | wetQ_avgstart |
| ETH_2021_ESPS-W5_v02_M | climate_geography | 1 | sect_cover_hh_w5.dta | 2 | saq19__Latitude;saq19__Longitude |
| ETH_2021_ESPS-W5_v02_M | climate_geography | 2 | sect10a_com_w5.dta | 2 | cs10q05__Latitude;cs10q05__Longitude |
| ETH_2021_ESPS-W5_v02_M | climate_geography | 3 | sect_cover_pp_w5.dta | 2 | saq19__Latitude;saq19__Longitude |
| ETH_2021_ESPS-W5_v02_M | climate_geography | 4 | sect_cover_ph_w5.dta | 2 | saq19__Latitude;saq19__Longitude |
| ETH_2021_ESPS-W5_v02_M | climate_geography | 5 | sect_cover_ls_w5.dta | 2 | saq19__Latitude;saq19__Longitude |
| ETH_2021_ESPS-W5_v02_M | climate_geography | 6 | sect3_pp_w5.dta | 2 | s3q09__Latitude;s3q09__Longitude |
| ETH_2018_ESS_v04_M | survey_timing | 1 | sect_cover_ph_w4.dta | 2 | InterviewDate;saq19__Timestamp |
| ETH_2018_ESS_v04_M | survey_timing | 2 | sect_cover_pp_w4.dta | 2 | InterviewDate;saq19__Timestamp |
| ETH_2018_ESS_v04_M | survey_timing | 3 | sect_cover_ls_w4.dta | 1 | InterviewDate;saq19__Timestamp |
| ETH_2018_ESS_v04_M | survey_timing | 4 | sect12b1_hh_w4.dta | 2 | s12bq08a;s12bq08b |
| ETH_2018_ESS_v04_M | survey_timing | 5 | ETH_HouseholdGeovariables_Y4.dta | 1 | wetQ_avgstart;h2018_wetQstart |
| ETH_2018_ESS_v04_M | survey_timing | 6 | sect_cover_hh_w4.dta | 1 | InterviewStart |
| ETH_2018_ESS_v04_M | survey_timing | 7 | sect15b_hh_w4.dta | 0 | s15q06b |
| ETH_2018_ESS_v04_M | climate_geography | 1 | sect_cover_ph_w4.dta | 3 | saq19__Latitude;saq19__Longitude;ea_id |
| ETH_2018_ESS_v04_M | climate_geography | 2 | sect_cover_pp_w4.dta | 2 | saq19__Latitude;saq19__Longitude |
| ETH_2018_ESS_v04_M | climate_geography | 3 | sect_cover_ls_w4.dta | 2 | saq19__Latitude;saq19__Longitude |
| ETH_2018_ESS_v04_M | climate_geography | 4 | sect3_pp_w4.dta | 2 | s3q09__Latitude;s3q09__Longitude |
| ETH_2018_ESS_v04_M | climate_geography | 5 | sect10a_com_w4.dta | 2 | cs10q05__Latitude;cs10q05__Longitude |
| ETH_2018_ESS_v04_M | climate_geography | 6 | sect_cover_hh_w4.dta | 1 | ea_id |
| NGA_2012_GHSP-W2_v02_M | survey_timing | 1 | secta_harvestw2 | 12 | saq14ah;saq14am;saq14bh;saq14bm;saq18ah;saq18am;saq18bh;saq18bm;saq22ah;saq22am;saq22bh... |
| NGA_2012_GHSP-W2_v02_M | climate_geography | 1 | HHTrack | 0 | ea;lga;state;zone |
| NGA_2012_GHSP-W2_v02_M | climate_geography | 2 | secta_harvestw2 | 0 | ea;lga;state;zone |
| NGA_2012_GHSP-W2_v02_M | climate_geography | 3 | NGA_HouseholdGeovars_Y2 | 2 | LAT_DD_MOD;LON_DD_MOD |
| NGA_2012_GHSP-W2_v02_M | climate_geography | 4 | cons_agg_wave2_visit1 | 1 | ea |
| NGA_2012_GHSP-W2_v02_M | climate_geography | 5 | cons_agg_wave2_visit2 | 1 | ea |
| NGA_2015_GHSP-W3_v02_M | survey_timing | 1 | secta_harvestw3 | 12 | saq14ah;saq14am;saq14bh;saq14bm;saq17ah;saq17am;saq17bh;saq17bm;saq20ah;saq20am;saq20bh... |
| NGA_2015_GHSP-W3_v02_M | climate_geography | 1 | sect1_harvestw3 | 4 | s1q31a;s1q31b;s1q31c;s1q31d |
| NGA_2015_GHSP-W3_v02_M | climate_geography | 2 | NGA_HouseholdGeovars_Y3 | 2 | LAT_DD_MOD;LON_DD_MOD |
| NGA_2015_GHSP-W3_v02_M | climate_geography | 3 | sectc1_harvestw3 | 2 | ea;lga |
| NGA_2015_GHSP-W3_v02_M | climate_geography | 4 | sectc2_harvestw3 | 2 | ea;lga |
| NGA_2015_GHSP-W3_v02_M | climate_geography | 5 | cons_agg_wave3_visit1 | 1 | ea |
| NGA_2015_GHSP-W3_v02_M | climate_geography | 6 | cons_agg_wave3_visit2 | 1 | ea |
| NGA_2010_GHSP-W1_v03_M | survey_timing | 1 | secta_harvestw1 | 11 | saq14ah;saq14am;saq14bh;saq14bm;saq18ah;saq18am;saq18bh;saq18bm;saq22ah;saq22am;saq22bh |
| NGA_2010_GHSP-W1_v03_M | survey_timing | 2 | sectc_plantingw1 | 1 | interview_date |
| NGA_2010_GHSP-W1_v03_M | climate_geography | 1 | NGA_HouseholdGeovariables_Y1 | 10 | lat_dd_mod;lon_dd_mod;ea;eviarea_avg;grn_avg;h2010_eviarea;h2010_grn;h2010_sen;lga;sen_avg |
| NGA_2010_GHSP-W1_v03_M | climate_geography | 2 | cons_agg_wave1_visit1 | 1 | ea |
| NGA_2010_GHSP-W1_v03_M | climate_geography | 3 | cons_agg_wave1_visit2 | 1 | ea |
| TZA_2008_NPS-R1_v03_M | survey_timing | 1 | SEC_A_T_Swahili_Labels | 0 | endmin;sa2q17endhr;sa2q17starthr;sa2q17startmins |
| TZA_2008_NPS-R1_v03_M | survey_timing | 2 | SEC_A_T_English_Labels | 0 | endmin;sa2q17endhr;sa2q17starthr |
| TZA_2008_NPS-R1_v03_M | survey_timing | 3 | SECTA1A2_English_Labels | 2 | ca07m;ca07y |
| TZA_2008_NPS-R1_v03_M | survey_timing | 4 | SEC_R_Swahili_Labels | 0 | srq5month;srq5year |
| TZA_2008_NPS-R1_v03_M | survey_timing | 5 | TZY1.HH.Consumption | 1 | intmonth |
| TZA_2008_NPS-R1_v03_M | climate_geography | 1 | HH.Geovariables_Y1 | 3 | ea_id;lat_modified;lon_modified |
| TZA_2008_NPS-R1_v03_M | climate_geography | 2 | SEC_A_T_English_Labels | 2 | clusterid;ea |
| TZA_2008_NPS-R1_v03_M | climate_geography | 3 | SEC_A_T_Swahili_Labels | 1 | ea |
| TZA_2008_NPS-R1_v03_M | climate_geography | 4 | SECTA1A2_Swahili_Labels | 1 | ea_id |
| TZA_2008_NPS-R1_v03_M | climate_geography | 5 | SECTCB_Swahili_Labels | 1 | ea_id |
| TZA_2008_NPS-R1_v03_M | climate_geography | 6 | SECTCEFG | 1 | ea_id |
| TZA_2008_NPS-R1_v03_M | climate_geography | 7 | SECTCH | 1 | ea_id |
| TZA_2008_NPS-R1_v03_M | climate_geography | 8 | SECTCI | 1 | ea_id |
| TZA_2010_NPS-R2_v03_M | survey_timing | 1 | HH_SEC_C | 0 | hh_c08;hh_c10;hh_c30 |
| TZA_2010_NPS-R2_v03_M | survey_timing | 2 | HH_SEC_E1 | 0 | hh_e44;hh_e67;hh_e68 |
| ... | ... | ... | ... | ... | ... |

## Stop Rule

Every row remains climate-linkage blocked until the complete official raw
package is present, receipt validation passes, timing/geography variables are
value-checked, and the chosen CHIRPS or ERA5 extraction route is validated.
