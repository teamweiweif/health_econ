from __future__ import annotations

import importlib.util
from pathlib import Path

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "result" / "idea_scan"
REPORT = ROOT / "report" / "97_arpa_100150_nonexpansion_screen.md"
DECISION = ROOT / "report" / "98_fortyfirst_round_arpa_100150_nonexpansion_decision.md"
SOURCE_SCRIPT = ROOT / "script" / "11_idea_scan" / "40_arpa_400fpl_source_decomposition_test.py"
POLICY = ROOT / "data" / "policy" / "medicaid_expansion_state_month.csv"


spec = importlib.util.spec_from_file_location("arpa400_source", SOURCE_SCRIPT)
source = importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(source)


OUTCOMES = [
    "uninsured",
    "any_coverage",
    "market_or_subsidy",
    "direct_purchase",
    "marketplace_flag",
    "source_employer_related",
    "private",
    "public",
    "medicaid",
]


def load_panel() -> pd.DataFrame:
    d = source.add_constructs(source.read_augmented_panel())
    pol = pd.read_csv(POLICY, dtype={"state_fips": "string"})
    pol["state_fips"] = pol["state_fips"].astype("string").str.zfill(2)
    pol["reference_date"] = pd.to_datetime(pol["reference_date"])
    pol["reference_year"] = pol["reference_date"].dt.year
    pol["reference_month"] = pol["reference_date"].dt.month
    pol = pol[["state_fips", "reference_year", "reference_month", "expansion_state_month"]].copy()
    d = d.merge(pol, on=["state_fips", "reference_year", "reference_month"], how="left", validate="many_to_one")
    d["expansion_state_month"] = pd.to_numeric(d["expansion_state_month"], errors="coerce")
    d["nonexpansion"] = d["expansion_state_month"].eq(0).astype(float)
    d["low_100_150"] = d["monthly_fpl"].between(1.0, 1.5, inclusive="left").astype(float)
    d["mid_150_200"] = d["monthly_fpl"].between(1.5, 2.0, inclusive="left").astype(float)
    d["band_100_200"] = d["monthly_fpl"].between(1.0, 2.0, inclusive="left")
    d["band_125_175"] = d["monthly_fpl"].between(1.25, 1.75, inclusive="both")
    return d[
        d["age"].between(26, 64, inclusive="both")
        & d["medicare"].lt(0.5)
        & d["monthly_fpl"].between(0.75, 2.5, inclusive="both")
        & d["weight"].gt(0)
        & d["expansion_state_month"].notna()
    ].copy()


def wmean(y: pd.Series, w: pd.Series) -> float:
    mask = y.notna() & w.notna() & w.gt(0)
    if not mask.any():
        return np.nan
    return float(np.average(y[mask].astype(float), weights=w[mask].astype(float)))


def add_intercept_fe(parts: list[pd.Series | pd.DataFrame], d: pd.DataFrame) -> pd.DataFrame:
    parts = [pd.Series(1.0, index=d.index, name="const"), *parts]
    return source.add_fe(parts, d, ["reference_year", "reference_month", "state_fips"])


def estimate(
    d: pd.DataFrame,
    outcome: str,
    model: str,
    term: str,
    x: pd.DataFrame,
) -> dict[str, object]:
    beta, se_hc1, se_person, se_state, nobs, g_person, g_state = source.weighted_ols_two_clusters(
        d[outcome].to_numpy(float),
        x.to_numpy(float),
        d["analysis_weight"].to_numpy(float),
        d["person_id"].astype("string").to_numpy(),
        d["state_fips"].astype("string").to_numpy(),
    )
    idx = list(x.columns).index(term)
    return {
        "model": model,
        "outcome": outcome,
        "term": term,
        "coef": beta[idx],
        "se_hc1": se_hc1[idx],
        "t_hc1": beta[idx] / se_hc1[idx] if se_hc1[idx] else np.nan,
        "se_person_cluster": se_person[idx],
        "t_person_cluster": beta[idx] / se_person[idx] if se_person[idx] else np.nan,
        "se_state_cluster": se_state[idx],
        "t_state_cluster": beta[idx] / se_state[idx] if se_state[idx] else np.nan,
        "n_person_months": nobs,
        "n_persons": source.persons(d["person_id"]),
        "n_state_clusters": g_state,
    }


