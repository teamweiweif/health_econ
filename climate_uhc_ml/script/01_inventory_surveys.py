from __future__ import annotations

import concurrent.futures as futures
import re
import time
from collections import defaultdict
from typing import Any

import requests

from common import TEMP_DIR, append_log, compact_text, ensure_dirs, write_csv, write_json


USER_AGENT = "Codex climate_uhc_ml country-wave inventory"
CATALOG_API = "https://microdata.worldbank.org/index.php/api/catalog/search"
DETAIL_API = "https://microdata.worldbank.org/index.php/api/catalog/{idno}"
VARIABLE_API = "https://microdata.worldbank.org/index.php/api/catalog/{idno}/variables"

LSMS_ISA_COUNTRIES = {
    "Burkina Faso",
    "Ethiopia",
    "Malawi",
    "Mali",
    "Niger",
    "Nigeria",
    "Tanzania",
    "Uganda",
}

TITLE_KEYWORDS = [
    "living standards",
    "lsms",
    "lsms-isa",
    "integrated household",
    "household budget",
    "household income",
    "household expenditure",
    "income and expenditure",
    "household consumption",
    "welfare monitoring",
    "welfare survey",
    "consumption survey",
    "expenditure survey",
    "ehcvm",
    "household survey",
    "panel survey",
    "socio-economic",
    "socioeconomic",
]

GROUPS = {
    "household_id": ["hhid", "household id", "identifiant menage", "id menage", "case id"],
    "person_id": ["pid", "person id", "individual id", "member id", "line number", "membres__id"],
    "weights": ["weight", "weights", "poids", "ponderation", "sampling weight", "hhweight", "expansion"],
    "strata": ["strata", "stratum", "strate"],
    "psu_cluster": ["psu", "cluster", "grappe", "enumeration area", "ea ", "zone de denombrement"],
    "interview_date": ["interview date", "date of interview", "interview month", "month of interview", "survey month", "fieldwork", "date interview"],
    "admin_geography": ["region", "district", "province", "admin", "county", "commune", "ward", "locality", "state", "lga"],
    "gps": ["latitude", "longitude", "gps", "coord", "geocode", "geospatial"],
    "total_consumption_income": ["consumption aggregate", "total consumption", "consumption expenditure", "consommation", "depense totale", "expenditure aggregate", "income aggregate", "total income", "welfare aggregate"],
    "food_consumption": ["food consumption", "food expenditure", "alimentaire", "food exp"],
    "nonfood_consumption": ["non-food", "nonfood", "non food", "nonalimentaire"],
    "oop_health_expenditure": ["health expenditure", "medical expenditure", "out-of-pocket", "out of pocket", "oop", "depense de sante", "depenses de sante", "health spending", "medical cost", "hospital cost", "medicine cost"],
    "health_utilization": ["sought care", "seek care", "consultation", "visited health", "health facility", "treatment", "utilization", "soins"],
    "illness_need": ["illness", "injury", "sick", "symptom", "maladie", "blessure", "health problem"],
    "reason_not_sought": ["reason", "why", "not seek", "did not seek", "cost", "expensive", "distance", "transport", "too far", "drug", "medicine unavailable", "staff", "provider"],
    "cost_barrier": ["too expensive", "cost", "money", "afford", "financial", "cher"],
    "distance_barrier": ["distance", "transport", "too far", "travel"],
    "supply_barrier": ["drug unavailable", "medicine unavailable", "staff absent", "no doctor", "closed", "provider unavailable", "facility closed"],
    "insurance": ["insurance", "insured", "mutuelle", "coverage", "assurance"],
    "shock_module": ["shock", "drought", "flood", "rain", "rainfall", "climate", "weather", "heat", "crop loss", "natural disaster"],
    "coping": ["borrow", "loan", "sold asset", "sell asset", "coping", "reduced consumption"],
    "food_insecurity": ["food insecurity", "hunger", "fies", "reduced meals", "food security"],
    "assets_wealth": ["asset", "wealth", "dwelling", "roof", "floor", "electricity", "durable"],
    "education": ["education", "schooling", "literacy", "educ"],
    "rural_urban": ["rural", "urban", "milieu"],
    "agriculture_livelihood": ["agriculture", "crop", "livestock", "farm", "plot", "harvest", "agric"],
}

