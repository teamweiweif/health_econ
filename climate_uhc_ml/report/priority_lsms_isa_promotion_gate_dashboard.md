# Priority LSMS/ISA Promotion Gate Dashboard

Status: raw-package-to-promotion gate dashboard for the refocused LSMS/ISA
country-wave queue.

This dashboard does not download raw data and does not write new `data/`
outputs. It combines the current registry, official file receipt validator,
received raw schema audit, value profile, and semantics review into one
country-wave gate view.

## Summary

| metric | value | interpretation |
| --- | --- | --- |
| priority_lsms_promotion_gate_country_wave_rows | 19 | Country-waves tracked in the promotion-gate dashboard. |
| priority_lsms_promotion_gate_requirement_rows | 152 | Requirement-level gate rows tracked across country-waves. |
| priority_lsms_promotion_gate_promoted_rows | 1 | Rows already promoted analysis-ready in the registry. |
| priority_lsms_promotion_gate_blocked_raw_package_rows | 18 | Rows still blocked because complete official raw package receipt is missing. |
| priority_lsms_promotion_gate_ready_for_packet_rows | 0 | Rows whose requirement gates are ready for a promotion packet but are not yet in data/. |
| priority_lsms_promotion_gate_minimum_remaining_rows | 10 | Unpromoted minimum-batch rows still tracked here. |
| priority_lsms_promotion_gate_backup_rows | 8 | Backup rows tracked after the minimum batch. |
| priority_lsms_promotion_gate_requirement_blocked_raw_package_rows | 144 | Requirement rows blocked at raw package receipt. |
| data_write_gate_status | blocked_for_unpromoted_rows | No new unpromoted country-wave may be written to data/ from this dashboard. |
| modeling_gate_status | blocked | No predictive, reduced-form, causal ML, or policy learning until registry thresholds pass. |
| priority_lsms_promotion_gate_status_blocked_at_raw_package_receipt | 18 | Country-wave count by promotion readiness status. |
| priority_lsms_promotion_gate_status_promoted_analysis_ready | 1 | Country-wave count by promotion readiness status. |
| priority_lsms_promotion_gate_requirement_status_accepted_via_promoted_registry | 8 | Requirement-row count by gate status. |
| priority_lsms_promotion_gate_requirement_status_blocked_raw_package_not_received | 144 | Requirement-row count by gate status. |

## Country-Wave Gate View

