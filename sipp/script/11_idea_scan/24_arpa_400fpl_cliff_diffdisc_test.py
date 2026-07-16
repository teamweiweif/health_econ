from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[2]
PANEL = ROOT / "data" / "analysis_ready" / "sipp_2018_2024_person_month_panel.parquet"
OUT = ROOT / "result" / "idea_scan"
REPORT = ROOT / "report" / "50_arpa_400fpl_cliff_diffdisc_test.md"


SOURCES = [
    "CMS American Rescue Plan and the Marketplace: https://www.cms.gov/newsroom/fact-sheets/american-rescue-plan-and-marketplace",
    "IRS Premium Tax Credit eligibility: https://www.irs.gov/affordable-care-act/individuals-and-families/eligibility-for-the-premium-tax-credit",
    "KFF 2026 Marketplace enrollment/premiums/deductibles: https://www.kff.org/affordable-care-act/what-we-know-so-far-about-2026-aca-marketplace-enrollment-premiums-and-deductibles/",
    "KFF enhanced PTC expiration premium-payment analysis: https://www.kff.org/affordable-care-act/aca-marketplace-premium-payments-would-more-than-double-on-average-next-year-if-enhanced-premium-tax-credits-expire/",
]


def yes(s: pd.Series) -> pd.Series:
    return s.eq(1)


def clean_weight(df: pd.DataFrame) -> pd.Series:
    w = pd.to_numeric(df.get("WPFINWGT"), errors="coerce")
    return w.where(w.gt(0))


def bounded_numeric(s: pd.Series, lo: float, hi: float) -> pd.Series:
    out = pd.to_numeric(s, errors="coerce")
    return out.where(out.between(lo, hi, inclusive="both"))


def wmean(y: pd.Series, w: pd.Series) -> float:
    mask = y.notna() & w.notna() & (w > 0)
    if not mask.any():
        return np.nan
    return float(np.average(y[mask].astype(float), weights=w[mask].astype(float)))


def wls_hc1_cluster(
    y: np.ndarray,
    x: np.ndarray,
    w: np.ndarray,
    cluster: np.ndarray,
) -> tuple[np.ndarray, np.ndarray, np.ndarray, int, int]:
    mask = np.isfinite(y) & np.isfinite(w) & (w > 0) & np.all(np.isfinite(x), axis=1)
    y = y[mask]
    x = x[mask]
    w = w[mask]
    cluster = cluster[mask]
    if len(y) <= x.shape[1] + 5:
        k = x.shape[1]
        return np.full(k, np.nan), np.full(k, np.nan), np.full(k, np.nan), int(len(y)), int(pd.Series(cluster).nunique())

    sw = np.sqrt(w / np.nanmean(w))
    xw = x * sw[:, None]
    yw = y * sw
    inv = np.linalg.pinv(xw.T @ xw)
    beta = inv @ (xw.T @ yw)
    resid = yw - xw @ beta

    meat_hc1 = xw.T @ ((resid**2)[:, None] * xw)
    n, k = xw.shape
    cov_hc1 = (n / max(n - k, 1)) * inv @ meat_hc1 @ inv
    se_hc1 = np.sqrt(np.where(np.diag(cov_hc1) >= 0, np.diag(cov_hc1), np.nan))

    codes, uniques = pd.factorize(cluster, sort=False)
    score_rows = xw * resid[:, None]
    score_sums = np.zeros((len(uniques), k))
    np.add.at(score_sums, codes, score_rows)
    meat = score_sums.T @ score_sums
    g_count = int(len(uniques))
    if g_count > 1:
        meat *= (g_count / (g_count - 1)) * ((n - 1) / max(n - k, 1))
    cov_cluster = inv @ meat @ inv
    se_cluster = np.sqrt(np.where(np.diag(cov_cluster) >= 0, np.diag(cov_cluster), np.nan))
    return beta, se_hc1, se_cluster, int(n), g_count


