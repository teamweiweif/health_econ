from __future__ import annotations

import csv
from pathlib import Path
from typing import Any

from common import REPORT_DIR, RESULT_DIR, TEMP_DIR, append_log, ensure_dirs, write_csv


IDNO = "ALB_2005_LSMS_v01_M"
COUNTRY = "Albania"
SURVEY_NAME = "Living Standards Measurement Survey 2005"
WAVE = "2005"

CORE_SUMMARY_PATH = RESULT_DIR / "alb2005_household_core_candidate_summary.csv"
VALUE_DECISION_SUMMARY_PATH = RESULT_DIR / "alb2005_harmonization_value_decision_summary.csv"
UNIT_PERIOD_SUMMARY_PATH = RESULT_DIR / "alb2005_consumption_oop_unit_period_summary.csv"
OOP_POLICY_SUMMARY_PATH = RESULT_DIR / "alb2005_oop_aggregation_policy_summary.csv"
OUTCOME_SEMANTICS_SUMMARY_PATH = RESULT_DIR / "alb2005_outcome_semantics_raw_value_summary.csv"
TIMING_GEO_SUMMARY_PATH = RESULT_DIR / "alb2005_timing_geography_exhaustive_summary.csv"
COMPONENT_SOURCE_SUMMARY_PATH = RESULT_DIR / "alb2005_consumption_component_source_search_summary.csv"
REQUIRED_VALUE_KEY_SUMMARY_PATH = RESULT_DIR / "alb2005_required_value_key_summary.csv"
HEALTH_QUESTIONNAIRE_SUMMARY_PATH = RESULT_DIR / "alb2005_health_questionnaire_semantics_summary.csv"
SKIP_MISSING_SUMMARY_PATH = RESULT_DIR / "alb2005_skip_missing_semantics_summary.csv"

ACTION_QUEUE_PATH = TEMP_DIR / "alb2005_minimum_recipe_promotion_action_queue.csv"
GATE_CHECKLIST_PATH = TEMP_DIR / "alb2005_minimum_recipe_promotion_gate_checklist.csv"
SUMMARY_PATH = RESULT_DIR / "alb2005_minimum_recipe_promotion_summary.csv"
REPORT_PATH = REPORT_DIR / "alb2005_minimum_recipe_promotion_packet.md"

DECISION = "blocked_alb2005_minimum_recipe_not_ready_for_promotion"

ACTION_COLUMNS = [
    "action_rank",
    "gate_id",
    "blocker_domain",
    "current_evidence",
    "blocking_status",
    "required_resolution",
    "acceptance_evidence",
    "post_resolution_commands",
]
GATE_COLUMNS = [
    "gate_id",
    "gate_label",
    "required_for",
    "current_status",
    "current_evidence",
    "minimum_evidence_to_pass",
    "promotion_effect_if_passed",
    "fail_closed_stop_rule",
]
SUMMARY_COLUMNS = ["metric", "value", "interpretation"]


