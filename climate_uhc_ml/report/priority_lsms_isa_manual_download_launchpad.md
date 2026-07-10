# Priority LSMS/ISA Manual Download Launchpad

Status: clickable manual-download launchpad for the 10 locked download-required
World Bank LSMS/ISA waves.

Use the HTML launchpad at `report/priority_lsms_isa_manual_download_launchpad.html`
to open official get-microdata pages and copy local target-folder paths. This
artifact does not download raw data, export credentials, write `data/`, or
promote country-waves.

## Summary

| metric | value | interpretation |
| --- | --- | --- |
| manual_download_launchpad_rows | 10 | Manual-download launchpad rows for the locked download-required waves. |
| manual_download_launchpad_country_rows | 5 | Countries covered by the launchpad. |
| manual_download_launchpad_priority_country_rows | 9 | Rows from priority countries. |
| manual_download_launchpad_sixth_country_rows | 1 | Rows supplying the sixth country. |
| manual_download_launchpad_expected_full_file_rows | 838 | Expected official file rows across launchpad targets. |
| manual_download_launchpad_expected_core_file_rows | 323 | Expected core-file rows across launchpad targets. |
| manual_download_launchpad_target_file_rows | 0 | Files currently present under exact target folders. |
| manual_download_launchpad_incoming_file_rows | 0 | Files currently staged under temp/raw_downloads/_incoming. |
| manual_download_launchpad_open_official_page_rows | 10 | Rows still requiring official page opening, terms acceptance, and package placement. |
| manual_download_launchpad_html_written | 1 | Whether the clickable HTML launchpad was written. |
| data_write_gate_status | blocked_no_data_write | The launchpad writes only acquisition-control artifacts. |
| modeling_gate_status | blocked | No predictive, reduced-form, causal ML, or policy learning is opened. |
| manual_download_launchpad_status_open_official_page_accept_terms_download_package | 10 | Manual-download launchpad status count. |

## Launch Rows

| launch_rank | canary_role | country | wave | idno | catalog_id | launch_status | expected_core_file_rows | target_file_count |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | first_canary | Ethiopia | 2021-2022 | ETH_2021_ESPS-W5_v02_M | 6161 | open_official_page_accept_terms_download_package | 36 | 0 |
| 2 | follow_after_first_canary_passes | Ethiopia | 2018-2019 | ETH_2018_ESS_v04_M | 3823 | open_official_page_accept_terms_download_package | 35 | 0 |
| 3 | follow_after_first_canary_passes | Nigeria | 2012-2013 | NGA_2012_GHSP-W2_v02_M | 1952 | open_official_page_accept_terms_download_package | 26 | 0 |
| 4 | follow_after_first_canary_passes | Nigeria | 2015-2016 | NGA_2015_GHSP-W3_v02_M | 2734 | open_official_page_accept_terms_download_package | 26 | 0 |
| 5 | follow_after_first_canary_passes | Nigeria | 2010-2011 | NGA_2010_GHSP-W1_v03_M | 1002 | open_official_page_accept_terms_download_package | 27 | 0 |
| 6 | follow_after_first_canary_passes | Tanzania | 2008-2009 | TZA_2008_NPS-R1_v03_M | 76 | open_official_page_accept_terms_download_package | 35 | 0 |
| 7 | follow_after_first_canary_passes | Tanzania | 2010-2011 | TZA_2010_NPS-R2_v03_M | 1050 | open_official_page_accept_terms_download_package | 38 | 0 |
| 8 | follow_after_first_canary_passes | Tanzania | 2012-2013 | TZA_2012_NPS-R3_v01_M | 2252 | open_official_page_accept_terms_download_package | 33 | 0 |
| 9 | follow_after_first_canary_passes | Uganda | 2019-2020 | UGA_2019_UNPS_v03_M | 3902 | open_official_page_accept_terms_download_package | 39 | 0 |
| 10 | follow_after_first_canary_passes | Nepal | 2010-2011 | NPL_2010_LSS-III_v01_M | 1000 | open_official_page_accept_terms_download_package | 28 | 0 |

## Commands

