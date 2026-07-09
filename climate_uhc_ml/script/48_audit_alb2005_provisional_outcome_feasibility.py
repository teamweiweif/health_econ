from __future__ import annotations

import math
from typing import Any

import pandas as pd

from common import REPORT_DIR, RESULT_DIR, TEMP_DIR, append_log, ensure_dirs, write_csv


CORE_PATH = TEMP_DIR / "alb2005_household_core_candidate.csv"
AUDIT_PATH = TEMP_DIR / "alb2005_provisional_outcome_feasibility_audit.csv"
SUMMARY_PATH = RESULT_DIR / "alb2005_provisional_outcome_feasibility_summary.csv"
REPORT_PATH = REPORT_DIR / "alb2005_provisional_outcome_feasibility.md"

AUDIT_COLUMNS = [
    "outcome_family",
    "outcome_candidate",
    "threshold",
    "formula",
    "denominator_rows",
    "numerator_rows",
    "unweighted_rate",
    "weighted_denominator",
    "weighted_numerator",
    "weighted_rate",
    "missing_required_rows",
    "share_mean",
    "share_p50",
    "share_p95",
    "share_max",
    "low_event_rate_flag",
    "recall_or_denominator_status",
    "promotion_status",
    "blocking_reason",
]
SUMMARY_COLUMNS = ["metric", "value", "interpretation"]

BLOCKING_REASON = (
    "provisional raw-value diagnostic only; survey timing, climate geography, OOP recall comparability, "
    "SDG discretionary denominator inputs, units, missing-code semantics, and access skip patterns remain unresolved"
)
DECISION = "not_final_outcomes_timing_geography_recall_blocked"


def fmt(value: Any) -> str:
    if value is None:
        return ""
    try:
        if pd.isna(value):
            return ""
    except TypeError:
        pass
    if isinstance(value, float):
        if not math.isfinite(value):
            return ""
        return f"{value:.6g}"
    return str(value)


def num(df: pd.DataFrame, column: str) -> pd.Series:
    if column not in df.columns:
        return pd.Series(float("nan"), index=df.index)
    return pd.to_numeric(df[column], errors="coerce")


def boolish(df: pd.DataFrame, column: str) -> pd.Series:
    if column not in df.columns:
        return pd.Series(pd.NA, index=df.index, dtype="boolean")
    numeric = pd.to_numeric(df[column], errors="coerce")
    out = numeric == 1
    out[numeric.isna()] = pd.NA
    return out.astype("boolean")


def combine_any(series_list: list[pd.Series]) -> pd.Series:
    if not series_list:
        return pd.Series(pd.NA, dtype="boolean")
    frame = pd.concat(series_list, axis=1)
    return frame.fillna(False).any(axis=1).astype("boolean")


def share_stats(shares: pd.Series) -> dict[str, str]:
    valid = pd.to_numeric(shares, errors="coerce").replace([float("inf"), float("-inf")], pd.NA).dropna()
    if valid.empty:
        return {"share_mean": "", "share_p50": "", "share_p95": "", "share_max": ""}
    return {
        "share_mean": fmt(float(valid.mean())),
        "share_p50": fmt(float(valid.quantile(0.50))),
        "share_p95": fmt(float(valid.quantile(0.95))),
        "share_max": fmt(float(valid.max())),
    }


