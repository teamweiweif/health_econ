# Priority Official Raw Access Probe

Status: official-page access probe for the priority 10-wave acquisition batch
and sixth-country backup candidates. This script snapshots official World Bank
get-microdata pages and classifies visible login, registration, request, terms,
and direct-link signals. It does not download raw microdata and does not bypass
access controls.

## Summary

| Metric | Value | Interpretation |
|---|---:|---|
| priority_official_raw_access_probe_rows | 13 | Priority acquisition and backup waves with official get-microdata pages probed. |
| priority_10_wave_probe_rows | 10 | Immediate priority 10-wave batch rows probed. |
| sixth_country_backup_probe_rows | 3 | Backup sixth-country rows probed. |
| access_gate_detected_rows | 13 | Rows with login/register/request/terms language on official pages. |
| possible_direct_raw_link_rows | 0 | Rows with possible direct raw links not requiring gate language; no raw files are downloaded by this probe. |
| manual_action_required_rows | 13 | Rows needing manual account, terms, or review steps. |
| modeling_gate_status | blocked | Models remain blocked until promoted registry thresholds pass. |
| direct_raw_route_status_no_direct_raw_route_access_gate_detected | 13 | Direct raw route status count. |
| manual_action_status_manual_account_or_terms_required | 13 | Manual action status count. |

## Direct Raw Route Status

| Direct raw route status | Count |
|---|---:|
| no_direct_raw_route_access_gate_detected | 13 |

## Manual Action Status

| Manual action status | Count |
|---|---:|
| manual_account_or_terms_required | 13 |

## Probe Rows

| acquisition_batch_rank | batch_role | idno | http_status | access_gate_detected | direct_raw_route_status | manual_action_status | login_link |
|---|---|---|---|---|---|---|---|
| 1 | priority_10_wave_batch | ETH_2021_ESPS-W5_v02_M | 200 | 1 | no_direct_raw_route_access_gate_detected | manual_account_or_terms_required | https://microdata.worldbank.org/catalog/6161/get-microdata |
| 2 | priority_10_wave_batch | ETH_2018_ESS_v04_M | 200 | 1 | no_direct_raw_route_access_gate_detected | manual_account_or_terms_required | https://microdata.worldbank.org/catalog/3823/get-microdata |
| 3 | priority_10_wave_batch | MWI_2007-2009_MTM_v01_M | 200 | 1 | no_direct_raw_route_access_gate_detected | manual_account_or_terms_required | https://microdata.worldbank.org/catalog/3462/get-microdata |
| 4 | priority_10_wave_batch | NGA_2012_GHSP-W2_v02_M | 200 | 1 | no_direct_raw_route_access_gate_detected | manual_account_or_terms_required | https://microdata.worldbank.org/catalog/1952/get-microdata |
| 5 | priority_10_wave_batch | NGA_2015_GHSP-W3_v02_M | 200 | 1 | no_direct_raw_route_access_gate_detected | manual_account_or_terms_required | https://microdata.worldbank.org/catalog/2734/get-microdata |
| 6 | priority_10_wave_batch | NGA_2010_GHSP-W1_v03_M | 200 | 1 | no_direct_raw_route_access_gate_detected | manual_account_or_terms_required | https://microdata.worldbank.org/catalog/1002/get-microdata |
| 7 | priority_10_wave_batch | TZA_2008_NPS-R1_v03_M | 200 | 1 | no_direct_raw_route_access_gate_detected | manual_account_or_terms_required | https://microdata.worldbank.org/catalog/76/get-microdata |
| 8 | priority_10_wave_batch | TZA_2010_NPS-R2_v03_M | 200 | 1 | no_direct_raw_route_access_gate_detected | manual_account_or_terms_required | https://microdata.worldbank.org/catalog/1050/get-microdata |
| 9 | priority_10_wave_batch | TZA_2012_NPS-R3_v01_M | 200 | 1 | no_direct_raw_route_access_gate_detected | manual_account_or_terms_required | https://microdata.worldbank.org/catalog/2252/get-microdata |
| 10 | priority_10_wave_batch | UGA_2014_SAGE-EL_v01_M | 200 | 1 | no_direct_raw_route_access_gate_detected | manual_account_or_terms_required | https://microdata.worldbank.org/catalog/2654/get-microdata |
| 11 | sixth_country_backup_candidate | JAM_1997_SLC_v01_M | 200 | 1 | no_direct_raw_route_access_gate_detected | manual_account_or_terms_required | https://microdata.worldbank.org/catalog/2368/get-microdata |
| 12 | sixth_country_backup_candidate | KGZ_1993_KMPS_v01_M | 200 | 1 | no_direct_raw_route_access_gate_detected | manual_account_or_terms_required | https://microdata.worldbank.org/catalog/280/get-microdata |
| 13 | sixth_country_backup_candidate | NPL_2010_LSS-III_v01_M | 200 | 1 | no_direct_raw_route_access_gate_detected | manual_account_or_terms_required | https://microdata.worldbank.org/catalog/1000/get-microdata |

## Interpretation Guardrails

- A saved HTML page is documentation evidence, not raw microdata.
- Candidate raw links are not downloaded or treated as usable unless access
  terms are manually satisfied.
- If an access gate is detected, the dataset remains blocked until account,
  terms, or Data Access Agreement steps are completed and raw files are placed
  in `temp/raw_downloads/`.
- Do not promote, harmonize into final `data/`, or run models from this probe.

## Machine-Readable Outputs

- `temp/priority_official_raw_access_probe.csv`
- `result/priority_official_raw_access_summary.csv`
