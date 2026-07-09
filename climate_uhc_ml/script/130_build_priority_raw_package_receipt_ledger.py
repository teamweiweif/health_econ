from __future__ import annotations

import csv
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

from common import PROJECT_ROOT, REPORT_DIR, RESULT_DIR, TEMP_DIR, append_log, ensure_dirs, sha256_file, write_csv


WAVE_PLAN_PATH = RESULT_DIR / "priority_promotion_acquisition_wave_plan.csv"
INTAKE_GATE_PATH = TEMP_DIR / "priority_raw_intake_gate.csv"
ARCHIVE_COMPLETENESS_PATH = TEMP_DIR / "priority_archive_completeness_matrix.csv"
MANUAL_DECISION_PATH = TEMP_DIR / "priority_manual_verification_decision_gate.csv"
ACCESS_PROBE_PATH = TEMP_DIR / "priority_official_raw_access_probe.csv"

LEDGER_PATH = TEMP_DIR / "priority_raw_package_receipt_ledger.csv"
FILE_MANIFEST_PATH = TEMP_DIR / "priority_raw_package_file_manifest.csv"
MISSING_TARGETS_PATH = TEMP_DIR / "priority_raw_package_missing_targets.csv"
SUMMARY_PATH = RESULT_DIR / "priority_raw_package_receipt_summary.csv"
REPORT_PATH = REPORT_DIR / "priority_raw_package_receipt_ledger.md"

RAW_ROOT = TEMP_DIR / "raw_downloads"

RAW_SUFFIXES = {".dta", ".sav", ".por", ".sas7bdat", ".xpt", ".csv", ".tsv", ".txt", ".xlsx", ".xls", ".parquet", ".feather"}
ARCHIVE_SUFFIXES = {".zip", ".tar", ".tgz", ".gz", ".bz2", ".xz", ".7z", ".rar", ".tar.gz", ".tar.bz2", ".tar.xz"}
DOCUMENTATION_SUFFIXES = {".pdf", ".doc", ".docx", ".rtf", ".html", ".htm", ".xml", ".json"}
GENERATED_PREFIXES = {"_PLACE_RAW_FILES_HERE", "_PRIORITY_"}

POST_RECEIPT_COMMANDS = [
    "python script/17_audit_raw_downloads.py",
    "python script/128_build_priority_archive_member_preflight.py",
    "python script/03_inspect_raw_schemas.py",
    "python script/29_build_raw_variable_verification_protocol.py",
    "python script/33_build_harmonization_recipe_gate.py",
    "python script/125_build_priority_climate_linkage_preflight.py",
    "python script/126_build_priority_raw_verification_workbook.py",
    "python script/140_build_priority_first_pass_variable_review_queue.py",
    "python script/141_build_priority_download_execution_packet.py",
    "python script/129_build_priority_manual_verification_decision_gate.py",
    "python script/130_build_priority_raw_package_receipt_ledger.py",
    "python script/127_enforce_promoted_data_gate.py",
    "python script/36_build_direct_read_audit_bundle.py",
    "python script/14_validate_workspace.py",
]

LEDGER_COLUMNS = [
    "acquisition_batch_rank",
    "batch_role",
    "country",
    "wave",
    "idno",
    "survey_name",
    "official_url",
    "local_target_folder",
    "access_gate_detected",
    "direct_raw_route_status",
    "manual_action_status",
    "folder_exists",
    "original_file_count",
    "ignored_generated_file_count",
    "archive_file_count",
    "raw_tabular_file_count",
    "documentation_file_count",
    "other_original_file_count",
    "total_original_bytes",
    "priority_file_targets",
    "priority_targets_covered_direct_or_archive",
    "priority_targets_missing",
    "required_concepts_unverified",
    "manual_verification_status",
    "receipt_status",
    "next_action",
    "post_receipt_commands",
    "promotion_stop_rule",
    "handoff_readme",
]

FILE_COLUMNS = [
    "acquisition_batch_rank",
    "batch_role",
    "country",
    "wave",
    "idno",
    "relative_path",
    "file_name",
    "extension",
    "file_role",
    "file_size_bytes",
    "sha256",
    "receipt_note",
]

