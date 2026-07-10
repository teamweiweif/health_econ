from __future__ import annotations

import csv
import re
import tarfile
import zipfile
from collections import defaultdict
from pathlib import Path, PurePosixPath
from typing import Any

from common import PROJECT_ROOT, REPORT_DIR, RESULT_DIR, TEMP_DIR, append_log, ensure_dirs, write_csv


ROUTE_DECISION_PATH = RESULT_DIR / "priority_lsms_isa_acquisition_route_decision.csv"
EXPECTED_FILE_MANIFEST_PATH = TEMP_DIR / "priority_lsms_isa_minimum_batch_expected_file_manifest.csv"
CORE_FILE_MANIFEST_PATH = TEMP_DIR / "priority_lsms_isa_minimum_batch_core_file_manifest.csv"

INCOMING_DIR = TEMP_DIR / "raw_downloads" / "_incoming"

ROUTER_PATH = RESULT_DIR / "priority_lsms_isa_scoped_incoming_package_router.csv"
EVIDENCE_PATH = RESULT_DIR / "priority_lsms_isa_scoped_incoming_package_router_evidence.csv"
SUMMARY_PATH = RESULT_DIR / "priority_lsms_isa_scoped_incoming_package_router_summary.csv"
REPORT_PATH = REPORT_DIR / "priority_lsms_isa_scoped_incoming_package_router.md"

ARCHIVE_SUFFIXES = {".zip", ".tar", ".tgz", ".gz"}

POST_COPY_VALIDATION_COMMANDS = (
    "python script/178_build_priority_lsms_isa_post_download_validation_runner.py --idno {idno}; "
    "python script/178_build_priority_lsms_isa_post_download_validation_runner.py --idno {idno} --execute; "
    "python script/199_build_priority_lsms_isa_acquisition_to_promotion_handoff.py; "
    "python script/200_build_priority_lsms_isa_dataset_scope_lock.py; "
    "python script/201_build_priority_lsms_isa_acquisition_route_decision.py; "
    "python script/202_build_priority_lsms_isa_scoped_incoming_package_router.py; "
    "python script/36_build_direct_read_audit_bundle.py; "
    "python script/14_validate_workspace.py"
)

ROUTER_COLUMNS = [
    "download_rank",
    "country",
    "wave",
    "idno",
    "scope_role",
    "priority_country",
    "sixth_country_candidate",
    "local_target_folder",
    "acquisition_route_decision",
    "expected_core_file_rows",
    "incoming_file_rows",
    "route_status",
    "top_incoming_relative_path",
    "top_incoming_file_name",
    "top_route_score",
    "second_route_score",
    "matched_expected_file_names",
    "matched_core_file_names",
    "copy_command_powershell",
    "post_copy_validation_commands",
    "next_action",
    "data_write_gate_status",
    "modeling_gate_status",
]

