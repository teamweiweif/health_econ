from __future__ import annotations

import csv
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

from common import PROJECT_ROOT, REPORT_DIR, RESULT_DIR, TEMP_DIR, append_log, ensure_dirs, write_csv


WAVE_PLAN_PATH = RESULT_DIR / "priority_promotion_acquisition_wave_plan.csv"
FILE_QUEUE_PATH = RESULT_DIR / "priority_promotion_acquisition_file_queue.csv"
ACCESS_PROBE_PATH = TEMP_DIR / "priority_official_raw_access_probe.csv"
INTAKE_PATH = TEMP_DIR / "raw_download_intake_manifest.csv"
EXPECTED_PATH = TEMP_DIR / "raw_download_expected_files.csv"
RAW_FILE_MANIFEST_PATH = TEMP_DIR / "raw_download_file_manifest.csv"
CONCEPT_PATH = TEMP_DIR / "raw_ingestion_concept_checklist.csv"

GATE_PATH = TEMP_DIR / "priority_raw_intake_gate.csv"
FILE_TARGET_PATH = TEMP_DIR / "priority_raw_file_targets.csv"
SUMMARY_PATH = RESULT_DIR / "priority_raw_intake_gate_summary.csv"
REPORT_PATH = REPORT_DIR / "priority_raw_intake_gate.md"

RAW_ROOT = TEMP_DIR / "raw_downloads"
RAW_TABULAR_ROLES = {"raw_tabular_or_spreadsheet"}
RAW_PRESENT_STATUSES = {"exact_file_present", "stem_match_present", "archive_present_needs_schema_extraction"}

POST_DOWNLOAD_COMMANDS = [
    "python script/17_audit_raw_downloads.py",
    "python script/03_inspect_raw_schemas.py",
    "python script/29_build_raw_variable_verification_protocol.py",
    "python script/33_build_harmonization_recipe_gate.py",
    "python script/121_build_country_wave_promotion_registry.py",
    "python script/122_build_priority_promotion_acquisition_plan.py",
    "python script/123_probe_priority_official_raw_access.py",
    "python script/124_build_priority_raw_intake_gate.py",
    "python script/36_build_direct_read_audit_bundle.py",
    "python script/14_validate_workspace.py",
]

GATE_COLUMNS = [
    "acquisition_batch_rank",
    "batch_role",
    "country",
    "wave",
    "idno",
    "survey_name",
    "official_url",
    "local_target_folder",
    "folder_exists",
    "file_count",
    "raw_tabular_file_count",
    "archive_file_count",
    "documentation_file_count",
    "priority_expected_file_rows",
    "priority_expected_files_present",
    "priority_expected_files_not_present",
    "required_concept_rows",
    "required_concepts_unverified",
    "access_gate_detected",
    "direct_raw_route_status",
    "manual_action_status",
    "current_gate_status",
    "next_action",
    "promotion_blockers",
    "handoff_readme",
    "post_download_commands",
]

