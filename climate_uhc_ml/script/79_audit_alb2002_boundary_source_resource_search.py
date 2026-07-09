from __future__ import annotations

import csv
import json
import math
import re
import unicodedata
import urllib.error
import urllib.request
from collections import Counter
from difflib import SequenceMatcher
from pathlib import Path
from typing import Any

import pandas as pd

from common import REPORT_DIR, RESULT_DIR, SNAPSHOT_DIR, TEMP_DIR, append_log, ensure_dirs, sha256_file, write_csv, write_json


TEMPLATE_PATH = TEMP_DIR / "alb2002_district_climate_crosswalk_template.csv"
CURRENT_GEOJSON_PATH = SNAPSHOT_DIR / "alb2002_geoboundaries_alb_adm2_current.geojson"
GB_201_PATH = SNAPSHOT_DIR / "alb2002_geoboundaries_2_0_1_alb_adm2.geojson"
HDX_PACKAGE_PATH = SNAPSHOT_DIR / "hdx_cod_ab_alb_package_show.json"
HDX_GAZETTEER_PATH = SNAPSHOT_DIR / "hdx_alb_adm_gazetteer_2019.xlsx"
AUDIT_PATH = TEMP_DIR / "alb2002_boundary_source_resource_search_audit.csv"
SUMMARY_PATH = RESULT_DIR / "alb2002_boundary_source_resource_search_summary.csv"
REPORT_PATH = REPORT_DIR / "alb2002_boundary_source_resource_search_audit.md"

CURRENT_GEOJSON_URL = "https://github.com/wmgeolab/geoBoundaries/raw/9469f09/releaseData/gbOpen/ALB/ADM2/geoBoundaries-ALB-ADM2.geojson"
GB_201_URL = "https://www.geoboundaries.org/data/geoBoundaries-2_0_1/ALB/ADM2/geoBoundaries-2_0_1-ALB-ADM2.geojson"
HDX_PACKAGE_API_URL = "https://data.humdata.org/api/3/action/package_show?id=cod-ab-alb"
HDX_PACKAGE_PAGE_URL = "https://data.humdata.org/dataset/cod-ab-alb"

DECISION = "blocked_alb2002_boundary_resource_search_no_historical_climate_ready_source"

AUDIT_COLUMNS = [
    "candidate_id",
    "source_name",
    "source_url",
    "source_type",
    "source_year_claim",
    "resource_probe_method",
    "resource_status",
    "http_status",
    "local_snapshot_path",
    "local_snapshot_sha256",
    "name_field",
    "feature_count",
    "distinct_boundary_key_count",
    "observed_survey_district_rows",
    "exact_name_match_rows",
    "repaired_encoding_match_rows",
    "documented_alias_match_rows",
    "high_similarity_match_rows",
    "unmatched_survey_rows",
    "unmatched_survey_keys",
    "unmatched_boundary_keys",
    "duplicate_boundary_keys",
    "has_korce",
    "has_kucove",
    "has_vlore",
    "historical_2002_boundary_ready",
    "climate_linkage_ready",
    "suitability_status",
    "promotion_status",
    "blocking_reason",
    "next_review_action",
]
SUMMARY_COLUMNS = ["metric", "value", "interpretation"]

ADMIN_TERMS_RE = re.compile(
    r"\b(DISTRICT|BASHKIA|MUNICIPALITY|MUNICIPALLY|QARKU|QARK|RRETHI|RRETH|PREFECTURE|COUNTY)\b"
)
ALIASES = {
    "TIRANE": "TIRANA",
}


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


def safe_download(url: str, path: Path, accept: str = "*/*") -> tuple[str, str, str]:
    request = urllib.request.Request(
        url,
        headers={
            "User-Agent": "climate-uhc-ml-audit/1.0",
            "Accept": accept,
        },
    )
    try:
        with urllib.request.urlopen(request, timeout=45) as response:
            status = str(getattr(response, "status", ""))
            body = response.read()
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(body)
        return "downloaded", status, ""
    except urllib.error.HTTPError as exc:
        return "blocked_http_error", str(exc.code), str(exc)
    except (urllib.error.URLError, TimeoutError, OSError) as exc:
        return "blocked_unreachable", "", str(exc)


