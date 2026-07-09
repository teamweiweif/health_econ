from __future__ import annotations

import csv
from collections import Counter
from pathlib import Path
from typing import Any

from common import DATA_DIR, REPORT_DIR, RESULT_DIR, TEMP_DIR, append_log, ensure_dirs, write_csv


PLAN_PATH = TEMP_DIR / "modeling_identification_plan.csv"
VALIDATION_PATH = RESULT_DIR / "modeling_validation_plan.csv"
FALSIFICATION_PATH = RESULT_DIR / "falsification_placebo_plan.csv"
POLICY_PATH = RESULT_DIR / "policy_learning_plan.csv"
SUMMARY_PATH = RESULT_DIR / "modeling_identification_plan_summary.csv"
REPORT_PATH = REPORT_DIR / "modeling_identification_plan.md"

PLAN_COLUMNS = [
    "quality_rank",
    "country",
    "survey_name",
    "wave",
    "idno",
    "outcome",
    "outcome_family",
    "ingestion_gate_status",
    "outcome_gate_status",
    "climate_linkage_gate_status",
    "sample_gate_status",
    "eligible_for_final_sample",
    "predictive_ml_gate_status",
    "reduced_form_gate_status",
    "causal_ml_policy_gate_status",
    "robustness_gate_status",
    "policy_learning_gate_status",
    "minimum_required_inputs",
    "next_allowed_action",
    "blocking_gap",
]

VALIDATION_COLUMNS = [
    "outcome",
    "outcome_family",
    "validation_design",
    "eligible_model_families",
    "required_sample_structure",
    "required_metrics",
    "current_status",
    "blocking_gap",
    "guardrail",
]

FALSIFICATION_COLUMNS = [
    "test",
    "design_stage",
    "minimum_input",
    "pass_rule",
    "current_status",
    "blocking_gap",
    "interpretation_if_fails",
]

POLICY_COLUMNS = [
    "targeting_rule",
    "budget_share",
    "required_score_or_effect",
    "validation_requirement",
    "current_status",
    "blocking_gap",
    "sensitivity_required",
    "guardrail",
]

SUMMARY_COLUMNS = ["metric", "value", "interpretation"]

VALIDATION_DESIGNS = [
    {
        "validation_design": "leave_country_out",
        "required_sample_structure": "at least two raw-verified countries with constructed target and climate-linked rows",
        "guardrail": "required before transportable targeting claims",
    },
    {
        "validation_design": "leave_wave_out",
        "required_sample_structure": "at least two raw-verified waves or survey years for the target",
        "guardrail": "required before temporal generalization claims",
    },
    {
        "validation_design": "time_forward_validation",
        "required_sample_structure": "ordered survey timing with earlier waves used for training and later waves for testing",
        "guardrail": "use only where fieldwork timing supports a time split",
    },
    {
        "validation_design": "country_group_validation",
        "required_sample_structure": "country groups with enough events to compare model transportability",
        "guardrail": "group definitions must be pre-specified and not selected by performance",
    },
    {
        "validation_design": "random_split_sanity_check",
        "required_sample_structure": "constructed target with both classes and sufficient rows",
        "guardrail": "random split is a diagnostic only and cannot be the primary validation design",
    },
]

