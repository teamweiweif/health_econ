from __future__ import annotations

import argparse
import csv
import hashlib
import html
import re
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from urllib.parse import urljoin, urlparse

import pandas as pd
import requests
from bs4 import BeautifulSoup
from pypdf import PdfReader
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry


ROOT = Path(__file__).resolve().parents[2]
SOURCE_ROOT = ROOT / "temp" / "source_metadata" / "census_sipp"
METADATA_ROOT = ROOT / "data" / "metadata"
AUDIT_ROOT = ROOT / "data" / "sample_audits"
AUDIT_DATE = "20260716"

TECH_BASE = "https://www2.census.gov/programs-surveys/sipp/tech-documentation"
USER_NOTES_BASE = (
    "https://www.census.gov/programs-surveys/sipp/tech-documentation/user-notes"
)
DATASETS_PAGE = "https://www.census.gov/programs-surveys/sipp/data/datasets.html"
WEIGHT_GUIDE_URL = (
    "https://www2.census.gov/programs-surveys/sipp/Select_weights_2018_SIPP_JUN24.pdf"
)
LATEST_CORE_DOCUMENTS = (
    (
        "2025_users_guide",
        f"{TECH_BASE}/methodology/2025_SIPP_Users_Guide.pdf",
        SOURCE_ROOT / "2025" / "2025_SIPP_Users_Guide.pdf",
    ),
    (
        "2025_source_and_accuracy_statement",
        f"{TECH_BASE}/source-accuracy-statements/2025/SIPP-2025-SA.pdf",
        SOURCE_ROOT / "2025" / "SIPP-2025-SA.pdf",
    ),
)

YEARS = tuple(range(2018, 2026))
LEGACY_PANELS = tuple(range(1984, 1994)) + (1996, 2001, 2004, 2008, 2014)

TECH_CATALOG = METADATA_ROOT / f"sipp_official_technical_document_catalog_{AUDIT_DATE}.csv"
RELEASE_LEDGER = METADATA_ROOT / "sipp_release_version_ledger_2018_2025.csv"
USER_NOTE_INVENTORY = METADATA_ROOT / "sipp_official_user_notes_inventory_2018_2025.csv"
LEGACY_SCOPE = METADATA_ROOT / "sipp_legacy_official_archive_scope.csv"
LEGACY_LINKS = METADATA_ROOT / "sipp_legacy_official_file_link_catalog.csv"
WEIGHT_LEDGER = METADATA_ROOT / "sipp_weight_product_use_ledger.csv"
DOCUMENT_PROVENANCE = METADATA_ROOT / f"sipp_official_document_provenance_{AUDIT_DATE}.csv"
ISSUE_REGISTER = AUDIT_ROOT / f"sipp_raw_and_weight_issue_register_{AUDIT_DATE}.csv"

PANEL_VARIABLES = METADATA_ROOT / "sipp_2018_2025_panel_variable_inventory.csv"
WEIGHT_GUIDE_PATH = SOURCE_ROOT / "common" / "Select_weights_2018_SIPP_JUN24.pdf"
WEIGHT_GUIDE_TEXT = SOURCE_ROOT / "common" / "Select_weights_2018_SIPP_JUN24.txt"


def log(message: str) -> None:
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
        total=5,
        connect=5,
        read=0,
        backoff_factor=1.5,
        status_forcelist=(429, 500, 502, 503, 504),
        allowed_methods=frozenset({"GET", "HEAD"}),
        respect_retry_after_header=True,
    )
    adapter = HTTPAdapter(max_retries=retry, pool_connections=8, pool_maxsize=8)
    session = requests.Session()
    session.headers.update(
        {"User-Agent": "SIPP-documentation-audit/1.0 (official Census source verification)"}
    )
    session.mount("https://", adapter)
    return session


def fetch(url: str, attempts: int = 8, read_timeout: int = 75) -> requests.Response:
    for attempt in range(1, attempts + 1):
        try:
            response = build_session().get(url, timeout=(20, read_timeout))
            response.raise_for_status()
            return response
        except Exception as exc:
            log(f"FETCH RETRY attempt={attempt} url={url} error={exc!r}")
            if attempt == attempts:
                raise
            time.sleep(min(20, 2**attempt))
    raise AssertionError("unreachable")


