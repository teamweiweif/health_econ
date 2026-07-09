from __future__ import annotations

import csv
from collections import Counter
from pathlib import Path
from typing import Any

from common import REPORT_DIR, RESULT_DIR, TEMP_DIR, append_log, ensure_dirs, write_csv


IDNO = "ALB_2005_LSMS_v01_M"
COUNTRY = "Albania"
SURVEY_NAME = "Living Standards Measurement Survey 2005"
WAVE = "2005"

GATE_PATH = TEMP_DIR / "harmonization_recipe_gate.csv"
DOCUMENTED_EVIDENCE_PATH = TEMP_DIR / "alb2005_documented_variable_evidence.csv"
CORE_SUMMARY_PATH = RESULT_DIR / "alb2005_household_core_candidate_summary.csv"
OUTCOME_SUMMARY_PATH = RESULT_DIR / "alb2005_provisional_outcome_feasibility_summary.csv"
SEMANTICS_SUMMARY_PATH = RESULT_DIR / "alb2005_outcome_semantics_raw_value_summary.csv"
TIMING_GEO_SUMMARY_PATH = RESULT_DIR / "alb2005_timing_geography_exhaustive_summary.csv"
LEGACY_TIMING_SUMMARY_PATH = RESULT_DIR / "albania_legacy_questionnaire_timing_field_summary.csv"

AUDIT_PATH = TEMP_DIR / "alb2005_harmonization_value_decision_audit.csv"
SUMMARY_PATH = RESULT_DIR / "alb2005_harmonization_value_decision_summary.csv"
REPORT_PATH = REPORT_DIR / "alb2005_harmonization_value_decision_audit.md"

DECISION = "blocked_no_alb2005_value_decision_ready_for_recipe"

