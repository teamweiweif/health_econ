# SIPP Data Metadata

This folder is the GitHub-readable data layer for the local SIPP workspace.
It does not contain raw Census microdata or analysis-ready person-month panels.

Included files:

- `metadata/variable_registry.csv`: curated variable registry.
- `metadata/variable_year_availability.csv`: variable availability across SIPP
  years.
- `metadata/concept_crosswalk_initial.csv`: initial concept-to-variable
  crosswalk.
- `metadata/sipp_release_version_ledger_2018_2025.csv`: current release
  versions and official correction provenance.
- `metadata/sipp_weight_product_use_ledger.csv`: estimand-specific point and
  replicate weight selection.
- `metadata/sipp_2025_response_and_attrition_summary.csv`: official current
  response and longitudinal attrition rates.
- `policy/`: lightweight policy files used in screening.
- `sample_audits/`: sample construction, current-remote byte comparisons,
  panel alignment, issue register, and final 15/15 re-audit checks.
- `local_file_inventory.csv`: full local file inventory with inclusion status
  and GitHub destination paths for published files.
- `excluded_file_inventory.csv`: local files excluded from GitHub, sorted by
  size when generated.

Publication boundary:

- Included: reports, scripts, aggregate results, figures, policy CSVs, and
  metadata.
- Excluded: raw downloads, Parquet panels, row-level panel CSVs, scratch
  artifacts, archives, HTML snapshots, logs, and caches.
