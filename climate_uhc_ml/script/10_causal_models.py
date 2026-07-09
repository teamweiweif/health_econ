from __future__ import annotations

import math
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

from common import DATA_DIR, REPORT_DIR, RESULT_DIR, TEMP_DIR, append_log, ensure_dirs, write_csv


INPUT_PATH = DATA_DIR / "climate_linked_household.csv"
AUDIT_PATH = RESULT_DIR / "causal_model_audit.csv"
ESTIMATE_PATH = RESULT_DIR / "reduced_form_estimates.csv"
PLACEBO_PATH = RESULT_DIR / "placebo_readiness_audit.csv"

AUDIT_COLUMNS = ["check", "status", "detail", "input_path", "rows_input", "rows_output", "output_path", "required_action"]
ESTIMATE_COLUMNS = [
    "outcome",
    "exposure",
    "model",
    "rows",
    "clusters",
    "beta",
    "se_hc1",
    "t_stat",
    "p_value_normal",
    "mean_outcome",
    "mean_exposure",
    "fixed_effects",
    "covariates",
    "identification_status",
    "notes",
]
PLACEBO_COLUMNS = ["test", "status", "detail", "required_action"]

OUTCOMES = [
    "uhc_double_failure",
    "sdg382_discretionary_40",
    "che10_total_budget",
    "che25_total_budget",
    "forgone_care_conditional_need",
    "forgone_care_cost_barrier",
]
EXPOSURE_TOKENS = ["drought", "heat", "precip", "rainfall", "temp", "spei"]
LIMITED_LINKED_DATA_USE_LIMIT = "climate_linked_che_diagnostic_only_not_for_promoted_descriptive_ml_causal_or_policy_analysis"
POST_TREATMENT_CANDIDATES = {
    "total_consumption",
    "total_income",
    "food_consumption",
    "nonfood_consumption",
    "oop_health_expenditure",
    "illness_or_injury_need",
    "care_sought",
    "care_not_sought",
    "coping_borrowed",
    "coping_sold_assets",
    "food_insecurity",
}
BASELINE_COVARIATES = [
    "rural",
    "household_size",
    "children_under_5",
    "children_under_15",
    "elderly_60_plus",
    "elderly_65_plus",
    "hh_head_age",
    "hh_head_sex",
    "hh_head_education",
    "asset_index",
    "health_insurance",
    "agriculture_livelihood",
]
FE_CANDIDATES = ["country", "wave", "survey_month", "admin1"]
LIMITED_DIAGNOSTIC_FE_CANDIDATES = ["admin2", "survey_month"]


def relative(path: Path) -> str:
    try:
        return str(path.relative_to(TEMP_DIR.parent))
    except ValueError:
        return str(path)


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


def write_empty_outputs() -> None:
    write_csv(ESTIMATE_PATH, [], ESTIMATE_COLUMNS)
    write_csv(PLACEBO_PATH, [], PLACEBO_COLUMNS)


def write_blocked(status: str, detail: str, action: str) -> None:
    write_empty_outputs()
    write_csv(AUDIT_PATH, [audit_row("causal_inputs", status, detail, input_path=relative(INPUT_PATH), required_action=action)], AUDIT_COLUMNS)
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    append_log(TEMP_DIR / "audit_log.md", f"Reduced-form models blocked: {status} - {detail}")
    print(f"Reduced-form models blocked: {detail}")


def is_limited_linked_diagnostic(df: pd.DataFrame) -> bool:
    return "data_use_limit" in df.columns and df["data_use_limit"].astype(str).str.strip().eq(LIMITED_LINKED_DATA_USE_LIMIT).any()


def limited_linked_blocker(df: pd.DataFrame, readiness_column: str) -> str:
    if readiness_column in df.columns:
        ready = pd.to_numeric(df[readiness_column], errors="coerce").fillna(0)
        if int(ready.sum()) == 0:
            return f"All {readiness_column} values are zero."
    return ""


