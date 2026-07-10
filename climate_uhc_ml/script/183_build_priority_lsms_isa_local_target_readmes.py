from __future__ import annotations

import csv
from pathlib import Path
from typing import Any

from common import PROJECT_ROOT, REPORT_DIR, RESULT_DIR, TEMP_DIR, append_log, ensure_dirs, sha256_file, write_csv


BOARD_PATH = TEMP_DIR / "priority_lsms_isa_manual_download_execution_board.csv"
FILE_MATRIX_PATH = TEMP_DIR / "priority_lsms_isa_download_acceptance_file_matrix.csv"
REQUIREMENT_MATRIX_PATH = TEMP_DIR / "priority_lsms_isa_download_acceptance_requirement_matrix.csv"

MANIFEST_PATH = TEMP_DIR / "priority_lsms_isa_local_target_readme_manifest.csv"
SUMMARY_PATH = RESULT_DIR / "priority_lsms_isa_local_target_readme_summary.csv"
REPORT_PATH = REPORT_DIR / "priority_lsms_isa_local_target_readmes.md"

TARGET_README_NAME = "_PRIORITY_LSMS_ISA_DOWNLOAD_ACCEPTANCE.md"

POST_DOWNLOAD_COMMANDS = (
    "python script/17_audit_raw_downloads.py; "
    "python script/144_build_priority_lsms_isa_raw_package_intake_packet.py; "
    "python script/145_build_priority_lsms_isa_archive_member_preflight.py; "
    "python script/150_build_priority_lsms_isa_raw_package_receipt_checklist.py; "
    "python script/153_validate_priority_lsms_isa_official_file_receipt.py; "
    "python script/182_build_priority_lsms_isa_download_acceptance_matrix.py; "
    "python script/157_build_priority_lsms_isa_received_raw_schema_audit.py; "
    "python script/158_build_priority_lsms_isa_received_raw_value_profile.py; "
    "python script/159_build_priority_lsms_isa_received_raw_semantics_review.py; "
    "python script/148_build_priority_lsms_isa_country_wave_promotion_packets.py; "
    "python script/151_refresh_refocused_promoted_country_wave_registry.py; "
    "python script/173_build_priority_lsms_isa_promotion_gate_dashboard.py; "
    "python script/36_build_direct_read_audit_bundle.py; "
    "python script/14_validate_workspace.py"
)