def sha256_bytes(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(8 * 1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def parse_apache_index(content: str, base_url: str) -> list[dict[str, str]]:
    row_pattern = re.compile(
        r'<tr>.*?<a\s+href="([^"]+)"[^>]*>.*?</a></td>'
        r"\s*<td[^>]*>(.*?)</td>\s*<td[^>]*>(.*?)</td>",
        flags=re.IGNORECASE | re.DOTALL,
    )
    rows = []
    for href, modified, listed_size in row_pattern.findall(content):
        href = html.unescape(href.strip())
        if href.startswith(("?", "/")) or href in {"../", ""}:
            continue
        rows.append(
            {
                "filename": href,
                "official_url": urljoin(base_url, href),
                "listed_last_modified": re.sub(r"<.*?>", "", modified).strip(),
                "listed_size": re.sub(r"<.*?>", "", listed_size).strip(),
            }
        )
    return rows


def crawl_technical_year(year: int) -> tuple[int, list[dict]]:
    url = f"{TECH_BASE}/{year}/"
    snapshot = SOURCE_ROOT / str(year) / f"official_technical_directory_reaudit_{AUDIT_DATE}.html"
    expected_release = (
        "2018_Release_Notes.pdf" if year == 2018 else f"{year}_SIPP_Release_Notes.pdf"
    )
    response = None
    rows: list[dict[str, str]] = []
    if snapshot.exists():
        cached = snapshot.read_text(encoding="utf-8", errors="replace")
        rows = parse_apache_index(cached, url)
        if expected_release in {row["filename"] for row in rows}:
            log(f"TECH CRAWL {year}: reuse current audit snapshot")
    if expected_release not in {row["filename"] for row in rows}:
        for attempt in range(1, 9):
            response = fetch(url)
            rows = parse_apache_index(response.text, url)
            if expected_release in {row["filename"] for row in rows}:
                snapshot.parent.mkdir(parents=True, exist_ok=True)
                snapshot.write_bytes(response.content)
                break
            log(
                f"TECH INDEX RETRY {year}: attempt={attempt} parsed={len(rows)} "
                f"missing={expected_release}"
            )
            if attempt == 8:
                raise RuntimeError(
                    f"Live technical index never listed {expected_release}; parsed={len(rows)}"
                )
            time.sleep(min(20, 2**attempt))
    fetched_at = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    for row in rows:
        row.update(
            {
                "year": year,
                "fetched_at_utc": fetched_at,
                "directory_http_date": response.headers.get("Date", "") if response else "",
                "directory_last_modified": (
                    response.headers.get("Last-Modified", "") if response else ""
                ),
                "directory_cache_age_seconds": response.headers.get("Age", "") if response else "",
                "snapshot_relative_path": str(snapshot.relative_to(ROOT)),
            }
        )
    log(f"TECH CRAWL {year}: {len(rows)} files")
    return year, rows


def crawl_technical_catalog() -> list[dict]:
    by_year: dict[int, list[dict]] = {}
    with ThreadPoolExecutor(max_workers=4) as pool:
        futures = {pool.submit(crawl_technical_year, year): year for year in YEARS}
        for future in as_completed(futures):
            year, rows = future.result()
            by_year[year] = rows
    output = [row for year in YEARS for row in by_year[year]]
    write_csv(TECH_CATALOG, output)
    return output


def extract_pdf_text(path: Path) -> str:
    reader = PdfReader(path)
    return "\n".join(page.extract_text() or "" for page in reader.pages)


def release_notes_local_path(year: int) -> Path:
    candidates = sorted((SOURCE_ROOT / str(year)).glob("*Release_Notes.pdf"))
    if len(candidates) != 1:
        raise FileNotFoundError(f"Expected one release-notes PDF for {year}: {candidates}")
    return candidates[0]


def current_version(text: str) -> tuple[str, str, str]:
    matches = re.findall(
        r"Version\s+([0-9.]+)\s*\(Released\s+([0-9/]+)\)", text, flags=re.IGNORECASE
    )
    if not matches:
        raise ValueError("No release version/date found")
    parsed = sorted(matches, key=lambda item: tuple(int(x) for x in item[0].split(".")), reverse=True)
    version, current_date = parsed[0]
    initial = next((date for ver, date in matches if ver == "1.0"), "")
    return version, current_date, initial


def build_release_ledger(tech_catalog: list[dict]) -> tuple[list[dict], list[dict]]:
    tech_by_name = {(int(row["year"]), row["filename"]): row for row in tech_catalog}
    ledger = []
    provenance = []
    for year in YEARS:
        local = release_notes_local_path(year)
        text = extract_pdf_text(local)
        version, release_date, initial_date = current_version(text)
        remote_row = tech_by_name.get((year, local.name))
        official_url = (
            remote_row["official_url"] if remote_row else f"{TECH_BASE}/{year}/{local.name}"
        )
        response = fetch(official_url, read_timeout=180)
        remote_sha = sha256_bytes(response.content)
        local_sha = sha256_file(local)
        exact = response.content == local.read_bytes()
        correction = year <= 2021 and version == "1.1"
        ledger.append(
            {
                "file_year": year,
                "reference_year": year - 1,
                "current_release_version": version,
                "current_release_date_as_printed": release_date,
                "initial_release_date_as_printed": initial_date,
                "updated_2025_07_24": correction,
                "social_security_amount_correction": correction,
                "tssamt_and_downstream_income_poverty_recodes_affected": correction,
                "thtotinct2_minor_correction": year in (2018, 2019, 2020),
                "correction_summary": (
                    "TSSSAMT Medicare Parts B/C/D deductions were double-counted; Census rebuilt "
                    "TSSSAMT and dependent personal/family/household income and poverty recodes."
                    if correction
                    else "No later public-use file version documented in the current release notes."
                ),
                "official_release_notes_url": official_url,
                "local_relative_path": str(local.relative_to(ROOT)),
                "remote_bytes_exactly_match_local": exact,
                "local_sha256_project_generated": local_sha,
                "remote_sha256_project_generated": remote_sha,
                "official_checksum_published": False,
            }
        )
        provenance.append(
            {
                "document_role": f"{year}_release_notes",
                "official_url": official_url,
                "local_relative_path": str(local.relative_to(ROOT)),
                "bytes": local.stat().st_size,
                "sha256_project_generated": local_sha,
                "remote_bytes_exactly_match_local": exact,
                "remote_last_modified": response.headers.get("Last-Modified", ""),
                "remote_etag": response.headers.get("ETag", ""),
                "official_checksum_published": False,
            }
        )
        log(f"RELEASE {year}: v{version} exact_remote_match={exact}")
    write_csv(RELEASE_LEDGER, ledger)
    return ledger, provenance


def archive_weight_guide(provenance: list[dict]) -> str:
    response = fetch(WEIGHT_GUIDE_URL, read_timeout=180)
    WEIGHT_GUIDE_PATH.parent.mkdir(parents=True, exist_ok=True)
    prior_equal = WEIGHT_GUIDE_PATH.exists() and WEIGHT_GUIDE_PATH.read_bytes() == response.content
    WEIGHT_GUIDE_PATH.write_bytes(response.content)
    text = extract_pdf_text(WEIGHT_GUIDE_PATH)
    WEIGHT_GUIDE_TEXT.write_text(text, encoding="utf-8")
    provenance.append(
        {
            "document_role": "2018_plus_weight_selection_guide",
            "official_url": WEIGHT_GUIDE_URL,
            "local_relative_path": str(WEIGHT_GUIDE_PATH.relative_to(ROOT)),
            "bytes": WEIGHT_GUIDE_PATH.stat().st_size,
            "sha256_project_generated": sha256_file(WEIGHT_GUIDE_PATH),
            "remote_bytes_exactly_match_local": True,
            "remote_last_modified": response.headers.get("Last-Modified", ""),
            "remote_etag": response.headers.get("ETag", ""),
            "official_checksum_published": False,
        }
    )
    log(f"WEIGHT GUIDE: bytes={len(response.content)} prior_equal={prior_equal}")
    return text


def archive_latest_core_documents(provenance: list[dict]) -> None:
    for role, url, path in LATEST_CORE_DOCUMENTS:
        response = fetch(url, read_timeout=240)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(response.content)
        provenance.append(
            {
                "document_role": role,
                "official_url": url,
                "local_relative_path": str(path.relative_to(ROOT)),
                "bytes": path.stat().st_size,
                "sha256_project_generated": sha256_file(path),
                "remote_bytes_exactly_match_local": path.read_bytes() == response.content,
                "remote_last_modified": response.headers.get("Last-Modified", ""),
                "remote_etag": response.headers.get("ETag", ""),
                "official_checksum_published": False,
            }
        )
        log(f"LATEST DOC {role}: bytes={len(response.content)}")


def build_weight_ledger(weight_text: str) -> list[dict]:
    required_phrases = ("WPFINWGT", "FINYR2", "FINYR3", "FINYR4", "REPWGT240")
    missing = [phrase for phrase in required_phrases if phrase not in weight_text]
    if missing:
        raise ValueError(f"Official weight guide extraction is missing {missing}")
    rows = [
        {
            "estimand_time_scope": "monthly cross-sectional",
            "point_weight": "WPFINWGT",
            "point_weight_source": "primary public-use file",
            "required_row_restriction": "MONTHCODE equals target month",
            "replicate_weight_source": "rwYYYY annual replicate file",
            "replicate_variables": "REPWGT1-REPWGT240",
            "variance_method": "Fay BRR; rho=0.5; MSE form",
            "official_guidance": "Use WPFINWGT and matching annual replicate weights.",
        },
        {
            "estimand_time_scope": "annual cross-sectional",
            "point_weight": "WPFINWGT",
            "point_weight_source": "primary public-use file",
            "required_row_restriction": "MONTHCODE=12 after constructing annual measure",
            "replicate_weight_source": "rwYYYY annual replicate file",
            "replicate_variables": "REPWGT1-REPWGT240",
            "variance_method": "Fay BRR; rho=0.5; MSE form",
            "official_guidance": "Use December WPFINWGT and December annual replicate weights.",
        },
        {
            "estimand_time_scope": "two consecutive calendar years",
            "point_weight": "FINYR2",
            "point_weight_source": "lgtwgtYYYYyr2 cohort file",
            "required_row_restriction": "Eligible continuously observed 2-year cohort",
            "replicate_weight_source": "lgtrwYYYYyr2 longitudinal replicate file",
            "replicate_variables": "REPWGT1-REPWGT240",
            "variance_method": "Fay BRR; rho=0.5; MSE form",
            "official_guidance": "Use FINYR2 and the matching 2-year longitudinal replicates.",
        },
        {
            "estimand_time_scope": "three consecutive calendar years",
            "point_weight": "FINYR3",
            "point_weight_source": "lgtwgtYYYYyr3 cohort file",
            "required_row_restriction": "Eligible continuously observed 3-year cohort",
            "replicate_weight_source": "lgtrwYYYYyr3 longitudinal replicate file",
            "replicate_variables": "REPWGT1-REPWGT240",
            "variance_method": "Fay BRR; rho=0.5; MSE form",
            "official_guidance": "Use FINYR3 and the matching 3-year longitudinal replicates.",
        },
        {
            "estimand_time_scope": "four consecutive calendar years",
            "point_weight": "FINYR4",
            "point_weight_source": "lgtwgtYYYYyr4 cohort file",
            "required_row_restriction": "Eligible continuously observed 4-year cohort",
            "replicate_weight_source": "lgtrwYYYYyr4 longitudinal replicate file",
            "replicate_variables": "REPWGT1-REPWGT240",
            "variance_method": "Fay BRR; rho=0.5; MSE form",
            "official_guidance": "Use FINYR4 and the matching 4-year longitudinal replicates.",
        },
    ]
    for row in rows:
        row["official_weight_guide_url"] = WEIGHT_GUIDE_URL
        row["official_variance_formula"] = (
            "variance = sum((replicate_estimate - full_sample_estimate)^2) / "
            "(240 * 0.5^2)"
        )
    write_csv(WEIGHT_LEDGER, rows)
    return rows


def user_note_index(year: int) -> tuple[int, list[str]]:
    url = f"{USER_NOTES_BASE}/{year}-usernotes.html"
    response = fetch(url)
    snapshot = SOURCE_ROOT / str(year) / f"official_user_notes_index_reaudit_{AUDIT_DATE}.html"
    snapshot.write_bytes(response.content)
    soup = BeautifulSoup(response.text, "html.parser")
    marker = f"/{year}-usernotes/"
    links = sorted(
        {
            urljoin(url, anchor["href"])
            for anchor in soup.select("a[href]")
            if marker in anchor.get("href", "") and anchor.get("href", "").lower().endswith(".html")
        }
    )
    log(f"USER NOTE INDEX {year}: {len(links)} notes")
    return year, links


def classify_domain(text: str) -> str:
    lowered = text.lower()
    domains = []
    terms = {
        "health_insurance": (
            "health insurance",
            "medicaid",
            "medicare",
            "marketplace",
            "uninsured",
            "coverage",
            "premium",
        ),
        "income_poverty": ("income", "poverty", "social security", "earnings", "tssamt"),
        "weights_sampling": ("weight", "nonresponse", "sample design", "sampling"),
        "employment": ("employment", "job", "work schedule", "labor force"),
        "food_security": ("food security", "food insecurity", "school meal", "snap"),
        "family_relationship": ("relationship", "fertility", "marital", "household composition"),
        "education": ("school enrollment", "education", "degree"),
    }
    for domain, keywords in terms.items():
        if any(keyword in lowered for keyword in keywords):
            domains.append(domain)
    return "|".join(domains) if domains else "other"


def parse_modified_date(soup: BeautifulSoup, text: str) -> str:
    for selector in (
        'meta[name="DC.date"]',
        'meta[name="date"]',
        'meta[property="article:modified_time"]',
    ):
        node = soup.select_one(selector)
        if node and node.get("content"):
            return str(node["content"])
    match = re.search(r"Last Revised:\s*([A-Za-z]+\s+\d{1,2},\s+\d{4})", text)
    return match.group(1) if match else ""


def fetch_user_note(year: int, url: str, panel_variables: set[str]) -> dict:
    response = fetch(url)
    soup = BeautifulSoup(response.text, "html.parser")
    h1 = soup.select_one("h1")
    title = " ".join((h1.get_text(" ", strip=True) if h1 else soup.title.get_text(" ", strip=True)).split())
    description_node = soup.select_one('meta[name="description"]')
    description = description_node.get("content", "").strip() if description_node else ""
    page_text = " ".join(soup.get_text(" ", strip=True).split())
    upper_tokens = set(re.findall(r"\b[A-Z][A-Z0-9_]{2,}\b", page_text.upper()))
    matched = sorted(panel_variables & upper_tokens)
    domain = classify_domain(f"{title} {description} {page_text}")
    issue_language = bool(
        re.search(
            r"\b(error|incorrect|inconsisten|quality concern|not comparable|allocation|missing)\w*",
            f"{title} {description}",
            flags=re.IGNORECASE,
        )
    )
    if matched and issue_language:
        priority = "high"
    elif matched or any(x in domain for x in ("health_insurance", "income_poverty", "weights_sampling")):
        priority = "medium"
    else:
        priority = "low"
    slug = Path(urlparse(url).path).name
    snapshot = SOURCE_ROOT / "user_notes" / str(year) / slug
    snapshot.parent.mkdir(parents=True, exist_ok=True)
    snapshot.write_bytes(response.content)
    return {
        "file_year_page": year,
        "title": title,
        "description": description,
        "official_url": url,
        "domain_tags": domain,
        "current_panel_variables_named": "|".join(matched),
        "current_panel_variable_match_count": len(matched),
        "issue_language_in_title_or_description": issue_language,
        "audit_priority_for_current_panel": priority,
        "page_modified_date": parse_modified_date(soup, page_text),
        "http_last_modified": response.headers.get("Last-Modified", ""),
        "fetched_at_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "snapshot_relative_path": str(snapshot.relative_to(ROOT)),
        "snapshot_sha256_project_generated": sha256_bytes(response.content),
    }


def crawl_user_notes() -> list[dict]:
    variable_frame = pd.read_csv(PANEL_VARIABLES)
    panel_variables = set(
        variable_frame.loc[variable_frame["column_origin"].eq("census_source"), "column_name"].astype(str)
    )
    links_by_year: dict[int, list[str]] = {}
    with ThreadPoolExecutor(max_workers=4) as pool:
        futures = {pool.submit(user_note_index, year): year for year in YEARS}
        for future in as_completed(futures):
            year, links = future.result()
            links_by_year[year] = links

    rows: list[dict] = []
    with ThreadPoolExecutor(max_workers=6) as pool:
        futures = {
            pool.submit(fetch_user_note, year, url, panel_variables): (year, url)
            for year in YEARS
            for url in links_by_year[year]
        }
        for number, future in enumerate(as_completed(futures), start=1):
            row = future.result()
            rows.append(row)
            if number % 20 == 0:
                log(f"USER NOTE DETAIL: {number}/{len(futures)}")
    rows.sort(key=lambda row: (row["file_year_page"], row["official_url"]))
    write_csv(USER_NOTE_INVENTORY, rows)
    return rows


def legacy_page(panel: int) -> tuple[dict, list[dict]]:
    url = f"https://www.census.gov/programs-surveys/sipp/data/datasets.{panel}.html"
    response = fetch(url)
    soup = BeautifulSoup(response.text, "html.parser")
    snapshot = SOURCE_ROOT / "legacy" / str(panel) / f"official_dataset_page_{AUDIT_DATE}.html"
    snapshot.parent.mkdir(parents=True, exist_ok=True)
    snapshot.write_bytes(response.content)
    detail_marker = f"/programs-surveys/sipp/data/datasets/{panel}-panel/"
    detail_urls = sorted(
        {
            urljoin(url, anchor.get("href", ""))
            for anchor in soup.select("a[href]")
            if detail_marker in urljoin(url, anchor.get("href", ""))
            and urlparse(urljoin(url, anchor.get("href", ""))).path.lower().endswith(".html")
        }
    )
    pages: list[tuple[str, BeautifulSoup, str]] = [(url, soup, str(snapshot.relative_to(ROOT)))]
    for detail_url in detail_urls:
        detail_response = fetch(detail_url)
        detail_slug = Path(urlparse(detail_url).path).name
        detail_snapshot = SOURCE_ROOT / "legacy" / str(panel) / "details" / detail_slug
        detail_snapshot.parent.mkdir(parents=True, exist_ok=True)
        detail_snapshot.write_bytes(detail_response.content)
        pages.append(
            (
                detail_url,
                BeautifulSoup(detail_response.text, "html.parser"),
                str(detail_snapshot.relative_to(ROOT)),
            )
        )

    links = []
    for source_page, source_soup, source_snapshot in pages:
      for anchor in source_soup.select("a[href]"):
        href = urljoin(source_page, anchor.get("href", ""))
        parsed = urlparse(href)
        if parsed.netloc not in {"www2.census.gov", "www.census.gov"}:
            continue
        if "/programs-surveys/sipp/" not in parsed.path:
            continue
        link_text = " ".join(anchor.get_text(" ", strip=True).split())
        lower = parsed.path.lower()
        is_payload = any(
            lower.endswith(ext)
            for ext in (
                ".zip",
                ".gz",
                ".csv",
                ".dat",
                ".dta",
                ".sas7bdat",
                ".txt",
                ".pdf",
                ".xls",
                ".xlsx",
            )
        )
        if is_payload:
            links.append(
                {
                    "panel_year": panel,
                    "link_text": link_text,
                    "official_url": href,
                    "file_extension": Path(parsed.path).suffix.lower(),
                    "likely_data_payload": lower.endswith((".zip", ".gz", ".csv", ".dat", ".dta", ".sas7bdat")),
                    "downloaded_locally_in_this_modern_archive": False,
                    "source_page": source_page,
                    "source_page_snapshot_relative_path": source_snapshot,
                }
            )
    unique = {row["official_url"]: row for row in links}
    links = sorted(unique.values(), key=lambda row: row["official_url"])
    title = soup.title.get_text(" ", strip=True) if soup.title else ""
    summary = {
        "panel_year": panel,
        "official_page": url,
        "http_status": response.status_code,
        "page_title": " ".join(title.split()),
        "wave_or_detail_pages": len(detail_urls),
        "official_payload_or_document_links": len(links),
        "likely_data_payload_links": sum(row["likely_data_payload"] for row in links),
        "raw_payloads_downloaded_locally": 0,
        "local_scope_status": "metadata_catalog_only_not_downloaded",
        "snapshot_relative_path": str(snapshot.relative_to(ROOT)),
        "snapshot_sha256_project_generated": sha256_bytes(response.content),
    }
    log(f"LEGACY {panel}: links={len(links)} likely_data={summary['likely_data_payload_links']}")
    return summary, links


def crawl_legacy_scope() -> tuple[list[dict], list[dict]]:
    summaries = []
    links = []
    with ThreadPoolExecutor(max_workers=4) as pool:
        futures = {pool.submit(legacy_page, panel): panel for panel in LEGACY_PANELS}
        for future in as_completed(futures):
            summary, page_links = future.result()
            summaries.append(summary)
            links.extend(page_links)
    summaries.sort(key=lambda row: row["panel_year"])
    links.sort(key=lambda row: (row["panel_year"], row["official_url"]))
    write_csv(LEGACY_SCOPE, summaries)
    write_csv(LEGACY_LINKS, links)
    return summaries, links


def build_issue_register(releases: list[dict], notes: list[dict]) -> list[dict]:
    bad_weight_files = []
    pattern = re.compile(r"where\([^\r\n]*TSSSAMT")
    for path in (ROOT / "script").rglob("*.py"):
        if pattern.search(path.read_text(encoding="utf-8", errors="replace")):
            bad_weight_files.append(str(path.relative_to(ROOT)))
    panel = pd.read_parquet(
        ROOT / "data" / "analysis_ready" / "sipp_2018_2025_person_month_panel.parquet",
        columns=["WPFINWGT", "TSSSAMT"],
    )
    weight = pd.to_numeric(panel["WPFINWGT"], errors="coerce")
    tssamt = pd.to_numeric(panel["TSSSAMT"], errors="coerce")
    nonpositive = weight.le(0)
    rows = [
        {
            "issue_id": "RAW_REMOTE_IDENTITY",
            "severity": "none",
            "layer": "raw_archive",
            "status": "pass",
            "finding": "All 50 canonical modern CSV ZIPs match the current official remote files byte for byte.",
            "affected_scope": "2018-2025 primary, annual replicate, longitudinal, longitudinal replicate",
            "required_action": "Retain manifests and rerun remote comparison after future Census updates.",
            "evidence": "data/sample_audits/sipp_remote_byte_comparison_20260716.csv",
        },
        {
            "issue_id": "PUBLIC_USE_V11_CORRECTION",
            "severity": "high",
            "layer": "official_release_version",
            "status": "mitigated_and_panel_verified",
            "finding": "Census replaced 2018-2021 public-use files with v1.1 on 2025-07-24 after correcting TSSSAMT and dependent income/poverty recodes.",
            "affected_scope": "2018-2021",
            "required_action": "Keep using the current raw archive; rerun the alignment check if Census changes these files again.",
            "evidence": "data/metadata/sipp_release_version_ledger_2018_2025.csv|data/sample_audits/sipp_v11_correction_panel_alignment.csv",
        },
        {
            "issue_id": "MONTHLY_HEALTH_INSURANCE_PROCESSING_ERROR",
            "severity": "high",
            "layer": "official_known_issue",
            "status": "mitigated_with_additive_patch",
            "finding": "Census documents begin/end-month processing errors affecting edited monthly Medicare, Medicaid, other-coverage, and downstream health-insurance recodes in the 2018-2023 files.",
            "affected_scope": "19625 unique affected person-month rows in the current selected panel; original official values remain unchanged",
            "required_action": "Use the additive correction patch for health-insurance analyses and retain the unmodified panel for provenance and sensitivity checks.",
            "evidence": "data/analysis_ready/sipp_2018_2023_health_insurance_official_usernote_correction_patch.parquet|data/sample_audits/sipp_health_insurance_usernote_correction_counts.csv",
        },
        {
            "issue_id": "HEALTH_NOTE_PRIVATE_RECODE_FORMULA_CONFLICT",
            "severity": "high",
            "layer": "official_documentation",
            "status": "open_documentation_inconsistency",
            "finding": "The Census web correction table prints EHEMPLY{1:2}=1 when rebuilding RPRIMTH, but the data dictionary defines EHEMPLY as a multi-category source code and the literal formula contradicts observed raw recodes and the note's stated affected-record scale.",
            "affected_scope": "RPRIMTH and downstream RHLTHMTH correction interpretation for 2018-2023",
            "required_action": "Use the documented begin/end logic with monthly plan indicators EPR1MTH/EPR2MTH, disclose the interpretation, and retain original-versus-corrected sensitivity results.",
            "evidence": "report/107_arpa400_raw_data_quality_sensitivity.md|data/sample_audits/sipp_health_insurance_usernote_correction_counts.csv",
        },
        {
            "issue_id": "TSSSAMT_FALSE_WEIGHT_FALLBACK",
            "severity": "critical",
            "layer": "analysis_code_not_raw_data",
            "status": "fixed_in_source_results_require_regeneration",
            "finding": "Thirty-five idea-screen scripts formerly used TSSSAMT, a Social Security income amount, as a fallback when WPFINWGT was nonpositive; all matching source instances were removed on 2026-07-16.",
            "affected_scope": f"{len(bad_weight_files)} scripts still match the invalid pattern; {int(nonpositive.sum())} panel rows have nonpositive WPFINWGT; {int((nonpositive & tssamt.gt(0)).sum())} would have received a positive false weight under the old code",
            "required_action": "Regenerate any historical idea-screen output used in a paper; nonpositive official weights are now missing and excluded by model masks.",
            "evidence": "script/01_ingest/10_arpa400_raw_data_quality_sensitivity.py|report/107_arpa400_raw_data_quality_sensitivity.md",
        },
        {
            "issue_id": "REPLICATE_VARIANCE_NOT_USED",
            "severity": "high",
            "layer": "analysis_variance",
            "status": "open",
            "finding": "Official guidance requires matching replicate weights for accurate standard errors and variances; screening regressions generally do not use Fay BRR replicates.",
            "affected_scope": "Existing model screens unless a script explicitly implements REPWGT1-REPWGT240",
            "required_action": "For final inference, implement the matching annual or longitudinal Fay BRR design and report sensitivity to clustering choices.",
            "evidence": "data/metadata/sipp_weight_product_use_ledger.csv",
        },
        {
            "issue_id": "ANNUAL_WEIGHT_MONTH_RESTRICTION",
            "severity": "high",
            "layer": "analysis_weight_selection",
            "status": "open_for_review",
            "finding": "Official annual estimates use WPFINWGT on MONTHCODE=12; monthly estimates use the target month, while multi-year estimates use FINYR2/3/4.",
            "affected_scope": "Any pooled person-month or annual estimate that treats all 12 monthly rows as independent annual observations",
            "required_action": "Define the estimand first, then select the official weight and row restriction from the weight ledger.",
            "evidence": "temp/source_metadata/census_sipp/common/Select_weights_2018_SIPP_JUN24.pdf",
        },
        {
            "issue_id": "2025_RESPONSE_AND_LONGITUDINAL_ATTRITION",
            "severity": "high",
            "layer": "sampling_and_nonresponse",
            "status": "official_weights_adjust_but_residual_risk_remains",
            "finding": "The 2025 source-and-accuracy statement reports a 42.63% cross-sectional weighted household response rate and declining longitudinal person response rates of 61.67%, 42.42%, and 25.75% for FINYR2, FINYR3, and FINYR4.",
            "affected_scope": "2025 cross-sectional estimates and especially 2-, 3-, and 4-year longitudinal cohorts",
            "required_action": "Use the official weights and replicate weights, report cohort attrition, and test whether conclusions change across longitudinal horizons and complete-case restrictions.",
            "evidence": "data/metadata/sipp_2025_response_and_attrition_summary.csv|temp/source_metadata/census_sipp/2025/SIPP-2025-SA.pdf",
        },
        {
            "issue_id": "LEGACY_ARCHIVE_NOT_LOCAL",
            "severity": "scope",
            "layer": "archive_completeness",
            "status": "explicitly_not_downloaded",
            "finding": "The local complete archive covers the 2018+ annual redesign products, not all 1984-2014 panel/wave raw payloads.",
            "affected_scope": "1984-1993, 1996, 2001, 2004, 2008, 2014 panel archives",
            "required_action": "Download legacy raw payloads only if the research question needs historical panel/wave data.",
            "evidence": "data/metadata/sipp_legacy_official_archive_scope.csv",
        },
        {
            "issue_id": "LANDING_PAGE_LAG",
            "severity": "medium",
            "layer": "official_navigation",
            "status": "confirmed",
            "finding": "Census navigation updates are asynchronous: the datasets landing page now lists 2025, while users-guide, source/accuracy, and complete-technical-documentation navigation still stop at 2024 even though direct 2025 technical files exist.",
            "affected_scope": "Source discovery and automated freshness checks",
            "required_action": "Audit direct www2.census.gov directories in addition to narrative landing pages.",
            "evidence": "data/metadata/sipp_live_official_channel_reaudit_20260716.csv",
        },
        {
            "issue_id": "USER_NOTES_REQUIRE_OUTCOME_REVIEW",
            "severity": "high",
            "layer": "official_known_issues",
            "status": "cataloged",
            "finding": "Official annual user-note pages contain processing, comparability, allocation, and data-quality warnings, including health-insurance and income issues relevant to the current panel.",
            "affected_scope": f"{len(notes)} user notes; {sum(row['audit_priority_for_current_panel'] == 'high' for row in notes)} automatically high-priority matches",
            "required_action": "Review all high-priority notes before locking each outcome/exposure definition.",
            "evidence": "data/metadata/sipp_official_user_notes_inventory_2018_2025.csv",
        },
        {
            "issue_id": "RMARKTPLACE_NOT_INSURANCE_TYPE",
            "severity": "high",
            "layer": "variable_interpretation",
            "status": "confirmed_scope_limit",
            "finding": "Census states that RMARKTPLACE does not identify insurance type; private, Medicaid, and other coverage may all be reported as Marketplace coverage.",
            "affected_scope": "Any analysis labeling RMARKTPLACE alone as nongroup private Marketplace enrollment",
            "required_action": "Treat RMARKTPLACE as a reporting-channel flag and combine it with plan/source variables before making insurance-type claims.",
            "evidence": "data/metadata/sipp_official_user_notes_inventory_2018_2025.csv",
        },
        {
            "issue_id": "NO_OFFICIAL_CRYPTO_CHECKSUMS",
            "severity": "medium",
            "layer": "provenance",
            "status": "mitigated",
            "finding": "Census directories do not publish a uniform cryptographic checksum for these products.",
            "affected_scope": "All archived products",
            "required_action": "Keep project-generated SHA-256 plus periodic live byte comparison; do not label local hashes as Census-issued.",
            "evidence": "data/metadata/sipp_raw_download_manifest_2018_2025.csv",
        },
        {
            "issue_id": "ANALYSIS_PANEL_IS_SELECTED_EXTRACT",
            "severity": "scope",
            "layer": "derived_data",
            "status": "confirmed",
            "finding": "The analysis-ready panel contains 90 official source fields plus 7 technical fields, not all roughly 5,000 columns in each annual primary file.",
            "affected_scope": "sipp_2018_2025_person_month_panel.parquet",
            "required_action": "Use raw primary ZIPs or build a new selected extract when a variable is absent; do not call the 97-column panel a full-column raw copy.",
            "evidence": "data/metadata/sipp_2018_2025_panel_variable_inventory.csv",
        },
        {
            "issue_id": "OFFICIAL_2021_FINYR4_LABEL_ANOMALY",
            "severity": "medium",
            "layer": "official_longitudinal_metadata",
            "status": "preserved_and_flagged",
            "finding": "The official 2021 four-year longitudinal metadata has an internal period-label inconsistency; raw values were not altered.",
            "affected_scope": "2021 FINYR4 / matching longitudinal replicate metadata",
            "required_action": "Use the verified file-year/horizon mapping and retain the anomaly flag.",
            "evidence": "data/metadata/sipp_longitudinal_product_audit_2019_2025.csv",
        },
    ]
    write_csv(ISSUE_REGISTER, rows)
    return rows


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--legacy-only",
        action="store_true",
        help="Refresh only the recursive legacy panel/wave metadata catalog.",
    )
    parser.add_argument(
        "--latest-docs-only",
        action="store_true",
        help="Archive the latest users guide and source/accuracy statement only.",
    )
    parser.add_argument(
        "--issues-only",
        action="store_true",
        help="Rebuild only the raw-data and weight issue register from local audited inputs.",
    )
    args = parser.parse_args()
    if not PANEL_VARIABLES.exists():
        raise FileNotFoundError(PANEL_VARIABLES)
    if args.legacy_only:
        legacy, legacy_links = crawl_legacy_scope()
        log(
            f"LEGACY AUDIT COMPLETE panels={len(legacy)} links={len(legacy_links)}"
        )
        return
    if args.latest_docs_only:
        provenance = (
            pd.read_csv(DOCUMENT_PROVENANCE).fillna("").to_dict("records")
            if DOCUMENT_PROVENANCE.exists()
            else []
        )
        provenance = [
            row
            for row in provenance
            if row.get("document_role")
            not in {item[0] for item in LATEST_CORE_DOCUMENTS}
        ]
        archive_latest_core_documents(provenance)
        write_csv(DOCUMENT_PROVENANCE, provenance)
        return
    if args.issues_only:
        releases = pd.read_csv(RELEASE_LEDGER).fillna("").to_dict("records")
        notes = pd.read_csv(USER_NOTE_INVENTORY).fillna("").to_dict("records")
        issues = build_issue_register(releases, notes)
        log(f"ISSUE REGISTER COMPLETE issues={len(issues)}")
        return
    tech = crawl_technical_catalog()
    releases, provenance = build_release_ledger(tech)
    weight_text = archive_weight_guide(provenance)
    archive_latest_core_documents(provenance)
    build_weight_ledger(weight_text)
    write_csv(DOCUMENT_PROVENANCE, provenance)
    notes = crawl_user_notes()
    legacy, legacy_links = crawl_legacy_scope()
    issues = build_issue_register(releases, notes)
    log(
        "DOCUMENT AUDIT COMPLETE "
        f"tech_files={len(tech)} releases={len(releases)} user_notes={len(notes)} "
        f"legacy_panels={len(legacy)} legacy_links={len(legacy_links)} issues={len(issues)}"
    )


if __name__ == "__main__":
    main()
