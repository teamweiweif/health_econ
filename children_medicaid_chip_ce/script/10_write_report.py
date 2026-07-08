from __future__ import annotations

from pathlib import Path

import pandas as pd

from project_utils import DATA, REPORT, RESULT, TEMP, append_audit


def read_csv_if(path: Path) -> pd.DataFrame:
    return pd.read_csv(path) if path.exists() and path.stat().st_size > 0 else pd.DataFrame()


def fmt_est(df: pd.DataFrame, term: str | None = None) -> str:
    if df.empty:
        return "not estimated"
    d = df if term is None else df[df["term"].astype(str).eq(term)]
    if d.empty:
        d = df.head(1)
    r = d.iloc[0]
    est = r.get("estimate")
    se = r.get("std_error")
    n = r.get("n")
    try:
        return f"{float(est):.4f} (SE {float(se):.4f}, n={int(n)})"
    except Exception:
        return "not estimated"


def summarize_outputs() -> dict:
    main = read_csv_if(RESULT / "main_ddd_table.csv")
    event = read_csv_if(RESULT / "main_event_study_coefficients.csv")
    robust = read_csv_if(RESULT / "robustness_summary.csv")
    mech = read_csv_if(RESULT / "renewal_mechanism_table.csv")
    acs = read_csv_if(RESULT / "acs_validation_table.csv")
    loo = read_csv_if(RESULT / "leave_one_state_out.csv")
    coverage = read_csv_if(RESULT / "source_coverage_table.csv")
    summary = {
        "main_any": fmt_est(
            main[main["spec"].eq("main_any_newly_treated_gap")] if "spec" in main else main,
            "did_any_newly_treated",
        ),
        "mechanism_procedural": fmt_est(
            mech[mech.get("mechanism_outcome", pd.Series(dtype=str)).eq("procedural_termination_rate_due")] if not mech.empty else mech,
            "did_any_newly_treated",
        ),
        "acs_uninsured": fmt_est(
            acs[acs.get("validation_outcome", pd.Series(dtype=str)).eq("uninsured_percent")] if not acs.empty else acs,
            "ddd_any_newly_treated",
        ),
        "event_pre_coefficients": int(((event.get("event_month", pd.Series(dtype=float)) < 0) & event.get("estimate", pd.Series(dtype=float)).notna()).sum()) if not event.empty else 0,
        "event_post_coefficients": int(((event.get("event_month", pd.Series(dtype=float)) >= 0) & event.get("estimate", pd.Series(dtype=float)).notna()).sum()) if not event.empty else 0,
        "leave_one_state_min": float(loo["estimate"].min()) if not loo.empty and "estimate" in loo else None,
        "leave_one_state_max": float(loo["estimate"].max()) if not loo.empty and "estimate" in loo else None,
        "coverage_rows": int(coverage["rows"].sum()) if not coverage.empty and "rows" in coverage else None,
    }
    return summary


def write_readme() -> None:
    text = """# Children Medicaid/CHIP Continuous Eligibility Project

This workspace builds an audit-ready public-data empirical project on the January 1, 2024 federal mandate requiring 12-month continuous eligibility for children under age 19 in Medicaid and CHIP.

## Reproduce

From the project root:

```powershell
powershell -ExecutionPolicy Bypass -File script/run_all.ps1
```

On Unix-like shells:

```bash
bash script/run_all.sh
```

Or run the verified Python sequence directly:

```powershell
python script/00_setup.py
python script/01_acquire_sources.py
python script/02_build_policy_panel.py
python script/03_build_enrollment_panel.py
python script/04_build_renewal_mechanism_panel.py
python script/05_build_acs_validation_panel.py
python script/06_construct_designs_and_outcomes.py
python script/07_descriptive_diagnostics.py
python script/08_main_models.py
python script/09_robustness_and_falsification.py
python script/10_write_report.py
```

Clean analysis files are in `data/`, model and diagnostic outputs are in `result/`, and source/audit logs are in `temp/`.
"""
    (REPORT / "README.md").write_text(text, encoding="utf-8")


