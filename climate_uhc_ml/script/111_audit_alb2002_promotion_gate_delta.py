from __future__ import annotations

import csv
from typing import Any

from common import REPORT_DIR, RESULT_DIR, TEMP_DIR, append_log, ensure_dirs, write_csv


AUDIT_PATH = TEMP_DIR / "alb2002_promotion_gate_delta_audit.csv"
SUMMARY_PATH = RESULT_DIR / "alb2002_promotion_gate_delta_summary.csv"
REPORT_PATH = REPORT_DIR / "alb2002_promotion_gate_delta_audit.md"

DECISION = "partial_gate_delta_documented_keep_data_empty_until_outcome_sdg_geography_gates_pass"

AUDIT_COLUMNS = [
    "gate_id",
    "gate_label",
    "required_for",
    "prior_status",
    "delta_status",
    "evidence_strength",
    "promotion_ready_rows",
    "data_write_ready_rows",
    "evidence",
    "remaining_blocker",
    "next_action",
]
SUMMARY_COLUMNS = ["metric", "value", "interpretation"]


def read_csv_dicts(path) -> list[dict[str, str]]:
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


def gate_lookup(rows: list[dict[str, str]]) -> dict[str, dict[str, str]]:
    return {row.get("gate_id", ""): row for row in rows}


def audit_row(
    gates: dict[str, dict[str, str]],
    gate_id: str,
    delta_status: str,
    evidence_strength: str,
    promotion_ready_rows: int,
    evidence: str,
    remaining_blocker: str,
    next_action: str,
) -> dict[str, str]:
    prior = gates.get(gate_id, {})
    return {
        "gate_id": gate_id,
        "gate_label": prior.get("gate_label", gate_id),
        "required_for": prior.get("required_for", ""),
        "prior_status": prior.get("current_status", ""),
        "delta_status": delta_status,
        "evidence_strength": evidence_strength,
        "promotion_ready_rows": str(promotion_ready_rows),
        "data_write_ready_rows": "0",
        "evidence": evidence,
        "remaining_blocker": remaining_blocker,
        "next_action": next_action,
    }


def summary_row(metric: str, value: Any, interpretation: str) -> dict[str, str]:
    return {"metric": metric, "value": str(value), "interpretation": interpretation}


def count_status(rows: list[dict[str, str]], field: str, value: str) -> int:
    return sum(1 for row in rows if row.get(field) == value)


