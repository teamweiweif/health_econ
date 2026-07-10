# Priority LSMS/ISA Acquisition Route Decision

Status: consolidated acquisition-route decision for the 10 download-required
waves in the locked LSMS/ISA dataset-promotion scope.

This artifact does not download, copy, extract, write promoted `data/`, expose
credentials, or run models. It merges official endpoint evidence, resource-
level route probes, redacted session-material presence, browser/manual starter
commands, local target-folder counts, and post-download validation commands.

## Summary

| metric | value | interpretation |
| --- | --- | --- |
| acquisition_route_decision_rows | 10 | Download-required waves with a consolidated acquisition-route decision. |
| acquisition_route_decision_country_rows | 5 | Countries covered by the download-required route decision rows. |
| acquisition_route_decision_priority_country_rows | 9 | Download-required rows from Ethiopia, Nigeria, Malawi, Tanzania, or Uganda. |
| acquisition_route_decision_sixth_country_rows | 1 | Download-required rows that supply the sixth country. |
| acquisition_route_decision_local_files_present_rows | 0 | Rows with local non-generated files ready for validation. |
| acquisition_route_decision_public_raw_candidate_rows | 0 | Rows with public raw-route candidate evidence requiring terms review. |
| acquisition_route_decision_credentialed_probe_ready_rows | 0 | Rows with local redacted session material available for credentialed probing. |
| acquisition_route_decision_browser_manual_required_rows | 10 | Rows whose current route is browser/manual terms acceptance and local file placement. |
| acquisition_route_decision_access_gate_rows | 10 | Rows with access-gate evidence from endpoint or resource-route probes. |
| acquisition_route_decision_expected_core_file_rows | 323 | Expected core raw-file rows that will be checked after acquisition. |
| data_write_gate_status | blocked_no_data_write | Route decision artifacts do not write promoted data. |
| modeling_gate_status | blocked | No predictive, reduced-form, causal ML, or policy learning is opened. |
| acquisition_route_decision_status_browser_manual_terms_acceptance_required | 10 | Acquisition route decision status count. |

## Route Decisions

| download_rank | country | wave | idno | acquisition_route_decision | target_file_count | endpoint_get_microdata_gate_endpoints | resource_raw_payload_candidate_rows | credentialed_ready_to_probe | browser_starter_status |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | Ethiopia | 2021-2022 | ETH_2021_ESPS-W5_v02_M | browser_manual_terms_acceptance_required | 0 | 1 | 0 | 0 | ready_for_browser_terms_acceptance |
| 2 | Ethiopia | 2018-2019 | ETH_2018_ESS_v04_M | browser_manual_terms_acceptance_required | 0 | 1 | 0 | 0 | ready_for_browser_terms_acceptance |
| 3 | Nigeria | 2012-2013 | NGA_2012_GHSP-W2_v02_M | browser_manual_terms_acceptance_required | 0 | 1 | 0 | 0 | ready_for_browser_terms_acceptance |
| 4 | Nigeria | 2015-2016 | NGA_2015_GHSP-W3_v02_M | browser_manual_terms_acceptance_required | 0 | 1 | 0 | 0 | ready_for_browser_terms_acceptance |
| 5 | Nigeria | 2010-2011 | NGA_2010_GHSP-W1_v03_M | browser_manual_terms_acceptance_required | 0 | 1 | 0 | 0 | ready_for_browser_terms_acceptance |
| 6 | Tanzania | 2008-2009 | TZA_2008_NPS-R1_v03_M | browser_manual_terms_acceptance_required | 0 | 1 | 0 | 0 | ready_for_browser_terms_acceptance |
| 7 | Tanzania | 2010-2011 | TZA_2010_NPS-R2_v03_M | browser_manual_terms_acceptance_required | 0 | 1 | 0 | 0 | ready_for_browser_terms_acceptance |
| 8 | Tanzania | 2012-2013 | TZA_2012_NPS-R3_v01_M | browser_manual_terms_acceptance_required | 0 | 1 | 0 | 0 | ready_for_browser_terms_acceptance |
| 9 | Uganda | 2019-2020 | UGA_2019_UNPS_v03_M | browser_manual_terms_acceptance_required | 0 | 1 | 0 | 0 | ready_for_browser_terms_acceptance |
| 10 | Nepal | 2010-2011 | NPL_2010_LSS-III_v01_M | browser_manual_terms_acceptance_required | 0 | 1 | 0 | 0 | ready_for_browser_terms_acceptance |

## Immediate Use

Rows with `browser_manual_terms_acceptance_required` should be handled by
opening the official get-microdata URL, accepting official World Bank terms,
placing the complete unchanged package under the listed target folder, and
then running the per-IDNO post-download validation runner.

Rows with local files present should run receipt, schema, value-profile,
semantics, timing/geography, climate-linkage, and promotion-packet gates before
any write into `data/`.

## Stop Rule

No row becomes analysis-ready from this route decision alone. Promotion still
requires complete official raw package receipt, value verification, accepted
outcome construction, survey timing/geography evidence, and CHIRPS or ERA5
climate-linkage acceptance.