def read_panel() -> pd.DataFrame:
    cols = [
        "person_id",
        "person_month_key",
        "reference_year",
        "reference_month",
        "state_fips",
        "TAGE",
        "ESEX",
        "ERACE",
        "EHISPAN",
        "RDIS",
        "WPFINWGT",
        "TSSSAMT",
        "RHLTHMTH",
        "RPRIMTH",
        "RPUBMTH",
        "RPUBTYPE1",
        "EMDMTH",
        "RPRITYPE2",
        "RMARKTPLACE",
        "EPRIEXCH1",
        "EPRIEXCH2",
        "EPRISUBS1",
        "EPRISUBS2",
        "EMDEXCH",
        "EMDSUBS",
        "TFINCPOV",
        "TFCYINCPOV",
        "TMDPAY",
        "TVISDOC",
    ]
    df = pd.read_parquet(PANEL, columns=cols)
    df = df[df["reference_year"].between(2017, 2023)].copy()
    df["state_fips"] = df["state_fips"].astype(str).str.zfill(2)
    df["age"] = bounded_numeric(df["TAGE"], 0, 100)
    df["female"] = pd.to_numeric(df["ESEX"], errors="coerce").eq(2).astype(float)
    df["black"] = pd.to_numeric(df["ERACE"], errors="coerce").eq(2).astype(float)
    df["hispanic"] = yes(df["EHISPAN"]).astype(float)
    df["disabled"] = yes(df["RDIS"]).astype(float)
    df["monthly_fpl"] = bounded_numeric(df["TFINCPOV"], 0, 20)
    df["annual_fpl"] = bounded_numeric(df["TFCYINCPOV"], 0, 20)
    df["weight"] = clean_weight(df)
    df["month_id"] = df["reference_year"].astype(int) * 100 + df["reference_month"].astype(int)
    df["post_year2021"] = df["reference_year"].ge(2021).astype(int)
    df["post_apr2021"] = df["month_id"].ge(202104).astype(int)
    df["medicare"] = yes(df["RPUBTYPE1"]).astype(float)

    df["any_coverage"] = yes(df["RHLTHMTH"]).astype(float)
    df["uninsured"] = df["RHLTHMTH"].eq(2).astype(float)
    df["private"] = yes(df["RPRIMTH"]).astype(float)
    df["public"] = yes(df["RPUBMTH"]).astype(float)
    df["medicaid"] = yes(df["EMDMTH"]).astype(float)
    df["direct_purchase"] = (yes(df["RPRITYPE2"]) | yes(df["RMARKTPLACE"])).astype(float)
    df["marketplace_flag"] = (
        yes(df["RMARKTPLACE"]) | yes(df["EPRIEXCH1"]) | yes(df["EPRIEXCH2"]) | yes(df["EMDEXCH"])
    ).astype(float)
    df["subsidized_private"] = (yes(df["EPRISUBS1"]) | yes(df["EPRISUBS2"]) | yes(df["EMDSUBS"])).astype(float)
    df["market_or_subsidy"] = (
        df["direct_purchase"].eq(1) | df["marketplace_flag"].eq(1) | df["subsidized_private"].eq(1)
    ).astype(float)
    df["oop_any"] = pd.to_numeric(df["TMDPAY"], errors="coerce").gt(0).astype(float)
    df["doctor_any"] = pd.to_numeric(df["TVISDOC"], errors="coerce").gt(0).astype(float)
    return df


