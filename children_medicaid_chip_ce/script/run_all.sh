#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
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
