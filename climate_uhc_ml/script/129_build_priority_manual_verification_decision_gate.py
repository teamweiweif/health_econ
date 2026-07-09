from __future__ import annotations

import csv
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

from common import PROJECT_ROOT, REPORT_DIR, RESULT_DIR, TEMP_DIR, append_log, ensure_dirs, write_csv


WAVE_PLAN_PATH = RESULT_DIR / "priority_promotion_acquisition_wave_plan.csv"
DATASET_GATE_PATH = RESULT_DIR / "priority_dataset_verification_gate.csv"
REQUIREMENT_PATH = TEMP_DIR / "priority_promotion_verification_checklist.csv"
CONCEPT_PATH = TEMP_DIR / "priority_concept_verification_template.csv"
VARIABLE_PATH = TEMP_DIR / "priority_variable_verification_template.csv"
ARCHIVE_MATRIX_PATH = TEMP_DIR / "priority_archive_completeness_matrix.csv"

DATASET_DECISION_PATH = TEMP_DIR / "priority_manual_verification_decision_gate.csv"
REQUIREMENT_DECISION_PATH = TEMP_DIR / "priority_manual_requirement_decision_audit.csv"
CONCEPT_DECISION_PATH = TEMP_DIR / "priority_manual_concept_decision_audit.csv"
VARIABLE_DECISION_PATH = TEMP_DIR / "priority_manual_variable_decision_audit.csv"
SUMMARY_PATH = RESULT_DIR / "priority_manual_verification_decision_summary.csv"
REPORT_PATH = REPORT_DIR / "priority_manual_verification_decision_gate.md"

FINANCIAL_REQUIREMENTS = {
    "household_person_merge_keys",
    "weights_and_survey_design",
    "consumption_or_income_aggregate",
    "oop_health_expenditure",
    "survey_timing",
    "geography_climate_linkage",
    "missing_skip_units_recall",
}
DOUBLE_FAILURE_REQUIREMENTS = FINANCIAL_REQUIREMENTS | {"illness_need_care_access"}
FINANCIAL_CONCEPTS = {"household_id", "survey_weight", "total_consumption_or_income", "oop_health_expenditure", "survey_timing", "climate_geography"}
DOUBLE_FAILURE_CONCEPTS = {"health_need", "care_or_barrier"}
DESIGN_CONCEPTS = {"household_id", "psu_cluster", "strata", "survey_weight", "survey_timing", "climate_geography"}

PASS_VALUES = {"1", "yes", "y", "true", "pass", "passed", "verified", "ready", "ok", "complete", "promote"}

DATASET_COLUMNS = [
    "acquisition_batch_rank",
    "batch_role",
    "country",
    "survey_name",
    "wave",
    "idno",
    "requirement_rows",
    "requirements_passed",
    "financial_requirements_passed",
    "double_failure_requirements_passed",
    "concept_rows",
    "concepts_passed",
    "financial_concepts_passed",
    "double_failure_concepts_passed",
    "design_concepts_passed",
    "variable_rows",
    "variables_passed",
    "archive_file_targets",
    "archive_or_direct_targets_covered",
    "accepted_chirps_era5_route_status",
    "manual_verification_status",
    "financial_protection_manual_ready",
    "double_failure_manual_ready",
    "analysis_ready_candidate",
    "remaining_blockers",
    "handoff_readme",
]

AUDIT_COLUMNS = [
    "acquisition_batch_rank",
    "batch_role",
    "country",
    "wave",
    "idno",
    "item_type",
    "item_id",
    "source_gate_status",
    "manual_fields_required",
    "manual_fields_passed",
    "missing_or_failed_fields",
    "manual_decision_status",
    "review_notes",
]

SUMMARY_COLUMNS = ["metric", "value", "interpretation"]


