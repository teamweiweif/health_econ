from __future__ import annotations

import csv
import re
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

from common import REPORT_DIR, RESULT_DIR, TEMP_DIR, append_log, ensure_dirs, write_csv


VARIABLE_AUDIT_PATH = TEMP_DIR / "variable_map_confidence_audit.csv"
COUNTRY_WAVE_AUDIT_PATH = RESULT_DIR / "metadata_candidate_quality_audit.csv"
SUMMARY_PATH = RESULT_DIR / "metadata_candidate_quality_summary.csv"
PRIORITY_PATH = TEMP_DIR / "metadata_quality_download_priority.csv"
REPORT_PATH = REPORT_DIR / "metadata_candidate_quality_audit.md"

MAP_FILES = [
    TEMP_DIR / "variable_map_consumption.csv",
    TEMP_DIR / "variable_map_health_expenditure.csv",
    TEMP_DIR / "variable_map_health_need_access.csv",
    TEMP_DIR / "variable_map_geography.csv",
    TEMP_DIR / "variable_map_survey_design.csv",
    TEMP_DIR / "variable_map_demographics.csv",
    TEMP_DIR / "variable_map_shocks.csv",
]

QUALITY_SCORE = {
    "likely_false_positive": 0,
    "low": 1,
    "moderate": 2,
    "high": 3,
}

VARIABLE_COLUMNS = [
    "map_file",
    "map_category",
    "country",
    "survey_name",
    "wave",
    "idno",
    "file",
    "raw_variable",
    "raw_label",
    "harmonized_variable",
    "metadata_confidence",
    "confidence_reason",
    "raw_verification_required",
]

COUNTRY_WAVE_COLUMNS = [
    "country",
    "survey_name",
    "wave",
    "idno",
    "feasibility_score",
    "sample_gate_status",
    "priority_rank",
    "priority_score",
    "map_rows",
    "high_confidence_rows",
    "moderate_confidence_rows",
    "low_confidence_rows",
    "likely_false_positive_rows",
    "quality_has_budget",
    "quality_has_oop",
    "quality_has_weight",
    "quality_has_timing",
    "quality_has_geography",
    "quality_has_access_core",
    "quality_has_main_financial_core",
    "quality_has_double_failure_core",
    "quality_download_priority_tier",
    "quality_gap",
]

SUMMARY_COLUMNS = ["metric", "value", "interpretation"]

PRIORITY_COLUMNS = [
    "quality_rank",
    "quality_download_priority_tier",
    "country",
    "survey_name",
    "wave",
    "idno",
    "official_url",
    "sample_gate_status",
    "manual_priority_rank",
    "manual_priority_score",
    "high_confidence_rows",
    "moderate_confidence_rows",
    "likely_false_positive_rows",
    "local_target_folder",
    "quality_gap",
]


