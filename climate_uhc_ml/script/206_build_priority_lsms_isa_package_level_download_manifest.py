from __future__ import annotations

import csv
from collections import defaultdict
from pathlib import Path
from typing import Any

from common import PROJECT_ROOT, REPORT_DIR, RESULT_DIR, TEMP_DIR, append_log, ensure_dirs, write_csv


LAUNCHPAD_PATH = RESULT_DIR / "priority_lsms_isa_manual_download_launchpad.csv"
FILE_MATRIX_PATH = TEMP_DIR / "priority_lsms_isa_download_acceptance_file_matrix.csv"
REQUIREMENT_MATRIX_PATH = TEMP_DIR / "priority_lsms_isa_download_acceptance_requirement_matrix.csv"

PACKAGE_MANIFEST_PATH = RESULT_DIR / "priority_lsms_isa_package_level_download_manifest.csv"
CORE_FILE_MANIFEST_PATH = RESULT_DIR / "priority_lsms_isa_package_level_core_file_manifest.csv"
SUMMARY_PATH = RESULT_DIR / "priority_lsms_isa_package_level_download_manifest_summary.csv"
REPORT_PATH = REPORT_DIR / "priority_lsms_isa_package_level_download_manifest.md"

PACKAGE_COLUMNS = [
    "download_rank",
    "country",
    "wave",
    "idno",
    "catalog_id",
    "official_get_microdata_url",
    "credentialed_download_url",
    "local_target_folder",
    "target_folder_exists",
    "target_file_count",
    "incoming_file_rows",
    "expected_full_file_rows",
    "expected_core_file_rows",
    "unique_core_file_rows",
    "expected_requirement_gate_rows",
    "blocked_requirement_gate_rows",
    "package_receipt_status",
    "required_package_scope",
    "package_placement_rule",
    "receipt_validation_chain",
    "first_core_file_names",
    "requirements_covered",
    "data_write_gate_status",
    "modeling_gate_status",
]

CORE_COLUMNS = [
    "download_rank",
    "country",
    "wave",
    "idno",
    "catalog_id",
    "expected_file_name",
    "file_description",
    "core_requirements",
    "core_top_variable_names",
    "package_receipt_status",
    "post_download_acceptance_action",
    "data_write_gate_status",
    "modeling_gate_status",
]

SUMMARY_COLUMNS = ["metric", "value", "interpretation"]

POST_DOWNLOAD_VALIDATION_CHAIN = (
    "python script/150_build_priority_lsms_isa_raw_package_receipt_checklist.py; "
    "python script/153_validate_priority_lsms_isa_official_file_receipt.py; "
    "python script/157_build_priority_lsms_isa_received_raw_schema_audit.py; "
    "python script/158_build_priority_lsms_isa_received_raw_value_profile.py; "
    "python script/159_build_priority_lsms_isa_received_raw_semantics_review.py; "
    "python script/178_build_priority_lsms_isa_post_download_validation_runner.py --idno {idno}; "
    "python script/205_build_priority_lsms_isa_post_download_receipt_handoff.py"
)


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


def rel_exists(path_text: str) -> str:
    if not path_text:
        return "0"
    path = PROJECT_ROOT / path_text
    return "1" if path.exists() else "0"


def status_for(target_files: int, incoming_files: int) -> str:
    if target_files > 0:
        return "local_package_or_files_present_run_receipt_validation"
    if incoming_files > 0:
        return "incoming_package_present_route_before_validation"
    return "blocked_no_local_package_or_incoming_files"


def group_by_id(rows: list[dict[str, str]]) -> dict[str, list[dict[str, str]]]:
    out: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in rows:
        idno = clean(row.get("idno"))
        if idno:
            out[idno].append(row)
    return out


