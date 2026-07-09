from __future__ import annotations

import json
import math
import unicodedata
import urllib.error
import urllib.request
from difflib import SequenceMatcher
from typing import Any

import pandas as pd

from common import REPORT_DIR, RESULT_DIR, SNAPSHOT_DIR, TEMP_DIR, append_log, ensure_dirs, sha256_file, write_csv


TEMPLATE_PATH = TEMP_DIR / "alb2002_district_climate_crosswalk_template.csv"
SOURCE_PROBE_PATH = TEMP_DIR / "alb2002_district_boundary_source_probe.csv"
GEOJSON_PATH = SNAPSHOT_DIR / "alb2002_geoboundaries_alb_adm2_current.geojson"
MATCH_AUDIT_PATH = TEMP_DIR / "alb2002_boundary_name_match_audit.csv"
BOUNDARY_INVENTORY_PATH = TEMP_DIR / "alb2002_boundary_geojson_inventory.csv"
SUMMARY_PATH = RESULT_DIR / "alb2002_boundary_name_match_summary.csv"
REPORT_PATH = REPORT_DIR / "alb2002_boundary_name_match_audit.md"

DEFAULT_GEOJSON_URL = "https://github.com/wmgeolab/geoBoundaries/raw/9469f09/releaseData/gbOpen/ALB/ADM2/geoBoundaries-ALB-ADM2.geojson"
DECISION = "blocked_current_boundary_name_match_incomplete_historical_crosswalk_no_gps"

MATCH_COLUMNS = [
    "country",
    "survey_name",
    "wave",
    "idno",
    "district_code_identification",
    "district_name_identification",
    "survey_review_key",
    "survey_review_key_euro_as_c",
    "household_rows",
    "boundary_source_url",
    "boundary_year_represented",
    "boundary_feature_count",
    "boundary_name_field",
    "best_boundary_name",
    "best_boundary_review_key",
    "best_match_method",
    "best_match_score",
    "match_status",
    "promotion_status",
    "blocking_reason",
]
INVENTORY_COLUMNS = [
    "boundary_source_url",
    "boundary_sha256",
    "boundary_feature_index",
    "boundary_name_field",
    "boundary_name",
    "boundary_review_key",
    "geometry_type",
    "property_keys",
]
SUMMARY_COLUMNS = ["metric", "value", "interpretation"]


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


def normalize_name(value: Any, euro_as_c: bool = False) -> str:
    text = fmt(value).strip().upper()
    if euro_as_c:
        text = text.replace("€", "C")
    normalized = unicodedata.normalize("NFKD", text)
    ascii_text = normalized.encode("ascii", "ignore").decode("ascii")
    cleaned = "".join(ch if ch.isalnum() else " " for ch in ascii_text)
    return " ".join(cleaned.split())


def read_csv_dicts(path: Any) -> list[dict[str, str]]:
    p = path if hasattr(path, "exists") else None
    if p is None or not p.exists():
        return []
    return list(pd.read_csv(p, dtype=str, keep_default_na=False).to_dict("records"))


def boundary_download_url(source_rows: list[dict[str, str]]) -> str:
    for row in source_rows:
        url = row.get("download_url", "").strip()
        if url:
            return url
    return DEFAULT_GEOJSON_URL


def boundary_year(source_rows: list[dict[str, str]]) -> str:
    for row in source_rows:
        year = row.get("boundary_year_represented", "").strip()
        if year:
            return year
    return ""


def download_geojson(url: str) -> tuple[dict[str, Any] | None, str, str]:
    request = urllib.request.Request(url, headers={"User-Agent": "climate-uhc-ml-audit/1.0"})
    try:
        with urllib.request.urlopen(request, timeout=45) as response:
            body = response.read()
        GEOJSON_PATH.parent.mkdir(parents=True, exist_ok=True)
        GEOJSON_PATH.write_bytes(body)
        return json.loads(body.decode("utf-8")), "downloaded_geojson_snapshot", ""
    except urllib.error.HTTPError as exc:
        return None, "blocked_geojson_http_error", f"{exc.code}: {exc}"
    except (urllib.error.URLError, TimeoutError, json.JSONDecodeError, UnicodeDecodeError) as exc:
        return None, "blocked_geojson_unreachable_or_unparseable", str(exc)


def choose_name(props: dict[str, Any]) -> tuple[str, str]:
    preferred = ["shapeName", "shapeName_1", "NAME_2", "NAME_1", "ADM2_EN", "ADM2_NAME", "name", "Name", "NAME"]
    for key in preferred:
        value = fmt(props.get(key)).strip()
        if value:
            return key, value
    for key, value in props.items():
        if "name" in key.lower() and fmt(value).strip():
            return key, fmt(value).strip()
    return "", ""


