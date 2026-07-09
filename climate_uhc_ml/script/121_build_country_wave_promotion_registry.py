from __future__ import annotations

import csv
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

from common import DATA_DIR, REPORT_DIR, RESULT_DIR, TEMP_DIR, append_log, ensure_dirs, write_csv


TARGETS_PATH = RESULT_DIR / "minimum_viable_acquisition_targets.csv"
INTAKE_PATH = TEMP_DIR / "raw_download_intake_manifest.csv"
EXPECTED_PATH = TEMP_DIR / "raw_download_expected_files.csv"
CONCEPT_PATH = TEMP_DIR / "raw_ingestion_concept_checklist.csv"
PROTOCOL_PATH = TEMP_DIR / "raw_variable_verification_protocol.csv"
CURRENT_LINKED_PATH = DATA_DIR / "climate_linked_household.csv"

REGISTRY_PATH = RESULT_DIR / "promoted_country_wave_registry.csv"
GATE_AUDIT_PATH = RESULT_DIR / "country_wave_promotion_gate_audit.csv"
SUMMARY_PATH = RESULT_DIR / "country_wave_promotion_summary.csv"
QUEUE_PATH = RESULT_DIR / "priority_country_wave_download_queue.csv"
PACKET_DIR = REPORT_DIR / "country_wave_promotion_packets"
REPORT_PATH = REPORT_DIR / "country_wave_promotion_registry.md"

PRIORITY_COUNTRIES = {"Ethiopia", "Nigeria", "Malawi", "Tanzania", "Uganda"}
ALBANIA_DIAGNOSTIC_LIMIT = "climate_linked_che_diagnostic_only_not_for_promoted_descriptive_ml_causal_or_policy_analysis"
REQUIRED_CONCEPTS = [
    "household_id",
    "survey_weight",
    "psu_cluster",
    "strata",
    "total_consumption_or_income",
    "oop_health_expenditure",
    "health_need",
    "care_or_barrier",
    "survey_timing",
    "climate_geography",
]
FINANCIAL_CONCEPTS = {"household_id", "survey_weight", "total_consumption_or_income", "oop_health_expenditure", "survey_timing", "climate_geography"}
ACCESS_CONCEPTS = {"health_need", "care_or_barrier"}

REGISTRY_COLUMNS = [
    "country",
    "wave",
    "idno",
    "survey_name",
    "priority_country",
    "source",
    "official_url",
    "local_target_folder",
    "rows",
    "outcome_ready_status",
    "sdg382_ready_status",
    "che10_che25_ready_status",
    "access_forgone_care_ready_status",
    "climate_linkage_ready_status",
    "analysis_ready_status",
    "raw_package_status",
    "raw_value_verification_status",
    "promotion_packet",
    "remaining_blockers",
]

GATE_COLUMNS = [
    "country",
    "wave",
    "idno",
    "gate",
    "status",
    "evidence",
    "required_action",
]

SUMMARY_COLUMNS = ["metric", "value", "interpretation"]
QUEUE_COLUMNS = [
    "action_rank",
    "country",
    "wave",
    "idno",
    "survey_name",
    "official_url",
    "local_target_folder",
    "raw_package_status",
    "top_expected_files_or_modules",
    "promotion_packet",
    "next_action",
]


