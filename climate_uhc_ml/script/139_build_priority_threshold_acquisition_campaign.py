from __future__ import annotations

import csv
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

from common import PROJECT_ROOT, REPORT_DIR, RESULT_DIR, TEMP_DIR, append_log, ensure_dirs, write_csv


WAVE_PLAN_PATH = RESULT_DIR / "priority_promotion_acquisition_wave_plan.csv"
PACKET_INDEX_PATH = TEMP_DIR / "priority_country_wave_promotion_packet_index.csv"
RAW_RECEIPT_PATH = TEMP_DIR / "priority_raw_package_receipt_ledger.csv"
CREDENTIALED_PATH = TEMP_DIR / "priority_credentialed_raw_acquisition_ledger.csv"
CORE_ENDPOINT_PATH = TEMP_DIR / "priority_core_file_endpoint_dataset_matrix.csv"
REGISTRY_PATH = RESULT_DIR / "promoted_country_wave_registry.csv"

CAMPAIGN_PATH = TEMP_DIR / "priority_threshold_acquisition_campaign.csv"
COUNTRY_PATH = TEMP_DIR / "priority_threshold_country_coverage.csv"
SUMMARY_PATH = RESULT_DIR / "priority_threshold_acquisition_campaign_summary.csv"
REPORT_PATH = REPORT_DIR / "priority_threshold_acquisition_campaign.md"

RAW_ROOT = TEMP_DIR / "raw_downloads"

CAMPAIGN_COLUMNS = [
    "acquisition_batch_rank",
    "campaign_phase",
    "threshold_role",
    "country_role",
    "country",
    "wave",
    "idno",
    "batch_role",
    "survey_name",
    "official_url",
    "local_target_folder",
    "public_documentation_status",
    "official_metadata_evidence_status",
    "official_endpoint_matrix_status",
    "core_file_endpoint_matrix_status",
    "credentialed_acquisition_status",
    "raw_receipt_status",
    "receipt_original_file_count",
    "receipt_priority_targets_missing",
    "financial_protection_status",
    "access_forgone_care_status",
    "climate_linkage_status",
    "analysis_ready_status",
    "promoted_registry_status",
    "download_priority_action",
    "post_download_validation_commands",
    "promotion_stop_rule",
    "handoff_readme",
]

COUNTRY_COLUMNS = [
    "country",
    "country_role",
    "planned_country_wave_rows",
    "phase1_10_wave_rows",
    "phase2_backup_rows",
    "promoted_analysis_ready_rows",
    "financial_protection_ready_rows",
    "double_failure_ready_rows",
    "climate_linkage_ready_rows",
    "raw_package_received_rows",
    "raw_package_missing_rows",
    "threshold_contribution",
    "next_action",
]

SUMMARY_COLUMNS = ["metric", "value", "interpretation"]


