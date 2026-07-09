from __future__ import annotations

import csv
import re
import time
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

import requests
from bs4 import BeautifulSoup

from common import PROJECT_ROOT, REPORT_DIR, RESULT_DIR, SNAPSHOT_DIR, TEMP_DIR, append_log, ensure_dirs, sha256_file, utc_now_iso, write_csv


DOSSIER_PATH = TEMP_DIR / "priority_official_download_dossier.csv"
ACCESS_PROBE_PATH = TEMP_DIR / "priority_official_raw_access_probe.csv"
RECEIPT_PATH = TEMP_DIR / "priority_public_documentation_receipt.csv"
DATASET_RECEIPT_PATH = TEMP_DIR / "priority_public_documentation_dataset_receipt.csv"
SUMMARY_PATH = RESULT_DIR / "priority_public_documentation_receipt_summary.csv"
REPORT_PATH = REPORT_DIR / "priority_public_documentation_receipt.md"
SNAPSHOT_ROOT = SNAPSHOT_DIR / "priority_public_documentation"

MAX_BYTES = 30 * 1024 * 1024
REQUEST_RETRIES = 3
TIMEOUT = 90
USER_AGENT = "Codex climate_uhc_ml priority public documentation receipt"

RESOURCE_SPECS = [
    ("get_microdata_html", "official_get_microdata_url", ".html", True),
    ("pdf_documentation", "pdf_documentation_url", ".pdf", False),
    ("ddi_metadata", "ddi_metadata_url", ".xml", True),
    ("json_metadata", "json_metadata_url", ".json", True),
    ("data_dictionary_html", "data_dictionary_url", ".html", True),
    ("related_materials_html", "related_materials_url", ".html", True),
]

CORE_RESOURCE_TYPES = {
    "get_microdata_html",
    "ddi_metadata",
    "json_metadata",
    "data_dictionary_html",
    "related_materials_html",
}

ACCESS_GATE_HINTS = [
    "login",
    "log in",
    "sign in",
    "register",
    "registration",
    "terms of use",
    "data access agreement",
    "request access",
]

RECEIPT_COLUMNS = [
    "receipt_time",
    "acquisition_batch_rank",
    "batch_role",
    "country",
    "wave",
    "idno",
    "catalog_id",
    "resource_type",
    "url",
    "final_url",
    "http_status",
    "content_type",
    "content_length",
    "receipt_status",
    "saved_path",
    "bytes",
    "sha256",
    "required_for_core_public_documentation",
    "access_gate_detected",
    "login_link",
    "register_link",
    "metadata_links",
    "notes",
]

