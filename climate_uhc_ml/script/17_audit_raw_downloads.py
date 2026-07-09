from __future__ import annotations

import csv
from collections import Counter
from pathlib import Path

from common import PROJECT_ROOT, REPORT_DIR, TEMP_DIR, append_log, ensure_dirs, sha256_file, write_csv


RAW_ROOT = TEMP_DIR / "raw_downloads"
MANIFEST_PATH = TEMP_DIR / "raw_download_file_manifest.csv"
TARGET_AUDIT_PATH = TEMP_DIR / "raw_download_target_audit.csv"
REPORT_PATH = REPORT_DIR / "raw_download_audit.md"

RAW_TABULAR_EXTENSIONS = {
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

ARCHIVE_EXTENSIONS = {
    ".zip",
    ".tar",
    ".gz",
    ".tgz",
    ".bz2",
    ".xz",
    ".7z",
    ".rar",
}

DOCUMENTATION_EXTENSIONS = {
    ".pdf",
    ".doc",
    ".docx",
    ".rtf",
    ".html",
    ".htm",
    ".md",
    ".xml",
    ".json",
}

MANIFEST_COLUMNS = [
    "relative_path",
    "target_dataset_idno",
    "target_folder",
    "inside_expected_target",
    "file_name",
    "extension",
    "file_role",
    "supported_by_schema_inspector",
    "file_size_bytes",
    "sha256",
    "status",
    "notes",
]

TARGET_COLUMNS = [
    "action_rank",
    "source_name",
    "dataset_idno",
    "dataset",
    "target_folder",
    "folder_exists",
    "file_count",
    "raw_tabular_file_count",
    "archive_file_count",
    "documentation_file_count",
    "total_bytes",
    "status",
    "notes",
]


def read_csv_dicts(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        return []
    with path.open(encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def is_relative_to(path: Path, parent: Path) -> bool:
    try:
        path.resolve().relative_to(parent.resolve())
    except ValueError:
        return False
    return True


def compound_suffix(path: Path) -> str:
    name = path.name.lower()
    for suffix in [".tar.gz", ".tar.bz2", ".tar.xz"]:
        if name.endswith(suffix):
            return suffix
    return path.suffix.lower()


def file_role(path: Path) -> str:
    suffix = compound_suffix(path)
    name = path.name.lower()
    if name == "readme.md" or name.startswith("readme"):
        return "readme_or_instructions"
    if suffix in ARCHIVE_EXTENSIONS or suffix in {".tar.gz", ".tar.bz2", ".tar.xz"}:
        return "archive"
    if suffix in RAW_TABULAR_EXTENSIONS:
        return "raw_tabular_or_spreadsheet"
    if suffix in DOCUMENTATION_EXTENSIONS:
        return "documentation_or_metadata"
    return "other"


def supported_by_schema_inspector(path: Path) -> str:
    role = file_role(path)
    suffix = compound_suffix(path)
    if role in {"archive", "raw_tabular_or_spreadsheet"}:
        if suffix in {".7z", ".rar"}:
            return "partial_archive_not_auto_extracted"
        return "1"
    return "0"


def expected_targets() -> list[dict[str, str]]:
    intake = read_csv_dicts(TEMP_DIR / "raw_download_intake_manifest.csv")
    if intake:
        return [
            {
                "action_rank": row.get("action_rank", ""),
                "source_name": row.get("source_name", ""),
                "dataset_idno": row.get("dataset_idno", ""),
                "dataset": row.get("dataset", ""),
                "local_target_folder": row.get("local_target_folder", ""),
            }
            for row in intake
        ]
    actions = read_csv_dicts(TEMP_DIR / "manual_access_action_queue.csv")
    if actions:
        return actions
    priority = read_csv_dicts(TEMP_DIR / "manual_download_priority.csv")
    out = []
    for row in priority:
        idno = row.get("idno", "")
        if not idno:
            continue
        out.append(
            {
                "action_rank": row.get("priority_rank", ""),
                "source_name": row.get("source_name", ""),
                "dataset_idno": idno,
                "dataset": row.get("dataset", ""),
                "local_target_folder": f"temp/raw_downloads/{idno}/",
            }
        )
    return out


def target_path(row: dict[str, str]) -> Path:
    folder = row.get("local_target_folder") or row.get("target_folder") or ""
    folder = folder.replace("\\", "/").strip("/")
    if folder.startswith("temp/raw_downloads/"):
        return PROJECT_ROOT / folder
    return RAW_ROOT / folder


def match_target(path: Path, targets: list[dict[str, str]]) -> tuple[str, str, str]:
    for row in targets:
        folder = target_path(row)
        if is_relative_to(path, folder):
            return row.get("dataset_idno", ""), str(folder.relative_to(PROJECT_ROOT)).replace("\\", "/") + "/", "1"
    return "", "", "0"


def iter_files() -> list[Path]:
    if not RAW_ROOT.exists():
        return []
    return sorted(path for path in RAW_ROOT.rglob("*") if path.is_file())


def build_manifest(files: list[Path], targets: list[dict[str, str]]) -> list[dict[str, str]]:
    rows = []
    for path in files:
        idno, folder, inside = match_target(path, targets)
        role = file_role(path)
        rows.append(
            {
                "relative_path": str(path.relative_to(PROJECT_ROOT)).replace("\\", "/"),
                "target_dataset_idno": idno,
                "target_folder": folder,
                "inside_expected_target": inside,
                "file_name": path.name,
                "extension": compound_suffix(path),
                "file_role": role,
                "supported_by_schema_inspector": supported_by_schema_inspector(path),
                "file_size_bytes": str(path.stat().st_size),
                "sha256": sha256_file(path),
                "status": "present",
                "notes": "Root README/instructions are not raw microdata." if path.name.lower().startswith("readme") else "",
            }
        )
    return rows


def target_audit_rows(targets: list[dict[str, str]], files: list[Path]) -> list[dict[str, str]]:
    rows = []
    for row in targets:
        folder = target_path(row)
        folder_files = [path for path in files if is_relative_to(path, folder)]
        role_counts = Counter(file_role(path) for path in folder_files)
        total_bytes = sum(path.stat().st_size for path in folder_files)
        raw_count = role_counts.get("raw_tabular_or_spreadsheet", 0)
        archive_count = role_counts.get("archive", 0)
        doc_count = role_counts.get("documentation_or_metadata", 0) + role_counts.get("readme_or_instructions", 0)
        if raw_count or archive_count:
            status = "raw_or_archive_files_present"
            notes = "Run script/03_inspect_raw_schemas.py to inspect supported tabular files and archive members."
        elif folder_files:
            status = "documentation_only_present"
            notes = "Documentation exists, but no raw tabular/archive files are present."
        elif folder.exists():
            status = "folder_exists_empty"
            notes = "Place original raw downloads here."
        else:
            status = "folder_missing"
            notes = "Create this folder when downloading the dataset."
        rows.append(
            {
                "action_rank": row.get("action_rank", ""),
                "source_name": row.get("source_name", ""),
                "dataset_idno": row.get("dataset_idno", ""),
                "dataset": row.get("dataset", ""),
                "target_folder": str(folder.relative_to(PROJECT_ROOT)).replace("\\", "/") + "/",
                "folder_exists": "1" if folder.exists() else "0",
                "file_count": str(len(folder_files)),
                "raw_tabular_file_count": str(raw_count),
                "archive_file_count": str(archive_count),
                "documentation_file_count": str(doc_count),
                "total_bytes": str(total_bytes),
                "status": status,
                "notes": notes,
            }
        )
    return rows


def markdown_count_table(counter: Counter[str], key_name: str) -> str:
    lines = [f"| {key_name} | Count |", "|---|---:|"]
    for key, count in counter.most_common():
        lines.append(f"| {key or 'blank'} | {count} |")
    return "\n".join(lines)


def write_report(manifest_rows: list[dict[str, str]], target_rows: list[dict[str, str]]) -> None:
    role_counts = Counter(row.get("file_role", "") for row in manifest_rows)
    target_status_counts = Counter(row.get("status", "") for row in target_rows)
    raw_like_targets = sum(1 for row in target_rows if row.get("status") == "raw_or_archive_files_present")
    lines = [
        "# Raw Download Audit",
        "",
        "Status: this audit checks files placed under `temp/raw_downloads/`; it does not claim that raw microdata are available unless raw tabular files or raw archives are present in expected target folders.",
        "",
        "## File Manifest",
        "",
        f"- Files under `temp/raw_downloads/`: {len(manifest_rows)}",
        f"- Expected target folders: {len(target_rows)}",
        f"- Targets with raw tabular/archive files: {raw_like_targets}",
        "",
        markdown_count_table(role_counts, "File role"),
        "",
        "## Target Folder Status",
        "",
        markdown_count_table(target_status_counts, "Target status"),
        "",
        "## Machine-Readable Outputs",
        "",
        f"- `temp/{MANIFEST_PATH.name}`",
        f"- `temp/{TARGET_AUDIT_PATH.name}`",
        "",
        "## Guardrail",
        "",
        "Only files in `temp/raw_downloads/` are considered raw acquisition inputs. Clean analytical datasets may be written to `data/` only after raw schema/value inspection and harmonization audits pass.",
    ]
    REPORT_PATH.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    ensure_dirs()
    RAW_ROOT.mkdir(parents=True, exist_ok=True)
    targets = expected_targets()
    for row in targets:
        target_path(row).mkdir(parents=True, exist_ok=True)
    files = iter_files()
    manifest_rows = build_manifest(files, targets)
    target_rows = target_audit_rows(targets, files)
    write_csv(MANIFEST_PATH, manifest_rows, MANIFEST_COLUMNS)
    write_csv(TARGET_AUDIT_PATH, target_rows, TARGET_COLUMNS)
    write_report(manifest_rows, target_rows)
    raw_like = sum(1 for row in manifest_rows if row.get("file_role") in {"archive", "raw_tabular_or_spreadsheet"})
    append_log(TEMP_DIR / "audit_log.md", f"Audited raw download folder: files={len(manifest_rows)} raw_like_files={raw_like} targets={len(target_rows)}.")
    print(f"Raw download audit files={len(manifest_rows)} raw_like_files={raw_like} targets={len(target_rows)}")


if __name__ == "__main__":
    main()
