from __future__ import annotations

import csv
from pathlib import Path

import pandas as pd


THIS_FILE = Path(__file__).resolve()
AUDIT_ROOT = THIS_FILE.parents[1]
TABLES = AUDIT_ROOT / "result" / "tables"
REPORT = AUDIT_ROOT / "report"


REQUIRED_TABLES: dict[str, list[str]] = {
    "time_period_policy_variable_map.csv": [
        "period_id",
        "period_dates",
        "policy_status",
        "public_reporting_status",
        "five_star_rating_status",
        "employee_level_data_status",
        "provider_catalog_field_status",
        "interpretation_for_pre_period",
        "interpretation_for_research_design",
        "source_evidence",
    ],
    "raw_pbj_daily_codebook_by_period.csv": [
        "period_id",
        "source_file_or_doc",
        "exact_raw_variable_name",
        "exact_label_or_description",
        "job_code_if_applicable",
        "staff_type_if_applicable",
        "unit",
        "frequency_or_unit_of_observation",
        "first_available_period_verified",
        "last_available_period_verified",
        "appears_before_jan2022",
        "appears_after_jan2022",
        "notes",
        "source_evidence",
    ],
    "pbj_employee_detail_codebook_by_period.csv": [
        "period_id",
        "source_file_or_doc",
        "exact_raw_variable_name",
        "exact_label_or_description",
        "unit",
        "frequency_or_unit_of_observation",
        "first_public_availability",
        "needed_for_turnover",
        "appears_before_jan2022_publicly",
        "appears_after_jan2022_publicly",
        "notes",
        "source_evidence",
    ],
    "provider_catalog_codebook_by_snapshot.csv": [
        "snapshot_date",
        "archive_zip_or_source",
        "file_name",
        "exact_raw_variable_name",
        "exact_label_or_description",
        "normalized_project_name_if_any",
        "role",
        "missingness",
        "direct_official_field",
        "constructed_in_project",
        "notes",
        "source_evidence",
    ],
    "six_measure_rating_component_crosswalk.csv": [
        "official_six_measure_number",
        "official_measure_name_from_technical_guide",
        "official_description",
        "official_rating_role",
        "max_points",
        "point_rule",
        "official_raw_or_adjusted_status",
        "exact_available_field_jan2022",
        "exact_available_field_apr2022",
        "exact_available_field_jul2022",
        "exact_available_field_oct2022",
        "exact_available_field_jan2023",
        "project_variable_name",
        "direct_or_reconstructed",
        "reconstruction_formula_if_any",
        "evidence_strength",
        "source_evidence",
        "notes",
    ],
    "constructed_variables_codebook.csv": [
        "constructed_variable_name",
        "formula",
        "inputs_exact_raw_field_names",
        "unit",
        "constructed_from_raw_or_official_component",
        "first_period_constructible",
        "valid_pre_period",
        "valid_post_period",
        "used_as_outcome",
        "used_as_running_variable_component",
        "used_as_treatment_or_exposure",
        "notes",
        "source_evidence",
    ],
    "running_variable_audit.csv": [
        "running_variable_name",
        "official_or_reconstructed",
        "source_components",
        "formula",
        "official_cutoffs",
        "cutoffs_source",
        "validation_target",
        "validation_match_rate",
        "validation_period",
        "validity_status",
        "limitations",
        "design_implication",
        "source_evidence",
    ],
    "outcome_family_codebook.csv": [
        "outcome_family",
        "outcome_variable_name",
        "raw_or_constructed",
        "exact_inputs",
        "period_available",
        "level_of_observation",
        "interpretation",
        "policy_proximity",
        "should_be_primary",
        "limitations",
        "source_evidence",
    ],
}


