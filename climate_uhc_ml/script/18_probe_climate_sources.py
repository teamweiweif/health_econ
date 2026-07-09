from __future__ import annotations

import csv
import json
import re
from collections import Counter
from pathlib import Path
from urllib.parse import urlparse

import requests

from common import PROJECT_ROOT, REPORT_DIR, SNAPSHOT_DIR, TEMP_DIR, append_log, ensure_dirs, sha256_file, utc_now_iso, write_csv


USER_AGENT = "Codex climate_uhc_ml climate source probe"
MAX_SNAPSHOT_BYTES = 1024 * 1024
SNAPSHOT_DIR = SNAPSHOT_DIR / "climate_sources"
PROBE_PATH = TEMP_DIR / "climate_source_probe.csv"
REPORT_PATH = REPORT_DIR / "climate_source_probe.md"

NASA_POWER_API = "https://power.larc.nasa.gov/api/temporal/daily/point"
NASA_POWER_PARAMS = {
    "parameters": "PRECTOTCORR,T2M,T2M_MAX,T2M_MIN",
    "community": "AG",
    "longitude": "38.76000",
    "latitude": "9.01000",
    "start": "20210701",
    "end": "20210703",
    "format": "JSON",
}

SOURCE_ROWS = [
    {
        "source_name": "CHIRPS precipitation documentation",
        "source_role": "primary_rainfall_documentation",
        "official_url": "https://www.chc.ucsb.edu/data/chirps",
        "expected_use": "Primary rainfall documentation for CHIRPS precipitation.",
        "unit_notes": "CHIRPS precipitation is used as rainfall in mm; confirm file-level units during extraction.",
        "probe_kind": "page",
    },
    {
        "source_name": "CHIRPS 2.0 global daily directory",
        "source_role": "primary_rainfall_data_directory",
        "official_url": "https://data.chc.ucsb.edu/products/CHIRPS-2.0/global_daily/",
        "expected_use": "Primary daily rainfall file directory.",
        "unit_notes": "Do not download bulk files in this probe; verify daily file units before analysis.",
        "probe_kind": "page",
    },
    {
        "source_name": "ERA5-Land reanalysis",
        "source_role": "primary_temperature_documentation",
        "official_url": "https://cds.climate.copernicus.eu/datasets/reanalysis-era5-land",
        "expected_use": "Primary temperature/source reanalysis documentation.",
        "unit_notes": "ERA5-family temperatures are commonly Kelvin in raw products; convert only after metadata verification.",
        "probe_kind": "page",
    },
    {
        "source_name": "ERA5-Land daily statistics",
        "source_role": "primary_daily_temperature_documentation",
        "official_url": "https://cds.climate.copernicus.eu/datasets/derived-era5-land-daily-statistics",
        "expected_use": "Daily temperature/statistics source documentation.",
        "unit_notes": "Daily-statistics units depend on selected variable/statistic; verify request metadata.",
        "probe_kind": "page",
    },
    {
        "source_name": "NASA POWER daily API documentation",
        "source_role": "rapid_point_fallback_documentation",
        "official_url": "https://power.larc.nasa.gov/docs/services/api/temporal/daily/",
        "expected_use": "Fallback point extraction documentation.",
        "unit_notes": "API response metadata must be recorded with extracted variables.",
        "probe_kind": "page",
    },
    {
        "source_name": "NASA POWER daily API smoke test",
        "source_role": "rapid_point_fallback_api",
        "official_url": NASA_POWER_API,
        "expected_use": "Small point API smoke test for precipitation and temperature variables.",
        "unit_notes": "PRECTOTCORR, T2M, T2M_MAX, and T2M_MIN are validated from a small JSON response only.",
        "probe_kind": "nasa_power_api",
    },
    {
        "source_name": "TerraClimate documentation",
        "source_role": "water_balance_robustness_documentation",
        "official_url": "https://www.climatologylab.org/terraclimate.html",
        "expected_use": "Monthly water-balance robustness documentation.",
        "unit_notes": "Water-balance variables require variable-specific unit checks before use.",
        "probe_kind": "page",
    },
    {
        "source_name": "TerraClimate Earth Engine catalog",
        "source_role": "water_balance_robustness_catalog",
        "official_url": "https://developers.google.com/earth-engine/datasets/catalog/IDAHO_EPSCOR_TERRACLIMATE",
        "expected_use": "Catalog metadata for TerraClimate robustness extraction.",
        "unit_notes": "Catalog units/scales must be honored when extracting from Earth Engine or mirrored data.",
        "probe_kind": "page",
    },
    {
        "source_name": "SPEI Global Drought Monitor",
        "source_role": "drought_robustness_documentation",
        "official_url": "https://spei.csic.es/map/",
        "expected_use": "SPEI drought robustness documentation and map endpoint.",
        "unit_notes": "SPEI is standardized drought index; use only after temporal scale and baseline are documented.",
        "probe_kind": "page",
    },
]