AUDIT_COLUMNS = [
    "country",
    "survey_name",
    "wave",
    "idno",
    "concept",
    "harmonized_variable",
    "required",
    "merge_level",
    "key_role",
    "matched_source_files",
    "matched_raw_variables",
    "raw_label",
    "source_file_status",
    "raw_variable_status",
    "value_audit_status",
    "recipe_gate_status",
    "minimum_recipe_role",
    "candidate_evidence_status",
    "decision_status",
    "ready_for_recipe",
    "promotion_status",
    "blocking_reason",
    "next_action",
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


def int_value(value: Any) -> int:
    try:
        return int(float(str(value).strip()))
    except (TypeError, ValueError):
        return 0


def normalize_row(row: dict[str, str]) -> dict[str, str]:
    return {key.lstrip("\ufeff"): value for key, value in row.items()}


def minimum_role(required: str) -> str:
    if required == "yes":
        return "required_hard_blocker"
    if required == "recommended":
        return "recommended_quality_or_design_item"
    return "optional_not_minimum_recipe"


def classify(row: dict[str, str]) -> tuple[str, str, str, str, str]:
    concept = row.get("concept", "")
    harmonized = row.get("harmonized_variable", "")
    required = row.get("required", "")

    if concept == "survey_timing":
        return (
            "no_verified_raw_interview_month_or_date",
            "blocked_missing_interview_timing",
            "No verified ALB_2005 household interview month/date exists, and questionnaire form-design cells cannot define climate exposure windows.",
            "Find a raw household interview timing variable or defensible official fieldwork calendar before any climate-linked recipe.",
            "temp/harmonization_recipe_gate.csv; result/alb2005_timing_geography_exhaustive_summary.csv; result/albania_legacy_questionnaire_timing_field_summary.csv",
        )

    if concept == "climate_geography":
        if harmonized in {"latitude", "longitude"}:
            evidence = "no_gps_or_coordinate_candidate"
        else:
            evidence = "partial_district_or_cluster_key_without_full_coverage_or_timing"
        return (
            evidence,
            "blocked_partial_geography_no_gps_or_timing",
            "ALB_2005 has partial current district evidence and cluster-like keys, but no GPS, no full-coverage climate-ready geography, and no verified interview timing.",
            "Resolve current-location coverage, district boundary/crosswalk, no-GPS admin aggregation, and interview timing before climate linkage.",
            "temp/harmonization_recipe_gate.csv; temp/alb2005_documented_variable_evidence.csv; result/alb2005_timing_geography_exhaustive_summary.csv",
        )

    if concept == "household_id":
        return (
            "documented_household_key_candidate_requires_cardinality_review",
            "candidate_for_manual_key_review_not_recipe_ready",
            "Household ID variables are documented, but cross-file uniqueness, merge cardinality, and module coverage still need manual verification.",
            "Verify household uniqueness and joins across poverty, health, filters, roster, and weight files.",
            "temp/harmonization_recipe_gate.csv; temp/alb2005_documented_variable_evidence.csv; result/alb2005_household_core_candidate_summary.csv",
        )

    if concept == "total_consumption_or_income":
        if harmonized == "total_consumption":
            return (
                "documented_totcons_candidate_requires_unit_period_review",
                "candidate_for_manual_unit_period_review_not_recipe_ready",
                "The survey total-consumption aggregate exists, but old/new lek scaling, period, household-total interpretation, missing codes, and denominator use remain unverified.",
                "Confirm local-currency unit, price basis, period, missing rules, and household-total interpretation before denominator construction.",
                "temp/harmonization_recipe_gate.csv; temp/alb2005_documented_variable_evidence.csv; result/alb2005_household_core_candidate_summary.csv",
            )
        if harmonized in {"food_consumption", "nonfood_consumption"}:
            return (
                "component_or_per_capita_measure_requires_unit_scope_review",
                "blocked_component_scope_not_verified",
                "Food/nonfood components are not verified as direct household totals and cannot be promoted from the current gate match.",
                "Review component variables, units, per-capita denominators, and reconstruction rules before using them in SDG or CHE denominators.",
                "temp/harmonization_recipe_gate.csv; temp/alb2005_documented_variable_evidence.csv",
            )
        return (
            "no_verified_total_income_candidate",
            "blocked_income_variable_not_verified",
            "The gate match reflects consumption evidence, not a verified income aggregate.",
            "Do not substitute total consumption for total income unless the outcome protocol explicitly uses consumption as the denominator.",
            "temp/harmonization_recipe_gate.csv; temp/alb2005_documented_variable_evidence.csv",
        )

    if concept == "oop_health_expenditure":
        return (
            "documented_payment_items_require_aggregation_recall_skip_review",
            "blocked_oop_aggregation_recall_skip_patterns",
            "Payment variables exist, but item scope, gift inclusion, recall periods, missing/zero coding, person-to-household aggregation, and skip patterns are unresolved.",
            "Map each payment item to care context and build an auditable aggregation rule before outcome construction.",
            "temp/harmonization_recipe_gate.csv; temp/alb2005_documented_variable_evidence.csv; result/alb2005_outcome_semantics_raw_value_summary.csv",
        )

    if concept == "health_need":
        return (
            "documented_need_variables_require_denominator_review",
            "blocked_need_denominator_skip_patterns",
            "Need variables mix chronic/disability, diagnosis, disease category, and sudden illness concepts; denominator and skip patterns remain unresolved.",
            "Choose the need definition and verify questionnaire skip paths before access or double-failure outcomes.",
            "temp/harmonization_recipe_gate.csv; temp/alb2005_documented_variable_evidence.csv; result/alb2005_outcome_semantics_raw_value_summary.csv",
        )

    if concept == "care_or_barrier":
        return (
            "documented_access_variables_require_value_label_denominator_review",
            "blocked_access_denominator_skip_patterns",
            "Access variables appear to cover referral nonuse, distance, and reasons, but denominator, cost/distance/supply coding, and skip paths are unresolved.",
            "Confirm value labels and denominator among eligible need/referral observations before constructing forgone-care outcomes.",
            "temp/harmonization_recipe_gate.csv; temp/alb2005_documented_variable_evidence.csv; result/alb2005_outcome_semantics_raw_value_summary.csv",
        )

    if concept == "survey_weight":
        if harmonized == "household_weight":
            return (
                "gate_false_positive_birth_weight_but_weight_retro_candidate_exists",
                "blocked_false_positive_gate_candidate_weight_retro_requires_design_review",
                "The gate-matched m10_q13a/m10_q13b variables are birth-weight measures, not survey weights; a separate weight_retro candidate exists but still needs design and merge review.",
                "Exclude m10_q13a/m10_q13b and verify official weight_retro use, population, merge key, and coverage before any weighted analysis.",
                "temp/harmonization_recipe_gate.csv; temp/alb2005_documented_variable_evidence.csv; result/alb2005_household_core_candidate_summary.csv",
            )
        return (
            "gate_false_positive_birth_weight_no_verified_person_weight",
            "blocked_false_positive_birth_weight_no_person_weight_ready",
            "The gate-matched m10_q13a/m10_q13b variables are birth-weight measures; no verified person weight is ready.",
            "Exclude birth-weight variables from survey-design candidates and verify any person-weight candidate from official documentation before use.",
            "temp/harmonization_recipe_gate.csv; temp/alb2005_documented_variable_evidence.csv",
        )

    if concept == "psu_cluster":
        return (
            "psu_cluster_key_candidate_requires_design_review",
            "candidate_for_manual_cluster_design_review_not_climate_linkage",
            "PSU-like keys exist and may support survey design or merges, but they are not coordinates or admin polygons for climate linkage.",
            "Verify PSU meaning, merge consistency, variance-cluster suitability, and whether any official cluster geography exists.",
            "temp/harmonization_recipe_gate.csv; result/alb2005_timing_geography_exhaustive_summary.csv",
        )

    if concept == "strata":
        return (
            "recommended_strata_not_matched",
            "recommended_absent_not_minimum_recipe_blocker",
            "A strata variable is not matched; this is a design-quality limitation, not a standalone minimum recipe blocker.",
            "Keep strata missing in design notes unless official sampling documentation identifies a usable stratum variable.",
            "temp/harmonization_recipe_gate.csv",
        )

    if concept == "demographics":
        return (
            "recommended_demographic_files_not_matched_in_current_gate",
            "recommended_demographics_absent_not_minimum_recipe_blocker",
            "Recommended demographic variables are not matched by the current gate and cannot be added without raw value/key review.",
            "Review roster and demographic modules only after the required timing/geography, consumption, OOP, and key blockers are resolved.",
            "temp/harmonization_recipe_gate.csv",
        )

    if concept == "shocks_or_livelihood":
        return (
            "optional_shock_module_candidate_not_climate_exposure",
            "optional_mechanism_covariate_review_not_minimum_recipe",
            "Shock-module candidates may be mechanism or covariate evidence, but they are not external climate exposure variables and remain optional.",
            "Document household shock coding only after the main recipe blockers are resolved; do not use it as climate exposure.",
            "temp/harmonization_recipe_gate.csv; temp/alb2005_documented_variable_evidence.csv",
        )

    if concept == "insurance":
        return (
            "optional_insurance_absent",
            "optional_absent_not_minimum_recipe_blocker",
            "No verified insurance candidate is available, and insurance is optional for the minimum financial-protection recipe.",
            "Leave insurance absent unless official raw variables and value labels are later verified.",
            "temp/harmonization_recipe_gate.csv",
        )

    return (
        "unclassified_gate_row_requires_manual_review",
        "blocked_unclassified_manual_review_required" if required == "yes" else "not_ready_manual_review_required",
        "The gate row is not classified by the ALB_2005 decision audit and remains non-promoted.",
        "Inspect raw values, units, recall periods, missing codes, merge keys, and documentation before any recipe update.",
        "temp/harmonization_recipe_gate.csv",
    )


def build_audit() -> list[dict[str, str]]:
    gate_rows = [normalize_row(row) for row in read_csv_dicts(GATE_PATH)]
    alb_rows = [row for row in gate_rows if row.get("idno") == IDNO]
    audit: list[dict[str, str]] = []
    for row in alb_rows:
        evidence_status, decision_status, blocker, next_action, sources = classify(row)
        audit.append(
            {
                "country": row.get("country", COUNTRY),
                "survey_name": row.get("survey_name", SURVEY_NAME),
                "wave": row.get("wave", WAVE),
                "idno": row.get("idno", IDNO),
                "concept": row.get("concept", ""),
                "harmonized_variable": row.get("harmonized_variable", ""),
                "required": row.get("required", ""),
                "merge_level": row.get("merge_level", ""),
                "key_role": row.get("key_role", ""),
                "matched_source_files": row.get("matched_source_files", ""),
                "matched_raw_variables": row.get("matched_raw_variables", ""),
                "raw_label": row.get("raw_label", ""),
                "source_file_status": row.get("source_file_status", ""),
                "raw_variable_status": row.get("raw_variable_status", ""),
                "value_audit_status": row.get("value_audit_status", ""),
                "recipe_gate_status": row.get("recipe_gate_status", ""),
                "minimum_recipe_role": minimum_role(row.get("required", "")),
                "candidate_evidence_status": evidence_status,
                "decision_status": decision_status,
                "ready_for_recipe": "0",
                "promotion_status": "not_promoted_fail_closed",
                "blocking_reason": blocker,
                "next_action": next_action,
                "evidence_sources": sources,
            }
        )
    return audit


def summary_rows(audit: list[dict[str, str]]) -> list[dict[str, str]]:
    documented = read_csv_dicts(DOCUMENTED_EVIDENCE_PATH)
    core_summary = read_csv_dicts(CORE_SUMMARY_PATH)
    outcome_summary = read_csv_dicts(OUTCOME_SUMMARY_PATH)
    semantics_summary = read_csv_dicts(SEMANTICS_SUMMARY_PATH)
    timing_geo_summary = read_csv_dicts(TIMING_GEO_SUMMARY_PATH)
    legacy_timing_summary = read_csv_dicts(LEGACY_TIMING_SUMMARY_PATH)

    decision_counts = Counter(row["decision_status"] for row in audit)
    role_counts = Counter(row["minimum_recipe_role"] for row in audit)
    concept_counts = Counter(row["concept"] for row in audit)

    rows = [
        {
            "metric": "alb2005_harmonization_value_decision_rows",
            "value": str(len(audit)),
            "interpretation": "Rows in the ALB_2005 harmonization value decision audit.",
        },
        {
            "metric": "alb2005_harmonization_value_decision_required_rows",
            "value": str(sum(1 for row in audit if row["required"] == "yes")),
            "interpretation": "Gate rows marked required for the minimum recipe.",
        },
        {
            "metric": "alb2005_harmonization_value_decision_recommended_rows",
            "value": str(sum(1 for row in audit if row["required"] == "recommended")),
            "interpretation": "Gate rows marked recommended but not minimum requirements.",
        },
        {
            "metric": "alb2005_harmonization_value_decision_optional_rows",
            "value": str(sum(1 for row in audit if row["required"] == "no")),
            "interpretation": "Gate rows marked optional or not required.",
        },
        {
            "metric": "alb2005_harmonization_value_decision_recipe_ready_rows",
            "value": str(sum(1 for row in audit if row["ready_for_recipe"] == "1")),
            "interpretation": "Rows promoted to a verified harmonization recipe by this decision audit.",
        },
        {
            "metric": "alb2005_harmonization_value_decision_required_blocked_rows",
            "value": str(sum(1 for row in audit if row["required"] == "yes" and row["ready_for_recipe"] != "1")),
            "interpretation": "Required rows that remain blocked after source-derived ALB_2005 review.",
        },
        {
            "metric": "alb2005_harmonization_value_decision_manual_future_candidate_rows",
            "value": str(sum(1 for row in audit if row["decision_status"].startswith("candidate_for_manual"))),
            "interpretation": "Rows that may become recipe candidates only after manual key, unit, period, or design review.",
        },
        {
            "metric": "alb2005_harmonization_value_decision_false_positive_rows",
            "value": str(sum(1 for row in audit if "false_positive" in row["decision_status"])),
            "interpretation": "Rows explicitly blocked because current gate candidates include known false positives.",
        },
        {
            "metric": "alb2005_harmonization_value_decision_timing_geography_hard_blocker_rows",
            "value": str(
                sum(
                    1
                    for row in audit
                    if row["decision_status"]
                    in {"blocked_missing_interview_timing", "blocked_partial_geography_no_gps_or_timing"}
                )
            ),
            "interpretation": "Rows blocked by missing interview timing or insufficient geography/GPS evidence.",
        },
        {
            "metric": "alb2005_harmonization_value_decision_current_decision",
            "value": DECISION,
            "interpretation": "Fail-closed decision for ALB_2005 value interpretation and recipe promotion.",
        },
        {
            "metric": "alb2005_documented_evidence_rows_used",
            "value": str(len(documented)),
            "interpretation": "Rows read from the documented ALB_2005 harmonization review.",
        },
        {
            "metric": "alb2005_household_core_recipe_ready_rows_observed",
            "value": metric_value(core_summary, "alb2005_household_core_recipe_ready_rows", "0"),
            "interpretation": "Recipe-ready rows observed in the temp-only household-core audit.",
        },
        {
            "metric": "alb2005_provisional_outcome_ready_rows_observed",
            "value": metric_value(outcome_summary, "alb2005_provisional_outcome_ready_rows", "0"),
            "interpretation": "Outcome-ready rows observed in the provisional outcome audit.",
        },
        {
            "metric": "alb2005_outcome_semantics_outcome_ready_rows_observed",
            "value": metric_value(semantics_summary, "alb2005_outcome_semantics_outcome_ready_rows", "0"),
            "interpretation": "Outcome-ready rows observed in the raw semantics audit.",
        },
        {
            "metric": "alb2005_outcome_semantics_sdg382_ready_rows_observed",
            "value": metric_value(semantics_summary, "alb2005_outcome_semantics_sdg382_ready_rows", "0"),
            "interpretation": "SDG 3.8.2-ready rows observed in the raw semantics audit.",
        },
        {
            "metric": "alb2005_timing_geography_climate_linkage_ready_rows_observed",
            "value": metric_value(timing_geo_summary, "alb2005_climate_linkage_ready_rows", "0"),
            "interpretation": "Climate-linkage-ready rows observed in the ALB_2005 timing/geography audit.",
        },
        {
            "metric": "alb2005_legacy_questionnaire_verified_timing_rows_observed",
            "value": metric_value(legacy_timing_summary, "alb2005_legacy_questionnaire_timing_raw_verified_interview_timing_rows", "0"),
            "interpretation": "ALB_2005 raw household interview timing rows observed by the legacy questionnaire timing audit.",
        },
    ]

    for concept, count in sorted(concept_counts.items()):
        rows.append(
            {
                "metric": f"alb2005_harmonization_value_decision_concept_{concept}",
                "value": str(count),
                "interpretation": "ALB_2005 value-decision rows by concept.",
            }
        )
    for role, count in sorted(role_counts.items()):
        rows.append(
            {
                "metric": f"alb2005_harmonization_value_decision_role_{role}",
                "value": str(count),
                "interpretation": "ALB_2005 value-decision rows by minimum recipe role.",
            }
        )
    for decision, count in sorted(decision_counts.items()):
        rows.append(
            {
                "metric": f"alb2005_harmonization_value_decision_status_{decision}",
                "value": str(count),
                "interpretation": "ALB_2005 value-decision rows by decision status.",
            }
        )
    return rows


def markdown_table(rows: list[dict[str, str]], columns: list[str], limit: int = 20) -> str:
    lines = ["| " + " | ".join(columns) + " |", "|" + "|".join("---" for _ in columns) + "|"]
    for row in rows[:limit]:
        values = []
        for column in columns:
            value = (row.get(column, "") or "").replace("|", "/")
            if len(value) > 110:
                value = value[:107] + "..."
            values.append(value)
        lines.append("| " + " | ".join(values) + " |")
    return "\n".join(lines)


def markdown_count_table(counter: Counter[str], label: str) -> str:
    lines = [f"| {label} | Count |", "|---|---:|"]
    for key, count in counter.most_common():
        lines.append(f"| {key or 'blank'} | {count} |")
    return "\n".join(lines)


def write_report(audit: list[dict[str, str]], summary: list[dict[str, str]]) -> None:
    decision_counts = Counter(row["decision_status"] for row in audit)
    concept_counts = Counter(row["concept"] for row in audit)
    required_rows = [row for row in audit if row["required"] == "yes"]
    summary_table = "\n".join(
        f"| {row['metric']} | {row['value']} | {row['interpretation']} |" for row in summary
    )
    REPORT_PATH.write_text(
        f"""# ALB_2005 Harmonization Value Decision Audit

Status: fail-closed interpretation layer. This audit classifies ALB_2005 gate blockers from source-derived evidence but does not pass any value audit row or write any analytical data to `data/`.

## Bottom Line

- Recipe-ready rows from this audit: 0.
- Required rows still blocked: {sum(1 for row in required_rows if row['ready_for_recipe'] != '1')} of {len(required_rows)}.
- Binding blockers: no verified household interview month/date, no GPS or full-coverage climate-ready geography, unresolved OOP aggregation/recall/skip patterns, unresolved denominator units for consumption components, and unresolved key/design review.
- Specific correction: `m10_q13a/m10_q13b` remain rejected as birth-weight variables; `weight_retro` is a future household-weight candidate only after design and merge review.

## Summary Metrics

| Metric | Value | Interpretation |
|---|---:|---|
{summary_table}

## Decision Status Counts

{markdown_count_table(decision_counts, 'Decision status') if audit else 'No decision rows exist.'}

## Concept Counts

{markdown_count_table(concept_counts, 'Concept') if audit else 'No concept rows exist.'}

## Required Gate Rows

{markdown_table(required_rows, ['concept', 'harmonized_variable', 'candidate_evidence_status', 'decision_status', 'ready_for_recipe', 'blocking_reason'], 25) if required_rows else 'No required ALB_2005 gate rows were found.'}

## Manual Review Candidates

These rows are not ready. They only identify where future manual review could focus if the timing/geography blockers are later resolved.

{markdown_table([row for row in audit if row['decision_status'].startswith('candidate_for_manual')], ['concept', 'harmonized_variable', 'candidate_evidence_status', 'decision_status', 'next_action'], 20)}

## Machine-Readable Outputs

- `temp/alb2005_harmonization_value_decision_audit.csv`
- `result/alb2005_harmonization_value_decision_summary.csv`
""",
        encoding="utf-8",
    )


def main() -> None:
    ensure_dirs()
    audit = build_audit()
    summary = summary_rows(audit)
    write_csv(AUDIT_PATH, audit, AUDIT_COLUMNS)
    write_csv(SUMMARY_PATH, summary, SUMMARY_COLUMNS)
    write_report(audit, summary)
    append_log(
        TEMP_DIR / "audit_log.md",
        f"ALB_2005 harmonization value decision audit rows={len(audit)} ready_for_recipe=0 decision={DECISION}.",
    )


if __name__ == "__main__":
    main()
