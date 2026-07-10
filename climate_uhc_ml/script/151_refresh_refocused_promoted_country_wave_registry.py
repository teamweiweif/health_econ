from __future__ import annotations

import csv
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

from common import REPORT_DIR, RESULT_DIR, TEMP_DIR, append_log, ensure_dirs, write_csv


QUEUE_PATH = TEMP_DIR / "priority_lsms_isa_refocused_acquisition_queue.csv"
PACKET_INDEX_PATH = TEMP_DIR / "priority_lsms_isa_country_wave_promotion_packet_index.csv"
PACKET_GATE_PATH = TEMP_DIR / "priority_lsms_isa_country_wave_promotion_packet_gate_matrix.csv"
RECEIPT_PATH = TEMP_DIR / "priority_lsms_isa_raw_package_receipt_checklist.csv"
MWI2004_ACCEPTANCE_DECISION_PATH = RESULT_DIR / "mwi2004_requirement_acceptance_decisions.csv"

REGISTRY_PATH = RESULT_DIR / "promoted_country_wave_registry.csv"
GATE_AUDIT_PATH = RESULT_DIR / "country_wave_promotion_gate_audit.csv"
SUMMARY_PATH = RESULT_DIR / "country_wave_promotion_summary.csv"
DOWNLOAD_QUEUE_PATH = RESULT_DIR / "priority_country_wave_download_queue.csv"
REPORT_PATH = REPORT_DIR / "country_wave_promotion_registry.md"

PRIORITY_COUNTRIES = {"Ethiopia", "Nigeria", "Malawi", "Tanzania", "Uganda"}

REGISTRY_COLUMNS = [
    "country",
    "wave",
    "idno",
    "survey_name",
    "priority_country",
    "source",
    "official_url",
    "local_target_folder",
    "rows",
    "outcome_ready_status",
    "sdg382_ready_status",
    "che10_che25_ready_status",
    "access_forgone_care_ready_status",
    "climate_linkage_ready_status",
    "analysis_ready_status",
    "raw_package_status",
    "raw_value_verification_status",
    "promotion_packet",
    "remaining_blockers",
]

GATE_COLUMNS = [
    "country",
    "wave",
    "idno",
    "gate",
    "status",
    "evidence",
    "required_action",
]

SUMMARY_COLUMNS = ["metric", "value", "interpretation"]

QUEUE_COLUMNS = [
    "action_rank",
    "country",
    "wave",
    "idno",
    "survey_name",
    "official_url",
    "local_target_folder",
    "raw_package_status",
    "top_expected_files_or_modules",
    "promotion_packet",
    "next_action",
]


