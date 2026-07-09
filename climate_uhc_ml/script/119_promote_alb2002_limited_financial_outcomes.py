from __future__ import annotations

import math
from pathlib import Path
from typing import Any

import pandas as pd

from common import DATA_DIR, REPORT_DIR, RESULT_DIR, TEMP_DIR, append_log, ensure_dirs, write_csv


IDNO = "ALB_2002_LSMS_v01_M"
COUNTRY = "Albania"
SURVEY_NAME = "Living Standards Measurement Survey 2002"
WAVE = "2002"

SOURCE_PATH = TEMP_DIR / "alb2002_che_candidate_household_outcomes.csv"
OUTPUT_PATH = DATA_DIR / "household_outcomes.csv"
OUTCOME_AUDIT_PATH = RESULT_DIR / "outcome_audit.csv"
CONSTRUCTION_AUDIT_PATH = TEMP_DIR / "outcome_construction_audit.csv"
PROMOTION_AUDIT_PATH = TEMP_DIR / "alb2002_limited_financial_outcome_promotion_audit.csv"
SUMMARY_PATH = RESULT_DIR / "alb2002_limited_financial_outcome_promotion_summary.csv"
REPORT_PATH = REPORT_DIR / "alb2002_limited_financial_outcome_promotion.md"
OUTCOME_REPORT_PATH = REPORT_DIR / "outcome_construction.md"

DECISION = "limited_che10_che25_financial_outcomes_promoted_sdg_access_climate_still_blocked"
SCOPE = "alb2002_financial_protection_che10_che25_limited_no_sdg382_no_access"
DATA_USE_LIMIT = "outcome_che10_che25_only_not_for_final_sdg382_access_or_climate_analysis"
PROMOTION_STATUS = "limited_financial_outcomes_promoted_sdg_access_climate_modeling_blocked"

OUTPUT_COLUMNS = [
    "country",
    "survey_name",
    "wave",
    "idno",
    "hhid",
    "survey_year",
    "survey_month",
    "interview_date",
    "household_weight",
    "strata",
    "psu",
    "admin2_code",
    "admin2",
    "cluster_id",
    "total_consumption",
    "oop_health_expenditure",
    "oop_share_total",
    "log_oop_plus_one",
    "che10_total_budget",
    "che25_total_budget",
    "positive_oop",
    "outcome_scope",
    "data_use_limit",
    "outcome_policy_name",
    "outcome_formula",
    "sdg382_ready",
    "access_outcome_ready",
    "composite_uhc_ready",
    "weighted_inference_ready",
    "climate_linkage_ready",
    "final_analysis_ready",
    "limited_outcome_write_ready",
    "promotion_status",
    "blocking_reason",
]

OUTCOME_AUDIT_COLUMNS = [
    "country",
    "survey_name",
    "wave",
    "outcome",
    "status",
    "rows",
    "nonmissing",
    "missing_rate",
    "event_rate",
    "weighted_prevalence",
    "low_event_flag",
    "construction_rule",
    "required_columns",
    "missing_columns",
    "notes",
]

CONSTRUCTION_AUDIT_COLUMNS = ["check", "status", "detail", "input_path", "rows_input", "rows_output", "output_path"]

PROMOTION_AUDIT_COLUMNS = [
    "gate_id",
    "gate_label",
    "status",
    "rows_checked",
    "rows_passing",
    "rows_blocked",
    "evidence",
    "output_artifact",
    "next_action",
]

SUMMARY_COLUMNS = ["metric", "value", "interpretation"]


def numeric(frame: pd.DataFrame, column: str) -> pd.Series:
    if column not in frame.columns:
        return pd.Series(pd.NA, index=frame.index, dtype="Float64")
    return pd.to_numeric(frame[column], errors="coerce")


def nonmissing(frame: pd.DataFrame, column: str) -> int:
    if column not in frame.columns:
        return 0
    series = frame[column]
    return int((series.notna() & (series.astype(str).str.strip() != "")).sum())