def make_design(d: pd.DataFrame, fpl_col: str, post_col: str, cutoff: float, bandwidth: float) -> tuple[pd.DataFrame, pd.DataFrame]:
    s = d.copy()
    s["running"] = s[fpl_col] - cutoff
    s["above"] = s[fpl_col].gt(cutoff).astype(float)
    s["post"] = s[post_col].astype(float)
    s["key"] = s["above"] * s["post"]
    s["kernel"] = (1 - (s["running"].abs() / bandwidth)).clip(lower=0)
    s["analysis_weight"] = s["weight"] * s["kernel"]

    parts: list[pd.Series | pd.DataFrame] = [
        pd.Series(1.0, index=s.index, name="const"),
        s["above"].rename("above"),
        s["post"].rename("post"),
        s["key"].rename("above_x_post"),
        s["running"].rename("running"),
        (s["running"] * s["above"]).rename("running_x_above"),
        (s["running"] * s["post"]).rename("running_x_post"),
        (s["running"] * s["above"] * s["post"]).rename("running_x_above_x_post"),
        s["age"].rename("age"),
        s["female"].rename("female"),
        s["black"].rename("black"),
        s["hispanic"].rename("hispanic"),
        s["disabled"].rename("disabled"),
    ]
    for col in ["reference_year", "reference_month", "state_fips"]:
        parts.append(pd.get_dummies(s[col].astype(str), prefix=col, drop_first=True, dtype=float))
    x = pd.concat(parts, axis=1)
    return s, x


def estimate_one(
    df: pd.DataFrame,
    outcome: str,
    model: str,
    fpl_col: str,
    post_col: str,
    age_min: int,
    cutoff: float,
    bandwidth: float,
) -> dict:
    d = df[
        df["age"].between(age_min, 64, inclusive="both")
        & df["medicare"].ne(1)
        & df[fpl_col].between(cutoff - bandwidth, cutoff + bandwidth, inclusive="both")
        & df["weight"].gt(0)
    ].copy()
    s, x = make_design(d, fpl_col, post_col, cutoff, bandwidth)
    beta, se_hc1, se_person, n, g = wls_hc1_cluster(
        s[outcome].to_numpy(dtype=float),
        x.to_numpy(dtype=float),
        s["analysis_weight"].to_numpy(dtype=float),
        s["person_id"].to_numpy(),
    )
    b = pd.Series(beta, index=x.columns)
    hc1 = pd.Series(se_hc1, index=x.columns)
    pcl = pd.Series(se_person, index=x.columns)

    cell = (
        s.groupby(["post", "above"], observed=True)
        .agg(rows=("person_id", "size"), persons=("person_id", "nunique"), events=(outcome, "sum"))
        .reset_index()
    )
    return {
        "model": model,
        "outcome": outcome,
        "fpl_col": fpl_col,
        "post_col": post_col,
        "age_min": age_min,
        "cutoff": cutoff,
        "bandwidth": bandwidth,
        "coef_above_x_post": b.get("above_x_post", np.nan),
        "se_hc1": hc1.get("above_x_post", np.nan),
        "t_hc1": b.get("above_x_post", np.nan) / hc1.get("above_x_post", np.nan)
        if hc1.get("above_x_post", np.nan) > 0
        else np.nan,
        "se_person_cluster": pcl.get("above_x_post", np.nan),
        "t_person_cluster": b.get("above_x_post", np.nan) / pcl.get("above_x_post", np.nan)
        if pcl.get("above_x_post", np.nan) > 0
        else np.nan,
        "n_person_months": n,
        "n_persons": int(s["person_id"].nunique()),
        "n_person_clusters": g,
        "n_states": int(s["state_fips"].nunique()),
        "min_cell_persons": int(cell["persons"].min()) if not cell.empty else 0,
        "min_cell_events": int(cell["events"].min()) if not cell.empty else 0,
        "weighted_mean": wmean(s[outcome], s["weight"]),
    }