def boundary_rows(geojson: dict[str, Any], source_url: str) -> list[dict[str, str]]:
    features = geojson.get("features", [])
    checksum = sha256_file(GEOJSON_PATH) if GEOJSON_PATH.exists() else ""
    rows: list[dict[str, str]] = []
    for index, feature in enumerate(features):
        props = feature.get("properties") or {}
        name_field, name = choose_name(props)
        geometry = feature.get("geometry") or {}
        rows.append(
            {
                "boundary_source_url": source_url,
                "boundary_sha256": checksum,
                "boundary_feature_index": str(index),
                "boundary_name_field": name_field,
                "boundary_name": name,
                "boundary_review_key": normalize_name(name, euro_as_c=True),
                "geometry_type": fmt(geometry.get("type")),
                "property_keys": ";".join(sorted(str(key) for key in props.keys())),
            }
        )
    return rows


def best_match(survey_key: str, repaired_key: str, boundaries: list[dict[str, str]]) -> tuple[dict[str, str] | None, str, float]:
    by_key: dict[str, dict[str, str]] = {}
    for row in boundaries:
        key = row.get("boundary_review_key", "")
        if key and key not in by_key:
            by_key[key] = row
    if survey_key in by_key:
        return by_key[survey_key], "exact_normalized_name_match", 1.0
    if repaired_key and repaired_key in by_key:
        return by_key[repaired_key], "mojibake_euro_as_c_name_match", 1.0

    best_row: dict[str, str] | None = None
    best_score = 0.0
    target = repaired_key or survey_key
    for row in boundaries:
        key = row.get("boundary_review_key", "")
        if not key or not target:
            continue
        score = SequenceMatcher(None, target, key).ratio()
        if score > best_score:
            best_score = score
            best_row = row
    if best_row is not None and best_score >= 0.92:
        return best_row, "high_similarity_name_match_requires_review", best_score
    return best_row, "no_name_match", best_score


def build_match_rows(
    template: list[dict[str, str]],
    boundaries: list[dict[str, str]],
    source_url: str,
    represented_year: str,
    download_status: str,
) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    feature_count = len(boundaries)
    for row in template:
        survey_name = row.get("district_name_identification", "")
        survey_key = normalize_name(survey_name)
        repaired_key = normalize_name(survey_name, euro_as_c=True)
        match, method, score = best_match(survey_key, repaired_key, boundaries)
        if download_status != "downloaded_geojson_snapshot":
            match_status = download_status
            blocking = "Boundary GeoJSON could not be downloaded or parsed; no survey-to-boundary name comparison is possible."
        elif method == "no_name_match":
            match_status = "blocked_no_current_boundary_name_match"
            blocking = "Survey district name did not match the current public boundary names after normalized and high-similarity review."
        else:
            match_status = "candidate_current_boundary_name_match_not_historical_or_geometric_verified"
            blocking = "Name match is candidate evidence only; 2021 current boundaries are not verified as 2002 survey districts, polygons/centroids are not reviewed, and no household or cluster GPS exists."
        rows.append(
            {
                "country": row.get("country", "Albania"),
                "survey_name": row.get("survey_name", "Living Standards Measurement Survey 2002"),
                "wave": row.get("wave", "2002"),
                "idno": row.get("idno", "ALB_2002_LSMS_v01_M"),
                "district_code_identification": row.get("district_code_identification", ""),
                "district_name_identification": survey_name,
                "survey_review_key": survey_key,
                "survey_review_key_euro_as_c": repaired_key,
                "household_rows": row.get("household_rows", ""),
                "boundary_source_url": source_url,
                "boundary_year_represented": represented_year,
                "boundary_feature_count": str(feature_count),
                "boundary_name_field": match.get("boundary_name_field", "") if match else "",
                "best_boundary_name": match.get("boundary_name", "") if match else "",
                "best_boundary_review_key": match.get("boundary_review_key", "") if match else "",
                "best_match_method": method,
                "best_match_score": f"{score:.3f}" if score else "0",
                "match_status": match_status,
                "promotion_status": "blocked_not_ready_for_climate_linkage",
                "blocking_reason": blocking,
            }
        )
    return rows


def summary_row(metric: str, value: Any, interpretation: str) -> dict[str, str]:
    return {"metric": metric, "value": fmt(value), "interpretation": interpretation}


