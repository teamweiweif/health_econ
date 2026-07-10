from __future__ import annotations

import csv
from pathlib import Path
from typing import Any

from common import REPORT_DIR, RESULT_DIR, append_log, ensure_dirs, write_csv


AUDIT_PATH = RESULT_DIR / "priority_lsms_isa_external_local_raw_candidate_audit.csv"
INTAKE_PATH = RESULT_DIR / "priority_lsms_isa_external_local_raw_intake_decision.csv"
DOC_MANIFEST_PATH = RESULT_DIR / "priority_lsms_isa_external_local_raw_document_manifest.csv"
SUMMARY_PATH = RESULT_DIR / "priority_lsms_isa_external_local_raw_intake_summary.csv"
REPORT_PATH = REPORT_DIR / "priority_lsms_isa_external_local_raw_intake_decision.md"

DOC_SUFFIXES = {".pdf", ".txt", ".doc", ".docx", ".rtf"}
QUESTIONNAIRE_TOKENS = ("quest", "questionnaire", "interview", "hhq", "household")
CODEBOOK_TOKENS = ("codebook", "dictionary", "basic", "information", "metadata", "readme")

INTAKE_COLUMNS = [
    "intake_rank",
    "download_priority_order",
    "queue_role",
    "country",
    "wave",
    "idno",
    "locked_download_target",
    "current_plan_status",
    "external_candidate_folder",
    "external_candidate_folder_exists",
    "documentation_file_rows",
    "questionnaire_document_rows",
    "codebook_or_basic_info_rows",
    "external_raw_like_file_rows",
    "expected_file_rows",
    "external_expected_file_match_rows",
    "expected_file_match_rate",
    "core_file_rows",
    "external_core_file_match_rows",
    "core_file_match_rate",
    "matched_requirement_names",
    "unmatched_requirement_names",
    "candidate_receipt_status",
    "package_review_status",
    "intake_decision",
    "copy_target_folder",
    "copy_command_hint",
    "post_copy_validation_command",
    "data_write_gate_status",
    "modeling_gate_status",
]

DOC_COLUMNS = [
    "intake_rank",
    "country",
    "wave",
    "idno",
    "locked_download_target",
    "external_candidate_folder",
    "document_file_name",
    "document_relative_path",
    "document_extension",
    "document_bytes",
    "document_evidence_role",
]

SUMMARY_COLUMNS = ["metric", "value", "interpretation"]


