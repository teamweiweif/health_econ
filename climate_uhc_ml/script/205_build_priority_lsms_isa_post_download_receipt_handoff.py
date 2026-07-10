from __future__ import annotations

import csv
from collections import defaultdict
from typing import Any

from common import REPORT_DIR, RESULT_DIR, TEMP_DIR, append_log, ensure_dirs, write_csv


LAUNCHPAD_PATH = RESULT_DIR / "priority_lsms_isa_manual_download_launchpad.csv"
PROGRESS_PATH = TEMP_DIR / "priority_lsms_isa_manual_download_progress_tracker.csv"
FILE_MATRIX_PATH = TEMP_DIR / "priority_lsms_isa_download_acceptance_file_matrix.csv"
REQUIREMENT_MATRIX_PATH = TEMP_DIR / "priority_lsms_isa_download_acceptance_requirement_matrix.csv"
TARGET_README_MANIFEST_PATH = TEMP_DIR / "priority_lsms_isa_local_target_readme_manifest.csv"

HANDOFF_PATH = RESULT_DIR / "priority_lsms_isa_post_download_receipt_handoff.csv"
REQUIREMENT_GATE_PATH = RESULT_DIR / "priority_lsms_isa_post_download_receipt_requirement_gate.csv"
SUMMARY_PATH = RESULT_DIR / "priority_lsms_isa_post_download_receipt_handoff_summary.csv"
REPORT_PATH = REPORT_DIR / "priority_lsms_isa_post_download_receipt_handoff.md"

POST_DOWNLOAD_SEQUENCE = (
    "python script/177_build_priority_lsms_isa_manual_download_progress_tracker.py; "
    "python script/178_build_priority_lsms_isa_post_download_validation_runner.py --idno {idno}; "
    "python script/178_build_priority_lsms_isa_post_download_validation_runner.py --idno {idno} --execute; "
    "python script/182_build_priority_lsms_isa_download_acceptance_matrix.py; "
    "python script/183_build_priority_lsms_isa_local_target_readmes.py; "
    "python script/199_build_priority_lsms_isa_acquisition_to_promotion_handoff.py; "
    "python script/200_build_priority_lsms_isa_dataset_scope_lock.py; "
    "python script/201_build_priority_lsms_isa_acquisition_route_decision.py; "
    "python script/202_build_priority_lsms_isa_scoped_incoming_package_router.py; "
    "python script/203_build_priority_lsms_isa_webgpt_download_control_manifest.py; "
    "python script/204_build_priority_lsms_isa_manual_download_launchpad.py; "
    "python script/205_build_priority_lsms_isa_post_download_receipt_handoff.py; "
    "python script/36_build_direct_read_audit_bundle.py; "
    "python script/14_validate_workspace.py"
)

HANDOFF_COLUMNS = [
    "download_rank",
    "country",
    "wave",
    "idno",
    "catalog_id",
    "official_get_microdata_url",
    "local_target_folder",
    "launchpad_html_path",
    "target_readme_path",
    "current_progress_status",
    "target_file_count",
    "incoming_file_rows",
    "expected_file_rows",
    "missing_expected_file_rows",
    "present_expected_file_rows",
    "requirement_gate_rows",
    "blocked_requirement_rows",
    "ready_requirement_rows",
    "expected_core_file_rows",
    "missing_core_file_rows",
    "post_download_receipt_status",
    "first_validation_command",
    "execute_validation_command",
    "canonical_post_download_sequence",
    "next_action",
    "promotion_unlock_condition",
    "data_write_gate_status",
    "modeling_gate_status",
]

REQUIREMENT_COLUMNS = [
    "download_rank",
    "country",
    "wave",
    "idno",
    "requirement",
    "core_file_rows",
    "core_matched_file_rows",
    "core_missing_file_rows",
    "unique_expected_core_files",
    "top_variable_names",
    "requirement_acceptance_status",
    "post_download_requirement_action",
    "data_write_gate_status",
    "modeling_gate_status",
]

SUMMARY_COLUMNS = ["metric", "value", "interpretation"]


def read_csv_dicts(path) -> list[dict[str, str]]:
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


