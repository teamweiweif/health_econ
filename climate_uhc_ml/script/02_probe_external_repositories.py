from __future__ import annotations

import csv
import os
import re
from pathlib import Path
from urllib.parse import urljoin, urlparse

import requests
from bs4 import BeautifulSoup

from common import TEMP_DIR, append_log, ensure_dirs, sha256_file, utc_now_iso, write_csv


USER_AGENT = "Codex climate_uhc_ml external repository probe"
MAX_EXTERNAL_PROBES = int(os.environ.get("CLIMATE_UHC_MAX_EXTERNAL_PROBES", "50"))
MAX_PAGE_BYTES = int(os.environ.get("CLIMATE_UHC_MAX_EXTERNAL_PAGE_BYTES", str(2 * 1024 * 1024)))
MAX_DIRECT_BYTES = int(os.environ.get("CLIMATE_UHC_MAX_DIRECT_RAW_BYTES", str(300 * 1024 * 1024)))
DOWNLOAD_DIRECT = os.environ.get("CLIMATE_UHC_DOWNLOAD_DIRECT", "0") == "1"

PROBE_PATH = TEMP_DIR / "external_repository_probe.csv"
DIRECT_DOWNLOAD_DIR = TEMP_DIR / "raw_downloads" / "direct_external"

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
RAW_HINTS = ["microdata", "stata", "spss", "sas", "data", "download", "public use", "puf", "household"]
ACCESS_GATE_HINTS = ["login", "log in", "sign in", "register", "registration", "data access agreement", "licensed", "request access"]

PROBE_COLUMNS = [
    "probe_time",
    "country",
    "survey_name",
    "wave",
    "idno",
    "catalog_id",
    "source_url",
    "final_url",
    "http_status",
    "content_type",
    "content_length",
    "probe_status",
    "access_gate_detected",
    "candidate_download_links",
    "downloaded_path",
    "download_sha256",
    "notes",
]


