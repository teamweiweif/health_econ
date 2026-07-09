from __future__ import annotations

import csv
import hashlib
import json
import re
import shutil
import subprocess
import tarfile
import unicodedata
import zipfile
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup

from common import REPORT_DIR, RESULT_DIR, TEMP_DIR, append_log, compact_text, ensure_dirs, sha256_file, write_csv


USER_AGENT = "Codex climate_uhc_ml schema audit"
DATA_DICTIONARY_URL = "https://microdata.worldbank.org/catalog/{catalog_id}/data-dictionary"


SCHEMA_FILE_COLUMNS = [
    "country",
    "survey_name",
    "wave",
    "idno",
    "catalog_id",
    "fid",
    "file_name",
    "file_description",
    "cases",
    "variable_count",
    "unit_guess",
    "module_guess",
    "source_url",
    "status",
]

VARIABLE_CATALOG_COLUMNS = [
    "country",
    "survey_name",
    "wave",
    "idno",
    "catalog_id",
    "fid",
    "file_name",
    "file_description",
    "variable_name",
    "variable_label",
    "concept_hits",
    "source",
]

STUDY_INVENTORY_COLUMNS = [
    "country",
    "survey_name",
    "wave",
    "idno",
    "catalog_id",
    "access_type",
    "analysis_unit",
    "geographic_coverage",
    "fieldwork_dates",
    "study_kind",
    "file_count",
    "variable_count_api",
    "variable_count_catalog",
    "metadata_json",
    "variables_json",
    "data_dictionary_html",
    "status",
]

MAP_COLUMNS = [
    "country",
    "survey_name",
    "wave",
    "idno",
    "file",
    "raw_variable",
    "raw_label",
    "harmonized_variable",
    "unit",
    "recall_period",
    "construction_rule",
    "quality_flag",
    "notes",
]

DESIGN_COLUMNS = [
    "design_id",
    "country_scope",
    "outcome",
    "exposure",
    "data_coverage",
    "outcome_validity",
    "exposure_precision",
    "sample_size",
    "event_rate",
    "climate_geography_linkage_quality",
    "identifying_variation",
    "pre-trend/placebo credibility",
    "model_stability",
    "policy_relevance",
    "ML usefulness",
    "journal potential",
    "go/no-go",
    "reason",
]

RAW_FILE_COLUMNS = [
    "source_path",
    "extracted_from",
    "file_format",
    "file_size_bytes",
    "sha256",
    "row_count",
    "column_count",
    "status",
    "error",
]

RAW_VARIABLE_COLUMNS = [
    "source_path",
    "extracted_from",
    "file_format",
    "variable_name",
    "variable_label",
    "dtype",
    "concept_hits",
    "status",
]


CONCEPT_PATTERNS: dict[str, list[str]] = {
    "household_id": [r"\bhhid\b", "household id", "household identification", "identifiant menage", "id menage"],
    "person_id": [r"\bpid\b", "person id", "individual id", "member id", "line number", "person code"],
    "weights": ["weight", "poids", "ponderation", "sampling weight", "hhweight", "expansion factor"],
    "strata": ["strata", "stratum", "strate"],
    "psu_cluster": [r"\bpsu\b", "cluster", "grappe", "enumeration area", r"\bea\b", "zone de denombrement"],
    "interview_date": ["interview date", "date of interview", "month of interview", "interview month", "survey month", "fieldwork"],
    "admin_geography": ["region", "district", "province", "admin", "county", "commune", "ward", "state", "lga", "department"],
    "gps": ["latitude", "longitude", "gps", "coordinate", "coord", "geocode", "geo data"],
    "rural_urban": ["rural", "urban", "milieu", "area of residence", "residence area"],
    "household_size": ["household size", "hh size", "number of household members", "taille du menage"],
    "age": [r"\bage\b", "years old", "date of birth"],
    "sex": [r"\bsex\b", "gender", "male", "female"],
    "head": ["household head", "head of household", "chef de menage"],
    "education": ["education", "schooling", "literacy", "highest grade", "educ"],
    "assets_wealth": ["asset", "wealth", "dwelling", "roof", "floor", "electricity", "durable"],
    "total_consumption_income": ["consumption aggregate", "total consumption", "consumption expenditure", "expenditure aggregate", "income aggregate", "total income", "welfare aggregate", "depense totale", "consommation totale"],
    "food_consumption": ["food consumption", "food expenditure", "alimentaire", "food exp"],
    "nonfood_consumption": ["non-food", "nonfood", "non food", "nonalimentaire"],
    "oop_health_expenditure": ["health expenditure", "medical expenditure", "out-of-pocket", "out of pocket", r"\boop\b", "depense de sante", "health spending", "medical cost", "hospital cost", "medicine cost"],
    "health_insurance": ["health insurance", "medical insurance", "assurance maladie", "covered by insurance", "couvert.*assurance", "mutuelle"],
    "illness_need": ["illness", "injury", "sick", "symptom", "maladie", "blessure", "health problem"],
    "care_sought": ["sought care", "seek care", "consultation", "visited health", "health facility", "treatment", "utilization", "soins"],
    "reason_not_sought": ["reason for not", "why did.*not", "not seek", "did not seek", "no treatment", "not consult", "not go", "renonc"],
    "cost_barrier": ["too expensive", "cost too much", "could not afford", "cannot afford", "no money", "lack of money", "financial reason", "reason.*cost", "trop cher", "faute.*argent"],
    "distance_barrier": ["distance", "transport", "too far", "travel"],
    "supply_barrier": ["drug unavailable", "medicine unavailable", "staff absent", "no doctor", "closed", "provider unavailable", "facility closed"],
    "health_facility_distance": ["distance to health", "nearest health", "health facility distance"],
    "shock_module": ["shock", "drought", "flood", "rain", "rainfall", "climate", "weather", "heat", "crop loss", "natural disaster"],
    "coping_borrowed": ["borrow", "loan", "credit"],
    "coping_sold_assets": ["sold asset", "sell asset", "sale of asset"],
    "food_insecurity": ["food insecurity", "hunger", "fies", "reduced meals", "food security"],
    "agriculture_livelihood": ["agriculture", "crop", "livestock", "farm", "plot", "harvest", "agric"],
}


