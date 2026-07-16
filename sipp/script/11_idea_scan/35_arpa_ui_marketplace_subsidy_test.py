from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[2]
PANEL = ROOT / "data" / "analysis_ready" / "sipp_2018_2024_person_month_panel.parquet"
OUT = ROOT / "result" / "idea_scan"
REPORT = ROOT / "report" / "70_arpa_ui_marketplace_subsidy_test.md"


SOURCES = [
    "CMS American Rescue Plan and the Marketplace: https://www.cms.gov/newsroom/fact-sheets/american-rescue-plan-and-marketplace",
    "KFF ARPA affordability analysis for Marketplace shoppers and the uninsured: https://www.kff.org/affordable-care-act/how-the-american-rescue-plan-act-affects-subsidies-for-marketplace-shoppers-and-people-who-are-uninsured/",
    "KFF ARPA private-coverage affordability analysis: https://www.kff.org/affordable-care-act/how-the-american-rescue-plan-will-improve-affordability-of-private-health-coverage/",
    "CMS assister webinar on unemployment compensation and APTC: https://www.cms.gov/marketplace/assister-webinars/uc-aptc-arp-webinar.pdf",
]


def yes(s: pd.Series) -> pd.Series:
    return pd.to_numeric(s, errors="coerce").eq(1)


def clean_weight(df: pd.DataFrame) -> pd.Series:
    w = pd.to_numeric(df.get("WPFINWGT"), errors="coerce")
    return w.where(w.gt(0))


def bounded_numeric(s: pd.Series, lo: float, hi: float) -> pd.Series:
    out = pd.to_numeric(s, errors="coerce")
    return out.where(out.between(lo, hi, inclusive="both"))


def wmean(y: pd.Series, w: pd.Series) -> float:
    mask = y.notna() & w.notna() & w.gt(0)
    if not mask.any():
        return np.nan
    return float(np.average(y[mask].astype(float), weights=w[mask].astype(float)))


def persons(s: pd.Series) -> int:
    return int(s.dropna().nunique())


