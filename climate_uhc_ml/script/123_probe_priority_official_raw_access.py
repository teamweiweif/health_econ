from __future__ import annotations

import csv
import re
from collections import Counter
from pathlib import Path
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup

from common import PROJECT_ROOT, REPORT_DIR, RESULT_DIR, SNAPSHOT_DIR, TEMP_DIR, append_log, ensure_dirs, sha256_file, utc_now_iso, write_csv


WAVE_PLAN_PATH = RESULT_DIR / "priority_promotion_acquisition_wave_plan.csv"
PROBE_PATH = TEMP_DIR / "priority_official_raw_access_probe.csv"
SUMMARY_PATH = RESULT_DIR / "priority_official_raw_access_summary.csv"
REPORT_PATH = REPORT_DIR / "priority_official_raw_access_probe.md"
SNAPSHOT_ROOT = SNAPSHOT_DIR / "priority_official_raw_access"

USER_AGENT = "Codex climate_uhc_ml priority official raw access probe"
MAX_BYTES = 2 * 1024 * 1024
TIMEOUT = 60

DATA_EXTENSIONS = {
    ".dta",
    ".sav",
    ".por",
    ".sas7bdat",
    ".xpt",
    ".csv",
    ".tsv",
    ".txt",
    ".xlsx",
    ".xls",
    ".zip",
    ".tar",
    ".gz",
    ".tgz",
    ".7z",
    ".rar",
}
RAW_LINK_HINTS = ["microdata", "data", "download", "stata", "spss", "sas", "zip", "dta", "public use"]
GATE_HINTS = ["login", "log in", "sign in", "register", "registration", "terms", "data access agreement", "licensed", "request access"]

