from __future__ import annotations

import csv
import math
import re
from pathlib import Path
from typing import Any

import pandas as pd

from common import REPORT_DIR, RESULT_DIR, TEMP_DIR, append_log, ensure_dirs, write_csv


RAW_EXTRACTED_GLOB = "lsms2002en_*/lsms2002en"
RAW_VARIABLE_CATALOG = TEMP_DIR / "raw_schema_inventory" / "raw_variable_catalog.csv"
SOURCE_ALTERNATIVE_SUMMARY = RESULT_DIR / "alb2002_boundary_source_alternative_summary.csv"
AUDIT_PATH = TEMP_DIR / "alb2002_local_geography_artifact_audit.csv"
SUMMARY_PATH = RESULT_DIR / "alb2002_local_geography_artifact_summary.csv"
REPORT_PATH = REPORT_DIR / "alb2002_local_geography_artifact_audit.md"

DECISION = "blocked_questionnaire_gps_fields_not_present_as_raw_coordinate_artifacts"

AUDIT_COLUMNS = [
    "evidence_id",
    "evidence_type",
    "source_path",
    "file_name",
    "sheet_name",
    "row_number",
    "column_number",
    "variable_name",
    "variable_label",
    "evidence_role",
    "evidence_signal",
    "local_value_status",
    "promotion_status",
    "blocking_reason",
    "next_review_action",
]
SUMMARY_COLUMNS = ["metric", "value", "interpretation"]

RAW_TABULAR_SUFFIXES = {".sav", ".dta", ".por", ".sas7bdat", ".xpt", ".csv", ".xlsx", ".xls"}
GIS_SUFFIXES = {".shp", ".shx", ".dbf", ".prj", ".geojson", ".json", ".kml", ".kmz", ".gpx", ".gpkg"}
COORD_RE = re.compile(r"\b(gps|latitude|longitude|lat|lon|coordinate|coordinates|easting|northing|utm)\b", re.I)
ADMIN_RE = re.compile(r"\b(district|commune|municipality|prefecture|qark|rreth|urban|rural|stratum|psu|cluster|enumerator area|enumeration area)\b", re.I)
PSU_EA_RE = re.compile(r"\b(psu|cluster|enumerator area|enumeration area)\b", re.I)
DISTRICT_COMMUNE_RE = re.compile(r"\b(district|commune|municipality|prefecture|qark|rreth)\b", re.I)
MAP_RE = re.compile(r"\b(map|boundary|boundaries|shape|shapefile|polygon|centroid|gis|geograph)\b", re.I)


def fmt(value: Any) -> str:
    if value is None:
        return ""
    try:
        if math.isnan(value):
            return ""
    except TypeError:
        pass
    if isinstance(value, float):
        if value.is_integer():
            return str(int(value))
        return f"{value:.6g}"
    return str(value)


def rel(path: Path) -> str:
    try:
        return str(path.relative_to(TEMP_DIR.parent)).replace("\\", "/")
    except ValueError:
        return str(path).replace("\\", "/")