def build_audit() -> list[dict[str, str]]:
    gates = gate_lookup(read_csv_dicts(TEMP_DIR / "alb2002_minimum_recipe_promotion_gate_checklist.csv"))
    core = read_csv_dicts(RESULT_DIR / "alb2002_household_core_candidate_summary.csv")
    weight = read_csv_dicts(RESULT_DIR / "alb2002_weight_design_evidence_summary.csv")
    sample = read_csv_dicts(RESULT_DIR / "alb2002_sample_design_documentation_summary.csv")
    sdg = read_csv_dicts(RESULT_DIR / "alb2002_consumption_sdg_denominator_policy_summary.csv")
    construction = read_csv_dicts(RESULT_DIR / "alb2002_consumption_construction_source_summary.csv")
    aggregate = read_csv_dicts(RESULT_DIR / "alb2002_consumption_aggregate_metadata_crosswalk_summary.csv")
    period = read_csv_dicts(RESULT_DIR / "alb2002_period_aligned_che_policy_summary.csv")
    skip = read_csv_dicts(RESULT_DIR / "alb2002_oop_skip_value_decision_summary.csv")
    access = read_csv_dicts(RESULT_DIR / "alb2002_access_need_denominator_policy_summary.csv")
    analysis = read_csv_dicts(RESULT_DIR / "alb2002_analysis_candidate_readiness_summary.csv")
    local_geo = read_csv_dicts(RESULT_DIR / "alb2002_local_geography_artifact_summary.csv")
    gadm = read_csv_dicts(RESULT_DIR / "alb2002_gadm_boundary_lead_summary.csv")
    centroid = read_csv_dicts(RESULT_DIR / "alb2002_climate_centroid_exposure_summary.csv")
    linked = read_csv_dicts(RESULT_DIR / "alb2002_climate_outcome_linked_candidate_summary.csv")

    core_rows = safe_int(metric_value(core, "alb2002_household_core_candidate_rows"))
    merge_modules = safe_int(metric_value(core, "alb2002_merge_modules_complete_base_coverage"))
    total_consumption = safe_int(metric_value(core, "alb2002_households_with_total_consumption"))
    survey_month = safe_int(metric_value(core, "alb2002_households_with_survey_month"))
    interview_date = safe_int(metric_value(core, "alb2002_households_with_interview_date"))
    weight_rows = safe_int(metric_value(weight, "alb2002_weight_design_positive_weight_rows"))
    weight_matches = safe_int(metric_value(weight, "alb2002_weight_design_candidate_key_match_rows"))
    sample_doc = safe_int(metric_value(sample, "alb2002_sample_design_documentation_ready_rows"))
    sample_concordance = safe_int(metric_value(sample, "alb2002_sample_design_raw_design_concordance_rows"))
    denominator_docs = safe_int(metric_value(construction, "alb2002_consumption_construction_documentation_ready_rows"))
    denominator_mapping = safe_int(metric_value(aggregate, "alb2002_consumption_aggregate_crosswalk_released_variable_mapping_ready_rows"))
    spl_ready = safe_int(metric_value(sdg, "alb2002_consumption_sdg_spl_ready_rows"))
    ppp_ready = safe_int(metric_value(sdg, "alb2002_consumption_sdg_ppp_cpi_ready_rows"))
    discretionary_ready = safe_int(metric_value(sdg, "alb2002_consumption_sdg_discretionary_budget_ready_rows"))
    che_period = safe_int(metric_value(period, "alb2002_period_aligned_che_period_alignment_ready_rows"))
    zero_skip = safe_int(metric_value(skip, "alb2002_oop_skip_value_zero_skip_policy_ready_rows"))
    oop_recall_ready = safe_int(metric_value(skip, "alb2002_oop_skip_value_oop_recall_scope_ready_rows"))
    oop_inclusion_ready = safe_int(metric_value(skip, "alb2002_oop_skip_value_oop_inclusion_scope_ready_rows"))
    access_rows = safe_int(metric_value(access, "alb2002_access_need_denominator_policy_rows"))
    access_low_event = safe_int(metric_value(access, "alb2002_access_need_low_event_rate_rows"))
    access_recipe_ready = safe_int(metric_value(access, "alb2002_access_need_recipe_ready_rows"))
    local_coordinate_ready = safe_int(metric_value(local_geo, "alb2002_local_geo_artifact_local_coordinate_ready_rows"))
    local_boundary_ready = safe_int(metric_value(local_geo, "alb2002_local_geo_artifact_local_boundary_ready_rows"))
    gadm_historical_ready = safe_int(metric_value(gadm, "alb2002_gadm_boundary_lead_historical_2002_ready_rows"))
    centroid_exposures = safe_int(metric_value(centroid, "alb2002_climate_centroid_exposure_rows"))
    linked_rows = safe_int(metric_value(linked, "alb2002_climate_outcome_linked_candidate_rows"))
    analysis_complete = safe_int(metric_value(analysis, "alb2002_analysis_candidate_complete_candidate_gates"))
    analysis_missing = safe_int(metric_value(analysis, "alb2002_analysis_candidate_missing_gates"))

    rows = [
        audit_row(
            gates,
            "household_frame",
            "review_ready_not_promoted" if core_rows == 3599 and merge_modules == 7 else "still_blocked",
            "strong_household_frame_evidence",
            0,
            f"core_rows={core_rows}; complete_base_coverage_modules={merge_modules}; analysis_complete_gates={analysis_complete}; analysis_missing_gates={analysis_missing}",
            "Minimum recipe still keeps recipe-ready and harmonized-promotion rows at zero.",
            "Manually review the assembled household-frame lineage and decide whether a non-climate harmonized core can be scoped separately from outcome/climate gates.",
        ),
        audit_row(
            gates,
            "survey_weight",
            "documented_candidate_not_promoted" if weight_rows == 3599 and weight_matches == 3599 and sample_doc == 1 else "still_blocked",
            "strong_weight_and_design_evidence",
            0,
            f"positive_weight_rows={weight_rows}; key_match_rows={weight_matches}; sample_documentation_ready={sample_doc}; raw_design_concordance={sample_concordance}",
            "Weight target-population, normalization, and variance-use decisions are documented but not accepted for final weighted inference.",
            "Create a weight-use decision note before any weighted descriptive prevalence or model fitting.",
        ),
        audit_row(
            gates,
            "interview_timing",
            "review_ready_not_promoted" if survey_month == 3599 and interview_date == 3599 else "still_blocked",
            "strong_month_date_coverage",
            0,
            f"survey_month_rows={survey_month}; interview_date_rows={interview_date}",
            "Timing alone cannot promote climate linkage while geography and primary climate-source gates are blocked.",
            "Preserve survey month/date lineage and combine it only with an accepted geography source.",
        ),
        audit_row(
            gates,
            "consumption_denominator",
            "documented_total_budget_not_sdg_ready" if total_consumption == 3599 and denominator_docs >= 9 and denominator_mapping >= 3 else "still_blocked",
            "strong_che_denominator_evidence_but_no_sdg_discretionary_budget",
            0,
            f"total_consumption_rows={total_consumption}; construction_documentation_ready={denominator_docs}; released_mapping_ready={denominator_mapping}; spl_ready={spl_ready}; ppp_cpi_ready={ppp_ready}; discretionary_budget_ready={discretionary_ready}",
            "CHE denominator is documented, but SDG 3.8.2 discretionary-budget inputs remain absent.",
            "Allow CHE denominator review to proceed while keeping SDG 3.8.2 blocked until SPL, PPP/CPI, and discretionary-budget inputs are built.",
        ),
        audit_row(
            gates,
            "oop_aggregation",
            "candidate_policy_not_promoted" if che_period == 3 and zero_skip >= 4 else "still_blocked",
            "moderate_oop_policy_evidence",
            0,
            f"period_alignment_ready_rows={che_period}; zero_skip_policy_ready_rows={zero_skip}; recall_scope_ready={oop_recall_ready}; inclusion_scope_ready={oop_inclusion_ready}",
            "A single accepted OOP recall and inclusion-scope policy has not been promoted.",
            "Write an explicit OOP numerator decision separating CHE10/CHE25 stress tests from final outcome construction.",
        ),
        audit_row(
            gates,
            "health_need_access",
            "candidate_policy_not_promoted" if access_rows >= 20 else "still_blocked",
            "moderate_access_policy_evidence",
            0,
            f"access_policy_rows={access_rows}; low_event_rate_rows={access_low_event}; recipe_ready_rows={access_recipe_ready}",
            "Need/care/access denominators and barrier scope are audited but not accepted as final outcomes.",
            "Choose denominator and barrier rules, then re-audit event rates and low-event-rate flags before promotion.",
        ),
        audit_row(
            gates,
            "climate_geography",
            "hard_blocked",
            "hard_blocker",
            0,
            f"local_coordinate_ready={local_coordinate_ready}; local_boundary_ready={local_boundary_ready}; gadm_historical_2002_ready={gadm_historical_ready}; centroid_exposure_rows={centroid_exposures}",
            "No accepted 2001/2002 boundary, GPS, coordinate, or EA-map artifact supports promoted climate linkage.",
            "Obtain or verify historical district/commune boundary evidence or an accepted coordinate artifact before any climate exposure write.",
        ),
        audit_row(
            gates,
            "outcome_promotion",
            "hard_blocked",
            "hard_blocker",
            0,
            f"oop_recall_scope_ready={oop_recall_ready}; oop_inclusion_scope_ready={oop_inclusion_ready}; access_recipe_ready={access_recipe_ready}; spl_ready={spl_ready}; discretionary_budget_ready={discretionary_ready}",
            "Outcome promotion remains blocked by unaccepted OOP numerator, access denominator, and SDG input policies.",
            "Promote CHE/access outcomes only after numerator, denominator, skip, missing, benchmark, and access-denominator decisions pass.",
        ),
        audit_row(
            gates,
            "harmonized_dataset_promotion",
            "hard_blocked",
            "hard_blocker",
            0,
            f"analysis_complete_gates={analysis_complete}; analysis_missing_gates={analysis_missing}; linked_rows={linked_rows}",
            "The existing project gate requires the minimum recipe and downstream outcome/climate separation to pass before any data/ write.",
            "Keep `data/harmonized_household.csv` absent until a reviewed promotion recipe explicitly permits a scoped harmonized household core.",
        ),
        audit_row(
            gates,
            "climate_dataset_promotion",
            "hard_blocked",
            "hard_blocker",
            0,
            f"centroid_exposure_rows={centroid_exposures}; linked_rows={linked_rows}; local_coordinate_ready={local_coordinate_ready}; gadm_historical_2002_ready={gadm_historical_ready}",
            "Climate exposure and linked-data promotion remain blocked despite temp-only centroid diagnostics.",
            "Do not write `data/climate_exposures_*` or `data/climate_linked_household.csv` until historical geography, primary-source, baseline, and outcome gates pass.",
        ),
    ]
    return rows


