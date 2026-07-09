from __future__ import annotations

import csv
import re
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

from common import PROJECT_ROOT, REPORT_DIR, RESULT_DIR, TEMP_DIR, append_log, ensure_dirs, read_json, write_csv


QUEUE_PATH = TEMP_DIR / "priority_lsms_isa_refocused_acquisition_queue.csv"
RECEIPT_PATH = TEMP_DIR / "priority_lsms_isa_public_documentation_receipt.csv"
FILE_INVENTORY_PATH = TEMP_DIR / "priority_lsms_isa_public_documentation_file_inventory.csv"

MATRIX_PATH = TEMP_DIR / "priority_lsms_isa_variable_evidence_matrix.csv"
COVERAGE_PATH = TEMP_DIR / "priority_lsms_isa_requirement_variable_coverage.csv"
FILE_SHORTLIST_PATH = TEMP_DIR / "priority_lsms_isa_concept_file_shortlist.csv"
SUMMARY_PATH = RESULT_DIR / "priority_lsms_isa_variable_evidence_summary.csv"
REPORT_PATH = REPORT_DIR / "priority_lsms_isa_variable_evidence_matrix.md"
RAW_ROOT = TEMP_DIR / "raw_downloads"

TOP_VARIABLES_PER_REQUIREMENT = 12
TOP_FILES_PER_REQUIREMENT = 8
STRONG_SCORE = 12

REQUIREMENTS = [
    "household_person_keys",
    "weights_and_design",
    "consumption_or_income",
    "oop_health_expenditure",
    "health_need_and_access",
    "survey_timing",
    "climate_geography",
    "missing_codes_units_recall_skip_patterns",
]

CONCEPT_SPECS = {
    "household_person_keys": {
        "phrases": ["household id", "unique household", "person id", "individual id", "member id", "roster", "line number"],
        "tokens": ["hhid", "hh_id", "household_id", "individual_id", "personid", "person_id", "pid", "member", "roster", "case_id"],
        "file_terms": ["roster", "cover", "household"],
    },
    "weights_and_design": {
        "phrases": ["sample weight", "household weight", "sampling weight", "enumeration area", "primary sampling", "stratum"],
        "tokens": ["weight", "pw_", "pweight", "strata", "stratum", "cluster", "ea_id", "ea", "psu", "enumeration"],
        "file_terms": ["cover", "household", "sampling", "weight"],
    },
    "consumption_or_income": {
        "phrases": ["total consumption", "consumption aggregate", "food consumption", "nonfood expenditure", "non-food expenditure", "total income", "household expenditure"],
        "tokens": ["consumption", "consume", "expenditure", "expenses", "income", "food", "nonfood", "non_food", "aggregate", "cons", "hh_exp"],
        "file_terms": ["consumption", "expenditure", "food", "nonfood", "income"],
    },
    "oop_health_expenditure": {
        "phrases": ["health expenditure", "medical expenditure", "medical expenses", "health expenses", "out of pocket", "out-of-pocket", "paid for health", "cost of treatment", "consultation fee"],
        "tokens": ["expenditure", "expenses", "spent", "spend", "cost", "payment", "paid", "fee", "amount", "medical", "medicine"],
        "required_any": ["health", "medical", "medicine", "hospital", "clinic", "doctor", "treatment", "consultation"],
        "file_terms": ["health", "medical", "hospital", "clinic", "expenditure"],
    },
    "health_need_and_access": {
        "phrases": ["illness or injury", "suffer from illness", "sought care", "seek care", "health facility", "reason for not", "medical treatment", "consulted"],
        "tokens": ["illness", "injury", "sick", "disease", "health", "care", "treatment", "doctor", "clinic", "hospital", "facility", "medicine", "distance", "cost", "consult"],
        "file_terms": ["health", "medical", "illness", "access"],
    },
    "survey_timing": {
        "phrases": ["date of interview", "interview date", "survey date", "start time", "end time", "visit date", "month of interview"],
        "tokens": ["interviewdate", "interview_date", "date", "month", "year", "visit", "start", "end", "time"],
        "file_terms": ["cover", "household", "interview"],
    },
    "climate_geography": {
        "phrases": ["gps coordinates", "latitude", "longitude", "enumeration area", "rural urban", "region code", "district code", "cluster id"],
        "tokens": ["latitude", "longitude", "gps", "coord", "region", "district", "zone", "woreda", "ea_id", "ea", "cluster", "state", "lga", "ward", "parish", "village", "rural", "urban", "admin"],
        "file_terms": ["cover", "geovariables", "geodata", "location", "household"],
    },
    "missing_codes_units_recall_skip_patterns": {
        "phrases": ["do not know", "don't know", "refused", "not applicable", "other specify", "unit of measure", "recall period"],
        "tokens": ["dk", "refused", "missing", "other", "specify", "unit", "quantity", "recall"],
        "file_terms": ["questionnaire", "documentation"],
        "documentation_only": True,
    },
}

