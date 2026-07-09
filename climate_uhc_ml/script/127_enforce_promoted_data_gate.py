from __future__ import annotations

import csv
import shutil
from pathlib import Path
from typing import Any

from common import DATA_DIR, REPORT_DIR, RESULT_DIR, TEMP_DIR, append_log, ensure_dirs, sha256_file, write_csv


REGISTRY_PATH = RESULT_DIR / "promoted_country_wave_registry.csv"
MANIFEST_PATH = TEMP_DIR / "promoted_data_gate_manifest.csv"
SUMMARY_PATH = RESULT_DIR / "promoted_data_gate_summary.csv"
REPORT_PATH = REPORT_DIR / "promoted_data_gate.md"
QUARANTINE_DIR = TEMP_DIR / "diagnostic_data_quarantine" / "current"
DATA_README_PATH = DATA_DIR / "README.md"

MANIFEST_COLUMNS = [
    "relative_path",
    "bytes",
    "sha256",
    "promotion_status",
    "action",
    "quarantine_path",
    "reason",
]
SUMMARY_COLUMNS = ["metric", "value", "interpretation"]

DATASET_SUFFIXES = {".csv", ".parquet", ".dta", ".sav", ".sas7bdat", ".xpt", ".zip", ".7z", ".rar"}
KEEP_FILENAMES = {"README.md", ".gitkeep"}


