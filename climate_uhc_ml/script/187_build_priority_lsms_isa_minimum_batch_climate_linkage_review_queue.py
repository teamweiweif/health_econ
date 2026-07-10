from __future__ import annotations

import csv
from collections import defaultdict
from typing import Any

from common import REPORT_DIR, RESULT_DIR, TEMP_DIR, append_log, ensure_dirs, write_csv


BOARD_PATH = TEMP_DIR / "priority_lsms_isa_manual_download_execution_board.csv"
COVERAGE_PATH = TEMP_DIR / "priority_lsms_isa_requirement_variable_coverage.csv"
FILE_SHORTLIST_PATH = TEMP_DIR / "priority_lsms_isa_concept_file_shortlist.csv"
TARGET_SMOKE_STATUS_PATH = TEMP_DIR / "priority_lsms_isa_target_folder_receipt_status.csv"

REVIEW_QUEUE_PATH = TEMP_DIR / "priority_lsms_isa_minimum_batch_climate_linkage_review_queue.csv"
FILE_QUEUE_PATH = TEMP_DIR / "priority_lsms_isa_minimum_batch_climate_linkage_file_queue.csv"
SUMMARY_PATH = RESULT_DIR / "priority_lsms_isa_minimum_batch_climate_linkage_review_summary.csv"
REPORT_PATH = REPORT_DIR / "priority_lsms_isa_minimum_batch_climate_linkage_review_queue.md"

REQUIREMENTS = {"survey_timing", "climate_geography"}
POINT_HINTS = ("lat", "latitude", "lon", "long", "longitude", "gps", "coordinate", "geovariable")
ADMIN_HINTS = ("district", "region", "zone", "ward", "ea", "cluster", "village", "admin")

REVIEW_COLUMNS = [
    "download_rank",
    "country",
    "wave",
    "idno",
    "threshold_download_role",
    "official_get_microdata_url",
    "local_target_folder",
    "target_receipt_smoke_status",
    "timing_candidate_variable_rows",
    "timing_strong_candidate_variable_rows",
    "timing_candidate_file_rows",
    "geography_candidate_variable_rows",
    "geography_strong_candidate_variable_rows",
    "geography_candidate_file_rows",
    "top_timing_files",
    "top_geography_files",
    "top_timing_variables",
    "top_geography_variables",
    "planned_geography_route",
    "planned_temporal_route",
    "planned_climate_sources",
    "required_timing_raw_checks",
    "required_geography_raw_checks",
    "source_route_preflight_status",
    "raw_review_status",
    "climate_linkage_gate_status",
    "next_action",
    "data_write_gate_status",
    "modeling_gate_status",
]

