# Priority LSMS-ISA Alignment Audit

Status: fail-closed family-alignment audit for the current 13-wave
priority/backup campaign. This audit corrects the acquisition plan before
manual credentialed downloads by separating usable execution packets from
country-wave family suitability.

## Bottom Line

- The current campaign covers the five named priority countries, but two core
  country-waves are off-family for the LSMS/LSMS-ISA objective.
- Malawi is currently represented by MTM, a specialized panel, while stronger
  Malawi IHS/IHPS candidates are already present in the screening inventory.
- Uganda is currently represented by SAGE, a social-protection impact
  evaluation, while Uganda UNPS candidates are already present in the screening
  inventory.
- No raw data or promoted data were created. Modeling remains blocked.

## Summary

| Metric | Value | Interpretation |
|---|---:|---|
| priority_lsms_alignment_current_campaign_rows | 13 | Current priority/backup campaign rows audited for LSMS/ISA alignment. |
| priority_lsms_alignment_core_priority_wave_rows | 10 | Core 10-wave campaign rows. |
| priority_lsms_alignment_backup_wave_rows | 3 | Backup wave rows outside the five-country LSMS/ISA core requirement. |
| priority_lsms_alignment_required_priority_countries | 5 | Required priority countries from the LSMS/ISA-centered goal. |
| priority_lsms_alignment_current_required_countries | 5 | Required priority countries represented in the current core campaign. |
| priority_lsms_alignment_aligned_core_wave_rows | 8 | Current core rows that are family-aligned with LSMS/ISA or LSMS-style panels. |
| priority_lsms_alignment_off_family_core_wave_rows | 2 | Current core rows that should not be used as the LSMS/ISA main sample without replacement or augmentation. |
| priority_lsms_alignment_off_family_core_country_rows | 2 | Core priority countries affected by off-family current waves. |
| priority_lsms_alignment_replacement_candidate_rows | 17 | Candidate rows found for replacing or documenting off-family Malawi/Uganda waves. |
| priority_lsms_alignment_strong_replacement_candidate_rows | 15 | Strong LSMS/ISA replacement candidates not already selected in the current campaign. |
| priority_lsms_alignment_inventory_gap_rows | 0 | Off-family core countries without a strong LSMS/ISA replacement in the current screening inventory. |
| priority_lsms_alignment_inventory_gap_countries |  | Countries requiring new inventory search if non-empty. |
| priority_lsms_alignment_handoff_readmes_written | 13 | Per-wave alignment handoff files written under temp/raw_downloads. |
| priority_lsms_alignment_campaign_decision | needs_core_wave_replacement_before_manual_download_execution | Campaign-level family-alignment decision before credentialed downloads. |
| modeling_gate_status | blocked | Models remain blocked until raw-backed promotion thresholds and accepted climate linkage pass. |
| priority_lsms_alignment_status_aligned_lsms_isa_or_lsms_panel | 8 | Current campaign row status count. |
| priority_lsms_alignment_status_backup_not_core_five_country_requirement | 3 | Current campaign row status count. |
| priority_lsms_alignment_status_off_family_needs_lsms_isa_replacement_or_augmentation | 1 | Current campaign row status count. |
| priority_lsms_alignment_status_off_family_needs_unps_lsms_isa_replacement_or_augmentation | 1 | Current campaign row status count. |

## Current High-Risk Core Waves

| acquisition_batch_rank | country | wave | idno | current_survey_family | lsms_isa_alignment_status | recommended_replacement_search |
|---|---|---|---|---|---|---|
| 3 | Malawi | 2007-2009 | MWI_2007-2009_MTM_v01_M | non_lsms_specialized_panel | off_family_needs_lsms_isa_replacement_or_augmentation | Prefer Malawi Integrated Household Survey or Integrated Household Panel Survey candidates already in country_wave_scr... |
| 10 | Uganda | 2014 | UGA_2014_SAGE-EL_v01_M | non_lsms_social_protection_evaluation | off_family_needs_unps_lsms_isa_replacement_or_augmentation | Prefer Uganda National Panel Survey candidates already in country_wave_screening.csv. |

## Strong Replacement Candidates

