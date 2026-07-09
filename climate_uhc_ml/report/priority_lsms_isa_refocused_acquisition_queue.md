# Priority LSMS-ISA Refocused Acquisition Queue

Status: actionable metadata-only acquisition queue. This queue is the next
manual-download target list after the LSMS/ISA alignment audit found that
Malawi MTM and Uganda SAGE should not anchor the five-country core sample.

## Bottom Line

- The refocused 10-wave core keeps Ethiopia, Nigeria, and Tanzania as selected.
- Malawi MTM is replaced by the highest-scoring Malawi IHS/IHPS candidate.
- Uganda SAGE is replaced by the highest-scoring Uganda UNPS candidate.
- Extra Malawi/Uganda backup waves are queued in case primary replacements fail
  raw consumption, OOP, access, timing, or geography review.
- No raw packages are present and no data were promoted.

## Summary

| Metric | Value | Interpretation |
|---|---:|---|
| priority_lsms_refocused_wave_plan_rows | 13 | Refocused selected wave-plan rows after replacing off-family core waves. |
| priority_lsms_refocused_core_wave_rows | 10 | Core priority wave rows in the refocused plan. |
| priority_lsms_refocused_core_required_countries | 5 | Required LSMS/ISA priority countries represented in the refocused core. |
| priority_lsms_refocused_core_lsms_aligned_rows | 10 | Core rows in the refocused plan with LSMS/ISA or LSMS-style family alignment. |
| priority_lsms_refocused_replaced_off_family_core_rows | 2 | Off-family current core rows replaced in the refocused plan. |
| priority_lsms_refocused_acquisition_queue_rows | 19 | Selected and backup rows in the refocused manual acquisition queue. |
| priority_lsms_refocused_replacement_backup_rows | 6 | Extra Malawi/Uganda LSMS/ISA backup waves queued if primary replacements fail manual review. |
| priority_lsms_refocused_requirement_rows | 152 | Requirement rows for selected and backup acquisition targets. |
| priority_lsms_refocused_requirement_metadata_hit_rows | 98 | Requirement rows with public metadata evidence, still requiring raw review. |
| priority_lsms_refocused_requirement_weak_or_proxy_rows | 11 | Requirement rows where public metadata may be a weak proxy or false positive and must be resolved from raw documentation. |
| priority_lsms_refocused_requirement_missing_or_raw_only_rows | 54 | Requirement rows requiring raw package or documentation review because public metadata is missing, weak, or insufficient. |
| priority_lsms_refocused_raw_package_received_rows | 0 | Refocused targets with original raw package receipt; still zero. |
| priority_lsms_refocused_handoff_readmes_written | 19 | Per-wave refocused acquisition handoff files written. |
| priority_lsms_refocused_data_write_status | blocked_no_promoted_rows | No refocused wave may write to data/ before all raw and climate gates pass. |
| modeling_gate_status | blocked | Models remain blocked until raw-backed promotion thresholds and accepted climate linkage pass. |
| priority_lsms_refocused_queue_role_core_replacement_primary | 2 | Refocused acquisition queue role count. |
| priority_lsms_refocused_queue_role_core_selected_lsms_isa_aligned | 8 | Refocused acquisition queue role count. |
| priority_lsms_refocused_queue_role_replacement_backup_wave | 6 | Refocused acquisition queue role count. |
| priority_lsms_refocused_queue_role_sixth_country_backup_candidate | 3 | Refocused acquisition queue role count. |

## Replacements

| refocused_rank | country | wave | idno | supersedes_idno | current_survey_family | metadata_feasibility_score | metadata_requirement_score |
|---|---|---|---|---|---|---|---|
| 3 | Malawi | 2004-2005 | MWI_2004_IHS-II_v01_M | MWI_2007-2009_MTM_v01_M | lsms_isa_integrated_household_survey | 5 | 7 |
| 10 | Uganda | 2019-2020 | UGA_2019_UNPS_v03_M | UGA_2014_SAGE-EL_v01_M | lsms_isa_national_panel_survey | 4 | 5 |

## Refocused Download Queue

