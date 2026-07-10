from __future__ import annotations

from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[2]
IN = ROOT / "result" / "idea_scan"
OUT = IN / "arpa400_manuscript_package"


def fmt_num(value: object, digits: int = 4) -> str:
    if pd.isna(value):
        return ""
    try:
        x = float(value)
    except (TypeError, ValueError):
        return str(value)
    if abs(x) >= 1000 and x.is_integer():
        return f"{int(x):,}"
    return f"{x:+.{digits}f}" if x < 0 else f"{x:.{digits}f}"


def fmt_int(value: object) -> str:
    if pd.isna(value):
        return ""
    try:
        return f"{int(float(value)):,}"
    except (TypeError, ValueError):
        return str(value)


def markdown_table(df: pd.DataFrame, cols: list[str]) -> str:
    shown = df.loc[:, cols].copy()
    header = "| " + " | ".join(cols) + " |"
    sep = "| " + " | ".join(["---"] * len(cols)) + " |"
    rows = []
    for _, row in shown.iterrows():
        values = [str(row[col]) if not pd.isna(row[col]) else "" for col in cols]
        rows.append("| " + " | ".join(values) + " |")
    return "\n".join([header, sep, *rows]) + "\n"


def write_table(df: pd.DataFrame, stem: str, cols: list[str]) -> None:
    df.to_csv(OUT / f"{stem}.csv", index=False)
    (OUT / f"{stem}.md").write_text(markdown_table(df, cols), encoding="utf-8")


def table1_support() -> pd.DataFrame:
    d = pd.read_csv(IN / "arpa400_source_decomposition_support.csv")
    keep = [
        "main_age26_64",
        "lag_nonemployer_months",
        "lag_current_employer_months",
        "older_age50_64",
        "younger_age26_49",
    ]
    d = d[d["sample"].isin(keep)].copy()
    d["period"] = d["post"].map({0: "pre_2017_2020", 1: "post_2021_2023"})
    d["side"] = d["above400"].map({0: "below400", 1: "above400"})
    out = pd.DataFrame(
        {
            "sample": d["sample"],
            "period": d["period"],
            "side": d["side"],
            "person_months": d["person_months"].map(fmt_int),
            "persons": d["persons"].map(fmt_int),
            "states": d["states"].map(fmt_int),
            "uninsured": d["uninsured"].map(lambda x: fmt_num(x, 3)),
            "employer_source": d["source_employer_related"].map(lambda x: fmt_num(x, 3)),
            "bought_direct": d["source_bought_direct"].map(lambda x: fmt_num(x, 3)),
            "market_or_subsidy": d["market_or_subsidy"].map(lambda x: fmt_num(x, 3)),
        }
    )
    return out


def load_design() -> pd.DataFrame:
    return pd.read_csv(IN / "arpa400_paper_design_table.csv")


def format_estimates(d: pd.DataFrame) -> pd.DataFrame:
    out = d.copy()
    out["coef"] = out["coef"].map(lambda x: fmt_num(x, 4))
    out["se_person"] = out["se_person"].map(lambda x: fmt_num(x, 4))
    out["t_person"] = out["t_person"].map(lambda x: fmt_num(x, 2))
    out["se_state"] = out["se_state"].map(lambda x: fmt_num(x, 4))
    out["t_state"] = out["t_state"].map(lambda x: fmt_num(x, 2))
    out["n_person_months"] = out["n_person_months"].map(fmt_int)
    if "n_persons" in out.columns:
        out["n_persons"] = out["n_persons"].map(fmt_int)
    return out


def table2_primary() -> pd.DataFrame:
    d = load_design()
    d = d[d["panel"].eq("Primary source-decomposition, monthly FPL 350-450%")].copy()
    order = ["uninsured", "any_coverage", "market_or_subsidy", "direct_purchase", "source_employer_related"]
    d["sort"] = d["outcome"].map({x: i for i, x in enumerate(order)})
    d = d.sort_values("sort").drop(columns=["sort"])
    return format_estimates(d)


