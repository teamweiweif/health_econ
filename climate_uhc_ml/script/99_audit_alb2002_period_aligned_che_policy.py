from __future__ import annotations

import csv
import math
from pathlib import Path
from typing import Any

import pandas as pd

from common import REPORT_DIR, RESULT_DIR, TEMP_DIR, append_log, ensure_dirs, write_csv


IDNO = "ALB_2002_LSMS_v01_M"
COUNTRY = "Albania"
SURVEY_NAME = "Living Standards Measurement Survey 2002"
WAVE = "2002"

CANDIDATE_PATH = TEMP_DIR / "alb2002_household_core_candidate.csv"
AGGREGATE_AUDIT_PATH = TEMP_DIR / "alb2002_consumption_aggregate_metadata_crosswalk_audit.csv"
AGGREGATE_SUMMARY_PATH = RESULT_DIR / "alb2002_consumption_aggregate_metadata_crosswalk_summary.csv"
OOP_POLICY_SUMMARY_PATH = RESULT_DIR / "alb2002_oop_aggregation_policy_summary.csv"
OOP_SKIP_SUMMARY_PATH = RESULT_DIR / "alb2002_oop_skip_value_decision_summary.csv"
CROSSWALK_SUMMARY_PATH = RESULT_DIR / "alb2002_district_climate_crosswalk_summary.csv"

AUDIT_PATH = TEMP_DIR / "alb2002_period_aligned_che_policy_audit.csv"
SUMMARY_PATH = RESULT_DIR / "alb2002_period_aligned_che_policy_summary.csv"
REPORT_PATH = REPORT_DIR / "alb2002_period_aligned_che_policy_audit.md"

DECISION = "blocked_alb2002_period_aligned_che_policy_not_outcome_ready"
NO_PROMOTION = "not_promoted_period_aligned_che_stress_test_only"

AUDIT_COLUMNS = [
    "country",
    "survey_name",
    "wave",
    "idno",
    "policy_name",
    "denominator_period",
    "numerator_period_alignment",
    "source_oop_policy",
    "formula",
    "household_rows",
    "denominator_rows",
    "positive_oop_rows",
    "positive_oop_rate",
    "weighted_denominator",
    "weighted_positive_oop_rate",
    "mean_oop_monthly_equivalent",
    "p50_oop_monthly_equivalent",
    "p95_oop_monthly_equivalent",
    "max_oop_monthly_equivalent",
    "mean_oop_share",
    "p50_oop_share",
    "p95_oop_share",
    "max_oop_share",
    "che10_rows",
    "che10_rate",
    "che10_weighted_rate",
    "che25_rows",
    "che25_rate",
    "che25_weighted_rate",
    "denominator_documented_candidate",
    "zero_skip_decision_ready",
    "period_alignment_ready",
    "ready_for_outcome",
    "ready_for_recipe",
    "sdg382_ready",
    "climate_linkage_ready",
    "promotion_status",
    "blocking_reason",
    "next_action",
]
SUMMARY_COLUMNS = ["metric", "value", "interpretation"]