MISSING_COLUMNS = [
    "acquisition_batch_rank",
    "batch_role",
    "country",
    "wave",
    "idno",
    "file_rank",
    "expected_file_name",
    "coverage_status",
    "verification_action",
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
        text = str(value).strip()
        return int(float(text)) if text else default
    except (TypeError, ValueError):
        return default


def rel(path: Path) -> str:
    try:
        return str(path.relative_to(PROJECT_ROOT)).replace("\\", "/")
    except ValueError:
        return str(path).replace("\\", "/")


def compact(values: list[str], limit: int = 12) -> str:
    out: list[str] = []
    seen: set[str] = set()
    for value in values:
        item = " ".join(clean(value).split())
        if item and item not in seen:
            out.append(item)
            seen.add(item)
        if len(out) >= limit:
            break
    return "; ".join(out)


def first_by(rows: list[dict[str, str]], field: str) -> dict[str, dict[str, str]]:
    out: dict[str, dict[str, str]] = {}
    for row in rows:
        key = clean(row.get(field))
        if key and key not in out:
            out[key] = row
    return out


def group(rows: list[dict[str, str]], field: str) -> dict[str, list[dict[str, str]]]:
    out: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in rows:
        key = clean(row.get(field))
        if key:
            out[key].append(row)
    return out


def target_folder_path(folder: str, idno: str) -> Path:
    folder_clean = clean(folder).replace("\\", "/").strip("/")
    if folder_clean.startswith("temp/raw_downloads/"):
        return PROJECT_ROOT / folder_clean
    if folder_clean:
        return RAW_ROOT / folder_clean
    return RAW_ROOT / idno


def compound_suffix(path: Path) -> str:
    lower = path.name.lower()
    for suffix in [".tar.gz", ".tar.bz2", ".tar.xz"]:
        if lower.endswith(suffix):
            return suffix
    return path.suffix.lower()


def is_generated_handoff(path: Path) -> bool:
    name = path.name
    return name.lower().startswith("readme") or any(name.startswith(prefix) for prefix in GENERATED_PREFIXES)


def file_role(path: Path) -> str:
    suffix = compound_suffix(path)
    if suffix in ARCHIVE_SUFFIXES:
        return "archive_package"
    if suffix in RAW_SUFFIXES:
        return "raw_tabular_file"
    if suffix in DOCUMENTATION_SUFFIXES:
        return "documentation_or_metadata"
    return "other_original_file"


def current_files(folder: Path) -> tuple[list[Path], list[Path]]:
    if not folder.exists():
        return [], []
    files = [path for path in sorted(folder.rglob("*")) if path.is_file()]
    generated = [path for path in files if is_generated_handoff(path)]
    original = [path for path in files if not is_generated_handoff(path)]
    return original, generated


def coverage_counts(rows: list[dict[str, str]]) -> tuple[int, int, int]:
    total = len(rows)
    covered = 0
    missing = 0
    for row in rows:
        status = clean(row.get("coverage_status"))
        if status in {"covered_by_direct_file", "covered_by_archive_member", "covered_by_direct_and_archive"}:
            covered += 1
        else:
            missing += 1
    return total, covered, missing


def receipt_status(archive_count: int, raw_count: int, doc_count: int, missing_targets: int) -> str:
    if archive_count + raw_count == 0:
        return "not_received_no_original_raw_package"
    if missing_targets == 0 and doc_count > 0:
        return "complete_raw_package_candidate_ready_for_schema_and_manual_audit"
    if missing_targets == 0:
        return "raw_targets_covered_documentation_review_needed"
    return "partial_raw_package_candidate_missing_priority_targets"


def next_action(status: str, missing_targets: int) -> str:
    if status == "not_received_no_original_raw_package":
        return "Complete the official access workflow, download the unchanged raw package plus documentation, and place original files in this folder."
    if status == "partial_raw_package_candidate_missing_priority_targets":
        return f"Add or extract missing priority modules before value verification; currently missing {missing_targets} target files."
    if status == "raw_targets_covered_documentation_review_needed":
        return "Add official questionnaires, codebooks, data dictionaries, and study documentation before promotion review."
    return "Run schema inspection, archive member preflight, raw value/unit/key audits, and manual verification decision gates."


def write_handoff(row: dict[str, str], missing_rows: list[dict[str, str]]) -> str:
    folder = target_folder_path(row.get("local_target_folder", ""), row.get("idno", ""))
    folder.mkdir(parents=True, exist_ok=True)
    path = folder / "_PRIORITY_RAW_PACKAGE_RECEIPT_LEDGER.md"
    missing_names = [clean(item.get("expected_file_name")) for item in missing_rows if clean(item.get("expected_file_name"))]
    path.write_text(
        f"""# Priority Raw Package Receipt Ledger

Dataset: {row.get('idno', '')} - {row.get('country', '')} {row.get('wave', '')}

Status: {row.get('receipt_status', '')}

Official URL: {row.get('official_url', '')}

Target folder: {row.get('local_target_folder', '')}

Current evidence:

- Original files counted: {row.get('original_file_count', '0')}
- Archive packages: {row.get('archive_file_count', '0')}
- Raw tabular files: {row.get('raw_tabular_file_count', '0')}
- Documentation files: {row.get('documentation_file_count', '0')}
- Priority targets covered: {row.get('priority_targets_covered_direct_or_archive', '0')} / {row.get('priority_file_targets', '0')}
- Missing priority targets: {row.get('priority_targets_missing', '0')}
- Manual verification status: {row.get('manual_verification_status', '')}

Next action: {row.get('next_action', '')}

Missing target examples:

{chr(10).join(f'- {name}' for name in missing_names[:20]) if missing_names else '- None at current target-file level'}

Post-receipt commands:

{chr(10).join(f'- `{command}`' for command in POST_RECEIPT_COMMANDS)}

Promotion stop rule: {row.get('promotion_stop_rule', '')}
""",
        encoding="utf-8",
    )
    return rel(path)


def build_outputs() -> tuple[list[dict[str, str]], list[dict[str, str]], list[dict[str, str]], list[dict[str, str]]]:
    waves = read_csv_dicts(WAVE_PLAN_PATH)
    intake_by_id = first_by(read_csv_dicts(INTAKE_GATE_PATH), "idno")
    access_by_id = first_by(read_csv_dicts(ACCESS_PROBE_PATH), "idno")
    manual_by_id = first_by(read_csv_dicts(MANUAL_DECISION_PATH), "idno")
    completeness_by_id = group(read_csv_dicts(ARCHIVE_COMPLETENESS_PATH), "idno")

    ledger_rows: list[dict[str, str]] = []
    file_rows: list[dict[str, str]] = []
    missing_rows: list[dict[str, str]] = []

    for wave in waves:
        idno = clean(wave.get("idno"))
        folder = target_folder_path(wave.get("local_target_folder", ""), idno)
        original_files, generated_files = current_files(folder)
        role_counts = Counter(file_role(path) for path in original_files)
        total_bytes = sum(path.stat().st_size for path in original_files)
        completion_rows = completeness_by_id.get(idno, [])
        targets_total, targets_covered, targets_missing = coverage_counts(completion_rows)
        missing_for_wave = [row for row in completion_rows if clean(row.get("coverage_status")) not in {"covered_by_direct_file", "covered_by_archive_member", "covered_by_direct_and_archive"}]

        for path in original_files:
            role = file_role(path)
            file_rows.append(
                {
                    "acquisition_batch_rank": wave.get("acquisition_batch_rank", ""),
                    "batch_role": wave.get("batch_role", ""),
                    "country": wave.get("country", ""),
                    "wave": wave.get("wave", ""),
                    "idno": idno,
                    "relative_path": rel(path),
                    "file_name": path.name,
                    "extension": compound_suffix(path),
                    "file_role": role,
                    "file_size_bytes": str(path.stat().st_size),
                    "sha256": sha256_file(path),
                    "receipt_note": "Preserve unchanged original package/file; downstream promotion must cite this checksum.",
                }
            )

        for item in missing_for_wave:
            missing_rows.append(
                {
                    "acquisition_batch_rank": wave.get("acquisition_batch_rank", ""),
                    "batch_role": wave.get("batch_role", ""),
                    "country": wave.get("country", ""),
                    "wave": wave.get("wave", ""),
                    "idno": idno,
                    "file_rank": item.get("file_rank", ""),
                    "expected_file_name": item.get("expected_file_name", ""),
                    "coverage_status": item.get("coverage_status", ""),
                    "verification_action": item.get("verification_action", ""),
                }
            )

        status_value = receipt_status(
            role_counts.get("archive_package", 0),
            role_counts.get("raw_tabular_file", 0),
            role_counts.get("documentation_or_metadata", 0),
            targets_missing,
        )
        intake = intake_by_id.get(idno, {})
        access = access_by_id.get(idno, {})
        manual = manual_by_id.get(idno, {})
        dataset_row = {
            "acquisition_batch_rank": wave.get("acquisition_batch_rank", ""),
            "batch_role": wave.get("batch_role", ""),
            "country": wave.get("country", ""),
            "wave": wave.get("wave", ""),
            "idno": idno,
            "survey_name": wave.get("survey_name", ""),
            "official_url": wave.get("official_url", ""),
            "local_target_folder": rel(folder) + "/",
            "access_gate_detected": access.get("access_gate_detected", intake.get("access_gate_detected", "")),
            "direct_raw_route_status": access.get("direct_raw_route_status", intake.get("direct_raw_route_status", "")),
            "manual_action_status": access.get("manual_action_status", intake.get("manual_action_status", "")),
            "folder_exists": "1" if folder.exists() else "0",
            "original_file_count": str(len(original_files)),
            "ignored_generated_file_count": str(len(generated_files)),
            "archive_file_count": str(role_counts.get("archive_package", 0)),
            "raw_tabular_file_count": str(role_counts.get("raw_tabular_file", 0)),
            "documentation_file_count": str(role_counts.get("documentation_or_metadata", 0)),
            "other_original_file_count": str(role_counts.get("other_original_file", 0)),
            "total_original_bytes": str(total_bytes),
            "priority_file_targets": str(targets_total),
            "priority_targets_covered_direct_or_archive": str(targets_covered),
            "priority_targets_missing": str(targets_missing),
            "required_concepts_unverified": intake.get("required_concepts_unverified", ""),
            "manual_verification_status": manual.get("manual_verification_status", "missing_manual_decision_gate"),
            "receipt_status": status_value,
            "next_action": next_action(status_value, targets_missing),
            "post_receipt_commands": "; ".join(POST_RECEIPT_COMMANDS),
            "promotion_stop_rule": "Do not write this wave into data/ until original package receipt, raw target coverage, manual value/unit/key review, and CHIRPS/ERA5 linkage gates pass.",
            "handoff_readme": "",
        }
        dataset_row["handoff_readme"] = write_handoff(dataset_row, missing_for_wave)
        ledger_rows.append(dataset_row)

    return ledger_rows, file_rows, missing_rows, build_summary(ledger_rows, file_rows, missing_rows)


def build_summary(
    ledger_rows: list[dict[str, str]],
    file_rows: list[dict[str, str]],
    missing_rows: list[dict[str, str]],
) -> list[dict[str, str]]:
    receipt_counts = Counter(row.get("receipt_status", "") for row in ledger_rows)
    file_role_counts = Counter(row.get("file_role", "") for row in file_rows)
    rows = [
        {"metric": "priority_raw_receipt_dataset_rows", "value": str(len(ledger_rows)), "interpretation": "Priority and backup waves represented in the receipt ledger."},
        {"metric": "priority_raw_receipt_original_file_rows", "value": str(len(file_rows)), "interpretation": "Original package/documentation files counted after ignoring generated handoff files."},
        {"metric": "priority_raw_receipt_archive_files", "value": str(file_role_counts.get("archive_package", 0)), "interpretation": "Original archive packages present in priority target folders."},
        {"metric": "priority_raw_receipt_raw_tabular_files", "value": str(file_role_counts.get("raw_tabular_file", 0)), "interpretation": "Original raw tabular files present in priority target folders."},
        {"metric": "priority_raw_receipt_documentation_files", "value": str(file_role_counts.get("documentation_or_metadata", 0)), "interpretation": "Original documentation files present in priority target folders."},
        {"metric": "priority_raw_receipt_total_original_bytes", "value": str(sum(safe_int(row.get("total_original_bytes")) for row in ledger_rows)), "interpretation": "Total bytes of original files counted in priority target folders."},
        {"metric": "priority_raw_receipt_priority_targets", "value": str(sum(safe_int(row.get("priority_file_targets")) for row in ledger_rows)), "interpretation": "Priority target file/module rows checked for receipt coverage."},
        {"metric": "priority_raw_receipt_priority_targets_covered", "value": str(sum(safe_int(row.get("priority_targets_covered_direct_or_archive")) for row in ledger_rows)), "interpretation": "Priority targets covered by direct files or archive members."},
        {"metric": "priority_raw_receipt_priority_targets_missing", "value": str(sum(safe_int(row.get("priority_targets_missing")) for row in ledger_rows)), "interpretation": "Priority targets still missing from direct/archive receipt coverage."},
        {"metric": "priority_raw_receipt_missing_target_rows", "value": str(len(missing_rows)), "interpretation": "Missing target rows written for reviewer follow-up."},
        {"metric": "priority_raw_receipt_generated_files_ignored", "value": str(sum(safe_int(row.get("ignored_generated_file_count")) for row in ledger_rows)), "interpretation": "Generated handoff/placeholder files ignored as original package evidence."},
        {"metric": "priority_raw_receipt_complete_package_candidates", "value": str(receipt_counts.get("complete_raw_package_candidate_ready_for_schema_and_manual_audit", 0)), "interpretation": "Datasets with original raw/package receipt and all priority targets covered."},
        {"metric": "priority_raw_receipt_partial_package_candidates", "value": str(receipt_counts.get("partial_raw_package_candidate_missing_priority_targets", 0) + receipt_counts.get("raw_targets_covered_documentation_review_needed", 0)), "interpretation": "Datasets with some original raw/package receipt but remaining receipt or documentation gaps."},
        {"metric": "priority_raw_receipt_missing_package_rows", "value": str(receipt_counts.get("not_received_no_original_raw_package", 0)), "interpretation": "Datasets with no original raw package/tabular receipt yet."},
        {"metric": "modeling_gate_status", "value": "blocked", "interpretation": "Models remain blocked until promoted registry thresholds and accepted CHIRPS/ERA5 linkage pass."},
    ]
    for status, count in sorted(receipt_counts.items()):
        rows.append({"metric": f"priority_raw_receipt_status_{status}", "value": str(count), "interpretation": "Receipt status count."})
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


def write_report(ledger_rows: list[dict[str, str]], summary: list[dict[str, str]]) -> None:
    summary_table = "\n".join(f"| {row['metric']} | {row['value']} | {row['interpretation']} |" for row in summary)
    REPORT_PATH.write_text(
        f"""# Priority Raw Package Receipt Ledger

Status: fail-closed raw-package receipt layer. Generated placeholder and
handoff files are ignored as original package evidence.

## Summary

| Metric | Value | Interpretation |
|---|---:|---|
{summary_table}

## Dataset Receipt Status

{markdown_table(ledger_rows, ['acquisition_batch_rank', 'idno', 'country', 'wave', 'original_file_count', 'archive_file_count', 'raw_tabular_file_count', 'priority_targets_covered_direct_or_archive', 'priority_targets_missing', 'receipt_status'], 20)}

## Rule

Receipt is not promotion. A dataset can move toward promotion only after the
unchanged official raw package and documentation are present, priority target
coverage is checked through direct files or archive members, and downstream
manual value, unit, recall-period, missing-code, merge-key, weight, timing,
geography, and CHIRPS/ERA5 linkage gates pass.

## Machine-Readable Outputs

- `temp/priority_raw_package_receipt_ledger.csv`
- `temp/priority_raw_package_file_manifest.csv`
- `temp/priority_raw_package_missing_targets.csv`
- `result/priority_raw_package_receipt_summary.csv`
""",
        encoding="utf-8",
    )


def main() -> None:
    ensure_dirs()
    ledger_rows, file_rows, missing_rows, summary = build_outputs()
    write_csv(LEDGER_PATH, ledger_rows, LEDGER_COLUMNS)
    write_csv(FILE_MANIFEST_PATH, file_rows, FILE_COLUMNS)
    write_csv(MISSING_TARGETS_PATH, missing_rows, MISSING_COLUMNS)
    write_csv(SUMMARY_PATH, summary, SUMMARY_COLUMNS)
    write_report(ledger_rows, summary)
    append_log(
        TEMP_DIR / "audit_log.md",
        f"Built priority raw package receipt ledger datasets={len(ledger_rows)} original_files={len(file_rows)} missing_targets={len(missing_rows)}.",
    )
    print(
        f"Priority raw package receipt ledger datasets={len(ledger_rows)} "
        f"original_files={len(file_rows)} missing_targets={len(missing_rows)}."
    )


if __name__ == "__main__":
    main()
