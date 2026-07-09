from __future__ import annotations

import csv
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

from common import PROJECT_ROOT, REPORT_DIR, RESULT_DIR, TEMP_DIR, append_log, ensure_dirs, write_csv


QUEUE_PATH = TEMP_DIR / "priority_lsms_isa_refocused_acquisition_queue.csv"
COVERAGE_PATH = TEMP_DIR / "priority_lsms_isa_requirement_variable_coverage.csv"
VARIABLE_MATRIX_PATH = TEMP_DIR / "priority_lsms_isa_variable_evidence_matrix.csv"
FILE_SHORTLIST_PATH = TEMP_DIR / "priority_lsms_isa_concept_file_shortlist.csv"
RAW_INTAKE_LEDGER_PATH = TEMP_DIR / "priority_lsms_isa_raw_package_intake_ledger.csv"
ARCHIVE_PREFLIGHT_PATH = TEMP_DIR / "priority_lsms_isa_archive_member_preflight.csv"
PACKET_INDEX_PATH = TEMP_DIR / "priority_lsms_isa_country_wave_promotion_packet_index.csv"

REQUIREMENT_WORKBOOK_PATH = TEMP_DIR / "priority_lsms_isa_raw_value_requirement_workbook.csv"
VARIABLE_WORKBOOK_PATH = TEMP_DIR / "priority_lsms_isa_raw_value_variable_workbook.csv"
FILE_WORKBOOK_PATH = TEMP_DIR / "priority_lsms_isa_raw_value_file_workbook.csv"
SUMMARY_PATH = RESULT_DIR / "priority_lsms_isa_raw_value_verification_workbook_summary.csv"
REPORT_PATH = REPORT_DIR / "priority_lsms_isa_raw_value_verification_workbook.md"

RAW_ROOT = TEMP_DIR / "raw_downloads"

REQUIREMENT_CHECKS = {
    "household_person_keys": {
        "role": "merge_key_gate",
        "checks": "confirm household/person IDs; module key cardinality; duplicate keys; household-person join path; panel/wave IDs where relevant",
        "acceptance_rule": "At least one household key and all needed person/module keys are raw-value verified, unique at the expected level, and joinable across required files.",
        "promotion_effect": "unblocks household/person merge key gate",
    },
    "weights_and_design": {
        "role": "survey_design_gate",
        "checks": "confirm household/person weights; PSU/cluster; strata; sample domains; positive/nonmissing weight distribution; documentation source",
        "acceptance_rule": "Weights and design variables are raw-value verified and documented well enough for descriptive and model-weight sensitivity checks.",
        "promotion_effect": "unblocks weighted prevalence and survey-design gate",
    },
    "consumption_or_income": {
        "role": "financial_denominator_gate",
        "checks": "confirm total consumption or income aggregate; currency; period; household level; zero/missing semantics; survey-team aggregate preference",
        "acceptance_rule": "A household-level total consumption/income denominator is verified with unit, period, and missing semantics.",
        "promotion_effect": "unblocks CHE10/CHE25 denominator review",
    },
    "oop_health_expenditure": {
        "role": "financial_outcome_gate",
        "checks": "confirm OOP health expenditure variables; payer scope; service/drug categories; recall periods; zero vs missing; aggregation policy",
        "acceptance_rule": "OOP health spending inputs are raw-value verified with recall period and aggregation policy documented.",
        "promotion_effect": "unblocks financial-protection outcome construction review",
    },
    "health_need_and_access": {
        "role": "access_outcome_gate",
        "checks": "confirm illness/need denominator; care sought; care not sought; cost/distance/supply barriers; skip pattern; person vs household level",
        "acceptance_rule": "Need/access variables are raw-value verified with denominator, skip pattern, and barrier coding documented.",
        "promotion_effect": "unblocks forgone-care and double-failure outcome review",
    },
    "survey_timing": {
        "role": "climate_timing_gate",
        "checks": "confirm interview date/month/year or fieldwork window; visit/season module; valid ranges; missing dates; usable lag-window anchor",
        "acceptance_rule": "Survey timing is verified at month or date resolution, or a defensible fieldwork window is documented.",
        "promotion_effect": "unblocks climate exposure lag-window construction",
    },
    "climate_geography": {
        "role": "climate_geography_gate",
        "checks": "confirm GPS/cluster/EA/admin variables; coordinate quality; displacement/suppression; admin codes; rural/urban; boundary crosswalk path",
        "acceptance_rule": "A geography route is raw-value verified and can support point, cluster, EA, or admin climate linkage with quality caveats.",
        "promotion_effect": "unblocks CHIRPS/ERA5 linkage route review",
    },
    "missing_codes_units_recall_skip_patterns": {
        "role": "documentation_semantics_gate",
        "checks": "confirm value labels; missing/refused/don't-know codes; skip universes; units; recall periods; valid ranges; questionnaire text",
        "acceptance_rule": "Critical variables have documented missing codes, units, recall periods, and skip patterns from raw metadata and questionnaires.",
        "promotion_effect": "unblocks final raw-value promotion decision",
    },
}

