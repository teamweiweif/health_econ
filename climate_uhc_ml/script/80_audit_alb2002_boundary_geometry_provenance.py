from __future__ import annotations

import csv
import json
import math
import re
import unicodedata
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any

from common import REPORT_DIR, RESULT_DIR, SNAPSHOT_DIR, TEMP_DIR, append_log, ensure_dirs, sha256_file, write_csv


TEMPLATE_PATH = TEMP_DIR / "alb2002_district_climate_crosswalk_template.csv"
RESOURCE_SUMMARY_PATH = RESULT_DIR / "alb2002_boundary_source_resource_search_summary.csv"
GEOJSON_PATH = SNAPSHOT_DIR / "alb2002_geoboundaries_2_0_1_alb_adm2.geojson"
METADATA_PATH = SNAPSHOT_DIR / "alb2002_geoboundaries_2_0_1_alb_adm2_metadata.json"
GEOMETRY_AUDIT_PATH = TEMP_DIR / "alb2002_boundary_geometry_provenance_audit.csv"
METADATA_AUDIT_PATH = TEMP_DIR / "alb2002_boundary_metadata_provenance_probe.csv"
SUMMARY_PATH = RESULT_DIR / "alb2002_boundary_geometry_provenance_summary.csv"
REPORT_PATH = REPORT_DIR / "alb2002_boundary_geometry_provenance_audit.md"

GEOJSON_URL = "https://www.geoboundaries.org/data/geoBoundaries-2_0_1/ALB/ADM2/geoBoundaries-2_0_1-ALB-ADM2.geojson"
METADATA_URL = "https://www.geoboundaries.org/data/geoBoundaries-2_0_1/ALB/ADM2/geoBoundaries-2_0_1-ALB-ADM2-metaData.json"
DECISION = "blocked_geoboundaries_2_0_1_boundary_year_2013_not_verified_2002"

ADMIN_TERMS_RE = re.compile(
    r"\b(DISTRICT|BASHKIA|MUNICIPALITY|MUNICIPALLY|QARKU|QARK|RRETHI|RRETH|PREFECTURE|COUNTY)\b"
)
ALIASES = {"TIRANE": "TIRANA"}
BROAD_ALBANIA_BBOX = (18.0, 39.0, 22.0, 43.5)

GEOMETRY_COLUMNS = [
    "feature_index",
    "shape_id",
    "shape_name",
    "boundary_key",
    "survey_district_code",
    "survey_district_name",
    "survey_match_method",
    "shape_group",
    "shape_type",
    "shape_iso",
    "geometry_type",
    "polygon_parts",
    "ring_count",
    "coordinate_pair_count",
    "closed_ring_failures",
    "out_of_range_coordinate_pairs",
    "bbox_min_lon",
    "bbox_min_lat",
    "bbox_max_lon",
    "bbox_max_lat",
    "bbox_centroid_lon",
    "bbox_centroid_lat",
    "within_broad_albania_bbox",
    "geometry_structure_status",
    "historical_2002_boundary_ready",
    "climate_linkage_ready",
    "promotion_status",
    "blocking_reason",
]
METADATA_COLUMNS = [
    "probe_id",
    "source_url",
    "local_snapshot_path",
    "local_snapshot_sha256",
    "http_status",
    "probe_status",
    "field",
    "value",
    "evidence_status",
    "interpretation",
]
SUMMARY_COLUMNS = ["metric", "value", "interpretation"]


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


def metric_value(rows: list[dict[str, str]], metric: str, default: str = "") -> str:
    for row in rows:
        if row.get("metric") == metric:
            return row.get("value", default)
    return default


def canonical_key(value: Any, repair_euro: bool = True, apply_alias: bool = True) -> str:
    text = fmt(value).strip()
    if repair_euro:
        text = text.replace("\u20ac", "C")
    normalized = unicodedata.normalize("NFKD", text)
    ascii_text = normalized.encode("ascii", "ignore").decode("ascii")
    upper = ADMIN_TERMS_RE.sub(" ", ascii_text.upper())
    cleaned = re.sub(r"[^A-Z0-9]+", " ", upper)
    key = " ".join(cleaned.split())
    if apply_alias:
        key = ALIASES.get(key, key)
    return key


