from __future__ import annotations

import csv
import re
import shutil
import subprocess
from pathlib import Path
from typing import Any

from common import REPORT_DIR, RESULT_DIR, TEMP_DIR, append_log, ensure_dirs, write_csv


IDNO = "ALB_2005_LSMS_v01_M"
COUNTRY = "Albania"
SURVEY_NAME = "Living Standards Measurement Survey 2005"

SCHEMA_FILE_PATH = TEMP_DIR / "raw_schema_inventory" / "Albania_2005_ALB_2005_LSMS_v01_M" / "Albania_2005_ALB_2005_LSMS_v01_M_schema_files.csv"
VARIABLE_CATALOG_PATH = TEMP_DIR / "raw_schema_inventory" / "Albania_2005_ALB_2005_LSMS_v01_M" / "Albania_2005_ALB_2005_LSMS_v01_M_variable_catalog.csv"
ARCHIVE_PATH = TEMP_DIR / "raw_downloads" / "ALB_2005_LSMS_v01_M" / "lsms2005en.rar"
RAW_EXTRACTED_ROOT = TEMP_DIR / "raw_extracted" / "lsms2005en_1e7f1965c4a5" / "lsms2005en" / "Data_2005"

AUDIT_PATH = TEMP_DIR / "alb2005_extracted_module_coverage_audit.csv"
EXTRA_PATH = TEMP_DIR / "alb2005_extracted_extra_files_audit.csv"
ARCHIVE_MANIFEST_PATH = TEMP_DIR / "alb2005_archive_member_manifest.csv"
SUMMARY_PATH = RESULT_DIR / "alb2005_extracted_module_coverage_summary.csv"
REPORT_PATH = REPORT_DIR / "alb2005_extracted_module_coverage_audit.md"

DECISION = "blocked_extracted_package_missing_bookmetadata_and_coordinate_values"

AUDIT_COLUMNS = [
    "country",
    "idno",
    "fid",
    "ddi_file_name",
    "ddi_cases",
    "ddi_variable_count",
    "module_role",
    "expected_for",
    "coverage_status",
    "matched_extracted_file",
    "matched_extracted_bytes",
    "archive_coverage_status",
    "matched_archive_member",
    "blocking_implication",
    "required_next_evidence",
]
EXTRA_COLUMNS = [
    "extracted_file",
    "normalized_name",
    "bytes",
    "coverage_status",
    "notes",
]
ARCHIVE_COLUMNS = [
    "country",
    "idno",
    "archive_path",
    "member_path",
    "member_name",
    "member_ext",
    "normalized_name",
    "archive_member_type",
]
SUMMARY_COLUMNS = ["metric", "value", "interpretation"]

CRITICAL_ROLE_BY_NAME = {
    "bookmetadata_cl": ("diary_timing", "household timing candidate merge review"),
    "bookdaily_cl": ("food_diary_consumption", "consumption denominator reconstruction review"),
    "bookfoodeaten_cl": ("food_diary_consumption", "consumption denominator reconstruction review"),
    "bookchecklist_cl": ("food_diary_consumption", "consumption denominator reconstruction review"),
    "bookbread_cl": ("food_diary_consumption", "consumption denominator reconstruction review"),
    "booknonpurchased_cl": ("food_diary_consumption", "consumption denominator reconstruction review"),
    "weights_cl": ("survey_design", "survey design/weight review"),
    "weights_psu": ("survey_design", "survey design/PSU review"),
    "community_all": ("community_context", "community context review"),
}