def weighted_mean(values: pd.Series, weights: pd.Series) -> str:
    valid = values.notna() & weights.notna() & (weights > 0)
    if not valid.any():
        return ""
    return f"{float((values[valid].astype(float) * weights[valid]).sum() / weights[valid].sum()):.6g}"


def blocking_reason() -> str:
    return (
        "CHE10/CHE25 are promoted only as limited ALB_2002 financial-protection outcomes. "
        "SDG 3.8.2 discretionary-budget, capacity-to-pay, impoverishment, access, composite UHC, "
        "weighted-inference, climate-linkage, and model-ready gates remain unresolved."
    )


def require_columns(frame: pd.DataFrame) -> None:
    required = [
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
        "positive_oop_candidate",
        "candidate_policy_name",
        "candidate_formula",
    ]
    missing = [column for column in required if column not in frame.columns]
    if missing:
        raise ValueError(f"Missing required CHE candidate columns: {', '.join(missing)}")


def build_output(source: pd.DataFrame) -> pd.DataFrame:
    out = pd.DataFrame(
        {
            "country": source["country"],
            "survey_name": source["survey_name"],
            "wave": source["wave"],
            "idno": source["idno"],
            "hhid": source["hhid"],
            "survey_year": source["survey_year"],
            "survey_month": source["survey_month"],
            "interview_date": source["interview_date"],
            "household_weight": source["household_weight"],
            "strata": source["stratum"],
            "psu": source["psu"],
            "admin2_code": source["district_code"],
            "admin2": source["district_name"],
            "cluster_id": source["psu"],
            "total_consumption": source["total_consumption_monthly_candidate"],
            "oop_health_expenditure": source["oop_combined_monthly_equivalent"],
            "oop_share_total": source["oop_share_total_budget_candidate"],
            "che10_total_budget": source["che10_total_budget_candidate"],
            "che25_total_budget": source["che25_total_budget_candidate"],
            "positive_oop": source["positive_oop_candidate"],
            "outcome_policy_name": source["candidate_policy_name"],
            "outcome_formula": source["candidate_formula"],
            "outcome_scope": SCOPE,
            "data_use_limit": DATA_USE_LIMIT,
            "sdg382_ready": "0",
            "access_outcome_ready": "0",
            "composite_uhc_ready": "0",
            "weighted_inference_ready": "0",
            "climate_linkage_ready": "0",
            "final_analysis_ready": "0",
            "limited_outcome_write_ready": "1",
            "promotion_status": PROMOTION_STATUS,
            "blocking_reason": blocking_reason(),
        }
    )
    oop = numeric(out, "oop_health_expenditure")
    log_oop = pd.Series(pd.NA, index=out.index, dtype="Float64")
    log_oop[oop >= 0] = (oop[oop >= 0] + 1).map(math.log)
    out["log_oop_plus_one"] = log_oop
    for column in OUTPUT_COLUMNS:
        if column not in out.columns:
            out[column] = ""
    return out[OUTPUT_COLUMNS]


def constructed_audit_row(output: pd.DataFrame, outcome: str, rule: str, *, continuous: bool = False) -> dict[str, Any]:
    series = numeric(output, outcome)
    weights = numeric(output, "household_weight")
    nonmiss = int(series.notna().sum())
    event_rate: str | float = ""
    low_event = ""
    if nonmiss and not continuous:
        event_rate = float(series.mean())
        if event_rate < 0.03:
            low_event = "event_rate_below_3_percent"
    return {
        "country": COUNTRY,
        "survey_name": SURVEY_NAME,
        "wave": WAVE,
        "outcome": outcome,
        "status": "constructed",
        "rows": len(output),
        "nonmissing": nonmiss,
        "missing_rate": float(1 - nonmiss / len(output)) if len(output) else "",
        "event_rate": event_rate,
        "weighted_prevalence": weighted_mean(series, weights),
        "low_event_flag": low_event,
        "construction_rule": rule,
        "required_columns": "",
        "missing_columns": "",
        "notes": f"limited ALB_2002 CHE-only financial-protection outcome; data_use_limit={DATA_USE_LIMIT}",
    }


