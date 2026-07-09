from __future__ import annotations

import csv
import re
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

from common import REPORT_DIR, RESULT_DIR, TEMP_DIR, append_log, ensure_dirs, write_csv


SCAFFOLD_PATH = TEMP_DIR / "harmonization_recipe_scaffold.csv"
PROTOCOL_PATH = TEMP_DIR / "raw_variable_verification_protocol.csv"
VALUE_AUDIT_PATH = TEMP_DIR / "harmonization_value_audit.csv"
AUTO_VALUE_AUDIT_PATH = TEMP_DIR / "first_batch_harmonization_value_audit_auto.csv"
RAW_FILE_PATH = TEMP_DIR / "raw_schema_inventory" / "raw_file_inventory.csv"
RAW_VARIABLE_PATH = TEMP_DIR / "raw_schema_inventory" / "raw_variable_catalog.csv"

GATE_PATH = TEMP_DIR / "harmonization_recipe_gate.csv"
VALUE_AUDIT_TEMPLATE_PATH = TEMP_DIR / "harmonization_value_audit_template.csv"
VERIFIED_CANDIDATES_PATH = TEMP_DIR / "harmonization_recipe_verified_candidates.csv"
READINESS_PATH = RESULT_DIR / "harmonization_readiness_matrix.csv"
SUMMARY_PATH = RESULT_DIR / "harmonization_recipe_gate_summary.csv"
REPORT_PATH = REPORT_DIR / "harmonization_recipe_gate.md"

GATE_COLUMNS = [
    "bundle_rank",
    "country",
    "survey_name",
    "wave",
    "idno",
    "concept",
    "harmonized_variable",
    "required",
    "merge_level",
    "key_role",
    "candidate_source_files",
    "matched_source_files",
    "candidate_raw_variables",
    "matched_raw_variables",
    "raw_label",
    "source_file_status",
    "raw_variable_status",
    "value_audit_status",
    "recipe_gate_status",
    "blocking_reason",
    "minimum_evidence_to_promote",
    "next_action",
]

VALUE_TEMPLATE_COLUMNS = [
    "country",
    "survey_name",
    "wave",
    "idno",
    "concept",
    "harmonized_variable",
    "source_file",
    "raw_variable",
    "raw_label",
    "value_audit_status",
    "ready_for_recipe",
    "confirmed_merge_level",
    "confirmed_key_role",
    "confirmed_unit",
    "confirmed_recall_period",
    "missing_code_rule",
    "valid_range_rule",
    "lineage_notes",
    "auditor",
    "audit_date",
]

READINESS_COLUMNS = [
    "bundle_rank",
    "country",
    "survey_name",
    "wave",
    "idno",
    "required_variable_rows",
    "recommended_variable_rows",
    "optional_variable_rows",
    "recipe_ready_required_rows",
    "recipe_ready_recommended_rows",
    "blocked_required_rows",
    "blocked_recommended_rows",
    "required_variables_missing",
    "readiness_status",
    "next_action",
]

SUMMARY_COLUMNS = ["metric", "value", "interpretation"]

PASS_STATUSES = {
    "pass",
    "passed",
    "verified",
    "verified_pass",
    "value_audit_passed",
    "ready",
    "ready_for_recipe",
}
YES_VALUES = {"1", "true", "yes", "y", "ready", "pass", "passed"}


