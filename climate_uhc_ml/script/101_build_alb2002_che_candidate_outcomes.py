from __future__ import annotations

import csv
import math
from typing import Any

import pandas as pd

from common import REPORT_DIR, RESULT_DIR, TEMP_DIR, append_log, ensure_dirs, write_csv


IDNO = "ALB_2002_LSMS_v01_M"
COUNTRY = "Albania"
SURVEY_NAME = "Living Standards Measurement Survey 2002"
WAVE = "2002"

CANDIDATE_PATH = TEMP_DIR / "alb2002_household_core_candidate.csv"
PERIOD_CHE_SUMMARY_PATH = RESULT_DIR / "alb2002_period_aligned_che_policy_summary.csv"
PERIOD_CHE_AUDIT_PATH = TEMP_DIR / "alb2002_period_aligned_che_policy_audit.csv"
WEIGHT_SUMMARY_PATH = RESULT_DIR / "alb2002_weight_design_evidence_summary.csv"
MINIMUM_RECIPE_SUMMARY_PATH = RESULT_DIR / "alb2002_minimum_recipe_promotion_summary.csv"
CROSSWALK_SUMMARY_PATH = RESULT_DIR / "alb2002_district_climate_crosswalk_summary.csv"

HOUSEHOLD_OUTCOME_PATH = TEMP_DIR / "alb2002_che_candidate_household_outcomes.csv"
LINEAGE_PATH = TEMP_DIR / "alb2002_che_candidate_outcome_lineage.csv"
AUDIT_PATH = RESULT_DIR / "alb2002_che_candidate_outcome_audit.csv"
SUMMARY_PATH = RESULT_DIR / "alb2002_che_candidate_outcome_summary.csv"
REPORT_PATH = REPORT_DIR / "alb2002_che_candidate_outcome_audit.md"

DECISION = "blocked_alb2002_che_candidate_not_promoted_due_recipe_sdg_climate_gates"
PROMOTION_STATUS = "temp_only_candidate_outcomes_not_promoted"

POLICY_NAME = "period_aligned_combined_no_gifts_transport_monthly_equivalent"

HOUSEHOLD_COLUMNS = [
    "country",
    "survey_name",
    "wave",
    "idno",
    "hhid",
    "survey_year",
    "survey_month",
    "interview_date",
    "psu",
    "stratum",
    "district_code",
    "district_name",
    "urban_rural_code",
    "household_weight",
    "total_consumption_monthly_candidate",
    "oop_4w_monthly_equivalent",
    "oop_12m_monthly_equivalent",
    "oop_combined_monthly_equivalent",
    "oop_share_total_budget_candidate",
    "che10_total_budget_candidate",
    "che25_total_budget_candidate",
    "positive_oop_candidate",
    "denominator_valid",
    "outcome_missing",
    "candidate_policy_name",
    "candidate_formula",
    "outcome_quality_flag",
    "promotion_status",
    "blocking_reason",
]

LINEAGE_COLUMNS = [
    "lineage_id",
    "derived_field",
    "source_fields",
    "source_artifacts",
    "formula_or_rule",
    "status",
    "blocking_reason",
]

