from __future__ import annotations

import csv
import json
import xml.etree.ElementTree as ET
from collections import Counter, defaultdict
from pathlib import Path, PurePosixPath
from typing import Any

from common import PROJECT_ROOT, REPORT_DIR, RESULT_DIR, TEMP_DIR, append_log, ensure_dirs, write_csv


VALUE_PROFILE_PATH = TEMP_DIR / "priority_lsms_isa_received_raw_value_profile.csv"
KEY_PROFILE_PATH = TEMP_DIR / "priority_lsms_isa_received_raw_key_design_geography_profile.csv"
RECEIPT_VALIDATION_PATH = TEMP_DIR / "priority_lsms_isa_official_file_receipt_validation.csv"

VARIABLE_REVIEW_PATH = TEMP_DIR / "priority_lsms_isa_received_raw_semantics_variable_review.csv"
REQUIREMENT_REVIEW_PATH = TEMP_DIR / "priority_lsms_isa_received_raw_semantics_requirement_review.csv"
DOCUMENTATION_SCOPE_PATH = TEMP_DIR / "priority_lsms_isa_received_raw_documentation_scope_review.csv"
SUMMARY_PATH = RESULT_DIR / "priority_lsms_isa_received_raw_semantics_review_summary.csv"
REPORT_PATH = REPORT_DIR / "priority_lsms_isa_received_raw_semantics_review.md"

DOC_ROOT = TEMP_DIR / "source_snapshots" / "priority_lsms_isa_public_documentation"
DDI_BY_IDNO = {
    "MWI_2004_IHS-II_v01_M": DOC_ROOT / "3_MWI_2004_IHS-II_v01_M" / "ddi_metadata.xml",
}
CATALOG_BY_IDNO = {
    "MWI_2004_IHS-II_v01_M": DOC_ROOT / "3_MWI_2004_IHS-II_v01_M" / "catalog_idno_json.json",
}

VARIABLE_REVIEW_COLUMNS = [
    "download_priority_order",
    "queue_role",
    "country",
    "wave",
    "idno",
    "review_source",
    "requirement",
    "actual_member_name",
    "variable_name",
    "variable_role",
    "raw_variable_label",
    "ddi_file_name",
    "ddi_file_content",
    "ddi_variable_label",
    "ddi_interval_type",
    "ddi_format_type",
    "ddi_valid_count",
    "ddi_invalid_count",
    "ddi_range_min",
    "ddi_range_max",
    "ddi_category_count",
    "ddi_categories_preview",
    "raw_row_count",
    "raw_nonmissing_count",
    "raw_missing_count",
    "raw_distinct_nonmissing_count",
    "raw_numeric_min",
    "raw_numeric_max",
    "raw_top_values",
    "raw_possible_missing_codes",
    "raw_detected_recall_period",
    "raw_detected_unit_or_scale",
    "raw_possible_skip_pattern",
    "documentation_recall_period",
    "documentation_unit_or_scale",
    "documentation_missing_code_evidence",
    "documentation_skip_evidence",
    "documentation_level_evidence",
    "raw_vs_ddi_count_status",
    "raw_vs_ddi_range_status",
    "semantics_review_status",
    "remaining_manual_review",
]

REQUIREMENT_REVIEW_COLUMNS = [
    "download_priority_order",
    "queue_role",
    "country",
    "wave",
    "idno",
    "requirement",
    "semantics_variable_rows",
    "raw_profile_variable_rows",
    "utility_profile_variable_rows",
    "ddi_documented_variable_rows",
    "variables_with_categories",
    "variables_with_valid_ranges",
    "documentation_recall_periods",
    "documentation_units_or_scales",
    "documentation_missing_code_variables",
    "documentation_skip_pattern_variables",
    "documentation_level_evidence",
    "study_level_evidence",
    "semantics_requirement_status",
    "remaining_manual_review",
]

DOCUMENTATION_SCOPE_COLUMNS = [
    "download_priority_order",
    "queue_role",
    "country",
    "wave",
    "idno",
    "documentation_domain",
    "documentation_evidence",
    "source_path",
    "review_status",
]

SUMMARY_COLUMNS = ["metric", "value", "interpretation"]


