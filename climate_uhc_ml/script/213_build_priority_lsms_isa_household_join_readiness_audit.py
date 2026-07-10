from __future__ import annotations

import csv
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

import pandas as pd
import pyreadstat

from common import PROJECT_ROOT, REPORT_DIR, RESULT_DIR, TEMP_DIR, append_log, ensure_dirs, write_csv


QUEUE_PATH = TEMP_DIR / "priority_lsms_isa_refocused_acquisition_queue.csv"
FOCUSED_DECISION_PATH = RESULT_DIR / "priority_lsms_isa_requirement_acceptance_decisions.csv"

FILE_AUDIT_PATH = TEMP_DIR / "priority_lsms_isa_household_join_file_audit.csv"
PAIR_AUDIT_PATH = TEMP_DIR / "priority_lsms_isa_household_join_pair_audit.csv"
READINESS_PATH = RESULT_DIR / "priority_lsms_isa_household_join_readiness.csv"
SUMMARY_PATH = RESULT_DIR / "priority_lsms_isa_household_join_readiness_summary.csv"
REPORT_PATH = REPORT_DIR / "priority_lsms_isa_household_join_readiness_audit.md"

RAW_ROOT = TEMP_DIR / "raw_downloads"

FILE_COLUMNS = [
    "download_priority_order",
    "queue_role",
    "country",
    "wave",
    "idno",
    "component",
    "component_role",
    "file_name",
    "relative_path",
    "household_key",
    "person_key",
    "row_count",
    "household_key_present",
    "person_key_present",
    "household_key_nonmissing_rows",
    "distinct_households",
    "duplicate_household_rows",
    "unique_at_household_level",
    "required_variables",
    "required_variables_present",
    "required_variables_missing",
    "required_variables_with_nonmissing_values",
    "nonmissing_required_variable_counts",
    "component_status",
]

PAIR_COLUMNS = [
    "download_priority_order",
    "queue_role",
    "country",
    "wave",
    "idno",
    "base_component",
    "base_file",
    "component",
    "component_file",
    "base_households",
    "component_households",
    "matched_households",
    "base_coverage_rate",
    "component_coverage_rate",
    "pair_status",
]

READINESS_COLUMNS = [
    "download_priority_order",
    "queue_role",
    "country",
    "wave",
    "idno",
    "best_base_component",
    "best_base_file",
    "base_households",
    "consumption_or_income_join_ready",
    "weights_and_design_join_ready",
    "oop_health_expenditure_join_ready",
    "health_need_and_access_join_ready",
    "survey_timing_join_ready",
    "climate_geography_join_ready",
    "household_person_keys_join_ready",
    "complete_household_join_path_ready",
    "focused_requirement_decision_rows",
    "focused_requirements_with_mechanical_hits",
    "focused_raw_value_verified_rows",
    "household_join_readiness_status",
    "data_write_status",
    "modeling_gate_status",
    "remaining_blockers",
]

SUMMARY_COLUMNS = ["metric", "value", "interpretation"]

