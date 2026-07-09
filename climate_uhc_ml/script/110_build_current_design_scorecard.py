from __future__ import annotations

import csv
from typing import Any

from common import DATA_DIR, REPORT_DIR, RESULT_DIR, TEMP_DIR, append_log, ensure_dirs, write_csv


SCORECARD_PATH = RESULT_DIR / "design_scorecard.csv"
AUDIT_PATH = RESULT_DIR / "design_scorecard_current_audit.csv"
THRESHOLD_PATH = RESULT_DIR / "design_no_go_threshold_audit.csv"
SUMMARY_PATH = RESULT_DIR / "design_scorecard_current_summary.csv"
REPORT_PATH = REPORT_DIR / "design_scorecard_audit.md"

CURRENT_PREFIX = "current_"
DECISION = "fail_closed_design_scorecard_currently_no_go_for_estimation_or_policy_learning"

DESIGN_COLUMNS = [
    "design_id",
    "country_scope",
    "outcome",
    "exposure",
    "data_coverage",
    "outcome_validity",
    "exposure_precision",
    "sample_size",
    "event_rate",
    "climate_geography_linkage_quality",
    "identifying_variation",
    "pre-trend/placebo credibility",
    "model_stability",
    "policy_relevance",
    "ML usefulness",
    "journal potential",
    "go/no-go",
    "reason",
]

AUDIT_COLUMNS = [
    "check_id",
    "check_label",
    "status",
    "rows_checked",
    "passing_rows",
    "failing_rows",
    "evidence",
    "blocking_reason",
    "next_action",
]
THRESHOLD_COLUMNS = ["rule_id", "rule", "current_status", "evidence", "go_no_go", "required_action"]
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


def row_count(path) -> int:
    return len(read_csv_dicts(path))


def data_file_count() -> int:
    return sum(1 for path in DATA_DIR.rglob("*") if path.is_file()) if DATA_DIR.exists() else 0


def score(value: int) -> str:
    return str(max(0, min(5, int(value))))


def design_row(
    design_id: str,
    country_scope: str,
    outcome: str,
    exposure: str,
    scores: dict[str, int],
    go_no_go: str,
    reason: str,
) -> dict[str, str]:
    row = {
        "design_id": design_id,
        "country_scope": country_scope,
        "outcome": outcome,
        "exposure": exposure,
        "go/no-go": go_no_go,
        "reason": reason,
    }
    for column in DESIGN_COLUMNS:
        if column not in row:
            row[column] = score(scores.get(column, 0))
    return row


def audit_row(
    check_id: str,
    label: str,
    status: str,
    rows_checked: int,
    passing: int,
    evidence: str,
    block: str,
    next_action: str,
) -> dict[str, str]:
    return {
        "check_id": check_id,
        "check_label": label,
        "status": status,
        "rows_checked": str(rows_checked),
        "passing_rows": str(passing),
        "failing_rows": str(max(rows_checked - passing, 0)),
        "evidence": evidence,
        "blocking_reason": block,
        "next_action": next_action,
    }


