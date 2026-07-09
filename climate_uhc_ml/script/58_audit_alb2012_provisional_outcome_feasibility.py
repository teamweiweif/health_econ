from __future__ import annotations

import math
from typing import Any

import pandas as pd

from common import REPORT_DIR, RESULT_DIR, TEMP_DIR, append_log, ensure_dirs, write_csv


CORE_PATH = TEMP_DIR / "alb2012_household_core_candidate.csv"
AUDIT_PATH = TEMP_DIR / "alb2012_provisional_outcome_feasibility_audit.csv"
SUMMARY_PATH = RESULT_DIR / "alb2012_provisional_outcome_feasibility_summary.csv"
REPORT_PATH = REPORT_DIR / "alb2012_provisional_outcome_feasibility.md"

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
    "provisional raw-value diagnostic only; OOP recall comparability, SDG discretionary denominator inputs, "
    "units, missing-code semantics, access skip patterns, no interview timing, coarse prefecture/region geography, "
    "no GPS, climate crosswalk, and cross-wave comparability remain unresolved"
)
DECISION = "not_final_outcomes_timing_geography_recall_semantics_blocked"


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
    raw = df[column]
    text = raw.astype(str).str.strip().str.lower()
    numeric = pd.to_numeric(raw, errors="coerce")
    true_tokens = {"1", "1.0", "true", "yes", "y"}
    false_tokens = {"0", "0.0", "false", "no", "n", ""}
    out = pd.Series(pd.NA, index=df.index, dtype="boolean")
    out.loc[text.isin(true_tokens) | numeric.eq(1).fillna(False)] = True
    out.loc[text.isin(false_tokens) | numeric.eq(0).fillna(False)] = False
    return out


def combine_any(series_list: list[pd.Series]) -> pd.Series:
    if not series_list:
        return pd.Series(dtype="boolean")
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


def add_bool_row(rows: list[dict[str, str]], df: pd.DataFrame, family: str, name: str, formula: str, status: str) -> pd.Series:
    value = boolish(df, name)
    rows.append(event_row(df, family, name, "", formula, value.notna(), value, status))
    return value


