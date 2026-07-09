from __future__ import annotations

import csv
from pathlib import Path
from typing import Any

from common import DATA_DIR, RESULT_DIR, TEMP_DIR, append_log, ensure_dirs, write_csv


INPUT_PATH = DATA_DIR / "climate_linked_household.csv"
CAUSAL_AUDIT_PATH = RESULT_DIR / "causal_model_audit.csv"
PLACEBO_PATH = RESULT_DIR / "placebo_readiness_audit.csv"
ESTIMATE_PATH = RESULT_DIR / "reduced_form_estimates.csv"
AUDIT_PATH = RESULT_DIR / "causal_ml_policy_audit.csv"
CATE_PATH = RESULT_DIR / "causal_ml_cate_summary.csv"
POLICY_PATH = RESULT_DIR / "policy_targeting_simulation.csv"
REJECTED_PATH = TEMP_DIR / "rejected_designs.md"

AUDIT_COLUMNS = ["check", "status", "detail", "input_path", "rows_input", "rows_output", "output_path", "required_action"]
CATE_COLUMNS = ["outcome", "treatment", "method", "rows", "ate", "ate_se", "cate_calibration", "overlap_status", "notes"]
POLICY_COLUMNS = ["outcome", "treatment", "targeting_rule", "budget_share", "policy_value", "precision", "false_exclusion_poorest", "equity_weighted_value", "notes"]


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


def append_rejection_once(reason: str) -> None:
    REJECTED_PATH.parent.mkdir(parents=True, exist_ok=True)
    if not REJECTED_PATH.exists():
        REJECTED_PATH.write_text("# Rejected Designs\n\n| Date | Design/model | Status | Reason |\n|---|---|---|---|\n", encoding="utf-8")
    text = REJECTED_PATH.read_text(encoding="utf-8")
    marker = "Causal ML/policy learning after reduced-form gate"
    if marker in text:
        return
    with REJECTED_PATH.open("a", encoding="utf-8") as f:
        f.write(f"| 2026-07-08 | {marker} | rejected for now | {reason} |\n")


def write_empty_results() -> None:
    write_csv(CATE_PATH, [], CATE_COLUMNS)
    write_csv(POLICY_PATH, [], POLICY_COLUMNS)


def main() -> None:
    ensure_dirs()
    write_empty_results()
    rows = []
    estimates = read_csv_dicts(ESTIMATE_PATH)
    placebos = read_csv_dicts(PLACEBO_PATH)
    causal_audit = read_csv_dicts(CAUSAL_AUDIT_PATH)
    if not INPUT_PATH.exists():
        reason = "No climate-linked analytical dataset exists."
        rows.append(audit_row("causal_ml_inputs", "rejected_no_analytical_dataset", reason, input_path=relative(INPUT_PATH), required_action="Build climate-linked household outcome data."))
        append_rejection_once(reason)
    elif not estimates:
        reason = "No reduced-form climate-shock estimate exists."
        rows.append(audit_row("reduced_form_gate", "rejected_no_reduced_form_estimate", reason, input_path=relative(ESTIMATE_PATH), rows_input=len(causal_audit), required_action="Estimate and audit a reduced-form model first."))
        append_rejection_once(reason)
    elif not placebos or any(row.get("status") != "ready" for row in placebos):
        blockers = "; ".join(f"{row.get('test')}: {row.get('status')}" for row in placebos) if placebos else "no placebo audit"
        reason = f"Reduced-form gate is not placebo-ready ({blockers})."
        rows.append(audit_row("identification_gate", "rejected_placebo_not_ready", reason, input_path=relative(PLACEBO_PATH), rows_input=len(placebos), required_action="Construct and pass climate-lead, seasonality, and geography checks before causal ML."))
        append_rejection_once(reason)
    elif not any(row.get("identification_status") == "placebo_ready_not_yet_interpreted" for row in estimates):
        reason = "Reduced-form estimates are not marked as identification-ready."
        rows.append(audit_row("identification_gate", "rejected_reduced_form_not_credible", reason, input_path=relative(ESTIMATE_PATH), rows_input=len(estimates), required_action="Resolve reduced-form identification audit."))
        append_rejection_once(reason)
    else:
        rows.append(
            audit_row(
                "causal_ml_gate",
                "ready_not_estimated",
                "Reduced-form and placebo-readiness gates are present, but causal ML estimators are intentionally not run until moderator set, overlap checks, and cross-fitting design are specified.",
                input_path=relative(INPUT_PATH),
                rows_input=len(estimates),
                required_action="Specify treatment, moderators, cross-fitting folds, overlap rules, and policy-value assumptions.",
            )
        )

    write_csv(AUDIT_PATH, rows, AUDIT_COLUMNS)
    append_log(TEMP_DIR / "audit_log.md", f"Causal ML/policy learning audit wrote {len(rows)} row(s).")
    print(f"Causal ML/policy learning audit wrote {len(rows)} row(s).")


if __name__ == "__main__":
    main()
