from __future__ import annotations

import csv
from pathlib import Path
from typing import Any

from common import PROJECT_ROOT, REPORT_DIR, RESULT_DIR, TEMP_DIR, append_log, ensure_dirs, write_csv


PACKET_INDEX_PATH = TEMP_DIR / "priority_lsms_isa_manual_download_packet_index.csv"
INCOMING_ROUTE_PLAN_PATH = TEMP_DIR / "priority_lsms_isa_incoming_raw_package_route_plan.csv"

PROGRESS_PATH = TEMP_DIR / "priority_lsms_isa_manual_download_progress_tracker.csv"
SUMMARY_PATH = RESULT_DIR / "priority_lsms_isa_manual_download_progress_summary.csv"
REPORT_PATH = REPORT_DIR / "priority_lsms_isa_manual_download_progress_tracker.md"

ARCHIVE_SUFFIXES = {".zip", ".rar", ".7z", ".tar", ".gz", ".tgz"}
TABULAR_SUFFIXES = {".dta", ".sav", ".por", ".sas7bdat", ".xpt", ".csv", ".tsv", ".xlsx", ".xls", ".nsdstat"}
DOCUMENT_SUFFIXES = {".pdf", ".doc", ".docx", ".txt", ".xml", ".html", ".htm", ".rtf"}