def read_csv_dicts(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        return []
    with path.open(encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def metric_value(rows: list[dict[str, str]], metric: str, default: str = "0") -> str:
    return next((row.get("value", default) for row in rows if row.get("metric") == metric), default)


def int_value(value: Any) -> int:
    try:
        return int(float(str(value).strip()))
    except (TypeError, ValueError):
        return 0


def action_row(rank: int, gate_id: str, blocker_domain: str, current_evidence: str, blocking_status: str, required_resolution: str, acceptance_evidence: str) -> dict[str, str]:
    return {
        "action_rank": str(rank),
        "gate_id": gate_id,
        "blocker_domain": blocker_domain,
        "current_evidence": current_evidence,
        "blocking_status": blocking_status,
        "required_resolution": required_resolution,
        "acceptance_evidence": acceptance_evidence,
        "post_resolution_commands": "python script/47_audit_alb2005_household_core_merge.py; python script/68_build_alb2005_harmonization_value_decision_audit.py; python script/83_build_alb2005_minimum_recipe_promotion_packet.py; python script/84_audit_alb2005_public_fieldwork_geo_metadata.py; python script/85_audit_alb2005_diary_timing_candidates.py; python script/86_audit_alb2005_extracted_module_coverage.py; python script/87_build_albania_first_analysis_promotion_gate.py; python script/115_build_alb2005_fallback_blocker_resolution_matrix.py; python script/13_write_reports.py; python script/14_validate_workspace.py",
    }


def gate_row(gate_id: str, label: str, required_for: str, status: str, evidence: str, minimum: str, effect: str, stop_rule: str) -> dict[str, str]:
    return {
        "gate_id": gate_id,
        "gate_label": label,
        "required_for": required_for,
        "current_status": status,
        "current_evidence": evidence,
        "minimum_evidence_to_pass": minimum,
        "promotion_effect_if_passed": effect,
        "fail_closed_stop_rule": stop_rule,
    }


def build_packet() -> tuple[list[dict[str, str]], list[dict[str, str]], list[dict[str, str]]]:
    core = read_csv_dicts(CORE_SUMMARY_PATH)
    value = read_csv_dicts(VALUE_DECISION_SUMMARY_PATH)
    unit = read_csv_dicts(UNIT_PERIOD_SUMMARY_PATH)
    oop = read_csv_dicts(OOP_POLICY_SUMMARY_PATH)
    semantics = read_csv_dicts(OUTCOME_SEMANTICS_SUMMARY_PATH)
    timing = read_csv_dicts(TIMING_GEO_SUMMARY_PATH)
    components = read_csv_dicts(COMPONENT_SOURCE_SUMMARY_PATH)
    required_value = read_csv_dicts(REQUIRED_VALUE_KEY_SUMMARY_PATH)
    health_questionnaire = read_csv_dicts(HEALTH_QUESTIONNAIRE_SUMMARY_PATH)
    skip_missing = read_csv_dicts(SKIP_MISSING_SUMMARY_PATH)

    candidate_rows = metric_value(core, "alb2005_household_core_candidate_rows")
    total_consumption_rows = metric_value(core, "alb2005_households_with_total_consumption")
    weight_rows = metric_value(core, "alb2005_households_with_household_weight")
    oop_4w_positive = metric_value(core, "alb2005_households_with_oop_4w_positive")
    oop_12m_positive = metric_value(core, "alb2005_households_with_oop_12m_positive")
    survey_month_rows = metric_value(core, "alb2005_households_with_survey_month")
    partial_district_code_rows = metric_value(core, "alb2005_households_with_partial_district_code")
    core_decision = metric_value(core, "alb2005_household_core_current_decision", "missing")
    value_ready = metric_value(value, "alb2005_harmonization_value_decision_recipe_ready_rows")
    required_blocked = metric_value(value, "alb2005_harmonization_value_decision_required_blocked_rows")
    manual_future = metric_value(value, "alb2005_harmonization_value_decision_manual_future_candidate_rows")
    timing_verified = metric_value(timing, "alb2005_interview_timing_verified_rows")
    coordinate_rows = metric_value(timing, "alb2005_coordinate_candidate_rows")
    full_geo_rows = metric_value(timing, "alb2005_geography_verified_full_coverage_rows")
    climate_ready = metric_value(timing, "alb2005_climate_linkage_ready_rows")
    outcome_ready = metric_value(semantics, "alb2005_outcome_semantics_outcome_ready_rows")
    sdg_ready = metric_value(semantics, "alb2005_outcome_semantics_sdg382_ready_rows")
    unit_recipe_ready = metric_value(unit, "alb2005_consumption_oop_unit_period_recipe_ready_rows")
    unit_outcome_ready = metric_value(unit, "alb2005_consumption_oop_unit_period_outcome_ready_rows")
    oop_policy_ready = metric_value(oop, "alb2005_oop_aggregation_policy_recipe_ready_rows")
    component_recipe_ready = metric_value(components, "alb2005_consumption_component_source_search_recipe_ready_rows")
    construction_code_files = metric_value(components, "alb2005_consumption_component_source_search_construction_code_files_found")
    exact_missing = metric_value(components, "alb2005_consumption_component_source_search_exact_target_variables_missing")
    required_recipe_ready = metric_value(required_value, "alb2005_required_value_key_recipe_ready_rows")
    health_questionnaire_ready = metric_value(health_questionnaire, "alb2005_health_questionnaire_semantics_outcome_ready_rows")
    skip_ready = metric_value(skip_missing, "alb2005_skip_missing_semantics_outcome_ready_rows")

    actions = [
        action_row(
            1,
            "interview_timing",
            "survey_timing",
            f"verified_interview_timing_rows={timing_verified}; household survey_month rows={survey_month_rows}",
            "blocked_no_verified_household_interview_month_or_date",
            "Find raw household interview month/date or official fieldwork-period metadata that can be linked to households or defensibly assigned at wave/admin level.",
            "Machine-readable evidence shows nonmissing timing for the analysis rows, timing source/assumption, and exposure-window implications.",
        ),
        action_row(
            2,
            "geography_for_climate",
            "climate_geography",
            f"coordinate candidates={coordinate_rows}; full-coverage geography rows={full_geo_rows}; partial district code rows={partial_district_code_rows}",
            "blocked_partial_geography_no_gps_or_full_admin_crosswalk",
            "Resolve full-coverage admin geography or GPS/cluster geography, then document no-GPS/admin aggregation and boundary source.",
            "A joinable geography field covers analysis rows with boundary/crosswalk evidence and a declared geolocation-quality flag.",
        ),
        action_row(
            3,
            "oop_aggregation",
            "financial_protection_outcome",
            f"positive unreviewed OOP rows: 4w={oop_4w_positive}, 12m={oop_12m_positive}; OOP policy recipe-ready rows={oop_policy_ready}",
            "blocked_oop_aggregation_recall_skip_gift_policy",
            "Choose and document recall period, item scope, gift/payment inclusion, person-to-household aggregation, old/new lek handling, missing-code rules, and skip paths.",
            "OOP aggregation has a single auditable recipe with raw-variable lineage, value-label/missing-code rules, and event-rate checks.",
        ),
        action_row(
            4,
            "consumption_denominator",
            "financial_protection_denominator",
            f"total_consumption rows={total_consumption_rows}; unit-period recipe-ready rows={unit_recipe_ready}; construction code files found={construction_code_files}; exact component targets missing={exact_missing}",
            "blocked_consumption_unit_period_component_scope_review",
            "Confirm total-consumption unit, period, old/new lek basis, household-total interpretation, and whether `totcons` can be used as denominator without reconstructing components.",
            "Denominator audit accepts one raw variable or reconstruction path, with unit/period/price basis and missing-code rules.",
        ),
        action_row(
            5,
            "access_need_denominator",
            "access_outcome",
            f"outcome semantics ready rows={outcome_ready}; health questionnaire outcome-ready rows={health_questionnaire_ready}; skip/missing outcome-ready rows={skip_ready}",
            "blocked_need_access_denominator_skip_patterns",
            "Verify illness/need denominator, care-seeking/referral denominator, reason-not-sought coding, and cost/distance/supply barrier value labels.",
            "Access outcome formulas have eligible-denominator rules, raw value labels, and skip-path evidence.",
        ),
        action_row(
            6,
            "keys_weights_merge",
            "household_merge_and_survey_design",
            f"candidate rows={candidate_rows}; household weight rows={weight_rows}; required value/key recipe-ready rows={required_recipe_ready}",
            "blocked_merge_key_weight_design_manual_review",
            "Verify household ID uniqueness, cross-file merge cardinality, official weight variable use, and exclusion of birth-weight false positives.",
            "Key/weight audit accepts a household-level analysis frame with weight coverage and no unresolved false-positive weight variables.",
        ),
    ]

    gates = [
        gate_row(
            "household_frame",
            "Household frame and merge keys are accepted",
            "harmonized_household_dataset",
            "candidate_not_ready",
            f"temp candidate rows={candidate_rows}; core decision={core_decision}",
            "Complete household frame, key uniqueness/cardinality, and module coverage are verified.",
            "Allows a non-climate harmonized household candidate to be considered if value/outcome gates also pass.",
            "Do not write `data/harmonized_household.csv` while key/merge review remains unresolved.",
        ),
        gate_row(
            "survey_weight",
            "Household survey weight is verified",
            "weighted_descriptive_and_modeling",
            "candidate_not_ready",
            f"household weight rows={weight_rows}; required value/key recipe-ready rows={required_recipe_ready}",
            "Official household weight use and population are verified; birth-weight false positives are excluded.",
            "Permits weighted descriptive diagnostics after outcomes exist.",
            "Do not report weighted prevalence if the weight is not verified.",
        ),
        gate_row(
            "consumption_denominator",
            "Total consumption denominator is accepted",
            "CHE10_CHE25_and_SDG_denominator",
            "blocked",
            f"total consumption rows={total_consumption_rows}; unit recipe-ready={unit_recipe_ready}; component recipe-ready={component_recipe_ready}",
            "Total consumption has verified unit, period, price basis, missing rules, and household-total interpretation.",
            "Permits CHE10/CHE25 denominator construction; SDG 3.8.2 still requires poverty-line/discretionary-budget inputs.",
            "Do not construct official financial-protection outcomes until denominator semantics pass.",
        ),
        gate_row(
            "oop_aggregation",
            "OOP health expenditure aggregation is accepted",
            "CHE10_CHE25_and_OOP_outcomes",
            "blocked",
            f"positive unreviewed OOP rows: 4w={oop_4w_positive}, 12m={oop_12m_positive}; OOP policy recipe-ready={oop_policy_ready}",
            "OOP item scope, recall period, annualization policy, gift/payment inclusion, missing/zero rules, and household aggregation are verified.",
            "Permits provisional financial-hardship outcome construction after denominator gate passes.",
            "Do not treat unreviewed OOP sums as final outcomes.",
        ),
        gate_row(
            "health_need_access",
            "Need/care/access denominator is accepted",
            "forgone_care_and_double_failure_outcomes",
            "blocked",
            f"semantics outcome-ready rows={outcome_ready}; questionnaire outcome-ready rows={health_questionnaire_ready}; skip/missing outcome-ready rows={skip_ready}",
            "Illness/need, care-seeking, and barrier value labels and skip paths are verified.",
            "Permits access outcomes and UHC double-failure construction.",
            "Do not construct access or double-failure outcomes from unresolved skip-path variables.",
        ),
        gate_row(
            "interview_timing",
            "Interview timing is verified",
            "climate_linkage",
            "blocked",
            f"verified timing rows={timing_verified}; household survey_month rows={survey_month_rows}",
            "Interview month/date or defensible fieldwork-period timing is linked to analysis rows.",
            "Allows exposure-window construction after geography gate passes.",
            "Do not construct lagged climate exposures without timing.",
        ),
        gate_row(
            "climate_geography",
            "Climate geography is verified",
            "climate_linkage",
            "blocked",
            f"coordinate candidates={coordinate_rows}; full-coverage geography rows={full_geo_rows}; climate-ready rows={climate_ready}",
            "GPS/cluster coordinates or full-coverage admin geography with boundary/crosswalk evidence are available.",
            "Allows admin or point climate extraction with documented measurement error after timing gate passes.",
            "Do not call the dataset climate-linked while geography is partial or non-GPS without crosswalk evidence.",
        ),
        gate_row(
            "outcome_promotion",
            "Main outcomes may be constructed",
            "household_outcomes",
            "blocked",
            f"outcome-ready rows={outcome_ready}; SDG 3.8.2-ready rows={sdg_ready}; value-decision ready rows={value_ready}",
            "Key, weight, consumption, OOP, and access/need gates pass, with event-rate and missingness audits.",
            "Allows writing `data/household_outcomes.csv` for accepted outcome families.",
            "Do not write final outcome data while any required outcome component gate is blocked.",
        ),
        gate_row(
            "harmonized_dataset_promotion",
            "ALB_2005 may be promoted to a harmonized household dataset",
            "data/harmonized_household.csv",
            "blocked",
            f"value-decision recipe-ready rows={value_ready}; required blocked rows={required_blocked}; manual future candidate rows={manual_future}",
            "Required household frame, key, weight, denominator, OOP, and minimum outcome variables all pass value/key/unit review.",
            "Allows a single-country harmonized household dataset to be written, still without climate linkage if timing/geography remain blocked.",
            "Keep ALB_2005 in temp-only candidate state until all required minimum recipe gates pass.",
        ),
        gate_row(
            "climate_dataset_promotion",
            "ALB_2005 may be promoted to climate-linked analysis data",
            "data/climate_linked_household.csv",
            "blocked",
            f"climate-linkage-ready rows={climate_ready}; outcome-ready rows={outcome_ready}",
            "Harmonized dataset, accepted outcomes, verified timing, and verified climate geography all pass.",
            "Allows climate exposure extraction and merge for ALB_2005.",
            "Do not create climate-linked data until timing, geography, outcomes, and harmonization are all accepted.",
        ),
    ]

    summary = [
        summary_row("alb2005_minimum_recipe_promotion_action_rows", len(actions), "Action rows needed before ALB_2005 can become a minimum harmonized household dataset."),
        summary_row("alb2005_minimum_recipe_promotion_gate_rows", len(gates), "Pass/fail promotion gates for ALB_2005 harmonization, outcome, and climate linkage."),
        summary_row("alb2005_minimum_recipe_promotion_blocked_gates", sum(1 for row in gates if row["current_status"] == "blocked"), "Promotion gates still blocked."),
        summary_row("alb2005_minimum_recipe_promotion_candidate_gates", sum(1 for row in gates if row["current_status"] == "candidate_not_ready"), "Gates with candidate evidence that still needs acceptance review."),
        summary_row("alb2005_minimum_recipe_promotion_harmonized_ready_rows", 0, "Rows ready for harmonized dataset promotion after this packet; intentionally zero."),
        summary_row("alb2005_minimum_recipe_promotion_outcome_ready_rows", int_value(outcome_ready), "Existing ALB_2005 outcome-ready rows observed from semantics audits."),
        summary_row("alb2005_minimum_recipe_promotion_climate_linkage_ready_rows", int_value(climate_ready), "Existing ALB_2005 climate-linkage-ready rows observed from timing/geography audits."),
        summary_row("alb2005_minimum_recipe_promotion_current_decision", DECISION, "Current fail-closed ALB_2005 minimum recipe promotion decision."),
    ]
    return actions, gates, summary


def summary_row(metric: str, value: Any, interpretation: str) -> dict[str, str]:
    return {"metric": metric, "value": str(value), "interpretation": interpretation}


def markdown_rows(rows: list[dict[str, str]], columns: list[str]) -> str:
    lines = ["| " + " | ".join(columns) + " |", "|" + "|".join("---" for _ in columns) + "|"]
    for row in rows:
        values = []
        for column in columns:
            value = (row.get(column, "") or "").replace("|", "/")
            if len(value) > 115:
                value = value[:112] + "..."
            values.append(value)
        lines.append("| " + " | ".join(values) + " |")
    return "\n".join(lines)


def write_report(actions: list[dict[str, str]], gates: list[dict[str, str]], summary: list[dict[str, str]]) -> None:
    summary_table = "\n".join(f"| {row['metric']} | {row['value']} | {row['interpretation']} |" for row in summary)
    REPORT_PATH.write_text(
        f"""# ALB_2005 Minimum Recipe Promotion Packet

Status: fail-closed promotion packet. ALB_2005 is the current raw-ready first-batch candidate, but this packet does not promote any dataset to `data/`. It records what must pass before the temp household-core candidate can become a harmonized household dataset, outcome dataset, or climate-linked dataset.

## Summary

| Metric | Value | Interpretation |
|---|---:|---|
{summary_table}

## Action Queue

{markdown_rows(actions, ['action_rank', 'gate_id', 'blocker_domain', 'blocking_status', 'required_resolution'])}

## Promotion Gates

{markdown_rows(gates, ['gate_id', 'required_for', 'current_status', 'current_evidence', 'minimum_evidence_to_pass'])}

## Interpretation

- ALB_2005 has a substantial temp household-core candidate and raw value evidence, but it is not analysis-ready.
- The minimum harmonized dataset is blocked by key/weight review, denominator and OOP semantics, access/need skip paths, and the absence of accepted value-decision rows.
- Climate linkage is separately blocked by zero verified interview timing rows and no full-coverage GPS/admin geography.
- This packet preserves the line between useful raw diagnostics and promoted analytical data.

## Machine-Readable Outputs

- `temp/alb2005_minimum_recipe_promotion_action_queue.csv`
- `temp/alb2005_minimum_recipe_promotion_gate_checklist.csv`
- `result/alb2005_minimum_recipe_promotion_summary.csv`
""",
        encoding="utf-8",
    )


def main() -> None:
    ensure_dirs()
    actions, gates, summary = build_packet()
    write_csv(ACTION_QUEUE_PATH, actions, ACTION_COLUMNS)
    write_csv(GATE_CHECKLIST_PATH, gates, GATE_COLUMNS)
    write_csv(SUMMARY_PATH, summary, SUMMARY_COLUMNS)
    write_report(actions, gates, summary)
    append_log(TEMP_DIR / "audit_log.md", f"Built ALB_2005 minimum recipe promotion packet actions={len(actions)} gates={len(gates)} decision={DECISION}.")
    print(f"ALB_2005 minimum recipe promotion packet actions={len(actions)} gates={len(gates)} decision={DECISION}.")


if __name__ == "__main__":
    main()