def exposure_columns(df: pd.DataFrame) -> list[str]:
    out = []
    for column in df.columns:
        low = column.lower()
        if any(token in low for token in EXPOSURE_TOKENS) and not low.startswith("future_"):
            values = pd.to_numeric(df[column], errors="coerce")
            if values.notna().sum() > 0 and values.nunique(dropna=True) > 1:
                out.append(column)
    return out


def eligible_outcomes(df: pd.DataFrame) -> list[str]:
    out = []
    for column in OUTCOMES:
        if column not in df.columns:
            continue
        values = pd.to_numeric(df[column], errors="coerce")
        if values.isin([0, 1]).sum() > 0 and values.nunique(dropna=True) > 1:
            out.append(column)
    return out


def usable_columns(df: pd.DataFrame, candidates: list[str], max_categories: int = 50) -> list[str]:
    out = []
    for column in candidates:
        if column not in df.columns or column in POST_TREATMENT_CANDIDATES:
            continue
        if df[column].notna().sum() == 0:
            continue
        if not pd.api.types.is_numeric_dtype(df[column]) and df[column].nunique(dropna=True) > max_categories:
            continue
        out.append(column)
    return out


def estimation_samples(df: pd.DataFrame, limited_diagnostic: bool) -> list[tuple[pd.DataFrame, str, str]]:
    if limited_diagnostic and "window_months" in df.columns:
        windows = pd.to_numeric(df["window_months"], errors="coerce")
        out = []
        for window in sorted(windows.dropna().unique()):
            window_value = int(window) if float(window).is_integer() else float(window)
            subset = df.loc[windows == window].copy()
            out.append((subset, f"window_{window_value}m", f"window_months={window_value}"))
        if out:
            return out
    return [(df, "pooled", "pooled sample")]


def build_design(df: pd.DataFrame, outcome: str, exposure: str, *, limited_diagnostic: bool = False) -> tuple[pd.Series, pd.DataFrame, list[str], list[str]]:
    covariates = usable_columns(df, BASELINE_COVARIATES)
    fixed_effect_candidates = LIMITED_DIAGNOSTIC_FE_CANDIDATES if limited_diagnostic else FE_CANDIDATES
    fixed_effects = usable_columns(df, fixed_effect_candidates, max_categories=100)
    columns = [outcome, exposure] + covariates + fixed_effects
    sample = df[columns].copy()
    sample[outcome] = pd.to_numeric(sample[outcome], errors="coerce")
    sample[exposure] = pd.to_numeric(sample[exposure], errors="coerce")
    sample = sample.dropna(subset=[outcome, exposure])
    y = sample[outcome]
    parts = [pd.Series(1.0, index=sample.index, name="intercept"), sample[exposure].rename(exposure)]
    numeric_covariates = []
    categorical_covariates = []
    for column in covariates:
        values = sample[column]
        if pd.api.types.is_numeric_dtype(values):
            numeric_covariates.append(column)
            parts.append(pd.to_numeric(values, errors="coerce").fillna(values.median() if values.notna().any() else 0).rename(column))
        else:
            categorical_covariates.append(column)
            parts.append(pd.get_dummies(values.astype("string").fillna("missing"), prefix=column, drop_first=True, dtype=float))
    for column in fixed_effects:
        if sample[column].nunique(dropna=True) > 1:
            parts.append(pd.get_dummies(sample[column].astype("string").fillna("missing"), prefix=f"fe_{column}", drop_first=True, dtype=float))
    X = pd.concat(parts, axis=1)
    X = X.loc[:, X.nunique(dropna=False) > 1]
    if "intercept" not in X.columns:
        X.insert(0, "intercept", 1.0)
    return y, X.astype(float), covariates, fixed_effects


def normal_p_value(t_stat: float) -> float:
    return float(math.erfc(abs(t_stat) / math.sqrt(2)))


