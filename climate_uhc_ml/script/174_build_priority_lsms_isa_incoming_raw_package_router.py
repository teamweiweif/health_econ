from __future__ import annotations

import csv
import tarfile
import zipfile
from collections import defaultdict
from pathlib import Path, PurePosixPath
from typing import Any

from common import PROJECT_ROOT, REPORT_DIR, RESULT_DIR, TEMP_DIR, append_log, ensure_dirs, write_csv


ACTION_QUEUE_PATH = TEMP_DIR / "priority_lsms_isa_next_raw_package_action_queue.csv"
FULL_FILE_MANIFEST_PATH = TEMP_DIR / "priority_lsms_isa_credentialed_raw_full_file_manifest.csv"
CORE_FILE_CHECKLIST_PATH = TEMP_DIR / "priority_lsms_isa_credentialed_raw_core_file_checklist.csv"

INCOMING_DIR = TEMP_DIR / "raw_downloads" / "_incoming"
TARGET_ROOT = TEMP_DIR / "raw_downloads"

CANDIDATE_PATH = TEMP_DIR / "priority_lsms_isa_incoming_raw_package_route_candidates.csv"
PLAN_PATH = TEMP_DIR / "priority_lsms_isa_incoming_raw_package_route_plan.csv"
SUMMARY_PATH = RESULT_DIR / "priority_lsms_isa_incoming_raw_package_router_summary.csv"
REPORT_PATH = REPORT_DIR / "priority_lsms_isa_incoming_raw_package_router.md"
INCOMING_README_PATH = INCOMING_DIR / "_README_PLACE_DOWNLOADED_RAW_PACKAGES_HERE.md"

ARCHIVE_SUFFIXES = {".zip", ".tar", ".tgz", ".gz"}
DATA_SUFFIXES = {".dta", ".sav", ".por", ".sas7bdat", ".xpt", ".csv", ".tsv", ".xlsx", ".xls", ".zip", ".tar", ".tgz", ".gz", ".rar", ".7z"}

POST_ROUTE_COMMANDS = (
    "python script/17_audit_raw_downloads.py; "
    "python script/144_build_priority_lsms_isa_raw_package_intake_packet.py; "
    "python script/145_build_priority_lsms_isa_archive_member_preflight.py; "
    "python script/150_build_priority_lsms_isa_raw_package_receipt_checklist.py; "
    "python script/153_validate_priority_lsms_isa_official_file_receipt.py; "
    "python script/157_build_priority_lsms_isa_received_raw_schema_audit.py; "
    "python script/158_build_priority_lsms_isa_received_raw_value_profile.py; "
    "python script/159_build_priority_lsms_isa_received_raw_semantics_review.py; "
    "python script/148_build_priority_lsms_isa_country_wave_promotion_packets.py; "
    "python script/151_refresh_refocused_promoted_country_wave_registry.py; "
    "python script/172_build_priority_lsms_isa_next_raw_package_action_packet.py; "
    "python script/173_build_priority_lsms_isa_promotion_gate_dashboard.py; "
    "python script/36_build_direct_read_audit_bundle.py; "
    "python script/14_validate_workspace.py"
)

CANDIDATE_COLUMNS = [
    "incoming_relative_path",
    "incoming_file_name",
    "incoming_bytes",
    "incoming_kind",
    "archive_read_status",
    "candidate_rank",
    "candidate_idno",
    "candidate_country",
    "candidate_wave",
    "candidate_target_folder",
    "expected_file_rows",
    "expected_file_name_matches",
    "core_file_rows",
    "core_file_name_matches",
    "idno_hint_match",
    "catalog_hint_match",
    "country_year_hint_match",
    "route_score",
    "matched_expected_file_names",
    "matched_core_file_names",
]

PLAN_COLUMNS = [
    "incoming_relative_path",
    "incoming_file_name",
    "incoming_bytes",
    "incoming_kind",
    "route_decision",
    "selected_idno",
    "selected_country",
    "selected_wave",
    "selected_target_folder",
    "top_route_score",
    "second_route_score",
    "matched_expected_file_names",
    "matched_core_file_names",
    "copy_command_powershell",
    "post_route_validation_commands",
    "next_action",
]

SUMMARY_COLUMNS = ["metric", "value", "interpretation"]


