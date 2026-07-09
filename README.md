# Health Economics Project Workspace

This repository contains public-data health economics project workspaces.
Each project is kept as a separate top-level folder with scripts, reports,
lightweight outputs, and a GitHub-friendly data metadata layer.

## Projects

| Folder | Topic | Current empirical status |
| --- | --- | --- |
| `988_telecom_fee_crisis_performance/` | State 988 telecom fee funding and crisis-line performance | Conditional go for exploratory policy-audit evidence |
| `ccbhc_expansion_capacity/` | 2024 CCBHC Medicaid Demonstration expansion and behavioral-health capacity | Monitoring package; no-go for a current causal paper |
| `nursing_home_staffing_reporting/` | CMS 2022 nursing-home staffing transparency and Five-Star rating changes | Large staffing panel; weak current causal design because pretrends/placebo fail |
| `climate_uhc_ml/` | Climate shocks, UHC financial protection, and diagnostic ML targeting feasibility | Objective audit workspace complete; empirical manuscript claims remain fail-closed |

## Data Policy

Large raw downloads, intermediate panels, Parquet files, ZIP archives, and other
rebuildable heavy artifacts are not committed. Instead, each project has a
`data_metadata/` folder that lets GitHub readers inspect the local data layer
without cloning bulky files.

Each `data_metadata/` folder contains:

- `dataset_inventory.csv`: file-level format, size, row count where available,
  column count, and profiling status.
- `variable_catalog.csv`: variable-level dtype, missingness, uniqueness, numeric
  summaries when applicable, and the most common observed value.
- `categorical_top_values.csv`: top observed values for each variable in the
  profiled rows.
- `file_manifest_sha256.csv`, where available: local download audit for source
  files, including omitted large files, with size, read status, and SHA-256 hash.
- `README.md`: generation notes for the metadata profile.

The full local download audit summary is stored in
`download_audit_summary.csv`. At the time of the original three-project push all
422 source files across those local project folders were readable with zero read
errors. Newer project folders may carry their own source inventories and direct
read audit bundles.

## Refreshing Metadata

Use `tools/build_data_metadata.py` after rebuilding local data:

```powershell
python tools\build_data_metadata.py `
  --project-name nursing_home_staffing_reporting `
  --source-root "D:\GlobalHealthPolicy Dropbox\Fan Bowei\nh_staffing\nursing_home_staffing_reporting" `
  --output-root "nursing_home_staffing_reporting\data_metadata"
```
