from __future__ import annotations

import csv
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

from common import PROJECT_ROOT, REPORT_DIR, RESULT_DIR, TEMP_DIR, append_log, ensure_dirs, write_csv


QUEUE_PATH = TEMP_DIR / "priority_lsms_isa_refocused_acquisition_queue.csv"
CREDENTIALED_PATH = TEMP_DIR / "priority_lsms_isa_credentialed_raw_acquisition_workbench.csv"
OFFICIAL_FILE_RECEIPT_PATH = TEMP_DIR / "priority_lsms_isa_official_file_receipt_validation.csv"
PACKET_INDEX_PATH = TEMP_DIR / "priority_lsms_isa_country_wave_promotion_packet_index.csv"
REGISTRY_PATH = RESULT_DIR / "promoted_country_wave_registry.csv"

SEQUENCE_PATH = TEMP_DIR / "priority_lsms_isa_threshold_download_sequence.csv"
MINIMUM_BATCH_PATH = TEMP_DIR / "priority_lsms_isa_threshold_minimum_batch.csv"
COUNTRY_COVERAGE_PATH = TEMP_DIR / "priority_lsms_isa_threshold_country_coverage.csv"
SUMMARY_PATH = RESULT_DIR / "priority_lsms_isa_threshold_download_sequence_summary.csv"
REPORT_PATH = REPORT_DIR / "priority_lsms_isa_threshold_download_sequence.md"

RAW_ROOT = TEMP_DIR / "raw_downloads"

PRIORITY_COUNTRIES = {"Ethiopia", "Nigeria", "Malawi", "Tanzania", "Uganda"}

POST_DOWNLOAD_COMMANDS = (
    "python script/17_audit_raw_downloads.py; "
    "python script/144_build_priority_lsms_isa_raw_package_intake_packet.py; "
    "python script/145_build_priority_lsms_isa_archive_member_preflight.py; "
    "python script/150_build_priority_lsms_isa_raw_package_receipt_checklist.py; "
    "python script/152_build_priority_lsms_isa_credentialed_raw_acquisition_workbench.py; "
    "python script/153_validate_priority_lsms_isa_official_file_receipt.py; "
    "python script/154_build_priority_lsms_isa_threshold_download_sequence.py; "
    "python script/155_build_priority_lsms_isa_minimum_batch_raw_intake_guide.py; "
    "python script/149_build_priority_lsms_isa_raw_value_verification_workbook.py; "
    "python script/132_build_priority_analysis_dataset_synthesis_blueprint.py; "
    "python script/148_build_priority_lsms_isa_country_wave_promotion_packets.py; "
    "python script/151_refresh_refocused_promoted_country_wave_registry.py; "
    "python script/127_enforce_promoted_data_gate.py; "
    "python script/36_build_direct_read_audit_bundle.py; "
    "python script/14_validate_workspace.py"
)

SEQUENCE_COLUMNS = [
    "threshold_sequence_rank",
    "download_priority_order",
    "threshold_phase",
    "threshold_download_role",
    "in_minimum_threshold_batch",
    "in_recommended_threshold_batch",
    "in_full_refocused_queue",
    "queue_role",
    "country",
    "wave",
    "idno",
    "survey_name",
    "candidate_family",
    "metadata_feasibility_score",
    "metadata_requirement_score",
    "official_get_microdata_url",
    "register_url",
    "terms_url",
    "local_target_folder",
    "official_expected_file_rows",
    "official_expected_matched_rows",
    "official_expected_missing_rows",
    "official_core_file_rows",
    "official_core_matched_rows",
    "official_core_missing_rows",
    "official_file_receipt_status",
    "credentialed_acquisition_status",
    "promoted_registry_status",
    "raw_package_status",
    "raw_value_verification_status",
    "financial_protection_status",
    "access_forgone_care_status",
    "climate_linkage_status",
    "analysis_ready_status",
    "next_manual_action",
    "post_download_validation_commands",
    "promotion_stop_rule",
    "handoff_readme",
]