WAVE_CONFIGS: dict[str, dict[str, Any]] = {
    "NGA_2015_GHSP-W3_v02_M": {
        "key": "hhid",
        "base_components": ["consumption_visit1", "consumption_visit2"],
        "components": [
            {
                "component": "consumption_visit1",
                "role": "consumption_or_income",
                "file": "cons_agg_wave3_visit1.dta",
                "key": "hhid",
                "person_key": "",
                "required": ["hhid", "totcons", "hhweight", "ea"],
            },
            {
                "component": "consumption_visit2",
                "role": "consumption_or_income",
                "file": "cons_agg_wave3_visit2.dta",
                "key": "hhid",
                "person_key": "",
                "required": ["hhid", "totcons", "hhweight", "ea"],
            },
            {
                "component": "health_access_oop",
                "role": "health_need_and_access;oop_health_expenditure",
                "file": "sect4a_harvestw3.dta",
                "key": "hhid",
                "person_key": "indiv",
                "required": [
                    "hhid",
                    "indiv",
                    "s4aq1",
                    "s4aq3",
                    "s4aq6a",
                    "s4aq9",
                    "s4aq10",
                    "s4aq13",
                    "s4aq14",
                    "s4aq15",
                    "s4aq17",
                    "s4aq19",
                    "s4aq21",
                ],
            },
            {
                "component": "survey_timing",
                "role": "survey_timing",
                "file": "secta_harvestw3.dta",
                "key": "hhid",
                "person_key": "",
                "required": ["hhid", "saq13", "saq13d", "saq13m", "saq13y", "saq16", "saq19"],
            },
            {
                "component": "climate_geography",
                "role": "climate_geography",
                "file": "NGA_HouseholdGeovars_Y3.dta",
                "key": "hhid",
                "person_key": "",
                "required": ["hhid", "ea", "LAT_DD_MOD", "LON_DD_MOD"],
            },
            {
                "component": "panel_weights",
                "role": "weights_and_design",
                "file": "HHTrack.dta",
                "key": "hhid",
                "person_key": "",
                "required": ["hhid", "wt_wave3", "wt_w3v1", "wt_w3v2", "wt_w1_w2_w3"],
            },
        ],
        "role_components": {
            "consumption_or_income": ["consumption_visit1", "consumption_visit2"],
            "weights_and_design": ["consumption_visit1", "consumption_visit2", "panel_weights"],
            "oop_health_expenditure": ["health_access_oop"],
            "health_need_and_access": ["health_access_oop"],
            "survey_timing": ["survey_timing"],
            "climate_geography": ["climate_geography"],
            "household_person_keys": ["consumption_visit1", "consumption_visit2", "health_access_oop", "survey_timing", "climate_geography", "panel_weights"],
        },
    },
    "TZA_2012_NPS-R3_v01_M": {
        "key": "y3_hhid",
        "base_components": ["consumption_aggregate"],
        "components": [
            {
                "component": "consumption_aggregate",
                "role": "consumption_or_income;oop_health_expenditure",
                "file": "ConsumptionNPS3.dta",
                "key": "y3_hhid",
                "person_key": "",
                "required": ["y3_hhid", "expm", "expmR", "health", "healthR"],
            },
            {
                "component": "household_header_timing_design",
                "role": "survey_timing;weights_and_design;climate_geography",
                "file": "HH_SEC_A.dta",
                "key": "y3_hhid",
                "person_key": "",
                "required": ["y3_hhid", "y3_cluster", "strataid", "y3_weight", "hh_a04_1", "hh_a04_2", "hh_a18", "hh_a18_1", "hh_a18_2", "hh_a18_3"],
            },
            {
                "component": "health_access_oop",
                "role": "health_need_and_access;oop_health_expenditure",
                "file": "HH_SEC_D.dta",
                "key": "y3_hhid",
                "person_key": "indidy3",
                "required": [
                    "y3_hhid",
                    "indidy3",
                    "hh_d02",
                    "hh_d05_1",
                    "hh_d05_2",
                    "hh_d07",
                    "hh_d08",
                    "hh_d09",
                    "hh_d10",
                    "hh_d13",
                    "hh_d15",
                    "hh_d20",
                ],
            },
            {
                "component": "climate_geography",
                "role": "climate_geography",
                "file": "HouseholdGeovars_Y3.dta",
                "key": "y3_hhid",
                "person_key": "",
                "required": ["y3_hhid", "lat_dd_mod", "lon_dd_mod"],
            },
            {
                "component": "panel_weights",
                "role": "weights_and_design",
                "file": "Y3_weights.dta",
                "key": "y3_hhid",
                "person_key": "",
                "required": ["y3_hhid", "y3_panelweight"],
            },
        ],
        "role_components": {
            "consumption_or_income": ["consumption_aggregate"],
            "weights_and_design": ["household_header_timing_design", "panel_weights"],
            "oop_health_expenditure": ["consumption_aggregate", "health_access_oop"],
            "health_need_and_access": ["health_access_oop"],
            "survey_timing": ["household_header_timing_design"],
            "climate_geography": ["household_header_timing_design", "climate_geography"],
            "household_person_keys": ["consumption_aggregate", "household_header_timing_design", "health_access_oop", "climate_geography", "panel_weights"],
        },
    },
    "TZA_2010_NPS-R2_v03_M": {
        "key": "y2_hhid",
        "base_components": ["consumption_aggregate"],
        "components": [
            {
                "component": "consumption_aggregate",
                "role": "consumption_or_income;oop_health_expenditure;weights_and_design;survey_timing;climate_geography",
                "file": "TZY2.HH.Consumption.dta",
                "key": "y2_hhid",
                "person_key": "",
                "required": ["y2_hhid", "expm", "expmR", "health", "healthR", "hhweight", "strata", "region", "intmonth", "intyear"],
            },
            {
                "component": "household_header_timing_design",
                "role": "survey_timing;weights_and_design;climate_geography",
                "file": "HH_SEC_A.dta",
                "key": "y2_hhid",
                "person_key": "",
                "required": ["y2_hhid", "y2_weight", "clusterid", "strataid", "region", "district", "ward", "ea", "hh_a18_month", "hh_a18_year"],
            },
            {
                "component": "health_access_oop",
                "role": "health_need_and_access;oop_health_expenditure",
                "file": "HH_SEC_D.dta",
                "key": "y2_hhid",
                "person_key": "",
                "required": [
                    "y2_hhid",
                    "hh_d02",
                    "hh_d05_1",
                    "hh_d05_2",
                    "hh_d07",
                    "hh_d08",
                    "hh_d09",
                    "hh_d10",
                    "hh_d13",
                    "hh_d15",
                    "hh_d43",
                    "hh_d48",
                ],
            },
            {
                "component": "climate_geography",
                "role": "climate_geography",
                "file": "HH.Geovariables_Y2.dta",
                "key": "y2_hhid",
                "person_key": "",
                "required": ["y2_hhid", "ea_id", "lat_modified", "lon_modified"],
            },
        ],
        "role_components": {
            "consumption_or_income": ["consumption_aggregate"],
            "weights_and_design": ["consumption_aggregate", "household_header_timing_design"],
            "oop_health_expenditure": ["consumption_aggregate", "health_access_oop"],
            "health_need_and_access": ["health_access_oop"],
            "survey_timing": ["consumption_aggregate", "household_header_timing_design"],
            "climate_geography": ["consumption_aggregate", "household_header_timing_design", "climate_geography"],
            "household_person_keys": ["consumption_aggregate", "household_header_timing_design", "health_access_oop", "climate_geography"],
        },
    },
}


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