def build_outputs() -> tuple[list[dict[str, str]], list[dict[str, str]], list[dict[str, str]]]:
    launch_rows = sorted(read_csv_dicts(LAUNCHPAD_PATH), key=lambda row: safe_int(row.get("launch_rank"), 9999))
    file_rows_by_id = group_by_id(read_csv_dicts(FILE_MATRIX_PATH))
    req_rows_by_id = group_by_id(read_csv_dicts(REQUIREMENT_MATRIX_PATH))

    packages: list[dict[str, str]] = []
    core_files: list[dict[str, str]] = []
    for launch in launch_rows:
        idno = clean(launch.get("idno"))
        target_files = safe_int(launch.get("target_file_count"))
        incoming_files = safe_int(launch.get("incoming_file_rows"))
        receipt_status = status_for(target_files, incoming_files)
        all_file_rows = file_rows_by_id.get(idno, [])
        core_rows = [row for row in all_file_rows if clean(row.get("priority_core_target")) == "1"]
        req_rows = req_rows_by_id.get(idno, [])
        expected_core_rows = safe_int(launch.get("expected_core_file_rows"))
        blocked_requirements = sum(1 for row in req_rows if clean(row.get("requirement_acceptance_status")) == "blocked_missing_core_files")
        first_core_names = ";".join(clean(row.get("expected_file_name")) for row in core_rows[:12])

        packages.append(
            {
                "download_rank": clean(launch.get("launch_rank")),
                "country": clean(launch.get("country")),
                "wave": clean(launch.get("wave")),
                "idno": idno,
                "catalog_id": clean(launch.get("catalog_id")),
                "official_get_microdata_url": clean(launch.get("official_get_microdata_url")),
                "credentialed_download_url": clean(launch.get("credentialed_download_url")),
                "local_target_folder": clean(launch.get("local_target_folder")),
                "target_folder_exists": rel_exists(clean(launch.get("local_target_folder"))),
                "target_file_count": str(target_files),
                "incoming_file_rows": str(incoming_files),
                "expected_full_file_rows": clean(launch.get("expected_full_file_rows")),
                "expected_core_file_rows": str(expected_core_rows),
                "unique_core_file_rows": str(len(core_rows)),
                "expected_requirement_gate_rows": str(len(req_rows)),
                "blocked_requirement_gate_rows": str(blocked_requirements),
                "package_receipt_status": receipt_status,
                "required_package_scope": "complete_unchanged_official_world_bank_microdata_package_plus_documentation",
                "package_placement_rule": f"After accepting official terms, place the downloaded package or extracted official files under {clean(launch.get('local_target_folder'))}; if the target is uncertain, place the package under temp/raw_downloads/_incoming/ first.",
                "receipt_validation_chain": POST_DOWNLOAD_VALIDATION_CHAIN.format(idno=idno),
                "first_core_file_names": first_core_names,
                "requirements_covered": clean(launch.get("requirements_covered")),
                "data_write_gate_status": "blocked_no_data_write",
                "modeling_gate_status": "blocked",
            }
        )

        for row in core_rows:
            core_files.append(
                {
                    "download_rank": clean(launch.get("launch_rank")),
                    "country": clean(launch.get("country")),
                    "wave": clean(launch.get("wave")),
                    "idno": idno,
                    "catalog_id": clean(launch.get("catalog_id")),
                    "expected_file_name": clean(row.get("expected_file_name")),
                    "file_description": clean(row.get("file_description")),
                    "core_requirements": clean(row.get("core_requirements")),
                    "core_top_variable_names": clean(row.get("core_top_variable_names")),
                    "package_receipt_status": receipt_status,
                    "post_download_acceptance_action": clean(row.get("post_download_acceptance_action")),
                    "data_write_gate_status": "blocked_no_data_write",
                    "modeling_gate_status": "blocked",
                }
            )

    countries = {row["country"] for row in packages if row.get("country")}
    priority_countries = {"Ethiopia", "Nigeria", "Malawi", "Tanzania", "Uganda"}
    summary = [
        {"metric": "package_level_download_manifest_rows", "value": str(len(packages)), "interpretation": "Package-level rows for locked download-required country-waves."},
        {"metric": "package_level_download_country_rows", "value": str(len(countries)), "interpretation": "Countries covered by the package-level manifest."},
        {"metric": "package_level_download_priority_country_rows", "value": str(sum(1 for row in packages if row.get("country") in priority_countries)), "interpretation": "Package-level rows from the five priority countries."},
        {"metric": "package_level_download_sixth_country_rows", "value": str(sum(1 for row in packages if row.get("country") not in priority_countries)), "interpretation": "Package-level rows supplying the sixth-country buffer."},
        {"metric": "package_level_download_expected_full_file_rows", "value": str(sum(safe_int(row.get("expected_full_file_rows")) for row in packages)), "interpretation": "Expected official file rows after complete packages are placed or extracted."},
        {"metric": "package_level_download_expected_core_file_rows", "value": str(sum(safe_int(row.get("expected_core_file_rows")) for row in packages)), "interpretation": "Requirement-linked core file rows after complete packages are placed or extracted."},
        {"metric": "package_level_download_unique_core_file_manifest_rows", "value": str(len(core_files)), "interpretation": "Unique expected core files represented in the package-level core manifest."},
        {"metric": "package_level_download_requirement_gate_rows", "value": str(sum(safe_int(row.get("expected_requirement_gate_rows")) for row in packages)), "interpretation": "Requirement-level gates covered by package receipt."},
        {"metric": "package_level_download_blocked_requirement_gate_rows", "value": str(sum(safe_int(row.get("blocked_requirement_gate_rows")) for row in packages)), "interpretation": "Requirement gates blocked until complete package receipt."},
        {"metric": "package_level_download_target_file_rows", "value": str(sum(safe_int(row.get("target_file_count")) for row in packages)), "interpretation": "Files currently present under exact target folders."},
        {"metric": "package_level_download_incoming_file_rows", "value": str(max((safe_int(row.get("incoming_file_rows")) for row in packages), default=0)), "interpretation": "Files currently staged under temp/raw_downloads/_incoming."},
        {"metric": "package_level_download_blocked_no_local_package_rows", "value": str(sum(1 for row in packages if row.get("package_receipt_status") == "blocked_no_local_package_or_incoming_files")), "interpretation": "Package rows still lacking local package or incoming files."},
        {"metric": "package_level_download_first_canary_idno", "value": packages[0]["idno"] if packages else "", "interpretation": "First package to download and validate before scaling."},
        {"metric": "data_write_gate_status", "value": "blocked_no_data_write", "interpretation": "The manifest does not write promoted data."},
        {"metric": "modeling_gate_status", "value": "blocked", "interpretation": "No predictive, reduced-form, causal ML, or policy learning is opened."},
    ]
    return packages, core_files, summary


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
        lines.append("| " + " | ".join("..." for _ in columns) + " |")
    return "\n".join(lines)