FILE_COLUMNS = [
    "download_rank",
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
    "official_metadata_status",
    "raw_value_verification_status",
    "minimum_batch_review_role",
    "local_target_folder",
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


def group_by_id_requirement(rows: list[dict[str, str]]) -> dict[tuple[str, str], list[dict[str, str]]]:
    grouped: dict[tuple[str, str], list[dict[str, str]]] = defaultdict(list)
    for row in rows:
        idno = clean(row.get("idno"))
        requirement = clean(row.get("requirement"))
        if idno and requirement in REQUIREMENTS:
            grouped[(idno, requirement)].append(row)
    return grouped


def one_by_id(rows: list[dict[str, str]], field: str = "idno") -> dict[str, dict[str, str]]:
    out: dict[str, dict[str, str]] = {}
    for row in rows:
        idno = clean(row.get(field))
        if idno and idno not in out:
            out[idno] = row
    return out


def unique_join(values: list[str], limit: int = 12) -> str:
    seen: list[str] = []
    for value in values:
        for piece in clean(value).split(";"):
            text = clean(piece)
            if text and text not in seen:
                seen.append(text)
    if len(seen) > limit:
        return ";".join(seen[:limit] + [f"...{len(seen) - limit} more"])
    return ";".join(seen)


def coverage_row(rows: list[dict[str, str]]) -> dict[str, str]:
    return rows[0] if rows else {}


def file_rows_for(rows: list[dict[str, str]]) -> list[dict[str, str]]:
    return sorted(rows, key=lambda row: safe_int(row.get("file_rank"), 9999))


def route_from_geography(top_variables: str, top_files: str) -> str:
    text = f"{top_variables};{top_files}".lower()
    if any(hint in text for hint in POINT_HINTS):
        return "point_or_cluster_coordinate_route_raw_unverified"
    if any(hint in text for hint in ADMIN_HINTS):
        return "admin_or_ea_geography_route_raw_unverified"
    return "geography_route_raw_unverified_manual_review"


def route_from_timing(top_variables: str, top_files: str) -> str:
    text = f"{top_variables};{top_files}".lower()
    if "date" in text or "timestamp" in text:
        return "interview_date_route_raw_unverified"
    if "month" in text or "_m" in text or "year" in text or "_y" in text:
        return "interview_month_year_route_raw_unverified"
    return "fieldwork_period_route_raw_unverified_manual_review"


def timing_checks(route: str) -> str:
    if route == "interview_date_route_raw_unverified":
        return "verify interview date parseability; derive survey month/year; check date missing codes; check module level and household key"
    if route == "interview_month_year_route_raw_unverified":
        return "verify interview month/year variables; check month range; check year range; check household key and wave linkage"
    return "verify questionnaire fieldwork period; document whether month-level lag windows are defensible"


def geography_checks(route: str) -> str:
    if route == "point_or_cluster_coordinate_route_raw_unverified":
        return "verify latitude/longitude numeric units; CRS/datum; coordinate level; displacement or masking; missing codes; household/cluster key"
    if route == "admin_or_ea_geography_route_raw_unverified":
        return "verify admin or EA codes/names; boundary vintage; crosswalk source; centroid/area aggregation method; missing codes"
    return "identify raw geography fields, level, boundary source, and whether climate linkage is defensible"


def build_outputs() -> tuple[list[dict[str, str]], list[dict[str, str]], list[dict[str, str]]]:
    board_rows = read_csv_dicts(BOARD_PATH)
    coverage = group_by_id_requirement(read_csv_dicts(COVERAGE_PATH))
    shortlist = group_by_id_requirement(read_csv_dicts(FILE_SHORTLIST_PATH))
    smoke_by_id = one_by_id(read_csv_dicts(TARGET_SMOKE_STATUS_PATH))

    review_rows: list[dict[str, str]] = []
    file_queue_rows: list[dict[str, str]] = []

    for board in board_rows:
        idno = clean(board.get("idno"))
        timing_cov = coverage_row(coverage.get((idno, "survey_timing"), []))
        geo_cov = coverage_row(coverage.get((idno, "climate_geography"), []))
        timing_files = file_rows_for(shortlist.get((idno, "survey_timing"), []))
        geo_files = file_rows_for(shortlist.get((idno, "climate_geography"), []))
        top_timing_variables = unique_join([row.get("top_variable_names", "") for row in timing_files])
        top_geography_variables = unique_join([row.get("top_variable_names", "") for row in geo_files])
        top_timing_files = unique_join([row.get("file_name", "") for row in timing_files])
        top_geography_files = unique_join([row.get("file_name", "") for row in geo_files])
        geography_route = route_from_geography(top_geography_variables, top_geography_files)
        temporal_route = route_from_timing(top_timing_variables, top_timing_files)
        smoke_status = clean(smoke_by_id.get(idno, {}).get("receipt_smoke_status")) or "target_not_in_smoke_test"

        for requirement, rows_for_requirement in [("survey_timing", timing_files), ("climate_geography", geo_files)]:
            for row in rows_for_requirement:
                file_queue_rows.append(
                    {
                        "download_rank": clean(board.get("download_rank")),
                        "country": clean(board.get("country")),
                        "wave": clean(board.get("wave")),
                        "idno": idno,
                        "requirement": requirement,
                        "file_rank": clean(row.get("file_rank")),
                        "file_name": clean(row.get("file_name")),
                        "file_description": clean(row.get("file_description")),
                        "candidate_variable_rows": clean(row.get("candidate_variable_rows")),
                        "strong_candidate_variable_rows": clean(row.get("strong_candidate_variable_rows")),
                        "top_variable_names": clean(row.get("top_variable_names")),
                        "official_metadata_status": clean(row.get("official_metadata_status")),
                        "raw_value_verification_status": clean(row.get("raw_value_verification_status")),
                        "minimum_batch_review_role": "timing_geography_raw_review_required",
                        "local_target_folder": clean(board.get("local_target_folder")),
                        "data_write_gate_status": "blocked_no_data_write",
                        "modeling_gate_status": "blocked",
                    }
                )

        review_rows.append(
            {
                "download_rank": clean(board.get("download_rank")),
                "country": clean(board.get("country")),
                "wave": clean(board.get("wave")),
                "idno": idno,
                "threshold_download_role": clean(board.get("threshold_download_role")),
                "official_get_microdata_url": clean(board.get("official_get_microdata_url")),
                "local_target_folder": clean(board.get("local_target_folder")),
                "target_receipt_smoke_status": smoke_status,
                "timing_candidate_variable_rows": clean(timing_cov.get("candidate_variable_rows")),
                "timing_strong_candidate_variable_rows": clean(timing_cov.get("strong_candidate_variable_rows")),
                "timing_candidate_file_rows": str(len(timing_files)),
                "geography_candidate_variable_rows": clean(geo_cov.get("candidate_variable_rows")),
                "geography_strong_candidate_variable_rows": clean(geo_cov.get("strong_candidate_variable_rows")),
                "geography_candidate_file_rows": str(len(geo_files)),
                "top_timing_files": top_timing_files,
                "top_geography_files": top_geography_files,
                "top_timing_variables": top_timing_variables,
                "top_geography_variables": top_geography_variables,
                "planned_geography_route": geography_route,
                "planned_temporal_route": temporal_route,
                "planned_climate_sources": "CHIRPS rainfall primary; ERA5-Land temperature primary; NASA POWER point fallback; source route not accepted until raw timing/geography pass",
                "required_timing_raw_checks": timing_checks(temporal_route),
                "required_geography_raw_checks": geography_checks(geography_route),
                "source_route_preflight_status": "climate_sources_ready_raw_timing_geography_blocked",
                "raw_review_status": "blocked_no_candidate_raw_files" if smoke_status.startswith("blocked_no_candidate_raw") else "raw_arrival_review_required",
                "climate_linkage_gate_status": "blocked_raw_timing_geography_not_verified",
                "next_action": "Place the complete official raw package, rerun receipt/schema/value audits, then verify timing and geography fields before any CHIRPS/ERA5 extraction.",
                "data_write_gate_status": "blocked_no_data_write",
                "modeling_gate_status": "blocked",
            }
        )

    point_rows = [row for row in review_rows if row.get("planned_geography_route") == "point_or_cluster_coordinate_route_raw_unverified"]
    admin_rows = [row for row in review_rows if row.get("planned_geography_route") == "admin_or_ea_geography_route_raw_unverified"]
    manual_rows = [row for row in review_rows if row.get("planned_geography_route") == "geography_route_raw_unverified_manual_review"]
    summary_rows = [
        {"metric": "priority_lsms_minimum_climate_review_dataset_rows", "value": str(len(review_rows)), "interpretation": "Current manual-download minimum-batch rows covered by the climate linkage review queue."},
        {"metric": "priority_lsms_minimum_climate_review_file_rows", "value": str(len(file_queue_rows)), "interpretation": "Timing/geography candidate file rows to inspect after raw receipt."},
        {"metric": "priority_lsms_minimum_climate_review_timing_ready_metadata_rows", "value": str(sum(1 for row in review_rows if safe_int(row.get("timing_strong_candidate_variable_rows")) > 0)), "interpretation": "Rows with strong official metadata timing candidates."},
        {"metric": "priority_lsms_minimum_climate_review_geography_ready_metadata_rows", "value": str(sum(1 for row in review_rows if safe_int(row.get("geography_strong_candidate_variable_rows")) > 0)), "interpretation": "Rows with strong official metadata geography candidates."},
        {"metric": "priority_lsms_minimum_climate_review_point_route_rows", "value": str(len(point_rows)), "interpretation": "Rows whose metadata suggest coordinate or cluster-point linkage after raw verification."},
        {"metric": "priority_lsms_minimum_climate_review_admin_route_rows", "value": str(len(admin_rows)), "interpretation": "Rows whose metadata suggest admin/EA aggregation after raw verification."},
        {"metric": "priority_lsms_minimum_climate_review_manual_route_rows", "value": str(len(manual_rows)), "interpretation": "Rows needing manual route choice after raw review."},
        {"metric": "priority_lsms_minimum_climate_review_raw_blocked_rows", "value": str(sum(1 for row in review_rows if row.get("raw_review_status") == "blocked_no_candidate_raw_files")), "interpretation": "Rows still blocked because target folders contain no candidate raw files."},
        {"metric": "priority_lsms_minimum_climate_review_source_ready_rows", "value": str(len(review_rows)), "interpretation": "Rows with CHIRPS/ERA5/NASA source plan ready but not accepted."},
        {"metric": "priority_lsms_minimum_climate_review_accepted_route_rows", "value": "0", "interpretation": "Rows with accepted climate linkage routes after raw timing/geography verification."},
        {"metric": "priority_lsms_minimum_climate_review_data_write_status", "value": "blocked_no_data_write", "interpretation": "Climate linkage review does not write promoted data."},
        {"metric": "modeling_gate_status", "value": "blocked", "interpretation": "No predictive, reduced-form, causal ML, or policy learning until registry thresholds pass."},
    ]
    return review_rows, file_queue_rows, summary_rows


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


def write_report(review_rows: list[dict[str, str]], file_rows: list[dict[str, str]], summary_rows: list[dict[str, str]]) -> None:
    REPORT_PATH.write_text(
        f"""# Priority LSMS/ISA Minimum-Batch Climate Linkage Review Queue

Status: raw-blocked climate linkage review queue for the current 10 manual-download packets.

This queue aligns the current minimum-batch download board with official
metadata timing and geography candidates. It does not extract climate data,
accept a CHIRPS/ERA5 route, write `data/`, or run models. It tells the raw
review step which timing and geography files/variables must be verified once
the official packages are placed locally.

## Summary

{markdown_table(summary_rows, ['metric', 'value', 'interpretation'], 30)}

## Country-Wave Queue

{markdown_table(review_rows, ['download_rank', 'idno', 'target_receipt_smoke_status', 'planned_temporal_route', 'planned_geography_route', 'timing_strong_candidate_variable_rows', 'geography_strong_candidate_variable_rows', 'climate_linkage_gate_status'], 20)}

## File Review Queue

{markdown_table(file_rows, ['idno', 'requirement', 'file_rank', 'file_name', 'strong_candidate_variable_rows', 'top_variable_names'], 60)}

## Stop Rule

Every row remains climate-linkage blocked until the complete official raw
package is present, receipt validation passes, timing/geography variables are
value-checked, and the chosen CHIRPS or ERA5 extraction route is validated.
""",
        encoding="utf-8",
    )


def main() -> None:
    ensure_dirs()
    review_rows, file_rows, summary_rows = build_outputs()
    write_csv(REVIEW_QUEUE_PATH, review_rows, REVIEW_COLUMNS)
    write_csv(FILE_QUEUE_PATH, file_rows, FILE_COLUMNS)
    write_csv(SUMMARY_PATH, summary_rows, SUMMARY_COLUMNS)
    write_report(review_rows, file_rows, summary_rows)
    append_log(
        TEMP_DIR / "audit_log.md",
        f"Built priority LSMS/ISA minimum-batch climate linkage review queue rows={len(review_rows)} file_rows={len(file_rows)}.",
    )
    print(f"Priority LSMS/ISA minimum-batch climate linkage review queue rows={len(review_rows)} file_rows={len(file_rows)}.")


if __name__ == "__main__":
    main()
