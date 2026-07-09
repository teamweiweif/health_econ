from __future__ import annotations

import csv
import hashlib
import json
import os
import re
import sys
from datetime import date
from pathlib import Path
from typing import Any
from urllib.request import Request, urlopen
from zipfile import ZipFile
from xml.etree import ElementTree as ET

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
SCRIPT = ROOT / "script"
RESULT = ROOT / "result"
REPORT = ROOT / "report"
TEMP = ROOT / "temp"
RAW = TEMP / "raw_downloads"
SNAP = TEMP / "source_snapshots"
LOGS = TEMP / "logs"

SOURCE_INVENTORY = TEMP / "source_inventory.csv"
ACCESS_DATE = date.today().isoformat()

STATE_ABBR_TO_FIPS = {
    "AL": "01",
    "AK": "02",
    "AZ": "04",
    "AR": "05",
    "CA": "06",
    "CO": "08",
    "CT": "09",
    "DE": "10",
    "DC": "11",
    "FL": "12",
    "GA": "13",
    "HI": "15",
    "ID": "16",
    "IL": "17",
    "IN": "18",
    "IA": "19",
    "KS": "20",
    "KY": "21",
    "LA": "22",
    "ME": "23",
    "MD": "24",
    "MA": "25",
    "MI": "26",
    "MN": "27",
    "MS": "28",
    "MO": "29",
    "MT": "30",
    "NE": "31",
    "NV": "32",
    "NH": "33",
    "NJ": "34",
    "NM": "35",
    "NY": "36",
    "NC": "37",
    "ND": "38",
    "OH": "39",
    "OK": "40",
    "OR": "41",
    "PA": "42",
    "RI": "44",
    "SC": "45",
    "SD": "46",
    "TN": "47",
    "TX": "48",
    "UT": "49",
    "VT": "50",
    "VA": "51",
    "WA": "53",
    "WV": "54",
    "WI": "55",
    "WY": "56",
}

STATE_NAME_TO_ABBR = {
    "Alabama": "AL",
    "Alaska": "AK",
    "Arizona": "AZ",
    "Arkansas": "AR",
    "California": "CA",
    "Colorado": "CO",
    "Connecticut": "CT",
    "Delaware": "DE",
    "District of Columbia": "DC",
    "Florida": "FL",
    "Georgia": "GA",
    "Hawaii": "HI",
    "Idaho": "ID",
    "Illinois": "IL",
    "Indiana": "IN",
    "Iowa": "IA",
    "Kansas": "KS",
    "Kentucky": "KY",
    "Louisiana": "LA",
    "Maine": "ME",
    "Maryland": "MD",
    "Massachusetts": "MA",
    "Michigan": "MI",
    "Minnesota": "MN",
    "Mississippi": "MS",
    "Missouri": "MO",
    "Montana": "MT",
    "Nebraska": "NE",
    "Nevada": "NV",
    "New Hampshire": "NH",
    "New Jersey": "NJ",
    "New Mexico": "NM",
    "New York": "NY",
    "North Carolina": "NC",
    "North Dakota": "ND",
    "Ohio": "OH",
    "Oklahoma": "OK",
    "Oregon": "OR",
    "Pennsylvania": "PA",
    "Rhode Island": "RI",
    "South Carolina": "SC",
    "South Dakota": "SD",
    "Tennessee": "TN",
    "Texas": "TX",
    "Utah": "UT",
    "Vermont": "VT",
    "Virginia": "VA",
    "Washington": "WA",
    "West Virginia": "WV",
    "Wisconsin": "WI",
    "Wyoming": "WY",
}


def ensure_dirs() -> None:
    for path in (DATA, SCRIPT, RESULT, REPORT, TEMP, RAW, SNAP, LOGS):
        path.mkdir(parents=True, exist_ok=True)


def log(message: str) -> None:
    print(message, flush=True)


def append_audit(message: str) -> None:
    ensure_dirs()
    with (TEMP / "audit_log.md").open("a", encoding="utf-8") as fh:
        fh.write(f"- {ACCESS_DATE}: {message}\n")


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def download(url: str, dest: Path, overwrite: bool = False) -> tuple[str, str]:
    ensure_dirs()
    dest.parent.mkdir(parents=True, exist_ok=True)
    if dest.exists() and dest.stat().st_size > 0 and not overwrite:
        return "exists", sha256_file(dest)
    req = Request(url, headers={"User-Agent": "Mozilla/5.0 reproducible-research-bot"})
    with urlopen(req, timeout=120) as resp, dest.open("wb") as out:
        while True:
            chunk = resp.read(1024 * 1024)
            if not chunk:
                break
            out.write(chunk)
    return "downloaded", sha256_file(dest)