def read_csv_dicts(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        return []
    with path.open(encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def split_values(value: str, limit: int | None = None) -> list[str]:
    seen: set[str] = set()
    out: list[str] = []
    for item in (value or "").replace(",", ";").split(";"):
        clean = item.strip()
        if not clean or clean in seen:
            continue
        out.append(clean)
        seen.add(clean)
        if limit is not None and len(out) >= limit:
            break
    return out


def compact_join(values: list[str], limit: int = 20) -> str:
    out: list[str] = []
    seen: set[str] = set()
    for value in values:
        clean = (value or "").strip()
        if not clean or clean in seen:
            continue
        out.append(clean)
        seen.add(clean)
        if len(out) >= limit:
            break
    return ";".join(out)


def safe_int(value: str, default: int = 9999) -> int:
    try:
        return int(float(value))
    except (TypeError, ValueError):
        return default


def path_name(value: str) -> str:
    value = (value or "").replace("\\", "/").strip()
    return Path(value).name.lower()


def normalize_token(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "", (value or "").lower())


def file_match(candidate: str, actual: str) -> bool:
    candidate_norm = normalize_token(candidate)
    actual_text = (actual or "").replace("\\", "/")
    actual_norms = {
        normalize_token(actual_text),
        normalize_token(Path(actual_text).name),
        normalize_token(Path(actual_text).stem),
    }
    return bool(candidate_norm and any(candidate_norm in actual_norm or actual_norm in candidate_norm for actual_norm in actual_norms if actual_norm))


def infer_idno(value: str, known_idnos: set[str]) -> str:
    low = (value or "").lower()
    for idno in sorted(known_idnos, key=len, reverse=True):
        if idno and idno.lower() in low:
            return idno
    return ""


def build_bundle_rank(scaffold_rows: list[dict[str, str]], protocol_rows: list[dict[str, str]]) -> dict[str, str]:
    rank_by_idno: dict[str, str] = {}
    for row in protocol_rows:
        idno = row.get("idno", "")
        rank = row.get("quality_rank", "")
        if idno and rank and (idno not in rank_by_idno or safe_int(rank) < safe_int(rank_by_idno[idno])):
            rank_by_idno[idno] = rank
    for idx, idno in enumerate(dict.fromkeys(row.get("idno", "") for row in scaffold_rows if row.get("idno", "")), start=1):
        rank_by_idno.setdefault(idno, str(idx))
    return rank_by_idno


def build_raw_file_index(raw_files: list[dict[str, str]], known_idnos: set[str]) -> dict[str, set[str]]:
    out: dict[str, set[str]] = defaultdict(set)
    for row in raw_files:
        fields = [row.get("source_path", ""), row.get("extracted_from", ""), row.get("path", ""), row.get("file_name", "")]
        text = " ".join(fields)
        idno = row.get("idno", "") or infer_idno(text, known_idnos)
        if not idno:
            continue
        for value in fields:
            name = path_name(value)
            if name:
                out[idno].add(name)
            if value:
                out[idno].add(value.replace("\\", "/").lower())
    return out


def build_raw_variable_index(raw_variables: list[dict[str, str]], known_idnos: set[str]) -> dict[str, dict[str, set[str]]]:
    out: dict[str, dict[str, set[str]]] = defaultdict(lambda: defaultdict(set))
    for row in raw_variables:
        fields = [row.get("source_path", ""), row.get("extracted_from", ""), row.get("file_name", "")]
        text = " ".join(fields)
        idno = row.get("idno", "") or infer_idno(text, known_idnos)
        variable = (row.get("variable_name", "") or row.get("raw_variable", "")).strip().lower()
        if not idno or not variable:
            continue
        for value in fields:
            name = path_name(value)
            if name:
                out[idno][variable].add(name)
        if not out[idno][variable]:
            out[idno][variable].add("")
    return out


def value_audit_passed(row: dict[str, str]) -> bool:
    status = (row.get("value_audit_status", "") or row.get("raw_value_audit_status", "") or row.get("status", "")).strip().lower()
    ready = (row.get("ready_for_recipe", "") or row.get("recipe_ready", "")).strip().lower()
    if ready and ready not in YES_VALUES:
        return False
    return status in PASS_STATUSES and (not ready or ready in YES_VALUES)


def build_value_audit_index(value_rows: list[dict[str, str]]) -> dict[tuple[str, str, str], list[dict[str, str]]]:
    out: dict[tuple[str, str, str], list[dict[str, str]]] = defaultdict(list)
    for row in value_rows:
        idno = row.get("idno", "").strip()
        hvar = row.get("harmonized_variable", "").strip()
        raw_values = split_values(row.get("raw_variable", ""))
        if not raw_values:
            raw_values = [""]
        for raw in raw_values:
            out[(idno, hvar, raw.lower())].append(row)
    return out


def matched_files(candidate_files: list[str], available_files: set[str]) -> list[str]:
    matches = []
    for item in candidate_files:
        direct = [available for available in available_files if file_match(item, available)]
        if direct:
            matches.extend(sorted(Path(value).name for value in direct))
    return matches


def matched_variables(
    candidate_vars: list[str],
    candidate_files: list[str],
    available_vars: dict[str, set[str]],
) -> list[str]:
    matches = []
    for item in candidate_vars:
        low = item.lower()
        if low not in available_vars:
            continue
        seen_files = available_vars[low]
        if not candidate_files or "" in seen_files or any(file_match(candidate, seen) for candidate in candidate_files for seen in seen_files):
            matches.append(item)
    return matches


def value_status_for_row(
    idno: str,
    hvar: str,
    matched_vars: list[str],
    value_index: dict[tuple[str, str, str], list[dict[str, str]]],
    value_rows_exist: bool,
) -> str:
    if not value_rows_exist:
        return "value_audit_file_missing"
    if not matched_vars:
        return "value_audit_blocked_until_raw_variable_seen"
    matched_audits = []
    for raw in matched_vars:
        matched_audits.extend(value_index.get((idno, hvar, raw.lower()), []))
        matched_audits.extend(value_index.get((idno, hvar, ""), []))
    if not matched_audits:
        return "value_audit_row_missing"
    if any(value_audit_passed(row) for row in matched_audits):
        return "value_audit_passed"
    return compact_join(
        [
            row.get("value_audit_status", "") or row.get("raw_value_audit_status", "") or row.get("status", "value_audit_not_passed")
            for row in matched_audits
        ],
        6,
    )


def gate_status(source_file_status: str, raw_variable_status: str, value_audit_status: str) -> tuple[str, str, str]:
    if source_file_status != "raw_file_seen":
        return (
            "blocked_raw_file_missing",
            "candidate source files have not been found in raw_file_inventory",
            "place original files under temp/raw_downloads and rerun raw-download/schema inspection",
        )
    if raw_variable_status != "raw_variable_seen":
        return (
            "blocked_raw_variable_missing",
            "candidate raw variables have not been found in raw_variable_catalog",
            "inspect schemas and verify candidate variable names against raw files",
        )
    if value_audit_status != "value_audit_passed":
        return (
            "blocked_value_audit_missing",
            "raw variable names alone are insufficient; values, units, recall period, keys, missing codes, and lineage must pass",
            "complete temp/harmonization_value_audit.csv using the generated template",
        )
    return (
        "recipe_candidate_ready",
        "",
        "copy only verified candidate rows into temp/harmonization_recipe.csv and rerun household harmonization",
    )


def build_gate_rows(
    scaffold_rows: list[dict[str, str]],
    protocol_rows: list[dict[str, str]],
    raw_files: list[dict[str, str]],
    raw_variables: list[dict[str, str]],
    value_rows: list[dict[str, str]],
) -> list[dict[str, str]]:
    known_idnos = {row.get("idno", "") for row in scaffold_rows if row.get("idno", "")}
    rank_by_idno = build_bundle_rank(scaffold_rows, protocol_rows)
    files_by_idno = build_raw_file_index(raw_files, known_idnos)
    variables_by_idno = build_raw_variable_index(raw_variables, known_idnos)
    value_index = build_value_audit_index(value_rows)
    value_rows_exist = (VALUE_AUDIT_PATH.exists() or AUTO_VALUE_AUDIT_PATH.exists()) and bool(value_rows)

    rows = []
    for row in scaffold_rows:
        idno = row.get("idno", "")
        candidate_files = split_values(row.get("source_file", ""))
        candidate_vars = split_values(row.get("raw_variable", ""))
        file_matches = matched_files(candidate_files, files_by_idno.get(idno, set()))
        var_matches = matched_variables(candidate_vars, candidate_files, variables_by_idno.get(idno, {}))
        source_status = "raw_file_seen" if file_matches else ("raw_file_inventory_empty" if not raw_files else "raw_file_not_matched")
        var_status = "raw_variable_seen" if var_matches else ("raw_variable_catalog_empty" if not raw_variables else "raw_variable_not_matched")
        value_status = value_status_for_row(idno, row.get("harmonized_variable", ""), var_matches, value_index, value_rows_exist)
        recipe_status, reason, action = gate_status(source_status, var_status, value_status)
        rows.append(
            {
                "bundle_rank": rank_by_idno.get(idno, ""),
                "country": row.get("country", ""),
                "survey_name": row.get("survey_name", ""),
                "wave": row.get("wave", ""),
                "idno": idno,
                "concept": row.get("concept", ""),
                "harmonized_variable": row.get("harmonized_variable", ""),
                "required": row.get("required", ""),
                "merge_level": row.get("merge_level", ""),
                "key_role": row.get("key_role", ""),
                "candidate_source_files": compact_join(candidate_files, 30),
                "matched_source_files": compact_join(file_matches, 30),
                "candidate_raw_variables": compact_join(candidate_vars, 30),
                "matched_raw_variables": compact_join(var_matches, 30),
                "raw_label": row.get("raw_label", ""),
                "source_file_status": source_status,
                "raw_variable_status": var_status,
                "value_audit_status": value_status,
                "recipe_gate_status": recipe_status,
                "blocking_reason": reason,
                "minimum_evidence_to_promote": row.get(
                    "verification_required",
                    "raw labels, values, units, recall period, merge keys, missing codes, and lineage must pass",
                ),
                "next_action": action,
            }
        )
    rows.sort(key=lambda r: (safe_int(r["bundle_rank"]), r["idno"], r["required"] != "yes", r["concept"], r["harmonized_variable"]))
    return rows


def build_value_audit_template(gate_rows: list[dict[str, str]]) -> list[dict[str, str]]:
    rows = []
    for row in gate_rows:
        raw_values = split_values(row.get("candidate_raw_variables", ""), 8) or [""]
        source_files = split_values(row.get("candidate_source_files", ""), 8) or [""]
        for raw in raw_values:
            rows.append(
                {
                    "country": row.get("country", ""),
                    "survey_name": row.get("survey_name", ""),
                    "wave": row.get("wave", ""),
                    "idno": row.get("idno", ""),
                    "concept": row.get("concept", ""),
                    "harmonized_variable": row.get("harmonized_variable", ""),
                    "source_file": compact_join(source_files, 8),
                    "raw_variable": raw,
                    "raw_label": row.get("raw_label", ""),
                    "value_audit_status": "pending_raw_file_and_value_inspection",
                    "ready_for_recipe": "0",
                    "confirmed_merge_level": "",
                    "confirmed_key_role": "",
                    "confirmed_unit": "",
                    "confirmed_recall_period": "",
                    "missing_code_rule": "",
                    "valid_range_rule": "",
                    "lineage_notes": "",
                    "auditor": "",
                    "audit_date": "",
                }
            )
    return rows


def build_readiness(gate_rows: list[dict[str, str]]) -> list[dict[str, str]]:
    grouped: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in gate_rows:
        grouped[row["idno"]].append(row)

    readiness = []
    for idno, rows in grouped.items():
        first = rows[0]
        required = [row for row in rows if row.get("required") == "yes"]
        recommended = [row for row in rows if row.get("required") == "recommended"]
        optional = [row for row in rows if row.get("required") not in {"yes", "recommended"}]
        required_ready = [row for row in required if row.get("recipe_gate_status") == "recipe_candidate_ready"]
        recommended_ready = [row for row in recommended if row.get("recipe_gate_status") == "recipe_candidate_ready"]
        blocked_required = [row for row in required if row.get("recipe_gate_status") != "recipe_candidate_ready"]
        blocked_recommended = [row for row in recommended if row.get("recipe_gate_status") != "recipe_candidate_ready"]
        missing_required = sorted({row.get("harmonized_variable", "") for row in blocked_required if row.get("harmonized_variable", "")})

        if not required:
            status = "blocked_no_required_harmonized_variables"
            action = "review scaffold and concept requirements before recipe assembly"
        elif blocked_required:
            status = "blocked_until_required_raw_value_audits_pass"
            action = "complete raw-file, raw-variable, and value/unit/recall/key audits for required variables"
        elif blocked_recommended:
            status = "minimum_required_ready_recommended_still_blocked"
            action = "assemble a minimum recipe only if required-variable quality is sufficient; continue recommended-variable audits"
        else:
            status = "ready_for_verified_recipe_assembly"
            action = "assemble temp/harmonization_recipe.csv from verified candidate rows and run household harmonization"

        readiness.append(
            {
                "bundle_rank": first.get("bundle_rank", ""),
                "country": first.get("country", ""),
                "survey_name": first.get("survey_name", ""),
                "wave": first.get("wave", ""),
                "idno": idno,
                "required_variable_rows": str(len(required)),
                "recommended_variable_rows": str(len(recommended)),
                "optional_variable_rows": str(len(optional)),
                "recipe_ready_required_rows": str(len(required_ready)),
                "recipe_ready_recommended_rows": str(len(recommended_ready)),
                "blocked_required_rows": str(len(blocked_required)),
                "blocked_recommended_rows": str(len(blocked_recommended)),
                "required_variables_missing": compact_join(missing_required, 40),
                "readiness_status": status,
                "next_action": action,
            }
        )
    readiness.sort(key=lambda r: safe_int(r["bundle_rank"]))
    return readiness


def build_summary(
    gate_rows: list[dict[str, str]],
    value_template: list[dict[str, str]],
    verified_candidates: list[dict[str, str]],
    readiness: list[dict[str, str]],
    raw_files: list[dict[str, str]],
    raw_variables: list[dict[str, str]],
    value_rows: list[dict[str, str]],
) -> list[dict[str, str]]:
    gate_counts = Counter(row.get("recipe_gate_status", "") for row in gate_rows)
    readiness_counts = Counter(row.get("readiness_status", "") for row in readiness)
    required_counts = Counter(row.get("required", "") for row in gate_rows)
    value_counts = Counter(row.get("value_audit_status", "") for row in gate_rows)
    rows = [
        {"metric": "gate_rows", "value": str(len(gate_rows)), "interpretation": "Scaffold rows assessed by raw-file, raw-variable, and value-audit gates."},
        {"metric": "value_audit_template_rows", "value": str(len(value_template)), "interpretation": "Rows in the post-download value-audit template."},
        {"metric": "verified_candidate_rows", "value": str(len(verified_candidates)), "interpretation": "Rows that can be copied into a real harmonization recipe after all gates pass."},
        {"metric": "country_wave_rows", "value": str(len(readiness)), "interpretation": "Country-waves assessed for minimum harmonization readiness."},
        {"metric": "ready_country_wave_rows", "value": str(sum(1 for row in readiness if row.get("readiness_status") == "ready_for_verified_recipe_assembly")), "interpretation": "Country-waves ready for verified recipe assembly."},
        {"metric": "blocked_country_wave_rows", "value": str(sum(1 for row in readiness if row.get("readiness_status") != "ready_for_verified_recipe_assembly")), "interpretation": "Country-waves still blocked by required raw evidence."},
        {"metric": "raw_file_inventory_rows", "value": str(len(raw_files)), "interpretation": "Raw file inventory rows available to the gate."},
        {"metric": "raw_variable_catalog_rows", "value": str(len(raw_variables)), "interpretation": "Raw variable catalog rows available to the gate."},
        {"metric": "value_audit_rows", "value": str(len(value_rows)), "interpretation": "Manually or programmatically completed value-audit rows."},
    ]
    for key, count in sorted(gate_counts.items()):
        rows.append({"metric": f"recipe_gate_status_{key}", "value": str(count), "interpretation": "Recipe gate status count."})
    for key, count in sorted(readiness_counts.items()):
        rows.append({"metric": f"readiness_status_{key}", "value": str(count), "interpretation": "Country-wave readiness status count."})
    for key, count in sorted(required_counts.items()):
        rows.append({"metric": f"required_flag_{key or 'blank'}", "value": str(count), "interpretation": "Required/recommended/optional scaffold row count."})
    for key, count in sorted(value_counts.items()):
        rows.append({"metric": f"value_audit_status_{key}", "value": str(count), "interpretation": "Value-audit status count."})
    return rows


def markdown_count_table(counter: Counter[str], label: str) -> str:
    lines = [f"| {label} | Count |", "|---|---:|"]
    for key, count in counter.most_common():
        lines.append(f"| {key or 'blank'} | {count} |")
    return "\n".join(lines)


def markdown_rows(rows: list[dict[str, str]], columns: list[str], limit: int = 15) -> str:
    lines = ["| " + " | ".join(columns) + " |", "|" + "|".join("---" for _ in columns) + "|"]
    for row in rows[:limit]:
        vals = []
        for column in columns:
            value = (row.get(column, "") or "").replace("|", "/")
            if len(value) > 120:
                value = value[:117] + "..."
            vals.append(value)
        lines.append("| " + " | ".join(vals) + " |")
    return "\n".join(lines)


def write_report(gate_rows: list[dict[str, str]], readiness: list[dict[str, str]], summary: list[dict[str, str]]) -> None:
    gate_counts = Counter(row.get("recipe_gate_status", "") for row in gate_rows)
    source_counts = Counter(row.get("source_file_status", "") for row in gate_rows)
    variable_counts = Counter(row.get("raw_variable_status", "") for row in gate_rows)
    value_counts = Counter(row.get("value_audit_status", "") for row in gate_rows)
    readiness_counts = Counter(row.get("readiness_status", "") for row in readiness)
    summary_table = "\n".join(f"| {row['metric']} | {row['value']} | {row['interpretation']} |" for row in summary)
    REPORT_PATH.write_text(
        f"""# Harmonization Recipe Gate

Status: fail-closed. Metadata scaffold rows are not executable harmonization recipes. A row becomes a verified recipe candidate only after the raw file is present, the raw variable is found in the inspected schema, and a value/unit/recall/key/missing-code/lineage audit passes.

## Counts

| Metric | Value | Interpretation |
|---|---:|---|
{summary_table}

## Gate Status

{markdown_count_table(gate_counts, 'Recipe gate status') if gate_rows else 'No gate rows exist yet.'}

## Raw File Status

{markdown_count_table(source_counts, 'Raw file status') if gate_rows else 'No gate rows exist yet.'}

## Raw Variable Status

{markdown_count_table(variable_counts, 'Raw variable status') if gate_rows else 'No gate rows exist yet.'}

## Value Audit Status

{markdown_count_table(value_counts, 'Value audit status') if gate_rows else 'No gate rows exist yet.'}

## Country-Wave Readiness

{markdown_count_table(readiness_counts, 'Readiness status') if readiness else 'No readiness rows exist yet.'}

{markdown_rows(readiness, ['bundle_rank', 'country', 'wave', 'idno', 'required_variable_rows', 'recipe_ready_required_rows', 'blocked_required_rows', 'readiness_status'], 20) if readiness else ''}

## Guardrails

- Do not create `temp/harmonization_recipe.csv` from `temp/harmonization_recipe_scaffold.csv`.
- Do not promote a row based only on metadata labels or a raw variable-name match.
- Do not construct `data/harmonized_household.csv` until required variables pass value, unit, recall-period, key, missing-code, and lineage checks.
- Use `temp/harmonization_value_audit_template.csv` as the checklist after raw downloads, then save completed checks as `temp/harmonization_value_audit.csv`.

## Outputs

- `temp/harmonization_recipe_gate.csv`
- `temp/harmonization_value_audit_template.csv`
- `temp/first_batch_harmonization_value_audit_auto.csv` when first-batch raw value summaries exist
- `temp/harmonization_recipe_verified_candidates.csv`
- `result/harmonization_readiness_matrix.csv`
- `result/harmonization_recipe_gate_summary.csv`
""",
        encoding="utf-8",
    )


def main() -> None:
    ensure_dirs()
    scaffold_rows = read_csv_dicts(SCAFFOLD_PATH)
    protocol_rows = read_csv_dicts(PROTOCOL_PATH)
    raw_files = read_csv_dicts(RAW_FILE_PATH)
    raw_variables = read_csv_dicts(RAW_VARIABLE_PATH)
    value_rows = read_csv_dicts(VALUE_AUDIT_PATH) + read_csv_dicts(AUTO_VALUE_AUDIT_PATH)

    gate_rows = build_gate_rows(scaffold_rows, protocol_rows, raw_files, raw_variables, value_rows)
    value_template = build_value_audit_template(gate_rows)
    verified_candidates = [row for row in gate_rows if row.get("recipe_gate_status") == "recipe_candidate_ready"]
    readiness = build_readiness(gate_rows)
    summary = build_summary(gate_rows, value_template, verified_candidates, readiness, raw_files, raw_variables, value_rows)

    write_csv(GATE_PATH, gate_rows, GATE_COLUMNS)
    write_csv(VALUE_AUDIT_TEMPLATE_PATH, value_template, VALUE_TEMPLATE_COLUMNS)
    write_csv(VERIFIED_CANDIDATES_PATH, verified_candidates, GATE_COLUMNS)
    write_csv(READINESS_PATH, readiness, READINESS_COLUMNS)
    write_csv(SUMMARY_PATH, summary, SUMMARY_COLUMNS)
    write_report(gate_rows, readiness, summary)
    append_log(
        TEMP_DIR / "audit_log.md",
        f"Harmonization recipe gate rows={len(gate_rows)} verified_candidates={len(verified_candidates)} country_wave_rows={len(readiness)}.",
    )
    print(f"Harmonization recipe gate rows={len(gate_rows)} verified_candidates={len(verified_candidates)} country_wave_rows={len(readiness)}.")


if __name__ == "__main__":
    main()