def read_csv_dicts(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        return []
    with path.open(encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def clean(value: Any) -> str:
    return "" if value is None else str(value).strip()


def bool_text(value: bool) -> str:
    return "1" if value else "0"


def has(text: str, pattern: str) -> bool:
    return re.search(pattern, text, flags=re.IGNORECASE) is not None


def has_any(text: str, patterns: list[str]) -> bool:
    return any(has(text, pattern) for pattern in patterns)


def classify_variable(row: dict[str, str], map_category: str) -> tuple[str, str]:
    raw_variable = clean(row.get("raw_variable", ""))
    raw_label = clean(row.get("raw_label", ""))
    harmonized = clean(row.get("harmonized_variable", ""))
    file_name = clean(row.get("file", ""))
    notes = clean(row.get("notes", ""))
    unit = clean(row.get("unit", ""))
    text = " ".join([raw_variable, raw_label, harmonized, file_name, notes, unit]).lower()
    var = raw_variable.lower()
    label = raw_label.lower()

    health_context = has_any(
        text,
        [
            r"\bhealth\b",
            r"\bmedical\b",
            r"\bmedicine(s)?\b",
            r"\bdrug(s)?\b",
            r"\bdoctor\b",
            r"\bhospital\b",
            r"\bclinic\b",
            r"\bout[- ]?patient\b",
            r"\bin[- ]?patient\b",
            r"\blab(oratory)?\b",
            r"\btreatment\b",
            r"\bill(ness)?\b",
            r"\bsick(ness)?\b",
            r"\binjur(y|ies|ed)\b",
        ],
    )
    cost_context = has_any(text, [r"\bpaid\b", r"\bpayment\b", r"\bcost(s)?\b", r"\bexpenditure(s)?\b", r"\bexpense(s)?\b", r"\bfee(s)?\b", r"\bcharge(s)?\b"])

    if map_category == "consumption":
        if harmonized == "food_consumption" and has_any(text, [r"\bnon[- ]?food\b", r"\bnfood\b"]):
            return "likely_false_positive", "food consumption candidate contains non-food terms"
        if harmonized == "nonfood_consumption" and has_any(text, [r"\bnon[- ]?food\b", r"\bnfood\b"]):
            return "high", "explicit non-food consumption evidence"
        if harmonized == "food_consumption" and has_any(text, [r"\bfood\b", r"\bcrop\b", r"\bmeal\b"]):
            return "moderate", "food consumption evidence; raw units/recall still unverified"
        if harmonized == "total_consumption_or_income" and has_any(
            text,
            [
                r"\btotal (household )?(consumption|expenditure|income)\b",
                r"\bconsumption aggregate\b",
                r"\bwelfare aggregate\b",
                r"\bper capita (consumption|expenditure)\b",
                r"\btot(cons|exp|inc)\b",
            ],
        ):
            return "high", "explicit total consumption/income or welfare aggregate evidence"
        if harmonized == "total_consumption_or_income" and has_any(text, [r"\bconsumption\b", r"\bincome\b", r"\bexpenditure\b"]):
            return "moderate", "budget concept present but aggregate status requires raw/codebook check"
        return "low", "broad consumption keyword hit only"

    if map_category == "health_expenditure":
        if harmonized == "health_insurance" and has_any(text, [r"\binsur(ed|ance)\b", r"\bcoverage\b"]):
            return "high", "explicit health insurance or coverage evidence"
        if has_any(text, [r"\bout[- ]?of[- ]?pocket\b", r"\boop\b"]):
            return "high", "explicit OOP terminology"
        if health_context and cost_context:
            if has_any(unit, [r"community", r"geography"]):
                return "moderate", "health payment evidence in metadata; unit may not be household/person"
            return "high", "health payment/expenditure evidence"
        if health_context:
            return "moderate", "health context present without clear payment/expenditure wording"
        if cost_context:
            return "low", "payment/expenditure wording without health context"
        return "low", "broad health-expenditure keyword hit only"

    if map_category == "health_need_access":
        access_context = has_any(text, [r"\bseek\b", r"\bsought\b", r"\bvisit\b", r"\bconsult", r"\bcare\b", r"\btreatment\b", r"\bfacility\b"])
        barrier_context = has_any(text, [r"\btoo expensive\b", r"\bexpensive\b", r"\bcost\b", r"\btoo far\b", r"\bdistance\b", r"\btransport\b", r"\bno (drug|medicine|staff|provider)\b"])
        if harmonized == "illness_or_injury_need" and has_any(text, [r"\bill(ness)?\b", r"\bsick(ness)?\b", r"\binjur(y|ies|ed)\b", r"\bsymptom(s)?\b", r"\bdisease\b"]):
            return "high", "explicit illness/injury/need evidence"
        if harmonized in {"care_sought", "care_not_sought_reason", "reason_not_sought_cost", "reason_not_sought_distance", "reason_not_sought_supply", "health_facility_distance"}:
            if not health_context and barrier_context:
                return "likely_false_positive", "barrier wording lacks health-care context"
            if health_context and (access_context or barrier_context):
                return "high", "health-care access/barrier evidence"
            if health_context:
                return "moderate", "health context present; access/barrier role requires raw/codebook check"
            if access_context:
                return "low", "access wording without health context"
        return "low", "broad health-need/access keyword hit only"

    if map_category == "geography":
        if harmonized == "latitude_or_longitude" and has_any(text, [r"\blat(itude)?\b", r"\blon(gitude)?\b", r"\bgps\b", r"\bcoordinate(s)?\b"]):
            return "high", "explicit coordinate/GPS evidence"
        if harmonized == "rural" and has_any(text, [r"\brural\b", r"\burban\b", r"\bresidence\b"]):
            return "high", "explicit rural/urban residence evidence"
        exact_admin_var = has_any(var, [r"^(dist|district|region|province|admin|adm|county|commune|village|ward|ea|cluster)(_?code)?$", r"^distcode$", r"^reg(ion)?$"])
        admin_label = has_any(label, [r"\bdistrict code\b", r"\bregion\b", r"\bprovince\b", r"\badmin", r"\bcounty\b", r"\bcommune\b", r"\bvillage\b", r"\bcluster\b", r"\benumeration area\b"])
        false_context = has_any(text, [r"\bmarket\b", r"\bsold\b", r"\bcrop\b", r"\bout of district\b", r"\bwork outside\b"])
        if harmonized == "admin1_or_admin2" and (exact_admin_var or admin_label) and not false_context:
            return "high", "explicit administrative geography or cluster evidence"
        if harmonized == "admin1_or_admin2" and false_context and not (exact_admin_var or admin_label):
            return "likely_false_positive", "district/geography word appears in non-location context"
        if harmonized == "admin1_or_admin2" and has_any(text, [r"\bdistrict\b", r"\bregion\b", r"\bprovince\b", r"\bcluster\b"]):
            return "moderate", "geography wording present but raw role requires verification"
        return "low", "broad geography keyword hit only"

    if map_category == "survey_design":
        if harmonized == "hhid" and has_any(text, [r"\bhh(id)?\b", r"\bhousehold id\b", r"\bhousehold identifier\b"]):
            return "high", "explicit household identifier evidence"
        if harmonized == "pid" and has_any(text, [r"\bperson id\b", r"\bindividual id\b", r"\bpid\b", r"\bline number\b"]):
            return "high", "explicit person identifier evidence"
        if harmonized == "household_weight_or_person_weight" and has_any(text, [r"\bweight\b", r"\bwt\b", r"\bpweight\b", r"\bexpansion factor\b"]):
            return "high", "explicit survey weight evidence"
        if harmonized == "strata" and has_any(text, [r"\bstrata\b", r"\bstratum\b", r"\bstratification\b"]):
            return "high", "explicit strata evidence"
        if harmonized == "psu_or_cluster_id" and has_any(text, [r"\bpsu\b", r"\bcluster\b", r"\benumeration area\b", r"\bea\b"]):
            return "high", "explicit PSU/cluster evidence"
        if harmonized == "interview_date_or_survey_month" and has_any(text, [r"\binterview\b", r"\bsurvey date\b", r"\bmonth\b", r"\bdate\b", r"\byear\b"]):
            return "high", "explicit interview date/month/year evidence"
        return "low", "broad survey-design keyword hit only"

    if map_category == "demographics":
        if harmonized == "age" and has_any(text, [r"\bage\b", r"\byear(s)? old\b"]):
            return "high", "explicit age evidence"
        if harmonized == "sex" and has_any(text, [r"\bsex\b", r"\bgender\b", r"\bfemale\b", r"\bmale\b"]):
            return "high", "explicit sex/gender evidence"
        if harmonized == "education" and has_any(text, [r"\beducation\b", r"\bschool\b", r"\bgrade\b", r"\bliteracy\b"]):
            return "high", "explicit education evidence"
        if harmonized == "household_size" and has_any(text, [r"\bhousehold size\b", r"\bnumber of household members\b", r"\bhh size\b"]):
            return "high", "explicit household-size evidence"
        if harmonized == "household_head_marker" and has_any(text, [r"\bhead\b", r"\brelation(ship)? to head\b"]):
            return "high", "explicit household-head evidence"
        if harmonized == "asset_index_or_asset_variable" and has_any(text, [r"\basset\b", r"\bwealth\b", r"\bdurable\b", r"\blivestock\b", r"\bland\b"]):
            return "moderate", "asset/wealth evidence; index construction requires raw data"
        return "low", "broad demographic keyword hit only"

    if map_category == "shocks":
        if harmonized == "shock_module_variable" and has_any(text, [r"\bshock\b", r"\bdrought\b", r"\bflood\b", r"\bheat\b", r"\brainfall\b", r"\bdry spell\b", r"\bcrop loss\b", r"\bnatural disaster\b"]):
            return "high", "explicit shock or climate-sensitive event evidence"
        if harmonized == "agriculture_livelihood" and has_any(text, [r"\bagricultur", r"\bcrop\b", r"\bfarm\b", r"\blivestock\b"]):
            return "moderate", "agriculture/livelihood evidence; moderator role requires raw data"
        if harmonized == "coping_borrowed" and has_any(text, [r"\bborrow", r"\bloan\b", r"\bcredit\b"]):
            return "high", "explicit borrowing/coping evidence"
        if harmonized == "coping_sold_assets" and has_any(text, [r"\bsold asset", r"\bsale of asset", r"\bsell assets?\b"]):
            return "high", "explicit sold-assets coping evidence"
        if harmonized == "food_insecurity" and has_any(text, [r"\bfood insecurity\b", r"\bhunger\b", r"\bskip(ped)? meal\b", r"\bnot enough food\b"]):
            return "high", "explicit food-insecurity evidence"
        return "low", "broad shocks/livelihood keyword hit only"

    return "low", "unclassified metadata keyword hit"


def map_category(path: Path) -> str:
    return path.stem.replace("variable_map_", "")


def audited_variable_rows() -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    for path in MAP_FILES:
        category = map_category(path)
        for row in read_csv_dicts(path):
            confidence, reason = classify_variable(row, category)
            rows.append(
                {
                    "map_file": path.name,
                    "map_category": category,
                    "country": row.get("country", ""),
                    "survey_name": row.get("survey_name", ""),
                    "wave": row.get("wave", ""),
                    "idno": row.get("idno", ""),
                    "file": row.get("file", ""),
                    "raw_variable": row.get("raw_variable", ""),
                    "raw_label": row.get("raw_label", ""),
                    "harmonized_variable": row.get("harmonized_variable", ""),
                    "metadata_confidence": confidence,
                    "confidence_reason": reason,
                    "raw_verification_required": "1",
                }
            )
    return rows


def update_best(best: dict[str, int], key: str, confidence: str) -> None:
    best[key] = max(best.get(key, 0), QUALITY_SCORE.get(confidence, 0))


def aggregate_quality(variable_rows: list[dict[str, str]]) -> dict[str, dict[str, Any]]:
    groups: dict[str, dict[str, Any]] = defaultdict(lambda: {"counts": Counter(), "best": {}, "rows": 0})
    for row in variable_rows:
        idno = row.get("idno", "")
        if not idno:
            continue
        group = groups[idno]
        group["rows"] += 1
        group["counts"][row.get("metadata_confidence", "")] += 1
        category = row.get("map_category", "")
        harmonized = row.get("harmonized_variable", "")
        confidence = row.get("metadata_confidence", "")
        if category == "consumption" and harmonized == "total_consumption_or_income":
            update_best(group["best"], "budget", confidence)
        if category == "health_expenditure" and harmonized == "oop_health_expenditure":
            update_best(group["best"], "oop", confidence)
        if category == "survey_design" and harmonized == "household_weight_or_person_weight":
            update_best(group["best"], "weight", confidence)
        if category == "survey_design" and harmonized == "interview_date_or_survey_month":
            update_best(group["best"], "timing", confidence)
        if category == "geography" and harmonized in {"admin1_or_admin2", "latitude_or_longitude"}:
            update_best(group["best"], "geography", confidence)
        if category == "health_need_access" and harmonized == "illness_or_injury_need":
            update_best(group["best"], "need", confidence)
        if category == "health_need_access" and harmonized == "care_sought":
            update_best(group["best"], "care", confidence)
        if category == "health_need_access" and harmonized in {"care_not_sought_reason", "reason_not_sought_cost", "reason_not_sought_distance", "reason_not_sought_supply"}:
            update_best(group["best"], "barrier", confidence)
    return groups


def quality_flag(best: dict[str, int], key: str) -> bool:
    return best.get(key, 0) >= QUALITY_SCORE["moderate"]


def country_wave_rows(variable_rows: list[dict[str, str]]) -> list[dict[str, str]]:
    grouped = aggregate_quality(variable_rows)
    screening = read_csv_dicts(TEMP_DIR / "country_wave_screening.csv")
    gate_by_idno = {row.get("idno", ""): row for row in read_csv_dicts(RESULT_DIR / "sample_selection_gate_audit.csv")}
    priority_by_idno = {row.get("idno", ""): row for row in read_csv_dicts(TEMP_DIR / "manual_download_priority.csv")}
    out: list[dict[str, str]] = []
    for row in screening:
        idno = row.get("idno", "")
        group = grouped.get(idno, {"counts": Counter(), "best": {}, "rows": 0})
        counts: Counter[str] = group["counts"]
        best: dict[str, int] = group["best"]
        budget = quality_flag(best, "budget")
        oop = quality_flag(best, "oop")
        weight = quality_flag(best, "weight")
        timing = quality_flag(best, "timing")
        geography = quality_flag(best, "geography")
        access = quality_flag(best, "need") and (quality_flag(best, "care") or quality_flag(best, "barrier"))
        financial_core = budget and oop and weight and timing and geography
        double_core = financial_core and access
        gaps = []
        if not budget:
            gaps.append("no_moderate_or_high_budget_metadata")
        if not oop:
            gaps.append("no_moderate_or_high_oop_metadata")
        if not weight:
            gaps.append("no_moderate_or_high_weight_metadata")
        if not timing:
            gaps.append("no_moderate_or_high_timing_metadata")
        if not geography:
            gaps.append("no_moderate_or_high_geography_metadata")
        if not access:
            gaps.append("no_moderate_or_high_access_core_metadata")
        if counts.get("likely_false_positive", 0) > counts.get("high", 0) + counts.get("moderate", 0):
            gaps.append("metadata_hits_more_noisy_than_supported")
        if double_core:
            tier = "tier_1_quality_supported_financial_and_access_download"
        elif financial_core:
            tier = "tier_2_quality_supported_financial_download"
        elif access and geography and timing:
            tier = "tier_3_quality_supported_access_only_download"
        elif group["rows"]:
            tier = "tier_4_metadata_present_but_noisy_or_incomplete"
        else:
            tier = "tier_5_no_variable_map_evidence"
        priority = priority_by_idno.get(idno, {})
        gate = gate_by_idno.get(idno, {})
        out.append(
            {
                "country": row.get("country", ""),
                "survey_name": row.get("survey name", ""),
                "wave": row.get("wave/year", ""),
                "idno": idno,
                "feasibility_score": row.get("feasibility score from 0 to 5", ""),
                "sample_gate_status": gate.get("status", ""),
                "priority_rank": priority.get("priority_rank", ""),
                "priority_score": priority.get("priority_score", ""),
                "map_rows": str(group["rows"]),
                "high_confidence_rows": str(counts.get("high", 0)),
                "moderate_confidence_rows": str(counts.get("moderate", 0)),
                "low_confidence_rows": str(counts.get("low", 0)),
                "likely_false_positive_rows": str(counts.get("likely_false_positive", 0)),
                "quality_has_budget": bool_text(budget),
                "quality_has_oop": bool_text(oop),
                "quality_has_weight": bool_text(weight),
                "quality_has_timing": bool_text(timing),
                "quality_has_geography": bool_text(geography),
                "quality_has_access_core": bool_text(access),
                "quality_has_main_financial_core": bool_text(financial_core),
                "quality_has_double_failure_core": bool_text(double_core),
                "quality_download_priority_tier": tier,
                "quality_gap": ";".join(gaps),
            }
        )
    return out


def summary_rows(variable_rows: list[dict[str, str]], country_rows: list[dict[str, str]]) -> list[dict[str, str]]:
    confidence_counts = Counter(row.get("metadata_confidence", "") for row in variable_rows)
    tier_counts = Counter(row.get("quality_download_priority_tier", "") for row in country_rows)
    gate_main = [row for row in country_rows if row.get("sample_gate_status") == "metadata_main_sample_candidate_not_selectable"]
    quality_financial = [row for row in country_rows if row.get("quality_has_main_financial_core") == "1"]
    quality_double = [row for row in country_rows if row.get("quality_has_double_failure_core") == "1"]
    rows = [
        {
            "metric": "variable_map_rows",
            "value": str(len(variable_rows)),
            "interpretation": "Metadata-only variable-map rows scored for confidence; none are raw-verified.",
        },
        {
            "metric": "high_confidence_variable_rows",
            "value": str(confidence_counts.get("high", 0)),
            "interpretation": "Strong label/name evidence, still requiring raw values, units, and merge-key checks.",
        },
        {
            "metric": "moderate_confidence_variable_rows",
            "value": str(confidence_counts.get("moderate", 0)),
            "interpretation": "Useful for manual download targeting, not for final sample selection.",
        },
        {
            "metric": "likely_false_positive_variable_rows",
            "value": str(confidence_counts.get("likely_false_positive", 0)),
            "interpretation": "Metadata hits with context suggesting the keyword match is probably not the target concept.",
        },
        {
            "metric": "quality_supported_financial_country_waves",
            "value": str(len(quality_financial)),
            "interpretation": "Country-waves with moderate/high metadata support for budget, OOP, weights, timing, and geography.",
        },
        {
            "metric": "quality_supported_double_failure_country_waves",
            "value": str(len(quality_double)),
            "interpretation": "Country-waves with quality-supported financial and access-core metadata.",
        },
        {
            "metric": "sample_gate_metadata_main_candidates",
            "value": str(len(gate_main)),
            "interpretation": "Original sample-gate metadata candidates before this confidence screen.",
        },
        {
            "metric": "sample_gate_main_candidates_with_quality_financial_core",
            "value": str(sum(1 for row in gate_main if row.get("quality_has_main_financial_core") == "1")),
            "interpretation": "Still metadata-only; this count is a better raw-download priority signal, not an analytical sample.",
        },
    ]
    for tier, count in sorted(tier_counts.items()):
        rows.append({"metric": f"tier_count_{tier}", "value": str(count), "interpretation": "Country-wave metadata-quality tier count."})
    return rows


def priority_rows(country_rows: list[dict[str, str]]) -> list[dict[str, str]]:
    tier_order = {
        "tier_1_quality_supported_financial_and_access_download": 1,
        "tier_2_quality_supported_financial_download": 2,
        "tier_3_quality_supported_access_only_download": 3,
        "tier_4_metadata_present_but_noisy_or_incomplete": 4,
        "tier_5_no_variable_map_evidence": 5,
    }
    screening_by_idno = {row.get("idno", ""): row for row in read_csv_dicts(TEMP_DIR / "country_wave_screening.csv")}
    manual_by_idno = {row.get("idno", ""): row for row in read_csv_dicts(TEMP_DIR / "manual_download_priority.csv")}
    selected = [
        row
        for row in country_rows
        if row.get("quality_download_priority_tier") in {
            "tier_1_quality_supported_financial_and_access_download",
            "tier_2_quality_supported_financial_download",
            "tier_3_quality_supported_access_only_download",
        }
    ]
    selected.sort(
        key=lambda row: (
            tier_order.get(row.get("quality_download_priority_tier", ""), 99),
            int(row.get("priority_rank") or 9999),
            -int(row.get("high_confidence_rows") or 0),
            -int(row.get("moderate_confidence_rows") or 0),
            int(row.get("likely_false_positive_rows") or 0),
            row.get("country", ""),
            row.get("wave", ""),
        )
    )
    out = []
    for rank, row in enumerate(selected, start=1):
        idno = row.get("idno", "")
        screening = screening_by_idno.get(idno, {})
        manual = manual_by_idno.get(idno, {})
        official_url = manual.get("official_url") or screening.get("public URL", "")
        out.append(
            {
                "quality_rank": str(rank),
                "quality_download_priority_tier": row.get("quality_download_priority_tier", ""),
                "country": row.get("country", ""),
                "survey_name": row.get("survey_name", ""),
                "wave": row.get("wave", ""),
                "idno": idno,
                "official_url": official_url,
                "sample_gate_status": row.get("sample_gate_status", ""),
                "manual_priority_rank": row.get("priority_rank", ""),
                "manual_priority_score": row.get("priority_score", ""),
                "high_confidence_rows": row.get("high_confidence_rows", ""),
                "moderate_confidence_rows": row.get("moderate_confidence_rows", ""),
                "likely_false_positive_rows": row.get("likely_false_positive_rows", ""),
                "local_target_folder": f"temp/raw_downloads/{idno}/" if idno else "",
                "quality_gap": row.get("quality_gap", ""),
            }
        )
    return out


def markdown_count_table(counter: Counter[str], label: str) -> str:
    lines = [f"| {label} | Count |", "|---|---:|"]
    for key, count in counter.most_common():
        lines.append(f"| {key or 'blank'} | {count} |")
    return "\n".join(lines)


def write_report(variable_rows: list[dict[str, str]], country_rows: list[dict[str, str]], summaries: list[dict[str, str]], priorities: list[dict[str, str]]) -> None:
    confidence_counts = Counter(row.get("metadata_confidence", "") for row in variable_rows)
    tier_counts = Counter(row.get("quality_download_priority_tier", "") for row in country_rows)
    false_examples = [row for row in variable_rows if row.get("metadata_confidence") == "likely_false_positive"][:12]
    lines = [
        "# Metadata Candidate Quality Audit",
        "",
        "Status: metadata-only variable hits have been scored for confidence. This is a download-prioritization audit only; it does not verify raw variables or select the final analytical sample.",
        "",
        "## Counts",
        "",
        markdown_count_table(confidence_counts, "Variable-row confidence"),
        "",
        markdown_count_table(tier_counts, "Country-wave quality tier"),
        "",
        "## Summary Metrics",
        "",
        "| Metric | Value | Interpretation |",
        "|---|---:|---|",
    ]
    for row in summaries:
        lines.append(f"| {row['metric']} | {row['value']} | {row['interpretation']} |")
    lines.extend(
        [
            "",
            "## Quality-Supported Download Priorities",
            "",
            f"`temp/metadata_quality_download_priority.csv` contains {len(priorities)} quality-supported country-waves from tiers 1-3. These are still metadata-only download priorities, not selected analytical samples.",
            "",
            "",
            "## False-Positive Examples",
            "",
            "| IDNO | Map | Raw variable | Raw label | Reason |",
            "|---|---|---|---|---|",
        ]
    )
    if false_examples:
        for row in false_examples:
            label = row.get("raw_label", "").replace("|", "/")
            if len(label) > 120:
                label = label[:117] + "..."
            lines.append(
                f"| {row.get('idno', '')} | {row.get('map_category', '')}:{row.get('harmonized_variable', '')} | `{row.get('raw_variable', '')}` | {label} | {row.get('confidence_reason', '')} |"
            )
    else:
        lines.append("| none | none | none | none | No likely false positives detected by current rules. |")
    lines.extend(
        [
            "",
            "## Guardrail",
            "",
            "Moderate/high metadata evidence means the label or variable name is plausible enough to prioritize manual raw download. It is not proof of analyzable content, correct units, recall period, mergeability, household/person level, or final sample eligibility.",
            "",
            "## Machine-Readable Outputs",
            "",
            "- `temp/variable_map_confidence_audit.csv`",
            "- `temp/metadata_quality_download_priority.csv`",
            "- `result/metadata_candidate_quality_audit.csv`",
            "- `result/metadata_candidate_quality_summary.csv`",
        ]
    )
    REPORT_PATH.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    ensure_dirs()
    variable_rows = audited_variable_rows()
    country_rows = country_wave_rows(variable_rows)
    summaries = summary_rows(variable_rows, country_rows)
    priorities = priority_rows(country_rows)
    write_csv(VARIABLE_AUDIT_PATH, variable_rows, VARIABLE_COLUMNS)
    write_csv(COUNTRY_WAVE_AUDIT_PATH, country_rows, COUNTRY_WAVE_COLUMNS)
    write_csv(SUMMARY_PATH, summaries, SUMMARY_COLUMNS)
    write_csv(PRIORITY_PATH, priorities, PRIORITY_COLUMNS)
    write_report(variable_rows, country_rows, summaries, priorities)
    quality_financial = sum(1 for row in country_rows if row.get("quality_has_main_financial_core") == "1")
    likely_false = sum(1 for row in variable_rows if row.get("metadata_confidence") == "likely_false_positive")
    append_log(TEMP_DIR / "audit_log.md", f"Metadata variable quality audit rows={len(variable_rows)} quality_financial_country_waves={quality_financial} likely_false_positive_rows={likely_false} priority_rows={len(priorities)}.")
    print(f"Metadata variable quality audit rows={len(variable_rows)} quality_financial_country_waves={quality_financial} likely_false_positive_rows={likely_false} priority_rows={len(priorities)}.")


if __name__ == "__main__":
    main()
