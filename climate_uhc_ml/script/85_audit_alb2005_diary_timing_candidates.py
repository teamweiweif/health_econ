from __future__ import annotations

import csv
import re
from pathlib import Path
from typing import Any

from common import REPORT_DIR, RESULT_DIR, TEMP_DIR, append_log, ensure_dirs, write_csv


IDNO = "ALB_2005_LSMS_v01_M"
COUNTRY = "Albania"
SURVEY_NAME = "Living Standards Measurement Survey 2005"

DDI_PATH = TEMP_DIR / "source_snapshots" / "first_batch_public_documentation" / "1_ALB_2005_LSMS_v01_M" / "metadata_ddi_xml.xml"
SCHEMA_FILE_PATH = TEMP_DIR / "raw_schema_inventory" / "Albania_2005_ALB_2005_LSMS_v01_M" / "Albania_2005_ALB_2005_LSMS_v01_M_schema_files.csv"
VARIABLE_CATALOG_PATH = TEMP_DIR / "raw_schema_inventory" / "Albania_2005_ALB_2005_LSMS_v01_M" / "Albania_2005_ALB_2005_LSMS_v01_M_variable_catalog.csv"
PUBLIC_FIELDWORK_SUMMARY_PATH = RESULT_DIR / "alb2005_public_fieldwork_geo_metadata_summary.csv"

AUDIT_PATH = TEMP_DIR / "alb2005_diary_timing_candidate_audit.csv"
SUMMARY_PATH = RESULT_DIR / "alb2005_diary_timing_candidate_summary.csv"
REPORT_PATH = REPORT_DIR / "alb2005_diary_timing_candidate_audit.md"

DECISION = "blocked_diary_timing_metadata_candidate_no_raw_merge_semantics"

AUDIT_COLUMNS = [
    "variable_name",
    "file_id",
    "file_name",
    "variable_label",
    "concept_role",
    "metadata_catalog_status",
    "ddi_line",
    "ddi_valid_count",
    "ddi_invalid_count",
    "ddi_min",
    "ddi_max",
    "ddi_categories",
    "candidate_use",
    "promotion_status",
    "required_next_evidence",
]
SUMMARY_COLUMNS = ["metric", "value", "interpretation"]


VARIABLE_SPECS = {
    "ma_q00": {
        "concept_role": "psu_key",
        "candidate_use": "Potential PSU key for linking diary timing metadata to the household frame.",
        "promotion_status": "candidate_key_not_merge_verified",
        "required_next_evidence": "Raw bookmetadata_cl values and merge cardinality against the accepted household frame.",
    },
    "ma_q01": {
        "concept_role": "household_id_component",
        "candidate_use": "Potential household ID component in bookmetadata_cl.",
        "promotion_status": "candidate_key_not_merge_verified",
        "required_next_evidence": "Raw key values, uniqueness checks, and reconciliation with hhid and household core IDs.",
    },
    "hhid": {
        "concept_role": "household_identifier",
        "candidate_use": "Potential household identifier in bookmetadata_cl.",
        "promotion_status": "candidate_key_not_merge_verified",
        "required_next_evidence": "Raw hhid values and one-to-one/one-to-many merge checks against household core rows.",
    },
    "ma_q04d": {
        "concept_role": "diary_beginning_day",
        "candidate_use": "Diary beginning day candidate, not automatically the household interview day.",
        "promotion_status": "candidate_diary_timing_not_interview_verified",
        "required_next_evidence": "Raw values, diary protocol review, and a documented rule translating diary dates into exposure timing if justified.",
    },
    "ma_q04m": {
        "concept_role": "diary_beginning_month",
        "candidate_use": "Diary beginning month candidate with May-July metadata categories.",
        "promotion_status": "candidate_diary_timing_not_interview_verified",
        "required_next_evidence": "Raw values, merge coverage, and confirmation that diary beginning month is acceptable for the chosen climate exposure window.",
    },
    "ma_q04y": {
        "concept_role": "diary_beginning_year",
        "candidate_use": "Diary beginning year candidate.",
        "promotion_status": "candidate_diary_timing_not_interview_verified",
        "required_next_evidence": "Raw values and merge coverage with household analysis rows.",
    },
    "ma_q05d": {
        "concept_role": "diary_finishing_day",
        "candidate_use": "Diary finishing day candidate, not automatically the household interview day.",
        "promotion_status": "candidate_diary_timing_not_interview_verified",
        "required_next_evidence": "Raw values, diary protocol review, and a documented rule for using finish date or midpoint date.",
    },
    "ma_q05m": {
        "concept_role": "diary_finishing_month",
        "candidate_use": "Diary finishing month candidate with May-July metadata categories.",
        "promotion_status": "candidate_diary_timing_not_interview_verified",
        "required_next_evidence": "Raw values, merge coverage, and confirmation that finishing month is acceptable for the chosen exposure window.",
    },
    "ma_q05y": {
        "concept_role": "diary_finishing_year",
        "candidate_use": "Diary finishing year candidate.",
        "promotion_status": "candidate_diary_timing_not_interview_verified",
        "required_next_evidence": "Raw values and merge coverage with household analysis rows.",
    },
    "ma_q08": {
        "concept_role": "verification_month",
        "candidate_use": "Verification month is all missing in DDI summary and is not a timing source.",
        "promotion_status": "rejected_all_missing_not_interview_timing",
        "required_next_evidence": "None unless raw values contradict DDI missingness, which must be proven from raw data.",
    },
    "ma_q09": {
        "concept_role": "verification_day",
        "candidate_use": "Verification day is all missing in DDI summary and is not a timing source.",
        "promotion_status": "rejected_all_missing_not_interview_timing",
        "required_next_evidence": "None unless raw values contradict DDI missingness, which must be proven from raw data.",
    },
}


