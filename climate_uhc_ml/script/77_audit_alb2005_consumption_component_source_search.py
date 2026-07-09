from __future__ import annotations

import csv
import math
from pathlib import Path
from typing import Any

import pandas as pd

from common import REPORT_DIR, RESULT_DIR, TEMP_DIR, append_log, ensure_dirs, write_csv


IDNO = "ALB_2005_LSMS_v01_M"
COUNTRY = "Albania"
SURVEY_NAME = "Living Standards Measurement Survey 2005"
WAVE = "2005"

RAW_ROOT = TEMP_DIR / "raw_extracted" / "lsms2005en_1e7f1965c4a5" / "lsms2005en"
DATA_ROOT = RAW_ROOT / "Data_2005"
QUESTIONNAIRE_ROOT = RAW_ROOT / "Questionnaire 2005"

RAW_VARIABLE_CATALOG = TEMP_DIR / "raw_schema_inventory" / "raw_variable_catalog.csv"
RAW_FILE_INVENTORY = TEMP_DIR / "raw_schema_inventory" / "raw_file_inventory.csv"
METADATA_VARIABLE_CATALOG = TEMP_DIR / "raw_schema_inventory" / "metadata_variable_catalog.csv"
CROSSWALK_SUMMARY_PATH = RESULT_DIR / "alb2005_consumption_aggregate_metadata_crosswalk_summary.csv"

AUDIT_PATH = TEMP_DIR / "alb2005_consumption_component_source_search_audit.csv"
SUMMARY_PATH = RESULT_DIR / "alb2005_consumption_component_source_search_summary.csv"
REPORT_PATH = REPORT_DIR / "alb2005_consumption_component_source_search_audit.md"

DECISION = "blocked_alb2005_consumption_component_source_search_not_ready"
NO_PROMOTION = "not_promoted_component_source_search_audit_only"

TARGETS = {
    "food": {
        "phrases": ["total food consumption", "food consumption"],
        "file_hints": ["food"],
    },
    "edu": {
        "phrases": ["total education expenditures", "education expenditure"],
        "file_hints": ["education"],
    },
    "durcons": {
        "phrases": ["total durable consumption", "durable consumption", "durable"],
        "file_hints": ["dwelling", "non_food"],
    },
    "nfoodc": {
        "phrases": ["total non-food consumption component", "non-food consumption component", "non food consumption"],
        "file_hints": ["non_food"],
    },
    "nfood05": {
        "phrases": ["total non-food consumption", "maintenance and repair", "non-food consumption"],
        "file_hints": ["non_food"],
    },
    "totutil": {
        "phrases": ["total utilities", "utilities", "computer usage"],
        "file_hints": ["dwelling"],
    },
    "totutil05": {
        "phrases": ["total utilities", "utilities", "computer usage"],
        "file_hints": ["dwelling"],
    },
    "totcons": {
        "phrases": ["total consumption", "household total consumption"],
        "file_hints": ["poverty"],
    },
    "totcons05": {
        "phrases": ["total consumption", "nfood05"],
        "file_hints": ["poverty"],
    },
}

CODE_SUFFIXES = {".do", ".sps", ".spss", ".syntax", ".sas", ".R", ".r", ".py", ".txt"}

AUDIT_COLUMNS = [
    "country",
    "survey_name",
    "wave",
    "idno",
    "audit_family",
    "evidence_item",
    "target_variable",
    "public_metadata_label",
    "source_scope",
    "source_artifact",
    "local_files_scanned",
    "local_variables_scanned",
    "exact_variable_hit_count",
    "label_phrase_hit_count",
    "questionnaire_phrase_hit_count",
    "candidate_module_file_count",
    "construction_code_file_count",
    "evidence_detail",
    "evidence_status",
    "ready_for_recipe",
    "ready_for_outcome",
    "sdg382_ready",
    "climate_linkage_ready",
    "promotion_status",
    "blocking_reason",
    "next_action",
]

SUMMARY_COLUMNS = ["metric", "value", "interpretation"]