def ddd_model(d: pd.DataFrame, outcome: str) -> dict[str, object]:
    s = d[d["band_100_200"]].copy()
    s["analysis_weight"] = s["weight"]
    s["post"] = s["post_year2021"]
    s["low"] = s["low_100_150"]
    s["nonexp"] = s["nonexpansion"]
    s["low_post"] = s["low"] * s["post"]
    s["low_nonexp"] = s["low"] * s["nonexp"]
    s["post_nonexp"] = s["post"] * s["nonexp"]
    s["low_post_nonexp"] = s["low"] * s["post"] * s["nonexp"]
    s["running150"] = s["monthly_fpl"] - 1.5
    parts = [
        s["low"].rename("low"),
        s["low_post"].rename("low_post"),
        s["low_nonexp"].rename("low_nonexp"),
        s["post_nonexp"].rename("post_nonexp"),
        s["low_post_nonexp"].rename("low_post_nonexp"),
        s["running150"].rename("running150"),
        s["age"].rename("age"),
        s["female"].rename("female"),
        s["black"].rename("black"),
        s["hispanic"].rename("hispanic"),
        s["disabled"].rename("disabled"),
    ]
    x = add_intercept_fe(parts, s)
    return estimate(s, outcome, "ddd_nonexp_low100150_vs_150200_all_states", "low_post_nonexp", x)


def nonexp_local_150_model(d: pd.DataFrame, outcome: str, bandwidth: float = 0.50) -> dict[str, object]:
    s = d[d["nonexpansion"].eq(1) & d["monthly_fpl"].between(1.5 - bandwidth, 1.5 + bandwidth, inclusive="both")].copy()
    s["running150"] = s["monthly_fpl"] - 1.5
    s["below150"] = s["monthly_fpl"].lt(1.5).astype(float)
    s["post"] = s["post_year2021"]
    s["below_post"] = s["below150"] * s["post"]
    s["running_below"] = s["running150"] * s["below150"]
    s["running_post"] = s["running150"] * s["post"]
    s["running_below_post"] = s["running150"] * s["below150"] * s["post"]
    s["kernel"] = (1 - (s["running150"].abs() / bandwidth)).clip(lower=0)
    s["analysis_weight"] = s["weight"] * s["kernel"]
    parts = [
        s["below150"].rename("below150"),
        s["post"].rename("post"),
        s["below_post"].rename("below_post"),
        s["running150"].rename("running150"),
        s["running_below"].rename("running_below"),
        s["running_post"].rename("running_post"),
        s["running_below_post"].rename("running_below_post"),
        s["age"].rename("age"),
        s["female"].rename("female"),
        s["black"].rename("black"),
        s["hispanic"].rename("hispanic"),
        s["disabled"].rename("disabled"),
    ]
    x = add_intercept_fe(parts, s)
    out = estimate(s, outcome, f"nonexp_local150_bw{bandwidth:.2f}", "below_post", x)
    out["bandwidth"] = bandwidth
    return out


def expansion_local_150_placebo(d: pd.DataFrame, outcome: str, bandwidth: float = 0.50) -> dict[str, object]:
    s = d[d["expansion_state_month"].eq(1) & d["monthly_fpl"].between(1.5 - bandwidth, 1.5 + bandwidth, inclusive="both")].copy()
    s["running150"] = s["monthly_fpl"] - 1.5
    s["below150"] = s["monthly_fpl"].lt(1.5).astype(float)
    s["post"] = s["post_year2021"]
    s["below_post"] = s["below150"] * s["post"]
    s["running_below"] = s["running150"] * s["below150"]
    s["running_post"] = s["running150"] * s["post"]
    s["running_below_post"] = s["running150"] * s["below150"] * s["post"]
    s["kernel"] = (1 - (s["running150"].abs() / bandwidth)).clip(lower=0)
    s["analysis_weight"] = s["weight"] * s["kernel"]
    parts = [
        s["below150"].rename("below150"),
        s["post"].rename("post"),
        s["below_post"].rename("below_post"),
        s["running150"].rename("running150"),
        s["running_below"].rename("running_below"),
        s["running_post"].rename("running_post"),
        s["running_below_post"].rename("running_below_post"),
        s["age"].rename("age"),
        s["female"].rename("female"),
        s["black"].rename("black"),
        s["hispanic"].rename("hispanic"),
        s["disabled"].rename("disabled"),
    ]
    x = add_intercept_fe(parts, s)
    out = estimate(s, outcome, f"expansion_local150_placebo_bw{bandwidth:.2f}", "below_post", x)
    out["bandwidth"] = bandwidth
    return out


def support_table(d: pd.DataFrame) -> pd.DataFrame:
    s = d[d["band_100_200"]].copy()
    rows = []
    for (nonexp, post, band), g in s.groupby(
        [
            s["nonexpansion"].astype(int),
            s["post_year2021"].astype(int),
            np.where(s["low_100_150"].eq(1), "100_150", "150_200"),
        ],
        observed=True,
    ):
        row = {
            "nonexpansion": nonexp,
            "post": post,
            "income_band": band,
            "person_months": len(g),
            "persons": source.persons(g["person_id"]),
            "states": source.persons(g["state_fips"]),
        }
        for outcome in OUTCOMES:
            row[outcome] = wmean(g[outcome], g["weight"])
        rows.append(row)
    return pd.DataFrame(rows).sort_values(["nonexpansion", "income_band", "post"])