def check_rows() -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []

    loaded: dict[str, pd.DataFrame] = {}
    for file_name, cols in REQUIRED_TABLES.items():
        path = TABLES / file_name
        ok = path.exists()
        rows.append(check(f"exists_{file_name}", ok, str(path), "all required CSV tables exist"))
        if not ok:
            continue
        df = pd.read_csv(path, dtype=str).fillna("")
        loaded[file_name] = df
        missing = [c for c in cols if c not in df.columns]
        rows.append(check(f"columns_{file_name}", not missing, ", ".join(missing), "all required columns are present"))
        if "source_evidence" in df.columns:
            empty_evidence = int(df["source_evidence"].astype(str).str.strip().eq("").sum())
            rows.append(check(f"source_evidence_{file_name}", empty_evidence == 0, f"empty_rows={empty_evidence}", "every row has source evidence"))

    constructed = loaded.get("constructed_variables_codebook.csv")
    if constructed is not None:
        marker = constructed["constructed_from_raw_or_official_component"].str.lower().str.strip()
        bad = constructed[marker.eq("raw official field")]
        rows.append(check("constructed_not_raw_official", bad.empty, f"bad_rows={len(bad)}", "no constructed variable is listed as a raw official field"))

    time_map = loaded.get("time_period_policy_variable_map.csv")
    if time_map is not None:
        jan_rows = time_map[time_map["period_id"].str.contains("2022_01|2022_01_26", regex=True)]
        text = " ".join(jan_rows.astype(str).agg(" ".join, axis=1).tolist()).lower()
        rows.append(
            check(
                "jan2022_not_first_pbj_daily_existence",
                "not the first" in text or "not a clean untreated" in text or "transition" in text,
                text[:300],
                "January 2022 is not described as first existence of PBJ daily staffing data",
            )
        )
        jan_july = time_map[time_map["period_id"].eq("2022_01_26_to_2022_07_26")]
        transition_text = " ".join(jan_july.astype(str).agg(" ".join, axis=1).tolist()).lower()
        rows.append(
            check(
                "jan_to_july_not_clean_pre",
                "not a clean untreated pre-period" in transition_text or "transition" in transition_text,
                transition_text[:300],
                "January-July 2022 is not described as clean untreated pre-period",
            )
        )

    six = loaded.get("six_measure_rating_component_crosswalk.csv")
    if six is not None:
        weekend = six[six["official_measure_name_from_technical_guide"].str.lower().str.contains("weekend")]
        july_text = " ".join(weekend["exact_available_field_jul2022"].astype(str).tolist()).lower()
        direct_text = " ".join(weekend["direct_or_reconstructed"].astype(str).tolist()).lower()
        rows.append(
            check(
                "july_adjusted_weekend_not_falsely_direct",
                "absent" in july_text and "reconstructed" in direct_text,
                f"july_field={july_text}; direct={direct_text}",
                "July 2022 adjusted weekend total nurse HPRD is not falsely described as directly available if absent",
            )
        )

    running = loaded.get("running_variable_audit.csv")
    if running is not None:
        official = running[running["running_variable_name"].str.contains("official_facility_level", regex=False)]
        official_text = " ".join(official.astype(str).agg(" ".join, axis=1).tolist()).lower()
        rows.append(
            check(
                "official_0_380_not_direct_observed",
                "not found" in official_text and "not_directly_observed" in official_text,
                official_text[:300],
                "official 0-380 score is not falsely described as directly observed",
            )
        )

    report_path = REPORT / "final_time_versioned_codebook.md"
    report_exists = report_path.exists()
    rows.append(check("final_report_exists", report_exists, str(report_path), "final report exists"))
    if report_exists:
        report = report_path.read_text(encoding="utf-8").lower()
        rows.append(
            check(
                "report_separates_variable_types",
                all(term in report for term in ["raw variables", "official published measures", "reconstructed official-like", "research-created outcomes"]),
                "variable-type terms checked",
                "final report clearly separates raw variables, official measures, reconstructed variables, and outcomes",
            )
        )
        rows.append(
            check(
                "report_jan2022_not_first_data",
                "january 2022 is not the first existence of pbj daily staffing data" in report,
                "phrase checked",
                "final report states January 2022 is not first existence of PBJ daily data",
            )
        )
        rows.append(
            check(
                "report_jan_july_transition",
                "january-july 2022 is a transition" in report or "january-july 2022 is a transition/public-reporting/anticipation period" in report,
                "phrase checked",
                "final report states January-July 2022 is transition, not clean pre-period",
            )
        )

    return rows


def check(name: str, passed: bool, detail: str, requirement: str) -> dict[str, str]:
    return {
        "check_name": name,
        "passed": "PASS" if passed else "FAIL",
        "requirement": requirement,
        "detail": detail.strip(),
    }


def write_outputs(rows: list[dict[str, str]]) -> None:
    out_csv = TABLES / "self_check_metadata_audit.csv"
    out_csv.parent.mkdir(parents=True, exist_ok=True)
    with out_csv.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["check_name", "passed", "requirement", "detail"])
        writer.writeheader()
        writer.writerows(rows)

    n_pass = sum(r["passed"] == "PASS" for r in rows)
    n_fail = sum(r["passed"] == "FAIL" for r in rows)
    lines = [
        "# Self-Check Metadata Audit",
        "",
        f"Result: {'PASS' if n_fail == 0 else 'FAIL'}",
        "",
        f"- Passed checks: {n_pass}",
        f"- Failed checks: {n_fail}",
        "",
        "| Check | Status | Requirement | Detail |",
        "|---|---:|---|---|",
    ]
    for row in rows:
        detail = row["detail"].replace("\n", " ").replace("|", "/")[:220]
        lines.append(f"| {row['check_name']} | {row['passed']} | {row['requirement']} | {detail} |")
    report_path = REPORT / "self_check_metadata_audit.md"
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text("\n".join(lines) + "\n", encoding="utf-8")

    if n_fail:
        raise SystemExit(f"Self-check failed with {n_fail} failed checks.")


def main() -> None:
    rows = check_rows()
    write_outputs(rows)


if __name__ == "__main__":
    main()