COUNTRY_COLUMNS = [
    "country",
    "priority_country",
    "planned_country_wave_rows",
    "minimum_threshold_batch_rows",
    "recommended_threshold_batch_rows",
    "full_refocused_queue_rows",
    "core_country_wave_rows",
    "sixth_country_candidate_rows",
    "replacement_backup_rows",
    "raw_package_received_rows",
    "official_expected_file_rows",
    "official_expected_matched_rows",
    "official_core_file_rows",
    "official_core_matched_rows",
    "promoted_analysis_ready_rows",
    "financial_protection_ready_rows",
    "double_failure_ready_rows",
    "accepted_climate_linkage_rows",
    "threshold_contribution",
    "next_action",
]

SUMMARY_COLUMNS = ["metric", "value", "interpretation"]


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


def rel(path: Path) -> str:
    try:
        return str(path.relative_to(PROJECT_ROOT)).replace("\\", "/")
    except ValueError:
        return str(path).replace("\\", "/")


def one_by_id(rows: list[dict[str, str]], field: str = "idno") -> dict[str, dict[str, str]]:
    out: dict[str, dict[str, str]] = {}
    for row in rows:
        key = clean(row.get(field))
        if key and key not in out:
            out[key] = row
    return out


def raw_folder_path(folder: str, idno: str) -> Path:
    folder_clean = clean(folder).replace("\\", "/").strip("/")
    if folder_clean:
        return PROJECT_ROOT / folder_clean
    return RAW_ROOT / idno


def family_priority(row: dict[str, str]) -> int:
    family = clean(row.get("candidate_family")).lower()
    if family.startswith("non_lsms"):
        return 1
    if "lsms_isa" in family:
        return 3
    if "lsms" in family or "living_standards" in family:
        return 2
    return 1


def sixth_candidate_sort(row: dict[str, str]) -> tuple[int, int, int, int]:
    return (
        -family_priority(row),
        -safe_int(row.get("metadata_requirement_score")),
        -safe_int(row.get("metadata_feasibility_score")),
        safe_int(row.get("download_priority_order"), 999),
    )


def core_sort(row: dict[str, str]) -> tuple[int, str]:
    return (safe_int(row.get("download_priority_order"), 999), clean(row.get("idno")))


def backup_sort(row: dict[str, str]) -> tuple[str, int, int, str]:
    return (
        clean(row.get("country")),
        -safe_int(row.get("metadata_requirement_score")),
        safe_int(row.get("download_priority_order"), 999),
        clean(row.get("idno")),
    )


def threshold_phase(queue_role: str) -> str:
    if queue_role in {"core_selected_lsms_isa_aligned", "core_replacement_primary"}:
        return "phase_1_core_10_wave_double_failure_base"
    if queue_role == "sixth_country_backup_candidate":
        return "phase_2_sixth_country_financial_protection_candidate"
    if queue_role == "replacement_backup_wave":
        return "phase_3_same_country_replacement_backup_after_primary_failure"
    return "phase_4_other_refocused_candidate"


def threshold_role(queue_role: str, sixth_rank: int | None) -> str:
    if queue_role in {"core_selected_lsms_isa_aligned", "core_replacement_primary"}:
        return "minimum_10_wave_core"
    if queue_role == "sixth_country_backup_candidate" and sixth_rank == 1:
        return "minimum_6th_country_financial_protection_candidate"
    if queue_role == "sixth_country_backup_candidate":
        return "sixth_country_failure_backup"
    if queue_role == "replacement_backup_wave":
        return "same_country_primary_failure_backup"
    return "other_refocused_candidate"


def bool_flag(value: bool) -> str:
    return "1" if value else "0"


def status_ready(value: str) -> bool:
    text = clean(value).lower()
    return text in {"1", "ready", "analysis_ready", "ready_for_analysis", "promoted", "accepted", "pass"} or text.startswith("ready_")


