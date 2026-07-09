from __future__ import annotations

import csv
from pathlib import Path
from typing import Any

from common import REPORT_DIR, RESULT_DIR, TEMP_DIR, append_log, ensure_dirs, write_csv


AUDIT_PATH = TEMP_DIR / "alb2002_outcome_blocker_resolution_matrix.csv"
SUMMARY_PATH = RESULT_DIR / "alb2002_outcome_blocker_resolution_summary.csv"
REPORT_PATH = REPORT_DIR / "alb2002_outcome_blocker_resolution_matrix.md"

DECISION = "blocked_no_alb2002_outcome_ready_for_promotion"

AUDIT_COLUMNS = [
    "outcome_id",
    "outcome_family",
    "outcome_label",
    "candidate_denominator_status",
    "candidate_event_rows",
    "candidate_event_rate",
    "candidate_weighted_rate",
    "policy_evidence_status",
    "promotion_status",
    "outcome_ready_rows",
    "sdg382_ready_rows",
    "climate_linkage_ready_rows",
    "data_write_ready_rows",
    "blocking_reason",
    "next_resolution_step",
    "evidence_sources",
]
SUMMARY_COLUMNS = ["metric", "value", "interpretation"]


def read_csv_dicts(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        return []
    with path.open(encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def metric_value(rows: list[dict[str, str]], metric: str, default: str = "0") -> str:
    return next((row.get("value", default) for row in rows if row.get("metric") == metric), default)


def safe_int(value: Any, default: int = 0) -> int:
    try:
        return int(float(str(value).strip()))
    except (TypeError, ValueError):
        return default


def summary_row(metric: str, value: Any, interpretation: str) -> dict[str, str]:
    return {"metric": metric, "value": str(value), "interpretation": interpretation}


def outcome_row(
    outcome_id: str,
    outcome_family: str,
    outcome_label: str,
    candidate_denominator_status: str,
    candidate_event_rows: Any,
    candidate_event_rate: Any,
    candidate_weighted_rate: Any,
    policy_evidence_status: str,
    promotion_status: str,
    blocking_reason: str,
    next_resolution_step: str,
    evidence_sources: list[str],
) -> dict[str, str]:
    return {
        "outcome_id": outcome_id,
        "outcome_family": outcome_family,
        "outcome_label": outcome_label,
        "candidate_denominator_status": candidate_denominator_status,
        "candidate_event_rows": str(candidate_event_rows),
        "candidate_event_rate": str(candidate_event_rate),
        "candidate_weighted_rate": str(candidate_weighted_rate),
        "policy_evidence_status": policy_evidence_status,
        "promotion_status": promotion_status,
        "outcome_ready_rows": "0",
        "sdg382_ready_rows": "0",
        "climate_linkage_ready_rows": "0",
        "data_write_ready_rows": "0",
        "blocking_reason": blocking_reason,
        "next_resolution_step": next_resolution_step,
        "evidence_sources": "; ".join(evidence_sources),
    }


def build_matrix() -> list[dict[str, str]]:
    che = read_csv_dicts(RESULT_DIR / "alb2002_che_candidate_outcome_summary.csv")
    access = read_csv_dicts(RESULT_DIR / "alb2002_access_candidate_outcome_summary.csv")
    composite = read_csv_dicts(RESULT_DIR / "alb2002_uhc_composite_candidate_summary.csv")
    period = read_csv_dicts(RESULT_DIR / "alb2002_period_aligned_che_policy_summary.csv")
    oop_policy = read_csv_dicts(RESULT_DIR / "alb2002_oop_aggregation_policy_summary.csv")
    skip = read_csv_dicts(RESULT_DIR / "alb2002_oop_skip_value_decision_summary.csv")
    access_policy = read_csv_dicts(RESULT_DIR / "alb2002_access_need_denominator_policy_summary.csv")
    sdg = read_csv_dicts(RESULT_DIR / "alb2002_consumption_sdg_denominator_policy_summary.csv")
    aggregate = read_csv_dicts(RESULT_DIR / "alb2002_consumption_aggregate_metadata_crosswalk_summary.csv")
    boundary = read_csv_dicts(RESULT_DIR / "alb2002_boundary_blocker_resolution_summary.csv")

    household_rows = metric_value(che, "alb2002_che_candidate_household_rows")
    denominator_rows = metric_value(che, "alb2002_che_candidate_denominator_rows")
    period_ready = metric_value(period, "alb2002_period_aligned_che_period_alignment_ready_rows")
    zero_skip_ready = metric_value(skip, "alb2002_oop_skip_value_zero_skip_policy_ready_rows")
    oop_recall_ready = metric_value(skip, "alb2002_oop_skip_value_oop_recall_scope_ready_rows")
    oop_inclusion_ready = metric_value(skip, "alb2002_oop_skip_value_oop_inclusion_scope_ready_rows")
    sdg_spl_ready = metric_value(sdg, "alb2002_consumption_sdg_spl_ready_rows")
    sdg_ppp_ready = metric_value(sdg, "alb2002_consumption_sdg_ppp_cpi_ready_rows")
    sdg_discretionary_ready = metric_value(sdg, "alb2002_consumption_sdg_discretionary_budget_ready_rows")
    aggregate_docs = metric_value(aggregate, "alb2002_consumption_aggregate_crosswalk_official_documentation_ready_rows")
    aggregate_mapping = metric_value(aggregate, "alb2002_consumption_aggregate_crosswalk_released_variable_mapping_ready_rows")
    access_policy_rows = metric_value(access_policy, "alb2002_access_need_denominator_policy_rows")
    access_low_policy_rows = metric_value(access_policy, "alb2002_access_need_low_event_rate_rows")
    boundary_climate_ready = metric_value(boundary, "alb2002_boundary_blocker_climate_linkage_ready_rows")

    che_blocker = (
        f"Period-aligned CHE stress tests exist, but recall-scope ready rows={oop_recall_ready}, "
        f"inclusion-scope ready rows={oop_inclusion_ready}, and climate-linkage-ready rows={boundary_climate_ready}."
    )
    access_blocker = (
        f"Access policy rows={access_policy_rows}, but denominator/barrier scope is not accepted for final outcomes "
        f"and climate-linkage-ready rows={boundary_climate_ready}."
    )
    composite_blocker = "Composite candidates combine non-promoted CHE and access candidates, so they cannot be promoted independently."

    rows = [
        outcome_row(
            "che10_total_budget_candidate",
            "financial_protection",
            "CHE10 total-budget candidate",
            f"positive_monthly_total_budget_rows={denominator_rows}; household_rows={household_rows}",
            metric_value(che, "alb2002_che_candidate_che10_rows"),
            metric_value(che, "alb2002_che_candidate_che10_rate"),
            metric_value(che, "alb2002_che_candidate_che10_weighted_rate"),
            f"period_alignment_ready_rows={period_ready}; zero_skip_ready_rows={zero_skip_ready}; aggregate_docs={aggregate_docs}; aggregate_mapping={aggregate_mapping}",
            "candidate_not_promoted",
            che_blocker,
            "Accept final OOP recall/inclusion policy, denominator policy, benchmark validation, and geography gate before promotion.",
            ["result/alb2002_che_candidate_outcome_summary.csv", "result/alb2002_period_aligned_che_policy_summary.csv"],
        ),
        outcome_row(
            "che25_total_budget_candidate",
            "financial_protection",
            "CHE25 total-budget candidate",
            f"positive_monthly_total_budget_rows={denominator_rows}; household_rows={household_rows}",
            metric_value(che, "alb2002_che_candidate_che25_rows"),
            metric_value(che, "alb2002_che_candidate_che25_rate"),
            metric_value(che, "alb2002_che_candidate_che25_weighted_rate"),
            f"period_alignment_ready_rows={period_ready}; zero_skip_ready_rows={zero_skip_ready}; aggregate_docs={aggregate_docs}; aggregate_mapping={aggregate_mapping}",
            "candidate_not_promoted",
            che_blocker,
            "Keep as a stress-test candidate until final OOP numerator and denominator policies are accepted.",
            ["result/alb2002_che_candidate_outcome_summary.csv", "result/alb2002_oop_skip_value_decision_summary.csv"],
        ),
        outcome_row(
            "oop_share_total_candidate",
            "financial_protection",
            "OOP share of total budget candidate",
            f"positive_monthly_total_budget_rows={denominator_rows}; positive_oop_rows={metric_value(che, 'alb2002_che_candidate_positive_oop_rows')}",
            metric_value(che, "alb2002_che_candidate_positive_oop_rows"),
            metric_value(che, "alb2002_che_candidate_positive_oop_weighted_rate"),
            metric_value(che, "alb2002_che_candidate_positive_oop_weighted_rate"),
            f"oop_policy_rows={metric_value(oop_policy, 'alb2002_oop_aggregation_policy_rows')}; core_4w_match_rows={metric_value(oop_policy, 'alb2002_oop_aggregation_policy_core_4w_match_rows')}; core_12m_match_rows={metric_value(oop_policy, 'alb2002_oop_aggregation_policy_core_12m_match_rows')}",
            "candidate_not_promoted",
            "OOP share inputs exist for diagnostics, but the final numerator period and inclusion policy is not accepted.",
            "Write an explicit numerator decision for recall period, gifts, transport, skipped values, and annualization before promotion.",
            ["result/alb2002_oop_aggregation_policy_summary.csv", "result/alb2002_che_candidate_outcome_summary.csv"],
        ),
        outcome_row(
            "sdg382_discretionary_40",
            "financial_protection",
            "SDG 3.8.2 discretionary-budget 40 percent",
            f"total_consumption_rows={metric_value(sdg, 'alb2002_consumption_sdg_total_consumption_rows')}; spl_ready={sdg_spl_ready}; ppp_cpi_ready={sdg_ppp_ready}; discretionary_budget_ready={sdg_discretionary_ready}",
            "0",
            "0",
            "0",
            f"consumption_policy_rows={metric_value(sdg, 'alb2002_consumption_sdg_denominator_policy_rows')}; blocked_components={metric_value(sdg, 'alb2002_consumption_sdg_blocked_component_rows')}",
            "hard_blocked_sdg_denominator",
            "The official SDG denominator requires SPL, PPP/CPI or price-basis handling, and household discretionary budget inputs that are not accepted.",
            "Construct and audit SPL, PPP/CPI, poverty-line, and discretionary-budget inputs before any SDG 3.8.2 outcome.",
            ["result/alb2002_consumption_sdg_denominator_policy_summary.csv"],
        ),
        outcome_row(
            "forgone_or_barrier_any_candidate",
            "access",
            "Any access-barrier candidate",
            f"household_rows={metric_value(access, 'alb2002_access_candidate_household_rows')}; q01_need_rows={metric_value(access, 'alb2002_access_candidate_q01_need_rows')}",
            metric_value(access, "alb2002_access_candidate_composite_any_rows"),
            metric_value(access, "alb2002_access_candidate_composite_any_rate"),
            metric_value(access, "alb2002_access_candidate_composite_any_weighted_rate"),
            f"access_policy_rows={access_policy_rows}; low_event_policy_rows={access_low_policy_rows}",
            "candidate_not_promoted",
            access_blocker,
            "Choose a final need denominator and barrier scope, then re-audit event rates and missingness before promotion.",
            ["result/alb2002_access_candidate_outcome_summary.csv", "result/alb2002_access_need_denominator_policy_summary.csv"],
        ),
        outcome_row(
            "forgone_or_barrier_cost_candidate",
            "access",
            "Cost-barrier access candidate",
            f"household_rows={metric_value(access, 'alb2002_access_candidate_household_rows')}; q01_need_rows={metric_value(access, 'alb2002_access_candidate_q01_need_rows')}",
            metric_value(access, "alb2002_access_candidate_composite_cost_rows"),
            metric_value(access, "alb2002_access_candidate_composite_cost_rate"),
            metric_value(access, "alb2002_access_candidate_composite_cost_weighted_rate"),
            f"q01_cost_difficulty_rows={metric_value(access_policy, 'alb2002_access_need_q01_cost_difficulty_rows')}; access_policy_rows={access_policy_rows}",
            "candidate_not_promoted",
            access_blocker,
            "Review whether payment difficulty, nonuse, referral, refusal, and medicine-discount variables should be separate outcomes or a composite.",
            ["result/alb2002_access_candidate_outcome_summary.csv"],
        ),
        outcome_row(
            "forgone_or_barrier_distance_candidate",
            "access",
            "Distance-barrier access candidate",
            f"household_rows={metric_value(access, 'alb2002_access_candidate_household_rows')}; q01_need_rows={metric_value(access, 'alb2002_access_candidate_q01_need_rows')}",
            metric_value(access, "alb2002_access_candidate_composite_distance_rows"),
            "",
            "",
            f"access_policy_low_event_rows={access_low_policy_rows}; candidate_low_event_rows={metric_value(access, 'alb2002_access_candidate_low_event_rate_rows')}",
            "low_event_candidate_not_promoted",
            "Distance-barrier candidate events are sparse and the access denominator is not accepted.",
            "Do not use as a standalone main outcome unless event-rate and denominator audits pass.",
            ["result/alb2002_access_candidate_outcome_summary.csv"],
        ),
        outcome_row(
            "forgone_or_barrier_supply_admin_candidate",
            "access",
            "Supply/admin access-barrier candidate",
            f"household_rows={metric_value(access, 'alb2002_access_candidate_household_rows')}; q01_need_rows={metric_value(access, 'alb2002_access_candidate_q01_need_rows')}",
            metric_value(access, "alb2002_access_candidate_composite_supply_admin_rows"),
            "",
            "",
            f"supply_admin_rows={metric_value(access_policy, 'alb2002_access_need_composite_supply_admin_barrier_rows')}; access_policy_rows={access_policy_rows}",
            "candidate_not_promoted",
            access_blocker,
            "Keep as a candidate component until barrier-scope semantics and denominator policy are accepted.",
            ["result/alb2002_access_need_denominator_policy_summary.csv"],
        ),
        outcome_row(
            "delayed_or_nonuse_candidate",
            "access",
            "Delayed, refused, referral-not-gone, or nonuse candidate",
            f"household_rows={metric_value(access, 'alb2002_access_candidate_household_rows')}; q01_need_rows={metric_value(access, 'alb2002_access_candidate_q01_need_rows')}",
            metric_value(access, "alb2002_access_candidate_composite_nonuse_rows"),
            "",
            "",
            f"delayed_help_rows={metric_value(access, 'alb2002_access_candidate_delayed_help_rows')}; referral_not_gone_rows={metric_value(access, 'alb2002_access_candidate_referral_not_gone_rows')}; refused_service_rows={metric_value(access, 'alb2002_access_candidate_refused_service_rows')}",
            "candidate_not_promoted",
            access_blocker,
            "Separate delayed care, nonuse, referral, and refusal semantics before treating this as a final access outcome.",
            ["result/alb2002_access_candidate_outcome_summary.csv"],
        ),
        outcome_row(
            "uhc_che10_or_access_candidate",
            "composite_uhc_failure",
            "CHE10 or any access barrier",
            "composite over non-promoted CHE10 and access candidates",
            metric_value(composite, "alb2002_uhc_composite_candidate_che10_or_access_rows"),
            metric_value(composite, "alb2002_uhc_composite_candidate_che10_or_access_rate"),
            metric_value(composite, "alb2002_uhc_composite_candidate_che10_or_access_weighted_rate"),
            f"source_che10_rows={metric_value(composite, 'alb2002_uhc_composite_candidate_source_che10_rows')}; source_access_any_rows={metric_value(composite, 'alb2002_uhc_composite_candidate_source_access_any_rows')}",
            "candidate_not_promoted",
            composite_blocker,
            "Promote only after both the financial and access component outcomes pass final policy and geography gates.",
            ["result/alb2002_uhc_composite_candidate_summary.csv"],
        ),
        outcome_row(
            "uhc_che25_or_access_candidate",
            "composite_uhc_failure",
            "CHE25 or any access barrier",
            "composite over non-promoted CHE25 and access candidates",
            metric_value(composite, "alb2002_uhc_composite_candidate_che25_or_access_rows"),
            metric_value(composite, "alb2002_uhc_composite_candidate_che25_or_access_rate"),
            metric_value(composite, "alb2002_uhc_composite_candidate_che25_or_access_weighted_rate"),
            f"source_che25_rows={metric_value(composite, 'alb2002_uhc_composite_candidate_source_che25_rows')}; source_access_any_rows={metric_value(composite, 'alb2002_uhc_composite_candidate_source_access_any_rows')}",
            "candidate_not_promoted",
            composite_blocker,
            "Use only as a temp diagnostic until component outcomes are promoted.",
            ["result/alb2002_uhc_composite_candidate_summary.csv"],
        ),
        outcome_row(
            "coping_failure_candidate",
            "composite_uhc_failure",
            "Health-cost coping candidate",
            "candidate coping count from non-promoted composite audit",
            metric_value(composite, "alb2002_uhc_composite_candidate_coping_rows"),
            "",
            "",
            f"composite_audit_rows={metric_value(composite, 'alb2002_uhc_composite_candidate_audit_rows')}; low_event_rows={metric_value(composite, 'alb2002_uhc_composite_candidate_low_event_rate_rows')}",
            "candidate_not_promoted",
            "Coping evidence is useful as a mechanism or secondary outcome candidate, but it is not accepted as a final UHC failure outcome.",
            "Review coping-module semantics and whether coping is pre/post-treatment before any final outcome or mechanism use.",
            ["result/alb2002_uhc_composite_candidate_summary.csv"],
        ),
    ]
    return rows


def build_summary(rows: list[dict[str, str]]) -> list[dict[str, str]]:
    candidate_statuses = {"candidate_not_promoted", "low_event_candidate_not_promoted"}
    return [
        summary_row("alb2002_outcome_blocker_resolution_rows", len(rows), "Outcome blocker rows consolidated."),
        summary_row("alb2002_outcome_blocker_financial_rows", sum(1 for row in rows if row["outcome_family"] == "financial_protection"), "Financial-protection outcome rows in the matrix."),
        summary_row("alb2002_outcome_blocker_access_rows", sum(1 for row in rows if row["outcome_family"] == "access"), "Access outcome rows in the matrix."),
        summary_row("alb2002_outcome_blocker_composite_rows", sum(1 for row in rows if row["outcome_family"] == "composite_uhc_failure"), "Composite UHC/coping outcome rows in the matrix."),
        summary_row("alb2002_outcome_blocker_candidate_not_promoted_rows", sum(1 for row in rows if row["promotion_status"] in candidate_statuses), "Candidate outcome rows with evidence but no final promotion."),
        summary_row("alb2002_outcome_blocker_low_event_candidate_rows", sum(1 for row in rows if row["promotion_status"] == "low_event_candidate_not_promoted"), "Sparse candidate outcome rows flagged as low-event."),
        summary_row("alb2002_outcome_blocker_hard_blocked_rows", sum(1 for row in rows if row["promotion_status"].startswith("hard_blocked")), "Outcome rows hard-blocked by missing required inputs."),
        summary_row("alb2002_outcome_blocker_outcome_ready_rows", sum(safe_int(row["outcome_ready_rows"]) for row in rows), "Rows ready for final outcome promotion; intentionally zero."),
        summary_row("alb2002_outcome_blocker_sdg382_ready_rows", sum(safe_int(row["sdg382_ready_rows"]) for row in rows), "Rows ready for SDG 3.8.2 promotion; intentionally zero."),
        summary_row("alb2002_outcome_blocker_climate_linkage_ready_rows", sum(safe_int(row["climate_linkage_ready_rows"]) for row in rows), "Rows ready for climate-linked outcome promotion; intentionally zero."),
        summary_row("alb2002_outcome_blocker_data_write_ready_rows", sum(safe_int(row["data_write_ready_rows"]) for row in rows), "Rows allowed for data/ writes by this outcome matrix; intentionally zero."),
        summary_row("alb2002_outcome_blocker_current_decision", DECISION, "Current consolidated ALB_2002 outcome promotion decision."),
    ]


def markdown_rows(rows: list[dict[str, str]], columns: list[str]) -> str:
    lines = ["| " + " | ".join(columns) + " |", "|" + "|".join("---" for _ in columns) + "|"]
    for item in rows:
        values = []
        for column in columns:
            value = str(item.get(column, "")).replace("\n", " ").replace("|", "/")
            if len(value) > 120:
                value = value[:117] + "..."
            values.append(value)
        lines.append("| " + " | ".join(values) + " |")
    return "\n".join(lines)


def write_report(rows: list[dict[str, str]], summary: list[dict[str, str]]) -> None:
    summary_table = "\n".join(f"| {item['metric']} | {item['value']} | {item['interpretation']} |" for item in summary)
    REPORT_PATH.write_text(
        f"""# ALB_2002 Outcome Blocker Resolution Matrix

Status: fail-closed outcome-promotion matrix. This consolidates ALB_2002 financial-protection, access, composite UHC, and coping outcome candidates into one promotion decision. It does not write `data/`, does not promote `data/household_outcomes.csv`, and does not treat SDG 3.8.2, CHE, access, composite, descriptive, predictive, causal, or policy-learning outcomes as complete.

## Summary

| Metric | Value | Interpretation |
|---|---:|---|
{summary_table}

## Outcome Matrix

{markdown_rows(rows, ['outcome_id', 'outcome_family', 'candidate_event_rows', 'candidate_event_rate', 'candidate_weighted_rate', 'promotion_status', 'outcome_ready_rows', 'data_write_ready_rows'])}

## Interpretation

- CHE10 and CHE25 total-budget candidates have useful period-aligned stress-test rates, but final OOP recall and inclusion policies are not accepted.
- SDG 3.8.2 remains hard-blocked because SPL, PPP/CPI or price-basis handling, and discretionary-budget construction are not accepted.
- Access outcomes have several candidate signals, but the need denominator, barrier scope, low-event flags, and climate-geography gate are unresolved.
- Composite UHC outcomes are mechanical combinations of non-promoted CHE and access candidates, so they cannot be promoted independently.

## Required Resolution

Before any final outcome write, a future step must promote a numerator policy, denominator policy, skip/missing policy, SDG denominator if used, access denominator/barrier rules, event-rate/missingness audit, benchmark comparison where feasible, and climate-geography gate. Until then, outcome-ready, climate-linkage-ready, and data-write-ready rows remain zero.

## Machine-Readable Outputs

- `temp/alb2002_outcome_blocker_resolution_matrix.csv`
- `result/alb2002_outcome_blocker_resolution_summary.csv`
""",
        encoding="utf-8",
    )


def main() -> None:
    ensure_dirs()
    rows = build_matrix()
    summary = build_summary(rows)
    write_csv(AUDIT_PATH, rows, AUDIT_COLUMNS)
    write_csv(SUMMARY_PATH, summary, SUMMARY_COLUMNS)
    write_report(rows, summary)
    append_log(TEMP_DIR / "audit_log.md", f"Built ALB_2002 outcome blocker resolution matrix rows={len(rows)} decision={DECISION}.")
    print(f"ALB_2002 outcome blocker resolution rows={len(rows)} decision={DECISION}.")


if __name__ == "__main__":
    main()