def key_values(series: pd.Series) -> set[str]:
    out: set[str] = set()
    for value in series.dropna():
        if isinstance(value, float) and value.is_integer():
            text = str(int(value))
        else:
            text = str(value).strip()
        if text and text.lower() != "nan":
            out.add(text)
    return out


def nonmissing_count(series: pd.Series) -> int:
    if pd.api.types.is_string_dtype(series):
        return int(series.fillna("").astype(str).str.strip().ne("").sum())
    return int(series.notna().sum())


def read_component(wave: dict[str, str], component: dict[str, Any]) -> tuple[dict[str, str], set[str]]:
    idno = clean(wave.get("idno"))
    folder = raw_folder_path(wave.get("local_target_folder", ""), idno)
    path = folder / component["file"]
    key = component["key"]
    person_key = clean(component.get("person_key"))
    required = list(dict.fromkeys(component["required"]))
    base_row = {
        "download_priority_order": clean(wave.get("download_priority_order")),
        "queue_role": clean(wave.get("queue_role")),
        "country": clean(wave.get("country")),
        "wave": clean(wave.get("wave")),
        "idno": idno,
        "component": component["component"],
        "component_role": component["role"],
        "file_name": component["file"],
        "relative_path": rel(path),
        "household_key": key,
        "person_key": person_key,
        "required_variables": "; ".join(required),
    }
    if not path.exists():
        return {
            **base_row,
            "row_count": "0",
            "household_key_present": "0",
            "person_key_present": "0" if person_key else "",
            "household_key_nonmissing_rows": "0",
            "distinct_households": "0",
            "duplicate_household_rows": "0",
            "unique_at_household_level": "0",
            "required_variables_present": "",
            "required_variables_missing": "; ".join(required),
            "required_variables_with_nonmissing_values": "",
            "nonmissing_required_variable_counts": "",
            "component_status": "blocked_missing_file",
        }, set()
    _df_meta, meta = pyreadstat.read_dta(str(path), metadataonly=True)
    columns = list(meta.column_names)
    present = [var for var in required if var in columns]
    missing = [var for var in required if var not in columns]
    usecols = present.copy()
    if key in columns and key not in usecols:
        usecols.append(key)
    if person_key and person_key in columns and person_key not in usecols:
        usecols.append(person_key)
    df, _meta = pyreadstat.read_dta(str(path), usecols=usecols)
    row_count = len(df)
    key_present = key in df.columns
    person_present = person_key in df.columns if person_key else False
    hkeys = key_values(df[key]) if key_present else set()
    key_nonmissing = nonmissing_count(df[key]) if key_present else 0
    duplicate_rows = max(0, key_nonmissing - len(hkeys))
    nonmissing_by_var = {var: nonmissing_count(df[var]) for var in present if var in df.columns}
    nonmissing_present = [var for var, count in nonmissing_by_var.items() if count > 0]
    unique_at_hh = "1" if key_present and key_nonmissing == len(hkeys) and row_count == len(hkeys) else "0"
    if missing:
        status = "blocked_required_variables_missing"
    elif not key_present or key_nonmissing == 0:
        status = "blocked_household_key_missing_or_empty"
    elif not nonmissing_present:
        status = "blocked_required_variables_empty"
    elif duplicate_rows == 0:
        status = "household_level_component_ready_for_join_audit"
    else:
        status = "person_or_item_level_component_ready_for_household_aggregation_review"
    return {
        **base_row,
        "row_count": str(row_count),
        "household_key_present": "1" if key_present else "0",
        "person_key_present": "1" if person_present else ("0" if person_key else ""),
        "household_key_nonmissing_rows": str(key_nonmissing),
        "distinct_households": str(len(hkeys)),
        "duplicate_household_rows": str(duplicate_rows),
        "unique_at_household_level": unique_at_hh,
        "required_variables_present": "; ".join(present),
        "required_variables_missing": "; ".join(missing),
        "required_variables_with_nonmissing_values": "; ".join(nonmissing_present),
        "nonmissing_required_variable_counts": "; ".join(f"{var}:{count}" for var, count in nonmissing_by_var.items()),
        "component_status": status,
    }, hkeys