FALSIFICATION_TESTS = [
    {
        "test": "future_climate_lead_placebo",
        "stage": "identification",
        "input": "future rainfall/heat exposure constructed from verified geography and interview timing",
        "pass": "future shocks do not predict current UHC outcomes after the chosen controls",
        "fail": "downgrade climate estimates to weak/descriptive association",
    },
    {
        "test": "alternative_lag_grid",
        "stage": "robustness",
        "input": "1, 3, 6, and 12 month exposure windows",
        "pass": "sign and magnitude are not driven by a single arbitrary lag",
        "fail": "report instability and avoid a single-window causal claim",
    },
    {
        "test": "alternative_climate_source",
        "stage": "robustness",
        "input": "CHIRPS, ERA5-Land, NASA POWER, TerraClimate, or SPEI source variants as appropriate",
        "pass": "core result is not an artifact of one climate product",
        "fail": "treat source-sensitive estimates as fragile",
    },
    {
        "test": "seasonality_controls",
        "stage": "identification",
        "input": "verified interview month/date and survey timing controls",
        "pass": "results remain after survey-month or fieldwork-season controls",
        "fail": "do not interpret shock timing as causal",
    },
    {
        "test": "geography_fixed_effects",
        "stage": "identification",
        "input": "verified admin, cluster, or panel geography identifiers",
        "pass": "estimates are not explained by time-invariant local geography",
        "fail": "downgrade to descriptive cross-sectional pattern",
    },
    {
        "test": "admin_or_cluster_robust_variance",
        "stage": "robustness",
        "input": "verified clustering level and sufficient clusters",
        "pass": "inference survives design-appropriate clustering or survey variance treatment",
        "fail": "report uncertainty as too fragile for inference",
    },
    {
        "test": "country_leave_one_out",
        "stage": "robustness",
        "input": "at least two raw-verified countries in the estimation sample",
        "pass": "pooled estimate is not driven by one country",
        "fail": "report country-specific evidence only",
    },
    {
        "test": "survey_design_weight_sensitivity",
        "stage": "robustness",
        "input": "verified survey weights, strata, and PSU variables where available",
        "pass": "weighted and unweighted/design-adjusted conclusions are consistent enough to interpret",
        "fail": "report design sensitivity and avoid precise pooled claims",
    },
    {
        "test": "non_climate_sensitive_outcome_placebo",
        "stage": "falsification",
        "input": "defensible outcome unlikely to respond to climate shocks",
        "pass": "placebo outcome is not predicted by climate shock",
        "fail": "suspect omitted seasonality, geography, or survey artifacts",
    },
    {
        "test": "negative_control_group",
        "stage": "falsification",
        "input": "pre-specified group with weak expected shock channel and sufficient sample size",
        "pass": "effect is weaker or absent in the negative-control group",
        "fail": "heterogeneity story is not credible",
    },
    {
        "test": "gps_vs_admin_aggregation",
        "stage": "measurement",
        "input": "point/cluster coordinates and admin geography that can both be linked",
        "pass": "conclusions are not driven by exposure aggregation level",
        "fail": "report exposure measurement error and lower causal confidence",
    },
    {
        "test": "multiple_testing_control",
        "stage": "inference",
        "input": "pre-specified outcome, exposure, subgroup, and lag family",
        "pass": "key findings survive an explicit multiple-testing adjustment or are labeled exploratory",
        "fail": "do not present exploratory significant results as confirmatory",
    },
]

TARGETING_RULES = [
    ("cate_based_targeting", "estimated individual treatment-effect ranking from causal ML"),
    ("predicted_risk_targeting", "validated out-of-sample UHC failure risk score"),
    ("poverty_only_targeting", "pre-shock poverty or consumption/income rank"),
    ("rural_only_targeting", "verified rural residence flag"),
    ("agricultural_livelihood_targeting", "verified agriculture/livelihood variable"),
    ("children_in_household_targeting", "verified child age-structure indicator"),
    ("elderly_in_household_targeting", "verified elderly age-structure indicator"),
    ("high_climate_shock_area_blanket", "verified recent local climate-shock exposure"),
    ("recent_illness_need_targeting", "verified health need/illness variable"),
    ("random_targeting_baseline", "random assignment baseline for policy-value comparison"),
]

BUDGET_SHARES = ["5%", "10%", "20%", "30%"]


