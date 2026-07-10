from __future__ import annotations

import csv
from pathlib import Path
from typing import Any

from common import REPORT_DIR, RESULT_DIR, TEMP_DIR, append_log, ensure_dirs, write_csv


THRESHOLD_BATCH_PATH = TEMP_DIR / "priority_lsms_isa_threshold_minimum_batch.csv"
MANUAL_BOARD_PATH = TEMP_DIR / "priority_lsms_isa_manual_download_execution_board.csv"
REGISTRY_PATH = RESULT_DIR / "promoted_country_wave_registry.csv"
RAW_PRESENCE_PATH = RESULT_DIR / "priority_lsms_isa_local_raw_presence_audit.csv"
UNLOCK_BOARD_PATH = RESULT_DIR / "priority_lsms_isa_minimum_batch_promotion_unlock_board.csv"
ENDPOINT_STATUS_PATH = TEMP_DIR / "priority_lsms_isa_minimum_batch_endpoint_dataset_status.csv"
REPLACEMENT_SUMMARY_PATH = RESULT_DIR / "priority_lsms_isa_threshold_replacement_plan_summary.csv"

SCOPE_PATH = RESULT_DIR / "priority_lsms_isa_dataset_scope_lock.csv"
GATE_MATRIX_PATH = RESULT_DIR / "priority_lsms_isa_dataset_scope_lock_gate_matrix.csv"
SUMMARY_PATH = RESULT_DIR / "priority_lsms_isa_dataset_scope_lock_summary.csv"
REPORT_PATH = REPORT_DIR / "priority_lsms_isa_dataset_scope_lock.md"

PRIORITY_COUNTRIES = {"Ethiopia", "Nigeria", "Malawi", "Tanzania", "Uganda"}
TARGET_COUNTRY_THRESHOLD = 6
TARGET_WAVE_THRESHOLD = 10

SCOPE_COLUMNS = [
    "scope_rank",
    "country",
    "wave",
    "idno",
    "scope_role",
    "priority_country",
    "download_required",
    "current_promoted_anchor",
    "analysis_ready_status",
    "raw_like_file_count",
    "local_raw_presence_status",
    "unlock_status",
    "endpoint_refresh_status",
    "credentialed_download_required",
    "official_get_microdata_url",
    "local_target_folder",
    "target_status",
    "next_action",
    "data_write_gate_status",
    "modeling_gate_status",
]

