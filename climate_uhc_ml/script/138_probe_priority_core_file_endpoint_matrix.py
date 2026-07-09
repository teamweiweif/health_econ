from __future__ import annotations

import csv
import hashlib
import re
from collections import Counter, defaultdict
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from typing import Any
from urllib.parse import quote

import requests

from common import PROJECT_ROOT, REPORT_DIR, RESULT_DIR, TEMP_DIR, append_log, ensure_dirs, utc_now_iso, write_csv


CORE_CHECKLIST_PATH = TEMP_DIR / "priority_credentialed_raw_core_file_checklist.csv"
FULL_FILE_INVENTORY_PATH = TEMP_DIR / "priority_official_full_file_inventory.csv"
DOSSIER_PATH = TEMP_DIR / "priority_official_download_dossier.csv"

MATRIX_PATH = TEMP_DIR / "priority_core_file_endpoint_matrix.csv"
DATASET_PATH = TEMP_DIR / "priority_core_file_endpoint_dataset_matrix.csv"
SUMMARY_PATH = RESULT_DIR / "priority_core_file_endpoint_matrix_summary.csv"
REPORT_PATH = REPORT_DIR / "priority_core_file_endpoint_matrix.md"

RAW_ROOT = TEMP_DIR / "raw_downloads"

USER_AGENT = "Codex climate_uhc_ml priority core file endpoint matrix"
TIMEOUT = 35
MAX_BYTES = 64 * 1024
MAX_WORKERS = 6

DATA_EXTENSIONS = {".dta", ".sav", ".por", ".sas7bdat", ".xpt", ".csv", ".tsv", ".zip", ".tar", ".gz", ".tgz", ".7z", ".rar"}
GATE_HINTS = ["login", "log in", "sign in", "register", "registration", "terms", "data access agreement", "licensed", "request access"]

DOWNLOAD_ENDPOINTS = [
    ("catalog_download_fid_path", "https://microdata.worldbank.org/catalog/{catalog_id}/download/{fid}", "numeric catalog file download path"),
    ("index_catalog_download_fid_path", "https://microdata.worldbank.org/index.php/catalog/{catalog_id}/download/{fid}", "index.php numeric catalog file download path"),
    ("catalog_download_fid_query", "https://microdata.worldbank.org/catalog/{catalog_id}/download?fid={fid}", "numeric catalog file download query by fid"),
    ("catalog_download_file_query", "https://microdata.worldbank.org/catalog/{catalog_id}/download?file={file_name_quoted}", "numeric catalog file download query by filename"),
]

MATRIX_COLUMNS = [
    "probe_time",
    "acquisition_batch_rank",
    "batch_role",
    "country",
    "wave",
    "idno",
    "catalog_id",
    "core_file_rank",
    "fid",
    "metadata_file_name",
    "metadata_file_description",
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
    "file_endpoint_classification",
    "raw_download_candidate",
    "access_gate_detected",
    "metadata_reference",
    "evidence_snippet",
    "next_action",
]