def blocked_audit_row(outcome: str, required_columns: str, notes: str, rows: int) -> dict[str, Any]:
    return {
        "country": COUNTRY,
        "survey_name": SURVEY_NAME,
        "wave": WAVE,
        "outcome": outcome,
        "status": "blocked_limited_financial_outcome_scope",
        "rows": rows,
        "nonmissing": "",
        "missing_rate": "",
        "event_rate": "",
        "weighted_prevalence": "",
        "low_event_flag": "",
        "construction_rule": "",
        "required_columns": required_columns,
        "missing_columns": "",
        "notes": notes,
    }


def outcome_audit_rows(output: pd.DataFrame) -> list[dict[str, Any]]:
    rows = [
        constructed_audit_row(
            output,
            "oop_share_total",
            "period-aligned combined monthly-equivalent OOP / documented monthly total-budget candidate",
            continuous=True,
        ),
        constructed_audit_row(
            output,
            "log_oop_plus_one",
            "log(period-aligned combined monthly-equivalent OOP + 1)",
            continuous=True,
        ),
        constructed_audit_row(
            output,
            "che10_total_budget",
            "period-aligned combined monthly-equivalent OOP > 10% of documented monthly total-budget candidate",
        ),
        constructed_audit_row(
            output,
            "che25_total_budget",
            "period-aligned combined monthly-equivalent OOP > 25% of documented monthly total-budget candidate",
        ),
    ]
    blocked = [
        ("sdg382_discretionary_40", "societal poverty line; PPP/CPI; discretionary budget", "SDG 3.8.2 denominator is not accepted for ALB_2002."),
        ("capacity_to_pay_40", "capacity-to-pay denominator", "Capacity-to-pay denominator is not harmonized."),
        ("impoverishing_health_spending", "household poverty line before/after OOP", "Impoverishment inputs are not harmonized."),
        ("forgone_care_conditional_need", "accepted access denominator and skip policy", "Access outcome denominator remains blocked."),
        ("forgone_care_cost_barrier", "accepted access denominator and skip policy", "Access cost-barrier outcome remains blocked."),
        ("forgone_care_distance_barrier", "accepted access denominator and skip policy", "Access distance-barrier outcome remains blocked."),
        ("forgone_care_supply_barrier", "accepted access denominator and skip policy", "Access supply/admin outcome remains blocked."),
        ("delayed_or_unmet_care_outcome", "accepted delayed/unmet-care denominator", "Delayed/unmet-care outcome remains blocked."),
        ("uhc_double_failure", "promoted financial and access outcomes", "Composite UHC failure remains blocked because access outcomes are unpromoted."),
        ("financial_only_failure", "promoted financial and access outcomes", "Composite decomposition remains blocked because access outcomes are unpromoted."),
        ("access_only_failure", "promoted financial and access outcomes", "Composite decomposition remains blocked because access outcomes are unpromoted."),
        ("both_financial_and_access_failure", "promoted financial and access outcomes", "Composite decomposition remains blocked because access outcomes are unpromoted."),
        ("coping_failure", "accepted health-cost coping variable policy", "Coping outcome remains blocked."),
    ]
    rows.extend(blocked_audit_row(outcome, required, notes, len(output)) for outcome, required, notes in blocked)
    return rows