def next_action(row: dict[str, str]) -> str:
    if clean(row.get("official_file_receipt_status")) == "blocked_no_original_package":
        return "Download the complete unchanged official World Bank package and documentation, then place it in the target folder."
    if safe_int(row.get("official_core_missing_rows")) > 0:
        return "Locate missing core official files or archive members before raw-value review."
    if safe_int(row.get("official_expected_missing_rows")) > 0:
        return "Core files may be present, but the full official package is incomplete; resolve before promotion."
    return "Run schema, raw-value, outcome, timing, geography, and climate-linkage verification before any data write."


def promotion_stop_rule(row: dict[str, str]) -> str:
    return (
        "Do not write this country-wave into data/ until complete official file receipt, "
        "raw value verification, outcome construction, survey timing/geography, and "
        "accepted CHIRPS or ERA5 climate linkage all pass."
    )


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


def write_handoff(row: dict[str, str]) -> str:
    folder = raw_folder_path(row.get("local_target_folder", ""), row.get("idno", ""))
    folder.mkdir(parents=True, exist_ok=True)
    path = folder / "_PRIORITY_LSMS_ISA_THRESHOLD_DOWNLOAD_SEQUENCE.md"
    path.write_text(
        f"""# Priority LSMS-ISA Threshold Download Sequence

IDNO: `{row.get('idno', '')}`

Country-wave: {row.get('country', '')} {row.get('wave', '')}

Threshold sequence rank: {row.get('threshold_sequence_rank', '')}

Threshold phase: `{row.get('threshold_phase', '')}`

Threshold download role: `{row.get('threshold_download_role', '')}`

Minimum threshold batch: `{row.get('in_minimum_threshold_batch', '')}`

Recommended threshold batch: `{row.get('in_recommended_threshold_batch', '')}`

Official URL: {row.get('official_get_microdata_url', '')}

Target folder: `{row.get('local_target_folder', '')}`

Official file receipt status: `{row.get('official_file_receipt_status', '')}`

Expected official files: {row.get('official_expected_file_rows', '0')}

Expected matched files: {row.get('official_expected_matched_rows', '0')}

Core files: {row.get('official_core_file_rows', '0')}

Core matched files: {row.get('official_core_matched_rows', '0')}

## Next Action

{row.get('next_manual_action', '')}

## Post-Download Validation

`{POST_DOWNLOAD_COMMANDS}`

## Stop Rule

{row.get('promotion_stop_rule', '')}
""",
        encoding="utf-8",
    )
    return rel(path)


def ordered_queue(queue_rows: list[dict[str, str]]) -> list[dict[str, str]]:
    core_rows = [
        row for row in queue_rows
        if clean(row.get("queue_role")) in {"core_selected_lsms_isa_aligned", "core_replacement_primary"}
    ]
    sixth_rows = [row for row in queue_rows if clean(row.get("queue_role")) == "sixth_country_backup_candidate"]
    backup_rows = [row for row in queue_rows if clean(row.get("queue_role")) == "replacement_backup_wave"]
    other_rows = [
        row for row in queue_rows
        if clean(row.get("queue_role")) not in {
            "core_selected_lsms_isa_aligned",
            "core_replacement_primary",
            "sixth_country_backup_candidate",
            "replacement_backup_wave",
        }
    ]
    return sorted(core_rows, key=core_sort) + sorted(sixth_rows, key=sixth_candidate_sort) + sorted(backup_rows, key=backup_sort) + sorted(other_rows, key=core_sort)