def by_id(rows: list[dict[str, str]]) -> dict[str, dict[str, str]]:
    out: dict[str, dict[str, str]] = {}
    for row in rows:
        idno = clean(row.get("idno"))
        if idno and idno not in out:
            out[idno] = row
    return out


def group_by_id(rows: list[dict[str, str]]) -> dict[str, list[dict[str, str]]]:
    out: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in rows:
        idno = clean(row.get("idno"))
        if idno:
            out[idno].append(row)
    return out


def status_for(target_files: int, missing_expected: int, blocked_requirements: int) -> str:
    if target_files == 0:
        return "blocked_no_target_files"
    if missing_expected > 0:
        return "blocked_missing_expected_official_files"
    if blocked_requirements > 0:
        return "blocked_requirement_core_files_missing"
    return "receipt_ready_for_raw_value_semantics_review"


def build_outputs() -> tuple[list[dict[str, str]], list[dict[str, str]], list[dict[str, str]]]:
    launch_rows = sorted(read_csv_dicts(LAUNCHPAD_PATH), key=lambda row: safe_int(row.get("launch_rank"), 9999))
    progress_by_id = by_id(read_csv_dicts(PROGRESS_PATH))
    readme_by_id = by_id(read_csv_dicts(TARGET_README_MANIFEST_PATH))
    files_by_id = group_by_id(read_csv_dicts(FILE_MATRIX_PATH))
    requirements_by_id = group_by_id(read_csv_dicts(REQUIREMENT_MATRIX_PATH))

    handoff: list[dict[str, str]] = []
    requirement_gate: list[dict[str, str]] = []
    for launch in launch_rows:
        idno = clean(launch.get("idno"))
        progress = progress_by_id.get(idno, {})
        readme = readme_by_id.get(idno, {})
        file_rows = files_by_id.get(idno, [])
        req_rows = requirements_by_id.get(idno, [])
        expected_files = len(file_rows)
        missing_expected = sum(1 for row in file_rows if clean(row.get("acceptance_gate_status")) == "missing_required_official_file")
        present_expected = sum(1 for row in file_rows if clean(row.get("acceptance_gate_status")) == "present_needs_raw_value_review")
        blocked_requirements = sum(1 for row in req_rows if clean(row.get("requirement_acceptance_status")) == "blocked_missing_core_files")
        ready_requirements = sum(1 for row in req_rows if clean(row.get("requirement_acceptance_status")) == "ready_for_raw_value_review")
        expected_core = sum(safe_int(row.get("core_file_rows")) for row in req_rows)
        missing_core = sum(safe_int(row.get("core_missing_file_rows")) for row in req_rows)
        target_files = safe_int(progress.get("target_file_count")) or safe_int(launch.get("target_file_count"))
        incoming_files = safe_int(progress.get("incoming_route_rows")) or safe_int(launch.get("incoming_file_rows"))
        receipt_status = status_for(target_files, missing_expected, blocked_requirements)
        validation_dry_run = f"python script/178_build_priority_lsms_isa_post_download_validation_runner.py --idno {idno}"
        validation_execute = f"python script/178_build_priority_lsms_isa_post_download_validation_runner.py --idno {idno} --execute"

        handoff.append(
            {
                "download_rank": clean(launch.get("launch_rank")),
                "country": clean(launch.get("country")),
                "wave": clean(launch.get("wave")),
                "idno": idno,
                "catalog_id": clean(launch.get("catalog_id")),
                "official_get_microdata_url": clean(launch.get("official_get_microdata_url")),
                "local_target_folder": clean(launch.get("local_target_folder")),
                "launchpad_html_path": "report/priority_lsms_isa_manual_download_launchpad.html",
                "target_readme_path": clean(readme.get("target_readme_path")),
                "current_progress_status": clean(progress.get("progress_status")) or "not_in_progress_tracker",
                "target_file_count": str(target_files),
                "incoming_file_rows": str(incoming_files),
                "expected_file_rows": str(expected_files),
                "missing_expected_file_rows": str(missing_expected),
                "present_expected_file_rows": str(present_expected),
                "requirement_gate_rows": str(len(req_rows)),
                "blocked_requirement_rows": str(blocked_requirements),
                "ready_requirement_rows": str(ready_requirements),
                "expected_core_file_rows": str(expected_core),
                "missing_core_file_rows": str(missing_core),
                "post_download_receipt_status": receipt_status,
                "first_validation_command": validation_dry_run,
                "execute_validation_command": validation_execute,
                "canonical_post_download_sequence": POST_DOWNLOAD_SEQUENCE.format(idno=idno),
                "next_action": "Place the complete official raw package in the target folder, then run the first validation command." if target_files == 0 else "Run receipt and requirement validation; do not promote until all gates pass.",
                "promotion_unlock_condition": "No missing expected files, no missing requirement-linked core files, raw values/semantics/timing/geography accepted, and promotion packet refreshed.",
                "data_write_gate_status": "blocked_no_data_write",
                "modeling_gate_status": "blocked",
            }
        )

        for req in sorted(req_rows, key=lambda row: clean(row.get("requirement"))):
            requirement_gate.append(
                {
                    "download_rank": clean(launch.get("launch_rank")),
                    "country": clean(launch.get("country")),
                    "wave": clean(launch.get("wave")),
                    "idno": idno,
                    "requirement": clean(req.get("requirement")),
                    "core_file_rows": clean(req.get("core_file_rows")),
                    "core_matched_file_rows": clean(req.get("core_matched_file_rows")),
                    "core_missing_file_rows": clean(req.get("core_missing_file_rows")),
                    "unique_expected_core_files": clean(req.get("unique_expected_core_files")),
                    "top_variable_names": clean(req.get("top_variable_names")),
                    "requirement_acceptance_status": clean(req.get("requirement_acceptance_status")),
                    "post_download_requirement_action": clean(req.get("post_download_requirement_action")),
                    "data_write_gate_status": "blocked_no_data_write",
                    "modeling_gate_status": "blocked",
                }
            )

    countries = {row["country"] for row in handoff if row.get("country")}
    summary = [
        {"metric": "post_download_receipt_handoff_rows", "value": str(len(handoff)), "interpretation": "Post-download receipt handoff rows for locked download-required waves."},
        {"metric": "post_download_receipt_country_rows", "value": str(len(countries)), "interpretation": "Countries covered by the post-download handoff."},
        {"metric": "post_download_receipt_priority_country_rows", "value": str(sum(1 for row in handoff if row.get("country") in {"Ethiopia", "Nigeria", "Malawi", "Tanzania", "Uganda"})), "interpretation": "Rows from priority countries."},
        {"metric": "post_download_receipt_sixth_country_rows", "value": str(sum(1 for row in handoff if row.get("country") not in {"Ethiopia", "Nigeria", "Malawi", "Tanzania", "Uganda"})), "interpretation": "Rows supplying the sixth country."},
        {"metric": "post_download_receipt_expected_file_rows", "value": str(sum(safe_int(row.get("expected_file_rows")) for row in handoff)), "interpretation": "Expected official file rows across handoff targets."},
        {"metric": "post_download_receipt_missing_expected_file_rows", "value": str(sum(safe_int(row.get("missing_expected_file_rows")) for row in handoff)), "interpretation": "Expected official file rows currently missing."},
        {"metric": "post_download_receipt_requirement_gate_rows", "value": str(len(requirement_gate)), "interpretation": "Requirement-level gates exported for direct review."},
        {"metric": "post_download_receipt_blocked_requirement_rows", "value": str(sum(1 for row in requirement_gate if row.get("requirement_acceptance_status") == "blocked_missing_core_files")), "interpretation": "Requirement gates blocked by missing core files."},
        {"metric": "post_download_receipt_ready_requirement_rows", "value": str(sum(1 for row in requirement_gate if row.get("requirement_acceptance_status") == "ready_for_raw_value_review")), "interpretation": "Requirement gates whose core files are present."},
        {"metric": "post_download_receipt_expected_core_file_rows", "value": str(sum(safe_int(row.get("core_file_rows")) for row in requirement_gate)), "interpretation": "Requirement-linked core file rows in the handoff."},
        {"metric": "post_download_receipt_missing_core_file_rows", "value": str(sum(safe_int(row.get("core_missing_file_rows")) for row in requirement_gate)), "interpretation": "Requirement-linked core file rows currently missing."},
        {"metric": "post_download_receipt_target_file_rows", "value": str(sum(safe_int(row.get("target_file_count")) for row in handoff)), "interpretation": "Files currently present under exact target folders."},
        {"metric": "post_download_receipt_incoming_file_rows", "value": str(max((safe_int(row.get("incoming_file_rows")) for row in handoff), default=0)), "interpretation": "Files currently staged under temp/raw_downloads/_incoming."},
        {"metric": "post_download_receipt_blocked_no_target_files_rows", "value": str(sum(1 for row in handoff if row.get("post_download_receipt_status") == "blocked_no_target_files")), "interpretation": "Handoff rows still blocked because target folders contain no files."},
        {"metric": "data_write_gate_status", "value": "blocked_no_data_write", "interpretation": "The handoff does not write promoted data."},
        {"metric": "modeling_gate_status", "value": "blocked", "interpretation": "No predictive, reduced-form, causal ML, or policy learning is opened."},
    ]
    return handoff, requirement_gate, summary


