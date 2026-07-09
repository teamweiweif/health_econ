from __future__ import annotations

import csv
import hashlib
import json
import re
import time
from collections import Counter, defaultdict
from html.parser import HTMLParser
from pathlib import Path
from typing import Any
from urllib.parse import urlparse
import xml.etree.ElementTree as ET

import requests

from common import PROJECT_ROOT, REPORT_DIR, RESULT_DIR, SNAPSHOT_DIR, TEMP_DIR, append_log, ensure_dirs, utc_now_iso, write_csv


QUEUE_PATH = TEMP_DIR / "priority_lsms_isa_refocused_acquisition_queue.csv"
RECEIPT_PATH = TEMP_DIR / "priority_lsms_isa_public_documentation_receipt.csv"
DATASET_RECEIPT_PATH = TEMP_DIR / "priority_lsms_isa_public_documentation_dataset_receipt.csv"
CATALOG_DIGEST_PATH = TEMP_DIR / "priority_lsms_isa_public_documentation_catalog_digest.csv"
FILE_INVENTORY_PATH = TEMP_DIR / "priority_lsms_isa_public_documentation_file_inventory.csv"
SUMMARY_PATH = RESULT_DIR / "priority_lsms_isa_public_documentation_receipt_summary.csv"
REPORT_PATH = REPORT_DIR / "priority_lsms_isa_public_documentation_receipt.md"
SNAPSHOT_ROOT = SNAPSHOT_DIR / "priority_lsms_isa_public_documentation"
RAW_ROOT = TEMP_DIR / "raw_downloads"

TIMEOUT = 90
REQUEST_RETRIES = 3
MAX_BYTES = 35 * 1024 * 1024
USER_AGENT = "Codex climate_uhc_ml refocused LSMS-ISA public documentation receipt"

RESOURCE_SPECS = [
    ("get_microdata_html", "official_get_microdata_url", ".html", True),
    ("catalog_idno_json", "catalog_idno_api_url", ".json", True),
    ("variables_idno_json", "variables_idno_api_url", ".json", True),
    ("ddi_metadata", "ddi_metadata_url", ".xml", True),
    ("json_metadata", "json_metadata_url", ".json", True),
    ("data_dictionary_html", "data_dictionary_url", ".html", True),
    ("related_materials_html", "related_materials_url", ".html", True),
]

CORE_RESOURCE_TYPES = {name for name, _field, _suffix, required in RESOURCE_SPECS if required}
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
    "download_priority_order",
    "queue_role",
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
    "download_priority_order",
    "queue_role",
    "country",
    "wave",
    "idno",
    "catalog_id",
    "candidate_family",
    "alignment_priority",
    "saved_resource_types",
    "missing_core_resource_types",
    "public_documentation_receipt_status",
    "access_gate_detected",
    "raw_package_status",
    "data_write_status",
    "modeling_gate_status",
    "handoff_readme",
]

CATALOG_DIGEST_COLUMNS = [
    "download_priority_order",
    "queue_role",
    "country",
    "wave",
    "idno",
    "catalog_id",
    "title",
    "nation",
    "year_start",
    "year_end",
    "repositoryid",
    "doi",
    "authoring_entity",
    "published",
    "created",
    "changed",
    "varcount",
    "total_downloads",
    "data_access_type",
    "version",
    "metadata_status",
    "source_saved_path",
    "source_sha256",
]

FILE_INVENTORY_COLUMNS = [
    "download_priority_order",
    "queue_role",
    "country",
    "wave",
    "idno",
    "catalog_id",
    "file_id",
    "file_name",
    "file_description",
    "case_quantity",
    "variable_quantity",
    "source_saved_path",
    "source_sha256",
]

SUMMARY_COLUMNS = ["metric", "value", "interpretation"]


class LinkParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.links: list[tuple[str, str]] = []
        self._current_href = ""
        self._current_text: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag.lower() != "a":
            return
        attr_map = {key.lower(): value or "" for key, value in attrs}
        self._current_href = attr_map.get("href", "")
        self._current_text = []

    def handle_data(self, data: str) -> None:
        if self._current_href:
            self._current_text.append(data)

    def handle_endtag(self, tag: str) -> None:
        if tag.lower() == "a" and self._current_href:
            self.links.append((self._current_href, " ".join(" ".join(self._current_text).split())))
            self._current_href = ""
            self._current_text = []


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


