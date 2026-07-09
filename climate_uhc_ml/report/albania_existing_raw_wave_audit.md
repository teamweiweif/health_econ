# Existing Albania Raw Wave Audit

Status: local raw-wave utilization audit only. This report makes already-present Albania LSMS raw archives/extractions visible for future wave-specific auditing. It does not promote any wave into `data/`, does not construct harmonized outcomes, and does not construct climate linkage.

## Summary

| Metric | Value | Interpretation |
|---|---:|---|
| albania_existing_raw_wave_rows | 4 | Existing Albania LSMS wave rows audited. |
| albania_existing_raw_wave_archive_present_rows | 4 | Audited waves with raw archive present. |
| albania_existing_raw_wave_extracted_rows | 4 | Audited waves with extracted raw root present. |
| albania_existing_raw_wave_unintegrated_rows | 3 | Audited waves present locally but not yet in the core schema inventory. |
| albania_existing_raw_wave_deep_audited_rows | 4 | Audited waves with at least one existing deep raw/core audit layer. |
| albania_existing_raw_wave_total_raw_tabular_files | 163 | Total raw .sav files under audited Albania wave extraction roots. |
| albania_existing_raw_wave_total_raw_variable_rows | 4148 | Total raw variables readable from audited Albania wave extraction roots. |
| albania_existing_raw_wave_oop_signal_rows | 4 | Audited waves with at least one OOP/health-expenditure keyword signal. |
| albania_existing_raw_wave_timing_signal_rows | 0 | Audited waves with apparent interview/fieldwork timing keyword signals. |
| albania_existing_raw_wave_gps_signal_rows | 0 | Audited waves with GPS/coordinate keyword signals. |
| albania_existing_raw_wave_harmonization_ready_rows | 0 | Existing Albania waves ready for harmonized data promotion after this audit. |
| albania_existing_raw_wave_climate_linkage_ready_rows | 0 | Existing Albania waves ready for climate-linkage input promotion after this audit. |
| albania_existing_raw_wave_current_decision | present_raw_waves_require_wave_specific_schema_value_key_timing_audits | Current decision for existing Albania raw waves. |

## Wave Rows

| idno | wave | archive_present | raw_tabular_files | raw_variable_rows | schema_inventory_status | current_status |
|---|---|---|---|---|---|---|
| ALB_2002_LSMS_v01_M | 2002 | 1 | 43 | 860 | not_in_core_schema_inventory | household_core_outcome_semantics_crosswalk_boundary_name_audited_timing_geography_observed_climate_blocked |
| ALB_2005_LSMS_v01_M | 2005 | 1 | 44 | 1187 | in_core_schema_inventory | documented_core_provisional_outcome_semantics_timing_audited_but_blocked |
| ALB_2008_LSMS_v01_M | 2008 | 1 | 42 | 1195 | not_in_core_schema_inventory | household_core_outcome_semantics_timing_audited_but_blocked_by_coarse_geography_no_interview_timing |
| ALB_2012_LSMS_v01_M_v01_A_PUF | 2012 | 1 | 34 | 906 | not_in_core_schema_inventory | raw_core_outcome_semantics_questionnaire_timing_audited_but_blocked_by_no_raw_interview_timing_coarse_geography |

## Concept Signal Counts

| idno | consumption_signal_count | oop_health_signal_count | health_need_access_signal_count | timing_signal_count | geography_signal_count | gps_signal_count | shock_signal_count |
|---|---|---|---|---|---|---|---|
| ALB_2002_LSMS_v01_M | 2 | 30 | 42 | 0 | 11 | 0 | 0 |
| ALB_2005_LSMS_v01_M | 3 | 37 | 57 | 0 | 38 | 0 | 3 |
| ALB_2008_LSMS_v01_M | 2 | 36 | 56 | 0 | 32 | 0 | 3 |
| ALB_2012_LSMS_v01_M_v01_A_PUF | 4 | 1 | 37 | 0 | 10 | 0 | 7 |

## Interpretation

- ALB_2002 now has temp household-core, provisional outcome, raw outcome-semantics, district crosswalk, and public boundary name-match diagnostics with observed interview date/month and district fields, but remains blocked by manual OOP/access unit, recall, missing-code, skip-pattern, unmatched KORCE label, duplicate current-boundary names, unverified district boundary polygons/historical crosswalk, no-GPS, and cross-wave comparability checks.
- ALB_2012 raw archives/extractions are present locally and now have temp raw-core, provisional outcome-feasibility, raw outcome-semantics, timing/geography, and questionnaire timing-field audits, but remain blocked because questionnaire timing fields are not verified raw household interview timing values; coarse prefecture/region-only geography, no GPS, OOP/access unit and recall review, gift/payment-scope policy, skip patterns, and service-quality proxy interpretation also remain unresolved.
- ALB_2008 has household-core, provisional outcome-feasibility, raw outcome-semantics, and timing/geography audits, but remains blocked by missing interview timing, coarse non-GPS geography, OOP units, recall periods, missing-code semantics, skip patterns, gift/payment-scope policy, service-quality proxy interpretation, and cross-wave comparability.
- ALB_2005 now has documented, household-core, provisional outcome, raw outcome-semantics, and timing/geography audits, but remains blocked by timing/geography, gift/payment-scope policy, OOP units, recall periods, missing-code semantics, skip patterns, merge keys, and cross-wave comparability.
- ALB_2002, ALB_2005, and ALB_2008 legacy `.xls` questionnaires are present, readable, and now have a timing/control field audit; the audit documents form-design evidence but does not promote any wave because raw household timing/geography and outcome-semantics gates remain unresolved.
- Keyword signals are triage evidence only. They do not verify units, recall periods, missing codes, merge keys, fieldwork timing, current geography, or comparability.
- Promotion-ready harmonized rows and climate-linkage-ready rows remain zero.

## Machine-Readable Outputs

- `temp/albania_existing_raw_wave_audit.csv`
- `result/albania_existing_raw_wave_audit_summary.csv`