PROBE_COLUMNS = [
    "probe_time",
    "source_name",
    "source_role",
    "official_url",
    "final_url",
    "probe_kind",
    "http_status",
    "content_type",
    "content_length",
    "status",
    "saved_path",
    "sha256",
    "expected_use",
    "unit_notes",
    "parsed_units_or_parameters",
    "notes",
]


def safe_name(text: str) -> str:
    return re.sub(r"[^A-Za-z0-9._-]+", "_", text).strip("_").lower()[:120] or "climate_source"


def snapshot_suffix(url: str, content_type: str, probe_kind: str) -> str:
    if probe_kind == "nasa_power_api":
        return ".json"
    suffix = Path(urlparse(url).path).suffix.lower()
    if suffix and len(suffix) <= 8:
        return suffix
    if "json" in content_type.lower():
        return ".json"
    return ".html"


def write_limited_snapshot(response: requests.Response, source_name: str, probe_kind: str) -> tuple[str, str, str]:
    suffix = snapshot_suffix(response.url, response.headers.get("content-type", ""), probe_kind)
    path = SNAPSHOT_DIR / f"{safe_name(source_name)}{suffix}"
    path.parent.mkdir(parents=True, exist_ok=True)
    chunks: list[bytes] = []
    total = 0
    for chunk in response.iter_content(chunk_size=64 * 1024):
        if not chunk:
            continue
        total += len(chunk)
        if total > MAX_SNAPSHOT_BYTES:
            break
        chunks.append(chunk)
    path.write_bytes(b"".join(chunks))
    note = "snapshot_truncated_to_1mb" if total > MAX_SNAPSHOT_BYTES else ""
    return str(path.relative_to(PROJECT_ROOT)).replace("\\", "/"), sha256_file(path), note


def parse_nasa_units(data: dict) -> str:
    parameters = data.get("properties", {}).get("parameter", {})
    observed = []
    for name in ["PRECTOTCORR", "T2M", "T2M_MAX", "T2M_MIN"]:
        values = parameters.get(name, {})
        observed.append(f"{name}:days={len(values)}")
    header = data.get("header", {})
    units = header.get("parameters") or header.get("units") or ""
    if units:
        observed.append(f"header_units={units}")
    return "; ".join(observed)


