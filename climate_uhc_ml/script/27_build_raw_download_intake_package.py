from __future__ import annotations

import csv
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

from common import PROJECT_ROOT, REPORT_DIR, RESULT_DIR, TEMP_DIR, append_log, ensure_dirs, write_csv


RAW_ROOT = TEMP_DIR / "raw_downloads"
INTAKE_PATH = TEMP_DIR / "raw_download_intake_manifest.csv"
EXPECTED_PATH = TEMP_DIR / "raw_download_expected_files.csv"
SUMMARY_PATH = RESULT_DIR / "raw_download_intake_summary.csv"
REPORT_PATH = REPORT_DIR / "raw_download_intake_plan.md"

DOCUMENTATION_EXTENSIONS = {".pdf", ".doc", ".docx", ".rtf", ".html", ".htm", ".md", ".xml", ".json"}
ARCHIVE_EXTENSIONS = {".zip", ".tar", ".gz", ".tgz", ".bz2", ".xz", ".7z", ".rar"}
RAW_TABULAR_EXTENSIONS = {".dta", ".sav", ".por", ".sas7bdat", ".xpt", ".csv", ".tsv", ".txt", ".xlsx", ".xls", ".parquet", ".feather"}

INTAKE_COLUMNS = [
    "action_rank",
    "source_name",
    "dataset_idno",
    "dataset",
    "account_or_access_url",
    "local_target_folder",
    "folder_readme",
    "folder_exists",
    "file_count",
    "raw_tabular_file_count",
    "archive_file_count",
    "documentation_file_count",
    "expected_module_rows",
    "expected_core_module_rows",
    "expected_exact_matches",
    "expected_stem_matches",
    "top_modules_to_verify_first",
    "intake_status",
    "next_action",
]

EXPECTED_COLUMNS = [
    "action_rank",
    "dataset_idno",
    "dataset",
    "local_target_folder",
    "expected_file_name",
    "module_priority_role",
    "candidate_categories",
    "candidate_harmonized_variables",
    "candidate_variable_count",
    "candidate_raw_variables_examples",
    "expected_file_status",
    "present_matching_files",
    "verification_action",
]

SUMMARY_COLUMNS = ["metric", "value", "interpretation"]