def table3_mechanism() -> pd.DataFrame:
    d = load_design()
    panels = [
        "Primary source-decomposition, monthly FPL 350-450%",
        "Mechanism sample: lagged non-employer",
        "Placebo/substitution sample: lagged current employer",
    ]
    outcomes = ["uninsured", "market_or_subsidy", "direct_purchase", "source_employer_related"]
    d = d[d["panel"].isin(panels) & d["outcome"].isin(outcomes)].copy()
    panel_order = {x: i for i, x in enumerate(panels)}
    outcome_order = {x: i for i, x in enumerate(outcomes)}
    d["panel_sort"] = d["panel"].map(panel_order)
    d["outcome_sort"] = d["outcome"].map(outcome_order)
    d = d.sort_values(["panel_sort", "outcome_sort"]).drop(columns=["panel_sort", "outcome_sort"])
    return format_estimates(d)


def table4_robustness_summary() -> pd.DataFrame:
    d = pd.read_csv(IN / "arpa400_robustness_summary.csv")
    keep_models = [
        "main_bandwidth",
        "lag_nonemployer_bandwidth",
        "main_donut_bw050",
        "lag_nonemployer_donut_bw050",
        "main_annual_fpl",
        "main_post_apr2021",
        "lag_nonemployer_post_apr2021",
        "placebo_thresholds",
        "pre_arpa_fake_policy",
        "lag_current_employer_bw050",
    ]
    keep_outcomes = ["uninsured", "market_or_subsidy", "direct_purchase", "source_employer_related"]
    d = d[d["model"].isin(keep_models) & d["outcome"].isin(keep_outcomes)].copy()
    order = {x: i for i, x in enumerate(keep_models)}
    d["sort"] = d["model"].map(order)
    d = d.sort_values(["sort", "outcome"]).drop(columns=["sort"])
    for col in ["median_coef", "min_coef", "max_coef", "share_negative", "share_positive"]:
        d[col] = d[col].map(lambda x: fmt_num(x, 4))
    for col in ["specs", "person_sig_specs", "state_sig_specs"]:
        d[col] = d[col].map(fmt_int)
    return d


def table5_placebo_falsification() -> pd.DataFrame:
    d = pd.read_csv(IN / "arpa400_robustness_estimates.csv")
    models = [
        "placebo_thresholds",
        "pre_arpa_fake_policy",
        "main_annual_fpl",
        "lag_current_employer_bw050",
    ]
    outcomes = ["uninsured", "market_or_subsidy", "direct_purchase", "source_employer_related"]
    d = d[d["model"].isin(models) & d["outcome"].isin(outcomes)].copy()
    order = {x: i for i, x in enumerate(models)}
    d["sort"] = d["model"].map(order)
    d = d.sort_values(["sort", "threshold", "post_col", "outcome"]).drop(columns=["sort"])
    keep = [
        "model",
        "outcome",
        "threshold",
        "bandwidth",
        "donut",
        "fpl_col",
        "post_col",
        "pre_only",
        "coef",
        "se_person_cluster",
        "t_person_cluster",
        "se_state_cluster",
        "t_state_cluster",
        "n_person_months",
        "n_persons",
        "n_state_clusters",
    ]
    d = d.loc[:, keep]
    for col in ["coef", "se_person_cluster", "t_person_cluster", "se_state_cluster", "t_state_cluster"]:
        d[col] = d[col].map(lambda x: fmt_num(x, 4 if "t_" not in col else 2))
    for col in ["n_person_months", "n_persons", "n_state_clusters"]:
        d[col] = d[col].map(fmt_int)
    return d


