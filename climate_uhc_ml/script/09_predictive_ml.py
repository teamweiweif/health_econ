from __future__ import annotations

from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

from common import DATA_DIR, REPORT_DIR, RESULT_DIR, TEMP_DIR, append_log, ensure_dirs, write_csv


INPUT_PATH = DATA_DIR / "climate_linked_household.csv"
AUDIT_PATH = RESULT_DIR / "predictive_ml_audit.csv"
METRICS_PATH = RESULT_DIR / "predictive_ml_metrics.csv"
FEATURE_PATH = RESULT_DIR / "predictive_ml_feature_manifest.csv"
REPORT_PATH = REPORT_DIR / "predictive_ml_report.md"

AUDIT_COLUMNS = ["check", "status", "detail", "input_path", "rows_input", "rows_output", "output_path", "required_action"]
METRIC_COLUMNS = ["target", "model", "validation", "fold", "train_rows", "test_rows", "event_rate_test", "auroc", "auprc", "brier", "calibration_intercept", "calibration_slope", "notes"]
FEATURE_COLUMNS = ["target", "feature", "feature_type", "missing_rate", "n_unique", "included"]

TARGETS = [
    "uhc_double_failure",
    "sdg382_discretionary_40",
    "che10_total_budget",
    "che25_total_budget",
    "forgone_care_conditional_need",
    "forgone_care_cost_barrier",
]
LEAKY_OR_POST_OUTCOME_PREFIXES = ("sdg382_", "che", "forgone_", "uhc_", "financial_", "access_", "both_", "coping_failure")
SAFE_CANDIDATES = [
    "survey_year",
    "survey_month",
    "rural",
    "household_size",
    "children_under_5",
    "children_under_15",
    "elderly_60_plus",
    "elderly_65_plus",
    "hh_head_sex",
    "hh_head_age",
    "hh_head_education",
    "asset_index",
    "health_insurance",
    "food_insecurity",
    "agriculture_livelihood",
    "admin1",
    "admin2",
    "country",
    "wave",
]
CLIMATE_TOKENS = ["precip", "temp", "rainfall", "heat", "drought", "spei", "water", "exposure"]
LIMITED_LINKED_DATA_USE_LIMIT = "climate_linked_che_diagnostic_only_not_for_promoted_descriptive_ml_causal_or_policy_analysis"


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
    write_csv(METRICS_PATH, [], METRIC_COLUMNS)
    write_csv(FEATURE_PATH, [], FEATURE_COLUMNS)


def write_blocked(status: str, detail: str, action: str) -> None:
    write_empty_outputs()
    write_csv(
        AUDIT_PATH,
        [audit_row("predictive_ml_inputs", status, detail, input_path=relative(INPUT_PATH), required_action=action)],
        AUDIT_COLUMNS,
    )
    REPORT_PATH.write_text(
        f"""# Predictive ML Report

Status: blocked.

Reason: {detail}

Required action: {action}
""",
        encoding="utf-8",
    )
    append_log(TEMP_DIR / "audit_log.md", f"Predictive ML blocked: {status} - {detail}")
    print(f"Predictive ML blocked: {detail}")


def is_limited_linked_diagnostic(df: pd.DataFrame) -> bool:
    return "data_use_limit" in df.columns and df["data_use_limit"].astype(str).str.strip().eq(LIMITED_LINKED_DATA_USE_LIMIT).any()


def limited_linked_blocker(df: pd.DataFrame, readiness_column: str) -> str:
    if readiness_column in df.columns:
        ready = pd.to_numeric(df[readiness_column], errors="coerce").fillna(0)
        if int(ready.sum()) == 0:
            return f"All {readiness_column} values are zero."
    return ""


def candidate_features(df: pd.DataFrame, target: str) -> list[str]:
    features = []
    for column in df.columns:
        low = column.lower()
        if column == target:
            continue
        if low in {"hhid", "pid", "interview_date"}:
            continue
        if low.startswith(LEAKY_OR_POST_OUTCOME_PREFIXES):
            continue
        if column in SAFE_CANDIDATES or any(token in low for token in CLIMATE_TOKENS):
            series = df[column]
            observed = series.notna() & (series.astype(str).str.strip() != "")
            if int(observed.sum()) == 0:
                continue
            features.append(column)
    return features