def build_current_designs(base_rows: list[dict[str, str]]) -> tuple[list[dict[str, str]], list[dict[str, str]], list[dict[str, str]]]:
    linked = read_csv_dicts(RESULT_DIR / "alb2002_climate_outcome_linked_candidate_summary.csv")
    descriptive = read_csv_dicts(RESULT_DIR / "alb2002_linked_candidate_descriptive_summary.csv")
    minimum = read_csv_dicts(RESULT_DIR / "alb2002_minimum_recipe_promotion_summary.csv")
    promotion = read_csv_dicts(RESULT_DIR / "analysis_dataset_promotion_barrier_summary.csv")
    sample_gate = read_csv_dicts(RESULT_DIR / "sample_selection_gate_summary.csv")

    linked_rows = safe_int(metric_value(linked, "alb2002_climate_outcome_linked_candidate_rows"))
    linked_households = safe_int(metric_value(linked, "alb2002_climate_outcome_linked_candidate_household_rows"))
    linked_windows = safe_int(metric_value(linked, "alb2002_climate_outcome_linked_candidate_window_rows"))
    linked_combined = safe_int(metric_value(linked, "alb2002_climate_outcome_linked_candidate_combined_stress_rows"))
    linked_climate_ready = safe_int(metric_value(linked, "alb2002_climate_outcome_linked_candidate_climate_linkage_ready_rows"))
    linked_outcome_ready = safe_int(metric_value(linked, "alb2002_climate_outcome_linked_candidate_outcome_promotion_ready_rows"))
    linked_data_write = safe_int(metric_value(linked, "alb2002_climate_outcome_linked_candidate_data_write_ready_rows"))
    descriptive_cells = safe_int(metric_value(descriptive, "alb2002_linked_candidate_descriptive_cell_rows"))
    descriptive_che10 = safe_int(metric_value(descriptive, "alb2002_linked_candidate_descriptive_che10_or_access_households"))
    descriptive_che25 = safe_int(metric_value(descriptive, "alb2002_linked_candidate_descriptive_che25_or_access_households"))
    descriptive_ready = safe_int(metric_value(descriptive, "alb2002_linked_candidate_descriptive_data_write_ready_rows"))
    minimum_harmonized = safe_int(metric_value(minimum, "alb2002_minimum_recipe_promotion_harmonized_ready_rows"))
    minimum_outcome = safe_int(metric_value(minimum, "alb2002_minimum_recipe_promotion_outcome_ready_rows"))
    minimum_climate = safe_int(metric_value(minimum, "alb2002_minimum_recipe_promotion_climate_linkage_ready_rows"))
    promoted_rows = safe_int(metric_value(promotion, "analysis_dataset_promotion_promoted_rows"))
    data_files = safe_int(metric_value(promotion, "analysis_dataset_promotion_data_file_count", str(data_file_count())))
    failed_rules = sum(1 for row in sample_gate if row.get("status") == "fail")

    base_clean = [row for row in base_rows if not row.get("design_id", "").startswith(CURRENT_PREFIX)]
    current_designs = [
        design_row(
            "current_alb2002_temp_linked_candidate_financial_access_climate",
            "Albania ALB_2002 only",
            "Temp-only CHE10/CHE25-or-access candidate, both-failure candidate, and coping candidate; not promoted final outcomes",
            "NASA POWER fallback district-centroid within-candidate 1/3/6/12 month rainfall and temperature diagnostics; not CHIRPS/ERA5 historical anomalies",
            {
                "data_coverage": 4 if linked_households == 3599 else 2,
                "outcome_validity": 3 if descriptive_che10 > 0 and descriptive_che25 > 0 else 1,
                "exposure_precision": 1,
                "sample_size": 3 if linked_households >= 2000 else 1,
                "event_rate": 4 if descriptive_che10 > 0 and descriptive_che25 > 0 else 0,
                "climate_geography_linkage_quality": 1,
                "identifying_variation": 1,
                "pre-trend/placebo credibility": 0,
                "model_stability": 1,
                "policy_relevance": 3,
                "ML usefulness": 1,
                "journal potential": 1,
            },
            "no-go for estimation; go for source/boundary/baseline/outcome-resolution work",
            f"Temp candidate is mechanically rich but not promoted: linked_rows={linked_rows}; households={linked_households}; windows={linked_windows}; combined_stress={linked_combined}; descriptive_cells={descriptive_cells}; harmonized_ready={minimum_harmonized}; outcome_ready={linked_outcome_ready}; climate_ready={linked_climate_ready}; data_write_ready={linked_data_write}.",
        ),
        design_row(
            "current_multi_country_financial_protection_main",
            "multi-country",
            "Official SDG 3.8.2 plus CHE10/CHE25 financial-protection outcomes, preferred with access outcomes",
            "Primary CHIRPS rainfall and ERA5-Land temperature historical anomalies at verified GPS/admin geography",
            {
                "data_coverage": 2,
                "outcome_validity": 1,
                "exposure_precision": 0,
                "sample_size": 2,
                "event_rate": 0,
                "climate_geography_linkage_quality": 0,
                "identifying_variation": 0,
                "pre-trend/placebo credibility": 0,
                "model_stability": 0,
                "policy_relevance": 4,
                "ML usefulness": 0,
                "journal potential": 1,
            },
            "no-go for main multi-country paper under current evidence",
            f"Main go/no-go gates fail because promoted data_files={data_files}, promoted_rows={promoted_rows}, failed_no_go_rules={failed_rules}, and no value-verified six-country financial-protection sample exists.",
        ),
        design_row(
            "current_alb2002_descriptive_resource_candidate",
            "Albania ALB_2002 only",
            "Candidate UHC outcome-rate screen for audit readability only",
            "Diagnostic climate flags by household-window; no accepted climate exposure",
            {
                "data_coverage": 3,
                "outcome_validity": 2,
                "exposure_precision": 1,
                "sample_size": 3,
                "event_rate": 4 if descriptive_che10 > 0 else 0,
                "climate_geography_linkage_quality": 1,
                "identifying_variation": 0,
                "pre-trend/placebo credibility": 0,
                "model_stability": 0,
                "policy_relevance": 2,
                "ML usefulness": 0,
                "journal potential": 1,
            },
            "go for internal audit screen only; no-go for publishable descriptive estimates",
            f"Candidate screen has cell_rows={descriptive_cells}, CHE10-or-access households={descriptive_che10}, CHE25-or-access households={descriptive_che25}, but descriptive_data_write_ready={descriptive_ready}.",
        ),
    ]

    thresholds = [
        {
            "rule_id": "go_no_go_01_six_country_financial_sample",
            "rule": "If fewer than 6 countries have consumption, OOP health expenditure, usable geography, and survey timing, do not proceed with the main multi-country financial-protection paper.",
            "current_status": "failed",
            "evidence": f"promoted_data_files={data_files}; promoted_rows={promoted_rows}; sample_gate_failed_rules={failed_rules}",
            "go_no_go": "no-go_main_multi_country_financial_protection",
            "required_action": "Promote at least six value-verified country household datasets with OOP, budget, timing, geography, and weights.",
        },
        {
            "rule_id": "go_no_go_02_ten_double_failure_waves",
            "rule": "If fewer than 10 country-waves support both financial hardship and forgone care, keep UHC double failure secondary.",
            "current_status": "failed",
            "evidence": f"ALB_2002 has temp double-failure candidates only; linked_data_write_ready={linked_data_write}; outcome_ready={linked_outcome_ready}",
            "go_no_go": "no-go_double_failure_primary",
            "required_action": "Verify financial and access outcomes across at least ten country-waves before making double failure primary.",
        },
        {
            "rule_id": "go_no_go_03_geolocation_precision",
            "rule": "If geolocation is too weak for most countries, use admin aggregation and lower causal claims.",
            "current_status": "failed_for_causal_claims",
            "evidence": f"ALB_2002 climate_ready={linked_climate_ready}; NASA centroid diagnostics exist but historical boundaries and GPS/EA maps are not accepted.",
            "go_no_go": "no-go_point_or_strong_causal_claims",
            "required_action": "Verify historical boundaries, GPS/EA maps, or accepted crosswalks; then build CHIRPS/ERA5 historical anomalies.",
        },
        {
            "rule_id": "go_no_go_04_event_rates",
            "rule": "If event rates are below 3%, expand outcomes or countries; do not force rare-event ML.",
            "current_status": "candidate_only_not_final",
            "evidence": f"Candidate ALB_2002 CHE10-or-access households={descriptive_che10}; CHE25-or-access households={descriptive_che25}; final event rates remain unavailable.",
            "go_no_go": "no-go_final_event_rate_claims",
            "required_action": "Compute event rates only after promoted outcome and sample gates pass.",
        },
        {
            "rule_id": "go_no_go_05_predictive_transportability",
            "rule": "If leave-country-out predictive performance is poor, do not claim transportable targeting.",
            "current_status": "not_estimable",
            "evidence": "No promoted multi-country analysis data or predictive validation metrics exist.",
            "go_no_go": "no-go_transportable_targeting_claim",
            "required_action": "Estimate predictive models only after promoted multi-country outcome and climate-linked data exist.",
        },
        {
            "rule_id": "go_no_go_06_climate_lead_placebo",
            "rule": "If climate lead placebo predicts outcomes, treat causal design as weak.",
            "current_status": "not_estimable",
            "evidence": "No future climate lead variables or promoted reduced-form analysis data exist.",
            "go_no_go": "no-go_causal_claims",
            "required_action": "Construct future climate lead variables after primary exposure extraction and run placebo tests.",
        },
        {
            "rule_id": "go_no_go_07_policy_learning_value",
            "rule": "If CATE/policy learning does not beat simple rules out of sample, report null targeting value honestly.",
            "current_status": "rejected_until_reduced_form_passes",
            "evidence": "Causal ML/policy learning is explicitly rejected until reduced-form and placebo gates pass.",
            "go_no_go": "no-go_policy_learning_claim",
            "required_action": "Attempt CATE and policy learning only after credible reduced-form estimates and validation splits exist.",
        },
        {
            "rule_id": "go_no_go_08_descriptive_fallback",
            "rule": "If only descriptive evidence survives, write a descriptive data paper and do not claim causal effects.",
            "current_status": "not_yet_descriptive_paper_ready",
            "evidence": f"Current descriptive screen is temp-only; descriptive_cells={descriptive_cells}; promoted descriptive_data_write_ready={descriptive_ready}.",
            "go_no_go": "go_audit_only_no_go_descriptive_manuscript",
            "required_action": "Promote harmonized outcomes and climate-linked data before final descriptive prevalence, maps, and sample-flow claims.",
        },
    ]

    scorecard_rows = base_clean + current_designs
    audit = [
        audit_row(
            "metadata_scorecard_preserved",
            "Broad metadata scorecard rows are preserved before appending current fail-closed designs",
            "complete" if base_clean else "missing",
            len(base_rows),
            len(base_clean),
            f"base_rows={len(base_rows)}; preserved_non_current_rows={len(base_clean)}; current_rows_added={len(current_designs)}",
            "Metadata rows remain screening evidence only.",
            "Continue raw verification before estimation.",
        ),
        audit_row(
            "alb2002_current_candidate_design",
            "ALB_2002 current candidate is scored without promoting it to estimation",
            "complete_candidate_not_promoted" if linked_rows == 14396 and descriptive_cells == 108 else "partial_or_failed",
            linked_rows,
            linked_rows if linked_rows == 14396 and descriptive_cells == 108 else 0,
            f"linked_rows={linked_rows}; households={linked_households}; descriptive_cells={descriptive_cells}; climate_ready={linked_climate_ready}; outcome_ready={linked_outcome_ready}; data_write_ready={linked_data_write}",
            "Candidate rows are not analysis-ready and cannot be used for predictive, causal, or policy-learning claims.",
            "Resolve outcome, harmonization, geography, primary-source, baseline, and placebo gates.",
        ),
        audit_row(
            "go_no_go_thresholds",
            "Objective go/no-go thresholds are explicitly evaluated against current evidence",
            "complete_fail_closed" if len(thresholds) == 8 else "partial_or_failed",
            len(thresholds),
            len(thresholds),
            f"threshold_rows={len(thresholds)}; failed_or_not_estimable={sum(1 for row in thresholds if row['current_status'] != 'passed')}; decision={DECISION}",
            "All estimation and policy-learning thresholds remain no-go or not estimable.",
            "Use this scorecard to prioritize raw access, outcome promotion, and climate linkage rather than model fitting.",
        ),
        audit_row(
            "promotion_guardrail",
            "Design scorecard does not create promoted data or model claims",
            "blocked",
            len(scorecard_rows),
            0,
            f"scorecard_rows={len(scorecard_rows)}; data_files={data_files}; promoted_rows={promoted_rows}; current_decision={DECISION}",
            "A design scorecard is planning and audit evidence, not empirical estimation.",
            "Keep completion criteria for data, descriptive, predictive, causal, and robustness outputs incomplete until promoted inputs exist.",
        ),
    ]
    return scorecard_rows, audit, thresholds


