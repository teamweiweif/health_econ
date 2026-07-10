from __future__ import annotations

import csv
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

from common import REPORT_DIR, RESULT_DIR, TEMP_DIR, append_log, ensure_dirs, write_csv


REGISTRY_PATH = RESULT_DIR / "promoted_country_wave_registry.csv"
MINIMUM_BATCH_PATH = TEMP_DIR / "priority_lsms_isa_threshold_minimum_batch.csv"
ACTION_QUEUE_PATH = TEMP_DIR / "priority_lsms_isa_next_raw_package_action_queue.csv"
INCOMING_ROUTE_PLAN_PATH = TEMP_DIR / "priority_lsms_isa_incoming_raw_package_route_plan.csv"

DOWNLOAD_PANEL_PATH = TEMP_DIR / "priority_lsms_isa_threshold_gap_download_panel.csv"
COUNTRY_PANEL_PATH = RESULT_DIR / "priority_lsms_isa_threshold_gap_country_panel.csv"
SUMMARY_PATH = RESULT_DIR / "priority_lsms_isa_threshold_gap_control_panel_summary.csv"
REPORT_PATH = REPORT_DIR / "priority_lsms_isa_threshold_gap_control_panel.md"

COUNTRY_THRESHOLD = 6
WAVE_THRESHOLD = 10

DOWNLOAD_COLUMNS = [
    "threshold_sequence_rank",
    "threshold_download_role",
    "download_batch_role",
    "country",
    "wave",
    "idno",
    "analysis_ready_status",
    "raw_package_status",
    "raw_value_verification_status",
    "financial_protection_status",
    "access_forgone_care_status",
    "climate_linkage_status",
    "official_expected_file_rows",
    "official_expected_missing_rows",
    "official_core_file_rows",
    "official_core_missing_rows",
    "incoming_route_rows",
    "incoming_copy_candidate_rows",
    "credentialed_acquisition_status",
    "official_get_microdata_url",
    "local_target_folder",
    "next_action",
    "post_download_validation_commands",
    "promotion_stop_rule",
]

