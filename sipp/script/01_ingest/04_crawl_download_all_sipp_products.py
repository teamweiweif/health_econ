from __future__ import annotations

import argparse
import csv
import hashlib
import html
import os
import re
import time
import zipfile
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass
from pathlib import Path
from urllib.parse import urljoin

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry


ROOT = Path(__file__).resolve().parents[2]
BASE_URL = "https://www2.census.gov/programs-surveys/sipp/data/datasets"
RAW_ROOT = ROOT / "temp" / "raw_downloads" / "census_sipp"
SOURCE_ROOT = ROOT / "temp" / "source_metadata" / "census_sipp"
METADATA_ROOT = ROOT / "data" / "metadata"

CATALOG_PATH = METADATA_ROOT / "sipp_official_file_catalog_2018_2025.csv"
MATRIX_PATH = METADATA_ROOT / "sipp_official_product_matrix_2018_2025.csv"
MANIFEST_PATH = METADATA_ROOT / "sipp_raw_download_manifest_2018_2025.csv"

YEARS = tuple(range(2018, 2026))
LONGITUDINAL_HORIZONS = {
    2018: (),
    2019: (2,),
    2020: (2, 3),
    2021: (2, 3, 4),
    2022: (2, 3),
    2023: (2, 3, 4),
    2024: (2, 3, 4),
    2025: (2, 3, 4),
}

LIGHTWEIGHT_SOURCE_PATTERNS = (
    re.compile(r"(?i)_schema\.json$"),
    re.compile(r"(?i)_validate\.xlsx?$"),
    re.compile(r"(?i)dictionary.*\.txt$"),
    re.compile(r"(?i)sipp.*metadata.*\.pdf$"),
    re.compile(r"(?i)sipp.*input_example\.(?:py|r)$"),
)


@dataclass(frozen=True)
class Product:
    year: int
    product_type: str
    horizon_years: int | None
    filename: str

    @property
    def url(self) -> str:
        return f"{BASE_URL}/{self.year}/{self.filename}"

    @property
    def local_path(self) -> Path:
        directories = {
            "primary": "primary",
            "replicate_weights": "replicate_weights",
            "longitudinal_weights": "longitudinal_weights",
            "longitudinal_replicate_weights": "longitudinal_replicate_weights",
        }
        return RAW_ROOT / str(self.year) / directories[self.product_type] / self.filename

    @property
    def product_id(self) -> str:
        horizon = f"_{self.horizon_years}y" if self.horizon_years else ""
        return f"sipp_{self.year}_{self.product_type}{horizon}"


def expected_products() -> list[Product]:
    products: list[Product] = []
    for year in YEARS:
        products.extend(
            [
                Product(year, "primary", None, f"pu{year}_csv.zip"),
                Product(year, "replicate_weights", None, f"rw{year}_csv.zip"),
            ]
        )
        for horizon in LONGITUDINAL_HORIZONS[year]:
            lgt_name = (
                "lgtwgt2019_csv.zip"
                if year == 2019 and horizon == 2
                else f"lgtwgt{year}yr{horizon}_csv.zip"
            )
            products.extend(
                [
                    Product(year, "longitudinal_weights", horizon, lgt_name),
                    Product(
                        year,
                        "longitudinal_replicate_weights",
                        horizon,
                        f"lgtrw{year}yr{horizon}_csv.zip",
                    ),
                ]
            )
    return products


def build_session() -> requests.Session:
    retry = Retry(
        total=8,
        connect=8,
        read=8,
        backoff_factor=2,
        status_forcelist=(429, 500, 502, 503, 504),
        allowed_methods=frozenset({"GET", "HEAD"}),
        respect_retry_after_header=True,
    )
    adapter = HTTPAdapter(max_retries=retry, pool_connections=8, pool_maxsize=8)
    session = requests.Session()
    session.headers.update({"User-Agent": "SIPP-source-audit/1.0 (official Census archive verification)"})
    session.mount("https://", adapter)
    return session