def markdown_table(rows: list[dict[str, str]], columns: list[str], limit: int = 30) -> str:
    if not rows:
        return "_No rows._"
    lines = ["| " + " | ".join(columns) + " |", "| " + " | ".join("---" for _ in columns) + " |"]
    for row in rows[:limit]:
        values: list[str] = []
        for column in columns:
            value = clean(row.get(column)).replace("|", "/")
            if len(value) > 110:
                value = value[:107] + "..."
            values.append(value)
        lines.append("| " + " | ".join(values) + " |")
    if len(rows) > limit:
        lines.append("| " + " | ".join("..." for _ in columns) + " |")
    return "\n".join(lines)


def write_report(handoff: list[dict[str, str]], requirement_gate: list[dict[str, str]], summary: list[dict[str, str]]) -> None:
    REPORT_PATH.write_text(
        f"""# Priority LSMS/ISA Post-Download Receipt Handoff

Status: direct-read post-download handoff for the 10 locked World Bank LSMS/ISA
packages.

This artifact starts where the manual download launchpad stops. It tells the
reviewer what receipt and requirement gates must pass after a complete official
raw package is placed in the target folder. It does not download, copy, delete,
extract, write `data/`, or promote country-waves.

## Summary

{markdown_table(summary, ['metric', 'value', 'interpretation'], 25)}

## Handoff Rows

{markdown_table(handoff, ['download_rank', 'country', 'wave', 'idno', 'post_download_receipt_status', 'expected_file_rows', 'missing_expected_file_rows', 'requirement_gate_rows', 'blocked_requirement_rows'], 20)}

## Requirement Gate Preview

{markdown_table(requirement_gate, ['download_rank', 'idno', 'requirement', 'core_file_rows', 'core_missing_file_rows', 'requirement_acceptance_status'], 50)}

## Stop Rule

Receipt handoff completion is not promotion. A country-wave can only enter
`data/` after the official package receipt, raw schema, raw value, semantics,
timing/geography, climate-linkage, and country-wave promotion-packet gates all
pass.
""",
        encoding="utf-8",
    )


def main() -> None:
    ensure_dirs()
    handoff, requirement_gate, summary = build_outputs()
    write_csv(HANDOFF_PATH, handoff, HANDOFF_COLUMNS)
    write_csv(REQUIREMENT_GATE_PATH, requirement_gate, REQUIREMENT_COLUMNS)
    write_csv(SUMMARY_PATH, summary, SUMMARY_COLUMNS)
    write_report(handoff, requirement_gate, summary)
    append_log(TEMP_DIR / "audit_log.md", f"Built priority LSMS/ISA post-download receipt handoff rows={len(handoff)} requirement_rows={len(requirement_gate)}.")
    print(f"Priority LSMS/ISA post-download receipt handoff rows={len(handoff)} requirement_rows={len(requirement_gate)}.")


if __name__ == "__main__":
    main()