def safe_download_json(url: str, path: Path) -> tuple[dict[str, Any] | None, str, str, str]:
    request = urllib.request.Request(
        url,
        headers={
            "User-Agent": "climate-uhc-ml-audit/1.0",
            "Accept": "application/json,application/geo+json,*/*",
        },
    )
    try:
        with urllib.request.urlopen(request, timeout=45) as response:
            status = str(getattr(response, "status", ""))
            body = response.read()
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(body)
        return json.loads(body.decode("utf-8")), "downloaded_json", status, ""
    except urllib.error.HTTPError as exc:
        return None, "blocked_http_error", str(exc.code), str(exc)
    except (urllib.error.URLError, TimeoutError, OSError, json.JSONDecodeError, UnicodeDecodeError) as exc:
        return None, "blocked_unreachable_or_parse_error", "", str(exc)


def load_geojson() -> tuple[dict[str, Any], str, str, str]:
    if GEOJSON_PATH.exists():
        try:
            return json.loads(GEOJSON_PATH.read_text(encoding="utf-8")), "local_geojson_snapshot_parsed", "", ""
        except (json.JSONDecodeError, UnicodeDecodeError):
            pass
    obj, status, http_status, error = safe_download_json(GEOJSON_URL, GEOJSON_PATH)
    return obj or {"type": "", "features": []}, status, http_status, error


def load_metadata() -> tuple[dict[str, Any], str, str, str]:
    obj, status, http_status, error = safe_download_json(METADATA_URL, METADATA_PATH)
    return obj or {}, status, http_status, error


def build_survey_lookup(rows: list[dict[str, str]]) -> dict[str, dict[str, str]]:
    lookup: dict[str, dict[str, str]] = {}
    for row in rows:
        name = row.get("district_name_identification", "")
        variants = [
            ("exact_normalized_survey_name", canonical_key(name, repair_euro=False, apply_alias=False)),
            ("encoding_repaired_survey_name", canonical_key(name, repair_euro=True, apply_alias=False)),
            ("documented_alias_survey_name", canonical_key(name, repair_euro=True, apply_alias=True)),
        ]
        for method, key in variants:
            if key and key not in lookup:
                copy = dict(row)
                copy["_match_method"] = method
                lookup[key] = copy
    return lookup


def iter_positions(geometry: dict[str, Any]) -> tuple[int, int, int, int, list[tuple[float, float]]]:
    geometry_type = geometry.get("type", "")
    coords = geometry.get("coordinates", [])
    polygons = coords if geometry_type == "MultiPolygon" else [coords] if geometry_type == "Polygon" else []
    polygon_parts = len(polygons)
    ring_count = 0
    closed_ring_failures = 0
    out_of_range = 0
    points: list[tuple[float, float]] = []
    for polygon in polygons:
        if not isinstance(polygon, list):
            continue
        for ring in polygon:
            if not isinstance(ring, list):
                continue
            ring_count += 1
            parsed_ring: list[tuple[float, float]] = []
            for point in ring:
                if not isinstance(point, list | tuple) or len(point) < 2:
                    continue
                try:
                    lon = float(point[0])
                    lat = float(point[1])
                except (TypeError, ValueError):
                    continue
                if not (-180 <= lon <= 180 and -90 <= lat <= 90):
                    out_of_range += 1
                parsed_ring.append((lon, lat))
                points.append((lon, lat))
            if parsed_ring and parsed_ring[0] != parsed_ring[-1]:
                closed_ring_failures += 1
    return polygon_parts, ring_count, len(points), closed_ring_failures, out_of_range, points


