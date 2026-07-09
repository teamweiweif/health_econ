# ALB_2002 Consumption Construction Source Audit

Status: public-source documentation audit for the ALB_2002 total-consumption aggregate. This report does not write `data/`, does not construct CHE or SDG outcomes, and does not promote climate-linked analysis.

## Bottom Line

- IHSN related materials list a public PDF titled `Construction of the Consumption Aggregate and Estimation of the Poverty Line`.
- IHSN related materials also list a public Stata program ZIP; the extracted package contains 19 `.do` files, including `totcons.do`, `poverty.do`, and `overall.do`.
- The public metadata JSON identifies `totcons3` in file `poverty` as `with durables and without rent and health`.
- Local `Poverty_2002.sav` column `totcons` matches public metadata `totcons3` on row count, minimum, and maximum, so the prior denominator evidence is now documented as the final poverty total-budget variant.
- This resolves the narrow official aggregate-documentation blocker, but it does not resolve OOP numerator policy, SDG 3.8.2 SPL/PPP/CPI/discretionary-budget construction, benchmark validation, or climate linkage.
- Current decision: `documented_alb2002_consumption_aggregate_but_not_outcome_sdg_climate_ready`.

## Summary

| Metric | Value | Interpretation |
|---|---:|---|
| alb2002_consumption_construction_source_audit_rows | 9 | Rows in the ALB_2002 public consumption-construction source audit. |
| alb2002_consumption_construction_public_pdf_present | 1 | Public IHSN consumption aggregate and poverty-line PDF downloaded. |
| alb2002_consumption_construction_program_zip_present | 1 | Public IHSN Stata program ZIP downloaded. |
| alb2002_consumption_construction_do_file_rows | 19 | Extracted Stata do-files in the public consumption program package. |
| alb2002_consumption_construction_totcons_do_present | 1 | Whether totcons.do is present in the extracted program package. |
| alb2002_consumption_construction_poverty_do_present | 1 | Whether poverty.do is present in the extracted program package. |
| alb2002_consumption_construction_metadata_json_present | 1 | Public IHSN metadata JSON downloaded. |
| alb2002_consumption_construction_documentation_ready_rows | 9 | Audit rows with accepted public documentation evidence. |
| alb2002_consumption_construction_released_variable_mapping_ready_rows | 3 | Audit rows supporting the mapping from local `totcons` to public metadata `totcons3`. |
| alb2002_consumption_construction_denominator_variant_ready_rows | 8 | Audit rows documenting the final total-budget denominator variant. |
| alb2002_consumption_construction_recipe_ready_rows | 0 | Rows promoted to a full harmonization recipe by this source audit; intentionally zero. |
| alb2002_consumption_construction_outcome_ready_rows | 0 | Rows promoted to outcome construction by this source audit; intentionally zero. |
| alb2002_consumption_construction_sdg382_ready_rows | 0 | Rows promoted to SDG 3.8.2 construction by this source audit; intentionally zero. |
| alb2002_consumption_construction_climate_linkage_ready_rows | 0 | Rows promoted to climate linkage by this source audit; intentionally zero. |
| alb2002_consumption_construction_current_decision | documented_alb2002_consumption_aggregate_but_not_outcome_sdg_climate_ready | Current decision for ALB_2002 public consumption aggregate construction evidence. |

## Evidence Rows

| audit_family | evidence_item | row_count | evidence_status | documentation_ready | released_variable_mapping_ready | denominator_variant_ready |
|---|---|---|---|---|---|---|
| public_catalog_evidence | ihsn_related_materials_lists_consumption_pdf_and_program_zip | 1 | source_page_downloaded | 1 | 0 | 0 |
| official_method_pdf | consumption_aggregate_and_poverty_line_pdf | 1 | official_method_pdf_downloaded | 1 | 0 | 1 |
| official_program_files | consumption_stata_program_zip | 19 | official_program_zip_downloaded_and_extracted | 1 | 0 | 1 |
| code_sequence | overall_do_runs_consumption_pipeline_sequence | 1 | pipeline_sequence_seen | 1 | 0 | 1 |
| code_formula | totcons_do_defines_denominator_variants | 4 | denominator_variants_defined | 1 | 0 | 1 |
| code_formula | poverty_do_uses_rpcons3_for_poverty_estimates | 1 | final_poverty_denominator_variant_seen | 1 | 0 | 1 |
| public_metadata_json | metadata_json_totcons3_label | 1 | public_metadata_variable_seen | 1 | 1 | 1 |
| released_spSS_mapping | local_totcons_matches_public_metadata_totcons3_stats | 3599 | local_totcons_matches_totcons3_metadata | 1 | 1 | 1 |
| policy_boundary | health_and_rent_exclusion_denominator_policy | 1 | health_rent_exclusion_documented | 1 | 1 | 1 |

## Source Files

- `D:/GlobalHealthPolicy Dropbox/Fan Bowei/nh_staffing/climate_uhc_ml/temp/source_snapshots/alb2002_consumption_construction/ihsn_alb2002_related_materials.html`
- `D:/GlobalHealthPolicy Dropbox/Fan Bowei/nh_staffing/climate_uhc_ml/temp/source_snapshots/alb2002_consumption_construction/ihsn_alb2002_consumption_aggregate_poverty_line.pdf`
- `D:/GlobalHealthPolicy Dropbox/Fan Bowei/nh_staffing/climate_uhc_ml/temp/source_snapshots/alb2002_consumption_construction/ihsn_alb2002_consumption_aggregate_poverty_line.txt`
- `D:/GlobalHealthPolicy Dropbox/Fan Bowei/nh_staffing/climate_uhc_ml/temp/source_snapshots/alb2002_consumption_construction/ihsn_alb2002_consumption_program_files.zip`
- `D:/GlobalHealthPolicy Dropbox/Fan Bowei/nh_staffing/climate_uhc_ml/temp/source_snapshots/alb2002_consumption_construction/program_files`
- `D:/GlobalHealthPolicy Dropbox/Fan Bowei/nh_staffing/climate_uhc_ml/temp/source_snapshots/alb2002_consumption_construction/ihsn_alb2002_metadata.json`

## Interpretation

The denominator gate should no longer say no official ALB_2002 consumption-construction source was found. The correct narrower statement is that official source evidence supports local `totcons` as the public metadata `totcons3` variant, with durables and without rent and health. Promotion still remains blocked because this source audit does not define the accepted health OOP numerator, SDG societal poverty line, PPP/CPI conversion, discretionary budget, geography, or climate exposure.
