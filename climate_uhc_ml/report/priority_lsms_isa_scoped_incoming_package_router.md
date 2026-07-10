# Priority LSMS/ISA Scoped Incoming Package Router

Status: non-destructive incoming-package router for the locked 10 download-required
LSMS/ISA country-waves.

This artifact is narrower than the older broad incoming router. It uses
`result/priority_lsms_isa_acquisition_route_decision.csv` as the scope lock, so
the rows match the current dataset-promotion target: Ethiopia, Nigeria, Tanzania,
Uganda, and Nepal download-required waves, with Malawi 2004 retained as the
already promoted anchor outside this incoming queue.

It scans `temp/raw_downloads/_incoming/`, scores any files found there against
official expected filenames, core-file manifests, IDNO hints, catalog IDs, and
country/year hints. It does not download, move, delete, extract, write `data/`,
or promote any wave.

## Summary

| metric | value | interpretation |
| --- | --- | --- |
| scoped_incoming_router_target_rows | 10 | Download-required waves from the locked 10-wave route decision scope. |
| scoped_incoming_router_country_rows | 5 | Countries covered by the scoped incoming router. |
| scoped_incoming_router_priority_country_rows | 9 | Rows from Ethiopia, Nigeria, Malawi, Tanzania, or Uganda. |
| scoped_incoming_router_sixth_country_rows | 1 | Rows supplying the sixth country. |
| scoped_incoming_router_incoming_file_rows | 0 | Files currently staged under temp/raw_downloads/_incoming. |
| scoped_incoming_router_candidate_evidence_rows | 10 | Incoming-package evidence rows, including fail-closed waiting rows. |
| scoped_incoming_router_expected_core_file_rows | 323 | Expected core-file checks across the 10 target waves. |
| scoped_incoming_router_copy_candidate_rows | 0 | Targets with a single suggested incoming file to copy after review. |
| scoped_incoming_router_pending_drop_rows | 10 | Targets still waiting for an incoming package drop. |
| scoped_incoming_router_manual_review_rows | 0 | Targets requiring manual route review. |
| data_write_gate_status | blocked_no_data_write | The router only writes manifests and reports. |
| modeling_gate_status | blocked | No modeling is opened by incoming package routing. |
| scoped_incoming_router_status_waiting_for_incoming_package | 10 | Scoped incoming router route status count. |

## Target Route Plan

| download_rank | country | wave | idno | route_status | top_incoming_file_name | top_route_score | local_target_folder |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | Ethiopia | 2021-2022 | ETH_2021_ESPS-W5_v02_M | waiting_for_incoming_package |  |  | temp/raw_downloads/ETH_2021_ESPS-W5_v02_M/ |
| 2 | Ethiopia | 2018-2019 | ETH_2018_ESS_v04_M | waiting_for_incoming_package |  |  | temp/raw_downloads/ETH_2018_ESS_v04_M/ |
| 3 | Nigeria | 2012-2013 | NGA_2012_GHSP-W2_v02_M | waiting_for_incoming_package |  |  | temp/raw_downloads/NGA_2012_GHSP-W2_v02_M/ |
| 4 | Nigeria | 2015-2016 | NGA_2015_GHSP-W3_v02_M | waiting_for_incoming_package |  |  | temp/raw_downloads/NGA_2015_GHSP-W3_v02_M/ |
| 5 | Nigeria | 2010-2011 | NGA_2010_GHSP-W1_v03_M | waiting_for_incoming_package |  |  | temp/raw_downloads/NGA_2010_GHSP-W1_v03_M/ |
| 6 | Tanzania | 2008-2009 | TZA_2008_NPS-R1_v03_M | waiting_for_incoming_package |  |  | temp/raw_downloads/TZA_2008_NPS-R1_v03_M/ |
| 7 | Tanzania | 2010-2011 | TZA_2010_NPS-R2_v03_M | waiting_for_incoming_package |  |  | temp/raw_downloads/TZA_2010_NPS-R2_v03_M/ |
| 8 | Tanzania | 2012-2013 | TZA_2012_NPS-R3_v01_M | waiting_for_incoming_package |  |  | temp/raw_downloads/TZA_2012_NPS-R3_v01_M/ |
| 9 | Uganda | 2019-2020 | UGA_2019_UNPS_v03_M | waiting_for_incoming_package |  |  | temp/raw_downloads/UGA_2019_UNPS_v03_M/ |
| 10 | Nepal | 2010-2011 | NPL_2010_LSS-III_v01_M | waiting_for_incoming_package |  |  | temp/raw_downloads/NPL_2010_LSS-III_v01_M/ |

## Evidence Preview

| download_rank | idno | incoming_file_name | route_score | expected_file_name_matches | core_file_name_matches | evidence_status |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | ETH_2021_ESPS-W5_v02_M |  |  |  |  | waiting_for_incoming_package |
| 2 | ETH_2018_ESS_v04_M |  |  |  |  | waiting_for_incoming_package |
| 3 | NGA_2012_GHSP-W2_v02_M |  |  |  |  | waiting_for_incoming_package |
| 4 | NGA_2015_GHSP-W3_v02_M |  |  |  |  | waiting_for_incoming_package |
| 5 | NGA_2010_GHSP-W1_v03_M |  |  |  |  | waiting_for_incoming_package |
| 6 | TZA_2008_NPS-R1_v03_M |  |  |  |  | waiting_for_incoming_package |
| 7 | TZA_2010_NPS-R2_v03_M |  |  |  |  | waiting_for_incoming_package |
| 8 | TZA_2012_NPS-R3_v01_M |  |  |  |  | waiting_for_incoming_package |
| 9 | UGA_2019_UNPS_v03_M |  |  |  |  | waiting_for_incoming_package |
| 10 | NPL_2010_LSS-III_v01_M |  |  |  |  | waiting_for_incoming_package |

## Use Rule

Only run a generated copy command after confirming the incoming file is an
unchanged official World Bank package for that wave. Copying a package into the
target folder starts receipt/schema/value/semantics validation; it does not make
the wave analysis-ready.
