# First-Batch Official Raw Access Probe

Status: official-page access probe only. This script snapshots first-batch World Bank get-microdata pages and classifies visible login, registration, request, terms, and direct-link signals. It does not download raw microdata and does not bypass access controls.

## Summary

| Metric | Value | Interpretation |
|---|---:|---|
| first_batch_access_probe_rows | 10 | First-batch official get-microdata pages probed. |
| access_gate_detected_rows | 10 | Rows with login/register/request/terms language on official pages. |
| possible_direct_raw_link_rows | 0 | Rows with possible direct raw links not requiring gate language; none are downloaded by this script. |
| manual_action_required_rows | 10 | Rows needing manual account, terms, or review steps. |
| direct_raw_route_status_no_direct_raw_route_access_gate_detected | 10 | Direct raw route status count. |
| manual_action_status_manual_account_or_terms_required | 10 | Manual action status count. |

## Direct Raw Route Status

| Direct raw route status | Count |
|---|---:|
| no_direct_raw_route_access_gate_detected | 10 |

## Manual Action Status

| Manual action status | Count |
|---|---:|
| manual_account_or_terms_required | 10 |

## Probe Rows

| batch_rank | idno | http_status | access_gate_detected | direct_raw_route_status | manual_action_status | login_link |
|---|---|---|---|---|---|---|
| 1 | ALB_2005_LSMS_v01_M | 200 | 1 | no_direct_raw_route_access_gate_detected | manual_account_or_terms_required | https://microdata.worldbank.org/catalog/64/get-microdata |
| 2 | ETH_2021_ESPS-W5_v02_M | 200 | 1 | no_direct_raw_route_access_gate_detected | manual_account_or_terms_required | https://microdata.worldbank.org/catalog/6161/get-microdata |
| 3 | ETH_2018_ESS_v04_M | 200 | 1 | no_direct_raw_route_access_gate_detected | manual_account_or_terms_required | https://microdata.worldbank.org/catalog/3823/get-microdata |
| 4 | JAM_1997_SLC_v01_M | 200 | 1 | no_direct_raw_route_access_gate_detected | manual_account_or_terms_required | https://microdata.worldbank.org/catalog/2368/get-microdata |
| 5 | KGZ_1993_KMPS_v01_M | 200 | 1 | no_direct_raw_route_access_gate_detected | manual_account_or_terms_required | https://microdata.worldbank.org/catalog/280/get-microdata |
| 6 | MWI_2007-2009_MTM_v01_M | 200 | 1 | no_direct_raw_route_access_gate_detected | manual_account_or_terms_required | https://microdata.worldbank.org/catalog/3462/get-microdata |
| 7 | MWI_2004_IHS-II_v01_M | 200 | 1 | no_direct_raw_route_access_gate_detected | manual_account_or_terms_required | https://microdata.worldbank.org/catalog/2307/get-microdata |
| 8 | NPL_2010_LSS-III_v01_M | 200 | 1 | no_direct_raw_route_access_gate_detected | manual_account_or_terms_required | https://microdata.worldbank.org/catalog/1000/get-microdata |
| 9 | NGA_2012_GHSP-W2_v02_M | 200 | 1 | no_direct_raw_route_access_gate_detected | manual_account_or_terms_required | https://microdata.worldbank.org/catalog/1952/get-microdata |
| 10 | NGA_2015_GHSP-W3_v02_M | 200 | 1 | no_direct_raw_route_access_gate_detected | manual_account_or_terms_required | https://microdata.worldbank.org/catalog/2734/get-microdata |

## Interpretation Guardrails

- A saved HTML page is documentation evidence, not raw microdata.
- Candidate raw links are not downloaded or treated as usable unless access terms are manually satisfied.
- If an access gate is detected, the dataset remains blocked until the account, terms, or Data Access Agreement step is completed and raw files are placed in `temp/raw_downloads/`.

## Machine-Readable Outputs

- `temp/first_batch_official_raw_access_probe.csv`
- `result/first_batch_official_raw_access_summary.csv`