SCREENING_COLUMNS = [
    "country",
    "survey name",
    "wave/year",
    "public URL",
    "access type",
    "file formats",
    "unit",
    "sample size",
    "panel or repeated cross-section",
    "household ID",
    "person ID",
    "weights",
    "strata",
    "PSU/cluster",
    "interview date",
    "interview month",
    "interview year",
    "admin1/admin2 geography",
    "GPS or cluster coordinates",
    "whether GPS is exact, displaced, restricted, or absent",
    "total consumption or income aggregate",
    "food consumption",
    "non-food consumption",
    "OOP health expenditure",
    "health-care utilization",
    "illness/injury/health need",
    "care-seeking",
    "reason for not seeking care",
    "cost barrier",
    "distance barrier",
    "supply/drug/staff barrier",
    "insurance/coverage",
    "shock module",
    "drought/flood/heat/agricultural shock questions",
    "borrowing/selling assets/coping because of illness or health spending",
    "food insecurity",
    "assets/wealth",
    "education",
    "household age structure",
    "rural/urban",
    "agriculture/livelihood variables",
    "feasibility score from 0 to 5",
    "reason for pass/fail",
    "screening detail level",
    "idno",
    "catalog id",
    "collection",
    "repository",
    "authoring entity",
    "doi",
    "catalog changed",
    "variable count",
]


def request_json(url: str, params: dict[str, Any] | None = None) -> dict[str, Any]:
    response = requests.get(url, params=params, headers={"User-Agent": USER_AGENT}, timeout=60)
    response.raise_for_status()
    return response.json()


def fetch_catalog() -> list[dict[str, Any]]:
    data = request_json(CATALOG_API, {"ps": 10000, "sort_by": "title", "sort_order": "asc"})
    rows = data.get("result", {}).get("rows", [])
    write_json(TEMP_DIR / "api_cache" / "worldbank_catalog_all.json", data)
    return rows


def is_candidate(row: dict[str, Any]) -> tuple[bool, str]:
    haystack = " ".join(
        [
            str(row.get("title", "")),
            str(row.get("idno", "")),
            str(row.get("repo_title", "")),
            str(row.get("repositoryid", "")),
            str(row.get("authoring_entity", "")),
        ]
    ).lower()
    reasons = []
    if row.get("repositoryid") == "lsms":
        reasons.append("LSMS collection")
    if str(row.get("nation", "")) in LSMS_ISA_COUNTRIES:
        reasons.append("LSMS-ISA partner country")
    for kw in TITLE_KEYWORDS:
        if kw in haystack:
            reasons.append(f"title/catalog keyword: {kw}")
            break
    return bool(reasons), "; ".join(reasons)


def fetch_detail_and_variables(row: dict[str, Any]) -> dict[str, Any]:
    idno = row.get("idno")
    out: dict[str, Any] = {"idno": idno, "detail_error": "", "variables_error": "", "variables": []}
    if not idno:
        out["detail_error"] = "missing idno"
        return out
    try:
        detail = request_json(DETAIL_API.format(idno=idno))
        out["detail"] = detail.get("dataset", {})
        time.sleep(0.05)
    except Exception as exc:
        out["detail_error"] = str(exc)[:300]
    try:
        variables = request_json(VARIABLE_API.format(idno=idno))
        out["variables"] = variables.get("variables", [])
        out["variable_total_api"] = variables.get("total", "")
        time.sleep(0.05)
    except Exception as exc:
        out["variables_error"] = str(exc)[:300]
    return out


def group_hits(variables: list[dict[str, Any]]) -> dict[str, list[str]]:
    hits: dict[str, list[str]] = defaultdict(list)
    for var in variables:
        name = str(var.get("name", ""))
        label = str(var.get("labl", ""))
        text = f"{name} {label}".lower()
        for group, needles in GROUPS.items():
            if any(needle.lower() in text for needle in needles):
                hits[group].append(f"{name}: {label}"[:180])
    return hits


def yes_no(hits: dict[str, list[str]], key: str) -> str:
    return "yes" if hits.get(key) else "not found in metadata"


