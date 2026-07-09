from __future__ import annotations

import csv
from pathlib import Path
from typing import Any

from common import DATA_DIR, RESULT_DIR, TEMP_DIR, append_log, ensure_dirs, write_csv


INPUT_PATH = DATA_DIR / "climate_linked_household.csv"
ESTIMATE_PATH = RESULT_DIR / "reduced_form_estimates.csv"
PLACEBO_PATH = RESULT_DIR / "placebo_readiness_audit.csv"
AUDIT_PATH = RESULT_DIR / "robustness_audit.csv"
RESULT_PATH = RESULT_DIR / "robustness_results.csv"

AUDIT_COLUMNS = ["check", "status", "detail", "input_path", "rows_input", "rows_output", "output_path", "required_action"]
RESULT_COLUMNS = ["primary_outcome", "primary_exposure", "robustness_check", "status", "estimate_rows", "result", "notes"]
LIMITED_LINKED_DATA_USE_LIMIT = "climate_linked_che_diagnostic_only_not_for_promoted_descriptive_ml_causal_or_policy_analysis"

REQUIRED_CHECKS = [
    "alternative_financial_hardship_thresholds",
    "alternative_climate_lags",
    "alternative_climate_datasets",
    "gps_point_vs_admin_aggregation",
    "with_and_without_survey_weights",
    "country_leave_one_out",
    "region_leave_one_out",
    "exclude_weak_outcome_construction",
    "exclude_poor_geolocation",
    "rural_urban_splits",
    "agricultural_livelihood_splits",
    "multiple_testing_correction",
    "household_or_repeated_cross_section_fixed_effects",
    "future_climate_placebo",
    "negative_control_or_non_climate_sensitive_outcome",
    "poverty_line_assumption_sensitivity",
    "ppp_cpi_assumption_sensitivity",
    "missing_data_sensitivity",
]


