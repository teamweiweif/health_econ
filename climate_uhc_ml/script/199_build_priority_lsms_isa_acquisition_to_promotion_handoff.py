from __future__ import annotations

import csv
from pathlib import Path
from typing import Any

from common import REPORT_DIR, RESULT_DIR, TEMP_DIR, append_log, ensure_dirs, write_csv


REGISTRY_PATH = RESULT_DIR / "promoted_country_wave_registry.csv"
RAW_PRESENCE_PATH = RESULT_DIR / "priority_lsms_isa_local_raw_presence_audit.csv"
EXECUTION_BOARD_PATH = TEMP_DIR / "priority_lsms_isa_manual_download_execution_board.csv"

HANDOFF_PATH = RESULT_DIR / "priority_lsms_isa_acquisition_to_promotion_handoff.csv"
GATE_CHECKLIST_PATH = RESULT_DIR / "priority_lsms_isa_acquisition_to_promotion_gate_checklist.csv"
SUMMARY_PATH = RESULT_DIR / "priority_lsms_isa_acquisition_to_promotion_handoff_summary.csv"
REPORT_PATH = REPORT_DIR / "priority_lsms_isa_acquisition_to_promotion_handoff.md"

VERIFICATION_GATES = [
    ("complete_original_raw_package", "Complete unchanged official raw package and documentation are locally present."),
    ("household_person_merge_keys", "Household/person IDs, uniqueness, and merge levels are raw-verified."),
    ("household_weights_survey_design", "Weights, strata, PSU/cluster, and design variables are raw-verified."),
    ("consumption_or_income_aggregate", "Total consumption or income aggregate is raw-verified."),
    ("oop_health_expenditure", "OOP health expenditure variables, units, and recall periods are raw-verified."),
    ("illness_need_care_access", "Illness/need and care-seeking/access variables are raw-verified."),
    ("survey_timing", "Survey month/date or fieldwork timing is raw-verified."),
    ("geography_climate_anchor", "GPS, cluster, EA, or admin geography is raw-verified for climate linkage."),
    ("missing_units_recall_skip_patterns", "Missing codes, units, recall periods, and skip patterns are reviewed."),
    ("climate_linkage_route", "CHIRPS or ERA5 linkage route is accepted for the verified geography/timing."),
    ("promotion_packet_registry", "Country-wave promotion packet and promoted registry row are refreshed."),
]

HANDOFF_COLUMNS = [
    "country",
    "wave",
    "idno",
    "priority_country",
    "minimum_batch_row",
    "official_url",
    "local_target_folder",
    "analysis_ready_status",
    "raw_like_file_count",
    "local_raw_presence_status",
    "handoff_stage",
    "next_required_action",
    "manual_download_action",
    "post_placement_validation_sequence",
    "promotion_refresh_sequence",
    "expected_full_file_rows",
    "core_file_rows",
    "requirements_covered",
    "data_write_gate_status",
    "modeling_gate_status",
]