def read_csv_dicts(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        return []
    with path.open(encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def clean(value: Any) -> str:
    return "" if value is None else str(value).strip()


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


def by_id(rows: list[dict[str, str]], field: str = "idno") -> dict[str, list[dict[str, str]]]:
    out: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in rows:
        idno = clean(row.get(field))
        if idno:
            out[idno].append(row)
    return out


def compact(values: list[str], limit: int = 8) -> str:
    seen: set[str] = set()
    out: list[str] = []
    for value in values:
        text = " ".join(clean(value).split())
        if text and text not in seen:
            out.append(text)
            seen.add(text)
        if len(out) >= limit:
            break
    return "; ".join(out)


def is_ready(status: str) -> bool:
    text = clean(status).lower()
    return text.startswith("ready") or text.startswith("promoted") or text == "pass"


def accepted_climate(status: str) -> bool:
    text = clean(status).lower()
    return "chirps" in text and "accepted" in text or "era5" in text and "accepted" in text


def failed_gate_blockers(gate_rows: list[dict[str, str]]) -> str:
    failed = [row for row in gate_rows if clean(row.get("status")) == "fail"]
    gate_names = compact([row.get("gate", "") for row in failed], 8)
    actions = compact([row.get("required_action", "") for row in failed], 5)
    if not failed:
        return ""
    return f"failed_gates={len(failed)} ({gate_names}); required_actions={actions}"


def focused_decision_blockers(decision_rows: list[dict[str, str]]) -> str:
    if not decision_rows:
        return ""
    blockers = []
    for row in decision_rows:
        if clean(row.get("final_verification_decision")) == "not_final_verified":
            blockers.append(
                f"{row.get('requirement', '')}: {row.get('mechanical_raw_check_decision', '')} - {row.get('remaining_blocker', '')}"
            )
    if not blockers:
        return ""
    return "focused_raw_acceptance_blockers=" + compact(blockers, 5)


def build_registry_rows(
    queue_rows: list[dict[str, str]],
    packet_by_id: dict[str, dict[str, str]],
    receipt_by_id: dict[str, dict[str, str]],
    gates_by_id: dict[str, list[dict[str, str]]],
    acceptance_by_id: dict[str, list[dict[str, str]]],
) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    for wave in queue_rows:
        idno = clean(wave.get("idno"))
        packet = packet_by_id.get(idno, {})
        receipt = receipt_by_id.get(idno, {})
        gate_rows = gates_by_id.get(idno, [])
        acceptance_rows = acceptance_by_id.get(idno, [])
        country = clean(wave.get("country"))
        financial_status = clean(packet.get("financial_protection_status")) or "blocked"
        access_status = clean(packet.get("access_forgone_care_status")) or "blocked"
        climate_status = clean(packet.get("climate_linkage_status")) or "blocked"
        analysis_status = clean(packet.get("promoted_registry_status")) or "not_promoted"
        raw_package = clean(receipt.get("current_receipt_status")) or clean(packet.get("raw_package_status")) or "missing"
        raw_value = clean(packet.get("raw_value_verification_status")) or "blocked_not_raw_value_verified"
        financial_ready = is_ready(financial_status)
        access_ready = is_ready(access_status)
        climate_ready = accepted_climate(climate_status)
        analysis_ready = analysis_status == "promoted_analysis_ready"
        receipt_blocker = ""
        if raw_package == "blocked_no_original_package":
            receipt_blocker = "complete original raw package not received"
        blockers = compact(
            [
                receipt_blocker,
                failed_gate_blockers(gate_rows),
                focused_decision_blockers(acceptance_rows),
                "no accepted CHIRPS or ERA5 climate-linkage route" if not climate_ready else "",
                "raw values, labels, units, recall periods, missing codes, skip patterns, and merge keys not verified"
                if not financial_ready or not access_ready
                else "",
            ],
            8,
        )
        rows.append(
            {
                "country": country,
                "wave": clean(wave.get("wave")),
                "idno": idno,
                "survey_name": clean(wave.get("survey_name")),
                "priority_country": "1" if country in PRIORITY_COUNTRIES else "0",
                "source": "priority_lsms_isa_refocused_acquisition_queue",
                "official_url": clean(wave.get("official_get_microdata_url")),
                "local_target_folder": clean(wave.get("local_target_folder")),
                "rows": "0" if not analysis_ready else clean(packet.get("promoted_rows")) or "0",
                "outcome_ready_status": "outcome_ready_financial_and_access" if financial_ready and access_ready else "blocked_raw_value_verification_required",
                "sdg382_ready_status": "ready_sdg382" if financial_ready and analysis_ready else "blocked_poverty_line_ppp_cpi_discretionary_budget_not_verified",
                "che10_che25_ready_status": "ready_che10_che25" if financial_ready else "blocked_consumption_oop_units_recall_not_verified",
                "access_forgone_care_ready_status": "ready_access_forgone_care" if access_ready else "blocked_health_need_care_access_values_not_verified",
                "climate_linkage_ready_status": "accepted_chirps_or_era5_route" if climate_ready else "blocked_timing_geography_or_chirps_era5_route_not_verified",
                "analysis_ready_status": "promoted_analysis_ready" if analysis_ready else "not_promoted",
                "raw_package_status": raw_package,
                "raw_value_verification_status": raw_value,
                "promotion_packet": clean(packet.get("packet_report")) or f"report/priority_lsms_isa_country_wave_promotion_packets/{idno}.md",
                "remaining_blockers": blockers,
            }
        )
    return rows


def build_gate_rows(packet_gate_rows: list[dict[str, str]]) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    for row in packet_gate_rows:
        rows.append(
            {
                "country": clean(row.get("country")),
                "wave": clean(row.get("wave")),
                "idno": clean(row.get("idno")),
                "gate": clean(row.get("gate")),
                "status": clean(row.get("status")),
                "evidence": clean(row.get("evidence")),
                "required_action": clean(row.get("required_action")),
            }
        )
    return rows


def build_download_queue(registry_rows: list[dict[str, str]], queue_by_id: dict[str, dict[str, str]]) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    for row in registry_rows:
        wave = queue_by_id.get(row["idno"], {})
        if row.get("analysis_ready_status") == "promoted_analysis_ready":
            continue
        if row.get("raw_package_status") == "blocked_no_original_package":
            next_action = "download_or_place_complete_original_raw_package"
            top_expected = "complete unchanged official raw package plus documentation; see per-wave receipt checklist"
        elif row.get("raw_value_verification_status") != "raw_value_verified":
            next_action = "complete_raw_value_key_unit_verification"
            top_expected = "received raw package is present; resolve remaining raw value, key, unit, recall, skip, and construct blockers"
        elif row.get("climate_linkage_ready_status") != "accepted_chirps_or_era5_route":
            next_action = "accept_chirps_or_era5_linkage_route"
            top_expected = "raw values are verified but climate timing/geography route remains blocked"
        else:
            next_action = "complete_analysis_dataset_synthesis_join_review"
            top_expected = "upstream gates are nearly ready; complete household-climate synthesis and registry write gate"
        rows.append(
            {
                "action_rank": clean(wave.get("download_priority_order")),
                "country": row["country"],
                "wave": row["wave"],
                "idno": row["idno"],
                "survey_name": row["survey_name"],
                "official_url": row["official_url"],
                "local_target_folder": row["local_target_folder"],
                "raw_package_status": row["raw_package_status"],
                "top_expected_files_or_modules": top_expected,
                "promotion_packet": row["promotion_packet"],
                "next_action": next_action,
            }
        )
    return sorted(rows, key=lambda r: safe_int(r.get("action_rank"), 999999))


def build_summary(registry_rows: list[dict[str, str]], queue_rows: list[dict[str, str]], gate_rows: list[dict[str, str]]) -> list[dict[str, str]]:
    queue_ids = {clean(row.get("idno")) for row in queue_rows if clean(row.get("idno"))}
    registry_ids = {clean(row.get("idno")) for row in registry_rows if clean(row.get("idno"))}
    priority_countries_ready = {
        row["country"]
        for row in registry_rows
        if row.get("priority_country") == "1" and row.get("che10_che25_ready_status") == "ready_che10_che25"
    }
    double_failure_ready = [
        row
        for row in registry_rows
        if row.get("che10_che25_ready_status") == "ready_che10_che25"
        and row.get("access_forgone_care_ready_status") == "ready_access_forgone_care"
    ]
    accepted_climate_rows = [
        row for row in registry_rows if row.get("climate_linkage_ready_status") == "accepted_chirps_or_era5_route"
    ]
    promoted_rows = [row for row in registry_rows if row.get("analysis_ready_status") == "promoted_analysis_ready"]
    gate_counts = Counter(row.get("status", "") for row in gate_rows)
    role_counts = Counter(clean(row.get("queue_role")) for row in queue_rows)
    threshold_open = len(priority_countries_ready) >= 6 and len(double_failure_ready) >= 10 and len(accepted_climate_rows) >= 1
    rows = [
        {"metric": "registry_rows", "value": str(len(registry_rows)), "interpretation": "Country-waves currently tracked in the promoted registry."},
        {"metric": "refocused_queue_rows", "value": str(len(queue_rows)), "interpretation": "Refocused LSMS/ISA acquisition queue rows that should be represented in the registry."},
        {"metric": "refocused_registry_coverage_rows", "value": str(len(queue_ids & registry_ids)), "interpretation": "Refocused queue rows covered by the promoted registry."},
        {"metric": "refocused_missing_from_registry_rows", "value": str(len(queue_ids - registry_ids)), "interpretation": "Refocused queue rows missing from the promoted registry; must be zero."},
        {"metric": "registry_extra_non_refocused_rows", "value": str(len(registry_ids - queue_ids)), "interpretation": "Registry rows outside the current refocused LSMS/ISA target; should be zero for this campaign."},
        {"metric": "priority_country_rows", "value": str(sum(1 for row in registry_rows if row.get("priority_country") == "1")), "interpretation": "Rows from Ethiopia, Nigeria, Malawi, Tanzania, and Uganda."},
        {"metric": "refocused_core_country_wave_rows", "value": str(role_counts.get("core_selected_lsms_isa_aligned", 0) + role_counts.get("core_replacement_primary", 0)), "interpretation": "Core country-waves in the refocused LSMS/ISA plan."},
        {"metric": "refocused_backup_country_wave_rows", "value": str(len(queue_rows) - role_counts.get("core_selected_lsms_isa_aligned", 0) - role_counts.get("core_replacement_primary", 0)), "interpretation": "Backup waves retained for raw-review failure risk and sixth-country coverage."},
        {"metric": "promoted_analysis_ready_rows", "value": str(len(promoted_rows)), "interpretation": "Rows allowed into promoted analysis data."},
        {"metric": "financial_protection_ready_countries", "value": str(len(priority_countries_ready)), "interpretation": "Countries meeting value-verified CHE financial-protection requirements."},
        {"metric": "double_failure_ready_country_waves", "value": str(len(double_failure_ready)), "interpretation": "Country-waves with both financial protection and access/forgone-care ready."},
        {"metric": "accepted_chirps_era5_climate_linkage_rows", "value": str(len(accepted_climate_rows)), "interpretation": "Country-waves with accepted CHIRPS or ERA5 linkage route."},
        {"metric": "raw_package_received_rows", "value": str(sum(1 for row in registry_rows if row.get("raw_package_status") != "blocked_no_original_package")), "interpretation": "Registry rows with some non-generated raw package receipt evidence."},
        {"metric": "raw_value_verified_rows", "value": str(sum(1 for row in registry_rows if row.get("raw_value_verification_status") == "raw_value_verified")), "interpretation": "Registry rows with accepted raw-value verification."},
        {"metric": "gate_pass_rows", "value": str(gate_counts.get("pass", 0)), "interpretation": "Promotion gate rows passing in the refocused packet matrix."},
        {"metric": "gate_fail_rows", "value": str(gate_counts.get("fail", 0)), "interpretation": "Promotion gate rows failing in the refocused packet matrix."},
        {"metric": "albania_main_case_rows", "value": str(sum(1 for row in registry_rows if row.get("country") == "Albania")), "interpretation": "Albania rows in the main refocused promoted registry; should remain zero."},
        {"metric": "promoted_registry_data_write_status", "value": "blocked_no_promoted_rows" if not promoted_rows else "open_registry_has_promoted_rows", "interpretation": "Data write gate implied by the promoted registry."},
        {"metric": "modeling_gate_status", "value": "open" if threshold_open else "blocked", "interpretation": "Do not run predictive, reduced-form, causal ML, or policy-learning models until registry thresholds pass."},
    ]
    return rows


def markdown_table(rows: list[dict[str, str]], columns: list[str], limit: int = 30) -> str:
    lines = ["| " + " | ".join(columns) + " |", "|" + "|".join("---" for _ in columns) + "|"]
    for row in rows[:limit]:
        values = []
        for column in columns:
            value = clean(row.get(column)).replace("|", "/")
            if len(value) > 120:
                value = value[:117] + "..."
            values.append(value)
        lines.append("| " + " | ".join(values) + " |")
    return "\n".join(lines)


def write_report(registry_rows: list[dict[str, str]], gate_rows: list[dict[str, str]], summary_rows: list[dict[str, str]]) -> None:
    summary_table = "\n".join(f"| {row['metric']} | {row['value']} | {row['interpretation']} |" for row in summary_rows)
    REPORT_PATH.write_text(
        f"""# Country-Wave Promotion Registry

Status: fail-closed promoted registry refreshed to the 19-wave LSMS/ISA
refocused acquisition queue. This is the controlling registry for promoted
multi-country household-climate data writes.

Albania is excluded from the main promoted registry and remains a diagnostic
template only unless its historical boundary, timing, and outcome gates are
resolved.

## Summary

| Metric | Value | Interpretation |
|---|---:|---|
{summary_table}

## Registry Preview

{markdown_table(registry_rows, ['country', 'wave', 'idno', 'priority_country', 'raw_package_status', 'raw_value_verification_status', 'climate_linkage_ready_status', 'analysis_ready_status', 'remaining_blockers'], 30)}

## Gate Audit Preview

{markdown_table(gate_rows, ['country', 'wave', 'idno', 'gate', 'status', 'required_action'], 40)}

## Machine-Readable Outputs

- `result/promoted_country_wave_registry.csv`
- `result/country_wave_promotion_gate_audit.csv`
- `result/country_wave_promotion_summary.csv`
- `result/priority_country_wave_download_queue.csv`

## Stop Rules

- No row may write to `data/` until `analysis_ready_status` is `promoted_analysis_ready`.
- Modeling remains blocked until the registry contains at least 6 value-verified financial-protection countries, 10 value-verified double-failure country-waves, and at least one accepted CHIRPS or ERA5 linkage route.
""",
        encoding="utf-8",
    )


def main() -> None:
    ensure_dirs()
    queue_rows = read_csv_dicts(QUEUE_PATH)
    packet_rows = read_csv_dicts(PACKET_INDEX_PATH)
    packet_gate_rows = read_csv_dicts(PACKET_GATE_PATH)
    receipt_rows = read_csv_dicts(RECEIPT_PATH)
    acceptance_rows = read_csv_dicts(MWI2004_ACCEPTANCE_DECISION_PATH)

    queue_by_id = one_by_id(queue_rows)
    registry_rows = build_registry_rows(
        queue_rows,
        one_by_id(packet_rows),
        one_by_id(receipt_rows),
        by_id(packet_gate_rows),
        by_id(acceptance_rows),
    )
    gate_rows = build_gate_rows(packet_gate_rows)
    download_rows = build_download_queue(registry_rows, queue_by_id)
    summary_rows = build_summary(registry_rows, queue_rows, gate_rows)

    write_csv(REGISTRY_PATH, registry_rows, REGISTRY_COLUMNS)
    write_csv(GATE_AUDIT_PATH, gate_rows, GATE_COLUMNS)
    write_csv(SUMMARY_PATH, summary_rows, SUMMARY_COLUMNS)
    write_csv(DOWNLOAD_QUEUE_PATH, download_rows, QUEUE_COLUMNS)
    write_report(registry_rows, gate_rows, summary_rows)
    append_log(
        TEMP_DIR / "audit_log.md",
        f"Refreshed promoted country-wave registry to refocused LSMS/ISA queue rows={len(registry_rows)} gates={len(gate_rows)}.",
    )
    print(
        "Refocused promoted country-wave registry "
        f"rows={len(registry_rows)} gates={len(gate_rows)} download_queue={len(download_rows)}."
    )


if __name__ == "__main__":
    main()
