from __future__ import annotations

import importlib.util
from pathlib import Path

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "result" / "idea_scan"
REPORT = ROOT / "report" / "56_arpa_400fpl_rd_diagnostics.md"
EMP_SCRIPT = ROOT / "script" / "11_idea_scan" / "26_arpa_400fpl_employer_mechanism_test.py"


spec = importlib.util.spec_from_file_location("arpa400_emp", EMP_SCRIPT)
emp = importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(emp)


OUTCOMES = ["uninsured", "employer_private", "direct_purchase", "marketplace_flag", "market_or_subsidy", "private"]


def wmean(y: pd.Series, w: pd.Series) -> float:
    mask = y.notna() & w.notna() & (w > 0)
    if not mask.any():
        return np.nan
    return float(np.average(y[mask].astype(float), weights=w[mask].astype(float)))


def prepare_panel() -> pd.DataFrame:
    df = emp.read_augmented_panel()
    d = df.copy()
    d["state_fips"] = d["state_fips"].astype(str).str.zfill(2)
    d["age"] = emp.bounded_numeric(d["TAGE"], 0, 100)
    d["female"] = pd.to_numeric(d["ESEX"], errors="coerce").eq(2).astype(float)
    d["black"] = pd.to_numeric(d["ERACE"], errors="coerce").eq(2).astype(float)
    d["hispanic"] = emp.yes(d["EHISPAN"]).astype(float)
    d["disabled"] = emp.yes(d["RDIS"]).astype(float)
    d["monthly_fpl"] = emp.bounded_numeric(d["TFINCPOV"], 0, 20)
    d["annual_fpl"] = emp.bounded_numeric(d["TFCYINCPOV"], 0, 20)
    d["weight"] = emp.clean_weight(d)
    d["month_id"] = d["reference_year"].astype(int) * 100 + d["reference_month"].astype(int)
    d["post_year2021"] = d["reference_year"].ge(2021).astype(int)
    d["post_apr2021"] = d["month_id"].ge(202104).astype(int)
    d["medicare"] = emp.yes(d["RPUBTYPE1"]).astype(float)

    d["any_coverage"] = emp.yes(d["RHLTHMTH"]).astype(float)
    d["uninsured"] = d["RHLTHMTH"].eq(2).astype(float)
    d["private"] = emp.yes(d["RPRIMTH"]).astype(float)
    d["public"] = emp.yes(d["RPUBMTH"]).astype(float)
    d["medicaid"] = emp.yes(d["EMDMTH"]).astype(float)
    d["employer_private"] = emp.yes(d["RPRITYPE1"]).astype(float)
    d["direct_purchase"] = (emp.yes(d["RPRITYPE2"]) | emp.yes(d["RMARKTPLACE"])).astype(float)
    d["marketplace_flag"] = (
        emp.yes(d["RMARKTPLACE"]) | emp.yes(d["EPRIEXCH1"]) | emp.yes(d["EPRIEXCH2"]) | emp.yes(d["EMDEXCH"])
    ).astype(float)
    d["subsidized_private"] = (emp.yes(d["EPRISUBS1"]) | emp.yes(d["EPRISUBS2"]) | emp.yes(d["EMDSUBS"])).astype(float)
    d["market_or_subsidy"] = (
        d["direct_purchase"].eq(1) | d["marketplace_flag"].eq(1) | d["subsidized_private"].eq(1)
    ).astype(float)
    return d


def add_fe(parts: list[pd.Series | pd.DataFrame], s: pd.DataFrame, fe_cols: list[str]) -> pd.DataFrame:
    for col in fe_cols:
        parts.append(pd.get_dummies(s[col].astype(str), prefix=col, drop_first=True, dtype=float))
    return pd.concat(parts, axis=1)


