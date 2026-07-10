from __future__ import annotations

import csv
from pathlib import Path
from typing import Any

from common import REPORT_DIR, RESULT_DIR, TEMP_DIR, append_log, ensure_dirs, write_csv


BOARD_PATH = RESULT_DIR / "priority_lsms_isa_minimum_batch_promotion_unlock_board.csv"
SUMMARY_PATH = RESULT_DIR / "priority_lsms_isa_minimum_batch_promotion_unlock_summary.csv"
REPORT_PATH = REPORT_DIR / "priority_lsms_isa_minimum_batch_promotion_unlock_board.md"

PACKET_INDEX_PATH = TEMP_DIR / "priority_lsms_isa_manual_download_packet_index.csv"
PROGRESS_PATH = TEMP_DIR / "priority_lsms_isa_manual_download_progress_tracker.csv"
TARGET_SMOKE_PATH = TEMP_DIR / "priority_lsms_isa_target_folder_receipt_status.csv"
PUBLIC_DOCS_PATH = TEMP_DIR / "priority_lsms_isa_public_documentation_dataset_receipt.csv"
PROMOTED_REGISTRY_PATH = RESULT_DIR / "promoted_country_wave_registry.csv"
DOWNLOAD_ACCEPTANCE_SUMMARY_PATH = RESULT_DIR / "priority_lsms_isa_download_acceptance_matrix_summary.csv"
ROUTE_PROBE_SUMMARY_PATH = RESULT_DIR / "priority_lsms_isa_resource_download_route_probe_summary.csv"

BOARD_COLUMNS = [
    "download_rank",
    "country",
    "wave",
    "idno",
    "unlock_status",
    "threshold_role",
    "official_get_microdata_url",
    "local_target_folder",
    "public_documentation_receipt_status",
    "access_gate_detected",
    "target_file_count",
    "target_total_bytes",
    "candidate_raw_file_rows",
    "candidate_documentation_file_rows",
    "expected_full_file_rows",
    "expected_core_file_rows",
    "expected_file_name_matches",
    "expected_core_file_name_matches",
    "requirements_covered",
    "registry_analysis_ready_status",
    "registry_outcome_ready_status",
    "registry_che10_che25_ready_status",
    "registry_access_ready_status",
    "registry_climate_linkage_ready_status",
    "registry_raw_package_status",
    "immediate_next_action",
    "post_download_validation_commands",
    "promotion_stop_rule",
]
SUMMARY_COLUMNS = ["metric", "value", "interpretation"]


def clean(value: Any) -> str:
    if value is None:
        return ""
    return " ".join(str(value).split())


def safe_int(value: Any, default: int = 0) -> int:
    try:
        return int(float(clean(value)))
    except (TypeError, ValueError):
        return default