def write_json(path: Path, obj: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, indent=2, sort_keys=True), encoding="utf-8")


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def clean_col(name: str) -> str:
    name = name.strip().lower()
    name = re.sub(r"[^a-z0-9]+", "_", name)
    return re.sub(r"_+", "_", name).strip("_")


def month_from_reporting_period(value: Any) -> pd.Timestamp:
    s = str(int(value))
    return pd.Timestamp(year=int(s[:4]), month=int(s[4:6]), day=1)


def safe_div(num: pd.Series, den: pd.Series) -> pd.Series:
    return num.where(den != 0) / den.where(den != 0)


def source_row(
    source_name: str,
    official_public_source: str,
    download_path: Path | str,
    period_covered: str = "",
    unit: str = "",
    row_count: int | str = "",
    column_count: int | str = "",
    checksum: str = "",
    status: str = "ok",
    notes: str = "",
) -> dict[str, Any]:
    rel_path = ""
    if download_path:
        p = Path(download_path)
        try:
            rel_path = str(p.relative_to(ROOT))
        except ValueError:
            rel_path = str(p)
    return {
        "source_name": source_name,
        "official_public_source": official_public_source,
        "access_date": ACCESS_DATE,
        "download_path": rel_path,
        "period_covered": period_covered,
        "unit": unit,
        "row_count": row_count,
        "column_count": column_count,
        "checksum": checksum,
        "status": status,
        "notes": notes,
    }


def write_source_inventory(rows: list[dict[str, Any]]) -> None:
    ensure_dirs()
    cols = [
        "source_name",
        "official_public_source",
        "access_date",
        "download_path",
        "period_covered",
        "unit",
        "row_count",
        "column_count",
        "checksum",
        "status",
        "notes",
    ]
    with SOURCE_INVENTORY.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=cols)
        writer.writeheader()
        for row in rows:
            writer.writerow({col: row.get(col, "") for col in cols})


def add_or_update_inventory(new_rows: list[dict[str, Any]]) -> None:
    rows: list[dict[str, Any]] = []
    if SOURCE_INVENTORY.exists():
        rows = list(csv.DictReader(SOURCE_INVENTORY.open(encoding="utf-8")))
    by_name = {r["source_name"]: r for r in rows}
    for row in new_rows:
        by_name[row["source_name"]] = row
    write_source_inventory(list(by_name.values()))


def csv_shape(path: Path) -> tuple[int, int]:
    rows = 0
    cols = 0
    for chunk in pd.read_csv(path, chunksize=100_000):
        rows += len(chunk)
        cols = len(chunk.columns)
    return rows, cols


def parse_xlsx_first_sheet(path: Path) -> list[dict[str, str]]:
    ns = {"a": "http://schemas.openxmlformats.org/spreadsheetml/2006/main"}
    with ZipFile(path) as zf:
        shared: list[str] = []
        if "xl/sharedStrings.xml" in zf.namelist():
            root = ET.fromstring(zf.read("xl/sharedStrings.xml"))
            for si in root.findall("a:si", ns):
                texts = [
                    t.text or ""
                    for t in si.iter(
                        "{http://schemas.openxmlformats.org/spreadsheetml/2006/main}t"
                    )
                ]
                shared.append("".join(texts))
        sheet_name = "xl/worksheets/sheet1.xml"
        root = ET.fromstring(zf.read(sheet_name))
        out: list[dict[str, str]] = []
        for row in root.findall(".//a:row", ns):
            vals: dict[str, str] = {}
            for cell in row.findall("a:c", ns):
                ref = cell.attrib.get("r", "")
                m = re.match(r"[A-Z]+", ref)
                if not m:
                    continue
                col = m.group(0)
                v = cell.find("a:v", ns)
                if v is None or v.text is None:
                    val = ""
                elif cell.attrib.get("t") == "s":
                    val = shared[int(v.text)]
                else:
                    val = v.text
                vals[col] = val
            out.append(vals)
        return out


def to_number(x: Any) -> float | None:
    if x in ("", None, "N", "Z", "-"):
        return None
    try:
        return float(str(x).replace(",", ""))
    except ValueError:
        return None


def save_parquet(df: pd.DataFrame, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    df.to_parquet(path, index=False)


def package_versions() -> dict[str, str]:
    versions = {"python": sys.version.split()[0]}
    for pkg in ("pandas", "pyarrow", "matplotlib", "requests", "pypdf"):
        try:
            mod = __import__(pkg)
            versions[pkg] = getattr(mod, "__version__", "installed")
        except Exception:
            versions[pkg] = "missing"
    return versions
