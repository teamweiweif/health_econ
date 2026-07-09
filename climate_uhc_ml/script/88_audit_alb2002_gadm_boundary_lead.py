from __future__ import annotations

import csv
import hashlib
import re
import unicodedata
import urllib.request
import zipfile
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

from common import REPORT_DIR, RESULT_DIR, SNAPSHOT_DIR, TEMP_DIR, append_log, ensure_dirs, write_csv


SURVEY_TEMPLATE = TEMP_DIR / "alb2002_district_climate_crosswalk_template.csv"
AUDIT_PATH = TEMP_DIR / "alb2002_gadm_boundary_lead_audit.csv"
MATCH_PATH = TEMP_DIR / "alb2002_gadm_boundary_name_match_audit.csv"
SUMMARY_PATH = RESULT_DIR / "alb2002_gadm_boundary_lead_summary.csv"
REPORT_PATH = REPORT_DIR / "alb2002_gadm_boundary_lead_audit.md"

GADM_SOURCES = [
    {
        "candidate_id": "gadm36_alb_adm2",
        "source_name": "GADM 3.6 Albania shapefile",
        "source_url": "https://geodata.ucdavis.edu/gadm/gadm3.6/shp/gadm36_ALB_shp.zip",
        "snapshot_name": "gadm36_ALB_shp.zip",
        "adm2_dbf": "gadm36_ALB_2.dbf",
        "expected_level": "ADM2",
        "source_version": "3.6",
    },
    {
        "candidate_id": "gadm41_alb_adm2",
        "source_name": "GADM 4.1 Albania shapefile",
        "source_url": "https://geodata.ucdavis.edu/gadm/gadm4.1/shp/gadm41_ALB_shp.zip",
        "snapshot_name": "gadm41_ALB_shp.zip",
        "adm2_dbf": "gadm41_ALB_2.dbf",
        "expected_level": "ADM2",
        "source_version": "4.1",
    },
]

DECISION = "blocked_gadm_boundary_lead_no_verified_2002_historical_provenance"

AUDIT_COLUMNS = [
    "candidate_id",
    "source_name",
    "source_url",
    "snapshot_path",
    "snapshot_sha256",
    "download_status",
    "source_version",
    "adm2_dbf",
    "adm2_row_count",
    "adm2_distinct_normalized_key_count",
    "adm2_engtype_district_rows",
    "adm2_type_rreth_rows",
    "complete_name_coverage",
    "missing_survey_key_count",
    "extra_boundary_key_count",
    "duplicate_boundary_key_count",
    "duplicate_boundary_feature_rows",
    "historical_2002_provenance_status",
    "geometry_promoted",
    "climate_linkage_ready",
    "suitability_status",
    "blocking_reason",
]

MATCH_COLUMNS = [
    "candidate_id",
    "match_scope",
    "survey_district_code",
    "survey_district_key",
    "boundary_gid",
    "boundary_name_1",
    "boundary_name_2",
    "boundary_type_2",
    "boundary_engtype_2",
    "normalized_boundary_key",
    "match_status",
    "notes",
]

SUMMARY_COLUMNS = ["metric", "value", "interpretation"]

GENITIVE_REPAIRS = {
    "BERATIT": "BERAT",
    "KUCOVES": "KUCOVE",
    "SKRAPARIT": "SKRAPAR",
    "BULQIZES": "BULQIZE",
    "DIBRES": "DIBER",
    "MATIT": "MAT",
    "DURRESIT": "DURRES",
    "KRUJES": "KRUJE",
    "KAVAJES": "KAVAJE",
    "ELBASANIT": "ELBASAN",
    "GRAMSHIT": "GRAMSH",
    "LIBRAZHDIT": "LIBRAZHD",
    "PEQINIT": "PEQIN",
    "FIERIT": "FIER",
    "LUSHNJES": "LUSHNJE",
    "MALLAKASTRES": "MALLAKASTER",
    "GJIROKASTRES": "GJIROKASTER",
    "PERMETIT": "PERMET",
    "TEPELENES": "TEPELENE",
    "KORCES": "KORCE",
    "DEVOLLIT": "DEVOLL",
    "KOLONJES": "KOLONJE",
    "POGRADECIT": "POGRADEC",
    "KUKESIT": "KUKES",
    "HASIT": "HAS",
    "TROPOJES": "TROPOJE",
    "LEZHES": "LEZHE",
    "KURBINIT": "KURBIN",
    "MIRDITES": "MIRDITE",
    "SHKODRES": "SHKODER",
    "MALESISE E MADHE": "MALESI E MADHE",
    "PUKES": "PUKE",
    "TIRANES": "TIRANE",
    "DELVINES": "DELVINE",
    "SARANDES": "SARANDE",
    "VLORES": "VLORE",
}