def first_hits(hits: dict[str, list[str]], key: str, max_items: int = 3) -> str:
    values = hits.get(key, [])
    return " | ".join(values[:max_items])


def infer_unit(detail: dict[str, Any], row: dict[str, Any]) -> str:
    md = detail.get("metadata", {}) if detail else {}
    unit = (
        md.get("study_desc", {})
        .get("study_info", {})
        .get("analysis_unit", "")
    )
    if unit:
        return compact_text(unit)
    title = str(row.get("title", "")).lower()
    if "household" in title:
        return "household"
    return ""


def infer_panel(detail: dict[str, Any], row: dict[str, Any]) -> str:
    text = compact_text(detail) + " " + compact_text(row)
    low = text.lower()
    if "panel" in low or "longitudinal" in low:
        return "panel/longitudinal possible"
    if "repeated" in low or "round" in low or "wave" in low:
        return "repeated cross-section or multi-round possible"
    return "not clear from catalog metadata"


def score_candidate(hits: dict[str, list[str]], row: dict[str, Any], detail: dict[str, Any], detailed: bool) -> tuple[int, str]:
    score = 0
    reasons = []
    if hits.get("total_consumption_income"):
        score += 1
        reasons.append("consumption/income variable hit")
    if hits.get("oop_health_expenditure"):
        score += 1
        reasons.append("OOP/health expenditure hit")
    if hits.get("illness_need") and hits.get("health_utilization"):
        score += 1
        reasons.append("need and utilization hits")
    if hits.get("interview_date"):
        score += 1
        reasons.append("interview timing hit")
    if hits.get("gps") or hits.get("admin_geography") or hits.get("psu_cluster"):
        score += 1
        reasons.append("geography/cluster hit")
    if not detailed:
        if row.get("repositoryid") == "lsms":
            score = max(score, 2)
            reasons.append("LSMS metadata-only candidate")
        elif str(row.get("nation", "")) in LSMS_ISA_COUNTRIES:
            score = max(score, 1)
            reasons.append("partner-country metadata-only candidate")
    score = min(score, 5)
    if score >= 4:
        decision = "priority schema inspection"
    elif score >= 2:
        decision = "keep for manual screening"
    else:
        decision = "low priority unless raw documentation shows missing fields"
    return score, f"{decision}: {'; '.join(reasons) if reasons else 'limited catalog evidence'}"