def event_row(
    df: pd.DataFrame,
    outcome_family: str,
    outcome_candidate: str,
    threshold: str,
    formula: str,
    denominator: pd.Series,
    event: pd.Series,
    status: str,
    shares: pd.Series | None = None,
) -> dict[str, str]:
    weight = num(df, "household_weight")
    valid_den = denominator.fillna(False).astype(bool)
    valid_event = event.fillna(False).astype(bool) & valid_den
    valid_weight = valid_den & weight.notna() & (weight > 0)
    denominator_rows = int(valid_den.sum())
    numerator_rows = int(valid_event.sum())
    weighted_denominator = float(weight.loc[valid_weight].sum()) if valid_weight.any() else 0.0
    weighted_numerator = float(weight.loc[valid_weight & valid_event].sum()) if (valid_weight & valid_event).any() else 0.0
    unweighted_rate = numerator_rows / denominator_rows if denominator_rows else float("nan")
    weighted_rate = weighted_numerator / weighted_denominator if weighted_denominator else float("nan")
    stats = share_stats(shares.loc[valid_den]) if shares is not None else {"share_mean": "", "share_p50": "", "share_p95": "", "share_max": ""}
    return {
        "outcome_family": outcome_family,
        "outcome_candidate": outcome_candidate,
        "threshold": threshold,
        "formula": formula,
        "denominator_rows": str(denominator_rows),
        "numerator_rows": str(numerator_rows),
        "unweighted_rate": fmt(unweighted_rate),
        "weighted_denominator": fmt(weighted_denominator),
        "weighted_numerator": fmt(weighted_numerator),
        "weighted_rate": fmt(weighted_rate),
        "missing_required_rows": str(max(len(df) - denominator_rows, 0)),
        "low_event_rate_flag": "1" if denominator_rows > 0 and unweighted_rate < 0.03 else "0",
        "recall_or_denominator_status": status,
        "promotion_status": "not_ready_provisional_only",
        "blocking_reason": BLOCKING_REASON,
        **stats,
    }


def summary_row(metric: str, value: Any, interpretation: str) -> dict[str, str]:
    return {"metric": metric, "value": fmt(value), "interpretation": interpretation}


