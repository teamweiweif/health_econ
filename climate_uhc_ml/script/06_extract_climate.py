from __future__ import annotations

import argparse
import csv
import hashlib
import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any

import pandas as pd
import requests
from dateutil.relativedelta import relativedelta

from common import DATA_DIR, REPORT_DIR, TEMP_DIR, append_log, ensure_dirs, write_csv


NASA_POWER_URL = "https://power.larc.nasa.gov/api/temporal/daily/point"
NASA_PARAMETERS = ["PRECTOTCORR", "T2M", "T2M_MAX", "T2M_MIN"]
DEFAULT_WINDOWS_MONTHS = [1, 3, 6, 12]

INPUT_CANDIDATES = [
    DATA_DIR / "climate_linkage_input.csv",
    DATA_DIR / "climate_linkage_input.parquet",
    DATA_DIR / "harmonized_household.csv",
    DATA_DIR / "harmonized_household.parquet",
    DATA_DIR / "household_panel.csv",
    DATA_DIR / "household_panel.parquet",
]

TEMPLATE_COLUMNS = [
    "country",
    "survey_name",
    "wave",
    "hhid",
    "pid",
    "cluster_id",
    "latitude",
    "longitude",
    "geolocation_quality",
    "interview_date",
    "survey_year",
    "survey_month",
    "household_weight",
    "notes",
]

AUDIT_COLUMNS = [
    "check",
    "status",
    "detail",
    "input_path",
    "rows",
    "valid_rows",
    "output_path",
]

