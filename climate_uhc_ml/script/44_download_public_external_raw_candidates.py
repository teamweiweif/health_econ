from __future__ import annotations

import csv
import os
import re
from pathlib import Path
from urllib.parse import urlparse

import requests

from common import REPORT_DIR, RESULT_DIR, TEMP_DIR, append_log, ensure_dirs, sha256_file, utc_now_iso, write_csv


PROBE_PATH = TEMP_DIR / "external_repository_probe.csv"
SCREENING_PATH = TEMP_DIR / "country_wave_screening.csv"
SOURCE_INVENTORY_PATH = TEMP_DIR / "source_inventory.csv"
DOWNLOAD_AUDIT_PATH = TEMP_DIR / "public_external_raw_candidate_downloads.csv"
SUMMARY_PATH = RESULT_DIR / "public_external_raw_candidate_download_summary.csv"
REPORT_PATH = REPORT_DIR / "public_external_raw_candidate_downloads.md"

USER_AGENT = "Codex climate_uhc_ml public external raw candidate downloader"
MAX_DOWNLOAD_BYTES = int(os.environ.get("CLIMATE_UHC_PUBLIC_EXTERNAL_MAX_BYTES", str(100 * 1024 * 1024)))
DOWNLOAD_ENABLED = os.environ.get("CLIMATE_UHC_PUBLIC_EXTERNAL_DOWNLOAD", "1") == "1"

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

AUDIT_COLUMNS = [
    "download_time",
    "country",
    "survey_name",
    "wave",
    "idno",
    "catalog_id",
    "source_probe_idno",
    "source_page_url",
    "candidate_url",
    "http_status",
    "content_type",
    "content_length",
    "local_path",
    "file_size_bytes",
    "sha256",
    "download_status",
    "mapping_reason",
    "notes",
]

SUMMARY_COLUMNS = ["metric", "value", "interpretation"]

SOURCE_COLUMNS = [
    "source name",
    "official URL",
    "access date",
    "file/wave",
    "unit",
    "geography",
    "row count",
    "column count",
    "checksum",
    "status",
]


