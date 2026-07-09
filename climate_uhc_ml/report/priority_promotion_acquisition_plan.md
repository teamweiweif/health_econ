# Priority Promotion Acquisition Plan

Status: priority-first raw acquisition and value-verification plan. This report
does not promote any country-wave into `data/`; it defines the immediate raw
package acquisition batch and the first modules to verify after download.

## Summary

| Metric | Value | Interpretation |
|---|---:|---|
| priority_promotion_wave_plan_rows | 13 | Rows in the priority acquisition wave plan. |
| priority_10_wave_batch_rows | 10 | Priority waves selected for immediate raw-package acquisition. |
| priority_10_wave_batch_countries | 5 | Priority countries covered by the first 10-wave batch. |
| priority_country_list | Ethiopia;Malawi;Nigeria;Tanzania;Uganda | Priority countries covered by the first 10-wave batch. |
| sixth_country_backup_rows | 3 | Non-Albania backup countries for the 6-country financial-protection threshold. |
| waves_with_raw_package_present | 0 | Selected or backup waves with raw archive/tabular files currently present. |
| waves_still_requiring_manual_download | 13 | Selected or backup waves still needing manual raw-package download or placement. |
| priority_file_queue_rows | 156 | Top core files/modules to verify first after complete raw packages are placed. |
| modeling_gate_status | blocked | Models remain blocked until the promoted registry thresholds pass. |

## Immediate 10-Wave Priority Batch

| acquisition_batch_rank | country | wave | idno | raw_package_status | expected_core_module_rows | local_target_folder |
|---|---|---|---|---|---|---|
| 1 | Ethiopia | 2021-2022 | ETH_2021_ESPS-W5_v02_M | documentation_or_placeholder_only_no_raw_microdata | 66 | temp/raw_downloads/ETH_2021_ESPS-W5_v02_M/ |
| 2 | Ethiopia | 2018-2019 | ETH_2018_ESS_v04_M | documentation_or_placeholder_only_no_raw_microdata | 66 | temp/raw_downloads/ETH_2018_ESS_v04_M/ |
| 3 | Malawi | 2007-2009 | MWI_2007-2009_MTM_v01_M | documentation_or_placeholder_only_no_raw_microdata | 102 | temp/raw_downloads/MWI_2007-2009_MTM_v01_M/ |
| 4 | Nigeria | 2012-2013 | NGA_2012_GHSP-W2_v02_M | documentation_or_placeholder_only_no_raw_microdata | 100 | temp/raw_downloads/NGA_2012_GHSP-W2_v02_M/ |
| 5 | Nigeria | 2015-2016 | NGA_2015_GHSP-W3_v02_M | documentation_or_placeholder_only_no_raw_microdata | 102 | temp/raw_downloads/NGA_2015_GHSP-W3_v02_M/ |
| 6 | Nigeria | 2010-2011 | NGA_2010_GHSP-W1_v03_M | documentation_or_placeholder_only_no_raw_microdata | 98 | temp/raw_downloads/NGA_2010_GHSP-W1_v03_M/ |
| 7 | Tanzania | 2008-2009 | TZA_2008_NPS-R1_v03_M | documentation_or_placeholder_only_no_raw_microdata | 61 | temp/raw_downloads/TZA_2008_NPS-R1_v03_M/ |
| 8 | Tanzania | 2010-2011 | TZA_2010_NPS-R2_v03_M | documentation_or_placeholder_only_no_raw_microdata | 27 | temp/raw_downloads/TZA_2010_NPS-R2_v03_M/ |
| 9 | Tanzania | 2012-2013 | TZA_2012_NPS-R3_v01_M | documentation_or_placeholder_only_no_raw_microdata | 79 | temp/raw_downloads/TZA_2012_NPS-R3_v01_M/ |
| 10 | Uganda | 2014 | UGA_2014_SAGE-EL_v01_M | documentation_or_placeholder_only_no_raw_microdata | 32 | temp/raw_downloads/UGA_2014_SAGE-EL_v01_M/ |

## Sixth-Country Backup Candidates

The main priority set covers five countries. The project still needs six
value-verified financial-protection countries before modeling is allowed, so
these non-Albania backup country candidates should be downloaded if the priority
five-country batch cannot satisfy the six-country gate.

| acquisition_batch_rank | country | wave | idno | raw_package_status | local_target_folder |
|---|---|---|---|---|---|
| 11 | Jamaica | 1997 | JAM_1997_SLC_v01_M | documentation_or_placeholder_only_no_raw_microdata | temp/raw_downloads/JAM_1997_SLC_v01_M/ |
| 12 | Kyrgyz Republic | 1993 | KGZ_1993_KMPS_v01_M | documentation_or_placeholder_only_no_raw_microdata | temp/raw_downloads/KGZ_1993_KMPS_v01_M/ |
| 13 | Nepal | 2010-2011 | NPL_2010_LSS-III_v01_M | documentation_or_placeholder_only_no_raw_microdata | temp/raw_downloads/NPL_2010_LSS-III_v01_M/ |

## File Queue Coverage

| IDNO | Top files/modules queued |
|---|---:|
| `ETH_2018_ESS_v04_M` | 12 |
| `ETH_2021_ESPS-W5_v02_M` | 12 |
| `JAM_1997_SLC_v01_M` | 12 |
| `KGZ_1993_KMPS_v01_M` | 12 |
| `MWI_2007-2009_MTM_v01_M` | 12 |
| `NGA_2010_GHSP-W1_v03_M` | 12 |
| `NGA_2012_GHSP-W2_v02_M` | 12 |
| `NGA_2015_GHSP-W3_v02_M` | 12 |
| `NPL_2010_LSS-III_v01_M` | 12 |
| `TZA_2008_NPS-R1_v03_M` | 12 |
| `TZA_2010_NPS-R2_v03_M` | 12 |
| `TZA_2012_NPS-R3_v01_M` | 12 |
| `UGA_2014_SAGE-EL_v01_M` | 12 |

## Required Procedure

1. Complete official access, account, and terms steps at each `official_url`.
2. Download the complete original raw package and all documentation offered for
   the wave; do not cherry-pick only the files in the queue.
3. Place unchanged raw archives/files under the listed `local_target_folder`.
4. Run the post-download verification commands in
   `result/priority_promotion_acquisition_wave_plan.csv`.
5. Promote no wave into `data/` until raw value, unit, recall-period, missing
   code, merge-key, survey-design, timing/geography, and CHIRPS/ERA5 gates pass.

## Machine-Readable Outputs

- `result/priority_promotion_acquisition_wave_plan.csv`
- `result/priority_promotion_acquisition_file_queue.csv`
- `result/priority_promotion_acquisition_summary.csv`