| promotion_rank | promotion_tier | country | wave | idno | promotion_readiness_status | next_required_gate |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | current_promoted_registry | Malawi | 2004-2005 | MWI_2004_IHS-II_v01_M | promoted_analysis_ready | none |
| 2 | minimum_batch_remaining | Ethiopia | 2021-2022 | ETH_2021_ESPS-W5_v02_M | blocked_at_raw_package_receipt | download_place_complete_official_raw_package |
| 3 | minimum_batch_remaining | Ethiopia | 2018-2019 | ETH_2018_ESS_v04_M | blocked_at_raw_package_receipt | download_place_complete_official_raw_package |
| 4 | minimum_batch_remaining | Nigeria | 2012-2013 | NGA_2012_GHSP-W2_v02_M | blocked_at_raw_package_receipt | download_place_complete_official_raw_package |
| 5 | minimum_batch_remaining | Nigeria | 2015-2016 | NGA_2015_GHSP-W3_v02_M | blocked_at_raw_package_receipt | download_place_complete_official_raw_package |
| 6 | minimum_batch_remaining | Nigeria | 2010-2011 | NGA_2010_GHSP-W1_v03_M | blocked_at_raw_package_receipt | download_place_complete_official_raw_package |
| 7 | minimum_batch_remaining | Tanzania | 2008-2009 | TZA_2008_NPS-R1_v03_M | blocked_at_raw_package_receipt | download_place_complete_official_raw_package |
| 8 | minimum_batch_remaining | Tanzania | 2010-2011 | TZA_2010_NPS-R2_v03_M | blocked_at_raw_package_receipt | download_place_complete_official_raw_package |
| 9 | minimum_batch_remaining | Tanzania | 2012-2013 | TZA_2012_NPS-R3_v01_M | blocked_at_raw_package_receipt | download_place_complete_official_raw_package |
| 10 | minimum_batch_remaining | Uganda | 2019-2020 | UGA_2019_UNPS_v03_M | blocked_at_raw_package_receipt | download_place_complete_official_raw_package |
| 11 | minimum_batch_remaining | Nepal | 2010-2011 | NPL_2010_LSS-III_v01_M | blocked_at_raw_package_receipt | download_place_complete_official_raw_package |
| 12 | backup_after_minimum_batch | Jamaica | 1997 | JAM_1997_SLC_v01_M | blocked_at_raw_package_receipt | download_place_complete_official_raw_package |
| 13 | backup_after_minimum_batch | Kyrgyz Republic | 1993 | KGZ_1993_KMPS_v01_M | blocked_at_raw_package_receipt | download_place_complete_official_raw_package |
| 14 | backup_after_minimum_batch | Malawi | 2019-2020 | MWI_2019_IHS-V_v06_M | blocked_at_raw_package_receipt | download_place_complete_official_raw_package |
| 15 | backup_after_minimum_batch | Malawi | 2016-2017 | MWI_2016_IHS-IV_v04_M | blocked_at_raw_package_receipt | download_place_complete_official_raw_package |
| 16 | backup_after_minimum_batch | Malawi | 2010-2011 | MWI_2010_IHS-III_v01_M | blocked_at_raw_package_receipt | download_place_complete_official_raw_package |
| 17 | backup_after_minimum_batch | Uganda | 2011-2012 | UGA_2011_UNPS_v02_M | blocked_at_raw_package_receipt | download_place_complete_official_raw_package |
| 18 | backup_after_minimum_batch | Uganda | 2018-2019 | UGA_2018_UNPS_v02_M | blocked_at_raw_package_receipt | download_place_complete_official_raw_package |
| 19 | backup_after_minimum_batch | Uganda | 2015-2016 | UGA_2015_UNPS_v02_M | blocked_at_raw_package_receipt | download_place_complete_official_raw_package |

## Blocked Rows

