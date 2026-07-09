from __future__ import annotations

import csv
from collections import Counter, defaultdict
from pathlib import Path

from common import DATA_DIR, REPORT_DIR, RESULT_DIR, TEMP_DIR, append_log, ensure_dirs, write_csv


BUNDLES_PATH = TEMP_DIR / "minimum_viable_download_bundles.csv"
PRIORITY_PATH = TEMP_DIR / "metadata_quality_download_priority.csv"
QUALITY_PATH = RESULT_DIR / "metadata_candidate_quality_audit.csv"
SAMPLE_PATH = RESULT_DIR / "sample_selection_gate_audit.csv"
RAW_INTAKE_PATH = TEMP_DIR / "raw_download_intake_manifest.csv"
RAW_EXPECTED_PATH = TEMP_DIR / "raw_download_expected_files.csv"
RAW_FILE_PATH = TEMP_DIR / "raw_schema_inventory" / "raw_file_inventory.csv"
RAW_VARIABLE_PATH = TEMP_DIR / "raw_schema_inventory" / "raw_variable_catalog.csv"
HARMONIZATION_PATH = RESULT_DIR / "harmonization_readiness_matrix.csv"
SDG382_PATH = RESULT_DIR / "sdg382_denominator_country_wave_readiness.csv"
CLIMATE_PATH = RESULT_DIR / "climate_linkage_readiness.csv"
OUTCOME_PATH = TEMP_DIR / "outcome_denominator_plan.csv"
MODELING_PATH = TEMP_DIR / "modeling_identification_plan.csv"
MECHANISM_PATH = RESULT_DIR / "mechanism_readiness_matrix.csv"
PREDICTIVE_METRICS_PATH = RESULT_DIR / "predictive_ml_metrics.csv"
REDUCED_FORM_PATH = RESULT_DIR / "reduced_form_estimates.csv"
ROBUSTNESS_PATH = RESULT_DIR / "robustness_results.csv"

DASHBOARD_PATH = RESULT_DIR / "empirical_readiness_dashboard.csv"
NOGO_PATH = RESULT_DIR / "empirical_no_go_threshold_status.csv"
SUMMARY_PATH = RESULT_DIR / "empirical_readiness_dashboard_summary.csv"
REPORT_PATH = REPORT_DIR / "empirical_readiness_dashboard.md"

DASHBOARD_COLUMNS = [
    "bundle_rank",
    "country",
    "survey_name",
    "wave",
    "idno",
    "included_acquisition_sets",
    "official_url",
    "local_target_folder",
    "metadata_quality_tier",
    "sample_gate_status",
    "eligible_for_final_sample",
    "eligible_for_access_secondary_sample",
    "raw_intake_status",
    "file_count",
    "raw_tabular_file_count",
    "archive_file_count",
    "expected_module_rows",
    "expected_core_module_rows",
    "expected_files_not_present",
    "expected_exact_matches",
    "expected_stem_matches",
    "raw_file_inventory_rows",
    "raw_variable_catalog_rows",
    "high_confidence_rows",
    "moderate_confidence_rows",
    "likely_false_positive_rows",
    "harmonization_status",
    "harmonization_ready_required_rows",
    "harmonization_blocked_required_rows",
    "sdg382_status",
    "sdg382_blocked_component_rows",
    "climate_linkage_status",
    "climate_blocked_requirement_rows",
    "outcome_ready_rows",
    "outcome_metadata_ready_rows",
    "outcome_metadata_incomplete_rows",
    "predictive_ready_rows",
    "reduced_form_ready_rows",
    "causal_ml_ready_rows",
    "policy_learning_ready_rows",
    "mechanism_ready_rows",
    "mechanism_blocked_rows",
    "current_stage",
    "analysis_claim_status",
    "next_blocking_action",
    "blocking_gaps",
    "post_download_commands",
]

