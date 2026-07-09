# Priority Raw Intake Handoff: KGZ_1993_KMPS_v01_M

This folder is reserved for the complete original raw package and documentation
for `Kyrgyz Republic` `1993`. Keep source archive
and file names unchanged.

Official access URL: https://microdata.worldbank.org/catalog/280/get-microdata

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
| 1 | KPRICE2 | geography;shocks | blocked_missing_raw_file | inspect raw schema and verify units, labels, missing codes, recall periods, levels, and merge keys before harmonization |
| 2 | KHHLD | demographics;geography;health_expenditure;health_need_access;shocks;survey_design | blocked_missing_raw_file | inspect raw schema and verify units, labels, missing codes, recall periods, levels, and merge keys before harmonization |
| 3 | KPRICE3 | geography;shocks | blocked_missing_raw_file | inspect raw schema and verify units, labels, missing codes, recall periods, levels, and merge keys before harmonization |
| 4 | KADULT | consumption;demographics;geography;health_expenditure;health_need_access;shocks;survey_design | blocked_missing_raw_file | inspect raw schema and verify units, labels, missing codes, recall periods, levels, and merge keys before harmonization |
| 5 | KCOMM | demographics;geography;health_need_access;shocks | blocked_missing_raw_file | inspect raw schema and verify units, labels, missing codes, recall periods, levels, and merge keys before harmonization |
| 6 | KCHILD | demographics;health_expenditure;health_need_access;shocks;survey_design | blocked_missing_raw_file | inspect raw schema and verify units, labels, missing codes, recall periods, levels, and merge keys before harmonization |
| 7 | KINDIVH | demographics;survey_design | blocked_missing_raw_file | inspect raw schema and verify units, labels, missing codes, recall periods, levels, and merge keys before harmonization |
| 8 | INCEXP | consumption;demographics;geography;health_need_access;shocks;survey_design | blocked_missing_raw_file | inspect raw schema and verify units, labels, missing codes, recall periods, levels, and merge keys before harmonization |
| 9 | KYGPOV | geography;survey_design | blocked_missing_raw_file | inspect raw schema and verify units, labels, missing codes, recall periods, levels, and merge keys before harmonization |
| 10 | CONADULT | demographics;survey_design | blocked_missing_raw_file | inspect raw schema and verify units, labels, missing codes, recall periods, levels, and merge keys before harmonization |
| 11 | KINDIV | demographics;survey_design | blocked_missing_raw_file | inspect raw schema and verify units, labels, missing codes, recall periods, levels, and merge keys before harmonization |
| 12 | CORE | geography;survey_design | blocked_missing_raw_file | inspect raw schema and verify units, labels, missing codes, recall periods, levels, and merge keys before harmonization |

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