def ols_hc1(y: pd.Series, X: pd.DataFrame, exposure: str) -> dict[str, Any] | None:
    if exposure not in X.columns or len(y) <= X.shape[1] + 5:
        return None
    x = X.to_numpy(dtype=float)
    yy = y.to_numpy(dtype=float).reshape(-1, 1)
    try:
        xtx_inv = np.linalg.pinv(x.T @ x)
        beta = xtx_inv @ x.T @ yy
        resid = yy - x @ beta
        n, k = x.shape
        scale = n / max(n - k, 1)
        meat = x.T @ ((resid.flatten() ** 2)[:, None] * x)
        vcov = scale * xtx_inv @ meat @ xtx_inv
        names = list(X.columns)
        idx = names.index(exposure)
        se = float(np.sqrt(max(vcov[idx, idx], 0)))
        b = float(beta[idx, 0])
        t_stat = b / se if se > 0 else np.nan
        return {"beta": b, "se_hc1": se, "t_stat": t_stat, "p_value_normal": normal_p_value(t_stat) if np.isfinite(t_stat) else ""}
    except Exception:
        return None


def placebo_readiness(df: pd.DataFrame) -> list[dict[str, str]]:
    future_exposures = [column for column in df.columns if column.lower().startswith("future_") and any(token in column.lower() for token in EXPOSURE_TOKENS)]
    timing = any(column in df.columns and df[column].notna().sum() > 0 for column in ["interview_date", "survey_month"])
    geography = any(column in df.columns and df[column].notna().sum() > 0 for column in ["latitude", "longitude", "admin1", "admin2", "cluster_id"])
    return [
        {
            "test": "future_climate_lead_placebo",
            "status": "ready" if future_exposures else "not_ready",
            "detail": ";".join(future_exposures) if future_exposures else "No future/lead climate exposure columns exist.",
            "required_action": "" if future_exposures else "Construct future climate lead variables after primary exposure extraction.",
        },
        {
            "test": "seasonality_controls",
            "status": "ready" if timing else "not_ready",
            "detail": "interview_date or survey_month present" if timing else "No verified interview timing column.",
            "required_action": "" if timing else "Verify interview month/date in harmonized microdata.",
        },
        {
            "test": "geography_controls",
            "status": "ready" if geography else "not_ready",
            "detail": "At least one geography field present" if geography else "No verified geography field.",
            "required_action": "" if geography else "Verify admin or coordinate linkage.",
        },
    ]