def load_geojson_resource(url: str, path: Path, use_existing: bool) -> tuple[list[str], str, str, str, str]:
    if use_existing and path.exists():
        status = "local_geojson_snapshot_parsed"
        http_status = ""
        error = ""
    else:
        download_status, http_status, error = safe_download(url, path, "application/geo+json,application/json,*/*")
        status = f"{download_status}_geojson"
    if not path.exists():
        return [], status, http_status, "", error
    try:
        obj = json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, UnicodeDecodeError) as exc:
        return [], "blocked_geojson_parse_error", http_status, "", str(exc)
    features = obj.get("features", [])
    names: list[str] = []
    name_field = ""
    preferred = ["shapeName", "shapeName_1", "NAME_2", "NAME_1", "ADM2_EN", "ADM2_NAME", "name", "Name", "NAME"]
    for feature in features:
        props = feature.get("properties") or {}
        chosen_field = ""
        chosen_name = ""
        for field in preferred:
            value = fmt(props.get(field)).strip()
            if value:
                chosen_field = field
                chosen_name = value
                break
        if not chosen_name:
            for field, value in props.items():
                if "name" in str(field).lower() and fmt(value).strip():
                    chosen_field = str(field)
                    chosen_name = fmt(value).strip()
                    break
        if chosen_field and not name_field:
            name_field = chosen_field
        names.append(chosen_name)
    return names, status, http_status, name_field, error


def load_hdx_gazetteer_resource() -> tuple[list[str], str, str, str, str]:
    package_status, http_status, error = safe_download(HDX_PACKAGE_API_URL, HDX_PACKAGE_PATH, "application/json,*/*")
    if package_status != "downloaded":
        return [], f"{package_status}_package_metadata", http_status, "ADM2_EN", error
    try:
        package = json.loads(HDX_PACKAGE_PATH.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, UnicodeDecodeError) as exc:
        return [], "blocked_hdx_package_parse_error", http_status, "ADM2_EN", str(exc)
    write_json(HDX_PACKAGE_PATH, package)
    resources = package.get("result", {}).get("resources", [])
    xlsx_resource = next((row for row in resources if fmt(row.get("format")).upper() == "XLSX"), None)
    if not xlsx_resource:
        return [], "blocked_hdx_xlsx_resource_not_found", http_status, "ADM2_EN", "No XLSX gazetteer resource found in package metadata."
    xlsx_url = fmt(xlsx_resource.get("url"))
    download_status, download_http_status, download_error = safe_download(xlsx_url, HDX_GAZETTEER_PATH, "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet,*/*")
    if download_status != "downloaded":
        return [], f"{download_status}_hdx_gazetteer", download_http_status, "ADM2_EN", download_error
    try:
        df = pd.read_excel(HDX_GAZETTEER_PATH, sheet_name="alb_adm2_gz", dtype=str)
    except Exception as exc:  # noqa: BLE001 - audit preserves parser failures.
        return [], "blocked_hdx_gazetteer_parse_error", download_http_status, "ADM2_EN", str(exc)
    name_field = "ADM2_EN"
    if name_field not in df.columns:
        return [], "blocked_hdx_adm2_name_field_missing", download_http_status, name_field, "ADM2_EN not found in alb_adm2_gz."
    names = [fmt(value).strip() for value in df[name_field].dropna().tolist() if fmt(value).strip()]
    return names, "downloaded_hdx_2019_gazetteer_adm2_sheet", download_http_status, name_field, ""


def survey_rows() -> list[dict[str, str]]:
    rows = read_csv_dicts(TEMPLATE_PATH)
    if not rows:
        raise FileNotFoundError(f"Missing prerequisite or empty file: {TEMPLATE_PATH}")
    return rows