def build_summary(
    match_rows: list[dict[str, str]],
    boundaries: list[dict[str, str]],
    source_url: str,
    represented_year: str,
    download_status: str,
    download_error: str,
) -> list[dict[str, str]]:
    matched_boundary_keys = {row["best_boundary_review_key"] for row in match_rows if row.get("best_match_method") != "no_name_match" and row.get("best_boundary_review_key")}
    all_boundary_keys = {row["boundary_review_key"] for row in boundaries if row.get("boundary_review_key")}
    boundary_key_counts: dict[str, int] = {}
    for row in boundaries:
        key = row.get("boundary_review_key", "")
        if key:
            boundary_key_counts[key] = boundary_key_counts.get(key, 0) + 1
    duplicate_keys = sorted(key for key, count in boundary_key_counts.items() if count > 1)
    duplicate_feature_rows = sum(count for key, count in boundary_key_counts.items() if count > 1)
    unmatched_boundary_keys = sorted(all_boundary_keys - matched_boundary_keys)
    return [
        summary_row("alb2002_boundary_name_match_survey_district_rows", len(match_rows), "ALB_2002 survey district rows compared to public boundary names."),
        summary_row("alb2002_boundary_name_match_geojson_feature_rows", len(boundaries), "Features parsed from the public boundary GeoJSON snapshot."),
        summary_row("alb2002_boundary_name_match_exact_rows", sum(1 for row in match_rows if row["best_match_method"] == "exact_normalized_name_match"), "Survey rows matching boundary names by normalized exact match."),
        summary_row("alb2002_boundary_name_match_euro_repaired_rows", sum(1 for row in match_rows if row["best_match_method"] == "mojibake_euro_as_c_name_match"), "Survey rows matching only after treating euro-sign mojibake as C."),
        summary_row("alb2002_boundary_name_match_high_similarity_rows", sum(1 for row in match_rows if row["best_match_method"] == "high_similarity_name_match_requires_review"), "Survey rows with high-similarity candidate matches requiring manual review."),
        summary_row("alb2002_boundary_name_match_unmatched_survey_rows", sum(1 for row in match_rows if row["best_match_method"] == "no_name_match"), "Survey district rows without a candidate boundary-name match."),
        summary_row("alb2002_boundary_name_match_unmatched_boundary_name_rows", len(unmatched_boundary_keys), "Boundary-name keys not matched to an observed ALB_2002 district row."),
        summary_row("alb2002_boundary_name_match_duplicate_boundary_name_keys", len(duplicate_keys), "Distinct boundary-name keys appearing in more than one GeoJSON feature."),
        summary_row("alb2002_boundary_name_match_duplicate_boundary_feature_rows", duplicate_feature_rows, "GeoJSON feature rows belonging to duplicate boundary-name keys."),
        summary_row("alb2002_boundary_name_match_download_status", download_status, "Public boundary GeoJSON download/parse status."),
        summary_row("alb2002_boundary_name_match_download_error", download_error, "Download or parse error if any."),
        summary_row("alb2002_boundary_name_match_boundary_source_url", source_url, "Public boundary GeoJSON source URL."),
        summary_row("alb2002_boundary_name_match_boundary_year_represented", represented_year, "Boundary year represented by the public source metadata."),
        summary_row("alb2002_boundary_name_match_historical_year_ready_rows", 0, "Rows ready for 2002 historical boundary validity after this audit; intentionally zero."),
        summary_row("alb2002_boundary_name_match_climate_linkage_ready_rows", 0, "Rows ready for climate-linkage input promotion after this audit; intentionally zero."),
        summary_row("alb2002_boundary_name_match_current_decision", DECISION, "Current fail-closed decision for ALB_2002 boundary name matching."),
    ]


def markdown_rows(rows: list[dict[str, str]], columns: list[str], limit: int = 20) -> str:
    lines = ["| " + " | ".join(columns) + " |", "|" + "|".join("---" for _ in columns) + "|"]
    for row in rows[:limit]:
        values = []
        for column in columns:
            value = (row.get(column, "") or "").replace("|", "/")
            if len(value) > 100:
                value = value[:97] + "..."
            values.append(value)
        lines.append("| " + " | ".join(values) + " |")
    return "\n".join(lines)