| promotion_rank | country | wave | idno | official_file_receipt_status | promotion_readiness_status | next_required_gate |
| --- | --- | --- | --- | --- | --- | --- |
| 2 | Ethiopia | 2021-2022 | ETH_2021_ESPS-W5_v02_M | blocked_no_original_package | blocked_at_raw_package_receipt | download_place_complete_official_raw_package |
| 3 | Ethiopia | 2018-2019 | ETH_2018_ESS_v04_M | blocked_no_original_package | blocked_at_raw_package_receipt | download_place_complete_official_raw_package |
| 4 | Nigeria | 2012-2013 | NGA_2012_GHSP-W2_v02_M | blocked_no_original_package | blocked_at_raw_package_receipt | download_place_complete_official_raw_package |
| 5 | Nigeria | 2015-2016 | NGA_2015_GHSP-W3_v02_M | blocked_no_original_package | blocked_at_raw_package_receipt | download_place_complete_official_raw_package |
| 6 | Nigeria | 2010-2011 | NGA_2010_GHSP-W1_v03_M | blocked_no_original_package | blocked_at_raw_package_receipt | download_place_complete_official_raw_package |
| 7 | Tanzania | 2008-2009 | TZA_2008_NPS-R1_v03_M | blocked_no_original_package | blocked_at_raw_package_receipt | download_place_complete_official_raw_package |
| 8 | Tanzania | 2010-2011 | TZA_2010_NPS-R2_v03_M | blocked_no_original_package | blocked_at_raw_package_receipt | download_place_complete_official_raw_package |
| 9 | Tanzania | 2012-2013 | TZA_2012_NPS-R3_v01_M | blocked_no_original_package | blocked_at_raw_package_receipt | download_place_complete_official_raw_package |
| 10 | Uganda | 2019-2020 | UGA_2019_UNPS_v03_M | blocked_no_original_package | blocked_at_raw_package_receipt | download_place_complete_official_raw_package |
| 11 | Nepal | 2010-2011 | NPL_2010_LSS-III_v01_M | blocked_no_original_package | blocked_at_raw_package_receipt | download_place_complete_official_raw_package |
| 12 | Jamaica | 1997 | JAM_1997_SLC_v01_M | blocked_no_original_package | blocked_at_raw_package_receipt | download_place_complete_official_raw_package |
| 13 | Kyrgyz Republic | 1993 | KGZ_1993_KMPS_v01_M | blocked_no_original_package | blocked_at_raw_package_receipt | download_place_complete_official_raw_package |
| 14 | Malawi | 2019-2020 | MWI_2019_IHS-V_v06_M | blocked_no_original_package | blocked_at_raw_package_receipt | download_place_complete_official_raw_package |
| 15 | Malawi | 2016-2017 | MWI_2016_IHS-IV_v04_M | blocked_no_original_package | blocked_at_raw_package_receipt | download_place_complete_official_raw_package |
| 16 | Malawi | 2010-2011 | MWI_2010_IHS-III_v01_M | blocked_no_original_package | blocked_at_raw_package_receipt | download_place_complete_official_raw_package |
| 17 | Uganda | 2011-2012 | UGA_2011_UNPS_v02_M | blocked_no_original_package | blocked_at_raw_package_receipt | download_place_complete_official_raw_package |
| 18 | Uganda | 2018-2019 | UGA_2018_UNPS_v02_M | blocked_no_original_package | blocked_at_raw_package_receipt | download_place_complete_official_raw_package |
| 19 | Uganda | 2015-2016 | UGA_2015_UNPS_v02_M | blocked_no_original_package | blocked_at_raw_package_receipt | download_place_complete_official_raw_package |

## Requirement Gate Preview

