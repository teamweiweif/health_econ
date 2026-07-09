# ALB_2002 Weight And Design Evidence Audit

Status: fail-closed. This audit documents the ALB_2002 household weight and survey-design evidence now visible in local raw files and official study-page metadata. It does not promote weighted inference or write analysis-ready data.

## Summary

| Metric | Value | Interpretation |
|---|---:|---|
| alb2002_weight_design_evidence_audit_rows | 6 | Rows in the ALB_2002 weight/design evidence audit. |
| alb2002_weight_design_source_page_reachable_rows | 1 | Official study page or saved snapshot available for source context. |
| alb2002_weight_design_source_page_flag_rows | 9 | Official study-page flags detected for study identity, sampling context, fieldwork, and GPS intent. |
| alb2002_weight_design_raw_weight_file_rows | 3599 | Rows read from weights_1.sav. |
| alb2002_weight_design_positive_weight_rows | 3599 | Rows with positive household weights in weights_1.sav. |
| alb2002_weight_design_candidate_key_match_rows | 3599 | Readable weight-file keys matching the temp household core candidate. |
| alb2002_weight_design_distinct_psu_rows | 450 | Distinct PSU values in the readable weight file. |
| alb2002_weight_design_distinct_stratum_rows | 4 | Distinct stratum values in the readable weight file. |
| alb2002_weight_design_weighted_inference_ready_rows | 0 | Rows ready for promoted weighted inference; intentionally zero. |
| alb2002_weight_design_harmonized_promotion_ready_rows | 0 | Rows ready for harmonized data promotion after this audit; intentionally zero. |
| alb2002_weight_design_current_decision | blocked_alb2002_weight_design_semantics_not_promotion_ready | Current fail-closed ALB_2002 weight/design decision. |

## Evidence Rows

| evidence_domain | evidence_item | observed_rows | promotion_ready_rows | evidence_status | diagnostic_value |
|---|---|---|---|---|---|
| official_study_metadata | worldbank_study_page_sampling_context | 1 | 0 | official_page_context_seen_weight_rules_not_explicit | page_status=reachable_page_saved; http_status=200; sha256=2d8d869a05bc15ccace49525494e9474af3d8d8a9973d8d2829fae11ae8ef1e6; referenc... |
| raw_weight_file_metadata | weights_1_sav_variable_labels | 3599 | 0 | raw_weight_file_readable_household_weight_label_seen | read_status=read_ok; sha256=f22a8607282f7c2e84d8cd712f1f0053984a780241f42843ebb239169fdd6736; columns=psu;hh;distr;distr_n;hhid;stra... |
| raw_weight_file_metadata | weights_sav_legacy_encoding_probe | 0 | 0 | legacy_weight_file_not_used_weight_1_readable | legacy_weight_probe_status=metadata_read_failed_latin1:SystemError;cp1252:SystemError;iso-8859-1:SystemError |
| raw_weight_value_coverage | household_weight_values_and_key_coverage | 3599 | 0 | complete_positive_weight_key_coverage_design_semantics_blocked | positive_weight_rows=3599; nonmissing_weight_rows=3599; min=40.885; p50=177.517; p95=412.2; max=412.2; sum=726851; distinct_keys=359... |
| raw_design_fields | psu_stratum_urban_rural_fields_available | 3599 | 0 | design_fields_available_in_raw_and_candidate_design_semantics_blocked | distinct_psu=450; distinct_stratum=4; distinct_urban_rural=2; distinct_district=36; candidate_has_stratum=1; candidate_has_urban_rur... |
| promotion_gate | weighted_inference_and_harmonized_promotion_gate | 1 | 0 | blocked_alb2002_weight_design_semantics_not_promotion_ready | weight/design evidence is stronger than before, but promotion-ready rows remain zero by design |

## Interpretation

- `weights_1.sav` is readable and contains household keys, district, stratum, urban/rural, household size, and a `weight` variable labelled as household weights.
- The readable weight file covers the 3,599 temp household-core rows and carries positive household weights for all rows.
- The official World Bank study page verifies the ALB_2002 study identity and sampling context, including the 2001 census sampling frame and fieldwork context, and documents GPS intent. It is not enough by itself to promote GPS linkage or final weighted inference.
- Promotion remains blocked because the target population, weight normalization, survey-design variance handling, finite-population assumptions, and downstream outcome/climate gates have not all passed together.

## Machine-Readable Outputs

- `temp/alb2002_weight_design_evidence_audit.csv`
- `result/alb2002_weight_design_evidence_summary.csv`
- `temp/source_snapshots/alb2002_worldbank_study_description_weight_design.html`
