from __future__ import annotations

import csv
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

from common import REPORT_DIR, RESULT_DIR, TEMP_DIR, append_log, ensure_dirs, write_csv


ACTION_QUEUE_PATH = TEMP_DIR / "priority_lsms_isa_next_raw_package_action_queue.csv"
MINIMUM_BATCH_PATH = TEMP_DIR / "priority_lsms_isa_threshold_minimum_batch.csv"
REGISTRY_PATH = RESULT_DIR / "promoted_country_wave_registry.csv"
RECEIPT_VALIDATION_PATH = TEMP_DIR / "priority_lsms_isa_official_file_receipt_validation.csv"
CORE_MATCH_PATH = TEMP_DIR / "priority_lsms_isa_official_file_receipt_core_match.csv"
SCHEMA_EVIDENCE_PATH = TEMP_DIR / "priority_lsms_isa_received_raw_requirement_evidence.csv"
VALUE_REQUIREMENT_PATH = TEMP_DIR / "priority_lsms_isa_received_raw_value_requirement_profile.csv"
SEMANTICS_REQUIREMENT_PATH = TEMP_DIR / "priority_lsms_isa_received_raw_semantics_requirement_review.csv"
ENDPOINT_STATUS_PATH = TEMP_DIR / "priority_lsms_isa_minimum_batch_endpoint_dataset_status.csv"

DASHBOARD_PATH = TEMP_DIR / "priority_lsms_isa_promotion_gate_dashboard.csv"
REQUIREMENT_DASHBOARD_PATH = TEMP_DIR / "priority_lsms_isa_promotion_gate_requirement_dashboard.csv"
SUMMARY_PATH = RESULT_DIR / "priority_lsms_isa_promotion_gate_dashboard_summary.csv"
REPORT_PATH = REPORT_DIR / "priority_lsms_isa_promotion_gate_dashboard.md"

REQUIRED_REQUIREMENTS = [
    "household_person_keys",
    "weights_and_design",
    "consumption_or_income",
    "oop_health_expenditure",
    "health_need_and_access",
    "survey_timing",
    "climate_geography",
    "missing_codes_units_recall_skip_patterns",
]

DASHBOARD_COLUMNS = [
    "promotion_rank",
    "promotion_tier",
    "country",
    "wave",
    "idno",
    "registry_analysis_ready_status",
    "registry_rows",
    "raw_package_status",
    "raw_value_verification_status",
    "endpoint_refresh_status",
    "credentialed_download_required",
    "official_file_receipt_status",
    "official_core_match_rate",
    "receipt_gate_status",
    "schema_gate_status",
    "value_profile_gate_status",
    "semantics_gate_status",
    "climate_linkage_gate_status",
    "data_write_gate_status",
    "promotion_readiness_status",
    "next_required_gate",
    "blocking_reasons",
]