MANIFEST_COLUMNS = [
    "download_rank",
    "country",
    "wave",
    "idno",
    "official_get_microdata_url",
    "local_target_folder",
    "target_readme_path",
    "target_readme_sha256",
    "expected_file_rows",
    "missing_expected_file_rows",
    "priority_core_file_rows",
    "requirement_rows",
    "blocked_requirement_rows",
    "ready_requirement_rows",
    "top_expected_files",
    "post_download_commands",
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


def rel(path: Path) -> str:
    try:
        return str(path.relative_to(PROJECT_ROOT)).replace("\\", "/")
    except ValueError:
        return str(path).replace("\\", "/")


def resolve_project_path(path_text: str) -> Path:
    text = clean(path_text).replace("\\", "/").strip("/")
    path = Path(text)
    if path.is_absolute():
        return path
    return PROJECT_ROOT / text


def rows_by_id(rows: list[dict[str, str]]) -> dict[str, list[dict[str, str]]]:
    grouped: dict[str, list[dict[str, str]]] = {}
    for row in rows:
        idno = clean(row.get("idno"))
        if idno:
            grouped.setdefault(idno, []).append(row)
    return grouped


def markdown_table(rows: list[dict[str, str]], columns: list[str], limit: int = 35) -> str:
    if not rows:
        return "_No rows._"
    lines = ["| " + " | ".join(columns) + " |", "| " + " | ".join("---" for _ in columns) + " |"]
    for row in rows[:limit]:
        values: list[str] = []
        for column in columns:
            value = clean(row.get(column)).replace("|", "/")
            if len(value) > 90:
                value = value[:87] + "..."
            values.append(value)
        lines.append("| " + " | ".join(values) + " |")
    if len(rows) > limit:
        lines.append("| " + " | ".join("..." for _ in columns) + " |")
    return "\n".join(lines)


def unique_join(values: list[str], limit: int = 12) -> str:
    seen: list[str] = []
    for value in values:
        text = clean(value)
        if text and text not in seen:
            seen.append(text)
    if len(seen) > limit:
        return ";".join(seen[:limit] + [f"...{len(seen) - limit} more"])
    return ";".join(seen)


def write_target_readme(
    board_row: dict[str, str],
    file_rows: list[dict[str, str]],
    requirement_rows: list[dict[str, str]],
) -> Path:
    target_folder = resolve_project_path(board_row.get("local_target_folder", ""))
    target_folder.mkdir(parents=True, exist_ok=True)
    readme_path = target_folder / TARGET_README_NAME

    missing_files = [row for row in file_rows if row.get("acceptance_gate_status") == "missing_required_official_file"]
    priority_files = [row for row in missing_files if row.get("priority_core_target") == "1"]
    blocked_requirements = [row for row in requirement_rows if row.get("requirement_acceptance_status") == "blocked_missing_core_files"]

    lines = [
        f"# Download Acceptance: {clean(board_row.get('idno'))}",
        "",
        "This folder is the local target for one complete official World Bank raw package.",
        "Keep original downloaded filenames intact. Do not put cleaned or analysis-ready files here.",
        "",
        "## Target",
        "",
        f"- Country: {clean(board_row.get('country'))}",
        f"- Wave: {clean(board_row.get('wave'))}",
        f"- IDNO: {clean(board_row.get('idno'))}",
        f"- Official get-microdata URL: {clean(board_row.get('official_get_microdata_url'))}",
        f"- Local target folder: `{clean(board_row.get('local_target_folder'))}`",
        "",
        "## Current Acceptance Counts",
        "",
        f"- Expected official files: {len(file_rows)}",
        f"- Missing expected files: {len(missing_files)}",
        f"- Requirement rows: {len(requirement_rows)}",
        f"- Blocked requirement rows: {len(blocked_requirements)}",
        "",
        "## Minimum Action",
        "",
        "Download the complete unchanged official package and documentation through the permitted World Bank account and terms workflow, then place the files or original archive in this folder.",
        "",
        "After placing files, rerun:",
        "",
        f"`{POST_DOWNLOAD_COMMANDS}`",
        "",
        "## Requirement Gates",
        "",
        markdown_table(requirement_rows, ["requirement", "core_file_rows", "core_missing_file_rows", "requirement_acceptance_status"], 20),
        "",
        "## Priority Core Files",
        "",
        markdown_table(priority_files, ["file_id", "expected_file_name", "core_requirements", "core_top_variable_names", "acceptance_gate_status"], 40),
        "",
        "## Guardrails",
        "",
        "- This README is local handoff metadata, not raw data.",
        "- `data/` remains blocked until raw receipt, schema, value, semantics, climate, and promotion gates pass.",
        "- Models remain blocked until the registry reaches the required 6-country and 10-wave thresholds.",
    ]
    readme_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return readme_path


def build_manifest(
    board_rows: list[dict[str, str]],
    file_rows_by_id: dict[str, list[dict[str, str]]],
    requirement_rows_by_id: dict[str, list[dict[str, str]]],
) -> list[dict[str, str]]:
    manifest: list[dict[str, str]] = []
    for board in sorted(board_rows, key=lambda row: safe_int(row.get("download_rank"), 9999)):
        idno = clean(board.get("idno"))
        file_rows = file_rows_by_id.get(idno, [])
        requirement_rows = requirement_rows_by_id.get(idno, [])
        readme_path = write_target_readme(board, file_rows, requirement_rows)
        missing_files = [row for row in file_rows if row.get("acceptance_gate_status") == "missing_required_official_file"]
        priority_core = [row for row in file_rows if row.get("priority_core_target") == "1"]
        blocked_requirements = [row for row in requirement_rows if row.get("requirement_acceptance_status") == "blocked_missing_core_files"]
        ready_requirements = [row for row in requirement_rows if row.get("requirement_acceptance_status") == "ready_for_raw_value_review"]
        manifest.append(
            {
                "download_rank": clean(board.get("download_rank")),
                "country": clean(board.get("country")),
                "wave": clean(board.get("wave")),
                "idno": idno,
                "official_get_microdata_url": clean(board.get("official_get_microdata_url")),
                "local_target_folder": clean(board.get("local_target_folder")),
                "target_readme_path": rel(readme_path),
                "target_readme_sha256": sha256_file(readme_path),
                "expected_file_rows": str(len(file_rows)),
                "missing_expected_file_rows": str(len(missing_files)),
                "priority_core_file_rows": str(len(priority_core)),
                "requirement_rows": str(len(requirement_rows)),
                "blocked_requirement_rows": str(len(blocked_requirements)),
                "ready_requirement_rows": str(len(ready_requirements)),
                "top_expected_files": unique_join([row.get("expected_file_name", "") for row in priority_core], limit=20),
                "post_download_commands": POST_DOWNLOAD_COMMANDS,
                "data_write_gate_status": "blocked_no_data_write",
                "modeling_gate_status": "blocked",
            }
        )
    return manifest


def summary_row(metric: str, value: Any, interpretation: str) -> dict[str, str]:
    return {"metric": metric, "value": str(value), "interpretation": interpretation}


def build_summary(manifest_rows: list[dict[str, str]]) -> list[dict[str, str]]:
    return [
        summary_row("local_target_readme_rows", len(manifest_rows), "Per-target local README files generated."),
        summary_row("local_target_readme_expected_file_rows", sum(safe_int(row.get("expected_file_rows")) for row in manifest_rows), "Expected official files covered by target-folder README files."),
        summary_row("local_target_readme_missing_expected_file_rows", sum(safe_int(row.get("missing_expected_file_rows")) for row in manifest_rows), "Expected official files still missing across target folders."),
        summary_row("local_target_readme_requirement_rows", sum(safe_int(row.get("requirement_rows")) for row in manifest_rows), "Requirement rows covered by target-folder README files."),
        summary_row("local_target_readme_blocked_requirement_rows", sum(safe_int(row.get("blocked_requirement_rows")) for row in manifest_rows), "Requirement rows still blocked by missing files."),
        summary_row("local_target_readme_ready_requirement_rows", sum(safe_int(row.get("ready_requirement_rows")) for row in manifest_rows), "Requirement rows ready for raw value review."),
        summary_row("data_write_gate_status", "blocked_no_data_write", "Target-folder readmes are local handoff metadata and never write promoted data."),
        summary_row("modeling_gate_status", "blocked", "No predictive, reduced-form, causal ML, or policy learning until registry thresholds pass."),
    ]


def write_report(manifest_rows: list[dict[str, str]], summary_rows: list[dict[str, str]]) -> None:
    metric = {row["metric"]: row["value"] for row in summary_rows}
    lines = [
        "# Priority LSMS-ISA Local Target Readmes",
        "",
        "Status: local target-folder handoff readmes generated for the 10 remaining minimum-batch downloads.",
        "",
        "The readmes are written under `temp/raw_downloads/<IDNO>/`, which is intentionally excluded from Git. This report and manifest record the generated paths, hashes, counts, and post-download commands for review.",
        "",
        "## Summary",
        "",
        f"- Target readmes: {metric.get('local_target_readme_rows', '0')}",
        f"- Expected official files covered: {metric.get('local_target_readme_expected_file_rows', '0')}",
        f"- Missing expected files: {metric.get('local_target_readme_missing_expected_file_rows', '0')}",
        f"- Requirement rows: {metric.get('local_target_readme_requirement_rows', '0')}",
        f"- Blocked requirement rows: {metric.get('local_target_readme_blocked_requirement_rows', '0')}",
        f"- Ready requirement rows: {metric.get('local_target_readme_ready_requirement_rows', '0')}",
        f"- Data-write gate: {metric.get('data_write_gate_status', 'missing')}",
        f"- Modeling gate: {metric.get('modeling_gate_status', 'missing')}",
        "",
        "## Manifest",
        "",
        markdown_table(manifest_rows, ["download_rank", "country", "wave", "idno", "target_readme_path", "expected_file_rows", "missing_expected_file_rows", "requirement_rows", "blocked_requirement_rows"], 20),
    ]
    REPORT_PATH.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    ensure_dirs()
    board_rows = read_csv_dicts(BOARD_PATH)
    file_rows_by_id = rows_by_id(read_csv_dicts(FILE_MATRIX_PATH))
    requirement_rows_by_id = rows_by_id(read_csv_dicts(REQUIREMENT_MATRIX_PATH))
    manifest_rows = build_manifest(board_rows, file_rows_by_id, requirement_rows_by_id)
    summary_rows = build_summary(manifest_rows)

    write_csv(MANIFEST_PATH, manifest_rows, MANIFEST_COLUMNS)
    write_csv(SUMMARY_PATH, summary_rows, SUMMARY_COLUMNS)
    write_report(manifest_rows, summary_rows)
    append_log(TEMP_DIR / "audit_log.md", f"Built priority LSMS/ISA local target readmes: {len(manifest_rows)} target folders.")


if __name__ == "__main__":
    main()