ENCODING_REPAIRS = {
    "KORE": "KORCE",
    "KUOVE": "KUCOVE",
}


def read_csv_dicts(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        return []
    with path.open(encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def download(url: str, path: Path) -> str:
    if path.exists() and path.stat().st_size > 0:
        return "already_exists"
    try:
        with urllib.request.urlopen(url, timeout=60) as response:
            path.write_bytes(response.read())
        return "downloaded"
    except Exception as exc:  # pragma: no cover - network-specific evidence path
        return f"download_failed:{type(exc).__name__}:{exc}"


def normalize_key(value: str) -> str:
    text = unicodedata.normalize("NFKD", value or "").encode("ascii", "ignore").decode("ascii")
    text = re.sub(r"[^A-Za-z0-9]+", " ", text).strip().upper()
    text = re.sub(r"\b(RRETHI|RRETH|DISTRICT|QARK|COUNTY)\b", "", text).strip()
    text = re.sub(r"\s+", " ", text)
    text = GENITIVE_REPAIRS.get(text, text)
    text = ENCODING_REPAIRS.get(text, text)
    return text


def normalize_type_value(value: str) -> str:
    text = unicodedata.normalize("NFKD", value or "").encode("ascii", "ignore").decode("ascii")
    text = re.sub(r"[^A-Za-z0-9]+", " ", text).strip().upper()
    return re.sub(r"\s+", " ", text)


def read_dbf_from_zip(zip_path: Path, dbf_name: str) -> list[dict[str, str]]:
    with zipfile.ZipFile(zip_path) as zf:
        data = zf.read(dbf_name)
    nrec = int.from_bytes(data[4:8], "little")
    header_len = int.from_bytes(data[8:10], "little")
    record_len = int.from_bytes(data[10:12], "little")
    fields: list[tuple[str, int]] = []
    pos = 32
    while pos < header_len - 1:
        desc = data[pos : pos + 32]
        if not desc or desc[0] == 0x0D:
            break
        name = desc[:11].split(b"\x00", 1)[0].decode("ascii", errors="replace")
        length = desc[16]
        fields.append((name, length))
        pos += 32

    rows: list[dict[str, str]] = []
    for i in range(nrec):
        rec = data[header_len + i * record_len : header_len + (i + 1) * record_len]
        if not rec or rec[0:1] == b"*":
            continue
        offset = 1
        row: dict[str, str] = {}
        for name, length in fields:
            raw = rec[offset : offset + length]
            offset += length
            row[name] = raw.decode("utf-8", errors="replace").strip()
        rows.append(row)
    return rows


def survey_rows() -> list[dict[str, str]]:
    return read_csv_dicts(SURVEY_TEMPLATE)


def build_audit() -> tuple[list[dict[str, str]], list[dict[str, str]], list[dict[str, str]]]:
    ensure_dirs()
    SNAPSHOT_DIR.mkdir(parents=True, exist_ok=True)
    survey = survey_rows()
    survey_keys = {normalize_key(row.get("district_name_review_key", "")): row for row in survey}
    survey_key_set = set(survey_keys)

    audit_rows: list[dict[str, str]] = []
    match_rows: list[dict[str, str]] = []

    for source in GADM_SOURCES:
        snapshot = SNAPSHOT_DIR / source["snapshot_name"]
        status = download(source["source_url"], snapshot)
        rows: list[dict[str, str]] = []
        if snapshot.exists() and snapshot.stat().st_size > 0:
            rows = read_dbf_from_zip(snapshot, source["adm2_dbf"])

        boundary_by_key: dict[str, list[dict[str, str]]] = defaultdict(list)
        for row in rows:
            boundary_by_key[normalize_key(row.get("NAME_2", ""))].append(row)

        boundary_keys = set(boundary_by_key)
        missing = sorted(survey_key_set - boundary_keys)
        extra = sorted(boundary_keys - survey_key_set)
        duplicates = {key: vals for key, vals in boundary_by_key.items() if len(vals) > 1}
        duplicate_feature_rows = sum(len(vals) for vals in duplicates.values())
        engtype_district = sum(1 for row in rows if normalize_type_value(row.get("ENGTYPE_2", "")) == "DISTRICT")
        type_rreth = sum(1 for row in rows if normalize_type_value(row.get("TYPE_2", "")) == "RRETH")
        complete_name_coverage = int(not missing and not extra)

        if source["candidate_id"] == "gadm36_alb_adm2" and complete_name_coverage and engtype_district == len(rows):
            suitability = "candidate_name_coverage_but_duplicate_key_and_provenance_blocked"
            blocker = "GADM 3.6 ADM2 is labeled District/Rreth and covers the 36 normalized LSMS district keys, but it has 37 features because SHKODER appears twice and no verified 2001/2002 official source provenance is present."
        elif complete_name_coverage:
            suitability = "candidate_name_coverage_but_not_historical_or_typed_district_ready"
            blocker = "Names can be aligned after repairs, but source type/provenance is insufficient for 2002 historical climate linkage."
        else:
            suitability = "blocked_name_coverage_or_unit_mismatch"
            blocker = "Boundary keys do not fully match the 36 ALB_2002 survey district keys after documented normalization."

        audit_rows.append(
            {
                "candidate_id": source["candidate_id"],
                "source_name": source["source_name"],
                "source_url": source["source_url"],
                "snapshot_path": str(snapshot.relative_to(TEMP_DIR.parent)).replace("\\", "/"),
                "snapshot_sha256": sha256(snapshot) if snapshot.exists() and snapshot.stat().st_size > 0 else "",
                "download_status": status,
                "source_version": source["source_version"],
                "adm2_dbf": source["adm2_dbf"],
                "adm2_row_count": str(len(rows)),
                "adm2_distinct_normalized_key_count": str(len(boundary_keys)),
                "adm2_engtype_district_rows": str(engtype_district),
                "adm2_type_rreth_rows": str(type_rreth),
                "complete_name_coverage": str(complete_name_coverage),
                "missing_survey_key_count": str(len(missing)),
                "extra_boundary_key_count": str(len(extra)),
                "duplicate_boundary_key_count": str(len(duplicates)),
                "duplicate_boundary_feature_rows": str(duplicate_feature_rows),
                "historical_2002_provenance_status": "blocked_no_verified_official_2001_2002_boundary_provenance",
                "geometry_promoted": "0",
                "climate_linkage_ready": "0",
                "suitability_status": suitability,
                "blocking_reason": blocker,
            }
        )

        for key in sorted(survey_key_set):
            survey_row = survey_keys[key]
            vals = boundary_by_key.get(key, [])
            if vals:
                for val in vals:
                    match_rows.append(
                        match_row(source, "survey_to_boundary", survey_row, key, val, "matched_normalized_key", "")
                    )
            else:
                match_rows.append(match_row(source, "survey_to_boundary", survey_row, key, {}, "missing_boundary_key", "No GADM ADM2 row matched this survey district key."))
        for key in extra:
            for val in boundary_by_key[key]:
                match_rows.append(match_row(source, "boundary_extra", {}, "", val, "extra_boundary_key", "Boundary key does not match a survey district key after normalization."))
        for key, vals in duplicates.items():
            for val in vals:
                match_rows.append(match_row(source, "boundary_duplicate", {}, key, val, "duplicate_boundary_key", "Multiple GADM ADM2 features normalize to this district key."))

    summary = build_summary(audit_rows)
    return audit_rows, match_rows, summary


def match_row(
    source: dict[str, str],
    scope: str,
    survey_row: dict[str, str],
    survey_key: str,
    boundary_row: dict[str, str],
    status: str,
    notes: str,
) -> dict[str, str]:
    return {
        "candidate_id": source["candidate_id"],
        "match_scope": scope,
        "survey_district_code": survey_row.get("district_code_identification", ""),
        "survey_district_key": survey_key,
        "boundary_gid": boundary_row.get("GID_2", ""),
        "boundary_name_1": boundary_row.get("NAME_1", ""),
        "boundary_name_2": boundary_row.get("NAME_2", ""),
        "boundary_type_2": boundary_row.get("TYPE_2", ""),
        "boundary_engtype_2": boundary_row.get("ENGTYPE_2", ""),
        "normalized_boundary_key": normalize_key(boundary_row.get("NAME_2", "")),
        "match_status": status,
        "notes": notes,
    }


def build_summary(rows: list[dict[str, str]]) -> list[dict[str, str]]:
    by_id = {row["candidate_id"]: row for row in rows}
    gadm36 = by_id.get("gadm36_alb_adm2", {})
    gadm41 = by_id.get("gadm41_alb_adm2", {})
    return [
        summary_row("alb2002_gadm_boundary_lead_candidate_rows", len(rows), "GADM source candidates audited."),
        summary_row("alb2002_gadm36_adm2_row_count", gadm36.get("adm2_row_count", "0"), "GADM 3.6 ADM2 feature rows."),
        summary_row("alb2002_gadm36_distinct_normalized_key_count", gadm36.get("adm2_distinct_normalized_key_count", "0"), "GADM 3.6 distinct normalized ADM2 keys."),
        summary_row("alb2002_gadm36_engtype_district_rows", gadm36.get("adm2_engtype_district_rows", "0"), "GADM 3.6 rows labeled as District."),
        summary_row("alb2002_gadm36_type_rreth_rows", gadm36.get("adm2_type_rreth_rows", "0"), "GADM 3.6 rows labeled as Rreth."),
        summary_row("alb2002_gadm36_complete_name_coverage_rows", gadm36.get("complete_name_coverage", "0"), "Whether GADM 3.6 covers all 36 normalized ALB_2002 district keys with no extra keys."),
        summary_row("alb2002_gadm36_duplicate_boundary_key_count", gadm36.get("duplicate_boundary_key_count", "0"), "Distinct duplicated normalized GADM 3.6 boundary keys."),
        summary_row("alb2002_gadm36_duplicate_boundary_feature_rows", gadm36.get("duplicate_boundary_feature_rows", "0"), "GADM 3.6 feature rows belonging to duplicated keys."),
        summary_row("alb2002_gadm41_adm2_row_count", gadm41.get("adm2_row_count", "0"), "GADM 4.1 ADM2 feature rows."),
        summary_row("alb2002_gadm41_engtype_district_rows", gadm41.get("adm2_engtype_district_rows", "0"), "GADM 4.1 rows labeled as District; expected zero because type fields are NA."),
        summary_row("alb2002_gadm_boundary_lead_historical_2002_ready_rows", 0, "Rows ready as verified 2001/2002 historical district boundaries after this audit; intentionally zero."),
        summary_row("alb2002_gadm_boundary_lead_climate_linkage_ready_rows", 0, "Rows ready for ALB_2002 climate-linkage promotion after this audit; intentionally zero."),
        summary_row("alb2002_gadm_boundary_lead_current_decision", DECISION, "Current fail-closed decision for the GADM boundary lead."),
    ]


def summary_row(metric: str, value: Any, interpretation: str) -> dict[str, str]:
    return {"metric": metric, "value": str(value), "interpretation": interpretation}


def markdown_rows(rows: list[dict[str, str]], columns: list[str], limit: int = 20) -> str:
    lines = ["| " + " | ".join(columns) + " |", "|" + "|".join("---" for _ in columns) + "|"]
    for row in rows[:limit]:
        values = []
        for column in columns:
            value = (row.get(column, "") or "").replace("|", "/")
            if len(value) > 100:
                value = value[:97] + "..."
            values.append(value)
        lines.append("| " + " | ".join(values) + " |")
    if len(rows) > limit:
        lines.append("| " + " | ".join(["..."] + [f"{len(rows) - limit} additional rows omitted"] + [""] * max(0, len(columns) - 2)) + " |")
    return "\n".join(lines)


def write_report(audit_rows: list[dict[str, str]], match_rows: list[dict[str, str]], summary: list[dict[str, str]]) -> None:
    summary_table = "\n".join(f"| {row['metric']} | {row['value']} | {row['interpretation']} |" for row in summary)
    duplicate_rows = [row for row in match_rows if row["match_status"] == "duplicate_boundary_key"]
    blocked_counts = Counter(row["suitability_status"] for row in audit_rows)
    status_table = "\n".join(f"| {key} | {value} |" for key, value in blocked_counts.items())
    REPORT_PATH.write_text(
        f"""# ALB_2002 GADM Boundary Lead Audit

Status: fail-closed source audit. This checks whether public GADM Albania ADM2 shapefiles can resolve the ALB_2002 district-boundary blocker.

## Summary

| Metric | Value | Interpretation |
|---|---:|---|
{summary_table}

## Source Status

| Suitability status | Count |
|---|---:|
{status_table}

## Candidate Rows

{markdown_rows(audit_rows, ['candidate_id', 'download_status', 'adm2_row_count', 'adm2_distinct_normalized_key_count', 'adm2_engtype_district_rows', 'complete_name_coverage', 'duplicate_boundary_key_count', 'climate_linkage_ready', 'suitability_status'])}

## Duplicate Boundary Keys

{markdown_rows(duplicate_rows, ['candidate_id', 'survey_district_key', 'boundary_gid', 'boundary_name_1', 'boundary_name_2', 'boundary_type_2', 'boundary_engtype_2', 'notes']) if duplicate_rows else 'No duplicate normalized boundary keys were found.'}

## Interpretation

- GADM 3.6 is a stronger public lead than current-boundary sources because its ADM2 rows are labeled `Rreth` / `District` and the normalized names cover the ALB_2002 district keys after documented encoding and genitive-name repairs.
- The GADM 3.6 ADM2 table still has 37 feature rows and 36 normalized keys because `SHKODER` appears twice under different parent counties.
- GADM 4.1 also has 37 ADM2 rows, but its ADM2 type fields are `NA`, so it is not a clearer historical district source.
- Neither GADM snapshot provides verified official 2001/2002 boundary provenance, LSMS join-key documentation, or geometry validation in this audit.
- Historical-boundary-ready rows and climate-linkage-ready rows remain zero.

## Machine-Readable Outputs

- `temp/alb2002_gadm_boundary_lead_audit.csv`
- `temp/alb2002_gadm_boundary_name_match_audit.csv`
- `result/alb2002_gadm_boundary_lead_summary.csv`
- `temp/source_snapshots/gadm36_ALB_shp.zip`
- `temp/source_snapshots/gadm41_ALB_shp.zip`
""",
        encoding="utf-8",
    )


def main() -> None:
    ensure_dirs()
    audit_rows, match_rows, summary = build_audit()
    write_csv(AUDIT_PATH, audit_rows, AUDIT_COLUMNS)
    write_csv(MATCH_PATH, match_rows, MATCH_COLUMNS)
    write_csv(SUMMARY_PATH, summary, SUMMARY_COLUMNS)
    write_report(audit_rows, match_rows, summary)
    append_log(TEMP_DIR / "audit_log.md", f"Built ALB_2002 GADM boundary lead audit candidates={len(audit_rows)} decision={DECISION}.")
    print(f"ALB_2002 GADM boundary lead audit candidates={len(audit_rows)} decision={DECISION}.")


if __name__ == "__main__":
    main()
