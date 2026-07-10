from __future__ import annotations

import json
import os
import tempfile
from pathlib import Path, PurePosixPath
from typing import Any
from zipfile import ZipFile

import pandas as pd
import pyreadstat

from common import REPORT_DIR, RESULT_DIR, TEMP_DIR, append_log, ensure_dirs, sha256_file, write_csv


IDNO = "MWI_2004_IHS-II_v01_M"
COUNTRY = "Malawi"
WAVE = "2004-2005"
RAW_DIR = TEMP_DIR / "raw_downloads" / IDNO
ZIP_PATH = RAW_DIR / "MWI_2004_IHS-II_v01_M_Stata8.zip"
BOUNDARY_DIR = TEMP_DIR / "raw_downloads" / "climate_boundaries"
BOUNDARY_PATH = BOUNDARY_DIR / "geoBoundaries-MWI-ADM2.geojson"

CHIRPS_DOC_URL = "https://www.chc.ucsb.edu/data/chirps"
CHIRPS_MONTHLY_TIF_BASE = "https://data.chc.ucsb.edu/products/CHIRPS-2.0/africa_monthly/tifs"
GEOB_API_URL = "https://www.geoboundaries.org/api/current/gbOpen/MWI/ADM2/"
GEOB_ADM2_GEOJSON_URL = (
    "https://github.com/wmgeolab/geoBoundaries/raw/9469f09/"
    "releaseData/gbOpen/MWI/ADM2/geoBoundaries-MWI-ADM2.geojson"
)

POLICY_PATH = RESULT_DIR / "mwi2004_chirps_admin2_route_policy.csv"
CROSSWALK_PATH = RESULT_DIR / "mwi2004_chirps_admin2_crosswalk.csv"
DOWNLOADS_PATH = RESULT_DIR / "mwi2004_chirps_admin2_required_downloads.csv"
SUMMARY_PATH = RESULT_DIR / "mwi2004_chirps_admin2_route_policy_summary.csv"
REPORT_PATH = REPORT_DIR / "mwi2004_chirps_admin2_route_policy.md"
HANDOFF_PATH = RAW_DIR / "_MWI2004_CHIRPS_ADMIN2_ROUTE_POLICY.md"

POLICY_COLUMNS = [
    "country",
    "wave",
    "idno",
    "policy_component",
    "route_decision",
    "source_or_input",
    "verified_evidence",
    "route_status",
    "next_action",
    "data_write_gate_effect",
]
CROSSWALK_COLUMNS = [
    "country",
    "wave",
    "idno",
    "raw_dist_code",
    "raw_dist_label",
    "normalized_adm2_name",
    "household_rows",
    "interview_month_count",
    "interview_month_min",
    "interview_month_max",
    "boundary_match_status",
    "boundary_source",
    "route_role",
]
DOWNLOAD_COLUMNS = [
    "country",
    "wave",
    "idno",
    "source",
    "chirps_month",
    "chirps_file",
    "url",
    "required_for_lag_windows",
    "local_target_path",
    "download_status",
    "notes",
]
SUMMARY_COLUMNS = ["metric", "value", "interpretation"]


def clean(value: Any) -> str:
    if value is None:
        return ""
    return " ".join(str(value).split())


def member_name(zip_path: Path, basename: str) -> str:
    with ZipFile(zip_path) as zf:
        for name in zf.namelist():
            if PurePosixPath(name).name.lower() == basename.lower():
                return name
    raise FileNotFoundError(f"{basename} not found in {zip_path}")


def read_member(zip_path: Path, basename: str, columns: list[str], apply_value_formats: bool) -> tuple[pd.DataFrame, Any]:
    member = member_name(zip_path, basename)
    with ZipFile(zip_path) as zf:
        payload = zf.read(member)
    fd, raw_name = tempfile.mkstemp(suffix=PurePosixPath(member).suffix or ".dta")
    raw_path = Path(raw_name)
    try:
        with os.fdopen(fd, "wb") as f:
            f.write(payload)
        _, meta = pyreadstat.read_dta(str(raw_path), metadataonly=True)
        available = set(getattr(meta, "column_names", []) or [])
        usecols = [column for column in columns if column in available]
        return pyreadstat.read_dta(str(raw_path), apply_value_formats=apply_value_formats, usecols=usecols)
    finally:
        raw_path.unlink(missing_ok=True)


