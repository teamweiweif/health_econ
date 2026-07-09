from __future__ import annotations

import csv
from pathlib import Path
from typing import Any

from common import REPORT_DIR, RESULT_DIR, TEMP_DIR, append_log, ensure_dirs, write_csv


GATE_PATH = TEMP_DIR / "albania_first_analysis_promotion_gate_checklist.csv"
ACTION_PATH = TEMP_DIR / "albania_first_analysis_promotion_action_queue.csv"
WAVE_PATH = RESULT_DIR / "albania_first_analysis_promotion_wave_ranking.csv"
SUMMARY_PATH = RESULT_DIR / "albania_first_analysis_promotion_summary.csv"
REPORT_PATH = REPORT_DIR / "albania_first_analysis_promotion_gate.md"

DECISION = "blocked_no_albania_wave_ready_for_first_analysis_promotion"

GATE_COLUMNS = [
    "country",
    "idno",
    "wave",
    "survey_name",
    "gate_id",
    "gate_label",
    "gate_status",
    "evidence_metric",
    "evidence_value",
    "evidence_source",
    "blocking_implication",
    "required_next_evidence",
]

ACTION_COLUMNS = [
    "priority_rank",
    "country",
    "idno",
    "wave",
    "action_id",
    "action_status",
    "blocking_gate",
    "action",
    "source_artifacts",
    "success_condition",
    "expected_effect",
]

WAVE_COLUMNS = [
    "priority_rank",
    "country",
    "idno",
    "wave",
    "survey_name",
    "household_rows",
    "consumption_rows",
    "weight_rows",
    "oop_4w_positive_rows",
    "oop_12m_positive_rows",
    "timing_signal_rows",
    "geography_signal_rows",
    "outcome_ready_rows",
    "sdg382_ready_rows",
    "climate_linkage_ready_rows",
    "harmonized_ready_rows",
    "candidate_evidence_gate_rows",
    "blocked_gate_rows",
    "promotion_ready",
    "primary_blocker",
    "recommended_next_action",
    "current_decision",
]

SUMMARY_COLUMNS = ["metric", "value", "interpretation"]


