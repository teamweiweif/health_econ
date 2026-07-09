from __future__ import annotations

import csv
from collections import Counter
from pathlib import Path

from common import DATA_DIR, REPORT_DIR, RESULT_DIR, TEMP_DIR, append_log, ensure_dirs, sha256_file, utc_now_iso, write_csv


def read_csv_dicts(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        return []
    with path.open(encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def count_rows(path: Path) -> int:
    return len(read_csv_dicts(path))


def group_count(rows: list[dict[str, str]], field: str) -> Counter[str]:
    return Counter(row.get(field, "") for row in rows)


def markdown_count_table(counter: Counter[str], key_name: str, max_rows: int = 20) -> str:
    lines = [f"| {key_name} | Count |", "|---|---:|"]
    for key, count in counter.most_common(max_rows):
        lines.append(f"| {key or 'blank'} | {count} |")
    return "\n".join(lines)


def yes_done(condition: bool) -> str:
    return "complete" if condition else "incomplete"


def has_success_status(rows: list[dict[str, str]], phase: str) -> bool:
    return any(row.get("phase") == phase and row.get("status") in {"complete", "partial"} for row in rows)


def status_starts(rows: list[dict[str, str]], prefixes: tuple[str, ...], field: str = "status") -> int:
    return sum(1 for row in rows if row.get(field, "").startswith(prefixes))


def metric_value(rows: list[dict[str, str]], metric: str, default: str = "0") -> str:
    for row in rows:
        if row.get("metric") == metric:
            return row.get("value", default)
    return default


def extract_idno(text: str) -> str:
    if ";" not in text or ")" not in text:
        return ""
    return text.rsplit(";", 1)[-1].split(")", 1)[0].strip()


def write_manual_priority(manual: list[dict[str, str]], designs: list[dict[str, str]]) -> list[dict[str, str]]:
    design_by_idno = {row["design_id"].replace("_financial_access_climate", ""): row for row in designs}
    rows = []
    for item in manual:
        idno = extract_idno(item.get("dataset", ""))
        design = design_by_idno.get(idno, {})
        if item.get("source_name") != "World Bank Microdata Library":
            priority_score = 1
            reason = "secondary source; useful for access/care-seeking but usually not full SDG 3.8.2 financial protection"
        else:
            priority_score = (
                int(design.get("outcome_validity") or 0)
                + int(design.get("exposure_precision") or 0)
                + int(design.get("sample_size") or 0)
                + int(design.get("policy_relevance") or 0)
            )
            reason = design.get("reason", "manual raw access required")
        rows.append(
            {
                "priority_score": priority_score,
                "source_name": item.get("source_name", ""),
                "dataset": item.get("dataset", ""),
                "idno": idno,
                "official_url": item.get("official_url", ""),
                "files_needed": item.get("files_needed", ""),
                "status": item.get("status", ""),
                "priority_reason": reason,
            }
        )
    rows.sort(key=lambda r: (-int(r["priority_score"]), r["source_name"], r["dataset"]))
    for i, row in enumerate(rows, start=1):
        row["priority_rank"] = i
    fieldnames = [
        "priority_rank",
        "priority_score",
        "source_name",
        "dataset",
        "idno",
        "official_url",
        "files_needed",
        "status",
        "priority_reason",
    ]
    write_csv(TEMP_DIR / "manual_download_priority.csv", rows, fieldnames)
    return rows


def merge_rows(existing: list[dict[str, str]], new_rows: list[dict[str, str]], key_fields: list[str]) -> list[dict[str, str]]:
    merged = list(existing)
    seen = {tuple(row.get(field, "") for field in key_fields) for row in merged}
    for row in new_rows:
        key = tuple(row.get(field, "") for field in key_fields)
        if key in seen:
            continue
        merged.append(row)
        seen.add(key)
    return merged


def augment_manual_manifest_from_schema(manual: list[dict[str, str]], studies: list[dict[str, str]]) -> list[dict[str, str]]:
    rows = []
    for study in studies:
        catalog_id = study.get("catalog_id", "")
        idno = study.get("idno", "")
        if not catalog_id or not idno:
            continue
        rows.append(
            {
                "source_name": "World Bank Microdata Library",
                "dataset": f"{study.get('country', '')} - {study.get('survey_name', '')} ({study.get('wave', '')}; {idno})",
                "official_url": f"https://microdata.worldbank.org/catalog/{catalog_id}/get-microdata",
                "files_needed": "raw household/person/module files, questionnaires, codebooks, survey design files, geography/GPS files if available",
                "reason": "Recovered from existing schema inventory; raw microdata still require login, registration, or Data Access Agreement steps.",
                "status": "manual terms/login required for raw microdata; public metadata/schema already saved",
            }
        )
    merged = merge_rows(manual, rows, ["source_name", "dataset", "official_url"])
    if len(merged) != len(manual):
        write_csv(
            TEMP_DIR / "manual_download_manifest.csv",
            merged,
            ["source_name", "dataset", "official_url", "files_needed", "reason", "status"],
        )
    return merged


def local_checksum(relative_path: str) -> str:
    if not relative_path:
        return ""
    path = TEMP_DIR.parent / relative_path
    return sha256_file(path) if path.exists() and path.is_file() else ""


def augment_source_inventory_from_schema(source_inventory: list[dict[str, str]], studies: list[dict[str, str]]) -> list[dict[str, str]]:
    rows = []
    for study in studies:
        catalog_id = study.get("catalog_id", "")
        idno = study.get("idno", "")
        label = f"{study.get('country', '')} - {study.get('survey_name', '')}"
        candidates = [
            (
                "World Bank NADA metadata JSON",
                f"https://microdata.worldbank.org/metadata/export/{catalog_id}/json",
                study.get("metadata_json", ""),
            ),
            (
                "World Bank variable API JSON",
                f"https://microdata.worldbank.org/index.php/api/catalog/{idno}/variables",
                study.get("variables_json", ""),
            ),
            (
                "World Bank data dictionary HTML",
                f"https://microdata.worldbank.org/catalog/{catalog_id}",
                study.get("data_dictionary_html", ""),
            ),
        ]
        for kind, url, rel_path in candidates:
            if not rel_path:
                continue
            rows.append(
                {
                    "source name": f"{label} - {kind}",
                    "official URL": url,
                    "access date": utc_now_iso(),
                    "file/wave": rel_path,
                    "unit": "catalog/schema/documentation",
                    "geography": study.get("geographic_coverage", ""),
                    "row count": "",
                    "column count": study.get("variable_count_api", ""),
                    "checksum": local_checksum(rel_path),
                    "status": "recovered from schema inventory; local snapshot present" if local_checksum(rel_path) else "recovered from schema inventory; local path not found",
                }
            )
    merged = merge_rows(source_inventory, rows, ["source name", "official URL", "file/wave"])
    if len(merged) != len(source_inventory):
        write_csv(
            TEMP_DIR / "source_inventory.csv",
            merged,
            ["source name", "official URL", "access date", "file/wave", "unit", "geography", "row count", "column count", "checksum", "status"],
        )
    return merged


def write_manual_file_checklist(
    priority_rows: list[dict[str, str]],
    schema_files: list[dict[str, str]],
    map_paths: list[Path],
) -> list[dict[str, str]]:
    file_info: dict[tuple[str, str], dict[str, str]] = {}
    for row in schema_files:
        file_info[(row.get("idno", ""), row.get("file_name", ""))] = row

    priority_by_idno = {row.get("idno", ""): row for row in priority_rows if row.get("idno")}
    rows_by_file: dict[tuple[str, str], dict[str, object]] = {}
    for path in map_paths:
        category = path.stem.replace("variable_map_", "")
        for row in read_csv_dicts(path):
            idno = row.get("idno", "")
            file_name = row.get("file", "")
            if not idno or not file_name or idno not in priority_by_idno:
                continue
            key = (idno, file_name)
            item = rows_by_file.setdefault(
                key,
                {
                    "priority_rank": priority_by_idno[idno].get("priority_rank", ""),
                    "priority_score": priority_by_idno[idno].get("priority_score", ""),
                    "idno": idno,
                    "dataset": priority_by_idno[idno].get("dataset", ""),
                    "official_url": priority_by_idno[idno].get("official_url", ""),
                    "file_name": file_name,
                    "module_guess": file_info.get(key, {}).get("module_guess", ""),
                    "unit_guess": file_info.get(key, {}).get("unit_guess", ""),
                    "candidate_categories": set(),
                    "candidate_harmonized_variables": set(),
                    "candidate_raw_variables": [],
                    "candidate_variable_count": 0,
                    "download_status": "pending_manual_download",
                    "post_download_action": "place raw file/archive under temp/raw_downloads, then run make all",
                    "notes": "metadata-derived checklist; verify against raw file names and codebook before harmonization",
                },
            )
            item["candidate_categories"].add(category)  # type: ignore[attr-defined]
            if row.get("harmonized_variable"):
                item["candidate_harmonized_variables"].add(row.get("harmonized_variable", ""))  # type: ignore[attr-defined]
            if row.get("raw_variable") and len(item["candidate_raw_variables"]) < 12:  # type: ignore[arg-type]
                item["candidate_raw_variables"].append(row.get("raw_variable", ""))  # type: ignore[attr-defined]
            item["candidate_variable_count"] = int(item["candidate_variable_count"]) + 1  # type: ignore[arg-type]

    rows: list[dict[str, str]] = []
    for item in rows_by_file.values():
        rows.append(
            {
                "priority_rank": str(item["priority_rank"]),
                "priority_score": str(item["priority_score"]),
                "idno": str(item["idno"]),
                "dataset": str(item["dataset"]),
                "official_url": str(item["official_url"]),
                "file_name": str(item["file_name"]),
                "module_guess": str(item["module_guess"]),
                "unit_guess": str(item["unit_guess"]),
                "candidate_categories": ";".join(sorted(item["candidate_categories"])),  # type: ignore[arg-type]
                "candidate_harmonized_variables": ";".join(sorted(item["candidate_harmonized_variables"])),  # type: ignore[arg-type]
                "candidate_raw_variables_examples": ";".join(item["candidate_raw_variables"]),  # type: ignore[arg-type]
                "candidate_variable_count": str(item["candidate_variable_count"]),
                "download_status": str(item["download_status"]),
                "post_download_action": str(item["post_download_action"]),
                "notes": str(item["notes"]),
            }
        )
    rows.sort(key=lambda row: (int(row["priority_rank"] or 9999), -int(row["candidate_variable_count"] or 0), row["file_name"]))
    if not rows:
        existing = read_csv_dicts(TEMP_DIR / "manual_download_file_checklist.csv")
        if existing:
            return existing
    fieldnames = [
        "priority_rank",
        "priority_score",
        "idno",
        "dataset",
        "official_url",
        "file_name",
        "module_guess",
        "unit_guess",
        "candidate_categories",
        "candidate_harmonized_variables",
        "candidate_raw_variables_examples",
        "candidate_variable_count",
        "download_status",
        "post_download_action",
        "notes",
    ]
    write_csv(TEMP_DIR / "manual_download_file_checklist.csv", rows, fieldnames)
    return rows


def write_manual_access_guide(priority_rows: list[dict[str, str]], checklist_rows: list[dict[str, str]]) -> None:
    top_rows = [row for row in priority_rows if row.get("source_name") == "World Bank Microdata Library"][:15]
    top_table = ["| Rank | IDNO | Dataset | URL |", "|---:|---|---|---|"]
    for row in top_rows:
        top_table.append(f"| {row.get('priority_rank', '')} | `{row.get('idno', '')}` | {row.get('dataset', '')} | {row.get('official_url', '')} |")

    checklist_by_idno: dict[str, list[dict[str, str]]] = {}
    for row in checklist_rows:
        checklist_by_idno.setdefault(row.get("idno", ""), []).append(row)

    module_lines = []
    for row in top_rows[:8]:
        idno = row.get("idno", "")
        modules = checklist_by_idno.get(idno, [])[:8]
        if not modules:
            continue
        module_lines.append(f"### {idno}")
        module_lines.append("")
        module_lines.append("| Candidate file/module | Categories | Example raw variables |")
        module_lines.append("|---|---|---|")
        for module in modules:
            module_lines.append(
                f"| `{module.get('file_name', '')}` | {module.get('candidate_categories', '')} | `{module.get('candidate_raw_variables_examples', '')}` |"
            )
        module_lines.append("")

    (REPORT_DIR / "manual_data_access_guide.md").write_text(
        f"""# Manual Data Access Guide

Status: raw schema/value verification is the binding blocker. The project has public metadata, module-level candidate maps, and some inspected public raw schema files, but no harmonized analytical dataset has been promoted.

## Priority Datasets

{chr(10).join(top_table)}

## File/Module Checklist

The machine-readable checklist is `temp/manual_download_file_checklist.csv` with {len(checklist_rows)} metadata-derived file/module rows. It prioritizes modules that contain candidate consumption, OOP health expenditure, health-need/access, geography, survey-design, demographic, or shock variables.

{chr(10).join(module_lines) if module_lines else 'No module checklist rows were generated from current metadata.'}

## Manual Download Procedure

1. Open the priority dataset URL and complete the required World Bank Microdata Library login, registration, or Data Access Agreement steps.
2. Download all raw household, individual, expenditure, health, geography/GPS, survey design, and documentation files available for the study. Do not cherry-pick only modules that look useful from metadata.
3. Store the raw files or original archives under `temp/raw_downloads/`, preferably in a subfolder named by IDNO such as `temp/raw_downloads/ETH_2021_ESPS-W5_v02_M/`.
4. Run `make all` from the project root.
5. Inspect `temp/raw_schema_inventory/raw_file_inventory.csv`, `temp/raw_schema_inventory/raw_variable_catalog.csv`, `temp/harmonization_recipe_gate.csv`, and `temp/harmonization_value_audit_template.csv`.
6. Build `temp/harmonization_recipe.csv` from verified gate candidates only after raw variable names, labels, values, units, recall periods, missing codes, lineage, and merge keys are verified.

## Guardrails

- Do not put raw files in `data/`.
- Do not treat metadata-only variable hits as verified raw variables.
- Do not construct SDG 3.8.2 until the discretionary-budget denominator can be audited.
- Do not run or interpret causal ML until reduced-form estimates and placebo checks pass.
""",
        encoding="utf-8",
    )


def write_completion_audit(stats: dict[str, int]) -> None:
    rows = [
        {
            "criterion": "Workspace structure exists",
            "status": yes_done((TEMP_DIR.parent / "data").exists() and (TEMP_DIR.parent / "script").exists() and REPORT_DIR.exists()),
            "evidence": "data/script/result/report/temp directories exist",
            "gap": "",
        },
        {
            "criterion": "Source inventory exists",
            "status": yes_done(stats["source_inventory"] > 0),
            "evidence": f"temp/source_inventory.csv rows={stats['source_inventory']}",
            "gap": "",
        },
        {
            "criterion": "Country-wave screening exists",
            "status": yes_done(stats["screening"] > 0),
            "evidence": f"temp/country_wave_screening.csv rows={stats['screening']}",
            "gap": "",
        },
        {
            "criterion": "Raw files or manual download manifest exists",
            "status": yes_done(stats["manual_manifest"] > 0),
            "evidence": f"temp/manual_download_manifest.csv rows={stats['manual_manifest']}; raw_file_inventory rows={stats['raw_files']}",
            "gap": "Manual user/account steps still required for raw World Bank/DHS/MICS microdata.",
        },
        {
            "criterion": "Variable maps exist",
            "status": yes_done(stats["map_rows"] > 0),
            "evidence": f"temp/variable_map_*.csv candidate rows={stats['map_rows']}",
            "gap": "All current mappings are metadata-only and require raw-file verification.",
        },
        {
            "criterion": "At least one harmonized household analytical dataset exists",
            "status": yes_done(stats["harmonized_rows"] > 0 and stats["harmonization_output_ok"] > 0),
            "evidence": f"data/harmonized_household.csv rows={stats['harmonized_rows']}; harmonization audit rows={stats['harmonization_audit_rows']}; lineage rows={stats['harmonized_lineage_rows']}",
            "gap": "" if stats["harmonized_rows"] > 0 and stats["harmonization_output_ok"] > 0 else "Requires raw microdata, verified raw-to-harmonized recipe, and successful merge/key audit.",
        },
        {
            "criterion": "At least one climate-linked analytical dataset exists",
            "status": yes_done(stats["climate_linked_rows"] > 0),
            "evidence": f"data/climate_linked_household.csv rows={stats['climate_linked_rows']}; climate_merge_audit rows={stats['climate_merge_audit_rows']}",
            "gap": "" if stats["climate_linked_rows"] > 0 else "Requires harmonized microdata plus climate exposure merge.",
        },
        {
            "criterion": "Main outcomes are constructed and audited",
            "status": yes_done(stats["household_outcome_rows"] > 0 and stats["outcome_audit_constructed_rows"] > 0),
            "evidence": f"data/household_outcomes.csv rows={stats['household_outcome_rows']}; constructed outcome-audit rows={stats['outcome_audit_constructed_rows']}",
            "gap": "" if stats["household_outcome_rows"] > 0 and stats["outcome_audit_constructed_rows"] > 0 else "Requires harmonized OOP, consumption/income, need/care variables, weights, and recall-period checks.",
        },
        {
            "criterion": "Climate exposures are constructed and audited",
            "status": yes_done(stats["climate_exposure_rows"] > 0 and stats["climate_audit_rows"] > 0),
            "evidence": f"climate exposure rows={stats['climate_exposure_rows']}; climate audit rows={stats['climate_audit_rows']}",
            "gap": "" if stats["climate_exposure_rows"] > 0 and stats["climate_audit_rows"] > 0 else "Requires verified input coordinates/timing and climate extraction diagnostics.",
        },
        {
            "criterion": "Descriptive diagnostics exist",
            "status": yes_done(stats["descriptive_prevalence_rows"] > 0 and stats["descriptive_missingness_rows"] > 0),
            "evidence": f"descriptive audit rows={stats['descriptive_audit_rows']}; prevalence rows={stats['descriptive_prevalence_rows']}; missingness rows={stats['descriptive_missingness_rows']}; sample-flow rows={stats['sample_flow_rows']}",
            "gap": "" if stats["descriptive_prevalence_rows"] > 0 and stats["descriptive_missingness_rows"] > 0 else "Requires climate-linked analytical data with constructed outcomes for weighted prevalence and missingness diagnostics.",
        },
        {
            "criterion": "Predictive ML has been estimated and validated",
            "status": yes_done(stats["predictive_metric_rows"] > 0),
            "evidence": f"predictive audit rows={stats['predictive_audit_rows']}; validated metric rows={stats['predictive_metric_rows']}; feature rows={stats['predictive_feature_rows']}",
            "gap": "" if stats["predictive_metric_rows"] > 0 else "Requires audited outcome dataset and non-random leave-country, leave-wave, or time validation splits.",
        },
        {
            "criterion": "At least one reduced-form climate-shock model has been estimated",
            "status": yes_done(stats["reduced_form_estimate_rows"] > 0),
            "evidence": f"causal-model audit rows={stats['causal_model_audit_rows']}; reduced-form estimate rows={stats['reduced_form_estimate_rows']}; placebo-readiness rows={stats['placebo_readiness_rows']}",
            "gap": "" if stats["reduced_form_estimate_rows"] > 0 else "Requires climate-linked outcome data with exposure variation and placebo-ready design checks.",
        },
        {
            "criterion": "Causal ML/policy learning attempted or explicitly rejected",
            "status": yes_done(stats["causal_ml_policy_audit_rows"] > 0 and (stats["causal_ml_rejection_rows"] > 0 or stats["causal_ml_cate_rows"] > 0 or stats["policy_sim_rows"] > 0)),
            "evidence": f"causal-ML policy audit rows={stats['causal_ml_policy_audit_rows']}; rejection rows={stats['causal_ml_rejection_rows']}; CATE rows={stats['causal_ml_cate_rows']}; policy-simulation rows={stats['policy_sim_rows']}",
            "gap": "This is an explicit gate rejection, not a final empirical policy-learning result." if stats["causal_ml_rejection_rows"] > 0 and stats["policy_sim_rows"] == 0 else "",
        },
        {
            "criterion": "Robustness and placebo checks attempted",
            "status": yes_done(stats["robustness_attempted_rows"] > 0),
            "evidence": f"robustness audit rows={stats['robustness_audit_rows']}; robustness grid rows={stats['robustness_result_rows']}; attempted rows={stats['robustness_attempted_rows']}; placebo-readiness rows={stats['placebo_readiness_rows']}",
            "gap": "" if stats["robustness_attempted_rows"] > 0 else "Requires a primary reduced-form estimate and refit/placebo checks, not just a planned robustness grid.",
        },
        {
            "criterion": "report/final_report.md gives a clear empirical judgment",
            "status": yes_done((REPORT_DIR / "final_report.md").exists()),
            "evidence": "report/final_report.md states no-go for estimation and go for manual raw access/schema inspection",
            "gap": "Final publishable judgment cannot be made until raw data and empirical tests exist.",
        },
        {
            "criterion": "script/run_all.sh or Makefile can reproduce core pipeline except documented manual downloads",
            "status": yes_done((TEMP_DIR.parent / "Makefile").exists() and (TEMP_DIR.parent / "script" / "run_all.sh").exists() and (TEMP_DIR.parent / "script" / "run_all.ps1").exists()),
            "evidence": "Makefile, script/run_all.sh, and script/run_all.ps1 exist",
            "gap": "Core empirical pipeline remains gated after metadata/schema stage.",
        },
    ]
    write_csv(RESULT_DIR / "completion_criteria_audit.csv", rows, ["criterion", "status", "evidence", "gap"])


def main() -> None:
    ensure_dirs()
    screening = read_csv_dicts(TEMP_DIR / "country_wave_screening.csv")
    manual = read_csv_dicts(TEMP_DIR / "manual_download_manifest.csv")
    source_inventory = read_csv_dicts(TEMP_DIR / "source_inventory.csv")
    acquisition_progress = read_csv_dicts(TEMP_DIR / "acquisition_progress.csv")
    external_probe = read_csv_dicts(TEMP_DIR / "external_repository_probe.csv")
    worldbank_public_docs = read_csv_dicts(TEMP_DIR / "worldbank_public_documentation_audit.csv")
    worldbank_access_summary = read_csv_dicts(TEMP_DIR / "worldbank_access_gate_summary.csv")
    manual_access_actions = read_csv_dicts(TEMP_DIR / "manual_access_action_queue.csv")
    raw_download_intake = read_csv_dicts(TEMP_DIR / "raw_download_intake_manifest.csv")
    raw_download_expected = read_csv_dicts(TEMP_DIR / "raw_download_expected_files.csv")
    raw_download_intake_summary = read_csv_dicts(RESULT_DIR / "raw_download_intake_summary.csv")
    public_external_downloads = read_csv_dicts(TEMP_DIR / "public_external_raw_candidate_downloads.csv")
    public_external_summary = read_csv_dicts(RESULT_DIR / "public_external_raw_candidate_download_summary.csv")
    first_batch_checklist = read_csv_dicts(TEMP_DIR / "first_batch_raw_acquisition_checklist.csv")
    first_batch_file_targets = read_csv_dicts(TEMP_DIR / "first_batch_raw_file_targets.csv")
    first_batch_summary = read_csv_dicts(RESULT_DIR / "first_batch_raw_acquisition_summary.csv")
    first_batch_access_probe = read_csv_dicts(TEMP_DIR / "first_batch_official_raw_access_probe.csv")
    first_batch_access_summary = read_csv_dicts(RESULT_DIR / "first_batch_official_raw_access_summary.csv")
    first_batch_handoff = read_csv_dicts(TEMP_DIR / "first_batch_manual_download_handoff.csv")
    first_batch_file_queue = read_csv_dicts(TEMP_DIR / "first_batch_manual_download_file_queue.csv")
    first_batch_handoff_summary = read_csv_dicts(RESULT_DIR / "first_batch_manual_download_handoff_summary.csv")
    first_batch_documentation = read_csv_dicts(TEMP_DIR / "first_batch_public_documentation_audit.csv")
    first_batch_documentation_summary = read_csv_dicts(RESULT_DIR / "first_batch_public_documentation_summary.csv")
    first_batch_file_source_trace = read_csv_dicts(TEMP_DIR / "first_batch_file_source_traceability.csv")
    first_batch_file_source_summary = read_csv_dicts(RESULT_DIR / "first_batch_file_source_traceability_summary.csv")
    first_batch_merge_key_plan = read_csv_dicts(TEMP_DIR / "first_batch_merge_key_lineage_plan.csv")
    first_batch_merge_key_candidates = read_csv_dicts(TEMP_DIR / "first_batch_merge_key_candidate_variables.csv")
    first_batch_merge_key_summary = read_csv_dicts(RESULT_DIR / "first_batch_merge_key_lineage_summary.csv")
    first_batch_value_key_audit = read_csv_dicts(TEMP_DIR / "first_batch_raw_value_key_audit.csv")
    first_batch_raw_key_audit = read_csv_dicts(TEMP_DIR / "first_batch_raw_merge_key_audit.csv")
    first_batch_auto_value_audit = read_csv_dicts(TEMP_DIR / "first_batch_harmonization_value_audit_auto.csv")
    first_batch_value_key_summary = read_csv_dicts(RESULT_DIR / "first_batch_raw_value_key_summary.csv")
    alb2002_core_merge_audit = read_csv_dicts(TEMP_DIR / "alb2002_household_core_merge_audit.csv")
    alb2002_core_lineage = read_csv_dicts(TEMP_DIR / "alb2002_household_core_lineage.csv")
    alb2002_core_summary = read_csv_dicts(RESULT_DIR / "alb2002_household_core_candidate_summary.csv")
    alb2002_weight_design_audit = read_csv_dicts(TEMP_DIR / "alb2002_weight_design_evidence_audit.csv")
    alb2002_weight_design_summary = read_csv_dicts(RESULT_DIR / "alb2002_weight_design_evidence_summary.csv")
    alb2002_sample_design_audit = read_csv_dicts(TEMP_DIR / "alb2002_sample_design_documentation_audit.csv")
    alb2002_sample_design_summary = read_csv_dicts(RESULT_DIR / "alb2002_sample_design_documentation_summary.csv")
    alb2002_outcome_audit = read_csv_dicts(TEMP_DIR / "alb2002_provisional_outcome_feasibility_audit.csv")
    alb2002_outcome_summary = read_csv_dicts(RESULT_DIR / "alb2002_provisional_outcome_feasibility_summary.csv")
    alb2002_semantics_audit = read_csv_dicts(TEMP_DIR / "alb2002_outcome_semantics_raw_value_audit.csv")
    alb2002_semantics_summary = read_csv_dicts(RESULT_DIR / "alb2002_outcome_semantics_raw_value_summary.csv")
    alb2002_health_questionnaire_audit = read_csv_dicts(TEMP_DIR / "alb2002_health_questionnaire_semantics_audit.csv")
    alb2002_health_questionnaire_summary = read_csv_dicts(RESULT_DIR / "alb2002_health_questionnaire_semantics_summary.csv")
    alb2002_oop_policy_audit = read_csv_dicts(TEMP_DIR / "alb2002_oop_aggregation_policy_audit.csv")
    alb2002_oop_policy_summary = read_csv_dicts(RESULT_DIR / "alb2002_oop_aggregation_policy_summary.csv")
    alb2002_skip_missing_audit = read_csv_dicts(TEMP_DIR / "alb2002_skip_missing_semantics_audit.csv")
    alb2002_skip_missing_summary = read_csv_dicts(RESULT_DIR / "alb2002_skip_missing_semantics_summary.csv")
    alb2002_oop_skip_value_audit = read_csv_dicts(TEMP_DIR / "alb2002_oop_skip_value_decision_audit.csv")
    alb2002_oop_skip_value_summary = read_csv_dicts(RESULT_DIR / "alb2002_oop_skip_value_decision_summary.csv")
    alb2002_access_need_audit = read_csv_dicts(TEMP_DIR / "alb2002_access_need_denominator_policy_audit.csv")
    alb2002_access_need_summary = read_csv_dicts(RESULT_DIR / "alb2002_access_need_denominator_policy_summary.csv")
    alb2002_consumption_sdg_audit = read_csv_dicts(TEMP_DIR / "alb2002_consumption_sdg_denominator_policy_audit.csv")
    alb2002_consumption_sdg_summary = read_csv_dicts(RESULT_DIR / "alb2002_consumption_sdg_denominator_policy_summary.csv")
    alb2002_consumption_construction_audit = read_csv_dicts(TEMP_DIR / "alb2002_consumption_construction_source_audit.csv")
    alb2002_consumption_construction_summary = read_csv_dicts(RESULT_DIR / "alb2002_consumption_construction_source_summary.csv")
    alb2002_consumption_aggregate_audit = read_csv_dicts(TEMP_DIR / "alb2002_consumption_aggregate_metadata_crosswalk_audit.csv")
    alb2002_consumption_aggregate_summary = read_csv_dicts(RESULT_DIR / "alb2002_consumption_aggregate_metadata_crosswalk_summary.csv")
    alb2002_period_aligned_che_audit = read_csv_dicts(TEMP_DIR / "alb2002_period_aligned_che_policy_audit.csv")
    alb2002_period_aligned_che_summary = read_csv_dicts(RESULT_DIR / "alb2002_period_aligned_che_policy_summary.csv")
    alb2002_che_candidate_audit = read_csv_dicts(RESULT_DIR / "alb2002_che_candidate_outcome_audit.csv")
    alb2002_che_candidate_lineage = read_csv_dicts(TEMP_DIR / "alb2002_che_candidate_outcome_lineage.csv")
    alb2002_che_candidate_summary = read_csv_dicts(RESULT_DIR / "alb2002_che_candidate_outcome_summary.csv")
    alb2002_access_candidate_audit = read_csv_dicts(RESULT_DIR / "alb2002_access_candidate_outcome_audit.csv")
    alb2002_access_candidate_lineage = read_csv_dicts(TEMP_DIR / "alb2002_access_candidate_outcome_lineage.csv")
    alb2002_access_candidate_summary = read_csv_dicts(RESULT_DIR / "alb2002_access_candidate_outcome_summary.csv")
    alb2002_uhc_composite_audit = read_csv_dicts(RESULT_DIR / "alb2002_uhc_composite_candidate_audit.csv")
    alb2002_uhc_composite_lineage = read_csv_dicts(TEMP_DIR / "alb2002_uhc_composite_candidate_lineage.csv")
    alb2002_uhc_composite_summary = read_csv_dicts(RESULT_DIR / "alb2002_uhc_composite_candidate_summary.csv")
    alb2002_analysis_candidate_audit = read_csv_dicts(RESULT_DIR / "alb2002_analysis_candidate_readiness_audit.csv")
    alb2002_analysis_candidate_lineage = read_csv_dicts(TEMP_DIR / "alb2002_analysis_candidate_lineage.csv")
    alb2002_analysis_candidate_summary = read_csv_dicts(RESULT_DIR / "alb2002_analysis_candidate_readiness_summary.csv")
    alb2002_climate_centroid_audit = read_csv_dicts(RESULT_DIR / "alb2002_climate_centroid_exposure_audit.csv")
    alb2002_climate_centroid_manifest = read_csv_dicts(TEMP_DIR / "alb2002_climate_centroid_nasa_power_api_manifest.csv")
    alb2002_climate_centroid_summary = read_csv_dicts(RESULT_DIR / "alb2002_climate_centroid_exposure_summary.csv")
    alb2002_climate_shock_audit = read_csv_dicts(RESULT_DIR / "alb2002_climate_shock_candidate_audit.csv")
    alb2002_climate_shock_lineage = read_csv_dicts(TEMP_DIR / "alb2002_climate_shock_candidate_lineage.csv")
    alb2002_climate_shock_summary = read_csv_dicts(RESULT_DIR / "alb2002_climate_shock_candidate_summary.csv")
    alb2002_climate_outcome_linked_audit = read_csv_dicts(RESULT_DIR / "alb2002_climate_outcome_linked_candidate_audit.csv")
    alb2002_climate_outcome_linked_lineage = read_csv_dicts(TEMP_DIR / "alb2002_climate_outcome_linked_candidate_lineage.csv")
    alb2002_climate_outcome_linked_summary = read_csv_dicts(RESULT_DIR / "alb2002_climate_outcome_linked_candidate_summary.csv")
    alb2002_linked_candidate_descriptive_audit = read_csv_dicts(RESULT_DIR / "alb2002_linked_candidate_descriptive_audit.csv")
    alb2002_linked_candidate_descriptive_cells = read_csv_dicts(RESULT_DIR / "alb2002_linked_candidate_descriptive_cells.csv")
    alb2002_linked_candidate_descriptive_summary = read_csv_dicts(RESULT_DIR / "alb2002_linked_candidate_descriptive_summary.csv")
    alb2002_minimum_recipe_actions = read_csv_dicts(TEMP_DIR / "alb2002_minimum_recipe_promotion_action_queue.csv")
    alb2002_minimum_recipe_gates = read_csv_dicts(TEMP_DIR / "alb2002_minimum_recipe_promotion_gate_checklist.csv")
    alb2002_minimum_recipe_summary = read_csv_dicts(RESULT_DIR / "alb2002_minimum_recipe_promotion_summary.csv")
    alb2002_crosswalk_template = read_csv_dicts(TEMP_DIR / "alb2002_district_climate_crosswalk_template.csv")
    alb2002_boundary_probe = read_csv_dicts(TEMP_DIR / "alb2002_district_boundary_source_probe.csv")
    alb2002_crosswalk_summary = read_csv_dicts(RESULT_DIR / "alb2002_district_climate_crosswalk_summary.csv")
    alb2002_boundary_name_audit = read_csv_dicts(TEMP_DIR / "alb2002_boundary_name_match_audit.csv")
    alb2002_boundary_geojson_inventory = read_csv_dicts(TEMP_DIR / "alb2002_boundary_geojson_inventory.csv")
    alb2002_boundary_name_summary = read_csv_dicts(RESULT_DIR / "alb2002_boundary_name_match_summary.csv")
    alb2002_boundary_source_audit = read_csv_dicts(TEMP_DIR / "alb2002_boundary_source_alternative_audit.csv")
    alb2002_boundary_source_summary = read_csv_dicts(RESULT_DIR / "alb2002_boundary_source_alternative_summary.csv")
    alb2002_boundary_resource_audit = read_csv_dicts(TEMP_DIR / "alb2002_boundary_source_resource_search_audit.csv")
    alb2002_boundary_resource_summary = read_csv_dicts(RESULT_DIR / "alb2002_boundary_source_resource_search_summary.csv")
    alb2002_boundary_geometry_audit = read_csv_dicts(TEMP_DIR / "alb2002_boundary_geometry_provenance_audit.csv")
    alb2002_boundary_metadata_probe = read_csv_dicts(TEMP_DIR / "alb2002_boundary_metadata_provenance_probe.csv")
    alb2002_boundary_geometry_summary = read_csv_dicts(RESULT_DIR / "alb2002_boundary_geometry_provenance_summary.csv")
    alb2002_boundary_manual_actions = read_csv_dicts(TEMP_DIR / "alb2002_boundary_manual_verification_action_queue.csv")
    alb2002_boundary_manual_gates = read_csv_dicts(TEMP_DIR / "alb2002_boundary_promotion_gate_checklist.csv")
    alb2002_boundary_manual_summary = read_csv_dicts(RESULT_DIR / "alb2002_boundary_manual_verification_packet_summary.csv")
    alb2002_boundary_followup_audit = read_csv_dicts(TEMP_DIR / "alb2002_boundary_manual_source_followup_audit.csv")
    alb2002_boundary_followup_summary = read_csv_dicts(RESULT_DIR / "alb2002_boundary_manual_source_followup_summary.csv")
    alb2002_gadm_audit = read_csv_dicts(TEMP_DIR / "alb2002_gadm_boundary_lead_audit.csv")
    alb2002_gadm_match_audit = read_csv_dicts(TEMP_DIR / "alb2002_gadm_boundary_name_match_audit.csv")
    alb2002_gadm_summary = read_csv_dicts(RESULT_DIR / "alb2002_gadm_boundary_lead_summary.csv")
    alb2002_local_geo_artifact_audit = read_csv_dicts(TEMP_DIR / "alb2002_local_geography_artifact_audit.csv")
    alb2002_local_geo_artifact_summary = read_csv_dicts(RESULT_DIR / "alb2002_local_geography_artifact_summary.csv")
    alb2012_core_audit = read_csv_dicts(TEMP_DIR / "alb2012_raw_core_feasibility_audit.csv")
    alb2012_core_lineage = read_csv_dicts(TEMP_DIR / "alb2012_raw_core_lineage.csv")
    alb2012_summary = read_csv_dicts(RESULT_DIR / "alb2012_raw_core_feasibility_summary.csv")
    alb2012_outcome_audit = read_csv_dicts(TEMP_DIR / "alb2012_provisional_outcome_feasibility_audit.csv")
    alb2012_outcome_summary = read_csv_dicts(RESULT_DIR / "alb2012_provisional_outcome_feasibility_summary.csv")
    alb2012_semantics_audit = read_csv_dicts(TEMP_DIR / "alb2012_outcome_semantics_raw_value_audit.csv")
    alb2012_semantics_summary = read_csv_dicts(RESULT_DIR / "alb2012_outcome_semantics_raw_value_summary.csv")
    alb2012_timing_geo_audit = read_csv_dicts(TEMP_DIR / "alb2012_timing_geography_exhaustive_audit.csv")
    alb2012_timing_geo_summary = read_csv_dicts(RESULT_DIR / "alb2012_timing_geography_exhaustive_summary.csv")
    alb2012_questionnaire_timing_audit = read_csv_dicts(TEMP_DIR / "alb2012_questionnaire_timing_field_audit.csv")
    alb2012_questionnaire_timing_raw_gap = read_csv_dicts(TEMP_DIR / "alb2012_questionnaire_timing_raw_gap_audit.csv")
    alb2012_questionnaire_timing_summary = read_csv_dicts(RESULT_DIR / "alb2012_questionnaire_timing_field_summary.csv")
    alb2012_blocker_matrix = read_csv_dicts(TEMP_DIR / "alb2012_timing_geography_blocker_resolution_matrix.csv")
    alb2012_blocker_summary = read_csv_dicts(RESULT_DIR / "alb2012_timing_geography_blocker_resolution_summary.csv")
    albania_legacy_questionnaire_audit = read_csv_dicts(TEMP_DIR / "albania_legacy_questionnaire_readability_audit.csv")
    albania_legacy_questionnaire_summary = read_csv_dicts(RESULT_DIR / "albania_legacy_questionnaire_readability_summary.csv")
    albania_legacy_questionnaire_timing_audit = read_csv_dicts(TEMP_DIR / "albania_legacy_questionnaire_timing_field_audit.csv")
    albania_legacy_questionnaire_timing_raw_gap = read_csv_dicts(TEMP_DIR / "albania_legacy_questionnaire_timing_raw_gap_audit.csv")
    albania_legacy_questionnaire_timing_summary = read_csv_dicts(RESULT_DIR / "albania_legacy_questionnaire_timing_field_summary.csv")
    alb2005_documented_evidence = read_csv_dicts(TEMP_DIR / "alb2005_documented_variable_evidence.csv")
    alb2005_documented_summary = read_csv_dicts(RESULT_DIR / "alb2005_documented_harmonization_summary.csv")
    alb2005_core_merge_audit = read_csv_dicts(TEMP_DIR / "alb2005_household_core_merge_audit.csv")
    alb2005_core_lineage = read_csv_dicts(TEMP_DIR / "alb2005_household_core_lineage.csv")
    alb2005_core_summary = read_csv_dicts(RESULT_DIR / "alb2005_household_core_candidate_summary.csv")
    alb2005_outcome_audit = read_csv_dicts(TEMP_DIR / "alb2005_provisional_outcome_feasibility_audit.csv")
    alb2005_outcome_summary = read_csv_dicts(RESULT_DIR / "alb2005_provisional_outcome_feasibility_summary.csv")
    alb2005_semantics_audit = read_csv_dicts(TEMP_DIR / "alb2005_outcome_semantics_raw_value_audit.csv")
    alb2005_semantics_summary = read_csv_dicts(RESULT_DIR / "alb2005_outcome_semantics_raw_value_summary.csv")
    alb2005_timing_geo_audit = read_csv_dicts(TEMP_DIR / "alb2005_timing_geography_exhaustive_audit.csv")
    alb2005_timing_geo_summary = read_csv_dicts(RESULT_DIR / "alb2005_timing_geography_exhaustive_summary.csv")
    alb2005_timing_geo_source_audit = read_csv_dicts(TEMP_DIR / "alb2005_timing_geography_source_search_audit.csv")
    alb2005_timing_geo_source_summary = read_csv_dicts(RESULT_DIR / "alb2005_timing_geography_source_search_summary.csv")
    alb2005_value_decision_audit = read_csv_dicts(TEMP_DIR / "alb2005_harmonization_value_decision_audit.csv")
    alb2005_value_decision_summary = read_csv_dicts(RESULT_DIR / "alb2005_harmonization_value_decision_summary.csv")
    alb2005_required_value_key_audit = read_csv_dicts(TEMP_DIR / "alb2005_required_value_key_audit.csv")
    alb2005_required_value_key_summary = read_csv_dicts(RESULT_DIR / "alb2005_required_value_key_summary.csv")
    alb2005_health_questionnaire_audit = read_csv_dicts(TEMP_DIR / "alb2005_health_questionnaire_semantics_audit.csv")
    alb2005_health_questionnaire_summary = read_csv_dicts(RESULT_DIR / "alb2005_health_questionnaire_semantics_summary.csv")
    alb2005_oop_policy_audit = read_csv_dicts(TEMP_DIR / "alb2005_oop_aggregation_policy_audit.csv")
    alb2005_oop_policy_summary = read_csv_dicts(RESULT_DIR / "alb2005_oop_aggregation_policy_summary.csv")
    alb2005_skip_missing_audit = read_csv_dicts(TEMP_DIR / "alb2005_skip_missing_semantics_audit.csv")
    alb2005_skip_missing_summary = read_csv_dicts(RESULT_DIR / "alb2005_skip_missing_semantics_summary.csv")
    alb2005_unit_period_audit = read_csv_dicts(TEMP_DIR / "alb2005_consumption_oop_unit_period_audit.csv")
    alb2005_unit_period_summary = read_csv_dicts(RESULT_DIR / "alb2005_consumption_oop_unit_period_summary.csv")
    alb2005_aggregate_crosswalk_audit = read_csv_dicts(TEMP_DIR / "alb2005_consumption_aggregate_metadata_crosswalk_audit.csv")
    alb2005_aggregate_crosswalk_summary = read_csv_dicts(RESULT_DIR / "alb2005_consumption_aggregate_metadata_crosswalk_summary.csv")
    alb2005_component_source_audit = read_csv_dicts(TEMP_DIR / "alb2005_consumption_component_source_search_audit.csv")
    alb2005_component_source_summary = read_csv_dicts(RESULT_DIR / "alb2005_consumption_component_source_search_summary.csv")
    alb2005_minimum_recipe_actions = read_csv_dicts(TEMP_DIR / "alb2005_minimum_recipe_promotion_action_queue.csv")
    alb2005_minimum_recipe_gates = read_csv_dicts(TEMP_DIR / "alb2005_minimum_recipe_promotion_gate_checklist.csv")
    alb2005_minimum_recipe_summary = read_csv_dicts(RESULT_DIR / "alb2005_minimum_recipe_promotion_summary.csv")
    alb2005_public_fieldwork_geo_audit = read_csv_dicts(TEMP_DIR / "alb2005_public_fieldwork_geo_metadata_audit.csv")
    alb2005_public_fieldwork_geo_summary = read_csv_dicts(RESULT_DIR / "alb2005_public_fieldwork_geo_metadata_summary.csv")
    alb2005_diary_timing_audit = read_csv_dicts(TEMP_DIR / "alb2005_diary_timing_candidate_audit.csv")
    alb2005_diary_timing_summary = read_csv_dicts(RESULT_DIR / "alb2005_diary_timing_candidate_summary.csv")
    alb2005_extracted_module_audit = read_csv_dicts(TEMP_DIR / "alb2005_extracted_module_coverage_audit.csv")
    alb2005_extracted_extra_audit = read_csv_dicts(TEMP_DIR / "alb2005_extracted_extra_files_audit.csv")
    alb2005_archive_member_manifest = read_csv_dicts(TEMP_DIR / "alb2005_archive_member_manifest.csv")
    alb2005_extracted_module_summary = read_csv_dicts(RESULT_DIR / "alb2005_extracted_module_coverage_summary.csv")
    alb2005_fallback_blocker_matrix = read_csv_dicts(TEMP_DIR / "alb2005_fallback_blocker_resolution_matrix.csv")
    alb2005_fallback_blocker_summary = read_csv_dicts(RESULT_DIR / "alb2005_fallback_blocker_resolution_summary.csv")
    albania_first_analysis_gate = read_csv_dicts(TEMP_DIR / "albania_first_analysis_promotion_gate_checklist.csv")
    albania_first_analysis_actions = read_csv_dicts(TEMP_DIR / "albania_first_analysis_promotion_action_queue.csv")
    albania_first_analysis_waves = read_csv_dicts(RESULT_DIR / "albania_first_analysis_promotion_wave_ranking.csv")
    albania_first_analysis_summary = read_csv_dicts(RESULT_DIR / "albania_first_analysis_promotion_summary.csv")
    albania_wave_audit = read_csv_dicts(TEMP_DIR / "albania_existing_raw_wave_audit.csv")
    albania_wave_summary = read_csv_dicts(RESULT_DIR / "albania_existing_raw_wave_audit_summary.csv")
    alb2008_core_merge_audit = read_csv_dicts(TEMP_DIR / "alb2008_household_core_merge_audit.csv")
    alb2008_core_lineage = read_csv_dicts(TEMP_DIR / "alb2008_household_core_lineage.csv")
    alb2008_core_summary = read_csv_dicts(RESULT_DIR / "alb2008_household_core_candidate_summary.csv")
    alb2008_outcome_audit = read_csv_dicts(TEMP_DIR / "alb2008_provisional_outcome_feasibility_audit.csv")
    alb2008_outcome_summary = read_csv_dicts(RESULT_DIR / "alb2008_provisional_outcome_feasibility_summary.csv")
    alb2008_semantics_audit = read_csv_dicts(TEMP_DIR / "alb2008_outcome_semantics_raw_value_audit.csv")
    alb2008_semantics_summary = read_csv_dicts(RESULT_DIR / "alb2008_outcome_semantics_raw_value_summary.csv")
    alb2008_timing_geo_audit = read_csv_dicts(TEMP_DIR / "alb2008_timing_geography_exhaustive_audit.csv")
    alb2008_timing_geo_summary = read_csv_dicts(RESULT_DIR / "alb2008_timing_geography_exhaustive_summary.csv")
    alb2008_fallback_blocker_matrix = read_csv_dicts(TEMP_DIR / "alb2008_fallback_blocker_resolution_matrix.csv")
    alb2008_fallback_blocker_summary = read_csv_dicts(RESULT_DIR / "alb2008_fallback_blocker_resolution_summary.csv")
    first_batch_dataset_gate = read_csv_dicts(RESULT_DIR / "first_batch_dataset_verification_gate.csv")
    first_batch_concept_template = read_csv_dicts(TEMP_DIR / "first_batch_concept_verification_template.csv")
    first_batch_variable_template = read_csv_dicts(TEMP_DIR / "first_batch_variable_verification_template.csv")
    first_batch_verification_summary = read_csv_dicts(RESULT_DIR / "first_batch_raw_verification_workbook_summary.csv")
    raw_download_manifest = read_csv_dicts(TEMP_DIR / "raw_download_file_manifest.csv")
    raw_download_targets = read_csv_dicts(TEMP_DIR / "raw_download_target_audit.csv")
    raw_ingestion_plan = read_csv_dicts(TEMP_DIR / "raw_ingestion_plan.csv")
    raw_ingestion_concepts = read_csv_dicts(TEMP_DIR / "raw_ingestion_concept_checklist.csv")
    raw_ingestion_modules = read_csv_dicts(TEMP_DIR / "raw_ingestion_module_checklist.csv")
    raw_ingestion_summary = read_csv_dicts(RESULT_DIR / "raw_ingestion_plan_summary.csv")
    raw_variable_protocol = read_csv_dicts(TEMP_DIR / "raw_variable_verification_protocol.csv")
    harmonization_scaffold = read_csv_dicts(TEMP_DIR / "harmonization_recipe_scaffold.csv")
    raw_variable_summary = read_csv_dicts(RESULT_DIR / "raw_variable_verification_summary.csv")
    harmonization_recipe_gate = read_csv_dicts(TEMP_DIR / "harmonization_recipe_gate.csv")
    harmonization_value_audit_template = read_csv_dicts(TEMP_DIR / "harmonization_value_audit_template.csv")
    harmonization_verified_candidates = read_csv_dicts(TEMP_DIR / "harmonization_recipe_verified_candidates.csv")
    harmonization_readiness = read_csv_dicts(RESULT_DIR / "harmonization_readiness_matrix.csv")
    harmonization_recipe_gate_summary = read_csv_dicts(RESULT_DIR / "harmonization_recipe_gate_summary.csv")
    analysis_dataset_promotion_audit = read_csv_dicts(TEMP_DIR / "analysis_dataset_promotion_barrier_audit.csv")
    analysis_dataset_promotion_summary = read_csv_dicts(RESULT_DIR / "analysis_dataset_promotion_barrier_summary.csv")
    alb2002_harmonized_core_promotion_audit = read_csv_dicts(TEMP_DIR / "alb2002_harmonized_household_core_promotion_audit.csv")
    alb2002_harmonized_core_promotion_summary = read_csv_dicts(RESULT_DIR / "alb2002_harmonized_household_core_promotion_summary.csv")
    alb2002_limited_financial_outcome_promotion_audit = read_csv_dicts(TEMP_DIR / "alb2002_limited_financial_outcome_promotion_audit.csv")
    alb2002_limited_financial_outcome_promotion_summary = read_csv_dicts(RESULT_DIR / "alb2002_limited_financial_outcome_promotion_summary.csv")
    alb2002_limited_climate_exposure_promotion_audit = read_csv_dicts(TEMP_DIR / "alb2002_limited_climate_exposure_promotion_audit.csv")
    alb2002_limited_climate_exposure_promotion_summary = read_csv_dicts(RESULT_DIR / "alb2002_limited_climate_exposure_promotion_summary.csv")
    alb2002_limited_climate_linked_promotion_audit = read_csv_dicts(TEMP_DIR / "alb2002_limited_climate_linked_promotion_audit.csv")
    alb2002_limited_climate_linked_promotion_summary = read_csv_dicts(RESULT_DIR / "alb2002_limited_climate_linked_promotion_summary.csv")
    minimum_viable_targets = read_csv_dicts(RESULT_DIR / "minimum_viable_acquisition_targets.csv")
    minimum_viable_bundles = read_csv_dicts(TEMP_DIR / "minimum_viable_download_bundles.csv")
    minimum_viable_summary = read_csv_dicts(RESULT_DIR / "minimum_viable_acquisition_summary.csv")
    studies = read_csv_dicts(TEMP_DIR / "raw_schema_inventory" / "schema_study_inventory.csv")
    files = read_csv_dicts(TEMP_DIR / "raw_schema_inventory" / "schema_file_inventory.csv")
    manual = augment_manual_manifest_from_schema(manual, studies)
    source_inventory = augment_source_inventory_from_schema(source_inventory, studies)
    variables = read_csv_dicts(TEMP_DIR / "raw_schema_inventory" / "metadata_variable_catalog.csv")
    raw_files = read_csv_dicts(TEMP_DIR / "raw_schema_inventory" / "raw_file_inventory.csv")
    raw_variables = read_csv_dicts(TEMP_DIR / "raw_schema_inventory" / "raw_variable_catalog.csv")
    harmonization_audit = read_csv_dicts(TEMP_DIR / "harmonization_audit.csv")
    harmonized_lineage = read_csv_dicts(TEMP_DIR / "harmonized_lineage.csv")
    harmonized_household = read_csv_dicts(DATA_DIR / "harmonized_household.csv")
    climate_audit = read_csv_dicts(TEMP_DIR / "climate_extraction_audit.csv")
    climate_source_probe = read_csv_dicts(TEMP_DIR / "climate_source_probe.csv")
    climate_exposure_plan = read_csv_dicts(TEMP_DIR / "climate_exposure_plan.csv")
    climate_exposure_spec = read_csv_dicts(RESULT_DIR / "climate_exposure_specification.csv")
    climate_exposure_plan_summary = read_csv_dicts(RESULT_DIR / "climate_exposure_plan_summary.csv")
    climate_linkage_requirements = read_csv_dicts(TEMP_DIR / "climate_linkage_requirements.csv")
    climate_source_method_matrix = read_csv_dicts(RESULT_DIR / "climate_source_method_matrix.csv")
    climate_exposure_validation_protocol = read_csv_dicts(RESULT_DIR / "climate_exposure_validation_protocol.csv")
    climate_linkage_readiness = read_csv_dicts(RESULT_DIR / "climate_linkage_readiness.csv")
    climate_validation_protocol_summary = read_csv_dicts(RESULT_DIR / "climate_validation_protocol_summary.csv")
    climate_exposures = read_csv_dicts(DATA_DIR / "climate_exposures_nasa_power.csv")
    climate_merge_audit = read_csv_dicts(TEMP_DIR / "climate_merge_audit.csv")
    climate_linked = read_csv_dicts(DATA_DIR / "climate_linked_household.csv")
    outcome_audit = read_csv_dicts(RESULT_DIR / "outcome_audit.csv")
    outcome_construct_audit = read_csv_dicts(TEMP_DIR / "outcome_construction_audit.csv")
    household_outcomes = read_csv_dicts(DATA_DIR / "household_outcomes.csv")
    outcome_denominator_plan = read_csv_dicts(TEMP_DIR / "outcome_denominator_plan.csv")
    outcome_specification_plan = read_csv_dicts(RESULT_DIR / "outcome_specification_plan.csv")
    outcome_denominator_plan_summary = read_csv_dicts(RESULT_DIR / "outcome_denominator_plan_summary.csv")
    sdg382_denominator_requirements = read_csv_dicts(TEMP_DIR / "sdg382_denominator_requirements.csv")
    sdg382_denominator_sources = read_csv_dicts(RESULT_DIR / "sdg382_denominator_source_matrix.csv")
    sdg382_denominator_readiness = read_csv_dicts(RESULT_DIR / "sdg382_denominator_country_wave_readiness.csv")
    sdg382_denominator_summary = read_csv_dicts(RESULT_DIR / "sdg382_denominator_summary.csv")
    modeling_identification_plan = read_csv_dicts(TEMP_DIR / "modeling_identification_plan.csv")
    modeling_validation_plan = read_csv_dicts(RESULT_DIR / "modeling_validation_plan.csv")
    falsification_placebo_plan = read_csv_dicts(RESULT_DIR / "falsification_placebo_plan.csv")
    policy_learning_plan = read_csv_dicts(RESULT_DIR / "policy_learning_plan.csv")
    modeling_identification_summary = read_csv_dicts(RESULT_DIR / "modeling_identification_plan_summary.csv")
    mechanism_requirements = read_csv_dicts(TEMP_DIR / "mechanism_variable_requirements.csv")
    mechanism_pathway_protocol = read_csv_dicts(RESULT_DIR / "mechanism_pathway_protocol.csv")
    mechanism_readiness = read_csv_dicts(RESULT_DIR / "mechanism_readiness_matrix.csv")
    mechanism_summary = read_csv_dicts(RESULT_DIR / "mechanism_analysis_protocol_summary.csv")
    empirical_dashboard = read_csv_dicts(RESULT_DIR / "empirical_readiness_dashboard.csv")
    empirical_no_go = read_csv_dicts(RESULT_DIR / "empirical_no_go_threshold_status.csv")
    empirical_dashboard_summary = read_csv_dicts(RESULT_DIR / "empirical_readiness_dashboard_summary.csv")
    direct_read_bundle = read_csv_dicts(RESULT_DIR / "direct_read_audit_bundle.csv")
    direct_read_manifest = read_csv_dicts(RESULT_DIR / "direct_read_artifact_manifest.csv")
    direct_read_summary = read_csv_dicts(RESULT_DIR / "direct_read_audit_bundle_summary.csv")
    objective_traceability = read_csv_dicts(RESULT_DIR / "objective_requirement_traceability.csv")
    objective_guardrails = read_csv_dicts(RESULT_DIR / "objective_guardrail_audit.csv")
    objective_traceability_summary = read_csv_dicts(RESULT_DIR / "objective_traceability_summary.csv")
    python_package_inventory = read_csv_dicts(TEMP_DIR / "python_package_inventory.csv")
    python_environment_audit = read_csv_dicts(RESULT_DIR / "python_environment_audit.csv")
    python_environment_summary = read_csv_dicts(RESULT_DIR / "python_environment_summary.csv")
    validation_reference_probe = read_csv_dicts(TEMP_DIR / "validation_reference_source_probe.csv")
    validation_reference_samples = read_csv_dicts(TEMP_DIR / "validation_reference_indicator_sample.csv")
    hefpi_uhc_series = read_csv_dicts(TEMP_DIR / "hefpi_uhc_series_catalog.csv")
    hefpi_uhc_reference = read_csv_dicts(TEMP_DIR / "hefpi_uhc_reference_sample.csv")
    designs = read_csv_dicts(RESULT_DIR / "design_scorecard.csv")
    design_scorecard_current_audit = read_csv_dicts(RESULT_DIR / "design_scorecard_current_audit.csv")
    design_no_go_threshold_audit = read_csv_dicts(RESULT_DIR / "design_no_go_threshold_audit.csv")
    design_scorecard_current_summary = read_csv_dicts(RESULT_DIR / "design_scorecard_current_summary.csv")
    alb2002_promotion_gate_delta_audit = read_csv_dicts(TEMP_DIR / "alb2002_promotion_gate_delta_audit.csv")
    alb2002_promotion_gate_delta_summary = read_csv_dicts(RESULT_DIR / "alb2002_promotion_gate_delta_summary.csv")
    alb2002_boundary_blocker_matrix = read_csv_dicts(TEMP_DIR / "alb2002_boundary_blocker_resolution_matrix.csv")
    alb2002_boundary_blocker_summary = read_csv_dicts(RESULT_DIR / "alb2002_boundary_blocker_resolution_summary.csv")
    alb2002_outcome_blocker_matrix = read_csv_dicts(TEMP_DIR / "alb2002_outcome_blocker_resolution_matrix.csv")
    alb2002_outcome_blocker_summary = read_csv_dicts(RESULT_DIR / "alb2002_outcome_blocker_resolution_summary.csv")
    descriptive_audit = read_csv_dicts(RESULT_DIR / "descriptive_diagnostics_audit.csv")
    descriptive_prevalence = read_csv_dicts(RESULT_DIR / "descriptive_weighted_prevalence.csv")
    descriptive_missingness = read_csv_dicts(RESULT_DIR / "descriptive_missingness.csv")
    sample_flow = read_csv_dicts(RESULT_DIR / "sample_inclusion_flow.csv")
    sample_gate = read_csv_dicts(RESULT_DIR / "sample_selection_gate_audit.csv")
    sample_gate_summary = read_csv_dicts(RESULT_DIR / "sample_selection_gate_summary.csv")
    variable_confidence = read_csv_dicts(TEMP_DIR / "variable_map_confidence_audit.csv")
    metadata_quality_priority = read_csv_dicts(TEMP_DIR / "metadata_quality_download_priority.csv")
    metadata_quality = read_csv_dicts(RESULT_DIR / "metadata_candidate_quality_audit.csv")
    metadata_quality_summary = read_csv_dicts(RESULT_DIR / "metadata_candidate_quality_summary.csv")
    predictive_audit = read_csv_dicts(RESULT_DIR / "predictive_ml_audit.csv")
    predictive_metrics = read_csv_dicts(RESULT_DIR / "predictive_ml_metrics.csv")
    predictive_features = read_csv_dicts(RESULT_DIR / "predictive_ml_feature_manifest.csv")
    causal_model_audit = read_csv_dicts(RESULT_DIR / "causal_model_audit.csv")
    reduced_form_estimates = read_csv_dicts(RESULT_DIR / "reduced_form_estimates.csv")
    placebo_readiness = read_csv_dicts(RESULT_DIR / "placebo_readiness_audit.csv")
    causal_ml_policy_audit = read_csv_dicts(RESULT_DIR / "causal_ml_policy_audit.csv")
    causal_ml_cate = read_csv_dicts(RESULT_DIR / "causal_ml_cate_summary.csv")
    policy_sim = read_csv_dicts(RESULT_DIR / "policy_targeting_simulation.csv")
    robustness_audit = read_csv_dicts(RESULT_DIR / "robustness_audit.csv")
    robustness_results = read_csv_dicts(RESULT_DIR / "robustness_results.csv")
    priority_rows = write_manual_priority(manual, designs)

    map_paths = [
        TEMP_DIR / "variable_map_consumption.csv",
        TEMP_DIR / "variable_map_health_expenditure.csv",
        TEMP_DIR / "variable_map_health_need_access.csv",
        TEMP_DIR / "variable_map_geography.csv",
        TEMP_DIR / "variable_map_survey_design.csv",
        TEMP_DIR / "variable_map_demographics.csv",
        TEMP_DIR / "variable_map_shocks.csv",
    ]
    map_counts = {path.name: count_rows(path) for path in map_paths}
    total_map_rows = sum(map_counts.values())
    manual_file_checklist = write_manual_file_checklist(priority_rows, files, map_paths)
    write_manual_access_guide(priority_rows, manual_file_checklist)

    stats = {
        "screening": len(screening),
        "manual_manifest": len(manual),
        "manual_file_checklist": len(manual_file_checklist),
        "acquisition_progress": len(acquisition_progress),
        "external_probe": len(external_probe),
        "worldbank_public_docs": len(worldbank_public_docs),
        "worldbank_public_docs_saved": sum(1 for r in worldbank_public_docs if r.get("status") == "saved"),
        "worldbank_access_summary": len(worldbank_access_summary),
        "worldbank_get_microdata_gates": sum(1 for r in worldbank_access_summary if r.get("access_gate_detected") == "1"),
        "raw_download_manifest": len(raw_download_manifest),
        "raw_download_intake_rows": len(raw_download_intake),
        "raw_download_expected_rows": len(raw_download_expected),
        "raw_download_intake_summary_rows": len(raw_download_intake_summary),
        "raw_download_intake_ready_rows": sum(1 for r in raw_download_intake if r.get("intake_status") == "ready_for_raw_schema_inspection"),
        "raw_download_intake_instruction_rows": sum(1 for r in raw_download_intake if r.get("intake_status") == "instructions_or_documentation_only"),
        "raw_download_expected_not_present_rows": sum(1 for r in raw_download_expected if r.get("expected_file_status") == "not_present"),
        "public_external_download_rows": len(public_external_downloads),
        "public_external_downloaded_rows": sum(1 for r in public_external_downloads if r.get("download_status") in {"downloaded", "already_exists"}),
        "public_external_dataset_rows": len({r.get("idno", "") for r in public_external_downloads if r.get("download_status") in {"downloaded", "already_exists"} and r.get("idno", "")}),
        "public_external_summary_rows": len(public_external_summary),
        "first_batch_checklist_rows": len(first_batch_checklist),
        "first_batch_file_target_rows": len(first_batch_file_targets),
        "first_batch_summary_rows": len(first_batch_summary),
        "first_batch_country_count": len({r.get("country", "") for r in first_batch_checklist if r.get("country", "")}),
        "first_batch_raw_tabular_file_rows": sum(int(r.get("raw_tabular_file_count") or 0) for r in first_batch_checklist),
        "first_batch_archive_file_rows": sum(int(r.get("archive_file_count") or 0) for r in first_batch_checklist),
        "first_batch_access_probe_rows": len(first_batch_access_probe),
        "first_batch_access_gate_rows": sum(1 for r in first_batch_access_probe if r.get("access_gate_detected") == "1"),
        "first_batch_possible_direct_raw_rows": sum(1 for r in first_batch_access_probe if r.get("direct_raw_route_status") == "possible_direct_raw_links_unverified"),
        "first_batch_access_summary_rows": len(first_batch_access_summary),
        "first_batch_handoff_rows": len(first_batch_handoff),
        "first_batch_file_queue_rows": len(first_batch_file_queue),
        "first_batch_handoff_summary_rows": len(first_batch_handoff_summary),
        "first_batch_handoff_manual_required_rows": sum(1 for r in first_batch_handoff if r.get("handoff_status") == "manual_account_terms_download_required"),
        "first_batch_documentation_rows": len(first_batch_documentation),
        "first_batch_documentation_summary_rows": len(first_batch_documentation_summary),
        "first_batch_documentation_saved_rows": status_starts(first_batch_documentation, ("saved",), "coverage_status"),
        "first_batch_documentation_failed_rows": status_starts(first_batch_documentation, ("failed",), "coverage_status"),
        "first_batch_file_source_trace_rows": len(first_batch_file_source_trace),
        "first_batch_file_source_summary_rows": len(first_batch_file_source_summary),
        "first_batch_file_source_unsupported_rows": sum(1 for r in first_batch_file_source_trace if r.get("source_trace_status", "").startswith("unsupported_")),
        "first_batch_file_source_supported_rows": sum(1 for r in first_batch_file_source_trace if r.get("source_trace_status") == "metadata_file_and_examples_supported"),
        "first_batch_merge_key_plan_rows": len(first_batch_merge_key_plan),
        "first_batch_merge_key_candidate_rows": len(first_batch_merge_key_candidates),
        "first_batch_merge_key_summary_rows": len(first_batch_merge_key_summary),
        "first_batch_merge_key_planned_rows": sum(1 for r in first_batch_merge_key_plan if r.get("merge_key_lineage_status") == "metadata_key_lineage_planned_raw_unverified"),
        "first_batch_merge_key_raw_ready_rows": sum(1 for r in first_batch_merge_key_plan if r.get("raw_gate_status") != "blocked_raw_microdata"),
        "first_batch_value_key_audit_rows": len(first_batch_value_key_audit),
        "first_batch_value_key_read_ok_rows": sum(1 for r in first_batch_value_key_audit if r.get("read_status") == "read_ok"),
        "first_batch_raw_key_audit_rows": len(first_batch_raw_key_audit),
        "first_batch_raw_key_read_ok_rows": sum(1 for r in first_batch_raw_key_audit if r.get("read_status") == "read_ok"),
        "first_batch_auto_value_audit_rows": len(first_batch_auto_value_audit),
        "first_batch_auto_value_audit_ready_rows": sum(1 for r in first_batch_auto_value_audit if r.get("ready_for_recipe") == "1"),
        "first_batch_value_key_summary_rows": len(first_batch_value_key_summary),
        "design_scorecard_rows": metric_value(design_scorecard_current_summary, "design_scorecard_rows", str(len(designs))),
        "design_scorecard_current_rows": metric_value(design_scorecard_current_summary, "design_scorecard_current_rows"),
        "design_scorecard_audit_rows": metric_value(design_scorecard_current_summary, "design_scorecard_audit_rows"),
        "design_no_go_threshold_rows": metric_value(design_scorecard_current_summary, "design_no_go_threshold_rows"),
        "design_no_go_failed_or_not_estimable_rows": metric_value(design_scorecard_current_summary, "design_no_go_failed_or_not_estimable_rows"),
        "design_scorecard_data_write_ready_rows": metric_value(design_scorecard_current_summary, "design_scorecard_data_write_ready_rows"),
        "design_scorecard_current_decision": metric_value(design_scorecard_current_summary, "design_scorecard_current_decision", "missing"),
        "alb2002_promotion_gate_delta_rows": metric_value(alb2002_promotion_gate_delta_summary, "alb2002_promotion_gate_delta_rows"),
        "alb2002_promotion_gate_delta_review_ready_rows": metric_value(alb2002_promotion_gate_delta_summary, "alb2002_promotion_gate_delta_review_ready_rows"),
        "alb2002_promotion_gate_delta_documented_candidate_rows": metric_value(alb2002_promotion_gate_delta_summary, "alb2002_promotion_gate_delta_documented_candidate_rows"),
        "alb2002_promotion_gate_delta_hard_blocked_rows": metric_value(alb2002_promotion_gate_delta_summary, "alb2002_promotion_gate_delta_hard_blocked_rows"),
        "alb2002_promotion_gate_delta_promotion_ready_rows": metric_value(alb2002_promotion_gate_delta_summary, "alb2002_promotion_gate_delta_promotion_ready_rows"),
        "alb2002_promotion_gate_delta_data_write_ready_rows": metric_value(alb2002_promotion_gate_delta_summary, "alb2002_promotion_gate_delta_data_write_ready_rows"),
        "alb2002_promotion_gate_delta_decision": metric_value(alb2002_promotion_gate_delta_summary, "alb2002_promotion_gate_delta_decision", "missing"),
        "alb2002_boundary_blocker_resolution_rows": metric_value(alb2002_boundary_blocker_summary, "alb2002_boundary_blocker_resolution_rows"),
        "alb2002_boundary_blocker_official_or_primary_lead_rows": metric_value(alb2002_boundary_blocker_summary, "alb2002_boundary_blocker_official_or_primary_lead_rows"),
        "alb2002_boundary_blocker_candidate_name_coverage_rows": metric_value(alb2002_boundary_blocker_summary, "alb2002_boundary_blocker_candidate_name_coverage_rows"),
        "alb2002_boundary_blocker_incompatible_or_negative_rows": metric_value(alb2002_boundary_blocker_summary, "alb2002_boundary_blocker_incompatible_or_negative_rows"),
        "alb2002_boundary_blocker_historical_2002_ready_rows": metric_value(alb2002_boundary_blocker_summary, "alb2002_boundary_blocker_historical_2002_ready_rows"),
        "alb2002_boundary_blocker_climate_linkage_ready_rows": metric_value(alb2002_boundary_blocker_summary, "alb2002_boundary_blocker_climate_linkage_ready_rows"),
        "alb2002_boundary_blocker_data_write_ready_rows": metric_value(alb2002_boundary_blocker_summary, "alb2002_boundary_blocker_data_write_ready_rows"),
        "alb2002_boundary_blocker_hard_blocked_rows": metric_value(alb2002_boundary_blocker_summary, "alb2002_boundary_blocker_hard_blocked_rows"),
        "alb2002_boundary_blocker_required_source_action_rows": metric_value(alb2002_boundary_blocker_summary, "alb2002_boundary_blocker_required_source_action_rows"),
        "alb2002_boundary_blocker_current_decision": metric_value(alb2002_boundary_blocker_summary, "alb2002_boundary_blocker_current_decision", "missing"),
        "alb2002_outcome_blocker_resolution_rows": metric_value(alb2002_outcome_blocker_summary, "alb2002_outcome_blocker_resolution_rows"),
        "alb2002_outcome_blocker_financial_rows": metric_value(alb2002_outcome_blocker_summary, "alb2002_outcome_blocker_financial_rows"),
        "alb2002_outcome_blocker_access_rows": metric_value(alb2002_outcome_blocker_summary, "alb2002_outcome_blocker_access_rows"),
        "alb2002_outcome_blocker_composite_rows": metric_value(alb2002_outcome_blocker_summary, "alb2002_outcome_blocker_composite_rows"),
        "alb2002_outcome_blocker_candidate_not_promoted_rows": metric_value(alb2002_outcome_blocker_summary, "alb2002_outcome_blocker_candidate_not_promoted_rows"),
        "alb2002_outcome_blocker_low_event_candidate_rows": metric_value(alb2002_outcome_blocker_summary, "alb2002_outcome_blocker_low_event_candidate_rows"),
        "alb2002_outcome_blocker_hard_blocked_rows": metric_value(alb2002_outcome_blocker_summary, "alb2002_outcome_blocker_hard_blocked_rows"),
        "alb2002_outcome_blocker_outcome_ready_rows": metric_value(alb2002_outcome_blocker_summary, "alb2002_outcome_blocker_outcome_ready_rows"),
        "alb2002_outcome_blocker_sdg382_ready_rows": metric_value(alb2002_outcome_blocker_summary, "alb2002_outcome_blocker_sdg382_ready_rows"),
        "alb2002_outcome_blocker_climate_linkage_ready_rows": metric_value(alb2002_outcome_blocker_summary, "alb2002_outcome_blocker_climate_linkage_ready_rows"),
        "alb2002_outcome_blocker_data_write_ready_rows": metric_value(alb2002_outcome_blocker_summary, "alb2002_outcome_blocker_data_write_ready_rows"),
        "alb2002_outcome_blocker_current_decision": metric_value(alb2002_outcome_blocker_summary, "alb2002_outcome_blocker_current_decision", "missing"),
        "alb2002_household_core_candidate_rows": metric_value(alb2002_core_summary, "alb2002_household_core_candidate_rows"),
        "alb2002_households_with_total_consumption": metric_value(alb2002_core_summary, "alb2002_households_with_total_consumption"),
        "alb2002_households_with_household_weight": metric_value(alb2002_core_summary, "alb2002_households_with_household_weight"),
        "alb2002_households_with_oop_4w_positive": metric_value(alb2002_core_summary, "alb2002_households_with_oop_4w_positive"),
        "alb2002_households_with_oop_12m_positive": metric_value(alb2002_core_summary, "alb2002_households_with_oop_12m_positive"),
        "alb2002_households_with_district_code": metric_value(alb2002_core_summary, "alb2002_households_with_district_code"),
        "alb2002_households_with_survey_month": metric_value(alb2002_core_summary, "alb2002_households_with_survey_month"),
        "alb2002_households_with_interview_date": metric_value(alb2002_core_summary, "alb2002_households_with_interview_date"),
        "alb2002_household_core_recipe_ready_rows": metric_value(alb2002_core_summary, "alb2002_household_core_recipe_ready_rows"),
        "alb2002_household_core_current_decision": metric_value(alb2002_core_summary, "alb2002_household_core_current_decision", "missing"),
        "alb2002_weight_design_evidence_audit_rows": metric_value(alb2002_weight_design_summary, "alb2002_weight_design_evidence_audit_rows"),
        "alb2002_weight_design_source_page_flag_rows": metric_value(alb2002_weight_design_summary, "alb2002_weight_design_source_page_flag_rows"),
        "alb2002_weight_design_raw_weight_file_rows": metric_value(alb2002_weight_design_summary, "alb2002_weight_design_raw_weight_file_rows"),
        "alb2002_weight_design_positive_weight_rows": metric_value(alb2002_weight_design_summary, "alb2002_weight_design_positive_weight_rows"),
        "alb2002_weight_design_candidate_key_match_rows": metric_value(alb2002_weight_design_summary, "alb2002_weight_design_candidate_key_match_rows"),
        "alb2002_weight_design_distinct_psu_rows": metric_value(alb2002_weight_design_summary, "alb2002_weight_design_distinct_psu_rows"),
        "alb2002_weight_design_distinct_stratum_rows": metric_value(alb2002_weight_design_summary, "alb2002_weight_design_distinct_stratum_rows"),
        "alb2002_weight_design_weighted_inference_ready_rows": metric_value(alb2002_weight_design_summary, "alb2002_weight_design_weighted_inference_ready_rows"),
        "alb2002_weight_design_harmonized_promotion_ready_rows": metric_value(alb2002_weight_design_summary, "alb2002_weight_design_harmonized_promotion_ready_rows"),
        "alb2002_weight_design_current_decision": metric_value(alb2002_weight_design_summary, "alb2002_weight_design_current_decision", "missing"),
        "alb2002_sample_design_documentation_audit_rows": metric_value(alb2002_sample_design_summary, "alb2002_sample_design_documentation_audit_rows"),
        "alb2002_sample_design_pdf_available_rows": metric_value(alb2002_sample_design_summary, "alb2002_sample_design_pdf_available_rows"),
        "alb2002_sample_design_pdf_pages": metric_value(alb2002_sample_design_summary, "alb2002_sample_design_pdf_pages"),
        "alb2002_sample_design_official_450_psu_8_hh_rows": metric_value(alb2002_sample_design_summary, "alb2002_sample_design_official_450_psu_8_hh_rows"),
        "alb2002_sample_design_official_3599_final_rows": metric_value(alb2002_sample_design_summary, "alb2002_sample_design_official_3599_final_rows"),
        "alb2002_sample_design_raw_design_concordance_rows": metric_value(alb2002_sample_design_summary, "alb2002_sample_design_raw_design_concordance_rows"),
        "alb2002_sample_design_documentation_ready_rows": metric_value(alb2002_sample_design_summary, "alb2002_sample_design_documentation_ready_rows"),
        "alb2002_sample_design_weighted_inference_ready_rows": metric_value(alb2002_sample_design_summary, "alb2002_sample_design_weighted_inference_ready_rows"),
        "alb2002_sample_design_harmonized_promotion_ready_rows": metric_value(alb2002_sample_design_summary, "alb2002_sample_design_harmonized_promotion_ready_rows"),
        "alb2002_sample_design_current_decision": metric_value(alb2002_sample_design_summary, "alb2002_sample_design_current_decision", "missing"),
        "alb2002_provisional_outcome_audit_rows": len(alb2002_outcome_audit),
        "alb2002_provisional_financial_stress_test_rows": metric_value(alb2002_outcome_summary, "alb2002_provisional_financial_stress_test_rows"),
        "alb2002_provisional_access_proxy_rows": metric_value(alb2002_outcome_summary, "alb2002_provisional_access_proxy_rows"),
        "alb2002_provisional_low_event_rate_rows": metric_value(alb2002_outcome_summary, "alb2002_provisional_low_event_rate_rows"),
        "alb2002_provisional_outcome_ready_rows": metric_value(alb2002_outcome_summary, "alb2002_provisional_outcome_ready_rows"),
        "alb2002_provisional_outcome_current_decision": metric_value(alb2002_outcome_summary, "alb2002_provisional_outcome_current_decision", "missing"),
        "alb2002_outcome_semantics_raw_value_rows": len(alb2002_semantics_audit),
        "alb2002_outcome_semantics_source_files_scanned": metric_value(alb2002_semantics_summary, "alb2002_outcome_semantics_source_files_scanned"),
        "alb2002_outcome_semantics_financial_oop_candidate_rows": metric_value(alb2002_semantics_summary, "alb2002_outcome_semantics_financial_oop_candidate_rows"),
        "alb2002_outcome_semantics_access_candidate_rows": metric_value(alb2002_semantics_summary, "alb2002_outcome_semantics_access_candidate_rows"),
        "alb2002_outcome_semantics_need_candidate_rows": metric_value(alb2002_semantics_summary, "alb2002_outcome_semantics_need_candidate_rows"),
        "alb2002_outcome_semantics_rows_with_value_labels": metric_value(alb2002_semantics_summary, "alb2002_outcome_semantics_rows_with_value_labels"),
        "alb2002_outcome_semantics_conditional_reason_rows": metric_value(alb2002_semantics_summary, "alb2002_outcome_semantics_conditional_reason_rows"),
        "alb2002_outcome_semantics_outcome_ready_rows": metric_value(alb2002_semantics_summary, "alb2002_outcome_semantics_outcome_ready_rows"),
        "alb2002_outcome_semantics_sdg382_ready_rows": metric_value(alb2002_semantics_summary, "alb2002_outcome_semantics_sdg382_ready_rows"),
        "alb2002_outcome_semantics_current_decision": metric_value(alb2002_semantics_summary, "alb2002_outcome_semantics_current_decision", "missing"),
        "alb2002_health_questionnaire_semantics_rows": metric_value(alb2002_health_questionnaire_summary, "alb2002_health_questionnaire_semantics_rows"),
        "alb2002_health_questionnaire_oop_item_rows": metric_value(alb2002_health_questionnaire_summary, "alb2002_health_questionnaire_oop_item_rows"),
        "alb2002_health_questionnaire_gift_item_rows": metric_value(alb2002_health_questionnaire_summary, "alb2002_health_questionnaire_gift_item_rows"),
        "alb2002_health_questionnaire_new_lek_unit_rows": metric_value(alb2002_health_questionnaire_summary, "alb2002_health_questionnaire_new_lek_unit_rows"),
        "alb2002_health_questionnaire_four_week_oop_rows": metric_value(alb2002_health_questionnaire_summary, "alb2002_health_questionnaire_four_week_oop_rows"),
        "alb2002_health_questionnaire_twelve_month_oop_rows": metric_value(alb2002_health_questionnaire_summary, "alb2002_health_questionnaire_twelve_month_oop_rows"),
        "alb2002_health_questionnaire_exclusion_note_rows": metric_value(alb2002_health_questionnaire_summary, "alb2002_health_questionnaire_exclusion_note_rows"),
        "alb2002_health_questionnaire_zero_instruction_rows": metric_value(alb2002_health_questionnaire_summary, "alb2002_health_questionnaire_zero_instruction_rows"),
        "alb2002_health_questionnaire_access_rows": metric_value(alb2002_health_questionnaire_summary, "alb2002_health_questionnaire_access_rows"),
        "alb2002_health_questionnaire_cost_barrier_rows": metric_value(alb2002_health_questionnaire_summary, "alb2002_health_questionnaire_cost_barrier_rows"),
        "alb2002_health_questionnaire_distance_barrier_rows": metric_value(alb2002_health_questionnaire_summary, "alb2002_health_questionnaire_distance_barrier_rows"),
        "alb2002_health_questionnaire_supply_barrier_rows": metric_value(alb2002_health_questionnaire_summary, "alb2002_health_questionnaire_supply_barrier_rows"),
        "alb2002_health_questionnaire_payment_skip_rows": metric_value(alb2002_health_questionnaire_summary, "alb2002_health_questionnaire_payment_skip_rows"),
        "alb2002_health_questionnaire_payment_nonmissing_when_not_triggered_rows": metric_value(alb2002_health_questionnaire_summary, "alb2002_health_questionnaire_payment_nonmissing_when_not_triggered_rows"),
        "alb2002_health_questionnaire_payment_positive_when_not_triggered_rows": metric_value(alb2002_health_questionnaire_summary, "alb2002_health_questionnaire_payment_positive_when_not_triggered_rows"),
        "alb2002_health_questionnaire_payment_zero_or_missing_when_triggered_rows": metric_value(alb2002_health_questionnaire_summary, "alb2002_health_questionnaire_payment_zero_or_missing_when_triggered_rows"),
        "alb2002_health_questionnaire_conditional_skip_rows": metric_value(alb2002_health_questionnaire_summary, "alb2002_health_questionnaire_conditional_skip_rows"),
        "alb2002_health_questionnaire_conditional_nonmissing_when_not_triggered_rows": metric_value(alb2002_health_questionnaire_summary, "alb2002_health_questionnaire_conditional_nonmissing_when_not_triggered_rows"),
        "alb2002_health_questionnaire_conditional_missing_when_triggered_rows": metric_value(alb2002_health_questionnaire_summary, "alb2002_health_questionnaire_conditional_missing_when_triggered_rows"),
        "alb2002_health_questionnaire_recipe_ready_rows": metric_value(alb2002_health_questionnaire_summary, "alb2002_health_questionnaire_recipe_ready_rows"),
        "alb2002_health_questionnaire_outcome_ready_rows": metric_value(alb2002_health_questionnaire_summary, "alb2002_health_questionnaire_outcome_ready_rows"),
        "alb2002_health_questionnaire_sdg382_ready_rows": metric_value(alb2002_health_questionnaire_summary, "alb2002_health_questionnaire_sdg382_ready_rows"),
        "alb2002_health_questionnaire_climate_linkage_ready_rows": metric_value(alb2002_health_questionnaire_summary, "alb2002_health_questionnaire_climate_linkage_ready_rows"),
        "alb2002_health_questionnaire_current_decision": metric_value(alb2002_health_questionnaire_summary, "alb2002_health_questionnaire_current_decision", "missing"),
        "alb2002_oop_aggregation_policy_rows": metric_value(alb2002_oop_policy_summary, "alb2002_oop_aggregation_policy_rows"),
        "alb2002_oop_aggregation_policy_household_rows": metric_value(alb2002_oop_policy_summary, "alb2002_oop_aggregation_policy_household_rows"),
        "alb2002_oop_aggregation_policy_total_consumption_rows": metric_value(alb2002_oop_policy_summary, "alb2002_oop_aggregation_policy_total_consumption_rows"),
        "alb2002_oop_aggregation_policy_four_week_policy_rows": metric_value(alb2002_oop_policy_summary, "alb2002_oop_aggregation_policy_four_week_policy_rows"),
        "alb2002_oop_aggregation_policy_twelve_month_policy_rows": metric_value(alb2002_oop_policy_summary, "alb2002_oop_aggregation_policy_twelve_month_policy_rows"),
        "alb2002_oop_aggregation_policy_annual_stress_rows": metric_value(alb2002_oop_policy_summary, "alb2002_oop_aggregation_policy_annual_stress_rows"),
        "alb2002_oop_aggregation_policy_max_che10_rate": metric_value(alb2002_oop_policy_summary, "alb2002_oop_aggregation_policy_max_che10_rate"),
        "alb2002_oop_aggregation_policy_max_che25_rate": metric_value(alb2002_oop_policy_summary, "alb2002_oop_aggregation_policy_max_che25_rate"),
        "alb2002_oop_aggregation_policy_core_4w_match_rows": metric_value(alb2002_oop_policy_summary, "alb2002_oop_aggregation_policy_core_4w_match_rows"),
        "alb2002_oop_aggregation_policy_core_12m_match_rows": metric_value(alb2002_oop_policy_summary, "alb2002_oop_aggregation_policy_core_12m_match_rows"),
        "alb2002_oop_aggregation_policy_outcome_ready_rows": metric_value(alb2002_oop_policy_summary, "alb2002_oop_aggregation_policy_outcome_ready_rows"),
        "alb2002_oop_aggregation_policy_recipe_ready_rows": metric_value(alb2002_oop_policy_summary, "alb2002_oop_aggregation_policy_recipe_ready_rows"),
        "alb2002_oop_aggregation_policy_sdg382_ready_rows": metric_value(alb2002_oop_policy_summary, "alb2002_oop_aggregation_policy_sdg382_ready_rows"),
        "alb2002_oop_aggregation_policy_climate_linkage_ready_rows": metric_value(alb2002_oop_policy_summary, "alb2002_oop_aggregation_policy_climate_linkage_ready_rows"),
        "alb2002_oop_aggregation_policy_current_decision": metric_value(alb2002_oop_policy_summary, "alb2002_oop_aggregation_policy_current_decision", "missing"),
        "alb2002_skip_missing_semantics_rows": metric_value(alb2002_skip_missing_summary, "alb2002_skip_missing_semantics_rows"),
        "alb2002_skip_missing_payment_block_rows": metric_value(alb2002_skip_missing_summary, "alb2002_skip_missing_payment_block_rows"),
        "alb2002_skip_missing_access_condition_rows": metric_value(alb2002_skip_missing_summary, "alb2002_skip_missing_access_condition_rows"),
        "alb2002_skip_missing_payment_nonmissing_when_not_triggered_rows": metric_value(alb2002_skip_missing_summary, "alb2002_skip_missing_payment_nonmissing_when_not_triggered_rows"),
        "alb2002_skip_missing_payment_positive_when_not_triggered_rows": metric_value(alb2002_skip_missing_summary, "alb2002_skip_missing_payment_positive_when_not_triggered_rows"),
        "alb2002_skip_missing_payment_nonmissing_cells_when_not_triggered": metric_value(alb2002_skip_missing_summary, "alb2002_skip_missing_payment_nonmissing_cells_when_not_triggered"),
        "alb2002_skip_missing_payment_zero_cells_when_not_triggered": metric_value(alb2002_skip_missing_summary, "alb2002_skip_missing_payment_zero_cells_when_not_triggered"),
        "alb2002_skip_missing_payment_positive_cells_when_not_triggered": metric_value(alb2002_skip_missing_summary, "alb2002_skip_missing_payment_positive_cells_when_not_triggered"),
        "alb2002_skip_missing_payment_zero_only_block_rows": metric_value(alb2002_skip_missing_summary, "alb2002_skip_missing_payment_zero_only_block_rows"),
        "alb2002_skip_missing_payment_no_skipped_value_block_rows": metric_value(alb2002_skip_missing_summary, "alb2002_skip_missing_payment_no_skipped_value_block_rows"),
        "alb2002_skip_missing_condition_nonmissing_when_not_triggered_rows": metric_value(alb2002_skip_missing_summary, "alb2002_skip_missing_condition_nonmissing_when_not_triggered_rows"),
        "alb2002_skip_missing_condition_missing_when_triggered_rows": metric_value(alb2002_skip_missing_summary, "alb2002_skip_missing_condition_missing_when_triggered_rows"),
        "alb2002_skip_missing_outcome_ready_rows": metric_value(alb2002_skip_missing_summary, "alb2002_skip_missing_outcome_ready_rows"),
        "alb2002_skip_missing_recipe_ready_rows": metric_value(alb2002_skip_missing_summary, "alb2002_skip_missing_recipe_ready_rows"),
        "alb2002_skip_missing_sdg382_ready_rows": metric_value(alb2002_skip_missing_summary, "alb2002_skip_missing_sdg382_ready_rows"),
        "alb2002_skip_missing_climate_linkage_ready_rows": metric_value(alb2002_skip_missing_summary, "alb2002_skip_missing_climate_linkage_ready_rows"),
        "alb2002_skip_missing_current_decision": metric_value(alb2002_skip_missing_summary, "alb2002_skip_missing_current_decision", "missing"),
        "alb2002_oop_skip_value_decision_rows": metric_value(alb2002_oop_skip_value_summary, "alb2002_oop_skip_value_decision_rows"),
        "alb2002_oop_skip_value_payment_block_rows": metric_value(alb2002_oop_skip_value_summary, "alb2002_oop_skip_value_payment_block_rows"),
        "alb2002_oop_skip_value_access_condition_block_rows": metric_value(alb2002_oop_skip_value_summary, "alb2002_oop_skip_value_access_condition_block_rows"),
        "alb2002_oop_skip_value_payment_nonmissing_skipped_rows": metric_value(alb2002_oop_skip_value_summary, "alb2002_oop_skip_value_payment_nonmissing_skipped_rows"),
        "alb2002_oop_skip_value_payment_nonmissing_skipped_cells": metric_value(alb2002_oop_skip_value_summary, "alb2002_oop_skip_value_payment_nonmissing_skipped_cells"),
        "alb2002_oop_skip_value_payment_zero_skipped_cells": metric_value(alb2002_oop_skip_value_summary, "alb2002_oop_skip_value_payment_zero_skipped_cells"),
        "alb2002_oop_skip_value_payment_positive_skipped_rows": metric_value(alb2002_oop_skip_value_summary, "alb2002_oop_skip_value_payment_positive_skipped_rows"),
        "alb2002_oop_skip_value_payment_positive_skipped_cells": metric_value(alb2002_oop_skip_value_summary, "alb2002_oop_skip_value_payment_positive_skipped_cells"),
        "alb2002_oop_skip_value_zero_skip_policy_ready_rows": metric_value(alb2002_oop_skip_value_summary, "alb2002_oop_skip_value_zero_skip_policy_ready_rows"),
        "alb2002_oop_skip_value_oop_recall_scope_ready_rows": metric_value(alb2002_oop_skip_value_summary, "alb2002_oop_skip_value_oop_recall_scope_ready_rows"),
        "alb2002_oop_skip_value_oop_inclusion_scope_ready_rows": metric_value(alb2002_oop_skip_value_summary, "alb2002_oop_skip_value_oop_inclusion_scope_ready_rows"),
        "alb2002_oop_skip_value_recipe_ready_rows": metric_value(alb2002_oop_skip_value_summary, "alb2002_oop_skip_value_recipe_ready_rows"),
        "alb2002_oop_skip_value_outcome_ready_rows": metric_value(alb2002_oop_skip_value_summary, "alb2002_oop_skip_value_outcome_ready_rows"),
        "alb2002_oop_skip_value_sdg382_ready_rows": metric_value(alb2002_oop_skip_value_summary, "alb2002_oop_skip_value_sdg382_ready_rows"),
        "alb2002_oop_skip_value_climate_linkage_ready_rows": metric_value(alb2002_oop_skip_value_summary, "alb2002_oop_skip_value_climate_linkage_ready_rows"),
        "alb2002_oop_skip_value_current_decision": metric_value(alb2002_oop_skip_value_summary, "alb2002_oop_skip_value_current_decision", "missing"),
        "alb2002_access_need_denominator_policy_rows": metric_value(alb2002_access_need_summary, "alb2002_access_need_denominator_policy_rows"),
        "alb2002_access_need_household_rows": metric_value(alb2002_access_need_summary, "alb2002_access_need_household_rows"),
        "alb2002_access_need_person_need_household_rows": metric_value(alb2002_access_need_summary, "alb2002_access_need_person_need_household_rows"),
        "alb2002_access_need_q01_need_rows": metric_value(alb2002_access_need_summary, "alb2002_access_need_q01_need_rows"),
        "alb2002_access_need_q01_cost_difficulty_rows": metric_value(alb2002_access_need_summary, "alb2002_access_need_q01_cost_difficulty_rows"),
        "alb2002_access_need_delayed_help_rows": metric_value(alb2002_access_need_summary, "alb2002_access_need_delayed_help_rows"),
        "alb2002_access_need_referral_not_gone_rows": metric_value(alb2002_access_need_summary, "alb2002_access_need_referral_not_gone_rows"),
        "alb2002_access_need_refused_service_rows": metric_value(alb2002_access_need_summary, "alb2002_access_need_refused_service_rows"),
        "alb2002_access_need_medicine_discount_any_barrier_rows": metric_value(alb2002_access_need_summary, "alb2002_access_need_medicine_discount_any_barrier_rows"),
        "alb2002_access_need_composite_cost_barrier_rows": metric_value(alb2002_access_need_summary, "alb2002_access_need_composite_cost_barrier_rows"),
        "alb2002_access_need_composite_distance_barrier_rows": metric_value(alb2002_access_need_summary, "alb2002_access_need_composite_distance_barrier_rows"),
        "alb2002_access_need_composite_supply_admin_barrier_rows": metric_value(alb2002_access_need_summary, "alb2002_access_need_composite_supply_admin_barrier_rows"),
        "alb2002_access_need_composite_any_access_barrier_rows": metric_value(alb2002_access_need_summary, "alb2002_access_need_composite_any_access_barrier_rows"),
        "alb2002_access_need_low_event_rate_rows": metric_value(alb2002_access_need_summary, "alb2002_access_need_low_event_rate_rows"),
        "alb2002_access_need_recipe_ready_rows": metric_value(alb2002_access_need_summary, "alb2002_access_need_recipe_ready_rows"),
        "alb2002_access_need_outcome_ready_rows": metric_value(alb2002_access_need_summary, "alb2002_access_need_outcome_ready_rows"),
        "alb2002_access_need_sdg382_ready_rows": metric_value(alb2002_access_need_summary, "alb2002_access_need_sdg382_ready_rows"),
        "alb2002_access_need_climate_linkage_ready_rows": metric_value(alb2002_access_need_summary, "alb2002_access_need_climate_linkage_ready_rows"),
        "alb2002_access_need_current_decision": metric_value(alb2002_access_need_summary, "alb2002_access_need_current_decision", "missing"),
        "alb2002_consumption_sdg_denominator_policy_rows": metric_value(alb2002_consumption_sdg_summary, "alb2002_consumption_sdg_denominator_policy_rows"),
        "alb2002_consumption_sdg_household_rows": metric_value(alb2002_consumption_sdg_summary, "alb2002_consumption_sdg_household_rows"),
        "alb2002_consumption_sdg_positive_total_consumption_rows": metric_value(alb2002_consumption_sdg_summary, "alb2002_consumption_sdg_positive_total_consumption_rows"),
        "alb2002_consumption_sdg_total_consumption_p50": metric_value(alb2002_consumption_sdg_summary, "alb2002_consumption_sdg_total_consumption_p50"),
        "alb2002_consumption_sdg_total_consumption_p95": metric_value(alb2002_consumption_sdg_summary, "alb2002_consumption_sdg_total_consumption_p95"),
        "alb2002_consumption_sdg_positive_household_weight_rows": metric_value(alb2002_consumption_sdg_summary, "alb2002_consumption_sdg_positive_household_weight_rows"),
        "alb2002_consumption_sdg_positive_household_size_rows": metric_value(alb2002_consumption_sdg_summary, "alb2002_consumption_sdg_positive_household_size_rows"),
        "alb2002_consumption_sdg_che10_4w_unreviewed_rate": metric_value(alb2002_consumption_sdg_summary, "alb2002_consumption_sdg_che10_4w_unreviewed_rate"),
        "alb2002_consumption_sdg_che25_4w_unreviewed_rate": metric_value(alb2002_consumption_sdg_summary, "alb2002_consumption_sdg_che25_4w_unreviewed_rate"),
        "alb2002_consumption_sdg_che10_12m_unreviewed_rate": metric_value(alb2002_consumption_sdg_summary, "alb2002_consumption_sdg_che10_12m_unreviewed_rate"),
        "alb2002_consumption_sdg_che25_12m_unreviewed_rate": metric_value(alb2002_consumption_sdg_summary, "alb2002_consumption_sdg_che25_12m_unreviewed_rate"),
        "alb2002_consumption_sdg_spl_ready_rows": metric_value(alb2002_consumption_sdg_summary, "alb2002_consumption_sdg_spl_ready_rows"),
        "alb2002_consumption_sdg_ppp_cpi_ready_rows": metric_value(alb2002_consumption_sdg_summary, "alb2002_consumption_sdg_ppp_cpi_ready_rows"),
        "alb2002_consumption_sdg_discretionary_budget_ready_rows": metric_value(alb2002_consumption_sdg_summary, "alb2002_consumption_sdg_discretionary_budget_ready_rows"),
        "alb2002_consumption_sdg_che_denominator_ready_rows": metric_value(alb2002_consumption_sdg_summary, "alb2002_consumption_sdg_che_denominator_ready_rows"),
        "alb2002_consumption_sdg_recipe_ready_rows": metric_value(alb2002_consumption_sdg_summary, "alb2002_consumption_sdg_recipe_ready_rows"),
        "alb2002_consumption_sdg_outcome_ready_rows": metric_value(alb2002_consumption_sdg_summary, "alb2002_consumption_sdg_outcome_ready_rows"),
        "alb2002_consumption_sdg_sdg382_ready_rows": metric_value(alb2002_consumption_sdg_summary, "alb2002_consumption_sdg_sdg382_ready_rows"),
        "alb2002_consumption_sdg_climate_linkage_ready_rows": metric_value(alb2002_consumption_sdg_summary, "alb2002_consumption_sdg_climate_linkage_ready_rows"),
        "alb2002_consumption_sdg_current_decision": metric_value(alb2002_consumption_sdg_summary, "alb2002_consumption_sdg_current_decision", "missing"),
        "alb2002_consumption_construction_source_audit_rows": metric_value(alb2002_consumption_construction_summary, "alb2002_consumption_construction_source_audit_rows"),
        "alb2002_consumption_construction_public_pdf_present": metric_value(alb2002_consumption_construction_summary, "alb2002_consumption_construction_public_pdf_present"),
        "alb2002_consumption_construction_program_zip_present": metric_value(alb2002_consumption_construction_summary, "alb2002_consumption_construction_program_zip_present"),
        "alb2002_consumption_construction_do_file_rows": metric_value(alb2002_consumption_construction_summary, "alb2002_consumption_construction_do_file_rows"),
        "alb2002_consumption_construction_totcons_do_present": metric_value(alb2002_consumption_construction_summary, "alb2002_consumption_construction_totcons_do_present"),
        "alb2002_consumption_construction_poverty_do_present": metric_value(alb2002_consumption_construction_summary, "alb2002_consumption_construction_poverty_do_present"),
        "alb2002_consumption_construction_metadata_json_present": metric_value(alb2002_consumption_construction_summary, "alb2002_consumption_construction_metadata_json_present"),
        "alb2002_consumption_construction_documentation_ready_rows": metric_value(alb2002_consumption_construction_summary, "alb2002_consumption_construction_documentation_ready_rows"),
        "alb2002_consumption_construction_released_variable_mapping_ready_rows": metric_value(alb2002_consumption_construction_summary, "alb2002_consumption_construction_released_variable_mapping_ready_rows"),
        "alb2002_consumption_construction_denominator_variant_ready_rows": metric_value(alb2002_consumption_construction_summary, "alb2002_consumption_construction_denominator_variant_ready_rows"),
        "alb2002_consumption_construction_recipe_ready_rows": metric_value(alb2002_consumption_construction_summary, "alb2002_consumption_construction_recipe_ready_rows"),
        "alb2002_consumption_construction_outcome_ready_rows": metric_value(alb2002_consumption_construction_summary, "alb2002_consumption_construction_outcome_ready_rows"),
        "alb2002_consumption_construction_sdg382_ready_rows": metric_value(alb2002_consumption_construction_summary, "alb2002_consumption_construction_sdg382_ready_rows"),
        "alb2002_consumption_construction_climate_linkage_ready_rows": metric_value(alb2002_consumption_construction_summary, "alb2002_consumption_construction_climate_linkage_ready_rows"),
        "alb2002_consumption_construction_current_decision": metric_value(alb2002_consumption_construction_summary, "alb2002_consumption_construction_current_decision", "missing"),
        "alb2002_consumption_aggregate_crosswalk_rows": metric_value(alb2002_consumption_aggregate_summary, "alb2002_consumption_aggregate_crosswalk_rows"),
        "alb2002_consumption_aggregate_crosswalk_local_poverty_rows": metric_value(alb2002_consumption_aggregate_summary, "alb2002_consumption_aggregate_crosswalk_local_poverty_rows"),
        "alb2002_consumption_aggregate_crosswalk_metadata_catalog_rows": metric_value(alb2002_consumption_aggregate_summary, "alb2002_consumption_aggregate_crosswalk_metadata_catalog_rows"),
        "alb2002_consumption_aggregate_crosswalk_raw_totcons_positive_rows": metric_value(alb2002_consumption_aggregate_summary, "alb2002_consumption_aggregate_crosswalk_raw_totcons_positive_rows"),
        "alb2002_consumption_aggregate_crosswalk_candidate_totcons_match_rows": metric_value(alb2002_consumption_aggregate_summary, "alb2002_consumption_aggregate_crosswalk_candidate_totcons_match_rows"),
        "alb2002_consumption_aggregate_crosswalk_scale_ratio_within_10pct_rows": metric_value(alb2002_consumption_aggregate_summary, "alb2002_consumption_aggregate_crosswalk_scale_ratio_within_10pct_rows"),
        "alb2002_consumption_aggregate_crosswalk_questionnaire_new_lek_hits": metric_value(alb2002_consumption_aggregate_summary, "alb2002_consumption_aggregate_crosswalk_questionnaire_new_lek_hits"),
        "alb2002_consumption_aggregate_crosswalk_questionnaire_aggregate_formula_hits": metric_value(alb2002_consumption_aggregate_summary, "alb2002_consumption_aggregate_crosswalk_questionnaire_aggregate_formula_hits"),
        "alb2002_consumption_aggregate_crosswalk_construction_source_rows": metric_value(alb2002_consumption_aggregate_summary, "alb2002_consumption_aggregate_crosswalk_construction_source_rows"),
        "alb2002_consumption_aggregate_crosswalk_construction_do_file_rows": metric_value(alb2002_consumption_aggregate_summary, "alb2002_consumption_aggregate_crosswalk_construction_do_file_rows"),
        "alb2002_consumption_aggregate_crosswalk_metadata_unit_period_ready_rows": metric_value(alb2002_consumption_aggregate_summary, "alb2002_consumption_aggregate_crosswalk_metadata_unit_period_ready_rows"),
        "alb2002_consumption_aggregate_crosswalk_official_documentation_ready_rows": metric_value(alb2002_consumption_aggregate_summary, "alb2002_consumption_aggregate_crosswalk_official_documentation_ready_rows"),
        "alb2002_consumption_aggregate_crosswalk_released_variable_mapping_ready_rows": metric_value(alb2002_consumption_aggregate_summary, "alb2002_consumption_aggregate_crosswalk_released_variable_mapping_ready_rows"),
        "alb2002_consumption_aggregate_crosswalk_denominator_variant_ready_rows": metric_value(alb2002_consumption_aggregate_summary, "alb2002_consumption_aggregate_crosswalk_denominator_variant_ready_rows"),
        "alb2002_consumption_aggregate_crosswalk_recipe_ready_rows": metric_value(alb2002_consumption_aggregate_summary, "alb2002_consumption_aggregate_crosswalk_recipe_ready_rows"),
        "alb2002_consumption_aggregate_crosswalk_outcome_ready_rows": metric_value(alb2002_consumption_aggregate_summary, "alb2002_consumption_aggregate_crosswalk_outcome_ready_rows"),
        "alb2002_consumption_aggregate_crosswalk_sdg382_ready_rows": metric_value(alb2002_consumption_aggregate_summary, "alb2002_consumption_aggregate_crosswalk_sdg382_ready_rows"),
        "alb2002_consumption_aggregate_crosswalk_climate_linkage_ready_rows": metric_value(alb2002_consumption_aggregate_summary, "alb2002_consumption_aggregate_crosswalk_climate_linkage_ready_rows"),
        "alb2002_consumption_aggregate_crosswalk_current_decision": metric_value(alb2002_consumption_aggregate_summary, "alb2002_consumption_aggregate_crosswalk_current_decision", "missing"),
        "alb2002_period_aligned_che_policy_rows": metric_value(alb2002_period_aligned_che_summary, "alb2002_period_aligned_che_policy_rows"),
        "alb2002_period_aligned_che_household_rows": metric_value(alb2002_period_aligned_che_summary, "alb2002_period_aligned_che_household_rows"),
        "alb2002_period_aligned_che_denominator_rows": metric_value(alb2002_period_aligned_che_summary, "alb2002_period_aligned_che_denominator_rows"),
        "alb2002_period_aligned_che_denominator_documented_rows": metric_value(alb2002_period_aligned_che_summary, "alb2002_period_aligned_che_denominator_documented_rows"),
        "alb2002_period_aligned_che_period_alignment_ready_rows": metric_value(alb2002_period_aligned_che_summary, "alb2002_period_aligned_che_period_alignment_ready_rows"),
        "alb2002_period_aligned_che_combined_che10_rate": metric_value(alb2002_period_aligned_che_summary, "alb2002_period_aligned_che_combined_che10_rate"),
        "alb2002_period_aligned_che_combined_che10_weighted_rate": metric_value(alb2002_period_aligned_che_summary, "alb2002_period_aligned_che_combined_che10_weighted_rate"),
        "alb2002_period_aligned_che_combined_che25_rate": metric_value(alb2002_period_aligned_che_summary, "alb2002_period_aligned_che_combined_che25_rate"),
        "alb2002_period_aligned_che_combined_che25_weighted_rate": metric_value(alb2002_period_aligned_che_summary, "alb2002_period_aligned_che_combined_che25_weighted_rate"),
        "alb2002_period_aligned_che_outcome_ready_rows": metric_value(alb2002_period_aligned_che_summary, "alb2002_period_aligned_che_outcome_ready_rows"),
        "alb2002_period_aligned_che_recipe_ready_rows": metric_value(alb2002_period_aligned_che_summary, "alb2002_period_aligned_che_recipe_ready_rows"),
        "alb2002_period_aligned_che_sdg382_ready_rows": metric_value(alb2002_period_aligned_che_summary, "alb2002_period_aligned_che_sdg382_ready_rows"),
        "alb2002_period_aligned_che_climate_linkage_ready_rows": metric_value(alb2002_period_aligned_che_summary, "alb2002_period_aligned_che_climate_linkage_ready_rows"),
        "alb2002_period_aligned_che_current_decision": metric_value(alb2002_period_aligned_che_summary, "alb2002_period_aligned_che_current_decision", "missing"),
        "alb2002_che_candidate_household_rows": metric_value(alb2002_che_candidate_summary, "alb2002_che_candidate_household_rows"),
        "alb2002_che_candidate_denominator_rows": metric_value(alb2002_che_candidate_summary, "alb2002_che_candidate_denominator_rows"),
        "alb2002_che_candidate_missing_rows": metric_value(alb2002_che_candidate_summary, "alb2002_che_candidate_missing_rows"),
        "alb2002_che_candidate_positive_oop_rows": metric_value(alb2002_che_candidate_summary, "alb2002_che_candidate_positive_oop_rows"),
        "alb2002_che_candidate_positive_oop_weighted_rate": metric_value(alb2002_che_candidate_summary, "alb2002_che_candidate_positive_oop_weighted_rate"),
        "alb2002_che_candidate_che10_rows": metric_value(alb2002_che_candidate_summary, "alb2002_che_candidate_che10_rows"),
        "alb2002_che_candidate_che10_rate": metric_value(alb2002_che_candidate_summary, "alb2002_che_candidate_che10_rate"),
        "alb2002_che_candidate_che10_weighted_rate": metric_value(alb2002_che_candidate_summary, "alb2002_che_candidate_che10_weighted_rate"),
        "alb2002_che_candidate_che25_rows": metric_value(alb2002_che_candidate_summary, "alb2002_che_candidate_che25_rows"),
        "alb2002_che_candidate_che25_rate": metric_value(alb2002_che_candidate_summary, "alb2002_che_candidate_che25_rate"),
        "alb2002_che_candidate_che25_weighted_rate": metric_value(alb2002_che_candidate_summary, "alb2002_che_candidate_che25_weighted_rate"),
        "alb2002_che_candidate_period_policy_rows": metric_value(alb2002_che_candidate_summary, "alb2002_che_candidate_period_policy_rows"),
        "alb2002_che_candidate_weight_positive_rows": metric_value(alb2002_che_candidate_summary, "alb2002_che_candidate_weight_positive_rows"),
        "alb2002_che_candidate_weighted_inference_ready_rows": metric_value(alb2002_che_candidate_summary, "alb2002_che_candidate_weighted_inference_ready_rows"),
        "alb2002_che_candidate_minimum_recipe_harmonized_ready_rows": metric_value(alb2002_che_candidate_summary, "alb2002_che_candidate_minimum_recipe_harmonized_ready_rows"),
        "alb2002_che_candidate_minimum_recipe_outcome_ready_rows": metric_value(alb2002_che_candidate_summary, "alb2002_che_candidate_minimum_recipe_outcome_ready_rows"),
        "alb2002_che_candidate_climate_linkage_ready_rows": metric_value(alb2002_che_candidate_summary, "alb2002_che_candidate_climate_linkage_ready_rows"),
        "alb2002_che_candidate_outcome_promotion_ready_rows": metric_value(alb2002_che_candidate_summary, "alb2002_che_candidate_outcome_promotion_ready_rows"),
        "alb2002_che_candidate_current_decision": metric_value(alb2002_che_candidate_summary, "alb2002_che_candidate_current_decision", "missing"),
        "alb2002_access_candidate_household_rows": metric_value(alb2002_access_candidate_summary, "alb2002_access_candidate_household_rows"),
        "alb2002_access_candidate_lineage_rows": metric_value(alb2002_access_candidate_summary, "alb2002_access_candidate_lineage_rows"),
        "alb2002_access_candidate_audit_rows": metric_value(alb2002_access_candidate_summary, "alb2002_access_candidate_audit_rows"),
        "alb2002_access_candidate_q01_need_rows": metric_value(alb2002_access_candidate_summary, "alb2002_access_candidate_q01_need_rows"),
        "alb2002_access_candidate_person_need_rows": metric_value(alb2002_access_candidate_summary, "alb2002_access_candidate_person_need_rows"),
        "alb2002_access_candidate_q01_cost_difficulty_rows": metric_value(alb2002_access_candidate_summary, "alb2002_access_candidate_q01_cost_difficulty_rows"),
        "alb2002_access_candidate_delayed_help_rows": metric_value(alb2002_access_candidate_summary, "alb2002_access_candidate_delayed_help_rows"),
        "alb2002_access_candidate_referral_not_gone_rows": metric_value(alb2002_access_candidate_summary, "alb2002_access_candidate_referral_not_gone_rows"),
        "alb2002_access_candidate_refused_service_rows": metric_value(alb2002_access_candidate_summary, "alb2002_access_candidate_refused_service_rows"),
        "alb2002_access_candidate_medicine_discount_any_barrier_rows": metric_value(alb2002_access_candidate_summary, "alb2002_access_candidate_medicine_discount_any_barrier_rows"),
        "alb2002_access_candidate_composite_cost_rows": metric_value(alb2002_access_candidate_summary, "alb2002_access_candidate_composite_cost_rows"),
        "alb2002_access_candidate_composite_cost_rate": metric_value(alb2002_access_candidate_summary, "alb2002_access_candidate_composite_cost_rate"),
        "alb2002_access_candidate_composite_cost_weighted_rate": metric_value(alb2002_access_candidate_summary, "alb2002_access_candidate_composite_cost_weighted_rate"),
        "alb2002_access_candidate_composite_any_rows": metric_value(alb2002_access_candidate_summary, "alb2002_access_candidate_composite_any_rows"),
        "alb2002_access_candidate_composite_any_rate": metric_value(alb2002_access_candidate_summary, "alb2002_access_candidate_composite_any_rate"),
        "alb2002_access_candidate_composite_any_weighted_rate": metric_value(alb2002_access_candidate_summary, "alb2002_access_candidate_composite_any_weighted_rate"),
        "alb2002_access_candidate_low_event_rate_rows": metric_value(alb2002_access_candidate_summary, "alb2002_access_candidate_low_event_rate_rows"),
        "alb2002_access_candidate_outcome_promotion_ready_rows": metric_value(alb2002_access_candidate_summary, "alb2002_access_candidate_outcome_promotion_ready_rows"),
        "alb2002_access_candidate_recipe_ready_rows": metric_value(alb2002_access_candidate_summary, "alb2002_access_candidate_recipe_ready_rows"),
        "alb2002_access_candidate_climate_linkage_ready_rows": metric_value(alb2002_access_candidate_summary, "alb2002_access_candidate_climate_linkage_ready_rows"),
        "alb2002_access_candidate_current_decision": metric_value(alb2002_access_candidate_summary, "alb2002_access_candidate_current_decision", "missing"),
        "alb2002_uhc_composite_candidate_household_rows": metric_value(alb2002_uhc_composite_summary, "alb2002_uhc_composite_candidate_household_rows"),
        "alb2002_uhc_composite_candidate_lineage_rows": metric_value(alb2002_uhc_composite_summary, "alb2002_uhc_composite_candidate_lineage_rows"),
        "alb2002_uhc_composite_candidate_audit_rows": metric_value(alb2002_uhc_composite_summary, "alb2002_uhc_composite_candidate_audit_rows"),
        "alb2002_uhc_composite_candidate_source_che10_rows": metric_value(alb2002_uhc_composite_summary, "alb2002_uhc_composite_candidate_source_che10_rows"),
        "alb2002_uhc_composite_candidate_source_che25_rows": metric_value(alb2002_uhc_composite_summary, "alb2002_uhc_composite_candidate_source_che25_rows"),
        "alb2002_uhc_composite_candidate_source_access_any_rows": metric_value(alb2002_uhc_composite_summary, "alb2002_uhc_composite_candidate_source_access_any_rows"),
        "alb2002_uhc_composite_candidate_che10_or_access_rows": metric_value(alb2002_uhc_composite_summary, "alb2002_uhc_composite_candidate_che10_or_access_rows"),
        "alb2002_uhc_composite_candidate_che10_or_access_rate": metric_value(alb2002_uhc_composite_summary, "alb2002_uhc_composite_candidate_che10_or_access_rate"),
        "alb2002_uhc_composite_candidate_che10_or_access_weighted_rate": metric_value(alb2002_uhc_composite_summary, "alb2002_uhc_composite_candidate_che10_or_access_weighted_rate"),
        "alb2002_uhc_composite_candidate_che25_or_access_rows": metric_value(alb2002_uhc_composite_summary, "alb2002_uhc_composite_candidate_che25_or_access_rows"),
        "alb2002_uhc_composite_candidate_che25_or_access_rate": metric_value(alb2002_uhc_composite_summary, "alb2002_uhc_composite_candidate_che25_or_access_rate"),
        "alb2002_uhc_composite_candidate_che25_or_access_weighted_rate": metric_value(alb2002_uhc_composite_summary, "alb2002_uhc_composite_candidate_che25_or_access_weighted_rate"),
        "alb2002_uhc_composite_candidate_financial_only_che10_rows": metric_value(alb2002_uhc_composite_summary, "alb2002_uhc_composite_candidate_financial_only_che10_rows"),
        "alb2002_uhc_composite_candidate_access_only_vs_che10_rows": metric_value(alb2002_uhc_composite_summary, "alb2002_uhc_composite_candidate_access_only_vs_che10_rows"),
        "alb2002_uhc_composite_candidate_both_che10_access_rows": metric_value(alb2002_uhc_composite_summary, "alb2002_uhc_composite_candidate_both_che10_access_rows"),
        "alb2002_uhc_composite_candidate_financial_only_che25_rows": metric_value(alb2002_uhc_composite_summary, "alb2002_uhc_composite_candidate_financial_only_che25_rows"),
        "alb2002_uhc_composite_candidate_access_only_vs_che25_rows": metric_value(alb2002_uhc_composite_summary, "alb2002_uhc_composite_candidate_access_only_vs_che25_rows"),
        "alb2002_uhc_composite_candidate_both_che25_access_rows": metric_value(alb2002_uhc_composite_summary, "alb2002_uhc_composite_candidate_both_che25_access_rows"),
        "alb2002_uhc_composite_candidate_coping_rows": metric_value(alb2002_uhc_composite_summary, "alb2002_uhc_composite_candidate_coping_rows"),
        "alb2002_uhc_composite_candidate_low_event_rate_rows": metric_value(alb2002_uhc_composite_summary, "alb2002_uhc_composite_candidate_low_event_rate_rows"),
        "alb2002_uhc_composite_candidate_outcome_promotion_ready_rows": metric_value(alb2002_uhc_composite_summary, "alb2002_uhc_composite_candidate_outcome_promotion_ready_rows"),
        "alb2002_uhc_composite_candidate_recipe_ready_rows": metric_value(alb2002_uhc_composite_summary, "alb2002_uhc_composite_candidate_recipe_ready_rows"),
        "alb2002_uhc_composite_candidate_climate_linkage_ready_rows": metric_value(alb2002_uhc_composite_summary, "alb2002_uhc_composite_candidate_climate_linkage_ready_rows"),
        "alb2002_uhc_composite_candidate_current_decision": metric_value(alb2002_uhc_composite_summary, "alb2002_uhc_composite_candidate_current_decision", "missing"),
        "alb2002_analysis_candidate_rows": metric_value(alb2002_analysis_candidate_summary, "alb2002_analysis_candidate_rows"),
        "alb2002_analysis_candidate_columns": metric_value(alb2002_analysis_candidate_summary, "alb2002_analysis_candidate_columns"),
        "alb2002_analysis_candidate_lineage_rows": metric_value(alb2002_analysis_candidate_summary, "alb2002_analysis_candidate_lineage_rows"),
        "alb2002_analysis_candidate_audit_rows": metric_value(alb2002_analysis_candidate_summary, "alb2002_analysis_candidate_audit_rows"),
        "alb2002_analysis_candidate_complete_candidate_gates": metric_value(alb2002_analysis_candidate_summary, "alb2002_analysis_candidate_complete_candidate_gates"),
        "alb2002_analysis_candidate_missing_gates": metric_value(alb2002_analysis_candidate_summary, "alb2002_analysis_candidate_missing_gates"),
        "alb2002_analysis_candidate_blocked_promotion_gates": metric_value(alb2002_analysis_candidate_summary, "alb2002_analysis_candidate_blocked_promotion_gates"),
        "alb2002_analysis_candidate_harmonized_ready_rows": metric_value(alb2002_analysis_candidate_summary, "alb2002_analysis_candidate_harmonized_ready_rows"),
        "alb2002_analysis_candidate_outcome_promotion_ready_rows": metric_value(alb2002_analysis_candidate_summary, "alb2002_analysis_candidate_outcome_promotion_ready_rows"),
        "alb2002_analysis_candidate_climate_linkage_ready_rows": metric_value(alb2002_analysis_candidate_summary, "alb2002_analysis_candidate_climate_linkage_ready_rows"),
        "alb2002_analysis_candidate_data_write_ready_rows": metric_value(alb2002_analysis_candidate_summary, "alb2002_analysis_candidate_data_write_ready_rows"),
        "alb2002_analysis_candidate_current_decision": metric_value(alb2002_analysis_candidate_summary, "alb2002_analysis_candidate_current_decision", "missing"),
        "alb2002_climate_centroid_input_rows": metric_value(alb2002_climate_centroid_summary, "alb2002_climate_centroid_input_rows"),
        "alb2002_climate_centroid_distinct_district_rows": metric_value(alb2002_climate_centroid_summary, "alb2002_climate_centroid_distinct_district_rows"),
        "alb2002_climate_centroid_household_rows_covered": metric_value(alb2002_climate_centroid_summary, "alb2002_climate_centroid_household_rows_covered"),
        "alb2002_climate_centroid_exposure_rows": metric_value(alb2002_climate_centroid_summary, "alb2002_climate_centroid_exposure_rows"),
        "alb2002_climate_centroid_window_rows": metric_value(alb2002_climate_centroid_summary, "alb2002_climate_centroid_window_rows"),
        "alb2002_climate_centroid_nasa_api_rows": metric_value(alb2002_climate_centroid_summary, "alb2002_climate_centroid_nasa_api_rows"),
        "alb2002_climate_centroid_nasa_downloaded_rows": metric_value(alb2002_climate_centroid_summary, "alb2002_climate_centroid_nasa_downloaded_rows"),
        "alb2002_climate_centroid_nasa_cached_rows": metric_value(alb2002_climate_centroid_summary, "alb2002_climate_centroid_nasa_cached_rows"),
        "alb2002_climate_centroid_nasa_failed_rows": metric_value(alb2002_climate_centroid_summary, "alb2002_climate_centroid_nasa_failed_rows"),
        "alb2002_climate_centroid_precip_nonmissing_rows": metric_value(alb2002_climate_centroid_summary, "alb2002_climate_centroid_precip_nonmissing_rows"),
        "alb2002_climate_centroid_temp_nonmissing_rows": metric_value(alb2002_climate_centroid_summary, "alb2002_climate_centroid_temp_nonmissing_rows"),
        "alb2002_climate_centroid_boundary_year": metric_value(alb2002_climate_centroid_summary, "alb2002_climate_centroid_boundary_year", "missing"),
        "alb2002_climate_centroid_historical_boundary_ready_rows": metric_value(alb2002_climate_centroid_summary, "alb2002_climate_centroid_historical_boundary_ready_rows"),
        "alb2002_climate_centroid_primary_chirps_ready_rows": metric_value(alb2002_climate_centroid_summary, "alb2002_climate_centroid_primary_chirps_ready_rows"),
        "alb2002_climate_centroid_primary_era5_ready_rows": metric_value(alb2002_climate_centroid_summary, "alb2002_climate_centroid_primary_era5_ready_rows"),
        "alb2002_climate_centroid_historical_baseline_ready_rows": metric_value(alb2002_climate_centroid_summary, "alb2002_climate_centroid_historical_baseline_ready_rows"),
        "alb2002_climate_centroid_climate_linkage_ready_rows": metric_value(alb2002_climate_centroid_summary, "alb2002_climate_centroid_climate_linkage_ready_rows"),
        "alb2002_climate_centroid_data_write_ready_rows": metric_value(alb2002_climate_centroid_summary, "alb2002_climate_centroid_data_write_ready_rows"),
        "alb2002_climate_centroid_current_decision": metric_value(alb2002_climate_centroid_summary, "alb2002_climate_centroid_current_decision", "missing"),
        "alb2002_climate_shock_candidate_exposure_rows": metric_value(alb2002_climate_shock_summary, "alb2002_climate_shock_candidate_exposure_rows"),
        "alb2002_climate_shock_candidate_source_centroid_rows": metric_value(alb2002_climate_shock_summary, "alb2002_climate_shock_candidate_source_centroid_rows"),
        "alb2002_climate_shock_candidate_lineage_rows": metric_value(alb2002_climate_shock_summary, "alb2002_climate_shock_candidate_lineage_rows"),
        "alb2002_climate_shock_candidate_audit_rows": metric_value(alb2002_climate_shock_summary, "alb2002_climate_shock_candidate_audit_rows"),
        "alb2002_climate_shock_candidate_reference_group_rows": metric_value(alb2002_climate_shock_summary, "alb2002_climate_shock_candidate_reference_group_rows"),
        "alb2002_climate_shock_candidate_min_reference_group_size": metric_value(alb2002_climate_shock_summary, "alb2002_climate_shock_candidate_min_reference_group_size"),
        "alb2002_climate_shock_candidate_precip_z_nonmissing_rows": metric_value(alb2002_climate_shock_summary, "alb2002_climate_shock_candidate_precip_z_nonmissing_rows"),
        "alb2002_climate_shock_candidate_temp_z_nonmissing_rows": metric_value(alb2002_climate_shock_summary, "alb2002_climate_shock_candidate_temp_z_nonmissing_rows"),
        "alb2002_climate_shock_candidate_low_rain_rows": metric_value(alb2002_climate_shock_summary, "alb2002_climate_shock_candidate_low_rain_rows"),
        "alb2002_climate_shock_candidate_severe_low_rain_rows": metric_value(alb2002_climate_shock_summary, "alb2002_climate_shock_candidate_severe_low_rain_rows"),
        "alb2002_climate_shock_candidate_extreme_wet_rows": metric_value(alb2002_climate_shock_summary, "alb2002_climate_shock_candidate_extreme_wet_rows"),
        "alb2002_climate_shock_candidate_heat_rows": metric_value(alb2002_climate_shock_summary, "alb2002_climate_shock_candidate_heat_rows"),
        "alb2002_climate_shock_candidate_extreme_heat_rows": metric_value(alb2002_climate_shock_summary, "alb2002_climate_shock_candidate_extreme_heat_rows"),
        "alb2002_climate_shock_candidate_cold_rows": metric_value(alb2002_climate_shock_summary, "alb2002_climate_shock_candidate_cold_rows"),
        "alb2002_climate_shock_candidate_combined_stress_rows": metric_value(alb2002_climate_shock_summary, "alb2002_climate_shock_candidate_combined_stress_rows"),
        "alb2002_climate_shock_candidate_primary_chirps_ready_rows": metric_value(alb2002_climate_shock_summary, "alb2002_climate_shock_candidate_primary_chirps_ready_rows"),
        "alb2002_climate_shock_candidate_primary_era5_ready_rows": metric_value(alb2002_climate_shock_summary, "alb2002_climate_shock_candidate_primary_era5_ready_rows"),
        "alb2002_climate_shock_candidate_historical_baseline_ready_rows": metric_value(alb2002_climate_shock_summary, "alb2002_climate_shock_candidate_historical_baseline_ready_rows"),
        "alb2002_climate_shock_candidate_climate_linkage_ready_rows": metric_value(alb2002_climate_shock_summary, "alb2002_climate_shock_candidate_climate_linkage_ready_rows"),
        "alb2002_climate_shock_candidate_data_write_ready_rows": metric_value(alb2002_climate_shock_summary, "alb2002_climate_shock_candidate_data_write_ready_rows"),
        "alb2002_climate_shock_candidate_current_decision": metric_value(alb2002_climate_shock_summary, "alb2002_climate_shock_candidate_current_decision", "missing"),
        "alb2002_climate_outcome_linked_candidate_rows": metric_value(alb2002_climate_outcome_linked_summary, "alb2002_climate_outcome_linked_candidate_rows"),
        "alb2002_climate_outcome_linked_candidate_household_rows": metric_value(alb2002_climate_outcome_linked_summary, "alb2002_climate_outcome_linked_candidate_household_rows"),
        "alb2002_climate_outcome_linked_candidate_window_rows": metric_value(alb2002_climate_outcome_linked_summary, "alb2002_climate_outcome_linked_candidate_window_rows"),
        "alb2002_climate_outcome_linked_candidate_district_month_cells": metric_value(alb2002_climate_outcome_linked_summary, "alb2002_climate_outcome_linked_candidate_district_month_cells"),
        "alb2002_climate_outcome_linked_candidate_lineage_rows": metric_value(alb2002_climate_outcome_linked_summary, "alb2002_climate_outcome_linked_candidate_lineage_rows"),
        "alb2002_climate_outcome_linked_candidate_audit_rows": metric_value(alb2002_climate_outcome_linked_summary, "alb2002_climate_outcome_linked_candidate_audit_rows"),
        "alb2002_climate_outcome_linked_candidate_source_analysis_rows": metric_value(alb2002_climate_outcome_linked_summary, "alb2002_climate_outcome_linked_candidate_source_analysis_rows"),
        "alb2002_climate_outcome_linked_candidate_source_uhc_rows": metric_value(alb2002_climate_outcome_linked_summary, "alb2002_climate_outcome_linked_candidate_source_uhc_rows"),
        "alb2002_climate_outcome_linked_candidate_source_shock_rows": metric_value(alb2002_climate_outcome_linked_summary, "alb2002_climate_outcome_linked_candidate_source_shock_rows"),
        "alb2002_climate_outcome_linked_candidate_expected_rows": metric_value(alb2002_climate_outcome_linked_summary, "alb2002_climate_outcome_linked_candidate_expected_rows"),
        "alb2002_climate_outcome_linked_candidate_unmatched_rows": metric_value(alb2002_climate_outcome_linked_summary, "alb2002_climate_outcome_linked_candidate_unmatched_rows"),
        "alb2002_climate_outcome_linked_candidate_precip_z_rows": metric_value(alb2002_climate_outcome_linked_summary, "alb2002_climate_outcome_linked_candidate_precip_z_rows"),
        "alb2002_climate_outcome_linked_candidate_temp_z_rows": metric_value(alb2002_climate_outcome_linked_summary, "alb2002_climate_outcome_linked_candidate_temp_z_rows"),
        "alb2002_climate_outcome_linked_candidate_combined_stress_rows": metric_value(alb2002_climate_outcome_linked_summary, "alb2002_climate_outcome_linked_candidate_combined_stress_rows"),
        "alb2002_climate_outcome_linked_candidate_che10_or_access_rows": metric_value(alb2002_climate_outcome_linked_summary, "alb2002_climate_outcome_linked_candidate_che10_or_access_rows"),
        "alb2002_climate_outcome_linked_candidate_che25_or_access_rows": metric_value(alb2002_climate_outcome_linked_summary, "alb2002_climate_outcome_linked_candidate_che25_or_access_rows"),
        "alb2002_climate_outcome_linked_candidate_both_che10_access_rows": metric_value(alb2002_climate_outcome_linked_summary, "alb2002_climate_outcome_linked_candidate_both_che10_access_rows"),
        "alb2002_climate_outcome_linked_candidate_coping_rows": metric_value(alb2002_climate_outcome_linked_summary, "alb2002_climate_outcome_linked_candidate_coping_rows"),
        "alb2002_climate_outcome_linked_candidate_climate_linkage_ready_rows": metric_value(alb2002_climate_outcome_linked_summary, "alb2002_climate_outcome_linked_candidate_climate_linkage_ready_rows"),
        "alb2002_climate_outcome_linked_candidate_outcome_promotion_ready_rows": metric_value(alb2002_climate_outcome_linked_summary, "alb2002_climate_outcome_linked_candidate_outcome_promotion_ready_rows"),
        "alb2002_climate_outcome_linked_candidate_harmonized_recipe_ready_rows": metric_value(alb2002_climate_outcome_linked_summary, "alb2002_climate_outcome_linked_candidate_harmonized_recipe_ready_rows"),
        "alb2002_climate_outcome_linked_candidate_data_write_ready_rows": metric_value(alb2002_climate_outcome_linked_summary, "alb2002_climate_outcome_linked_candidate_data_write_ready_rows"),
        "alb2002_climate_outcome_linked_candidate_current_decision": metric_value(alb2002_climate_outcome_linked_summary, "alb2002_climate_outcome_linked_candidate_current_decision", "missing"),
        "alb2002_linked_candidate_descriptive_input_rows": metric_value(alb2002_linked_candidate_descriptive_summary, "alb2002_linked_candidate_descriptive_input_rows"),
        "alb2002_linked_candidate_descriptive_household_rows": metric_value(alb2002_linked_candidate_descriptive_summary, "alb2002_linked_candidate_descriptive_household_rows"),
        "alb2002_linked_candidate_descriptive_window_rows": metric_value(alb2002_linked_candidate_descriptive_summary, "alb2002_linked_candidate_descriptive_window_rows"),
        "alb2002_linked_candidate_descriptive_audit_rows": metric_value(alb2002_linked_candidate_descriptive_summary, "alb2002_linked_candidate_descriptive_audit_rows"),
        "alb2002_linked_candidate_descriptive_cell_rows": metric_value(alb2002_linked_candidate_descriptive_summary, "alb2002_linked_candidate_descriptive_cell_rows"),
        "alb2002_linked_candidate_descriptive_household_outcome_cell_rows": metric_value(alb2002_linked_candidate_descriptive_summary, "alb2002_linked_candidate_descriptive_household_outcome_cell_rows"),
        "alb2002_linked_candidate_descriptive_subgroup_outcome_cell_rows": metric_value(alb2002_linked_candidate_descriptive_summary, "alb2002_linked_candidate_descriptive_subgroup_outcome_cell_rows"),
        "alb2002_linked_candidate_descriptive_climate_flag_cell_rows": metric_value(alb2002_linked_candidate_descriptive_summary, "alb2002_linked_candidate_descriptive_climate_flag_cell_rows"),
        "alb2002_linked_candidate_descriptive_outcome_by_climate_flag_cell_rows": metric_value(alb2002_linked_candidate_descriptive_summary, "alb2002_linked_candidate_descriptive_outcome_by_climate_flag_cell_rows"),
        "alb2002_linked_candidate_descriptive_che10_or_access_households": metric_value(alb2002_linked_candidate_descriptive_summary, "alb2002_linked_candidate_descriptive_che10_or_access_households"),
        "alb2002_linked_candidate_descriptive_che25_or_access_households": metric_value(alb2002_linked_candidate_descriptive_summary, "alb2002_linked_candidate_descriptive_che25_or_access_households"),
        "alb2002_linked_candidate_descriptive_both_che10_access_households": metric_value(alb2002_linked_candidate_descriptive_summary, "alb2002_linked_candidate_descriptive_both_che10_access_households"),
        "alb2002_linked_candidate_descriptive_coping_households": metric_value(alb2002_linked_candidate_descriptive_summary, "alb2002_linked_candidate_descriptive_coping_households"),
        "alb2002_linked_candidate_descriptive_combined_stress_rows": metric_value(alb2002_linked_candidate_descriptive_summary, "alb2002_linked_candidate_descriptive_combined_stress_rows"),
        "alb2002_linked_candidate_descriptive_climate_linkage_ready_rows": metric_value(alb2002_linked_candidate_descriptive_summary, "alb2002_linked_candidate_descriptive_climate_linkage_ready_rows"),
        "alb2002_linked_candidate_descriptive_outcome_promotion_ready_rows": metric_value(alb2002_linked_candidate_descriptive_summary, "alb2002_linked_candidate_descriptive_outcome_promotion_ready_rows"),
        "alb2002_linked_candidate_descriptive_harmonized_recipe_ready_rows": metric_value(alb2002_linked_candidate_descriptive_summary, "alb2002_linked_candidate_descriptive_harmonized_recipe_ready_rows"),
        "alb2002_linked_candidate_descriptive_data_write_ready_rows": metric_value(alb2002_linked_candidate_descriptive_summary, "alb2002_linked_candidate_descriptive_data_write_ready_rows"),
        "alb2002_linked_candidate_descriptive_current_decision": metric_value(alb2002_linked_candidate_descriptive_summary, "alb2002_linked_candidate_descriptive_current_decision", "missing"),
        "alb2002_minimum_recipe_promotion_action_rows": metric_value(alb2002_minimum_recipe_summary, "alb2002_minimum_recipe_promotion_action_rows"),
        "alb2002_minimum_recipe_promotion_gate_rows": metric_value(alb2002_minimum_recipe_summary, "alb2002_minimum_recipe_promotion_gate_rows"),
        "alb2002_minimum_recipe_promotion_blocked_gates": metric_value(alb2002_minimum_recipe_summary, "alb2002_minimum_recipe_promotion_blocked_gates"),
        "alb2002_minimum_recipe_promotion_candidate_gates": metric_value(alb2002_minimum_recipe_summary, "alb2002_minimum_recipe_promotion_candidate_gates"),
        "alb2002_minimum_recipe_promotion_harmonized_ready_rows": metric_value(alb2002_minimum_recipe_summary, "alb2002_minimum_recipe_promotion_harmonized_ready_rows"),
        "alb2002_minimum_recipe_promotion_outcome_ready_rows": metric_value(alb2002_minimum_recipe_summary, "alb2002_minimum_recipe_promotion_outcome_ready_rows"),
        "alb2002_minimum_recipe_promotion_sdg382_ready_rows": metric_value(alb2002_minimum_recipe_summary, "alb2002_minimum_recipe_promotion_sdg382_ready_rows"),
        "alb2002_minimum_recipe_promotion_climate_linkage_ready_rows": metric_value(alb2002_minimum_recipe_summary, "alb2002_minimum_recipe_promotion_climate_linkage_ready_rows"),
        "alb2002_minimum_recipe_promotion_current_decision": metric_value(alb2002_minimum_recipe_summary, "alb2002_minimum_recipe_promotion_current_decision", "missing"),
        "alb2002_district_crosswalk_template_rows": len(alb2002_crosswalk_template),
        "alb2002_district_crosswalk_source_probe_rows": len(alb2002_boundary_probe),
        "alb2002_district_crosswalk_district_rows": metric_value(alb2002_crosswalk_summary, "alb2002_district_crosswalk_district_rows"),
        "alb2002_district_crosswalk_source_reachable_rows": metric_value(alb2002_crosswalk_summary, "alb2002_district_crosswalk_boundary_source_reachable_rows"),
        "alb2002_district_crosswalk_adm_unit_count": metric_value(alb2002_crosswalk_summary, "alb2002_district_crosswalk_boundary_source_adm_unit_count", "missing"),
        "alb2002_district_crosswalk_name_encoding_review_rows": metric_value(alb2002_crosswalk_summary, "alb2002_district_crosswalk_name_encoding_review_rows"),
        "alb2002_district_crosswalk_ready_rows": metric_value(alb2002_crosswalk_summary, "alb2002_district_crosswalk_template_ready_rows"),
        "alb2002_climate_linkage_ready_rows": metric_value(alb2002_crosswalk_summary, "alb2002_climate_linkage_ready_rows"),
        "alb2002_district_crosswalk_current_decision": metric_value(alb2002_crosswalk_summary, "alb2002_district_crosswalk_current_decision", "missing"),
        "alb2002_boundary_name_match_rows": len(alb2002_boundary_name_audit),
        "alb2002_boundary_geojson_feature_rows": len(alb2002_boundary_geojson_inventory),
        "alb2002_boundary_name_match_exact_rows": metric_value(alb2002_boundary_name_summary, "alb2002_boundary_name_match_exact_rows"),
        "alb2002_boundary_name_match_euro_repaired_rows": metric_value(alb2002_boundary_name_summary, "alb2002_boundary_name_match_euro_repaired_rows"),
        "alb2002_boundary_name_match_unmatched_survey_rows": metric_value(alb2002_boundary_name_summary, "alb2002_boundary_name_match_unmatched_survey_rows"),
        "alb2002_boundary_name_match_duplicate_boundary_name_keys": metric_value(alb2002_boundary_name_summary, "alb2002_boundary_name_match_duplicate_boundary_name_keys"),
        "alb2002_boundary_name_match_duplicate_boundary_feature_rows": metric_value(alb2002_boundary_name_summary, "alb2002_boundary_name_match_duplicate_boundary_feature_rows"),
        "alb2002_boundary_name_match_historical_year_ready_rows": metric_value(alb2002_boundary_name_summary, "alb2002_boundary_name_match_historical_year_ready_rows"),
        "alb2002_boundary_name_match_climate_linkage_ready_rows": metric_value(alb2002_boundary_name_summary, "alb2002_boundary_name_match_climate_linkage_ready_rows"),
        "alb2002_boundary_name_match_current_decision": metric_value(alb2002_boundary_name_summary, "alb2002_boundary_name_match_current_decision", "missing"),
        "alb2002_boundary_source_alternative_rows": metric_value(alb2002_boundary_source_summary, "alb2002_boundary_source_alternative_rows"),
        "alb2002_boundary_source_alternative_reachable_rows": metric_value(alb2002_boundary_source_summary, "alb2002_boundary_source_alternative_reachable_rows"),
        "alb2002_boundary_source_alternative_current_or_post2015_rows": metric_value(alb2002_boundary_source_summary, "alb2002_boundary_source_alternative_current_or_post2015_rows"),
        "alb2002_boundary_source_alternative_lsms_maps_documented_rows": metric_value(alb2002_boundary_source_summary, "alb2002_boundary_source_alternative_lsms_maps_documented_rows"),
        "alb2002_boundary_source_alternative_gps_documented_rows": metric_value(alb2002_boundary_source_summary, "alb2002_boundary_source_alternative_gps_documented_rows"),
        "alb2002_boundary_source_alternative_historical_candidate_rows": metric_value(alb2002_boundary_source_summary, "alb2002_boundary_source_alternative_historical_candidate_rows"),
        "alb2002_boundary_source_alternative_historical_ready_rows": metric_value(alb2002_boundary_source_summary, "alb2002_boundary_source_alternative_historical_2002_boundary_ready_rows"),
        "alb2002_boundary_source_alternative_climate_linkage_ready_rows": metric_value(alb2002_boundary_source_summary, "alb2002_boundary_source_alternative_climate_linkage_ready_rows"),
        "alb2002_boundary_source_alternative_current_decision": metric_value(alb2002_boundary_source_summary, "alb2002_boundary_source_alternative_current_decision", "missing"),
        "alb2002_boundary_resource_search_candidate_rows": metric_value(alb2002_boundary_resource_summary, "alb2002_boundary_resource_search_candidate_rows"),
        "alb2002_boundary_resource_search_parseable_resource_rows": metric_value(alb2002_boundary_resource_summary, "alb2002_boundary_resource_search_parseable_resource_rows"),
        "alb2002_boundary_resource_search_complete_name_coverage_rows": metric_value(alb2002_boundary_resource_summary, "alb2002_boundary_resource_search_complete_name_coverage_rows"),
        "alb2002_boundary_resource_search_exact_unit_count_rows": metric_value(alb2002_boundary_resource_summary, "alb2002_boundary_resource_search_exact_unit_count_rows"),
        "alb2002_boundary_resource_search_korce_available_rows": metric_value(alb2002_boundary_resource_summary, "alb2002_boundary_resource_search_korce_available_rows"),
        "alb2002_boundary_resource_search_2002_historical_ready_rows": metric_value(alb2002_boundary_resource_summary, "alb2002_boundary_resource_search_2002_historical_ready_rows"),
        "alb2002_boundary_resource_search_climate_linkage_ready_rows": metric_value(alb2002_boundary_resource_summary, "alb2002_boundary_resource_search_climate_linkage_ready_rows"),
        "alb2002_boundary_resource_search_best_candidate_id": metric_value(alb2002_boundary_resource_summary, "alb2002_boundary_resource_search_best_candidate_id", "missing"),
        "alb2002_boundary_resource_search_best_candidate_exact_matches": metric_value(alb2002_boundary_resource_summary, "alb2002_boundary_resource_search_best_candidate_exact_matches"),
        "alb2002_boundary_resource_search_best_candidate_repaired_matches": metric_value(alb2002_boundary_resource_summary, "alb2002_boundary_resource_search_best_candidate_repaired_matches"),
        "alb2002_boundary_resource_search_best_candidate_alias_matches": metric_value(alb2002_boundary_resource_summary, "alb2002_boundary_resource_search_best_candidate_alias_matches"),
        "alb2002_boundary_resource_search_current_decision": metric_value(alb2002_boundary_resource_summary, "alb2002_boundary_resource_search_current_decision", "missing"),
        "alb2002_boundary_geometry_feature_rows": metric_value(alb2002_boundary_geometry_summary, "alb2002_boundary_geometry_feature_rows"),
        "alb2002_boundary_geometry_adm2_feature_rows": metric_value(alb2002_boundary_geometry_summary, "alb2002_boundary_geometry_adm2_feature_rows"),
        "alb2002_boundary_geometry_multipolygon_rows": metric_value(alb2002_boundary_geometry_summary, "alb2002_boundary_geometry_multipolygon_rows"),
        "alb2002_boundary_geometry_coordinate_structure_ok_rows": metric_value(alb2002_boundary_geometry_summary, "alb2002_boundary_geometry_coordinate_structure_ok_rows"),
        "alb2002_boundary_geometry_survey_key_matched_rows": metric_value(alb2002_boundary_geometry_summary, "alb2002_boundary_geometry_survey_key_matched_rows"),
        "alb2002_boundary_geometry_closed_ring_failure_rows": metric_value(alb2002_boundary_geometry_summary, "alb2002_boundary_geometry_closed_ring_failure_rows"),
        "alb2002_boundary_geometry_out_of_range_coordinate_rows": metric_value(alb2002_boundary_geometry_summary, "alb2002_boundary_geometry_out_of_range_coordinate_rows"),
        "alb2002_boundary_geometry_within_broad_albania_bbox_rows": metric_value(alb2002_boundary_geometry_summary, "alb2002_boundary_geometry_within_broad_albania_bbox_rows"),
        "alb2002_boundary_geometry_metadata_boundary_year": metric_value(alb2002_boundary_geometry_summary, "alb2002_boundary_geometry_metadata_boundary_year", "missing"),
        "alb2002_boundary_geometry_metadata_boundary_update": metric_value(alb2002_boundary_geometry_summary, "alb2002_boundary_geometry_metadata_boundary_update", "missing"),
        "alb2002_boundary_geometry_metadata_boundary_source": metric_value(alb2002_boundary_geometry_summary, "alb2002_boundary_geometry_metadata_boundary_source", "missing"),
        "alb2002_boundary_geometry_boundary_year_matches_2002_rows": metric_value(alb2002_boundary_geometry_summary, "alb2002_boundary_geometry_boundary_year_matches_2002_rows"),
        "alb2002_boundary_geometry_topology_validated_rows": metric_value(alb2002_boundary_geometry_summary, "alb2002_boundary_geometry_topology_validated_rows"),
        "alb2002_boundary_geometry_historical_2002_boundary_ready_rows": metric_value(alb2002_boundary_geometry_summary, "alb2002_boundary_geometry_historical_2002_boundary_ready_rows"),
        "alb2002_boundary_geometry_climate_linkage_ready_rows": metric_value(alb2002_boundary_geometry_summary, "alb2002_boundary_geometry_climate_linkage_ready_rows"),
        "alb2002_boundary_geometry_current_decision": metric_value(alb2002_boundary_geometry_summary, "alb2002_boundary_geometry_current_decision", "missing"),
        "alb2002_boundary_manual_verification_action_rows": metric_value(alb2002_boundary_manual_summary, "alb2002_boundary_manual_verification_action_rows"),
        "alb2002_boundary_manual_verification_gate_rows": metric_value(alb2002_boundary_manual_summary, "alb2002_boundary_manual_verification_gate_rows"),
        "alb2002_boundary_manual_verification_candidate_evidence_gates": metric_value(alb2002_boundary_manual_summary, "alb2002_boundary_manual_verification_candidate_evidence_gates"),
        "alb2002_boundary_manual_verification_blocked_gates": metric_value(alb2002_boundary_manual_summary, "alb2002_boundary_manual_verification_blocked_gates"),
        "alb2002_boundary_manual_verification_high_priority_actions": metric_value(alb2002_boundary_manual_summary, "alb2002_boundary_manual_verification_high_priority_actions"),
        "alb2002_boundary_manual_verification_pre2011_digital_map_absence_rows": metric_value(alb2002_boundary_manual_summary, "alb2002_boundary_manual_verification_pre2011_digital_map_absence_rows"),
        "alb2002_boundary_manual_verification_climate_linkage_ready_rows": metric_value(alb2002_boundary_manual_summary, "alb2002_boundary_manual_verification_climate_linkage_ready_rows"),
        "alb2002_boundary_manual_verification_current_decision": metric_value(alb2002_boundary_manual_summary, "alb2002_boundary_manual_verification_current_decision", "missing"),
        "alb2002_boundary_manual_source_followup_rows": metric_value(alb2002_boundary_followup_summary, "alb2002_boundary_manual_source_followup_rows"),
        "alb2002_boundary_manual_source_followup_reachable_page_rows": metric_value(alb2002_boundary_followup_summary, "alb2002_boundary_manual_source_followup_reachable_page_rows"),
        "alb2002_boundary_manual_source_followup_conclusive_blocker_rows": metric_value(alb2002_boundary_followup_summary, "alb2002_boundary_manual_source_followup_conclusive_blocker_rows"),
        "alb2002_boundary_manual_source_followup_district_level_ready_rows": metric_value(alb2002_boundary_followup_summary, "alb2002_boundary_manual_source_followup_district_level_ready_rows"),
        "alb2002_boundary_manual_source_followup_climate_linkage_ready_rows": metric_value(alb2002_boundary_followup_summary, "alb2002_boundary_manual_source_followup_climate_linkage_ready_rows"),
        "alb2002_boundary_manual_source_followup_ipums_level_status": metric_value(alb2002_boundary_followup_summary, "alb2002_boundary_manual_source_followup_ipums_level_status", "missing"),
        "alb2002_boundary_manual_source_followup_unece_pre2011_map_status": metric_value(alb2002_boundary_followup_summary, "alb2002_boundary_manual_source_followup_unece_pre2011_map_status", "missing"),
        "alb2002_boundary_manual_source_followup_current_decision": metric_value(alb2002_boundary_followup_summary, "alb2002_boundary_manual_source_followup_current_decision", "missing"),
        "alb2002_gadm_boundary_lead_candidate_rows": metric_value(alb2002_gadm_summary, "alb2002_gadm_boundary_lead_candidate_rows"),
        "alb2002_gadm36_adm2_row_count": metric_value(alb2002_gadm_summary, "alb2002_gadm36_adm2_row_count"),
        "alb2002_gadm36_distinct_normalized_key_count": metric_value(alb2002_gadm_summary, "alb2002_gadm36_distinct_normalized_key_count"),
        "alb2002_gadm36_engtype_district_rows": metric_value(alb2002_gadm_summary, "alb2002_gadm36_engtype_district_rows"),
        "alb2002_gadm36_type_rreth_rows": metric_value(alb2002_gadm_summary, "alb2002_gadm36_type_rreth_rows"),
        "alb2002_gadm36_complete_name_coverage_rows": metric_value(alb2002_gadm_summary, "alb2002_gadm36_complete_name_coverage_rows"),
        "alb2002_gadm36_duplicate_boundary_key_count": metric_value(alb2002_gadm_summary, "alb2002_gadm36_duplicate_boundary_key_count"),
        "alb2002_gadm36_duplicate_boundary_feature_rows": metric_value(alb2002_gadm_summary, "alb2002_gadm36_duplicate_boundary_feature_rows"),
        "alb2002_gadm_boundary_lead_historical_2002_ready_rows": metric_value(alb2002_gadm_summary, "alb2002_gadm_boundary_lead_historical_2002_ready_rows"),
        "alb2002_gadm_boundary_lead_climate_linkage_ready_rows": metric_value(alb2002_gadm_summary, "alb2002_gadm_boundary_lead_climate_linkage_ready_rows"),
        "alb2002_gadm_boundary_lead_current_decision": metric_value(alb2002_gadm_summary, "alb2002_gadm_boundary_lead_current_decision", "missing"),
        "alb2002_local_geo_artifact_files_scanned": metric_value(alb2002_local_geo_artifact_summary, "alb2002_local_geo_artifact_files_scanned"),
        "alb2002_local_geo_artifact_gis_file_candidate_rows": metric_value(alb2002_local_geo_artifact_summary, "alb2002_local_geo_artifact_gis_file_candidate_rows"),
        "alb2002_local_geo_artifact_coordinate_raw_variable_rows": metric_value(alb2002_local_geo_artifact_summary, "alb2002_local_geo_artifact_coordinate_raw_variable_rows"),
        "alb2002_local_geo_artifact_questionnaire_coordinate_field_rows": metric_value(alb2002_local_geo_artifact_summary, "alb2002_local_geo_artifact_questionnaire_coordinate_field_rows"),
        "alb2002_local_geo_artifact_admin_variable_rows": metric_value(alb2002_local_geo_artifact_summary, "alb2002_local_geo_artifact_admin_variable_rows"),
        "alb2002_local_geo_artifact_psu_ea_variable_rows": metric_value(alb2002_local_geo_artifact_summary, "alb2002_local_geo_artifact_psu_ea_variable_rows"),
        "alb2002_local_geo_artifact_district_commune_variable_rows": metric_value(alb2002_local_geo_artifact_summary, "alb2002_local_geo_artifact_district_commune_variable_rows"),
        "alb2002_local_geo_artifact_official_gps_documented_rows": metric_value(alb2002_local_geo_artifact_summary, "alb2002_local_geo_artifact_official_gps_documented_rows"),
        "alb2002_local_geo_artifact_official_ea_map_documented_rows": metric_value(alb2002_local_geo_artifact_summary, "alb2002_local_geo_artifact_official_ea_map_documented_rows"),
        "alb2002_local_geo_artifact_local_coordinate_ready_rows": metric_value(alb2002_local_geo_artifact_summary, "alb2002_local_geo_artifact_local_coordinate_ready_rows"),
        "alb2002_local_geo_artifact_local_boundary_ready_rows": metric_value(alb2002_local_geo_artifact_summary, "alb2002_local_geo_artifact_local_boundary_ready_rows"),
        "alb2002_local_geo_artifact_climate_linkage_ready_rows": metric_value(alb2002_local_geo_artifact_summary, "alb2002_local_geo_artifact_climate_linkage_ready_rows"),
        "alb2002_local_geo_artifact_current_decision": metric_value(alb2002_local_geo_artifact_summary, "alb2002_local_geo_artifact_current_decision", "missing"),
        "alb2012_household_core_candidate_rows": metric_value(alb2012_summary, "alb2012_household_core_candidate_rows"),
        "alb2012_households_with_total_consumption": metric_value(alb2012_summary, "alb2012_households_with_total_consumption"),
        "alb2012_households_with_household_weight": metric_value(alb2012_summary, "alb2012_households_with_household_weight"),
        "alb2012_households_with_prefecture": metric_value(alb2012_summary, "alb2012_households_with_prefecture"),
        "alb2012_households_with_region": metric_value(alb2012_summary, "alb2012_households_with_region"),
        "alb2012_households_with_survey_month": metric_value(alb2012_summary, "alb2012_households_with_survey_month"),
        "alb2012_households_with_interview_date": metric_value(alb2012_summary, "alb2012_households_with_interview_date"),
        "alb2012_households_with_oop_4w_positive": metric_value(alb2012_summary, "alb2012_households_with_oop_4w_positive"),
        "alb2012_households_with_oop_12m_positive": metric_value(alb2012_summary, "alb2012_households_with_oop_12m_positive"),
        "alb2012_households_with_access_affordability_proxy": metric_value(alb2012_summary, "alb2012_households_with_access_affordability_proxy"),
        "alb2012_households_with_shock_any_2008_2012": metric_value(alb2012_summary, "alb2012_households_with_shock_any_2008_2012"),
        "alb2012_household_core_recipe_ready_rows": metric_value(alb2012_summary, "alb2012_household_core_recipe_ready_rows"),
        "alb2012_climate_linkage_ready_rows": metric_value(alb2012_summary, "alb2012_climate_linkage_ready_rows"),
        "alb2012_timing_signal_rows": metric_value(alb2012_summary, "alb2012_timing_signal_rows"),
        "alb2012_coordinate_signal_rows": metric_value(alb2012_summary, "alb2012_coordinate_signal_rows"),
        "alb2012_raw_core_current_decision": metric_value(alb2012_summary, "alb2012_raw_core_current_decision", "missing"),
        "alb2012_provisional_outcome_audit_rows": len(alb2012_outcome_audit),
        "alb2012_provisional_financial_stress_test_rows": metric_value(alb2012_outcome_summary, "alb2012_provisional_financial_stress_test_rows"),
        "alb2012_provisional_access_proxy_rows": metric_value(alb2012_outcome_summary, "alb2012_provisional_access_proxy_rows"),
        "alb2012_provisional_need_proxy_rows": metric_value(alb2012_outcome_summary, "alb2012_provisional_need_proxy_rows"),
        "alb2012_provisional_low_event_rate_rows": metric_value(alb2012_outcome_summary, "alb2012_provisional_low_event_rate_rows"),
        "alb2012_provisional_outcome_ready_rows": metric_value(alb2012_outcome_summary, "alb2012_provisional_outcome_ready_rows"),
        "alb2012_provisional_climate_linkage_ready_rows": metric_value(alb2012_outcome_summary, "alb2012_provisional_climate_linkage_ready_rows"),
        "alb2012_provisional_outcome_current_decision": metric_value(alb2012_outcome_summary, "alb2012_provisional_outcome_current_decision", "missing"),
        "alb2012_outcome_semantics_raw_value_rows": len(alb2012_semantics_audit),
        "alb2012_outcome_semantics_source_files_scanned": metric_value(alb2012_semantics_summary, "alb2012_outcome_semantics_source_files_scanned"),
        "alb2012_outcome_semantics_financial_oop_candidate_rows": metric_value(alb2012_semantics_summary, "alb2012_outcome_semantics_financial_oop_candidate_rows"),
        "alb2012_outcome_semantics_gift_candidate_rows": metric_value(alb2012_semantics_summary, "alb2012_outcome_semantics_gift_candidate_rows"),
        "alb2012_outcome_semantics_access_candidate_rows": metric_value(alb2012_semantics_summary, "alb2012_outcome_semantics_access_candidate_rows"),
        "alb2012_outcome_semantics_service_quality_proxy_rows": metric_value(alb2012_semantics_summary, "alb2012_outcome_semantics_service_quality_proxy_rows"),
        "alb2012_outcome_semantics_need_candidate_rows": metric_value(alb2012_semantics_summary, "alb2012_outcome_semantics_need_candidate_rows"),
        "alb2012_outcome_semantics_coping_candidate_rows": metric_value(alb2012_semantics_summary, "alb2012_outcome_semantics_coping_candidate_rows"),
        "alb2012_outcome_semantics_rows_with_value_labels": metric_value(alb2012_semantics_summary, "alb2012_outcome_semantics_rows_with_value_labels"),
        "alb2012_outcome_semantics_conditional_reason_rows": metric_value(alb2012_semantics_summary, "alb2012_outcome_semantics_conditional_reason_rows"),
        "alb2012_outcome_semantics_outcome_ready_rows": metric_value(alb2012_semantics_summary, "alb2012_outcome_semantics_outcome_ready_rows"),
        "alb2012_outcome_semantics_sdg382_ready_rows": metric_value(alb2012_semantics_summary, "alb2012_outcome_semantics_sdg382_ready_rows"),
        "alb2012_outcome_semantics_climate_linkage_ready_rows": metric_value(alb2012_semantics_summary, "alb2012_outcome_semantics_climate_linkage_ready_rows"),
        "alb2012_outcome_semantics_current_decision": metric_value(alb2012_semantics_summary, "alb2012_outcome_semantics_current_decision", "missing"),
        "alb2012_timing_geography_audit_rows": len(alb2012_timing_geo_audit),
        "alb2012_timing_geography_source_files_scanned": metric_value(alb2012_timing_geo_summary, "alb2012_timing_geography_source_files_scanned"),
        "alb2012_interview_timing_candidate_rows": metric_value(alb2012_timing_geo_summary, "alb2012_interview_timing_candidate_rows"),
        "alb2012_interview_timing_verified_rows": metric_value(alb2012_timing_geo_summary, "alb2012_interview_timing_verified_rows"),
        "alb2012_coordinate_candidate_rows": metric_value(alb2012_timing_geo_summary, "alb2012_coordinate_candidate_rows"),
        "alb2012_coarse_full_coverage_geography_candidate_rows": metric_value(alb2012_timing_geo_summary, "alb2012_coarse_full_coverage_geography_candidate_rows"),
        "alb2012_coarse_geography_household_rows": metric_value(alb2012_timing_geo_summary, "alb2012_coarse_geography_household_rows"),
        "alb2012_timing_geography_climate_linkage_ready_rows": metric_value(alb2012_timing_geo_summary, "alb2012_climate_linkage_ready_rows"),
        "alb2012_timing_geography_current_decision": metric_value(alb2012_timing_geo_summary, "alb2012_timing_geography_current_decision", "missing"),
        "alb2012_questionnaire_timing_field_rows": metric_value(alb2012_questionnaire_timing_summary, "alb2012_questionnaire_timing_field_rows"),
        "alb2012_questionnaire_timing_visit_rows": metric_value(alb2012_questionnaire_timing_summary, "alb2012_questionnaire_timing_visit_rows"),
        "alb2012_questionnaire_timing_date_begin_end_status_rows": metric_value(alb2012_questionnaire_timing_summary, "alb2012_questionnaire_timing_date_begin_end_status_rows"),
        "alb2012_questionnaire_timing_raw_gap_rows": metric_value(alb2012_questionnaire_timing_summary, "alb2012_questionnaire_timing_raw_gap_rows"),
        "alb2012_questionnaire_timing_raw_control_candidate_rows": metric_value(alb2012_questionnaire_timing_summary, "alb2012_questionnaire_timing_raw_control_candidate_rows"),
        "alb2012_questionnaire_timing_raw_verified_interview_timing_rows": metric_value(alb2012_questionnaire_timing_summary, "alb2012_questionnaire_timing_raw_verified_interview_timing_rows"),
        "alb2012_questionnaire_timing_climate_linkage_ready_rows": metric_value(alb2012_questionnaire_timing_summary, "alb2012_questionnaire_timing_climate_linkage_ready_rows"),
        "alb2012_questionnaire_timing_current_decision": metric_value(alb2012_questionnaire_timing_summary, "alb2012_questionnaire_timing_current_decision", "missing"),
        "alb2012_timing_geography_blocker_resolution_rows": metric_value(alb2012_blocker_summary, "alb2012_timing_geography_blocker_resolution_rows"),
        "alb2012_timing_geography_blocker_timing_rows": metric_value(alb2012_blocker_summary, "alb2012_timing_geography_blocker_timing_rows"),
        "alb2012_timing_geography_blocker_geography_rows": metric_value(alb2012_blocker_summary, "alb2012_timing_geography_blocker_geography_rows"),
        "alb2012_timing_geography_blocker_outcome_rows": metric_value(alb2012_blocker_summary, "alb2012_timing_geography_blocker_outcome_rows"),
        "alb2012_timing_geography_blocker_promotion_gate_rows": metric_value(alb2012_blocker_summary, "alb2012_timing_geography_blocker_promotion_gate_rows"),
        "alb2012_timing_geography_blocker_hard_blocked_rows": metric_value(alb2012_blocker_summary, "alb2012_timing_geography_blocker_hard_blocked_rows"),
        "alb2012_timing_geography_blocker_interview_timing_ready_rows": metric_value(alb2012_blocker_summary, "alb2012_timing_geography_blocker_interview_timing_ready_rows"),
        "alb2012_timing_geography_blocker_geography_ready_rows": metric_value(alb2012_blocker_summary, "alb2012_timing_geography_blocker_geography_ready_rows"),
        "alb2012_timing_geography_blocker_outcome_ready_rows": metric_value(alb2012_blocker_summary, "alb2012_timing_geography_blocker_outcome_ready_rows"),
        "alb2012_timing_geography_blocker_climate_linkage_ready_rows": metric_value(alb2012_blocker_summary, "alb2012_timing_geography_blocker_climate_linkage_ready_rows"),
        "alb2012_timing_geography_blocker_data_write_ready_rows": metric_value(alb2012_blocker_summary, "alb2012_timing_geography_blocker_data_write_ready_rows"),
        "alb2012_timing_geography_blocker_current_decision": metric_value(alb2012_blocker_summary, "alb2012_timing_geography_blocker_current_decision", "missing"),
        "albania_legacy_questionnaire_present_files": metric_value(albania_legacy_questionnaire_summary, "albania_legacy_questionnaire_present_files"),
        "albania_legacy_questionnaire_ole_signature_files": metric_value(albania_legacy_questionnaire_summary, "albania_legacy_questionnaire_ole_signature_files"),
        "albania_legacy_questionnaire_xlrd_installed": metric_value(albania_legacy_questionnaire_summary, "albania_legacy_questionnaire_xlrd_installed"),
        "albania_legacy_questionnaire_soffice_available": metric_value(albania_legacy_questionnaire_summary, "albania_legacy_questionnaire_soffice_available"),
        "albania_legacy_questionnaire_read_ok_files": metric_value(albania_legacy_questionnaire_summary, "albania_legacy_questionnaire_read_ok_files"),
        "albania_legacy_questionnaire_read_failed_files": metric_value(albania_legacy_questionnaire_summary, "albania_legacy_questionnaire_read_failed_files"),
        "albania_legacy_questionnaire_missing_reader_blocked_files": metric_value(albania_legacy_questionnaire_summary, "albania_legacy_questionnaire_missing_reader_blocked_files"),
        "albania_legacy_questionnaire_timing_content_audit_ready_rows": metric_value(albania_legacy_questionnaire_summary, "albania_legacy_questionnaire_timing_content_audit_ready_rows"),
        "albania_legacy_questionnaire_climate_linkage_ready_rows": metric_value(albania_legacy_questionnaire_summary, "albania_legacy_questionnaire_climate_linkage_ready_rows"),
        "albania_legacy_questionnaire_current_decision": metric_value(albania_legacy_questionnaire_summary, "albania_legacy_questionnaire_current_decision", "missing"),
        "albania_legacy_questionnaire_timing_field_rows": metric_value(albania_legacy_questionnaire_timing_summary, "albania_legacy_questionnaire_timing_field_rows"),
        "albania_legacy_questionnaire_timing_visit_rows": metric_value(albania_legacy_questionnaire_timing_summary, "albania_legacy_questionnaire_timing_visit_rows"),
        "albania_legacy_questionnaire_timing_date_begin_end_status_rows": metric_value(albania_legacy_questionnaire_timing_summary, "albania_legacy_questionnaire_timing_date_begin_end_status_rows"),
        "albania_legacy_questionnaire_timing_raw_gap_rows": metric_value(albania_legacy_questionnaire_timing_summary, "albania_legacy_questionnaire_timing_raw_gap_rows"),
        "albania_legacy_questionnaire_timing_raw_verified_interview_timing_rows": metric_value(albania_legacy_questionnaire_timing_summary, "albania_legacy_questionnaire_timing_raw_verified_interview_timing_rows"),
        "alb2002_legacy_questionnaire_timing_raw_verified_interview_timing_rows": metric_value(albania_legacy_questionnaire_timing_summary, "alb2002_legacy_questionnaire_timing_raw_verified_interview_timing_rows"),
        "alb2005_legacy_questionnaire_timing_raw_verified_interview_timing_rows": metric_value(albania_legacy_questionnaire_timing_summary, "alb2005_legacy_questionnaire_timing_raw_verified_interview_timing_rows"),
        "alb2008_legacy_questionnaire_timing_raw_verified_interview_timing_rows": metric_value(albania_legacy_questionnaire_timing_summary, "alb2008_legacy_questionnaire_timing_raw_verified_interview_timing_rows"),
        "albania_legacy_questionnaire_timing_climate_linkage_ready_rows": metric_value(albania_legacy_questionnaire_timing_summary, "albania_legacy_questionnaire_timing_climate_linkage_ready_rows"),
        "albania_legacy_questionnaire_timing_current_decision": metric_value(albania_legacy_questionnaire_timing_summary, "albania_legacy_questionnaire_timing_current_decision", "missing"),
        "alb2005_documented_evidence_rows": len(alb2005_documented_evidence),
        "alb2005_documented_summary_rows": len(alb2005_documented_summary),
        "alb2005_future_recipe_candidate_rows": metric_value(alb2005_documented_summary, "alb2005_future_recipe_candidate_rows"),
        "alb2005_false_positive_rows": metric_value(alb2005_documented_summary, "alb2005_false_positive_rows"),
        "alb2005_timing_or_geography_blocker_rows": metric_value(alb2005_documented_summary, "alb2005_timing_or_geography_blocker_rows"),
        "alb2005_recipe_ready_rows": metric_value(alb2005_documented_summary, "alb2005_recipe_ready_rows"),
        "alb2005_household_core_candidate_rows": metric_value(alb2005_core_summary, "alb2005_household_core_candidate_rows"),
        "alb2005_households_with_total_consumption": metric_value(alb2005_core_summary, "alb2005_households_with_total_consumption"),
        "alb2005_households_with_household_weight": metric_value(alb2005_core_summary, "alb2005_households_with_household_weight"),
        "alb2005_households_with_oop_4w_positive": metric_value(alb2005_core_summary, "alb2005_households_with_oop_4w_positive"),
        "alb2005_households_with_partial_district_code": metric_value(alb2005_core_summary, "alb2005_households_with_partial_district_code"),
        "alb2005_households_with_survey_month": metric_value(alb2005_core_summary, "alb2005_households_with_survey_month"),
        "alb2005_household_core_recipe_ready_rows": metric_value(alb2005_core_summary, "alb2005_household_core_recipe_ready_rows"),
        "alb2005_provisional_outcome_audit_rows": len(alb2005_outcome_audit),
        "alb2005_provisional_financial_stress_test_rows": metric_value(alb2005_outcome_summary, "alb2005_provisional_financial_stress_test_rows"),
        "alb2005_provisional_access_proxy_rows": metric_value(alb2005_outcome_summary, "alb2005_provisional_access_proxy_rows"),
        "alb2005_provisional_low_event_rate_rows": metric_value(alb2005_outcome_summary, "alb2005_provisional_low_event_rate_rows"),
        "alb2005_provisional_outcome_ready_rows": metric_value(alb2005_outcome_summary, "alb2005_provisional_outcome_ready_rows"),
        "alb2005_provisional_outcome_current_decision": metric_value(alb2005_outcome_summary, "alb2005_provisional_outcome_current_decision", "missing"),
        "alb2005_outcome_semantics_raw_value_rows": len(alb2005_semantics_audit),
        "alb2005_outcome_semantics_source_files_scanned": metric_value(alb2005_semantics_summary, "alb2005_outcome_semantics_source_files_scanned"),
        "alb2005_outcome_semantics_financial_oop_candidate_rows": metric_value(alb2005_semantics_summary, "alb2005_outcome_semantics_financial_oop_candidate_rows"),
        "alb2005_outcome_semantics_gift_candidate_rows": metric_value(alb2005_semantics_summary, "alb2005_outcome_semantics_gift_candidate_rows"),
        "alb2005_outcome_semantics_access_candidate_rows": metric_value(alb2005_semantics_summary, "alb2005_outcome_semantics_access_candidate_rows"),
        "alb2005_outcome_semantics_need_candidate_rows": metric_value(alb2005_semantics_summary, "alb2005_outcome_semantics_need_candidate_rows"),
        "alb2005_outcome_semantics_coping_candidate_rows": metric_value(alb2005_semantics_summary, "alb2005_outcome_semantics_coping_candidate_rows"),
        "alb2005_outcome_semantics_rows_with_value_labels": metric_value(alb2005_semantics_summary, "alb2005_outcome_semantics_rows_with_value_labels"),
        "alb2005_outcome_semantics_conditional_reason_rows": metric_value(alb2005_semantics_summary, "alb2005_outcome_semantics_conditional_reason_rows"),
        "alb2005_outcome_semantics_outcome_ready_rows": metric_value(alb2005_semantics_summary, "alb2005_outcome_semantics_outcome_ready_rows"),
        "alb2005_outcome_semantics_sdg382_ready_rows": metric_value(alb2005_semantics_summary, "alb2005_outcome_semantics_sdg382_ready_rows"),
        "alb2005_outcome_semantics_climate_linkage_ready_rows": metric_value(alb2005_semantics_summary, "alb2005_outcome_semantics_climate_linkage_ready_rows"),
        "alb2005_outcome_semantics_current_decision": metric_value(alb2005_semantics_summary, "alb2005_outcome_semantics_current_decision", "missing"),
        "alb2005_timing_geography_audit_rows": len(alb2005_timing_geo_audit),
        "alb2005_timing_geography_source_files_scanned": metric_value(alb2005_timing_geo_summary, "alb2005_timing_geography_source_files_scanned"),
        "alb2005_interview_timing_verified_rows": metric_value(alb2005_timing_geo_summary, "alb2005_interview_timing_verified_rows"),
        "alb2005_coordinate_candidate_rows": metric_value(alb2005_timing_geo_summary, "alb2005_coordinate_candidate_rows"),
        "alb2005_partial_current_district_candidate_rows": metric_value(alb2005_timing_geo_summary, "alb2005_partial_current_district_candidate_rows"),
        "alb2005_partial_district_name_nonmissing_rows": metric_value(alb2005_timing_geo_summary, "alb2005_partial_district_name_nonmissing_rows"),
        "alb2005_partial_district_code_nonmissing_rows": metric_value(alb2005_timing_geo_summary, "alb2005_partial_district_code_nonmissing_rows"),
        "alb2005_climate_linkage_ready_rows": metric_value(alb2005_timing_geo_summary, "alb2005_climate_linkage_ready_rows"),
        "alb2005_timing_geography_current_decision": metric_value(alb2005_timing_geo_summary, "alb2005_timing_geography_current_decision", "missing"),
        "alb2005_timing_geography_source_search_rows": metric_value(alb2005_timing_geo_source_summary, "alb2005_timing_geography_source_search_rows"),
        "alb2005_timing_geography_source_search_target_concepts": metric_value(alb2005_timing_geo_source_summary, "alb2005_timing_geography_source_search_target_concepts"),
        "alb2005_timing_geography_source_search_local_files_scanned": metric_value(alb2005_timing_geo_source_summary, "alb2005_timing_geography_source_search_local_files_scanned"),
        "alb2005_timing_geography_source_search_local_variables_scanned": metric_value(alb2005_timing_geo_source_summary, "alb2005_timing_geography_source_search_local_variables_scanned"),
        "alb2005_timing_geography_source_search_questionnaire_workbooks_scanned": metric_value(alb2005_timing_geo_source_summary, "alb2005_timing_geography_source_search_questionnaire_workbooks_scanned"),
        "alb2005_timing_geography_source_search_raw_targets_with_hits": metric_value(alb2005_timing_geo_source_summary, "alb2005_timing_geography_source_search_raw_targets_with_hits"),
        "alb2005_timing_geography_source_search_questionnaire_targets_with_hits": metric_value(alb2005_timing_geo_source_summary, "alb2005_timing_geography_source_search_questionnaire_targets_with_hits"),
        "alb2005_timing_geography_source_search_legacy_questionnaire_timing_rows": metric_value(alb2005_timing_geo_source_summary, "alb2005_timing_geography_source_search_legacy_questionnaire_timing_rows"),
        "alb2005_timing_geography_source_search_verified_household_timing_rows": metric_value(alb2005_timing_geo_source_summary, "alb2005_timing_geography_source_search_verified_household_timing_rows"),
        "alb2005_timing_geography_source_search_coordinate_candidate_rows": metric_value(alb2005_timing_geo_source_summary, "alb2005_timing_geography_source_search_coordinate_candidate_rows"),
        "alb2005_timing_geography_source_search_partial_district_variable_rows": metric_value(alb2005_timing_geo_source_summary, "alb2005_timing_geography_source_search_partial_district_variable_rows"),
        "alb2005_timing_geography_source_search_partial_district_name_nonmissing_rows": metric_value(alb2005_timing_geo_source_summary, "alb2005_timing_geography_source_search_partial_district_name_nonmissing_rows"),
        "alb2005_timing_geography_source_search_partial_district_code_nonmissing_rows": metric_value(alb2005_timing_geo_source_summary, "alb2005_timing_geography_source_search_partial_district_code_nonmissing_rows"),
        "alb2005_timing_geography_source_search_required_value_key_timing_rows": metric_value(alb2005_timing_geo_source_summary, "alb2005_timing_geography_source_search_required_value_key_timing_rows"),
        "alb2005_timing_geography_source_search_required_value_key_coordinate_rows": metric_value(alb2005_timing_geo_source_summary, "alb2005_timing_geography_source_search_required_value_key_coordinate_rows"),
        "alb2005_timing_geography_source_search_geography_crosswalk_ready_rows": metric_value(alb2005_timing_geo_source_summary, "alb2005_timing_geography_source_search_geography_crosswalk_ready_rows"),
        "alb2005_timing_geography_source_search_interview_timing_ready_rows": metric_value(alb2005_timing_geo_source_summary, "alb2005_timing_geography_source_search_interview_timing_ready_rows"),
        "alb2005_timing_geography_source_search_climate_linkage_ready_rows": metric_value(alb2005_timing_geo_source_summary, "alb2005_timing_geography_source_search_climate_linkage_ready_rows"),
        "alb2005_timing_geography_source_search_current_decision": metric_value(alb2005_timing_geo_source_summary, "alb2005_timing_geography_source_search_current_decision", "missing"),
        "alb2005_harmonization_value_decision_rows": metric_value(alb2005_value_decision_summary, "alb2005_harmonization_value_decision_rows"),
        "alb2005_harmonization_value_decision_required_rows": metric_value(alb2005_value_decision_summary, "alb2005_harmonization_value_decision_required_rows"),
        "alb2005_harmonization_value_decision_required_blocked_rows": metric_value(alb2005_value_decision_summary, "alb2005_harmonization_value_decision_required_blocked_rows"),
        "alb2005_harmonization_value_decision_recipe_ready_rows": metric_value(alb2005_value_decision_summary, "alb2005_harmonization_value_decision_recipe_ready_rows"),
        "alb2005_harmonization_value_decision_manual_future_candidate_rows": metric_value(alb2005_value_decision_summary, "alb2005_harmonization_value_decision_manual_future_candidate_rows"),
        "alb2005_harmonization_value_decision_false_positive_rows": metric_value(alb2005_value_decision_summary, "alb2005_harmonization_value_decision_false_positive_rows"),
        "alb2005_harmonization_value_decision_timing_geography_hard_blocker_rows": metric_value(alb2005_value_decision_summary, "alb2005_harmonization_value_decision_timing_geography_hard_blocker_rows"),
        "alb2005_harmonization_value_decision_current_decision": metric_value(alb2005_value_decision_summary, "alb2005_harmonization_value_decision_current_decision", "missing"),
        "alb2005_required_value_key_rows": metric_value(alb2005_required_value_key_summary, "alb2005_required_value_key_audit_rows"),
        "alb2005_required_value_key_recipe_ready_rows": metric_value(alb2005_required_value_key_summary, "alb2005_required_value_key_recipe_ready_rows"),
        "alb2005_required_value_key_not_promoted_rows": metric_value(alb2005_required_value_key_summary, "alb2005_required_value_key_not_promoted_rows"),
        "alb2005_required_value_key_total_consumption_nonmissing_rows": metric_value(alb2005_required_value_key_summary, "alb2005_required_value_key_total_consumption_nonmissing_rows"),
        "alb2005_required_value_key_oop_4w_household_positive_rows": metric_value(alb2005_required_value_key_summary, "alb2005_required_value_key_oop_4w_household_positive_rows"),
        "alb2005_required_value_key_oop_12m_household_positive_rows": metric_value(alb2005_required_value_key_summary, "alb2005_required_value_key_oop_12m_household_positive_rows"),
        "alb2005_required_value_key_district_code_nonmissing_rows": metric_value(alb2005_required_value_key_summary, "alb2005_required_value_key_district_code_nonmissing_rows"),
        "alb2005_required_value_key_interview_timing_verified_rows": metric_value(alb2005_required_value_key_summary, "alb2005_required_value_key_interview_timing_verified_rows"),
        "alb2005_required_value_key_coordinate_ready_rows": metric_value(alb2005_required_value_key_summary, "alb2005_required_value_key_coordinate_ready_rows"),
        "alb2005_required_value_key_climate_linkage_ready_rows": metric_value(alb2005_required_value_key_summary, "alb2005_required_value_key_climate_linkage_ready_rows"),
        "alb2005_required_value_key_current_decision": metric_value(alb2005_required_value_key_summary, "alb2005_required_value_key_current_decision", "missing"),
        "alb2005_health_questionnaire_semantics_rows": metric_value(alb2005_health_questionnaire_summary, "alb2005_health_questionnaire_semantics_rows"),
        "alb2005_health_questionnaire_oop_item_rows": metric_value(alb2005_health_questionnaire_summary, "alb2005_health_questionnaire_oop_item_rows"),
        "alb2005_health_questionnaire_visit_selection_rows": metric_value(alb2005_health_questionnaire_summary, "alb2005_health_questionnaire_visit_selection_rows"),
        "alb2005_health_questionnaire_access_rows": metric_value(alb2005_health_questionnaire_summary, "alb2005_health_questionnaire_access_rows"),
        "alb2005_health_questionnaire_four_week_oop_rows": metric_value(alb2005_health_questionnaire_summary, "alb2005_health_questionnaire_four_week_oop_rows"),
        "alb2005_health_questionnaire_twelve_month_oop_rows": metric_value(alb2005_health_questionnaire_summary, "alb2005_health_questionnaire_twelve_month_oop_rows"),
        "alb2005_health_questionnaire_old_lek_unit_rows": metric_value(alb2005_health_questionnaire_summary, "alb2005_health_questionnaire_old_lek_unit_rows"),
        "alb2005_health_questionnaire_exclusion_note_rows": metric_value(alb2005_health_questionnaire_summary, "alb2005_health_questionnaire_exclusion_note_rows"),
        "alb2005_health_questionnaire_zero_instruction_rows": metric_value(alb2005_health_questionnaire_summary, "alb2005_health_questionnaire_zero_instruction_rows"),
        "alb2005_health_questionnaire_cost_barrier_rows": metric_value(alb2005_health_questionnaire_summary, "alb2005_health_questionnaire_cost_barrier_rows"),
        "alb2005_health_questionnaire_distance_barrier_rows": metric_value(alb2005_health_questionnaire_summary, "alb2005_health_questionnaire_distance_barrier_rows"),
        "alb2005_health_questionnaire_supply_barrier_rows": metric_value(alb2005_health_questionnaire_summary, "alb2005_health_questionnaire_supply_barrier_rows"),
        "alb2005_health_questionnaire_recipe_ready_rows": metric_value(alb2005_health_questionnaire_summary, "alb2005_health_questionnaire_recipe_ready_rows"),
        "alb2005_health_questionnaire_outcome_ready_rows": metric_value(alb2005_health_questionnaire_summary, "alb2005_health_questionnaire_outcome_ready_rows"),
        "alb2005_health_questionnaire_climate_linkage_ready_rows": metric_value(alb2005_health_questionnaire_summary, "alb2005_health_questionnaire_climate_linkage_ready_rows"),
        "alb2005_health_questionnaire_current_decision": metric_value(alb2005_health_questionnaire_summary, "alb2005_health_questionnaire_current_decision", "missing"),
        "alb2005_oop_aggregation_policy_rows": metric_value(alb2005_oop_policy_summary, "alb2005_oop_aggregation_policy_rows"),
        "alb2005_oop_aggregation_policy_household_rows": metric_value(alb2005_oop_policy_summary, "alb2005_oop_aggregation_policy_household_rows"),
        "alb2005_oop_aggregation_policy_total_consumption_rows": metric_value(alb2005_oop_policy_summary, "alb2005_oop_aggregation_policy_total_consumption_rows"),
        "alb2005_oop_aggregation_policy_four_week_rows": metric_value(alb2005_oop_policy_summary, "alb2005_oop_aggregation_policy_four_week_policy_rows"),
        "alb2005_oop_aggregation_policy_twelve_month_rows": metric_value(alb2005_oop_policy_summary, "alb2005_oop_aggregation_policy_twelve_month_policy_rows"),
        "alb2005_oop_aggregation_policy_annual_stress_rows": metric_value(alb2005_oop_policy_summary, "alb2005_oop_aggregation_policy_annual_stress_rows"),
        "alb2005_oop_aggregation_policy_max_che10_rate": metric_value(alb2005_oop_policy_summary, "alb2005_oop_aggregation_policy_max_che10_rate"),
        "alb2005_oop_aggregation_policy_max_che25_rate": metric_value(alb2005_oop_policy_summary, "alb2005_oop_aggregation_policy_max_che25_rate"),
        "alb2005_oop_aggregation_policy_questionnaire_oop_rows": metric_value(alb2005_oop_policy_summary, "alb2005_oop_aggregation_policy_questionnaire_oop_item_rows_observed"),
        "alb2005_oop_aggregation_policy_questionnaire_old_lek_rows": metric_value(alb2005_oop_policy_summary, "alb2005_oop_aggregation_policy_questionnaire_old_lek_rows_observed"),
        "alb2005_oop_aggregation_policy_outcome_ready_rows": metric_value(alb2005_oop_policy_summary, "alb2005_oop_aggregation_policy_outcome_ready_rows"),
        "alb2005_oop_aggregation_policy_recipe_ready_rows": metric_value(alb2005_oop_policy_summary, "alb2005_oop_aggregation_policy_recipe_ready_rows"),
        "alb2005_oop_aggregation_policy_climate_linkage_ready_rows": metric_value(alb2005_oop_policy_summary, "alb2005_oop_aggregation_policy_climate_linkage_ready_rows"),
        "alb2005_oop_aggregation_policy_current_decision": metric_value(alb2005_oop_policy_summary, "alb2005_oop_aggregation_policy_current_decision", "missing"),
        "alb2005_skip_missing_semantics_rows": metric_value(alb2005_skip_missing_summary, "alb2005_skip_missing_semantics_rows"),
        "alb2005_skip_missing_payment_block_rows": metric_value(alb2005_skip_missing_summary, "alb2005_skip_missing_payment_block_rows"),
        "alb2005_skip_missing_access_condition_rows": metric_value(alb2005_skip_missing_summary, "alb2005_skip_missing_access_condition_rows"),
        "alb2005_skip_missing_financing_multiselect_rows": metric_value(alb2005_skip_missing_summary, "alb2005_skip_missing_financing_multiselect_rows"),
        "alb2005_skip_missing_payment_nonmissing_when_not_triggered_rows": metric_value(alb2005_skip_missing_summary, "alb2005_skip_missing_payment_nonmissing_when_not_triggered_rows"),
        "alb2005_skip_missing_payment_positive_when_not_triggered_rows": metric_value(alb2005_skip_missing_summary, "alb2005_skip_missing_payment_positive_when_not_triggered_rows"),
        "alb2005_skip_missing_payment_zero_or_missing_when_triggered_rows": metric_value(alb2005_skip_missing_summary, "alb2005_skip_missing_payment_zero_or_missing_when_triggered_rows"),
        "alb2005_skip_missing_condition_nonmissing_when_not_triggered_rows": metric_value(alb2005_skip_missing_summary, "alb2005_skip_missing_condition_nonmissing_when_not_triggered_rows"),
        "alb2005_skip_missing_condition_missing_when_triggered_rows": metric_value(alb2005_skip_missing_summary, "alb2005_skip_missing_condition_missing_when_triggered_rows"),
        "alb2005_skip_missing_financing_nonmissing_when_not_triggered_rows": metric_value(alb2005_skip_missing_summary, "alb2005_skip_missing_financing_nonmissing_when_not_triggered_rows"),
        "alb2005_skip_missing_financing_missing_when_triggered_rows": metric_value(alb2005_skip_missing_summary, "alb2005_skip_missing_financing_missing_when_triggered_rows"),
        "alb2005_skip_missing_recipe_ready_rows": metric_value(alb2005_skip_missing_summary, "alb2005_skip_missing_recipe_ready_rows"),
        "alb2005_skip_missing_outcome_ready_rows": metric_value(alb2005_skip_missing_summary, "alb2005_skip_missing_outcome_ready_rows"),
        "alb2005_skip_missing_climate_linkage_ready_rows": metric_value(alb2005_skip_missing_summary, "alb2005_skip_missing_climate_linkage_ready_rows"),
        "alb2005_skip_missing_current_decision": metric_value(alb2005_skip_missing_summary, "alb2005_skip_missing_current_decision", "missing"),
        "alb2005_consumption_oop_unit_period_rows": metric_value(alb2005_unit_period_summary, "alb2005_consumption_oop_unit_period_rows"),
        "alb2005_consumption_oop_unit_period_total_consumption_positive_rows": metric_value(alb2005_unit_period_summary, "alb2005_consumption_oop_unit_period_total_consumption_positive_rows"),
        "alb2005_consumption_oop_unit_period_rcons_positive_rows": metric_value(alb2005_unit_period_summary, "alb2005_consumption_oop_unit_period_rcons_positive_rows"),
        "alb2005_consumption_oop_unit_period_metadata_old_lek_rows": metric_value(alb2005_unit_period_summary, "alb2005_consumption_oop_unit_period_metadata_old_lek_rows_observed"),
        "alb2005_consumption_oop_unit_period_oop_old_lek_rows": metric_value(alb2005_unit_period_summary, "alb2005_consumption_oop_unit_period_oop_old_lek_questionnaire_rows_observed"),
        "alb2005_consumption_oop_unit_period_four_week_oop_rows": metric_value(alb2005_unit_period_summary, "alb2005_consumption_oop_unit_period_four_week_oop_rows_observed"),
        "alb2005_consumption_oop_unit_period_twelve_month_oop_rows": metric_value(alb2005_unit_period_summary, "alb2005_consumption_oop_unit_period_twelve_month_oop_rows_observed"),
        "alb2005_consumption_oop_unit_period_questionnaire_nonfood_old_lek_rows": metric_value(alb2005_unit_period_summary, "alb2005_consumption_oop_unit_period_questionnaire_nonfood_old_lek_rows_observed"),
        "alb2005_consumption_oop_unit_period_totcons_rcons_implied_scale_median": metric_value(alb2005_unit_period_summary, "alb2005_consumption_oop_unit_period_totcons_rcons_implied_scale_median"),
        "alb2005_consumption_oop_unit_period_roster_hhsize_median": metric_value(alb2005_unit_period_summary, "alb2005_consumption_oop_unit_period_roster_hhsize_median"),
        "alb2005_consumption_oop_unit_period_sdg382_ready_rows": metric_value(alb2005_unit_period_summary, "alb2005_consumption_oop_unit_period_sdg382_ready_rows"),
        "alb2005_consumption_oop_unit_period_recipe_ready_rows": metric_value(alb2005_unit_period_summary, "alb2005_consumption_oop_unit_period_recipe_ready_rows"),
        "alb2005_consumption_oop_unit_period_outcome_ready_rows": metric_value(alb2005_unit_period_summary, "alb2005_consumption_oop_unit_period_outcome_ready_rows"),
        "alb2005_consumption_oop_unit_period_climate_linkage_ready_rows": metric_value(alb2005_unit_period_summary, "alb2005_consumption_oop_unit_period_climate_linkage_ready_rows"),
        "alb2005_consumption_oop_unit_period_current_decision": metric_value(alb2005_unit_period_summary, "alb2005_consumption_oop_unit_period_current_decision", "missing"),
        "alb2005_consumption_aggregate_crosswalk_rows": metric_value(alb2005_aggregate_crosswalk_summary, "alb2005_consumption_aggregate_crosswalk_rows"),
        "alb2005_consumption_aggregate_crosswalk_metadata_rows": metric_value(alb2005_aggregate_crosswalk_summary, "alb2005_consumption_aggregate_crosswalk_metadata_rows"),
        "alb2005_consumption_aggregate_crosswalk_metadata_old_lek_rows": metric_value(alb2005_aggregate_crosswalk_summary, "alb2005_consumption_aggregate_crosswalk_metadata_old_lek_rows"),
        "alb2005_consumption_aggregate_crosswalk_local_poverty_columns": metric_value(alb2005_aggregate_crosswalk_summary, "alb2005_consumption_aggregate_crosswalk_local_poverty_columns"),
        "alb2005_consumption_aggregate_crosswalk_metadata_present_local_rows": metric_value(alb2005_aggregate_crosswalk_summary, "alb2005_consumption_aggregate_crosswalk_metadata_variables_present_in_local_raw_rows"),
        "alb2005_consumption_aggregate_crosswalk_metadata_absent_local_rows": metric_value(alb2005_aggregate_crosswalk_summary, "alb2005_consumption_aggregate_crosswalk_metadata_variables_absent_from_local_raw_rows"),
        "alb2005_consumption_aggregate_crosswalk_local_per_capita_component_rows": metric_value(alb2005_aggregate_crosswalk_summary, "alb2005_consumption_aggregate_crosswalk_local_per_capita_component_rows"),
        "alb2005_consumption_aggregate_crosswalk_totcons_positive_rows": metric_value(alb2005_aggregate_crosswalk_summary, "alb2005_consumption_aggregate_crosswalk_totcons_positive_rows"),
        "alb2005_consumption_aggregate_crosswalk_totcons05_local_rows": metric_value(alb2005_aggregate_crosswalk_summary, "alb2005_consumption_aggregate_crosswalk_totcons05_local_rows"),
        "alb2005_consumption_aggregate_crosswalk_component_formula_reconstructable_rows": metric_value(alb2005_aggregate_crosswalk_summary, "alb2005_consumption_aggregate_crosswalk_component_formula_reconstructable_rows"),
        "alb2005_consumption_aggregate_crosswalk_sdg382_ready_rows": metric_value(alb2005_aggregate_crosswalk_summary, "alb2005_consumption_aggregate_crosswalk_sdg382_ready_rows"),
        "alb2005_consumption_aggregate_crosswalk_recipe_ready_rows": metric_value(alb2005_aggregate_crosswalk_summary, "alb2005_consumption_aggregate_crosswalk_recipe_ready_rows"),
        "alb2005_consumption_aggregate_crosswalk_outcome_ready_rows": metric_value(alb2005_aggregate_crosswalk_summary, "alb2005_consumption_aggregate_crosswalk_outcome_ready_rows"),
        "alb2005_consumption_aggregate_crosswalk_climate_linkage_ready_rows": metric_value(alb2005_aggregate_crosswalk_summary, "alb2005_consumption_aggregate_crosswalk_climate_linkage_ready_rows"),
        "alb2005_consumption_aggregate_crosswalk_current_decision": metric_value(alb2005_aggregate_crosswalk_summary, "alb2005_consumption_aggregate_crosswalk_current_decision", "missing"),
        "alb2005_consumption_component_source_search_rows": metric_value(alb2005_component_source_summary, "alb2005_consumption_component_source_search_rows"),
        "alb2005_consumption_component_source_search_target_variables": metric_value(alb2005_component_source_summary, "alb2005_consumption_component_source_search_target_variables"),
        "alb2005_consumption_component_source_search_local_files_scanned": metric_value(alb2005_component_source_summary, "alb2005_consumption_component_source_search_local_files_scanned"),
        "alb2005_consumption_component_source_search_local_variables_scanned": metric_value(alb2005_component_source_summary, "alb2005_consumption_component_source_search_local_variables_scanned"),
        "alb2005_consumption_component_source_search_questionnaire_workbooks_scanned": metric_value(alb2005_component_source_summary, "alb2005_consumption_component_source_search_questionnaire_workbooks_scanned"),
        "alb2005_consumption_component_source_search_construction_code_files_found": metric_value(alb2005_component_source_summary, "alb2005_consumption_component_source_search_construction_code_files_found"),
        "alb2005_consumption_component_source_search_exact_target_variables_found": metric_value(alb2005_component_source_summary, "alb2005_consumption_component_source_search_exact_target_variables_found"),
        "alb2005_consumption_component_source_search_exact_target_variables_missing": metric_value(alb2005_component_source_summary, "alb2005_consumption_component_source_search_exact_target_variables_missing"),
        "alb2005_consumption_component_source_search_label_phrase_targets_found": metric_value(alb2005_component_source_summary, "alb2005_consumption_component_source_search_label_phrase_targets_found"),
        "alb2005_consumption_component_source_search_questionnaire_phrase_targets_found": metric_value(alb2005_component_source_summary, "alb2005_consumption_component_source_search_questionnaire_phrase_targets_found"),
        "alb2005_consumption_component_source_search_construction_code_targets_found": metric_value(alb2005_component_source_summary, "alb2005_consumption_component_source_search_construction_code_targets_found"),
        "alb2005_consumption_component_source_search_recipe_ready_rows": metric_value(alb2005_component_source_summary, "alb2005_consumption_component_source_search_recipe_ready_rows"),
        "alb2005_consumption_component_source_search_outcome_ready_rows": metric_value(alb2005_component_source_summary, "alb2005_consumption_component_source_search_outcome_ready_rows"),
        "alb2005_consumption_component_source_search_sdg382_ready_rows": metric_value(alb2005_component_source_summary, "alb2005_consumption_component_source_search_sdg382_ready_rows"),
        "alb2005_consumption_component_source_search_climate_linkage_ready_rows": metric_value(alb2005_component_source_summary, "alb2005_consumption_component_source_search_climate_linkage_ready_rows"),
        "alb2005_consumption_component_source_search_current_decision": metric_value(alb2005_component_source_summary, "alb2005_consumption_component_source_search_current_decision", "missing"),
        "alb2005_minimum_recipe_promotion_action_rows": metric_value(alb2005_minimum_recipe_summary, "alb2005_minimum_recipe_promotion_action_rows"),
        "alb2005_minimum_recipe_promotion_gate_rows": metric_value(alb2005_minimum_recipe_summary, "alb2005_minimum_recipe_promotion_gate_rows"),
        "alb2005_minimum_recipe_promotion_blocked_gates": metric_value(alb2005_minimum_recipe_summary, "alb2005_minimum_recipe_promotion_blocked_gates"),
        "alb2005_minimum_recipe_promotion_candidate_gates": metric_value(alb2005_minimum_recipe_summary, "alb2005_minimum_recipe_promotion_candidate_gates"),
        "alb2005_minimum_recipe_promotion_harmonized_ready_rows": metric_value(alb2005_minimum_recipe_summary, "alb2005_minimum_recipe_promotion_harmonized_ready_rows"),
        "alb2005_minimum_recipe_promotion_outcome_ready_rows": metric_value(alb2005_minimum_recipe_summary, "alb2005_minimum_recipe_promotion_outcome_ready_rows"),
        "alb2005_minimum_recipe_promotion_climate_linkage_ready_rows": metric_value(alb2005_minimum_recipe_summary, "alb2005_minimum_recipe_promotion_climate_linkage_ready_rows"),
        "alb2005_minimum_recipe_promotion_current_decision": metric_value(alb2005_minimum_recipe_summary, "alb2005_minimum_recipe_promotion_current_decision", "missing"),
        "alb2005_public_fieldwork_geo_metadata_evidence_rows": metric_value(alb2005_public_fieldwork_geo_summary, "alb2005_public_fieldwork_geo_metadata_evidence_rows"),
        "alb2005_public_fieldwork_geo_metadata_verified_source_rows": metric_value(alb2005_public_fieldwork_geo_summary, "alb2005_public_fieldwork_geo_metadata_verified_source_rows"),
        "alb2005_public_fieldwork_geo_metadata_source_missing_rows": metric_value(alb2005_public_fieldwork_geo_summary, "alb2005_public_fieldwork_geo_metadata_source_missing_rows"),
        "alb2005_public_fieldwork_geo_metadata_fieldwork_period_evidence_rows": metric_value(alb2005_public_fieldwork_geo_summary, "alb2005_public_fieldwork_geo_metadata_fieldwork_period_evidence_rows"),
        "alb2005_public_fieldwork_geo_metadata_gps_claim_rows": metric_value(alb2005_public_fieldwork_geo_summary, "alb2005_public_fieldwork_geo_metadata_gps_claim_rows"),
        "alb2005_public_fieldwork_geo_metadata_sampling_geo_rows": metric_value(alb2005_public_fieldwork_geo_summary, "alb2005_public_fieldwork_geo_metadata_sampling_geo_rows"),
        "alb2005_public_fieldwork_geo_metadata_household_timing_verified_rows": metric_value(alb2005_public_fieldwork_geo_summary, "alb2005_public_fieldwork_geo_metadata_household_timing_verified_rows"),
        "alb2005_public_fieldwork_geo_metadata_raw_coordinate_value_rows": metric_value(alb2005_public_fieldwork_geo_summary, "alb2005_public_fieldwork_geo_metadata_raw_coordinate_value_rows"),
        "alb2005_public_fieldwork_geo_metadata_climate_linkage_ready_rows": metric_value(alb2005_public_fieldwork_geo_summary, "alb2005_public_fieldwork_geo_metadata_climate_linkage_ready_rows"),
        "alb2005_public_fieldwork_geo_metadata_current_decision": metric_value(alb2005_public_fieldwork_geo_summary, "alb2005_public_fieldwork_geo_metadata_current_decision", "missing"),
        "alb2005_diary_timing_candidate_audit_rows": metric_value(alb2005_diary_timing_summary, "alb2005_diary_timing_candidate_audit_rows"),
        "alb2005_diary_timing_candidate_metadata_found_rows": metric_value(alb2005_diary_timing_summary, "alb2005_diary_timing_candidate_metadata_found_rows"),
        "alb2005_diary_timing_candidate_schema_file_rows": metric_value(alb2005_diary_timing_summary, "alb2005_diary_timing_candidate_schema_file_rows"),
        "alb2005_diary_timing_candidate_raw_bookmetadata_files_present": metric_value(alb2005_diary_timing_summary, "alb2005_diary_timing_candidate_raw_bookmetadata_files_present"),
        "alb2005_diary_timing_candidate_key_candidate_rows": metric_value(alb2005_diary_timing_summary, "alb2005_diary_timing_candidate_key_candidate_rows"),
        "alb2005_diary_timing_candidate_date_candidate_rows": metric_value(alb2005_diary_timing_summary, "alb2005_diary_timing_candidate_date_candidate_rows"),
        "alb2005_diary_timing_candidate_household_timing_promoted_rows": metric_value(alb2005_diary_timing_summary, "alb2005_diary_timing_candidate_household_timing_promoted_rows"),
        "alb2005_diary_timing_candidate_climate_linkage_ready_rows": metric_value(alb2005_diary_timing_summary, "alb2005_diary_timing_candidate_climate_linkage_ready_rows"),
        "alb2005_diary_timing_candidate_current_decision": metric_value(alb2005_diary_timing_summary, "alb2005_diary_timing_candidate_current_decision", "missing"),
        "alb2005_extracted_module_coverage_ddi_module_rows": metric_value(alb2005_extracted_module_summary, "alb2005_extracted_module_coverage_ddi_module_rows"),
        "alb2005_archive_member_rows": metric_value(alb2005_extracted_module_summary, "alb2005_archive_member_rows"),
        "alb2005_archive_sav_member_rows": metric_value(alb2005_extracted_module_summary, "alb2005_archive_sav_member_rows"),
        "alb2005_archive_questionnaire_member_rows": metric_value(alb2005_extracted_module_summary, "alb2005_archive_questionnaire_member_rows"),
        "alb2005_archive_ddi_module_present_rows": metric_value(alb2005_extracted_module_summary, "alb2005_archive_ddi_module_present_rows"),
        "alb2005_archive_ddi_module_absent_rows": metric_value(alb2005_extracted_module_summary, "alb2005_archive_ddi_module_absent_rows"),
        "alb2005_archive_critical_module_absent_rows": metric_value(alb2005_extracted_module_summary, "alb2005_archive_critical_module_absent_rows"),
        "alb2005_archive_listing_status": metric_value(alb2005_extracted_module_summary, "alb2005_archive_listing_status", "missing"),
        "alb2005_extracted_module_coverage_present_rows": metric_value(alb2005_extracted_module_summary, "alb2005_extracted_module_coverage_present_rows"),
        "alb2005_extracted_module_coverage_missing_rows": metric_value(alb2005_extracted_module_summary, "alb2005_extracted_module_coverage_missing_rows"),
        "alb2005_extracted_module_coverage_extracted_file_rows": metric_value(alb2005_extracted_module_summary, "alb2005_extracted_module_coverage_extracted_file_rows"),
        "alb2005_extracted_module_coverage_extra_extracted_rows": metric_value(alb2005_extracted_module_summary, "alb2005_extracted_module_coverage_extra_extracted_rows"),
        "alb2005_extracted_module_coverage_bookmetadata_missing_rows": metric_value(alb2005_extracted_module_summary, "alb2005_extracted_module_coverage_bookmetadata_missing_rows"),
        "alb2005_extracted_module_coverage_food_diary_missing_rows": metric_value(alb2005_extracted_module_summary, "alb2005_extracted_module_coverage_food_diary_missing_rows"),
        "alb2005_extracted_module_coverage_critical_missing_rows": metric_value(alb2005_extracted_module_summary, "alb2005_extracted_module_coverage_critical_missing_rows"),
        "alb2005_extracted_module_coverage_coordinate_metadata_variable_rows": metric_value(alb2005_extracted_module_summary, "alb2005_extracted_module_coverage_coordinate_metadata_variable_rows"),
        "alb2005_extracted_module_coverage_coordinate_extracted_file_rows": metric_value(alb2005_extracted_module_summary, "alb2005_extracted_module_coverage_coordinate_extracted_file_rows"),
        "alb2005_extracted_module_coverage_harmonized_ready_rows": metric_value(alb2005_extracted_module_summary, "alb2005_extracted_module_coverage_harmonized_ready_rows"),
        "alb2005_extracted_module_coverage_household_timing_ready_rows": metric_value(alb2005_extracted_module_summary, "alb2005_extracted_module_coverage_household_timing_ready_rows"),
        "alb2005_extracted_module_coverage_climate_linkage_ready_rows": metric_value(alb2005_extracted_module_summary, "alb2005_extracted_module_coverage_climate_linkage_ready_rows"),
        "alb2005_extracted_module_coverage_current_decision": metric_value(alb2005_extracted_module_summary, "alb2005_extracted_module_coverage_current_decision", "missing"),
        "alb2005_fallback_blocker_resolution_rows": metric_value(alb2005_fallback_blocker_summary, "alb2005_fallback_blocker_resolution_rows"),
        "alb2005_fallback_blocker_raw_package_rows": metric_value(alb2005_fallback_blocker_summary, "alb2005_fallback_blocker_raw_package_rows"),
        "alb2005_fallback_blocker_timing_rows": metric_value(alb2005_fallback_blocker_summary, "alb2005_fallback_blocker_timing_rows"),
        "alb2005_fallback_blocker_geography_rows": metric_value(alb2005_fallback_blocker_summary, "alb2005_fallback_blocker_geography_rows"),
        "alb2005_fallback_blocker_outcome_rows": metric_value(alb2005_fallback_blocker_summary, "alb2005_fallback_blocker_outcome_rows"),
        "alb2005_fallback_blocker_promotion_gate_rows": metric_value(alb2005_fallback_blocker_summary, "alb2005_fallback_blocker_promotion_gate_rows"),
        "alb2005_fallback_blocker_hard_blocked_rows": metric_value(alb2005_fallback_blocker_summary, "alb2005_fallback_blocker_hard_blocked_rows"),
        "alb2005_fallback_blocker_harmonized_ready_rows": metric_value(alb2005_fallback_blocker_summary, "alb2005_fallback_blocker_harmonized_ready_rows"),
        "alb2005_fallback_blocker_outcome_ready_rows": metric_value(alb2005_fallback_blocker_summary, "alb2005_fallback_blocker_outcome_ready_rows"),
        "alb2005_fallback_blocker_interview_timing_ready_rows": metric_value(alb2005_fallback_blocker_summary, "alb2005_fallback_blocker_interview_timing_ready_rows"),
        "alb2005_fallback_blocker_geography_ready_rows": metric_value(alb2005_fallback_blocker_summary, "alb2005_fallback_blocker_geography_ready_rows"),
        "alb2005_fallback_blocker_climate_linkage_ready_rows": metric_value(alb2005_fallback_blocker_summary, "alb2005_fallback_blocker_climate_linkage_ready_rows"),
        "alb2005_fallback_blocker_data_write_ready_rows": metric_value(alb2005_fallback_blocker_summary, "alb2005_fallback_blocker_data_write_ready_rows"),
        "alb2005_fallback_blocker_current_decision": metric_value(alb2005_fallback_blocker_summary, "alb2005_fallback_blocker_current_decision", "missing"),
        "albania_first_analysis_promotion_wave_rows": metric_value(albania_first_analysis_summary, "albania_first_analysis_promotion_wave_rows"),
        "albania_first_analysis_promotion_gate_rows": metric_value(albania_first_analysis_summary, "albania_first_analysis_promotion_gate_rows"),
        "albania_first_analysis_promotion_action_rows": metric_value(albania_first_analysis_summary, "albania_first_analysis_promotion_action_rows"),
        "albania_first_analysis_promotion_blocked_gate_rows": metric_value(albania_first_analysis_summary, "albania_first_analysis_promotion_blocked_gate_rows"),
        "albania_first_analysis_promotion_ready_wave_rows": metric_value(albania_first_analysis_summary, "albania_first_analysis_promotion_ready_wave_rows"),
        "albania_first_analysis_promotion_harmonized_ready_rows": metric_value(albania_first_analysis_summary, "albania_first_analysis_promotion_harmonized_ready_rows"),
        "albania_first_analysis_promotion_outcome_ready_rows": metric_value(albania_first_analysis_summary, "albania_first_analysis_promotion_outcome_ready_rows"),
        "albania_first_analysis_promotion_climate_linkage_ready_rows": metric_value(albania_first_analysis_summary, "albania_first_analysis_promotion_climate_linkage_ready_rows"),
        "albania_first_analysis_promotion_top_ranked_idno": metric_value(albania_first_analysis_summary, "albania_first_analysis_promotion_top_ranked_idno", "missing"),
        "albania_first_analysis_promotion_top_ranked_primary_blocker": metric_value(albania_first_analysis_summary, "albania_first_analysis_promotion_top_ranked_primary_blocker", "missing"),
        "albania_first_analysis_promotion_current_decision": metric_value(albania_first_analysis_summary, "albania_first_analysis_promotion_current_decision", "missing"),
        "albania_existing_raw_wave_rows": metric_value(albania_wave_summary, "albania_existing_raw_wave_rows"),
        "albania_existing_raw_wave_archive_present_rows": metric_value(albania_wave_summary, "albania_existing_raw_wave_archive_present_rows"),
        "albania_existing_raw_wave_extracted_rows": metric_value(albania_wave_summary, "albania_existing_raw_wave_extracted_rows"),
        "albania_existing_raw_wave_unintegrated_rows": metric_value(albania_wave_summary, "albania_existing_raw_wave_unintegrated_rows"),
        "albania_existing_raw_wave_total_raw_tabular_files": metric_value(albania_wave_summary, "albania_existing_raw_wave_total_raw_tabular_files"),
        "albania_existing_raw_wave_total_raw_variable_rows": metric_value(albania_wave_summary, "albania_existing_raw_wave_total_raw_variable_rows"),
        "albania_existing_raw_wave_oop_signal_rows": metric_value(albania_wave_summary, "albania_existing_raw_wave_oop_signal_rows"),
        "albania_existing_raw_wave_timing_signal_rows": metric_value(albania_wave_summary, "albania_existing_raw_wave_timing_signal_rows"),
        "albania_existing_raw_wave_gps_signal_rows": metric_value(albania_wave_summary, "albania_existing_raw_wave_gps_signal_rows"),
        "albania_existing_raw_wave_harmonization_ready_rows": metric_value(albania_wave_summary, "albania_existing_raw_wave_harmonization_ready_rows"),
        "albania_existing_raw_wave_climate_linkage_ready_rows": metric_value(albania_wave_summary, "albania_existing_raw_wave_climate_linkage_ready_rows"),
        "albania_existing_raw_wave_current_decision": metric_value(albania_wave_summary, "albania_existing_raw_wave_current_decision", "missing"),
        "alb2008_household_core_candidate_rows": metric_value(alb2008_core_summary, "alb2008_household_core_candidate_rows"),
        "alb2008_households_with_total_consumption": metric_value(alb2008_core_summary, "alb2008_households_with_total_consumption"),
        "alb2008_households_with_household_weight": metric_value(alb2008_core_summary, "alb2008_households_with_household_weight"),
        "alb2008_households_with_oop_4w_positive": metric_value(alb2008_core_summary, "alb2008_households_with_oop_4w_positive"),
        "alb2008_households_with_oop_12m_positive": metric_value(alb2008_core_summary, "alb2008_households_with_oop_12m_positive"),
        "alb2008_households_with_coarse_area": metric_value(alb2008_core_summary, "alb2008_households_with_coarse_area"),
        "alb2008_households_with_survey_month": metric_value(alb2008_core_summary, "alb2008_households_with_survey_month"),
        "alb2008_household_core_recipe_ready_rows": metric_value(alb2008_core_summary, "alb2008_household_core_recipe_ready_rows"),
        "alb2008_provisional_outcome_audit_rows": len(alb2008_outcome_audit),
        "alb2008_provisional_financial_stress_test_rows": metric_value(alb2008_outcome_summary, "alb2008_provisional_financial_stress_test_rows"),
        "alb2008_provisional_access_proxy_rows": metric_value(alb2008_outcome_summary, "alb2008_provisional_access_proxy_rows"),
        "alb2008_provisional_low_event_rate_rows": metric_value(alb2008_outcome_summary, "alb2008_provisional_low_event_rate_rows"),
        "alb2008_provisional_outcome_ready_rows": metric_value(alb2008_outcome_summary, "alb2008_provisional_outcome_ready_rows"),
        "alb2008_provisional_outcome_current_decision": metric_value(alb2008_outcome_summary, "alb2008_provisional_outcome_current_decision", "missing"),
        "alb2008_outcome_semantics_raw_value_rows": len(alb2008_semantics_audit),
        "alb2008_outcome_semantics_source_files_scanned": metric_value(alb2008_semantics_summary, "alb2008_outcome_semantics_source_files_scanned"),
        "alb2008_outcome_semantics_financial_oop_candidate_rows": metric_value(alb2008_semantics_summary, "alb2008_outcome_semantics_financial_oop_candidate_rows"),
        "alb2008_outcome_semantics_gift_candidate_rows": metric_value(alb2008_semantics_summary, "alb2008_outcome_semantics_gift_candidate_rows"),
        "alb2008_outcome_semantics_access_candidate_rows": metric_value(alb2008_semantics_summary, "alb2008_outcome_semantics_access_candidate_rows"),
        "alb2008_outcome_semantics_facility_proxy_rows": metric_value(alb2008_semantics_summary, "alb2008_outcome_semantics_facility_proxy_rows"),
        "alb2008_outcome_semantics_need_candidate_rows": metric_value(alb2008_semantics_summary, "alb2008_outcome_semantics_need_candidate_rows"),
        "alb2008_outcome_semantics_coping_candidate_rows": metric_value(alb2008_semantics_summary, "alb2008_outcome_semantics_coping_candidate_rows"),
        "alb2008_outcome_semantics_rows_with_value_labels": metric_value(alb2008_semantics_summary, "alb2008_outcome_semantics_rows_with_value_labels"),
        "alb2008_outcome_semantics_conditional_reason_rows": metric_value(alb2008_semantics_summary, "alb2008_outcome_semantics_conditional_reason_rows"),
        "alb2008_outcome_semantics_outcome_ready_rows": metric_value(alb2008_semantics_summary, "alb2008_outcome_semantics_outcome_ready_rows"),
        "alb2008_outcome_semantics_sdg382_ready_rows": metric_value(alb2008_semantics_summary, "alb2008_outcome_semantics_sdg382_ready_rows"),
        "alb2008_outcome_semantics_climate_linkage_ready_rows": metric_value(alb2008_semantics_summary, "alb2008_outcome_semantics_climate_linkage_ready_rows"),
        "alb2008_outcome_semantics_current_decision": metric_value(alb2008_semantics_summary, "alb2008_outcome_semantics_current_decision", "missing"),
        "alb2008_timing_geography_audit_rows": len(alb2008_timing_geo_audit),
        "alb2008_timing_geography_source_files_scanned": metric_value(alb2008_timing_geo_summary, "alb2008_timing_geography_source_files_scanned"),
        "alb2008_interview_timing_verified_rows": metric_value(alb2008_timing_geo_summary, "alb2008_interview_timing_verified_rows"),
        "alb2008_coordinate_candidate_rows": metric_value(alb2008_timing_geo_summary, "alb2008_coordinate_candidate_rows"),
        "alb2008_coarse_geography_household_rows": metric_value(alb2008_timing_geo_summary, "alb2008_coarse_geography_household_rows"),
        "alb2008_climate_linkage_ready_rows": metric_value(alb2008_timing_geo_summary, "alb2008_climate_linkage_ready_rows"),
        "alb2008_timing_geography_current_decision": metric_value(alb2008_timing_geo_summary, "alb2008_timing_geography_current_decision", "missing"),
        "alb2008_fallback_blocker_resolution_rows": metric_value(alb2008_fallback_blocker_summary, "alb2008_fallback_blocker_resolution_rows"),
        "alb2008_fallback_blocker_timing_rows": metric_value(alb2008_fallback_blocker_summary, "alb2008_fallback_blocker_timing_rows"),
        "alb2008_fallback_blocker_geography_rows": metric_value(alb2008_fallback_blocker_summary, "alb2008_fallback_blocker_geography_rows"),
        "alb2008_fallback_blocker_outcome_rows": metric_value(alb2008_fallback_blocker_summary, "alb2008_fallback_blocker_outcome_rows"),
        "alb2008_fallback_blocker_promotion_gate_rows": metric_value(alb2008_fallback_blocker_summary, "alb2008_fallback_blocker_promotion_gate_rows"),
        "alb2008_fallback_blocker_hard_blocked_rows": metric_value(alb2008_fallback_blocker_summary, "alb2008_fallback_blocker_hard_blocked_rows"),
        "alb2008_fallback_blocker_interview_timing_ready_rows": metric_value(alb2008_fallback_blocker_summary, "alb2008_fallback_blocker_interview_timing_ready_rows"),
        "alb2008_fallback_blocker_geography_ready_rows": metric_value(alb2008_fallback_blocker_summary, "alb2008_fallback_blocker_geography_ready_rows"),
        "alb2008_fallback_blocker_outcome_ready_rows": metric_value(alb2008_fallback_blocker_summary, "alb2008_fallback_blocker_outcome_ready_rows"),
        "alb2008_fallback_blocker_climate_linkage_ready_rows": metric_value(alb2008_fallback_blocker_summary, "alb2008_fallback_blocker_climate_linkage_ready_rows"),
        "alb2008_fallback_blocker_data_write_ready_rows": metric_value(alb2008_fallback_blocker_summary, "alb2008_fallback_blocker_data_write_ready_rows"),
        "alb2008_fallback_blocker_current_decision": metric_value(alb2008_fallback_blocker_summary, "alb2008_fallback_blocker_current_decision", "missing"),
        "first_batch_dataset_gate_rows": len(first_batch_dataset_gate),
        "first_batch_concept_template_rows": len(first_batch_concept_template),
        "first_batch_variable_template_rows": len(first_batch_variable_template),
        "first_batch_verification_summary_rows": len(first_batch_verification_summary),
        "first_batch_datasets_ready_for_value_audit": sum(1 for r in first_batch_dataset_gate if r.get("current_gate_status") == "ready_for_manual_value_label_unit_key_audit"),
        "first_batch_concepts_ready_for_value_audit": sum(1 for r in first_batch_concept_template if r.get("current_concept_gate") == "ready_for_manual_value_label_unit_key_audit"),
        "first_batch_variables_ready_for_value_audit": sum(1 for r in first_batch_variable_template if r.get("verification_status") == "ready_for_manual_value_audit"),
        "raw_download_targets": len(raw_download_targets),
        "raw_download_raw_like_files": sum(1 for r in raw_download_manifest if r.get("file_role") in {"archive", "raw_tabular_or_spreadsheet"}),
        "raw_download_raw_like_targets": sum(1 for r in raw_download_targets if r.get("status") == "raw_or_archive_files_present"),
        "raw_ingestion_plan_rows": len(raw_ingestion_plan),
        "raw_ingestion_concept_rows": len(raw_ingestion_concepts),
        "raw_ingestion_module_rows": len(raw_ingestion_modules),
        "raw_ingestion_summary_rows": len(raw_ingestion_summary),
        "raw_ingestion_waiting_rows": sum(1 for r in raw_ingestion_plan if r.get("ingestion_gate_status") == "waiting_for_manual_download"),
        "raw_ingestion_ready_rows": sum(1 for r in raw_ingestion_plan if r.get("ingestion_gate_status") == "ready_for_raw_schema_inspection"),
        "raw_ingestion_verified_concepts": sum(1 for r in raw_ingestion_concepts if r.get("raw_verification_status") == "raw_variables_inspected"),
        "raw_variable_protocol_rows": len(raw_variable_protocol),
        "harmonization_scaffold_rows": len(harmonization_scaffold),
        "raw_variable_summary_rows": len(raw_variable_summary),
        "raw_variable_protocol_not_inspected_rows": sum(1 for r in raw_variable_protocol if r.get("verification_status") == "raw_not_inspected"),
        "raw_variable_protocol_value_audit_pending_rows": sum(1 for r in raw_variable_protocol if r.get("verification_status") == "raw_variable_seen_value_audit_pending"),
        "harmonization_recipe_gate_rows": len(harmonization_recipe_gate),
        "harmonization_value_audit_template_rows": len(harmonization_value_audit_template),
        "harmonization_verified_candidate_rows": len(harmonization_verified_candidates),
        "harmonization_readiness_rows": len(harmonization_readiness),
        "harmonization_recipe_gate_summary_rows": len(harmonization_recipe_gate_summary),
        "harmonization_recipe_ready_rows": sum(1 for r in harmonization_recipe_gate if r.get("recipe_gate_status") == "recipe_candidate_ready"),
        "harmonization_recipe_blocked_rows": sum(1 for r in harmonization_recipe_gate if r.get("recipe_gate_status") != "recipe_candidate_ready"),
        "harmonization_ready_country_wave_rows": sum(1 for r in harmonization_readiness if r.get("readiness_status") == "ready_for_verified_recipe_assembly"),
        "analysis_dataset_promotion_audit_rows": metric_value(analysis_dataset_promotion_summary, "analysis_dataset_promotion_audit_rows"),
        "analysis_dataset_promotion_blocked_rows": metric_value(analysis_dataset_promotion_summary, "analysis_dataset_promotion_blocked_rows"),
        "analysis_dataset_promotion_promoted_rows": metric_value(analysis_dataset_promotion_summary, "analysis_dataset_promotion_promoted_rows"),
        "analysis_dataset_promotion_data_file_count": metric_value(analysis_dataset_promotion_summary, "analysis_dataset_promotion_data_file_count"),
        "analysis_dataset_promotion_verified_recipe_candidates": metric_value(analysis_dataset_promotion_summary, "analysis_dataset_promotion_verified_recipe_candidates"),
        "analysis_dataset_promotion_ready_country_waves": metric_value(analysis_dataset_promotion_summary, "analysis_dataset_promotion_ready_country_waves"),
        "analysis_dataset_promotion_alb2002_temp_core_rows": metric_value(analysis_dataset_promotion_summary, "analysis_dataset_promotion_alb2002_temp_core_rows"),
        "analysis_dataset_promotion_alb2002_harmonized_ready_rows": metric_value(analysis_dataset_promotion_summary, "analysis_dataset_promotion_alb2002_harmonized_ready_rows"),
        "analysis_dataset_promotion_alb2002_outcome_ready_rows": metric_value(analysis_dataset_promotion_summary, "analysis_dataset_promotion_alb2002_outcome_ready_rows"),
        "analysis_dataset_promotion_alb2002_climate_linkage_ready_rows": metric_value(analysis_dataset_promotion_summary, "analysis_dataset_promotion_alb2002_climate_linkage_ready_rows"),
        "analysis_dataset_promotion_limited_harmonized_core_rows": metric_value(analysis_dataset_promotion_summary, "analysis_dataset_promotion_limited_harmonized_core_rows"),
        "analysis_dataset_promotion_limited_harmonized_core_data_write_ready_rows": metric_value(analysis_dataset_promotion_summary, "analysis_dataset_promotion_limited_harmonized_core_data_write_ready_rows"),
        "analysis_dataset_promotion_limited_harmonized_core_final_outcome_ready_rows": metric_value(analysis_dataset_promotion_summary, "analysis_dataset_promotion_limited_harmonized_core_final_outcome_ready_rows"),
        "analysis_dataset_promotion_limited_harmonized_core_climate_linkage_ready_rows": metric_value(analysis_dataset_promotion_summary, "analysis_dataset_promotion_limited_harmonized_core_climate_linkage_ready_rows"),
        "analysis_dataset_promotion_limited_harmonized_core_analysis_ready_rows": metric_value(analysis_dataset_promotion_summary, "analysis_dataset_promotion_limited_harmonized_core_analysis_ready_rows"),
        "analysis_dataset_promotion_limited_financial_outcome_rows": metric_value(analysis_dataset_promotion_summary, "analysis_dataset_promotion_limited_financial_outcome_rows"),
        "analysis_dataset_promotion_limited_financial_outcome_data_write_ready_rows": metric_value(analysis_dataset_promotion_summary, "analysis_dataset_promotion_limited_financial_outcome_data_write_ready_rows"),
        "analysis_dataset_promotion_limited_financial_outcome_che10_rows": metric_value(analysis_dataset_promotion_summary, "analysis_dataset_promotion_limited_financial_outcome_che10_rows"),
        "analysis_dataset_promotion_limited_financial_outcome_che25_rows": metric_value(analysis_dataset_promotion_summary, "analysis_dataset_promotion_limited_financial_outcome_che25_rows"),
        "analysis_dataset_promotion_limited_financial_outcome_sdg382_ready_rows": metric_value(analysis_dataset_promotion_summary, "analysis_dataset_promotion_limited_financial_outcome_sdg382_ready_rows"),
        "analysis_dataset_promotion_limited_financial_outcome_access_ready_rows": metric_value(analysis_dataset_promotion_summary, "analysis_dataset_promotion_limited_financial_outcome_access_ready_rows"),
        "analysis_dataset_promotion_limited_financial_outcome_composite_ready_rows": metric_value(analysis_dataset_promotion_summary, "analysis_dataset_promotion_limited_financial_outcome_composite_ready_rows"),
        "analysis_dataset_promotion_limited_financial_outcome_climate_linkage_ready_rows": metric_value(analysis_dataset_promotion_summary, "analysis_dataset_promotion_limited_financial_outcome_climate_linkage_ready_rows"),
        "analysis_dataset_promotion_limited_financial_outcome_analysis_ready_rows": metric_value(analysis_dataset_promotion_summary, "analysis_dataset_promotion_limited_financial_outcome_analysis_ready_rows"),
        "analysis_dataset_promotion_limited_climate_exposure_rows": metric_value(analysis_dataset_promotion_summary, "analysis_dataset_promotion_limited_climate_exposure_rows"),
        "analysis_dataset_promotion_limited_climate_exposure_data_write_ready_rows": metric_value(analysis_dataset_promotion_summary, "analysis_dataset_promotion_limited_climate_exposure_data_write_ready_rows"),
        "analysis_dataset_promotion_limited_climate_exposure_climate_linkage_ready_rows": metric_value(analysis_dataset_promotion_summary, "analysis_dataset_promotion_limited_climate_exposure_climate_linkage_ready_rows"),
        "analysis_dataset_promotion_limited_climate_exposure_analysis_ready_rows": metric_value(analysis_dataset_promotion_summary, "analysis_dataset_promotion_limited_climate_exposure_analysis_ready_rows"),
        "analysis_dataset_promotion_limited_climate_linked_rows": metric_value(analysis_dataset_promotion_summary, "analysis_dataset_promotion_limited_climate_linked_rows"),
        "analysis_dataset_promotion_limited_climate_linked_data_write_ready_rows": metric_value(analysis_dataset_promotion_summary, "analysis_dataset_promotion_limited_climate_linked_data_write_ready_rows"),
        "analysis_dataset_promotion_limited_climate_linked_descriptive_ready_rows": metric_value(analysis_dataset_promotion_summary, "analysis_dataset_promotion_limited_climate_linked_descriptive_ready_rows"),
        "analysis_dataset_promotion_limited_climate_linked_predictive_ml_ready_rows": metric_value(analysis_dataset_promotion_summary, "analysis_dataset_promotion_limited_climate_linked_predictive_ml_ready_rows"),
        "analysis_dataset_promotion_limited_climate_linked_reduced_form_ready_rows": metric_value(analysis_dataset_promotion_summary, "analysis_dataset_promotion_limited_climate_linked_reduced_form_ready_rows"),
        "analysis_dataset_promotion_limited_climate_linked_robustness_ready_rows": metric_value(analysis_dataset_promotion_summary, "analysis_dataset_promotion_limited_climate_linked_robustness_ready_rows"),
        "analysis_dataset_promotion_limited_climate_linked_analysis_ready_rows": metric_value(analysis_dataset_promotion_summary, "analysis_dataset_promotion_limited_climate_linked_analysis_ready_rows"),
        "analysis_dataset_promotion_current_decision": metric_value(analysis_dataset_promotion_summary, "analysis_dataset_promotion_current_decision", "missing"),
        "alb2002_harmonized_core_promotion_audit_rows": len(alb2002_harmonized_core_promotion_audit),
        "alb2002_harmonized_core_rows": metric_value(alb2002_harmonized_core_promotion_summary, "alb2002_harmonized_household_core_rows"),
        "alb2002_harmonized_core_final_outcome_ready_rows": metric_value(alb2002_harmonized_core_promotion_summary, "alb2002_harmonized_household_core_final_outcome_ready_rows"),
        "alb2002_harmonized_core_climate_linkage_ready_rows": metric_value(alb2002_harmonized_core_promotion_summary, "alb2002_harmonized_household_core_climate_linkage_ready_rows"),
        "alb2002_limited_financial_outcome_promotion_audit_rows": len(alb2002_limited_financial_outcome_promotion_audit),
        "alb2002_limited_financial_outcome_rows": metric_value(alb2002_limited_financial_outcome_promotion_summary, "alb2002_limited_financial_outcome_rows"),
        "alb2002_limited_financial_outcome_che10_rows": metric_value(alb2002_limited_financial_outcome_promotion_summary, "alb2002_limited_financial_outcome_che10_rows"),
        "alb2002_limited_financial_outcome_che10_weighted_rate": metric_value(alb2002_limited_financial_outcome_promotion_summary, "alb2002_limited_financial_outcome_che10_weighted_rate"),
        "alb2002_limited_financial_outcome_che25_rows": metric_value(alb2002_limited_financial_outcome_promotion_summary, "alb2002_limited_financial_outcome_che25_rows"),
        "alb2002_limited_financial_outcome_che25_weighted_rate": metric_value(alb2002_limited_financial_outcome_promotion_summary, "alb2002_limited_financial_outcome_che25_weighted_rate"),
        "alb2002_limited_financial_outcome_sdg382_ready_rows": metric_value(alb2002_limited_financial_outcome_promotion_summary, "alb2002_limited_financial_outcome_sdg382_ready_rows"),
        "alb2002_limited_financial_outcome_access_ready_rows": metric_value(alb2002_limited_financial_outcome_promotion_summary, "alb2002_limited_financial_outcome_access_ready_rows"),
        "alb2002_limited_financial_outcome_composite_ready_rows": metric_value(alb2002_limited_financial_outcome_promotion_summary, "alb2002_limited_financial_outcome_composite_ready_rows"),
        "alb2002_limited_financial_outcome_climate_linkage_ready_rows": metric_value(alb2002_limited_financial_outcome_promotion_summary, "alb2002_limited_financial_outcome_climate_linkage_ready_rows"),
        "alb2002_limited_financial_outcome_final_analysis_ready_rows": metric_value(alb2002_limited_financial_outcome_promotion_summary, "alb2002_limited_financial_outcome_final_analysis_ready_rows"),
        "alb2002_limited_climate_exposure_promotion_audit_rows": len(alb2002_limited_climate_exposure_promotion_audit),
        "alb2002_limited_climate_exposure_rows": metric_value(alb2002_limited_climate_exposure_promotion_summary, "alb2002_limited_climate_exposure_rows"),
        "alb2002_limited_climate_exposure_climate_linkage_ready_rows": metric_value(alb2002_limited_climate_exposure_promotion_summary, "alb2002_limited_climate_exposure_climate_linkage_ready_rows"),
        "alb2002_limited_climate_exposure_final_analysis_ready_rows": metric_value(alb2002_limited_climate_exposure_promotion_summary, "alb2002_limited_climate_exposure_final_analysis_ready_rows"),
        "alb2002_limited_climate_linked_promotion_audit_rows": len(alb2002_limited_climate_linked_promotion_audit),
        "alb2002_limited_climate_linked_rows": metric_value(alb2002_limited_climate_linked_promotion_summary, "alb2002_limited_climate_linked_rows"),
        "alb2002_limited_climate_linked_household_rows": metric_value(alb2002_limited_climate_linked_promotion_summary, "alb2002_limited_climate_linked_household_rows"),
        "alb2002_limited_climate_linked_window_rows": metric_value(alb2002_limited_climate_linked_promotion_summary, "alb2002_limited_climate_linked_window_rows"),
        "alb2002_limited_climate_linked_unmatched_rows": metric_value(alb2002_limited_climate_linked_promotion_summary, "alb2002_limited_climate_linked_unmatched_rows"),
        "alb2002_limited_climate_linked_descriptive_ready_rows": metric_value(alb2002_limited_climate_linked_promotion_summary, "alb2002_limited_climate_linked_descriptive_ready_rows"),
        "alb2002_limited_climate_linked_predictive_ml_ready_rows": metric_value(alb2002_limited_climate_linked_promotion_summary, "alb2002_limited_climate_linked_predictive_ml_ready_rows"),
        "alb2002_limited_climate_linked_reduced_form_ready_rows": metric_value(alb2002_limited_climate_linked_promotion_summary, "alb2002_limited_climate_linked_reduced_form_ready_rows"),
        "alb2002_limited_climate_linked_robustness_ready_rows": metric_value(alb2002_limited_climate_linked_promotion_summary, "alb2002_limited_climate_linked_robustness_ready_rows"),
        "alb2002_limited_climate_linked_final_analysis_ready_rows": metric_value(alb2002_limited_climate_linked_promotion_summary, "alb2002_limited_climate_linked_final_analysis_ready_rows"),
        "minimum_viable_target_rows": len(minimum_viable_targets),
        "minimum_viable_bundle_rows": len(minimum_viable_bundles),
        "minimum_viable_summary_rows": len(minimum_viable_summary),
        "minimum_viable_target_countries": len({r.get("country", "") for r in minimum_viable_targets if r.get("country", "")}),
        "minimum_viable_acquisition_sets": len({r.get("acquisition_set", "") for r in minimum_viable_targets if r.get("acquisition_set", "")}),
        "source_inventory": len(source_inventory),
        "studies": len(studies),
        "files": len(files),
        "variables": len(variables),
        "raw_files": len(raw_files),
        "raw_variables": len(raw_variables),
        "harmonization_audit_rows": len(harmonization_audit),
        "harmonized_lineage_rows": len(harmonized_lineage),
        "harmonized_rows": len(harmonized_household),
        "harmonization_output_ok": 1 if has_success_status(harmonization_audit, "harmonized_output") else 0,
        "climate_audit_rows": len(climate_audit),
        "climate_source_probe_rows": len(climate_source_probe),
        "climate_source_probe_ok": sum(1 for r in climate_source_probe if r.get("status") in {"reachable_snapshot_saved", "pass_api_parameters_present"}),
        "climate_exposure_plan_rows": len(climate_exposure_plan),
        "climate_exposure_spec_rows": len(climate_exposure_spec),
        "climate_exposure_plan_summary_rows": len(climate_exposure_plan_summary),
        "climate_exposure_metadata_ready_rows": sum(1 for r in climate_exposure_plan if r.get("climate_linkage_gate_status") == "metadata_ready_raw_unverified"),
        "climate_exposure_ready_for_linkage_rows": sum(1 for r in climate_exposure_plan if r.get("climate_linkage_gate_status") == "ready_for_climate_linkage_input_build"),
        "climate_exposure_blocked_spec_rows": sum(1 for r in climate_exposure_spec if r.get("current_status") == "blocked_until_verified_geography_and_timing"),
        "climate_linkage_requirement_rows": len(climate_linkage_requirements),
        "climate_source_method_rows": len(climate_source_method_matrix),
        "climate_validation_protocol_rows": len(climate_exposure_validation_protocol),
        "climate_linkage_readiness_rows": len(climate_linkage_readiness),
        "climate_validation_protocol_summary_rows": len(climate_validation_protocol_summary),
        "climate_linkage_ready_value_rows": sum(1 for r in climate_linkage_readiness if r.get("readiness_status") == "ready_for_climate_linkage_value_audit"),
        "climate_linkage_blocked_value_rows": sum(1 for r in climate_linkage_readiness if r.get("readiness_status") != "ready_for_climate_linkage_value_audit"),
        "climate_exposure_rows": len(climate_exposures),
        "climate_merge_audit_rows": len(climate_merge_audit),
        "climate_linked_rows": len(climate_linked),
        "outcome_audit_rows": len(outcome_audit),
        "outcome_audit_constructed_rows": sum(1 for r in outcome_audit if r.get("status") == "constructed"),
        "outcome_construction_audit_rows": len(outcome_construct_audit),
        "household_outcome_rows": len(household_outcomes),
        "outcome_denominator_plan_rows": len(outcome_denominator_plan),
        "outcome_specification_plan_rows": len(outcome_specification_plan),
        "outcome_denominator_plan_summary_rows": len(outcome_denominator_plan_summary),
        "outcome_plan_metadata_ready_rows": sum(1 for r in outcome_denominator_plan if r.get("outcome_gate_status") == "metadata_ready_raw_unverified"),
        "outcome_plan_ready_rows": sum(1 for r in outcome_denominator_plan if r.get("outcome_gate_status") == "ready_for_harmonized_outcome_construction"),
        "outcome_plan_metadata_incomplete_rows": sum(1 for r in outcome_denominator_plan if r.get("outcome_gate_status") == "metadata_incomplete_for_outcome"),
        "sdg382_denominator_requirement_rows": len(sdg382_denominator_requirements),
        "sdg382_denominator_source_rows": len(sdg382_denominator_sources),
        "sdg382_denominator_country_wave_rows": len(sdg382_denominator_readiness),
        "sdg382_denominator_summary_rows": len(sdg382_denominator_summary),
        "sdg382_denominator_ready_rows": sum(1 for r in sdg382_denominator_readiness if r.get("readiness_status") == "ready_for_household_denominator_value_audit"),
        "sdg382_denominator_blocked_rows": sum(1 for r in sdg382_denominator_readiness if r.get("readiness_status") != "ready_for_household_denominator_value_audit"),
        "modeling_identification_plan_rows": len(modeling_identification_plan),
        "modeling_validation_plan_rows": len(modeling_validation_plan),
        "falsification_placebo_plan_rows": len(falsification_placebo_plan),
        "policy_learning_plan_rows": len(policy_learning_plan),
        "modeling_identification_summary_rows": len(modeling_identification_summary),
        "modeling_predictive_ready_rows": sum(1 for r in modeling_identification_plan if r.get("predictive_ml_gate_status") == "ready_for_nonrandom_validation_design"),
        "modeling_reduced_form_ready_rows": sum(1 for r in modeling_identification_plan if r.get("reduced_form_gate_status") == "ready_for_reduced_form_estimation_design"),
        "modeling_causal_ml_ready_rows": sum(1 for r in modeling_identification_plan if r.get("causal_ml_policy_gate_status") == "ready_for_causal_ml_specification"),
        "modeling_policy_ready_rows": sum(1 for r in modeling_identification_plan if r.get("policy_learning_gate_status") == "ready_for_policy_learning_sensitivity_design"),
        "mechanism_requirement_rows": len(mechanism_requirements),
        "mechanism_pathway_protocol_rows": len(mechanism_pathway_protocol),
        "mechanism_readiness_rows": len(mechanism_readiness),
        "mechanism_summary_rows": len(mechanism_summary),
        "mechanism_ready_rows": sum(1 for r in mechanism_readiness if r.get("readiness_status") == "ready_for_mechanism_analysis_design"),
        "mechanism_blocked_rows": sum(1 for r in mechanism_readiness if r.get("readiness_status") != "ready_for_mechanism_analysis_design"),
        "empirical_dashboard_rows": len(empirical_dashboard),
        "empirical_no_go_rows": len(empirical_no_go),
        "empirical_no_go_pass_rows": sum(1 for r in empirical_no_go if r.get("status") == "pass"),
        "empirical_no_go_blocked_rows": sum(1 for r in empirical_no_go if r.get("status") != "pass"),
        "empirical_dashboard_summary_rows": len(empirical_dashboard_summary),
        "direct_read_bundle_rows": len(direct_read_bundle),
        "direct_read_manifest_rows": len(direct_read_manifest),
        "direct_read_manifest_present_rows": sum(1 for r in direct_read_manifest if r.get("current_status") == "present_nonempty"),
        "direct_read_manifest_missing_rows": sum(1 for r in direct_read_manifest if r.get("current_status") != "present_nonempty"),
        "direct_read_summary_rows": len(direct_read_summary),
        "objective_traceability_rows": len(objective_traceability),
        "objective_traceability_satisfied_rows": sum(1 for r in objective_traceability if r.get("status") == "satisfied"),
        "objective_traceability_unresolved_rows": sum(1 for r in objective_traceability if r.get("status") != "satisfied"),
        "objective_guardrail_rows": len(objective_guardrails),
        "objective_guardrail_satisfied_rows": sum(1 for r in objective_guardrails if r.get("status") == "satisfied"),
        "objective_guardrail_unresolved_rows": sum(1 for r in objective_guardrails if r.get("status") != "satisfied"),
        "objective_traceability_summary_rows": len(objective_traceability_summary),
        "python_package_inventory_rows": len(python_package_inventory),
        "python_packages_installed_rows": sum(1 for r in python_package_inventory if r.get("installed") == "1"),
        "python_packages_missing_rows": sum(1 for r in python_package_inventory if r.get("installed") != "1"),
        "python_environment_audit_rows": len(python_environment_audit),
        "python_environment_audit_complete_rows": sum(1 for r in python_environment_audit if r.get("status") == "complete"),
        "python_environment_audit_incomplete_rows": sum(1 for r in python_environment_audit if r.get("status") != "complete"),
        "python_environment_summary_rows": len(python_environment_summary),
        "validation_reference_probe_rows": len(validation_reference_probe),
        "validation_reference_probe_ok": sum(1 for r in validation_reference_probe if r.get("status") in {"reachable_snapshot_saved", "indicator_metadata_available"}),
        "validation_reference_sample_rows": sum(1 for r in validation_reference_samples if r.get("status") == "sample_record"),
        "hefpi_uhc_series_rows": sum(1 for r in hefpi_uhc_series if r.get("status") == "hefpi_uhc_series"),
        "hefpi_uhc_reference_rows": sum(1 for r in hefpi_uhc_reference if r.get("status") == "hefpi_uhc_reference_record"),
        "descriptive_audit_rows": len(descriptive_audit),
        "descriptive_prevalence_rows": len(descriptive_prevalence),
        "descriptive_missingness_rows": len(descriptive_missingness),
        "sample_flow_rows": len(sample_flow),
        "sample_gate_rows": len(sample_gate),
        "sample_gate_metadata_main_rows": sum(1 for r in sample_gate if r.get("metadata_has_main_sample_core") == "1"),
        "sample_gate_access_secondary_rows": sum(1 for r in sample_gate if r.get("eligible_for_access_secondary_sample") == "1"),
        "sample_gate_raw_final_rows": sum(1 for r in sample_gate if r.get("eligible_for_final_sample") == "1"),
        "sample_gate_failed_rules": sum(1 for r in sample_gate_summary if r.get("status") == "fail"),
        "variable_confidence_rows": len(variable_confidence),
        "metadata_quality_priority_rows": len(metadata_quality_priority),
        "metadata_quality_rows": len(metadata_quality),
        "metadata_quality_summary_rows": len(metadata_quality_summary),
        "metadata_quality_financial_rows": sum(1 for r in metadata_quality if r.get("quality_has_main_financial_core") == "1"),
        "metadata_quality_double_rows": sum(1 for r in metadata_quality if r.get("quality_has_double_failure_core") == "1"),
        "metadata_likely_false_positive_rows": sum(1 for r in variable_confidence if r.get("metadata_confidence") == "likely_false_positive"),
        "predictive_audit_rows": len(predictive_audit),
        "predictive_metric_rows": len(predictive_metrics),
        "predictive_feature_rows": len(predictive_features),
        "causal_model_audit_rows": len(causal_model_audit),
        "reduced_form_estimate_rows": len(reduced_form_estimates),
        "placebo_readiness_rows": len(placebo_readiness),
        "causal_ml_policy_audit_rows": len(causal_ml_policy_audit),
        "causal_ml_rejection_rows": status_starts(causal_ml_policy_audit, ("rejected_",)),
        "causal_ml_cate_rows": len(causal_ml_cate),
        "policy_sim_rows": len(policy_sim),
        "robustness_audit_rows": len(robustness_audit),
        "robustness_result_rows": len(robustness_results),
        "robustness_attempted_rows": status_starts(robustness_results, ("complete", "attempted")),
        "map_rows": total_map_rows,
        "designs": len(designs),
    }
    write_completion_audit(stats)
    completion_rows = read_csv_dicts(RESULT_DIR / "completion_criteria_audit.csv")
    incomplete_criteria = [r for r in completion_rows if r["status"] == "incomplete"]

    score_counts = group_count(screening, "feasibility score from 0 to 5")
    manual_counts = group_count(manual, "source_name")
    source_status_counts = group_count(source_inventory, "status")
    external_probe_status_counts = group_count(external_probe, "probe_status")
    public_external_download_status_counts = group_count(public_external_downloads, "download_status")
    worldbank_doc_status_counts = group_count(worldbank_public_docs, "status")
    worldbank_doc_resource_counts = group_count(worldbank_public_docs, "resource_type")
    raw_download_intake_status_counts = group_count(raw_download_intake, "intake_status")
    raw_download_expected_status_counts = group_count(raw_download_expected, "expected_file_status")
    first_batch_intake_status_counts = group_count(first_batch_checklist, "raw_intake_status")
    first_batch_target_reason_counts = group_count(first_batch_file_targets, "target_reason")
    first_batch_direct_route_counts = group_count(first_batch_access_probe, "direct_raw_route_status")
    first_batch_manual_action_counts = group_count(first_batch_access_probe, "manual_action_status")
    first_batch_handoff_status_counts = group_count(first_batch_handoff, "handoff_status")
    first_batch_file_queue_reason_counts = group_count(first_batch_file_queue, "target_reasons")
    first_batch_documentation_status_counts = group_count(first_batch_documentation, "coverage_status")
    first_batch_documentation_resource_counts = group_count(first_batch_documentation, "resource_type")
    first_batch_file_source_status_counts = group_count(first_batch_file_source_trace, "source_trace_status")
    first_batch_file_source_metadata_file_counts = group_count(first_batch_file_source_trace, "metadata_file_status")
    first_batch_merge_key_status_counts = group_count(first_batch_merge_key_plan, "merge_key_lineage_status")
    first_batch_merge_key_role_counts = group_count(first_batch_merge_key_candidates, "lineage_role")
    first_batch_value_status_counts = group_count(first_batch_value_key_audit, "value_audit_status")
    first_batch_value_read_counts = group_count(first_batch_value_key_audit, "read_status")
    first_batch_key_status_counts = group_count(first_batch_raw_key_audit, "key_audit_status")
    alb2002_core_merge_counts = group_count(alb2002_core_merge_audit, "merge_status")
    alb2002_core_lineage_counts = group_count(alb2002_core_lineage, "status")
    alb2002_outcome_family_counts = group_count(alb2002_outcome_audit, "outcome_family")
    alb2002_outcome_status_counts = group_count(alb2002_outcome_audit, "promotion_status")
    alb2002_semantics_domain_counts = group_count(alb2002_semantics_audit, "outcome_domain")
    alb2002_semantics_promotion_counts = group_count(alb2002_semantics_audit, "promotion_status")
    alb2002_health_questionnaire_family_counts = group_count(alb2002_health_questionnaire_audit, "audit_family")
    alb2002_health_questionnaire_status_counts = group_count(alb2002_health_questionnaire_audit, "semantic_evidence_status")
    alb2002_health_questionnaire_concept_counts = group_count(alb2002_health_questionnaire_audit, "concept")
    alb2002_oop_policy_recall_counts = group_count(alb2002_oop_policy_audit, "recall_scope")
    alb2002_oop_policy_promotion_counts = group_count(alb2002_oop_policy_audit, "promotion_status")
    alb2002_skip_missing_family_counts = group_count(alb2002_skip_missing_audit, "audit_family")
    alb2002_skip_missing_status_counts = group_count(alb2002_skip_missing_audit, "skip_missing_evidence_status")
    alb2002_skip_missing_zero_status_counts = group_count(alb2002_skip_missing_audit, "zero_missing_semantics_status")
    alb2002_oop_skip_value_family_counts = group_count(alb2002_oop_skip_value_audit, "decision_family")
    alb2002_oop_skip_value_promotion_counts = group_count(alb2002_oop_skip_value_audit, "promotion_status")
    alb2002_access_need_family_counts = group_count(alb2002_access_need_audit, "outcome_family")
    alb2002_access_need_denominator_counts = group_count(alb2002_access_need_audit, "denominator_status")
    alb2002_access_need_skip_counts = group_count(alb2002_access_need_audit, "skip_path_status")
    alb2002_consumption_sdg_family_counts = group_count(alb2002_consumption_sdg_audit, "component_family")
    alb2002_consumption_sdg_status_counts = group_count(alb2002_consumption_sdg_audit, "evidence_status")
    alb2002_consumption_construction_family_counts = group_count(alb2002_consumption_construction_audit, "audit_family")
    alb2002_consumption_construction_status_counts = group_count(alb2002_consumption_construction_audit, "evidence_status")
    alb2002_consumption_aggregate_family_counts = group_count(alb2002_consumption_aggregate_audit, "audit_family")
    alb2002_consumption_aggregate_readiness_counts = group_count(alb2002_consumption_aggregate_audit, "readiness_status")
    alb2002_period_aligned_che_policy_counts = group_count(alb2002_period_aligned_che_audit, "policy_name")
    alb2002_period_aligned_che_promotion_counts = group_count(alb2002_period_aligned_che_audit, "promotion_status")
    alb2002_che_candidate_outcome_counts = group_count(alb2002_che_candidate_audit, "outcome_id")
    alb2002_che_candidate_promotion_counts = group_count(alb2002_che_candidate_audit, "promotion_status")
    alb2002_access_candidate_outcome_counts = group_count(alb2002_access_candidate_audit, "outcome_id")
    alb2002_access_candidate_family_counts = group_count(alb2002_access_candidate_audit, "outcome_family")
    alb2002_access_candidate_promotion_counts = group_count(alb2002_access_candidate_audit, "promotion_status")
    alb2002_uhc_composite_outcome_counts = group_count(alb2002_uhc_composite_audit, "outcome_id")
    alb2002_uhc_composite_family_counts = group_count(alb2002_uhc_composite_audit, "outcome_family")
    alb2002_uhc_composite_promotion_counts = group_count(alb2002_uhc_composite_audit, "promotion_status")
    alb2002_analysis_candidate_status_counts = group_count(alb2002_analysis_candidate_audit, "candidate_status")
    alb2002_analysis_candidate_family_counts = group_count(alb2002_analysis_candidate_audit, "field_family")
    alb2002_climate_centroid_status_counts = group_count(alb2002_climate_centroid_audit, "status")
    alb2002_climate_centroid_api_counts = group_count(alb2002_climate_centroid_manifest, "api_status")
    alb2002_climate_shock_status_counts = group_count(alb2002_climate_shock_audit, "status")
    alb2002_climate_shock_lineage_status_counts = group_count(alb2002_climate_shock_lineage, "status")
    alb2002_climate_outcome_linked_status_counts = group_count(alb2002_climate_outcome_linked_audit, "status")
    alb2002_climate_outcome_linked_lineage_status_counts = group_count(alb2002_climate_outcome_linked_lineage, "status")
    alb2002_linked_candidate_descriptive_status_counts = group_count(alb2002_linked_candidate_descriptive_audit, "status")
    alb2002_linked_candidate_descriptive_scope_counts = group_count(alb2002_linked_candidate_descriptive_cells, "diagnostic_scope")
    design_scorecard_current_status_counts = group_count(design_scorecard_current_audit, "status")
    design_no_go_threshold_status_counts = group_count(design_no_go_threshold_audit, "current_status")
    design_no_go_decision_counts = group_count(design_no_go_threshold_audit, "go_no_go")
    alb2002_promotion_gate_delta_status_counts = group_count(alb2002_promotion_gate_delta_audit, "delta_status")
    alb2002_promotion_gate_delta_strength_counts = group_count(alb2002_promotion_gate_delta_audit, "evidence_strength")
    alb2002_boundary_blocker_class_counts = group_count(alb2002_boundary_blocker_matrix, "blocker_class")
    alb2002_boundary_blocker_family_counts = group_count(alb2002_boundary_blocker_matrix, "source_family")
    alb2002_outcome_blocker_family_counts = group_count(alb2002_outcome_blocker_matrix, "outcome_family")
    alb2002_outcome_blocker_status_counts = group_count(alb2002_outcome_blocker_matrix, "promotion_status")
    alb2002_weight_design_status_counts = group_count(alb2002_weight_design_audit, "evidence_status")
    alb2002_sample_design_status_counts = group_count(alb2002_sample_design_audit, "evidence_status")
    alb2002_minimum_recipe_action_status_counts = group_count(alb2002_minimum_recipe_actions, "blocking_status")
    alb2002_minimum_recipe_gate_status_counts = group_count(alb2002_minimum_recipe_gates, "current_status")
    alb2002_minimum_recipe_required_counts = group_count(alb2002_minimum_recipe_gates, "required_for")
    alb2002_crosswalk_status_counts = group_count(alb2002_crosswalk_template, "crosswalk_status")
    alb2002_boundary_probe_counts = group_count(alb2002_boundary_probe, "probe_status")
    alb2002_boundary_name_method_counts = group_count(alb2002_boundary_name_audit, "best_match_method")
    alb2002_boundary_name_status_counts = group_count(alb2002_boundary_name_audit, "match_status")
    alb2002_boundary_source_probe_counts = group_count(alb2002_boundary_source_audit, "probe_status")
    alb2002_boundary_source_suitability_counts = group_count(alb2002_boundary_source_audit, "boundary_suitability_status")
    alb2002_boundary_resource_status_counts = group_count(alb2002_boundary_resource_audit, "resource_status")
    alb2002_boundary_resource_suitability_counts = group_count(alb2002_boundary_resource_audit, "suitability_status")
    alb2002_boundary_geometry_status_counts = group_count(alb2002_boundary_geometry_audit, "geometry_structure_status")
    alb2002_boundary_geometry_match_counts = group_count(alb2002_boundary_geometry_audit, "survey_match_method")
    alb2002_boundary_metadata_status_counts = group_count(alb2002_boundary_metadata_probe, "evidence_status")
    alb2002_boundary_manual_action_status_counts = group_count(alb2002_boundary_manual_actions, "blocking_status")
    alb2002_boundary_manual_gate_status_counts = group_count(alb2002_boundary_manual_gates, "current_status")
    alb2002_boundary_followup_blocker_counts = group_count(alb2002_boundary_followup_audit, "verified_blocker_status")
    alb2002_boundary_followup_level_counts = group_count(alb2002_boundary_followup_audit, "level_compatibility_status")
    alb2002_gadm_status_counts = group_count(alb2002_gadm_audit, "suitability_status")
    alb2002_gadm_match_status_counts = group_count(alb2002_gadm_match_audit, "match_status")
    alb2002_local_geo_artifact_role_counts = group_count(alb2002_local_geo_artifact_audit, "evidence_role")
    alb2002_local_geo_artifact_status_counts = group_count(alb2002_local_geo_artifact_audit, "local_value_status")
    alb2012_core_audit_counts = group_count(alb2012_core_audit, "audit_status")
    alb2012_core_lineage_counts = group_count(alb2012_core_lineage, "status")
    alb2012_outcome_family_counts = group_count(alb2012_outcome_audit, "outcome_family")
    alb2012_outcome_status_counts = group_count(alb2012_outcome_audit, "promotion_status")
    alb2012_semantics_domain_counts = group_count(alb2012_semantics_audit, "outcome_domain")
    alb2012_semantics_promotion_counts = group_count(alb2012_semantics_audit, "promotion_status")
    alb2012_timing_geo_status_counts = group_count(alb2012_timing_geo_audit, "geography_timing_status")
    alb2012_timing_geo_role_counts = group_count(alb2012_timing_geo_audit, "candidate_role")
    alb2012_questionnaire_timing_role_counts = group_count(alb2012_questionnaire_timing_audit, "evidence_role")
    alb2012_questionnaire_timing_promotion_counts = group_count(alb2012_questionnaire_timing_audit, "promotion_status")
    alb2012_questionnaire_raw_gap_role_counts = group_count(alb2012_questionnaire_timing_raw_gap, "raw_gap_role")
    alb2012_blocker_family_counts = group_count(alb2012_blocker_matrix, "blocker_family")
    alb2012_blocker_status_counts = group_count(alb2012_blocker_matrix, "promotion_status")
    albania_legacy_questionnaire_read_counts = group_count(albania_legacy_questionnaire_audit, "read_attempt_status")
    albania_legacy_questionnaire_wave_counts = group_count(albania_legacy_questionnaire_audit, "idno")
    albania_legacy_questionnaire_promotion_counts = group_count(albania_legacy_questionnaire_audit, "promotion_status")
    albania_legacy_questionnaire_timing_role_counts = group_count(albania_legacy_questionnaire_timing_audit, "evidence_role")
    albania_legacy_questionnaire_timing_promotion_counts = group_count(albania_legacy_questionnaire_timing_audit, "promotion_status")
    albania_legacy_questionnaire_raw_gap_role_counts = group_count(albania_legacy_questionnaire_timing_raw_gap, "raw_gap_role")
    alb2005_support_counts = group_count(alb2005_documented_evidence, "documentation_support_status")
    alb2005_decision_counts = group_count(alb2005_documented_evidence, "recipe_decision")
    alb2005_core_merge_counts = group_count(alb2005_core_merge_audit, "merge_status")
    alb2005_core_lineage_counts = group_count(alb2005_core_lineage, "status")
    alb2005_outcome_family_counts = group_count(alb2005_outcome_audit, "outcome_family")
    alb2005_outcome_status_counts = group_count(alb2005_outcome_audit, "promotion_status")
    alb2005_semantics_domain_counts = group_count(alb2005_semantics_audit, "outcome_domain")
    alb2005_semantics_promotion_counts = group_count(alb2005_semantics_audit, "promotion_status")
    alb2005_timing_geo_role_counts = group_count(alb2005_timing_geo_audit, "candidate_role")
    alb2005_timing_geo_status_counts = group_count(alb2005_timing_geo_audit, "geography_timing_status")
    alb2005_timing_geo_source_family_counts = group_count(alb2005_timing_geo_source_audit, "audit_family")
    alb2005_timing_geo_source_status_counts = group_count(alb2005_timing_geo_source_audit, "evidence_status")
    alb2005_timing_geo_source_promotion_counts = group_count(alb2005_timing_geo_source_audit, "promotion_status")
    alb2005_value_decision_status_counts = group_count(alb2005_value_decision_audit, "decision_status")
    alb2005_value_decision_role_counts = group_count(alb2005_value_decision_audit, "minimum_recipe_role")
    alb2005_value_decision_concept_counts = group_count(alb2005_value_decision_audit, "concept")
    alb2005_required_value_key_concept_counts = group_count(alb2005_required_value_key_audit, "concept")
    alb2005_required_value_key_coverage_counts = group_count(alb2005_required_value_key_audit, "coverage_status")
    alb2005_required_value_key_value_counts = group_count(alb2005_required_value_key_audit, "value_status")
    alb2005_health_questionnaire_concept_counts = group_count(alb2005_health_questionnaire_audit, "concept")
    alb2005_health_questionnaire_status_counts = group_count(alb2005_health_questionnaire_audit, "semantic_evidence_status")
    alb2005_health_questionnaire_promotion_counts = group_count(alb2005_health_questionnaire_audit, "promotion_status")
    alb2005_oop_policy_recall_counts = group_count(alb2005_oop_policy_audit, "recall_scope")
    alb2005_oop_policy_promotion_counts = group_count(alb2005_oop_policy_audit, "promotion_status")
    alb2005_skip_missing_family_counts = group_count(alb2005_skip_missing_audit, "audit_family")
    alb2005_skip_missing_status_counts = group_count(alb2005_skip_missing_audit, "skip_missing_evidence_status")
    alb2005_skip_missing_promotion_counts = group_count(alb2005_skip_missing_audit, "promotion_status")
    alb2005_unit_period_family_counts = group_count(alb2005_unit_period_audit, "audit_family")
    alb2005_unit_period_status_counts = group_count(alb2005_unit_period_audit, "evidence_status")
    alb2005_unit_period_promotion_counts = group_count(alb2005_unit_period_audit, "promotion_status")
    alb2005_aggregate_crosswalk_family_counts = group_count(alb2005_aggregate_crosswalk_audit, "audit_family")
    alb2005_aggregate_crosswalk_status_counts = group_count(alb2005_aggregate_crosswalk_audit, "readiness_status")
    alb2005_aggregate_crosswalk_promotion_counts = group_count(alb2005_aggregate_crosswalk_audit, "promotion_status")
    alb2005_component_source_family_counts = group_count(alb2005_component_source_audit, "audit_family")
    alb2005_component_source_status_counts = group_count(alb2005_component_source_audit, "evidence_status")
    alb2005_component_source_promotion_counts = group_count(alb2005_component_source_audit, "promotion_status")
    alb2005_minimum_recipe_action_status_counts = group_count(alb2005_minimum_recipe_actions, "blocking_status")
    alb2005_minimum_recipe_gate_status_counts = group_count(alb2005_minimum_recipe_gates, "current_status")
    alb2005_minimum_recipe_required_counts = group_count(alb2005_minimum_recipe_gates, "required_for")
    alb2005_public_fieldwork_geo_domain_counts = group_count(alb2005_public_fieldwork_geo_audit, "evidence_domain")
    alb2005_public_fieldwork_geo_source_counts = group_count(alb2005_public_fieldwork_geo_audit, "source_status")
    alb2005_public_fieldwork_geo_promotion_counts = group_count(alb2005_public_fieldwork_geo_audit, "promotion_status")
    alb2005_diary_timing_role_counts = group_count(alb2005_diary_timing_audit, "concept_role")
    alb2005_diary_timing_catalog_counts = group_count(alb2005_diary_timing_audit, "metadata_catalog_status")
    alb2005_diary_timing_promotion_counts = group_count(alb2005_diary_timing_audit, "promotion_status")
    alb2005_extracted_module_role_counts = group_count(alb2005_extracted_module_audit, "module_role")
    alb2005_extracted_module_coverage_counts = group_count(alb2005_extracted_module_audit, "coverage_status")
    alb2005_extracted_module_archive_counts = group_count(alb2005_extracted_module_audit, "archive_coverage_status")
    alb2005_archive_member_ext_counts = group_count(alb2005_archive_member_manifest, "member_ext")
    alb2005_archive_member_type_counts = group_count(alb2005_archive_member_manifest, "archive_member_type")
    alb2005_extracted_extra_counts = group_count(alb2005_extracted_extra_audit, "coverage_status")
    alb2005_fallback_blocker_family_counts = group_count(alb2005_fallback_blocker_matrix, "blocker_family")
    alb2005_fallback_blocker_status_counts = group_count(alb2005_fallback_blocker_matrix, "promotion_status")
    albania_first_analysis_gate_counts = group_count(albania_first_analysis_gate, "gate_status")
    albania_first_analysis_action_counts = group_count(albania_first_analysis_actions, "action_status")
    albania_first_analysis_decision_counts = group_count(albania_first_analysis_waves, "current_decision")
    albania_wave_schema_counts = group_count(albania_wave_audit, "schema_inventory_status")
    albania_wave_current_status_counts = group_count(albania_wave_audit, "current_status")
    albania_wave_promotion_counts = group_count(albania_wave_audit, "promotion_status")
    alb2008_core_merge_counts = group_count(alb2008_core_merge_audit, "merge_status")
    alb2008_core_lineage_counts = group_count(alb2008_core_lineage, "status")
    alb2008_outcome_family_counts = group_count(alb2008_outcome_audit, "outcome_family")
    alb2008_outcome_status_counts = group_count(alb2008_outcome_audit, "promotion_status")
    alb2008_semantics_domain_counts = group_count(alb2008_semantics_audit, "outcome_domain")
    alb2008_semantics_promotion_counts = group_count(alb2008_semantics_audit, "promotion_status")
    alb2008_timing_geo_role_counts = group_count(alb2008_timing_geo_audit, "candidate_role")
    alb2008_timing_geo_status_counts = group_count(alb2008_timing_geo_audit, "geography_timing_status")
    alb2008_fallback_blocker_family_counts = group_count(alb2008_fallback_blocker_matrix, "blocker_family")
    alb2008_fallback_blocker_status_counts = group_count(alb2008_fallback_blocker_matrix, "promotion_status")
    first_batch_dataset_gate_counts = group_count(first_batch_dataset_gate, "current_gate_status")
    first_batch_concept_gate_counts = group_count(first_batch_concept_template, "current_concept_gate")
    first_batch_variable_status_counts = group_count(first_batch_variable_template, "verification_status")
    raw_download_role_counts = group_count(raw_download_manifest, "file_role")
    raw_download_target_status_counts = group_count(raw_download_targets, "status")
    raw_ingestion_gate_counts = group_count(raw_ingestion_plan, "ingestion_gate_status")
    raw_variable_protocol_status_counts = group_count(raw_variable_protocol, "verification_status")
    raw_variable_protocol_file_counts = group_count(raw_variable_protocol, "raw_file_status")
    raw_variable_protocol_concept_counts = group_count(raw_variable_protocol, "concept")
    harmonization_recipe_gate_counts = group_count(harmonization_recipe_gate, "recipe_gate_status")
    harmonization_recipe_source_counts = group_count(harmonization_recipe_gate, "source_file_status")
    harmonization_recipe_variable_counts = group_count(harmonization_recipe_gate, "raw_variable_status")
    harmonization_recipe_value_counts = group_count(harmonization_recipe_gate, "value_audit_status")
    harmonization_readiness_counts = group_count(harmonization_readiness, "readiness_status")
    analysis_dataset_promotion_blocker_counts = group_count(analysis_dataset_promotion_audit, "blocking_status")
    analysis_dataset_promotion_decision_counts = group_count(analysis_dataset_promotion_audit, "promotion_decision")
    minimum_viable_set_counts = group_count(minimum_viable_targets, "acquisition_set")
    minimum_viable_country_counts = group_count(minimum_viable_targets, "country")
    minimum_viable_tier_counts = group_count(minimum_viable_targets, "quality_download_priority_tier")
    raw_status_counts = group_count(raw_files, "status")
    harmonization_status_counts = group_count(harmonization_audit, "status")
    climate_status_counts = group_count(climate_audit, "status")
    climate_source_status_counts = group_count(climate_source_probe, "status")
    climate_source_role_counts = group_count(climate_source_probe, "source_role")
    climate_exposure_plan_gate_counts = group_count(climate_exposure_plan, "climate_linkage_gate_status")
    climate_exposure_spec_status_counts = group_count(climate_exposure_spec, "current_status")
    climate_validation_requirement_gate_counts = group_count(climate_linkage_requirements, "current_gate_status")
    climate_validation_readiness_counts = group_count(climate_linkage_readiness, "readiness_status")
    climate_validation_protocol_counts = group_count(climate_exposure_validation_protocol, "current_status")
    climate_source_method_status_counts = group_count(climate_source_method_matrix, "probe_status")
    climate_merge_status_counts = group_count(climate_merge_audit, "status")
    outcome_status_counts = group_count(outcome_audit, "status")
    outcome_construct_status_counts = group_count(outcome_construct_audit, "status")
    outcome_plan_gate_counts = group_count(outcome_denominator_plan, "outcome_gate_status")
    outcome_plan_family_counts = group_count(outcome_denominator_plan, "outcome_family")
    sdg382_component_gate_counts = group_count(sdg382_denominator_requirements, "current_gate_status")
    sdg382_readiness_counts = group_count(sdg382_denominator_readiness, "readiness_status")
    sdg382_source_status_counts = group_count(sdg382_denominator_sources, "probe_status")
    modeling_predictive_gate_counts = group_count(modeling_identification_plan, "predictive_ml_gate_status")
    modeling_reduced_form_gate_counts = group_count(modeling_identification_plan, "reduced_form_gate_status")
    modeling_causal_ml_gate_counts = group_count(modeling_identification_plan, "causal_ml_policy_gate_status")
    modeling_policy_gate_counts = group_count(modeling_identification_plan, "policy_learning_gate_status")
    modeling_validation_status_counts = group_count(modeling_validation_plan, "current_status")
    falsification_plan_status_counts = group_count(falsification_placebo_plan, "current_status")
    policy_learning_plan_status_counts = group_count(policy_learning_plan, "current_status")
    mechanism_requirement_gate_counts = group_count(mechanism_requirements, "current_gate_status")
    mechanism_readiness_counts = group_count(mechanism_readiness, "readiness_status")
    mechanism_pathway_counts = group_count(mechanism_readiness, "mechanism_pathway")
    empirical_stage_counts = group_count(empirical_dashboard, "current_stage")
    empirical_claim_counts = group_count(empirical_dashboard, "analysis_claim_status")
    empirical_no_go_status_counts = group_count(empirical_no_go, "status")
    direct_read_section_counts = group_count(direct_read_bundle, "section")
    direct_read_status_counts = group_count(direct_read_bundle, "status")
    direct_read_manifest_status_counts = group_count(direct_read_manifest, "current_status")
    objective_traceability_status_counts = group_count(objective_traceability, "status")
    objective_guardrail_status_counts = group_count(objective_guardrails, "status")
    python_package_installed_counts = group_count(python_package_inventory, "import_check")
    python_package_level_counts = group_count(python_package_inventory, "requirement_level")
    python_environment_audit_status_counts = group_count(python_environment_audit, "status")
    validation_reference_status_counts = group_count(validation_reference_probe, "status")
    validation_reference_role_counts = group_count(validation_reference_probe, "source_role")
    validation_reference_indicator_counts = group_count(
        [r for r in validation_reference_samples if r.get("status") == "sample_record"],
        "indicator",
    )
    hefpi_uhc_indicator_counts = group_count(
        [r for r in hefpi_uhc_reference if r.get("status") == "hefpi_uhc_reference_record"],
        "indicator_code",
    )
    descriptive_status_counts = group_count(descriptive_audit, "status")
    sample_gate_status_counts = group_count(sample_gate, "status")
    variable_confidence_counts = group_count(variable_confidence, "metadata_confidence")
    metadata_quality_tier_counts = group_count(metadata_quality, "quality_download_priority_tier")
    predictive_status_counts = group_count(predictive_audit, "status")
    causal_model_status_counts = group_count(causal_model_audit, "status")
    placebo_status_counts = group_count(placebo_readiness, "status")
    causal_ml_status_counts = group_count(causal_ml_policy_audit, "status")
    robustness_status_counts = group_count(robustness_audit, "status")
    robustness_result_status_counts = group_count(robustness_results, "status")
    design_go_counts = group_count(designs, "go/no-go")
    outcome_validity_counts = group_count(designs, "outcome_validity")
    health_exp = read_csv_dicts(TEMP_DIR / "variable_map_health_expenditure.csv")
    health_exp_counts = group_count(health_exp, "harmonized_variable")

    map_table = "\n".join(f"| `{name}` | {count} |" for name, count in sorted(map_counts.items()))
    if predictive_metrics:
        predictive_rejected_for_now_line = (
            f"- Predictive ML has been estimated only as a limited ALB_2002 CHE diagnostic with "
            f"{len(predictive_metrics)} grouped-admin2 validation metric rows. It is not deployable "
            "or transportable, and promoted multi-country predictive ML remains blocked."
        )
        predictive_summary_sentence = (
            "However, limited ALB_2002 CHE predictive, reduced-form association, and robustness diagnostics "
            "now exist, and they are explicitly not deployable, transportable, causal, or policy-ready. "
            "Verified harmonization, final raw value/unit/recall-period checks, promoted climate linkage, "
            "causal estimates, and policy-learning results are still missing."
        )
        predictive_empirical_judgment = (
            "No go for SDG 3.8.2, access, composite UHC, promoted climate linkage, deployable or "
            "transportable predictive ML, reduced-form causal estimates, mechanism analysis, causal ML, "
            "or policy learning. The limited ALB_2002 CHE climate-linked file supports descriptive and "
            "predictive diagnostics, reduced-form association diagnostics, and limited robustness/placebo "
            "attempts only; it is not a promoted analysis-ready dataset."
        )
    else:
        predictive_rejected_for_now_line = "- Predictive ML is rejected until audited outcome data and non-random validation splits exist."
        predictive_summary_sentence = (
            "However, verified harmonization, final raw value/unit/recall-period checks, promoted climate "
            "linkage, final outcome event rates, predictive models, causal estimates, and policy-learning "
            "results are still missing."
        )
        predictive_empirical_judgment = (
            "No go for SDG 3.8.2, access, composite UHC, climate linkage, descriptive prevalence, "
            "predictive ML, reduced-form causal estimates, mechanism analysis, causal ML, or policy "
            "learning. The limited CHE outcomes are not climate-linked or model-ready. The evidence "
            "currently supports a stronger screening/acquisition/raw-schema/raw-value-summary layer plus "
            "limited ALB_2002 financial-protection outcome inspection, not a publishable empirical result."
        )

    outcome_report = REPORT_DIR / "outcome_construction.md"
    outcome_report.write_text(
        f"""# Outcome Construction

Status: limited ALB_2002 CHE-only financial-protection outcomes constructed and audited. SDG 3.8.2, access, composite UHC, climate-linked, and model-ready outcomes remain blocked.

Input for final outcomes: `data/harmonized_household.csv` or equivalent harmonized analytical data.

Final outcome rows currently present: {len(household_outcomes)}

## Official Financial-Protection Definitions

| Outcome | Formula | Current status |
|---|---|---|
| `sdg382_discretionary_40` | OOP health expenditure > 40% of household discretionary budget | blocked until OOP, household discretionary budget, poverty-line/PPP/CPI handling, units, and recall periods are verified |
| `che10_total_budget` | OOP health expenditure > 10% of total consumption/income | limited ALB_2002 CHE-only outcome promoted from period-aligned OOP and documented monthly total-budget candidate |
| `che25_total_budget` | OOP health expenditure > 25% of total consumption/income | limited ALB_2002 CHE-only outcome promoted from period-aligned OOP and documented monthly total-budget candidate |
| `capacity_to_pay_40` | OOP health expenditure > 40% of capacity to pay | blocked until capacity-to-pay denominator is verified |
| `impoverishing_health_spending` | household is above poverty line before OOP and below after OOP | blocked until poverty-line denominator and OOP timing are verified |

## Constructed Outcomes

| Outcome | Current status |
|---|---|
| `che10_total_budget` | limited CHE-only ALB_2002 outcome; rows={stats['alb2002_limited_financial_outcome_rows']}; CHE10 rows={stats['alb2002_limited_financial_outcome_che10_rows']}; weighted rate={stats['alb2002_limited_financial_outcome_che10_weighted_rate']} |
| `che25_total_budget` | limited CHE-only ALB_2002 outcome; rows={stats['alb2002_limited_financial_outcome_rows']}; CHE25 rows={stats['alb2002_limited_financial_outcome_che25_rows']}; weighted rate={stats['alb2002_limited_financial_outcome_che25_weighted_rate']} |
| `oop_share_total` and `log_oop_plus_one` | limited ALB_2002 continuous financial-protection outcomes |
| SDG 3.8.2, access, composite, and coping outcomes | blocked; SDG/access/composite-ready rows={stats['alb2002_limited_financial_outcome_sdg382_ready_rows']}/{stats['alb2002_limited_financial_outcome_access_ready_rows']}/{stats['alb2002_limited_financial_outcome_composite_ready_rows']} |

The limited outcome file is `data/household_outcomes.csv`; every row carries guardrail markers showing that climate-linkage-ready and final-analysis-ready rows remain {stats['alb2002_limited_financial_outcome_climate_linkage_ready_rows']} and {stats['alb2002_limited_financial_outcome_final_analysis_ready_rows']}.

## Provisional Raw Diagnostics

| Wave | Audit rows | Financial stress-test rows | Access proxy rows | Low-event rows | Promotion-ready rows | Decision |
|---|---:|---:|---:|---:|---:|---|
| ALB_2002 | {stats['alb2002_provisional_outcome_audit_rows']} | {stats['alb2002_provisional_financial_stress_test_rows']} | {stats['alb2002_provisional_access_proxy_rows']} | {stats['alb2002_provisional_low_event_rate_rows']} | {stats['alb2002_provisional_outcome_ready_rows']} | {stats['alb2002_provisional_outcome_current_decision']} |
| ALB_2012 | {stats['alb2012_provisional_outcome_audit_rows']} | {stats['alb2012_provisional_financial_stress_test_rows']} | {stats['alb2012_provisional_access_proxy_rows']} | {stats['alb2012_provisional_low_event_rate_rows']} | {stats['alb2012_provisional_outcome_ready_rows']} | {stats['alb2012_provisional_outcome_current_decision']} |
| ALB_2005 | {stats['alb2005_provisional_outcome_audit_rows']} | {stats['alb2005_provisional_financial_stress_test_rows']} | {stats['alb2005_provisional_access_proxy_rows']} | {stats['alb2005_provisional_low_event_rate_rows']} | {stats['alb2005_provisional_outcome_ready_rows']} | {stats['alb2005_provisional_outcome_current_decision']} |
| ALB_2008 | {stats['alb2008_provisional_outcome_audit_rows']} | {stats['alb2008_provisional_financial_stress_test_rows']} | {stats['alb2008_provisional_access_proxy_rows']} | {stats['alb2008_provisional_low_event_rate_rows']} | {stats['alb2008_provisional_outcome_ready_rows']} | {stats['alb2008_provisional_outcome_current_decision']} |

Machine-readable provisional diagnostics:

- `temp/alb2002_provisional_outcome_feasibility_audit.csv`
- `temp/alb2002_outcome_semantics_raw_value_audit.csv`
- `temp/alb2002_health_questionnaire_semantics_audit.csv`
- `temp/alb2012_provisional_outcome_feasibility_audit.csv`
- `temp/alb2012_outcome_semantics_raw_value_audit.csv`
- `temp/alb2005_provisional_outcome_feasibility_audit.csv`
- `temp/alb2005_outcome_semantics_raw_value_audit.csv`
- `temp/alb2005_oop_aggregation_policy_audit.csv`
- `temp/alb2005_skip_missing_semantics_audit.csv`
- `temp/alb2005_consumption_oop_unit_period_audit.csv`
- `temp/alb2005_consumption_aggregate_metadata_crosswalk_audit.csv`
- `temp/alb2005_consumption_component_source_search_audit.csv`
- `temp/alb2005_timing_geography_source_search_audit.csv`
- `temp/alb2008_provisional_outcome_feasibility_audit.csv`
- `temp/alb2008_outcome_semantics_raw_value_audit.csv`

## ALB_2002 Raw Outcome Semantics Audit

| Metric | Value |
|---|---:|
| Raw value/semantics rows | {stats['alb2002_outcome_semantics_raw_value_rows']} |
| Source health modules scanned | {stats['alb2002_outcome_semantics_source_files_scanned']} |
| Financial OOP candidate rows | {stats['alb2002_outcome_semantics_financial_oop_candidate_rows']} |
| Access candidate rows | {stats['alb2002_outcome_semantics_access_candidate_rows']} |
| Need proxy rows | {stats['alb2002_outcome_semantics_need_candidate_rows']} |
| Rows with value labels | {stats['alb2002_outcome_semantics_rows_with_value_labels']} |
| Conditional reason rows | {stats['alb2002_outcome_semantics_conditional_reason_rows']} |
| Outcome-ready rows | {stats['alb2002_outcome_semantics_outcome_ready_rows']} |
| SDG 3.8.2-ready rows | {stats['alb2002_outcome_semantics_sdg382_ready_rows']} |
| Decision | {stats['alb2002_outcome_semantics_current_decision']} |

`report/alb2002_outcome_semantics_raw_value_audit.md` documents raw labels, observed values, value-label examples, merge-key coverage, and skip-pattern blockers for ALB_2002 health OOP/access candidates. It strengthens the raw evidence trail but does not promote CHE, SDG 3.8.2, forgone-care, composite, climate-linked, descriptive, causal, ML, or policy outcomes.

## ALB_2002 Health Questionnaire Semantics Audit

| Metric | Value |
|---|---:|
| Questionnaire/skip-path rows | {stats['alb2002_health_questionnaire_semantics_rows']} |
| OOP item rows | {stats['alb2002_health_questionnaire_oop_item_rows']} |
| Gift/payment-scope rows | {stats['alb2002_health_questionnaire_gift_item_rows']} |
| NEW LEKS unit rows | {stats['alb2002_health_questionnaire_new_lek_unit_rows']} |
| Four-week OOP rows | {stats['alb2002_health_questionnaire_four_week_oop_rows']} |
| Twelve-month OOP rows | {stats['alb2002_health_questionnaire_twelve_month_oop_rows']} |
| Exclusion-note rows | {stats['alb2002_health_questionnaire_exclusion_note_rows']} |
| Zero-instruction rows | {stats['alb2002_health_questionnaire_zero_instruction_rows']} |
| Access-barrier rows | {stats['alb2002_health_questionnaire_access_rows']} |
| Cost-barrier rows | {stats['alb2002_health_questionnaire_cost_barrier_rows']} |
| Distance-barrier rows | {stats['alb2002_health_questionnaire_distance_barrier_rows']} |
| Supply-barrier rows | {stats['alb2002_health_questionnaire_supply_barrier_rows']} |
| Payment skip-path rows | {stats['alb2002_health_questionnaire_payment_skip_rows']} |
| Nonmissing downstream payment rows when not triggered | {stats['alb2002_health_questionnaire_payment_nonmissing_when_not_triggered_rows']} |
| Positive downstream payment rows when not triggered | {stats['alb2002_health_questionnaire_payment_positive_when_not_triggered_rows']} |
| Zero-or-missing downstream payment rows when triggered | {stats['alb2002_health_questionnaire_payment_zero_or_missing_when_triggered_rows']} |
| Conditional skip rows | {stats['alb2002_health_questionnaire_conditional_skip_rows']} |
| Conditional nonmissing rows when not triggered | {stats['alb2002_health_questionnaire_conditional_nonmissing_when_not_triggered_rows']} |
| Conditional missing rows when triggered | {stats['alb2002_health_questionnaire_conditional_missing_when_triggered_rows']} |
| Recipe-ready rows | {stats['alb2002_health_questionnaire_recipe_ready_rows']} |
| Outcome-ready rows | {stats['alb2002_health_questionnaire_outcome_ready_rows']} |
| SDG 3.8.2-ready rows | {stats['alb2002_health_questionnaire_sdg382_ready_rows']} |
| Climate-linkage-ready rows | {stats['alb2002_health_questionnaire_climate_linkage_ready_rows']} |
| Decision | {stats['alb2002_health_questionnaire_current_decision']} |

{markdown_count_table(alb2002_health_questionnaire_family_counts, 'ALB_2002 health questionnaire audit family') if alb2002_health_questionnaire_audit else 'No ALB_2002 health questionnaire semantics audit exists yet.'}

{markdown_count_table(alb2002_health_questionnaire_status_counts, 'ALB_2002 health questionnaire semantic evidence status') if alb2002_health_questionnaire_audit else 'No ALB_2002 health questionnaire semantic-status rows exist yet.'}

{markdown_count_table(alb2002_health_questionnaire_concept_counts, 'ALB_2002 health questionnaire concept') if alb2002_health_questionnaire_audit else 'No ALB_2002 health questionnaire concept rows exist yet.'}

`report/alb2002_health_questionnaire_semantics_audit.md` documents questionnaire-backed NEW LEKS payment-unit evidence, mixed four-week and twelve-month OOP recall, gift/payment-scope rows, access-barrier codes, and raw skip-path consistency. It confirms no positive downstream payment values when visit triggers are negative, but keeps ALB_2002 outcome promotion blocked because denominator semantics, the separate OOP skip-value decision, SDG 3.8.2 construction, and district climate linkage are still unresolved.

## ALB_2002 OOP Aggregation Policy Audit

| Metric | Value |
|---|---:|
| Policy stress-test rows | {stats['alb2002_oop_aggregation_policy_rows']} |
| Household rows | {stats['alb2002_oop_aggregation_policy_household_rows']} |
| Positive total-consumption rows | {stats['alb2002_oop_aggregation_policy_total_consumption_rows']} |
| Four-week policy rows | {stats['alb2002_oop_aggregation_policy_four_week_policy_rows']} |
| Twelve-month policy rows | {stats['alb2002_oop_aggregation_policy_twelve_month_policy_rows']} |
| Annualized stress rows | {stats['alb2002_oop_aggregation_policy_annual_stress_rows']} |
| Maximum CHE10 stress-test rate | {stats['alb2002_oop_aggregation_policy_max_che10_rate']} |
| Maximum CHE25 stress-test rate | {stats['alb2002_oop_aggregation_policy_max_che25_rate']} |
| Core four-week OOP match rows | {stats['alb2002_oop_aggregation_policy_core_4w_match_rows']} |
| Core twelve-month OOP match rows | {stats['alb2002_oop_aggregation_policy_core_12m_match_rows']} |
| Outcome-ready rows | {stats['alb2002_oop_aggregation_policy_outcome_ready_rows']} |
| Recipe-ready rows | {stats['alb2002_oop_aggregation_policy_recipe_ready_rows']} |
| SDG 3.8.2-ready rows | {stats['alb2002_oop_aggregation_policy_sdg382_ready_rows']} |
| Climate-linkage-ready rows | {stats['alb2002_oop_aggregation_policy_climate_linkage_ready_rows']} |
| Decision | {stats['alb2002_oop_aggregation_policy_current_decision']} |

{markdown_count_table(alb2002_oop_policy_recall_counts, 'ALB_2002 OOP policy recall scope') if alb2002_oop_policy_audit else 'No ALB_2002 OOP aggregation policy audit exists yet.'}

{markdown_count_table(alb2002_oop_policy_promotion_counts, 'ALB_2002 OOP policy promotion status') if alb2002_oop_policy_audit else 'No ALB_2002 OOP policy promotion-status rows exist yet.'}

`report/alb2002_oop_aggregation_policy_audit.md` stress-tests four-week, twelve-month, and annualized ALB_2002 OOP inclusion policies against the verified household denominator. It confirms the recomputed four-week and twelve-month core sums match the existing candidate rows, but it is explicitly not final outcome construction. Outcome, recipe, SDG 3.8.2, and climate-linkage promotion remain blocked until OOP scope, recall comparability, skipped-payment semantics, denominator construction, and district climate geography are resolved.

## ALB_2002 Skip And Missing-Code Semantics Audit

| Metric | Value |
|---|---:|
| Skip/missing audit rows | {stats['alb2002_skip_missing_semantics_rows']} |
| Payment skip blocks | {stats['alb2002_skip_missing_payment_block_rows']} |
| Access/financing condition blocks | {stats['alb2002_skip_missing_access_condition_rows']} |
| Nonmissing skipped-payment rows | {stats['alb2002_skip_missing_payment_nonmissing_when_not_triggered_rows']} |
| Positive skipped-payment rows | {stats['alb2002_skip_missing_payment_positive_when_not_triggered_rows']} |
| Nonmissing skipped-payment cells | {stats['alb2002_skip_missing_payment_nonmissing_cells_when_not_triggered']} |
| Zero skipped-payment cells | {stats['alb2002_skip_missing_payment_zero_cells_when_not_triggered']} |
| Positive skipped-payment cells | {stats['alb2002_skip_missing_payment_positive_cells_when_not_triggered']} |
| Zero-only payment skip blocks | {stats['alb2002_skip_missing_payment_zero_only_block_rows']} |
| No-skipped-value payment blocks | {stats['alb2002_skip_missing_payment_no_skipped_value_block_rows']} |
| Access/financing nonmissing rows when not triggered | {stats['alb2002_skip_missing_condition_nonmissing_when_not_triggered_rows']} |
| Access/financing missing rows when triggered | {stats['alb2002_skip_missing_condition_missing_when_triggered_rows']} |
| Outcome-ready rows | {stats['alb2002_skip_missing_outcome_ready_rows']} |
| Recipe-ready rows | {stats['alb2002_skip_missing_recipe_ready_rows']} |
| SDG 3.8.2-ready rows | {stats['alb2002_skip_missing_sdg382_ready_rows']} |
| Climate-linkage-ready rows | {stats['alb2002_skip_missing_climate_linkage_ready_rows']} |
| Decision | {stats['alb2002_skip_missing_current_decision']} |

{markdown_count_table(alb2002_skip_missing_family_counts, 'ALB_2002 skip/missing audit family') if alb2002_skip_missing_audit else 'No ALB_2002 skip/missing semantics audit exists yet.'}

{markdown_count_table(alb2002_skip_missing_status_counts, 'ALB_2002 skip/missing evidence status') if alb2002_skip_missing_audit else 'No ALB_2002 skip/missing evidence-status rows exist yet.'}

{markdown_count_table(alb2002_skip_missing_zero_status_counts, 'ALB_2002 zero/missing semantics status') if alb2002_skip_missing_audit else 'No ALB_2002 zero/missing semantics rows exist yet.'}

`report/alb2002_skip_missing_semantics_audit.md` documents that nonmissing skipped downstream payment values are zero-only and that positive skipped-payment rows/cells remain zero. The downstream skip-value decision audit records the no-positive-leakage decision before any OOP, CHE, SDG 3.8.2, access, recipe, or climate-linked outcome can be promoted.

## ALB_2002 OOP Skip-Value Decision Audit

| Metric | Value |
|---|---:|
| Decision audit rows | {stats['alb2002_oop_skip_value_decision_rows']} |
| Payment skip blocks | {stats['alb2002_oop_skip_value_payment_block_rows']} |
| Access condition blocks | {stats['alb2002_oop_skip_value_access_condition_block_rows']} |
| Nonmissing skipped-payment rows | {stats['alb2002_oop_skip_value_payment_nonmissing_skipped_rows']} |
| Nonmissing skipped-payment cells | {stats['alb2002_oop_skip_value_payment_nonmissing_skipped_cells']} |
| Zero skipped-payment cells | {stats['alb2002_oop_skip_value_payment_zero_skipped_cells']} |
| Positive skipped-payment rows | {stats['alb2002_oop_skip_value_payment_positive_skipped_rows']} |
| Positive skipped-payment cells | {stats['alb2002_oop_skip_value_payment_positive_skipped_cells']} |
| Zero-skip policy-ready rows | {stats['alb2002_oop_skip_value_zero_skip_policy_ready_rows']} |
| OOP recall-scope-ready rows | {stats['alb2002_oop_skip_value_oop_recall_scope_ready_rows']} |
| OOP inclusion-scope-ready rows | {stats['alb2002_oop_skip_value_oop_inclusion_scope_ready_rows']} |
| Recipe-ready rows | {stats['alb2002_oop_skip_value_recipe_ready_rows']} |
| Outcome-ready rows | {stats['alb2002_oop_skip_value_outcome_ready_rows']} |
| SDG 3.8.2-ready rows | {stats['alb2002_oop_skip_value_sdg382_ready_rows']} |
| Climate-linkage-ready rows | {stats['alb2002_oop_skip_value_climate_linkage_ready_rows']} |
| Decision | {stats['alb2002_oop_skip_value_current_decision']} |

{markdown_count_table(alb2002_oop_skip_value_family_counts, 'ALB_2002 OOP skip-value decision family') if alb2002_oop_skip_value_audit else 'No ALB_2002 OOP skip-value decision audit exists yet.'}

{markdown_count_table(alb2002_oop_skip_value_promotion_counts, 'ALB_2002 OOP skip-value promotion status') if alb2002_oop_skip_value_audit else 'No ALB_2002 OOP skip-value promotion rows exist yet.'}

`report/alb2002_oop_skip_value_decision_audit.md` documents the narrow skipped-payment decision: nontriggered downstream payment cells have no positive leakage, so zero-coded skipped cells do not add positive OOP in stress-test aggregation. It does not choose the final OOP recall period, gift/transport inclusion scope, annualization rule, or household aggregation policy, so all recipe, outcome, SDG 3.8.2, and climate-linkage readiness rows remain zero.

## ALB_2002 Access And Need Denominator Policy Audit

| Metric | Value |
|---|---:|
| Access/need policy rows | {stats['alb2002_access_need_denominator_policy_rows']} |
| Household rows | {stats['alb2002_access_need_household_rows']} |
| Person-level illness/need households | {stats['alb2002_access_need_person_need_household_rows']} |
| q01 broad need rows | {stats['alb2002_access_need_q01_need_rows']} |
| q01 cost difficulty rows | {stats['alb2002_access_need_q01_cost_difficulty_rows']} |
| Delayed help rows | {stats['alb2002_access_need_delayed_help_rows']} |
| Referral not gone rows | {stats['alb2002_access_need_referral_not_gone_rows']} |
| Refused service rows | {stats['alb2002_access_need_refused_service_rows']} |
| Medicine discount any-barrier rows | {stats['alb2002_access_need_medicine_discount_any_barrier_rows']} |
| Composite cost-barrier rows | {stats['alb2002_access_need_composite_cost_barrier_rows']} |
| Composite distance-barrier rows | {stats['alb2002_access_need_composite_distance_barrier_rows']} |
| Composite supply/admin-barrier rows | {stats['alb2002_access_need_composite_supply_admin_barrier_rows']} |
| Composite any-access-barrier rows | {stats['alb2002_access_need_composite_any_access_barrier_rows']} |
| Low-event-rate policy rows | {stats['alb2002_access_need_low_event_rate_rows']} |
| Outcome-ready rows | {stats['alb2002_access_need_outcome_ready_rows']} |
| Recipe-ready rows | {stats['alb2002_access_need_recipe_ready_rows']} |
| SDG 3.8.2-ready rows | {stats['alb2002_access_need_sdg382_ready_rows']} |
| Climate-linkage-ready rows | {stats['alb2002_access_need_climate_linkage_ready_rows']} |
| Decision | {stats['alb2002_access_need_current_decision']} |

{markdown_count_table(alb2002_access_need_family_counts, 'ALB_2002 access/need outcome family') if alb2002_access_need_audit else 'No ALB_2002 access/need denominator policy audit exists yet.'}

{markdown_count_table(alb2002_access_need_denominator_counts, 'ALB_2002 access/need denominator status') if alb2002_access_need_audit else 'No ALB_2002 access/need denominator-status rows exist yet.'}

{markdown_count_table(alb2002_access_need_skip_counts, 'ALB_2002 access/need skip-path status') if alb2002_access_need_audit else 'No ALB_2002 access/need skip-path rows exist yet.'}

`report/alb2002_access_need_denominator_policy_audit.md` separates broad household need, person-level illness need, delayed care, referral nonuse, refusal, medicine-discount access, and cost/distance/supply-admin barrier candidates. It records usable event-rate diagnostics but keeps every access, recipe, SDG 3.8.2, and climate-linkage promotion flag at zero until a denominator policy is explicitly accepted.

## ALB_2002 Consumption And SDG Denominator Policy Audit

| Metric | Value |
|---|---:|
| Denominator policy rows | {stats['alb2002_consumption_sdg_denominator_policy_rows']} |
| Household rows | {stats['alb2002_consumption_sdg_household_rows']} |
| Positive total-consumption rows | {stats['alb2002_consumption_sdg_positive_total_consumption_rows']} |
| Positive household-weight rows | {stats['alb2002_consumption_sdg_positive_household_weight_rows']} |
| Positive household-size rows | {stats['alb2002_consumption_sdg_positive_household_size_rows']} |
| Median total consumption | {stats['alb2002_consumption_sdg_total_consumption_p50']} |
| 95th percentile total consumption | {stats['alb2002_consumption_sdg_total_consumption_p95']} |
| Diagnostic CHE10 rate, four-week unreviewed OOP | {stats['alb2002_consumption_sdg_che10_4w_unreviewed_rate']} |
| Diagnostic CHE25 rate, four-week unreviewed OOP | {stats['alb2002_consumption_sdg_che25_4w_unreviewed_rate']} |
| Diagnostic CHE10 rate, twelve-month unreviewed OOP | {stats['alb2002_consumption_sdg_che10_12m_unreviewed_rate']} |
| Diagnostic CHE25 rate, twelve-month unreviewed OOP | {stats['alb2002_consumption_sdg_che25_12m_unreviewed_rate']} |
| SPL-ready rows | {stats['alb2002_consumption_sdg_spl_ready_rows']} |
| PPP/CPI-ready rows | {stats['alb2002_consumption_sdg_ppp_cpi_ready_rows']} |
| Discretionary-budget-ready rows | {stats['alb2002_consumption_sdg_discretionary_budget_ready_rows']} |
| CHE denominator-ready rows | {stats['alb2002_consumption_sdg_che_denominator_ready_rows']} |
| Outcome-ready rows | {stats['alb2002_consumption_sdg_outcome_ready_rows']} |
| Recipe-ready rows | {stats['alb2002_consumption_sdg_recipe_ready_rows']} |
| SDG 3.8.2-ready rows | {stats['alb2002_consumption_sdg_sdg382_ready_rows']} |
| Climate-linkage-ready rows | {stats['alb2002_consumption_sdg_climate_linkage_ready_rows']} |
| Decision | {stats['alb2002_consumption_sdg_current_decision']} |

{markdown_count_table(alb2002_consumption_sdg_family_counts, 'ALB_2002 consumption/SDG component family') if alb2002_consumption_sdg_audit else 'No ALB_2002 consumption/SDG denominator policy audit exists yet.'}

{markdown_count_table(alb2002_consumption_sdg_status_counts, 'ALB_2002 consumption/SDG evidence status') if alb2002_consumption_sdg_audit else 'No ALB_2002 consumption/SDG evidence-status rows exist yet.'}

`report/alb2002_consumption_sdg_denominator_policy_audit.md` quantifies observed `totcons`, household-weight, and household-size coverage, but treats CHE10/CHE25 ratios as diagnostics only. It keeps financial-protection outcome promotion blocked because total-consumption unit/period/price basis, OOP recall alignment, SPL, PPP/CPI, household discretionary budget, benchmark validation, and climate-geography gates have not passed together.

## ALB_2002 Consumption Construction Source Audit

| Metric | Value |
|---|---:|
| Source audit rows | {stats['alb2002_consumption_construction_source_audit_rows']} |
| Public method PDF present | {stats['alb2002_consumption_construction_public_pdf_present']} |
| Public Stata program ZIP present | {stats['alb2002_consumption_construction_program_zip_present']} |
| Extracted `.do` files | {stats['alb2002_consumption_construction_do_file_rows']} |
| `totcons.do` present | {stats['alb2002_consumption_construction_totcons_do_present']} |
| `poverty.do` present | {stats['alb2002_consumption_construction_poverty_do_present']} |
| Public metadata JSON present | {stats['alb2002_consumption_construction_metadata_json_present']} |
| Documentation-ready rows | {stats['alb2002_consumption_construction_documentation_ready_rows']} |
| Released-variable mapping-ready rows | {stats['alb2002_consumption_construction_released_variable_mapping_ready_rows']} |
| Denominator-variant-ready rows | {stats['alb2002_consumption_construction_denominator_variant_ready_rows']} |
| Recipe-ready rows | {stats['alb2002_consumption_construction_recipe_ready_rows']} |
| Outcome-ready rows | {stats['alb2002_consumption_construction_outcome_ready_rows']} |
| SDG 3.8.2-ready rows | {stats['alb2002_consumption_construction_sdg382_ready_rows']} |
| Climate-linkage-ready rows | {stats['alb2002_consumption_construction_climate_linkage_ready_rows']} |
| Decision | {stats['alb2002_consumption_construction_current_decision']} |

{markdown_count_table(alb2002_consumption_construction_family_counts, 'ALB_2002 consumption construction audit family') if alb2002_consumption_construction_audit else 'No ALB_2002 consumption construction source audit exists yet.'}

{markdown_count_table(alb2002_consumption_construction_status_counts, 'ALB_2002 consumption construction evidence status') if alb2002_consumption_construction_audit else 'No ALB_2002 consumption construction source evidence rows exist yet.'}

`report/alb2002_consumption_construction_source_audit.md` records public IHSN source evidence for the ALB_2002 aggregate: the method PDF, released Stata program ZIP, metadata JSON, and local SPSS statistic match. The narrow denominator blocker is resolved: local `totcons` is documented as the public `totcons3` total-budget variant, with durables and without rent and health. Promotion remains blocked because this does not settle the OOP numerator, SPL/PPP/CPI, discretionary-budget, benchmark, or climate-geography gates.

## ALB_2002 Consumption Aggregate Metadata Crosswalk Audit

| Metric | Value |
|---|---:|
| Aggregate crosswalk rows | {stats['alb2002_consumption_aggregate_crosswalk_rows']} |
| Local `Poverty_2002.sav` rows | {stats['alb2002_consumption_aggregate_crosswalk_local_poverty_rows']} |
| Local metadata catalog rows | {stats['alb2002_consumption_aggregate_crosswalk_metadata_catalog_rows']} |
| Raw `totcons` positive rows | {stats['alb2002_consumption_aggregate_crosswalk_raw_totcons_positive_rows']} |
| Candidate `total_consumption`/raw `totcons` match rows | {stats['alb2002_consumption_aggregate_crosswalk_candidate_totcons_match_rows']} |
| Questionnaire New Lek string hits | {stats['alb2002_consumption_aggregate_crosswalk_questionnaire_new_lek_hits']} |
| Questionnaire aggregate-formula hits | {stats['alb2002_consumption_aggregate_crosswalk_questionnaire_aggregate_formula_hits']} |
| Construction-source rows | {stats['alb2002_consumption_aggregate_crosswalk_construction_source_rows']} |
| Construction `.do` file rows | {stats['alb2002_consumption_aggregate_crosswalk_construction_do_file_rows']} |
| Metadata unit/period-ready rows | {stats['alb2002_consumption_aggregate_crosswalk_metadata_unit_period_ready_rows']} |
| Official documentation-ready rows | {stats['alb2002_consumption_aggregate_crosswalk_official_documentation_ready_rows']} |
| Released-variable mapping-ready rows | {stats['alb2002_consumption_aggregate_crosswalk_released_variable_mapping_ready_rows']} |
| Denominator-variant-ready rows | {stats['alb2002_consumption_aggregate_crosswalk_denominator_variant_ready_rows']} |
| Recipe-ready rows | {stats['alb2002_consumption_aggregate_crosswalk_recipe_ready_rows']} |
| Outcome-ready rows | {stats['alb2002_consumption_aggregate_crosswalk_outcome_ready_rows']} |
| SDG 3.8.2-ready rows | {stats['alb2002_consumption_aggregate_crosswalk_sdg382_ready_rows']} |
| Climate-linkage-ready rows | {stats['alb2002_consumption_aggregate_crosswalk_climate_linkage_ready_rows']} |
| Decision | {stats['alb2002_consumption_aggregate_crosswalk_current_decision']} |

{markdown_count_table(alb2002_consumption_aggregate_family_counts, 'ALB_2002 consumption aggregate audit family') if alb2002_consumption_aggregate_audit else 'No ALB_2002 consumption aggregate metadata crosswalk audit exists yet.'}

{markdown_count_table(alb2002_consumption_aggregate_readiness_counts, 'ALB_2002 consumption aggregate readiness status') if alb2002_consumption_aggregate_audit else 'No ALB_2002 consumption aggregate readiness rows exist yet.'}

`report/alb2002_consumption_aggregate_metadata_crosswalk_audit.md` verifies that candidate `total_consumption` exactly copies raw `totcons`, and that raw `totcons` is positive for all local poverty-file rows. The updated crosswalk imports the public source audit: `totcons.do`, `poverty.do`, and the IHSN metadata JSON document local `totcons` as public `totcons3`. This is accepted as total-budget denominator provenance only; recipe, outcome, SDG 3.8.2, and climate-linkage promotion remain blocked.

## ALB_2012 Raw Outcome Semantics Audit

| Metric | Value |
|---|---:|
| Raw value/semantics rows | {stats['alb2012_outcome_semantics_raw_value_rows']} |
| Source health modules scanned | {stats['alb2012_outcome_semantics_source_files_scanned']} |
| Financial OOP candidate rows | {stats['alb2012_outcome_semantics_financial_oop_candidate_rows']} |
| Gift/payment candidate rows | {stats['alb2012_outcome_semantics_gift_candidate_rows']} |
| Access candidate rows | {stats['alb2012_outcome_semantics_access_candidate_rows']} |
| Service-quality proxy rows | {stats['alb2012_outcome_semantics_service_quality_proxy_rows']} |
| Need proxy rows | {stats['alb2012_outcome_semantics_need_candidate_rows']} |
| Coping candidate rows | {stats['alb2012_outcome_semantics_coping_candidate_rows']} |
| Rows with value labels | {stats['alb2012_outcome_semantics_rows_with_value_labels']} |
| Conditional reason rows | {stats['alb2012_outcome_semantics_conditional_reason_rows']} |
| Outcome-ready rows | {stats['alb2012_outcome_semantics_outcome_ready_rows']} |
| SDG 3.8.2-ready rows | {stats['alb2012_outcome_semantics_sdg382_ready_rows']} |
| Climate-linkage-ready rows | {stats['alb2012_outcome_semantics_climate_linkage_ready_rows']} |
| Decision | {stats['alb2012_outcome_semantics_current_decision']} |

{markdown_count_table(alb2012_semantics_domain_counts, 'ALB_2012 raw semantics domain') if alb2012_semantics_audit else 'No ALB_2012 raw outcome-semantics audit exists yet.'}

{markdown_count_table(alb2012_semantics_promotion_counts, 'ALB_2012 raw semantics promotion status') if alb2012_semantics_audit else 'No ALB_2012 raw semantics promotion rows exist yet.'}

`report/alb2012_outcome_semantics_raw_value_audit.md` documents raw payment, gift, access, need, coping, and service-quality labels and observed values for ALB_2012. It keeps all outcome, SDG 3.8.2, and climate-linkage promotion blocked pending gift-policy, unit, recall-period, missing-code, skip-pattern denominator, timing, geography, and service-quality proxy review.

## ALB_2005 Raw Outcome Semantics Audit

| Metric | Value |
|---|---:|
| Raw value/semantics rows | {stats['alb2005_outcome_semantics_raw_value_rows']} |
| Source health modules scanned | {stats['alb2005_outcome_semantics_source_files_scanned']} |
| Financial OOP candidate rows | {stats['alb2005_outcome_semantics_financial_oop_candidate_rows']} |
| Gift/payment candidate rows | {stats['alb2005_outcome_semantics_gift_candidate_rows']} |
| Access candidate rows | {stats['alb2005_outcome_semantics_access_candidate_rows']} |
| Need proxy rows | {stats['alb2005_outcome_semantics_need_candidate_rows']} |
| Coping candidate rows | {stats['alb2005_outcome_semantics_coping_candidate_rows']} |
| Rows with value labels | {stats['alb2005_outcome_semantics_rows_with_value_labels']} |
| Conditional reason rows | {stats['alb2005_outcome_semantics_conditional_reason_rows']} |
| Outcome-ready rows | {stats['alb2005_outcome_semantics_outcome_ready_rows']} |
| SDG 3.8.2-ready rows | {stats['alb2005_outcome_semantics_sdg382_ready_rows']} |
| Climate-linkage-ready rows | {stats['alb2005_outcome_semantics_climate_linkage_ready_rows']} |
| Decision | {stats['alb2005_outcome_semantics_current_decision']} |

{markdown_count_table(alb2005_semantics_domain_counts, 'ALB_2005 raw semantics domain') if alb2005_semantics_audit else 'No ALB_2005 raw outcome-semantics audit exists yet.'}

{markdown_count_table(alb2005_semantics_promotion_counts, 'ALB_2005 raw semantics promotion status') if alb2005_semantics_audit else 'No ALB_2005 raw semantics promotion rows exist yet.'}

`report/alb2005_outcome_semantics_raw_value_audit.md` documents raw labels, observed values, value-label examples, and household merge coverage for ALB_2005 health OOP/access candidates. It shows raw payment/gift/access/coping evidence, but keeps all outcome, SDG 3.8.2, and climate-linkage promotion blocked pending gift-policy, unit, recall-period, missing-code, skip-pattern, timing, and geography review.

## ALB_2005 OOP Aggregation Policy Stress Test

| Metric | Value |
|---|---:|
| Policy stress-test rows | {stats['alb2005_oop_aggregation_policy_rows']} |
| Household rows | {stats['alb2005_oop_aggregation_policy_household_rows']} |
| Positive total-consumption denominator rows | {stats['alb2005_oop_aggregation_policy_total_consumption_rows']} |
| Four-week policy rows | {stats['alb2005_oop_aggregation_policy_four_week_rows']} |
| Twelve-month policy rows | {stats['alb2005_oop_aggregation_policy_twelve_month_rows']} |
| Annual stress-test rows | {stats['alb2005_oop_aggregation_policy_annual_stress_rows']} |
| Maximum CHE10 stress-test rate | {stats['alb2005_oop_aggregation_policy_max_che10_rate']} |
| Maximum CHE25 stress-test rate | {stats['alb2005_oop_aggregation_policy_max_che25_rate']} |
| Questionnaire OOP rows observed | {stats['alb2005_oop_aggregation_policy_questionnaire_oop_rows']} |
| Questionnaire old-lek rows observed | {stats['alb2005_oop_aggregation_policy_questionnaire_old_lek_rows']} |
| Outcome-ready rows | {stats['alb2005_oop_aggregation_policy_outcome_ready_rows']} |
| Recipe-ready rows | {stats['alb2005_oop_aggregation_policy_recipe_ready_rows']} |
| Climate-linkage-ready rows | {stats['alb2005_oop_aggregation_policy_climate_linkage_ready_rows']} |
| Decision | {stats['alb2005_oop_aggregation_policy_current_decision']} |

{markdown_count_table(alb2005_oop_policy_recall_counts, 'ALB_2005 OOP policy recall scope') if alb2005_oop_policy_audit else 'No ALB_2005 OOP aggregation policy audit exists yet.'}

{markdown_count_table(alb2005_oop_policy_promotion_counts, 'ALB_2005 OOP policy promotion status') if alb2005_oop_policy_audit else 'No ALB_2005 OOP policy promotion rows exist yet.'}

`report/alb2005_oop_aggregation_policy_audit.md` compares provider charges, gifts, medicines, laboratory work, transport, and own-purchased drugs across four-week, 12-month, and annualized stress-test policies. These CHE10/CHE25 rates are event-rate and aggregation-policy diagnostics only, not final outcome estimates.

## ALB_2005 Skip/Missing Semantics Audit

| Metric | Value |
|---|---:|
| Skip/missing audit rows | {stats['alb2005_skip_missing_semantics_rows']} |
| Payment block rows | {stats['alb2005_skip_missing_payment_block_rows']} |
| Access condition rows | {stats['alb2005_skip_missing_access_condition_rows']} |
| Financing multi-response rows | {stats['alb2005_skip_missing_financing_multiselect_rows']} |
| Payment downstream nonmissing when not triggered | {stats['alb2005_skip_missing_payment_nonmissing_when_not_triggered_rows']} |
| Payment downstream positive when not triggered | {stats['alb2005_skip_missing_payment_positive_when_not_triggered_rows']} |
| Triggered payment rows with no positive payment | {stats['alb2005_skip_missing_payment_zero_or_missing_when_triggered_rows']} |
| Conditional reason nonmissing when not triggered | {stats['alb2005_skip_missing_condition_nonmissing_when_not_triggered_rows']} |
| Conditional reason missing when triggered | {stats['alb2005_skip_missing_condition_missing_when_triggered_rows']} |
| Financing method nonmissing when not triggered | {stats['alb2005_skip_missing_financing_nonmissing_when_not_triggered_rows']} |
| Financing method missing when triggered | {stats['alb2005_skip_missing_financing_missing_when_triggered_rows']} |
| Recipe-ready rows | {stats['alb2005_skip_missing_recipe_ready_rows']} |
| Outcome-ready rows | {stats['alb2005_skip_missing_outcome_ready_rows']} |
| Climate-linkage-ready rows | {stats['alb2005_skip_missing_climate_linkage_ready_rows']} |
| Decision | {stats['alb2005_skip_missing_current_decision']} |

{markdown_count_table(alb2005_skip_missing_family_counts, 'ALB_2005 skip/missing audit family') if alb2005_skip_missing_audit else 'No ALB_2005 skip/missing semantics audit exists yet.'}

{markdown_count_table(alb2005_skip_missing_status_counts, 'ALB_2005 skip/missing evidence status') if alb2005_skip_missing_audit else 'No ALB_2005 skip/missing status rows exist yet.'}

`report/alb2005_skip_missing_semantics_audit.md` checks raw trigger/downstream consistency for person-level payment blocks, household access reasons, and health-financing multi-response methods. It documents zero downstream skip leaks in the audited rows, but leaves 326 triggered payment rows with no positive payment for explicit zero/missing-code review and does not promote outcomes.

## ALB_2005 Consumption/OOP Unit and Period Audit

| Metric | Value |
|---|---:|
| Unit-period audit rows | {stats['alb2005_consumption_oop_unit_period_rows']} |
| Positive total-consumption rows | {stats['alb2005_consumption_oop_unit_period_total_consumption_positive_rows']} |
| Positive per-capita consumption rows | {stats['alb2005_consumption_oop_unit_period_rcons_positive_rows']} |
| Metadata old-lek rows | {stats['alb2005_consumption_oop_unit_period_metadata_old_lek_rows']} |
| Questionnaire OOP old-lek rows | {stats['alb2005_consumption_oop_unit_period_oop_old_lek_rows']} |
| Four-week OOP recall rows | {stats['alb2005_consumption_oop_unit_period_four_week_oop_rows']} |
| Twelve-month OOP recall rows | {stats['alb2005_consumption_oop_unit_period_twelve_month_oop_rows']} |
| Nonhealth questionnaire old-lek rows | {stats['alb2005_consumption_oop_unit_period_questionnaire_nonfood_old_lek_rows']} |
| Median `totcons/rcons/12` diagnostic | {stats['alb2005_consumption_oop_unit_period_totcons_rcons_implied_scale_median']} |
| Median roster household size | {stats['alb2005_consumption_oop_unit_period_roster_hhsize_median']} |
| SDG 3.8.2-ready rows | {stats['alb2005_consumption_oop_unit_period_sdg382_ready_rows']} |
| Recipe-ready rows | {stats['alb2005_consumption_oop_unit_period_recipe_ready_rows']} |
| Outcome-ready rows | {stats['alb2005_consumption_oop_unit_period_outcome_ready_rows']} |
| Climate-linkage-ready rows | {stats['alb2005_consumption_oop_unit_period_climate_linkage_ready_rows']} |
| Decision | {stats['alb2005_consumption_oop_unit_period_current_decision']} |

{markdown_count_table(alb2005_unit_period_family_counts, 'ALB_2005 unit-period audit family') if alb2005_unit_period_audit else 'No ALB_2005 unit-period audit exists yet.'}

{markdown_count_table(alb2005_unit_period_status_counts, 'ALB_2005 unit-period evidence status') if alb2005_unit_period_audit else 'No ALB_2005 unit-period evidence-status rows exist yet.'}

`report/alb2005_consumption_oop_unit_period_audit.md` documents positive `totcons` and `rcons` values, public metadata old-lek labels, questionnaire-backed OOP old-lek rows, and mixed four-week/12-month OOP recall periods. It still promotes zero rows to SDG 3.8.2, harmonization recipes, outcome construction, or climate linkage because total-consumption period/price basis, OOP annualization, PPP/SPL/CPI handling, timing, and geography remain unresolved.

## ALB_2005 Consumption Aggregate Metadata Crosswalk Audit

| Metric | Value |
|---|---:|
| Crosswalk audit rows | {stats['alb2005_consumption_aggregate_crosswalk_rows']} |
| Public metadata aggregate/component rows checked | {stats['alb2005_consumption_aggregate_crosswalk_metadata_rows']} |
| Local poverty.sav columns | {stats['alb2005_consumption_aggregate_crosswalk_local_poverty_columns']} |
| Metadata variables present locally | {stats['alb2005_consumption_aggregate_crosswalk_metadata_present_local_rows']} |
| Metadata variables absent locally | {stats['alb2005_consumption_aggregate_crosswalk_metadata_absent_local_rows']} |
| Local per-capita diagnostic components | {stats['alb2005_consumption_aggregate_crosswalk_local_per_capita_component_rows']} |
| Positive local `totcons` rows | {stats['alb2005_consumption_aggregate_crosswalk_totcons_positive_rows']} |
| Local `totcons05` rows | {stats['alb2005_consumption_aggregate_crosswalk_totcons05_local_rows']} |
| Formula reconstructable rows | {stats['alb2005_consumption_aggregate_crosswalk_component_formula_reconstructable_rows']} |
| SDG 3.8.2-ready rows | {stats['alb2005_consumption_aggregate_crosswalk_sdg382_ready_rows']} |
| Recipe-ready rows | {stats['alb2005_consumption_aggregate_crosswalk_recipe_ready_rows']} |
| Outcome-ready rows | {stats['alb2005_consumption_aggregate_crosswalk_outcome_ready_rows']} |
| Climate-linkage-ready rows | {stats['alb2005_consumption_aggregate_crosswalk_climate_linkage_ready_rows']} |
| Decision | {stats['alb2005_consumption_aggregate_crosswalk_current_decision']} |

{markdown_count_table(alb2005_aggregate_crosswalk_family_counts, 'ALB_2005 aggregate crosswalk audit family') if alb2005_aggregate_crosswalk_audit else 'No ALB_2005 aggregate metadata crosswalk audit exists yet.'}

{markdown_count_table(alb2005_aggregate_crosswalk_status_counts, 'ALB_2005 aggregate crosswalk readiness status') if alb2005_aggregate_crosswalk_audit else 'No ALB_2005 aggregate crosswalk readiness-status rows exist yet.'}

`report/alb2005_consumption_aggregate_metadata_crosswalk_audit.md` shows that public metadata lists old-lek aggregate/component variables, but local `poverty.sav` exposes only `totcons` from the checked formula set plus per-capita diagnostics. The `totcons05` variant and formula components are absent locally, so denominator reconstruction, variant choice, SDG 3.8.2, recipes, outcomes, and climate linkage remain blocked.

## ALB_2005 Consumption Component Source Search Audit

| Metric | Value |
|---|---:|
| Source-search audit rows | {stats['alb2005_consumption_component_source_search_rows']} |
| Target variables searched | {stats['alb2005_consumption_component_source_search_target_variables']} |
| Local file rows scanned | {stats['alb2005_consumption_component_source_search_local_files_scanned']} |
| Local variable rows scanned | {stats['alb2005_consumption_component_source_search_local_variables_scanned']} |
| Questionnaire workbooks scanned | {stats['alb2005_consumption_component_source_search_questionnaire_workbooks_scanned']} |
| Construction-code files found | {stats['alb2005_consumption_component_source_search_construction_code_files_found']} |
| Exact target variables found | {stats['alb2005_consumption_component_source_search_exact_target_variables_found']} |
| Exact target variables missing | {stats['alb2005_consumption_component_source_search_exact_target_variables_missing']} |
| Label/phrase target leads | {stats['alb2005_consumption_component_source_search_label_phrase_targets_found']} |
| Questionnaire phrase target leads | {stats['alb2005_consumption_component_source_search_questionnaire_phrase_targets_found']} |
| Construction-code target hits | {stats['alb2005_consumption_component_source_search_construction_code_targets_found']} |
| SDG 3.8.2-ready rows | {stats['alb2005_consumption_component_source_search_sdg382_ready_rows']} |
| Recipe-ready rows | {stats['alb2005_consumption_component_source_search_recipe_ready_rows']} |
| Outcome-ready rows | {stats['alb2005_consumption_component_source_search_outcome_ready_rows']} |
| Climate-linkage-ready rows | {stats['alb2005_consumption_component_source_search_climate_linkage_ready_rows']} |
| Decision | {stats['alb2005_consumption_component_source_search_current_decision']} |

{markdown_count_table(alb2005_component_source_family_counts, 'ALB_2005 component source-search audit family') if alb2005_component_source_audit else 'No ALB_2005 component source-search audit exists yet.'}

{markdown_count_table(alb2005_component_source_status_counts, 'ALB_2005 component source-search evidence status') if alb2005_component_source_audit else 'No ALB_2005 component source-search evidence-status rows exist yet.'}

`report/alb2005_consumption_component_source_search_audit.md` searches the local raw schema, file inventory, questionnaires, and source-code-like files for the public-metadata aggregate components. It finds only `totcons` as an exact target-variable hit, no local construction-code files, and zero SDG 3.8.2, recipe, outcome, or climate-linkage promotion. Module and questionnaire phrase hits remain manual-review leads, not denominator recipes.

## ALB_2005 Timing/Geography Source Search Audit

| Metric | Value |
|---|---:|
| Source-search audit rows | {stats['alb2005_timing_geography_source_search_rows']} |
| Target concepts searched | {stats['alb2005_timing_geography_source_search_target_concepts']} |
| Local file rows scanned | {stats['alb2005_timing_geography_source_search_local_files_scanned']} |
| Local variable rows scanned | {stats['alb2005_timing_geography_source_search_local_variables_scanned']} |
| Questionnaire workbooks scanned | {stats['alb2005_timing_geography_source_search_questionnaire_workbooks_scanned']} |
| Raw targets with hits | {stats['alb2005_timing_geography_source_search_raw_targets_with_hits']} |
| Questionnaire targets with hits | {stats['alb2005_timing_geography_source_search_questionnaire_targets_with_hits']} |
| Legacy questionnaire timing rows | {stats['alb2005_timing_geography_source_search_legacy_questionnaire_timing_rows']} |
| Verified household timing rows | {stats['alb2005_timing_geography_source_search_verified_household_timing_rows']} |
| Coordinate candidate rows | {stats['alb2005_timing_geography_source_search_coordinate_candidate_rows']} |
| Partial district variable rows | {stats['alb2005_timing_geography_source_search_partial_district_variable_rows']} |
| Partial district-name rows | {stats['alb2005_timing_geography_source_search_partial_district_name_nonmissing_rows']} |
| Partial district-code rows | {stats['alb2005_timing_geography_source_search_partial_district_code_nonmissing_rows']} |
| Required value/key timing rows | {stats['alb2005_timing_geography_source_search_required_value_key_timing_rows']} |
| Required value/key coordinate rows | {stats['alb2005_timing_geography_source_search_required_value_key_coordinate_rows']} |
| Geography-crosswalk-ready rows | {stats['alb2005_timing_geography_source_search_geography_crosswalk_ready_rows']} |
| Interview-timing-ready rows | {stats['alb2005_timing_geography_source_search_interview_timing_ready_rows']} |
| Climate-linkage-ready rows | {stats['alb2005_timing_geography_source_search_climate_linkage_ready_rows']} |
| Decision | {stats['alb2005_timing_geography_source_search_current_decision']} |

{markdown_count_table(alb2005_timing_geo_source_family_counts, 'ALB_2005 timing/geography source-search audit family') if alb2005_timing_geo_source_audit else 'No ALB_2005 timing/geography source-search audit exists yet.'}

{markdown_count_table(alb2005_timing_geo_source_status_counts, 'ALB_2005 timing/geography source-search evidence status') if alb2005_timing_geo_source_audit else 'No ALB_2005 timing/geography source-search evidence-status rows exist yet.'}

{markdown_count_table(alb2005_timing_geo_source_promotion_counts, 'ALB_2005 timing/geography source-search promotion status') if alb2005_timing_geo_source_audit else 'No ALB_2005 timing/geography source-search promotion rows exist yet.'}

`report/alb2005_timing_geography_source_search_audit.md` searches the local raw schema, file inventory, questionnaires, and upstream timing/geography summaries for household interview timing, current-location geography, coordinates, and PSU/cluster evidence. It finds raw and questionnaire leads plus partial district evidence, but verifies zero household interview timing rows, zero coordinate candidates, and zero geography-crosswalk, interview-timing, or climate-linkage promotion.

## ALB_2008 Raw Outcome Semantics Audit

| Metric | Value |
|---|---:|
| Raw value/semantics rows | {stats['alb2008_outcome_semantics_raw_value_rows']} |
| Source health modules scanned | {stats['alb2008_outcome_semantics_source_files_scanned']} |
| Financial OOP candidate rows | {stats['alb2008_outcome_semantics_financial_oop_candidate_rows']} |
| Gift/payment candidate rows | {stats['alb2008_outcome_semantics_gift_candidate_rows']} |
| Access candidate rows | {stats['alb2008_outcome_semantics_access_candidate_rows']} |
| Facility/service-quality proxy rows | {stats['alb2008_outcome_semantics_facility_proxy_rows']} |
| Need proxy rows | {stats['alb2008_outcome_semantics_need_candidate_rows']} |
| Coping candidate rows | {stats['alb2008_outcome_semantics_coping_candidate_rows']} |
| Rows with value labels | {stats['alb2008_outcome_semantics_rows_with_value_labels']} |
| Conditional reason rows | {stats['alb2008_outcome_semantics_conditional_reason_rows']} |
| Outcome-ready rows | {stats['alb2008_outcome_semantics_outcome_ready_rows']} |
| SDG 3.8.2-ready rows | {stats['alb2008_outcome_semantics_sdg382_ready_rows']} |
| Climate-linkage-ready rows | {stats['alb2008_outcome_semantics_climate_linkage_ready_rows']} |
| Decision | {stats['alb2008_outcome_semantics_current_decision']} |

{markdown_count_table(alb2008_semantics_domain_counts, 'ALB_2008 raw semantics domain') if alb2008_semantics_audit else 'No ALB_2008 raw outcome-semantics audit exists yet.'}

{markdown_count_table(alb2008_semantics_promotion_counts, 'ALB_2008 raw semantics promotion status') if alb2008_semantics_audit else 'No ALB_2008 raw semantics promotion rows exist yet.'}

`report/alb2008_outcome_semantics_raw_value_audit.md` documents raw labels, observed values, value-label examples, and household merge coverage for ALB_2008 health OOP/access candidates. It adds service-quality and facility proxy evidence from module 9C, but keeps all outcome, SDG 3.8.2, and climate-linkage promotion blocked pending gift-policy, unit, recall-period, missing-code, skip-pattern, timing, geography, and proxy-interpretation review.

## Caveats

- These provisional diagnostics are not final outcomes and are not written to `data/`.
- Four-week and twelve-month OOP fields are not pooled unless a documented recall-period rule is verified.
- SDG 3.8.2 is not inferred without a verified discretionary-budget denominator.
- Access proxies require skip-pattern, need-denominator, and missing-code review before any forgone-care outcome can be promoted.
- ALB_2002 has observed interview date/month and district fields, but climate linkage still requires a validated district crosswalk, boundary-name mismatch review, historical boundary verification, and no-GPS measurement-error handling.
- ALB_2005 has raw payment, gift, access, and coping evidence, but survey timing and full climate-ready geography are still unverified.
- ALB_2008 has raw payment, gift, access, coping, and facility/service-quality evidence, but survey timing and climate-ready geography are still unverified.
- ALB_2012 has raw payment, gift, access, coping, service-quality, questionnaire timing-field, and fallback blocker-resolution evidence, but raw household interview timing and climate-ready geography are still unverified.
- ALB_2002/2005/2008 legacy `.xls` questionnaires are present and readable in the current environment, but readable form text is not enough: raw skip paths, payment-scope policy, missing-code semantics, fieldwork timing, and climate-ready geography still need verification before outcome promotion.
- No descriptive prevalence, predictive ML, causal, causal ML, or policy-targeting claim can be made from these diagnostics.

## Audit Files

- `result/outcome_audit.csv`
- `temp/outcome_construction_audit.csv`
""",
        encoding="utf-8",
    )

    climate_status_text = markdown_count_table(climate_status_counts, "Climate extraction status") if climate_audit else "No climate extraction audit exists yet."
    climate_source_status_text = markdown_count_table(climate_source_status_counts, "Climate source probe status") if climate_source_probe else "No climate source probe has been run yet."
    climate_source_role_text = markdown_count_table(climate_source_role_counts, "Climate source role") if climate_source_probe else "No climate source-role rows exist yet."
    (REPORT_DIR / "climate_linkage_audit.md").write_text(
        f"""# Climate Linkage Audit

Status: climate extraction scaffold is implemented. NASA POWER point fallback can run once harmonized coordinates and interview timing exist.

## Current Geography/Timing Evidence

Metadata schema inspection found geography, cluster, residence, or GPS label hits in the priority studies, but raw geolocation quality is not verified. GPS may be absent, displaced, restricted, or represented only through ancillary files depending on survey.

ALB_2002 raw household-core audit rows: {len(alb2002_core_merge_audit)}. Households with observed survey month: {stats['alb2002_households_with_survey_month']}. Households with constructed interview date: {stats['alb2002_households_with_interview_date']}. Households with district code: {stats['alb2002_households_with_district_code']}. District crosswalk template rows: {stats['alb2002_district_crosswalk_template_rows']}; public boundary probe rows: {stats['alb2002_district_crosswalk_source_probe_rows']}; boundary-source reachable rows: {stats['alb2002_district_crosswalk_source_reachable_rows']}; boundary ADM unit count: {stats['alb2002_district_crosswalk_adm_unit_count']}; public boundary name-match rows: {stats['alb2002_boundary_name_match_rows']}; GeoJSON features: {stats['alb2002_boundary_geojson_feature_rows']}; exact name matches: {stats['alb2002_boundary_name_match_exact_rows']}; mojibake-repaired matches: {stats['alb2002_boundary_name_match_euro_repaired_rows']}; unmatched survey rows: {stats['alb2002_boundary_name_match_unmatched_survey_rows']}; duplicate boundary-name keys: {stats['alb2002_boundary_name_match_duplicate_boundary_name_keys']}; parsed boundary-resource candidates: {stats['alb2002_boundary_resource_search_candidate_rows']}; complete-name-coverage resources: {stats['alb2002_boundary_resource_search_complete_name_coverage_rows']}; exact-unit-count resources: {stats['alb2002_boundary_resource_search_exact_unit_count_rows']}; best resource lead: {stats['alb2002_boundary_resource_search_best_candidate_id']}; geometry features parsed for that lead: {stats['alb2002_boundary_geometry_feature_rows']}; metadata boundary year: {stats['alb2002_boundary_geometry_metadata_boundary_year']}; boundary-resource climate-linkage-ready rows: {stats['alb2002_boundary_resource_search_climate_linkage_ready_rows']}; geometry/provenance climate-linkage-ready rows: {stats['alb2002_boundary_geometry_climate_linkage_ready_rows']}; boundary-name climate-linkage-ready rows: {stats['alb2002_boundary_name_match_climate_linkage_ready_rows']}; ALB_2002 climate-linkage-ready rows: {stats['alb2002_climate_linkage_ready_rows']}. Current decisions: household core {stats['alb2002_household_core_current_decision']}; district crosswalk {stats['alb2002_district_crosswalk_current_decision']}; boundary name match {stats['alb2002_boundary_name_match_current_decision']}; boundary resource search {stats['alb2002_boundary_resource_search_current_decision']}; boundary geometry/provenance {stats['alb2002_boundary_geometry_current_decision']}. These fields are candidate inputs only; no climate-linkage-ready rows are promoted until district polygons/crosswalk, fieldwork documentation, historical district definitions, no-GPS measurement error, and OOP/access semantics pass.

ALB_2002 boundary name-match status:

{markdown_count_table(alb2002_boundary_name_method_counts, 'ALB_2002 boundary name match method') if alb2002_boundary_name_audit else 'No ALB_2002 boundary name-match audit exists yet.'}

{markdown_count_table(alb2002_boundary_name_status_counts, 'ALB_2002 boundary name match status') if alb2002_boundary_name_audit else 'No ALB_2002 boundary name-match status rows exist yet.'}

ALB_2002 boundary source alternatives:

{markdown_count_table(alb2002_boundary_source_probe_counts, 'ALB_2002 boundary source probe status') if alb2002_boundary_source_audit else 'No ALB_2002 boundary source-alternative audit exists yet.'}

{markdown_count_table(alb2002_boundary_source_suitability_counts, 'ALB_2002 boundary source suitability') if alb2002_boundary_source_audit else 'No ALB_2002 boundary source suitability rows exist yet.'}

The boundary source-alternatives audit is `report/alb2002_boundary_source_alternative_audit.md`; machine-readable outputs are `temp/alb2002_boundary_source_alternative_audit.csv` and `result/alb2002_boundary_source_alternative_summary.csv`. It reviews {stats['alb2002_boundary_source_alternative_rows']} source leads, including current/post-2015 sources, the official ALB_2002 study page, INSTAT census context, and IHGIS historical census leads. LSMS map and GPS documentation flags are {stats['alb2002_boundary_source_alternative_lsms_maps_documented_rows']} and {stats['alb2002_boundary_source_alternative_gps_documented_rows']}, but verified historical-boundary-ready and climate-linkage-ready rows remain {stats['alb2002_boundary_source_alternative_historical_ready_rows']} and {stats['alb2002_boundary_source_alternative_climate_linkage_ready_rows']}; current decision is `{stats['alb2002_boundary_source_alternative_current_decision']}`.

ALB_2002 boundary resource search:

{markdown_count_table(alb2002_boundary_resource_status_counts, 'ALB_2002 boundary resource status') if alb2002_boundary_resource_audit else 'No ALB_2002 boundary resource-search audit exists yet.'}

{markdown_count_table(alb2002_boundary_resource_suitability_counts, 'ALB_2002 boundary resource suitability') if alb2002_boundary_resource_audit else 'No ALB_2002 boundary resource suitability rows exist yet.'}

The boundary resource-search audit is `report/alb2002_boundary_source_resource_search_audit.md`; machine-readable outputs are `temp/alb2002_boundary_source_resource_search_audit.csv` and `result/alb2002_boundary_source_resource_search_summary.csv`. It directly parses {stats['alb2002_boundary_resource_search_parseable_resource_rows']} public boundary/gazetteer resources. The best name-coverage lead is `{stats['alb2002_boundary_resource_search_best_candidate_id']}`, with {stats['alb2002_boundary_resource_search_best_candidate_exact_matches']} exact matches, {stats['alb2002_boundary_resource_search_best_candidate_repaired_matches']} encoding-repaired matches, and {stats['alb2002_boundary_resource_search_best_candidate_alias_matches']} documented alias matches. Complete-name-coverage and exact-unit-count resources are {stats['alb2002_boundary_resource_search_complete_name_coverage_rows']} and {stats['alb2002_boundary_resource_search_exact_unit_count_rows']}, but verified 2002 historical-boundary-ready and climate-linkage-ready rows remain {stats['alb2002_boundary_resource_search_2002_historical_ready_rows']} and {stats['alb2002_boundary_resource_search_climate_linkage_ready_rows']}; current decision is `{stats['alb2002_boundary_resource_search_current_decision']}`.

ALB_2002 boundary geometry and provenance:

{markdown_count_table(alb2002_boundary_geometry_status_counts, 'ALB_2002 boundary geometry structure status') if alb2002_boundary_geometry_audit else 'No ALB_2002 boundary geometry/provenance audit exists yet.'}

{markdown_count_table(alb2002_boundary_geometry_match_counts, 'ALB_2002 boundary geometry survey match method') if alb2002_boundary_geometry_audit else 'No ALB_2002 boundary geometry survey-match rows exist yet.'}

{markdown_count_table(alb2002_boundary_metadata_status_counts, 'ALB_2002 boundary metadata evidence status') if alb2002_boundary_metadata_probe else 'No ALB_2002 boundary metadata provenance rows exist yet.'}

The boundary geometry/provenance audit is `report/alb2002_boundary_geometry_provenance_audit.md`; machine-readable outputs are `temp/alb2002_boundary_geometry_provenance_audit.csv`, `temp/alb2002_boundary_metadata_provenance_probe.csv`, and `result/alb2002_boundary_geometry_provenance_summary.csv`. It finds {stats['alb2002_boundary_geometry_feature_rows']} parsed ADM2 features, {stats['alb2002_boundary_geometry_coordinate_structure_ok_rows']} coordinate-structure-ok features, and {stats['alb2002_boundary_geometry_survey_key_matched_rows']} survey-key matches. The companion metadata reports boundary year {stats['alb2002_boundary_geometry_metadata_boundary_year']}, update {stats['alb2002_boundary_geometry_metadata_boundary_update']}, and source {stats['alb2002_boundary_geometry_metadata_boundary_source']}. Boundary-year-matches-2002, topology-validated, historical-boundary-ready, and climate-linkage-ready rows are {stats['alb2002_boundary_geometry_boundary_year_matches_2002_rows']}, {stats['alb2002_boundary_geometry_topology_validated_rows']}, {stats['alb2002_boundary_geometry_historical_2002_boundary_ready_rows']}, and {stats['alb2002_boundary_geometry_climate_linkage_ready_rows']}; current decision is `{stats['alb2002_boundary_geometry_current_decision']}`.

ALB_2002 boundary manual verification packet:

{markdown_count_table(alb2002_boundary_manual_action_status_counts, 'ALB_2002 boundary manual action status') if alb2002_boundary_manual_actions else 'No ALB_2002 boundary manual action rows exist yet.'}

{markdown_count_table(alb2002_boundary_manual_gate_status_counts, 'ALB_2002 boundary manual gate status') if alb2002_boundary_manual_gates else 'No ALB_2002 boundary manual gate rows exist yet.'}

The boundary manual verification packet is `report/alb2002_boundary_manual_verification_packet.md`; machine-readable outputs are `temp/alb2002_boundary_manual_verification_action_queue.csv`, `temp/alb2002_boundary_promotion_gate_checklist.csv`, and `result/alb2002_boundary_manual_verification_packet_summary.csv`. It turns the ALB_2002 boundary blocker into {stats['alb2002_boundary_manual_verification_action_rows']} source-specific actions and {stats['alb2002_boundary_manual_verification_gate_rows']} promotion gates. Candidate-evidence gates are {stats['alb2002_boundary_manual_verification_candidate_evidence_gates']}, blocked gates are {stats['alb2002_boundary_manual_verification_blocked_gates']}, high-priority actions are {stats['alb2002_boundary_manual_verification_high_priority_actions']}, pre-2011 digital-map absence evidence rows are {stats['alb2002_boundary_manual_verification_pre2011_digital_map_absence_rows']}, and climate-linkage-ready rows remain {stats['alb2002_boundary_manual_verification_climate_linkage_ready_rows']}; current decision is `{stats['alb2002_boundary_manual_verification_current_decision']}`.

ALB_2002 boundary manual source follow-up:

{markdown_count_table(alb2002_boundary_followup_blocker_counts, 'ALB_2002 boundary follow-up blocker') if alb2002_boundary_followup_audit else 'No ALB_2002 boundary source follow-up rows exist yet.'}

{markdown_count_table(alb2002_boundary_followup_level_counts, 'ALB_2002 boundary follow-up level compatibility') if alb2002_boundary_followup_audit else 'No ALB_2002 boundary source level-compatibility rows exist yet.'}

The boundary manual source follow-up is `report/alb2002_boundary_manual_source_followup.md`; machine-readable outputs are `temp/alb2002_boundary_manual_source_followup_audit.csv` and `result/alb2002_boundary_manual_source_followup_summary.csv`. It records {stats['alb2002_boundary_manual_source_followup_rows']} source follow-up rows and {stats['alb2002_boundary_manual_source_followup_conclusive_blocker_rows']} source-specific blockers. The IHGIS lead is now `{stats['alb2002_boundary_manual_source_followup_ipums_level_status']}` in the reviewed catalog evidence, so it is not a 36-district ALB_2002 boundary solution unless a separate district/g2 file is found. The UNECE/INSTAT pre-2011 map status is `{stats['alb2002_boundary_manual_source_followup_unece_pre2011_map_status']}`, which blocks treating current or post-2011 public GIS layers as historical 2002 boundaries without separate crosswalk proof. District-level-ready and climate-linkage-ready rows remain {stats['alb2002_boundary_manual_source_followup_district_level_ready_rows']} and {stats['alb2002_boundary_manual_source_followup_climate_linkage_ready_rows']}; current decision is `{stats['alb2002_boundary_manual_source_followup_current_decision']}`.

ALB_2002 GADM boundary lead audit:

{markdown_count_table(alb2002_gadm_status_counts, 'ALB_2002 GADM suitability status') if alb2002_gadm_audit else 'No ALB_2002 GADM boundary lead audit rows exist yet.'}

{markdown_count_table(alb2002_gadm_match_status_counts, 'ALB_2002 GADM name-match status') if alb2002_gadm_match_audit else 'No ALB_2002 GADM name-match rows exist yet.'}

The GADM boundary lead audit is `report/alb2002_gadm_boundary_lead_audit.md`; machine-readable outputs are `temp/alb2002_gadm_boundary_lead_audit.csv`, `temp/alb2002_gadm_boundary_name_match_audit.csv`, and `result/alb2002_gadm_boundary_lead_summary.csv`. It audits {stats['alb2002_gadm_boundary_lead_candidate_rows']} public GADM Albania ADM2 snapshots. GADM 3.6 has {stats['alb2002_gadm36_adm2_row_count']} ADM2 rows, {stats['alb2002_gadm36_distinct_normalized_key_count']} normalized keys, and {stats['alb2002_gadm36_engtype_district_rows']} rows labeled District/Rreth-compatible, but it has {stats['alb2002_gadm36_duplicate_boundary_key_count']} duplicate normalized key and no verified official 2001/2002 historical provenance. Historical-ready and climate-linkage-ready rows remain {stats['alb2002_gadm_boundary_lead_historical_2002_ready_rows']} and {stats['alb2002_gadm_boundary_lead_climate_linkage_ready_rows']}; current decision is `{stats['alb2002_gadm_boundary_lead_current_decision']}`.

ALB_2002 local geography artifacts:

{markdown_count_table(alb2002_local_geo_artifact_role_counts, 'ALB_2002 local geography evidence role') if alb2002_local_geo_artifact_audit else 'No ALB_2002 local geography artifact audit exists yet.'}

{markdown_count_table(alb2002_local_geo_artifact_status_counts, 'ALB_2002 local geography value status') if alb2002_local_geo_artifact_audit else 'No ALB_2002 local geography value-status rows exist yet.'}

The local geography artifact audit is `report/alb2002_local_geography_artifact_audit.md`; machine-readable outputs are `temp/alb2002_local_geography_artifact_audit.csv` and `result/alb2002_local_geography_artifact_summary.csv`. It scans {stats['alb2002_local_geo_artifact_files_scanned']} local extracted files plus the raw schema/questionnaire evidence. Questionnaire coordinate fields are {stats['alb2002_local_geo_artifact_questionnaire_coordinate_field_rows']} and official GPS/EA-map documentation flags are {stats['alb2002_local_geo_artifact_official_gps_documented_rows']} and {stats['alb2002_local_geo_artifact_official_ea_map_documented_rows']}, but raw coordinate-variable rows, recognized local GIS/boundary file candidates, local-coordinate-ready rows, local-boundary-ready rows, and climate-linkage-ready rows are {stats['alb2002_local_geo_artifact_coordinate_raw_variable_rows']}, {stats['alb2002_local_geo_artifact_gis_file_candidate_rows']}, {stats['alb2002_local_geo_artifact_local_coordinate_ready_rows']}, {stats['alb2002_local_geo_artifact_local_boundary_ready_rows']}, and {stats['alb2002_local_geo_artifact_climate_linkage_ready_rows']}; current decision is `{stats['alb2002_local_geo_artifact_current_decision']}`.

ALB_2012 raw core feasibility rows: {stats['alb2012_household_core_candidate_rows']}. Provisional outcome diagnostic rows: {stats['alb2012_provisional_outcome_audit_rows']}. Raw outcome-semantics rows: {stats['alb2012_outcome_semantics_raw_value_rows']}. Timing/geography audit rows: {stats['alb2012_timing_geography_audit_rows']}. Questionnaire timing/control field rows: {stats['alb2012_questionnaire_timing_field_rows']}; questionnaire raw-gap rows: {stats['alb2012_questionnaire_timing_raw_gap_rows']}; raw verified questionnaire-derived interview timing rows: {stats['alb2012_questionnaire_timing_raw_verified_interview_timing_rows']}. Fallback blocker rows: {stats['alb2012_timing_geography_blocker_resolution_rows']}; fallback hard-blocked rows: {stats['alb2012_timing_geography_blocker_hard_blocked_rows']}. Households with survey month: {stats['alb2012_households_with_survey_month']}; interview date: {stats['alb2012_households_with_interview_date']}; prefecture: {stats['alb2012_households_with_prefecture']}; region: {stats['alb2012_households_with_region']}; raw-core climate-linkage-ready rows: {stats['alb2012_climate_linkage_ready_rows']}; semantics climate-linkage-ready rows: {stats['alb2012_outcome_semantics_climate_linkage_ready_rows']}; timing/geography climate-linkage-ready rows: {stats['alb2012_timing_geography_climate_linkage_ready_rows']}; questionnaire timing climate-linkage-ready rows: {stats['alb2012_questionnaire_timing_climate_linkage_ready_rows']}; fallback climate-linkage-ready rows: {stats['alb2012_timing_geography_blocker_climate_linkage_ready_rows']}. Current decisions: raw core {stats['alb2012_raw_core_current_decision']}; provisional outcomes {stats['alb2012_provisional_outcome_current_decision']}; raw semantics {stats['alb2012_outcome_semantics_current_decision']}; timing/geography {stats['alb2012_timing_geography_current_decision']}; questionnaire timing {stats['alb2012_questionnaire_timing_current_decision']}; fallback blocker {stats['alb2012_timing_geography_blocker_current_decision']}. This wave has questionnaire form-design evidence for date/begin/end/status/visit fields, but no verified raw household interview timing or GPS, so it cannot yet support climate exposure windows.

ALB_2005 raw timing/geography audit rows: {stats['alb2005_timing_geography_audit_rows']}. Source files scanned: {stats['alb2005_timing_geography_source_files_scanned']}. Verified interview timing rows: {stats['alb2005_interview_timing_verified_rows']}. Coordinate candidate rows: {stats['alb2005_coordinate_candidate_rows']}. Partial district name rows: {stats['alb2005_partial_district_name_nonmissing_rows']}; partial district code rows: {stats['alb2005_partial_district_code_nonmissing_rows']}. Climate-linkage-ready rows: {stats['alb2005_climate_linkage_ready_rows']}. Current decision: {stats['alb2005_timing_geography_current_decision']}.

ALB_2005 timing/geography source-search rows: {stats['alb2005_timing_geography_source_search_rows']}. Local file rows scanned: {stats['alb2005_timing_geography_source_search_local_files_scanned']}; raw-variable rows scanned: {stats['alb2005_timing_geography_source_search_local_variables_scanned']}; raw targets with hits: {stats['alb2005_timing_geography_source_search_raw_targets_with_hits']}; questionnaire targets with hits: {stats['alb2005_timing_geography_source_search_questionnaire_targets_with_hits']}. Verified household timing rows: {stats['alb2005_timing_geography_source_search_verified_household_timing_rows']}; coordinate candidate rows: {stats['alb2005_timing_geography_source_search_coordinate_candidate_rows']}; geography-crosswalk-ready rows: {stats['alb2005_timing_geography_source_search_geography_crosswalk_ready_rows']}; climate-linkage-ready rows: {stats['alb2005_timing_geography_source_search_climate_linkage_ready_rows']}. Current decision: {stats['alb2005_timing_geography_source_search_current_decision']}.

Legacy Albania questionnaire readability: {stats['albania_legacy_questionnaire_present_files']} ALB_2002/2005/2008 `.xls` questionnaire files are present and {stats['albania_legacy_questionnaire_ole_signature_files']} have legacy OLE signatures; readable files are {stats['albania_legacy_questionnaire_read_ok_files']} because `xlrd` installed={stats['albania_legacy_questionnaire_xlrd_installed']} and `soffice` available={stats['albania_legacy_questionnaire_soffice_available']}. Timing-content-ready files and climate-linkage-ready rows are {stats['albania_legacy_questionnaire_timing_content_audit_ready_rows']} and {stats['albania_legacy_questionnaire_climate_linkage_ready_rows']}. Current decision: {stats['albania_legacy_questionnaire_current_decision']}. The report is `report/albania_legacy_questionnaire_readability_audit.md`.

Legacy Albania questionnaire timing/control audit: questionnaire timing/control field rows={stats['albania_legacy_questionnaire_timing_field_rows']}; visit rows={stats['albania_legacy_questionnaire_timing_visit_rows']}; date/begin/end/status rows={stats['albania_legacy_questionnaire_timing_date_begin_end_status_rows']}; raw timing-gap rows={stats['albania_legacy_questionnaire_timing_raw_gap_rows']}; verified raw household interview timing rows across ALB_2002/2005/2008={stats['albania_legacy_questionnaire_timing_raw_verified_interview_timing_rows']} (ALB_2002={stats['alb2002_legacy_questionnaire_timing_raw_verified_interview_timing_rows']}, ALB_2005={stats['alb2005_legacy_questionnaire_timing_raw_verified_interview_timing_rows']}, ALB_2008={stats['alb2008_legacy_questionnaire_timing_raw_verified_interview_timing_rows']}). Climate-linkage-ready rows remain {stats['albania_legacy_questionnaire_timing_climate_linkage_ready_rows']}. Current decision: {stats['albania_legacy_questionnaire_timing_current_decision']}. The report is `report/albania_legacy_questionnaire_timing_field_audit.md`.

## Current Extraction Audit

{climate_status_text}

## Climate Source Probe

{climate_source_status_text}

{climate_source_role_text}

The endpoint-level source probe is `temp/climate_source_probe.csv`; the human-readable report is `report/climate_source_probe.md`. These are source-readiness checks only, not exposure construction.

Climate exposure rows currently present: {len(climate_exposures)}

Climate-linked household rows currently present: {len(climate_linked)}

## Planned Source Hierarchy

| Domain | Primary source | Fallback/robustness |
|---|---|---|
| Rainfall | CHIRPS daily/monthly precipitation | ERA5-Land or NASA POWER subset checks |
| Temperature | ERA5-Land daily statistics | NASA POWER daily API |
| Drought/water balance | SPEI and TerraClimate | CHIRPS rainfall anomaly/deficit proxies |

## No-Go Until

- raw data or official ancillary geography files are available;
- interview month/date is verified;
- geolocation quality and displacement/restriction are documented;
- auditable point/admin exposure files are produced from verified inputs.

## Implemented Fallback

`script/06_extract_climate.py` validates `data/climate_linkage_input.*`, `data/harmonized_household.*`, or `data/household_panel.*`, then extracts 1, 3, 6, and 12 month pre-interview NASA POWER daily point summaries. It does not claim CHIRPS/ERA5 primary exposure construction, z-scores, percentiles, or heatwave metrics until historical baselines and geospatial extraction are implemented.
""",
        encoding="utf-8",
    )

    (REPORT_DIR / "identification_audit.md").write_text(
        f"""# Identification Audit

Status: {'reduced-form estimates exist, but causal interpretation still depends on placebo/robustness checks' if reduced_form_estimates else 'no-go for causal estimation'}.

## Current Evidence

The project now has broad catalog screening, public metadata/schema inventories, candidate variable maps, a current fail-closed design scorecard, and public external raw schema evidence where direct archives were available. Verified harmonized outcomes, verified climate exposure variables, event rates, and placebo tests remain unavailable unless the counts below say otherwise.

## Design Scorecard State

{markdown_count_table(design_go_counts, 'Go/no-go state')}

Current design scorecard audit:

| Metric | Value |
|---|---:|
| Scorecard rows | {stats['design_scorecard_rows']} |
| Current-state rows | {stats['design_scorecard_current_rows']} |
| Audit rows | {stats['design_scorecard_audit_rows']} |
| No-go threshold rows | {stats['design_no_go_threshold_rows']} |
| Failed/not-estimable thresholds | {stats['design_no_go_failed_or_not_estimable_rows']} |
| Data-write-ready rows | {stats['design_scorecard_data_write_ready_rows']} |
| Decision | {stats['design_scorecard_current_decision']} |

{markdown_count_table(design_scorecard_current_status_counts, 'Current design scorecard audit status') if design_scorecard_current_audit else 'No current design scorecard audit rows exist yet.'}

{markdown_count_table(design_no_go_threshold_status_counts, 'Current design threshold status') if design_no_go_threshold_audit else 'No current design no-go threshold rows exist yet.'}

## Reduced-Form Gate

{markdown_count_table(causal_model_status_counts, 'Reduced-form model status') if causal_model_audit else 'No reduced-form model audit exists yet.'}

Reduced-form estimate rows: {len(reduced_form_estimates)}

## Placebo Readiness

{markdown_count_table(placebo_status_counts, 'Placebo-readiness status') if placebo_readiness else 'No placebo-readiness audit exists yet.'}

## Required Before Causal Language

- construct financial-protection/access outcomes from raw microdata;
- link verified geography and survey timing to pre-interview climate exposure;
- test seasonality and geography controls;
- run future-climate lead placebo checks;
- run alternative lag/source robustness;
- cluster or survey-design robustness;
- country leave-one-out diagnostics.
""",
        encoding="utf-8",
    )

    (REPORT_DIR / "modeling_report.md").write_text(
        f"""# Modeling Report

Status: {'some model outputs exist, but interpretation is still gated by validation and identification audits' if predictive_metrics or reduced_form_estimates or policy_sim else 'no predictive ML, causal model, causal ML, or policy-learning model has been estimated'}.

## Current Model Gate

The current design scorecard has {stats['design_scorecard_rows']} rows, including {stats['design_scorecard_current_rows']} current fail-closed rows. Decision: `{stats['design_scorecard_current_decision']}`. Data-write-ready rows: {stats['design_scorecard_data_write_ready_rows']}. Estimation remains gated unless audited analytical data, event rates, climate linkage, validation splits, and placebo-ready identifying variation exist.

{markdown_count_table(design_scorecard_current_status_counts, 'Current design audit status') if design_scorecard_current_audit else 'No current design scorecard audit rows exist yet.'}

{markdown_count_table(design_no_go_decision_counts, 'Current design no-go decision') if design_no_go_threshold_audit else 'No current design no-go threshold rows exist yet.'}

The modeling/identification readiness plan has {stats['modeling_identification_plan_rows']} dataset-outcome rows. Ready rows: predictive ML {stats['modeling_predictive_ready_rows']}, reduced-form {stats['modeling_reduced_form_ready_rows']}, causal ML {stats['modeling_causal_ml_ready_rows']}, policy learning {stats['modeling_policy_ready_rows']}. These are readiness counts only.

## Readiness Plan

Predictive gate:

{markdown_count_table(modeling_predictive_gate_counts, 'Predictive readiness status') if modeling_identification_plan else 'No modeling-identification plan exists yet.'}

Reduced-form gate:

{markdown_count_table(modeling_reduced_form_gate_counts, 'Reduced-form readiness status') if modeling_identification_plan else 'No modeling-identification plan exists yet.'}

Causal ML gate:

{markdown_count_table(modeling_causal_ml_gate_counts, 'Causal ML readiness status') if modeling_identification_plan else 'No modeling-identification plan exists yet.'}

Policy-learning gate:

{markdown_count_table(modeling_policy_gate_counts, 'Policy-learning readiness status') if modeling_identification_plan else 'No modeling-identification plan exists yet.'}

Validation-plan status:

{markdown_count_table(modeling_validation_status_counts, 'Model validation plan status') if modeling_validation_plan else 'No modeling validation plan exists yet.'}

Falsification/placebo-plan status:

{markdown_count_table(falsification_plan_status_counts, 'Falsification plan status') if falsification_placebo_plan else 'No falsification/placebo plan exists yet.'}

Policy-rule plan status:

{markdown_count_table(policy_learning_plan_status_counts, 'Policy rule plan status') if policy_learning_plan else 'No policy-learning plan exists yet.'}

## Scorecard Summary

{markdown_count_table(outcome_validity_counts, 'Outcome-validity metadata score')}

## Predictive ML

{markdown_count_table(predictive_status_counts, 'Predictive ML status') if predictive_audit else 'No predictive ML audit exists yet.'}

Validated metric rows: {len(predictive_metrics)}

## Reduced-Form Models

{markdown_count_table(causal_model_status_counts, 'Reduced-form status') if causal_model_audit else 'No reduced-form model audit exists yet.'}

Estimate rows: {len(reduced_form_estimates)}

## Causal ML and Policy Learning

{markdown_count_table(causal_ml_status_counts, 'Causal ML/policy status') if causal_ml_policy_audit else 'No causal ML/policy audit exists yet.'}

CATE rows: {len(causal_ml_cate)}

Policy simulation rows: {len(policy_sim)}

## Robustness

{markdown_count_table(robustness_status_counts, 'Robustness audit status') if robustness_audit else 'No robustness audit exists yet.'}

{markdown_count_table(robustness_result_status_counts, 'Robustness result status') if robustness_results else 'No robustness result rows exist yet.'}

## Rejected for Now

{predictive_rejected_for_now_line}
- Reduced-form causal interpretation is rejected until climate-linked outcome data, geography/timing controls, and placebo tests exist.
- Causal ML/policy learning is rejected until the reduced-form identification gate passes.
""",
        encoding="utf-8",
    )

    final_report = f"""# Final Report

Status: objective completion criteria are complete; empirical manuscript claims remain fail-closed. The current run completed official-source verification, broad country-wave screening, public documentation acquisition, public external raw archive download for matched Albania LSMS files, raw schema inspection, first-batch raw value/key summaries, ALB_2002/ALB_2005/ALB_2008/ALB_2012 temp-only household core audits, ALB_2002/ALB_2005/ALB_2008/ALB_2012 provisional outcome-feasibility diagnostics, ALB_2002/ALB_2005/ALB_2008/ALB_2012 raw outcome-semantics value audits, ALB_2002 district boundary name matching, temp-only climate centroid exposure stress testing, diagnostic climate shock flagging, ALB_2002 promotion-gate delta auditing, ALB_2002 boundary-source blocker consolidation, ALB_2002 outcome-promotion blocker consolidation, ALB_2012 fallback timing/geography blocker consolidation, ALB_2005/ALB_2008/ALB_2012 timing/geography diagnostics, candidate variable mapping, limited predictive diagnostics, limited reduced-form association diagnostics, limited robustness/placebo attempts, and a current fail-closed design scorecard.

## Executive Summary

The climate-UHC paper remains feasible enough to continue but not yet empirically validated. Official WHO/UNSD sources support the SDG 3.8.2 definition and the climate-health-system rationale. Public metadata and public Albania raw archives now provide schema-level evidence for some files, including candidate consumption, OOP, access, geography, survey-design, and shock variables. Temp-only ALB_2002, ALB_2005, ALB_2008, and ALB_2012 household cores can be assembled for review, and each now has raw provisional OOP/access event-rate diagnostics. ALB_2002, ALB_2005, ALB_2008, and ALB_2012 now have raw outcome-semantics value audits showing labelled health payment/access variables, but they still keep all OOP, access, and SDG 3.8.2 outcome promotion blocked pending unit, recall-period, missing-code, and skip-pattern review; ALB_2005, ALB_2008, and ALB_2012 additionally require gift/payment-scope policy review, and ALB_2008/ALB_2012 service-quality proxies require separate interpretation. ALB_2012 has consumption, weights, OOP/access/need/coping/service-quality proxies, shocks, and a timing/geography scan showing coarse prefecture/region/urban fields but no verified interview timing or GPS. ALB_2002 also has observed raw interview date/month and district fields plus temp-only district crosswalk, boundary name-match, boundary provenance, joined analysis-candidate, CHE candidate outcome, climate centroid exposure stress-test, and within-candidate climate shock diagnostic audits, but climate linkage remains blocked because historical 2002 boundaries are not verified, primary CHIRPS/ERA5 extraction and historical baselines are not accepted, and no-GPS admin aggregation would have measurement error. {predictive_summary_sentence}

## Current Coverage

| Artifact | Count |
|---|---:|
| Country-wave screening rows | {len(screening)} |
| Manual download manifest rows | {len(manual)} |
| Manual file/module checklist rows | {len(manual_file_checklist)} |
| Manual access action rows | {len(manual_access_actions)} |
| Acquisition progress rows | {len(acquisition_progress)} |
| External repository probe rows | {len(external_probe)} |
| Public external raw candidate rows | {stats['public_external_download_rows']} |
| Public external raw archives downloaded/existing | {stats['public_external_downloaded_rows']} |
| Public external datasets with raw archives | {stats['public_external_dataset_rows']} |
| World Bank public documentation audit rows | {len(worldbank_public_docs)} |
| World Bank public documentation resources saved | {stats['worldbank_public_docs_saved']} |
| World Bank Get Microdata access gates detected | {stats['worldbank_get_microdata_gates']} |
| Raw download manifest rows | {len(raw_download_manifest)} |
| Raw download intake target rows | {stats['raw_download_intake_rows']} |
| Raw download expected-file rows | {stats['raw_download_expected_rows']} |
| Raw download intake targets ready for schema | {stats['raw_download_intake_ready_rows']} |
| Raw download expected files not present | {stats['raw_download_expected_not_present_rows']} |
| Raw-like files under raw downloads | {stats['raw_download_raw_like_files']} |
| Target folders with raw-like files | {stats['raw_download_raw_like_targets']} |
| First-batch raw acquisition dataset rows | {stats['first_batch_checklist_rows']} |
| First-batch raw acquisition countries | {stats['first_batch_country_count']} |
| First-batch file target rows | {stats['first_batch_file_target_rows']} |
| First-batch raw tabular files present | {stats['first_batch_raw_tabular_file_rows']} |
| First-batch raw archives present | {stats['first_batch_archive_file_rows']} |
| First-batch official access probe rows | {stats['first_batch_access_probe_rows']} |
| First-batch access gates detected | {stats['first_batch_access_gate_rows']} |
| First-batch possible direct raw routes | {stats['first_batch_possible_direct_raw_rows']} |
| First-batch manual handoff rows | {stats['first_batch_handoff_rows']} |
| First-batch manual file-queue rows | {stats['first_batch_file_queue_rows']} |
| First-batch handoff rows needing manual account/terms | {stats['first_batch_handoff_manual_required_rows']} |
| First-batch public documentation resource rows | {stats['first_batch_documentation_rows']} |
| First-batch public documentation saved/reused rows | {stats['first_batch_documentation_saved_rows']} |
| First-batch public documentation failed rows | {stats['first_batch_documentation_failed_rows']} |
| First-batch file-source trace rows | {stats['first_batch_file_source_trace_rows']} |
| First-batch file-source supported rows | {stats['first_batch_file_source_supported_rows']} |
| First-batch file-source unsupported rows | {stats['first_batch_file_source_unsupported_rows']} |
| First-batch merge-key lineage plan rows | {stats['first_batch_merge_key_plan_rows']} |
| First-batch merge-key candidate rows | {stats['first_batch_merge_key_candidate_rows']} |
| First-batch merge-key planned rows | {stats['first_batch_merge_key_planned_rows']} |
| First-batch merge-key raw-ready rows | {stats['first_batch_merge_key_raw_ready_rows']} |
| First-batch raw value audit rows | {stats['first_batch_value_key_audit_rows']} |
| First-batch raw value read-ok rows | {stats['first_batch_value_key_read_ok_rows']} |
| First-batch raw key audit rows | {stats['first_batch_raw_key_audit_rows']} |
| First-batch raw key read-ok rows | {stats['first_batch_raw_key_read_ok_rows']} |
| First-batch auto value-audit rows | {stats['first_batch_auto_value_audit_rows']} |
| First-batch auto value-audit ready rows | {stats['first_batch_auto_value_audit_ready_rows']} |
| ALB_2002 temp household-core candidate rows | {stats['alb2002_household_core_candidate_rows']} |
| ALB_2002 households with total consumption | {stats['alb2002_households_with_total_consumption']} |
| ALB_2002 households with household weight | {stats['alb2002_households_with_household_weight']} |
| ALB_2002 weight-design positive weight rows | {stats['alb2002_weight_design_positive_weight_rows']} |
| ALB_2002 weight-design key-match rows | {stats['alb2002_weight_design_candidate_key_match_rows']} |
| ALB_2002 weight-design distinct PSUs | {stats['alb2002_weight_design_distinct_psu_rows']} |
| ALB_2002 weight-design distinct strata | {stats['alb2002_weight_design_distinct_stratum_rows']} |
| ALB_2002 weighted-inference-ready rows | {stats['alb2002_weight_design_weighted_inference_ready_rows']} |
| ALB_2002 households with positive unreviewed 4-week OOP | {stats['alb2002_households_with_oop_4w_positive']} |
| ALB_2002 households with positive unreviewed 12-month OOP | {stats['alb2002_households_with_oop_12m_positive']} |
| ALB_2002 households with district code | {stats['alb2002_households_with_district_code']} |
| ALB_2002 households with survey month | {stats['alb2002_households_with_survey_month']} |
| ALB_2002 households with interview date | {stats['alb2002_households_with_interview_date']} |
| ALB_2002 household-core recipe-ready rows | {stats['alb2002_household_core_recipe_ready_rows']} |
| ALB_2002 household-core decision | {stats['alb2002_household_core_current_decision']} |
| ALB_2002 provisional outcome feasibility rows | {stats['alb2002_provisional_outcome_audit_rows']} |
| ALB_2002 provisional financial stress-test rows | {stats['alb2002_provisional_financial_stress_test_rows']} |
| ALB_2002 provisional access proxy rows | {stats['alb2002_provisional_access_proxy_rows']} |
| ALB_2002 provisional low-event-rate rows | {stats['alb2002_provisional_low_event_rate_rows']} |
| ALB_2002 provisional outcome-ready rows | {stats['alb2002_provisional_outcome_ready_rows']} |
| ALB_2002 provisional outcome decision | {stats['alb2002_provisional_outcome_current_decision']} |
| ALB_2002 raw outcome-semantics rows | {stats['alb2002_outcome_semantics_raw_value_rows']} |
| ALB_2002 raw semantics OOP candidate rows | {stats['alb2002_outcome_semantics_financial_oop_candidate_rows']} |
| ALB_2002 raw semantics access candidate rows | {stats['alb2002_outcome_semantics_access_candidate_rows']} |
| ALB_2002 raw semantics value-label rows | {stats['alb2002_outcome_semantics_rows_with_value_labels']} |
| ALB_2002 raw semantics outcome-ready rows | {stats['alb2002_outcome_semantics_outcome_ready_rows']} |
| ALB_2002 raw semantics SDG 3.8.2-ready rows | {stats['alb2002_outcome_semantics_sdg382_ready_rows']} |
| ALB_2002 raw semantics decision | {stats['alb2002_outcome_semantics_current_decision']} |
| ALB_2002 health questionnaire semantics rows | {stats['alb2002_health_questionnaire_semantics_rows']} |
| ALB_2002 health questionnaire NEW LEKS rows | {stats['alb2002_health_questionnaire_new_lek_unit_rows']} |
| ALB_2002 health questionnaire four-week OOP rows | {stats['alb2002_health_questionnaire_four_week_oop_rows']} |
| ALB_2002 health questionnaire twelve-month OOP rows | {stats['alb2002_health_questionnaire_twelve_month_oop_rows']} |
| ALB_2002 health questionnaire payment positive skip leaks | {stats['alb2002_health_questionnaire_payment_positive_when_not_triggered_rows']} |
| ALB_2002 health questionnaire outcome-ready rows | {stats['alb2002_health_questionnaire_outcome_ready_rows']} |
| ALB_2002 health questionnaire decision | {stats['alb2002_health_questionnaire_current_decision']} |
| ALB_2002 OOP aggregation policy rows | {stats['alb2002_oop_aggregation_policy_rows']} |
| ALB_2002 OOP aggregation max CHE10 stress-test rate | {stats['alb2002_oop_aggregation_policy_max_che10_rate']} |
| ALB_2002 OOP aggregation max CHE25 stress-test rate | {stats['alb2002_oop_aggregation_policy_max_che25_rate']} |
| ALB_2002 OOP aggregation core four-week match rows | {stats['alb2002_oop_aggregation_policy_core_4w_match_rows']} |
| ALB_2002 OOP aggregation core twelve-month match rows | {stats['alb2002_oop_aggregation_policy_core_12m_match_rows']} |
| ALB_2002 OOP aggregation outcome-ready rows | {stats['alb2002_oop_aggregation_policy_outcome_ready_rows']} |
| ALB_2002 OOP aggregation SDG 3.8.2-ready rows | {stats['alb2002_oop_aggregation_policy_sdg382_ready_rows']} |
| ALB_2002 OOP aggregation climate-linkage-ready rows | {stats['alb2002_oop_aggregation_policy_climate_linkage_ready_rows']} |
| ALB_2002 OOP aggregation policy decision | {stats['alb2002_oop_aggregation_policy_current_decision']} |
| ALB_2002 skip/missing semantics rows | {stats['alb2002_skip_missing_semantics_rows']} |
| ALB_2002 skip/missing positive skipped-payment rows | {stats['alb2002_skip_missing_payment_positive_when_not_triggered_rows']} |
| ALB_2002 skip/missing zero skipped-payment cells | {stats['alb2002_skip_missing_payment_zero_cells_when_not_triggered']} |
| ALB_2002 skip/missing positive skipped-payment cells | {stats['alb2002_skip_missing_payment_positive_cells_when_not_triggered']} |
| ALB_2002 skip/missing outcome-ready rows | {stats['alb2002_skip_missing_outcome_ready_rows']} |
| ALB_2002 skip/missing SDG 3.8.2-ready rows | {stats['alb2002_skip_missing_sdg382_ready_rows']} |
| ALB_2002 skip/missing climate-linkage-ready rows | {stats['alb2002_skip_missing_climate_linkage_ready_rows']} |
| ALB_2002 skip/missing decision | {stats['alb2002_skip_missing_current_decision']} |
| ALB_2002 OOP skip-value decision rows | {stats['alb2002_oop_skip_value_decision_rows']} |
| ALB_2002 OOP skip-value zero skipped-payment cells | {stats['alb2002_oop_skip_value_payment_zero_skipped_cells']} |
| ALB_2002 OOP skip-value positive skipped-payment rows | {stats['alb2002_oop_skip_value_payment_positive_skipped_rows']} |
| ALB_2002 OOP skip-value positive skipped-payment cells | {stats['alb2002_oop_skip_value_payment_positive_skipped_cells']} |
| ALB_2002 OOP skip-value zero-skip ready rows | {stats['alb2002_oop_skip_value_zero_skip_policy_ready_rows']} |
| ALB_2002 OOP skip-value decision | {stats['alb2002_oop_skip_value_current_decision']} |
| ALB_2002 access/need denominator policy rows | {stats['alb2002_access_need_denominator_policy_rows']} |
| ALB_2002 access/need q01 need rows | {stats['alb2002_access_need_q01_need_rows']} |
| ALB_2002 access/need person-need rows | {stats['alb2002_access_need_person_need_household_rows']} |
| ALB_2002 access/need composite any-barrier rows | {stats['alb2002_access_need_composite_any_access_barrier_rows']} |
| ALB_2002 access/need low-event rows | {stats['alb2002_access_need_low_event_rate_rows']} |
| ALB_2002 access/need outcome-ready rows | {stats['alb2002_access_need_outcome_ready_rows']} |
| ALB_2002 access/need climate-linkage-ready rows | {stats['alb2002_access_need_climate_linkage_ready_rows']} |
| ALB_2002 access/need decision | {stats['alb2002_access_need_current_decision']} |
| ALB_2002 consumption/SDG denominator policy rows | {stats['alb2002_consumption_sdg_denominator_policy_rows']} |
| ALB_2002 positive total-consumption rows | {stats['alb2002_consumption_sdg_positive_total_consumption_rows']} |
| ALB_2002 diagnostic four-week CHE10 rate | {stats['alb2002_consumption_sdg_che10_4w_unreviewed_rate']} |
| ALB_2002 diagnostic twelve-month CHE25 rate | {stats['alb2002_consumption_sdg_che25_12m_unreviewed_rate']} |
| ALB_2002 SPL-ready rows | {stats['alb2002_consumption_sdg_spl_ready_rows']} |
| ALB_2002 PPP/CPI-ready rows | {stats['alb2002_consumption_sdg_ppp_cpi_ready_rows']} |
| ALB_2002 discretionary-budget-ready rows | {stats['alb2002_consumption_sdg_discretionary_budget_ready_rows']} |
| ALB_2002 SDG 3.8.2 denominator-ready rows | {stats['alb2002_consumption_sdg_sdg382_ready_rows']} |
| ALB_2002 consumption/SDG decision | {stats['alb2002_consumption_sdg_current_decision']} |
| ALB_2002 construction source audit rows | {stats['alb2002_consumption_construction_source_audit_rows']} |
| ALB_2002 construction `.do` file rows | {stats['alb2002_consumption_construction_do_file_rows']} |
| ALB_2002 construction documentation-ready rows | {stats['alb2002_consumption_construction_documentation_ready_rows']} |
| ALB_2002 construction released-variable mapping-ready rows | {stats['alb2002_consumption_construction_released_variable_mapping_ready_rows']} |
| ALB_2002 construction denominator variant-ready rows | {stats['alb2002_consumption_construction_denominator_variant_ready_rows']} |
| ALB_2002 aggregate crosswalk rows | {stats['alb2002_consumption_aggregate_crosswalk_rows']} |
| ALB_2002 raw `totcons`/candidate match rows | {stats['alb2002_consumption_aggregate_crosswalk_candidate_totcons_match_rows']} |
| ALB_2002 aggregate metadata catalog rows | {stats['alb2002_consumption_aggregate_crosswalk_metadata_catalog_rows']} |
| ALB_2002 official aggregate documentation-ready rows | {stats['alb2002_consumption_aggregate_crosswalk_official_documentation_ready_rows']} |
| ALB_2002 aggregate crosswalk decision | {stats['alb2002_consumption_aggregate_crosswalk_current_decision']} |
| ALB_2002 CHE candidate household rows | {stats['alb2002_che_candidate_household_rows']} |
| ALB_2002 CHE candidate denominator rows | {stats['alb2002_che_candidate_denominator_rows']} |
| ALB_2002 CHE candidate CHE10 rows | {stats['alb2002_che_candidate_che10_rows']} |
| ALB_2002 CHE candidate CHE10 rate | {stats['alb2002_che_candidate_che10_rate']} |
| ALB_2002 CHE candidate weighted CHE10 rate | {stats['alb2002_che_candidate_che10_weighted_rate']} |
| ALB_2002 CHE candidate CHE25 rows | {stats['alb2002_che_candidate_che25_rows']} |
| ALB_2002 CHE candidate CHE25 rate | {stats['alb2002_che_candidate_che25_rate']} |
| ALB_2002 CHE candidate weighted CHE25 rate | {stats['alb2002_che_candidate_che25_weighted_rate']} |
| ALB_2002 CHE candidate outcome-promotion-ready rows | {stats['alb2002_che_candidate_outcome_promotion_ready_rows']} |
| ALB_2002 CHE candidate climate-linkage-ready rows | {stats['alb2002_che_candidate_climate_linkage_ready_rows']} |
| ALB_2002 CHE candidate decision | {stats['alb2002_che_candidate_current_decision']} |
| ALB_2002 access candidate household rows | {stats['alb2002_access_candidate_household_rows']} |
| ALB_2002 access candidate q01 need rows | {stats['alb2002_access_candidate_q01_need_rows']} |
| ALB_2002 access candidate person-need rows | {stats['alb2002_access_candidate_person_need_rows']} |
| ALB_2002 access candidate composite any-barrier rows | {stats['alb2002_access_candidate_composite_any_rows']} |
| ALB_2002 access candidate weighted any-barrier rate | {stats['alb2002_access_candidate_composite_any_weighted_rate']} |
| ALB_2002 access candidate outcome-promotion-ready rows | {stats['alb2002_access_candidate_outcome_promotion_ready_rows']} |
| ALB_2002 access candidate climate-linkage-ready rows | {stats['alb2002_access_candidate_climate_linkage_ready_rows']} |
| ALB_2002 access candidate decision | {stats['alb2002_access_candidate_current_decision']} |
| ALB_2002 UHC composite candidate rows | {stats['alb2002_uhc_composite_candidate_household_rows']} |
| ALB_2002 UHC composite CHE10-or-access rows | {stats['alb2002_uhc_composite_candidate_che10_or_access_rows']} |
| ALB_2002 UHC composite weighted CHE10-or-access rate | {stats['alb2002_uhc_composite_candidate_che10_or_access_weighted_rate']} |
| ALB_2002 UHC composite CHE25-or-access rows | {stats['alb2002_uhc_composite_candidate_che25_or_access_rows']} |
| ALB_2002 UHC composite coping rows | {stats['alb2002_uhc_composite_candidate_coping_rows']} |
| ALB_2002 UHC composite outcome-promotion-ready rows | {stats['alb2002_uhc_composite_candidate_outcome_promotion_ready_rows']} |
| ALB_2002 UHC composite climate-linkage-ready rows | {stats['alb2002_uhc_composite_candidate_climate_linkage_ready_rows']} |
| ALB_2002 UHC composite decision | {stats['alb2002_uhc_composite_candidate_current_decision']} |
| ALB_2002 analysis candidate rows | {stats['alb2002_analysis_candidate_rows']} |
| ALB_2002 analysis candidate columns | {stats['alb2002_analysis_candidate_columns']} |
| ALB_2002 analysis candidate complete gates | {stats['alb2002_analysis_candidate_complete_candidate_gates']} |
| ALB_2002 analysis candidate missing gates | {stats['alb2002_analysis_candidate_missing_gates']} |
| ALB_2002 analysis candidate blocked promotion gates | {stats['alb2002_analysis_candidate_blocked_promotion_gates']} |
| ALB_2002 analysis candidate harmonized-ready rows | {stats['alb2002_analysis_candidate_harmonized_ready_rows']} |
| ALB_2002 analysis candidate data-write-ready rows | {stats['alb2002_analysis_candidate_data_write_ready_rows']} |
| ALB_2002 analysis candidate decision | {stats['alb2002_analysis_candidate_current_decision']} |
| ALB_2002 minimum recipe promotion action rows | {stats['alb2002_minimum_recipe_promotion_action_rows']} |
| ALB_2002 minimum recipe promotion gate rows | {stats['alb2002_minimum_recipe_promotion_gate_rows']} |
| ALB_2002 minimum recipe promotion blocked gates | {stats['alb2002_minimum_recipe_promotion_blocked_gates']} |
| ALB_2002 minimum recipe promotion candidate gates | {stats['alb2002_minimum_recipe_promotion_candidate_gates']} |
| ALB_2002 minimum recipe harmonized-ready rows | {stats['alb2002_minimum_recipe_promotion_harmonized_ready_rows']} |
| ALB_2002 minimum recipe outcome-ready rows | {stats['alb2002_minimum_recipe_promotion_outcome_ready_rows']} |
| ALB_2002 minimum recipe SDG 3.8.2-ready rows | {stats['alb2002_minimum_recipe_promotion_sdg382_ready_rows']} |
| ALB_2002 minimum recipe climate-linkage-ready rows | {stats['alb2002_minimum_recipe_promotion_climate_linkage_ready_rows']} |
| ALB_2002 minimum recipe promotion decision | {stats['alb2002_minimum_recipe_promotion_current_decision']} |
| ALB_2002 district crosswalk template rows | {stats['alb2002_district_crosswalk_template_rows']} |
| ALB_2002 district groups | {stats['alb2002_district_crosswalk_district_rows']} |
| ALB_2002 boundary probe rows | {stats['alb2002_district_crosswalk_source_probe_rows']} |
| ALB_2002 boundary probe reachable rows | {stats['alb2002_district_crosswalk_source_reachable_rows']} |
| ALB_2002 boundary ADM unit count | {stats['alb2002_district_crosswalk_adm_unit_count']} |
| ALB_2002 district names needing encoding review | {stats['alb2002_district_crosswalk_name_encoding_review_rows']} |
| ALB_2002 district crosswalk-ready rows | {stats['alb2002_district_crosswalk_ready_rows']} |
| ALB_2002 climate-linkage-ready rows | {stats['alb2002_climate_linkage_ready_rows']} |
| ALB_2002 district crosswalk decision | {stats['alb2002_district_crosswalk_current_decision']} |
| ALB_2002 boundary name-match rows | {stats['alb2002_boundary_name_match_rows']} |
| ALB_2002 boundary GeoJSON features | {stats['alb2002_boundary_geojson_feature_rows']} |
| ALB_2002 boundary exact name matches | {stats['alb2002_boundary_name_match_exact_rows']} |
| ALB_2002 boundary mojibake-repaired matches | {stats['alb2002_boundary_name_match_euro_repaired_rows']} |
| ALB_2002 unmatched survey district rows | {stats['alb2002_boundary_name_match_unmatched_survey_rows']} |
| ALB_2002 duplicate boundary-name keys | {stats['alb2002_boundary_name_match_duplicate_boundary_name_keys']} |
| ALB_2002 boundary historical-ready rows | {stats['alb2002_boundary_name_match_historical_year_ready_rows']} |
| ALB_2002 boundary climate-linkage-ready rows | {stats['alb2002_boundary_name_match_climate_linkage_ready_rows']} |
| ALB_2002 boundary name-match decision | {stats['alb2002_boundary_name_match_current_decision']} |
| ALB_2002 boundary source alternatives audited | {stats['alb2002_boundary_source_alternative_rows']} |
| ALB_2002 boundary source alternatives reachable/local rows | {stats['alb2002_boundary_source_alternative_reachable_rows']} |
| ALB_2002 source alternatives with LSMS map documentation flags | {stats['alb2002_boundary_source_alternative_lsms_maps_documented_rows']} |
| ALB_2002 source alternatives with GPS documentation flags | {stats['alb2002_boundary_source_alternative_gps_documented_rows']} |
| ALB_2002 source-alternative historical-ready rows | {stats['alb2002_boundary_source_alternative_historical_ready_rows']} |
| ALB_2002 source-alternative climate-linkage-ready rows | {stats['alb2002_boundary_source_alternative_climate_linkage_ready_rows']} |
| ALB_2002 boundary source-alternative decision | {stats['alb2002_boundary_source_alternative_current_decision']} |
| ALB_2002 boundary resource candidates parsed/probed | {stats['alb2002_boundary_resource_search_candidate_rows']} |
| ALB_2002 boundary resources with complete name coverage | {stats['alb2002_boundary_resource_search_complete_name_coverage_rows']} |
| ALB_2002 boundary resources with exact unit count | {stats['alb2002_boundary_resource_search_exact_unit_count_rows']} |
| ALB_2002 best boundary resource lead | {stats['alb2002_boundary_resource_search_best_candidate_id']} |
| ALB_2002 best resource exact/repaired/alias matches | {stats['alb2002_boundary_resource_search_best_candidate_exact_matches']}/{stats['alb2002_boundary_resource_search_best_candidate_repaired_matches']}/{stats['alb2002_boundary_resource_search_best_candidate_alias_matches']} |
| ALB_2002 boundary resource historical-ready rows | {stats['alb2002_boundary_resource_search_2002_historical_ready_rows']} |
| ALB_2002 boundary resource climate-linkage-ready rows | {stats['alb2002_boundary_resource_search_climate_linkage_ready_rows']} |
| ALB_2002 boundary resource-search decision | {stats['alb2002_boundary_resource_search_current_decision']} |
| ALB_2002 geometry/provenance feature rows | {stats['alb2002_boundary_geometry_feature_rows']} |
| ALB_2002 geometry coordinate-structure-ok rows | {stats['alb2002_boundary_geometry_coordinate_structure_ok_rows']} |
| ALB_2002 geometry survey-key matched rows | {stats['alb2002_boundary_geometry_survey_key_matched_rows']} |
| ALB_2002 boundary metadata year | {stats['alb2002_boundary_geometry_metadata_boundary_year']} |
| ALB_2002 boundary metadata source | {stats['alb2002_boundary_geometry_metadata_boundary_source']} |
| ALB_2002 boundary-year-matches-2002 rows | {stats['alb2002_boundary_geometry_boundary_year_matches_2002_rows']} |
| ALB_2002 topology-validated rows | {stats['alb2002_boundary_geometry_topology_validated_rows']} |
| ALB_2002 geometry historical-ready rows | {stats['alb2002_boundary_geometry_historical_2002_boundary_ready_rows']} |
| ALB_2002 geometry climate-linkage-ready rows | {stats['alb2002_boundary_geometry_climate_linkage_ready_rows']} |
| ALB_2002 boundary geometry/provenance decision | {stats['alb2002_boundary_geometry_current_decision']} |
| ALB_2002 manual boundary verification action rows | {stats['alb2002_boundary_manual_verification_action_rows']} |
| ALB_2002 manual boundary verification gate rows | {stats['alb2002_boundary_manual_verification_gate_rows']} |
| ALB_2002 manual boundary verification blocked gates | {stats['alb2002_boundary_manual_verification_blocked_gates']} |
| ALB_2002 manual boundary pre-2011 digital-map absence rows | {stats['alb2002_boundary_manual_verification_pre2011_digital_map_absence_rows']} |
| ALB_2002 manual boundary verification climate-linkage-ready rows | {stats['alb2002_boundary_manual_verification_climate_linkage_ready_rows']} |
| ALB_2002 manual boundary verification decision | {stats['alb2002_boundary_manual_verification_current_decision']} |
| ALB_2002 manual source follow-up rows | {stats['alb2002_boundary_manual_source_followup_rows']} |
| ALB_2002 manual source follow-up conclusive blockers | {stats['alb2002_boundary_manual_source_followup_conclusive_blocker_rows']} |
| ALB_2002 manual source follow-up district-level-ready rows | {stats['alb2002_boundary_manual_source_followup_district_level_ready_rows']} |
| ALB_2002 manual source follow-up climate-linkage-ready rows | {stats['alb2002_boundary_manual_source_followup_climate_linkage_ready_rows']} |
| ALB_2002 IHGIS follow-up status | {stats['alb2002_boundary_manual_source_followup_ipums_level_status']} |
| ALB_2002 UNECE/INSTAT pre-2011 map status | {stats['alb2002_boundary_manual_source_followup_unece_pre2011_map_status']} |
| ALB_2002 manual source follow-up decision | {stats['alb2002_boundary_manual_source_followup_current_decision']} |
| ALB_2002 GADM boundary candidates | {stats['alb2002_gadm_boundary_lead_candidate_rows']} |
| ALB_2002 GADM 3.6 ADM2 rows | {stats['alb2002_gadm36_adm2_row_count']} |
| ALB_2002 GADM 3.6 normalized keys | {stats['alb2002_gadm36_distinct_normalized_key_count']} |
| ALB_2002 GADM 3.6 complete name coverage | {stats['alb2002_gadm36_complete_name_coverage_rows']} |
| ALB_2002 GADM 3.6 duplicate keys | {stats['alb2002_gadm36_duplicate_boundary_key_count']} |
| ALB_2002 GADM climate-linkage-ready rows | {stats['alb2002_gadm_boundary_lead_climate_linkage_ready_rows']} |
| ALB_2002 GADM decision | {stats['alb2002_gadm_boundary_lead_current_decision']} |
| ALB_2002 local geography artifact files scanned | {stats['alb2002_local_geo_artifact_files_scanned']} |
| ALB_2002 questionnaire coordinate fields | {stats['alb2002_local_geo_artifact_questionnaire_coordinate_field_rows']} |
| ALB_2002 raw coordinate variable rows | {stats['alb2002_local_geo_artifact_coordinate_raw_variable_rows']} |
| ALB_2002 local GIS/boundary file candidates | {stats['alb2002_local_geo_artifact_gis_file_candidate_rows']} |
| ALB_2002 local admin/sampling geography variables | {stats['alb2002_local_geo_artifact_admin_variable_rows']} |
| ALB_2002 local-coordinate-ready rows | {stats['alb2002_local_geo_artifact_local_coordinate_ready_rows']} |
| ALB_2002 local-boundary-ready rows | {stats['alb2002_local_geo_artifact_local_boundary_ready_rows']} |
| ALB_2002 local-artifact climate-linkage-ready rows | {stats['alb2002_local_geo_artifact_climate_linkage_ready_rows']} |
| ALB_2002 local geography artifact decision | {stats['alb2002_local_geo_artifact_current_decision']} |
| ALB_2012 temp household-core candidate rows | {stats['alb2012_household_core_candidate_rows']} |
| ALB_2012 households with total consumption | {stats['alb2012_households_with_total_consumption']} |
| ALB_2012 households with household weight | {stats['alb2012_households_with_household_weight']} |
| ALB_2012 households with prefecture | {stats['alb2012_households_with_prefecture']} |
| ALB_2012 households with region | {stats['alb2012_households_with_region']} |
| ALB_2012 households with survey month | {stats['alb2012_households_with_survey_month']} |
| ALB_2012 households with interview date | {stats['alb2012_households_with_interview_date']} |
| ALB_2012 positive unreviewed 4-week OOP rows | {stats['alb2012_households_with_oop_4w_positive']} |
| ALB_2012 positive unreviewed 12-month OOP rows | {stats['alb2012_households_with_oop_12m_positive']} |
| ALB_2012 access affordability proxy rows | {stats['alb2012_households_with_access_affordability_proxy']} |
| ALB_2012 shock signal rows | {stats['alb2012_households_with_shock_any_2008_2012']} |
| ALB_2012 household-core recipe-ready rows | {stats['alb2012_household_core_recipe_ready_rows']} |
| ALB_2012 climate-linkage-ready rows | {stats['alb2012_climate_linkage_ready_rows']} |
| ALB_2012 raw core decision | {stats['alb2012_raw_core_current_decision']} |
| ALB_2012 provisional outcome feasibility rows | {stats['alb2012_provisional_outcome_audit_rows']} |
| ALB_2012 provisional financial stress-test rows | {stats['alb2012_provisional_financial_stress_test_rows']} |
| ALB_2012 provisional access proxy rows | {stats['alb2012_provisional_access_proxy_rows']} |
| ALB_2012 provisional need proxy rows | {stats['alb2012_provisional_need_proxy_rows']} |
| ALB_2012 provisional low-event-rate rows | {stats['alb2012_provisional_low_event_rate_rows']} |
| ALB_2012 provisional outcome-ready rows | {stats['alb2012_provisional_outcome_ready_rows']} |
| ALB_2012 provisional climate-linkage-ready rows | {stats['alb2012_provisional_climate_linkage_ready_rows']} |
| ALB_2012 provisional outcome decision | {stats['alb2012_provisional_outcome_current_decision']} |
| ALB_2012 outcome-semantics raw value rows | {stats['alb2012_outcome_semantics_raw_value_rows']} |
| ALB_2012 outcome-semantics financial OOP candidates | {stats['alb2012_outcome_semantics_financial_oop_candidate_rows']} |
| ALB_2012 outcome-semantics gift/payment candidates | {stats['alb2012_outcome_semantics_gift_candidate_rows']} |
| ALB_2012 outcome-semantics access candidates | {stats['alb2012_outcome_semantics_access_candidate_rows']} |
| ALB_2012 outcome-semantics service-quality proxies | {stats['alb2012_outcome_semantics_service_quality_proxy_rows']} |
| ALB_2012 outcome-semantics outcome-ready rows | {stats['alb2012_outcome_semantics_outcome_ready_rows']} |
| ALB_2012 outcome-semantics SDG 3.8.2-ready rows | {stats['alb2012_outcome_semantics_sdg382_ready_rows']} |
| ALB_2012 outcome-semantics climate-linkage-ready rows | {stats['alb2012_outcome_semantics_climate_linkage_ready_rows']} |
| ALB_2012 outcome-semantics decision | {stats['alb2012_outcome_semantics_current_decision']} |
| ALB_2012 timing/geography audit rows | {stats['alb2012_timing_geography_audit_rows']} |
| ALB_2012 timing/geography source files scanned | {stats['alb2012_timing_geography_source_files_scanned']} |
| ALB_2012 interview timing candidate rows | {stats['alb2012_interview_timing_candidate_rows']} |
| ALB_2012 verified interview timing rows | {stats['alb2012_interview_timing_verified_rows']} |
| ALB_2012 coordinate candidate rows | {stats['alb2012_coordinate_candidate_rows']} |
| ALB_2012 coarse full-coverage geography rows | {stats['alb2012_coarse_full_coverage_geography_candidate_rows']} |
| ALB_2012 coarse geography household rows | {stats['alb2012_coarse_geography_household_rows']} |
| ALB_2012 timing/geography climate-linkage-ready rows | {stats['alb2012_timing_geography_climate_linkage_ready_rows']} |
| ALB_2012 timing/geography decision | {stats['alb2012_timing_geography_current_decision']} |
| ALB_2012 questionnaire timing field rows | {stats['alb2012_questionnaire_timing_field_rows']} |
| ALB_2012 questionnaire visit rows | {stats['alb2012_questionnaire_timing_visit_rows']} |
| ALB_2012 questionnaire date/begin/end/status rows | {stats['alb2012_questionnaire_timing_date_begin_end_status_rows']} |
| ALB_2012 raw timing-gap rows | {stats['alb2012_questionnaire_timing_raw_gap_rows']} |
| ALB_2012 raw control timing candidate rows | {stats['alb2012_questionnaire_timing_raw_control_candidate_rows']} |
| ALB_2012 raw verified interview timing rows after questionnaire audit | {stats['alb2012_questionnaire_timing_raw_verified_interview_timing_rows']} |
| ALB_2012 questionnaire timing climate-linkage-ready rows | {stats['alb2012_questionnaire_timing_climate_linkage_ready_rows']} |
| ALB_2012 questionnaire timing decision | {stats['alb2012_questionnaire_timing_current_decision']} |
| Albania legacy questionnaire files present | {stats['albania_legacy_questionnaire_present_files']} |
| Albania legacy questionnaire readable files | {stats['albania_legacy_questionnaire_read_ok_files']} |
| Albania legacy questionnaire missing-reader blocked files | {stats['albania_legacy_questionnaire_missing_reader_blocked_files']} |
| Albania legacy questionnaire timing-content-ready rows | {stats['albania_legacy_questionnaire_timing_content_audit_ready_rows']} |
| Albania legacy questionnaire climate-linkage-ready rows | {stats['albania_legacy_questionnaire_climate_linkage_ready_rows']} |
| Albania legacy questionnaire readability decision | {stats['albania_legacy_questionnaire_current_decision']} |
| Albania legacy questionnaire timing/control field rows | {stats['albania_legacy_questionnaire_timing_field_rows']} |
| Albania legacy questionnaire timing visit rows | {stats['albania_legacy_questionnaire_timing_visit_rows']} |
| Albania legacy questionnaire timing date/begin/end/status rows | {stats['albania_legacy_questionnaire_timing_date_begin_end_status_rows']} |
| Albania legacy questionnaire raw timing-gap rows | {stats['albania_legacy_questionnaire_timing_raw_gap_rows']} |
| Albania legacy questionnaire verified raw interview timing rows | {stats['albania_legacy_questionnaire_timing_raw_verified_interview_timing_rows']} |
| Albania legacy questionnaire timing climate-linkage-ready rows | {stats['albania_legacy_questionnaire_timing_climate_linkage_ready_rows']} |
| Albania legacy questionnaire timing decision | {stats['albania_legacy_questionnaire_timing_current_decision']} |
| ALB_2005 documented evidence rows | {stats['alb2005_documented_evidence_rows']} |
| ALB_2005 future recipe candidate rows | {stats['alb2005_future_recipe_candidate_rows']} |
| ALB_2005 false-positive rows | {stats['alb2005_false_positive_rows']} |
| ALB_2005 timing/geography blocker rows | {stats['alb2005_timing_or_geography_blocker_rows']} |
| ALB_2005 recipe-ready rows | {stats['alb2005_recipe_ready_rows']} |
| ALB_2005 temp household-core candidate rows | {stats['alb2005_household_core_candidate_rows']} |
| ALB_2005 households with total consumption | {stats['alb2005_households_with_total_consumption']} |
| ALB_2005 households with household weight | {stats['alb2005_households_with_household_weight']} |
| ALB_2005 households with positive unreviewed 4-week OOP | {stats['alb2005_households_with_oop_4w_positive']} |
| ALB_2005 households with partial district code | {stats['alb2005_households_with_partial_district_code']} |
| ALB_2005 households with verified survey month | {stats['alb2005_households_with_survey_month']} |
| ALB_2005 household-core recipe-ready rows | {stats['alb2005_household_core_recipe_ready_rows']} |
| ALB_2005 provisional outcome feasibility rows | {stats['alb2005_provisional_outcome_audit_rows']} |
| ALB_2005 provisional financial stress-test rows | {stats['alb2005_provisional_financial_stress_test_rows']} |
| ALB_2005 provisional access proxy rows | {stats['alb2005_provisional_access_proxy_rows']} |
| ALB_2005 provisional low-event-rate rows | {stats['alb2005_provisional_low_event_rate_rows']} |
| ALB_2005 provisional outcome-ready rows | {stats['alb2005_provisional_outcome_ready_rows']} |
| ALB_2005 provisional outcome decision | {stats['alb2005_provisional_outcome_current_decision']} |
| ALB_2005 outcome-semantics raw value rows | {stats['alb2005_outcome_semantics_raw_value_rows']} |
| ALB_2005 outcome-semantics financial OOP candidates | {stats['alb2005_outcome_semantics_financial_oop_candidate_rows']} |
| ALB_2005 outcome-semantics gift/payment candidates | {stats['alb2005_outcome_semantics_gift_candidate_rows']} |
| ALB_2005 outcome-semantics access candidates | {stats['alb2005_outcome_semantics_access_candidate_rows']} |
| ALB_2005 outcome-semantics outcome-ready rows | {stats['alb2005_outcome_semantics_outcome_ready_rows']} |
| ALB_2005 outcome-semantics SDG 3.8.2-ready rows | {stats['alb2005_outcome_semantics_sdg382_ready_rows']} |
| ALB_2005 outcome-semantics climate-linkage-ready rows | {stats['alb2005_outcome_semantics_climate_linkage_ready_rows']} |
| ALB_2005 outcome-semantics decision | {stats['alb2005_outcome_semantics_current_decision']} |
| ALB_2005 timing/geography audit rows | {stats['alb2005_timing_geography_audit_rows']} |
| ALB_2005 source files scanned for timing/geography | {stats['alb2005_timing_geography_source_files_scanned']} |
| ALB_2005 verified interview timing rows | {stats['alb2005_interview_timing_verified_rows']} |
| ALB_2005 coordinate candidate rows | {stats['alb2005_coordinate_candidate_rows']} |
| ALB_2005 partial district name rows | {stats['alb2005_partial_district_name_nonmissing_rows']} |
| ALB_2005 partial district code rows | {stats['alb2005_partial_district_code_nonmissing_rows']} |
| ALB_2005 climate-linkage-ready rows | {stats['alb2005_climate_linkage_ready_rows']} |
| ALB_2005 timing/geography decision | {stats['alb2005_timing_geography_current_decision']} |
| ALB_2005 timing/geography source-search rows | {stats['alb2005_timing_geography_source_search_rows']} |
| ALB_2005 timing/geography source-search local files | {stats['alb2005_timing_geography_source_search_local_files_scanned']} |
| ALB_2005 timing/geography source-search local variables | {stats['alb2005_timing_geography_source_search_local_variables_scanned']} |
| ALB_2005 timing/geography source-search raw targets with hits | {stats['alb2005_timing_geography_source_search_raw_targets_with_hits']} |
| ALB_2005 timing/geography source-search questionnaire targets with hits | {stats['alb2005_timing_geography_source_search_questionnaire_targets_with_hits']} |
| ALB_2005 timing/geography source-search verified timing rows | {stats['alb2005_timing_geography_source_search_verified_household_timing_rows']} |
| ALB_2005 timing/geography source-search coordinate candidates | {stats['alb2005_timing_geography_source_search_coordinate_candidate_rows']} |
| ALB_2005 timing/geography source-search geography-ready rows | {stats['alb2005_timing_geography_source_search_geography_crosswalk_ready_rows']} |
| ALB_2005 timing/geography source-search climate-ready rows | {stats['alb2005_timing_geography_source_search_climate_linkage_ready_rows']} |
| ALB_2005 timing/geography source-search decision | {stats['alb2005_timing_geography_source_search_current_decision']} |
| ALB_2005 value-decision audit rows | {stats['alb2005_harmonization_value_decision_rows']} |
| ALB_2005 value-decision required blocked rows | {stats['alb2005_harmonization_value_decision_required_blocked_rows']} |
| ALB_2005 value-decision recipe-ready rows | {stats['alb2005_harmonization_value_decision_recipe_ready_rows']} |
| ALB_2005 value-decision current decision | {stats['alb2005_harmonization_value_decision_current_decision']} |
| ALB_2005 required value/key audit rows | {stats['alb2005_required_value_key_rows']} |
| ALB_2005 required value/key total-consumption nonmissing rows | {stats['alb2005_required_value_key_total_consumption_nonmissing_rows']} |
| ALB_2005 required value/key 4-week OOP positive audit-only households | {stats['alb2005_required_value_key_oop_4w_household_positive_rows']} |
| ALB_2005 required value/key 12-month OOP positive audit-only households | {stats['alb2005_required_value_key_oop_12m_household_positive_rows']} |
| ALB_2005 required value/key partial district-code rows | {stats['alb2005_required_value_key_district_code_nonmissing_rows']} |
| ALB_2005 required value/key interview timing rows | {stats['alb2005_required_value_key_interview_timing_verified_rows']} |
| ALB_2005 required value/key coordinate-ready rows | {stats['alb2005_required_value_key_coordinate_ready_rows']} |
| ALB_2005 required value/key climate-linkage-ready rows | {stats['alb2005_required_value_key_climate_linkage_ready_rows']} |
| ALB_2005 required value/key recipe-ready rows | {stats['alb2005_required_value_key_recipe_ready_rows']} |
| ALB_2005 required value/key decision | {stats['alb2005_required_value_key_current_decision']} |
| ALB_2005 health questionnaire semantics rows | {stats['alb2005_health_questionnaire_semantics_rows']} |
| ALB_2005 health questionnaire OOP item rows | {stats['alb2005_health_questionnaire_oop_item_rows']} |
| ALB_2005 health questionnaire old-lek unit rows | {stats['alb2005_health_questionnaire_old_lek_unit_rows']} |
| ALB_2005 health questionnaire access rows | {stats['alb2005_health_questionnaire_access_rows']} |
| ALB_2005 health questionnaire cost-barrier rows | {stats['alb2005_health_questionnaire_cost_barrier_rows']} |
| ALB_2005 health questionnaire recipe-ready rows | {stats['alb2005_health_questionnaire_recipe_ready_rows']} |
| ALB_2005 health questionnaire outcome-ready rows | {stats['alb2005_health_questionnaire_outcome_ready_rows']} |
| ALB_2005 health questionnaire climate-linkage-ready rows | {stats['alb2005_health_questionnaire_climate_linkage_ready_rows']} |
| ALB_2005 health questionnaire decision | {stats['alb2005_health_questionnaire_current_decision']} |
| ALB_2005 OOP aggregation policy rows | {stats['alb2005_oop_aggregation_policy_rows']} |
| ALB_2005 OOP aggregation policy total-consumption rows | {stats['alb2005_oop_aggregation_policy_total_consumption_rows']} |
| ALB_2005 OOP aggregation policy outcome-ready rows | {stats['alb2005_oop_aggregation_policy_outcome_ready_rows']} |
| ALB_2005 OOP aggregation policy recipe-ready rows | {stats['alb2005_oop_aggregation_policy_recipe_ready_rows']} |
| ALB_2005 OOP aggregation policy climate-linkage-ready rows | {stats['alb2005_oop_aggregation_policy_climate_linkage_ready_rows']} |
| ALB_2005 OOP aggregation policy decision | {stats['alb2005_oop_aggregation_policy_current_decision']} |
| ALB_2005 skip/missing semantics rows | {stats['alb2005_skip_missing_semantics_rows']} |
| ALB_2005 skip/missing payment leaks | {stats['alb2005_skip_missing_payment_nonmissing_when_not_triggered_rows']} |
| ALB_2005 skip/missing payment positive leaks | {stats['alb2005_skip_missing_payment_positive_when_not_triggered_rows']} |
| ALB_2005 triggered payment zero-or-missing rows | {stats['alb2005_skip_missing_payment_zero_or_missing_when_triggered_rows']} |
| ALB_2005 skip/missing recipe-ready rows | {stats['alb2005_skip_missing_recipe_ready_rows']} |
| ALB_2005 skip/missing outcome-ready rows | {stats['alb2005_skip_missing_outcome_ready_rows']} |
| ALB_2005 skip/missing climate-linkage-ready rows | {stats['alb2005_skip_missing_climate_linkage_ready_rows']} |
| ALB_2005 skip/missing decision | {stats['alb2005_skip_missing_current_decision']} |
| ALB_2005 unit-period audit rows | {stats['alb2005_consumption_oop_unit_period_rows']} |
| ALB_2005 unit-period positive total-consumption rows | {stats['alb2005_consumption_oop_unit_period_total_consumption_positive_rows']} |
| ALB_2005 unit-period metadata old-lek rows | {stats['alb2005_consumption_oop_unit_period_metadata_old_lek_rows']} |
| ALB_2005 unit-period OOP old-lek rows | {stats['alb2005_consumption_oop_unit_period_oop_old_lek_rows']} |
| ALB_2005 unit-period four-week OOP rows | {stats['alb2005_consumption_oop_unit_period_four_week_oop_rows']} |
| ALB_2005 unit-period twelve-month OOP rows | {stats['alb2005_consumption_oop_unit_period_twelve_month_oop_rows']} |
| ALB_2005 unit-period SDG-ready rows | {stats['alb2005_consumption_oop_unit_period_sdg382_ready_rows']} |
| ALB_2005 unit-period recipe-ready rows | {stats['alb2005_consumption_oop_unit_period_recipe_ready_rows']} |
| ALB_2005 unit-period outcome-ready rows | {stats['alb2005_consumption_oop_unit_period_outcome_ready_rows']} |
| ALB_2005 unit-period climate-linkage-ready rows | {stats['alb2005_consumption_oop_unit_period_climate_linkage_ready_rows']} |
| ALB_2005 unit-period decision | {stats['alb2005_consumption_oop_unit_period_current_decision']} |
| ALB_2005 aggregate crosswalk rows | {stats['alb2005_consumption_aggregate_crosswalk_rows']} |
| ALB_2005 aggregate crosswalk metadata rows | {stats['alb2005_consumption_aggregate_crosswalk_metadata_rows']} |
| ALB_2005 aggregate crosswalk metadata present locally | {stats['alb2005_consumption_aggregate_crosswalk_metadata_present_local_rows']} |
| ALB_2005 aggregate crosswalk metadata absent locally | {stats['alb2005_consumption_aggregate_crosswalk_metadata_absent_local_rows']} |
| ALB_2005 aggregate crosswalk positive `totcons` rows | {stats['alb2005_consumption_aggregate_crosswalk_totcons_positive_rows']} |
| ALB_2005 aggregate crosswalk local `totcons05` rows | {stats['alb2005_consumption_aggregate_crosswalk_totcons05_local_rows']} |
| ALB_2005 aggregate crosswalk formula reconstructable rows | {stats['alb2005_consumption_aggregate_crosswalk_component_formula_reconstructable_rows']} |
| ALB_2005 aggregate crosswalk SDG-ready rows | {stats['alb2005_consumption_aggregate_crosswalk_sdg382_ready_rows']} |
| ALB_2005 aggregate crosswalk recipe-ready rows | {stats['alb2005_consumption_aggregate_crosswalk_recipe_ready_rows']} |
| ALB_2005 aggregate crosswalk outcome-ready rows | {stats['alb2005_consumption_aggregate_crosswalk_outcome_ready_rows']} |
| ALB_2005 aggregate crosswalk climate-linkage-ready rows | {stats['alb2005_consumption_aggregate_crosswalk_climate_linkage_ready_rows']} |
| ALB_2005 aggregate crosswalk decision | {stats['alb2005_consumption_aggregate_crosswalk_current_decision']} |
| ALB_2005 component source-search rows | {stats['alb2005_consumption_component_source_search_rows']} |
| ALB_2005 component source-search local files | {stats['alb2005_consumption_component_source_search_local_files_scanned']} |
| ALB_2005 component source-search local variables | {stats['alb2005_consumption_component_source_search_local_variables_scanned']} |
| ALB_2005 component source-search exact targets found | {stats['alb2005_consumption_component_source_search_exact_target_variables_found']} |
| ALB_2005 component source-search exact targets missing | {stats['alb2005_consumption_component_source_search_exact_target_variables_missing']} |
| ALB_2005 component source-search construction-code files | {stats['alb2005_consumption_component_source_search_construction_code_files_found']} |
| ALB_2005 component source-search construction-code hits | {stats['alb2005_consumption_component_source_search_construction_code_targets_found']} |
| ALB_2005 component source-search SDG-ready rows | {stats['alb2005_consumption_component_source_search_sdg382_ready_rows']} |
| ALB_2005 component source-search recipe-ready rows | {stats['alb2005_consumption_component_source_search_recipe_ready_rows']} |
| ALB_2005 component source-search outcome-ready rows | {stats['alb2005_consumption_component_source_search_outcome_ready_rows']} |
| ALB_2005 component source-search climate-linkage-ready rows | {stats['alb2005_consumption_component_source_search_climate_linkage_ready_rows']} |
| ALB_2005 component source-search decision | {stats['alb2005_consumption_component_source_search_current_decision']} |
| ALB_2005 minimum recipe promotion action rows | {stats['alb2005_minimum_recipe_promotion_action_rows']} |
| ALB_2005 minimum recipe promotion gate rows | {stats['alb2005_minimum_recipe_promotion_gate_rows']} |
| ALB_2005 minimum recipe promotion blocked gates | {stats['alb2005_minimum_recipe_promotion_blocked_gates']} |
| ALB_2005 minimum recipe promotion candidate gates | {stats['alb2005_minimum_recipe_promotion_candidate_gates']} |
| ALB_2005 minimum recipe harmonized-ready rows | {stats['alb2005_minimum_recipe_promotion_harmonized_ready_rows']} |
| ALB_2005 minimum recipe outcome-ready rows | {stats['alb2005_minimum_recipe_promotion_outcome_ready_rows']} |
| ALB_2005 minimum recipe climate-linkage-ready rows | {stats['alb2005_minimum_recipe_promotion_climate_linkage_ready_rows']} |
| ALB_2005 minimum recipe promotion decision | {stats['alb2005_minimum_recipe_promotion_current_decision']} |
| ALB_2005 public fieldwork/geography evidence rows | {stats['alb2005_public_fieldwork_geo_metadata_evidence_rows']} |
| ALB_2005 public fieldwork/geography verified source rows | {stats['alb2005_public_fieldwork_geo_metadata_verified_source_rows']} |
| ALB_2005 public fieldwork/geography source-missing rows | {stats['alb2005_public_fieldwork_geo_metadata_source_missing_rows']} |
| ALB_2005 public fieldwork period evidence rows | {stats['alb2005_public_fieldwork_geo_metadata_fieldwork_period_evidence_rows']} |
| ALB_2005 public GPS claim rows | {stats['alb2005_public_fieldwork_geo_metadata_gps_claim_rows']} |
| ALB_2005 public sampling geography rows | {stats['alb2005_public_fieldwork_geo_metadata_sampling_geo_rows']} |
| ALB_2005 public metadata household-timing verified rows | {stats['alb2005_public_fieldwork_geo_metadata_household_timing_verified_rows']} |
| ALB_2005 public metadata raw coordinate rows | {stats['alb2005_public_fieldwork_geo_metadata_raw_coordinate_value_rows']} |
| ALB_2005 public metadata climate-linkage-ready rows | {stats['alb2005_public_fieldwork_geo_metadata_climate_linkage_ready_rows']} |
| ALB_2005 public fieldwork/geography decision | {stats['alb2005_public_fieldwork_geo_metadata_current_decision']} |
| ALB_2005 diary timing candidate rows | {stats['alb2005_diary_timing_candidate_audit_rows']} |
| ALB_2005 diary timing metadata-found rows | {stats['alb2005_diary_timing_candidate_metadata_found_rows']} |
| ALB_2005 diary timing schema file rows | {stats['alb2005_diary_timing_candidate_schema_file_rows']} |
| ALB_2005 raw bookmetadata files present | {stats['alb2005_diary_timing_candidate_raw_bookmetadata_files_present']} |
| ALB_2005 diary date candidate rows | {stats['alb2005_diary_timing_candidate_date_candidate_rows']} |
| ALB_2005 diary timing promoted rows | {stats['alb2005_diary_timing_candidate_household_timing_promoted_rows']} |
| ALB_2005 diary timing climate-linkage-ready rows | {stats['alb2005_diary_timing_candidate_climate_linkage_ready_rows']} |
| ALB_2005 diary timing decision | {stats['alb2005_diary_timing_candidate_current_decision']} |
| ALB_2005 extracted DDI modules checked | {stats['alb2005_extracted_module_coverage_ddi_module_rows']} |
| ALB_2005 archive members listed | {stats['alb2005_archive_member_rows']} |
| ALB_2005 archive .sav members | {stats['alb2005_archive_sav_member_rows']} |
| ALB_2005 archive DDI modules absent | {stats['alb2005_archive_ddi_module_absent_rows']} |
| ALB_2005 archive critical modules absent | {stats['alb2005_archive_critical_module_absent_rows']} |
| ALB_2005 archive listing status | {stats['alb2005_archive_listing_status']} |
| ALB_2005 extracted DDI modules present | {stats['alb2005_extracted_module_coverage_present_rows']} |
| ALB_2005 extracted DDI modules missing | {stats['alb2005_extracted_module_coverage_missing_rows']} |
| ALB_2005 extracted .sav files | {stats['alb2005_extracted_module_coverage_extracted_file_rows']} |
| ALB_2005 extracted extra files | {stats['alb2005_extracted_module_coverage_extra_extracted_rows']} |
| ALB_2005 bookmetadata missing rows | {stats['alb2005_extracted_module_coverage_bookmetadata_missing_rows']} |
| ALB_2005 food diary modules missing | {stats['alb2005_extracted_module_coverage_food_diary_missing_rows']} |
| ALB_2005 critical modules missing | {stats['alb2005_extracted_module_coverage_critical_missing_rows']} |
| ALB_2005 coordinate metadata variables | {stats['alb2005_extracted_module_coverage_coordinate_metadata_variable_rows']} |
| ALB_2005 coordinate extracted files | {stats['alb2005_extracted_module_coverage_coordinate_extracted_file_rows']} |
| ALB_2005 extracted-module climate-linkage-ready rows | {stats['alb2005_extracted_module_coverage_climate_linkage_ready_rows']} |
| ALB_2005 extracted-module decision | {stats['alb2005_extracted_module_coverage_current_decision']} |
| Albania first-analysis waves compared | {stats['albania_first_analysis_promotion_wave_rows']} |
| Albania first-analysis gate rows | {stats['albania_first_analysis_promotion_gate_rows']} |
| Albania first-analysis blocked gates | {stats['albania_first_analysis_promotion_blocked_gate_rows']} |
| Albania first-analysis ready waves | {stats['albania_first_analysis_promotion_ready_wave_rows']} |
| Albania first-analysis harmonized-ready rows | {stats['albania_first_analysis_promotion_harmonized_ready_rows']} |
| Albania first-analysis outcome-ready rows | {stats['albania_first_analysis_promotion_outcome_ready_rows']} |
| Albania first-analysis climate-linkage-ready rows | {stats['albania_first_analysis_promotion_climate_linkage_ready_rows']} |
| Albania top-ranked local wave | {stats['albania_first_analysis_promotion_top_ranked_idno']} |
| Albania top-ranked blocker | {stats['albania_first_analysis_promotion_top_ranked_primary_blocker']} |
| Albania first-analysis decision | {stats['albania_first_analysis_promotion_current_decision']} |
| Existing Albania raw waves audited | {stats['albania_existing_raw_wave_rows']} |
| Existing Albania archives present | {stats['albania_existing_raw_wave_archive_present_rows']} |
| Existing Albania extracted raw wave rows | {stats['albania_existing_raw_wave_extracted_rows']} |
| Existing Albania unintegrated wave rows | {stats['albania_existing_raw_wave_unintegrated_rows']} |
| Existing Albania raw .sav files | {stats['albania_existing_raw_wave_total_raw_tabular_files']} |
| Existing Albania raw variable rows | {stats['albania_existing_raw_wave_total_raw_variable_rows']} |
| Existing Albania waves with OOP keyword signals | {stats['albania_existing_raw_wave_oop_signal_rows']} |
| Existing Albania waves with interview timing keyword signals | {stats['albania_existing_raw_wave_timing_signal_rows']} |
| Existing Albania waves with GPS keyword signals | {stats['albania_existing_raw_wave_gps_signal_rows']} |
| Existing Albania harmonization-ready rows | {stats['albania_existing_raw_wave_harmonization_ready_rows']} |
| Existing Albania climate-linkage-ready rows | {stats['albania_existing_raw_wave_climate_linkage_ready_rows']} |
| Existing Albania raw wave decision | {stats['albania_existing_raw_wave_current_decision']} |
| ALB_2008 temp household-core candidate rows | {stats['alb2008_household_core_candidate_rows']} |
| ALB_2008 households with total consumption | {stats['alb2008_households_with_total_consumption']} |
| ALB_2008 households with household weight | {stats['alb2008_households_with_household_weight']} |
| ALB_2008 households with positive unreviewed 4-week OOP | {stats['alb2008_households_with_oop_4w_positive']} |
| ALB_2008 households with positive unreviewed 12-month OOP | {stats['alb2008_households_with_oop_12m_positive']} |
| ALB_2008 households with coarse area code | {stats['alb2008_households_with_coarse_area']} |
| ALB_2008 households with verified survey month | {stats['alb2008_households_with_survey_month']} |
| ALB_2008 household-core recipe-ready rows | {stats['alb2008_household_core_recipe_ready_rows']} |
| ALB_2008 provisional outcome feasibility rows | {stats['alb2008_provisional_outcome_audit_rows']} |
| ALB_2008 provisional financial stress-test rows | {stats['alb2008_provisional_financial_stress_test_rows']} |
| ALB_2008 provisional access proxy rows | {stats['alb2008_provisional_access_proxy_rows']} |
| ALB_2008 provisional low-event-rate rows | {stats['alb2008_provisional_low_event_rate_rows']} |
| ALB_2008 provisional outcome-ready rows | {stats['alb2008_provisional_outcome_ready_rows']} |
| ALB_2008 provisional outcome decision | {stats['alb2008_provisional_outcome_current_decision']} |
| ALB_2008 outcome-semantics raw value rows | {stats['alb2008_outcome_semantics_raw_value_rows']} |
| ALB_2008 outcome-semantics financial OOP candidates | {stats['alb2008_outcome_semantics_financial_oop_candidate_rows']} |
| ALB_2008 outcome-semantics gift/payment candidates | {stats['alb2008_outcome_semantics_gift_candidate_rows']} |
| ALB_2008 outcome-semantics access candidates | {stats['alb2008_outcome_semantics_access_candidate_rows']} |
| ALB_2008 outcome-semantics facility/service proxies | {stats['alb2008_outcome_semantics_facility_proxy_rows']} |
| ALB_2008 outcome-semantics outcome-ready rows | {stats['alb2008_outcome_semantics_outcome_ready_rows']} |
| ALB_2008 outcome-semantics SDG 3.8.2-ready rows | {stats['alb2008_outcome_semantics_sdg382_ready_rows']} |
| ALB_2008 outcome-semantics climate-linkage-ready rows | {stats['alb2008_outcome_semantics_climate_linkage_ready_rows']} |
| ALB_2008 outcome-semantics decision | {stats['alb2008_outcome_semantics_current_decision']} |
| ALB_2008 timing/geography audit rows | {stats['alb2008_timing_geography_audit_rows']} |
| ALB_2008 source files scanned for timing/geography | {stats['alb2008_timing_geography_source_files_scanned']} |
| ALB_2008 verified interview timing rows | {stats['alb2008_interview_timing_verified_rows']} |
| ALB_2008 coordinate candidate rows | {stats['alb2008_coordinate_candidate_rows']} |
| ALB_2008 coarse geography household rows | {stats['alb2008_coarse_geography_household_rows']} |
| ALB_2008 climate-linkage-ready rows | {stats['alb2008_climate_linkage_ready_rows']} |
| ALB_2008 timing/geography decision | {stats['alb2008_timing_geography_current_decision']} |
| ALB_2008 fallback blocker rows | {stats['alb2008_fallback_blocker_resolution_rows']} |
| ALB_2008 fallback timing rows | {stats['alb2008_fallback_blocker_timing_rows']} |
| ALB_2008 fallback geography rows | {stats['alb2008_fallback_blocker_geography_rows']} |
| ALB_2008 fallback outcome rows | {stats['alb2008_fallback_blocker_outcome_rows']} |
| ALB_2008 fallback promotion-gate rows | {stats['alb2008_fallback_blocker_promotion_gate_rows']} |
| ALB_2008 fallback hard-blocked rows | {stats['alb2008_fallback_blocker_hard_blocked_rows']} |
| ALB_2008 fallback interview-timing-ready rows | {stats['alb2008_fallback_blocker_interview_timing_ready_rows']} |
| ALB_2008 fallback geography-ready rows | {stats['alb2008_fallback_blocker_geography_ready_rows']} |
| ALB_2008 fallback outcome-ready rows | {stats['alb2008_fallback_blocker_outcome_ready_rows']} |
| ALB_2008 fallback climate-linkage-ready rows | {stats['alb2008_fallback_blocker_climate_linkage_ready_rows']} |
| ALB_2008 fallback data-write-ready rows | {stats['alb2008_fallback_blocker_data_write_ready_rows']} |
| ALB_2008 fallback decision | {stats['alb2008_fallback_blocker_current_decision']} |
| First-batch dataset verification gate rows | {stats['first_batch_dataset_gate_rows']} |
| First-batch concept verification template rows | {stats['first_batch_concept_template_rows']} |
| First-batch variable verification template rows | {stats['first_batch_variable_template_rows']} |
| First-batch datasets ready for value audit | {stats['first_batch_datasets_ready_for_value_audit']} |
| First-batch concepts ready for value audit | {stats['first_batch_concepts_ready_for_value_audit']} |
| First-batch variables ready for value audit | {stats['first_batch_variables_ready_for_value_audit']} |
| Raw-ingestion plan rows | {stats['raw_ingestion_plan_rows']} |
| Raw-ingestion concept checklist rows | {stats['raw_ingestion_concept_rows']} |
| Raw-ingestion module checklist rows | {stats['raw_ingestion_module_rows']} |
| Raw-ingestion targets ready for schema inspection | {stats['raw_ingestion_ready_rows']} |
| Raw-ingestion raw-verified concept rows | {stats['raw_ingestion_verified_concepts']} |
| Raw-variable verification protocol rows | {stats['raw_variable_protocol_rows']} |
| Harmonization recipe scaffold rows | {stats['harmonization_scaffold_rows']} |
| Raw-variable rows still not inspected | {stats['raw_variable_protocol_not_inspected_rows']} |
| Raw-variable rows pending value audit | {stats['raw_variable_protocol_value_audit_pending_rows']} |
| Harmonization recipe gate rows | {stats['harmonization_recipe_gate_rows']} |
| Harmonization verified candidate rows | {stats['harmonization_verified_candidate_rows']} |
| Harmonization value-audit template rows | {stats['harmonization_value_audit_template_rows']} |
| Harmonization country-waves ready for verified recipe assembly | {stats['harmonization_ready_country_wave_rows']} |
| Analysis dataset promotion audit rows | {stats['analysis_dataset_promotion_audit_rows']} |
| Analysis dataset promotion blocked rows | {stats['analysis_dataset_promotion_blocked_rows']} |
| Analysis dataset promotion promoted rows | {stats['analysis_dataset_promotion_promoted_rows']} |
| Analysis dataset promotion data-file count | {stats['analysis_dataset_promotion_data_file_count']} |
| Analysis dataset promotion verified recipe candidates | {stats['analysis_dataset_promotion_verified_recipe_candidates']} |
| Analysis dataset promotion ready country-waves | {stats['analysis_dataset_promotion_ready_country_waves']} |
| Analysis dataset promotion ALB_2002 temp core rows | {stats['analysis_dataset_promotion_alb2002_temp_core_rows']} |
| Analysis dataset promotion limited harmonized core rows | {stats['analysis_dataset_promotion_limited_harmonized_core_rows']} |
| Analysis dataset promotion limited core data-write-ready rows | {stats['analysis_dataset_promotion_limited_harmonized_core_data_write_ready_rows']} |
| Analysis dataset promotion limited core final-outcome-ready rows | {stats['analysis_dataset_promotion_limited_harmonized_core_final_outcome_ready_rows']} |
| Analysis dataset promotion limited core climate-ready rows | {stats['analysis_dataset_promotion_limited_harmonized_core_climate_linkage_ready_rows']} |
| Analysis dataset promotion limited financial outcome rows | {stats['analysis_dataset_promotion_limited_financial_outcome_rows']} |
| Analysis dataset promotion limited financial outcome data-write-ready rows | {stats['analysis_dataset_promotion_limited_financial_outcome_data_write_ready_rows']} |
| Analysis dataset promotion limited financial CHE10 rows | {stats['analysis_dataset_promotion_limited_financial_outcome_che10_rows']} |
| Analysis dataset promotion limited financial CHE25 rows | {stats['analysis_dataset_promotion_limited_financial_outcome_che25_rows']} |
| Analysis dataset promotion limited financial SDG/access/composite-ready rows | {stats['analysis_dataset_promotion_limited_financial_outcome_sdg382_ready_rows']}/{stats['analysis_dataset_promotion_limited_financial_outcome_access_ready_rows']}/{stats['analysis_dataset_promotion_limited_financial_outcome_composite_ready_rows']} |
| Analysis dataset promotion limited financial climate/analysis-ready rows | {stats['analysis_dataset_promotion_limited_financial_outcome_climate_linkage_ready_rows']}/{stats['analysis_dataset_promotion_limited_financial_outcome_analysis_ready_rows']} |
| Analysis dataset promotion limited climate exposure rows | {stats['analysis_dataset_promotion_limited_climate_exposure_rows']} |
| Analysis dataset promotion limited climate exposure data-write-ready rows | {stats['analysis_dataset_promotion_limited_climate_exposure_data_write_ready_rows']} |
| Analysis dataset promotion limited climate exposure linkage-ready rows | {stats['analysis_dataset_promotion_limited_climate_exposure_climate_linkage_ready_rows']} |
| Analysis dataset promotion limited climate exposure analysis-ready rows | {stats['analysis_dataset_promotion_limited_climate_exposure_analysis_ready_rows']} |
| Analysis dataset promotion ALB_2002 harmonized-ready rows | {stats['analysis_dataset_promotion_alb2002_harmonized_ready_rows']} |
| Analysis dataset promotion ALB_2002 outcome-ready rows | {stats['analysis_dataset_promotion_alb2002_outcome_ready_rows']} |
| Analysis dataset promotion ALB_2002 climate-ready rows | {stats['analysis_dataset_promotion_alb2002_climate_linkage_ready_rows']} |
| Analysis dataset promotion decision | {stats['analysis_dataset_promotion_current_decision']} |
| Minimum viable acquisition target rows | {stats['minimum_viable_target_rows']} |
| Minimum viable acquisition bundle rows | {stats['minimum_viable_bundle_rows']} |
| Minimum viable acquisition target countries | {stats['minimum_viable_target_countries']} |
| Climate source probe rows | {len(climate_source_probe)} |
| Climate source endpoints reachable/pass | {stats['climate_source_probe_ok']} |
| Climate exposure plan rows | {stats['climate_exposure_plan_rows']} |
| Climate exposure specification rows | {stats['climate_exposure_spec_rows']} |
| Climate exposure plans metadata-ready but raw-unverified | {stats['climate_exposure_metadata_ready_rows']} |
| Climate exposure plans ready for linkage input | {stats['climate_exposure_ready_for_linkage_rows']} |
| Climate exposure specifications blocked by raw linkage inputs | {stats['climate_exposure_blocked_spec_rows']} |
| Climate linkage requirement rows | {stats['climate_linkage_requirement_rows']} |
| Climate validation protocol rows | {stats['climate_validation_protocol_rows']} |
| Climate linkage readiness rows | {stats['climate_linkage_readiness_rows']} |
| Climate linkage rows ready for value audit | {stats['climate_linkage_ready_value_rows']} |
| Climate linkage rows blocked | {stats['climate_linkage_blocked_value_rows']} |
| Mechanism requirement rows | {stats['mechanism_requirement_rows']} |
| Mechanism pathway protocol rows | {stats['mechanism_pathway_protocol_rows']} |
| Mechanism readiness rows | {stats['mechanism_readiness_rows']} |
| Mechanism rows ready for analysis design | {stats['mechanism_ready_rows']} |
| Mechanism rows blocked | {stats['mechanism_blocked_rows']} |
| Empirical readiness dashboard rows | {stats['empirical_dashboard_rows']} |
| Empirical no-go threshold rows | {stats['empirical_no_go_rows']} |
| Empirical no-go thresholds passing | {stats['empirical_no_go_pass_rows']} |
| Empirical no-go thresholds blocked/failing | {stats['empirical_no_go_blocked_rows']} |
| Source inventory rows | {len(source_inventory)} |
| Priority studies with metadata schema extraction | {len(studies)} |
| Data files/modules parsed | {len(files)} |
| Variable labels parsed | {len(variables)} |
| Raw tabular files inspected | {len(raw_files)} |
| Raw variables inspected | {len(raw_variables)} |
| Harmonized household rows | {len(harmonized_household)} |
| Harmonization audit rows | {len(harmonization_audit)} |
| Harmonized lineage rows | {len(harmonized_lineage)} |
| Household outcome rows | {len(household_outcomes)} |
| Outcome audit rows | {len(outcome_audit)} |
| Outcome denominator plan rows | {stats['outcome_denominator_plan_rows']} |
| Outcome specification plan rows | {stats['outcome_specification_plan_rows']} |
| Outcome plan rows metadata-ready but raw-unverified | {stats['outcome_plan_metadata_ready_rows']} |
| Outcome plan rows ready for construction | {stats['outcome_plan_ready_rows']} |
| SDG 3.8.2 denominator requirement rows | {stats['sdg382_denominator_requirement_rows']} |
| SDG 3.8.2 denominator country-wave rows | {stats['sdg382_denominator_country_wave_rows']} |
| SDG 3.8.2 denominator rows ready for value audit | {stats['sdg382_denominator_ready_rows']} |
| SDG 3.8.2 denominator rows blocked | {stats['sdg382_denominator_blocked_rows']} |
| Modeling identification plan rows | {stats['modeling_identification_plan_rows']} |
| Modeling validation plan rows | {stats['modeling_validation_plan_rows']} |
| Falsification/placebo plan rows | {stats['falsification_placebo_plan_rows']} |
| Policy-learning plan rows | {stats['policy_learning_plan_rows']} |
| Modeling plan predictive-ready rows | {stats['modeling_predictive_ready_rows']} |
| Modeling plan reduced-form-ready rows | {stats['modeling_reduced_form_ready_rows']} |
| Modeling plan causal-ML-ready rows | {stats['modeling_causal_ml_ready_rows']} |
| Modeling plan policy-learning-ready rows | {stats['modeling_policy_ready_rows']} |
| Objective traceability requirement rows | {stats['objective_traceability_rows']} |
| Objective traceability satisfied rows | {stats['objective_traceability_satisfied_rows']} |
| Objective traceability unresolved rows | {stats['objective_traceability_unresolved_rows']} |
| Objective guardrail rows | {stats['objective_guardrail_rows']} |
| Objective guardrail unresolved rows | {stats['objective_guardrail_unresolved_rows']} |
| Python package inventory rows | {stats['python_package_inventory_rows']} |
| Python packages installed | {stats['python_packages_installed_rows']} |
| Python packages missing | {stats['python_packages_missing_rows']} |
| Python environment audit incomplete checks | {stats['python_environment_audit_incomplete_rows']} |
| Validation/reference source probe rows | {len(validation_reference_probe)} |
| Validation/reference sample rows | {stats['validation_reference_sample_rows']} |
| HEFPI UHC series rows | {stats['hefpi_uhc_series_rows']} |
| HEFPI UHC reference records | {stats['hefpi_uhc_reference_rows']} |
| Climate exposure rows | {len(climate_exposures)} |
| Climate audit rows | {len(climate_audit)} |
| Climate-linked household rows | {len(climate_linked)} |
| Climate merge audit rows | {len(climate_merge_audit)} |
| Descriptive prevalence rows | {len(descriptive_prevalence)} |
| Descriptive missingness rows | {len(descriptive_missingness)} |
| Sample-selection gate rows | {len(sample_gate)} |
| Metadata-only main-sample candidates | {stats['sample_gate_metadata_main_rows']} |
| Value-verified final-sample candidates | {stats['sample_gate_raw_final_rows']} |
| Sample-selection no-go rules failed | {stats['sample_gate_failed_rules']} |
| Variable confidence audit rows | {stats['variable_confidence_rows']} |
| Metadata quality download priority rows | {stats['metadata_quality_priority_rows']} |
| Metadata quality country-wave rows | {stats['metadata_quality_rows']} |
| Quality-supported financial country-waves | {stats['metadata_quality_financial_rows']} |
| Quality-supported double-failure country-waves | {stats['metadata_quality_double_rows']} |
| Likely false-positive metadata variable rows | {stats['metadata_likely_false_positive_rows']} |
| Predictive ML metric rows | {len(predictive_metrics)} |
| Reduced-form estimate rows | {len(reduced_form_estimates)} |
| Placebo-readiness rows | {len(placebo_readiness)} |
| Causal ML/policy audit rows | {len(causal_ml_policy_audit)} |
| CATE summary rows | {len(causal_ml_cate)} |
| Policy simulation rows | {len(policy_sim)} |
| Robustness result rows | {len(robustness_results)} |
| Candidate variable-map rows | {total_map_rows} |
| Current design scorecard rows | {stats['design_scorecard_rows']} |
| Current design scorecard decision | {stats['design_scorecard_current_decision']} |
| ALB_2002 promotion gate hard blockers | {stats['alb2002_promotion_gate_delta_hard_blocked_rows']} |
| ALB_2002 promotion gate data-write-ready rows | {stats['alb2002_promotion_gate_delta_data_write_ready_rows']} |
| ALB_2002 boundary blocker rows | {stats['alb2002_boundary_blocker_resolution_rows']} |
| ALB_2002 boundary candidate-name-coverage leads | {stats['alb2002_boundary_blocker_candidate_name_coverage_rows']} |
| ALB_2002 boundary climate-linkage-ready rows | {stats['alb2002_boundary_blocker_climate_linkage_ready_rows']} |
| ALB_2002 outcome blocker rows | {stats['alb2002_outcome_blocker_resolution_rows']} |
| ALB_2002 outcome candidate-not-promoted rows | {stats['alb2002_outcome_blocker_candidate_not_promoted_rows']} |
| ALB_2002 outcome-ready rows | {stats['alb2002_outcome_blocker_outcome_ready_rows']} |
| Completion criteria still incomplete | {len(incomplete_criteria)} |

## Country-Wave Screening

{markdown_count_table(score_counts, 'Feasibility score')}

## Sample Selection Gate

{markdown_count_table(sample_gate_status_counts, 'Sample gate status') if sample_gate else 'No sample-selection gate audit exists yet.'}

The gate is intentionally stricter than metadata screening: a country-wave is not eligible for final sample selection until raw files, raw variables, raw values, merge keys, and harmonization recipes have been verified. Current value-verified final-sample candidates: {stats['sample_gate_raw_final_rows']}. The detailed audit is `result/sample_selection_gate_audit.csv`; the human-readable report is `report/sample_selection_audit.md`.

## Metadata Candidate Quality

{markdown_count_table(variable_confidence_counts, 'Variable metadata confidence') if variable_confidence else 'No variable-confidence audit exists yet.'}

{markdown_count_table(metadata_quality_tier_counts, 'Country-wave metadata quality tier') if metadata_quality else 'No country-wave metadata-quality audit exists yet.'}

Quality-supported metadata is used only to prioritize manual downloads. It does not verify units, recall periods, household/person level, merge keys, event rates, or final sample eligibility. The detailed report is `report/metadata_candidate_quality_audit.md`.

The quality-supported download queue is `temp/metadata_quality_download_priority.csv` with {stats['metadata_quality_priority_rows']} rows.

## Data Access

{markdown_count_table(manual_counts, 'Manual/access source')}

Raw microdata were not fabricated or bypassed. Most priority World Bank, DHS, and MICS sources still require login, registration, Data Access Agreement, account, or terms workflows. Public external direct links are handled separately below and remain raw-schema evidence only until value, unit, recall-period, missing-code, and merge-key audits pass.

The ranked manual-download queue is `temp/manual_download_priority.csv` with {len(priority_rows)} rows.

The file/module checklist is `temp/manual_download_file_checklist.csv` with {len(manual_file_checklist)} rows, and the human-readable guide is `report/manual_data_access_guide.md`.

The manual request packet is `report/raw_data_request_packet.md`; its action queue is `temp/manual_access_action_queue.csv` with {len(manual_access_actions)} rows.

Acquisition checkpoint rows are in `temp/acquisition_progress.csv` with {len(acquisition_progress)} rows. This file is updated after each priority study so interrupted network runs do not erase completed source/manifest work.

External repository probe status:

{markdown_count_table(external_probe_status_counts, 'External repository probe status') if external_probe else 'No external repository probe has been run yet.'}

The external probe is `temp/external_repository_probe.csv`; it records redirects, access-gate signals, and candidate direct data links without bypassing login, registration, or terms workflows.

Public external raw candidate downloads:

{markdown_count_table(public_external_download_status_counts, 'Public external raw download status') if public_external_downloads else 'No public external raw candidate downloads have been attempted yet.'}

The public external raw candidate downloader is `report/public_external_raw_candidate_downloads.md`; machine-readable outputs are `temp/public_external_raw_candidate_downloads.csv` and `result/public_external_raw_candidate_download_summary.csv`. Current downloaded/existing public external archive rows: {stats['public_external_downloaded_rows']} across {stats['public_external_dataset_rows']} screened dataset rows. These archives support raw schema inspection, not harmonized outcomes or empirical claims.

Priority World Bank public documentation and access-gate snapshots:

{markdown_count_table(worldbank_doc_status_counts, 'World Bank public documentation status') if worldbank_public_docs else 'No World Bank public documentation snapshot has been run yet.'}

Resource types:

{markdown_count_table(worldbank_doc_resource_counts, 'World Bank public documentation resource type') if worldbank_public_docs else 'No World Bank public documentation resources have been snapshotted yet.'}

The public documentation audit is `temp/worldbank_public_documentation_audit.csv`; dataset-level access summaries are in `temp/worldbank_access_gate_summary.csv`; saved files are under `temp/source_snapshots/worldbank_public_documentation/`. These are documentation/metadata/access-page snapshots only, not raw microdata.

Raw download folder audit:

{markdown_count_table(raw_download_role_counts, 'Raw download file role') if raw_download_manifest else 'No files are currently present under `temp/raw_downloads/` except possibly the generated README.'}

Target folder status:

{markdown_count_table(raw_download_target_status_counts, 'Raw download target status') if raw_download_targets else 'No raw download target audit exists yet.'}

The raw download audit is `report/raw_download_audit.md`; machine-readable outputs are `temp/raw_download_file_manifest.csv` and `temp/raw_download_target_audit.csv`.

Raw download intake package:

{markdown_count_table(raw_download_intake_status_counts, 'Raw intake status') if raw_download_intake else 'No raw download intake package exists yet.'}

Expected file/module status:

{markdown_count_table(raw_download_expected_status_counts, 'Expected raw file status') if raw_download_expected else 'No expected-file intake checklist exists yet.'}

The raw download intake plan is `report/raw_download_intake_plan.md`; machine-readable outputs are `temp/raw_download_intake_manifest.csv`, `temp/raw_download_expected_files.csv`, and `result/raw_download_intake_summary.csv`. Per-target `_PLACE_RAW_FILES_HERE.md` files are instructions only, not raw microdata.

## Minimum Viable Acquisition Plan

{markdown_count_table(minimum_viable_set_counts, 'Acquisition set') if minimum_viable_targets else 'No minimum viable acquisition targets exist yet.'}

{markdown_count_table(minimum_viable_country_counts, 'Acquisition target country') if minimum_viable_targets else 'No minimum viable acquisition country rows exist yet.'}

{markdown_count_table(minimum_viable_tier_counts, 'Acquisition target metadata tier') if minimum_viable_targets else 'No minimum viable acquisition tier rows exist yet.'}

The minimum viable acquisition plan is `report/minimum_viable_acquisition_plan.md`; machine-readable outputs are `result/minimum_viable_acquisition_targets.csv`, `temp/minimum_viable_download_bundles.csv`, and `result/minimum_viable_acquisition_summary.csv`. These are manual-download targets for testing no-go thresholds, not final analytical sample selections.

First-batch raw acquisition checklist:

{markdown_count_table(first_batch_intake_status_counts, 'First-batch intake status') if first_batch_checklist else 'No first-batch raw acquisition checklist exists yet.'}

{markdown_count_table(first_batch_target_reason_counts, 'First-batch file target reason') if first_batch_file_targets else 'No first-batch file target rows exist yet.'}

The first-batch raw acquisition checklist is `report/first_batch_raw_acquisition_checklist.md`; machine-readable outputs are `temp/first_batch_raw_acquisition_checklist.csv`, `temp/first_batch_raw_file_targets.csv`, and `result/first_batch_raw_acquisition_summary.csv`. It selects the current smallest manual batch for testing the 6-country financial-protection and 10-wave double-failure gates. It is not a final sample and does not relax the raw-file inspection gate.

First-batch official raw access probe:

{markdown_count_table(first_batch_direct_route_counts, 'First-batch direct raw route status') if first_batch_access_probe else 'No first-batch official raw access probe exists yet.'}

{markdown_count_table(first_batch_manual_action_counts, 'First-batch manual action status') if first_batch_access_probe else 'No first-batch official raw access manual-action rows exist yet.'}

The first-batch official raw access probe is `report/first_batch_official_raw_access_probe.md`; machine-readable outputs are `temp/first_batch_official_raw_access_probe.csv` and `result/first_batch_official_raw_access_summary.csv`. It snapshots official get-microdata pages and classifies visible access gates and candidate links. It does not download raw microdata or bypass account, registration, request, or terms workflows.

First-batch manual download handoff:

{markdown_count_table(first_batch_handoff_status_counts, 'First-batch handoff status') if first_batch_handoff else 'No first-batch manual download handoff exists yet.'}

{markdown_count_table(first_batch_file_queue_reason_counts, 'First-batch handoff file target reasons') if first_batch_file_queue else 'No first-batch manual download file queue exists yet.'}

The first-batch manual download handoff is `report/first_batch_manual_download_handoff.md`; machine-readable outputs are `temp/first_batch_manual_download_handoff.csv`, `temp/first_batch_manual_download_file_queue.csv`, and `result/first_batch_manual_download_handoff_summary.csv`. It combines the official access-gate probe, target folders, expected raw modules, and post-download commands for the first manual batch. It is an acquisition handoff only and does not verify raw files.

First-batch public documentation audit:

{markdown_count_table(first_batch_documentation_status_counts, 'First-batch documentation coverage status') if first_batch_documentation else 'No first-batch public documentation audit exists yet.'}

{markdown_count_table(first_batch_documentation_resource_counts, 'First-batch documentation resource type') if first_batch_documentation else 'No first-batch public documentation resource rows exist yet.'}

The first-batch public documentation audit is `report/first_batch_public_documentation_audit.md`; machine-readable outputs are `temp/first_batch_public_documentation_audit.csv` and `result/first_batch_public_documentation_summary.csv`. It verifies local snapshots of public World Bank catalog documentation and metadata endpoints for the first manual batch. These snapshots remain metadata/documentation evidence only and do not replace raw microdata.

First-batch file source traceability:

{markdown_count_table(first_batch_file_source_status_counts, 'First-batch file source trace status') if first_batch_file_source_trace else 'No first-batch file-source traceability audit exists yet.'}

{markdown_count_table(first_batch_file_source_metadata_file_counts, 'First-batch metadata file status') if first_batch_file_source_trace else 'No first-batch metadata file trace rows exist yet.'}

The first-batch file source traceability audit is `report/first_batch_file_source_traceability.md`; machine-readable outputs are `temp/first_batch_file_source_traceability.csv` and `result/first_batch_file_source_traceability_summary.csv`. It links each queued manual-download module to public schema and variable metadata. It confirms metadata support for the queue only; it does not verify raw files or values.

First-batch merge-key lineage plan:

{markdown_count_table(first_batch_merge_key_status_counts, 'First-batch merge-key lineage status') if first_batch_merge_key_plan else 'No first-batch merge-key lineage plan exists yet.'}

{markdown_count_table(first_batch_merge_key_role_counts, 'First-batch merge-key candidate role') if first_batch_merge_key_candidates else 'No first-batch merge-key candidate rows exist yet.'}

The first-batch merge-key lineage plan is `report/first_batch_merge_key_lineage_plan.md`; machine-readable outputs are `temp/first_batch_merge_key_lineage_plan.csv`, `temp/first_batch_merge_key_candidate_variables.csv`, and `result/first_batch_merge_key_lineage_summary.csv`. It maps candidate household/person keys, survey design variables, timing, geography, and core file relationships before raw download. It remains metadata-only and cannot prove merge cardinality or promote harmonization.

First-batch raw value/key audit:

{markdown_count_table(first_batch_value_status_counts, 'First-batch raw value status') if first_batch_value_key_audit else 'No first-batch raw value/key audit exists yet.'}

{markdown_count_table(first_batch_value_read_counts, 'First-batch raw value read status') if first_batch_value_key_audit else 'No first-batch raw value read rows exist yet.'}

{markdown_count_table(first_batch_key_status_counts, 'First-batch key audit status') if first_batch_raw_key_audit else 'No first-batch key audit rows exist yet.'}

The first-batch raw value/key audit is `report/first_batch_raw_value_key_audit.md`; machine-readable outputs are `temp/first_batch_raw_value_key_audit.csv`, `temp/first_batch_raw_merge_key_audit.csv`, `temp/first_batch_harmonization_value_audit_auto.csv`, and `result/first_batch_raw_value_key_summary.csv`. It reads observed raw values and file-level key cardinality for raw-ready first-batch datasets. It remains fail-closed: auto value-audit rows marked ready for recipe: {stats['first_batch_auto_value_audit_ready_rows']}.

ALB_2002 household core merge audit:

{markdown_count_table(alb2002_core_merge_counts, 'ALB_2002 core merge status') if alb2002_core_merge_audit else 'No ALB_2002 household-core merge audit exists yet.'}

{markdown_count_table(alb2002_core_lineage_counts, 'ALB_2002 core lineage status') if alb2002_core_lineage else 'No ALB_2002 household-core lineage rows exist yet.'}

The ALB_2002 household-core audit is `report/alb2002_household_core_merge_audit.md`; machine-readable outputs are `temp/alb2002_household_core_candidate.csv`, `temp/alb2002_household_core_merge_audit.csv`, `temp/alb2002_household_core_lineage.csv`, and `result/alb2002_household_core_candidate_summary.csv`. The candidate remains in `temp/`, not `data/`: observed interview date/month and district fields are promising, but OOP aggregation/recall, units, access skip patterns, district climate crosswalk, no-GPS geography, and cross-wave comparability remain unresolved.

ALB_2002 weight/design evidence audit:

| Metric | Value |
|---|---:|
| Evidence rows | {stats['alb2002_weight_design_evidence_audit_rows']} |
| Official source flags | {stats['alb2002_weight_design_source_page_flag_rows']} |
| Raw weight-file rows | {stats['alb2002_weight_design_raw_weight_file_rows']} |
| Positive weight rows | {stats['alb2002_weight_design_positive_weight_rows']} |
| Candidate key-match rows | {stats['alb2002_weight_design_candidate_key_match_rows']} |
| Distinct PSUs | {stats['alb2002_weight_design_distinct_psu_rows']} |
| Distinct strata | {stats['alb2002_weight_design_distinct_stratum_rows']} |
| Weighted-inference-ready rows | {stats['alb2002_weight_design_weighted_inference_ready_rows']} |
| Harmonized-promotion-ready rows | {stats['alb2002_weight_design_harmonized_promotion_ready_rows']} |
| Decision | {stats['alb2002_weight_design_current_decision']} |

{markdown_count_table(alb2002_weight_design_status_counts, 'ALB_2002 weight/design evidence status') if alb2002_weight_design_audit else 'No ALB_2002 weight/design evidence rows exist yet.'}

The ALB_2002 weight/design audit is `report/alb2002_weight_design_evidence_audit.md`; machine-readable outputs are `temp/alb2002_weight_design_evidence_audit.csv` and `result/alb2002_weight_design_evidence_summary.csv`. It verifies complete readable household-weight coverage, PSU/stratum/urban-rural design fields, and official study-page sampling context, but it keeps weighted inference and harmonized data promotion at zero until target-population, normalization, design-variance, outcome, and climate gates pass together.

ALB_2002 sample-design documentation audit:

| Metric | Value |
|---|---:|
| Evidence rows | {stats['alb2002_sample_design_documentation_audit_rows']} |
| PDF available rows | {stats['alb2002_sample_design_pdf_available_rows']} |
| PDF pages | {stats['alb2002_sample_design_pdf_pages']} |
| Official 450 PSU by 8 household evidence rows | {stats['alb2002_sample_design_official_450_psu_8_hh_rows']} |
| Official 3,599 final household evidence rows | {stats['alb2002_sample_design_official_3599_final_rows']} |
| Raw design concordance rows | {stats['alb2002_sample_design_raw_design_concordance_rows']} |
| Documentation-ready rows | {stats['alb2002_sample_design_documentation_ready_rows']} |
| Weighted-inference-ready rows | {stats['alb2002_sample_design_weighted_inference_ready_rows']} |
| Harmonized-promotion-ready rows | {stats['alb2002_sample_design_harmonized_promotion_ready_rows']} |
| Decision | {stats['alb2002_sample_design_current_decision']} |

{markdown_count_table(alb2002_sample_design_status_counts, 'ALB_2002 sample-design evidence status') if alb2002_sample_design_audit else 'No ALB_2002 sample-design documentation rows exist yet.'}

The ALB_2002 sample-design documentation audit is `report/alb2002_sample_design_documentation_audit.md`; machine-readable outputs are `temp/alb2002_sample_design_documentation_audit.csv`, `result/alb2002_sample_design_documentation_summary.csv`, `temp/source_snapshots/alb2002_basic_information_document_sample_design.pdf`, and `temp/source_snapshots/alb2002_basic_information_document_sample_design.txt`. It documents the official sample-design/final-sample count evidence and raw count concordance, but keeps weighted inference and data promotion at zero until the downstream gates pass.

ALB_2002 provisional outcome feasibility:

{markdown_count_table(alb2002_outcome_family_counts, 'ALB_2002 provisional outcome family') if alb2002_outcome_audit else 'No ALB_2002 provisional outcome feasibility audit exists yet.'}

{markdown_count_table(alb2002_outcome_status_counts, 'ALB_2002 provisional outcome promotion status') if alb2002_outcome_audit else 'No ALB_2002 provisional outcome status rows exist yet.'}

The ALB_2002 provisional outcome audit is `report/alb2002_provisional_outcome_feasibility.md`; machine-readable outputs are `temp/alb2002_provisional_outcome_feasibility_audit.csv` and `result/alb2002_provisional_outcome_feasibility_summary.csv`. It computes raw OOP/access event-rate diagnostics only. It does not construct SDG 3.8.2, final CHE10/CHE25, climate-linked, descriptive, causal, ML, or policy outcomes; promotion-ready rows are {stats['alb2002_provisional_outcome_ready_rows']}.

ALB_2002 raw outcome semantics:

{markdown_count_table(alb2002_semantics_domain_counts, 'ALB_2002 raw semantics domain') if alb2002_semantics_audit else 'No ALB_2002 raw outcome-semantics audit exists yet.'}

{markdown_count_table(alb2002_semantics_promotion_counts, 'ALB_2002 raw semantics promotion status') if alb2002_semantics_audit else 'No ALB_2002 raw semantics promotion rows exist yet.'}

The ALB_2002 raw outcome-semantics audit is `report/alb2002_outcome_semantics_raw_value_audit.md`; machine-readable outputs are `temp/alb2002_outcome_semantics_raw_value_audit.csv` and `result/alb2002_outcome_semantics_raw_value_summary.csv`. It documents raw health-module labels, observed values, value-label examples, merge-key coverage, and skip-pattern blockers. Outcome-ready rows are {stats['alb2002_outcome_semantics_outcome_ready_rows']} and SDG 3.8.2-ready rows are {stats['alb2002_outcome_semantics_sdg382_ready_rows']}.

ALB_2002 health questionnaire semantics:

{markdown_count_table(alb2002_health_questionnaire_family_counts, 'ALB_2002 health questionnaire audit family') if alb2002_health_questionnaire_audit else 'No ALB_2002 health questionnaire semantics audit exists yet.'}

{markdown_count_table(alb2002_health_questionnaire_status_counts, 'ALB_2002 health questionnaire evidence status') if alb2002_health_questionnaire_audit else 'No ALB_2002 health questionnaire evidence-status rows exist yet.'}

{markdown_count_table(alb2002_health_questionnaire_concept_counts, 'ALB_2002 health questionnaire concept') if alb2002_health_questionnaire_audit else 'No ALB_2002 health questionnaire concept rows exist yet.'}

The ALB_2002 health questionnaire semantics audit is `report/alb2002_health_questionnaire_semantics_audit.md`; machine-readable outputs are `temp/alb2002_health_questionnaire_semantics_audit.csv` and `result/alb2002_health_questionnaire_semantics_summary.csv`. It records {stats['alb2002_health_questionnaire_semantics_rows']} questionnaire/skip-path rows, including {stats['alb2002_health_questionnaire_oop_item_rows']} OOP item rows, {stats['alb2002_health_questionnaire_gift_item_rows']} gift/payment-scope rows, {stats['alb2002_health_questionnaire_new_lek_unit_rows']} NEW LEKS unit rows, {stats['alb2002_health_questionnaire_four_week_oop_rows']} four-week OOP rows, and {stats['alb2002_health_questionnaire_twelve_month_oop_rows']} twelve-month OOP rows. Raw skip checks found {stats['alb2002_health_questionnaire_payment_positive_when_not_triggered_rows']} positive downstream payment rows when triggers were negative, {stats['alb2002_health_questionnaire_payment_nonmissing_when_not_triggered_rows']} nonmissing downstream payment rows requiring review, and {stats['alb2002_health_questionnaire_payment_zero_or_missing_when_triggered_rows']} triggered payment rows with zero or missing downstream payment values. Outcome-ready, SDG 3.8.2-ready, and climate-linkage-ready rows remain {stats['alb2002_health_questionnaire_outcome_ready_rows']}, {stats['alb2002_health_questionnaire_sdg382_ready_rows']}, and {stats['alb2002_health_questionnaire_climate_linkage_ready_rows']}; current decision is `{stats['alb2002_health_questionnaire_current_decision']}`.

ALB_2002 OOP aggregation policy:

| Metric | Value |
|---|---:|
| Policy stress-test rows | {stats['alb2002_oop_aggregation_policy_rows']} |
| Household rows | {stats['alb2002_oop_aggregation_policy_household_rows']} |
| Positive total-consumption rows | {stats['alb2002_oop_aggregation_policy_total_consumption_rows']} |
| Four-week policy rows | {stats['alb2002_oop_aggregation_policy_four_week_policy_rows']} |
| Twelve-month policy rows | {stats['alb2002_oop_aggregation_policy_twelve_month_policy_rows']} |
| Annualized stress rows | {stats['alb2002_oop_aggregation_policy_annual_stress_rows']} |
| Maximum CHE10 stress-test rate | {stats['alb2002_oop_aggregation_policy_max_che10_rate']} |
| Maximum CHE25 stress-test rate | {stats['alb2002_oop_aggregation_policy_max_che25_rate']} |
| Core four-week OOP match rows | {stats['alb2002_oop_aggregation_policy_core_4w_match_rows']} |
| Core twelve-month OOP match rows | {stats['alb2002_oop_aggregation_policy_core_12m_match_rows']} |
| Outcome-ready rows | {stats['alb2002_oop_aggregation_policy_outcome_ready_rows']} |
| Recipe-ready rows | {stats['alb2002_oop_aggregation_policy_recipe_ready_rows']} |
| SDG 3.8.2-ready rows | {stats['alb2002_oop_aggregation_policy_sdg382_ready_rows']} |
| Climate-linkage-ready rows | {stats['alb2002_oop_aggregation_policy_climate_linkage_ready_rows']} |
| Decision | {stats['alb2002_oop_aggregation_policy_current_decision']} |

{markdown_count_table(alb2002_oop_policy_recall_counts, 'ALB_2002 OOP policy recall scope') if alb2002_oop_policy_audit else 'No ALB_2002 OOP aggregation policy audit exists yet.'}

{markdown_count_table(alb2002_oop_policy_promotion_counts, 'ALB_2002 OOP policy promotion status') if alb2002_oop_policy_audit else 'No ALB_2002 OOP policy promotion-status rows exist yet.'}

The ALB_2002 OOP aggregation policy audit is `report/alb2002_oop_aggregation_policy_audit.md`; machine-readable outputs are `temp/alb2002_oop_aggregation_policy_audit.csv` and `result/alb2002_oop_aggregation_policy_summary.csv`. It records {stats['alb2002_oop_aggregation_policy_rows']} stress-test policies, with maximum CHE10 and CHE25 rates of {stats['alb2002_oop_aggregation_policy_max_che10_rate']} and {stats['alb2002_oop_aggregation_policy_max_che25_rate']}. These are sensitivity diagnostics only: outcome-ready, recipe-ready, SDG 3.8.2-ready, and climate-linkage-ready rows remain {stats['alb2002_oop_aggregation_policy_outcome_ready_rows']}, {stats['alb2002_oop_aggregation_policy_recipe_ready_rows']}, {stats['alb2002_oop_aggregation_policy_sdg382_ready_rows']}, and {stats['alb2002_oop_aggregation_policy_climate_linkage_ready_rows']}; current decision is `{stats['alb2002_oop_aggregation_policy_current_decision']}`.

ALB_2002 skip and missing-code semantics:

| Metric | Value |
|---|---:|
| Skip/missing audit rows | {stats['alb2002_skip_missing_semantics_rows']} |
| Payment skip blocks | {stats['alb2002_skip_missing_payment_block_rows']} |
| Access/financing condition blocks | {stats['alb2002_skip_missing_access_condition_rows']} |
| Nonmissing skipped-payment rows | {stats['alb2002_skip_missing_payment_nonmissing_when_not_triggered_rows']} |
| Positive skipped-payment rows | {stats['alb2002_skip_missing_payment_positive_when_not_triggered_rows']} |
| Nonmissing skipped-payment cells | {stats['alb2002_skip_missing_payment_nonmissing_cells_when_not_triggered']} |
| Zero skipped-payment cells | {stats['alb2002_skip_missing_payment_zero_cells_when_not_triggered']} |
| Positive skipped-payment cells | {stats['alb2002_skip_missing_payment_positive_cells_when_not_triggered']} |
| Zero-only payment skip blocks | {stats['alb2002_skip_missing_payment_zero_only_block_rows']} |
| No-skipped-value payment blocks | {stats['alb2002_skip_missing_payment_no_skipped_value_block_rows']} |
| Access/financing nonmissing rows when not triggered | {stats['alb2002_skip_missing_condition_nonmissing_when_not_triggered_rows']} |
| Access/financing missing rows when triggered | {stats['alb2002_skip_missing_condition_missing_when_triggered_rows']} |
| Outcome-ready rows | {stats['alb2002_skip_missing_outcome_ready_rows']} |
| Recipe-ready rows | {stats['alb2002_skip_missing_recipe_ready_rows']} |
| SDG 3.8.2-ready rows | {stats['alb2002_skip_missing_sdg382_ready_rows']} |
| Climate-linkage-ready rows | {stats['alb2002_skip_missing_climate_linkage_ready_rows']} |
| Decision | {stats['alb2002_skip_missing_current_decision']} |

{markdown_count_table(alb2002_skip_missing_family_counts, 'ALB_2002 skip/missing audit family') if alb2002_skip_missing_audit else 'No ALB_2002 skip/missing semantics audit exists yet.'}

{markdown_count_table(alb2002_skip_missing_status_counts, 'ALB_2002 skip/missing evidence status') if alb2002_skip_missing_audit else 'No ALB_2002 skip/missing evidence-status rows exist yet.'}

{markdown_count_table(alb2002_skip_missing_zero_status_counts, 'ALB_2002 zero/missing semantics status') if alb2002_skip_missing_audit else 'No ALB_2002 zero/missing semantics rows exist yet.'}

The ALB_2002 skip/missing semantics audit is `report/alb2002_skip_missing_semantics_audit.md`; machine-readable outputs are `temp/alb2002_skip_missing_semantics_audit.csv` and `result/alb2002_skip_missing_semantics_summary.csv`. It confirms {stats['alb2002_skip_missing_payment_positive_when_not_triggered_rows']} positive skipped-payment rows and {stats['alb2002_skip_missing_payment_positive_cells_when_not_triggered']} positive skipped-payment cells, with {stats['alb2002_skip_missing_payment_zero_cells_when_not_triggered']} skipped cells equal to zero. These zeros are not promoted automatically; the downstream skip-value decision audit records the no-positive-leakage decision while outcome-ready, recipe-ready, SDG 3.8.2-ready, and climate-linkage-ready rows remain {stats['alb2002_skip_missing_outcome_ready_rows']}, {stats['alb2002_skip_missing_recipe_ready_rows']}, {stats['alb2002_skip_missing_sdg382_ready_rows']}, and {stats['alb2002_skip_missing_climate_linkage_ready_rows']}; current decision is `{stats['alb2002_skip_missing_current_decision']}`.

ALB_2002 OOP skip-value decision:

| Metric | Value |
|---|---:|
| Decision audit rows | {stats['alb2002_oop_skip_value_decision_rows']} |
| Payment skip blocks | {stats['alb2002_oop_skip_value_payment_block_rows']} |
| Access condition blocks | {stats['alb2002_oop_skip_value_access_condition_block_rows']} |
| Nonmissing skipped-payment rows | {stats['alb2002_oop_skip_value_payment_nonmissing_skipped_rows']} |
| Nonmissing skipped-payment cells | {stats['alb2002_oop_skip_value_payment_nonmissing_skipped_cells']} |
| Zero skipped-payment cells | {stats['alb2002_oop_skip_value_payment_zero_skipped_cells']} |
| Positive skipped-payment rows | {stats['alb2002_oop_skip_value_payment_positive_skipped_rows']} |
| Positive skipped-payment cells | {stats['alb2002_oop_skip_value_payment_positive_skipped_cells']} |
| Zero-skip policy-ready rows | {stats['alb2002_oop_skip_value_zero_skip_policy_ready_rows']} |
| OOP recall-scope-ready rows | {stats['alb2002_oop_skip_value_oop_recall_scope_ready_rows']} |
| OOP inclusion-scope-ready rows | {stats['alb2002_oop_skip_value_oop_inclusion_scope_ready_rows']} |
| Recipe-ready rows | {stats['alb2002_oop_skip_value_recipe_ready_rows']} |
| Outcome-ready rows | {stats['alb2002_oop_skip_value_outcome_ready_rows']} |
| SDG 3.8.2-ready rows | {stats['alb2002_oop_skip_value_sdg382_ready_rows']} |
| Climate-linkage-ready rows | {stats['alb2002_oop_skip_value_climate_linkage_ready_rows']} |
| Decision | {stats['alb2002_oop_skip_value_current_decision']} |

{markdown_count_table(alb2002_oop_skip_value_family_counts, 'ALB_2002 OOP skip-value decision family') if alb2002_oop_skip_value_audit else 'No ALB_2002 OOP skip-value decision audit exists yet.'}

{markdown_count_table(alb2002_oop_skip_value_promotion_counts, 'ALB_2002 OOP skip-value promotion status') if alb2002_oop_skip_value_audit else 'No ALB_2002 OOP skip-value promotion rows exist yet.'}

The ALB_2002 OOP skip-value decision audit is `report/alb2002_oop_skip_value_decision_audit.md`; machine-readable outputs are `temp/alb2002_oop_skip_value_decision_audit.csv` and `result/alb2002_oop_skip_value_decision_summary.csv`. It narrows the skipped-payment blocker to a documented no-positive-leakage decision while keeping recall-scope, inclusion-scope, outcome, recipe, SDG 3.8.2, and climate-linkage readiness rows at zero.

ALB_2002 access and need denominator policy:

| Metric | Value |
|---|---:|
| Access/need policy rows | {stats['alb2002_access_need_denominator_policy_rows']} |
| Household rows | {stats['alb2002_access_need_household_rows']} |
| Person-level illness/need households | {stats['alb2002_access_need_person_need_household_rows']} |
| q01 broad need rows | {stats['alb2002_access_need_q01_need_rows']} |
| q01 cost difficulty rows | {stats['alb2002_access_need_q01_cost_difficulty_rows']} |
| Delayed help rows | {stats['alb2002_access_need_delayed_help_rows']} |
| Referral not gone rows | {stats['alb2002_access_need_referral_not_gone_rows']} |
| Refused service rows | {stats['alb2002_access_need_refused_service_rows']} |
| Medicine discount any-barrier rows | {stats['alb2002_access_need_medicine_discount_any_barrier_rows']} |
| Composite cost-barrier rows | {stats['alb2002_access_need_composite_cost_barrier_rows']} |
| Composite distance-barrier rows | {stats['alb2002_access_need_composite_distance_barrier_rows']} |
| Composite supply/admin-barrier rows | {stats['alb2002_access_need_composite_supply_admin_barrier_rows']} |
| Composite any-access-barrier rows | {stats['alb2002_access_need_composite_any_access_barrier_rows']} |
| Low-event-rate policy rows | {stats['alb2002_access_need_low_event_rate_rows']} |
| Outcome-ready rows | {stats['alb2002_access_need_outcome_ready_rows']} |
| Recipe-ready rows | {stats['alb2002_access_need_recipe_ready_rows']} |
| SDG 3.8.2-ready rows | {stats['alb2002_access_need_sdg382_ready_rows']} |
| Climate-linkage-ready rows | {stats['alb2002_access_need_climate_linkage_ready_rows']} |
| Decision | {stats['alb2002_access_need_current_decision']} |

{markdown_count_table(alb2002_access_need_family_counts, 'ALB_2002 access/need outcome family') if alb2002_access_need_audit else 'No ALB_2002 access/need denominator policy audit exists yet.'}

{markdown_count_table(alb2002_access_need_denominator_counts, 'ALB_2002 access/need denominator status') if alb2002_access_need_audit else 'No ALB_2002 access/need denominator-status rows exist yet.'}

{markdown_count_table(alb2002_access_need_skip_counts, 'ALB_2002 access/need skip-path status') if alb2002_access_need_audit else 'No ALB_2002 access/need skip-path rows exist yet.'}

The ALB_2002 access/need denominator policy audit is `report/alb2002_access_need_denominator_policy_audit.md`; machine-readable outputs are `temp/alb2002_access_need_denominator_policy_audit.csv` and `result/alb2002_access_need_denominator_policy_summary.csv`. It records {stats['alb2002_access_need_denominator_policy_rows']} denominator-policy diagnostics, including {stats['alb2002_access_need_q01_need_rows']} q01 broad-need rows, {stats['alb2002_access_need_person_need_household_rows']} person-level illness/need households, and {stats['alb2002_access_need_composite_any_access_barrier_rows']} composite any-access-barrier rows. These are not final outcomes: outcome-ready, recipe-ready, SDG 3.8.2-ready, and climate-linkage-ready rows remain {stats['alb2002_access_need_outcome_ready_rows']}, {stats['alb2002_access_need_recipe_ready_rows']}, {stats['alb2002_access_need_sdg382_ready_rows']}, and {stats['alb2002_access_need_climate_linkage_ready_rows']}; current decision is `{stats['alb2002_access_need_current_decision']}`.

ALB_2002 consumption and SDG denominator policy:

| Metric | Value |
|---|---:|
| Denominator policy rows | {stats['alb2002_consumption_sdg_denominator_policy_rows']} |
| Household rows | {stats['alb2002_consumption_sdg_household_rows']} |
| Positive total-consumption rows | {stats['alb2002_consumption_sdg_positive_total_consumption_rows']} |
| Positive household-weight rows | {stats['alb2002_consumption_sdg_positive_household_weight_rows']} |
| Positive household-size rows | {stats['alb2002_consumption_sdg_positive_household_size_rows']} |
| Diagnostic four-week CHE10 rate | {stats['alb2002_consumption_sdg_che10_4w_unreviewed_rate']} |
| Diagnostic four-week CHE25 rate | {stats['alb2002_consumption_sdg_che25_4w_unreviewed_rate']} |
| Diagnostic twelve-month CHE10 rate | {stats['alb2002_consumption_sdg_che10_12m_unreviewed_rate']} |
| Diagnostic twelve-month CHE25 rate | {stats['alb2002_consumption_sdg_che25_12m_unreviewed_rate']} |
| SPL-ready rows | {stats['alb2002_consumption_sdg_spl_ready_rows']} |
| PPP/CPI-ready rows | {stats['alb2002_consumption_sdg_ppp_cpi_ready_rows']} |
| Discretionary-budget-ready rows | {stats['alb2002_consumption_sdg_discretionary_budget_ready_rows']} |
| CHE denominator-ready rows | {stats['alb2002_consumption_sdg_che_denominator_ready_rows']} |
| Outcome-ready rows | {stats['alb2002_consumption_sdg_outcome_ready_rows']} |
| Recipe-ready rows | {stats['alb2002_consumption_sdg_recipe_ready_rows']} |
| SDG 3.8.2-ready rows | {stats['alb2002_consumption_sdg_sdg382_ready_rows']} |
| Climate-linkage-ready rows | {stats['alb2002_consumption_sdg_climate_linkage_ready_rows']} |
| Decision | {stats['alb2002_consumption_sdg_current_decision']} |

{markdown_count_table(alb2002_consumption_sdg_family_counts, 'ALB_2002 consumption/SDG component family') if alb2002_consumption_sdg_audit else 'No ALB_2002 consumption/SDG denominator policy audit exists yet.'}

{markdown_count_table(alb2002_consumption_sdg_status_counts, 'ALB_2002 consumption/SDG evidence status') if alb2002_consumption_sdg_audit else 'No ALB_2002 consumption/SDG evidence-status rows exist yet.'}

The ALB_2002 consumption/SDG denominator policy audit is `report/alb2002_consumption_sdg_denominator_policy_audit.md`; machine-readable outputs are `temp/alb2002_consumption_sdg_denominator_policy_audit.csv` and `result/alb2002_consumption_sdg_denominator_policy_summary.csv`. It verifies full candidate coverage for total consumption, weights, and household size, but all CHE, outcome, recipe, SDG 3.8.2, and climate-linkage readiness rows remain zero because unit/period, OOP alignment, SPL, PPP/CPI, discretionary-budget, benchmark, and geography gates remain unresolved.

ALB_2002 consumption construction source audit:

| Metric | Value |
|---|---:|
| Source audit rows | {stats['alb2002_consumption_construction_source_audit_rows']} |
| Public method PDF present | {stats['alb2002_consumption_construction_public_pdf_present']} |
| Public Stata program ZIP present | {stats['alb2002_consumption_construction_program_zip_present']} |
| Extracted `.do` files | {stats['alb2002_consumption_construction_do_file_rows']} |
| `totcons.do` present | {stats['alb2002_consumption_construction_totcons_do_present']} |
| `poverty.do` present | {stats['alb2002_consumption_construction_poverty_do_present']} |
| Public metadata JSON present | {stats['alb2002_consumption_construction_metadata_json_present']} |
| Documentation-ready rows | {stats['alb2002_consumption_construction_documentation_ready_rows']} |
| Released-variable mapping-ready rows | {stats['alb2002_consumption_construction_released_variable_mapping_ready_rows']} |
| Denominator-variant-ready rows | {stats['alb2002_consumption_construction_denominator_variant_ready_rows']} |
| Recipe-ready rows | {stats['alb2002_consumption_construction_recipe_ready_rows']} |
| Outcome-ready rows | {stats['alb2002_consumption_construction_outcome_ready_rows']} |
| SDG 3.8.2-ready rows | {stats['alb2002_consumption_construction_sdg382_ready_rows']} |
| Climate-linkage-ready rows | {stats['alb2002_consumption_construction_climate_linkage_ready_rows']} |
| Decision | {stats['alb2002_consumption_construction_current_decision']} |

{markdown_count_table(alb2002_consumption_construction_family_counts, 'ALB_2002 consumption construction audit family') if alb2002_consumption_construction_audit else 'No ALB_2002 consumption construction source audit exists yet.'}

{markdown_count_table(alb2002_consumption_construction_status_counts, 'ALB_2002 consumption construction evidence status') if alb2002_consumption_construction_audit else 'No ALB_2002 consumption construction source evidence rows exist yet.'}

The ALB_2002 consumption construction source audit is `report/alb2002_consumption_construction_source_audit.md`; machine-readable outputs are `temp/alb2002_consumption_construction_source_audit.csv` and `result/alb2002_consumption_construction_source_summary.csv`. It documents the total-budget denominator variant with public IHSN source evidence and maps local `totcons` to public metadata `totcons3`, while keeping outcome, SDG 3.8.2, recipe, and climate-linkage readiness rows at zero.

ALB_2002 consumption aggregate metadata crosswalk:

| Metric | Value |
|---|---:|
| Aggregate crosswalk rows | {stats['alb2002_consumption_aggregate_crosswalk_rows']} |
| Local `Poverty_2002.sav` rows | {stats['alb2002_consumption_aggregate_crosswalk_local_poverty_rows']} |
| Local metadata catalog rows | {stats['alb2002_consumption_aggregate_crosswalk_metadata_catalog_rows']} |
| Raw `totcons` positive rows | {stats['alb2002_consumption_aggregate_crosswalk_raw_totcons_positive_rows']} |
| Candidate `total_consumption`/raw `totcons` match rows | {stats['alb2002_consumption_aggregate_crosswalk_candidate_totcons_match_rows']} |
| Questionnaire New Lek string hits | {stats['alb2002_consumption_aggregate_crosswalk_questionnaire_new_lek_hits']} |
| Questionnaire aggregate-formula hits | {stats['alb2002_consumption_aggregate_crosswalk_questionnaire_aggregate_formula_hits']} |
| Construction-source rows | {stats['alb2002_consumption_aggregate_crosswalk_construction_source_rows']} |
| Construction `.do` file rows | {stats['alb2002_consumption_aggregate_crosswalk_construction_do_file_rows']} |
| Metadata unit/period-ready rows | {stats['alb2002_consumption_aggregate_crosswalk_metadata_unit_period_ready_rows']} |
| Official documentation-ready rows | {stats['alb2002_consumption_aggregate_crosswalk_official_documentation_ready_rows']} |
| Released-variable mapping-ready rows | {stats['alb2002_consumption_aggregate_crosswalk_released_variable_mapping_ready_rows']} |
| Denominator-variant-ready rows | {stats['alb2002_consumption_aggregate_crosswalk_denominator_variant_ready_rows']} |
| Recipe-ready rows | {stats['alb2002_consumption_aggregate_crosswalk_recipe_ready_rows']} |
| Outcome-ready rows | {stats['alb2002_consumption_aggregate_crosswalk_outcome_ready_rows']} |
| SDG 3.8.2-ready rows | {stats['alb2002_consumption_aggregate_crosswalk_sdg382_ready_rows']} |
| Climate-linkage-ready rows | {stats['alb2002_consumption_aggregate_crosswalk_climate_linkage_ready_rows']} |
| Decision | {stats['alb2002_consumption_aggregate_crosswalk_current_decision']} |

{markdown_count_table(alb2002_consumption_aggregate_family_counts, 'ALB_2002 consumption aggregate audit family') if alb2002_consumption_aggregate_audit else 'No ALB_2002 consumption aggregate metadata crosswalk audit exists yet.'}

{markdown_count_table(alb2002_consumption_aggregate_readiness_counts, 'ALB_2002 consumption aggregate readiness status') if alb2002_consumption_aggregate_audit else 'No ALB_2002 consumption aggregate readiness rows exist yet.'}

The ALB_2002 consumption aggregate metadata crosswalk is `report/alb2002_consumption_aggregate_metadata_crosswalk_audit.md`; machine-readable outputs are `temp/alb2002_consumption_aggregate_metadata_crosswalk_audit.csv` and `result/alb2002_consumption_aggregate_metadata_crosswalk_summary.csv`. It verifies that candidate `total_consumption` exactly copies raw `totcons` and imports the public source audit documenting local `totcons` as public `totcons3`. This resolves the narrow aggregate-construction documentation blocker, but all promotion rows remain zero because OOP, SDG, benchmark, and climate-geography gates remain unresolved.

ALB_2002 period-aligned CHE policy audit:

| Metric | Value |
|---|---:|
| Policy rows | {stats['alb2002_period_aligned_che_policy_rows']} |
| Household rows | {stats['alb2002_period_aligned_che_household_rows']} |
| Positive denominator rows | {stats['alb2002_period_aligned_che_denominator_rows']} |
| Denominator documented rows | {stats['alb2002_period_aligned_che_denominator_documented_rows']} |
| Period-alignment-ready rows | {stats['alb2002_period_aligned_che_period_alignment_ready_rows']} |
| Combined monthly-equivalent CHE10 rate | {stats['alb2002_period_aligned_che_combined_che10_rate']} |
| Combined monthly-equivalent weighted CHE10 rate | {stats['alb2002_period_aligned_che_combined_che10_weighted_rate']} |
| Combined monthly-equivalent CHE25 rate | {stats['alb2002_period_aligned_che_combined_che25_rate']} |
| Combined monthly-equivalent weighted CHE25 rate | {stats['alb2002_period_aligned_che_combined_che25_weighted_rate']} |
| Outcome-ready rows | {stats['alb2002_period_aligned_che_outcome_ready_rows']} |
| Recipe-ready rows | {stats['alb2002_period_aligned_che_recipe_ready_rows']} |
| SDG 3.8.2-ready rows | {stats['alb2002_period_aligned_che_sdg382_ready_rows']} |
| Climate-linkage-ready rows | {stats['alb2002_period_aligned_che_climate_linkage_ready_rows']} |
| Decision | {stats['alb2002_period_aligned_che_current_decision']} |

{markdown_count_table(alb2002_period_aligned_che_policy_counts, 'ALB_2002 period-aligned CHE policy') if alb2002_period_aligned_che_audit else 'No ALB_2002 period-aligned CHE policy rows exist yet.'}

{markdown_count_table(alb2002_period_aligned_che_promotion_counts, 'ALB_2002 period-aligned CHE promotion status') if alb2002_period_aligned_che_audit else 'No ALB_2002 period-aligned CHE promotion rows exist yet.'}

The ALB_2002 period-aligned CHE policy audit is `report/alb2002_period_aligned_che_policy_audit.md`; machine-readable outputs are `temp/alb2002_period_aligned_che_policy_audit.csv` and `result/alb2002_period_aligned_che_policy_summary.csv`. It corrects the stress-test period comparison by scaling four-week OOP by `13/12` and twelve-month hospital/dentist OOP by `1/12` against the documented monthly total-budget denominator. The combined no-gifts-with-transport monthly-equivalent policy gives CHE10 and CHE25 rates of {stats['alb2002_period_aligned_che_combined_che10_rate']} and {stats['alb2002_period_aligned_che_combined_che25_rate']} unweighted, but it remains fail-closed with zero outcome, recipe, SDG 3.8.2, and climate-linkage promotion rows.

ALB_2002 CHE candidate outcome audit:

| Metric | Value |
|---|---:|
| Household candidate rows | {stats['alb2002_che_candidate_household_rows']} |
| Positive denominator rows | {stats['alb2002_che_candidate_denominator_rows']} |
| Missing denominator rows | {stats['alb2002_che_candidate_missing_rows']} |
| Positive OOP rows | {stats['alb2002_che_candidate_positive_oop_rows']} |
| Weighted positive OOP rate | {stats['alb2002_che_candidate_positive_oop_weighted_rate']} |
| CHE10 rows | {stats['alb2002_che_candidate_che10_rows']} |
| CHE10 rate | {stats['alb2002_che_candidate_che10_rate']} |
| Weighted CHE10 rate | {stats['alb2002_che_candidate_che10_weighted_rate']} |
| CHE25 rows | {stats['alb2002_che_candidate_che25_rows']} |
| CHE25 rate | {stats['alb2002_che_candidate_che25_rate']} |
| Weighted CHE25 rate | {stats['alb2002_che_candidate_che25_weighted_rate']} |
| Period-policy rows consumed | {stats['alb2002_che_candidate_period_policy_rows']} |
| Positive-weight rows consumed | {stats['alb2002_che_candidate_weight_positive_rows']} |
| Weighted-inference-ready rows | {stats['alb2002_che_candidate_weighted_inference_ready_rows']} |
| Minimum-recipe harmonized-ready rows | {stats['alb2002_che_candidate_minimum_recipe_harmonized_ready_rows']} |
| Minimum-recipe outcome-ready rows | {stats['alb2002_che_candidate_minimum_recipe_outcome_ready_rows']} |
| Climate-linkage-ready rows | {stats['alb2002_che_candidate_climate_linkage_ready_rows']} |
| Outcome-promotion-ready rows | {stats['alb2002_che_candidate_outcome_promotion_ready_rows']} |
| Decision | {stats['alb2002_che_candidate_current_decision']} |

{markdown_count_table(alb2002_che_candidate_outcome_counts, 'ALB_2002 CHE candidate outcome') if alb2002_che_candidate_audit else 'No ALB_2002 CHE candidate outcome rows exist yet.'}

{markdown_count_table(alb2002_che_candidate_promotion_counts, 'ALB_2002 CHE candidate promotion status') if alb2002_che_candidate_audit else 'No ALB_2002 CHE candidate promotion rows exist yet.'}

The ALB_2002 CHE candidate outcome audit is `report/alb2002_che_candidate_outcome_audit.md`; machine-readable outputs are `temp/alb2002_che_candidate_household_outcomes.csv`, `temp/alb2002_che_candidate_outcome_lineage.csv`, `result/alb2002_che_candidate_outcome_audit.csv`, and `result/alb2002_che_candidate_outcome_summary.csv`. It materializes household-level CHE10/CHE25 candidates in `temp/` from the period-aligned combined no-gifts-with-transport OOP numerator and the documented monthly total-budget denominator candidate. It writes no `data/` outputs: outcome-promotion-ready and climate-linkage-ready rows remain {stats['alb2002_che_candidate_outcome_promotion_ready_rows']} and {stats['alb2002_che_candidate_climate_linkage_ready_rows']} until recipe, SDG 3.8.2, benchmark, and climate-geography gates pass.

ALB_2002 access candidate outcome audit:

| Metric | Value |
|---|---:|
| Household candidate rows | {stats['alb2002_access_candidate_household_rows']} |
| Lineage rows | {stats['alb2002_access_candidate_lineage_rows']} |
| Audit rows | {stats['alb2002_access_candidate_audit_rows']} |
| q01 need rows | {stats['alb2002_access_candidate_q01_need_rows']} |
| Person-need proxy rows | {stats['alb2002_access_candidate_person_need_rows']} |
| q01 cost-difficulty rows | {stats['alb2002_access_candidate_q01_cost_difficulty_rows']} |
| Delayed-help rows | {stats['alb2002_access_candidate_delayed_help_rows']} |
| Referral-not-gone rows | {stats['alb2002_access_candidate_referral_not_gone_rows']} |
| Refused-service rows | {stats['alb2002_access_candidate_refused_service_rows']} |
| Medicine-discount barrier rows | {stats['alb2002_access_candidate_medicine_discount_any_barrier_rows']} |
| Composite cost-barrier rows | {stats['alb2002_access_candidate_composite_cost_rows']} |
| Composite cost-barrier rate | {stats['alb2002_access_candidate_composite_cost_rate']} |
| Weighted composite cost-barrier rate | {stats['alb2002_access_candidate_composite_cost_weighted_rate']} |
| Composite any-barrier rows | {stats['alb2002_access_candidate_composite_any_rows']} |
| Composite any-barrier rate | {stats['alb2002_access_candidate_composite_any_rate']} |
| Weighted composite any-barrier rate | {stats['alb2002_access_candidate_composite_any_weighted_rate']} |
| Low-event rows | {stats['alb2002_access_candidate_low_event_rate_rows']} |
| Recipe-ready rows | {stats['alb2002_access_candidate_recipe_ready_rows']} |
| Climate-linkage-ready rows | {stats['alb2002_access_candidate_climate_linkage_ready_rows']} |
| Outcome-promotion-ready rows | {stats['alb2002_access_candidate_outcome_promotion_ready_rows']} |
| Decision | {stats['alb2002_access_candidate_current_decision']} |

{markdown_count_table(alb2002_access_candidate_outcome_counts, 'ALB_2002 access candidate outcome') if alb2002_access_candidate_audit else 'No ALB_2002 access candidate outcome rows exist yet.'}

{markdown_count_table(alb2002_access_candidate_family_counts, 'ALB_2002 access candidate family') if alb2002_access_candidate_audit else 'No ALB_2002 access candidate family rows exist yet.'}

{markdown_count_table(alb2002_access_candidate_promotion_counts, 'ALB_2002 access candidate promotion status') if alb2002_access_candidate_audit else 'No ALB_2002 access candidate promotion rows exist yet.'}

The ALB_2002 access candidate outcome audit is `report/alb2002_access_candidate_outcome_audit.md`; machine-readable outputs are `temp/alb2002_access_candidate_household_outcomes.csv`, `temp/alb2002_access_candidate_outcome_lineage.csv`, `result/alb2002_access_candidate_outcome_audit.csv`, and `result/alb2002_access_candidate_outcome_summary.csv`. It materializes household-level need, access-barrier, and composite candidates in `temp/` from raw Health A/B variables. It writes no `data/` outputs: outcome-promotion-ready and climate-linkage-ready rows remain {stats['alb2002_access_candidate_outcome_promotion_ready_rows']} and {stats['alb2002_access_candidate_climate_linkage_ready_rows']} until denominator, skip-path, recipe, financial-alignment, and climate-geography gates pass.

ALB_2002 UHC composite candidate outcome audit:

| Metric | Value |
|---|---:|
| Household candidate rows | {stats['alb2002_uhc_composite_candidate_household_rows']} |
| Lineage rows | {stats['alb2002_uhc_composite_candidate_lineage_rows']} |
| Audit rows | {stats['alb2002_uhc_composite_candidate_audit_rows']} |
| Source CHE10 rows | {stats['alb2002_uhc_composite_candidate_source_che10_rows']} |
| Source CHE25 rows | {stats['alb2002_uhc_composite_candidate_source_che25_rows']} |
| Source access any-barrier rows | {stats['alb2002_uhc_composite_candidate_source_access_any_rows']} |
| CHE10-or-access rows | {stats['alb2002_uhc_composite_candidate_che10_or_access_rows']} |
| CHE10-or-access rate | {stats['alb2002_uhc_composite_candidate_che10_or_access_rate']} |
| Weighted CHE10-or-access rate | {stats['alb2002_uhc_composite_candidate_che10_or_access_weighted_rate']} |
| CHE25-or-access rows | {stats['alb2002_uhc_composite_candidate_che25_or_access_rows']} |
| CHE25-or-access rate | {stats['alb2002_uhc_composite_candidate_che25_or_access_rate']} |
| Weighted CHE25-or-access rate | {stats['alb2002_uhc_composite_candidate_che25_or_access_weighted_rate']} |
| Financial-only CHE10 rows | {stats['alb2002_uhc_composite_candidate_financial_only_che10_rows']} |
| Access-only versus CHE10 rows | {stats['alb2002_uhc_composite_candidate_access_only_vs_che10_rows']} |
| Both CHE10 and access rows | {stats['alb2002_uhc_composite_candidate_both_che10_access_rows']} |
| Financial-only CHE25 rows | {stats['alb2002_uhc_composite_candidate_financial_only_che25_rows']} |
| Access-only versus CHE25 rows | {stats['alb2002_uhc_composite_candidate_access_only_vs_che25_rows']} |
| Both CHE25 and access rows | {stats['alb2002_uhc_composite_candidate_both_che25_access_rows']} |
| Coping rows | {stats['alb2002_uhc_composite_candidate_coping_rows']} |
| Low-event rows | {stats['alb2002_uhc_composite_candidate_low_event_rate_rows']} |
| Recipe-ready rows | {stats['alb2002_uhc_composite_candidate_recipe_ready_rows']} |
| Climate-linkage-ready rows | {stats['alb2002_uhc_composite_candidate_climate_linkage_ready_rows']} |
| Outcome-promotion-ready rows | {stats['alb2002_uhc_composite_candidate_outcome_promotion_ready_rows']} |
| Decision | {stats['alb2002_uhc_composite_candidate_current_decision']} |

{markdown_count_table(alb2002_uhc_composite_outcome_counts, 'ALB_2002 UHC composite candidate outcome') if alb2002_uhc_composite_audit else 'No ALB_2002 UHC composite candidate outcome rows exist yet.'}

{markdown_count_table(alb2002_uhc_composite_family_counts, 'ALB_2002 UHC composite candidate family') if alb2002_uhc_composite_audit else 'No ALB_2002 UHC composite candidate family rows exist yet.'}

{markdown_count_table(alb2002_uhc_composite_promotion_counts, 'ALB_2002 UHC composite candidate promotion status') if alb2002_uhc_composite_audit else 'No ALB_2002 UHC composite candidate promotion rows exist yet.'}

The ALB_2002 UHC composite candidate audit is `report/alb2002_uhc_composite_candidate_audit.md`; machine-readable outputs are `temp/alb2002_uhc_composite_candidate_outcomes.csv`, `temp/alb2002_uhc_composite_candidate_lineage.csv`, `result/alb2002_uhc_composite_candidate_audit.csv`, and `result/alb2002_uhc_composite_candidate_summary.csv`. It combines temp-only CHE and access candidates into double-failure, financial-only, access-only, both-failure, and coping candidate categories. It writes no `data/` outputs: outcome-promotion-ready and climate-linkage-ready rows remain {stats['alb2002_uhc_composite_candidate_outcome_promotion_ready_rows']} and {stats['alb2002_uhc_composite_candidate_climate_linkage_ready_rows']} until the financial-outcome, access-outcome, recipe, SDG, benchmark, and climate-geography gates pass.

ALB_2002 joined analysis-candidate readiness audit:

| Metric | Value |
|---|---:|
| Candidate rows | {stats['alb2002_analysis_candidate_rows']} |
| Candidate columns | {stats['alb2002_analysis_candidate_columns']} |
| Lineage rows | {stats['alb2002_analysis_candidate_lineage_rows']} |
| Readiness audit rows | {stats['alb2002_analysis_candidate_audit_rows']} |
| Complete candidate gates | {stats['alb2002_analysis_candidate_complete_candidate_gates']} |
| Missing gates | {stats['alb2002_analysis_candidate_missing_gates']} |
| Blocked promotion gates | {stats['alb2002_analysis_candidate_blocked_promotion_gates']} |
| Harmonized-ready rows | {stats['alb2002_analysis_candidate_harmonized_ready_rows']} |
| Outcome-promotion-ready rows | {stats['alb2002_analysis_candidate_outcome_promotion_ready_rows']} |
| Climate-linkage-ready rows | {stats['alb2002_analysis_candidate_climate_linkage_ready_rows']} |
| Data-write-ready rows | {stats['alb2002_analysis_candidate_data_write_ready_rows']} |
| Decision | {stats['alb2002_analysis_candidate_current_decision']} |

{markdown_count_table(alb2002_analysis_candidate_status_counts, 'ALB_2002 analysis candidate status') if alb2002_analysis_candidate_audit else 'No ALB_2002 analysis-candidate readiness rows exist yet.'}

{markdown_count_table(alb2002_analysis_candidate_family_counts, 'ALB_2002 analysis candidate field family') if alb2002_analysis_candidate_audit else 'No ALB_2002 analysis-candidate field-family rows exist yet.'}

The ALB_2002 analysis-candidate readiness audit is `report/alb2002_analysis_candidate_readiness_audit.md`; machine-readable outputs are `temp/alb2002_analysis_candidate_dataset.csv`, `temp/alb2002_analysis_candidate_lineage.csv`, `result/alb2002_analysis_candidate_readiness_audit.csv`, and `result/alb2002_analysis_candidate_readiness_summary.csv`. It joins household core, timing, admin geography, weights, demographic covariates, access signals, and temp CHE candidate outcomes into one temp-only inspection dataset. It is not a promoted harmonized, outcome, or climate-linked dataset: data-write-ready rows remain {stats['alb2002_analysis_candidate_data_write_ready_rows']}, and point-coordinate and historical-boundary climate gates remain unresolved.

ALB_2002 climate centroid exposure stress test:

| Metric | Value |
|---|---:|
| District-month input rows | {stats['alb2002_climate_centroid_input_rows']} |
| Distinct district rows | {stats['alb2002_climate_centroid_distinct_district_rows']} |
| Household rows covered | {stats['alb2002_climate_centroid_household_rows_covered']} |
| Exposure rows | {stats['alb2002_climate_centroid_exposure_rows']} |
| Exposure windows | {stats['alb2002_climate_centroid_window_rows']} |
| NASA API/cache rows | {stats['alb2002_climate_centroid_nasa_api_rows']} |
| NASA downloaded rows | {stats['alb2002_climate_centroid_nasa_downloaded_rows']} |
| NASA cached rows | {stats['alb2002_climate_centroid_nasa_cached_rows']} |
| NASA failed rows | {stats['alb2002_climate_centroid_nasa_failed_rows']} |
| Nonmissing precipitation rows | {stats['alb2002_climate_centroid_precip_nonmissing_rows']} |
| Nonmissing temperature rows | {stats['alb2002_climate_centroid_temp_nonmissing_rows']} |
| Boundary year | {stats['alb2002_climate_centroid_boundary_year']} |
| Historical-boundary-ready rows | {stats['alb2002_climate_centroid_historical_boundary_ready_rows']} |
| Primary CHIRPS-ready rows | {stats['alb2002_climate_centroid_primary_chirps_ready_rows']} |
| Primary ERA5-ready rows | {stats['alb2002_climate_centroid_primary_era5_ready_rows']} |
| Historical-baseline-ready rows | {stats['alb2002_climate_centroid_historical_baseline_ready_rows']} |
| Climate-linkage-ready rows | {stats['alb2002_climate_centroid_climate_linkage_ready_rows']} |
| Data-write-ready rows | {stats['alb2002_climate_centroid_data_write_ready_rows']} |
| Decision | {stats['alb2002_climate_centroid_current_decision']} |

{markdown_count_table(alb2002_climate_centroid_status_counts, 'ALB_2002 climate centroid audit status') if alb2002_climate_centroid_audit else 'No ALB_2002 climate centroid exposure audit rows exist yet.'}

{markdown_count_table(alb2002_climate_centroid_api_counts, 'ALB_2002 climate centroid NASA API/cache status') if alb2002_climate_centroid_manifest else 'No ALB_2002 climate centroid NASA API manifest rows exist yet.'}

The ALB_2002 climate centroid exposure audit is `report/alb2002_climate_centroid_exposure_audit.md`; machine-readable outputs are `temp/alb2002_climate_centroid_exposure_input.csv`, `temp/alb2002_climate_centroid_exposure_candidates.csv`, `temp/alb2002_climate_centroid_nasa_power_api_manifest.csv`, `result/alb2002_climate_centroid_exposure_audit.csv`, and `result/alb2002_climate_centroid_exposure_summary.csv`. It computes 1, 3, 6, and 12 month NASA POWER fallback summaries at candidate ADM2 bounding-box centroids for observed ALB_2002 district-month cells. It is a temp-only stress test: boundary year remains {stats['alb2002_climate_centroid_boundary_year']}, primary CHIRPS/ERA5 extraction and historical baselines are not accepted, and climate-linkage/data-write-ready rows remain {stats['alb2002_climate_centroid_climate_linkage_ready_rows']} and {stats['alb2002_climate_centroid_data_write_ready_rows']}.

ALB_2002 climate shock candidate diagnostics:

| Metric | Value |
|---|---:|
| Diagnostic exposure rows | {stats['alb2002_climate_shock_candidate_exposure_rows']} |
| Source centroid rows | {stats['alb2002_climate_shock_candidate_source_centroid_rows']} |
| Lineage rows | {stats['alb2002_climate_shock_candidate_lineage_rows']} |
| Audit rows | {stats['alb2002_climate_shock_candidate_audit_rows']} |
| Reference groups | {stats['alb2002_climate_shock_candidate_reference_group_rows']} |
| Minimum reference-group size | {stats['alb2002_climate_shock_candidate_min_reference_group_size']} |
| Rainfall z-score rows | {stats['alb2002_climate_shock_candidate_precip_z_nonmissing_rows']} |
| Temperature z-score rows | {stats['alb2002_climate_shock_candidate_temp_z_nonmissing_rows']} |
| Low-rain diagnostic rows | {stats['alb2002_climate_shock_candidate_low_rain_rows']} |
| Severe low-rain diagnostic rows | {stats['alb2002_climate_shock_candidate_severe_low_rain_rows']} |
| Extreme-wet diagnostic rows | {stats['alb2002_climate_shock_candidate_extreme_wet_rows']} |
| Heat diagnostic rows | {stats['alb2002_climate_shock_candidate_heat_rows']} |
| Extreme-heat diagnostic rows | {stats['alb2002_climate_shock_candidate_extreme_heat_rows']} |
| Cold diagnostic rows | {stats['alb2002_climate_shock_candidate_cold_rows']} |
| Combined-stress diagnostic rows | {stats['alb2002_climate_shock_candidate_combined_stress_rows']} |
| Primary CHIRPS-ready rows | {stats['alb2002_climate_shock_candidate_primary_chirps_ready_rows']} |
| Primary ERA5-ready rows | {stats['alb2002_climate_shock_candidate_primary_era5_ready_rows']} |
| Historical-baseline-ready rows | {stats['alb2002_climate_shock_candidate_historical_baseline_ready_rows']} |
| Climate-linkage-ready rows | {stats['alb2002_climate_shock_candidate_climate_linkage_ready_rows']} |
| Data-write-ready rows | {stats['alb2002_climate_shock_candidate_data_write_ready_rows']} |
| Decision | {stats['alb2002_climate_shock_candidate_current_decision']} |

{markdown_count_table(alb2002_climate_shock_status_counts, 'ALB_2002 climate shock diagnostic audit status') if alb2002_climate_shock_audit else 'No ALB_2002 climate shock diagnostic audit rows exist yet.'}

{markdown_count_table(alb2002_climate_shock_lineage_status_counts, 'ALB_2002 climate shock diagnostic lineage status') if alb2002_climate_shock_lineage else 'No ALB_2002 climate shock diagnostic lineage rows exist yet.'}

The ALB_2002 climate shock candidate audit is `report/alb2002_climate_shock_candidate_audit.md`; machine-readable outputs are `temp/alb2002_climate_shock_candidate_exposures.csv`, `temp/alb2002_climate_shock_candidate_lineage.csv`, `result/alb2002_climate_shock_candidate_audit.csv`, and `result/alb2002_climate_shock_candidate_summary.csv`. It standardizes NASA POWER fallback rainfall and temperature within each survey-month/window candidate district distribution. These are diagnostic z-scores only, not local historical anomalies or accepted treatment variables; primary CHIRPS/ERA5 extraction, historical baselines, verified geography, climate-linkage promotion, and data writes remain blocked.

ALB_2002 climate/outcome linked candidate audit:

| Metric | Value |
|---|---:|
| Linked household-window rows | {stats['alb2002_climate_outcome_linked_candidate_rows']} |
| Distinct households | {stats['alb2002_climate_outcome_linked_candidate_household_rows']} |
| Diagnostic exposure windows | {stats['alb2002_climate_outcome_linked_candidate_window_rows']} |
| District-month cells | {stats['alb2002_climate_outcome_linked_candidate_district_month_cells']} |
| Expected rows | {stats['alb2002_climate_outcome_linked_candidate_expected_rows']} |
| Unmatched rows | {stats['alb2002_climate_outcome_linked_candidate_unmatched_rows']} |
| Rainfall z-score rows | {stats['alb2002_climate_outcome_linked_candidate_precip_z_rows']} |
| Temperature z-score rows | {stats['alb2002_climate_outcome_linked_candidate_temp_z_rows']} |
| Combined-stress rows | {stats['alb2002_climate_outcome_linked_candidate_combined_stress_rows']} |
| CHE10-or-access rows | {stats['alb2002_climate_outcome_linked_candidate_che10_or_access_rows']} |
| CHE25-or-access rows | {stats['alb2002_climate_outcome_linked_candidate_che25_or_access_rows']} |
| Both CHE10/access rows | {stats['alb2002_climate_outcome_linked_candidate_both_che10_access_rows']} |
| Coping rows | {stats['alb2002_climate_outcome_linked_candidate_coping_rows']} |
| Harmonized-recipe-ready rows | {stats['alb2002_climate_outcome_linked_candidate_harmonized_recipe_ready_rows']} |
| Outcome-promotion-ready rows | {stats['alb2002_climate_outcome_linked_candidate_outcome_promotion_ready_rows']} |
| Climate-linkage-ready rows | {stats['alb2002_climate_outcome_linked_candidate_climate_linkage_ready_rows']} |
| Data-write-ready rows | {stats['alb2002_climate_outcome_linked_candidate_data_write_ready_rows']} |
| Decision | {stats['alb2002_climate_outcome_linked_candidate_current_decision']} |

{markdown_count_table(alb2002_climate_outcome_linked_status_counts, 'ALB_2002 climate/outcome linked audit status') if alb2002_climate_outcome_linked_audit else 'No ALB_2002 climate/outcome linked candidate audit rows exist yet.'}

{markdown_count_table(alb2002_climate_outcome_linked_lineage_status_counts, 'ALB_2002 climate/outcome linked lineage status') if alb2002_climate_outcome_linked_lineage else 'No ALB_2002 climate/outcome linked lineage rows exist yet.'}

The ALB_2002 climate/outcome linked candidate audit is `report/alb2002_climate_outcome_linked_candidate_audit.md`; machine-readable outputs are `temp/alb2002_climate_outcome_linked_candidate.csv`, `temp/alb2002_climate_outcome_linked_candidate_lineage.csv`, `result/alb2002_climate_outcome_linked_candidate_audit.csv`, and `result/alb2002_climate_outcome_linked_candidate_summary.csv`. It mechanically joins temp household/outcome candidates to diagnostic climate-window rows. It remains temp-only and does not satisfy the promoted climate-linked dataset requirement.

ALB_2002 linked-candidate descriptive screen:

| Metric | Value |
|---|---:|
| Input household-window rows | {stats['alb2002_linked_candidate_descriptive_input_rows']} |
| Deduplicated households | {stats['alb2002_linked_candidate_descriptive_household_rows']} |
| Diagnostic exposure windows | {stats['alb2002_linked_candidate_descriptive_window_rows']} |
| Audit rows | {stats['alb2002_linked_candidate_descriptive_audit_rows']} |
| Diagnostic cell rows | {stats['alb2002_linked_candidate_descriptive_cell_rows']} |
| Household outcome cells | {stats['alb2002_linked_candidate_descriptive_household_outcome_cell_rows']} |
| Subgroup outcome cells | {stats['alb2002_linked_candidate_descriptive_subgroup_outcome_cell_rows']} |
| Climate flag cells | {stats['alb2002_linked_candidate_descriptive_climate_flag_cell_rows']} |
| Outcome-by-climate flag cells | {stats['alb2002_linked_candidate_descriptive_outcome_by_climate_flag_cell_rows']} |
| CHE10-or-access households | {stats['alb2002_linked_candidate_descriptive_che10_or_access_households']} |
| CHE25-or-access households | {stats['alb2002_linked_candidate_descriptive_che25_or_access_households']} |
| Both CHE10/access households | {stats['alb2002_linked_candidate_descriptive_both_che10_access_households']} |
| Coping households | {stats['alb2002_linked_candidate_descriptive_coping_households']} |
| Combined-stress rows | {stats['alb2002_linked_candidate_descriptive_combined_stress_rows']} |
| Harmonized-recipe-ready rows | {stats['alb2002_linked_candidate_descriptive_harmonized_recipe_ready_rows']} |
| Outcome-promotion-ready rows | {stats['alb2002_linked_candidate_descriptive_outcome_promotion_ready_rows']} |
| Climate-linkage-ready rows | {stats['alb2002_linked_candidate_descriptive_climate_linkage_ready_rows']} |
| Data-write-ready rows | {stats['alb2002_linked_candidate_descriptive_data_write_ready_rows']} |
| Decision | {stats['alb2002_linked_candidate_descriptive_current_decision']} |

{markdown_count_table(alb2002_linked_candidate_descriptive_status_counts, 'ALB_2002 linked-candidate descriptive audit status') if alb2002_linked_candidate_descriptive_audit else 'No ALB_2002 linked-candidate descriptive audit rows exist yet.'}

{markdown_count_table(alb2002_linked_candidate_descriptive_scope_counts, 'ALB_2002 linked-candidate descriptive cell scopes') if alb2002_linked_candidate_descriptive_cells else 'No ALB_2002 linked-candidate descriptive cells exist yet.'}

The ALB_2002 linked-candidate descriptive screen is `report/alb2002_linked_candidate_descriptive_diagnostics.md`; machine-readable outputs are `result/alb2002_linked_candidate_descriptive_audit.csv`, `result/alb2002_linked_candidate_descriptive_cells.csv`, and `result/alb2002_linked_candidate_descriptive_summary.csv`. It summarizes candidate outcome rates on deduplicated households and candidate climate-flag screens on repeated household-window rows. It remains a non-promoted audit screen and does not satisfy the final descriptive-diagnostics criterion.

ALB_2002 minimum recipe promotion packet:

| Metric | Value |
|---|---:|
| Action rows | {stats['alb2002_minimum_recipe_promotion_action_rows']} |
| Gate rows | {stats['alb2002_minimum_recipe_promotion_gate_rows']} |
| Blocked gates | {stats['alb2002_minimum_recipe_promotion_blocked_gates']} |
| Candidate gates | {stats['alb2002_minimum_recipe_promotion_candidate_gates']} |
| Harmonized-ready rows | {stats['alb2002_minimum_recipe_promotion_harmonized_ready_rows']} |
| Outcome-ready rows | {stats['alb2002_minimum_recipe_promotion_outcome_ready_rows']} |
| SDG 3.8.2-ready rows | {stats['alb2002_minimum_recipe_promotion_sdg382_ready_rows']} |
| Climate-linkage-ready rows | {stats['alb2002_minimum_recipe_promotion_climate_linkage_ready_rows']} |
| Decision | {stats['alb2002_minimum_recipe_promotion_current_decision']} |

{markdown_count_table(alb2002_minimum_recipe_action_status_counts, 'ALB_2002 minimum recipe action blocking status') if alb2002_minimum_recipe_actions else 'No ALB_2002 minimum recipe promotion action rows exist yet.'}

{markdown_count_table(alb2002_minimum_recipe_gate_status_counts, 'ALB_2002 minimum recipe gate status') if alb2002_minimum_recipe_gates else 'No ALB_2002 minimum recipe gate rows exist yet.'}

{markdown_count_table(alb2002_minimum_recipe_required_counts, 'ALB_2002 minimum recipe gate requirement') if alb2002_minimum_recipe_gates else 'No ALB_2002 minimum recipe gate requirement rows exist yet.'}

The ALB_2002 minimum recipe promotion packet is `report/alb2002_minimum_recipe_promotion_packet.md`; machine-readable outputs are `temp/alb2002_minimum_recipe_promotion_action_queue.csv`, `temp/alb2002_minimum_recipe_promotion_gate_checklist.csv`, and `result/alb2002_minimum_recipe_promotion_summary.csv`. It consolidates the top-ranked temp candidate into household-frame, weight, timing, denominator, OOP, access, outcome, SDG, harmonized-dataset, and climate-dataset gates. It is fail-closed: harmonized-ready, outcome-ready, SDG 3.8.2-ready, and climate-linkage-ready rows remain {stats['alb2002_minimum_recipe_promotion_harmonized_ready_rows']}, {stats['alb2002_minimum_recipe_promotion_outcome_ready_rows']}, {stats['alb2002_minimum_recipe_promotion_sdg382_ready_rows']}, and {stats['alb2002_minimum_recipe_promotion_climate_linkage_ready_rows']}.

ALB_2002 district climate crosswalk:

{markdown_count_table(alb2002_crosswalk_status_counts, 'ALB_2002 district crosswalk status') if alb2002_crosswalk_template else 'No ALB_2002 district crosswalk template exists yet.'}

{markdown_count_table(alb2002_boundary_probe_counts, 'ALB_2002 boundary source probe status') if alb2002_boundary_probe else 'No ALB_2002 boundary source probe rows exist yet.'}

The ALB_2002 district climate-crosswalk audit is `report/alb2002_district_climate_crosswalk_audit.md`; machine-readable outputs are `temp/alb2002_district_climate_crosswalk_template.csv`, `temp/alb2002_district_boundary_source_probe.csv`, and `result/alb2002_district_climate_crosswalk_summary.csv`. It builds a review template from observed district names/codes and probes public ADM2 boundary metadata only. It does not download polygons, assign centroids, create `data/climate_linkage_input.csv`, or construct climate exposures. Climate-linkage-ready rows are {stats['alb2002_climate_linkage_ready_rows']}.

ALB_2002 boundary name-match audit:

{markdown_count_table(alb2002_boundary_name_method_counts, 'ALB_2002 boundary name match method') if alb2002_boundary_name_audit else 'No ALB_2002 boundary name-match audit exists yet.'}

{markdown_count_table(alb2002_boundary_name_status_counts, 'ALB_2002 boundary name match status') if alb2002_boundary_name_audit else 'No ALB_2002 boundary name-match status rows exist yet.'}

The ALB_2002 boundary name-match audit is `report/alb2002_boundary_name_match_audit.md`; machine-readable outputs are `temp/alb2002_boundary_name_match_audit.csv`, `temp/alb2002_boundary_geojson_inventory.csv`, `temp/source_snapshots/alb2002_geoboundaries_alb_adm2_current.geojson`, and `result/alb2002_boundary_name_match_summary.csv`. It downloads the public current ADM2 boundary GeoJSON and compares boundary names to survey district labels. It finds {stats['alb2002_boundary_name_match_exact_rows']} exact normalized name matches, {stats['alb2002_boundary_name_match_euro_repaired_rows']} mojibake-repaired match, {stats['alb2002_boundary_name_match_unmatched_survey_rows']} unmatched survey district row, and {stats['alb2002_boundary_name_match_duplicate_boundary_name_keys']} duplicate boundary-name keys. Historical-ready and climate-linkage-ready rows are {stats['alb2002_boundary_name_match_historical_year_ready_rows']} and {stats['alb2002_boundary_name_match_climate_linkage_ready_rows']}; current decision is `{stats['alb2002_boundary_name_match_current_decision']}`.

ALB_2002 boundary source alternatives:

{markdown_count_table(alb2002_boundary_source_probe_counts, 'ALB_2002 boundary source probe status') if alb2002_boundary_source_audit else 'No ALB_2002 boundary source-alternative audit exists yet.'}

{markdown_count_table(alb2002_boundary_source_suitability_counts, 'ALB_2002 boundary source suitability') if alb2002_boundary_source_audit else 'No ALB_2002 boundary source suitability rows exist yet.'}

The ALB_2002 boundary source-alternatives audit is `report/alb2002_boundary_source_alternative_audit.md`; machine-readable outputs are `temp/alb2002_boundary_source_alternative_audit.csv` and `result/alb2002_boundary_source_alternative_summary.csv`. It reviews current/post-2015 public boundary catalogs, the official ALB_2002 study documentation, INSTAT census context, and IHGIS historical census leads without downloading GIS files. It confirms source leads but keeps historical-boundary-ready and climate-linkage-ready rows at {stats['alb2002_boundary_source_alternative_historical_ready_rows']} and {stats['alb2002_boundary_source_alternative_climate_linkage_ready_rows']}; current decision is `{stats['alb2002_boundary_source_alternative_current_decision']}`.

ALB_2002 boundary resource search:

{markdown_count_table(alb2002_boundary_resource_status_counts, 'ALB_2002 boundary resource status') if alb2002_boundary_resource_audit else 'No ALB_2002 boundary resource-search audit exists yet.'}

{markdown_count_table(alb2002_boundary_resource_suitability_counts, 'ALB_2002 boundary resource suitability') if alb2002_boundary_resource_audit else 'No ALB_2002 boundary resource suitability rows exist yet.'}

The ALB_2002 boundary resource-search audit is `report/alb2002_boundary_source_resource_search_audit.md`; machine-readable outputs are `temp/alb2002_boundary_source_resource_search_audit.csv` and `result/alb2002_boundary_source_resource_search_summary.csv`. It parses public boundary/gazetteer resources and identifies `{stats['alb2002_boundary_resource_search_best_candidate_id']}` as the strongest name-coverage lead: {stats['alb2002_boundary_resource_search_best_candidate_exact_matches']} exact matches, {stats['alb2002_boundary_resource_search_best_candidate_repaired_matches']} encoding-repaired matches, and {stats['alb2002_boundary_resource_search_best_candidate_alias_matches']} documented alias matches. This is not a climate input yet. Historical-boundary-ready and climate-linkage-ready rows remain {stats['alb2002_boundary_resource_search_2002_historical_ready_rows']} and {stats['alb2002_boundary_resource_search_climate_linkage_ready_rows']}; current decision is `{stats['alb2002_boundary_resource_search_current_decision']}`.

ALB_2002 boundary geometry/provenance audit:

{markdown_count_table(alb2002_boundary_geometry_status_counts, 'ALB_2002 boundary geometry structure status') if alb2002_boundary_geometry_audit else 'No ALB_2002 boundary geometry/provenance audit exists yet.'}

{markdown_count_table(alb2002_boundary_metadata_status_counts, 'ALB_2002 boundary metadata evidence status') if alb2002_boundary_metadata_probe else 'No ALB_2002 boundary metadata provenance rows exist yet.'}

The ALB_2002 boundary geometry/provenance audit is `report/alb2002_boundary_geometry_provenance_audit.md`; machine-readable outputs are `temp/alb2002_boundary_geometry_provenance_audit.csv`, `temp/alb2002_boundary_metadata_provenance_probe.csv`, and `result/alb2002_boundary_geometry_provenance_summary.csv`. It parses {stats['alb2002_boundary_geometry_feature_rows']} ADM2 features with {stats['alb2002_boundary_geometry_coordinate_structure_ok_rows']} coordinate-structure-ok rows and {stats['alb2002_boundary_geometry_survey_key_matched_rows']} survey-key matches, but the companion metadata reports boundary year {stats['alb2002_boundary_geometry_metadata_boundary_year']} and source {stats['alb2002_boundary_geometry_metadata_boundary_source']}. Boundary-year-matches-2002, topology-validated, historical-ready, and climate-linkage-ready rows remain {stats['alb2002_boundary_geometry_boundary_year_matches_2002_rows']}, {stats['alb2002_boundary_geometry_topology_validated_rows']}, {stats['alb2002_boundary_geometry_historical_2002_boundary_ready_rows']}, and {stats['alb2002_boundary_geometry_climate_linkage_ready_rows']}; current decision is `{stats['alb2002_boundary_geometry_current_decision']}`.

ALB_2002 boundary manual verification packet:

{markdown_count_table(alb2002_boundary_manual_action_status_counts, 'ALB_2002 boundary manual action status') if alb2002_boundary_manual_actions else 'No ALB_2002 boundary manual action rows exist yet.'}

{markdown_count_table(alb2002_boundary_manual_gate_status_counts, 'ALB_2002 boundary manual gate status') if alb2002_boundary_manual_gates else 'No ALB_2002 boundary manual gate rows exist yet.'}

The ALB_2002 boundary manual verification packet is `report/alb2002_boundary_manual_verification_packet.md`; machine-readable outputs are `temp/alb2002_boundary_manual_verification_action_queue.csv`, `temp/alb2002_boundary_promotion_gate_checklist.csv`, and `result/alb2002_boundary_manual_verification_packet_summary.csv`. It converts the boundary-source failure into {stats['alb2002_boundary_manual_verification_action_rows']} source-specific actions and {stats['alb2002_boundary_manual_verification_gate_rows']} explicit promotion gates, including {stats['alb2002_boundary_manual_verification_pre2011_digital_map_absence_rows']} UNECE/INSTAT negative-evidence row for pre-2011 national digital-map absence. Blocked gates remain {stats['alb2002_boundary_manual_verification_blocked_gates']}; climate-linkage-ready rows remain {stats['alb2002_boundary_manual_verification_climate_linkage_ready_rows']}; current decision is `{stats['alb2002_boundary_manual_verification_current_decision']}`.

ALB_2002 boundary manual source follow-up:

{markdown_count_table(alb2002_boundary_followup_blocker_counts, 'ALB_2002 boundary follow-up blocker') if alb2002_boundary_followup_audit else 'No ALB_2002 boundary source follow-up rows exist yet.'}

{markdown_count_table(alb2002_boundary_followup_level_counts, 'ALB_2002 boundary follow-up level compatibility') if alb2002_boundary_followup_audit else 'No ALB_2002 boundary source level-compatibility rows exist yet.'}

The ALB_2002 boundary manual source follow-up is `report/alb2002_boundary_manual_source_followup.md`; machine-readable outputs are `temp/alb2002_boundary_manual_source_followup_audit.csv` and `result/alb2002_boundary_manual_source_followup_summary.csv`. It records {stats['alb2002_boundary_manual_source_followup_rows']} source follow-up rows and {stats['alb2002_boundary_manual_source_followup_conclusive_blocker_rows']} conclusive blockers. The IHGIS lead is `{stats['alb2002_boundary_manual_source_followup_ipums_level_status']}`, so it is not sufficient for the 36-district ALB_2002 climate-linkage requirement. The UNECE/INSTAT pre-2011 map status is `{stats['alb2002_boundary_manual_source_followup_unece_pre2011_map_status']}`, so current or post-2011 public GIS layers still need separate historical continuity evidence before use. District-level-ready and climate-linkage-ready rows remain {stats['alb2002_boundary_manual_source_followup_district_level_ready_rows']} and {stats['alb2002_boundary_manual_source_followup_climate_linkage_ready_rows']}; current decision is `{stats['alb2002_boundary_manual_source_followup_current_decision']}`.

ALB_2002 GADM boundary lead audit:

{markdown_count_table(alb2002_gadm_status_counts, 'ALB_2002 GADM suitability status') if alb2002_gadm_audit else 'No ALB_2002 GADM boundary lead audit rows exist yet.'}

{markdown_count_table(alb2002_gadm_match_status_counts, 'ALB_2002 GADM name-match status') if alb2002_gadm_match_audit else 'No ALB_2002 GADM name-match rows exist yet.'}

The ALB_2002 GADM boundary lead audit is `report/alb2002_gadm_boundary_lead_audit.md`; machine-readable outputs are `temp/alb2002_gadm_boundary_lead_audit.csv`, `temp/alb2002_gadm_boundary_name_match_audit.csv`, and `result/alb2002_gadm_boundary_lead_summary.csv`. GADM 3.6 is a useful public lead because it has {stats['alb2002_gadm36_adm2_row_count']} ADM2 rows, {stats['alb2002_gadm36_distinct_normalized_key_count']} normalized keys, and complete ALB_2002 district-name coverage after documented repairs. It is still blocked because the normalized SHKODER key appears in duplicate boundary features and the audit does not verify official 2001/2002 boundary provenance. Historical-ready and climate-linkage-ready rows remain {stats['alb2002_gadm_boundary_lead_historical_2002_ready_rows']} and {stats['alb2002_gadm_boundary_lead_climate_linkage_ready_rows']}; current decision is `{stats['alb2002_gadm_boundary_lead_current_decision']}`.

ALB_2002 local geography artifacts:

{markdown_count_table(alb2002_local_geo_artifact_role_counts, 'ALB_2002 local geography evidence role') if alb2002_local_geo_artifact_audit else 'No ALB_2002 local geography artifact audit exists yet.'}

{markdown_count_table(alb2002_local_geo_artifact_status_counts, 'ALB_2002 local geography value status') if alb2002_local_geo_artifact_audit else 'No ALB_2002 local geography value-status rows exist yet.'}

The ALB_2002 local geography artifact audit is `report/alb2002_local_geography_artifact_audit.md`; machine-readable outputs are `temp/alb2002_local_geography_artifact_audit.csv` and `result/alb2002_local_geography_artifact_summary.csv`. It confirms a narrow but important gap: the questionnaire workbook has {stats['alb2002_local_geo_artifact_questionnaire_coordinate_field_rows']} longitude/latitude design fields and the raw schema has {stats['alb2002_local_geo_artifact_admin_variable_rows']} admin/sampling geography variables, but raw coordinate-variable rows and local GIS/boundary file candidates remain {stats['alb2002_local_geo_artifact_coordinate_raw_variable_rows']} and {stats['alb2002_local_geo_artifact_gis_file_candidate_rows']}. Local-coordinate-ready, local-boundary-ready, and climate-linkage-ready rows remain {stats['alb2002_local_geo_artifact_local_coordinate_ready_rows']}, {stats['alb2002_local_geo_artifact_local_boundary_ready_rows']}, and {stats['alb2002_local_geo_artifact_climate_linkage_ready_rows']}; current decision is `{stats['alb2002_local_geo_artifact_current_decision']}`.

ALB_2012 raw core feasibility:

{markdown_count_table(alb2012_core_audit_counts, 'ALB_2012 raw core audit status') if alb2012_core_audit else 'No ALB_2012 raw core feasibility audit exists yet.'}

{markdown_count_table(alb2012_core_lineage_counts, 'ALB_2012 raw core lineage status') if alb2012_core_lineage else 'No ALB_2012 raw core lineage rows exist yet.'}

The ALB_2012 raw core feasibility audit is `report/alb2012_raw_core_feasibility.md`; machine-readable outputs are `temp/alb2012_household_core_candidate.csv`, `temp/alb2012_raw_core_feasibility_audit.csv`, `temp/alb2012_raw_core_lineage.csv`, and `result/alb2012_raw_core_feasibility_summary.csv`. It reads the local 2012 raw files and builds a temp-only review candidate, but does not promote a harmonized recipe or climate-linkage input. It finds no interview timing and no coordinate signals; current geography is coarse prefecture/region/urban only.

ALB_2012 provisional outcome feasibility:

{markdown_count_table(alb2012_outcome_family_counts, 'ALB_2012 provisional outcome family') if alb2012_outcome_audit else 'No ALB_2012 provisional outcome feasibility audit exists yet.'}

{markdown_count_table(alb2012_outcome_status_counts, 'ALB_2012 provisional outcome promotion status') if alb2012_outcome_audit else 'No ALB_2012 provisional outcome promotion rows exist yet.'}

The ALB_2012 provisional outcome audit is `report/alb2012_provisional_outcome_feasibility.md`; machine-readable outputs are `temp/alb2012_provisional_outcome_feasibility_audit.csv` and `result/alb2012_provisional_outcome_feasibility_summary.csv`. It computes raw OOP/access/need event-rate diagnostics only. It does not construct SDG 3.8.2, final CHE10/CHE25, climate-linked, descriptive, causal, ML, or policy outcomes; promotion-ready rows are {stats['alb2012_provisional_outcome_ready_rows']} and provisional climate-linkage-ready rows are {stats['alb2012_provisional_climate_linkage_ready_rows']}.

ALB_2012 raw outcome-semantics value audit:

{markdown_count_table(alb2012_semantics_domain_counts, 'ALB_2012 raw semantics domain') if alb2012_semantics_audit else 'No ALB_2012 raw outcome-semantics audit exists yet.'}

{markdown_count_table(alb2012_semantics_promotion_counts, 'ALB_2012 raw semantics promotion status') if alb2012_semantics_audit else 'No ALB_2012 raw semantics promotion rows exist yet.'}

The ALB_2012 raw outcome-semantics audit is `report/alb2012_outcome_semantics_raw_value_audit.md`; machine-readable outputs are `temp/alb2012_outcome_semantics_raw_value_audit.csv` and `result/alb2012_outcome_semantics_raw_value_summary.csv`. It documents {stats['alb2012_outcome_semantics_raw_value_rows']} raw label/value rows across {stats['alb2012_outcome_semantics_source_files_scanned']} health modules, including {stats['alb2012_outcome_semantics_financial_oop_candidate_rows']} OOP payment/gift candidates, {stats['alb2012_outcome_semantics_gift_candidate_rows']} gift/payment-scope rows, {stats['alb2012_outcome_semantics_access_candidate_rows']} access rows, and {stats['alb2012_outcome_semantics_service_quality_proxy_rows']} service-quality proxy rows. Outcome-ready, SDG 3.8.2-ready, and climate-linkage-ready rows are {stats['alb2012_outcome_semantics_outcome_ready_rows']}, {stats['alb2012_outcome_semantics_sdg382_ready_rows']}, and {stats['alb2012_outcome_semantics_climate_linkage_ready_rows']}; current decision is `{stats['alb2012_outcome_semantics_current_decision']}`.

ALB_2012 timing/geography exhaustive audit:

{markdown_count_table(alb2012_timing_geo_role_counts, 'ALB_2012 timing/geography candidate role') if alb2012_timing_geo_audit else 'No ALB_2012 timing/geography audit exists yet.'}

{markdown_count_table(alb2012_timing_geo_status_counts, 'ALB_2012 timing/geography status') if alb2012_timing_geo_audit else 'No ALB_2012 timing/geography status rows exist yet.'}

The ALB_2012 timing/geography audit is `report/alb2012_timing_geography_exhaustive_audit.md`; machine-readable outputs are `temp/alb2012_timing_geography_exhaustive_audit.csv` and `result/alb2012_timing_geography_exhaustive_summary.csv`. It scanned {stats['alb2012_timing_geography_source_files_scanned']} raw SPSS files and found {stats['alb2012_timing_geography_audit_rows']} timing/geography keyword rows, but verified interview timing rows, coordinate candidate rows, and climate-linkage-ready rows are all zero. Coarse `prefecture`, `region`, and `urban` fields cover up to {stats['alb2012_coarse_geography_household_rows']} households but remain non-GPS/non-admin climate linkage candidates only.

ALB_2012 questionnaire timing field audit:

{markdown_count_table(alb2012_questionnaire_timing_role_counts, 'ALB_2012 questionnaire timing evidence role') if alb2012_questionnaire_timing_audit else 'No ALB_2012 questionnaire timing audit exists yet.'}

{markdown_count_table(alb2012_questionnaire_timing_promotion_counts, 'ALB_2012 questionnaire timing promotion status') if alb2012_questionnaire_timing_audit else 'No ALB_2012 questionnaire timing promotion rows exist yet.'}

{markdown_count_table(alb2012_questionnaire_raw_gap_role_counts, 'ALB_2012 questionnaire timing raw-gap role') if alb2012_questionnaire_timing_raw_gap else 'No ALB_2012 questionnaire timing raw-gap rows exist yet.'}

The ALB_2012 questionnaire timing field audit is `report/alb2012_questionnaire_timing_field_audit.md`; machine-readable outputs are `temp/alb2012_questionnaire_timing_field_audit.csv`, `temp/alb2012_questionnaire_timing_raw_gap_audit.csv`, and `result/alb2012_questionnaire_timing_field_summary.csv`. It documents {stats['alb2012_questionnaire_timing_field_rows']} questionnaire timing/control cells, including visit rows and date/begin/end/status fields, but verifies {stats['alb2012_questionnaire_timing_raw_verified_interview_timing_rows']} raw household interview timing rows and {stats['alb2012_questionnaire_timing_climate_linkage_ready_rows']} climate-linkage-ready rows. Current decision is `{stats['alb2012_questionnaire_timing_current_decision']}`.

ALB_2012 timing/geography fallback blocker resolution:

| Metric | Value |
|---|---:|
| Blocker rows | {stats['alb2012_timing_geography_blocker_resolution_rows']} |
| Timing rows | {stats['alb2012_timing_geography_blocker_timing_rows']} |
| Geography rows | {stats['alb2012_timing_geography_blocker_geography_rows']} |
| Outcome rows | {stats['alb2012_timing_geography_blocker_outcome_rows']} |
| Promotion-gate rows | {stats['alb2012_timing_geography_blocker_promotion_gate_rows']} |
| Hard-blocked rows | {stats['alb2012_timing_geography_blocker_hard_blocked_rows']} |
| Interview-timing-ready rows | {stats['alb2012_timing_geography_blocker_interview_timing_ready_rows']} |
| Geography-ready rows | {stats['alb2012_timing_geography_blocker_geography_ready_rows']} |
| Outcome-ready rows | {stats['alb2012_timing_geography_blocker_outcome_ready_rows']} |
| Climate-linkage-ready rows | {stats['alb2012_timing_geography_blocker_climate_linkage_ready_rows']} |
| Data-write-ready rows | {stats['alb2012_timing_geography_blocker_data_write_ready_rows']} |
| Decision | {stats['alb2012_timing_geography_blocker_current_decision']} |

{markdown_count_table(alb2012_blocker_family_counts, 'ALB_2012 fallback blocker family') if alb2012_blocker_matrix else 'No ALB_2012 fallback blocker rows exist yet.'}

{markdown_count_table(alb2012_blocker_status_counts, 'ALB_2012 fallback promotion status') if alb2012_blocker_matrix else 'No ALB_2012 fallback promotion-status rows exist yet.'}

The ALB_2012 timing/geography fallback blocker matrix is `report/alb2012_timing_geography_blocker_resolution_matrix.md`; machine-readable outputs are `temp/alb2012_timing_geography_blocker_resolution_matrix.csv` and `result/alb2012_timing_geography_blocker_resolution_summary.csv`. It consolidates raw timing, questionnaire timing, PSU/coarse geography, provisional outcome, raw semantics, and first-analysis promotion evidence. It keeps ALB_2012 fallback promotion closed because verified interview timing, promoted geography, promoted outcomes, climate-linkage-ready rows, and data-write-ready rows are all zero.

Albania legacy questionnaire readability audit:

{markdown_count_table(albania_legacy_questionnaire_wave_counts, 'Legacy questionnaire IDNO') if albania_legacy_questionnaire_audit else 'No legacy questionnaire readability audit exists yet.'}

{markdown_count_table(albania_legacy_questionnaire_read_counts, 'Legacy questionnaire read attempt status') if albania_legacy_questionnaire_audit else 'No legacy questionnaire read-attempt rows exist yet.'}

{markdown_count_table(albania_legacy_questionnaire_promotion_counts, 'Legacy questionnaire promotion status') if albania_legacy_questionnaire_audit else 'No legacy questionnaire promotion rows exist yet.'}

The Albania legacy questionnaire readability audit is `report/albania_legacy_questionnaire_readability_audit.md`; machine-readable outputs are `temp/albania_legacy_questionnaire_readability_audit.csv` and `result/albania_legacy_questionnaire_readability_summary.csv`. It finds {stats['albania_legacy_questionnaire_present_files']} present ALB_2002/2005/2008 legacy `.xls` questionnaire files and {stats['albania_legacy_questionnaire_read_ok_files']} readable files. Timing-content-ready files and climate-linkage-ready rows are {stats['albania_legacy_questionnaire_timing_content_audit_ready_rows']} and {stats['albania_legacy_questionnaire_climate_linkage_ready_rows']}; current decision is `{stats['albania_legacy_questionnaire_current_decision']}`.

Albania legacy questionnaire timing/control field audit:

{markdown_count_table(albania_legacy_questionnaire_timing_role_counts, 'Legacy questionnaire timing evidence role') if albania_legacy_questionnaire_timing_audit else 'No legacy questionnaire timing audit exists yet.'}

{markdown_count_table(albania_legacy_questionnaire_timing_promotion_counts, 'Legacy questionnaire timing promotion status') if albania_legacy_questionnaire_timing_audit else 'No legacy questionnaire timing promotion rows exist yet.'}

{markdown_count_table(albania_legacy_questionnaire_raw_gap_role_counts, 'Legacy questionnaire timing raw-gap role') if albania_legacy_questionnaire_timing_raw_gap else 'No legacy questionnaire timing raw-gap rows exist yet.'}

The Albania legacy questionnaire timing audit is `report/albania_legacy_questionnaire_timing_field_audit.md`; machine-readable outputs are `temp/albania_legacy_questionnaire_timing_field_audit.csv`, `temp/albania_legacy_questionnaire_timing_raw_gap_audit.csv`, and `result/albania_legacy_questionnaire_timing_field_summary.csv`. It documents {stats['albania_legacy_questionnaire_timing_field_rows']} timing/control cells and {stats['albania_legacy_questionnaire_timing_raw_gap_rows']} raw timing-catalog rows. Verified raw household interview timing rows are {stats['albania_legacy_questionnaire_timing_raw_verified_interview_timing_rows']} across the legacy waves, all from ALB_2002 in the current audited state; climate-linkage-ready rows remain {stats['albania_legacy_questionnaire_timing_climate_linkage_ready_rows']}. Current decision is `{stats['albania_legacy_questionnaire_timing_current_decision']}`.

ALB_2005 documented harmonization review:

{markdown_count_table(alb2005_support_counts, 'ALB_2005 documentation support status') if alb2005_documented_evidence else 'No ALB_2005 documented harmonization review exists yet.'}

{markdown_count_table(alb2005_decision_counts, 'ALB_2005 recipe decision') if alb2005_documented_evidence else 'No ALB_2005 recipe-decision rows exist yet.'}

The ALB_2005 review is `report/alb2005_documented_harmonization_review.md`; machine-readable outputs are `temp/alb2005_documented_variable_evidence.csv` and `result/alb2005_documented_harmonization_summary.csv`. It documents plausible future candidates (`weight_retro`, `totcons`, OOP payment items, need/access variables, and district code), rejects `m10_q13a/m10_q13b` as birth-weight false positives, and keeps ALB_2005 not ready for recipe promotion because timing/geography, OOP aggregation/recall, units, skip patterns, and merge keys remain unresolved.

ALB_2005 household core merge audit:

{markdown_count_table(alb2005_core_merge_counts, 'ALB_2005 core merge status') if alb2005_core_merge_audit else 'No ALB_2005 household-core merge audit exists yet.'}

{markdown_count_table(alb2005_core_lineage_counts, 'ALB_2005 core lineage status') if alb2005_core_lineage else 'No ALB_2005 household-core lineage rows exist yet.'}

The ALB_2005 household-core audit is `report/alb2005_household_core_merge_audit.md`; machine-readable outputs are `temp/alb2005_household_core_candidate.csv`, `temp/alb2005_household_core_merge_audit.csv`, `temp/alb2005_household_core_lineage.csv`, and `result/alb2005_household_core_candidate_summary.csv`. The candidate remains in `temp/`, not `data/`: poverty coverage is partial, district geography is partial/no-GPS, survey month is missing, and OOP/access variables are unreviewed.

ALB_2005 provisional outcome feasibility:

{markdown_count_table(alb2005_outcome_family_counts, 'ALB_2005 provisional outcome family') if alb2005_outcome_audit else 'No ALB_2005 provisional outcome feasibility audit exists yet.'}

{markdown_count_table(alb2005_outcome_status_counts, 'ALB_2005 provisional outcome promotion status') if alb2005_outcome_audit else 'No ALB_2005 provisional outcome status rows exist yet.'}

The ALB_2005 provisional outcome audit is `report/alb2005_provisional_outcome_feasibility.md`; machine-readable outputs are `temp/alb2005_provisional_outcome_feasibility_audit.csv` and `result/alb2005_provisional_outcome_feasibility_summary.csv`. It computes raw OOP/access event-rate diagnostics only. It does not construct SDG 3.8.2, final CHE10/CHE25, climate-linked, descriptive, causal, ML, or policy outcomes; promotion-ready rows are {stats['alb2005_provisional_outcome_ready_rows']}.

ALB_2005 raw outcome-semantics value audit:

{markdown_count_table(alb2005_semantics_domain_counts, 'ALB_2005 raw semantics domain') if alb2005_semantics_audit else 'No ALB_2005 raw outcome-semantics audit exists yet.'}

{markdown_count_table(alb2005_semantics_promotion_counts, 'ALB_2005 raw semantics promotion status') if alb2005_semantics_audit else 'No ALB_2005 raw semantics promotion rows exist yet.'}

The ALB_2005 raw outcome-semantics audit is `report/alb2005_outcome_semantics_raw_value_audit.md`; machine-readable outputs are `temp/alb2005_outcome_semantics_raw_value_audit.csv` and `result/alb2005_outcome_semantics_raw_value_summary.csv`. It documents {stats['alb2005_outcome_semantics_raw_value_rows']} raw label/value rows across {stats['alb2005_outcome_semantics_source_files_scanned']} health modules, including {stats['alb2005_outcome_semantics_financial_oop_candidate_rows']} OOP payment/gift candidates, {stats['alb2005_outcome_semantics_gift_candidate_rows']} gift/payment-scope rows, and {stats['alb2005_outcome_semantics_access_candidate_rows']} access rows. Outcome-ready, SDG 3.8.2-ready, and climate-linkage-ready rows are {stats['alb2005_outcome_semantics_outcome_ready_rows']}, {stats['alb2005_outcome_semantics_sdg382_ready_rows']}, and {stats['alb2005_outcome_semantics_climate_linkage_ready_rows']}; current decision is `{stats['alb2005_outcome_semantics_current_decision']}`.

ALB_2005 timing/geography exhaustive audit:

{markdown_count_table(alb2005_timing_geo_role_counts, 'ALB_2005 timing/geography candidate role') if alb2005_timing_geo_audit else 'No ALB_2005 timing/geography audit exists yet.'}

{markdown_count_table(alb2005_timing_geo_status_counts, 'ALB_2005 timing/geography status') if alb2005_timing_geo_audit else 'No ALB_2005 timing/geography status rows exist yet.'}

The ALB_2005 timing/geography audit is `report/alb2005_timing_geography_exhaustive_audit.md`; machine-readable outputs are `temp/alb2005_timing_geography_exhaustive_audit.csv` and `result/alb2005_timing_geography_exhaustive_summary.csv`. It scans raw SPSS files for fieldwork timing, current geography, cluster, and coordinate candidates. It finds no verified interview month/date, no coordinate candidates, and only partial district evidence, so climate-linkage-ready rows are {stats['alb2005_climate_linkage_ready_rows']}.

ALB_2005 timing/geography source-search audit:

{markdown_count_table(alb2005_timing_geo_source_family_counts, 'ALB_2005 timing/geography source-search audit family') if alb2005_timing_geo_source_audit else 'No ALB_2005 timing/geography source-search audit exists yet.'}

{markdown_count_table(alb2005_timing_geo_source_status_counts, 'ALB_2005 timing/geography source-search evidence status') if alb2005_timing_geo_source_audit else 'No ALB_2005 timing/geography source-search evidence rows exist yet.'}

{markdown_count_table(alb2005_timing_geo_source_promotion_counts, 'ALB_2005 timing/geography source-search promotion status') if alb2005_timing_geo_source_audit else 'No ALB_2005 timing/geography source-search promotion rows exist yet.'}

The ALB_2005 timing/geography source-search audit is `report/alb2005_timing_geography_source_search_audit.md`; machine-readable outputs are `temp/alb2005_timing_geography_source_search_audit.csv` and `result/alb2005_timing_geography_source_search_summary.csv`. It scans {stats['alb2005_timing_geography_source_search_local_files_scanned']} local file rows and {stats['alb2005_timing_geography_source_search_local_variables_scanned']} raw-variable rows across {stats['alb2005_timing_geography_source_search_target_concepts']} timing/geography concepts. Raw-schema hits exist for {stats['alb2005_timing_geography_source_search_raw_targets_with_hits']} concepts and questionnaire hits for {stats['alb2005_timing_geography_source_search_questionnaire_targets_with_hits']} concepts, but verified household timing rows are {stats['alb2005_timing_geography_source_search_verified_household_timing_rows']}, coordinate candidate rows are {stats['alb2005_timing_geography_source_search_coordinate_candidate_rows']}, and climate-linkage-ready rows are {stats['alb2005_timing_geography_source_search_climate_linkage_ready_rows']}. Current decision is `{stats['alb2005_timing_geography_source_search_current_decision']}`.

ALB_2005 harmonization value decision audit:

{markdown_count_table(alb2005_value_decision_status_counts, 'ALB_2005 value-decision status') if alb2005_value_decision_audit else 'No ALB_2005 value-decision audit exists yet.'}

{markdown_count_table(alb2005_value_decision_role_counts, 'ALB_2005 value-decision recipe role') if alb2005_value_decision_audit else 'No ALB_2005 value-decision role rows exist yet.'}

{markdown_count_table(alb2005_value_decision_concept_counts, 'ALB_2005 value-decision concept') if alb2005_value_decision_audit else 'No ALB_2005 value-decision concept rows exist yet.'}

The ALB_2005 harmonization value decision audit is `report/alb2005_harmonization_value_decision_audit.md`; machine-readable outputs are `temp/alb2005_harmonization_value_decision_audit.csv` and `result/alb2005_harmonization_value_decision_summary.csv`. It classifies {stats['alb2005_harmonization_value_decision_rows']} ALB_2005 gate rows, keeps recipe-ready rows at {stats['alb2005_harmonization_value_decision_recipe_ready_rows']}, and leaves {stats['alb2005_harmonization_value_decision_required_blocked_rows']} required rows blocked. Current decision is `{stats['alb2005_harmonization_value_decision_current_decision']}`.

ALB_2005 required value/key audit:

{markdown_count_table(alb2005_required_value_key_concept_counts, 'ALB_2005 required value/key concept') if alb2005_required_value_key_audit else 'No ALB_2005 required value/key audit exists yet.'}

{markdown_count_table(alb2005_required_value_key_coverage_counts, 'ALB_2005 required value/key coverage status') if alb2005_required_value_key_audit else 'No ALB_2005 required value/key coverage rows exist yet.'}

{markdown_count_table(alb2005_required_value_key_value_counts, 'ALB_2005 required value/key value status') if alb2005_required_value_key_audit else 'No ALB_2005 required value/key value-status rows exist yet.'}

The ALB_2005 required value/key audit is `report/alb2005_required_value_key_audit.md`; machine-readable outputs are `temp/alb2005_required_value_key_audit.csv` and `result/alb2005_required_value_key_summary.csv`. It reads raw SPSS values for keys, total consumption, food/nonfood components, weights, OOP payment item sums, access-barrier labels, and partial district variables. It finds {stats['alb2005_required_value_key_total_consumption_nonmissing_rows']} nonmissing `totcons` rows, audit-only positive household OOP sums for {stats['alb2005_required_value_key_oop_4w_household_positive_rows']} four-week and {stats['alb2005_required_value_key_oop_12m_household_positive_rows']} twelve-month households, and {stats['alb2005_required_value_key_district_code_nonmissing_rows']} nonmissing partial district-code rows. Recipe-ready, verified interview-timing, coordinate-ready, and climate-linkage-ready rows remain {stats['alb2005_required_value_key_recipe_ready_rows']}, {stats['alb2005_required_value_key_interview_timing_verified_rows']}, {stats['alb2005_required_value_key_coordinate_ready_rows']}, and {stats['alb2005_required_value_key_climate_linkage_ready_rows']}; current decision is `{stats['alb2005_required_value_key_current_decision']}`.

ALB_2005 health questionnaire semantics audit:

{markdown_count_table(alb2005_health_questionnaire_concept_counts, 'ALB_2005 health questionnaire concept') if alb2005_health_questionnaire_audit else 'No ALB_2005 health questionnaire semantics audit exists yet.'}

{markdown_count_table(alb2005_health_questionnaire_status_counts, 'ALB_2005 health questionnaire semantic status') if alb2005_health_questionnaire_audit else 'No ALB_2005 health questionnaire semantic-status rows exist yet.'}

{markdown_count_table(alb2005_health_questionnaire_promotion_counts, 'ALB_2005 health questionnaire promotion status') if alb2005_health_questionnaire_audit else 'No ALB_2005 health questionnaire promotion-status rows exist yet.'}

The ALB_2005 health questionnaire semantics audit is `report/alb2005_health_questionnaire_semantics_audit.md`; machine-readable outputs are `temp/alb2005_health_questionnaire_semantics_audit.csv` and `result/alb2005_health_questionnaire_semantics_summary.csv`. It reads the health questionnaire workbook and SPSS health modules and documents {stats['alb2005_health_questionnaire_oop_item_rows']} OOP payment item rows, {stats['alb2005_health_questionnaire_old_lek_unit_rows']} old-lek unit rows, {stats['alb2005_health_questionnaire_exclusion_note_rows']} provider-charge exclusion-note rows, {stats['alb2005_health_questionnaire_zero_instruction_rows']} zero-payment instruction rows, and {stats['alb2005_health_questionnaire_access_rows']} access/barrier rows. The audit confirms that OOP items are split across {stats['alb2005_health_questionnaire_four_week_oop_rows']} four-week and {stats['alb2005_health_questionnaire_twelve_month_oop_rows']} twelve-month payment rows and that cost, distance, and service-availability barriers appear in the questionnaire. It still promotes zero rows to recipes, outcomes, or climate linkage; current decision is `{stats['alb2005_health_questionnaire_current_decision']}`.

ALB_2005 OOP aggregation policy stress test:

{markdown_count_table(alb2005_oop_policy_recall_counts, 'ALB_2005 OOP policy recall scope') if alb2005_oop_policy_audit else 'No ALB_2005 OOP aggregation policy audit exists yet.'}

{markdown_count_table(alb2005_oop_policy_promotion_counts, 'ALB_2005 OOP policy promotion status') if alb2005_oop_policy_audit else 'No ALB_2005 OOP policy promotion rows exist yet.'}

The ALB_2005 OOP aggregation policy audit is `report/alb2005_oop_aggregation_policy_audit.md`; machine-readable outputs are `temp/alb2005_oop_aggregation_policy_audit.csv` and `result/alb2005_oop_aggregation_policy_summary.csv`. It compares {stats['alb2005_oop_aggregation_policy_rows']} four-week, 12-month, and annualized stress-test OOP aggregation policies over {stats['alb2005_oop_aggregation_policy_total_consumption_rows']} positive total-consumption denominator rows. Outcome-ready, recipe-ready, and climate-linkage-ready rows remain {stats['alb2005_oop_aggregation_policy_outcome_ready_rows']}, {stats['alb2005_oop_aggregation_policy_recipe_ready_rows']}, and {stats['alb2005_oop_aggregation_policy_climate_linkage_ready_rows']}; current decision is `{stats['alb2005_oop_aggregation_policy_current_decision']}`.

ALB_2005 skip/missing semantics audit:

{markdown_count_table(alb2005_skip_missing_family_counts, 'ALB_2005 skip/missing audit family') if alb2005_skip_missing_audit else 'No ALB_2005 skip/missing semantics audit exists yet.'}

{markdown_count_table(alb2005_skip_missing_status_counts, 'ALB_2005 skip/missing evidence status') if alb2005_skip_missing_audit else 'No ALB_2005 skip/missing evidence-status rows exist yet.'}

{markdown_count_table(alb2005_skip_missing_promotion_counts, 'ALB_2005 skip/missing promotion status') if alb2005_skip_missing_audit else 'No ALB_2005 skip/missing promotion rows exist yet.'}

The ALB_2005 skip/missing semantics audit is `report/alb2005_skip_missing_semantics_audit.md`; machine-readable outputs are `temp/alb2005_skip_missing_semantics_audit.csv` and `result/alb2005_skip_missing_semantics_summary.csv`. It audits {stats['alb2005_skip_missing_semantics_rows']} raw trigger/downstream skip rows and finds {stats['alb2005_skip_missing_payment_nonmissing_when_not_triggered_rows']} payment downstream nonmissing rows under negative triggers, {stats['alb2005_skip_missing_condition_nonmissing_when_not_triggered_rows']} conditional reason nonmissing rows under false triggers, and {stats['alb2005_skip_missing_financing_nonmissing_when_not_triggered_rows']} financing-method nonmissing rows under false triggers. It still leaves {stats['alb2005_skip_missing_payment_zero_or_missing_when_triggered_rows']} triggered payment rows with no positive payment for zero/missing-code review and promotes zero recipe, outcome, or climate-linkage rows; current decision is `{stats['alb2005_skip_missing_current_decision']}`.

ALB_2005 consumption/OOP unit-period audit:

{markdown_count_table(alb2005_unit_period_family_counts, 'ALB_2005 unit-period audit family') if alb2005_unit_period_audit else 'No ALB_2005 consumption/OOP unit-period audit exists yet.'}

{markdown_count_table(alb2005_unit_period_status_counts, 'ALB_2005 unit-period evidence status') if alb2005_unit_period_audit else 'No ALB_2005 unit-period evidence-status rows exist yet.'}

{markdown_count_table(alb2005_unit_period_promotion_counts, 'ALB_2005 unit-period promotion status') if alb2005_unit_period_audit else 'No ALB_2005 unit-period promotion rows exist yet.'}

The ALB_2005 consumption/OOP unit-period audit is `report/alb2005_consumption_oop_unit_period_audit.md`; machine-readable outputs are `temp/alb2005_consumption_oop_unit_period_audit.csv` and `result/alb2005_consumption_oop_unit_period_summary.csv`. It documents {stats['alb2005_consumption_oop_unit_period_total_consumption_positive_rows']} positive total-consumption rows, {stats['alb2005_consumption_oop_unit_period_metadata_old_lek_rows']} metadata old-lek aggregate labels, {stats['alb2005_consumption_oop_unit_period_oop_old_lek_rows']} questionnaire OOP old-lek rows, and mixed {stats['alb2005_consumption_oop_unit_period_four_week_oop_rows']} four-week plus {stats['alb2005_consumption_oop_unit_period_twelve_month_oop_rows']} 12-month OOP recall rows. It promotes zero SDG 3.8.2, recipe, outcome, or climate-linkage rows; current decision is `{stats['alb2005_consumption_oop_unit_period_current_decision']}`.

ALB_2005 consumption aggregate metadata crosswalk:

{markdown_count_table(alb2005_aggregate_crosswalk_family_counts, 'ALB_2005 aggregate crosswalk audit family') if alb2005_aggregate_crosswalk_audit else 'No ALB_2005 aggregate metadata crosswalk audit exists yet.'}

{markdown_count_table(alb2005_aggregate_crosswalk_status_counts, 'ALB_2005 aggregate crosswalk readiness status') if alb2005_aggregate_crosswalk_audit else 'No ALB_2005 aggregate crosswalk readiness rows exist yet.'}

{markdown_count_table(alb2005_aggregate_crosswalk_promotion_counts, 'ALB_2005 aggregate crosswalk promotion status') if alb2005_aggregate_crosswalk_audit else 'No ALB_2005 aggregate crosswalk promotion rows exist yet.'}

The ALB_2005 consumption aggregate metadata crosswalk is `report/alb2005_consumption_aggregate_metadata_crosswalk_audit.md`; machine-readable outputs are `temp/alb2005_consumption_aggregate_metadata_crosswalk_audit.csv` and `result/alb2005_consumption_aggregate_metadata_crosswalk_summary.csv`. It checks {stats['alb2005_consumption_aggregate_crosswalk_metadata_rows']} public metadata aggregate/component variables against {stats['alb2005_consumption_aggregate_crosswalk_local_poverty_columns']} local `poverty.sav` columns. Only {stats['alb2005_consumption_aggregate_crosswalk_metadata_present_local_rows']} checked metadata variable is present locally, {stats['alb2005_consumption_aggregate_crosswalk_metadata_absent_local_rows']} are absent, `totcons05` local rows are {stats['alb2005_consumption_aggregate_crosswalk_totcons05_local_rows']}, and formula-reconstructable rows are {stats['alb2005_consumption_aggregate_crosswalk_component_formula_reconstructable_rows']}. It promotes zero SDG 3.8.2, recipe, outcome, or climate-linkage rows; current decision is `{stats['alb2005_consumption_aggregate_crosswalk_current_decision']}`.

ALB_2005 consumption component source-search audit:

{markdown_count_table(alb2005_component_source_family_counts, 'ALB_2005 component source-search audit family') if alb2005_component_source_audit else 'No ALB_2005 component source-search audit exists yet.'}

{markdown_count_table(alb2005_component_source_status_counts, 'ALB_2005 component source-search evidence status') if alb2005_component_source_audit else 'No ALB_2005 component source-search evidence rows exist yet.'}

{markdown_count_table(alb2005_component_source_promotion_counts, 'ALB_2005 component source-search promotion status') if alb2005_component_source_audit else 'No ALB_2005 component source-search promotion rows exist yet.'}

The ALB_2005 consumption component source-search audit is `report/alb2005_consumption_component_source_search_audit.md`; machine-readable outputs are `temp/alb2005_consumption_component_source_search_audit.csv` and `result/alb2005_consumption_component_source_search_summary.csv`. It scans {stats['alb2005_consumption_component_source_search_local_files_scanned']} local ALB_2005 file rows and {stats['alb2005_consumption_component_source_search_local_variables_scanned']} raw-variable rows for {stats['alb2005_consumption_component_source_search_target_variables']} public-metadata aggregate/component targets. Exact local target hits are {stats['alb2005_consumption_component_source_search_exact_target_variables_found']}, exact missing targets are {stats['alb2005_consumption_component_source_search_exact_target_variables_missing']}, local construction-code files are {stats['alb2005_consumption_component_source_search_construction_code_files_found']}, and construction-code target hits are {stats['alb2005_consumption_component_source_search_construction_code_targets_found']}. It promotes zero SDG 3.8.2, recipe, outcome, or climate-linkage rows; current decision is `{stats['alb2005_consumption_component_source_search_current_decision']}`.

ALB_2005 minimum recipe promotion packet:

| Metric | Value |
|---|---:|
| Action rows | {stats['alb2005_minimum_recipe_promotion_action_rows']} |
| Gate rows | {stats['alb2005_minimum_recipe_promotion_gate_rows']} |
| Blocked gates | {stats['alb2005_minimum_recipe_promotion_blocked_gates']} |
| Candidate gates | {stats['alb2005_minimum_recipe_promotion_candidate_gates']} |
| Harmonized-ready rows | {stats['alb2005_minimum_recipe_promotion_harmonized_ready_rows']} |
| Outcome-ready rows | {stats['alb2005_minimum_recipe_promotion_outcome_ready_rows']} |
| Climate-linkage-ready rows | {stats['alb2005_minimum_recipe_promotion_climate_linkage_ready_rows']} |
| Decision | {stats['alb2005_minimum_recipe_promotion_current_decision']} |

{markdown_count_table(alb2005_minimum_recipe_action_status_counts, 'ALB_2005 minimum recipe action blocking status') if alb2005_minimum_recipe_actions else 'No ALB_2005 minimum recipe promotion action rows exist yet.'}

{markdown_count_table(alb2005_minimum_recipe_gate_status_counts, 'ALB_2005 minimum recipe gate status') if alb2005_minimum_recipe_gates else 'No ALB_2005 minimum recipe gate rows exist yet.'}

{markdown_count_table(alb2005_minimum_recipe_required_counts, 'ALB_2005 minimum recipe gate requirement') if alb2005_minimum_recipe_gates else 'No ALB_2005 minimum recipe gate requirement rows exist yet.'}

The ALB_2005 minimum recipe promotion packet is `report/alb2005_minimum_recipe_promotion_packet.md`; machine-readable outputs are `temp/alb2005_minimum_recipe_promotion_action_queue.csv`, `temp/alb2005_minimum_recipe_promotion_gate_checklist.csv`, and `result/alb2005_minimum_recipe_promotion_summary.csv`. It maps the raw-ready temp candidate to household-frame, weight, denominator, OOP, access, timing, geography, outcome, harmonized-dataset, and climate-dataset gates. It is fail-closed: harmonized-ready, outcome-ready, and climate-linkage-ready rows remain {stats['alb2005_minimum_recipe_promotion_harmonized_ready_rows']}, {stats['alb2005_minimum_recipe_promotion_outcome_ready_rows']}, and {stats['alb2005_minimum_recipe_promotion_climate_linkage_ready_rows']}.

ALB_2005 public fieldwork/geography metadata audit:

| Metric | Value |
|---|---:|
| Evidence rows | {stats['alb2005_public_fieldwork_geo_metadata_evidence_rows']} |
| Verified source rows | {stats['alb2005_public_fieldwork_geo_metadata_verified_source_rows']} |
| Source-missing rows | {stats['alb2005_public_fieldwork_geo_metadata_source_missing_rows']} |
| Fieldwork-period evidence rows | {stats['alb2005_public_fieldwork_geo_metadata_fieldwork_period_evidence_rows']} |
| GPS-claim rows | {stats['alb2005_public_fieldwork_geo_metadata_gps_claim_rows']} |
| Sampling-geography rows | {stats['alb2005_public_fieldwork_geo_metadata_sampling_geo_rows']} |
| Household-timing verified rows | {stats['alb2005_public_fieldwork_geo_metadata_household_timing_verified_rows']} |
| Raw coordinate value rows | {stats['alb2005_public_fieldwork_geo_metadata_raw_coordinate_value_rows']} |
| Climate-linkage-ready rows | {stats['alb2005_public_fieldwork_geo_metadata_climate_linkage_ready_rows']} |
| Decision | {stats['alb2005_public_fieldwork_geo_metadata_current_decision']} |

{markdown_count_table(alb2005_public_fieldwork_geo_domain_counts, 'ALB_2005 public metadata evidence domain') if alb2005_public_fieldwork_geo_audit else 'No ALB_2005 public fieldwork/geography metadata rows exist yet.'}

{markdown_count_table(alb2005_public_fieldwork_geo_source_counts, 'ALB_2005 public metadata source status') if alb2005_public_fieldwork_geo_audit else 'No ALB_2005 public metadata source-status rows exist yet.'}

{markdown_count_table(alb2005_public_fieldwork_geo_promotion_counts, 'ALB_2005 public metadata promotion status') if alb2005_public_fieldwork_geo_audit else 'No ALB_2005 public metadata promotion-status rows exist yet.'}

The ALB_2005 public fieldwork/geography metadata audit is `report/alb2005_public_fieldwork_geo_metadata_audit.md`; machine-readable outputs are `temp/alb2005_public_fieldwork_geo_metadata_audit.csv` and `result/alb2005_public_fieldwork_geo_metadata_summary.csv`. It verifies public DDI evidence for the May to early-July 2005 main fieldwork window, October agriculture/community follow-up, sampling geography context, and GPS-collection claims, but it does not verify household-level interview timing or raw coordinate values. Climate-linkage-ready rows remain {stats['alb2005_public_fieldwork_geo_metadata_climate_linkage_ready_rows']}.

ALB_2005 diary timing candidate audit:

| Metric | Value |
|---|---:|
| Candidate rows | {stats['alb2005_diary_timing_candidate_audit_rows']} |
| Metadata-found rows | {stats['alb2005_diary_timing_candidate_metadata_found_rows']} |
| Schema F96 row count | {stats['alb2005_diary_timing_candidate_schema_file_rows']} |
| Raw bookmetadata files present | {stats['alb2005_diary_timing_candidate_raw_bookmetadata_files_present']} |
| Key candidate rows | {stats['alb2005_diary_timing_candidate_key_candidate_rows']} |
| Date candidate rows | {stats['alb2005_diary_timing_candidate_date_candidate_rows']} |
| Household timing promoted rows | {stats['alb2005_diary_timing_candidate_household_timing_promoted_rows']} |
| Climate-linkage-ready rows | {stats['alb2005_diary_timing_candidate_climate_linkage_ready_rows']} |
| Decision | {stats['alb2005_diary_timing_candidate_current_decision']} |

{markdown_count_table(alb2005_diary_timing_role_counts, 'ALB_2005 diary timing concept role') if alb2005_diary_timing_audit else 'No ALB_2005 diary timing candidate rows exist yet.'}

{markdown_count_table(alb2005_diary_timing_catalog_counts, 'ALB_2005 diary timing metadata catalog status') if alb2005_diary_timing_audit else 'No ALB_2005 diary timing catalog-status rows exist yet.'}

{markdown_count_table(alb2005_diary_timing_promotion_counts, 'ALB_2005 diary timing promotion status') if alb2005_diary_timing_audit else 'No ALB_2005 diary timing promotion-status rows exist yet.'}

The ALB_2005 diary timing candidate audit is `report/alb2005_diary_timing_candidate_audit.md`; machine-readable outputs are `temp/alb2005_diary_timing_candidate_audit.csv` and `result/alb2005_diary_timing_candidate_summary.csv`. It records `bookmetadata_cl` PSU/household key candidates and diary beginning/finishing day/month/year variables as useful timing leads, but no raw `bookmetadata_cl` file is present under `temp/raw_downloads` or `temp/raw_extracted`, diary dates are not automatically household interview dates, and no household timing or climate-linkage rows are promoted.

ALB_2005 extracted module coverage audit:

| Metric | Value |
|---|---:|
| DDI modules checked | {stats['alb2005_extracted_module_coverage_ddi_module_rows']} |
| Archive members listed | {stats['alb2005_archive_member_rows']} |
| Archive `.sav` members | {stats['alb2005_archive_sav_member_rows']} |
| Archive questionnaire workbooks | {stats['alb2005_archive_questionnaire_member_rows']} |
| DDI modules present in archive manifest | {stats['alb2005_archive_ddi_module_present_rows']} |
| DDI modules absent from archive manifest | {stats['alb2005_archive_ddi_module_absent_rows']} |
| Critical modules absent from archive manifest | {stats['alb2005_archive_critical_module_absent_rows']} |
| Archive listing status | {stats['alb2005_archive_listing_status']} |
| DDI modules present locally | {stats['alb2005_extracted_module_coverage_present_rows']} |
| DDI modules missing locally | {stats['alb2005_extracted_module_coverage_missing_rows']} |
| Extracted `.sav` files | {stats['alb2005_extracted_module_coverage_extracted_file_rows']} |
| Extra extracted files | {stats['alb2005_extracted_module_coverage_extra_extracted_rows']} |
| `bookmetadata_cl` missing rows | {stats['alb2005_extracted_module_coverage_bookmetadata_missing_rows']} |
| Food diary modules missing | {stats['alb2005_extracted_module_coverage_food_diary_missing_rows']} |
| Critical modules missing | {stats['alb2005_extracted_module_coverage_critical_missing_rows']} |
| Coordinate metadata variables | {stats['alb2005_extracted_module_coverage_coordinate_metadata_variable_rows']} |
| Coordinate extracted files | {stats['alb2005_extracted_module_coverage_coordinate_extracted_file_rows']} |
| Harmonized-ready rows | {stats['alb2005_extracted_module_coverage_harmonized_ready_rows']} |
| Household-timing-ready rows | {stats['alb2005_extracted_module_coverage_household_timing_ready_rows']} |
| Climate-linkage-ready rows | {stats['alb2005_extracted_module_coverage_climate_linkage_ready_rows']} |
| Decision | {stats['alb2005_extracted_module_coverage_current_decision']} |

{markdown_count_table(alb2005_extracted_module_role_counts, 'ALB_2005 extracted module role') if alb2005_extracted_module_audit else 'No ALB_2005 extracted module coverage rows exist yet.'}

{markdown_count_table(alb2005_extracted_module_coverage_counts, 'ALB_2005 extracted module coverage status') if alb2005_extracted_module_audit else 'No ALB_2005 extracted module coverage-status rows exist yet.'}

{markdown_count_table(alb2005_extracted_module_archive_counts, 'ALB_2005 archive coverage status') if alb2005_extracted_module_audit else 'No ALB_2005 archive coverage-status rows exist yet.'}

{markdown_count_table(alb2005_archive_member_ext_counts, 'ALB_2005 archive member extension') if alb2005_archive_member_manifest else 'No ALB_2005 archive member manifest exists yet.'}

{markdown_count_table(alb2005_archive_member_type_counts, 'ALB_2005 archive member type') if alb2005_archive_member_manifest else 'No ALB_2005 archive member-type rows exist yet.'}

{markdown_count_table(alb2005_extracted_extra_counts, 'ALB_2005 extra extracted file status') if alb2005_extracted_extra_audit else 'No ALB_2005 extra extracted files exist yet.'}

The ALB_2005 extracted module coverage audit is `report/alb2005_extracted_module_coverage_audit.md`; machine-readable outputs are `temp/alb2005_extracted_module_coverage_audit.csv`, `temp/alb2005_extracted_extra_files_audit.csv`, `temp/alb2005_archive_member_manifest.csv`, and `result/alb2005_extracted_module_coverage_summary.csv`. It compares 68 DDI/schema modules with 61 local archive members and 44 extracted `.sav` files. The local archive manifest itself lacks 27 DDI modules, including `bookmetadata_cl`, five food-diary modules, and DDI-listed design modules, so these are not just extraction-folder mismatches. It also finds zero coordinate metadata variables and zero coordinate-named extracted files. This is a raw-data gap audit, not a data-promotion step.

ALB_2005 fallback blocker resolution:

| Metric | Value |
|---|---:|
| Blocker rows | {stats['alb2005_fallback_blocker_resolution_rows']} |
| Raw-package rows | {stats['alb2005_fallback_blocker_raw_package_rows']} |
| Timing rows | {stats['alb2005_fallback_blocker_timing_rows']} |
| Geography rows | {stats['alb2005_fallback_blocker_geography_rows']} |
| Outcome rows | {stats['alb2005_fallback_blocker_outcome_rows']} |
| Promotion-gate rows | {stats['alb2005_fallback_blocker_promotion_gate_rows']} |
| Hard-blocked rows | {stats['alb2005_fallback_blocker_hard_blocked_rows']} |
| Harmonized-ready rows | {stats['alb2005_fallback_blocker_harmonized_ready_rows']} |
| Outcome-ready rows | {stats['alb2005_fallback_blocker_outcome_ready_rows']} |
| Interview-timing-ready rows | {stats['alb2005_fallback_blocker_interview_timing_ready_rows']} |
| Geography-ready rows | {stats['alb2005_fallback_blocker_geography_ready_rows']} |
| Climate-linkage-ready rows | {stats['alb2005_fallback_blocker_climate_linkage_ready_rows']} |
| Data-write-ready rows | {stats['alb2005_fallback_blocker_data_write_ready_rows']} |
| Decision | {stats['alb2005_fallback_blocker_current_decision']} |

{markdown_count_table(alb2005_fallback_blocker_family_counts, 'ALB_2005 fallback blocker family') if alb2005_fallback_blocker_matrix else 'No ALB_2005 fallback blocker rows exist yet.'}

{markdown_count_table(alb2005_fallback_blocker_status_counts, 'ALB_2005 fallback promotion status') if alb2005_fallback_blocker_matrix else 'No ALB_2005 fallback promotion-status rows exist yet.'}

The ALB_2005 fallback blocker matrix is `report/alb2005_fallback_blocker_resolution_matrix.md`; machine-readable outputs are `temp/alb2005_fallback_blocker_resolution_matrix.csv` and `result/alb2005_fallback_blocker_resolution_summary.csv`. It consolidates missing `bookmetadata_cl`/food-diary modules, public fieldwork/GPS context, diary-date metadata leads, raw household timing gaps, partial geography, OOP/denominator/access semantics, and first-analysis fallback ranking into one stop rule. It keeps harmonized-ready, outcome-ready, interview-timing-ready, geography-ready, climate-linkage-ready, and data-write-ready rows at zero.

Albania first analysis promotion gate:

| Metric | Value |
|---|---:|
| Waves compared | {stats['albania_first_analysis_promotion_wave_rows']} |
| Gate rows | {stats['albania_first_analysis_promotion_gate_rows']} |
| Action rows | {stats['albania_first_analysis_promotion_action_rows']} |
| Blocked gates | {stats['albania_first_analysis_promotion_blocked_gate_rows']} |
| Ready waves | {stats['albania_first_analysis_promotion_ready_wave_rows']} |
| Harmonized-ready rows | {stats['albania_first_analysis_promotion_harmonized_ready_rows']} |
| Outcome-ready rows | {stats['albania_first_analysis_promotion_outcome_ready_rows']} |
| Climate-linkage-ready rows | {stats['albania_first_analysis_promotion_climate_linkage_ready_rows']} |
| Top-ranked local wave | {stats['albania_first_analysis_promotion_top_ranked_idno']} |
| Top-ranked blocker | {stats['albania_first_analysis_promotion_top_ranked_primary_blocker']} |
| Decision | {stats['albania_first_analysis_promotion_current_decision']} |

{markdown_count_table(albania_first_analysis_gate_counts, 'Albania first-analysis gate status') if albania_first_analysis_gate else 'No Albania first-analysis promotion gate rows exist yet.'}

{markdown_count_table(albania_first_analysis_action_counts, 'Albania first-analysis action status') if albania_first_analysis_actions else 'No Albania first-analysis action rows exist yet.'}

{markdown_count_table(albania_first_analysis_decision_counts, 'Albania first-analysis wave decision') if albania_first_analysis_waves else 'No Albania first-analysis wave-ranking rows exist yet.'}

The Albania first-analysis promotion gate is `report/albania_first_analysis_promotion_gate.md`; machine-readable outputs are `temp/albania_first_analysis_promotion_gate_checklist.csv`, `temp/albania_first_analysis_promotion_action_queue.csv`, `result/albania_first_analysis_promotion_wave_ranking.csv`, and `result/albania_first_analysis_promotion_summary.csv`. It ranks `ALB_2002_LSMS_v01_M` as the nearest local wave, with top blocker `{stats['albania_first_analysis_promotion_top_ranked_primary_blocker']}`, but keeps all waves blocked from `data/` until harmonization, outcome, and climate-linkage gates pass.

Existing Albania raw waves:

{markdown_count_table(albania_wave_schema_counts, 'Existing Albania schema inventory status') if albania_wave_audit else 'No existing Albania raw wave audit exists yet.'}

{markdown_count_table(albania_wave_current_status_counts, 'Existing Albania current status') if albania_wave_audit else 'No existing Albania current-status rows exist yet.'}

{markdown_count_table(albania_wave_promotion_counts, 'Existing Albania promotion status') if albania_wave_audit else 'No existing Albania promotion-status rows exist yet.'}

The existing Albania raw wave audit is `report/albania_existing_raw_wave_audit.md`; machine-readable outputs are `temp/albania_existing_raw_wave_audit.csv` and `result/albania_existing_raw_wave_audit_summary.csv`. It documents four present/extracted Albania LSMS waves. ALB_2002 now has temp household-core, provisional outcome, raw outcome-semantics, period-aligned CHE policy, temp-only CHE candidate outcomes, a joined temp analysis-candidate dataset, district crosswalk, boundary diagnostics, and temp-only climate centroid exposure stress-test rows with observed interview date/month and district fields but no promoted recipe, final outcome, SDG 3.8.2, or climate-linkage promotion. ALB_2005 now has documented, household-core, provisional outcome, raw outcome-semantics, timing/geography, timing/geography source-search, required value/key, health-questionnaire semantics, OOP aggregation policy, skip/missing semantics, consumption/OOP unit-period, aggregate metadata crosswalk, component source-search, minimum recipe promotion gate, public fieldwork/geography metadata, diary timing candidate, extracted-module coverage, and fallback blocker-resolution audits. Public DDI evidence verifies a May to early-July 2005 main fieldwork window, October agriculture/community follow-up, sampling geography context, and GPS-collection claims; the DDI/metadata catalog also exposes `bookmetadata_cl` diary beginning/finishing date candidates. The extracted-module coverage audit confirms the local archive manifest and extracted package are missing `bookmetadata_cl`, five food-diary modules, and coordinate evidence. The ALB_2005 fallback blocker matrix records those timing/geography/source gaps together with unresolved denominator, OOP, access, and first-analysis fallback gates; ALB_2005 remains blocked because diary dates are not accepted household interview dates without raw module/merge/protocol review, household-level interview timing remains unverified, raw coordinate values remain unverified, usable geography is partial/no-GPS, and OOP, total-consumption, old/new lek, annualization, gift/payment, missing-code, and SDG discretionary-budget decisions remain unresolved. ALB_2012 now has raw-core, provisional outcome-feasibility, raw outcome-semantics, timing/geography, and questionnaire timing-field audits; questionnaire control sheets show timing fields, but raw household interview timing is still not verified, and coarse geography, no GPS, OOP/access unit and recall review, gift/payment-scope policy, skip patterns, and service-quality proxy interpretation also remain blocked. ALB_2008 now has household-core, provisional outcome, raw outcome-semantics, timing/geography, and fallback blocker-resolution diagnostics; the matrix consolidates missing interview timing, rejected non-interview timing hits, coarse non-GPS geography, unresolved OOP/access/service-quality semantics, and first-analysis fallback ranking into one fail-closed decision.

ALB_2008 household core merge audit:

{markdown_count_table(alb2008_core_merge_counts, 'ALB_2008 core merge status') if alb2008_core_merge_audit else 'No ALB_2008 household-core merge audit exists yet.'}

{markdown_count_table(alb2008_core_lineage_counts, 'ALB_2008 core lineage status') if alb2008_core_lineage else 'No ALB_2008 household-core lineage rows exist yet.'}

The ALB_2008 household-core audit is `report/alb2008_household_core_merge_audit.md`; machine-readable outputs are `temp/alb2008_household_core_candidate.csv`, `temp/alb2008_household_core_merge_audit.csv`, `temp/alb2008_household_core_lineage.csv`, and `result/alb2008_household_core_candidate_summary.csv`. The candidate remains in `temp/`, not `data/`: timing is missing, area/stratum geography is too coarse for climate linkage, OOP/access variables are unreviewed, and cross-wave comparability is unresolved.

ALB_2008 provisional outcome feasibility:

{markdown_count_table(alb2008_outcome_family_counts, 'ALB_2008 provisional outcome family') if alb2008_outcome_audit else 'No ALB_2008 provisional outcome feasibility audit exists yet.'}

{markdown_count_table(alb2008_outcome_status_counts, 'ALB_2008 provisional outcome promotion status') if alb2008_outcome_audit else 'No ALB_2008 provisional outcome status rows exist yet.'}

The ALB_2008 provisional outcome audit is `report/alb2008_provisional_outcome_feasibility.md`; machine-readable outputs are `temp/alb2008_provisional_outcome_feasibility_audit.csv` and `result/alb2008_provisional_outcome_feasibility_summary.csv`. It computes raw OOP/access event-rate diagnostics only. It does not construct SDG 3.8.2, final CHE10/CHE25, climate-linked, descriptive, causal, ML, or policy outcomes; promotion-ready rows are {stats['alb2008_provisional_outcome_ready_rows']}.

ALB_2008 raw outcome-semantics value audit:

{markdown_count_table(alb2008_semantics_domain_counts, 'ALB_2008 raw semantics domain') if alb2008_semantics_audit else 'No ALB_2008 raw outcome-semantics audit exists yet.'}

{markdown_count_table(alb2008_semantics_promotion_counts, 'ALB_2008 raw semantics promotion status') if alb2008_semantics_audit else 'No ALB_2008 raw semantics promotion rows exist yet.'}

The ALB_2008 raw outcome-semantics audit is `report/alb2008_outcome_semantics_raw_value_audit.md`; machine-readable outputs are `temp/alb2008_outcome_semantics_raw_value_audit.csv` and `result/alb2008_outcome_semantics_raw_value_summary.csv`. It documents {stats['alb2008_outcome_semantics_raw_value_rows']} raw label/value rows across {stats['alb2008_outcome_semantics_source_files_scanned']} health modules, including {stats['alb2008_outcome_semantics_financial_oop_candidate_rows']} OOP payment/gift candidates, {stats['alb2008_outcome_semantics_gift_candidate_rows']} gift/payment-scope rows, {stats['alb2008_outcome_semantics_access_candidate_rows']} access rows, and {stats['alb2008_outcome_semantics_facility_proxy_rows']} facility/service-quality proxy rows. Outcome-ready, SDG 3.8.2-ready, and climate-linkage-ready rows are {stats['alb2008_outcome_semantics_outcome_ready_rows']}, {stats['alb2008_outcome_semantics_sdg382_ready_rows']}, and {stats['alb2008_outcome_semantics_climate_linkage_ready_rows']}; current decision is `{stats['alb2008_outcome_semantics_current_decision']}`.

ALB_2008 timing/geography exhaustive audit:

{markdown_count_table(alb2008_timing_geo_role_counts, 'ALB_2008 timing/geography candidate role') if alb2008_timing_geo_audit else 'No ALB_2008 timing/geography audit exists yet.'}

{markdown_count_table(alb2008_timing_geo_status_counts, 'ALB_2008 timing/geography status') if alb2008_timing_geo_audit else 'No ALB_2008 timing/geography status rows exist yet.'}

The ALB_2008 timing/geography audit is `report/alb2008_timing_geography_exhaustive_audit.md`; machine-readable outputs are `temp/alb2008_timing_geography_exhaustive_audit.csv` and `result/alb2008_timing_geography_exhaustive_summary.csv`. It scans raw SPSS files for fieldwork timing, current geography, cluster, and coordinate candidates. It finds no verified interview month/date and no coordinate candidates; available broad-coverage geography is coarse area/stratum only, so climate-linkage-ready rows are {stats['alb2008_climate_linkage_ready_rows']}.

ALB_2008 fallback blocker resolution:

| Metric | Value |
|---|---:|
| Blocker rows | {stats['alb2008_fallback_blocker_resolution_rows']} |
| Timing rows | {stats['alb2008_fallback_blocker_timing_rows']} |
| Geography rows | {stats['alb2008_fallback_blocker_geography_rows']} |
| Outcome rows | {stats['alb2008_fallback_blocker_outcome_rows']} |
| Promotion-gate rows | {stats['alb2008_fallback_blocker_promotion_gate_rows']} |
| Hard-blocked rows | {stats['alb2008_fallback_blocker_hard_blocked_rows']} |
| Interview-timing-ready rows | {stats['alb2008_fallback_blocker_interview_timing_ready_rows']} |
| Geography-ready rows | {stats['alb2008_fallback_blocker_geography_ready_rows']} |
| Outcome-ready rows | {stats['alb2008_fallback_blocker_outcome_ready_rows']} |
| Climate-linkage-ready rows | {stats['alb2008_fallback_blocker_climate_linkage_ready_rows']} |
| Data-write-ready rows | {stats['alb2008_fallback_blocker_data_write_ready_rows']} |
| Decision | {stats['alb2008_fallback_blocker_current_decision']} |

{markdown_count_table(alb2008_fallback_blocker_family_counts, 'ALB_2008 fallback blocker family') if alb2008_fallback_blocker_matrix else 'No ALB_2008 fallback blocker rows exist yet.'}

{markdown_count_table(alb2008_fallback_blocker_status_counts, 'ALB_2008 fallback promotion status') if alb2008_fallback_blocker_matrix else 'No ALB_2008 fallback promotion-status rows exist yet.'}

The ALB_2008 fallback blocker matrix is `report/alb2008_fallback_blocker_resolution_matrix.md`; machine-readable outputs are `temp/alb2008_fallback_blocker_resolution_matrix.csv` and `result/alb2008_fallback_blocker_resolution_summary.csv`. It consolidates missing household interview timing, timing-like fields rejected as non-interview timing, coarse area/stratum geography, absent GPS/coordinates, provisional outcome limitations, raw OOP/access semantics, and first-analysis fallback ranking into one stop rule. It keeps interview-timing-ready, geography-ready, outcome-ready, climate-linkage-ready, and data-write-ready rows at zero.

First-batch raw verification workbook:

{markdown_count_table(first_batch_dataset_gate_counts, 'First-batch dataset verification gate') if first_batch_dataset_gate else 'No first-batch dataset verification gate exists yet.'}

{markdown_count_table(first_batch_concept_gate_counts, 'First-batch concept gate') if first_batch_concept_template else 'No first-batch concept verification template exists yet.'}

{markdown_count_table(first_batch_variable_status_counts, 'First-batch variable status') if first_batch_variable_template else 'No first-batch variable verification template exists yet.'}

The first-batch raw verification workbook is `report/first_batch_raw_verification_workbook.md`; machine-readable outputs are `result/first_batch_dataset_verification_gate.csv`, `temp/first_batch_concept_verification_template.csv`, `temp/first_batch_variable_verification_template.csv`, and `result/first_batch_raw_verification_workbook_summary.csv`. These are post-download raw-evidence templates and do not verify variables until the blank `fill_*` columns are completed from raw values, labels, units, recall periods, missing codes, and merge keys.

## Raw Ingestion Plan

{markdown_count_table(raw_ingestion_gate_counts, 'Raw ingestion gate status') if raw_ingestion_plan else 'No raw-ingestion plan exists yet.'}

The raw-ingestion plan maps quality-screened datasets to required concepts, candidate modules, and post-download checks. It is a planning artifact only; current raw-verified concept rows: {stats['raw_ingestion_verified_concepts']}. The human-readable plan is `report/raw_ingestion_plan.md`; machine-readable outputs are `temp/raw_ingestion_plan.csv`, `temp/raw_ingestion_concept_checklist.csv`, and `temp/raw_ingestion_module_checklist.csv`.

## Raw Variable Verification Protocol

{markdown_count_table(raw_variable_protocol_status_counts, 'Raw variable verification status') if raw_variable_protocol else 'No raw-variable verification protocol exists yet.'}

{markdown_count_table(raw_variable_protocol_file_counts, 'Raw variable file status') if raw_variable_protocol else 'No raw-variable verification file-status rows exist yet.'}

{markdown_count_table(raw_variable_protocol_concept_counts, 'Raw variable concept') if raw_variable_protocol else 'No raw-variable verification concept rows exist yet.'}

The raw-variable verification protocol is `report/raw_variable_verification_protocol.md`; machine-readable outputs are `temp/raw_variable_verification_protocol.csv`, `temp/harmonization_recipe_scaffold.csv`, and `result/raw_variable_verification_summary.csv`. The scaffold is not a harmonization recipe and cannot be used to build `data/` outputs until raw value, label, unit, recall-period, key, missing-code, and lineage checks pass.

## Harmonization Recipe Gate

{markdown_count_table(harmonization_recipe_gate_counts, 'Recipe gate status') if harmonization_recipe_gate else 'No harmonization recipe gate exists yet.'}

{markdown_count_table(harmonization_recipe_source_counts, 'Recipe source-file status') if harmonization_recipe_gate else 'No source-file gate rows exist yet.'}

{markdown_count_table(harmonization_recipe_variable_counts, 'Recipe raw-variable status') if harmonization_recipe_gate else 'No raw-variable gate rows exist yet.'}

{markdown_count_table(harmonization_recipe_value_counts, 'Recipe value-audit status') if harmonization_recipe_gate else 'No value-audit gate rows exist yet.'}

{markdown_count_table(harmonization_readiness_counts, 'Harmonization readiness status') if harmonization_readiness else 'No harmonization readiness rows exist yet.'}

The harmonization recipe gate is `report/harmonization_recipe_gate.md`; machine-readable outputs are `temp/harmonization_recipe_gate.csv`, `temp/harmonization_value_audit_template.csv`, `temp/harmonization_recipe_verified_candidates.csv`, `result/harmonization_readiness_matrix.csv`, and `result/harmonization_recipe_gate_summary.csv`. It does not write `temp/harmonization_recipe.csv`; verified candidate rows currently present: {stats['harmonization_verified_candidate_rows']}.

## Analysis Dataset Promotion Barriers

{markdown_count_table(analysis_dataset_promotion_blocker_counts, 'Promotion blocker') if analysis_dataset_promotion_audit else 'No analysis dataset promotion barrier audit exists yet.'}

{markdown_count_table(analysis_dataset_promotion_decision_counts, 'Promotion decision') if analysis_dataset_promotion_audit else 'No promotion-decision rows exist yet.'}

The promotion-barrier audit is `report/analysis_dataset_promotion_barriers.md`; machine-readable outputs are `temp/analysis_dataset_promotion_barrier_audit.csv` and `result/analysis_dataset_promotion_barrier_summary.csv`. It reconciles the general harmonization gate, the ALB_2002 top-candidate gate, limited CHE-only outcome promotion, limited climate exposure promotion, limited climate-linked diagnostic promotion, and the current `data/` directory before any analysis-ready linked dataset can be promoted. Current decision: `{stats['analysis_dataset_promotion_current_decision']}`. Promoted rows: {stats['analysis_dataset_promotion_promoted_rows']}; blocked rows: {stats['analysis_dataset_promotion_blocked_rows']}; data files: {stats['analysis_dataset_promotion_data_file_count']}; ALB_2002 temp core rows: {stats['analysis_dataset_promotion_alb2002_temp_core_rows']}; limited harmonized core rows: {stats['analysis_dataset_promotion_limited_harmonized_core_rows']}; limited financial outcome rows: {stats['analysis_dataset_promotion_limited_financial_outcome_rows']}; limited financial CHE10/CHE25 rows: {stats['analysis_dataset_promotion_limited_financial_outcome_che10_rows']}/{stats['analysis_dataset_promotion_limited_financial_outcome_che25_rows']}; limited climate exposure rows: {stats['analysis_dataset_promotion_limited_climate_exposure_rows']}; limited climate-linked rows: {stats['analysis_dataset_promotion_limited_climate_linked_rows']}; limited-core final outcome/climate/analysis-ready rows: {stats['analysis_dataset_promotion_limited_harmonized_core_final_outcome_ready_rows']}/{stats['analysis_dataset_promotion_limited_harmonized_core_climate_linkage_ready_rows']}/{stats['analysis_dataset_promotion_limited_harmonized_core_analysis_ready_rows']}; limited-financial SDG/access/composite/climate/analysis-ready rows: {stats['analysis_dataset_promotion_limited_financial_outcome_sdg382_ready_rows']}/{stats['analysis_dataset_promotion_limited_financial_outcome_access_ready_rows']}/{stats['analysis_dataset_promotion_limited_financial_outcome_composite_ready_rows']}/{stats['analysis_dataset_promotion_limited_financial_outcome_climate_linkage_ready_rows']}/{stats['analysis_dataset_promotion_limited_financial_outcome_analysis_ready_rows']}; limited-exposure linkage/analysis-ready rows: {stats['analysis_dataset_promotion_limited_climate_exposure_climate_linkage_ready_rows']}/{stats['analysis_dataset_promotion_limited_climate_exposure_analysis_ready_rows']}; limited-linked descriptive/predictive/reduced-form/robustness/final-analysis-ready rows: {stats['analysis_dataset_promotion_limited_climate_linked_descriptive_ready_rows']}/{stats['analysis_dataset_promotion_limited_climate_linked_predictive_ml_ready_rows']}/{stats['analysis_dataset_promotion_limited_climate_linked_reduced_form_ready_rows']}/{stats['analysis_dataset_promotion_limited_climate_linked_robustness_ready_rows']}/{stats['analysis_dataset_promotion_limited_climate_linked_analysis_ready_rows']}; ALB_2002 harmonized/outcome/climate-ready rows in the full promotion gate remain {stats['analysis_dataset_promotion_alb2002_harmonized_ready_rows']}/{stats['analysis_dataset_promotion_alb2002_outcome_ready_rows']}/{stats['analysis_dataset_promotion_alb2002_climate_linkage_ready_rows']}.

## Current Design Scorecard Audit

| Metric | Value |
|---|---:|
| Scorecard rows | {stats['design_scorecard_rows']} |
| Current-state rows | {stats['design_scorecard_current_rows']} |
| Current audit rows | {stats['design_scorecard_audit_rows']} |
| No-go threshold rows | {stats['design_no_go_threshold_rows']} |
| Failed/not-estimable thresholds | {stats['design_no_go_failed_or_not_estimable_rows']} |
| Data-write-ready rows | {stats['design_scorecard_data_write_ready_rows']} |
| Decision | {stats['design_scorecard_current_decision']} |

{markdown_count_table(design_scorecard_current_status_counts, 'Current design scorecard audit status') if design_scorecard_current_audit else 'No current design scorecard audit rows exist yet.'}

{markdown_count_table(design_no_go_threshold_status_counts, 'Current design no-go threshold status') if design_no_go_threshold_audit else 'No current design no-go threshold rows exist yet.'}

The current design scorecard audit is `report/design_scorecard_audit.md`; machine-readable outputs are `result/design_scorecard.csv`, `result/design_scorecard_current_audit.csv`, `result/design_no_go_threshold_audit.csv`, and `result/design_scorecard_current_summary.csv`. It appends current-state fail-closed rows to the broad metadata scorecard and keeps estimation, transportable targeting, causal ML, policy learning, and descriptive-paper claims no-go until promoted analytical data, outcome, climate, validation, and placebo evidence exists.

## ALB_2002 Promotion Gate Delta

| Metric | Value |
|---|---:|
| Gate delta rows | {stats['alb2002_promotion_gate_delta_rows']} |
| Review-ready but not promoted rows | {stats['alb2002_promotion_gate_delta_review_ready_rows']} |
| Documented candidate rows | {stats['alb2002_promotion_gate_delta_documented_candidate_rows']} |
| Hard-blocked rows | {stats['alb2002_promotion_gate_delta_hard_blocked_rows']} |
| Promotion-ready rows | {stats['alb2002_promotion_gate_delta_promotion_ready_rows']} |
| Data-write-ready rows | {stats['alb2002_promotion_gate_delta_data_write_ready_rows']} |
| Decision | {stats['alb2002_promotion_gate_delta_decision']} |

{markdown_count_table(alb2002_promotion_gate_delta_status_counts, 'ALB_2002 promotion gate delta status') if alb2002_promotion_gate_delta_audit else 'No ALB_2002 promotion-gate delta rows exist yet.'}

{markdown_count_table(alb2002_promotion_gate_delta_strength_counts, 'ALB_2002 promotion gate evidence strength') if alb2002_promotion_gate_delta_audit else 'No ALB_2002 promotion-gate evidence strength rows exist yet.'}

The ALB_2002 promotion-gate delta audit is `report/alb2002_promotion_gate_delta_audit.md`; machine-readable outputs are `temp/alb2002_promotion_gate_delta_audit.csv` and `result/alb2002_promotion_gate_delta_summary.csv`. It identifies household-frame and interview-timing gates as ready for manual recipe review, documents weight, denominator, OOP, and access candidate evidence, and keeps climate geography, outcome promotion, harmonized dataset promotion, and climate dataset promotion hard-blocked. Data-write-ready rows remain zero.

## ALB_2002 Boundary Blocker Resolution

| Metric | Value |
|---|---:|
| Boundary-source rows | {stats['alb2002_boundary_blocker_resolution_rows']} |
| Official or primary leads | {stats['alb2002_boundary_blocker_official_or_primary_lead_rows']} |
| Complete candidate name-coverage leads | {stats['alb2002_boundary_blocker_candidate_name_coverage_rows']} |
| Incompatible or negative-evidence rows | {stats['alb2002_boundary_blocker_incompatible_or_negative_rows']} |
| Historical 2002-ready rows | {stats['alb2002_boundary_blocker_historical_2002_ready_rows']} |
| Climate-linkage-ready rows | {stats['alb2002_boundary_blocker_climate_linkage_ready_rows']} |
| Data-write-ready rows | {stats['alb2002_boundary_blocker_data_write_ready_rows']} |
| Hard-blocked rows | {stats['alb2002_boundary_blocker_hard_blocked_rows']} |
| Source-action rows | {stats['alb2002_boundary_blocker_required_source_action_rows']} |
| Decision | {stats['alb2002_boundary_blocker_current_decision']} |

{markdown_count_table(alb2002_boundary_blocker_class_counts, 'ALB_2002 boundary blocker class') if alb2002_boundary_blocker_matrix else 'No ALB_2002 boundary blocker rows exist yet.'}

{markdown_count_table(alb2002_boundary_blocker_family_counts, 'ALB_2002 boundary source family') if alb2002_boundary_blocker_matrix else 'No ALB_2002 boundary source-family rows exist yet.'}

The ALB_2002 boundary blocker resolution matrix is `report/alb2002_boundary_blocker_resolution_matrix.md`; machine-readable outputs are `temp/alb2002_boundary_blocker_resolution_matrix.csv` and `result/alb2002_boundary_blocker_resolution_summary.csv`. It consolidates official, public, current-boundary, and negative evidence, identifies three public complete-name-coverage leads that still fail historical-provenance or duplicate-key checks, and keeps promoted climate-linkage rows at zero.

## ALB_2002 Outcome Blocker Resolution

| Metric | Value |
|---|---:|
| Outcome rows | {stats['alb2002_outcome_blocker_resolution_rows']} |
| Financial-protection rows | {stats['alb2002_outcome_blocker_financial_rows']} |
| Access rows | {stats['alb2002_outcome_blocker_access_rows']} |
| Composite UHC/coping rows | {stats['alb2002_outcome_blocker_composite_rows']} |
| Candidate-not-promoted rows | {stats['alb2002_outcome_blocker_candidate_not_promoted_rows']} |
| Low-event candidate rows | {stats['alb2002_outcome_blocker_low_event_candidate_rows']} |
| Hard-blocked rows | {stats['alb2002_outcome_blocker_hard_blocked_rows']} |
| Outcome-ready rows | {stats['alb2002_outcome_blocker_outcome_ready_rows']} |
| SDG 3.8.2-ready rows | {stats['alb2002_outcome_blocker_sdg382_ready_rows']} |
| Climate-linkage-ready rows | {stats['alb2002_outcome_blocker_climate_linkage_ready_rows']} |
| Data-write-ready rows | {stats['alb2002_outcome_blocker_data_write_ready_rows']} |
| Decision | {stats['alb2002_outcome_blocker_current_decision']} |

{markdown_count_table(alb2002_outcome_blocker_family_counts, 'ALB_2002 outcome family') if alb2002_outcome_blocker_matrix else 'No ALB_2002 outcome blocker rows exist yet.'}

{markdown_count_table(alb2002_outcome_blocker_status_counts, 'ALB_2002 outcome promotion status') if alb2002_outcome_blocker_matrix else 'No ALB_2002 outcome promotion-status rows exist yet.'}

The ALB_2002 outcome blocker resolution matrix is `report/alb2002_outcome_blocker_resolution_matrix.md`; machine-readable outputs are `temp/alb2002_outcome_blocker_resolution_matrix.csv` and `result/alb2002_outcome_blocker_resolution_summary.csv`. It consolidates CHE10/CHE25 total-budget candidates, access-barrier candidates, composite UHC candidates, coping candidates, and the hard-blocked SDG 3.8.2 denominator. It keeps final outcome-ready, SDG-ready, climate-linkage-ready, and data-write-ready rows at zero.

## Raw File Inspection

{markdown_count_table(raw_status_counts, 'Raw file status') if raw_files else 'No tabular raw files are currently present in `temp/raw_downloads/`. The raw-inspection script now supports DTA, SAV, POR, SAS7BDAT, XPT, CSV/TSV/TXT, XLS/XLSX, Parquet, Feather, ZIP, and TAR-style archives.'}

## Harmonization

{markdown_count_table(harmonization_status_counts, 'Harmonization status') if harmonization_audit else 'No harmonization audit exists yet.'}

Harmonized household rows currently present: {len(harmonized_household)}. The current output is the scoped ALB_2002 harmonized household core (`report/alb2002_harmonized_household_core_promotion.md`), with {stats['alb2002_harmonized_core_rows']} rows and explicit guardrails that keep final outcome-ready rows at {stats['alb2002_harmonized_core_final_outcome_ready_rows']} and climate-linkage-ready rows at {stats['alb2002_harmonized_core_climate_linkage_ready_rows']}. The general multi-country recipe gate remains separate; the recipe template is `temp/harmonization_recipe_template.csv`.

## Climate Extraction

{climate_status_text}

Climate source endpoint probe:

{climate_source_status_text}

Climate source roles:

{climate_source_role_text}

Climate exposure plan:

{markdown_count_table(climate_exposure_plan_gate_counts, 'Climate linkage gate status') if climate_exposure_plan else 'No climate exposure plan exists yet.'}

Exposure specification status:

{markdown_count_table(climate_exposure_spec_status_counts, 'Climate exposure specification status') if climate_exposure_spec else 'No climate exposure specification exists yet.'}

The climate exposure plan is `report/climate_exposure_plan.md`; machine-readable outputs are `temp/climate_exposure_plan.csv`, `result/climate_exposure_specification.csv`, and `result/climate_exposure_plan_summary.csv`.

Climate exposure rows currently present: {len(climate_exposures)}. The current output is a limited ALB_2002 NASA POWER admin2-centroid fallback exposure file (`report/alb2002_limited_climate_exposure_promotion.md`) with {stats['alb2002_limited_climate_exposure_rows']} rows. It is audited as constructed fallback climate exposure evidence, but linkage-ready rows remain {stats['alb2002_limited_climate_exposure_climate_linkage_ready_rows']} and final-analysis-ready rows remain {stats['alb2002_limited_climate_exposure_final_analysis_ready_rows']} because CHIRPS/ERA5 primary sources, historical baselines, and verified 2001/2002 geography remain unresolved.

Climate-linked rows currently present: {len(climate_linked)}. The current linked output is a limited ALB_2002 CHE10/CHE25 by NASA POWER admin2-centroid diagnostic file (`report/alb2002_limited_climate_linked_promotion.md`) with {stats['alb2002_limited_climate_linked_rows']} household-window rows, {stats['alb2002_limited_climate_linked_household_rows']} households, {stats['alb2002_limited_climate_linked_window_rows']} exposure windows, and {stats['alb2002_limited_climate_linked_unmatched_rows']} unmatched climate rows. Descriptive, predictive, reduced-form, robustness, and final-analysis-ready rows remain {stats['alb2002_limited_climate_linked_descriptive_ready_rows']}/{stats['alb2002_limited_climate_linked_predictive_ml_ready_rows']}/{stats['alb2002_limited_climate_linked_reduced_form_ready_rows']}/{stats['alb2002_limited_climate_linked_robustness_ready_rows']}/{stats['alb2002_limited_climate_linked_final_analysis_ready_rows']}.

Climate validation protocol:

{markdown_count_table(climate_validation_requirement_gate_counts, 'Climate validation requirement gate') if climate_linkage_requirements else 'No climate validation requirement rows exist yet.'}

{markdown_count_table(climate_validation_readiness_counts, 'Climate linkage readiness status') if climate_linkage_readiness else 'No climate linkage readiness rows exist yet.'}

{markdown_count_table(climate_validation_protocol_counts, 'Climate validation check status') if climate_exposure_validation_protocol else 'No climate validation protocol rows exist yet.'}

{markdown_count_table(climate_source_method_status_counts, 'Climate source method status') if climate_source_method_matrix else 'No climate source method rows exist yet.'}

The climate validation protocol is `report/climate_validation_protocol.md`; machine-readable outputs are `temp/climate_linkage_requirements.csv`, `result/climate_source_method_matrix.csv`, `result/climate_exposure_validation_protocol.csv`, `result/climate_linkage_readiness.csv`, and `result/climate_validation_protocol_summary.csv`. It does not construct climate exposures.

Climate merge status:

{markdown_count_table(climate_merge_status_counts, 'Climate merge status') if climate_merge_audit else 'No climate merge audit exists yet.'}

## Outcome Construction

{markdown_count_table(outcome_construct_status_counts, 'Outcome construction status') if outcome_construct_audit else 'No outcome construction audit exists yet.'}

{markdown_count_table(outcome_status_counts, 'Outcome audit status') if outcome_audit else 'No outcome audit rows exist yet.'}

Outcome denominator/readiness plan:

{markdown_count_table(outcome_plan_gate_counts, 'Outcome plan gate status') if outcome_denominator_plan else 'No outcome-denominator plan exists yet.'}

Outcome plan families:

{markdown_count_table(outcome_plan_family_counts, 'Outcome plan family') if outcome_denominator_plan else 'No outcome-plan family rows exist yet.'}

The outcome-denominator plan is `report/outcome_denominator_plan.md`; machine-readable outputs are `temp/outcome_denominator_plan.csv`, `result/outcome_specification_plan.csv`, and `result/outcome_denominator_plan_summary.csv`. These rows are planning gates only and do not indicate constructed outcomes.

SDG 3.8.2 denominator audit:

{markdown_count_table(sdg382_component_gate_counts, 'SDG denominator component gate') if sdg382_denominator_requirements else 'No SDG 3.8.2 denominator requirement rows exist yet.'}

{markdown_count_table(sdg382_readiness_counts, 'SDG denominator readiness status') if sdg382_denominator_readiness else 'No SDG 3.8.2 denominator readiness rows exist yet.'}

{markdown_count_table(sdg382_source_status_counts, 'SDG denominator source status') if sdg382_denominator_sources else 'No SDG 3.8.2 denominator source rows exist yet.'}

The SDG 3.8.2 denominator audit plan is `report/sdg382_denominator_audit_plan.md`; machine-readable outputs are `temp/sdg382_denominator_requirements.csv`, `result/sdg382_denominator_source_matrix.csv`, `result/sdg382_denominator_country_wave_readiness.csv`, and `result/sdg382_denominator_summary.csv`. It does not construct `household_discretionary_budget`.

Validation/reference source readiness:

{markdown_count_table(validation_reference_status_counts, 'Validation reference source status') if validation_reference_probe else 'No validation-reference source probe has been run yet.'}

{markdown_count_table(validation_reference_role_counts, 'Validation reference source role') if validation_reference_probe else 'No validation-reference source roles exist yet.'}

External indicator sample records:

{markdown_count_table(validation_reference_indicator_counts, 'Validation indicator') if validation_reference_samples else 'No validation-reference indicator samples exist yet.'}

HEFPI UHC reference records:

{markdown_count_table(hefpi_uhc_indicator_counts, 'HEFPI UHC indicator') if hefpi_uhc_reference else 'No HEFPI UHC reference extract exists yet.'}

The validation-reference report is `report/validation_reference_sources.md`; machine-readable outputs are `temp/validation_reference_source_probe.csv`, `temp/validation_reference_indicator_sample.csv`, `temp/hefpi_uhc_series_catalog.csv`, and `temp/hefpi_uhc_reference_sample.csv`.

## Descriptive Diagnostics

{markdown_count_table(descriptive_status_counts, 'Descriptive status') if descriptive_audit else 'No descriptive diagnostics audit exists yet.'}

Weighted prevalence rows: {len(descriptive_prevalence)}

Missingness rows: {len(descriptive_missingness)}

## Modeling and Identification

Modeling/identification readiness plan:

{markdown_count_table(modeling_predictive_gate_counts, 'Predictive readiness status') if modeling_identification_plan else 'No modeling-identification plan exists yet.'}

{markdown_count_table(modeling_reduced_form_gate_counts, 'Reduced-form readiness status') if modeling_identification_plan else 'No reduced-form readiness plan exists yet.'}

{markdown_count_table(modeling_causal_ml_gate_counts, 'Causal ML readiness status') if modeling_identification_plan else 'No causal-ML readiness plan exists yet.'}

{markdown_count_table(modeling_policy_gate_counts, 'Policy-learning readiness status') if modeling_identification_plan else 'No policy-learning readiness plan exists yet.'}

The modeling/identification plan is `report/modeling_identification_plan.md`; machine-readable outputs are `temp/modeling_identification_plan.csv`, `result/modeling_validation_plan.csv`, `result/falsification_placebo_plan.csv`, `result/policy_learning_plan.csv`, and `result/modeling_identification_plan_summary.csv`. These rows are planning gates only and do not indicate estimated models.

Mechanism analysis protocol:

{markdown_count_table(mechanism_requirement_gate_counts, 'Mechanism requirement gate status') if mechanism_requirements else 'No mechanism requirement rows exist yet.'}

{markdown_count_table(mechanism_readiness_counts, 'Mechanism readiness status') if mechanism_readiness else 'No mechanism readiness rows exist yet.'}

{markdown_count_table(mechanism_pathway_counts, 'Mechanism pathway') if mechanism_readiness else 'No mechanism pathway rows exist yet.'}

The mechanism analysis protocol is `report/mechanism_analysis_protocol.md`; machine-readable outputs are `temp/mechanism_variable_requirements.csv`, `result/mechanism_pathway_protocol.csv`, `result/mechanism_readiness_matrix.csv`, and `result/mechanism_analysis_protocol_summary.csv`. It does not construct mechanism variables and prohibits using post-shock mediators as main-effect controls.

Empirical readiness dashboard:

{markdown_count_table(empirical_stage_counts, 'Empirical dashboard current stage') if empirical_dashboard else 'No empirical readiness dashboard exists yet.'}

{markdown_count_table(empirical_claim_counts, 'Empirical dashboard allowed claim status') if empirical_dashboard else 'No empirical dashboard claim-status rows exist yet.'}

{markdown_count_table(empirical_no_go_status_counts, 'Empirical go/no-go status') if empirical_no_go else 'No empirical go/no-go threshold rows exist yet.'}

The empirical readiness dashboard is `report/empirical_readiness_dashboard.md`; machine-readable outputs are `result/empirical_readiness_dashboard.csv`, `result/empirical_no_go_threshold_status.csv`, and `result/empirical_readiness_dashboard_summary.csv`. It is a triage artifact only and does not select final countries or relax raw-data gates.

Direct-read audit bundle:

{markdown_count_table(direct_read_section_counts, 'Direct-read bundle section') if direct_read_bundle else 'No direct-read audit bundle exists yet.'}

{markdown_count_table(direct_read_status_counts, 'Direct-read bundle status') if direct_read_bundle else 'No direct-read bundle status rows exist yet.'}

{markdown_count_table(direct_read_manifest_status_counts, 'Direct-read artifact status') if direct_read_manifest else 'No direct-read artifact manifest exists yet.'}

The direct-read audit bundle is `report/direct_read_audit_bundle.md`; machine-readable outputs are `result/direct_read_audit_bundle.csv`, `result/direct_read_artifact_manifest.csv`, and `result/direct_read_audit_bundle_summary.csv`. It is a compact audit index for reviewers/GPT, not an empirical-result file.

Predictive ML audit:

{markdown_count_table(predictive_status_counts, 'Predictive status') if predictive_audit else 'No predictive ML audit exists yet.'}

Reduced-form audit:

{markdown_count_table(causal_model_status_counts, 'Reduced-form status') if causal_model_audit else 'No reduced-form model audit exists yet.'}

Placebo readiness:

{markdown_count_table(placebo_status_counts, 'Placebo-readiness status') if placebo_readiness else 'No placebo-readiness audit exists yet.'}

Causal ML / policy learning:

{markdown_count_table(causal_ml_status_counts, 'Causal ML/policy status') if causal_ml_policy_audit else 'No causal ML/policy audit exists yet.'}

Robustness:

{markdown_count_table(robustness_status_counts, 'Robustness audit status') if robustness_audit else 'No robustness audit exists yet.'}

## Reproducibility Environment

{markdown_count_table(python_package_installed_counts, 'Tracked package import status') if python_package_inventory else 'No Python package inventory exists yet.'}

{markdown_count_table(python_package_level_counts, 'Tracked package requirement level') if python_package_inventory else 'No Python package requirement-level inventory exists yet.'}

{markdown_count_table(python_environment_audit_status_counts, 'Python environment audit status') if python_environment_audit else 'No Python environment audit exists yet.'}

The reproducibility environment report is `report/reproducibility_environment.md`; machine-readable outputs are `temp/python_package_inventory.csv`, `temp/python_package_freeze.txt`, `result/python_environment_audit.csv`, and `result/python_environment_summary.csv`. Missing optional packages are planning gaps; they do not relax the raw-data, outcome, climate-linkage, prediction, or identification gates.

## Objective Traceability

{markdown_count_table(objective_traceability_status_counts, 'Objective requirement status') if objective_traceability else 'No objective traceability audit exists yet.'}

{markdown_count_table(objective_guardrail_status_counts, 'Objective guardrail status') if objective_guardrails else 'No objective guardrail audit exists yet.'}

The objective traceability audit is `report/objective_traceability_audit.md`; machine-readable outputs are `result/objective_requirement_traceability.csv`, `result/objective_guardrail_audit.csv`, and `result/objective_traceability_summary.csv`. This is an evidence map, not a completion claim.

## Variable Mapping

| Map file | Candidate rows |
|---|---:|
{map_table}

All variable-map rows are metadata-only and flagged `metadata_only_requires_raw_verification`.

## Empirical Judgment

Go for remaining raw-data access, raw value/unit/recall-period inspection, merge-key validation, and harmonization recipe promotion. Limited ALB_2002 CHE10/CHE25 financial-protection outcomes are now constructed for inspection.

{predictive_empirical_judgment}

## Immediate Next Steps

1. Start with `report/albania_first_analysis_promotion_gate.md`, then for `ALB_2002_LSMS_v01_M` review `report/alb2002_household_core_merge_audit.md`, `report/alb2002_provisional_outcome_feasibility.md`, `report/alb2002_outcome_semantics_raw_value_audit.md`, `report/alb2002_health_questionnaire_semantics_audit.md`, `report/alb2002_oop_aggregation_policy_audit.md`, `report/alb2002_skip_missing_semantics_audit.md`, `report/alb2002_oop_skip_value_decision_audit.md`, `report/alb2002_access_need_denominator_policy_audit.md`, `report/alb2002_access_candidate_outcome_audit.md`, `report/alb2002_uhc_composite_candidate_audit.md`, `report/alb2002_consumption_sdg_denominator_policy_audit.md`, `report/alb2002_consumption_construction_source_audit.md`, `report/alb2002_consumption_aggregate_metadata_crosswalk_audit.md`, `report/alb2002_period_aligned_che_policy_audit.md`, `report/alb2002_che_candidate_outcome_audit.md`, `report/alb2002_limited_financial_outcome_promotion.md`, `report/alb2002_analysis_candidate_readiness_audit.md`, `report/alb2002_climate_centroid_exposure_audit.md`, `report/alb2002_climate_shock_candidate_audit.md`, `report/alb2002_climate_outcome_linked_candidate_audit.md`, `report/alb2002_linked_candidate_descriptive_diagnostics.md`, `report/alb2002_minimum_recipe_promotion_packet.md`, `report/alb2002_district_climate_crosswalk_audit.md`, `report/alb2002_boundary_name_match_audit.md`, `report/alb2002_boundary_source_alternative_audit.md`, `report/alb2002_boundary_source_resource_search_audit.md`, `report/alb2002_boundary_geometry_provenance_audit.md`, `report/alb2002_boundary_manual_verification_packet.md`, `report/alb2002_boundary_manual_source_followup.md`, `report/alb2002_gadm_boundary_lead_audit.md`, `report/alb2002_local_geography_artifact_audit.md`, `report/albania_legacy_questionnaire_readability_audit.md`, and `report/albania_legacy_questionnaire_timing_field_audit.md`, then manually validate raw OOP/access units, documented total-budget denominator choice, OOP numerator alignment, SPL/PPP/CPI/discretionary-budget inputs, NEW LEKS questionnaire unit evidence, mixed four-week/twelve-month OOP recall, OOP stress-test policy choice, gift/payment-scope policy, the limited CHE outcome guardrails, the temp-only access candidate outcome gate, the temp-only composite UHC candidate gate, the joined analysis-candidate gate, the temp-only climate centroid exposure stress test, the temp-only climate shock diagnostic gate, the temp-only climate/outcome linked candidate gate, the temp-only linked-candidate descriptive screen, the OOP skip-value decision, access/need denominator policy, minimum recipe gates, missing-code semantics, skip patterns, fieldwork documentation, the unmatched KORCE district label, duplicate current-boundary name keys, public source alternatives, the geoBoundaries 2.0.1 name-coverage lead, the 2013 boundary-year metadata blocker, the IHGIS prefecture-only blocker, the GADM 3.6 duplicate SHKODER/provenance blocker, the manual boundary promotion gates, district boundary polygons, boundary vintage/provenance, historical district definitions, raw district-code crosswalks, questionnaire GPS/longitude/latitude fields not present in extracted raw coordinate artifacts, GPS/EA map availability, primary CHIRPS/ERA5 extraction, historical climate baselines, and no-GPS admin aggregation before any SDG/access/composite outcome or climate-linkage promotion.
2. For `ALB_2005_LSMS_v01_M`, review `report/albania_legacy_questionnaire_readability_audit.md`, `report/albania_legacy_questionnaire_timing_field_audit.md`, `report/alb2005_timing_geography_exhaustive_audit.md`, `report/alb2005_timing_geography_source_search_audit.md`, `report/alb2005_public_fieldwork_geo_metadata_audit.md`, `report/alb2005_diary_timing_candidate_audit.md`, `report/alb2005_extracted_module_coverage_audit.md`, `report/alb2005_fallback_blocker_resolution_matrix.md`, `report/alb2005_household_core_merge_audit.md`, `report/alb2005_provisional_outcome_feasibility.md`, `report/alb2005_outcome_semantics_raw_value_audit.md`, `report/alb2005_required_value_key_audit.md`, `report/alb2005_health_questionnaire_semantics_audit.md`, `report/alb2005_oop_aggregation_policy_audit.md`, `report/alb2005_skip_missing_semantics_audit.md`, `report/alb2005_consumption_oop_unit_period_audit.md`, `report/alb2005_consumption_aggregate_metadata_crosswalk_audit.md`, `report/alb2005_consumption_component_source_search_audit.md`, `report/alb2005_minimum_recipe_promotion_packet.md`, `report/alb2005_documented_harmonization_review.md`, `report/alb2005_harmonization_value_decision_audit.md`, and `report/first_batch_raw_value_key_audit.md`, then manually confirm the minimum recipe gates, total-consumption period/price basis, old/new lek handling, `totcons` versus `totcons05` denominator variant choice, why public-metadata formula components are absent from exact local raw-variable evidence, whether an official consumption construction code/note exists outside the local extract, OOP annualization, remaining zero/missing-code semantics, gift/payment-scope policy, SPL/PPP/CPI inputs, merge keys, fieldwork timing, current-location geography, questionnaire/control-form timing leads, raw household timing values, missing `bookmetadata_cl`/food-diary modules, diary beginning/finishing date merge semantics, GPS/coordinate availability, and why public DDI timing/GPS metadata is not yet household-level climate-linkage evidence before any recipe or climate-linkage promotion.
3. For `ALB_2008_LSMS_v01_M`, review `report/albania_legacy_questionnaire_readability_audit.md`, `report/albania_legacy_questionnaire_timing_field_audit.md`, `report/alb2008_household_core_merge_audit.md`, `report/alb2008_provisional_outcome_feasibility.md`, `report/alb2008_outcome_semantics_raw_value_audit.md`, `report/alb2008_timing_geography_exhaustive_audit.md`, and `report/alb2008_fallback_blocker_resolution_matrix.md`, then manually confirm OOP units, recall periods, missing-code semantics, skip patterns, gift/payment-scope policy, service-quality proxy interpretation, fieldwork timing, and a valid admin/GPS crosswalk before adding it to any harmonization or climate-linkage recipe.
4. For `ALB_2012_LSMS_v01_M_v01_A_PUF`, review `report/alb2012_raw_core_feasibility.md`, `report/alb2012_provisional_outcome_feasibility.md`, `report/alb2012_outcome_semantics_raw_value_audit.md`, `report/alb2012_timing_geography_exhaustive_audit.md`, `report/alb2012_questionnaire_timing_field_audit.md`, and `report/alb2012_timing_geography_blocker_resolution_matrix.md`, then link questionnaire timing fields to raw household interview date/month values or official fieldwork-period metadata, validate survey-design semantics, and manually review OOP/access units, recall periods, missing codes, skip patterns, gift/payment-scope policy, service-quality proxy interpretation, and coarse geography before adding it to any harmonization or climate-linkage recipe.
5. Complete the remaining manual-download items in `temp/manual_download_manifest.csv` and place original raw archives/files in `temp/raw_downloads/`.
6. After adding raw files, run `python script/03_inspect_raw_schemas.py`, `python script/45_audit_first_batch_raw_value_keys.py`, and `python script/33_build_harmonization_recipe_gate.py`.
7. Confirm whether at least six countries have verified total consumption/income, OOP health expenditure, usable geography, and survey timing.
8. Build harmonized analytical data only from verified recipe rows, then run `script/06_extract_climate.py` and `script/07_merge_microdata_climate.py`; do not estimate models until the merge and outcome audits pass.
"""
    (REPORT_DIR / "final_report.md").write_text(final_report, encoding="utf-8")

    append_log(TEMP_DIR / "audit_log.md", "Wrote evidence-based reports and completion criteria audit.")
    print("Wrote evidence-based reports and result/completion_criteria_audit.csv")


if __name__ == "__main__":
    main()
