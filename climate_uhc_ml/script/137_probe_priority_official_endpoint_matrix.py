from __future__ import annotations

import csv
import hashlib
import json
import re
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any
from urllib.parse import urljoin

import requests

from common import PROJECT_ROOT, REPORT_DIR, RESULT_DIR, TEMP_DIR, append_log, ensure_dirs, utc_now_iso, write_csv


WAVE_PLAN_PATH = RESULT_DIR / "priority_promotion_acquisition_wave_plan.csv"
DOSSIER_PATH = TEMP_DIR / "priority_official_download_dossier.csv"

MATRIX_PATH = TEMP_DIR / "priority_official_endpoint_matrix.csv"
DATASET_PATH = TEMP_DIR / "priority_official_endpoint_dataset_matrix.csv"
SUMMARY_PATH = RESULT_DIR / "priority_official_endpoint_matrix_summary.csv"
REPORT_PATH = REPORT_DIR / "priority_official_endpoint_matrix.md"

RAW_ROOT = TEMP_DIR / "raw_downloads"

USER_AGENT = "Codex climate_uhc_ml priority official endpoint matrix"
TIMEOUT = 45
MAX_BYTES = 512 * 1024

DATA_EXTENSIONS = {".dta", ".sav", ".por", ".sas7bdat", ".xpt", ".csv", ".tsv", ".zip", ".tar", ".gz", ".tgz", ".7z", ".rar"}
GATE_HINTS = ["login", "log in", "sign in", "register", "registration", "terms", "data access agreement", "licensed", "request access"]
METADATA_HINTS = ["metadata", "data-dictionary", "study-description", "related-materials", "variables", "ddi", "json"]

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

