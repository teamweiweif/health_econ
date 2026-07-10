from __future__ import annotations

import csv
import hashlib
import re
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from typing import Any
from urllib.parse import quote, urlparse

import requests

from common import REPORT_DIR, RESULT_DIR, TEMP_DIR, append_log, ensure_dirs, utc_now_iso, write_csv


BOARD_PATH = TEMP_DIR / "priority_lsms_isa_manual_download_execution_board.csv"
CORE_PATH = TEMP_DIR / "priority_lsms_isa_manual_download_packet_core_files.csv"
INVENTORY_PATH = TEMP_DIR / "priority_lsms_isa_public_documentation_file_inventory.csv"

PROBE_PATH = TEMP_DIR / "priority_lsms_isa_resource_download_route_probe.csv"
SUMMARY_PATH = RESULT_DIR / "priority_lsms_isa_resource_download_route_probe_summary.csv"
REPORT_PATH = REPORT_DIR / "priority_lsms_isa_resource_download_route_probe.md"

USER_AGENT = "Codex climate_uhc_ml LSMS-ISA resource route probe"
TIMEOUT = 30
MAX_BYTES = 256 * 1024
MAX_FILES_PER_DATASET = 4
MAX_WORKERS = 4
REQUEST_RETRIES = 2

RAW_SUFFIXES = {
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
RAW_CONTENT_HINTS = (
    "application/zip",
    "application/x-zip",
    "application/x-7z",
    "application/rar",
    "application/octet-stream",
    "application/x-stata",
    "application/vnd.ms-excel",
)
HTML_HINTS = ("text/html", "application/xhtml")
GATE_HINTS = (
    "login",
    "log in",
    "sign in",
    "register",
    "registration",
    "terms",
    "data access agreement",
    "licensed",
    "request access",
)

ROUTES = [
    (
        "catalog_download_file_id_path",
        "https://microdata.worldbank.org/catalog/{catalog_id}/download/{file_id}",
        "numeric catalog file-id download path",
    ),
    (
        "index_catalog_download_file_id_path",
        "https://microdata.worldbank.org/index.php/catalog/{catalog_id}/download/{file_id}",
        "index.php numeric catalog file-id download path",
    ),
    (
        "catalog_download_file_id_filename_query",
        "https://microdata.worldbank.org/catalog/{catalog_id}/download/{file_id}?file_name={file_name_quoted}",
        "numeric catalog file-id route with filename query",
    ),
    (
        "index_catalog_download_file_id_filename_query",
        "https://microdata.worldbank.org/index.php/catalog/{catalog_id}/download/{file_id}?file_name={file_name_quoted}",
        "index.php numeric catalog file-id route with filename query",
    ),
    (
        "catalog_data_dictionary_file_id_filename_query",
        "https://microdata.worldbank.org/catalog/{catalog_id}/data-dictionary/{file_id}?file_name={file_name_quoted}",
        "numeric catalog data-dictionary file page",
    ),
    (
        "index_catalog_data_dictionary_file_id_filename_query",
        "https://microdata.worldbank.org/index.php/catalog/{catalog_id}/data-dictionary/{file_id}?file_name={file_name_quoted}",
        "index.php numeric catalog data-dictionary file page",
    ),
]

PROBE_COLUMNS = [
    "probe_time",
    "download_rank",
    "country",
    "wave",
    "idno",
    "catalog_id",
    "sample_file_rank",
    "file_id",
    "file_name",
    "file_description",
    "route_name",
    "route_role",
    "url",
    "request_attempted",
    "http_status",
    "final_url",
    "content_type",
    "content_length_header",
    "content_disposition",
    "bytes_read",
    "truncated",
    "content_sha256_limited",
    "route_classification",
    "raw_payload_candidate",
    "access_gate_detected",
    "data_dictionary_html_detected",
    "evidence_flags",
    "next_action",
    "data_write_gate_status",
    "modeling_gate_status",
]

SUMMARY_COLUMNS = ["metric", "value", "interpretation"]


def read_csv_dicts(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        return []
    with path.open(encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def clean(value: Any) -> str:
    if value is None:
        return ""
    return " ".join(str(value).split())


def safe_int(value: Any, default: int = 0) -> int:
    try:
        text = clean(value)
        return int(float(text)) if text else default
    except (TypeError, ValueError):
        return default


def summary_row(metric: str, value: Any, interpretation: str) -> dict[str, str]:
    return {"metric": metric, "value": str(value), "interpretation": interpretation}


def sha256_bytes(content: bytes) -> str:
    return hashlib.sha256(content).hexdigest() if content else ""


def suffix_from_disposition(disposition: str) -> str:
    match = re.search(r'filename="?([^";]+)"?', disposition, flags=re.IGNORECASE)
    if not match:
        return ""
    return Path(match.group(1)).suffix.lower()


def extension_from_url(url: str) -> str:
    return Path(clean(url).split("?", 1)[0].split("#", 1)[0]).suffix.lower()


def response_is_raw(url: str, content_type: str, disposition: str) -> bool:
    low_type = content_type.lower()
    low_disp = disposition.lower()
    parsed_suffix = Path(urlparse(url).path).suffix.lower()
    disp_suffix = suffix_from_disposition(disposition)
    return (
        parsed_suffix in RAW_SUFFIXES
        or disp_suffix in RAW_SUFFIXES
        or any(hint in low_type for hint in RAW_CONTENT_HINTS)
        or ("attachment" in low_disp and not any(hint in low_type for hint in HTML_HINTS))
    )


def decode_text(content: bytes, response: requests.Response) -> str:
    return content.decode(response.encoding or "utf-8", errors="replace") if content else ""


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


def inventory_lookup(rows: list[dict[str, str]]) -> dict[tuple[str, str], dict[str, str]]:
    lookup: dict[tuple[str, str], dict[str, str]] = {}
    for row in rows:
        idno = clean(row.get("idno"))
        file_id = clean(row.get("file_id"))
        if idno and file_id:
            lookup[(idno, file_id)] = row
    return lookup


def select_sample_files(
    board_rows: list[dict[str, str]],
    core_rows: list[dict[str, str]],
    inventory_rows: list[dict[str, str]],
) -> list[dict[str, str]]:
    board_by_id = {clean(row.get("idno")): row for row in board_rows if clean(row.get("idno"))}
    lookup = inventory_lookup(inventory_rows)
    by_id: dict[str, list[dict[str, str]]] = {}
    for row in core_rows:
        idno = clean(row.get("idno"))
        if idno in board_by_id:
            by_id.setdefault(idno, []).append(row)

    sample_rows: list[dict[str, str]] = []
    for idno, rows in by_id.items():
        seen: set[str] = set()
        selected = 0
        for core in sorted(rows, key=lambda r: safe_int(r.get("file_rank"), 9999)):
            file_id = clean(core.get("file_id"))
            if not file_id or file_id in seen:
                continue
            seen.add(file_id)
            inventory = lookup.get((idno, file_id), {})
            board = board_by_id[idno]
            catalog_id = clean(inventory.get("catalog_id"))
            file_name = clean(inventory.get("file_name")) or clean(core.get("expected_file_name"))
            if not catalog_id or not file_name:
                continue
            selected += 1
            sample_rows.append(
                {
                    "download_rank": clean(board.get("download_rank")) or clean(core.get("download_rank")),
                    "country": clean(board.get("country")) or clean(core.get("country")),
                    "wave": clean(board.get("wave")) or clean(core.get("wave")),
                    "idno": idno,
                    "catalog_id": catalog_id,
                    "sample_file_rank": str(selected),
                    "file_id": file_id,
                    "file_name": file_name,
                    "file_description": clean(inventory.get("file_description")) or clean(core.get("file_description")),
                }
            )
            if selected >= MAX_FILES_PER_DATASET:
                break
    return sorted(sample_rows, key=lambda r: (safe_int(r.get("download_rank"), 9999), safe_int(r.get("sample_file_rank"), 9999)))


def classify_response(
    route_name: str,
    url: str,
    response: requests.Response | None,
    content: bytes,
    request_error: str = "",
) -> tuple[str, str, str, str, str, str]:
    if response is None:
        return "request_failed", "0", "0", "0", "request_error", f"Retry route probe if network is available. Error: {request_error}"

    content_type = response.headers.get("content-type", "")
    disposition = response.headers.get("content-disposition", "")
    text = decode_text(content, response)
    low = text.lower()
    gate = "1" if any(hint in low for hint in GATE_HINTS) else "0"
    dictionary_route = "data_dictionary" in route_name or "data-dictionary" in response.url.lower()
    dictionary_html = "1" if dictionary_route and any(hint in content_type.lower() for hint in HTML_HINTS) else "0"
    raw = "1" if response_is_raw(response.url or url, content_type, disposition) else "0"
    flags = ";".join(
        flag
        for flag, active in [
            ("raw_header_or_suffix", raw == "1"),
            ("access_gate_language", gate == "1"),
            ("data_dictionary_html", dictionary_html == "1"),
            ("html_response", any(hint in content_type.lower() for hint in HTML_HINTS)),
            ("empty_body", not content),
        ]
        if active
    )

    if response.status_code >= 400:
        return "resource_http_error", raw, gate, dictionary_html, flags, "Use official get-microdata workflow; this resource route did not expose public raw payload."
    if raw == "1" and gate == "0":
        return "resource_raw_payload_candidate", raw, gate, dictionary_html, flags, "Manual terms review is required before any download; do not promote from route probe alone."
    if raw == "1" and gate == "1":
        return "resource_access_gate_or_terms_html", raw, gate, dictionary_html, flags, "Complete official login and terms workflow before acquiring complete raw package."
    if dictionary_html == "1":
        return "resource_data_dictionary_html_not_raw", raw, gate, dictionary_html, flags, "Use as metadata evidence only; raw package receipt remains missing."
    if any(hint in content_type.lower() for hint in HTML_HINTS) and gate == "1":
        return "resource_access_gate_or_terms_html", raw, gate, dictionary_html, flags, "Complete official login and terms workflow before acquiring complete raw package."
    if any(hint in content_type.lower() for hint in HTML_HINTS):
        return "resource_non_raw_html", raw, gate, dictionary_html, flags, "No raw package accepted; continue credentialed/manual acquisition."
    if not content:
        return "resource_empty_or_no_payload", raw, gate, dictionary_html, flags, "No raw payload returned; continue credentialed/manual acquisition."
    return "resource_non_raw_response", raw, gate, dictionary_html, flags, "Manual review required; no raw package accepted from route probe."


def probe_route(sample: dict[str, str], route_name: str, template: str, route_role: str) -> dict[str, str]:
    file_name = clean(sample.get("file_name"))
    url = template.format(
        catalog_id=quote(clean(sample.get("catalog_id"))),
        file_id=quote(clean(sample.get("file_id"))),
        file_name_quoted=quote(file_name),
    )
    base = {
        "probe_time": utc_now_iso(),
        **sample,
        "route_name": route_name,
        "route_role": route_role,
        "url": url,
        "request_attempted": "1",
        "http_status": "",
        "final_url": "",
        "content_type": "",
        "content_length_header": "",
        "content_disposition": "",
        "bytes_read": "0",
        "truncated": "0",
        "content_sha256_limited": "",
        "route_classification": "",
        "raw_payload_candidate": "0",
        "access_gate_detected": "0",
        "data_dictionary_html_detected": "0",
        "evidence_flags": "",
        "next_action": "",
        "data_write_gate_status": "blocked_no_data_write",
        "modeling_gate_status": "blocked",
    }
    last_error = ""
    for attempt in range(REQUEST_RETRIES + 1):
        try:
            with requests.get(url, headers={"User-Agent": USER_AGENT}, timeout=TIMEOUT, stream=True, allow_redirects=True) as response:
                content, truncated = read_limited(response)
                classification, raw, gate, dictionary_html, flags, next_action = classify_response(route_name, url, response, content)
                base.update(
                    {
                        "http_status": str(response.status_code),
                        "final_url": response.url,
                        "content_type": response.headers.get("content-type", ""),
                        "content_length_header": response.headers.get("content-length", ""),
                        "content_disposition": response.headers.get("content-disposition", ""),
                        "bytes_read": str(len(content)),
                        "truncated": truncated,
                        "content_sha256_limited": sha256_bytes(content),
                        "route_classification": classification,
                        "raw_payload_candidate": raw,
                        "access_gate_detected": gate,
                        "data_dictionary_html_detected": dictionary_html,
                        "evidence_flags": flags,
                        "next_action": next_action,
                    }
                )
                return base
        except requests.RequestException as exc:
            last_error = str(exc)
            if attempt < REQUEST_RETRIES:
                continue
    classification, raw, gate, dictionary_html, flags, next_action = classify_response(route_name, url, None, b"", last_error)
    base.update(
        {
            "route_classification": classification,
            "raw_payload_candidate": raw,
            "access_gate_detected": gate,
            "data_dictionary_html_detected": dictionary_html,
            "evidence_flags": flags,
            "next_action": next_action,
        }
    )
    return base


def build_probe_rows(sample_files: list[dict[str, str]]) -> list[dict[str, str]]:
    jobs: list[tuple[int, dict[str, str], str, str, str]] = []
    rank = 0
    for sample in sample_files:
        for route_name, template, route_role in ROUTES:
            rank += 1
            jobs.append((rank, sample, route_name, template, route_role))

    rows_by_rank: dict[int, dict[str, str]] = {}
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        futures = {executor.submit(probe_route, sample, route_name, template, route_role): rank for rank, sample, route_name, template, route_role in jobs}
        for future in as_completed(futures):
            rows_by_rank[futures[future]] = future.result()
    return [rows_by_rank[rank] for rank in sorted(rows_by_rank)]


def build_summary(sample_files: list[dict[str, str]], probe_rows: list[dict[str, str]]) -> list[dict[str, str]]:
    dataset_count = len({row.get("idno", "") for row in sample_files if row.get("idno")})
    route_rows = len(probe_rows)
    raw_rows = sum(1 for row in probe_rows if row.get("raw_payload_candidate") == "1")
    access_rows = sum(1 for row in probe_rows if row.get("access_gate_detected") == "1" or row.get("route_classification") == "resource_access_gate_or_terms_html")
    dictionary_rows = sum(1 for row in probe_rows if row.get("data_dictionary_html_detected") == "1")
    http_error_rows = sum(1 for row in probe_rows if row.get("route_classification") == "resource_http_error")
    request_failed_rows = sum(1 for row in probe_rows if row.get("route_classification") == "request_failed")
    non_raw_html_rows = sum(1 for row in probe_rows if row.get("route_classification") == "resource_non_raw_html")
    empty_rows = sum(1 for row in probe_rows if row.get("route_classification") == "resource_empty_or_no_payload")

    return [
        summary_row("resource_download_route_probe_scope", "bounded_route_family_smoke_test", "The probe samples core files and route templates; it is not a full raw-package download."),
        summary_row("resource_download_route_probe_max_files_per_dataset", MAX_FILES_PER_DATASET, "Maximum distinct core files probed per manual-download packet."),
        summary_row("resource_download_route_probe_route_templates", len(ROUTES), "Route templates probed for each sampled core file."),
        summary_row("resource_download_route_probe_datasets", dataset_count, "Manual-download packet datasets covered by the resource-level route probe."),
        summary_row("resource_download_route_probe_sampled_files", len(sample_files), "Distinct core files sampled from the manual-download packets."),
        summary_row("resource_download_route_probe_route_rows", route_rows, "Constructed resource-level download/data-dictionary route rows probed."),
        summary_row("resource_download_route_probe_request_attempted_rows", sum(1 for row in probe_rows if row.get("request_attempted") == "1"), "HTTP request attempts made by the probe."),
        summary_row("resource_download_route_probe_raw_payload_candidate_rows", raw_rows, "Rows whose headers or URL suffix suggested a raw payload candidate."),
        summary_row("resource_download_route_probe_access_gate_rows", access_rows, "Rows with login, registration, terms, or data access gate evidence."),
        summary_row("resource_download_route_probe_data_dictionary_html_rows", dictionary_rows, "Rows returning data-dictionary HTML rather than raw payload."),
        summary_row("resource_download_route_probe_http_error_rows", http_error_rows, "Rows returning HTTP errors rather than public raw payloads."),
        summary_row("resource_download_route_probe_request_failed_rows", request_failed_rows, "Rows where the request failed before classification."),
        summary_row("resource_download_route_probe_non_raw_html_rows", non_raw_html_rows, "Rows returning non-raw HTML without accepted raw payload evidence."),
        summary_row("resource_download_route_probe_empty_or_no_payload_rows", empty_rows, "Rows returning no body or no accepted payload."),
        summary_row("data_write_gate_status", "blocked_no_data_write", "The route probe does not save raw files or write promoted data."),
        summary_row("modeling_gate_status", "blocked", "No predictive, reduced-form, causal ML, or policy learning until registry thresholds pass."),
    ]


def markdown_table(rows: list[dict[str, str]], columns: list[str], limit: int = 30) -> str:
    if not rows:
        return "_No rows._"
    lines = ["| " + " | ".join(columns) + " |", "| " + " | ".join("---" for _ in columns) + " |"]
    for row in rows[:limit]:
        lines.append("| " + " | ".join(clean(row.get(column)).replace("|", "/") for column in columns) + " |")
    if len(rows) > limit:
        lines.append("| " + " | ".join("..." for _ in columns) + " |")
    return "\n".join(lines)


def write_report(sample_files: list[dict[str, str]], probe_rows: list[dict[str, str]], summary_rows: list[dict[str, str]]) -> None:
    metric = {row["metric"]: row["value"] for row in summary_rows}
    dataset_rows: list[dict[str, str]] = []
    for idno in sorted({row.get("idno", "") for row in sample_files if row.get("idno")}):
        rows = [row for row in probe_rows if row.get("idno") == idno]
        sample = next((row for row in sample_files if row.get("idno") == idno), {})
        dataset_rows.append(
            {
                "download_rank": clean(sample.get("download_rank")),
                "country": clean(sample.get("country")),
                "wave": clean(sample.get("wave")),
                "idno": idno,
                "sampled_files": str(len({row.get("file_id", "") for row in rows if row.get("file_id")})),
                "route_rows": str(len(rows)),
                "raw_payload_candidates": str(sum(1 for row in rows if row.get("raw_payload_candidate") == "1")),
                "access_gate_rows": str(sum(1 for row in rows if row.get("access_gate_detected") == "1" or row.get("route_classification") == "resource_access_gate_or_terms_html")),
                "data_dictionary_html_rows": str(sum(1 for row in rows if row.get("data_dictionary_html_detected") == "1")),
                "http_error_rows": str(sum(1 for row in rows if row.get("route_classification") == "resource_http_error")),
            }
        )

    lines = [
        "# Priority LSMS-ISA Resource Download Route Probe",
        "",
        "Status: bounded resource-level route-family smoke test for the 10 manual-download packets.",
        "",
        "The probe constructs official World Bank catalog file-id download and data-dictionary URL patterns for up to four core files per dataset. It reads only a limited response sample, does not save raw payloads, does not use cookies or private headers, and does not write promoted `data/`.",
        "",
        "This is not a substitute for official credentialed package acquisition. It is a fail-closed evidence layer showing whether common public resource routes expose accepted raw payloads.",
        "",
        "## Summary",
        "",
        f"- Datasets covered: {metric.get('resource_download_route_probe_datasets', '0')}",
        f"- Sampled core files: {metric.get('resource_download_route_probe_sampled_files', '0')}",
        f"- Route rows probed: {metric.get('resource_download_route_probe_route_rows', '0')}",
        f"- Raw payload candidates: {metric.get('resource_download_route_probe_raw_payload_candidate_rows', '0')}",
        f"- Access-gate rows: {metric.get('resource_download_route_probe_access_gate_rows', '0')}",
        f"- Data-dictionary HTML rows: {metric.get('resource_download_route_probe_data_dictionary_html_rows', '0')}",
        f"- HTTP-error rows: {metric.get('resource_download_route_probe_http_error_rows', '0')}",
        f"- Data-write gate: {metric.get('data_write_gate_status', 'missing')}",
        f"- Modeling gate: {metric.get('modeling_gate_status', 'missing')}",
        "",
        "## Dataset Route Status",
        "",
        markdown_table(dataset_rows, ["download_rank", "country", "wave", "idno", "sampled_files", "route_rows", "raw_payload_candidates", "access_gate_rows", "data_dictionary_html_rows", "http_error_rows"], 20),
        "",
        "## Route Sample",
        "",
        markdown_table(probe_rows, ["download_rank", "idno", "file_id", "file_name", "route_name", "http_status", "route_classification", "raw_payload_candidate"], 60),
        "",
        "## Guardrails",
        "",
        "- No raw files are saved.",
        "- No cookies, tokens, private headers, or user credentials are read.",
        "- No promoted dataset is written.",
        "- The result cannot promote a wave; it can only support the access-route decision.",
    ]
    REPORT_PATH.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    ensure_dirs()
    board_rows = read_csv_dicts(BOARD_PATH)
    core_rows = read_csv_dicts(CORE_PATH)
    inventory_rows = read_csv_dicts(INVENTORY_PATH)
    sample_files = select_sample_files(board_rows, core_rows, inventory_rows)
    probe_rows = build_probe_rows(sample_files)
    summary_rows = build_summary(sample_files, probe_rows)

    write_csv(PROBE_PATH, probe_rows, PROBE_COLUMNS)
    write_csv(SUMMARY_PATH, summary_rows, SUMMARY_COLUMNS)
    write_report(sample_files, probe_rows, summary_rows)
    append_log(TEMP_DIR / "audit_log.md", f"Built priority LSMS/ISA resource download route probe: {len(probe_rows)} route rows, {len(sample_files)} sampled files.")


if __name__ == "__main__":
    main()