def build_summary(rows: list[dict[str, str]]) -> list[dict[str, str]]:
    return [
        summary_row("alb2002_promotion_gate_delta_rows", len(rows), "Gate delta rows audited."),
        summary_row("alb2002_promotion_gate_delta_review_ready_rows", count_status(rows, "delta_status", "review_ready_not_promoted"), "Gates with strong evidence that are ready for manual recipe review but not data promotion."),
        summary_row("alb2002_promotion_gate_delta_documented_candidate_rows", sum(1 for row in rows if row["delta_status"].endswith("not_promoted") or row["delta_status"].startswith("documented_") or row["delta_status"].startswith("candidate_")), "Evidence-rich candidate gates still not promoted."),
        summary_row("alb2002_promotion_gate_delta_hard_blocked_rows", count_status(rows, "delta_status", "hard_blocked"), "Hard blocked gates."),
        summary_row("alb2002_promotion_gate_delta_promotion_ready_rows", sum(safe_int(row["promotion_ready_rows"]) for row in rows), "Rows ready for promotion by this delta audit; intentionally zero."),
        summary_row("alb2002_promotion_gate_delta_data_write_ready_rows", sum(safe_int(row["data_write_ready_rows"]) for row in rows), "Rows allowed for data/ write by this delta audit; intentionally zero."),
        summary_row("alb2002_promotion_gate_delta_decision", DECISION, "Current ALB_2002 promotion-gate delta decision."),
    ]


