from __future__ import annotations

import csv
import tarfile
import zipfile
from collections import Counter
from pathlib import Path
from typing import Any

from common import PROJECT_ROOT, REPORT_DIR, RESULT_DIR, TEMP_DIR, append_log, ensure_dirs, write_csv


QUEUE_PATH = TEMP_DIR / "priority_lsms_isa_refocused_acquisition_queue.csv"
INTAKE_LEDGER_PATH = TEMP_DIR / "priority_lsms_isa_raw_package_intake_ledger.csv"
FILE_MANIFEST_PATH = TEMP_DIR / "priority_lsms_isa_raw_package_file_manifest.csv"
REQUIREMENT_MATRIX_PATH = TEMP_DIR / "priority_lsms_isa_refocused_requirement_matrix.csv"

PREFLIGHT_PATH = TEMP_DIR / "priority_lsms_isa_archive_member_preflight.csv"
ARCHIVE_MEMBER_PATH = TEMP_DIR / "priority_lsms_isa_archive_member_manifest.csv"
DIRECT_FILE_PATH = TEMP_DIR / "priority_lsms_isa_direct_file_preflight.csv"
REQUIREMENT_PREFLIGHT_PATH = TEMP_DIR / "priority_lsms_isa_archive_requirement_preflight.csv"
SUMMARY_PATH = RESULT_DIR / "priority_lsms_isa_archive_member_preflight_summary.csv"
REPORT_PATH = REPORT_DIR / "priority_lsms_isa_archive_member_preflight.md"

RAW_ROOT = TEMP_DIR / "raw_downloads"

RAW_TABULAR_EXTENSIONS = {".dta", ".sav", ".por", ".sas7bdat", ".xpt", ".csv", ".tsv", ".xlsx", ".xls"}
ARCHIVE_EXTENSIONS = {".zip", ".tar", ".tgz", ".gz"}
DOCUMENTATION_EXTENSIONS = {".pdf", ".doc", ".docx", ".rtf", ".html", ".htm", ".xml", ".json", ".ddi", ".txt", ".md"}

PREFLIGHT_COLUMNS = [
    "download_priority_order",
    "queue_role",
    "country",
    "wave",
    "idno",
    "survey_name",
    "local_target_folder",
    "intake_raw_package_status",
    "direct_original_file_rows",
    "direct_archive_file_rows",
    "direct_raw_tabular_file_rows",
    "direct_documentation_file_rows",
    "archive_member_rows",
    "archive_raw_tabular_member_rows",
    "archive_documentation_member_rows",
    "readable_archive_rows",
    "unreadable_archive_rows",
    "archive_preflight_status",
    "next_action",
    "handoff_readme",
]

ARCHIVE_MEMBER_COLUMNS = [
    "download_priority_order",
    "country",
    "wave",
    "idno",
    "archive_relative_path",
    "archive_file_name",
    "archive_read_status",
    "member_name",
    "member_suffix",
    "member_size",
    "member_role",
    "member_acceptance_status",
]

DIRECT_FILE_COLUMNS = [
    "download_priority_order",
    "country",
    "wave",
    "idno",
    "relative_path",
    "file_name",
    "suffix",
    "bytes",
    "file_role",
    "direct_file_acceptance_status",
]