def build_screening_rows(catalog_rows: list[dict[str, Any]], max_detailed: int = 350) -> list[dict[str, Any]]:
    candidates: list[tuple[dict[str, Any], str]] = []
    for row in catalog_rows:
        ok, reason = is_candidate(row)
        if ok:
            r = dict(row)
            r["_candidate_reason"] = reason
            candidates.append((r, reason))

    def priority_key(item: tuple[dict[str, Any], str]) -> tuple[int, int, str]:
        row, _ = item
        title = str(row.get("title", "")).lower()
        priority = 0
        if row.get("repositoryid") == "lsms":
            priority += 5
        if str(row.get("nation", "")) in LSMS_ISA_COUNTRIES:
            priority += 3
        if any(k in title for k in ["living standards", "integrated household", "household budget", "income and expenditure", "consumption"]):
            priority += 4
        if any(k in title for k in ["phone", "covid", "rapid"]):
            priority -= 2
        return (-priority, -int(row.get("varcount") or 0), str(row.get("title", "")))

    candidates.sort(key=priority_key)
    detailed_rows = [row for row, _ in candidates[:max_detailed]]
    details_by_idno: dict[str, dict[str, Any]] = {}
    with futures.ThreadPoolExecutor(max_workers=8) as executor:
        future_map = {executor.submit(fetch_detail_and_variables, row): row for row in detailed_rows}
        for fut in futures.as_completed(future_map):
            row = future_map[fut]
            try:
                details_by_idno[str(row.get("idno"))] = fut.result()
            except Exception as exc:
                details_by_idno[str(row.get("idno"))] = {"detail_error": str(exc), "variables": []}

    write_json(TEMP_DIR / "api_cache" / "worldbank_variable_screen_cache.json", details_by_idno)

    output_rows: list[dict[str, Any]] = []
    hit_rows: list[dict[str, Any]] = []
    for row, reason in candidates:
        idno = str(row.get("idno", ""))
        packed = details_by_idno.get(idno, {})
        detail = packed.get("detail", {})
        variables = packed.get("variables", [])
        detailed = bool(variables)
        hits = group_hits(variables)
        score, score_reason = score_candidate(hits, row, detail, detailed)

        for group, values in hits.items():
            hit_rows.append(
                {
                    "idno": idno,
                    "country": row.get("nation", ""),
                    "survey_name": row.get("title", ""),
                    "group": group,
                    "n_hits": len(values),
                    "examples": " | ".join(values[:8]),
                }
            )

        wave = f"{row.get('year_start', '')}-{row.get('year_end', '')}" if row.get("year_start") != row.get("year_end") else str(row.get("year_start", ""))
        access = detail.get("data_access_type") or row.get("form_model") or ""
        if detail.get("remote_data_url"):
            access = f"{access}; external repository: {detail.get('remote_data_url')}"

        output_rows.append(
            {
                "country": row.get("nation", ""),
                "survey name": row.get("title", ""),
                "wave/year": wave,
                "public URL": row.get("url", ""),
                "access type": access,
                "file formats": "not available from catalog API; inspect Get Microdata/resources manually",
                "unit": infer_unit(detail, row),
                "sample size": "",
                "panel or repeated cross-section": infer_panel(detail, row),
                "household ID": first_hits(hits, "household_id") or yes_no(hits, "household_id"),
                "person ID": first_hits(hits, "person_id") or yes_no(hits, "person_id"),
                "weights": first_hits(hits, "weights") or yes_no(hits, "weights"),
                "strata": first_hits(hits, "strata") or yes_no(hits, "strata"),
                "PSU/cluster": first_hits(hits, "psu_cluster") or yes_no(hits, "psu_cluster"),
                "interview date": first_hits(hits, "interview_date") or yes_no(hits, "interview_date"),
                "interview month": first_hits(hits, "interview_date") or yes_no(hits, "interview_date"),
                "interview year": "catalog years available" if row.get("year_start") else "",
                "admin1/admin2 geography": first_hits(hits, "admin_geography") or yes_no(hits, "admin_geography"),
                "GPS or cluster coordinates": first_hits(hits, "gps") or yes_no(hits, "gps"),
                "whether GPS is exact, displaced, restricted, or absent": "not determined from catalog metadata",
                "total consumption or income aggregate": first_hits(hits, "total_consumption_income") or yes_no(hits, "total_consumption_income"),
                "food consumption": first_hits(hits, "food_consumption") or yes_no(hits, "food_consumption"),
                "non-food consumption": first_hits(hits, "nonfood_consumption") or yes_no(hits, "nonfood_consumption"),
                "OOP health expenditure": first_hits(hits, "oop_health_expenditure") or yes_no(hits, "oop_health_expenditure"),
                "health-care utilization": first_hits(hits, "health_utilization") or yes_no(hits, "health_utilization"),
                "illness/injury/health need": first_hits(hits, "illness_need") or yes_no(hits, "illness_need"),
                "care-seeking": first_hits(hits, "health_utilization") or yes_no(hits, "health_utilization"),
                "reason for not seeking care": first_hits(hits, "reason_not_sought") or yes_no(hits, "reason_not_sought"),
                "cost barrier": first_hits(hits, "cost_barrier") or yes_no(hits, "cost_barrier"),
                "distance barrier": first_hits(hits, "distance_barrier") or yes_no(hits, "distance_barrier"),
                "supply/drug/staff barrier": first_hits(hits, "supply_barrier") or yes_no(hits, "supply_barrier"),
                "insurance/coverage": first_hits(hits, "insurance") or yes_no(hits, "insurance"),
                "shock module": first_hits(hits, "shock_module") or yes_no(hits, "shock_module"),
                "drought/flood/heat/agricultural shock questions": first_hits(hits, "shock_module") or yes_no(hits, "shock_module"),
                "borrowing/selling assets/coping because of illness or health spending": first_hits(hits, "coping") or yes_no(hits, "coping"),
                "food insecurity": first_hits(hits, "food_insecurity") or yes_no(hits, "food_insecurity"),
                "assets/wealth": first_hits(hits, "assets_wealth") or yes_no(hits, "assets_wealth"),
                "education": first_hits(hits, "education") or yes_no(hits, "education"),
                "household age structure": "requires raw roster or variable-level age hits in next pass",
                "rural/urban": first_hits(hits, "rural_urban") or yes_no(hits, "rural_urban"),
                "agriculture/livelihood variables": first_hits(hits, "agriculture_livelihood") or yes_no(hits, "agriculture_livelihood"),
                "feasibility score from 0 to 5": score,
                "reason for pass/fail": f"{reason}; {score_reason}",
                "screening detail level": "catalog + variable metadata" if detailed else f"catalog only ({packed.get('variables_error') or packed.get('detail_error') or 'not in detailed subset'})",
                "idno": idno,
                "catalog id": row.get("id", ""),
                "collection": row.get("repositoryid", ""),
                "repository": row.get("repo_title", ""),
                "authoring entity": row.get("authoring_entity", ""),
                "doi": row.get("doi", ""),
                "catalog changed": row.get("changed", ""),
                "variable count": row.get("varcount", ""),
            }
        )

    write_csv(TEMP_DIR / "variable_keyword_hits.csv", hit_rows, ["idno", "country", "survey_name", "group", "n_hits", "examples"])
    return output_rows