def read_csv_dicts(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        return []
    with path.open(encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def fmt(value: Any) -> str:
    if value is None:
        return ""
    try:
        if pd.isna(value):
            return ""
    except TypeError:
        pass
    if isinstance(value, float):
        if not math.isfinite(value):
            return ""
        if value.is_integer():
            return str(int(value))
        return f"{value:.6g}"
    return str(value)


def clean_text(value: Any) -> str:
    if value is None:
        return ""
    try:
        if pd.isna(value):
            return ""
    except TypeError:
        pass
    return " ".join(str(value).split()).encode("ascii", "replace").decode("ascii")


def compact_join(values: list[Any], limit: int = 8) -> str:
    out: list[str] = []
    seen: set[str] = set()
    for value in values:
        text = clean_text(value)
        if not text or text in seen:
            continue
        out.append(text)
        seen.add(text)
        if len(out) >= limit:
            break
    return "; ".join(out)


def metadata_variable_name(row: dict[str, str]) -> str:
    return row.get("variable_name") or row.get("name") or ""


def metadata_variable_label(row: dict[str, str]) -> str:
    return row.get("variable_label") or row.get("labl") or ""


def metadata_rows_by_variable() -> dict[str, dict[str, str]]:
    out: dict[str, dict[str, str]] = {}
    for row in read_csv_dicts(METADATA_VARIABLE_CATALOG):
        if row.get("idno") != IDNO:
            continue
        if (row.get("file_name") or "").lower() != "poverty":
            continue
        name = metadata_variable_name(row).lower()
        if name:
            out[name] = row
    return out


def is_alb2005_path(value: str) -> bool:
    return "lsms2005en_1e7f1965c4a5" in value.replace("/", "\\")


def local_raw_variable_rows() -> list[dict[str, str]]:
    return [row for row in read_csv_dicts(RAW_VARIABLE_CATALOG) if is_alb2005_path(row.get("source_path", ""))]


def local_raw_file_rows() -> list[dict[str, str]]:
    return [row for row in read_csv_dicts(RAW_FILE_INVENTORY) if is_alb2005_path(row.get("source_path", ""))]


def label_contains_any(row: dict[str, str], phrases: list[str]) -> bool:
    text = f"{row.get('variable_name', '')} {row.get('variable_label', '')}".lower().replace("_", " ")
    return any(phrase.lower().replace("_", " ") in text for phrase in phrases)


def source_path_name(row: dict[str, str]) -> str:
    return Path(row.get("source_path", "")).name


def file_hint_match(row: dict[str, str], hints: list[str]) -> bool:
    text = source_path_name(row).lower().replace("-", "_")
    return any(hint.lower().replace("-", "_") in text for hint in hints)


def scan_questionnaire_workbooks() -> dict[str, list[str]]:
    hits = {target: [] for target in TARGETS}
    for workbook_path in sorted(QUESTIONNAIRE_ROOT.glob("*.xls")):
        try:
            workbook = pd.ExcelFile(workbook_path)
        except Exception:
            continue
        for sheet_name in workbook.sheet_names:
            try:
                df = pd.read_excel(workbook, sheet_name=sheet_name, header=None, dtype=object)
            except Exception:
                continue
            for row_index, row in df.iterrows():
                text = clean_text(" ".join(clean_text(value) for value in row.tolist()))
                low = text.lower().replace("_", " ")
                if not low:
                    continue
                for target, spec in TARGETS.items():
                    if any(phrase.lower().replace("_", " ") in low for phrase in spec["phrases"]):
                        hits[target].append(f"{workbook_path.name}:{sheet_name}:row{row_index + 1}: {text[:160]}")
    return hits


def construction_code_files() -> list[Path]:
    if not RAW_ROOT.exists():
        return []
    return sorted(path for path in RAW_ROOT.rglob("*") if path.is_file() and path.suffix in CODE_SUFFIXES)


def target_code_hits(files: list[Path], target: str, phrases: list[str]) -> list[str]:
    hits: list[str] = []
    needles = [target.lower(), *[phrase.lower() for phrase in phrases]]
    for path in files:
        try:
            text = path.read_text(encoding="utf-8", errors="ignore").lower()
        except Exception:
            continue
        if any(needle in text for needle in needles):
            try:
                rel = path.relative_to(TEMP_DIR.parent)
            except ValueError:
                rel = path
            hits.append(str(rel).replace("\\", "/"))
    return hits


def base_row(audit_family: str, evidence_item: str, target_variable: str, metadata_label: str) -> dict[str, str]:
    return {
        "country": COUNTRY,
        "survey_name": SURVEY_NAME,
        "wave": WAVE,
        "idno": IDNO,
        "audit_family": audit_family,
        "evidence_item": evidence_item,
        "target_variable": target_variable,
        "public_metadata_label": metadata_label,
        "source_scope": "",
        "source_artifact": "",
        "local_files_scanned": "0",
        "local_variables_scanned": "0",
        "exact_variable_hit_count": "0",
        "label_phrase_hit_count": "0",
        "questionnaire_phrase_hit_count": "0",
        "candidate_module_file_count": "0",
        "construction_code_file_count": "0",
        "evidence_detail": "",
        "evidence_status": "blocked_not_run",
        "ready_for_recipe": "0",
        "ready_for_outcome": "0",
        "sdg382_ready": "0",
        "climate_linkage_ready": "0",
        "promotion_status": NO_PROMOTION,
        "blocking_reason": (
            "Audit-only source search. It does not verify official aggregate construction code, final period, price basis, "
            "PPP/SPL/CPI treatment, OOP annualization, household timing, or climate-ready geography."
        ),
        "next_action": (
            "Use this search output to target manual documentation review before any ALB_2005 denominator recipe, "
            "CHE, SDG 3.8.2, or climate-linked outcome promotion."
        ),
    }


def build_rows() -> tuple[list[dict[str, str]], dict[str, Any]]:
    metadata = metadata_rows_by_variable()
    raw_variables = local_raw_variable_rows()
    raw_files = local_raw_file_rows()
    questionnaire_hits = scan_questionnaire_workbooks()
    code_files = construction_code_files()
    crosswalk_summary = read_csv_dicts(CROSSWALK_SUMMARY_PATH)

    rows: list[dict[str, str]] = []
    exact_targets_found = 0
    label_targets_found = 0
    questionnaire_targets_found = 0
    code_targets_found = 0

    for target, spec in TARGETS.items():
        metadata_label = clean_text(metadata_variable_label(metadata.get(target, {})))
        exact_hits = [row for row in raw_variables if row.get("variable_name", "").lower() == target]
        label_hits = [row for row in raw_variables if label_contains_any(row, spec["phrases"])]
        candidate_files = [row for row in raw_files if file_hint_match(row, spec["file_hints"])]
        q_hits = questionnaire_hits.get(target, [])
        c_hits = target_code_hits(code_files, target, spec["phrases"])
        exact_targets_found += int(bool(exact_hits))
        label_targets_found += int(bool(label_hits))
        questionnaire_targets_found += int(bool(q_hits))
        code_targets_found += int(bool(c_hits))

        row = base_row("schema_exact_variable_search", "exact_target_variable_search", target, metadata_label)
        row.update(
            {
                "source_scope": "local raw-variable catalog",
                "source_artifact": "temp/raw_schema_inventory/raw_variable_catalog.csv",
                "local_files_scanned": str(len(raw_files)),
                "local_variables_scanned": str(len(raw_variables)),
                "exact_variable_hit_count": str(len(exact_hits)),
                "label_phrase_hit_count": str(len(label_hits)),
                "questionnaire_phrase_hit_count": str(len(q_hits)),
                "candidate_module_file_count": str(len(candidate_files)),
                "construction_code_file_count": str(len(c_hits)),
                "evidence_detail": compact_join(
                    [f"{Path(row.get('source_path', '')).name}:{row.get('variable_name', '')}:{row.get('variable_label', '')}" for row in exact_hits],
                    6,
                )
                or "No exact local raw variable hit.",
                "evidence_status": "exact_local_raw_variable_seen" if exact_hits else "exact_local_raw_variable_not_found",
                "blocking_reason": (
                    "The exact target exists locally, but this source search alone does not prove the official aggregate construction recipe or denominator variant."
                    if exact_hits
                    else "The exact public-metadata aggregate/component variable is absent from the local raw-variable catalog."
                ),
                "next_action": (
                    "Confirm whether this local variable is the intended denominator and locate the official construction note/code."
                    if exact_hits
                    else "Locate official aggregate construction documentation or a different raw package version containing this component."
                ),
            }
        )
        rows.append(row)

        row = base_row("schema_label_phrase_search", "label_or_phrase_search", target, metadata_label)
        row.update(
            {
                "source_scope": "local raw-variable catalog labels",
                "source_artifact": "temp/raw_schema_inventory/raw_variable_catalog.csv",
                "local_files_scanned": str(len(raw_files)),
                "local_variables_scanned": str(len(raw_variables)),
                "exact_variable_hit_count": str(len(exact_hits)),
                "label_phrase_hit_count": str(len(label_hits)),
                "questionnaire_phrase_hit_count": str(len(q_hits)),
                "candidate_module_file_count": str(len(candidate_files)),
                "construction_code_file_count": str(len(c_hits)),
                "evidence_detail": compact_join(
                    [f"{Path(row.get('source_path', '')).name}:{row.get('variable_name', '')}:{row.get('variable_label', '')}" for row in label_hits],
                    8,
                )
                or "No local label/phrase hit for the target aggregate concept.",
                "evidence_status": "local_label_phrase_hit_seen_not_recipe" if label_hits else "local_label_phrase_hit_not_found",
                "blocking_reason": (
                    "A local label/phrase hit exists, but label text is not an official aggregate construction recipe."
                    if label_hits
                    else "No local raw-variable label provides an equivalent aggregate/component source for this target."
                ),
                "next_action": "Use label hits only as search leads; do not promote outcomes until the official construction recipe is verified.",
            }
        )
        rows.append(row)

        row = base_row("questionnaire_and_module_search", "questionnaire_phrase_and_module_file_search", target, metadata_label)
        row.update(
            {
                "source_scope": "local questionnaires and module file names",
                "source_artifact": "Questionnaire 2005/*.xls; temp/raw_schema_inventory/raw_file_inventory.csv",
                "local_files_scanned": str(len(raw_files)),
                "local_variables_scanned": str(len(raw_variables)),
                "exact_variable_hit_count": str(len(exact_hits)),
                "label_phrase_hit_count": str(len(label_hits)),
                "questionnaire_phrase_hit_count": str(len(q_hits)),
                "candidate_module_file_count": str(len(candidate_files)),
                "construction_code_file_count": str(len(c_hits)),
                "evidence_detail": compact_join(
                    [f"module={source_path_name(row)}" for row in candidate_files] + q_hits,
                    10,
                )
                or "No questionnaire phrase or module-name lead found.",
                "evidence_status": "item_module_or_questionnaire_lead_seen_not_aggregate_recipe" if candidate_files or q_hits else "no_item_module_or_questionnaire_lead_seen",
                "blocking_reason": (
                    "Local modules/questionnaire text may identify item-level source material, but this does not prove the final aggregate formula, period, or price basis."
                    if candidate_files or q_hits
                    else "No local questionnaire/module lead was found for this component; it remains unsupported locally."
                ),
                "next_action": "Review candidate modules and official aggregate documentation manually before reconstructing or validating total consumption.",
            }
        )
        rows.append(row)

        row = base_row("construction_code_search", "local_construction_code_search", target, metadata_label)
        row.update(
            {
                "source_scope": "local extracted source-code-like files",
                "source_artifact": "temp/raw_extracted/lsms2005en_1e7f1965c4a5/lsms2005en",
                "local_files_scanned": str(len(raw_files)),
                "local_variables_scanned": str(len(raw_variables)),
                "exact_variable_hit_count": str(len(exact_hits)),
                "label_phrase_hit_count": str(len(label_hits)),
                "questionnaire_phrase_hit_count": str(len(q_hits)),
                "candidate_module_file_count": str(len(candidate_files)),
                "construction_code_file_count": str(len(c_hits)),
                "evidence_detail": compact_join(c_hits, 8) or f"source-code-like files found={len(code_files)}; no target construction-code hit.",
                "evidence_status": "construction_code_hit_seen_manual_review_required" if c_hits else "construction_code_hit_not_found",
                "blocking_reason": (
                    "A code-like file contains target text but still needs manual review before recipe promotion."
                    if c_hits
                    else "No local construction-code hit was found for this target, so the aggregate formula is not reproducible from local extracted source code."
                ),
                "next_action": "Obtain or locate the official consumption aggregate construction code/note before outcome promotion.",
            }
        )
        rows.append(row)

    rows.append(
        {
            **base_row("upstream_crosscheck", "aggregate_crosswalk_fail_closed_status", "all_targets", "crosswalk summary"),
            "source_scope": "upstream aggregate metadata crosswalk",
            "source_artifact": "result/alb2005_consumption_aggregate_metadata_crosswalk_summary.csv",
            "local_files_scanned": str(len(raw_files)),
            "local_variables_scanned": str(len(raw_variables)),
            "evidence_detail": (
                f"crosswalk_decision={next((row.get('value', '') for row in crosswalk_summary if row.get('metric') == 'alb2005_consumption_aggregate_crosswalk_current_decision'), 'missing')}; "
                f"metadata_absent_local={next((row.get('value', '0') for row in crosswalk_summary if row.get('metric') == 'alb2005_consumption_aggregate_crosswalk_metadata_variables_absent_from_local_raw_rows'), '0')}"
            ),
            "evidence_status": "upstream_aggregate_crosswalk_remains_fail_closed",
            "blocking_reason": "The upstream aggregate metadata crosswalk keeps SDG, recipe, outcome, and climate-linkage promotion blocked.",
            "next_action": "Use this wider source search plus the crosswalk to target manual documentation and package-version review.",
        }
    )

    diagnostics = {
        "target_variables": len(TARGETS),
        "local_files_scanned": len(raw_files),
        "local_variables_scanned": len(raw_variables),
        "questionnaire_workbooks_scanned": len(list(QUESTIONNAIRE_ROOT.glob("*.xls"))) if QUESTIONNAIRE_ROOT.exists() else 0,
        "construction_code_files_found": len(code_files),
        "exact_targets_found": exact_targets_found,
        "exact_targets_missing": len(TARGETS) - exact_targets_found,
        "label_phrase_targets_found": label_targets_found,
        "questionnaire_phrase_targets_found": questionnaire_targets_found,
        "construction_code_targets_found": code_targets_found,
        "candidate_module_target_rows": sum(1 for target, spec in TARGETS.items() if any(file_hint_match(row, spec["file_hints"]) for row in raw_files)),
    }
    return rows, diagnostics


def summary_row(metric: str, value: Any, interpretation: str) -> dict[str, str]:
    return {"metric": metric, "value": fmt(value), "interpretation": interpretation}


def build_summary(rows: list[dict[str, str]], diagnostics: dict[str, Any]) -> list[dict[str, str]]:
    return [
        summary_row("alb2005_consumption_component_source_search_rows", len(rows), "Rows in the ALB_2005 consumption component source-search audit."),
        summary_row("alb2005_consumption_component_source_search_target_variables", diagnostics["target_variables"], "Public metadata aggregate/component variables searched locally."),
        summary_row("alb2005_consumption_component_source_search_local_files_scanned", diagnostics["local_files_scanned"], "Local ALB_2005 raw/schema file rows scanned."),
        summary_row("alb2005_consumption_component_source_search_local_variables_scanned", diagnostics["local_variables_scanned"], "Local ALB_2005 raw-variable rows scanned."),
        summary_row("alb2005_consumption_component_source_search_questionnaire_workbooks_scanned", diagnostics["questionnaire_workbooks_scanned"], "Local ALB_2005 questionnaire workbooks scanned for phrase leads."),
        summary_row("alb2005_consumption_component_source_search_construction_code_files_found", diagnostics["construction_code_files_found"], "Local source-code-like files found under the ALB_2005 extract."),
        summary_row("alb2005_consumption_component_source_search_exact_target_variables_found", diagnostics["exact_targets_found"], "Target variables with exact local raw-variable hits."),
        summary_row("alb2005_consumption_component_source_search_exact_target_variables_missing", diagnostics["exact_targets_missing"], "Target variables without exact local raw-variable hits."),
        summary_row("alb2005_consumption_component_source_search_label_phrase_targets_found", diagnostics["label_phrase_targets_found"], "Target variables with local raw-label/phrase hits."),
        summary_row("alb2005_consumption_component_source_search_questionnaire_phrase_targets_found", diagnostics["questionnaire_phrase_targets_found"], "Target variables with questionnaire phrase leads."),
        summary_row("alb2005_consumption_component_source_search_construction_code_targets_found", diagnostics["construction_code_targets_found"], "Target variables with local construction-code text hits."),
        summary_row("alb2005_consumption_component_source_search_candidate_module_target_rows", diagnostics["candidate_module_target_rows"], "Target variables with module-name leads only."),
        summary_row("alb2005_consumption_component_source_search_recipe_ready_rows", 0, "Rows promoted to a harmonization recipe by this audit; intentionally zero."),
        summary_row("alb2005_consumption_component_source_search_outcome_ready_rows", 0, "Rows promoted to outcome construction by this audit; intentionally zero."),
        summary_row("alb2005_consumption_component_source_search_sdg382_ready_rows", 0, "Rows promoted to SDG 3.8.2 denominator readiness by this audit; intentionally zero."),
        summary_row("alb2005_consumption_component_source_search_climate_linkage_ready_rows", 0, "Rows promoted to climate linkage by this audit; intentionally zero."),
        summary_row("alb2005_consumption_component_source_search_current_decision", DECISION, "Current fail-closed decision for the ALB_2005 component source-search evidence."),
    ]


def markdown_rows(rows: list[dict[str, str]], columns: list[str], limit: int = 40) -> str:
    lines = ["| " + " | ".join(columns) + " |", "|" + "|".join("---" for _ in columns) + "|"]
    for row in rows[:limit]:
        values = []
        for column in columns:
            value = (row.get(column, "") or "").replace("|", "/")
            if len(value) > 140:
                value = value[:137] + "..."
            values.append(value)
        lines.append("| " + " | ".join(values) + " |")
    return "\n".join(lines)


def write_report(rows: list[dict[str, str]], summary: list[dict[str, str]]) -> None:
    summary_table = "\n".join(f"| {row['metric']} | {row['value']} | {row['interpretation']} |" for row in summary)
    report = f"""# ALB_2005 Consumption Component Source Search Audit

Status: fail-closed local source search. This audit searches local ALB_2005 raw-variable metadata, file inventory, questionnaire workbooks, and source-code-like files for the public-metadata consumption aggregate/component variables. It does not write `data/`, does not reconstruct consumption, does not construct CHE/SDG outcomes, and does not promote any row to harmonization, outcome construction, SDG 3.8.2, or climate linkage.

## Bottom Line

- The exact local raw-variable search finds only the already-known `totcons` target from the checked public metadata aggregate/component set.
- The missing public-metadata components and `totcons05` are still not found as exact local raw variables.
- Local module names and questionnaire text provide item-level leads for manual review, but no local construction-code hit proves the final aggregate formula, period, or price basis.
- SDG 3.8.2, recipe-ready, outcome-ready, and climate-linkage-ready rows from this audit: 0.
- Current decision: `{DECISION}`.

## Summary

| Metric | Value | Interpretation |
|---|---:|---|
{summary_table}

## Source Search Rows

{markdown_rows(rows, ['audit_family', 'target_variable', 'exact_variable_hit_count', 'label_phrase_hit_count', 'questionnaire_phrase_hit_count', 'candidate_module_file_count', 'construction_code_file_count', 'evidence_status'], 40)}

## Interpretation

- A local item module or questionnaire phrase is not equivalent to a documented survey-team aggregate construction recipe.
- The denominator variant remains unresolved because `totcons05` and the public-metadata formula components are absent from local exact raw-variable evidence.
- This audit strengthens the no-promotion decision: any ALB_2005 CHE/SDG denominator would still require official aggregate construction documentation or a raw package version containing the missing component variables.
- Climate-linked analysis remains independently blocked by missing verified household interview timing and climate-ready geography.

## Machine-Readable Outputs

- `temp/alb2005_consumption_component_source_search_audit.csv`
- `result/alb2005_consumption_component_source_search_summary.csv`
"""
    REPORT_PATH.write_text(report, encoding="utf-8")


def main() -> None:
    ensure_dirs()
    rows, diagnostics = build_rows()
    summary = build_summary(rows, diagnostics)
    write_csv(AUDIT_PATH, rows, AUDIT_COLUMNS)
    write_csv(SUMMARY_PATH, summary, SUMMARY_COLUMNS)
    write_report(rows, summary)
    append_log(TEMP_DIR / "audit_log.md", f"Built ALB_2005 consumption component source-search audit rows={len(rows)} decision={DECISION}.")
    print(f"ALB_2005 consumption component source-search rows={len(rows)} decision={DECISION}.")


if __name__ == "__main__":
    main()