def read_csv_dicts(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        return []
    with path.open(encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def relative(path: Path) -> str:
    try:
        return str(path.relative_to(TEMP_DIR.parent)).replace("\\", "/")
    except ValueError:
        return str(path).replace("\\", "/")


def data_files() -> list[Path]:
    if not DATA_DIR.exists():
        return []
    out: list[Path] = []
    for path in sorted(DATA_DIR.rglob("*")):
        if not path.is_file():
            continue
        if path.name in KEEP_FILENAMES:
            continue
        if path.suffix.lower() in DATASET_SUFFIXES:
            out.append(path)
    return out


def promoted_rows() -> list[dict[str, str]]:
    rows = read_csv_dicts(REGISTRY_PATH)
    return [row for row in rows if row.get("analysis_ready_status") == "promoted_analysis_ready"]


def quarantine_path_for(path: Path) -> Path:
    rel = path.relative_to(DATA_DIR)
    return QUARANTINE_DIR / rel


def quarantine_file(path: Path) -> tuple[str, str]:
    target = quarantine_path_for(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    if target.exists():
        if target.is_file() and sha256_file(target) == sha256_file(path):
            path.unlink()
            return "quarantined_existing_copy_removed_from_data", relative(target)
        stem = target.stem
        suffix = target.suffix
        counter = 2
        while True:
            candidate = target.with_name(f"{stem}_{counter}{suffix}")
            if not candidate.exists():
                target = candidate
                break
            counter += 1
    shutil.copy2(path, target)
    path.unlink()
    return "quarantined_to_temp_removed_from_data", relative(target)


def build_data_readme(promoted_count: int, data_file_count: int, quarantined_count: int) -> None:
    DATA_README_PATH.write_text(
        f"""# Data Directory

Status: dataset-promotion gate enforced.

`data/` is reserved for country-waves that pass the promotion registry gates:
raw package present, value/unit/recall/missing-code verification complete,
financial/access outcome gates resolved, and accepted climate linkage ready.

Current promoted rows in `result/promoted_country_wave_registry.csv`: {promoted_count}

Current promoted dataset files kept in `data/`: {data_file_count}

Diagnostic or pre-promotion files quarantined this run: {quarantined_count}

Quarantined diagnostic files, when present, live under
`temp/diagnostic_data_quarantine/current/` and are indexed in
`temp/promoted_data_gate_manifest.csv`.
""",
        encoding="utf-8",
    )


def write_report(summary_rows: list[dict[str, Any]], manifest_rows: list[dict[str, Any]]) -> None:
    summary_table = "\n".join(
        f"| {row['metric']} | {row['value']} | {row['interpretation']} |"
        for row in summary_rows
    )
    manifest_preview = "\n".join(
        f"| {row['relative_path']} | {row['action']} | {row['quarantine_path']} | {row['reason']} |"
        for row in manifest_rows[:40]
    )
    if not manifest_preview:
        manifest_preview = "| None | none |  | No dataset-like files were present in data/. |"
    REPORT_PATH.write_text(
        f"""# Promoted Data Gate

Status: fail-closed guard for `data/`.

The active objective allows country-waves into `data/` only after the promotion
registry marks them `promoted_analysis_ready`. Diagnostic Albania files and
other pre-promotion outputs belong in `temp/`, not in `data/`.

## Summary

| Metric | Value | Interpretation |
|---|---:|---|
{summary_table}

## Data File Actions

| Original path | Action | Quarantine path | Reason |
|---|---|---|---|
{manifest_preview}

## Rule

If `result/promoted_country_wave_registry.csv` has zero promoted rows, this
script removes dataset-like files from `data/` after copying them to
`temp/diagnostic_data_quarantine/current/`. This preserves diagnostic evidence
while preventing provisional outputs from masquerading as promoted datasets.
""",
        encoding="utf-8",
    )


def main() -> None:
    ensure_dirs()
    QUARANTINE_DIR.mkdir(parents=True, exist_ok=True)

    promoted = promoted_rows()
    promoted_count = len(promoted)
    before_files = data_files()
    manifest_rows: list[dict[str, Any]] = []
    seen_quarantine_paths: set[str] = set()

    for path in before_files:
        file_hash = sha256_file(path)
        base = {
            "relative_path": relative(path),
            "bytes": path.stat().st_size,
            "sha256": file_hash,
            "promotion_status": "registry_promoted_rows_present" if promoted_count else "no_registry_promoted_rows",
        }
        if promoted_count == 0:
            action, quarantine_path = quarantine_file(path)
            manifest_rows.append(
                {
                    **base,
                    "action": action,
                    "quarantine_path": quarantine_path,
                    "reason": "No country-wave currently passes promoted_analysis_ready; data/ must remain reserved for promoted datasets.",
                }
            )
            seen_quarantine_paths.add(quarantine_path)
        else:
            manifest_rows.append(
                {
                    **base,
                    "action": "kept_registry_has_promoted_rows",
                    "quarantine_path": "",
                    "reason": "Registry has promoted rows; downstream promoted-data builder must maintain file-level lineage.",
                }
            )

    for path in sorted(QUARANTINE_DIR.rglob("*")):
        if not path.is_file() or path.suffix.lower() not in DATASET_SUFFIXES:
            continue
        qpath = relative(path)
        if qpath in seen_quarantine_paths:
            continue
        original = DATA_DIR / path.relative_to(QUARANTINE_DIR)
        manifest_rows.append(
            {
                "relative_path": relative(original),
                "bytes": path.stat().st_size,
                "sha256": sha256_file(path),
                "promotion_status": "already_quarantined_no_registry_promoted_rows" if promoted_count == 0 else "already_quarantined_registry_promoted_rows_present",
                "action": "already_quarantined",
                "quarantine_path": qpath,
                "reason": "Diagnostic or pre-promotion dataset file is preserved in temp/ and not present in data/.",
            }
        )

    after_files = data_files()
    quarantined_count = sum(1 for row in manifest_rows if str(row.get("action", "")).startswith("quarantined"))
    current_quarantine_count = sum(1 for row in manifest_rows if row.get("action") in {"already_quarantined", "quarantined_to_temp_removed_from_data", "quarantined_existing_copy_removed_from_data"})
    build_data_readme(promoted_count, len(after_files), quarantined_count)

    summary_rows = [
        {"metric": "registry_promoted_analysis_ready_rows", "value": promoted_count, "interpretation": "Country-waves currently allowed to write promoted datasets into data/."},
        {"metric": "data_dataset_files_before_gate", "value": len(before_files), "interpretation": "Dataset-like files found in data/ before enforcing the gate."},
        {"metric": "data_dataset_files_after_gate", "value": len(after_files), "interpretation": "Dataset-like files left in data/ after enforcing the gate."},
        {"metric": "quarantined_diagnostic_data_files", "value": quarantined_count, "interpretation": "Pre-promotion data files preserved under temp/diagnostic_data_quarantine/current/ and removed from data/."},
        {"metric": "current_diagnostic_quarantine_files", "value": current_quarantine_count, "interpretation": "Diagnostic or pre-promotion dataset files currently indexed under temp/diagnostic_data_quarantine/current/."},
        {"metric": "data_readme_written", "value": int(DATA_README_PATH.exists()), "interpretation": "Whether data/README.md records the current promoted-data status."},
        {"metric": "promoted_data_gate_status", "value": "closed_no_promoted_rows" if promoted_count == 0 else "open_registry_has_promoted_rows", "interpretation": "Current write gate status for promoted data outputs."},
    ]

    write_csv(MANIFEST_PATH, manifest_rows, MANIFEST_COLUMNS)
    write_csv(SUMMARY_PATH, summary_rows, SUMMARY_COLUMNS)
    write_report(summary_rows, manifest_rows)
    append_log(
        TEMP_DIR / "audit_log.md",
        f"Promoted data gate promoted_rows={promoted_count} before={len(before_files)} after={len(after_files)} quarantined={quarantined_count}.",
    )
    print(
        f"Promoted data gate promoted_rows={promoted_count} before={len(before_files)} "
        f"after={len(after_files)} quarantined={quarantined_count}."
    )


if __name__ == "__main__":
    main()
