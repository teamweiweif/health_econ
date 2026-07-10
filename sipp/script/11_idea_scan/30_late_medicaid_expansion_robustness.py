from __future__ import annotations

from pathlib import Path
import importlib.util

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[2]
MOD_PATH = ROOT / "script" / "11_idea_scan" / "29_late_medicaid_expansion_threshold_test.py"
OUT = ROOT / "result" / "idea_scan"
REPORT = ROOT / "report" / "61_late_medicaid_expansion_robustness.md"


def load_base_module():
    spec = importlib.util.spec_from_file_location("late_expansion_base", MOD_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Cannot load {MOD_PATH}")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def ym_add(ym: int, months: int) -> int:
    year = ym // 100
    month = ym % 100
    total = year * 12 + (month - 1) + months
    return (total // 12) * 100 + (total % 12 + 1)


def keep_terms(est: pd.DataFrame, check: str) -> pd.DataFrame:
    d = est[est["outcome"].isin(["medicaid", "uninsured", "any_coverage", "public", "private"])].copy()
    d.insert(0, "check", check)
    return d[
        [
            "check",
            "spec",
            "outcome",
            "coef",
            "se_state_cluster",
            "t_state_cluster",
            "se_person_cluster",
            "t_person_cluster",
            "n",
            "persons",
            "states",
        ]
    ]


def main() -> None:
    mod = load_base_module()
    OUT.mkdir(parents=True, exist_ok=True)
    base = mod.prep()
    outcomes = ["medicaid", "uninsured", "any_coverage", "public", "private"]
    rows = []

    # Baseline narrow threshold design.
    d, x, label = mod.build_model_frame(base, "near_100_250_monthly_fpl")
    rows.append(keep_terms(mod.estimate(d, x, outcomes, "near_100_250_monthly_fpl", label), "baseline"))

    # Leave-one-treated-state checks.
    for state, date in mod.LATE_EXPANSION_DATES.items():
        state_name = mod.STATE_NAMES.get(state, state)
        filtered = base[base["state_fips"].ne(state)].copy()
        d, x, label = mod.build_model_frame(filtered, "near_100_250_monthly_fpl")
        rows.append(keep_terms(mod.estimate(d, x, outcomes, "near_100_250_monthly_fpl", label), f"drop_{state_name}"))

    # Group exclusions: early adopters, PHE adopters, and very late 2023 adopters.
    group_checks = {
        "drop_2019_2020_adopters": {"23", "51", "16", "49"},
        "drop_2021_phe_adopters": {"40", "29"},
        "drop_2023_adopters": {"46", "37"},
        "only_2021_phe_adopters_vs_never": set(mod.LATE_EXPANSION_DATES) - {"40", "29"},
    }
    for name, excluded in group_checks.items():
        filtered = base[~base["state_fips"].isin(excluded)].copy()
        if name == "only_2021_phe_adopters_vs_never":
            filtered = filtered[filtered["state_fips"].isin({"40", "29"} | mod.NEVER_EXPANSION)].copy()
        d, x, label = mod.build_model_frame(filtered, "near_100_250_monthly_fpl")
        rows.append(keep_terms(mod.estimate(d, x, outcomes, "near_100_250_monthly_fpl", label), name))

    # Fake pre-period placebo: move each late adopter's implementation 12 months earlier,
    # then drop true post-implementation months for late-adopter states.
    fake = base.copy()
    fake_impl = {state: ym_add(int(date.replace("-", "")), -12) for state, date in mod.LATE_EXPANSION_DATES.items()}
    true_impl = {state: int(date.replace("-", "")) for state, date in mod.LATE_EXPANSION_DATES.items()}
    fake["fake_implementation_ym"] = fake["state_fips"].map(fake_impl)
    fake["true_implementation_ym"] = fake["state_fips"].map(true_impl)
    pre_late = fake["late_expansion_state"].eq(1) & fake["month_id"].lt(fake["true_implementation_ym"])
    never = fake["never_expansion_state"].eq(1)
    fake = fake[pre_late | never].copy()
    fake["expansion_active"] = (
        fake["late_expansion_state"].eq(1)
        & fake["fake_implementation_ym"].notna()
        & fake["month_id"].ge(fake["fake_implementation_ym"])
    ).astype(float)
    d, x, label = mod.build_model_frame(fake, "near_100_250_monthly_fpl")
    rows.append(keep_terms(mod.estimate(d, x, outcomes, "near_100_250_monthly_fpl", label), "fake_12m_pre_placebo"))

    out = pd.concat(rows, ignore_index=True)
    out.to_csv(OUT / "late_medicaid_expansion_robustness.csv", index=False)

    selected = out[out["outcome"].isin(["medicaid", "uninsured"])].copy()
    pivot = selected.pivot(index="check", columns="outcome", values=["coef", "t_state_cluster"]).reset_index()
    pivot.columns = ["_".join([str(x) for x in col if x]) for col in pivot.columns.to_flat_index()]
    pivot.to_csv(OUT / "late_medicaid_expansion_robustness_pivot.csv", index=False)

    def md_table(df: pd.DataFrame, cols: list[str]) -> str:
        lines = ["| " + " | ".join(cols) + " |", "|" + "|".join(["---"] * len(cols)) + "|"]
        for _, r in df[cols].iterrows():
            vals = []
            for c in cols:
                v = r[c]
                vals.append(f"{v:.4f}" if isinstance(v, float) and np.isfinite(v) else str(v))
            lines.append("| " + " | ".join(vals) + " |")
        return "\n".join(lines)

    report = f"""# Late Medicaid Expansion Robustness Checks

## Purpose

The first late-expansion screen found large Medicaid gains and uninsured declines around the
100-138% FPL eligibility band. Because Medicaid expansion is a saturated literature, this file
stress-tests whether the signal is one-state driven or visible before implementation.

## Checks

- Baseline narrow design: monthly FPL 100-250%, eligible 100-138%.
- Leave one late-expansion state out.
- Drop early 2019/2020 adopters.
- Drop 2021 PHE adopters.
- Drop 2023 adopters.
- Keep only Oklahoma and Missouri as 2021 PHE adopters against never-expansion states.
- Fake pre-period placebo: move implementation 12 months earlier and remove true post months.

## Medicaid / Uninsured Summary

{md_table(pivot, list(pivot.columns))}

## Interpretation

The leave-one checks should preserve a positive Medicaid effect and negative uninsured effect if the
design is not dominated by a single treated state. The fake pre-period placebo should be much smaller
than the true effect; a large placebo would indicate anticipatory trends or treated-state pre-trend
differences that weaken causal interpretation.

## Artifacts

- `script/11_idea_scan/30_late_medicaid_expansion_robustness.py`
- `result/idea_scan/late_medicaid_expansion_robustness.csv`
- `result/idea_scan/late_medicaid_expansion_robustness_pivot.csv`
"""
    REPORT.write_text(report, encoding="utf-8")
    print(pivot.to_string(index=False))


if __name__ == "__main__":
    main()