CONCEPT_TO_MAP = {
    "household_id": ("survey_design", "hhid"),
    "person_id": ("survey_design", "pid"),
    "weights": ("survey_design", "household_weight_or_person_weight"),
    "strata": ("survey_design", "strata"),
    "psu_cluster": ("survey_design", "psu_or_cluster_id"),
    "interview_date": ("survey_design", "interview_date_or_survey_month"),
    "admin_geography": ("geography", "admin1_or_admin2"),
    "gps": ("geography", "latitude_or_longitude"),
    "rural_urban": ("geography", "rural"),
    "household_size": ("demographics", "household_size"),
    "age": ("demographics", "age"),
    "sex": ("demographics", "sex"),
    "head": ("demographics", "household_head_marker"),
    "education": ("demographics", "education"),
    "assets_wealth": ("demographics", "asset_index_or_asset_variable"),
    "total_consumption_income": ("consumption", "total_consumption_or_income"),
    "food_consumption": ("consumption", "food_consumption"),
    "nonfood_consumption": ("consumption", "nonfood_consumption"),
    "oop_health_expenditure": ("health_expenditure", "oop_health_expenditure"),
    "health_insurance": ("health_expenditure", "health_insurance"),
    "illness_need": ("health_need_access", "illness_or_injury_need"),
    "care_sought": ("health_need_access", "care_sought"),
    "reason_not_sought": ("health_need_access", "care_not_sought_reason"),
    "cost_barrier": ("health_need_access", "reason_not_sought_cost"),
    "distance_barrier": ("health_need_access", "reason_not_sought_distance"),
    "supply_barrier": ("health_need_access", "reason_not_sought_supply"),
    "health_facility_distance": ("health_need_access", "health_facility_distance"),
    "shock_module": ("shocks", "shock_module_variable"),
    "coping_borrowed": ("shocks", "coping_borrowed"),
    "coping_sold_assets": ("shocks", "coping_sold_assets"),
    "food_insecurity": ("shocks", "food_insecurity"),
    "agriculture_livelihood": ("shocks", "agriculture_livelihood"),
}


HEALTH_CONTEXT_PATTERNS = [
    "health",
    "medical",
    "hospital",
    "medicine",
    "doctor",
    "consult",
    "treatment",
    "pharm",
    "drug",
    "clinic",
    "soins",
    "sant",
    "maladie",
    "blessure",
]

PAYMENT_PATTERNS = [
    "amount paid",
    "paid for",
    "payment",
    "health expenditure",
    "medical expenditure",
    "monthly health expenditure",
    "cost of",
    "costs associated",
    "consultation fee",
    "fee",
    "spent",
    "expense",
    "expenditure",
    "combien avez-vous pay",
    "depense",
]


MAP_FILENAMES = {
    "consumption": "variable_map_consumption.csv",
    "health_expenditure": "variable_map_health_expenditure.csv",
    "health_need_access": "variable_map_health_need_access.csv",
    "geography": "variable_map_geography.csv",
    "survey_design": "variable_map_survey_design.csv",
    "demographics": "variable_map_demographics.csv",
    "shocks": "variable_map_shocks.csv",
}

RAW_SUPPORTED_EXTENSIONS = {
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
    ".parquet",
    ".feather",
}

ARCHIVE_EXTENSIONS = {".zip", ".tar", ".gz", ".tgz", ".7z", ".rar"}


def safe_name(text: str) -> str:
    text = re.sub(r"[^A-Za-z0-9._-]+", "_", text).strip("_")
    return text[:120] or "unnamed"


def normalize_match_text(text: str) -> str:
    normalized = unicodedata.normalize("NFKD", text)
    return normalized.encode("ascii", "ignore").decode("ascii").lower()


