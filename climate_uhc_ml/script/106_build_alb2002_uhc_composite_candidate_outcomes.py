from __future__ import annotations

import csv
import math
from typing import Any

import pandas as pd

from common import REPORT_DIR, RESULT_DIR, TEMP_DIR, append_log, ensure_dirs, write_csv


CHE_PATH = TEMP_DIR / "alb2002_che_candidate_household_outcomes.csv"
ACCESS_PATH = TEMP_DIR / "alb2002_access_candidate_household_outcomes.csv"
CHE_SUMMARY_PATH = RESULT_DIR / "alb2002_che_candidate_outcome_summary.csv"
ACCESS_SUMMARY_PATH = RESULT_DIR / "alb2002_access_candidate_outcome_summary.csv"

OUTCOME_PATH = TEMP_DIR / "alb2002_uhc_composite_candidate_outcomes.csv"
LINEAGE_PATH = TEMP_DIR / "alb2002_uhc_composite_candidate_lineage.csv"
AUDIT_PATH = RESULT_DIR / "alb2002_uhc_composite_candidate_audit.csv"
SUMMARY_PATH = RESULT_DIR / "alb2002_uhc_composite_candidate_summary.csv"
REPORT_PATH = REPORT_DIR / "alb2002_uhc_composite_candidate_audit.md"

DECISION = "blocked_alb2002_uhc_composite_candidate_not_promoted_due_outcome_recipe_climate_gates"
PROMOTION_STATUS = "temp_only_uhc_composite_candidate_not_promoted"

