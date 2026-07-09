# Empirical Readiness Dashboard

Status: consolidated evidence map only. No country-wave is currently analysis-ready because final outcomes and analysis-ready climate-linked data are absent. Limited ALB_2002 harmonized household, CHE-only outcome, fallback climate exposure, and linked diagnostic files may exist for inspection only and do not unlock descriptive, model, causal, or policy claims.

## Purpose

This dashboard joins acquisition, sample-selection, harmonization, SDG 3.8.2 denominator, climate linkage, outcome, modeling, mechanism, and go/no-go gates into one country-wave table. It is meant to guide manual raw-data acquisition and prevent premature country selection or empirical claims.

## Counts

| Metric | Value | Interpretation |
|---|---:|---|
| dashboard_rows | 23 | Priority acquisition bundle rows in the dashboard. |
| country_count | 11 | Unique countries in priority acquisition bundles. |
| no_go_rule_rows | 8 | Pre-specified go/no-go threshold rows. |
| no_go_pass_rows | 2 | Go/no-go rules currently passing. |
| no_go_blocked_rows | 6 | Go/no-go rules blocked or failing. |
| limited_harmonized_household_rows | 3599 | Country-wave rows ready at this stage. |
| limited_household_outcome_rows | 3599 | Country-wave rows ready at this stage. |
| limited_climate_exposure_rows | 384 | Country-wave rows ready at this stage. |
| limited_climate_linked_rows | 14396 | Country-wave rows ready at this stage. |
| harmonization_ready_country_waves | 0 | Country-wave rows ready at this stage. |
| sdg382_ready_country_waves | 0 | Country-wave rows ready at this stage. |
| climate_ready_country_waves | 0 | Country-wave rows ready at this stage. |
| outcome_ready_country_waves | 1 | Country-wave rows ready at this stage. |
| reduced_form_ready_country_waves | 0 | Country-wave rows ready at this stage. |
| mechanism_ready_country_waves | 0 | Country-wave rows ready at this stage. |
| current_stage_harmonization_value_audit_required | 1 | Dashboard current-stage count. |
| current_stage_manual_raw_download_required | 22 | Dashboard current-stage count. |
| claim_status_metadata_protocol_only_no_empirical_claims | 22 | Allowed claim status count. |
| claim_status_raw_schema_claims_only_no_analysis_dataset_claims | 1 | Allowed claim status count. |

## Current Stage

| Current stage | Count |
|---|---:|
| manual_raw_download_required | 22 |
| harmonization_value_audit_required | 1 |

## Allowed Claim Status

| Allowed claim status | Count |
|---|---:|
| metadata_protocol_only_no_empirical_claims | 22 |
| raw_schema_claims_only_no_analysis_dataset_claims | 1 |

## Go/No-Go Status

| Go/no-go status | Count |
|---|---:|
| blocked_raw_microdata | 6 |
| pass | 2 |

| rule_id | threshold | current_value | status | next_action |
|---|---|---|---|---|
| main_financial_protection_minimum_countries | >=6 raw-verified countries | 0 | blocked_raw_microdata | complete raw downloads and verify consumption, OOP, geography, timing, and weights |
| double_failure_minimum_country_waves | >=10 raw-verified country-waves | 1 | blocked_raw_microdata | verify financial and access outcome concepts in raw data before promoting the composite outcome |
| climate_geography_precision | verified timing/geography for most analytical country-waves | 0 | blocked_raw_microdata | inspect raw timing/geography variables and classify GPS/admin linkage quality |
| event_rate_minimum | event rate >=3% after outcome construction | 3599 | blocked_raw_microdata | run promoted descriptive diagnostics after climate-linked data before treating event-rate checks as model-r... |
| transportable_prediction | validated non-random predictive metrics | 30 | pass | run predictive ML only after audited outcomes and climate-linked data exist |
| climate_lead_placebo | future-shock placebo attempted and passes | 88 | pass | estimate main reduced-form model, then run future climate lead placebo |
| causal_ml_policy_value | causal ML and policy learning ready after credible reduced-form design | 0 | blocked_raw_microdata | do not run causal ML or policy learning until identification and validation gates pass |
| descriptive_fallback | descriptive diagnostics attempted after data construction | 3599 | blocked_raw_microdata | resolve climate-linkage gates, then run descriptive diagnostics before deciding manuscript scope |

## Priority Bundle Snapshot