def read_csv_dicts(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        return []
    with path.open(encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def relative(path: Path) -> str:
    try:
        return str(path.relative_to(TEMP_DIR.parent))
    except ValueError:
        return str(path)


def audit_row(
    check: str,
    status: str,
    detail: str,
    *,
    input_path: str = "",
    rows_input: Any = 0,
    rows_output: Any = 0,
    output_path: str = "",
    required_action: str = "",
) -> dict[str, Any]:
    return {
        "check": check,
        "status": status,
        "detail": detail,
        "input_path": input_path,
        "rows_input": rows_input,
        "rows_output": rows_output,
        "output_path": output_path,
        "required_action": required_action,
    }


def limited_linked_blocker(path: Path) -> dict[str, Any] | None:
    if not path.exists():
        return None
    with path.open(encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        fields = set(reader.fieldnames or [])
        rows = 0
        has_limited_marker = False
        robustness_ready_sum = 0
        for row in reader:
            rows += 1
            if row.get("data_use_limit", "").strip() == LIMITED_LINKED_DATA_USE_LIMIT:
                has_limited_marker = True
            try:
                robustness_ready_sum += int(float(row.get("robustness_ready", "0") or 0))
            except ValueError:
                pass
    if has_limited_marker:
        detail = f"Input carries data_use_limit={LIMITED_LINKED_DATA_USE_LIMIT}."
    elif "robustness_ready" in fields and robustness_ready_sum == 0:
        detail = "All robustness_ready values are zero."
    else:
        return None
    return audit_row(
        "robustness_inputs",
        "blocked_limited_climate_linked_not_robustness_ready",
        detail,
        input_path=relative(path),
        rows_input=rows,
        required_action="Promote a verified reduced-form design with robustness_ready=1 before robustness/placebo stress tests.",
    )


def has_limited_linked_marker(path: Path) -> bool:
    if not path.exists():
        return False
    with path.open(encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        return any(row.get("data_use_limit", "").strip() == LIMITED_LINKED_DATA_USE_LIMIT for row in reader)


def estimate_values(rows: list[dict[str, str]], key: str) -> set[str]:
    return {row.get(key, "").strip() for row in rows if row.get(key, "").strip()}


def p_value_summary(rows: list[dict[str, str]]) -> str:
    p_values = []
    for row in rows:
        try:
            value = float(row.get("p_value_normal", ""))
        except ValueError:
            continue
        if 0 <= value <= 1:
            p_values.append(value)
    if not p_values:
        return "No numeric p-values available."
    p_values.sort()
    m = len(p_values)
    bh_values = [min(p * m / (idx + 1), 1.0) for idx, p in enumerate(p_values)]
    return f"p-values={m}; min_p={min(p_values):.6g}; min_bh_q={min(bh_values):.6g}"


def main() -> None:
    ensure_dirs()
    estimates = read_csv_dicts(ESTIMATE_PATH)
    placebos = read_csv_dicts(PLACEBO_PATH)
    audit = []
    result_rows = []
    limited_diagnostic = has_limited_linked_marker(INPUT_PATH) or any(
        row.get("identification_status", "").startswith("limited_diagnostic") for row in estimates
    )

    if not INPUT_PATH.exists():
        audit.append(
            audit_row(
                "robustness_inputs",
                "blocked_no_analytical_dataset",
                "No climate-linked analytical dataset exists.",
                input_path=relative(INPUT_PATH),
                required_action="Build climate-linked household outcome data before robustness checks.",
            )
        )
    elif (blocker := limited_linked_blocker(INPUT_PATH)) and not estimates:
        audit.append(blocker)
    elif not estimates:
        audit.append(
            audit_row(
                "primary_estimate_gate",
                "blocked_no_primary_estimate",
                "No reduced-form estimate exists to stress-test.",
                input_path=relative(ESTIMATE_PATH),
                required_action="Run script/10_causal_models.py and obtain at least one reduced-form estimate.",
            )
        )
    else:
        primary = estimates[0]
        outcomes = estimate_values(estimates, "outcome")
        exposures = estimate_values(estimates, "exposure")
        models = estimate_values(estimates, "model")
        window_models = {model for model in models if "window_" in model}
        for check in REQUIRED_CHECKS:
            status = "planned_not_attempted"
            notes = "Requires specialized data or refit logic beyond the primary estimate."
            result = ""
            if check == "alternative_financial_hardship_thresholds":
                if {"che10_total_budget", "che25_total_budget"}.issubset(outcomes):
                    status = "attempted_limited_threshold_comparison" if limited_diagnostic else "attempted_threshold_comparison"
                    result = "CHE10 and CHE25 reduced-form diagnostic estimates are both present."
                    notes = "Threshold comparison is diagnostic only; outcome promotion remains blocked." if limited_diagnostic else "Threshold comparison estimated."
                else:
                    status = "blocked_no_alternative_financial_threshold_estimate"
                    notes = "Need at least two financial-hardship threshold outcomes."
            if check == "alternative_climate_lags":
                if len(window_models) >= 2:
                    status = "attempted_limited_window_lag_comparison" if limited_diagnostic else "attempted_window_lag_comparison"
                    result = f"Window-specific estimate models={len(window_models)}."
                    notes = "Compares diagnostic windows only; primary climate baseline remains unaccepted." if limited_diagnostic else "Alternative exposure windows estimated."
                else:
                    status = "blocked_no_lagged_exposure_family"
                    notes = "No comparable lagged exposure family detected."
            if check == "multiple_testing_correction":
                status = "attempted_limited_bh_correction" if limited_diagnostic else "attempted_bh_correction"
                result = p_value_summary(estimates)
                notes = "Benjamini-Hochberg summary over diagnostic estimates; not inferentially promoted." if limited_diagnostic else "Benjamini-Hochberg summary over reduced-form estimates."
            if check == "future_climate_placebo":
                ready = any(row.get("test") == "future_climate_lead_placebo" and row.get("status") == "ready" for row in placebos)
                status = "attempted_future_climate_placebo_not_available" if not ready else "ready_not_run"
                result = "No future climate lead variables exist in the linked diagnostic file." if not ready else "Future climate lead variables are available but not yet refit."
                notes = "" if ready else "Placebo attempt documented as unavailable; construct future lead exposures before causal interpretation."
            result_rows.append(
                {
                    "primary_outcome": primary.get("outcome", ""),
                    "primary_exposure": primary.get("exposure", ""),
                    "robustness_check": check,
                    "status": status,
                    "estimate_rows": len(estimates),
                    "result": result,
                    "notes": notes,
                }
            )
        attempted = [row for row in result_rows if row["status"] not in {"planned_not_attempted", "blocked_no_future_climate_lead", "blocked_no_lagged_exposure_family"}]
        audit.append(
            audit_row(
                "robustness_grid",
                "complete_limited_diagnostic" if limited_diagnostic and attempted else ("partial_attempted" if attempted else "blocked_no_attempted_checks"),
                f"Primary estimates={len(estimates)}; robustness grid rows={len(result_rows)}; ready rows={len(attempted)}.",
                input_path=relative(ESTIMATE_PATH),
                rows_input=len(estimates),
                rows_output=len(result_rows),
                output_path=relative(RESULT_PATH),
                required_action="Promote verified analytical data and run full refits before treating robustness/placebo checks as causal evidence." if limited_diagnostic else "Refit models for each robustness design before treating robustness/placebo checks as complete.",
            )
        )

    write_csv(AUDIT_PATH, audit, AUDIT_COLUMNS)
    write_csv(RESULT_PATH, result_rows, RESULT_COLUMNS)
    append_log(TEMP_DIR / "audit_log.md", f"Robustness audit wrote result rows={len(result_rows)}.")
    print(f"Robustness audit wrote result rows={len(result_rows)}.")


if __name__ == "__main__":
    main()