def pair_row(wave: dict[str, str], base: dict[str, str], component: dict[str, str], base_keys: set[str], component_keys: set[str]) -> dict[str, str]:
    matched = base_keys & component_keys
    base_count = len(base_keys)
    component_count = len(component_keys)
    base_rate = (len(matched) / base_count) if base_count else 0
    component_rate = (len(matched) / component_count) if component_count else 0
    if not base_keys or not component_keys:
        status = "blocked_missing_household_keys"
    elif base_rate >= 0.95:
        status = "join_ready_ge95_base_coverage"
    elif base_rate >= 0.80:
        status = "partial_join_80_95_base_coverage"
    else:
        status = "blocked_low_base_coverage"
    return {
        "download_priority_order": clean(wave.get("download_priority_order")),
        "queue_role": clean(wave.get("queue_role")),
        "country": clean(wave.get("country")),
        "wave": clean(wave.get("wave")),
        "idno": clean(wave.get("idno")),
        "base_component": clean(base.get("component")),
        "base_file": clean(base.get("file_name")),
        "component": clean(component.get("component")),
        "component_file": clean(component.get("file_name")),
        "base_households": str(base_count),
        "component_households": str(component_count),
        "matched_households": str(len(matched)),
        "base_coverage_rate": f"{base_rate:.6f}",
        "component_coverage_rate": f"{component_rate:.6f}",
        "pair_status": status,
    }


def role_ready(
    role: str,
    config: dict[str, Any],
    file_by_component: dict[str, dict[str, str]],
    pair_by_base_component: dict[tuple[str, str], dict[str, str]],
    best_base: str,
) -> bool:
    components = config["role_components"][role]
    for component_name in components:
        file_row = file_by_component.get(component_name, {})
        if "blocked" in clean(file_row.get("component_status")):
            continue
        if component_name == best_base:
            return True
        pair = pair_by_base_component.get((best_base, component_name), {})
        if clean(pair.get("pair_status")) == "join_ready_ge95_base_coverage":
            return True
    return False


def focused_stats(rows: list[dict[str, str]], idno: str) -> tuple[int, int, int]:
    wave_rows = [row for row in rows if clean(row.get("idno")) == idno]
    mechanical = sum(1 for row in wave_rows if clean(row.get("mechanical_raw_check_decision")).startswith("mechanical_"))
    verified = sum(1 for row in wave_rows if clean(row.get("final_verification_decision")).startswith("raw_value_verified"))
    return len(wave_rows), mechanical, verified