def read_csv_dicts(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        return []
    with path.open(encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def clean(value: Any) -> str:
    return "" if value is None else str(value).strip()


def compact(value: Any, limit: int = 280) -> str:
    text = " ".join(clean(value).replace("|", "/").split())
    return text[: limit - 3] + "..." if len(text) > limit else text


def safe_int(value: Any, default: int = 0) -> int:
    try:
        text = clean(value)
        return int(float(text)) if text else default
    except (TypeError, ValueError):
        return default


def safe_float(value: Any) -> float | None:
    try:
        text = clean(value)
        return float(text) if text else None
    except (TypeError, ValueError):
        return None


def rel(path: Path) -> str:
    try:
        return str(path.relative_to(PROJECT_ROOT)).replace("\\", "/")
    except ValueError:
        return str(path).replace("\\", "/")


def file_key(value: str) -> str:
    name = PurePosixPath(clean(value).replace("\\", "/")).name.lower()
    if name.endswith(".nsdstat"):
        return name[: -len(".nsdstat")] + ".dta"
    return name


def parse_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def text_of(element: ET.Element | None) -> str:
    if element is None:
        return ""
    return compact(" ".join(element.itertext()))


def find_child(element: ET.Element, path: str, ns: dict[str, str]) -> ET.Element | None:
    return element.find("/".join(f"d:{part}" for part in path.split("/")), ns)


def parse_ddi(path: Path) -> tuple[dict[str, dict[str, str]], dict[tuple[str, str], dict[str, str]]]:
    if not path.exists():
        return {}, {}
    tree = ET.parse(path)
    root = tree.getroot()
    ns = {"d": "http://www.icpsr.umich.edu/DDI"}
    files_by_id: dict[str, dict[str, str]] = {}
    for file_dscr in root.findall(".//d:fileDscr", ns):
        file_id = clean(file_dscr.attrib.get("ID"))
        file_name = text_of(find_child(file_dscr, "fileTxt/fileName", ns))
        files_by_id[file_id] = {
            "ddi_file_id": file_id,
            "ddi_file_name": file_name,
            "ddi_file_key": file_key(file_name),
            "ddi_file_content": text_of(find_child(file_dscr, "fileTxt/fileCont", ns)),
            "ddi_case_qty": text_of(find_child(file_dscr, "fileTxt/dimensns/caseQnty", ns)),
            "ddi_var_qty": text_of(find_child(file_dscr, "fileTxt/dimensns/varQnty", ns)),
        }

    variables: dict[tuple[str, str], dict[str, str]] = {}
    for var in root.findall(".//d:var", ns):
        file_id = clean(var.attrib.get("files")).split()[0]
        file_row = files_by_id.get(file_id, {})
        var_name = clean(var.attrib.get("name"))
        if not var_name or not file_row:
            continue
        categories: list[str] = []
        for cat in var.findall("d:catgry", ns)[:12]:
            value = text_of(cat.find("d:catValu", ns))
            label = text_of(cat.find("d:labl", ns))
            stat = text_of(cat.find("d:catStat", ns))
            bit = value
            if label:
                bit = f"{bit}={label}"
            if stat:
                bit = f"{bit}:{stat}"
            if bit:
                categories.append(bit)
        ranges = []
        for rng in var.findall("d:valrng/d:range", ns):
            ranges.append(
                {
                    "min": clean(rng.attrib.get("min")),
                    "max": clean(rng.attrib.get("max")),
                    "units": clean(rng.attrib.get("UNITS")),
                }
            )
        first_range = ranges[0] if ranges else {}
        sum_stats = {clean(s.attrib.get("type")): text_of(s) for s in var.findall("d:sumStat", ns)}
        fmt = var.find("d:varFormat", ns)
        row = {
            **file_row,
            "ddi_variable_label": text_of(var.find("d:labl", ns)),
            "ddi_interval_type": clean(var.attrib.get("intrvl")),
            "ddi_format_type": clean(fmt.attrib.get("type")) if fmt is not None else "",
            "ddi_valid_count": clean(sum_stats.get("vald")),
            "ddi_invalid_count": clean(sum_stats.get("invd")),
            "ddi_range_min": clean(first_range.get("min")),
            "ddi_range_max": clean(first_range.get("max")),
            "ddi_range_units": clean(first_range.get("units")),
            "ddi_category_count": str(len(var.findall("d:catgry", ns))),
            "ddi_categories_preview": "; ".join(categories),
        }
        variables[(file_row["ddi_file_key"], var_name.lower())] = row
    return files_by_id, variables


def catalog_metadata(path: Path) -> dict[str, Any]:
    obj = parse_json(path)
    return (((obj.get("dataset") or {}).get("metadata") or {}).get("study_desc") or {})


def nested_text(obj: Any) -> str:
    if isinstance(obj, str):
        return obj
    if isinstance(obj, list):
        return " ".join(nested_text(item) for item in obj)
    if isinstance(obj, dict):
        return " ".join(nested_text(v) for v in obj.values())
    return clean(obj)


def study_scope_rows(receipt: dict[str, str], catalog_path: Path) -> list[dict[str, str]]:
    study = catalog_metadata(catalog_path)
    info = study.get("study_info") or {}
    method = ((info.get("method") or {}).get("data_collection") or {})
    sum_dscr = info.get("sumDscr") or {}
    coll_dates = sum_dscr.get("coll_dates") or []
    if not coll_dates and isinstance(info.get("coll_dates"), list):
        coll_dates = info.get("coll_dates") or []
    date_text = "; ".join(
        f"{clean(row.get('start'))}-{clean(row.get('end'))}" if isinstance(row, dict) else clean(row)
        for row in coll_dates
    )
    source = rel(catalog_path) if catalog_path.exists() else ""
    base = {
        "download_priority_order": clean(receipt.get("download_priority_order")),
        "queue_role": clean(receipt.get("queue_role")),
        "country": clean(receipt.get("country")),
        "wave": clean(receipt.get("wave")),
        "idno": clean(receipt.get("idno")),
        "source_path": source,
        "review_status": "official_metadata_available" if source else "missing_official_metadata",
    }
    rows = [
        {**base, "documentation_domain": "collection_period", "documentation_evidence": compact(date_text or nested_text(sum_dscr.get("collDate")))},
        {**base, "documentation_domain": "analysis_unit", "documentation_evidence": compact(nested_text(sum_dscr.get("anlyUnit") or info.get("analysis_unit")))},
        {**base, "documentation_domain": "geographic_coverage", "documentation_evidence": compact(nested_text(sum_dscr.get("geogCover") or info.get("geog_coverage")))},
        {**base, "documentation_domain": "sampling_design", "documentation_evidence": compact(nested_text(method.get("sampling_procedure") or method.get("sampProc")), 900)},
        {**base, "documentation_domain": "research_instrument", "documentation_evidence": compact(nested_text(method.get("research_instrument") or method.get("resInstru")), 900)},
        {**base, "documentation_domain": "survey_topics_and_recall_modules", "documentation_evidence": compact(nested_text(info.get("notes")), 900)},
    ]
    return rows


def detect_recall(*texts: str) -> str:
    low = " ".join(texts).lower()
    hits: list[str] = []
    checks = [
        ("past_2_weeks", ["past 2 weeks", "past two weeks"]),
        ("past_4_weeks", ["past 4 wks", "past 4 weeks", "past four weeks"]),
        ("past_3_days", ["past three days", "past 3 days"]),
        ("past_week", ["past one week", "past 1 week", "past week"]),
        ("past_month", ["past month", "one month"]),
        ("past_3_months", ["past three months", "past 3 months"]),
        ("past_12_months", ["past twelve months", "past 12 months", "past year"]),
        ("interview_month", ["month of interview"]),
        ("interview_date", ["interview date"]),
        ("collection_period_2004_03_to_2005_03", ["2004-03", "2005-03"]),
    ]
    for name, needles in checks:
        if any(needle in low for needle in needles):
            hits.append(name)
    return "; ".join(dict.fromkeys(hits))


def detect_unit(*texts: str) -> str:
    low = " ".join(texts).lower()
    hits: list[str] = []
    if any(token in low for token in ["how much", "spent", "spend", "paid", "cost", "expenditure", "income", "consumption"]):
        hits.append("money_amount_local_currency_needs_malawi_kwacha_confirmation")
    if "price" in low and "mk" in low:
        hits.append("price_malawi_kwacha")
    if "distance" in low or "how far" in low:
        hits.append("distance_unit_pair_or_code_needs_category_check")
    if "unit" in low:
        hits.append("unit_variable")
    if "weight" in low:
        hits.append("survey_weight")
    if "month" in low:
        hits.append("month")
    if "year" in low:
        hits.append("year")
    return "; ".join(dict.fromkeys(hits))


def detect_missing(ddi: dict[str, str], raw_possible: str) -> str:
    hits: list[str] = []
    invalid = safe_int(ddi.get("ddi_invalid_count"))
    if invalid > 0:
        hits.append(f"ddi_invalid_count={invalid}")
    categories = ddi.get("ddi_categories_preview", "").lower()
    for needle in ["missing", "refus", "don't know", "dont know", "not applicable", "other"]:
        if needle in categories:
            token = needle.replace(" ", "_").replace("'", "")
            hits.append(f"ddi_category_contains_{token}")
            break
    if raw_possible:
        hits.append(f"raw_possible_codes={raw_possible}")
    return "; ".join(dict.fromkeys(hits))


def detect_skip(row: dict[str, str], ddi: dict[str, str], profile_skip: str) -> str:
    hits: list[str] = []
    raw_row_count = safe_int(row.get("row_count"))
    nonmissing = safe_int(row.get("nonmissing_count"))
    if raw_row_count and nonmissing < raw_row_count:
        hits.append("raw_conditional_nonmissing")
    label_text = f"{row.get('raw_variable_label', '')} {ddi.get('ddi_variable_label', '')}".lower()
    if any(token in label_text for token in ["if ", "did you", "have you", "under", "over", "which ", "why "]):
        hits.append("question_text_suggests_skip_or_universe")
    if profile_skip:
        hits.append(profile_skip)
    return "; ".join(dict.fromkeys(hits))


def level_evidence(row: dict[str, str], ddi: dict[str, str], source: str) -> str:
    member = row.get("actual_member_name", "")
    file_content = ddi.get("ddi_file_content", "")
    count = safe_int(row.get("row_count"))
    distinct = safe_int(row.get("distinct_nonmissing_count"))
    variable = row.get("variable_name", "").lower()
    role = row.get("variable_role", "")
    bits = []
    if "module d: health" in file_content.lower() or member.lower() == "sec_d.dta":
        bits.append("health_module_person_level_or_roster_linked")
    if "module b: household roster" in file_content.lower() or member.lower() == "sec_b.dta":
        bits.append("household_roster_person_level")
    if count == 11280:
        bits.append("household_level_11280_rows")
    elif count and distinct == 11280 and variable == "case_id":
        bits.append("household_key_repeated_across_person_item_rows")
    if "key" in role and row.get("duplicate_if_key_count") == "0":
        bits.append("unique_at_file_level")
    elif "key" in role and safe_int(row.get("duplicate_if_key_count")) > 0:
        bits.append("requires_secondary_member_or_item_key")
    if source == "utility_profile" and ("geography" in role or "cluster" in role):
        bits.append("geography_linkage_candidate_not_coordinates")
    return "; ".join(dict.fromkeys(bits))


def compare_counts(row: dict[str, str], ddi: dict[str, str]) -> str:
    raw_count = safe_int(row.get("row_count"))
    ddi_count = safe_int(ddi.get("ddi_valid_count"))
    if not raw_count or not ddi_count:
        return "count_comparison_not_available"
    if raw_count == ddi_count:
        return "raw_row_count_matches_ddi_valid_count"
    return f"raw_row_count_differs_from_ddi_valid_count raw={raw_count} ddi_valid={ddi_count}"


def compare_ranges(row: dict[str, str], ddi: dict[str, str]) -> str:
    raw_min = safe_float(row.get("numeric_min"))
    raw_max = safe_float(row.get("numeric_max"))
    ddi_min = safe_float(ddi.get("ddi_range_min"))
    ddi_max = safe_float(ddi.get("ddi_range_max"))
    if raw_min is None or raw_max is None or ddi_min is None or ddi_max is None:
        return "range_comparison_not_available"
    if abs(raw_min - ddi_min) < 1e-6 and abs(raw_max - ddi_max) < 1e-6:
        return "raw_range_matches_ddi_range"
    if raw_min >= ddi_min and raw_max <= ddi_max:
        return "raw_range_within_ddi_range"
    return f"raw_range_outside_ddi_range raw={raw_min:g}-{raw_max:g} ddi={ddi_min:g}-{ddi_max:g}"


def base_receipts() -> dict[str, dict[str, str]]:
    return {clean(row.get("idno")): row for row in read_csv_dicts(RECEIPT_VALIDATION_PATH) if clean(row.get("idno"))}


def variable_review_rows(
    value_rows: list[dict[str, str]],
    key_rows: list[dict[str, str]],
    ddi_variables: dict[str, dict[tuple[str, str], dict[str, str]]],
) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    combined: list[tuple[str, dict[str, str]]] = [("raw_value_profile", row) for row in value_rows]
    combined.extend(("utility_profile", row) for row in key_rows)
    for source, row in combined:
        idno = clean(row.get("idno"))
        member = clean(row.get("actual_member_name"))
        variable = clean(row.get("variable_name"))
        ddi = ddi_variables.get(idno, {}).get((file_key(member), variable.lower()), {})
        raw_label = clean(row.get("raw_variable_label"))
        ddi_label = clean(ddi.get("ddi_variable_label"))
        file_context = ddi.get("ddi_file_content", "") if source == "raw_value_profile" else ""
        recall = detect_recall(raw_label, ddi_label, file_context, row.get("raw_detected_recall_period", ""))
        unit = detect_unit(raw_label, ddi_label, file_context, row.get("raw_detected_unit_or_scale", ""))
        missing = detect_missing(ddi, clean(row.get("possible_missing_codes") or row.get("raw_possible_missing_codes")))
        skip = detect_skip(row, ddi, clean(row.get("possible_skip_pattern") or row.get("raw_possible_skip_pattern")))
        level = level_evidence(row, ddi, source)
        documented = "1" if ddi else "0"
        rows.append(
            {
                "download_priority_order": clean(row.get("download_priority_order")),
                "queue_role": clean(row.get("queue_role")),
                "country": clean(row.get("country")),
                "wave": clean(row.get("wave")),
                "idno": idno,
                "review_source": source,
                "requirement": clean(row.get("requirement")) or role_to_requirement(row.get("variable_role", "")),
                "actual_member_name": member,
                "variable_name": variable,
                "variable_role": clean(row.get("variable_role")),
                "raw_variable_label": raw_label,
                "ddi_file_name": clean(ddi.get("ddi_file_name")),
                "ddi_file_content": clean(ddi.get("ddi_file_content")),
                "ddi_variable_label": ddi_label,
                "ddi_interval_type": clean(ddi.get("ddi_interval_type")),
                "ddi_format_type": clean(ddi.get("ddi_format_type")),
                "ddi_valid_count": clean(ddi.get("ddi_valid_count")),
                "ddi_invalid_count": clean(ddi.get("ddi_invalid_count")),
                "ddi_range_min": clean(ddi.get("ddi_range_min")),
                "ddi_range_max": clean(ddi.get("ddi_range_max")),
                "ddi_category_count": clean(ddi.get("ddi_category_count")),
                "ddi_categories_preview": clean(ddi.get("ddi_categories_preview")),
                "raw_row_count": clean(row.get("row_count")),
                "raw_nonmissing_count": clean(row.get("nonmissing_count")),
                "raw_missing_count": clean(row.get("missing_count")),
                "raw_distinct_nonmissing_count": clean(row.get("distinct_nonmissing_count")),
                "raw_numeric_min": clean(row.get("numeric_min")),
                "raw_numeric_max": clean(row.get("numeric_max")),
                "raw_top_values": clean(row.get("top_values")),
                "raw_possible_missing_codes": clean(row.get("possible_missing_codes")),
                "raw_detected_recall_period": clean(row.get("detected_recall_period")),
                "raw_detected_unit_or_scale": clean(row.get("detected_unit_or_scale")),
                "raw_possible_skip_pattern": clean(row.get("possible_skip_pattern")),
                "documentation_recall_period": recall,
                "documentation_unit_or_scale": unit,
                "documentation_missing_code_evidence": missing,
                "documentation_skip_evidence": skip,
                "documentation_level_evidence": level,
                "raw_vs_ddi_count_status": compare_counts(row, ddi),
                "raw_vs_ddi_range_status": compare_ranges(row, ddi),
                "semantics_review_status": "semantics_evidence_available_not_value_verified" if documented == "1" else "missing_ddi_documentation_for_profiled_variable",
                "remaining_manual_review": "confirm questionnaire skip universe, units, missing codes, recall period, merge level, and promotion decision before accepting",
            }
        )
    return rows


def role_to_requirement(role: str) -> str:
    if "weight" in role or "survey_design" in role:
        return "weights_and_design"
    if "key" in role:
        return "household_person_keys"
    if "geography" in role or "cluster" in role or "urban_rural" in role:
        return "climate_geography"
    return "missing_codes_units_recall_skip_patterns"


def requirement_review_rows(
    variable_rows: list[dict[str, str]],
    doc_rows: list[dict[str, str]],
    receipts: dict[str, dict[str, str]],
) -> list[dict[str, str]]:
    grouped: dict[tuple[str, str], list[dict[str, str]]] = defaultdict(list)
    for row in variable_rows:
        req = clean(row.get("requirement")) or "missing_codes_units_recall_skip_patterns"
        grouped[(clean(row.get("idno")), req)].append(row)

    for idno in {row.get("idno", "") for row in variable_rows}:
        all_rows = [row for row in variable_rows if row.get("idno") == idno]
        if all_rows:
            grouped[(idno, "missing_codes_units_recall_skip_patterns")] = list(all_rows)

    study_by_id: dict[str, dict[str, str]] = defaultdict(dict)
    for row in doc_rows:
        study_by_id[clean(row.get("idno"))][clean(row.get("documentation_domain"))] = clean(row.get("documentation_evidence"))

    rows: list[dict[str, str]] = []
    for (idno, requirement), vars_for_req in sorted(grouped.items()):
        receipt = receipts.get(idno, {})
        recall = sorted({clean(row.get("documentation_recall_period")) for row in vars_for_req if clean(row.get("documentation_recall_period"))})
        units = sorted({clean(row.get("documentation_unit_or_scale")) for row in vars_for_req if clean(row.get("documentation_unit_or_scale"))})
        missing_vars = sorted({row.get("variable_name", "") for row in vars_for_req if clean(row.get("documentation_missing_code_evidence"))})
        skip_vars = sorted({row.get("variable_name", "") for row in vars_for_req if clean(row.get("documentation_skip_evidence"))})
        level = sorted({clean(row.get("documentation_level_evidence")) for row in vars_for_req if clean(row.get("documentation_level_evidence"))})
        study = study_by_id.get(idno, {})
        study_bits = []
        if requirement == "survey_timing":
            study_bits.append(study.get("collection_period", ""))
        if requirement in {"weights_and_design", "climate_geography"}:
            study_bits.append(study.get("sampling_design", ""))
            study_bits.append(study.get("geographic_coverage", ""))
        if requirement in {"consumption_or_income", "oop_health_expenditure"}:
            study_bits.append(study.get("survey_topics_and_recall_modules", ""))
        if requirement == "missing_codes_units_recall_skip_patterns":
            study_bits.extend([study.get("research_instrument", ""), study.get("survey_topics_and_recall_modules", "")])
        rows.append(
            {
                "download_priority_order": clean(receipt.get("download_priority_order")) or clean(vars_for_req[0].get("download_priority_order")),
                "queue_role": clean(receipt.get("queue_role")) or clean(vars_for_req[0].get("queue_role")),
                "country": clean(receipt.get("country")) or clean(vars_for_req[0].get("country")),
                "wave": clean(receipt.get("wave")) or clean(vars_for_req[0].get("wave")),
                "idno": idno,
                "requirement": requirement,
                "semantics_variable_rows": str(len(vars_for_req)),
                "raw_profile_variable_rows": str(sum(1 for row in vars_for_req if row.get("review_source") == "raw_value_profile")),
                "utility_profile_variable_rows": str(sum(1 for row in vars_for_req if row.get("review_source") == "utility_profile")),
                "ddi_documented_variable_rows": str(sum(1 for row in vars_for_req if row.get("semantics_review_status") == "semantics_evidence_available_not_value_verified")),
                "variables_with_categories": str(sum(1 for row in vars_for_req if safe_int(row.get("ddi_category_count")) > 0)),
                "variables_with_valid_ranges": str(sum(1 for row in vars_for_req if clean(row.get("ddi_range_min")) or clean(row.get("ddi_range_max")))),
                "documentation_recall_periods": "; ".join(recall),
                "documentation_units_or_scales": "; ".join(units),
                "documentation_missing_code_variables": "; ".join(missing_vars[:40]),
                "documentation_skip_pattern_variables": "; ".join(skip_vars[:40]),
                "documentation_level_evidence": "; ".join(level[:20]),
                "study_level_evidence": compact(" ".join(bit for bit in study_bits if bit), 900),
                "semantics_requirement_status": "semantics_review_available_not_value_verified",
                "remaining_manual_review": "review PDF/questionnaire wording and fill acceptance fields before any raw-value verification or promotion",
            }
        )
    return rows


def summarize(variable_rows: list[dict[str, str]], requirement_rows: list[dict[str, str]], doc_rows: list[dict[str, str]]) -> list[dict[str, str]]:
    dataset_ids = {row.get("idno", "") for row in variable_rows if row.get("idno")}
    status_counts = Counter(row.get("semantics_review_status", "") for row in variable_rows)
    req_counts = Counter(row.get("semantics_requirement_status", "") for row in requirement_rows)
    rows = [
        {"metric": "priority_lsms_received_raw_semantics_dataset_rows", "value": str(len(dataset_ids)), "interpretation": "Datasets with received raw semantics review evidence."},
        {"metric": "priority_lsms_received_raw_semantics_variable_rows", "value": str(len(variable_rows)), "interpretation": "Variable-level semantics review rows from value and utility profiles."},
        {"metric": "priority_lsms_received_raw_semantics_ddi_documented_variable_rows", "value": str(sum(1 for row in variable_rows if row.get("semantics_review_status") == "semantics_evidence_available_not_value_verified")), "interpretation": "Profiled variables matched to official DDI documentation."},
        {"metric": "priority_lsms_received_raw_semantics_requirement_rows", "value": str(len(requirement_rows)), "interpretation": "Requirement-level semantics review rows."},
        {"metric": "priority_lsms_received_raw_semantics_documentation_scope_rows", "value": str(len(doc_rows)), "interpretation": "Study-level documentation scope rows."},
        {"metric": "priority_lsms_received_raw_semantics_missing_codes_units_recall_skip_requirement_rows", "value": str(sum(1 for row in requirement_rows if row.get("requirement") == "missing_codes_units_recall_skip_patterns")), "interpretation": "Documentation-semantics gate rows now backed by review evidence."},
        {"metric": "priority_lsms_received_raw_semantics_raw_value_verified_rows", "value": "0", "interpretation": "Semantics review does not value-verify any country-wave."},
        {"metric": "priority_lsms_received_raw_semantics_data_write_status", "value": "blocked_semantics_review_only", "interpretation": "Semantics review evidence does not write promoted analysis data."},
        {"metric": "modeling_gate_status", "value": "blocked", "interpretation": "Models remain blocked until promoted registry thresholds and climate linkage pass."},
    ]
    for status, count in sorted(status_counts.items()):
        rows.append({"metric": f"priority_lsms_received_raw_semantics_status_{status}", "value": str(count), "interpretation": "Variable-level semantics review status count."})
    for status, count in sorted(req_counts.items()):
        rows.append({"metric": f"priority_lsms_received_raw_semantics_requirement_status_{status}", "value": str(count), "interpretation": "Requirement-level semantics review status count."})
    return rows


def markdown_table(rows: list[dict[str, str]], columns: list[str], limit: int = 30) -> str:
    lines = ["| " + " | ".join(columns) + " |", "|" + "|".join("---" for _ in columns) + "|"]
    for row in rows[:limit]:
        lines.append("| " + " | ".join(compact(row.get(column), 120) for column in columns) + " |")
    return "\n".join(lines)


def write_handoffs(receipts: dict[str, dict[str, str]], requirement_rows: list[dict[str, str]], variable_rows: list[dict[str, str]]) -> int:
    written = 0
    for idno, receipt in sorted(receipts.items()):
        reqs = [row for row in requirement_rows if row.get("idno") == idno]
        vars_for_id = [row for row in variable_rows if row.get("idno") == idno]
        if not reqs:
            continue
        folder = PROJECT_ROOT / clean(receipt.get("local_target_folder")).replace("/", "\\")
        folder.mkdir(parents=True, exist_ok=True)
        path = folder / "_PRIORITY_LSMS_ISA_RECEIVED_RAW_SEMANTICS_REVIEW.md"
        path.write_text(
            f"""# Priority LSMS-ISA Received Raw Semantics Review

IDNO: `{idno}`

Country-wave: {receipt.get('country', '')} {receipt.get('wave', '')}

Status: official DDI/metadata semantics have been aligned to the received raw
value-profile. This is a review prefill, not raw-value verification.

## Requirement Review

{markdown_table(reqs, ['requirement', 'semantics_variable_rows', 'ddi_documented_variable_rows', 'documentation_recall_periods', 'documentation_units_or_scales', 'semantics_requirement_status'], 20)}

## Selected Variable Review

{markdown_table(vars_for_id, ['requirement', 'actual_member_name', 'variable_name', 'ddi_file_content', 'documentation_recall_period', 'documentation_unit_or_scale', 'documentation_skip_evidence', 'raw_vs_ddi_range_status'], 80)}

## Remaining Gate Meaning

The missing-code/unit/recall/skip gate now has structured evidence, but it
remains unaccepted until a reviewer checks questionnaire/PDF wording and fills
the raw-value workbook acceptance fields.
""",
            encoding="utf-8",
        )
        written += 1
    return written


def write_report(variable_rows: list[dict[str, str]], requirement_rows: list[dict[str, str]], doc_rows: list[dict[str, str]], summary_rows: list[dict[str, str]]) -> None:
    summary_table = "\n".join(f"| {row['metric']} | {row['value']} | {row['interpretation']} |" for row in summary_rows)
    REPORT_PATH.write_text(
        f"""# Priority LSMS-ISA Received Raw Semantics Review

Status: official DDI/catalog semantics aligned to received raw value-profile
evidence. No raw microdata are persisted and no country-wave is promoted by
this review.

## Summary

| metric | value | interpretation |
|---|---:|---|
{summary_table}

## Documentation Scope

{markdown_table(doc_rows, ['documentation_domain', 'documentation_evidence', 'review_status'], 20)}

## Requirement Review

{markdown_table(requirement_rows, ['country', 'wave', 'idno', 'requirement', 'semantics_variable_rows', 'ddi_documented_variable_rows', 'documentation_recall_periods', 'documentation_units_or_scales', 'semantics_requirement_status'], 40)}

## Selected Variable Review

{markdown_table(variable_rows, ['review_source', 'requirement', 'actual_member_name', 'variable_name', 'ddi_file_content', 'documentation_recall_period', 'documentation_unit_or_scale', 'documentation_missing_code_evidence', 'documentation_skip_evidence', 'semantics_review_status'], 80)}

## Interpretation

The audit advances Malawi 2004 from value-profile evidence to structured
documentation-semantics review. It still does not accept any variable or
requirement. Promotion remains blocked until reviewer acceptance, harmonized
outcome construction, and climate-linkage evidence pass.
""",
        encoding="utf-8",
    )


def main() -> None:
    ensure_dirs()
    receipts = base_receipts()
    value_rows = read_csv_dicts(VALUE_PROFILE_PATH)
    key_rows = read_csv_dicts(KEY_PROFILE_PATH)
    ddi_vars_by_id: dict[str, dict[tuple[str, str], dict[str, str]]] = {}
    doc_rows: list[dict[str, str]] = []
    for idno, receipt in receipts.items():
        ddi_path = DDI_BY_IDNO.get(idno)
        _, vars_by_key = parse_ddi(ddi_path) if ddi_path and ddi_path.exists() else ({}, {})
        ddi_vars_by_id[idno] = vars_by_key
        catalog_path = CATALOG_BY_IDNO.get(idno)
        if catalog_path and catalog_path.exists():
            doc_rows.extend(study_scope_rows(receipt, catalog_path))

    variable_rows = variable_review_rows(value_rows, key_rows, ddi_vars_by_id)
    requirement_rows = requirement_review_rows(variable_rows, doc_rows, receipts)
    handoff_count = write_handoffs(receipts, requirement_rows, variable_rows)
    summary_rows = summarize(variable_rows, requirement_rows, doc_rows)
    summary_rows.append({"metric": "priority_lsms_received_raw_semantics_handoff_readmes_written", "value": str(handoff_count), "interpretation": "Per-dataset semantics review handoffs written."})

    write_csv(VARIABLE_REVIEW_PATH, variable_rows, VARIABLE_REVIEW_COLUMNS)
    write_csv(REQUIREMENT_REVIEW_PATH, requirement_rows, REQUIREMENT_REVIEW_COLUMNS)
    write_csv(DOCUMENTATION_SCOPE_PATH, doc_rows, DOCUMENTATION_SCOPE_COLUMNS)
    write_csv(SUMMARY_PATH, summary_rows, SUMMARY_COLUMNS)
    write_report(variable_rows, requirement_rows, doc_rows, summary_rows)
    append_log(
        TEMP_DIR / "audit_log.md",
        f"Built priority LSMS/ISA received raw semantics review variables={len(variable_rows)} requirements={len(requirement_rows)} documentation_scope={len(doc_rows)}.",
    )
    print(
        "Priority LSMS/ISA received raw semantics review "
        f"variables={len(variable_rows)} requirements={len(requirement_rows)} documentation_scope={len(doc_rows)}."
    )


if __name__ == "__main__":
    main()