def local_diffdisc(s: pd.DataFrame, outcome: str, model: str, bandwidth: float = 0.5) -> dict:
    d = s.copy()
    d["running"] = d["monthly_fpl"] - 4.0
    d["above"] = d["monthly_fpl"].gt(4.0).astype(float)
    d["post"] = d["post_year2021"].astype(float)
    d["above_x_post"] = d["above"] * d["post"]
    d["kernel"] = (1 - (d["running"].abs() / bandwidth)).clip(lower=0)
    d["analysis_weight"] = d["weight"] * d["kernel"]
    parts: list[pd.Series | pd.DataFrame] = [
        pd.Series(1.0, index=d.index, name="const"),
        d["above"].rename("above"),
        d["post"].rename("post"),
        d["above_x_post"].rename("above_x_post"),
        d["running"].rename("running"),
        (d["running"] * d["above"]).rename("running_x_above"),
        (d["running"] * d["post"]).rename("running_x_post"),
        (d["running"] * d["above"] * d["post"]).rename("running_x_above_x_post"),
        d["age"].rename("age"),
        d["female"].rename("female"),
        d["black"].rename("black"),
        d["hispanic"].rename("hispanic"),
        d["disabled"].rename("disabled"),
    ]
    x = add_fe(parts, d, ["reference_year", "reference_month", "state_fips"])
    beta, se_hc1, se_cluster, n, g = emp.wls_hc1_cluster(
        d[outcome].to_numpy(dtype=float),
        x.to_numpy(dtype=float),
        d["analysis_weight"].to_numpy(dtype=float),
        d["person_id"].to_numpy(),
    )
    b = pd.Series(beta, index=x.columns)
    cl = pd.Series(se_cluster, index=x.columns)
    hc1 = pd.Series(se_hc1, index=x.columns)
    return {
        "model": model,
        "outcome": outcome,
        "coef": b.get("above_x_post", np.nan),
        "se_hc1": hc1.get("above_x_post", np.nan),
        "t_hc1": b.get("above_x_post", np.nan) / hc1.get("above_x_post", np.nan)
        if hc1.get("above_x_post", np.nan) > 0
        else np.nan,
        "se_person_cluster": cl.get("above_x_post", np.nan),
        "t_person_cluster": b.get("above_x_post", np.nan) / cl.get("above_x_post", np.nan)
        if cl.get("above_x_post", np.nan) > 0
        else np.nan,
        "n": n,
        "persons": int(d["person_id"].nunique()),
        "clusters": g,
    }


def local_year_discontinuity(s: pd.DataFrame, outcome: str, year: int, bandwidth: float = 0.5) -> dict:
    d = s[s["reference_year"].eq(year)].copy()
    d["running"] = d["monthly_fpl"] - 4.0
    d["above"] = d["monthly_fpl"].gt(4.0).astype(float)
    d["kernel"] = (1 - (d["running"].abs() / bandwidth)).clip(lower=0)
    d["analysis_weight"] = d["weight"] * d["kernel"]
    parts: list[pd.Series | pd.DataFrame] = [
        pd.Series(1.0, index=d.index, name="const"),
        d["above"].rename("above"),
        d["running"].rename("running"),
        (d["running"] * d["above"]).rename("running_x_above"),
        d["age"].rename("age"),
        d["female"].rename("female"),
        d["black"].rename("black"),
        d["hispanic"].rename("hispanic"),
        d["disabled"].rename("disabled"),
    ]
    x = add_fe(parts, d, ["reference_month", "state_fips"])
    beta, se_hc1, se_cluster, n, g = emp.wls_hc1_cluster(
        d[outcome].to_numpy(dtype=float),
        x.to_numpy(dtype=float),
        d["analysis_weight"].to_numpy(dtype=float),
        d["person_id"].to_numpy(),
    )
    b = pd.Series(beta, index=x.columns)
    cl = pd.Series(se_cluster, index=x.columns)
    return {
        "reference_year": year,
        "outcome": outcome,
        "coef_above": b.get("above", np.nan),
        "se_person_cluster": cl.get("above", np.nan),
        "t_person_cluster": b.get("above", np.nan) / cl.get("above", np.nan)
        if cl.get("above", np.nan) > 0
        else np.nan,
        "n": n,
        "persons": int(d["person_id"].nunique()),
    }


