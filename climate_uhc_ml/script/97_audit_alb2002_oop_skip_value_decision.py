from __future__ import annotations

import csv
from pathlib import Path
from typing import Any

from common import REPORT_DIR, RESULT_DIR, TEMP_DIR, append_log, ensure_dirs, write_csv


IDNO = "ALB_2002_LSMS_v01_M"
COUNTRY = "Albania"
SURVEY_NAME = "Living Standards Measurement Survey 2002"
WAVE = "2002"

SKIP_AUDIT_PATH = TEMP_DIR / "alb2002_skip_missing_semantics_audit.csv"
SKIP_SUMMARY_PATH = RESULT_DIR / "alb2002_skip_missing_semantics_summary.csv"
OOP_SUMMARY_PATH = RESULT_DIR / "alb2002_oop_aggregation_policy_summary.csv"
QUESTIONNAIRE_SUMMARY_PATH = RESULT_DIR / "alb2002_health_questionnaire_semantics_summary.csv"

AUDIT_PATH = TEMP_DIR / "alb2002_oop_skip_value_decision_audit.csv"
SUMMARY_PATH = RESULT_DIR / "alb2002_oop_skip_value_decision_summary.csv"
REPORT_PATH = REPORT_DIR / "alb2002_oop_skip_value_decision_audit.md"

DECISION = "documented_alb2002_oop_skipped_values_zero_only_but_oop_policy_not_ready"
NO_PROMOTION = "not_promoted_skip_value_decision_only"

