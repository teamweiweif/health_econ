# Priority Manual Verification Decision Gate: TZA_2010_NPS-R2_v03_M

Status: `blocked_raw_module_coverage_missing`

Financial-protection manual ready: `0`

Double-failure manual ready: `0`

Analysis-ready candidate: `0`

Remaining blockers: priority direct/archive raw module coverage incomplete; manual requirement verification incomplete; manual financial concept verification incomplete; manual double-failure concept verification incomplete; manual survey-design/timing/geography concept verification incomplete; no selected raw variables manually verified; accepted CHIRPS/ERA5 route absent

## Evidence Counts

- requirements passed: 0 / 8
- concepts passed: 0 / 13
- variables passed: 0 / 91
- raw module targets covered: 0 / 12
- accepted CHIRPS/ERA5 route: `not_accepted_raw_timing_geography_unverified`

## Rule

This wave cannot be promoted until source gates are ready and all required
`fill_*` evidence columns are raw-backed and passing. A manual pass never
overrides missing raw package, missing schema, incomplete value checks, or
unaccepted climate linkage.