def summary_row(metric: str, value: Any, interpretation: str) -> dict[str, str]:
    return {"metric": metric, "value": str(value), "interpretation": interpretation}


def build_summary(scorecard: list[dict[str, str]], audit: list[dict[str, str]], thresholds: list[dict[str, str]]) -> list[dict[str, str]]:
    current_rows = [row for row in scorecard if row.get("design_id", "").startswith(CURRENT_PREFIX)]
    return [
        summary_row("design_scorecard_rows", len(scorecard), "Total design scorecard rows after current fail-closed refresh."),
        summary_row("design_scorecard_current_rows", len(current_rows), "Current-state design rows appended to the metadata scorecard."),
        summary_row("design_scorecard_audit_rows", len(audit), "Audit rows for the current design scorecard refresh."),
        summary_row("design_no_go_threshold_rows", len(thresholds), "Go/no-go threshold audit rows."),
        summary_row("design_no_go_failed_or_not_estimable_rows", sum(1 for row in thresholds if row["current_status"] != "passed"), "Threshold rows that are failed, candidate-only, or not estimable."),
        summary_row("design_scorecard_data_write_ready_rows", 0, "Rows allowed for data/ write by this design scorecard; intentionally zero."),
        summary_row("design_scorecard_current_decision", DECISION, "Current design scorecard decision."),
    ]


