from __future__ import annotations

import argparse
import csv
import hashlib
import html
import re
import threading
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from urllib.parse import urljoin

import pandas as pd
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry


ROOT = Path(__file__).resolve().parents[2]
BASE_URL = "https://www2.census.gov/programs-surveys/sipp/data/datasets"
RAW_ROOT = ROOT / "temp" / "raw_downloads" / "census_sipp"
SOURCE_ROOT = ROOT / "temp" / "source_metadata" / "census_sipp"
METADATA_ROOT = ROOT / "data" / "metadata"
AUDIT_ROOT = ROOT / "data" / "sample_audits"

AUDIT_DATE = "20260716"
EXISTING_CATALOG = METADATA_ROOT / "sipp_official_file_catalog_2018_2025.csv"
MANIFEST = METADATA_ROOT / "sipp_raw_download_manifest_2018_2025.csv"
LIVE_CATALOG = METADATA_ROOT / f"sipp_live_official_channel_reaudit_{AUDIT_DATE}.csv"
REMOTE_COMPARISON = AUDIT_ROOT / f"sipp_remote_byte_comparison_{AUDIT_DATE}.csv"
REMOTE_CHECKS = AUDIT_ROOT / f"sipp_remote_source_reaudit_checks_{AUDIT_DATE}.csv"

YEARS = tuple(range(2018, 2026))
CHUNK_BYTES = 4 * 1024 * 1024
MAX_ATTEMPTS = 12

_PRINT_LOCK = threading.Lock()


def log(message: str) -> None:
    with _PRINT_LOCK:
        print(message, flush=True)


