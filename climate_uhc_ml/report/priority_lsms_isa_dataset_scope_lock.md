# Priority LSMS/ISA Dataset Scope Lock

Status: locked target scope for the dataset-promotion campaign.

This artifact answers what dataset is being built before any new modeling:
the target is a six-country, 11-country-wave LSMS/ISA-centered household
microdata scope, with one current promoted anchor and 10 official raw packages
still requiring acquisition and validation.

It does not download, copy, extract, write promoted `data/`, or run models.

## Summary

| metric | value | interpretation |
| --- | --- | --- |
| dataset_scope_lock_rows | 11 | Locked target country-wave rows in the threshold scope. |
| dataset_scope_lock_country_rows | 6 | Countries represented if all locked target rows pass promotion gates. |
| dataset_scope_lock_priority_country_rows | 5 | Priority countries represented in the locked scope. |
| dataset_scope_lock_priority_country_wave_rows | 10 | Locked target rows from Ethiopia, Nigeria, Malawi, Tanzania, and Uganda. |
| dataset_scope_lock_nonpriority_country_wave_rows | 1 | Locked target rows outside the five priority countries. |
| dataset_scope_lock_download_required_rows | 10 | Rows still requiring official raw-package acquisition. |
| dataset_scope_lock_promoted_anchor_rows | 1 | Rows already promoted and serving as current anchors. |
| dataset_scope_lock_raw_missing_download_required_rows | 10 | Download-required rows with no local raw-like files yet. |
| dataset_scope_lock_wave_period_min | 2004-2005 | Earliest wave label in the locked target scope. |
| dataset_scope_lock_wave_period_max | 2021-2022 | Latest wave label in the locked target scope. |
| dataset_scope_lock_gate_matrix_rows | 5 | Scenario/gate rows explaining implemented, download-required, priority-only, and sixth-country scope. |
| dataset_scope_lock_replacement_backup_candidate_rows | 8 | Backup candidates available if the locked sixth-country or priority waves fail. |
| data_write_gate_status | blocked_no_data_write | Scope lock writes only audit artifacts and does not promote datasets. |
| modeling_gate_status | blocked | No predictive, reduced-form, causal ML, or policy learning is opened. |

## Gate Matrix

| gate_name | country_rows | country_wave_rows | priority_country_wave_rows | nonpriority_country_wave_rows | promoted_analysis_ready_rows | download_required_rows | raw_missing_download_required_rows | country_threshold_status | wave_threshold_status |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| current_implemented_promoted_registry | 1 | 1 | 1 | 0 | 1 | 0 | 0 | fails_short_by_5 | fails_short_by_9 |
| manual_download_required_execution_board | 5 | 10 | 9 | 1 | 0 | 10 | 10 | fails_short_by_1 | passes |
| strict_five_priority_countries_only | 5 | 10 | 10 | 0 | 1 | 9 | 9 | fails_short_by_1 | passes |
| locked_threshold_scope_with_sixth_country | 6 | 11 | 10 | 1 | 1 | 10 | 10 | passes | passes |
| scope_if_nepal_sixth_country_removed | 5 | 10 | 10 | 0 | 1 | 9 | 9 | fails_short_by_1 | passes |

## Locked Scope Rows

| scope_rank | country | wave | idno | scope_role | download_required | current_promoted_anchor | target_status |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | Ethiopia | 2021-2022 | ETH_2021_ESPS-W5_v02_M | download_required_priority_country_wave | 1 | 0 | blocked_download_required_raw_absent |
| 2 | Ethiopia | 2018-2019 | ETH_2018_ESS_v04_M | download_required_priority_country_wave | 1 | 0 | blocked_download_required_raw_absent |
| 3 | Malawi | 2004-2005 | MWI_2004_IHS-II_v01_M | current_promoted_anchor | 0 | 1 | implemented_promoted_anchor |
| 4 | Nigeria | 2012-2013 | NGA_2012_GHSP-W2_v02_M | download_required_priority_country_wave | 1 | 0 | blocked_download_required_raw_absent |
| 5 | Nigeria | 2015-2016 | NGA_2015_GHSP-W3_v02_M | download_required_priority_country_wave | 1 | 0 | blocked_download_required_raw_absent |
| 6 | Nigeria | 2010-2011 | NGA_2010_GHSP-W1_v03_M | download_required_priority_country_wave | 1 | 0 | blocked_download_required_raw_absent |
| 7 | Tanzania | 2008-2009 | TZA_2008_NPS-R1_v03_M | download_required_priority_country_wave | 1 | 0 | blocked_download_required_raw_absent |
| 8 | Tanzania | 2010-2011 | TZA_2010_NPS-R2_v03_M | download_required_priority_country_wave | 1 | 0 | blocked_download_required_raw_absent |
| 9 | Tanzania | 2012-2013 | TZA_2012_NPS-R3_v01_M | download_required_priority_country_wave | 1 | 0 | blocked_download_required_raw_absent |
| 10 | Uganda | 2019-2020 | UGA_2019_UNPS_v03_M | download_required_priority_country_wave | 1 | 0 | blocked_download_required_raw_absent |
| 11 | Nepal | 2010-2011 | NPL_2010_LSS-III_v01_M | download_required_sixth_country_candidate | 1 | 0 | blocked_download_required_raw_absent |

## Interpretation

- Implemented now: Malawi 2004-2005 is the only promoted analysis-ready anchor.
- Still required: 10 official raw packages must be acquired and pass receipt,
  schema, raw-value, semantics, timing/geography, climate-linkage, and
  promotion-packet gates.
- Priority-country only scope reaches 10 waves but only five countries.
- Nepal is the current sixth-country candidate; if it fails, the replacement
  plan must supply another non-priority country.
- Modeling remains blocked.
