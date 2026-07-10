from __future__ import annotations

import csv
from collections import Counter, defaultdict
from pathlib import Path, PurePosixPath
from typing import Any

from common import PROJECT_ROOT, REPORT_DIR, RESULT_DIR, TEMP_DIR, append_log, ensure_dirs, write_csv


QUEUE_PATH = TEMP_DIR / "priority_lsms_isa_refocused_acquisition_queue.csv"
FULL_EXPECTED_PATH = TEMP_DIR / "priority_lsms_isa_credentialed_raw_full_file_manifest.csv"
CORE_EXPECTED_PATH = TEMP_DIR / "priority_lsms_isa_credentialed_raw_core_file_checklist.csv"
LOCAL_FILE_MANIFEST_PATH = TEMP_DIR / "priority_lsms_isa_raw_package_file_manifest.csv"
ARCHIVE_MEMBER_PATH = TEMP_DIR / "priority_lsms_isa_archive_member_manifest.csv"

DATASET_VALIDATION_PATH = TEMP_DIR / "priority_lsms_isa_official_file_receipt_validation.csv"
FULL_FILE_MATCH_PATH = TEMP_DIR / "priority_lsms_isa_official_file_receipt_file_match.csv"
CORE_FILE_MATCH_PATH = TEMP_DIR / "priority_lsms_isa_official_file_receipt_core_match.csv"
SUMMARY_PATH = RESULT_DIR / "priority_lsms_isa_official_file_receipt_validator_summary.csv"
REPORT_PATH = REPORT_DIR / "priority_lsms_isa_official_file_receipt_validator.md"

RAW_ROOT = TEMP_DIR / "raw_downloads"

POST_RECEIPT_COMMANDS = (
    "python script/17_audit_raw_downloads.py; "
    "python script/144_build_priority_lsms_isa_raw_package_intake_packet.py; "
    "python script/145_build_priority_lsms_isa_archive_member_preflight.py; "
    "python script/150_build_priority_lsms_isa_raw_package_receipt_checklist.py; "
    "python script/152_build_priority_lsms_isa_credentialed_raw_acquisition_workbench.py; "
    "python script/153_validate_priority_lsms_isa_official_file_receipt.py; "
    "python script/154_build_priority_lsms_isa_threshold_download_sequence.py; "
    "python script/155_build_priority_lsms_isa_minimum_batch_raw_intake_guide.py; "
    "python script/156_probe_priority_lsms_isa_minimum_batch_endpoint_refresh.py; "
    "python script/149_build_priority_lsms_isa_raw_value_verification_workbook.py; "
    "python script/132_build_priority_analysis_dataset_synthesis_blueprint.py; "
    "python script/148_build_priority_lsms_isa_country_wave_promotion_packets.py; "
    "python script/151_refresh_refocused_promoted_country_wave_registry.py; "
    "python script/127_enforce_promoted_data_gate.py; "
    "python script/36_build_direct_read_audit_bundle.py; "
    "python script/14_validate_workspace.py"
)

DATASET_COLUMNS = [
    "download_priority_order",
    "queue_role",
    "country",
    "wave",
    "idno",
    "survey_name",
    "local_target_folder",
    "official_expected_file_rows",
    "official_expected_matched_rows",
    "official_expected_missing_rows",
    "official_expected_match_rate",
    "official_core_file_rows",
    "official_core_matched_rows",
    "official_core_missing_rows",
    "official_core_match_rate",
    "local_original_file_rows",
    "local_archive_member_rows",
    "local_generated_handoff_rows",
    "official_file_receipt_status",
    "next_action",
    "post_receipt_commands",
    "handoff_readme",
]

FULL_MATCH_COLUMNS = [
    "download_priority_order",
    "queue_role",
    "country",
    "wave",
    "idno",
    "file_id",
    "expected_file_name",
    "expected_file_key",
    "file_description",
    "priority_core_target",
    "official_file_match_status",
    "matched_local_locations",
    "matched_source_types",
]

CORE_MATCH_COLUMNS = [
    "download_priority_order",
    "queue_role",
    "country",
    "wave",
    "idno",
    "requirement",
    "file_rank",
    "file_id",
    "expected_file_name",
    "expected_file_key",
    "candidate_variable_rows",
    "strong_candidate_variable_rows",
    "top_variable_names",
    "official_core_file_match_status",
    "matched_local_locations",
]

SUMMARY_COLUMNS = ["metric", "value", "interpretation"]