GATE_COLUMNS = [
    "gate_name",
    "country_rows",
    "country_wave_rows",
    "priority_country_wave_rows",
    "nonpriority_country_wave_rows",
    "promoted_analysis_ready_rows",
    "download_required_rows",
    "raw_missing_download_required_rows",
    "country_threshold_status",
    "wave_threshold_status",
    "interpretation",
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


def by_id(rows: list[dict[str, str]]) -> dict[str, dict[str, str]]:
    return {clean(row.get("idno")): row for row in rows if clean(row.get("idno"))}


def summary_value(rows: list[dict[str, str]], metric: str, default: str = "0") -> str:
    return next((clean(row.get("value")) for row in rows if clean(row.get("metric")) == metric), default)


def is_promoted(row: dict[str, str]) -> bool:
    return clean(row.get("analysis_ready_status")) == "promoted_analysis_ready"


def country_count(rows: list[dict[str, str]]) -> int:
    return len({clean(row.get("country")) for row in rows if clean(row.get("country"))})


def threshold_status(value: int, threshold: int) -> str:
    return "passes" if value >= threshold else f"fails_short_by_{threshold - value}"


def scope_role(batch_row: dict[str, str], manual_ids: set[str], registry_row: dict[str, str]) -> str:
    idno = clean(batch_row.get("idno"))
    country = clean(batch_row.get("country"))
    if is_promoted(registry_row):
        return "current_promoted_anchor"
    if idno in manual_ids and country not in PRIORITY_COUNTRIES:
        return "download_required_sixth_country_candidate"
    if idno in manual_ids:
        return "download_required_priority_country_wave"
    return "threshold_context_row"


def build_scope_rows() -> list[dict[str, str]]:
    threshold_rows = read_csv_dicts(THRESHOLD_BATCH_PATH)
    manual_by_id = by_id(read_csv_dicts(MANUAL_BOARD_PATH))
    registry_by_id = by_id(read_csv_dicts(REGISTRY_PATH))
    raw_by_id = by_id(read_csv_dicts(RAW_PRESENCE_PATH))
    unlock_by_id = by_id(read_csv_dicts(UNLOCK_BOARD_PATH))
    endpoint_by_id = by_id(read_csv_dicts(ENDPOINT_STATUS_PATH))
    manual_ids = set(manual_by_id)

    rows: list[dict[str, str]] = []
    for rank, batch in enumerate(sorted(threshold_rows, key=lambda row: safe_int(row.get("threshold_sequence_rank"), 9999)), start=1):
        idno = clean(batch.get("idno"))
        country = clean(batch.get("country"))
        manual = manual_by_id.get(idno, {})
        registry = registry_by_id.get(idno, {})
        raw = raw_by_id.get(idno, {})
        unlock = unlock_by_id.get(idno, {})
        endpoint = endpoint_by_id.get(idno, {})
        role = scope_role(batch, manual_ids, registry)
        promoted = is_promoted(registry)
        download_required = idno in manual_ids and not promoted
        raw_count = safe_int(raw.get("raw_like_file_count"))
        if promoted:
            target_status = "implemented_promoted_anchor"
            next_action = "Keep promoted row current; do not use it to open modeling thresholds alone."
        elif download_required and raw_count == 0:
            target_status = "blocked_download_required_raw_absent"
            next_action = "Acquire the complete unchanged official raw package and documentation, then rerun post-download validation."
        elif download_required:
            target_status = "raw_present_needs_receipt_value_climate_promotion_gates"
            next_action = "Run receipt, archive, schema, value, semantics, timing/geography, climate-linkage, and promotion-packet gates."
        else:
            target_status = "context_only_not_in_current_download_board"
            next_action = "Use only as threshold context unless the execution board is refreshed."

        rows.append(
            {
                "scope_rank": str(rank),
                "country": country,
                "wave": clean(batch.get("wave")),
                "idno": idno,
                "scope_role": role,
                "priority_country": "1" if country in PRIORITY_COUNTRIES else "0",
                "download_required": "1" if download_required else "0",
                "current_promoted_anchor": "1" if promoted else "0",
                "analysis_ready_status": clean(registry.get("analysis_ready_status")),
                "raw_like_file_count": str(raw_count),
                "local_raw_presence_status": clean(raw.get("local_raw_presence_status")),
                "unlock_status": clean(unlock.get("unlock_status")),
                "endpoint_refresh_status": clean(endpoint.get("endpoint_refresh_status")),
                "credentialed_download_required": clean(endpoint.get("credentialed_download_required")),
                "official_get_microdata_url": clean(manual.get("official_get_microdata_url")) or clean(batch.get("official_get_microdata_url")),
                "local_target_folder": clean(manual.get("local_target_folder")) or clean(batch.get("local_target_folder")),
                "target_status": target_status,
                "next_action": next_action,
                "data_write_gate_status": "blocked_no_data_write",
                "modeling_gate_status": "blocked",
            }
        )
    return rows


def gate_row(name: str, rows: list[dict[str, str]], interpretation: str) -> dict[str, str]:
    countries = country_count(rows)
    waves = len(rows)
    priority_rows = sum(1 for row in rows if row.get("priority_country") == "1")
    promoted_rows = sum(1 for row in rows if row.get("current_promoted_anchor") == "1")
    download_rows = sum(1 for row in rows if row.get("download_required") == "1")
    raw_missing_download = sum(
        1
        for row in rows
        if row.get("download_required") == "1" and safe_int(row.get("raw_like_file_count")) == 0
    )
    return {
        "gate_name": name,
        "country_rows": str(countries),
        "country_wave_rows": str(waves),
        "priority_country_wave_rows": str(priority_rows),
        "nonpriority_country_wave_rows": str(waves - priority_rows),
        "promoted_analysis_ready_rows": str(promoted_rows),
        "download_required_rows": str(download_rows),
        "raw_missing_download_required_rows": str(raw_missing_download),
        "country_threshold_status": threshold_status(countries, TARGET_COUNTRY_THRESHOLD),
        "wave_threshold_status": threshold_status(waves, TARGET_WAVE_THRESHOLD),
        "interpretation": interpretation,
        "data_write_gate_status": "blocked_no_data_write",
        "modeling_gate_status": "blocked",
    }


def build_gate_matrix(scope_rows: list[dict[str, str]]) -> list[dict[str, str]]:
    promoted = [row for row in scope_rows if row.get("current_promoted_anchor") == "1"]
    download_required = [row for row in scope_rows if row.get("download_required") == "1"]
    priority_only = [row for row in scope_rows if row.get("priority_country") == "1"]
    locked_scope = list(scope_rows)
    if_nepal_removed = [row for row in scope_rows if clean(row.get("country")) != "Nepal"]
    return [
        gate_row(
            "current_implemented_promoted_registry",
            promoted,
            "Current implemented scope only; this is not enough for multi-country modeling or the target dataset.",
        ),
        gate_row(
            "manual_download_required_execution_board",
            download_required,
            "The 10 packages that still need official raw acquisition before promotion can proceed.",
        ),
        gate_row(
            "strict_five_priority_countries_only",
            priority_only,
            "The five priority countries can supply 10 waves only if all pass, but they still fail the six-country threshold.",
        ),
        gate_row(
            "locked_threshold_scope_with_sixth_country",
            locked_scope,
            "The locked target scope reaches six countries and has an 11-wave buffer only if all gated waves pass.",
        ),
        gate_row(
            "scope_if_nepal_sixth_country_removed",
            if_nepal_removed,
            "Removing Nepal leaves 10 priority-country waves but only five countries, so a replacement sixth country is required.",
        ),
    ]


def build_summary(scope_rows: list[dict[str, str]], gate_rows: list[dict[str, str]]) -> list[dict[str, str]]:
    replacement_summary = read_csv_dicts(REPLACEMENT_SUMMARY_PATH)
    locked_countries = country_count(scope_rows)
    locked_waves = len(scope_rows)
    promoted_rows = sum(1 for row in scope_rows if row.get("current_promoted_anchor") == "1")
    download_required = sum(1 for row in scope_rows if row.get("download_required") == "1")
    download_missing_raw = sum(
        1
        for row in scope_rows
        if row.get("download_required") == "1" and safe_int(row.get("raw_like_file_count")) == 0
    )
    priority_rows = sum(1 for row in scope_rows if row.get("priority_country") == "1")
    priority_countries = len({row["country"] for row in scope_rows if row.get("priority_country") == "1"})
    years = [clean(row.get("wave")) for row in scope_rows if clean(row.get("wave"))]
    return [
        {"metric": "dataset_scope_lock_rows", "value": str(locked_waves), "interpretation": "Locked target country-wave rows in the threshold scope."},
        {"metric": "dataset_scope_lock_country_rows", "value": str(locked_countries), "interpretation": "Countries represented if all locked target rows pass promotion gates."},
        {"metric": "dataset_scope_lock_priority_country_rows", "value": str(priority_countries), "interpretation": "Priority countries represented in the locked scope."},
        {"metric": "dataset_scope_lock_priority_country_wave_rows", "value": str(priority_rows), "interpretation": "Locked target rows from Ethiopia, Nigeria, Malawi, Tanzania, and Uganda."},
        {"metric": "dataset_scope_lock_nonpriority_country_wave_rows", "value": str(locked_waves - priority_rows), "interpretation": "Locked target rows outside the five priority countries."},
        {"metric": "dataset_scope_lock_download_required_rows", "value": str(download_required), "interpretation": "Rows still requiring official raw-package acquisition."},
        {"metric": "dataset_scope_lock_promoted_anchor_rows", "value": str(promoted_rows), "interpretation": "Rows already promoted and serving as current anchors."},
        {"metric": "dataset_scope_lock_raw_missing_download_required_rows", "value": str(download_missing_raw), "interpretation": "Download-required rows with no local raw-like files yet."},
        {"metric": "dataset_scope_lock_wave_period_min", "value": min(years) if years else "", "interpretation": "Earliest wave label in the locked target scope."},
        {"metric": "dataset_scope_lock_wave_period_max", "value": max(years) if years else "", "interpretation": "Latest wave label in the locked target scope."},
        {"metric": "dataset_scope_lock_gate_matrix_rows", "value": str(len(gate_rows)), "interpretation": "Scenario/gate rows explaining implemented, download-required, priority-only, and sixth-country scope."},
        {"metric": "dataset_scope_lock_replacement_backup_candidate_rows", "value": summary_value(replacement_summary, "priority_lsms_replacement_backup_candidate_rows", "0"), "interpretation": "Backup candidates available if the locked sixth-country or priority waves fail."},
        {"metric": "data_write_gate_status", "value": "blocked_no_data_write", "interpretation": "Scope lock writes only audit artifacts and does not promote datasets."},
        {"metric": "modeling_gate_status", "value": "blocked", "interpretation": "No predictive, reduced-form, causal ML, or policy learning is opened."},
    ]


def markdown_table(rows: list[dict[str, str]], columns: list[str], limit: int = 40) -> str:
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


def write_report(scope_rows: list[dict[str, str]], gate_rows: list[dict[str, str]], summary_rows: list[dict[str, str]]) -> None:
    REPORT_PATH.write_text(
        f"""# Priority LSMS/ISA Dataset Scope Lock

Status: locked target scope for the dataset-promotion campaign.

This artifact answers what dataset is being built before any new modeling:
the target is a six-country, 11-country-wave LSMS/ISA-centered household
microdata scope, with one current promoted anchor and 10 official raw packages
still requiring acquisition and validation.

It does not download, copy, extract, write promoted `data/`, or run models.

## Summary

{markdown_table(summary_rows, ['metric', 'value', 'interpretation'], 30)}

## Gate Matrix

{markdown_table(gate_rows, ['gate_name', 'country_rows', 'country_wave_rows', 'priority_country_wave_rows', 'nonpriority_country_wave_rows', 'promoted_analysis_ready_rows', 'download_required_rows', 'raw_missing_download_required_rows', 'country_threshold_status', 'wave_threshold_status'], 10)}

## Locked Scope Rows

{markdown_table(scope_rows, ['scope_rank', 'country', 'wave', 'idno', 'scope_role', 'download_required', 'current_promoted_anchor', 'target_status'], 20)}

## Interpretation

- Implemented now: Malawi 2004-2005 is the only promoted analysis-ready anchor.
- Still required: 10 official raw packages must be acquired and pass receipt,
  schema, raw-value, semantics, timing/geography, climate-linkage, and
  promotion-packet gates.
- Priority-country only scope reaches 10 waves but only five countries.
- Nepal is the current sixth-country candidate; if it fails, the replacement
  plan must supply another non-priority country.
- Modeling remains blocked.
""",
        encoding="utf-8",
    )


def main() -> None:
    ensure_dirs()
    scope_rows = build_scope_rows()
    gate_rows = build_gate_matrix(scope_rows)
    summary_rows = build_summary(scope_rows, gate_rows)
    write_csv(SCOPE_PATH, scope_rows, SCOPE_COLUMNS)
    write_csv(GATE_MATRIX_PATH, gate_rows, GATE_COLUMNS)
    write_csv(SUMMARY_PATH, summary_rows, SUMMARY_COLUMNS)
    write_report(scope_rows, gate_rows, summary_rows)
    append_log(TEMP_DIR / "audit_log.md", f"Built priority LSMS/ISA dataset scope lock rows={len(scope_rows)}.")
    print(f"Priority LSMS/ISA dataset scope lock rows={len(scope_rows)} gate_rows={len(gate_rows)}.")


if __name__ == "__main__":
    main()