def read_csv_dicts(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        return []
    with path.open(encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def clean(value: Any) -> str:
    return "" if value is None else str(value).strip()


def safe_int(value: Any, default: int = 999999) -> int:
    try:
        return int(str(value).strip())
    except (TypeError, ValueError):
        return default


def compound_suffix(path: Path) -> str:
    name = path.name.lower()
    for suffix in [".tar.gz", ".tar.bz2", ".tar.xz"]:
        if name.endswith(suffix):
            return suffix
    return path.suffix.lower()


def normalize_name(value: str) -> str:
    name = value.strip().lower().replace("\\", "/").split("/")[-1]
    for suffix in [".tar.gz", ".tar.bz2", ".tar.xz"]:
        if name.endswith(suffix):
            return name[: -len(suffix)]
    suffix = Path(name).suffix
    if suffix:
        return name[: -len(suffix)]
    return name


def file_role(path: Path) -> str:
    suffix = compound_suffix(path)
    name = path.name.lower()
    if name.startswith("readme") or name.startswith("_readme") or name.startswith("_place_raw_files_here"):
        return "readme_or_instructions"
    if suffix in ARCHIVE_EXTENSIONS or suffix in {".tar.gz", ".tar.bz2", ".tar.xz"}:
        return "archive"
    if suffix in RAW_TABULAR_EXTENSIONS:
        return "raw_tabular_or_spreadsheet"
    if suffix in DOCUMENTATION_EXTENSIONS:
        return "documentation_or_metadata"
    return "other"


def actions() -> list[dict[str, str]]:
    merged: dict[str, dict[str, str]] = {}

    def key(row: dict[str, str]) -> str:
        idno = clean(row.get("dataset_idno") or row.get("idno"))
        if idno:
            return f"idno:{idno}"
        return f"source:{clean(row.get('source_name'))}:{clean(row.get('dataset'))}"

    def add(row: dict[str, str]) -> None:
        row_key = key(row)
        if row_key not in merged:
            merged[row_key] = row
            return
        existing = merged[row_key]
        for field, value in row.items():
            if not clean(existing.get(field)) and clean(value):
                existing[field] = value

    for row in read_csv_dicts(TEMP_DIR / "manual_access_action_queue.csv"):
        add(row)

    for row in read_csv_dicts(TEMP_DIR / "manual_download_priority.csv"):
        idno = row.get("idno", "")
        if not idno:
            continue
        add(
            {
                "action_rank": row.get("priority_rank", ""),
                "source_name": row.get("source_name", ""),
                "dataset_idno": idno,
                "dataset": row.get("dataset", ""),
                "account_or_access_url": row.get("official_url", ""),
                "official_url": row.get("official_url", ""),
                "local_target_folder": f"temp/raw_downloads/{idno}/",
                "key_modules_to_verify_first": "",
            }
        )

    for row in read_csv_dicts(TEMP_DIR / "metadata_quality_download_priority.csv"):
        idno = row.get("idno", "")
        if not idno:
            continue
        add(
            {
                "action_rank": row.get("manual_priority_rank") or str(1000 + safe_int(row.get("quality_rank"), 0)),
                "source_name": "World Bank Microdata Library",
                "dataset_idno": idno,
                "dataset": f"{row.get('country', '')} - {row.get('survey_name', '')} ({row.get('wave', '')}; {idno})",
                "account_or_access_url": row.get("official_url", ""),
                "official_url": row.get("official_url", ""),
                "local_target_folder": row.get("local_target_folder", f"temp/raw_downloads/{idno}/"),
                "key_modules_to_verify_first": "",
            }
        )
    return sorted(merged.values(), key=lambda row: (safe_int(row.get("action_rank")), row.get("dataset_idno", ""), row.get("dataset", "")))


def target_path(row: dict[str, str]) -> Path:
    folder = clean(row.get("local_target_folder") or row.get("target_folder"))
    folder = folder.replace("\\", "/").strip("/")
    if folder.startswith("temp/raw_downloads/"):
        return PROJECT_ROOT / folder
    if folder:
        return RAW_ROOT / folder
    idno = clean(row.get("dataset_idno"))
    return RAW_ROOT / idno


def relative(path: Path) -> str:
    return str(path.relative_to(PROJECT_ROOT)).replace("\\", "/")


def grouped_modules() -> dict[str, list[dict[str, str]]]:
    rows = read_csv_dicts(TEMP_DIR / "raw_ingestion_module_checklist.csv")
    if not rows:
        rows = read_csv_dicts(TEMP_DIR / "manual_download_file_checklist.csv")
    out: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in rows:
        idno = row.get("idno", "")
        if not idno:
            continue
        out[idno].append(row)
    for idno, items in out.items():
        items.sort(
            key=lambda row: (
                0 if row.get("module_priority_role") == "core_main_sample_module_candidate" else 1,
                -safe_int(row.get("candidate_variable_count"), 0),
                row.get("file_name", ""),
            )
        )
    return out


def folder_files(folder: Path) -> list[Path]:
    if not folder.exists():
        return []
    return sorted(path for path in folder.rglob("*") if path.is_file())


def match_expected(expected: str, files: list[Path]) -> tuple[str, str]:
    expected_clean = expected.strip().lower()
    expected_stem = normalize_name(expected)
    exact = [path for path in files if path.name.lower() == expected_clean]
    if exact:
        return "exact_file_present", ";".join(relative(path) for path in exact[:5])
    stem = [path for path in files if normalize_name(path.name) == expected_stem]
    if stem:
        return "stem_match_present", ";".join(relative(path) for path in stem[:5])
    archives = [path for path in files if file_role(path) == "archive"]
    if archives:
        return "archive_present_needs_schema_extraction", ";".join(relative(path) for path in archives[:5])
    return "not_present", ""


def markdown_table(rows: list[dict[str, str]], columns: list[str], limit: int = 15) -> str:
    lines = ["| " + " | ".join(columns) + " |", "|" + "|".join("---" for _ in columns) + "|"]
    for row in rows[:limit]:
        values = []
        for column in columns:
            value = clean(row.get(column, "")).replace("|", "/")
            if len(value) > 120:
                value = value[:117] + "..."
            values.append(value)
        lines.append("| " + " | ".join(values) + " |")
    return "\n".join(lines)


def top_modules_text(rows: list[dict[str, str]], limit: int = 10) -> str:
    parts = []
    for row in rows[:limit]:
        label = row.get("file_name", "")
        cats = row.get("candidate_categories", "")
        if label:
            parts.append(f"{label} [{cats}]")
    return "; ".join(parts)


def write_target_readme(action: dict[str, str], modules: list[dict[str, str]], folder: Path) -> Path:
    folder.mkdir(parents=True, exist_ok=True)
    idno = clean(action.get("dataset_idno")) or folder.name
    readme = folder / "_PLACE_RAW_FILES_HERE.md"
    module_rows = []
    for row in modules[:12]:
        module_rows.append(
            {
                "file": row.get("file_name", ""),
                "role": row.get("module_priority_role", row.get("download_status", "")),
                "categories": row.get("candidate_categories", ""),
                "examples": row.get("candidate_raw_variables_examples", ""),
            }
        )
    text = [
        f"# Raw Intake Folder: {idno}",
        "",
        f"Dataset: {clean(action.get('dataset'))}",
        "",
        f"Access URL: {clean(action.get('account_or_access_url') or action.get('official_url'))}",
        "",
        "Place the original downloaded raw archive(s), tabular file(s), and documentation for this dataset in this folder.",
        "",
        "Rules:",
        "",
        "- Keep original filenames and archives intact.",
        "- Download the full available package where terms permit; do not cherry-pick only the modules listed below.",
        "- Do not put raw files in `data/`.",
        "- Do not redistribute raw microdata.",
        "- After placing files here, run `powershell -ExecutionPolicy Bypass -File script/run_all.ps1` from the project root.",
        "",
        "First modules to verify after download:",
        "",
        "| File/module | Role | Categories | Example variables |",
        "|---|---|---|---|",
    ]
    if module_rows:
        for row in module_rows:
            text.append(f"| `{row['file']}` | {row['role']} | {row['categories']} | `{row['examples']}` |")
    else:
        text.append("| full raw package | pending metadata checklist | download all permitted raw and documentation files |  |")
    text.extend(
        [
            "",
            "Expected post-download checks:",
            "",
            "1. `temp/raw_download_file_manifest.csv` should show raw tabular or archive files in this target folder.",
            "2. `temp/raw_schema_inventory/raw_file_inventory.csv` should list inspected raw files after schema extraction.",
            "3. `temp/raw_schema_inventory/raw_variable_catalog.csv` should list raw variables and labels.",
            "4. `temp/harmonization_recipe.csv` should only be built after raw variables, units, recall periods, missing codes, and merge keys are verified.",
        ]
    )
    readme.write_text("\n".join(text) + "\n", encoding="utf-8")
    return readme


def write_root_readme(intake_rows: list[dict[str, str]]) -> Path:
    RAW_ROOT.mkdir(parents=True, exist_ok=True)
    readme = RAW_ROOT / "README_RAW_DATA_INTAKE.md"
    lines = [
        "# Raw Data Intake",
        "",
        "This folder is the only accepted location for original raw downloads. Keep raw data out of `data/`.",
        "",
        "Each target folder contains `_PLACE_RAW_FILES_HERE.md` with dataset-specific access URL, target folder, and first modules to verify.",
        "",
        "After adding files, run:",
        "",
        "```powershell",
        "powershell -ExecutionPolicy Bypass -File script/run_all.ps1",
        "```",
        "",
        "Current target summary:",
        "",
        markdown_table(intake_rows, ["action_rank", "dataset_idno", "intake_status", "local_target_folder"], 30),
    ]
    readme.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return readme


def build_outputs() -> tuple[list[dict[str, str]], list[dict[str, str]], list[dict[str, str]], int]:
    action_rows = actions()
    modules_by_idno = grouped_modules()
    intake_rows: list[dict[str, str]] = []
    expected_rows: list[dict[str, str]] = []
    readmes_written = 0

    for action in sorted(action_rows, key=lambda row: safe_int(row.get("action_rank"))):
        folder = target_path(action)
        idno = clean(action.get("dataset_idno")) or folder.name
        modules = modules_by_idno.get(idno, [])
        readme = write_target_readme(action, modules, folder)
        readmes_written += 1
        files = folder_files(folder)
        role_counts = Counter(file_role(path) for path in files)
        raw_count = role_counts.get("raw_tabular_or_spreadsheet", 0)
        archive_count = role_counts.get("archive", 0)
        doc_count = role_counts.get("documentation_or_metadata", 0) + role_counts.get("readme_or_instructions", 0)
        exact_count = 0
        stem_count = 0
        for module in modules:
            status, matches = match_expected(module.get("file_name", ""), files)
            if status == "exact_file_present":
                exact_count += 1
            if status == "stem_match_present":
                stem_count += 1
            expected_rows.append(
                {
                    "action_rank": action.get("action_rank", ""),
                    "dataset_idno": idno,
                    "dataset": action.get("dataset", ""),
                    "local_target_folder": relative(folder) + "/",
                    "expected_file_name": module.get("file_name", ""),
                    "module_priority_role": module.get("module_priority_role", module.get("download_status", "")),
                    "candidate_categories": module.get("candidate_categories", ""),
                    "candidate_harmonized_variables": module.get("candidate_harmonized_variables", ""),
                    "candidate_variable_count": module.get("candidate_variable_count", ""),
                    "candidate_raw_variables_examples": module.get("candidate_raw_variables_examples", ""),
                    "expected_file_status": status,
                    "present_matching_files": matches,
                    "verification_action": "inspect raw schema and verify units, labels, missing codes, recall periods, levels, and merge keys before harmonization",
                }
            )
        if raw_count or archive_count:
            intake_status = "ready_for_raw_schema_inspection"
            next_action = "run script/17_audit_raw_downloads.py and script/03_inspect_raw_schemas.py"
        elif files:
            intake_status = "instructions_or_documentation_only"
            next_action = "place original raw archives or tabular files in the target folder"
        else:
            intake_status = "waiting_for_download"
            next_action = "complete access/terms workflow and place original raw files here"
        intake_rows.append(
            {
                "action_rank": action.get("action_rank", ""),
                "source_name": action.get("source_name", ""),
                "dataset_idno": idno,
                "dataset": action.get("dataset", ""),
                "account_or_access_url": action.get("account_or_access_url", action.get("official_url", "")),
                "local_target_folder": relative(folder) + "/",
                "folder_readme": relative(readme),
                "folder_exists": "1" if folder.exists() else "0",
                "file_count": str(len(files)),
                "raw_tabular_file_count": str(raw_count),
                "archive_file_count": str(archive_count),
                "documentation_file_count": str(doc_count),
                "expected_module_rows": str(len(modules)),
                "expected_core_module_rows": str(sum(1 for row in modules if row.get("module_priority_role") == "core_main_sample_module_candidate")),
                "expected_exact_matches": str(exact_count),
                "expected_stem_matches": str(stem_count),
                "top_modules_to_verify_first": top_modules_text(modules, 8) or action.get("key_modules_to_verify_first", ""),
                "intake_status": intake_status,
                "next_action": next_action,
            }
        )
    write_root_readme(intake_rows)
    summary = summary_rows(intake_rows, expected_rows, readmes_written)
    return intake_rows, expected_rows, summary, readmes_written


def summary_rows(intake_rows: list[dict[str, str]], expected_rows: list[dict[str, str]], readmes_written: int) -> list[dict[str, str]]:
    intake_counts = Counter(row.get("intake_status", "") for row in intake_rows)
    expected_counts = Counter(row.get("expected_file_status", "") for row in expected_rows)
    rows = [
        {"metric": "raw_download_intake_targets", "value": str(len(intake_rows)), "interpretation": "Target folders with dataset-level intake instructions."},
        {"metric": "target_readmes_written", "value": str(readmes_written), "interpretation": "Per-target README files written under temp/raw_downloads."},
        {"metric": "expected_module_rows", "value": str(len(expected_rows)), "interpretation": "Metadata-derived module/file rows to check after download."},
        {"metric": "ready_for_raw_schema_inspection_targets", "value": str(intake_counts.get("ready_for_raw_schema_inspection", 0)), "interpretation": "Targets with raw tabular or archive files currently present."},
        {"metric": "instructions_or_documentation_only_targets", "value": str(intake_counts.get("instructions_or_documentation_only", 0)), "interpretation": "Targets containing only README/documentation files."},
        {"metric": "waiting_for_download_targets", "value": str(intake_counts.get("waiting_for_download", 0)), "interpretation": "Targets with no files yet."},
    ]
    for status, count in sorted(expected_counts.items()):
        rows.append({"metric": f"expected_file_status_{status}", "value": str(count), "interpretation": "Expected module/file matching status."})
    return rows


def write_report(intake_rows: list[dict[str, str]], expected_rows: list[dict[str, str]], summaries: list[dict[str, str]]) -> None:
    intake_counts = Counter(row.get("intake_status", "") for row in intake_rows)
    expected_counts = Counter(row.get("expected_file_status", "") for row in expected_rows)
    lines = [
        "# Raw Download Intake Plan",
        "",
        "Status: this package prepares target folders and file-level expectations for manual raw-data intake. It does not claim raw microdata are present unless raw tabular files or archives are detected.",
        "",
        "## Intake Status",
        "",
        "| Intake status | Count |",
        "|---|---:|",
    ]
    for status, count in sorted(intake_counts.items()):
        lines.append(f"| {status or 'blank'} | {count} |")
    lines.extend(["", "## Expected File Status", "", "| Expected file status | Count |", "|---|---:|"])
    for status, count in sorted(expected_counts.items()):
        lines.append(f"| {status or 'blank'} | {count} |")
    lines.extend(["", "## Summary Metrics", "", "| Metric | Value | Interpretation |", "|---|---:|---|"])
    for row in summaries:
        lines.append(f"| {row['metric']} | {row['value']} | {row['interpretation']} |")
    lines.extend(
        [
            "",
            "## First Target Folders",
            "",
            markdown_table(intake_rows, ["action_rank", "dataset_idno", "intake_status", "raw_tabular_file_count", "archive_file_count", "expected_core_module_rows", "local_target_folder"], 15),
            "",
            "## Required Action",
            "",
            "1. Complete the access, login, or terms workflow at the dataset URL.",
            "2. Download the full available raw package and documentation where permitted.",
            "3. Place original files in the listed target folder without renaming them.",
            "4. Run `powershell -ExecutionPolicy Bypass -File script/run_all.ps1`.",
            "5. Inspect `temp/raw_schema_inventory/raw_file_inventory.csv`, `temp/raw_schema_inventory/raw_variable_catalog.csv`, and `temp/harmonization_audit.csv` before building a harmonization recipe.",
            "",
            "## Machine-Readable Outputs",
            "",
            "- `temp/raw_download_intake_manifest.csv`",
            "- `temp/raw_download_expected_files.csv`",
            "- `result/raw_download_intake_summary.csv`",
            "- `temp/raw_downloads/README_RAW_DATA_INTAKE.md`",
        ]
    )
    REPORT_PATH.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    ensure_dirs()
    RAW_ROOT.mkdir(parents=True, exist_ok=True)
    intake_rows, expected_rows, summaries, readmes_written = build_outputs()
    write_csv(INTAKE_PATH, intake_rows, INTAKE_COLUMNS)
    write_csv(EXPECTED_PATH, expected_rows, EXPECTED_COLUMNS)
    write_csv(SUMMARY_PATH, summaries, SUMMARY_COLUMNS)
    write_report(intake_rows, expected_rows, summaries)
    ready = sum(1 for row in intake_rows if row.get("intake_status") == "ready_for_raw_schema_inspection")
    append_log(TEMP_DIR / "audit_log.md", f"Raw download intake package targets={len(intake_rows)} expected_rows={len(expected_rows)} readmes={readmes_written} ready_for_schema={ready}.")
    print(f"Raw download intake targets={len(intake_rows)} expected_rows={len(expected_rows)} readmes={readmes_written} ready_for_schema={ready}.")


if __name__ == "__main__":
    main()