def build_sequence_rows() -> list[dict[str, str]]:
    credentialed_by_id = one_by_id(read_csv_dicts(CREDENTIALED_PATH))
    receipt_by_id = one_by_id(read_csv_dicts(OFFICIAL_FILE_RECEIPT_PATH))
    packet_by_id = one_by_id(read_csv_dicts(PACKET_INDEX_PATH))
    registry_by_id = one_by_id(read_csv_dicts(REGISTRY_PATH))
    ordered = ordered_queue(read_csv_dicts(QUEUE_PATH))
    sixth_seen = 0
    rows: list[dict[str, str]] = []
    for rank, queue in enumerate(ordered, start=1):
        idno = clean(queue.get("idno"))
        queue_role = clean(queue.get("queue_role"))
        if queue_role == "sixth_country_backup_candidate":
            sixth_seen += 1
            sixth_rank: int | None = sixth_seen
        else:
            sixth_rank = None
        role = threshold_role(queue_role, sixth_rank)
        receipt = receipt_by_id.get(idno, {})
        credentialed = credentialed_by_id.get(idno, {})
        packet = packet_by_id.get(idno, {})
        registry = registry_by_id.get(idno, {})
        in_minimum = role in {"minimum_10_wave_core", "minimum_6th_country_financial_protection_candidate"}
        in_recommended = role in {
            "minimum_10_wave_core",
            "minimum_6th_country_financial_protection_candidate",
            "sixth_country_failure_backup",
        }
        row = {
            "threshold_sequence_rank": str(rank),
            "download_priority_order": clean(queue.get("download_priority_order")),
            "threshold_phase": threshold_phase(queue_role),
            "threshold_download_role": role,
            "in_minimum_threshold_batch": bool_flag(in_minimum),
            "in_recommended_threshold_batch": bool_flag(in_recommended),
            "in_full_refocused_queue": "1",
            "queue_role": queue_role,
            "country": clean(queue.get("country")),
            "wave": clean(queue.get("wave")),
            "idno": idno,
            "survey_name": clean(queue.get("survey_name")),
            "candidate_family": clean(queue.get("candidate_family")),
            "metadata_feasibility_score": clean(queue.get("metadata_feasibility_score")),
            "metadata_requirement_score": clean(queue.get("metadata_requirement_score")),
            "official_get_microdata_url": clean(queue.get("official_get_microdata_url")),
            "register_url": clean(credentialed.get("register_url")),
            "terms_url": clean(credentialed.get("terms_url")),
            "local_target_folder": clean(queue.get("local_target_folder")),
            "official_expected_file_rows": clean(receipt.get("official_expected_file_rows")) or "0",
            "official_expected_matched_rows": clean(receipt.get("official_expected_matched_rows")) or "0",
            "official_expected_missing_rows": clean(receipt.get("official_expected_missing_rows")) or "0",
            "official_core_file_rows": clean(receipt.get("official_core_file_rows")) or "0",
            "official_core_matched_rows": clean(receipt.get("official_core_matched_rows")) or "0",
            "official_core_missing_rows": clean(receipt.get("official_core_missing_rows")) or "0",
            "official_file_receipt_status": clean(receipt.get("official_file_receipt_status")) or "missing_official_file_receipt_validation",
            "credentialed_acquisition_status": clean(credentialed.get("credentialed_acquisition_status")) or "missing_credentialed_acquisition_status",
            "promoted_registry_status": clean(registry.get("analysis_ready_status")) or clean(packet.get("promoted_registry_status")) or "not_promoted",
            "raw_package_status": clean(registry.get("raw_package_status")) or clean(packet.get("raw_package_status")) or clean(queue.get("raw_package_status")),
            "raw_value_verification_status": clean(registry.get("raw_value_verification_status")) or clean(packet.get("raw_value_verification_status")) or "blocked_not_raw_value_verified",
            "financial_protection_status": clean(registry.get("che10_che25_ready_status")) or clean(packet.get("financial_protection_status")) or "blocked",
            "access_forgone_care_status": clean(registry.get("access_forgone_care_ready_status")) or clean(packet.get("access_forgone_care_status")) or "blocked",
            "climate_linkage_status": clean(registry.get("climate_linkage_ready_status")) or clean(packet.get("climate_linkage_status")) or "blocked",
            "analysis_ready_status": clean(registry.get("analysis_ready_status")) or clean(packet.get("analysis_synthesis_status")) or "not_promoted",
            "next_manual_action": "",
            "post_download_validation_commands": POST_DOWNLOAD_COMMANDS,
            "promotion_stop_rule": "",
            "handoff_readme": "",
        }
        row["next_manual_action"] = next_action(row)
        row["promotion_stop_rule"] = promotion_stop_rule(row)
        row["handoff_readme"] = write_handoff(row)
        rows.append(row)
    return rows


