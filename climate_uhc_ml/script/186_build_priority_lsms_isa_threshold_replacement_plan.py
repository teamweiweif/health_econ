from __future__ import annotations

import csv
from collections import Counter
from typing import Any

from common import REPORT_DIR, RESULT_DIR, TEMP_DIR, append_log, ensure_dirs, write_csv


ACTION_QUEUE_PATH = TEMP_DIR / "priority_lsms_isa_next_raw_package_action_queue.csv"
MINIMUM_BATCH_PATH = TEMP_DIR / "priority_lsms_isa_threshold_gap_download_panel.csv"
REGISTRY_PATH = RESULT_DIR / "promoted_country_wave_registry.csv"
TARGET_SMOKE_STATUS_PATH = TEMP_DIR / "priority_lsms_isa_target_folder_receipt_status.csv"

BACKUP_CANDIDATE_PATH = TEMP_DIR / "priority_lsms_isa_threshold_replacement_candidate_rank.csv"
SCENARIO_PATH = TEMP_DIR / "priority_lsms_isa_threshold_replacement_scenarios.csv"
STRATEGY_PATH = TEMP_DIR / "priority_lsms_isa_threshold_replacement_strategy.csv"
SUMMARY_PATH = RESULT_DIR / "priority_lsms_isa_threshold_replacement_plan_summary.csv"
REPORT_PATH = REPORT_DIR / "priority_lsms_isa_threshold_replacement_plan.md"

COUNTRY_THRESHOLD = 6
WAVE_THRESHOLD = 10
PRIORITY_COUNTRIES = {"Ethiopia", "Nigeria", "Malawi", "Tanzania", "Uganda"}

BACKUP_COLUMNS = [
    "backup_rank",
    "candidate_priority_group",
    "country",
    "wave",
    "idno",
    "official_get_microdata_url",
    "local_target_folder",
    "full_official_file_rows",
    "unique_core_files_required",
    "core_requirement_rows",
    "current_receipt_status",
    "target_receipt_smoke_status",
    "priority_country_candidate",
    "new_country_candidate_if_nepal_fails",
    "same_country_backup_for",
    "replacement_use_case",
    "post_download_validation_commands",
    "data_write_gate_status",
    "modeling_gate_status",
]

SCENARIO_COLUMNS = [
    "scenario_rank",
    "failed_minimum_country",
    "failed_minimum_wave",
    "failed_minimum_idno",
    "failure_type",
    "countries_after_failure_without_replacement",
    "waves_after_failure_without_replacement",
    "country_threshold_without_replacement",
    "wave_threshold_without_replacement",
    "replacement_required_for_threshold",
    "selected_replacement_idno",
    "selected_replacement_country",
    "selected_replacement_wave",
    "selected_replacement_reason",
    "countries_after_selected_replacement",
    "waves_after_selected_replacement",
    "country_threshold_after_selected_replacement",
    "wave_threshold_after_selected_replacement",
    "priority_country_waves_after_selected_replacement",
    "sixth_country_status_after_selected_replacement",
    "next_action",
    "data_write_gate_status",
    "modeling_gate_status",
]

