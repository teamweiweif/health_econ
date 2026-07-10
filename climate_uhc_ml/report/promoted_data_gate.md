# Promoted Data Gate

Status: fail-closed guard for `data/`.

The active objective allows country-waves into `data/` only after the promotion
registry marks them `promoted_analysis_ready`. Diagnostic Albania files and
other pre-promotion outputs belong in `temp/`, not in `data/`.

## Summary

| Metric | Value | Interpretation |
|---|---:|---|
| registry_promoted_analysis_ready_rows | 1 | Country-waves currently allowed to write promoted datasets into data/. |
| data_dataset_files_before_gate | 1 | Dataset-like files found in data/ before enforcing the gate. |
| data_dataset_files_after_gate | 1 | Dataset-like files left in data/ after enforcing the gate. |
| quarantined_diagnostic_data_files | 0 | Pre-promotion data files preserved under temp/diagnostic_data_quarantine/current/ and removed from data/. |
| current_diagnostic_quarantine_files | 4 | Diagnostic or pre-promotion dataset files currently indexed under temp/diagnostic_data_quarantine/current/. |
| data_readme_written | 1 | Whether data/README.md records the current promoted-data status. |
| promoted_data_gate_status | open_registry_has_promoted_rows | Current write gate status for promoted data outputs. |

## Data File Actions

| Original path | Action | Quarantine path | Reason |
|---|---|---|---|
| data/mwi2004_household_climate_analysis.csv | kept_registry_has_promoted_rows |  | Registry has promoted rows; downstream promoted-data builder must maintain file-level lineage. |
| data/climate_exposures_nasa_power.csv | already_quarantined | temp/diagnostic_data_quarantine/current/climate_exposures_nasa_power.csv | Diagnostic or pre-promotion dataset file is preserved in temp/ and not present in data/. |
| data/climate_linked_household.csv | already_quarantined | temp/diagnostic_data_quarantine/current/climate_linked_household.csv | Diagnostic or pre-promotion dataset file is preserved in temp/ and not present in data/. |
| data/harmonized_household.csv | already_quarantined | temp/diagnostic_data_quarantine/current/harmonized_household.csv | Diagnostic or pre-promotion dataset file is preserved in temp/ and not present in data/. |
| data/household_outcomes.csv | already_quarantined | temp/diagnostic_data_quarantine/current/household_outcomes.csv | Diagnostic or pre-promotion dataset file is preserved in temp/ and not present in data/. |

## Rule

If `result/promoted_country_wave_registry.csv` has zero promoted rows, this
script removes dataset-like files from `data/` after copying them to
`temp/diagnostic_data_quarantine/current/`. This preserves diagnostic evidence
while preventing provisional outputs from masquerading as promoted datasets.
