$ErrorActionPreference = "Stop"
$root = Split-Path -Parent $MyInvocation.MyCommand.Path
$scripts = Join-Path $root "script"
$env:PYTHONUTF8 = "1"

python (Join-Path $scripts "10_source_algorithm_audit.py")
python (Join-Path $scripts "11_rating_algorithm_emulator.py")
python (Join-Path $scripts "12_construct_reliability_outcomes.py")
python (Join-Path $scripts "13_construct_threshold_running_variables.py")
python (Join-Path $scripts "14_rd_threshold_models.py")
python (Join-Path $scripts "15_rd_did_models.py")
python (Join-Path $scripts "16_formula_label_shock_models.py")
python (Join-Path $scripts "17_metric_salience_ddd.py")
python (Join-Path $scripts "18_shadow_price_bunching.py")
python (Join-Path $scripts "19_2018_validation_event.py")
python (Join-Path $scripts "20_design_scorecard.py")
python (Join-Path $scripts "21_write_breakthrough_report.py")
python (Join-Path $scripts "22_self_test.py")
