from __future__ import annotations

import csv
from collections import defaultdict
from pathlib import Path
from typing import Any

from common import REPORT_DIR, RESULT_DIR, TEMP_DIR, append_log, ensure_dirs, write_csv


DOWNLOAD_PANEL_PATH = TEMP_DIR / "priority_lsms_isa_threshold_gap_download_panel.csv"
CORE_MANIFEST_PATH = TEMP_DIR / "priority_lsms_isa_minimum_batch_core_file_manifest.csv"
FULL_MANIFEST_PATH = TEMP_DIR / "priority_lsms_isa_minimum_batch_expected_file_manifest.csv"

PACKET_DIR = REPORT_DIR / "priority_lsms_isa_manual_download_packets"
PACKET_INDEX_PATH = TEMP_DIR / "priority_lsms_isa_manual_download_packet_index.csv"
PACKET_CORE_PATH = TEMP_DIR / "priority_lsms_isa_manual_download_packet_core_files.csv"
SUMMARY_PATH = RESULT_DIR / "priority_lsms_isa_manual_download_packet_summary.csv"
REPORT_PATH = REPORT_DIR / "priority_lsms_isa_manual_download_packets.md"

INDEX_COLUMNS = [
    "download_rank",
    "country",
    "wave",
    "idno",
    "threshold_download_role",
    "official_get_microdata_url",
    "local_target_folder",
    "expected_full_file_rows",
    "expected_missing_file_rows",
    "core_file_rows",
    "core_missing_file_rows",
    "unique_core_file_names",
    "requirements_covered",
    "packet_report_path",
    "download_action",
    "post_download_validation_commands",
    "promotion_stop_rule",
]

