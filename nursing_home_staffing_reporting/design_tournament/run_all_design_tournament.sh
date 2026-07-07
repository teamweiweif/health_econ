#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SCRIPTS="$ROOT/script"

python "$SCRIPTS/10_source_algorithm_audit.py"
python "$SCRIPTS/11_rating_algorithm_emulator.py"
python "$SCRIPTS/12_construct_reliability_outcomes.py"
python "$SCRIPTS/13_construct_threshold_running_variables.py"
python "$SCRIPTS/14_rd_threshold_models.py"
python "$SCRIPTS/15_rd_did_models.py"
python "$SCRIPTS/16_formula_label_shock_models.py"
python "$SCRIPTS/17_metric_salience_ddd.py"
python "$SCRIPTS/18_shadow_price_bunching.py"
python "$SCRIPTS/19_2018_validation_event.py"
python "$SCRIPTS/20_design_scorecard.py"
python "$SCRIPTS/21_write_breakthrough_report.py"
python "$SCRIPTS/22_self_test.py"
