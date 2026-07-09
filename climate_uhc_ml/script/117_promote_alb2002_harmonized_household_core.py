from __future__ import annotations

import csv
from pathlib import Path
from typing import Any

import pandas as pd

from common import DATA_DIR, REPORT_DIR, RESULT_DIR, TEMP_DIR, append_log, ensure_dirs, write_csv


IDNO = "ALB_2002_LSMS_v01_M"
COUNTRY = "Albania"
SURVEY_NAME = "Living Standards Measurement Survey 2002"
WAVE = "2002"

SOURCE_PATH = TEMP_DIR / "alb2002_analysis_candidate_dataset.csv"
OUTPUT_PATH = DATA_DIR / "harmonized_household.csv"
HARMONIZATION_AUDIT_PATH = TEMP_DIR / "harmonization_audit.csv"
HARMONIZED_LINEAGE_PATH = TEMP_DIR / "harmonized_lineage.csv"
PROMOTION_AUDIT_PATH = TEMP_DIR / "alb2002_harmonized_household_core_promotion_audit.csv"
SUMMARY_PATH = RESULT_DIR / "alb2002_harmonized_household_core_promotion_summary.csv"
REPORT_PATH = REPORT_DIR / "alb2002_harmonized_household_core_promotion.md"

SCOPE = "alb2002_household_core_limited_no_final_outcome_no_climate"
DATA_USE_LIMIT = "harmonized_household_core_only_not_for_final_outcome_or_climate_analysis"
OUTCOME_STATUS = "candidate_inputs_not_final_outcomes"
CLIMATE_STATUS = "admin2_timing_present_boundary_coordinates_not_promoted"
SURVEY_DESIGN_STATUS = "household_weights_present_weighted_inference_not_promoted"
DECISION = "limited_harmonized_household_core_promoted_outcome_climate_still_blocked"

EXPECTED_HARMONIZED_COLUMNS = [
    "country",
    "survey_name",
    "wave",
    "survey_year",
    "survey_month",
    "interview_date",
    "hhid",
    "pid",
    "household_weight",
    "person_weight",
    "strata",
    "psu",
    "admin1",
    "admin2",
    "cluster_id",
    "latitude",
    "longitude",
    "geolocation_quality",
    "rural",
    "household_size",
    "children_under_5",
    "children_under_15",
    "elderly_60_plus",
    "elderly_65_plus",
    "hh_head_sex",
    "hh_head_age",
    "hh_head_education",
    "asset_index",
    "total_consumption",
    "total_income",
    "food_consumption",
    "nonfood_consumption",
    "oop_health_expenditure",
    "health_insurance",
    "illness_or_injury_need",
    "care_sought",
    "care_not_sought",
    "reason_not_sought_cost",
    "reason_not_sought_distance",
    "reason_not_sought_supply",
    "health_facility_distance",
    "coping_borrowed",
    "coping_sold_assets",
    "food_insecurity",
    "agriculture_livelihood",
    "employment_labor",
]

EXTRA_COLUMNS = [
    "idno",
    "admin2_code",
    "oop_share_total_budget_candidate",
    "che10_total_budget_candidate",
    "che25_total_budget_candidate",
    "positive_oop_candidate",
    "sudden_illness_4w_any",
    "delayed_or_unmet_care_candidate",
    "uhc_double_failure_che10_or_access_candidate",
    "uhc_double_failure_che25_or_access_candidate",
    "coping_health_cost_candidate",
    "oop_4w_monthly_equivalent",
    "oop_12m_monthly_equivalent",
    "candidate_policy_name",
    "harmonized_scope",
    "outcome_status",
    "climate_linkage_status",
    "survey_design_status",
    "data_use_limit",
    "source_candidate_artifact",
    "source_candidate_status",
    "source_promotion_status",
]

OUTPUT_COLUMNS = [
    "country",
    "survey_name",
    "wave",
    "idno",
    *[column for column in EXPECTED_HARMONIZED_COLUMNS if column not in {"country", "survey_name", "wave"}],
    *[column for column in EXTRA_COLUMNS if column != "idno"],
]

HARMONIZATION_AUDIT_COLUMNS = [
    "phase",
    "status",
    "detail",
    "country",
    "survey_name",
    "wave",
    "idno",
    "input_path",
    "rows_input",
    "rows_output",
    "output_path",
    "required_action",
]

