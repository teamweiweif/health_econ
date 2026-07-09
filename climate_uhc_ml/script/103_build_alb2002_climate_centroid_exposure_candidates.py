from __future__ import annotations

import csv
import hashlib
import json
import time
from datetime import date, timedelta
from typing import Any

import pandas as pd
import requests
from dateutil.relativedelta import relativedelta

from common import REPORT_DIR, RESULT_DIR, TEMP_DIR, append_log, ensure_dirs, write_csv


IDNO = "ALB_2002_LSMS_v01_M"
COUNTRY = "Albania"
SURVEY_NAME = "Living Standards Measurement Survey 2002"
WAVE = "2002"

ANALYSIS_CANDIDATE_PATH = TEMP_DIR / "alb2002_analysis_candidate_dataset.csv"
BOUNDARY_GEOMETRY_PATH = TEMP_DIR / "alb2002_boundary_geometry_provenance_audit.csv"
BOUNDARY_SUMMARY_PATH = RESULT_DIR / "alb2002_boundary_geometry_provenance_summary.csv"

INPUT_PATH = TEMP_DIR / "alb2002_climate_centroid_exposure_input.csv"
EXPOSURE_PATH = TEMP_DIR / "alb2002_climate_centroid_exposure_candidates.csv"
API_MANIFEST_PATH = TEMP_DIR / "alb2002_climate_centroid_nasa_power_api_manifest.csv"
AUDIT_PATH = RESULT_DIR / "alb2002_climate_centroid_exposure_audit.csv"
SUMMARY_PATH = RESULT_DIR / "alb2002_climate_centroid_exposure_summary.csv"
REPORT_PATH = REPORT_DIR / "alb2002_climate_centroid_exposure_audit.md"

NASA_POWER_URL = "https://power.larc.nasa.gov/api/temporal/daily/point"
NASA_PARAMETERS = ["PRECTOTCORR", "T2M", "T2M_MAX", "T2M_MIN"]
WINDOWS_MONTHS = [1, 3, 6, 12]

DECISION = "blocked_alb2002_climate_centroid_exposures_not_promoted_due_boundary_vintage_source_and_baseline_gates"
PROMOTION_STATUS = "temp_only_climate_centroid_exposure_candidates_not_promoted"

INPUT_COLUMNS = [
    "country",
    "survey_name",
    "wave",
    "idno",
    "survey_year",
    "survey_month",
    "exposure_anchor_date",
    "district_code",
    "district_name",
    "household_rows",
    "centroid_lon",
    "centroid_lat",
    "boundary_source",
    "boundary_year",
    "boundary_match_method",
    "geolocation_quality",
    "promotion_status",
    "blocking_reason",
]

EXPOSURE_COLUMNS = [
    "country",
    "survey_name",
    "wave",
    "idno",
    "survey_year",
    "survey_month",
    "exposure_anchor_date",
    "district_code",
    "district_name",
    "household_rows",
    "centroid_lon",
    "centroid_lat",
    "window_months",
    "start_date",
    "end_date",
    "n_days",
    "precip_total_mm",
    "precip_mean_mm_day",
    "temp_mean_c",
    "temp_max_c",
    "temp_min_c",
    "source",
    "boundary_source",
    "boundary_year",
    "exposure_quality_flag",
    "primary_chirps_ready",
    "primary_era5_ready",
    "historical_baseline_ready",
    "climate_linkage_ready",
    "promotion_status",
    "blocking_reason",
]

API_COLUMNS = [
    "district_code",
    "district_name",
    "centroid_lon",
    "centroid_lat",
    "start_date",
    "end_date",
    "api_status",
    "cache_path",
    "nasa_request_url",
    "error",
]

AUDIT_COLUMNS = [
    "check_id",
    "check_label",
    "status",
    "rows_checked",
    "passing_rows",
    "failing_rows",
    "evidence",
    "promotion_ready_rows",
    "blocking_reason",
    "next_action",
]