def geometry_rows(geojson: dict[str, Any], survey_rows: list[dict[str, str]]) -> list[dict[str, str]]:
    lookup = build_survey_lookup(survey_rows)
    rows: list[dict[str, str]] = []
    for index, feature in enumerate(geojson.get("features", [])):
        props = feature.get("properties") or {}
        geometry = feature.get("geometry") or {}
        shape_name = fmt(props.get("shapeName"))
        boundary_key = canonical_key(shape_name)
        survey = lookup.get(boundary_key, {})
        polygon_parts, ring_count, coordinate_pairs, closed_failures, out_of_range, points = iter_positions(geometry)
        if points:
            min_lon = min(point[0] for point in points)
            min_lat = min(point[1] for point in points)
            max_lon = max(point[0] for point in points)
            max_lat = max(point[1] for point in points)
            centroid_lon = (min_lon + max_lon) / 2
            centroid_lat = (min_lat + max_lat) / 2
        else:
            min_lon = min_lat = max_lon = max_lat = centroid_lon = centroid_lat = float("nan")
        bbox_ok = (
            points
            and min_lon >= BROAD_ALBANIA_BBOX[0]
            and min_lat >= BROAD_ALBANIA_BBOX[1]
            and max_lon <= BROAD_ALBANIA_BBOX[2]
            and max_lat <= BROAD_ALBANIA_BBOX[3]
        )
        if not points:
            geometry_status = "blocked_geometry_coordinates_missing"
        elif geometry.get("type") not in {"Polygon", "MultiPolygon"}:
            geometry_status = "blocked_unexpected_geometry_type"
        elif closed_failures or out_of_range:
            geometry_status = "blocked_geometry_structure_problem"
        elif not bbox_ok:
            geometry_status = "coordinate_structure_parse_ok_outside_broad_albania_bbox"
        else:
            geometry_status = "coordinate_structure_parse_ok_topology_not_validated"
        rows.append(
            {
                "feature_index": str(index),
                "shape_id": fmt(props.get("shapeID")),
                "shape_name": shape_name,
                "boundary_key": boundary_key,
                "survey_district_code": survey.get("district_code_identification", ""),
                "survey_district_name": survey.get("district_name_identification", ""),
                "survey_match_method": survey.get("_match_method", "no_survey_key_match"),
                "shape_group": fmt(props.get("shapeGroup")),
                "shape_type": fmt(props.get("shapeType")),
                "shape_iso": fmt(props.get("shapeISO")),
                "geometry_type": fmt(geometry.get("type")),
                "polygon_parts": str(polygon_parts),
                "ring_count": str(ring_count),
                "coordinate_pair_count": str(coordinate_pairs),
                "closed_ring_failures": str(closed_failures),
                "out_of_range_coordinate_pairs": str(out_of_range),
                "bbox_min_lon": fmt(min_lon),
                "bbox_min_lat": fmt(min_lat),
                "bbox_max_lon": fmt(max_lon),
                "bbox_max_lat": fmt(max_lat),
                "bbox_centroid_lon": fmt(centroid_lon),
                "bbox_centroid_lat": fmt(centroid_lat),
                "within_broad_albania_bbox": "1" if bbox_ok else "0",
                "geometry_structure_status": geometry_status,
                "historical_2002_boundary_ready": "0",
                "climate_linkage_ready": "0",
                "promotion_status": "blocked_not_ready_for_climate_linkage",
                "blocking_reason": "Geometry coordinates parse structurally, but the companion metadata reports boundaryYear 2013 and the audit has not verified 2002 LSMS district vintage, topology, or raw district-code crosswalk.",
            }
        )
    return rows


def metadata_rows(metadata: dict[str, Any], status: str, http_status: str, error: str) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    checksum = sha256_file(METADATA_PATH) if METADATA_PATH.exists() else ""
    if error:
        rows.append(
            {
                "probe_id": "metadata_error",
                "source_url": METADATA_URL,
                "local_snapshot_path": rel(METADATA_PATH) if METADATA_PATH.exists() else "",
                "local_snapshot_sha256": checksum,
                "http_status": http_status,
                "probe_status": status,
                "field": "download_error",
                "value": error,
                "evidence_status": "blocked_metadata_not_verified",
                "interpretation": "Metadata probe failed; no provenance or boundary-year evidence can be accepted from this URL.",
            }
        )
        return rows
    important_fields = [
        "boundaryID",
        "boundaryISO",
        "boundaryType",
        "boundaryYear",
        "boundaryUpdate",
        "boundarySource-1",
        "boundarySource-2",
        "boundarySourceURL",
        "boundaryLicense",
        "licenseDetail",
        "licenseSource",
        "downloadURL",
    ]
    for field in important_fields:
        value = fmt(metadata.get(field))
        if field == "boundaryYear":
            evidence_status = "blocked_boundary_year_2013_not_2002" if value and value != "2002" else "candidate_boundary_year_2002"
            interpretation = "Companion metadata boundaryYear; this is the main vintage gate for ALB_2002."
        elif field.startswith("boundarySource"):
            evidence_status = "source_metadata_present" if value else "source_metadata_missing"
            interpretation = "Companion metadata source field; provenance still requires source-history review against 2002 LSMS geography."
        else:
            evidence_status = "metadata_present" if value else "metadata_missing"
            interpretation = "Companion metadata field captured for provenance review."
        rows.append(
            {
                "probe_id": f"metadata_{field}",
                "source_url": METADATA_URL,
                "local_snapshot_path": rel(METADATA_PATH) if METADATA_PATH.exists() else "",
                "local_snapshot_sha256": checksum,
                "http_status": http_status,
                "probe_status": status,
                "field": field,
                "value": value,
                "evidence_status": evidence_status,
                "interpretation": interpretation,
            }
        )
    return rows


