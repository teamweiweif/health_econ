# Priority LSMS/ISA Acquisition-to-Promotion Handoff

Status: executable handoff from raw-package acquisition to receipt,
raw-value, climate-linkage, promotion-packet, and registry-refresh gates.

It does not download, copy, extract, write promoted `data/`, or run models.

## Summary

| metric | value | interpretation |
| --- | --- | --- |
| acquisition_to_promotion_handoff_rows | 19 | Registry country-waves mapped to the next acquisition or promotion stage. |
| acquisition_to_promotion_gate_rows | 209 | Verification-gate checklist rows across registry country-waves. |
| acquisition_to_promotion_minimum_batch_acquire_rows | 10 | Minimum-batch rows still requiring official raw package acquisition. |
| acquisition_to_promotion_promoted_keep_current_rows | 1 | Rows already promoted and held in place. |
| acquisition_to_promotion_raw_validation_ready_rows | 0 | Rows with raw-like files present but validation still required. |
| acquisition_to_promotion_acquire_raw_rows | 18 | Rows still blocked at raw acquisition. |
| data_write_gate_status | blocked_no_new_data_write | No new promoted data writes are opened by this handoff. |
| modeling_gate_status | blocked | No predictive, reduced-form, causal ML, or policy learning is opened. |

## Handoff Rows

| country | wave | idno | minimum_batch_row | raw_like_file_count | handoff_stage | next_required_action |
| --- | --- | --- | --- | --- | --- | --- |
| Ethiopia | 2021-2022 | ETH_2021_ESPS-W5_v02_M | 1 | 0 | acquire_official_raw_package | Download or manually place the complete unchanged official raw package and documentation. |
| Ethiopia | 2018-2019 | ETH_2018_ESS_v04_M | 1 | 0 | acquire_official_raw_package | Download or manually place the complete unchanged official raw package and documentation. |
| Malawi | 2004-2005 | MWI_2004_IHS-II_v01_M | 0 | 1 | promoted_keep_current | Keep promoted dataset and registry; no modeling until threshold is met. |
| Nigeria | 2012-2013 | NGA_2012_GHSP-W2_v02_M | 1 | 0 | acquire_official_raw_package | Download or manually place the complete unchanged official raw package and documentation. |
| Nigeria | 2015-2016 | NGA_2015_GHSP-W3_v02_M | 1 | 0 | acquire_official_raw_package | Download or manually place the complete unchanged official raw package and documentation. |
| Nigeria | 2010-2011 | NGA_2010_GHSP-W1_v03_M | 1 | 0 | acquire_official_raw_package | Download or manually place the complete unchanged official raw package and documentation. |
| Tanzania | 2008-2009 | TZA_2008_NPS-R1_v03_M | 1 | 0 | acquire_official_raw_package | Download or manually place the complete unchanged official raw package and documentation. |
| Tanzania | 2010-2011 | TZA_2010_NPS-R2_v03_M | 1 | 0 | acquire_official_raw_package | Download or manually place the complete unchanged official raw package and documentation. |
| Tanzania | 2012-2013 | TZA_2012_NPS-R3_v01_M | 1 | 0 | acquire_official_raw_package | Download or manually place the complete unchanged official raw package and documentation. |
| Uganda | 2019-2020 | UGA_2019_UNPS_v03_M | 1 | 0 | acquire_official_raw_package | Download or manually place the complete unchanged official raw package and documentation. |
| Jamaica | 1997 | JAM_1997_SLC_v01_M | 0 | 0 | acquire_official_raw_package | Download or manually place the complete unchanged official raw package and documentation. |
| Kyrgyz Republic | 1993 | KGZ_1993_KMPS_v01_M | 0 | 0 | acquire_official_raw_package | Download or manually place the complete unchanged official raw package and documentation. |
| Nepal | 2010-2011 | NPL_2010_LSS-III_v01_M | 1 | 0 | acquire_official_raw_package | Download or manually place the complete unchanged official raw package and documentation. |
| Malawi | 2019-2020 | MWI_2019_IHS-V_v06_M | 0 | 0 | acquire_official_raw_package | Download or manually place the complete unchanged official raw package and documentation. |
| Malawi | 2016-2017 | MWI_2016_IHS-IV_v04_M | 0 | 0 | acquire_official_raw_package | Download or manually place the complete unchanged official raw package and documentation. |
| Malawi | 2010-2011 | MWI_2010_IHS-III_v01_M | 0 | 0 | acquire_official_raw_package | Download or manually place the complete unchanged official raw package and documentation. |
| Uganda | 2011-2012 | UGA_2011_UNPS_v02_M | 0 | 0 | acquire_official_raw_package | Download or manually place the complete unchanged official raw package and documentation. |
| Uganda | 2018-2019 | UGA_2018_UNPS_v02_M | 0 | 0 | acquire_official_raw_package | Download or manually place the complete unchanged official raw package and documentation. |
| Uganda | 2015-2016 | UGA_2015_UNPS_v02_M | 0 | 0 | acquire_official_raw_package | Download or manually place the complete unchanged official raw package and documentation. |

## Gate Checklist Preview

