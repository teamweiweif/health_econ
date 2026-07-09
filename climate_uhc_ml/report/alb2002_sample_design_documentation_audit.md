# ALB_2002 Sample Design Documentation Audit

Status: documented candidate, not promoted. This audit snapshots the official World Bank Basic Information document and checks whether its sample-design statements concord with the local ALB_2002 weight file and temp household candidate.

## Summary

| Metric | Value | Interpretation |
|---|---:|---|
| alb2002_sample_design_documentation_audit_rows | 7 | Rows in the ALB_2002 sample-design documentation audit. |
| alb2002_sample_design_pdf_available_rows | 1 | Official Basic Information PDF snapshot available locally. |
| alb2002_sample_design_pdf_pages | 66 | Pages extracted from the official Basic Information PDF. |
| alb2002_sample_design_text_chars | 168234 | Characters extracted from the official Basic Information PDF. |
| alb2002_sample_design_official_450_psu_8_hh_rows | 1 | Official text states a 450 PSU by 8 household sample-design claim. |
| alb2002_sample_design_official_3599_final_rows | 1 | Official text states or supports the 3,599 final household sample size. |
| alb2002_sample_design_april_2001_census_frame_rows | 1 | Official text documents the April 2001 census sampling-frame context. |
| alb2002_sample_design_tirana_listing_rows | 1 | Official text documents the Tirana quick-count or listing context. |
| alb2002_sample_design_reserve_replacement_rows | 1 | Official text documents reserve household or replacement context. |
| alb2002_sample_design_raw_weight_rows | 3599 | Rows read from the ALB_2002 readable household weight file. |
| alb2002_sample_design_positive_weight_rows | 3599 | Rows with positive household weights. |
| alb2002_sample_design_distinct_psu_rows | 450 | Distinct PSU values in the readable weight file. |
| alb2002_sample_design_distinct_stratum_rows | 4 | Distinct stratum values in the readable weight file. |
| alb2002_sample_design_candidate_rows | 3599 | Rows in the temp ALB_2002 household core candidate. |
| alb2002_sample_design_expected_design_household_rows | 3600 | 450 PSU by 8 households per PSU design arithmetic. |
| alb2002_sample_design_documented_final_sample_rows | 3599 | Official final household sample size used for concordance checks. |
| alb2002_sample_design_raw_design_concordance_rows | 1 | Raw and candidate counts concordant with official sample-design/final-sample evidence. |
| alb2002_sample_design_documentation_ready_rows | 1 | Sample-design documentation evidence ready; this is not analysis-data promotion. |
| alb2002_sample_design_weighted_inference_ready_rows | 0 | Rows ready for promoted weighted inference; intentionally zero. |
| alb2002_sample_design_harmonized_promotion_ready_rows | 0 | Rows ready for harmonized data promotion after this audit; intentionally zero. |
| alb2002_sample_design_current_decision | candidate_alb2002_sample_design_documented_not_promoted_due_downstream_gates | Current ALB_2002 sample-design documentation decision. |

## Evidence Rows

| evidence_domain | evidence_item | observed_rows | promotion_ready_rows | evidence_status | diagnostic_value |
|---|---|---|---|---|---|
| official_basic_information_document | worldbank_basic_information_pdf_snapshot | 1 | 0 | official_pdf_snapshot_available | pdf_status=reachable_pdf_saved; http_status=200; content_type=application/octet-stream; bytes=363262; sha256=0a6966f81d0595741f202c5... |
| official_basic_information_document | pdf_text_extraction | 1 | 0 | pdf_text_extracted | text_status=text_extracted_with_pypdf; pages=66; text_chars=168234 |
| official_sample_design_claims | final_sample_design_and_size | 1 | 0 | official_450_psu_8_household_design_and_3599_final_sample_seen | sample_design_450_psu_8_households_seen=1; final_sample_3599_seen=1; one_household_drop_seen=1 |
| official_sample_design_claims | sampling_frame_fieldwork_and_listing_context | 1 | 0 | official_sampling_frame_and_listing_context_seen | april_2001_census_sampling_frame_seen=1; tirana_quick_count_listing_seen=1; fieldwork_april_july_seen=1 |
| official_sample_design_claims | reserve_household_and_replacement_context | 1 | 0 | official_replacement_context_seen | reserve_household_replacement_seen=1 |
| raw_design_count_concordance | raw_weights_candidate_and_official_sample_size_match | 1 | 0 | raw_weight_candidate_counts_concordant_with_official_final_sample | expected_design_rows=450*8=3600; documented_final_rows=3599; weight_read_status=read_ok; raw_weight_rows=3599; positive_weight_rows=... |
| documentation_gate | sample_design_documentation_ready_not_promotion_ready | 1 | 0 | candidate_alb2002_sample_design_documented_not_promoted_due_downstream_gates | documentation_ready_rows=1; weighted_inference_ready_rows=0; harmonized_promotion_ready_rows=0; decision=candidate_alb2002_sample_de... |

## Interpretation

- The official Basic Information document is saved locally and its text is extracted for reproducible checks.
- The documentation supports the 450 PSU by 8 household sample-design frame and the 3,599 final household sample size.
- Local readable weights and the temp household-core candidate concord with the 3,599 final household count and 450 PSU structure.
- This resolves a narrow sample-design documentation gap only. It does not promote final weighted inference because weight-use rules, variance handling, outcome construction, denominator decisions, and climate geography are still gated separately.

## Machine-Readable Outputs

- `temp/alb2002_sample_design_documentation_audit.csv`
- `result/alb2002_sample_design_documentation_summary.csv`
- `temp/source_snapshots/alb2002_basic_information_document_sample_design.pdf`
- `temp/source_snapshots/alb2002_basic_information_document_sample_design.txt`