def weighted_ols_cluster(
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
    k = x.shape[1]
    if len(y) <= k + 10:
        return np.full(k, np.nan), np.full(k, np.nan), np.full(k, np.nan), int(len(y)), 0

    sw = np.sqrt(w / np.nanmean(w))
    xw = x * sw[:, None]
    yw = y * sw
    inv = np.linalg.pinv(xw.T @ xw)
    beta = inv @ (xw.T @ yw)
    resid = yw - xw @ beta
    n, k = xw.shape

    meat_hc1 = xw.T @ ((resid**2)[:, None] * xw)
    cov_hc1 = (n / max(n - k, 1)) * inv @ meat_hc1 @ inv
    se_hc1 = np.sqrt(np.where(np.diag(cov_hc1) >= 0, np.diag(cov_hc1), np.nan))

    codes, uniques = pd.factorize(cluster, sort=False)
    score = xw * resid[:, None]
    score_sums = np.zeros((len(uniques), k))
    np.add.at(score_sums, codes, score)
    meat = score_sums.T @ score_sums
    g = len(uniques)
    if g > 1:
        meat *= (g / (g - 1)) * ((n - 1) / max(n - k, 1))
    cov_cluster = inv @ meat @ inv
    se_cluster = np.sqrt(np.where(np.diag(cov_cluster) >= 0, np.diag(cov_cluster), np.nan))
    return beta, se_hc1, se_cluster, int(n), int(g)


def read_panel() -> pd.DataFrame:
    cols = [
        "person_id",
        "person_month_key",
        "reference_year",
        "reference_month",
        "state_fips",
        "TAGE",
        "TAGE_EHC",
        "ESEX",
        "ERACE",
        "EORIGIN",
        "EHISPAN",
        "EEDUC",
        "RDIS",
        "WPFINWGT",
        "TSSSAMT",
        "EUC1MNYN",
        "EUC2MNYN",
        "EUC3MNYN",
        "RMESR",
        "RMWKWJB",
        "TPEARN",
        "TPTOTINC",
        "TFINCPOV",
        "TFCYINCPOV",
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
        "TMDPAY",
        "TVISDOC",
    ]
    df = pd.read_parquet(PANEL, columns=cols)
    df = df[df["reference_year"].between(2018, 2023)].copy()
    df["state_fips"] = df["state_fips"].astype(str).str.zfill(2)
    df["age"] = bounded_numeric(df["TAGE_EHC"], 0, 100)
    df["age"] = df["age"].where(df["age"].notna(), bounded_numeric(df["TAGE"], 0, 100))
    df["female"] = pd.to_numeric(df["ESEX"], errors="coerce").eq(2).astype(float)
    df["black"] = pd.to_numeric(df["ERACE"], errors="coerce").eq(2).astype(float)
    df["hispanic"] = (
        pd.to_numeric(df["EORIGIN"], errors="coerce").eq(1)
        | pd.to_numeric(df["EHISPAN"], errors="coerce").eq(1)
    ).astype(float)
    df["disabled"] = yes(df["RDIS"]).astype(float)
    df["educ"] = bounded_numeric(df["EEDUC"], 0, 50)
    df["fpl"] = bounded_numeric(df["TFINCPOV"], 0, 20)
    df["annual_fpl"] = bounded_numeric(df["TFCYINCPOV"], 0, 20)
    df["weight"] = clean_weight(df)
    df["medicare"] = yes(df["RPUBTYPE1"]).astype(float)
    df["medicaid"] = yes(df["EMDMTH"]).astype(float)
    df["ui_month"] = (yes(df["EUC1MNYN"]) | yes(df["EUC2MNYN"]) | yes(df["EUC3MNYN"])).astype(float)
    df["ui_year"] = df.groupby(["person_id", "reference_year"], observed=True)["ui_month"].transform("max").astype(float)
    df["weeks_worked"] = bounded_numeric(df["RMWKWJB"], 0, 5).fillna(0)
    df["employed_any_week"] = df["weeks_worked"].gt(0).astype(float)
    df["earnings"] = bounded_numeric(df["TPEARN"], -100_000, 100_000).fillna(0)
    df["personal_income"] = bounded_numeric(df["TPTOTINC"], -100_000, 100_000).fillna(0)
    df["any_coverage"] = yes(df["RHLTHMTH"]).astype(float)
    df["uninsured"] = pd.to_numeric(df["RHLTHMTH"], errors="coerce").eq(2).astype(float)
    df["private"] = yes(df["RPRIMTH"]).astype(float)
    df["public"] = yes(df["RPUBMTH"]).astype(float)
    df["direct_purchase"] = (yes(df["RPRITYPE2"]) | yes(df["RMARKTPLACE"])).astype(float)
    df["marketplace_flag"] = (
        yes(df["RMARKTPLACE"]) | yes(df["EPRIEXCH1"]) | yes(df["EPRIEXCH2"]) | yes(df["EMDEXCH"])
    ).astype(float)
    df["subsidized_private"] = (yes(df["EPRISUBS1"]) | yes(df["EPRISUBS2"]) | yes(df["EMDSUBS"])).astype(float)
    df["market_or_subsidy"] = (
        df["direct_purchase"].eq(1) | df["marketplace_flag"].eq(1) | df["subsidized_private"].eq(1)
    ).astype(float)
    df["oop_any"] = bounded_numeric(df["TMDPAY"], 0, 200_000).gt(0).astype(float)
    df["doctor_any"] = bounded_numeric(df["TVISDOC"], 0, 200).gt(0).astype(float)
    df["year2021"] = df["reference_year"].eq(2021).astype(float)
    df["subsidy_month_apr_sep"] = df["reference_month"].between(4, 9, inclusive="both").astype(float)
    # CMS implementation on HealthCare.gov became operational July 1, 2021; use this as a timing sensitivity.
    df["subsidy_month_jul_dec"] = df["reference_month"].between(7, 12, inclusive="both").astype(float)
    df["ym"] = df["reference_year"].astype(int).astype(str) + "-" + df["reference_month"].astype(int).astype(str).str.zfill(2)
    return df


def base_sample(df: pd.DataFrame, years: list[int] | None = None, no_2020: bool = False) -> pd.DataFrame:
    s = df[
        df["age"].between(26, 64, inclusive="both")
        & df["medicare"].lt(0.5)
        & df["fpl"].between(0, 10, inclusive="both")
        & df["weight"].gt(0)
    ].copy()
    if years is not None:
        s = s[s["reference_year"].isin(years)].copy()
    if no_2020:
        s = s[~s["reference_year"].eq(2020)].copy()
    return s


def design_year2021(df: pd.DataFrame) -> tuple[np.ndarray, list[str]]:
    x = pd.DataFrame(index=df.index)
    x["intercept"] = 1.0
    x["ui_year_x_2021"] = df["ui_year"] * df["year2021"]
    x["ui_year"] = df["ui_year"]
    x["age"] = df["age"]
    x["fpl"] = df["fpl"]
    x["female"] = df["female"]
    x["black"] = df["black"]
    x["hispanic"] = df["hispanic"]
    x["disabled"] = df["disabled"]
    x["employed_any_week"] = df["employed_any_week"]
    x["earnings_pos"] = df["earnings"].gt(0).astype(float)
    x["medicaid"] = df["medicaid"]
    fixed = [
        pd.get_dummies(df["reference_year"].astype(int), prefix="year", drop_first=True, dtype=float),
        pd.get_dummies(df["reference_month"].astype(int), prefix="month", drop_first=True, dtype=float),
        pd.get_dummies(df["state_fips"].astype(str), prefix="state", drop_first=True, dtype=float),
    ]
    x = pd.concat([x] + fixed, axis=1)
    return x.to_numpy(float), x.columns.tolist()


def design_timing(df: pd.DataFrame, timing_col: str) -> tuple[np.ndarray, list[str]]:
    ui = df["ui_year"].astype(float)
    y2021 = df["year2021"].astype(float)
    timing = df[timing_col].astype(float)
    x = pd.DataFrame(index=df.index)
    x["intercept"] = 1.0
    x["ui_x_2021_x_timing"] = ui * y2021 * timing
    x["ui_x_2021"] = ui * y2021
    x["ui_x_timing"] = ui * timing
    x["ui_year"] = ui
    x["age"] = df["age"]
    x["fpl"] = df["fpl"]
    x["female"] = df["female"]
    x["black"] = df["black"]
    x["hispanic"] = df["hispanic"]
    x["disabled"] = df["disabled"]
    x["employed_any_week"] = df["employed_any_week"]
    x["earnings_pos"] = df["earnings"].gt(0).astype(float)
    x["medicaid"] = df["medicaid"]
    fixed = [
        pd.get_dummies(df["ym"], prefix="ym", drop_first=True, dtype=float),
        pd.get_dummies(df["state_fips"].astype(str), prefix="state", drop_first=True, dtype=float),
    ]
    x = pd.concat([x] + fixed, axis=1)
    return x.to_numpy(float), x.columns.tolist()


def run_model(df: pd.DataFrame, model: str, outcome: str, timing_col: str | None = None) -> dict[str, float | int | str]:
    if model == "year2021_all_years":
        sample = base_sample(df)
        x, names = design_year2021(sample)
        key = "ui_year_x_2021"
    elif model == "year2021_no_2020":
        sample = base_sample(df, no_2020=True)
        x, names = design_year2021(sample)
        key = "ui_year_x_2021"
    elif model == "timing_2019_2021_2022":
        if timing_col is None:
            raise ValueError("timing_col required")
        sample = base_sample(df, years=[2019, 2021, 2022])
        x, names = design_timing(sample, timing_col)
        key = "ui_x_2021_x_timing"
    else:
        raise ValueError(model)

    y = sample[outcome].astype(float).to_numpy()
    beta, se_hc1, se_cluster, n, g = weighted_ols_cluster(
        y,
        x,
        sample["weight"].astype(float).to_numpy(),
        sample["person_id"].astype(str).to_numpy(),
    )
    idx = names.index(key)
    return {
        "model": model if timing_col is None else f"{model}_{timing_col}",
        "outcome": outcome,
        "key": key,
        "coef": float(beta[idx]),
        "se_hc1": float(se_hc1[idx]),
        "t_hc1": float(beta[idx] / se_hc1[idx]) if se_hc1[idx] > 0 else np.nan,
        "se_person_cluster": float(se_cluster[idx]),
        "t_person_cluster": float(beta[idx] / se_cluster[idx]) if se_cluster[idx] > 0 else np.nan,
        "n": n,
        "clusters_person": g,
    }


def support_and_raw(df: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    s = base_sample(df)
    support_rows = []
    for year, g in s.groupby("reference_year", observed=True):
        ui = g[g["ui_year"].eq(1)]
        support_rows.append(
            {
                "reference_year": int(year),
                "rows": int(len(g)),
                "persons": persons(g["person_id"]),
                "ui_year_rows": int(len(ui)),
                "ui_year_persons": persons(ui["person_id"]),
                "ui_month_rows": int(g["ui_month"].sum()),
                "ui_month_persons": persons(g.loc[g["ui_month"].eq(1), "person_id"]),
            }
        )
    support = pd.DataFrame(support_rows)

    raw_rows = []
    outcomes = ["uninsured", "direct_purchase", "marketplace_flag", "subsidized_private", "market_or_subsidy", "private", "public", "medicaid"]
    for year in [2019, 2020, 2021, 2022, 2023]:
        y = s[s["reference_year"].eq(year)]
        for ui_year in [0.0, 1.0]:
            cell = y[y["ui_year"].eq(ui_year)]
            if cell.empty:
                continue
            row = {
                "reference_year": year,
                "ui_year": int(ui_year),
                "period": "full_year",
                "rows": int(len(cell)),
                "persons": persons(cell["person_id"]),
            }
            for out in outcomes:
                row[out] = wmean(cell[out], cell["weight"])
            raw_rows.append(row)
        if year in [2019, 2021, 2022]:
            for period_name, mask in [
                ("jan_mar", y["reference_month"].between(1, 3, inclusive="both")),
                ("apr_sep", y["reference_month"].between(4, 9, inclusive="both")),
                ("jul_dec", y["reference_month"].between(7, 12, inclusive="both")),
            ]:
                for ui_year in [0.0, 1.0]:
                    cell = y[mask & y["ui_year"].eq(ui_year)]
                    if cell.empty:
                        continue
                    row = {
                        "reference_year": year,
                        "ui_year": int(ui_year),
                        "period": period_name,
                        "rows": int(len(cell)),
                        "persons": persons(cell["person_id"]),
                    }
                    for out in outcomes:
                        row[out] = wmean(cell[out], cell["weight"])
                    raw_rows.append(row)
    raw = pd.DataFrame(raw_rows)
    return support, raw


def write_report(estimates: pd.DataFrame, support: pd.DataFrame, raw: pd.DataFrame) -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    estimates.to_csv(OUT / "arpa_ui_marketplace_estimates.csv", index=False)
    support.to_csv(OUT / "arpa_ui_marketplace_support.csv", index=False)
    raw.to_csv(OUT / "arpa_ui_marketplace_raw_cells.csv", index=False)

    def fmt(model: str, outcome: str) -> str:
        r = estimates[(estimates["model"].eq(model)) & (estimates["outcome"].eq(outcome))]
        if r.empty:
            return "NA"
        row = r.iloc[0]
        return f"{row['coef']:.4f} (person-cluster t={row['t_person_cluster']:.2f})"

    ui_2021 = support[support["reference_year"].eq(2021)]
    ui_line = ""
    if not ui_2021.empty:
        row = ui_2021.iloc[0]
        ui_line = (
            f"- 2021 UI-recipient support: {int(row['ui_year_rows']):,} person-months, "
            f"{int(row['ui_year_persons']):,} persons with any UI in the year; "
            f"{int(row['ui_month_rows']):,} UI-receipt person-months."
        )

    lines = [
        "# ARPA Unemployment-Compensation Marketplace Subsidy Fast Test",
        "",
        "## Question",
        "",
        "Did ARPA's special 2021 Marketplace subsidy rule for people receiving unemployment compensation increase Marketplace/direct-purchase coverage or reduce uninsurance among UI recipients?",
        "",
        "## Source Checks",
        "",
    ]
    lines += [f"- {s}" for s in SOURCES]
    lines += [
        "",
        "Policy logic: CMS states that taxpayers receiving unemployment compensation during any week beginning in 2021 may be eligible for premium tax credits for 2021 Marketplace coverage. KFF explains that for UI recipients, household income above 133% FPL was disregarded for Marketplace premium and cost-sharing subsidy purposes in 2021, making zero-premium benchmark silver coverage possible.",
        "",
        "## Design",
        "",
        "Unit: person-month.",
        "",
        "Main sample: adults ages 26-64, non-Medicare, FPL <= 1000%, SIPP reference years 2018-2023.",
        "",
        "Exposure:",
        "",
        "- `ui_year`: any regular, supplemental, or other unemployment compensation receipt in the reference year.",
        "- Main DDD key: `ui_year x 2021`.",
        "- Timing sensitivity: `ui_year x 2021 x subsidy-window month`, using April-September and July-December windows.",
        "",
        "Outcomes:",
        "",
        "- uninsured;",
        "- direct-purchase private coverage;",
        "- Marketplace flag;",
        "- subsidized private flag;",
        "- direct-purchase / Marketplace / subsidy composite.",
        "",
        "Controls and fixed effects:",
        "",
        "- age, FPL, sex, race/ethnicity, disability, employment and earnings indicators, Medicaid;",
        "- state fixed effects, calendar month/year fixed effects for the year-2021 model;",
        "- state and year-month fixed effects for timing models.",
        "",
        "## Support",
        "",
        f"- Full screen support table: `result/idea_scan/arpa_ui_marketplace_support.csv`.",
        ui_line,
        "",
        "## Results",
        "",
        "Main `ui_year x 2021` model, all years:",
        "",
        f"- Uninsured: {fmt('year2021_all_years', 'uninsured')}.",
        f"- Direct purchase: {fmt('year2021_all_years', 'direct_purchase')}.",
        f"- Marketplace flag: {fmt('year2021_all_years', 'marketplace_flag')}.",
        f"- Subsidized private: {fmt('year2021_all_years', 'subsidized_private')}.",
        f"- Market/subsidy composite: {fmt('year2021_all_years', 'market_or_subsidy')}.",
        "",
        "Main `ui_year x 2021` model excluding 2020:",
        "",
        f"- Uninsured: {fmt('year2021_no_2020', 'uninsured')}.",
        f"- Direct purchase: {fmt('year2021_no_2020', 'direct_purchase')}.",
        f"- Marketplace flag: {fmt('year2021_no_2020', 'marketplace_flag')}.",
        f"- Market/subsidy composite: {fmt('year2021_no_2020', 'market_or_subsidy')}.",
        "",
        "Timing model, 2019/2021/2022 with April-September window:",
        "",
        f"- Uninsured: {fmt('timing_2019_2021_2022_subsidy_month_apr_sep', 'uninsured')}.",
        f"- Direct purchase: {fmt('timing_2019_2021_2022_subsidy_month_apr_sep', 'direct_purchase')}.",
        f"- Marketplace flag: {fmt('timing_2019_2021_2022_subsidy_month_apr_sep', 'marketplace_flag')}.",
        f"- Market/subsidy composite: {fmt('timing_2019_2021_2022_subsidy_month_apr_sep', 'market_or_subsidy')}.",
        "",
        "Timing model, 2019/2021/2022 with July-December window:",
        "",
        f"- Uninsured: {fmt('timing_2019_2021_2022_subsidy_month_jul_dec', 'uninsured')}.",
        f"- Direct purchase: {fmt('timing_2019_2021_2022_subsidy_month_jul_dec', 'direct_purchase')}.",
        f"- Marketplace flag: {fmt('timing_2019_2021_2022_subsidy_month_jul_dec', 'marketplace_flag')}.",
        f"- Market/subsidy composite: {fmt('timing_2019_2021_2022_subsidy_month_jul_dec', 'market_or_subsidy')}.",
        "",
        "## Interpretation",
        "",
        "This is a credible new SIPP idea only if the UI-recipient group shows a clear 2021-specific Marketplace/direct-purchase increase and a corresponding uninsured decline. Otherwise, the individual-level eligibility rule is too entangled with pandemic labor-market shocks to serve as a lead causal design.",
        "",
        "## Artifacts",
        "",
        "- `script/11_idea_scan/35_arpa_ui_marketplace_subsidy_test.py`",
        "- `report/70_arpa_ui_marketplace_subsidy_test.md`",
        "- `result/idea_scan/arpa_ui_marketplace_estimates.csv`",
        "- `result/idea_scan/arpa_ui_marketplace_support.csv`",
        "- `result/idea_scan/arpa_ui_marketplace_raw_cells.csv`",
    ]
    REPORT.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    df = read_panel()
    outcomes = [
        "uninsured",
        "any_coverage",
        "direct_purchase",
        "marketplace_flag",
        "subsidized_private",
        "market_or_subsidy",
        "private",
        "public",
        "medicaid",
        "oop_any",
        "doctor_any",
    ]
    rows = []
    for outcome in outcomes:
        rows.append(run_model(df, "year2021_all_years", outcome))
        rows.append(run_model(df, "year2021_no_2020", outcome))
        rows.append(run_model(df, "timing_2019_2021_2022", outcome, "subsidy_month_apr_sep"))
        rows.append(run_model(df, "timing_2019_2021_2022", outcome, "subsidy_month_jul_dec"))
    estimates = pd.DataFrame(rows)
    support, raw = support_and_raw(df)
    write_report(estimates, support, raw)
    print(f"Wrote {REPORT}")
    print(f"Wrote {OUT / 'arpa_ui_marketplace_estimates.csv'}")


if __name__ == "__main__":
    main()