def build_audit(df: pd.DataFrame) -> list[dict[str, str]]:
    total = num(df, "total_consumption")
    oop_4w = num(df, "oop_4w_sum_unreviewed").fillna(0)
    oop_12m = num(df, "oop_12m_sum_unreviewed").fillna(0)
    valid_total = total.notna() & (total > 0)

    rows: list[dict[str, str]] = []

    for threshold in [0.10, 0.25]:
        share = oop_4w / total
        rows.append(
            event_row(
                df,
                "financial_stress_test",
                f"oop_4w_unannualized_che{int(threshold * 100)}",
                fmt(threshold),
                f"oop_4w_sum_unreviewed / total_consumption > {threshold:g}",
                valid_total,
                share > threshold,
                "blocked_recall_mismatch_four_week_oop_over_total_consumption",
                share,
            )
        )
        annualized_share = (oop_4w * 13) / total
        rows.append(
            event_row(
                df,
                "financial_stress_test",
                f"oop_4w_annualized_13x_che{int(threshold * 100)}",
                fmt(threshold),
                f"(oop_4w_sum_unreviewed * 13) / total_consumption > {threshold:g}",
                valid_total,
                annualized_share > threshold,
                "stress_test_annualized_four_week_oop_not_final",
                annualized_share,
            )
        )
        share_12m = oop_12m / total
        rows.append(
            event_row(
                df,
                "financial_stress_test",
                f"oop_12m_che{int(threshold * 100)}",
                fmt(threshold),
                f"oop_12m_sum_unreviewed / total_consumption > {threshold:g}",
                valid_total,
                share_12m > threshold,
                "blocked_incomplete_annual_oop_module_not_full_oop",
                share_12m,
            )
        )

    rows.append(
        event_row(
            df,
            "financial_stress_test",
            "oop_any_positive_4w",
            "",
            "oop_4w_sum_unreviewed > 0",
            oop_4w.notna(),
            oop_4w > 0,
            "diagnostic_positive_unreviewed_four_week_oop_not_outcome",
        )
    )
    rows.append(
        event_row(
            df,
            "financial_stress_test",
            "oop_any_positive_12m",
            "",
            "oop_12m_sum_unreviewed > 0",
            oop_12m.notna(),
            oop_12m > 0,
            "diagnostic_positive_unreviewed_twelve_month_oop_not_outcome",
        )
    )

    access_vars = [
        ("difficulty_pay_health", "difficulty_pay_health == 1"),
        ("delayed_help_any", "delayed_help_any == 1"),
        ("hospital_referral_not_gone_any", "hospital_referral_not_gone_any == 1"),
        ("delay_reason_cost", "delay_reason_cost == 1"),
        ("delay_reason_distance", "delay_reason_distance == 1"),
        ("not_gone_reason_cost", "not_gone_reason_cost == 1"),
        ("not_gone_reason_distance", "not_gone_reason_distance == 1"),
    ]
    access_series: dict[str, pd.Series] = {}
    for name, formula in access_vars:
        value = boolish(df, name)
        access_series[name] = value
        rows.append(
            event_row(
                df,
                "access_proxy",
                name,
                "",
                formula,
                value.notna(),
                value,
                "proxy_skip_pattern_unreviewed_not_final",
            )
        )

    delayed_or_referral = combine_any([access_series["delayed_help_any"], access_series["hospital_referral_not_gone_any"]])
    rows.append(
        event_row(
            df,
            "access_proxy",
            "delayed_or_referral_nonuse_proxy",
            "",
            "delayed_help_any == 1 OR hospital_referral_not_gone_any == 1",
            delayed_or_referral.notna(),
            delayed_or_referral,
            "proxy_skip_pattern_unreviewed_not_final",
        )
    )
    cost_barrier = combine_any([access_series["delay_reason_cost"], access_series["not_gone_reason_cost"]])
    rows.append(
        event_row(
            df,
            "access_proxy",
            "access_cost_barrier_proxy",
            "",
            "delay_reason_cost == 1 OR not_gone_reason_cost == 1",
            cost_barrier.notna(),
            cost_barrier,
            "proxy_skip_pattern_unreviewed_not_final",
        )
    )
    distance_barrier = combine_any([access_series["delay_reason_distance"], access_series["not_gone_reason_distance"]])
    rows.append(
        event_row(
            df,
            "access_proxy",
            "access_distance_barrier_proxy",
            "",
            "delay_reason_distance == 1 OR not_gone_reason_distance == 1",
            distance_barrier.notna(),
            distance_barrier,
            "proxy_skip_pattern_unreviewed_not_final",
        )
    )

    for name in ["illness_or_disability_any", "sudden_illness_4w_any"]:
        value = boolish(df, name)
        rows.append(
            event_row(
                df,
                "need_proxy",
                name,
                "",
                f"{name} == 1",
                value.notna(),
                value,
                "need_proxy_unreviewed_not_outcome",
            )
        )

    oop12_che10 = (oop_12m / total) > 0.10
    oop12_che25 = (oop_12m / total) > 0.25
    rows.append(
        event_row(
            df,
            "composite_proxy",
            "uhc_proxy_oop12m_che10_or_access_proxy",
            "0.10",
            "oop_12m_sum_unreviewed / total_consumption > 0.10 OR delayed/referral nonuse proxy",
            valid_total,
            oop12_che10 | delayed_or_referral.fillna(False),
            "proxy_composite_not_final",
        )
    )
    rows.append(
        event_row(
            df,
            "composite_proxy",
            "uhc_proxy_oop12m_che25_or_access_proxy",
            "0.25",
            "oop_12m_sum_unreviewed / total_consumption > 0.25 OR delayed/referral nonuse proxy",
            valid_total,
            oop12_che25 | delayed_or_referral.fillna(False),
            "proxy_composite_not_final",
        )
    )
    rows.append(
        event_row(
            df,
            "composite_proxy",
            "uhc_proxy_oop12m_che10_or_cost_barrier",
            "0.10",
            "oop_12m_sum_unreviewed / total_consumption > 0.10 OR cost barrier proxy",
            valid_total,
            oop12_che10 | cost_barrier.fillna(False),
            "proxy_composite_not_final",
        )
    )

    return rows


def build_summary(df: pd.DataFrame, audit_rows: list[dict[str, str]]) -> list[dict[str, str]]:
    total = num(df, "total_consumption")
    weight = num(df, "household_weight")
    rows = [
        summary_row("alb2005_provisional_outcome_audit_rows", len(audit_rows), "Rows in the provisional ALB_2005 outcome feasibility audit."),
        summary_row(
            "alb2005_provisional_financial_stress_test_rows",
            sum(1 for row in audit_rows if row["outcome_family"] == "financial_stress_test"),
            "Financial-protection stress-test rows, none final.",
        ),
        summary_row(
            "alb2005_provisional_access_proxy_rows",
            sum(1 for row in audit_rows if row["outcome_family"] == "access_proxy"),
            "Access proxy rows, none final.",
        ),
        summary_row(
            "alb2005_provisional_low_event_rate_rows",
            sum(1 for row in audit_rows if row["low_event_rate_flag"] == "1"),
            "Outcome candidates with unweighted event rate below 3 percent.",
        ),
        summary_row("alb2005_provisional_outcome_base_rows", len(df), "Rows in temp/alb2005_household_core_candidate.csv."),
        summary_row("alb2005_provisional_positive_total_consumption_rows", int(((total.notna()) & (total > 0)).sum()), "Rows with positive total_consumption."),
        summary_row("alb2005_provisional_positive_household_weight_rows", int(((weight.notna()) & (weight > 0)).sum()), "Rows with positive household_weight."),
        summary_row(
            "alb2005_provisional_consumption_weight_rows",
            int(((total.notna()) & (total > 0) & (weight.notna()) & (weight > 0)).sum()),
            "Rows with both positive total_consumption and positive household_weight.",
        ),
        summary_row("alb2005_provisional_outcome_ready_rows", 0, "No provisional ALB_2005 diagnostic row is ready for data/ or outcome promotion."),
        summary_row("alb2005_provisional_outcome_current_decision", DECISION, "Current fail-closed decision for ALB_2005 provisional outcome feasibility."),
    ]
    return rows