PROGRESS_COLUMNS = [
    "download_rank",
    "country",
    "wave",
    "idno",
    "progress_status",
    "local_target_folder",
    "target_folder_exists",
    "target_file_count",
    "target_total_bytes",
    "target_archive_file_count",
    "target_raw_tabular_file_count",
    "target_documentation_file_count",
    "top_local_file_names",
    "incoming_route_rows",
    "incoming_copy_candidate_rows",
    "incoming_manual_review_rows",
    "official_get_microdata_url",
    "packet_report_path",
    "next_action",
    "post_download_validation_commands",
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


def resolve_project_path(path_text: str) -> Path:
    text = clean(path_text).replace("\\", "/").strip()
    path = Path(text)
    if path.is_absolute():
        return path
    return PROJECT_ROOT / text


def file_kind_counts(files: list[Path]) -> tuple[int, int, int]:
    archive = tabular = docs = 0
    for path in files:
        lower_name = path.name.lower()
        suffix = path.suffix.lower()
        if suffix in ARCHIVE_SUFFIXES or lower_name.endswith(".tar.gz"):
            archive += 1
        if suffix in TABULAR_SUFFIXES or lower_name.endswith(".nsdstat"):
            tabular += 1
        if suffix in DOCUMENT_SUFFIXES:
            docs += 1
    return archive, tabular, docs


def target_files(folder: Path) -> list[Path]:
    if not folder.exists():
        return []
    return sorted(path for path in folder.rglob("*") if path.is_file() and not path.name.startswith("_"))


def incoming_rows_for_id(rows: list[dict[str, str]], idno: str) -> list[dict[str, str]]:
    return [row for row in rows if clean(row.get("selected_idno")) == idno]


def progress_status(target_count: int, incoming_rows: list[dict[str, str]]) -> str:
    if target_count > 0:
        return "target_files_present_run_validation"
    copy_rows = [row for row in incoming_rows if clean(row.get("route_decision")) == "copy_to_selected_target"]
    if copy_rows:
        return "incoming_copy_candidate_review_and_copy"
    if incoming_rows:
        return "incoming_route_review_required"
    return "blocked_no_local_or_incoming_files"


def next_action(status: str, packet: dict[str, str]) -> str:
    if status == "target_files_present_run_validation":
        return "Run the post-download validation commands, then refresh receipt, schema, value-profile, semantics, promotion packets, registry, and validation."
    if status == "incoming_copy_candidate_review_and_copy":
        return "Review temp/priority_lsms_isa_incoming_raw_package_route_plan.csv, copy the selected incoming file into the target folder, then run validation."
    if status == "incoming_route_review_required":
        return "Review incoming route candidates manually before copying any file into a country-wave target folder."
    return clean(packet.get("download_action"))


def build_progress_rows(packet_rows: list[dict[str, str]], incoming_rows: list[dict[str, str]]) -> list[dict[str, str]]:
    progress_rows: list[dict[str, str]] = []
    for packet in sorted(packet_rows, key=lambda r: safe_int(r.get("download_rank"), 9999)):
        idno = clean(packet.get("idno"))
        folder = resolve_project_path(packet.get("local_target_folder", ""))
        files = target_files(folder)
        incoming_for_id = incoming_rows_for_id(incoming_rows, idno)
        copy_rows = [row for row in incoming_for_id if clean(row.get("route_decision")) == "copy_to_selected_target"]
        manual_rows = [row for row in incoming_for_id if clean(row.get("route_decision")) != "copy_to_selected_target"]
        archive_count, tabular_count, doc_count = file_kind_counts(files)
        status = progress_status(len(files), incoming_for_id)
        progress_rows.append(
            {
                "download_rank": clean(packet.get("download_rank")),
                "country": clean(packet.get("country")),
                "wave": clean(packet.get("wave")),
                "idno": idno,
                "progress_status": status,
                "local_target_folder": clean(packet.get("local_target_folder")),
                "target_folder_exists": "1" if folder.exists() else "0",
                "target_file_count": str(len(files)),
                "target_total_bytes": str(sum(path.stat().st_size for path in files)),
                "target_archive_file_count": str(archive_count),
                "target_raw_tabular_file_count": str(tabular_count),
                "target_documentation_file_count": str(doc_count),
                "top_local_file_names": ";".join(path.name for path in files[:12]),
                "incoming_route_rows": str(len(incoming_for_id)),
                "incoming_copy_candidate_rows": str(len(copy_rows)),
                "incoming_manual_review_rows": str(len(manual_rows)),
                "official_get_microdata_url": clean(packet.get("official_get_microdata_url")),
                "packet_report_path": clean(packet.get("packet_report_path")),
                "next_action": next_action(status, packet),
                "post_download_validation_commands": clean(packet.get("post_download_validation_commands")),
                "data_write_gate_status": "blocked_no_data_write",
                "modeling_gate_status": "blocked",
            }
        )
    return progress_rows


def summary_row(metric: str, value: Any, interpretation: str) -> dict[str, str]:
    return {"metric": metric, "value": str(value), "interpretation": interpretation}


def build_summary(rows: list[dict[str, str]]) -> list[dict[str, str]]:
    status_counts: dict[str, int] = {}
    for row in rows:
        status = clean(row.get("progress_status"))
        status_counts[status] = status_counts.get(status, 0) + 1
    target_files = sum(safe_int(row.get("target_file_count")) for row in rows)
    target_bytes = sum(safe_int(row.get("target_total_bytes")) for row in rows)
    incoming_routes = sum(safe_int(row.get("incoming_route_rows")) for row in rows)
    copy_candidates = sum(safe_int(row.get("incoming_copy_candidate_rows")) for row in rows)
    summary = [
        summary_row("manual_download_progress_packet_rows", len(rows), "Manual-download packets tracked for local file progress."),
        summary_row("manual_download_progress_target_file_rows", target_files, "Non-generated files currently found under packet target folders."),
        summary_row("manual_download_progress_target_total_bytes", target_bytes, "Bytes currently found under packet target folders."),
        summary_row("manual_download_progress_incoming_route_rows", incoming_routes, "Incoming route rows currently mapped to tracked packet IDNOs."),
        summary_row("manual_download_progress_incoming_copy_candidate_rows", copy_candidates, "Incoming files with one selected packet target."),
        summary_row("manual_download_progress_validation_ready_packets", status_counts.get("target_files_present_run_validation", 0), "Packets with target files present and ready for receipt/schema/value validation."),
        summary_row("manual_download_progress_blocked_no_file_packets", status_counts.get("blocked_no_local_or_incoming_files", 0), "Packets still lacking local target files or incoming route matches."),
        summary_row("data_write_gate_status", "blocked_no_data_write", "Progress tracking does not write promoted data."),
        summary_row("modeling_gate_status", "blocked", "No predictive, reduced-form, causal ML, or policy learning until registry thresholds pass."),
    ]
    for status, count in sorted(status_counts.items()):
        summary.append(summary_row(f"manual_download_progress_status_{status}", count, "Packet count by local download progress status."))
    return summary


def markdown_table(rows: list[dict[str, str]], columns: list[str], limit: int = 30) -> str:
    if not rows:
        return "_No rows._"
    lines = ["| " + " | ".join(columns) + " |", "| " + " | ".join("---" for _ in columns) + " |"]
    for row in rows[:limit]:
        lines.append("| " + " | ".join(clean(row.get(column)).replace("|", "/") for column in columns) + " |")
    if len(rows) > limit:
        lines.append("| " + " | ".join("..." for _ in columns) + " |")
    return "\n".join(lines)


def write_report(rows: list[dict[str, str]], summary_rows: list[dict[str, str]]) -> None:
    metric = {row["metric"]: row["value"] for row in summary_rows}
    lines = [
        "# Priority LSMS-ISA Manual Download Progress Tracker",
        "",
        "Status: local progress tracker for the 10 remaining minimum-batch manual",
        "download packets. It scans packet target folders and incoming-route rows.",
        "",
        "It does not download, copy, delete, extract, promote, write `data/`, or run models.",
        "",
        "## Summary",
        "",
        f"- Packets tracked: {metric.get('manual_download_progress_packet_rows', '0')}",
        f"- Packets with target files ready for validation: {metric.get('manual_download_progress_validation_ready_packets', '0')}",
        f"- Packets still blocked with no local or incoming files: {metric.get('manual_download_progress_blocked_no_file_packets', '0')}",
        f"- Incoming copy candidates: {metric.get('manual_download_progress_incoming_copy_candidate_rows', '0')}",
        f"- Target-folder non-generated files: {metric.get('manual_download_progress_target_file_rows', '0')}",
        "",
        "## Packet Progress",
        "",
        markdown_table(
            rows,
            [
                "download_rank",
                "country",
                "wave",
                "idno",
                "progress_status",
                "target_file_count",
                "incoming_route_rows",
                "packet_report_path",
            ],
            limit=20,
        ),
        "",
        "## Outputs",
        "",
        "- `temp/priority_lsms_isa_manual_download_progress_tracker.csv`",
        "- `result/priority_lsms_isa_manual_download_progress_summary.csv`",
        "",
        "## Stop Rule",
        "",
        "This tracker only reports local acquisition progress. Each country-wave still",
        "needs complete official-file receipt, raw-value verification, outcome/timing/",
        "geography checks, and accepted climate linkage before any `data/` write.",
    ]
    REPORT_PATH.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    ensure_dirs()
    packet_rows = read_csv_dicts(PACKET_INDEX_PATH)
    incoming_rows = read_csv_dicts(INCOMING_ROUTE_PLAN_PATH)
    progress_rows = build_progress_rows(packet_rows, incoming_rows)
    summary_rows = build_summary(progress_rows)
    write_csv(PROGRESS_PATH, progress_rows, PROGRESS_COLUMNS)
    write_csv(SUMMARY_PATH, summary_rows, SUMMARY_COLUMNS)
    write_report(progress_rows, summary_rows)
    append_log(TEMP_DIR / "audit_log.md", "Built priority LSMS/ISA manual download progress tracker.")
    print(
        "Priority LSMS/ISA manual download progress tracker complete: "
        f"packets={len(progress_rows)}, validation_ready="
        f"{sum(1 for row in progress_rows if row['progress_status'] == 'target_files_present_run_validation')}"
    )


if __name__ == "__main__":
    main()
