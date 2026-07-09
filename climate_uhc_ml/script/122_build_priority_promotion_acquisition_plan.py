from __future__ import annotations

import csv
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

from common import REPORT_DIR, RESULT_DIR, TEMP_DIR, append_log, ensure_dirs, write_csv


QUALITY_PATH = TEMP_DIR / "metadata_quality_download_priority.csv"
TARGETS_PATH = RESULT_DIR / "minimum_viable_acquisition_targets.csv"
REGISTRY_PATH = RESULT_DIR / "promoted_country_wave_registry.csv"
INTAKE_PATH = TEMP_DIR / "raw_download_intake_manifest.csv"
MODULES_PATH = TEMP_DIR / "raw_ingestion_module_checklist.csv"
CONCEPT_PATH = TEMP_DIR / "raw_ingestion_concept_checklist.csv"

WAVE_PLAN_PATH = RESULT_DIR / "priority_promotion_acquisition_wave_plan.csv"
FILE_QUEUE_PATH = RESULT_DIR / "priority_promotion_acquisition_file_queue.csv"
SUMMARY_PATH = RESULT_DIR / "priority_promotion_acquisition_summary.csv"
REPORT_PATH = REPORT_DIR / "priority_promotion_acquisition_plan.md"

PRIORITY_COUNTRIES = ["Ethiopia", "Nigeria", "Malawi", "Tanzania", "Uganda"]
PRIORITY_WAVE_TARGET = 10
BACKUP_COUNTRY_TARGET = 3
TOP_FILES_PER_WAVE = 12

POST_DOWNLOAD_COMMANDS = [
    "python script/17_audit_raw_downloads.py",
    "python script/03_inspect_raw_schemas.py",
    "python script/29_build_raw_variable_verification_protocol.py",
    "python script/33_build_harmonization_recipe_gate.py",
    "python script/121_build_country_wave_promotion_registry.py",
    "python script/122_build_priority_promotion_acquisition_plan.py",
    "python script/36_build_direct_read_audit_bundle.py",
    "python script/14_validate_workspace.py",
]

WAVE_COLUMNS = [
    "acquisition_batch_rank",
    "batch_role",
    "country",
    "wave",
    "idno",
    "survey_name",
    "official_url",
    "local_target_folder",
    "quality_rank",
    "priority_country",
    "country_coverage_role",
    "raw_package_status",
    "raw_tabular_file_count",
    "archive_file_count",
    "documentation_file_count",
    "expected_core_module_rows",
    "top_core_files",
    "missing_required_concepts",
    "required_manual_action",
    "post_download_verification_commands",
    "promotion_stop_rule",
]

FILE_COLUMNS = [
    "acquisition_batch_rank",
    "batch_role",
    "country",
    "wave",
    "idno",
    "file_rank",
    "file_name",
    "module_priority_role",
    "candidate_categories",
    "candidate_harmonized_variables",
    "candidate_variable_count",
    "candidate_raw_variables_examples",
    "download_priority_reason",
]

SUMMARY_COLUMNS = ["metric", "value", "interpretation"]