PROBE_COLUMNS = [
    "probe_time",
    "acquisition_batch_rank",
    "batch_role",
    "country",
    "survey_name",
    "wave",
    "idno",
    "catalog_id",
    "official_url",
    "final_url",
    "http_status",
    "content_type",
    "content_length",
    "saved_snapshot",
    "snapshot_sha256",
    "access_gate_detected",
    "login_link",
    "register_link",
    "request_or_terms_links",
    "candidate_raw_links",
    "candidate_metadata_links",
    "direct_raw_route_status",
    "manual_action_status",
    "local_target_folder",
    "next_action",
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


def catalog_id(url: str) -> str:
    match = re.search(r"/catalog/(\d+)", url or "")
    return match.group(1) if match else ""


def extension_from_url(url: str) -> str:
    clean = (url or "").split("?", 1)[0].split("#", 1)[0]
    return Path(clean).suffix.lower()


def read_limited(response: requests.Response) -> tuple[bytes, str]:
    chunks: list[bytes] = []
    total = 0
    for chunk in response.iter_content(chunk_size=64 * 1024):
        if not chunk:
            continue
        total += len(chunk)
        if total > MAX_BYTES:
            return b"".join(chunks), f"truncated_at_{MAX_BYTES}_bytes"
        chunks.append(chunk)
    return b"".join(chunks), ""


def text_from_content(content: bytes, response: requests.Response) -> str:
    encoding = response.encoding or "utf-8"
    return content.decode(encoding, errors="replace")


def classify_links(base_url: str, html: str) -> tuple[str, str, str, str, str]:
    soup = BeautifulSoup(html, "html.parser")
    login = ""
    register = ""
    terms: list[str] = []
    raw_links: list[str] = []
    metadata_links: list[str] = []
    seen_terms: set[str] = set()
    seen_raw: set[str] = set()
    seen_meta: set[str] = set()
    for anchor in soup.find_all("a", href=True):
        href = urljoin(base_url, anchor["href"])
        text = anchor.get_text(" ", strip=True)
        low = f"{href} {text}".lower()
        if not login and any(token in low for token in ["login", "log in", "sign in"]):
            login = href
        if not register and "register" in low:
            register = href
        if any(token in low for token in ["terms", "request access", "data access agreement", "licensed"]):
            if href not in seen_terms:
                terms.append(href)
                seen_terms.add(href)
        suffix = extension_from_url(href)
        if suffix in DATA_EXTENSIONS or any(token in low for token in RAW_LINK_HINTS):
            if href not in seen_raw:
                raw_links.append(href)
                seen_raw.add(href)
        if any(token in low for token in ["/metadata/export/", "/data-dictionary", "/pdf-documentation", "/related-materials", "metadata", "questionnaire", "codebook"]):
            if href not in seen_meta:
                metadata_links.append(href)
                seen_meta.add(href)
    return login, register, ";".join(terms[:10]), ";".join(raw_links[:30]), ";".join(metadata_links[:30])


def status_from_html(html: str, candidate_raw_links: str) -> tuple[str, str, str, str]:
    low = html.lower()
    gate = any(hint in low for hint in GATE_HINTS)
    raw_links = [link for link in candidate_raw_links.split(";") if link.strip()]
    direct_data_links = [link for link in raw_links if extension_from_url(link) in DATA_EXTENSIONS]
    if direct_data_links and not gate:
        return (
            "possible_direct_raw_links_unverified",
            "direct_link_review_required",
            "Review candidate direct links, confirm terms, then place original files under local_target_folder.",
            "Candidate data-extension links exist; this script does not download raw files or bypass terms.",
        )
    if direct_data_links and gate:
        return (
            "candidate_raw_links_behind_or_near_access_gate",
            "manual_account_or_terms_required",
            "Complete official account/terms workflow, then download complete raw package.",
            "Candidate data links appear with access-gate language; manual review required.",
        )
    if gate:
        return (
            "no_direct_raw_route_access_gate_detected",
            "manual_account_or_terms_required",
            "Complete official login/register/request/terms workflow, then download complete raw package.",
            "Official get-microdata page contains login/registration/request/terms signals.",
        )
    if raw_links:
        return (
            "candidate_download_links_no_raw_extension",
            "manual_review_required",
            "Review download-like official links and confirm whether they expose the full raw package.",
            "Download-like links exist but no recognized raw data extension was confirmed.",
        )
    return (
        "no_direct_raw_route_found",
        "manual_review_required",
        "Manually review official catalog page and data-access instructions.",
        "No recognized direct raw-data link was found on the official page.",
    )


def probe_one(row: dict[str, str]) -> dict[str, str]:
    url = row.get("official_url", "")
    base = {
        "probe_time": utc_now_iso(),
        "acquisition_batch_rank": row.get("acquisition_batch_rank", ""),
        "batch_role": row.get("batch_role", ""),
        "country": row.get("country", ""),
        "survey_name": row.get("survey_name", ""),
        "wave": row.get("wave", ""),
        "idno": row.get("idno", ""),
        "catalog_id": catalog_id(url),
        "official_url": url,
        "final_url": "",
        "http_status": "",
        "content_type": "",
        "content_length": "",
        "saved_snapshot": "",
        "snapshot_sha256": "",
        "access_gate_detected": "",
        "login_link": "",
        "register_link": "",
        "request_or_terms_links": "",
        "candidate_raw_links": "",
        "candidate_metadata_links": "",
        "direct_raw_route_status": "",
        "manual_action_status": "",
        "local_target_folder": row.get("local_target_folder", ""),
        "next_action": "",
        "notes": "",
    }
    if not url:
        base["direct_raw_route_status"] = "missing_official_url"
        base["manual_action_status"] = "manual_url_recovery_required"
        base["next_action"] = "Recover official URL before raw acquisition."
        return base
    try:
        with requests.get(url, headers={"User-Agent": USER_AGENT}, timeout=TIMEOUT, stream=True, allow_redirects=True) as response:
            base["final_url"] = response.url
            base["http_status"] = str(response.status_code)
            base["content_type"] = response.headers.get("content-type", "")
            base["content_length"] = response.headers.get("content-length", "")
            content, note = read_limited(response)
            if response.status_code != 200:
                base["direct_raw_route_status"] = "official_page_http_error"
                base["manual_action_status"] = "manual_review_required"
                base["next_action"] = "Manually open official URL and inspect access route."
                base["notes"] = f"HTTP {response.status_code}; {note}".strip("; ")
                return base
    except Exception as exc:
        base["direct_raw_route_status"] = "official_page_request_failed"
        base["manual_action_status"] = "manual_review_required"
        base["next_action"] = "Retry official URL manually and inspect access route."
        base["notes"] = str(exc)
        return base

    snapshot_dir = SNAPSHOT_ROOT / safe_name(f"{row.get('acquisition_batch_rank', '')}_{row.get('idno', '')}")
    snapshot_dir.mkdir(parents=True, exist_ok=True)
    snapshot_path = snapshot_dir / "get_microdata.html"
    snapshot_path.write_bytes(content)
    base["saved_snapshot"] = str(snapshot_path.relative_to(PROJECT_ROOT)).replace("\\", "/")
    base["snapshot_sha256"] = sha256_file(snapshot_path)

    html = text_from_content(content, response)
    login, register, terms, raw_links, metadata_links = classify_links(base["final_url"] or url, html)
    direct_status, manual_status, next_action, notes = status_from_html(html, raw_links)
    base["access_gate_detected"] = "1" if any(hint in html.lower() for hint in GATE_HINTS) else "0"
    base["login_link"] = login
    base["register_link"] = register
    base["request_or_terms_links"] = terms
    base["candidate_raw_links"] = raw_links
    base["candidate_metadata_links"] = metadata_links
    base["direct_raw_route_status"] = direct_status
    base["manual_action_status"] = manual_status
    base["next_action"] = next_action
    base["notes"] = notes
    return base


def build_summary(rows: list[dict[str, str]]) -> list[dict[str, str]]:
    direct_counts = Counter(row["direct_raw_route_status"] for row in rows)
    manual_counts = Counter(row["manual_action_status"] for row in rows)
    role_counts = Counter(row["batch_role"] for row in rows)
    gate_rows = sum(1 for row in rows if row.get("access_gate_detected") == "1")
    possible_direct = sum(1 for row in rows if row.get("direct_raw_route_status") == "possible_direct_raw_links_unverified")
    manual_required = sum(1 for row in rows if row.get("manual_action_status") != "direct_link_review_required")
    rows_out = [
        {"metric": "priority_official_raw_access_probe_rows", "value": str(len(rows)), "interpretation": "Priority acquisition and backup waves with official get-microdata pages probed."},
        {"metric": "priority_10_wave_probe_rows", "value": str(role_counts.get("priority_10_wave_batch", 0)), "interpretation": "Immediate priority 10-wave batch rows probed."},
        {"metric": "sixth_country_backup_probe_rows", "value": str(role_counts.get("sixth_country_backup_candidate", 0)), "interpretation": "Backup sixth-country rows probed."},
        {"metric": "access_gate_detected_rows", "value": str(gate_rows), "interpretation": "Rows with login/register/request/terms language on official pages."},
        {"metric": "possible_direct_raw_link_rows", "value": str(possible_direct), "interpretation": "Rows with possible direct raw links not requiring gate language; no raw files are downloaded by this probe."},
        {"metric": "manual_action_required_rows", "value": str(manual_required), "interpretation": "Rows needing manual account, terms, or review steps."},
        {"metric": "modeling_gate_status", "value": "blocked", "interpretation": "Models remain blocked until promoted registry thresholds pass."},
    ]
    for status, count in sorted(direct_counts.items()):
        rows_out.append({"metric": f"direct_raw_route_status_{status or 'blank'}", "value": str(count), "interpretation": "Direct raw route status count."})
    for status, count in sorted(manual_counts.items()):
        rows_out.append({"metric": f"manual_action_status_{status or 'blank'}", "value": str(count), "interpretation": "Manual action status count."})
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


def count_table(counter: Counter[str], label: str) -> str:
    lines = [f"| {label} | Count |", "|---|---:|"]
    for key, count in counter.most_common():
        lines.append(f"| {key or 'blank'} | {count} |")
    return "\n".join(lines)


def write_report(rows: list[dict[str, str]], summary: list[dict[str, str]]) -> None:
    direct_counts = Counter(row["direct_raw_route_status"] for row in rows)
    manual_counts = Counter(row["manual_action_status"] for row in rows)
    summary_table = "\n".join(f"| {row['metric']} | {row['value']} | {row['interpretation']} |" for row in summary)
    REPORT_PATH.write_text(
        f"""# Priority Official Raw Access Probe

Status: official-page access probe for the priority 10-wave acquisition batch
and sixth-country backup candidates. This script snapshots official World Bank
get-microdata pages and classifies visible login, registration, request, terms,
and direct-link signals. It does not download raw microdata and does not bypass
access controls.

## Summary

| Metric | Value | Interpretation |
|---|---:|---|
{summary_table}

## Direct Raw Route Status

{count_table(direct_counts, 'Direct raw route status') if rows else 'No priority access probe rows exist.'}

## Manual Action Status

{count_table(manual_counts, 'Manual action status') if rows else 'No priority access probe rows exist.'}

## Probe Rows

{markdown_rows(rows, ['acquisition_batch_rank', 'batch_role', 'idno', 'http_status', 'access_gate_detected', 'direct_raw_route_status', 'manual_action_status', 'login_link'], 20)}

## Interpretation Guardrails

- A saved HTML page is documentation evidence, not raw microdata.
- Candidate raw links are not downloaded or treated as usable unless access
  terms are manually satisfied.
- If an access gate is detected, the dataset remains blocked until account,
  terms, or Data Access Agreement steps are completed and raw files are placed
  in `temp/raw_downloads/`.
- Do not promote, harmonize into final `data/`, or run models from this probe.

## Machine-Readable Outputs

- `temp/priority_official_raw_access_probe.csv`
- `result/priority_official_raw_access_summary.csv`
""",
        encoding="utf-8",
    )


def main() -> None:
    ensure_dirs()
    rows = [probe_one(row) for row in read_csv_dicts(WAVE_PLAN_PATH)]
    summary = build_summary(rows)
    write_csv(PROBE_PATH, rows, PROBE_COLUMNS)
    write_csv(SUMMARY_PATH, summary, SUMMARY_COLUMNS)
    write_report(rows, summary)
    append_log(TEMP_DIR / "audit_log.md", f"Probed priority official raw access pages rows={len(rows)}.")
    print(f"Priority official raw access probe rows={len(rows)}.")


if __name__ == "__main__":
    main()