def read_csv_dicts(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        return []
    with path.open(encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def clean(value: Any) -> str:
    return "" if value is None else str(value).strip()


def yes(value: Any) -> bool:
    return clean(value).lower() in PASS_VALUES


def safe_int(value: Any, default: int = 0) -> int:
    try:
        text = str(value).strip()
        return int(float(text)) if text else default
    except (TypeError, ValueError):
        return default


def compact(values: list[str], limit: int = 12) -> str:
    out: list[str] = []
    seen: set[str] = set()
    for value in values:
        item = clean(value)
        if item and item not in seen:
            out.append(item)
            seen.add(item)
        if len(out) >= limit:
            break
    return "; ".join(out)


def group(rows: list[dict[str, str]], field: str) -> dict[str, list[dict[str, str]]]:
    out: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in rows:
        key = clean(row.get(field))
        if key:
            out[key].append(row)
    return out


def first_by(rows: list[dict[str, str]], field: str) -> dict[str, dict[str, str]]:
    out: dict[str, dict[str, str]] = {}
    for row in rows:
        key = clean(row.get(field))
        if key and key not in out:
            out[key] = row
    return out


def rel(path: Path) -> str:
    try:
        return str(path.relative_to(PROJECT_ROOT)).replace("\\", "/")
    except ValueError:
        return str(path).replace("\\", "/")


def required_status(row: dict[str, str], item_type: str) -> tuple[str, list[str], str]:
    if item_type == "requirement":
        fields = [
            "fill_evidence_file_or_module",
            "fill_raw_variables_used",
            "fill_value_label_pass",
            "fill_unit_or_recall_pass",
            "fill_merge_key_or_level_pass",
            "fill_missing_skip_pattern_pass",
            "fill_promote_requirement",
        ]
        source_gate = row.get("current_requirement_gate", "")
        source_ready = source_gate == "ready_for_manual_requirement_audit"
    elif item_type == "concept":
        fields = [
            "fill_raw_file_used",
            "fill_raw_variable_used",
            "fill_value_label_pass",
            "fill_unit_or_recall_pass",
            "fill_merge_key_pass",
            "fill_sample_level_pass",
            "fill_missing_code_pass",
            "fill_promote_to_harmonization_recipe",
        ]
        source_gate = row.get("current_concept_gate", "")
        source_ready = source_gate == "ready_for_manual_value_label_unit_key_audit"
    else:
        fields = [
            "fill_raw_file_used",
            "fill_raw_variable_used",
            "fill_variable_label_verified",
            "fill_value_distribution_checked",
            "fill_missing_codes_documented",
            "fill_unit_recall_period_documented",
            "fill_merge_key_level_verified",
            "fill_promote_to_harmonization_recipe",
        ]
        source_gate = row.get("verification_status", "")
        source_ready = source_gate == "ready_for_manual_value_audit"

    missing: list[str] = []
    passed = 0
    for field in fields:
        if field in {"fill_evidence_file_or_module", "fill_raw_variables_used", "fill_raw_file_used", "fill_raw_variable_used"}:
            ok = bool(clean(row.get(field)))
        else:
            ok = yes(row.get(field))
        if ok:
            passed += 1
        else:
            missing.append(field)
    if not source_ready:
        return source_gate or "source_gate_missing", fields, "blocked_source_gate_not_ready"
    if missing:
        return source_gate, fields, "blocked_manual_fields_incomplete"
    return source_gate, fields, "manual_verified"


def audit_row(row: dict[str, str], item_type: str, item_id: str) -> dict[str, str]:
    source_gate, fields, status = required_status(row, item_type)
    missing = []
    passed = 0
    for field in fields:
        if field in {"fill_evidence_file_or_module", "fill_raw_variables_used", "fill_raw_file_used", "fill_raw_variable_used"}:
            ok = bool(clean(row.get(field)))
        else:
            ok = yes(row.get(field))
        if ok:
            passed += 1
        else:
            missing.append(field)
    return {
        "acquisition_batch_rank": row.get("acquisition_batch_rank", ""),
        "batch_role": row.get("batch_role", ""),
        "country": row.get("country", ""),
        "wave": row.get("wave", ""),
        "idno": row.get("idno", ""),
        "item_type": item_type,
        "item_id": item_id,
        "source_gate_status": source_gate,
        "manual_fields_required": str(len(fields)),
        "manual_fields_passed": str(passed),
        "missing_or_failed_fields": compact(missing, limit=20),
        "manual_decision_status": status,
        "review_notes": row.get("review_notes", ""),
    }


def archive_counts(rows: list[dict[str, str]]) -> dict[str, Counter[str]]:
    out: dict[str, Counter[str]] = defaultdict(Counter)
    for row in rows:
        idno = row.get("idno", "")
        if not idno:
            continue
        out[idno]["targets"] += 1
        if row.get("coverage_status") in {"covered_by_direct_raw_file", "covered_by_archive_member_needs_extraction"}:
            out[idno]["covered"] += 1
    return out


def write_handoff(row: dict[str, str], req_audits: list[dict[str, str]], concept_audits: list[dict[str, str]], variable_audits: list[dict[str, str]]) -> str:
    folder = PROJECT_ROOT / clean(row.get("local_target_folder", f"temp/raw_downloads/{row.get('idno', '')}/")).replace("\\", "/")
    folder.mkdir(parents=True, exist_ok=True)
    path = folder / "_PRIORITY_MANUAL_VERIFICATION_DECISION_GATE.md"
    path.write_text(
        f"""# Priority Manual Verification Decision Gate: {row.get('idno', '')}

Status: `{row['manual_verification_status']}`

Financial-protection manual ready: `{row['financial_protection_manual_ready']}`

Double-failure manual ready: `{row['double_failure_manual_ready']}`

Analysis-ready candidate: `{row['analysis_ready_candidate']}`

Remaining blockers: {row['remaining_blockers']}

## Evidence Counts

- requirements passed: {row['requirements_passed']} / {row['requirement_rows']}
- concepts passed: {row['concepts_passed']} / {row['concept_rows']}
- variables passed: {row['variables_passed']} / {row['variable_rows']}
- raw module targets covered: {row['archive_or_direct_targets_covered']} / {row['archive_file_targets']}
- accepted CHIRPS/ERA5 route: `{row['accepted_chirps_era5_route_status']}`

## Rule

This wave cannot be promoted until source gates are ready and all required
`fill_*` evidence columns are raw-backed and passing. A manual pass never
overrides missing raw package, missing schema, incomplete value checks, or
unaccepted climate linkage.
""",
        encoding="utf-8",
    )
    return rel(path)


def build_outputs() -> tuple[list[dict[str, str]], list[dict[str, str]], list[dict[str, str]], list[dict[str, str]], list[dict[str, str]]]:
    waves = read_csv_dicts(WAVE_PLAN_PATH)
    dataset_gate_by_id = first_by(read_csv_dicts(DATASET_GATE_PATH), "idno")
    requirements = read_csv_dicts(REQUIREMENT_PATH)
    concepts = read_csv_dicts(CONCEPT_PATH)
    variables = read_csv_dicts(VARIABLE_PATH)
    archive_by_id = archive_counts(read_csv_dicts(ARCHIVE_MATRIX_PATH))

    req_audits = [audit_row(row, "requirement", row.get("requirement_id", "")) for row in requirements]
    concept_audits = [audit_row(row, "concept", row.get("concept", "")) for row in concepts]
    variable_audits = [
        audit_row(
            row,
            "variable",
            f"{row.get('concept', '')}:{row.get('candidate_files', '')}:{row.get('candidate_raw_variable', '')}",
        )
        for row in variables
    ]

    req_by_id = group(req_audits, "idno")
    concept_by_id = group(concept_audits, "idno")
    variable_by_id = group(variable_audits, "idno")
    req_source_by_id = group(requirements, "idno")
    concept_source_by_id = group(concepts, "idno")

    dataset_rows: list[dict[str, str]] = []
    for wave in waves:
        idno = wave.get("idno", "")
        req_rows = req_by_id.get(idno, [])
        concept_rows = concept_by_id.get(idno, [])
        variable_rows = variable_by_id.get(idno, [])
        req_source = req_source_by_id.get(idno, [])
        concept_source = concept_source_by_id.get(idno, [])
        archive = archive_by_id.get(idno, Counter())

        req_passed = sum(1 for row in req_rows if row["manual_decision_status"] == "manual_verified")
        concept_passed = sum(1 for row in concept_rows if row["manual_decision_status"] == "manual_verified")
        variable_passed = sum(1 for row in variable_rows if row["manual_decision_status"] == "manual_verified")

        req_pass_set = {row["item_id"] for row in req_rows if row["manual_decision_status"] == "manual_verified"}
        concept_pass_set = {row["item_id"] for row in concept_rows if row["manual_decision_status"] == "manual_verified"}

        financial_req_ready = FINANCIAL_REQUIREMENTS.issubset(req_pass_set)
        double_req_ready = DOUBLE_FAILURE_REQUIREMENTS.issubset(req_pass_set)
        financial_concept_ready = FINANCIAL_CONCEPTS.issubset(concept_pass_set)
        double_concept_ready = DOUBLE_FAILURE_CONCEPTS.issubset(concept_pass_set)
        design_concept_ready = DESIGN_CONCEPTS.issubset(concept_pass_set)
        archive_ready = archive.get("targets", 0) > 0 and archive.get("covered", 0) == archive.get("targets", 0)
        climate_status = dataset_gate_by_id.get(idno, {}).get("accepted_chirps_era5_route_status", "not_accepted_missing_dataset_gate")
        climate_ready = climate_status.startswith("accepted")

        blockers = []
        if not archive_ready:
            blockers.append("priority direct/archive raw module coverage incomplete")
        if req_passed < len(req_rows):
            blockers.append("manual requirement verification incomplete")
        if not financial_concept_ready:
            blockers.append("manual financial concept verification incomplete")
        if not double_concept_ready:
            blockers.append("manual double-failure concept verification incomplete")
        if not design_concept_ready:
            blockers.append("manual survey-design/timing/geography concept verification incomplete")
        if variable_passed == 0:
            blockers.append("no selected raw variables manually verified")
        if not climate_ready:
            blockers.append("accepted CHIRPS/ERA5 route absent")

        financial_ready = financial_req_ready and financial_concept_ready and design_concept_ready and variable_passed > 0 and archive_ready
        double_ready = financial_ready and double_req_ready and double_concept_ready
        analysis_candidate = double_ready and climate_ready

        if analysis_candidate:
            status = "ready_for_harmonization_recipe_review"
        elif archive.get("covered", 0) == 0:
            status = "blocked_raw_module_coverage_missing"
        elif req_passed == 0 and concept_passed == 0 and variable_passed == 0:
            status = "blocked_no_manual_verification_passes"
        elif not climate_ready:
            status = "blocked_climate_route_not_accepted"
        else:
            status = "blocked_manual_verification_incomplete"

        dataset_row = {
            "acquisition_batch_rank": wave.get("acquisition_batch_rank", ""),
            "batch_role": wave.get("batch_role", ""),
            "country": wave.get("country", ""),
            "survey_name": wave.get("survey_name", ""),
            "wave": wave.get("wave", ""),
            "idno": idno,
            "requirement_rows": str(len(req_rows)),
            "requirements_passed": str(req_passed),
            "financial_requirements_passed": str(len(FINANCIAL_REQUIREMENTS & req_pass_set)),
            "double_failure_requirements_passed": str(len(DOUBLE_FAILURE_REQUIREMENTS & req_pass_set)),
            "concept_rows": str(len(concept_rows)),
            "concepts_passed": str(concept_passed),
            "financial_concepts_passed": str(len(FINANCIAL_CONCEPTS & concept_pass_set)),
            "double_failure_concepts_passed": str(len(DOUBLE_FAILURE_CONCEPTS & concept_pass_set)),
            "design_concepts_passed": str(len(DESIGN_CONCEPTS & concept_pass_set)),
            "variable_rows": str(len(variable_rows)),
            "variables_passed": str(variable_passed),
            "archive_file_targets": str(archive.get("targets", 0)),
            "archive_or_direct_targets_covered": str(archive.get("covered", 0)),
            "accepted_chirps_era5_route_status": climate_status,
            "manual_verification_status": status,
            "financial_protection_manual_ready": "1" if financial_ready else "0",
            "double_failure_manual_ready": "1" if double_ready else "0",
            "analysis_ready_candidate": "1" if analysis_candidate else "0",
            "remaining_blockers": "; ".join(blockers),
            "handoff_readme": "",
        }
        dataset_row["handoff_readme"] = write_handoff(dataset_row | {"local_target_folder": wave.get("local_target_folder", "")}, req_rows, concept_rows, variable_rows)
        dataset_rows.append(dataset_row)

    return dataset_rows, req_audits, concept_audits, variable_audits, build_summary(dataset_rows, req_audits, concept_audits, variable_audits)


def build_summary(
    dataset_rows: list[dict[str, str]],
    req_rows: list[dict[str, str]],
    concept_rows: list[dict[str, str]],
    variable_rows: list[dict[str, str]],
) -> list[dict[str, str]]:
    status_counts = Counter(row["manual_verification_status"] for row in dataset_rows)
    req_counts = Counter(row["manual_decision_status"] for row in req_rows)
    concept_counts = Counter(row["manual_decision_status"] for row in concept_rows)
    variable_counts = Counter(row["manual_decision_status"] for row in variable_rows)
    rows = [
        {"metric": "priority_manual_decision_dataset_rows", "value": str(len(dataset_rows)), "interpretation": "Priority waves with manual verification decision gates."},
        {"metric": "priority_manual_requirement_decision_rows", "value": str(len(req_rows)), "interpretation": "Requirement-level manual verification audit rows."},
        {"metric": "priority_manual_concept_decision_rows", "value": str(len(concept_rows)), "interpretation": "Concept-level manual verification audit rows."},
        {"metric": "priority_manual_variable_decision_rows", "value": str(len(variable_rows)), "interpretation": "Variable-level manual verification audit rows."},
        {"metric": "priority_manual_requirements_verified", "value": str(req_counts.get("manual_verified", 0)), "interpretation": "Requirement rows passing source and fill-field manual verification."},
        {"metric": "priority_manual_concepts_verified", "value": str(concept_counts.get("manual_verified", 0)), "interpretation": "Concept rows passing source and fill-field manual verification."},
        {"metric": "priority_manual_variables_verified", "value": str(variable_counts.get("manual_verified", 0)), "interpretation": "Variable rows passing source and fill-field manual verification."},
        {"metric": "priority_financial_protection_manual_ready_countries", "value": str(len({row["country"] for row in dataset_rows if row["financial_protection_manual_ready"] == "1"})), "interpretation": "Countries with financial-protection manual verification ready."},
        {"metric": "priority_double_failure_manual_ready_waves", "value": str(sum(1 for row in dataset_rows if row["double_failure_manual_ready"] == "1")), "interpretation": "Country-waves with double-failure manual verification ready."},
        {"metric": "priority_analysis_ready_candidates", "value": str(sum(1 for row in dataset_rows if row["analysis_ready_candidate"] == "1")), "interpretation": "Country-waves ready for harmonization recipe review and climate-linked data promotion."},
        {"metric": "priority_manual_handoff_readmes_written", "value": str(sum(1 for row in dataset_rows if row.get("handoff_readme"))), "interpretation": "Per-wave manual verification decision README files written."},
        {"metric": "modeling_gate_status", "value": "blocked", "interpretation": "Models remain blocked until promoted registry thresholds and accepted climate linkage pass."},
    ]
    for status, count in sorted(status_counts.items()):
        rows.append({"metric": f"dataset_manual_status_{status}", "value": str(count), "interpretation": "Dataset manual verification status count."})
    for status, count in sorted(req_counts.items()):
        rows.append({"metric": f"requirement_manual_status_{status}", "value": str(count), "interpretation": "Requirement manual verification status count."})
    for status, count in sorted(concept_counts.items()):
        rows.append({"metric": f"concept_manual_status_{status}", "value": str(count), "interpretation": "Concept manual verification status count."})
    for status, count in sorted(variable_counts.items()):
        rows.append({"metric": f"variable_manual_status_{status}", "value": str(count), "interpretation": "Variable manual verification status count."})
    return rows


def markdown_table(rows: list[dict[str, str]], columns: list[str], limit: int = 30) -> str:
    lines = ["| " + " | ".join(columns) + " |", "|" + "|".join("---" for _ in columns) + "|"]
    for row in rows[:limit]:
        values = []
        for column in columns:
            value = clean(row.get(column)).replace("|", "/")
            if len(value) > 120:
                value = value[:117] + "..."
            values.append(value)
        lines.append("| " + " | ".join(values) + " |")
    return "\n".join(lines)


def write_report(dataset_rows: list[dict[str, str]], summary: list[dict[str, str]]) -> None:
    summary_table = "\n".join(f"| {row['metric']} | {row['value']} | {row['interpretation']} |" for row in summary)
    REPORT_PATH.write_text(
        f"""# Priority Manual Verification Decision Gate

Status: fail-closed consumer of the priority workbook `fill_*` fields. This
report does not promote data by itself; it verifies whether the human raw-value
audit evidence is complete enough to allow harmonization-recipe review.

## Summary

| Metric | Value | Interpretation |
|---|---:|---|
{summary_table}

## Dataset Decisions

{markdown_table(dataset_rows, ['acquisition_batch_rank', 'idno', 'country', 'wave', 'manual_verification_status', 'requirements_passed', 'concepts_passed', 'variables_passed', 'archive_or_direct_targets_covered', 'analysis_ready_candidate'], 20)}

## Rule

The decision gate requires source gates plus manual `fill_*` fields. A blank or
ambiguous fill value is treated as not passing. Manual evidence is preserved by
`script/126_build_priority_raw_verification_workbook.py` when templates are
rebuilt.

## Machine-Readable Outputs

- `temp/priority_manual_verification_decision_gate.csv`
- `temp/priority_manual_requirement_decision_audit.csv`
- `temp/priority_manual_concept_decision_audit.csv`
- `temp/priority_manual_variable_decision_audit.csv`
- `result/priority_manual_verification_decision_summary.csv`
""",
        encoding="utf-8",
    )


def main() -> None:
    ensure_dirs()
    dataset_rows, req_rows, concept_rows, variable_rows, summary = build_outputs()
    write_csv(DATASET_DECISION_PATH, dataset_rows, DATASET_COLUMNS)
    write_csv(REQUIREMENT_DECISION_PATH, req_rows, AUDIT_COLUMNS)
    write_csv(CONCEPT_DECISION_PATH, concept_rows, AUDIT_COLUMNS)
    write_csv(VARIABLE_DECISION_PATH, variable_rows, AUDIT_COLUMNS)
    write_csv(SUMMARY_PATH, summary, SUMMARY_COLUMNS)
    write_report(dataset_rows, summary)
    append_log(
        TEMP_DIR / "audit_log.md",
        f"Built priority manual verification decision gate datasets={len(dataset_rows)} requirements={len(req_rows)} concepts={len(concept_rows)} variables={len(variable_rows)}.",
    )
    print(
        f"Priority manual verification decision gate datasets={len(dataset_rows)} "
        f"requirements={len(req_rows)} concepts={len(concept_rows)} variables={len(variable_rows)}."
    )


if __name__ == "__main__":
    main()
