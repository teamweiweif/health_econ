from __future__ import annotations

import csv
import os
import re
import time
from pathlib import Path
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup

from common import SNAPSHOT_DIR, TEMP_DIR, append_log, ensure_dirs, sha256_file, utc_now_iso, write_csv


USER_AGENT = "Codex climate_uhc_ml microdata acquisition audit"
MAX_PRIORITY_DATASETS = int(os.environ.get("CLIMATE_UHC_MAX_PRIORITY_DATASETS", "35"))
MAX_RELATED_DOCS_PER_STUDY = int(os.environ.get("CLIMATE_UHC_MAX_RELATED_DOCS_PER_STUDY", "4"))
MAX_DOC_BYTES = int(os.environ.get("CLIMATE_UHC_MAX_DOC_BYTES", str(25 * 1024 * 1024)))


MANIFEST_COLUMNS = ["source_name", "dataset", "official_url", "files_needed", "reason", "status"]
PROGRESS_COLUMNS = ["priority_index", "country", "survey_name", "wave", "idno", "catalog_id", "status", "source_rows", "manifest_rows"]
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


def safe_name(text: str) -> str:
    text = re.sub(r"[^A-Za-z0-9._-]+", "_", text).strip("_")
    return text[:120] or "unnamed"


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
        old = merged[index[key]]
        old_status = old.get("status", "")
        new_status = row.get("status", "")
        if (
            (old_status.startswith("failed") or old_status.startswith("skipped"))
            and (new_status in {"downloaded", "already exists"} or row.get("checksum"))
        ):
            merged[index[key]] = row
    write_csv(path, merged, fieldnames)


def get(url: str) -> requests.Response:
    response = requests.get(url, headers={"User-Agent": USER_AGENT}, timeout=90, allow_redirects=True)
    response.raise_for_status()
    return response


def download(url: str, path: Path) -> tuple[bool, str]:
    if path.exists() and path.stat().st_size > 0:
        return True, "already exists"
    last_error = ""
    for attempt in range(1, 4):
        try:
            with requests.get(url, headers={"User-Agent": USER_AGENT}, timeout=120, stream=True, allow_redirects=True) as r:
                r.raise_for_status()
                total = int(r.headers.get("content-length") or 0)
                if total > MAX_DOC_BYTES:
                    return False, f"skipped, content-length {total} exceeds limit {MAX_DOC_BYTES}"
                path.parent.mkdir(parents=True, exist_ok=True)
                written = 0
                with path.open("wb") as f:
                    for chunk in r.iter_content(chunk_size=1024 * 1024):
                        if not chunk:
                            continue
                        written += len(chunk)
                        if written > MAX_DOC_BYTES:
                            path.unlink(missing_ok=True)
                            return False, f"skipped, streamed bytes exceed limit {MAX_DOC_BYTES}"
                        f.write(chunk)
            return path.exists() and path.stat().st_size > 0, "downloaded"
        except Exception as exc:
            last_error = str(exc)
            path.unlink(missing_ok=True)
            if attempt < 3:
                time.sleep(1.5 * attempt)
    return False, f"failed after retries: {last_error}"


def priority_rows() -> list[dict[str, str]]:
    rows = read_csv_dicts(TEMP_DIR / "country_wave_screening.csv")
    rows.sort(
        key=lambda r: (
            -int(r.get("feasibility score from 0 to 5") or 0),
            "impact evaluation" in r.get("survey name", "").lower(),
            r.get("country", ""),
            r.get("wave/year", ""),
        )
    )
    return [r for r in rows if int(r.get("feasibility score from 0 to 5") or 0) >= 5][:MAX_PRIORITY_DATASETS]


def related_doc_links(catalog_id: str) -> list[tuple[str, str]]:
    url = f"https://microdata.worldbank.org/catalog/{catalog_id}/related-materials"
    try:
        response = get(url)
    except Exception as exc:
        append_log(TEMP_DIR / "audit_log.md", f"Could not fetch related materials for catalog {catalog_id}: {exc}")
        return []
    soup = BeautifulSoup(response.text, "html.parser")
    links: list[tuple[str, str]] = []
    for a in soup.find_all("a", href=True):
        text = a.get_text(" ", strip=True)
        href = urljoin(url, a["href"])
        low = f"{text} {href}".lower()
        if "download" in low and any(ext in low for ext in ["pdf", "doc", "xls", "zip"]):
            links.append((text or "related material", href))
    deduped = []
    seen = set()
    for text, href in links:
        if href not in seen:
            deduped.append((text, href))
            seen.add(href)
    return deduped[:MAX_RELATED_DOCS_PER_STUDY]