def read_csv_dicts(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        return []
    with path.open(encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def find_file(study_dir: Path, suffix: str) -> Path | None:
    matches = sorted(study_dir.glob(f"*{suffix}"))
    return matches[0] if matches else None


def match_idno(study_dir: Path, screen_by_idno: dict[str, dict[str, str]]) -> str:
    candidates = []
    for idno in screen_by_idno:
        idno_variants = {idno, safe_name(idno)}
        if any(variant and variant in study_dir.name for variant in idno_variants):
            candidates.append(idno)
    if candidates:
        return max(candidates, key=len)
    return ""


def fetch_data_dictionary(catalog_id: str, output: Path) -> tuple[Path | None, str]:
    if output.exists() and output.stat().st_size > 0:
        return output, "already exists"
    url = DATA_DICTIONARY_URL.format(catalog_id=catalog_id)
    try:
        response = requests.get(url, headers={"User-Agent": USER_AGENT}, timeout=90)
        response.raise_for_status()
        output.write_text(response.text, encoding="utf-8")
        return output, "downloaded"
    except Exception as exc:
        append_log(TEMP_DIR / "audit_log.md", f"Data dictionary fetch failed for catalog {catalog_id}: {exc}")
        return None, f"failed: {exc}"


def parse_data_dictionary(html_path: Path | None, catalog_id: str) -> dict[str, dict[str, str]]:
    if not html_path or not html_path.exists():
        return {}
    soup = BeautifulSoup(html_path.read_text(encoding="utf-8", errors="replace"), "html.parser")
    file_map: dict[str, dict[str, str]] = {}
    tables = soup.find_all("table")
    if not tables:
        return file_map
    for tr in tables[0].find_all("tr")[1:]:
        cells = tr.find_all(["td", "th"])
        if len(cells) < 3:
            continue
        link = cells[0].find("a", href=True)
        href = urljoin(DATA_DICTIONARY_URL.format(catalog_id=catalog_id), link["href"]) if link else ""
        fid_match = re.search(r"/data-dictionary/(F\d+)", href)
        fid = fid_match.group(1) if fid_match else ""
        file_name = link.get_text(" ", strip=True) if link else cells[0].get_text(" ", strip=True).split()[0]
        full_text = cells[0].get_text(" ", strip=True)
        desc = full_text[len(file_name):].strip() if full_text.startswith(file_name) else full_text
        file_map[fid] = {
            "fid": fid,
            "file_name": file_name,
            "file_description": desc,
            "cases": cells[1].get_text(" ", strip=True),
            "variable_count": cells[2].get_text(" ", strip=True),
            "source_url": href,
        }
    return file_map


def concept_hits(variable_name: str, label: str, file_name: str, file_description: str) -> list[str]:
    # Match concepts on variable names/labels only. File descriptions are too
    # broad and can otherwise mark every variable in a health or shock module.
    text = normalize_match_text(f"{variable_name} {label}")
    file_context = normalize_match_text(f"{file_name} {file_description}")
    hits = []
    for concept, patterns in CONCEPT_PATTERNS.items():
        for pattern in patterns:
            if pattern.startswith("\\") or any(token in pattern for token in ["\\b", ".*", "[", "]", "(", ")", "|", "^", "$"]):
                if re.search(pattern, text, flags=re.IGNORECASE):
                    hits.append(concept)
                    break
            elif pattern.lower() in text:
                hits.append(concept)
                break
    has_health_context = any(p in text or p in file_context for p in HEALTH_CONTEXT_PATTERNS)
    has_payment = any(p in text for p in PAYMENT_PATTERNS)
    if has_health_context and has_payment and "oop_health_expenditure" not in hits:
        hits.append("oop_health_expenditure")
    return hits


def unit_guess(file_name: str, file_description: str) -> str:
    text = normalize_match_text(f"{file_name} {file_description}")
    if any(x in text for x in ["household", "menage", "ménage", "hh"]):
        return "household"
    if any(x in text for x in ["individual", "person", "roster", "member", "individ"]):
        return "person"
    if any(x in text for x in ["community", "ea", "enumeration"]):
        return "community/geography"
    if any(x in text for x in ["plot", "crop", "livestock", "agric"]):
        return "agriculture/plot"
    return "unknown"


def module_guess(file_name: str, file_description: str) -> str:
    text = normalize_match_text(f"{file_name} {file_description}")
    if "health" in text or "sant" in text:
        return "health"
    if "consumption" in text or "expenditure" in text or "pov" in text or "welfare" in text:
        return "consumption/welfare"
    if "shock" in text:
        return "shocks"
    if "geography" in text or "gps" in text or "ea" in text:
        return "geography"
    if "agric" in text or "plot" in text or "crop" in text:
        return "agriculture"
    if "roster" in text or "individual" in text:
        return "demographics/roster"
    return "other"


def parse_coll_dates(metadata: dict[str, Any]) -> str:
    dates = (
        metadata.get("study_desc", {})
        .get("study_info", {})
        .get("coll_dates", [])
    )
    if isinstance(dates, list):
        return " | ".join(compact_text(d) for d in dates)
    return compact_text(dates)


def study_metadata(metadata: dict[str, Any], key: str) -> str:
    study = metadata.get("study_desc", {})
    info = study.get("study_info", {})
    if key == "analysis_unit":
        return compact_text(info.get("analysis_unit", ""))
    if key == "geographic_coverage":
        return compact_text(info.get("geog_coverage", ""))
    if key == "study_kind":
        return compact_text(info.get("data_kind", ""))
    if key == "access_type":
        return compact_text(study.get("data_access", {}).get("dataset_use", {}).get("conditions", ""))
    return ""


def summarize_hits(rows: list[dict[str, str]]) -> dict[str, set[str]]:
    by_idno: dict[str, set[str]] = defaultdict(set)
    for row in rows:
        for hit in row["concept_hits"].split(";"):
            if hit:
                by_idno[row["idno"]].add(hit)
    return by_idno


def discover_raw_files() -> list[tuple[Path, str]]:
    raw_root = TEMP_DIR / "raw_downloads"
    extract_root = TEMP_DIR / "raw_extracted"
    extract_root.mkdir(parents=True, exist_ok=True)
    discovered: list[tuple[Path, str]] = []
    if not raw_root.exists():
        return discovered

    for path in sorted(p for p in raw_root.rglob("*") if p.is_file()):
        suffix = path.suffix.lower()
        if suffix in RAW_SUPPORTED_EXTENSIONS:
            discovered.append((path, ""))
            continue
        if suffix == ".zip":
            discovered.extend(extract_zip_members(path, extract_root))
        elif suffix in {".tar", ".tgz", ".gz"} or path.name.lower().endswith((".tar.gz", ".tar.bz2", ".tar.xz")):
            discovered.extend(extract_tar_members(path, extract_root))
        elif suffix in {".7z", ".rar"}:
            discovered.extend(extract_command_archive_members(path, extract_root))
    return discovered


def archive_extract_dir(archive: Path, extract_root: Path) -> Path:
    digest = sha256_file(archive)[:12]
    out = extract_root / f"{safe_name(archive.stem)}_{digest}"
    out.mkdir(parents=True, exist_ok=True)
    return out


def safe_member_path(base: Path, member_name: str) -> Path | None:
    target = (base / member_name).resolve()
    try:
        target.relative_to(base.resolve())
    except ValueError:
        return None
    return target


def extract_zip_members(archive: Path, extract_root: Path) -> list[tuple[Path, str]]:
    out_dir = archive_extract_dir(archive, extract_root)
    found: list[tuple[Path, str]] = []
    try:
        with zipfile.ZipFile(archive) as zf:
            for member in zf.infolist():
                if member.is_dir():
                    continue
                suffix = Path(member.filename).suffix.lower()
                if suffix not in RAW_SUPPORTED_EXTENSIONS:
                    continue
                target = safe_member_path(out_dir, member.filename)
                if target is None:
                    append_log(TEMP_DIR / "audit_log.md", f"Skipped unsafe zip member {member.filename} in {archive}")
                    continue
                target.parent.mkdir(parents=True, exist_ok=True)
                if not target.exists() or target.stat().st_size != member.file_size:
                    with zf.open(member) as src, target.open("wb") as dst:
                        dst.write(src.read())
                found.append((target, str(archive.relative_to(TEMP_DIR.parent))))
    except Exception as exc:
        append_log(TEMP_DIR / "audit_log.md", f"Could not extract zip archive {archive}: {exc}")
    return found


def extract_tar_members(archive: Path, extract_root: Path) -> list[tuple[Path, str]]:
    out_dir = archive_extract_dir(archive, extract_root)
    found: list[tuple[Path, str]] = []
    try:
        with tarfile.open(archive) as tf:
            for member in tf.getmembers():
                if not member.isfile():
                    continue
                suffix = Path(member.name).suffix.lower()
                if suffix not in RAW_SUPPORTED_EXTENSIONS:
                    continue
                target = safe_member_path(out_dir, member.name)
                if target is None:
                    append_log(TEMP_DIR / "audit_log.md", f"Skipped unsafe tar member {member.name} in {archive}")
                    continue
                target.parent.mkdir(parents=True, exist_ok=True)
                extracted = tf.extractfile(member)
                if extracted is None:
                    continue
                if not target.exists() or target.stat().st_size != member.size:
                    with extracted, target.open("wb") as dst:
                        dst.write(extracted.read())
                found.append((target, str(archive.relative_to(TEMP_DIR.parent))))
    except Exception as exc:
        append_log(TEMP_DIR / "audit_log.md", f"Could not extract tar archive {archive}: {exc}")
    return found


def extract_command_archive_members(archive: Path, extract_root: Path) -> list[tuple[Path, str]]:
    tar_cmd = shutil.which("tar")
    if tar_cmd is None:
        append_log(TEMP_DIR / "audit_log.md", f"Archive format requires external extractor but tar was not found: {archive}")
        return []
    out_dir = archive_extract_dir(archive, extract_root)
    try:
        listed = subprocess.run(
            [tar_cmd, "-tf", str(archive)],
            check=True,
            capture_output=True,
            text=True,
            timeout=120,
        )
    except Exception as exc:
        append_log(TEMP_DIR / "audit_log.md", f"Could not list archive {archive} with tar: {exc}")
        return []

    members: list[str] = []
    for line in listed.stdout.splitlines():
        member = line.strip()
        if not member:
            continue
        suffix = Path(member).suffix.lower()
        if suffix not in RAW_SUPPORTED_EXTENSIONS:
            continue
        if safe_member_path(out_dir, member) is None:
            append_log(TEMP_DIR / "audit_log.md", f"Skipped unsafe archive member {member} in {archive}")
            continue
        members.append(member)
    if not members:
        append_log(TEMP_DIR / "audit_log.md", f"No supported raw members found in archive {archive}")
        return []

    for start in range(0, len(members), 50):
        chunk = members[start : start + 50]
        try:
            subprocess.run(
                [tar_cmd, "-xf", str(archive), "-C", str(out_dir), *chunk],
                check=True,
                capture_output=True,
                text=True,
                timeout=300,
            )
        except Exception as exc:
            append_log(TEMP_DIR / "audit_log.md", f"Could not extract archive members from {archive} with tar: {exc}")
            return []

    found: list[tuple[Path, str]] = []
    for member in members:
        target = safe_member_path(out_dir, member)
        if target is not None and target.exists() and target.is_file():
            found.append((target, str(archive.relative_to(TEMP_DIR.parent))))
    return found


def inspect_stat_file(path: Path, extracted_from: str, suffix: str) -> tuple[dict[str, str], list[dict[str, str]]]:
    try:
        import pyreadstat
    except Exception as exc:
        return raw_file_row(path, extracted_from, suffix, "", "", f"pyreadstat_missing: {exc}"), []

    readers = {
        ".dta": pyreadstat.read_dta,
        ".sav": pyreadstat.read_sav,
        ".por": pyreadstat.read_por,
        ".sas7bdat": pyreadstat.read_sas7bdat,
        ".xpt": pyreadstat.read_xport,
    }
    reader = readers.get(suffix)
    if reader is None:
        return raw_file_row(path, extracted_from, suffix, "", "", "unsupported_stat_format"), []
    try:
        df, meta = reader(str(path), metadataonly=True)
        names = list(getattr(meta, "column_names", []) or list(df.columns))
        labels = list(getattr(meta, "column_labels", []) or [])
        dtypes = [str(df[col].dtype) if col in df.columns else "" for col in names]
        row_count = str(getattr(meta, "number_rows", "") or "")
        file_row = raw_file_row(path, extracted_from, suffix, row_count, str(len(names)), "raw_schema_inspected_metadataonly")
        var_rows = raw_variable_rows(path, extracted_from, suffix, names, labels, dtypes, "raw_schema_inspected_metadataonly")
        return file_row, var_rows
    except Exception as exc:
        return raw_file_row(path, extracted_from, suffix, "", "", f"read_failed: {exc}"), []


def inspect_delimited_file(path: Path, extracted_from: str, suffix: str) -> tuple[dict[str, str], list[dict[str, str]]]:
    try:
        import pandas as pd

        sep = "\t" if suffix == ".tsv" else None if suffix == ".txt" else ","
        sample = pd.read_csv(path, sep=sep, engine="python", nrows=1000, encoding_errors="replace")
        row_count = 0
        for chunk in pd.read_csv(path, sep=sep, engine="python", chunksize=100000, usecols=[sample.columns[0]], encoding_errors="replace"):
            row_count += len(chunk)
        names = [str(c) for c in sample.columns]
        labels = [""] * len(names)
        dtypes = [str(sample[c].dtype) for c in sample.columns]
        return (
            raw_file_row(path, extracted_from, suffix, str(row_count), str(len(names)), "raw_schema_inspected_sampled_values"),
            raw_variable_rows(path, extracted_from, suffix, names, labels, dtypes, "raw_schema_inspected_sampled_values"),
        )
    except Exception as exc:
        return raw_file_row(path, extracted_from, suffix, "", "", f"read_failed: {exc}"), []


def inspect_excel_file(path: Path, extracted_from: str, suffix: str) -> tuple[list[dict[str, str]], list[dict[str, str]]]:
    try:
        import pandas as pd

        workbook = pd.ExcelFile(path)
        file_rows = []
        var_rows = []
        for sheet in workbook.sheet_names:
            sample = pd.read_excel(path, sheet_name=sheet, nrows=1000)
            sheet_path = Path(f"{path}::{sheet}")
            names = [str(c) for c in sample.columns]
            labels = [""] * len(names)
            dtypes = [str(sample[c].dtype) for c in sample.columns]
            file_rows.append(raw_file_row(sheet_path, extracted_from, suffix, "", str(len(names)), "raw_schema_inspected_excel_sample"))
            var_rows.extend(raw_variable_rows(sheet_path, extracted_from, suffix, names, labels, dtypes, "raw_schema_inspected_excel_sample"))
        return file_rows, var_rows
    except Exception as exc:
        return [raw_file_row(path, extracted_from, suffix, "", "", f"read_failed: {exc}")], []


def inspect_parquet_or_feather(path: Path, extracted_from: str, suffix: str) -> tuple[dict[str, str], list[dict[str, str]]]:
    try:
        if suffix == ".parquet":
            import pyarrow.parquet as pq

            meta = pq.read_metadata(path)
            schema = meta.schema.to_arrow_schema()
            names = schema.names
            dtypes = [str(schema.field(name).type) for name in names]
            labels = [""] * len(names)
            return (
                raw_file_row(path, extracted_from, suffix, str(meta.num_rows), str(meta.num_columns), "raw_schema_inspected_metadataonly"),
                raw_variable_rows(path, extracted_from, suffix, names, labels, dtypes, "raw_schema_inspected_metadataonly"),
            )
        import pandas as pd

        sample = pd.read_feather(path)
        names = [str(c) for c in sample.columns]
        labels = [""] * len(names)
        dtypes = [str(sample[c].dtype) for c in sample.columns]
        return (
            raw_file_row(path, extracted_from, suffix, str(len(sample)), str(len(names)), "raw_schema_inspected_values"),
            raw_variable_rows(path, extracted_from, suffix, names, labels, dtypes, "raw_schema_inspected_values"),
        )
    except Exception as exc:
        return raw_file_row(path, extracted_from, suffix, "", "", f"read_failed: {exc}"), []


def raw_file_row(path: Path, extracted_from: str, suffix: str, row_count: str, column_count: str, status: str) -> dict[str, str]:
    real_path = Path(str(path).split("::", 1)[0])
    sheet_suffix = ""
    if "::" in str(path):
        sheet_suffix = "::" + str(path).split("::", 1)[1]
    error = status if status.startswith(("read_failed", "pyreadstat_missing")) else ""
    clean_status = "failed" if error else status
    if real_path.exists():
        try:
            source_path = str(real_path.relative_to(TEMP_DIR.parent)) + sheet_suffix
        except ValueError:
            source_path = str(real_path) + sheet_suffix
    else:
        source_path = str(path)
    return {
        "source_path": source_path,
        "extracted_from": extracted_from,
        "file_format": suffix,
        "file_size_bytes": str(real_path.stat().st_size) if real_path.exists() else "",
        "sha256": sha256_file(real_path) if real_path.exists() else "",
        "row_count": row_count,
        "column_count": column_count,
        "status": clean_status,
        "error": error,
    }


def raw_variable_rows(
    path: Path,
    extracted_from: str,
    suffix: str,
    names: list[str],
    labels: list[str],
    dtypes: list[str],
    status: str,
) -> list[dict[str, str]]:
    rows = []
    for i, name in enumerate(names):
        label = labels[i] if i < len(labels) and labels[i] is not None else ""
        dtype = dtypes[i] if i < len(dtypes) else ""
        real_path = Path(str(path).split("::", 1)[0])
        sheet_suffix = ""
        if "::" in str(path):
            sheet_suffix = "::" + str(path).split("::", 1)[1]
        if real_path.exists():
            try:
                source_path = str(real_path.relative_to(TEMP_DIR.parent)) + sheet_suffix
            except ValueError:
                source_path = str(real_path) + sheet_suffix
        else:
            source_path = str(path)
        rows.append(
            {
                "source_path": source_path,
                "extracted_from": extracted_from,
                "file_format": suffix,
                "variable_name": name,
                "variable_label": str(label),
                "dtype": dtype,
                "concept_hits": ";".join(concept_hits(name, str(label), path.name, "")),
                "status": status,
            }
        )
    return rows


def inspect_raw_downloads() -> tuple[list[dict[str, str]], list[dict[str, str]]]:
    file_rows: list[dict[str, str]] = []
    variable_rows: list[dict[str, str]] = []
    for path, extracted_from in discover_raw_files():
        suffix = path.suffix.lower()
        if suffix in {".dta", ".sav", ".por", ".sas7bdat", ".xpt"}:
            file_row, var_rows = inspect_stat_file(path, extracted_from, suffix)
            file_rows.append(file_row)
            variable_rows.extend(var_rows)
        elif suffix in {".csv", ".tsv", ".txt"}:
            file_row, var_rows = inspect_delimited_file(path, extracted_from, suffix)
            file_rows.append(file_row)
            variable_rows.extend(var_rows)
        elif suffix in {".xlsx", ".xls"}:
            rows, var_rows = inspect_excel_file(path, extracted_from, suffix)
            file_rows.extend(rows)
            variable_rows.extend(var_rows)
        elif suffix in {".parquet", ".feather"}:
            file_row, var_rows = inspect_parquet_or_feather(path, extracted_from, suffix)
            file_rows.append(file_row)
            variable_rows.extend(var_rows)
    return file_rows, variable_rows


def infer_raw_context(source_path: str, screen_by_idno: dict[str, dict[str, str]]) -> tuple[str, dict[str, str]]:
    matches = []
    path_text = source_path.replace("\\", "/")
    safe_text = safe_name(path_text)
    for idno, screen in screen_by_idno.items():
        if idno in path_text or safe_name(idno) in safe_text:
            matches.append((idno, screen))
    if not matches:
        return "", {}
    return max(matches, key=lambda item: len(item[0]))


def add_raw_map_rows(
    map_rows: dict[str, list[dict[str, str]]],
    raw_variable_rows_in: list[dict[str, str]],
    screen_by_idno: dict[str, dict[str, str]],
) -> None:
    for row in raw_variable_rows_in:
        hits = [hit for hit in row.get("concept_hits", "").split(";") if hit]
        if not hits:
            continue
        idno, screen = infer_raw_context(row["source_path"], screen_by_idno)
        for hit in hits:
            if hit not in CONCEPT_TO_MAP:
                continue
            map_group, harmonized = CONCEPT_TO_MAP[hit]
            map_rows[map_group].append(
                {
                    "country": screen.get("country", ""),
                    "survey_name": screen.get("survey name", ""),
                    "wave": screen.get("wave/year", ""),
                    "idno": idno,
                    "file": row["source_path"],
                    "raw_variable": row["variable_name"],
                    "raw_label": row["variable_label"],
                    "harmonized_variable": harmonized,
                    "unit": "unknown_from_raw_schema",
                    "recall_period": "unknown_from_raw_schema",
                    "construction_rule": "candidate from raw schema; inspect values, questionnaires, units, and recall period before use",
                    "quality_flag": "raw_schema_inspected_requires_value_audit",
                    "notes": f"concept_hit={hit}; dtype={row.get('dtype', '')}; extracted_from={row.get('extracted_from', '')}",
                }
            )


def bool_score(has_it: bool, score_if_true: int = 1) -> int:
    return score_if_true if has_it else 0


def int_or_zero(value: str) -> int:
    try:
        return int(str(value).replace(",", ""))
    except Exception:
        return 0


def write_design_scorecard(screening_rows: list[dict[str, str]], file_rows: list[dict[str, str]], variable_rows: list[dict[str, str]]) -> None:
    hits_by_idno = summarize_hits(variable_rows)
    max_cases_by_idno: dict[str, int] = defaultdict(int)
    for row in file_rows:
        max_cases_by_idno[row["idno"]] = max(max_cases_by_idno[row["idno"]], int_or_zero(row.get("cases", "")))

    score_rows = []
    screened_by_idno = {r["idno"]: r for r in screening_rows}
    for idno, hits in sorted(hits_by_idno.items()):
        screen = screened_by_idno.get(idno, {})
        has_financial = "total_consumption_income" in hits and "oop_health_expenditure" in hits
        has_access = "illness_need" in hits and ("care_sought" in hits or "reason_not_sought" in hits)
        has_timing = "interview_date" in hits or "catalog years available" in screen.get("interview year", "").lower()
        has_geo = bool({"gps", "admin_geography", "psu_cluster", "rural_urban"} & hits)
        data_coverage = int(screen.get("feasibility score from 0 to 5") or 0)
        outcome_validity = min(5, bool_score(has_financial, 3) + bool_score(has_access, 2))
        exposure_precision = min(5, bool_score(has_timing, 2) + bool_score("gps" in hits, 2) + bool_score(has_geo and "gps" not in hits, 1))
        max_cases = max_cases_by_idno.get(idno, 0)
        sample_size_score = 5 if max_cases >= 10000 else 4 if max_cases >= 5000 else 3 if max_cases >= 2000 else 2 if max_cases > 0 else 0
        panel_text = screen.get("panel or repeated cross-section", "").lower()
        identifying = 3 if "panel" in panel_text or "longitudinal" in panel_text else 2 if "repeated" in panel_text or "wave" in panel_text else 1
        policy_relevance = 4 if screen.get("country", "") in {"Burkina Faso", "Ethiopia", "Malawi", "Mali", "Niger", "Nigeria", "Tanzania", "Uganda"} else 3
        reason = "metadata-only score; raw microdata access, event rates, climate linkage, and placebo tests are still missing"
        if not has_financial:
            reason = "financial-protection design not yet supported by metadata hits for both total consumption/income and OOP health spending"
        score_rows.append(
            {
                "design_id": f"{idno}_financial_access_climate",
                "country_scope": screen.get("country", ""),
                "outcome": "financial hardship plus access outcomes if raw variables verify",
                "exposure": "pre-interview CHIRPS/ERA5/NASA POWER climate anomaly, not yet extracted",
                "data_coverage": data_coverage,
                "outcome_validity": outcome_validity,
                "exposure_precision": exposure_precision,
                "sample_size": sample_size_score,
                "event_rate": 0,
                "climate_geography_linkage_quality": exposure_precision,
                "identifying_variation": identifying,
                "pre-trend/placebo credibility": 0,
                "model_stability": 0,
                "policy_relevance": policy_relevance,
                "ML usefulness": 0,
                "journal potential": 2 if has_financial and has_geo and has_timing else 1,
                "go/no-go": "no-go for estimation; go for manual raw access/schema inspection",
                "reason": reason,
            }
        )
    write_csv(RESULT_DIR / "design_scorecard.csv", score_rows, DESIGN_COLUMNS)


def write_reports(
    study_rows: list[dict[str, str]],
    file_rows: list[dict[str, str]],
    variable_rows: list[dict[str, str]],
    map_counts: Counter[str],
    raw_file_count: int,
    raw_variable_count: int,
) -> None:
    concept_counts = Counter()
    study_hits = summarize_hits(variable_rows)
    for row in variable_rows:
        for hit in row["concept_hits"].split(";"):
            if hit:
                concept_counts[hit] += 1
    financial_ready_metadata = sum(
        1 for hits in study_hits.values() if "total_consumption_income" in hits and "oop_health_expenditure" in hits
    )
    access_ready_metadata = sum(
        1 for hits in study_hits.values() if "illness_need" in hits and ("care_sought" in hits or "reason_not_sought" in hits)
    )
    geography_timing_metadata = sum(
        1 for hits in study_hits.values() if {"gps", "admin_geography", "psu_cluster", "rural_urban"} & hits
    )

    top_concepts = "\n".join(f"| {k} | {v} |" for k, v in concept_counts.most_common(20))
    map_table = "\n".join(f"| `{MAP_FILENAMES[k]}` | {v} |" for k, v in sorted(map_counts.items()))

    (REPORT_DIR / "data_dictionary.md").write_text(
        f"""# Harmonized Data Dictionary

Status: metadata-backed draft only. These fields are candidate mappings from official World Bank catalog/data-dictionary metadata and variable labels. They are not yet verified against raw microdata files.

## Metadata Coverage

| Item | Count |
|---|---:|
| Priority studies with metadata schema extraction | {len(study_rows)} |
| Data files/modules parsed from data dictionaries | {len(file_rows)} |
| Variables parsed from API labels | {len(variable_rows)} |
| Studies with metadata hits for both consumption/income and OOP health expenditure | {financial_ready_metadata} |
| Studies with metadata hits for health need plus care/access | {access_ready_metadata} |
| Studies with some geography/cluster/residence metadata hit | {geography_timing_metadata} |

## Candidate Variable Map Rows

| Map file | Candidate rows |
|---|---:|
{map_table}

## Top Metadata Concepts

| Concept | Variable-label hits |
|---|---:|
{top_concepts}

## Harmonized Minimum Fields

The intended harmonized fields remain those in the project objective: country, survey metadata, IDs, weights, survey design, timing, geography, household demographics, total consumption/income, OOP health expenditure, insurance, illness/need, care seeking, access barriers, coping, food insecurity, and livelihood variables.

Every current row in `temp/variable_map_*.csv` has quality flag `metadata_only_requires_raw_verification`. Raw Stata/SPSS/SAS/CSV files must be inspected before any harmonized analytical dataset is built.
""",
        encoding="utf-8",
    )

    raw_status = (
        f"raw schema inspection found {raw_file_count} tabular files and {raw_variable_count} variables"
        if raw_file_count
        else "raw microdata inspection still pending manual access; no tabular files found in temp/raw_downloads"
    )

    summary = f"""# Metadata Schema Audit

Status: public metadata/schema extraction complete for priority studies; {raw_status}.

## Outputs

- `temp/raw_schema_inventory/schema_study_inventory.csv`
- `temp/raw_schema_inventory/schema_file_inventory.csv`
- `temp/raw_schema_inventory/metadata_variable_catalog.csv`
- `temp/variable_map_consumption.csv`
- `temp/variable_map_health_expenditure.csv`
- `temp/variable_map_health_need_access.csv`
- `temp/variable_map_geography.csv`
- `temp/variable_map_survey_design.csv`
- `temp/variable_map_demographics.csv`
- `temp/variable_map_shocks.csv`
- `result/design_scorecard.csv`

## Counts

| Item | Count |
|---|---:|
| Studies | {len(study_rows)} |
| Data files/modules | {len(file_rows)} |
| Variables | {len(variable_rows)} |
| Raw tabular files inspected | {raw_file_count} |
| Raw variables inspected | {raw_variable_count} |
| Metadata financial-protection candidates | {financial_ready_metadata} |
| Metadata access-outcome candidates | {access_ready_metadata} |

## Interpretation

This audit strengthens the acquisition and screening layer but does not by itself satisfy analytical-dataset requirements. Metadata can identify promising modules and variables. Raw schema inspection verifies file readability and labels when files are present, but outcome construction still requires value checks, missingness, event rates, recall periods, survey weights, GPS displacement, and harmonized formulas.
"""
    (TEMP_DIR / "metadata_schema_audit.md").write_text(summary, encoding="utf-8")


def main() -> None:
    ensure_dirs()
    screening_rows = read_csv_dicts(TEMP_DIR / "country_wave_screening.csv")
    screen_by_idno = {row["idno"]: row for row in screening_rows if row.get("idno")}
    study_dirs = sorted([p for p in (TEMP_DIR / "raw_schema_inventory").iterdir() if p.is_dir()])

    study_rows: list[dict[str, str]] = []
    file_rows: list[dict[str, str]] = []
    variable_rows: list[dict[str, str]] = []
    map_rows: dict[str, list[dict[str, str]]] = defaultdict(list)

    for study_dir in study_dirs:
        variables_path = find_file(study_dir, "_variables.json")
        metadata_path = find_file(study_dir, "_metadata_export.json")
        if not variables_path:
            continue
        variables_json = read_json(variables_path)
        variables = variables_json.get("variables", [])
        idno = match_idno(study_dir, screen_by_idno)
        screen = screen_by_idno.get(idno, {})
        catalog_id = screen.get("catalog id", "")
        if not catalog_id:
            continue

        html_path, dd_status = fetch_data_dictionary(catalog_id, study_dir / f"{study_dir.name}_data_dictionary.html")
        file_map = parse_data_dictionary(html_path, catalog_id)
        metadata = read_json(metadata_path) if metadata_path and metadata_path.exists() else {}

        for fid, fdata in sorted(file_map.items(), key=lambda x: int(re.sub(r"\D", "", x[0]) or 0)):
            file_rows.append(
                {
                    "country": screen.get("country", ""),
                    "survey_name": screen.get("survey name", ""),
                    "wave": screen.get("wave/year", ""),
                    "idno": idno,
                    "catalog_id": catalog_id,
                    "fid": fid,
                    "file_name": fdata.get("file_name", ""),
                    "file_description": fdata.get("file_description", ""),
                    "cases": fdata.get("cases", ""),
                    "variable_count": fdata.get("variable_count", ""),
                    "unit_guess": unit_guess(fdata.get("file_name", ""), fdata.get("file_description", "")),
                    "module_guess": module_guess(fdata.get("file_name", ""), fdata.get("file_description", "")),
                    "source_url": fdata.get("source_url", ""),
                    "status": f"metadata_only; data_dictionary_{dd_status}",
                }
            )

        for var in variables:
            fid = str(var.get("fid", ""))
            fdata = file_map.get(fid, {})
            name = str(var.get("name", ""))
            label = str(var.get("labl", ""))
            hits = concept_hits(name, label, fdata.get("file_name", ""), fdata.get("file_description", ""))
            variable_rows.append(
                {
                    "country": screen.get("country", ""),
                    "survey_name": screen.get("survey name", ""),
                    "wave": screen.get("wave/year", ""),
                    "idno": idno,
                    "catalog_id": catalog_id,
                    "fid": fid,
                    "file_name": fdata.get("file_name", ""),
                    "file_description": fdata.get("file_description", ""),
                    "variable_name": name,
                    "variable_label": label,
                    "concept_hits": ";".join(hits),
                    "source": str(variables_path.relative_to(TEMP_DIR.parent)),
                }
            )
            for hit in hits:
                if hit not in CONCEPT_TO_MAP:
                    continue
                map_group, harmonized = CONCEPT_TO_MAP[hit]
                map_rows[map_group].append(
                    {
                        "country": screen.get("country", ""),
                        "survey_name": screen.get("survey name", ""),
                        "wave": screen.get("wave/year", ""),
                        "idno": idno,
                        "file": fdata.get("file_name", fid),
                        "raw_variable": name,
                        "raw_label": label,
                        "harmonized_variable": harmonized,
                        "unit": unit_guess(fdata.get("file_name", ""), fdata.get("file_description", "")),
                        "recall_period": "unknown_from_metadata",
                        "construction_rule": "candidate only; inspect raw values, questionnaires, units, and recall period before use",
                        "quality_flag": "metadata_only_requires_raw_verification",
                        "notes": f"concept_hit={hit}; file_description={fdata.get('file_description', '')[:160]}",
                    }
                )

        study_rows.append(
            {
                "country": screen.get("country", ""),
                "survey_name": screen.get("survey name", ""),
                "wave": screen.get("wave/year", ""),
                "idno": idno,
                "catalog_id": catalog_id,
                "access_type": screen.get("access type", ""),
                "analysis_unit": study_metadata(metadata, "analysis_unit"),
                "geographic_coverage": study_metadata(metadata, "geographic_coverage"),
                "fieldwork_dates": parse_coll_dates(metadata),
                "study_kind": study_metadata(metadata, "study_kind"),
                "file_count": len(file_map),
                "variable_count_api": str(variables_json.get("total", len(variables))),
                "variable_count_catalog": screen.get("variable count", ""),
                "metadata_json": str(metadata_path.relative_to(TEMP_DIR.parent)) if metadata_path else "",
                "variables_json": str(variables_path.relative_to(TEMP_DIR.parent)),
                "data_dictionary_html": str(html_path.relative_to(TEMP_DIR.parent)) if html_path else "",
                "status": "metadata_schema_extracted; raw_microdata_pending_manual_access",
            }
        )

        write_csv(study_dir / f"{study_dir.name}_schema_files.csv", [r for r in file_rows if r["idno"] == idno], SCHEMA_FILE_COLUMNS)
        write_csv(study_dir / f"{study_dir.name}_variable_catalog.csv", [r for r in variable_rows if r["idno"] == idno], VARIABLE_CATALOG_COLUMNS)

    raw_file_rows, raw_variable_rows_out = inspect_raw_downloads()
    add_raw_map_rows(map_rows, raw_variable_rows_out, screen_by_idno)

    schema_root = TEMP_DIR / "raw_schema_inventory"
    write_csv(schema_root / "schema_study_inventory.csv", study_rows, STUDY_INVENTORY_COLUMNS)
    write_csv(schema_root / "schema_file_inventory.csv", file_rows, SCHEMA_FILE_COLUMNS)
    write_csv(schema_root / "metadata_variable_catalog.csv", variable_rows, VARIABLE_CATALOG_COLUMNS)
    write_csv(schema_root / "raw_file_inventory.csv", raw_file_rows, RAW_FILE_COLUMNS)
    write_csv(schema_root / "raw_variable_catalog.csv", raw_variable_rows_out, RAW_VARIABLE_COLUMNS)

    map_counts = Counter()
    for group, filename in MAP_FILENAMES.items():
        rows = map_rows.get(group, [])
        rows.sort(key=lambda r: (r["country"], r["survey_name"], r["file"], r["raw_variable"], r["harmonized_variable"]))
        map_counts[group] = len(rows)
        write_csv(TEMP_DIR / filename, rows, MAP_COLUMNS)

    write_design_scorecard(screening_rows, file_rows, variable_rows)
    write_reports(study_rows, file_rows, variable_rows, map_counts, len(raw_file_rows), len(raw_variable_rows_out))
    append_log(
        TEMP_DIR / "audit_log.md",
        f"Metadata schema inspection complete for {len(study_rows)} studies, {len(file_rows)} files/modules, and {len(variable_rows)} variables.",
    )
    append_log(
        TEMP_DIR / "audit_log.md",
        f"Raw file inspection found {len(raw_file_rows)} tabular files and {len(raw_variable_rows_out)} raw variables.",
    )
    print(f"Metadata schema inspection complete for {len(study_rows)} studies, {len(file_rows)} files/modules, and {len(variable_rows)} variables.")
    print(f"Raw file inspection found {len(raw_file_rows)} tabular files and {len(raw_variable_rows_out)} raw variables.")


if __name__ == "__main__":
    main()