def build_country_rows(sequence_rows: list[dict[str, str]]) -> list[dict[str, str]]:
    by_country: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in sequence_rows:
        by_country[row["country"]].append(row)
    out: list[dict[str, str]] = []
    for country, rows in sorted(by_country.items()):
        minimum_rows = [row for row in rows if row["in_minimum_threshold_batch"] == "1"]
        recommended_rows = [row for row in rows if row["in_recommended_threshold_batch"] == "1"]
        core_rows = [row for row in rows if row["threshold_download_role"] == "minimum_10_wave_core"]
        sixth_rows = [row for row in rows if "6th_country" in row["threshold_download_role"] or row["threshold_download_role"] == "sixth_country_failure_backup"]
        replacement_rows = [row for row in rows if row["threshold_download_role"] == "same_country_primary_failure_backup"]
        raw_received = [
            row for row in rows
            if clean(row.get("official_file_receipt_status")) not in {"blocked_no_original_package", "missing_official_file_receipt_validation"}
        ]
        promoted = [row for row in rows if clean(row.get("analysis_ready_status")) in {"analysis_ready", "promoted"}]
        fp_ready = [row for row in rows if status_ready(row.get("financial_protection_status", ""))]
        double_ready = [
            row for row in rows
            if status_ready(row.get("financial_protection_status", "")) and status_ready(row.get("access_forgone_care_status", ""))
        ]
        climate_ready = [row for row in rows if status_ready(row.get("climate_linkage_status", ""))]
        if minimum_rows:
            contribution = "minimum_threshold_batch_country"
        elif recommended_rows:
            contribution = "recommended_sixth_country_backup"
        elif replacement_rows:
            contribution = "same_country_failure_backup"
        else:
            contribution = "not_in_threshold_batch"
        out.append(
            {
                "country": country,
                "priority_country": bool_flag(country in PRIORITY_COUNTRIES),
                "planned_country_wave_rows": str(len(rows)),
                "minimum_threshold_batch_rows": str(len(minimum_rows)),
                "recommended_threshold_batch_rows": str(len(recommended_rows)),
                "full_refocused_queue_rows": str(len(rows)),
                "core_country_wave_rows": str(len(core_rows)),
                "sixth_country_candidate_rows": str(len(sixth_rows)),
                "replacement_backup_rows": str(len(replacement_rows)),
                "raw_package_received_rows": str(len(raw_received)),
                "official_expected_file_rows": str(sum(safe_int(row.get("official_expected_file_rows")) for row in rows)),
                "official_expected_matched_rows": str(sum(safe_int(row.get("official_expected_matched_rows")) for row in rows)),
                "official_core_file_rows": str(sum(safe_int(row.get("official_core_file_rows")) for row in rows)),
                "official_core_matched_rows": str(sum(safe_int(row.get("official_core_matched_rows")) for row in rows)),
                "promoted_analysis_ready_rows": str(len(promoted)),
                "financial_protection_ready_rows": str(len(fp_ready)),
                "double_failure_ready_rows": str(len(double_ready)),
                "accepted_climate_linkage_rows": str(len(climate_ready)),
                "threshold_contribution": contribution,
                "next_action": "Download/place official packages for this country's threshold rows, then rerun receipt and value-verification gates.",
            }
        )
    return out