MATRIX_COLUMNS = [
    "probe_time",
    "acquisition_batch_rank",
    "batch_role",
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
    "bytes_read",
    "truncated",
    "content_sha256_limited",
    "endpoint_classification",
    "raw_download_candidate",
    "access_gate_detected",
    "metadata_endpoint_detected",
    "json_status",
    "json_top_level_keys",
    "candidate_links",
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
    "endpoint_rows",
    "successful_public_metadata_endpoints",
    "successful_variable_api_endpoints",
    "get_microdata_gate_endpoints",
    "raw_download_candidate_endpoints",
    "numeric_api_bad_request_endpoints",
    "credentialed_download_required",
    "endpoint_matrix_status",
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


def safe_name(text: str) -> str:
    return re.sub(r"[^A-Za-z0-9._-]+", "_", text).strip("_")[:140] or "item"


def one_by_id(rows: list[dict[str, str]], field: str = "idno") -> dict[str, dict[str, str]]:
    out: dict[str, dict[str, str]] = {}
    for row in rows:
        idno = clean(row.get(field))
        if idno and idno not in out:
            out[idno] = row
    return out


def rel(path: Path) -> str:
    try:
        return str(path.relative_to(PROJECT_ROOT)).replace("\\", "/")
    except ValueError:
        return str(path).replace("\\", "/")


def read_limited(response: requests.Response) -> tuple[bytes, str]:
    chunks: list[bytes] = []
    total = 0
    truncated = "0"
    for chunk in response.iter_content(chunk_size=64 * 1024):
        if not chunk:
            continue
        if total + len(chunk) > MAX_BYTES:
            chunks.append(chunk[: max(0, MAX_BYTES - total)])
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


def extract_links(base_url: str, html: str) -> list[str]:
    links = []
    seen = set()
    for href in re.findall(r"""href=["']([^"']+)["']""", html, flags=re.IGNORECASE):
        url = urljoin(base_url, href)
        low = url.lower()
        if any(ext in low for ext in DATA_EXTENSIONS) or any(token in low for token in ["download", "get-microdata", "metadata/export", "data-dictionary"]):
            if url not in seen:
                links.append(url)
                seen.add(url)
        if len(links) >= 20:
            break
    return links


def classify_endpoint(endpoint_name: str, url: str, response: requests.Response | None, content: bytes, error_status: str = "") -> tuple[str, str, str, str, str, str, str]:
    if response is None:
        return "request_failed_or_http_error", "0", "0", "0", "", "", "Retry endpoint or inspect manually."
    status = response.status_code
    content_type = response.headers.get("content-type", "").lower()
    disposition = response.headers.get("content-disposition", "").lower()
    text = decode_text(content, response)
    low = text.lower()
    links = extract_links(response.url or url, text) if "html" in content_type else []
    suffix = extension_from_url(response.url or url)
    raw_candidate = "1" if (
        suffix in DATA_EXTENSIONS
        or any(ext in disposition for ext in DATA_EXTENSIONS)
        or any(extension_from_url(link) in DATA_EXTENSIONS for link in links)
    ) else "0"
    gate = "1" if any(hint in low for hint in GATE_HINTS) else "0"
    metadata = "1" if any(hint in endpoint_name.lower() or hint in (response.url or url).lower() for hint in METADATA_HINTS) else "0"
    json_status = ""
    json_keys = ""
    if "json" in content_type or text.lstrip().startswith("{"):
        try:
            data = json.loads(text)
            json_status = "valid_json"
            if isinstance(data, dict):
                json_keys = ";".join(list(data.keys())[:12])
        except Exception:
            json_status = "invalid_or_truncated_json"

    if status >= 400:
        classification = "http_error_not_public_endpoint"
        next_action = "Use IDNO API or official get-microdata page; do not treat this as raw access."
    elif raw_candidate == "1" and gate == "0":
        classification = "possible_public_raw_endpoint_needs_terms_review"
        next_action = "Manually inspect link and terms before any download."
    elif endpoint_name == "numeric_get_microdata_page" and gate == "1":
        classification = "official_get_microdata_access_gate"
        next_action = "Use official login/register/terms workflow and download complete raw package."
    elif endpoint_name in {"catalog_idno_api", "variables_idno_api", "metadata_ddi_export", "metadata_json_export"} and status == 200:
        classification = "public_metadata_endpoint_not_raw_package"
        next_action = "Use as metadata evidence only; raw package still requires credentialed download."
    elif endpoint_name == "numeric_download_page" and status == 200 and len(content) == 0:
        classification = "empty_download_route_not_raw_package"
        next_action = "Use official get-microdata workflow; no public raw payload returned."
    elif endpoint_name == "idno_get_microdata_page" and status == 200:
        classification = "idno_route_returns_catalog_or_search_html_not_raw_package"
        next_action = "Use numeric catalog get-microdata URL for official access workflow."
    else:
        classification = "non_raw_endpoint_manual_review"
        next_action = "Review endpoint manually; no raw package evidence accepted."
    return classification, raw_candidate, gate, metadata, json_status, json_keys, next_action


def probe_endpoint(wave: dict[str, str], endpoint_name: str, template: str, role: str, catalog_id: str) -> dict[str, str]:
    url = template.format(catalog_id=catalog_id, idno=wave.get("idno", ""))
    base = {
        "probe_time": utc_now_iso(),
        "acquisition_batch_rank": wave.get("acquisition_batch_rank", ""),
        "batch_role": wave.get("batch_role", ""),
        "country": wave.get("country", ""),
        "wave": wave.get("wave", ""),
        "idno": wave.get("idno", ""),
        "catalog_id": catalog_id,
        "endpoint_name": endpoint_name,
        "endpoint_url": url,
        "endpoint_role": role,
        "http_status": "",
        "final_url": "",
        "content_type": "",
        "content_length_header": "",
        "bytes_read": "0",
        "truncated": "0",
        "content_sha256_limited": "",
        "endpoint_classification": "",
        "raw_download_candidate": "0",
        "access_gate_detected": "0",
        "metadata_endpoint_detected": "0",
        "json_status": "",
        "json_top_level_keys": "",
        "candidate_links": "",
        "evidence_snippet": "",
        "next_action": "",
    }
    try:
        with requests.get(url, headers={"User-Agent": USER_AGENT}, timeout=TIMEOUT, stream=True, allow_redirects=True) as response:
            content, truncated = read_limited(response)
            text = decode_text(content, response)
            classification, raw_candidate, gate, metadata, json_status, json_keys, next_action = classify_endpoint(endpoint_name, url, response, content)
            links = extract_links(response.url or url, text) if "html" in response.headers.get("content-type", "").lower() else []
            base.update(
                {
                    "http_status": str(response.status_code),
                    "final_url": response.url,
                    "content_type": response.headers.get("content-type", ""),
                    "content_length_header": response.headers.get("content-length", ""),
                    "bytes_read": str(len(content)),
                    "truncated": truncated,
                    "content_sha256_limited": hashlib.sha256(content).hexdigest() if content else "",
                    "endpoint_classification": classification,
                    "raw_download_candidate": raw_candidate,
                    "access_gate_detected": gate,
                    "metadata_endpoint_detected": metadata,
                    "json_status": json_status,
                    "json_top_level_keys": json_keys,
                    "candidate_links": ";".join(links[:12]),
                    "evidence_snippet": " ".join(text[:220].split()),
                    "next_action": next_action,
                }
            )
    except Exception as exc:
        base["endpoint_classification"] = "request_failed_or_http_error"
        base["evidence_snippet"] = str(exc)[:220]
        base["next_action"] = "Retry endpoint or inspect manually."
    return base


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


def write_handoff(dataset_row: dict[str, str], endpoint_rows: list[dict[str, str]]) -> str:
    folder = raw_folder_path(dataset_row.get("idno", ""))
    folder.mkdir(parents=True, exist_ok=True)
    path = folder / "_PRIORITY_OFFICIAL_ENDPOINT_MATRIX.md"
    path.write_text(
        f"""# Priority Official Endpoint Matrix

Dataset: {dataset_row.get('idno', '')} - {dataset_row.get('country', '')} {dataset_row.get('wave', '')}

Status: {dataset_row.get('endpoint_matrix_status', '')}

Endpoint rows: {dataset_row.get('endpoint_rows', '0')}

Public metadata endpoints: {dataset_row.get('successful_public_metadata_endpoints', '0')}

Variable API endpoints: {dataset_row.get('successful_variable_api_endpoints', '0')}

Get-microdata access gates: {dataset_row.get('get_microdata_gate_endpoints', '0')}

Raw download candidate endpoints: {dataset_row.get('raw_download_candidate_endpoints', '0')}

Credentialed download required: {dataset_row.get('credentialed_download_required', '')}

## Endpoint Preview

{markdown_table(endpoint_rows, ['endpoint_name', 'http_status', 'endpoint_classification', 'raw_download_candidate', 'access_gate_detected'], 12)}

Guardrail: public API/metadata endpoints are metadata evidence only. They do
not replace the complete unchanged official raw package.
""",
        encoding="utf-8",
    )
    return rel(path)


def build_outputs() -> tuple[list[dict[str, str]], list[dict[str, str]], list[dict[str, str]]]:
    dossier_by_id = one_by_id(read_csv_dicts(DOSSIER_PATH))
    endpoint_rows: list[dict[str, str]] = []
    endpoint_by_id: dict[str, list[dict[str, str]]] = defaultdict(list)
    for wave in read_csv_dicts(WAVE_PLAN_PATH):
        catalog_id = dossier_by_id.get(wave.get("idno", ""), {}).get("catalog_id", "")
        for endpoint_name, template, role in ENDPOINTS:
            row = probe_endpoint(wave, endpoint_name, template, role, catalog_id)
            endpoint_rows.append(row)
            endpoint_by_id[wave.get("idno", "")].append(row)

    dataset_rows: list[dict[str, str]] = []
    for idno, rows in endpoint_by_id.items():
        first = rows[0]
        public_metadata = sum(1 for row in rows if row["endpoint_classification"] == "public_metadata_endpoint_not_raw_package")
        variable_api = sum(1 for row in rows if row["endpoint_name"] == "variables_idno_api" and row["http_status"] == "200" and row["json_status"] == "valid_json")
        gate_rows = sum(1 for row in rows if row["endpoint_classification"] == "official_get_microdata_access_gate")
        raw_candidates = sum(1 for row in rows if row["raw_download_candidate"] == "1")
        numeric_bad = sum(1 for row in rows if row["endpoint_name"] == "catalog_numeric_api" and row["endpoint_classification"] == "http_error_not_public_endpoint")
        status = (
            "metadata_api_confirmed_raw_access_gate_confirmed"
            if public_metadata >= 3 and gate_rows >= 1 and raw_candidates == 0
            else "endpoint_matrix_needs_manual_review"
        )
        dataset_row = {
            "acquisition_batch_rank": first.get("acquisition_batch_rank", ""),
            "batch_role": first.get("batch_role", ""),
            "country": first.get("country", ""),
            "wave": first.get("wave", ""),
            "idno": idno,
            "catalog_id": first.get("catalog_id", ""),
            "endpoint_rows": str(len(rows)),
            "successful_public_metadata_endpoints": str(public_metadata),
            "successful_variable_api_endpoints": str(variable_api),
            "get_microdata_gate_endpoints": str(gate_rows),
            "raw_download_candidate_endpoints": str(raw_candidates),
            "numeric_api_bad_request_endpoints": str(numeric_bad),
            "credentialed_download_required": "1" if raw_candidates == 0 and gate_rows >= 1 else "0",
            "endpoint_matrix_status": status,
            "handoff_readme": "",
        }
        dataset_row["handoff_readme"] = write_handoff(dataset_row, rows)
        dataset_rows.append(dataset_row)
    dataset_rows.sort(key=lambda row: int(row.get("acquisition_batch_rank") or 9999))
    summary = build_summary(endpoint_rows, dataset_rows)
    return endpoint_rows, dataset_rows, summary


def build_summary(endpoint_rows: list[dict[str, str]], dataset_rows: list[dict[str, str]]) -> list[dict[str, str]]:
    classification_counts = Counter(row["endpoint_classification"] for row in endpoint_rows)
    rows = [
        {"metric": "priority_endpoint_matrix_dataset_rows", "value": str(len(dataset_rows)), "interpretation": "Priority and backup datasets with endpoint matrix rows."},
        {"metric": "priority_endpoint_matrix_endpoint_rows", "value": str(len(endpoint_rows)), "interpretation": "Official endpoint probes across priority and backup datasets."},
        {"metric": "priority_endpoint_matrix_public_metadata_endpoint_rows", "value": str(sum(int(row["successful_public_metadata_endpoints"]) for row in dataset_rows)), "interpretation": "Dataset-level count of successful public metadata endpoint hits."},
        {"metric": "priority_endpoint_matrix_variable_api_dataset_rows", "value": str(sum(1 for row in dataset_rows if int(row["successful_variable_api_endpoints"]) > 0)), "interpretation": "Datasets with a public variable metadata API endpoint."},
        {"metric": "priority_endpoint_matrix_get_microdata_gate_dataset_rows", "value": str(sum(1 for row in dataset_rows if int(row["get_microdata_gate_endpoints"]) > 0)), "interpretation": "Datasets whose official get-microdata endpoint shows an access gate."},
        {"metric": "priority_endpoint_matrix_raw_download_candidate_rows", "value": str(sum(int(row["raw_download_candidate_endpoints"]) for row in dataset_rows)), "interpretation": "Raw download candidate endpoints detected without accepting them as usable."},
        {"metric": "priority_endpoint_matrix_credentialed_download_required_rows", "value": str(sum(1 for row in dataset_rows if row["credentialed_download_required"] == "1")), "interpretation": "Datasets requiring credentialed download after endpoint matrix review."},
        {"metric": "priority_endpoint_matrix_handoff_readmes_written", "value": str(sum(1 for row in dataset_rows if row.get("handoff_readme"))), "interpretation": "Per-wave official endpoint matrix handoffs written."},
        {"metric": "modeling_gate_status", "value": "blocked", "interpretation": "Endpoint matrix evidence does not satisfy raw receipt, raw value verification, or climate-linkage gates."},
    ]
    for status, count in sorted(classification_counts.items()):
        rows.append({"metric": f"priority_endpoint_matrix_classification_{status}", "value": str(count), "interpretation": "Endpoint classification count."})
    return rows


def write_report(endpoint_rows: list[dict[str, str]], dataset_rows: list[dict[str, str]], summary: list[dict[str, str]]) -> None:
    summary_table = "\n".join(f"| {row['metric']} | {row['value']} | {row['interpretation']} |" for row in summary)
    REPORT_PATH.write_text(
        f"""# Priority Official Endpoint Matrix

Status: official endpoint matrix for priority raw acquisition. This probes
World Bank catalog/API/metadata/get-microdata routes and classifies whether
they provide metadata, access-gated raw acquisition pages, empty/non-raw routes,
or possible raw download candidates. It does not download raw microdata.

## Summary

| Metric | Value | Interpretation |
|---|---:|---|
{summary_table}

## Dataset Matrix

{markdown_table(dataset_rows, ['acquisition_batch_rank', 'idno', 'endpoint_rows', 'successful_public_metadata_endpoints', 'successful_variable_api_endpoints', 'get_microdata_gate_endpoints', 'raw_download_candidate_endpoints', 'credentialed_download_required', 'endpoint_matrix_status'], 20)}

## Endpoint Preview

{markdown_table(endpoint_rows, ['acquisition_batch_rank', 'idno', 'endpoint_name', 'http_status', 'endpoint_classification', 'raw_download_candidate', 'access_gate_detected'], 40)}

## Guardrail

Public IDNO catalog, variable, DDI, and JSON routes are metadata endpoints. They
are useful for variable screening and acquisition planning, but they are not the
complete original raw package. The official numeric get-microdata page remains
the credentialed raw acquisition route when an access gate is present.

## Machine-Readable Outputs

- `temp/priority_official_endpoint_matrix.csv`
- `temp/priority_official_endpoint_dataset_matrix.csv`
- `result/priority_official_endpoint_matrix_summary.csv`
""",
        encoding="utf-8",
    )


def main() -> None:
    ensure_dirs()
    endpoint_rows, dataset_rows, summary = build_outputs()
    write_csv(MATRIX_PATH, endpoint_rows, MATRIX_COLUMNS)
    write_csv(DATASET_PATH, dataset_rows, DATASET_COLUMNS)
    write_csv(SUMMARY_PATH, summary, SUMMARY_COLUMNS)
    write_report(endpoint_rows, dataset_rows, summary)
    append_log(
        TEMP_DIR / "audit_log.md",
        f"Built priority official endpoint matrix endpoints={len(endpoint_rows)} datasets={len(dataset_rows)}.",
    )
    print(f"Priority official endpoint matrix endpoints={len(endpoint_rows)} datasets={len(dataset_rows)}.")


if __name__ == "__main__":
    main()