def build_outputs() -> tuple[list[dict[str, str]], list[dict[str, str]], list[dict[str, str]], list[dict[str, str]]]:
    queue_rows = [row for row in read_csv_dicts(QUEUE_PATH) if clean(row.get("idno")) in WAVE_CONFIGS]
    focused_rows = read_csv_dicts(FOCUSED_DECISION_PATH)
    file_rows: list[dict[str, str]] = []
    pair_rows: list[dict[str, str]] = []
    readiness_rows: list[dict[str, str]] = []
    for wave in queue_rows:
        idno = clean(wave.get("idno"))
        config = WAVE_CONFIGS[idno]
        file_by_component: dict[str, dict[str, str]] = {}
        keys_by_component: dict[str, set[str]] = {}
        for component in config["components"]:
            file_row, keys = read_component(wave, component)
            file_rows.append(file_row)
            file_by_component[component["component"]] = file_row
            keys_by_component[component["component"]] = keys
        base_candidates = config["base_components"]
        pair_by_base_component: dict[tuple[str, str], dict[str, str]] = {}
        for base_name in base_candidates:
            base_row = file_by_component[base_name]
            for component_name, component_row in file_by_component.items():
                if component_name == base_name:
                    continue
                row = pair_row(wave, base_row, component_row, keys_by_component[base_name], keys_by_component[component_name])
                pair_rows.append(row)
                pair_by_base_component[(base_name, component_name)] = row
        best_base = max(
            base_candidates,
            key=lambda base: sum(
                1
                for component in file_by_component
                if component != base and clean(pair_by_base_component.get((base, component), {}).get("pair_status")) == "join_ready_ge95_base_coverage"
            ),
        )
        focused_count, focused_mechanical, focused_verified = focused_stats(focused_rows, idno)
        role_status = {
            role: role_ready(role, config, file_by_component, pair_by_base_component, best_base)
            for role in [
                "consumption_or_income",
                "weights_and_design",
                "oop_health_expenditure",
                "health_need_and_access",
                "survey_timing",
                "climate_geography",
                "household_person_keys",
            ]
        }
        complete_join = all(role_status.values())
        blockers = []
        if not complete_join:
            blockers.append("one_or_more_required_components_not_join_ready_at_household_level")
        if focused_verified == 0:
            blockers.append("raw_value_verification_still_requires_reviewer_acceptance")
        blockers.append("climate_exposure_route_not_accepted_for_this_wave")
        readiness_rows.append(
            {
                "download_priority_order": clean(wave.get("download_priority_order")),
                "queue_role": clean(wave.get("queue_role")),
                "country": clean(wave.get("country")),
                "wave": clean(wave.get("wave")),
                "idno": idno,
                "best_base_component": best_base,
                "best_base_file": clean(file_by_component[best_base].get("file_name")),
                "base_households": clean(file_by_component[best_base].get("distinct_households")),
                "consumption_or_income_join_ready": "1" if role_status["consumption_or_income"] else "0",
                "weights_and_design_join_ready": "1" if role_status["weights_and_design"] else "0",
                "oop_health_expenditure_join_ready": "1" if role_status["oop_health_expenditure"] else "0",
                "health_need_and_access_join_ready": "1" if role_status["health_need_and_access"] else "0",
                "survey_timing_join_ready": "1" if role_status["survey_timing"] else "0",
                "climate_geography_join_ready": "1" if role_status["climate_geography"] else "0",
                "household_person_keys_join_ready": "1" if role_status["household_person_keys"] else "0",
                "complete_household_join_path_ready": "1" if complete_join else "0",
                "focused_requirement_decision_rows": str(focused_count),
                "focused_requirements_with_mechanical_hits": str(focused_mechanical),
                "focused_raw_value_verified_rows": str(focused_verified),
                "household_join_readiness_status": "household_join_path_ready_value_verification_and_climate_blocked" if complete_join else "household_join_path_incomplete",
                "data_write_status": "blocked_join_audit_only",
                "modeling_gate_status": "blocked",
                "remaining_blockers": "; ".join(blockers),
            }
        )
    summary_rows = build_summary(file_rows, pair_rows, readiness_rows)
    return file_rows, pair_rows, readiness_rows, summary_rows