def write_summary(rows: list[dict[str, Any]]) -> None:
    total = len(rows)
    detailed = sum(1 for r in rows if r["screening detail level"].startswith("catalog + variable"))
    score_counts: dict[str, int] = defaultdict(int)
    country_counts: dict[str, int] = defaultdict(int)
    priority = []
    for r in rows:
        score_counts[str(r["feasibility score from 0 to 5"])] += 1
        country_counts[str(r["country"])] += 1
        try:
            if int(r["feasibility score from 0 to 5"]) >= 4:
                priority.append(r)
        except ValueError:
            pass
    top_countries = sorted(country_counts.items(), key=lambda x: (-x[1], x[0]))[:20]
    priority_sorted = sorted(priority, key=lambda r: (-int(r["feasibility score from 0 to 5"]), r["country"], r["survey name"]))[:30]

    lines = [
        "# Country-Wave Screening Summary",
        "",
        f"Candidate country-waves recorded: {total}",
        f"Records with variable-metadata screening: {detailed}",
        "",
        "## Feasibility Score Counts",
        "",
        "| Score | Count |",
        "|---|---:|",
    ]
    for score in sorted(score_counts, key=lambda x: int(x) if re.match(r"^\d+$", x) else -1, reverse=True):
        lines.append(f"| {score} | {score_counts[score]} |")
    lines.extend(["", "## Top Countries by Candidate Count", "", "| Country | Count |", "|---|---:|"])
    for country, count in top_countries:
        lines.append(f"| {country} | {count} |")
    lines.extend(["", "## Initial Priority Schema-Inspection Candidates", "", "| Country | Wave | Survey | Score | Reason |", "|---|---|---|---:|---|"])
    for r in priority_sorted:
        reason = str(r["reason for pass/fail"]).replace("|", "/")
        lines.append(f"| {r['country']} | {r['wave/year']} | {str(r['survey name']).replace('|', '/')} | {r['feasibility score from 0 to 5']} | {reason[:240]} |")
    lines.extend(
        [
            "",
            "## Interpretation",
            "",
            "This is a screening file, not a final country selection. It uses World Bank catalog metadata plus variable names/labels where available. Final inclusion requires raw file access, schema extraction, questionnaire/codebook checks, survey timing, geography quality, and outcome validation.",
        ]
    )
    (TEMP_DIR / "country_wave_screening_summary.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    ensure_dirs()
    catalog_rows = fetch_catalog()
    screening = build_screening_rows(catalog_rows)
    write_csv(TEMP_DIR / "country_wave_screening.csv", screening, SCREENING_COLUMNS)
    write_summary(screening)
    append_log(
        TEMP_DIR / "audit_log.md",
        f"Built country-wave screening with {len(screening)} candidate rows from World Bank Microdata catalog.",
    )
    print(f"Wrote temp/country_wave_screening.csv with {len(screening)} rows")


if __name__ == "__main__":
    main()