def markdown_rows(rows: list[dict[str, Any]], columns: list[str], limit: int = 25) -> str:
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


def write_report(scorecard: list[dict[str, str]], audit: list[dict[str, str]], thresholds: list[dict[str, str]], summary: list[dict[str, str]]) -> None:
    summary_table = "\n".join(f"| {row['metric']} | {row['value']} | {row['interpretation']} |" for row in summary)
    current = [row for row in scorecard if row.get("design_id", "").startswith(CURRENT_PREFIX)]
    REPORT_PATH.write_text(
        f"""# Current Design Scorecard Audit

Status: fail-closed design tournament refresh. This preserves the broad metadata scorecard and appends current-state design rows using the ALB_2002 temp-only outcome, climate, linkage, and descriptive-screen audits. It does not create analysis data, estimate models, or satisfy predictive, causal, robustness, or final descriptive criteria.

## Summary

| Metric | Value | Interpretation |
|---|---:|---|
{summary_table}

## Current-State Design Rows

{markdown_rows(current, ['design_id', 'country_scope', 'outcome_validity', 'exposure_precision', 'sample_size', 'event_rate', 'climate_geography_linkage_quality', 'identifying_variation', 'pre-trend/placebo credibility', 'go/no-go', 'reason'], limit=10)}

## Go/No-Go Thresholds

{markdown_rows(thresholds, THRESHOLD_COLUMNS, limit=20)}

## Audit

{markdown_rows(audit, ['check_id', 'status', 'rows_checked', 'passing_rows', 'evidence', 'blocking_reason'])}

## Interpretation

- ALB_2002 is now the strongest inspected local candidate, but it remains temp-only.
- Candidate event rates and linked climate flags improve prioritization, not empirical identification.
- Main multi-country, predictive, causal, causal-ML, policy-learning, and robustness claims remain no-go until promoted outcomes, harmonized data, accepted climate exposure, and placebo-ready designs exist.

## Machine-Readable Outputs

- `result/design_scorecard.csv`
- `result/design_scorecard_current_audit.csv`
- `result/design_no_go_threshold_audit.csv`
- `result/design_scorecard_current_summary.csv`
""",
        encoding="utf-8",
    )


def main() -> None:
    ensure_dirs()
    base_rows = read_csv_dicts(SCORECARD_PATH)
    scorecard, audit, thresholds = build_current_designs(base_rows)
    summary = build_summary(scorecard, audit, thresholds)
    write_csv(SCORECARD_PATH, scorecard, DESIGN_COLUMNS)
    write_csv(AUDIT_PATH, audit, AUDIT_COLUMNS)
    write_csv(THRESHOLD_PATH, thresholds, THRESHOLD_COLUMNS)
    write_csv(SUMMARY_PATH, summary, SUMMARY_COLUMNS)
    write_report(scorecard, audit, thresholds, summary)
    append_log(TEMP_DIR / "audit_log.md", f"Built current design scorecard rows={len(scorecard)} decision={DECISION}.")
    print(f"Current design scorecard rows={len(scorecard)} decision={DECISION}.")


if __name__ == "__main__":
    main()