WAVES = [
    {
        "country": "Albania",
        "idno": "ALB_2002_LSMS_v01_M",
        "wave": "2002",
        "survey_name": "Living Standards Measurement Survey 2002",
        "rank_hint": 1,
        "core_summary": "alb2002_household_core_candidate_summary.csv",
        "outcome_summary": "alb2002_outcome_semantics_raw_value_summary.csv",
        "timing_summary": "alb2002_household_core_candidate_summary.csv",
        "geo_summary": "alb2002_boundary_manual_source_followup_summary.csv",
        "household_metric": "alb2002_household_core_candidate_rows",
        "consumption_metric": "alb2002_households_with_total_consumption",
        "weight_metric": "alb2002_households_with_household_weight",
        "oop_4w_metric": "alb2002_households_with_oop_4w_positive",
        "oop_12m_metric": "alb2002_households_with_oop_12m_positive",
        "timing_metric": "alb2002_households_with_interview_date",
        "geo_signal_metric": "alb2002_households_with_district_code",
        "geo_ready_metric": "alb2002_boundary_manual_source_followup_climate_linkage_ready_rows",
        "harmonized_ready_metric": "alb2002_household_core_recipe_ready_rows",
        "outcome_ready_metric": "alb2002_outcome_semantics_outcome_ready_rows",
        "sdg382_ready_metric": "alb2002_outcome_semantics_sdg382_ready_rows",
        "outcome_decision_metric": "alb2002_outcome_semantics_current_decision",
        "geo_decision_metric": "alb2002_boundary_manual_source_followup_current_decision",
        "primary_blocker": "verified_2002_district_boundary_absent_gadm_lead_blocked_and_outcome_semantics_unpromoted",
        "recommended_next_action": "review the GADM 3.6 district lead, resolve its duplicate SHKODER/provenance blocker or obtain an official 2001/2002 boundary, and manually resolve OOP/access unit, recall, value-label, and skip-pattern semantics",
    },
    {
        "country": "Albania",
        "idno": "ALB_2005_LSMS_v01_M",
        "wave": "2005",
        "survey_name": "Living Standards Measurement Survey 2005",
        "rank_hint": 2,
        "core_summary": "alb2005_household_core_candidate_summary.csv",
        "outcome_summary": "alb2005_outcome_semantics_raw_value_summary.csv",
        "timing_summary": "alb2005_timing_geography_exhaustive_summary.csv",
        "geo_summary": "alb2005_extracted_module_coverage_summary.csv",
        "household_metric": "alb2005_household_core_candidate_rows",
        "consumption_metric": "alb2005_households_with_total_consumption",
        "weight_metric": "alb2005_households_with_household_weight",
        "oop_4w_metric": "alb2005_households_with_oop_4w_positive",
        "oop_12m_metric": "alb2005_households_with_oop_12m_positive",
        "timing_metric": "alb2005_interview_timing_verified_rows",
        "geo_signal_metric": "alb2005_households_with_partial_district_code",
        "geo_ready_metric": "alb2005_extracted_module_coverage_climate_linkage_ready_rows",
        "harmonized_ready_metric": "alb2005_household_core_recipe_ready_rows",
        "outcome_ready_metric": "alb2005_outcome_semantics_outcome_ready_rows",
        "sdg382_ready_metric": "alb2005_outcome_semantics_sdg382_ready_rows",
        "outcome_decision_metric": "alb2005_outcome_semantics_current_decision",
        "geo_decision_metric": "alb2005_extracted_module_coverage_current_decision",
        "primary_blocker": "missing_bookmetadata_food_diary_modules_no_household_timing_no_coordinates",
        "recommended_next_action": "obtain missing bookmetadata/food-diary or official equivalent files, then verify household timing, geography/GPS, OOP units, and total-consumption denominator semantics",
    },
    {
        "country": "Albania",
        "idno": "ALB_2008_LSMS_v01_M",
        "wave": "2008",
        "survey_name": "Living Standards Measurement Survey 2008",
        "rank_hint": 3,
        "core_summary": "alb2008_household_core_candidate_summary.csv",
        "outcome_summary": "alb2008_outcome_semantics_raw_value_summary.csv",
        "timing_summary": "alb2008_timing_geography_exhaustive_summary.csv",
        "geo_summary": "alb2008_timing_geography_exhaustive_summary.csv",
        "household_metric": "alb2008_household_core_candidate_rows",
        "consumption_metric": "alb2008_households_with_total_consumption",
        "weight_metric": "alb2008_households_with_household_weight",
        "oop_4w_metric": "alb2008_households_with_oop_4w_positive",
        "oop_12m_metric": "alb2008_households_with_oop_12m_positive",
        "timing_metric": "alb2008_interview_timing_verified_rows",
        "geo_signal_metric": "alb2008_coarse_geography_household_rows",
        "geo_ready_metric": "alb2008_climate_linkage_ready_rows",
        "harmonized_ready_metric": "alb2008_household_core_recipe_ready_rows",
        "outcome_ready_metric": "alb2008_outcome_semantics_outcome_ready_rows",
        "sdg382_ready_metric": "alb2008_outcome_semantics_sdg382_ready_rows",
        "outcome_decision_metric": "alb2008_outcome_semantics_current_decision",
        "geo_decision_metric": "alb2008_timing_geography_current_decision",
        "primary_blocker": "missing_interview_timing_and_only_coarse_geography_no_gps",
        "recommended_next_action": "find official fieldwork/interview timing and a defensible admin geography crosswalk before revisiting OOP/access semantics",
    },
    {
        "country": "Albania",
        "idno": "ALB_2012_LSMS_v01_M_v01_A_PUF",
        "wave": "2012",
        "survey_name": "Living Standards Measurement Survey 2012",
        "rank_hint": 4,
        "core_summary": "alb2012_raw_core_feasibility_summary.csv",
        "outcome_summary": "alb2012_outcome_semantics_raw_value_summary.csv",
        "timing_summary": "alb2012_timing_geography_exhaustive_summary.csv",
        "geo_summary": "alb2012_timing_geography_exhaustive_summary.csv",
        "household_metric": "alb2012_household_core_candidate_rows",
        "consumption_metric": "alb2012_households_with_total_consumption",
        "weight_metric": "alb2012_households_with_household_weight",
        "oop_4w_metric": "alb2012_households_with_oop_4w_positive",
        "oop_12m_metric": "alb2012_households_with_oop_12m_positive",
        "timing_metric": "alb2012_interview_timing_verified_rows",
        "geo_signal_metric": "alb2012_coarse_geography_household_rows",
        "geo_ready_metric": "alb2012_climate_linkage_ready_rows",
        "harmonized_ready_metric": "alb2012_household_core_recipe_ready_rows",
        "outcome_ready_metric": "alb2012_outcome_semantics_outcome_ready_rows",
        "sdg382_ready_metric": "alb2012_outcome_semantics_sdg382_ready_rows",
        "outcome_decision_metric": "alb2012_outcome_semantics_current_decision",
        "geo_decision_metric": "alb2012_timing_geography_current_decision",
        "primary_blocker": "missing_interview_timing_coarse_prefecture_region_no_gps",
        "recommended_next_action": "link questionnaire timing fields to raw household dates or official fieldwork metadata and verify whether prefecture/region aggregation is defensible",
    },
]