REQUIREMENT_COLUMNS = [
    "download_priority_order",
    "queue_role",
    "country",
    "wave",
    "idno",
    "requirement",
    "metadata_status",
    "current_archive_preflight_status",
    "requirement_preflight_status",
    "required_next_evidence",
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


def folder_for(row: dict[str, str]) -> Path:
    folder = clean(row.get("local_target_folder")).replace("\\", "/").strip("/")
    if folder.startswith("temp/raw_downloads/"):
        return PROJECT_ROOT / folder
    if folder:
        return PROJECT_ROOT / folder
    return RAW_ROOT / clean(row.get("idno"))


def path_from_relative(relative_path: str) -> Path:
    return PROJECT_ROOT / clean(relative_path).replace("/", "\\")


def suffix_from_name(name: str) -> str:
    return Path(name).suffix.lower()


def role_from_suffix(name: str) -> str:
    suffix = suffix_from_name(name)
    lower = name.lower()
    if suffix in RAW_TABULAR_EXTENSIONS:
        if any(token in lower for token in ["questionnaire", "codebook", "dictionary", "basic", "manual", "readme"]):
            return "documentation_candidate"
        return "raw_tabular_candidate"
    if suffix in DOCUMENTATION_EXTENSIONS:
        return "documentation_candidate"
    if suffix in ARCHIVE_EXTENSIONS:
        return "nested_archive_candidate"
    return "other_member_candidate"


def is_archive_path(path: Path) -> bool:
    lower = path.name.lower()
    return path.suffix.lower() in ARCHIVE_EXTENSIONS or lower.endswith(".tar.gz")


def archive_members(path: Path) -> tuple[str, list[dict[str, str]]]:
    rows: list[dict[str, str]] = []
    try:
        if zipfile.is_zipfile(path):
            with zipfile.ZipFile(path) as zf:
                for info in zf.infolist():
                    if info.is_dir():
                        continue
                    member = info.filename
                    rows.append(
                        {
                            "member_name": member,
                            "member_suffix": suffix_from_name(member),
                            "member_size": str(info.file_size),
                            "member_role": role_from_suffix(member),
                        }
                    )
            return "readable_zip", rows
        if tarfile.is_tarfile(path):
            with tarfile.open(path) as tf:
                for info in tf.getmembers():
                    if not info.isfile():
                        continue
                    member = info.name
                    rows.append(
                        {
                            "member_name": member,
                            "member_suffix": suffix_from_name(member),
                            "member_size": str(info.size),
                            "member_role": role_from_suffix(member),
                        }
                    )
            return "readable_tar", rows
        return "unsupported_or_unreadable_archive", rows
    except (OSError, tarfile.TarError, zipfile.BadZipFile, RuntimeError):
        return "unsupported_or_unreadable_archive", []


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


def write_handoff(preflight_row: dict[str, str], requirement_rows: list[dict[str, str]], member_rows: list[dict[str, str]]) -> str:
    folder = folder_for(preflight_row)
    folder.mkdir(parents=True, exist_ok=True)
    path = folder / "_PRIORITY_LSMS_ISA_ARCHIVE_PREFLIGHT.md"
    path.write_text(
        f"""# Priority LSMS-ISA Archive Member Preflight

Dataset: `{preflight_row.get('idno', '')}` - {preflight_row.get('country', '')} {preflight_row.get('wave', '')}

Current status: `{preflight_row.get('archive_preflight_status', '')}`

Target folder: `{preflight_row.get('local_target_folder', '')}`

Direct archives: {preflight_row.get('direct_archive_file_rows', '0')}

Archive members: {preflight_row.get('archive_member_rows', '0')}

Raw tabular members: {preflight_row.get('archive_raw_tabular_member_rows', '0')}

Documentation members: {preflight_row.get('archive_documentation_member_rows', '0')}

## Requirement Preflight

{markdown_table(requirement_rows, ['requirement', 'metadata_status', 'requirement_preflight_status'], 12)}

## Archive Member Preview

{markdown_table(member_rows, ['archive_file_name', 'member_name', 'member_role', 'member_acceptance_status'], 20) if member_rows else 'No archive members were readable.'}

## Next Action

{preflight_row.get('next_action', '')}
""",
        encoding="utf-8",
    )
    return rel(path)


def build_direct_and_members(queue_rows: list[dict[str, str]], manifest_rows: list[dict[str, str]]) -> tuple[list[dict[str, str]], list[dict[str, str]]]:
    queue_by_id = {clean(row.get("idno")): row for row in queue_rows}
    direct_rows: list[dict[str, str]] = []
    member_rows: list[dict[str, str]] = []
    originals = [row for row in manifest_rows if row.get("generated_or_original") == "original_candidate"]
    for row in originals:
        idno = clean(row.get("idno"))
        queue = queue_by_id.get(idno, {})
        direct_status = "direct_file_present_pending_schema_or_documentation_review"
        direct_rows.append(
            {
                "download_priority_order": clean(row.get("download_priority_order")),
                "country": clean(row.get("country")),
                "wave": clean(row.get("wave")),
                "idno": idno,
                "relative_path": clean(row.get("relative_path")),
                "file_name": clean(row.get("file_name")),
                "suffix": clean(row.get("suffix")),
                "bytes": clean(row.get("bytes")),
                "file_role": clean(row.get("file_role")),
                "direct_file_acceptance_status": direct_status,
            }
        )
        path = path_from_relative(row.get("relative_path", ""))
        if clean(row.get("file_role")) == "official_archive_or_compressed_package_candidate" or is_archive_path(path):
            archive_status, members = archive_members(path)
            if not members:
                member_rows.append(
                    {
                        "download_priority_order": clean(queue.get("download_priority_order")) or clean(row.get("download_priority_order")),
                        "country": clean(row.get("country")),
                        "wave": clean(row.get("wave")),
                        "idno": idno,
                        "archive_relative_path": clean(row.get("relative_path")),
                        "archive_file_name": clean(row.get("file_name")),
                        "archive_read_status": archive_status,
                        "member_name": "",
                        "member_suffix": "",
                        "member_size": "",
                        "member_role": "",
                        "member_acceptance_status": "blocked_archive_unreadable_or_no_members",
                    }
                )
            for member in members:
                role = member["member_role"]
                status = "archive_member_candidate_pending_schema_or_documentation_review"
                if role == "other_member_candidate":
                    status = "archive_member_present_role_unclear"
                member_rows.append(
                    {
                        "download_priority_order": clean(queue.get("download_priority_order")) or clean(row.get("download_priority_order")),
                        "country": clean(row.get("country")),
                        "wave": clean(row.get("wave")),
                        "idno": idno,
                        "archive_relative_path": clean(row.get("relative_path")),
                        "archive_file_name": clean(row.get("file_name")),
                        "archive_read_status": archive_status,
                        "member_name": clean(member.get("member_name")),
                        "member_suffix": clean(member.get("member_suffix")),
                        "member_size": clean(member.get("member_size")),
                        "member_role": role,
                        "member_acceptance_status": status,
                    }
                )
    return direct_rows, member_rows


def preflight_status(direct_archive: int, direct_raw: int, direct_doc: int, member_raw: int, member_doc: int, unreadable_archives: int) -> tuple[str, str]:
    if direct_archive == 0 and direct_raw == 0 and direct_doc == 0 and member_raw == 0 and member_doc == 0:
        return "blocked_no_original_archive_or_direct_files", "Place the complete official archive/raw package and documentation in the target folder."
    if direct_archive > 0 and unreadable_archives >= direct_archive and member_raw == 0 and member_doc == 0:
        return "blocked_archive_present_but_unreadable_by_preflight", "Use a readable zip/tar package or manually list/archive-extract contents for schema inspection."
    if direct_raw + member_raw == 0:
        return "blocked_no_raw_tabular_candidate", "Confirm the official package contains raw Stata/SPSS/SAS/CSV/workbook files."
    if direct_doc + member_doc == 0:
        return "blocked_no_documentation_candidate", "Add or locate questionnaires, codebooks, basic information documents, and data dictionaries."
    return "ready_for_raw_receipt_schema_and_manual_review", "Run schema inspection and raw value/unit/key review before promotion."


def build_preflight(
    queue_rows: list[dict[str, str]],
    ledger_rows: list[dict[str, str]],
    direct_rows: list[dict[str, str]],
    member_rows: list[dict[str, str]],
) -> list[dict[str, str]]:
    ledger_by_id = {clean(row.get("idno")): row for row in ledger_rows}
    by_direct: dict[str, list[dict[str, str]]] = {}
    by_member: dict[str, list[dict[str, str]]] = {}
    for row in direct_rows:
        by_direct.setdefault(clean(row.get("idno")), []).append(row)
    for row in member_rows:
        by_member.setdefault(clean(row.get("idno")), []).append(row)
    rows: list[dict[str, str]] = []
    for queue in queue_rows:
        idno = clean(queue.get("idno"))
        direct = by_direct.get(idno, [])
        members = by_member.get(idno, [])
        direct_archive = sum(1 for row in direct if row.get("file_role") == "official_archive_or_compressed_package_candidate")
        direct_raw = sum(1 for row in direct if row.get("file_role") == "raw_tabular_or_workbook_candidate")
        direct_doc = sum(1 for row in direct if row.get("file_role") == "documentation_candidate")
        member_raw = sum(1 for row in members if row.get("member_role") == "raw_tabular_candidate")
        member_doc = sum(1 for row in members if row.get("member_role") == "documentation_candidate")
        readable_archive_names = {row["archive_file_name"] for row in members if clean(row.get("archive_read_status")).startswith("readable")}
        unreadable_archive_names = {row["archive_file_name"] for row in members if clean(row.get("archive_read_status")).startswith("unsupported")}
        status, next_action = preflight_status(direct_archive, direct_raw, direct_doc, member_raw, member_doc, len(unreadable_archive_names))
        rows.append(
            {
                "download_priority_order": clean(queue.get("download_priority_order")),
                "queue_role": clean(queue.get("queue_role")),
                "country": clean(queue.get("country")),
                "wave": clean(queue.get("wave")),
                "idno": idno,
                "survey_name": clean(queue.get("survey_name")),
                "local_target_folder": clean(queue.get("local_target_folder")),
                "intake_raw_package_status": clean(ledger_by_id.get(idno, {}).get("raw_package_status")) or "missing_intake_ledger",
                "direct_original_file_rows": str(len(direct)),
                "direct_archive_file_rows": str(direct_archive),
                "direct_raw_tabular_file_rows": str(direct_raw),
                "direct_documentation_file_rows": str(direct_doc),
                "archive_member_rows": str(len([row for row in members if row.get("member_name")])),
                "archive_raw_tabular_member_rows": str(member_raw),
                "archive_documentation_member_rows": str(member_doc),
                "readable_archive_rows": str(len(readable_archive_names)),
                "unreadable_archive_rows": str(len(unreadable_archive_names)),
                "archive_preflight_status": status,
                "next_action": next_action,
                "handoff_readme": "",
            }
        )
    return rows


def build_requirement_preflight(preflight_rows: list[dict[str, str]], requirement_rows: list[dict[str, str]]) -> list[dict[str, str]]:
    preflight_by_id = {clean(row.get("idno")): row for row in preflight_rows}
    rows: list[dict[str, str]] = []
    for requirement in requirement_rows:
        idno = clean(requirement.get("idno"))
        preflight = preflight_by_id.get(idno, {})
        status = clean(preflight.get("archive_preflight_status")) or "missing_archive_preflight"
        if status == "ready_for_raw_receipt_schema_and_manual_review":
            requirement_status = "ready_for_schema_and_manual_requirement_review"
        else:
            requirement_status = "blocked_no_archive_or_direct_raw_evidence"
        rows.append(
            {
                "download_priority_order": clean(requirement.get("download_priority_order")),
                "queue_role": clean(requirement.get("queue_role")),
                "country": clean(requirement.get("country")),
                "wave": clean(requirement.get("wave")),
                "idno": idno,
                "requirement": clean(requirement.get("requirement")),
                "metadata_status": clean(requirement.get("metadata_status")),
                "current_archive_preflight_status": status,
                "requirement_preflight_status": requirement_status,
                "required_next_evidence": "Readable archive/direct raw file plus documentation, followed by schema inspection and manual value/unit/key review.",
            }
        )
    return rows


def build_summary(preflight_rows: list[dict[str, str]], direct_rows: list[dict[str, str]], member_rows: list[dict[str, str]], requirement_rows: list[dict[str, str]]) -> list[dict[str, str]]:
    status_counts = Counter(row["archive_preflight_status"] for row in preflight_rows)
    req_counts = Counter(row["requirement_preflight_status"] for row in requirement_rows)
    role_counts = Counter(row["queue_role"] for row in preflight_rows)
    rows = [
        {"metric": "priority_lsms_archive_preflight_dataset_rows", "value": str(len(preflight_rows)), "interpretation": "Refocused LSMS/ISA targets checked by archive/direct-file preflight."},
        {"metric": "priority_lsms_archive_preflight_direct_file_rows", "value": str(len(direct_rows)), "interpretation": "Direct non-generated original candidate files found under target folders."},
        {"metric": "priority_lsms_archive_preflight_direct_archive_rows", "value": str(sum(1 for row in direct_rows if row.get("file_role") == "official_archive_or_compressed_package_candidate")), "interpretation": "Direct archive/compressed package candidates found."},
        {"metric": "priority_lsms_archive_preflight_direct_raw_tabular_rows", "value": str(sum(1 for row in direct_rows if row.get("file_role") == "raw_tabular_or_workbook_candidate")), "interpretation": "Direct raw tabular/workbook candidates found."},
        {"metric": "priority_lsms_archive_preflight_direct_documentation_rows", "value": str(sum(1 for row in direct_rows if row.get("file_role") == "documentation_candidate")), "interpretation": "Direct documentation candidates found."},
        {"metric": "priority_lsms_archive_preflight_archive_member_rows", "value": str(sum(1 for row in member_rows if row.get("member_name"))), "interpretation": "Readable archive member rows found without extraction."},
        {"metric": "priority_lsms_archive_preflight_archive_raw_tabular_member_rows", "value": str(sum(1 for row in member_rows if row.get("member_role") == "raw_tabular_candidate")), "interpretation": "Raw tabular-like archive members found."},
        {"metric": "priority_lsms_archive_preflight_archive_documentation_member_rows", "value": str(sum(1 for row in member_rows if row.get("member_role") == "documentation_candidate")), "interpretation": "Documentation-like archive members found."},
        {"metric": "priority_lsms_archive_preflight_ready_dataset_rows", "value": str(status_counts.get("ready_for_raw_receipt_schema_and_manual_review", 0)), "interpretation": "Targets ready for schema and manual raw review."},
        {"metric": "priority_lsms_archive_preflight_blocked_dataset_rows", "value": str(len(preflight_rows) - status_counts.get("ready_for_raw_receipt_schema_and_manual_review", 0)), "interpretation": "Targets still blocked before schema/manual raw review."},
        {"metric": "priority_lsms_archive_preflight_requirement_rows", "value": str(len(requirement_rows)), "interpretation": "Requirement rows covered by archive/direct-file preflight."},
        {"metric": "priority_lsms_archive_preflight_blocked_requirement_rows", "value": str(req_counts.get("blocked_no_archive_or_direct_raw_evidence", 0)), "interpretation": "Requirement rows blocked because no archive/direct raw evidence is available."},
        {"metric": "priority_lsms_archive_preflight_handoff_readmes_written", "value": str(sum(1 for row in preflight_rows if row.get("handoff_readme"))), "interpretation": "Per-target archive preflight handoff files written."},
        {"metric": "priority_lsms_archive_preflight_data_write_status", "value": "blocked_no_promoted_rows", "interpretation": "No country-wave may write to data/ from archive preflight alone."},
        {"metric": "modeling_gate_status", "value": "blocked", "interpretation": "Models remain blocked until raw-backed promotion thresholds and accepted climate linkage pass."},
    ]
    for role, count in sorted(role_counts.items()):
        rows.append({"metric": f"priority_lsms_archive_preflight_queue_role_{role}", "value": str(count), "interpretation": "Archive preflight target count by refocused queue role."})
    for state, count in sorted(status_counts.items()):
        rows.append({"metric": f"priority_lsms_archive_preflight_status_{state}", "value": str(count), "interpretation": "Archive preflight dataset status count."})
    return rows


def write_report(preflight_rows: list[dict[str, str]], direct_rows: list[dict[str, str]], member_rows: list[dict[str, str]], requirement_rows: list[dict[str, str]], summary_rows: list[dict[str, str]]) -> None:
    blocked = [row for row in preflight_rows if row["archive_preflight_status"] != "ready_for_raw_receipt_schema_and_manual_review"]
    summary_table = "\n".join(f"| {row['metric']} | {row['value']} | {row['interpretation']} |" for row in summary_rows)
    REPORT_PATH.write_text(
        f"""# Priority LSMS-ISA Archive Member Preflight

Status: archive/direct-file preflight for the refocused LSMS/ISA raw package
targets. This script does not extract, convert, or promote data; it only checks
whether direct original files or readable archive members exist.

## Summary

| Metric | Value | Interpretation |
|---|---:|---|
{summary_table}

## Dataset Preflight

{markdown_table(preflight_rows, ['download_priority_order', 'queue_role', 'country', 'wave', 'idno', 'direct_archive_file_rows', 'archive_member_rows', 'archive_preflight_status'], 25)}

## Blocked Targets

{markdown_table(blocked, ['download_priority_order', 'country', 'idno', 'local_target_folder', 'archive_preflight_status', 'next_action'], 25) if blocked else 'No blocked targets were found.'}

## Direct File Preview

{markdown_table(direct_rows, ['download_priority_order', 'idno', 'file_name', 'file_role', 'direct_file_acceptance_status'], 20) if direct_rows else 'No non-generated direct files were found.'}

## Archive Member Preview

{markdown_table(member_rows, ['download_priority_order', 'idno', 'archive_file_name', 'member_name', 'member_role', 'member_acceptance_status'], 20) if member_rows else 'No readable archive members were found.'}

## Machine-Readable Outputs

- `temp/priority_lsms_isa_archive_member_preflight.csv`
- `temp/priority_lsms_isa_archive_member_manifest.csv`
- `temp/priority_lsms_isa_direct_file_preflight.csv`
- `temp/priority_lsms_isa_archive_requirement_preflight.csv`
- `result/priority_lsms_isa_archive_member_preflight_summary.csv`

## Guardrail

Readable archive members or direct raw files are only preflight evidence. A wave
still cannot enter `data/` until raw schema inspection, manual value/unit/key
review, outcome readiness, and accepted CHIRPS/ERA5 linkage all pass.
""",
        encoding="utf-8",
    )


def main() -> None:
    ensure_dirs()
    queue_rows = read_csv_dicts(QUEUE_PATH)
    ledger_rows = read_csv_dicts(INTAKE_LEDGER_PATH)
    manifest_rows = read_csv_dicts(FILE_MANIFEST_PATH)
    requirement_rows = read_csv_dicts(REQUIREMENT_MATRIX_PATH)
    direct_rows, member_rows = build_direct_and_members(queue_rows, manifest_rows)
    preflight_rows = build_preflight(queue_rows, ledger_rows, direct_rows, member_rows)
    requirement_preflight_rows = build_requirement_preflight(preflight_rows, requirement_rows)
    by_id_req: dict[str, list[dict[str, str]]] = {}
    by_id_member: dict[str, list[dict[str, str]]] = {}
    for row in requirement_preflight_rows:
        by_id_req.setdefault(clean(row.get("idno")), []).append(row)
    for row in member_rows:
        by_id_member.setdefault(clean(row.get("idno")), []).append(row)
    for row in preflight_rows:
        row["handoff_readme"] = write_handoff(row, by_id_req.get(clean(row.get("idno")), []), by_id_member.get(clean(row.get("idno")), []))
    summary_rows = build_summary(preflight_rows, direct_rows, member_rows, requirement_preflight_rows)
    write_csv(PREFLIGHT_PATH, preflight_rows, PREFLIGHT_COLUMNS)
    write_csv(ARCHIVE_MEMBER_PATH, member_rows, ARCHIVE_MEMBER_COLUMNS)
    write_csv(DIRECT_FILE_PATH, direct_rows, DIRECT_FILE_COLUMNS)
    write_csv(REQUIREMENT_PREFLIGHT_PATH, requirement_preflight_rows, REQUIREMENT_COLUMNS)
    write_csv(SUMMARY_PATH, summary_rows, SUMMARY_COLUMNS)
    write_report(preflight_rows, direct_rows, member_rows, requirement_preflight_rows, summary_rows)
    append_log(
        TEMP_DIR / "audit_log.md",
        f"Built priority LSMS-ISA archive member preflight datasets={len(preflight_rows)} direct_files={len(direct_rows)} archive_members={len(member_rows)}.",
    )
    print(f"Priority LSMS-ISA archive preflight rows={len(preflight_rows)} archive_member_rows={len(member_rows)}.")


if __name__ == "__main__":
    main()
