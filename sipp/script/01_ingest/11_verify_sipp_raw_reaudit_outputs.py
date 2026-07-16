from __future__ import annotations

import ast
import csv
import re
from pathlib import Path

import pandas as pd
import pyarrow.parquet as pq


ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "data" / "sample_audits" / "sipp_reaudit_final_checks_20260716.csv"


def truthy(series: pd.Series) -> pd.Series:
    return series.astype(str).str.strip().str.lower().isin({"true", "1", "yes"})


def add(checks: list[dict], check_id: str, requirement: str, passed: bool, evidence: str) -> None:
    checks.append(
        {
            "check_id": check_id,
            "requirement": requirement,
            "passed": bool(passed),
            "evidence": evidence,
        }
    )


def main() -> None:
    checks: list[dict] = []

    remote = pd.read_csv(
        ROOT / "data" / "sample_audits" / "sipp_remote_byte_comparison_20260716.csv"
    )
    remote_pass = truthy(remote["remote_bytes_exactly_match_local"])
    add(
        checks,
        "remote_byte_identity",
        "All 50 canonical ZIPs exactly match the current official remotes",
        len(remote) == 50 and remote_pass.all() and remote["status"].eq("PASS").all(),
        f"rows={len(remote)}; passed={int(remote_pass.sum())}; bytes={int(remote['compared_bytes'].sum())}",
    )
    add(
        checks,
        "remote_year_coverage",
        "Current official re-audit covers file years 2018-2025",
        sorted(remote["file_year"].unique().tolist()) == list(range(2018, 2026)),
        f"years={sorted(remote['file_year'].unique().tolist())}",
    )

    releases = pd.read_csv(ROOT / "data" / "metadata" / "sipp_release_version_ledger_2018_2025.csv")
    expected_versions = {**{year: 1.1 for year in range(2018, 2022)}, **{year: 1.0 for year in range(2022, 2026)}}
    observed_versions = dict(zip(releases["file_year"], releases["current_release_version"]))
    add(
        checks,
        "release_versions",
        "Current releases are v1.1 for 2018-2021 and v1.0 for 2022-2025",
        observed_versions == expected_versions,
        f"observed={observed_versions}",
    )

    provenance = pd.read_csv(
        ROOT / "data" / "metadata" / "sipp_official_document_provenance_20260716.csv"
    )
    core_roles = {
        *(f"{year}_release_notes" for year in range(2018, 2026)),
        "2018_plus_weight_selection_guide",
        "2025_users_guide",
        "2025_source_and_accuracy_statement",
    }
    core = provenance[provenance["document_role"].isin(core_roles)]
    add(
        checks,
        "official_core_documents",
        "Release notes, weight guide, latest users guide, and source/accuracy PDF match official bytes",
        set(core["document_role"]) == core_roles
        and truthy(core["remote_bytes_exactly_match_local"]).all(),
        f"required_roles={len(core_roles)}; matched_roles={len(core)}",
    )

    v11 = pd.read_csv(ROOT / "data" / "sample_audits" / "sipp_v11_correction_panel_alignment.csv")
    add(
        checks,
        "v11_panel_alignment",
        "All 32 audited v1.1 income/poverty year-variable comparisons match current raw",
        len(v11) == 32 and truthy(v11["all_keys_and_values_match"]).all(),
        f"rows={len(v11)}; mismatches={int(v11['value_mismatches_after_float32_cast'].sum())}",
    )

    health = pd.read_csv(ROOT / "data" / "sample_audits" / "sipp_health_source_panel_alignment.csv")
    add(
        checks,
        "health_source_panel_alignment",
        "All 42 audited health source year-variable comparisons match current raw",
        len(health) == 42 and truthy(health["all_keys_and_values_match"]).all(),
        f"rows={len(health)}; mismatches={int(health['value_mismatches_after_float32_cast'].sum())}",
    )

    patch_path = (
        ROOT
        / "data"
        / "analysis_ready"
        / "sipp_2018_2023_health_insurance_official_usernote_correction_patch.parquet"
    )
    patch_meta = pq.ParquetFile(patch_path).metadata
    patch_keys = pd.read_parquet(
        patch_path, columns=["file_year", "SSUID", "PNUM", "MONTHCODE"]
    )
    add(
        checks,
        "health_patch_unique",
        "The additive health correction patch has 19,625 unique person-month keys",
        patch_meta.num_rows == 19625
        and not patch_keys.duplicated(["file_year", "SSUID", "PNUM", "MONTHCODE"]).any(),
        f"rows={patch_meta.num_rows}; duplicate_keys={int(patch_keys.duplicated().sum())}",
    )

    issue_register = pd.read_csv(
        ROOT / "data" / "sample_audits" / "sipp_raw_and_weight_issue_register_20260716.csv"
    )
    weight_issue = issue_register.loc[
        issue_register["issue_id"].eq("TSSSAMT_FALSE_WEIGHT_FALLBACK")
    ]
    add(
        checks,
        "issue_register",
        "The current issue register contains all 15 classified findings",
        len(issue_register) == 15 and len(weight_issue) == 1,
        f"rows={len(issue_register)}",
    )

    fallback_pattern = re.compile(r"where\([^\r\n]*TSSSAMT")
    fallback_files: list[str] = []
    syntax_errors: list[str] = []
    for path in (ROOT / "script" / "11_idea_scan").glob("*.py"):
        source = path.read_text(encoding="utf-8", errors="replace")
        if fallback_pattern.search(source):
            fallback_files.append(path.name)
        try:
            ast.parse(source, filename=str(path))
        except SyntaxError:
            syntax_errors.append(path.name)
    add(
        checks,
        "invalid_weight_fallback_removed",
        "No idea-screen script retains the TSSSAMT weight fallback",
        not fallback_files,
        f"matching_files={fallback_files}",
    )
    add(
        checks,
        "idea_scan_syntax",
        "All idea-screen Python files parse after the weight repair",
        not syntax_errors,
        f"syntax_errors={syntax_errors}",
    )

    weights = pd.read_csv(ROOT / "data" / "metadata" / "sipp_weight_product_use_ledger.csv")
    add(
        checks,
        "weight_ledger",
        "Weight ledger covers monthly, annual, and 2/3/4-year estimands with Fay-BRR replicates",
        len(weights) == 5
        and set(weights["point_weight"]) == {"WPFINWGT", "FINYR2", "FINYR3", "FINYR4"}
        and weights["replicate_variables"].eq("REPWGT1-REPWGT240").all(),
        f"rows={len(weights)}; estimands={weights['estimand_time_scope'].tolist()}",
    )

    response = pd.read_csv(
        ROOT / "data" / "metadata" / "sipp_2025_response_and_attrition_summary.csv"
    )
    observed_response = dict(
        zip(response["panel_or_weight"], response["weighted_response_rate_percent"])
    )
    add(
        checks,
        "response_attrition_ledger",
        "2025 response ledger records the official cross-sectional and FINYR2/3/4 rates",
        len(response) == 8
        and observed_response.get("2022-2025 panels") == 42.63
        and observed_response.get("FINYR2") == 61.67
        and observed_response.get("FINYR3") == 42.42
        and observed_response.get("FINYR4") == 25.75,
        f"rows={len(response)}; selected_rates={observed_response}",
    )

    sensitivity = pd.read_csv(
        ROOT / "result" / "data_audit" / "arpa400_health_weight_data_quality_sensitivity.csv"
    )
    corrected = sensitivity[
        sensitivity["data_quality_scenario"].eq(
            "official_positive_wpfinwgt_plus_health_usernote_correction"
        )
        & sensitivity["outcome"].eq("uninsured")
    ]
    add(
        checks,
        "arpa_corrected_sensitivity",
        "Corrected ARPA uninsured sensitivity is present and remains below |t|=1.96 with person clustering",
        len(corrected) == 1
        and corrected.iloc[0]["coef_above_x_post"] < 0
        and abs(corrected.iloc[0]["t_person_cluster"]) < 1.96,
        (
            "coef="
            f"{corrected.iloc[0]['coef_above_x_post']:.6f}; "
            f"person_t={corrected.iloc[0]['t_person_cluster']:.3f}"
            if len(corrected) == 1
            else "corrected row missing"
        ),
    )

    required_reports = [
        ROOT / "report" / "107_arpa400_raw_data_quality_sensitivity.md",
        ROOT / "report" / "108_sipp_official_sources_versions_weights_raw_reaudit.md",
        ROOT / "report" / "109_sipp_raw_data_issue_register.md",
    ]
    add(
        checks,
        "current_reports",
        "Current sensitivity, comprehensive audit, and issue-register reports exist",
        all(path.exists() and path.stat().st_size > 0 for path in required_reports),
        "|".join(str(path.relative_to(ROOT)) for path in required_reports),
    )

    partials = list((ROOT / "temp").rglob("*.part"))
    add(
        checks,
        "no_partial_downloads",
        "No interrupted .part downloads remain",
        not partials,
        f"part_files={len(partials)}",
    )

    OUT.parent.mkdir(parents=True, exist_ok=True)
    with OUT.open("w", newline="", encoding="utf-8-sig") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(checks[0]))
        writer.writeheader()
        writer.writerows(checks)

    failed = [row for row in checks if not row["passed"]]
    print(f"SIPP REAUDIT FINAL CHECKS passed={len(checks) - len(failed)}/{len(checks)}")
    for row in failed:
        print(f"FAIL {row['check_id']}: {row['evidence']}")
    if failed:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