def read_csv_dicts(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        return []
    with path.open(encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def metric_value(rows: list[dict[str, str]], metric: str, default: str = "0") -> str:
    return next((row.get("value", default) for row in rows if row.get("metric") == metric), default)


def safe_int(value: Any) -> int:
    try:
        return int(float(str(value).strip()))
    except (TypeError, ValueError):
        return 0


def read_lines(path: Path) -> list[str]:
    if not path.exists():
        return []
    return path.read_text(encoding="utf-8", errors="replace").splitlines()


def parse_var_blocks(lines: list[str]) -> dict[str, dict[str, str]]:
    blocks: dict[str, dict[str, str]] = {}
    idx = 0
    while idx < len(lines):
        line = lines[idx]
        match = re.search(r'<var ID="[^"]+" name="([^"]+)" files="([^"]+)"', line)
        if not match:
            idx += 1
            continue
        name, file_id = match.group(1), match.group(2)
        start_line = idx + 1
        block = [line]
        idx += 1
        while idx < len(lines):
            block.append(lines[idx])
            if "</var>" in lines[idx]:
                break
            idx += 1
        text = "\n".join(block)
        label = first_match(text, r"<labl>(.*?)</labl>")
        blocks[name] = {
            "file_id": file_id,
            "ddi_line": str(start_line),
            "variable_label": compact_xml_text(label),
            "valid": first_match(text, r'<sumStat type="vald">(.*?)</sumStat>'),
            "invalid": first_match(text, r'<sumStat type="invd">(.*?)</sumStat>'),
            "min": first_match(text, r'<sumStat type="min">(.*?)</sumStat>'),
            "max": first_match(text, r'<sumStat type="max">(.*?)</sumStat>'),
            "categories": category_summary(text),
        }
        idx += 1
    return blocks


def first_match(text: str, pattern: str) -> str:
    match = re.search(pattern, text, flags=re.S)
    return compact_xml_text(match.group(1)) if match else ""


def compact_xml_text(value: str) -> str:
    return " ".join((value or "").replace("&amp;", "&").split())


def category_summary(text: str) -> str:
    categories = []
    for cat in re.finditer(r"<catgry.*?>(.*?)</catgry>", text, flags=re.S):
        cat_text = cat.group(1)
        value = first_match(cat_text, r"<catValu>(.*?)</catValu>")
        label = first_match(cat_text, r"<labl>(.*?)</labl>")
        freq = first_match(cat_text, r'<catStat type="freq">(.*?)</catStat>')
        if value or label or freq:
            categories.append(f"{value}:{label}:{freq}")
    return "; ".join(categories[:12])


def file_rows() -> dict[str, dict[str, str]]:
    rows = read_csv_dicts(SCHEMA_FILE_PATH)
    return {row.get("fid", "") or row.get("file_id", ""): row for row in rows}


def catalog_rows() -> dict[str, dict[str, str]]:
    rows = read_csv_dicts(VARIABLE_CATALOG_PATH)
    return {row.get("variable_name", ""): row for row in rows if row.get("file_name") == "bookmetadata_cl"}


def raw_bookmetadata_present() -> bool:
    roots = [TEMP_DIR / "raw_downloads", TEMP_DIR / "raw_extracted"]
    return any(
        path.is_file() and "bookmetadata" in path.name.lower()
        for root in roots
        if root.exists()
        for path in root.rglob("*")
    )


def build_audit() -> tuple[list[dict[str, str]], list[dict[str, str]]]:
    lines = read_lines(DDI_PATH)
    blocks = parse_var_blocks(lines)
    files = file_rows()
    catalog = catalog_rows()
    f96 = files.get("F96", {})
    raw_present = raw_bookmetadata_present()

    rows = []
    for variable_name, spec in VARIABLE_SPECS.items():
        block = blocks.get(variable_name, {})
        catalog_row = catalog.get(variable_name, {})
        found_catalog = bool(catalog_row)
        found_ddi = bool(block)
        valid_count = safe_int(block.get("valid", "0"))
        rows.append(
            {
                "variable_name": variable_name,
                "file_id": block.get("file_id") or catalog_row.get("file_id", "F96"),
                "file_name": catalog_row.get("file_name", "bookmetadata_cl"),
                "variable_label": catalog_row.get("variable_label") or block.get("variable_label", ""),
                "concept_role": spec["concept_role"],
                "metadata_catalog_status": "metadata_catalog_and_ddi_found" if found_catalog and found_ddi else "metadata_or_ddi_missing",
                "ddi_line": block.get("ddi_line", ""),
                "ddi_valid_count": block.get("valid", ""),
                "ddi_invalid_count": block.get("invalid", ""),
                "ddi_min": block.get("min", ""),
                "ddi_max": block.get("max", ""),
                "ddi_categories": block.get("categories", ""),
                "candidate_use": spec["candidate_use"],
                "promotion_status": spec["promotion_status"] if not raw_present or valid_count > 0 else "rejected_zero_valid_metadata",
                "required_next_evidence": spec["required_next_evidence"],
            }
        )

    public_summary = read_csv_dicts(PUBLIC_FIELDWORK_SUMMARY_PATH)
    timing_candidate_rows = sum(1 for row in rows if row["concept_role"].startswith("diary_") and safe_int(row["ddi_valid_count"]) > 0)
    key_candidate_rows = sum(1 for row in rows if row["concept_role"] in {"psu_key", "household_id_component", "household_identifier"} and safe_int(row["ddi_valid_count"]) > 0)
    rejected_missing_rows = sum(1 for row in rows if row["promotion_status"].startswith("rejected"))
    metadata_found_rows = sum(1 for row in rows if row["metadata_catalog_status"] == "metadata_catalog_and_ddi_found")
    max_valid = max((safe_int(row["ddi_valid_count"]) for row in rows), default=0)
    summary = [
        summary_row("alb2005_diary_timing_candidate_audit_rows", len(rows), "Bookmetadata timing/key variable rows audited from metadata and DDI."),
        summary_row("alb2005_diary_timing_candidate_metadata_found_rows", metadata_found_rows, "Rows found in both the metadata variable catalog and saved DDI XML."),
        summary_row("alb2005_diary_timing_candidate_schema_file_rows", safe_int(f96.get("cases", "0") or f96.get("row_count", "0")), "F96 bookmetadata_cl row count from schema inventory metadata."),
        summary_row("alb2005_diary_timing_candidate_schema_variable_rows", safe_int(f96.get("variable_count", "0") or f96.get("column_count", "0")), "F96 bookmetadata_cl variable count from schema inventory metadata."),
        summary_row("alb2005_diary_timing_candidate_raw_bookmetadata_files_present", 1 if raw_present else 0, "Whether a raw bookmetadata file was found under temp/raw_downloads or temp/raw_extracted."),
        summary_row("alb2005_diary_timing_candidate_key_candidate_rows", key_candidate_rows, "PSU/household key candidates with nonzero DDI valid counts."),
        summary_row("alb2005_diary_timing_candidate_date_candidate_rows", timing_candidate_rows, "Diary beginning/finishing day/month/year candidates with nonzero DDI valid counts."),
        summary_row("alb2005_diary_timing_candidate_max_valid_count", max_valid, "Largest DDI valid count across candidate variables."),
        summary_row("alb2005_diary_timing_candidate_rejected_all_missing_rows", rejected_missing_rows, "Verification date fields rejected because DDI summary shows all missing or zero valid."),
        summary_row("alb2005_diary_timing_candidate_household_timing_promoted_rows", 0, "Rows promoted as household interview timing after this audit; intentionally zero."),
        summary_row("alb2005_diary_timing_candidate_climate_linkage_ready_rows", 0, "Rows ready for climate linkage after this audit; intentionally zero."),
        summary_row("alb2005_diary_timing_candidate_public_fieldwork_verified_rows", metric_value(public_summary, "alb2005_public_fieldwork_geo_metadata_verified_source_rows", "0"), "Verified public fieldwork/geography source rows from the upstream public metadata audit."),
        summary_row("alb2005_diary_timing_candidate_current_decision", DECISION, "Current fail-closed decision for diary timing candidates."),
    ]
    return rows, summary


def summary_row(metric: str, value: Any, interpretation: str) -> dict[str, str]:
    return {"metric": metric, "value": str(value), "interpretation": interpretation}


def markdown_rows(rows: list[dict[str, str]], columns: list[str]) -> str:
    lines = ["| " + " | ".join(columns) + " |", "|" + "|".join("---" for _ in columns) + "|"]
    for row in rows:
        values = []
        for column in columns:
            value = (row.get(column, "") or "").replace("|", "/")
            if len(value) > 110:
                value = value[:107] + "..."
            values.append(value)
        lines.append("| " + " | ".join(values) + " |")
    return "\n".join(lines)


def write_report(rows: list[dict[str, str]], summary: list[dict[str, str]]) -> None:
    summary_table = "\n".join(f"| {row['metric']} | {row['value']} | {row['interpretation']} |" for row in summary)
    REPORT_PATH.write_text(
        f"""# ALB_2005 Diary Timing Candidate Audit

Status: fail-closed timing-candidate audit. The saved DDI and metadata schema expose `bookmetadata_cl` date variables for diary beginning and finishing, with May-July 2005 metadata categories and 3,840 F96 metadata rows. These are useful timing candidates, but they are not promoted as household interview timing or climate-linkage inputs because no raw `bookmetadata_cl` file is present under `temp/raw_downloads` or `temp/raw_extracted`, merge coverage is not verified, and diary beginning/finishing dates are not automatically the household interview date.

## Summary

| Metric | Value | Interpretation |
|---|---:|---|
{summary_table}

## Candidate Variables

{markdown_rows(rows, ['variable_name', 'concept_role', 'ddi_valid_count', 'ddi_min', 'ddi_max', 'promotion_status', 'candidate_use'])}

## Interpretation

- `ma_q04d`, `ma_q04m`, and `ma_q04y` are diary beginning date candidates.
- `ma_q05d`, `ma_q05m`, and `ma_q05y` are diary finishing date candidates.
- `ma_q00`, `ma_q01`, and `hhid` are key candidates needed to merge diary timing to the household frame.
- `ma_q08` and `ma_q09` are rejected for this purpose because the DDI summary shows zero valid verification-date values.
- No timing variable is promoted until raw values, merge cardinality, diary protocol semantics, and exposure-window implications are reviewed.

## Machine-Readable Outputs

- `temp/alb2005_diary_timing_candidate_audit.csv`
- `result/alb2005_diary_timing_candidate_summary.csv`
""",
        encoding="utf-8",
    )


def main() -> None:
    ensure_dirs()
    rows, summary = build_audit()
    write_csv(AUDIT_PATH, rows, AUDIT_COLUMNS)
    write_csv(SUMMARY_PATH, summary, SUMMARY_COLUMNS)
    write_report(rows, summary)
    append_log(TEMP_DIR / "audit_log.md", f"Built ALB_2005 diary timing candidate audit rows={len(rows)} decision={DECISION}.")
    print(f"ALB_2005 diary timing candidate audit rows={len(rows)} decision={DECISION}.")


if __name__ == "__main__":
    main()
