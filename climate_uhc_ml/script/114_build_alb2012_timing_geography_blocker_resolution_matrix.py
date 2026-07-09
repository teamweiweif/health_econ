from __future__ import annotations

import csv
from pathlib import Path
from typing import Any

from common import REPORT_DIR, RESULT_DIR, TEMP_DIR, append_log, ensure_dirs, write_csv


AUDIT_PATH = TEMP_DIR / "alb2012_timing_geography_blocker_resolution_matrix.csv"
SUMMARY_PATH = RESULT_DIR / "alb2012_timing_geography_blocker_resolution_summary.csv"
REPORT_PATH = REPORT_DIR / "alb2012_timing_geography_blocker_resolution_matrix.md"

DECISION = "blocked_alb2012_no_timing_geography_fallback_ready"

ALB2012_IDNO = "ALB_2012_LSMS_v01_M_v01_A_PUF"

AUDIT_COLUMNS = [
    "blocker_id",
    "blocker_family",
    "evidence_label",
    "evidence_rows",
    "household_rows_or_coverage",
    "promotion_status",
    "interview_timing_ready_rows",
    "geography_ready_rows",
    "outcome_ready_rows",
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


def first_row(rows: list[dict[str, str]], field: str, value: str) -> dict[str, str]:
    return next((row for row in rows if row.get(field) == value), {})


def max_int(rows: list[dict[str, str]], field: str) -> int:
    return max((safe_int(row.get(field), 0) for row in rows), default=0)


def summary_row(metric: str, value: Any, interpretation: str) -> dict[str, str]:
    return {"metric": metric, "value": str(value), "interpretation": interpretation}


def row(
    blocker_id: str,
    blocker_family: str,
    evidence_label: str,
    evidence_rows: Any,
    household_rows_or_coverage: str,
    promotion_status: str,
    blocking_reason: str,
    next_resolution_step: str,
    evidence_sources: list[str],
) -> dict[str, str]:
    return {
        "blocker_id": blocker_id,
        "blocker_family": blocker_family,
        "evidence_label": evidence_label,
        "evidence_rows": str(evidence_rows),
        "household_rows_or_coverage": household_rows_or_coverage,
        "promotion_status": promotion_status,
        "interview_timing_ready_rows": "0",
        "geography_ready_rows": "0",
        "outcome_ready_rows": "0",
        "climate_linkage_ready_rows": "0",
        "data_write_ready_rows": "0",
        "blocking_reason": blocking_reason,
        "next_resolution_step": next_resolution_step,
        "evidence_sources": "; ".join(evidence_sources),
    }


def build_matrix() -> list[dict[str, str]]:
    timing_geo = read_csv_dicts(RESULT_DIR / "alb2012_timing_geography_exhaustive_summary.csv")
    timing_geo_audit = read_csv_dicts(TEMP_DIR / "alb2012_timing_geography_exhaustive_audit.csv")
    questionnaire = read_csv_dicts(RESULT_DIR / "alb2012_questionnaire_timing_field_summary.csv")
    provisional = read_csv_dicts(RESULT_DIR / "alb2012_provisional_outcome_feasibility_summary.csv")
    semantics = read_csv_dicts(RESULT_DIR / "alb2012_outcome_semantics_raw_value_summary.csv")
    first_analysis = read_csv_dicts(RESULT_DIR / "albania_first_analysis_promotion_summary.csv")
    wave_ranking = read_csv_dicts(RESULT_DIR / "albania_first_analysis_promotion_wave_ranking.csv")
    alb2012_wave = first_row(wave_ranking, "idno", ALB2012_IDNO)

    psu_rows = [
        item for item in timing_geo_audit if item.get("candidate_role") == "psu_cluster_key"
    ]
    psu_distinct = max_int(psu_rows, "distinct_values")

    return [
        row(
            "raw_household_interview_timing_values",
            "timing",
            "Raw SPSS household interview date/month candidates",
            metric_value(timing_geo, "alb2012_interview_timing_candidate_rows"),
            f"verified_interview_timing_rows={metric_value(timing_geo, 'alb2012_interview_timing_verified_rows')}",
            "hard_blocked_missing_raw_interview_timing",
            "The exhaustive raw-file scan did not verify household interview date or month values.",
            "Obtain a raw household control module, fieldwork dates, or official fieldwork-period metadata linkable to household records.",
            ["result/alb2012_timing_geography_exhaustive_summary.csv"],
        ),
        row(
            "questionnaire_control_sheet_timing_fields",
            "timing",
            "Questionnaire DATE/BEGIN/END/STATUS/VISIT design fields",
            metric_value(questionnaire, "alb2012_questionnaire_timing_field_rows"),
            f"visit_rows={metric_value(questionnaire, 'alb2012_questionnaire_timing_visit_rows')}; raw_gap_rows={metric_value(questionnaire, 'alb2012_questionnaire_timing_raw_gap_rows')}",
            "hard_blocked_questionnaire_design_not_raw_value",
            "Questionnaire timing/control fields document form design, not verified raw household timing values in the public SPSS modules.",
            "Trace the control-sheet fields to raw household values or obtain the omitted control module before using them for exposure windows.",
            ["temp/alb2012_questionnaire_timing_field_audit.csv", "result/alb2012_questionnaire_timing_field_summary.csv"],
        ),
        row(
            "official_fieldwork_period_metadata",
            "timing",
            "Official fieldwork-period fallback metadata",
            "0",
            "locally_verified_official_fieldwork_period_rows=0",
            "hard_blocked_no_official_fieldwork_period",
            "No locally verified official fieldwork-period metadata was captured that can replace household-level timing.",
            "Search official study documents, fieldwork reports, or DDI notes for a citable fieldwork period and document whether month-level exposure windows are defensible.",
            ["report/alb2012_timing_geography_exhaustive_audit.md", "report/alb2012_questionnaire_timing_field_audit.md"],
        ),
        row(
            "psu_cluster_keys_without_coordinates",
            "geography",
            "PSU/cluster keys in raw modules",
            metric_value(timing_geo, "alb2012_psu_cluster_key_rows"),
            f"max_distinct_psu_values={psu_distinct}; household_base_match_rows_up_to={metric_value(timing_geo, 'alb2012_coarse_geography_household_rows')}",
            "hard_blocked_cluster_keys_no_coordinates",
            "PSU keys may support merges, but they do not provide coordinates or an official admin crosswalk for climate linkage.",
            "Obtain cluster coordinates, an official PSU-to-admin crosswalk, or a documented sampling-frame geography file.",
            ["temp/alb2012_timing_geography_exhaustive_audit.csv"],
        ),
        row(
            "coarse_prefecture_region_geography",
            "geography",
            "Coarse prefecture/region/urban geography fields",
            metric_value(timing_geo, "alb2012_coarse_full_coverage_geography_candidate_rows"),
            f"coarse_geography_household_rows={metric_value(timing_geo, 'alb2012_coarse_geography_household_rows')}",
            "hard_blocked_coarse_geography_no_timing_no_gps",
            "Prefecture/region/urban fields cover households but remain coarse, non-GPS geography without verified interview timing.",
            "Validate whether official prefecture/region climate aggregation is acceptable and pair it with household timing or a defensible fieldwork-period fallback.",
            ["result/alb2012_timing_geography_exhaustive_summary.csv", "result/alb2012_raw_core_feasibility_summary.csv"],
        ),
        row(
            "gps_coordinate_candidates",
            "geography",
            "Raw GPS/coordinate candidates",
            metric_value(timing_geo, "alb2012_coordinate_candidate_rows"),
            "coordinate_candidate_rows=0",
            "hard_blocked_no_coordinate_candidates",
            "No raw coordinate/GPS candidates were found in the local ALB_2012 raw files.",
            "Obtain restricted GPS, cluster coordinates, or an accepted admin-polygon aggregation plan before climate linkage.",
            ["result/alb2012_timing_geography_exhaustive_summary.csv"],
        ),
        row(
            "provisional_outcome_candidates",
            "outcome",
            "Provisional OOP/access/need stress-test outcomes",
            metric_value(provisional, "alb2012_provisional_outcome_audit_rows"),
            f"outcome_base_rows={metric_value(provisional, 'alb2012_provisional_outcome_base_rows')}; oop_4w_positive_rows={metric_value(provisional, 'alb2012_provisional_oop_4w_positive_rows')}; access_proxy_rows={metric_value(provisional, 'alb2012_provisional_access_proxy_rows')}",
            "hard_blocked_outcome_not_final_no_timing_geography",
            "Outcome candidates are diagnostic only because timing, geography, recall-period, and semantics gates are unresolved.",
            "Resolve timing/geography first, then finalize OOP numerator, denominator, recall-period, and access-need policies.",
            ["temp/alb2012_provisional_outcome_feasibility_audit.csv", "result/alb2012_provisional_outcome_feasibility_summary.csv"],
        ),
        row(
            "raw_outcome_semantics_candidates",
            "outcome",
            "Raw health OOP/access/coping semantics",
            metric_value(semantics, "alb2012_outcome_semantics_raw_value_audit_rows"),
            f"financial_oop_rows={metric_value(semantics, 'alb2012_outcome_semantics_financial_oop_candidate_rows')}; access_rows={metric_value(semantics, 'alb2012_outcome_semantics_access_candidate_rows')}; complete_household_merge_coverage_rows={metric_value(semantics, 'alb2012_outcome_semantics_rows_with_complete_household_merge_coverage')}",
            "hard_blocked_semantics_units_recall_skip_patterns",
            "Raw outcome semantics are useful, but units, recall periods, skip patterns, and payment-scope rules are not accepted.",
            "Manually review OOP/access units, missing codes, gifts/payments, skip patterns, and service-quality proxy semantics before promotion.",
            ["temp/alb2012_outcome_semantics_raw_value_audit.csv", "result/alb2012_outcome_semantics_raw_value_summary.csv"],
        ),
        row(
            "climate_linkage_promotion_gate",
            "promotion_gate",
            "Combined ALB_2012 climate-linkage gate",
            "0",
            f"raw_core_climate_ready=0; timing_geo_climate_ready={metric_value(timing_geo, 'alb2012_climate_linkage_ready_rows')}; questionnaire_climate_ready={metric_value(questionnaire, 'alb2012_questionnaire_timing_climate_linkage_ready_rows')}",
            "hard_blocked_no_climate_linkage_ready_rows",
            "No ALB_2012 evidence source currently supplies both defensible timing and geography for climate exposure construction.",
            "Re-run the timing/geography, questionnaire timing, and outcome audits only after new timing or geography source evidence is obtained.",
            ["result/alb2012_timing_geography_exhaustive_summary.csv", "result/alb2012_questionnaire_timing_field_summary.csv"],
        ),
        row(
            "first_analysis_fallback_promotion_gate",
            "promotion_gate",
            "Albania first-analysis fallback ranking",
            metric_value(first_analysis, "albania_first_analysis_promotion_wave_rows"),
            f"alb2012_priority_rank={alb2012_wave.get('priority_rank', 'missing')}; alb2012_candidate_gate_rows={alb2012_wave.get('candidate_evidence_gate_rows', '0')}; alb2012_blocked_gate_rows={alb2012_wave.get('blocked_gate_rows', '0')}",
            "hard_blocked_not_fallback_promoted",
            f"ALB_2012 remains blocked in first-analysis ranking: {alb2012_wave.get('primary_blocker', 'missing_interview_timing_coarse_prefecture_region_no_gps')}.",
            "Do not substitute ALB_2012 for ALB_2002 until raw household timing, defensible geography, and outcome promotion gates pass.",
            ["result/albania_first_analysis_promotion_summary.csv", "result/albania_first_analysis_promotion_wave_ranking.csv"],
        ),
    ]


def build_summary(rows: list[dict[str, str]]) -> list[dict[str, str]]:
    return [
        summary_row("alb2012_timing_geography_blocker_resolution_rows", len(rows), "ALB_2012 fallback blocker rows consolidated."),
        summary_row("alb2012_timing_geography_blocker_timing_rows", sum(1 for r in rows if r["blocker_family"] == "timing"), "Timing blocker rows in the matrix."),
        summary_row("alb2012_timing_geography_blocker_geography_rows", sum(1 for r in rows if r["blocker_family"] == "geography"), "Geography blocker rows in the matrix."),
        summary_row("alb2012_timing_geography_blocker_outcome_rows", sum(1 for r in rows if r["blocker_family"] == "outcome"), "Outcome blocker rows in the matrix."),
        summary_row("alb2012_timing_geography_blocker_promotion_gate_rows", sum(1 for r in rows if r["blocker_family"] == "promotion_gate"), "Promotion-gate rows in the matrix."),
        summary_row("alb2012_timing_geography_blocker_hard_blocked_rows", sum(1 for r in rows if r["promotion_status"].startswith("hard_blocked")), "Rows hard-blocked from fallback promotion."),
        summary_row("alb2012_timing_geography_blocker_interview_timing_ready_rows", sum(safe_int(r["interview_timing_ready_rows"]) for r in rows), "Rows with verified interview timing; intentionally zero."),
        summary_row("alb2012_timing_geography_blocker_geography_ready_rows", sum(safe_int(r["geography_ready_rows"]) for r in rows), "Rows with promoted geography; intentionally zero."),
        summary_row("alb2012_timing_geography_blocker_outcome_ready_rows", sum(safe_int(r["outcome_ready_rows"]) for r in rows), "Rows with promoted outcomes; intentionally zero."),
        summary_row("alb2012_timing_geography_blocker_climate_linkage_ready_rows", sum(safe_int(r["climate_linkage_ready_rows"]) for r in rows), "Rows ready for climate linkage; intentionally zero."),
        summary_row("alb2012_timing_geography_blocker_data_write_ready_rows", sum(safe_int(r["data_write_ready_rows"]) for r in rows), "Rows allowed for data/ writes by this matrix; intentionally zero."),
        summary_row("alb2012_timing_geography_blocker_current_decision", DECISION, "Current consolidated ALB_2012 fallback decision."),
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
        f"""# ALB_2012 Timing/Geography Blocker Resolution Matrix

Status: fail-closed fallback-resolution matrix. This consolidates ALB_2012 timing, geography, outcome, and first-analysis promotion evidence into one decision. It does not write `data/`, does not promote ALB_2012 as a fallback analysis wave, and does not treat questionnaire control-sheet fields as raw household interview timing.

## Summary

| Metric | Value | Interpretation |
|---|---:|---|
{summary_table}

## Blocker Matrix

{markdown_rows(rows, ['blocker_id', 'blocker_family', 'evidence_rows', 'promotion_status', 'interview_timing_ready_rows', 'geography_ready_rows', 'outcome_ready_rows', 'climate_linkage_ready_rows', 'data_write_ready_rows'])}

## Interpretation

- ALB_2012 has household consumption, weights, OOP payment signals, access proxies, and coarse geography, but it has no verified raw household interview timing.
- Questionnaire control sheets expose date/time/visit fields, but those fields are not verified in raw household values.
- PSU keys and prefecture/region fields are useful for review, but no GPS, official PSU crosswalk, or promoted admin climate-linkage source is available.
- Provisional outcomes and raw health semantics remain diagnostic because timing, geography, units, recall periods, skip patterns, and payment-scope rules are unresolved.

## Required Resolution

ALB_2012 can become a fallback analysis wave only after a source supplies linkable household timing or defensible fieldwork-period metadata, a climate-linkage geography source, and accepted outcome policies. Until then, interview-timing-ready, geography-ready, outcome-ready, climate-linkage-ready, and data-write-ready rows remain zero.

## Machine-Readable Outputs

- `temp/alb2012_timing_geography_blocker_resolution_matrix.csv`
- `result/alb2012_timing_geography_blocker_resolution_summary.csv`
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
    append_log(TEMP_DIR / "audit_log.md", f"Built ALB_2012 timing/geography blocker resolution matrix rows={len(rows)} decision={DECISION}.")
    print(f"ALB_2012 timing/geography blocker resolution rows={len(rows)} decision={DECISION}.")


if __name__ == "__main__":
    main()