def normalize_adm2_name(value: Any) -> str:
    text = clean(value)
    if "/" in text:
        text = text.split("/", 1)[0]
    return text.strip()


def boundary_names(path: Path) -> list[str]:
    obj = json.loads(path.read_text(encoding="utf-8"))
    names = []
    for feature in obj.get("features", []):
        props = feature.get("properties", {})
        name = clean(props.get("shapeName"))
        if name:
            names.append(name)
    return sorted(set(names))


def date_months(series: pd.Series) -> pd.Series:
    numeric = pd.to_numeric(series, errors="coerce")
    converted = pd.to_datetime(numeric, unit="D", origin="1960-01-01", errors="coerce")
    return converted.dt.to_period("M")


def period_text(period: pd.Period | Any) -> str:
    if isinstance(period, pd.Period):
        return f"{period.year:04d}-{period.month:02d}"
    return clean(period)


def lag_window_months(interview_months: list[pd.Period]) -> dict[pd.Period, set[str]]:
    required: dict[pd.Period, set[str]] = {}
    for interview_month in interview_months:
        for lag in [1, 3, 6, 12]:
            start = interview_month - lag
            end = interview_month - 1
            for month in pd.period_range(start=start, end=end, freq="M"):
                required.setdefault(month, set()).add(f"interview={period_text(interview_month)};lag={lag}m")
    return required


def markdown_table(rows: list[dict[str, str]], columns: list[str], limit: int = 25) -> str:
    if not rows:
        return "_No rows._"
    lines = ["| " + " | ".join(columns) + " |", "| " + " | ".join("---" for _ in columns) + " |"]
    for row in rows[:limit]:
        lines.append("| " + " | ".join(clean(row.get(column)).replace("|", "/") for column in columns) + " |")
    if len(rows) > limit:
        lines.append("| " + " | ".join("..." for _ in columns) + " |")
    return "\n".join(lines)


def build_crosswalk(household: pd.DataFrame, household_labels: pd.DataFrame, boundary: list[str]) -> tuple[list[dict[str, str]], dict[str, str]]:
    month_series = date_months(household["idate"])
    work = household[["dist"]].copy()
    work["dist_label"] = household_labels["dist"].astype(str)
    work["interview_month"] = month_series.astype(str)
    boundary_by_key = {name.casefold(): name for name in boundary}

    rows: list[dict[str, str]] = []
    grouped = work.groupby(["dist", "dist_label"], dropna=False)
    matched_names: set[str] = set()
    for (code, label), group in grouped:
        norm = normalize_adm2_name(label)
        boundary_name = boundary_by_key.get(norm.casefold(), "")
        if boundary_name:
            matched_names.add(boundary_name)
        valid_months = sorted(month for month in group["interview_month"].dropna().unique() if month and month != "NaT")
        rows.append(
            {
                "country": COUNTRY,
                "wave": WAVE,
                "idno": IDNO,
                "raw_dist_code": str(int(code)) if pd.notna(code) else "",
                "raw_dist_label": clean(label),
                "normalized_adm2_name": boundary_name or norm,
                "household_rows": str(len(group)),
                "interview_month_count": str(len(valid_months)),
                "interview_month_min": valid_months[0] if valid_months else "",
                "interview_month_max": valid_months[-1] if valid_months else "",
                "boundary_match_status": "matched_to_geoboundaries_adm2" if boundary_name else "unmatched_boundary_name",
                "boundary_source": "geoBoundaries gbOpen MWI ADM2 2020, source National Statistics Office of Malawi and OCHA ROSEA",
                "route_role": "sampled_raw_district",
            }
        )

    for boundary_name in sorted(set(boundary) - matched_names):
        rows.append(
            {
                "country": COUNTRY,
                "wave": WAVE,
                "idno": IDNO,
                "raw_dist_code": "",
                "raw_dist_label": "",
                "normalized_adm2_name": boundary_name,
                "household_rows": "0",
                "interview_month_count": "0",
                "interview_month_min": "",
                "interview_month_max": "",
                "boundary_match_status": "boundary_present_no_raw_sample",
                "boundary_source": "geoBoundaries gbOpen MWI ADM2 2020, source National Statistics Office of Malawi and OCHA ROSEA",
                "route_role": "unsampled_boundary_district",
            }
        )

    counts = {
        "raw_district_rows": str(sum(1 for row in rows if row["route_role"] == "sampled_raw_district")),
        "boundary_features": str(len(boundary)),
        "raw_district_boundary_matches": str(sum(1 for row in rows if row["boundary_match_status"] == "matched_to_geoboundaries_adm2")),
        "raw_district_boundary_unmatched": str(sum(1 for row in rows if row["boundary_match_status"] == "unmatched_boundary_name")),
        "boundary_no_sample_rows": str(sum(1 for row in rows if row["boundary_match_status"] == "boundary_present_no_raw_sample")),
        "boundary_no_sample_names": ";".join(row["normalized_adm2_name"] for row in rows if row["boundary_match_status"] == "boundary_present_no_raw_sample"),
    }
    return rows, counts