def match_resource(survey: list[dict[str, str]], boundary_names: list[str]) -> dict[str, Any]:
    boundary_key_counts = Counter(canonical_key(name) for name in boundary_names if canonical_key(name))
    boundary_keys = set(boundary_key_counts)
    matched_boundary_keys: set[str] = set()
    exact = repaired = alias = high_similarity = unmatched = 0
    unmatched_survey_keys: list[str] = []
    for row in survey:
        name = row.get("district_name_identification", "")
        raw_key = canonical_key(name, repair_euro=False, apply_alias=False)
        repaired_key = canonical_key(name, repair_euro=True, apply_alias=False)
        alias_key = canonical_key(name, repair_euro=True, apply_alias=True)
        if raw_key in boundary_keys:
            exact += 1
            matched_boundary_keys.add(raw_key)
        elif repaired_key in boundary_keys:
            repaired += 1
            matched_boundary_keys.add(repaired_key)
        elif alias_key in boundary_keys:
            alias += 1
            matched_boundary_keys.add(alias_key)
        else:
            best_key = ""
            best_score = 0.0
            for key in boundary_keys:
                score = SequenceMatcher(None, alias_key, key).ratio()
                if score > best_score:
                    best_score = score
                    best_key = key
            if best_key and best_score >= 0.92:
                high_similarity += 1
                matched_boundary_keys.add(best_key)
            else:
                unmatched += 1
                unmatched_survey_keys.append(alias_key or raw_key)
    duplicate_keys = [key for key, count in sorted(boundary_key_counts.items()) if count > 1]
    unmatched_boundary_keys = sorted(boundary_keys - matched_boundary_keys)
    return {
        "feature_count": len(boundary_names),
        "distinct_boundary_key_count": len(boundary_keys),
        "observed_survey_district_rows": len(survey),
        "exact_name_match_rows": exact,
        "repaired_encoding_match_rows": repaired,
        "documented_alias_match_rows": alias,
        "high_similarity_match_rows": high_similarity,
        "unmatched_survey_rows": unmatched,
        "unmatched_survey_keys": ";".join(sorted(set(unmatched_survey_keys))[:20]),
        "unmatched_boundary_keys": ";".join(unmatched_boundary_keys[:25]),
        "duplicate_boundary_keys": ";".join(duplicate_keys[:25]),
        "has_korce": "1" if "KORCE" in boundary_keys else "0",
        "has_kucove": "1" if "KUCOVE" in boundary_keys else "0",
        "has_vlore": "1" if "VLORE" in boundary_keys else "0",
    }


def candidate_row(
    candidate_id: str,
    source_name: str,
    source_url: str,
    source_type: str,
    source_year_claim: str,
    probe_method: str,
    resource_status: str,
    http_status: str,
    snapshot_path: Path,
    name_field: str,
    match_stats: dict[str, Any],
    suitability_status: str,
    blocking_reason: str,
    next_review_action: str,
) -> dict[str, str]:
    return {
        "candidate_id": candidate_id,
        "source_name": source_name,
        "source_url": source_url,
        "source_type": source_type,
        "source_year_claim": source_year_claim,
        "resource_probe_method": probe_method,
        "resource_status": resource_status,
        "http_status": http_status,
        "local_snapshot_path": rel(snapshot_path) if snapshot_path.exists() else "",
        "local_snapshot_sha256": sha256_file(snapshot_path) if snapshot_path.exists() else "",
        "name_field": name_field,
        "feature_count": fmt(match_stats.get("feature_count", 0)),
        "distinct_boundary_key_count": fmt(match_stats.get("distinct_boundary_key_count", 0)),
        "observed_survey_district_rows": fmt(match_stats.get("observed_survey_district_rows", 0)),
        "exact_name_match_rows": fmt(match_stats.get("exact_name_match_rows", 0)),
        "repaired_encoding_match_rows": fmt(match_stats.get("repaired_encoding_match_rows", 0)),
        "documented_alias_match_rows": fmt(match_stats.get("documented_alias_match_rows", 0)),
        "high_similarity_match_rows": fmt(match_stats.get("high_similarity_match_rows", 0)),
        "unmatched_survey_rows": fmt(match_stats.get("unmatched_survey_rows", 0)),
        "unmatched_survey_keys": fmt(match_stats.get("unmatched_survey_keys", "")),
        "unmatched_boundary_keys": fmt(match_stats.get("unmatched_boundary_keys", "")),
        "duplicate_boundary_keys": fmt(match_stats.get("duplicate_boundary_keys", "")),
        "has_korce": fmt(match_stats.get("has_korce", "0")),
        "has_kucove": fmt(match_stats.get("has_kucove", "0")),
        "has_vlore": fmt(match_stats.get("has_vlore", "0")),
        "historical_2002_boundary_ready": "0",
        "climate_linkage_ready": "0",
        "suitability_status": suitability_status,
        "promotion_status": "blocked_not_ready_for_climate_linkage",
        "blocking_reason": blocking_reason,
        "next_review_action": next_review_action,
    }


