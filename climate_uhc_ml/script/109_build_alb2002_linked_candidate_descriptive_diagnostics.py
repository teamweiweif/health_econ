from __future__ import annotations

import csv
import math
from typing import Any

import pandas as pd

from common import REPORT_DIR, RESULT_DIR, TEMP_DIR, append_log, ensure_dirs, write_csv


LINKED_PATH = TEMP_DIR / "alb2002_climate_outcome_linked_candidate.csv"
LINKED_SUMMARY_PATH = RESULT_DIR / "alb2002_climate_outcome_linked_candidate_summary.csv"
AUDIT_PATH = RESULT_DIR / "alb2002_linked_candidate_descriptive_audit.csv"
CELLS_PATH = RESULT_DIR / "alb2002_linked_candidate_descriptive_cells.csv"
SUMMARY_PATH = RESULT_DIR / "alb2002_linked_candidate_descriptive_summary.csv"
REPORT_PATH = REPORT_DIR / "alb2002_linked_candidate_descriptive_diagnostics.md"

DECISION = "blocked_alb2002_linked_candidate_descriptive_screen_not_promoted_due_unpromoted_inputs"

OUTCOMES = [
    "uhc_double_failure_che10_or_access_candidate",
    "uhc_double_failure_che25_or_access_candidate",
    "both_che10_access_candidate",
    "coping_health_cost_candidate",
]
PRIMARY_OUTCOMES = [
    "uhc_double_failure_che10_or_access_candidate",
    "uhc_double_failure_che25_or_access_candidate",
]
CLIMATE_FLAGS = [
    "diagnostic_low_rain_z_le_m1",
    "diagnostic_extreme_wet_z_ge_15",
    "diagnostic_extreme_heat_z_ge_15",
    "diagnostic_combined_climate_stress",
]
SUBGROUPS = ["rural", "agriculture_livelihood", "health_insurance_candidate"]
READINESS_COLUMNS = [
    "harmonized_recipe_ready",
    "outcome_promotion_ready",
    "climate_linkage_ready",
    "data_write_ready",
]

AUDIT_COLUMNS = [
    "check_id",
    "check_label",
    "status",
    "rows_checked",
    "passing_rows",
    "failing_rows",
    "evidence",
    "promotion_ready_rows",
    "blocking_reason",
    "next_action",
]
CELL_COLUMNS = [
    "cell_id",
    "diagnostic_scope",
    "population",
    "group_variable",
    "group_value",
    "window_months",
    "climate_flag",
    "outcome",
    "rows",
    "households",
    "nonmissing",
    "events",
    "event_rate",
    "candidate_weighted_rate_not_inference",
    "positive_weight_rows",
    "weight_sum",
    "interpretation",
]
SUMMARY_COLUMNS = ["metric", "value", "interpretation"]


