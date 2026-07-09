from __future__ import annotations

import csv
import io
import json
import re
import time
import zipfile
from collections import Counter
from pathlib import Path
from urllib.parse import urlparse

import requests
import pandas as pd

from common import PROJECT_ROOT, REPORT_DIR, SNAPSHOT_DIR, TEMP_DIR, append_log, ensure_dirs, sha256_file, utc_now_iso, write_csv


USER_AGENT = "Codex climate_uhc_ml validation reference probe"
SNAPSHOT_DIR = SNAPSHOT_DIR / "validation_reference_sources"
MAX_SNAPSHOT_BYTES = 2 * 1024 * 1024
REQUEST_RETRIES = 3

PROBE_PATH = TEMP_DIR / "validation_reference_source_probe.csv"
INDICATOR_SAMPLE_PATH = TEMP_DIR / "validation_reference_indicator_sample.csv"
HEFPI_UHC_SERIES_PATH = TEMP_DIR / "hefpi_uhc_series_catalog.csv"
HEFPI_UHC_REFERENCE_PATH = TEMP_DIR / "hefpi_uhc_reference_sample.csv"
REPORT_PATH = REPORT_DIR / "validation_reference_sources.md"

WORLD_BANK_INDICATOR_API = "https://api.worldbank.org/v2/indicator/{indicator}"
WORLD_BANK_DATA_API = "https://api.worldbank.org/v2/country/{countries}/indicator/{indicator}"

SOURCE_ROWS = [
    {
        "source_name": "World Bank HEFPI portal",
        "source_role": "country_validation_portal",
        "official_url": "https://datatopics.worldbank.org/health-equity-and-financial-protection/",
        "probe_kind": "page",
        "expected_use": "Country-level validation source for financial protection estimates where comparable indicators exist.",
        "unit_or_definition_note": "Use for external validation only; microdata outcome construction remains source survey based.",
    },
    {
        "source_name": "World Bank HEFPI data catalog record",
        "source_role": "country_validation_catalog",
        "official_url": "https://datacatalog.worldbank.org/search/dataset/0038633",
        "probe_kind": "page",
        "expected_use": "Catalog record linked from the HEFPI portal for downloadable/reference data discovery.",
        "unit_or_definition_note": "Catalog/download formats must be verified before using as validation data.",
    },
    {
        "source_name": "World Bank HEFPI source 65 indicator API",
        "source_role": "hefpi_indicator_api_catalog",
        "official_url": "https://api.worldbank.org/v2/source/65/Indicators",
        "probe_kind": "page",
        "expected_use": "HEFPI-specific indicator catalog linked from the World Bank data catalog.",
        "unit_or_definition_note": "Use to identify HEFPI-specific financial-protection indicator codes.",
    },
    {
        "source_name": "World Bank HEFPI bulk CSV download",
        "source_role": "hefpi_bulk_csv_reference",
        "official_url": "https://databank.worldbank.org/data/download/HEFPI_CSV.zip",
        "probe_kind": "download",
        "expected_use": "Public aggregate HEFPI reference data for CHE/impoverishment validation where comparable.",
        "unit_or_definition_note": "Aggregate country-year validation data only; not household microdata.",
    },
]

INDICATOR_ROWS = [
    {
        "indicator": "SH.UHC.OOPC.10.ZS",
        "source_role": "che10_country_validation",
        "expected_use": "External comparison for CHE10 total-budget outcome.",
        "unit_or_definition_note": "Population spending more than 10% of household consumption or income on OOP health care expenditure.",
    },
    {
        "indicator": "SH.UHC.OOPC.25.ZS",
        "source_role": "che25_country_validation",
        "expected_use": "External comparison for CHE25 total-budget outcome.",
        "unit_or_definition_note": "Population spending more than 25% of household consumption or income on OOP health care expenditure.",
    },
    {
        "indicator": "SH.XPD.OOPC.CH.ZS",
        "source_role": "oop_macro_context",
        "expected_use": "Country macro context for OOP share of current health expenditure; not a household catastrophic-spending validation.",
        "unit_or_definition_note": "Out-of-pocket expenditure as percentage of current health expenditure.",
    },
    {
        "indicator": "SH.XPD.OOPC.PC.CD",
        "source_role": "oop_macro_context",
        "expected_use": "Country macro context for OOP per-capita spending in current US dollars.",
        "unit_or_definition_note": "Not a substitute for household OOP variable construction.",
    },
    {
        "indicator": "SH.XPD.OOPC.PP.CD",
        "source_role": "oop_macro_context",
        "expected_use": "Country macro context for OOP per-capita spending in current international dollars.",
        "unit_or_definition_note": "Not a substitute for household OOP variable construction.",
    },
    {
        "indicator": "SI.POV.DDAY",
        "source_role": "poverty_line_context",
        "expected_use": "Poverty-line context for SDG 3.8.2 denominator feasibility.",
        "unit_or_definition_note": "WDI poverty headcount at $3.00/day 2021 PPP; not the household-level societal poverty line by itself.",
    },
    {
        "indicator": "PA.NUS.PRVT.PP",
        "source_role": "ppp_conversion_context",
        "expected_use": "PPP conversion factor for household final consumption context.",
        "unit_or_definition_note": "LCU per international dollar; verify PPP base and compatibility with SDG metadata before denominator use.",
    },
    {
        "indicator": "FP.CPI.TOTL",
        "source_role": "cpi_context",
        "expected_use": "CPI context for within-country price adjustment if raw survey currency years require deflation.",
        "unit_or_definition_note": "Consumer price index (2010 = 100) in WDI.",
    },
]