def promotion_audit_rows(output: pd.DataFrame) -> list[dict[str, Any]]:
    rows = len(output)
    weight_rows = nonmissing(output, "household_weight")
    che10 = int(numeric(output, "che10_total_budget").sum())
    che25 = int(numeric(output, "che25_total_budget").sum())
    return [
        {
            "gate_id": "source_candidate",
            "gate_label": "ALB_2002 CHE candidate rows",
            "status": "complete_limited_financial_outcome_source",
            "rows_checked": rows,
            "rows_passing": rows,
            "rows_blocked": 0,
            "evidence": "temp/alb2002_che_candidate_household_outcomes.csv exists with household-level CHE10/CHE25 candidates.",
            "output_artifact": "data/household_outcomes.csv",
            "next_action": "Keep the output limited to CHE-only financial-protection outcomes.",
        },
        {
            "gate_id": "financial_outcome_values",
            "gate_label": "CHE10/CHE25 values and denominators",
            "status": "complete_limited_financial_outcomes",
            "rows_checked": rows,
            "rows_passing": min(nonmissing(output, "oop_share_total"), nonmissing(output, "che10_total_budget"), nonmissing(output, "che25_total_budget")),
            "rows_blocked": 0,
            "evidence": f"che10_rows={che10}; che25_rows={che25}; denominator_rows={nonmissing(output, 'total_consumption')}",
            "output_artifact": "data/household_outcomes.csv",
            "next_action": "Use these as CHE-only outcomes; do not infer SDG 3.8.2 or access failure.",
        },
        {
            "gate_id": "weight_evidence",
            "gate_label": "Household weight coverage",
            "status": "present_not_weighted_inference_ready",
            "rows_checked": rows,
            "rows_passing": weight_rows,
            "rows_blocked": rows,
            "evidence": f"weight_rows={weight_rows}; weighted_inference_ready=0",
            "output_artifact": "data/household_outcomes.csv",
            "next_action": "Resolve final survey-design and weighted-inference policy before using model estimates.",
        },
        {
            "gate_id": "sdg382_access_composite",
            "gate_label": "SDG, access, and composite UHC outcomes",
            "status": "blocked_outside_limited_scope",
            "rows_checked": rows,
            "rows_passing": 0,
            "rows_blocked": rows,
            "evidence": "sdg382_ready=0; access_outcome_ready=0; composite_uhc_ready=0",
            "output_artifact": "",
            "next_action": "Resolve discretionary-budget, access denominator, and composite-outcome gates separately.",
        },
        {
            "gate_id": "climate_model_readiness",
            "gate_label": "Climate linkage and model readiness",
            "status": "blocked_not_climate_or_model_ready",
            "rows_checked": rows,
            "rows_passing": 0,
            "rows_blocked": rows,
            "evidence": "climate_linkage_ready=0; final_analysis_ready=0",
            "output_artifact": "",
            "next_action": "Do not use this file for descriptive, predictive, reduced-form, causal ML, policy learning, or robustness until climate-linked data are promoted.",
        },
    ]