DATASET_COLUMNS = [
    "acquisition_batch_rank",
    "batch_role",
    "country",
    "wave",
    "idno",
    "catalog_id",
    "core_file_rows",
    "endpoint_rows",
    "metadata_reference_rows",
    "probed_download_endpoint_rows",
    "http_error_route_rows",
    "empty_download_route_rows",
    "access_gate_route_rows",
    "non_raw_html_route_rows",
    "request_failed_rows",
    "raw_download_candidate_rows",
    "download_routes_without_public_raw_rows",
    "credentialed_download_required",
    "core_file_endpoint_matrix_status",
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


def rel(path: Path) -> str:
    try:
        return str(path.relative_to(PROJECT_ROOT)).replace("\\", "/")
    except ValueError:
        return str(path).replace("\\", "/")


def one_by_id(rows: list[dict[str, str]], field: str = "idno") -> dict[str, dict[str, str]]:
    out: dict[str, dict[str, str]] = {}
    for row in rows:
        key = clean(row.get(field))
        if key and key not in out:
            out[key] = row
    return out


def inventory_by_key(rows: list[dict[str, str]]) -> dict[tuple[str, str], dict[str, str]]:
    out: dict[tuple[str, str], dict[str, str]] = {}
    for row in rows:
        idno = clean(row.get("idno"))
        name = clean(row.get("metadata_file_name")).lower()
        fid = clean(row.get("fid")).upper()
        if idno and name:
            out[(idno, name)] = row
        if idno and fid:
            out[(idno, fid)] = row
    return out


def read_limited(response: requests.Response) -> tuple[bytes, str]:
    chunks: list[bytes] = []
    total = 0
    truncated = "0"
    for chunk in response.iter_content(chunk_size=16 * 1024):
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


def extension_from_url(url: str) -> str:
    return Path((url or "").split("?", 1)[0].split("#", 1)[0]).suffix.lower()


def is_raw_candidate(response: requests.Response, content: bytes) -> bool:
    content_type = response.headers.get("content-type", "").lower()
    disposition = response.headers.get("content-disposition", "").lower()
    suffix = extension_from_url(response.url)
    if response.status_code != 200 or not content:
        return False
    if any(ext in disposition for ext in DATA_EXTENSIONS):
        return True
    if suffix in DATA_EXTENSIONS and "html" not in content_type:
        return True
    if any(token in content_type for token in ["octet-stream", "stata", "zip", "x-spss", "x-7z", "x-rar"]):
        return True
    return False


def classify_response(
    endpoint_name: str,
    response: requests.Response | None,
    content: bytes,
    truncated: str,
    error: str = "",
) -> tuple[str, str, str, str, str]:
    if response is None:
        return "request_failed_needs_retry", "0", "0", error[:220], "Retry the endpoint; do not accept this as raw access evidence."

    content_type = response.headers.get("content-type", "").lower()
    text = decode_text(content, response)
    low = text.lower()
    gate = "1" if any(hint in low for hint in GATE_HINTS) else "0"
    raw_candidate = "1" if is_raw_candidate(response, content) else "0"
    snippet = " ".join(text[:220].split()) if "html" in content_type or text else ""

    if response.status_code >= 400:
        return (
            "file_download_route_http_error_not_public_raw",
            raw_candidate,
            gate,
            snippet,
            "Use the official get-microdata workflow; this file route is not a public raw endpoint.",
        )
    if raw_candidate == "1" and gate == "0":
        return (
            "possible_public_raw_file_endpoint_needs_terms_review",
            raw_candidate,
            gate,
            snippet,
            "Manually inspect terms before any download; do not promote from endpoint probe alone.",
        )
    if gate == "1":
        return (
            "file_download_route_access_gate",
            raw_candidate,
            gate,
            snippet,
            "Use official login/register/terms workflow and download the complete package.",
        )
    if response.status_code == 200 and len(content) == 0:
        return (
            "file_download_route_empty_not_raw_package",
            raw_candidate,
            gate,
            "",
            "Use official get-microdata workflow; this route returned no payload.",
        )
    if "html" in content_type:
        return (
            "file_download_route_non_raw_html",
            raw_candidate,
            gate,
            snippet,
            "Treat as non-raw HTML; raw package still requires credentialed acquisition.",
        )
    return (
        "file_download_route_non_raw_response",
        raw_candidate,
        gate,
        snippet if snippet else f"bytes={len(content)} truncated={truncated}",
        "Review manually; no raw package evidence accepted without official receipt and verification.",
    )


def base_fields(core: dict[str, str], inventory: dict[str, str], endpoint_name: str, endpoint_url: str, endpoint_role: str) -> dict[str, str]:
    return {
        "probe_time": utc_now_iso(),
        "acquisition_batch_rank": core.get("acquisition_batch_rank", ""),
        "batch_role": core.get("batch_role", ""),
        "country": core.get("country", ""),
        "wave": core.get("wave", ""),
        "idno": core.get("idno", ""),
        "catalog_id": inventory.get("catalog_id", ""),
        "core_file_rank": core.get("core_file_rank", ""),
        "fid": inventory.get("fid", ""),
        "metadata_file_name": core.get("metadata_file_name", ""),
        "metadata_file_description": core.get("metadata_file_description", ""),
        "endpoint_name": endpoint_name,
        "endpoint_url": endpoint_url,
        "endpoint_role": endpoint_role,
        "http_status": "",
        "final_url": "",
        "content_type": "",
        "content_length_header": "",
        "content_disposition": "",
        "bytes_read": "0",
        "truncated": "0",
        "content_sha256_limited": "",
        "file_endpoint_classification": "",
        "raw_download_candidate": "0",
        "access_gate_detected": "0",
        "metadata_reference": "0",
        "evidence_snippet": "",
        "next_action": "",
    }


def metadata_reference_row(core: dict[str, str], inventory: dict[str, str]) -> dict[str, str]:
    source_url = inventory.get("source_url", "")
    row = base_fields(core, inventory, "data_dictionary_source_url", source_url, "official file-level public metadata reference")
    row.update(
        {
            "file_endpoint_classification": "public_file_metadata_reference_not_raw_package",
            "metadata_reference": "1",
            "evidence_snippet": "Official data-dictionary file row from public metadata inventory.",
            "next_action": "Use as file-level metadata evidence only; raw values require credentialed package receipt.",
        }
    )
    return row


def probe_download_endpoint(core: dict[str, str], inventory: dict[str, str], endpoint_name: str, template: str, endpoint_role: str) -> dict[str, str]:
    catalog_id = inventory.get("catalog_id", "")
    fid = inventory.get("fid", "")
    file_name = core.get("metadata_file_name", "")
    url = template.format(catalog_id=catalog_id, fid=quote(fid), file_name_quoted=quote(file_name))
    row = base_fields(core, inventory, endpoint_name, url, endpoint_role)
    if not catalog_id or not fid:
        row.update(
            {
                "file_endpoint_classification": "missing_catalog_id_or_fid",
                "evidence_snippet": "Catalog ID or file ID is missing from official metadata inventory.",
                "next_action": "Refresh official full file inventory before probing file-level routes.",
            }
        )
        return row
    try:
        with requests.get(url, headers={"User-Agent": USER_AGENT}, timeout=TIMEOUT, stream=True, allow_redirects=True) as response:
            content, truncated = read_limited(response)
            classification, raw_candidate, gate, snippet, next_action = classify_response(endpoint_name, response, content, truncated)
            row.update(
                {
                    "http_status": str(response.status_code),
                    "final_url": response.url,
                    "content_type": response.headers.get("content-type", ""),
                    "content_length_header": response.headers.get("content-length", ""),
                    "content_disposition": response.headers.get("content-disposition", ""),
                    "bytes_read": str(len(content)),
                    "truncated": truncated,
                    "content_sha256_limited": hashlib.sha256(content).hexdigest() if content else "",
                    "file_endpoint_classification": classification,
                    "raw_download_candidate": raw_candidate,
                    "access_gate_detected": gate,
                    "evidence_snippet": snippet,
                    "next_action": next_action,
                }
            )
    except Exception as exc:
        classification, raw_candidate, gate, snippet, next_action = classify_response(endpoint_name, None, b"", "0", str(exc))
        row.update(
            {
                "file_endpoint_classification": classification,
                "raw_download_candidate": raw_candidate,
                "access_gate_detected": gate,
                "evidence_snippet": snippet,
                "next_action": next_action,
            }
        )
    return row


def markdown_table(rows: list[dict[str, str]], columns: list[str], limit: int = 20) -> str:
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


def raw_folder_path(idno: str) -> Path:
    return RAW_ROOT / idno


def write_handoff(dataset_row: dict[str, str], rows: list[dict[str, str]]) -> str:
    folder = raw_folder_path(dataset_row.get("idno", ""))
    folder.mkdir(parents=True, exist_ok=True)
    path = folder / "_PRIORITY_CORE_FILE_ENDPOINT_MATRIX.md"
    path.write_text(
        f"""# Priority Core File Endpoint Matrix

Dataset: {dataset_row.get('idno', '')} - {dataset_row.get('country', '')} {dataset_row.get('wave', '')}

Status: {dataset_row.get('core_file_endpoint_matrix_status', '')}

Core files checked: {dataset_row.get('core_file_rows', '0')}

File endpoint rows: {dataset_row.get('endpoint_rows', '0')}

Probed download routes: {dataset_row.get('probed_download_endpoint_rows', '0')}

Raw download candidates: {dataset_row.get('raw_download_candidate_rows', '0')}

Credentialed download required: {dataset_row.get('credentialed_download_required', '')}

## File Endpoint Preview

{markdown_table(rows, ['core_file_rank', 'metadata_file_name', 'endpoint_name', 'http_status', 'file_endpoint_classification', 'raw_download_candidate'], 24)}

Guardrail: file-level route probes do not download or accept raw microdata.
Promotion still requires the complete unchanged official raw package plus raw
value, unit, recall-period, missing-code, merge-key, survey-design, timing,
geography, and climate-linkage verification.
""",
        encoding="utf-8",
    )
    return rel(path)


def build_outputs() -> tuple[list[dict[str, str]], list[dict[str, str]], list[dict[str, str]]]:
    core_rows = read_csv_dicts(CORE_CHECKLIST_PATH)
    inventory_lookup = inventory_by_key(read_csv_dicts(FULL_FILE_INVENTORY_PATH))
    dossier_by_id = one_by_id(read_csv_dicts(DOSSIER_PATH))

    metadata_rows: list[dict[str, str]] = []
    probe_jobs: list[tuple[dict[str, str], dict[str, str], str, str, str]] = []
    for core in core_rows:
        idno = clean(core.get("idno"))
        inventory = inventory_lookup.get((idno, clean(core.get("metadata_file_name")).lower()), {})
        if not inventory:
            inventory = inventory_lookup.get((idno, clean(core.get("fid")).upper()), {})
        if not inventory and idno in dossier_by_id:
            inventory = {"catalog_id": dossier_by_id[idno].get("catalog_id", ""), "fid": ""}
        metadata_rows.append(metadata_reference_row(core, inventory))
        for endpoint_name, template, endpoint_role in DOWNLOAD_ENDPOINTS:
            probe_jobs.append((core, inventory, endpoint_name, template, endpoint_role))

    probed_rows: list[dict[str, str]] = []
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        futures = [executor.submit(probe_download_endpoint, *job) for job in probe_jobs]
        for future in as_completed(futures):
            probed_rows.append(future.result())

    matrix_rows = metadata_rows + probed_rows
    matrix_rows.sort(
        key=lambda row: (
            safe_int(row.get("acquisition_batch_rank"), 9999),
            safe_int(row.get("core_file_rank"), 9999),
            row.get("endpoint_name", ""),
        )
    )

    rows_by_id: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in matrix_rows:
        rows_by_id[row.get("idno", "")].append(row)

    dataset_rows: list[dict[str, str]] = []
    no_public_raw_classes = {
        "file_download_route_http_error_not_public_raw",
        "file_download_route_empty_not_raw_package",
        "file_download_route_access_gate",
        "file_download_route_non_raw_html",
        "file_download_route_non_raw_response",
    }
    for idno, rows in rows_by_id.items():
        first = rows[0]
        core_files = {row.get("metadata_file_name", "") for row in rows if row.get("metadata_file_name")}
        classifications = Counter(row.get("file_endpoint_classification", "") for row in rows)
        probed = [row for row in rows if row.get("metadata_reference") != "1"]
        raw_candidates = sum(1 for row in rows if row.get("raw_download_candidate") == "1")
        no_public_raw = sum(1 for row in probed if row.get("file_endpoint_classification") in no_public_raw_classes)
        credentialed_required = "1" if raw_candidates == 0 and no_public_raw >= len(core_files) * len(DOWNLOAD_ENDPOINTS) else "0"
        status = (
            "core_file_routes_confirmed_non_public_raw"
            if credentialed_required == "1"
            else "core_file_endpoint_matrix_needs_manual_review"
        )
        dataset_row = {
            "acquisition_batch_rank": first.get("acquisition_batch_rank", ""),
            "batch_role": first.get("batch_role", ""),
            "country": first.get("country", ""),
            "wave": first.get("wave", ""),
            "idno": idno,
            "catalog_id": first.get("catalog_id", ""),
            "core_file_rows": str(len(core_files)),
            "endpoint_rows": str(len(rows)),
            "metadata_reference_rows": str(classifications.get("public_file_metadata_reference_not_raw_package", 0)),
            "probed_download_endpoint_rows": str(len(probed)),
            "http_error_route_rows": str(classifications.get("file_download_route_http_error_not_public_raw", 0)),
            "empty_download_route_rows": str(classifications.get("file_download_route_empty_not_raw_package", 0)),
            "access_gate_route_rows": str(classifications.get("file_download_route_access_gate", 0)),
            "non_raw_html_route_rows": str(classifications.get("file_download_route_non_raw_html", 0)),
            "request_failed_rows": str(classifications.get("request_failed_needs_retry", 0)),
            "raw_download_candidate_rows": str(raw_candidates),
            "download_routes_without_public_raw_rows": str(no_public_raw),
            "credentialed_download_required": credentialed_required,
            "core_file_endpoint_matrix_status": status,
            "handoff_readme": "",
        }
        dataset_row["handoff_readme"] = write_handoff(dataset_row, rows)
        dataset_rows.append(dataset_row)

    dataset_rows.sort(key=lambda row: safe_int(row.get("acquisition_batch_rank"), 9999))
    summary = build_summary(matrix_rows, dataset_rows)
    return matrix_rows, dataset_rows, summary


def build_summary(matrix_rows: list[dict[str, str]], dataset_rows: list[dict[str, str]]) -> list[dict[str, str]]:
    classifications = Counter(row.get("file_endpoint_classification", "") for row in matrix_rows)
    rows = [
        {"metric": "priority_core_file_endpoint_dataset_rows", "value": str(len(dataset_rows)), "interpretation": "Priority and backup datasets with core file endpoint matrices."},
        {"metric": "priority_core_file_endpoint_core_file_rows", "value": str(sum(safe_int(row.get("core_file_rows")) for row in dataset_rows)), "interpretation": "Priority core file rows covered by the file endpoint matrix."},
        {"metric": "priority_core_file_endpoint_matrix_rows", "value": str(len(matrix_rows)), "interpretation": "File-level metadata references and download route probes."},
        {"metric": "priority_core_file_endpoint_metadata_reference_rows", "value": str(sum(safe_int(row.get("metadata_reference_rows")) for row in dataset_rows)), "interpretation": "Official data-dictionary source rows carried as metadata references."},
        {"metric": "priority_core_file_endpoint_probed_download_rows", "value": str(sum(safe_int(row.get("probed_download_endpoint_rows")) for row in dataset_rows)), "interpretation": "Constructed file-level download routes probed without downloading raw files."},
        {"metric": "priority_core_file_endpoint_http_error_rows", "value": str(sum(safe_int(row.get("http_error_route_rows")) for row in dataset_rows)), "interpretation": "File download routes returning HTTP errors rather than public raw payloads."},
        {"metric": "priority_core_file_endpoint_empty_download_rows", "value": str(sum(safe_int(row.get("empty_download_route_rows")) for row in dataset_rows)), "interpretation": "File download routes returning empty non-raw responses."},
        {"metric": "priority_core_file_endpoint_request_failed_rows", "value": str(sum(safe_int(row.get("request_failed_rows")) for row in dataset_rows)), "interpretation": "File download route probes that need retry."},
        {"metric": "priority_core_file_endpoint_raw_candidate_rows", "value": str(sum(safe_int(row.get("raw_download_candidate_rows")) for row in dataset_rows)), "interpretation": "Potential public raw file candidates detected; zero is required before treating credentialed route as necessary."},
        {"metric": "priority_core_file_endpoint_download_routes_without_public_raw_rows", "value": str(sum(safe_int(row.get("download_routes_without_public_raw_rows")) for row in dataset_rows)), "interpretation": "Probed download route rows that did not expose public raw payloads."},
        {"metric": "priority_core_file_endpoint_credentialed_download_required_rows", "value": str(sum(1 for row in dataset_rows if row.get("credentialed_download_required") == "1")), "interpretation": "Datasets whose core file route probes still require official credentialed raw acquisition."},
        {"metric": "priority_core_file_endpoint_handoff_readmes_written", "value": str(sum(1 for row in dataset_rows if row.get("handoff_readme"))), "interpretation": "Per-wave core file endpoint handoffs written."},
        {"metric": "modeling_gate_status", "value": "blocked", "interpretation": "File endpoint evidence does not satisfy raw receipt, raw value verification, or climate-linkage gates."},
    ]
    for status, count in sorted(classifications.items()):
        rows.append({"metric": f"priority_core_file_endpoint_classification_{status}", "value": str(count), "interpretation": "File endpoint classification count."})
    return rows


def write_report(matrix_rows: list[dict[str, str]], dataset_rows: list[dict[str, str]], summary: list[dict[str, str]]) -> None:
    summary_table = "\n".join(f"| {row['metric']} | {row['value']} | {row['interpretation']} |" for row in summary)
    REPORT_PATH.write_text(
        f"""# Priority Core File Endpoint Matrix

Status: file-level official endpoint probe for priority raw acquisition. This
checks core file data-dictionary references and common World Bank/NADA
file-download route patterns. It reads only small response samples and does not
download raw microdata.

## Summary

| Metric | Value | Interpretation |
|---|---:|---|
{summary_table}

## Dataset Matrix

{markdown_table(dataset_rows, ['acquisition_batch_rank', 'idno', 'core_file_rows', 'endpoint_rows', 'probed_download_endpoint_rows', 'raw_download_candidate_rows', 'download_routes_without_public_raw_rows', 'credentialed_download_required', 'core_file_endpoint_matrix_status'], 20)}

## Endpoint Preview

{markdown_table(matrix_rows, ['acquisition_batch_rank', 'idno', 'core_file_rank', 'metadata_file_name', 'endpoint_name', 'http_status', 'file_endpoint_classification', 'raw_download_candidate'], 50)}

## Guardrail

File-level public metadata and empty/404 download routes are not raw package
receipt. Promotion still requires complete original raw package placement,
archive/direct file coverage, raw values and labels, units and recall periods,
missing-code and skip-pattern review, merge-key and survey-design checks,
timing/geography verification, and an accepted CHIRPS or ERA5 linkage route.

## Machine-Readable Outputs

- `temp/priority_core_file_endpoint_matrix.csv`
- `temp/priority_core_file_endpoint_dataset_matrix.csv`
- `result/priority_core_file_endpoint_matrix_summary.csv`
""",
        encoding="utf-8",
    )


def main() -> None:
    ensure_dirs()
    matrix_rows, dataset_rows, summary = build_outputs()
    write_csv(MATRIX_PATH, matrix_rows, MATRIX_COLUMNS)
    write_csv(DATASET_PATH, dataset_rows, DATASET_COLUMNS)
    write_csv(SUMMARY_PATH, summary, SUMMARY_COLUMNS)
    write_report(matrix_rows, dataset_rows, summary)
    append_log(
        TEMP_DIR / "audit_log.md",
        f"Built priority core file endpoint matrix rows={len(matrix_rows)} datasets={len(dataset_rows)}.",
    )
    print(f"Priority core file endpoint matrix rows={len(matrix_rows)} datasets={len(dataset_rows)}.")


if __name__ == "__main__":
    main()