def read_csv_dicts(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        return []
    with path.open(encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def metric_value(rows: list[dict[str, str]], metric: str, default: str = "0") -> str:
    return next((row.get("value", default) for row in rows if row.get("metric") == metric), default)


def safe_int(value: Any) -> int:
    try:
        return int(float(str(value).strip()))
    except (TypeError, ValueError):
        return 0


def fmt(value: Any) -> str:
    if value is None:
        return ""
    try:
        if pd.isna(value):
            return ""
    except TypeError:
        pass
    try:
        number = float(value)
    except (TypeError, ValueError):
        return str(value)
    if not math.isfinite(number):
        return ""
    if number.is_integer():
        return str(int(number))
    return f"{number:.6g}"


def numeric(series: pd.Series) -> pd.Series:
    return pd.to_numeric(series, errors="coerce")


def quantiles(series: pd.Series) -> dict[str, str]:
    valid = numeric(series).replace([float("inf"), float("-inf")], pd.NA).dropna()
    if valid.empty:
        return {"mean": "", "p50": "", "p95": "", "max": ""}
    return {
        "mean": fmt(float(valid.mean())),
        "p50": fmt(float(valid.quantile(0.50))),
        "p95": fmt(float(valid.quantile(0.95))),
        "max": fmt(float(valid.max())),
    }


def weighted_rate(event: pd.Series, denominator: pd.Series, weight: pd.Series) -> str:
    valid = denominator.fillna(False).astype(bool) & weight.notna() & (weight > 0)
    if not valid.any():
        return ""
    denominator_weight = float(weight.loc[valid].sum())
    if denominator_weight <= 0:
        return ""
    numerator_weight = float(weight.loc[valid & event.fillna(False).astype(bool)].sum())
    return fmt(numerator_weight / denominator_weight)


def monthly_denominator_documented(aggregate_rows: list[dict[str, str]], aggregate_summary: list[dict[str, str]]) -> int:
    total_rows = [
        row
        for row in aggregate_rows
        if row.get("source_variable") == "totcons"
        and row.get("readiness_status") == "local_totcons_documented_as_public_totcons3_total_budget_candidate"
    ]
    period_monthly = any("monthly" in row.get("period_evidence", "").lower() for row in total_rows)
    documentation_ready = safe_int(metric_value(aggregate_summary, "alb2002_consumption_aggregate_crosswalk_official_documentation_ready_rows")) > 0
    denominator_variant_ready = safe_int(metric_value(aggregate_summary, "alb2002_consumption_aggregate_crosswalk_denominator_variant_ready_rows")) > 0
    return int(bool(total_rows) and period_monthly and documentation_ready and denominator_variant_ready)


def build_policy_row(
    policy_name: str,
    numerator_alignment: str,
    source_oop_policy: str,
    formula: str,
    oop: pd.Series,
    total: pd.Series,
    weight: pd.Series,
    denominator_documented: int,
    zero_skip_ready: int,
    climate_ready: int,
) -> dict[str, str]:
    denominator = total.notna() & (total > 0)
    oop_clean = numeric(oop).fillna(0)
    share = oop_clean / total
    positive = denominator & (oop_clean > 0)
    che10 = denominator & (share > 0.10)
    che25 = denominator & (share > 0.25)
    oop_stats = quantiles(oop_clean.loc[denominator])
    share_stats = quantiles(share.loc[denominator])
    period_alignment_ready = int(denominator_documented == 1 and zero_skip_ready > 0)
    return {
        "country": COUNTRY,
        "survey_name": SURVEY_NAME,
        "wave": WAVE,
        "idno": IDNO,
        "policy_name": policy_name,
        "denominator_period": "monthly_total_budget_candidate_totcons",
        "numerator_period_alignment": numerator_alignment,
        "source_oop_policy": source_oop_policy,
        "formula": formula,
        "household_rows": str(int(total.shape[0])),
        "denominator_rows": str(int(denominator.sum())),
        "positive_oop_rows": str(int(positive.sum())),
        "positive_oop_rate": fmt(float(positive.sum() / denominator.sum())) if denominator.any() else "",
        "weighted_denominator": fmt(float(weight.loc[denominator & weight.notna() & (weight > 0)].sum())) if denominator.any() else "0",
        "weighted_positive_oop_rate": weighted_rate(positive, denominator, weight),
        "mean_oop_monthly_equivalent": oop_stats["mean"],
        "p50_oop_monthly_equivalent": oop_stats["p50"],
        "p95_oop_monthly_equivalent": oop_stats["p95"],
        "max_oop_monthly_equivalent": oop_stats["max"],
        "mean_oop_share": share_stats["mean"],
        "p50_oop_share": share_stats["p50"],
        "p95_oop_share": share_stats["p95"],
        "max_oop_share": share_stats["max"],
        "che10_rows": str(int(che10.sum())),
        "che10_rate": fmt(float(che10.sum() / denominator.sum())) if denominator.any() else "",
        "che10_weighted_rate": weighted_rate(che10, denominator, weight),
        "che25_rows": str(int(che25.sum())),
        "che25_rate": fmt(float(che25.sum() / denominator.sum())) if denominator.any() else "",
        "che25_weighted_rate": weighted_rate(che25, denominator, weight),
        "denominator_documented_candidate": str(denominator_documented),
        "zero_skip_decision_ready": str(zero_skip_ready),
        "period_alignment_ready": str(period_alignment_ready),
        "ready_for_outcome": "0",
        "ready_for_recipe": "0",
        "sdg382_ready": "0",
        "climate_linkage_ready": str(climate_ready),
        "promotion_status": NO_PROMOTION,
        "blocking_reason": (
            "Period-aligned CHE stress tests now compare monthly-equivalent OOP candidates with the documented monthly "
            "total-budget denominator, but final outcome promotion still requires an explicit OOP inclusion policy, "
            "benchmark validation, recipe promotion, and climate geography remains blocked."
        ),
        "next_action": (
            "Use these monthly-equivalent rates to choose a single OOP numerator policy; do not write household outcomes "
            "to data/ until the numerator, denominator, recipe, and geography gates pass."
        ),
    }


def build_rows() -> list[dict[str, str]]:
    candidate = pd.read_csv(CANDIDATE_PATH)
    aggregate_rows = read_csv_dicts(AGGREGATE_AUDIT_PATH)
    aggregate_summary = read_csv_dicts(AGGREGATE_SUMMARY_PATH)
    oop_policy_summary = read_csv_dicts(OOP_POLICY_SUMMARY_PATH)
    skip_summary = read_csv_dicts(OOP_SKIP_SUMMARY_PATH)
    crosswalk_summary = read_csv_dicts(CROSSWALK_SUMMARY_PATH)

    total = numeric(candidate["total_consumption"])
    weight = numeric(candidate["household_weight"])
    oop_4w = numeric(candidate["oop_4w_sum_unreviewed"]).fillna(0)
    oop_12m = numeric(candidate["oop_12m_sum_unreviewed"]).fillna(0)

    denominator_documented = monthly_denominator_documented(aggregate_rows, aggregate_summary)
    zero_skip_ready = safe_int(metric_value(skip_summary, "alb2002_oop_skip_value_zero_skip_policy_ready_rows"))
    climate_ready = safe_int(metric_value(crosswalk_summary, "alb2002_climate_linkage_ready_rows"))
    core_4w_match = safe_int(metric_value(oop_policy_summary, "alb2002_oop_aggregation_policy_core_4w_match_rows"))
    core_12m_match = safe_int(metric_value(oop_policy_summary, "alb2002_oop_aggregation_policy_core_12m_match_rows"))
    if core_4w_match != int(total.shape[0]) or core_12m_match != int(total.shape[0]):
        zero_skip_ready = 0

    return [
        build_policy_row(
            "period_aligned_4w_no_gifts_transport_monthly_equivalent",
            "four_week_oop_scaled_by_13_over_12_to_monthly_equivalent",
            "audited_core_4w_no_gifts_with_transport",
            "oop_4w_sum_unreviewed * 13 / 12",
            oop_4w * (13.0 / 12.0),
            total,
            weight,
            denominator_documented,
            zero_skip_ready,
            climate_ready,
        ),
        build_policy_row(
            "period_aligned_12m_hospital_dentist_monthly_equivalent",
            "twelve_month_hospital_dentist_oop_scaled_by_1_over_12",
            "audited_core_12m_no_gifts_with_transport",
            "oop_12m_sum_unreviewed / 12",
            oop_12m / 12.0,
            total,
            weight,
            denominator_documented,
            zero_skip_ready,
            climate_ready,
        ),
        build_policy_row(
            "period_aligned_combined_no_gifts_transport_monthly_equivalent",
            "four_week_oop_scaled_by_13_over_12_plus_twelve_month_hospital_dentist_scaled_by_1_over_12",
            "audited_core_4w_and_12m_no_gifts_with_transport",
            "(oop_4w_sum_unreviewed * 13 / 12) + (oop_12m_sum_unreviewed / 12)",
            (oop_4w * (13.0 / 12.0)) + (oop_12m / 12.0),
            total,
            weight,
            denominator_documented,
            zero_skip_ready,
            climate_ready,
        ),
    ]


def summary_row(metric: str, value: Any, interpretation: str) -> dict[str, str]:
    return {"metric": metric, "value": str(value), "interpretation": interpretation}


def build_summary(rows: list[dict[str, str]]) -> list[dict[str, str]]:
    combined = next((row for row in rows if row["policy_name"] == "period_aligned_combined_no_gifts_transport_monthly_equivalent"), {})
    return [
        summary_row("alb2002_period_aligned_che_policy_rows", len(rows), "Period-aligned ALB_2002 CHE stress-test policies."),
        summary_row("alb2002_period_aligned_che_household_rows", combined.get("household_rows", "0"), "Household rows evaluated by the period-aligned CHE audit."),
        summary_row("alb2002_period_aligned_che_denominator_rows", combined.get("denominator_rows", "0"), "Rows with positive documented total-budget denominator candidate."),
        summary_row("alb2002_period_aligned_che_denominator_documented_rows", sum(safe_int(row["denominator_documented_candidate"]) for row in rows), "Rows where the monthly total-budget denominator evidence is documented for this policy row."),
        summary_row("alb2002_period_aligned_che_zero_skip_ready_rows", max((safe_int(row["zero_skip_decision_ready"]) for row in rows), default=0), "Existing narrow zero-skipped-payment decision rows carried into this audit."),
        summary_row("alb2002_period_aligned_che_period_alignment_ready_rows", sum(safe_int(row["period_alignment_ready"]) for row in rows), "Policy rows with denominator period and no-positive-leakage skip evidence ready for stress testing."),
        summary_row("alb2002_period_aligned_che_combined_che10_rows", combined.get("che10_rows", "0"), "CHE10 rows under the combined monthly-equivalent no-gifts-with-transport policy."),
        summary_row("alb2002_period_aligned_che_combined_che10_rate", combined.get("che10_rate", ""), "Unweighted CHE10 rate under the combined monthly-equivalent no-gifts-with-transport policy."),
        summary_row("alb2002_period_aligned_che_combined_che10_weighted_rate", combined.get("che10_weighted_rate", ""), "Weighted CHE10 rate under the combined monthly-equivalent no-gifts-with-transport policy."),
        summary_row("alb2002_period_aligned_che_combined_che25_rows", combined.get("che25_rows", "0"), "CHE25 rows under the combined monthly-equivalent no-gifts-with-transport policy."),
        summary_row("alb2002_period_aligned_che_combined_che25_rate", combined.get("che25_rate", ""), "Unweighted CHE25 rate under the combined monthly-equivalent no-gifts-with-transport policy."),
        summary_row("alb2002_period_aligned_che_combined_che25_weighted_rate", combined.get("che25_weighted_rate", ""), "Weighted CHE25 rate under the combined monthly-equivalent no-gifts-with-transport policy."),
        summary_row("alb2002_period_aligned_che_outcome_ready_rows", sum(safe_int(row["ready_for_outcome"]) for row in rows), "Rows promoted to final household outcomes by this audit; intentionally zero."),
        summary_row("alb2002_period_aligned_che_recipe_ready_rows", sum(safe_int(row["ready_for_recipe"]) for row in rows), "Rows promoted to harmonized recipe status by this audit; intentionally zero."),
        summary_row("alb2002_period_aligned_che_sdg382_ready_rows", sum(safe_int(row["sdg382_ready"]) for row in rows), "Rows promoted to SDG 3.8.2 status by this audit; intentionally zero."),
        summary_row("alb2002_period_aligned_che_climate_linkage_ready_rows", sum(safe_int(row["climate_linkage_ready"]) for row in rows), "Rows ready for climate linkage by this audit; intentionally zero."),
        summary_row("alb2002_period_aligned_che_current_decision", DECISION, "Current fail-closed decision for ALB_2002 period-aligned CHE policy."),
    ]


def markdown_rows(rows: list[dict[str, str]], columns: list[str]) -> str:
    lines = ["| " + " | ".join(columns) + " |", "|" + "|".join("---" for _ in columns) + "|"]
    for row in rows:
        values = []
        for column in columns:
            value = (row.get(column, "") or "").replace("|", "/")
            if len(value) > 120:
                value = value[:117] + "..."
            values.append(value)
        lines.append("| " + " | ".join(values) + " |")
    return "\n".join(lines)


def write_report(rows: list[dict[str, str]], summary: list[dict[str, str]]) -> None:
    summary_table = "\n".join(f"| {row['metric']} | {row['value']} | {row['interpretation']} |" for row in summary)
    REPORT_PATH.write_text(
        f"""# ALB_2002 Period-Aligned CHE Policy Audit

Status: fail-closed period-aligned CHE stress test. This audit compares monthly-equivalent OOP numerator candidates with the documented monthly total-budget denominator candidate (`totcons`) but does not promote household outcomes.

## Summary

| Metric | Value | Interpretation |
|---|---:|---|
{summary_table}

## Policy Rows

{markdown_rows(rows, ['policy_name', 'numerator_period_alignment', 'positive_oop_rows', 'che10_rows', 'che10_rate', 'che10_weighted_rate', 'che25_rows', 'che25_rate', 'che25_weighted_rate', 'period_alignment_ready', 'ready_for_outcome'])}

## Interpretation

- The denominator audit documents local `totcons` as the public `totcons3` monthly total-budget candidate.
- The OOP aggregation audit verifies that the existing four-week and twelve-month core OOP sums match the no-gifts-with-transport reconstruction for all household rows.
- This audit corrects the period comparison for stress testing: four-week OOP is scaled by `13/12`, and twelve-month hospital/dentist OOP is scaled by `1/12`.
- These remain stress tests. The audit writes no `data/` files and promotes zero recipe, outcome, SDG 3.8.2, or climate-linkage rows.

## Machine-Readable Outputs

- `temp/alb2002_period_aligned_che_policy_audit.csv`
- `result/alb2002_period_aligned_che_policy_summary.csv`
""",
        encoding="utf-8",
    )


def main() -> None:
    ensure_dirs()
    rows = build_rows()
    summary = build_summary(rows)
    write_csv(AUDIT_PATH, rows, AUDIT_COLUMNS)
    write_csv(SUMMARY_PATH, summary, SUMMARY_COLUMNS)
    write_report(rows, summary)
    append_log(TEMP_DIR / "audit_log.md", f"Built ALB_2002 period-aligned CHE policy audit policies={len(rows)} decision={DECISION}.")
    print(f"ALB_2002 period-aligned CHE policy audit policies={len(rows)} decision={DECISION}.")


if __name__ == "__main__":
    main()