def build_summary(sequence_rows: list[dict[str, str]], country_rows: list[dict[str, str]], handoff_count: int) -> list[dict[str, str]]:
    role_counts = Counter(row["threshold_download_role"] for row in sequence_rows)
    phase_counts = Counter(row["threshold_phase"] for row in sequence_rows)
    minimum_rows = [row for row in sequence_rows if row["in_minimum_threshold_batch"] == "1"]
    recommended_rows = [row for row in sequence_rows if row["in_recommended_threshold_batch"] == "1"]
    raw_received = [
        row for row in sequence_rows
        if clean(row.get("official_file_receipt_status")) not in {"blocked_no_original_package", "missing_official_file_receipt_validation"}
    ]
    rows = [
        {"metric": "priority_lsms_threshold_sequence_dataset_rows", "value": str(len(sequence_rows)), "interpretation": "Refocused LSMS/ISA country-waves ordered for threshold-oriented manual download."},
        {"metric": "priority_lsms_threshold_sequence_country_rows", "value": str(len(country_rows)), "interpretation": "Countries represented in the threshold download sequence."},
        {"metric": "priority_lsms_threshold_sequence_priority_country_rows", "value": str(sum(1 for row in sequence_rows if row["country"] in PRIORITY_COUNTRIES)), "interpretation": "Rows from Ethiopia, Nigeria, Malawi, Tanzania, and Uganda."},
        {"metric": "priority_lsms_threshold_sequence_minimum_download_rows", "value": str(len(minimum_rows)), "interpretation": "Minimum manual downloads: 10 core waves plus the highest-ranked sixth-country candidate if every wave passes raw/value/climate gates."},
        {"metric": "priority_lsms_threshold_sequence_minimum_country_rows", "value": str(len({row["country"] for row in minimum_rows})), "interpretation": "Distinct countries represented by the minimum threshold batch."},
        {"metric": "priority_lsms_threshold_sequence_recommended_download_rows", "value": str(len(recommended_rows)), "interpretation": "Recommended threshold downloads: 10 core waves plus all sixth-country candidates to reduce failure risk."},
        {"metric": "priority_lsms_threshold_sequence_recommended_country_rows", "value": str(len({row["country"] for row in recommended_rows})), "interpretation": "Distinct countries represented by the recommended threshold batch."},
        {"metric": "priority_lsms_threshold_sequence_full_download_rows", "value": str(len(sequence_rows)), "interpretation": "Full refocused acquisition queue including same-country replacement backups."},
        {"metric": "priority_lsms_threshold_sequence_expected_file_rows", "value": str(sum(safe_int(row.get("official_expected_file_rows")) for row in sequence_rows)), "interpretation": "Official DDI files expected across the full refocused queue."},
        {"metric": "priority_lsms_threshold_sequence_expected_file_matched_rows", "value": str(sum(safe_int(row.get("official_expected_matched_rows")) for row in sequence_rows)), "interpretation": "Expected official files currently matched locally."},
        {"metric": "priority_lsms_threshold_sequence_core_file_rows", "value": str(sum(safe_int(row.get("official_core_file_rows")) for row in sequence_rows)), "interpretation": "Core official file rows across the full refocused queue."},
        {"metric": "priority_lsms_threshold_sequence_core_file_matched_rows", "value": str(sum(safe_int(row.get("official_core_matched_rows")) for row in sequence_rows)), "interpretation": "Core official files currently matched locally."},
        {"metric": "priority_lsms_threshold_sequence_raw_package_received_rows", "value": str(len(raw_received)), "interpretation": "Rows with any non-blocked official file receipt status."},
        {"metric": "priority_lsms_threshold_sequence_promoted_analysis_ready_rows", "value": str(sum(1 for row in sequence_rows if row.get("analysis_ready_status") in {"analysis_ready", "promoted"})), "interpretation": "Rows analysis-ready in the promoted registry."},
        {"metric": "priority_lsms_threshold_sequence_handoff_readmes_written", "value": str(handoff_count), "interpretation": "Per-wave threshold download sequence handoffs written."},
        {"metric": "priority_lsms_threshold_sequence_data_write_status", "value": "blocked_no_promoted_rows", "interpretation": "Threshold sequencing never writes promoted data."},
        {"metric": "modeling_gate_status", "value": "blocked", "interpretation": "Models remain blocked until 6 countries, 10 country-waves, and accepted CHIRPS/ERA5 linkage are value-verified."},
    ]
    for phase, count in sorted(phase_counts.items()):
        rows.append({"metric": f"priority_lsms_threshold_sequence_phase_{phase}", "value": str(count), "interpretation": "Threshold sequence row count by phase."})
    for role, count in sorted(role_counts.items()):
        rows.append({"metric": f"priority_lsms_threshold_sequence_role_{role}", "value": str(count), "interpretation": "Threshold sequence row count by download role."})
    return rows