REQUIREMENT_COLUMNS = [
    "promotion_rank",
    "promotion_tier",
    "country",
    "wave",
    "idno",
    "requirement",
    "official_core_file_rows",
    "official_core_matched_rows",
    "official_core_missing_rows",
    "schema_candidate_rows",
    "schema_present_rows",
    "value_profile_status",
    "semantics_review_status",
    "requirement_gate_status",
    "next_required_action",
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


def safe_float(value: Any, default: float = 0.0) -> float:
    try:
        text = clean(value)
        return float(text) if text else default
    except (TypeError, ValueError):
        return default


def one_by_id(rows: list[dict[str, str]], field: str = "idno") -> dict[str, dict[str, str]]:
    out: dict[str, dict[str, str]] = {}
    for row in rows:
        key = clean(row.get(field))
        if key and key not in out:
            out[key] = row
    return out


def by_id_requirement(rows: list[dict[str, str]], requirement_field: str = "requirement") -> dict[str, dict[str, list[dict[str, str]]]]:
    out: dict[str, dict[str, list[dict[str, str]]]] = defaultdict(lambda: defaultdict(list))
    for row in rows:
        idno = clean(row.get("idno"))
        requirement = clean(row.get(requirement_field))
        if idno and requirement:
            out[idno][requirement].append(row)
    return out


def markdown_table(rows: list[dict[str, str]], columns: list[str], limit: int = 30) -> str:
    if not rows:
        return "_No rows._"
    lines = ["| " + " | ".join(columns) + " |", "| " + " | ".join("---" for _ in columns) + " |"]
    for row in rows[:limit]:
        values = []
        for column in columns:
            value = clean(row.get(column)).replace("|", "/")
            if len(value) > 120:
                value = value[:117] + "..."
            values.append(value)
        lines.append("| " + " | ".join(values) + " |")
    if len(rows) > limit:
        lines.append("| " + " | ".join("..." for _ in columns) + " |")
    return "\n".join(lines)


def core_counts(rows: list[dict[str, str]]) -> tuple[int, int, int]:
    total = len(rows)
    matched = sum(1 for row in rows if clean(row.get("official_core_file_match_status")) == "matched")
    return total, matched, total - matched


def schema_counts(rows: list[dict[str, str]]) -> tuple[int, int]:
    total = len(rows)
    present = sum(1 for row in rows if clean(row.get("raw_variable_present")) == "1")
    return total, present


def value_status(rows: list[dict[str, str]]) -> str:
    if not rows:
        return "blocked_no_value_profile"
    statuses = {clean(row.get("value_profile_requirement_status")) for row in rows}
    if "raw_value_verified" in statuses or "value_verified" in statuses:
        return "raw_value_verified"
    if any(status.startswith("value_profile_available") for status in statuses):
        return "value_profile_available_not_value_verified"
    return sorted(statuses)[0] if statuses else "blocked_no_value_profile"


def semantics_status(rows: list[dict[str, str]]) -> str:
    if not rows:
        return "blocked_no_semantics_review"
    statuses = {clean(row.get("semantics_requirement_status")) for row in rows}
    if "semantics_verified" in statuses:
        return "semantics_verified"
    if any(status.startswith("semantics_review_available") for status in statuses):
        return "semantics_review_available_not_value_verified"
    return sorted(statuses)[0] if statuses else "blocked_no_semantics_review"


def requirement_gate(
    promoted: bool,
    receipt_complete: bool,
    core_total: int,
    core_missing: int,
    schema_total: int,
    schema_present: int,
    value_gate: str,
    semantics_gate: str,
) -> tuple[str, str]:
    if promoted:
        return "accepted_via_promoted_registry", "No action for this dashboard; keep registry/data lineage reproducible."
    if not receipt_complete:
        return "blocked_raw_package_not_received", "Download/place the complete unchanged official package and documentation."
    if core_total <= 0:
        return "blocked_no_official_core_file_expectation", "Refresh official DDI/core-file manifest before promotion review."
    if core_missing > 0:
        return "blocked_official_core_files_missing", "Add the missing official core files or archive members and rerun receipt validation."
    if schema_total <= 0 or schema_present < schema_total:
        return "blocked_schema_evidence_incomplete", "Run received raw schema audit and resolve unreadable or missing variables."
    if value_gate != "raw_value_verified":
        return "blocked_value_profile_not_manually_verified", "Review units, recall periods, missing codes, skip patterns, and acceptance decisions."
    if semantics_gate != "semantics_verified":
        return "blocked_semantics_not_accepted", "Accept requirement semantics against questionnaire/codebook evidence."
    return "ready_for_country_wave_promotion_packet", "Refresh promotion packet and promoted registry."


def build_seed_rows(
    registry_rows: list[dict[str, str]],
    action_rows: list[dict[str, str]],
    minimum_rows: list[dict[str, str]],
) -> list[dict[str, str]]:
    registry_by_id = one_by_id(registry_rows)
    action_by_id = one_by_id(action_rows)
    minimum_ids = [clean(row.get("idno")) for row in minimum_rows if clean(row.get("idno"))]

    seeds: list[dict[str, str]] = []
    seen: set[str] = set()
    promoted = [
        row
        for row in registry_rows
        if clean(row.get("analysis_ready_status")) == "promoted_analysis_ready"
        and safe_int(row.get("rows")) > 0
    ]
    for row in promoted:
        idno = clean(row.get("idno"))
        seeds.append(
            {
                "promotion_rank": str(len(seeds) + 1),
                "promotion_tier": "current_promoted_registry",
                "country": clean(row.get("country")),
                "wave": clean(row.get("wave")),
                "idno": idno,
            }
        )
        seen.add(idno)

    for row in action_rows:
        idno = clean(row.get("idno"))
        if not idno or idno in seen:
            continue
        seeds.append(
            {
                "promotion_rank": str(len(seeds) + 1),
                "promotion_tier": clean(row.get("acquisition_tier")) or ("minimum_batch_remaining" if idno in minimum_ids else "backup_after_minimum_batch"),
                "country": clean(row.get("country")) or clean(registry_by_id.get(idno, {}).get("country")),
                "wave": clean(row.get("wave")) or clean(registry_by_id.get(idno, {}).get("wave")),
                "idno": idno,
            }
        )
        seen.add(idno)

    for idno in minimum_ids:
        if idno in seen:
            continue
        row = registry_by_id.get(idno, action_by_id.get(idno, {}))
        seeds.append(
            {
                "promotion_rank": str(len(seeds) + 1),
                "promotion_tier": "minimum_batch_unqueued_review",
                "country": clean(row.get("country")),
                "wave": clean(row.get("wave")),
                "idno": idno,
            }
        )
        seen.add(idno)
    return seeds


def build_dashboards() -> tuple[list[dict[str, str]], list[dict[str, str]], list[dict[str, str]]]:
    registry_by_id = one_by_id(read_csv_dicts(REGISTRY_PATH))
    receipt_by_id = one_by_id(read_csv_dicts(RECEIPT_VALIDATION_PATH))
    endpoint_by_id = one_by_id(read_csv_dicts(ENDPOINT_STATUS_PATH))
    core_by_req = by_id_requirement(read_csv_dicts(CORE_MATCH_PATH))
    schema_by_req = by_id_requirement(read_csv_dicts(SCHEMA_EVIDENCE_PATH))
    value_by_req = by_id_requirement(read_csv_dicts(VALUE_REQUIREMENT_PATH))
    semantics_by_req = by_id_requirement(read_csv_dicts(SEMANTICS_REQUIREMENT_PATH))

    seeds = build_seed_rows(
        read_csv_dicts(REGISTRY_PATH),
        read_csv_dicts(ACTION_QUEUE_PATH),
        read_csv_dicts(MINIMUM_BATCH_PATH),
    )

    dashboard_rows: list[dict[str, str]] = []
    requirement_rows: list[dict[str, str]] = []

    for seed in seeds:
        idno = seed["idno"]
        registry = registry_by_id.get(idno, {})
        receipt = receipt_by_id.get(idno, {})
        endpoint = endpoint_by_id.get(idno, {})
        promoted = clean(registry.get("analysis_ready_status")) == "promoted_analysis_ready" and safe_int(registry.get("rows")) > 0
        receipt_status = clean(receipt.get("official_file_receipt_status")) or "blocked_no_receipt_validation"
        receipt_complete = receipt_status == "official_file_receipt_complete_pending_schema_value_review" or promoted
        core_match_rate = clean(receipt.get("official_core_match_rate")) or ("1.000" if promoted else "0.000")
        core_rate = safe_float(core_match_rate)

        requirement_statuses: list[str] = []
        blockers: list[str] = []
        for requirement in REQUIRED_REQUIREMENTS:
            core_total, core_matched, core_missing = core_counts(core_by_req.get(idno, {}).get(requirement, []))
            schema_total, schema_present = schema_counts(schema_by_req.get(idno, {}).get(requirement, []))
            value_gate = value_status(value_by_req.get(idno, {}).get(requirement, []))
            sem_gate = semantics_status(semantics_by_req.get(idno, {}).get(requirement, []))
            gate, next_action = requirement_gate(
                promoted,
                receipt_complete,
                core_total,
                core_missing,
                schema_total,
                schema_present,
                value_gate,
                sem_gate,
            )
            requirement_statuses.append(gate)
            if gate != "accepted_via_promoted_registry" and gate != "ready_for_country_wave_promotion_packet":
                blockers.append(f"{requirement}:{gate}")
            requirement_rows.append(
                {
                    "promotion_rank": seed["promotion_rank"],
                    "promotion_tier": seed["promotion_tier"],
                    "country": seed["country"],
                    "wave": seed["wave"],
                    "idno": idno,
                    "requirement": requirement,
                    "official_core_file_rows": str(core_total),
                    "official_core_matched_rows": str(core_matched),
                    "official_core_missing_rows": str(core_missing),
                    "schema_candidate_rows": str(schema_total),
                    "schema_present_rows": str(schema_present),
                    "value_profile_status": value_gate,
                    "semantics_review_status": sem_gate,
                    "requirement_gate_status": gate,
                    "next_required_action": next_action,
                }
            )

        if promoted:
            receipt_gate = "passed_promoted_registry"
            schema_gate = "passed_promoted_registry"
            value_gate_status = "passed_promoted_registry"
            semantics_gate = "passed_promoted_registry"
            climate_gate = clean(registry.get("climate_linkage_ready_status")) or "accepted_chirps_or_era5_route"
            data_gate = "open_promoted_registry_row"
            readiness = "promoted_analysis_ready"
            next_gate = "none"
            blocking_reasons = ""
        elif not receipt_complete:
            receipt_gate = "blocked_raw_package_not_received"
            schema_gate = "not_started"
            value_gate_status = "not_started"
            semantics_gate = "not_started"
            climate_gate = "blocked_timing_geography_or_chirps_era5_route_not_verified"
            data_gate = "blocked_no_data_write"
            readiness = "blocked_at_raw_package_receipt"
            next_gate = "download_place_complete_official_raw_package"
            blocking_reasons = "; ".join(blockers[:8]) or "complete original raw package not received"
        elif core_rate < 1:
            receipt_gate = "blocked_official_core_files_missing"
            schema_gate = "not_started"
            value_gate_status = "not_started"
            semantics_gate = "not_started"
            climate_gate = "blocked_timing_geography_or_chirps_era5_route_not_verified"
            data_gate = "blocked_no_data_write"
            readiness = "blocked_at_official_file_receipt"
            next_gate = "resolve_missing_official_core_files"
            blocking_reasons = "; ".join(blockers[:8])
        elif all(status == "ready_for_country_wave_promotion_packet" for status in requirement_statuses):
            receipt_gate = "passed_official_file_receipt"
            schema_gate = "passed_schema_evidence"
            value_gate_status = "passed_raw_value_verification"
            semantics_gate = "passed_semantics_review"
            climate_gate = "pending_climate_linkage_acceptance"
            data_gate = "blocked_until_registry_refresh"
            readiness = "ready_for_country_wave_promotion_packet"
            next_gate = "refresh_promotion_packet_and_climate_route"
            blocking_reasons = "climate-linkage and registry refresh still required"
        else:
            receipt_gate = "passed_official_file_receipt"
            schema_gate = "schema_or_requirement_review_incomplete"
            value_gate_status = "value_profile_not_raw_value_verified"
            semantics_gate = "semantics_not_accepted"
            climate_gate = "blocked_timing_geography_or_chirps_era5_route_not_verified"
            data_gate = "blocked_no_data_write"
            readiness = "blocked_after_receipt_before_value_verification"
            next_gate = "complete_schema_value_semantics_requirement_reviews"
            blocking_reasons = "; ".join(blockers[:8])

        dashboard_rows.append(
            {
                "promotion_rank": seed["promotion_rank"],
                "promotion_tier": seed["promotion_tier"],
                "country": seed["country"],
                "wave": seed["wave"],
                "idno": idno,
                "registry_analysis_ready_status": clean(registry.get("analysis_ready_status")) or "not_promoted",
                "registry_rows": clean(registry.get("rows")) or "0",
                "raw_package_status": clean(registry.get("raw_package_status")) or ("ready_for_raw_value_review" if receipt_complete else "blocked_no_original_package"),
                "raw_value_verification_status": clean(registry.get("raw_value_verification_status")) or "blocked_not_raw_value_verified",
                "endpoint_refresh_status": clean(endpoint.get("endpoint_refresh_status")) or "not_in_minimum_endpoint_refresh",
                "credentialed_download_required": clean(endpoint.get("credentialed_download_required")) or ("0" if promoted else "1"),
                "official_file_receipt_status": receipt_status,
                "official_core_match_rate": core_match_rate,
                "receipt_gate_status": receipt_gate,
                "schema_gate_status": schema_gate,
                "value_profile_gate_status": value_gate_status,
                "semantics_gate_status": semantics_gate,
                "climate_linkage_gate_status": climate_gate,
                "data_write_gate_status": data_gate,
                "promotion_readiness_status": readiness,
                "next_required_gate": next_gate,
                "blocking_reasons": blocking_reasons,
            }
        )

    status_counts = Counter(row["promotion_readiness_status"] for row in dashboard_rows)
    tier_counts = Counter(row["promotion_tier"] for row in dashboard_rows)
    req_counts = Counter(row["requirement_gate_status"] for row in requirement_rows)
    summary_rows = [
        {"metric": "priority_lsms_promotion_gate_country_wave_rows", "value": str(len(dashboard_rows)), "interpretation": "Country-waves tracked in the promotion-gate dashboard."},
        {"metric": "priority_lsms_promotion_gate_requirement_rows", "value": str(len(requirement_rows)), "interpretation": "Requirement-level gate rows tracked across country-waves."},
        {"metric": "priority_lsms_promotion_gate_promoted_rows", "value": str(status_counts.get("promoted_analysis_ready", 0)), "interpretation": "Rows already promoted analysis-ready in the registry."},
        {"metric": "priority_lsms_promotion_gate_blocked_raw_package_rows", "value": str(status_counts.get("blocked_at_raw_package_receipt", 0)), "interpretation": "Rows still blocked because complete official raw package receipt is missing."},
        {"metric": "priority_lsms_promotion_gate_ready_for_packet_rows", "value": str(status_counts.get("ready_for_country_wave_promotion_packet", 0)), "interpretation": "Rows whose requirement gates are ready for a promotion packet but are not yet in data/."},
        {"metric": "priority_lsms_promotion_gate_minimum_remaining_rows", "value": str(tier_counts.get("minimum_batch_remaining", 0)), "interpretation": "Unpromoted minimum-batch rows still tracked here."},
        {"metric": "priority_lsms_promotion_gate_backup_rows", "value": str(tier_counts.get("backup_after_minimum_batch", 0)), "interpretation": "Backup rows tracked after the minimum batch."},
        {"metric": "priority_lsms_promotion_gate_requirement_blocked_raw_package_rows", "value": str(req_counts.get("blocked_raw_package_not_received", 0)), "interpretation": "Requirement rows blocked at raw package receipt."},
        {"metric": "data_write_gate_status", "value": "blocked_for_unpromoted_rows", "interpretation": "No new unpromoted country-wave may be written to data/ from this dashboard."},
        {"metric": "modeling_gate_status", "value": "blocked", "interpretation": "No predictive, reduced-form, causal ML, or policy learning until registry thresholds pass."},
    ]
    for status, count in sorted(status_counts.items()):
        summary_rows.append({"metric": f"priority_lsms_promotion_gate_status_{status}", "value": str(count), "interpretation": "Country-wave count by promotion readiness status."})
    for status, count in sorted(req_counts.items()):
        summary_rows.append({"metric": f"priority_lsms_promotion_gate_requirement_status_{status}", "value": str(count), "interpretation": "Requirement-row count by gate status."})
    return dashboard_rows, requirement_rows, summary_rows


def write_report(dashboard_rows: list[dict[str, str]], requirement_rows: list[dict[str, str]], summary_rows: list[dict[str, str]]) -> None:
    blocked = [row for row in dashboard_rows if row["promotion_readiness_status"] != "promoted_analysis_ready"]
    REPORT_PATH.write_text(
        f"""# Priority LSMS/ISA Promotion Gate Dashboard

Status: raw-package-to-promotion gate dashboard for the refocused LSMS/ISA
country-wave queue.

This dashboard does not download raw data and does not write new `data/`
outputs. It combines the current registry, official file receipt validator,
received raw schema audit, value profile, and semantics review into one
country-wave gate view.

## Summary

{markdown_table(summary_rows, ['metric', 'value', 'interpretation'], 40)}

## Country-Wave Gate View

{markdown_table(dashboard_rows, ['promotion_rank', 'promotion_tier', 'country', 'wave', 'idno', 'promotion_readiness_status', 'next_required_gate'], 40)}

## Blocked Rows

{markdown_table(blocked, ['promotion_rank', 'country', 'wave', 'idno', 'official_file_receipt_status', 'promotion_readiness_status', 'next_required_gate'], 40)}

## Requirement Gate Preview

{markdown_table(requirement_rows, ['promotion_rank', 'idno', 'requirement', 'requirement_gate_status', 'next_required_action'], 80)}

## Rule

Only rows with `promoted_analysis_ready` in
`result/promoted_country_wave_registry.csv` can be represented in `data/`.
Rows that merely have metadata, endpoint evidence, or public documentation
remain blocked until complete official raw packages and raw-backed value,
semantics, timing, geography, and climate-linkage gates pass.
""",
        encoding="utf-8",
    )


def main() -> None:
    ensure_dirs()
    dashboard_rows, requirement_rows, summary_rows = build_dashboards()
    write_csv(DASHBOARD_PATH, dashboard_rows, DASHBOARD_COLUMNS)
    write_csv(REQUIREMENT_DASHBOARD_PATH, requirement_rows, REQUIREMENT_COLUMNS)
    write_csv(SUMMARY_PATH, summary_rows, SUMMARY_COLUMNS)
    write_report(dashboard_rows, requirement_rows, summary_rows)
    append_log(
        TEMP_DIR / "audit_log.md",
        f"Built priority LSMS/ISA promotion gate dashboard rows={len(dashboard_rows)} requirements={len(requirement_rows)}.",
    )
    print(f"Priority LSMS/ISA promotion gate dashboard rows={len(dashboard_rows)} requirements={len(requirement_rows)}.")


if __name__ == "__main__":
    main()