def build_download_manifest(interview_months: list[pd.Period]) -> list[dict[str, str]]:
    required = lag_window_months(interview_months)
    rows: list[dict[str, str]] = []
    for month in sorted(required):
        file_name = f"chirps-v2.0.{month.year:04d}.{month.month:02d}.tif.gz"
        rows.append(
            {
                "country": COUNTRY,
                "wave": WAVE,
                "idno": IDNO,
                "source": "CHIRPS v2.0 Africa monthly GeoTIFF",
                "chirps_month": period_text(month),
                "chirps_file": file_name,
                "url": f"{CHIRPS_MONTHLY_TIF_BASE}/{file_name}",
                "required_for_lag_windows": ";".join(sorted(required[month])),
                "local_target_path": f"temp/raw_downloads/climate_chirps/africa_monthly/{file_name}",
                "download_status": "not_downloaded_source_url_verified",
                "notes": "Needed for 1, 3, 6, and 12 complete-month rainfall windows before Malawi 2004 interview month.",
            }
        )
    return rows


def build_outputs() -> tuple[list[dict[str, str]], list[dict[str, str]], list[dict[str, str]], list[dict[str, str]]]:
    if not ZIP_PATH.exists():
        raise FileNotFoundError(f"Missing raw package: {ZIP_PATH}")
    if not BOUNDARY_PATH.exists():
        raise FileNotFoundError(
            f"Missing boundary file: {BOUNDARY_PATH}. Download from {GEOB_ADM2_GEOJSON_URL} before running this script."
        )

    household, _ = read_member(ZIP_PATH, "ihs2_household.dta", ["dist", "idate"], apply_value_formats=False)
    household_labels, _ = read_member(ZIP_PATH, "ihs2_household.dta", ["dist"], apply_value_formats=True)
    months = sorted(period for period in date_months(household["idate"]).dropna().unique())
    boundary = boundary_names(BOUNDARY_PATH)

    crosswalk_rows, counts = build_crosswalk(household, household_labels, boundary)
    download_rows = build_download_manifest(months)
    route_design_ready = counts["raw_district_boundary_unmatched"] == "0" and bool(download_rows)
    status = (
        "chirps_admin2_district_month_route_design_ready_extraction_validation_pending"
        if route_design_ready
        else "chirps_admin2_route_design_blocked_crosswalk_or_download_manifest"
    )

    policy_rows = [
        {
            "country": COUNTRY,
            "wave": WAVE,
            "idno": IDNO,
            "policy_component": "rainfall_source",
            "route_decision": "select_chirps_v2_africa_monthly_geotiff_for_precipitation",
            "source_or_input": CHIRPS_MONTHLY_TIF_BASE,
            "verified_evidence": "Official CHC page describes CHIRPS as 0.05 degree gridded rainfall from 1981 to near-present; monthly Africa GeoTIFF directory exposes required 2003-03 through 2005-02 files.",
            "route_status": "source_route_selected",
            "next_action": "Download listed monthly GeoTIFF files into temp/raw_downloads/climate_chirps/africa_monthly and compute checksums.",
            "data_write_gate_effect": "does_not_open_data_gate",
        },
        {
            "country": COUNTRY,
            "wave": WAVE,
            "idno": IDNO,
            "policy_component": "spatial_boundary_source",
            "route_decision": "use_geoboundaries_mwi_adm2_as_district_boundary_candidate",
            "source_or_input": GEOB_API_URL,
            "verified_evidence": f"Local boundary file present with {len(boundary)} ADM2 features; sha256={sha256_file(BOUNDARY_PATH)}.",
            "route_status": "boundary_file_cached_for_local_validation",
            "next_action": "Run zonal or raster extraction once geospatial dependencies and CHIRPS GeoTIFFs are available.",
            "data_write_gate_effect": "does_not_open_data_gate",
        },
        {
            "country": COUNTRY,
            "wave": WAVE,
            "idno": IDNO,
            "policy_component": "raw_district_crosswalk",
            "route_decision": "map_raw_dist_labels_to_adm2_district_names_after_city_suffix_normalization",
            "source_or_input": "ihs2_household.dist labels and geoBoundaries ADM2 shapeName",
            "verified_evidence": f"raw_districts={counts['raw_district_rows']}; matches={counts['raw_district_boundary_matches']}; unmatched={counts['raw_district_boundary_unmatched']}; unsampled_boundaries={counts['boundary_no_sample_names']}.",
            "route_status": "crosswalk_ready" if counts["raw_district_boundary_unmatched"] == "0" else "crosswalk_blocked_unmatched_names",
            "next_action": "Keep city/district combined labels assigned to parent district; keep Likoma and Neno as boundary districts with no sampled households.",
            "data_write_gate_effect": "does_not_open_data_gate",
        },
        {
            "country": COUNTRY,
            "wave": WAVE,
            "idno": IDNO,
            "policy_component": "temporal_window_plan",
            "route_decision": "use_1_3_6_12_complete_month_windows_before_interview_month",
            "source_or_input": "ihs2_household.idate and CHIRPS monthly files",
            "verified_evidence": f"interview_months={len(months)}; chirps_required_months={len(download_rows)}; first={download_rows[0]['chirps_month']}; last={download_rows[-1]['chirps_month']}.",
            "route_status": "download_manifest_ready",
            "next_action": "After CHIRPS download, aggregate district rainfall and build lag-window exposure columns.",
            "data_write_gate_effect": "does_not_open_data_gate",
        },
        {
            "country": COUNTRY,
            "wave": WAVE,
            "idno": IDNO,
            "policy_component": "promotion_stop_rule",
            "route_decision": "keep_accepted_chirps_era5_route_closed_until_extraction_validation_passes",
            "source_or_input": "promotion registry and climate preflight gate",
            "verified_evidence": f"route_design_ready={1 if route_design_ready else 0}; required_downloads={len(download_rows)}; raster_extraction_completed=0.",
            "route_status": "not_accepted_extraction_and_validation_pending",
            "next_action": "Do not write promoted household-climate data until CHIRPS values are extracted, units checked, district coverage validated, and lag windows reviewed.",
            "data_write_gate_effect": "does_not_open_data_gate",
        },
    ]

    summary_rows = [
        {"metric": "country_wave", "value": IDNO, "interpretation": "Country-wave covered by the CHIRPS ADM2 route policy."},
        {"metric": "climate_route_policy_status", "value": status, "interpretation": "Route design status before climate raster extraction."},
        {"metric": "route_design_ready", "value": "1" if route_design_ready else "0", "interpretation": "Whether raw timing, raw district labels, ADM2 boundary names, and CHIRPS download manifest form a coherent route design."},
        {"metric": "accepted_chirps_era5_route", "value": "0", "interpretation": "The promoted climate gate remains closed until CHIRPS extraction and validation pass."},
        {"metric": "current_climate_linkage_gate_status", "value": "route_preflight_ready_needs_extraction_validation" if route_design_ready else "blocked_crosswalk_or_source_manifest", "interpretation": "Updated preflight status for Malawi 2004 climate linkage."},
        {"metric": "raw_district_rows", "value": counts["raw_district_rows"], "interpretation": "Raw Malawi 2004 district labels observed in household data."},
        {"metric": "boundary_adm2_features", "value": counts["boundary_features"], "interpretation": "ADM2 features in the local geoBoundaries Malawi boundary file."},
        {"metric": "raw_district_boundary_matches", "value": counts["raw_district_boundary_matches"], "interpretation": "Raw district labels matched to ADM2 boundary names after normalization."},
        {"metric": "raw_district_boundary_unmatched", "value": counts["raw_district_boundary_unmatched"], "interpretation": "Raw district labels not matched to ADM2 boundary names; must be zero before extraction."},
        {"metric": "boundary_no_sample_rows", "value": counts["boundary_no_sample_rows"], "interpretation": "ADM2 boundary districts with no sampled households in Malawi 2004."},
        {"metric": "boundary_no_sample_names", "value": counts["boundary_no_sample_names"], "interpretation": "Boundary districts present but absent from the raw sample."},
        {"metric": "interview_month_count", "value": str(len(months)), "interpretation": "Distinct raw interview months."},
        {"metric": "interview_month_min", "value": period_text(months[0]), "interpretation": "Earliest raw interview month."},
        {"metric": "interview_month_max", "value": period_text(months[-1]), "interpretation": "Latest raw interview month."},
        {"metric": "required_chirps_months", "value": str(len(download_rows)), "interpretation": "CHIRPS monthly files needed for 1, 3, 6, and 12 complete-month windows."},
        {"metric": "required_chirps_month_min", "value": download_rows[0]["chirps_month"], "interpretation": "Earliest required CHIRPS month."},
        {"metric": "required_chirps_month_max", "value": download_rows[-1]["chirps_month"], "interpretation": "Latest required CHIRPS month."},
        {"metric": "boundary_file_sha256", "value": sha256_file(BOUNDARY_PATH), "interpretation": "Checksum of the local boundary file used for route validation; raw boundary file is not intended for GitHub publication."},
        {"metric": "data_write_gate_status", "value": "closed", "interpretation": "No promoted household-climate data are written by this route policy."},
    ]
    return policy_rows, crosswalk_rows, download_rows, summary_rows