def read_csv_dicts(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        return []
    with path.open(encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def clean(value: Any) -> str:
    if value is None:
        return ""
    return " ".join(str(value).split())


def safe_int(value: Any, default: int = 0) -> int:
    try:
        text = clean(value)
        return int(float(text)) if text else default
    except (TypeError, ValueError):
        return default


def rate(numerator: int, denominator: int) -> str:
    if denominator <= 0:
        return ""
    return f"{numerator / denominator:.3f}"


def doc_role(path: Path) -> str:
    name = path.name.lower()
    if any(token in name for token in QUESTIONNAIRE_TOKENS):
        return "questionnaire_or_household_interview_document"
    if any(token in name for token in CODEBOOK_TOKENS):
        return "codebook_basic_info_or_metadata_document"
    return "other_documentation"


def documentation_files(folder: Path) -> list[Path]:
    if not folder.exists() or not folder.is_dir():
        return []
    return sorted(
        (path for path in folder.rglob("*") if path.is_file() and path.suffix.lower() in DOC_SUFFIXES),
        key=lambda path: str(path).lower(),
    )


def decision_for(row: dict[str, str], doc_count: int) -> tuple[int, str, str]:
    locked = clean(row.get("locked_download_target")) == "1"
    expected_rows = safe_int(row.get("expected_file_rows"))
    expected_matches = safe_int(row.get("external_expected_file_match_rows"))
    core_rows = safe_int(row.get("core_file_rows"))
    core_matches = safe_int(row.get("external_core_file_match_rows"))
    folder_exists = clean(row.get("external_candidate_folder_exists")) == "1"
    expected_complete = expected_rows > 0 and expected_matches >= expected_rows * 0.95
    core_complete = core_rows > 0 and core_matches == core_rows
    has_docs = doc_count > 0

    if not folder_exists or expected_matches == 0:
        return 90, "not_review_ready", "No usable external local folder or expected-file match."
    if locked and expected_complete and core_complete and has_docs:
        return (
            10,
            "copy_review_ready_pending_official_provenance",
            "Selected wave has near-complete expected-file matches, complete requirement-linked core filenames, and documentation; review official provenance before copying.",
        )
    if locked and expected_matches > 0:
        return (
            30,
            "selected_partial_intake_review_required",
            "Selected wave has external local matches, but expected/core completeness is not sufficient for package receipt without targeted provenance and missing-file review.",
        )
    return (
        60,
        "backup_intake_review_after_selected_batch",
        "Backup wave has external local matches; hold for later unless it is needed to replace a selected wave or expand country-wave coverage.",
    )


def build_outputs() -> tuple[list[dict[str, str]], list[dict[str, str]], list[dict[str, str]]]:
    audit_rows = read_csv_dicts(AUDIT_PATH)
    candidates = [
        row
        for row in audit_rows
        if clean(row.get("external_candidate_folder_exists")) == "1"
        and safe_int(row.get("external_expected_file_match_rows")) > 0
    ]

    intake_rows: list[dict[str, str]] = []
    doc_rows: list[dict[str, str]] = []

    for row in candidates:
        folder = Path(clean(row.get("external_candidate_folder")))
        docs = documentation_files(folder)
        questionnaire_rows = [path for path in docs if doc_role(path) == "questionnaire_or_household_interview_document"]
        codebook_rows = [path for path in docs if doc_role(path) == "codebook_basic_info_or_metadata_document"]
        rank, decision, review_status = decision_for(row, len(docs))
        idno = clean(row.get("idno"))

        for path in docs:
            try:
                relative_path = str(path.relative_to(folder))
            except ValueError:
                relative_path = path.name
            doc_rows.append(
                {
                    "intake_rank": str(rank),
                    "country": clean(row.get("country")),
                    "wave": clean(row.get("wave")),
                    "idno": idno,
                    "locked_download_target": clean(row.get("locked_download_target")),
                    "external_candidate_folder": str(folder),
                    "document_file_name": path.name,
                    "document_relative_path": relative_path,
                    "document_extension": path.suffix.lower(),
                    "document_bytes": str(path.stat().st_size),
                    "document_evidence_role": doc_role(path),
                }
            )

        target = clean(row.get("copy_target_folder"))
        intake_rows.append(
            {
                "intake_rank": str(rank),
                "download_priority_order": clean(row.get("download_priority_order")),
                "queue_role": clean(row.get("queue_role")),
                "country": clean(row.get("country")),
                "wave": clean(row.get("wave")),
                "idno": idno,
                "locked_download_target": clean(row.get("locked_download_target")),
                "current_plan_status": clean(row.get("current_plan_status")),
                "external_candidate_folder": str(folder),
                "external_candidate_folder_exists": clean(row.get("external_candidate_folder_exists")),
                "documentation_file_rows": str(len(docs)),
                "questionnaire_document_rows": str(len(questionnaire_rows)),
                "codebook_or_basic_info_rows": str(len(codebook_rows)),
                "external_raw_like_file_rows": clean(row.get("external_raw_like_file_rows")),
                "expected_file_rows": clean(row.get("expected_file_rows")),
                "external_expected_file_match_rows": clean(row.get("external_expected_file_match_rows")),
                "expected_file_match_rate": rate(safe_int(row.get("external_expected_file_match_rows")), safe_int(row.get("expected_file_rows"))),
                "core_file_rows": clean(row.get("core_file_rows")),
                "external_core_file_match_rows": clean(row.get("external_core_file_match_rows")),
                "core_file_match_rate": rate(safe_int(row.get("external_core_file_match_rows")), safe_int(row.get("core_file_rows"))),
                "matched_requirement_names": clean(row.get("matched_requirement_names")),
                "unmatched_requirement_names": clean(row.get("unmatched_requirement_names")),
                "candidate_receipt_status": clean(row.get("candidate_receipt_status")),
                "package_review_status": review_status,
                "intake_decision": decision,
                "copy_target_folder": target,
                "copy_command_hint": f"After provenance approval only: Copy-Item -Recurse -LiteralPath '{folder}' -Destination '{target}'",
                "post_copy_validation_command": clean(row.get("post_copy_validation_command")),
                "data_write_gate_status": "blocked_no_data_write",
                "modeling_gate_status": "blocked",
            }
        )

    intake_rows.sort(key=lambda row: (safe_int(row.get("intake_rank"), 99), safe_int(row.get("download_priority_order"), 999)))
    doc_rows.sort(key=lambda row: (safe_int(row.get("intake_rank"), 99), clean(row.get("idno")), clean(row.get("document_relative_path"))))

    selected_rows = [row for row in intake_rows if row.get("locked_download_target") == "1"]
    ready_rows = [row for row in intake_rows if row.get("intake_decision") == "copy_review_ready_pending_official_provenance"]
    selected_partial_rows = [row for row in selected_rows if row.get("intake_decision") == "selected_partial_intake_review_required"]
    backup_rows = [row for row in intake_rows if row.get("locked_download_target") != "1"]
    summary = [
        {"metric": "external_local_raw_intake_review_rows", "value": str(len(intake_rows)), "interpretation": "External local candidate folders with expected-file matches promoted from discovery into intake review."},
        {"metric": "external_local_raw_intake_selected_review_rows", "value": str(len(selected_rows)), "interpretation": "Currently selected refocused-plan rows with external local candidate matches."},
        {"metric": "external_local_raw_intake_copy_review_ready_rows", "value": str(len(ready_rows)), "interpretation": "Selected rows ready for human official-provenance review before copying into temp/raw_downloads."},
        {"metric": "external_local_raw_intake_selected_partial_review_rows", "value": str(len(selected_partial_rows)), "interpretation": "Selected rows with partial external local matches needing missing-file or provenance triage."},
        {"metric": "external_local_raw_intake_backup_review_rows", "value": str(len(backup_rows)), "interpretation": "Backup rows with external local matches held behind the selected batch."},
        {"metric": "external_local_raw_intake_document_manifest_rows", "value": str(len(doc_rows)), "interpretation": "Documentation files found in external local candidate folders."},
        {"metric": "external_local_raw_intake_questionnaire_document_rows", "value": str(sum(1 for row in doc_rows if row.get("document_evidence_role") == "questionnaire_or_household_interview_document")), "interpretation": "Documentation files whose filename suggests questionnaire or interview evidence."},
        {"metric": "external_local_raw_intake_provenance_accepted_rows", "value": "0", "interpretation": "External local folders accepted as official raw receipt; remains zero until official-source and unchanged-package review passes."},
        {"metric": "external_local_raw_intake_immediate_copy_rows", "value": "0", "interpretation": "Rows copied automatically by this script; must remain zero."},
        {"metric": "data_write_gate_status", "value": "blocked_no_data_write", "interpretation": "This intake decision writes no promoted data and copies no raw files."},
        {"metric": "modeling_gate_status", "value": "blocked", "interpretation": "No predictive, reduced-form, causal ML, or policy learning is opened."},
    ]
    return intake_rows, doc_rows, summary


def markdown_table(rows: list[dict[str, str]], columns: list[str], limit: int = 30) -> str:
    if not rows:
        return "_No rows._"
    lines = ["| " + " | ".join(columns) + " |", "| " + " | ".join("---" for _ in columns) + " |"]
    for row in rows[:limit]:
        values: list[str] = []
        for column in columns:
            value = clean(row.get(column)).replace("|", "/")
            if len(value) > 120:
                value = value[:117] + "..."
            values.append(value)
        lines.append("| " + " | ".join(values) + " |")
    if len(rows) > limit:
        lines.append("| ... | ... | ... | ... | ... | ... | ... |")
    return "\n".join(lines)


def write_report(intake_rows: list[dict[str, str]], doc_rows: list[dict[str, str]], summary: list[dict[str, str]]) -> None:
    lines = [
        "# Priority LSMS/ISA External Local Raw Intake Decision",
        "",
        "Status: intake decision layer for external local raw-folder candidates. It turns the filename discovery audit into a concrete review queue, but still does not accept provenance, copy raw files, write `data/`, or open modeling.",
        "",
        "## Summary",
        "",
        markdown_table(summary, ["metric", "value", "interpretation"], limit=20),
        "",
        "## Intake Queue",
        "",
        markdown_table(
            intake_rows,
            [
                "intake_rank",
                "country",
                "wave",
                "idno",
                "locked_download_target",
                "documentation_file_rows",
                "external_expected_file_match_rows",
                "expected_file_rows",
                "external_core_file_match_rows",
                "core_file_rows",
                "intake_decision",
            ],
            limit=20,
        ),
        "",
        "## Documentation Evidence",
        "",
        markdown_table(
            doc_rows,
            [
                "country",
                "wave",
                "idno",
                "document_file_name",
                "document_evidence_role",
                "document_bytes",
            ],
            limit=30,
        ),
        "",
        "## Operational Rule",
        "",
        "Rows marked `copy_review_ready_pending_official_provenance` are the next practical acquisition targets. A human/source review still has to confirm that the external local folder is an unchanged official package before copying it into `temp/raw_downloads/` and running the existing post-download validation command.",
        "",
        "The current accepted-provenance count is intentionally zero. This prevents accidental promotion from local filename matches alone.",
    ]
    REPORT_PATH.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    ensure_dirs()
    intake_rows, doc_rows, summary = build_outputs()
    write_csv(INTAKE_PATH, intake_rows, INTAKE_COLUMNS)
    write_csv(DOC_MANIFEST_PATH, doc_rows, DOC_COLUMNS)
    write_csv(SUMMARY_PATH, summary, SUMMARY_COLUMNS)
    write_report(intake_rows, doc_rows, summary)
    append_log(REPORT_DIR.parent / "temp" / "audit_log.md", f"Built priority LSMS/ISA external local raw intake decision: review_rows={len(intake_rows)} doc_rows={len(doc_rows)}.")
    print(f"Priority LSMS/ISA external local raw intake decision rows={len(intake_rows)} doc_rows={len(doc_rows)}.")


if __name__ == "__main__":
    main()