| launch_rank | idno | prepare_target_folder_command | open_target_folder_command | python_probe_command |
| --- | --- | --- | --- | --- |
| 1 | ETH_2021_ESPS-W5_v02_M | New-Item -ItemType Directory -Force -Path 'temp/raw_downloads/ETH_2021_ESPS-W5_v02_M' | Invoke-Item 'temp/raw_downloads/ETH_2021_ESPS-W5_v02_M' | python script/180_build_priority_lsms_isa_credentialed_download_handoff.py --idno ETH_2021_ESPS-W5_v02_M --... |
| 2 | ETH_2018_ESS_v04_M | New-Item -ItemType Directory -Force -Path 'temp/raw_downloads/ETH_2018_ESS_v04_M' | Invoke-Item 'temp/raw_downloads/ETH_2018_ESS_v04_M' | python script/180_build_priority_lsms_isa_credentialed_download_handoff.py --idno ETH_2018_ESS_v04_M --probe |
| 3 | NGA_2012_GHSP-W2_v02_M | New-Item -ItemType Directory -Force -Path 'temp/raw_downloads/NGA_2012_GHSP-W2_v02_M' | Invoke-Item 'temp/raw_downloads/NGA_2012_GHSP-W2_v02_M' | python script/180_build_priority_lsms_isa_credentialed_download_handoff.py --idno NGA_2012_GHSP-W2_v02_M --... |
| 4 | NGA_2015_GHSP-W3_v02_M | New-Item -ItemType Directory -Force -Path 'temp/raw_downloads/NGA_2015_GHSP-W3_v02_M' | Invoke-Item 'temp/raw_downloads/NGA_2015_GHSP-W3_v02_M' | python script/180_build_priority_lsms_isa_credentialed_download_handoff.py --idno NGA_2015_GHSP-W3_v02_M --... |
| 5 | NGA_2010_GHSP-W1_v03_M | New-Item -ItemType Directory -Force -Path 'temp/raw_downloads/NGA_2010_GHSP-W1_v03_M' | Invoke-Item 'temp/raw_downloads/NGA_2010_GHSP-W1_v03_M' | python script/180_build_priority_lsms_isa_credentialed_download_handoff.py --idno NGA_2010_GHSP-W1_v03_M --... |
| 6 | TZA_2008_NPS-R1_v03_M | New-Item -ItemType Directory -Force -Path 'temp/raw_downloads/TZA_2008_NPS-R1_v03_M' | Invoke-Item 'temp/raw_downloads/TZA_2008_NPS-R1_v03_M' | python script/180_build_priority_lsms_isa_credentialed_download_handoff.py --idno TZA_2008_NPS-R1_v03_M --p... |
| 7 | TZA_2010_NPS-R2_v03_M | New-Item -ItemType Directory -Force -Path 'temp/raw_downloads/TZA_2010_NPS-R2_v03_M' | Invoke-Item 'temp/raw_downloads/TZA_2010_NPS-R2_v03_M' | python script/180_build_priority_lsms_isa_credentialed_download_handoff.py --idno TZA_2010_NPS-R2_v03_M --p... |
| 8 | TZA_2012_NPS-R3_v01_M | New-Item -ItemType Directory -Force -Path 'temp/raw_downloads/TZA_2012_NPS-R3_v01_M' | Invoke-Item 'temp/raw_downloads/TZA_2012_NPS-R3_v01_M' | python script/180_build_priority_lsms_isa_credentialed_download_handoff.py --idno TZA_2012_NPS-R3_v01_M --p... |
| 9 | UGA_2019_UNPS_v03_M | New-Item -ItemType Directory -Force -Path 'temp/raw_downloads/UGA_2019_UNPS_v03_M' | Invoke-Item 'temp/raw_downloads/UGA_2019_UNPS_v03_M' | python script/180_build_priority_lsms_isa_credentialed_download_handoff.py --idno UGA_2019_UNPS_v03_M --probe |
| 10 | NPL_2010_LSS-III_v01_M | New-Item -ItemType Directory -Force -Path 'temp/raw_downloads/NPL_2010_LSS-III_v01_M' | Invoke-Item 'temp/raw_downloads/NPL_2010_LSS-III_v01_M' | python script/180_build_priority_lsms_isa_credentialed_download_handoff.py --idno NPL_2010_LSS-III_v01_M --... |

## Stop Rule

Opening a page or placing files only starts package receipt validation. A wave
can only move toward promoted data after receipt, schema, value, semantics,
timing/geography, climate-linkage, and promotion-packet gates pass.