def write_report(match_rows: list[dict[str, str]], boundaries: list[dict[str, str]], summary: list[dict[str, str]]) -> None:
    summary_table = "\n".join(f"| {row['metric']} | {row['value']} | {row['interpretation']} |" for row in summary)
    unmatched_survey = [row for row in match_rows if row["best_match_method"] == "no_name_match"]
    unmatched_boundary_keys = sorted(
        {row["boundary_review_key"] for row in boundaries if row.get("boundary_review_key")}
        - {row["best_boundary_review_key"] for row in match_rows if row.get("best_match_method") != "no_name_match" and row.get("best_boundary_review_key")}
    )
    boundary_extra_rows = [{"unmatched_boundary_review_key": key} for key in unmatched_boundary_keys]
    boundary_key_counts: dict[str, int] = {}
    for row in boundaries:
        key = row.get("boundary_review_key", "")
        if key:
            boundary_key_counts[key] = boundary_key_counts.get(key, 0) + 1
    duplicate_boundary_rows = [
        {"duplicate_boundary_review_key": key, "feature_count": str(count)}
        for key, count in sorted(boundary_key_counts.items())
        if count > 1
    ]
    REPORT_PATH.write_text(
        f"""# ALB_2002 Boundary Name Match Audit

Status: temp-only public boundary name audit. This audit downloads a public current ADM2 GeoJSON snapshot to `temp/source_snapshots/`, compares boundary names with observed ALB_2002 district labels, and keeps promotion blocked. It does not create centroids, does not construct climate-linkage input, does not write `data/`, and does not construct climate exposures.

## Summary

| Metric | Value | Interpretation |
|---|---:|---|
{summary_table}

## Survey-to-Boundary Name Match Preview

{markdown_rows(match_rows, ['district_code_identification', 'district_name_identification', 'survey_review_key_euro_as_c', 'best_boundary_name', 'best_match_method', 'match_status'], 40)}

## Unmatched Survey Districts

{markdown_rows(unmatched_survey, ['district_code_identification', 'district_name_identification', 'survey_review_key_euro_as_c', 'best_boundary_name', 'best_match_score'], 20) if unmatched_survey else 'No unmatched survey district rows after candidate name matching.'}

## Boundary Names Not Observed in ALB_2002

{markdown_rows(boundary_extra_rows, ['unmatched_boundary_review_key'], 20) if boundary_extra_rows else 'No unmatched boundary-name keys after candidate name matching.'}

## Duplicate Boundary Name Keys

{markdown_rows(duplicate_boundary_rows, ['duplicate_boundary_review_key', 'feature_count'], 20) if duplicate_boundary_rows else 'No duplicate boundary-name keys found in the public GeoJSON.'}

## Interpretation

- Name matches are candidate evidence only; they are not a historical boundary crosswalk.
- The public boundary source is represented as current ADM2 metadata, not verified 2002 LSMS fieldwork geography.
- Two ALB_2002 district labels require mojibake-style review before accepting any automated name match.
- The public boundary file has a different unit count from the observed survey district groups, and duplicate/missing name evidence must be explained before climate linkage.
- No household or cluster GPS exists in the ALB_2002 candidate; any future linkage would be admin-level and must report measurement error.
- Climate-linkage-ready rows remain zero.

## Machine-Readable Outputs

- `temp/alb2002_boundary_name_match_audit.csv`
- `temp/alb2002_boundary_geojson_inventory.csv`
- `temp/source_snapshots/alb2002_geoboundaries_alb_adm2_current.geojson`
- `result/alb2002_boundary_name_match_summary.csv`
""",
        encoding="utf-8",
    )


def main() -> None:
    ensure_dirs()
    if not TEMPLATE_PATH.exists():
        raise FileNotFoundError(f"Missing prerequisite: {TEMPLATE_PATH}")
    source_rows = read_csv_dicts(SOURCE_PROBE_PATH)
    source_url = boundary_download_url(source_rows)
    represented_year = boundary_year(source_rows)
    geojson, download_status, download_error = download_geojson(source_url)
    boundaries = boundary_rows(geojson or {"features": []}, source_url)
    template = read_csv_dicts(TEMPLATE_PATH)
    match_rows = build_match_rows(template, boundaries, source_url, represented_year, download_status)
    summary = build_summary(match_rows, boundaries, source_url, represented_year, download_status, download_error)
    write_csv(MATCH_AUDIT_PATH, match_rows, MATCH_COLUMNS)
    write_csv(BOUNDARY_INVENTORY_PATH, boundaries, INVENTORY_COLUMNS)
    write_csv(SUMMARY_PATH, summary, SUMMARY_COLUMNS)
    write_report(match_rows, boundaries, summary)
    append_log(
        TEMP_DIR / "audit_log.md",
        f"Built ALB_2002 boundary name match audit rows={len(match_rows)} boundary_features={len(boundaries)} decision={DECISION}.",
    )
    print(f"ALB_2002 boundary name match audit rows={len(match_rows)} boundary_features={len(boundaries)} decision={DECISION}.")


if __name__ == "__main__":
    main()