def read_csv_dicts(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        return []
    with path.open(encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def count_rows(path: Path) -> int:
    return len(read_csv_dicts(path))


def clean(value: Any) -> str:
    return "" if value is None else str(value).strip()


def first_by(rows: list[dict[str, str]], key: str) -> dict[str, dict[str, str]]:
    out: dict[str, dict[str, str]] = {}
    for row in rows:
        item_key = row.get(key, "")
        if item_key and item_key not in out:
            out[item_key] = row
    return out


def unique_outcomes(outcome_specs: list[dict[str, str]], outcome_plans: list[dict[str, str]]) -> list[dict[str, str]]:
    rows = outcome_specs or outcome_plans
    seen = set()
    out = []
    for row in rows:
        outcome = row.get("outcome", "")
        if not outcome or outcome in seen:
            continue
        seen.add(outcome)
        out.append(
            {
                "outcome": outcome,
                "outcome_family": row.get("outcome_family", ""),
            }
        )
    return out


def any_constructed_outcomes() -> bool:
    audit = read_csv_dicts(RESULT_DIR / "outcome_audit.csv")
    if any(row.get("status") == "constructed" for row in audit):
        return True
    return count_rows(DATA_DIR / "household_outcomes.csv") > 0


def climate_linked_rows_exist() -> bool:
    return count_rows(DATA_DIR / "climate_linked_household.csv") > 0


def primary_reduced_form_exists() -> bool:
    return count_rows(RESULT_DIR / "reduced_form_estimates.csv") > 0


def placebo_ready_or_passed() -> bool:
    rows = read_csv_dicts(RESULT_DIR / "placebo_readiness_audit.csv")
    return any(row.get("status") in {"complete", "ready", "placebo_ready_not_yet_interpreted"} for row in rows)


def gate_statuses(
    outcome_gate: str,
    climate_gate: str,
    ingestion_gate: str,
    eligible_final: str,
    constructed_outcomes: bool,
    linked_rows: bool,
    reduced_form_exists: bool,
    placebo_ready: bool,
) -> tuple[str, str, str, str, str, str, str]:
    metadata_incomplete = "metadata_incomplete" in outcome_gate or "metadata_incomplete" in climate_gate
    raw_unverified = "raw_unverified" in outcome_gate or "raw_unverified" in climate_gate or ingestion_gate == "waiting_for_manual_download"
    final_sample_ready = eligible_final == "1"

    if metadata_incomplete:
        predictive = "blocked_metadata_incomplete"
        reduced = "blocked_metadata_incomplete"
        causal_ml = "rejected_until_reduced_form_identification_passes"
        robustness = "blocked_until_primary_estimate_exists"
        policy = "rejected_until_validated_prediction_or_causal_effect_exists"
        action = "complete missing metadata/raw source checks before modeling"
    elif raw_unverified or not final_sample_ready:
        predictive = "metadata_plan_only_raw_unverified"
        reduced = "metadata_plan_only_raw_unverified"
        causal_ml = "rejected_until_reduced_form_identification_passes"
        robustness = "blocked_until_primary_estimate_exists"
        policy = "rejected_until_validated_prediction_or_causal_effect_exists"
        action = "complete manual raw download, raw schema inspection, harmonization, outcome construction, and climate linkage"
    elif not constructed_outcomes or not linked_rows:
        predictive = "blocked_until_constructed_outcome_and_climate_linked_data"
        reduced = "blocked_until_constructed_outcome_and_climate_linked_data"
        causal_ml = "rejected_until_reduced_form_identification_passes"
        robustness = "blocked_until_primary_estimate_exists"
        policy = "rejected_until_validated_prediction_or_causal_effect_exists"
        action = "build and audit household outcomes and climate-linked household data"
    else:
        predictive = "ready_for_nonrandom_validation_design"
        reduced = "ready_for_reduced_form_estimation_design"
        causal_ml = "rejected_until_reduced_form_identification_passes"
        robustness = "blocked_until_primary_estimate_exists"
        policy = "rejected_until_validated_prediction_or_causal_effect_exists"
        action = "run predictive and reduced-form scripts, then audit placebo/robustness results"

    if reduced_form_exists and placebo_ready:
        causal_ml = "ready_for_causal_ml_specification"
        robustness = "ready_for_full_robustness_grid"
        policy = "ready_for_policy_learning_sensitivity_design"
    elif reduced_form_exists:
        robustness = "ready_for_placebo_and_robustness_checks"

    minimum = (
        "constructed outcome with event-rate/missingness audit; climate-linked household data; "
        "verified survey timing/geography; survey design variables; non-random validation splits; "
        "future-shock placebo and alternative lag/source checks before causal language"
    )
    gap = []
    if ingestion_gate == "waiting_for_manual_download":
        gap.append("manual raw files absent")
    if "metadata_incomplete" in outcome_gate:
        gap.append("outcome metadata incomplete")
    if "raw_unverified" in outcome_gate:
        gap.append("outcome raw variables unverified")
    if "metadata_incomplete" in climate_gate:
        gap.append("climate timing/geography metadata incomplete")
    if "raw_unverified" in climate_gate:
        gap.append("climate timing/geography raw variables unverified")
    if eligible_final != "1":
        gap.append("not eligible for final sample under raw-data gate")
    if not constructed_outcomes:
        gap.append("no constructed audited outcome dataset")
    if not linked_rows:
        gap.append("no climate-linked household dataset")
    if not reduced_form_exists:
        gap.append("no reduced-form estimate")
    if not placebo_ready:
        gap.append("placebo/identification gate not ready")
    return predictive, reduced, causal_ml, robustness, policy, minimum, action, "; ".join(gap)


def build_modeling_plan() -> list[dict[str, str]]:
    outcome_plans = read_csv_dicts(TEMP_DIR / "outcome_denominator_plan.csv")
    ingestion_by_idno = first_by(read_csv_dicts(TEMP_DIR / "raw_ingestion_plan.csv"), "idno")
    climate_by_idno = first_by(read_csv_dicts(TEMP_DIR / "climate_exposure_plan.csv"), "idno")
    sample_by_idno = first_by(read_csv_dicts(RESULT_DIR / "sample_selection_gate_audit.csv"), "idno")
    constructed = any_constructed_outcomes()
    linked = climate_linked_rows_exist()
    reduced_exists = primary_reduced_form_exists()
    placebo_ready = placebo_ready_or_passed()

    rows = []
    for outcome in outcome_plans:
        idno = outcome.get("idno", "")
        ingestion = ingestion_by_idno.get(idno, {})
        climate = climate_by_idno.get(idno, {})
        sample = sample_by_idno.get(idno, {})
        statuses = gate_statuses(
            outcome.get("outcome_gate_status", ""),
            climate.get("climate_linkage_gate_status", ""),
            ingestion.get("ingestion_gate_status", ""),
            sample.get("eligible_for_final_sample", ""),
            constructed,
            linked,
            reduced_exists,
            placebo_ready,
        )
        predictive, reduced, causal_ml, robustness, policy, minimum, action, gap = statuses
        rows.append(
            {
                "quality_rank": outcome.get("quality_rank", ""),
                "country": outcome.get("country", ""),
                "survey_name": outcome.get("survey_name", ""),
                "wave": outcome.get("wave", ""),
                "idno": idno,
                "outcome": outcome.get("outcome", ""),
                "outcome_family": outcome.get("outcome_family", ""),
                "ingestion_gate_status": ingestion.get("ingestion_gate_status", "missing_raw_ingestion_plan"),
                "outcome_gate_status": outcome.get("outcome_gate_status", ""),
                "climate_linkage_gate_status": climate.get("climate_linkage_gate_status", "missing_climate_plan"),
                "sample_gate_status": sample.get("status", "missing_sample_gate"),
                "eligible_for_final_sample": sample.get("eligible_for_final_sample", "0"),
                "predictive_ml_gate_status": predictive,
                "reduced_form_gate_status": reduced,
                "causal_ml_policy_gate_status": causal_ml,
                "robustness_gate_status": robustness,
                "policy_learning_gate_status": policy,
                "minimum_required_inputs": minimum,
                "next_allowed_action": action,
                "blocking_gap": gap,
            }
        )
    return rows


def build_validation_plan() -> list[dict[str, str]]:
    outcomes = unique_outcomes(
        read_csv_dicts(RESULT_DIR / "outcome_specification_plan.csv"),
        read_csv_dicts(TEMP_DIR / "outcome_denominator_plan.csv"),
    )
    constructed = any_constructed_outcomes()
    linked = climate_linked_rows_exist()
    status = "ready_to_screen_targets_and_build_splits" if constructed and linked else "blocked_until_constructed_target_and_climate_linked_dataset"
    gap = "" if constructed and linked else "requires data/household_outcomes.* plus data/climate_linked_household.* and result/outcome_audit.csv constructed rows"
    rows = []
    for outcome in outcomes:
        for design in VALIDATION_DESIGNS:
            rows.append(
                {
                    "outcome": outcome["outcome"],
                    "outcome_family": outcome["outcome_family"],
                    "validation_design": design["validation_design"],
                    "eligible_model_families": "logistic_regression;elastic_net;random_forest;gradient_boosting;xgboost_or_lightgbm_or_catboost_if_available",
                    "required_sample_structure": design["required_sample_structure"],
                    "required_metrics": "AUROC;AUPRC;Brier;calibration_slope;calibration_intercept;decision_curve;sensitivity_specificity_at_policy_thresholds;country_or_subgroup_performance",
                    "current_status": status,
                    "blocking_gap": gap,
                    "guardrail": design["guardrail"] + "; SHAP is prediction explanation only, not causal evidence",
                }
            )
    return rows


def build_falsification_plan() -> list[dict[str, str]]:
    has_estimate = primary_reduced_form_exists()
    has_linked = climate_linked_rows_exist()
    rows = []
    for item in FALSIFICATION_TESTS:
        if has_estimate and has_linked:
            status = "ready_to_implement_or_evaluate"
            gap = "run the specified check before causal interpretation"
        else:
            status = "blocked_until_primary_estimate_and_required_inputs"
            gap = "requires constructed outcomes, climate-linked data, and a primary reduced-form estimate"
        rows.append(
            {
                "test": item["test"],
                "design_stage": item["stage"],
                "minimum_input": item["input"],
                "pass_rule": item["pass"],
                "current_status": status,
                "blocking_gap": gap,
                "interpretation_if_fails": item["fail"],
            }
        )
    return rows


def build_policy_plan() -> list[dict[str, str]]:
    has_prediction = count_rows(RESULT_DIR / "predictive_ml_metrics.csv") > 0
    has_reduced = primary_reduced_form_exists()
    placebo_ready = placebo_ready_or_passed()
    rows = []
    for rule, required_score in TARGETING_RULES:
        for budget in BUDGET_SHARES:
            if has_reduced and placebo_ready and (has_prediction or "risk" not in rule):
                status = "ready_for_policy_value_sensitivity_design"
                gap = "must specify assumed benefit sizes and validate out of sample before interpretation"
            else:
                status = "rejected_until_reduced_form_identification_and_validation_pass"
                gap = "requires credible reduced-form identification; causal ML/policy learning cannot substitute for failed identification"
            rows.append(
                {
                    "targeting_rule": rule,
                    "budget_share": budget,
                    "required_score_or_effect": required_score,
                    "validation_requirement": "compare policy value, false exclusion among poorest, rural coverage, country-specific value, and transportability under held-out country/wave splits where feasible",
                    "current_status": status,
                    "blocking_gap": gap,
                    "sensitivity_required": "evaluate assumed support benefits over multiple effect sizes; do not assume one treatment benefit",
                    "guardrail": "policy ranking is a scenario analysis unless a real intervention effect is identified",
                }
            )
    return rows


def summary_rows(
    modeling_rows: list[dict[str, str]],
    validation_rows: list[dict[str, str]],
    falsification_rows: list[dict[str, str]],
    policy_rows: list[dict[str, str]],
) -> list[dict[str, str]]:
    predictive_counts = Counter(row.get("predictive_ml_gate_status", "") for row in modeling_rows)
    reduced_counts = Counter(row.get("reduced_form_gate_status", "") for row in modeling_rows)
    causal_counts = Counter(row.get("causal_ml_policy_gate_status", "") for row in modeling_rows)
    policy_counts = Counter(row.get("policy_learning_gate_status", "") for row in modeling_rows)
    validation_counts = Counter(row.get("current_status", "") for row in validation_rows)
    falsification_counts = Counter(row.get("current_status", "") for row in falsification_rows)
    policy_rule_counts = Counter(row.get("current_status", "") for row in policy_rows)
    rows = [
        {"metric": "modeling_identification_plan_rows", "value": str(len(modeling_rows)), "interpretation": "Dataset-outcome modeling readiness rows."},
        {"metric": "modeling_validation_plan_rows", "value": str(len(validation_rows)), "interpretation": "Outcome-by-validation-design predictive ML planning rows."},
        {"metric": "falsification_placebo_plan_rows", "value": str(len(falsification_rows)), "interpretation": "Required placebo, robustness, and falsification checks to run after estimation exists."},
        {"metric": "policy_learning_plan_rows", "value": str(len(policy_rows)), "interpretation": "Targeting-rule by budget planning rows."},
        {"metric": "predictive_ready_rows", "value": str(predictive_counts.get("ready_for_nonrandom_validation_design", 0)), "interpretation": "Rows ready for predictive model validation."},
        {"metric": "reduced_form_ready_rows", "value": str(reduced_counts.get("ready_for_reduced_form_estimation_design", 0)), "interpretation": "Rows ready for reduced-form estimation."},
        {"metric": "causal_ml_ready_rows", "value": str(causal_counts.get("ready_for_causal_ml_specification", 0)), "interpretation": "Rows where causal ML may be specified after reduced-form and placebo gates."},
        {"metric": "policy_learning_ready_rows", "value": str(policy_counts.get("ready_for_policy_learning_sensitivity_design", 0)), "interpretation": "Rows where policy learning may be evaluated."},
    ]
    for label, counts in [
        ("predictive_gate_count", predictive_counts),
        ("reduced_form_gate_count", reduced_counts),
        ("causal_ml_gate_count", causal_counts),
        ("validation_plan_status_count", validation_counts),
        ("falsification_plan_status_count", falsification_counts),
        ("policy_rule_status_count", policy_rule_counts),
    ]:
        for key, count in sorted(counts.items()):
            rows.append({"metric": f"{label}_{key}", "value": str(count), "interpretation": "Modeling/identification planning status count."})
    return rows


def markdown_count_table(counter: Counter[str], label: str) -> str:
    lines = [f"| {label} | Count |", "|---|---:|"]
    for key, count in counter.most_common():
        lines.append(f"| {key or 'blank'} | {count} |")
    return "\n".join(lines)


def write_report(
    modeling_rows: list[dict[str, str]],
    validation_rows: list[dict[str, str]],
    falsification_rows: list[dict[str, str]],
    policy_rows: list[dict[str, str]],
    summaries: list[dict[str, str]],
) -> None:
    predictive_counts = Counter(row.get("predictive_ml_gate_status", "") for row in modeling_rows)
    reduced_counts = Counter(row.get("reduced_form_gate_status", "") for row in modeling_rows)
    causal_counts = Counter(row.get("causal_ml_policy_gate_status", "") for row in modeling_rows)
    validation_counts = Counter(row.get("current_status", "") for row in validation_rows)
    falsification_counts = Counter(row.get("current_status", "") for row in falsification_rows)
    policy_counts = Counter(row.get("current_status", "") for row in policy_rows)
    lines = [
        "# Modeling and Identification Plan",
        "",
        "Status: modeling, identification, robustness, and policy-learning designs are planned but not estimated. These rows are gate checks only and do not claim predictive performance, causal effects, CATEs, or policy value.",
        "",
        "## Predictive ML Gate",
        "",
        markdown_count_table(predictive_counts, "Predictive ML gate status"),
        "",
        "## Reduced-Form Gate",
        "",
        markdown_count_table(reduced_counts, "Reduced-form gate status"),
        "",
        "## Causal ML Gate",
        "",
        markdown_count_table(causal_counts, "Causal ML gate status"),
        "",
        "## Validation Plan Status",
        "",
        markdown_count_table(validation_counts, "Validation plan status"),
        "",
        "## Falsification and Placebo Plan Status",
        "",
        markdown_count_table(falsification_counts, "Falsification plan status"),
        "",
        "## Policy-Learning Plan Status",
        "",
        markdown_count_table(policy_counts, "Policy rule status"),
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
            "## Guardrails",
            "",
            "- Predictive ML requires constructed outcomes, climate-linked data, and non-random validation splits before any performance claim.",
            "- Reduced-form climate estimates require verified geography, timing, exposure variation, controls, and placebo checks before causal language.",
            "- Causal ML and policy learning are rejected until the reduced-form identification gate passes; they cannot compensate for weak identification.",
            "- Policy simulations require sensitivity over assumed support benefit sizes and must report false exclusion and transportability diagnostics.",
            "",
            "## Machine-Readable Outputs",
            "",
            "- `temp/modeling_identification_plan.csv`",
            "- `result/modeling_validation_plan.csv`",
            "- `result/falsification_placebo_plan.csv`",
            "- `result/policy_learning_plan.csv`",
            "- `result/modeling_identification_plan_summary.csv`",
        ]
    )
    REPORT_PATH.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    ensure_dirs()
    modeling_rows = build_modeling_plan()
    validation_rows = build_validation_plan()
    falsification_rows = build_falsification_plan()
    policy_rows = build_policy_plan()
    summaries = summary_rows(modeling_rows, validation_rows, falsification_rows, policy_rows)
    write_csv(PLAN_PATH, modeling_rows, PLAN_COLUMNS)
    write_csv(VALIDATION_PATH, validation_rows, VALIDATION_COLUMNS)
    write_csv(FALSIFICATION_PATH, falsification_rows, FALSIFICATION_COLUMNS)
    write_csv(POLICY_PATH, policy_rows, POLICY_COLUMNS)
    write_csv(SUMMARY_PATH, summaries, SUMMARY_COLUMNS)
    write_report(modeling_rows, validation_rows, falsification_rows, policy_rows, summaries)
    predictive_ready = sum(1 for row in modeling_rows if row.get("predictive_ml_gate_status") == "ready_for_nonrandom_validation_design")
    reduced_ready = sum(1 for row in modeling_rows if row.get("reduced_form_gate_status") == "ready_for_reduced_form_estimation_design")
    append_log(
        TEMP_DIR / "audit_log.md",
        f"Modeling identification plan rows={len(modeling_rows)} validation_rows={len(validation_rows)} falsification_rows={len(falsification_rows)} policy_rows={len(policy_rows)} predictive_ready={predictive_ready} reduced_form_ready={reduced_ready}.",
    )
    print(
        f"Modeling identification plan rows={len(modeling_rows)} validation_rows={len(validation_rows)} falsification_rows={len(falsification_rows)} policy_rows={len(policy_rows)} predictive_ready={predictive_ready} reduced_form_ready={reduced_ready}."
    )


if __name__ == "__main__":
    main()
