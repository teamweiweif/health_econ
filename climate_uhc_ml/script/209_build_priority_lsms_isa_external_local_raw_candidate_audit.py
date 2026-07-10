from __future__ import annotations

import csv
import re
from collections import defaultdict
from pathlib import Path
from typing import Any

from common import REPORT_DIR, RESULT_DIR, TEMP_DIR, append_log, ensure_dirs, write_csv


EXTERNAL_ROOT = Path(r"D:\GlobalHealthPolicy Dropbox\Fan Bowei\HEALTH EXPENDITURE MEASUREMENT\HEALTH VS CONSUMPTION\Data")
QUEUE_PATH = TEMP_DIR / "priority_lsms_isa_refocused_acquisition_queue.csv"
FILE_MATCH_PATH = TEMP_DIR / "priority_lsms_isa_official_file_receipt_file_match.csv"
CORE_MATCH_PATH = TEMP_DIR / "priority_lsms_isa_official_file_receipt_core_match.csv"

AUDIT_PATH = RESULT_DIR / "priority_lsms_isa_external_local_raw_candidate_audit.csv"
FILE_MATCH_AUDIT_PATH = RESULT_DIR / "priority_lsms_isa_external_local_raw_candidate_file_match.csv"
SUMMARY_PATH = RESULT_DIR / "priority_lsms_isa_external_local_raw_candidate_summary.csv"
REPORT_PATH = REPORT_DIR / "priority_lsms_isa_external_local_raw_candidate_audit.md"

EXTERNAL_FOLDER_HINTS = {
    "MWI_2004_IHS-II_v01_M": ["malawi_2004"],
    "MWI_2010_IHS-III_v01_M": ["malawi_2010"],
    "MWI_2016_IHS-IV_v04_M": ["malawi_2016"],
    "NGA_2010_GHSP-W1_v03_M": ["nigeria_2010"],
    "NGA_2012_GHSP-W2_v02_M": ["nigeria_2012"],
    "NGA_2015_GHSP-W3_v02_M": ["nigeria_2015"],
    "TZA_2008_NPS-R1_v03_M": ["tanzania_NPS_08_10_12_14/NPS_08"],
    "TZA_2010_NPS-R2_v03_M": ["tanzania_NPS_08_10_12_14/NPS_10"],
    "TZA_2012_NPS-R3_v01_M": ["tanzania_NPS_08_10_12_14/NPS_12"],
    "UGA_2011_UNPS_v02_M": ["uganda_2011"],
}

RAW_LIKE_SUFFIXES = {".dta", ".sav", ".por", ".sas7bdat", ".xpt", ".csv", ".xlsx", ".xls"}

AUDIT_COLUMNS = [
    "download_priority_order",
    "queue_role",
    "country",
    "wave",
    "idno",
    "current_plan_status",
    "locked_download_target",
    "external_root_exists",
    "external_folder_hint",
    "external_candidate_folder",
    "external_candidate_folder_exists",
    "external_file_rows",
    "external_raw_like_file_rows",
    "external_total_bytes",
    "expected_file_rows",
    "external_expected_file_match_rows",
    "external_expected_file_missing_rows",
    "core_file_rows",
    "external_core_file_match_rows",
    "external_core_file_missing_rows",
    "matched_requirement_names",
    "unmatched_requirement_names",
    "candidate_receipt_status",
    "provenance_acceptance_status",
    "recommended_next_action",
    "copy_target_folder",
    "post_copy_validation_command",
    "data_write_gate_status",
    "modeling_gate_status",
]