FILE_TARGET_COLUMNS = [
    "acquisition_batch_rank",
    "batch_role",
    "country",
    "wave",
    "idno",
    "file_rank",
    "file_name",
    "local_target_folder",
    "candidate_categories",
    "candidate_harmonized_variables",
    "download_priority_reason",
    "expected_file_status",
    "present_matching_files",
    "current_file_gate_status",
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


def compact(values: list[str], limit: int = 12, sep: str = "; ") -> str:
    out: list[str] = []
    seen: set[str] = set()
    for value in values:
        item = " ".join(clean(value).split())
        if item and item not in seen:
            out.append(item)
            seen.add(item)
        if len(out) >= limit:
            break
    return sep.join(out)


def rel(path: Path) -> str:
    try:
        return str(path.relative_to(PROJECT_ROOT)).replace("\\", "/")
    except ValueError:
        return str(path).replace("\\", "/")


def target_folder_path(folder: str, idno: str) -> Path:
    folder_clean = clean(folder).replace("\\", "/").strip("/")
    if folder_clean.startswith("temp/raw_downloads/"):
        return PROJECT_ROOT / folder_clean
    if folder_clean:
        return RAW_ROOT / folder_clean
    return RAW_ROOT / idno


def normalize_file_name(value: str) -> str:
    name = clean(value).replace("\\", "/").split("/")[-1].lower()
    for suffix in [".tar.gz", ".tar.bz2", ".tar.xz"]:
        if name.endswith(suffix):
            return name[: -len(suffix)]
    suffix = Path(name).suffix
    return name[: -len(suffix)] if suffix else name


def group(rows: list[dict[str, str]], field: str) -> dict[str, list[dict[str, str]]]:
    out: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in rows:
        key = clean(row.get(field))
        if key:
            out[key].append(row)
    return out


def first_by(rows: list[dict[str, str]], field: str) -> dict[str, dict[str, str]]:
    out: dict[str, dict[str, str]] = {}
    for row in rows:
        key = clean(row.get(field))
        if key and key not in out:
            out[key] = row
    return out


def expected_lookup(rows: list[dict[str, str]]) -> dict[tuple[str, str], dict[str, str]]:
    out: dict[tuple[str, str], dict[str, str]] = {}
    for row in rows:
        idno = clean(row.get("dataset_idno"))
        file_name = clean(row.get("expected_file_name"))
        if idno and file_name:
            out.setdefault((idno, file_name.lower()), row)
            out.setdefault((idno, normalize_file_name(file_name)), row)
    return out


def raw_manifest_counts(rows: list[dict[str, str]]) -> dict[str, Counter[str]]:
    counts: dict[str, Counter[str]] = defaultdict(Counter)
    for row in rows:
        idno = clean(row.get("target_dataset_idno"))
        if not idno:
            continue
        role = clean(row.get("file_role"))
        counts[idno]["file_count"] += 1
        if role in RAW_TABULAR_ROLES:
            counts[idno]["raw_tabular_file_count"] += 1
        elif role == "archive":
            counts[idno]["archive_file_count"] += 1
        elif role in {"documentation_or_metadata", "readme_or_instructions"}:
            counts[idno]["documentation_file_count"] += 1
    return counts


def concept_counts(rows: list[dict[str, str]]) -> dict[str, tuple[int, int, str]]:
    grouped_rows = group(rows, "idno")
    out: dict[str, tuple[int, int, str]] = {}
    for idno, items in grouped_rows.items():
        unverified = [
            clean(row.get("concept"))
            for row in items
            if clean(row.get("raw_verification_status")) not in {"raw_value_verified", "verified"}
        ]
        out[idno] = (len(items), len(unverified), compact(unverified, limit=20))
    return out


def file_gate_status(expected_status: str) -> str:
    if expected_status in {"exact_file_present", "stem_match_present"}:
        return "ready_for_raw_value_key_audit"
    if expected_status == "archive_present_needs_schema_extraction":
        return "archive_present_extract_or_inspect_members_first"
    return "blocked_missing_raw_file"


def current_gate_status(
    raw_tabular_count: int,
    archive_count: int,
    missing_priority_files: int,
    unverified_concepts: int,
    direct_route_status: str,
) -> str:
    if raw_tabular_count > 0 and missing_priority_files == 0 and unverified_concepts == 0:
        return "ready_for_manual_value_label_unit_key_audit"
    if raw_tabular_count > 0:
        return "raw_tabular_present_partial_priority_gate_blocked"
    if archive_count > 0:
        return "archive_present_needs_extraction_schema_and_priority_file_check"
    if direct_route_status == "possible_direct_raw_link_found":
        return "direct_raw_candidate_needs_download_and_checksum"
    return "blocked_manual_raw_package_required"


def next_action_for(status: str) -> str:
    if status == "ready_for_manual_value_label_unit_key_audit":
        return "Run raw schema inspection and complete manual value, label, unit, recall-period, missing-code, key, weight, timing, and geography audits."
    if status == "raw_tabular_present_partial_priority_gate_blocked":
        return "Inspect present raw files, then add missing priority modules or complete archive extraction before promotion."
    if status == "archive_present_needs_extraction_schema_and_priority_file_check":
        return "Extract or inspect archive members, preserve original archive, then rerun raw download and schema audits."
    if status == "direct_raw_candidate_needs_download_and_checksum":
        return "Download only through the official permitted route, compute checksums, and rerun the promotion pipeline."
    return "Complete official login/register/terms workflow, download the complete original raw package plus documentation, and place unchanged files in the target folder."


def promotion_blockers(status: str, missing_files: int, unverified_concepts: int, manual_action_status: str) -> str:
    blockers = []
    if status == "blocked_manual_raw_package_required":
        blockers.append("complete original raw package absent")
    if missing_files > 0:
        blockers.append(f"{missing_files} priority metadata-derived file targets not present")
    if unverified_concepts > 0:
        blockers.append(f"{unverified_concepts} required concepts lack raw value/key verification")
    if manual_action_status:
        blockers.append(manual_action_status)
    blockers.append("CHIRPS/ERA5 climate-linkage route not accepted")
    blockers.append("do not write to data/ until all promotion gates pass")
    return "; ".join(blockers)


def markdown_table(rows: list[dict[str, str]], columns: list[str], limit: int = 20) -> str:
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


def write_handoff_readme(wave: dict[str, str], file_rows: list[dict[str, str]], gate_row: dict[str, str]) -> str:
    folder = target_folder_path(wave.get("local_target_folder", ""), wave.get("idno", ""))
    folder.mkdir(parents=True, exist_ok=True)
    readme = folder / "_PRIORITY_RAW_INTAKE_HANDOFF.md"
    files_table = markdown_table(
        file_rows,
        ["file_rank", "file_name", "candidate_categories", "current_file_gate_status", "verification_action"],
        20,
    )
    readme.write_text(
        f"""# Priority Raw Intake Handoff: {wave.get('idno', '')}

This folder is reserved for the complete original raw package and documentation
for `{wave.get('country', '')}` `{wave.get('wave', '')}`. Keep source archive
and file names unchanged.

Official access URL: {wave.get('official_url', '')}

Current gate status: `{gate_row['current_gate_status']}`

Next action: {gate_row['next_action']}

## Required Promotion Gates

- Complete original raw package is present in this folder.
- Household/person merge keys are verified from raw values.
- Household weights, strata, PSU/cluster, and survey design are verified.
- Consumption or income denominator is verified.
- OOP health expenditure values, units, recall periods, and missing codes are verified.
- Illness/need and care-seeking/access variables are verified where available.
- Survey timing and geography are verified for climate linkage.
- CHIRPS or ERA5 route is accepted before writing to `data/`.

## Priority Files To Inspect First

{files_table}

## Post-Download Commands

```powershell
{chr(10).join(POST_DOWNLOAD_COMMANDS)}
```
""",
        encoding="utf-8",
    )
    return rel(readme)


def build_outputs() -> tuple[list[dict[str, str]], list[dict[str, str]], list[dict[str, str]]]:
    waves = read_csv_dicts(WAVE_PLAN_PATH)
    queue_by_id = group(read_csv_dicts(FILE_QUEUE_PATH), "idno")
    access_by_id = first_by(read_csv_dicts(ACCESS_PROBE_PATH), "idno")
    intake_by_id = first_by(read_csv_dicts(INTAKE_PATH), "dataset_idno")
    expected_by_key = expected_lookup(read_csv_dicts(EXPECTED_PATH))
    raw_counts = raw_manifest_counts(read_csv_dicts(RAW_FILE_MANIFEST_PATH))
    concept_by_id = concept_counts(read_csv_dicts(CONCEPT_PATH))

    gate_rows: list[dict[str, str]] = []
    file_rows: list[dict[str, str]] = []

    for wave in waves:
        idno = clean(wave.get("idno"))
        access = access_by_id.get(idno, {})
        intake = intake_by_id.get(idno, {})
        counts = raw_counts.get(idno, Counter())
        raw_tabular_count = safe_int(intake.get("raw_tabular_file_count"), counts.get("raw_tabular_file_count", 0))
        archive_count = safe_int(intake.get("archive_file_count"), counts.get("archive_file_count", 0))
        documentation_count = safe_int(intake.get("documentation_file_count"), counts.get("documentation_file_count", 0))
        file_count = safe_int(intake.get("file_count"), counts.get("file_count", 0))
        concept_rows, unverified_concepts, concept_text = concept_by_id.get(idno, (0, 0, ""))

        priority_files = queue_by_id.get(idno, [])
        wave_file_rows: list[dict[str, str]] = []
        present_count = 0
        for item in priority_files:
            file_name = clean(item.get("file_name"))
            expected = expected_by_key.get((idno, file_name.lower())) or expected_by_key.get((idno, normalize_file_name(file_name))) or {}
            expected_status = clean(expected.get("expected_file_status")) or "not_present"
            present_files = clean(expected.get("present_matching_files"))
            if expected_status in RAW_PRESENT_STATUSES:
                present_count += 1
            file_gate = file_gate_status(expected_status)
            row = {
                "acquisition_batch_rank": wave.get("acquisition_batch_rank", ""),
                "batch_role": wave.get("batch_role", ""),
                "country": wave.get("country", ""),
                "wave": wave.get("wave", ""),
                "idno": idno,
                "file_rank": item.get("file_rank", ""),
                "file_name": file_name,
                "local_target_folder": wave.get("local_target_folder", ""),
                "candidate_categories": item.get("candidate_categories", ""),
                "candidate_harmonized_variables": item.get("candidate_harmonized_variables", ""),
                "download_priority_reason": item.get("download_priority_reason", ""),
                "expected_file_status": expected_status,
                "present_matching_files": present_files,
                "current_file_gate_status": file_gate,
                "verification_action": clean(expected.get("verification_action")) or "download complete original raw package, then inspect raw values, labels, units, recall periods, missing codes, and merge keys",
            }
            wave_file_rows.append(row)

        missing_files = max(len(priority_files) - present_count, 0)
        direct_route = clean(access.get("direct_raw_route_status"))
        manual_action = clean(access.get("manual_action_status"))
        gate_status = current_gate_status(raw_tabular_count, archive_count, missing_files, unverified_concepts, direct_route)
        gate_row = {
            "acquisition_batch_rank": wave.get("acquisition_batch_rank", ""),
            "batch_role": wave.get("batch_role", ""),
            "country": wave.get("country", ""),
            "wave": wave.get("wave", ""),
            "idno": idno,
            "survey_name": wave.get("survey_name", ""),
            "official_url": wave.get("official_url", ""),
            "local_target_folder": wave.get("local_target_folder", ""),
            "folder_exists": intake.get("folder_exists", "0"),
            "file_count": str(file_count),
            "raw_tabular_file_count": str(raw_tabular_count),
            "archive_file_count": str(archive_count),
            "documentation_file_count": str(documentation_count),
            "priority_expected_file_rows": str(len(priority_files)),
            "priority_expected_files_present": str(present_count),
            "priority_expected_files_not_present": str(missing_files),
            "required_concept_rows": str(concept_rows),
            "required_concepts_unverified": str(unverified_concepts),
            "access_gate_detected": access.get("access_gate_detected", ""),
            "direct_raw_route_status": direct_route,
            "manual_action_status": manual_action,
            "current_gate_status": gate_status,
            "next_action": next_action_for(gate_status),
            "promotion_blockers": promotion_blockers(gate_status, missing_files, unverified_concepts, manual_action),
            "handoff_readme": "",
            "post_download_commands": "; ".join(POST_DOWNLOAD_COMMANDS),
        }
        gate_row["handoff_readme"] = write_handoff_readme(wave, wave_file_rows, gate_row)
        gate_rows.append(gate_row)
        file_rows.extend(wave_file_rows)

    role_counts = Counter(row["batch_role"] for row in gate_rows)
    country_count = len({row["country"] for row in gate_rows if row["batch_role"] == "priority_10_wave_batch"})
    status_counts = Counter(row["current_gate_status"] for row in gate_rows)
    file_status_counts = Counter(row["current_file_gate_status"] for row in file_rows)
    summary = [
        {"metric": "priority_raw_intake_gate_rows", "value": str(len(gate_rows)), "interpretation": "Priority acquisition and backup waves with raw-intake gates."},
        {"metric": "priority_raw_intake_priority_10_rows", "value": str(role_counts.get("priority_10_wave_batch", 0)), "interpretation": "Immediate priority wave rows covered by the raw-intake gate."},
        {"metric": "priority_raw_intake_priority_10_countries", "value": str(country_count), "interpretation": "Priority countries covered by the raw-intake gate."},
        {"metric": "priority_raw_intake_backup_rows", "value": str(role_counts.get("sixth_country_backup_candidate", 0)), "interpretation": "Sixth-country backup rows covered by the raw-intake gate."},
        {"metric": "priority_raw_file_target_rows", "value": str(len(file_rows)), "interpretation": "Priority file/module targets with current present/missing gate status."},
        {"metric": "priority_raw_file_targets_missing_rows", "value": str(file_status_counts.get("blocked_missing_raw_file", 0)), "interpretation": "Priority file targets still absent from raw-download folders."},
        {"metric": "priority_raw_gate_blocked_manual_rows", "value": str(status_counts.get("blocked_manual_raw_package_required", 0)), "interpretation": "Waves still blocked by missing complete original raw package."},
        {"metric": "priority_raw_gate_schema_ready_rows", "value": str(status_counts.get("ready_for_manual_value_label_unit_key_audit", 0)), "interpretation": "Waves ready for raw value/key/unit audit after current intake check."},
        {"metric": "priority_raw_handoff_readmes_written", "value": str(sum(1 for row in gate_rows if row["handoff_readme"])), "interpretation": "Per-target handoff README files written under temp/raw_downloads."},
        {"metric": "modeling_gate_status", "value": "blocked", "interpretation": "Models remain blocked until promoted registry thresholds and climate linkage gates pass."},
    ]
    return gate_rows, file_rows, summary


def write_report(gates: list[dict[str, str]], files: list[dict[str, str]], summary: list[dict[str, str]]) -> None:
    summary_rows = "\n".join(f"| {row['metric']} | {row['value']} | {row['interpretation']} |" for row in summary)
    status_counts = Counter(row["current_gate_status"] for row in gates)
    status_lines = "\n".join(f"| `{status}` | {count} |" for status, count in sorted(status_counts.items()))
    REPORT_PATH.write_text(
        f"""# Priority Raw Intake Gate

Status: priority acquisition handoff and fail-closed raw-intake gate. This
report does not promote country-waves into `data/`; it makes the manual raw
package placement and post-download verification requirements explicit for the
10-wave priority batch and sixth-country backups.

## Summary

| Metric | Value | Interpretation |
|---|---:|---|
{summary_rows}

## Gate Status

| Current gate status | Waves |
|---|---:|
{status_lines}

## Wave-Level Intake Gate

{markdown_table(gates, ['acquisition_batch_rank', 'batch_role', 'country', 'wave', 'idno', 'current_gate_status', 'priority_expected_files_not_present', 'required_concepts_unverified', 'handoff_readme'], 20)}

## File-Level Targets

{markdown_table(files, ['acquisition_batch_rank', 'idno', 'file_rank', 'file_name', 'current_file_gate_status', 'download_priority_reason'], 30)}

## Machine-Readable Outputs

- `temp/priority_raw_intake_gate.csv`
- `temp/priority_raw_file_targets.csv`
- `result/priority_raw_intake_gate_summary.csv`
- per-wave `temp/raw_downloads/<IDNO>/_PRIORITY_RAW_INTAKE_HANDOFF.md`
""",
        encoding="utf-8",
    )


def main() -> None:
    ensure_dirs()
    gates, files, summary = build_outputs()
    write_csv(GATE_PATH, gates, GATE_COLUMNS)
    write_csv(FILE_TARGET_PATH, files, FILE_TARGET_COLUMNS)
    write_csv(SUMMARY_PATH, summary, SUMMARY_COLUMNS)
    write_report(gates, files, summary)
    append_log(TEMP_DIR / "audit_log.md", f"Built priority raw intake gate waves={len(gates)} file_targets={len(files)}.")
    print(f"Priority raw intake gate waves={len(gates)} file_targets={len(files)}.")


if __name__ == "__main__":
    main()
