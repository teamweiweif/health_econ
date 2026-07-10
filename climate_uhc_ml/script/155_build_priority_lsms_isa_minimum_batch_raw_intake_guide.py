from __future__ import annotations

import csv
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

from common import PROJECT_ROOT, REPORT_DIR, RESULT_DIR, TEMP_DIR, append_log, ensure_dirs, write_csv


MINIMUM_BATCH_PATH = TEMP_DIR / "priority_lsms_isa_threshold_minimum_batch.csv"
VALIDATION_PATH = TEMP_DIR / "priority_lsms_isa_official_file_receipt_validation.csv"
FULL_FILE_MATCH_PATH = TEMP_DIR / "priority_lsms_isa_official_file_receipt_file_match.csv"
CORE_FILE_MATCH_PATH = TEMP_DIR / "priority_lsms_isa_official_file_receipt_core_match.csv"
FULL_EXPECTED_PATH = TEMP_DIR / "priority_lsms_isa_credentialed_raw_full_file_manifest.csv"

INTAKE_GUIDE_PATH = TEMP_DIR / "priority_lsms_isa_minimum_batch_raw_intake_guide.csv"
EXPECTED_MANIFEST_PATH = TEMP_DIR / "priority_lsms_isa_minimum_batch_expected_file_manifest.csv"
CORE_MANIFEST_PATH = TEMP_DIR / "priority_lsms_isa_minimum_batch_core_file_manifest.csv"
SUMMARY_PATH = RESULT_DIR / "priority_lsms_isa_minimum_batch_raw_intake_guide_summary.csv"
REPORT_PATH = REPORT_DIR / "priority_lsms_isa_minimum_batch_raw_intake_guide.md"

RAW_ROOT = TEMP_DIR / "raw_downloads"