| promotion_rank | idno | requirement | requirement_gate_status | next_required_action |
| --- | --- | --- | --- | --- |
| 1 | MWI_2004_IHS-II_v01_M | household_person_keys | accepted_via_promoted_registry | No action for this dashboard; keep registry/data lineage reproducible. |
| 1 | MWI_2004_IHS-II_v01_M | weights_and_design | accepted_via_promoted_registry | No action for this dashboard; keep registry/data lineage reproducible. |
| 1 | MWI_2004_IHS-II_v01_M | consumption_or_income | accepted_via_promoted_registry | No action for this dashboard; keep registry/data lineage reproducible. |
| 1 | MWI_2004_IHS-II_v01_M | oop_health_expenditure | accepted_via_promoted_registry | No action for this dashboard; keep registry/data lineage reproducible. |
| 1 | MWI_2004_IHS-II_v01_M | health_need_and_access | accepted_via_promoted_registry | No action for this dashboard; keep registry/data lineage reproducible. |
| 1 | MWI_2004_IHS-II_v01_M | survey_timing | accepted_via_promoted_registry | No action for this dashboard; keep registry/data lineage reproducible. |
| 1 | MWI_2004_IHS-II_v01_M | climate_geography | accepted_via_promoted_registry | No action for this dashboard; keep registry/data lineage reproducible. |
| 1 | MWI_2004_IHS-II_v01_M | missing_codes_units_recall_skip_patterns | accepted_via_promoted_registry | No action for this dashboard; keep registry/data lineage reproducible. |
| 2 | ETH_2021_ESPS-W5_v02_M | household_person_keys | blocked_raw_package_not_received | Download/place the complete unchanged official package and documentation. |
| 2 | ETH_2021_ESPS-W5_v02_M | weights_and_design | blocked_raw_package_not_received | Download/place the complete unchanged official package and documentation. |
| 2 | ETH_2021_ESPS-W5_v02_M | consumption_or_income | blocked_raw_package_not_received | Download/place the complete unchanged official package and documentation. |
| 2 | ETH_2021_ESPS-W5_v02_M | oop_health_expenditure | blocked_raw_package_not_received | Download/place the complete unchanged official package and documentation. |
| 2 | ETH_2021_ESPS-W5_v02_M | health_need_and_access | blocked_raw_package_not_received | Download/place the complete unchanged official package and documentation. |
| 2 | ETH_2021_ESPS-W5_v02_M | survey_timing | blocked_raw_package_not_received | Download/place the complete unchanged official package and documentation. |
| 2 | ETH_2021_ESPS-W5_v02_M | climate_geography | blocked_raw_package_not_received | Download/place the complete unchanged official package and documentation. |
| 2 | ETH_2021_ESPS-W5_v02_M | missing_codes_units_recall_skip_patterns | blocked_raw_package_not_received | Download/place the complete unchanged official package and documentation. |
| 3 | ETH_2018_ESS_v04_M | household_person_keys | blocked_raw_package_not_received | Download/place the complete unchanged official package and documentation. |
| 3 | ETH_2018_ESS_v04_M | weights_and_design | blocked_raw_package_not_received | Download/place the complete unchanged official package and documentation. |
| 3 | ETH_2018_ESS_v04_M | consumption_or_income | blocked_raw_package_not_received | Download/place the complete unchanged official package and documentation. |
| 3 | ETH_2018_ESS_v04_M | oop_health_expenditure | blocked_raw_package_not_received | Download/place the complete unchanged official package and documentation. |
| 3 | ETH_2018_ESS_v04_M | health_need_and_access | blocked_raw_package_not_received | Download/place the complete unchanged official package and documentation. |
| 3 | ETH_2018_ESS_v04_M | survey_timing | blocked_raw_package_not_received | Download/place the complete unchanged official package and documentation. |
| 3 | ETH_2018_ESS_v04_M | climate_geography | blocked_raw_package_not_received | Download/place the complete unchanged official package and documentation. |
| 3 | ETH_2018_ESS_v04_M | missing_codes_units_recall_skip_patterns | blocked_raw_package_not_received | Download/place the complete unchanged official package and documentation. |
| 4 | NGA_2012_GHSP-W2_v02_M | household_person_keys | blocked_raw_package_not_received | Download/place the complete unchanged official package and documentation. |
| 4 | NGA_2012_GHSP-W2_v02_M | weights_and_design | blocked_raw_package_not_received | Download/place the complete unchanged official package and documentation. |
| 4 | NGA_2012_GHSP-W2_v02_M | consumption_or_income | blocked_raw_package_not_received | Download/place the complete unchanged official package and documentation. |
| 4 | NGA_2012_GHSP-W2_v02_M | oop_health_expenditure | blocked_raw_package_not_received | Download/place the complete unchanged official package and documentation. |
| 4 | NGA_2012_GHSP-W2_v02_M | health_need_and_access | blocked_raw_package_not_received | Download/place the complete unchanged official package and documentation. |
| 4 | NGA_2012_GHSP-W2_v02_M | survey_timing | blocked_raw_package_not_received | Download/place the complete unchanged official package and documentation. |
| 4 | NGA_2012_GHSP-W2_v02_M | climate_geography | blocked_raw_package_not_received | Download/place the complete unchanged official package and documentation. |
| 4 | NGA_2012_GHSP-W2_v02_M | missing_codes_units_recall_skip_patterns | blocked_raw_package_not_received | Download/place the complete unchanged official package and documentation. |
| 5 | NGA_2015_GHSP-W3_v02_M | household_person_keys | blocked_raw_package_not_received | Download/place the complete unchanged official package and documentation. |
| 5 | NGA_2015_GHSP-W3_v02_M | weights_and_design | blocked_raw_package_not_received | Download/place the complete unchanged official package and documentation. |
| 5 | NGA_2015_GHSP-W3_v02_M | consumption_or_income | blocked_raw_package_not_received | Download/place the complete unchanged official package and documentation. |
| 5 | NGA_2015_GHSP-W3_v02_M | oop_health_expenditure | blocked_raw_package_not_received | Download/place the complete unchanged official package and documentation. |
| 5 | NGA_2015_GHSP-W3_v02_M | health_need_and_access | blocked_raw_package_not_received | Download/place the complete unchanged official package and documentation. |
| 5 | NGA_2015_GHSP-W3_v02_M | survey_timing | blocked_raw_package_not_received | Download/place the complete unchanged official package and documentation. |
| 5 | NGA_2015_GHSP-W3_v02_M | climate_geography | blocked_raw_package_not_received | Download/place the complete unchanged official package and documentation. |
| 5 | NGA_2015_GHSP-W3_v02_M | missing_codes_units_recall_skip_patterns | blocked_raw_package_not_received | Download/place the complete unchanged official package and documentation. |
| 6 | NGA_2010_GHSP-W1_v03_M | household_person_keys | blocked_raw_package_not_received | Download/place the complete unchanged official package and documentation. |
| 6 | NGA_2010_GHSP-W1_v03_M | weights_and_design | blocked_raw_package_not_received | Download/place the complete unchanged official package and documentation. |
| 6 | NGA_2010_GHSP-W1_v03_M | consumption_or_income | blocked_raw_package_not_received | Download/place the complete unchanged official package and documentation. |
| 6 | NGA_2010_GHSP-W1_v03_M | oop_health_expenditure | blocked_raw_package_not_received | Download/place the complete unchanged official package and documentation. |
| 6 | NGA_2010_GHSP-W1_v03_M | health_need_and_access | blocked_raw_package_not_received | Download/place the complete unchanged official package and documentation. |
| 6 | NGA_2010_GHSP-W1_v03_M | survey_timing | blocked_raw_package_not_received | Download/place the complete unchanged official package and documentation. |
| 6 | NGA_2010_GHSP-W1_v03_M | climate_geography | blocked_raw_package_not_received | Download/place the complete unchanged official package and documentation. |
| 6 | NGA_2010_GHSP-W1_v03_M | missing_codes_units_recall_skip_patterns | blocked_raw_package_not_received | Download/place the complete unchanged official package and documentation. |
| 7 | TZA_2008_NPS-R1_v03_M | household_person_keys | blocked_raw_package_not_received | Download/place the complete unchanged official package and documentation. |
| 7 | TZA_2008_NPS-R1_v03_M | weights_and_design | blocked_raw_package_not_received | Download/place the complete unchanged official package and documentation. |
| 7 | TZA_2008_NPS-R1_v03_M | consumption_or_income | blocked_raw_package_not_received | Download/place the complete unchanged official package and documentation. |
| 7 | TZA_2008_NPS-R1_v03_M | oop_health_expenditure | blocked_raw_package_not_received | Download/place the complete unchanged official package and documentation. |
| 7 | TZA_2008_NPS-R1_v03_M | health_need_and_access | blocked_raw_package_not_received | Download/place the complete unchanged official package and documentation. |
| 7 | TZA_2008_NPS-R1_v03_M | survey_timing | blocked_raw_package_not_received | Download/place the complete unchanged official package and documentation. |
| 7 | TZA_2008_NPS-R1_v03_M | climate_geography | blocked_raw_package_not_received | Download/place the complete unchanged official package and documentation. |
| 7 | TZA_2008_NPS-R1_v03_M | missing_codes_units_recall_skip_patterns | blocked_raw_package_not_received | Download/place the complete unchanged official package and documentation. |
| 8 | TZA_2010_NPS-R2_v03_M | household_person_keys | blocked_raw_package_not_received | Download/place the complete unchanged official package and documentation. |
| 8 | TZA_2010_NPS-R2_v03_M | weights_and_design | blocked_raw_package_not_received | Download/place the complete unchanged official package and documentation. |
| 8 | TZA_2010_NPS-R2_v03_M | consumption_or_income | blocked_raw_package_not_received | Download/place the complete unchanged official package and documentation. |
| 8 | TZA_2010_NPS-R2_v03_M | oop_health_expenditure | blocked_raw_package_not_received | Download/place the complete unchanged official package and documentation. |
| 8 | TZA_2010_NPS-R2_v03_M | health_need_and_access | blocked_raw_package_not_received | Download/place the complete unchanged official package and documentation. |
| 8 | TZA_2010_NPS-R2_v03_M | survey_timing | blocked_raw_package_not_received | Download/place the complete unchanged official package and documentation. |
| 8 | TZA_2010_NPS-R2_v03_M | climate_geography | blocked_raw_package_not_received | Download/place the complete unchanged official package and documentation. |
| 8 | TZA_2010_NPS-R2_v03_M | missing_codes_units_recall_skip_patterns | blocked_raw_package_not_received | Download/place the complete unchanged official package and documentation. |
| 9 | TZA_2012_NPS-R3_v01_M | household_person_keys | blocked_raw_package_not_received | Download/place the complete unchanged official package and documentation. |
| 9 | TZA_2012_NPS-R3_v01_M | weights_and_design | blocked_raw_package_not_received | Download/place the complete unchanged official package and documentation. |
| 9 | TZA_2012_NPS-R3_v01_M | consumption_or_income | blocked_raw_package_not_received | Download/place the complete unchanged official package and documentation. |
| 9 | TZA_2012_NPS-R3_v01_M | oop_health_expenditure | blocked_raw_package_not_received | Download/place the complete unchanged official package and documentation. |
| 9 | TZA_2012_NPS-R3_v01_M | health_need_and_access | blocked_raw_package_not_received | Download/place the complete unchanged official package and documentation. |
| 9 | TZA_2012_NPS-R3_v01_M | survey_timing | blocked_raw_package_not_received | Download/place the complete unchanged official package and documentation. |
| 9 | TZA_2012_NPS-R3_v01_M | climate_geography | blocked_raw_package_not_received | Download/place the complete unchanged official package and documentation. |
| 9 | TZA_2012_NPS-R3_v01_M | missing_codes_units_recall_skip_patterns | blocked_raw_package_not_received | Download/place the complete unchanged official package and documentation. |
| 10 | UGA_2019_UNPS_v03_M | household_person_keys | blocked_raw_package_not_received | Download/place the complete unchanged official package and documentation. |
| 10 | UGA_2019_UNPS_v03_M | weights_and_design | blocked_raw_package_not_received | Download/place the complete unchanged official package and documentation. |
| 10 | UGA_2019_UNPS_v03_M | consumption_or_income | blocked_raw_package_not_received | Download/place the complete unchanged official package and documentation. |
| 10 | UGA_2019_UNPS_v03_M | oop_health_expenditure | blocked_raw_package_not_received | Download/place the complete unchanged official package and documentation. |
| 10 | UGA_2019_UNPS_v03_M | health_need_and_access | blocked_raw_package_not_received | Download/place the complete unchanged official package and documentation. |
| 10 | UGA_2019_UNPS_v03_M | survey_timing | blocked_raw_package_not_received | Download/place the complete unchanged official package and documentation. |
| 10 | UGA_2019_UNPS_v03_M | climate_geography | blocked_raw_package_not_received | Download/place the complete unchanged official package and documentation. |
| 10 | UGA_2019_UNPS_v03_M | missing_codes_units_recall_skip_patterns | blocked_raw_package_not_received | Download/place the complete unchanged official package and documentation. |
| ... | ... | ... | ... | ... |

## Rule

Only rows with `promoted_analysis_ready` in
`result/promoted_country_wave_registry.csv` can be represented in `data/`.
Rows that merely have metadata, endpoint evidence, or public documentation
remain blocked until complete official raw packages and raw-backed value,
semantics, timing, geography, and climate-linkage gates pass.
