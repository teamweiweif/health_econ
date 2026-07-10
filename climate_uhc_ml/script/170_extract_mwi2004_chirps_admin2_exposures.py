from __future__ import annotations

import csv
import gzip
import io
import json
import math
import os
import tempfile
from pathlib import Path, PurePosixPath
from typing import Any, Iterable
from zipfile import ZipFile

import numpy as np
import pandas as pd
import pyreadstat
from PIL import Image

from common import REPORT_DIR, RESULT_DIR, TEMP_DIR, append_log, ensure_dirs, sha256_file, write_csv


Image.MAX_IMAGE_PIXELS = None

IDNO = "MWI_2004_IHS-II_v01_M"
COUNTRY = "Malawi"
WAVE = "2004-2005"
RAW_DIR = TEMP_DIR / "raw_downloads" / IDNO
ZIP_PATH = RAW_DIR / "MWI_2004_IHS-II_v01_M_Stata8.zip"
BOUNDARY_PATH = TEMP_DIR / "raw_downloads" / "climate_boundaries" / "geoBoundaries-MWI-ADM2.geojson"
DOWNLOAD_MANIFEST_PATH = RESULT_DIR / "mwi2004_chirps_admin2_required_downloads.csv"
CROSSWALK_PATH = RESULT_DIR / "mwi2004_chirps_admin2_crosswalk.csv"

DOWNLOAD_AUDIT_PATH = RESULT_DIR / "mwi2004_chirps_admin2_download_audit.csv"
DISTRICT_MONTH_PATH = RESULT_DIR / "mwi2004_chirps_admin2_district_month_exposure.csv"
LAG_WINDOW_PATH = RESULT_DIR / "mwi2004_chirps_admin2_lag_window_exposure.csv"
VALIDATION_PATH = RESULT_DIR / "mwi2004_chirps_admin2_extraction_validation.csv"
SUMMARY_PATH = RESULT_DIR / "mwi2004_chirps_admin2_extraction_summary.csv"
REPORT_PATH = REPORT_DIR / "mwi2004_chirps_admin2_extraction_validation.md"
HANDOFF_PATH = RAW_DIR / "_MWI2004_CHIRPS_ADMIN2_EXTRACTION_VALIDATION.md"

DOWNLOAD_AUDIT_COLUMNS = [
    "country",
    "wave",
    "idno",
    "chirps_month",
    "chirps_file",
    "local_target_path",
    "exists",
    "bytes",
    "sha256",
    "read_status",
    "width",
    "height",
    "origin_lon",
    "origin_lat",
    "pixel_width_degree",
    "pixel_height_degree",
    "valid_value_min",
    "valid_value_max",
    "notes",
]
DISTRICT_MONTH_COLUMNS = [
    "country",
    "wave",
    "idno",
    "adm2_name",
    "chirps_month",
    "source_file",
    "source_sha256",
    "mask_pixel_count",
    "valid_pixel_count",
    "mean_precip_mm",
    "min_precip_mm",
    "max_precip_mm",
    "extraction_status",
]
LAG_WINDOW_COLUMNS = [
    "country",
    "wave",
    "idno",
    "raw_dist_code",
    "raw_dist_label",
    "adm2_name",
    "interview_month",
    "household_rows",
    "lag_months",
    "window_start_month",
    "window_end_month",
    "months_expected",
    "months_available",
    "precip_total_mm",
    "precip_mean_monthly_mm",
    "window_complete",
]
VALIDATION_COLUMNS = [
    "country",
    "wave",
    "idno",
    "validation_component",
    "status",
    "evidence",
    "required_action",
]
SUMMARY_COLUMNS = ["metric", "value", "interpretation"]


def clean(value: Any) -> str:
    if value is None:
        return ""
    return " ".join(str(value).split())


