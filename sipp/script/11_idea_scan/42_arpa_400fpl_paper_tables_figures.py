from __future__ import annotations

import importlib.util
from pathlib import Path

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "result" / "idea_scan"
REPORT = ROOT / "report" / "84_arpa_400fpl_paper_tables_figures.md"
DECISION = ROOT / "report" / "85_thirtyfourth_round_arpa_400fpl_paper_readiness.md"
SOURCE_SCRIPT = ROOT / "script" / "11_idea_scan" / "40_arpa_400fpl_source_decomposition_test.py"


spec = importlib.util.spec_from_file_location("arpa400_source", SOURCE_SCRIPT)
source = importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(source)


MAIN_OUTCOMES = ["uninsured", "market_or_subsidy", "source_employer_related", "direct_purchase"]


def wmean(y: pd.Series, w: pd.Series) -> float:
    mask = y.notna() & w.notna() & w.gt(0)
    if not mask.any():
        return np.nan
    return float(np.average(y[mask].astype(float), weights=w[mask].astype(float)))


def build_panel() -> pd.DataFrame:
    d = source.add_constructs(source.read_augmented_panel())
    return d[
        d["age"].between(26, 64, inclusive="both")
        & d["medicare"].lt(0.5)
        & d["monthly_fpl"].between(3.0, 5.0, inclusive="both")
        & d["weight"].gt(0)
    ].copy()


def binned_means(panel: pd.DataFrame) -> pd.DataFrame:
    samples = {
        "main_age26_64": panel,
        "lag_nonemployer": panel[panel["lag_source_employer_related"].eq(0)].copy(),
        "lag_current_employer": panel[panel["lag_source_current_employer"].eq(1)].copy(),
    }
    rows = []
    for sample_name, s in samples.items():
        d = s.copy()
        d["period"] = np.where(d["reference_year"].le(2020), "pre_2017_2020", "post_2021_2023")
        d["bin_left"] = np.floor((d["monthly_fpl"] - 3.0) / 0.05) * 0.05 + 3.0
        d["bin_left"] = d["bin_left"].round(2)
        d = d[d["bin_left"].lt(5.0)].copy()
        d["bin_mid"] = d["bin_left"] + 0.025
        for (period, bin_left), g in d.groupby(["period", "bin_left"], observed=True):
            row = {
                "sample": sample_name,
                "period": period,
                "bin_left": float(bin_left),
                "bin_mid": float(g["bin_mid"].iloc[0]),
                "person_months": int(len(g)),
                "persons": source.persons(g["person_id"]),
            }
            for outcome in MAIN_OUTCOMES:
                row[outcome] = wmean(g[outcome], g["weight"])
            rows.append(row)
    return pd.DataFrame(rows).sort_values(["sample", "period", "bin_left"])


def load_design_rows() -> pd.DataFrame:
    source_est = pd.read_csv(OUT / "arpa400_source_decomposition_estimates.csv")
    robust = pd.read_csv(OUT / "arpa400_robustness_estimates.csv")

    rows = []

    def add_from(df: pd.DataFrame, label: str, model: str, outcomes: list[str], **filters: object) -> None:
        d = df[df["model"].eq(model)].copy()
        for key, value in filters.items():
            if value is None:
                continue
            if isinstance(value, float):
                d = d[np.isclose(pd.to_numeric(d[key], errors="coerce"), value)]
            else:
                d = d[d[key].astype(str).eq(str(value))]
        for outcome in outcomes:
            r = d[d["outcome"].eq(outcome)]
            if r.empty:
                continue
            row = r.iloc[0].to_dict()
            rows.append(
                {
                    "panel": label,
                    "model": model,
                    "outcome": outcome,
                    "coef": float(row.get("coef", np.nan)),
                    "se_person": float(row.get("se_person_cluster", np.nan)),
                    "t_person": float(row.get("t_person_cluster", np.nan)),
                    "se_state": float(row.get("se_state_cluster", np.nan)),
                    "t_state": float(row.get("t_state_cluster", np.nan)),
                    "n_person_months": int(float(row.get("n_person_months", np.nan))),
                    "n_persons": int(float(row.get("n_persons", np.nan))) if "n_persons" in row else np.nan,
                    "bandwidth": row.get("bandwidth", ""),
                    "donut": row.get("donut", ""),
                    "threshold": row.get("threshold", ""),
                    "post_col": row.get("post_col", ""),
                }
            )

    add_from(
        source_est,
        "Primary source-decomposition, monthly FPL 350-450%",
        "main_age26_64",
        ["uninsured", "any_coverage", "market_or_subsidy", "direct_purchase", "source_employer_related"],
    )
    add_from(
        source_est,
        "Mechanism sample: lagged non-employer",
        "lag_nonemployer_months",
        ["uninsured", "market_or_subsidy", "direct_purchase", "source_employer_related"],
    )
    add_from(
        source_est,
        "Placebo/substitution sample: lagged current employer",
        "lag_current_employer_months",
        ["uninsured", "market_or_subsidy", "direct_purchase", "source_employer_related"],
    )
    add_from(
        robust,
        "Robustness: main donut 0.05",
        "main_donut_bw050",
        ["uninsured", "market_or_subsidy"],
        donut=0.05,
    )
    add_from(
        robust,
        "Robustness: annual FPL bw 0.50",
        "main_annual_fpl",
        ["uninsured", "market_or_subsidy"],
        bandwidth=0.50,
    )
    add_from(
        robust,
        "Placebo threshold 3.5 FPL",
        "placebo_thresholds",
        ["uninsured", "market_or_subsidy"],
        threshold=3.5,
    )
    add_from(
        robust,
        "Pre-ARPA fake policy 2020",
        "pre_arpa_fake_policy",
        ["uninsured", "market_or_subsidy"],
        post_col="fake_post_2020",
    )

    out = pd.DataFrame(rows)
    out["stars_person"] = out["t_person"].abs().map(lambda t: "***" if t >= 2.58 else "**" if t >= 1.96 else "*" if t >= 1.64 else "")
    out["stars_state"] = out["t_state"].abs().map(lambda t: "***" if t >= 2.58 else "**" if t >= 1.96 else "*" if t >= 1.64 else "")
    out["coef_fmt"] = out.apply(
        lambda r: f"{r['coef']:+.4f}{r['stars_person']} ({r['se_person']:.4f})",
        axis=1,
    )
    return out