SUMMARY_COLUMNS = ["metric", "value", "interpretation"]


def read_csv_dicts(path) -> list[dict[str, str]]:
    if not path.exists():
        return []
    with path.open(encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def metric_value(rows: list[dict[str, str]], metric: str, default: str = "0") -> str:
    return next((row.get("value", default) for row in rows if row.get("metric") == metric), default)


def safe_int(value: Any) -> int:
    try:
        return int(float(str(value).strip()))
    except (TypeError, ValueError):
        return 0


def safe_float(value: Any) -> float | None:
    try:
        return float(str(value).strip())
    except (TypeError, ValueError):
        return None


def fmt(value: Any) -> str:
    if value == "" or value is None:
        return ""
    try:
        number = float(value)
    except (TypeError, ValueError):
        return str(value)
    if number.is_integer():
        return str(int(number))
    return f"{number:.6g}"


def month_anchor(year: int, month: int) -> date:
    return date(year, month, 15)


def blocking_reason() -> str:
    return (
        "NASA POWER daily point summaries are computed at candidate district bounding-box centroids from a "
        "geoBoundaries 2.0.1 ADM2 snapshot, but the boundary metadata reports boundaryYear 2013 and no verified "
        "2001/2002 district boundary, exact GPS, CHIRPS/ERA5 primary extraction, or historical anomaly baseline is accepted."
    )


def build_input_rows(analysis: pd.DataFrame, geometry: pd.DataFrame, boundary_summary: list[dict[str, str]]) -> list[dict[str, Any]]:
    boundary_year = metric_value(boundary_summary, "alb2002_boundary_geometry_metadata_boundary_year", "missing")
    boundary_source = "geoBoundaries 2.0.1 ADM2 candidate snapshot"
    keep = [
        "survey_year",
        "survey_month",
        "admin2_code",
        "admin2",
    ]
    observed = analysis[keep].copy()
    observed["survey_year"] = pd.to_numeric(observed["survey_year"], errors="coerce").astype("Int64")
    observed["survey_month"] = pd.to_numeric(observed["survey_month"], errors="coerce").astype("Int64")
    observed["district_code"] = pd.to_numeric(observed["admin2_code"], errors="coerce").astype("Int64")
    grouped = (
        observed.dropna(subset=["survey_year", "survey_month", "district_code"])
        .groupby(["survey_year", "survey_month", "district_code", "admin2"], dropna=False)
        .size()
        .reset_index(name="household_rows")
    )

    geometry_by_code = {safe_int(row.get("survey_district_code")): row for row in geometry.to_dict("records")}
    rows: list[dict[str, Any]] = []
    for row in grouped.to_dict("records"):
        district_code = safe_int(row["district_code"])
        geo = geometry_by_code.get(district_code, {})
        lon = safe_float(geo.get("bbox_centroid_lon"))
        lat = safe_float(geo.get("bbox_centroid_lat"))
        anchor = month_anchor(int(row["survey_year"]), int(row["survey_month"]))
        rows.append(
            {
                "country": COUNTRY,
                "survey_name": SURVEY_NAME,
                "wave": WAVE,
                "idno": IDNO,
                "survey_year": int(row["survey_year"]),
                "survey_month": int(row["survey_month"]),
                "exposure_anchor_date": anchor.isoformat(),
                "district_code": district_code,
                "district_name": row["admin2"],
                "household_rows": int(row["household_rows"]),
                "centroid_lon": fmt(lon),
                "centroid_lat": fmt(lat),
                "boundary_source": boundary_source,
                "boundary_year": boundary_year,
                "boundary_match_method": geo.get("survey_match_method", ""),
                "geolocation_quality": "candidate_admin2_bbox_centroid_not_verified_2002_boundary",
                "promotion_status": PROMOTION_STATUS,
                "blocking_reason": blocking_reason(),
            }
        )
    return rows


def cache_key(lon: float, lat: float, start: str, end: str) -> str:
    raw = f"{lon:.5f}_{lat:.5f}_{start}_{end}_{','.join(NASA_PARAMETERS)}"
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()[:24]


def fetch_nasa_power(lon: float, lat: float, start: str, end: str) -> tuple[dict[str, Any] | None, dict[str, str]]:
    cache_dir = TEMP_DIR / "climate_cache" / "alb2002_nasa_power_centroid"
    cache_dir.mkdir(parents=True, exist_ok=True)
    key = cache_key(lon, lat, start, end)
    cache_path = cache_dir / f"{key}.json"
    params = {
        "parameters": ",".join(NASA_PARAMETERS),
        "community": "AG",
        "longitude": f"{lon:.5f}",
        "latitude": f"{lat:.5f}",
        "start": start.replace("-", ""),
        "end": end.replace("-", ""),
        "format": "JSON",
    }
    prepared = requests.Request("GET", NASA_POWER_URL, params=params).prepare()
    if cache_path.exists():
        return json.loads(cache_path.read_text(encoding="utf-8")), {
            "api_status": "cached",
            "cache_path": str(cache_path.relative_to(TEMP_DIR.parent)),
            "nasa_request_url": prepared.url or "",
            "error": "",
        }
    last_error = ""
    for attempt in range(1, 4):
        try:
            response = requests.get(NASA_POWER_URL, params=params, timeout=90)
            response.raise_for_status()
            data = response.json()
            cache_path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
            return data, {
                "api_status": "downloaded",
                "cache_path": str(cache_path.relative_to(TEMP_DIR.parent)),
                "nasa_request_url": response.url,
                "error": "",
            }
        except Exception as exc:
            last_error = str(exc)
            if attempt < 3:
                time.sleep(2 * attempt)
    return None, {
        "api_status": "failed",
        "cache_path": str(cache_path.relative_to(TEMP_DIR.parent)),
        "nasa_request_url": prepared.url or "",
        "error": last_error,
    }


def parameter_frame(data: dict[str, Any]) -> pd.DataFrame:
    params = data.get("properties", {}).get("parameter", {})
    frame = pd.DataFrame(
        {
            "date_key": sorted(set().union(*(set(values.keys()) for values in params.values())) if params else []),
        }
    )
    if frame.empty:
        return frame
    frame["date"] = pd.to_datetime(frame["date_key"], format="%Y%m%d", errors="coerce")
    for parameter in NASA_PARAMETERS:
        values = params.get(parameter, {})
        frame[parameter] = pd.to_numeric(frame["date_key"].map(values), errors="coerce").replace(-999, pd.NA)
    return frame.dropna(subset=["date"])


def aggregate_window(frame: pd.DataFrame, start: date, end: date) -> dict[str, Any]:
    mask = (frame["date"] >= pd.Timestamp(start)) & (frame["date"] <= pd.Timestamp(end))
    window = frame.loc[mask].copy()
    if window.empty:
        return {
            "n_days": 0,
            "precip_total_mm": "",
            "precip_mean_mm_day": "",
            "temp_mean_c": "",
            "temp_max_c": "",
            "temp_min_c": "",
        }
    precip = pd.to_numeric(window["PRECTOTCORR"], errors="coerce").dropna()
    tmean = pd.to_numeric(window["T2M"], errors="coerce").dropna()
    tmax = pd.to_numeric(window["T2M_MAX"], errors="coerce").dropna()
    tmin = pd.to_numeric(window["T2M_MIN"], errors="coerce").dropna()
    return {
        "n_days": int(len(window)),
        "precip_total_mm": fmt(float(precip.sum())) if not precip.empty else "",
        "precip_mean_mm_day": fmt(float(precip.mean())) if not precip.empty else "",
        "temp_mean_c": fmt(float(tmean.mean())) if not tmean.empty else "",
        "temp_max_c": fmt(float(tmax.max())) if not tmax.empty else "",
        "temp_min_c": fmt(float(tmin.min())) if not tmin.empty else "",
    }


def build_exposures(inputs: list[dict[str, Any]]) -> tuple[list[dict[str, Any]], list[dict[str, str]]]:
    by_district: dict[int, list[dict[str, Any]]] = {}
    for row in inputs:
        by_district.setdefault(safe_int(row["district_code"]), []).append(row)

    exposures: list[dict[str, Any]] = []
    manifest: list[dict[str, str]] = []
    for district_code, rows in sorted(by_district.items()):
        valid_rows = [row for row in rows if safe_float(row.get("centroid_lon")) is not None and safe_float(row.get("centroid_lat")) is not None]
        if not valid_rows:
            for row in rows:
                for months in WINDOWS_MONTHS:
                    exposures.append(exposure_row(row, months, "", "", {}, "failed_no_centroid"))
            continue

        lon = float(valid_rows[0]["centroid_lon"])
        lat = float(valid_rows[0]["centroid_lat"])
        anchors = [pd.Timestamp(row["exposure_anchor_date"]).date() for row in valid_rows]
        earliest_start = min(anchor - relativedelta(months=max(WINDOWS_MONTHS)) for anchor in anchors)
        latest_end = max(anchor - timedelta(days=1) for anchor in anchors)
        data, api = fetch_nasa_power(lon, lat, earliest_start.isoformat(), latest_end.isoformat())
        manifest.append(
            {
                "district_code": str(district_code),
                "district_name": str(valid_rows[0]["district_name"]),
                "centroid_lon": fmt(lon),
                "centroid_lat": fmt(lat),
                "start_date": earliest_start.isoformat(),
                "end_date": latest_end.isoformat(),
                **api,
            }
        )
        frame = parameter_frame(data) if data else pd.DataFrame()
        for row in rows:
            anchor = pd.Timestamp(row["exposure_anchor_date"]).date()
            for months in WINDOWS_MONTHS:
                start = anchor - relativedelta(months=months)
                end = anchor - timedelta(days=1)
                aggregate = aggregate_window(frame, start, end) if not frame.empty else {}
                exposures.append(exposure_row(row, months, start.isoformat(), end.isoformat(), aggregate, api["api_status"]))
    return exposures, manifest


def exposure_row(row: dict[str, Any], months: int, start: str, end: str, aggregate: dict[str, Any], api_status: str) -> dict[str, Any]:
    return {
        "country": row.get("country", COUNTRY),
        "survey_name": row.get("survey_name", SURVEY_NAME),
        "wave": row.get("wave", WAVE),
        "idno": row.get("idno", IDNO),
        "survey_year": row.get("survey_year", ""),
        "survey_month": row.get("survey_month", ""),
        "exposure_anchor_date": row.get("exposure_anchor_date", ""),
        "district_code": row.get("district_code", ""),
        "district_name": row.get("district_name", ""),
        "household_rows": row.get("household_rows", ""),
        "centroid_lon": row.get("centroid_lon", ""),
        "centroid_lat": row.get("centroid_lat", ""),
        "window_months": months,
        "start_date": start,
        "end_date": end,
        "n_days": aggregate.get("n_days", ""),
        "precip_total_mm": aggregate.get("precip_total_mm", ""),
        "precip_mean_mm_day": aggregate.get("precip_mean_mm_day", ""),
        "temp_mean_c": aggregate.get("temp_mean_c", ""),
        "temp_max_c": aggregate.get("temp_max_c", ""),
        "temp_min_c": aggregate.get("temp_min_c", ""),
        "source": "NASA POWER daily point API fallback",
        "boundary_source": row.get("boundary_source", ""),
        "boundary_year": row.get("boundary_year", ""),
        "exposure_quality_flag": "admin2_bbox_centroid_nasa_power_stress_test_not_promoted",
        "primary_chirps_ready": "0",
        "primary_era5_ready": "0",
        "historical_baseline_ready": "0",
        "climate_linkage_ready": "0",
        "promotion_status": PROMOTION_STATUS,
        "blocking_reason": blocking_reason() if api_status != "failed_no_centroid" else "No centroid was available for this district-month row.",
    }


def audit_row(check_id: str, label: str, status: str, rows_checked: int, passing: int, evidence: str, block: str, next_action: str) -> dict[str, str]:
    return {
        "check_id": check_id,
        "check_label": label,
        "status": status,
        "rows_checked": str(rows_checked),
        "passing_rows": str(passing),
        "failing_rows": str(max(rows_checked - passing, 0)),
        "evidence": evidence,
        "promotion_ready_rows": "0",
        "blocking_reason": block,
        "next_action": next_action,
    }


def build_audit(inputs: list[dict[str, Any]], exposures: list[dict[str, Any]], manifest: list[dict[str, str]], boundary_summary: list[dict[str, str]]) -> list[dict[str, str]]:
    boundary_year = metric_value(boundary_summary, "alb2002_boundary_geometry_metadata_boundary_year", "missing")
    hist_ready = safe_int(metric_value(boundary_summary, "alb2002_boundary_geometry_historical_2002_boundary_ready_rows"))
    exposure_rows = len(exposures)
    nonmissing_precip = sum(1 for row in exposures if str(row.get("precip_total_mm", "")).strip() != "")
    nonmissing_temp = sum(1 for row in exposures if str(row.get("temp_mean_c", "")).strip() != "")
    api_ok = sum(1 for row in manifest if row.get("api_status") in {"downloaded", "cached"})
    return [
        audit_row("input_join", "Observed ALB_2002 district-month rows are matched to candidate centroids", "complete_candidate_not_promoted", len(inputs), sum(1 for row in inputs if row.get("centroid_lon") and row.get("centroid_lat")), f"input_rows={len(inputs)}; districts={len(set(row['district_code'] for row in inputs))}", blocking_reason(), "Resolve verified historical district boundary or GPS evidence before promotion."),
        audit_row("nasa_power_api", "NASA POWER daily fallback data are cached by candidate district centroid", "complete_candidate_not_promoted" if api_ok == len(manifest) else "partial_or_failed", len(manifest), api_ok, f"api_manifest_rows={len(manifest)}; ok={api_ok}; failed={len(manifest) - api_ok}", "NASA POWER is a fallback source and point centroid extraction is not the primary CHIRPS/ERA5 climate specification.", "Use CHIRPS rainfall and ERA5-Land temperature after geography is verified; retain NASA POWER as fallback/validation."),
        audit_row("window_exposures", "Exposure windows are computed for observed district-month centroids", "complete_candidate_not_promoted" if exposure_rows and nonmissing_precip == exposure_rows and nonmissing_temp == exposure_rows else "partial_or_failed", exposure_rows, min(nonmissing_precip, nonmissing_temp), f"exposure_rows={exposure_rows}; precip_nonmissing={nonmissing_precip}; temp_nonmissing={nonmissing_temp}; windows={';'.join(str(w) for w in WINDOWS_MONTHS)}", "Historical anomaly baselines, CHIRPS/ERA5 primary metrics, and verified geography are missing.", "Compute z-scores/percentiles only after accepted geography and historical climate baselines are available."),
        audit_row("boundary_vintage", "Boundary vintage gate for ALB_2002 climate linkage", "blocked", 1, hist_ready, f"boundary_year={boundary_year}; historical_2002_boundary_ready_rows={hist_ready}", "Candidate geometry metadata reports boundaryYear 2013, not verified 2002 LSMS district geography.", "Obtain or verify official 2001/2002 district boundary/GPS/EA-map evidence before climate-linkage promotion."),
        audit_row("promotion", "Climate exposure promotion to data remains blocked", "blocked", exposure_rows, 0, f"temp_exposure_rows={exposure_rows}; data_write_ready_rows=0; decision={DECISION}", blocking_reason(), "Do not write data/climate_exposures_* or data/climate_linked_household until geography, source, baseline, and outcome gates pass."),
    ]


def summary_row(metric: str, value: Any, interpretation: str) -> dict[str, str]:
    return {"metric": metric, "value": str(value), "interpretation": interpretation}


def build_summary(inputs: list[dict[str, Any]], exposures: list[dict[str, Any]], manifest: list[dict[str, str]], boundary_summary: list[dict[str, str]]) -> list[dict[str, str]]:
    api_downloaded = sum(1 for row in manifest if row.get("api_status") == "downloaded")
    api_cached = sum(1 for row in manifest if row.get("api_status") == "cached")
    api_failed = sum(1 for row in manifest if row.get("api_status") == "failed")
    return [
        summary_row("alb2002_climate_centroid_input_rows", len(inputs), "Observed ALB_2002 district-month rows with candidate centroid inputs."),
        summary_row("alb2002_climate_centroid_distinct_district_rows", len(set(row["district_code"] for row in inputs)), "Distinct ALB_2002 districts represented in the centroid stress test."),
        summary_row("alb2002_climate_centroid_household_rows_covered", sum(safe_int(row.get("household_rows")) for row in inputs), "Household rows represented across district-month input cells."),
        summary_row("alb2002_climate_centroid_exposure_rows", len(exposures), "Temp-only NASA POWER district-centroid exposure candidate rows."),
        summary_row("alb2002_climate_centroid_window_rows", len(WINDOWS_MONTHS), "Exposure window definitions computed per district-month."),
        summary_row("alb2002_climate_centroid_nasa_api_rows", len(manifest), "NASA POWER API/cache manifest rows."),
        summary_row("alb2002_climate_centroid_nasa_downloaded_rows", api_downloaded, "NASA POWER responses downloaded in this run."),
        summary_row("alb2002_climate_centroid_nasa_cached_rows", api_cached, "NASA POWER responses reused from local cache."),
        summary_row("alb2002_climate_centroid_nasa_failed_rows", api_failed, "NASA POWER responses that failed."),
        summary_row("alb2002_climate_centroid_precip_nonmissing_rows", sum(1 for row in exposures if str(row.get("precip_total_mm", "")).strip() != ""), "Exposure rows with nonmissing precipitation totals."),
        summary_row("alb2002_climate_centroid_temp_nonmissing_rows", sum(1 for row in exposures if str(row.get("temp_mean_c", "")).strip() != ""), "Exposure rows with nonmissing mean temperature."),
        summary_row("alb2002_climate_centroid_boundary_year", metric_value(boundary_summary, "alb2002_boundary_geometry_metadata_boundary_year", "missing"), "Boundary year from candidate geoBoundaries companion metadata."),
        summary_row("alb2002_climate_centroid_historical_boundary_ready_rows", metric_value(boundary_summary, "alb2002_boundary_geometry_historical_2002_boundary_ready_rows", "0"), "Rows ready as historical 2002 boundaries; should remain zero."),
        summary_row("alb2002_climate_centroid_primary_chirps_ready_rows", 0, "Rows with primary CHIRPS rainfall extraction accepted; intentionally zero."),
        summary_row("alb2002_climate_centroid_primary_era5_ready_rows", 0, "Rows with primary ERA5-Land temperature extraction accepted; intentionally zero."),
        summary_row("alb2002_climate_centroid_historical_baseline_ready_rows", 0, "Rows with historical climate anomaly baselines accepted; intentionally zero."),
        summary_row("alb2002_climate_centroid_climate_linkage_ready_rows", 0, "Rows ready for promoted climate linkage; intentionally zero."),
        summary_row("alb2002_climate_centroid_data_write_ready_rows", 0, "Rows allowed to be written to data/ by this audit; intentionally zero."),
        summary_row("alb2002_climate_centroid_current_decision", DECISION, "Current fail-closed climate centroid exposure decision."),
    ]


def markdown_table(rows: list[dict[str, Any]], columns: list[str], max_rows: int | None = None) -> str:
    selected = rows if max_rows is None else rows[:max_rows]
    lines = ["| " + " | ".join(columns) + " |", "|" + "|".join("---" for _ in columns) + "|"]
    for row in selected:
        values = []
        for col in columns:
            value = str(row.get(col, "")).replace("|", "/")
            if len(value) > 150:
                value = value[:147] + "..."
            values.append(value)
        lines.append("| " + " | ".join(values) + " |")
    return "\n".join(lines)


def write_report(summary: list[dict[str, str]], audit: list[dict[str, str]], manifest: list[dict[str, str]]) -> None:
    REPORT_PATH.write_text(
        f"""# ALB_2002 Climate Centroid Exposure Candidate Audit

Status: temp-only climate stress-test. This audit uses candidate district bounding-box centroids from the local geoBoundaries 2.0.1 ADM2 snapshot and NASA POWER daily point API fallback data to compute 1, 3, 6, and 12 month exposure summaries for observed ALB_2002 district-month cells. It does not write `data/`, does not replace CHIRPS/ERA5 primary extraction, and does not promote climate linkage.

## Summary

{markdown_table(summary, ['metric', 'value', 'interpretation'])}

## Readiness Audit

{markdown_table(audit, ['check_id', 'status', 'rows_checked', 'passing_rows', 'promotion_ready_rows', 'evidence', 'blocking_reason'])}

## API Manifest Preview

{markdown_table(manifest, ['district_code', 'district_name', 'centroid_lon', 'centroid_lat', 'start_date', 'end_date', 'api_status'], 20)}

## Interpretation

- The stress test confirms that climate summaries can be computed mechanically for the observed ALB_2002 district-month cells.
- The outputs remain candidate evidence only: the centroid geometry is not verified as 2001/2002 LSMS district geography, and NASA POWER is a fallback source.
- Primary CHIRPS rainfall, ERA5-Land temperature, historical z-score/percentile baselines, and climate-linkage promotion remain unresolved.

## Machine-Readable Outputs

- `temp/alb2002_climate_centroid_exposure_input.csv`
- `temp/alb2002_climate_centroid_exposure_candidates.csv`
- `temp/alb2002_climate_centroid_nasa_power_api_manifest.csv`
- `result/alb2002_climate_centroid_exposure_audit.csv`
- `result/alb2002_climate_centroid_exposure_summary.csv`
""",
        encoding="utf-8",
    )


def main() -> None:
    ensure_dirs()
    if not ANALYSIS_CANDIDATE_PATH.exists():
        raise FileNotFoundError(f"Missing required input: {ANALYSIS_CANDIDATE_PATH}")
    if not BOUNDARY_GEOMETRY_PATH.exists():
        raise FileNotFoundError(f"Missing required input: {BOUNDARY_GEOMETRY_PATH}")

    analysis = pd.read_csv(ANALYSIS_CANDIDATE_PATH, dtype=str)
    geometry = pd.read_csv(BOUNDARY_GEOMETRY_PATH, dtype=str)
    boundary_summary = read_csv_dicts(BOUNDARY_SUMMARY_PATH)
    inputs = build_input_rows(analysis, geometry, boundary_summary)
    exposures, manifest = build_exposures(inputs)
    audit = build_audit(inputs, exposures, manifest, boundary_summary)
    summary = build_summary(inputs, exposures, manifest, boundary_summary)

    write_csv(INPUT_PATH, inputs, INPUT_COLUMNS)
    write_csv(EXPOSURE_PATH, exposures, EXPOSURE_COLUMNS)
    write_csv(API_MANIFEST_PATH, manifest, API_COLUMNS)
    write_csv(AUDIT_PATH, audit, AUDIT_COLUMNS)
    write_csv(SUMMARY_PATH, summary, SUMMARY_COLUMNS)
    write_report(summary, audit, manifest)
    append_log(TEMP_DIR / "audit_log.md", f"Built ALB_2002 climate centroid exposure candidates rows={len(exposures)} decision={DECISION}.")
    print(f"ALB_2002 climate centroid exposure candidates rows={len(exposures)} decision={DECISION}.")


if __name__ == "__main__":
    main()