MATRIX_COLUMNS = [
    "download_priority_order",
    "queue_role",
    "country",
    "wave",
    "idno",
    "requirement",
    "candidate_rank",
    "variable_name",
    "variable_label",
    "file_id",
    "file_name",
    "file_description",
    "match_score",
    "matched_terms",
    "match_basis",
    "official_metadata_status",
    "raw_value_verification_status",
    "promotion_guardrail",
]

COVERAGE_COLUMNS = [
    "download_priority_order",
    "queue_role",
    "country",
    "wave",
    "idno",
    "requirement",
    "candidate_variable_rows",
    "strong_candidate_variable_rows",
    "candidate_file_rows",
    "top_file_names",
    "coverage_status",
    "raw_value_verification_status",
    "promotion_guardrail",
]

FILE_SHORTLIST_COLUMNS = [
    "download_priority_order",
    "queue_role",
    "country",
    "wave",
    "idno",
    "requirement",
    "file_rank",
    "file_id",
    "file_name",
    "file_description",
    "candidate_variable_rows",
    "strong_candidate_variable_rows",
    "top_variable_names",
    "official_metadata_status",
    "raw_value_verification_status",
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


def shorten(value: Any, limit: int = 220) -> str:
    text = " ".join(clean(value).split())
    if len(text) <= limit:
        return text
    return text[: limit - 3] + "..."


def normalize(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", " ", clean(value).lower()).strip()


def compact(values: list[str], limit: int = 8) -> str:
    out: list[str] = []
    seen: set[str] = set()
    for value in values:
        item = shorten(value, 90)
        if item and item not in seen:
            out.append(item)
            seen.add(item)
        if len(out) >= limit:
            break
    return ";".join(out)


def receipt_by_idno_resource() -> dict[tuple[str, str], dict[str, str]]:
    out: dict[tuple[str, str], dict[str, str]] = {}
    for row in read_csv_dicts(RECEIPT_PATH):
        if row.get("receipt_status") not in {"saved", "saved_existing"}:
            continue
        out[(row.get("idno", ""), row.get("resource_type", ""))] = row
    return out


def file_inventory_by_idno() -> dict[str, dict[str, dict[str, str]]]:
    out: dict[str, dict[str, dict[str, str]]] = defaultdict(dict)
    for row in read_csv_dicts(FILE_INVENTORY_PATH):
        out[row.get("idno", "")][row.get("file_id", "")] = row
    return out


def variables_by_idno() -> dict[str, list[dict[str, str]]]:
    receipts = receipt_by_idno_resource()
    out: dict[str, list[dict[str, str]]] = {}
    for row in read_csv_dicts(QUEUE_PATH):
        idno = row.get("idno", "")
        receipt = receipts.get((idno, "variables_idno_json"), {})
        saved = receipt.get("saved_path", "")
        path = PROJECT_ROOT / saved
        if not saved or not path.exists():
            out[idno] = []
            continue
        data = read_json(path)
        out[idno] = data.get("variables", []) if isinstance(data, dict) else []
    return out


def term_present(term: str, text: str) -> bool:
    term_norm = normalize(term)
    if not term_norm:
        return False
    return bool(re.search(rf"(^|\s){re.escape(term_norm)}($|\s)", text)) or term_norm.replace(" ", "") in text.replace(" ", "")


def score_variable(requirement: str, var: dict[str, str], file_row: dict[str, str]) -> tuple[int, list[str], str]:
    spec = CONCEPT_SPECS[requirement]
    name = clean(var.get("name"))
    label = clean(var.get("labl"))
    file_name = clean(file_row.get("file_name"))
    file_description = clean(file_row.get("file_description"))
    name_text = normalize(name)
    label_text = normalize(label)
    file_text = normalize(f"{file_name} {file_description}")
    all_text = normalize(f"{name} {label} {file_name} {file_description}")
    score = 0
    matched: list[str] = []
    basis: list[str] = []

    required_any = spec.get("required_any", [])
    if required_any and not any(term_present(term, all_text) for term in required_any):
        return 0, [], "missing_required_health_context"

    for phrase in spec.get("phrases", []):
        if term_present(phrase, all_text):
            score += 7
            matched.append(phrase)
            basis.append("phrase")
    for token in spec.get("tokens", []):
        if term_present(token, name_text):
            score += 8
            matched.append(token)
            basis.append("name")
        elif term_present(token, label_text):
            score += 4
            matched.append(token)
            basis.append("label")
    for token in spec.get("file_terms", []):
        if term_present(token, file_text):
            score += 2
            matched.append(f"file:{token}")
            basis.append("file")

    if requirement == "oop_health_expenditure":
        spending_terms = ["expenditure", "expenses", "spent", "spend", "cost", "payment", "paid", "fee", "amount"]
        health_terms = spec.get("required_any", [])
        has_spending = any(term_present(term, all_text) for term in spending_terms)
        has_health = any(term_present(term, all_text) for term in health_terms)
        if not (has_spending and has_health):
            return 0, [], "missing_joint_health_spending_context"
        score += 6

    if requirement == "survey_timing" and term_present("date", name_text):
        score += 6
    if requirement == "climate_geography" and any(term_present(term, name_text) for term in ["latitude", "longitude", "gps"]):
        score += 10
    if requirement == "weights_and_design" and any(term_present(term, name_text) for term in ["weight", "pw_"]):
        score += 10

    matched_unique = []
    seen: set[str] = set()
    for item in matched:
        if item not in seen:
            matched_unique.append(item)
            seen.add(item)
    return score, matched_unique, ";".join(sorted(set(basis))) if basis else "no_match"


def build_matrix_rows() -> list[dict[str, str]]:
    queue_rows = read_csv_dicts(QUEUE_PATH)
    vars_by_id = variables_by_idno()
    files_by_id = file_inventory_by_idno()
    rows: list[dict[str, str]] = []

    for queue in queue_rows:
        idno = queue.get("idno", "")
        file_map = files_by_id.get(idno, {})
        for requirement in REQUIREMENTS:
            scored: list[tuple[int, list[str], str, dict[str, str], dict[str, str]]] = []
            spec = CONCEPT_SPECS[requirement]
            if spec.get("documentation_only"):
                continue
            for var in vars_by_id.get(idno, []):
                file_row = file_map.get(clean(var.get("fid")), {})
                score, matched_terms, basis = score_variable(requirement, var, file_row)
                if score <= 0:
                    continue
                scored.append((score, matched_terms, basis, var, file_row))
            scored.sort(
                key=lambda item: (
                    -item[0],
                    clean(item[3].get("fid")),
                    clean(item[3].get("name")).lower(),
                )
            )
            for rank, (score, matched_terms, basis, var, file_row) in enumerate(scored[:TOP_VARIABLES_PER_REQUIREMENT], start=1):
                rows.append(
                    {
                        "download_priority_order": queue.get("download_priority_order", ""),
                        "queue_role": queue.get("queue_role", ""),
                        "country": queue.get("country", ""),
                        "wave": queue.get("wave", ""),
                        "idno": idno,
                        "requirement": requirement,
                        "candidate_rank": str(rank),
                        "variable_name": clean(var.get("name")),
                        "variable_label": shorten(var.get("labl"), 190),
                        "file_id": clean(var.get("fid")),
                        "file_name": file_row.get("file_name", ""),
                        "file_description": shorten(file_row.get("file_description"), 190),
                        "match_score": str(score),
                        "matched_terms": compact(matched_terms, 16),
                        "match_basis": basis,
                        "official_metadata_status": "official_public_metadata_candidate",
                        "raw_value_verification_status": "not_raw_value_verified",
                        "promotion_guardrail": "metadata candidate only; verify raw values, labels, units, recall periods, missing codes, skip patterns, merge keys, and survey design before promotion",
                    }
                )
    return rows


def build_coverage_rows(matrix_rows: list[dict[str, str]]) -> list[dict[str, str]]:
    queue_rows = read_csv_dicts(QUEUE_PATH)
    by_key: dict[tuple[str, str], list[dict[str, str]]] = defaultdict(list)
    for row in matrix_rows:
        by_key[(row.get("idno", ""), row.get("requirement", ""))].append(row)

    rows: list[dict[str, str]] = []
    for queue in queue_rows:
        idno = queue.get("idno", "")
        for requirement in REQUIREMENTS:
            candidates = by_key.get((idno, requirement), [])
            file_names = []
            for candidate in candidates:
                if candidate.get("file_name"):
                    file_names.append(candidate["file_name"])
            strong = [row for row in candidates if safe_int(row.get("match_score")) >= STRONG_SCORE]
            docs_only = CONCEPT_SPECS[requirement].get("documentation_only", False)
            if docs_only:
                status = "documentation_and_raw_review_required_no_variable_shortlist"
            elif strong:
                status = "official_metadata_strong_candidates_present_raw_review_required"
            elif candidates:
                status = "official_metadata_weak_candidates_present_raw_review_required"
            else:
                status = "no_official_metadata_variable_candidate_found_raw_review_required"
            rows.append(
                {
                    "download_priority_order": queue.get("download_priority_order", ""),
                    "queue_role": queue.get("queue_role", ""),
                    "country": queue.get("country", ""),
                    "wave": queue.get("wave", ""),
                    "idno": idno,
                    "requirement": requirement,
                    "candidate_variable_rows": str(len(candidates)),
                    "strong_candidate_variable_rows": str(len(strong)),
                    "candidate_file_rows": str(len(set(file_names))),
                    "top_file_names": compact(file_names, 10),
                    "coverage_status": status,
                    "raw_value_verification_status": "not_raw_value_verified",
                    "promotion_guardrail": "official metadata coverage is pre-review evidence only; raw package verification remains required",
                }
            )
    return rows


def build_file_shortlist(matrix_rows: list[dict[str, str]]) -> list[dict[str, str]]:
    groups: dict[tuple[str, str, str], list[dict[str, str]]] = defaultdict(list)
    queue_lookup = {row.get("idno", ""): row for row in read_csv_dicts(QUEUE_PATH)}
    for row in matrix_rows:
        groups[(row.get("idno", ""), row.get("requirement", ""), row.get("file_id", ""))].append(row)

    rows: list[dict[str, str]] = []
    by_dataset_requirement: dict[tuple[str, str], list[tuple[str, list[dict[str, str]]]]] = defaultdict(list)
    for (idno, requirement, file_id), candidates in groups.items():
        by_dataset_requirement[(idno, requirement)].append((file_id, candidates))

    for (idno, requirement), file_groups in by_dataset_requirement.items():
        queue = queue_lookup.get(idno, {})
        ranked = sorted(
            file_groups,
            key=lambda item: (
                -sum(safe_int(row.get("match_score")) for row in item[1]),
                -len(item[1]),
                item[0],
            ),
        )
        for rank, (file_id, candidates) in enumerate(ranked[:TOP_FILES_PER_REQUIREMENT], start=1):
            first = candidates[0]
            strong = [row for row in candidates if safe_int(row.get("match_score")) >= STRONG_SCORE]
            rows.append(
                {
                    "download_priority_order": queue.get("download_priority_order", ""),
                    "queue_role": queue.get("queue_role", ""),
                    "country": queue.get("country", ""),
                    "wave": queue.get("wave", ""),
                    "idno": idno,
                    "requirement": requirement,
                    "file_rank": str(rank),
                    "file_id": file_id,
                    "file_name": first.get("file_name", ""),
                    "file_description": first.get("file_description", ""),
                    "candidate_variable_rows": str(len(candidates)),
                    "strong_candidate_variable_rows": str(len(strong)),
                    "top_variable_names": compact([row.get("variable_name", "") for row in candidates], 12),
                    "official_metadata_status": "official_public_metadata_file_candidate",
                    "raw_value_verification_status": "not_raw_value_verified",
                }
            )
    rows.sort(key=lambda row: (safe_int(row.get("download_priority_order"), 9999), row.get("requirement", ""), safe_int(row.get("file_rank"), 9999)))
    return rows


def write_handoffs(coverage_rows: list[dict[str, str]], file_rows: list[dict[str, str]]) -> int:
    by_idno: dict[str, list[dict[str, str]]] = defaultdict(list)
    files_by_idno: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in coverage_rows:
        by_idno[row.get("idno", "")].append(row)
    for row in file_rows:
        files_by_idno[row.get("idno", "")].append(row)
    count = 0
    for idno, rows in by_idno.items():
        first = rows[0]
        folder = RAW_ROOT / idno
        folder.mkdir(parents=True, exist_ok=True)
        path = folder / "_PRIORITY_LSMS_ISA_VARIABLE_EVIDENCE.md"
        lines = [
            "# Priority LSMS-ISA Variable Evidence",
            "",
            f"Dataset: {idno} - {first.get('country', '')} {first.get('wave', '')}",
            "",
            "Status: official public metadata candidate variables only.",
            "",
            "## Requirement Coverage",
            "",
            "| Requirement | Candidate variables | Strong candidates | Candidate files | Status |",
            "|---|---:|---:|---:|---|",
        ]
        for row in rows:
            lines.append(
                f"| {row.get('requirement', '')} | {row.get('candidate_variable_rows', '0')} | {row.get('strong_candidate_variable_rows', '0')} | {row.get('candidate_file_rows', '0')} | {row.get('coverage_status', '')} |"
            )
        lines.extend(
            [
                "",
                "## File Shortlist",
                "",
                "| Requirement | File | Candidate variables | Top variable names |",
                "|---|---|---:|---|",
            ]
        )
        for row in files_by_idno.get(idno, [])[:30]:
            lines.append(
                f"| {row.get('requirement', '')} | {row.get('file_name', '')} | {row.get('candidate_variable_rows', '0')} | {row.get('top_variable_names', '')} |"
            )
        lines.extend(
            [
                "",
                "Guardrail: these candidates are not raw value verification. Do not promote",
                "this wave until the original raw package confirms values, labels, units,",
                "recall periods, missing codes, skip patterns, merge keys, survey design,",
                "timing/geography, and accepted climate linkage.",
                "",
            ]
        )
        path.write_text("\n".join(lines), encoding="utf-8")
        count += 1
    return count


def build_summary(
    matrix_rows: list[dict[str, str]],
    coverage_rows: list[dict[str, str]],
    file_rows: list[dict[str, str]],
    handoff_count: int,
) -> list[dict[str, str]]:
    coverage_counts = Counter(row.get("coverage_status", "") for row in coverage_rows)
    role_counts = Counter(row.get("queue_role", "") for row in coverage_rows if row.get("requirement") == REQUIREMENTS[0])
    dataset_count = len({row.get("idno", "") for row in coverage_rows})
    non_doc_requirements = [row for row in coverage_rows if row.get("requirement") != "missing_codes_units_recall_skip_patterns"]
    strong_non_doc = [row for row in non_doc_requirements if safe_int(row.get("strong_candidate_variable_rows")) > 0]
    rows = [
        {"metric": "priority_lsms_variable_evidence_dataset_rows", "value": str(dataset_count), "interpretation": "Refocused LSMS/ISA datasets covered by official variable evidence."},
        {"metric": "priority_lsms_variable_evidence_requirement_rows", "value": str(len(coverage_rows)), "interpretation": "Requirement-by-wave coverage rows."},
        {"metric": "priority_lsms_variable_evidence_candidate_variable_rows", "value": str(len(matrix_rows)), "interpretation": "Top official public metadata candidate variables shortlisted for raw review."},
        {"metric": "priority_lsms_variable_evidence_file_shortlist_rows", "value": str(len(file_rows)), "interpretation": "Official DDI files shortlisted by concept for raw package checking."},
        {"metric": "priority_lsms_variable_evidence_strong_requirement_rows", "value": str(len(strong_non_doc)), "interpretation": "Non-documentation requirement rows with at least one strong metadata candidate."},
        {"metric": "priority_lsms_variable_evidence_documentation_only_requirement_rows", "value": str(coverage_counts.get("documentation_and_raw_review_required_no_variable_shortlist", 0)), "interpretation": "Rows where missing codes, units, recall, and skips require documentation/raw review rather than variable shortlisting."},
        {"metric": "priority_lsms_variable_evidence_no_candidate_requirement_rows", "value": str(coverage_counts.get("no_official_metadata_variable_candidate_found_raw_review_required", 0)), "interpretation": "Rows where public metadata found no variable candidate."},
        {"metric": "priority_lsms_variable_evidence_handoff_readmes_written", "value": str(handoff_count), "interpretation": "Per-wave variable-evidence handoff files written."},
        {"metric": "priority_lsms_variable_evidence_raw_value_verified_rows", "value": "0", "interpretation": "Official metadata shortlists do not verify raw values."},
        {"metric": "priority_lsms_variable_evidence_data_write_status", "value": "blocked_no_promoted_rows", "interpretation": "No country-wave may write to data/ from metadata variable evidence alone."},
        {"metric": "modeling_gate_status", "value": "blocked", "interpretation": "Models remain blocked until raw-backed promotion thresholds and accepted climate linkage pass."},
    ]
    for status, count in sorted(coverage_counts.items()):
        rows.append({"metric": f"priority_lsms_variable_evidence_coverage_status_{status}", "value": str(count), "interpretation": "Requirement coverage status count."})
    for role, count in sorted(role_counts.items()):
        rows.append({"metric": f"priority_lsms_variable_evidence_queue_role_{role}", "value": str(count), "interpretation": "Dataset count by refocused queue role."})
    return rows


def markdown_rows(rows: list[dict[str, str]], columns: list[str], limit: int = 20) -> str:
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


def write_report(
    matrix_rows: list[dict[str, str]],
    coverage_rows: list[dict[str, str]],
    file_rows: list[dict[str, str]],
    summary_rows: list[dict[str, str]],
) -> None:
    summary_table = "\n".join(f"| {row['metric']} | {row['value']} | {row['interpretation']} |" for row in summary_rows)
    no_candidate = [row for row in coverage_rows if row.get("coverage_status") == "no_official_metadata_variable_candidate_found_raw_review_required"]
    REPORT_PATH.write_text(
        f"""# Priority LSMS-ISA Variable Evidence Matrix

Status: official public metadata variable shortlist for the refocused LSMS/ISA
queue. This is a pre-review layer for raw package checking. It does not verify
raw values, units, recall periods, missing codes, skip patterns, merge keys,
survey design, timing/geography, or climate linkage.

## Summary

| Metric | Value | Interpretation |
|---|---:|---|
{summary_table}

## Requirement Coverage

{markdown_rows(coverage_rows, ['download_priority_order', 'idno', 'requirement', 'candidate_variable_rows', 'strong_candidate_variable_rows', 'candidate_file_rows', 'coverage_status'], 60)}

## No-Candidate Requirement Rows

{markdown_rows(no_candidate, ['download_priority_order', 'idno', 'requirement', 'coverage_status'], 40) if no_candidate else 'No non-documentation requirement row lacked a public-metadata variable candidate.'}

## Candidate Variable Preview

{markdown_rows(matrix_rows, ['download_priority_order', 'idno', 'requirement', 'candidate_rank', 'variable_name', 'variable_label', 'file_name', 'match_score'], 80)}

## File Shortlist Preview

{markdown_rows(file_rows, ['download_priority_order', 'idno', 'requirement', 'file_rank', 'file_name', 'candidate_variable_rows', 'top_variable_names'], 60)}

## Guardrails

- Candidate variables are metadata search hits, not accepted harmonized fields.
- OOP and care-access candidates must be checked in raw values and questionnaires.
- Missing codes, units, recall periods, and skip patterns remain documentation/raw review tasks.
- No country-wave can be promoted or written to `data/` from this evidence alone.

## Machine-Readable Outputs

- `temp/priority_lsms_isa_variable_evidence_matrix.csv`
- `temp/priority_lsms_isa_requirement_variable_coverage.csv`
- `temp/priority_lsms_isa_concept_file_shortlist.csv`
- `result/priority_lsms_isa_variable_evidence_summary.csv`
""",
        encoding="utf-8",
    )


def main() -> None:
    ensure_dirs()
    matrix_rows = build_matrix_rows()
    coverage_rows = build_coverage_rows(matrix_rows)
    file_rows = build_file_shortlist(matrix_rows)
    handoff_count = write_handoffs(coverage_rows, file_rows)
    summary_rows = build_summary(matrix_rows, coverage_rows, file_rows, handoff_count)
    write_csv(MATRIX_PATH, matrix_rows, MATRIX_COLUMNS)
    write_csv(COVERAGE_PATH, coverage_rows, COVERAGE_COLUMNS)
    write_csv(FILE_SHORTLIST_PATH, file_rows, FILE_SHORTLIST_COLUMNS)
    write_csv(SUMMARY_PATH, summary_rows, SUMMARY_COLUMNS)
    write_report(matrix_rows, coverage_rows, file_rows, summary_rows)
    append_log(
        TEMP_DIR / "audit_log.md",
        f"Built priority LSMS/ISA variable evidence matrix variables={len(matrix_rows)} requirements={len(coverage_rows)} files={len(file_rows)}.",
    )
    print(f"Priority LSMS/ISA variable evidence variables={len(matrix_rows)} requirements={len(coverage_rows)} files={len(file_rows)}.")


if __name__ == "__main__":
    main()
