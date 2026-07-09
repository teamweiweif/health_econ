from __future__ import annotations

import csv
import re
import time
from collections import Counter, defaultdict
from pathlib import Path
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup

from common import PROJECT_ROOT, REPORT_DIR, RESULT_DIR, SNAPSHOT_DIR, TEMP_DIR, append_log, ensure_dirs, sha256_file, utc_now_iso, write_csv


HANDOFF_PATH = TEMP_DIR / "first_batch_manual_download_handoff.csv"
GLOBAL_DOC_AUDIT_PATH = TEMP_DIR / "worldbank_public_documentation_audit.csv"
ACCESS_PROBE_PATH = TEMP_DIR / "first_batch_official_raw_access_probe.csv"

AUDIT_PATH = TEMP_DIR / "first_batch_public_documentation_audit.csv"
SUMMARY_PATH = RESULT_DIR / "first_batch_public_documentation_summary.csv"
REPORT_PATH = REPORT_DIR / "first_batch_public_documentation_audit.md"
SNAPSHOT_ROOT = SNAPSHOT_DIR / "first_batch_public_documentation"

MAX_BYTES = 25 * 1024 * 1024
REQUEST_RETRIES = 3
USER_AGENT = "Codex climate_uhc_ml first-batch public documentation audit"

RESOURCE_TYPES = {
    "get_microdata_html": "https://microdata.worldbank.org/catalog/{catalog_id}/get-microdata",
    "metadata_ddi_xml": "https://microdata.worldbank.org/metadata/export/{catalog_id}/ddi",
    "metadata_json": "https://microdata.worldbank.org/metadata/export/{catalog_id}/json",
    "pdf_documentation": "https://microdata.worldbank.org/catalog/{catalog_id}/pdf-documentation",
    "data_dictionary_html": "https://microdata.worldbank.org/catalog/{catalog_id}/data-dictionary",
    "related_materials_html": "https://microdata.worldbank.org/catalog/{catalog_id}/related-materials",
}

EXTENSIONS = {
    "get_microdata_html": ".html",
    "metadata_ddi_xml": ".xml",
    "metadata_json": ".json",
    "pdf_documentation": ".pdf",
    "data_dictionary_html": ".html",
    "related_materials_html": ".html",
}

ACCESS_GATE_HINTS = [
    "login",
    "log in",
    "register",
    "registration",
    "data access agreement",
    "terms of use",
    "request access",
]

AUDIT_COLUMNS = [
    "snapshot_time",
    "batch_rank",
    "country",
    "survey_name",
    "wave",
    "idno",
    "catalog_id",
    "resource_type",
    "url",
    "final_url",
    "http_status",
    "content_type",
    "content_length",
    "coverage_status",
    "saved_path",
    "sha256",
    "source_snapshot_group",
    "access_gate_detected",
    "login_link",
    "register_link",
    "metadata_links",
    "notes",
]

SUMMARY_COLUMNS = ["metric", "value", "interpretation"]


