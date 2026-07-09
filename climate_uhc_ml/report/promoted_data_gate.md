# Promoted Data Gate

Status: fail-closed guard for `data/`.

The active objective allows country-waves into `data/` only after the promotion
registry marks them `promoted_analysis_ready`. Diagnostic Albania files and
other pre-promotion outputs belong in `temp/`, not in `data/`.

## Summary

| Metric | Value | Interpretation |
|---|---:|---|
| registry_promoted_analysis_ready_rows | 0 | Country-waves currently allowed to write promoted datasets into data/. |
| data_dataset_files_before_gate | 4 | Dataset-like files found in data/ before enforcing the gate. |
| data_dataset_files_after_gate | 0 | Dataset-like files left in data/ after enforcing the gate. |
| quarantined_diagnostic_data_files | 4 | Pre-promotion data files preserved under temp/diagnostic_data_quarantine/current/ and removed from data/. |
| current_diagnostic_quarantine_files | 4 | Diagnostic or pre-promotion dataset files currently indexed under temp/diagnostic_data_quarantine/current/. |
| data_readme_written | 1 | Whether data/README.md records the current promoted-data status. |
| promoted_data_gate_status | closed_no_promoted_rows | Current write gate status for promoted data outputs. |

## Data File Actions

| Original path | Action | Quarantine path | Reason |
|---|---|---|---|
| data/climate_exposures_nasa_power.csv | quarantined_to_temp_removed_from_data | temp/diagnostic_data_quarantine/current/climate_exposures_nasa_power.csv | No country-wave currently passes promoted_analysis_ready; data/ must remain reserved for promoted datasets. |
| data/climate_linked_household.csv | quarantined_to_temp_removed_from_data | temp/diagnostic_data_quarantine/current/climate_linked_household.csv | No country-wave currently passes promoted_analysis_ready; data/ must remain reserved for promoted datasets. |
| data/harmonized_household.csv | quarantined_to_temp_removed_from_data | temp/diagnostic_data_quarantine/current/harmonized_household.csv | No country-wave currently passes promoted_analysis_ready; data/ must remain reserved for promoted datasets. |
| data/household_outcomes.csv | quarantined_to_temp_removed_from_data | temp/diagnostic_data_quarantine/current/household_outcomes.csv | No country-wave currently passes promoted_analysis_ready; data/ must remain reserved for promoted datasets. |

## Rule

If `result/promoted_country_wave_registry.csv` has zero promoted rows, this
script removes dataset-like files from `data/` after copying them to
`temp/diagnostic_data_quarantine/current/`. This preserves diagnostic evidence
while preventing provisional outputs from masquerading as promoted datasets.