def read_csv_dicts(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        return []
    with path.open(encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def safe_int(value: Any) -> int:
    try:
        return int(float(str(value).strip()))
    except (TypeError, ValueError):
        return 0


def normalize_name(value: str) -> str:
    stem = Path(value).stem.lower()
    stem = re.sub(r"[^a-z0-9_]+", "_", stem)
    stem = re.sub(r"_+", "_", stem).strip("_")
    stem = re.sub(r"^modul_\d+[a-z]?_", "", stem)
    stem = re.sub(r"^module_\d+[a-z]?_", "", stem)
    return stem


def extracted_files() -> list[Path]:
    if not RAW_EXTRACTED_ROOT.exists():
        return []
    return sorted(path for path in RAW_EXTRACTED_ROOT.glob("*.sav") if path.is_file())


def archive_members() -> list[str]:
    tar = shutil.which("tar")
    if not tar or not ARCHIVE_PATH.exists():
        return []
    try:
        proc = subprocess.run(
            [tar, "-tf", str(ARCHIVE_PATH)],
            check=False,
            capture_output=True,
            text=True,
            timeout=60,
        )
    except (OSError, subprocess.SubprocessError):
        return []
    if proc.returncode != 0:
        return []
    return [line.strip() for line in proc.stdout.splitlines() if line.strip()]


def archive_manifest_rows(members: list[str]) -> list[dict[str, str]]:
    rows = []
    for member in members:
        name = Path(member).name
        ext = Path(name).suffix.lower()
        if ext in {".sav", ".xls", ".xlsx", ".dta", ".csv"}:
            member_type = "candidate_data_or_document_file"
        else:
            member_type = "directory_or_container_marker"
        rows.append(
            {
                "country": COUNTRY,
                "idno": IDNO,
                "archive_path": ARCHIVE_PATH.relative_to(TEMP_DIR.parent).as_posix(),
                "member_path": member,
                "member_name": name,
                "member_ext": ext,
                "normalized_name": normalize_name(name),
                "archive_member_type": member_type,
            }
        )
    return rows


def module_role(name: str) -> tuple[str, str]:
    norm = normalize_name(name)
    if norm in CRITICAL_ROLE_BY_NAME:
        return CRITICAL_ROLE_BY_NAME[norm]
    if norm.startswith("health"):
        return "health_outcome", "OOP/access outcome review"
    if "non_food_expenditures" in norm or norm == "poverty":
        return "consumption_denominator", "financial protection denominator review"
    if "migration" in norm or "shock" in norm:
        return "shock_or_migration", "mechanism/covariate review"
    if "roster" in norm or norm in {"filters", "filters_cl"}:
        return "household_frame", "household frame/key review"
    if "education" in norm or "labour" in norm or "dwelling" in norm:
        return "covariates", "covariate review"
    return "other", "manual review if needed"


def build_audit() -> tuple[list[dict[str, str]], list[dict[str, str]], list[dict[str, str]], list[dict[str, str]]]:
    schema_rows = [row for row in read_csv_dicts(SCHEMA_FILE_PATH) if row.get("idno") == IDNO]
    variables = [row for row in read_csv_dicts(VARIABLE_CATALOG_PATH) if row.get("idno") == IDNO]
    extracted = extracted_files()
    archive_manifest = archive_manifest_rows(archive_members())
    extracted_by_norm: dict[str, Path] = {normalize_name(path.name): path for path in extracted}
    archive_by_norm: dict[str, str] = {
        row["normalized_name"]: row["member_path"]
        for row in archive_manifest
        if row["member_ext"] == ".sav"
    }
    matched_norms: set[str] = set()

    rows = []
    for row in schema_rows:
        ddi_name = row.get("file_name", "")
        norm = normalize_name(ddi_name)
        role, expected_for = module_role(ddi_name)
        match = extracted_by_norm.get(norm)
        archive_match = archive_by_norm.get(norm, "")
        if match:
            matched_norms.add(norm)
            status = "extracted_file_present"
            implication = "Module is present in the extracted ALB_2005 package; downstream value/merge review may still block promotion."
            required = "Run or review module-specific raw-value and merge audits before using this module in a recipe."
        elif archive_match:
            status = "archive_member_present_not_extracted"
            implication = "DDI module is visible in the local archive manifest but not in the extracted folder, so extraction should be rerun or checked before promotion."
            required = "Re-extract the archive and rerun raw schema inspection before using this module."
        else:
            status = "ddi_module_missing_from_extracted_package"
            if norm == "bookmetadata_cl":
                implication = "Diary beginning/finishing date candidates are in public metadata but the raw bookmetadata file is absent from both the local archive manifest and extracted folder, so household timing cannot be promoted."
                required = "Obtain the raw bookmetadata_cl file or official equivalent, then verify hhid/PSU merge coverage and diary timing semantics."
            elif role == "food_diary_consumption":
                implication = "Food diary source module is absent locally, limiting component-level consumption reconstruction from raw item records."
                required = "Obtain the missing food diary module or document why the survey-provided aggregate can be used without component reconstruction."
            elif role == "survey_design":
                implication = "DDI-listed design/weight module is absent under this exact module name; alternate local weight files require separate review."
                required = "Verify whether local weight files are official substitutes and how they merge to household rows."
            else:
                implication = "DDI module is not present in the extracted package; keep it out of recipes unless separately obtained."
                required = "Obtain the module or document exclusion from analytical recipes."
        rows.append(
            {
                "country": COUNTRY,
                "idno": IDNO,
                "fid": row.get("fid", ""),
                "ddi_file_name": ddi_name,
                "ddi_cases": row.get("cases", ""),
                "ddi_variable_count": row.get("variable_count", ""),
                "module_role": role,
                "expected_for": expected_for,
                "coverage_status": status,
                "matched_extracted_file": match.name if match else "",
                "matched_extracted_bytes": str(match.stat().st_size) if match else "",
                "archive_coverage_status": "archive_member_present" if archive_match else "absent_from_local_archive_manifest",
                "matched_archive_member": archive_match,
                "blocking_implication": implication,
                "required_next_evidence": required,
            }
        )

    extras = []
    schema_norms = {normalize_name(row.get("file_name", "")) for row in schema_rows}
    for path in extracted:
        norm = normalize_name(path.name)
        if norm in schema_norms:
            continue
        extras.append(
            {
                "extracted_file": path.name,
                "normalized_name": norm,
                "bytes": str(path.stat().st_size),
                "coverage_status": "extracted_file_not_matched_to_ddi_schema_file_name",
                "notes": "Useful local raw file but not matched by normalized DDI file name; review before using as official substitute.",
            }
        )

    variable_names = {row.get("variable_name", "").lower() for row in variables}
    coordinate_variable_rows = sum(
        1
        for row in variables
        if any(token in (row.get("variable_name", "") + " " + row.get("variable_label", "")).lower() for token in ["longitude", "latitude", "gps", "coordinate"])
    )
    coordinate_extracted_files = sum(1 for path in extracted if any(token in path.name.lower() for token in ["coord", "gps", "lat", "long"]))
    archive_sav_members = [row for row in archive_manifest if row["member_ext"] == ".sav"]
    archive_questionnaire_members = [row for row in archive_manifest if row["member_ext"] in {".xls", ".xlsx"}]
    archive_present = sum(1 for row in rows if row["archive_coverage_status"] == "archive_member_present")
    archive_absent = sum(1 for row in rows if row["archive_coverage_status"] == "absent_from_local_archive_manifest")
    archive_critical_absent = sum(
        1
        for row in rows
        if row["module_role"] in {"diary_timing", "food_diary_consumption", "survey_design"}
        and row["archive_coverage_status"] == "absent_from_local_archive_manifest"
    )
    archive_listing_status = "tar_listing_available" if archive_manifest else "archive_listing_unavailable"
    bookmetadata_missing = sum(1 for row in rows if normalize_name(row["ddi_file_name"]) == "bookmetadata_cl" and row["coverage_status"] != "extracted_file_present")
    food_diary_missing = sum(1 for row in rows if row["module_role"] == "food_diary_consumption" and row["coverage_status"] != "extracted_file_present")
    critical_missing = sum(1 for row in rows if row["module_role"] in {"diary_timing", "food_diary_consumption", "survey_design"} and row["coverage_status"] != "extracted_file_present")
    summary = [
        summary_row("alb2005_extracted_module_coverage_ddi_module_rows", len(rows), "DDI/schema modules checked against the extracted ALB_2005 package."),
        summary_row("alb2005_archive_member_rows", len(archive_manifest), "Members listed directly from the local ALB_2005 RAR archive."),
        summary_row("alb2005_archive_sav_member_rows", len(archive_sav_members), "SPSS .sav members listed directly from the local ALB_2005 RAR archive."),
        summary_row("alb2005_archive_questionnaire_member_rows", len(archive_questionnaire_members), "Questionnaire workbook members listed directly from the local ALB_2005 RAR archive."),
        summary_row("alb2005_archive_ddi_module_present_rows", archive_present, "DDI/schema modules present in the local archive manifest."),
        summary_row("alb2005_archive_ddi_module_absent_rows", archive_absent, "DDI/schema modules absent from the local archive manifest."),
        summary_row("alb2005_archive_critical_module_absent_rows", archive_critical_absent, "Critical timing/food-diary/design DDI modules absent from the local archive manifest."),
        summary_row("alb2005_archive_listing_status", archive_listing_status, "Whether the local ALB_2005 archive member list was readable."),
        summary_row("alb2005_extracted_module_coverage_present_rows", sum(1 for row in rows if row["coverage_status"] == "extracted_file_present"), "DDI modules with a normalized extracted file match."),
        summary_row("alb2005_extracted_module_coverage_missing_rows", sum(1 for row in rows if row["coverage_status"] != "extracted_file_present"), "DDI modules missing from the extracted ALB_2005 package."),
        summary_row("alb2005_extracted_module_coverage_extracted_file_rows", len(extracted), "Extracted .sav files under the ALB_2005 Data_2005 folder."),
        summary_row("alb2005_extracted_module_coverage_extra_extracted_rows", len(extras), "Extracted .sav files not matched to a normalized DDI file name."),
        summary_row("alb2005_extracted_module_coverage_bookmetadata_missing_rows", bookmetadata_missing, "Whether DDI `bookmetadata_cl` is missing from the extracted package."),
        summary_row("alb2005_extracted_module_coverage_food_diary_missing_rows", food_diary_missing, "Missing DDI food-diary modules relevant to consumption component reconstruction."),
        summary_row("alb2005_extracted_module_coverage_critical_missing_rows", critical_missing, "Missing timing/food-diary/design modules that require follow-up before recipe promotion."),
        summary_row("alb2005_extracted_module_coverage_coordinate_metadata_variable_rows", coordinate_variable_rows, "Coordinate/GPS variable candidates found in the ALB_2005 metadata variable catalog."),
        summary_row("alb2005_extracted_module_coverage_coordinate_extracted_file_rows", coordinate_extracted_files, "Extracted files whose names suggest coordinate/GPS content."),
        summary_row("alb2005_extracted_module_coverage_harmonized_ready_rows", 0, "Rows promoted to harmonized analytical data by this audit; intentionally zero."),
        summary_row("alb2005_extracted_module_coverage_household_timing_ready_rows", 0, "Rows promoted to verified household timing by this audit; intentionally zero."),
        summary_row("alb2005_extracted_module_coverage_climate_linkage_ready_rows", 0, "Rows ready for climate linkage after this audit; intentionally zero."),
        summary_row("alb2005_extracted_module_coverage_current_decision", DECISION, "Current fail-closed decision for ALB_2005 extracted module coverage."),
    ]
    return rows, extras, archive_manifest, summary


def summary_row(metric: str, value: Any, interpretation: str) -> dict[str, str]:
    return {"metric": metric, "value": str(value), "interpretation": interpretation}


def markdown_rows(rows: list[dict[str, str]], columns: list[str], limit: int = 25) -> str:
    lines = ["| " + " | ".join(columns) + " |", "|" + "|".join("---" for _ in columns) + "|"]
    for row in rows[:limit]:
        values = []
        for column in columns:
            value = (row.get(column, "") or "").replace("|", "/")
            if len(value) > 105:
                value = value[:102] + "..."
            values.append(value)
        lines.append("| " + " | ".join(values) + " |")
    if len(rows) > limit:
        omitted = ["..."] + [f"{len(rows) - limit} additional rows omitted from report preview"] + [""] * max(0, len(columns) - 2)
        lines.append("| " + " | ".join(omitted[: len(columns)]) + " |")
    return "\n".join(lines)


def write_report(rows: list[dict[str, str]], extras: list[dict[str, str]], archive_manifest: list[dict[str, str]], summary: list[dict[str, str]]) -> None:
    summary_table = "\n".join(f"| {row['metric']} | {row['value']} | {row['interpretation']} |" for row in summary)
    missing = [row for row in rows if row["coverage_status"] != "extracted_file_present"]
    critical = [row for row in missing if row["module_role"] in {"diary_timing", "food_diary_consumption", "survey_design"}]
    archive_files = [row for row in archive_manifest if row["archive_member_type"] == "candidate_data_or_document_file"]
    REPORT_PATH.write_text(
        f"""# ALB_2005 Extracted Module Coverage Audit

Status: fail-closed extracted-module coverage audit. This compares the ALB_2005 public DDI/schema module list with both the local archive manifest and the extracted local `.sav` files under `temp/raw_extracted/lsms2005en_1e7f1965c4a5/lsms2005en/Data_2005/`.

## Summary

| Metric | Value | Interpretation |
|---|---:|---|
{summary_table}

## Critical Missing Modules

{markdown_rows(critical, ['fid', 'ddi_file_name', 'module_role', 'expected_for', 'coverage_status', 'archive_coverage_status', 'blocking_implication']) if critical else 'No critical DDI modules are missing from the extracted package.'}

## Missing Module Preview

{markdown_rows(missing, ['fid', 'ddi_file_name', 'module_role', 'ddi_cases', 'ddi_variable_count', 'coverage_status', 'archive_coverage_status', 'required_next_evidence']) if missing else 'No DDI modules are missing from the extracted package.'}

## Extra Extracted Files

{markdown_rows(extras, ['extracted_file', 'normalized_name', 'bytes', 'coverage_status', 'notes']) if extras else 'No extra extracted files were found outside normalized DDI module names.'}

## Archive File Members

{markdown_rows(archive_files, ['member_path', 'member_ext', 'normalized_name', 'archive_member_type'], 60) if archive_files else 'No candidate data or questionnaire files were listed from the local archive.'}

## Interpretation

- The local archive manifest and extracted package both contain many core household, health, expenditure, poverty, and weight files, but they do not contain the DDI `bookmetadata_cl` module needed to verify diary beginning/finishing dates from raw values.
- The missing critical DDI modules are therefore not only an extraction-folder mismatch in the current workspace; they are also absent from the local archive member list.
- Public metadata therefore remains useful for identifying timing leads, but cannot be used to promote household interview timing.
- No extracted file name or metadata variable currently verifies household coordinates, despite the public DDI GPS statement.
- This audit does not write to `data/` and does not promote harmonized, household-timing, outcome, or climate-linkage rows.

## Machine-Readable Outputs

- `temp/alb2005_extracted_module_coverage_audit.csv`
- `temp/alb2005_extracted_extra_files_audit.csv`
- `temp/alb2005_archive_member_manifest.csv`
- `result/alb2005_extracted_module_coverage_summary.csv`
""",
        encoding="utf-8",
    )


def main() -> None:
    ensure_dirs()
    rows, extras, archive_manifest, summary = build_audit()
    write_csv(AUDIT_PATH, rows, AUDIT_COLUMNS)
    write_csv(EXTRA_PATH, extras, EXTRA_COLUMNS)
    write_csv(ARCHIVE_MANIFEST_PATH, archive_manifest, ARCHIVE_COLUMNS)
    write_csv(SUMMARY_PATH, summary, SUMMARY_COLUMNS)
    write_report(rows, extras, archive_manifest, summary)
    append_log(TEMP_DIR / "audit_log.md", f"Built ALB_2005 extracted module coverage audit modules={len(rows)} decision={DECISION}.")
    print(f"ALB_2005 extracted module coverage audit modules={len(rows)} decision={DECISION}.")


if __name__ == "__main__":
    main()
