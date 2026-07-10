# Priority LSMS-ISA Manual Download Packets

Status: per-wave manual acquisition packets for the remaining minimum
threshold batch. These packets are intentionally small and executable:
open the official page, download the complete unchanged package, place it
under the local target folder, and run the validation commands.

No raw data are stored here. No `data/` writes or models are triggered.

## Summary

- Manual download packet rows: 10
- Priority-country packet rows: 9
- Expected official full-file rows across packets: 838
- Still-missing expected full-file rows: 838
- Requirement-linked core-file rows listed: 323
- Still-missing core-file rows: 323
- Minimum-batch official full-file manifest rows available: 890

## Packet Index

| download_rank | country | wave | idno | expected_missing_file_rows | core_missing_file_rows | official_get_microdata_url | local_target_folder | packet_report_path |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | Ethiopia | 2021-2022 | ETH_2021_ESPS-W5_v02_M | 68 | 36 | https://microdata.worldbank.org/catalog/6161/get-microdata | temp/raw_downloads/ETH_2021_ESPS-W5_v02_M/ | report/priority_lsms_isa_manual_download_packets/ETH_2021_ESPS-W5_v02_M.md |
| 2 | Ethiopia | 2018-2019 | ETH_2018_ESS_v04_M | 68 | 35 | https://microdata.worldbank.org/catalog/3823/get-microdata | temp/raw_downloads/ETH_2018_ESS_v04_M/ | report/priority_lsms_isa_manual_download_packets/ETH_2018_ESS_v04_M.md |
| 3 | Nigeria | 2012-2013 | NGA_2012_GHSP-W2_v02_M | 103 | 26 | https://microdata.worldbank.org/catalog/1952/get-microdata | temp/raw_downloads/NGA_2012_GHSP-W2_v02_M/ | report/priority_lsms_isa_manual_download_packets/NGA_2012_GHSP-W2_v02_M.md |
| 4 | Nigeria | 2015-2016 | NGA_2015_GHSP-W3_v02_M | 104 | 26 | https://microdata.worldbank.org/catalog/2734/get-microdata | temp/raw_downloads/NGA_2015_GHSP-W3_v02_M/ | report/priority_lsms_isa_manual_download_packets/NGA_2015_GHSP-W3_v02_M.md |
| 5 | Nigeria | 2010-2011 | NGA_2010_GHSP-W1_v03_M | 99 | 27 | https://microdata.worldbank.org/catalog/1002/get-microdata | temp/raw_downloads/NGA_2010_GHSP-W1_v03_M/ | report/priority_lsms_isa_manual_download_packets/NGA_2010_GHSP-W1_v03_M.md |
| 6 | Tanzania | 2008-2009 | TZA_2008_NPS-R1_v03_M | 61 | 35 | https://microdata.worldbank.org/catalog/76/get-microdata | temp/raw_downloads/TZA_2008_NPS-R1_v03_M/ | report/priority_lsms_isa_manual_download_packets/TZA_2008_NPS-R1_v03_M.md |
| 7 | Tanzania | 2010-2011 | TZA_2010_NPS-R2_v03_M | 95 | 38 | https://microdata.worldbank.org/catalog/1050/get-microdata | temp/raw_downloads/TZA_2010_NPS-R2_v03_M/ | report/priority_lsms_isa_manual_download_packets/TZA_2010_NPS-R2_v03_M.md |
| 8 | Tanzania | 2012-2013 | TZA_2012_NPS-R3_v01_M | 80 | 33 | https://microdata.worldbank.org/catalog/2252/get-microdata | temp/raw_downloads/TZA_2012_NPS-R3_v01_M/ | report/priority_lsms_isa_manual_download_packets/TZA_2012_NPS-R3_v01_M.md |
| 9 | Uganda | 2019-2020 | UGA_2019_UNPS_v03_M | 109 | 39 | https://microdata.worldbank.org/catalog/3902/get-microdata | temp/raw_downloads/UGA_2019_UNPS_v03_M/ | report/priority_lsms_isa_manual_download_packets/UGA_2019_UNPS_v03_M.md |
| 10 | Nepal | 2010-2011 | NPL_2010_LSS-III_v01_M | 51 | 28 | https://microdata.worldbank.org/catalog/1000/get-microdata | temp/raw_downloads/NPL_2010_LSS-III_v01_M/ | report/priority_lsms_isa_manual_download_packets/NPL_2010_LSS-III_v01_M.md |

## Outputs

- `temp/priority_lsms_isa_manual_download_packet_index.csv`
- `temp/priority_lsms_isa_manual_download_packet_core_files.csv`
- `result/priority_lsms_isa_manual_download_packet_summary.csv`
- `report/priority_lsms_isa_manual_download_packets/<IDNO>.md`

## Stop Rule

These packets only support credentialed/manual acquisition. Modeling remains
blocked until promoted registry thresholds pass with value-verified raw files
and accepted CHIRPS or ERA5 climate linkage.
