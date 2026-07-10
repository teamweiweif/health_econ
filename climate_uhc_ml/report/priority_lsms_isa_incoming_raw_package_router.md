# Priority LSMS/ISA Incoming Raw Package Router

Status: non-destructive routing audit for manually downloaded raw packages.

This router scans `temp/raw_downloads/_incoming/` and scores each incoming file
against the refocused LSMS/ISA action queue using official expected filenames,
core-file names, IDNO hints, country/year hints, and catalog IDs. It does not
download, move, delete, extract, or promote data.

## Summary

| metric | value | interpretation |
| --- | --- | --- |
| priority_lsms_incoming_router_incoming_folder_exists | 1 | Whether temp/raw_downloads/_incoming exists. |
| priority_lsms_incoming_router_action_country_wave_rows | 18 | Country-waves considered by the incoming raw package router. |
| priority_lsms_incoming_router_incoming_file_rows | 0 | Files currently found under the incoming raw package folder. |
| priority_lsms_incoming_router_candidate_rows | 0 | Scored incoming-file to country-wave route candidates. |
| priority_lsms_incoming_router_copy_candidate_rows | 0 | Incoming files with a single top suggested target folder. |
| priority_lsms_incoming_router_manual_review_rows | 0 | Incoming files that require manual route review. |
| priority_lsms_incoming_router_data_write_status | blocked_no_data_write | Routing suggestions do not permit data/ writes. |
| modeling_gate_status | blocked | No predictive, reduced-form, causal ML, or policy learning until registry thresholds pass. |

## Route Plan

_No rows._

## Candidate Preview

_No rows._

## Rule

Only review and run a generated copy command after checking that the incoming
file is an unchanged official package from the World Bank get-microdata workflow.
Copying a file to a target folder still only starts receipt validation; it does
not make a country-wave analysis-ready.