def markdown_rows(rows: list[dict[str, str]], columns: list[str], limit: int = 24) -> str:
    lines = ["| " + " | ".join(columns) + " |", "|" + "|".join("---" for _ in columns) + "|"]
    for row in rows[:limit]:
        values = []
        for column in columns:
            value = (row.get(column, "") or "").replace("|", "/")
            if len(value) > 100:
                value = value[:97] + "..."
            values.append(value)
        lines.append("| " + " | ".join(values) + " |")
    return "\n".join(lines)


def write_report(audit_rows: list[dict[str, str]], summary_rows: list[dict[str, str]]) -> None:
    summary_table = "\n".join(f"| {row['metric']} | {row['value']} | {row['interpretation']} |" for row in summary_rows)
    REPORT_PATH.write_text(
        f"""# ALB_2005 Provisional Outcome Feasibility Audit

Status: provisional, temp-only, and fail-closed. This audit computes raw event-rate diagnostics from `temp/alb2005_household_core_candidate.csv` to see whether candidate ALB_2005 OOP/access fields have nonzero variation. It does not construct final UHC outcomes and does not write any file to `data/`.

## Summary

| Metric | Value | Interpretation |
|---|---:|---|
{summary_table}

## Candidate Diagnostics

{markdown_rows(audit_rows, ['outcome_family', 'outcome_candidate', 'denominator_rows', 'numerator_rows', 'unweighted_rate', 'weighted_rate', 'low_event_rate_flag', 'promotion_status'], 30)}

## Interpretation

- No SDG 3.8.2 outcome is constructed here: discretionary-budget inputs, societal poverty line adjustments, and official denominator handling are unresolved.
- No final CHE10/CHE25 outcome is constructed here: the four-week and twelve-month OOP sums are unreviewed stress tests, not harmonized OOP health expenditure.
- No climate exposure is linked here: ALB_2005 still lacks verified survey month/date and has only partial district geography with no GPS.
- No causal, ML, descriptive-prevalence, or policy-targeting claim can be made from this audit.
- All rows remain `not_ready_provisional_only`; promotion-ready rows are intentionally zero.

## Machine-Readable Outputs

- `temp/alb2005_provisional_outcome_feasibility_audit.csv`
- `result/alb2005_provisional_outcome_feasibility_summary.csv`
""",
        encoding="utf-8",
    )


def main() -> None:
    ensure_dirs()
    if not CORE_PATH.exists():
        raise FileNotFoundError(f"Missing prerequisite: {CORE_PATH}")
    df = pd.read_csv(CORE_PATH, encoding="utf-8-sig")
    audit_rows = build_audit(df)
    summary_rows = build_summary(df, audit_rows)
    write_csv(AUDIT_PATH, audit_rows, AUDIT_COLUMNS)
    write_csv(SUMMARY_PATH, summary_rows, SUMMARY_COLUMNS)
    write_report(audit_rows, summary_rows)
    append_log(
        TEMP_DIR / "audit_log.md",
        f"Built ALB_2005 provisional outcome feasibility audit rows={len(audit_rows)} decision={DECISION}.",
    )
    print(f"ALB_2005 provisional outcome feasibility audit rows={len(audit_rows)} decision={DECISION}.")


if __name__ == "__main__":
    main()