def read_csv_dicts(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        return []
    with path.open(encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def member_name(zip_path: Path, basename: str) -> str:
    with ZipFile(zip_path) as zf:
        for name in zf.namelist():
            if PurePosixPath(name).name.lower() == basename.lower():
                return name
    raise FileNotFoundError(f"{basename} not found in {zip_path}")


def read_member(zip_path: Path, basename: str, columns: list[str], apply_value_formats: bool) -> pd.DataFrame:
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
        df, _ = pyreadstat.read_dta(str(raw_path), apply_value_formats=apply_value_formats, usecols=usecols)
        return df
    finally:
        raw_path.unlink(missing_ok=True)


def period_text(period: pd.Period | Any) -> str:
    if isinstance(period, pd.Period):
        return f"{period.year:04d}-{period.month:02d}"
    return clean(period)


def fmt(value: float | np.floating[Any] | None, digits: int = 6) -> str:
    if value is None:
        return ""
    if not np.isfinite(value):
        return ""
    return f"{float(value):.{digits}f}"


def read_chirps(path: Path) -> tuple[np.ndarray, dict[str, float | int | str]]:
    with gzip.open(path, "rb") as f:
        payload = f.read()
    image = Image.open(io.BytesIO(payload))
    array = np.asarray(image, dtype=np.float32)
    scale = tuple(float(x) for x in image.tag_v2[33550])
    tiepoint = tuple(float(x) for x in image.tag_v2[33922])
    info: dict[str, float | int | str] = {
        "width": int(image.size[0]),
        "height": int(image.size[1]),
        "origin_lon": tiepoint[3],
        "origin_lat": tiepoint[4],
        "pixel_width_degree": scale[0],
        "pixel_height_degree": scale[1],
    }
    valid = array[np.isfinite(array) & (array > -9000)]
    info["valid_value_min"] = float(valid.min()) if valid.size else math.nan
    info["valid_value_max"] = float(valid.max()) if valid.size else math.nan
    return array, info


def iter_points(obj: Any) -> Iterable[tuple[float, float]]:
    if isinstance(obj, list):
        if len(obj) >= 2 and all(isinstance(item, (int, float)) for item in obj[:2]):
            yield float(obj[0]), float(obj[1])
        else:
            for item in obj:
                yield from iter_points(item)


def geometry_bbox(geometry: dict[str, Any]) -> tuple[float, float, float, float]:
    points = list(iter_points(geometry.get("coordinates", [])))
    xs = [point[0] for point in points]
    ys = [point[1] for point in points]
    return min(xs), min(ys), max(xs), max(ys)


def geometry_polygons(geometry: dict[str, Any]) -> list[list[list[list[float]]]]:
    gtype = geometry.get("type")
    coords = geometry.get("coordinates", [])
    if gtype == "Polygon":
        return [coords]
    if gtype == "MultiPolygon":
        return [polygon for polygon in coords]
    raise ValueError(f"Unsupported geometry type: {gtype}")


def point_in_ring(xs: np.ndarray, ys: np.ndarray, ring: list[list[float]]) -> np.ndarray:
    xv = np.asarray([point[0] for point in ring], dtype=np.float64)
    yv = np.asarray([point[1] for point in ring], dtype=np.float64)
    inside = np.zeros(xs.shape, dtype=bool)
    j = len(xv) - 1
    for i in range(len(xv)):
        yi = yv[i]
        yj = yv[j]
        xi = xv[i]
        xj = xv[j]
        crosses = (yi > ys) != (yj > ys)
        denom = yj - yi
        denom = denom if abs(denom) > 1e-15 else 1e-15
        x_intersect = (xj - xi) * (ys - yi) / denom + xi
        inside ^= crosses & (xs < x_intersect)
        j = i
    return inside


def polygon_mask_indices(
    geometry: dict[str, Any],
    raster_info: dict[str, float | int | str],
) -> tuple[np.ndarray, np.ndarray]:
    width = int(raster_info["width"])
    height = int(raster_info["height"])
    x0 = float(raster_info["origin_lon"])
    y0 = float(raster_info["origin_lat"])
    dx = float(raster_info["pixel_width_degree"])
    dy = float(raster_info["pixel_height_degree"])
    minx, miny, maxx, maxy = geometry_bbox(geometry)
    col_min = max(0, int(math.floor((minx - x0) / dx)) - 2)
    col_max = min(width - 1, int(math.ceil((maxx - x0) / dx)) + 2)
    row_min = max(0, int(math.floor((y0 - maxy) / dy)) - 2)
    row_max = min(height - 1, int(math.ceil((y0 - miny) / dy)) + 2)
    rows = np.arange(row_min, row_max + 1)
    cols = np.arange(col_min, col_max + 1)
    grid_cols, grid_rows = np.meshgrid(cols, rows)
    xs = x0 + (grid_cols.astype(np.float64) + 0.5) * dx
    ys = y0 - (grid_rows.astype(np.float64) + 0.5) * dy
    inside_any = np.zeros(xs.shape, dtype=bool)
    for polygon in geometry_polygons(geometry):
        if not polygon:
            continue
        inside = point_in_ring(xs, ys, polygon[0])
        for hole in polygon[1:]:
            inside &= ~point_in_ring(xs, ys, hole)
        inside_any |= inside
    selected_rows = grid_rows[inside_any].astype(np.int64)
    selected_cols = grid_cols[inside_any].astype(np.int64)
    return selected_rows, selected_cols


def load_boundary_features() -> dict[str, dict[str, Any]]:
    obj = json.loads(BOUNDARY_PATH.read_text(encoding="utf-8"))
    out: dict[str, dict[str, Any]] = {}
    for feature in obj.get("features", []):
        name = clean(feature.get("properties", {}).get("shapeName"))
        if name:
            out[name] = feature.get("geometry", {})
    return out


def household_dist_months() -> list[dict[str, str]]:
    raw = read_member(ZIP_PATH, "ihs2_household.dta", ["dist", "idate"], apply_value_formats=False)
    labels = read_member(ZIP_PATH, "ihs2_household.dta", ["dist"], apply_value_formats=True)
    numeric = pd.to_numeric(raw["idate"], errors="coerce")
    months = pd.to_datetime(numeric, unit="D", origin="1960-01-01", errors="coerce").dt.to_period("M")
    work = pd.DataFrame(
        {
            "raw_dist_code": raw["dist"],
            "raw_dist_label": labels["dist"].astype(str),
            "interview_month": months.astype(str),
        }
    )
    crosswalk = {
        clean(row.get("raw_dist_code")): clean(row.get("normalized_adm2_name"))
        for row in read_csv_dicts(CROSSWALK_PATH)
        if clean(row.get("route_role")) == "sampled_raw_district"
    }
    rows: list[dict[str, str]] = []
    grouped = work.groupby(["raw_dist_code", "raw_dist_label", "interview_month"], dropna=False).size().reset_index(name="household_rows")
    for _, row in grouped.iterrows():
        if clean(row["interview_month"]) == "NaT":
            continue
        code = str(int(row["raw_dist_code"])) if pd.notna(row["raw_dist_code"]) else ""
        rows.append(
            {
                "raw_dist_code": code,
                "raw_dist_label": clean(row["raw_dist_label"]),
                "adm2_name": crosswalk.get(code, ""),
                "interview_month": clean(row["interview_month"]),
                "household_rows": str(int(row["household_rows"])),
            }
        )
    return rows


def build_lag_rows(
    observed_dist_months: list[dict[str, str]],
    district_month_values: dict[tuple[str, str], float],
) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    for item in observed_dist_months:
        interview_month = pd.Period(item["interview_month"], freq="M")
        adm2 = item["adm2_name"]
        for lag in [1, 3, 6, 12]:
            months = list(pd.period_range(start=interview_month - lag, end=interview_month - 1, freq="M"))
            values = [district_month_values.get((adm2, period_text(month))) for month in months]
            available = [value for value in values if value is not None and np.isfinite(value)]
            total = float(sum(available)) if len(available) == len(months) else math.nan
            mean = float(total / lag) if np.isfinite(total) else math.nan
            rows.append(
                {
                    "country": COUNTRY,
                    "wave": WAVE,
                    "idno": IDNO,
                    "raw_dist_code": item["raw_dist_code"],
                    "raw_dist_label": item["raw_dist_label"],
                    "adm2_name": adm2,
                    "interview_month": item["interview_month"],
                    "household_rows": item["household_rows"],
                    "lag_months": str(lag),
                    "window_start_month": period_text(months[0]),
                    "window_end_month": period_text(months[-1]),
                    "months_expected": str(len(months)),
                    "months_available": str(len(available)),
                    "precip_total_mm": fmt(total),
                    "precip_mean_monthly_mm": fmt(mean),
                    "window_complete": "1" if len(available) == len(months) else "0",
                }
            )
    return rows


def validation_row(component: str, ok: bool, evidence: str, action: str) -> dict[str, str]:
    return {
        "country": COUNTRY,
        "wave": WAVE,
        "idno": IDNO,
        "validation_component": component,
        "status": "pass" if ok else "fail",
        "evidence": evidence,
        "required_action": "" if ok else action,
    }


def markdown_table(rows: list[dict[str, str]], columns: list[str], limit: int = 25) -> str:
    if not rows:
        return "_No rows._"
    lines = ["| " + " | ".join(columns) + " |", "| " + " | ".join("---" for _ in columns) + " |"]
    for row in rows[:limit]:
        lines.append("| " + " | ".join(clean(row.get(column)).replace("|", "/") for column in columns) + " |")
    if len(rows) > limit:
        lines.append("| " + " | ".join("..." for _ in columns) + " |")
    return "\n".join(lines)


def build_outputs() -> tuple[list[dict[str, str]], list[dict[str, str]], list[dict[str, str]], list[dict[str, str]], list[dict[str, str]]]:
    manifest = read_csv_dicts(DOWNLOAD_MANIFEST_PATH)
    if not manifest:
        raise FileNotFoundError(f"Missing CHIRPS download manifest: {DOWNLOAD_MANIFEST_PATH}")
    if not BOUNDARY_PATH.exists():
        raise FileNotFoundError(f"Missing boundary file: {BOUNDARY_PATH}")

    first_array: np.ndarray | None = None
    first_info: dict[str, float | int | str] | None = None
    download_rows: list[dict[str, str]] = []
    arrays: dict[str, np.ndarray] = {}
    infos: dict[str, dict[str, float | int | str]] = {}
    for row in manifest:
        path = Path(row["local_target_path"])
        exists = path.exists() and path.stat().st_size > 0
        read_status = "not_read"
        info: dict[str, float | int | str] = {}
        if exists:
            array, info = read_chirps(path)
            arrays[row["chirps_month"]] = array
            infos[row["chirps_month"]] = info
            read_status = "readable_geotiff"
            if first_array is None:
                first_array = array
                first_info = info
        download_rows.append(
            {
                "country": COUNTRY,
                "wave": WAVE,
                "idno": IDNO,
                "chirps_month": row.get("chirps_month", ""),
                "chirps_file": row.get("chirps_file", ""),
                "local_target_path": row.get("local_target_path", ""),
                "exists": "1" if exists else "0",
                "bytes": str(path.stat().st_size) if exists else "0",
                "sha256": sha256_file(path) if exists else "",
                "read_status": read_status,
                "width": str(info.get("width", "")),
                "height": str(info.get("height", "")),
                "origin_lon": str(info.get("origin_lon", "")),
                "origin_lat": str(info.get("origin_lat", "")),
                "pixel_width_degree": str(info.get("pixel_width_degree", "")),
                "pixel_height_degree": str(info.get("pixel_height_degree", "")),
                "valid_value_min": fmt(info.get("valid_value_min") if info else None),
                "valid_value_max": fmt(info.get("valid_value_max") if info else None),
                "notes": "CHIRPS monthly precipitation in millimeters; -9999 ignored as no-data.",
            }
        )
    if first_array is None or first_info is None:
        raise RuntimeError("No readable CHIRPS rasters were found.")

    boundary_features = load_boundary_features()
    masks = {
        name: polygon_mask_indices(geometry, first_info)
        for name, geometry in boundary_features.items()
    }
    georef_ref = (
        first_info["width"],
        first_info["height"],
        first_info["origin_lon"],
        first_info["origin_lat"],
        round(float(first_info["pixel_width_degree"]), 10),
        round(float(first_info["pixel_height_degree"]), 10),
    )
    georef_consistent = all(
        (
            info["width"],
            info["height"],
            info["origin_lon"],
            info["origin_lat"],
            round(float(info["pixel_width_degree"]), 10),
            round(float(info["pixel_height_degree"]), 10),
        )
        == georef_ref
        for info in infos.values()
    )

    district_rows: list[dict[str, str]] = []
    district_month_values: dict[tuple[str, str], float] = {}
    for month in sorted(arrays):
        array = arrays[month]
        source_file = next(row for row in download_rows if row["chirps_month"] == month)
        for adm2_name in sorted(boundary_features):
            rr, cc = masks[adm2_name]
            values = array[rr, cc]
            valid = values[np.isfinite(values) & (values > -9000)]
            mean_value = float(valid.mean()) if valid.size else math.nan
            district_month_values[(adm2_name, month)] = mean_value
            district_rows.append(
                {
                    "country": COUNTRY,
                    "wave": WAVE,
                    "idno": IDNO,
                    "adm2_name": adm2_name,
                    "chirps_month": month,
                    "source_file": source_file["chirps_file"],
                    "source_sha256": source_file["sha256"],
                    "mask_pixel_count": str(len(values)),
                    "valid_pixel_count": str(int(valid.size)),
                    "mean_precip_mm": fmt(mean_value),
                    "min_precip_mm": fmt(float(valid.min()) if valid.size else math.nan),
                    "max_precip_mm": fmt(float(valid.max()) if valid.size else math.nan),
                    "extraction_status": "pass" if valid.size else "fail_no_valid_pixels",
                }
            )

    observed = household_dist_months()
    lag_rows = build_lag_rows(observed, district_month_values)
    sampled_districts = sorted({row["adm2_name"] for row in observed if row["adm2_name"]})
    sampled_district_month_rows = [
        row for row in district_rows if row["adm2_name"] in sampled_districts
    ]
    sampled_all_valid = all(int(row["valid_pixel_count"]) > 0 for row in sampled_district_month_rows)
    all_lag_complete = all(row["window_complete"] == "1" for row in lag_rows)
    value_min = min(float(row["mean_precip_mm"]) for row in district_rows if row["mean_precip_mm"])
    value_max = max(float(row["mean_precip_mm"]) for row in district_rows if row["mean_precip_mm"])
    all_downloads_present = all(row["exists"] == "1" and row["read_status"] == "readable_geotiff" for row in download_rows)
    all_masks_nonempty = all(len(rows) > 0 for rows, _cols in masks.values())
    accepted = all_downloads_present and georef_consistent and sampled_all_valid and all_lag_complete and value_min >= 0

    validation_rows = [
        validation_row(
            "download_manifest_fulfilled",
            all_downloads_present,
            f"downloaded_readable={sum(1 for row in download_rows if row['read_status'] == 'readable_geotiff')}/{len(download_rows)}",
            "Download every required CHIRPS monthly GeoTIFF and rerun extraction.",
        ),
        validation_row(
            "geotiff_grid_consistency",
            georef_consistent,
            f"reference_grid={georef_ref}; raster_files={len(infos)}",
            "Use a consistent CHIRPS grid before district-month aggregation.",
        ),
        validation_row(
            "adm2_polygon_masks_nonempty",
            all_masks_nonempty,
            f"adm2_masks={len(masks)}; min_pixels={min(len(rows) for rows, _cols in masks.values())}; max_pixels={max(len(rows) for rows, _cols in masks.values())}",
            "Repair boundary geometry or raster georeference before extraction.",
        ),
        validation_row(
            "sampled_raw_district_month_coverage",
            sampled_all_valid,
            f"sampled_districts={len(sampled_districts)}; sampled_district_month_rows={len(sampled_district_month_rows)}; valid_rows={sum(1 for row in sampled_district_month_rows if int(row['valid_pixel_count']) > 0)}",
            "All raw-sampled districts must have valid CHIRPS pixels for every required month.",
        ),
        validation_row(
            "lag_windows_complete",
            all_lag_complete,
            f"lag_rows={len(lag_rows)}; complete_rows={sum(1 for row in lag_rows if row['window_complete'] == '1')}",
            "Every observed district-interview-month lag window must have all required monthly values.",
        ),
        validation_row(
            "precipitation_values_nonnegative",
            value_min >= 0 and np.isfinite(value_max),
            f"mean_precip_min={fmt(value_min)}; mean_precip_max={fmt(value_max)}",
            "Inspect no-data handling and units if extracted precipitation is negative or missing.",
        ),
    ]

    summary_rows = [
        {"metric": "country_wave", "value": IDNO, "interpretation": "Country-wave covered by CHIRPS ADM2 extraction."},
        {"metric": "chirps_files_required", "value": str(len(manifest)), "interpretation": "Required CHIRPS monthly GeoTIFF files from the route manifest."},
        {"metric": "chirps_files_downloaded_readable", "value": str(sum(1 for row in download_rows if row["read_status"] == "readable_geotiff")), "interpretation": "Downloaded files read successfully as GeoTIFF with PIL."},
        {"metric": "boundary_adm2_features", "value": str(len(boundary_features)), "interpretation": "ADM2 boundary features used for district masks."},
        {"metric": "district_month_exposure_rows", "value": str(len(district_rows)), "interpretation": "ADM2 district-month rainfall exposure rows."},
        {"metric": "sampled_raw_districts", "value": str(len(sampled_districts)), "interpretation": "Raw Malawi 2004 districts observed in household data and mapped to ADM2."},
        {"metric": "observed_raw_district_interview_month_rows", "value": str(len(observed)), "interpretation": "Observed raw district by interview-month cells in the household sample."},
        {"metric": "lag_window_exposure_rows", "value": str(len(lag_rows)), "interpretation": "District-interview-month lag-window exposure rows."},
        {"metric": "lag_window_complete_rows", "value": str(sum(1 for row in lag_rows if row["window_complete"] == "1")), "interpretation": "Lag-window rows with all required months available."},
        {"metric": "mean_precip_min_mm", "value": fmt(value_min), "interpretation": "Minimum extracted district-month mean precipitation."},
        {"metric": "mean_precip_max_mm", "value": fmt(value_max), "interpretation": "Maximum extracted district-month mean precipitation."},
        {"metric": "geotiff_grid_consistent", "value": "1" if georef_consistent else "0", "interpretation": "Whether all CHIRPS rasters share the same georeference."},
        {"metric": "accepted_chirps_route", "value": "1" if accepted else "0", "interpretation": "Whether the CHIRPS ADM2 route passes extraction validation."},
        {"metric": "accepted_chirps_era5_route", "value": "1" if accepted else "0", "interpretation": "Promotion gate flag for accepted CHIRPS or ERA5 route; this is CHIRPS-only."},
        {"metric": "current_climate_linkage_gate_status", "value": "accepted_chirps_admin2_extraction_validated" if accepted else "blocked_chirps_admin2_extraction_validation_failed", "interpretation": "Current climate linkage gate after raster extraction validation."},
        {"metric": "data_write_gate_status", "value": "closed", "interpretation": "This extraction artifact does not write promoted household-climate data by itself."},
    ]
    return download_rows, district_rows, lag_rows, validation_rows, summary_rows


def write_report(
    download_rows: list[dict[str, str]],
    district_rows: list[dict[str, str]],
    lag_rows: list[dict[str, str]],
    validation_rows: list[dict[str, str]],
    summary_rows: list[dict[str, str]],
) -> None:
    report = f"""# Malawi 2004 CHIRPS ADM2 Extraction Validation

Dataset: `{IDNO}` - {COUNTRY} {WAVE}

This artifact extracts CHIRPS v2.0 Africa monthly rainfall to Malawi ADM2
district polygons using only local CHIRPS GeoTIFF files and the cached
geoBoundaries Malawi ADM2 geometry. It does not write a promoted household
dataset to `data/`.

## Summary

{markdown_table(summary_rows, ["metric", "value", "interpretation"], 25)}

## Validation

{markdown_table(validation_rows, ["validation_component", "status", "evidence", "required_action"], 20)}

## Download Audit Preview

{markdown_table(download_rows, ["chirps_month", "chirps_file", "bytes", "read_status", "valid_value_min", "valid_value_max"], 12)}

## District-Month Exposure Preview

{markdown_table(district_rows, ["adm2_name", "chirps_month", "valid_pixel_count", "mean_precip_mm", "extraction_status"], 20)}

## Lag-Window Exposure Preview

{markdown_table(lag_rows, ["raw_dist_code", "raw_dist_label", "interview_month", "lag_months", "precip_total_mm", "window_complete"], 20)}

## Remaining Promotion Work

- Merge lag-window exposures onto the verified Malawi 2004 household outcome
  construction.
- Review rainfall shock definitions before any model run.
- Keep modeling blocked until the multi-country registry thresholds pass.
"""
    REPORT_PATH.write_text(report, encoding="utf-8")
    HANDOFF_PATH.write_text(report, encoding="utf-8")


def main() -> None:
    ensure_dirs()
    download_rows, district_rows, lag_rows, validation_rows, summary_rows = build_outputs()
    write_csv(DOWNLOAD_AUDIT_PATH, download_rows, DOWNLOAD_AUDIT_COLUMNS)
    write_csv(DISTRICT_MONTH_PATH, district_rows, DISTRICT_MONTH_COLUMNS)
    write_csv(LAG_WINDOW_PATH, lag_rows, LAG_WINDOW_COLUMNS)
    write_csv(VALIDATION_PATH, validation_rows, VALIDATION_COLUMNS)
    write_csv(SUMMARY_PATH, summary_rows, SUMMARY_COLUMNS)
    write_report(download_rows, district_rows, lag_rows, validation_rows, summary_rows)
    append_log(TEMP_DIR / "audit_log.md", f"Extracted Malawi 2004 CHIRPS ADM2 exposures for {IDNO}.")


if __name__ == "__main__":
    main()