def read_csv_dicts(path) -> list[dict[str, str]]:
    if not path.exists():
        return []
    with path.open(encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def metric_value(rows: list[dict[str, str]], metric: str, default: str = "0") -> str:
    return next((row.get("value", default) for row in rows if row.get("metric") == metric), default)


def safe_float(value: Any) -> float:
    try:
        number = float(str(value).strip())
    except (TypeError, ValueError):
        return float("nan")
    return number if math.isfinite(number) else float("nan")


def fmt(value: Any) -> str:
    number = safe_float(value)
    if math.isnan(number):
        return "" if value is None else str(value)
    if number.is_integer():
        return str(int(number))
    return f"{number:.6g}"


def numeric(frame: pd.DataFrame, column: str) -> pd.Series:
    if column not in frame.columns:
        return pd.Series(pd.NA, index=frame.index)
    return pd.to_numeric(frame[column], errors="coerce")


def nonmissing_count(frame: pd.DataFrame, column: str) -> int:
    if column not in frame.columns:
        return 0
    return int(numeric(frame, column).notna().sum())


def positive_sum(frame: pd.DataFrame, column: str) -> int:
    return int(numeric(frame, column).fillna(0).sum()) if column in frame.columns else 0


def label_value(value: Any) -> str:
    if pd.isna(value):
        return "missing"
    text = str(value).strip()
    number = safe_float(text)
    if not math.isnan(number) and number.is_integer():
        return str(int(number))
    return text or "missing"


def sort_key(value: Any) -> tuple[int, float | str]:
    text = label_value(value)
    number = safe_float(text)
    if not math.isnan(number):
        return (0, number)
    return (1, text)


def rate_stats(frame: pd.DataFrame, value_column: str) -> dict[str, Any]:
    values = numeric(frame, value_column)
    nonmissing_mask = values.notna()
    nonmissing = int(nonmissing_mask.sum())
    events = int((values[nonmissing_mask] == 1).sum()) if nonmissing else 0

    weights = numeric(frame, "household_weight")
    weight_mask = nonmissing_mask & weights.notna() & (weights > 0)
    positive_weight_rows = int(weight_mask.sum())
    weight_sum = float(weights[weight_mask].sum()) if positive_weight_rows else float("nan")
    weighted_rate = (
        float((values[weight_mask] * weights[weight_mask]).sum() / weight_sum)
        if positive_weight_rows and weight_sum > 0
        else float("nan")
    )
    return {
        "nonmissing": nonmissing,
        "events": events,
        "event_rate": "" if not nonmissing else fmt(events / nonmissing),
        "candidate_weighted_rate_not_inference": "" if math.isnan(weighted_rate) else fmt(weighted_rate),
        "positive_weight_rows": positive_weight_rows,
        "weight_sum": "" if math.isnan(weight_sum) else fmt(weight_sum),
    }


def add_rate_cell(
    rows: list[dict[str, Any]],
    *,
    diagnostic_scope: str,
    population: str,
    group_variable: str,
    group_value: str,
    window_months: str,
    climate_flag: str,
    outcome: str,
    frame: pd.DataFrame,
    value_column: str,
    interpretation: str,
) -> None:
    stats = rate_stats(frame, value_column)
    rows.append(
        {
            "cell_id": f"cell_{len(rows) + 1:03d}",
            "diagnostic_scope": diagnostic_scope,
            "population": population,
            "group_variable": group_variable,
            "group_value": group_value,
            "window_months": window_months,
            "climate_flag": climate_flag,
            "outcome": outcome,
            "rows": len(frame),
            "households": frame["hhid"].nunique() if "hhid" in frame.columns else "",
            **stats,
            "interpretation": interpretation,
        }
    )


def build_cells(linked: pd.DataFrame, households: pd.DataFrame) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []

    for outcome in OUTCOMES:
        add_rate_cell(
            rows,
            diagnostic_scope="household_outcome_rate",
            population="deduplicated_households",
            group_variable="all",
            group_value="all",
            window_months="",
            climate_flag="",
            outcome=outcome,
            frame=households,
            value_column=outcome,
            interpretation="Candidate household outcome rate on one row per household; not a promoted descriptive estimate.",
        )

    for subgroup in SUBGROUPS:
        if subgroup not in households.columns:
            continue
        for key, group in sorted(households.groupby(subgroup, dropna=False), key=lambda item: sort_key(item[0])):
            for outcome in OUTCOMES:
                add_rate_cell(
                    rows,
                    diagnostic_scope="household_outcome_rate_by_subgroup",
                    population="deduplicated_households",
                    group_variable=subgroup,
                    group_value=label_value(key),
                    window_months="",
                    climate_flag="",
                    outcome=outcome,
                    frame=group,
                    value_column=outcome,
                    interpretation="Candidate subgroup screen only; survey design and outcome promotion gates remain blocked.",
                )

    for window, window_group in sorted(linked.groupby("window_months", dropna=False), key=lambda item: sort_key(item[0])):
        window_label = label_value(window)
        for flag in CLIMATE_FLAGS:
            add_rate_cell(
                rows,
                diagnostic_scope="household_window_climate_flag_rate",
                population="household_window_rows",
                group_variable="window_months",
                group_value=window_label,
                window_months=window_label,
                climate_flag=flag,
                outcome="",
                frame=window_group,
                value_column=flag,
                interpretation="Diagnostic climate flag prevalence within the linked candidate; not an accepted exposure.",
            )

    for window, window_group in sorted(linked.groupby("window_months", dropna=False), key=lambda item: sort_key(item[0])):
        window_label = label_value(window)
        for flag in CLIMATE_FLAGS:
            flag_values = numeric(window_group, flag).fillna(-1)
            for flag_value in [0, 1]:
                flag_group = window_group[flag_values == flag_value]
                for outcome in PRIMARY_OUTCOMES:
                    add_rate_cell(
                        rows,
                        diagnostic_scope="household_window_outcome_by_climate_flag",
                        population="household_window_rows",
                        group_variable=flag,
                        group_value=str(flag_value),
                        window_months=window_label,
                        climate_flag=flag,
                        outcome=outcome,
                        frame=flag_group,
                        value_column=outcome,
                        interpretation="Candidate outcome screen by diagnostic climate flag; repeated household-window rows are not an analysis sample.",
                    )

    return rows


def audit_row(check_id: str, label: str, status: str, rows_checked: int, passing: int, evidence: str, block: str, next_action: str) -> dict[str, str]:
    return {
        "check_id": check_id,
        "check_label": label,
        "status": status,
        "rows_checked": str(rows_checked),
        "passing_rows": str(passing),
        "failing_rows": str(max(rows_checked - passing, 0)),
        "evidence": evidence,
        "promotion_ready_rows": "0",
        "blocking_reason": block,
        "next_action": next_action,
    }


def blocking_reason() -> str:
    return (
        "This descriptive screen uses the temp-only ALB_2002 climate/outcome linked candidate. "
        "The linked inputs remain unpromoted because final outcome, harmonized recipe, verified geography, "
        "primary climate source, and historical baseline gates have not passed together."
    )


def build_audit(linked: pd.DataFrame, households: pd.DataFrame, cells: list[dict[str, Any]]) -> list[dict[str, str]]:
    household_window_counts = linked.groupby("hhid")["window_months"].nunique() if len(linked) else pd.Series(dtype="int64")
    outcome_nonmissing = min(nonmissing_count(households, outcome) for outcome in OUTCOMES)
    climate_nonmissing = min(nonmissing_count(linked, flag) for flag in CLIMATE_FLAGS)
    positive_weight_rows = int((numeric(linked, "household_weight") > 0).sum())
    readiness_ready_rows = sum(positive_sum(linked, column) for column in READINESS_COLUMNS)
    return [
        audit_row(
            "input_profile",
            "Linked candidate input exists and is limited to ALB_2002 household-window rows",
            "complete_candidate_not_promoted" if len(linked) and households["hhid"].nunique() == len(households) else "partial_or_failed",
            len(linked),
            len(linked) if len(linked) and households["hhid"].nunique() == len(households) else 0,
            f"linked_rows={len(linked)}; deduplicated_households={len(households)}; distinct_households={households['hhid'].nunique()}; windows={linked['window_months'].nunique()}",
            blocking_reason(),
            "Keep this screen tied to temp/alb2002_climate_outcome_linked_candidate.csv until upstream promotion gates pass.",
        ),
        audit_row(
            "household_window_structure",
            "Every household contributes the expected diagnostic exposure windows",
            "complete_candidate_not_promoted" if len(household_window_counts) and int(household_window_counts.min()) == 4 and int(household_window_counts.max()) == 4 else "partial_or_failed",
            len(household_window_counts),
            int((household_window_counts == 4).sum()) if len(household_window_counts) else 0,
            f"min_windows_per_household={int(household_window_counts.min()) if len(household_window_counts) else 0}; max_windows_per_household={int(household_window_counts.max()) if len(household_window_counts) else 0}; expected_long_rows={len(households) * linked['window_months'].nunique()}",
            "Repeated household-window rows must not be treated as independent final observations.",
            "Use deduplicated households for outcome screens and long rows only for window-specific diagnostics.",
        ),
        audit_row(
            "household_outcome_screen",
            "Candidate outcome fields are nonmissing on deduplicated households",
            "complete_candidate_not_promoted" if outcome_nonmissing == len(households) else "partial_or_failed",
            len(households),
            outcome_nonmissing,
            f"che10_or_access_households={positive_sum(households, 'uhc_double_failure_che10_or_access_candidate')}; che25_or_access_households={positive_sum(households, 'uhc_double_failure_che25_or_access_candidate')}; both_che10_access_households={positive_sum(households, 'both_che10_access_candidate')}; coping_households={positive_sum(households, 'coping_health_cost_candidate')}",
            "Outcome fields are candidate screens, not final SDG/UHC outcomes.",
            "Promote outcome definitions only after OOP, access, denominator, SDG, and benchmark checks pass.",
        ),
        audit_row(
            "climate_window_screen",
            "Diagnostic climate flags are nonmissing on household-window rows",
            "complete_candidate_not_promoted" if climate_nonmissing == len(linked) else "partial_or_failed",
            len(linked),
            climate_nonmissing,
            f"low_rain_rows={positive_sum(linked, 'diagnostic_low_rain_z_le_m1')}; extreme_wet_rows={positive_sum(linked, 'diagnostic_extreme_wet_z_ge_15')}; extreme_heat_rows={positive_sum(linked, 'diagnostic_extreme_heat_z_ge_15')}; combined_stress_rows={positive_sum(linked, 'diagnostic_combined_climate_stress')}",
            "Climate flags are within-candidate NASA POWER centroid diagnostics, not accepted historical anomalies.",
            "Replace these flags with promoted CHIRPS/ERA5 historical anomalies before formal descriptives or models.",
        ),
        audit_row(
            "cell_output_screen",
            "Descriptive screen writes only result/report outputs and no data outputs",
            "complete_candidate_not_promoted" if len(cells) else "partial_or_failed",
            len(cells),
            len(cells),
            f"cell_rows={len(cells)}; output_cells=result/alb2002_linked_candidate_descriptive_cells.csv; output_report=report/alb2002_linked_candidate_descriptive_diagnostics.md",
            "The cell table is a readability screen over blocked inputs.",
            "Do not cite these cells as final weighted prevalence, maps, missingness heatmaps, or analysis-sample diagnostics.",
        ),
        audit_row(
            "weight_design_guardrail",
            "Candidate household weights are present but not accepted for inference",
            "blocked",
            len(linked),
            0,
            f"positive_candidate_weight_rows={positive_weight_rows}; weight_field=household_weight; survey_design_status=not_accepted_for_inference",
            "Weights are carried for audit visibility only; the accepted survey design and promoted analysis sample are absent.",
            "Use candidate-weighted rates only to inspect plausibility, not to report inferential estimates.",
        ),
        audit_row(
            "promotion_gate",
            "Descriptive screen does not promote the linked candidate",
            "blocked",
            len(linked),
            0,
            f"readiness_positive_rows={readiness_ready_rows}; decision={DECISION}",
            blocking_reason(),
            "Do not write data/climate_linked_household.* or mark descriptive diagnostics complete from this screen.",
        ),
    ]


def summary_row(metric: str, value: Any, interpretation: str) -> dict[str, str]:
    return {"metric": metric, "value": fmt(value), "interpretation": interpretation}


def build_summary(linked: pd.DataFrame, households: pd.DataFrame, cells: list[dict[str, Any]], audit: list[dict[str, str]]) -> list[dict[str, str]]:
    linked_summary = read_csv_dicts(LINKED_SUMMARY_PATH)
    scope_counts = pd.Series([row["diagnostic_scope"] for row in cells]).value_counts().to_dict() if cells else {}
    return [
        summary_row("alb2002_linked_candidate_descriptive_input_rows", len(linked), "Input temp-only household-window rows screened."),
        summary_row("alb2002_linked_candidate_descriptive_household_rows", len(households), "Deduplicated households used for household-level candidate outcome rates."),
        summary_row("alb2002_linked_candidate_descriptive_window_rows", linked["window_months"].nunique(), "Diagnostic exposure windows represented."),
        summary_row("alb2002_linked_candidate_descriptive_audit_rows", len(audit), "Audit rows for temp-only descriptive screen guardrails."),
        summary_row("alb2002_linked_candidate_descriptive_cell_rows", len(cells), "Readable diagnostic cell rows written."),
        summary_row("alb2002_linked_candidate_descriptive_household_outcome_cell_rows", scope_counts.get("household_outcome_rate", 0), "Overall deduplicated-household candidate outcome cells."),
        summary_row("alb2002_linked_candidate_descriptive_subgroup_outcome_cell_rows", scope_counts.get("household_outcome_rate_by_subgroup", 0), "Subgroup candidate outcome cells."),
        summary_row("alb2002_linked_candidate_descriptive_climate_flag_cell_rows", scope_counts.get("household_window_climate_flag_rate", 0), "Window-specific diagnostic climate flag cells."),
        summary_row("alb2002_linked_candidate_descriptive_outcome_by_climate_flag_cell_rows", scope_counts.get("household_window_outcome_by_climate_flag", 0), "Candidate outcome-by-diagnostic-climate-flag cells."),
        summary_row("alb2002_linked_candidate_descriptive_che10_or_access_households", positive_sum(households, "uhc_double_failure_che10_or_access_candidate"), "Deduplicated households with CHE10-or-access candidate flag."),
        summary_row("alb2002_linked_candidate_descriptive_che25_or_access_households", positive_sum(households, "uhc_double_failure_che25_or_access_candidate"), "Deduplicated households with CHE25-or-access candidate flag."),
        summary_row("alb2002_linked_candidate_descriptive_both_che10_access_households", positive_sum(households, "both_che10_access_candidate"), "Deduplicated households with both CHE10 and access candidate flag."),
        summary_row("alb2002_linked_candidate_descriptive_coping_households", positive_sum(households, "coping_health_cost_candidate"), "Deduplicated households with health-cost coping candidate flag."),
        summary_row("alb2002_linked_candidate_descriptive_low_rain_rows", positive_sum(linked, "diagnostic_low_rain_z_le_m1"), "Long rows with diagnostic low-rain flag."),
        summary_row("alb2002_linked_candidate_descriptive_extreme_wet_rows", positive_sum(linked, "diagnostic_extreme_wet_z_ge_15"), "Long rows with diagnostic extreme-wet flag."),
        summary_row("alb2002_linked_candidate_descriptive_extreme_heat_rows", positive_sum(linked, "diagnostic_extreme_heat_z_ge_15"), "Long rows with diagnostic extreme-heat flag."),
        summary_row("alb2002_linked_candidate_descriptive_combined_stress_rows", positive_sum(linked, "diagnostic_combined_climate_stress"), "Long rows with any diagnostic combined-stress flag."),
        summary_row("alb2002_linked_candidate_descriptive_climate_linkage_ready_rows", positive_sum(linked, "climate_linkage_ready"), "Rows ready for promoted climate linkage; should remain zero."),
        summary_row("alb2002_linked_candidate_descriptive_outcome_promotion_ready_rows", positive_sum(linked, "outcome_promotion_ready"), "Rows ready for promoted outcomes; should remain zero."),
        summary_row("alb2002_linked_candidate_descriptive_harmonized_recipe_ready_rows", positive_sum(linked, "harmonized_recipe_ready"), "Rows ready for harmonized recipe promotion; should remain zero."),
        summary_row("alb2002_linked_candidate_descriptive_data_write_ready_rows", positive_sum(linked, "data_write_ready"), "Rows allowed to be written to data/; should remain zero."),
        summary_row("alb2002_linked_candidate_descriptive_source_linked_decision", metric_value(linked_summary, "alb2002_climate_outcome_linked_candidate_current_decision", "missing"), "Upstream linked-candidate decision consumed."),
        summary_row("alb2002_linked_candidate_descriptive_current_decision", DECISION, "Current temp-only descriptive screen decision."),
    ]


def markdown_rows(rows: list[dict[str, Any]], columns: list[str], limit: int = 25) -> str:
    lines = ["| " + " | ".join(columns) + " |", "|" + "|".join("---" for _ in columns) + "|"]
    for row in rows[:limit]:
        values = []
        for column in columns:
            value = str(row.get(column, "")).replace("|", "/")
            if len(value) > 130:
                value = value[:127] + "..."
            values.append(value)
        lines.append("| " + " | ".join(values) + " |")
    return "\n".join(lines)


def write_report(summary: list[dict[str, str]], audit: list[dict[str, str]], cells: list[dict[str, Any]]) -> None:
    summary_table = "\n".join(f"| {row['metric']} | {row['value']} | {row['interpretation']} |" for row in summary)
    REPORT_PATH.write_text(
        f"""# ALB_2002 Linked Candidate Descriptive Diagnostics

Status: temp-only descriptive screen over the blocked ALB_2002 climate/outcome linked candidate. This report is for audit readability only. It does not create a promoted descriptive diagnostic, accepted prevalence estimate, map, missingness heatmap, analysis sample, predictive feature table, or causal input.

## Summary

| Metric | Value | Interpretation |
|---|---:|---|
{summary_table}

## Guardrail Audit

{markdown_rows(audit, ['check_id', 'status', 'rows_checked', 'passing_rows', 'promotion_ready_rows', 'evidence', 'blocking_reason'])}

## Example Diagnostic Cells

{markdown_rows(cells, ['diagnostic_scope', 'population', 'group_variable', 'group_value', 'window_months', 'climate_flag', 'outcome', 'rows', 'households', 'events', 'event_rate', 'candidate_weighted_rate_not_inference'], limit=30)}

## Interpretation

- Household outcome rates are computed on one deduplicated row per household.
- Climate flag rates and outcome-by-flag screens use repeated household-window rows and are not final analysis observations.
- Candidate weighted rates use `household_weight` only as a plausibility screen; survey design and promoted analysis-sample gates remain blocked.
- The underlying climate fields are within-candidate NASA POWER centroid diagnostics, not CHIRPS/ERA5 historical anomalies.
- Harmonized-recipe-ready, outcome-promotion-ready, climate-linkage-ready, and data-write-ready rows remain zero.

## Machine-Readable Outputs

- `result/alb2002_linked_candidate_descriptive_audit.csv`
- `result/alb2002_linked_candidate_descriptive_cells.csv`
- `result/alb2002_linked_candidate_descriptive_summary.csv`
""",
        encoding="utf-8",
    )


def main() -> None:
    ensure_dirs()
    if not LINKED_PATH.exists():
        raise FileNotFoundError(f"Missing prerequisite: {LINKED_PATH}")
    linked = pd.read_csv(LINKED_PATH, encoding="utf-8-sig")
    if "hhid" not in linked.columns:
        raise ValueError("Linked candidate is missing hhid.")
    households = linked.drop_duplicates("hhid").copy()
    cells = build_cells(linked, households)
    audit = build_audit(linked, households, cells)
    summary = build_summary(linked, households, cells, audit)
    write_csv(AUDIT_PATH, audit, AUDIT_COLUMNS)
    write_csv(CELLS_PATH, cells, CELL_COLUMNS)
    write_csv(SUMMARY_PATH, summary, SUMMARY_COLUMNS)
    write_report(summary, audit, cells)
    append_log(TEMP_DIR / "audit_log.md", f"Built ALB_2002 linked candidate descriptive screen cell_rows={len(cells)} decision={DECISION}.")
    print(f"ALB_2002 linked candidate descriptive screen cell_rows={len(cells)} decision={DECISION}.")


if __name__ == "__main__":
    main()