def run_estimates(df: pd.DataFrame, *, limited_diagnostic: bool = False) -> tuple[list[dict[str, Any]], list[dict[str, Any]], list[dict[str, str]]]:
    outcomes = eligible_outcomes(df)
    exposures = exposure_columns(df)
    audit = []
    estimates = []
    placebos = placebo_readiness(df)
    placebo_ready = all(row["status"] == "ready" for row in placebos)
    if not outcomes:
        audit.append(audit_row("outcomes", "blocked_no_eligible_outcomes", "No binary UHC outcome has variation.", rows_input=len(df), required_action="Construct and audit outcomes before reduced-form estimation."))
    if not exposures:
        audit.append(audit_row("exposures", "blocked_no_exposure_variation", "No climate-shock/exposure column has usable variation.", rows_input=len(df), required_action="Construct climate exposure variables with variation."))
    if not outcomes or not exposures:
        return audit, estimates, placebos

    for sample_df, sample_label, sample_note in estimation_samples(df, limited_diagnostic):
        for outcome in outcomes:
            for exposure in exposures:
                y, X, covariates, fixed_effects = build_design(sample_df, outcome, exposure, limited_diagnostic=limited_diagnostic)
                if len(y) < 100 or y.nunique(dropna=True) < 2 or X[exposure].nunique(dropna=True) < 2:
                    audit.append(audit_row("model_sample", "skipped_insufficient_variation", f"{outcome} on {exposure} {sample_note}: rows={len(y)}.", rows_input=len(sample_df)))
                    continue
                if X.shape[1] > max(80, len(y) // 5):
                    audit.append(audit_row("model_complexity", "skipped_too_many_parameters", f"{outcome} on {exposure} {sample_note}: rows={len(y)}, parameters={X.shape[1]}.", rows_input=len(y)))
                    continue
                result = ols_hc1(y, X, exposure)
                if result is None:
                    audit.append(audit_row("model_fit", "failed_ols", f"{outcome} on {exposure} {sample_note}: model could not be estimated.", rows_input=len(y)))
                    continue
                clusters = sample_df.loc[y.index, "cluster_id"].nunique(dropna=True) if "cluster_id" in sample_df.columns else ""
                estimates.append(
                    {
                        "outcome": outcome,
                        "exposure": exposure,
                        "model": f"linear_probability_ols_hc1_limited_diagnostic_{sample_label}" if limited_diagnostic else "linear_probability_ols_hc1",
                        "rows": len(y),
                        "clusters": clusters,
                        "mean_outcome": float(y.mean()),
                        "mean_exposure": float(pd.to_numeric(sample_df.loc[y.index, exposure], errors="coerce").mean()),
                        "fixed_effects": ";".join(fixed_effects),
                        "covariates": ";".join(covariates),
                        "identification_status": "limited_diagnostic_association_only_not_causal" if limited_diagnostic else ("placebo_ready_not_yet_interpreted" if placebo_ready else "descriptive_association_only_placebo_not_ready"),
                        "notes": (
                            f"Limited ALB_2002 CHE/admin-centroid diagnostic only ({sample_note}); do not describe as causal or policy-ready."
                            if limited_diagnostic
                            else "Do not describe as causal until placebo, seasonality, geography, and robustness checks pass."
                        ),
                        **result,
                    }
                )
    if estimates:
        audit.append(audit_row("reduced_form_estimation", "complete_limited_diagnostic" if limited_diagnostic else "complete", f"Estimate rows={len(estimates)}.", rows_input=len(df), rows_output=len(estimates), output_path=relative(ESTIMATE_PATH)))
        if limited_diagnostic:
            audit.append(
                audit_row(
                    "limited_diagnostic_guardrail",
                    "complete_limited_reduced_form_diagnostic_not_promoted",
                    "Estimates are association diagnostics on the limited ALB_2002 climate-linked file, not causal reduced-form evidence.",
                    rows_input=len(df),
                    rows_output=len(estimates),
                    required_action="Use promoted multi-country outcome/climate data, primary CHIRPS/ERA5 or accepted baseline exposures, and placebo tests before causal interpretation.",
                )
            )
    else:
        audit.append(audit_row("reduced_form_estimation", "blocked_no_estimates", "No outcome-exposure pair passed sample and complexity checks.", rows_input=len(df), required_action="Resolve outcome/exposure variation and design complexity blockers."))
    return audit, estimates, placebos


def main() -> None:
    ensure_dirs()
    if not INPUT_PATH.exists():
        write_blocked(
            "blocked_no_climate_linked_dataset",
            "No climate-linked analytical dataset exists.",
            "Build climate-linked household outcome data before reduced-form models.",
        )
        return
    try:
        df = read_table(INPUT_PATH)
    except Exception as exc:
        write_blocked("failed_input_read", str(exc), "Inspect climate-linked analytical dataset format.")
        return
    if len(df) == 0:
        write_blocked("blocked_empty_dataset", "Climate-linked analytical dataset has zero rows.", "Rebuild upstream analytical data.")
        return
    limited_diagnostic = is_limited_linked_diagnostic(df)
    blocker = "" if limited_diagnostic else limited_linked_blocker(df, "reduced_form_ready")
    if blocker:
        write_blocked(
            "blocked_limited_climate_linked_not_reduced_form_ready",
            blocker,
            "Resolve outcome promotion, primary climate-source/baseline, placebo, and identification gates before reduced-form estimation.",
        )
        return

    audit, estimates, placebos = run_estimates(df, limited_diagnostic=limited_diagnostic)
    write_csv(AUDIT_PATH, audit, AUDIT_COLUMNS)
    write_csv(ESTIMATE_PATH, estimates, ESTIMATE_COLUMNS)
    write_csv(PLACEBO_PATH, placebos, PLACEBO_COLUMNS)
    append_log(TEMP_DIR / "audit_log.md", f"Reduced-form model stage wrote estimates={len(estimates)}.")
    print(f"Reduced-form model stage wrote estimates={len(estimates)}.")


if __name__ == "__main__":
    main()