def write_report(sequence_rows: list[dict[str, str]], minimum_rows: list[dict[str, str]], country_rows: list[dict[str, str]], summary_rows: list[dict[str, str]]) -> None:
    summary_table = "\n".join(f"| {row['metric']} | {row['value']} | {row['interpretation']} |" for row in summary_rows)
    REPORT_PATH.write_text(
        f"""# Priority LSMS-ISA Threshold Download Sequence

Status: refocused threshold-oriented manual download sequence for the
19-wave LSMS/ISA acquisition queue. This replaces the older 13-wave threshold
campaign for the current dataset-promotion objective.

It does not download raw data, accept terms, verify values, create harmonized
datasets, or write `data/`.

## Summary

| Metric | Value | Interpretation |
|---|---:|---|
{summary_table}

## Minimum Threshold Batch

This is the smallest current download set that can plausibly reach the formal
pre-modeling thresholds if every wave passes raw receipt, raw-value, outcome,
and climate-linkage gates: 10 core waves plus one sixth-country candidate.

{markdown_table(minimum_rows, ['threshold_sequence_rank', 'threshold_download_role', 'country', 'wave', 'idno', 'official_expected_file_rows', 'official_core_file_rows', 'official_file_receipt_status'], 20)}

## Full Refocused Download Sequence

{markdown_table(sequence_rows, ['threshold_sequence_rank', 'threshold_phase', 'threshold_download_role', 'country', 'wave', 'idno', 'metadata_requirement_score', 'official_file_receipt_status'], 30)}

## Country Coverage

{markdown_table(country_rows, ['country', 'priority_country', 'planned_country_wave_rows', 'minimum_threshold_batch_rows', 'recommended_threshold_batch_rows', 'threshold_contribution'], 20)}

## Outputs

- `temp/priority_lsms_isa_threshold_download_sequence.csv`
- `temp/priority_lsms_isa_threshold_minimum_batch.csv`
- `temp/priority_lsms_isa_threshold_country_coverage.csv`
- `result/priority_lsms_isa_threshold_download_sequence_summary.csv`

## Stop Rule

The sequence is only an acquisition ordering tool. Modeling and promoted
dataset writes remain blocked until the promoted registry contains at least
6 value-verified financial-protection countries, 10 value-verified
country-waves for double failure, and at least one accepted CHIRPS or ERA5
climate-linkage route.
""",
        encoding="utf-8",
    )


def main() -> None:
    ensure_dirs()
    sequence_rows = build_sequence_rows()
    minimum_rows = [row for row in sequence_rows if row["in_minimum_threshold_batch"] == "1"]
    country_rows = build_country_rows(sequence_rows)
    summary_rows = build_summary(sequence_rows, country_rows, sum(1 for row in sequence_rows if row.get("handoff_readme")))
    write_csv(SEQUENCE_PATH, sequence_rows, SEQUENCE_COLUMNS)
    write_csv(MINIMUM_BATCH_PATH, minimum_rows, SEQUENCE_COLUMNS)
    write_csv(COUNTRY_COVERAGE_PATH, country_rows, COUNTRY_COLUMNS)
    write_csv(SUMMARY_PATH, summary_rows, SUMMARY_COLUMNS)
    write_report(sequence_rows, minimum_rows, country_rows, summary_rows)
    append_log(
        TEMP_DIR / "audit_log.md",
        "Priority LSMS/ISA threshold download sequence "
        f"rows={len(sequence_rows)} minimum_rows={len(minimum_rows)} countries={len(country_rows)}.",
    )
    print(
        "Priority LSMS/ISA threshold download sequence "
        f"rows={len(sequence_rows)} minimum_rows={len(minimum_rows)} countries={len(country_rows)}."
    )


if __name__ == "__main__":
    main()
