# Priority LSMS/ISA Threshold Replacement Plan

Status: replacement and buffer plan for the minimum LSMS/ISA download batch.

This plan keeps the modeling gate blocked. It only explains how to preserve the
6-country and 10-country-wave thresholds if a minimum-batch raw package cannot
be obtained or later fails receipt, raw-value, outcome, timing/geography, or
climate-linkage gates.

## Summary

| metric | value | interpretation |
| --- | --- | --- |
| priority_lsms_replacement_backup_candidate_rows | 8 | Backup country-waves available after the current minimum batch. |
| priority_lsms_replacement_scenario_rows | 10 | Single minimum-batch failure scenarios evaluated. |
| priority_lsms_replacement_strategy_rows | 3 | Download-batch strategy rows evaluated. |
| priority_lsms_replacement_required_for_threshold_rows | 2 | Failure scenarios where a replacement is required to keep 6 countries and 10 waves. |
| priority_lsms_replacement_optional_buffer_rows | 8 | Failure scenarios where thresholds still pass but the one-wave buffer is lost. |
| priority_lsms_replacement_priority_country_backup_rows | 6 | Backup rows from the priority country set. |
| priority_lsms_replacement_new_country_backup_rows | 2 | Backup rows that can add a new country for the 6-country threshold. |
| priority_lsms_replacement_strict_priority_countries | 5 | Countries covered if Nepal and all other non-priority countries are excluded. |
| priority_lsms_replacement_strict_priority_waves | 10 | Country-waves covered if Nepal and all other non-priority countries are excluded. |
| priority_lsms_replacement_current_minimum_countries | 6 | Countries covered by the current minimum batch if all rows pass. |
| priority_lsms_replacement_current_minimum_waves | 11 | Country-waves covered by the current minimum batch if all rows pass. |
| priority_lsms_replacement_top_selected_replacement_ids | MWI_2019_IHS-V_v06_M:8;UGA_2011_UNPS_v02_M:1;JAM_1997_SLC_v01_M:1 | Replacement IDs selected across single-failure scenarios. |
| priority_lsms_replacement_data_write_status | blocked_no_data_write | Replacement planning never writes promoted data. |
| modeling_gate_status | blocked | No predictive, reduced-form, causal ML, or policy learning until registry thresholds pass. |

## Strategy Check

| strategy | countries_if_all_pass | country_waves_if_all_pass | priority_country_rows | nonpriority_country_rows | country_threshold_status | wave_threshold_status |
| --- | --- | --- | --- | --- | --- | --- |
| current_minimum_batch_all_passes | 6 | 11 | 10 | 1 | passes | passes |
| strict_five_priority_countries_only | 5 | 10 | 10 | 0 | fails_short_by_1 | passes |
| priority_countries_plus_first_sixth_country | 6 | 11 | 10 | 1 | passes | passes |

## Single-Failure Replacement Scenarios

| failed_minimum_idno | countries_after_failure_without_replacement | waves_after_failure_without_replacement | replacement_required_for_threshold | selected_replacement_idno | selected_replacement_reason | countries_after_selected_replacement | waves_after_selected_replacement |
| --- | --- | --- | --- | --- | --- | --- | --- |
| ETH_2021_ESPS-W5_v02_M | 6 | 10 | 0 | MWI_2019_IHS-V_v06_M | optional_buffer_to_restore_11th_wave_after_single_wave_failure | 6 | 11 |
| ETH_2018_ESS_v04_M | 6 | 10 | 0 | MWI_2019_IHS-V_v06_M | optional_buffer_to_restore_11th_wave_after_single_wave_failure | 6 | 11 |
| NGA_2012_GHSP-W2_v02_M | 6 | 10 | 0 | MWI_2019_IHS-V_v06_M | optional_buffer_to_restore_11th_wave_after_single_wave_failure | 6 | 11 |
| NGA_2015_GHSP-W3_v02_M | 6 | 10 | 0 | MWI_2019_IHS-V_v06_M | optional_buffer_to_restore_11th_wave_after_single_wave_failure | 6 | 11 |
| NGA_2010_GHSP-W1_v03_M | 6 | 10 | 0 | MWI_2019_IHS-V_v06_M | optional_buffer_to_restore_11th_wave_after_single_wave_failure | 6 | 11 |
| TZA_2008_NPS-R1_v03_M | 6 | 10 | 0 | MWI_2019_IHS-V_v06_M | optional_buffer_to_restore_11th_wave_after_single_wave_failure | 6 | 11 |
| TZA_2010_NPS-R2_v03_M | 6 | 10 | 0 | MWI_2019_IHS-V_v06_M | optional_buffer_to_restore_11th_wave_after_single_wave_failure | 6 | 11 |
| TZA_2012_NPS-R3_v01_M | 6 | 10 | 0 | MWI_2019_IHS-V_v06_M | optional_buffer_to_restore_11th_wave_after_single_wave_failure | 6 | 11 |
| UGA_2019_UNPS_v03_M | 5 | 10 | 1 | UGA_2011_UNPS_v02_M | selected_to_restore_failed_country_or_wave_threshold | 6 | 11 |
| NPL_2010_LSS-III_v01_M | 5 | 10 | 1 | JAM_1997_SLC_v01_M | selected_to_restore_failed_country_or_wave_threshold | 6 | 11 |

## Backup Candidate Rank

| backup_rank | candidate_priority_group | country | wave | idno | same_country_backup_for | replacement_use_case |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | sixth_country_replacement | Jamaica | 1997 | JAM_1997_SLC_v01_M |  | Use if the sixth-country candidate fails or a whole priority country drops out and a ne... |
| 2 | sixth_country_replacement | Kyrgyz Republic | 1993 | KGZ_1993_KMPS_v01_M |  | Use if the sixth-country candidate fails or a whole priority country drops out and a ne... |
| 3 | priority_country_wave_buffer | Malawi | 2019-2020 | MWI_2019_IHS-V_v06_M |  | Use to restore the 10-wave buffer inside the priority-country family; it does not add a... |
| 4 | priority_country_wave_buffer | Malawi | 2016-2017 | MWI_2016_IHS-IV_v04_M |  | Use to restore the 10-wave buffer inside the priority-country family; it does not add a... |
| 5 | priority_country_wave_buffer | Malawi | 2010-2011 | MWI_2010_IHS-III_v01_M |  | Use to restore the 10-wave buffer inside the priority-country family; it does not add a... |
| 6 | priority_country_wave_buffer | Uganda | 2011-2012 | UGA_2011_UNPS_v02_M | Uganda | Use first if UGA_2019_UNPS_v03_M fails; keeps Uganda in the priority-country set and re... |
| 7 | priority_country_wave_buffer | Uganda | 2018-2019 | UGA_2018_UNPS_v02_M | Uganda | Use first if UGA_2019_UNPS_v03_M fails; keeps Uganda in the priority-country set and re... |
| 8 | priority_country_wave_buffer | Uganda | 2015-2016 | UGA_2015_UNPS_v02_M | Uganda | Use first if UGA_2019_UNPS_v03_M fails; keeps Uganda in the priority-country set and re... |

## Interpretation

The strict five-priority-country set can reach 10 waves but not 6 countries.
That means a sixth-country candidate is still required for the financial-
protection country threshold. Nepal is the current sixth-country candidate.
If Nepal fails, the first viable non-priority backup country should be used.
Malawi and Uganda backups are still useful as wave buffers, but they do not add
a new country when Malawi 2004 and Uganda 2019 remain in the batch.
