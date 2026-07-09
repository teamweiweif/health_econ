from __future__ import annotations

import json
import math
import unicodedata
import urllib.error
import urllib.request
from typing import Any

import pandas as pd

from common import REPORT_DIR, RESULT_DIR, TEMP_DIR, append_log, ensure_dirs, write_csv, write_json


CORE_PATH = TEMP_DIR / "alb2002_household_core_candidate.csv"
TEMPLATE_PATH = TEMP_DIR / "alb2002_district_climate_crosswalk_template.csv"
SOURCE_PROBE_PATH = TEMP_DIR / "alb2002_district_boundary_source_probe.csv"
SUMMARY_PATH = RESULT_DIR / "alb2002_district_climate_crosswalk_summary.csv"
REPORT_PATH = REPORT_DIR / "alb2002_district_climate_crosswalk_audit.md"
API_SNAPSHOT_PATH = TEMP_DIR / "alb2002_geoboundaries_adm2_api.json"

GEOB_API_URL = "https://www.geoboundaries.org/api/current/gbOpen/ALB/ADM2/"
DECISION = "blocked_boundary_crosswalk_not_verified_no_gps"

TEMPLATE_COLUMNS = [
    "country",
    "survey_name",
    "wave",
    "idno",
    "district_code_identification",
    "district_name_identification",
    "district_name_review_key",
    "household_rows",
    "weighted_households",
    "psu_count",
    "enumerator_area_count",
    "survey_month_values",
    "interview_date_min",
    "interview_date_max",
    "district_code_weight_values",
    "district_name_weight_values",
    "geolocation_quality_values",
    "boundary_candidate_source",
    "boundary_candidate_adm_level",
    "boundary_candidate_year_represented",
    "boundary_candidate_unit_count",
    "boundary_candidate_download_url",
    "district_count_matches_boundary_count",
    "name_encoding_review_flag",
    "crosswalk_status",
    "blocking_reason",
]
SOURCE_COLUMNS = [
    "source_name",
    "source_url",
    "probe_method",
    "probe_status",
    "http_status",
    "boundary_id",
    "boundary_type",
    "boundary_year_represented",
    "boundary_canonical",
    "adm_unit_count",
    "download_url",
    "license",
    "snapshot_path",
    "review_status",
    "detail",
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


def rel(path: Any) -> str:
    path = path if hasattr(path, "relative_to") else None
    if path is None:
        return ""
    try:
        return str(path.relative_to(TEMP_DIR.parent)).replace("\\", "/")
    except ValueError:
        return str(path).replace("\\", "/")


def normalize_name(value: Any) -> str:
    text = fmt(value).strip().upper()
    normalized = unicodedata.normalize("NFKD", text)
    ascii_text = normalized.encode("ascii", "ignore").decode("ascii")
    cleaned = "".join(ch if ch.isalnum() else " " for ch in ascii_text)
    return " ".join(cleaned.split())


def has_non_ascii(value: Any) -> bool:
    text = fmt(value)
    return any(ord(ch) > 127 for ch in text)


def unique_join(series: pd.Series, limit: int = 20) -> str:
    out: list[str] = []
    seen: set[str] = set()
    for value in series:
        clean = fmt(value).strip()
        if not clean or clean.lower() == "nan" or clean in seen:
            continue
        out.append(clean)
        seen.add(clean)
        if len(out) >= limit:
            break
    return ";".join(out)


def fetch_json(url: str) -> tuple[dict[str, Any] | None, str, str, str]:
    request = urllib.request.Request(url, headers={"User-Agent": "climate-uhc-ml-audit/1.0"})
    try:
        with urllib.request.urlopen(request, timeout=20) as response:
            status = getattr(response, "status", "")
            body = response.read().decode("utf-8")
        return json.loads(body), "reachable_metadata_saved", str(status), ""
    except urllib.error.HTTPError as exc:
        return None, "blocked_source_http_error", str(exc.code), str(exc)
    except (urllib.error.URLError, TimeoutError, json.JSONDecodeError) as exc:
        return None, "blocked_source_unreachable_or_unparseable", "", str(exc)


def probe_boundary_source() -> tuple[list[dict[str, str]], dict[str, Any]]:
    data, status, http_status, error = fetch_json(GEOB_API_URL)
    if data is not None:
        write_json(API_SNAPSHOT_PATH, data)
    meta = data or {}
    row = {
        "source_name": "geoBoundaries gbOpen Albania ADM2 current API",
        "source_url": GEOB_API_URL,
        "probe_method": "GET_json_metadata_only_no_polygon_download",
        "probe_status": status,
        "http_status": http_status,
        "boundary_id": fmt(meta.get("boundaryID")),
        "boundary_type": fmt(meta.get("boundaryType")),
        "boundary_year_represented": fmt(meta.get("boundaryYearRepresented")),
        "boundary_canonical": fmt(meta.get("boundaryCanonical")),
        "adm_unit_count": fmt(meta.get("admUnitCount")),
        "download_url": fmt(meta.get("gjDownloadURL") or meta.get("staticDownloadLink")),
        "license": fmt(meta.get("boundaryLicense")),
        "snapshot_path": rel(API_SNAPSHOT_PATH) if data is not None else "",
        "review_status": "candidate_boundary_metadata_only_not_crosswalk_verified",
        "detail": error or "Public boundary metadata reached; polygons and names were not downloaded or matched.",
    }
    return [row], meta


def source_unit_count(meta: dict[str, Any]) -> int | None:
    try:
        return int(float(str(meta.get("admUnitCount", "")).strip()))
    except (TypeError, ValueError):
        return None


def build_template(df: pd.DataFrame, meta: dict[str, Any]) -> list[dict[str, str]]:
    required = {"district_code_identification", "district_name_identification", "survey_month", "interview_date"}
    missing = sorted(required - set(df.columns))
    if missing:
        raise ValueError(f"Missing required ALB_2002 district/timing columns: {', '.join(missing)}")

    work = df.copy()
    work["district_code_key"] = work["district_code_identification"].map(fmt)
    work["district_name_key"] = work["district_name_identification"].map(fmt)
    unit_count = source_unit_count(meta)
    district_count = int(work[["district_code_key", "district_name_key"]].drop_duplicates().shape[0])
    count_match = "1" if unit_count is not None and unit_count == district_count else "0"
    if unit_count is None:
        status = "blocked_public_boundary_metadata_unreachable"
        reason = "No parsed public boundary unit count; cannot validate district crosswalk."
    elif count_match == "0":
        status = "blocked_boundary_unit_count_mismatch_unverified"
        reason = (
            f"ALB_2002 has {district_count} observed district groups, but the probed ADM2 boundary metadata reports "
            f"{unit_count} units; historical district definitions and polygons must be manually verified."
        )
    else:
        status = "blocked_boundary_polygons_not_downloaded_names_unverified"
        reason = "Boundary metadata unit count matches, but polygons, name fields, historical validity, and survey coding are not verified."

    rows: list[dict[str, str]] = []
    group_cols = ["district_code_key", "district_name_key"]
    for (_, _), group in work.groupby(group_cols, dropna=False, sort=True):
        weight = pd.to_numeric(group.get("household_weight", pd.Series(dtype=float)), errors="coerce")
        dates = pd.to_datetime(group["interview_date"], errors="coerce")
        district_name = fmt(group["district_name_identification"].iloc[0])
        rows.append(
            {
                "country": "Albania",
                "survey_name": "Living Standards Measurement Survey 2002",
                "wave": "2002",
                "idno": "ALB_2002_LSMS_v01_M",
                "district_code_identification": fmt(group["district_code_identification"].iloc[0]),
                "district_name_identification": district_name,
                "district_name_review_key": normalize_name(district_name),
                "household_rows": str(len(group)),
                "weighted_households": fmt(float(weight.sum(skipna=True))) if not weight.empty else "",
                "psu_count": str(group["psu"].astype(str).nunique(dropna=True)) if "psu" in group.columns else "",
                "enumerator_area_count": str(group["enumerator_area"].astype(str).nunique(dropna=True)) if "enumerator_area" in group.columns else "",
                "survey_month_values": unique_join(group["survey_month"]),
                "interview_date_min": dates.min().strftime("%Y-%m-%d") if dates.notna().any() else "",
                "interview_date_max": dates.max().strftime("%Y-%m-%d") if dates.notna().any() else "",
                "district_code_weight_values": unique_join(group["district_code_weight"]) if "district_code_weight" in group.columns else "",
                "district_name_weight_values": unique_join(group["district_name_weight"]) if "district_name_weight" in group.columns else "",
                "geolocation_quality_values": unique_join(group["geolocation_quality"]) if "geolocation_quality" in group.columns else "",
                "boundary_candidate_source": "geoBoundaries gbOpen Albania ADM2 current API" if meta else "",
                "boundary_candidate_adm_level": fmt(meta.get("boundaryType")),
                "boundary_candidate_year_represented": fmt(meta.get("boundaryYearRepresented")),
                "boundary_candidate_unit_count": str(unit_count) if unit_count is not None else "",
                "boundary_candidate_download_url": fmt(meta.get("gjDownloadURL") or meta.get("staticDownloadLink")),
                "district_count_matches_boundary_count": count_match,
                "name_encoding_review_flag": "1" if has_non_ascii(district_name) else "0",
                "crosswalk_status": status,
                "blocking_reason": reason + " No household or cluster GPS is present in the ALB_2002 candidate.",
            }
        )
    return rows


def summary_row(metric: str, value: Any, interpretation: str) -> dict[str, str]:
    return {"metric": metric, "value": fmt(value), "interpretation": interpretation}


def build_summary(df: pd.DataFrame, template: list[dict[str, str]], source_rows: list[dict[str, str]]) -> list[dict[str, str]]:
    district_code = pd.to_numeric(df["district_code_identification"], errors="coerce")
    survey_month = pd.to_numeric(df["survey_month"], errors="coerce")
    interview_date = df["interview_date"].astype(str)
    reachable_sources = sum(1 for row in source_rows if row["probe_status"] == "reachable_metadata_saved")
    unit_match_rows = sum(1 for row in template if row["district_count_matches_boundary_count"] == "1")
    source_unit = next((row["adm_unit_count"] for row in source_rows if row.get("adm_unit_count")), "")
    return [
        summary_row("alb2002_district_crosswalk_household_rows", len(df), "Rows in temp/alb2002_household_core_candidate.csv."),
        summary_row("alb2002_district_crosswalk_households_with_district", int(district_code.notna().sum()), "Households with observed ALB_2002 district code."),
        summary_row("alb2002_district_crosswalk_district_rows", len(template), "Observed district code/name groups in the crosswalk template."),
        summary_row("alb2002_district_crosswalk_survey_month_rows", int(survey_month.notna().sum()), "Households with raw survey month for climate windows."),
        summary_row("alb2002_district_crosswalk_interview_date_rows", int(interview_date.str.len().gt(0).sum()), "Households with constructed interview date for climate windows."),
        summary_row("alb2002_district_crosswalk_name_encoding_review_rows", sum(1 for row in template if row["name_encoding_review_flag"] == "1"), "District names with non-ASCII characters requiring raw-label encoding review."),
        summary_row("alb2002_district_crosswalk_boundary_source_rows", len(source_rows), "Public boundary metadata sources probed."),
        summary_row("alb2002_district_crosswalk_boundary_source_reachable_rows", reachable_sources, "Public boundary metadata sources reachable and saved."),
        summary_row("alb2002_district_crosswalk_boundary_source_adm_unit_count", source_unit, "ADM unit count reported by the probed public boundary source."),
        summary_row("alb2002_district_crosswalk_boundary_unit_count_match_rows", unit_match_rows, "Template district rows where observed district count matches boundary unit count."),
        summary_row("alb2002_district_crosswalk_template_ready_rows", 0, "Rows ready for crosswalk or data promotion after this audit."),
        summary_row("alb2002_climate_linkage_ready_rows", 0, "ALB_2002 rows ready for climate-linkage input promotion after this audit."),
        summary_row("alb2002_district_crosswalk_current_decision", DECISION, "Current fail-closed decision for ALB_2002 district climate crosswalk readiness."),
    ]


def markdown_rows(rows: list[dict[str, str]], columns: list[str], limit: int = 20) -> str:
    lines = ["| " + " | ".join(columns) + " |", "|" + "|".join("---" for _ in columns) + "|"]
    for row in rows[:limit]:
        values = []
        for column in columns:
            value = (row.get(column, "") or "").replace("|", "/")
            if len(value) > 110:
                value = value[:107] + "..."
            values.append(value)
        lines.append("| " + " | ".join(values) + " |")
    return "\n".join(lines)


def write_report(template: list[dict[str, str]], source_rows: list[dict[str, str]], summary: list[dict[str, str]]) -> None:
    summary_table = "\n".join(f"| {row['metric']} | {row['value']} | {row['interpretation']} |" for row in summary)
    REPORT_PATH.write_text(
        f"""# ALB_2002 District Climate Crosswalk Audit

Status: temp-only boundary-readiness audit. This audit builds an ALB_2002 district crosswalk template and probes public ADM2 boundary metadata. It does not download polygons, does not geocode, does not assign centroids, does not write `data/climate_linkage_input.csv`, and does not construct climate exposures.

## Summary

| Metric | Value | Interpretation |
|---|---:|---|
{summary_table}

## Public Boundary Metadata Probe

{markdown_rows(source_rows, ['source_name', 'probe_status', 'boundary_type', 'boundary_year_represented', 'boundary_canonical', 'adm_unit_count', 'review_status'], 10)}

## District Template Preview

{markdown_rows(template, ['district_code_identification', 'district_name_identification', 'household_rows', 'survey_month_values', 'interview_date_min', 'interview_date_max', 'crosswalk_status'], 40)}

## Interpretation

- ALB_2002 has observed district code/name groups plus survey month and interview date fields, which is useful for future admin-level climate windows.
- The probed public boundary metadata is candidate evidence only. It is not a verified survey-to-boundary crosswalk.
- The current metadata reports an ADM2 unit count that must be reconciled against the 36 observed ALB_2002 district groups before any aggregation.
- District names also need raw-label/encoding review before matching, because some labels contain non-ASCII or mojibake-like characters.
- No household or cluster GPS is available in the candidate, so any future climate linkage would be admin-level and must report measurement error.
- Climate-linkage-ready rows remain zero.

## Machine-Readable Outputs

- `temp/alb2002_district_climate_crosswalk_template.csv`
- `temp/alb2002_district_boundary_source_probe.csv`
- `temp/alb2002_geoboundaries_adm2_api.json` when the public API is reachable
- `result/alb2002_district_climate_crosswalk_summary.csv`
""",
        encoding="utf-8",
    )


def main() -> None:
    ensure_dirs()
    if not CORE_PATH.exists():
        raise FileNotFoundError(f"Missing prerequisite: {CORE_PATH}")
    df = pd.read_csv(CORE_PATH, encoding="utf-8-sig")
    source_rows, meta = probe_boundary_source()
    template = build_template(df, meta)
    summary = build_summary(df, template, source_rows)
    write_csv(TEMPLATE_PATH, template, TEMPLATE_COLUMNS)
    write_csv(SOURCE_PROBE_PATH, source_rows, SOURCE_COLUMNS)
    write_csv(SUMMARY_PATH, summary, SUMMARY_COLUMNS)
    write_report(template, source_rows, summary)
    append_log(
        TEMP_DIR / "audit_log.md",
        f"Built ALB_2002 district climate crosswalk audit rows={len(template)} decision={DECISION}.",
    )
    print(f"ALB_2002 district climate crosswalk audit rows={len(template)} decision={DECISION}.")


if __name__ == "__main__":
    main()