POST_DOWNLOAD_COMMANDS = [
    "python script/17_audit_raw_downloads.py",
    "python script/128_build_priority_archive_member_preflight.py",
    "python script/130_build_priority_raw_package_receipt_ledger.py",
    "python script/03_inspect_raw_schemas.py",
    "python script/29_build_raw_variable_verification_protocol.py",
    "python script/33_build_harmonization_recipe_gate.py",
    "python script/125_build_priority_climate_linkage_preflight.py",
    "python script/126_build_priority_raw_verification_workbook.py",
    "python script/129_build_priority_manual_verification_decision_gate.py",
    "python script/140_build_priority_first_pass_variable_review_queue.py",
    "python script/141_build_priority_download_execution_packet.py",
    "python script/132_build_priority_analysis_dataset_synthesis_blueprint.py",
    "python script/134_build_priority_country_wave_promotion_packets.py",
    "python script/127_enforce_promoted_data_gate.py",
    "python script/36_build_direct_read_audit_bundle.py",
    "python script/14_validate_workspace.py",
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


def registry_by_id(rows: list[dict[str, str]]) -> dict[str, dict[str, str]]:
    return one_by_id(rows, "idno")


def raw_folder_path(folder: str, idno: str) -> Path:
    folder_clean = clean(folder).replace("\\", "/").strip("/")
    if folder_clean.startswith("temp/raw_downloads/"):
        return PROJECT_ROOT / folder_clean
    if folder_clean:
        return RAW_ROOT / folder_clean
    return RAW_ROOT / idno


def campaign_phase(batch_role: str) -> str:
    if batch_role == "priority_10_wave_batch":
        return "phase_1_double_failure_10_wave_base"
    if batch_role == "sixth_country_backup_candidate":
        return "phase_2_sixth_country_financial_protection_backup"
    return "other_candidate"


def threshold_role(batch_role: str) -> str:
    if batch_role == "priority_10_wave_batch":
        return "required_for_10_country_wave_double_failure_threshold"
    if batch_role == "sixth_country_backup_candidate":
        return "candidate_for_6th_financial_protection_country"
    return "not_in_current_threshold_campaign"


def country_role(batch_role: str) -> str:
    if batch_role == "priority_10_wave_batch":
        return "core_five_country_base"
    if batch_role == "sixth_country_backup_candidate":
        return "sixth_country_backup_option"
    return "other"


def promoted_status(registry: dict[str, str]) -> str:
    if not registry:
        return "not_in_promoted_registry"
    return clean(registry.get("analysis_ready_status")) or "registry_status_missing"


def next_action(receipt_status: str, credentialed_status: str, missing_targets: int) -> str:
    if safe_int(missing_targets) > 0 and "ready_for_credentialed_manual_download" in credentialed_status:
        return "Open official get-microdata URL with an authorized account, complete terms/Data Access Agreement, download the complete unchanged package plus documentation, and place it in the target folder."
    if receipt_status == "partial_raw_package_candidate_missing_priority_targets":
        return "Add the missing priority modules or identify documented renamed files, then rerun archive and receipt gates."
    if receipt_status in {"complete_raw_package_candidate_ready_for_schema_and_manual_audit", "raw_targets_covered_documentation_review_needed"}:
        return "Run post-download validation commands and complete raw value, merge-key, survey-design, timing, geography, outcome, and climate-linkage reviews."
    return "Resolve raw package receipt before any promoted data write."


def write_handoff(row: dict[str, str]) -> str:
    folder = raw_folder_path(row.get("local_target_folder", ""), row.get("idno", ""))
    folder.mkdir(parents=True, exist_ok=True)
    path = folder / "_PRIORITY_THRESHOLD_ACQUISITION_CAMPAIGN.md"
    path.write_text(
        f"""# Priority Threshold Acquisition Campaign

Dataset: {row.get('idno', '')} - {row.get('country', '')} {row.get('wave', '')}

Campaign phase: {row.get('campaign_phase', '')}

Threshold role: {row.get('threshold_role', '')}

Country role: {row.get('country_role', '')}

Official URL: {row.get('official_url', '')}

Target folder: `{row.get('local_target_folder', '')}`

Current raw receipt: {row.get('raw_receipt_status', '')}

Current promoted registry status: {row.get('promoted_registry_status', '')}

Next action: {row.get('download_priority_action', '')}

Post-download validation commands:

{chr(10).join(f'- `{command}`' for command in POST_DOWNLOAD_COMMANDS)}

Promotion stop rule: {row.get('promotion_stop_rule', '')}
""",
        encoding="utf-8",
    )
    return rel(path)


def build_campaign_rows() -> list[dict[str, str]]:
    packet_by_id = one_by_id(read_csv_dicts(PACKET_INDEX_PATH))
    receipt_by_id = one_by_id(read_csv_dicts(RAW_RECEIPT_PATH))
    credentialed_by_id = one_by_id(read_csv_dicts(CREDENTIALED_PATH))
    core_endpoint_by_id = one_by_id(read_csv_dicts(CORE_ENDPOINT_PATH))
    registry = registry_by_id(read_csv_dicts(REGISTRY_PATH))

    rows: list[dict[str, str]] = []
    for wave in read_csv_dicts(WAVE_PLAN_PATH):
        idno = clean(wave.get("idno"))
        batch_role = clean(wave.get("batch_role"))
        packet = packet_by_id.get(idno, {})
        receipt = receipt_by_id.get(idno, {})
        credentialed = credentialed_by_id.get(idno, {})
        core_endpoint = core_endpoint_by_id.get(idno, {})
        reg = registry.get(idno, {})
        receipt_status = clean(receipt.get("receipt_status")) or clean(packet.get("raw_package_status")) or "missing_raw_receipt_status"
        credentialed_status = clean(credentialed.get("credentialed_acquisition_status")) or clean(packet.get("credentialed_acquisition_status"))
        missing_targets = safe_int(receipt.get("priority_targets_missing", packet.get("failed_gate_count", "0")))
        row = {
            "acquisition_batch_rank": wave.get("acquisition_batch_rank", ""),
            "campaign_phase": campaign_phase(batch_role),
            "threshold_role": threshold_role(batch_role),
            "country_role": country_role(batch_role),
            "country": wave.get("country", ""),
            "wave": wave.get("wave", ""),
            "idno": idno,
            "batch_role": batch_role,
            "survey_name": wave.get("survey_name", ""),
            "official_url": wave.get("official_url", ""),
            "local_target_folder": wave.get("local_target_folder", ""),
            "public_documentation_status": clean(packet.get("public_documentation_status")) or "missing_packet_index",
            "official_metadata_evidence_status": clean(packet.get("official_metadata_evidence_status")) or "missing_packet_index",
            "official_endpoint_matrix_status": clean(packet.get("official_endpoint_matrix_status")) or "missing_packet_index",
            "core_file_endpoint_matrix_status": clean(core_endpoint.get("core_file_endpoint_matrix_status")) or "missing_core_file_endpoint_matrix",
            "credentialed_acquisition_status": credentialed_status or "missing_credentialed_acquisition_status",
            "raw_receipt_status": receipt_status,
            "receipt_original_file_count": clean(receipt.get("original_file_count")) or "0",
            "receipt_priority_targets_missing": str(missing_targets),
            "financial_protection_status": clean(packet.get("financial_protection_status")) or clean(reg.get("che10_che25_ready_status")) or "missing",
            "access_forgone_care_status": clean(packet.get("access_forgone_care_status")) or clean(reg.get("access_forgone_care_ready_status")) or "missing",
            "climate_linkage_status": clean(packet.get("climate_linkage_status")) or clean(reg.get("climate_linkage_ready_status")) or "missing",
            "analysis_ready_status": clean(packet.get("analysis_ready_status")) or clean(reg.get("analysis_ready_status")) or "missing",
            "promoted_registry_status": promoted_status(reg),
            "download_priority_action": next_action(receipt_status, credentialed_status, missing_targets),
            "post_download_validation_commands": "; ".join(POST_DOWNLOAD_COMMANDS),
            "promotion_stop_rule": "Do not write this country-wave into data/ until the complete original package, raw value verification, outcome readiness, and CHIRPS/ERA5 linkage gates pass.",
            "handoff_readme": "",
        }
        row["handoff_readme"] = write_handoff(row)
        rows.append(row)
    rows.sort(key=lambda item: safe_int(item.get("acquisition_batch_rank"), 9999))
    return rows


def build_country_rows(campaign_rows: list[dict[str, str]]) -> list[dict[str, str]]:
    rows_by_country: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in campaign_rows:
        rows_by_country[row["country"]].append(row)
    country_rows: list[dict[str, str]] = []
    for country, rows in sorted(rows_by_country.items(), key=lambda item: min(safe_int(row["acquisition_batch_rank"], 9999) for row in item[1])):
        role = "core_five_country_base" if any(row["country_role"] == "core_five_country_base" for row in rows) else "sixth_country_backup_option"
        promoted_ready = sum(1 for row in rows if row["promoted_registry_status"] == "promoted_analysis_ready")
        financial_ready = sum(1 for row in rows if row["financial_protection_status"] in {"ready", "promoted_analysis_ready", "financial_protection_value_ready"})
        double_ready = sum(1 for row in rows if row["access_forgone_care_status"] in {"ready", "promoted_analysis_ready", "double_failure_value_ready"})
        climate_ready = sum(1 for row in rows if row["climate_linkage_status"] in {"ready", "accepted_chirps_era5_climate_linkage", "climate_linkage_ready"})
        raw_received = sum(1 for row in rows if safe_int(row["receipt_original_file_count"]) > 0)
        raw_missing = sum(1 for row in rows if safe_int(row["receipt_original_file_count"]) == 0)
        threshold = (
            "core_5_country_base_for_10_wave_double_failure_threshold"
            if role == "core_five_country_base"
            else "backup_option_for_6th_financial_protection_country"
        )
        next_country_action = (
            "Download all planned core-country waves in this country to preserve multi-wave double-failure coverage."
            if role == "core_five_country_base"
            else "Download at least one backup-country wave; keep all three backups in the campaign to reduce sixth-country failure risk."
        )
        country_rows.append(
            {
                "country": country,
                "country_role": role,
                "planned_country_wave_rows": str(len(rows)),
                "phase1_10_wave_rows": str(sum(1 for row in rows if row["campaign_phase"] == "phase_1_double_failure_10_wave_base")),
                "phase2_backup_rows": str(sum(1 for row in rows if row["campaign_phase"] == "phase_2_sixth_country_financial_protection_backup")),
                "promoted_analysis_ready_rows": str(promoted_ready),
                "financial_protection_ready_rows": str(financial_ready),
                "double_failure_ready_rows": str(double_ready),
                "climate_linkage_ready_rows": str(climate_ready),
                "raw_package_received_rows": str(raw_received),
                "raw_package_missing_rows": str(raw_missing),
                "threshold_contribution": threshold,
                "next_action": next_country_action,
            }
        )
    return country_rows


def build_summary(campaign_rows: list[dict[str, str]], country_rows: list[dict[str, str]]) -> list[dict[str, str]]:
    phase_counts = Counter(row["campaign_phase"] for row in campaign_rows)
    role_counts = Counter(row["country_role"] for row in campaign_rows)
    country_role_counts = Counter(row["country_role"] for row in country_rows)
    promoted_rows = sum(1 for row in campaign_rows if row["promoted_registry_status"] == "promoted_analysis_ready")
    raw_received = sum(1 for row in campaign_rows if safe_int(row["receipt_original_file_count"]) > 0)
    core_endpoint_ready = sum(1 for row in campaign_rows if row["core_file_endpoint_matrix_status"] == "core_file_routes_confirmed_non_public_raw")
    handoffs = sum(1 for row in campaign_rows if row.get("handoff_readme"))
    rows = [
        {"metric": "priority_threshold_campaign_dataset_rows", "value": str(len(campaign_rows)), "interpretation": "Priority and backup country-waves in the threshold acquisition campaign."},
        {"metric": "priority_threshold_campaign_phase1_10_wave_rows", "value": str(phase_counts.get("phase_1_double_failure_10_wave_base", 0)), "interpretation": "Core campaign rows needed for the 10 country-wave double-failure threshold."},
        {"metric": "priority_threshold_campaign_phase2_sixth_country_backup_rows", "value": str(phase_counts.get("phase_2_sixth_country_financial_protection_backup", 0)), "interpretation": "Backup rows kept to reach a sixth financial-protection country."},
        {"metric": "priority_threshold_campaign_distinct_countries", "value": str(len(country_rows)), "interpretation": "Distinct countries represented in the campaign."},
        {"metric": "priority_threshold_campaign_core_country_rows", "value": str(country_role_counts.get("core_five_country_base", 0)), "interpretation": "Core countries represented by the first 10 waves."},
        {"metric": "priority_threshold_campaign_backup_country_rows", "value": str(country_role_counts.get("sixth_country_backup_option", 0)), "interpretation": "Backup countries available as sixth-country candidates."},
        {"metric": "priority_threshold_campaign_core_wave_rows", "value": str(role_counts.get("core_five_country_base", 0)), "interpretation": "Wave rows in the core five-country base."},
        {"metric": "priority_threshold_campaign_backup_wave_rows", "value": str(role_counts.get("sixth_country_backup_option", 0)), "interpretation": "Wave rows in the sixth-country backup set."},
        {"metric": "priority_threshold_campaign_minimum_download_rows_for_formal_thresholds", "value": "11", "interpretation": "Ten phase-1 waves plus at least one backup-country wave are the minimum raw downloads if every selected wave verifies."},
        {"metric": "priority_threshold_campaign_recommended_download_rows", "value": str(len(campaign_rows)), "interpretation": "Recommended downloads include all three backup countries to reduce sixth-country failure risk."},
        {"metric": "priority_threshold_campaign_current_promoted_analysis_ready_rows", "value": str(promoted_rows), "interpretation": "Campaign rows currently promoted analysis-ready."},
        {"metric": "priority_threshold_campaign_raw_package_received_rows", "value": str(raw_received), "interpretation": "Campaign rows with any original raw/package receipt."},
        {"metric": "priority_threshold_campaign_raw_package_missing_rows", "value": str(len(campaign_rows) - raw_received), "interpretation": "Campaign rows still missing original raw/package receipt."},
        {"metric": "priority_threshold_campaign_core_file_endpoint_ready_rows", "value": str(core_endpoint_ready), "interpretation": "Campaign rows with core-file endpoint probes confirming public routes do not expose accepted raw payloads."},
        {"metric": "priority_threshold_campaign_handoff_readmes_written", "value": str(handoffs), "interpretation": "Per-wave threshold acquisition handoffs written."},
        {"metric": "modeling_gate_status", "value": "blocked", "interpretation": "Models remain blocked until 6 countries, 10 country-waves, and accepted CHIRPS/ERA5 linkage are value-verified."},
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


def write_report(campaign_rows: list[dict[str, str]], country_rows: list[dict[str, str]], summary: list[dict[str, str]]) -> None:
    summary_table = "\n".join(f"| {row['metric']} | {row['value']} | {row['interpretation']} |" for row in summary)
    REPORT_PATH.write_text(
        f"""# Priority Threshold Acquisition Campaign

Status: acquisition campaign for the promoted dataset thresholds. This file
maps the current 13 priority/backup waves to the actual modeling guardrails:
10 value-verified country-waves for double failure, 6 value-verified countries
for financial protection, and at least one accepted CHIRPS/ERA5 linkage route.

## Summary

| Metric | Value | Interpretation |
|---|---:|---|
{summary_table}

## Country Coverage

{markdown_table(country_rows, ['country', 'country_role', 'planned_country_wave_rows', 'phase1_10_wave_rows', 'phase2_backup_rows', 'raw_package_received_rows', 'promoted_analysis_ready_rows', 'threshold_contribution'], 20)}

## Campaign Queue

{markdown_table(campaign_rows, ['acquisition_batch_rank', 'campaign_phase', 'country', 'wave', 'idno', 'raw_receipt_status', 'core_file_endpoint_matrix_status', 'promoted_registry_status'], 20)}

## Operational Rule

The first 10 waves are the base campaign for the 10 country-wave double-failure
threshold, but they represent only five countries. At least one backup-country
wave must pass financial-protection value verification to reach the sixth
country threshold. All three backup countries remain in the campaign because
any one backup may fail outcome, geography, timing, or climate-linkage checks
after raw receipt.

## Machine-Readable Outputs

- `temp/priority_threshold_acquisition_campaign.csv`
- `temp/priority_threshold_country_coverage.csv`
- `result/priority_threshold_acquisition_campaign_summary.csv`
""",
        encoding="utf-8",
    )


def main() -> None:
    ensure_dirs()
    campaign_rows = build_campaign_rows()
    country_rows = build_country_rows(campaign_rows)
    summary = build_summary(campaign_rows, country_rows)
    write_csv(CAMPAIGN_PATH, campaign_rows, CAMPAIGN_COLUMNS)
    write_csv(COUNTRY_PATH, country_rows, COUNTRY_COLUMNS)
    write_csv(SUMMARY_PATH, summary, SUMMARY_COLUMNS)
    write_report(campaign_rows, country_rows, summary)
    append_log(
        TEMP_DIR / "audit_log.md",
        f"Built priority threshold acquisition campaign rows={len(campaign_rows)} countries={len(country_rows)}.",
    )
    print(f"Priority threshold acquisition campaign rows={len(campaign_rows)} countries={len(country_rows)}.")


if __name__ == "__main__":
    main()
