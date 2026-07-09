# Priority Raw Intake Handoff: ETH_2018_ESS_v04_M

This folder is reserved for the complete original raw package and documentation
for `Ethiopia` `2018-2019`. Keep source archive
and file names unchanged.

Official access URL: https://microdata.worldbank.org/catalog/3823/get-microdata

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
| 1 | sect8_3_ls_w4.dta | geography;health_expenditure;health_need_access;shocks;survey_design | blocked_missing_raw_file | inspect raw schema and verify units, labels, missing codes, recall periods, levels, and merge keys before harmonization |
| 2 | sect10c_hh_w4.dta | demographics;geography;shocks;survey_design | blocked_missing_raw_file | inspect raw schema and verify units, labels, missing codes, recall periods, levels, and merge keys before harmonization |
| 3 | sect11_ph_w4.dta | geography;health_need_access;shocks;survey_design | blocked_missing_raw_file | inspect raw schema and verify units, labels, missing codes, recall periods, levels, and merge keys before harmonization |
| 4 | sect04_com_w4.dta | demographics;geography;health_need_access;shocks;survey_design | blocked_missing_raw_file | inspect raw schema and verify units, labels, missing codes, recall periods, levels, and merge keys before harmonization |
| 5 | sect06_com_w4.dta | geography;health_need_access;shocks;survey_design | blocked_missing_raw_file | inspect raw schema and verify units, labels, missing codes, recall periods, levels, and merge keys before harmonization |
| 6 | sect3_pp_w4.dta | geography;shocks;survey_design | blocked_missing_raw_file | inspect raw schema and verify units, labels, missing codes, recall periods, levels, and merge keys before harmonization |
| 7 | sect5b2_hh_w4.dta | demographics;geography;survey_design | blocked_missing_raw_file | inspect raw schema and verify units, labels, missing codes, recall periods, levels, and merge keys before harmonization |
| 8 | sect4_pp_w4.dta | geography;shocks;survey_design | blocked_missing_raw_file | inspect raw schema and verify units, labels, missing codes, recall periods, levels, and merge keys before harmonization |
| 9 | sect3_hh_w4.dta | demographics;geography;health_expenditure;health_need_access;survey_design | blocked_missing_raw_file | inspect raw schema and verify units, labels, missing codes, recall periods, levels, and merge keys before harmonization |
| 10 | sect8_2_ls_w4.dta | consumption;geography;health_need_access;shocks;survey_design | blocked_missing_raw_file | inspect raw schema and verify units, labels, missing codes, recall periods, levels, and merge keys before harmonization |
| 11 | sect9_ph_w4.dta | geography;shocks;survey_design | blocked_missing_raw_file | inspect raw schema and verify units, labels, missing codes, recall periods, levels, and merge keys before harmonization |
| 12 | sect8_4_ls_w4.dta | geography;shocks;survey_design | blocked_missing_raw_file | inspect raw schema and verify units, labels, missing codes, recall periods, levels, and merge keys before harmonization |

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