def relative(path: Path) -> str:
    return str(path.relative_to(ROOT))


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(8 * 1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def parse_directory_index(year: int, content: str) -> list[dict[str, str]]:
    row_pattern = re.compile(
        r"<tr>.*?<a\s+href=\"([^\"]+)\"[^>]*>.*?</a></td>"
        r"\s*<td[^>]*>(.*?)</td>\s*<td[^>]*>(.*?)</td>",
        flags=re.IGNORECASE | re.DOTALL,
    )
    rows: list[dict[str, str]] = []
    for href, modified, listed_size in row_pattern.findall(content):
        href = html.unescape(href.strip())
        if href.startswith(("?", "/")) or href in {"../", ""}:
            continue
        rows.append(
            {
                "year": str(year),
                "filename": href,
                "official_url": urljoin(f"{BASE_URL}/{year}/", href),
                "listed_last_modified": re.sub(r"<.*?>", "", modified).strip(),
                "listed_size": re.sub(r"<.*?>", "", listed_size).strip(),
            }
        )
    if not rows:
        raise RuntimeError(f"No source files parsed from the official {year} directory")
    return rows


def fetch_directory(year: int) -> tuple[int, list[dict[str, str]]]:
    url = f"{BASE_URL}/{year}/"
    snapshot = SOURCE_ROOT / str(year) / "official_dataset_directory_index.html"
    snapshot.parent.mkdir(parents=True, exist_ok=True)
    if snapshot.exists():
        content = snapshot.read_text(encoding="utf-8", errors="replace")
        try:
            return year, parse_directory_index(year, content)
        except RuntimeError:
            pass

    session = build_session()
    print(f"CRAWL {year}: {url}", flush=True)
    response = session.get(url, timeout=(30, 240))
    response.raise_for_status()
    content = response.text
    snapshot.write_text(content, encoding="utf-8")
    return year, parse_directory_index(year, content)


def classify_file(filename: str, expected_names: set[str]) -> dict[str, str | bool | int]:
    lower = filename.lower()
    product_type = "documentation_or_metadata"
    horizon: int | str = ""
    data_format = "other"

    if re.fullmatch(r"pu\d{4}.*", lower):
        product_type = "primary"
    elif re.fullmatch(r"rw\d{4}.*", lower):
        product_type = "replicate_weights"
    elif re.fullmatch(r"lgtwgt\d{4}.*", lower):
        product_type = "longitudinal_weights"
        match = re.search(r"yr([234])", lower)
        horizon = int(match.group(1)) if match else 2
    elif re.fullmatch(r"(?:lgtrw|lgtrepwgt)\d{4}.*", lower):
        product_type = "longitudinal_replicate_weights"
        match = re.search(r"yr([234])", lower)
        horizon = int(match.group(1)) if match else ""

    if lower.endswith("_csv.zip"):
        data_format = "csv_zip"
    elif lower.endswith(".csv.gz"):
        data_format = "csv_gzip"
    elif lower.endswith(("_dta.zip", ".dta.zip", ".dta.gz")):
        data_format = "stata"
    elif lower.endswith(("_sas.zip", "_sasdata.zip", ".sas7bdat.gz")):
        data_format = "sas"
    elif lower.endswith(".json"):
        data_format = "json_schema"
    elif lower.endswith((".xls", ".xlsx")):
        data_format = "validation_or_workbook"
    elif lower.endswith(".txt"):
        data_format = "text_dictionary"
    elif lower.endswith(".pdf"):
        data_format = "pdf_documentation"
    elif lower.endswith((".py", ".r")):
        data_format = "input_example"

    return {
        "product_type": product_type,
        "horizon_years": horizon,
        "data_format": data_format,
        "canonical_csv_product": filename in expected_names,
        "download_policy": (
            "download_raw_canonical"
            if filename in expected_names
            else "catalog_only_redundant_encoding"
            if data_format in {"csv_gzip", "stata", "sas"}
            else "download_lightweight_source"
            if any(pattern.search(filename) for pattern in LIGHTWEIGHT_SOURCE_PATTERNS)
            else "catalog_only_other"
        ),
    }


def crawl_catalog() -> list[dict[str, str | bool | int]]:
    by_year: dict[int, list[dict[str, str]]] = {}
    with ThreadPoolExecutor(max_workers=4) as pool:
        futures = {pool.submit(fetch_directory, year): year for year in YEARS}
        for future in as_completed(futures):
            year, rows = future.result()
            by_year[year] = rows
            print(f"CRAWL {year}: {len(rows)} files", flush=True)

    expected_names = {product.filename for product in expected_products()}
    catalog: list[dict[str, str | bool | int]] = []
    for year in YEARS:
        for row in by_year[year]:
            record: dict[str, str | bool | int] = dict(row)
            record.update(classify_file(row["filename"], expected_names))
            catalog.append(record)

    discovered = {str(row["filename"]) for row in catalog}
    missing = sorted(expected_names - discovered)
    if missing:
        raise RuntimeError(f"Official directory crawl is missing expected products: {missing}")
    write_csv(CATALOG_PATH, catalog)
    return catalog


def write_csv(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = list(rows[0]) if rows else []
    with path.open("w", newline="", encoding="utf-8-sig") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def zip_summary(path: Path) -> tuple[bool, str, int]:
    try:
        with zipfile.ZipFile(path) as archive:
            entries = archive.infolist()
            return True, "|".join(item.filename for item in entries), sum(item.file_size for item in entries)
    except (OSError, zipfile.BadZipFile):
        return False, "", 0


def download_file(url: str, destination: Path) -> None:
    destination.parent.mkdir(parents=True, exist_ok=True)
    if destination.exists():
        if destination.suffix.lower() != ".zip" or zip_summary(destination)[0]:
            print(f"EXISTS {relative(destination)} ({destination.stat().st_size:,} bytes)", flush=True)
            return
        raise RuntimeError(f"Existing ZIP is invalid and was not overwritten: {destination}")

    part = destination.with_name(destination.name + ".part")
    for attempt in range(1, 9):
        offset = part.stat().st_size if part.exists() else 0
        headers = {"Range": f"bytes={offset}-"} if offset else {}
        mode = "ab" if offset else "wb"
        try:
            session = build_session()
            with session.get(url, headers=headers, stream=True, timeout=(30, 300)) as response:
                if offset and response.status_code == 200:
                    offset = 0
                    mode = "wb"
                elif offset and response.status_code != 206:
                    response.raise_for_status()
                else:
                    response.raise_for_status()

                total_header = response.headers.get("Content-Range", "").rsplit("/", 1)
                if len(total_header) == 2 and total_header[1].isdigit():
                    expected_total = int(total_header[1])
                else:
                    content_length = int(response.headers.get("Content-Length", 0) or 0)
                    expected_total = offset + content_length if content_length else 0

                print(
                    f"DOWNLOAD {relative(destination)} attempt={attempt} start={offset:,} expected={expected_total:,}",
                    flush=True,
                )
                downloaded = offset
                next_report = time.monotonic() + 30
                with part.open(mode) as handle:
                    for block in response.iter_content(chunk_size=8 * 1024 * 1024):
                        if not block:
                            continue
                        handle.write(block)
                        downloaded += len(block)
                        if time.monotonic() >= next_report:
                            print(
                                f"PROGRESS {destination.name}: {downloaded / 1024**2:,.1f} MiB",
                                flush=True,
                            )
                            next_report = time.monotonic() + 30
            if expected_total and part.stat().st_size != expected_total:
                raise IOError(
                    f"Size mismatch for {destination.name}: {part.stat().st_size} != {expected_total}"
                )
            if destination.suffix.lower() == ".zip" and not zip_summary(part)[0]:
                raise zipfile.BadZipFile(f"Incomplete or invalid ZIP: {part}")
            os.replace(part, destination)
            print(f"DONE {relative(destination)} ({destination.stat().st_size:,} bytes)", flush=True)
            return
        except Exception as exc:  # retries preserve the .part file
            print(f"RETRY {destination.name} attempt={attempt}: {exc!r}", flush=True)
            if attempt == 8:
                raise
            time.sleep(min(60, 2**attempt))


def lightweight_destination(year: int, filename: str) -> Path:
    return SOURCE_ROOT / str(year) / filename


def download_all(catalog: list[dict[str, str | bool | int]]) -> None:
    canonical = expected_products()
    lightweight = [
        (str(row["official_url"]), lightweight_destination(int(str(row["year"])), str(row["filename"])))
        for row in catalog
        if row["download_policy"] == "download_lightweight_source"
    ]

    print(f"Downloading/verifying {len(lightweight)} lightweight source files", flush=True)
    with ThreadPoolExecutor(max_workers=4) as pool:
        futures = [pool.submit(download_file, url, path) for url, path in lightweight]
        for future in as_completed(futures):
            future.result()

    # Download smaller longitudinal products first, then the large annual replicate files.
    ordered = sorted(
        canonical,
        key=lambda product: (
            product.product_type == "replicate_weights",
            product.product_type == "primary",
            product.year,
            product.horizon_years or 0,
        ),
    )
    print(f"Downloading/verifying {len(ordered)} canonical CSV products", flush=True)
    with ThreadPoolExecutor(max_workers=3) as pool:
        futures = [pool.submit(download_file, product.url, product.local_path) for product in ordered]
        for future in as_completed(futures):
            future.result()


def build_matrix_and_manifest(catalog: list[dict[str, str | bool | int]]) -> None:
    catalog_names = {str(row["filename"]) for row in catalog}
    matrix: list[dict] = []
    manifest: list[dict] = []
    for product in expected_products():
        exists = product.local_path.exists()
        zip_valid, entries, uncompressed_bytes = (
            zip_summary(product.local_path) if exists else (False, "", 0)
        )
        base = {
            "product_id": product.product_id,
            "file_year": product.year,
            "reference_end_year": product.year - 1,
            "product_type": product.product_type,
            "horizon_years": product.horizon_years or "",
            "reference_start_year": (
                product.year - product.horizon_years
                if product.horizon_years
                else product.year - 1
            ),
            "official_filename": product.filename,
            "official_url": product.url,
            "listed_in_official_directory": product.filename in catalog_names,
            "canonical_format": "pipe_delimited_csv_in_zip",
            "local_relative_path": relative(product.local_path),
            "downloaded": exists,
        }
        matrix.append(base)
        manifest.append(
            {
                **base,
                "bytes": product.local_path.stat().st_size if exists else "",
                "sha256": sha256_file(product.local_path) if exists else "",
                "zip_structure_valid": zip_valid,
                "zip_entries": entries,
                "zip_uncompressed_bytes": uncompressed_bytes,
            }
        )
    write_csv(MATRIX_PATH, matrix)
    write_csv(MANIFEST_PATH, manifest)

    missing = [row["product_id"] for row in manifest if not row["downloaded"]]
    invalid = [row["product_id"] for row in manifest if row["downloaded"] and not row["zip_structure_valid"]]
    print(
        f"MATRIX products={len(matrix)} downloaded={len(matrix) - len(missing)} missing={len(missing)} invalid_zip={len(invalid)}",
        flush=True,
    )
    if missing:
        print("MISSING " + ", ".join(missing), flush=True)
    if invalid:
        print("INVALID " + ", ".join(invalid), flush=True)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Crawl and archive all official 2018-2025 SIPP CSV data-product versions."
    )
    parser.add_argument(
        "--crawl-only",
        action="store_true",
        help="Build the official catalog/matrix without downloading missing payloads.",
    )
    args = parser.parse_args()

    catalog = crawl_catalog()
    build_matrix_and_manifest(catalog)
    if not args.crawl_only:
        download_all(catalog)
        build_matrix_and_manifest(catalog)


if __name__ == "__main__":
    main()
