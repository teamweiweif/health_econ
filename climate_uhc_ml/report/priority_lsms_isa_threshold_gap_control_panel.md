# Priority LSMS-ISA Threshold Gap Control Panel

Status: manual-download control panel for the minimum threshold batch.
It does not download raw data, accept terms, extract microdata, write `data/`,
or run predictive/reduced-form/causal ML.

## Threshold Arithmetic

- Current promoted registry: 1 country-wave(s) across 1 country/countries.
- Current gap: 5 country/countries and 9 country-wave(s).
- If every remaining minimum-batch row passes verification: 6 countries and 11 country-waves.
- Buffer after minimum batch: 0 country and 1 country-wave(s).
- Remaining minimum-batch manual downloads: 10.
- Backup actions after the minimum batch: 8.

## Minimum Batch Download Actions

| threshold_sequence_rank | country | wave | idno | official_expected_missing_rows | official_core_missing_rows | incoming_route_rows | official_get_microdata_url | local_target_folder |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | Ethiopia | 2021-2022 | ETH_2021_ESPS-W5_v02_M | 68 | 36 | 0 | https://microdata.worldbank.org/catalog/6161/get-microdata | temp/raw_downloads/ETH_2021_ESPS-W5_v02_M/ |
| 2 | Ethiopia | 2018-2019 | ETH_2018_ESS_v04_M | 68 | 35 | 0 | https://microdata.worldbank.org/catalog/3823/get-microdata | temp/raw_downloads/ETH_2018_ESS_v04_M/ |
| 4 | Nigeria | 2012-2013 | NGA_2012_GHSP-W2_v02_M | 103 | 26 | 0 | https://microdata.worldbank.org/catalog/1952/get-microdata | temp/raw_downloads/NGA_2012_GHSP-W2_v02_M/ |
| 5 | Nigeria | 2015-2016 | NGA_2015_GHSP-W3_v02_M | 104 | 26 | 0 | https://microdata.worldbank.org/catalog/2734/get-microdata | temp/raw_downloads/NGA_2015_GHSP-W3_v02_M/ |
| 6 | Nigeria | 2010-2011 | NGA_2010_GHSP-W1_v03_M | 99 | 27 | 0 | https://microdata.worldbank.org/catalog/1002/get-microdata | temp/raw_downloads/NGA_2010_GHSP-W1_v03_M/ |
| 7 | Tanzania | 2008-2009 | TZA_2008_NPS-R1_v03_M | 61 | 35 | 0 | https://microdata.worldbank.org/catalog/76/get-microdata | temp/raw_downloads/TZA_2008_NPS-R1_v03_M/ |
| 8 | Tanzania | 2010-2011 | TZA_2010_NPS-R2_v03_M | 95 | 38 | 0 | https://microdata.worldbank.org/catalog/1050/get-microdata | temp/raw_downloads/TZA_2010_NPS-R2_v03_M/ |
| 9 | Tanzania | 2012-2013 | TZA_2012_NPS-R3_v01_M | 80 | 33 | 0 | https://microdata.worldbank.org/catalog/2252/get-microdata | temp/raw_downloads/TZA_2012_NPS-R3_v01_M/ |
| 10 | Uganda | 2019-2020 | UGA_2019_UNPS_v03_M | 109 | 39 | 0 | https://microdata.worldbank.org/catalog/3902/get-microdata | temp/raw_downloads/UGA_2019_UNPS_v03_M/ |
| 11 | Nepal | 2010-2011 | NPL_2010_LSS-III_v01_M | 51 | 28 | 0 | https://microdata.worldbank.org/catalog/1000/get-microdata | temp/raw_downloads/NPL_2010_LSS-III_v01_M/ |

## Country Threshold Panel

| country | current_promoted_waves | minimum_batch_remaining_rows | backup_action_rows | country_threshold_role | waves_if_minimum_remaining_passes |
| --- | --- | --- | --- | --- | --- |
| Ethiopia | 0 | 2 | 0 | needed_for_minimum_country_threshold | 2 |
| Jamaica | 0 | 0 | 1 | backup_country_or_replacement_after_failure | 0 |
| Kyrgyz Republic | 0 | 0 | 1 | backup_country_or_replacement_after_failure | 0 |
| Malawi | 1 | 0 | 3 | already_contributes_current_threshold | 1 |
| Nepal | 0 | 1 | 0 | needed_for_minimum_country_threshold | 1 |
| Nigeria | 0 | 3 | 0 | needed_for_minimum_country_threshold | 3 |
| Tanzania | 0 | 3 | 0 | needed_for_minimum_country_threshold | 3 |
| Uganda | 0 | 1 | 3 | needed_for_minimum_country_threshold | 1 |

## Outputs

- `temp/priority_lsms_isa_threshold_gap_download_panel.csv`
- `result/priority_lsms_isa_threshold_gap_country_panel.csv`
- `result/priority_lsms_isa_threshold_gap_control_panel_summary.csv`

## Stop Rule

The modeling gate remains blocked until the promoted registry proves at least
6 value-verified financial-protection countries, 10 value-verified
country-waves for double failure, and at least one accepted CHIRPS or ERA5
climate-linkage route.