def build_audit(df: pd.DataFrame) -> list[dict[str, str]]:
    total = num(df, "total_consumption")
    oop_4w = num(df, "oop_4w_sum_unreviewed")
    oop_12m = num(df, "oop_12m_sum_unreviewed")
    oop_4w_zero = oop_4w.fillna(0)
    oop_12m_zero = oop_12m.fillna(0)
    valid_total = total.notna() & (total > 0)

    rows: list[dict[str, str]] = []

    for threshold in [0.10, 0.25]:
        share_4w = oop_4w_zero / total
        rows.append(
            event_row(
                df,
                "financial_stress_test",
                f"oop_4w_unannualized_che{int(threshold * 100)}",
                fmt(threshold),
                f"oop_4w_sum_unreviewed / total_consumption > {threshold:g}",
                valid_total,
                share_4w > threshold,
                "blocked_recall_mismatch_four_week_oop_over_total_consumption",
                share_4w,
            )
        )
        annualized_share_4w = (oop_4w_zero * 13) / total
        rows.append(
            event_row(
                df,
                "financial_stress_test",
                f"oop_4w_annualized_13x_che{int(threshold * 100)}",
                fmt(threshold),
                f"(oop_4w_sum_unreviewed * 13) / total_consumption > {threshold:g}",
                valid_total,
                annualized_share_4w > threshold,
                "stress_test_annualized_four_week_oop_not_final",
                annualized_share_4w,
            )
        )
        share_12m = oop_12m_zero / total
        rows.append(
            event_row(
                df,
                "financial_stress_test",
                f"oop_12m_che{int(threshold * 100)}",
                fmt(threshold),
                f"oop_12m_sum_unreviewed / total_consumption > {threshold:g}",
                valid_total,
                share_12m > threshold,
                "blocked_unreviewed_twelve_month_oop_recall_not_full_oop",
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

    access_series: dict[str, pd.Series] = {}
    for name, formula in [
        ("difficulty_pay_health", "difficulty_pay_health == 1"),
        ("delayed_help_any", "delayed_help_any == 1"),
        ("hospital_referral_not_gone_any", "hospital_referral_not_gone_any == 1"),
        ("delay_reason_cost", "delay_reason_cost == 1"),
        ("delay_reason_distance", "delay_reason_distance == 1"),
        ("not_gone_reason_cost", "not_gone_reason_cost == 1"),
        ("not_gone_reason_distance", "not_gone_reason_distance == 1"),
        ("refused_health_services_any", "refused_health_services_any == 1"),
        ("refused_reason_cost", "refused_reason_cost == 1"),
        ("refused_reason_distance", "refused_reason_distance == 1"),
        ("medicine_discount_cost_barrier", "medicine_discount_cost_barrier == 1"),
    ]:
        access_series[name] = add_bool_row(rows, df, "access_proxy", name, formula, "proxy_skip_pattern_unreviewed_not_final")

    money_raising = add_bool_row(
        rows,
        df,
        "coping_proxy",
        "health_payment_money_raising_any_unreviewed",
        "health_payment_money_raising_any_unreviewed == 1",
        "coping_proxy_unreviewed_not_final",
    )

    delayed_referral_or_refusal = combine_any(
        [
            access_series["delayed_help_any"],
            access_series["hospital_referral_not_gone_any"],
            access_series["refused_health_services_any"],
        ]
    )
    rows.append(
        event_row(
            df,
            "access_proxy",
            "delayed_referral_or_refusal_proxy",
            "",
            "delayed_help_any == 1 OR hospital_referral_not_gone_any == 1 OR refused_health_services_any == 1",
            delayed_referral_or_refusal.notna(),
            delayed_referral_or_refusal,
            "proxy_skip_pattern_unreviewed_not_final",
        )
    )
    cost_barrier = combine_any(
        [
            access_series["delay_reason_cost"],
            access_series["not_gone_reason_cost"],
            access_series["refused_reason_cost"],
            access_series["medicine_discount_cost_barrier"],
        ]
    )
    rows.append(
        event_row(
            df,
            "access_proxy",
            "access_cost_barrier_proxy",
            "",
            "delay_reason_cost == 1 OR not_gone_reason_cost == 1 OR refused_reason_cost == 1 OR medicine_discount_cost_barrier == 1",
            cost_barrier.notna(),
            cost_barrier,
            "proxy_skip_pattern_unreviewed_not_final",
        )
    )
    distance_barrier = combine_any(
        [
            access_series["delay_reason_distance"],
            access_series["not_gone_reason_distance"],
            access_series["refused_reason_distance"],
        ]
    )
    rows.append(
        event_row(
            df,
            "access_proxy",
            "access_distance_barrier_proxy",
            "",
            "delay_reason_distance == 1 OR not_gone_reason_distance == 1 OR refused_reason_distance == 1",
            distance_barrier.notna(),
            distance_barrier,
            "proxy_skip_pattern_unreviewed_not_final",
        )
    )
    affordability_proxy = combine_any([access_series["difficulty_pay_health"], cost_barrier, money_raising])
    rows.append(
        event_row(
            df,
            "access_proxy",
            "access_affordability_or_coping_proxy",
            "",
            "difficulty_pay_health == 1 OR access_cost_barrier_proxy == 1 OR health_payment_money_raising_any_unreviewed == 1",
            affordability_proxy.notna(),
            affordability_proxy,
            "proxy_skip_pattern_and_coping_semantics_unreviewed_not_final",
        )
    )

    need_series = {}
    for name in ["chronic_illness_any", "sudden_illness_4w_any", "health_license_any"]:
        need_series[name] = add_bool_row(rows, df, "need_proxy", name, f"{name} == 1", "need_proxy_unreviewed_not_outcome")

    shock_any = add_bool_row(
        rows,
        df,
        "shock_proxy",
        "shock_any_2008_2012",
        "shock_any_2008_2012 == 1",
        "shock_proxy_unreviewed_not_climate_exposure",
    )

    need_or_shock = combine_any(list(need_series.values()) + [shock_any])
    rows.append(
        event_row(
            df,
            "need_proxy",
            "need_or_shock_proxy",
            "",
            "chronic_illness_any == 1 OR sudden_illness_4w_any == 1 OR health_license_any == 1 OR shock_any_2008_2012 == 1",
            need_or_shock.notna(),
            need_or_shock,
            "need_and_shock_proxy_unreviewed_not_outcome",
        )
    )

    oop12_che10 = (oop_12m_zero / total) > 0.10
    oop12_che25 = (oop_12m_zero / total) > 0.25
    oop4w_ann_che10 = ((oop_4w_zero * 13) / total) > 0.10
    rows.append(
        event_row(
            df,
            "composite_proxy",
            "uhc_proxy_oop12m_che10_or_access_affordability",
            "0.10",
            "oop_12m_sum_unreviewed / total_consumption > 0.10 OR access affordability/coping proxy",
            valid_total,
            oop12_che10 | affordability_proxy.fillna(False),
            "proxy_composite_not_final",
        )
    )
    rows.append(
        event_row(
            df,
            "composite_proxy",
            "uhc_proxy_oop12m_che25_or_access_affordability",
            "0.25",
            "oop_12m_sum_unreviewed / total_consumption > 0.25 OR access affordability/coping proxy",
            valid_total,
            oop12_che25 | affordability_proxy.fillna(False),
            "proxy_composite_not_final",
        )
    )
    rows.append(
        event_row(
            df,
            "composite_proxy",
            "uhc_proxy_oop4w_annualized_che10_or_access_affordability",
            "0.10",
            "(oop_4w_sum_unreviewed * 13) / total_consumption > 0.10 OR access affordability/coping proxy",
            valid_total,
            oop4w_ann_che10 | affordability_proxy.fillna(False),
            "proxy_composite_not_final",
        )
    )
    rows.append(
        event_row(
            df,
            "composite_proxy",
            "uhc_proxy_oop12m_che10_or_distance_barrier",
            "0.10",
            "oop_12m_sum_unreviewed / total_consumption > 0.10 OR distance barrier proxy",
            valid_total,
            oop12_che10 | distance_barrier.fillna(False),
            "proxy_composite_not_final",
        )
    )

    return rows


def build_summary(df: pd.DataFrame, audit_rows: list[dict[str, str]]) -> list[dict[str, str]]:
    total = num(df, "total_consumption")
    weight = num(df, "household_weight")
    prefecture = df["prefecture"].astype(str) if "prefecture" in df.columns else pd.Series("", index=df.index)
    region = df["region"].astype(str) if "region" in df.columns else pd.Series("", index=df.index)
    survey_month = num(df, "survey_month")
    interview_date = df["interview_date"] if "interview_date" in df.columns else pd.Series(pd.NA, index=df.index)
    interview_date_present = interview_date.notna() & interview_date.astype(str).str.strip().str.len().gt(0)
    access_affordability = boolish(df, "difficulty_pay_health")
    distance_barrier = combine_any([boolish(df, "delay_reason_distance"), boolish(df, "not_gone_reason_distance"), boolish(df, "refused_reason_distance")])
    need_any = combine_any([boolish(df, "chronic_illness_any"), boolish(df, "sudden_illness_4w_any"), boolish(df, "health_license_any")])
    rows = [
        summary_row("alb2012_provisional_outcome_audit_rows", len(audit_rows), "Rows in the provisional ALB_2012 outcome feasibility audit."),
        summary_row(
            "alb2012_provisional_financial_stress_test_rows",
            sum(1 for row in audit_rows if row["outcome_family"] == "financial_stress_test"),
            "Financial-protection stress-test rows, none final.",
        ),
        summary_row(
            "alb2012_provisional_access_proxy_rows",
            sum(1 for row in audit_rows if row["outcome_family"] == "access_proxy"),
            "Access proxy rows, none final.",
        ),
        summary_row(
            "alb2012_provisional_need_proxy_rows",
            sum(1 for row in audit_rows if row["outcome_family"] == "need_proxy"),
            "Need proxy rows, none final.",
        ),
        summary_row(
            "alb2012_provisional_coping_proxy_rows",
            sum(1 for row in audit_rows if row["outcome_family"] == "coping_proxy"),
            "Health-payment coping proxy rows, none final.",
        ),
        summary_row(
            "alb2012_provisional_shock_proxy_rows",
            sum(1 for row in audit_rows if row["outcome_family"] == "shock_proxy"),
            "Raw household shock proxy rows, not climate exposure rows.",
        ),
        summary_row(
            "alb2012_provisional_low_event_rate_rows",
            sum(1 for row in audit_rows if row["low_event_rate_flag"] == "1"),
            "Outcome candidates with unweighted event rate below 3 percent.",
        ),
        summary_row("alb2012_provisional_outcome_base_rows", len(df), "Rows in temp/alb2012_household_core_candidate.csv."),
        summary_row("alb2012_provisional_positive_total_consumption_rows", int(((total.notna()) & (total > 0)).sum()), "Rows with positive total_consumption."),
        summary_row("alb2012_provisional_positive_household_weight_rows", int(((weight.notna()) & (weight > 0)).sum()), "Rows with positive household_weight."),
        summary_row(
            "alb2012_provisional_consumption_weight_rows",
            int(((total.notna()) & (total > 0) & (weight.notna()) & (weight > 0)).sum()),
            "Rows with both positive total_consumption and positive household_weight.",
        ),
        summary_row("alb2012_provisional_prefecture_rows", int(prefecture.str.len().gt(0).sum()), "Rows with coarse prefecture field for future geography review."),
        summary_row("alb2012_provisional_region_rows", int(region.str.len().gt(0).sum()), "Rows with coarse region field for future geography review."),
        summary_row("alb2012_provisional_survey_month_rows", int(survey_month.notna().sum()), "Rows with raw survey month for future climate window review."),
        summary_row("alb2012_provisional_interview_date_rows", int(interview_date_present.sum()), "Rows with raw interview date for future climate window review."),
        summary_row("alb2012_provisional_oop_4w_positive_rows", int((num(df, "oop_4w_sum_unreviewed") > 0).sum()), "Rows with positive unreviewed four-week OOP."),
        summary_row("alb2012_provisional_oop_12m_positive_rows", int((num(df, "oop_12m_sum_unreviewed") > 0).sum()), "Rows with positive unreviewed twelve-month OOP."),
        summary_row("alb2012_provisional_access_affordability_proxy_rows", int(access_affordability.fillna(False).sum()), "Rows with difficulty paying health care proxy."),
        summary_row("alb2012_provisional_distance_barrier_proxy_rows", int(distance_barrier.fillna(False).sum()), "Rows with any unreviewed distance-barrier proxy."),
        summary_row("alb2012_provisional_need_signal_rows", int(need_any.fillna(False).sum()), "Rows with any unreviewed health-need proxy."),
        summary_row("alb2012_provisional_outcome_ready_rows", 0, "No provisional ALB_2012 diagnostic row is ready for data/ or outcome promotion."),
        summary_row("alb2012_provisional_climate_linkage_ready_rows", 0, "No ALB_2012 provisional diagnostic row is ready for climate linkage."),
        summary_row("alb2012_provisional_outcome_current_decision", DECISION, "Current fail-closed decision for ALB_2012 provisional outcome feasibility."),
    ]
    return rows


def markdown_rows(rows: list[dict[str, str]], columns: list[str], limit: int = 40) -> str:
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
        f"""# ALB_2012 Provisional Outcome Feasibility Audit

Status: provisional, temp-only, and fail-closed. This audit computes raw event-rate diagnostics from `temp/alb2012_household_core_candidate.csv` to see whether candidate ALB_2012 OOP/access/need fields have nonzero variation. It does not construct final UHC outcomes and does not write any file to `data/`.

## Summary

| Metric | Value | Interpretation |
|---|---:|---|
{summary_table}

## Candidate Diagnostics

{markdown_rows(audit_rows, ['outcome_family', 'outcome_candidate', 'denominator_rows', 'numerator_rows', 'unweighted_rate', 'weighted_rate', 'low_event_rate_flag', 'promotion_status'], 45)}

## Interpretation

- No SDG 3.8.2 outcome is constructed here: discretionary-budget inputs, societal poverty line adjustments, PPP/CPI handling, and official denominator handling are unresolved.
- No final CHE10/CHE25 outcome is constructed here: four-week and twelve-month OOP sums are unreviewed stress tests, not harmonized OOP health expenditure.
- No final forgone-care outcome is constructed here: illness/need, delayed care, referral nonuse, refusal, cost, distance, medicine-discount, and money-raising proxies still require skip-pattern and denominator validation.
- No climate exposure is linked here: ALB_2012 has no observed interview date/month, no GPS, and only coarse prefecture/region geography.
- No descriptive prevalence, causal, ML, or policy-targeting claim can be made from this audit.
- All rows remain `not_ready_provisional_only`; promotion-ready rows are intentionally zero.

## Machine-Readable Outputs

- `temp/alb2012_provisional_outcome_feasibility_audit.csv`
- `result/alb2012_provisional_outcome_feasibility_summary.csv`
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
        f"Built ALB_2012 provisional outcome feasibility audit rows={len(audit_rows)} decision={DECISION}.",
    )
    print(f"ALB_2012 provisional outcome feasibility audit rows={len(audit_rows)} decision={DECISION}.")


if __name__ == "__main__":
    main()
