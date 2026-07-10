# Priority LSMS-ISA Credentialed Download Handoff

Status: local-only World Bank get-microdata session handoff. It can use
`temp/private/worldbank_session_cookies.txt` or
`temp/private/worldbank_session_headers.txt` from a browser session to probe
the official `/download` routes for the 10 remaining minimum-batch packets.

No credential values are written to this report. `temp/private/` is ignored by git.

Default mode is dry-run. Use `--probe` to test authenticated responses without
saving raw files. Use `--execute` only after the official terms have been accepted
in the browser session; raw files are saved only when the response looks like a
downloadable raw payload.

It does not extract archives, write promoted `data/`, or run models.

## Summary

- Mode: dry_run
- Filter: all
- Board rows before filter: 10
- Rows: 10
- Cookie file present: 0
- Header file present: 0
- Requests attempted: 0
- Raw payload detected rows: 0
- Saved raw file rows: 0
- Missing-session rows: 10
- Access-gate rows: 0

## Handoff Plan

| download_rank | country | wave | idno | run_mode | request_attempted | response_classification | saved_path | next_action |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | Ethiopia | 2021-2022 | ETH_2021_ESPS-W5_v02_M | dry_run | 0 | blocked_missing_worldbank_session |  | Create temp/private/worldbank_session_cookies.txt or temp/private/worldbank_session_headers.txt from a logged-in World Bank Microdata browser session, then rerun with --probe. |
| 2 | Ethiopia | 2018-2019 | ETH_2018_ESS_v04_M | dry_run | 0 | blocked_missing_worldbank_session |  | Create temp/private/worldbank_session_cookies.txt or temp/private/worldbank_session_headers.txt from a logged-in World Bank Microdata browser session, then rerun with --probe. |
| 3 | Nigeria | 2012-2013 | NGA_2012_GHSP-W2_v02_M | dry_run | 0 | blocked_missing_worldbank_session |  | Create temp/private/worldbank_session_cookies.txt or temp/private/worldbank_session_headers.txt from a logged-in World Bank Microdata browser session, then rerun with --probe. |
| 4 | Nigeria | 2015-2016 | NGA_2015_GHSP-W3_v02_M | dry_run | 0 | blocked_missing_worldbank_session |  | Create temp/private/worldbank_session_cookies.txt or temp/private/worldbank_session_headers.txt from a logged-in World Bank Microdata browser session, then rerun with --probe. |
| 5 | Nigeria | 2010-2011 | NGA_2010_GHSP-W1_v03_M | dry_run | 0 | blocked_missing_worldbank_session |  | Create temp/private/worldbank_session_cookies.txt or temp/private/worldbank_session_headers.txt from a logged-in World Bank Microdata browser session, then rerun with --probe. |
| 6 | Tanzania | 2008-2009 | TZA_2008_NPS-R1_v03_M | dry_run | 0 | blocked_missing_worldbank_session |  | Create temp/private/worldbank_session_cookies.txt or temp/private/worldbank_session_headers.txt from a logged-in World Bank Microdata browser session, then rerun with --probe. |
| 7 | Tanzania | 2010-2011 | TZA_2010_NPS-R2_v03_M | dry_run | 0 | blocked_missing_worldbank_session |  | Create temp/private/worldbank_session_cookies.txt or temp/private/worldbank_session_headers.txt from a logged-in World Bank Microdata browser session, then rerun with --probe. |
| 8 | Tanzania | 2012-2013 | TZA_2012_NPS-R3_v01_M | dry_run | 0 | blocked_missing_worldbank_session |  | Create temp/private/worldbank_session_cookies.txt or temp/private/worldbank_session_headers.txt from a logged-in World Bank Microdata browser session, then rerun with --probe. |
| 9 | Uganda | 2019-2020 | UGA_2019_UNPS_v03_M | dry_run | 0 | blocked_missing_worldbank_session |  | Create temp/private/worldbank_session_cookies.txt or temp/private/worldbank_session_headers.txt from a logged-in World Bank Microdata browser session, then rerun with --probe. |
| 10 | Nepal | 2010-2011 | NPL_2010_LSS-III_v01_M | dry_run | 0 | blocked_missing_worldbank_session |  | Create temp/private/worldbank_session_cookies.txt or temp/private/worldbank_session_headers.txt from a logged-in World Bank Microdata browser session, then rerun with --probe. |

## Local Session Files

- `temp/private/worldbank_session_cookies.txt`: Netscape cookies export or a raw `Cookie:` header from a logged-in World Bank Microdata browser session.
- `temp/private/worldbank_session_headers.txt`: optional header lines such as `User-Agent: ...`; do not commit this file.

## Commands

```bash
python script/180_build_priority_lsms_isa_credentialed_download_handoff.py
python script/180_build_priority_lsms_isa_credentialed_download_handoff.py --probe
python script/180_build_priority_lsms_isa_credentialed_download_handoff.py --execute
python script/180_build_priority_lsms_isa_credentialed_download_handoff.py --idno ETH_2021_ESPS-W5_v02_M --probe
python script/180_build_priority_lsms_isa_credentialed_download_handoff.py --idno ETH_2021_ESPS-W5_v02_M --execute
```

## Outputs

- `temp/priority_lsms_isa_credentialed_download_handoff_plan.csv`
- `temp/priority_lsms_isa_credentialed_download_handoff_log.csv`
- `result/priority_lsms_isa_credentialed_download_handoff_summary.csv`

## Stop Rule

This handoff only helps acquire official raw packages. Promotion remains blocked
until receipt, schema, value-profile, semantics, timing/geography, and climate
linkage gates pass.
