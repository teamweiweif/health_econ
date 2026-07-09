# Climate UHC ML

This workspace studies whether climate shocks increase household-level universal health coverage (UHC) failure through financial hardship, forgone care, or both, and whether predictive or causal machine learning improves post-shock policy targeting.

Run the current reproducible pipeline from the project root:

```powershell
powershell -ExecutionPolicy Bypass -File script/run_all.ps1
```

On systems with GNU Make:

```bash
make all
```

Equivalent script sequence if neither runner is convenient:

```bash
python script/00_setup.py
python script/01_verify_sources.py
python script/01_inventory_surveys.py
python script/02_acquire_microdata.py
python script/02_probe_external_repositories.py
python script/03_inspect_raw_schemas.py
python script/04_build_household_panel.py
python script/05_construct_outcomes.py
python script/06_extract_climate.py
python script/07_merge_microdata_climate.py
python script/08_descriptive_diagnostics.py
python script/09_predictive_ml.py
python script/10_causal_models.py
python script/11_causal_ml_policy_learning.py
python script/12_robustness.py
python script/13_write_reports.py
python script/14_validate_workspace.py
python script/15_prepare_manual_request_packet.py
```

Raw files are not stored in `data/`. Direct downloads and source snapshots belong in `temp/`; analysis-ready datasets belong in `data/`.

Current status:

- Official UHC and climate-health anchors are verified in `report/source_audit.md`.
- World Bank Microdata Library screening is saved in `temp/country_wave_screening.csv`.
- Public metadata/documentation for priority studies is saved under `temp/raw_schema_inventory/`.
- Raw microdata downloads are not complete because priority World Bank studies require login or Data Access Agreement steps; see `temp/manual_download_manifest.csv` and the ranked queue in `temp/manual_download_priority.csv`.
- The manual raw-data handoff is summarized in `report/manual_data_access_guide.md`; the module-level checklist is `temp/manual_download_file_checklist.csv`.
- Long metadata acquisition runs checkpoint to `temp/acquisition_progress.csv` after each priority study. If acquisition is interrupted, rerun `python script/03_inspect_raw_schemas.py` and `python script/13_write_reports.py` to rebuild maps and reports from saved schema files.
- Direct-public external repository candidates are probed in `temp/external_repository_probe.csv`; the probe does not bypass login, registration, or terms gates.
- The objective-level validator writes `result/workspace_validation_audit.csv` and `report/workspace_validation.md`.
- The manual request packet writes `report/raw_data_request_packet.md`, `temp/manual_access_action_queue.csv`, and an updated `temp/raw_downloads/README.md`.
- Put manual raw files in `temp/raw_downloads/`, then rerun `make all` to refresh raw schema inspection, harmonization gates, outcome construction, climate linkage, diagnostics, modeling gates, robustness gates, and reports.
- Create `temp/harmonization_recipe.csv` from `temp/harmonization_recipe_template.csv` after raw schema inspection. The project will not write `data/harmonized_household.csv` without verified raw files and explicit raw-to-harmonized mappings.