def estimate_model(
    df: pd.DataFrame,
    outcomes: list[str],
    model: str,
    fpl_col: str,
    post_col: str,
    age_min: int,
    cutoff: float,
    bandwidth: float,
) -> list[dict]:
    d = df[
        df["age"].between(age_min, 64, inclusive="both")
        & df["medicare"].ne(1)
        & df[fpl_col].between(cutoff - bandwidth, cutoff + bandwidth, inclusive="both")
        & df["weight"].gt(0)
    ].copy()
    s, x = make_design(d, fpl_col, post_col, cutoff, bandwidth)
    x_np = x.to_numpy(dtype=float)
    w_np = s["analysis_weight"].to_numpy(dtype=float)
    cluster_np = s["person_id"].to_numpy()
    cell_base = s.groupby(["post", "above"], observed=True).agg(rows=("person_id", "size"), persons=("person_id", "nunique")).reset_index()
    rows = []
    for outcome in outcomes:
        beta, se_hc1, se_person, n, g = wls_hc1_cluster(
            s[outcome].to_numpy(dtype=float),
            x_np,
            w_np,
            cluster_np,
        )
        b = pd.Series(beta, index=x.columns)
        hc1 = pd.Series(se_hc1, index=x.columns)
        pcl = pd.Series(se_person, index=x.columns)
        events = s.groupby(["post", "above"], observed=True)[outcome].sum().reset_index(name="events")
        cell = cell_base.merge(events, on=["post", "above"], how="left")
        rows.append(
            {
                "model": model,
                "outcome": outcome,
                "fpl_col": fpl_col,
                "post_col": post_col,
                "age_min": age_min,
                "cutoff": cutoff,
                "bandwidth": bandwidth,
                "coef_above_x_post": b.get("above_x_post", np.nan),
                "se_hc1": hc1.get("above_x_post", np.nan),
                "t_hc1": b.get("above_x_post", np.nan) / hc1.get("above_x_post", np.nan)
                if hc1.get("above_x_post", np.nan) > 0
                else np.nan,
                "se_person_cluster": pcl.get("above_x_post", np.nan),
                "t_person_cluster": b.get("above_x_post", np.nan) / pcl.get("above_x_post", np.nan)
                if pcl.get("above_x_post", np.nan) > 0
                else np.nan,
                "n_person_months": n,
                "n_persons": int(s["person_id"].nunique()),
                "n_person_clusters": g,
                "n_states": int(s["state_fips"].nunique()),
                "min_cell_persons": int(cell["persons"].min()) if not cell.empty else 0,
                "min_cell_events": int(cell["events"].min()) if not cell.empty else 0,
                "weighted_mean": wmean(s[outcome], s["weight"]),
            }
        )
    return rows


def cell_means(
    df: pd.DataFrame,
    outcomes: list[str],
    model: str,
    fpl_col: str,
    post_col: str,
    age_min: int,
    cutoff: float,
    bandwidth: float,
) -> pd.DataFrame:
    d = df[
        df["age"].between(age_min, 64, inclusive="both")
        & df["medicare"].ne(1)
        & df[fpl_col].between(cutoff - bandwidth, cutoff + bandwidth, inclusive="both")
        & df["weight"].gt(0)
    ].copy()
    d["above"] = d[fpl_col].gt(cutoff).astype(int)
    d["post"] = d[post_col].astype(int)
    rows = []
    for (post, above), g in d.groupby(["post", "above"], observed=True):
        row = {
            "model": model,
            "post": int(post),
            "above": int(above),
            "person_months": int(len(g)),
            "persons": int(g["person_id"].nunique()),
        }
        for outcome in outcomes:
            row[outcome] = wmean(g[outcome], g["weight"])
        rows.append(row)
    return pd.DataFrame(rows)