def write_csv(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = list(rows[0]) if rows else []
    with path.open("w", newline="", encoding="utf-8-sig") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def build_session() -> requests.Session:
    retry = Retry(
        total=6,
        connect=6,
        read=0,
        backoff_factor=1.5,
        status_forcelist=(429, 500, 502, 503, 504),
        allowed_methods=frozenset({"GET", "HEAD"}),
        respect_retry_after_header=True,
    )
    adapter = HTTPAdapter(max_retries=retry, pool_connections=4, pool_maxsize=4)
    session = requests.Session()
    session.headers.update(
        {"User-Agent": "SIPP-source-reaudit/2.0 (official Census byte verification)"}
    )
    session.mount("https://", adapter)
    return session


def parse_directory_index(year: int, content: str) -> list[dict[str, str]]:
    row_pattern = re.compile(
        r'<tr>.*?<a\s+href="([^"]+)"[^>]*>.*?</a></td>'
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
        raise RuntimeError(f"No files parsed from the live official {year} directory")
    return rows


def fetch_live_directory(year: int) -> tuple[int, list[dict[str, str]]]:
    url = f"{BASE_URL}/{year}/"
    response = None
    for attempt in range(1, 9):
        try:
            session = build_session()
            response = session.get(url, timeout=(20, 45))
            response.raise_for_status()
            break
        except Exception as exc:
            log(f"LIVE CRAWL RETRY {year}: attempt={attempt} error={exc!r}")
            if attempt == 8:
                raise
            time.sleep(min(20, 2**attempt))
    assert response is not None
    content = response.text
    snapshot = (
        SOURCE_ROOT
        / str(year)
        / f"official_dataset_directory_index_reaudit_{AUDIT_DATE}.html"
    )
    snapshot.parent.mkdir(parents=True, exist_ok=True)
    snapshot.write_text(content, encoding="utf-8")
    rows = parse_directory_index(year, content)
    fetched_at = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    for row in rows:
        row.update(
            {
                "directory_fetched_at_utc": fetched_at,
                "directory_http_date": response.headers.get("Date", ""),
                "directory_last_modified": response.headers.get("Last-Modified", ""),
                "directory_cache_age_seconds": response.headers.get("Age", ""),
                "directory_cf_cache_status": response.headers.get("CF-Cache-Status", ""),
            }
        )
    log(f"LIVE CRAWL {year}: {len(rows)} files")
    return year, rows


def crawl_live_catalog() -> list[dict]:
    old = pd.read_csv(EXISTING_CATALOG, dtype=str).fillna("")
    old_by_url = old.set_index("official_url").to_dict("index")
    live_by_year: dict[int, list[dict[str, str]]] = {}
    with ThreadPoolExecutor(max_workers=4) as pool:
        futures = {pool.submit(fetch_live_directory, year): year for year in YEARS}
        for future in as_completed(futures):
            year, rows = future.result()
            live_by_year[year] = rows

    output: list[dict] = []
    for year in YEARS:
        for row in live_by_year[year]:
            previous = old_by_url.get(row["official_url"], {})
            output.append(
                {
                    **row,
                    "present_in_prior_catalog": bool(previous),
                    "prior_listed_last_modified": previous.get("listed_last_modified", ""),
                    "prior_listed_size": previous.get("listed_size", ""),
                    "listed_metadata_changed": bool(previous)
                    and (
                        row["listed_last_modified"]
                        != previous.get("listed_last_modified", "")
                        or row["listed_size"] != previous.get("listed_size", "")
                    ),
                    "live_snapshot_relative_path": str(
                        (
                            SOURCE_ROOT
                            / str(year)
                            / f"official_dataset_directory_index_reaudit_{AUDIT_DATE}.html"
                        ).relative_to(ROOT)
                    ),
                }
            )
    write_csv(LIVE_CATALOG, output)
    return output


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(16 * 1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def content_range_total(value: str) -> int | None:
    match = re.search(r"/(\d+)$", value)
    return int(match.group(1)) if match else None


def remote_metadata(session: requests.Session, url: str) -> dict[str, str | int | bool]:
    response = session.head(url, allow_redirects=True, timeout=(30, 120))
    response.raise_for_status()
    return {
        "head_status": response.status_code,
        "remote_content_length": int(response.headers.get("Content-Length", 0) or 0),
        "remote_last_modified": response.headers.get("Last-Modified", ""),
        "remote_etag": response.headers.get("ETag", ""),
        "remote_accept_ranges": response.headers.get("Accept-Ranges", ""),
        "remote_content_type": response.headers.get("Content-Type", ""),
    }


def compare_one(row: dict) -> dict:
    path = ROOT / Path(str(row["local_relative_path"]))
    url = str(row["official_url"])
    product_id = str(row["product_id"])
    started = time.monotonic()
    result = {
        "product_id": product_id,
        "file_year": int(row["file_year"]),
        "product_type": str(row["product_type"]),
        "horizon_years": (
            int(float(row["horizon_years"]))
            if str(row.get("horizon_years", "")).strip() not in {"", "nan"}
            else ""
        ),
        "official_url": url,
        "local_relative_path": str(row["local_relative_path"]),
        "local_exists": path.exists(),
        "local_bytes": path.stat().st_size if path.exists() else 0,
        "manifest_sha256": str(row.get("sha256", "")),
    }
    if not path.exists():
        return {
            **result,
            "head_status": "",
            "remote_content_length": "",
            "remote_last_modified": "",
            "remote_etag": "",
            "remote_accept_ranges": "",
            "remote_content_type": "",
            "compared_bytes": 0,
            "first_mismatch_offset": "",
            "local_stream_sha256": "",
            "remote_stream_sha256": "",
            "remote_size_matches_local": False,
            "remote_bytes_exactly_match_local": False,
            "comparison_attempts": 0,
            "elapsed_seconds": 0,
            "status": "FAIL_LOCAL_MISSING",
            "error": "Local file does not exist",
        }

    session = build_session()
    try:
        metadata = remote_metadata(session, url)
    except Exception as exc:
        metadata = {
            "head_status": "",
            "remote_content_length": "",
            "remote_last_modified": "",
            "remote_etag": "",
            "remote_accept_ranges": "",
            "remote_content_type": "",
        }
        head_error = repr(exc)
    else:
        head_error = ""

    offset = 0
    attempts = 0
    first_mismatch: int | str = ""
    local_digest = hashlib.sha256()
    remote_digest = hashlib.sha256()
    expected_total = (
        int(metadata["remote_content_length"])
        if metadata.get("remote_content_length")
        else None
    )
    error = head_error
    exact = False
    next_report = time.monotonic() + 30

    with path.open("rb") as local_handle:
        while offset < path.stat().st_size and attempts < MAX_ATTEMPTS:
            attempts += 1
            headers = {"Range": f"bytes={offset}-"} if offset else {}
            try:
                with session.get(
                    url,
                    headers=headers,
                    stream=True,
                    timeout=(30, 300),
                ) as response:
                    if offset and response.status_code == 200:
                        log(f"RESTART {product_id}: server ignored Range at {offset:,}")
                        offset = 0
                        local_handle.seek(0)
                        local_digest = hashlib.sha256()
                        remote_digest = hashlib.sha256()
                        continue
                    response.raise_for_status()
                    if offset and response.status_code != 206:
                        raise IOError(
                            f"Expected HTTP 206 for resumed comparison, got {response.status_code}"
                        )
                    range_total = content_range_total(response.headers.get("Content-Range", ""))
                    if range_total is not None:
                        expected_total = range_total
                    elif not offset:
                        length = int(response.headers.get("Content-Length", 0) or 0)
                        if length:
                            expected_total = length

                    for remote_block in response.iter_content(chunk_size=CHUNK_BYTES):
                        if not remote_block:
                            continue
                        local_block = local_handle.read(len(remote_block))
                        if local_block != remote_block:
                            common = min(len(local_block), len(remote_block))
                            mismatch_in_block = next(
                                (
                                    index
                                    for index in range(common)
                                    if local_block[index] != remote_block[index]
                                ),
                                common,
                            )
                            first_mismatch = offset + mismatch_in_block
                            error = f"Byte mismatch at offset {first_mismatch}"
                            raise ValueError(error)
                        local_digest.update(local_block)
                        remote_digest.update(remote_block)
                        offset += len(remote_block)
                        if time.monotonic() >= next_report:
                            log(
                                f"REMOTE COMPARE {product_id}: "
                                f"{offset / 1024**2:,.1f}/{path.stat().st_size / 1024**2:,.1f} MiB"
                            )
                            next_report = time.monotonic() + 30
                    error = ""
            except ValueError:
                break
            except Exception as exc:
                error = repr(exc)
                log(
                    f"REMOTE RETRY {product_id}: attempt={attempts} "
                    f"confirmed={offset:,} error={error}"
                )
                if attempts < MAX_ATTEMPTS:
                    time.sleep(min(30, 2**min(attempts, 5)))

    local_size = path.stat().st_size
    size_match = expected_total == local_size if expected_total is not None else False
    if offset == local_size and size_match and first_mismatch == "":
        exact = local_digest.hexdigest() == remote_digest.hexdigest()
    status = "PASS" if exact else "FAIL"
    elapsed = time.monotonic() - started
    log(
        f"{status} REMOTE {product_id}: compared={offset:,}/{local_size:,} "
        f"attempts={attempts} seconds={elapsed:,.1f}"
    )
    return {
        **result,
        **metadata,
        "compared_bytes": offset,
        "first_mismatch_offset": first_mismatch,
        "local_stream_sha256": local_digest.hexdigest() if offset == local_size else "",
        "remote_stream_sha256": remote_digest.hexdigest() if offset == local_size else "",
        "remote_size_matches_local": size_match,
        "remote_bytes_exactly_match_local": exact,
        "comparison_attempts": attempts,
        "elapsed_seconds": round(elapsed, 3),
        "status": status,
        "error": error,
    }


def load_completed() -> dict[str, dict]:
    if not REMOTE_COMPARISON.exists():
        return {}
    prior = pd.read_csv(REMOTE_COMPARISON, dtype=str).fillna("")
    return {
        row["product_id"]: row
        for row in prior.to_dict("records")
        if row.get("status") == "PASS"
        and row.get("remote_bytes_exactly_match_local", "").lower() == "true"
    }


def compare_raw_products(manifest: pd.DataFrame, workers: int, force: bool) -> list[dict]:
    prior = {} if force else load_completed()
    current_rows = manifest.to_dict("records")
    output_by_id: dict[str, dict] = {}
    pending: list[dict] = []
    for row in current_rows:
        product_id = str(row["product_id"])
        local_path = ROOT / Path(str(row["local_relative_path"]))
        old = prior.get(product_id)
        reusable = (
            old is not None
            and local_path.exists()
            and str(local_path.stat().st_size) == str(old.get("local_bytes", ""))
            and str(row.get("sha256", "")) == str(old.get("manifest_sha256", ""))
        )
        if reusable:
            output_by_id[product_id] = old
            log(f"REUSE PASS {product_id}")
        else:
            pending.append(row)

    log(f"REMOTE BYTE AUDIT: pending={len(pending)} reusable={len(output_by_id)} workers={workers}")
    with ThreadPoolExecutor(max_workers=workers) as pool:
        futures = {pool.submit(compare_one, row): str(row["product_id"]) for row in pending}
        for future in as_completed(futures):
            record = future.result()
            output_by_id[str(record["product_id"])] = record
            ordered = [
                output_by_id[str(row["product_id"])]
                for row in current_rows
                if str(row["product_id"]) in output_by_id
            ]
            write_csv(REMOTE_COMPARISON, ordered)
    return [output_by_id[str(row["product_id"])] for row in current_rows]


def build_checks(live: list[dict], manifest: pd.DataFrame, comparison: list[dict]) -> list[dict]:
    live_urls = {row["official_url"] for row in live}
    expected_urls = set(manifest["official_url"].astype(str))
    compare_df = pd.DataFrame(comparison)
    size_pass = compare_df["remote_size_matches_local"].map(
        lambda value: value is True or str(value).strip().lower() == "true"
    )
    bytes_pass = compare_df["remote_bytes_exactly_match_local"].map(
        lambda value: value is True or str(value).strip().lower() == "true"
    )
    checks = [
        {
            "check_id": "live_year_directories",
            "requirement": "Fresh official directory snapshots cover every 2018-2025 file year",
            "passed": {int(row["year"]) for row in live} == set(YEARS),
            "evidence": f"years={sorted({int(row['year']) for row in live})}; live_files={len(live)}",
        },
        {
            "check_id": "canonical_products_still_listed",
            "requirement": "All 50 canonical CSV ZIP products remain listed in the live official archive",
            "passed": expected_urls.issubset(live_urls) and len(expected_urls) == 50,
            "evidence": f"expected=50; found={len(expected_urls & live_urls)}",
        },
        {
            "check_id": "remote_sizes_match",
            "requirement": "All current official remote Content-Length values match local ZIP byte sizes",
            "passed": len(compare_df) == 50 and size_pass.all(),
            "evidence": f"passed={int(size_pass.sum())}/{len(compare_df)}",
        },
        {
            "check_id": "remote_bytes_match",
            "requirement": "Every byte of all 50 local canonical ZIPs matches the current official remote file",
            "passed": len(compare_df) == 50 and bytes_pass.all(),
            "evidence": f"passed={int(bytes_pass.sum())}/{len(compare_df)}; compared_bytes={int(pd.to_numeric(compare_df['compared_bytes']).sum())}",
        },
    ]
    write_csv(REMOTE_CHECKS, checks)
    return checks


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Re-crawl official SIPP channels and byte-compare local canonical raw ZIPs."
    )
    parser.add_argument("--workers", type=int, default=3)
    parser.add_argument("--force", action="store_true", help="Repeat already-passing byte comparisons.")
    parser.add_argument(
        "--skip-byte-compare",
        action="store_true",
        help="Only refresh official directory snapshots and catalog status.",
    )
    args = parser.parse_args()

    if not EXISTING_CATALOG.exists() or not MANIFEST.exists():
        raise FileNotFoundError("Run 04_crawl_download_all_sipp_products.py first")

    live = crawl_live_catalog()
    manifest = pd.read_csv(MANIFEST, dtype=str).fillna("")
    if args.skip_byte_compare:
        log(f"LIVE CATALOG WRITTEN {LIVE_CATALOG.relative_to(ROOT)} rows={len(live)}")
        return
    comparison = compare_raw_products(manifest, max(1, args.workers), args.force)
    checks = build_checks(live, manifest, comparison)
    failed = [row for row in checks if not row["passed"]]
    log(
        f"REMOTE SOURCE REAUDIT COMPLETE checks={len(checks) - len(failed)}/{len(checks)} "
        f"raw_products={sum(row['status'] == 'PASS' for row in comparison)}/{len(comparison)}"
    )
    if failed:
        raise SystemExit(f"Remote source reaudit failed: {[row['check_id'] for row in failed]}")


if __name__ == "__main__":
    main()