REQUIREMENT_COLUMNS = [
    "download_priority_order",
    "queue_role",
    "country",
    "wave",
    "idno",
    "survey_name",
    "requirement",
    "requirement_role",
    "candidate_variable_rows",
    "strong_candidate_variable_rows",
    "candidate_file_rows",
    "top_file_names",
    "required_checks",
    "acceptance_rule",
    "raw_package_status",
    "archive_preflight_status",
    "current_verification_status",
    "promotion_effect_if_passed",
    "fill_raw_file_or_archive_member_used",
    "fill_raw_variables_verified",
    "fill_value_label_pass",
    "fill_unit_or_recall_pass",
    "fill_missing_code_pass",
    "fill_skip_pattern_pass",
    "fill_merge_key_or_level_pass",
    "fill_accept_requirement",
    "review_notes",
]

VARIABLE_COLUMNS = [
    "download_priority_order",
    "queue_role",
    "country",
    "wave",
    "idno",
    "survey_name",
    "requirement",
    "requirement_role",
    "candidate_rank",
    "file_name",
    "variable_name",
    "variable_label",
    "match_score",
    "checklist_ref",
    "raw_package_status",
    "archive_preflight_status",
    "current_verification_status",
    "fill_raw_file_used",
    "fill_raw_variable_used",
    "fill_variable_label_verified",
    "fill_value_distribution_checked",
    "fill_missing_codes_documented",
    "fill_unit_recall_period_documented",
    "fill_merge_key_or_level_verified",
    "fill_skip_pattern_checked",
    "fill_promote_variable",
    "review_notes",
]