def write_report(support: pd.DataFrame, estimates: pd.DataFrame) -> None:
    def md_table(df: pd.DataFrame, cols: list[str], max_rows: int = 80) -> str:
        x = df.loc[:, cols].head(max_rows).copy()
        formatted = x.copy()
        for col in formatted.columns:
            if pd.api.types.is_numeric_dtype(formatted[col]):
                formatted[col] = formatted[col].map(
                    lambda v: "" if pd.isna(v) else (f"{int(v):d}" if float(v).is_integer() else f"{float(v):.4f}")
                )
            else:
                formatted[col] = formatted[col].fillna("").astype(str)
        header = "| " + " | ".join(formatted.columns) + " |"
        sep = "| " + " | ".join(["---"] * len(formatted.columns)) + " |"
        body = [
            "| " + " | ".join(str(row[col]) for col in formatted.columns) + " |"
            for _, row in formatted.iterrows()
        ]
        return "\n".join([header, sep, *body])

    key = estimates[
        estimates["outcome"].isin(["uninsured", "market_or_subsidy", "direct_purchase", "medicaid"])
    ].copy()
    lines = [
        "# ARPA 100-150% FPL Non-Expansion State Screen",
        "",
        "## Purpose",
        "",
        "This screen evaluates the backup idea that ARPA's zero-premium / near-zero-premium Marketplace environment improved coverage among adults at 100-150% FPL in non-expansion states.",
        "",
        "Policy hook: CMS states that many consumers with incomes from 100% to 150% FPL would have $0 premium plans after ARPA tax credits. The current 2026 enhanced-PTC expiration debate makes this margin policy-relevant again.",
        "",
        "## Data and Sample",
        "",
        "- SIPP person-month panel, reference years 2017-2023.",
        "- Adults age 26-64, non-Medicare.",
        "- Monthly family FPL 100-200% for DDD support and models.",
        "- Medicaid expansion status merged from `data/policy/medicaid_expansion_state_month.csv`.",
        "- Outcomes use the same coverage/source definitions as the ARPA400 source-decomposition scripts.",
        "",
        "## Support and Raw Means",
        "",
        md_table(
            support,
            [
                "nonexpansion",
                "post",
                "income_band",
                "person_months",
                "persons",
                "states",
                "uninsured",
                "market_or_subsidy",
                "direct_purchase",
                "marketplace_flag",
                "medicaid",
            ],
        ),
        "",
        "## Screen Estimates",
        "",
        "Key terms:",
        "",
        "- DDD: `low_100_150 x post2021 x nonexpansion` among 100-200% FPL adults.",
        "- Non-expansion local 150% model: `below150 x post2021` within a local window around 150% FPL.",
        "- Expansion local 150% model: same local threshold model, used as a placebo/contrast.",
        "",
        md_table(
            key,
            [
                "model",
                "outcome",
                "term",
                "coef",
                "se_person_cluster",
                "t_person_cluster",
                "se_state_cluster",
                "t_state_cluster",
                "n_person_months",
                "n_state_clusters",
            ],
            max_rows=100,
        ),
        "",
        "## Interpretation",
        "",
        "This backup idea is policy-relevant, but the screen is designed to be stricter than raw pre/post means. A strong backup would need:",
        "",
        "- lower uninsured or higher any coverage in the non-expansion 100-150% group;",
        "- positive `market_or_subsidy` or direct-purchase movement;",
        "- a pattern stronger than the expansion-state local placebo;",
        "- enough state clusters and cell support.",
        "",
        "The decision memo records whether the idea is a backup conditional go or should be downgraded.",
        "",
        "## Artifacts",
        "",
        "- `sipp/script/11_idea_scan/44_arpa_100150_nonexpansion_screen.py`",
        "- `sipp/result/idea_scan/arpa100150_nonexpansion_support.csv`",
        "- `sipp/result/idea_scan/arpa100150_nonexpansion_estimates.csv`",
    ]
    REPORT.write_text("\n".join(lines), encoding="utf-8")