def read_csv_dicts(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        return []
    with path.open(encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def clean(value: Any) -> str:
    if value is None:
        return ""
    return " ".join(str(value).split())


def safe_int(value: Any, default: int = 0) -> int:
    try:
        text = clean(value)
        return int(float(text)) if text else default
    except (TypeError, ValueError):
        return default


def rel(path: Path) -> str:
    try:
        return str(path.relative_to(PROJECT_ROOT)).replace("\\", "/")
    except ValueError:
        return str(path).replace("\\", "/")


def file_key(value: str) -> str:
    text = clean(value).replace("\\", "/")
    if not text:
        return ""
    key = PurePosixPath(text).name.lower()
    if key.endswith(".nsdstat"):
        return key[: -len(".nsdstat")] + ".dta"
    return key


def folder_from_row(row: dict[str, str]) -> str:
    folder = clean(row.get("local_target_folder")).replace("\\", "/").strip("/")
    if folder:
        return folder + "/"
    return f"temp/raw_downloads/{clean(row.get('idno'))}/"


def ps_quote(path: str) -> str:
    return "'" + path.replace("'", "''") + "'"


def is_archive(path: Path) -> bool:
    lower = path.name.lower()
    return path.suffix.lower() in ARCHIVE_SUFFIXES or lower.endswith(".tar.gz")


def archive_members(path: Path) -> tuple[str, list[str]]:
    try:
        if zipfile.is_zipfile(path):
            with zipfile.ZipFile(path) as zf:
                return "readable_zip", [info.filename for info in zf.infolist() if not info.is_dir()]
        if tarfile.is_tarfile(path):
            with tarfile.open(path) as tf:
                return "readable_tar", [info.name for info in tf.getmembers() if info.isfile()]
        return "unsupported_or_unreadable_archive", []
    except (OSError, RuntimeError, tarfile.TarError, zipfile.BadZipFile):
        return "unsupported_or_unreadable_archive", []


def incoming_files() -> list[Path]:
    if not INCOMING_DIR.exists():
        return []
    return sorted(
        path
        for path in INCOMING_DIR.rglob("*")
        if path.is_file() and not path.name.startswith("_")
    )


def expected_by_id(rows: list[dict[str, str]], field: str = "file_name") -> dict[str, set[str]]:
    out: dict[str, set[str]] = defaultdict(set)
    for row in rows:
        idno = clean(row.get("idno"))
        key = file_key(row.get(field, ""))
        if idno and key:
            out[idno].add(key)
    return out


def candidate_seed_rows(action_rows: list[dict[str, str]]) -> list[dict[str, str]]:
    out: list[dict[str, str]] = []
    for row in action_rows:
        idno = clean(row.get("idno"))
        if not idno:
            continue
        out.append(
            {
                "idno": idno,
                "country": clean(row.get("country")),
                "wave": clean(row.get("wave")),
                "local_target_folder": folder_from_row(row),
            }
        )
    return out


def token_hint(text: str, row: dict[str, str]) -> int:
    low = text.lower()
    score = 0
    idno = clean(row.get("idno")).lower()
    country = clean(row.get("country")).lower()
    wave = clean(row.get("wave")).lower()
    if idno and idno.lower() in low:
        score += 1
    if country and country in low:
        score += 1
    for token in wave.replace("-", " ").split():
        if len(token) == 4 and token in low:
            score += 1
            break
    return score


def catalog_id_by_id(full_rows: list[dict[str, str]]) -> dict[str, str]:
    out: dict[str, str] = {}
    for row in full_rows:
        idno = clean(row.get("idno"))
        catalog_id = clean(row.get("catalog_id"))
        if idno and catalog_id and idno not in out:
            out[idno] = catalog_id
    return out


def score_file(
    path: Path,
    member_names: list[str],
    archive_status: str,
    seeds: list[dict[str, str]],
    expected_files: dict[str, set[str]],
    core_files: dict[str, set[str]],
    catalog_ids: dict[str, str],
) -> list[dict[str, str]]:
    keys = {file_key(path.name)}
    keys.update(file_key(member) for member in member_names)
    keys.discard("")
    text = " ".join([path.name, *member_names]).lower()
    rows: list[dict[str, str]] = []
    for seed in seeds:
        idno = seed["idno"]
        expected = expected_files.get(idno, set())
        core = core_files.get(idno, set())
        expected_matches = sorted(keys & expected)
        core_matches = sorted(keys & core)
        idno_hint = 1 if clean(idno).lower() in text else 0
        catalog_hint = 1 if catalog_ids.get(idno) and catalog_ids[idno] in text else 0
        country_year_hint = 1 if token_hint(text, seed) >= 2 else 0
        score = len(expected_matches) * 10 + len(core_matches) * 25 + idno_hint * 100 + catalog_hint * 50 + country_year_hint * 20
        if score <= 0:
            continue
        rows.append(
            {
                "incoming_relative_path": rel(path),
                "incoming_file_name": path.name,
                "incoming_bytes": str(path.stat().st_size),
                "incoming_kind": "archive" if is_archive(path) else "direct_file",
                "archive_read_status": archive_status,
                "candidate_idno": idno,
                "candidate_country": seed["country"],
                "candidate_wave": seed["wave"],
                "candidate_target_folder": seed["local_target_folder"],
                "expected_file_rows": str(len(expected)),
                "expected_file_name_matches": str(len(expected_matches)),
                "core_file_rows": str(len(core)),
                "core_file_name_matches": str(len(core_matches)),
                "idno_hint_match": str(idno_hint),
                "catalog_hint_match": str(catalog_hint),
                "country_year_hint_match": str(country_year_hint),
                "route_score": str(score),
                "matched_expected_file_names": ";".join(expected_matches[:20]),
                "matched_core_file_names": ";".join(core_matches[:20]),
            }
        )
    rows.sort(key=lambda row: safe_int(row.get("route_score")), reverse=True)
    for idx, row in enumerate(rows, start=1):
        row["candidate_rank"] = str(idx)
    return rows


def plan_for_file(path: Path, candidate_rows: list[dict[str, str]]) -> dict[str, str]:
    top = candidate_rows[0] if candidate_rows else {}
    second_score = safe_int(candidate_rows[1].get("route_score")) if len(candidate_rows) > 1 else 0
    top_score = safe_int(top.get("route_score")) if top else 0
    if not top:
        decision = "manual_review_no_route_candidate"
        next_action = "Keep this file in _incoming and inspect manually; no official expected-file or IDNO hints matched."
        target_folder = ""
        command = ""
    elif top_score == second_score:
        decision = "manual_review_ambiguous_route"
        next_action = "Multiple country-waves have the same top route score; inspect archive contents and rename or place manually."
        target_folder = clean(top.get("candidate_target_folder"))
        command = ""
    else:
        decision = "copy_candidate_to_target_folder"
        next_action = "Review the suggested target, then copy the incoming file to the target folder and rerun post-route validation."
        target_folder = clean(top.get("candidate_target_folder"))
        target = PROJECT_ROOT / target_folder.replace("/", "\\") / path.name
        command = f"New-Item -ItemType Directory -Force -Path {ps_quote(str(target.parent))} | Out-Null; Copy-Item -LiteralPath {ps_quote(str(path))} -Destination {ps_quote(str(target))} -Force"
    return {
        "incoming_relative_path": rel(path),
        "incoming_file_name": path.name,
        "incoming_bytes": str(path.stat().st_size),
        "incoming_kind": "archive" if is_archive(path) else "direct_file",
        "route_decision": decision,
        "selected_idno": clean(top.get("candidate_idno")),
        "selected_country": clean(top.get("candidate_country")),
        "selected_wave": clean(top.get("candidate_wave")),
        "selected_target_folder": target_folder,
        "top_route_score": str(top_score),
        "second_route_score": str(second_score),
        "matched_expected_file_names": clean(top.get("matched_expected_file_names")),
        "matched_core_file_names": clean(top.get("matched_core_file_names")),
        "copy_command_powershell": command,
        "post_route_validation_commands": POST_ROUTE_COMMANDS if command else "",
        "next_action": next_action,
    }


def markdown_table(rows: list[dict[str, str]], columns: list[str], limit: int = 30) -> str:
    if not rows:
        return "_No rows._"
    lines = ["| " + " | ".join(columns) + " |", "| " + " | ".join("---" for _ in columns) + " |"]
    for row in rows[:limit]:
        values = []
        for column in columns:
            value = clean(row.get(column)).replace("|", "/")
            if len(value) > 120:
                value = value[:117] + "..."
            values.append(value)
        lines.append("| " + " | ".join(values) + " |")
    if len(rows) > limit:
        lines.append("| " + " | ".join("..." for _ in columns) + " |")
    return "\n".join(lines)


def build_outputs() -> tuple[list[dict[str, str]], list[dict[str, str]], list[dict[str, str]]]:
    full_rows = read_csv_dicts(FULL_FILE_MANIFEST_PATH)
    core_rows = read_csv_dicts(CORE_FILE_CHECKLIST_PATH)
    seeds = candidate_seed_rows(read_csv_dicts(ACTION_QUEUE_PATH))
    expected_files = expected_by_id(full_rows)
    core_files = expected_by_id(core_rows)
    catalog_ids = catalog_id_by_id(full_rows)

    candidate_rows: list[dict[str, str]] = []
    plan_rows: list[dict[str, str]] = []
    files = incoming_files()
    for path in files:
        if is_archive(path):
            archive_status, members = archive_members(path)
        else:
            archive_status, members = "not_archive", []
        rows = score_file(path, members, archive_status, seeds, expected_files, core_files, catalog_ids)
        candidate_rows.extend(rows)
        plan_rows.append(plan_for_file(path, rows))

    summary_rows = [
        {"metric": "priority_lsms_incoming_router_incoming_folder_exists", "value": "1" if INCOMING_DIR.exists() else "0", "interpretation": "Whether temp/raw_downloads/_incoming exists."},
        {"metric": "priority_lsms_incoming_router_action_country_wave_rows", "value": str(len(seeds)), "interpretation": "Country-waves considered by the incoming raw package router."},
        {"metric": "priority_lsms_incoming_router_incoming_file_rows", "value": str(len(files)), "interpretation": "Files currently found under the incoming raw package folder."},
        {"metric": "priority_lsms_incoming_router_candidate_rows", "value": str(len(candidate_rows)), "interpretation": "Scored incoming-file to country-wave route candidates."},
        {"metric": "priority_lsms_incoming_router_copy_candidate_rows", "value": str(sum(1 for row in plan_rows if row.get("route_decision") == "copy_candidate_to_target_folder")), "interpretation": "Incoming files with a single top suggested target folder."},
        {"metric": "priority_lsms_incoming_router_manual_review_rows", "value": str(sum(1 for row in plan_rows if row.get("route_decision", "").startswith("manual_review"))), "interpretation": "Incoming files that require manual route review."},
        {"metric": "priority_lsms_incoming_router_data_write_status", "value": "blocked_no_data_write", "interpretation": "Routing suggestions do not permit data/ writes."},
        {"metric": "modeling_gate_status", "value": "blocked", "interpretation": "No predictive, reduced-form, causal ML, or policy learning until registry thresholds pass."},
    ]
    return candidate_rows, plan_rows, summary_rows


def write_incoming_readme() -> None:
    INCOMING_DIR.mkdir(parents=True, exist_ok=True)
    INCOMING_README_PATH.write_text(
        f"""# Incoming Raw Package Drop Folder

Place newly downloaded official World Bank raw packages here first if you are
not sure which `temp/raw_downloads/<IDNO>/` target folder they belong to.

Then run from `climate_uhc_ml/`:

```bash
python script/174_build_priority_lsms_isa_incoming_raw_package_router.py
```

Review `temp/priority_lsms_isa_incoming_raw_package_route_plan.csv`. The router
does not move or delete incoming files. It only writes suggested copy commands
based on official expected filenames, core-file manifests, IDNO hints, and
catalog hints.

After copying files to the suggested target folder, run:

```bash
{POST_ROUTE_COMMANDS}
```
""",
        encoding="utf-8",
    )


def write_report(candidate_rows: list[dict[str, str]], plan_rows: list[dict[str, str]], summary_rows: list[dict[str, str]]) -> None:
    REPORT_PATH.write_text(
        f"""# Priority LSMS/ISA Incoming Raw Package Router

Status: non-destructive routing audit for manually downloaded raw packages.

This router scans `temp/raw_downloads/_incoming/` and scores each incoming file
against the refocused LSMS/ISA action queue using official expected filenames,
core-file names, IDNO hints, country/year hints, and catalog IDs. It does not
download, move, delete, extract, or promote data.

## Summary

{markdown_table(summary_rows, ['metric', 'value', 'interpretation'], 20)}

## Route Plan

{markdown_table(plan_rows, ['incoming_file_name', 'route_decision', 'selected_idno', 'selected_target_folder', 'top_route_score', 'second_route_score'], 40)}

## Candidate Preview

{markdown_table(candidate_rows, ['incoming_file_name', 'candidate_rank', 'candidate_idno', 'route_score', 'expected_file_name_matches', 'core_file_name_matches'], 80)}

## Rule

Only review and run a generated copy command after checking that the incoming
file is an unchanged official package from the World Bank get-microdata workflow.
Copying a file to a target folder still only starts receipt validation; it does
not make a country-wave analysis-ready.
""",
        encoding="utf-8",
    )


def main() -> None:
    ensure_dirs()
    write_incoming_readme()
    candidate_rows, plan_rows, summary_rows = build_outputs()
    write_csv(CANDIDATE_PATH, candidate_rows, CANDIDATE_COLUMNS)
    write_csv(PLAN_PATH, plan_rows, PLAN_COLUMNS)
    write_csv(SUMMARY_PATH, summary_rows, SUMMARY_COLUMNS)
    write_report(candidate_rows, plan_rows, summary_rows)
    append_log(
        TEMP_DIR / "audit_log.md",
        f"Built priority LSMS/ISA incoming raw package router incoming_files={len(plan_rows)} candidates={len(candidate_rows)}.",
    )
    print(f"Priority LSMS/ISA incoming raw package router incoming_files={len(plan_rows)} candidates={len(candidate_rows)}.")


if __name__ == "__main__":
    main()
