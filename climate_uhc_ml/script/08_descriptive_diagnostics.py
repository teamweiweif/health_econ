from __future__ import annotations

from pathlib import Path
from typing import Any

import pandas as pd

from common import DATA_DIR, REPORT_DIR, RESULT_DIR, TEMP_DIR, append_log, ensure_dirs, write_csv


INPUT_PATH = DATA_DIR / "climate_linked_household.csv"
AUDIT_PATH = RESULT_DIR / "descriptive_diagnostics_audit.csv"
PREVALENCE_PATH = RESULT_DIR / "descriptive_weighted_prevalence.csv"
MISSINGNESS_PATH = RESULT_DIR / "descriptive_missingness.csv"
EXPOSURE_PATH = RESULT_DIR / "descriptive_climate_exposure_summary.csv"
SAMPLE_FLOW_PATH = RESULT_DIR / "sample_inclusion_flow.csv"
FEASIBILITY_PATH = RESULT_DIR / "analysis_sample_feasibility.csv"
REPORT_PATH = REPORT_DIR / "descriptive_diagnostics.md"

AUDIT_COLUMNS = ["check", "status", "detail", "input_path", "rows_input", "rows_output", "output_path", "required_action"]
GROUP_COLUMNS = ["country", "survey_name", "wave"]
WEIGHT_COLUMNS = ["household_weight", "person_weight", "weight"]
FINANCIAL_OUTCOMES = ["sdg382_discretionary_40", "che10_total_budget", "che25_total_budget", "capacity_to_pay_40"]
ACCESS_OUTCOMES = [
    "forgone_care_conditional_need",
    "forgone_care_cost_barrier",
    "forgone_care_distance_barrier",
    "forgone_care_supply_barrier",
]
COMPOSITE_OUTCOMES = ["uhc_double_failure", "financial_only_failure", "access_only_failure", "both_financial_and_access_failure"]
OUTCOME_COLUMNS = FINANCIAL_OUTCOMES + ACCESS_OUTCOMES + COMPOSITE_OUTCOMES
CLIMATE_PREFIXES = ["precip_", "temp_", "rainfall_", "heat_", "drought_", "spei_", "water_"]
LIMITED_LINKED_DATA_USE_LIMIT = "climate_linked_che_diagnostic_only_not_for_promoted_descriptive_ml_causal_or_policy_analysis"
REQUIRED_MAIN_SAMPLE = [
    "total_consumption",
    "oop_health_expenditure",
    "household_weight",
    "survey_year",
    "survey_month",
]


def read_table(path: Path) -> pd.DataFrame:
    if path.suffix.lower() == ".parquet":
        return pd.read_parquet(path)
    return pd.read_csv(path)


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


def relative(path: Path) -> str:
    try:
        return str(path.relative_to(TEMP_DIR.parent))
    except ValueError:
        return str(path)


def empty_outputs() -> None:
    write_csv(PREVALENCE_PATH, [], ["country", "survey_name", "wave", "outcome", "rows", "nonmissing", "event_rate", "weighted_prevalence"])
    write_csv(MISSINGNESS_PATH, [], ["country", "survey_name", "wave", "variable", "rows", "missing", "missing_rate"])
    write_csv(EXPOSURE_PATH, [], ["country", "survey_name", "wave", "exposure", "rows", "nonmissing", "mean", "sd", "min", "p25", "median", "p75", "max"])
    write_csv(SAMPLE_FLOW_PATH, [], ["step", "status", "rows", "dropped", "detail"])
    write_csv(FEASIBILITY_PATH, [], ["country", "survey_name", "wave", "rows", "has_financial_outcome", "has_access_outcome", "has_climate", "passes_main_sample_gate", "gap"])


def is_limited_linked_diagnostic(df: pd.DataFrame) -> bool:
    return "data_use_limit" in df.columns and df["data_use_limit"].astype(str).str.strip().eq(LIMITED_LINKED_DATA_USE_LIMIT).any()


def readiness_blocker(df: pd.DataFrame, readiness_column: str) -> str:
    if readiness_column in df.columns:
        ready = pd.to_numeric(df[readiness_column], errors="coerce").fillna(0)
        if int(ready.sum()) == 0:
            return f"All {readiness_column} values are zero."
    return ""