def build_summary(
    file_rows: list[dict[str, str]],
    pair_rows: list[dict[str, str]],
    readiness_rows: list[dict[str, str]],
) -> list[dict[str, str]]:
    component_counts = Counter(row.get("component_status", "") for row in file_rows)
    pair_counts = Counter(row.get("pair_status", "") for row in pair_rows)
    rows = [
        {"metric": "priority_lsms_household_join_dataset_rows", "value": str(len(readiness_rows)), "interpretation": "Received raw country-waves included in household join readiness audit."},
        {"metric": "priority_lsms_household_join_file_audit_rows", "value": str(len(file_rows)), "interpretation": "Core component files audited for household keys and required variables."},
        {"metric": "priority_lsms_household_join_pair_audit_rows", "value": str(len(pair_rows)), "interpretation": "Base-to-component household join coverage rows."},
        {"metric": "priority_lsms_household_join_complete_join_path_rows", "value": str(sum(1 for row in readiness_rows if row["complete_household_join_path_ready"] == "1")), "interpretation": "Country-waves with all required modules join-ready at household level."},
        {"metric": "priority_lsms_household_join_raw_value_verified_rows", "value": str(sum(safe_int(row.get("focused_raw_value_verified_rows")) for row in readiness_rows)), "interpretation": "Focused requirements already accepted as raw-value verified; should remain zero until reviewer acceptance."},
        {"metric": "priority_lsms_household_join_data_write_status", "value": "blocked_join_audit_only", "interpretation": "Household join readiness audit does not write promoted data."},
        {"metric": "modeling_gate_status", "value": "blocked", "interpretation": "Models remain blocked until promoted registry thresholds and accepted climate linkage pass."},
    ]
    for status, count in sorted(component_counts.items()):
        rows.append({"metric": f"priority_lsms_household_join_component_status_{status}", "value": str(count), "interpretation": "Core file component status count."})
    for status, count in sorted(pair_counts.items()):
        rows.append({"metric": f"priority_lsms_household_join_pair_status_{status}", "value": str(count), "interpretation": "Household join pair status count."})
    return rows


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


def write_report(
    file_rows: list[dict[str, str]],
    pair_rows: list[dict[str, str]],
    readiness_rows: list[dict[str, str]],
    summary_rows: list[dict[str, str]],
) -> None:
    summary_table = "\n".join(f"| {row['metric']} | {row['value']} | {row['interpretation']} |" for row in summary_rows)
    readiness_table = markdown_table(
        readiness_rows,
        [
            "idno",
            "best_base_file",
            "base_households",
            "complete_household_join_path_ready",
            "focused_raw_value_verified_rows",
            "household_join_readiness_status",
        ],
        10,
    )
    file_table = markdown_table(
        file_rows,
        ["idno", "component", "file_name", "row_count", "distinct_households", "required_variables_missing", "component_status"],
        20,
    )
    pair_table = markdown_table(
        sorted(pair_rows, key=lambda row: (row.get("idno", ""), row.get("base_file", ""), row.get("pair_status", ""))),
        ["idno", "base_file", "component_file", "matched_households", "base_coverage_rate", "pair_status"],
        20,
    )
    REPORT_PATH.write_text(
        f"""# Priority LSMS-ISA Household Join Readiness Audit

Status: raw-backed household join audit for the received Nigeria 2015,
Tanzania 2010, and Tanzania 2012 LSMS/ISA packages. This is a
promotion-control artifact; it does not write to `data/` and does not mark any
requirement as value-verified.

## Summary

| Metric | Value | Interpretation |
|---|---:|---|
{summary_table}

## Wave Readiness

{readiness_table}

## Core File Audit

{file_table}

## Join Coverage Preview

{pair_table}

## Stop Rule

Even when the household join path is ready, country-waves remain blocked from
promotion until reviewer acceptance verifies raw values, value labels, units,
recall periods, missing codes, skip patterns, merge levels, and an accepted
CHIRPS or ERA5 climate linkage route.
""",
        encoding="utf-8",
    )


def main() -> None:
    ensure_dirs()
    file_rows, pair_rows, readiness_rows, summary_rows = build_outputs()
    write_csv(FILE_AUDIT_PATH, file_rows, FILE_COLUMNS)
    write_csv(PAIR_AUDIT_PATH, pair_rows, PAIR_COLUMNS)
    write_csv(READINESS_PATH, readiness_rows, READINESS_COLUMNS)
    write_csv(SUMMARY_PATH, summary_rows, SUMMARY_COLUMNS)
    write_report(file_rows, pair_rows, readiness_rows, summary_rows)
    append_log(
        TEMP_DIR / "audit_log.md",
        "Built priority LSMS/ISA household join readiness audit; data writes and modeling remain blocked.",
    )
    print(
        "Priority LSMS/ISA household join readiness "
        f"datasets={len(readiness_rows)} files={len(file_rows)} pairs={len(pair_rows)}."
    )


if __name__ == "__main__":
    main()