def acquire_public_metadata(row: dict[str, str]) -> tuple[list[dict[str, str]], list[dict[str, str]]]:
    catalog_id = row["catalog id"]
    idno = row["idno"]
    stem = safe_name(f"{row['country']}_{row['wave/year']}_{idno}")
    schema_dir = TEMP_DIR / "raw_schema_inventory" / stem
    schema_dir.mkdir(parents=True, exist_ok=True)

    source_rows: list[dict[str, str]] = []
    manifest_rows: list[dict[str, str]] = []

    downloads = [
        (
            f"https://microdata.worldbank.org/metadata/export/{catalog_id}/json",
            schema_dir / f"{stem}_metadata_export.json",
            "World Bank NADA metadata JSON",
        ),
        (
            f"https://microdata.worldbank.org/index.php/api/catalog/{idno}/variables",
            schema_dir / f"{stem}_variables.json",
            "World Bank variable API JSON",
        ),
        (
            f"https://microdata.worldbank.org/catalog/{catalog_id}/pdf-documentation",
            schema_dir / f"{stem}_pdf_documentation.pdf",
            "World Bank generated PDF documentation",
        ),
    ]
    for url, path, label in downloads:
        try:
            ok, status = download(url, path)
        except Exception as exc:
            ok, status = False, f"failed: {exc}"
        source_rows.append(
            {
                "source name": f"{row['country']} - {row['survey name']} - {label}",
                "official URL": url,
                "access date": utc_now_iso(),
                "file/wave": str(path.relative_to(TEMP_DIR.parent)) if path.exists() else "",
                "unit": "catalog/schema/documentation",
                "geography": "",
                "row count": "",
                "column count": row.get("variable count", ""),
                "checksum": sha256_file(path) if path.exists() else "",
                "status": status if ok else status,
            }
        )

    for i, (text, url) in enumerate(related_doc_links(catalog_id), start=1):
        suffix = ".pdf" if ".pdf" in url.lower() or "pdf" in text.lower() else ".bin"
        path = schema_dir / f"{stem}_related_{i:02d}{suffix}"
        try:
            ok, status = download(url, path)
        except Exception as exc:
            ok, status = False, f"failed: {exc}"
        source_rows.append(
            {
                "source name": f"{row['country']} - {row['survey name']} - related material: {text[:80]}",
                "official URL": url,
                "access date": utc_now_iso(),
                "file/wave": str(path.relative_to(TEMP_DIR.parent)) if path.exists() else "",
                "unit": "documentation",
                "geography": "",
                "row count": "",
                "column count": "",
                "checksum": sha256_file(path) if path.exists() else "",
                "status": status if ok else status,
            }
        )

    get_microdata_url = f"https://microdata.worldbank.org/catalog/{catalog_id}/get-microdata"
    reason = "Catalog exposes public metadata/documentation, but the Get Microdata page requires login, registration, or a Data Access Agreement before raw files can be downloaded."
    try:
        page = get(get_microdata_url).text.lower()
        if "data access agreement" in page:
            reason = "Get Microdata page states that a Data Access Agreement is required before raw files can be downloaded."
        elif "login" in page or "register" in page:
            reason = "Get Microdata page requires login or registration before raw files can be downloaded."
    except Exception as exc:
        reason = f"Could not verify download form automatically: {exc}"
    manifest_rows.append(
        {
            "source_name": "World Bank Microdata Library",
            "dataset": f"{row['country']} - {row['survey name']} ({row['wave/year']}; {idno})",
            "official_url": get_microdata_url,
            "files_needed": "raw household/person/module files, questionnaires, codebooks, survey design files, geography/GPS files if available",
            "reason": reason,
            "status": "manual terms/login required for raw microdata; public metadata/docs saved where available",
        }
    )
    return source_rows, manifest_rows


def main() -> None:
    ensure_dirs()
    selected = priority_rows()
    all_source_rows: list[dict[str, str]] = []
    all_manifest_rows: list[dict[str, str]] = []
    progress_rows = read_csv_dicts(TEMP_DIR / "acquisition_progress.csv")
    write_csv(TEMP_DIR / "acquisition_progress.csv", progress_rows, PROGRESS_COLUMNS)
    for i, row in enumerate(selected, start=1):
        source_rows, manifest_rows = acquire_public_metadata(row)
        all_source_rows.extend(source_rows)
        all_manifest_rows.extend(manifest_rows)
        append_unique_csv(TEMP_DIR / "source_inventory.csv", source_rows, SOURCE_COLUMNS, ["source name", "official URL"])
        append_unique_csv(TEMP_DIR / "manual_download_manifest.csv", manifest_rows, MANIFEST_COLUMNS, ["source_name", "dataset", "official_url"])
        progress_rows = [
            existing
            for existing in progress_rows
            if existing.get("idno") != row.get("idno", "")
        ]
        progress_rows.append(
            {
                "priority_index": str(i),
                "country": row.get("country", ""),
                "survey_name": row.get("survey name", ""),
                "wave": row.get("wave/year", ""),
                "idno": row.get("idno", ""),
                "catalog_id": row.get("catalog id", ""),
                "status": "metadata_attempted_raw_manual",
                "source_rows": str(len(source_rows)),
                "manifest_rows": str(len(manifest_rows)),
            }
        )
        write_csv(TEMP_DIR / "acquisition_progress.csv", progress_rows, PROGRESS_COLUMNS)
        append_log(
            TEMP_DIR / "audit_log.md",
            f"Acquisition checkpoint {i}/{len(selected)} for {row.get('idno', '')}: source_rows={len(source_rows)} manifest_rows={len(manifest_rows)}.",
        )

    append_unique_csv(TEMP_DIR / "source_inventory.csv", all_source_rows, SOURCE_COLUMNS, ["source name", "official URL"])
    append_unique_csv(TEMP_DIR / "manual_download_manifest.csv", all_manifest_rows, MANIFEST_COLUMNS, ["source_name", "dataset", "official_url"])
    append_log(
        TEMP_DIR / "audit_log.md",
        f"Saved public metadata/documentation for {len(selected)} priority studies and routed raw microdata to manual manifest.",
    )
    print(f"Saved public metadata/documentation for {len(selected)} priority studies.")
    print("Raw microdata were not downloaded where login/Data Access Agreement gates were detected.")


if __name__ == "__main__":
    main()