| download_priority_order | queue_role | country | wave | idno | metadata_feasibility_score | metadata_requirement_score | official_get_microdata_url |
|---|---|---|---|---|---|---|---|
| 1 | core_selected_lsms_isa_aligned | Ethiopia | 2021-2022 | ETH_2021_ESPS-W5_v02_M | 5 | 7 | https://microdata.worldbank.org/catalog/6161/get-microdata |
| 2 | core_selected_lsms_isa_aligned | Ethiopia | 2018-2019 | ETH_2018_ESS_v04_M | 5 | 7 | https://microdata.worldbank.org/catalog/3823/get-microdata |
| 3 | core_replacement_primary | Malawi | 2004-2005 | MWI_2004_IHS-II_v01_M | 5 | 7 | https://microdata.worldbank.org/catalog/2307/get-microdata |
| 4 | core_selected_lsms_isa_aligned | Nigeria | 2012-2013 | NGA_2012_GHSP-W2_v02_M | 5 | 7 | https://microdata.worldbank.org/catalog/1952/get-microdata |
| 5 | core_selected_lsms_isa_aligned | Nigeria | 2015-2016 | NGA_2015_GHSP-W3_v02_M | 5 | 7 | https://microdata.worldbank.org/catalog/2734/get-microdata |
| 6 | core_selected_lsms_isa_aligned | Nigeria | 2010-2011 | NGA_2010_GHSP-W1_v03_M | 5 | 7 | https://microdata.worldbank.org/catalog/1002/get-microdata |
| 7 | core_selected_lsms_isa_aligned | Tanzania | 2008-2009 | TZA_2008_NPS-R1_v03_M | 2 | 1 | https://microdata.worldbank.org/catalog/76/get-microdata |
| 8 | core_selected_lsms_isa_aligned | Tanzania | 2010-2011 | TZA_2010_NPS-R2_v03_M | 5 | 7 | https://microdata.worldbank.org/catalog/1050/get-microdata |
| 9 | core_selected_lsms_isa_aligned | Tanzania | 2012-2013 | TZA_2012_NPS-R3_v01_M | 5 | 7 | https://microdata.worldbank.org/catalog/2252/get-microdata |
| 10 | core_replacement_primary | Uganda | 2019-2020 | UGA_2019_UNPS_v03_M | 4 | 5 | https://microdata.worldbank.org/catalog/3902/get-microdata |
| 11 | sixth_country_backup_candidate | Jamaica | 1997 | JAM_1997_SLC_v01_M | 2 | 1 | https://microdata.worldbank.org/catalog/2368/get-microdata |
| 12 | sixth_country_backup_candidate | Kyrgyz Republic | 1993 | KGZ_1993_KMPS_v01_M | 5 | 7 | https://microdata.worldbank.org/catalog/280/get-microdata |
| 13 | sixth_country_backup_candidate | Nepal | 2010-2011 | NPL_2010_LSS-III_v01_M | 5 | 7 | https://microdata.worldbank.org/catalog/1000/get-microdata |
| 14 | replacement_backup_wave | Malawi | 2019-2020 | MWI_2019_IHS-V_v06_M | 3 | 5 | https://microdata.worldbank.org/catalog/3818/get-microdata |
| 15 | replacement_backup_wave | Malawi | 2016-2017 | MWI_2016_IHS-IV_v04_M | 3 | 5 | https://microdata.worldbank.org/catalog/2936/get-microdata |
| 16 | replacement_backup_wave | Malawi | 2010-2011 | MWI_2010_IHS-III_v01_M | 3 | 5 | https://microdata.worldbank.org/catalog/1003/get-microdata |
| 17 | replacement_backup_wave | Uganda | 2011-2012 | UGA_2011_UNPS_v02_M | 3 | 7 | https://microdata.worldbank.org/catalog/2059/get-microdata |
| 18 | replacement_backup_wave | Uganda | 2018-2019 | UGA_2018_UNPS_v02_M | 3 | 5 | https://microdata.worldbank.org/catalog/3795/get-microdata |
| 19 | replacement_backup_wave | Uganda | 2015-2016 | UGA_2015_UNPS_v02_M | 3 | 5 | https://microdata.worldbank.org/catalog/3460/get-microdata |

## Replacement Backups