def weighted_mean(series: pd.Series, weights: pd.Series) -> float | None:
    values = pd.to_numeric(series, errors="coerce")
    weights = pd.to_numeric(weights, errors="coerce")
    mask = values.notna() & weights.notna() & (weights > 0)
    if not mask.any():
        return None
    return float((values[mask] * weights[mask]).sum() / weights[mask].sum())


def first_weight(df: pd.DataFrame) -> str | None:
    for column in WEIGHT_COLUMNS:
        if column in df.columns:
            return column
    return None


def binary_rate(series: pd.Series) -> float | None:
    values = pd.to_numeric(series, errors="coerce")
    values = values[values.notna()]
    if len(values) == 0:
        return None
    return float((values == 1).mean())


def exposure_columns(df: pd.DataFrame) -> list[str]:
    out = []
    for column in df.columns:
        low = column.lower()
        if any(low.startswith(prefix) or f"_{prefix}" in low for prefix in CLIMATE_PREFIXES):
            if pd.api.types.is_numeric_dtype(df[column]) or pd.to_numeric(df[column], errors="coerce").notna().any():
                out.append(column)
    return out


def group_iter(df: pd.DataFrame):
    available = [column for column in GROUP_COLUMNS if column in df.columns]
    if not available:
        yield ("all", "all", "all"), df
        return
    for key, group in df.groupby(available, dropna=False):
        if not isinstance(key, tuple):
            key = (key,)
        values = list(key) + [""] * (3 - len(key))
        yield tuple("" if pd.isna(v) else str(v) for v in values[:3]), group


def write_blocked(
    status: str = "blocked_no_climate_linked_dataset",
    detail: str = "No climate-linked analytical dataset exists.",
    action: str = "Build harmonized household data, construct outcomes, extract climate exposure, and merge before descriptive diagnostics.",
    rows_input: Any = 0,
) -> None:
    empty_outputs()
    rows = [
        audit_row(
            "descriptive_inputs",
            status,
            detail,
            input_path=relative(INPUT_PATH),
            rows_input=rows_input,
            required_action=action,
        )
    ]
    write_csv(AUDIT_PATH, rows, AUDIT_COLUMNS)
    REPORT_PATH.write_text(
        f"""# Descriptive Diagnostics

Status: blocked.

{detail}

Required action: {action}
""",
        encoding="utf-8",
    )
    append_log(TEMP_DIR / "audit_log.md", f"Descriptive diagnostics blocked: {status} - {detail}")
    print(f"Descriptive diagnostics blocked: {detail}")