def read_csv_dicts(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        return []
    with path.open(encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def metric(rows: list[dict[str, str]], name: str, default: str = "0") -> str:
    for row in rows:
        if row.get("metric") == name:
            return row.get("value", default)
    return default


def safe_int(value: Any) -> int:
    try:
        return int(float(str(value).strip()))
    except (TypeError, ValueError):
        return 0


def gate_status(value: int, ready_value: int = 0, candidate_if_positive: bool = True) -> str:
    if ready_value > 0:
        return "ready_for_promotion"
    if value > 0 and candidate_if_positive:
        return "candidate_evidence_not_promoted"
    return "blocked_missing_required_evidence"


def add_gate(
    rows: list[dict[str, str]],
    wave: dict[str, Any],
    gate_id: str,
    label: str,
    status: str,
    source: str,
    evidence_metric: str,
    evidence_value: Any,
    implication: str,
    required: str,
) -> None:
    rows.append(
        {
            "country": wave["country"],
            "idno": wave["idno"],
            "wave": wave["wave"],
            "survey_name": wave["survey_name"],
            "gate_id": gate_id,
            "gate_label": label,
            "gate_status": status,
            "evidence_metric": evidence_metric,
            "evidence_value": str(evidence_value),
            "evidence_source": source,
            "blocking_implication": implication,
            "required_next_evidence": required,
        }
    )


def build_rows() -> tuple[list[dict[str, str]], list[dict[str, str]], list[dict[str, str]], list[dict[str, str]]]:
    gates: list[dict[str, str]] = []
    actions: list[dict[str, str]] = []
    waves: list[dict[str, str]] = []

    for wave in WAVES:
        core = read_csv_dicts(RESULT_DIR / wave["core_summary"])
        outcome = read_csv_dicts(RESULT_DIR / wave["outcome_summary"])
        timing = read_csv_dicts(RESULT_DIR / wave["timing_summary"])
        geo = read_csv_dicts(RESULT_DIR / wave["geo_summary"])

        household_rows = safe_int(metric(core, wave["household_metric"]))
        consumption_rows = safe_int(metric(core, wave["consumption_metric"]))
        weight_rows = safe_int(metric(core, wave["weight_metric"]))
        oop_4w = safe_int(metric(core, wave["oop_4w_metric"]))
        oop_12m = safe_int(metric(core, wave["oop_12m_metric"]))
        timing_rows = safe_int(metric(timing, wave["timing_metric"], metric(core, wave["timing_metric"])))
        geo_signal_rows = safe_int(metric(core, wave["geo_signal_metric"], metric(timing, wave["geo_signal_metric"], "0")))
        climate_ready = safe_int(metric(geo, wave["geo_ready_metric"], metric(timing, wave["geo_ready_metric"], "0")))
        harmonized_ready = safe_int(metric(core, wave["harmonized_ready_metric"]))
        outcome_ready = safe_int(metric(outcome, wave["outcome_ready_metric"]))
        sdg_ready = safe_int(metric(outcome, wave["sdg382_ready_metric"]))

        add_gate(
            gates,
            wave,
            "household_frame",
            "Household frame candidate exists",
            gate_status(household_rows, harmonized_ready),
            f"result/{wave['core_summary']}",
            wave["household_metric"],
            household_rows,
            "A raw household candidate can be reviewed, but this alone is not an analysis-ready dataset.",
            "Keep lineage and merge-key evidence attached to any future harmonization recipe.",
        )
        add_gate(
            gates,
            wave,
            "consumption_denominator",
            "Total consumption/income candidate exists",
            gate_status(consumption_rows, 0),
            f"result/{wave['core_summary']}",
            wave["consumption_metric"],
            consumption_rows,
            "Financial-protection denominators have candidate values but are not yet accepted for SDG or CHE construction.",
            "Verify unit, period, price basis, and denominator variant against official documentation.",
        )
        add_gate(
            gates,
            wave,
            "survey_weight",
            "Household weight candidate exists",
            gate_status(weight_rows, 0),
            f"result/{wave['core_summary']}",
            wave["weight_metric"],
            weight_rows,
            "Weight candidates are present but survey-design semantics still require review before estimation.",
            "Verify weight, stratum, PSU, and merge semantics.",
        )
        add_gate(
            gates,
            wave,
            "oop_health_spending",
            "OOP health spending candidate values exist",
            gate_status(max(oop_4w, oop_12m), outcome_ready),
            f"result/{wave['core_summary']}; result/{wave['outcome_summary']}",
            f"{wave['oop_4w_metric']};{wave['oop_12m_metric']}",
            f"{oop_4w};{oop_12m}",
            "OOP positive-value diagnostics are not final outcomes because units, recall periods, missing codes, and skip patterns remain unaccepted.",
            "Manually accept or reject OOP item scope, gift handling, recall-period standardization, and missing-code treatment.",
        )
        add_gate(
            gates,
            wave,
            "interview_timing",
            "Interview timing supports climate windows",
            gate_status(timing_rows, 0),
            f"result/{wave['timing_summary']}",
            wave["timing_metric"],
            timing_rows,
            "Climate windows cannot be constructed unless timing is household-level or otherwise justified for the wave.",
            "Verify raw household interview date/month or official fieldwork period usable for exposure windows.",
        )
        add_gate(
            gates,
            wave,
            "geography_or_gps",
            "Geography supports climate linkage",
            "ready_for_promotion" if climate_ready > 0 else ("candidate_evidence_not_promoted" if geo_signal_rows > 0 else "blocked_missing_required_evidence"),
            f"result/{wave['geo_summary']}",
            wave["geo_signal_metric"],
            geo_signal_rows,
            "Climate linkage remains blocked until geography is verified as GPS or defensible admin aggregation.",
            "Verify GPS/coordinate values or a historically valid admin boundary/crosswalk.",
        )
        add_gate(
            gates,
            wave,
            "outcome_semantics",
            "Outcome semantics are accepted for construction",
            "ready_for_promotion" if outcome_ready > 0 else "blocked_missing_required_evidence",
            f"result/{wave['outcome_summary']}",
            wave["outcome_decision_metric"],
            metric(outcome, wave["outcome_decision_metric"], ""),
            "No wave has final outcome construction authorization.",
            "Resolve units, recall periods, missing codes, conditional denominators, and skip patterns.",
        )
        add_gate(
            gates,
            wave,
            "sdg382_denominator",
            "SDG 3.8.2 denominator is accepted",
            "ready_for_promotion" if sdg_ready > 0 else "blocked_missing_required_evidence",
            f"result/{wave['outcome_summary']}",
            wave["sdg382_ready_metric"],
            sdg_ready,
            "SDG 3.8.2 cannot be claimed until discretionary-budget inputs are verified.",
            "Verify SPL/PPP/CPI inputs and household discretionary-budget denominator construction.",
        )
        add_gate(
            gates,
            wave,
            "climate_linkage",
            "Climate-linked analytical input is ready",
            "ready_for_promotion" if climate_ready > 0 else "blocked_missing_required_evidence",
            f"result/{wave['geo_summary']}",
            wave["geo_ready_metric"],
            climate_ready,
            "No climate-linked analytical dataset can be built for this wave yet.",
            "Pass timing and geography gates, then construct and audit climate exposures.",
        )
        add_gate(
            gates,
            wave,
            "harmonized_dataset",
            "Harmonized household dataset may be promoted to data/",
            "ready_for_promotion" if harmonized_ready > 0 and outcome_ready > 0 and climate_ready > 0 else "blocked_missing_required_evidence",
            f"result/{wave['core_summary']}; result/{wave['outcome_summary']}; result/{wave['geo_summary']}",
            f"{wave['harmonized_ready_metric']};{wave['outcome_ready_metric']};{wave['geo_ready_metric']}",
            f"{harmonized_ready};{outcome_ready};{climate_ready}",
            "The wave cannot be used as the first analysis sample until harmonization, outcome, and climate gates all pass.",
            "Create data outputs only after all upstream gates are satisfied.",
        )

        wave_gates = [row for row in gates if row["idno"] == wave["idno"]]
        blocked = sum(1 for row in wave_gates if row["gate_status"] == "blocked_missing_required_evidence")
        candidate = sum(1 for row in wave_gates if row["gate_status"] == "candidate_evidence_not_promoted")
        ready = sum(1 for row in wave_gates if row["gate_status"] == "ready_for_promotion")
        promotion_ready = int(harmonized_ready > 0 and outcome_ready > 0 and climate_ready > 0)

        waves.append(
            {
                "priority_rank": str(wave["rank_hint"]),
                "country": wave["country"],
                "idno": wave["idno"],
                "wave": wave["wave"],
                "survey_name": wave["survey_name"],
                "household_rows": str(household_rows),
                "consumption_rows": str(consumption_rows),
                "weight_rows": str(weight_rows),
                "oop_4w_positive_rows": str(oop_4w),
                "oop_12m_positive_rows": str(oop_12m),
                "timing_signal_rows": str(timing_rows),
                "geography_signal_rows": str(geo_signal_rows),
                "outcome_ready_rows": str(outcome_ready),
                "sdg382_ready_rows": str(sdg_ready),
                "climate_linkage_ready_rows": str(climate_ready),
                "harmonized_ready_rows": str(harmonized_ready),
                "candidate_evidence_gate_rows": str(candidate + ready),
                "blocked_gate_rows": str(blocked),
                "promotion_ready": str(promotion_ready),
                "primary_blocker": wave["primary_blocker"],
                "recommended_next_action": wave["recommended_next_action"],
                "current_decision": DECISION if not promotion_ready else "ready_for_first_analysis_promotion",
            }
        )

        actions.append(
            {
                "priority_rank": str(wave["rank_hint"]),
                "country": wave["country"],
                "idno": wave["idno"],
                "wave": wave["wave"],
                "action_id": f"{wave['idno']}_resolve_primary_blocker",
                "action_status": "blocked_manual_or_external_evidence_required",
                "blocking_gate": wave["primary_blocker"],
                "action": wave["recommended_next_action"],
                "source_artifacts": f"result/{wave['core_summary']}; result/{wave['outcome_summary']}; result/{wave['timing_summary']}; result/{wave['geo_summary']}",
                "success_condition": "harmonized_ready_rows>0, outcome_ready_rows>0, and climate_linkage_ready_rows>0 for the wave",
                "expected_effect": "would make the wave eligible for the first harmonized and climate-linked analytical dataset gate, subject to validation",
            }
        )

    waves.sort(key=lambda row: int(row["priority_rank"]))
    actions.sort(key=lambda row: int(row["priority_rank"]))

    top = waves[0] if waves else {}
    summary = [
        summary_row("albania_first_analysis_promotion_wave_rows", len(waves), "Albania local raw waves compared for first analysis-sample promotion."),
        summary_row("albania_first_analysis_promotion_gate_rows", len(gates), "Promotion gate checklist rows."),
        summary_row("albania_first_analysis_promotion_action_rows", len(actions), "Prioritized action rows."),
        summary_row("albania_first_analysis_promotion_candidate_or_ready_gate_rows", sum(1 for row in gates if row["gate_status"] in {"candidate_evidence_not_promoted", "ready_for_promotion"}), "Gate rows with candidate or ready evidence."),
        summary_row("albania_first_analysis_promotion_blocked_gate_rows", sum(1 for row in gates if row["gate_status"] == "blocked_missing_required_evidence"), "Promotion gates still blocked."),
        summary_row("albania_first_analysis_promotion_ready_wave_rows", sum(1 for row in waves if row["promotion_ready"] == "1"), "Waves ready for first analytical-sample promotion; should remain zero until gates pass."),
        summary_row("albania_first_analysis_promotion_harmonized_ready_rows", sum(safe_int(row["harmonized_ready_rows"]) for row in waves), "Harmonized-ready rows across compared waves; should remain zero."),
        summary_row("albania_first_analysis_promotion_outcome_ready_rows", sum(safe_int(row["outcome_ready_rows"]) for row in waves), "Outcome-ready rows across compared waves; should remain zero."),
        summary_row("albania_first_analysis_promotion_climate_linkage_ready_rows", sum(safe_int(row["climate_linkage_ready_rows"]) for row in waves), "Climate-linkage-ready rows across compared waves; should remain zero."),
        summary_row("albania_first_analysis_promotion_top_ranked_idno", top.get("idno", ""), "Top local raw wave to investigate next."),
        summary_row("albania_first_analysis_promotion_top_ranked_primary_blocker", top.get("primary_blocker", ""), "Binding blocker for the top-ranked local wave."),
        summary_row("albania_first_analysis_promotion_current_decision", DECISION, "Current fail-closed first-analysis promotion decision."),
    ]
    return gates, actions, waves, summary


def summary_row(metric_name: str, value: Any, interpretation: str) -> dict[str, str]:
    return {"metric": metric_name, "value": str(value), "interpretation": interpretation}


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
    if len(rows) > limit:
        lines.append("| " + " | ".join(["..."] + [f"{len(rows) - limit} additional rows omitted"] + [""] * max(0, len(columns) - 2)) + " |")
    return "\n".join(lines)


def write_report(gates: list[dict[str, str]], actions: list[dict[str, str]], waves: list[dict[str, str]], summary: list[dict[str, str]]) -> None:
    summary_table = "\n".join(f"| {row['metric']} | {row['value']} | {row['interpretation']} |" for row in summary)
    REPORT_PATH.write_text(
        f"""# Albania First Analysis Promotion Gate

Status: fail-closed promotion gate. This packet compares local Albania raw waves and identifies the nearest path to the first harmonized, outcome-audited, climate-linked analytical dataset.

## Summary

| Metric | Value | Interpretation |
|---|---:|---|
{summary_table}

## Wave Ranking

{markdown_rows(waves, ['priority_rank', 'idno', 'wave', 'household_rows', 'timing_signal_rows', 'geography_signal_rows', 'outcome_ready_rows', 'climate_linkage_ready_rows', 'blocked_gate_rows', 'primary_blocker'])}

## Action Queue

{markdown_rows(actions, ['priority_rank', 'idno', 'blocking_gate', 'action', 'success_condition'], 10)}

## Gate Checklist Preview

{markdown_rows(gates, ['idno', 'gate_id', 'gate_status', 'evidence_metric', 'evidence_value', 'required_next_evidence'], 30)}

## Interpretation

- `ALB_2002_LSMS_v01_M` remains the nearest local raw-data path because it has household rows, consumption, weights, OOP candidates, interview date/month, and district-code signals.
- It still cannot be promoted because the public boundary follow-up found no conclusive 2002-compatible 36-district boundary source; the GADM 3.6 lead has duplicate `SHKODER` features and no verified official 2001/2002 provenance, and outcome semantics remain unpromoted.
- `ALB_2005_LSMS_v01_M` has useful household/OOP/consumption signals but is blocked by missing `bookmetadata_cl`/food-diary modules, no verified household timing, and no coordinate values.
- `ALB_2008_LSMS_v01_M` and `ALB_2012_LSMS_v01_M_v01_A_PUF` have usable household/value signals but lack verified interview timing and have only coarse/non-GPS geography in the current extracts.
- This packet writes no `data/` files and promotes zero harmonized, outcome, or climate-linkage rows.

## Machine-Readable Outputs

- `temp/albania_first_analysis_promotion_gate_checklist.csv`
- `temp/albania_first_analysis_promotion_action_queue.csv`
- `result/albania_first_analysis_promotion_wave_ranking.csv`
- `result/albania_first_analysis_promotion_summary.csv`
""",
        encoding="utf-8",
    )


def main() -> None:
    ensure_dirs()
    gates, actions, waves, summary = build_rows()
    write_csv(GATE_PATH, gates, GATE_COLUMNS)
    write_csv(ACTION_PATH, actions, ACTION_COLUMNS)
    write_csv(WAVE_PATH, waves, WAVE_COLUMNS)
    write_csv(SUMMARY_PATH, summary, SUMMARY_COLUMNS)
    write_report(gates, actions, waves, summary)
    append_log(TEMP_DIR / "audit_log.md", f"Built Albania first-analysis promotion gate waves={len(waves)} decision={DECISION}.")
    print(f"Albania first-analysis promotion gate waves={len(waves)} decision={DECISION}.")


if __name__ == "__main__":
    main()