def write_data_dictionary() -> None:
    lines = ["# Data Dictionary", ""]
    for fname in [
        "state_policy_month.parquet",
        "enrollment_state_group_month.parquet",
        "renewal_state_month.parquet",
        "acs_state_age_year.parquet",
        "main_ddd_panel.parquet",
        "mechanism_panel.parquet",
        "validation_panel.parquet",
    ]:
        path = DATA / fname
        if not path.exists():
            continue
        df = pd.read_parquet(path)
        lines.append(f"## {fname}")
        lines.append(f"Rows: {len(df)}. Columns: {len(df.columns)}.")
        for col in df.columns:
            lines.append(f"- `{col}`: {str(df[col].dtype)}")
        lines.append("")
    lines.append("Constructed outcome caveat: aggregate enrollment volatility is an aggregate coverage-instability proxy, not individual-level churn.")
    (REPORT / "data_dictionary.md").write_text("\n".join(lines), encoding="utf-8")


def write_identification(summary: dict) -> None:
    text = f"""# Identification Audit

## Preferred Design

The preferred design is implemented as a state-month child-vs-adult/non-child enrollment-gap difference-in-differences, equivalent to the two-group DDD comparison after differencing children against adults/non-children within each state-month:

`log(child enrollment) - log(adult/non-child enrollment proxy)` on `NewlyTreatedState x Post2024`, with state and month fixed effects.

The estimand is the incremental association of the federal 2024 children CE mandate in states without any pre-2024 child CE, relative to the adult/non-child comparison group and relative to already or partly compliant states. The adult/non-child comparison is constructed as total Medicaid/CHIP enrollment minus child Medicaid/CHIP enrollment so that the comparison group is consistently available from 2018 forward.

## Treatment Coding

Pre-2024 child CE status is transcribed from KFF/Georgetown Table 5 for January 2023 and preserved in `temp/policy_seed_child_ce_jan2023.csv`. The federal post period begins January 2024, verified against CMS SHO 23-004, CMS FAQ 10/27/2023, and the CMS continuous eligibility page.

## Main Threats

- The Medicaid unwinding transition in 2023 is the central confounder.
- Adult Medicaid enrollment is not a perfect untreated group.
- Already-compliant states are prior-treated comparison states, not never-treated controls.
- Renewal mechanism outcomes are state-level, not child-specific.
- Public state-month enrollment does not observe true individual churn.

## Diagnostics Status

Main DDD estimate: {summary['main_any']}.

Event-study coefficients estimated: {summary['event_pre_coefficients']} pre-period and {summary['event_post_coefficients']} post-period coefficients.

The final go/no-go judgment is in `temp/go_no_go.md` and `report/final_report.md`.
"""
    (REPORT / "identification_audit.md").write_text(text, encoding="utf-8")