def make_binned_plot(bins: pd.DataFrame, sample: str, outcomes: list[str], out_name: str) -> Path | None:
    try:
        import matplotlib.pyplot as plt
    except Exception:
        return None

    labels = {
        "uninsured": "Uninsured",
        "market_or_subsidy": "Marketplace / subsidy proxy",
        "source_employer_related": "Employer-related source",
        "direct_purchase": "Direct purchase",
    }
    fig, axes = plt.subplots(2, 2, figsize=(9.5, 6.8), sharex=True)
    axes = axes.ravel()
    d = bins[bins["sample"].eq(sample)].copy()
    for ax, outcome in zip(axes, outcomes):
        for period, g in d.groupby("period", observed=True):
            g = g.sort_values("bin_mid")
            ax.plot(
                g["bin_mid"],
                g[outcome],
                marker="o",
                markersize=2.5,
                linewidth=1.4,
                label="Pre-ARPA" if period.startswith("pre") else "Post-ARPA",
            )
        ax.axvline(4.0, color="black", linestyle="--", linewidth=1)
        ax.set_title(labels.get(outcome, outcome), fontsize=10)
        ax.grid(alpha=0.2)
        ax.set_ylabel("Weighted mean")
    axes[-1].set_xlabel("Monthly family income / FPL")
    axes[-2].set_xlabel("Monthly family income / FPL")
    handles, labels_ = axes[0].get_legend_handles_labels()
    fig.legend(handles, labels_, loc="lower center", ncol=2, frameon=False, bbox_to_anchor=(0.5, 0.0))
    fig.suptitle(f"ARPA 400% FPL binned means: {sample}", y=0.995, fontsize=12)
    fig.tight_layout(rect=(0, 0.05, 1, 0.95))
    out = OUT / out_name
    fig.savefig(out, dpi=170)
    plt.close(fig)
    return out


def make_coef_plot() -> Path | None:
    try:
        import matplotlib.pyplot as plt
    except Exception:
        return None
    est = pd.read_csv(OUT / "arpa400_robustness_estimates.csv")
    d = est[
        est["model"].isin(["main_bandwidth", "lag_nonemployer_bandwidth"])
        & est["outcome"].isin(["uninsured", "market_or_subsidy"])
    ].copy()
    d["ci_lo"] = d["coef"] - 1.96 * d["se_state_cluster"]
    d["ci_hi"] = d["coef"] + 1.96 * d["se_state_cluster"]
    fig, ax = plt.subplots(figsize=(8.5, 4.8))
    style = {
        ("main_bandwidth", "uninsured"): ("Main uninsured", "tab:blue", "o"),
        ("main_bandwidth", "market_or_subsidy"): ("Main market/subsidy", "tab:orange", "s"),
        ("lag_nonemployer_bandwidth", "uninsured"): ("Lag non-employer uninsured", "tab:green", "^"),
        ("lag_nonemployer_bandwidth", "market_or_subsidy"): ("Lag non-employer market/subsidy", "tab:red", "D"),
    }
    for key, g in d.groupby(["model", "outcome"], observed=True):
        label, color, marker = style[key]
        g = g.sort_values("bandwidth")
        ax.plot(g["bandwidth"], g["coef"], marker=marker, color=color, linewidth=1.5, label=label)
        ax.fill_between(g["bandwidth"], g["ci_lo"], g["ci_hi"], color=color, alpha=0.12)
    ax.axhline(0, color="black", linewidth=1)
    ax.set_xlabel("Bandwidth around 400% FPL")
    ax.set_ylabel("Coefficient: above 400% FPL x post-2021")
    ax.set_title("ARPA 400% FPL bandwidth robustness")
    ax.grid(alpha=0.2)
    ax.legend(frameon=False, fontsize=8, ncol=2)
    fig.tight_layout()
    out = OUT / "arpa400_bandwidth_robustness_coefficients.png"
    fig.savefig(out, dpi=170)
    plt.close(fig)
    return out


