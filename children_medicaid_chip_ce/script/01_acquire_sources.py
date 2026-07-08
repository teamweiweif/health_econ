from __future__ import annotations

import json
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

import pandas as pd
import requests

from project_utils import (
    RAW,
    SNAP,
    TEMP,
    add_or_update_inventory,
    append_audit,
    csv_shape,
    download,
    ensure_dirs,
    sha256_file,
    source_row,
    write_json,
)


DATASETS = {
    "cms_pi_enrollment": {
        "metadata_id": "6165f45b-ca93-5bb5-9d06-db29c692a360",
        "period": "2013-09 through latest release month",
        "unit": "state-month-report-version",
    },
    "cms_eligibility_processing_renewal": {
        "metadata_id": "5abea2e0-3f8e-4b49-a50d-d63d5fd9103c",
        "period": "2023-03 through latest release month",
        "unit": "state-month-report-version",
    },
    "cms_updated_renewal_outcomes": {
        "metadata_id": "e6205a51-e6d7-4849-9882-4483b8a28c41",
        "period": "2024 updated releases plus monthly files",
        "unit": "state-month-metric",
    },
}

STATIC_DOWNLOADS = {
    "cms_sho_23_004": "https://www.medicaid.gov/federal-policy-guidance/downloads/sho23004.pdf",
    "cms_faq_102723_child_ce_premium_nonpayment": "https://www.medicaid.gov/federal-policy-guidance/downloads/faq102723.pdf",
    "kff_table5_child_ce_jan2023": "https://files.kff.org/attachment/Table-5-Medicaid-and-CHIP-Eligibility-Enrollment-and-Renewal-Policies-as-States-Prepare-for-the-Unwinding-of-the-Pandemic-Era-Continuous-Enrollment-Provision.pdf",
}

PAGE_SNAPSHOTS = {
    "cms_continuous_eligibility_page": "https://www.medicaid.gov/medicaid/enrollment-strategies/continuous-eligibility-medicaid-and-chip-coverage",
    "cms_enrollment_data_page": "https://www.medicaid.gov/medicaid/national-medicaid-chip-program-information/medicaid-chip-enrollment-data",
    "cms_snapshot_page": "https://www.medicaid.gov/medicaid-and-chip-eligibility-operations-and-enrollment-snapshot",
    "census_acs_hi_page": "https://www.census.gov/data/tables/time-series/demo/health-insurance/acs-hi.html",
}

ACS_YEARS = [2018, 2019, 2021, 2022, 2023, 2024]


def fetch_text(url: str, path: Path) -> tuple[str, str]:
    status, checksum = download(url, path)
    return status, checksum


def get_dataset_metadata(name: str, metadata_id: str) -> tuple[dict, list[dict]]:
    meta_url = f"https://data.medicaid.gov/api/1/metastore/schemas/dataset/items/{metadata_id}"
    meta = requests.get(meta_url, timeout=60).json()
    write_json(SNAP / f"{name}_metadata.json", meta)
    distributions = meta.get("distribution", [])
    if isinstance(distributions, dict):
        distributions = [distributions]
    rows = [
        source_row(
            f"{name}_metadata",
            meta_url,
            SNAP / f"{name}_metadata.json",
            unit="dataset metadata",
            checksum=sha256_file(SNAP / f"{name}_metadata.json"),
            notes=meta.get("title", ""),
        )
    ]
    for i, dist in enumerate(distributions):
        dict_url = dist.get("describedBy")
        if dict_url:
            dd = requests.get(dict_url, timeout=60).json()
            dd_path = SNAP / f"{name}_data_dictionary_{i}.json"
            write_json(dd_path, dd)
            fields = dd.get("data", {}).get("fields", [])
            rows.append(
                source_row(
                    f"{name}_data_dictionary_{i}",
                    dict_url,
                    dd_path,
                    unit="data dictionary",
                    row_count=len(fields),
                    column_count=5,
                    checksum=sha256_file(dd_path),
                    notes=dist.get("format", ""),
                )
            )
    return meta, rows


def download_distribution(name: str, meta: dict, period: str, unit: str) -> list[dict]:
    distributions = meta.get("distribution", [])
    if isinstance(distributions, dict):
        distributions = [distributions]
    rows = []
    for dist in distributions:
        url = dist.get("downloadURL")
        fmt = (dist.get("format") or "").lower()
        if not url or fmt != "csv":
            continue
        filename = Path(url.split("?")[0]).name
        dest = RAW / filename
        status, checksum = download(url, dest)
        try:
            nrow, ncol = csv_shape(dest)
        except Exception as exc:
            nrow, ncol = "", ""
            status = f"{status}; shape_failed"
            append_audit(f"shape failed for {dest}: {exc}")
        rows.append(
            source_row(
                name,
                url,
                dest,
                period_covered=period,
                unit=unit,
                row_count=nrow,
                column_count=ncol,
                checksum=checksum,
                status=status,
                notes=meta.get("title", ""),
            )
        )
    return rows


