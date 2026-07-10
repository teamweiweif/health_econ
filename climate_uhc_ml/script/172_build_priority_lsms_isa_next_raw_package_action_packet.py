from __future__ import annotations

import csv
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

from common import REPORT_DIR, RESULT_DIR, TEMP_DIR, append_log, ensure_dirs, write_csv


QUEUE_PATH = TEMP_DIR / "priority_lsms_isa_refocused_acquisition_queue.csv"
MINIMUM_BATCH_PATH = TEMP_DIR / "priority_lsms_isa_threshold_minimum_batch.csv"
CORE_CHECKLIST_PATH = TEMP_DIR / "priority_lsms_isa_credentialed_raw_core_file_checklist.csv"
FULL_MANIFEST_PATH = TEMP_DIR / "priority_lsms_isa_credentialed_raw_full_file_manifest.csv"
REGISTRY_PATH = RESULT_DIR / "promoted_country_wave_registry.csv"
ENDPOINT_SUMMARY_PATH = RESULT_DIR / "priority_lsms_isa_minimum_batch_endpoint_refresh_summary.csv"

ACTION_QUEUE_PATH = TEMP_DIR / "priority_lsms_isa_next_raw_package_action_queue.csv"
CORE_FILES_PATH = TEMP_DIR / "priority_lsms_isa_next_raw_package_core_files.csv"
SUMMARY_PATH = RESULT_DIR / "priority_lsms_isa_next_raw_package_action_summary.csv"
REPORT_PATH = REPORT_DIR / "priority_lsms_isa_next_raw_package_action_packet.md"

ACTION_COLUMNS = [
    "action_rank",
    "acquisition_tier",
    "country",
    "wave",
    "idno",
    "official_get_microdata_url",
    "local_target_folder",
    "registry_analysis_ready_status",
    "registry_rows",
    "current_receipt_status",
    "credentialed_download_required",
    "full_official_file_rows",
    "unique_core_files_required",
    "core_requirement_rows",
    "missing_core_file_rows",
    "reason_for_priority",
    "next_action",
    "post_download_validation_commands",
]

CORE_COLUMNS = [
    "action_rank",
    "acquisition_tier",
    "country",
    "wave",
    "idno",
    "requirement",
    "file_rank",
    "file_name",
    "file_description",
    "candidate_variable_rows",
    "strong_candidate_variable_rows",
    "top_variable_names",
    "current_receipt_status",
    "local_target_folder",
    "post_download_validation_commands",
]

SUMMARY_COLUMNS = ["metric", "value", "interpretation"]