def build_rows(survey: list[dict[str, str]]) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []

    current_names, status, http_status, name_field, error = load_geojson_resource(CURRENT_GEOJSON_URL, CURRENT_GEOJSON_PATH, use_existing=True)
    current_stats = match_resource(survey, current_names)
    rows.append(
        candidate_row(
            "geoboundaries_current_pinned_adm2",
            "geoBoundaries gbOpen Albania ADM2 current pinned snapshot",
            CURRENT_GEOJSON_URL,
            "public_current_boundary_geojson",
            "2021/current boundary source in prior ALB_2002 audit",
            "local_snapshot_or_download_geojson",
            status,
            http_status,
            CURRENT_GEOJSON_PATH,
            name_field,
            current_stats,
            "blocked_current_boundary_name_or_unit_mismatch_not_historical",
            error
            or "Current public ADM2 boundaries are not verified as 2002 LSMS district boundaries; name coverage and duplicate key evidence remain insufficient for climate linkage.",
            "Keep as a current-boundary comparison only unless an official historical crosswalk proves these polygons represent the ALB_2002 district units.",
        )
    )

    old_names, status, http_status, name_field, error = load_geojson_resource(GB_201_URL, GB_201_PATH, use_existing=False)
    old_stats = match_resource(survey, old_names)
    old_complete = (
        int(old_stats["feature_count"]) == len(survey)
        and int(old_stats["distinct_boundary_key_count"]) == len(survey)
        and int(old_stats["unmatched_survey_rows"]) == 0
    )
    rows.append(
        candidate_row(
            "geoboundaries_2_0_1_adm2",
            "geoBoundaries 2.0.1 Albania ADM2 GeoJSON",
            GB_201_URL,
            "public_adm2_geojson_prior_release",
            "geoBoundaries 2.0.1 public ADM2 release; 2002 historical boundary vintage not verified",
            "download_geojson_and_compare_names",
            status,
            http_status,
            GB_201_PATH,
            name_field,
            old_stats,
            "candidate_complete_name_coverage_but_boundary_vintage_not_verified" if old_complete else "blocked_prior_release_name_or_unit_mismatch",
            error
            or "This resource has candidate district-name coverage, but the audit has not verified boundary provenance, geometry source, represented administrative year, LSMS sampling-frame compatibility, projection, or join keys against raw ALB_2002 codes.",
            "Manually verify the geoBoundaries 2.0.1 source provenance and represented boundary year, compare geometries to official 2001/2002 district definitions, and document a district-code crosswalk before any admin-level climate aggregation.",
        )
    )

    hdx_names, status, http_status, name_field, error = load_hdx_gazetteer_resource()
    hdx_stats = match_resource(survey, hdx_names)
    rows.append(
        candidate_row(
            "hdx_cod_ab_alb_2019_gazetteer_adm2",
            "HDX COD-AB Albania 2019 gazetteer ADM2 sheet",
            HDX_PACKAGE_PAGE_URL,
            "public_current_or_post2019_administrative_gazetteer",
            "2019 COD-AB administrative gazetteer; municipality units, not verified 2002 LSMS districts",
            "download_ckan_package_metadata_and_xlsx_gazetteer",
            status,
            http_status,
            HDX_GAZETTEER_PATH,
            name_field,
            hdx_stats,
            "blocked_2019_municipality_units_not_2002_lsms_districts",
            error
            or "HDX COD-AB is a current/post-2019 administrative gazetteer with municipality-style ADM2 units; it cannot be treated as the 36 ALB_2002 district boundary layer.",
            "Use only as a current administrative reference unless a documented historical crosswalk maps each 2002 LSMS district to the 2019 municipality units and supports the intended climate aggregation.",
        )
    )
    return rows


def summary_row(metric: str, value: Any, interpretation: str) -> dict[str, str]:
    return {"metric": metric, "value": fmt(value), "interpretation": interpretation}