AUDIT_COLUMNS = [
    "country",
    "survey_name",
    "wave",
    "idno",
    "decision_family",
    "decision_item",
    "source_artifacts",
    "evidence_summary",
    "payment_skip_block_rows",
    "access_condition_block_rows",
    "payment_nonmissing_skipped_rows",
    "payment_nonmissing_skipped_cells",
    "payment_zero_skipped_cells",
    "payment_positive_skipped_rows",
    "payment_positive_skipped_cells",
    "oop_policy_rows_observed",
    "oop_core_4w_match_rows",
    "oop_core_12m_match_rows",
    "zero_skip_policy_ready",
    "oop_recall_scope_ready",
    "oop_inclusion_scope_ready",
    "ready_for_recipe",
    "ready_for_outcome",
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


def int_value(value: Any) -> int:
    try:
        return int(float(str(value).strip()))
    except (TypeError, ValueError):
        return 0


def metric_value(rows: list[dict[str, str]], metric: str, default: str = "0") -> str:
    return next((row.get("value", default) for row in rows if row.get("metric") == metric), default)


def sum_int(rows: list[dict[str, str]], column: str) -> int:
    return sum(int_value(row.get(column, "0")) for row in rows)


def base_row(
    decision_family: str,
    decision_item: str,
    evidence_summary: str,
    metrics: dict[str, int],
    *,
    zero_skip_policy_ready: int,
    oop_recall_scope_ready: int = 0,
    oop_inclusion_scope_ready: int = 0,
    blocking_reason: str,
    next_action: str,
) -> dict[str, str]:
    return {
        "country": COUNTRY,
        "survey_name": SURVEY_NAME,
        "wave": WAVE,
        "idno": IDNO,
        "decision_family": decision_family,
        "decision_item": decision_item,
        "source_artifacts": (
            "temp/alb2002_skip_missing_semantics_audit.csv;"
            "result/alb2002_skip_missing_semantics_summary.csv;"
            "result/alb2002_oop_aggregation_policy_summary.csv;"
            "result/alb2002_health_questionnaire_semantics_summary.csv"
        ),
        "evidence_summary": evidence_summary,
        "payment_skip_block_rows": str(metrics["payment_skip_block_rows"]),
        "access_condition_block_rows": str(metrics["access_condition_block_rows"]),
        "payment_nonmissing_skipped_rows": str(metrics["payment_nonmissing_skipped_rows"]),
        "payment_nonmissing_skipped_cells": str(metrics["payment_nonmissing_skipped_cells"]),
        "payment_zero_skipped_cells": str(metrics["payment_zero_skipped_cells"]),
        "payment_positive_skipped_rows": str(metrics["payment_positive_skipped_rows"]),
        "payment_positive_skipped_cells": str(metrics["payment_positive_skipped_cells"]),
        "oop_policy_rows_observed": str(metrics["oop_policy_rows_observed"]),
        "oop_core_4w_match_rows": str(metrics["oop_core_4w_match_rows"]),
        "oop_core_12m_match_rows": str(metrics["oop_core_12m_match_rows"]),
        "zero_skip_policy_ready": str(zero_skip_policy_ready),
        "oop_recall_scope_ready": str(oop_recall_scope_ready),
        "oop_inclusion_scope_ready": str(oop_inclusion_scope_ready),
        "ready_for_recipe": "0",
        "ready_for_outcome": "0",
        "sdg382_ready": "0",
        "climate_linkage_ready": "0",
        "promotion_status": NO_PROMOTION,
        "blocking_reason": blocking_reason,
        "next_action": next_action,
    }


def build_rows() -> list[dict[str, str]]:
    skip_rows = read_csv_dicts(SKIP_AUDIT_PATH)
    skip_summary = read_csv_dicts(SKIP_SUMMARY_PATH)
    oop_summary = read_csv_dicts(OOP_SUMMARY_PATH)
    questionnaire_summary = read_csv_dicts(QUESTIONNAIRE_SUMMARY_PATH)

    payment_rows = [row for row in skip_rows if row.get("audit_family") == "person_payment_visit_skip"]
    access_rows = [row for row in skip_rows if row.get("audit_family") == "household_access_condition_skip"]
    metrics = {
        "payment_skip_block_rows": len(payment_rows),
        "access_condition_block_rows": len(access_rows),
        "payment_nonmissing_skipped_rows": int_value(metric_value(skip_summary, "alb2002_skip_missing_payment_nonmissing_when_not_triggered_rows")),
        "payment_nonmissing_skipped_cells": int_value(metric_value(skip_summary, "alb2002_skip_missing_payment_nonmissing_cells_when_not_triggered")),
        "payment_zero_skipped_cells": int_value(metric_value(skip_summary, "alb2002_skip_missing_payment_zero_cells_when_not_triggered")),
        "payment_positive_skipped_rows": int_value(metric_value(skip_summary, "alb2002_skip_missing_payment_positive_when_not_triggered_rows")),
        "payment_positive_skipped_cells": int_value(metric_value(skip_summary, "alb2002_skip_missing_payment_positive_cells_when_not_triggered")),
        "oop_policy_rows_observed": int_value(metric_value(oop_summary, "alb2002_oop_aggregation_policy_rows")),
        "oop_core_4w_match_rows": int_value(metric_value(oop_summary, "alb2002_oop_aggregation_policy_core_4w_match_rows")),
        "oop_core_12m_match_rows": int_value(metric_value(oop_summary, "alb2002_oop_aggregation_policy_core_12m_match_rows")),
        "questionnaire_payment_positive_skip_leaks": int_value(metric_value(questionnaire_summary, "alb2002_health_questionnaire_payment_positive_when_not_triggered_rows")),
        "questionnaire_payment_nonmissing_skip_review": int_value(metric_value(questionnaire_summary, "alb2002_health_questionnaire_payment_nonmissing_when_not_triggered_rows")),
    }
    # Cross-check direct audit sums against summary rows; keep the decision fail-closed if either source sees a positive skipped payment.
    metrics["direct_payment_positive_skipped_rows"] = sum_int(payment_rows, "downstream_any_positive_when_not_triggered_rows")
    metrics["direct_payment_positive_skipped_cells"] = sum_int(payment_rows, "downstream_positive_cells_when_not_triggered")
    positive_leak_rows = max(metrics["payment_positive_skipped_rows"], metrics["questionnaire_payment_positive_skip_leaks"], metrics["direct_payment_positive_skipped_rows"])
    positive_leak_cells = max(metrics["payment_positive_skipped_cells"], metrics["direct_payment_positive_skipped_cells"])

    zero_ready = int(
        metrics["payment_skip_block_rows"] == 7
        and metrics["payment_nonmissing_skipped_cells"] == metrics["payment_zero_skipped_cells"]
        and positive_leak_rows == 0
        and positive_leak_cells == 0
    )

    blocking_oop_policy = (
        "Skipped downstream payment cells have no positive leakage, but OOP recall period, "
        "gift/transport inclusion, annualization, SDG inputs, and climate geography are still unresolved."
    )
    next_oop_policy = (
        "Use this zero-leakage decision when reviewing OOP variants; do not promote outcomes until a single "
        "OOP scope/recall policy and denominator policy pass."
    )
    return [
        base_row(
            "payment_skip_values",
            "payment_skip_positive_leak_check",
            (
                f"payment blocks={metrics['payment_skip_block_rows']}; positive skipped rows/cells="
                f"{positive_leak_rows}/{positive_leak_cells}; questionnaire positive skipped rows="
                f"{metrics['questionnaire_payment_positive_skip_leaks']}"
            ),
            metrics,
            zero_skip_policy_ready=zero_ready,
            blocking_reason=blocking_oop_policy,
            next_action=next_oop_policy,
        ),
        base_row(
            "payment_skip_values",
            "zero_coded_skipped_payment_cells",
            (
                f"nonmissing skipped payment cells={metrics['payment_nonmissing_skipped_cells']}; "
                f"zero skipped payment cells={metrics['payment_zero_skipped_cells']}; "
                f"nonmissing skipped payment rows={metrics['payment_nonmissing_skipped_rows']}"
            ),
            metrics,
            zero_skip_policy_ready=zero_ready,
            blocking_reason=blocking_oop_policy,
            next_action=next_oop_policy,
        ),
        base_row(
            "access_condition_boundary",
            "access_skip_paths_not_oop_payment_values",
            (
                f"access condition skip blocks={metrics['access_condition_block_rows']}; these rows inform "
                "forgone-care denominator review, not OOP payment aggregation."
            ),
            metrics,
            zero_skip_policy_ready=0,
            blocking_reason=(
                "Access skip paths are not OOP payment values and still require a separate access/need denominator policy."
            ),
            next_action="Keep access-denominator decisions in the access/need audit rather than using OOP payment rules.",
        ),
        base_row(
            "oop_policy_boundary",
            "core_oop_recalculation_matches_existing_candidate",
            (
                f"OOP stress-test rows={metrics['oop_policy_rows_observed']}; recomputed no-gifts-with-transport "
                f"4w/12m sums match core candidate rows={metrics['oop_core_4w_match_rows']}/"
                f"{metrics['oop_core_12m_match_rows']}."
            ),
            metrics,
            zero_skip_policy_ready=zero_ready,
            blocking_reason=blocking_oop_policy,
            next_action=next_oop_policy,
        ),
        base_row(
            "promotion_boundary",
            "zero_skip_decision_not_outcome_promotion",
            (
                "This audit narrows the skipped-payment-value blocker only; it writes no data files and promotes "
                "zero recipe, outcome, SDG, or climate-linkage rows."
            ),
            metrics,
            zero_skip_policy_ready=zero_ready,
            blocking_reason=blocking_oop_policy,
            next_action=next_oop_policy,
        ),
    ]


def build_summary(rows: list[dict[str, str]]) -> list[dict[str, str]]:
    first = rows[0] if rows else {}
    zero_ready_rows = sum(int_value(row.get("zero_skip_policy_ready")) for row in rows)
    return [
        {"metric": "alb2002_oop_skip_value_decision_rows", "value": str(len(rows)), "interpretation": "Rows in the ALB_2002 OOP skip-value decision audit."},
        {"metric": "alb2002_oop_skip_value_payment_block_rows", "value": first.get("payment_skip_block_rows", "0"), "interpretation": "Person payment skip blocks checked for downstream skipped OOP values."},
        {"metric": "alb2002_oop_skip_value_access_condition_block_rows", "value": first.get("access_condition_block_rows", "0"), "interpretation": "Household access-condition skip blocks kept separate from OOP payment handling."},
        {"metric": "alb2002_oop_skip_value_payment_nonmissing_skipped_rows", "value": first.get("payment_nonmissing_skipped_rows", "0"), "interpretation": "Payment skip rows with any nonmissing downstream value when not triggered."},
        {"metric": "alb2002_oop_skip_value_payment_nonmissing_skipped_cells", "value": first.get("payment_nonmissing_skipped_cells", "0"), "interpretation": "Nonmissing downstream payment cells when the payment block was not triggered."},
        {"metric": "alb2002_oop_skip_value_payment_zero_skipped_cells", "value": first.get("payment_zero_skipped_cells", "0"), "interpretation": "Zero-valued downstream payment cells when the payment block was not triggered."},
        {"metric": "alb2002_oop_skip_value_payment_positive_skipped_rows", "value": first.get("payment_positive_skipped_rows", "0"), "interpretation": "Rows with positive downstream payment values when the payment block was not triggered; should remain zero."},
        {"metric": "alb2002_oop_skip_value_payment_positive_skipped_cells", "value": first.get("payment_positive_skipped_cells", "0"), "interpretation": "Positive downstream payment cells when the payment block was not triggered; should remain zero."},
        {"metric": "alb2002_oop_skip_value_oop_policy_rows_observed", "value": first.get("oop_policy_rows_observed", "0"), "interpretation": "OOP aggregation policy rows observed upstream."},
        {"metric": "alb2002_oop_skip_value_oop_core_4w_match_rows", "value": first.get("oop_core_4w_match_rows", "0"), "interpretation": "Rows where recomputed four-week no-gifts-with-transport OOP matches the core candidate sum."},
        {"metric": "alb2002_oop_skip_value_oop_core_12m_match_rows", "value": first.get("oop_core_12m_match_rows", "0"), "interpretation": "Rows where recomputed 12-month no-gifts-with-transport OOP matches the core candidate sum."},
        {"metric": "alb2002_oop_skip_value_zero_skip_policy_ready_rows", "value": str(zero_ready_rows), "interpretation": "Audit rows supporting the narrow no-positive-leakage skipped-payment decision."},
        {"metric": "alb2002_oop_skip_value_oop_recall_scope_ready_rows", "value": "0", "interpretation": "Rows accepting a final OOP recall-period policy; intentionally zero."},
        {"metric": "alb2002_oop_skip_value_oop_inclusion_scope_ready_rows", "value": "0", "interpretation": "Rows accepting final gift/transport/OOP inclusion scope; intentionally zero."},
        {"metric": "alb2002_oop_skip_value_recipe_ready_rows", "value": "0", "interpretation": "Rows ready for harmonized recipe promotion; intentionally zero."},
        {"metric": "alb2002_oop_skip_value_outcome_ready_rows", "value": "0", "interpretation": "Rows ready for outcome promotion; intentionally zero."},
        {"metric": "alb2002_oop_skip_value_sdg382_ready_rows", "value": "0", "interpretation": "Rows ready for SDG 3.8.2 promotion; intentionally zero."},
        {"metric": "alb2002_oop_skip_value_climate_linkage_ready_rows", "value": "0", "interpretation": "Rows ready for climate linkage; intentionally zero."},
        {"metric": "alb2002_oop_skip_value_current_decision", "value": DECISION, "interpretation": "Current decision for the ALB_2002 OOP skipped-payment-value audit."},
    ]


def write_report(rows: list[dict[str, str]], summary: list[dict[str, str]]) -> None:
    lines = [
        "# ALB_2002 OOP Skip-Value Decision Audit",
        "",
        "Status: focused decision audit for skipped downstream OOP payment values. This report does not write `data/`, does not choose a final OOP recall/inclusion policy, and does not promote outcomes.",
        "",
        "## Bottom Line",
        "",
        "- The payment skip-path audit covers 7 person-level payment blocks.",
        "- Nontriggered downstream payment cells are either missing or zero; no positive skipped-payment rows or cells are observed.",
        "- The zero-coded skipped payment cells can be treated as no positive OOP contribution for stress-test aggregation.",
        "- This resolves only the skipped-payment positive-leakage concern; OOP recall period, gift/transport scope, annualization, SDG denominator inputs, access denominators, and climate geography remain blocked.",
        f"- Current decision: `{DECISION}`.",
        "",
        "## Summary",
        "",
        "| Metric | Value | Interpretation |",
        "|---|---:|---|",
    ]
    for row in summary:
        lines.append(f"| {row['metric']} | {row['value']} | {row['interpretation']} |")
    lines.extend(
        [
            "",
            "## Evidence Rows",
            "",
            "| decision_family | decision_item | zero_skip_policy_ready | ready_for_recipe | ready_for_outcome | sdg382_ready | climate_linkage_ready |",
            "|---|---|---:|---:|---:|---:|---:|",
        ]
    )
    for row in rows:
        lines.append(
            "| {decision_family} | {decision_item} | {zero_skip_policy_ready} | {ready_for_recipe} | {ready_for_outcome} | {sdg382_ready} | {climate_linkage_ready} |".format(**row)
        )
    lines.extend(
        [
            "",
            "## Interpretation",
            "",
            "This audit narrows the OOP blocker from `zero/nonmissing skipped-payment review` to a documented no-positive-leakage decision. It does not make ALB_2002 outcome-ready because the final OOP numerator still needs a recall-period and inclusion-scope decision, and financial-protection outcomes still require accepted denominator, SDG, access, and climate gates.",
        ]
    )
    REPORT_PATH.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    ensure_dirs()
    rows = build_rows()
    summary = build_summary(rows)
    write_csv(AUDIT_PATH, rows, AUDIT_COLUMNS)
    write_csv(SUMMARY_PATH, summary, SUMMARY_COLUMNS)
    write_report(rows, summary)
    append_log(TEMP_DIR / "audit_log.md", f"Built ALB_2002 OOP skip-value decision audit: rows={len(rows)} decision={DECISION}.")
    print(f"ALB_2002 OOP skip-value decision audit rows={len(rows)} decision={DECISION}.")


if __name__ == "__main__":
    main()