def read_csv_dicts(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        return []
    with path.open(encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def key(row: dict[str, str]) -> str:
    return clean(row.get("idno"))


def index_by_idno(rows: list[dict[str, str]]) -> dict[str, dict[str, str]]:
    return {key(row): row for row in rows if key(row)}


def summary_value(rows: list[dict[str, str]], metric: str, default: str = "") -> str:
    for row in rows:
        if clean(row.get("metric")) == metric:
            return clean(row.get("value")) or default
    return default


def build_board() -> tuple[list[dict[str, str]], list[dict[str, str]]]:
    packets = read_csv_dicts(PACKET_INDEX_PATH)
    progress = index_by_idno(read_csv_dicts(PROGRESS_PATH))
    target_smoke = index_by_idno(read_csv_dicts(TARGET_SMOKE_PATH))
    public_docs = index_by_idno(read_csv_dicts(PUBLIC_DOCS_PATH))
    registry = index_by_idno(read_csv_dicts(PROMOTED_REGISTRY_PATH))
    download_acceptance = read_csv_dicts(DOWNLOAD_ACCEPTANCE_SUMMARY_PATH)
    route_probe = read_csv_dicts(ROUTE_PROBE_SUMMARY_PATH)

    board: list[dict[str, str]] = []
    for packet in sorted(packets, key=lambda row: safe_int(row.get("download_rank"), 9999)):
        idno = key(packet)
        progress_row = progress.get(idno, {})
        smoke_row = target_smoke.get(idno, {})
        docs_row = public_docs.get(idno, {})
        registry_row = registry.get(idno, {})
        target_file_count = safe_int(progress_row.get("target_file_count"))
        target_total_bytes = safe_int(progress_row.get("target_total_bytes"))
        candidate_raw = safe_int(smoke_row.get("candidate_raw_file_rows"))
        candidate_docs = safe_int(smoke_row.get("candidate_documentation_file_rows"))
        core_matches = safe_int(smoke_row.get("expected_core_file_name_matches"))
        expected_core = safe_int(packet.get("core_file_rows") or smoke_row.get("expected_core_file_rows"))
        public_docs_status = clean(docs_row.get("public_documentation_receipt_status"))
        analysis_status = clean(registry_row.get("analysis_ready_status"))

        if analysis_status == "promoted_analysis_ready":
            unlock_status = "already_promoted"
        elif target_file_count == 0 and candidate_raw == 0 and candidate_docs == 0:
            unlock_status = "blocked_no_local_or_incoming_files"
        elif candidate_raw == 0:
            unlock_status = "blocked_no_candidate_raw_files"
        elif core_matches < expected_core:
            unlock_status = "blocked_missing_expected_core_files"
        else:
            unlock_status = "ready_for_receipt_validation"

        board.append(
            {
                "download_rank": clean(packet.get("download_rank")),
                "country": clean(packet.get("country")),
                "wave": clean(packet.get("wave")),
                "idno": idno,
                "unlock_status": unlock_status,
                "threshold_role": clean(packet.get("threshold_download_role")),
                "official_get_microdata_url": clean(packet.get("official_get_microdata_url")),
                "local_target_folder": clean(packet.get("local_target_folder")),
                "public_documentation_receipt_status": public_docs_status,
                "access_gate_detected": clean(docs_row.get("access_gate_detected")),
                "target_file_count": str(target_file_count),
                "target_total_bytes": str(target_total_bytes),
                "candidate_raw_file_rows": str(candidate_raw),
                "candidate_documentation_file_rows": str(candidate_docs),
                "expected_full_file_rows": clean(packet.get("expected_full_file_rows") or smoke_row.get("expected_full_file_rows")),
                "expected_core_file_rows": str(expected_core),
                "expected_file_name_matches": clean(smoke_row.get("expected_file_name_matches")),
                "expected_core_file_name_matches": str(core_matches),
                "requirements_covered": clean(packet.get("requirements_covered")),
                "registry_analysis_ready_status": analysis_status,
                "registry_outcome_ready_status": clean(registry_row.get("outcome_ready_status")),
                "registry_che10_che25_ready_status": clean(registry_row.get("che10_che25_ready_status")),
                "registry_access_ready_status": clean(registry_row.get("access_forgone_care_ready_status")),
                "registry_climate_linkage_ready_status": clean(registry_row.get("climate_linkage_ready_status")),
                "registry_raw_package_status": clean(registry_row.get("raw_package_status")),
                "immediate_next_action": clean(progress_row.get("next_action") or packet.get("download_action")),
                "post_download_validation_commands": clean(packet.get("post_download_validation_commands")),
                "promotion_stop_rule": clean(packet.get("promotion_stop_rule")),
            }
        )

    registry_rows = read_csv_dicts(PROMOTED_REGISTRY_PATH)
    current_promoted = [row for row in registry_rows if clean(row.get("analysis_ready_status")) == "promoted_analysis_ready"]
    current_promoted_countries = sorted({clean(row.get("country")) for row in current_promoted if clean(row.get("country"))})
    batch_countries = sorted({clean(row.get("country")) for row in board if clean(row.get("country"))})
    projected_countries = sorted(set(current_promoted_countries).union(batch_countries))
    validation_ready = sum(1 for row in board if row["unlock_status"] == "ready_for_receipt_validation")
    blocked_no_files = sum(1 for row in board if row["unlock_status"] == "blocked_no_local_or_incoming_files")
    docs_complete = sum(1 for row in board if row["public_documentation_receipt_status"] == "complete_core_public_documentation_receipt")
    total_target_files = sum(safe_int(row["target_file_count"]) for row in board)
    total_target_bytes = sum(safe_int(row["target_total_bytes"]) for row in board)
    raw_payload_candidates = summary_value(route_probe, "resource_download_route_probe_raw_payload_candidate_rows", "0")
    route_access_gate_rows = summary_value(route_probe, "resource_download_route_probe_access_gate_rows", "0")
    missing_expected = summary_value(download_acceptance, "download_acceptance_missing_expected_file_rows", "0")
    missing_requirements = summary_value(download_acceptance, "download_acceptance_missing_core_requirement_rows", "0")

    summary = [
        {"metric": "minimum_batch_unlock_board_rows", "value": str(len(board)), "interpretation": "Manual-download country-waves in the current minimum batch."},
        {"metric": "minimum_batch_unlock_public_documentation_complete_rows", "value": str(docs_complete), "interpretation": "Rows with complete public catalog/DDI/variables/get-microdata documentation receipt."},
        {"metric": "minimum_batch_unlock_validation_ready_rows", "value": str(validation_ready), "interpretation": "Rows with enough local files to begin receipt validation."},
        {"metric": "minimum_batch_unlock_blocked_no_local_or_incoming_files", "value": str(blocked_no_files), "interpretation": "Rows still lacking placed official raw package files or incoming route matches."},
        {"metric": "minimum_batch_unlock_target_file_rows", "value": str(total_target_files), "interpretation": "Non-generated files currently found in target folders by the manual progress tracker."},
        {"metric": "minimum_batch_unlock_target_total_bytes", "value": str(total_target_bytes), "interpretation": "Total bytes currently found in target folders by the manual progress tracker."},
        {"metric": "minimum_batch_unlock_missing_expected_file_rows", "value": missing_expected, "interpretation": "Expected official files still absent according to the download acceptance matrix."},
        {"metric": "minimum_batch_unlock_missing_core_requirement_rows", "value": missing_requirements, "interpretation": "Requirement-level core file checks still blocked by missing official files."},
        {"metric": "minimum_batch_unlock_public_route_raw_payload_candidate_rows", "value": raw_payload_candidates, "interpretation": "Raw payload candidates found by public route probing."},
        {"metric": "minimum_batch_unlock_public_route_access_gate_rows", "value": route_access_gate_rows, "interpretation": "Route probes that hit login, registration, terms, or data-dictionary gates."},
        {"metric": "current_promoted_analysis_ready_rows", "value": str(len(current_promoted)), "interpretation": "Country-waves already promoted in the registry."},
        {"metric": "projected_country_wave_rows_if_all_minimum_batch_promoted", "value": str(len(current_promoted) + len(board)), "interpretation": "Promoted country-wave count if every minimum-batch package passes all gates."},
        {"metric": "projected_country_rows_if_all_minimum_batch_promoted", "value": str(len(projected_countries)), "interpretation": "Country count if the promoted row plus every minimum-batch package passes all gates."},
        {"metric": "minimum_batch_unlock_needed_for_modeling_threshold", "value": str(len(board)), "interpretation": "All current minimum-batch packages are still needed to reach both 6-country and 10-wave thresholds."},
        {"metric": "data_write_gate_status", "value": "blocked_no_data_write", "interpretation": "This board writes only result/report artifacts and does not promote datasets."},
        {"metric": "modeling_gate_status", "value": "blocked", "interpretation": "No predictive, reduced-form, causal ML, or policy learning is opened."},
    ]
    return board, summary


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


def write_report(board: list[dict[str, str]], summary: list[dict[str, str]]) -> None:
    REPORT_PATH.write_text(
        f"""# Priority LSMS/ISA Minimum-Batch Promotion Unlock Board

This report condenses the current 10-package manual-download batch into one
promotion-unlock row per country-wave. It does not download, copy, or promote
raw data. It only joins existing packet, public-documentation, target-folder,
download-acceptance, route-probe, and registry evidence.

The board is intentionally fail-closed: a row becomes ready only after local
official raw package files are present and expected core files match. Until
then, `data/` writes and all modeling remain blocked.

## Summary

{markdown_table(summary, ['metric', 'value', 'interpretation'], 25)}

## Unlock Board

{markdown_table(board, ['download_rank', 'country', 'wave', 'idno', 'unlock_status', 'public_documentation_receipt_status', 'target_file_count', 'expected_core_file_rows', 'expected_core_file_name_matches'], 12)}

## Use

For each blocked row, open the official get-microdata URL, download the complete
unchanged official raw package and documentation, place all files under the
listed local target folder, then run the post-download validation commands in
`result/priority_lsms_isa_minimum_batch_promotion_unlock_board.csv`.
""",
        encoding="utf-8",
    )


def main() -> None:
    ensure_dirs()
    board, summary = build_board()
    write_csv(BOARD_PATH, board, BOARD_COLUMNS)
    write_csv(SUMMARY_PATH, summary, SUMMARY_COLUMNS)
    write_report(board, summary)
    append_log(TEMP_DIR / "audit_log.md", f"Built priority LSMS/ISA minimum-batch promotion unlock board rows={len(board)}.")
    print(f"Priority LSMS/ISA minimum-batch promotion unlock board rows={len(board)}.")


if __name__ == "__main__":
    main()