def read_csv_dicts(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        return []
    with path.open(encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def safe_name(text: str) -> str:
    return re.sub(r"[^A-Za-z0-9._-]+", "_", text).strip("_")[:140] or "item"


def catalog_id_from_url(url: str) -> str:
    match = re.search(r"/catalog/(\d+)", url or "")
    return match.group(1) if match else ""


def project_path(relative_path: str) -> Path:
    return PROJECT_ROOT / relative_path.replace("\\", "/")


def metadata_from_html(base_url: str, html: str) -> tuple[str, str, str, str]:
    lower = html.lower()
    gate = "1" if any(hint in lower for hint in ACCESS_GATE_HINTS) else "0"
    soup = BeautifulSoup(html, "html.parser")
    login_link = ""
    register_link = ""
    metadata_links: list[str] = []
    for anchor in soup.find_all("a", href=True):
        text = anchor.get_text(" ", strip=True).lower()
        href = urljoin(base_url, anchor["href"])
        if not login_link and any(token in text for token in ["login", "log in", "sign in"]):
            login_link = href
        if not register_link and "register" in text:
            register_link = href
        if any(token in href.lower() for token in ["/metadata/export/", "/pdf-documentation", "/data-dictionary", "/related-materials"]):
            if href not in metadata_links:
                metadata_links.append(href)
    return gate, login_link, register_link, ";".join(metadata_links[:30])


def saved_existing_row(
    handoff: dict[str, str],
    resource_type: str,
    source_row: dict[str, str],
    source_group: str,
) -> dict[str, str] | None:
    saved_path = source_row.get("saved_path") or source_row.get("saved_access_snapshot")
    if not saved_path:
        return None
    path = project_path(saved_path)
    if not path.exists() or not path.is_file() or path.stat().st_size == 0:
        return None
    row = {
        "snapshot_time": utc_now_iso(),
        "batch_rank": handoff.get("batch_rank", ""),
        "country": handoff.get("country", ""),
        "survey_name": handoff.get("survey_name", ""),
        "wave": handoff.get("wave", ""),
        "idno": handoff.get("idno", ""),
        "catalog_id": catalog_id_from_url(handoff.get("official_url", "")),
        "resource_type": resource_type,
        "url": source_row.get("url") or handoff.get("official_url", ""),
        "final_url": source_row.get("final_url", ""),
        "http_status": source_row.get("http_status", ""),
        "content_type": source_row.get("content_type", ""),
        "content_length": source_row.get("content_length", ""),
        "coverage_status": f"saved_existing_{source_group}",
        "saved_path": saved_path,
        "sha256": sha256_file(path),
        "source_snapshot_group": source_group,
        "access_gate_detected": source_row.get("access_gate_detected", ""),
        "login_link": source_row.get("login_link", ""),
        "register_link": source_row.get("register_link", ""),
        "metadata_links": source_row.get("metadata_links") or source_row.get("candidate_metadata_links", ""),
        "notes": "existing public documentation snapshot reused",
    }
    if resource_type.endswith("_html") and not row["metadata_links"]:
        html = path.read_text(encoding="utf-8", errors="replace")
        gate, login_link, register_link, metadata_links = metadata_from_html(row["final_url"] or row["url"], html)
        row["access_gate_detected"] = gate
        row["login_link"] = row["login_link"] or login_link
        row["register_link"] = row["register_link"] or register_link
        row["metadata_links"] = metadata_links
    return row


def write_response_limited(response: requests.Response, out_path: Path) -> tuple[str, str, str]:
    content_length = int(response.headers.get("content-length") or 0)
    if content_length and content_length > MAX_BYTES:
        return "skipped_oversize", "", f"content-length {content_length} exceeds limit {MAX_BYTES}"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    tmp_path = out_path.with_suffix(out_path.suffix + ".tmp")
    written = 0
    with tmp_path.open("wb") as f:
        for chunk in response.iter_content(chunk_size=1024 * 1024):
            if not chunk:
                continue
            written += len(chunk)
            if written > MAX_BYTES:
                tmp_path.unlink(missing_ok=True)
                return "skipped_oversize", "", f"streamed bytes exceed limit {MAX_BYTES}"
            f.write(chunk)
    tmp_path.replace(out_path)
    return "saved", str(out_path.relative_to(PROJECT_ROOT)).replace("\\", "/"), sha256_file(out_path)


def fetch_resource(handoff: dict[str, str], resource_type: str, url: str) -> dict[str, str]:
    folder = SNAPSHOT_ROOT / safe_name(f"{handoff.get('batch_rank', '')}_{handoff.get('idno', '')}")
    out_path = folder / f"{resource_type}{EXTENSIONS[resource_type]}"
    base = {
        "snapshot_time": utc_now_iso(),
        "batch_rank": handoff.get("batch_rank", ""),
        "country": handoff.get("country", ""),
        "survey_name": handoff.get("survey_name", ""),
        "wave": handoff.get("wave", ""),
        "idno": handoff.get("idno", ""),
        "catalog_id": catalog_id_from_url(handoff.get("official_url", "")),
        "resource_type": resource_type,
        "url": url,
        "final_url": "",
        "http_status": "",
        "content_type": "",
        "content_length": "",
        "coverage_status": "",
        "saved_path": "",
        "sha256": "",
        "source_snapshot_group": "first_batch_public_documentation",
        "access_gate_detected": "",
        "login_link": "",
        "register_link": "",
        "metadata_links": "",
        "notes": "",
    }
    last_error = ""
    for attempt in range(1, REQUEST_RETRIES + 1):
        try:
            with requests.get(url, headers={"User-Agent": USER_AGENT}, timeout=90, stream=True, allow_redirects=True) as response:
                base["final_url"] = response.url
                base["http_status"] = str(response.status_code)
                base["content_type"] = response.headers.get("content-type", "")
                base["content_length"] = response.headers.get("content-length", "")
                if response.status_code != 200:
                    base["coverage_status"] = "failed_http"
                    base["notes"] = f"HTTP {response.status_code}"
                    return base
                status, saved_path, note_or_hash = write_response_limited(response, out_path)
                base["coverage_status"] = status
                base["saved_path"] = saved_path
                if status == "saved":
                    base["sha256"] = note_or_hash
                else:
                    base["notes"] = note_or_hash
                    return base
            break
        except Exception as exc:
            last_error = str(exc)
            if attempt < REQUEST_RETRIES:
                time.sleep(min(2 * attempt, 8))
    else:
        base["coverage_status"] = "failed_request"
        base["notes"] = last_error
        return base

    if resource_type.endswith("_html") and out_path.exists():
        html = out_path.read_text(encoding="utf-8", errors="replace")
        gate, login_link, register_link, metadata_links = metadata_from_html(base["final_url"] or url, html)
        base["access_gate_detected"] = gate
        base["login_link"] = login_link
        base["register_link"] = register_link
        base["metadata_links"] = metadata_links
    return base


def build_audit_rows() -> list[dict[str, str]]:
    handoff_rows = read_csv_dicts(HANDOFF_PATH)
    global_rows = read_csv_dicts(GLOBAL_DOC_AUDIT_PATH)
    access_rows = read_csv_dicts(ACCESS_PROBE_PATH)
    prior_rows = read_csv_dicts(AUDIT_PATH)
    global_by_key = {(row.get("idno", ""), row.get("resource_type", "")): row for row in global_rows if row.get("status") == "saved"}
    access_by_idno = {row.get("idno", ""): row for row in access_rows if row.get("saved_snapshot")}
    prior_by_key = {(row.get("idno", ""), row.get("resource_type", "")): row for row in prior_rows if row.get("coverage_status", "").startswith("saved")}

    rows: list[dict[str, str]] = []
    for handoff in handoff_rows:
        catalog_id = catalog_id_from_url(handoff.get("official_url", ""))
        for resource_type, template in RESOURCE_TYPES.items():
            key = (handoff.get("idno", ""), resource_type)
            existing = saved_existing_row(handoff, resource_type, global_by_key.get(key, {}), "worldbank_public_documentation")
            if existing is None and resource_type == "get_microdata_html":
                existing = saved_existing_row(handoff, resource_type, access_by_idno.get(handoff.get("idno", ""), {}), "first_batch_access_probe")
            if existing is None:
                existing = saved_existing_row(handoff, resource_type, prior_by_key.get(key, {}), "first_batch_public_documentation")
            rows.append(existing if existing is not None else fetch_resource(handoff, resource_type, template.format(catalog_id=catalog_id)))
    return rows


def is_saved(status: str) -> bool:
    return status == "saved" or status.startswith("saved_existing_")


def build_summary(rows: list[dict[str, str]]) -> list[dict[str, str]]:
    by_idno: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in rows:
        by_idno[row.get("idno", "")].append(row)
    complete_datasets = 0
    pdf_missing = 0
    get_gate = 0
    for values in by_idno.values():
        saved_types = {row["resource_type"] for row in values if is_saved(row.get("coverage_status", ""))}
        if set(RESOURCE_TYPES) <= saved_types:
            complete_datasets += 1
        if "pdf_documentation" not in saved_types:
            pdf_missing += 1
        get_row = next((row for row in values if row.get("resource_type") == "get_microdata_html"), {})
        if get_row.get("access_gate_detected") == "1":
            get_gate += 1

    status_counts = Counter(row.get("coverage_status", "") for row in rows)
    resource_counts = Counter(row.get("resource_type", "") for row in rows)
    rows_out = [
        {"metric": "first_batch_documentation_dataset_rows", "value": str(len(by_idno)), "interpretation": "First-batch datasets audited for public documentation coverage."},
        {"metric": "first_batch_documentation_resource_rows", "value": str(len(rows)), "interpretation": "Dataset-resource documentation rows."},
        {"metric": "first_batch_documentation_saved_rows", "value": str(sum(1 for row in rows if is_saved(row.get("coverage_status", "")))), "interpretation": "Documentation resources saved or reused as local snapshots."},
        {"metric": "first_batch_documentation_failed_rows", "value": str(sum(1 for row in rows if row.get("coverage_status", "").startswith("failed"))), "interpretation": "Documentation resources that failed to fetch."},
        {"metric": "first_batch_documentation_complete_dataset_rows", "value": str(complete_datasets), "interpretation": "Datasets with all six public documentation resource types saved or reused."},
        {"metric": "first_batch_documentation_pdf_missing_dataset_rows", "value": str(pdf_missing), "interpretation": "Datasets without a saved PDF documentation endpoint."},
        {"metric": "first_batch_documentation_access_gate_rows", "value": str(get_gate), "interpretation": "Datasets with access-gate language on the get-microdata HTML page."},
    ]
    for status, count in sorted(status_counts.items()):
        rows_out.append({"metric": f"coverage_status_{status or 'blank'}", "value": str(count), "interpretation": "Documentation coverage status count."})
    for resource, count in sorted(resource_counts.items()):
        rows_out.append({"metric": f"resource_type_{resource or 'blank'}", "value": str(count), "interpretation": "Documentation resource type count."})
    return rows_out


def markdown_rows(rows: list[dict[str, str]], columns: list[str], limit: int = 20) -> str:
    lines = ["| " + " | ".join(columns) + " |", "|" + "|".join("---" for _ in columns) + "|"]
    for row in rows[:limit]:
        values = []
        for column in columns:
            value = (row.get(column, "") or "").replace("|", "/")
            if len(value) > 120:
                value = value[:117] + "..."
            values.append(value)
        lines.append("| " + " | ".join(values) + " |")
    return "\n".join(lines)


def markdown_count_table(counter: Counter[str], label: str) -> str:
    lines = [f"| {label} | Count |", "|---|---:|"]
    for key, count in counter.most_common():
        lines.append(f"| {key or 'blank'} | {count} |")
    return "\n".join(lines)


def dataset_rows(rows: list[dict[str, str]]) -> list[dict[str, str]]:
    by_idno: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in rows:
        by_idno[row["idno"]].append(row)
    out = []
    for idno, values in by_idno.items():
        first = values[0]
        saved_types = sorted(row["resource_type"] for row in values if is_saved(row["coverage_status"]))
        missing_types = sorted(set(RESOURCE_TYPES) - set(saved_types))
        out.append(
            {
                "batch_rank": first["batch_rank"],
                "country": first["country"],
                "wave": first["wave"],
                "idno": idno,
                "saved_resource_types": ";".join(saved_types),
                "missing_resource_types": ";".join(missing_types),
                "public_documentation_status": "complete_public_documentation_snapshot" if not missing_types else "incomplete_public_documentation_snapshot",
            }
        )
    out.sort(key=lambda row: int(row["batch_rank"] or 9999))
    return out


def write_report(rows: list[dict[str, str]], summary: list[dict[str, str]]) -> None:
    status_counts = Counter(row["coverage_status"] for row in rows)
    resource_counts = Counter(row["resource_type"] for row in rows)
    datasets = dataset_rows(rows)
    failed = [row for row in rows if row["coverage_status"].startswith("failed") or row["coverage_status"] == "skipped_oversize"]
    summary_table = "\n".join(f"| {row['metric']} | {row['value']} | {row['interpretation']} |" for row in summary)
    REPORT_PATH.write_text(
        f"""# First-Batch Public Documentation Audit

Status: public documentation coverage audit only. This checks whether official World Bank catalog pages, metadata exports, data dictionaries, related-material pages, and PDF documentation are saved locally for first-batch datasets. It does not download raw microdata and does not bypass account, request, registration, or terms workflows.

## Summary

| Metric | Value | Interpretation |
|---|---:|---|
{summary_table}

## Coverage Status

{markdown_count_table(status_counts, 'Coverage status') if rows else 'No documentation coverage rows exist.'}

## Resource Types

{markdown_count_table(resource_counts, 'Resource type') if rows else 'No documentation coverage rows exist.'}

## Dataset Coverage

{markdown_rows(datasets, ['batch_rank', 'country', 'wave', 'idno', 'public_documentation_status', 'missing_resource_types'], 20)}

## Failed Or Missing Public Resources

{markdown_rows(failed, ['batch_rank', 'idno', 'resource_type', 'coverage_status', 'http_status', 'notes'], 20) if failed else 'No failed or oversized first-batch public documentation resources were found.'}

## Guardrails

- Saved public documentation can support metadata and planning audits only.
- Raw survey files still must be obtained through the listed account/terms workflow and placed in `temp/raw_downloads/<IDNO>/`.
- Do not promote harmonization, outcomes, climate linkage, models, causal claims, or policy simulations from this documentation audit alone.

## Machine-Readable Outputs

- `temp/first_batch_public_documentation_audit.csv`
- `result/first_batch_public_documentation_summary.csv`
""",
        encoding="utf-8",
    )


def main() -> None:
    ensure_dirs()
    rows = build_audit_rows()
    summary = build_summary(rows)
    write_csv(AUDIT_PATH, rows, AUDIT_COLUMNS)
    write_csv(SUMMARY_PATH, summary, SUMMARY_COLUMNS)
    write_report(rows, summary)
    saved_rows = sum(1 for row in rows if is_saved(row.get("coverage_status", "")))
    append_log(TEMP_DIR / "audit_log.md", f"Built first-batch public documentation audit rows={len(rows)} saved_or_reused={saved_rows}.")
    print(f"First-batch public documentation audit rows={len(rows)} saved_or_reused={saved_rows}.")


if __name__ == "__main__":
    main()
