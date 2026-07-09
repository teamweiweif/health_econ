from __future__ import annotations

import csv
from pathlib import Path
from typing import Any

from common import DATA_DIR, REPORT_DIR, RESULT_DIR, TEMP_DIR, append_log, ensure_dirs, write_csv


AUDIT_PATH = TEMP_DIR / "analysis_dataset_promotion_barrier_audit.csv"
SUMMARY_PATH = RESULT_DIR / "analysis_dataset_promotion_barrier_summary.csv"
REPORT_PATH = REPORT_DIR / "analysis_dataset_promotion_barriers.md"

DECISION = "limited_core_financial_outcomes_climate_exposures_and_linked_diagnostics_promoted_models_still_blocked"

AUDIT_COLUMNS = [
    "promotion_target",
    "completion_criteria",
    "required_artifact",
    "artifact_status",
    "candidate_evidence",
    "ready_rows",
    "blocking_status",
    "promotion_decision",
    "next_action",
]

SUMMARY_COLUMNS = ["metric", "value", "interpretation"]


def read_csv_dicts(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        return []
    with path.open(encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def metric_value(rows: list[dict[str, str]], metric: str, default: str = "0") -> str:
    for row in rows:
        if row.get("metric") == metric:
            return row.get("value", default)
    return default


def safe_int(value: Any, default: int = 0) -> int:
    try:
        return int(float(str(value)))
    except (TypeError, ValueError):
        return default


def csv_row_count(path: Path) -> int:
    if not path.exists() or path.stat().st_size == 0:
        return 0
    with path.open(encoding="utf-8-sig", newline="") as f:
        return sum(1 for _ in csv.DictReader(f))


def artifact_status(*paths: Path) -> str:
    for path in paths:
        if path.exists() and path.stat().st_size > 0:
            return f"present:{path.relative_to(DATA_DIR.parent).as_posix()}"
    return "missing"


def data_file_count() -> int:
    if not DATA_DIR.exists():
        return 0
    return sum(1 for path in DATA_DIR.rglob("*") if path.is_file())


def add_row(
    rows: list[dict[str, str]],
    promotion_target: str,
    completion_criteria: str,
    required_artifact: str,
    artifact_status_value: str,
    candidate_evidence: str,
    ready_rows: int,
    blocking_status: str,
    next_action: str,
    promotion_decision: str | None = None,
) -> None:
    rows.append(
        {
            "promotion_target": promotion_target,
            "completion_criteria": completion_criteria,
            "required_artifact": required_artifact,
            "artifact_status": artifact_status_value,
            "candidate_evidence": candidate_evidence,
            "ready_rows": str(ready_rows),
            "blocking_status": blocking_status,
            "promotion_decision": promotion_decision or ("blocked_keep_out_of_data" if ready_rows == 0 else "review_required_before_data_write"),
            "next_action": next_action,
        }
    )


def build_rows() -> list[dict[str, str]]:
    harmonization_summary = read_csv_dicts(RESULT_DIR / "harmonization_recipe_gate_summary.csv")
    readiness_rows = read_csv_dicts(RESULT_DIR / "harmonization_readiness_matrix.csv")
    alb2002_core_summary = read_csv_dicts(RESULT_DIR / "alb2002_household_core_candidate_summary.csv")
    alb2002_minimum_summary = read_csv_dicts(RESULT_DIR / "alb2002_minimum_recipe_promotion_summary.csv")
    alb2002_period_aligned_che_summary = read_csv_dicts(RESULT_DIR / "alb2002_period_aligned_che_policy_summary.csv")
    alb2002_che_candidate_summary = read_csv_dicts(RESULT_DIR / "alb2002_che_candidate_outcome_summary.csv")
    alb2002_access_candidate_summary = read_csv_dicts(RESULT_DIR / "alb2002_access_candidate_outcome_summary.csv")
    alb2002_uhc_composite_summary = read_csv_dicts(RESULT_DIR / "alb2002_uhc_composite_candidate_summary.csv")
    alb2002_analysis_candidate_summary = read_csv_dicts(RESULT_DIR / "alb2002_analysis_candidate_readiness_summary.csv")
    alb2002_harmonized_core_summary = read_csv_dicts(RESULT_DIR / "alb2002_harmonized_household_core_promotion_summary.csv")
    alb2002_limited_financial_summary = read_csv_dicts(RESULT_DIR / "alb2002_limited_financial_outcome_promotion_summary.csv")
    alb2002_limited_climate_summary = read_csv_dicts(RESULT_DIR / "alb2002_limited_climate_exposure_promotion_summary.csv")
    alb2002_limited_linked_summary = read_csv_dicts(RESULT_DIR / "alb2002_limited_climate_linked_promotion_summary.csv")
    alb2002_climate_centroid_summary = read_csv_dicts(RESULT_DIR / "alb2002_climate_centroid_exposure_summary.csv")
    alb2002_climate_shock_summary = read_csv_dicts(RESULT_DIR / "alb2002_climate_shock_candidate_summary.csv")
    alb2002_climate_outcome_linked_summary = read_csv_dicts(RESULT_DIR / "alb2002_climate_outcome_linked_candidate_summary.csv")
    alb2002_linked_candidate_descriptive_summary = read_csv_dicts(RESULT_DIR / "alb2002_linked_candidate_descriptive_summary.csv")
    alb2002_weight_design_summary = read_csv_dicts(RESULT_DIR / "alb2002_weight_design_evidence_summary.csv")
    alb2002_sample_design_summary = read_csv_dicts(RESULT_DIR / "alb2002_sample_design_documentation_summary.csv")
    albania_first_summary = read_csv_dicts(RESULT_DIR / "albania_first_analysis_promotion_summary.csv")
    climate_linkage_rows = read_csv_dicts(RESULT_DIR / "climate_linkage_readiness.csv")

    verified_recipe_candidates = safe_int(metric_value(harmonization_summary, "verified_candidate_rows"))
    ready_country_waves = safe_int(metric_value(harmonization_summary, "ready_country_wave_rows"))
    blocked_country_waves = safe_int(metric_value(harmonization_summary, "blocked_country_wave_rows"))
    value_audit_rows = safe_int(metric_value(harmonization_summary, "value_audit_rows"))
    ready_linkage_rows = sum(1 for row in climate_linkage_rows if row.get("readiness_status") == "ready_for_climate_linkage_value_audit")

    alb2002_temp_rows = safe_int(metric_value(alb2002_core_summary, "alb2002_household_core_candidate_rows"))
    alb2002_recipe_ready = safe_int(metric_value(alb2002_core_summary, "alb2002_household_core_recipe_ready_rows"))
    alb2002_harmonized_ready = safe_int(metric_value(alb2002_minimum_summary, "alb2002_minimum_recipe_promotion_harmonized_ready_rows"))
    alb2002_outcome_ready = safe_int(metric_value(alb2002_minimum_summary, "alb2002_minimum_recipe_promotion_outcome_ready_rows"))
    alb2002_sdg_ready = safe_int(metric_value(alb2002_minimum_summary, "alb2002_minimum_recipe_promotion_sdg382_ready_rows"))
    alb2002_climate_ready = safe_int(metric_value(alb2002_minimum_summary, "alb2002_minimum_recipe_promotion_climate_linkage_ready_rows"))
    alb2002_period_aligned_policy_rows = safe_int(metric_value(alb2002_period_aligned_che_summary, "alb2002_period_aligned_che_policy_rows"))
    alb2002_period_aligned_period_ready = safe_int(metric_value(alb2002_period_aligned_che_summary, "alb2002_period_aligned_che_period_alignment_ready_rows"))
    alb2002_period_aligned_outcome_ready = safe_int(metric_value(alb2002_period_aligned_che_summary, "alb2002_period_aligned_che_outcome_ready_rows"))
    alb2002_period_aligned_recipe_ready = safe_int(metric_value(alb2002_period_aligned_che_summary, "alb2002_period_aligned_che_recipe_ready_rows"))
    alb2002_period_aligned_climate_ready = safe_int(metric_value(alb2002_period_aligned_che_summary, "alb2002_period_aligned_che_climate_linkage_ready_rows"))
    alb2002_period_aligned_combined_che10 = metric_value(alb2002_period_aligned_che_summary, "alb2002_period_aligned_che_combined_che10_rate", "")
    alb2002_period_aligned_combined_che25 = metric_value(alb2002_period_aligned_che_summary, "alb2002_period_aligned_che_combined_che25_rate", "")
    alb2002_che_candidate_rows = safe_int(metric_value(alb2002_che_candidate_summary, "alb2002_che_candidate_household_rows"))
    alb2002_che_candidate_che10_rows = safe_int(metric_value(alb2002_che_candidate_summary, "alb2002_che_candidate_che10_rows"))
    alb2002_che_candidate_che25_rows = safe_int(metric_value(alb2002_che_candidate_summary, "alb2002_che_candidate_che25_rows"))
    alb2002_che_candidate_che10_weighted = metric_value(alb2002_che_candidate_summary, "alb2002_che_candidate_che10_weighted_rate", "")
    alb2002_che_candidate_che25_weighted = metric_value(alb2002_che_candidate_summary, "alb2002_che_candidate_che25_weighted_rate", "")
    alb2002_che_candidate_promotion_ready = safe_int(metric_value(alb2002_che_candidate_summary, "alb2002_che_candidate_outcome_promotion_ready_rows"))
    alb2002_che_candidate_climate_ready = safe_int(metric_value(alb2002_che_candidate_summary, "alb2002_che_candidate_climate_linkage_ready_rows"))
    alb2002_access_candidate_rows = safe_int(metric_value(alb2002_access_candidate_summary, "alb2002_access_candidate_household_rows"))
    alb2002_access_candidate_any_rows = safe_int(metric_value(alb2002_access_candidate_summary, "alb2002_access_candidate_composite_any_rows"))
    alb2002_access_candidate_cost_rows = safe_int(metric_value(alb2002_access_candidate_summary, "alb2002_access_candidate_composite_cost_rows"))
    alb2002_access_candidate_any_weighted = metric_value(alb2002_access_candidate_summary, "alb2002_access_candidate_composite_any_weighted_rate", "")
    alb2002_access_candidate_promotion_ready = safe_int(metric_value(alb2002_access_candidate_summary, "alb2002_access_candidate_outcome_promotion_ready_rows"))
    alb2002_access_candidate_climate_ready = safe_int(metric_value(alb2002_access_candidate_summary, "alb2002_access_candidate_climate_linkage_ready_rows"))
    alb2002_uhc_composite_rows = safe_int(metric_value(alb2002_uhc_composite_summary, "alb2002_uhc_composite_candidate_household_rows"))
    alb2002_uhc_composite_che10_or_access = safe_int(metric_value(alb2002_uhc_composite_summary, "alb2002_uhc_composite_candidate_che10_or_access_rows"))
    alb2002_uhc_composite_che25_or_access = safe_int(metric_value(alb2002_uhc_composite_summary, "alb2002_uhc_composite_candidate_che25_or_access_rows"))
    alb2002_uhc_composite_coping = safe_int(metric_value(alb2002_uhc_composite_summary, "alb2002_uhc_composite_candidate_coping_rows"))
    alb2002_uhc_composite_promotion_ready = safe_int(metric_value(alb2002_uhc_composite_summary, "alb2002_uhc_composite_candidate_outcome_promotion_ready_rows"))
    alb2002_uhc_composite_climate_ready = safe_int(metric_value(alb2002_uhc_composite_summary, "alb2002_uhc_composite_candidate_climate_linkage_ready_rows"))
    alb2002_analysis_candidate_rows = safe_int(metric_value(alb2002_analysis_candidate_summary, "alb2002_analysis_candidate_rows"))
    alb2002_analysis_complete_gates = safe_int(metric_value(alb2002_analysis_candidate_summary, "alb2002_analysis_candidate_complete_candidate_gates"))
    alb2002_analysis_missing_gates = safe_int(metric_value(alb2002_analysis_candidate_summary, "alb2002_analysis_candidate_missing_gates"))
    alb2002_analysis_harmonized_ready = safe_int(metric_value(alb2002_analysis_candidate_summary, "alb2002_analysis_candidate_harmonized_ready_rows"))
    alb2002_analysis_data_write_ready = safe_int(metric_value(alb2002_analysis_candidate_summary, "alb2002_analysis_candidate_data_write_ready_rows"))
    alb2002_limited_core_rows = safe_int(metric_value(alb2002_harmonized_core_summary, "alb2002_harmonized_household_core_rows"))
    alb2002_limited_core_data_write_ready = safe_int(metric_value(alb2002_harmonized_core_summary, "alb2002_harmonized_household_core_limited_data_write_ready_rows"))
    alb2002_limited_financial_rows = safe_int(metric_value(alb2002_limited_financial_summary, "alb2002_limited_financial_outcome_rows"))
    alb2002_limited_financial_data_write_ready = safe_int(metric_value(alb2002_limited_financial_summary, "alb2002_limited_financial_outcome_limited_data_write_ready_rows"))
    alb2002_limited_financial_sdg_ready = safe_int(metric_value(alb2002_limited_financial_summary, "alb2002_limited_financial_outcome_sdg382_ready_rows"))
    alb2002_limited_financial_access_ready = safe_int(metric_value(alb2002_limited_financial_summary, "alb2002_limited_financial_outcome_access_ready_rows"))
    alb2002_limited_financial_composite_ready = safe_int(metric_value(alb2002_limited_financial_summary, "alb2002_limited_financial_outcome_composite_ready_rows"))
    alb2002_limited_financial_climate_ready = safe_int(metric_value(alb2002_limited_financial_summary, "alb2002_limited_financial_outcome_climate_linkage_ready_rows"))
    alb2002_limited_financial_analysis_ready = safe_int(metric_value(alb2002_limited_financial_summary, "alb2002_limited_financial_outcome_final_analysis_ready_rows"))
    alb2002_limited_climate_rows = safe_int(metric_value(alb2002_limited_climate_summary, "alb2002_limited_climate_exposure_rows"))
    alb2002_limited_climate_data_write_ready = safe_int(metric_value(alb2002_limited_climate_summary, "alb2002_limited_climate_exposure_limited_data_write_ready_rows"))
    alb2002_limited_climate_linkage_ready = safe_int(metric_value(alb2002_limited_climate_summary, "alb2002_limited_climate_exposure_climate_linkage_ready_rows"))
    alb2002_limited_climate_analysis_ready = safe_int(metric_value(alb2002_limited_climate_summary, "alb2002_limited_climate_exposure_final_analysis_ready_rows"))
    alb2002_limited_linked_rows = safe_int(metric_value(alb2002_limited_linked_summary, "alb2002_limited_climate_linked_rows"))
    alb2002_limited_linked_data_write_ready = safe_int(metric_value(alb2002_limited_linked_summary, "alb2002_limited_climate_linked_limited_data_write_ready_rows"))
    alb2002_limited_linked_descriptive_ready = safe_int(metric_value(alb2002_limited_linked_summary, "alb2002_limited_climate_linked_descriptive_ready_rows"))
    alb2002_limited_linked_predictive_ready = safe_int(metric_value(alb2002_limited_linked_summary, "alb2002_limited_climate_linked_predictive_ml_ready_rows"))
    alb2002_limited_linked_reduced_ready = safe_int(metric_value(alb2002_limited_linked_summary, "alb2002_limited_climate_linked_reduced_form_ready_rows"))
    alb2002_limited_linked_robustness_ready = safe_int(metric_value(alb2002_limited_linked_summary, "alb2002_limited_climate_linked_robustness_ready_rows"))
    alb2002_limited_linked_analysis_ready = safe_int(metric_value(alb2002_limited_linked_summary, "alb2002_limited_climate_linked_final_analysis_ready_rows"))
    alb2002_climate_centroid_inputs = safe_int(metric_value(alb2002_climate_centroid_summary, "alb2002_climate_centroid_input_rows"))
    alb2002_climate_centroid_exposures = safe_int(metric_value(alb2002_climate_centroid_summary, "alb2002_climate_centroid_exposure_rows"))
    alb2002_climate_centroid_api_rows = safe_int(metric_value(alb2002_climate_centroid_summary, "alb2002_climate_centroid_nasa_api_rows"))
    alb2002_climate_centroid_api_failed = safe_int(metric_value(alb2002_climate_centroid_summary, "alb2002_climate_centroid_nasa_failed_rows"))
    alb2002_climate_centroid_precip = safe_int(metric_value(alb2002_climate_centroid_summary, "alb2002_climate_centroid_precip_nonmissing_rows"))
    alb2002_climate_centroid_temp = safe_int(metric_value(alb2002_climate_centroid_summary, "alb2002_climate_centroid_temp_nonmissing_rows"))
    alb2002_climate_centroid_climate_ready = safe_int(metric_value(alb2002_climate_centroid_summary, "alb2002_climate_centroid_climate_linkage_ready_rows"))
    alb2002_climate_centroid_data_write_ready = safe_int(metric_value(alb2002_climate_centroid_summary, "alb2002_climate_centroid_data_write_ready_rows"))
    alb2002_climate_shock_rows = safe_int(metric_value(alb2002_climate_shock_summary, "alb2002_climate_shock_candidate_exposure_rows"))
    alb2002_climate_shock_reference_groups = safe_int(metric_value(alb2002_climate_shock_summary, "alb2002_climate_shock_candidate_reference_group_rows"))
    alb2002_climate_shock_precip_z = safe_int(metric_value(alb2002_climate_shock_summary, "alb2002_climate_shock_candidate_precip_z_nonmissing_rows"))
    alb2002_climate_shock_temp_z = safe_int(metric_value(alb2002_climate_shock_summary, "alb2002_climate_shock_candidate_temp_z_nonmissing_rows"))
    alb2002_climate_shock_combined = safe_int(metric_value(alb2002_climate_shock_summary, "alb2002_climate_shock_candidate_combined_stress_rows"))
    alb2002_climate_shock_climate_ready = safe_int(metric_value(alb2002_climate_shock_summary, "alb2002_climate_shock_candidate_climate_linkage_ready_rows"))
    alb2002_climate_shock_data_write_ready = safe_int(metric_value(alb2002_climate_shock_summary, "alb2002_climate_shock_candidate_data_write_ready_rows"))
    alb2002_linked_rows = safe_int(metric_value(alb2002_climate_outcome_linked_summary, "alb2002_climate_outcome_linked_candidate_rows"))
    alb2002_linked_households = safe_int(metric_value(alb2002_climate_outcome_linked_summary, "alb2002_climate_outcome_linked_candidate_household_rows"))
    alb2002_linked_windows = safe_int(metric_value(alb2002_climate_outcome_linked_summary, "alb2002_climate_outcome_linked_candidate_window_rows"))
    alb2002_linked_unmatched = safe_int(metric_value(alb2002_climate_outcome_linked_summary, "alb2002_climate_outcome_linked_candidate_unmatched_rows"))
    alb2002_linked_precip_z = safe_int(metric_value(alb2002_climate_outcome_linked_summary, "alb2002_climate_outcome_linked_candidate_precip_z_rows"))
    alb2002_linked_temp_z = safe_int(metric_value(alb2002_climate_outcome_linked_summary, "alb2002_climate_outcome_linked_candidate_temp_z_rows"))
    alb2002_linked_combined = safe_int(metric_value(alb2002_climate_outcome_linked_summary, "alb2002_climate_outcome_linked_candidate_combined_stress_rows"))
    alb2002_linked_climate_ready = safe_int(metric_value(alb2002_climate_outcome_linked_summary, "alb2002_climate_outcome_linked_candidate_climate_linkage_ready_rows"))
    alb2002_linked_outcome_ready = safe_int(metric_value(alb2002_climate_outcome_linked_summary, "alb2002_climate_outcome_linked_candidate_outcome_promotion_ready_rows"))
    alb2002_linked_harmonized_ready = safe_int(metric_value(alb2002_climate_outcome_linked_summary, "alb2002_climate_outcome_linked_candidate_harmonized_recipe_ready_rows"))
    alb2002_linked_data_write_ready = safe_int(metric_value(alb2002_climate_outcome_linked_summary, "alb2002_climate_outcome_linked_candidate_data_write_ready_rows"))
    alb2002_descriptive_input_rows = safe_int(metric_value(alb2002_linked_candidate_descriptive_summary, "alb2002_linked_candidate_descriptive_input_rows"))
    alb2002_descriptive_cell_rows = safe_int(metric_value(alb2002_linked_candidate_descriptive_summary, "alb2002_linked_candidate_descriptive_cell_rows"))
    alb2002_descriptive_climate_ready = safe_int(metric_value(alb2002_linked_candidate_descriptive_summary, "alb2002_linked_candidate_descriptive_climate_linkage_ready_rows"))
    alb2002_descriptive_outcome_ready = safe_int(metric_value(alb2002_linked_candidate_descriptive_summary, "alb2002_linked_candidate_descriptive_outcome_promotion_ready_rows"))
    alb2002_descriptive_data_write_ready = safe_int(metric_value(alb2002_linked_candidate_descriptive_summary, "alb2002_linked_candidate_descriptive_data_write_ready_rows"))
    alb2002_weight_positive_rows = safe_int(metric_value(alb2002_weight_design_summary, "alb2002_weight_design_positive_weight_rows"))
    alb2002_weight_key_match_rows = safe_int(metric_value(alb2002_weight_design_summary, "alb2002_weight_design_candidate_key_match_rows"))
    alb2002_weight_inference_ready_rows = safe_int(metric_value(alb2002_weight_design_summary, "alb2002_weight_design_weighted_inference_ready_rows"))
    alb2002_sample_design_doc_ready = safe_int(metric_value(alb2002_sample_design_summary, "alb2002_sample_design_documentation_ready_rows"))
    alb2002_sample_design_raw_concordance = safe_int(metric_value(alb2002_sample_design_summary, "alb2002_sample_design_raw_design_concordance_rows"))
    albania_ready_waves = safe_int(metric_value(albania_first_summary, "albania_first_analysis_promotion_ready_wave_rows"))

    rows: list[dict[str, str]] = []
    add_row(
        rows,
        "harmonized_household_general_recipe_gate",
        "6",
        "data/harmonized_household.csv or data/harmonized_household.parquet",
        artifact_status(DATA_DIR / "harmonized_household.csv", DATA_DIR / "harmonized_household.parquet"),
        f"verified_recipe_candidates={verified_recipe_candidates}; ready_country_waves={ready_country_waves}; blocked_country_waves={blocked_country_waves}; value_audit_rows={value_audit_rows}",
        min(verified_recipe_candidates, ready_country_waves),
        "blocked_no_verified_recipe_candidates_or_ready_country_waves",
        "Complete raw value, unit, recall-period, merge-key, missing-code, and lineage audits, then create temp/harmonization_recipe.csv only from verified candidates.",
    )
    add_row(
        rows,
        "harmonized_household_alb2002_top_candidate",
        "6",
        "data/harmonized_household.csv or wave-specific promoted equivalent",
        artifact_status(DATA_DIR / "harmonized_household.csv", DATA_DIR / "harmonized_household.parquet"),
        f"temp_core_rows={alb2002_temp_rows}; analysis_candidate_rows={alb2002_analysis_candidate_rows}; analysis_complete_candidate_gates={alb2002_analysis_complete_gates}; analysis_missing_gates={alb2002_analysis_missing_gates}; analysis_data_write_ready={alb2002_analysis_data_write_ready}; limited_core_rows={alb2002_limited_core_rows}; limited_core_data_write_ready={alb2002_limited_core_data_write_ready}; core_recipe_ready={alb2002_recipe_ready}; weight_positive_rows={alb2002_weight_positive_rows}; weight_key_match_rows={alb2002_weight_key_match_rows}; sample_design_documentation_ready={alb2002_sample_design_doc_ready}; sample_design_raw_concordance={alb2002_sample_design_raw_concordance}; weight_inference_ready={alb2002_weight_inference_ready_rows}; minimum_harmonized_ready={alb2002_harmonized_ready}; analysis_harmonized_ready={alb2002_analysis_harmonized_ready}; period_aligned_che_policies={alb2002_period_aligned_policy_rows}; period_aligned_recipe_ready={alb2002_period_aligned_recipe_ready}; albania_ready_waves={albania_ready_waves}",
        alb2002_limited_core_rows if alb2002_limited_core_rows > 0 else min(alb2002_recipe_ready, alb2002_harmonized_ready, alb2002_analysis_harmonized_ready, alb2002_analysis_data_write_ready, albania_ready_waves),
        "limited_harmonized_core_promoted_full_analysis_still_blocked" if alb2002_limited_core_rows > 0 else "blocked_alb2002_temp_candidate_not_analysis_ready",
        "Use the limited ALB_2002 harmonized household core for inspection only; resolve weight/design semantics, OOP recall/inclusion, period-aligned numerator policy, access denominator, SDG denominator, and climate geography gates before outcome or climate-linked analysis.",
        "limited_harmonized_core_promoted_outcome_climate_blocked" if alb2002_limited_core_rows > 0 else None,
    )
    add_row(
        rows,
        "household_outcome_dataset",
        "8",
        "data/household_outcomes.csv or data/household_outcomes.parquet",
        artifact_status(DATA_DIR / "household_outcomes.csv", DATA_DIR / "household_outcomes.parquet"),
        f"alb2002_outcome_ready={alb2002_outcome_ready}; alb2002_sdg382_ready={alb2002_sdg_ready}; period_aligned_che_policies={alb2002_period_aligned_policy_rows}; period_aligned_ready={alb2002_period_aligned_period_ready}; period_aligned_outcome_ready={alb2002_period_aligned_outcome_ready}; combined_monthly_che10={alb2002_period_aligned_combined_che10}; combined_monthly_che25={alb2002_period_aligned_combined_che25}; che_candidate_rows={alb2002_che_candidate_rows}; che10_rows={alb2002_che_candidate_che10_rows}; che25_rows={alb2002_che_candidate_che25_rows}; che10_weighted={alb2002_che_candidate_che10_weighted}; che25_weighted={alb2002_che_candidate_che25_weighted}; che_candidate_promotion_ready={alb2002_che_candidate_promotion_ready}; limited_financial_rows={alb2002_limited_financial_rows}; limited_financial_data_write_ready={alb2002_limited_financial_data_write_ready}; limited_financial_sdg_ready={alb2002_limited_financial_sdg_ready}; limited_financial_access_ready={alb2002_limited_financial_access_ready}; limited_financial_composite_ready={alb2002_limited_financial_composite_ready}; limited_financial_climate_ready={alb2002_limited_financial_climate_ready}; access_candidate_rows={alb2002_access_candidate_rows}; access_any_rows={alb2002_access_candidate_any_rows}; access_cost_rows={alb2002_access_candidate_cost_rows}; access_any_weighted={alb2002_access_candidate_any_weighted}; access_outcome_promotion_ready={alb2002_access_candidate_promotion_ready}; uhc_composite_rows={alb2002_uhc_composite_rows}; che10_or_access_rows={alb2002_uhc_composite_che10_or_access}; che25_or_access_rows={alb2002_uhc_composite_che25_or_access}; coping_rows={alb2002_uhc_composite_coping}; uhc_composite_promotion_ready={alb2002_uhc_composite_promotion_ready}; harmonized_input_rows={csv_row_count(DATA_DIR / 'harmonized_household.csv')}",
        alb2002_limited_financial_rows if alb2002_limited_financial_rows > 0 else min(alb2002_outcome_ready, alb2002_che_candidate_promotion_ready, alb2002_access_candidate_promotion_ready, alb2002_uhc_composite_promotion_ready),
        "limited_financial_outcomes_promoted_sdg_access_climate_blocked" if alb2002_limited_financial_rows > 0 else "blocked_no_verified_harmonized_input_or_outcome_policy",
        "Use the limited ALB_2002 CHE10/CHE25 outcome file for financial-protection inspection only; resolve SDG 3.8.2, access, composite UHC, survey-design, and climate-linkage gates before modeling.",
        "limited_financial_outcomes_promoted_sdg_access_climate_blocked" if alb2002_limited_financial_rows > 0 else None,
    )
    add_row(
        rows,
        "climate_exposure_dataset",
        "9",
        "data/climate_exposures_nasa_power.csv",
        artifact_status(DATA_DIR / "climate_exposures_nasa_power.csv"),
        f"climate_linkage_ready_country_waves={ready_linkage_rows}; alb2002_climate_ready={alb2002_climate_ready}; period_aligned_che_climate_ready={alb2002_period_aligned_climate_ready}; che_candidate_climate_ready={alb2002_che_candidate_climate_ready}; access_candidate_climate_ready={alb2002_access_candidate_climate_ready}; uhc_composite_climate_ready={alb2002_uhc_composite_climate_ready}; centroid_input_rows={alb2002_climate_centroid_inputs}; centroid_exposure_rows={alb2002_climate_centroid_exposures}; centroid_api_rows={alb2002_climate_centroid_api_rows}; centroid_api_failed={alb2002_climate_centroid_api_failed}; centroid_precip_nonmissing={alb2002_climate_centroid_precip}; centroid_temp_nonmissing={alb2002_climate_centroid_temp}; centroid_climate_ready={alb2002_climate_centroid_climate_ready}; centroid_data_write_ready={alb2002_climate_centroid_data_write_ready}; limited_climate_rows={alb2002_limited_climate_rows}; limited_climate_data_write_ready={alb2002_limited_climate_data_write_ready}; limited_climate_linkage_ready={alb2002_limited_climate_linkage_ready}; limited_climate_analysis_ready={alb2002_limited_climate_analysis_ready}; shock_rows={alb2002_climate_shock_rows}; shock_reference_groups={alb2002_climate_shock_reference_groups}; shock_precip_z={alb2002_climate_shock_precip_z}; shock_temp_z={alb2002_climate_shock_temp_z}; shock_combined_stress={alb2002_climate_shock_combined}; shock_climate_ready={alb2002_climate_shock_climate_ready}; shock_data_write_ready={alb2002_climate_shock_data_write_ready}; linked_rows={alb2002_linked_rows}; linked_precip_z={alb2002_linked_precip_z}; linked_temp_z={alb2002_linked_temp_z}; linked_climate_ready={alb2002_linked_climate_ready}; linked_data_write_ready={alb2002_linked_data_write_ready}; climate_exposure_rows={csv_row_count(DATA_DIR / 'climate_exposures_nasa_power.csv')}",
        alb2002_limited_climate_rows if alb2002_limited_climate_rows > 0 else min(ready_linkage_rows, alb2002_climate_ready, alb2002_che_candidate_climate_ready, alb2002_access_candidate_climate_ready, alb2002_uhc_composite_climate_ready, alb2002_climate_centroid_climate_ready, alb2002_climate_centroid_data_write_ready, alb2002_climate_shock_climate_ready, alb2002_climate_shock_data_write_ready, alb2002_linked_climate_ready, alb2002_linked_data_write_ready),
        "limited_climate_exposure_promoted_full_linkage_still_blocked" if alb2002_limited_climate_rows > 0 else "blocked_no_verified_climate_linkage_input",
        "Use the limited NASA POWER admin2-centroid exposure file for fallback exposure inspection only; resolve historical geography, CHIRPS/ERA5, historical baselines, and outcome gates before climate-linked analysis.",
        "limited_climate_exposure_promoted_linkage_blocked" if alb2002_limited_climate_rows > 0 else None,
    )
    add_row(
        rows,
        "climate_linked_household_dataset",
        "7",
        "data/climate_linked_household.csv or data/climate_linked_household.parquet",
        artifact_status(DATA_DIR / "climate_linked_household.csv", DATA_DIR / "climate_linked_household.parquet"),
        f"harmonized_rows={csv_row_count(DATA_DIR / 'harmonized_household.csv')}; outcome_rows={csv_row_count(DATA_DIR / 'household_outcomes.csv')}; climate_exposure_rows={csv_row_count(DATA_DIR / 'climate_exposures_nasa_power.csv')}; limited_linked_rows={alb2002_limited_linked_rows}; limited_linked_data_write_ready={alb2002_limited_linked_data_write_ready}; limited_linked_descriptive_ready={alb2002_limited_linked_descriptive_ready}; limited_linked_predictive_ready={alb2002_limited_linked_predictive_ready}; limited_linked_reduced_ready={alb2002_limited_linked_reduced_ready}; alb2002_climate_ready={alb2002_climate_ready}; linked_candidate_rows={alb2002_linked_rows}; linked_households={alb2002_linked_households}; linked_windows={alb2002_linked_windows}; linked_unmatched_rows={alb2002_linked_unmatched}; linked_combined_stress={alb2002_linked_combined}; linked_harmonized_ready={alb2002_linked_harmonized_ready}; linked_outcome_ready={alb2002_linked_outcome_ready}; linked_climate_ready={alb2002_linked_climate_ready}; linked_data_write_ready={alb2002_linked_data_write_ready}",
        alb2002_limited_linked_rows if alb2002_limited_linked_rows > 0 else min(csv_row_count(DATA_DIR / "harmonized_household.csv"), csv_row_count(DATA_DIR / "climate_exposures_nasa_power.csv"), alb2002_climate_ready, alb2002_linked_harmonized_ready, alb2002_linked_outcome_ready, alb2002_linked_climate_ready, alb2002_linked_data_write_ready),
        "limited_climate_linked_promoted_descriptive_ml_causal_blocked" if alb2002_limited_linked_rows > 0 else "blocked_no_harmonized_microdata_or_climate_exposures",
        "Use the limited household-window climate-linked file for linkage inspection only; keep descriptive diagnostics and models blocked until final linkage, outcome, source, and baseline gates pass.",
        "limited_climate_linked_promoted_models_blocked" if alb2002_limited_linked_rows > 0 else None,
    )
    add_row(
        rows,
        "downstream_empirical_model_inputs",
        "10,11,12,14",
        "data/climate_linked_household.csv plus data/household_outcomes.csv",
        f"{artifact_status(DATA_DIR / 'climate_linked_household.csv', DATA_DIR / 'climate_linked_household.parquet')}; {artifact_status(DATA_DIR / 'household_outcomes.csv', DATA_DIR / 'household_outcomes.parquet')}",
        f"climate_linked_rows={csv_row_count(DATA_DIR / 'climate_linked_household.csv')}; outcome_rows={csv_row_count(DATA_DIR / 'household_outcomes.csv')}; limited_financial_analysis_ready={alb2002_limited_financial_analysis_ready}; linked_candidate_rows={alb2002_linked_rows}; descriptive_screen_input_rows={alb2002_descriptive_input_rows}; descriptive_screen_cell_rows={alb2002_descriptive_cell_rows}; descriptive_screen_climate_ready={alb2002_descriptive_climate_ready}; descriptive_screen_outcome_ready={alb2002_descriptive_outcome_ready}; descriptive_screen_data_write_ready={alb2002_descriptive_data_write_ready}",
        min(csv_row_count(DATA_DIR / "climate_linked_household.csv"), csv_row_count(DATA_DIR / "household_outcomes.csv"), alb2002_descriptive_climate_ready, alb2002_descriptive_outcome_ready, alb2002_descriptive_data_write_ready, alb2002_limited_linked_descriptive_ready, alb2002_limited_linked_predictive_ready, alb2002_limited_linked_reduced_ready, alb2002_limited_linked_robustness_ready, alb2002_limited_linked_analysis_ready),
        "blocked_downstream_models_without_analysis_dataset",
        "Run promoted descriptive, predictive, reduced-form, and robustness stages only after linked data and outcome data are promoted.",
    )
    return rows


def build_summary(rows: list[dict[str, str]]) -> list[dict[str, str]]:
    harmonization_summary = read_csv_dicts(RESULT_DIR / "harmonization_recipe_gate_summary.csv")
    alb2002_core_summary = read_csv_dicts(RESULT_DIR / "alb2002_household_core_candidate_summary.csv")
    alb2002_minimum_summary = read_csv_dicts(RESULT_DIR / "alb2002_minimum_recipe_promotion_summary.csv")
    alb2002_period_aligned_che_summary = read_csv_dicts(RESULT_DIR / "alb2002_period_aligned_che_policy_summary.csv")
    alb2002_che_candidate_summary = read_csv_dicts(RESULT_DIR / "alb2002_che_candidate_outcome_summary.csv")
    alb2002_access_candidate_summary = read_csv_dicts(RESULT_DIR / "alb2002_access_candidate_outcome_summary.csv")
    alb2002_uhc_composite_summary = read_csv_dicts(RESULT_DIR / "alb2002_uhc_composite_candidate_summary.csv")
    alb2002_analysis_candidate_summary = read_csv_dicts(RESULT_DIR / "alb2002_analysis_candidate_readiness_summary.csv")
    alb2002_harmonized_core_summary = read_csv_dicts(RESULT_DIR / "alb2002_harmonized_household_core_promotion_summary.csv")
    alb2002_limited_financial_summary = read_csv_dicts(RESULT_DIR / "alb2002_limited_financial_outcome_promotion_summary.csv")
    alb2002_limited_climate_summary = read_csv_dicts(RESULT_DIR / "alb2002_limited_climate_exposure_promotion_summary.csv")
    alb2002_limited_linked_summary = read_csv_dicts(RESULT_DIR / "alb2002_limited_climate_linked_promotion_summary.csv")
    alb2002_climate_centroid_summary = read_csv_dicts(RESULT_DIR / "alb2002_climate_centroid_exposure_summary.csv")
    alb2002_climate_shock_summary = read_csv_dicts(RESULT_DIR / "alb2002_climate_shock_candidate_summary.csv")
    alb2002_climate_outcome_linked_summary = read_csv_dicts(RESULT_DIR / "alb2002_climate_outcome_linked_candidate_summary.csv")
    alb2002_linked_candidate_descriptive_summary = read_csv_dicts(RESULT_DIR / "alb2002_linked_candidate_descriptive_summary.csv")
    alb2002_weight_design_summary = read_csv_dicts(RESULT_DIR / "alb2002_weight_design_evidence_summary.csv")
    alb2002_sample_design_summary = read_csv_dicts(RESULT_DIR / "alb2002_sample_design_documentation_summary.csv")
    promoted = sum(1 for row in rows if row.get("promotion_decision") != "blocked_keep_out_of_data")
    return [
        {"metric": "analysis_dataset_promotion_audit_rows", "value": str(len(rows)), "interpretation": "Rows checking missing analysis-ready data promotion targets."},
        {"metric": "analysis_dataset_promotion_blocked_rows", "value": str(len(rows) - promoted), "interpretation": "Promotion targets still blocked from data/."},
        {"metric": "analysis_dataset_promotion_promoted_rows", "value": str(promoted), "interpretation": "Promotion targets currently allowed for data/ write; limited core/outcome/exposure/linked diagnostic files are allowed while analysis-ready models remain blocked."},
        {"metric": "analysis_dataset_promotion_data_file_count", "value": str(data_file_count()), "interpretation": "Files currently present under data/."},
        {"metric": "analysis_dataset_promotion_verified_recipe_candidates", "value": metric_value(harmonization_summary, "verified_candidate_rows"), "interpretation": "General harmonization recipe candidate rows verified by value/unit/recall/key checks."},
        {"metric": "analysis_dataset_promotion_ready_country_waves", "value": metric_value(harmonization_summary, "ready_country_wave_rows"), "interpretation": "Country-waves ready for verified harmonization recipe assembly."},
        {"metric": "analysis_dataset_promotion_alb2002_temp_core_rows", "value": metric_value(alb2002_core_summary, "alb2002_household_core_candidate_rows"), "interpretation": "ALB_2002 temp-only household core rows."},
        {"metric": "analysis_dataset_promotion_alb2002_weight_positive_rows", "value": metric_value(alb2002_weight_design_summary, "alb2002_weight_design_positive_weight_rows"), "interpretation": "ALB_2002 positive household-weight rows observed in the readable weight file."},
        {"metric": "analysis_dataset_promotion_alb2002_weight_key_match_rows", "value": metric_value(alb2002_weight_design_summary, "alb2002_weight_design_candidate_key_match_rows"), "interpretation": "ALB_2002 readable weight-file keys matching the temp household core."},
        {"metric": "analysis_dataset_promotion_alb2002_sample_design_documentation_ready_rows", "value": metric_value(alb2002_sample_design_summary, "alb2002_sample_design_documentation_ready_rows"), "interpretation": "ALB_2002 official sample-design documentation ready; this is not data promotion."},
        {"metric": "analysis_dataset_promotion_alb2002_sample_design_raw_concordance_rows", "value": metric_value(alb2002_sample_design_summary, "alb2002_sample_design_raw_design_concordance_rows"), "interpretation": "ALB_2002 raw and candidate row counts concord with official sample-design evidence."},
        {"metric": "analysis_dataset_promotion_alb2002_weighted_inference_ready_rows", "value": metric_value(alb2002_weight_design_summary, "alb2002_weight_design_weighted_inference_ready_rows"), "interpretation": "ALB_2002 rows ready for promoted weighted inference; should remain zero."},
        {"metric": "analysis_dataset_promotion_alb2002_harmonized_ready_rows", "value": metric_value(alb2002_minimum_summary, "alb2002_minimum_recipe_promotion_harmonized_ready_rows"), "interpretation": "ALB_2002 rows ready for harmonized data promotion."},
        {"metric": "analysis_dataset_promotion_alb2002_outcome_ready_rows", "value": metric_value(alb2002_minimum_summary, "alb2002_minimum_recipe_promotion_outcome_ready_rows"), "interpretation": "ALB_2002 rows ready for final outcome promotion."},
        {"metric": "analysis_dataset_promotion_alb2002_period_aligned_che_policy_rows", "value": metric_value(alb2002_period_aligned_che_summary, "alb2002_period_aligned_che_policy_rows"), "interpretation": "ALB_2002 period-aligned CHE stress-test policies observed upstream."},
        {"metric": "analysis_dataset_promotion_alb2002_period_aligned_che_period_ready_rows", "value": metric_value(alb2002_period_aligned_che_summary, "alb2002_period_aligned_che_period_alignment_ready_rows"), "interpretation": "ALB_2002 period-aligned CHE policies ready for stress testing but not outcome promotion."},
        {"metric": "analysis_dataset_promotion_alb2002_period_aligned_che_outcome_ready_rows", "value": metric_value(alb2002_period_aligned_che_summary, "alb2002_period_aligned_che_outcome_ready_rows"), "interpretation": "ALB_2002 period-aligned CHE rows ready for final outcome promotion; should remain zero."},
        {"metric": "analysis_dataset_promotion_alb2002_period_aligned_che_combined_che10_rate", "value": metric_value(alb2002_period_aligned_che_summary, "alb2002_period_aligned_che_combined_che10_rate", ""), "interpretation": "Combined monthly-equivalent CHE10 stress-test rate; not a final outcome."},
        {"metric": "analysis_dataset_promotion_alb2002_period_aligned_che_combined_che25_rate", "value": metric_value(alb2002_period_aligned_che_summary, "alb2002_period_aligned_che_combined_che25_rate", ""), "interpretation": "Combined monthly-equivalent CHE25 stress-test rate; not a final outcome."},
        {"metric": "analysis_dataset_promotion_alb2002_che_candidate_rows", "value": metric_value(alb2002_che_candidate_summary, "alb2002_che_candidate_household_rows"), "interpretation": "ALB_2002 temp-only household CHE candidate rows."},
        {"metric": "analysis_dataset_promotion_alb2002_che_candidate_che10_rows", "value": metric_value(alb2002_che_candidate_summary, "alb2002_che_candidate_che10_rows"), "interpretation": "ALB_2002 temp-only CHE10 candidate rows."},
        {"metric": "analysis_dataset_promotion_alb2002_che_candidate_che10_weighted_rate", "value": metric_value(alb2002_che_candidate_summary, "alb2002_che_candidate_che10_weighted_rate", ""), "interpretation": "Weighted CHE10 candidate rate; not a promoted outcome."},
        {"metric": "analysis_dataset_promotion_alb2002_che_candidate_che25_rows", "value": metric_value(alb2002_che_candidate_summary, "alb2002_che_candidate_che25_rows"), "interpretation": "ALB_2002 temp-only CHE25 candidate rows."},
        {"metric": "analysis_dataset_promotion_alb2002_che_candidate_che25_weighted_rate", "value": metric_value(alb2002_che_candidate_summary, "alb2002_che_candidate_che25_weighted_rate", ""), "interpretation": "Weighted CHE25 candidate rate; not a promoted outcome."},
        {"metric": "analysis_dataset_promotion_alb2002_che_candidate_outcome_promotion_ready_rows", "value": metric_value(alb2002_che_candidate_summary, "alb2002_che_candidate_outcome_promotion_ready_rows"), "interpretation": "ALB_2002 temp-only CHE candidate rows ready for final outcome promotion; should remain zero."},
        {"metric": "analysis_dataset_promotion_alb2002_access_candidate_rows", "value": metric_value(alb2002_access_candidate_summary, "alb2002_access_candidate_household_rows"), "interpretation": "ALB_2002 temp-only household access candidate rows."},
        {"metric": "analysis_dataset_promotion_alb2002_access_candidate_any_rows", "value": metric_value(alb2002_access_candidate_summary, "alb2002_access_candidate_composite_any_rows"), "interpretation": "ALB_2002 temp-only composite any-access-barrier rows."},
        {"metric": "analysis_dataset_promotion_alb2002_access_candidate_any_weighted_rate", "value": metric_value(alb2002_access_candidate_summary, "alb2002_access_candidate_composite_any_weighted_rate", ""), "interpretation": "Weighted composite any-access-barrier candidate rate; not a promoted outcome."},
        {"metric": "analysis_dataset_promotion_alb2002_access_candidate_cost_rows", "value": metric_value(alb2002_access_candidate_summary, "alb2002_access_candidate_composite_cost_rows"), "interpretation": "ALB_2002 temp-only composite cost-barrier rows."},
        {"metric": "analysis_dataset_promotion_alb2002_access_candidate_outcome_promotion_ready_rows", "value": metric_value(alb2002_access_candidate_summary, "alb2002_access_candidate_outcome_promotion_ready_rows"), "interpretation": "ALB_2002 temp-only access candidate rows ready for final outcome promotion; should remain zero."},
        {"metric": "analysis_dataset_promotion_alb2002_uhc_composite_rows", "value": metric_value(alb2002_uhc_composite_summary, "alb2002_uhc_composite_candidate_household_rows"), "interpretation": "ALB_2002 temp-only composite UHC candidate rows."},
        {"metric": "analysis_dataset_promotion_alb2002_uhc_composite_che10_or_access_rows", "value": metric_value(alb2002_uhc_composite_summary, "alb2002_uhc_composite_candidate_che10_or_access_rows"), "interpretation": "ALB_2002 temp-only CHE10-or-access candidate rows."},
        {"metric": "analysis_dataset_promotion_alb2002_uhc_composite_che25_or_access_rows", "value": metric_value(alb2002_uhc_composite_summary, "alb2002_uhc_composite_candidate_che25_or_access_rows"), "interpretation": "ALB_2002 temp-only CHE25-or-access candidate rows."},
        {"metric": "analysis_dataset_promotion_alb2002_uhc_composite_coping_rows", "value": metric_value(alb2002_uhc_composite_summary, "alb2002_uhc_composite_candidate_coping_rows"), "interpretation": "ALB_2002 temp-only health-cost coping candidate rows."},
        {"metric": "analysis_dataset_promotion_alb2002_uhc_composite_outcome_promotion_ready_rows", "value": metric_value(alb2002_uhc_composite_summary, "alb2002_uhc_composite_candidate_outcome_promotion_ready_rows"), "interpretation": "ALB_2002 temp-only UHC composite candidate rows ready for final outcome promotion; should remain zero."},
        {"metric": "analysis_dataset_promotion_alb2002_analysis_candidate_rows", "value": metric_value(alb2002_analysis_candidate_summary, "alb2002_analysis_candidate_rows"), "interpretation": "ALB_2002 temp-only joined analysis-candidate household rows."},
        {"metric": "analysis_dataset_promotion_alb2002_analysis_candidate_complete_gates", "value": metric_value(alb2002_analysis_candidate_summary, "alb2002_analysis_candidate_complete_candidate_gates"), "interpretation": "ALB_2002 candidate field families with complete observed coverage, still not promoted."},
        {"metric": "analysis_dataset_promotion_alb2002_analysis_candidate_missing_gates", "value": metric_value(alb2002_analysis_candidate_summary, "alb2002_analysis_candidate_missing_gates"), "interpretation": "ALB_2002 candidate field families with missing required coverage."},
        {"metric": "analysis_dataset_promotion_alb2002_analysis_candidate_data_write_ready_rows", "value": metric_value(alb2002_analysis_candidate_summary, "alb2002_analysis_candidate_data_write_ready_rows"), "interpretation": "ALB_2002 joined analysis-candidate rows allowed to be written to data/; should remain zero."},
        {"metric": "analysis_dataset_promotion_limited_harmonized_core_rows", "value": metric_value(alb2002_harmonized_core_summary, "alb2002_harmonized_household_core_rows"), "interpretation": "ALB_2002 rows written to data/harmonized_household.csv under limited core scope."},
        {"metric": "analysis_dataset_promotion_limited_harmonized_core_data_write_ready_rows", "value": metric_value(alb2002_harmonized_core_summary, "alb2002_harmonized_household_core_limited_data_write_ready_rows"), "interpretation": "Rows allowed for data/ write only as limited harmonized household core."},
        {"metric": "analysis_dataset_promotion_limited_harmonized_core_final_outcome_ready_rows", "value": metric_value(alb2002_harmonized_core_summary, "alb2002_harmonized_household_core_final_outcome_ready_rows"), "interpretation": "Rows ready for final outcome construction; should remain zero."},
        {"metric": "analysis_dataset_promotion_limited_harmonized_core_climate_linkage_ready_rows", "value": metric_value(alb2002_harmonized_core_summary, "alb2002_harmonized_household_core_climate_linkage_ready_rows"), "interpretation": "Rows ready for climate linkage; should remain zero."},
        {"metric": "analysis_dataset_promotion_limited_harmonized_core_analysis_ready_rows", "value": metric_value(alb2002_harmonized_core_summary, "alb2002_harmonized_household_core_analysis_ready_rows"), "interpretation": "Rows ready for final empirical analysis; should remain zero."},
        {"metric": "analysis_dataset_promotion_limited_financial_outcome_rows", "value": metric_value(alb2002_limited_financial_summary, "alb2002_limited_financial_outcome_rows"), "interpretation": "ALB_2002 rows written to data/household_outcomes.csv under limited CHE-only scope."},
        {"metric": "analysis_dataset_promotion_limited_financial_outcome_data_write_ready_rows", "value": metric_value(alb2002_limited_financial_summary, "alb2002_limited_financial_outcome_limited_data_write_ready_rows"), "interpretation": "Rows allowed for data/ write only as limited CHE10/CHE25 financial outcomes."},
        {"metric": "analysis_dataset_promotion_limited_financial_outcome_che10_rows", "value": metric_value(alb2002_limited_financial_summary, "alb2002_limited_financial_outcome_che10_rows"), "interpretation": "Limited CHE10 outcome rows."},
        {"metric": "analysis_dataset_promotion_limited_financial_outcome_che25_rows", "value": metric_value(alb2002_limited_financial_summary, "alb2002_limited_financial_outcome_che25_rows"), "interpretation": "Limited CHE25 outcome rows."},
        {"metric": "analysis_dataset_promotion_limited_financial_outcome_sdg382_ready_rows", "value": metric_value(alb2002_limited_financial_summary, "alb2002_limited_financial_outcome_sdg382_ready_rows"), "interpretation": "Rows ready for SDG 3.8.2; should remain zero."},
        {"metric": "analysis_dataset_promotion_limited_financial_outcome_access_ready_rows", "value": metric_value(alb2002_limited_financial_summary, "alb2002_limited_financial_outcome_access_ready_rows"), "interpretation": "Rows ready for access outcomes; should remain zero."},
        {"metric": "analysis_dataset_promotion_limited_financial_outcome_composite_ready_rows", "value": metric_value(alb2002_limited_financial_summary, "alb2002_limited_financial_outcome_composite_ready_rows"), "interpretation": "Rows ready for composite UHC outcomes; should remain zero."},
        {"metric": "analysis_dataset_promotion_limited_financial_outcome_climate_linkage_ready_rows", "value": metric_value(alb2002_limited_financial_summary, "alb2002_limited_financial_outcome_climate_linkage_ready_rows"), "interpretation": "Rows ready for final climate linkage; should remain zero."},
        {"metric": "analysis_dataset_promotion_limited_financial_outcome_analysis_ready_rows", "value": metric_value(alb2002_limited_financial_summary, "alb2002_limited_financial_outcome_final_analysis_ready_rows"), "interpretation": "Rows ready for final empirical analysis; should remain zero."},
        {"metric": "analysis_dataset_promotion_limited_climate_exposure_rows", "value": metric_value(alb2002_limited_climate_summary, "alb2002_limited_climate_exposure_rows"), "interpretation": "ALB_2002 limited NASA POWER admin2-centroid exposure rows written to data/."},
        {"metric": "analysis_dataset_promotion_limited_climate_exposure_data_write_ready_rows", "value": metric_value(alb2002_limited_climate_summary, "alb2002_limited_climate_exposure_limited_data_write_ready_rows"), "interpretation": "Rows allowed for data/ write only as limited fallback climate exposures."},
        {"metric": "analysis_dataset_promotion_limited_climate_exposure_climate_linkage_ready_rows", "value": metric_value(alb2002_limited_climate_summary, "alb2002_limited_climate_exposure_climate_linkage_ready_rows"), "interpretation": "Rows ready for final climate linkage; should remain zero."},
        {"metric": "analysis_dataset_promotion_limited_climate_exposure_analysis_ready_rows", "value": metric_value(alb2002_limited_climate_summary, "alb2002_limited_climate_exposure_final_analysis_ready_rows"), "interpretation": "Rows ready for final empirical analysis; should remain zero."},
        {"metric": "analysis_dataset_promotion_limited_climate_linked_rows", "value": metric_value(alb2002_limited_linked_summary, "alb2002_limited_climate_linked_rows"), "interpretation": "ALB_2002 rows written to data/climate_linked_household.csv under limited diagnostic scope."},
        {"metric": "analysis_dataset_promotion_limited_climate_linked_data_write_ready_rows", "value": metric_value(alb2002_limited_linked_summary, "alb2002_limited_climate_linked_limited_data_write_ready_rows"), "interpretation": "Rows allowed for data/ write only as limited climate-linked diagnostics."},
        {"metric": "analysis_dataset_promotion_limited_climate_linked_descriptive_ready_rows", "value": metric_value(alb2002_limited_linked_summary, "alb2002_limited_climate_linked_descriptive_ready_rows"), "interpretation": "Rows ready for promoted descriptive diagnostics; should remain zero."},
        {"metric": "analysis_dataset_promotion_limited_climate_linked_predictive_ml_ready_rows", "value": metric_value(alb2002_limited_linked_summary, "alb2002_limited_climate_linked_predictive_ml_ready_rows"), "interpretation": "Rows ready for predictive ML; should remain zero."},
        {"metric": "analysis_dataset_promotion_limited_climate_linked_reduced_form_ready_rows", "value": metric_value(alb2002_limited_linked_summary, "alb2002_limited_climate_linked_reduced_form_ready_rows"), "interpretation": "Rows ready for reduced-form estimation; should remain zero."},
        {"metric": "analysis_dataset_promotion_limited_climate_linked_robustness_ready_rows", "value": metric_value(alb2002_limited_linked_summary, "alb2002_limited_climate_linked_robustness_ready_rows"), "interpretation": "Rows ready for robustness checks; should remain zero."},
        {"metric": "analysis_dataset_promotion_limited_climate_linked_analysis_ready_rows", "value": metric_value(alb2002_limited_linked_summary, "alb2002_limited_climate_linked_final_analysis_ready_rows"), "interpretation": "Rows ready for final empirical analysis; should remain zero."},
        {"metric": "analysis_dataset_promotion_alb2002_climate_centroid_input_rows", "value": metric_value(alb2002_climate_centroid_summary, "alb2002_climate_centroid_input_rows"), "interpretation": "ALB_2002 temp-only climate centroid input district-month cells."},
        {"metric": "analysis_dataset_promotion_alb2002_climate_centroid_exposure_rows", "value": metric_value(alb2002_climate_centroid_summary, "alb2002_climate_centroid_exposure_rows"), "interpretation": "ALB_2002 temp-only climate centroid exposure rows."},
        {"metric": "analysis_dataset_promotion_alb2002_climate_centroid_nasa_failed_rows", "value": metric_value(alb2002_climate_centroid_summary, "alb2002_climate_centroid_nasa_failed_rows"), "interpretation": "ALB_2002 NASA POWER centroid request failures."},
        {"metric": "analysis_dataset_promotion_alb2002_climate_centroid_climate_linkage_ready_rows", "value": metric_value(alb2002_climate_centroid_summary, "alb2002_climate_centroid_climate_linkage_ready_rows"), "interpretation": "ALB_2002 centroid exposure rows ready for promoted climate linkage; should remain zero."},
        {"metric": "analysis_dataset_promotion_alb2002_climate_centroid_data_write_ready_rows", "value": metric_value(alb2002_climate_centroid_summary, "alb2002_climate_centroid_data_write_ready_rows"), "interpretation": "ALB_2002 centroid exposure rows allowed for data/ write; should remain zero."},
        {"metric": "analysis_dataset_promotion_alb2002_climate_shock_rows", "value": metric_value(alb2002_climate_shock_summary, "alb2002_climate_shock_candidate_exposure_rows"), "interpretation": "ALB_2002 temp-only climate shock diagnostic rows."},
        {"metric": "analysis_dataset_promotion_alb2002_climate_shock_reference_groups", "value": metric_value(alb2002_climate_shock_summary, "alb2002_climate_shock_candidate_reference_group_rows"), "interpretation": "ALB_2002 survey-month/window diagnostic reference groups."},
        {"metric": "analysis_dataset_promotion_alb2002_climate_shock_precip_z_rows", "value": metric_value(alb2002_climate_shock_summary, "alb2002_climate_shock_candidate_precip_z_nonmissing_rows"), "interpretation": "ALB_2002 diagnostic rainfall z-score rows."},
        {"metric": "analysis_dataset_promotion_alb2002_climate_shock_temp_z_rows", "value": metric_value(alb2002_climate_shock_summary, "alb2002_climate_shock_candidate_temp_z_nonmissing_rows"), "interpretation": "ALB_2002 diagnostic temperature z-score rows."},
        {"metric": "analysis_dataset_promotion_alb2002_climate_shock_combined_stress_rows", "value": metric_value(alb2002_climate_shock_summary, "alb2002_climate_shock_candidate_combined_stress_rows"), "interpretation": "ALB_2002 diagnostic combined climate-stress rows; not accepted treatments."},
        {"metric": "analysis_dataset_promotion_alb2002_climate_shock_climate_linkage_ready_rows", "value": metric_value(alb2002_climate_shock_summary, "alb2002_climate_shock_candidate_climate_linkage_ready_rows"), "interpretation": "ALB_2002 shock diagnostic rows ready for promoted climate linkage; should remain zero."},
        {"metric": "analysis_dataset_promotion_alb2002_climate_shock_data_write_ready_rows", "value": metric_value(alb2002_climate_shock_summary, "alb2002_climate_shock_candidate_data_write_ready_rows"), "interpretation": "ALB_2002 shock diagnostic rows allowed for data/ write; should remain zero."},
        {"metric": "analysis_dataset_promotion_alb2002_climate_outcome_linked_rows", "value": metric_value(alb2002_climate_outcome_linked_summary, "alb2002_climate_outcome_linked_candidate_rows"), "interpretation": "ALB_2002 temp-only household-window climate/outcome linked candidate rows."},
        {"metric": "analysis_dataset_promotion_alb2002_climate_outcome_linked_households", "value": metric_value(alb2002_climate_outcome_linked_summary, "alb2002_climate_outcome_linked_candidate_household_rows"), "interpretation": "ALB_2002 households represented in the linked candidate."},
        {"metric": "analysis_dataset_promotion_alb2002_climate_outcome_linked_windows", "value": metric_value(alb2002_climate_outcome_linked_summary, "alb2002_climate_outcome_linked_candidate_window_rows"), "interpretation": "Diagnostic exposure windows per household in the linked candidate."},
        {"metric": "analysis_dataset_promotion_alb2002_climate_outcome_linked_unmatched_rows", "value": metric_value(alb2002_climate_outcome_linked_summary, "alb2002_climate_outcome_linked_candidate_unmatched_rows"), "interpretation": "Linked candidate rows without a diagnostic climate window; should remain zero."},
        {"metric": "analysis_dataset_promotion_alb2002_climate_outcome_linked_combined_stress_rows", "value": metric_value(alb2002_climate_outcome_linked_summary, "alb2002_climate_outcome_linked_candidate_combined_stress_rows"), "interpretation": "ALB_2002 linked diagnostic combined climate-stress rows; not accepted treatments."},
        {"metric": "analysis_dataset_promotion_alb2002_climate_outcome_linked_harmonized_ready_rows", "value": metric_value(alb2002_climate_outcome_linked_summary, "alb2002_climate_outcome_linked_candidate_harmonized_recipe_ready_rows"), "interpretation": "ALB_2002 linked rows ready for harmonized recipe promotion; should remain zero."},
        {"metric": "analysis_dataset_promotion_alb2002_climate_outcome_linked_outcome_ready_rows", "value": metric_value(alb2002_climate_outcome_linked_summary, "alb2002_climate_outcome_linked_candidate_outcome_promotion_ready_rows"), "interpretation": "ALB_2002 linked rows ready for outcome promotion; should remain zero."},
        {"metric": "analysis_dataset_promotion_alb2002_climate_outcome_linked_climate_ready_rows", "value": metric_value(alb2002_climate_outcome_linked_summary, "alb2002_climate_outcome_linked_candidate_climate_linkage_ready_rows"), "interpretation": "ALB_2002 linked rows ready for promoted climate linkage; should remain zero."},
        {"metric": "analysis_dataset_promotion_alb2002_climate_outcome_linked_data_write_ready_rows", "value": metric_value(alb2002_climate_outcome_linked_summary, "alb2002_climate_outcome_linked_candidate_data_write_ready_rows"), "interpretation": "ALB_2002 linked rows allowed for data/ write; should remain zero."},
        {"metric": "analysis_dataset_promotion_alb2002_linked_candidate_descriptive_input_rows", "value": metric_value(alb2002_linked_candidate_descriptive_summary, "alb2002_linked_candidate_descriptive_input_rows"), "interpretation": "ALB_2002 temp-only linked rows screened by the candidate descriptive diagnostic."},
        {"metric": "analysis_dataset_promotion_alb2002_linked_candidate_descriptive_cell_rows", "value": metric_value(alb2002_linked_candidate_descriptive_summary, "alb2002_linked_candidate_descriptive_cell_rows"), "interpretation": "ALB_2002 linked-candidate descriptive screen cells; not promoted descriptive diagnostics."},
        {"metric": "analysis_dataset_promotion_alb2002_linked_candidate_descriptive_climate_ready_rows", "value": metric_value(alb2002_linked_candidate_descriptive_summary, "alb2002_linked_candidate_descriptive_climate_linkage_ready_rows"), "interpretation": "ALB_2002 descriptive-screen rows ready for promoted climate linkage; should remain zero."},
        {"metric": "analysis_dataset_promotion_alb2002_linked_candidate_descriptive_outcome_ready_rows", "value": metric_value(alb2002_linked_candidate_descriptive_summary, "alb2002_linked_candidate_descriptive_outcome_promotion_ready_rows"), "interpretation": "ALB_2002 descriptive-screen rows ready for outcome promotion; should remain zero."},
        {"metric": "analysis_dataset_promotion_alb2002_linked_candidate_descriptive_data_write_ready_rows", "value": metric_value(alb2002_linked_candidate_descriptive_summary, "alb2002_linked_candidate_descriptive_data_write_ready_rows"), "interpretation": "ALB_2002 descriptive-screen rows allowed for data/ write; should remain zero."},
        {"metric": "analysis_dataset_promotion_alb2002_climate_linkage_ready_rows", "value": metric_value(alb2002_minimum_summary, "alb2002_minimum_recipe_promotion_climate_linkage_ready_rows"), "interpretation": "ALB_2002 rows ready for climate-linkage promotion."},
        {"metric": "analysis_dataset_promotion_current_decision", "value": DECISION, "interpretation": "Current fail-closed decision for data/ promotion."},
    ]


def markdown_rows(rows: list[dict[str, str]]) -> str:
    columns = ["promotion_target", "completion_criteria", "artifact_status", "ready_rows", "blocking_status", "next_action"]
    lines = ["| " + " | ".join(columns) + " |", "|" + "|".join("---" for _ in columns) + "|"]
    for row in rows:
        values = []
        for column in columns:
            value = (row.get(column, "") or "").replace("|", "/")
            if len(value) > 130:
                value = value[:127] + "..."
            values.append(value)
        lines.append("| " + " | ".join(values) + " |")
    return "\n".join(lines)


def write_report(rows: list[dict[str, str]], summary: list[dict[str, str]]) -> None:
    summary_table = "\n".join(f"| {row['metric']} | {row['value']} | {row['interpretation']} |" for row in summary)
    REPORT_PATH.write_text(
        f"""# Analysis Dataset Promotion Barriers

Status: limited core, CHE-only financial outcomes, fallback climate exposure, and household-window linked diagnostics promoted, modeling fail-closed. This audit reconciles the general harmonization recipe gate, the Albania-specific promotion gates, and the current `data/` directory. It allows only the scoped ALB_2002 harmonized household core, limited CHE10/CHE25 outcome rows, limited NASA POWER admin2-centroid exposure rows, and a limited household-window climate-linked diagnostic file. It does not create SDG 3.8.2, access, composite UHC, descriptive-ready, causal-shock, or model-ready data.

## Summary

| Metric | Value | Interpretation |
|---|---:|---|
{summary_table}

## Promotion Targets

{markdown_rows(rows)}

## Interpretation

- The nearest local empirical candidate remains ALB_2002. Its limited harmonized household core is now in `data/harmonized_household.csv`, its limited CHE10/CHE25 financial-protection outcomes are in `data/household_outcomes.csv`, its limited NASA POWER admin2-centroid fallback exposures are in `data/climate_exposures_nasa_power.csv`, and its limited household-window linked diagnostic file is in `data/climate_linked_household.csv`; all carry guardrail markers that block SDG 3.8.2, access/composite outcome claims, final climate-linkage readiness, descriptive diagnostics, and model use.
- The general harmonization gate has no verified recipe candidates and no country-wave ready for verified recipe assembly.
- ALB_2002 now has full raw household-weight coverage, period-aligned monthly-equivalent CHE stress-test rates, limited CHE10/CHE25 outcome rows, temp-only access and composite UHC candidate outcomes, a joined temp analysis-candidate dataset, a limited harmonized household core, limited NASA POWER fallback exposure rows, within-candidate climate shock diagnostics, a limited household-window linked diagnostic file, and a linked-candidate descriptive screen. Descriptive and model-ready rows remain blocked because weight/design semantics, access denominator scope, SDG denominator, verified historical geography, primary climate sources, and climate baselines have not passed together.
- Descriptive diagnostics, predictive ML, reduced-form estimation, and robustness remain blocked by the limited linked file's `descriptive_ready`, `predictive_ml_ready`, `reduced_form_ready`, and `robustness_ready` flags staying zero.
- The correct current action is to resolve ALB_2002 access/SDG outcome plus climate-geography gates before writing any climate-linked or model input files to `data/`.

## Machine-Readable Outputs

- `temp/analysis_dataset_promotion_barrier_audit.csv`
- `result/analysis_dataset_promotion_barrier_summary.csv`
""",
        encoding="utf-8",
    )


def main() -> None:
    ensure_dirs()
    rows = build_rows()
    summary = build_summary(rows)
    write_csv(AUDIT_PATH, rows, AUDIT_COLUMNS)
    write_csv(SUMMARY_PATH, summary, SUMMARY_COLUMNS)
    write_report(rows, summary)
    append_log(TEMP_DIR / "audit_log.md", f"Built analysis dataset promotion barrier audit rows={len(rows)} decision={DECISION}.")
    print(f"Analysis dataset promotion barrier audit rows={len(rows)} decision={DECISION}.")


if __name__ == "__main__":
    main()