def main() -> None:
    ensure_dirs()
    if not INPUT_PATH.exists():
        write_blocked()
        return

    df = read_table(INPUT_PATH)
    audit = [
        audit_row("descriptive_inputs", "complete", "Read climate-linked analytical dataset.", input_path=relative(INPUT_PATH), rows_input=len(df))
    ]
    if len(df) == 0:
        empty_outputs()
        audit.append(
            audit_row(
                "descriptive_inputs",
                "blocked_empty_dataset",
                "Climate-linked analytical dataset has zero rows.",
                input_path=relative(INPUT_PATH),
                required_action="Rebuild upstream analytical data with at least one row.",
            )
        )
        write_csv(AUDIT_PATH, audit, AUDIT_COLUMNS)
        append_log(TEMP_DIR / "audit_log.md", "Descriptive diagnostics blocked: empty dataset.")
        print("Descriptive diagnostics blocked: empty dataset.")
        return
    limited_diagnostic = is_limited_linked_diagnostic(df)
    blocker = "" if limited_diagnostic else readiness_blocker(df, "descriptive_ready")
    if blocker:
        write_blocked(
            "blocked_limited_climate_linked_not_descriptive_ready",
            blocker,
            "Resolve SDG/access/composite outcomes, primary climate source/baseline gates, and set descriptive_ready only after a verified analytical linked dataset exists.",
            rows_input=len(df),
        )
        return

    weight = first_weight(df)
    outcomes = [column for column in OUTCOME_COLUMNS if column in df.columns]
    climates = exposure_columns(df)
    prevalence_rows: list[dict[str, Any]] = []
    missingness_rows: list[dict[str, Any]] = []
    exposure_rows: list[dict[str, Any]] = []
    feasibility_rows: list[dict[str, Any]] = []

    required_for_missingness = sorted(set(REQUIRED_MAIN_SAMPLE + outcomes + climates + ["admin1", "admin2", "cluster_id", "latitude", "longitude"]))
    for (country, survey_name, wave), group in group_iter(df):
        prevalence_group = group.drop_duplicates(subset=["hhid"]) if "hhid" in group.columns else group
        for outcome in outcomes:
            nonmissing = int(prevalence_group[outcome].notna().sum())
            weights = prevalence_group[weight] if weight else pd.Series([1] * len(prevalence_group), index=prevalence_group.index)
            prevalence_rows.append(
                {
                    "country": country,
                    "survey_name": survey_name,
                    "wave": wave,
                    "outcome": outcome,
                    "rows": len(prevalence_group),
                    "nonmissing": nonmissing,
                    "event_rate": "" if nonmissing == 0 else binary_rate(prevalence_group[outcome]),
                    "weighted_prevalence": "" if nonmissing == 0 else weighted_mean(prevalence_group[outcome], weights),
                }
            )
        for variable in required_for_missingness:
            if variable not in group.columns:
                continue
            missing = int(group[variable].isna().sum())
            missingness_rows.append(
                {
                    "country": country,
                    "survey_name": survey_name,
                    "wave": wave,
                    "variable": variable,
                    "rows": len(group),
                    "missing": missing,
                    "missing_rate": missing / len(group) if len(group) else "",
                }
            )
        for exposure in climates:
            values = pd.to_numeric(group[exposure], errors="coerce")
            values = values[values.notna()]
            if len(values) == 0:
                continue
            exposure_rows.append(
                {
                    "country": country,
                    "survey_name": survey_name,
                    "wave": wave,
                    "exposure": exposure,
                    "rows": len(group),
                    "nonmissing": len(values),
                    "mean": float(values.mean()),
                    "sd": float(values.std()) if len(values) > 1 else "",
                    "min": float(values.min()),
                    "p25": float(values.quantile(0.25)),
                    "median": float(values.quantile(0.5)),
                    "p75": float(values.quantile(0.75)),
                    "max": float(values.max()),
                }
            )
        missing_required = [column for column in REQUIRED_MAIN_SAMPLE if column not in group.columns or group[column].notna().sum() == 0]
        has_geography = any(column in group.columns and group[column].notna().sum() > 0 for column in ["latitude", "longitude", "admin1", "admin2", "cluster_id"])
        has_financial = any(column in group.columns and group[column].notna().sum() > 0 for column in FINANCIAL_OUTCOMES)
        has_access = any(column in group.columns and group[column].notna().sum() > 0 for column in ACCESS_OUTCOMES)
        has_climate = any(column in group.columns and group[column].notna().sum() > 0 for column in climates)
        gap = []
        if missing_required:
            gap.append("missing required columns/values: " + ";".join(missing_required))
        if not has_geography:
            gap.append("no verified geography")
        if not has_financial:
            gap.append("no financial-protection outcome")
        if not has_climate:
            gap.append("no climate exposure")
        if limited_diagnostic:
            gap.append("limited diagnostic file; not promoted for final descriptive analysis")
        feasibility_rows.append(
            {
                "country": country,
                "survey_name": survey_name,
                "wave": wave,
                "rows": len(group),
                "has_financial_outcome": int(has_financial),
                "has_access_outcome": int(has_access),
                "has_climate": int(has_climate),
                "passes_main_sample_gate": int(not gap),
                "gap": "; ".join(gap),
            }
        )

    sample_flow = [
        {"step": "input_climate_linked_household", "status": "complete", "rows": len(df), "dropped": 0, "detail": relative(INPUT_PATH)},
        {
            "step": "has_financial_outcome",
            "status": "complete" if any(row["has_financial_outcome"] for row in feasibility_rows) else "failed",
            "rows": sum(int(row["rows"]) for row in feasibility_rows if int(row["has_financial_outcome"])),
            "dropped": len(df) - sum(int(row["rows"]) for row in feasibility_rows if int(row["has_financial_outcome"])),
            "detail": "At least one financial-protection outcome nonmissing by country-wave.",
        },
        {
            "step": "passes_main_sample_gate",
            "status": "complete" if any(row["passes_main_sample_gate"] for row in feasibility_rows) else "failed",
            "rows": sum(int(row["rows"]) for row in feasibility_rows if int(row["passes_main_sample_gate"])),
            "dropped": len(df) - sum(int(row["rows"]) for row in feasibility_rows if int(row["passes_main_sample_gate"])),
            "detail": "Requires consumption/OOP/weight/time/geography/financial outcome/climate exposure.",
        },
    ]

    write_csv(PREVALENCE_PATH, prevalence_rows, ["country", "survey_name", "wave", "outcome", "rows", "nonmissing", "event_rate", "weighted_prevalence"])
    write_csv(MISSINGNESS_PATH, missingness_rows, ["country", "survey_name", "wave", "variable", "rows", "missing", "missing_rate"])
    write_csv(EXPOSURE_PATH, exposure_rows, ["country", "survey_name", "wave", "exposure", "rows", "nonmissing", "mean", "sd", "min", "p25", "median", "p75", "max"])
    write_csv(SAMPLE_FLOW_PATH, sample_flow, ["step", "status", "rows", "dropped", "detail"])
    write_csv(FEASIBILITY_PATH, feasibility_rows, ["country", "survey_name", "wave", "rows", "has_financial_outcome", "has_access_outcome", "has_climate", "passes_main_sample_gate", "gap"])

    pass_count = sum(int(row["passes_main_sample_gate"]) for row in feasibility_rows)
    audit.extend(
        [
            audit_row("weighted_prevalence", "complete" if prevalence_rows else "blocked_no_outcomes", f"Prevalence rows={len(prevalence_rows)}.", rows_output=len(prevalence_rows), output_path=relative(PREVALENCE_PATH)),
            audit_row("missingness", "complete" if missingness_rows else "blocked_no_variables", f"Missingness rows={len(missingness_rows)}.", rows_output=len(missingness_rows), output_path=relative(MISSINGNESS_PATH)),
            audit_row("climate_summary", "complete" if exposure_rows else "blocked_no_exposures", f"Climate exposure summary rows={len(exposure_rows)}.", rows_output=len(exposure_rows), output_path=relative(EXPOSURE_PATH)),
            audit_row("analysis_sample_gate", "complete" if pass_count else "failed_no_country_wave_passes", f"Country-waves passing main sample gate={pass_count}.", rows_output=pass_count, output_path=relative(FEASIBILITY_PATH)),
        ]
    )
    if limited_diagnostic:
        audit.append(
            audit_row(
                "limited_diagnostic_guardrail",
                "complete_limited_diagnostic_not_promoted",
                "Input is the limited ALB_2002 CHE/NASA POWER linked diagnostic file; outputs are audit diagnostics only.",
                input_path=relative(INPUT_PATH),
                rows_input=len(df),
                required_action="Resolve SDG/access/composite, CHIRPS/ERA5, historical baseline, and geography gates before promoted descriptive analysis.",
            )
        )
    write_csv(AUDIT_PATH, audit, AUDIT_COLUMNS)
    status_text = (
        "complete limited diagnostic only; not promoted for manuscript descriptive claims"
        if limited_diagnostic
        else ("complete for available analytical data" if pass_count else "ran, but no country-wave passed the main analytical gate")
    )
    limitation_text = (
        "\nGuardrail: this uses the limited ALB_2002 CHE10/CHE25 by NASA POWER admin2-centroid diagnostic file. "
        "It does not satisfy SDG 3.8.2, access, composite UHC, primary climate-source, causal, ML, policy, or final-analysis gates.\n"
        if limited_diagnostic
        else ""
    )
    REPORT_PATH.write_text(
        f"""# Descriptive Diagnostics

Status: {status_text}.
{limitation_text}

Input rows: {len(df)}

Weighted prevalence rows: {len(prevalence_rows)}

Missingness rows: {len(missingness_rows)}

Climate exposure summary rows: {len(exposure_rows)}

Country-waves passing the main sample gate: {pass_count}

Outputs:
- `result/descriptive_weighted_prevalence.csv`
- `result/descriptive_missingness.csv`
- `result/descriptive_climate_exposure_summary.csv`
- `result/sample_inclusion_flow.csv`
- `result/analysis_sample_feasibility.csv`
""",
        encoding="utf-8",
    )
    append_log(TEMP_DIR / "audit_log.md", f"Descriptive diagnostics wrote prevalence rows={len(prevalence_rows)} and pass_count={pass_count}.")
    print(f"Descriptive diagnostics wrote prevalence rows={len(prevalence_rows)} and pass_count={pass_count}.")


if __name__ == "__main__":
    main()