def read_csv_dicts(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        return []
    with path.open(encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def metric_value(rows: list[dict[str, str]], metric: str, default: str = "0") -> str:
    for row in rows:
        if row.get("metric") == metric:
            return row.get("value", default)
    return default


def source_root() -> Path:
    candidates = sorted((TEMP_DIR / "raw_extracted").glob(RAW_EXTRACTED_GLOB))
    if not candidates:
        raise FileNotFoundError("Missing ALB_2002 extracted root under temp/raw_extracted/lsms2002en_*/lsms2002en")
    return candidates[0]


def classify_file(path: Path) -> tuple[str, str, str, str]:
    name_text = f"{path.name} {path.parent.name}"
    suffix = path.suffix.lower()
    if suffix in GIS_SUFFIXES or COORD_RE.search(name_text) or MAP_RE.search(name_text):
        return (
            "local_file_candidate",
            "potential_geography_or_boundary_file",
            "file_exists_not_validated_as_coordinate_or_boundary_input",
            "File name or suffix suggests possible geography evidence; content and join keys are not verified.",
        )
    if suffix in RAW_TABULAR_SUFFIXES:
        return (
            "local_file_inventory",
            "raw_or_documentation_file",
            "file_exists",
            "File exists in the ALB_2002 extracted package; not itself a verified geography input.",
        )
    return (
        "local_file_inventory",
        "other_file",
        "file_exists",
        "File exists in the ALB_2002 extracted package; not a recognized tabular/GIS geography artifact.",
    )


def file_rows(root: Path) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    for index, path in enumerate(sorted(root.rglob("*"))):
        if not path.is_file():
            continue
        evidence_type, role, value_status, reason = classify_file(path)
        rows.append(
            {
                "evidence_id": f"file_{index:04d}",
                "evidence_type": evidence_type,
                "source_path": rel(path),
                "file_name": path.name,
                "sheet_name": "",
                "row_number": "",
                "column_number": "",
                "variable_name": "",
                "variable_label": "",
                "evidence_role": role,
                "evidence_signal": path.suffix.lower() or "no_suffix",
                "local_value_status": value_status,
                "promotion_status": "blocked_not_ready_for_climate_linkage",
                "blocking_reason": reason,
                "next_review_action": "Confirm whether the file contains household/cluster coordinates, historical polygons, or joinable EA/district boundary keys before any climate linkage.",
            }
        )
    return rows


def classify_variable(variable: str, label: str) -> tuple[str, str] | None:
    text = f"{variable} {label}"
    if COORD_RE.search(text):
        return "raw_coordinate_variable_candidate", "coordinate_keyword_in_raw_schema"
    if PSU_EA_RE.search(text):
        return "raw_psu_or_ea_variable", "psu_or_enumerator_area_keyword_in_raw_schema"
    if DISTRICT_COMMUNE_RE.search(text):
        return "raw_district_or_commune_variable", "district_or_commune_keyword_in_raw_schema"
    if ADMIN_RE.search(text):
        return "raw_admin_geography_variable", "admin_geography_keyword_in_raw_schema"
    return None


def variable_rows() -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    raw_rows = [
        row
        for row in read_csv_dicts(RAW_VARIABLE_CATALOG)
        if "lsms2002en" in row.get("source_path", "").lower() and "data_2002" in row.get("source_path", "").lower()
    ]
    for index, row in enumerate(raw_rows):
        variable = row.get("variable_name", "")
        label = row.get("variable_label", "")
        classified = classify_variable(variable, label)
        if classified is None:
            continue
        role, signal = classified
        if role == "raw_coordinate_variable_candidate":
            value_status = "schema_keyword_only_values_not_verified"
            reason = "A coordinate keyword appears in raw schema metadata; values, units, precision, and linkage level still require direct verification."
            action = "Read observed values and verify whether they are household/cluster GPS coordinates, not IDs or non-geographic fields."
        elif role == "raw_psu_or_ea_variable":
            value_status = "admin_sampling_identifier_observed"
            reason = "PSU/enumerator-area identifiers are useful for sampling design but are not coordinates or polygons."
            action = "Search for official EA maps or an EA-to-coordinate/boundary crosswalk that can join to these identifiers."
        else:
            value_status = "admin_label_or_code_observed"
            reason = "Admin labels/codes are observed, but no verified historical polygon or coordinate artifact is attached."
            action = "Validate district/commune codes against a historical 2001/2002 boundary source before admin-level climate aggregation."
        rows.append(
            {
                "evidence_id": f"var_{index:04d}",
                "evidence_type": "raw_variable_schema",
                "source_path": row.get("source_path", ""),
                "file_name": Path(row.get("source_path", "")).name,
                "sheet_name": "",
                "row_number": "",
                "column_number": "",
                "variable_name": variable,
                "variable_label": label,
                "evidence_role": role,
                "evidence_signal": signal,
                "local_value_status": value_status,
                "promotion_status": "blocked_not_ready_for_climate_linkage",
                "blocking_reason": reason,
                "next_review_action": action,
            }
        )
    return rows


def classify_questionnaire_cell(text: str) -> tuple[str, str] | None:
    if COORD_RE.search(text):
        return "questionnaire_coordinate_field", "coordinate_keyword_in_questionnaire"
    if MAP_RE.search(text):
        return "questionnaire_map_or_boundary_text", "map_or_boundary_keyword_in_questionnaire"
    if ADMIN_RE.search(text):
        return "questionnaire_admin_geography_text", "admin_geography_keyword_in_questionnaire"
    return None


def questionnaire_rows(root: Path) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    workbooks = sorted(root.glob("Questionnaire 2002/*.xls")) + sorted(root.glob("Questionnaire 2002/*.xlsx"))
    row_index = 0
    for workbook in workbooks:
        try:
            sheets = pd.read_excel(workbook, sheet_name=None, header=None, dtype=str)
        except Exception as exc:  # noqa: BLE001 - audit should preserve read failure instead of crashing.
            rows.append(
                {
                    "evidence_id": f"questionnaire_{row_index:04d}",
                    "evidence_type": "questionnaire_read_attempt",
                    "source_path": rel(workbook),
                    "file_name": workbook.name,
                    "sheet_name": "",
                    "row_number": "",
                    "column_number": "",
                    "variable_name": "",
                    "variable_label": "",
                    "evidence_role": "questionnaire_read_failed",
                    "evidence_signal": type(exc).__name__,
                    "local_value_status": "questionnaire_not_read",
                    "promotion_status": "blocked_not_ready_for_climate_linkage",
                    "blocking_reason": f"Questionnaire workbook could not be scanned: {exc}",
                    "next_review_action": "Repair or convert the workbook before using questionnaire geography evidence.",
                }
            )
            row_index += 1
            continue
        for sheet_name, df in sheets.items():
            for r in range(df.shape[0]):
                for c in range(df.shape[1]):
                    text = fmt(df.iat[r, c]).strip()
                    if not text:
                        continue
                    classified = classify_questionnaire_cell(text)
                    if classified is None:
                        continue
                    role, signal = classified
                    if role == "questionnaire_coordinate_field":
                        reason = "Questionnaire contains coordinate fields, but no corresponding raw coordinate variables or values are verified in the extracted data package."
                        action = "Locate the raw coordinate file/variables or official GPS ancillary file that should contain these questionnaire fields."
                    elif role == "questionnaire_map_or_boundary_text":
                        reason = "Questionnaire/document text references maps or boundaries, but no local GIS artifact is verified."
                        action = "Locate EA maps, boundary files, or codebooks with join keys before climate aggregation."
                    else:
                        reason = "Questionnaire documents admin geography fields; raw data and historical boundary joins still need verification."
                        action = "Cross-check questionnaire fields against raw variables and historical boundary/crosswalk sources."
                    rows.append(
                        {
                            "evidence_id": f"questionnaire_{row_index:04d}",
                            "evidence_type": "questionnaire_text",
                            "source_path": rel(workbook),
                            "file_name": workbook.name,
                            "sheet_name": fmt(sheet_name),
                            "row_number": str(r + 1),
                            "column_number": str(c + 1),
                            "variable_name": "",
                            "variable_label": text[:300],
                            "evidence_role": role,
                            "evidence_signal": signal,
                            "local_value_status": "questionnaire_design_field_observed",
                            "promotion_status": "blocked_not_ready_for_climate_linkage",
                            "blocking_reason": reason,
                            "next_review_action": action,
                        }
                    )
                    row_index += 1
    return rows


def summary_row(metric: str, value: Any, interpretation: str) -> dict[str, str]:
    return {"metric": metric, "value": fmt(value), "interpretation": interpretation}


def build_summary(rows: list[dict[str, str]], source_summary: list[dict[str, str]]) -> list[dict[str, str]]:
    files = [row for row in rows if row["evidence_type"].startswith("local_file")]
    raw_tabular_files = [row for row in files if Path(row["file_name"]).suffix.lower() in RAW_TABULAR_SUFFIXES]
    gis_files = [row for row in files if row["evidence_role"] == "potential_geography_or_boundary_file" and Path(row["file_name"]).suffix.lower() in GIS_SUFFIXES]
    coordinate_variables = [row for row in rows if row["evidence_role"] == "raw_coordinate_variable_candidate"]
    admin_variables = [row for row in rows if row["evidence_role"] in {"raw_psu_or_ea_variable", "raw_district_or_commune_variable", "raw_admin_geography_variable"}]
    psu_ea_variables = [row for row in rows if row["evidence_role"] == "raw_psu_or_ea_variable"]
    district_commune_variables = [row for row in rows if row["evidence_role"] == "raw_district_or_commune_variable"]
    questionnaire_coordinates = [row for row in rows if row["evidence_role"] == "questionnaire_coordinate_field"]
    questionnaire_admin = [row for row in rows if row["evidence_role"] == "questionnaire_admin_geography_text"]
    questionnaire_maps = [row for row in rows if row["evidence_role"] == "questionnaire_map_or_boundary_text"]
    official_gps_doc = metric_value(source_summary, "alb2002_boundary_source_alternative_gps_documented_rows", "0")
    official_maps_doc = metric_value(source_summary, "alb2002_boundary_source_alternative_lsms_maps_documented_rows", "0")
    return [
        summary_row("alb2002_local_geo_artifact_files_scanned", len(files), "Files scanned under the extracted ALB_2002 package."),
        summary_row("alb2002_local_geo_artifact_raw_tabular_files", len(raw_tabular_files), "Raw tabular/document workbook files observed locally."),
        summary_row("alb2002_local_geo_artifact_gis_file_candidate_rows", len(gis_files), "Local GIS/boundary file candidates with recognized GIS suffixes; zero means no shapefile/GeoJSON/KML/GPX/GPKG candidate was found."),
        summary_row("alb2002_local_geo_artifact_coordinate_raw_variable_rows", len(coordinate_variables), "Raw schema variables with coordinate/GPS keywords."),
        summary_row("alb2002_local_geo_artifact_questionnaire_coordinate_field_rows", len(questionnaire_coordinates), "Questionnaire cells documenting coordinate/GPS fields."),
        summary_row("alb2002_local_geo_artifact_admin_variable_rows", len(admin_variables), "Raw schema variables documenting admin/sampling geography but not coordinates."),
        summary_row("alb2002_local_geo_artifact_psu_ea_variable_rows", len(psu_ea_variables), "Raw schema variables documenting PSU or enumerator-area identifiers."),
        summary_row("alb2002_local_geo_artifact_district_commune_variable_rows", len(district_commune_variables), "Raw schema variables documenting district/commune/municipality fields."),
        summary_row("alb2002_local_geo_artifact_questionnaire_admin_text_rows", len(questionnaire_admin), "Questionnaire cells documenting admin geography fields."),
        summary_row("alb2002_local_geo_artifact_questionnaire_map_text_rows", len(questionnaire_maps), "Questionnaire cells documenting map/boundary/GIS language."),
        summary_row("alb2002_local_geo_artifact_official_gps_documented_rows", official_gps_doc, "Upstream source-alternatives rows documenting GPS/longitude/latitude evidence."),
        summary_row("alb2002_local_geo_artifact_official_ea_map_documented_rows", official_maps_doc, "Upstream source-alternatives rows documenting EA boundary-map evidence."),
        summary_row("alb2002_local_geo_artifact_local_coordinate_ready_rows", 0, "Local raw coordinate artifacts ready for climate linkage after this audit; intentionally zero."),
        summary_row("alb2002_local_geo_artifact_local_boundary_ready_rows", 0, "Local boundary/GIS artifacts ready for climate linkage after this audit; intentionally zero."),
        summary_row("alb2002_local_geo_artifact_climate_linkage_ready_rows", 0, "ALB_2002 rows ready for climate-linkage input promotion after this audit; intentionally zero."),
        summary_row("alb2002_local_geo_artifact_current_decision", DECISION, "Current fail-closed decision for local ALB_2002 geography artifacts."),
    ]


def markdown_rows(rows: list[dict[str, str]], columns: list[str], limit: int = 20) -> str:
    lines = ["| " + " | ".join(columns) + " |", "|" + "|".join("---" for _ in columns) + "|"]
    for row in rows[:limit]:
        values = []
        for column in columns:
            value = (row.get(column, "") or "").replace("|", "/")
            if len(value) > 120:
                value = value[:117] + "..."
            values.append(value)
        lines.append("| " + " | ".join(values) + " |")
    return "\n".join(lines)


def write_report(rows: list[dict[str, str]], summary: list[dict[str, str]]) -> None:
    summary_table = "\n".join(f"| {row['metric']} | {row['value']} | {row['interpretation']} |" for row in summary)
    coord_questionnaire = [row for row in rows if row["evidence_role"] == "questionnaire_coordinate_field"]
    coord_variables = [row for row in rows if row["evidence_role"] == "raw_coordinate_variable_candidate"]
    admin_variables = [row for row in rows if row["evidence_role"] in {"raw_psu_or_ea_variable", "raw_district_or_commune_variable", "raw_admin_geography_variable"}]
    REPORT_PATH.write_text(
        f"""# ALB_2002 Local Geography Artifact Audit

Status: temp-only local geography artifact gap audit. This audit scans the extracted ALB_2002 raw package, raw schema catalog, and questionnaire workbook for coordinate, GPS, EA, district, commune, map, boundary, and GIS evidence. It does not create centroids, does not write `data/`, and does not construct climate exposures.

## Summary

| Metric | Value | Interpretation |
|---|---:|---|
{summary_table}

## Questionnaire Coordinate Fields

{markdown_rows(coord_questionnaire, ['source_path', 'sheet_name', 'row_number', 'column_number', 'variable_label', 'blocking_reason'], 20) if coord_questionnaire else 'No questionnaire coordinate fields found.'}

## Raw Coordinate Variable Candidates

{markdown_rows(coord_variables, ['source_path', 'variable_name', 'variable_label', 'local_value_status', 'blocking_reason'], 20) if coord_variables else 'No raw coordinate/GPS variables found in the extracted ALB_2002 raw schema catalog.'}

## Raw Admin/Sampling Geography Variables

{markdown_rows(admin_variables, ['source_path', 'variable_name', 'variable_label', 'evidence_role', 'blocking_reason'], 30) if admin_variables else 'No raw admin or sampling geography variables found.'}

## Interpretation

- The ALB_2002 questionnaire workbook contains coordinate design fields, including longitude and latitude on the cover sheet.
- The extracted raw schema catalog contains admin/sampling geography fields such as district, municipality/commune, PSU, enumerator area, stratum, and urban/rural.
- The extracted local package does not currently expose raw coordinate variables or a recognized GIS/boundary file candidate.
- This creates a specific gap: GPS was documented in source/questionnaire evidence, but the local raw value artifact needed for point climate extraction has not been verified.
- Climate-linkage-ready rows remain zero.

## Machine-Readable Outputs

- `temp/alb2002_local_geography_artifact_audit.csv`
- `result/alb2002_local_geography_artifact_summary.csv`
""",
        encoding="utf-8",
    )


def main() -> None:
    ensure_dirs()
    root = source_root()
    rows = file_rows(root)
    rows.extend(variable_rows())
    rows.extend(questionnaire_rows(root))
    source_summary = read_csv_dicts(SOURCE_ALTERNATIVE_SUMMARY)
    summary = build_summary(rows, source_summary)
    write_csv(AUDIT_PATH, rows, AUDIT_COLUMNS)
    write_csv(SUMMARY_PATH, summary, SUMMARY_COLUMNS)
    write_report(rows, summary)
    append_log(TEMP_DIR / "audit_log.md", f"Built ALB_2002 local geography artifact audit rows={len(rows)} decision={DECISION}.")
    print(f"ALB_2002 local geography artifact audit rows={len(rows)} decision={DECISION}.")


if __name__ == "__main__":
    main()