def read_csv_dicts(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        return []
    with path.open(encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def external_url(access_type: str) -> str:
    match = re.search(r"external repository:\s*(\S+)", access_type or "", flags=re.IGNORECASE)
    return match.group(1).rstrip(".,;") if match else ""


def safe_name(text: str) -> str:
    return re.sub(r"[^A-Za-z0-9._-]+", "_", text).strip("_")[:140] or "external_download"


def extension_from_url(url: str) -> str:
    return Path(urlparse(url).path).suffix.lower()


def looks_like_data_link(url: str, text: str = "") -> bool:
    suffix = extension_from_url(url)
    combined = f"{url} {text}".lower()
    return suffix in DATA_EXTENSIONS and any(hint in combined for hint in RAW_HINTS + list(DATA_EXTENSIONS))


def read_limited_text(response: requests.Response) -> str:
    chunks: list[bytes] = []
    total = 0
    for chunk in response.iter_content(chunk_size=64 * 1024):
        if not chunk:
            continue
        total += len(chunk)
        if total > MAX_PAGE_BYTES:
            break
        chunks.append(chunk)
    return b"".join(chunks).decode(response.encoding or "utf-8", errors="replace")


def candidate_links(base_url: str, html: str) -> list[str]:
    soup = BeautifulSoup(html, "html.parser")
    out = []
    seen = set()
    for a in soup.find_all("a", href=True):
        href = urljoin(base_url, a["href"])
        text = a.get_text(" ", strip=True)
        if not looks_like_data_link(href, text):
            continue
        if href in seen:
            continue
        seen.add(href)
        out.append(href)
    return out[:20]


def download_direct(url: str, idno: str) -> tuple[str, str, str]:
    if not DOWNLOAD_DIRECT:
        return "", "", "direct download disabled; set CLIMATE_UHC_DOWNLOAD_DIRECT=1 to enable"
    suffix = extension_from_url(url)
    if suffix not in DATA_EXTENSIONS:
        return "", "", "not a recognized raw/data extension"
    DIRECT_DOWNLOAD_DIR.mkdir(parents=True, exist_ok=True)
    name = safe_name(f"{idno}_{Path(urlparse(url).path).name or 'download'}")
    out = DIRECT_DOWNLOAD_DIR / name
    with requests.get(url, headers={"User-Agent": USER_AGENT}, timeout=120, stream=True, allow_redirects=True) as response:
        response.raise_for_status()
        total = int(response.headers.get("content-length") or 0)
        if total and total > MAX_DIRECT_BYTES:
            return "", "", f"skipped direct download; content-length {total} exceeds limit {MAX_DIRECT_BYTES}"
        written = 0
        with out.open("wb") as f:
            for chunk in response.iter_content(chunk_size=1024 * 1024):
                if not chunk:
                    continue
                written += len(chunk)
                if written > MAX_DIRECT_BYTES:
                    out.unlink(missing_ok=True)
                    return "", "", f"skipped direct download; streamed bytes exceed limit {MAX_DIRECT_BYTES}"
                f.write(chunk)
    return str(out.relative_to(TEMP_DIR.parent)), sha256_file(out), "downloaded"


def probe_one(row: dict[str, str]) -> dict[str, str]:
    src_url = external_url(row.get("access type", ""))
    base = {
        "probe_time": utc_now_iso(),
        "country": row.get("country", ""),
        "survey_name": row.get("survey name", ""),
        "wave": row.get("wave/year", ""),
        "idno": row.get("idno", ""),
        "catalog_id": row.get("catalog id", ""),
        "source_url": src_url,
        "final_url": "",
        "http_status": "",
        "content_type": "",
        "content_length": "",
        "probe_status": "",
        "access_gate_detected": "",
        "candidate_download_links": "",
        "downloaded_path": "",
        "download_sha256": "",
        "notes": "",
    }
    if not src_url:
        base["probe_status"] = "skipped_no_external_url"
        return base
    urls_to_try = [src_url]
    if src_url.startswith("http://"):
        urls_to_try.append("https://" + src_url[len("http://") :])

    last_error = ""
    for attempt_url in urls_to_try:
        try:
            with requests.get(attempt_url, headers={"User-Agent": USER_AGENT}, timeout=60, stream=True, allow_redirects=True) as response:
                base["final_url"] = response.url
                base["http_status"] = str(response.status_code)
                base["content_type"] = response.headers.get("content-type", "")
                base["content_length"] = response.headers.get("content-length", "")
                response.raise_for_status()
                content_type = base["content_type"].lower()
                suffix = extension_from_url(response.url)
                if suffix in DATA_EXTENSIONS and "html" not in content_type:
                    downloaded, digest, note = download_direct(response.url, row.get("idno", ""))
                    base["probe_status"] = "direct_raw_candidate_downloaded" if downloaded else "direct_raw_candidate_not_downloaded"
                    base["downloaded_path"] = downloaded
                    base["download_sha256"] = digest
                    base["notes"] = note
                    return base
                if "html" not in content_type and "text" not in content_type and not suffix:
                    base["probe_status"] = "non_html_non_data_response"
                    base["notes"] = "Response is not HTML and does not have a recognized data extension."
                    return base
                html = read_limited_text(response)
                break
        except Exception as exc:
            last_error = str(exc)
            html = ""
            continue
    else:
        base["probe_status"] = "failed"
        base["notes"] = last_error
        return base

    lower = html.lower()
    gate = any(hint in lower for hint in ACCESS_GATE_HINTS)
    links = candidate_links(base["final_url"] or src_url, html)
    base["access_gate_detected"] = "1" if gate else "0"
    base["candidate_download_links"] = ";".join(links)
    if gate and not links:
        base["probe_status"] = "html_access_gate_detected_no_direct_raw_links"
    elif links:
        base["probe_status"] = "html_candidate_raw_links"
    else:
        base["probe_status"] = "html_no_direct_raw_links"
    base["notes"] = "Probe does not bypass login/registration/terms; candidate links require separate verification."
    return base


def main() -> None:
    ensure_dirs()
    screening = read_csv_dicts(TEMP_DIR / "country_wave_screening.csv")
    candidates = [row for row in screening if external_url(row.get("access type", ""))]
    candidates.sort(key=lambda row: (-int(row.get("feasibility score from 0 to 5") or 0), row.get("country", ""), row.get("wave/year", "")))
    selected = candidates[:MAX_EXTERNAL_PROBES]
    rows = [probe_one(row) for row in selected]
    write_csv(PROBE_PATH, rows, PROBE_COLUMNS)
    append_log(TEMP_DIR / "audit_log.md", f"External repository probe checked {len(rows)} of {len(candidates)} external-repository candidates.")
    print(f"External repository probe checked {len(rows)} of {len(candidates)} external-repository candidates.")


if __name__ == "__main__":
    main()