NOGO_COLUMNS = [
    "rule_id",
    "go_no_go_rule",
    "threshold",
    "current_value",
    "status",
    "evidence",
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


def safe_int(value: str, default: int = 0) -> int:
    try:
        return int(float(value))
    except (TypeError, ValueError):
        return default


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


def by_idno(rows: list[dict[str, str]], id_field: str = "idno") -> dict[str, dict[str, str]]:
    out = {}
    for row in rows:
        idno = row.get(id_field, "")
        if idno and idno not in out:
            out[idno] = row
    return out


def grouped(rows: list[dict[str, str]], field: str = "idno") -> dict[str, list[dict[str, str]]]:
    out: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in rows:
        out[row.get(field, "")].append(row)
    return out


def count_status(rows: list[dict[str, str]], field: str, value: str) -> int:
    return sum(1 for row in rows if row.get(field) == value)


def infer_idno_from_path(value: str, known_idnos: set[str]) -> str:
    low = (value or "").lower().replace("\\", "/")
    for idno in sorted(known_idnos, key=len, reverse=True):
        if idno and idno.lower() in low:
            return idno
    return ""


def raw_inventory_counts(raw_files: list[dict[str, str]], raw_variables: list[dict[str, str]], known_idnos: set[str]) -> tuple[dict[str, int], dict[str, int]]:
    file_counts: dict[str, int] = defaultdict(int)
    variable_counts: dict[str, int] = defaultdict(int)
    for row in raw_files:
        idno = row.get("idno", "") or infer_idno_from_path(" ".join(row.values()), known_idnos)
        if idno:
            file_counts[idno] += 1
    for row in raw_variables:
        idno = row.get("idno", "") or infer_idno_from_path(" ".join(row.values()), known_idnos)
        if idno:
            variable_counts[idno] += 1
    return file_counts, variable_counts


def outcome_counts(rows: list[dict[str, str]]) -> tuple[int, int, int]:
    return (
        count_status(rows, "outcome_gate_status", "ready_for_harmonized_outcome_construction"),
        count_status(rows, "outcome_gate_status", "metadata_ready_raw_unverified"),
        count_status(rows, "outcome_gate_status", "metadata_incomplete_for_outcome"),
    )


def modeling_counts(rows: list[dict[str, str]]) -> tuple[int, int, int, int]:
    return (
        count_status(rows, "predictive_ml_gate_status", "ready_for_nonrandom_validation_design"),
        count_status(rows, "reduced_form_gate_status", "ready_for_reduced_form_estimation_design"),
        count_status(rows, "causal_ml_policy_gate_status", "ready_for_causal_ml_specification"),
        count_status(rows, "policy_learning_gate_status", "ready_for_policy_learning_sensitivity_design"),
    )


def current_stage(row: dict[str, str]) -> tuple[str, str, str, str]:
    gaps: list[str] = []
    if safe_int(row["raw_tabular_file_count"]) == 0 and safe_int(row["archive_file_count"]) == 0:
        gaps.append("raw_files_absent")
        return (
            "manual_raw_download_required",
            "metadata_protocol_only_no_empirical_claims",
            "place original raw archives/files in the target folder, then run raw-download and schema inspection",
            compact_join(gaps),
        )
    if safe_int(row["raw_file_inventory_rows"]) == 0 or safe_int(row["raw_variable_catalog_rows"]) == 0:
        gaps.append("raw_schema_inventory_missing")
        return (
            "raw_schema_inspection_required",
            "metadata_protocol_only_no_empirical_claims",
            "run script/03_inspect_raw_schemas.py and verify row/column/label extraction",
            compact_join(gaps),
        )
    if row["harmonization_status"] != "ready_for_verified_recipe_assembly":
        gaps.append("verified_harmonization_recipe_missing")
        return (
            "harmonization_value_audit_required",
            "raw_schema_claims_only_no_analysis_dataset_claims",
            "complete harmonization value/unit/recall/key audits and assemble verified recipe candidates",
            compact_join(gaps),
        )
    if safe_int(row["outcome_ready_rows"]) == 0:
        gaps.append("constructed_outcomes_missing")
        return (
            "outcome_construction_required",
            "harmonization_claims_only_no_outcome_claims",
            "construct and audit financial protection/access outcomes with event rates and missingness",
            compact_join(gaps),
        )
    if row["climate_linkage_status"] != "ready_for_climate_linkage_value_audit":
        gaps.append("climate_linkage_value_audit_missing")
        return (
            "climate_linkage_required",
            "outcome_claims_only_no_climate_claims",
            "verify timing/geography and construct climate exposure diagnostics",
            compact_join(gaps),
        )
    if safe_int(row["reduced_form_ready_rows"]) == 0:
        gaps.append("reduced_form_design_not_ready")
        return (
            "modeling_identification_gate_required",
            "descriptive_or_prediction_only_no_causal_claims",
            "pass modeling, placebo, timing, geography, and non-random validation gates",
            compact_join(gaps),
        )
    return (
        "ready_for_empirical_model_execution",
        "empirical_analysis_design_ready_but_estimates_still_must_be_run_and_audited",
        "run descriptive, predictive, reduced-form, robustness, and policy scripts in order",
        "",
    )


def build_dashboard() -> tuple[list[dict[str, str]], dict[str, list[dict[str, str]]]]:
    bundles = read_csv_dicts(BUNDLES_PATH)
    priority_by_id = by_idno(read_csv_dicts(PRIORITY_PATH))
    quality_by_id = by_idno(read_csv_dicts(QUALITY_PATH))
    sample_by_id = by_idno(read_csv_dicts(SAMPLE_PATH))
    intake_by_id = by_idno(read_csv_dicts(RAW_INTAKE_PATH), "dataset_idno")
    expected_by_id = grouped(read_csv_dicts(RAW_EXPECTED_PATH), "dataset_idno")
    raw_files = read_csv_dicts(RAW_FILE_PATH)
    raw_variables = read_csv_dicts(RAW_VARIABLE_PATH)
    known_idnos = {row.get("idno", "") for row in bundles if row.get("idno", "")}
    raw_file_counts, raw_variable_counts = raw_inventory_counts(raw_files, raw_variables, known_idnos)
    harmonization_by_id = by_idno(read_csv_dicts(HARMONIZATION_PATH))
    sdg_by_id = by_idno(read_csv_dicts(SDG382_PATH))
    climate_by_id = by_idno(read_csv_dicts(CLIMATE_PATH))
    outcome_by_id = grouped(read_csv_dicts(OUTCOME_PATH))
    modeling_by_id = grouped(read_csv_dicts(MODELING_PATH))
    mechanism_by_id = grouped(read_csv_dicts(MECHANISM_PATH))

    dashboard = []
    for bundle in bundles:
        idno = bundle.get("idno", "")
        priority = priority_by_id.get(idno, {})
        quality = quality_by_id.get(idno, {})
        sample = sample_by_id.get(idno, {})
        intake = intake_by_id.get(idno, {})
        expected_rows = expected_by_id.get(idno, [])
        harmonization = harmonization_by_id.get(idno, {})
        sdg = sdg_by_id.get(idno, {})
        climate = climate_by_id.get(idno, {})
        outcome_ready, outcome_meta, outcome_incomplete = outcome_counts(outcome_by_id.get(idno, []))
        predictive_ready, reduced_ready, causal_ready, policy_ready = modeling_counts(modeling_by_id.get(idno, []))
        mechanisms = mechanism_by_id.get(idno, [])
        mechanism_ready = count_status(mechanisms, "readiness_status", "ready_for_mechanism_analysis_design")
        mechanism_blocked = sum(1 for row in mechanisms if row.get("readiness_status") != "ready_for_mechanism_analysis_design")
        expected_not_present = count_status(expected_rows, "expected_file_status", "not_present")

        row = {
            "bundle_rank": bundle.get("bundle_rank", ""),
            "country": bundle.get("country", ""),
            "survey_name": bundle.get("survey_name", ""),
            "wave": bundle.get("wave", ""),
            "idno": idno,
            "included_acquisition_sets": bundle.get("included_acquisition_sets", ""),
            "official_url": bundle.get("official_url", ""),
            "local_target_folder": bundle.get("local_target_folder", ""),
            "metadata_quality_tier": priority.get("quality_download_priority_tier", quality.get("quality_download_priority_tier", "")),
            "sample_gate_status": sample.get("status", priority.get("sample_gate_status", "")),
            "eligible_for_final_sample": sample.get("eligible_for_final_sample", "0"),
            "eligible_for_access_secondary_sample": sample.get("eligible_for_access_secondary_sample", "0"),
            "raw_intake_status": intake.get("intake_status", bundle.get("raw_intake_status", "")),
            "file_count": intake.get("file_count", "0"),
            "raw_tabular_file_count": intake.get("raw_tabular_file_count", "0"),
            "archive_file_count": intake.get("archive_file_count", "0"),
            "expected_module_rows": intake.get("expected_module_rows", str(len(expected_rows))),
            "expected_core_module_rows": intake.get("expected_core_module_rows", ""),
            "expected_files_not_present": str(expected_not_present),
            "expected_exact_matches": intake.get("expected_exact_matches", "0"),
            "expected_stem_matches": intake.get("expected_stem_matches", "0"),
            "raw_file_inventory_rows": str(raw_file_counts.get(idno, 0)),
            "raw_variable_catalog_rows": str(raw_variable_counts.get(idno, 0)),
            "high_confidence_rows": priority.get("high_confidence_rows", quality.get("high_confidence_rows", "")),
            "moderate_confidence_rows": priority.get("moderate_confidence_rows", quality.get("moderate_confidence_rows", "")),
            "likely_false_positive_rows": priority.get("likely_false_positive_rows", quality.get("likely_false_positive_rows", "")),
            "harmonization_status": harmonization.get("readiness_status", "missing_harmonization_readiness"),
            "harmonization_ready_required_rows": harmonization.get("recipe_ready_required_rows", "0"),
            "harmonization_blocked_required_rows": harmonization.get("blocked_required_rows", "0"),
            "sdg382_status": sdg.get("readiness_status", "missing_sdg382_readiness"),
            "sdg382_blocked_component_rows": sdg.get("blocked_component_rows", "0"),
            "climate_linkage_status": climate.get("readiness_status", "missing_climate_readiness"),
            "climate_blocked_requirement_rows": climate.get("blocked_requirement_rows", "0"),
            "outcome_ready_rows": str(outcome_ready),
            "outcome_metadata_ready_rows": str(outcome_meta),
            "outcome_metadata_incomplete_rows": str(outcome_incomplete),
            "predictive_ready_rows": str(predictive_ready),
            "reduced_form_ready_rows": str(reduced_ready),
            "causal_ml_ready_rows": str(causal_ready),
            "policy_learning_ready_rows": str(policy_ready),
            "mechanism_ready_rows": str(mechanism_ready),
            "mechanism_blocked_rows": str(mechanism_blocked),
            "current_stage": "",
            "analysis_claim_status": "",
            "next_blocking_action": "",
            "blocking_gaps": "",
            "post_download_commands": bundle.get("post_download_commands", ""),
        }
        stage, claim_status, action, gaps = current_stage(row)
        row["current_stage"] = stage
        row["analysis_claim_status"] = claim_status
        row["next_blocking_action"] = action
        row["blocking_gaps"] = gaps
        dashboard.append(row)
    dashboard.sort(key=lambda row: safe_int(row.get("bundle_rank", ""), 9999))
    supporting = {
        "bundles": bundles,
        "sample": list(sample_by_id.values()),
        "outcomes": sum(outcome_by_id.values(), []),
        "modeling": sum(modeling_by_id.values(), []),
        "mechanism": sum(mechanism_by_id.values(), []),
        "harmonized_household": read_csv_dicts(DATA_DIR / "harmonized_household.csv"),
        "household_outcomes": read_csv_dicts(DATA_DIR / "household_outcomes.csv"),
        "climate_linked_household": read_csv_dicts(DATA_DIR / "climate_linked_household.csv"),
        "outcome_audit": read_csv_dicts(RESULT_DIR / "outcome_audit.csv"),
        "predictive_metrics": read_csv_dicts(PREDICTIVE_METRICS_PATH),
        "reduced_form": read_csv_dicts(REDUCED_FORM_PATH),
        "robustness": read_csv_dicts(ROBUSTNESS_PATH),
    }
    return dashboard, supporting


def build_no_go_rows(dashboard: list[dict[str, str]], supporting: dict[str, list[dict[str, str]]]) -> list[dict[str, str]]:
    final_ready_countries = {row["country"] for row in dashboard if row.get("eligible_for_final_sample") == "1"}
    double_failure_ready = [
        row
        for row in supporting["outcomes"]
        if row.get("outcome") == "uhc_double_failure" and row.get("outcome_gate_status") == "ready_for_harmonized_outcome_construction"
    ]
    climate_ready = [row for row in dashboard if row.get("climate_linkage_status") == "ready_for_climate_linkage_value_audit"]
    event_rate_ready = 0
    predictive_metric_rows = len(supporting["predictive_metrics"])
    reduced_form_rows = len(supporting["reduced_form"])
    robustness_attempted = sum(1 for row in supporting["robustness"] if row.get("status", "").startswith(("complete", "attempted")))
    causal_policy_ready = sum(safe_int(row.get("causal_ml_ready_rows", "0")) for row in dashboard)
    policy_ready = sum(safe_int(row.get("policy_learning_ready_rows", "0")) for row in dashboard)
    harmonized_rows = len(supporting["harmonized_household"])
    household_outcome_rows = len(supporting["household_outcomes"])
    limited_che_rows = sum(1 for row in supporting["household_outcomes"] if row.get("outcome_scope") == "alb2002_financial_protection_che10_che25_limited_no_sdg382_no_access")
    limited_climate_linked_rows = sum(1 for row in supporting["climate_linked_household"] if row.get("data_use_limit") == "climate_linked_che_diagnostic_only_not_for_promoted_descriptive_ml_causal_or_policy_analysis")
    constructed_outcome_rows = sum(1 for row in supporting["outcome_audit"] if row.get("status") == "constructed")

    def status(ok: bool, blocked: bool = True) -> str:
        if ok:
            return "pass"
        return "blocked_raw_microdata" if blocked else "fail"

    return [
        {
            "rule_id": "main_financial_protection_minimum_countries",
            "go_no_go_rule": "If fewer than 6 countries have consumption, OOP health expenditure, usable geography, and survey timing, do not proceed with the main multi-country financial-protection paper.",
            "threshold": ">=6 raw-verified countries",
            "current_value": str(len(final_ready_countries)),
            "status": status(len(final_ready_countries) >= 6),
            "evidence": f"eligible_for_final_sample countries={len(final_ready_countries)}",
            "next_action": "complete raw downloads and verify consumption, OOP, geography, timing, and weights",
        },
        {
            "rule_id": "double_failure_minimum_country_waves",
            "go_no_go_rule": "If fewer than 10 country-waves support both financial hardship and forgone care, keep UHC double failure secondary.",
            "threshold": ">=10 raw-verified country-waves",
            "current_value": str(len(double_failure_ready)),
            "status": status(len(double_failure_ready) >= 10),
            "evidence": f"uhc_double_failure ready outcome rows={len(double_failure_ready)}",
            "next_action": "verify financial and access outcome concepts in raw data before promoting the composite outcome",
        },
        {
            "rule_id": "climate_geography_precision",
            "go_no_go_rule": "If geolocation is too weak for most countries, use admin-level climate aggregation and lower causal claims.",
            "threshold": "verified timing/geography for most analytical country-waves",
            "current_value": str(len(climate_ready)),
            "status": status(len(climate_ready) > 0),
            "evidence": f"climate linkage ready rows={len(climate_ready)}",
            "next_action": "inspect raw timing/geography variables and classify GPS/admin linkage quality",
        },
        {
            "rule_id": "event_rate_minimum",
            "go_no_go_rule": "If event rates are below 3%, expand outcomes or countries; do not force rare-event ML.",
            "threshold": "event rate >=3% after outcome construction",
            "current_value": str(household_outcome_rows),
            "status": "blocked_raw_microdata",
            "evidence": f"limited CHE outcome rows={limited_che_rows}; constructed outcome-audit rows={constructed_outcome_rows}; promoted descriptive prevalence rows={event_rate_ready}",
            "next_action": "run promoted descriptive diagnostics after climate-linked data before treating event-rate checks as model-ready",
        },
        {
            "rule_id": "transportable_prediction",
            "go_no_go_rule": "If leave-country-out predictive performance is poor, do not claim transportable targeting.",
            "threshold": "validated non-random predictive metrics",
            "current_value": str(predictive_metric_rows),
            "status": status(predictive_metric_rows > 0),
            "evidence": f"predictive metric rows={predictive_metric_rows}",
            "next_action": "run predictive ML only after audited outcomes and climate-linked data exist",
        },
        {
            "rule_id": "climate_lead_placebo",
            "go_no_go_rule": "If climate lead placebo predicts outcomes, treat causal design as weak.",
            "threshold": "future-shock placebo attempted and passes",
            "current_value": str(reduced_form_rows),
            "status": status(reduced_form_rows > 0 and robustness_attempted > 0),
            "evidence": f"reduced-form rows={reduced_form_rows}; robustness attempted rows={robustness_attempted}",
            "next_action": "estimate main reduced-form model, then run future climate lead placebo",
        },
        {
            "rule_id": "causal_ml_policy_value",
            "go_no_go_rule": "If CATE/policy learning does not beat simple targeting rules out of sample, report null targeting value honestly.",
            "threshold": "causal ML and policy learning ready after credible reduced-form design",
            "current_value": str(causal_policy_ready + policy_ready),
            "status": status(causal_policy_ready > 0 and policy_ready > 0),
            "evidence": f"causal_ml_ready_rows={causal_policy_ready}; policy_learning_ready_rows={policy_ready}",
            "next_action": "do not run causal ML or policy learning until identification and validation gates pass",
        },
        {
            "rule_id": "descriptive_fallback",
            "go_no_go_rule": "If only descriptive evidence survives, write a descriptive data paper and do not claim causal effects.",
            "threshold": "descriptive diagnostics attempted after data construction",
            "current_value": str(harmonized_rows),
            "status": "blocked_raw_microdata",
            "evidence": f"limited harmonized core rows={harmonized_rows}; limited CHE outcome rows={limited_che_rows}; limited climate-linked diagnostic rows={limited_climate_linked_rows}; promoted descriptive result rows={event_rate_ready}",
            "next_action": "resolve climate-linkage gates, then run descriptive diagnostics before deciding manuscript scope",
        },
    ]


def build_summary(dashboard: list[dict[str, str]], no_go_rows: list[dict[str, str]]) -> list[dict[str, str]]:
    stage_counts = Counter(row.get("current_stage", "") for row in dashboard)
    claim_counts = Counter(row.get("analysis_claim_status", "") for row in dashboard)
    country_count = len({row.get("country", "") for row in dashboard if row.get("country", "")})
    ready_counts = {
        "limited_harmonized_household_rows": row_count(DATA_DIR / "harmonized_household.csv"),
        "limited_household_outcome_rows": row_count(DATA_DIR / "household_outcomes.csv"),
        "limited_climate_exposure_rows": row_count(DATA_DIR / "climate_exposures_nasa_power.csv"),
        "limited_climate_linked_rows": row_count(DATA_DIR / "climate_linked_household.csv"),
        "harmonization_ready_country_waves": sum(1 for row in dashboard if row.get("harmonization_status") == "ready_for_verified_recipe_assembly"),
        "sdg382_ready_country_waves": sum(1 for row in dashboard if row.get("sdg382_status") == "ready_for_household_denominator_value_audit"),
        "climate_ready_country_waves": sum(1 for row in dashboard if row.get("climate_linkage_status") == "ready_for_climate_linkage_value_audit"),
        "outcome_ready_country_waves": sum(1 for row in dashboard if safe_int(row.get("outcome_ready_rows", "0")) > 0),
        "reduced_form_ready_country_waves": sum(1 for row in dashboard if safe_int(row.get("reduced_form_ready_rows", "0")) > 0),
        "mechanism_ready_country_waves": sum(1 for row in dashboard if safe_int(row.get("mechanism_ready_rows", "0")) > 0),
    }
    rows = [
        {"metric": "dashboard_rows", "value": str(len(dashboard)), "interpretation": "Priority acquisition bundle rows in the dashboard."},
        {"metric": "country_count", "value": str(country_count), "interpretation": "Unique countries in priority acquisition bundles."},
        {"metric": "no_go_rule_rows", "value": str(len(no_go_rows)), "interpretation": "Pre-specified go/no-go threshold rows."},
        {"metric": "no_go_pass_rows", "value": str(sum(1 for row in no_go_rows if row.get("status") == "pass")), "interpretation": "Go/no-go rules currently passing."},
        {"metric": "no_go_blocked_rows", "value": str(sum(1 for row in no_go_rows if row.get("status") != "pass")), "interpretation": "Go/no-go rules blocked or failing."},
    ]
    for key, value in ready_counts.items():
        rows.append({"metric": key, "value": str(value), "interpretation": "Country-wave rows ready at this stage."})
    for key, count in sorted(stage_counts.items()):
        rows.append({"metric": f"current_stage_{key}", "value": str(count), "interpretation": "Dashboard current-stage count."})
    for key, count in sorted(claim_counts.items()):
        rows.append({"metric": f"claim_status_{key}", "value": str(count), "interpretation": "Allowed claim status count."})
    return rows


def markdown_count_table(counter: Counter[str], label: str) -> str:
    lines = [f"| {label} | Count |", "|---|---:|"]
    for key, count in counter.most_common():
        lines.append(f"| {key or 'blank'} | {count} |")
    return "\n".join(lines)


def markdown_rows(rows: list[dict[str, str]], columns: list[str], limit: int = 20) -> str:
    lines = ["| " + " | ".join(columns) + " |", "|" + "|".join("---" for _ in columns) + "|"]
    for row in rows[:limit]:
        values = []
        for column in columns:
            value = (row.get(column, "") or "").replace("|", "/")
            if len(value) > 110:
                value = value[:107] + "..."
            values.append(value)
        lines.append("| " + " | ".join(values) + " |")
    return "\n".join(lines)


def write_report(dashboard: list[dict[str, str]], no_go_rows: list[dict[str, str]], summary: list[dict[str, str]]) -> None:
    stage_counts = Counter(row.get("current_stage", "") for row in dashboard)
    claim_counts = Counter(row.get("analysis_claim_status", "") for row in dashboard)
    no_go_counts = Counter(row.get("status", "") for row in no_go_rows)
    summary_table = "\n".join(f"| {row['metric']} | {row['value']} | {row['interpretation']} |" for row in summary)
    REPORT_PATH.write_text(
        f"""# Empirical Readiness Dashboard

Status: consolidated evidence map only. No country-wave is currently analysis-ready because final outcomes and analysis-ready climate-linked data are absent. Limited ALB_2002 harmonized household, CHE-only outcome, fallback climate exposure, and linked diagnostic files may exist for inspection only and do not unlock descriptive, model, causal, or policy claims.

## Purpose

This dashboard joins acquisition, sample-selection, harmonization, SDG 3.8.2 denominator, climate linkage, outcome, modeling, mechanism, and go/no-go gates into one country-wave table. It is meant to guide manual raw-data acquisition and prevent premature country selection or empirical claims.

## Counts

| Metric | Value | Interpretation |
|---|---:|---|
{summary_table}

## Current Stage

{markdown_count_table(stage_counts, 'Current stage') if dashboard else 'No dashboard rows exist yet.'}

## Allowed Claim Status

{markdown_count_table(claim_counts, 'Allowed claim status') if dashboard else 'No dashboard rows exist yet.'}

## Go/No-Go Status

{markdown_count_table(no_go_counts, 'Go/no-go status') if no_go_rows else 'No go/no-go rows exist yet.'}

{markdown_rows(no_go_rows, ['rule_id', 'threshold', 'current_value', 'status', 'next_action'], 20) if no_go_rows else ''}

## Priority Bundle Snapshot

{markdown_rows(dashboard, ['bundle_rank', 'country', 'wave', 'idno', 'current_stage', 'analysis_claim_status', 'next_blocking_action'], 20) if dashboard else ''}

## Outputs

- `result/empirical_readiness_dashboard.csv`
- `result/empirical_no_go_threshold_status.csv`
- `result/empirical_readiness_dashboard_summary.csv`

## Guardrails

- This dashboard does not select final countries.
- This dashboard does not construct `data/` outputs.
- Limited harmonized household and fallback climate exposure files do not count as final outcome, climate-linked, model-ready, or policy-ready data.
- Dashboard rows remain blocked for empirical claims until outcome, climate, and model gates pass.
""",
        encoding="utf-8",
    )


def main() -> None:
    ensure_dirs()
    dashboard, supporting = build_dashboard()
    no_go_rows = build_no_go_rows(dashboard, supporting)
    summary = build_summary(dashboard, no_go_rows)

    write_csv(DASHBOARD_PATH, dashboard, DASHBOARD_COLUMNS)
    write_csv(NOGO_PATH, no_go_rows, NOGO_COLUMNS)
    write_csv(SUMMARY_PATH, summary, SUMMARY_COLUMNS)
    write_report(dashboard, no_go_rows, summary)
    append_log(TEMP_DIR / "audit_log.md", f"Empirical readiness dashboard rows={len(dashboard)} no_go_rows={len(no_go_rows)}.")
    print(f"Empirical readiness dashboard rows={len(dashboard)} no_go_rows={len(no_go_rows)}.")


if __name__ == "__main__":
    main()