def read_csv_dicts(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        return []
    with path.open(encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def safe_int(value: Any, default: int = 999999) -> int:
    try:
        text = str(value).strip()
        if not text:
            return default
        return int(float(text))
    except (TypeError, ValueError):
        return default


def compact(values: list[str], limit: int = 8) -> str:
    out: list[str] = []
    seen: set[str] = set()
    for value in values:
        clean = " ".join(str(value or "").split())
        if clean and clean not in seen:
            out.append(clean)
            seen.add(clean)
        if len(out) >= limit:
            break
    return "; ".join(out)


def by_id(rows: list[dict[str, str]], field: str = "idno") -> dict[str, list[dict[str, str]]]:
    out: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in rows:
        idno = row.get(field, "").strip()
        if idno:
            out[idno].append(row)
    return out


def one_by_id(rows: list[dict[str, str]], field: str = "idno") -> dict[str, dict[str, str]]:
    out: dict[str, dict[str, str]] = {}
    for row in rows:
        idno = row.get(field, "").strip()
        if idno and idno not in out:
            out[idno] = row
    return out


def best_quality_rows(rows: list[dict[str, str]]) -> list[dict[str, str]]:
    best: dict[str, dict[str, str]] = {}
    for row in rows:
        idno = row.get("idno", "").strip()
        if not idno:
            continue
        current = best.get(idno)
        if current is None or safe_int(row.get("quality_rank")) < safe_int(current.get("quality_rank")):
            best[idno] = dict(row)
    return sorted(best.values(), key=lambda r: (safe_int(r.get("quality_rank")), r.get("country", ""), r.get("idno", "")))


def select_priority_waves(rows: list[dict[str, str]]) -> list[dict[str, str]]:
    priority_rows = [r for r in rows if r.get("country") in PRIORITY_COUNTRIES]
    selected: dict[str, dict[str, str]] = {}

    for country in PRIORITY_COUNTRIES:
        country_rows = [r for r in priority_rows if r.get("country") == country]
        if country_rows:
            best = min(country_rows, key=lambda r: safe_int(r.get("quality_rank")))
            selected[best["idno"]] = best

    for row in priority_rows:
        if len(selected) >= PRIORITY_WAVE_TARGET:
            break
        selected.setdefault(row["idno"], row)

    return sorted(selected.values(), key=lambda r: (safe_int(r.get("quality_rank")), r.get("country", ""), r.get("idno", "")))


def select_backup_countries(target_rows: list[dict[str, str]], selected_ids: set[str]) -> list[dict[str, str]]:
    unique = best_quality_rows(target_rows)
    out: list[dict[str, str]] = []
    seen_countries: set[str] = set()
    for row in unique:
        country = row.get("country", "")
        if not country or country in PRIORITY_COUNTRIES or country == "Albania":
            continue
        if row.get("idno") in selected_ids or country in seen_countries:
            continue
        out.append(row)
        seen_countries.add(country)
        if len(out) >= BACKUP_COUNTRY_TARGET:
            break
    return out


def sorted_modules(rows: list[dict[str, str]]) -> list[dict[str, str]]:
    return sorted(
        rows,
        key=lambda r: (
            0 if r.get("module_priority_role") == "core_main_sample_module_candidate" else 1,
            -safe_int(r.get("candidate_variable_count"), 0),
            r.get("file_name", ""),
        ),
    )


def missing_concepts(rows: list[dict[str, str]]) -> str:
    missing = [
        row.get("concept", "")
        for row in rows
        if row.get("raw_verification_status") not in {"raw_value_verified", "verified"}
    ]
    return compact(missing, limit=20)


def manual_action(raw_status: str) -> str:
    if raw_status in {"raw_tabular_files_present_needs_schema_and_value_verification", "archive_present_needs_extraction_schema_and_value_verification"}:
        return "Extract if needed, inspect raw schemas, then verify values, labels, units, recall periods, missing codes, merge keys, timing, geography, and survey design."
    return "Complete the official account/terms workflow, download the complete original raw package plus documentation, and place the unchanged files in local_target_folder."


def wave_row(
    source: dict[str, str],
    rank: int,
    role: str,
    registry: dict[str, str],
    intake: dict[str, str],
    modules: list[dict[str, str]],
    concepts: list[dict[str, str]],
) -> dict[str, str]:
    core_modules = [m for m in sorted_modules(modules) if m.get("module_priority_role") == "core_main_sample_module_candidate"]
    if not core_modules:
        core_modules = sorted_modules(modules)
    raw_status = registry.get("raw_package_status") or intake.get("intake_status") or "raw_package_status_unknown"
    country = source.get("country", "")
    return {
        "acquisition_batch_rank": str(rank),
        "batch_role": role,
        "country": country,
        "wave": source.get("wave", ""),
        "idno": source.get("idno", ""),
        "survey_name": source.get("survey_name", ""),
        "official_url": source.get("official_url", ""),
        "local_target_folder": source.get("local_target_folder") or registry.get("local_target_folder") or intake.get("local_target_folder"),
        "quality_rank": source.get("quality_rank", ""),
        "priority_country": "1" if country in PRIORITY_COUNTRIES else "0",
        "country_coverage_role": "priority_country" if country in PRIORITY_COUNTRIES else "sixth_country_backup_candidate",
        "raw_package_status": raw_status,
        "raw_tabular_file_count": intake.get("raw_tabular_file_count", "0"),
        "archive_file_count": intake.get("archive_file_count", "0"),
        "documentation_file_count": intake.get("documentation_file_count", "0"),
        "expected_core_module_rows": str(len(core_modules)),
        "top_core_files": compact([m.get("file_name", "") for m in core_modules], limit=10),
        "missing_required_concepts": missing_concepts(concepts),
        "required_manual_action": manual_action(raw_status),
        "post_download_verification_commands": "; ".join(POST_DOWNLOAD_COMMANDS),
        "promotion_stop_rule": "Do not write this wave into data/ until raw package, merge keys, weights/design, consumption/OOP, access, timing/geography, value semantics, and CHIRPS/ERA5 linkage gates pass.",
    }


def file_rows_for_wave(wave: dict[str, str], modules: list[dict[str, str]], max_files: int = TOP_FILES_PER_WAVE) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    ordered = sorted_modules(modules)[:max_files]
    for idx, module in enumerate(ordered, start=1):
        categories = module.get("candidate_categories", "")
        reason_bits = []
        if "consumption" in categories:
            reason_bits.append("financial denominator")
        if "health_expenditure" in categories:
            reason_bits.append("OOP spending")
        if "health_need_access" in categories:
            reason_bits.append("need/access")
        if "geography" in categories:
            reason_bits.append("climate geography")
        if "survey_design" in categories:
            reason_bits.append("weights/design/keys")
        if not reason_bits:
            reason_bits.append("metadata-supported core module")
        rows.append(
            {
                "acquisition_batch_rank": wave["acquisition_batch_rank"],
                "batch_role": wave["batch_role"],
                "country": wave["country"],
                "wave": wave["wave"],
                "idno": wave["idno"],
                "file_rank": str(idx),
                "file_name": module.get("file_name", ""),
                "module_priority_role": module.get("module_priority_role", ""),
                "candidate_categories": categories,
                "candidate_harmonized_variables": module.get("candidate_harmonized_variables", ""),
                "candidate_variable_count": module.get("candidate_variable_count", ""),
                "candidate_raw_variables_examples": module.get("candidate_raw_variables_examples", "")[:500],
                "download_priority_reason": "; ".join(reason_bits),
            }
        )
    return rows


def build_summary(waves: list[dict[str, str]], files: list[dict[str, str]]) -> list[dict[str, str]]:
    role_counts = Counter(row["batch_role"] for row in waves)
    priority_waves = [row for row in waves if row["batch_role"] == "priority_10_wave_batch"]
    priority_countries = sorted({row["country"] for row in priority_waves})
    raw_present = sum(
        1
        for row in waves
        if row["raw_package_status"] in {"raw_tabular_files_present_needs_schema_and_value_verification", "archive_present_needs_extraction_schema_and_value_verification"}
    )
    rows = [
        {"metric": "priority_promotion_wave_plan_rows", "value": str(len(waves)), "interpretation": "Rows in the priority acquisition wave plan."},
        {"metric": "priority_10_wave_batch_rows", "value": str(role_counts.get("priority_10_wave_batch", 0)), "interpretation": "Priority waves selected for immediate raw-package acquisition."},
        {"metric": "priority_10_wave_batch_countries", "value": str(len(priority_countries)), "interpretation": "Priority countries covered by the first 10-wave batch."},
        {"metric": "priority_country_list", "value": ";".join(priority_countries), "interpretation": "Priority countries covered by the first 10-wave batch."},
        {"metric": "sixth_country_backup_rows", "value": str(role_counts.get("sixth_country_backup_candidate", 0)), "interpretation": "Non-Albania backup countries for the 6-country financial-protection threshold."},
        {"metric": "waves_with_raw_package_present", "value": str(raw_present), "interpretation": "Selected or backup waves with raw archive/tabular files currently present."},
        {"metric": "waves_still_requiring_manual_download", "value": str(len(waves) - raw_present), "interpretation": "Selected or backup waves still needing manual raw-package download or placement."},
        {"metric": "priority_file_queue_rows", "value": str(len(files)), "interpretation": "Top core files/modules to verify first after complete raw packages are placed."},
        {"metric": "modeling_gate_status", "value": "blocked", "interpretation": "Models remain blocked until the promoted registry thresholds pass."},
    ]
    return rows


def markdown_table(rows: list[dict[str, str]], columns: list[str], limit: int = 20) -> str:
    lines = ["| " + " | ".join(columns) + " |", "|" + "|".join("---" for _ in columns) + "|"]
    for row in rows[:limit]:
        values = []
        for column in columns:
            value = str(row.get(column, "") or "").replace("|", "/")
            if len(value) > 120:
                value = value[:117] + "..."
            values.append(value)
        lines.append("| " + " | ".join(values) + " |")
    return "\n".join(lines)


def write_report(waves: list[dict[str, str]], files: list[dict[str, str]], summary: list[dict[str, str]]) -> None:
    summary_rows = "\n".join(f"| {r['metric']} | {r['value']} | {r['interpretation']} |" for r in summary)
    priority = [r for r in waves if r["batch_role"] == "priority_10_wave_batch"]
    backups = [r for r in waves if r["batch_role"] == "sixth_country_backup_candidate"]
    file_counts = Counter(row["idno"] for row in files)
    file_count_lines = "\n".join(f"| `{idno}` | {count} |" for idno, count in sorted(file_counts.items()))
    REPORT_PATH.write_text(
        f"""# Priority Promotion Acquisition Plan

Status: priority-first raw acquisition and value-verification plan. This report
does not promote any country-wave into `data/`; it defines the immediate raw
package acquisition batch and the first modules to verify after download.

## Summary

| Metric | Value | Interpretation |
|---|---:|---|
{summary_rows}

## Immediate 10-Wave Priority Batch

{markdown_table(priority, ['acquisition_batch_rank', 'country', 'wave', 'idno', 'raw_package_status', 'expected_core_module_rows', 'local_target_folder'], 12)}

## Sixth-Country Backup Candidates

The main priority set covers five countries. The project still needs six
value-verified financial-protection countries before modeling is allowed, so
these non-Albania backup country candidates should be downloaded if the priority
five-country batch cannot satisfy the six-country gate.

{markdown_table(backups, ['acquisition_batch_rank', 'country', 'wave', 'idno', 'raw_package_status', 'local_target_folder'], 10)}

## File Queue Coverage

| IDNO | Top files/modules queued |
|---|---:|
{file_count_lines}

## Required Procedure

1. Complete official access, account, and terms steps at each `official_url`.
2. Download the complete original raw package and all documentation offered for
   the wave; do not cherry-pick only the files in the queue.
3. Place unchanged raw archives/files under the listed `local_target_folder`.
4. Run the post-download verification commands in
   `result/priority_promotion_acquisition_wave_plan.csv`.
5. Promote no wave into `data/` until raw value, unit, recall-period, missing
   code, merge-key, survey-design, timing/geography, and CHIRPS/ERA5 gates pass.

## Machine-Readable Outputs

- `result/priority_promotion_acquisition_wave_plan.csv`
- `result/priority_promotion_acquisition_file_queue.csv`
- `result/priority_promotion_acquisition_summary.csv`
""",
        encoding="utf-8",
    )


def main() -> None:
    ensure_dirs()
    quality_rows = best_quality_rows(read_csv_dicts(QUALITY_PATH))
    target_rows = read_csv_dicts(TARGETS_PATH)
    registry_by_id = one_by_id(read_csv_dicts(REGISTRY_PATH), "idno")
    intake_by_id = one_by_id(read_csv_dicts(INTAKE_PATH), "dataset_idno")
    modules_by_id = by_id(read_csv_dicts(MODULES_PATH))
    concepts_by_id = by_id(read_csv_dicts(CONCEPT_PATH))

    selected = select_priority_waves(quality_rows)
    selected_ids = {row["idno"] for row in selected}
    backups = select_backup_countries(target_rows, selected_ids)

    waves: list[dict[str, str]] = []
    rank = 1
    for row in selected:
        idno = row["idno"]
        waves.append(
            wave_row(
                row,
                rank,
                "priority_10_wave_batch",
                registry_by_id.get(idno, {}),
                intake_by_id.get(idno, {}),
                modules_by_id.get(idno, []),
                concepts_by_id.get(idno, []),
            )
        )
        rank += 1
    for row in backups:
        idno = row["idno"]
        waves.append(
            wave_row(
                row,
                rank,
                "sixth_country_backup_candidate",
                registry_by_id.get(idno, {}),
                intake_by_id.get(idno, {}),
                modules_by_id.get(idno, []),
                concepts_by_id.get(idno, []),
            )
        )
        rank += 1

    file_rows: list[dict[str, str]] = []
    for wave in waves:
        file_rows.extend(file_rows_for_wave(wave, modules_by_id.get(wave["idno"], [])))

    summary = build_summary(waves, file_rows)
    write_csv(WAVE_PLAN_PATH, waves, WAVE_COLUMNS)
    write_csv(FILE_QUEUE_PATH, file_rows, FILE_COLUMNS)
    write_csv(SUMMARY_PATH, summary, SUMMARY_COLUMNS)
    write_report(waves, file_rows, summary)
    append_log(TEMP_DIR / "audit_log.md", f"Built priority promotion acquisition plan waves={len(waves)} file_queue={len(file_rows)}.")
    print(f"Priority promotion acquisition plan waves={len(waves)} file_queue={len(file_rows)}.")


if __name__ == "__main__":
    main()
