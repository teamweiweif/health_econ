# Priority LSMS/ISA World Bank Session Bootstrap

This report captures the current credentialed-download session readiness for
the 10 minimum-batch World Bank Microdata packages. It is deliberately
redacted: it reports only whether local session files exist, their byte sizes,
and structural format checks. It never prints cookie or header values.

Local-only session files:

- `temp/private/worldbank_session_cookies.txt`: Netscape cookie export, raw cookie pairs, or a `Cookie:` header from a logged-in World Bank Microdata browser session.
- `temp/private/worldbank_session_headers.txt`: optional non-secret request headers. If a `Cookie:` header is placed here, review it before probing.

`temp/private/` is ignored by git. Keep those files local.

## Summary

| metric | value | interpretation |
| --- | --- | --- |
| worldbank_session_bootstrap_rows | 10 | Minimum-batch download rows covered by the session bootstrap. |
| worldbank_session_cookie_file_present | 0 | Whether temp/private/worldbank_session_cookies.txt exists. Contents are never exported. |
| worldbank_session_cookie_file_bytes | 0 | Cookie file size only; no credential values are reported. |
| worldbank_session_cookie_format_status | missing | Redacted structural classification of the cookie file. |
| worldbank_session_header_file_present | 0 | Whether temp/private/worldbank_session_headers.txt exists. Contents are never exported. |
| worldbank_session_header_file_bytes | 0 | Header file size only; no header values are reported. |
| worldbank_session_header_format_status | missing | Redacted structural classification of the header file. |
| worldbank_session_bootstrap_ready_for_probe_rows | 0 | Rows ready to run the credentialed --probe command. |
| worldbank_session_bootstrap_missing_session_rows | 10 | Rows blocked because no local session material is present. |
| worldbank_session_bootstrap_status_blocked_missing_worldbank_session_material | 10 | Status count. |
| data_write_gate_status | blocked_no_data_write | This bootstrap writes only result/report artifacts and does not promote datasets. |
| modeling_gate_status | blocked | No predictive, reduced-form, causal ML, or policy learning is opened. |

## Bootstrap Rows

| download_rank | country | wave | idno | session_bootstrap_status | credentialed_download_url | local_target_folder |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | Ethiopia | 2021-2022 | ETH_2021_ESPS-W5_v02_M | blocked_missing_worldbank_session_material | https://microdata.worldbank.org/catalog/6161/download | temp/raw_downloads/ETH_2021_ESPS-W5_v02_M/ |
| 2 | Ethiopia | 2018-2019 | ETH_2018_ESS_v04_M | blocked_missing_worldbank_session_material | https://microdata.worldbank.org/catalog/3823/download | temp/raw_downloads/ETH_2018_ESS_v04_M/ |
| 3 | Nigeria | 2012-2013 | NGA_2012_GHSP-W2_v02_M | blocked_missing_worldbank_session_material | https://microdata.worldbank.org/catalog/1952/download | temp/raw_downloads/NGA_2012_GHSP-W2_v02_M/ |
| 4 | Nigeria | 2015-2016 | NGA_2015_GHSP-W3_v02_M | blocked_missing_worldbank_session_material | https://microdata.worldbank.org/catalog/2734/download | temp/raw_downloads/NGA_2015_GHSP-W3_v02_M/ |
| 5 | Nigeria | 2010-2011 | NGA_2010_GHSP-W1_v03_M | blocked_missing_worldbank_session_material | https://microdata.worldbank.org/catalog/1002/download | temp/raw_downloads/NGA_2010_GHSP-W1_v03_M/ |
| 6 | Tanzania | 2008-2009 | TZA_2008_NPS-R1_v03_M | blocked_missing_worldbank_session_material | https://microdata.worldbank.org/catalog/76/download | temp/raw_downloads/TZA_2008_NPS-R1_v03_M/ |
| 7 | Tanzania | 2010-2011 | TZA_2010_NPS-R2_v03_M | blocked_missing_worldbank_session_material | https://microdata.worldbank.org/catalog/1050/download | temp/raw_downloads/TZA_2010_NPS-R2_v03_M/ |
| 8 | Tanzania | 2012-2013 | TZA_2012_NPS-R3_v01_M | blocked_missing_worldbank_session_material | https://microdata.worldbank.org/catalog/2252/download | temp/raw_downloads/TZA_2012_NPS-R3_v01_M/ |
| 9 | Uganda | 2019-2020 | UGA_2019_UNPS_v03_M | blocked_missing_worldbank_session_material | https://microdata.worldbank.org/catalog/3902/download | temp/raw_downloads/UGA_2019_UNPS_v03_M/ |
| 10 | Nepal | 2010-2011 | NPL_2010_LSS-III_v01_M | blocked_missing_worldbank_session_material | https://microdata.worldbank.org/catalog/1000/download | temp/raw_downloads/NPL_2010_LSS-III_v01_M/ |

## Commands

```bash
python script/180_build_priority_lsms_isa_credentialed_download_handoff.py --probe
python script/180_build_priority_lsms_isa_credentialed_download_handoff.py --execute
```

Run `--probe` first. Use `--execute` only after the official World Bank terms
have been accepted and the probe shows downloadable raw payloads.