| bundle_rank | country | wave | idno | current_stage | analysis_claim_status | next_blocking_action |
|---|---|---|---|---|---|---|
| 1 | Albania | 2005 | ALB_2005_LSMS_v01_M | harmonization_value_audit_required | raw_schema_claims_only_no_analysis_dataset_claims | complete harmonization value/unit/recall/key audits and assemble verified recipe candidates |
| 2 | Ethiopia | 2021-2022 | ETH_2021_ESPS-W5_v02_M | manual_raw_download_required | metadata_protocol_only_no_empirical_claims | place original raw archives/files in the target folder, then run raw-download and schema inspection |
| 3 | Ethiopia | 2018-2019 | ETH_2018_ESS_v04_M | manual_raw_download_required | metadata_protocol_only_no_empirical_claims | place original raw archives/files in the target folder, then run raw-download and schema inspection |
| 4 | Jamaica | 1997 | JAM_1997_SLC_v01_M | manual_raw_download_required | metadata_protocol_only_no_empirical_claims | place original raw archives/files in the target folder, then run raw-download and schema inspection |
| 5 | Kyrgyz Republic | 1993 | KGZ_1993_KMPS_v01_M | manual_raw_download_required | metadata_protocol_only_no_empirical_claims | place original raw archives/files in the target folder, then run raw-download and schema inspection |
| 6 | Malawi | 2007-2009 | MWI_2007-2009_MTM_v01_M | manual_raw_download_required | metadata_protocol_only_no_empirical_claims | place original raw archives/files in the target folder, then run raw-download and schema inspection |
| 7 | Malawi | 2004-2005 | MWI_2004_IHS-II_v01_M | manual_raw_download_required | metadata_protocol_only_no_empirical_claims | place original raw archives/files in the target folder, then run raw-download and schema inspection |
| 8 | Nepal | 2010-2011 | NPL_2010_LSS-III_v01_M | manual_raw_download_required | metadata_protocol_only_no_empirical_claims | place original raw archives/files in the target folder, then run raw-download and schema inspection |
| 9 | Nigeria | 2012-2013 | NGA_2012_GHSP-W2_v02_M | manual_raw_download_required | metadata_protocol_only_no_empirical_claims | place original raw archives/files in the target folder, then run raw-download and schema inspection |
| 10 | Nigeria | 2015-2016 | NGA_2015_GHSP-W3_v02_M | manual_raw_download_required | metadata_protocol_only_no_empirical_claims | place original raw archives/files in the target folder, then run raw-download and schema inspection |
| 11 | Nigeria | 2010-2011 | NGA_2010_GHSP-W1_v03_M | manual_raw_download_required | metadata_protocol_only_no_empirical_claims | place original raw archives/files in the target folder, then run raw-download and schema inspection |
| 12 | Tanzania | 2008-2009 | TZA_2008_NPS-R1_v03_M | manual_raw_download_required | metadata_protocol_only_no_empirical_claims | place original raw archives/files in the target folder, then run raw-download and schema inspection |
| 13 | Tanzania | 2010-2011 | TZA_2010_NPS-R2_v03_M | manual_raw_download_required | metadata_protocol_only_no_empirical_claims | place original raw archives/files in the target folder, then run raw-download and schema inspection |
| 14 | Tanzania | 2012-2013 | TZA_2012_NPS-R3_v01_M | manual_raw_download_required | metadata_protocol_only_no_empirical_claims | place original raw archives/files in the target folder, then run raw-download and schema inspection |
| 15 | Uganda | 2014 | UGA_2014_SAGE-EL_v01_M | manual_raw_download_required | metadata_protocol_only_no_empirical_claims | place original raw archives/files in the target folder, then run raw-download and schema inspection |
| 16 | Uganda | 2012 | UGA_2012_SAGE-BL_v01_M | manual_raw_download_required | metadata_protocol_only_no_empirical_claims | place original raw archives/files in the target folder, then run raw-download and schema inspection |
| 17 | Uganda | 2013 | UGA_2013_SAGE-ML_v01_M | manual_raw_download_required | metadata_protocol_only_no_empirical_claims | place original raw archives/files in the target folder, then run raw-download and schema inspection |
| 18 | Bulgaria | 1995 | BGR_1995_IHS_v01_M | manual_raw_download_required | metadata_protocol_only_no_empirical_claims | place original raw archives/files in the target folder, then run raw-download and schema inspection |
| 19 | Bulgaria | 1997 | BGR_1997_IHS_v01_M | manual_raw_download_required | metadata_protocol_only_no_empirical_claims | place original raw archives/files in the target folder, then run raw-download and schema inspection |
| 20 | Ethiopia | 2016-2020 | ETH_2016-2020_FJW_v01_M | manual_raw_download_required | metadata_protocol_only_no_empirical_claims | place original raw archives/files in the target folder, then run raw-download and schema inspection |

## Outputs

- `result/empirical_readiness_dashboard.csv`
- `result/empirical_no_go_threshold_status.csv`
- `result/empirical_readiness_dashboard_summary.csv`

## Guardrails

- This dashboard does not select final countries.
- This dashboard does not construct `data/` outputs.
- Limited harmonized household and fallback climate exposure files do not count as final outcome, climate-linked, model-ready, or policy-ready data.
- Dashboard rows remain blocked for empirical claims until outcome, climate, and model gates pass.