def summary_rows(output: pd.DataFrame, promotion_rows: list[dict[str, Any]]) -> list[dict[str, str]]:
    weights = numeric(output, "household_weight")
    che10 = numeric(output, "che10_total_budget")
    che25 = numeric(output, "che25_total_budget")
    share = numeric(output, "oop_share_total")
    positive = numeric(output, "positive_oop")
    return [
        {"metric": "alb2002_limited_financial_outcome_promotion_audit_rows", "value": str(len(promotion_rows)), "interpretation": "Rows in the limited financial outcome promotion audit."},
        {"metric": "alb2002_limited_financial_outcome_rows", "value": str(len(output)), "interpretation": "Rows written to data/household_outcomes.csv."},
        {"metric": "alb2002_limited_financial_outcome_denominator_rows", "value": str(nonmissing(output, "total_consumption")), "interpretation": "Rows with documented monthly total-budget candidate denominator."},
        {"metric": "alb2002_limited_financial_outcome_positive_oop_rows", "value": str(int(positive.sum())), "interpretation": "Rows with positive period-aligned OOP."},
        {"metric": "alb2002_limited_financial_outcome_positive_oop_weighted_rate", "value": weighted_mean(positive, weights), "interpretation": "Weighted positive-OOP rate, still not final weighted inference."},
        {"metric": "alb2002_limited_financial_outcome_che10_rows", "value": str(int(che10.sum())), "interpretation": "Rows with CHE10 total-budget outcome."},
        {"metric": "alb2002_limited_financial_outcome_che10_rate", "value": f"{float(che10.mean()):.6g}", "interpretation": "Unweighted CHE10 rate."},
        {"metric": "alb2002_limited_financial_outcome_che10_weighted_rate", "value": weighted_mean(che10, weights), "interpretation": "Weighted CHE10 rate, still not final weighted inference."},
        {"metric": "alb2002_limited_financial_outcome_che25_rows", "value": str(int(che25.sum())), "interpretation": "Rows with CHE25 total-budget outcome."},
        {"metric": "alb2002_limited_financial_outcome_che25_rate", "value": f"{float(che25.mean()):.6g}", "interpretation": "Unweighted CHE25 rate."},
        {"metric": "alb2002_limited_financial_outcome_che25_weighted_rate", "value": weighted_mean(che25, weights), "interpretation": "Weighted CHE25 rate, still not final weighted inference."},
        {"metric": "alb2002_limited_financial_outcome_oop_share_mean", "value": f"{float(share.mean()):.6g}", "interpretation": "Mean OOP share among rows with valid denominator."},
        {"metric": "alb2002_limited_financial_outcome_limited_data_write_ready_rows", "value": str(len(output)), "interpretation": "Rows allowed in data/ only under limited CHE-only outcome scope."},
        {"metric": "alb2002_limited_financial_outcome_sdg382_ready_rows", "value": "0", "interpretation": "Rows ready for SDG 3.8.2 outcome."},
        {"metric": "alb2002_limited_financial_outcome_access_ready_rows", "value": "0", "interpretation": "Rows ready for access outcomes."},
        {"metric": "alb2002_limited_financial_outcome_composite_ready_rows", "value": "0", "interpretation": "Rows ready for composite UHC failure outcomes."},
        {"metric": "alb2002_limited_financial_outcome_climate_linkage_ready_rows", "value": "0", "interpretation": "Rows ready for climate-linked household data."},
        {"metric": "alb2002_limited_financial_outcome_final_analysis_ready_rows", "value": "0", "interpretation": "Rows ready for final empirical analysis."},
        {"metric": "alb2002_limited_financial_outcome_current_decision", "value": DECISION, "interpretation": "Current limited outcome promotion decision."},
        {"metric": "alb2002_limited_financial_outcome_data_use_limit", "value": DATA_USE_LIMIT, "interpretation": "Guardrail embedded in every output row."},
    ]


def markdown_table(rows: list[dict[str, Any]], columns: list[str]) -> str:
    lines = ["| " + " | ".join(columns) + " |", "|" + "|".join("---" for _ in columns) + "|"]
    for row in rows:
        values = []
        for column in columns:
            value = str(row.get(column, "")).replace("|", "/")
            if len(value) > 120:
                value = value[:117] + "..."
            values.append(value)
        lines.append("| " + " | ".join(values) + " |")
    return "\n".join(lines)


