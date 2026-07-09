from __future__ import annotations

import csv
import os
import re
import time
from collections import Counter
from pathlib import Path
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup

from common import PROJECT_ROOT, REPORT_DIR, SNAPSHOT_DIR, TEMP_DIR, append_log, ensure_dirs, sha256_file, utc_now_iso, write_csv


TOP_N = int(os.environ.get("CLIMATE_UHC_PUBLIC_DOC_TOP_N", "20"))
MAX_BYTES = int(os.environ.get("CLIMATE_UHC_PUBLIC_DOC_MAX_BYTES", str(25 * 1024 * 1024)))
REQUEST_RETRIES = int(os.environ.get("CLIMATE_UHC_PUBLIC_DOC_RETRIES", "3"))
USER_AGENT = "Codex climate_uhc_ml public documentation snapshot"

AUDIT_PATH = TEMP_DIR / "worldbank_public_documentation_audit.csv"
SUMMARY_PATH = TEMP_DIR / "worldbank_access_gate_summary.csv"
REPORT_PATH = REPORT_DIR / "public_documentation_audit.md"
SNAPSHOT_ROOT = SNAPSHOT_DIR / "worldbank_public_documentation"

AUDIT_COLUMNS = [
    "snapshot_time",
    "priority_rank",
    "priority_score",
    "idno",
    "catalog_id",
    "dataset",
    "resource_type",
    "url",
    "final_url",
    "http_status",
    "content_type",
    "content_length",
    "status",
    "saved_path",
    "sha256",
    "access_gate_detected",
    "login_link",
    "register_link",
    "metadata_links",
    "notes",
]

SUMMARY_COLUMNS = [
    "priority_rank",
    "idno",
    "catalog_id",
    "dataset",
    "get_microdata_status",
    "access_gate_detected",
    "login_link",
    "register_link",
    "saved_resource_count",
    "failed_resource_count",
    "oversize_resource_count",
    "notes",
]

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


def priority_rows() -> list[dict[str, str]]:
    rows = read_csv_dicts(TEMP_DIR / "manual_download_priority.csv")
    world_bank = [row for row in rows if row.get("source_name") == "World Bank Microdata Library"]
    selected = []
    for row in world_bank:
        catalog_id = catalog_id_from_url(row.get("official_url", ""))
        if not catalog_id:
            continue
        selected.append(row)
    selected.sort(key=lambda row: int(row.get("priority_rank") or 999999))
    return selected[:TOP_N]


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
        if not login_link and "login" in text:
            login_link = href
        if not register_link and "register" in text:
            register_link = href
        if any(token in href.lower() for token in ["/metadata/export/", "/pdf-documentation", "/data-dictionary", "/related-materials"]):
            if href not in metadata_links:
                metadata_links.append(href)
    return gate, login_link, register_link, ";".join(metadata_links[:20])


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
    return "saved", str(out_path.relative_to(PROJECT_ROOT)), sha256_file(out_path)


def reuse_saved_row(row: dict[str, str], resource_type: str, out_path: Path, previous: dict[tuple[str, str], dict[str, str]]) -> dict[str, str] | None:
    idno = row.get("idno", "")
    prior = previous.get((idno, resource_type))
    if not prior or prior.get("status") != "saved" or not out_path.exists() or out_path.stat().st_size == 0:
        return None
    reused = dict(prior)
    reused["snapshot_time"] = utc_now_iso()
    reused["notes"] = "existing snapshot reused"
    reused["sha256"] = sha256_file(out_path)
    if resource_type.endswith("_html"):
        html = out_path.read_text(encoding="utf-8", errors="replace")
        gate, login_link, register_link, metadata_links = metadata_from_html(reused.get("final_url") or reused.get("url", ""), html)
        reused["access_gate_detected"] = gate
        reused["login_link"] = login_link
        reused["register_link"] = register_link
        reused["metadata_links"] = metadata_links
    return reused