def read_csv_dicts(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        return []
    with path.open(encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def append_unique_csv(path: Path, rows: list[dict[str, str]], fieldnames: list[str], key_fields: list[str]) -> None:
    existing = read_csv_dicts(path)
    index = {tuple(row.get(k, "") for k in key_fields): i for i, row in enumerate(existing)}
    merged = list(existing)
    for row in rows:
        key = tuple(row.get(k, "") for k in key_fields)
        if key not in index:
            merged.append(row)
            index[key] = len(merged) - 1
            continue
        current = merged[index[key]]
        if row.get("checksum") and not current.get("checksum"):
            merged[index[key]] = row
    write_csv(path, merged, fieldnames)


def split_semicolon(value: str) -> list[str]:
    out: list[str] = []
    seen: set[str] = set()
    for part in (value or "").split(";"):
        item = part.strip()
        if item and item not in seen:
            out.append(item)
            seen.add(item)
    return out


def suffix_from_url(url: str) -> str:
    return Path(urlparse(url).path).suffix.lower()


def filename_from_url(url: str) -> str:
    return Path(urlparse(url).path).name or "download.bin"


def years_in_text(value: str) -> list[str]:
    return re.findall(r"(?:19|20)\d{2}", value or "")


def normalized(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", " ", (value or "").lower()).strip()


def eligible_link(url: str) -> bool:
    suffix = suffix_from_url(url)
    if suffix not in DATA_EXTENSIONS:
        return False
    name = normalized(filename_from_url(url))
    # Avoid unrelated raw files on shared microdata pages.
    return "lsms" in name or "living standards" in name


def match_screening_row(probe_row: dict[str, str], url: str, screening: list[dict[str, str]]) -> tuple[dict[str, str] | None, str]:
    years = set(years_in_text(url))
    country = probe_row.get("country", "")
    candidates = []
    for row in screening:
        if row.get("country", "") != country:
            continue
        survey_name = row.get("survey name", "")
        if "living standards" not in survey_name.lower() and "lsms" not in survey_name.lower():
            continue
        wave_years = set(years_in_text(row.get("wave/year", "")))
        if years and not (years & wave_years):
            continue
        candidates.append(row)
    if not candidates:
        return None, "no matching screened LSMS country-year row"
    candidates.sort(key=lambda row: (-(int(row.get("feasibility score from 0 to 5") or 0)), row.get("wave/year", "")))
    match = candidates[0]
    return match, f"matched country={country}; url_years={','.join(sorted(years))}; screening_wave={match.get('wave/year', '')}"


def download_file(url: str, output_path: Path) -> tuple[str, str, str, str, str, str]:
    if output_path.exists() and output_path.stat().st_size > 0:
        return "already_exists", "", "", str(output_path.stat().st_size), sha256_file(output_path), ""
    if not DOWNLOAD_ENABLED:
        return "download_disabled", "", "", "", "", "set CLIMATE_UHC_PUBLIC_EXTERNAL_DOWNLOAD=1 to enable"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    try:
        with requests.get(url, headers={"User-Agent": USER_AGENT}, timeout=120, stream=True, allow_redirects=True) as response:
            status = str(response.status_code)
            content_type = response.headers.get("content-type", "")
            content_length = response.headers.get("content-length", "")
            response.raise_for_status()
            if "html" in content_type.lower():
                return "skipped_html_response", status, content_type, content_length, "", "candidate URL returned HTML, not a raw file"
            total = int(content_length or 0)
            if total and total > MAX_DOWNLOAD_BYTES:
                return "skipped_too_large", status, content_type, content_length, "", f"content-length exceeds {MAX_DOWNLOAD_BYTES}"
            written = 0
            with output_path.open("wb") as f:
                for chunk in response.iter_content(chunk_size=1024 * 1024):
                    if not chunk:
                        continue
                    written += len(chunk)
                    if written > MAX_DOWNLOAD_BYTES:
                        output_path.unlink(missing_ok=True)
                        return "skipped_too_large", status, content_type, str(written), "", f"streamed bytes exceed {MAX_DOWNLOAD_BYTES}"
                    f.write(chunk)
        return "downloaded", status, content_type, str(output_path.stat().st_size), sha256_file(output_path), ""
    except Exception as exc:
        output_path.unlink(missing_ok=True)
        return "failed", "", "", "", "", str(exc)


def build_download_rows() -> tuple[list[dict[str, str]], list[dict[str, str]]]:
    probes = read_csv_dicts(PROBE_PATH)
    screening = read_csv_dicts(SCREENING_PATH)
    rows: list[dict[str, str]] = []
    source_rows: list[dict[str, str]] = []
    seen: set[tuple[str, str]] = set()
    for probe in probes:
        for url in split_semicolon(probe.get("candidate_download_links", "")):
            if not eligible_link(url):
                continue
            match, reason = match_screening_row(probe, url, screening)
            if match is None:
                continue
            idno = match.get("idno", "")
            key = (idno, url)
            if key in seen:
                continue
            seen.add(key)
            local = TEMP_DIR / "raw_downloads" / idno / filename_from_url(url)
            status, http_status, content_type, content_length, digest, note = download_file(url, local)
            local_rel = str(local.relative_to(TEMP_DIR.parent)).replace("\\", "/") if local.exists() else ""
            rows.append(
                {
                    "download_time": utc_now_iso(),
                    "country": match.get("country", ""),
                    "survey_name": match.get("survey name", ""),
                    "wave": match.get("wave/year", ""),
                    "idno": idno,
                    "catalog_id": match.get("catalog id", ""),
                    "source_probe_idno": probe.get("idno", ""),
                    "source_page_url": probe.get("source_url", ""),
                    "candidate_url": url,
                    "http_status": http_status,
                    "content_type": content_type,
                    "content_length": content_length,
                    "local_path": local_rel,
                    "file_size_bytes": str(local.stat().st_size) if local.exists() else "",
                    "sha256": digest,
                    "download_status": status,
                    "mapping_reason": reason,
                    "notes": note or "public direct file link from screened external repository page; no login, terms bypass, or form automation used",
                }
            )
            if local.exists() and digest:
                source_rows.append(
                    {
                        "source name": f"{match.get('country', '')} - {match.get('survey name', '')} - public external raw archive",
                        "official URL": url,
                        "access date": utc_now_iso(),
                        "file/wave": local_rel,
                        "unit": "raw archive",
                        "geography": "",
                        "row count": "",
                        "column count": "",
                        "checksum": digest,
                        "status": status,
                    }
                )
    return rows, source_rows


def build_summary(rows: list[dict[str, str]]) -> list[dict[str, str]]:
    downloaded = sum(1 for row in rows if row.get("download_status") in {"downloaded", "already_exists"})
    datasets = {row.get("idno", "") for row in rows if row.get("download_status") in {"downloaded", "already_exists"}}
    bytes_total = sum(int(row.get("file_size_bytes") or 0) for row in rows if row.get("download_status") in {"downloaded", "already_exists"})
    failed = sum(1 for row in rows if row.get("download_status") not in {"downloaded", "already_exists"})
    return [
        {"metric": "public_external_candidate_rows", "value": str(len(rows)), "interpretation": "Matched public external raw candidate links."},
        {"metric": "public_external_downloaded_or_existing_rows", "value": str(downloaded), "interpretation": "Public external raw archives downloaded or already present."},
        {"metric": "public_external_dataset_rows", "value": str(len(datasets)), "interpretation": "Datasets with public external raw archives present."},
        {"metric": "public_external_failed_or_skipped_rows", "value": str(failed), "interpretation": "Candidate links not downloaded."},
        {"metric": "public_external_downloaded_bytes", "value": str(bytes_total), "interpretation": "Total bytes of present public external raw archives."},
    ]


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


def write_report(rows: list[dict[str, str]], summary: list[dict[str, str]]) -> None:
    summary_table = "\n".join(f"| {row['metric']} | {row['value']} | {row['interpretation']} |" for row in summary)
    REPORT_PATH.write_text(
        f"""# Public External Raw Candidate Downloads

Status: direct public-link acquisition audit. This step downloads only screened external candidate links that resolve to raw/archive files and match an existing country-wave screening row. It does not bypass login, registration, data access agreements, or terms forms.

## Summary

| Metric | Value | Interpretation |
|---|---:|---|
{summary_table}

## Downloads

{markdown_rows(rows, ['idno', 'survey_name', 'wave', 'candidate_url', 'download_status', 'file_size_bytes', 'local_path'], 30) if rows else 'No public external raw candidate links matched screening rows.'}

## Guardrails

- Downloaded archives are raw acquisition evidence only.
- RAR archives still require extraction before Stata/SPSS files can be schema-inspected.
- No harmonized dataset, outcomes, climate exposure, model, causal estimate, or policy simulation is justified by archive presence alone.

## Machine-Readable Outputs

- `temp/public_external_raw_candidate_downloads.csv`
- `result/public_external_raw_candidate_download_summary.csv`
""",
        encoding="utf-8",
    )


def main() -> None:
    ensure_dirs()
    rows, source_rows = build_download_rows()
    summary = build_summary(rows)
    write_csv(DOWNLOAD_AUDIT_PATH, rows, AUDIT_COLUMNS)
    write_csv(SUMMARY_PATH, summary, SUMMARY_COLUMNS)
    if source_rows:
        append_unique_csv(SOURCE_INVENTORY_PATH, source_rows, SOURCE_COLUMNS, ["source name", "official URL"])
    write_report(rows, summary)
    downloaded = sum(1 for row in rows if row.get("download_status") in {"downloaded", "already_exists"})
    append_log(TEMP_DIR / "audit_log.md", f"Downloaded/verified public external raw candidate archives rows={downloaded} matched_candidates={len(rows)}.")
    print(f"Public external raw candidate rows={len(rows)} downloaded_or_existing={downloaded}.")


if __name__ == "__main__":
    main()