DATASET_COLUMNS = [
    "acquisition_batch_rank",
    "batch_role",
    "country",
    "wave",
    "idno",
    "catalog_id",
    "saved_resource_types",
    "missing_core_resource_types",
    "missing_optional_resource_types",
    "public_documentation_receipt_status",
    "access_gate_detected",
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
    return re.sub(r"[^A-Za-z0-9._-]+", "_", clean(text)).strip("_")[:140] or "item"


def rel(path: Path) -> str:
    try:
        return str(path.relative_to(PROJECT_ROOT)).replace("\\", "/")
    except ValueError:
        return str(path).replace("\\", "/")


def parse_catalog_id(row: dict[str, str]) -> str:
    if clean(row.get("catalog_id")):
        return clean(row.get("catalog_id"))
    match = re.search(r"/catalog/(\d+)", row.get("official_get_microdata_url", ""))
    return match.group(1) if match else ""


def is_saved(status: str) -> bool:
    return status in {"saved", "saved_existing", "saved_existing_access_probe"}


def metadata_from_html(base_url: str, path: Path) -> tuple[str, str, str, str]:
    html = path.read_text(encoding="utf-8", errors="replace")
    lower = html.lower()
    gate = "1" if any(hint in lower for hint in ACCESS_GATE_HINTS) else "0"
    soup = BeautifulSoup(html, "html.parser")
    login = ""
    register = ""
    metadata_links: list[str] = []
    base_parts = urlparse(base_url)
    base = f"{base_parts.scheme}://{base_parts.netloc}" if base_parts.scheme and base_parts.netloc else ""
    for anchor in soup.find_all("a", href=True):
        href = anchor["href"]
        if href.startswith("/"):
            href = f"{base}{href}"
        text = anchor.get_text(" ", strip=True).lower()
        low = f"{href} {text}".lower()
        if not login and any(token in low for token in ["login", "log in", "sign in"]):
            login = href
        if not register and "register" in low:
            register = href
        if any(token in href.lower() for token in ["/metadata/export/", "/pdf-documentation", "/data-dictionary", "/related-materials"]):
            if href not in metadata_links:
                metadata_links.append(href)
    return gate, login, register, ";".join(metadata_links[:30])


def output_path(row: dict[str, str], resource_type: str, suffix: str) -> Path:
    folder = SNAPSHOT_ROOT / safe_name(f"{row.get('acquisition_batch_rank', '')}_{row.get('idno', '')}")
    return folder / f"{resource_type}{suffix}"


def access_probe_existing(row: dict[str, str], access_by_idno: dict[str, dict[str, str]]) -> dict[str, str] | None:
    access = access_by_idno.get(clean(row.get("idno")), {})
    saved = clean(access.get("saved_snapshot"))
    if not saved:
        return None
    path = PROJECT_ROOT / saved
    if not path.exists() or not path.is_file() or path.stat().st_size == 0:
        return None
    return {
        "receipt_time": utc_now_iso(),
        "acquisition_batch_rank": row.get("acquisition_batch_rank", ""),
        "batch_role": row.get("batch_role", ""),
        "country": row.get("country", ""),
        "wave": row.get("wave", ""),
        "idno": row.get("idno", ""),
        "catalog_id": parse_catalog_id(row),
        "resource_type": "get_microdata_html",
        "url": access.get("official_url", row.get("official_get_microdata_url", "")),
        "final_url": access.get("final_url", ""),
        "http_status": access.get("http_status", ""),
        "content_type": access.get("content_type", ""),
        "content_length": access.get("content_length", ""),
        "receipt_status": "saved_existing_access_probe",
        "saved_path": saved,
        "bytes": str(path.stat().st_size),
        "sha256": sha256_file(path),
        "required_for_core_public_documentation": "1",
        "access_gate_detected": access.get("access_gate_detected", ""),
        "login_link": access.get("login_link", ""),
        "register_link": access.get("register_link", ""),
        "metadata_links": access.get("candidate_metadata_links", ""),
        "notes": "existing priority official raw access probe snapshot reused",
    }


def existing_snapshot(row: dict[str, str], resource_type: str, suffix: str, required: bool) -> dict[str, str] | None:
    path = output_path(row, resource_type, suffix)
    if not path.exists() or not path.is_file() or path.stat().st_size == 0:
        return None
    gate = login = register = metadata_links = ""
    if suffix == ".html":
        gate, login, register, metadata_links = metadata_from_html(row.get("official_get_microdata_url", ""), path)
    return {
        "receipt_time": utc_now_iso(),
        "acquisition_batch_rank": row.get("acquisition_batch_rank", ""),
        "batch_role": row.get("batch_role", ""),
        "country": row.get("country", ""),
        "wave": row.get("wave", ""),
        "idno": row.get("idno", ""),
        "catalog_id": parse_catalog_id(row),
        "resource_type": resource_type,
        "url": row.get(resource_url_field(resource_type), ""),
        "final_url": "",
        "http_status": "",
        "content_type": "",
        "content_length": "",
        "receipt_status": "saved_existing",
        "saved_path": rel(path),
        "bytes": str(path.stat().st_size),
        "sha256": sha256_file(path),
        "required_for_core_public_documentation": "1" if required else "0",
        "access_gate_detected": gate,
        "login_link": login,
        "register_link": register,
        "metadata_links": metadata_links,
        "notes": "existing priority public documentation snapshot reused",
    }


def resource_url_field(resource_type: str) -> str:
    for candidate, field, _suffix, _required in RESOURCE_SPECS:
        if candidate == resource_type:
            return field
    return ""


def write_response_limited(response: requests.Response, out_path: Path) -> tuple[str, str]:
    content_length = int(response.headers.get("content-length") or 0)
    if content_length and content_length > MAX_BYTES:
        return "skipped_oversize", f"content-length {content_length} exceeds limit {MAX_BYTES}"
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
                return "skipped_oversize", f"streamed bytes exceed limit {MAX_BYTES}"
            f.write(chunk)
    tmp_path.replace(out_path)
    return "saved", ""


def fetch_resource(row: dict[str, str], resource_type: str, url: str, suffix: str, required: bool) -> dict[str, str]:
    out_path = output_path(row, resource_type, suffix)
    base = {
        "receipt_time": utc_now_iso(),
        "acquisition_batch_rank": row.get("acquisition_batch_rank", ""),
        "batch_role": row.get("batch_role", ""),
        "country": row.get("country", ""),
        "wave": row.get("wave", ""),
        "idno": row.get("idno", ""),
        "catalog_id": parse_catalog_id(row),
        "resource_type": resource_type,
        "url": url,
        "final_url": "",
        "http_status": "",
        "content_type": "",
        "content_length": "",
        "receipt_status": "",
        "saved_path": "",
        "bytes": "",
        "sha256": "",
        "required_for_core_public_documentation": "1" if required else "0",
        "access_gate_detected": "",
        "login_link": "",
        "register_link": "",
        "metadata_links": "",
        "notes": "",
    }
    if not url:
        base["receipt_status"] = "missing_optional_url" if not required else "missing_required_url"
        base["notes"] = "No official URL was listed in the priority download dossier."
        return base

    last_error = ""
    for attempt in range(1, REQUEST_RETRIES + 1):
        try:
            with requests.get(url, headers={"User-Agent": USER_AGENT}, timeout=TIMEOUT, stream=True, allow_redirects=True) as response:
                base["final_url"] = response.url
                base["http_status"] = str(response.status_code)
                base["content_type"] = response.headers.get("content-type", "")
                base["content_length"] = response.headers.get("content-length", "")
                if response.status_code != 200:
                    base["receipt_status"] = "failed_http"
                    base["notes"] = f"HTTP {response.status_code}"
                    return base
                status, note = write_response_limited(response, out_path)
                base["receipt_status"] = status
                if status == "saved":
                    base["saved_path"] = rel(out_path)
                    base["bytes"] = str(out_path.stat().st_size)
                    base["sha256"] = sha256_file(out_path)
                else:
                    base["notes"] = note
                    return base
            break
        except Exception as exc:
            last_error = str(exc)
            if attempt < REQUEST_RETRIES:
                time.sleep(min(2 * attempt, 8))
    else:
        base["receipt_status"] = "failed_request"
        base["notes"] = last_error
        return base

    if suffix == ".html" and out_path.exists():
        gate, login, register, metadata_links = metadata_from_html(base["final_url"] or url, out_path)
        base["access_gate_detected"] = gate
        base["login_link"] = login
        base["register_link"] = register
        base["metadata_links"] = metadata_links
    return base


def build_receipt_rows() -> list[dict[str, str]]:
    dossier_rows = read_csv_dicts(DOSSIER_PATH)
    access_by_idno = {row.get("idno", ""): row for row in read_csv_dicts(ACCESS_PROBE_PATH)}
    rows: list[dict[str, str]] = []
    for dossier in dossier_rows:
        for resource_type, field, suffix, required in RESOURCE_SPECS:
            if resource_type == "get_microdata_html":
                existing = access_probe_existing(dossier, access_by_idno)
                if existing is not None:
                    rows.append(existing)
                    continue
            existing = existing_snapshot(dossier, resource_type, suffix, required)
            if existing is not None:
                rows.append(existing)
                continue
            rows.append(fetch_resource(dossier, resource_type, clean(dossier.get(field)), suffix, required))
    return rows


def write_handoff(row: dict[str, str], resources: list[dict[str, str]]) -> str:
    folder = PROJECT_ROOT / clean(row.get("local_target_folder")).replace("\\", "/").strip("/")
    folder.mkdir(parents=True, exist_ok=True)
    path = folder / "_PRIORITY_PUBLIC_DOCUMENTATION_RECEIPT.md"
    resource_lines = [
        f"- {item['resource_type']}: {item['receipt_status']} ({item.get('saved_path', '') or item.get('notes', '')})"
        for item in resources
    ]
    path.write_text(
        f"""# Priority Public Documentation Receipt

Dataset: {row.get('idno', '')} - {row.get('country', '')} {row.get('wave', '')}

Status: public documentation and metadata receipt only.

Resources:

{chr(10).join(resource_lines)}

Guardrail: these snapshots are not raw microdata. Keep this country-wave blocked
until complete original raw packages are obtained through the official access
workflow, values/keys/units are manually verified, and climate linkage passes.
""",
        encoding="utf-8",
    )
    return rel(path)


def build_dataset_rows(receipt_rows: list[dict[str, str]]) -> list[dict[str, str]]:
    dossier_by_idno = {row.get("idno", ""): row for row in read_csv_dicts(DOSSIER_PATH)}
    by_idno: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in receipt_rows:
        by_idno[row.get("idno", "")].append(row)

    rows: list[dict[str, str]] = []
    for idno, resources in by_idno.items():
        first = resources[0]
        dossier = dossier_by_idno.get(idno, {})
        saved = sorted({row["resource_type"] for row in resources if is_saved(row.get("receipt_status", ""))})
        missing_core = sorted(CORE_RESOURCE_TYPES - set(saved))
        optional_types = {item[0] for item in RESOURCE_SPECS if not item[3]}
        missing_optional = sorted(optional_types - set(saved))
        access_gate = "1" if any(row.get("access_gate_detected") == "1" for row in resources) else "0"
        if not missing_core and not missing_optional:
            status = "complete_full_public_documentation_receipt"
        elif not missing_core:
            status = "complete_core_public_documentation_receipt_optional_pdf_unlisted_or_missing"
        else:
            status = "incomplete_core_public_documentation_receipt"
        dataset_row = {
            "acquisition_batch_rank": first.get("acquisition_batch_rank", ""),
            "batch_role": first.get("batch_role", ""),
            "country": first.get("country", ""),
            "wave": first.get("wave", ""),
            "idno": idno,
            "catalog_id": first.get("catalog_id", ""),
            "saved_resource_types": ";".join(saved),
            "missing_core_resource_types": ";".join(missing_core),
            "missing_optional_resource_types": ";".join(missing_optional),
            "public_documentation_receipt_status": status,
            "access_gate_detected": access_gate,
            "handoff_readme": "",
        }
        dataset_row["handoff_readme"] = write_handoff(dossier or first, resources)
        rows.append(dataset_row)
    rows.sort(key=lambda row: int(row.get("acquisition_batch_rank") or 9999))
    return rows


def build_summary(receipt_rows: list[dict[str, str]], dataset_rows: list[dict[str, str]]) -> list[dict[str, str]]:
    status_counts = Counter(row.get("receipt_status", "") for row in receipt_rows)
    resource_counts = Counter(row.get("resource_type", "") for row in receipt_rows)
    dataset_status_counts = Counter(row.get("public_documentation_receipt_status", "") for row in dataset_rows)
    saved_rows = sum(1 for row in receipt_rows if is_saved(row.get("receipt_status", "")))
    failed_rows = sum(1 for row in receipt_rows if row.get("receipt_status", "").startswith("failed"))
    access_gate_rows = sum(1 for row in dataset_rows if row.get("access_gate_detected") == "1")
    total_bytes = sum(int(row.get("bytes") or 0) for row in receipt_rows if is_saved(row.get("receipt_status", "")))
    rows = [
        {"metric": "priority_public_documentation_dataset_rows", "value": str(len(dataset_rows)), "interpretation": "Priority and backup waves with public documentation receipt rows."},
        {"metric": "priority_public_documentation_resource_rows", "value": str(len(receipt_rows)), "interpretation": "Public documentation or metadata resources attempted or reused."},
        {"metric": "priority_public_documentation_saved_rows", "value": str(saved_rows), "interpretation": "Public documentation resources saved or reused locally."},
        {"metric": "priority_public_documentation_failed_rows", "value": str(failed_rows), "interpretation": "Public documentation resources that failed to fetch."},
        {"metric": "priority_public_documentation_core_complete_dataset_rows", "value": str(sum(1 for row in dataset_rows if not row.get("missing_core_resource_types"))), "interpretation": "Datasets with all core public documentation resource types saved."},
        {"metric": "priority_public_documentation_full_complete_dataset_rows", "value": str(dataset_status_counts.get("complete_full_public_documentation_receipt", 0)), "interpretation": "Datasets with core public resources plus PDF documentation saved."},
        {"metric": "priority_public_documentation_optional_pdf_missing_dataset_rows", "value": str(sum(1 for row in dataset_rows if row.get("missing_optional_resource_types"))), "interpretation": "Datasets where the optional PDF documentation resource was not listed or not saved."},
        {"metric": "priority_public_documentation_access_gate_rows", "value": str(access_gate_rows), "interpretation": "Datasets whose get-microdata page still shows login/register/terms gate language."},
        {"metric": "priority_public_documentation_saved_bytes", "value": str(total_bytes), "interpretation": "Total bytes in saved or reused public documentation snapshots."},
        {"metric": "priority_public_documentation_handoff_readmes_written", "value": str(sum(1 for row in dataset_rows if row.get("handoff_readme"))), "interpretation": "Per-wave public documentation receipt handoff README files written."},
        {"metric": "modeling_gate_status", "value": "blocked", "interpretation": "Public documentation receipt does not satisfy raw value verification or climate-linkage promotion gates."},
    ]
    for status, count in sorted(status_counts.items()):
        rows.append({"metric": f"priority_public_documentation_receipt_status_{status or 'blank'}", "value": str(count), "interpretation": "Public documentation resource receipt status count."})
    for resource, count in sorted(resource_counts.items()):
        rows.append({"metric": f"priority_public_documentation_resource_type_{resource or 'blank'}", "value": str(count), "interpretation": "Public documentation resource type count."})
    for status, count in sorted(dataset_status_counts.items()):
        rows.append({"metric": f"priority_public_documentation_dataset_status_{status or 'blank'}", "value": str(count), "interpretation": "Dataset-level public documentation receipt status count."})
    return rows


def markdown_rows(rows: list[dict[str, str]], columns: list[str], limit: int = 20) -> str:
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


def write_report(receipt_rows: list[dict[str, str]], dataset_rows: list[dict[str, str]], summary: list[dict[str, str]]) -> None:
    summary_table = "\n".join(f"| {row['metric']} | {row['value']} | {row['interpretation']} |" for row in summary)
    failed_rows = [row for row in receipt_rows if row.get("receipt_status", "").startswith("failed") or row.get("receipt_status", "").startswith("missing_required")]
    REPORT_PATH.write_text(
        f"""# Priority Public Documentation Receipt

Status: public documentation and metadata receipt for priority acquisition
waves. This step downloads or reuses official public pages, DDI/XML exports,
JSON metadata, data dictionaries, related-material pages, and listed PDF
documentation. It does not download raw microdata and does not bypass account,
terms, registration, or data-access agreement gates.

## Summary

| Metric | Value | Interpretation |
|---|---:|---|
{summary_table}

## Dataset Receipt

{markdown_rows(dataset_rows, ['acquisition_batch_rank', 'idno', 'country', 'wave', 'public_documentation_receipt_status', 'missing_core_resource_types', 'missing_optional_resource_types'], 20)}

## Failed Or Missing Required Resources

{markdown_rows(failed_rows, ['acquisition_batch_rank', 'idno', 'resource_type', 'receipt_status', 'http_status', 'notes'], 20) if failed_rows else 'No failed or missing required public documentation resources.'}

## Guardrails

- Public documentation snapshots support planning and variable verification only.
- A complete public documentation receipt is not a raw package receipt.
- Keep all priority country-waves out of `data/` until original raw packages,
  manual value/key/unit/skip-pattern verification, and CHIRPS/ERA5 linkage pass.

## Machine-Readable Outputs

- `temp/priority_public_documentation_receipt.csv`
- `temp/priority_public_documentation_dataset_receipt.csv`
- `result/priority_public_documentation_receipt_summary.csv`
""",
        encoding="utf-8",
    )


def main() -> None:
    ensure_dirs()
    receipt_rows = build_receipt_rows()
    dataset_rows = build_dataset_rows(receipt_rows)
    summary = build_summary(receipt_rows, dataset_rows)
    write_csv(RECEIPT_PATH, receipt_rows, RECEIPT_COLUMNS)
    write_csv(DATASET_RECEIPT_PATH, dataset_rows, DATASET_COLUMNS)
    write_csv(SUMMARY_PATH, summary, SUMMARY_COLUMNS)
    write_report(receipt_rows, dataset_rows, summary)
    append_log(
        TEMP_DIR / "audit_log.md",
        f"Built priority public documentation receipt datasets={len(dataset_rows)} resources={len(receipt_rows)} saved={sum(1 for row in receipt_rows if is_saved(row.get('receipt_status', '')))}.",
    )
    print(f"Priority public documentation receipt datasets={len(dataset_rows)} resources={len(receipt_rows)}.")


if __name__ == "__main__":
    main()