def feature_manifest(df: pd.DataFrame, target: str, features: list[str]) -> list[dict[str, Any]]:
    rows = []
    for feature in features:
        series = df[feature]
        rows.append(
            {
                "target": target,
                "feature": feature,
                "feature_type": "numeric" if pd.api.types.is_numeric_dtype(series) else "categorical",
                "missing_rate": float(series.isna().mean()),
                "n_unique": int(series.nunique(dropna=True)),
                "included": 1,
            }
        )
    return rows


def prepare_xy(df: pd.DataFrame, target: str, features: list[str]):
    from sklearn.compose import ColumnTransformer
    from sklearn.impute import SimpleImputer
    from sklearn.pipeline import Pipeline
    from sklearn.preprocessing import OneHotEncoder, StandardScaler

    sample = df[[target] + features].copy()
    y = pd.to_numeric(sample[target], errors="coerce")
    keep = y.isin([0, 1])
    sample = sample.loc[keep]
    y = y.loc[keep].astype(int)
    numeric_features = [column for column in features if pd.api.types.is_numeric_dtype(sample[column])]
    categorical_features = [column for column in features if column not in numeric_features]
    try:
        encoder = OneHotEncoder(handle_unknown="ignore", sparse_output=False)
    except TypeError:  # scikit-learn < 1.2
        encoder = OneHotEncoder(handle_unknown="ignore", sparse=False)
    preprocessor = ColumnTransformer(
        transformers=[
            ("num", Pipeline([("imputer", SimpleImputer(strategy="median")), ("scaler", StandardScaler())]), numeric_features),
            ("cat", Pipeline([("imputer", SimpleImputer(strategy="most_frequent")), ("encoder", encoder)]), categorical_features),
        ],
        remainder="drop",
    )
    return sample, y, preprocessor


def metrics(y_true: pd.Series, pred: np.ndarray) -> dict[str, Any]:
    from sklearn.metrics import average_precision_score, brier_score_loss, roc_auc_score

    out: dict[str, Any] = {
        "event_rate_test": float(y_true.mean()) if len(y_true) else "",
        "auroc": "",
        "auprc": "",
        "brier": "",
        "calibration_intercept": "",
        "calibration_slope": "",
    }
    if len(y_true) == 0:
        return out
    if y_true.nunique() > 1:
        out["auroc"] = float(roc_auc_score(y_true, pred))
        out["auprc"] = float(average_precision_score(y_true, pred))
    out["brier"] = float(brier_score_loss(y_true, pred))
    clipped = np.clip(pred, 1e-6, 1 - 1e-6)
    logit = np.log(clipped / (1 - clipped))
    if y_true.nunique() > 1 and np.nanstd(logit) > 0:
        try:
            from sklearn.linear_model import LogisticRegression

            calib = LogisticRegression(solver="lbfgs")
            calib.fit(logit.reshape(-1, 1), y_true)
            out["calibration_intercept"] = float(calib.intercept_[0])
            out["calibration_slope"] = float(calib.coef_[0][0])
        except Exception:
            pass
    return out


def model_specs():
    from sklearn.ensemble import GradientBoostingClassifier, RandomForestClassifier
    from sklearn.linear_model import LogisticRegression

    return {
        "logistic_l2": LogisticRegression(max_iter=1000, class_weight="balanced"),
        "random_forest": RandomForestClassifier(n_estimators=200, min_samples_leaf=10, random_state=20260708, class_weight="balanced_subsample"),
        "gradient_boosting": GradientBoostingClassifier(random_state=20260708),
    }