def md_table(df: pd.DataFrame, cols: list[str], max_rows: int = 40) -> str:
    d = df[cols].head(max_rows)
    lines = ["| " + " | ".join(cols) + " |", "|" + "|".join(["---"] * len(cols)) + "|"]
    for _, r in d.iterrows():
        vals = []
        for c in cols:
            v = r[c]
            vals.append(f"{v:.4f}" if isinstance(v, float) else str(v))
        lines.append("| " + " | ".join(vals) + " |")
    return "\n".join(lines)


def write_outputs(bins: pd.DataFrame, table: pd.DataFrame, plots: list[Path]) -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    bins.to_csv(OUT / "arpa400_paper_binned_means.csv", index=False)
    table.to_csv(OUT / "arpa400_paper_design_table.csv", index=False)

    table_short = table[
        [
            "panel",
            "outcome",
            "coef_fmt",
            "t_person",
            "t_state",
            "n_person_months",
        ]
    ].copy()
    report = [
        "# ARPA 400% FPL Paper Tables and Figures",
        "",
        "## Purpose",
        "",
        "This file converts the idea-screen estimates into paper-facing artifacts: a compact design table, binned RD-style plots, and a bandwidth coefficient plot.",
        "",
        "## Paper Design Table",
        "",
        "Coefficient format is coefficient with person-cluster standard error in parentheses. Stars use person-cluster t-statistics.",
        "",
        md_table(table_short, ["panel", "outcome", "coef_fmt", "t_person", "t_state", "n_person_months"], max_rows=32),
        "",
        "## Generated Figures",
        "",
    ]
    report += [f"- `{p.relative_to(ROOT)}`" for p in plots]
    report += [
        "",
        "## Read for Writing",
        "",
        "- Main uninsured is the headline outcome.",
        "- Lagged non-employer market/subsidy is the cleanest mechanism figure and should be shown before any broad Marketplace claim.",
        "- Lagged current-employer patterns should be used as a mechanism contrast, not as proof of treatment irrelevance.",
        "- Placebo and annual-FPL rows must stay in the table because they define the conditional nature of the go decision.",
        "",
        "## Artifacts",
        "",
        "- `script/11_idea_scan/42_arpa_400fpl_paper_tables_figures.py`",
        "- `report/84_arpa_400fpl_paper_tables_figures.md`",
        "- `report/85_thirtyfourth_round_arpa_400fpl_paper_readiness.md`",
        "- `result/idea_scan/arpa400_paper_design_table.csv`",
        "- `result/idea_scan/arpa400_paper_binned_means.csv`",
    ]
    REPORT.write_text("\n".join(report) + "\n", encoding="utf-8")

    decision = [
        "# Thirty-Fourth Round Decision: ARPA 400% FPL Paper Readiness",
        "",
        "## Verdict",
        "",
        "`READY FOR A PAPER-STYLE DESIGN MEMO; NOT YET FINAL CLAIM`",
        "",
        "The project now has the minimum visual and tabular evidence needed to move from idea screening into a structured paper design memo.",
        "",
        "## What the Figures Should Show",
        "",
        "- Main binned uninsured plot: above-400 post-ARPA discontinuity should visibly move downward relative to pre-ARPA.",
        "- Lagged non-employer plot: market/subsidy should rise around the threshold, while employer-source movement should not explain the response.",
        "- Bandwidth coefficient plot: main uninsured should stay negative and lagged non-employer market/subsidy should stay positive across bandwidths.",
        "",
        "## Remaining Weaknesses",
        "",
        "- Annual-FPL direct-market mechanism is weak.",
        "- The older-adult gradient is not supportive.",
        "- Placebo thresholds are not empty enough to claim a fully clean design without caveats.",
        "",
        "## Next Step",
        "",
        "Write a single consolidated design memo that states the estimand, primary sample, primary bandwidth, secondary mechanism sample, all robustness checks, and exact no-go triggers before further tuning.",
    ]
    DECISION.write_text("\n".join(decision) + "\n", encoding="utf-8")


def main() -> None:
    panel = build_panel()
    bins = binned_means(panel)
    table = load_design_rows()
    plots: list[Path] = []
    for maybe in [
        make_binned_plot(bins, "main_age26_64", MAIN_OUTCOMES, "arpa400_paper_bins_main.png"),
        make_binned_plot(bins, "lag_nonemployer", MAIN_OUTCOMES, "arpa400_paper_bins_lag_nonemployer.png"),
        make_binned_plot(bins, "lag_current_employer", MAIN_OUTCOMES, "arpa400_paper_bins_lag_current_employer.png"),
        make_coef_plot(),
    ]:
        if maybe is not None:
            plots.append(maybe)
    write_outputs(bins, table, plots)
    print(f"Wrote {REPORT}")
    print(f"Wrote {DECISION}")
    print(table[["panel", "outcome", "coef", "se_person", "t_person", "se_state", "t_state", "n_person_months"]].to_string(index=False))
    for p in plots:
        print(p)


if __name__ == "__main__":
    main()
