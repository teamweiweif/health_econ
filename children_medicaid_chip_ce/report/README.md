# Children Medicaid/CHIP Continuous Eligibility Project

This workspace builds an audit-ready public-data empirical project on the January 1, 2024 federal mandate requiring 12-month continuous eligibility for children under age 19 in Medicaid and CHIP.

## Reproduce

From the project root:

```powershell
powershell -ExecutionPolicy Bypass -File script/run_all.ps1
```

On Unix-like shells:

```bash
bash script/run_all.sh
```

Or run the verified Python sequence directly:

```powershell
python script/00_setup.py
python script/01_acquire_sources.py
python script/02_build_policy_panel.py
python script/03_build_enrollment_panel.py
python script/04_build_renewal_mechanism_panel.py
python script/05_build_acs_validation_panel.py
python script/06_construct_designs_and_outcomes.py
python script/07_descriptive_diagnostics.py
python script/08_main_models.py
python script/09_robustness_and_falsification.py
python script/10_write_report.py
```

Clean analysis files are in `data/`, model and diagnostic outputs are in `result/`, and source/audit logs are in `temp/`.