POST_DOWNLOAD_COMMANDS = (
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

INTAKE_COLUMNS = [
    "threshold_sequence_rank",
    "threshold_download_role",
    "country",
    "wave",
    "idno",
    "survey_name",
    "official_get_microdata_url",
    "register_url",
    "terms_url",
    "local_target_folder",
    "expected_full_file_rows",
    "matched_full_file_rows",
    "missing_full_file_rows",
    "expected_core_file_rows",
    "matched_core_file_rows",
    "missing_core_file_rows",
    "official_file_receipt_status",
    "raw_package_status",
    "raw_value_verification_status",
    "analysis_ready_status",
    "top_core_file_examples",
    "next_manual_action",
    "post_download_validation_commands",
    "promotion_stop_rule",
    "handoff_readme",
]

EXPECTED_COLUMNS = [
    "threshold_sequence_rank",
    "country",
    "wave",
    "idno",
    "catalog_id",
    "file_id",
    "file_name",
    "file_description",
    "case_quantity",
    "variable_quantity",
    "priority_core_target",
    "current_receipt_status",
    "source_saved_path",
    "post_download_review_action",
]

CORE_COLUMNS = [
    "threshold_sequence_rank",
    "country",
    "wave",
    "idno",
    "requirement",
    "file_rank",
    "file_id",
    "expected_file_name",
    "file_description",
    "candidate_variable_rows",
    "strong_candidate_variable_rows",
    "top_variable_names",
    "official_core_file_match_status",
    "matched_local_locations",
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
        text = clean(value)
        return int(float(text)) if text else default
    except (TypeError, ValueError):
        return default


def rel(path: Path) -> str:
    try:
        return str(path.relative_to(PROJECT_ROOT)).replace("\\", "/")
    except ValueError:
        return str(path).replace("\\", "/")


def raw_folder_path(folder: str, idno: str) -> Path:
    folder_clean = clean(folder).replace("\\", "/").strip("/")
    if folder_clean:
        return PROJECT_ROOT / folder_clean
    return RAW_ROOT / idno


def file_id_number(value: str) -> int:
    text = clean(value).upper().lstrip("F")
    return safe_int(text, 999999)


def compact(values: list[str], limit: int = 10) -> str:
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


def one_by_id(rows: list[dict[str, str]], field: str = "idno") -> dict[str, dict[str, str]]:
    out: dict[str, dict[str, str]] = {}
    for row in rows:
        key = clean(row.get(field))
        if key and key not in out:
            out[key] = row
    return out


def rows_by_id(rows: list[dict[str, str]], field: str = "idno") -> dict[str, list[dict[str, str]]]:
    out: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in rows:
        key = clean(row.get(field))
        if key:
            out[key].append(row)
    return out


def matched_count(rows: list[dict[str, str]], status_field: str) -> int:
    return sum(1 for row in rows if clean(row.get(status_field)).startswith("matched_"))


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


def next_action(row: dict[str, str]) -> str:
    if safe_int(row.get("missing_core_file_rows")) > 0:
        return (
            "Download the complete unchanged official World Bank package, place it in the target folder, "
            "then rerun receipt validation before raw-value review."
        )
    if safe_int(row.get("missing_full_file_rows")) > 0:
        return (
            "Core files appear present but the full official package is incomplete; resolve full-package "
            "receipt before promotion."
        )
    return (
        "Run raw schema, value, outcome, timing, geography, and climate-linkage verification; do not promote "
        "from receipt alone."
    )


def stop_rule() -> str:
    return (
        "Do not write this country-wave into data/ or run ML until complete official file receipt, raw-value "
        "verification, outcome construction, survey timing/geography, and accepted CHIRPS or ERA5 climate linkage all pass."
    )


def enrich_full_rows(
    full_rows: list[dict[str, str]],
    rank_by_id: dict[str, str],
    allowed_ids: set[str],
) -> list[dict[str, str]]:
    out: list[dict[str, str]] = []
    for row in full_rows:
        idno = clean(row.get("idno"))
        if idno not in allowed_ids:
            continue
        out.append(
            {
                "threshold_sequence_rank": rank_by_id.get(idno, ""),
                "country": clean(row.get("country")),
                "wave": clean(row.get("wave")),
                "idno": idno,
                "catalog_id": clean(row.get("catalog_id")),
                "file_id": clean(row.get("file_id")),
                "file_name": clean(row.get("file_name")),
                "file_description": clean(row.get("file_description")),
                "case_quantity": clean(row.get("case_quantity")),
                "variable_quantity": clean(row.get("variable_quantity")),
                "priority_core_target": clean(row.get("priority_core_target")),
                "current_receipt_status": clean(row.get("current_receipt_status")),
                "source_saved_path": clean(row.get("source_saved_path")),
                "post_download_review_action": clean(row.get("post_download_review_action")),
            }
        )
    out.sort(key=lambda r: (safe_int(r["threshold_sequence_rank"], 999), file_id_number(r["file_id"]), r["file_name"]))
    return out


def enrich_core_rows(
    core_rows: list[dict[str, str]],
    full_rows: list[dict[str, str]],
    rank_by_id: dict[str, str],
    allowed_ids: set[str],
) -> list[dict[str, str]]:
    description_by_key = {
        (clean(row.get("idno")), clean(row.get("file_id"))): clean(row.get("file_description"))
        for row in full_rows
    }
    out: list[dict[str, str]] = []
    for row in core_rows:
        idno = clean(row.get("idno"))
        if idno not in allowed_ids:
            continue
        file_id = clean(row.get("file_id"))
        out.append(
            {
                "threshold_sequence_rank": rank_by_id.get(idno, ""),
                "country": clean(row.get("country")),
                "wave": clean(row.get("wave")),
                "idno": idno,
                "requirement": clean(row.get("requirement")),
                "file_rank": clean(row.get("file_rank")),
                "file_id": file_id,
                "expected_file_name": clean(row.get("expected_file_name")),
                "file_description": description_by_key.get((idno, file_id), ""),
                "candidate_variable_rows": clean(row.get("candidate_variable_rows")),
                "strong_candidate_variable_rows": clean(row.get("strong_candidate_variable_rows")),
                "top_variable_names": clean(row.get("top_variable_names")),
                "official_core_file_match_status": clean(row.get("official_core_file_match_status")),
                "matched_local_locations": clean(row.get("matched_local_locations")),
            }
        )
    out.sort(
        key=lambda r: (
            safe_int(r["threshold_sequence_rank"], 999),
            r["requirement"],
            safe_int(r["file_rank"], 999),
            file_id_number(r["file_id"]),
        )
    )
    return out


def write_handoff(intake: dict[str, str], core_rows: list[dict[str, str]]) -> str:
    folder = raw_folder_path(intake.get("local_target_folder", ""), intake.get("idno", ""))
    folder.mkdir(parents=True, exist_ok=True)
    path = folder / "_PRIORITY_LSMS_ISA_MINIMUM_BATCH_RAW_INTAKE_GUIDE.md"
    core_table = markdown_table(
        core_rows,
        [
            "requirement",
            "file_rank",
            "file_id",
            "expected_file_name",
            "top_variable_names",
            "official_core_file_match_status",
        ],
        30,
    )
    path.write_text(
        f"""# Minimum Batch Raw Intake Guide

IDNO: `{intake.get('idno', '')}`

Country-wave: {intake.get('country', '')} {intake.get('wave', '')}

Threshold rank: {intake.get('threshold_sequence_rank', '')}

Role: {intake.get('threshold_download_role', '')}

Official World Bank microdata URL: {intake.get('official_get_microdata_url', '')}

Target folder: `{intake.get('local_target_folder', '')}`

## Current Receipt Status

- Expected full official files: {intake.get('expected_full_file_rows', '0')}
- Matched full official files: {intake.get('matched_full_file_rows', '0')}
- Missing full official files: {intake.get('missing_full_file_rows', '0')}
- Expected core files: {intake.get('expected_core_file_rows', '0')}
- Matched core files: {intake.get('matched_core_file_rows', '0')}
- Missing core files: {intake.get('missing_core_file_rows', '0')}
- Official receipt status: `{intake.get('official_file_receipt_status', '')}`

## Core Files To Confirm

{core_table}

## Intake Steps

1. Use the official World Bank link above after login, terms, or Data Access Agreement acceptance.
2. Download the complete official package and documentation. Keep original archive names where possible.
3. Place the unchanged package or extracted original files under the target folder.
4. Rerun the post-download commands below.
5. Review raw-value, outcome, timing, geography, and climate-linkage gates before any promotion.

```bash
{POST_DOWNLOAD_COMMANDS}
```

## Stop Rule

{stop_rule()}
""",
        encoding="utf-8",
    )
    return rel(path)


def build_intake_rows(
    minimum_rows: list[dict[str, str]],
    validation_rows: list[dict[str, str]],
    full_match_rows: list[dict[str, str]],
    core_match_rows: list[dict[str, str]],
    expected_rows: list[dict[str, str]],
) -> list[dict[str, str]]:
    validation_by_id = one_by_id(validation_rows)
    full_by_id = rows_by_id(full_match_rows)
    core_by_id = rows_by_id(core_match_rows)
    expected_by_id = rows_by_id(expected_rows)
    intake_rows: list[dict[str, str]] = []

    for row in minimum_rows:
        idno = clean(row.get("idno"))
        validation = validation_by_id.get(idno, {})
        full_rows = full_by_id.get(idno, [])
        core_rows = core_by_id.get(idno, [])
        expected_full = len(expected_by_id.get(idno, [])) or safe_int(row.get("official_expected_file_rows"))
        expected_core = len(core_rows) or safe_int(row.get("official_core_file_rows"))
        matched_full = matched_count(full_rows, "official_file_match_status")
        matched_core = matched_count(core_rows, "official_core_file_match_status")
        intake = {
            "threshold_sequence_rank": clean(row.get("threshold_sequence_rank")),
            "threshold_download_role": clean(row.get("threshold_download_role")),
            "country": clean(row.get("country")),
            "wave": clean(row.get("wave")),
            "idno": idno,
            "survey_name": clean(row.get("survey_name")),
            "official_get_microdata_url": clean(row.get("official_get_microdata_url")),
            "register_url": clean(row.get("register_url")),
            "terms_url": clean(row.get("terms_url")),
            "local_target_folder": clean(row.get("local_target_folder")),
            "expected_full_file_rows": str(expected_full),
            "matched_full_file_rows": str(matched_full),
            "missing_full_file_rows": str(max(expected_full - matched_full, 0)),
            "expected_core_file_rows": str(expected_core),
            "matched_core_file_rows": str(matched_core),
            "missing_core_file_rows": str(max(expected_core - matched_core, 0)),
            "official_file_receipt_status": clean(validation.get("official_file_receipt_status")) or clean(row.get("official_file_receipt_status")),
            "raw_package_status": clean(row.get("raw_package_status")),
            "raw_value_verification_status": clean(row.get("raw_value_verification_status")),
            "analysis_ready_status": clean(row.get("analysis_ready_status")),
            "top_core_file_examples": compact(
                [
                    f"{clean(core.get('requirement'))}:{clean(core.get('expected_file_name'))}"
                    for core in core_rows
                ],
                12,
            ),
            "next_manual_action": "",
            "post_download_validation_commands": POST_DOWNLOAD_COMMANDS,
            "promotion_stop_rule": stop_rule(),
            "handoff_readme": "",
        }
        intake["next_manual_action"] = next_action(intake)
        intake["handoff_readme"] = write_handoff(intake, core_rows)
        intake_rows.append(intake)

    intake_rows.sort(key=lambda r: safe_int(r.get("threshold_sequence_rank"), 999))
    return intake_rows


def build_summary(intake_rows: list[dict[str, str]], expected_rows: list[dict[str, str]], core_rows: list[dict[str, str]]) -> list[dict[str, str]]:
    receipt_counts = Counter(clean(row.get("official_file_receipt_status")) for row in intake_rows)
    rows = [
        {"metric": "priority_lsms_minimum_batch_country_wave_rows", "value": str(len(intake_rows)), "interpretation": "Minimum batch country-waves requiring complete official raw package intake."},
        {"metric": "priority_lsms_minimum_batch_country_rows", "value": str(len({row['country'] for row in intake_rows})), "interpretation": "Countries represented in the minimum threshold batch."},
        {"metric": "priority_lsms_minimum_batch_expected_full_file_rows", "value": str(sum(safe_int(row.get("expected_full_file_rows")) for row in intake_rows)), "interpretation": "Official DDI file rows expected across the minimum batch."},
        {"metric": "priority_lsms_minimum_batch_matched_full_file_rows", "value": str(sum(safe_int(row.get("matched_full_file_rows")) for row in intake_rows)), "interpretation": "Expected full official files currently matched locally."},
        {"metric": "priority_lsms_minimum_batch_missing_full_file_rows", "value": str(sum(safe_int(row.get("missing_full_file_rows")) for row in intake_rows)), "interpretation": "Expected full official files still missing locally."},
        {"metric": "priority_lsms_minimum_batch_expected_core_file_rows", "value": str(sum(safe_int(row.get("expected_core_file_rows")) for row in intake_rows)), "interpretation": "Core requirement-linked official files expected across the minimum batch."},
        {"metric": "priority_lsms_minimum_batch_matched_core_file_rows", "value": str(sum(safe_int(row.get("matched_core_file_rows")) for row in intake_rows)), "interpretation": "Core requirement-linked official files currently matched locally."},
        {"metric": "priority_lsms_minimum_batch_missing_core_file_rows", "value": str(sum(safe_int(row.get("missing_core_file_rows")) for row in intake_rows)), "interpretation": "Core requirement-linked official files still missing locally."},
        {"metric": "priority_lsms_minimum_batch_expected_manifest_rows", "value": str(len(expected_rows)), "interpretation": "Rows written to the minimum-batch expected full-file manifest."},
        {"metric": "priority_lsms_minimum_batch_core_manifest_rows", "value": str(len(core_rows)), "interpretation": "Rows written to the minimum-batch core-file manifest."},
        {"metric": "priority_lsms_minimum_batch_handoff_readmes_written", "value": str(sum(1 for row in intake_rows if row.get("handoff_readme"))), "interpretation": "Per-wave raw intake guides written under temp/raw_downloads."},
        {"metric": "priority_lsms_minimum_batch_data_write_status", "value": "blocked_no_value_verified_raw_packages", "interpretation": "The minimum-batch intake guide never writes promoted data."},
        {"metric": "modeling_gate_status", "value": "blocked", "interpretation": "Models remain blocked until 6 countries, 10 country-waves, and accepted CHIRPS/ERA5 linkage are value-verified."},
    ]
    for status, count in sorted(receipt_counts.items()):
        rows.append({"metric": f"priority_lsms_minimum_batch_receipt_status_{status or 'blank'}", "value": str(count), "interpretation": "Minimum batch rows by current official file receipt status."})
    return rows


def write_report(intake_rows: list[dict[str, str]], expected_rows: list[dict[str, str]], core_rows: list[dict[str, str]], summary_rows: list[dict[str, str]]) -> None:
    summary_table = "\n".join(f"| {row['metric']} | {row['value']} | {row['interpretation']} |" for row in summary_rows)
    REPORT_PATH.write_text(
        f"""# Priority LSMS-ISA Minimum Batch Raw Intake Guide

Status: actionable intake guide for the 11 country-waves in the minimum
threshold batch. This is a post-download handoff, not a raw-data download and
not an analysis dataset.

It narrows the current acquisition burden to the smallest set that could
reach the pre-modeling thresholds if every row later passes raw receipt,
raw-value, outcome, timing, geography, and climate-linkage gates.

## Summary

| Metric | Value | Interpretation |
|---|---:|---|
{summary_table}

## Minimum Batch Intake Rows

{markdown_table(intake_rows, ['threshold_sequence_rank', 'threshold_download_role', 'country', 'wave', 'idno', 'expected_full_file_rows', 'missing_full_file_rows', 'expected_core_file_rows', 'missing_core_file_rows', 'official_file_receipt_status'], 20)}

## Core File Manifest Preview

{markdown_table(core_rows, ['threshold_sequence_rank', 'country', 'wave', 'idno', 'requirement', 'file_id', 'expected_file_name', 'official_core_file_match_status'], 30)}

## Outputs

- `temp/priority_lsms_isa_minimum_batch_raw_intake_guide.csv`
- `temp/priority_lsms_isa_minimum_batch_expected_file_manifest.csv`
- `temp/priority_lsms_isa_minimum_batch_core_file_manifest.csv`
- `result/priority_lsms_isa_minimum_batch_raw_intake_guide_summary.csv`
- `temp/raw_downloads/<IDNO>/_PRIORITY_LSMS_ISA_MINIMUM_BATCH_RAW_INTAKE_GUIDE.md`

## Stop Rule

This guide is only an acquisition and intake control file. `data/` writes and
all predictive, reduced-form, causal ML, or policy-learning models remain
blocked until the promoted registry passes the 6-country, 10-wave, and accepted
CHIRPS/ERA5 linkage thresholds with value-verified raw files.
""",
        encoding="utf-8",
    )


def main() -> None:
    ensure_dirs()
    minimum_rows = read_csv_dicts(MINIMUM_BATCH_PATH)
    allowed_ids = {clean(row.get("idno")) for row in minimum_rows if clean(row.get("idno"))}
    rank_by_id = {clean(row.get("idno")): clean(row.get("threshold_sequence_rank")) for row in minimum_rows}
    validation_rows = read_csv_dicts(VALIDATION_PATH)
    full_match_rows = read_csv_dicts(FULL_FILE_MATCH_PATH)
    core_match_rows = read_csv_dicts(CORE_FILE_MATCH_PATH)
    full_expected_rows = read_csv_dicts(FULL_EXPECTED_PATH)

    expected_rows = enrich_full_rows(full_expected_rows, rank_by_id, allowed_ids)
    core_rows = enrich_core_rows(core_match_rows, full_expected_rows, rank_by_id, allowed_ids)
    intake_rows = build_intake_rows(minimum_rows, validation_rows, full_match_rows, core_match_rows, expected_rows)
    summary_rows = build_summary(intake_rows, expected_rows, core_rows)

    write_csv(INTAKE_GUIDE_PATH, intake_rows, INTAKE_COLUMNS)
    write_csv(EXPECTED_MANIFEST_PATH, expected_rows, EXPECTED_COLUMNS)
    write_csv(CORE_MANIFEST_PATH, core_rows, CORE_COLUMNS)
    write_csv(SUMMARY_PATH, summary_rows, SUMMARY_COLUMNS)
    write_report(intake_rows, expected_rows, core_rows, summary_rows)
    append_log(
        TEMP_DIR / "audit_log.md",
        "Priority LSMS/ISA minimum-batch raw intake guide "
        f"rows={len(intake_rows)} expected_files={len(expected_rows)} core_files={len(core_rows)}.",
    )
    print(
        "Priority LSMS/ISA minimum-batch raw intake guide "
        f"rows={len(intake_rows)} expected_files={len(expected_rows)} core_files={len(core_rows)}."
    )


if __name__ == "__main__":
    main()