FILE_COLUMNS = [
    "download_priority_order",
    "queue_role",
    "country",
    "wave",
    "idno",
    "survey_name",
    "requirement",
    "requirement_role",
    "file_rank",
    "file_name",
    "file_description",
    "candidate_variable_rows",
    "strong_candidate_variable_rows",
    "top_variable_names",
    "required_checks",
    "raw_package_status",
    "archive_preflight_status",
    "current_file_verification_status",
    "fill_file_present_direct_or_archive",
    "fill_file_readable",
    "fill_schema_extracted",
    "fill_required_variables_found",
    "fill_documentation_crosschecked",
    "fill_accept_file_for_requirement",
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


def safe_int(value: Any, default: int = 0) -> int:
    try:
        text = clean(value)
        return int(float(text)) if text else default
    except (TypeError, ValueError):
        return default


def rel(path: Path) -> str:
    try:
        return str(path.relative_to(PROJECT_ROOT)).replace("\\", "/")
    except ValueError:
        return str(path).replace("\\", "/")


def shorten(value: Any, limit: int = 220) -> str:
    text = " ".join(clean(value).split())
    if len(text) <= limit:
        return text
    return text[: limit - 3] + "..."


def by_id(rows: list[dict[str, str]], field: str = "idno") -> dict[str, list[dict[str, str]]]:
    out: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in rows:
        idno = clean(row.get(field))
        if idno:
            out[idno].append(row)
    return out


def one_by_id(rows: list[dict[str, str]], field: str = "idno") -> dict[str, dict[str, str]]:
    out: dict[str, dict[str, str]] = {}
    for row in rows:
        idno = clean(row.get(field))
        if idno and idno not in out:
            out[idno] = row
    return out


def raw_folder_path(folder: str, idno: str) -> Path:
    folder_clean = clean(folder).replace("\\", "/").strip("/")
    if folder_clean:
        return PROJECT_ROOT / folder_clean
    return RAW_ROOT / idno


def current_status(raw_row: dict[str, str], archive_row: dict[str, str]) -> str:
    if safe_int(raw_row.get("original_file_count")) == 0:
        return "blocked_no_original_package"
    if clean(archive_row.get("archive_preflight_status")) != "ready_for_raw_receipt_schema_and_manual_review":
        return "blocked_archive_or_direct_file_preflight_not_ready"
    return "ready_for_manual_raw_value_review"


def requirement_spec(requirement: str) -> dict[str, str]:
    return REQUIREMENT_CHECKS.get(
        requirement,
        {
            "role": "required_gate",
            "checks": "verify raw values, labels, units, missing codes, skip patterns, merge level, and documentation",
            "acceptance_rule": "Requirement is accepted only after raw-value verification passes.",
            "promotion_effect": "unblocks requirement gate",
        },
    )


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


def build_requirement_rows(
    queue_rows: list[dict[str, str]],
    coverage_by_id: dict[str, list[dict[str, str]]],
    raw_by_id: dict[str, dict[str, str]],
    archive_by_id: dict[str, dict[str, str]],
) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    for wave in queue_rows:
        idno = clean(wave.get("idno"))
        raw = raw_by_id.get(idno, {})
        archive = archive_by_id.get(idno, {})
        status = current_status(raw, archive)
        for cov in coverage_by_id.get(idno, []):
            requirement = clean(cov.get("requirement"))
            spec = requirement_spec(requirement)
            rows.append(
                {
                    "download_priority_order": clean(wave.get("download_priority_order")),
                    "queue_role": clean(wave.get("queue_role")),
                    "country": clean(wave.get("country")),
                    "wave": clean(wave.get("wave")),
                    "idno": idno,
                    "survey_name": clean(wave.get("survey_name")),
                    "requirement": requirement,
                    "requirement_role": spec["role"],
                    "candidate_variable_rows": clean(cov.get("candidate_variable_rows")),
                    "strong_candidate_variable_rows": clean(cov.get("strong_candidate_variable_rows")),
                    "candidate_file_rows": clean(cov.get("candidate_file_rows")),
                    "top_file_names": clean(cov.get("top_file_names")),
                    "required_checks": spec["checks"],
                    "acceptance_rule": spec["acceptance_rule"],
                    "raw_package_status": clean(raw.get("intake_acceptance_status")) or "missing",
                    "archive_preflight_status": clean(archive.get("archive_preflight_status")) or "missing",
                    "current_verification_status": status,
                    "promotion_effect_if_passed": spec["promotion_effect"],
                    "fill_raw_file_or_archive_member_used": "",
                    "fill_raw_variables_verified": "",
                    "fill_value_label_pass": "",
                    "fill_unit_or_recall_pass": "",
                    "fill_missing_code_pass": "",
                    "fill_skip_pattern_pass": "",
                    "fill_merge_key_or_level_pass": "",
                    "fill_accept_requirement": "",
                    "review_notes": "",
                }
            )
    return rows


def build_variable_rows(
    queue_by_id: dict[str, dict[str, str]],
    matrix_rows: list[dict[str, str]],
    raw_by_id: dict[str, dict[str, str]],
    archive_by_id: dict[str, dict[str, str]],
) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    for row in matrix_rows:
        idno = clean(row.get("idno"))
        wave = queue_by_id.get(idno, {})
        raw = raw_by_id.get(idno, {})
        archive = archive_by_id.get(idno, {})
        requirement = clean(row.get("requirement"))
        spec = requirement_spec(requirement)
        status = current_status(raw, archive)
        rows.append(
            {
                "download_priority_order": clean(row.get("download_priority_order")),
                "queue_role": clean(row.get("queue_role")),
                "country": clean(row.get("country")),
                "wave": clean(row.get("wave")),
                "idno": idno,
                "survey_name": clean(wave.get("survey_name")),
                "requirement": requirement,
                "requirement_role": spec["role"],
                "candidate_rank": clean(row.get("candidate_rank")),
                "file_name": clean(row.get("file_name")),
                "variable_name": clean(row.get("variable_name")),
                "variable_label": clean(row.get("variable_label")),
                "match_score": clean(row.get("match_score")),
                "checklist_ref": requirement,
                "raw_package_status": clean(raw.get("intake_acceptance_status")) or "missing",
                "archive_preflight_status": clean(archive.get("archive_preflight_status")) or "missing",
                "current_verification_status": status,
                "fill_raw_file_used": "",
                "fill_raw_variable_used": "",
                "fill_variable_label_verified": "",
                "fill_value_distribution_checked": "",
                "fill_missing_codes_documented": "",
                "fill_unit_recall_period_documented": "",
                "fill_merge_key_or_level_verified": "",
                "fill_skip_pattern_checked": "",
                "fill_promote_variable": "",
                "review_notes": "",
            }
        )
    return rows


def build_file_rows(
    queue_by_id: dict[str, dict[str, str]],
    shortlist_rows: list[dict[str, str]],
    raw_by_id: dict[str, dict[str, str]],
    archive_by_id: dict[str, dict[str, str]],
) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    for row in shortlist_rows:
        idno = clean(row.get("idno"))
        wave = queue_by_id.get(idno, {})
        raw = raw_by_id.get(idno, {})
        archive = archive_by_id.get(idno, {})
        requirement = clean(row.get("requirement"))
        spec = requirement_spec(requirement)
        rows.append(
            {
                "download_priority_order": clean(row.get("download_priority_order")),
                "queue_role": clean(row.get("queue_role")),
                "country": clean(row.get("country")),
                "wave": clean(row.get("wave")),
                "idno": idno,
                "survey_name": clean(wave.get("survey_name")),
                "requirement": requirement,
                "requirement_role": spec["role"],
                "file_rank": clean(row.get("file_rank")),
                "file_name": clean(row.get("file_name")),
                "file_description": clean(row.get("file_description")),
                "candidate_variable_rows": clean(row.get("candidate_variable_rows")),
                "strong_candidate_variable_rows": clean(row.get("strong_candidate_variable_rows")),
                "top_variable_names": clean(row.get("top_variable_names")),
                "required_checks": spec["checks"],
                "raw_package_status": clean(raw.get("intake_acceptance_status")) or "missing",
                "archive_preflight_status": clean(archive.get("archive_preflight_status")) or "missing",
                "current_file_verification_status": current_status(raw, archive),
                "fill_file_present_direct_or_archive": "",
                "fill_file_readable": "",
                "fill_schema_extracted": "",
                "fill_required_variables_found": "",
                "fill_documentation_crosschecked": "",
                "fill_accept_file_for_requirement": "",
                "review_notes": "",
            }
        )
    return rows


def write_handoffs(
    queue_rows: list[dict[str, str]],
    requirement_by_id: dict[str, list[dict[str, str]]],
    file_by_id: dict[str, list[dict[str, str]]],
) -> int:
    count = 0
    for wave in queue_rows:
        idno = clean(wave.get("idno"))
        folder = raw_folder_path(clean(wave.get("local_target_folder")), idno)
        folder.mkdir(parents=True, exist_ok=True)
        path = folder / "_PRIORITY_LSMS_ISA_RAW_VALUE_VERIFICATION_WORKBOOK.md"
        req_rows = requirement_by_id.get(idno, [])
        file_rows = file_by_id.get(idno, [])
        path.write_text(
            f"""# Priority LSMS-ISA Raw Value Verification Workbook

Dataset: `{idno}` - {wave.get('country', '')} {wave.get('wave', '')}

Official get-microdata URL: {wave.get('official_get_microdata_url', '')}

Target folder: `{wave.get('local_target_folder', '')}`

Current status: blocked until the complete original raw package and
documentation are present and readable.

## Requirement Checklist

{markdown_table(req_rows, ['requirement', 'requirement_role', 'candidate_variable_rows', 'candidate_file_rows', 'current_verification_status'], 12)}

## File Review Preview

{markdown_table(file_rows, ['requirement', 'file_name', 'candidate_variable_rows', 'top_variable_names', 'current_file_verification_status'], 12)}

## Workbook Files

- `temp/priority_lsms_isa_raw_value_requirement_workbook.csv`
- `temp/priority_lsms_isa_raw_value_variable_workbook.csv`
- `temp/priority_lsms_isa_raw_value_file_workbook.csv`

## Stop Rule

Do not mark this wave as value-verified or analysis-ready until the workbook
evidence fields are filled from original raw files and all required gates pass.
""",
            encoding="utf-8",
        )
        count += 1
    return count


def build_summary(
    requirement_rows: list[dict[str, str]],
    variable_rows: list[dict[str, str]],
    file_rows: list[dict[str, str]],
    handoff_count: int,
) -> list[dict[str, str]]:
    requirement_status_counts = Counter(row.get("current_verification_status", "") for row in requirement_rows)
    variable_status_counts = Counter(row.get("current_verification_status", "") for row in variable_rows)
    file_status_counts = Counter(row.get("current_file_verification_status", "") for row in file_rows)
    role_counts = Counter(row.get("queue_role", "") for row in requirement_rows if row.get("requirement") == "household_person_keys")
    dataset_count = len({row.get("idno", "") for row in requirement_rows})
    rows = [
        {"metric": "priority_lsms_raw_value_workbook_dataset_rows", "value": str(dataset_count), "interpretation": "Refocused LSMS/ISA datasets covered by the raw-value verification workbook."},
        {"metric": "priority_lsms_raw_value_workbook_requirement_rows", "value": str(len(requirement_rows)), "interpretation": "Requirement-level raw-value verification rows."},
        {"metric": "priority_lsms_raw_value_workbook_variable_rows", "value": str(len(variable_rows)), "interpretation": "Candidate variable-level raw-value verification rows."},
        {"metric": "priority_lsms_raw_value_workbook_file_rows", "value": str(len(file_rows)), "interpretation": "Candidate file-level raw-value verification rows."},
        {"metric": "priority_lsms_raw_value_workbook_handoff_readmes_written", "value": str(handoff_count), "interpretation": "Per-wave raw-folder workbook handoffs written."},
        {"metric": "priority_lsms_raw_value_workbook_ready_for_manual_review_rows", "value": str(requirement_status_counts.get("ready_for_manual_raw_value_review", 0)), "interpretation": "Requirement rows ready for manual raw value review because raw package and archive preflight are present."},
        {"metric": "priority_lsms_raw_value_workbook_blocked_requirement_rows", "value": str(len(requirement_rows) - requirement_status_counts.get("ready_for_manual_raw_value_review", 0)), "interpretation": "Requirement rows still blocked before raw value review."},
        {"metric": "priority_lsms_raw_value_workbook_raw_value_verified_rows", "value": "0", "interpretation": "Workbook rows are unverified until reviewer evidence fields are filled and accepted."},
        {"metric": "priority_lsms_raw_value_workbook_data_write_status", "value": "blocked_no_promoted_rows", "interpretation": "No country-wave may write to data/ from an unfilled verification workbook."},
        {"metric": "modeling_gate_status", "value": "blocked", "interpretation": "Models remain blocked until promoted registry thresholds and accepted climate linkage pass."},
    ]
    for role, count in sorted(role_counts.items()):
        rows.append({"metric": f"priority_lsms_raw_value_workbook_queue_role_{role}", "value": str(count), "interpretation": "Dataset count by refocused queue role."})
    for status, count in sorted(requirement_status_counts.items()):
        rows.append({"metric": f"priority_lsms_raw_value_workbook_requirement_status_{status}", "value": str(count), "interpretation": "Requirement workbook status count."})
    for status, count in sorted(variable_status_counts.items()):
        rows.append({"metric": f"priority_lsms_raw_value_workbook_variable_status_{status}", "value": str(count), "interpretation": "Variable workbook status count."})
    for status, count in sorted(file_status_counts.items()):
        rows.append({"metric": f"priority_lsms_raw_value_workbook_file_status_{status}", "value": str(count), "interpretation": "File workbook status count."})
    return rows


def write_report(
    requirement_rows: list[dict[str, str]],
    variable_rows: list[dict[str, str]],
    file_rows: list[dict[str, str]],
    summary_rows: list[dict[str, str]],
) -> None:
    summary_table = "\n".join(f"| {row['metric']} | {row['value']} | {row['interpretation']} |" for row in summary_rows)
    REPORT_PATH.write_text(
        f"""# Priority LSMS-ISA Raw Value Verification Workbook

Status: fail-closed raw-value verification workbook for the 19-wave refocused
LSMS/ISA promotion queue. It translates official metadata candidates into
requirement, variable, and file review rows that must be filled from original
raw files before any country-wave can be promoted.

This workbook does not verify raw values by itself.

## Summary

| Metric | Value | Interpretation |
|---|---:|---|
{summary_table}

## Requirement Workbook Preview

{markdown_table(requirement_rows, ['download_priority_order', 'idno', 'requirement', 'requirement_role', 'candidate_variable_rows', 'candidate_file_rows', 'current_verification_status'], 80)}

## Variable Workbook Preview

{markdown_table(variable_rows, ['download_priority_order', 'idno', 'requirement', 'candidate_rank', 'file_name', 'variable_name', 'variable_label', 'current_verification_status'], 80)}

## File Workbook Preview

{markdown_table(file_rows, ['download_priority_order', 'idno', 'requirement', 'file_rank', 'file_name', 'candidate_variable_rows', 'current_file_verification_status'], 80)}

## Machine-Readable Outputs

- `temp/priority_lsms_isa_raw_value_requirement_workbook.csv`
- `temp/priority_lsms_isa_raw_value_variable_workbook.csv`
- `temp/priority_lsms_isa_raw_value_file_workbook.csv`
- `result/priority_lsms_isa_raw_value_verification_workbook_summary.csv`

## Guardrails

- Empty fill fields mean the requirement is not value-verified.
- Metadata candidates must be checked against original raw files and questionnaires.
- Financial-protection readiness requires verified consumption/income, OOP health expenditure, weights, design, and denominator semantics.
- Access readiness requires verified illness/need, care-seeking, forgone-care, and barrier skip patterns.
- Climate readiness requires verified timing and geography plus an accepted CHIRPS or ERA5 route.
""",
        encoding="utf-8",
    )


def main() -> None:
    ensure_dirs()
    queue_rows = read_csv_dicts(QUEUE_PATH)
    queue_by_id = {clean(row.get("idno")): row for row in queue_rows}
    coverage_by_id = by_id(read_csv_dicts(COVERAGE_PATH))
    matrix_rows = read_csv_dicts(VARIABLE_MATRIX_PATH)
    shortlist_rows = read_csv_dicts(FILE_SHORTLIST_PATH)
    raw_by_id = one_by_id(read_csv_dicts(RAW_INTAKE_LEDGER_PATH))
    archive_by_id = one_by_id(read_csv_dicts(ARCHIVE_PREFLIGHT_PATH))

    requirement_rows = build_requirement_rows(queue_rows, coverage_by_id, raw_by_id, archive_by_id)
    variable_rows = build_variable_rows(queue_by_id, matrix_rows, raw_by_id, archive_by_id)
    file_rows = build_file_rows(queue_by_id, shortlist_rows, raw_by_id, archive_by_id)
    handoff_count = write_handoffs(queue_rows, by_id(requirement_rows), by_id(file_rows))
    summary_rows = build_summary(requirement_rows, variable_rows, file_rows, handoff_count)

    write_csv(REQUIREMENT_WORKBOOK_PATH, requirement_rows, REQUIREMENT_COLUMNS)
    write_csv(VARIABLE_WORKBOOK_PATH, variable_rows, VARIABLE_COLUMNS)
    write_csv(FILE_WORKBOOK_PATH, file_rows, FILE_COLUMNS)
    write_csv(SUMMARY_PATH, summary_rows, SUMMARY_COLUMNS)
    write_report(requirement_rows, variable_rows, file_rows, summary_rows)
    append_log(
        TEMP_DIR / "audit_log.md",
        f"Built priority LSMS/ISA raw value verification workbook requirements={len(requirement_rows)} variables={len(variable_rows)} files={len(file_rows)}.",
    )
    print(
        "Priority LSMS/ISA raw value verification workbook "
        f"requirements={len(requirement_rows)} variables={len(variable_rows)} files={len(file_rows)}."
    )


if __name__ == "__main__":
    main()