def safe_name(value: str) -> str:
    return re.sub(r"[^A-Za-z0-9._-]+", "_", clean(value)).strip("_")[:140] or "item"


def parse_catalog_id(row: dict[str, str]) -> str:
    match = re.search(r"/catalog/(\d+)", clean(row.get("official_get_microdata_url")))
    return match.group(1) if match else ""


def resource_urls(row: dict[str, str]) -> dict[str, str]:
    catalog_id = parse_catalog_id(row)
    idno = clean(row.get("idno"))
    return {
        "official_get_microdata_url": clean(row.get("official_get_microdata_url")),
        "catalog_idno_api_url": f"https://microdata.worldbank.org/index.php/api/catalog/{idno}",
        "variables_idno_api_url": f"https://microdata.worldbank.org/index.php/api/catalog/{idno}/variables",
        "ddi_metadata_url": f"https://microdata.worldbank.org/metadata/export/{catalog_id}/ddi" if catalog_id else "",
        "json_metadata_url": f"https://microdata.worldbank.org/metadata/export/{catalog_id}/json" if catalog_id else "",
        "data_dictionary_url": f"https://microdata.worldbank.org/catalog/{catalog_id}/data-dictionary" if catalog_id else "",
        "related_materials_url": f"https://microdata.worldbank.org/catalog/{catalog_id}/related-materials" if catalog_id else "",
    }


def output_path(row: dict[str, str], resource_type: str, suffix: str) -> Path:
    folder = SNAPSHOT_ROOT / safe_name(f"{row.get('download_priority_order', '')}_{row.get('idno', '')}")
    return folder / f"{resource_type}{suffix}"


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def local_name(tag: str) -> str:
    return tag.split("}")[-1]


def xml_child_text(element: ET.Element, names: set[str]) -> str:
    for child in element.iter():
        if local_name(child.tag) in names:
            return " ".join((child.text or "").split())
    return ""


def nested_get(data: dict[str, Any], path: list[str]) -> Any:
    current: Any = data
    for key in path:
        if not isinstance(current, dict):
            return ""
        current = current.get(key, "")
    return current


def short(value: Any, limit: int = 260) -> str:
    text = " ".join(clean(value).split())
    if len(text) <= limit:
        return text
    return text[: limit - 3] + "..."


def normalize_link(base_url: str, href: str) -> str:
    href = clean(href)
    if not href:
        return ""
    if href.startswith("http://") or href.startswith("https://"):
        return href
    base_parts = urlparse(base_url)
    base = f"{base_parts.scheme}://{base_parts.netloc}" if base_parts.scheme and base_parts.netloc else ""
    if href.startswith("/"):
        return f"{base}{href}"
    return href


def metadata_from_html(base_url: str, path: Path) -> tuple[str, str, str, str]:
    html = path.read_text(encoding="utf-8", errors="replace")
    lower = html.lower()
    gate = "1" if any(hint in lower for hint in ACCESS_GATE_HINTS) else "0"
    parser = LinkParser()
    parser.feed(html)
    login = ""
    register = ""
    metadata_links: list[str] = []
    for href, text in parser.links:
        full = normalize_link(base_url, href)
        low = f"{full} {text}".lower()
        if not login and any(token in low for token in ["login", "log in", "sign in"]):
            login = full
        if not register and "register" in low:
            register = full
        if any(token in full.lower() for token in ["/metadata/export/", "/data-dictionary", "/related-materials", "pdf"]):
            if full and full not in metadata_links:
                metadata_links.append(full)
    return gate, login, register, ";".join(metadata_links[:30])


def is_saved(status: str) -> bool:
    return status in {"saved", "saved_existing"}


def existing_snapshot(row: dict[str, str], resource_type: str, suffix: str, required: bool, url: str) -> dict[str, str] | None:
    path = output_path(row, resource_type, suffix)
    if not path.exists() or not path.is_file() or path.stat().st_size == 0:
        return None
    gate = login = register = metadata_links = ""
    if suffix == ".html":
        gate, login, register, metadata_links = metadata_from_html(url, path)
    return {
        "receipt_time": utc_now_iso(),
        "download_priority_order": row.get("download_priority_order", ""),
        "queue_role": row.get("queue_role", ""),
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
        "receipt_status": "saved_existing",
        "saved_path": rel(path),
        "bytes": str(path.stat().st_size),
        "sha256": sha256_file(path),
        "required_for_core_public_documentation": "1" if required else "0",
        "access_gate_detected": gate,
        "login_link": login,
        "register_link": register,
        "metadata_links": metadata_links,
        "notes": "existing refocused LSMS/ISA public documentation snapshot reused",
    }