FILE_MATCH_COLUMNS = [
    "download_priority_order",
    "country",
    "wave",
    "idno",
    "file_id",
    "expected_file_name",
    "priority_core_target",
    "core_requirements",
    "external_candidate_folder",
    "external_match_status",
    "external_matched_file_name",
    "external_matched_file_path",
    "data_write_gate_status",
    "modeling_gate_status",
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


def norm_keys(name: str) -> set[str]:
    text = clean(name).lower().replace("\\", "/").split("/")[-1]
    stem = re.sub(r"\.(dta|sav|por|sas7bdat|xpt|csv|xlsx|xls|pdf|txt|do)$", "", text)
    compact = re.sub(r"[^a-z0-9]+", "", text)
    compact_stem = re.sub(r"[^a-z0-9]+", "", stem)
    keys = {text, stem, compact, compact_stem}
    if "." in stem:
        keys.add(stem.split(".")[0])
        keys.add(re.sub(r"[^a-z0-9]+", "", stem.split(".")[0]))
    return {key for key in keys if key}


def group_by_id(rows: list[dict[str, str]]) -> dict[str, list[dict[str, str]]]:
    out: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in rows:
        idno = clean(row.get("idno"))
        if idno:
            out[idno].append(row)
    return out


def candidate_files(folder: Path) -> list[Path]:
    if not folder.exists() or not folder.is_dir():
        return []
    return [path for path in folder.rglob("*") if path.is_file()]


def build_file_index(files: list[Path]) -> dict[str, Path]:
    out: dict[str, Path] = {}
    for path in files:
        for key in norm_keys(path.name):
            out.setdefault(key, path)
    return out


def first_match(expected_name: str, index: dict[str, Path]) -> Path | None:
    for key in norm_keys(expected_name):
        if key in index:
            return index[key]
    return None


def status_for(folder_exists: bool, expected_rows: int, expected_matched: int, core_rows: int, core_matched: int) -> str:
    if not folder_exists:
        return "no_external_candidate_folder"
    if expected_rows == 0 and core_rows == 0:
        return "external_candidate_present_no_expected_file_matrix"
    if core_rows > 0 and core_matched == core_rows:
        return "external_candidate_core_file_names_complete_pending_provenance"
    if core_matched > 0:
        return "external_candidate_partial_core_file_name_matches_pending_provenance"
    if expected_matched > 0:
        return "external_candidate_expected_file_name_matches_no_core_complete"
    return "external_candidate_present_no_expected_file_name_matches"


def build_outputs() -> tuple[list[dict[str, str]], list[dict[str, str]], list[dict[str, str]]]:
    queue_rows = read_csv_dicts(QUEUE_PATH)
    file_rows_by_id = group_by_id(read_csv_dicts(FILE_MATCH_PATH))
    core_rows_by_id = group_by_id(read_csv_dicts(CORE_MATCH_PATH))

    audits: list[dict[str, str]] = []
    file_matches: list[dict[str, str]] = []
    external_root_exists = EXTERNAL_ROOT.exists()

    for queue in queue_rows:
        idno = clean(queue.get("idno"))
        hints = EXTERNAL_FOLDER_HINTS.get(idno, [])
        folders = [EXTERNAL_ROOT / hint for hint in hints] if external_root_exists else []
        folder = next((candidate for candidate in folders if candidate.exists()), folders[0] if folders else None)
        folder_exists = bool(folder is not None and folder.exists())
        files = candidate_files(folder) if folder_exists and folder is not None else []
        file_index = build_file_index(files)
        raw_like_files = [path for path in files if path.suffix.lower() in RAW_LIKE_SUFFIXES]
        expected_rows = file_rows_by_id.get(idno, [])
        core_rows = core_rows_by_id.get(idno, [])
        expected_match_count = 0
        core_match_count = 0
        matched_requirements: set[str] = set()
        all_requirements: set[str] = set()

        for row in expected_rows:
            match = first_match(clean(row.get("expected_file_name")), file_index)
            if match:
                expected_match_count += 1
            file_matches.append(
                {
                    "download_priority_order": clean(queue.get("download_priority_order")),
                    "country": clean(queue.get("country")),
                    "wave": clean(queue.get("wave")),
                    "idno": idno,
                    "file_id": clean(row.get("file_id")),
                    "expected_file_name": clean(row.get("expected_file_name")),
                    "priority_core_target": clean(row.get("priority_core_target")),
                    "core_requirements": clean(row.get("core_requirements")),
                    "external_candidate_folder": str(folder) if folder is not None else "",
                    "external_match_status": "external_file_name_match" if match else "external_file_name_missing",
                    "external_matched_file_name": match.name if match else "",
                    "external_matched_file_path": str(match) if match else "",
                    "data_write_gate_status": "blocked_no_data_write",
                    "modeling_gate_status": "blocked",
                }
            )

        for row in core_rows:
            match = first_match(clean(row.get("expected_file_name")), file_index)
            requirement = clean(row.get("requirement"))
            if requirement:
                all_requirements.add(requirement)
            if match:
                core_match_count += 1
                if requirement:
                    matched_requirements.add(requirement)

        status = status_for(folder_exists, len(expected_rows), expected_match_count, len(core_rows), core_match_count)
        locked_target = "1" if clean(queue.get("current_plan_status")) == "selected_in_refocused_plan" else "0"
        audits.append(
            {
                "download_priority_order": clean(queue.get("download_priority_order")),
                "queue_role": clean(queue.get("queue_role")),
                "country": clean(queue.get("country")),
                "wave": clean(queue.get("wave")),
                "idno": idno,
                "current_plan_status": clean(queue.get("current_plan_status")),
                "locked_download_target": locked_target,
                "external_root_exists": "1" if external_root_exists else "0",
                "external_folder_hint": ";".join(hints),
                "external_candidate_folder": str(folder) if folder is not None else "",
                "external_candidate_folder_exists": "1" if folder_exists else "0",
                "external_file_rows": str(len(files)),
                "external_raw_like_file_rows": str(len(raw_like_files)),
                "external_total_bytes": str(sum(path.stat().st_size for path in files)),
                "expected_file_rows": str(len(expected_rows)),
                "external_expected_file_match_rows": str(expected_match_count),
                "external_expected_file_missing_rows": str(max(0, len(expected_rows) - expected_match_count)),
                "core_file_rows": str(len(core_rows)),
                "external_core_file_match_rows": str(core_match_count),
                "external_core_file_missing_rows": str(max(0, len(core_rows) - core_match_count)),
                "matched_requirement_names": ";".join(sorted(matched_requirements)),
                "unmatched_requirement_names": ";".join(sorted(all_requirements - matched_requirements)),
                "candidate_receipt_status": status,
                "provenance_acceptance_status": "not_accepted_external_local_candidate_requires_official_source_review",
                "recommended_next_action": "Review provenance against official World Bank package, then copy the complete folder into the target temp/raw_downloads IDNO folder and run receipt/schema/value validation." if folder_exists and expected_match_count > 0 else "No action unless provenance or a matching complete package is found.",
                "copy_target_folder": clean(queue.get("local_target_folder")),
                "post_copy_validation_command": f"python script/178_build_priority_lsms_isa_post_download_validation_runner.py --idno {idno} --execute",
                "data_write_gate_status": "blocked_no_data_write",
                "modeling_gate_status": "blocked",
            }
        )

    locked_rows = [row for row in audits if row.get("locked_download_target") == "1"]
    locked_candidate_rows = [row for row in locked_rows if row.get("external_candidate_folder_exists") == "1" and safe_int(row.get("external_expected_file_match_rows")) > 0]
    locked_core_complete_rows = [row for row in locked_rows if row.get("candidate_receipt_status") == "external_candidate_core_file_names_complete_pending_provenance"]
    backup_candidate_rows = [row for row in audits if row.get("locked_download_target") != "1" and row.get("external_candidate_folder_exists") == "1" and safe_int(row.get("external_expected_file_match_rows")) > 0]
    summary = [
        {"metric": "external_local_raw_candidate_queue_rows", "value": str(len(audits)), "interpretation": "Refocused LSMS/ISA queue rows audited against the external local raw candidate root."},
        {"metric": "external_local_raw_candidate_root_exists", "value": "1" if external_root_exists else "0", "interpretation": "Whether the external health-expenditure raw-data root exists on this machine."},
        {"metric": "external_local_raw_candidate_folder_exists_rows", "value": str(sum(1 for row in audits if row.get("external_candidate_folder_exists") == "1")), "interpretation": "Queue rows with a mapped external local folder."},
        {"metric": "external_local_raw_candidate_expected_match_rows", "value": str(sum(safe_int(row.get("external_expected_file_match_rows")) for row in audits)), "interpretation": "Expected official file-name rows matched by external local candidates."},
        {"metric": "external_local_raw_candidate_core_match_rows", "value": str(sum(safe_int(row.get("external_core_file_match_rows")) for row in audits)), "interpretation": "Requirement-linked core file-name rows matched by external local candidates."},
        {"metric": "external_local_raw_candidate_locked_target_rows", "value": str(len(locked_rows)), "interpretation": "Rows selected in the current refocused plan."},
        {"metric": "external_local_raw_candidate_locked_target_with_matches_rows", "value": str(len(locked_candidate_rows)), "interpretation": "Selected rows with external local expected-file matches."},
        {"metric": "external_local_raw_candidate_locked_core_complete_rows", "value": str(len(locked_core_complete_rows)), "interpretation": "Selected rows whose requirement-linked core file names are complete in the external local candidate folder."},
        {"metric": "external_local_raw_candidate_backup_with_matches_rows", "value": str(len(backup_candidate_rows)), "interpretation": "Backup rows with external local expected-file matches."},
        {"metric": "external_local_raw_candidate_provenance_accepted_rows", "value": "0", "interpretation": "External local candidates are not accepted as official receipt until provenance and unchanged package status are reviewed."},
        {"metric": "data_write_gate_status", "value": "blocked_no_data_write", "interpretation": "The audit does not copy raw files or write promoted data."},
        {"metric": "modeling_gate_status", "value": "blocked", "interpretation": "No predictive, reduced-form, causal ML, or policy learning is opened."},
    ]
    return audits, file_matches, summary


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
        lines.append("| ... | ... | ... | ... | ... | ... | ... | ... | ... | ... |")
    return "\n".join(lines)


def write_report(audits: list[dict[str, str]], summary: list[dict[str, str]]) -> None:
    lines = [
        "# Priority LSMS/ISA External Local Raw Candidate Audit",
        "",
        "Status: filesystem-only audit of local raw-data candidates found outside the `climate_uhc_ml` workspace.",
        "",
        "This audit checks whether an existing local health-expenditure data folder contains filenames matching the expected World Bank LSMS/ISA files for the refocused queue. It does not read raw data contents, copy raw files, accept provenance, write `data/`, or open modeling.",
        "",
        "## Summary",
        "",
        markdown_table(summary, ["metric", "value", "interpretation"], limit=30),
        "",
        "## Candidate Rows",
        "",
        markdown_table(
            audits,
            [
                "download_priority_order",
                "country",
                "wave",
                "idno",
                "current_plan_status",
                "external_candidate_folder_exists",
                "external_file_rows",
                "expected_file_rows",
                "external_expected_file_match_rows",
                "core_file_rows",
                "external_core_file_match_rows",
                "candidate_receipt_status",
            ],
            limit=25,
        ),
        "",
        "## Stop Rule",
        "",
        "External local matches are only acquisition leads. They cannot be treated as official raw package receipt until provenance, completeness, unchanged-file status, schema, value, semantics, timing/geography, and climate-linkage gates pass.",
    ]
    REPORT_PATH.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    ensure_dirs()
    audits, file_matches, summary = build_outputs()
    write_csv(AUDIT_PATH, audits, AUDIT_COLUMNS)
    write_csv(FILE_MATCH_AUDIT_PATH, file_matches, FILE_MATCH_COLUMNS)
    write_csv(SUMMARY_PATH, summary, SUMMARY_COLUMNS)
    write_report(audits, summary)
    append_log(TEMP_DIR / "audit_log.md", f"Built priority LSMS/ISA external local raw candidate audit rows={len(audits)}.")
    print(f"Priority LSMS/ISA external local raw candidate audit rows={len(audits)} file_rows={len(file_matches)}.")


if __name__ == "__main__":
    main()
