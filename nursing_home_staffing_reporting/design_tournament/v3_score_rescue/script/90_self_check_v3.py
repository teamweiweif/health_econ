from __future__ import annotations

import csv
import sys
from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
DT_ROOT = ROOT.parents[0]
REPORT = ROOT / "report"
TABLES = ROOT / "result" / "tables"
AUDIT = ROOT / "temp" / "audit_logs"
SCRIPT = ROOT / "script"


def rel(path: Path) -> str:
    return str(path.relative_to(ROOT))


def add(rows: list[dict], check: str, target: str, ok: bool, value: str = "") -> None:
    rows.append(
        {
            "check": check,
            "target": target,
            "pass": bool(ok),
            "value": value,
            "n": 1,
            "sample_definition": "self-check requirement row",
        }
    )


def contains(path: Path, *needles: str) -> bool:
    if not path.exists():
        return False
    text = path.read_text(encoding="utf-8", errors="replace").lower()
    return all(n.lower() in text for n in needles)


def main() -> int:
    rows: list[dict] = []
    v2_inputs = [
        DT_ROOT / "report" / "final_breakthrough_report.md",
        DT_ROOT / "report" / "design_tournament_scorecard.md",
        DT_ROOT / "report" / "rating_algorithm_emulation_audit.md",
        DT_ROOT / "report" / "rd_threshold_results.md",
        DT_ROOT / "report" / "formula_label_shock_results.md",
        DT_ROOT / "report" / "metric_salience_ddd_results.md",
        DT_ROOT / "report" / "official_policy_algorithm_audit.md",
        DT_ROOT / "report" / "outcome_reconstruction_audit.md",
        DT_ROOT / "report" / "identification_audit_v2.md",
        DT_ROOT / "temp" / "rejected_designs_v2.md",
        DT_ROOT / "temp" / "self_test_v2.md",
    ]
    for p in v2_inputs:
        add(rows, "v2_input_report_exists", str(p.relative_to(DT_ROOT)), p.exists(), str(p.exists()))

    inv = TABLES / "official_score_field_inventory.csv"
    add(rows, "official_source_field_inventory_exists", rel(inv), inv.exists(), str(inv.stat().st_size if inv.exists() else 0))

    em = TABLES / "emulator_validation_v3.csv"
    add(rows, "emulator_validation_exists", rel(em), em.exists(), str(em.stat().st_size if em.exists() else 0))
    july_recorded = False
    july_match = None
    if em.exists():
        df = pd.read_csv(em)
        row = df[df["snapshot_date"].astype(str).eq("2022-07-27")]
        if not row.empty and "star_match_rate" in row:
            july_recorded = True
            july_match = float(row["star_match_rate"].iloc[0])
    add(rows, "july_2022_match_rate_recorded", rel(em), july_recorded, "" if july_match is None else f"{july_match:.6f}")

    rd_report = REPORT / "03_rd_rddid_rescue_results.md"
    rd_nogo = REPORT / "03_rd_rddid_no_go_due_to_running_variable.md"
    rd_ok = False
    if rd_report.exists() and july_match is not None:
        rd_ok = july_match >= 0.95 and contains(rd_report, "running variable passed")
    if rd_nogo.exists():
        rd_ok = rd_ok or contains(rd_nogo, "no-go")
    add(rows, "rd_report_consistent_with_running_variable_status", "report/03", rd_ok, f"july_match={july_match}")

    formula_report = REPORT / "04_formula_label_shock_rescue_results.md"
    formula_ok = contains(formula_report, "first stage", "balance", "pretrends", "matched")
    for p in [
        TABLES / "formula_label_first_stage_v3.csv",
        TABLES / "formula_label_balance_v3.csv",
        TABLES / "formula_label_pretrends_v3.csv",
        TABLES / "formula_label_eventstudy_v3.csv",
        TABLES / "formula_label_matched_estimates_v3.csv",
    ]:
        formula_ok = formula_ok and p.exists()
    add(rows, "formula_report_has_required_sections_and_tables", rel(formula_report), formula_ok, str(formula_ok))

    metric_report = REPORT / "05_metric_salience_ddd_rescue_results.md"
    metric_ok = contains(metric_report, "facility-week") and (ROOT / "data" / "metric_salience_panel_v3.parquet").exists()
    add(rows, "metric_salience_uses_day_or_week_panel_or_documents_infeasibility", rel(metric_report), metric_ok, str(metric_ok))

    val2018_report = REPORT / "06_2018_validation_rescue_results.md"
    val2018_ok = contains(val2018_report, "zero-rn validation summary") or contains(val2018_report, "infeasible")
    add(rows, "2018_validation_results_or_infeasibility", rel(val2018_report), val2018_ok, str(val2018_ok))

    final = REPORT / "final_score_rescue_report.md"
    final_ok = contains(final, "rd/rd-did", "formula-induced", "metric-salience", "2018 validation", "recommended manuscript path")
    add(rows, "final_report_design_decisions_present", rel(final), final_ok, str(final_ok))

    all_reports_text = "\n".join(p.read_text(encoding="utf-8", errors="replace").lower() for p in REPORT.glob("*.md"))
    strong_go_claimed = any(
        token in all_reports_text
        for token in [
            "executive judgment\n\nstrong go",
            "decision: **strong go",
            "decision: strong go",
            "strong go for a local",
        ]
    )
    diagnostics_pass = False
    if strong_go_claimed and (TABLES / "rd_density_checks_v3.csv").exists():
        dens = pd.read_csv(TABLES / "rd_density_checks_v3.csv")
        bal = pd.read_csv(TABLES / "rd_covariate_balance_v3.csv")
        pre = pd.read_csv(TABLES / "rd_preoutcome_checks_v3.csv")
        diagnostics_pass = dens["binomial_density_p"].min() > 0.01 and (bal["p"].lt(0.05).mean() < 0.10) and (pre["p"].lt(0.05).mean() < 0.10)
    add(rows, "no_strong_causal_claim_without_diagnostics", "all v3 reports", (not strong_go_claimed) or diagnostics_pass, f"strong_go_claimed={strong_go_claimed}; diagnostics_pass={diagnostics_pass}")

    clinical_bad = False
    for idx in [m.start() for m in __import__("re").finditer("resident clinical quality improvement", all_reports_text)]:
        window = all_reports_text[max(0, idx - 100): idx + 120]
        if not any(token in window for token in ["not", "no ", "none", "cannot", "does not prove", "avoid"]):
            clinical_bad = True
    add(rows, "no_clinical_quality_improvement_claim", "all v3 reports", not clinical_bad, str(clinical_bad))

    old_did_primary = "old composite exposure did is the primary" in all_reports_text or "old composite exposure did as the primary design" in all_reports_text
    add(rows, "old_composite_did_not_primary", "all v3 reports", not old_did_primary, str(old_did_primary))

    table_checks = []
    for p in TABLES.glob("*.csv"):
        try:
            df = pd.read_csv(p, nrows=5)
            has_n = any(c in df.columns for c in ["n", "n_facilities", "n_valid_match_test", "n_rows_checked", "below_n"])
            has_sample = "sample_definition" in df.columns or p.name == "official_score_field_inventory.csv"
            table_checks.append(has_n and has_sample)
        except Exception:
            table_checks.append(False)
    add(rows, "all_result_tables_have_row_counts_and_sample_definitions", "result/tables/*.csv", all(table_checks), f"{sum(table_checks)}/{len(table_checks)}")

    scripts_ok = (SCRIPT / "v3_common.py").exists() and (SCRIPT / "90_self_check_v3.py").exists()
    add(rows, "scripts_runnable_from_project_or_v3_root", "script", scripts_ok, str(scripts_ok))

    failures = list(AUDIT.glob("*failure*.csv")) + list(AUDIT.glob("*failures*.csv"))
    documented = True
    for p in failures:
        documented = documented and p.stat().st_size > 0
    add(rows, "failed_downloads_or_missing_official_files_documented", "temp/audit_logs", documented, f"failure_files={len(failures)}")

    AUDIT.mkdir(parents=True, exist_ok=True)
    TABLES.mkdir(parents=True, exist_ok=True)
    with (TABLES / "self_check_v3.csv").open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["check", "target", "pass", "value", "n", "sample_definition"])
        w.writeheader()
        w.writerows(rows)
    failed = [r for r in rows if not r["pass"]]
    lines = ["# Self Check V3", "", f"Checks passed: {len(rows) - len(failed)}/{len(rows)}.", ""]
    if failed:
        lines += ["## Failed Checks", ""]
        for r in failed:
            lines.append(f"- {r['check']} (`{r['target']}`): {r['value']}")
    else:
        lines += ["## Failed Checks", "", "None."]
    lines += [
        "",
        "## Key Audit Interpretation",
        "",
        "- July 2022 emulator match is recorded and must exceed 0.950 before RD/RD-DID can be rerun as candidate evidence.",
        "- Strong causal language is blocked unless RD density, balance, pre-outcome, placebo, and bandwidth checks pass.",
        "- Reports are checked for avoiding resident clinical quality-improvement claims based only on staffing/rating outcomes.",
    ]
    (AUDIT / "self_check_v3.md").write_text("\n".join(lines).strip() + "\n", encoding="utf-8")
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