| download_priority_order | country | wave | idno | metadata_feasibility_score | metadata_requirement_score | official_get_microdata_url |
|---|---|---|---|---|---|---|
| 14 | Malawi | 2019-2020 | MWI_2019_IHS-V_v06_M | 3 | 5 | https://microdata.worldbank.org/catalog/3818/get-microdata |
| 15 | Malawi | 2016-2017 | MWI_2016_IHS-IV_v04_M | 3 | 5 | https://microdata.worldbank.org/catalog/2936/get-microdata |
| 16 | Malawi | 2010-2011 | MWI_2010_IHS-III_v01_M | 3 | 5 | https://microdata.worldbank.org/catalog/1003/get-microdata |
| 17 | Uganda | 2011-2012 | UGA_2011_UNPS_v02_M | 3 | 7 | https://microdata.worldbank.org/catalog/2059/get-microdata |
| 18 | Uganda | 2018-2019 | UGA_2018_UNPS_v02_M | 3 | 5 | https://microdata.worldbank.org/catalog/3795/get-microdata |
| 19 | Uganda | 2015-2016 | UGA_2015_UNPS_v02_M | 3 | 5 | https://microdata.worldbank.org/catalog/3460/get-microdata |

## High-Value Metadata Gaps To Check In Raw Packages