def support_row(df: pd.DataFrame, model: str, fpl_col: str, post_col: str, age_min: int, cutoff: float, bandwidth: float) -> dict:
    d = df[
        df["age"].between(age_min, 64, inclusive="both")
        & df["medicare"].ne(1)
        & df[fpl_col].between(cutoff - bandwidth, cutoff + bandwidth, inclusive="both")
        & df["weight"].gt(0)
    ].copy()
    d["above"] = d[fpl_col].gt(cutoff).astype(int)
    d["post"] = d[post_col].astype(int)
    return {
        "model": model,
        "fpl_col": fpl_col,
        "post_col": post_col,
        "age_min": age_min,
        "cutoff": cutoff,
        "bandwidth": bandwidth,
        "person_months": int(len(d)),
        "persons": int(d["person_id"].nunique()),
        "states": int(d["state_fips"].nunique()),
        "pre_below_persons": int(d[(d["post"].eq(0)) & (d["above"].eq(0))]["person_id"].nunique()),
        "pre_above_persons": int(d[(d["post"].eq(0)) & (d["above"].eq(1))]["person_id"].nunique()),
        "post_below_persons": int(d[(d["post"].eq(1)) & (d["above"].eq(0))]["person_id"].nunique()),
        "post_above_persons": int(d[(d["post"].eq(1)) & (d["above"].eq(1))]["person_id"].nunique()),
    }


def fmt(est: pd.DataFrame, model: str, outcomes: list[str]) -> str:
    d = est[est["model"].eq(model)].set_index("outcome")
    lines = []
    for outcome in outcomes:
        if outcome not in d.index:
            continue
        r = d.loc[outcome]
        lines.append(
            f"- `{outcome}`: {r['coef_above_x_post']:+.4f}, HC1 se {r['se_hc1']:.4f}, "
            f"t {r['t_hc1']:.2f}; person-cluster se {r['se_person_cluster']:.4f}, "
            f"t {r['t_person_cluster']:.2f}."
        )
    return "\n".join(lines)