| candidate_rank | country | wave | idno | survey_name | feasibility_score | official_url |
|---|---|---|---|---|---|---|
| 1 | Malawi | 2004-2005 | MWI_2004_IHS-II_v01_M | Second Integrated Household Survey 2004-2005 | 5 | https://microdata.worldbank.org/catalog/2307/get-microdata |
| 2 | Malawi | 2019-2020 | MWI_2019_IHS-V_v06_M | Fifth Integrated Household Survey 2019-2020 | 3 | https://microdata.worldbank.org/catalog/3818/get-microdata |
| 3 | Malawi | 2016-2017 | MWI_2016_IHS-IV_v04_M | Fourth Integrated Household Survey 2016-2017 | 3 | https://microdata.worldbank.org/catalog/2936/get-microdata |
| 4 | Malawi | 2010-2013 | MWI_2010-2013_IHPS_v01_M | Integrated Household Panel Survey 2010-2013 (Short-Term Panel, 204 EAs) | 3 | https://microdata.worldbank.org/catalog/2248/get-microdata |
| 5 | Malawi | 2010-2016 | MWI_2010-2016_IHPS_v03_M | Integrated Household Panel Survey 2010-2013-2016 (Long-Term Panel, 102 EAs) | 3 | https://microdata.worldbank.org/catalog/2939/get-microdata |
| 6 | Malawi | 2010-2011 | MWI_2010_IHS-III_v01_M | Third Integrated Household Survey 2010-2011 | 3 | https://microdata.worldbank.org/catalog/1003/get-microdata |
| 7 | Malawi | 2010-2019 | MWI_2010-2019_IHPS_v06_M | Integrated Household Panel Survey 2010-2013-2016-2019 (Long-Term Panel, 102 EAs) | 2 | https://microdata.worldbank.org/catalog/3819/get-microdata |
| 8 | Malawi | 2010-2011 | MWI_2010_IHS-III_v01_M_v01_A_ML | Integrated Household Living Conditions Survey 2010-2011 ; Subset for Machine Learning Comparative Assessment Project | 2 | https://microdata.worldbank.org/catalog/3016/get-microdata |
| 10 | Uganda | 2019-2020 | UGA_2019_UNPS_v03_M | National Panel Survey 2019-2020 | 4 | https://microdata.worldbank.org/catalog/3902/get-microdata |
| 11 | Uganda | 2018-2019 | UGA_2018_UNPS_v02_M | Uganda National Panel Survey 2018-2019 | 3 | https://microdata.worldbank.org/catalog/3795/get-microdata |
| 12 | Uganda | 2015-2016 | UGA_2015_UNPS_v02_M | National Panel Survey 2015-2016 | 3 | https://microdata.worldbank.org/catalog/3460/get-microdata |
| 13 | Uganda | 2011-2012 | UGA_2011_UNPS_v02_M | National Panel Survey 2011-2012 | 3 | https://microdata.worldbank.org/catalog/2059/get-microdata |
| 14 | Uganda | 2010-2011 | UGA_2010_UNPS_v03_M | National Panel Survey 2010-2011 | 3 | https://microdata.worldbank.org/catalog/2166/get-microdata |
| 15 | Uganda | 2005-2010 | UGA_2005-2009_UNPS_v03_M | National Panel Survey 2005-2009 | 3 | https://microdata.worldbank.org/catalog/1001/get-microdata |
| 16 | Uganda | 2013-2014 | UGA_2013_UNPS_v02_M | National Panel Survey 2013-2014 | 2 | https://microdata.worldbank.org/catalog/2663/get-microdata |

## Full Campaign Audit

| acquisition_batch_rank | batch_role | country | wave | idno | current_survey_family | lsms_isa_alignment_status | alignment_risk |
|---|---|---|---|---|---|---|---|
| 1 | priority_10_wave_batch | Ethiopia | 2021-2022 | ETH_2021_ESPS-W5_v02_M | lsms_isa_socioeconomic_survey | aligned_lsms_isa_or_lsms_panel | low |
| 2 | priority_10_wave_batch | Ethiopia | 2018-2019 | ETH_2018_ESS_v04_M | lsms_isa_socioeconomic_survey | aligned_lsms_isa_or_lsms_panel | low |
| 3 | priority_10_wave_batch | Malawi | 2007-2009 | MWI_2007-2009_MTM_v01_M | non_lsms_specialized_panel | off_family_needs_lsms_isa_replacement_or_augmentation | high |
| 4 | priority_10_wave_batch | Nigeria | 2012-2013 | NGA_2012_GHSP-W2_v02_M | lsms_isa_general_household_panel | aligned_lsms_isa_or_lsms_panel | low |
| 5 | priority_10_wave_batch | Nigeria | 2015-2016 | NGA_2015_GHSP-W3_v02_M | lsms_isa_general_household_panel | aligned_lsms_isa_or_lsms_panel | low |
| 6 | priority_10_wave_batch | Nigeria | 2010-2011 | NGA_2010_GHSP-W1_v03_M | lsms_isa_general_household_panel | aligned_lsms_isa_or_lsms_panel | low |
| 7 | priority_10_wave_batch | Tanzania | 2008-2009 | TZA_2008_NPS-R1_v03_M | lsms_isa_national_panel_survey | aligned_lsms_isa_or_lsms_panel | low |
| 8 | priority_10_wave_batch | Tanzania | 2010-2011 | TZA_2010_NPS-R2_v03_M | lsms_isa_national_panel_survey | aligned_lsms_isa_or_lsms_panel | low |
| 9 | priority_10_wave_batch | Tanzania | 2012-2013 | TZA_2012_NPS-R3_v01_M | lsms_isa_national_panel_survey | aligned_lsms_isa_or_lsms_panel | low |
| 10 | priority_10_wave_batch | Uganda | 2014 | UGA_2014_SAGE-EL_v01_M | non_lsms_social_protection_evaluation | off_family_needs_unps_lsms_isa_replacement_or_augmentation | high |
| 11 | sixth_country_backup_candidate | Jamaica | 1997 | JAM_1997_SLC_v01_M | non_lsms_or_unknown_family | backup_not_core_five_country_requirement | outside_core_scope |
| 12 | sixth_country_backup_candidate | Kyrgyz Republic | 1993 | KGZ_1993_KMPS_v01_M | non_lsms_or_unknown_family | backup_not_core_five_country_requirement | outside_core_scope |
| 13 | sixth_country_backup_candidate | Nepal | 2010-2011 | NPL_2010_LSS-III_v01_M | lsms_living_standards_survey | backup_not_core_five_country_requirement | outside_core_scope |

## Machine-Readable Outputs

- `temp/priority_lsms_isa_alignment_audit.csv`
- `temp/priority_lsms_isa_replacement_candidates.csv`
- `result/priority_lsms_isa_alignment_summary.csv`

## Guardrail

The 13 download packets remain useful as acquisition-control artifacts, but the
main core campaign should update Malawi and Uganda before manual download
execution. This artifact does not change the promoted-data registry and does
not authorize predictive ML, reduced-form estimation, causal ML, or policy
learning.