| download_priority_order | country | idno | requirement | metadata_status | raw_review_action |
|---|---|---|---|---|---|
| 1 | Ethiopia | ETH_2021_ESPS-W5_v02_M | oop_health_expenditure | metadata_weak_or_proxy_raw_review_required | Verify this requirement directly in the original raw package, questionnaires, codebooks, and value labels. |
| 2 | Ethiopia | ETH_2018_ESS_v04_M | oop_health_expenditure | metadata_weak_or_proxy_raw_review_required | Verify this requirement directly in the original raw package, questionnaires, codebooks, and value labels. |
| 3 | Malawi | MWI_2004_IHS-II_v01_M | oop_health_expenditure | metadata_weak_or_proxy_raw_review_required | Verify this requirement directly in the original raw package, questionnaires, codebooks, and value labels. |
| 4 | Nigeria | NGA_2012_GHSP-W2_v02_M | oop_health_expenditure | metadata_weak_or_proxy_raw_review_required | Verify this requirement directly in the original raw package, questionnaires, codebooks, and value labels. |
| 5 | Nigeria | NGA_2015_GHSP-W3_v02_M | oop_health_expenditure | metadata_weak_or_proxy_raw_review_required | Verify this requirement directly in the original raw package, questionnaires, codebooks, and value labels. |
| 6 | Nigeria | NGA_2010_GHSP-W1_v03_M | oop_health_expenditure | metadata_weak_or_proxy_raw_review_required | Verify this requirement directly in the original raw package, questionnaires, codebooks, and value labels. |
| 7 | Tanzania | TZA_2008_NPS-R1_v03_M | consumption_or_income | not_found_in_public_metadata_raw_review_required | Verify this requirement directly in the original raw package, questionnaires, codebooks, and value labels. |
| 7 | Tanzania | TZA_2008_NPS-R1_v03_M | oop_health_expenditure | not_found_in_public_metadata_raw_review_required | Verify this requirement directly in the original raw package, questionnaires, codebooks, and value labels. |
| 7 | Tanzania | TZA_2008_NPS-R1_v03_M | climate_geography | not_found_in_public_metadata_raw_review_required | Verify this requirement directly in the original raw package, questionnaires, codebooks, and value labels. |
| 8 | Tanzania | TZA_2010_NPS-R2_v03_M | oop_health_expenditure | metadata_weak_or_proxy_raw_review_required | Verify this requirement directly in the original raw package, questionnaires, codebooks, and value labels. |
| 9 | Tanzania | TZA_2012_NPS-R3_v01_M | oop_health_expenditure | metadata_weak_or_proxy_raw_review_required | Verify this requirement directly in the original raw package, questionnaires, codebooks, and value labels. |
| 10 | Uganda | UGA_2019_UNPS_v03_M | consumption_or_income | not_found_in_public_metadata_raw_review_required | Verify this requirement directly in the original raw package, questionnaires, codebooks, and value labels. |
| 10 | Uganda | UGA_2019_UNPS_v03_M | oop_health_expenditure | metadata_weak_or_proxy_raw_review_required | Verify this requirement directly in the original raw package, questionnaires, codebooks, and value labels. |
| 11 | Jamaica | JAM_1997_SLC_v01_M | consumption_or_income | not_found_in_public_metadata_raw_review_required | Verify this requirement directly in the original raw package, questionnaires, codebooks, and value labels. |
| 11 | Jamaica | JAM_1997_SLC_v01_M | oop_health_expenditure | not_found_in_public_metadata_raw_review_required | Verify this requirement directly in the original raw package, questionnaires, codebooks, and value labels. |
| 11 | Jamaica | JAM_1997_SLC_v01_M | climate_geography | not_found_in_public_metadata_raw_review_required | Verify this requirement directly in the original raw package, questionnaires, codebooks, and value labels. |
| 12 | Kyrgyz Republic | KGZ_1993_KMPS_v01_M | oop_health_expenditure | metadata_weak_or_proxy_raw_review_required | Verify this requirement directly in the original raw package, questionnaires, codebooks, and value labels. |
| 13 | Nepal | NPL_2010_LSS-III_v01_M | oop_health_expenditure | metadata_weak_or_proxy_raw_review_required | Verify this requirement directly in the original raw package, questionnaires, codebooks, and value labels. |
| 14 | Malawi | MWI_2019_IHS-V_v06_M | consumption_or_income | not_found_in_public_metadata_raw_review_required | Verify this requirement directly in the original raw package, questionnaires, codebooks, and value labels. |
| 14 | Malawi | MWI_2019_IHS-V_v06_M | oop_health_expenditure | not_found_in_public_metadata_raw_review_required | Verify this requirement directly in the original raw package, questionnaires, codebooks, and value labels. |
| 15 | Malawi | MWI_2016_IHS-IV_v04_M | consumption_or_income | not_found_in_public_metadata_raw_review_required | Verify this requirement directly in the original raw package, questionnaires, codebooks, and value labels. |
| 15 | Malawi | MWI_2016_IHS-IV_v04_M | oop_health_expenditure | not_found_in_public_metadata_raw_review_required | Verify this requirement directly in the original raw package, questionnaires, codebooks, and value labels. |
| 16 | Malawi | MWI_2010_IHS-III_v01_M | consumption_or_income | not_found_in_public_metadata_raw_review_required | Verify this requirement directly in the original raw package, questionnaires, codebooks, and value labels. |
| 16 | Malawi | MWI_2010_IHS-III_v01_M | oop_health_expenditure | not_found_in_public_metadata_raw_review_required | Verify this requirement directly in the original raw package, questionnaires, codebooks, and value labels. |
| 17 | Uganda | UGA_2011_UNPS_v02_M | oop_health_expenditure | not_found_in_public_metadata_raw_review_required | Verify this requirement directly in the original raw package, questionnaires, codebooks, and value labels. |
| 18 | Uganda | UGA_2018_UNPS_v02_M | consumption_or_income | not_found_in_public_metadata_raw_review_required | Verify this requirement directly in the original raw package, questionnaires, codebooks, and value labels. |
| 18 | Uganda | UGA_2018_UNPS_v02_M | oop_health_expenditure | not_found_in_public_metadata_raw_review_required | Verify this requirement directly in the original raw package, questionnaires, codebooks, and value labels. |
| 19 | Uganda | UGA_2015_UNPS_v02_M | consumption_or_income | not_found_in_public_metadata_raw_review_required | Verify this requirement directly in the original raw package, questionnaires, codebooks, and value labels. |
| 19 | Uganda | UGA_2015_UNPS_v02_M | oop_health_expenditure | not_found_in_public_metadata_raw_review_required | Verify this requirement directly in the original raw package, questionnaires, codebooks, and value labels. |

## Machine-Readable Outputs

- `result/priority_lsms_isa_refocused_wave_plan.csv`
- `temp/priority_lsms_isa_refocused_acquisition_queue.csv`
- `temp/priority_lsms_isa_refocused_requirement_matrix.csv`
- `result/priority_lsms_isa_refocused_acquisition_summary.csv`

## Guardrail

This queue replaces the off-family core download path but does not promote any
country-wave. Complete official raw packages, documentation, raw value review,
outcome review, and CHIRPS/ERA5 linkage review are still required before
anything can be written into `data/`.