VALIDATION_COMMANDS = (
    "python script/150_build_priority_lsms_isa_raw_package_receipt_checklist.py; "
    "python script/153_validate_priority_lsms_isa_official_file_receipt.py; "
    "python script/157_build_priority_lsms_isa_received_raw_schema_audit.py; "
    "python script/158_build_priority_lsms_isa_received_raw_value_profile.py; "
    "python script/159_build_priority_lsms_isa_received_raw_semantics_review.py"
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


def summary_value(rows: list[dict[str, str]], metric: str, default: str = "0") -> str:
    for row in rows:
        if clean(row.get("metric")) == metric:
            return clean(row.get("value")) or default
    return default


def one_by_id(rows: list[dict[str, str]], field: str = "idno") -> dict[str, dict[str, str]]:
    out: dict[str, dict[str, str]] = {}
    for row in rows:
        idno = clean(row.get(field))
        if idno and idno not in out:
            out[idno] = row
    return out


def by_id(rows: list[dict[str, str]], field: str = "idno") -> dict[str, list[dict[str, str]]]:
    out: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in rows:
        idno = clean(row.get(field))
        if idno:
            out[idno].append(row)
    return out


def local_target_folder(queue_row: dict[str, str], idno: str) -> str:
    folder = clean(queue_row.get("local_target_folder"))
    return folder if folder else f"temp/raw_downloads/{idno}/"


def core_unique_files(rows: list[dict[str, str]]) -> set[str]:
    return {clean(row.get("file_name")) for row in rows if clean(row.get("file_name"))}


def markdown_table(rows: list[dict[str, str]], columns: list[str], limit: int = 30) -> str:
    if not rows:
        return "_No rows._"
    lines = ["| " + " | ".join(columns) + " |", "| " + " | ".join("---" for _ in columns) + " |"]
    for row in rows[:limit]:
        lines.append("| " + " | ".join(clean(row.get(column)).replace("|", "/") for column in columns) + " |")
    if len(rows) > limit:
        lines.append("| " + " | ".join("..." for _ in columns) + " |")
    return "\n".join(lines)


def build_outputs() -> tuple[list[dict[str, str]], list[dict[str, str]], list[dict[str, str]]]:
    queue_rows = read_csv_dicts(QUEUE_PATH)
    minimum_rows = read_csv_dicts(MINIMUM_BATCH_PATH)
    core_rows_by_id = by_id(read_csv_dicts(CORE_CHECKLIST_PATH))
    full_rows_by_id = by_id(read_csv_dicts(FULL_MANIFEST_PATH))
    registry_by_id = one_by_id(read_csv_dicts(REGISTRY_PATH))
    endpoint_summary = read_csv_dicts(ENDPOINT_SUMMARY_PATH)
    queue_by_id = one_by_id(queue_rows)

    minimum_ids = [clean(row.get("idno")) for row in minimum_rows if clean(row.get("idno"))]
    minimum_rank = {idno: idx for idx, idno in enumerate(minimum_ids, start=1)}
    promoted_ids = {
        idno
        for idno, row in registry_by_id.items()
        if clean(row.get("analysis_ready_status")) == "promoted_analysis_ready" and safe_int(row.get("rows")) > 0
    }

    ordered_ids = [
        idno
        for idno in minimum_ids
        if idno not in promoted_ids
    ]
    backup_ids = [
        clean(row.get("idno"))
        for row in queue_rows
        if clean(row.get("idno")) and clean(row.get("idno")) not in set(minimum_ids) and clean(row.get("idno")) not in promoted_ids
    ]
    ordered_ids.extend(backup_ids)

    action_rows: list[dict[str, str]] = []
    core_file_rows: list[dict[str, str]] = []
    for action_rank, idno in enumerate(ordered_ids, start=1):
        queue = queue_by_id.get(idno, {})
        registry = registry_by_id.get(idno, {})
        core_rows = core_rows_by_id.get(idno, [])
        full_rows = full_rows_by_id.get(idno, [])
        unique_core = core_unique_files(core_rows)
        missing_core = sum(1 for row in core_rows if clean(row.get("current_receipt_status")) != "ready_for_raw_value_review")
        tier = "minimum_batch_remaining" if idno in minimum_rank else "backup_after_minimum_batch"
        reason = (
            "Needed to reach the 6-country and 10-country-wave raw-value/climate-linkage threshold if it passes verification."
            if tier == "minimum_batch_remaining"
            else "Backup wave if a minimum-batch country-wave fails raw-value, outcome, timing, or climate-linkage gates."
        )
        row = {
            "action_rank": str(action_rank),
            "acquisition_tier": tier,
            "country": clean(queue.get("country")),
            "wave": clean(queue.get("wave")),
            "idno": idno,
            "official_get_microdata_url": clean(queue.get("official_get_microdata_url")),
            "local_target_folder": local_target_folder(queue, idno),
            "registry_analysis_ready_status": clean(registry.get("analysis_ready_status")) or "not_promoted",
            "registry_rows": clean(registry.get("rows")) or "0",
            "current_receipt_status": clean(registry.get("raw_package_status")) or "blocked_no_original_package",
            "credentialed_download_required": "1",
            "full_official_file_rows": str(len(full_rows)),
            "unique_core_files_required": str(len(unique_core)),
            "core_requirement_rows": str(len(core_rows)),
            "missing_core_file_rows": str(missing_core),
            "reason_for_priority": reason,
            "next_action": "Login/register at the official World Bank Microdata get-microdata page, accept terms if required, download the complete unchanged official raw package and documentation, and place every file under the local target folder.",
            "post_download_validation_commands": VALIDATION_COMMANDS,
        }
        action_rows.append(row)
        for core in sorted(core_rows, key=lambda r: (clean(r.get("requirement")), safe_int(r.get("file_rank")))):
            core_file_rows.append(
                {
                    "action_rank": str(action_rank),
                    "acquisition_tier": tier,
                    "country": row["country"],
                    "wave": row["wave"],
                    "idno": idno,
                    "requirement": clean(core.get("requirement")),
                    "file_rank": clean(core.get("file_rank")),
                    "file_name": clean(core.get("file_name")),
                    "file_description": clean(core.get("file_description")),
                    "candidate_variable_rows": clean(core.get("candidate_variable_rows")),
                    "strong_candidate_variable_rows": clean(core.get("strong_candidate_variable_rows")),
                    "top_variable_names": clean(core.get("top_variable_names")),
                    "current_receipt_status": clean(core.get("current_receipt_status")) or "blocked_no_original_package",
                    "local_target_folder": row["local_target_folder"],
                    "post_download_validation_commands": VALIDATION_COMMANDS,
                }
            )

    tier_counts = Counter(row["acquisition_tier"] for row in action_rows)
    current_promoted_rows = [
        row
        for row in registry_by_id.values()
        if clean(row.get("analysis_ready_status")) == "promoted_analysis_ready" and safe_int(row.get("rows")) > 0
    ]
    countries_after_minimum = {
        clean(row.get("country"))
        for row in current_promoted_rows
        if clean(row.get("country"))
    }
    for row in action_rows:
        if row["acquisition_tier"] == "minimum_batch_remaining" and clean(row.get("country")):
            countries_after_minimum.add(row["country"])
    summary_rows = [
        {"metric": "next_raw_package_action_rows", "value": str(len(action_rows)), "interpretation": "Country-waves requiring raw package acquisition or backup acquisition action."},
        {"metric": "minimum_batch_remaining_action_rows", "value": str(tier_counts.get("minimum_batch_remaining", 0)), "interpretation": "Unpromoted minimum-batch waves still needing complete official raw packages."},
        {"metric": "backup_after_minimum_action_rows", "value": str(tier_counts.get("backup_after_minimum_batch", 0)), "interpretation": "Backup waves queued after the minimum batch."},
        {"metric": "core_file_action_rows", "value": str(len(core_file_rows)), "interpretation": "Requirement-file rows to verify after raw packages are placed."},
        {"metric": "unique_core_files_remaining_minimum_batch", "value": str(sum(safe_int(row["unique_core_files_required"]) for row in action_rows if row["acquisition_tier"] == "minimum_batch_remaining")), "interpretation": "Sum of per-wave unique core files in the remaining minimum batch."},
        {"metric": "current_promoted_analysis_ready_rows", "value": str(len(current_promoted_rows)), "interpretation": "Current promoted registry rows before additional raw acquisition."},
        {"metric": "current_promoted_country_rows", "value": str(len({clean(row.get("country")) for row in current_promoted_rows if clean(row.get("country"))})), "interpretation": "Current promoted countries before additional raw acquisition."},
        {"metric": "countries_if_minimum_batch_passes", "value": str(len(countries_after_minimum)), "interpretation": "Countries covered if current promoted rows plus remaining minimum batch all pass verification."},
        {"metric": "country_waves_if_minimum_batch_passes", "value": str(len(current_promoted_rows) + tier_counts.get("minimum_batch_remaining", 0)), "interpretation": "Country-waves covered if current promoted rows plus remaining minimum batch all pass verification."},
        {"metric": "official_raw_download_candidate_rows", "value": summary_value(endpoint_summary, "priority_lsms_minimum_endpoint_raw_download_candidate_rows", "0"), "interpretation": "Current endpoint-refresh raw download candidates; zero means login/terms workflow remains required."},
        {"metric": "credentialed_download_required_rows", "value": summary_value(endpoint_summary, "priority_lsms_minimum_endpoint_credentialed_download_required_rows", "0"), "interpretation": "Minimum-batch waves whose current get-microdata page requires credentialed access."},
        {"metric": "data_write_gate_status", "value": "blocked_raw_package_acquisition_required", "interpretation": "This packet only controls raw acquisition; it does not permit promoted data writes."},
        {"metric": "modeling_gate_status", "value": "blocked", "interpretation": "No predictive, reduced-form, causal ML, or policy learning until registry thresholds pass."},
    ]
    return action_rows, core_file_rows, summary_rows


def write_wave_handoffs(action_rows: list[dict[str, str]], core_file_rows: list[dict[str, str]]) -> int:
    rows_by_id = by_id(core_file_rows)
    count = 0
    for row in action_rows:
        folder = TEMP_DIR.parent / row["local_target_folder"]
        folder.mkdir(parents=True, exist_ok=True)
        path = folder / "_NEXT_RAW_PACKAGE_ACTION_PACKET.md"
        core_rows = rows_by_id.get(row["idno"], [])
        path.write_text(
            f"""# Next Raw Package Action Packet

Dataset: `{row['idno']}` - {row['country']} {row['wave']}

Official get-microdata URL: {row['official_get_microdata_url']}

Local target folder: `{row['local_target_folder']}`

Acquisition tier: `{row['acquisition_tier']}`

Current receipt status: `{row['current_receipt_status']}`

## Required Action

{row['next_action']}

## Core Files To Confirm After Download

{markdown_table(core_rows, ['requirement', 'file_rank', 'file_name', 'candidate_variable_rows', 'current_receipt_status'], 80)}

## Post-Download Validation

Run from `climate_uhc_ml/`:

```bash
{VALIDATION_COMMANDS}
```
""",
            encoding="utf-8",
        )
        count += 1
    return count


def write_report(action_rows: list[dict[str, str]], core_file_rows: list[dict[str, str]], summary_rows: list[dict[str, str]]) -> None:
    REPORT_PATH.write_text(
        f"""# Priority LSMS/ISA Next Raw Package Action Packet

Status: exact acquisition queue for moving beyond the first promoted Malawi
2004 household-climate dataset.

The current registry has one promoted country-wave. The remaining minimum
batch needs complete official raw packages before raw-value, outcome, timing,
geography, and climate-linkage verification can start.

This packet does not bypass World Bank account, registration, terms, or
request gates. It translates the existing minimum viable acquisition plan into
the next file-level acquisition actions.

## Summary

{markdown_table(summary_rows, ['metric', 'value', 'interpretation'], 20)}

## Action Queue

{markdown_table(action_rows, ['action_rank', 'acquisition_tier', 'country', 'wave', 'idno', 'full_official_file_rows', 'unique_core_files_required', 'missing_core_file_rows'], 30)}

## Core File Preview

{markdown_table(core_file_rows, ['action_rank', 'idno', 'requirement', 'file_rank', 'file_name', 'current_receipt_status'], 50)}

## Rule

After files are placed, rerun the receipt, official-file validation, schema,
value-profile, and semantics-review commands listed in the action queue. Do
not write additional country-waves to `data/` until every required gate passes.
""",
        encoding="utf-8",
    )


def main() -> None:
    ensure_dirs()
    action_rows, core_file_rows, summary_rows = build_outputs()
    handoffs = write_wave_handoffs(action_rows, core_file_rows)
    summary_rows.append(
        {
            "metric": "wave_handoff_readmes_written",
            "value": str(handoffs),
            "interpretation": "Per-wave next raw package handoff files written under target folders.",
        }
    )
    write_csv(ACTION_QUEUE_PATH, action_rows, ACTION_COLUMNS)
    write_csv(CORE_FILES_PATH, core_file_rows, CORE_COLUMNS)
    write_csv(SUMMARY_PATH, summary_rows, SUMMARY_COLUMNS)
    write_report(action_rows, core_file_rows, summary_rows)
    append_log(
        TEMP_DIR / "audit_log.md",
        f"Built priority LSMS/ISA next raw package action packet actions={len(action_rows)} core_files={len(core_file_rows)}.",
    )
    print(f"Priority LSMS/ISA next raw package action packet actions={len(action_rows)} core_files={len(core_file_rows)}.")


if __name__ == "__main__":
    main()