RAW_FILE_ALIAS_EXTENSIONS = (
    ".dta",
    ".sav",
    ".por",
    ".sas7bdat",
    ".xpt",
    ".csv",
    ".txt",
    ".xlsx",
    ".xls",
)


def read_csv_dicts(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        return []
    with path.open(encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def clean(value: Any) -> str:
    return "" if value is None else str(value).strip()


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


def compact(values: list[str], limit: int = 8) -> str:
    seen: set[str] = set()
    out: list[str] = []
    for value in values:
        text = " ".join(clean(value).split())
        if text and text not in seen:
            out.append(text)
            seen.add(text)
        if len(out) >= limit:
            break
    return ";".join(out)


def file_key(value: str) -> str:
    text = clean(value).replace("\\", "/")
    if not text:
        return ""
    return PurePosixPath(text).name.lower()


def expected_file_lookup_keys(expected_name: str) -> list[tuple[str, str]]:
    key = file_key(expected_name)
    if not key:
        return []
    keys = [("exact", key)]
    if key.endswith(".nsdstat"):
        stem = key[: -len(".nsdstat")]
        keys.extend((f"alias_nsdstat_to_{ext.lstrip('.')}", f"{stem}{ext}") for ext in RAW_FILE_ALIAS_EXTENSIONS)
    elif not PurePosixPath(key).suffix:
        keys.extend((f"alias_extensionless_to_{ext.lstrip('.')}", f"{key}{ext}") for ext in RAW_FILE_ALIAS_EXTENSIONS)
    return keys


def matched_locations(
    actual_by_id_key: dict[str, dict[str, list[str]]],
    idno: str,
    expected_name: str,
) -> list[str]:
    for method, key in expected_file_lookup_keys(expected_name):
        locations = actual_by_id_key.get(idno, {}).get(key, [])
        if locations and method == "exact":
            return locations
        if locations:
            return [f"{location}[{method}]" for location in locations]
    return []


def source_type(location: str) -> str:
    base = "archive" if location.startswith("archive:") else "direct"
    if "[alias_" in location:
        alias = location.rsplit("[", 1)[-1].rstrip("]")
        return f"{base}_{alias}"
    return base


def raw_folder_path(folder: str, idno: str) -> Path:
    folder_clean = clean(folder).replace("\\", "/").strip("/")
    if folder_clean:
        return PROJECT_ROOT / folder_clean
    return RAW_ROOT / idno


def pct(numerator: int, denominator: int) -> str:
    if denominator <= 0:
        return "0.000"
    return f"{numerator / denominator:.3f}"


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


def local_actual_file_index(
    local_manifest_rows: list[dict[str, str]],
    archive_member_rows: list[dict[str, str]],
) -> tuple[dict[str, dict[str, list[str]]], Counter[str], Counter[str]]:
    by_id_key: dict[str, dict[str, list[str]]] = defaultdict(lambda: defaultdict(list))
    original_counts: Counter[str] = Counter()
    generated_counts: Counter[str] = Counter()
    member_counts: Counter[str] = Counter()

    for row in local_manifest_rows:
        idno = clean(row.get("idno"))
        if not idno:
            continue
        if clean(row.get("generated_or_original")) == "generated":
            generated_counts[idno] += 1
            continue
        original_counts[idno] += 1
        key = file_key(row.get("file_name", ""))
        if key:
            by_id_key[idno][key].append(
                f"direct:{clean(row.get('relative_path'))}:{clean(row.get('file_role'))}"
            )

    for row in archive_member_rows:
        idno = clean(row.get("idno"))
        member_name = clean(row.get("member_name"))
        if not idno or not member_name:
            continue
        member_counts[idno] += 1
        key = file_key(member_name)
        if key:
            by_id_key[idno][key].append(
                f"archive:{clean(row.get('archive_relative_path'))}!{member_name}:{clean(row.get('member_role'))}"
            )

    return by_id_key, original_counts + member_counts, generated_counts


def build_full_matches(
    expected_rows: list[dict[str, str]],
    actual_by_id_key: dict[str, dict[str, list[str]]],
) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    for expected in expected_rows:
        idno = clean(expected.get("idno"))
        expected_name = clean(expected.get("file_name"))
        key = file_key(expected_name)
        locations = matched_locations(actual_by_id_key, idno, expected_name)
        source_types = [source_type(item) for item in locations]
        rows.append(
            {
                "download_priority_order": clean(expected.get("download_priority_order")),
                "queue_role": clean(expected.get("queue_role")),
                "country": clean(expected.get("country")),
                "wave": clean(expected.get("wave")),
                "idno": idno,
                "file_id": clean(expected.get("file_id")),
                "expected_file_name": expected_name,
                "expected_file_key": key,
                "file_description": clean(expected.get("file_description")),
                "priority_core_target": clean(expected.get("priority_core_target")),
                "official_file_match_status": "matched_expected_official_file" if locations else "missing_expected_official_file",
                "matched_local_locations": compact(locations),
                "matched_source_types": compact(source_types),
            }
        )
    return rows


def build_core_matches(
    core_rows: list[dict[str, str]],
    actual_by_id_key: dict[str, dict[str, list[str]]],
) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    for core in core_rows:
        idno = clean(core.get("idno"))
        expected_name = clean(core.get("file_name"))
        key = file_key(expected_name)
        locations = matched_locations(actual_by_id_key, idno, expected_name)
        rows.append(
            {
                "download_priority_order": clean(core.get("download_priority_order")),
                "queue_role": clean(core.get("queue_role")),
                "country": clean(core.get("country")),
                "wave": clean(core.get("wave")),
                "idno": idno,
                "requirement": clean(core.get("requirement")),
                "file_rank": clean(core.get("file_rank")),
                "file_id": clean(core.get("file_id")),
                "expected_file_name": expected_name,
                "expected_file_key": key,
                "candidate_variable_rows": clean(core.get("candidate_variable_rows")),
                "strong_candidate_variable_rows": clean(core.get("strong_candidate_variable_rows")),
                "top_variable_names": clean(core.get("top_variable_names")),
                "official_core_file_match_status": "matched_expected_core_file" if locations else "missing_expected_core_file",
                "matched_local_locations": compact(locations),
            }
        )
    return rows


def status_for(original_rows: int, member_rows: int, expected_rows: int, matched_rows: int, core_rows: int, core_matched: int) -> tuple[str, str]:
    if original_rows == 0 and member_rows == 0:
        return "blocked_no_original_package", "Place the complete unchanged official raw package and documentation in the target folder."
    if matched_rows == 0 and core_matched == 0:
        return "blocked_no_official_ddi_file_matches", "Check whether the downloaded package belongs to the same World Bank IDNO and rerun archive preflight."
    if core_matched < core_rows:
        return "blocked_core_official_files_missing", "Download the complete package or locate missing core files before raw-value verification."
    if matched_rows < expected_rows:
        return "core_files_present_full_official_package_incomplete", "Core files are present, but the full official file receipt is incomplete; review before promotion."
    return "official_file_receipt_complete_pending_schema_value_review", "Proceed to schema inspection and raw value/unit/key review; data write remains blocked until all promotion gates pass."


def build_dataset_rows(
    queue_rows: list[dict[str, str]],
    full_rows: list[dict[str, str]],
    core_rows: list[dict[str, str]],
    actual_counts: Counter[str],
    generated_counts: Counter[str],
    archive_member_rows: list[dict[str, str]],
) -> list[dict[str, str]]:
    full_by_id: dict[str, list[dict[str, str]]] = defaultdict(list)
    core_by_id: dict[str, list[dict[str, str]]] = defaultdict(list)
    archive_member_counts: Counter[str] = Counter()
    for row in full_rows:
        full_by_id[clean(row.get("idno"))].append(row)
    for row in core_rows:
        core_by_id[clean(row.get("idno"))].append(row)
    for row in archive_member_rows:
        if clean(row.get("member_name")):
            archive_member_counts[clean(row.get("idno"))] += 1

    rows: list[dict[str, str]] = []
    for queue in queue_rows:
        idno = clean(queue.get("idno"))
        full = full_by_id.get(idno, [])
        core = core_by_id.get(idno, [])
        expected = len(full)
        matched = sum(1 for row in full if row.get("official_file_match_status") == "matched_expected_official_file")
        core_expected = len(core)
        core_matched = sum(1 for row in core if row.get("official_core_file_match_status") == "matched_expected_core_file")
        local_original = actual_counts.get(idno, 0)
        local_members = archive_member_counts.get(idno, 0)
        status, action = status_for(local_original, local_members, expected, matched, core_expected, core_matched)
        rows.append(
            {
                "download_priority_order": clean(queue.get("download_priority_order")),
                "queue_role": clean(queue.get("queue_role")),
                "country": clean(queue.get("country")),
                "wave": clean(queue.get("wave")),
                "idno": idno,
                "survey_name": clean(queue.get("survey_name")),
                "local_target_folder": clean(queue.get("local_target_folder")),
                "official_expected_file_rows": str(expected),
                "official_expected_matched_rows": str(matched),
                "official_expected_missing_rows": str(max(expected - matched, 0)),
                "official_expected_match_rate": pct(matched, expected),
                "official_core_file_rows": str(core_expected),
                "official_core_matched_rows": str(core_matched),
                "official_core_missing_rows": str(max(core_expected - core_matched, 0)),
                "official_core_match_rate": pct(core_matched, core_expected),
                "local_original_file_rows": str(local_original),
                "local_archive_member_rows": str(local_members),
                "local_generated_handoff_rows": str(generated_counts.get(idno, 0)),
                "official_file_receipt_status": status,
                "next_action": action,
                "post_receipt_commands": POST_RECEIPT_COMMANDS,
                "handoff_readme": "",
            }
        )
    return rows


def write_handoff(dataset_row: dict[str, str], core_rows: list[dict[str, str]], full_rows: list[dict[str, str]]) -> str:
    idno = clean(dataset_row.get("idno"))
    folder = raw_folder_path(dataset_row.get("local_target_folder", ""), idno)
    folder.mkdir(parents=True, exist_ok=True)
    path = folder / "_PRIORITY_LSMS_ISA_OFFICIAL_FILE_RECEIPT_VALIDATOR.md"
    missing_core = [row for row in core_rows if row.get("official_core_file_match_status") != "matched_expected_core_file"]
    missing_full = [row for row in full_rows if row.get("official_file_match_status") != "matched_expected_official_file"]
    path.write_text(
        f"""# Priority LSMS-ISA Official File Receipt Validator

IDNO: `{idno}`

Country-wave: {dataset_row.get('country', '')} {dataset_row.get('wave', '')}

Target folder: `{dataset_row.get('local_target_folder', '')}`

Status: `{dataset_row.get('official_file_receipt_status', '')}`

## Counts

| Metric | Value |
|---|---:|
| Official expected file rows | {dataset_row.get('official_expected_file_rows', '0')} |
| Official expected matched rows | {dataset_row.get('official_expected_matched_rows', '0')} |
| Official expected missing rows | {dataset_row.get('official_expected_missing_rows', '0')} |
| Official core file rows | {dataset_row.get('official_core_file_rows', '0')} |
| Official core matched rows | {dataset_row.get('official_core_matched_rows', '0')} |
| Official core missing rows | {dataset_row.get('official_core_missing_rows', '0')} |
| Local original file/archive-member rows | {dataset_row.get('local_original_file_rows', '0')} |

## Missing Core Files

{markdown_table(missing_core, ['requirement', 'file_rank', 'expected_file_name', 'top_variable_names', 'official_core_file_match_status'], 40) if missing_core else 'No missing core files were found.'}

## Missing Official Files

{markdown_table(missing_full, ['file_id', 'expected_file_name', 'file_description', 'priority_core_target', 'official_file_match_status'], 60) if missing_full else 'No missing official files were found.'}

## Required Next Action

{dataset_row.get('next_action', '')}

After changing files in this folder, rerun:

`{POST_RECEIPT_COMMANDS}`

This validator only proves expected file-name receipt against official DDI
metadata. It does not prove variable values, labels, units, recall periods,
survey-design fields, merge keys, climate linkage, or analysis-ready status.
""",
        encoding="utf-8",
    )
    return rel(path)


def build_summary(
    dataset_rows: list[dict[str, str]],
    full_rows: list[dict[str, str]],
    core_rows: list[dict[str, str]],
    handoff_count: int,
) -> list[dict[str, str]]:
    status_counts = Counter(row.get("official_file_receipt_status", "") for row in dataset_rows)
    role_counts = Counter(row.get("queue_role", "") for row in dataset_rows)
    full_matched = sum(1 for row in full_rows if row.get("official_file_match_status") == "matched_expected_official_file")
    core_matched = sum(1 for row in core_rows if row.get("official_core_file_match_status") == "matched_expected_core_file")
    full_alias_matched = sum(1 for row in full_rows if "[alias_" in row.get("matched_local_locations", ""))
    core_alias_matched = sum(1 for row in core_rows if "[alias_" in row.get("matched_local_locations", ""))
    rows = [
        {"metric": "priority_lsms_official_file_receipt_dataset_rows", "value": str(len(dataset_rows)), "interpretation": "Refocused LSMS/ISA datasets checked against the official DDI file universe."},
        {"metric": "priority_lsms_official_file_receipt_expected_file_rows", "value": str(len(full_rows)), "interpretation": "Official DDI file rows expected after complete package receipt."},
        {"metric": "priority_lsms_official_file_receipt_expected_file_matched_rows", "value": str(full_matched), "interpretation": "Expected official files matched by direct files or archive members."},
        {"metric": "priority_lsms_official_file_receipt_expected_file_alias_matched_rows", "value": str(full_alias_matched), "interpretation": "Expected files matched through a constrained same-basename DDI format alias, most commonly NSDstat to Stata."},
        {"metric": "priority_lsms_official_file_receipt_expected_file_missing_rows", "value": str(len(full_rows) - full_matched), "interpretation": "Official DDI file rows still not found locally."},
        {"metric": "priority_lsms_official_file_receipt_core_file_rows", "value": str(len(core_rows)), "interpretation": "Core requirement/file rows that must be present before raw-value review."},
        {"metric": "priority_lsms_official_file_receipt_core_file_matched_rows", "value": str(core_matched), "interpretation": "Core expected files matched locally."},
        {"metric": "priority_lsms_official_file_receipt_core_file_alias_matched_rows", "value": str(core_alias_matched), "interpretation": "Core files matched through a constrained same-basename DDI format alias."},
        {"metric": "priority_lsms_official_file_receipt_core_file_missing_rows", "value": str(len(core_rows) - core_matched), "interpretation": "Core expected files still missing locally."},
        {"metric": "priority_lsms_official_file_receipt_core_complete_dataset_rows", "value": str(sum(1 for row in dataset_rows if safe_int(row.get("official_core_missing_rows")) == 0 and safe_int(row.get("official_core_file_rows")) > 0)), "interpretation": "Datasets whose expected core files all match local package evidence."},
        {"metric": "priority_lsms_official_file_receipt_complete_dataset_rows", "value": str(status_counts.get("official_file_receipt_complete_pending_schema_value_review", 0)), "interpretation": "Datasets with all expected official file rows matched, pending schema and value checks."},
        {"metric": "priority_lsms_official_file_receipt_original_or_member_rows", "value": str(sum(safe_int(row.get("local_original_file_rows")) for row in dataset_rows)), "interpretation": "Non-generated direct original files plus archive member rows indexed."},
        {"metric": "priority_lsms_official_file_receipt_generated_handoff_rows", "value": str(sum(safe_int(row.get("local_generated_handoff_rows")) for row in dataset_rows)), "interpretation": "Generated handoff files ignored as raw receipt evidence."},
        {"metric": "priority_lsms_official_file_receipt_handoff_readmes_written", "value": str(handoff_count), "interpretation": "Per-wave official file receipt validator handoffs written."},
        {"metric": "priority_lsms_official_file_receipt_data_write_status", "value": "blocked_no_promoted_rows", "interpretation": "Official file receipt alone never writes promoted data."},
        {"metric": "modeling_gate_status", "value": "blocked", "interpretation": "Models remain blocked until raw value, climate linkage, and promoted-registry thresholds pass."},
    ]
    for role, count in sorted(role_counts.items()):
        rows.append({"metric": f"priority_lsms_official_file_receipt_queue_role_{role}", "value": str(count), "interpretation": "Official file receipt validator row count by refocused queue role."})
    for status, count in sorted(status_counts.items()):
        rows.append({"metric": f"priority_lsms_official_file_receipt_status_{status}", "value": str(count), "interpretation": "Official file receipt dataset status count."})
    return rows


def write_report(
    dataset_rows: list[dict[str, str]],
    full_rows: list[dict[str, str]],
    core_rows: list[dict[str, str]],
    summary_rows: list[dict[str, str]],
) -> None:
    blocked = [row for row in dataset_rows if not row["official_file_receipt_status"].startswith("official_file_receipt_complete")]
    missing_core = [row for row in core_rows if row.get("official_core_file_match_status") != "matched_expected_core_file"]
    summary_table = "\n".join(f"| {row['metric']} | {row['value']} | {row['interpretation']} |" for row in summary_rows)
    REPORT_PATH.write_text(
        f"""# Priority LSMS-ISA Official File Receipt Validator

Status: fail-closed official file receipt validation for the refocused
LSMS/ISA dataset-promotion campaign. This validator compares local direct files
and readable archive members against the official World Bank DDI file names.
It also records constrained same-basename format aliases when a DDI entry such
as `.NSDstat` corresponds to a real package member such as `.dta`. It does not
download, extract, convert, or promote data.

## Summary

| Metric | Value | Interpretation |
|---|---:|---|
{summary_table}

## Dataset Receipt Status

{markdown_table(dataset_rows, ['download_priority_order', 'queue_role', 'country', 'wave', 'idno', 'official_expected_matched_rows', 'official_expected_file_rows', 'official_core_matched_rows', 'official_core_file_rows', 'official_file_receipt_status'], 30)}

## Blocked Targets

{markdown_table(blocked, ['download_priority_order', 'country', 'idno', 'local_target_folder', 'official_file_receipt_status', 'next_action'], 30) if blocked else 'No blocked targets were found.'}

## Missing Core Files

{markdown_table(missing_core, ['download_priority_order', 'idno', 'requirement', 'expected_file_name', 'top_variable_names', 'official_core_file_match_status'], 100) if missing_core else 'No missing core files were found.'}

## Outputs

- `temp/priority_lsms_isa_official_file_receipt_validation.csv`
- `temp/priority_lsms_isa_official_file_receipt_file_match.csv`
- `temp/priority_lsms_isa_official_file_receipt_core_match.csv`
- `result/priority_lsms_isa_official_file_receipt_validator_summary.csv`

## Interpretation

This is a receipt gate, not a value gate. A matched official file name only
means that a local file or archive member has the same basename as the official
DDI file entry. Promotion still requires schema inspection, raw-value checks,
units, missing codes, skip patterns, recall periods, survey-design variables,
merge keys, and accepted climate linkage.

Generated Markdown handoffs are excluded from raw receipt evidence.
""",
        encoding="utf-8",
    )


def main() -> None:
    ensure_dirs()
    queue_rows = read_csv_dicts(QUEUE_PATH)
    expected_rows = read_csv_dicts(FULL_EXPECTED_PATH)
    core_expected_rows = read_csv_dicts(CORE_EXPECTED_PATH)
    local_rows = read_csv_dicts(LOCAL_FILE_MANIFEST_PATH)
    archive_rows = read_csv_dicts(ARCHIVE_MEMBER_PATH)

    actual_by_id_key, actual_counts, generated_counts = local_actual_file_index(local_rows, archive_rows)
    full_matches = build_full_matches(expected_rows, actual_by_id_key)
    core_matches = build_core_matches(core_expected_rows, actual_by_id_key)
    dataset_rows = build_dataset_rows(queue_rows, full_matches, core_matches, actual_counts, generated_counts, archive_rows)

    full_by_id: dict[str, list[dict[str, str]]] = defaultdict(list)
    core_by_id: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in full_matches:
        full_by_id[clean(row.get("idno"))].append(row)
    for row in core_matches:
        core_by_id[clean(row.get("idno"))].append(row)

    handoff_count = 0
    for row in dataset_rows:
        row["handoff_readme"] = write_handoff(row, core_by_id.get(clean(row.get("idno")), []), full_by_id.get(clean(row.get("idno")), []))
        handoff_count += 1

    summary_rows = build_summary(dataset_rows, full_matches, core_matches, handoff_count)

    write_csv(DATASET_VALIDATION_PATH, dataset_rows, DATASET_COLUMNS)
    write_csv(FULL_FILE_MATCH_PATH, full_matches, FULL_MATCH_COLUMNS)
    write_csv(CORE_FILE_MATCH_PATH, core_matches, CORE_MATCH_COLUMNS)
    write_csv(SUMMARY_PATH, summary_rows, SUMMARY_COLUMNS)
    write_report(dataset_rows, full_matches, core_matches, summary_rows)
    append_log(
        TEMP_DIR / "audit_log.md",
        "Priority LSMS/ISA official file receipt validator "
        f"datasets={len(dataset_rows)} expected_files={len(full_matches)} core_files={len(core_matches)}.",
    )
    print(
        "Priority LSMS/ISA official file receipt validator "
        f"datasets={len(dataset_rows)} expected_files={len(full_matches)} core_files={len(core_matches)}."
    )


if __name__ == "__main__":
    main()
