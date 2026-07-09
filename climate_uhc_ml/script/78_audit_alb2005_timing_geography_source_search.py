from __future__ import annotations

import csv
import math
from pathlib import Path
from typing import Any

import pandas as pd

from common import REPORT_DIR, RESULT_DIR, TEMP_DIR, append_log, ensure_dirs, write_csv


IDNO = "ALB_2005_LSMS_v01_M"
COUNTRY = "Albania"
SURVEY_NAME = "Living Standards Measurement Survey 2005"
WAVE = "2005"

RAW_ROOT = TEMP_DIR / "raw_extracted" / "lsms2005en_1e7f1965c4a5" / "lsms2005en"
QUESTIONNAIRE_ROOT = RAW_ROOT / "Questionnaire 2005"

RAW_VARIABLE_CATALOG = TEMP_DIR / "raw_schema_inventory" / "raw_variable_catalog.csv"
RAW_FILE_INVENTORY = TEMP_DIR / "raw_schema_inventory" / "raw_file_inventory.csv"
TIMING_GEO_SUMMARY_PATH = RESULT_DIR / "alb2005_timing_geography_exhaustive_summary.csv"
LEGACY_TIMING_SUMMARY_PATH = RESULT_DIR / "albania_legacy_questionnaire_timing_field_summary.csv"
REQUIRED_VALUE_KEY_SUMMARY_PATH = RESULT_DIR / "alb2005_required_value_key_summary.csv"

AUDIT_PATH = TEMP_DIR / "alb2005_timing_geography_source_search_audit.csv"
SUMMARY_PATH = RESULT_DIR / "alb2005_timing_geography_source_search_summary.csv"
REPORT_PATH = REPORT_DIR / "alb2005_timing_geography_source_search_audit.md"

DECISION = "blocked_alb2005_timing_geography_source_search_not_ready"
NO_PROMOTION = "not_promoted_timing_geography_source_search_audit_only"

TARGETS = {
    "household_interview_timing": {
        "raw_phrases": ["interview", "fieldwork", "survey date", "survey month", "visit date", "date of interview"],
        "questionnaire_phrases": ["date", "begin", "end", "visit", "interview", "status"],
        "file_hints": ["filter", "control", "questionnaire"],
    },
    "gps_or_coordinates": {
        "raw_phrases": ["gps", "latitude", "longitude", "coordinate", "x coordinate", "y coordinate"],
        "questionnaire_phrases": ["gps", "latitude", "longitude", "coordinate"],
        "file_hints": ["geo", "gps", "coordinate"],
    },
    "current_admin_geography": {
        "raw_phrases": ["district", "region", "prefecture", "commune", "municipality", "village", "urban", "rural", "area"],
        "questionnaire_phrases": ["district", "region", "prefecture", "commune", "municipality", "urban", "rural"],
        "file_hints": ["filter", "poverty", "weight"],
    },
    "psu_cluster_keys": {
        "raw_phrases": ["psu", "cluster", "sampling point", "primary sampling"],
        "questionnaire_phrases": ["psu", "cluster", "sampling"],
        "file_hints": ["weight", "filter"],
    },
    "fieldwork_control_forms": {
        "raw_phrases": ["interviewer", "supervisor", "visit", "status", "contact", "remarks"],
        "questionnaire_phrases": ["interviewer", "supervisor", "visit", "status", "contact", "remarks", "result"],
        "file_hints": ["filter", "questionnaire"],
    },
}

AUDIT_COLUMNS = [
    "country",
    "survey_name",
    "wave",
    "idno",
    "audit_family",
    "evidence_item",
    "target_concept",
    "source_scope",
    "source_artifact",
    "local_files_scanned",
    "local_variables_scanned",
    "raw_phrase_hit_count",
    "questionnaire_phrase_hit_count",
    "candidate_file_count",
    "upstream_verified_household_timing_rows",
    "upstream_coordinate_candidate_rows",
    "upstream_partial_district_variable_rows",
    "upstream_partial_district_name_nonmissing_rows",
    "upstream_partial_district_code_nonmissing_rows",
    "upstream_climate_linkage_ready_rows",
    "evidence_detail",
    "evidence_status",
    "ready_for_geography_crosswalk",
    "ready_for_interview_timing",
    "ready_for_climate_linkage",
    "promotion_status",
    "blocking_reason",
    "next_action",
]

