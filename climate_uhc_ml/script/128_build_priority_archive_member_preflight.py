from __future__ import annotations

import csv
import re
import subprocess
import tarfile
import zipfile
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

from common import PROJECT_ROOT, REPORT_DIR, RESULT_DIR, TEMP_DIR, append_log, ensure_dirs, sha256_file, write_csv


WAVE_PLAN_PATH = RESULT_DIR / "priority_promotion_acquisition_wave_plan.csv"
FILE_TARGET_PATH = TEMP_DIR / "priority_raw_file_targets.csv"
MEMBER_INVENTORY_PATH = TEMP_DIR / "priority_archive_member_inventory.csv"
COMPLETENESS_PATH = TEMP_DIR / "priority_archive_completeness_matrix.csv"
SUMMARY_PATH = RESULT_DIR / "priority_archive_member_preflight_summary.csv"
REPORT_PATH = REPORT_DIR / "priority_archive_member_preflight.md"
RAW_ROOT = TEMP_DIR / "raw_downloads"

RAW_SUFFIXES = {".dta", ".sav", ".por", ".sas7bdat", ".xpt", ".csv", ".tsv", ".txt", ".xlsx", ".xls", ".parquet", ".feather"}
ARCHIVE_SUFFIXES = {".zip", ".tar", ".tgz", ".gz", ".bz2", ".xz", ".7z", ".rar"}
IGNORED_FILE_PREFIXES = {"_PLACE_RAW_FILES_HERE", "_PRIORITY_RAW_INTAKE_HANDOFF", "_PRIORITY_CLIMATE_LINKAGE_PREFLIGHT", "_PRIORITY_RAW_VERIFICATION_WORKBOOK"}

INVENTORY_COLUMNS = [
    "acquisition_batch_rank",
    "batch_role",
    "country",
    "wave",
    "idno",
    "archive_path",
    "archive_suffix",
    "archive_size_bytes",
    "archive_sha256",
    "member_path",
    "member_file_name",
    "member_stem",
    "member_suffix",
    "member_size_bytes",
    "listing_status",
    "listing_tool",
    "notes",
]

