# Climate UHC ML

This is a GitHub-readable export of the `climate_uhc_ml` audit workspace.

The project tests whether public household microdata can support a multi-country
climate shock, universal health coverage failure, and policy-targeting study.
The current export is intentionally evidence-first: it includes reports, scripts,
machine-readable audits, and the small limited diagnostic datasets, while raw
downloads, extracted archives, web caches, and source snapshots stay local.

## Read First

- `report/final_report.md` - final empirical judgment and go/no-go status.
- `report/direct_read_audit_bundle.md` - compact GPT-readable evidence bundle.
- `result/completion_criteria_audit.csv` - formal 16-item objective completion audit.
- `report/modeling_report.md` - predictive ML, reduced-form, causal ML, and robustness status.
- `metadata/country_wave_screening.csv` - broad country-wave screening table.

## Current Data Status

The original target was a multi-country, multi-wave household microdata by
climate exposure dataset. The current analysis-ready diagnostic data are limited
to Albania 2002 LSMS:

- `data/harmonized_household.csv`
- `data/household_outcomes.csv`
- `data/climate_exposures_nasa_power.csv`
- `data/climate_linked_household.csv`

These files support CHE10/CHE25 financial-protection diagnostics only. They do
not support SDG 3.8.2, deployable prediction, causal climate effects, causal ML,
or policy-learning claims.

## Included

- `report/` - human-readable reports and audits.
- `result/` - machine-readable outputs, model diagnostics, validation, and completion audits.
- `script/` - reusable pipeline scripts.
- `data/` - small current limited diagnostic CSVs.
- `metadata/` - source inventory, country-wave screening, manual-download manifest, and variable maps.
- `data_metadata/` - generated GitHub-readable metadata for the included data files.

## Excluded

- raw downloaded archives;
- extracted raw files;
- Stata/SPSS/SAS files;
- web snapshots and API caches;
- temporary scratch files.

Those exclusions are deliberate so this repository remains readable by GitHub
and Web GPT connectors without shipping raw or bulky data.