def markdown_rows(rows: list[dict[str, str]], columns: list[str]) -> str:
    lines = ["| " + " | ".join(columns) + " |", "|" + "|".join("---" for _ in columns) + "|"]
    for row in rows:
        lines.append("| " + " | ".join(str(row.get(col, "")).replace("\n", " ") for col in columns) + " |")
    return "\n".join(lines)


def write_report(rows: list[dict[str, str]], summary: list[dict[str, str]]) -> None:
    summary_table = "\n".join(f"| {row['metric']} | {row['value']} | {row['interpretation']} |" for row in summary)
    REPORT_PATH.write_text(
        f"""# ALB_2002 Promotion Gate Delta Audit

Status: partial gate-delta audit. This separates ALB_2002 gates with strong local evidence from hard blockers. It does not write `data/`, does not declare a harmonized household dataset ready, and does not relax outcome, SDG 3.8.2, climate-geography, primary climate-source, baseline, prediction, causal, or robustness gates.

## Summary

| Metric | Value | Interpretation |
|---|---:|---|
{summary_table}

## Gate Delta Rows

{markdown_rows(rows, ['gate_id', 'prior_status', 'delta_status', 'evidence_strength', 'promotion_ready_rows', 'data_write_ready_rows', 'remaining_blocker'])}

## Interpretation

- Household frame, survey timing, and survey-design evidence are now rich enough for manual recipe review, but this audit still permits zero `data/` writes.
- Consumption has documented total-budget evidence for CHE review, but SDG 3.8.2 remains blocked by SPL, PPP/CPI, and discretionary-budget inputs.
- OOP and access candidates have useful policy diagnostics, but final numerator, denominator, skip, and low-event-rate decisions are not accepted.
- Climate geography is the binding hard blocker for any climate exposure or climate-linked analytical dataset.

## Machine-Readable Outputs

- `temp/alb2002_promotion_gate_delta_audit.csv`
- `result/alb2002_promotion_gate_delta_summary.csv`
""",
        encoding="utf-8",
    )


def main() -> None:
    ensure_dirs()
    rows = build_audit()
    summary = build_summary(rows)
    write_csv(AUDIT_PATH, rows, AUDIT_COLUMNS)
    write_csv(SUMMARY_PATH, summary, SUMMARY_COLUMNS)
    write_report(rows, summary)
    append_log(TEMP_DIR / "audit_log.md", f"Built ALB_2002 promotion gate delta rows={len(rows)} decision={DECISION}.")
    print(f"ALB_2002 promotion gate delta rows={len(rows)} decision={DECISION}.")


if __name__ == "__main__":
    main()