PROBE_COLUMNS = [
    "probe_time",
    "source_name",
    "source_role",
    "probe_kind",
    "official_url",
    "final_url",
    "http_status",
    "content_type",
    "content_length",
    "status",
    "saved_path",
    "sha256",
    "indicator",
    "indicator_name",
    "indicator_source",
    "expected_use",
    "unit_or_definition_note",
    "notes",
]

SAMPLE_COLUMNS = [
    "indicator",
    "country_id",
    "countryiso3code",
    "country_name",
    "date",
    "value",
    "unit",
    "obs_status",
    "decimal",
    "source_role",
    "expected_use",
    "status",
]

HEFPI_SERIES_COLUMNS = [
    "series_code",
    "indicator_name",
    "long_definition",
    "source",
    "status",
]

HEFPI_REFERENCE_COLUMNS = [
    "country_code",
    "country_name",
    "indicator_code",
    "indicator_name",
    "year",
    "value",
    "source_role",
    "status",
]


def read_csv_dicts(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        return []
    with path.open(encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def safe_name(text: str) -> str:
    return re.sub(r"[^A-Za-z0-9._-]+", "_", text).strip("_").lower()[:120] or "validation_reference"


def suffix_for(url: str, content_type: str) -> str:
    suffix = Path(urlparse(url).path).suffix.lower()
    if suffix and len(suffix) <= 8:
        return suffix
    if "json" in content_type.lower():
        return ".json"
    return ".html"


def request_get(url: str, **kwargs) -> requests.Response:
    last_error: Exception | None = None
    for attempt in range(1, REQUEST_RETRIES + 1):
        try:
            response = requests.get(url, headers={"User-Agent": USER_AGENT}, timeout=90, allow_redirects=True, **kwargs)
            return response
        except Exception as exc:
            last_error = exc
            if attempt < REQUEST_RETRIES:
                time.sleep(min(attempt * 2, 8))
    raise RuntimeError(str(last_error))


def save_limited_response(response: requests.Response, name: str) -> tuple[str, str, str]:
    suffix = suffix_for(response.url, response.headers.get("content-type", ""))
    path = SNAPSHOT_DIR / f"{safe_name(name)}{suffix}"
    path.parent.mkdir(parents=True, exist_ok=True)
    total = 0
    chunks: list[bytes] = []
    for chunk in response.iter_content(chunk_size=64 * 1024):
        if not chunk:
            continue
        total += len(chunk)
        if total > MAX_SNAPSHOT_BYTES:
            break
        chunks.append(chunk)
    path.write_bytes(b"".join(chunks))
    note = "snapshot_truncated_to_2mb" if total > MAX_SNAPSHOT_BYTES else ""
    return str(path.relative_to(PROJECT_ROOT)).replace("\\", "/"), sha256_file(path), note


def probe_page(source: dict[str, str]) -> dict[str, str]:
    base = {
        "probe_time": utc_now_iso(),
        "source_name": source["source_name"],
        "source_role": source["source_role"],
        "probe_kind": source["probe_kind"],
        "official_url": source["official_url"],
        "final_url": "",
        "http_status": "",
        "content_type": "",
        "content_length": "",
        "status": "",
        "saved_path": "",
        "sha256": "",
        "indicator": "",
        "indicator_name": "",
        "indicator_source": "",
        "expected_use": source["expected_use"],
        "unit_or_definition_note": source["unit_or_definition_note"],
        "notes": "",
    }
    try:
        response = request_get(source["official_url"], stream=True)
        base["final_url"] = response.url
        base["http_status"] = str(response.status_code)
        base["content_type"] = response.headers.get("content-type", "")
        base["content_length"] = response.headers.get("content-length", "")
        if response.status_code != 200:
            base["status"] = "failed_http"
            base["notes"] = f"HTTP {response.status_code}"
            response.close()
            return base
        with response:
            saved_path, digest, note = save_limited_response(response, source["source_name"])
        base["status"] = "reachable_snapshot_saved"
        base["saved_path"] = saved_path
        base["sha256"] = digest
        base["notes"] = note
        return base
    except Exception as exc:
        base["status"] = "failed_request"
        base["notes"] = str(exc)
        return base


def probe_indicator(row: dict[str, str]) -> dict[str, str]:
    indicator = row["indicator"]
    url = WORLD_BANK_INDICATOR_API.format(indicator=indicator)
    base = {
        "probe_time": utc_now_iso(),
        "source_name": f"World Bank indicator {indicator}",
        "source_role": row["source_role"],
        "probe_kind": "world_bank_indicator_metadata",
        "official_url": url,
        "final_url": "",
        "http_status": "",
        "content_type": "",
        "content_length": "",
        "status": "",
        "saved_path": "",
        "sha256": "",
        "indicator": indicator,
        "indicator_name": "",
        "indicator_source": "",
        "expected_use": row["expected_use"],
        "unit_or_definition_note": row["unit_or_definition_note"],
        "notes": "",
    }
    try:
        response = request_get(url, params={"format": "json"}, stream=True)
        base["final_url"] = response.url
        base["http_status"] = str(response.status_code)
        base["content_type"] = response.headers.get("content-type", "")
        base["content_length"] = response.headers.get("content-length", "")
        if response.status_code != 200:
            base["status"] = "failed_http"
            base["notes"] = f"HTTP {response.status_code}"
            response.close()
            return base
        with response:
            saved_path, digest, note = save_limited_response(response, f"indicator_{indicator}")
        base["saved_path"] = saved_path
        base["sha256"] = digest
        base["notes"] = note
        data = json.loads((PROJECT_ROOT / saved_path).read_text(encoding="utf-8"))
        indicator_rows = data[1] if isinstance(data, list) and len(data) > 1 else []
        if indicator_rows:
            meta = indicator_rows[0]
            base["indicator_name"] = meta.get("name", "")
            source = meta.get("source", {})
            base["indicator_source"] = source.get("value", "") if isinstance(source, dict) else str(source)
            base["status"] = "indicator_metadata_available"
        else:
            base["status"] = "indicator_metadata_empty"
        return base
    except Exception as exc:
        base["status"] = "failed_request"
        base["notes"] = str(exc)
        return base


def priority_country_codes(limit: int = 20) -> list[str]:
    rows = read_csv_dicts(TEMP_DIR / "manual_download_priority.csv")
    codes: list[str] = []
    for row in rows:
        idno = row.get("idno", "")
        if len(idno) >= 3:
            code = idno[:3].upper()
            if code.isalpha() and code not in codes:
                codes.append(code)
        if len(codes) >= limit:
            break
    return codes


def sample_indicator_data(countries: list[str]) -> list[dict[str, str]]:
    if not countries:
        return []
    country_expr = ";".join(countries)
    out: list[dict[str, str]] = []
    role_by_indicator = {row["indicator"]: row for row in INDICATOR_ROWS}
    for indicator, info in role_by_indicator.items():
        url = WORLD_BANK_DATA_API.format(countries=country_expr, indicator=indicator)
        try:
            response = request_get(
                url,
                params={"format": "json", "per_page": "20000", "date": "2000:2026"},
            )
            if response.status_code != 200:
                out.append(
                    {
                        "indicator": indicator,
                        "country_id": "",
                        "countryiso3code": "",
                        "country_name": "",
                        "date": "",
                        "value": "",
                        "unit": "",
                        "obs_status": "",
                        "decimal": "",
                        "source_role": info["source_role"],
                        "expected_use": info["expected_use"],
                        "status": f"failed_http_{response.status_code}",
                    }
                )
                continue
            data = response.json()
            records = data[1] if isinstance(data, list) and len(data) > 1 else []
            if not records:
                out.append(
                    {
                        "indicator": indicator,
                        "country_id": "",
                        "countryiso3code": "",
                        "country_name": "",
                        "date": "",
                        "value": "",
                        "unit": "",
                        "obs_status": "",
                        "decimal": "",
                        "source_role": info["source_role"],
                        "expected_use": info["expected_use"],
                        "status": "no_records_returned",
                    }
                )
                continue
            for record in records:
                country = record.get("country", {})
                out.append(
                    {
                        "indicator": indicator,
                        "country_id": country.get("id", "") if isinstance(country, dict) else "",
                        "countryiso3code": record.get("countryiso3code", ""),
                        "country_name": country.get("value", "") if isinstance(country, dict) else "",
                        "date": record.get("date", ""),
                        "value": "" if record.get("value") is None else str(record.get("value")),
                        "unit": record.get("unit", ""),
                        "obs_status": record.get("obs_status", ""),
                        "decimal": str(record.get("decimal", "")),
                        "source_role": info["source_role"],
                        "expected_use": info["expected_use"],
                        "status": "sample_record",
                    }
                )
        except Exception as exc:
            out.append(
                {
                    "indicator": indicator,
                    "country_id": "",
                    "countryiso3code": "",
                    "country_name": "",
                    "date": "",
                    "value": "",
                    "unit": "",
                    "obs_status": "",
                    "decimal": "",
                    "source_role": info["source_role"],
                    "expected_use": info["expected_use"],
                    "status": f"failed_request: {exc}",
                }
            )
    return out


def parse_hefpi_uhc_reference(probe_rows: list[dict[str, str]], countries: list[str]) -> tuple[list[dict[str, str]], list[dict[str, str]]]:
    bulk_row = next((row for row in probe_rows if row.get("source_role") == "hefpi_bulk_csv_reference" and row.get("status") == "reachable_snapshot_saved"), None)
    if not bulk_row or not bulk_row.get("saved_path"):
        return (
            [
                {
                    "series_code": "",
                    "indicator_name": "",
                    "long_definition": "",
                    "source": "",
                    "status": "hefpi_bulk_csv_not_available",
                }
            ],
            [],
        )
    zip_path = PROJECT_ROOT / bulk_row["saved_path"]
    if not zip_path.exists():
        return (
            [
                {
                    "series_code": "",
                    "indicator_name": "",
                    "long_definition": "",
                    "source": "",
                    "status": "hefpi_bulk_csv_missing_after_probe",
                }
            ],
            [],
        )

    try:
        with zipfile.ZipFile(zip_path) as zf:
            series = pd.read_csv(zf.open("HEFPISeries.csv"))
            data = pd.read_csv(zf.open("HEFPIData.csv"))
    except Exception as exc:
        return (
            [
                {
                    "series_code": "",
                    "indicator_name": "",
                    "long_definition": "",
                    "source": "",
                    "status": f"hefpi_bulk_csv_parse_failed: {exc}",
                }
            ],
            [],
        )

    series_code_col = "Series Code"
    uhc_series = series[series[series_code_col].astype(str).str.startswith("HF.UHC", na=False)].copy()
    series_rows = []
    for _, row in uhc_series.iterrows():
        series_rows.append(
            {
                "series_code": str(row.get("Series Code", "")),
                "indicator_name": str(row.get("Indicator Name", "")),
                "long_definition": str(row.get("Long definition", "")),
                "source": str(row.get("Source", "")),
                "status": "hefpi_uhc_series",
            }
        )

    reference_rows = []
    if not countries or uhc_series.empty:
        return series_rows, reference_rows
    uhc_codes = set(uhc_series["Series Code"].astype(str))
    filtered = data[data["Indicator Code"].astype(str).isin(uhc_codes) & data["Country Code"].astype(str).isin(countries)].copy()
    year_columns = [col for col in filtered.columns if re.fullmatch(r"\d{4}", str(col))]
    for _, row in filtered.iterrows():
        for year in year_columns:
            value = row.get(year)
            if pd.isna(value):
                continue
            reference_rows.append(
                {
                    "country_code": str(row.get("Country Code", "")),
                    "country_name": str(row.get("Country Name", "")),
                    "indicator_code": str(row.get("Indicator Code", "")),
                    "indicator_name": str(row.get("Indicator Name", "")),
                    "year": str(year),
                    "value": str(value),
                    "source_role": "hefpi_uhc_country_validation",
                    "status": "hefpi_uhc_reference_record",
                }
            )
    return series_rows, reference_rows


def markdown_count_table(counter: Counter[str], key_name: str) -> str:
    lines = [f"| {key_name} | Count |", "|---|---:|"]
    for key, count in counter.most_common():
        lines.append(f"| {key or 'blank'} | {count} |")
    return "\n".join(lines)


def write_report(
    probe_rows: list[dict[str, str]],
    sample_rows: list[dict[str, str]],
    hefpi_series_rows: list[dict[str, str]],
    hefpi_reference_rows: list[dict[str, str]],
) -> None:
    status_counts = Counter(row.get("status", "") for row in probe_rows)
    role_counts = Counter(row.get("source_role", "") for row in probe_rows)
    sample_indicator_counts = Counter(row.get("indicator", "") for row in sample_rows if row.get("status") == "sample_record")
    sample_country_count = len({row.get("countryiso3code", "") for row in sample_rows if row.get("status") == "sample_record" and row.get("countryiso3code", "")})
    hefpi_reference_indicator_counts = Counter(row.get("indicator_code", "") for row in hefpi_reference_rows if row.get("status") == "hefpi_uhc_reference_record")
    hefpi_reference_country_count = len({row.get("country_code", "") for row in hefpi_reference_rows if row.get("status") == "hefpi_uhc_reference_record" and row.get("country_code", "")})
    lines = [
        "# Validation Reference Sources",
        "",
        "Status: external validation/reference sources were probed. These data are for later comparison, PPP/CPI context, and denominator feasibility checks; they do not construct household outcomes.",
        "",
        "## Probe Status",
        "",
        markdown_count_table(status_counts, "Status"),
        "",
        "## Source Roles",
        "",
        markdown_count_table(role_counts, "Source role"),
        "",
        "## Indicator Sample",
        "",
        f"- Sample rows: {len(sample_rows)}",
        f"- Countries with sample records: {sample_country_count}",
        "",
        markdown_count_table(sample_indicator_counts, "Indicator sample records"),
        "",
        "## HEFPI UHC Reference Extract",
        "",
        f"- HEFPI UHC series rows: {sum(1 for row in hefpi_series_rows if row.get('status') == 'hefpi_uhc_series')}",
        f"- HEFPI UHC country-year records for priority countries: {sum(1 for row in hefpi_reference_rows if row.get('status') == 'hefpi_uhc_reference_record')}",
        f"- Priority countries with HEFPI UHC records: {hefpi_reference_country_count}",
        "",
        markdown_count_table(hefpi_reference_indicator_counts, "HEFPI UHC indicator"),
        "",
        "## Guardrails",
        "",
        "- HEFPI/WDI country indicators are validation/context sources, not replacements for survey microdata outcomes.",
        "- CHE10/CHE25 WDI archive indicators may be useful external comparators, but project estimates must be constructed from audited raw survey OOP and household budget variables.",
        "- SDG 3.8.2 discretionary-budget construction still requires household OOP, consumption/income, societal poverty line, PPP/CPI assumptions, and survey-specific unit checks.",
        "",
        "## Machine-Readable Outputs",
        "",
        f"- `temp/{PROBE_PATH.name}`",
        f"- `temp/{INDICATOR_SAMPLE_PATH.name}`",
        f"- `temp/{HEFPI_UHC_SERIES_PATH.name}`",
        f"- `temp/{HEFPI_UHC_REFERENCE_PATH.name}`",
        "- Snapshots under `temp/source_snapshots/validation_reference_sources/`",
    ]
    REPORT_PATH.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    ensure_dirs()
    SNAPSHOT_DIR.mkdir(parents=True, exist_ok=True)
    probe_rows = [probe_page(source) for source in SOURCE_ROWS]
    probe_rows.extend(probe_indicator(row) for row in INDICATOR_ROWS)
    countries = priority_country_codes()
    sample_rows = sample_indicator_data(countries)
    hefpi_series_rows, hefpi_reference_rows = parse_hefpi_uhc_reference(probe_rows, countries)
    write_csv(PROBE_PATH, probe_rows, PROBE_COLUMNS)
    write_csv(INDICATOR_SAMPLE_PATH, sample_rows, SAMPLE_COLUMNS)
    write_csv(HEFPI_UHC_SERIES_PATH, hefpi_series_rows, HEFPI_SERIES_COLUMNS)
    write_csv(HEFPI_UHC_REFERENCE_PATH, hefpi_reference_rows, HEFPI_REFERENCE_COLUMNS)
    write_report(probe_rows, sample_rows, hefpi_series_rows, hefpi_reference_rows)
    ok = sum(1 for row in probe_rows if row.get("status") in {"reachable_snapshot_saved", "indicator_metadata_available"})
    samples = sum(1 for row in sample_rows if row.get("status") == "sample_record")
    hefpi_records = sum(1 for row in hefpi_reference_rows if row.get("status") == "hefpi_uhc_reference_record")
    append_log(TEMP_DIR / "audit_log.md", f"Validation reference probe checked {len(probe_rows)} sources; ok={ok}; sample_records={samples}; hefpi_uhc_records={hefpi_records}.")
    print(f"Validation reference probe sources={len(probe_rows)} ok={ok} sample_records={samples} hefpi_uhc_records={hefpi_records}")


if __name__ == "__main__":
    main()