EXPOSURE_COLUMNS = [
    "country",
    "survey_name",
    "wave",
    "hhid",
    "pid",
    "cluster_id",
    "latitude",
    "longitude",
    "geolocation_quality",
    "interview_date",
    "source",
    "window_months",
    "start_date",
    "end_date",
    "n_days",
    "precip_total_mm",
    "precip_mean_mm_day",
    "temp_mean_c",
    "temp_max_c",
    "temp_min_c",
    "api_status",
    "quality_flag",
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Extract climate exposures for verified household/cluster coordinates.")
    parser.add_argument("--input", type=Path, default=None, help="Input CSV/Parquet with coordinates and interview timing.")
    parser.add_argument("--limit", type=int, default=0, help="Optional limit on unique point-date rows for testing.")
    parser.add_argument("--smoke-test", action="store_true", help="Run a small NASA POWER API smoke test even if no input exists.")
    return parser.parse_args()


def write_template() -> None:
    template = TEMP_DIR / "climate_linkage_input_template.csv"
    if not template.exists():
        write_csv(
            template,
            [
                {
                    "country": "Exampleland",
                    "survey_name": "Example household survey",
                    "wave": "2021",
                    "hhid": "HH001",
                    "pid": "",
                    "cluster_id": "C001",
                    "latitude": "9.01",
                    "longitude": "38.76",
                    "geolocation_quality": "exact_or_displaced_cluster_point",
                    "interview_date": "2021-07-15",
                    "survey_year": "",
                    "survey_month": "",
                    "household_weight": "",
                    "notes": "Example only; replace with verified survey coordinates and timing.",
                }
            ],
            TEMPLATE_COLUMNS,
        )


def find_input(explicit: Path | None) -> Path | None:
    if explicit:
        return explicit if explicit.exists() else None
    for path in INPUT_CANDIDATES:
        if path.exists():
            return path
    return None


def read_input(path: Path) -> pd.DataFrame:
    if path.suffix.lower() == ".parquet":
        return pd.read_parquet(path)
    return pd.read_csv(path)


def normalize_date(row: pd.Series) -> pd.Timestamp | None:
    if "interview_date" in row and pd.notna(row["interview_date"]) and str(row["interview_date"]).strip():
        parsed = pd.to_datetime(row["interview_date"], errors="coerce")
        if pd.notna(parsed):
            return parsed.normalize()
    year = row.get("survey_year", None)
    month = row.get("survey_month", None)
    if pd.notna(year) and pd.notna(month):
        try:
            return pd.Timestamp(year=int(float(year)), month=int(float(month)), day=15)
        except Exception:
            return None
    return None


def validate_input(df: pd.DataFrame) -> tuple[pd.DataFrame, list[str]]:
    problems = []
    lower_cols = {c.lower(): c for c in df.columns}
    required = ["latitude", "longitude"]
    missing = [c for c in required if c not in lower_cols]
    if missing:
        problems.append(f"missing required columns: {', '.join(missing)}")
        return pd.DataFrame(), problems

    df = df.rename(columns={lower_cols[c]: c for c in lower_cols})
    for col in TEMPLATE_COLUMNS:
        if col not in df.columns:
            df[col] = ""
    df["latitude"] = pd.to_numeric(df["latitude"], errors="coerce")
    df["longitude"] = pd.to_numeric(df["longitude"], errors="coerce")
    df["interview_date_resolved"] = df.apply(normalize_date, axis=1)
    valid = df[
        df["latitude"].between(-90, 90)
        & df["longitude"].between(-180, 180)
        & df["interview_date_resolved"].notna()
    ].copy()
    if valid.empty:
        problems.append("no rows have valid latitude, longitude, and interview_date or survey_year+survey_month")
    return valid, problems


def cache_key(latitude: float, longitude: float, start: str, end: str) -> str:
    raw = f"{latitude:.5f}_{longitude:.5f}_{start}_{end}_{','.join(NASA_PARAMETERS)}"
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()[:24]


def fetch_nasa_power(latitude: float, longitude: float, start: str, end: str) -> tuple[dict[str, Any] | None, str]:
    cache_dir = TEMP_DIR / "climate_cache" / "nasa_power"
    cache_dir.mkdir(parents=True, exist_ok=True)
    cache_path = cache_dir / f"{cache_key(latitude, longitude, start, end)}.json"
    if cache_path.exists():
        return json.loads(cache_path.read_text(encoding="utf-8")), "cached"

    params = {
        "parameters": ",".join(NASA_PARAMETERS),
        "community": "AG",
        "longitude": f"{longitude:.5f}",
        "latitude": f"{latitude:.5f}",
        "start": start.replace("-", ""),
        "end": end.replace("-", ""),
        "format": "JSON",
    }
    try:
        response = requests.get(NASA_POWER_URL, params=params, timeout=90)
        response.raise_for_status()
        data = response.json()
        cache_path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
        return data, "downloaded"
    except Exception as exc:
        return None, f"failed: {exc}"


def aggregate_power(data: dict[str, Any]) -> dict[str, float | int | str]:
    params = data.get("properties", {}).get("parameter", {})
    precip = pd.Series(params.get("PRECTOTCORR", {}), dtype="float64")
    tmean = pd.Series(params.get("T2M", {}), dtype="float64")
    tmax = pd.Series(params.get("T2M_MAX", {}), dtype="float64")
    tmin = pd.Series(params.get("T2M_MIN", {}), dtype="float64")
    for series in [precip, tmean, tmax, tmin]:
        series.replace(-999, pd.NA, inplace=True)
    return {
        "n_days": int(max(len(precip.dropna()), len(tmean.dropna()), len(tmax.dropna()), len(tmin.dropna()))),
        "precip_total_mm": float(precip.dropna().sum()) if not precip.dropna().empty else "",
        "precip_mean_mm_day": float(precip.dropna().mean()) if not precip.dropna().empty else "",
        "temp_mean_c": float(tmean.dropna().mean()) if not tmean.dropna().empty else "",
        "temp_max_c": float(tmax.dropna().max()) if not tmax.dropna().empty else "",
        "temp_min_c": float(tmin.dropna().min()) if not tmin.dropna().empty else "",
    }


def exposure_rows(valid: pd.DataFrame, limit: int = 0) -> list[dict[str, Any]]:
    rows = []
    cols = TEMPLATE_COLUMNS + ["interview_date_resolved"]
    unique = valid[cols].drop_duplicates(
        subset=["country", "survey_name", "wave", "hhid", "pid", "cluster_id", "latitude", "longitude", "interview_date_resolved"]
    )
    if limit:
        unique = unique.head(limit)
    for _, row in unique.iterrows():
        interview = pd.Timestamp(row["interview_date_resolved"]).date()
        end_date = interview - timedelta(days=1)
        for months in DEFAULT_WINDOWS_MONTHS:
            start_date = (pd.Timestamp(interview) - relativedelta(months=months)).date()
            start = start_date.isoformat()
            end = end_date.isoformat()
            data, api_status = fetch_nasa_power(float(row["latitude"]), float(row["longitude"]), start, end)
            agg = aggregate_power(data) if data else {
                "n_days": "",
                "precip_total_mm": "",
                "precip_mean_mm_day": "",
                "temp_mean_c": "",
                "temp_max_c": "",
                "temp_min_c": "",
            }
            quality = "nasa_power_point_exposure"
            if "displaced" in str(row.get("geolocation_quality", "")).lower():
                quality = "nasa_power_displaced_point_measurement_error"
            rows.append(
                {
                    "country": row.get("country", ""),
                    "survey_name": row.get("survey_name", ""),
                    "wave": row.get("wave", ""),
                    "hhid": row.get("hhid", ""),
                    "pid": row.get("pid", ""),
                    "cluster_id": row.get("cluster_id", ""),
                    "latitude": row.get("latitude", ""),
                    "longitude": row.get("longitude", ""),
                    "geolocation_quality": row.get("geolocation_quality", ""),
                    "interview_date": interview.isoformat(),
                    "source": "NASA POWER daily point API",
                    "window_months": months,
                    "start_date": start,
                    "end_date": end,
                    "api_status": api_status,
                    "quality_flag": quality,
                    **agg,
                }
            )
    return rows


def run_smoke_test() -> dict[str, str]:
    data, status = fetch_nasa_power(9.01, 38.76, "2021-07-01", "2021-07-07")
    ok = data is not None and "properties" in data
    row = {
        "check": "nasa_power_api_smoke_test",
        "status": "pass" if ok else "fail",
        "detail": status,
        "input_path": "",
        "rows": "",
        "valid_rows": "",
        "output_path": "",
    }
    write_csv(TEMP_DIR / "climate_source_smoke_test.csv", [row], AUDIT_COLUMNS)
    return row


def write_audit(rows: list[dict[str, str]]) -> None:
    write_csv(TEMP_DIR / "climate_extraction_audit.csv", rows, AUDIT_COLUMNS)


def write_report(audit_rows: list[dict[str, str]], exposure_count: int) -> None:
    status_line = "; ".join(f"{r['check']}={r['status']}" for r in audit_rows)
    report = f"""# Climate Linkage Audit

Status: climate extraction scaffold implemented. Current extraction status: {status_line or 'not run'}.

## Implemented Extraction Path

- NASA POWER daily point API fallback is implemented in `script/06_extract_climate.py`.
- Supported input files are `data/climate_linkage_input.csv`, `data/climate_linkage_input.parquet`, `data/harmonized_household.*`, or `data/household_panel.*`.
- Required fields are `latitude`, `longitude`, and either `interview_date` or `survey_year` plus `survey_month`.
- The script writes `data/climate_exposures_nasa_power.csv` only when valid input rows exist.
- It always writes `temp/climate_extraction_audit.csv` and `temp/climate_linkage_input_template.csv`.

## Current Output

Climate exposure rows written: {exposure_count}

## Limitations

- NASA POWER is a fallback point-extraction source, not the preferred final rainfall source.
- CHIRPS rainfall and ERA5-Land temperature remain the intended primary/robustness sources once verified coordinates and geospatial dependencies are available.
- No exact household coordinates should be assumed. Displaced GPS or admin-only locations must be flagged and downgraded.
- Z-scores, percentiles, dry days, and heatwave metrics require historical baselines and are not claimed by the current fallback extractor.
"""
    (REPORT_DIR / "climate_linkage_audit.md").write_text(report, encoding="utf-8")


def main() -> None:
    ensure_dirs()
    args = parse_args()
    write_template()
    audit_rows: list[dict[str, str]] = []
    input_path = find_input(args.input)
    if args.smoke_test:
        audit_rows.append(run_smoke_test())
    if input_path is None:
        audit_rows.append(
            {
                "check": "climate_input",
                "status": "blocked_no_harmonized_geography_timing_input",
                "detail": "No climate linkage input found in data/. Use temp/climate_linkage_input_template.csv after raw-data harmonization.",
                "input_path": "",
                "rows": "0",
                "valid_rows": "0",
                "output_path": "",
            }
        )
        write_audit(audit_rows)
        write_report(audit_rows, 0)
        append_log(TEMP_DIR / "audit_log.md", "Climate extraction scaffold ready; no harmonized geography/timing input found.")
        print("Climate extraction scaffold ready; no harmonized geography/timing input found.")
        return

    df = read_input(input_path)
    valid, problems = validate_input(df)
    if problems:
        audit_rows.append(
            {
                "check": "climate_input_validation",
                "status": "failed",
                "detail": "; ".join(problems),
                "input_path": str(input_path.relative_to(TEMP_DIR.parent)),
                "rows": str(len(df)),
                "valid_rows": str(len(valid)),
                "output_path": "",
            }
        )
        write_audit(audit_rows)
        write_report(audit_rows, 0)
        append_log(TEMP_DIR / "audit_log.md", f"Climate extraction input validation failed: {'; '.join(problems)}")
        print(f"Climate extraction input validation failed: {'; '.join(problems)}")
        return

    rows = exposure_rows(valid, args.limit)
    output = DATA_DIR / "climate_exposures_nasa_power.csv"
    write_csv(output, rows, EXPOSURE_COLUMNS)
    audit_rows.append(
        {
            "check": "nasa_power_extraction",
            "status": "complete" if rows else "no_rows",
            "detail": "NASA POWER point fallback exposures generated; primary CHIRPS/ERA5 still pending.",
            "input_path": str(input_path.relative_to(TEMP_DIR.parent)),
            "rows": str(len(df)),
            "valid_rows": str(len(valid)),
            "output_path": str(output.relative_to(TEMP_DIR.parent)),
        }
    )
    write_audit(audit_rows)
    write_report(audit_rows, len(rows))
    append_log(TEMP_DIR / "audit_log.md", f"Climate extraction wrote {len(rows)} NASA POWER exposure rows.")
    print(f"Climate extraction wrote {len(rows)} NASA POWER exposure rows.")


if __name__ == "__main__":
    main()