def write_decision(support: pd.DataFrame, estimates: pd.DataFrame) -> None:
    def pick(model: str, outcome: str) -> pd.Series | None:
        r = estimates[estimates["model"].eq(model) & estimates["outcome"].eq(outcome)]
        return None if r.empty else r.iloc[0]

    ddd_unins = pick("ddd_nonexp_low100150_vs_150200_all_states", "uninsured")
    ddd_market = pick("ddd_nonexp_low100150_vs_150200_all_states", "market_or_subsidy")
    local_unins = pick("nonexp_local150_bw0.50", "uninsured")
    local_market = pick("nonexp_local150_bw0.50", "market_or_subsidy")
    placebo_unins = pick("expansion_local150_placebo_bw0.50", "uninsured")

    def fmt(r: pd.Series | None) -> str:
        if r is None:
            return "missing"
        return (
            f"{r['coef']:+.4f}, person t {r['t_person_cluster']:+.2f}, "
            f"state t {r['t_state_cluster']:+.2f}, N {int(r['n_person_months']):,}"
        )

    nonexp_low = support[
        support["nonexpansion"].eq(1) & support["income_band"].eq("100_150")
    ].copy()
    pre = nonexp_low[nonexp_low["post"].eq(0)].iloc[0] if (nonexp_low["post"].eq(0)).any() else None
    post = nonexp_low[nonexp_low["post"].eq(1)].iloc[0] if (nonexp_low["post"].eq(1)).any() else None

    raw_line = "missing"
    if pre is not None and post is not None:
        raw_line = (
            f"non-expansion 100-150 raw uninsured {pre['uninsured']:.1%} to {post['uninsured']:.1%}; "
            f"market/subsidy {pre['market_or_subsidy']:.1%} to {post['market_or_subsidy']:.1%}; "
            f"N pre {int(pre['person_months']):,}, post {int(post['person_months']):,}"
        )

    verdict = "BACKUP ONLY / WEAK CONDITIONAL"
    if ddd_market is not None and local_market is not None:
        if ddd_market["coef"] > 0 and local_market["coef"] > 0:
            verdict = "BACKUP CONDITIONAL GO"
        if ddd_market["coef"] <= 0 and local_market["coef"] <= 0:
            verdict = "DOWNGRADE AS MAIN BACKUP"

    lines = [
        "# Forty-First Round Decision: ARPA 100-150% FPL Non-Expansion Screen",
        "",
        "## Verdict",
        "",
        f"`{verdict}`",
        "",
        "This idea remains policy-relevant because ARPA made zero-premium / near-zero-premium Marketplace coverage available to many 100-150% FPL adults, and the 2026 enhanced-PTC expiration debate directly revisits this affordability margin.",
        "",
        "However, it is weaker than the ARPA400 lead because the identifying contrast is less clean. The 100-150 group in non-expansion states is highly policy-relevant, but comparisons against 150-200% FPL or expansion states are both contaminated by other ACA/ARPA subsidy and Medicaid eligibility differences.",
        "",
        "## Raw Non-Expansion Pattern",
        "",
        f"- {raw_line}.",
        "",
        "## Key Estimates",
        "",
        f"- DDD uninsured: {fmt(ddd_unins)}.",
        f"- DDD market/subsidy: {fmt(ddd_market)}.",
        f"- Non-expansion local 150 uninsured: {fmt(local_unins)}.",
        f"- Non-expansion local 150 market/subsidy: {fmt(local_market)}.",
        f"- Expansion local 150 placebo uninsured: {fmt(placebo_unins)}.",
        "",
        "## Decision Rule",
        "",
        "Promote only if the non-expansion 100-150 group shows both coverage improvement and direct-market/subsidy uptake that is stronger than the expansion-state threshold placebo.",
        "",
        "Do not promote if the signal is mostly raw pre/post, if the local 150 design is weak, or if the expansion placebo is equally strong.",
        "",
        "## Current Ranking",
        "",
        "1. ARPA 400% FPL cliff removal: current lead, conditional go.",
        "2. ARPA 100-150% FPL non-expansion zero-premium margin: backup only unless this screen shows clean mechanism and contrast evidence.",
        "",
        "## Artifacts",
        "",
        "- `sipp/report/97_arpa_100150_nonexpansion_screen.md`",
        "- `sipp/result/idea_scan/arpa100150_nonexpansion_support.csv`",
        "- `sipp/result/idea_scan/arpa100150_nonexpansion_estimates.csv`",
    ]
    DECISION.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    panel = load_panel()
    support = support_table(panel)
    rows = []
    for outcome in OUTCOMES:
        rows.append(ddd_model(panel, outcome))
        rows.append(nonexp_local_150_model(panel, outcome, bandwidth=0.50))
        rows.append(nonexp_local_150_model(panel, outcome, bandwidth=0.25))
        rows.append(expansion_local_150_placebo(panel, outcome, bandwidth=0.50))
    estimates = pd.DataFrame(rows)
    support.to_csv(OUT / "arpa100150_nonexpansion_support.csv", index=False)
    estimates.to_csv(OUT / "arpa100150_nonexpansion_estimates.csv", index=False)
    write_report(support, estimates)
    write_decision(support, estimates)
    print(f"Wrote {REPORT}")
    print(f"Wrote {DECISION}")


if __name__ == "__main__":
    main()