def read_csv_dicts(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        return []
    with path.open(encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def relative(path: Path) -> str:
    try:
        return str(path.relative_to(TEMP_DIR.parent)).replace("\\", "/")
    except ValueError:
        return str(path).replace("\\", "/")


def safe_int(value: Any, default: int = 0) -> int:
    try:
        return int(float(str(value).strip()))
    except (TypeError, ValueError):
        return default


def compact(values: list[str], limit: int = 8) -> str:
    seen: set[str] = set()
    out: list[str] = []
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


def one_by_id(rows: list[dict[str, str]], field: str = "dataset_idno") -> dict[str, dict[str, str]]:
    out: dict[str, dict[str, str]] = {}
    for row in rows:
        idno = row.get(field, "").strip()
        if idno and idno not in out:
            out[idno] = row
    return out


def unique_targets(rows: list[dict[str, str]]) -> list[dict[str, str]]:
    best: dict[str, dict[str, str]] = {}
    sets: dict[str, list[str]] = defaultdict(list)
    for row in rows:
        idno = row.get("idno", "").strip()
        if not idno:
            continue
        if row.get("acquisition_set") not in sets[idno]:
            sets[idno].append(row.get("acquisition_set", ""))
        current = best.get(idno)
        rank = safe_int(row.get("quality_rank"), 999999)
        if current is None or rank < safe_int(current.get("quality_rank"), 999999):
            best[idno] = dict(row)
    out = []
    for idno, row in best.items():
        row["included_acquisition_sets"] = ";".join(s for s in sets[idno] if s)
        out.append(row)
    return sorted(out, key=lambda r: (r.get("country", ""), str(r.get("wave", "")), r.get("idno", "")))


def concept_statuses(rows: list[dict[str, str]]) -> dict[str, str]:
    statuses: dict[str, str] = {}
    for row in rows:
        concept = row.get("concept", "").strip()
        if not concept:
            continue
        statuses[concept] = row.get("raw_verification_status", "") or row.get("verification_status", "")
    return statuses


def protocol_counts(rows: list[dict[str, str]]) -> Counter[str]:
    return Counter(row.get("verification_status", "") for row in rows)


def all_concepts_verified(concepts: set[str], statuses: dict[str, str]) -> bool:
    return bool(concepts) and all(statuses.get(concept) in {"raw_value_verified", "verified"} for concept in concepts)


def raw_package_status(intake: dict[str, str]) -> str:
    if not intake:
        return "missing_raw_intake_row"
    tabular = safe_int(intake.get("raw_tabular_file_count"))
    archives = safe_int(intake.get("archive_file_count"))
    docs = safe_int(intake.get("documentation_file_count"))
    expected = safe_int(intake.get("expected_core_module_rows"))
    if tabular > 0 and expected > 0:
        return "raw_tabular_files_present_needs_schema_and_value_verification"
    if archives > 0 and expected > 0:
        return "archive_present_needs_extraction_schema_and_value_verification"
    if docs > 0:
        return "documentation_or_placeholder_only_no_raw_microdata"
    return "raw_package_missing"


def status_from_bool(ok: bool, ready: str, blocked: str) -> str:
    return ready if ok else blocked


def current_albania_diagnostic_row() -> dict[str, str] | None:
    if not CURRENT_LINKED_PATH.exists():
        return None
    with CURRENT_LINKED_PATH.open(encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        rows = 0
        countries: set[str] = set()
        waves: set[str] = set()
        limited = False
        for row in reader:
            rows += 1
            if row.get("country"):
                countries.add(row["country"])
            if row.get("wave"):
                waves.add(row["wave"])
            if row.get("data_use_limit") == ALBANIA_DIAGNOSTIC_LIMIT:
                limited = True
    if not rows:
        return None
    if not limited:
        return None
    return {
        "country": compact(sorted(countries)) or "Albania",
        "wave": compact(sorted(waves)) or "2002",
        "idno": "ALB_2002_LSMS_v01_M",
        "survey_name": "Living Standards Measurement Survey 2002",
        "priority_country": "0",
        "source": "current_diagnostic_template",
        "official_url": "",
        "local_target_folder": "data/climate_linked_household.csv",
        "rows": str(rows),
        "outcome_ready_status": "diagnostic_che_only_not_promoted",
        "sdg382_ready_status": "blocked_not_constructed",
        "che10_che25_ready_status": "diagnostic_ready_not_promoted",
        "access_forgone_care_ready_status": "blocked_not_promoted",
        "climate_linkage_ready_status": "diagnostic_nasa_power_admin_centroid_not_accepted_chirps_era5",
        "analysis_ready_status": "not_promoted_diagnostic_template_only",
        "raw_package_status": "local_albania_raw_partially_processed",
        "raw_value_verification_status": "limited_diagnostic_only",
        "promotion_packet": "report/alb2002_limited_climate_linked_promotion.md",
        "remaining_blockers": "Historical boundary/timing/outcome gates unresolved; keep Albania as diagnostic template only.",
    }


def build_packet(row: dict[str, str], gates: list[dict[str, str]], expected_rows: list[dict[str, str]], protocol_rows: list[dict[str, str]]) -> str:
    packet_path = PACKET_DIR / f"{row['idno']}.md"
    expected_lines = "\n".join(
        f"- `{r.get('expected_file_name', '')}`: {r.get('expected_file_status', '')}; concepts={r.get('candidate_harmonized_variables', '')}"
        for r in expected_rows[:12]
    )
    if not expected_lines:
        expected_lines = "- No expected file rows found."
    protocol_lines = "\n".join(
        f"- `{r.get('candidate_files', '')}` / `{r.get('candidate_raw_variable', '')}`: {r.get('concept', '')}; {r.get('verification_status', '')}; action={r.get('verification_action', '')}"
        for r in protocol_rows[:16]
    )
    if not protocol_lines:
        protocol_lines = "- No variable verification protocol rows found."
    gate_table = "\n".join(
        f"| {g['gate']} | {g['status']} | {g['evidence']} | {g['required_action']} |"
        for g in gates
    )
    text = f"""# Country-Wave Promotion Packet: {row['country']} {row['wave']}

Dataset: `{row['survey_name']}`

IDNO: `{row['idno']}`

Official URL: {row.get('official_url', '')}

Local target folder: `{row.get('local_target_folder', '')}`

Current registry status: `{row['analysis_ready_status']}`

## Gate Summary

| Gate | Status | Evidence | Required action |
|---|---|---|---|
{gate_table}

## Expected Files or Modules

{expected_lines}

## Raw Variable Verification Queue

{protocol_lines}

## Promotion Rule

Do not write this country-wave into `data/` until the raw package is complete,
merge keys and survey design are verified, financial-protection and access
variables pass value/unit/recall/missing-code checks, and a CHIRPS or ERA5
climate-linkage route is accepted.
"""
    packet_path.write_text(text, encoding="utf-8")
    return relative(packet_path)


def main() -> None:
    ensure_dirs()
    PACKET_DIR.mkdir(parents=True, exist_ok=True)

    targets = unique_targets(read_csv_dicts(TARGETS_PATH))
    intake_by_id = one_by_id(read_csv_dicts(INTAKE_PATH))
    expected_by_id = by_id(read_csv_dicts(EXPECTED_PATH), "dataset_idno")
    concept_by_id = by_id(read_csv_dicts(CONCEPT_PATH))
    protocol_by_id = by_id(read_csv_dicts(PROTOCOL_PATH))

    registry_rows: list[dict[str, str]] = []
    gate_rows: list[dict[str, str]] = []
    queue_rows: list[dict[str, str]] = []

    for target in targets:
        idno = target.get("idno", "")
        country = target.get("country", "")
        wave = target.get("wave", "")
        intake = intake_by_id.get(idno, {})
        expected = expected_by_id.get(idno, [])
        concepts = concept_statuses(concept_by_id.get(idno, []))
        protocol_rows = protocol_by_id.get(idno, [])
        p_counts = protocol_counts(protocol_rows)

        raw_status = raw_package_status(intake)
        raw_complete = raw_status in {
            "raw_tabular_files_present_needs_schema_and_value_verification",
            "archive_present_needs_extraction_schema_and_value_verification",
        }
        value_verified = p_counts.get("raw_value_verified", 0) > 0 and p_counts.get("raw_not_inspected", 0) == 0
        financial_ready = raw_complete and value_verified and all_concepts_verified(FINANCIAL_CONCEPTS, concepts)
        access_ready = raw_complete and value_verified and all_concepts_verified(ACCESS_CONCEPTS, concepts)
        climate_ready = raw_complete and value_verified and all_concepts_verified({"survey_timing", "climate_geography"}, concepts)
        analysis_ready = financial_ready and climate_ready
        double_failure_ready = financial_ready and access_ready

        blockers = []
        if not raw_complete:
            blockers.append("complete original raw package not present")
        if p_counts.get("raw_not_inspected", 0) or not value_verified:
            blockers.append("raw values, labels, units, recall periods, missing codes, and merge keys not verified")
        missing_concepts = [concept for concept in REQUIRED_CONCEPTS if concepts.get(concept) not in {"raw_value_verified", "verified"}]
        if missing_concepts:
            blockers.append("unverified required concepts: " + ",".join(missing_concepts[:10]))
        if not climate_ready:
            blockers.append("no accepted CHIRPS/ERA5 climate-linkage route")

        row = {
            "country": country,
            "wave": wave,
            "idno": idno,
            "survey_name": target.get("survey_name", ""),
            "priority_country": "1" if country in PRIORITY_COUNTRIES else "0",
            "source": "minimum_viable_acquisition_plan",
            "official_url": target.get("official_url", ""),
            "local_target_folder": target.get("local_target_folder", ""),
            "rows": "0",
            "outcome_ready_status": status_from_bool(financial_ready or access_ready, "ready", "blocked_raw_value_verification_required"),
            "sdg382_ready_status": "blocked_poverty_line_ppp_cpi_discretionary_budget_not_verified",
            "che10_che25_ready_status": status_from_bool(financial_ready, "ready", "blocked_consumption_oop_units_recall_not_verified"),
            "access_forgone_care_ready_status": status_from_bool(access_ready, "ready", "blocked_health_need_care_access_values_not_verified"),
            "climate_linkage_ready_status": status_from_bool(climate_ready, "ready", "blocked_timing_geography_or_chirps_era5_route_not_verified"),
            "analysis_ready_status": status_from_bool(analysis_ready, "promoted_analysis_ready", "not_promoted"),
            "raw_package_status": raw_status,
            "raw_value_verification_status": "verified" if value_verified else "raw_not_value_verified",
            "promotion_packet": "",
            "remaining_blockers": "; ".join(blockers),
        }

        gates = [
            {
                "country": country,
                "wave": wave,
                "idno": idno,
                "gate": "complete_original_raw_package",
                "status": "pass" if raw_complete else "fail",
                "evidence": f"intake_status={intake.get('intake_status', '')}; tabular={intake.get('raw_tabular_file_count', '0')}; archives={intake.get('archive_file_count', '0')}; docs={intake.get('documentation_file_count', '0')}",
                "required_action": "" if raw_complete else "Place complete original raw archive/tabular package and documentation in the local target folder.",
            },
            {
                "country": country,
                "wave": wave,
                "idno": idno,
                "gate": "raw_value_unit_recall_missing_verification",
                "status": "pass" if value_verified else "fail",
                "evidence": "; ".join(f"{k}={v}" for k, v in sorted(p_counts.items()) if k),
                "required_action": "" if value_verified else "Inspect raw labels/values, merge keys, units, recall periods, skip patterns, and missing codes.",
            },
            {
                "country": country,
                "wave": wave,
                "idno": idno,
                "gate": "financial_protection_che10_che25",
                "status": "pass" if financial_ready else "fail",
                "evidence": compact([f"{c}:{concepts.get(c, 'missing')}" for c in sorted(FINANCIAL_CONCEPTS)]),
                "required_action": "" if financial_ready else "Verify total consumption/income, OOP health expenditure, weights, timing, geography, and merge keys.",
            },
            {
                "country": country,
                "wave": wave,
                "idno": idno,
                "gate": "access_forgone_care",
                "status": "pass" if access_ready else "fail",
                "evidence": compact([f"{c}:{concepts.get(c, 'missing')}" for c in sorted(ACCESS_CONCEPTS)]),
                "required_action": "" if access_ready else "Verify illness/need denominator, care seeking, and cost/distance/supply barrier semantics.",
            },
            {
                "country": country,
                "wave": wave,
                "idno": idno,
                "gate": "climate_linkage",
                "status": "pass" if climate_ready else "fail",
                "evidence": compact([f"{c}:{concepts.get(c, 'missing')}" for c in ["survey_timing", "climate_geography"]]),
                "required_action": "" if climate_ready else "Verify survey month/date, usable admin/GPS/cluster geography, and accepted CHIRPS/ERA5 extraction route.",
            },
            {
                "country": country,
                "wave": wave,
                "idno": idno,
                "gate": "double_failure",
                "status": "pass" if double_failure_ready else "fail",
                "evidence": f"financial_ready={int(financial_ready)}; access_ready={int(access_ready)}",
                "required_action": "" if double_failure_ready else "Pass both financial-protection and access/forgone-care value verification gates.",
            },
        ]
        row["promotion_packet"] = build_packet(row, gates, expected, protocol_rows)
        registry_rows.append(row)
        gate_rows.extend(gates)

        if row["priority_country"] == "1" and row["analysis_ready_status"] != "promoted_analysis_ready":
            top_expected = compact([item.get("expected_file_name", "") for item in expected[:10]], limit=10)
            if raw_status == "documentation_or_placeholder_only_no_raw_microdata":
                next_action = "Download/place complete original raw package and documentation in local_target_folder."
            elif raw_status == "archive_present_needs_extraction_schema_and_value_verification":
                next_action = "Extract archive, run raw schema inspection, then value/unit/recall/missing-code verification."
            elif raw_status == "raw_tabular_files_present_needs_schema_and_value_verification":
                next_action = "Run raw schema inspection and raw value/unit/recall/missing-code verification."
            else:
                next_action = "Create target folder and place complete original raw package plus documentation."
            queue_rows.append(
                {
                    "action_rank": "",
                    "country": country,
                    "wave": wave,
                    "idno": idno,
                    "survey_name": target.get("survey_name", ""),
                    "official_url": target.get("official_url", ""),
                    "local_target_folder": target.get("local_target_folder", ""),
                    "raw_package_status": raw_status,
                    "top_expected_files_or_modules": top_expected,
                    "promotion_packet": row["promotion_packet"],
                    "next_action": next_action,
                }
            )

    diagnostic = current_albania_diagnostic_row()
    if diagnostic:
        registry_rows.append(diagnostic)

    priority_rows = [r for r in registry_rows if r.get("priority_country") == "1"]
    promoted_rows = [r for r in registry_rows if r.get("analysis_ready_status") == "promoted_analysis_ready"]
    financial_countries = sorted({r["country"] for r in registry_rows if r.get("che10_che25_ready_status") == "ready"})
    double_failure_rows = [r for r in registry_rows if r.get("che10_che25_ready_status") == "ready" and r.get("access_forgone_care_ready_status") == "ready"]
    accepted_climate_rows = [r for r in registry_rows if r.get("climate_linkage_ready_status") == "ready"]

    summary_rows = [
        {"metric": "registry_rows", "value": len(registry_rows), "interpretation": "Country-waves currently tracked for promotion, including Albania diagnostic template if present."},
        {"metric": "priority_country_rows", "value": len(priority_rows), "interpretation": "Rows from Ethiopia, Nigeria, Malawi, Tanzania, and Uganda."},
        {"metric": "promoted_analysis_ready_rows", "value": len(promoted_rows), "interpretation": "Rows allowed into promoted analysis data."},
        {"metric": "financial_protection_ready_countries", "value": len(financial_countries), "interpretation": "Countries meeting value-verified CHE financial-protection requirements."},
        {"metric": "double_failure_ready_country_waves", "value": len(double_failure_rows), "interpretation": "Country-waves with both financial protection and access/forgone-care ready."},
        {"metric": "accepted_chirps_era5_climate_linkage_rows", "value": len(accepted_climate_rows), "interpretation": "Country-waves with accepted CHIRPS or ERA5 linkage route."},
        {"metric": "modeling_gate_status", "value": "blocked", "interpretation": "Do not run predictive, reduced-form, causal ML, or policy-learning models until registry thresholds pass."},
    ]

    write_csv(REGISTRY_PATH, registry_rows, REGISTRY_COLUMNS)
    write_csv(GATE_AUDIT_PATH, gate_rows, GATE_COLUMNS)
    queue_rows = sorted(queue_rows, key=lambda r: (r["country"], str(r["wave"]), r["idno"]))
    for rank, row in enumerate(queue_rows, start=1):
        row["action_rank"] = str(rank)
    write_csv(QUEUE_PATH, queue_rows, QUEUE_COLUMNS)
    write_csv(SUMMARY_PATH, summary_rows, SUMMARY_COLUMNS)

    blocked_for_modeling = (
        len(financial_countries) < 6
        or len(double_failure_rows) < 10
        or len(accepted_climate_rows) < 1
    )
    table_rows = "\n".join(
        f"| {r['country']} | {r['wave']} | `{r['idno']}` | {r['che10_che25_ready_status']} | {r['access_forgone_care_ready_status']} | {r['climate_linkage_ready_status']} | {r['analysis_ready_status']} | {r['remaining_blockers']} |"
        for r in registry_rows[:60]
    )
    REPORT_PATH.write_text(
        f"""# Country-Wave Promotion Registry

Status: dataset-promotion mode is active. Modeling remains {'blocked' if blocked_for_modeling else 'allowed by registry thresholds'}.

The registry is `result/promoted_country_wave_registry.csv`. It is fail-closed:
country-waves are not written to promoted `data/` outputs unless raw packages,
value verification, outcome gates, and accepted climate linkage all pass.

## Thresholds

| Requirement | Current | Required | Status |
|---|---:|---:|---|
| Value-verified financial-protection countries | {len(financial_countries)} | 6 | {'pass' if len(financial_countries) >= 6 else 'fail'} |
| Double-failure-ready country-waves | {len(double_failure_rows)} | 10 | {'pass' if len(double_failure_rows) >= 10 else 'fail'} |
| Accepted CHIRPS/ERA5 climate-linkage routes | {len(accepted_climate_rows)} | 1 | {'pass' if len(accepted_climate_rows) >= 1 else 'fail'} |

## Current Registry Preview

| Country | Wave | IDNO | CHE10/CHE25 | Access/Forgone care | Climate linkage | Analysis-ready | Remaining blockers |
|---|---|---|---|---|---|---|---|
{table_rows}

## Next Actions

1. Populate complete original raw packages and documentation for the priority LSMS/LSMS-ISA waves.
   Start with `result/priority_country_wave_download_queue.csv`.
2. Run raw schema extraction and value verification for household/person merge keys, weights, consumption/OOP, illness/access, timing, geography, units, recall periods, skip patterns, and missing codes.
3. Promote only passing country-waves into clean multi-country `data/` outputs.
4. Re-run models only after the registry thresholds pass.
""",
        encoding="utf-8",
    )

    append_log(TEMP_DIR / "audit_log.md", f"Built country-wave promotion registry rows={len(registry_rows)} promoted={len(promoted_rows)}.")
    print(f"Country-wave promotion registry rows={len(registry_rows)} promoted={len(promoted_rows)}.")


if __name__ == "__main__":
    main()