def write_response_limited(response: requests.Response, out_path: Path) -> tuple[str, str]:
    content_length = safe_int(response.headers.get("content-length"))
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
    base = {
        "receipt_time": utc_now_iso(),
        "download_priority_order": row.get("download_priority_order", ""),
        "queue_role": row.get("queue_role", ""),
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
        base["receipt_status"] = "missing_required_url" if required else "missing_optional_url"
        base["notes"] = "No official public URL could be derived."
        return base

    existing = existing_snapshot(row, resource_type, suffix, required, url)
    if existing is not None:
        return existing

    out_path = output_path(row, resource_type, suffix)
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
    rows: list[dict[str, str]] = []
    for queue_row in read_csv_dicts(QUEUE_PATH):
        urls = resource_urls(queue_row)
        for resource_type, field, suffix, required in RESOURCE_SPECS:
            rows.append(fetch_resource(queue_row, resource_type, urls.get(field, ""), suffix, required))
    return rows


def write_handoff(dataset_row: dict[str, str], resources: list[dict[str, str]]) -> str:
    folder = RAW_ROOT / clean(dataset_row.get("idno"))
    folder.mkdir(parents=True, exist_ok=True)
    path = folder / "_PRIORITY_LSMS_ISA_PUBLIC_DOCUMENTATION_RECEIPT.md"
    resource_lines = [
        f"- {item.get('resource_type', '')}: {item.get('receipt_status', '')} ({item.get('saved_path', '') or item.get('notes', '')})"
        for item in resources
    ]
    path.write_text(
        f"""# Priority LSMS-ISA Public Documentation Receipt

Dataset: {dataset_row.get('idno', '')} - {dataset_row.get('country', '')} {dataset_row.get('wave', '')}

Status: {dataset_row.get('public_documentation_receipt_status', '')}

Resources:

{chr(10).join(resource_lines)}

Guardrail: these are public documentation and metadata snapshots only. They are
not a raw package receipt and do not verify raw values, units, recall periods,
missing codes, skip patterns, merge keys, survey design, timing, geography, or
climate linkage. Keep the wave out of `data/` until the complete unchanged
official raw package is present and value-verified.
""",
        encoding="utf-8",
    )
    return rel(path)


def build_dataset_rows(receipt_rows: list[dict[str, str]]) -> list[dict[str, str]]:
    queue_by_idno = {row.get("idno", ""): row for row in read_csv_dicts(QUEUE_PATH)}
    by_idno: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in receipt_rows:
        by_idno[row.get("idno", "")].append(row)

    rows: list[dict[str, str]] = []
    for idno, resources in by_idno.items():
        queue_row = queue_by_idno.get(idno, {})
        saved = sorted({row.get("resource_type", "") for row in resources if is_saved(row.get("receipt_status", ""))})
        missing_core = sorted(CORE_RESOURCE_TYPES - set(saved))
        access_gate = "1" if any(row.get("access_gate_detected") == "1" for row in resources) else "0"
        status = "complete_core_public_documentation_receipt" if not missing_core else "incomplete_core_public_documentation_receipt"
        dataset_row = {
            "download_priority_order": queue_row.get("download_priority_order", resources[0].get("download_priority_order", "")),
            "queue_role": queue_row.get("queue_role", resources[0].get("queue_role", "")),
            "country": queue_row.get("country", resources[0].get("country", "")),
            "wave": queue_row.get("wave", resources[0].get("wave", "")),
            "idno": idno,
            "catalog_id": resources[0].get("catalog_id", ""),
            "candidate_family": queue_row.get("candidate_family", ""),
            "alignment_priority": queue_row.get("alignment_priority", ""),
            "saved_resource_types": ";".join(saved),
            "missing_core_resource_types": ";".join(missing_core),
            "public_documentation_receipt_status": status,
            "access_gate_detected": access_gate,
            "raw_package_status": queue_row.get("raw_package_status", "not_received_no_original_raw_package"),
            "data_write_status": "blocked_no_promoted_rows",
            "modeling_gate_status": "blocked",
            "handoff_readme": "",
        }
        dataset_row["handoff_readme"] = write_handoff(dataset_row, resources)
        rows.append(dataset_row)
    rows.sort(key=lambda row: safe_int(row.get("download_priority_order"), 9999))
    return rows


def receipt_lookup(receipt_rows: list[dict[str, str]]) -> dict[tuple[str, str], dict[str, str]]:
    out: dict[tuple[str, str], dict[str, str]] = {}
    for row in receipt_rows:
        idno = clean(row.get("idno"))
        resource_type = clean(row.get("resource_type"))
        if idno and resource_type and is_saved(row.get("receipt_status", "")):
            out[(idno, resource_type)] = row
    return out


def build_catalog_digest(receipt_rows: list[dict[str, str]]) -> list[dict[str, str]]:
    queue_by_idno = {row.get("idno", ""): row for row in read_csv_dicts(QUEUE_PATH)}
    lookup = receipt_lookup(receipt_rows)
    rows: list[dict[str, str]] = []
    for idno, queue_row in sorted(queue_by_idno.items(), key=lambda item: safe_int(item[1].get("download_priority_order"), 9999)):
        receipt = lookup.get((idno, "catalog_idno_json"), {})
        path = PROJECT_ROOT / clean(receipt.get("saved_path"))
        status = "catalog_json_missing"
        dataset: dict[str, Any] = {}
        if path.exists():
            try:
                with path.open(encoding="utf-8", errors="replace") as f:
                    dataset = json.load(f).get("dataset", {})
                status = "catalog_json_parsed"
            except Exception as exc:
                status = f"catalog_json_parse_failed:{short(exc, 120)}"
        version = nested_get(dataset, ["metadata", "doc_desc", "version_statement", "version"])
        rows.append(
            {
                "download_priority_order": queue_row.get("download_priority_order", ""),
                "queue_role": queue_row.get("queue_role", ""),
                "country": queue_row.get("country", ""),
                "wave": queue_row.get("wave", ""),
                "idno": idno,
                "catalog_id": clean(dataset.get("id")) or parse_catalog_id(queue_row),
                "title": short(dataset.get("title"), 220),
                "nation": short(dataset.get("nation"), 120),
                "year_start": clean(dataset.get("year_start")),
                "year_end": clean(dataset.get("year_end")),
                "repositoryid": clean(dataset.get("repositoryid")),
                "doi": short(dataset.get("doi"), 180),
                "authoring_entity": short(dataset.get("authoring_entity"), 220),
                "published": clean(dataset.get("published")),
                "created": clean(dataset.get("created")),
                "changed": clean(dataset.get("changed")),
                "varcount": clean(dataset.get("varcount")),
                "total_downloads": clean(dataset.get("total_downloads")),
                "data_access_type": clean(dataset.get("data_access_type")),
                "version": short(version, 220),
                "metadata_status": status,
                "source_saved_path": receipt.get("saved_path", ""),
                "source_sha256": receipt.get("sha256", ""),
            }
        )
    return rows


def build_file_inventory(receipt_rows: list[dict[str, str]]) -> list[dict[str, str]]:
    queue_by_idno = {row.get("idno", ""): row for row in read_csv_dicts(QUEUE_PATH)}
    lookup = receipt_lookup(receipt_rows)
    rows: list[dict[str, str]] = []
    for idno, queue_row in sorted(queue_by_idno.items(), key=lambda item: safe_int(item[1].get("download_priority_order"), 9999)):
        receipt = lookup.get((idno, "ddi_metadata"), {})
        path = PROJECT_ROOT / clean(receipt.get("saved_path"))
        if not path.exists():
            continue
        try:
            root = ET.parse(path).getroot()
        except Exception:
            continue
        for element in root.iter():
            if local_name(element.tag) != "fileDscr":
                continue
            rows.append(
                {
                    "download_priority_order": queue_row.get("download_priority_order", ""),
                    "queue_role": queue_row.get("queue_role", ""),
                    "country": queue_row.get("country", ""),
                    "wave": queue_row.get("wave", ""),
                    "idno": idno,
                    "catalog_id": parse_catalog_id(queue_row),
                    "file_id": element.attrib.get("ID", ""),
                    "file_name": short(xml_child_text(element, {"fileName"}), 220),
                    "file_description": short(xml_child_text(element, {"fileCont"}), 400),
                    "case_quantity": clean(xml_child_text(element, {"caseQnty"})),
                    "variable_quantity": clean(xml_child_text(element, {"varQnty"})),
                    "source_saved_path": receipt.get("saved_path", ""),
                    "source_sha256": receipt.get("sha256", ""),
                }
            )
    return rows


def build_summary(
    receipt_rows: list[dict[str, str]],
    dataset_rows: list[dict[str, str]],
    catalog_rows: list[dict[str, str]],
    file_rows: list[dict[str, str]],
) -> list[dict[str, str]]:
    status_counts = Counter(row.get("receipt_status", "") for row in receipt_rows)
    resource_counts = Counter(row.get("resource_type", "") for row in receipt_rows)
    dataset_status_counts = Counter(row.get("public_documentation_receipt_status", "") for row in dataset_rows)
    role_counts = Counter(row.get("queue_role", "") for row in dataset_rows)
    saved_rows = sum(1 for row in receipt_rows if is_saved(row.get("receipt_status", "")))
    failed_rows = sum(1 for row in receipt_rows if row.get("receipt_status", "").startswith("failed"))
    total_bytes = sum(safe_int(row.get("bytes")) for row in receipt_rows if is_saved(row.get("receipt_status", "")))
    access_gate_rows = sum(1 for row in dataset_rows if row.get("access_gate_detected") == "1")
    rows = [
        {"metric": "priority_lsms_isa_public_documentation_dataset_rows", "value": str(len(dataset_rows)), "interpretation": "Refocused LSMS/ISA queue datasets with public documentation receipt rows."},
        {"metric": "priority_lsms_isa_public_documentation_resource_rows", "value": str(len(receipt_rows)), "interpretation": "Public documentation and metadata resources attempted or reused for the refocused queue."},
        {"metric": "priority_lsms_isa_public_documentation_saved_rows", "value": str(saved_rows), "interpretation": "Public documentation resources saved or reused locally."},
        {"metric": "priority_lsms_isa_public_documentation_failed_rows", "value": str(failed_rows), "interpretation": "Public documentation resource requests that failed."},
        {"metric": "priority_lsms_isa_public_documentation_core_complete_dataset_rows", "value": str(sum(1 for row in dataset_rows if not row.get("missing_core_resource_types"))), "interpretation": "Datasets with all required public documentation and metadata resource types saved."},
        {"metric": "priority_lsms_isa_public_documentation_access_gate_rows", "value": str(access_gate_rows), "interpretation": "Datasets whose official get-microdata page still shows account, registration, terms, or request language."},
        {"metric": "priority_lsms_isa_public_documentation_catalog_digest_rows", "value": str(len(catalog_rows)), "interpretation": "Compact official catalog metadata digest rows extracted from saved JSON snapshots."},
        {"metric": "priority_lsms_isa_public_documentation_file_inventory_rows", "value": str(len(file_rows)), "interpretation": "Official DDI file-description rows extracted for Web-GPT-readable file planning."},
        {"metric": "priority_lsms_isa_public_documentation_saved_bytes", "value": str(total_bytes), "interpretation": "Total bytes in saved or reused public documentation snapshots."},
        {"metric": "priority_lsms_isa_public_documentation_handoff_readmes_written", "value": str(sum(1 for row in dataset_rows if row.get("handoff_readme"))), "interpretation": "Per-wave public documentation handoff files written."},
        {"metric": "priority_lsms_isa_public_documentation_data_write_status", "value": "blocked_no_promoted_rows", "interpretation": "Public documentation receipt is not sufficient to write analysis datasets to data/."},
        {"metric": "modeling_gate_status", "value": "blocked", "interpretation": "Models remain blocked until raw-backed promotion thresholds and accepted climate linkage pass."},
    ]
    for status, count in sorted(status_counts.items()):
        rows.append({"metric": f"priority_lsms_isa_public_documentation_receipt_status_{status or 'blank'}", "value": str(count), "interpretation": "Resource receipt status count."})
    for resource, count in sorted(resource_counts.items()):
        rows.append({"metric": f"priority_lsms_isa_public_documentation_resource_type_{resource or 'blank'}", "value": str(count), "interpretation": "Resource type count."})
    for status, count in sorted(dataset_status_counts.items()):
        rows.append({"metric": f"priority_lsms_isa_public_documentation_dataset_status_{status or 'blank'}", "value": str(count), "interpretation": "Dataset-level public documentation receipt status count."})
    for role, count in sorted(role_counts.items()):
        rows.append({"metric": f"priority_lsms_isa_public_documentation_queue_role_{role or 'blank'}", "value": str(count), "interpretation": "Dataset count by refocused queue role."})
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


def write_report(
    receipt_rows: list[dict[str, str]],
    dataset_rows: list[dict[str, str]],
    catalog_rows: list[dict[str, str]],
    file_rows: list[dict[str, str]],
    summary: list[dict[str, str]],
) -> None:
    summary_table = "\n".join(f"| {row['metric']} | {row['value']} | {row['interpretation']} |" for row in summary)
    failed_rows = [row for row in receipt_rows if row.get("receipt_status", "").startswith("failed") or row.get("receipt_status", "").startswith("missing_required")]
    REPORT_PATH.write_text(
        f"""# Priority LSMS-ISA Public Documentation Receipt

Status: public documentation and metadata receipt for the refocused 19-wave
LSMS/LSMS-ISA acquisition queue. This layer saves official get-microdata pages,
catalog JSON, variable JSON, DDI/XML, JSON metadata, data dictionaries, and
related-material pages where available. It does not download raw microdata and
does not bypass official account, registration, terms, or request gates.

## Summary

| Metric | Value | Interpretation |
|---|---:|---|
{summary_table}

## Dataset Receipt

{markdown_rows(dataset_rows, ['download_priority_order', 'queue_role', 'idno', 'country', 'wave', 'public_documentation_receipt_status', 'missing_core_resource_types', 'access_gate_detected'], 25)}

## Catalog Digest

{markdown_rows(catalog_rows, ['download_priority_order', 'idno', 'title', 'year_start', 'year_end', 'repositoryid', 'varcount', 'data_access_type', 'metadata_status'], 25)}

## Official DDI File Inventory Preview

{markdown_rows(file_rows, ['download_priority_order', 'idno', 'file_id', 'file_name', 'case_quantity', 'variable_quantity'], 40)}

## Failed Or Missing Required Resources

{markdown_rows(failed_rows, ['download_priority_order', 'idno', 'resource_type', 'receipt_status', 'http_status', 'notes'], 30) if failed_rows else 'No failed or missing required public documentation resources.'}

## Guardrails

- These snapshots support acquisition, file mapping, and pre-review only.
- They are not raw package receipts and do not verify values or row-level data.
- `data/` remains closed for these waves until complete original raw packages,
  manual value/key/unit/skip-pattern checks, survey-design checks,
  timing/geography checks, and accepted CHIRPS/ERA5 linkage pass.

## Machine-Readable Outputs

- `temp/priority_lsms_isa_public_documentation_receipt.csv`
- `temp/priority_lsms_isa_public_documentation_dataset_receipt.csv`
- `temp/priority_lsms_isa_public_documentation_catalog_digest.csv`
- `temp/priority_lsms_isa_public_documentation_file_inventory.csv`
- `result/priority_lsms_isa_public_documentation_receipt_summary.csv`
""",
        encoding="utf-8",
    )


def main() -> None:
    ensure_dirs()
    receipt_rows = build_receipt_rows()
    dataset_rows = build_dataset_rows(receipt_rows)
    catalog_rows = build_catalog_digest(receipt_rows)
    file_rows = build_file_inventory(receipt_rows)
    summary = build_summary(receipt_rows, dataset_rows, catalog_rows, file_rows)
    write_csv(RECEIPT_PATH, receipt_rows, RECEIPT_COLUMNS)
    write_csv(DATASET_RECEIPT_PATH, dataset_rows, DATASET_COLUMNS)
    write_csv(CATALOG_DIGEST_PATH, catalog_rows, CATALOG_DIGEST_COLUMNS)
    write_csv(FILE_INVENTORY_PATH, file_rows, FILE_INVENTORY_COLUMNS)
    write_csv(SUMMARY_PATH, summary, SUMMARY_COLUMNS)
    write_report(receipt_rows, dataset_rows, catalog_rows, file_rows, summary)
    append_log(
        TEMP_DIR / "audit_log.md",
        f"Built priority LSMS/ISA public documentation receipt datasets={len(dataset_rows)} resources={len(receipt_rows)}.",
    )
    print(f"Priority LSMS/ISA public documentation receipt datasets={len(dataset_rows)} resources={len(receipt_rows)}.")


if __name__ == "__main__":
    main()