def validation_folds(sample: pd.DataFrame, limited_diagnostic: bool = False) -> list[tuple[str, str, pd.Series]]:
    folds: list[tuple[str, str, pd.Series]] = []
    if "country" in sample.columns and sample["country"].nunique(dropna=True) >= 2:
        for country in sorted(sample["country"].dropna().astype(str).unique()):
            folds.append(("leave_country_out", country, sample["country"].astype(str) == country))
    if "wave" in sample.columns and sample["wave"].nunique(dropna=True) >= 2:
        for wave in sorted(sample["wave"].dropna().astype(str).unique()):
            folds.append(("leave_wave_out", wave, sample["wave"].astype(str) == wave))
    if "survey_year" in sample.columns and pd.to_numeric(sample["survey_year"], errors="coerce").nunique(dropna=True) >= 2:
        years = pd.to_numeric(sample["survey_year"], errors="coerce")
        cutoff = years.median()
        folds.append(("time_split_after_median_year", str(cutoff), years > cutoff))
    group_column = "admin2_code" if "admin2_code" in sample.columns else ("admin2" if "admin2" in sample.columns else "")
    if not folds and limited_diagnostic and group_column:
        codes = sorted(code for code in sample[group_column].dropna().astype(str).str.strip().unique() if code)
        if len(codes) >= 5:
            fold_count = 5
            for fold_id in range(fold_count):
                held_out = {code for idx, code in enumerate(codes) if idx % fold_count == fold_id}
                mask = sample[group_column].astype(str).str.strip().isin(held_out)
                folds.append(("limited_leave_admin2_group_out", f"group_{fold_id + 1}_of_{fold_count}", mask))
    return folds


def run_models(df: pd.DataFrame, limited_diagnostic: bool = False) -> tuple[list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]]]:
    from sklearn.pipeline import Pipeline

    audit: list[dict[str, Any]] = []
    metric_rows: list[dict[str, Any]] = []
    feature_rows: list[dict[str, Any]] = []
    specs = model_specs()
    available_targets = [target for target in TARGETS if target in df.columns and pd.to_numeric(df[target], errors="coerce").isin([0, 1]).sum() > 0]
    if not available_targets:
        return (
            [audit_row("targets", "blocked_no_binary_targets", "No candidate UHC failure target has observed binary values.", input_path=relative(INPUT_PATH), rows_input=len(df), required_action="Construct audited outcomes before predictive ML.")],
            [],
            [],
        )

    for target in available_targets:
        features = candidate_features(df, target)
        if not features:
            audit.append(audit_row("features", "blocked_no_safe_features", f"No safe pre-exposure/pre-outcome candidate features for {target}.", rows_input=len(df), required_action="Verify covariates and climate exposures."))
            continue
        sample, y, preprocessor = prepare_xy(df, target, features)
        feature_rows.extend(feature_manifest(sample, target, features))
        if len(sample) < 200 or y.nunique() < 2 or y.mean() in {0, 1}:
            audit.append(
                audit_row(
                    "target_sample",
                    "blocked_insufficient_target_variation",
                    f"{target}: usable rows={len(sample)}, event_rate={float(y.mean()) if len(y) else ''}.",
                    rows_input=len(df),
                    required_action="Need at least 200 rows and both outcome classes for validation.",
                )
            )
            continue
        folds = validation_folds(sample, limited_diagnostic=limited_diagnostic)
        if not folds:
            audit.append(
                audit_row(
                    "validation_design",
                    "blocked_no_external_validation_split",
                    f"{target}: no leave-country, leave-wave, or time split is available.",
                    rows_input=len(sample),
                    required_action="Need at least two countries, waves, survey years, or a documented limited grouped geography validation design. Random split alone is insufficient.",
                )
            )
            continue
        X = sample[features]
        for validation, fold, test_mask in folds:
            train_mask = ~test_mask
            if train_mask.sum() < 100 or test_mask.sum() < 30 or y.loc[train_mask].nunique() < 2:
                audit.append(
                    audit_row(
                        "validation_fold",
                        "skipped_insufficient_fold",
                        f"{target} {validation}={fold}: train_rows={int(train_mask.sum())}, test_rows={int(test_mask.sum())}.",
                        rows_input=len(sample),
                    )
                )
                continue
            for model_name, estimator in specs.items():
                pipe = Pipeline([("preprocess", preprocessor), ("model", estimator)])
                try:
                    pipe.fit(X.loc[train_mask], y.loc[train_mask])
                    pred = pipe.predict_proba(X.loc[test_mask])[:, 1]
                    row = {
                        "target": target,
                        "model": model_name,
                        "validation": validation,
                        "fold": fold,
                        "train_rows": int(train_mask.sum()),
                        "test_rows": int(test_mask.sum()),
                        "notes": "limited diagnostic grouped geography validation; not transportable or deployable" if limited_diagnostic else "validated on non-random split",
                    }
                    row.update(metrics(y.loc[test_mask], pred))
                    metric_rows.append(row)
                except Exception as exc:
                    audit.append(audit_row("model_fit", "failed_model_error", f"{target} {model_name} {validation}={fold}: {exc}", rows_input=len(sample)))
    if metric_rows:
        audit.append(audit_row("predictive_ml", "complete_limited_diagnostic" if limited_diagnostic else "complete", f"Validated metric rows={len(metric_rows)}.", rows_output=len(metric_rows), output_path=relative(METRICS_PATH)))
    else:
        audit.append(audit_row("predictive_ml", "blocked_no_validated_models", "No model produced a valid non-random validation metric row.", rows_input=len(df), required_action="Resolve target, sample-size, or validation-split blockers."))
    return audit, metric_rows, feature_rows


