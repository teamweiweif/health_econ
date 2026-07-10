from __future__ import annotations

import csv
import hashlib
import re
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any
from urllib.parse import urljoin

import requests

from common import PROJECT_ROOT, REPORT_DIR, RESULT_DIR, TEMP_DIR, append_log, ensure_dirs, utc_now_iso, write_csv


MINIMUM_BATCH_PATH = TEMP_DIR / "priority_lsms_isa_threshold_minimum_batch.csv"

ENDPOINT_PATH = TEMP_DIR / "priority_lsms_isa_minimum_batch_endpoint_refresh.csv"
DATASET_PATH = TEMP_DIR / "priority_lsms_isa_minimum_batch_endpoint_dataset_status.csv"
SUMMARY_PATH = RESULT_DIR / "priority_lsms_isa_minimum_batch_endpoint_refresh_summary.csv"
REPORT_PATH = REPORT_DIR / "priority_lsms_isa_minimum_batch_endpoint_refresh.md"

RAW_ROOT = TEMP_DIR / "raw_downloads"

USER_AGENT = "Codex climate_uhc_ml priority LSMS-ISA minimum batch endpoint refresh"
TIMEOUT = 45
MAX_BYTES = 512 * 1024

DATA_EXTENSIONS = {
    ".dta",
    ".sav",
    ".por",
    ".sas7bdat",
    ".xpt",
    ".csv",
    ".tsv",
    ".zip",
    ".tar",
    ".gz",
    ".tgz",
    ".7z",
    ".rar",
}
RAW_CONTENT_HINTS = ["application/zip", "application/octet-stream", "application/x-zip", "application/x-stata"]
GATE_HINTS = ["login", "log in", "sign in", "register", "registration", "terms", "data access agreement", "licensed", "request access"]
METADATA_HINTS = ["metadata", "data-dictionary", "related-materials", "variables", "ddi", "json"]
METADATA_ENDPOINT_NAMES = {"catalog_idno_api", "variables_idno_api", "metadata_ddi_export", "metadata_json_export"}

ENDPOINTS = [
    ("catalog_numeric_api", "https://microdata.worldbank.org/index.php/api/catalog/{catalog_id}", "numeric catalog API check"),
    ("catalog_idno_api", "https://microdata.worldbank.org/index.php/api/catalog/{idno}", "IDNO catalog API check"),
    ("variables_idno_api", "https://microdata.worldbank.org/index.php/api/catalog/{idno}/variables", "IDNO variable metadata API check"),
    ("metadata_ddi_export", "https://microdata.worldbank.org/metadata/export/{catalog_id}/ddi", "DDI/XML metadata export"),
    ("metadata_json_export", "https://microdata.worldbank.org/metadata/export/{catalog_id}/json", "JSON metadata export"),
    ("numeric_get_microdata_page", "https://microdata.worldbank.org/catalog/{catalog_id}/get-microdata", "numeric get-microdata page"),
    ("numeric_download_page", "https://microdata.worldbank.org/catalog/{catalog_id}/download", "numeric download route check"),
    ("idno_get_microdata_page", "https://microdata.worldbank.org/catalog/{idno}/get-microdata", "IDNO get-microdata route check"),
]

ENDPOINT_COLUMNS = [
    "probe_time",
    "threshold_sequence_rank",
    "threshold_download_role",
    "country",
    "wave",
    "idno",
    "catalog_id",
    "endpoint_name",
    "endpoint_url",
    "endpoint_role",
    "http_status",
    "final_url",
    "content_type",
    "content_length_header",
    "content_disposition",
    "bytes_read",
    "truncated",
    "content_sha256_limited",
    "endpoint_classification",
    "raw_download_candidate",
    "access_gate_detected",
    "metadata_endpoint_detected",
    "candidate_links",
    "evidence_flags",
    "next_action",
]

DATASET_COLUMNS = [
    "threshold_sequence_rank",
    "threshold_download_role",
    "country",
    "wave",
    "idno",
    "catalog_id",
    "official_get_microdata_url",
    "endpoint_rows",
    "successful_public_metadata_endpoints",
    "successful_variable_api_endpoints",
    "get_microdata_gate_endpoints",
    "raw_download_candidate_endpoints",
    "credentialed_download_required",
    "endpoint_refresh_status",
    "handoff_readme",
]