def write_reports(summary: list[dict[str, str]], promotion_rows: list[dict[str, Any]]) -> None:
    summary_table = markdown_table(summary, ["metric", "value", "interpretation"])
    gate_table = markdown_table(promotion_rows, ["gate_id", "status", "rows_passing", "rows_blocked", "next_action"])
    report = f"""# ALB_2002 Limited Financial Outcome Promotion

Status: limited CHE-only outcome promotion. This writes `data/household_outcomes.csv` from existing ALB_2002 CHE candidate rows. It promotes only `che10_total_budget`, `che25_total_budget`, `oop_share_total`, and `log_oop_plus_one`.

It does not promote SDG 3.8.2, capacity-to-pay, impoverishment, access outcomes, composite UHC failure, climate linkage, weighted inference, descriptive diagnostics, predictive ML, reduced-form estimation, causal ML, policy learning, or robustness checks.

## Summary

{summary_table}

## Gate Audit

{gate_table}

## Guardrails

- Every row carries `outcome_scope={SCOPE}`.
- Every row carries `data_use_limit={DATA_USE_LIMIT}`.
- `sdg382_ready`, `access_outcome_ready`, `composite_uhc_ready`, `climate_linkage_ready`, and `final_analysis_ready` remain zero.
- The file is sufficient only for CHE10/CHE25 financial-protection outcome inspection and audit.

## Machine-Readable Outputs

- `data/household_outcomes.csv`
- `result/outcome_audit.csv`
- `temp/outcome_construction_audit.csv`
- `temp/alb2002_limited_financial_outcome_promotion_audit.csv`
- `result/alb2002_limited_financial_outcome_promotion_summary.csv`
"""
    REPORT_PATH.write_text(report, encoding="utf-8")

    OUTCOME_REPORT_PATH.write_text(
        f"""# Outcome Construction

Status: limited ALB_2002 financial-protection outcomes constructed and audited. This is not a full UHC outcome set.

Input: `temp/alb2002_che_candidate_household_outcomes.csv`

Output: `data/household_outcomes.csv`

## Constructed Outcomes

| Outcome | Scope |
|---|---|
| `che10_total_budget` | OOP share of documented monthly total-budget candidate > 10% |
| `che25_total_budget` | OOP share of documented monthly total-budget candidate > 25% |
| `oop_share_total` | Period-aligned combined monthly-equivalent OOP / documented monthly total-budget candidate |
| `log_oop_plus_one` | log(period-aligned combined monthly-equivalent OOP + 1) |

## Blocked Outcomes

- `sdg382_discretionary_40` remains blocked because SPL/PPP/CPI/discretionary-budget inputs are not accepted.
- Access and composite UHC outcomes remain blocked because denominator, skip-path, and low-event handling are not accepted.
- Climate-linked and model-ready outcome use remains blocked.

## Audit Files

- `result/outcome_audit.csv`
- `temp/outcome_construction_audit.csv`
- `report/alb2002_limited_financial_outcome_promotion.md`
""",
        encoding="utf-8",
    )


def main() -> None:
    ensure_dirs()
    if not SOURCE_PATH.exists():
        raise FileNotFoundError(f"Missing source candidate: {SOURCE_PATH}")

    source = pd.read_csv(SOURCE_PATH, dtype=str, keep_default_na=False)
    require_columns(source)
    output = build_output(source)

    DATA_DIR.mkdir(parents=True, exist_ok=True)
    output.to_csv(OUTPUT_PATH, index=False, encoding="utf-8-sig")

    audit_rows = outcome_audit_rows(output)
    promotion_rows = promotion_audit_rows(output)
    summary = summary_rows(output, promotion_rows)

    write_csv(OUTCOME_AUDIT_PATH, audit_rows, OUTCOME_AUDIT_COLUMNS)
    write_csv(
        CONSTRUCTION_AUDIT_PATH,
        [
            {
                "check": "outcome_construction",
                "status": "complete_limited_financial_protection_only",
                "detail": "Limited ALB_2002 CHE10/CHE25, OOP share, and log OOP outcomes constructed; SDG/access/composite/climate/model gates remain blocked.",
                "input_path": "temp/alb2002_che_candidate_household_outcomes.csv",
                "rows_input": len(source),
                "rows_output": len(output),
                "output_path": "data/household_outcomes.csv",
            }
        ],
        CONSTRUCTION_AUDIT_COLUMNS,
    )
    write_csv(PROMOTION_AUDIT_PATH, promotion_rows, PROMOTION_AUDIT_COLUMNS)
    write_csv(SUMMARY_PATH, summary, SUMMARY_COLUMNS)
    write_reports(summary, promotion_rows)

    append_log(TEMP_DIR / "audit_log.md", f"Promoted limited ALB_2002 financial outcomes rows={len(output)} decision={DECISION}.")
    print(f"Promoted limited ALB_2002 financial outcomes rows={len(output)} decision={DECISION}.")


if __name__ == "__main__":
    main()