AUDIT_COLUMNS = [
    "outcome_id",
    "outcome_label",
    "policy_name",
    "household_rows",
    "denominator_rows",
    "missing_rows",
    "event_rows",
    "event_rate",
    "weighted_event_rate",
    "low_event_rate_flag",
    "mean_value",
    "p50_value",
    "p95_value",
    "max_value",
    "ready_for_outcome",
    "ready_for_recipe",
    "sdg382_ready",
    "climate_linkage_ready",
    "promotion_status",
    "blocking_reason",
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


def safe_int(value: Any) -> int:
    number = safe_float(value)
    if math.isnan(number):
        return 0
    return int(number)


def fmt(value: Any) -> str:
    number = safe_float(value)
    if math.isnan(number):
        return "" if value is None else str(value)
    if number.is_integer():
        return str(int(number))
    return f"{number:.6g}"


def numeric(series: pd.Series) -> pd.Series:
    return pd.to_numeric(series, errors="coerce")


def weighted_rate(event: pd.Series, denominator: pd.Series, weight: pd.Series) -> str:
    valid = denominator.fillna(False).astype(bool) & weight.notna() & (weight > 0)
    if not valid.any():
        return ""
    total_weight = float(weight.loc[valid].sum())
    if total_weight <= 0:
        return ""
    event_weight = float(weight.loc[valid & event.fillna(False).astype(bool)].sum())
    return fmt(event_weight / total_weight)


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


def blocking_reason() -> str:
    return (
        "Household-level CHE10/CHE25 candidate outcomes are constructed from the period-aligned combined "
        "no-gifts-with-transport OOP numerator and documented monthly total-budget candidate denominator, "
        "but they remain temp-only because the minimum recipe, SDG 3.8.2 denominator, external benchmark, "
        "and climate-geography promotion gates are not resolved."
    )


def build_household_outcomes(candidate: pd.DataFrame) -> pd.DataFrame:
    total = numeric(candidate["total_consumption"])
    oop_4w = numeric(candidate["oop_4w_sum_unreviewed"]).fillna(0) * (13.0 / 12.0)
    oop_12m = numeric(candidate["oop_12m_sum_unreviewed"]).fillna(0) / 12.0
    oop_combined = oop_4w + oop_12m
    denominator = total.notna() & (total > 0)
    share = oop_combined / total
    che10 = denominator & (share > 0.10)
    che25 = denominator & (share > 0.25)
    positive_oop = denominator & (oop_combined > 0)
    missing = ~denominator

    out = pd.DataFrame(
        {
            "country": candidate["country"],
            "survey_name": candidate["survey_name"],
            "wave": candidate["wave"],
            "idno": candidate["idno"],
            "hhid": candidate["hhid"],
            "survey_year": candidate["survey_year"],
            "survey_month": candidate["survey_month"],
            "interview_date": candidate["interview_date"],
            "psu": candidate["psu"],
            "stratum": candidate["stratum"],
            "district_code": candidate["district_code_identification"],
            "district_name": candidate["district_name_identification"],
            "urban_rural_code": candidate["urban_rural_code_identification"],
            "household_weight": candidate["household_weight"],
            "total_consumption_monthly_candidate": total,
            "oop_4w_monthly_equivalent": oop_4w,
            "oop_12m_monthly_equivalent": oop_12m,
            "oop_combined_monthly_equivalent": oop_combined,
            "oop_share_total_budget_candidate": share.where(denominator, pd.NA),
            "che10_total_budget_candidate": che10.astype(int),
            "che25_total_budget_candidate": che25.astype(int),
            "positive_oop_candidate": positive_oop.astype(int),
            "denominator_valid": denominator.astype(int),
            "outcome_missing": missing.astype(int),
            "candidate_policy_name": POLICY_NAME,
            "candidate_formula": "(oop_4w_sum_unreviewed * 13 / 12) + (oop_12m_sum_unreviewed / 12)",
            "outcome_quality_flag": "period_aligned_candidate_not_promoted",
            "promotion_status": PROMOTION_STATUS,
            "blocking_reason": blocking_reason(),
        }
    )
    return out


def audit_row(
    outcome_id: str,
    label: str,
    values: pd.Series,
    denominator: pd.Series,
    event: pd.Series | None,
    weight: pd.Series,
    climate_ready: int,
) -> dict[str, str]:
    stats = quantiles(values.loc[denominator])
    missing_rows = int((~denominator).sum())
    if event is None:
        event_rows = ""
        event_rate = ""
        weighted = ""
        low_event = ""
    else:
        event_rows_int = int((denominator & event.fillna(False).astype(bool)).sum())
        denom_int = int(denominator.sum())
        event_rows = str(event_rows_int)
        event_rate = fmt(event_rows_int / denom_int) if denom_int else ""
        weighted = weighted_rate(event, denominator, weight)
        low_event = str(int(bool(event_rate) and safe_float(event_rate) < 0.03))
    return {
        "outcome_id": outcome_id,
        "outcome_label": label,
        "policy_name": POLICY_NAME,
        "household_rows": str(int(values.shape[0])),
        "denominator_rows": str(int(denominator.sum())),
        "missing_rows": str(missing_rows),
        "event_rows": event_rows,
        "event_rate": event_rate,
        "weighted_event_rate": weighted,
        "low_event_rate_flag": low_event,
        "mean_value": stats["mean"],
        "p50_value": stats["p50"],
        "p95_value": stats["p95"],
        "max_value": stats["max"],
        "ready_for_outcome": "0",
        "ready_for_recipe": "0",
        "sdg382_ready": "0",
        "climate_linkage_ready": str(climate_ready),
        "promotion_status": PROMOTION_STATUS,
        "blocking_reason": blocking_reason(),
    }


def build_audit(household: pd.DataFrame, climate_ready: int) -> list[dict[str, str]]:
    denominator = numeric(household["denominator_valid"]).fillna(0).astype(bool)
    weight = numeric(household["household_weight"])
    share = numeric(household["oop_share_total_budget_candidate"])
    oop = numeric(household["oop_combined_monthly_equivalent"])
    che10 = numeric(household["che10_total_budget_candidate"]).fillna(0).astype(bool)
    che25 = numeric(household["che25_total_budget_candidate"]).fillna(0).astype(bool)
    positive = numeric(household["positive_oop_candidate"]).fillna(0).astype(bool)
    return [
        audit_row("positive_oop_candidate", "Any positive period-aligned OOP candidate", oop, denominator, positive, weight, climate_ready),
        audit_row("oop_share_total_budget_candidate", "OOP share of monthly total budget candidate", share, denominator, None, weight, climate_ready),
        audit_row("che10_total_budget_candidate", "OOP share > 10% of monthly total budget candidate", share, denominator, che10, weight, climate_ready),
        audit_row("che25_total_budget_candidate", "OOP share > 25% of monthly total budget candidate", share, denominator, che25, weight, climate_ready),
    ]


def lineage_rows() -> list[dict[str, str]]:
    artifacts = (
        "temp/alb2002_household_core_candidate.csv;"
        "temp/alb2002_period_aligned_che_policy_audit.csv;"
        "result/alb2002_period_aligned_che_policy_summary.csv;"
        "result/alb2002_weight_design_evidence_summary.csv"
    )
    return [
        {
            "lineage_id": "lineage_001",
            "derived_field": "oop_4w_monthly_equivalent",
            "source_fields": "oop_4w_sum_unreviewed",
            "source_artifacts": artifacts,
            "formula_or_rule": "oop_4w_sum_unreviewed * 13 / 12",
            "status": "candidate_not_promoted",
            "blocking_reason": "Four-week OOP scope is documented as a stress-test numerator, not a promoted final numerator.",
        },
        {
            "lineage_id": "lineage_002",
            "derived_field": "oop_12m_monthly_equivalent",
            "source_fields": "oop_12m_sum_unreviewed",
            "source_artifacts": artifacts,
            "formula_or_rule": "oop_12m_sum_unreviewed / 12",
            "status": "candidate_not_promoted",
            "blocking_reason": "Twelve-month hospital/dentist OOP scope is documented as a stress-test numerator, not a promoted final numerator.",
        },
        {
            "lineage_id": "lineage_003",
            "derived_field": "oop_combined_monthly_equivalent",
            "source_fields": "oop_4w_sum_unreviewed;oop_12m_sum_unreviewed",
            "source_artifacts": artifacts,
            "formula_or_rule": "(oop_4w_sum_unreviewed * 13 / 12) + (oop_12m_sum_unreviewed / 12)",
            "status": "candidate_not_promoted",
            "blocking_reason": "Combined mixed-recall OOP requires final numerator-scope and benchmark review before outcome promotion.",
        },
        {
            "lineage_id": "lineage_004",
            "derived_field": "oop_share_total_budget_candidate",
            "source_fields": "oop_combined_monthly_equivalent;total_consumption",
            "source_artifacts": artifacts,
            "formula_or_rule": "oop_combined_monthly_equivalent / total_consumption",
            "status": "candidate_not_promoted",
            "blocking_reason": "Total consumption is documented as a monthly total-budget candidate, but final outcome promotion still requires recipe and benchmark review.",
        },
        {
            "lineage_id": "lineage_005",
            "derived_field": "che10_total_budget_candidate",
            "source_fields": "oop_share_total_budget_candidate",
            "source_artifacts": artifacts,
            "formula_or_rule": "oop_share_total_budget_candidate > 0.10",
            "status": "candidate_not_promoted",
            "blocking_reason": "CHE10 candidate is computed for audit only and not written to data/.",
        },
        {
            "lineage_id": "lineage_006",
            "derived_field": "che25_total_budget_candidate",
            "source_fields": "oop_share_total_budget_candidate",
            "source_artifacts": artifacts,
            "formula_or_rule": "oop_share_total_budget_candidate > 0.25",
            "status": "candidate_not_promoted",
            "blocking_reason": "CHE25 candidate is computed for audit only and not written to data/.",
        },
    ]


def summary_row(metric: str, value: Any, interpretation: str) -> dict[str, str]:
    return {"metric": metric, "value": fmt(value), "interpretation": interpretation}


def build_summary(household: pd.DataFrame, audit: list[dict[str, str]], climate_ready: int) -> list[dict[str, str]]:
    period_summary = read_csv_dicts(PERIOD_CHE_SUMMARY_PATH)
    weight_summary = read_csv_dicts(WEIGHT_SUMMARY_PATH)
    recipe_summary = read_csv_dicts(MINIMUM_RECIPE_SUMMARY_PATH)
    audit_by_id = {row["outcome_id"]: row for row in audit}
    return [
        summary_row("alb2002_che_candidate_household_rows", len(household), "Temp-only ALB_2002 household CHE candidate rows."),
        summary_row("alb2002_che_candidate_denominator_rows", audit_by_id["che10_total_budget_candidate"]["denominator_rows"], "Rows with positive monthly total-budget candidate denominator."),
        summary_row("alb2002_che_candidate_missing_rows", audit_by_id["che10_total_budget_candidate"]["missing_rows"], "Rows missing the candidate denominator."),
        summary_row("alb2002_che_candidate_positive_oop_rows", audit_by_id["positive_oop_candidate"]["event_rows"], "Rows with positive period-aligned combined OOP candidate."),
        summary_row("alb2002_che_candidate_positive_oop_weighted_rate", audit_by_id["positive_oop_candidate"]["weighted_event_rate"], "Weighted positive-OOP rate using current weight evidence."),
        summary_row("alb2002_che_candidate_che10_rows", audit_by_id["che10_total_budget_candidate"]["event_rows"], "Rows with candidate CHE10 under the period-aligned combined OOP policy."),
        summary_row("alb2002_che_candidate_che10_rate", audit_by_id["che10_total_budget_candidate"]["event_rate"], "Unweighted candidate CHE10 rate."),
        summary_row("alb2002_che_candidate_che10_weighted_rate", audit_by_id["che10_total_budget_candidate"]["weighted_event_rate"], "Weighted candidate CHE10 rate."),
        summary_row("alb2002_che_candidate_che25_rows", audit_by_id["che25_total_budget_candidate"]["event_rows"], "Rows with candidate CHE25 under the period-aligned combined OOP policy."),
        summary_row("alb2002_che_candidate_che25_rate", audit_by_id["che25_total_budget_candidate"]["event_rate"], "Unweighted candidate CHE25 rate."),
        summary_row("alb2002_che_candidate_che25_weighted_rate", audit_by_id["che25_total_budget_candidate"]["weighted_event_rate"], "Weighted candidate CHE25 rate."),
        summary_row("alb2002_che_candidate_period_policy_rows", metric_value(period_summary, "alb2002_period_aligned_che_policy_rows"), "Period-aligned policy rows consumed upstream."),
        summary_row("alb2002_che_candidate_weight_positive_rows", metric_value(weight_summary, "alb2002_weight_design_positive_weight_rows"), "Positive household-weight rows consumed upstream."),
        summary_row("alb2002_che_candidate_weighted_inference_ready_rows", metric_value(weight_summary, "alb2002_weight_design_weighted_inference_ready_rows"), "Rows ready for promoted weighted inference; should remain zero."),
        summary_row("alb2002_che_candidate_minimum_recipe_harmonized_ready_rows", metric_value(recipe_summary, "alb2002_minimum_recipe_promotion_harmonized_ready_rows"), "Rows ready for harmonized data promotion upstream; should remain zero."),
        summary_row("alb2002_che_candidate_minimum_recipe_outcome_ready_rows", metric_value(recipe_summary, "alb2002_minimum_recipe_promotion_outcome_ready_rows"), "Rows ready for outcome promotion upstream; should remain zero."),
        summary_row("alb2002_che_candidate_climate_linkage_ready_rows", climate_ready, "Rows ready for climate linkage; should remain zero until geography is verified."),
        summary_row("alb2002_che_candidate_outcome_promotion_ready_rows", 0, "Rows ready for final household outcome promotion; intentionally zero."),
        summary_row("alb2002_che_candidate_current_decision", DECISION, "Current fail-closed CHE candidate outcome decision."),
    ]


def markdown_rows(rows: list[dict[str, str]], columns: list[str], limit: int = 20) -> str:
    lines = ["| " + " | ".join(columns) + " |", "|" + "|".join("---" for _ in columns) + "|"]
    for row in rows[:limit]:
        values = []
        for column in columns:
            value = str(row.get(column, "")).replace("|", "/")
            if len(value) > 140:
                value = value[:137] + "..."
            values.append(value)
        lines.append("| " + " | ".join(values) + " |")
    return "\n".join(lines)


def write_report(summary: list[dict[str, str]], audit: list[dict[str, str]], lineage: list[dict[str, str]]) -> None:
    summary_table = "\n".join(f"| {row['metric']} | {row['value']} | {row['interpretation']} |" for row in summary)
    REPORT_PATH.write_text(
        f"""# ALB_2002 CHE Candidate Outcome Audit

Status: temp-only household-level CHE candidate outcome audit. This builds household CHE10/CHE25 candidates from the period-aligned combined no-gifts-with-transport OOP numerator and documented monthly total-budget denominator candidate. It does not write `data/`, does not declare SDG 3.8.2 ready, and does not construct climate-linked outcomes.

## Summary

| Metric | Value | Interpretation |
|---|---:|---|
{summary_table}

## Outcome Audit

{markdown_rows(audit, ['outcome_id', 'denominator_rows', 'event_rows', 'event_rate', 'weighted_event_rate', 'ready_for_outcome', 'promotion_status'])}

## Lineage

{markdown_rows(lineage, ['derived_field', 'source_fields', 'formula_or_rule', 'status', 'blocking_reason'])}

## Interpretation

- Candidate CHE10 and CHE25 are now available at household level in `temp/alb2002_che_candidate_household_outcomes.csv`.
- The candidate rates are audit evidence only: outcome-promotion-ready rows remain zero.
- SDG 3.8.2 remains blocked because SPL, PPP/CPI, and discretionary-budget inputs are not accepted.
- Climate-linked outcome construction remains blocked because ALB_2002 geography is district-admin only and the available boundary lead is not verified as a 2001/2002 source.

## Machine-Readable Outputs

- `temp/alb2002_che_candidate_household_outcomes.csv`
- `temp/alb2002_che_candidate_outcome_lineage.csv`
- `result/alb2002_che_candidate_outcome_audit.csv`
- `result/alb2002_che_candidate_outcome_summary.csv`
""",
        encoding="utf-8",
    )


def main() -> None:
    ensure_dirs()
    if not CANDIDATE_PATH.exists():
        raise FileNotFoundError(f"Missing prerequisite: {CANDIDATE_PATH}")
    candidate = pd.read_csv(CANDIDATE_PATH)
    crosswalk_summary = read_csv_dicts(CROSSWALK_SUMMARY_PATH)
    climate_ready = safe_int(metric_value(crosswalk_summary, "alb2002_climate_linkage_ready_rows"))
    household = build_household_outcomes(candidate)
    audit = build_audit(household, climate_ready)
    lineage = lineage_rows()
    summary = build_summary(household, audit, climate_ready)

    write_csv(HOUSEHOLD_OUTCOME_PATH, household.fillna("").to_dict("records"), HOUSEHOLD_COLUMNS)
    write_csv(LINEAGE_PATH, lineage, LINEAGE_COLUMNS)
    write_csv(AUDIT_PATH, audit, AUDIT_COLUMNS)
    write_csv(SUMMARY_PATH, summary, SUMMARY_COLUMNS)
    write_report(summary, audit, lineage)
    append_log(TEMP_DIR / "audit_log.md", f"Built ALB_2002 CHE candidate outcome audit rows={len(household)} decision={DECISION}.")
    print(f"ALB_2002 CHE candidate outcomes rows={len(household)} decision={DECISION}.")


if __name__ == "__main__":
    main()