def md_table(df: pd.DataFrame, cols: list[str]) -> str:
    lines = ["| " + " | ".join(cols) + " |", "|" + "|".join(["---"] * len(cols)) + "|"]
    for _, r in df[cols].iterrows():
        vals = []
        for c in cols:
            v = r[c]
            if isinstance(v, float):
                vals.append(f"{v:.4f}")
            else:
                vals.append(str(v))
        lines.append("| " + " | ".join(vals) + " |")
    return "\n".join(lines)


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    df = read_panel()
    outcomes = [
        "uninsured",
        "any_coverage",
        "direct_purchase",
        "marketplace_flag",
        "market_or_subsidy",
        "private",
        "public",
        "medicaid",
        "oop_any",
        "doctor_any",
    ]
    specs = [
        ("monthly_fpl_age26_64_postyear_bw050", "monthly_fpl", "post_year2021", 26, 4.0, 0.50, outcomes),
        (
            "monthly_fpl_age21_64_postyear_bw050",
            "monthly_fpl",
            "post_year2021",
            21,
            4.0,
            0.50,
            ["uninsured", "any_coverage", "direct_purchase", "marketplace_flag", "market_or_subsidy"],
        ),
        (
            "monthly_fpl_age26_64_postapr2021_bw050",
            "monthly_fpl",
            "post_apr2021",
            26,
            4.0,
            0.50,
            ["uninsured", "any_coverage", "direct_purchase", "marketplace_flag", "market_or_subsidy"],
        ),
        (
            "annual_fpl_age26_64_postyear_bw050",
            "annual_fpl",
            "post_year2021",
            26,
            4.0,
            0.50,
            ["uninsured", "any_coverage", "direct_purchase", "marketplace_flag", "market_or_subsidy"],
        ),
        (
            "monthly_fpl_age26_64_postyear_bw025",
            "monthly_fpl",
            "post_year2021",
            26,
            4.0,
            0.25,
            ["uninsured", "direct_purchase", "market_or_subsidy"],
        ),
        (
            "monthly_fpl_age26_64_postyear_bw075",
            "monthly_fpl",
            "post_year2021",
            26,
            4.0,
            0.75,
            ["uninsured", "direct_purchase", "market_or_subsidy"],
        ),
    ]
    rows = []
    support = []
    means = []
    for model, fpl_col, post_col, age_min, cutoff, bw, spec_outcomes in specs:
        support.append(support_row(df, model, fpl_col, post_col, age_min, cutoff, bw))
        means.append(cell_means(df, outcomes, model, fpl_col, post_col, age_min, cutoff, bw))
        rows.extend(estimate_model(df, spec_outcomes, model, fpl_col, post_col, age_min, cutoff, bw))

    # Placebo cutoffs for the main outcome and market proxy.
    for cutoff in [3.0, 3.5, 4.5, 5.0]:
        model = f"placebo_cutoff_{cutoff:.1f}_monthly_fpl_age26_64"
        support.append(support_row(df, model, "monthly_fpl", "post_year2021", 26, cutoff, 0.50))
        means.append(cell_means(df, ["uninsured", "direct_purchase", "market_or_subsidy"], model, "monthly_fpl", "post_year2021", 26, cutoff, 0.50))
        rows.extend(
            estimate_model(
                df,
                ["uninsured", "direct_purchase", "market_or_subsidy"],
                model,
                "monthly_fpl",
                "post_year2021",
                26,
                cutoff,
                0.50,
            )
        )

    est = pd.DataFrame(rows)
    sup = pd.DataFrame(support)
    cm = pd.concat(means, ignore_index=True)
    est.to_csv(OUT / "arpa400_diffdisc_estimates.csv", index=False)
    sup.to_csv(OUT / "arpa400_diffdisc_support.csv", index=False)
    cm.to_csv(OUT / "arpa400_diffdisc_cell_means.csv", index=False)

    primary = "monthly_fpl_age26_64_postyear_bw050"
    user_match = "monthly_fpl_age21_64_postyear_bw050"
    apr = "monthly_fpl_age26_64_postapr2021_bw050"
    annual = "annual_fpl_age26_64_postyear_bw050"
    s_primary = sup[sup["model"].eq(primary)].iloc[0]
    s_user = sup[sup["model"].eq(user_match)].iloc[0]
    u = est[(est["model"].eq(primary)) & (est["outcome"].eq("uninsured"))].iloc[0]
    m = est[(est["model"].eq(primary)) & (est["outcome"].eq("market_or_subsidy"))].iloc[0]
    verdict = "NO-CLEAN-GO"
    if u["coef_above_x_post"] < -0.015 and u["t_person_cluster"] < -1.8:
        verdict = "CONDITIONAL-GO-UNINSURANCE-SIGNAL"
    elif u["coef_above_x_post"] < 0:
        verdict = "DIRECTIONAL-BUT-NOT-CLEAN"

    primary_means = md_table(
        cm[cm["model"].eq(primary)],
        ["post", "above", "person_months", "persons", "uninsured", "direct_purchase", "marketplace_flag", "market_or_subsidy"],
    )
    bandwidth_table = md_table(
        est[
            (est["model"].isin(["monthly_fpl_age26_64_postyear_bw025", "monthly_fpl_age26_64_postyear_bw050", "monthly_fpl_age26_64_postyear_bw075"]))
            & (est["outcome"].isin(["uninsured", "direct_purchase", "market_or_subsidy"]))
        ],
        ["model", "outcome", "coef_above_x_post", "se_person_cluster", "t_person_cluster", "n_persons", "min_cell_persons"],
    )
    placebo_table = md_table(
        est[(est["model"].str.startswith("placebo_cutoff")) & (est["outcome"].isin(["uninsured", "direct_purchase", "market_or_subsidy"]))],
        ["model", "outcome", "coef_above_x_post", "se_person_cluster", "t_person_cluster", "n_persons", "min_cell_persons"],
    )

    report = f"""# ARPA 400% FPL Subsidy-Cliff Difference-in-Discontinuities Test

## Question

Did ARPA's temporary removal of the ACA Marketplace 400% FPL subsidy cliff reduce uninsurance among
near-threshold adults?

## Source Checks

{chr(10).join(f"- {s}" for s in SOURCES)}

Policy facts used here:

- CMS states that before ARPA, households above 400% FPL were not eligible for Marketplace premium
  tax credits.
- CMS states that ARPA made premium tax credits available above 400% FPL when benchmark premiums
  exceeded 8.5% of household income.
- IRS confirms that ARPA temporarily eliminated the rule barring PTC eligibility above 400% FPL for
  tax years 2021 and 2022.
- KFF's 2026 analyses make the question current again: enhanced PTCs expired after 2025, the
  subsidy cliff returned, and above-400% FPL consumers account for a large share of early Marketplace
  enrollment losses.

## Design

- Unit: person-month, SIPP 2017-2023.
- Main running variable: `TFINCPOV`, family monthly income-to-poverty ratio.
- Sensitivity running variable: `TFCYINCPOV`, family calendar-year income-to-poverty ratio.
- Main sample: age 26-64, non-Medicare months, 350-450% FPL.
- User-matched support sample: age 21-64, non-Medicare months, 350-450% FPL.
- Treatment contrast: above 400% FPL x post-2021.
- Model: local linear difference-in-discontinuities with triangular kernel weights, year FE, month
  FE, state FE, and basic demographics.
- Standard errors: HC1 and person-clustered SEs.

## Support

Main age 26-64 monthly-FPL sample:

- Person-months: {int(s_primary['person_months']):,}.
- Persons: {int(s_primary['persons']):,}.
- States: {int(s_primary['states']):,}.
- Minimum cell persons: {int(est[est['model'].eq(primary)]['min_cell_persons'].min()):,}.

Age 21-64 monthly-FPL sample, matching the broader screen:

- Person-months: {int(s_user['person_months']):,}.
- Persons: {int(s_user['persons']):,}.
- States: {int(s_user['states']):,}.

## Raw Cell Means

Main age 26-64 monthly-FPL sample:

{primary_means}

## Main Estimates

Main age 26-64, monthly FPL, post = 2021-2023:

{fmt(est, primary, ['uninsured', 'any_coverage', 'direct_purchase', 'marketplace_flag', 'market_or_subsidy', 'private', 'public', 'medicaid'])}

Age 21-64, monthly FPL, post = 2021-2023:

{fmt(est, user_match, ['uninsured', 'any_coverage', 'direct_purchase', 'marketplace_flag', 'market_or_subsidy'])}

Age 26-64, monthly FPL, post = April 2021 onward:

{fmt(est, apr, ['uninsured', 'any_coverage', 'direct_purchase', 'marketplace_flag', 'market_or_subsidy'])}

Age 26-64, annual FPL sensitivity:

{fmt(est, annual, ['uninsured', 'any_coverage', 'direct_purchase', 'marketplace_flag', 'market_or_subsidy'])}

## Bandwidth Sensitivity

{bandwidth_table}

## Placebo Cutoffs

{placebo_table}

## Verdict

`{verdict}`

Interpretation:

- The go/no-go hinge is the uninsured estimate, because SIPP's Marketplace/direct-purchase
  measurement is known to be incomplete and the compact parquet lacks `RPRITYPE1` employer-related
  private coverage.
- A clean GO requires the uninsured reduction to survive age window, post-April-2021 timing, annual
  FPL sensitivity, bandwidth checks, and placebo-cutoff checks.
- If the uninsured effect survives but Marketplace proxies remain weak, the paper should be framed
  around coverage/uninsurance and then use direct-purchase/Marketplace proxies as secondary
  mechanism evidence, not as the sole first stage.

## Artifacts

- `script/11_idea_scan/24_arpa_400fpl_cliff_diffdisc_test.py`
- `result/idea_scan/arpa400_diffdisc_estimates.csv`
- `result/idea_scan/arpa400_diffdisc_support.csv`
- `result/idea_scan/arpa400_diffdisc_cell_means.csv`
"""
    REPORT.write_text(report, encoding="utf-8")
    print(verdict)
    print(sup.to_string(index=False))
    print(est[est["model"].isin([primary, user_match, apr, annual])].to_string(index=False))


if __name__ == "__main__":
    main()