def write_report(
    policy_rows: list[dict[str, str]],
    crosswalk_rows: list[dict[str, str]],
    download_rows: list[dict[str, str]],
    summary_rows: list[dict[str, str]],
) -> None:
    report = f"""# Malawi 2004 CHIRPS ADM2 Route Policy

Dataset: `{IDNO}` - {COUNTRY} {WAVE}

This artifact selects and verifies a district-month CHIRPS route design for
Malawi 2004. It does not download CHIRPS rasters, does not extract climate
values, does not accept the promoted CHIRPS/ERA5 linkage gate, and does not
write promoted data.

## Summary

{markdown_table(summary_rows, ["metric", "value", "interpretation"], 30)}

## Policy Rows

{markdown_table(policy_rows, ["policy_component", "route_decision", "route_status", "next_action"], 20)}

## District Crosswalk

{markdown_table(crosswalk_rows, ["raw_dist_code", "raw_dist_label", "normalized_adm2_name", "household_rows", "boundary_match_status"], 35)}

## CHIRPS Download Manifest Preview

{markdown_table(download_rows, ["chirps_month", "chirps_file", "download_status"], 30)}

## Source Route

- Rainfall: CHIRPS v2.0 Africa monthly GeoTIFF files under `{CHIRPS_MONTHLY_TIF_BASE}`.
- Boundary: geoBoundaries Malawi ADM2 GeoJSON from `{GEOB_API_URL}`.
- Spatial unit: ADM2 district. Raw combined city labels are assigned to the
  parent district name before matching.
- Temporal unit: interview month, with 1, 3, 6, and 12 complete-month
  rainfall windows before the interview month.

## Still Blocked

- CHIRPS monthly rasters are not downloaded in this artifact.
- District rainfall values and lag-window exposures are not extracted.
- The promoted `accepted_chirps_era5_route` gate remains closed until raster
  extraction, unit checks, spatial coverage checks, and lag-window validation
  pass.
"""
    REPORT_PATH.write_text(report, encoding="utf-8")
    HANDOFF_PATH.write_text(report, encoding="utf-8")


def main() -> None:
    ensure_dirs()
    policy_rows, crosswalk_rows, download_rows, summary_rows = build_outputs()
    write_csv(POLICY_PATH, policy_rows, POLICY_COLUMNS)
    write_csv(CROSSWALK_PATH, crosswalk_rows, CROSSWALK_COLUMNS)
    write_csv(DOWNLOADS_PATH, download_rows, DOWNLOAD_COLUMNS)
    write_csv(SUMMARY_PATH, summary_rows, SUMMARY_COLUMNS)
    write_report(policy_rows, crosswalk_rows, download_rows, summary_rows)
    append_log(TEMP_DIR / "audit_log.md", f"Built Malawi 2004 CHIRPS ADM2 route policy for {IDNO}.")


if __name__ == "__main__":
    main()