def binned_means(s: pd.DataFrame) -> pd.DataFrame:
    d = s[
        s["age"].between(26, 64, inclusive="both")
        & s["medicare"].ne(1)
        & s["monthly_fpl"].between(3.0, 5.0, inclusive="both")
        & s["weight"].gt(0)
    ].copy()
    d["period"] = np.where(d["reference_year"].le(2020), "pre_2017_2020", "post_2021_2023")
    d["fpl_bin_left"] = np.floor((d["monthly_fpl"] - 3.0) / 0.05) * 0.05 + 3.0
    d["fpl_bin_left"] = d["fpl_bin_left"].round(2)
    d["fpl_bin_mid"] = d["fpl_bin_left"] + 0.025
    rows = []
    for (period, bin_left), g in d.groupby(["period", "fpl_bin_left"], observed=True):
        row = {
            "period": period,
            "fpl_bin_left": float(bin_left),
            "fpl_bin_mid": float(g["fpl_bin_mid"].iloc[0]),
            "person_months": int(len(g)),
            "persons": int(g["person_id"].nunique()),
        }
        for outcome in OUTCOMES:
            row[outcome] = wmean(g[outcome], g["weight"])
        rows.append(row)
    return pd.DataFrame(rows).sort_values(["period", "fpl_bin_left"])


def make_plots(bins: pd.DataFrame) -> list[str]:
    paths = []
    try:
        import matplotlib.pyplot as plt
    except Exception:
        return paths
    for outcome in ["uninsured", "employer_private", "direct_purchase", "marketplace_flag"]:
        fig, ax = plt.subplots(figsize=(7, 4))
        for period, g in bins.groupby("period", observed=True):
            ax.plot(g["fpl_bin_mid"], g[outcome], marker="o", ms=2.5, lw=1, label=period)
        ax.axvline(4.0, color="black", lw=1, linestyle="--")
        ax.set_xlabel("Monthly family income / FPL")
        ax.set_ylabel(outcome)
        ax.set_title(f"ARPA 400% FPL RD bins: {outcome}")
        ax.legend(frameon=False)
        ax.grid(alpha=0.2)
        out = OUT / f"arpa400_rd_bins_{outcome}.png"
        fig.tight_layout()
        fig.savefig(out, dpi=160)
        plt.close(fig)
        paths.append(str(out.relative_to(ROOT)))
    return paths