GATE_COLUMNS = [
    "country",
    "wave",
    "idno",
    "minimum_batch_row",
    "verification_gate",
    "gate_description",
    "gate_status",
    "gate_blocker",
    "next_action",
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


def by_id(rows: list[dict[str, str]]) -> dict[str, dict[str, str]]:
    return {clean(row.get("idno")): row for row in rows if clean(row.get("idno"))}


def stage_for(analysis_ready: str, raw_count: int) -> str:
    if analysis_ready == "promoted_analysis_ready":
        return "promoted_keep_current"
    if raw_count > 0:
        return "run_receipt_schema_value_semantics_validation"
    return "acquire_official_raw_package"


def generic_validation_sequence(idno: str, minimum_batch: bool) -> str:
    if minimum_batch:
        return "; ".join(
            [
                "python script/177_build_priority_lsms_isa_manual_download_progress_tracker.py",
                "python script/198_build_priority_lsms_isa_local_raw_presence_audit.py",
                f"python script/178_build_priority_lsms_isa_post_download_validation_runner.py --idno {idno}",
                f"python script/178_build_priority_lsms_isa_post_download_validation_runner.py --idno {idno} --execute",
            ]
        )
    return "; ".join(
        [
            "python script/17_audit_raw_downloads.py",
            "python script/150_build_priority_lsms_isa_raw_package_receipt_checklist.py",
            "python script/153_validate_priority_lsms_isa_official_file_receipt.py",
            "python script/157_build_priority_lsms_isa_received_raw_schema_audit.py",
            "python script/158_build_priority_lsms_isa_received_raw_value_profile.py",
            "python script/159_build_priority_lsms_isa_received_raw_semantics_review.py",
        ]
    )


def promotion_refresh_sequence() -> str:
    return "; ".join(
        [
            "python script/173_build_priority_lsms_isa_promotion_gate_dashboard.py",
            "python script/148_build_priority_lsms_isa_country_wave_promotion_packets.py",
            "python script/151_refresh_refocused_promoted_country_wave_registry.py",
            "python script/127_enforce_promoted_data_gate.py",
            "python script/36_build_direct_read_audit_bundle.py",
            "python script/14_validate_workspace.py",
        ]
    )


def gate_status(stage: str) -> tuple[str, str, str]:
    if stage == "promoted_keep_current":
        return ("passed_current_promoted_scope", "", "Keep current promoted registry row; do not run models.")
    if stage == "run_receipt_schema_value_semantics_validation":
        return (
            "ready_for_raw_validation",
            "Raw-like files are present but receipt/schema/value/semantics gates are not accepted yet.",
            "Run the post-placement validation sequence before any data write.",
        )
    return (
        "blocked_raw_package_absent",
        "Complete unchanged official raw package is not locally present.",
        "Download or manually place the complete official raw package and documentation.",
    )


def build_outputs() -> tuple[list[dict[str, str]], list[dict[str, str]], list[dict[str, str]]]:
    registry_rows = read_csv_dicts(REGISTRY_PATH)
    raw_by_id = by_id(read_csv_dicts(RAW_PRESENCE_PATH))
    board_by_id = by_id(read_csv_dicts(EXECUTION_BOARD_PATH))
    handoff_rows: list[dict[str, str]] = []
    gate_rows: list[dict[str, str]] = []

    for registry in registry_rows:
        idno = clean(registry.get("idno"))
        raw = raw_by_id.get(idno, {})
        board = board_by_id.get(idno, {})
        minimum_batch = clean(raw.get("minimum_batch_row")) == "1" or bool(board)
        raw_count = safe_int(raw.get("raw_like_file_count"))
        analysis_ready = clean(registry.get("analysis_ready_status"))
        stage = stage_for(analysis_ready, raw_count)
        official_url = clean(registry.get("official_url")) or clean(board.get("official_get_microdata_url"))
        local_target = clean(registry.get("local_target_folder")) or clean(board.get("local_target_folder"))
        if stage == "promoted_keep_current":
            next_action = "Keep promoted dataset and registry; no modeling until threshold is met."
            manual_action = ""
        elif stage == "run_receipt_schema_value_semantics_validation":
            next_action = "Run receipt, schema, value-profile, semantics, timing/geography, and climate-linkage gates."
            manual_action = ""
        else:
            next_action = "Download or manually place the complete unchanged official raw package and documentation."
            manual_action = clean(board.get("manual_download_action")) or f"Open {official_url}, accept official terms if required, and place all files under {local_target}."

        handoff_rows.append(
            {
                "country": clean(registry.get("country")),
                "wave": clean(registry.get("wave")),
                "idno": idno,
                "priority_country": clean(registry.get("priority_country")),
                "minimum_batch_row": "1" if minimum_batch else "0",
                "official_url": official_url,
                "local_target_folder": local_target,
                "analysis_ready_status": analysis_ready,
                "raw_like_file_count": str(raw_count),
                "local_raw_presence_status": clean(raw.get("local_raw_presence_status")),
                "handoff_stage": stage,
                "next_required_action": next_action,
                "manual_download_action": manual_action,
                "post_placement_validation_sequence": generic_validation_sequence(idno, minimum_batch),
                "promotion_refresh_sequence": promotion_refresh_sequence(),
                "expected_full_file_rows": clean(board.get("expected_full_file_rows")),
                "core_file_rows": clean(board.get("core_file_rows")),
                "requirements_covered": clean(board.get("requirements_covered")),
                "data_write_gate_status": "blocked_no_data_write" if stage != "promoted_keep_current" else "open_only_for_existing_promoted_scope",
                "modeling_gate_status": "blocked",
            }
        )

        status, blocker, action = gate_status(stage)
        for gate, description in VERIFICATION_GATES:
            gate_rows.append(
                {
                    "country": clean(registry.get("country")),
                    "wave": clean(registry.get("wave")),
                    "idno": idno,
                    "minimum_batch_row": "1" if minimum_batch else "0",
                    "verification_gate": gate,
                    "gate_description": description,
                    "gate_status": status,
                    "gate_blocker": blocker,
                    "next_action": action,
                }
            )

    stage_counts = {stage: sum(1 for row in handoff_rows if row["handoff_stage"] == stage) for stage in sorted({row["handoff_stage"] for row in handoff_rows})}
    minimum_acquire = sum(1 for row in handoff_rows if row["minimum_batch_row"] == "1" and row["handoff_stage"] == "acquire_official_raw_package")
    summary = [
        {"metric": "acquisition_to_promotion_handoff_rows", "value": str(len(handoff_rows)), "interpretation": "Registry country-waves mapped to the next acquisition or promotion stage."},
        {"metric": "acquisition_to_promotion_gate_rows", "value": str(len(gate_rows)), "interpretation": "Verification-gate checklist rows across registry country-waves."},
        {"metric": "acquisition_to_promotion_minimum_batch_acquire_rows", "value": str(minimum_acquire), "interpretation": "Minimum-batch rows still requiring official raw package acquisition."},
        {"metric": "acquisition_to_promotion_promoted_keep_current_rows", "value": str(stage_counts.get("promoted_keep_current", 0)), "interpretation": "Rows already promoted and held in place."},
        {"metric": "acquisition_to_promotion_raw_validation_ready_rows", "value": str(stage_counts.get("run_receipt_schema_value_semantics_validation", 0)), "interpretation": "Rows with raw-like files present but validation still required."},
        {"metric": "acquisition_to_promotion_acquire_raw_rows", "value": str(stage_counts.get("acquire_official_raw_package", 0)), "interpretation": "Rows still blocked at raw acquisition."},
        {"metric": "data_write_gate_status", "value": "blocked_no_new_data_write", "interpretation": "No new promoted data writes are opened by this handoff."},
        {"metric": "modeling_gate_status", "value": "blocked", "interpretation": "No predictive, reduced-form, causal ML, or policy learning is opened."},
    ]
    return handoff_rows, gate_rows, summary


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


def write_report(handoff_rows: list[dict[str, str]], gate_rows: list[dict[str, str]], summary: list[dict[str, str]]) -> None:
    REPORT_PATH.write_text(
        f"""# Priority LSMS/ISA Acquisition-to-Promotion Handoff

Status: executable handoff from raw-package acquisition to receipt,
raw-value, climate-linkage, promotion-packet, and registry-refresh gates.

It does not download, copy, extract, write promoted `data/`, or run models.

## Summary

{markdown_table(summary, ['metric', 'value', 'interpretation'], 20)}

## Handoff Rows

{markdown_table(handoff_rows, ['country', 'wave', 'idno', 'minimum_batch_row', 'raw_like_file_count', 'handoff_stage', 'next_required_action'], 25)}

## Gate Checklist Preview

{markdown_table(gate_rows, ['idno', 'verification_gate', 'gate_status', 'gate_blocker'], 40)}

## Outputs

- `result/priority_lsms_isa_acquisition_to_promotion_handoff.csv`
- `result/priority_lsms_isa_acquisition_to_promotion_gate_checklist.csv`
- `result/priority_lsms_isa_acquisition_to_promotion_handoff_summary.csv`

## Stop Rule

This handoff is not a promotion decision. A country-wave can enter `data/` only
after all required receipt, raw-value, semantics, timing/geography, and
climate-linkage gates pass and the promoted registry is refreshed.
""",
        encoding="utf-8",
    )


def main() -> None:
    ensure_dirs()
    handoff_rows, gate_rows, summary = build_outputs()
    write_csv(HANDOFF_PATH, handoff_rows, HANDOFF_COLUMNS)
    write_csv(GATE_CHECKLIST_PATH, gate_rows, GATE_COLUMNS)
    write_csv(SUMMARY_PATH, summary, SUMMARY_COLUMNS)
    write_report(handoff_rows, gate_rows, summary)
    append_log(TEMP_DIR / "audit_log.md", f"Built priority LSMS/ISA acquisition-to-promotion handoff rows={len(handoff_rows)}.")
    print(f"Priority LSMS/ISA acquisition-to-promotion handoff complete: rows={len(handoff_rows)}, gate_rows={len(gate_rows)}.")


if __name__ == "__main__":
    main()
