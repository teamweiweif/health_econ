from __future__ import annotations

import csv
from pathlib import Path
from typing import Any

from common import REPORT_DIR, RESULT_DIR, TEMP_DIR, append_log, ensure_dirs, write_csv


AUDIT_PATH = TEMP_DIR / "alb2005_fallback_blocker_resolution_matrix.csv"
SUMMARY_PATH = RESULT_DIR / "alb2005_fallback_blocker_resolution_summary.csv"
REPORT_PATH = REPORT_DIR / "alb2005_fallback_blocker_resolution_matrix.md"

DECISION = "blocked_alb2005_no_fallback_ready"
ALB2005_IDNO = "ALB_2005_LSMS_v01_M"

AUDIT_COLUMNS = [
    "blocker_id",
    "blocker_family",
    "evidence_label",
    "evidence_rows",
    "coverage_or_current_evidence",
    "promotion_status",
    "harmonized_ready_rows",
    "outcome_ready_rows",
    "interview_timing_ready_rows",
    "geography_ready_rows",
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


def summary_row(metric: str, value: Any, interpretation: str) -> dict[str, str]:
    return {"metric": metric, "value": str(value), "interpretation": interpretation}


def row(
    blocker_id: str,
    blocker_family: str,
    evidence_label: str,
    evidence_rows: Any,
    coverage_or_current_evidence: str,
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
        "coverage_or_current_evidence": coverage_or_current_evidence,
        "promotion_status": promotion_status,
        "harmonized_ready_rows": "0",
        "outcome_ready_rows": "0",
        "interview_timing_ready_rows": "0",
        "geography_ready_rows": "0",
        "climate_linkage_ready_rows": "0",
        "data_write_ready_rows": "0",
        "blocking_reason": blocking_reason,
        "next_resolution_step": next_resolution_step,
        "evidence_sources": "; ".join(evidence_sources),
    }


def build_matrix() -> list[dict[str, str]]:
    minimum = read_csv_dicts(RESULT_DIR / "alb2005_minimum_recipe_promotion_summary.csv")
    public_geo = read_csv_dicts(RESULT_DIR / "alb2005_public_fieldwork_geo_metadata_summary.csv")
    diary = read_csv_dicts(RESULT_DIR / "alb2005_diary_timing_candidate_summary.csv")
    extracted = read_csv_dicts(RESULT_DIR / "alb2005_extracted_module_coverage_summary.csv")
    timing_source = read_csv_dicts(RESULT_DIR / "alb2005_timing_geography_source_search_summary.csv")
    oop_policy = read_csv_dicts(RESULT_DIR / "alb2005_oop_aggregation_policy_summary.csv")
    unit_period = read_csv_dicts(RESULT_DIR / "alb2005_consumption_oop_unit_period_summary.csv")
    aggregate = read_csv_dicts(RESULT_DIR / "alb2005_consumption_aggregate_metadata_crosswalk_summary.csv")
    required = read_csv_dicts(RESULT_DIR / "alb2005_required_value_key_summary.csv")
    health = read_csv_dicts(RESULT_DIR / "alb2005_health_questionnaire_semantics_summary.csv")
    skip = read_csv_dicts(RESULT_DIR / "alb2005_skip_missing_semantics_summary.csv")
    first_analysis = read_csv_dicts(RESULT_DIR / "albania_first_analysis_promotion_summary.csv")
    wave_ranking = read_csv_dicts(RESULT_DIR / "albania_first_analysis_promotion_wave_ranking.csv")
    alb2005_wave = first_row(wave_ranking, "idno", ALB2005_IDNO)

    return [
        row(
            "minimum_recipe_gate_checklist",
            "promotion_gate",
            "ALB_2005 minimum recipe promotion gates",
            metric_value(minimum, "alb2005_minimum_recipe_promotion_gate_rows"),
            f"blocked_gates={metric_value(minimum, 'alb2005_minimum_recipe_promotion_blocked_gates')}; candidate_gates={metric_value(minimum, 'alb2005_minimum_recipe_promotion_candidate_gates')}; decision={metric_value(minimum, 'alb2005_minimum_recipe_promotion_current_decision', 'missing')}",
            "hard_blocked_minimum_recipe_not_ready",
            "The minimum recipe still has blocked denominator, OOP, access, timing, geography, outcome, harmonized-dataset, and climate-dataset gates.",
            "Resolve each gate with raw value, unit, recall-period, missing-code, skip-path, merge-key, timing, and geography evidence before promoting ALB_2005.",
            ["temp/alb2005_minimum_recipe_promotion_gate_checklist.csv", "result/alb2005_minimum_recipe_promotion_summary.csv"],
        ),
        row(
            "missing_critical_modules",
            "raw_package",
            "Critical DDI modules absent from local archive/extract",
            metric_value(extracted, "alb2005_extracted_module_coverage_critical_missing_rows"),
            f"bookmetadata_missing={metric_value(extracted, 'alb2005_extracted_module_coverage_bookmetadata_missing_rows')}; food_diary_missing={metric_value(extracted, 'alb2005_extracted_module_coverage_food_diary_missing_rows')}; archive_absent={metric_value(extracted, 'alb2005_archive_ddi_module_absent_rows')}",
            "hard_blocked_missing_bookmetadata_food_diary",
            "The local archive manifest and extracted package do not contain the bookmetadata or food-diary modules needed to verify diary timing and some consumption context.",
            "Obtain the missing modules or a citable official substitute that links household keys to timing and the omitted diary/consumption documentation.",
            ["temp/alb2005_extracted_module_coverage_audit.csv", "result/alb2005_extracted_module_coverage_summary.csv"],
        ),
        row(
            "public_fieldwork_period_metadata",
            "timing",
            "Public fieldwork-period and follow-up metadata",
            metric_value(public_geo, "alb2005_public_fieldwork_geo_metadata_fieldwork_period_evidence_rows"),
            f"verified_source_rows={metric_value(public_geo, 'alb2005_public_fieldwork_geo_metadata_verified_source_rows')}; household_timing_verified={metric_value(public_geo, 'alb2005_public_fieldwork_geo_metadata_household_timing_verified_rows')}",
            "hard_blocked_context_only_not_household_timing",
            "The public DDI fieldwork window is useful context but does not provide household-level interview month/date values.",
            "Link fieldwork-period metadata to household records or document an accepted fieldwork-window exposure fallback before climate extraction.",
            ["temp/alb2005_public_fieldwork_geo_metadata_audit.csv", "result/alb2005_public_fieldwork_geo_metadata_summary.csv"],
        ),
        row(
            "diary_timing_metadata_candidates",
            "timing",
            "Diary beginning/finishing date metadata candidates",
            metric_value(diary, "alb2005_diary_timing_candidate_metadata_found_rows"),
            f"date_candidate_rows={metric_value(diary, 'alb2005_diary_timing_candidate_date_candidate_rows')}; raw_bookmetadata_present={metric_value(diary, 'alb2005_diary_timing_candidate_raw_bookmetadata_files_present')}; household_timing_promoted={metric_value(diary, 'alb2005_diary_timing_candidate_household_timing_promoted_rows')}",
            "hard_blocked_diary_metadata_without_raw_bookmetadata",
            "Bookmetadata date fields appear in metadata, but raw bookmetadata files and merge/protocol semantics are absent.",
            "Obtain raw bookmetadata values and verify whether diary beginning/finishing dates can stand in for household interview timing.",
            ["temp/alb2005_diary_timing_candidate_audit.csv", "result/alb2005_diary_timing_candidate_summary.csv"],
        ),
        row(
            "raw_household_interview_timing",
            "timing",
            "Raw household interview timing source search",
            metric_value(timing_source, "alb2005_timing_geography_source_search_verified_household_timing_rows"),
            f"legacy_questionnaire_timing_rows={metric_value(timing_source, 'alb2005_timing_geography_source_search_legacy_questionnaire_timing_rows')}; household_survey_month_rows=0; source_decision={metric_value(timing_source, 'alb2005_timing_geography_source_search_current_decision', 'missing')}",
            "hard_blocked_no_verified_interview_timing",
            "Local raw/schema/questionnaire searches do not verify household interview date or month values.",
            "Trace questionnaire timing fields to raw household values or obtain a household control/interview module before building exposure windows.",
            ["temp/alb2005_timing_geography_source_search_audit.csv", "result/alb2005_timing_geography_source_search_summary.csv"],
        ),
        row(
            "public_gps_claims",
            "geography",
            "Public GPS-collection claims",
            metric_value(public_geo, "alb2005_public_fieldwork_geo_metadata_gps_claim_rows"),
            f"raw_coordinate_value_rows={metric_value(public_geo, 'alb2005_public_fieldwork_geo_metadata_raw_coordinate_value_rows')}; coordinate_candidates={metric_value(timing_source, 'alb2005_timing_geography_source_search_coordinate_candidate_rows')}",
            "hard_blocked_public_gps_claim_no_raw_values",
            "Public metadata says GPS was collected for crop-condition linkage, but no raw coordinate values or coordinate files are verified locally.",
            "Obtain restricted/public coordinate files, a documented cluster-to-coordinate crosswalk, or an accepted admin aggregation source.",
            ["temp/alb2005_public_fieldwork_geo_metadata_audit.csv", "result/alb2005_timing_geography_source_search_summary.csv"],
        ),
        row(
            "partial_current_geography",
            "geography",
            "Partial district code/name geography",
            metric_value(timing_source, "alb2005_timing_geography_source_search_partial_district_code_nonmissing_rows"),
            f"partial_name_rows={metric_value(timing_source, 'alb2005_timing_geography_source_search_partial_district_name_nonmissing_rows')}; full_geography_rows={metric_value(public_geo, 'alb2005_public_fieldwork_geo_metadata_full_geography_rows')}; geography_crosswalk_ready={metric_value(timing_source, 'alb2005_timing_geography_source_search_geography_crosswalk_ready_rows')}",
            "hard_blocked_partial_geography_no_crosswalk",
            "The partial district signal is not full-coverage current-location geography and has no accepted boundary/crosswalk for climate linkage.",
            "Verify complete household geography coverage and a boundary vintage/crosswalk before admin-level climate aggregation.",
            ["result/alb2005_timing_geography_source_search_summary.csv", "result/alb2005_required_value_key_summary.csv"],
        ),
        row(
            "consumption_denominator",
            "outcome",
            "Total consumption unit, period, and component scope",
            metric_value(unit_period, "alb2005_consumption_oop_unit_period_total_consumption_positive_rows"),
            f"totcons_positive={metric_value(aggregate, 'alb2005_consumption_aggregate_crosswalk_totcons_positive_rows')}; totcons05_local={metric_value(aggregate, 'alb2005_consumption_aggregate_crosswalk_totcons05_local_rows')}; component_formula_reconstructable={metric_value(aggregate, 'alb2005_consumption_aggregate_crosswalk_component_formula_reconstructable_rows')}",
            "hard_blocked_denominator_unit_component_scope",
            "The `totcons` denominator has positive values, but unit/period/component-scope, old/new lek handling, and public metadata formula reconstruction are unresolved.",
            "Verify denominator units, price basis, period, component formula, and SDG discretionary-budget inputs before outcome construction.",
            ["result/alb2005_consumption_oop_unit_period_summary.csv", "result/alb2005_consumption_aggregate_metadata_crosswalk_summary.csv"],
        ),
        row(
            "oop_aggregation_policy",
            "outcome",
            "OOP aggregation recall, skip, and payment-scope policy",
            metric_value(oop_policy, "alb2005_oop_aggregation_policy_rows"),
            f"four_week_policy_rows={metric_value(oop_policy, 'alb2005_oop_aggregation_policy_four_week_policy_rows')}; twelve_month_policy_rows={metric_value(oop_policy, 'alb2005_oop_aggregation_policy_twelve_month_policy_rows')}; outcome_ready={metric_value(oop_policy, 'alb2005_oop_aggregation_policy_outcome_ready_rows')}",
            "hard_blocked_oop_recall_skip_gift",
            "Observed OOP sums are diagnostic only because recall alignment, annualization, gift/payment scope, skip logic, and zero/missing rules are not accepted.",
            "Finalize OOP numerator policy using questionnaire text, raw values, skip paths, and denominator period before creating CHE outcomes.",
            ["result/alb2005_oop_aggregation_policy_summary.csv", "result/alb2005_skip_missing_semantics_summary.csv"],
        ),
        row(
            "access_need_denominator",
            "outcome",
            "Need/access denominator and skip-path semantics",
            metric_value(health, "alb2005_health_questionnaire_semantics_rows"),
            f"access_rows={metric_value(health, 'alb2005_health_questionnaire_access_rows')}; skip_missing_rows={metric_value(skip, 'alb2005_skip_missing_semantics_rows')}; outcome_ready={metric_value(health, 'alb2005_health_questionnaire_outcome_ready_rows')}",
            "hard_blocked_need_access_skip_patterns",
            "Need/access concepts and barrier labels are documented, but denominator, trigger population, skip paths, and missing semantics are not accepted.",
            "Manually verify illness/need triggers, access denominator, barrier code interpretation, and skip/missing behavior before access-outcome promotion.",
            ["result/alb2005_health_questionnaire_semantics_summary.csv", "result/alb2005_skip_missing_semantics_summary.csv"],
        ),
        row(
            "first_analysis_fallback_promotion",
            "promotion_gate",
            "Albania first-analysis fallback ranking",
            metric_value(first_analysis, "albania_first_analysis_promotion_wave_rows"),
            f"alb2005_priority_rank={alb2005_wave.get('priority_rank', 'missing')}; candidate_gate_rows={alb2005_wave.get('candidate_evidence_gate_rows', '0')}; blocked_gate_rows={alb2005_wave.get('blocked_gate_rows', '0')}; primary_blocker={alb2005_wave.get('primary_blocker', 'missing')}",
            "hard_blocked_not_fallback_promoted",
            "ALB_2005 ranks second but remains blocked by missing bookmetadata/food-diary modules, no household timing, and no raw coordinate evidence.",
            "Do not substitute ALB_2005 for ALB_2002 until timing, geography, outcome, harmonization, and climate gates pass.",
            ["result/albania_first_analysis_promotion_wave_ranking.csv", "result/albania_first_analysis_promotion_summary.csv"],
        ),
        row(
            "dataset_promotion",
            "promotion_gate",
            "Combined harmonized and climate-linked dataset promotion",
            "0",
            f"minimum_harmonized_ready={metric_value(minimum, 'alb2005_minimum_recipe_promotion_harmonized_ready_rows')}; minimum_outcome_ready={metric_value(minimum, 'alb2005_minimum_recipe_promotion_outcome_ready_rows')}; minimum_climate_ready={metric_value(minimum, 'alb2005_minimum_recipe_promotion_climate_linkage_ready_rows')}; extracted_climate_ready={metric_value(extracted, 'alb2005_extracted_module_coverage_climate_linkage_ready_rows')}",
            "hard_blocked_no_harmonized_or_climate_dataset",
            "No ALB_2005 artifact currently authorizes a `data/` write, final outcome construction, or climate-linked analytical dataset.",
            "After all source-specific blockers pass, rerun the ALB_2005 audits and promotion gates before any data promotion.",
            ["result/alb2005_minimum_recipe_promotion_summary.csv", "result/alb2005_extracted_module_coverage_summary.csv"],
        ),
    ]


def build_summary(rows: list[dict[str, str]]) -> list[dict[str, str]]:
    return [
        summary_row("alb2005_fallback_blocker_resolution_rows", len(rows), "ALB_2005 fallback blocker rows consolidated."),
        summary_row("alb2005_fallback_blocker_raw_package_rows", sum(1 for r in rows if r["blocker_family"] == "raw_package"), "Raw-package blocker rows in the matrix."),
        summary_row("alb2005_fallback_blocker_timing_rows", sum(1 for r in rows if r["blocker_family"] == "timing"), "Timing blocker rows in the matrix."),
        summary_row("alb2005_fallback_blocker_geography_rows", sum(1 for r in rows if r["blocker_family"] == "geography"), "Geography blocker rows in the matrix."),
        summary_row("alb2005_fallback_blocker_outcome_rows", sum(1 for r in rows if r["blocker_family"] == "outcome"), "Outcome blocker rows in the matrix."),
        summary_row("alb2005_fallback_blocker_promotion_gate_rows", sum(1 for r in rows if r["blocker_family"] == "promotion_gate"), "Promotion-gate rows in the matrix."),
        summary_row("alb2005_fallback_blocker_hard_blocked_rows", sum(1 for r in rows if r["promotion_status"].startswith("hard_blocked")), "Rows hard-blocked from fallback promotion."),
        summary_row("alb2005_fallback_blocker_harmonized_ready_rows", sum(safe_int(r["harmonized_ready_rows"]) for r in rows), "Rows ready for harmonized data promotion; intentionally zero."),
        summary_row("alb2005_fallback_blocker_outcome_ready_rows", sum(safe_int(r["outcome_ready_rows"]) for r in rows), "Rows ready for outcome promotion; intentionally zero."),
        summary_row("alb2005_fallback_blocker_interview_timing_ready_rows", sum(safe_int(r["interview_timing_ready_rows"]) for r in rows), "Rows with verified interview timing; intentionally zero."),
        summary_row("alb2005_fallback_blocker_geography_ready_rows", sum(safe_int(r["geography_ready_rows"]) for r in rows), "Rows with promoted geography; intentionally zero."),
        summary_row("alb2005_fallback_blocker_climate_linkage_ready_rows", sum(safe_int(r["climate_linkage_ready_rows"]) for r in rows), "Rows ready for climate linkage; intentionally zero."),
        summary_row("alb2005_fallback_blocker_data_write_ready_rows", sum(safe_int(r["data_write_ready_rows"]) for r in rows), "Rows allowed for data/ writes by this matrix; intentionally zero."),
        summary_row("alb2005_fallback_blocker_current_decision", DECISION, "Current consolidated ALB_2005 fallback decision."),
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
        f"""# ALB_2005 Fallback Blocker Resolution Matrix

Status: fail-closed fallback-resolution matrix. This consolidates ALB_2005 raw-package, timing, geography, outcome, and first-analysis promotion evidence into one decision. It does not write `data/`, does not promote ALB_2005 as a fallback analysis wave, and does not treat public fieldwork/GPS claims or diary-date metadata as household-level climate-linkage evidence.

## Summary

| Metric | Value | Interpretation |
|---|---:|---|
{summary_table}

## Blocker Matrix

{markdown_rows(rows, ['blocker_id', 'blocker_family', 'evidence_rows', 'promotion_status', 'harmonized_ready_rows', 'outcome_ready_rows', 'interview_timing_ready_rows', 'geography_ready_rows', 'climate_linkage_ready_rows', 'data_write_ready_rows'])}

## Interpretation

- ALB_2005 has household rows, positive total-consumption values, positive OOP sums, weights, public fieldwork metadata, public GPS-collection claims, and diary-date metadata leads.
- The local archive and extracted package are missing `bookmetadata_cl`, five food-diary modules, and coordinate evidence, so the diary and GPS leads cannot be promoted.
- Household interview timing remains unverified, current geography is partial/no-GPS, and denominator/OOP/access semantics still need manual unit, recall-period, skip-pattern, and payment-scope review.
- First-analysis fallback promotion remains blocked because harmonized-ready, outcome-ready, timing-ready, geography-ready, climate-linkage-ready, and data-write-ready rows are all zero.

## Required Resolution

ALB_2005 can become a fallback analysis wave only after the missing module/source evidence is obtained or officially substituted, household timing is verified, geography/GPS or an accepted admin crosswalk is promoted, and outcome policies pass. Until then, no `data/` artifact, final UHC outcome, climate exposure, descriptive diagnostic, model, or policy-learning step should use ALB_2005.

## Machine-Readable Outputs

- `temp/alb2005_fallback_blocker_resolution_matrix.csv`
- `result/alb2005_fallback_blocker_resolution_summary.csv`
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
    append_log(TEMP_DIR / "audit_log.md", f"Built ALB_2005 fallback blocker resolution matrix rows={len(rows)} decision={DECISION}.")
    print(f"ALB_2005 fallback blocker resolution rows={len(rows)} decision={DECISION}.")


if __name__ == "__main__":
    main()