STRATEGY_COLUMNS = [
    "strategy",
    "countries_if_all_pass",
    "country_waves_if_all_pass",
    "priority_country_rows",
    "nonpriority_country_rows",
    "country_threshold_status",
    "wave_threshold_status",
    "interpretation",
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


def one_by_id(rows: list[dict[str, str]], field: str = "idno") -> dict[str, dict[str, str]]:
    out: dict[str, dict[str, str]] = {}
    for row in rows:
        idno = clean(row.get(field))
        if idno and idno not in out:
            out[idno] = row
    return out


def is_promoted(row: dict[str, str]) -> bool:
    return clean(row.get("analysis_ready_status")) == "promoted_analysis_ready" and safe_int(row.get("rows")) > 0


def threshold_status(value: int, threshold: int) -> str:
    return "passes" if value >= threshold else f"fails_short_by_{threshold - value}"


def unique_countries(rows: list[dict[str, str]]) -> int:
    return len({clean(row.get("country")) for row in rows if clean(row.get("country"))})


def priority_wave_count(rows: list[dict[str, str]]) -> int:
    return sum(1 for row in rows if clean(row.get("country")) in PRIORITY_COUNTRIES)


def status_by_id(rows: list[dict[str, str]]) -> dict[str, str]:
    return {clean(row.get("idno")): clean(row.get("receipt_smoke_status")) for row in rows if clean(row.get("idno"))}


def sorted_minimum_remaining(rows: list[dict[str, str]]) -> list[dict[str, str]]:
    return [
        row
        for row in sorted(rows, key=lambda r: safe_int(r.get("threshold_sequence_rank"), 9999))
        if clean(row.get("download_batch_role")) == "remaining_minimum_batch_download_action"
    ]


def sorted_backups(rows: list[dict[str, str]]) -> list[dict[str, str]]:
    return [
        row
        for row in sorted(rows, key=lambda r: safe_int(r.get("action_rank"), 9999))
        if clean(row.get("acquisition_tier")) == "backup_after_minimum_batch"
    ]


def promoted_rows(registry_rows: list[dict[str, str]]) -> list[dict[str, str]]:
    return [
        {
            "country": clean(row.get("country")),
            "wave": clean(row.get("wave")),
            "idno": clean(row.get("idno")),
        }
        for row in registry_rows
        if is_promoted(row)
    ]


def compact_wave(row: dict[str, str]) -> dict[str, str]:
    return {
        "country": clean(row.get("country")),
        "wave": clean(row.get("wave")),
        "idno": clean(row.get("idno")),
    }


def candidate_priority_group(row: dict[str, str]) -> str:
    country = clean(row.get("country"))
    if country in {"Uganda", "Malawi"}:
        return "priority_country_wave_buffer"
    if country not in PRIORITY_COUNTRIES:
        return "sixth_country_replacement"
    return "priority_country_other"


def same_country_backup_for(row: dict[str, str], minimum_rows: list[dict[str, str]]) -> str:
    country = clean(row.get("country"))
    minimum_countries = {clean(r.get("country")) for r in minimum_rows}
    return country if country in minimum_countries else ""


def replacement_use_case(row: dict[str, str]) -> str:
    country = clean(row.get("country"))
    if country == "Uganda":
        return "Use first if UGA_2019_UNPS_v03_M fails; keeps Uganda in the priority-country set and restores the 6-country threshold."
    if country in {"Jamaica", "Kyrgyz Republic"}:
        return "Use if the sixth-country candidate fails or a whole priority country drops out and a new country is needed for the 6-country threshold."
    if country == "Malawi":
        return "Use to restore the 10-wave buffer inside the priority-country family; it does not add a new country because Malawi 2004 is already promoted."
    return "Use as a backup if a same-country or new-country replacement is not needed."


def build_backup_candidates(
    backup_rows: list[dict[str, str]],
    minimum_rows: list[dict[str, str]],
    smoke_status: dict[str, str],
) -> list[dict[str, str]]:
    out: list[dict[str, str]] = []
    for rank, row in enumerate(backup_rows, start=1):
        idno = clean(row.get("idno"))
        country = clean(row.get("country"))
        out.append(
            {
                "backup_rank": str(rank),
                "candidate_priority_group": candidate_priority_group(row),
                "country": country,
                "wave": clean(row.get("wave")),
                "idno": idno,
                "official_get_microdata_url": clean(row.get("official_get_microdata_url")),
                "local_target_folder": clean(row.get("local_target_folder")),
                "full_official_file_rows": clean(row.get("full_official_file_rows")),
                "unique_core_files_required": clean(row.get("unique_core_files_required")),
                "core_requirement_rows": clean(row.get("core_requirement_rows")),
                "current_receipt_status": clean(row.get("current_receipt_status")),
                "target_receipt_smoke_status": smoke_status.get(idno, "not_in_minimum_target_smoke_test"),
                "priority_country_candidate": "1" if country in PRIORITY_COUNTRIES else "0",
                "new_country_candidate_if_nepal_fails": "1" if country not in PRIORITY_COUNTRIES else "0",
                "same_country_backup_for": same_country_backup_for(row, minimum_rows),
                "replacement_use_case": replacement_use_case(row),
                "post_download_validation_commands": clean(row.get("post_download_validation_commands")),
                "data_write_gate_status": "blocked_no_data_write",
                "modeling_gate_status": "blocked",
            }
        )
    return out


def choose_replacement(
    failed_row: dict[str, str],
    base_after_failure: list[dict[str, str]],
    backup_rows: list[dict[str, str]],
) -> tuple[dict[str, str], str, bool]:
    countries_without = unique_countries(base_after_failure)
    waves_without = len(base_after_failure)
    needs_threshold = countries_without < COUNTRY_THRESHOLD or waves_without < WAVE_THRESHOLD
    failed_country = clean(failed_row.get("country"))

    scored: list[tuple[int, int, int, int, dict[str, str]]] = []
    for idx, candidate in enumerate(backup_rows, start=1):
        candidate_wave = compact_wave(candidate)
        after = base_after_failure + [candidate_wave]
        countries_after = unique_countries(after)
        waves_after = len(after)
        passes_both = countries_after >= COUNTRY_THRESHOLD and waves_after >= WAVE_THRESHOLD
        same_country = clean(candidate.get("country")) == failed_country
        priority_country = clean(candidate.get("country")) in PRIORITY_COUNTRIES
        adds_new_country = clean(candidate.get("country")) not in {clean(row.get("country")) for row in base_after_failure}

        if needs_threshold:
            score = (
                0 if passes_both else 1,
                0 if same_country else 1,
                0 if adds_new_country else 1,
                idx,
            )
        else:
            score = (
                0 if priority_country else 1,
                0 if clean(candidate.get("country")) in {"Malawi", "Uganda"} else 1,
                idx,
                0,
            )
        scored.append((*score, candidate))

    if not scored:
        return {}, "no_backup_candidate_available", needs_threshold

    selected = sorted(scored, key=lambda item: item[:4])[0][4]
    if needs_threshold:
        reason = "selected_to_restore_failed_country_or_wave_threshold"
    else:
        reason = "optional_buffer_to_restore_11th_wave_after_single_wave_failure"
    return selected, reason, needs_threshold


def build_scenarios(
    promoted: list[dict[str, str]],
    minimum_remaining: list[dict[str, str]],
    backup_rows: list[dict[str, str]],
) -> list[dict[str, str]]:
    base = promoted + [compact_wave(row) for row in minimum_remaining]
    rows: list[dict[str, str]] = []
    for rank, failed in enumerate(minimum_remaining, start=1):
        failed_id = clean(failed.get("idno"))
        after_failure = [row for row in base if clean(row.get("idno")) != failed_id]
        countries_without = unique_countries(after_failure)
        waves_without = len(after_failure)
        selected, reason, required = choose_replacement(failed, after_failure, backup_rows)
        selected_wave = compact_wave(selected) if selected else {}
        after_selected = after_failure + ([selected_wave] if selected_wave else [])
        countries_after = unique_countries(after_selected)
        waves_after = len(after_selected)
        sixth_status = "has_sixth_country" if countries_after >= COUNTRY_THRESHOLD else "missing_sixth_country"
        rows.append(
            {
                "scenario_rank": str(rank),
                "failed_minimum_country": clean(failed.get("country")),
                "failed_minimum_wave": clean(failed.get("wave")),
                "failed_minimum_idno": failed_id,
                "failure_type": "single_minimum_batch_wave_fails_receipt_or_value_gate",
                "countries_after_failure_without_replacement": str(countries_without),
                "waves_after_failure_without_replacement": str(waves_without),
                "country_threshold_without_replacement": threshold_status(countries_without, COUNTRY_THRESHOLD),
                "wave_threshold_without_replacement": threshold_status(waves_without, WAVE_THRESHOLD),
                "replacement_required_for_threshold": "1" if required else "0",
                "selected_replacement_idno": clean(selected.get("idno")),
                "selected_replacement_country": clean(selected.get("country")),
                "selected_replacement_wave": clean(selected.get("wave")),
                "selected_replacement_reason": reason,
                "countries_after_selected_replacement": str(countries_after),
                "waves_after_selected_replacement": str(waves_after),
                "country_threshold_after_selected_replacement": threshold_status(countries_after, COUNTRY_THRESHOLD),
                "wave_threshold_after_selected_replacement": threshold_status(waves_after, WAVE_THRESHOLD),
                "priority_country_waves_after_selected_replacement": str(priority_wave_count(after_selected)),
                "sixth_country_status_after_selected_replacement": sixth_status,
                "next_action": clean(selected.get("next_action")) or "No replacement candidate available.",
                "data_write_gate_status": "blocked_no_data_write",
                "modeling_gate_status": "blocked",
            }
        )
    return rows


def build_strategy_rows(promoted: list[dict[str, str]], minimum_remaining: list[dict[str, str]]) -> list[dict[str, str]]:
    all_minimum = promoted + [compact_wave(row) for row in minimum_remaining]
    priority_only = [row for row in all_minimum if clean(row.get("country")) in PRIORITY_COUNTRIES]
    nonpriority_rows = [row for row in all_minimum if clean(row.get("country")) not in PRIORITY_COUNTRIES]
    plus_first_nonpriority = priority_only + nonpriority_rows[:1]

    strategies = [
        (
            "current_minimum_batch_all_passes",
            all_minimum,
            "Current minimum batch reaches 6 countries and 11 waves only if Nepal is retained as the sixth-country candidate.",
        ),
        (
            "strict_five_priority_countries_only",
            priority_only,
            "Strictly using Ethiopia, Nigeria, Malawi, Tanzania, and Uganda reaches 10 waves but only 5 countries, so the 6-country modeling gate remains blocked.",
        ),
        (
            "priority_countries_plus_first_sixth_country",
            plus_first_nonpriority,
            "Priority-country waves plus the first non-priority sixth-country candidate restore the 6-country threshold.",
        ),
    ]

    rows: list[dict[str, str]] = []
    for strategy, waves, interpretation in strategies:
        countries = unique_countries(waves)
        rows.append(
            {
                "strategy": strategy,
                "countries_if_all_pass": str(countries),
                "country_waves_if_all_pass": str(len(waves)),
                "priority_country_rows": str(priority_wave_count(waves)),
                "nonpriority_country_rows": str(len(waves) - priority_wave_count(waves)),
                "country_threshold_status": threshold_status(countries, COUNTRY_THRESHOLD),
                "wave_threshold_status": threshold_status(len(waves), WAVE_THRESHOLD),
                "interpretation": interpretation,
                "data_write_gate_status": "blocked_no_data_write",
                "modeling_gate_status": "blocked",
            }
        )
    return rows


def summary_row(metric: str, value: Any, interpretation: str) -> dict[str, str]:
    return {"metric": metric, "value": str(value), "interpretation": interpretation}


def build_summary(
    backup_rows: list[dict[str, str]],
    scenario_rows: list[dict[str, str]],
    strategy_rows: list[dict[str, str]],
) -> list[dict[str, str]]:
    required = sum(1 for row in scenario_rows if row.get("replacement_required_for_threshold") == "1")
    optional = sum(1 for row in scenario_rows if row.get("replacement_required_for_threshold") == "0")
    selected = [row.get("selected_replacement_idno", "") for row in scenario_rows if row.get("selected_replacement_idno")]
    selected_counts = Counter(selected)
    strict_row = next((row for row in strategy_rows if row.get("strategy") == "strict_five_priority_countries_only"), {})
    current_row = next((row for row in strategy_rows if row.get("strategy") == "current_minimum_batch_all_passes"), {})
    return [
        summary_row("priority_lsms_replacement_backup_candidate_rows", len(backup_rows), "Backup country-waves available after the current minimum batch."),
        summary_row("priority_lsms_replacement_scenario_rows", len(scenario_rows), "Single minimum-batch failure scenarios evaluated."),
        summary_row("priority_lsms_replacement_strategy_rows", len(strategy_rows), "Download-batch strategy rows evaluated."),
        summary_row("priority_lsms_replacement_required_for_threshold_rows", required, "Failure scenarios where a replacement is required to keep 6 countries and 10 waves."),
        summary_row("priority_lsms_replacement_optional_buffer_rows", optional, "Failure scenarios where thresholds still pass but the one-wave buffer is lost."),
        summary_row("priority_lsms_replacement_priority_country_backup_rows", sum(1 for row in backup_rows if row.get("priority_country_candidate") == "1"), "Backup rows from the priority country set."),
        summary_row("priority_lsms_replacement_new_country_backup_rows", sum(1 for row in backup_rows if row.get("new_country_candidate_if_nepal_fails") == "1"), "Backup rows that can add a new country for the 6-country threshold."),
        summary_row("priority_lsms_replacement_strict_priority_countries", strict_row.get("countries_if_all_pass", "0"), "Countries covered if Nepal and all other non-priority countries are excluded."),
        summary_row("priority_lsms_replacement_strict_priority_waves", strict_row.get("country_waves_if_all_pass", "0"), "Country-waves covered if Nepal and all other non-priority countries are excluded."),
        summary_row("priority_lsms_replacement_current_minimum_countries", current_row.get("countries_if_all_pass", "0"), "Countries covered by the current minimum batch if all rows pass."),
        summary_row("priority_lsms_replacement_current_minimum_waves", current_row.get("country_waves_if_all_pass", "0"), "Country-waves covered by the current minimum batch if all rows pass."),
        summary_row("priority_lsms_replacement_top_selected_replacement_ids", ";".join(f"{idno}:{count}" for idno, count in selected_counts.most_common()), "Replacement IDs selected across single-failure scenarios."),
        summary_row("priority_lsms_replacement_data_write_status", "blocked_no_data_write", "Replacement planning never writes promoted data."),
        summary_row("modeling_gate_status", "blocked", "No predictive, reduced-form, causal ML, or policy learning until registry thresholds pass."),
    ]


def markdown_table(rows: list[dict[str, str]], columns: list[str], limit: int = 40) -> str:
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


def write_report(
    backup_rows: list[dict[str, str]],
    scenario_rows: list[dict[str, str]],
    strategy_rows: list[dict[str, str]],
    summary_rows: list[dict[str, str]],
) -> None:
    REPORT_PATH.write_text(
        f"""# Priority LSMS/ISA Threshold Replacement Plan

Status: replacement and buffer plan for the minimum LSMS/ISA download batch.

This plan keeps the modeling gate blocked. It only explains how to preserve the
6-country and 10-country-wave thresholds if a minimum-batch raw package cannot
be obtained or later fails receipt, raw-value, outcome, timing/geography, or
climate-linkage gates.

## Summary

{markdown_table(summary_rows, ['metric', 'value', 'interpretation'], 30)}

## Strategy Check

{markdown_table(strategy_rows, ['strategy', 'countries_if_all_pass', 'country_waves_if_all_pass', 'priority_country_rows', 'nonpriority_country_rows', 'country_threshold_status', 'wave_threshold_status'], 10)}

## Single-Failure Replacement Scenarios

{markdown_table(scenario_rows, ['failed_minimum_idno', 'countries_after_failure_without_replacement', 'waves_after_failure_without_replacement', 'replacement_required_for_threshold', 'selected_replacement_idno', 'selected_replacement_reason', 'countries_after_selected_replacement', 'waves_after_selected_replacement'], 30)}

## Backup Candidate Rank

{markdown_table(backup_rows, ['backup_rank', 'candidate_priority_group', 'country', 'wave', 'idno', 'same_country_backup_for', 'replacement_use_case'], 30)}

## Interpretation

The strict five-priority-country set can reach 10 waves but not 6 countries.
That means a sixth-country candidate is still required for the financial-
protection country threshold. Nepal is the current sixth-country candidate.
If Nepal fails, the first viable non-priority backup country should be used.
Malawi and Uganda backups are still useful as wave buffers, but they do not add
a new country when Malawi 2004 and Uganda 2019 remain in the batch.
""",
        encoding="utf-8",
    )


def main() -> None:
    ensure_dirs()
    registry_rows = read_csv_dicts(REGISTRY_PATH)
    minimum_rows = sorted_minimum_remaining(read_csv_dicts(MINIMUM_BATCH_PATH))
    action_rows = read_csv_dicts(ACTION_QUEUE_PATH)
    backup_action_rows = sorted_backups(action_rows)
    smoke_status = status_by_id(read_csv_dicts(TARGET_SMOKE_STATUS_PATH))
    promoted = promoted_rows(registry_rows)

    backup_rows = build_backup_candidates(backup_action_rows, minimum_rows, smoke_status)
    scenario_rows = build_scenarios(promoted, minimum_rows, backup_action_rows)
    strategy_rows = build_strategy_rows(promoted, minimum_rows)
    summary_rows = build_summary(backup_rows, scenario_rows, strategy_rows)

    write_csv(BACKUP_CANDIDATE_PATH, backup_rows, BACKUP_COLUMNS)
    write_csv(SCENARIO_PATH, scenario_rows, SCENARIO_COLUMNS)
    write_csv(STRATEGY_PATH, strategy_rows, STRATEGY_COLUMNS)
    write_csv(SUMMARY_PATH, summary_rows, SUMMARY_COLUMNS)
    write_report(backup_rows, scenario_rows, strategy_rows, summary_rows)
    append_log(
        TEMP_DIR / "audit_log.md",
        f"Built priority LSMS/ISA threshold replacement plan scenarios={len(scenario_rows)} backups={len(backup_rows)}.",
    )
    print(f"Priority LSMS/ISA threshold replacement plan scenarios={len(scenario_rows)} backups={len(backup_rows)}.")


if __name__ == "__main__":
    main()
