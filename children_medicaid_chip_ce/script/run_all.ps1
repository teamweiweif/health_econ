$ErrorActionPreference = "Stop"

$scripts = @(
    "00_setup.py",
    "01_acquire_sources.py",
    "02_build_policy_panel.py",
    "03_build_enrollment_panel.py",
    "04_build_renewal_mechanism_panel.py",
    "05_build_acs_validation_panel.py",
    "06_construct_designs_and_outcomes.py",
    "07_descriptive_diagnostics.py",
    "08_main_models.py",
    "09_robustness_and_falsification.py",
    "10_write_report.py"
)

foreach ($script in $scripts) {
    Write-Host "RUN $script"
    python ".\script\$script"
}
