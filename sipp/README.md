# SIPP Adult Insurance Policy Workspace

This is a GitHub-readable export of the local SIPP 2018-2024 workspace used for
adult health-insurance policy idea screening. It is intended for review by GPT
or collaborators without committing raw Census downloads or analysis-ready
microdata.

## Current Lead

The main active idea is:

`ARPA 400% FPL subsidy-cliff removal`

The strongest current specification is a conditional-go
difference-in-discontinuities design around the ACA Marketplace 400% FPL
premium-tax-credit threshold, using SIPP person-month data for reference years
2017-2023. Key files:

- `report/88_arpa_400fpl_source_literature_gap_memo.md`
- `report/90_arpa_400fpl_specification_lock_and_identification_memo.md`
- `report/92_arpa_400fpl_paper_section_draft.md`
- `report/94_README_FOR_WEB_GPT_ARPA400.md`
- `result/idea_scan/arpa400_manuscript_package/README.md`
- `result/idea_scan/arpa400_manuscript_package/table2_primary_estimates.md`
- `result/idea_scan/arpa400_manuscript_package/table3_mechanism_decomposition.md`
- `result/idea_scan/arpa400_manuscript_package/table4_robustness_summary.md`
- `result/idea_scan/arpa400_manuscript_package/table5_placebo_falsification.md`

## Included

- `report/`: project memos, idea-screen decisions, gap memos, specification
  locks, and manuscript-section drafts.
- `script/`: rebuild and screening scripts, excluding Python caches.
- `result/`: lightweight result tables, figures, JSON manifests, and markdown
  exports. Row-level panel outputs are excluded.
- `data_metadata/metadata/`: variable registry and year-availability files.
- `data_metadata/policy/`: lightweight policy files used in screening.
- `data_metadata/sample_audits/`: sample build and missingness audit files.
- `data_metadata/local_file_inventory.csv`: full local SIPP file inventory with
  GitHub inclusion status.
- `data_metadata/excluded_file_inventory.csv`: excluded raw, panel, temporary,
  and large artifact inventory.

## Excluded

Large and rebuildable files are intentionally not committed:

- Census SIPP raw ZIP downloads.
- Analysis-ready Parquet person-month and transition panels.
- Scratch Parquet files and intermediate panels.
- Row-level panel CSV outputs.
- Raw web snapshots, HTML files, Python caches, logs, and process IDs.

The excluded files remain local in the source workspace and are documented in
`data_metadata/excluded_file_inventory.csv`.
