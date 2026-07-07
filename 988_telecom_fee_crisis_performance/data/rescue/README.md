# Rescue Data README

This folder contains additive identification-rescue datasets. Existing project data and reports were not overwritten.

## Key Files

- `analysis_panel_rescue.csv`: original analysis panel plus corrected `in_state_answer_rate_rescue`.
- `analysis_panel_rescue_treatments.csv`: rescue panel plus alternative treatment timing and dose variables.
- `fee_timing_audit_state.csv`: state-by-state treatment timing audit.
- `pdf_validation_sample_audit.csv`: validation audit for the original 30-row PDF sample.
- `pdf_answer_rate_denominator_audit_by_month.csv`: month-level answer-rate denominator check.
- `panel_coverage_audit.csv`: panel coverage and missing-month summary.
- `routing_mismatch_exposure_state.csv`: ACS proxy exposure variables for georouting/routing mismatch.
- `georouting_timeline.csv`: official georouting policy and implementation timeline.
- `legislative_988_fee_bills.csv`: bill-level legislative near-miss scan.
- `capacity_disbursement_source_scan.csv`: feasibility scan for disbursement/capacity timing.

## Important Caveat

The routing mismatch variables are proxies only. They are not actual phone-number, area-code, carrier, or handset-location data.
