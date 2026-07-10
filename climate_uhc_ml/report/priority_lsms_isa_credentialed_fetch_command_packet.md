# Priority LSMS/ISA Credentialed Fetch Command Packet

This packet turns the current minimum-batch World Bank Microdata download
board into per-wave fetch commands and post-download validation commands. It
does not download raw packages and does not include any cookie or header
values.

Local credential material, if used, must stay in `temp/private/`:

- `temp/private/worldbank_session_cookies.txt`: Netscape cookie jar exported from a logged-in World Bank Microdata browser session.

The safer Python route is still `script/180_build_priority_lsms_isa_credentialed_download_handoff.py`,
because it checks response headers before saving raw payloads. The `curl.exe`
commands are included only as a cookie-jar fallback for cases where the browser
export is already a Netscape-format cookie file.

## Summary

| metric | value | interpretation |
| --- | --- | --- |
| credentialed_fetch_command_packet_rows | 10 | Minimum-batch credentialed download command rows. |
| credentialed_fetch_command_packet_countries | 5 | Distinct countries covered by the command packet. |
| credentialed_fetch_command_packet_country_list | Ethiopia; Nepal; Nigeria; Tanzania; Uganda | Countries covered by the command packet. |
| credentialed_fetch_command_packet_expected_core_file_rows | 323 | Expected core raw-file rows that would be checked after package receipt. |
| credentialed_fetch_command_packet_target_file_count | 0 | Existing non-generated target files currently found before download. |
| credentialed_fetch_command_packet_ready_to_probe_rows | 0 | Rows ready for credentialed probing with local session material. |
| credentialed_fetch_command_packet_missing_session_rows | 10 | Rows blocked because temp/private session material is absent. |
| data_write_gate_status | blocked_no_data_write | This packet writes only result/report artifacts and does not promote datasets. |
| modeling_gate_status | blocked | No predictive, reduced-form, causal ML, or policy learning is opened. |
| credentialed_fetch_command_packet_status_blocked_missing_worldbank_session | 10 | Command packet status count. |

## Command Rows

| download_rank | country | wave | idno | command_packet_status | credentialed_download_url | payload_target_path |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | Ethiopia | 2021-2022 | ETH_2021_ESPS-W5_v02_M | blocked_missing_worldbank_session | https://microdata.worldbank.org/catalog/6161/download | temp/raw_downloads/ETH_2021_ESPS-W5_v02_M/_credentialed_payloads/ETH_2021_ESPS-W5_v02_M_worldbank_download_payload.bin |
| 2 | Ethiopia | 2018-2019 | ETH_2018_ESS_v04_M | blocked_missing_worldbank_session | https://microdata.worldbank.org/catalog/3823/download | temp/raw_downloads/ETH_2018_ESS_v04_M/_credentialed_payloads/ETH_2018_ESS_v04_M_worldbank_download_payload.bin |
| 3 | Nigeria | 2012-2013 | NGA_2012_GHSP-W2_v02_M | blocked_missing_worldbank_session | https://microdata.worldbank.org/catalog/1952/download | temp/raw_downloads/NGA_2012_GHSP-W2_v02_M/_credentialed_payloads/NGA_2012_GHSP-W2_v02_M_worldbank_download_payload.bin |
| 4 | Nigeria | 2015-2016 | NGA_2015_GHSP-W3_v02_M | blocked_missing_worldbank_session | https://microdata.worldbank.org/catalog/2734/download | temp/raw_downloads/NGA_2015_GHSP-W3_v02_M/_credentialed_payloads/NGA_2015_GHSP-W3_v02_M_worldbank_download_payload.bin |
| 5 | Nigeria | 2010-2011 | NGA_2010_GHSP-W1_v03_M | blocked_missing_worldbank_session | https://microdata.worldbank.org/catalog/1002/download | temp/raw_downloads/NGA_2010_GHSP-W1_v03_M/_credentialed_payloads/NGA_2010_GHSP-W1_v03_M_worldbank_download_payload.bin |
| 6 | Tanzania | 2008-2009 | TZA_2008_NPS-R1_v03_M | blocked_missing_worldbank_session | https://microdata.worldbank.org/catalog/76/download | temp/raw_downloads/TZA_2008_NPS-R1_v03_M/_credentialed_payloads/TZA_2008_NPS-R1_v03_M_worldbank_download_payload.bin |
| 7 | Tanzania | 2010-2011 | TZA_2010_NPS-R2_v03_M | blocked_missing_worldbank_session | https://microdata.worldbank.org/catalog/1050/download | temp/raw_downloads/TZA_2010_NPS-R2_v03_M/_credentialed_payloads/TZA_2010_NPS-R2_v03_M_worldbank_download_payload.bin |
| 8 | Tanzania | 2012-2013 | TZA_2012_NPS-R3_v01_M | blocked_missing_worldbank_session | https://microdata.worldbank.org/catalog/2252/download | temp/raw_downloads/TZA_2012_NPS-R3_v01_M/_credentialed_payloads/TZA_2012_NPS-R3_v01_M_worldbank_download_payload.bin |
| 9 | Uganda | 2019-2020 | UGA_2019_UNPS_v03_M | blocked_missing_worldbank_session | https://microdata.worldbank.org/catalog/3902/download | temp/raw_downloads/UGA_2019_UNPS_v03_M/_credentialed_payloads/UGA_2019_UNPS_v03_M_worldbank_download_payload.bin |
| 10 | Nepal | 2010-2011 | NPL_2010_LSS-III_v01_M | blocked_missing_worldbank_session | https://microdata.worldbank.org/catalog/1000/download | temp/raw_downloads/NPL_2010_LSS-III_v01_M/_credentialed_payloads/NPL_2010_LSS-III_v01_M_worldbank_download_payload.bin |

## Run Order

1. Log in to World Bank Microdata in a browser and accept the official terms for the target survey.
2. Export browser cookies to `temp/private/worldbank_session_cookies.txt` or manually place the downloaded official raw package into the listed local target folder.
3. Run `python script/180_build_priority_lsms_isa_credentialed_download_handoff.py --probe`.
4. Run `python script/180_build_priority_lsms_isa_credentialed_download_handoff.py --execute` only if the probe confirms downloadable raw payloads.
5. Re-run the post-download validation command chain listed for the downloaded wave.

Data writes remain blocked until receipt, schema, value-profile, semantics,
timing/geography, and climate-linkage gates pass.