EVIDENCE_COLUMNS = [
    "download_rank",
    "country",
    "wave",
    "idno",
    "incoming_relative_path",
    "incoming_file_name",
    "incoming_bytes",
    "incoming_kind",
    "archive_read_status",
    "route_score",
    "expected_file_name_matches",
    "core_file_name_matches",
    "idno_hint_match",
    "catalog_hint_match",
    "country_year_hint_match",
    "matched_expected_file_names",
    "matched_core_file_names",
    "evidence_status",
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


def ps_quote(value: str) -> str:
    return "'" + value.replace("'", "''") + "'"


def file_key(value: str) -> str:
    text = clean(value).replace("\\", "/")
    if not text:
        return ""
    key = PurePosixPath(text).name.lower()
    if key.endswith(".nsdstat"):
        return key[: -len(".nsdstat")] + ".dta"
    return key


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
    return sorted(path for path in INCOMING_DIR.rglob("*") if path.is_file() and not path.name.startswith("_"))


def file_names_by_id(rows: list[dict[str, str]], field: str) -> dict[str, set[str]]:
    out: dict[str, set[str]] = defaultdict(set)
    for row in rows:
        idno = clean(row.get("idno"))
        key = file_key(row.get(field, ""))
        if idno and key:
            out[idno].add(key)
    return out


def catalog_id(row: dict[str, str]) -> str:
    text = clean(row.get("credentialed_download_url")) or clean(row.get("official_get_microdata_url"))
    match = re.search(r"/catalog/(\d+)", text)
    return match.group(1) if match else ""


def country_year_hint(text: str, row: dict[str, str]) -> int:
    low = text.lower()
    score = 0
    country = clean(row.get("country")).lower()
    if country and country in low:
        score += 1
    for token in clean(row.get("wave")).replace("-", " ").split():
        if len(token) == 4 and token in low:
            score += 1
            break
    return 1 if score >= 2 else 0


def incoming_keys(path: Path, members: list[str]) -> set[str]:
    keys = {file_key(path.name)}
    keys.update(file_key(member) for member in members)
    keys.discard("")
    return keys


def score_target(
    target: dict[str, str],
    path: Path,
    members: list[str],
    archive_status: str,
    expected_by_id: dict[str, set[str]],
    core_by_id: dict[str, set[str]],
) -> dict[str, str]:
    idno = clean(target.get("idno"))
    keys = incoming_keys(path, members)
    expected_matches = sorted(keys & expected_by_id.get(idno, set()))
    core_matches = sorted(keys & core_by_id.get(idno, set()))
    text = " ".join([path.name, *members]).lower()
    idno_hint = 1 if idno.lower() in text else 0
    catalog_hint = 1 if catalog_id(target) and catalog_id(target) in text else 0
    cy_hint = country_year_hint(text, target)
    score = len(expected_matches) * 10 + len(core_matches) * 25 + idno_hint * 100 + catalog_hint * 50 + cy_hint * 20
    status = "matched_candidate" if score > 0 else "no_match"
    return {
        "download_rank": clean(target.get("download_rank")),
        "country": clean(target.get("country")),
        "wave": clean(target.get("wave")),
        "idno": idno,
        "incoming_relative_path": rel(path),
        "incoming_file_name": path.name,
        "incoming_bytes": str(path.stat().st_size),
        "incoming_kind": "archive" if is_archive(path) else "direct_file",
        "archive_read_status": archive_status,
        "route_score": str(score),
        "expected_file_name_matches": str(len(expected_matches)),
        "core_file_name_matches": str(len(core_matches)),
        "idno_hint_match": str(idno_hint),
        "catalog_hint_match": str(catalog_hint),
        "country_year_hint_match": str(cy_hint),
        "matched_expected_file_names": ";".join(expected_matches[:30]),
        "matched_core_file_names": ";".join(core_matches[:30]),
        "evidence_status": status,
    }


def placeholder_evidence(target: dict[str, str], status: str) -> dict[str, str]:
    return {
        "download_rank": clean(target.get("download_rank")),
        "country": clean(target.get("country")),
        "wave": clean(target.get("wave")),
        "idno": clean(target.get("idno")),
        "evidence_status": status,
    }


def route_status(top: dict[str, str], second: dict[str, str], incoming_count: int) -> str:
    if incoming_count == 0:
        return "waiting_for_incoming_package"
    if not top or safe_int(top.get("route_score")) <= 0:
        return "manual_review_no_matching_incoming_file"
    if second and safe_int(top.get("route_score")) == safe_int(second.get("route_score")):
        return "manual_review_tied_incoming_files"
    return "copy_candidate_to_target_folder_after_review"


def build_plan_row(target: dict[str, str], rows: list[dict[str, str]], incoming_count: int) -> dict[str, str]:
    sorted_rows = sorted(rows, key=lambda row: safe_int(row.get("route_score")), reverse=True)
    top = sorted_rows[0] if sorted_rows else {}
    second = sorted_rows[1] if len(sorted_rows) > 1 else {}
    status = route_status(top, second, incoming_count)
    local_target = clean(target.get("local_target_folder"))
    command = ""
    validation_commands = ""
    if status == "copy_candidate_to_target_folder_after_review":
        source = PROJECT_ROOT / clean(top.get("incoming_relative_path")).replace("/", "\\")
        destination = PROJECT_ROOT / local_target.replace("/", "\\") / clean(top.get("incoming_file_name"))
        command = (
            f"New-Item -ItemType Directory -Force -Path {ps_quote(str(destination.parent))} | Out-Null; "
            f"Copy-Item -LiteralPath {ps_quote(str(source))} -Destination {ps_quote(str(destination))} -Force"
        )
        validation_commands = POST_COPY_VALIDATION_COMMANDS.format(idno=clean(target.get("idno")))
        next_action = "Review the route, copy the official package into the target folder, then run post-copy validation."
    elif status == "waiting_for_incoming_package":
        next_action = "Place the complete unchanged official package in temp/raw_downloads/_incoming or the exact target folder."
    elif status == "manual_review_tied_incoming_files":
        next_action = "Inspect tied incoming files before copying; the router is fail-closed on ambiguous matches."
    else:
        next_action = "Inspect incoming files manually or rename with the target IDNO before rerunning the router."

    return {
        "download_rank": clean(target.get("download_rank")),
        "country": clean(target.get("country")),
        "wave": clean(target.get("wave")),
        "idno": clean(target.get("idno")),
        "scope_role": clean(target.get("scope_role")),
        "priority_country": clean(target.get("priority_country")),
        "sixth_country_candidate": clean(target.get("sixth_country_candidate")),
        "local_target_folder": local_target,
        "acquisition_route_decision": clean(target.get("acquisition_route_decision")),
        "expected_core_file_rows": clean(target.get("expected_core_file_rows")),
        "incoming_file_rows": str(incoming_count),
        "route_status": status,
        "top_incoming_relative_path": clean(top.get("incoming_relative_path")),
        "top_incoming_file_name": clean(top.get("incoming_file_name")),
        "top_route_score": clean(top.get("route_score")),
        "second_route_score": clean(second.get("route_score")),
        "matched_expected_file_names": clean(top.get("matched_expected_file_names")),
        "matched_core_file_names": clean(top.get("matched_core_file_names")),
        "copy_command_powershell": command,
        "post_copy_validation_commands": validation_commands,
        "next_action": next_action,
        "data_write_gate_status": "blocked_no_data_write",
        "modeling_gate_status": "blocked",
    }


def build_outputs() -> tuple[list[dict[str, str]], list[dict[str, str]], list[dict[str, str]]]:
    targets = [row for row in read_csv_dicts(ROUTE_DECISION_PATH) if clean(row.get("idno"))]
    expected_by_id = file_names_by_id(read_csv_dicts(EXPECTED_FILE_MANIFEST_PATH), "file_name")
    core_by_id = file_names_by_id(read_csv_dicts(CORE_FILE_MANIFEST_PATH), "expected_file_name")
    files = incoming_files()

    evidence_by_id: dict[str, list[dict[str, str]]] = defaultdict(list)
    if files:
        for path in files:
            if is_archive(path):
                archive_status, members = archive_members(path)
            else:
                archive_status, members = "not_archive", []
            for target in targets:
                scored = score_target(target, path, members, archive_status, expected_by_id, core_by_id)
                if safe_int(scored.get("route_score")) > 0:
                    evidence_by_id[clean(target.get("idno"))].append(scored)

    evidence_rows: list[dict[str, str]] = []
    plan_rows: list[dict[str, str]] = []
    for target in sorted(targets, key=lambda row: safe_int(row.get("download_rank"), 9999)):
        idno = clean(target.get("idno"))
        rows = evidence_by_id.get(idno, [])
        if not rows:
            evidence_rows.append(placeholder_evidence(target, "waiting_for_incoming_package" if not files else "no_matching_incoming_file"))
        else:
            evidence_rows.extend(sorted(rows, key=lambda row: safe_int(row.get("route_score")), reverse=True))
        plan_rows.append(build_plan_row(target, rows, len(files)))

    status_counts = defaultdict(int)
    for row in plan_rows:
        status_counts[clean(row.get("route_status"))] += 1

    countries = {clean(row.get("country")) for row in plan_rows if clean(row.get("country"))}
    summary_rows = [
        {"metric": "scoped_incoming_router_target_rows", "value": str(len(plan_rows)), "interpretation": "Download-required waves from the locked 10-wave route decision scope."},
        {"metric": "scoped_incoming_router_country_rows", "value": str(len(countries)), "interpretation": "Countries covered by the scoped incoming router."},
        {"metric": "scoped_incoming_router_priority_country_rows", "value": str(sum(1 for row in plan_rows if row.get("priority_country") == "1")), "interpretation": "Rows from Ethiopia, Nigeria, Malawi, Tanzania, or Uganda."},
        {"metric": "scoped_incoming_router_sixth_country_rows", "value": str(sum(1 for row in plan_rows if row.get("sixth_country_candidate") == "1")), "interpretation": "Rows supplying the sixth country."},
        {"metric": "scoped_incoming_router_incoming_file_rows", "value": str(len(files)), "interpretation": "Files currently staged under temp/raw_downloads/_incoming."},
        {"metric": "scoped_incoming_router_candidate_evidence_rows", "value": str(len(evidence_rows)), "interpretation": "Incoming-package evidence rows, including fail-closed waiting rows."},
        {"metric": "scoped_incoming_router_expected_core_file_rows", "value": str(sum(safe_int(row.get("expected_core_file_rows")) for row in plan_rows)), "interpretation": "Expected core-file checks across the 10 target waves."},
        {"metric": "scoped_incoming_router_copy_candidate_rows", "value": str(status_counts.get("copy_candidate_to_target_folder_after_review", 0)), "interpretation": "Targets with a single suggested incoming file to copy after review."},
        {"metric": "scoped_incoming_router_pending_drop_rows", "value": str(status_counts.get("waiting_for_incoming_package", 0)), "interpretation": "Targets still waiting for an incoming package drop."},
        {"metric": "scoped_incoming_router_manual_review_rows", "value": str(status_counts.get("manual_review_no_matching_incoming_file", 0) + status_counts.get("manual_review_tied_incoming_files", 0)), "interpretation": "Targets requiring manual route review."},
        {"metric": "data_write_gate_status", "value": "blocked_no_data_write", "interpretation": "The router only writes manifests and reports."},
        {"metric": "modeling_gate_status", "value": "blocked", "interpretation": "No modeling is opened by incoming package routing."},
        *[
            {"metric": f"scoped_incoming_router_status_{status}", "value": str(count), "interpretation": "Scoped incoming router route status count."}
            for status, count in sorted(status_counts.items())
        ],
    ]
    return plan_rows, evidence_rows, summary_rows


def markdown_table(rows: list[dict[str, str]], columns: list[str], limit: int = 30) -> str:
    if not rows:
        return "_No rows._"
    lines = ["| " + " | ".join(columns) + " |", "| " + " | ".join("---" for _ in columns) + " |"]
    for row in rows[:limit]:
        values: list[str] = []
        for column in columns:
            value = clean(row.get(column)).replace("|", "/")
            if len(value) > 110:
                value = value[:107] + "..."
            values.append(value)
        lines.append("| " + " | ".join(values) + " |")
    if len(rows) > limit:
        lines.append("| " + " | ".join("..." for _ in columns) + " |")
    return "\n".join(lines)


def write_report(plan_rows: list[dict[str, str]], evidence_rows: list[dict[str, str]], summary_rows: list[dict[str, str]]) -> None:
    REPORT_PATH.write_text(
        f"""# Priority LSMS/ISA Scoped Incoming Package Router

Status: non-destructive incoming-package router for the locked 10 download-required
LSMS/ISA country-waves.

This artifact is narrower than the older broad incoming router. It uses
`result/priority_lsms_isa_acquisition_route_decision.csv` as the scope lock, so
the rows match the current dataset-promotion target: Ethiopia, Nigeria, Tanzania,
Uganda, and Nepal download-required waves, with Malawi 2004 retained as the
already promoted anchor outside this incoming queue.

It scans `temp/raw_downloads/_incoming/`, scores any files found there against
official expected filenames, core-file manifests, IDNO hints, catalog IDs, and
country/year hints. It does not download, move, delete, extract, write `data/`,
or promote any wave.

## Summary

{markdown_table(summary_rows, ['metric', 'value', 'interpretation'], 30)}

## Target Route Plan

{markdown_table(plan_rows, ['download_rank', 'country', 'wave', 'idno', 'route_status', 'top_incoming_file_name', 'top_route_score', 'local_target_folder'], 20)}

## Evidence Preview

{markdown_table(evidence_rows, ['download_rank', 'idno', 'incoming_file_name', 'route_score', 'expected_file_name_matches', 'core_file_name_matches', 'evidence_status'], 40)}

## Use Rule

Only run a generated copy command after confirming the incoming file is an
unchanged official World Bank package for that wave. Copying a package into the
target folder starts receipt/schema/value/semantics validation; it does not make
the wave analysis-ready.
""",
        encoding="utf-8",
    )


def main() -> None:
    ensure_dirs()
    INCOMING_DIR.mkdir(parents=True, exist_ok=True)
    plan_rows, evidence_rows, summary_rows = build_outputs()
    write_csv(ROUTER_PATH, plan_rows, ROUTER_COLUMNS)
    write_csv(EVIDENCE_PATH, evidence_rows, EVIDENCE_COLUMNS)
    write_csv(SUMMARY_PATH, summary_rows, SUMMARY_COLUMNS)
    write_report(plan_rows, evidence_rows, summary_rows)
    append_log(TEMP_DIR / "audit_log.md", f"Built priority LSMS/ISA scoped incoming package router rows={len(plan_rows)}.")
    print(f"Priority LSMS/ISA scoped incoming package router rows={len(plan_rows)} evidence_rows={len(evidence_rows)}.")


if __name__ == "__main__":
    main()