SUMMARY_COLUMNS = ["metric", "value", "interpretation"]


def read_csv_dicts(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        return []
    with path.open(encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def metric_value(rows: list[dict[str, str]], metric: str, default: str = "0") -> str:
    return next((row.get("value", default) for row in rows if row.get("metric") == metric), default)


def fmt(value: Any) -> str:
    if value is None:
        return ""
    try:
        if pd.isna(value):
            return ""
    except TypeError:
        pass
    if isinstance(value, float):
        if not math.isfinite(value):
            return ""
        if value.is_integer():
            return str(int(value))
        return f"{value:.6g}"
    return str(value)


def safe_int(value: Any, default: int = 0) -> int:
    try:
        return int(float(str(value).strip()))
    except (TypeError, ValueError):
        return default


def clean_text(value: Any) -> str:
    if value is None:
        return ""
    try:
        if pd.isna(value):
            return ""
    except TypeError:
        pass
    return " ".join(str(value).split()).encode("ascii", "replace").decode("ascii")


def compact_join(values: list[Any], limit: int = 8) -> str:
    out: list[str] = []
    seen: set[str] = set()
    for value in values:
        text = clean_text(value)
        if not text or text in seen:
            continue
        out.append(text)
        seen.add(text)
        if len(out) >= limit:
            break
    return "; ".join(out)


def is_alb2005_path(value: str) -> bool:
    return "lsms2005en_1e7f1965c4a5" in value.replace("/", "\\")


def local_raw_variable_rows() -> list[dict[str, str]]:
    return [row for row in read_csv_dicts(RAW_VARIABLE_CATALOG) if is_alb2005_path(row.get("source_path", ""))]


def local_raw_file_rows() -> list[dict[str, str]]:
    return [row for row in read_csv_dicts(RAW_FILE_INVENTORY) if is_alb2005_path(row.get("source_path", ""))]


def row_blob(row: dict[str, str]) -> str:
    return f"{row.get('source_path', '')} {row.get('variable_name', '')} {row.get('variable_label', '')}".lower().replace("_", " ")


def contains_any(text: str, phrases: list[str]) -> bool:
    low = text.lower().replace("_", " ")
    return any(phrase.lower().replace("_", " ") in low for phrase in phrases)


def file_hint_match(row: dict[str, str], hints: list[str]) -> bool:
    return contains_any(Path(row.get("source_path", "")).name, hints)


def scan_questionnaire_workbooks() -> dict[str, list[str]]:
    hits = {target: [] for target in TARGETS}
    for workbook_path in sorted(QUESTIONNAIRE_ROOT.glob("*.xls")):
        try:
            workbook = pd.ExcelFile(workbook_path)
        except Exception:
            continue
        for sheet_name in workbook.sheet_names:
            is_control_like = contains_any(sheet_name, ["control", "panel", "information", "filter", "cover"])
            try:
                df = pd.read_excel(workbook, sheet_name=sheet_name, header=None, dtype=object)
            except Exception:
                continue
            for row_index, row in df.iterrows():
                text = clean_text(" ".join(clean_text(value) for value in row.tolist()))
                if not text:
                    continue
                for target, spec in TARGETS.items():
                    if contains_any(text, spec["questionnaire_phrases"]) and (is_control_like or target != "fieldwork_control_forms"):
                        hits[target].append(f"{workbook_path.name}:{sheet_name}:row{row_index + 1}: {text[:160]}")
    return hits


def base_row(audit_family: str, evidence_item: str, target_concept: str) -> dict[str, str]:
    return {
        "country": COUNTRY,
        "survey_name": SURVEY_NAME,
        "wave": WAVE,
        "idno": IDNO,
        "audit_family": audit_family,
        "evidence_item": evidence_item,
        "target_concept": target_concept,
        "source_scope": "",
        "source_artifact": "",
        "local_files_scanned": "0",
        "local_variables_scanned": "0",
        "raw_phrase_hit_count": "0",
        "questionnaire_phrase_hit_count": "0",
        "candidate_file_count": "0",
        "upstream_verified_household_timing_rows": "0",
        "upstream_coordinate_candidate_rows": "0",
        "upstream_partial_district_variable_rows": "0",
        "upstream_partial_district_name_nonmissing_rows": "0",
        "upstream_partial_district_code_nonmissing_rows": "0",
        "upstream_climate_linkage_ready_rows": "0",
        "evidence_detail": "",
        "evidence_status": "blocked_not_run",
        "ready_for_geography_crosswalk": "0",
        "ready_for_interview_timing": "0",
        "ready_for_climate_linkage": "0",
        "promotion_status": NO_PROMOTION,
        "blocking_reason": (
            "Audit-only timing/geography source search. It does not create climate exposure inputs, "
            "does not verify a household interview date/month, and does not validate any admin/GPS climate crosswalk."
        ),
        "next_action": (
            "Use this search output to target manual fieldwork documentation, questionnaire-control, GPS, or admin-boundary review before climate linkage."
        ),
    }


def build_rows() -> tuple[list[dict[str, str]], dict[str, Any]]:
    raw_variables = local_raw_variable_rows()
    raw_files = local_raw_file_rows()
    questionnaire_hits = scan_questionnaire_workbooks()
    timing_geo_summary = read_csv_dicts(TIMING_GEO_SUMMARY_PATH)
    legacy_timing_summary = read_csv_dicts(LEGACY_TIMING_SUMMARY_PATH)
    required_summary = read_csv_dicts(REQUIRED_VALUE_KEY_SUMMARY_PATH)

    upstream_verified_timing = safe_int(metric_value(timing_geo_summary, "alb2005_interview_timing_verified_rows"))
    upstream_coord = safe_int(metric_value(timing_geo_summary, "alb2005_coordinate_candidate_rows"))
    upstream_partial_geo_vars = safe_int(metric_value(timing_geo_summary, "alb2005_partial_current_district_candidate_rows"))
    upstream_district_name = safe_int(metric_value(timing_geo_summary, "alb2005_partial_district_name_nonmissing_rows"))
    upstream_district_code = safe_int(metric_value(timing_geo_summary, "alb2005_partial_district_code_nonmissing_rows"))
    upstream_climate_ready = safe_int(metric_value(timing_geo_summary, "alb2005_climate_linkage_ready_rows"))
    legacy_questionnaire_timing_rows = safe_int(metric_value(legacy_timing_summary, "albania_legacy_questionnaire_timing_field_rows"))
    required_timing_rows = safe_int(metric_value(required_summary, "alb2005_required_value_key_interview_timing_verified_rows"))
    required_coordinate_rows = safe_int(metric_value(required_summary, "alb2005_required_value_key_coordinate_ready_rows"))

    rows: list[dict[str, str]] = []
    raw_targets_with_hits = 0
    questionnaire_targets_with_hits = 0

    for target, spec in TARGETS.items():
        raw_hits = [row for row in raw_variables if contains_any(row_blob(row), spec["raw_phrases"])]
        q_hits = questionnaire_hits.get(target, [])
        file_hits = [row for row in raw_files if file_hint_match(row, spec["file_hints"])]
        raw_targets_with_hits += int(bool(raw_hits))
        questionnaire_targets_with_hits += int(bool(q_hits))

        row = base_row("raw_schema_source_search", "raw_variable_phrase_search", target)
        row.update(
            {
                "source_scope": "local raw-variable catalog",
                "source_artifact": "temp/raw_schema_inventory/raw_variable_catalog.csv",
                "local_files_scanned": str(len(raw_files)),
                "local_variables_scanned": str(len(raw_variables)),
                "raw_phrase_hit_count": str(len(raw_hits)),
                "questionnaire_phrase_hit_count": str(len(q_hits)),
                "candidate_file_count": str(len(file_hits)),
                "upstream_verified_household_timing_rows": str(upstream_verified_timing),
                "upstream_coordinate_candidate_rows": str(upstream_coord),
                "upstream_partial_district_variable_rows": str(upstream_partial_geo_vars),
                "upstream_partial_district_name_nonmissing_rows": str(upstream_district_name),
                "upstream_partial_district_code_nonmissing_rows": str(upstream_district_code),
                "upstream_climate_linkage_ready_rows": str(upstream_climate_ready),
                "evidence_detail": compact_join(
                    [f"{Path(row.get('source_path', '')).name}:{row.get('variable_name', '')}:{row.get('variable_label', '')}" for row in raw_hits],
                    10,
                )
                or "No local raw-variable phrase hit.",
                "evidence_status": (
                    "raw_schema_hits_seen_but_not_verified_climate_inputs"
                    if raw_hits
                    else "raw_schema_hits_not_found"
                ),
                "blocking_reason": (
                    "Raw schema hits exist, but upstream audits still verify no household interview date/month, no coordinates, and no climate-ready geography."
                    if raw_hits
                    else "No raw schema hit provides this climate-linkage input."
                ),
            }
        )
        rows.append(row)

        row = base_row("questionnaire_source_search", "questionnaire_phrase_search", target)
        row.update(
            {
                "source_scope": "local questionnaire workbooks",
                "source_artifact": "Questionnaire 2005/*.xls",
                "local_files_scanned": str(len(raw_files)),
                "local_variables_scanned": str(len(raw_variables)),
                "raw_phrase_hit_count": str(len(raw_hits)),
                "questionnaire_phrase_hit_count": str(len(q_hits)),
                "candidate_file_count": str(len(file_hits)),
                "upstream_verified_household_timing_rows": str(upstream_verified_timing),
                "upstream_coordinate_candidate_rows": str(upstream_coord),
                "upstream_partial_district_variable_rows": str(upstream_partial_geo_vars),
                "upstream_partial_district_name_nonmissing_rows": str(upstream_district_name),
                "upstream_partial_district_code_nonmissing_rows": str(upstream_district_code),
                "upstream_climate_linkage_ready_rows": str(upstream_climate_ready),
                "evidence_detail": compact_join(q_hits, 10) or "No local questionnaire phrase hit.",
                "evidence_status": (
                    "questionnaire_form_design_seen_raw_value_gap_remains"
                    if q_hits
                    else "questionnaire_phrase_hit_not_found"
                ),
                "blocking_reason": (
                    "Questionnaire/control-form wording is a design lead only; the corresponding raw household timing/geography value is still not verified."
                    if q_hits
                    else "No questionnaire evidence was found for this climate-linkage input."
                ),
            }
        )
        rows.append(row)

    row = base_row("upstream_crosscheck", "timing_geography_fail_closed_status", "upstream_timing_geography_audits")
    row.update(
        {
            "source_scope": "upstream timing/geography summaries",
            "source_artifact": "result/alb2005_timing_geography_exhaustive_summary.csv; result/albania_legacy_questionnaire_timing_field_summary.csv; result/alb2005_required_value_key_summary.csv",
            "local_files_scanned": str(len(raw_files)),
            "local_variables_scanned": str(len(raw_variables)),
            "upstream_verified_household_timing_rows": str(upstream_verified_timing),
            "upstream_coordinate_candidate_rows": str(upstream_coord),
            "upstream_partial_district_variable_rows": str(upstream_partial_geo_vars),
            "upstream_partial_district_name_nonmissing_rows": str(upstream_district_name),
            "upstream_partial_district_code_nonmissing_rows": str(upstream_district_code),
            "upstream_climate_linkage_ready_rows": str(upstream_climate_ready),
            "evidence_detail": (
                f"legacy_questionnaire_timing_rows={legacy_questionnaire_timing_rows}; "
                f"required_value_key_timing_rows={required_timing_rows}; "
                f"required_value_key_coordinate_rows={required_coordinate_rows}; "
                f"decision={metric_value(timing_geo_summary, 'alb2005_timing_geography_current_decision', 'missing')}"
            ),
            "evidence_status": "upstream_timing_geography_remains_fail_closed",
            "blocking_reason": "Upstream audits still verify zero interview-timing rows, zero coordinate rows, and zero climate-linkage-ready rows for ALB_2005.",
            "next_action": "Find official fieldwork date/month documentation and a defensible current-location admin/GPS crosswalk before any climate extraction.",
        }
    )
    rows.append(row)

    diagnostics = {
        "target_concepts": len(TARGETS),
        "local_files_scanned": len(raw_files),
        "local_variables_scanned": len(raw_variables),
        "questionnaire_workbooks_scanned": len(list(QUESTIONNAIRE_ROOT.glob("*.xls"))) if QUESTIONNAIRE_ROOT.exists() else 0,
        "raw_targets_with_hits": raw_targets_with_hits,
        "questionnaire_targets_with_hits": questionnaire_targets_with_hits,
        "legacy_questionnaire_timing_rows": legacy_questionnaire_timing_rows,
        "verified_household_timing_rows": upstream_verified_timing,
        "coordinate_candidate_rows": upstream_coord,
        "partial_district_variable_rows": upstream_partial_geo_vars,
        "partial_district_name_nonmissing_rows": upstream_district_name,
        "partial_district_code_nonmissing_rows": upstream_district_code,
        "required_value_key_timing_rows": required_timing_rows,
        "required_value_key_coordinate_rows": required_coordinate_rows,
        "climate_linkage_ready_rows": upstream_climate_ready,
    }
    return rows, diagnostics


def summary_row(metric: str, value: Any, interpretation: str) -> dict[str, str]:
    return {"metric": metric, "value": fmt(value), "interpretation": interpretation}


def build_summary(rows: list[dict[str, str]], diagnostics: dict[str, Any]) -> list[dict[str, str]]:
    return [
        summary_row("alb2005_timing_geography_source_search_rows", len(rows), "Rows in the ALB_2005 timing/geography source-search audit."),
        summary_row("alb2005_timing_geography_source_search_target_concepts", diagnostics["target_concepts"], "Climate-linkage concepts searched locally."),
        summary_row("alb2005_timing_geography_source_search_local_files_scanned", diagnostics["local_files_scanned"], "Local ALB_2005 raw/schema file rows scanned."),
        summary_row("alb2005_timing_geography_source_search_local_variables_scanned", diagnostics["local_variables_scanned"], "Local ALB_2005 raw-variable rows scanned."),
        summary_row("alb2005_timing_geography_source_search_questionnaire_workbooks_scanned", diagnostics["questionnaire_workbooks_scanned"], "Local ALB_2005 questionnaire workbooks scanned."),
        summary_row("alb2005_timing_geography_source_search_raw_targets_with_hits", diagnostics["raw_targets_with_hits"], "Target concepts with raw-schema phrase hits."),
        summary_row("alb2005_timing_geography_source_search_questionnaire_targets_with_hits", diagnostics["questionnaire_targets_with_hits"], "Target concepts with questionnaire phrase hits."),
        summary_row("alb2005_timing_geography_source_search_legacy_questionnaire_timing_rows", diagnostics["legacy_questionnaire_timing_rows"], "Legacy questionnaire timing/control rows observed upstream."),
        summary_row("alb2005_timing_geography_source_search_verified_household_timing_rows", diagnostics["verified_household_timing_rows"], "Verified ALB_2005 household interview timing rows; should remain zero."),
        summary_row("alb2005_timing_geography_source_search_coordinate_candidate_rows", diagnostics["coordinate_candidate_rows"], "Raw coordinate/GPS candidate rows; should remain zero."),
        summary_row("alb2005_timing_geography_source_search_partial_district_variable_rows", diagnostics["partial_district_variable_rows"], "Partial current district variables observed upstream."),
        summary_row("alb2005_timing_geography_source_search_partial_district_name_nonmissing_rows", diagnostics["partial_district_name_nonmissing_rows"], "Nonmissing partial district-name rows observed upstream."),
        summary_row("alb2005_timing_geography_source_search_partial_district_code_nonmissing_rows", diagnostics["partial_district_code_nonmissing_rows"], "Nonmissing partial district-code rows observed upstream."),
        summary_row("alb2005_timing_geography_source_search_required_value_key_timing_rows", diagnostics["required_value_key_timing_rows"], "Verified interview timing rows observed in required value/key audit; should remain zero."),
        summary_row("alb2005_timing_geography_source_search_required_value_key_coordinate_rows", diagnostics["required_value_key_coordinate_rows"], "Coordinate-ready rows observed in required value/key audit; should remain zero."),
        summary_row("alb2005_timing_geography_source_search_geography_crosswalk_ready_rows", 0, "Rows promoted to geography crosswalk readiness by this audit; intentionally zero."),
        summary_row("alb2005_timing_geography_source_search_interview_timing_ready_rows", 0, "Rows promoted to interview timing readiness by this audit; intentionally zero."),
        summary_row("alb2005_timing_geography_source_search_climate_linkage_ready_rows", diagnostics["climate_linkage_ready_rows"], "Rows promoted to climate linkage after this audit; intentionally zero."),
        summary_row("alb2005_timing_geography_source_search_current_decision", DECISION, "Current fail-closed decision for ALB_2005 timing/geography source-search evidence."),
    ]


def markdown_rows(rows: list[dict[str, str]], columns: list[str], limit: int = 30) -> str:
    lines = ["| " + " | ".join(columns) + " |", "|" + "|".join("---" for _ in columns) + "|"]
    for row in rows[:limit]:
        values = []
        for column in columns:
            value = (row.get(column, "") or "").replace("|", "/")
            if len(value) > 140:
                value = value[:137] + "..."
            values.append(value)
        lines.append("| " + " | ".join(values) + " |")
    return "\n".join(lines)


def write_report(rows: list[dict[str, str]], summary: list[dict[str, str]]) -> None:
    summary_table = "\n".join(f"| {row['metric']} | {row['value']} | {row['interpretation']} |" for row in summary)
    report = f"""# ALB_2005 Timing/Geography Source Search Audit

Status: fail-closed climate-linkage source search. This audit searches local ALB_2005 raw schema, questionnaires, and upstream timing/geography summaries for household interview timing, current-location geography, coordinates, and PSU/cluster evidence. It does not write `data/`, does not construct climate exposures, and does not promote any row to geography crosswalk, interview timing, or climate linkage readiness.

## Bottom Line

- Local raw-schema and questionnaire wording provide leads, but upstream audits still verify zero household interview timing rows and zero coordinate/GPS candidate rows.
- Partial district variables exist in `filters.sav`, but they are not full-coverage verified geography and cannot support climate linkage without a defensible boundary/crosswalk strategy.
- PSU/cluster keys are observed, but no coordinate or admin crosswalk is verified for climate extraction.
- Geography-crosswalk-ready, interview-timing-ready, and climate-linkage-ready rows from this audit: 0.
- Current decision: `{DECISION}`.

## Summary

| Metric | Value | Interpretation |
|---|---:|---|
{summary_table}

## Source Search Rows

{markdown_rows(rows, ['audit_family', 'target_concept', 'raw_phrase_hit_count', 'questionnaire_phrase_hit_count', 'candidate_file_count', 'upstream_verified_household_timing_rows', 'upstream_coordinate_candidate_rows', 'upstream_climate_linkage_ready_rows', 'evidence_status'], 30)}

## Interpretation

- Questionnaire/control-form timing fields are design evidence only; they do not prove that the released raw files contain usable household interview dates or months.
- Partial district name/code rows require coverage, boundary, historical-definition, and current-location validation before admin-level climate aggregation.
- Without household interview timing and climate-ready geography, ALB_2005 cannot enter climate-linked outcome construction or any reduced-form/causal ML stage.

## Machine-Readable Outputs

- `temp/alb2005_timing_geography_source_search_audit.csv`
- `result/alb2005_timing_geography_source_search_summary.csv`
"""
    REPORT_PATH.write_text(report, encoding="utf-8")


def main() -> None:
    ensure_dirs()
    rows, diagnostics = build_rows()
    summary = build_summary(rows, diagnostics)
    write_csv(AUDIT_PATH, rows, AUDIT_COLUMNS)
    write_csv(SUMMARY_PATH, summary, SUMMARY_COLUMNS)
    write_report(rows, summary)
    append_log(TEMP_DIR / "audit_log.md", f"Built ALB_2005 timing/geography source-search audit rows={len(rows)} decision={DECISION}.")
    print(f"ALB_2005 timing/geography source-search rows={len(rows)} decision={DECISION}.")


if __name__ == "__main__":
    main()