OUTCOME_COLUMNS = [
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
    "household_weight",
    "total_consumption_monthly_candidate",
    "oop_combined_monthly_equivalent",
    "oop_share_total_budget_candidate",
    "che10_total_budget_candidate",
    "che25_total_budget_candidate",
    "composite_any_access_barrier_candidate",
    "composite_cost_barrier_candidate",
    "money_raising_any_candidate",
    "uhc_double_failure_che10_or_access_candidate",
    "uhc_double_failure_che25_or_access_candidate",
    "financial_only_che10_candidate",
    "access_only_vs_che10_candidate",
    "both_che10_access_candidate",
    "financial_only_che25_candidate",
    "access_only_vs_che25_candidate",
    "both_che25_access_candidate",
    "coping_health_cost_candidate",
    "financial_denominator_valid",
    "access_denominator_valid",
    "composite_denominator_valid",
    "candidate_policy_name",
    "candidate_dataset_status",
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
    "outcome_family",
    "denominator_definition",
    "source_fields",
    "household_rows",
    "denominator_rows",
    "missing_rows",
    "event_rows",
    "event_rate",
    "weighted_event_rate",
    "low_event_rate_flag",
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


def fmt(value: Any) -> str:
    number = safe_float(value)
    if math.isnan(number):
        return "" if value is None else str(value)
    if number.is_integer():
        return str(int(number))
    return f"{number:.6g}"


def numeric(series: pd.Series) -> pd.Series:
    return pd.to_numeric(series, errors="coerce")


def bool_col(frame: pd.DataFrame, column: str) -> pd.Series:
    if column not in frame.columns:
        return pd.Series(False, index=frame.index)
    return numeric(frame[column]).fillna(0) > 0


def hhid_key(series: pd.Series) -> pd.Series:
    return series.astype(str).str.strip().str.replace(r"\.0$", "", regex=True)


def blocking_reason() -> str:
    return (
        "Composite UHC failure candidates combine temp-only ALB_2002 CHE and access candidates, "
        "but they remain outside data/ because financial outcomes, access outcomes, harmonization recipe, "
        "SDG denominator, benchmark, and climate-geography gates have not passed together."
    )


def build_merged() -> pd.DataFrame:
    if not CHE_PATH.exists():
        raise FileNotFoundError(f"Missing prerequisite: {CHE_PATH}")
    if not ACCESS_PATH.exists():
        raise FileNotFoundError(f"Missing prerequisite: {ACCESS_PATH}")
    che = pd.read_csv(CHE_PATH, encoding="utf-8-sig")
    access = pd.read_csv(ACCESS_PATH, encoding="utf-8-sig")
    che["hhid_key"] = hhid_key(che["hhid"])
    access["hhid_key"] = hhid_key(access["hhid"])
    if che["hhid_key"].duplicated().any() or access["hhid_key"].duplicated().any():
        raise ValueError("Non-unique hhid keys in CHE or access candidate inputs.")
    merged = che.merge(
        access[
            [
                "hhid_key",
                "composite_any_access_barrier_candidate",
                "composite_cost_barrier_candidate",
                "money_raising_any_candidate",
                "broad_access_denominator_valid",
            ]
        ],
        on="hhid_key",
        how="inner",
        validate="one_to_one",
    )
    if len(merged) != len(che) or len(merged) != len(access):
        raise ValueError(f"CHE/access candidate row mismatch after merge: che={len(che)} access={len(access)} merged={len(merged)}")
    return merged.drop(columns=["hhid_key"])


def build_outcomes() -> pd.DataFrame:
    merged = build_merged()
    che10 = bool_col(merged, "che10_total_budget_candidate")
    che25 = bool_col(merged, "che25_total_budget_candidate")
    access_any = bool_col(merged, "composite_any_access_barrier_candidate")
    access_cost = bool_col(merged, "composite_cost_barrier_candidate")
    coping = bool_col(merged, "money_raising_any_candidate")
    financial_denom = bool_col(merged, "denominator_valid")
    access_denom = bool_col(merged, "broad_access_denominator_valid")
    composite_denom = financial_denom & access_denom

    return pd.DataFrame(
        {
            "country": merged["country"],
            "survey_name": merged["survey_name"],
            "wave": merged["wave"],
            "idno": merged["idno"],
            "hhid": merged["hhid"],
            "survey_year": merged["survey_year"],
            "survey_month": merged["survey_month"],
            "interview_date": merged["interview_date"],
            "psu": merged["psu"],
            "stratum": merged["stratum"],
            "district_code": merged["district_code"],
            "district_name": merged["district_name"],
            "household_weight": merged["household_weight"],
            "total_consumption_monthly_candidate": merged["total_consumption_monthly_candidate"],
            "oop_combined_monthly_equivalent": merged["oop_combined_monthly_equivalent"],
            "oop_share_total_budget_candidate": merged["oop_share_total_budget_candidate"],
            "che10_total_budget_candidate": che10.astype(int),
            "che25_total_budget_candidate": che25.astype(int),
            "composite_any_access_barrier_candidate": access_any.astype(int),
            "composite_cost_barrier_candidate": access_cost.astype(int),
            "money_raising_any_candidate": coping.astype(int),
            "uhc_double_failure_che10_or_access_candidate": (che10 | access_any).astype(int),
            "uhc_double_failure_che25_or_access_candidate": (che25 | access_any).astype(int),
            "financial_only_che10_candidate": (che10 & ~access_any).astype(int),
            "access_only_vs_che10_candidate": (access_any & ~che10).astype(int),
            "both_che10_access_candidate": (che10 & access_any).astype(int),
            "financial_only_che25_candidate": (che25 & ~access_any).astype(int),
            "access_only_vs_che25_candidate": (access_any & ~che25).astype(int),
            "both_che25_access_candidate": (che25 & access_any).astype(int),
            "coping_health_cost_candidate": coping.astype(int),
            "financial_denominator_valid": financial_denom.astype(int),
            "access_denominator_valid": access_denom.astype(int),
            "composite_denominator_valid": composite_denom.astype(int),
            "candidate_policy_name": "che10_che25_or_access_composite_screening",
            "candidate_dataset_status": "temp_only_composite_uhc_candidate_not_promoted",
            "promotion_status": PROMOTION_STATUS,
            "blocking_reason": blocking_reason(),
        }
    )


def weighted_rate(event: pd.Series, denominator: pd.Series, weight: pd.Series) -> str:
    valid = denominator.fillna(False).astype(bool) & weight.notna() & (weight > 0)
    if not valid.any():
        return ""
    total_weight = float(weight.loc[valid].sum())
    if total_weight <= 0:
        return ""
    event_weight = float(weight.loc[valid & event.fillna(False).astype(bool)].sum())
    return fmt(event_weight / total_weight)


def audit_row(
    outcomes: pd.DataFrame,
    outcome_id: str,
    label: str,
    family: str,
    denominator: pd.Series,
    source_fields: str,
) -> dict[str, str]:
    denominator_bool = denominator.fillna(False).astype(bool)
    event_bool = bool_col(outcomes, outcome_id) & denominator_bool
    denom_rows = int(denominator_bool.sum())
    event_rows = int(event_bool.sum())
    event_rate = event_rows / denom_rows if denom_rows else float("nan")
    return {
        "outcome_id": outcome_id,
        "outcome_label": label,
        "outcome_family": family,
        "denominator_definition": "Financial denominator and broad access denominator both valid.",
        "source_fields": source_fields,
        "household_rows": str(len(outcomes)),
        "denominator_rows": str(denom_rows),
        "missing_rows": str(len(outcomes) - denom_rows),
        "event_rows": str(event_rows),
        "event_rate": fmt(event_rate),
        "weighted_event_rate": weighted_rate(event_bool, denominator_bool, numeric(outcomes["household_weight"])),
        "low_event_rate_flag": str(int(denom_rows > 0 and event_rate < 0.03)),
        "ready_for_outcome": "0",
        "ready_for_recipe": "0",
        "sdg382_ready": "0",
        "climate_linkage_ready": "0",
        "promotion_status": PROMOTION_STATUS,
        "blocking_reason": blocking_reason(),
    }


def build_audit(outcomes: pd.DataFrame) -> list[dict[str, str]]:
    denominator = bool_col(outcomes, "composite_denominator_valid")
    return [
        audit_row(outcomes, "uhc_double_failure_che10_or_access_candidate", "CHE10 or any access barrier", "double_failure", denominator, "che10_total_budget_candidate;composite_any_access_barrier_candidate"),
        audit_row(outcomes, "uhc_double_failure_che25_or_access_candidate", "CHE25 or any access barrier", "double_failure", denominator, "che25_total_budget_candidate;composite_any_access_barrier_candidate"),
        audit_row(outcomes, "financial_only_che10_candidate", "CHE10 without access barrier", "financial_only", denominator, "che10_total_budget_candidate;composite_any_access_barrier_candidate"),
        audit_row(outcomes, "access_only_vs_che10_candidate", "Access barrier without CHE10", "access_only", denominator, "che10_total_budget_candidate;composite_any_access_barrier_candidate"),
        audit_row(outcomes, "both_che10_access_candidate", "CHE10 and access barrier", "both_financial_and_access", denominator, "che10_total_budget_candidate;composite_any_access_barrier_candidate"),
        audit_row(outcomes, "financial_only_che25_candidate", "CHE25 without access barrier", "financial_only", denominator, "che25_total_budget_candidate;composite_any_access_barrier_candidate"),
        audit_row(outcomes, "access_only_vs_che25_candidate", "Access barrier without CHE25", "access_only", denominator, "che25_total_budget_candidate;composite_any_access_barrier_candidate"),
        audit_row(outcomes, "both_che25_access_candidate", "CHE25 and access barrier", "both_financial_and_access", denominator, "che25_total_budget_candidate;composite_any_access_barrier_candidate"),
        audit_row(outcomes, "composite_cost_barrier_candidate", "Composite access cost barrier", "access_cost", denominator, "composite_cost_barrier_candidate"),
        audit_row(outcomes, "coping_health_cost_candidate", "Money raising for health care", "coping_failure", denominator, "money_raising_any_candidate"),
    ]


def lineage_rows() -> list[dict[str, str]]:
    artifacts = "temp/alb2002_che_candidate_household_outcomes.csv;temp/alb2002_access_candidate_household_outcomes.csv"
    rows = [
        ("lineage_001", "uhc_double_failure_che10_or_access_candidate", "che10_total_budget_candidate;composite_any_access_barrier_candidate", "CHE10 candidate OR composite any-access-barrier candidate.", "Composite mixes temp-only financial and access candidates."),
        ("lineage_002", "uhc_double_failure_che25_or_access_candidate", "che25_total_budget_candidate;composite_any_access_barrier_candidate", "CHE25 candidate OR composite any-access-barrier candidate.", "Composite mixes temp-only financial and access candidates."),
        ("lineage_003", "financial_only_*_candidate", "che10_total_budget_candidate;che25_total_budget_candidate;composite_any_access_barrier_candidate", "Financial hardship candidate present and access barrier absent.", "Absence of observed access barrier is not proof of no access failure."),
        ("lineage_004", "access_only_vs_che*_candidate", "che10_total_budget_candidate;che25_total_budget_candidate;composite_any_access_barrier_candidate", "Access barrier candidate present and financial hardship candidate absent.", "Absence of CHE is threshold- and denominator-dependent."),
        ("lineage_005", "both_che*_access_candidate", "che10_total_budget_candidate;che25_total_budget_candidate;composite_any_access_barrier_candidate", "Financial hardship and access barrier candidates both present.", "Both components remain unpromoted."),
        ("lineage_006", "coping_health_cost_candidate", "money_raising_any_candidate", "Any Health B money-raising method for health care.", "Coping proxy requires final source-scope review."),
    ]
    return [
        {
            "lineage_id": row[0],
            "derived_field": row[1],
            "source_fields": row[2],
            "source_artifacts": artifacts,
            "formula_or_rule": row[3],
            "status": "candidate_not_promoted",
            "blocking_reason": row[4],
        }
        for row in rows
    ]


def summary_row(metric: str, value: Any, interpretation: str) -> dict[str, str]:
    return {"metric": metric, "value": fmt(value), "interpretation": interpretation}


def build_summary(outcomes: pd.DataFrame, audit: list[dict[str, str]]) -> list[dict[str, str]]:
    che_summary = read_csv_dicts(CHE_SUMMARY_PATH)
    access_summary = read_csv_dicts(ACCESS_SUMMARY_PATH)
    audit_by_id = {row["outcome_id"]: row for row in audit}

    def event_rows(outcome_id: str) -> str:
        return audit_by_id.get(outcome_id, {}).get("event_rows", "0")

    def event_rate(outcome_id: str) -> str:
        return audit_by_id.get(outcome_id, {}).get("event_rate", "")

    def weighted(outcome_id: str) -> str:
        return audit_by_id.get(outcome_id, {}).get("weighted_event_rate", "")

    return [
        summary_row("alb2002_uhc_composite_candidate_household_rows", len(outcomes), "Temp-only ALB_2002 composite UHC candidate rows."),
        summary_row("alb2002_uhc_composite_candidate_lineage_rows", 6, "Lineage rows for composite UHC candidate fields."),
        summary_row("alb2002_uhc_composite_candidate_audit_rows", len(audit), "Outcome audit rows for composite UHC candidate fields."),
        summary_row("alb2002_uhc_composite_candidate_source_che10_rows", metric_value(che_summary, "alb2002_che_candidate_che10_rows"), "Upstream CHE10 candidate rows consumed."),
        summary_row("alb2002_uhc_composite_candidate_source_che25_rows", metric_value(che_summary, "alb2002_che_candidate_che25_rows"), "Upstream CHE25 candidate rows consumed."),
        summary_row("alb2002_uhc_composite_candidate_source_access_any_rows", metric_value(access_summary, "alb2002_access_candidate_composite_any_rows"), "Upstream any-access-barrier candidate rows consumed."),
        summary_row("alb2002_uhc_composite_candidate_che10_or_access_rows", event_rows("uhc_double_failure_che10_or_access_candidate"), "CHE10 or any access-barrier candidate rows."),
        summary_row("alb2002_uhc_composite_candidate_che10_or_access_rate", event_rate("uhc_double_failure_che10_or_access_candidate"), "CHE10-or-access unweighted candidate rate."),
        summary_row("alb2002_uhc_composite_candidate_che10_or_access_weighted_rate", weighted("uhc_double_failure_che10_or_access_candidate"), "CHE10-or-access weighted candidate rate."),
        summary_row("alb2002_uhc_composite_candidate_che25_or_access_rows", event_rows("uhc_double_failure_che25_or_access_candidate"), "CHE25 or any access-barrier candidate rows."),
        summary_row("alb2002_uhc_composite_candidate_che25_or_access_rate", event_rate("uhc_double_failure_che25_or_access_candidate"), "CHE25-or-access unweighted candidate rate."),
        summary_row("alb2002_uhc_composite_candidate_che25_or_access_weighted_rate", weighted("uhc_double_failure_che25_or_access_candidate"), "CHE25-or-access weighted candidate rate."),
        summary_row("alb2002_uhc_composite_candidate_financial_only_che10_rows", event_rows("financial_only_che10_candidate"), "CHE10-only candidate rows."),
        summary_row("alb2002_uhc_composite_candidate_access_only_vs_che10_rows", event_rows("access_only_vs_che10_candidate"), "Access-only versus CHE10 candidate rows."),
        summary_row("alb2002_uhc_composite_candidate_both_che10_access_rows", event_rows("both_che10_access_candidate"), "Both CHE10 and access-barrier candidate rows."),
        summary_row("alb2002_uhc_composite_candidate_financial_only_che25_rows", event_rows("financial_only_che25_candidate"), "CHE25-only candidate rows."),
        summary_row("alb2002_uhc_composite_candidate_access_only_vs_che25_rows", event_rows("access_only_vs_che25_candidate"), "Access-only versus CHE25 candidate rows."),
        summary_row("alb2002_uhc_composite_candidate_both_che25_access_rows", event_rows("both_che25_access_candidate"), "Both CHE25 and access-barrier candidate rows."),
        summary_row("alb2002_uhc_composite_candidate_coping_rows", event_rows("coping_health_cost_candidate"), "Money-raising/coping candidate rows."),
        summary_row("alb2002_uhc_composite_candidate_low_event_rate_rows", sum(1 for row in audit if row["low_event_rate_flag"] == "1"), "Composite candidate outcomes with event rate below 3 percent."),
        summary_row("alb2002_uhc_composite_candidate_outcome_promotion_ready_rows", 0, "Rows ready for final composite outcome promotion; intentionally zero."),
        summary_row("alb2002_uhc_composite_candidate_recipe_ready_rows", 0, "Rows ready for harmonized recipe promotion; intentionally zero."),
        summary_row("alb2002_uhc_composite_candidate_sdg382_ready_rows", 0, "Rows ready for SDG 3.8.2 construction; intentionally zero."),
        summary_row("alb2002_uhc_composite_candidate_climate_linkage_ready_rows", 0, "Rows ready for climate linkage; intentionally zero."),
        summary_row("alb2002_uhc_composite_candidate_current_decision", DECISION, "Current fail-closed composite UHC candidate decision."),
    ]


def markdown_rows(rows: list[dict[str, str]], columns: list[str], limit: int = 25) -> str:
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


def write_report(summary: list[dict[str, str]], audit: list[dict[str, str]], lineage: list[dict[str, str]]) -> None:
    summary_table = "\n".join(f"| {row['metric']} | {row['value']} | {row['interpretation']} |" for row in summary)
    REPORT_PATH.write_text(
        f"""# ALB_2002 UHC Composite Candidate Outcome Audit

Status: temp-only household-level composite UHC outcome audit. This combines the ALB_2002 CHE10/CHE25 candidate outcomes with access-barrier candidates to inspect double-failure, financial-only, access-only, both-failure, and coping candidates. It does not write `data/` outputs and does not promote any final outcome.

## Summary

| Metric | Value | Interpretation |
|---|---:|---|
{summary_table}

## Outcome Audit

{markdown_rows(audit, ['outcome_id', 'outcome_family', 'denominator_rows', 'event_rows', 'event_rate', 'weighted_event_rate', 'low_event_rate_flag', 'ready_for_outcome'])}

## Lineage

{markdown_rows(lineage, ['derived_field', 'source_fields', 'formula_or_rule', 'status', 'blocking_reason'])}

## Interpretation

- Composite UHC candidates are available in `temp/alb2002_uhc_composite_candidate_outcomes.csv`.
- The CHE10-or-access and CHE25-or-access candidates are screening diagnostics, not final UHC failure outcomes.
- Access-only and financial-only categories depend on unresolved threshold, denominator, and skip-path decisions.
- Outcome-promotion-ready, recipe-ready, SDG 3.8.2-ready, and climate-linkage-ready rows remain zero.

## Machine-Readable Outputs

- `temp/alb2002_uhc_composite_candidate_outcomes.csv`
- `temp/alb2002_uhc_composite_candidate_lineage.csv`
- `result/alb2002_uhc_composite_candidate_audit.csv`
- `result/alb2002_uhc_composite_candidate_summary.csv`
""",
        encoding="utf-8",
    )


def main() -> None:
    ensure_dirs()
    outcomes = build_outcomes()
    audit = build_audit(outcomes)
    lineage = lineage_rows()
    summary = build_summary(outcomes, audit)
    write_csv(OUTCOME_PATH, outcomes.fillna("").to_dict("records"), OUTCOME_COLUMNS)
    write_csv(LINEAGE_PATH, lineage, LINEAGE_COLUMNS)
    write_csv(AUDIT_PATH, audit, AUDIT_COLUMNS)
    write_csv(SUMMARY_PATH, summary, SUMMARY_COLUMNS)
    write_report(summary, audit, lineage)
    append_log(TEMP_DIR / "audit_log.md", f"Built ALB_2002 UHC composite candidate audit rows={len(outcomes)} decision={DECISION}.")
    print(f"ALB_2002 UHC composite candidate rows={len(outcomes)} decision={DECISION}.")


if __name__ == "__main__":
    main()