def download_acs() -> list[dict]:
    rows = []
    for year in ACS_YEARS:
        release_folder = year + 1
        attempts = ["xlsx", "xls"] if year == 2018 else ["xlsx"]
        errors = []
        for ext in attempts:
            url = f"https://www2.census.gov/programs-surveys/demo/tables/health-insurance/{release_folder}/acs-hi/hi05_acs.{ext}"
            dest = RAW / f"census_hi05_acs_{year}.{ext}"
            try:
                status, checksum = download(url, dest)
                notes = "ACS HI-05 table; no 2020 ACS 1-year release."
                if ext == "xls":
                    notes += " Legacy XLS source is recorded but not parsed by the lightweight XLSX parser."
                rows.append(
                    source_row(
                        f"census_hi05_acs_{year}",
                        url,
                        dest,
                        period_covered=str(year),
                        unit="state-age-year table",
                        checksum=checksum,
                        status=status,
                        notes=notes,
                    )
                )
                break
            except Exception as exc:
                errors.append(f"{ext}: {exc}")
        else:
            append_audit(f"ACS HI05 download failed for {year}: {' | '.join(errors)}")
            rows.append(
                source_row(
                    f"census_hi05_acs_{year}",
                    f"https://www2.census.gov/programs-surveys/demo/tables/health-insurance/{release_folder}/acs-hi/hi05_acs.xlsx",
                    RAW / f"census_hi05_acs_{year}.xlsx",
                    period_covered=str(year),
                    unit="state-age-year table",
                    status="failed",
                    notes=" | ".join(errors),
                )
            )
    return rows


def census_api_probe() -> list[dict]:
    rows = []
    probe_url = "https://api.census.gov/data/2024/acs/acs1?get=NAME,B27001_001E&for=state:*"
    dest = SNAP / "census_api_probe_2024_acs1.html"
    try:
        status, checksum = download(probe_url, dest, overwrite=True)
        text = dest.read_text(errors="ignore")
        status_note = "ok" if text.lstrip().startswith("[") else "blocked_or_key_required"
        rows.append(
            source_row(
                "census_acs_api_probe_2024",
                probe_url,
                dest,
                period_covered="2024",
                unit="API probe",
                checksum=checksum,
                status=status_note,
                notes="API returned Missing Key in this environment; ACS validation uses public XLSX tables instead.",
            )
        )
    except Exception as exc:
        rows.append(
            source_row(
                "census_acs_api_probe_2024",
                probe_url,
                dest,
                period_covered="2024",
                unit="API probe",
                status="failed",
                notes=str(exc),
            )
        )
    return rows


def main() -> None:
    ensure_dirs()
    inventory_rows = []

    for name, spec in DATASETS.items():
        meta, rows = get_dataset_metadata(name, spec["metadata_id"])
        inventory_rows.extend(rows)
        inventory_rows.extend(download_distribution(name, meta, spec["period"], spec["unit"]))

    for name, url in STATIC_DOWNLOADS.items():
        suffix = Path(url.split("?")[0]).suffix or ".bin"
        dest = RAW / f"{name}{suffix}"
        try:
            status, checksum = download(url, dest)
            inventory_rows.append(
                source_row(
                    name,
                    url,
                    dest,
                    unit="policy document",
                    checksum=checksum,
                    status=status,
                )
            )
        except Exception as exc:
            append_audit(f"static download failed for {name}: {exc}")
            inventory_rows.append(source_row(name, url, dest, status="failed", notes=str(exc)))

    for name, url in PAGE_SNAPSHOTS.items():
        dest = SNAP / f"{name}.html"
        try:
            status, checksum = fetch_text(url, dest)
            inventory_rows.append(
                source_row(
                    name,
                    url,
                    dest,
                    unit="web page snapshot",
                    checksum=checksum,
                    status=status,
                )
            )
        except Exception as exc:
            append_audit(f"page snapshot failed for {name}: {exc}")
            inventory_rows.append(source_row(name, url, dest, status="failed", notes=str(exc)))

    inventory_rows.extend(download_acs())
    inventory_rows.extend(census_api_probe())
    add_or_update_inventory(inventory_rows)
    append_audit("source acquisition completed")
    print(f"acquired/recorded {len(inventory_rows)} source rows")


if __name__ == "__main__":
    main()
