# Metadata Audit

Canonical metadata source: `D:\GlobalHealthPolicy Dropbox\Fan Bowei\nh_staffing\sipp\temp\source_metadata\sipp_2018_2024_raw_variable_metadata.enriched.compact.json`

## Summary

- Unique variables in compact metadata: 5,312
- Variable-year rows: 35,836
- Requested/core variables present: 89
- Requested/core variables missing: 0

Missing or substituted variables:

- None.

Important substitutions:

- `TAGE` is present and used for age; `EAGE` is not present.
- `EORIGIN` and, where available, `EHISPAN` are used for Hispanic origin; `ERACEHISP` is not present.
- `ECRMTH` and `RPUBTYPE1` are used for Medicare exclusion.

## Outputs

- `data/metadata/variable_registry.csv`
- `data/metadata/variable_year_availability.csv`
- `data/metadata/concept_crosswalk_initial.csv`

## Initial Construction Decisions

- Medicaid is constructed primarily from `EMDMTH`, with `RPUBTYPE2` retained for agreement and sensitivity.
- Any coverage is constructed from `RHLTHMTH`.
- Direct-purchase/exchange bridge is constructed from `RPRITYPE2`, `RMARKTPLACE`, `EPRIEXCH*`, `EPRISUBS*`, `EMDEXCH`, and `EMDSUBS`.
- Family monthly income-to-poverty (`TFINCPOV`) is the primary running variable; household ratio (`THINCPOV`) and calendar-year ratios are retained for sensitivity.
- Annual recodes such as `RMCAIDANN` and `RDIRECTANN` begin only in 2022 and are not primary monthly measures.