COMPLETENESS_COLUMNS = [
    "acquisition_batch_rank",
    "batch_role",
    "country",
    "wave",
    "idno",
    "file_rank",
    "expected_file_name",
    "direct_file_matches",
    "archive_member_matches",
    "coverage_status",
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


def safe_int(value: Any, default: int = 0) -> int:
    try:
        text = str(value).strip()
        return int(float(text)) if text else default
    except (TypeError, ValueError):
        return default


def rel(path: Path) -> str:
    try:
        return str(path.relative_to(PROJECT_ROOT)).replace("\\", "/")
    except ValueError:
        return str(path).replace("\\", "/")


def compact(values: list[str], limit: int = 12) -> str:
    out: list[str] = []
    seen: set[str] = set()
    for value in values:
        item = " ".join(clean(value).split())
        if item and item not in seen:
            out.append(item)
            seen.add(item)
        if len(out) >= limit:
            break
    return "; ".join(out)


def target_folder_path(folder: str, idno: str) -> Path:
    folder_clean = clean(folder).replace("\\", "/").strip("/")
    if folder_clean.startswith("temp/raw_downloads/"):
        return PROJECT_ROOT / folder_clean
    if folder_clean:
        return RAW_ROOT / folder_clean
    return RAW_ROOT / idno


def compound_suffix(path_or_name: Path | str) -> str:
    name = path_or_name.name if isinstance(path_or_name, Path) else str(path_or_name)
    lower = name.lower()
    for suffix in [".tar.gz", ".tar.bz2", ".tar.xz"]:
        if lower.endswith(suffix):
            return suffix
    return Path(lower).suffix


def strip_known_suffix(name: str) -> str:
    lower = name.lower()
    for suffix in [".tar.gz", ".tar.bz2", ".tar.xz", ".sas7bdat"]:
        if lower.endswith(suffix):
            return name[: -len(suffix)]
    suffix = Path(name).suffix
    return name[: -len(suffix)] if suffix else name


def normalize_key(name: str) -> str:
    base = Path(clean(name).replace("\\", "/")).name.lower()
    stem = strip_known_suffix(base)
    return re.sub(r"[^a-z0-9]+", "", stem)


def match_keys(name: str) -> set[str]:
    base = Path(clean(name).replace("\\", "/")).name.lower()
    stem = strip_known_suffix(base).lower()
    return {base, stem, normalize_key(base)}


def is_raw_file(path: Path) -> bool:
    return compound_suffix(path) in RAW_SUFFIXES


def is_archive(path: Path) -> bool:
    return compound_suffix(path) in ARCHIVE_SUFFIXES or compound_suffix(path) in {".tar.gz", ".tar.bz2", ".tar.xz"}


def ignored_file(path: Path) -> bool:
    return any(path.name.startswith(prefix) for prefix in IGNORED_FILE_PREFIXES)


def run_listing_command(archive: Path) -> tuple[list[tuple[str, str]], str, str]:
    commands = [
        ("7z", ["7z", "l", "-slt", str(archive)]),
        ("7zz", ["7zz", "l", "-slt", str(archive)]),
    ]
    for tool, command in commands:
        try:
            result = subprocess.run(command, capture_output=True, text=True, timeout=60, check=False)
        except (FileNotFoundError, subprocess.SubprocessError):
            continue
        if result.returncode != 0:
            continue
        members: list[tuple[str, str]] = []
        current_path = ""
        current_size = ""
        for line in result.stdout.splitlines():
            if line.startswith("Path = "):
                current_path = line.split("=", 1)[1].strip()
                current_size = ""
            elif line.startswith("Size = "):
                current_size = line.split("=", 1)[1].strip()
            elif not line.strip() and current_path:
                if Path(current_path).suffix.lower() in RAW_SUFFIXES:
                    members.append((current_path, current_size))
                current_path = ""
                current_size = ""
        if current_path and Path(current_path).suffix.lower() in RAW_SUFFIXES:
            members.append((current_path, current_size))
        return members, "listed", tool
    return [], "unsupported_archive_listing", "none"


def list_archive_members(archive: Path) -> tuple[list[tuple[str, str]], str, str]:
    suffix = compound_suffix(archive)
    try:
        if suffix == ".zip":
            with zipfile.ZipFile(archive) as zf:
                return [
                    (member.filename, str(member.file_size))
                    for member in zf.infolist()
                    if not member.is_dir() and Path(member.filename).suffix.lower() in RAW_SUFFIXES
                ], "listed", "zipfile"
        if suffix in {".tar", ".tgz", ".gz", ".bz2", ".xz", ".tar.gz", ".tar.bz2", ".tar.xz"}:
            with tarfile.open(archive) as tf:
                return [
                    (member.name, str(member.size))
                    for member in tf.getmembers()
                    if member.isfile() and Path(member.name).suffix.lower() in RAW_SUFFIXES
                ], "listed", "tarfile"
        if suffix in {".7z", ".rar"}:
            return run_listing_command(archive)
    except Exception as exc:
        return [], "listing_failed", f"{suffix}:{exc}"
    return [], "unsupported_archive_listing", "none"


def wave_targets(rows: list[dict[str, str]]) -> dict[str, list[dict[str, str]]]:
    out: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in rows:
        idno = clean(row.get("idno"))
        if idno:
            out[idno].append(row)
    return out


def current_files(folder: Path) -> tuple[list[Path], list[Path]]:
    if not folder.exists():
        return [], []
    files = [path for path in sorted(folder.rglob("*")) if path.is_file() and not ignored_file(path)]
    raw_files = [path for path in files if is_raw_file(path)]
    archives = [path for path in files if is_archive(path)]
    return raw_files, archives


def build_outputs() -> tuple[list[dict[str, str]], list[dict[str, str]], list[dict[str, Any]]]:
    waves = read_csv_dicts(WAVE_PLAN_PATH)
    targets_by_id = wave_targets(read_csv_dicts(FILE_TARGET_PATH))
    inventory_rows: list[dict[str, str]] = []
    completeness_rows: list[dict[str, str]] = []
    dataset_statuses: list[str] = []

    for wave in waves:
        idno = clean(wave.get("idno"))
        folder = target_folder_path(wave.get("local_target_folder", ""), idno)
        raw_files, archives = current_files(folder)

        direct_by_key: dict[str, list[str]] = defaultdict(list)
        for path in raw_files:
            for key in match_keys(path.name):
                direct_by_key[key].append(rel(path))

        archive_by_key: dict[str, list[str]] = defaultdict(list)
        listed_archives = 0
        unsupported_archives = 0
        for archive in archives:
            members, status, tool = list_archive_members(archive)
            if status == "listed":
                listed_archives += 1
            else:
                unsupported_archives += 1
            if not members:
                inventory_rows.append(
                    {
                        "acquisition_batch_rank": wave.get("acquisition_batch_rank", ""),
                        "batch_role": wave.get("batch_role", ""),
                        "country": wave.get("country", ""),
                        "wave": wave.get("wave", ""),
                        "idno": idno,
                        "archive_path": rel(archive),
                        "archive_suffix": compound_suffix(archive),
                        "archive_size_bytes": str(archive.stat().st_size),
                        "archive_sha256": sha256_file(archive),
                        "member_path": "",
                        "member_file_name": "",
                        "member_stem": "",
                        "member_suffix": "",
                        "member_size_bytes": "",
                        "listing_status": status,
                        "listing_tool": tool,
                        "notes": "No raw-data members listed; archive may be unsupported, empty, documentation-only, or listing failed.",
                    }
                )
                continue
            for member_path, member_size in members:
                member_name = Path(member_path).name
                member_stem = strip_known_suffix(member_name)
                member_ref = f"{rel(archive)}::{member_path}"
                for key in match_keys(member_name):
                    archive_by_key[key].append(member_ref)
                inventory_rows.append(
                    {
                        "acquisition_batch_rank": wave.get("acquisition_batch_rank", ""),
                        "batch_role": wave.get("batch_role", ""),
                        "country": wave.get("country", ""),
                        "wave": wave.get("wave", ""),
                        "idno": idno,
                        "archive_path": rel(archive),
                        "archive_suffix": compound_suffix(archive),
                        "archive_size_bytes": str(archive.stat().st_size),
                        "archive_sha256": sha256_file(archive),
                        "member_path": member_path,
                        "member_file_name": member_name,
                        "member_stem": member_stem,
                        "member_suffix": Path(member_name).suffix.lower(),
                        "member_size_bytes": member_size,
                        "listing_status": status,
                        "listing_tool": tool,
                        "notes": "Archive member is only a preflight match candidate; raw values and metadata still require inspection.",
                    }
                )

        wave_targets_rows = targets_by_id.get(idno, [])
        covered = 0
        for target in wave_targets_rows:
            expected = clean(target.get("file_name"))
            keys = match_keys(expected)
            direct_matches = sorted({match for key in keys for match in direct_by_key.get(key, [])})
            archive_matches = sorted({match for key in keys for match in archive_by_key.get(key, [])})
            if direct_matches:
                coverage = "covered_by_direct_raw_file"
                action = "Run raw schema and value/key/unit/recall/missing-code verification on the direct raw file."
                covered += 1
            elif archive_matches:
                coverage = "covered_by_archive_member_needs_extraction"
                action = "Extract or inspect archive member, then run raw schema and value/key/unit/recall/missing-code verification."
                covered += 1
            elif archives and unsupported_archives and not listed_archives:
                coverage = "unknown_archive_listing_unsupported"
                action = "Install or use an archive tool that can list/extract the placed archive, then rerun this preflight."
            elif archives:
                coverage = "not_found_in_listed_archive_members"
                action = "Download the complete original raw package or identify the expected module under a documented renamed file."
            else:
                coverage = "blocked_no_raw_or_archive_file"
                action = "Place complete original raw archive/tabular package in the target folder."
            completeness_rows.append(
                {
                    "acquisition_batch_rank": wave.get("acquisition_batch_rank", ""),
                    "batch_role": wave.get("batch_role", ""),
                    "country": wave.get("country", ""),
                    "wave": wave.get("wave", ""),
                    "idno": idno,
                    "file_rank": target.get("file_rank", ""),
                    "expected_file_name": expected,
                    "direct_file_matches": compact(direct_matches, limit=8),
                    "archive_member_matches": compact(archive_matches, limit=8),
                    "coverage_status": coverage,
                    "verification_action": action,
                }
            )
        if wave_targets_rows and covered == len(wave_targets_rows):
            dataset_statuses.append("all_priority_targets_covered_needs_raw_value_verification")
        elif covered:
            dataset_statuses.append("partial_priority_targets_covered")
        elif archives:
            dataset_statuses.append("archives_present_no_priority_target_coverage")
        else:
            dataset_statuses.append("blocked_no_raw_or_archive_file")

    inv_counts = Counter(row["listing_status"] for row in inventory_rows)
    coverage_counts = Counter(row["coverage_status"] for row in completeness_rows)
    dataset_counts = Counter(dataset_statuses)
    summary_rows: list[dict[str, Any]] = [
        {"metric": "priority_archive_preflight_dataset_rows", "value": len(waves), "interpretation": "Priority and backup waves checked for direct/archive raw coverage."},
        {"metric": "priority_archive_preflight_file_target_rows", "value": len(completeness_rows), "interpretation": "Priority file targets checked against direct files and archive members."},
        {"metric": "priority_archive_files_found", "value": len({row["archive_path"] for row in inventory_rows if row["archive_path"]}), "interpretation": "Archive files found in priority target folders."},
        {"metric": "priority_archive_member_rows", "value": sum(1 for row in inventory_rows if row["member_path"]), "interpretation": "Raw-like members listed inside priority archives."},
        {"metric": "priority_targets_covered_by_direct_file", "value": coverage_counts.get("covered_by_direct_raw_file", 0), "interpretation": "Priority file targets covered by a direct raw file."},
        {"metric": "priority_targets_covered_by_archive_member", "value": coverage_counts.get("covered_by_archive_member_needs_extraction", 0), "interpretation": "Priority file targets covered by a listed archive member."},
        {"metric": "priority_targets_missing_direct_or_archive_member", "value": coverage_counts.get("blocked_no_raw_or_archive_file", 0) + coverage_counts.get("not_found_in_listed_archive_members", 0), "interpretation": "Priority file targets still missing after direct/archive preflight."},
        {"metric": "priority_archives_with_unsupported_listing", "value": inv_counts.get("unsupported_archive_listing", 0), "interpretation": "Archive files whose members could not be listed by available tools."},
        {"metric": "priority_datasets_all_targets_covered", "value": dataset_counts.get("all_priority_targets_covered_needs_raw_value_verification", 0), "interpretation": "Datasets with all priority targets covered but still requiring raw value verification."},
        {"metric": "priority_datasets_blocked_no_raw_or_archive", "value": dataset_counts.get("blocked_no_raw_or_archive_file", 0), "interpretation": "Datasets with no raw tabular or archive file in the priority folder."},
        {"metric": "modeling_gate_status", "value": "blocked", "interpretation": "Models remain blocked until promoted registry thresholds and accepted climate linkage pass."},
    ]
    return inventory_rows, completeness_rows, summary_rows


def markdown_table(rows: list[dict[str, str]], columns: list[str], limit: int = 30) -> str:
    lines = ["| " + " | ".join(columns) + " |", "|" + "|".join("---" for _ in columns) + "|"]
    for row in rows[:limit]:
        values = []
        for column in columns:
            value = clean(row.get(column)).replace("|", "/")
            if len(value) > 120:
                value = value[:117] + "..."
            values.append(value)
        lines.append("| " + " | ".join(values) + " |")
    return "\n".join(lines)


def write_report(inventory: list[dict[str, str]], completeness: list[dict[str, str]], summary: list[dict[str, Any]]) -> None:
    summary_table = "\n".join(f"| {row['metric']} | {row['value']} | {row['interpretation']} |" for row in summary)
    coverage_counts = Counter(row["coverage_status"] for row in completeness)
    coverage_table = "\n".join(f"| `{status}` | {count} |" for status, count in sorted(coverage_counts.items()))
    REPORT_PATH.write_text(
        f"""# Priority Archive Member Preflight

Status: fail-closed archive/direct-file completeness preflight for the priority
10-wave batch and sixth-country backups. This does not inspect raw values and
does not promote any country-wave into `data/`.

## Summary

| Metric | Value | Interpretation |
|---|---:|---|
{summary_table}

## Coverage Status

| Coverage status | File targets |
|---|---:|
{coverage_table}

## Completeness Preview

{markdown_table(completeness, ['acquisition_batch_rank', 'idno', 'file_rank', 'expected_file_name', 'coverage_status', 'verification_action'], 40)}

## Archive Member Preview

{markdown_table(inventory, ['acquisition_batch_rank', 'idno', 'archive_path', 'member_file_name', 'listing_status', 'listing_tool'], 30) if inventory else 'No priority archive files were found.'}

## Rule

An archive-member match is only a placement/completeness signal. Promotion still
requires extraction or direct schema inspection plus raw value, label, unit,
recall-period, missing-code, merge-key, survey-design, timing, geography, and
CHIRPS/ERA5 linkage verification.

## Machine-Readable Outputs

- `temp/priority_archive_member_inventory.csv`
- `temp/priority_archive_completeness_matrix.csv`
- `result/priority_archive_member_preflight_summary.csv`
""",
        encoding="utf-8",
    )


def main() -> None:
    ensure_dirs()
    inventory, completeness, summary = build_outputs()
    write_csv(MEMBER_INVENTORY_PATH, inventory, INVENTORY_COLUMNS)
    write_csv(COMPLETENESS_PATH, completeness, COMPLETENESS_COLUMNS)
    write_csv(SUMMARY_PATH, summary, SUMMARY_COLUMNS)
    write_report(inventory, completeness, summary)
    append_log(
        TEMP_DIR / "audit_log.md",
        f"Priority archive member preflight targets={len(completeness)} archive_member_rows={len(inventory)}.",
    )
    print(f"Priority archive member preflight targets={len(completeness)} archive_member_rows={len(inventory)}.")


if __name__ == "__main__":
    main()