def md_table(df: pd.DataFrame, cols: list[str]) -> str:
    lines = ["| " + " | ".join(cols) + " |", "|" + "|".join(["---"] * len(cols)) + "|"]
    for _, r in df[cols].iterrows():
        vals = []
        for c in cols:
            v = r[c]
            vals.append(f"{v:.4f}" if isinstance(v, float) else str(v))
        lines.append("| " + " | ".join(vals) + " |")
    return "\n".join(lines)


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    df = prepare_panel()
    main = df[
        df["age"].between(26, 64, inclusive="both")
        & df["medicare"].ne(1)
        & df["monthly_fpl"].between(3.5, 4.5, inclusive="both")
        & df["weight"].gt(0)
    ].copy()

    bins = binned_means(df)
    bins.to_csv(OUT / "arpa400_rd_bins.csv", index=False)
    plot_paths = make_plots(bins)

    year_rows = []
    for year in range(2017, 2024):
        for outcome in ["uninsured", "employer_private", "direct_purchase", "marketplace_flag", "market_or_subsidy"]:
            year_rows.append(local_year_discontinuity(main, outcome, year))
    yearly = pd.DataFrame(year_rows)
    yearly.to_csv(OUT / "arpa400_yearly_discontinuities.csv", index=False)

    age_rows = []
    age_specs = {
        "age_26_39": (26, 39),
        "age_40_49": (40, 49),
        "age_50_64": (50, 64),
    }
    for name, (lo, hi) in age_specs.items():
        ss = main[main["age"].between(lo, hi, inclusive="both")].copy()
        for outcome in ["uninsured", "employer_private", "direct_purchase", "marketplace_flag", "market_or_subsidy"]:
            age_rows.append(local_diffdisc(ss, outcome, name))
    age_est = pd.DataFrame(age_rows)
    age_est.to_csv(OUT / "arpa400_age_gradient_estimates.csv", index=False)

    pre_base = main[main["reference_year"].le(2020)].groupby("person_id", observed=True).agg(
        pre_months=("person_month_key", "size"),
        pre_any_employer=("employer_private", "max"),
    )
    eligible_ids = pre_base[(pre_base["pre_months"].ge(3)) & (pre_base["pre_any_employer"].eq(0))].index
    nonemp = main[main["person_id"].isin(eligible_ids)].copy()
    nonemp_rows = []
    for outcome in ["uninsured", "employer_private", "direct_purchase", "marketplace_flag", "market_or_subsidy"]:
        nonemp_rows.append(local_diffdisc(nonemp, outcome, "pre_nonemployer_baseline"))
    nonemp_est = pd.DataFrame(nonemp_rows)
    nonemp_est.to_csv(OUT / "arpa400_pre_nonemployer_estimates.csv", index=False)

    support = pd.DataFrame(
        [
            {
                "sample": "main_age26_64_bw050",
                "person_months": int(len(main)),
                "persons": int(main["person_id"].nunique()),
                "states": int(main["state_fips"].nunique()),
            },
            {
                "sample": "pre_nonemployer_baseline",
                "person_months": int(len(nonemp)),
                "persons": int(nonemp["person_id"].nunique()),
                "states": int(nonemp["state_fips"].nunique()),
            },
        ]
    )
    support.to_csv(OUT / "arpa400_diagnostics_support.csv", index=False)

    pre_yearly = yearly[yearly["reference_year"].le(2020)]
    post_yearly = yearly[yearly["reference_year"].ge(2021)]
    report = f"""# ARPA 400% FPL RD Diagnostics

## Purpose

This diagnostic pass tests whether the leading ARPA 400% FPL result looks like a clean subsidy-cliff
effect or a broader near-threshold private-coverage shift. It uses the augmented panel with
`RPRITYPE1` employer-related private coverage extracted from raw Census SIPP zips.

## Outputs

- `result/idea_scan/arpa400_rd_bins.csv`
- `result/idea_scan/arpa400_yearly_discontinuities.csv`
- `result/idea_scan/arpa400_age_gradient_estimates.csv`
- `result/idea_scan/arpa400_pre_nonemployer_estimates.csv`
- `result/idea_scan/arpa400_diagnostics_support.csv`

Generated plot files:

{chr(10).join(f"- `{p}`" for p in plot_paths) if plot_paths else "- Plot generation skipped because matplotlib was unavailable."}

## Support

{md_table(support, ['sample', 'person_months', 'persons', 'states'])}

## Year-Specific 400% FPL Discontinuities

These are within-year local linear discontinuities at 400% monthly FPL. They are not the final
diff-in-disc coefficient; they show whether jumps are already present before ARPA.

Pre-ARPA years 2017-2020:

{md_table(pre_yearly[pre_yearly['outcome'].isin(['uninsured', 'employer_private', 'direct_purchase', 'marketplace_flag'])], ['reference_year', 'outcome', 'coef_above', 'se_person_cluster', 't_person_cluster', 'persons'])}

Post-ARPA years 2021-2023:

{md_table(post_yearly[post_yearly['outcome'].isin(['uninsured', 'employer_private', 'direct_purchase', 'marketplace_flag'])], ['reference_year', 'outcome', 'coef_above', 'se_person_cluster', 't_person_cluster', 'persons'])}

## Age-Gradient Diff-in-Discontinuities

{md_table(age_est, ['model', 'outcome', 'coef', 'se_person_cluster', 't_person_cluster', 'persons'])}

## Pre-Period Non-Employer Baseline Sample

This restricts to people with at least three pre-2021 near-threshold months and no employer coverage
in those pre-period months. It is a selected robustness sample, not the primary design.

{md_table(nonemp_est, ['model', 'outcome', 'coef', 'se_person_cluster', 't_person_cluster', 'persons'])}

## Initial Interpretation

The yearly discontinuity and age-gradient checks are the decisive evidence for whether the 400% FPL
lead remains a clean cliff-removal paper. If employer coverage jumps are visible before ARPA or are
as large as Marketplace/direct-purchase jumps in the wrong age groups, the safer framing is a broader
ARPA-era private-coverage threshold response rather than a pure Marketplace cliff mechanism.
"""
    REPORT.write_text(report, encoding="utf-8")
    print(support.to_string(index=False))
    print(yearly.to_string(index=False))
    print(age_est.to_string(index=False))
    print(nonemp_est.to_string(index=False))


if __name__ == "__main__":
    main()