def summary_row(metric: str, value: Any, interpretation: str) -> dict[str, str]:
    return {"metric": metric, "value": fmt(value), "interpretation": interpretation}


def build_summary(
    geometry: list[dict[str, str]],
    metadata: dict[str, Any],
    metadata_status: str,
    geojson_status: str,
    resource_summary: list[dict[str, str]],
) -> list[dict[str, str]]:
    boundary_year = fmt(metadata.get("boundaryYear"))
    source_values = "; ".join(fmt(metadata.get(field)) for field in ["boundarySource-1", "boundarySource-2"] if fmt(metadata.get(field)))
    geometry_parse_ok = sum(1 for row in geometry if row["geometry_structure_status"] == "coordinate_structure_parse_ok_topology_not_validated")
    survey_matched = sum(1 for row in geometry if row["survey_match_method"] != "no_survey_key_match")
    return [
        summary_row("alb2002_boundary_geometry_candidate_resource_id", metric_value(resource_summary, "alb2002_boundary_resource_search_best_candidate_id", "geoboundaries_2_0_1_adm2"), "Resource selected from the prior public resource-search audit for geometry/provenance review."),
        summary_row("alb2002_boundary_geometry_geojson_status", geojson_status, "GeoJSON snapshot parse/download status."),
        summary_row("alb2002_boundary_geometry_metadata_status", metadata_status, "Companion metadata download/parse status."),
        summary_row("alb2002_boundary_geometry_feature_rows", len(geometry), "Boundary features in the candidate GeoJSON."),
        summary_row("alb2002_boundary_geometry_adm2_feature_rows", sum(1 for row in geometry if row["shape_type"] == "ADM2"), "Features whose shapeType property is ADM2."),
        summary_row("alb2002_boundary_geometry_multipolygon_rows", sum(1 for row in geometry if row["geometry_type"] == "MultiPolygon"), "Features represented as MultiPolygon geometry."),
        summary_row("alb2002_boundary_geometry_coordinate_structure_ok_rows", geometry_parse_ok, "Features with parseable polygon coordinate structure, closed rings, coordinate ranges, and a broad Albania bounding box; this is not topology validation."),
        summary_row("alb2002_boundary_geometry_survey_key_matched_rows", survey_matched, "Features matched back to ALB_2002 survey district keys after documented name repairs/aliases."),
        summary_row("alb2002_boundary_geometry_closed_ring_failure_rows", sum(1 for row in geometry if int(row["closed_ring_failures"] or 0) > 0), "Features with at least one unclosed ring."),
        summary_row("alb2002_boundary_geometry_out_of_range_coordinate_rows", sum(1 for row in geometry if int(row["out_of_range_coordinate_pairs"] or 0) > 0), "Features with any longitude/latitude outside global valid ranges."),
        summary_row("alb2002_boundary_geometry_within_broad_albania_bbox_rows", sum(1 for row in geometry if row["within_broad_albania_bbox"] == "1"), "Features whose coordinates fall inside a broad Albania bounding box."),
        summary_row("alb2002_boundary_geometry_metadata_boundary_year", boundary_year, "Boundary year reported by the geoBoundaries 2.0.1 companion metadata."),
        summary_row("alb2002_boundary_geometry_metadata_boundary_update", fmt(metadata.get("boundaryUpdate")), "Boundary update date reported by companion metadata."),
        summary_row("alb2002_boundary_geometry_metadata_boundary_source", source_values, "Boundary source fields reported by companion metadata."),
        summary_row("alb2002_boundary_geometry_metadata_source_url", fmt(metadata.get("boundarySourceURL")), "Boundary source URL reported by companion metadata."),
        summary_row("alb2002_boundary_geometry_boundary_year_matches_2002_rows", 1 if boundary_year == "2002" else 0, "Whether the candidate metadata directly supports a 2002 boundary vintage."),
        summary_row("alb2002_boundary_geometry_topology_validated_rows", 0, "Rows with real topology validation; zero because shapely/geopandas is not required or available in this pipeline step."),
        summary_row("alb2002_boundary_geometry_historical_2002_boundary_ready_rows", 0, "Rows ready as verified 2002 historical district boundaries after this audit; intentionally zero."),
        summary_row("alb2002_boundary_geometry_climate_linkage_ready_rows", 0, "Rows ready for climate-linkage promotion after this audit; intentionally zero."),
        summary_row("alb2002_boundary_geometry_current_decision", DECISION, "Current fail-closed decision for ALB_2002 boundary geometry/provenance."),
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


def write_report(geometry: list[dict[str, str]], metadata_audit: list[dict[str, str]], summary: list[dict[str, str]]) -> None:
    summary_table = "\n".join(f"| {row['metric']} | {row['value']} | {row['interpretation']} |" for row in summary)
    metadata_preview = [row for row in metadata_audit if row["field"] in {"boundaryYear", "boundaryUpdate", "boundarySource-1", "boundarySource-2", "boundarySourceURL", "boundaryLicense", "licenseSource"}]
    REPORT_PATH.write_text(
        f"""# ALB_2002 Boundary Geometry and Provenance Audit

Status: temp-only geometry/provenance audit for the geoBoundaries 2.0.1 ADM2 lead. This audit parses the candidate GeoJSON and companion metadata but does not validate topology with GIS libraries, does not create centroids for analysis, does not write `data/`, and does not construct climate exposures.

## Summary

| Metric | Value | Interpretation |
|---|---:|---|
{summary_table}

## Metadata Provenance Fields

{markdown_rows(metadata_preview, ['field', 'value', 'evidence_status', 'interpretation'], 20)}

## Geometry Structure Preview

{markdown_rows(geometry, ['shape_name', 'survey_district_code', 'survey_match_method', 'geometry_type', 'polygon_parts', 'ring_count', 'coordinate_pair_count', 'within_broad_albania_bbox', 'geometry_structure_status'], 40)}

## Interpretation

- The candidate geoBoundaries 2.0.1 ADM2 file has complete ALB_2002 district-name coverage and parseable coordinate structure.
- The companion metadata reports `boundaryYear` as 2013, with OpenStreetMap/Wambacher provenance, not a 2001/2002 LSMS or census boundary source.
- The audit therefore tightens the blocker: this source is a useful lead for manual review, but it is not verified as the ALB_2002 historical district boundary layer.
- No topology validation, official 2002 district-definition validation, raw district-code crosswalk validation, or climate-linkage promotion is performed here.
- Historical-boundary-ready and climate-linkage-ready rows remain zero.

## Machine-Readable Outputs

- `temp/alb2002_boundary_geometry_provenance_audit.csv`
- `temp/alb2002_boundary_metadata_provenance_probe.csv`
- `result/alb2002_boundary_geometry_provenance_summary.csv`
- `temp/source_snapshots/alb2002_geoboundaries_2_0_1_alb_adm2_metadata.json`
""",
        encoding="utf-8",
    )


def main() -> None:
    ensure_dirs()
    survey = read_csv_dicts(TEMPLATE_PATH)
    if not survey:
        raise FileNotFoundError(f"Missing prerequisite or empty file: {TEMPLATE_PATH}")
    geojson, geojson_status, _, geojson_error = load_geojson()
    metadata, metadata_status, metadata_http_status, metadata_error = load_metadata()
    if geojson_error:
        append_log(TEMP_DIR / "audit_log.md", f"ALB_2002 boundary geometry/provenance GeoJSON warning: {geojson_error}")
    resource_summary = read_csv_dicts(RESOURCE_SUMMARY_PATH)
    geom_rows = geometry_rows(geojson, survey)
    meta_rows = metadata_rows(metadata, metadata_status, metadata_http_status, metadata_error)
    summary = build_summary(geom_rows, metadata, metadata_status, geojson_status, resource_summary)
    write_csv(GEOMETRY_AUDIT_PATH, geom_rows, GEOMETRY_COLUMNS)
    write_csv(METADATA_AUDIT_PATH, meta_rows, METADATA_COLUMNS)
    write_csv(SUMMARY_PATH, summary, SUMMARY_COLUMNS)
    write_report(geom_rows, meta_rows, summary)
    append_log(
        TEMP_DIR / "audit_log.md",
        f"Built ALB_2002 boundary geometry/provenance audit features={len(geom_rows)} decision={DECISION}.",
    )
    print(f"ALB_2002 boundary geometry/provenance audit features={len(geom_rows)} decision={DECISION}.")


if __name__ == "__main__":
    main()