COUNTRY_COLUMNS = [
    "country",
    "current_promoted_waves",
    "minimum_batch_rows",
    "minimum_batch_remaining_rows",
    "backup_action_rows",
    "country_threshold_role",
    "waves_if_minimum_remaining_passes",
    "needed_idnos",
    "backup_idnos",
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


def by_id(rows: list[dict[str, str]], field: str = "idno") -> dict[str, dict[str, str]]:
    out: dict[str, dict[str, str]] = {}
    for row in rows:
        idno = clean(row.get(field))
        if idno and idno not in out:
            out[idno] = row
    return out


def group_by_id(rows: list[dict[str, str]], field: str = "idno") -> dict[str, list[dict[str, str]]]:
    out: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in rows:
        idno = clean(row.get(field))
        if idno:
            out[idno].append(row)
    return out


def summary_row(metric: str, value: Any, interpretation: str) -> dict[str, str]:
    return {"metric": metric, "value": str(value), "interpretation": interpretation}


def markdown_table(rows: list[dict[str, str]], columns: list[str], limit: int = 30) -> str:
    if not rows:
        return "_No rows._"
    lines = ["| " + " | ".join(columns) + " |", "| " + " | ".join("---" for _ in columns) + " |"]
    for row in rows[:limit]:
        lines.append("| " + " | ".join(clean(row.get(column)).replace("|", "/") for column in columns) + " |")
    if len(rows) > limit:
        lines.append("| " + " | ".join("..." for _ in columns) + " |")
    return "\n".join(lines)


def is_promoted(row: dict[str, str]) -> bool:
    return clean(row.get("analysis_ready_status")) == "promoted_analysis_ready" and safe_int(row.get("rows")) > 0


def classify_download_role(row: dict[str, str], registry_row: dict[str, str], action_by_id: dict[str, dict[str, str]]) -> str:
    idno = clean(row.get("idno"))
    if is_promoted(registry_row):
        return "already_promoted_no_download_action"
    if idno in action_by_id:
        return "remaining_minimum_batch_download_action"
    return "minimum_batch_not_in_current_action_queue_review"


def build_download_panel(
    minimum_rows: list[dict[str, str]],
    registry_by_id: dict[str, dict[str, str]],
    action_by_id: dict[str, dict[str, str]],
    incoming_by_id: dict[str, list[dict[str, str]]],
) -> list[dict[str, str]]:
    panel: list[dict[str, str]] = []
    for row in sorted(minimum_rows, key=lambda r: safe_int(r.get("threshold_sequence_rank"), 9999)):
        idno = clean(row.get("idno"))
        registry_row = registry_by_id.get(idno, {})
        action_row = action_by_id.get(idno, {})
        incoming_rows = incoming_by_id.get(idno, [])
        copy_rows = [r for r in incoming_rows if clean(r.get("route_decision")) == "copy_to_selected_target"]
        batch_role = classify_download_role(row, registry_row, action_by_id)
        panel.append(
            {
                "threshold_sequence_rank": clean(row.get("threshold_sequence_rank")),
                "threshold_download_role": clean(row.get("threshold_download_role")),
                "download_batch_role": batch_role,
                "country": clean(row.get("country")),
                "wave": clean(row.get("wave")),
                "idno": idno,
                "analysis_ready_status": clean(registry_row.get("analysis_ready_status")) or clean(row.get("analysis_ready_status")) or "not_promoted",
                "raw_package_status": clean(registry_row.get("raw_package_status")) or clean(row.get("raw_package_status")) or clean(row.get("official_file_receipt_status")),
                "raw_value_verification_status": clean(registry_row.get("raw_value_verification_status")) or clean(row.get("raw_value_verification_status")),
                "financial_protection_status": clean(registry_row.get("che10_che25_ready_status")) or clean(row.get("financial_protection_status")),
                "access_forgone_care_status": clean(registry_row.get("access_forgone_care_ready_status")) or clean(row.get("access_forgone_care_status")),
                "climate_linkage_status": clean(registry_row.get("climate_linkage_ready_status")) or clean(row.get("climate_linkage_status")),
                "official_expected_file_rows": clean(row.get("official_expected_file_rows")),
                "official_expected_missing_rows": clean(row.get("official_expected_missing_rows")),
                "official_core_file_rows": clean(row.get("official_core_file_rows")),
                "official_core_missing_rows": clean(row.get("official_core_missing_rows")),
                "incoming_route_rows": str(len(incoming_rows)),
                "incoming_copy_candidate_rows": str(len(copy_rows)),
                "credentialed_acquisition_status": clean(action_row.get("credentialed_acquisition_status")) or clean(row.get("credentialed_acquisition_status")),
                "official_get_microdata_url": clean(action_row.get("official_get_microdata_url")) or clean(row.get("official_get_microdata_url")),
                "local_target_folder": clean(action_row.get("local_target_folder")) or clean(row.get("local_target_folder")),
                "next_action": clean(action_row.get("next_action")) or clean(row.get("next_manual_action")),
                "post_download_validation_commands": clean(action_row.get("post_download_validation_commands")) or clean(row.get("post_download_validation_commands")),
                "promotion_stop_rule": clean(row.get("promotion_stop_rule"))
                or "Do not write this country-wave into data/ until all promotion gates pass.",
            }
        )
    return panel


def build_country_panel(
    registry_rows: list[dict[str, str]],
    minimum_rows: list[dict[str, str]],
    action_rows: list[dict[str, str]],
) -> list[dict[str, str]]:
    promoted_by_country: Counter[str] = Counter()
    for row in registry_rows:
        if is_promoted(row):
            promoted_by_country[clean(row.get("country"))] += 1

    minimum_by_country: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in minimum_rows:
        minimum_by_country[clean(row.get("country"))].append(row)

    action_by_country: dict[str, list[dict[str, str]]] = defaultdict(list)
    backup_by_country: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in action_rows:
        country = clean(row.get("country"))
        if clean(row.get("acquisition_tier")) == "minimum_batch_remaining":
            action_by_country[country].append(row)
        elif clean(row.get("acquisition_tier")) == "backup_after_minimum_batch":
            backup_by_country[country].append(row)

    countries = sorted(set(promoted_by_country) | set(minimum_by_country) | set(action_by_country) | set(backup_by_country))
    panel: list[dict[str, str]] = []
    for country in countries:
        current = promoted_by_country[country]
        minimum = minimum_by_country.get(country, [])
        remaining = action_by_country.get(country, [])
        backup = backup_by_country.get(country, [])
        if current > 0:
            role = "already_contributes_current_threshold"
        elif remaining:
            role = "needed_for_minimum_country_threshold"
        elif backup:
            role = "backup_country_or_replacement_after_failure"
        else:
            role = "monitor_only"
        panel.append(
            {
                "country": country,
                "current_promoted_waves": str(current),
                "minimum_batch_rows": str(len(minimum)),
                "minimum_batch_remaining_rows": str(len(remaining)),
                "backup_action_rows": str(len(backup)),
                "country_threshold_role": role,
                "waves_if_minimum_remaining_passes": str(current + len(remaining)),
                "needed_idnos": ";".join(clean(row.get("idno")) for row in remaining),
                "backup_idnos": ";".join(clean(row.get("idno")) for row in backup),
            }
        )
    return panel


def build_summary(
    registry_rows: list[dict[str, str]],
    minimum_rows: list[dict[str, str]],
    action_rows: list[dict[str, str]],
    download_panel: list[dict[str, str]],
    country_panel: list[dict[str, str]],
) -> list[dict[str, str]]:
    promoted_rows = [row for row in registry_rows if is_promoted(row)]
    promoted_countries = {clean(row.get("country")) for row in promoted_rows}
    minimum_ids = {clean(row.get("idno")) for row in minimum_rows if clean(row.get("idno"))}
    minimum_remaining = [
        row
        for row in download_panel
        if clean(row.get("download_batch_role")) == "remaining_minimum_batch_download_action"
    ]
    remaining_countries = {clean(row.get("country")) for row in minimum_remaining}
    backup_rows = [row for row in action_rows if clean(row.get("acquisition_tier")) == "backup_after_minimum_batch"]
    backup_countries = {clean(row.get("country")) for row in backup_rows}
    if_minimum_pass_countries = promoted_countries | remaining_countries
    if_minimum_pass_waves = len(promoted_rows) + len(minimum_remaining)
    country_gap_current = max(COUNTRY_THRESHOLD - len(promoted_countries), 0)
    wave_gap_current = max(WAVE_THRESHOLD - len(promoted_rows), 0)
    country_buffer_if_minimum_passes = len(if_minimum_pass_countries) - COUNTRY_THRESHOLD
    wave_buffer_if_minimum_passes = if_minimum_pass_waves - WAVE_THRESHOLD
    missing_core_files = sum(safe_int(row.get("official_core_missing_rows")) for row in download_panel)
    missing_full_files = sum(safe_int(row.get("official_expected_missing_rows")) for row in download_panel)
    incoming_route_rows = sum(safe_int(row.get("incoming_route_rows")) for row in download_panel)
    incoming_copy_rows = sum(safe_int(row.get("incoming_copy_candidate_rows")) for row in download_panel)
    blocked_download_rows = sum(1 for row in download_panel if clean(row.get("download_batch_role")) == "remaining_minimum_batch_download_action")
    promoted_minimum_rows = sum(1 for row in minimum_rows if clean(row.get("idno")) not in {clean(r.get("idno")) for r in minimum_remaining})

    return [
        summary_row("threshold_country_requirement", COUNTRY_THRESHOLD, "Minimum value-verified countries required before modeling can resume."),
        summary_row("threshold_country_wave_requirement", WAVE_THRESHOLD, "Minimum value-verified country-waves required before modeling can resume."),
        summary_row("current_promoted_analysis_ready_rows", len(promoted_rows), "Country-waves currently promoted analysis-ready in the registry."),
        summary_row("current_promoted_country_rows", len(promoted_countries), "Countries currently represented by promoted analysis-ready rows."),
        summary_row("current_country_gap_to_threshold", country_gap_current, "Additional value-verified countries needed from the current registry state."),
        summary_row("current_country_wave_gap_to_threshold", wave_gap_current, "Additional value-verified country-waves needed from the current registry state."),
        summary_row("minimum_threshold_batch_rows", len(minimum_rows), "Country-waves in the minimum threshold batch."),
        summary_row("minimum_threshold_batch_promoted_rows", promoted_minimum_rows, "Minimum-batch rows already promoted or not requiring a raw-package action."),
        summary_row("minimum_threshold_batch_remaining_download_rows", len(minimum_remaining), "Minimum-batch rows still requiring complete official raw packages."),
        summary_row("countries_if_minimum_remaining_passes", len(if_minimum_pass_countries), "Countries covered if all remaining minimum-batch downloads later pass verification."),
        summary_row("country_waves_if_minimum_remaining_passes", if_minimum_pass_waves, "Country-waves covered if all remaining minimum-batch downloads later pass verification."),
        summary_row("country_buffer_if_minimum_remaining_passes", country_buffer_if_minimum_passes, "Country-count buffer above the 6-country modeling threshold if the minimum batch passes."),
        summary_row("country_wave_buffer_if_minimum_remaining_passes", wave_buffer_if_minimum_passes, "Country-wave buffer above the 10-wave modeling threshold if the minimum batch passes."),
        summary_row("backup_action_rows_after_minimum_batch", len(backup_rows), "Backup raw package actions if a minimum-batch row fails."),
        summary_row("backup_country_rows_after_minimum_batch", len(backup_countries), "Backup countries represented after the minimum batch."),
        summary_row("download_panel_rows", len(download_panel), "Rows in the threshold-gap download control panel."),
        summary_row("country_panel_rows", len(country_panel), "Rows in the threshold-gap country control panel."),
        summary_row("minimum_batch_missing_full_file_rows", missing_full_files, "Expected official full-file rows still missing across the minimum batch."),
        summary_row("minimum_batch_missing_core_file_rows", missing_core_files, "Requirement-linked official core-file rows still missing across the minimum batch."),
        summary_row("incoming_route_rows_for_minimum_batch", incoming_route_rows, "Incoming route rows currently matched to minimum-batch IDNOs."),
        summary_row("incoming_copy_candidate_rows_for_minimum_batch", incoming_copy_rows, "Incoming files with one selected target among minimum-batch rows."),
        summary_row("blocked_download_rows_in_control_panel", blocked_download_rows, "Control-panel rows blocked at credentialed/manual raw package download."),
        summary_row("data_write_gate_status", "blocked_no_new_data_write", "The control panel never writes country-waves into data/."),
        summary_row("modeling_gate_status", "blocked", "No predictive, reduced-form, causal ML, or policy learning until registry thresholds pass."),
        summary_row(
            "minimum_batch_ids",
            ";".join(clean(row.get("idno")) for row in minimum_rows if clean(row.get("idno"))),
            "IDNOs in the minimum threshold batch.",
        ),
    ]


def write_report(
    summary_rows: list[dict[str, str]],
    download_panel: list[dict[str, str]],
    country_panel: list[dict[str, str]],
) -> None:
    metric = {row["metric"]: row["value"] for row in summary_rows}
    action_rows = [row for row in download_panel if clean(row.get("download_batch_role")) == "remaining_minimum_batch_download_action"]
    lines = [
        "# Priority LSMS-ISA Threshold Gap Control Panel",
        "",
        "Status: manual-download control panel for the minimum threshold batch.",
        "It does not download raw data, accept terms, extract microdata, write `data/`,",
        "or run predictive/reduced-form/causal ML.",
        "",
        "## Threshold Arithmetic",
        "",
        f"- Current promoted registry: {metric.get('current_promoted_analysis_ready_rows', '0')} country-wave(s) across {metric.get('current_promoted_country_rows', '0')} country/countries.",
        f"- Current gap: {metric.get('current_country_gap_to_threshold', '0')} country/countries and {metric.get('current_country_wave_gap_to_threshold', '0')} country-wave(s).",
        f"- If every remaining minimum-batch row passes verification: {metric.get('countries_if_minimum_remaining_passes', '0')} countries and {metric.get('country_waves_if_minimum_remaining_passes', '0')} country-waves.",
        f"- Buffer after minimum batch: {metric.get('country_buffer_if_minimum_remaining_passes', '0')} country and {metric.get('country_wave_buffer_if_minimum_remaining_passes', '0')} country-wave(s).",
        f"- Remaining minimum-batch manual downloads: {metric.get('minimum_threshold_batch_remaining_download_rows', '0')}.",
        f"- Backup actions after the minimum batch: {metric.get('backup_action_rows_after_minimum_batch', '0')}.",
        "",
        "## Minimum Batch Download Actions",
        "",
        markdown_table(
            action_rows,
            [
                "threshold_sequence_rank",
                "country",
                "wave",
                "idno",
                "official_expected_missing_rows",
                "official_core_missing_rows",
                "incoming_route_rows",
                "official_get_microdata_url",
                "local_target_folder",
            ],
            limit=20,
        ),
        "",
        "## Country Threshold Panel",
        "",
        markdown_table(
            country_panel,
            [
                "country",
                "current_promoted_waves",
                "minimum_batch_remaining_rows",
                "backup_action_rows",
                "country_threshold_role",
                "waves_if_minimum_remaining_passes",
            ],
            limit=20,
        ),
        "",
        "## Outputs",
        "",
        "- `temp/priority_lsms_isa_threshold_gap_download_panel.csv`",
        "- `result/priority_lsms_isa_threshold_gap_country_panel.csv`",
        "- `result/priority_lsms_isa_threshold_gap_control_panel_summary.csv`",
        "",
        "## Stop Rule",
        "",
        "The modeling gate remains blocked until the promoted registry proves at least",
        "6 value-verified financial-protection countries, 10 value-verified",
        "country-waves for double failure, and at least one accepted CHIRPS or ERA5",
        "climate-linkage route.",
    ]
    REPORT_PATH.write_text("\n".join(lines) + "\n", encoding="utf-8")


def build_outputs() -> tuple[list[dict[str, str]], list[dict[str, str]], list[dict[str, str]]]:
    registry_rows = read_csv_dicts(REGISTRY_PATH)
    minimum_rows = read_csv_dicts(MINIMUM_BATCH_PATH)
    action_rows = read_csv_dicts(ACTION_QUEUE_PATH)
    incoming_rows = read_csv_dicts(INCOMING_ROUTE_PLAN_PATH)
    registry_by_id = by_id(registry_rows)
    action_by_id = by_id(action_rows)
    incoming_by_id = group_by_id(incoming_rows, "selected_idno")
    download_panel = build_download_panel(minimum_rows, registry_by_id, action_by_id, incoming_by_id)
    country_panel = build_country_panel(registry_rows, minimum_rows, action_rows)
    summary_rows = build_summary(registry_rows, minimum_rows, action_rows, download_panel, country_panel)
    return download_panel, country_panel, summary_rows


def main() -> None:
    ensure_dirs()
    download_panel, country_panel, summary_rows = build_outputs()
    write_csv(DOWNLOAD_PANEL_PATH, download_panel, DOWNLOAD_COLUMNS)
    write_csv(COUNTRY_PANEL_PATH, country_panel, COUNTRY_COLUMNS)
    write_csv(SUMMARY_PATH, summary_rows, SUMMARY_COLUMNS)
    write_report(summary_rows, download_panel, country_panel)
    append_log(
        TEMP_DIR / "audit_log.md",
        "Built priority LSMS/ISA threshold gap control panel; data writes and models remain blocked.",
    )
    print(
        "Priority LSMS/ISA threshold gap control panel complete: "
        f"download_rows={len(download_panel)}, country_rows={len(country_panel)}"
    )


if __name__ == "__main__":
    main()