def probe_row(source: dict[str, str]) -> dict[str, str]:
    url = source["official_url"]
    params = NASA_POWER_PARAMS if source["probe_kind"] == "nasa_power_api" else None
    base = {
        "probe_time": utc_now_iso(),
        "source_name": source["source_name"],
        "source_role": source["source_role"],
        "official_url": url,
        "final_url": "",
        "probe_kind": source["probe_kind"],
        "http_status": "",
        "content_type": "",
        "content_length": "",
        "status": "",
        "saved_path": "",
        "sha256": "",
        "expected_use": source["expected_use"],
        "unit_notes": source["unit_notes"],
        "parsed_units_or_parameters": "",
        "notes": "",
    }
    try:
        with requests.get(
            url,
            params=params,
            headers={"User-Agent": USER_AGENT},
            timeout=90,
            stream=True,
            allow_redirects=True,
        ) as response:
            base["final_url"] = response.url
            base["http_status"] = str(response.status_code)
            base["content_type"] = response.headers.get("content-type", "")
            base["content_length"] = response.headers.get("content-length", "")
            if response.status_code != 200:
                base["status"] = "failed_http"
                base["notes"] = f"HTTP {response.status_code}"
                return base
            saved_path, digest, note = write_limited_snapshot(response, source["source_name"], source["probe_kind"])
            base["saved_path"] = saved_path
            base["sha256"] = digest
            base["notes"] = note
            if source["probe_kind"] == "nasa_power_api":
                data = json.loads((PROJECT_ROOT / saved_path).read_text(encoding="utf-8"))
                parsed = parse_nasa_units(data)
                if all(token in parsed for token in ["PRECTOTCORR", "T2M", "T2M_MAX", "T2M_MIN"]):
                    base["status"] = "pass_api_parameters_present"
                else:
                    base["status"] = "failed_api_missing_parameters"
                base["parsed_units_or_parameters"] = parsed
            else:
                base["status"] = "reachable_snapshot_saved"
            return base
    except Exception as exc:
        base["status"] = "failed_request"
        base["notes"] = str(exc)
        return base


def markdown_count_table(counter: Counter[str], key_name: str) -> str:
    lines = [f"| {key_name} | Count |", "|---|---:|"]
    for key, count in counter.most_common():
        lines.append(f"| {key or 'blank'} | {count} |")
    return "\n".join(lines)


def write_report(rows: list[dict[str, str]]) -> None:
    status_counts = Counter(row.get("status", "") for row in rows)
    role_counts = Counter(row.get("source_role", "") for row in rows)
    lines = [
        "# Climate Source Probe",
        "",
        "Status: official climate source endpoints were probed with small documentation/API snapshots. This is source-readiness evidence only; it does not construct household climate exposure data.",
        "",
        "## Status Counts",
        "",
        markdown_count_table(status_counts, "Status"),
        "",
        "## Source Roles",
        "",
        markdown_count_table(role_counts, "Source role"),
        "",
        "## Sources",
        "",
        "| Source | Role | Status | Saved snapshot | Unit notes |",
        "|---|---|---|---|---|",
    ]
    for row in rows:
        lines.append(
            "| {source} | {role} | {status} | `{saved}` | {units} |".format(
                source=row.get("source_name", "").replace("|", "/"),
                role=row.get("source_role", ""),
                status=row.get("status", ""),
                saved=row.get("saved_path", ""),
                units=row.get("unit_notes", "").replace("|", "/"),
            )
        )
    lines.extend(
        [
            "",
            "## Guardrail",
            "",
            "CHIRPS, ERA5-Land, TerraClimate, SPEI, and NASA POWER are not interchangeable. The analytical pipeline must still verify variable-specific units, temporal aggregation, historical baselines, and point/admin geospatial linkage after raw household geography and timing are available.",
        ]
    )
    REPORT_PATH.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    ensure_dirs()
    SNAPSHOT_DIR.mkdir(parents=True, exist_ok=True)
    rows = [probe_row(source) for source in SOURCE_ROWS]
    write_csv(PROBE_PATH, rows, PROBE_COLUMNS)
    write_report(rows)
    passed = sum(1 for row in rows if row.get("status") in {"reachable_snapshot_saved", "pass_api_parameters_present"})
    append_log(TEMP_DIR / "audit_log.md", f"Climate source probe checked {len(rows)} endpoints; pass_or_reachable={passed}.")
    print(f"Climate source probe endpoints={len(rows)} pass_or_reachable={passed}")


if __name__ == "__main__":
    main()