def figure_manifest() -> pd.DataFrame:
    rows = [
        {
            "figure": "Figure 1",
            "file": "sipp/result/idea_scan/arpa400_paper_bins_main.png",
            "use": "Binned uninsured and source means around 400% FPL, main sample.",
        },
        {
            "figure": "Figure 2",
            "file": "sipp/result/idea_scan/arpa400_paper_bins_lag_nonemployer.png",
            "use": "Binned mechanism plot for lagged non-employer sample.",
        },
        {
            "figure": "Figure 3",
            "file": "sipp/result/idea_scan/arpa400_paper_bins_lag_current_employer.png",
            "use": "Mechanism contrast for lagged current-employer sample.",
        },
        {
            "figure": "Figure 4",
            "file": "sipp/result/idea_scan/arpa400_bandwidth_robustness_coefficients.png",
            "use": "Bandwidth robustness coefficients for main and mechanism estimates.",
        },
    ]
    out = pd.DataFrame(rows)
    out["exists"] = out["file"].map(lambda p: (ROOT.parent / p).exists())
    return out


def write_readme() -> None:
    text = """# ARPA 400% FPL Manuscript Package

Status: CONDITIONAL GO.

This directory contains manuscript-ready filtered tables and figure manifests for the locked SIPP ARPA 400% FPL design. These outputs are derived from existing result CSVs only; this export script does not rerun models.

## Files

- `table1_support_cell_means.csv` / `.md`: support and weighted cell means by period and threshold side.
- `table2_primary_estimates.csv` / `.md`: locked primary local difference-in-discontinuities estimates.
- `table3_mechanism_decomposition.csv` / `.md`: full sample, lagged non-employer, and lagged current-employer mechanism comparison.
- `table4_robustness_summary.csv` / `.md`: bandwidth, donut, annual-FPL, timing, placebo, and fake-policy summaries.
- `table5_placebo_falsification.csv` / `.md`: row-level falsification and measurement-check estimates.
- `figure_manifest.csv` / `.md`: paths and intended uses for the four locked figures.

## Main Claim Discipline

Allowed: ARPA's removal of the 400% FPL subsidy cliff is associated with a local uninsured reduction near the threshold in SIPP monthly data.

Allowed: direct-market/subsidy mechanism evidence is strongest among lagged non-employer adults.

Not allowed: clean RDD, pure Marketplace enrollment effect, 2026 expiration effect, or older-adult headline effect.

## Minimum Web GPT Upload

Upload this README plus:

- `table2_primary_estimates.md`
- `table3_mechanism_decomposition.md`
- `table4_robustness_summary.md`
- `table5_placebo_falsification.md`
- `sipp/report/92_arpa_400fpl_paper_section_draft.md`
- `sipp/report/90_arpa_400fpl_specification_lock_and_identification_memo.md`
"""
    (OUT / "README.md").write_text(text, encoding="utf-8")


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)

    estimate_cols = ["panel", "outcome", "coef", "se_person", "t_person", "se_state", "t_state", "n_person_months"]
    robustness_cols = [
        "model",
        "outcome",
        "specs",
        "median_coef",
        "min_coef",
        "max_coef",
        "share_negative",
        "share_positive",
        "person_sig_specs",
        "state_sig_specs",
    ]
    falsification_cols = [
        "model",
        "outcome",
        "threshold",
        "fpl_col",
        "post_col",
        "coef",
        "se_person_cluster",
        "t_person_cluster",
        "se_state_cluster",
        "t_state_cluster",
        "n_person_months",
    ]

    write_table(
        table1_support(),
        "table1_support_cell_means",
        [
            "sample",
            "period",
            "side",
            "person_months",
            "persons",
            "states",
            "uninsured",
            "employer_source",
            "bought_direct",
            "market_or_subsidy",
        ],
    )
    write_table(table2_primary(), "table2_primary_estimates", estimate_cols)
    write_table(table3_mechanism(), "table3_mechanism_decomposition", estimate_cols)
    write_table(table4_robustness_summary(), "table4_robustness_summary", robustness_cols)
    write_table(table5_placebo_falsification(), "table5_placebo_falsification", falsification_cols)
    write_table(figure_manifest(), "figure_manifest", ["figure", "file", "exists", "use"])
    write_readme()

    print(f"Wrote manuscript package to {OUT}")


if __name__ == "__main__":
    main()