def main() -> None:
    ensure_dirs()
    if not INPUT_PATH.exists():
        write_blocked(
            "blocked_no_climate_linked_dataset",
            "No climate-linked analytical dataset exists.",
            "Build outcomes and climate-linked household data before predictive ML.",
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
    blocker = "" if limited_diagnostic else limited_linked_blocker(df, "predictive_ml_ready")
    if blocker:
        write_blocked(
            "blocked_limited_climate_linked_not_predictive_ready",
            blocker,
            "Promote a verified multi-country or externally validated analytical linked dataset before predictive ML.",
        )
        return

    try:
        audit, metric_rows, feature_rows = run_models(df, limited_diagnostic=limited_diagnostic)
    except ImportError as exc:
        write_blocked("blocked_missing_sklearn", str(exc), "Install scikit-learn or adjust the model stack.")
        return
    if limited_diagnostic:
        audit.append(
            audit_row(
                "limited_diagnostic_guardrail",
                "complete_limited_predictive_diagnostic_not_promoted",
                "Input is the limited ALB_2002 CHE/NASA POWER linked diagnostic file; predictive metrics are grouped-geography diagnostics only.",
                input_path=relative(INPUT_PATH),
                rows_input=len(df),
                rows_output=len(metric_rows),
                output_path=relative(METRICS_PATH),
                required_action="Use multi-country, multi-wave, or externally validated analytical data before transportable targeting claims.",
            )
        )
    write_csv(AUDIT_PATH, audit, AUDIT_COLUMNS)
    write_csv(METRICS_PATH, metric_rows, METRIC_COLUMNS)
    write_csv(FEATURE_PATH, feature_rows, FEATURE_COLUMNS)
    status = "complete limited diagnostic only; not deployable or transportable" if limited_diagnostic and metric_rows else ("complete" if metric_rows else "blocked")
    validation_rule = (
        "Random split is not accepted; this limited diagnostic uses deterministic grouped admin2 validation because only one country and wave are currently promoted."
        if limited_diagnostic
        else "Random split alone is not accepted; the script uses leave-country-out, leave-wave-out, or time-based splits when available."
    )
    REPORT_PATH.write_text(
        f"""# Predictive ML Report

Status: {status}.

Input rows: {len(df)}

Validated metric rows: {len(metric_rows)}

Feature manifest rows: {len(feature_rows)}

Validation rule: {validation_rule}

Interpretation: {'limited ALB_2002 CHE prediction diagnostic only; do not claim transportable targeting, deployable calibration, causal effects, causal ML, or policy value.' if limited_diagnostic else 'Use only with the validation and identification caveats in the audit.'}

Outputs:
- `result/predictive_ml_audit.csv`
- `result/predictive_ml_metrics.csv`
- `result/predictive_ml_feature_manifest.csv`
""",
        encoding="utf-8",
    )
    append_log(TEMP_DIR / "audit_log.md", f"Predictive ML status={status}; metric rows={len(metric_rows)}.")
    print(f"Predictive ML status={status}; metric rows={len(metric_rows)}.")


if __name__ == "__main__":
    main()