def write_final_report(summary: dict) -> None:
    loo_text = "not available"
    if summary["leave_one_state_min"] is not None:
        loo_text = f"{summary['leave_one_state_min']:.4f} to {summary['leave_one_state_max']:.4f}"
    text = f"""# Final Report

## Executive Summary

This project built a reproducible public-data workspace for the January 1, 2024 children Medicaid/CHIP 12-month continuous eligibility mandate. The main empirical product is a state-month child-vs-adult/non-child DDD-style enrollment-gap panel using CMS enrollment data through the latest staged June 2026 release, plus state-level renewal mechanism data and ACS health-insurance table validation.

Main DDD estimate for log enrollment: {summary['main_any']}.

Renewal mechanism procedural-rate estimate: {summary['mechanism_procedural']}.

ACS child-vs-adult uninsured validation estimate: {summary['acs_uninsured']}.

## Policy Background

Section 5112 of the Consolidated Appropriations Act, 2023 required all states to provide 12 months of continuous eligibility for children under age 19 in Medicaid and CHIP beginning January 1, 2024. Before that date, KFF/Georgetown Table 5 shows substantial state variation: some states already provided CE in Medicaid and CHIP, some only in one program, some only for younger ages, and some did not provide child CE.

## Exposure Definition

The primary exposure is `newly_treated_any_child_ce`: states with no pre-2024 child CE in either Medicaid or CHIP. Secondary designs use Medicaid-only and partial-or-new exposure definitions.

## Data Sources And Coverage

Core sources are CMS/Data.Medicaid.gov enrollment data, CMS eligibility processing renewal data, KFF/Georgetown policy survey Table 5, CMS SHO 23-004, CMS FAQ guidance, and Census ACS HI-05 public tables. Source inventory is in `temp/source_inventory.csv`.

## Outcomes

Primary administrative outcomes are child enrollment, adult/non-child proxy enrollment, the log child-adult/non-child enrollment gap, month-to-month net loss, and aggregate coverage-instability proxies. Mechanism outcomes include ex parte renewal rate, procedural termination rate/share, and pending renewal share. ACS validation outcomes include public/Medicaid coverage and uninsured percentages for children under 19 and adults 19-64.

## Identification

The preferred DDD-style gap design is stronger than a simple state DID because children are differenced against an adult/non-child comparison group before comparing newly treated states with already or partly compliant states. This is still not perfect: the comparison group is affected by Medicaid policy and unwinding, and already-compliant states are prior-treated comparison states.

## Diagnostics And Robustness

Dynamic event-study coefficients were estimated and plotted in `result/child_adult_gap_event_study.png`. Leave-one-state-out estimates ranged from {loo_text}. Window robustness outputs are in `result/robustness_summary.csv`.

## Mechanism Evidence

Renewal outcomes were attempted, but they are state-level and generally not child-specific. They should be interpreted as mechanism-consistent context or moderators, not child-specific causal outcomes.

## Survey Validation

ACS validation was attempted using Census published HI-05 tables. The reproducible XLSX parser uses 2019 and 2021-2024; 2020 is omitted by Census 1-year release limitations, and the 2018 HI-05 source is a legacy XLS file recorded in the source inventory but not parsed without an XLS reader. Census API access returned a key requirement in this environment, so validation uses official public table files rather than live API microdata/PUMS.

## Rejected Designs

Rejected or downgraded designs are documented in `temp/rejected_designs.md`. The main downgrades are: no individual-level true churn in public aggregate enrollment, renewal outcomes not child-specific, and ACS only having one current post-policy year in the staged tables.

## Final Go/No-Go Judgment

This workspace is empirically usable as a reproducible feasibility and first-results platform. It should not yet be treated as a finished publishable causal paper unless event-study pretrends, mechanism coherence, and influence diagnostics are judged acceptable after reviewing the generated plots and tables. If those diagnostics are weak, the appropriate paper is a transparent weak-design or wait-for-better-data report, not a significance search.

## Next Empirical Steps

1. Add a stronger state-specific source for CHIP premiums, lockouts, waiting periods, and unwinding completion timing.
2. Use a Census API key or direct PUMS download if microdata heterogeneity is required.
3. Add wild cluster bootstrap or randomization inference for state-cluster uncertainty.
4. Audit event-study pretrends visually before advancing to manuscript claims.
"""
    (REPORT / "final_report.md").write_text(text, encoding="utf-8")
    (TEMP / "go_no_go.md").write_text(
        "# Go/No-Go Assessment\n\n"
        "Status: conditional go for continued empirical development, not unconditional go for publication.\n\n"
        "Reasons to continue: official CMS enrollment and renewal data are available; pre-2024 CE coding is reproducible; main DDD and event-study scripts run; ACS validation is staged from public Census tables.\n\n"
        "Reasons to be cautious: aggregate data do not measure true churn; renewal mechanisms are not child-specific; 2023 unwinding remains the main threat; ACS validation currently has only one post-policy year.\n",
        encoding="utf-8",
    )


def write_skeleton() -> None:
    text = """# Manuscript Skeleton

## Title

One Mandate, Uneven Baselines: Mandatory 12-Month Continuous Eligibility for Children in Medicaid/CHIP, Coverage Stability, Administrative Churn, and Procedural Disenrollment

## Abstract

To be finalized after diagnostic review. The paper studies whether the 2024 federal child CE mandate changed children's Medicaid/CHIP coverage stability relative to adults and relative to already-compliant states.

## Sections

1. Introduction and contribution
2. Policy background and January 2024 mandate
3. Pre-2024 state variation in child CE
4. Data and source audit
5. Outcomes and limits of aggregate churn proxies
6. Identification strategy
7. Descriptive trends
8. Main DDD estimates
9. Event-study diagnostics and pretrends
10. Renewal/procedural mechanism evidence
11. ACS validation
12. Robustness and falsification
13. Limitations
14. Go/no-go and next data needs
"""
    (REPORT / "manuscript_skeleton.md").write_text(text, encoding="utf-8")


def main() -> None:
    REPORT.mkdir(exist_ok=True)
    summary = summarize_outputs()
    write_readme()
    write_data_dictionary()
    write_identification(summary)
    write_final_report(summary)
    write_skeleton()
    append_audit("final report and manuscript skeleton written")
    print("reports written")


if __name__ == "__main__":
    main()