def write_report(packages: list[dict[str, str]], core_files: list[dict[str, str]], summary: list[dict[str, str]]) -> None:
    REPORT_PATH.write_text(
        f"""# Priority LSMS/ISA Package-Level Download Manifest

Status: package-level download and receipt manifest for the 10 locked
World Bank LSMS/ISA targets that still need official raw packages.

This is the practical download view. The expected-file matrix has 838 official
file rows and 323 core rows, but the acquisition action is to download each
complete official microdata package after accepting World Bank terms, then
place it unchanged in the target folder or under `_incoming` for routing.

The manifest does not download files, extract archives, write `data/`, or open
any modeling gate.

## Summary

{markdown_table(summary, ['metric', 'value', 'interpretation'], 20)}

## Package Rows

{markdown_table(packages, ['download_rank', 'country', 'wave', 'idno', 'package_receipt_status', 'target_file_count', 'incoming_file_rows', 'expected_full_file_rows', 'expected_core_file_rows', 'unique_core_file_rows', 'expected_requirement_gate_rows'], 20)}

## Core File Preview

{markdown_table(core_files, ['download_rank', 'idno', 'expected_file_name', 'core_requirements', 'package_receipt_status'], 50)}

## Receipt Rule

Download the complete unchanged official package for each row. If the browser
download name is not known in advance, keep the original downloaded archive name
and place it in the target folder listed in the manifest. After local placement,
run the receipt validation chain before any extraction-derived promotion,
value-review, climate-linkage, or data-write step.
""",
        encoding="utf-8",
    )


def main() -> None:
    ensure_dirs()
    packages, core_files, summary = build_outputs()
    write_csv(PACKAGE_MANIFEST_PATH, packages, PACKAGE_COLUMNS)
    write_csv(CORE_FILE_MANIFEST_PATH, core_files, CORE_COLUMNS)
    write_csv(SUMMARY_PATH, summary, SUMMARY_COLUMNS)
    write_report(packages, core_files, summary)
    append_log(TEMP_DIR / "audit_log.md", f"Built priority LSMS/ISA package-level download manifest rows={len(packages)} core_rows={len(core_files)}.")
    print(f"Priority LSMS/ISA package-level download manifest rows={len(packages)} core_rows={len(core_files)}.")


if __name__ == "__main__":
    main()
