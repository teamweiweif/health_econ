# SIPP Adult Medicaid Boundary Project

## Objective

Build a reproducible empirical audit of whether temporary income eligibility-risk crossings near the adult Medicaid expansion boundary translate into Medicaid-to-uninsured transitions in SIPP 2017-2023, and whether administrative smoothing during the PHE muted that link.

## Local Paths

- `LOCAL_SIPP_RAW_DATA_DIR`: `D:\GlobalHealthPolicy Dropbox\Fan Bowei\nh_staffing\sipp\temp\raw_downloads\census_sipp`
- `LOCAL_SIPP_METADATA_JSON`: `D:\GlobalHealthPolicy Dropbox\Fan Bowei\nh_staffing\sipp\temp\source_metadata\sipp_2018_2024_raw_variable_metadata.enriched.compact.json`
- `LOCAL_PRIOR_SOURCE_DIR`: `D:\GlobalHealthPolicy Dropbox\Fan Bowei\US Insurance Project`
- `LOCAL_CHAT_EXPORT_OR_NOTES`: `C:\Users\admin\.codex\attachments\3657460f-baf5-436a-8680-f6d6b587838e\pasted-text-1.txt`
- `WORKSPACE_ROOT`: `D:\GlobalHealthPolicy Dropbox\Fan Bowei\nh_staffing\sipp`

## Execution Order

Run from this directory:

```powershell
python script/run_pipeline.py
```

Phase-specific scripts are stored under `script/00_setup` through `script/10_reporting`; they call the shared implementation in `script/pipeline_lib.py`.

## Dependencies

Required Python packages detected or used: `pandas`, `numpy`, `pyarrow`, `matplotlib`, `sklearn`, `openpyxl`.
`statsmodels` is not available in the current environment, so transparent weighted linear probability models with robust standard errors are implemented directly with `numpy`.

## Storage Boundary

Raw Census zips remain in `temp/raw_downloads/`. Yearly selected extracts are written to `temp/scratch/`. Clean analysis-ready files are written under `data/analysis_ready/`; reports and model summaries are written under `report/` and `result/`.