CORE_COLUMNS = [
    "download_rank",
    "country",
    "wave",
    "idno",
    "requirement",
    "file_rank",
    "file_id",
    "expected_file_name",
    "file_description",
    "candidate_variable_rows",
    "strong_candidate_variable_rows",
    "top_variable_names",
    "official_core_file_match_status",
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


def rel(path: Path) -> str:
    try:
        return str(path.relative_to(REPORT_DIR.parent)).replace("\\", "/")
    except ValueError:
        return str(path).replace("\\", "/")


def group_by_id(rows: list[dict[str, str]]) -> dict[str, list[dict[str, str]]]:
    grouped: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in rows:
        idno = clean(row.get("idno"))
        if idno:
            grouped[idno].append(row)
    return grouped


def unique_join(values: list[str], limit: int | None = None) -> str:
    seen: list[str] = []
    for value in values:
        text = clean(value)
        if text and text not in seen:
            seen.append(text)
    if limit is not None and len(seen) > limit:
        return ";".join(seen[:limit] + [f"...{len(seen) - limit} more"])
    return ";".join(seen)


def markdown_table(rows: list[dict[str, str]], columns: list[str], limit: int = 40) -> str:
    if not rows:
        return "_No rows._"
    lines = ["| " + " | ".join(columns) + " |", "| " + " | ".join("---" for _ in columns) + " |"]
    for row in rows[:limit]:
        lines.append("| " + " | ".join(clean(row.get(column)).replace("|", "/") for column in columns) + " |")
    if len(rows) > limit:
        lines.append("| " + " | ".join("..." for _ in columns) + " |")
    return "\n".join(lines)


def packet_rows(download_rows: list[dict[str, str]]) -> list[dict[str, str]]:
    return [
        row
        for row in sorted(download_rows, key=lambda r: safe_int(r.get("threshold_sequence_rank"), 9999))
        if clean(row.get("download_batch_role")) == "remaining_minimum_batch_download_action"
    ]


def build_index_and_core_rows(
    downloads: list[dict[str, str]],
    core_by_id: dict[str, list[dict[str, str]]],
) -> tuple[list[dict[str, str]], list[dict[str, str]]]:
    index_rows: list[dict[str, str]] = []
    core_packet_rows: list[dict[str, str]] = []
    for download_rank, row in enumerate(downloads, start=1):
        idno = clean(row.get("idno"))
        core_rows = sorted(
            core_by_id.get(idno, []),
            key=lambda r: (clean(r.get("requirement")), safe_int(r.get("file_rank")), clean(r.get("expected_file_name"))),
        )
        packet_path = PACKET_DIR / f"{idno}.md"
        unique_core_names = unique_join([core.get("expected_file_name", "") for core in core_rows], limit=25)
        requirements = unique_join([core.get("requirement", "") for core in core_rows])
        index_rows.append(
            {
                "download_rank": str(download_rank),
                "country": clean(row.get("country")),
                "wave": clean(row.get("wave")),
                "idno": idno,
                "threshold_download_role": clean(row.get("threshold_download_role")),
                "official_get_microdata_url": clean(row.get("official_get_microdata_url")),
                "local_target_folder": clean(row.get("local_target_folder")),
                "expected_full_file_rows": clean(row.get("official_expected_file_rows")),
                "expected_missing_file_rows": clean(row.get("official_expected_missing_rows")),
                "core_file_rows": clean(row.get("official_core_file_rows")),
                "core_missing_file_rows": clean(row.get("official_core_missing_rows")),
                "unique_core_file_names": unique_core_names,
                "requirements_covered": requirements,
                "packet_report_path": rel(packet_path),
                "download_action": clean(row.get("next_action")),
                "post_download_validation_commands": clean(row.get("post_download_validation_commands")),
                "promotion_stop_rule": clean(row.get("promotion_stop_rule")),
            }
        )
        for core in core_rows:
            core_packet_rows.append(
                {
                    "download_rank": str(download_rank),
                    "country": clean(row.get("country")),
                    "wave": clean(row.get("wave")),
                    "idno": idno,
                    "requirement": clean(core.get("requirement")),
                    "file_rank": clean(core.get("file_rank")),
                    "file_id": clean(core.get("file_id")),
                    "expected_file_name": clean(core.get("expected_file_name")),
                    "file_description": clean(core.get("file_description")),
                    "candidate_variable_rows": clean(core.get("candidate_variable_rows")),
                    "strong_candidate_variable_rows": clean(core.get("strong_candidate_variable_rows")),
                    "top_variable_names": clean(core.get("top_variable_names")),
                    "official_core_file_match_status": clean(core.get("official_core_file_match_status")),
                }
            )
    return index_rows, core_packet_rows


def write_packet(index_row: dict[str, str], core_rows: list[dict[str, str]]) -> None:
    packet_path = PACKET_DIR / f"{clean(index_row.get('idno'))}.md"
    lines = [
        f"# Manual Download Packet: {clean(index_row.get('idno'))}",
        "",
        "Status: credentialed/manual official raw package acquisition packet.",
        "This packet does not download raw data, accept terms, extract microdata,",
        "write `data/`, or run models.",
        "",
        "## Target",
        "",
        f"- Country: {clean(index_row.get('country'))}",
        f"- Wave: {clean(index_row.get('wave'))}",
        f"- IDNO: {clean(index_row.get('idno'))}",
        f"- Official get-microdata URL: {clean(index_row.get('official_get_microdata_url'))}",
        f"- Local target folder: `{clean(index_row.get('local_target_folder'))}`",
        f"- Expected official files: {clean(index_row.get('expected_full_file_rows'))}",
        f"- Missing expected files: {clean(index_row.get('expected_missing_file_rows'))}",
        f"- Requirement-linked core file rows: {clean(index_row.get('core_file_rows'))}",
        f"- Missing core file rows: {clean(index_row.get('core_missing_file_rows'))}",
        "",
        "## Manual Action",
        "",
        clean(index_row.get("download_action")),
        "",
        "## Core Files To Confirm After Download",
        "",
        markdown_table(
            core_rows,
            [
                "requirement",
                "file_id",
                "expected_file_name",
                "file_description",
                "top_variable_names",
                "official_core_file_match_status",
            ],
            limit=80,
        ),
        "",
        "## Post-Download Validation",
        "",
        "Run after the complete official package and documentation are placed locally:",
        "",
        "```bash",
        clean(index_row.get("post_download_validation_commands")),
        "```",
        "",
        "## Stop Rule",
        "",
        clean(index_row.get("promotion_stop_rule")),
    ]
    packet_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_index_report(index_rows: list[dict[str, str]], core_rows: list[dict[str, str]], full_rows: list[dict[str, str]]) -> None:
    priority_country_rows = sum(1 for row in index_rows if clean(row.get("country")) in {"Ethiopia", "Nigeria", "Malawi", "Tanzania", "Uganda"})
    expected_files = sum(safe_int(row.get("expected_full_file_rows")) for row in index_rows)
    missing_files = sum(safe_int(row.get("expected_missing_file_rows")) for row in index_rows)
    core_missing = sum(safe_int(row.get("core_missing_file_rows")) for row in index_rows)
    lines = [
        "# Priority LSMS-ISA Manual Download Packets",
        "",
        "Status: per-wave manual acquisition packets for the remaining minimum",
        "threshold batch. These packets are intentionally small and executable:",
        "open the official page, download the complete unchanged package, place it",
        "under the local target folder, and run the validation commands.",
        "",
        "No raw data are stored here. No `data/` writes or models are triggered.",
        "",
        "## Summary",
        "",
        f"- Manual download packet rows: {len(index_rows)}",
        f"- Priority-country packet rows: {priority_country_rows}",
        f"- Expected official full-file rows across packets: {expected_files}",
        f"- Still-missing expected full-file rows: {missing_files}",
        f"- Requirement-linked core-file rows listed: {len(core_rows)}",
        f"- Still-missing core-file rows: {core_missing}",
        f"- Minimum-batch official full-file manifest rows available: {len(full_rows)}",
        "",
        "## Packet Index",
        "",
        markdown_table(
            index_rows,
            [
                "download_rank",
                "country",
                "wave",
                "idno",
                "expected_missing_file_rows",
                "core_missing_file_rows",
                "official_get_microdata_url",
                "local_target_folder",
                "packet_report_path",
            ],
            limit=20,
        ),
        "",
        "## Outputs",
        "",
        "- `temp/priority_lsms_isa_manual_download_packet_index.csv`",
        "- `temp/priority_lsms_isa_manual_download_packet_core_files.csv`",
        "- `result/priority_lsms_isa_manual_download_packet_summary.csv`",
        "- `report/priority_lsms_isa_manual_download_packets/<IDNO>.md`",
        "",
        "## Stop Rule",
        "",
        "These packets only support credentialed/manual acquisition. Modeling remains",
        "blocked until promoted registry thresholds pass with value-verified raw files",
        "and accepted CHIRPS or ERA5 climate linkage.",
    ]
    REPORT_PATH.write_text("\n".join(lines) + "\n", encoding="utf-8")


def build_summary(index_rows: list[dict[str, str]], core_rows: list[dict[str, str]], full_rows: list[dict[str, str]]) -> list[dict[str, str]]:
    priority_countries = {"Ethiopia", "Nigeria", "Malawi", "Tanzania", "Uganda"}
    packet_files = sorted(PACKET_DIR.glob("*.md")) if PACKET_DIR.exists() else []
    return [
        {"metric": "manual_download_packet_rows", "value": str(len(index_rows)), "interpretation": "Remaining minimum-batch country-waves with a manual download packet."},
        {"metric": "manual_download_packet_priority_country_rows", "value": str(sum(1 for row in index_rows if clean(row.get("country")) in priority_countries)), "interpretation": "Packets for Ethiopia, Nigeria, Malawi, Tanzania, and Uganda."},
        {"metric": "manual_download_packet_sixth_country_rows", "value": str(sum(1 for row in index_rows if clean(row.get("country")) not in priority_countries)), "interpretation": "Packets for sixth-country threshold candidates."},
        {"metric": "manual_download_packet_expected_full_file_rows", "value": str(sum(safe_int(row.get("expected_full_file_rows")) for row in index_rows)), "interpretation": "Expected official full-file rows across packeted downloads."},
        {"metric": "manual_download_packet_missing_full_file_rows", "value": str(sum(safe_int(row.get("expected_missing_file_rows")) for row in index_rows)), "interpretation": "Expected official full-file rows still missing across packeted downloads."},
        {"metric": "manual_download_packet_core_file_rows", "value": str(len(core_rows)), "interpretation": "Requirement-linked core-file rows written to packet core-file CSV."},
        {"metric": "manual_download_packet_missing_core_file_rows", "value": str(sum(safe_int(row.get("core_missing_file_rows")) for row in index_rows)), "interpretation": "Requirement-linked core-file rows still missing across packeted downloads."},
        {"metric": "manual_download_packet_full_manifest_rows_available", "value": str(len(full_rows)), "interpretation": "Minimum-batch expected full-file manifest rows available as source evidence."},
        {"metric": "manual_download_packet_reports_written", "value": str(len(packet_files)), "interpretation": "Per-IDNO markdown packets written under report/priority_lsms_isa_manual_download_packets/."},
        {"metric": "data_write_gate_status", "value": "blocked_no_data_write", "interpretation": "Manual download packets do not write promoted data."},
        {"metric": "modeling_gate_status", "value": "blocked", "interpretation": "No predictive, reduced-form, causal ML, or policy learning until registry thresholds pass."},
    ]


def main() -> None:
    ensure_dirs()
    PACKET_DIR.mkdir(parents=True, exist_ok=True)
    download_rows = read_csv_dicts(DOWNLOAD_PANEL_PATH)
    core_rows = read_csv_dicts(CORE_MANIFEST_PATH)
    full_rows = read_csv_dicts(FULL_MANIFEST_PATH)
    downloads = packet_rows(download_rows)
    core_by_id = group_by_id(core_rows)
    index_rows, core_packet_rows = build_index_and_core_rows(downloads, core_by_id)
    core_packet_by_id = group_by_id(core_packet_rows)
    for index_row in index_rows:
        write_packet(index_row, core_packet_by_id.get(clean(index_row.get("idno")), []))
    write_index_report(index_rows, core_packet_rows, full_rows)
    summary_rows = build_summary(index_rows, core_packet_rows, full_rows)
    write_csv(PACKET_INDEX_PATH, index_rows, INDEX_COLUMNS)
    write_csv(PACKET_CORE_PATH, core_packet_rows, CORE_COLUMNS)
    write_csv(SUMMARY_PATH, summary_rows, SUMMARY_COLUMNS)
    append_log(TEMP_DIR / "audit_log.md", "Built priority LSMS/ISA manual download packets for the remaining minimum batch.")
    print(
        "Priority LSMS/ISA manual download packets complete: "
        f"packets={len(index_rows)}, core_rows={len(core_packet_rows)}"
    )


if __name__ == "__main__":
    main()
