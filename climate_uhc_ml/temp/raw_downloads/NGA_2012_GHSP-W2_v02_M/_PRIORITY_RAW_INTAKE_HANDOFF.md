# Priority Raw Intake Handoff: NGA_2012_GHSP-W2_v02_M

This folder is reserved for the complete original raw package and documentation
for `Nigeria` `2012-2013`. Keep source archive
and file names unchanged.

Official access URL: https://microdata.worldbank.org/catalog/1952/get-microdata

Current gate status: `blocked_manual_raw_package_required`

Next action: Complete official login/register/terms workflow, download the complete original raw package plus documentation, and place unchanged files in the target folder.

## Required Promotion Gates

- Complete original raw package is present in this folder.
- Household/person merge keys are verified from raw values.
- Household weights, strata, PSU/cluster, and survey design are verified.
- Consumption or income denominator is verified.
- OOP health expenditure values, units, recall periods, and missing codes are verified.
- Illness/need and care-seeking/access variables are verified where available.
- Survey timing and geography are verified for climate linkage.
- CHIRPS or ERA5 route is accepted before writing to `data/`.

## Priority Files To Inspect First

| file_rank | file_name | candidate_categories | current_file_gate_status | verification_action |
|---|---|---|---|---|
| 1 | secta1_harvestw2 | geography;shocks;survey_design | blocked_missing_raw_file | inspect raw schema and verify units, labels, missing codes, recall periods, levels, and merge keys before harmonization |
| 2 | sect11b1_plantingw2 | geography;shocks;survey_design | blocked_missing_raw_file | inspect raw schema and verify units, labels, missing codes, recall periods, levels, and merge keys before harmonization |
| 3 | sect11h_plantingw2 | geography;health_need_access;shocks;survey_design | blocked_missing_raw_file | inspect raw schema and verify units, labels, missing codes, recall periods, levels, and merge keys before harmonization |
| 4 | sect4a_harvestw2 | demographics;geography;health_expenditure;health_need_access;survey_design | blocked_missing_raw_file | inspect raw schema and verify units, labels, missing codes, recall periods, levels, and merge keys before harmonization |
| 5 | secta3_harvestw2 | geography;health_need_access;shocks;survey_design | blocked_missing_raw_file | inspect raw schema and verify units, labels, missing codes, recall periods, levels, and merge keys before harmonization |
| 6 | sect11d_plantingw2 | geography;health_need_access;shocks;survey_design | blocked_missing_raw_file | inspect raw schema and verify units, labels, missing codes, recall periods, levels, and merge keys before harmonization |
| 7 | sect9_harvestw2 | demographics;geography;health_need_access;shocks;survey_design | blocked_missing_raw_file | inspect raw schema and verify units, labels, missing codes, recall periods, levels, and merge keys before harmonization |
| 8 | sect11e_plantingw2 | geography;health_need_access;shocks;survey_design | blocked_missing_raw_file | inspect raw schema and verify units, labels, missing codes, recall periods, levels, and merge keys before harmonization |
| 9 | secta2_harvestw2 | geography;shocks;survey_design | blocked_missing_raw_file | inspect raw schema and verify units, labels, missing codes, recall periods, levels, and merge keys before harmonization |
| 10 | sect6_plantingw2 | demographics;geography;health_need_access;shocks;survey_design | blocked_missing_raw_file | inspect raw schema and verify units, labels, missing codes, recall periods, levels, and merge keys before harmonization |
| 11 | NGA_HouseholdGeovars_Y2 | geography;health_need_access;shocks;survey_design | blocked_missing_raw_file | inspect raw schema and verify units, labels, missing codes, recall periods, levels, and merge keys before harmonization |
| 12 | sect8_harvestw2 | demographics;geography;survey_design | blocked_missing_raw_file | inspect raw schema and verify units, labels, missing codes, recall periods, levels, and merge keys before harmonization |

## Post-Download Commands

```powershell
python script/17_audit_raw_downloads.py
python script/03_inspect_raw_schemas.py
python script/29_build_raw_variable_verification_protocol.py
python script/33_build_harmonization_recipe_gate.py
python script/121_build_country_wave_promotion_registry.py
python script/122_build_priority_promotion_acquisition_plan.py
python script/123_probe_priority_official_raw_access.py
python script/124_build_priority_raw_intake_gate.py
python script/36_build_direct_read_audit_bundle.py
python script/14_validate_workspace.py
```