LINEAGE_COLUMNS = [
    "country",
    "survey_name",
    "wave",
    "idno",
    "harmonized_variable",
    "source_path",
    "raw_variable",
    "raw_label",
    "transformation",
    "unit",
    "recall_period",
    "merge_level",
    "key_role",
    "required",
    "quality_flag",
    "rows_nonmissing",
    "notes",
]

PROMOTION_AUDIT_COLUMNS = [
    "gate_id",
    "gate_label",
    "status",
    "rows_checked",
    "rows_passing",
    "rows_blocked",
    "evidence",
    "output_artifact",
    "next_action",
]

SUMMARY_COLUMNS = ["metric", "value", "interpretation"]


def read_csv_dicts(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        return []
    with path.open(encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def row_count(path: Path) -> int:
    return len(read_csv_dicts(path))


def nonmissing(frame: pd.DataFrame, column: str) -> int:
    if column not in frame.columns:
        return 0
    series = frame[column]
    return int((series.notna() & (series.astype(str).str.strip() != "")).sum())


def pct(numerator: int, denominator: int) -> str:
    if denominator <= 0:
        return ""
    return f"{numerator / denominator:.6f}"


def summary_row(metric: str, value: Any, interpretation: str) -> dict[str, str]:
    return {"metric": metric, "value": str(value), "interpretation": interpretation}


def source_series(frame: pd.DataFrame, column: str, default: str = "") -> pd.Series:
    if column in frame.columns:
        return frame[column]
    return pd.Series(default, index=frame.index, dtype="object")


def require_source_columns(frame: pd.DataFrame) -> None:
    required = [
        "country",
        "survey_name",
        "wave",
        "idno",
        "hhid",
        "survey_year",
        "survey_month",
        "interview_date",
        "household_weight",
        "strata",
        "psu",
        "admin2",
        "admin2_code",
        "cluster_id",
        "candidate_dataset_status",
        "promotion_status",
    ]
    missing = [column for column in required if column not in frame.columns]
    if missing:
        raise ValueError(f"Missing required ALB_2002 candidate columns: {', '.join(missing)}")


def build_harmonized(candidate: pd.DataFrame) -> pd.DataFrame:
    out = pd.DataFrame(index=candidate.index)

    def assign(target: str, source: str | None = None, value: str = "") -> None:
        out[target] = source_series(candidate, source, value) if source else value

    direct = {
        "country": "country",
        "survey_name": "survey_name",
        "wave": "wave",
        "idno": "idno",
        "survey_year": "survey_year",
        "survey_month": "survey_month",
        "interview_date": "interview_date",
        "hhid": "hhid",
        "household_weight": "household_weight",
        "strata": "strata",
        "psu": "psu",
        "admin1": "admin1",
        "admin2": "admin2",
        "cluster_id": "cluster_id",
        "latitude": "latitude",
        "longitude": "longitude",
        "geolocation_quality": "geolocation_quality",
        "rural": "rural",
        "household_size": "household_size",
        "children_under_5": "children_under5",
        "children_under_15": "children_under15",
        "elderly_60_plus": "elderly_60plus",
        "elderly_65_plus": "elderly_65plus",
        "hh_head_sex": "head_sex",
        "hh_head_age": "head_age",
        "agriculture_livelihood": "agriculture_livelihood",
        "health_insurance": "health_insurance_candidate",
        "total_consumption": "total_consumption_monthly_candidate",
        "oop_health_expenditure": "oop_health_expenditure_monthly_candidate",
        "illness_or_injury_need": "illness_or_injury_need_candidate",
        "care_not_sought": "delayed_or_unmet_care_candidate",
        "reason_not_sought_cost": "forgone_care_cost_barrier_candidate",
        "reason_not_sought_distance": "forgone_care_distance_barrier_candidate",
        "reason_not_sought_supply": "forgone_care_supply_barrier_candidate",
        "admin2_code": "admin2_code",
        "oop_share_total_budget_candidate": "oop_share_total_budget_candidate",
        "che10_total_budget_candidate": "che10_total_budget_candidate",
        "che25_total_budget_candidate": "che25_total_budget_candidate",
        "positive_oop_candidate": "positive_oop_candidate",
        "sudden_illness_4w_any": "sudden_illness_4w_any",
        "delayed_or_unmet_care_candidate": "delayed_or_unmet_care_candidate",
        "uhc_double_failure_che10_or_access_candidate": "uhc_double_failure_che10_or_access_candidate",
        "uhc_double_failure_che25_or_access_candidate": "uhc_double_failure_che25_or_access_candidate",
        "coping_health_cost_candidate": "coping_health_cost_candidate",
        "oop_4w_monthly_equivalent": "oop_4w_monthly_equivalent",
        "oop_12m_monthly_equivalent": "oop_12m_monthly_equivalent",
        "candidate_policy_name": "candidate_policy_name",
        "source_candidate_status": "candidate_dataset_status",
        "source_promotion_status": "promotion_status",
    }
    for target, source in direct.items():
        assign(target, source)

    for target in [
        "pid",
        "person_weight",
        "hh_head_education",
        "asset_index",
        "total_income",
        "food_consumption",
        "nonfood_consumption",
        "care_sought",
        "health_facility_distance",
        "coping_borrowed",
        "coping_sold_assets",
        "food_insecurity",
        "employment_labor",
    ]:
        assign(target)

    assign("harmonized_scope", value=SCOPE)
    assign("outcome_status", value=OUTCOME_STATUS)
    assign("climate_linkage_status", value=CLIMATE_STATUS)
    assign("survey_design_status", value=SURVEY_DESIGN_STATUS)
    assign("data_use_limit", value=DATA_USE_LIMIT)
    assign("source_candidate_artifact", value="temp/alb2002_analysis_candidate_dataset.csv")

    for column in OUTPUT_COLUMNS:
        if column not in out.columns:
            out[column] = ""
    return out[OUTPUT_COLUMNS]


def harmonization_audit_rows(candidate: pd.DataFrame, output: pd.DataFrame) -> list[dict[str, Any]]:
    raw_file_rows = row_count(TEMP_DIR / "raw_schema_inventory" / "raw_file_inventory.csv")
    return [
        {
            "phase": "recipe_template",
            "status": "complete",
            "detail": "Standard harmonized schema template exists; this ALB_2002 promotion uses a scoped candidate-derived mapping, not a general multi-country recipe.",
            "country": COUNTRY,
            "survey_name": SURVEY_NAME,
            "wave": WAVE,
            "idno": IDNO,
            "input_path": "temp/harmonization_recipe_template.csv",
            "rows_input": len(EXPECTED_HARMONIZED_COLUMNS),
            "rows_output": "",
            "output_path": "",
            "required_action": "Keep building the verified multi-country recipe separately from this scoped ALB_2002 core.",
        },
        {
            "phase": "raw_files",
            "status": "complete",
            "detail": "Local raw/schema evidence exists for ALB_2002 and was assembled into the temp analysis candidate; other country-waves still require manual raw access.",
            "country": COUNTRY,
            "survey_name": SURVEY_NAME,
            "wave": WAVE,
            "idno": IDNO,
            "input_path": "temp/raw_schema_inventory/raw_file_inventory.csv",
            "rows_input": raw_file_rows,
            "rows_output": "",
            "output_path": "",
            "required_action": "Do not generalize this scoped output to other waves without raw value/key audits.",
        },
        {
            "phase": "source_candidate",
            "status": "complete",
            "detail": "ALB_2002 joined household core candidate is present with identity, timing, design, admin2, demographic, and candidate input fields.",
            "country": COUNTRY,
            "survey_name": SURVEY_NAME,
            "wave": WAVE,
            "idno": IDNO,
            "input_path": "temp/alb2002_analysis_candidate_dataset.csv",
            "rows_input": len(candidate),
            "rows_output": "",
            "output_path": "",
            "required_action": "Outcome and climate gates remain separate and must not be inferred from this core file.",
        },
        {
            "phase": "harmonized_output",
            "status": "complete",
            "detail": "Scoped ALB_2002 harmonized household core promoted for inspection only; final outcomes, SDG 3.8.2, climate linkage, and weighted inference remain unpromoted.",
            "country": COUNTRY,
            "survey_name": SURVEY_NAME,
            "wave": WAVE,
            "idno": IDNO,
            "input_path": "temp/alb2002_analysis_candidate_dataset.csv",
            "rows_input": len(candidate),
            "rows_output": len(output),
            "output_path": "data/harmonized_household.csv",
            "required_action": "Resolve OOP/access outcome policy, SDG denominator, weight-use, historical geography, coordinates, and primary climate-source gates before analysis-ready promotion.",
        },
        {
            "phase": "outcome_climate_guardrail",
            "status": "blocked",
            "detail": "The harmonized core carries candidate inputs with explicit data-use limits; it is not a final outcome or climate-linked analytical dataset.",
            "country": COUNTRY,
            "survey_name": SURVEY_NAME,
            "wave": WAVE,
            "idno": IDNO,
            "input_path": "data/harmonized_household.csv",
            "rows_input": len(output),
            "rows_output": 0,
            "output_path": "data/household_outcomes.csv; data/climate_linked_household.csv",
            "required_action": "Keep outcome and climate construction blocked until their dedicated gates pass.",
        },
    ]


def lineage_rows(output: pd.DataFrame) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []

    def add(
        variable: str,
        source_variable: str,
        transformation: str,
        quality_flag: str,
        notes: str,
        *,
        unit: str = "",
        recall_period: str = "",
        merge_level: str = "household",
        key_role: str = "",
        required: str = "no",
        source_path: str = "temp/alb2002_analysis_candidate_dataset.csv",
    ) -> None:
        rows.append(
            {
                "country": COUNTRY,
                "survey_name": SURVEY_NAME,
                "wave": WAVE,
                "idno": IDNO,
                "harmonized_variable": variable,
                "source_path": source_path,
                "raw_variable": source_variable,
                "raw_label": "",
                "transformation": transformation,
                "unit": unit,
                "recall_period": recall_period,
                "merge_level": merge_level,
                "key_role": key_role,
                "required": required,
                "quality_flag": quality_flag,
                "rows_nonmissing": nonmissing(output, variable),
                "notes": notes,
            }
        )

    direct_core = {
        "country": ("country", "constant/carry-forward study identifier", "promoted_limited_core", "Study-level country label.", "yes"),
        "survey_name": ("survey_name", "constant/carry-forward study identifier", "promoted_limited_core", "Study-level survey label.", "yes"),
        "wave": ("wave", "constant/carry-forward study identifier", "promoted_limited_core", "Study-level wave label.", "yes"),
        "idno": ("idno", "constant/carry-forward study identifier", "promoted_limited_core", "World Bank study identifier.", "yes"),
        "survey_year": ("survey_year", "direct carry-forward", "promoted_limited_core", "Interview year is observed for all candidate households.", "yes"),
        "survey_month": ("survey_month", "direct carry-forward", "promoted_limited_core", "Interview month is observed for all candidate households.", "yes"),
        "interview_date": ("interview_date", "direct carry-forward", "promoted_limited_core", "Candidate interview date is observed for all households.", "yes"),
        "hhid": ("hhid", "direct carry-forward", "promoted_limited_core", "Household key remains unique in the candidate source.", "yes"),
        "household_weight": ("household_weight", "direct carry-forward", "promoted_limited_core_weight_not_inference_ready", "Positive household weights are present, but weighted inference remains unpromoted pending weight-use decision.", "recommended"),
        "strata": ("strata", "direct carry-forward", "promoted_limited_core_weight_not_inference_ready", "Design stratum carried from candidate source.", "recommended"),
        "psu": ("psu", "direct carry-forward", "promoted_limited_core_weight_not_inference_ready", "PSU carried from candidate source.", "recommended"),
        "admin2": ("admin2", "direct carry-forward", "admin2_boundary_not_promoted", "District names are present but historical boundary/crosswalk evidence remains unresolved.", "recommended"),
        "admin2_code": ("admin2_code", "direct carry-forward", "admin2_boundary_not_promoted", "District codes are present but not promoted for climate linkage.", "recommended"),
        "cluster_id": ("cluster_id", "direct carry-forward", "promoted_limited_core", "Cluster ID mirrors the candidate PSU key.", "recommended"),
        "geolocation_quality": ("geolocation_quality", "direct carry-forward", "admin2_boundary_not_promoted", "Geography is admin2 candidate only, with no GPS coordinates.", "recommended"),
        "rural": ("rural", "direct carry-forward", "promoted_limited_core", "Urban/rural candidate field carried from source.", "recommended"),
        "household_size": ("household_size", "direct carry-forward", "promoted_limited_core", "Household-size covariate.", "recommended"),
        "children_under_5": ("children_under5", "renamed from candidate field", "promoted_limited_core", "Demographic covariate.", "no"),
        "children_under_15": ("children_under15", "renamed from candidate field", "promoted_limited_core", "Demographic covariate.", "no"),
        "elderly_60_plus": ("elderly_60plus", "renamed from candidate field", "promoted_limited_core", "Demographic covariate.", "no"),
        "elderly_65_plus": ("elderly_65plus", "renamed from candidate field", "promoted_limited_core", "Demographic covariate.", "no"),
        "hh_head_sex": ("head_sex", "renamed from candidate field", "promoted_limited_core", "Household-head covariate.", "no"),
        "hh_head_age": ("head_age", "renamed from candidate field", "promoted_limited_core", "Household-head covariate.", "no"),
        "agriculture_livelihood": ("agriculture_livelihood", "direct carry-forward", "promoted_limited_core", "Livelihood covariate.", "no"),
    }
    for variable, (source, transform, quality, notes, required) in direct_core.items():
        key_role = "base_key" if variable == "hhid" else ""
        add(variable, source, transform, quality, notes, required=required, key_role=key_role)

    candidate_inputs = {
        "total_consumption": ("total_consumption_monthly_candidate", "monthly local-currency candidate input", "candidate_input_not_final_outcome", "Candidate total-budget input is carried for audit; not a final SDG or CHE denominator.", "local_currency_monthly", "monthly-equivalent"),
        "oop_health_expenditure": ("oop_health_expenditure_monthly_candidate", "monthly local-currency candidate input", "candidate_input_not_final_outcome", "Candidate OOP input is carried for audit; not a final numerator.", "local_currency_monthly", "monthly-equivalent"),
        "health_insurance": ("health_insurance_candidate", "direct carry-forward candidate input", "candidate_input_not_final_outcome", "Insurance candidate input, not a final outcome.", "", ""),
        "illness_or_injury_need": ("illness_or_injury_need_candidate", "candidate any-positive need rule", "candidate_input_not_final_outcome", "Need candidate requires denominator/skip review before outcome use.", "", ""),
        "care_not_sought": ("delayed_or_unmet_care_candidate", "candidate unmet-care composite", "candidate_input_not_final_outcome", "Access candidate is present but not a final forgone-care outcome.", "", ""),
        "reason_not_sought_cost": ("forgone_care_cost_barrier_candidate", "candidate any-positive barrier rule", "candidate_input_not_final_outcome", "Cost-barrier candidate requires access denominator and skip-pattern review.", "", ""),
        "reason_not_sought_distance": ("forgone_care_distance_barrier_candidate", "candidate any-positive barrier rule", "candidate_input_not_final_outcome", "Distance-barrier candidate requires access denominator and skip-pattern review.", "", ""),
        "reason_not_sought_supply": ("forgone_care_supply_barrier_candidate", "candidate any-positive barrier rule", "candidate_input_not_final_outcome", "Supply-barrier candidate requires access denominator and skip-pattern review.", "", ""),
    }
    for variable, (source, transform, quality, notes, unit, recall) in candidate_inputs.items():
        add(variable, source, transform, quality, notes, unit=unit, recall_period=recall)

    blank_fields = [
        "pid",
        "person_weight",
        "admin1",
        "latitude",
        "longitude",
        "hh_head_education",
        "asset_index",
        "total_income",
        "food_consumption",
        "nonfood_consumption",
        "care_sought",
        "health_facility_distance",
        "coping_borrowed",
        "coping_sold_assets",
        "food_insecurity",
        "employment_labor",
    ]
    for variable in blank_fields:
        quality = "missing_coordinates_block_climate" if variable in {"latitude", "longitude"} else "missing_or_not_constructed"
        notes = "No household coordinates are available; climate linkage remains blocked." if variable in {"latitude", "longitude"} else "Not constructed in the scoped ALB_2002 harmonized core."
        add(variable, "", "left blank by limited promotion", quality, notes)

    extras = {
        "oop_share_total_budget_candidate": "Candidate CHE input retained with suffix to prevent final-outcome use.",
        "che10_total_budget_candidate": "Candidate CHE10 indicator retained with suffix to prevent final-outcome use.",
        "che25_total_budget_candidate": "Candidate CHE25 indicator retained with suffix to prevent final-outcome use.",
        "positive_oop_candidate": "Candidate positive OOP flag retained with suffix.",
        "sudden_illness_4w_any": "Candidate four-week illness signal retained for denominator review.",
        "delayed_or_unmet_care_candidate": "Candidate access composite retained with suffix.",
        "uhc_double_failure_che10_or_access_candidate": "Candidate composite retained with suffix.",
        "uhc_double_failure_che25_or_access_candidate": "Candidate composite retained with suffix.",
        "coping_health_cost_candidate": "Candidate coping signal retained with suffix; not mapped to borrowed/sold-assets final variables.",
        "oop_4w_monthly_equivalent": "Candidate monthly-equivalent OOP component retained for audit.",
        "oop_12m_monthly_equivalent": "Candidate monthly-equivalent OOP component retained for audit.",
        "candidate_policy_name": "Candidate OOP policy name retained for audit.",
        "harmonized_scope": "Constant data-scope marker.",
        "outcome_status": "Constant outcome guardrail marker.",
        "climate_linkage_status": "Constant climate guardrail marker.",
        "survey_design_status": "Constant survey-design guardrail marker.",
        "data_use_limit": "Constant data-use guardrail marker.",
        "source_candidate_artifact": "Constant source-artifact pointer.",
        "source_candidate_status": "Candidate status copied from source artifact.",
        "source_promotion_status": "Source promotion status copied from source artifact.",
    }
    for variable, notes in extras.items():
        source = variable if variable not in {"harmonized_scope", "outcome_status", "climate_linkage_status", "survey_design_status", "data_use_limit", "source_candidate_artifact"} else ""
        add(variable, source, "direct carry-forward or constant guardrail marker", "limited_core_guardrail", notes)

    return rows


def promotion_audit_rows(candidate: pd.DataFrame, output: pd.DataFrame) -> list[dict[str, Any]]:
    total = len(output)
    coordinates_present = min(nonmissing(output, "latitude"), nonmissing(output, "longitude"))
    return [
        {
            "gate_id": "source_candidate",
            "gate_label": "ALB_2002 joined candidate exists",
            "status": "complete",
            "rows_checked": len(candidate),
            "rows_passing": len(candidate),
            "rows_blocked": 0,
            "evidence": "temp/alb2002_analysis_candidate_dataset.csv present with household keys, timing, design, admin2, demographics, and candidate inputs.",
            "output_artifact": "data/harmonized_household.csv",
            "next_action": "Use only with the explicit data-use limit until final gates pass.",
        },
        {
            "gate_id": "identity_timing_design",
            "gate_label": "Household identity, timing, and design fields",
            "status": "complete_limited_core",
            "rows_checked": total,
            "rows_passing": min(nonmissing(output, "hhid"), nonmissing(output, "survey_month"), nonmissing(output, "interview_date"), nonmissing(output, "household_weight")),
            "rows_blocked": 0,
            "evidence": "Household ID, interview timing, and positive household-weight evidence are carried from the audited candidate.",
            "output_artifact": "data/harmonized_household.csv",
            "next_action": "Resolve weight-use semantics before weighted inference.",
        },
        {
            "gate_id": "demographic_covariates",
            "gate_label": "Basic household covariates",
            "status": "complete_limited_core",
            "rows_checked": total,
            "rows_passing": min(nonmissing(output, "household_size"), nonmissing(output, "hh_head_age")),
            "rows_blocked": 0,
            "evidence": "Household-size, age, sex, child, elderly, rural, and agriculture-livelihood fields are carried for covariate inspection.",
            "output_artifact": "data/harmonized_household.csv",
            "next_action": "Extend only after raw variable value/label checks are accepted.",
        },
        {
            "gate_id": "candidate_financial_inputs",
            "gate_label": "Candidate consumption and OOP inputs",
            "status": "candidate_input_not_final_outcome",
            "rows_checked": total,
            "rows_passing": min(nonmissing(output, "total_consumption"), nonmissing(output, "oop_health_expenditure")),
            "rows_blocked": total,
            "evidence": "Candidate monthly-equivalent OOP and total-budget inputs are retained for audit but marked as non-final outcome inputs.",
            "output_artifact": "data/harmonized_household.csv",
            "next_action": "Accept numerator inclusion, recall policy, denominator benchmark, and SDG 3.8.2 rules before outcome construction.",
        },
        {
            "gate_id": "candidate_access_inputs",
            "gate_label": "Candidate need/access inputs",
            "status": "candidate_input_not_final_outcome",
            "rows_checked": total,
            "rows_passing": nonmissing(output, "illness_or_injury_need"),
            "rows_blocked": total,
            "evidence": "Candidate need, unmet-care, and barrier signals are retained with outcome guardrail markers.",
            "output_artifact": "data/harmonized_household.csv",
            "next_action": "Accept access denominator, skip semantics, and low-event handling before final outcome construction.",
        },
        {
            "gate_id": "geography_for_climate",
            "gate_label": "Historical geography and coordinates for climate linkage",
            "status": "blocked_for_climate_linkage",
            "rows_checked": total,
            "rows_passing": coordinates_present,
            "rows_blocked": total - coordinates_present,
            "evidence": "Admin2 candidate names/codes are present, but coordinates and verified historical boundary/crosswalk remain unpromoted.",
            "output_artifact": "",
            "next_action": "Obtain/verify official GPS, PSU crosswalk, or historical district boundaries before climate linkage.",
        },
        {
            "gate_id": "final_outcomes",
            "gate_label": "Final household outcomes",
            "status": "blocked_final_outcome_promotion",
            "rows_checked": total,
            "rows_passing": 0,
            "rows_blocked": total,
            "evidence": "Outcome fields are candidate inputs only; data/household_outcomes.csv is intentionally not written.",
            "output_artifact": "",
            "next_action": "Resolve OOP/access/SDG rules and rerun outcome construction only after candidate status is removed.",
        },
        {
            "gate_id": "climate_linked_dataset",
            "gate_label": "Climate-linked household data",
            "status": "blocked_climate_linkage_promotion",
            "rows_checked": total,
            "rows_passing": 0,
            "rows_blocked": total,
            "evidence": "No promoted climate exposure or climate-linked household dataset is written.",
            "output_artifact": "",
            "next_action": "Promote climate exposure only after geography, timing, source, and baseline gates pass.",
        },
    ]


def summary_rows(output: pd.DataFrame, audit_rows: list[dict[str, Any]]) -> list[dict[str, str]]:
    total = len(output)
    coordinate_rows = min(nonmissing(output, "latitude"), nonmissing(output, "longitude"))
    return [
        summary_row("alb2002_harmonized_household_core_promotion_audit_rows", len(audit_rows), "Rows in the scoped harmonized-core promotion audit."),
        summary_row("alb2002_harmonized_household_core_source_candidate_rows", row_count(SOURCE_PATH), "Rows in temp/alb2002_analysis_candidate_dataset.csv."),
        summary_row("alb2002_harmonized_household_core_rows", total, "Rows written to data/harmonized_household.csv under limited scope."),
        summary_row("alb2002_harmonized_household_core_columns", len(output.columns), "Columns in the limited harmonized household core."),
        summary_row("alb2002_harmonized_household_core_identity_rows", nonmissing(output, "hhid"), "Rows with nonmissing household ID."),
        summary_row("alb2002_harmonized_household_core_timing_rows", min(nonmissing(output, "survey_month"), nonmissing(output, "interview_date")), "Rows with interview month and date."),
        summary_row("alb2002_harmonized_household_core_weight_rows", nonmissing(output, "household_weight"), "Rows with nonmissing household weight."),
        summary_row("alb2002_harmonized_household_core_admin2_rows", nonmissing(output, "admin2"), "Rows with candidate admin2 name."),
        summary_row("alb2002_harmonized_household_core_coordinate_rows", coordinate_rows, "Rows with both latitude and longitude; should remain zero."),
        summary_row("alb2002_harmonized_household_core_candidate_consumption_rows", nonmissing(output, "total_consumption"), "Rows carrying candidate total-budget input."),
        summary_row("alb2002_harmonized_household_core_candidate_oop_rows", nonmissing(output, "oop_health_expenditure"), "Rows carrying candidate OOP input."),
        summary_row("alb2002_harmonized_household_core_candidate_need_rows", nonmissing(output, "illness_or_injury_need"), "Rows carrying candidate health-need input."),
        summary_row("alb2002_harmonized_household_core_limited_data_write_ready_rows", total, "Rows allowed in data/ only as a limited harmonized household core."),
        summary_row("alb2002_harmonized_household_core_final_outcome_ready_rows", 0, "Rows ready for final outcome construction; intentionally zero."),
        summary_row("alb2002_harmonized_household_core_climate_linkage_ready_rows", 0, "Rows ready for climate linkage; intentionally zero."),
        summary_row("alb2002_harmonized_household_core_analysis_ready_rows", 0, "Rows ready for final empirical analysis; intentionally zero."),
        summary_row("alb2002_harmonized_household_core_current_decision", DECISION, "Current scoped promotion decision."),
        summary_row("alb2002_harmonized_household_core_data_use_limit", DATA_USE_LIMIT, "Guardrail embedded in every output row."),
    ]


def markdown_table(rows: list[dict[str, Any]], columns: list[str]) -> str:
    lines = ["| " + " | ".join(columns) + " |", "|" + "|".join("---" for _ in columns) + "|"]
    for row in rows:
        values = []
        for column in columns:
            value = str(row.get(column, "")).replace("|", "/")
            if len(value) > 120:
                value = value[:117] + "..."
            values.append(value)
        lines.append("| " + " | ".join(values) + " |")
    return "\n".join(lines)


def write_report(summary: list[dict[str, str]], audit_rows: list[dict[str, Any]]) -> None:
    summary_table = markdown_table(summary, ["metric", "value", "interpretation"])
    audit_table = markdown_table(audit_rows, ["gate_id", "status", "rows_passing", "rows_blocked", "next_action"])
    REPORT_PATH.write_text(
        f"""# ALB_2002 Harmonized Household Core Promotion

Status: scoped limited promotion. This writes `data/harmonized_household.csv` for ALB_2002 household-core inspection only. It does not promote final outcomes, SDG 3.8.2, climate exposure, climate-linked data, weighted inference, descriptive diagnostics, predictive ML, reduced-form estimation, causal ML, or policy learning.

## Summary

{summary_table}

## Gate Audit

{audit_table}

## Guardrails

- Every row carries `harmonized_scope={SCOPE}`.
- Every row carries `outcome_status={OUTCOME_STATUS}` and `data_use_limit={DATA_USE_LIMIT}`.
- Candidate OOP, consumption, access, and composite fields are retained for audit but are not final outcomes.
- Climate linkage remains blocked because the output has no coordinates and no promoted historical admin boundary/crosswalk.
- `data/household_outcomes.csv`, `data/climate_exposures_nasa_power.csv`, and `data/climate_linked_household.csv` are not written by this promotion.

## Machine-Readable Outputs

- `data/harmonized_household.csv`
- `temp/harmonization_audit.csv`
- `temp/harmonized_lineage.csv`
- `temp/alb2002_harmonized_household_core_promotion_audit.csv`
- `result/alb2002_harmonized_household_core_promotion_summary.csv`
""",
        encoding="utf-8",
    )


def main() -> None:
    ensure_dirs()
    if not SOURCE_PATH.exists():
        raise FileNotFoundError(f"Missing source candidate: {SOURCE_PATH}")

    candidate = pd.read_csv(SOURCE_PATH, dtype=str, keep_default_na=False)
    require_source_columns(candidate)
    output = build_harmonized(candidate)

    DATA_DIR.mkdir(parents=True, exist_ok=True)
    output.to_csv(OUTPUT_PATH, index=False, encoding="utf-8-sig")

    harmonization_rows = harmonization_audit_rows(candidate, output)
    lineage = lineage_rows(output)
    promotion_rows = promotion_audit_rows(candidate, output)
    summary = summary_rows(output, promotion_rows)

    write_csv(HARMONIZATION_AUDIT_PATH, harmonization_rows, HARMONIZATION_AUDIT_COLUMNS)
    write_csv(HARMONIZED_LINEAGE_PATH, lineage, LINEAGE_COLUMNS)
    write_csv(PROMOTION_AUDIT_PATH, promotion_rows, PROMOTION_AUDIT_COLUMNS)
    write_csv(SUMMARY_PATH, summary, SUMMARY_COLUMNS)
    write_report(summary, promotion_rows)

    append_log(TEMP_DIR / "audit_log.md", f"Promoted ALB_2002 limited harmonized household core rows={len(output)} decision={DECISION}.")
    print(f"Promoted ALB_2002 limited harmonized household core rows={len(output)} decision={DECISION}.")


if __name__ == "__main__":
    main()