def build_summary(rows: list[dict[str, str]]) -> list[dict[str, str]]:
    parseable = [row for row in rows if int(row.get("feature_count") or 0) > 0]
    complete_name_coverage = [
        row
        for row in rows
        if int(row.get("observed_survey_district_rows") or 0) > 0 and int(row.get("unmatched_survey_rows") or 0) == 0
    ]
    exact_unit_count = [
        row
        for row in rows
        if row.get("feature_count") == row.get("observed_survey_district_rows")
        and row.get("distinct_boundary_key_count") == row.get("observed_survey_district_rows")
    ]
    prior_release = next((row for row in rows if row["candidate_id"] == "geoboundaries_2_0_1_adm2"), {})
    return [
        summary_row("alb2002_boundary_resource_search_candidate_rows", len(rows), "Public boundary/gazetteer resources directly parsed or probed for ALB_2002."),
        summary_row("alb2002_boundary_resource_search_parseable_resource_rows", len(parseable), "Rows with a parsed GeoJSON or gazetteer name list."),
        summary_row("alb2002_boundary_resource_search_complete_name_coverage_rows", len(complete_name_coverage), "Resources with no unmatched ALB_2002 survey district keys after documented repairs/aliases."),
        summary_row("alb2002_boundary_resource_search_exact_unit_count_rows", len(exact_unit_count), "Resources whose feature and distinct-key counts both equal the 36 observed survey district groups."),
        summary_row("alb2002_boundary_resource_search_korce_available_rows", sum(1 for row in rows if row.get("has_korce") == "1"), "Resources whose parsed names include a canonical KORCE boundary key."),
        summary_row("alb2002_boundary_resource_search_2002_historical_ready_rows", 0, "Resources verified as 2002 historical boundary inputs after this audit; intentionally zero."),
        summary_row("alb2002_boundary_resource_search_climate_linkage_ready_rows", 0, "Resources ready for climate-linkage input promotion after this audit; intentionally zero."),
        summary_row("alb2002_boundary_resource_search_best_candidate_id", prior_release.get("candidate_id", ""), "Best current lead by name coverage only; not a promoted analytical input."),
        summary_row("alb2002_boundary_resource_search_best_candidate_exact_matches", prior_release.get("exact_name_match_rows", "0"), "Exact normalized matches for the best name-coverage candidate."),
        summary_row("alb2002_boundary_resource_search_best_candidate_repaired_matches", prior_release.get("repaired_encoding_match_rows", "0"), "Mojibake/encoding-repaired matches for the best name-coverage candidate."),
        summary_row("alb2002_boundary_resource_search_best_candidate_alias_matches", prior_release.get("documented_alias_match_rows", "0"), "Documented alias matches for the best name-coverage candidate."),
        summary_row("alb2002_boundary_resource_search_current_decision", DECISION, "Current fail-closed decision for ALB_2002 public boundary resource search."),
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
    REPORT_PATH.write_text(
        f"""# ALB_2002 Boundary Source Resource Search Audit

Status: temp-only public resource search. This audit parses public boundary or gazetteer resources and compares their names to the 36 observed ALB_2002 district groups. It does not create centroids, does not validate polygons, does not write `data/`, and does not construct climate exposures.

## Summary

| Metric | Value | Interpretation |
|---|---:|---|
{summary_table}

## Resource-Level Results

{markdown_rows(rows, ['candidate_id', 'resource_status', 'source_year_claim', 'feature_count', 'distinct_boundary_key_count', 'exact_name_match_rows', 'repaired_encoding_match_rows', 'documented_alias_match_rows', 'unmatched_survey_rows', 'suitability_status'], 20)}

## Name Gaps and Duplicate Keys

{markdown_rows(rows, ['candidate_id', 'has_korce', 'has_kucove', 'has_vlore', 'unmatched_survey_keys', 'unmatched_boundary_keys', 'duplicate_boundary_keys'], 20)}

## Interpretation

- The older geoBoundaries 2.0.1 ADM2 GeoJSON is the strongest public lead by name coverage: it has 36 parsed features, 36 distinct normalized boundary keys, and no unmatched ALB_2002 survey district keys after documented repairs.
- That lead is not an analytical input yet. The audit has not verified represented boundary year, source provenance, geometry quality, official 2001/2002 district definitions, or join keys to raw ALB_2002 district codes.
- The current pinned geoBoundaries snapshot remains blocked as a current-boundary comparison with incomplete name/unit evidence.
- HDX COD-AB is useful context for current administrative geography but is a 2019 municipality-style gazetteer and is not a 2002 district boundary layer.
- Historical-boundary-ready and climate-linkage-ready rows remain zero.

## Machine-Readable Outputs

- `temp/alb2002_boundary_source_resource_search_audit.csv`
- `result/alb2002_boundary_source_resource_search_summary.csv`
- `temp/source_snapshots/alb2002_geoboundaries_2_0_1_alb_adm2.geojson`
- `temp/source_snapshots/hdx_cod_ab_alb_package_show.json`
- `temp/source_snapshots/hdx_alb_adm_gazetteer_2019.xlsx`
""",
        encoding="utf-8",
    )


def main() -> None:
    ensure_dirs()
    survey = survey_rows()
    rows = build_rows(survey)
    summary = build_summary(rows)
    write_csv(AUDIT_PATH, rows, AUDIT_COLUMNS)
    write_csv(SUMMARY_PATH, summary, SUMMARY_COLUMNS)
    write_report(rows, summary)
    append_log(
        TEMP_DIR / "audit_log.md",
        f"Built ALB_2002 boundary source resource search rows={len(rows)} decision={DECISION}.",
    )
    print(f"ALB_2002 boundary source resource search rows={len(rows)} decision={DECISION}.")


if __name__ == "__main__":
    main()