SUMMARY_COLUMNS = ["metric", "value", "interpretation"]


def read_csv_dicts(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        return []
    with path.open(encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def clean(value: Any) -> str:
    return "" if value is None else str(value).strip()


def safe_int(value: Any, default: int = 0) -> int:
    try:
        text = clean(value)
        return int(float(text)) if text else default
    except (TypeError, ValueError):
        return default


def catalog_id_from_url(url: str) -> str:
    match = re.search(r"/catalog/(\d+)", clean(url))
    return match.group(1) if match else ""


def rel(path: Path) -> str:
    try:
        return str(path.relative_to(PROJECT_ROOT)).replace("\\", "/")
    except ValueError:
        return str(path).replace("\\", "/")


def raw_folder_path(folder: str, idno: str) -> Path:
    folder_clean = clean(folder).replace("\\", "/").strip("/")
    if folder_clean:
        return PROJECT_ROOT / folder_clean
    return RAW_ROOT / idno


def extension_from_url(url: str) -> str:
    return Path(clean(url).split("?", 1)[0].split("#", 1)[0]).suffix.lower()


def read_limited(response: requests.Response) -> tuple[bytes, str]:
    chunks: list[bytes] = []
    total = 0
    truncated = "0"
    for chunk in response.iter_content(chunk_size=64 * 1024):
        if not chunk:
            continue
        remaining = MAX_BYTES - total
        if remaining <= 0:
            truncated = "1"
            break
        if len(chunk) > remaining:
            chunks.append(chunk[:remaining])
            truncated = "1"
            break
        chunks.append(chunk)
        total += len(chunk)
    return b"".join(chunks), truncated


def decode_text(content: bytes, response: requests.Response) -> str:
    encoding = response.encoding or "utf-8"
    return content.decode(encoding, errors="replace")


def sha256_bytes(content: bytes) -> str:
    return hashlib.sha256(content).hexdigest() if content else ""


def extract_links(base_url: str, html: str) -> str:
    links: list[str] = []
    seen: set[str] = set()
    for href in re.findall(r"""href=["']([^"']+)["']""", html, flags=re.IGNORECASE):
        url = urljoin(base_url, href)
        low = url.lower()
        if (
            extension_from_url(url) in DATA_EXTENSIONS
            or "download" in low
            or "get-microdata" in low
            or "metadata/export" in low
            or "data-dictionary" in low
        ):
            if url not in seen:
                links.append(url)
                seen.add(url)
        if len(links) >= 20:
            break
    return ";".join(links)


def raw_candidate_from_headers(url: str, content_type: str, disposition: str) -> bool:
    low_type = content_type.lower()
    low_disp = disposition.lower()
    return (
        extension_from_url(url) in DATA_EXTENSIONS
        or any(hint in low_type for hint in RAW_CONTENT_HINTS)
        or "attachment" in low_disp
        or any(ext in low_disp for ext in DATA_EXTENSIONS)
    )


def classify(
    endpoint_name: str,
    response: requests.Response | None,
    content: bytes,
    raw_header_candidate: bool,
    candidate_links: str,
    request_error: str,
) -> tuple[str, str, str, str, str, str]:
    if response is None:
        return "request_failed", "0", "0", "0", "request_error", f"Retry official endpoint manually. Error: {request_error}"

    status = response.status_code
    content_type = response.headers.get("content-type", "")
    text = decode_text(content, response) if content else ""
    low = text.lower()
    gate = "1" if any(hint in low for hint in GATE_HINTS) else "0"
    link_raw = any(extension_from_url(link) in DATA_EXTENSIONS for link in candidate_links.split(";") if link)
    raw_candidate = "1" if raw_header_candidate or link_raw else "0"
    metadata = "1" if endpoint_name in METADATA_ENDPOINT_NAMES or any(hint in response.url.lower() for hint in METADATA_HINTS) else "0"
    evidence_flags = ";".join(
        flag
        for flag, active in [
            ("raw_header_candidate", raw_header_candidate),
            ("raw_link_candidate", link_raw),
            ("access_gate_language", gate == "1"),
            ("metadata_endpoint", metadata == "1"),
            ("empty_body", len(content) == 0),
        ]
        if active
    )

    if status >= 400:
        return "http_error_not_public_endpoint", raw_candidate, gate, metadata, evidence_flags, "Use official catalog/get-microdata workflow; do not treat this endpoint as raw access."
    if metadata == "1" and status == 200:
        return "public_metadata_endpoint_not_raw_package", "0", gate, metadata, evidence_flags, "Use as metadata evidence only; raw package receipt still requires original files."
    if raw_candidate == "1" and gate == "0":
        return "possible_public_raw_endpoint_needs_terms_review", raw_candidate, gate, metadata, evidence_flags, "Manually inspect official terms before any download; do not auto-promote from endpoint evidence."
    if raw_candidate == "1" and gate == "1":
        return "raw_candidate_access_gate_or_terms_present", raw_candidate, gate, metadata, evidence_flags, "Complete official login/terms workflow before downloading a complete raw package."
    if endpoint_name == "numeric_get_microdata_page" and gate == "1":
        return "official_get_microdata_access_gate", raw_candidate, gate, metadata, evidence_flags, "Use official login/register/terms workflow and download the complete package manually."
    if endpoint_name == "numeric_download_page" and len(content) == 0:
        return "empty_download_route_not_raw_package", raw_candidate, gate, metadata, evidence_flags, "Use the official get-microdata workflow; no public raw payload returned."
    if endpoint_name == "idno_get_microdata_page" and status == 200:
        return "idno_route_returns_catalog_or_search_html_not_raw_package", raw_candidate, gate, metadata, evidence_flags, "Use numeric catalog get-microdata URL for the official access workflow."
    if "html" in content_type.lower():
        return "non_raw_html_endpoint_manual_review", raw_candidate, gate, metadata, evidence_flags, "Review endpoint manually; no raw package evidence accepted."
    return "non_raw_endpoint_manual_review", raw_candidate, gate, metadata, evidence_flags, "Review endpoint manually; no raw package evidence accepted."


def probe_endpoint(wave: dict[str, str], endpoint_name: str, template: str, role: str) -> dict[str, str]:
    catalog_id = catalog_id_from_url(wave.get("official_get_microdata_url", ""))
    url = template.format(catalog_id=catalog_id, idno=wave.get("idno", ""))
    base = {
        "probe_time": utc_now_iso(),
        "threshold_sequence_rank": clean(wave.get("threshold_sequence_rank")),
        "threshold_download_role": clean(wave.get("threshold_download_role")),
        "country": clean(wave.get("country")),
        "wave": clean(wave.get("wave")),
        "idno": clean(wave.get("idno")),
        "catalog_id": catalog_id,
        "endpoint_name": endpoint_name,
        "endpoint_url": url,
        "endpoint_role": role,
        "http_status": "",
        "final_url": "",
        "content_type": "",
        "content_length_header": "",
        "content_disposition": "",
        "bytes_read": "0",
        "truncated": "0",
        "content_sha256_limited": "",
        "endpoint_classification": "",
        "raw_download_candidate": "0",
        "access_gate_detected": "0",
        "metadata_endpoint_detected": "0",
        "candidate_links": "",
        "evidence_flags": "",
        "next_action": "",
    }
    request_error = ""
    response: requests.Response | None = None
    content = b""
    raw_header_candidate = False
    try:
        response = requests.get(
            url,
            headers={"User-Agent": USER_AGENT},
            timeout=TIMEOUT,
            stream=True,
            allow_redirects=True,
        )
        base["http_status"] = str(response.status_code)
        base["final_url"] = response.url
        base["content_type"] = response.headers.get("content-type", "")
        base["content_length_header"] = response.headers.get("content-length", "")
        base["content_disposition"] = response.headers.get("content-disposition", "")
        raw_header_candidate = raw_candidate_from_headers(base["final_url"] or url, base["content_type"], base["content_disposition"]) and endpoint_name not in METADATA_ENDPOINT_NAMES
        if not raw_header_candidate:
            content, truncated = read_limited(response)
            base["bytes_read"] = str(len(content))
            base["truncated"] = truncated
            base["content_sha256_limited"] = sha256_bytes(content)
            if "html" in base["content_type"].lower() or content.lstrip().startswith(b"<"):
                base["candidate_links"] = extract_links(base["final_url"] or url, decode_text(content, response))
    except Exception as exc:
        request_error = str(exc)
    finally:
        if response is not None:
            response.close()

    classification, raw_candidate, gate, metadata, evidence_flags, next_action = classify(
        endpoint_name,
        response,
        content,
        raw_header_candidate,
        base["candidate_links"],
        request_error,
    )
    base["endpoint_classification"] = classification
    base["raw_download_candidate"] = raw_candidate
    base["access_gate_detected"] = gate
    base["metadata_endpoint_detected"] = metadata
    base["evidence_flags"] = evidence_flags
    base["next_action"] = next_action
    return base


def markdown_table(rows: list[dict[str, str]], columns: list[str], limit: int = 40) -> str:
    lines = ["| " + " | ".join(columns) + " |", "|" + "|".join("---" for _ in columns) + "|"]
    for row in rows[:limit]:
        values = []
        for column in columns:
            value = clean(row.get(column)).replace("|", "/")
            if len(value) > 120:
                value = value[:117] + "..."
            values.append(value)
        lines.append("| " + " | ".join(values) + " |")
    return "\n".join(lines)


def write_handoff(dataset_row: dict[str, str], endpoint_rows: list[dict[str, str]], local_target_folder: str) -> str:
    folder = raw_folder_path(local_target_folder, dataset_row.get("idno", ""))
    folder.mkdir(parents=True, exist_ok=True)
    path = folder / "_PRIORITY_LSMS_ISA_MINIMUM_BATCH_ENDPOINT_REFRESH.md"
    path.write_text(
        f"""# Minimum Batch Endpoint Refresh

IDNO: `{dataset_row.get('idno', '')}`

Country-wave: {dataset_row.get('country', '')} {dataset_row.get('wave', '')}

Official get-microdata URL: {dataset_row.get('official_get_microdata_url', '')}

Endpoint refresh status: `{dataset_row.get('endpoint_refresh_status', '')}`

Credentialed download required: `{dataset_row.get('credentialed_download_required', '')}`

## Endpoint Results

{markdown_table(endpoint_rows, ['endpoint_name', 'http_status', 'endpoint_classification', 'raw_download_candidate', 'access_gate_detected'], 20)}

## Stop Rule

Endpoint evidence can prove public metadata and access gates, but it does not
prove raw package receipt. Do not write `data/` or run ML until the complete
official package is locally received, official DDI file names match, raw values
are verified, and timing/geography/climate linkage gates pass.
""",
        encoding="utf-8",
    )
    return rel(path)


def build_dataset_rows(endpoint_rows: list[dict[str, str]], waves: list[dict[str, str]]) -> list[dict[str, str]]:
    by_id: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in endpoint_rows:
        by_id[row["idno"]].append(row)
    wave_by_id = {clean(row.get("idno")): row for row in waves}
    dataset_rows: list[dict[str, str]] = []
    for idno, rows in sorted(by_id.items(), key=lambda item: safe_int(wave_by_id.get(item[0], {}).get("threshold_sequence_rank"), 999)):
        wave = wave_by_id.get(idno, {})
        public_metadata = sum(1 for row in rows if row["endpoint_classification"] == "public_metadata_endpoint_not_raw_package")
        variable_api = sum(1 for row in rows if row["endpoint_name"] == "variables_idno_api" and row["http_status"] == "200")
        gate_rows = sum(1 for row in rows if row["endpoint_classification"] == "official_get_microdata_access_gate")
        raw_candidates = sum(1 for row in rows if row["raw_download_candidate"] == "1")
        credentialed_required = "1" if gate_rows > 0 and raw_candidates == 0 else "0"
        if raw_candidates > 0:
            status = "raw_candidate_needs_terms_review_not_accepted"
        elif credentialed_required == "1" and public_metadata >= 3:
            status = "metadata_confirmed_raw_access_gate_confirmed"
        elif credentialed_required == "1":
            status = "raw_access_gate_confirmed_metadata_partial"
        else:
            status = "manual_endpoint_review_required"
        dataset = {
            "threshold_sequence_rank": clean(wave.get("threshold_sequence_rank")),
            "threshold_download_role": clean(wave.get("threshold_download_role")),
            "country": clean(wave.get("country")),
            "wave": clean(wave.get("wave")),
            "idno": idno,
            "catalog_id": catalog_id_from_url(wave.get("official_get_microdata_url", "")),
            "official_get_microdata_url": clean(wave.get("official_get_microdata_url")),
            "endpoint_rows": str(len(rows)),
            "successful_public_metadata_endpoints": str(public_metadata),
            "successful_variable_api_endpoints": str(variable_api),
            "get_microdata_gate_endpoints": str(gate_rows),
            "raw_download_candidate_endpoints": str(raw_candidates),
            "credentialed_download_required": credentialed_required,
            "endpoint_refresh_status": status,
            "handoff_readme": "",
        }
        dataset["handoff_readme"] = write_handoff(dataset, rows, clean(wave.get("local_target_folder")))
        dataset_rows.append(dataset)
    return dataset_rows


def build_summary(dataset_rows: list[dict[str, str]], endpoint_rows: list[dict[str, str]]) -> list[dict[str, str]]:
    classification_counts = Counter(row["endpoint_classification"] for row in endpoint_rows)
    rows = [
        {"metric": "priority_lsms_minimum_endpoint_dataset_rows", "value": str(len(dataset_rows)), "interpretation": "Minimum threshold batch country-waves with refreshed official endpoint probes."},
        {"metric": "priority_lsms_minimum_endpoint_country_rows", "value": str(len({row['country'] for row in dataset_rows})), "interpretation": "Countries represented in the minimum endpoint refresh."},
        {"metric": "priority_lsms_minimum_endpoint_rows", "value": str(len(endpoint_rows)), "interpretation": "Official endpoint probes across the minimum threshold batch."},
        {"metric": "priority_lsms_minimum_endpoint_public_metadata_endpoint_rows", "value": str(sum(safe_int(row.get("successful_public_metadata_endpoints")) for row in dataset_rows)), "interpretation": "Dataset-level count of successful public metadata endpoint hits."},
        {"metric": "priority_lsms_minimum_endpoint_variable_api_dataset_rows", "value": str(sum(1 for row in dataset_rows if safe_int(row.get("successful_variable_api_endpoints")) > 0)), "interpretation": "Minimum-batch datasets with a public variable metadata API endpoint."},
        {"metric": "priority_lsms_minimum_endpoint_get_microdata_gate_dataset_rows", "value": str(sum(1 for row in dataset_rows if safe_int(row.get("get_microdata_gate_endpoints")) > 0)), "interpretation": "Minimum-batch datasets whose official get-microdata endpoint shows an access gate."},
        {"metric": "priority_lsms_minimum_endpoint_raw_download_candidate_rows", "value": str(sum(safe_int(row.get("raw_download_candidate_endpoints")) for row in dataset_rows)), "interpretation": "Raw download candidate endpoints detected without accepting them as usable."},
        {"metric": "priority_lsms_minimum_endpoint_credentialed_download_required_rows", "value": str(sum(1 for row in dataset_rows if row.get("credentialed_download_required") == "1")), "interpretation": "Minimum-batch datasets requiring credentialed download after endpoint refresh."},
        {"metric": "priority_lsms_minimum_endpoint_handoff_readmes_written", "value": str(sum(1 for row in dataset_rows if row.get("handoff_readme"))), "interpretation": "Per-wave endpoint-refresh handoffs written."},
        {"metric": "priority_lsms_minimum_endpoint_data_write_status", "value": "blocked_no_raw_package_receipt", "interpretation": "Endpoint refresh never writes promoted data."},
        {"metric": "modeling_gate_status", "value": "blocked", "interpretation": "Models remain blocked until 6 countries, 10 country-waves, and accepted CHIRPS/ERA5 linkage are value-verified."},
    ]
    for classification, count in sorted(classification_counts.items()):
        rows.append({"metric": f"priority_lsms_minimum_endpoint_classification_{classification}", "value": str(count), "interpretation": "Endpoint classification count."})
    return rows


def write_report(dataset_rows: list[dict[str, str]], endpoint_rows: list[dict[str, str]], summary_rows: list[dict[str, str]]) -> None:
    summary_table = "\n".join(f"| {row['metric']} | {row['value']} | {row['interpretation']} |" for row in summary_rows)
    REPORT_PATH.write_text(
        f"""# Priority LSMS-ISA Minimum Batch Endpoint Refresh

Status: official endpoint refresh for the 11 country-waves in the minimum
threshold batch. This probes World Bank catalog/API/metadata/get-microdata
routes and classifies public metadata endpoints, access gates, empty/non-raw
routes, and possible raw candidates.

It does not download raw microdata, accept terms, bypass login, verify values,
create harmonized datasets, or write `data/`.

## Summary

| Metric | Value | Interpretation |
|---|---:|---|
{summary_table}

## Dataset Status

{markdown_table(dataset_rows, ['threshold_sequence_rank', 'country', 'wave', 'idno', 'endpoint_rows', 'successful_public_metadata_endpoints', 'get_microdata_gate_endpoints', 'raw_download_candidate_endpoints', 'credentialed_download_required', 'endpoint_refresh_status'], 20)}

## Endpoint Preview

{markdown_table(endpoint_rows, ['threshold_sequence_rank', 'idno', 'endpoint_name', 'http_status', 'endpoint_classification', 'raw_download_candidate', 'access_gate_detected'], 40)}

## Outputs

- `temp/priority_lsms_isa_minimum_batch_endpoint_refresh.csv`
- `temp/priority_lsms_isa_minimum_batch_endpoint_dataset_status.csv`
- `result/priority_lsms_isa_minimum_batch_endpoint_refresh_summary.csv`
- `temp/raw_downloads/<IDNO>/_PRIORITY_LSMS_ISA_MINIMUM_BATCH_ENDPOINT_REFRESH.md`

## Guardrail

Public catalog, variable, DDI, and JSON routes are metadata endpoints only.
The numeric `get-microdata` route remains the official credentialed raw
acquisition route when an access gate is detected. Endpoint evidence alone
cannot satisfy raw package receipt, raw-value verification, climate linkage, or
analysis-ready gates.
""",
        encoding="utf-8",
    )


def main() -> None:
    ensure_dirs()
    waves = read_csv_dicts(MINIMUM_BATCH_PATH)
    endpoint_rows: list[dict[str, str]] = []
    for wave in waves:
        for endpoint_name, template, role in ENDPOINTS:
            endpoint_rows.append(probe_endpoint(wave, endpoint_name, template, role))
    dataset_rows = build_dataset_rows(endpoint_rows, waves)
    summary_rows = build_summary(dataset_rows, endpoint_rows)
    write_csv(ENDPOINT_PATH, endpoint_rows, ENDPOINT_COLUMNS)
    write_csv(DATASET_PATH, dataset_rows, DATASET_COLUMNS)
    write_csv(SUMMARY_PATH, summary_rows, SUMMARY_COLUMNS)
    write_report(dataset_rows, endpoint_rows, summary_rows)
    append_log(
        TEMP_DIR / "audit_log.md",
        "Priority LSMS/ISA minimum-batch endpoint refresh "
        f"datasets={len(dataset_rows)} endpoints={len(endpoint_rows)}.",
    )
    print(
        "Priority LSMS/ISA minimum-batch endpoint refresh "
        f"datasets={len(dataset_rows)} endpoints={len(endpoint_rows)}."
    )


if __name__ == "__main__":
    main()