def snapshot_resource(row: dict[str, str], resource_type: str, url: str, previous: dict[tuple[str, str], dict[str, str]]) -> dict[str, str]:
    catalog_id = catalog_id_from_url(row.get("official_url", ""))
    idno = row.get("idno", "")
    folder = SNAPSHOT_ROOT / safe_name(f"{row.get('priority_rank', '')}_{idno or catalog_id}")
    out_path = folder / f"{resource_type}{EXTENSIONS[resource_type]}"
    reused = reuse_saved_row(row, resource_type, out_path, previous)
    if reused is not None:
        return reused
    base = {
        "snapshot_time": utc_now_iso(),
        "priority_rank": row.get("priority_rank", ""),
        "priority_score": row.get("priority_score", ""),
        "idno": idno,
        "catalog_id": catalog_id,
        "dataset": row.get("dataset", ""),
        "resource_type": resource_type,
        "url": url,
        "final_url": "",
        "http_status": "",
        "content_type": "",
        "content_length": "",
        "status": "",
        "saved_path": "",
        "sha256": "",
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
                    base["status"] = "failed_http"
                    base["notes"] = f"HTTP {response.status_code}"
                    return base
                status, saved_path, note_or_hash = write_response_limited(response, out_path)
                base["status"] = status
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
        base["status"] = "failed_request"
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


def build_summary(rows: list[dict[str, str]]) -> list[dict[str, str]]:
    grouped: dict[str, list[dict[str, str]]] = {}
    for row in rows:
        grouped.setdefault(row.get("idno", ""), []).append(row)

    summary_rows = []
    for idno, values in grouped.items():
        get_row = next((row for row in values if row.get("resource_type") == "get_microdata_html"), {})
        saved_count = sum(1 for row in values if row.get("status") == "saved")
        failed_count = sum(1 for row in values if row.get("status", "").startswith("failed"))
        oversize_count = sum(1 for row in values if row.get("status") == "skipped_oversize")
        summary_rows.append(
            {
                "priority_rank": get_row.get("priority_rank", values[0].get("priority_rank", "")),
                "idno": idno,
                "catalog_id": get_row.get("catalog_id", values[0].get("catalog_id", "")),
                "dataset": get_row.get("dataset", values[0].get("dataset", "")),
                "get_microdata_status": get_row.get("status", ""),
                "access_gate_detected": get_row.get("access_gate_detected", ""),
                "login_link": get_row.get("login_link", ""),
                "register_link": get_row.get("register_link", ""),
                "saved_resource_count": str(saved_count),
                "failed_resource_count": str(failed_count),
                "oversize_resource_count": str(oversize_count),
                "notes": "Raw files were not downloaded; only public documentation and metadata endpoints were snapshotted.",
            }
        )
    summary_rows.sort(key=lambda row: int(row.get("priority_rank") or 999999))
    return summary_rows


def markdown_count_table(counter: Counter[str], key_name: str) -> str:
    lines = [f"| {key_name} | Count |", "|---|---:|"]
    for key, count in counter.most_common():
        lines.append(f"| {key or 'blank'} | {count} |")
    return "\n".join(lines)


def write_report(rows: list[dict[str, str]], summary_rows: list[dict[str, str]]) -> None:
    status_counts = Counter(row.get("status", "") for row in rows)
    resource_counts = Counter(row.get("resource_type", "") for row in rows)
    gate_count = sum(1 for row in summary_rows if row.get("access_gate_detected") == "1")
    lines = [
        "# Public Documentation Audit",
        "",
        "Status: public World Bank documentation and metadata were snapshotted for priority gated datasets. This does not download or bypass raw microdata access controls.",
        "",
        "## Coverage",
        "",
        f"- Priority World Bank datasets attempted: {len(summary_rows)}",
        f"- Resource rows attempted: {len(rows)}",
        f"- Datasets with login/register/terms gate detected on Get Microdata page: {gate_count}",
        "",
        "## Resource Status",
        "",
        markdown_count_table(status_counts, "Status"),
        "",
        "## Resource Types",
        "",
        markdown_count_table(resource_counts, "Resource type"),
        "",
        "## Dataset Summary",
        "",
        "| Rank | IDNO | Catalog | Saved resources | Failed | Oversize | Access gate |",
        "|---:|---|---:|---:|---:|---:|---|",
    ]
    for row in summary_rows:
        lines.append(
            "| {rank} | `{idno}` | {catalog} | {saved} | {failed} | {oversize} | {gate} |".format(
                rank=row.get("priority_rank", ""),
                idno=row.get("idno", ""),
                catalog=row.get("catalog_id", ""),
                saved=row.get("saved_resource_count", ""),
                failed=row.get("failed_resource_count", ""),
                oversize=row.get("oversize_resource_count", ""),
                gate=row.get("access_gate_detected", ""),
            )
        )
    lines.extend(
        [
            "",
            "## Files",
            "",
            f"- Machine-readable resource audit: `temp/{AUDIT_PATH.name}`",
            f"- Dataset access-gate summary: `temp/{SUMMARY_PATH.name}`",
            "- Snapshots: `temp/source_snapshots/worldbank_public_documentation/`",
            "",
            "## Guardrail",
            "",
            "Rows in this audit are documentation and metadata snapshots only. Raw survey microdata must still be manually downloaded under permitted account/terms workflows into `temp/raw_downloads/` before harmonization or analysis.",
        ]
    )
    REPORT_PATH.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    ensure_dirs()
    selected = priority_rows()
    previous_rows = read_csv_dicts(AUDIT_PATH)
    previous = {(row.get("idno", ""), row.get("resource_type", "")): row for row in previous_rows}
    rows: list[dict[str, str]] = []
    for row in selected:
        catalog_id = catalog_id_from_url(row.get("official_url", ""))
        for resource_type, template in RESOURCE_TYPES.items():
            url = template.format(catalog_id=catalog_id)
            rows.append(snapshot_resource(row, resource_type, url, previous))
    summary_rows = build_summary(rows)
    write_csv(AUDIT_PATH, rows, AUDIT_COLUMNS)
    write_csv(SUMMARY_PATH, summary_rows, SUMMARY_COLUMNS)
    write_report(rows, summary_rows)
    saved = sum(1 for row in rows if row.get("status") == "saved")
    append_log(
        TEMP_DIR / "audit_log.md",
        f"Snapshotted public World Bank documentation for {len(summary_rows)} priority datasets; saved resources={saved}.",
    )
    print(f"Public documentation snapshot datasets={len(summary_rows)} resources={len(rows)} saved={saved}")


if __name__ == "__main__":
    main()