| idno | verification_gate | gate_status | gate_blocker |
| --- | --- | --- | --- |
| ETH_2021_ESPS-W5_v02_M | complete_original_raw_package | blocked_raw_package_absent | Complete unchanged official raw package is not locally present. |
| ETH_2021_ESPS-W5_v02_M | household_person_merge_keys | blocked_raw_package_absent | Complete unchanged official raw package is not locally present. |
| ETH_2021_ESPS-W5_v02_M | household_weights_survey_design | blocked_raw_package_absent | Complete unchanged official raw package is not locally present. |
| ETH_2021_ESPS-W5_v02_M | consumption_or_income_aggregate | blocked_raw_package_absent | Complete unchanged official raw package is not locally present. |
| ETH_2021_ESPS-W5_v02_M | oop_health_expenditure | blocked_raw_package_absent | Complete unchanged official raw package is not locally present. |
| ETH_2021_ESPS-W5_v02_M | illness_need_care_access | blocked_raw_package_absent | Complete unchanged official raw package is not locally present. |
| ETH_2021_ESPS-W5_v02_M | survey_timing | blocked_raw_package_absent | Complete unchanged official raw package is not locally present. |
| ETH_2021_ESPS-W5_v02_M | geography_climate_anchor | blocked_raw_package_absent | Complete unchanged official raw package is not locally present. |
| ETH_2021_ESPS-W5_v02_M | missing_units_recall_skip_patterns | blocked_raw_package_absent | Complete unchanged official raw package is not locally present. |
| ETH_2021_ESPS-W5_v02_M | climate_linkage_route | blocked_raw_package_absent | Complete unchanged official raw package is not locally present. |
| ETH_2021_ESPS-W5_v02_M | promotion_packet_registry | blocked_raw_package_absent | Complete unchanged official raw package is not locally present. |
| ETH_2018_ESS_v04_M | complete_original_raw_package | blocked_raw_package_absent | Complete unchanged official raw package is not locally present. |
| ETH_2018_ESS_v04_M | household_person_merge_keys | blocked_raw_package_absent | Complete unchanged official raw package is not locally present. |
| ETH_2018_ESS_v04_M | household_weights_survey_design | blocked_raw_package_absent | Complete unchanged official raw package is not locally present. |
| ETH_2018_ESS_v04_M | consumption_or_income_aggregate | blocked_raw_package_absent | Complete unchanged official raw package is not locally present. |
| ETH_2018_ESS_v04_M | oop_health_expenditure | blocked_raw_package_absent | Complete unchanged official raw package is not locally present. |
| ETH_2018_ESS_v04_M | illness_need_care_access | blocked_raw_package_absent | Complete unchanged official raw package is not locally present. |
| ETH_2018_ESS_v04_M | survey_timing | blocked_raw_package_absent | Complete unchanged official raw package is not locally present. |
| ETH_2018_ESS_v04_M | geography_climate_anchor | blocked_raw_package_absent | Complete unchanged official raw package is not locally present. |
| ETH_2018_ESS_v04_M | missing_units_recall_skip_patterns | blocked_raw_package_absent | Complete unchanged official raw package is not locally present. |
| ETH_2018_ESS_v04_M | climate_linkage_route | blocked_raw_package_absent | Complete unchanged official raw package is not locally present. |
| ETH_2018_ESS_v04_M | promotion_packet_registry | blocked_raw_package_absent | Complete unchanged official raw package is not locally present. |
| MWI_2004_IHS-II_v01_M | complete_original_raw_package | passed_current_promoted_scope |  |
| MWI_2004_IHS-II_v01_M | household_person_merge_keys | passed_current_promoted_scope |  |
| MWI_2004_IHS-II_v01_M | household_weights_survey_design | passed_current_promoted_scope |  |
| MWI_2004_IHS-II_v01_M | consumption_or_income_aggregate | passed_current_promoted_scope |  |
| MWI_2004_IHS-II_v01_M | oop_health_expenditure | passed_current_promoted_scope |  |
| MWI_2004_IHS-II_v01_M | illness_need_care_access | passed_current_promoted_scope |  |
| MWI_2004_IHS-II_v01_M | survey_timing | passed_current_promoted_scope |  |
| MWI_2004_IHS-II_v01_M | geography_climate_anchor | passed_current_promoted_scope |  |
| MWI_2004_IHS-II_v01_M | missing_units_recall_skip_patterns | passed_current_promoted_scope |  |
| MWI_2004_IHS-II_v01_M | climate_linkage_route | passed_current_promoted_scope |  |
| MWI_2004_IHS-II_v01_M | promotion_packet_registry | passed_current_promoted_scope |  |
| NGA_2012_GHSP-W2_v02_M | complete_original_raw_package | blocked_raw_package_absent | Complete unchanged official raw package is not locally present. |
| NGA_2012_GHSP-W2_v02_M | household_person_merge_keys | blocked_raw_package_absent | Complete unchanged official raw package is not locally present. |
| NGA_2012_GHSP-W2_v02_M | household_weights_survey_design | blocked_raw_package_absent | Complete unchanged official raw package is not locally present. |
| NGA_2012_GHSP-W2_v02_M | consumption_or_income_aggregate | blocked_raw_package_absent | Complete unchanged official raw package is not locally present. |
| NGA_2012_GHSP-W2_v02_M | oop_health_expenditure | blocked_raw_package_absent | Complete unchanged official raw package is not locally present. |
| NGA_2012_GHSP-W2_v02_M | illness_need_care_access | blocked_raw_package_absent | Complete unchanged official raw package is not locally present. |
| NGA_2012_GHSP-W2_v02_M | survey_timing | blocked_raw_package_absent | Complete unchanged official raw package is not locally present. |
| ... | ... | ... | ... |

## Outputs

- `result/priority_lsms_isa_acquisition_to_promotion_handoff.csv`
- `result/priority_lsms_isa_acquisition_to_promotion_gate_checklist.csv`
- `result/priority_lsms_isa_acquisition_to_promotion_handoff_summary.csv`

## Stop Rule

This handoff is not a promotion decision. A country-wave can enter `data/` only
after all required receipt, raw-value, semantics, timing/geography, and
climate-linkage gates pass and the promoted registry is refreshed.
