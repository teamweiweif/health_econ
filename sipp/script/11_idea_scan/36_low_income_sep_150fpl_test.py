from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[2]
PANEL = ROOT / "data" / "analysis_ready" / "sipp_2018_2024_person_month_panel.parquet"
OUT = ROOT / "result" / "idea_scan"
REPORT = ROOT / "report" / "72_low_income_sep_150fpl_test.md"


SOURCES = [
    "CMS 150% FPL SEP online functionality bulletin: https://content.govdelivery.com/accounts/USCMSHIM/bulletins/30fd85c",
    "KFF Marketplace enrollment-period FAQ on 150% FPL SEP: https://www.kff.org/faqs/faqs-health-insurance-marketplace-and-the-aca/marketplace-enrollment-periods/i-hear-there-is-a-new-special-enrollment-opportunity-in-2022-for-people-with-very-low-income-how-does-that-work/",
    "CMS 2027 proposed rule fact sheet discussing removal of the 150% FPL SEP after PY2026: https://www.cms.gov/newsroom/fact-sheets/hhs-notice-benefit-payment-parameters-2027-proposed-rule",
    "Federal Register 2027 payment parameters discussion of the 150% FPL SEP: https://www.federalregister.gov/documents/2026/05/20/2026-10050/patient-protection-and-affordable-care-act-hhs-notice-of-benefit-and-payment-parameters-for-2027-and",
]


STATE_NAMES = {
    "01": "Alabama",
    "02": "Alaska",
    "04": "Arizona",
    "05": "Arkansas",
    "06": "California",
    "08": "Colorado",
    "09": "Connecticut",
    "10": "Delaware",
    "11": "District of Columbia",
    "12": "Florida",
    "13": "Georgia",
    "15": "Hawaii",
    "16": "Idaho",
    "17": "Illinois",
    "18": "Indiana",
    "19": "Iowa",
    "20": "Kansas",
    "21": "Kentucky",
    "22": "Louisiana",
    "23": "Maine",
    "24": "Maryland",
    "25": "Massachusetts",
    "26": "Michigan",
    "27": "Minnesota",
    "28": "Mississippi",
    "29": "Missouri",
    "30": "Montana",
    "31": "Nebraska",
    "32": "Nevada",
    "33": "New Hampshire",
    "34": "New Jersey",
    "35": "New Mexico",
    "36": "New York",
    "37": "North Carolina",
    "38": "North Dakota",
    "39": "Ohio",
    "40": "Oklahoma",
    "41": "Oregon",
    "42": "Pennsylvania",
    "44": "Rhode Island",
    "45": "South Carolina",
    "46": "South Dakota",
    "47": "Tennessee",
    "48": "Texas",
    "49": "Utah",
    "50": "Vermont",
    "51": "Virginia",
    "53": "Washington",
    "54": "West Virginia",
    "55": "Wisconsin",
    "56": "Wyoming",
}

# Full state-based marketplace platforms that did not transition during the screen window.
STABLE_SBM = {
    "06",  # CA
    "08",  # CO
    "09",  # CT
    "11",  # DC
    "16",  # ID
    "24",  # MD
    "25",  # MA
    "27",  # MN
    "32",  # NV
    "36",  # NY
    "44",  # RI
    "50",  # VT
    "53",  # WA
}

# Excluded because full SBM transition overlaps the 2021-2022 policy window.
SBM_TRANSITION = {
    "21",  # KY
    "23",  # ME
    "34",  # NJ
    "35",  # NM
    "42",  # PA
}


def yes(s: pd.Series) -> pd.Series:
    return pd.to_numeric(s, errors="coerce").eq(1)


def clean_weight(df: pd.DataFrame) -> pd.Series:
    w = pd.to_numeric(df.get("WPFINWGT"), errors="coerce")
    w = w.where(w.gt(0), pd.to_numeric(df.get("TSSSAMT"), errors="coerce"))
    return w.where(w.gt(0), 1.0)


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
        "RDIS",
        "WPFINWGT",
        "TSSSAMT",
        "RHLTHMTH",
        "RPRIMTH",
        "RPUBMTH",
        "RPUBTYPE1",
        "EMDMTH",
        "RPUBTYPE2",
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
    df["state_fips"] = df["state_fips"].astype(str).str.zfill(2)
    df = df[~df["state_fips"].isin(SBM_TRANSITION)].copy()
    df["age"] = bounded_numeric(df["TAGE_EHC"], 0, 100)
    df["age"] = df["age"].where(df["age"].notna(), bounded_numeric(df["TAGE"], 0, 100))
    df["female"] = pd.to_numeric(df["ESEX"], errors="coerce").eq(2).astype(float)
    df["black"] = pd.to_numeric(df["ERACE"], errors="coerce").eq(2).astype(float)
    df["hispanic"] = (
        pd.to_numeric(df["EORIGIN"], errors="coerce").eq(1)
        | pd.to_numeric(df["EHISPAN"], errors="coerce").eq(1)
    ).astype(float)
    df["disabled"] = yes(df["RDIS"]).astype(float)
    df["fpl"] = bounded_numeric(df["TFINCPOV"], 0, 20)
    df["annual_fpl"] = bounded_numeric(df["TFCYINCPOV"], 0, 20)
    df["weight"] = clean_weight(df)
    df["medicare"] = yes(df["RPUBTYPE1"]).astype(float)
    df["medicaid"] = (yes(df["EMDMTH"]) | yes(df["RPUBTYPE2"])).astype(float)
    df["hcg_state"] = (~df["state_fips"].isin(STABLE_SBM)).astype(float)
    df["target_138_150"] = df["fpl"].between(1.38, 1.50, inclusive="both").astype(float)
    df["post_2022"] = df["reference_year"].ge(2022).astype(float)
    df["offseason_mar_oct"] = df["reference_month"].between(3, 10, inclusive="both").astype(float)
    df["prepost_year"] = df["reference_year"].isin([2018, 2019, 2022, 2023]).astype(float)
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
    df["ym"] = df["reference_year"].astype(int).astype(str) + "-" + df["reference_month"].astype(int).astype(str).str.zfill(2)
    return df


def main_sample(df: pd.DataFrame, sensitivity: str = "main") -> pd.DataFrame:
    fpl_low = 1.0 if sensitivity == "broad_no_medicaid" else 1.38
    s = df[
        df["age"].between(26, 64, inclusive="both")
        & df["medicare"].lt(0.5)
        & df["prepost_year"].eq(1)
        & df["offseason_mar_oct"].eq(1)
        & df["fpl"].between(fpl_low, 2.00, inclusive="both")
        & df["weight"].gt(0)
    ].copy()
    if sensitivity == "nondisabled":
        s = s[s["disabled"].lt(0.5)].copy()
    elif sensitivity == "no_medicaid":
        s = s[s["medicaid"].lt(0.5)].copy()
    elif sensitivity == "broad_no_medicaid":
        s = s[s["medicaid"].lt(0.5)].copy()
        s["target_138_150"] = s["fpl"].between(1.0, 1.5, inclusive="both").astype(float)
    return s


def design_matrix(sample: pd.DataFrame) -> tuple[np.ndarray, list[str]]:
    h = sample["hcg_state"].astype(float)
    t = sample["target_138_150"].astype(float)
    p = sample["post_2022"].astype(float)
    x = pd.DataFrame(index=sample.index)
    x["intercept"] = 1.0
    x["hcg_x_target_x_post"] = h * t * p
    x["hcg_x_target"] = h * t
    x["hcg_x_post"] = h * p
    x["target_x_post"] = t * p
    x["hcg_state"] = h
    x["target_138_150"] = t
    x["age"] = sample["age"].astype(float)
    x["fpl"] = sample["fpl"].astype(float)
    x["female"] = sample["female"].astype(float)
    x["black"] = sample["black"].astype(float)
    x["hispanic"] = sample["hispanic"].astype(float)
    x["disabled"] = sample["disabled"].astype(float)
    x["medicaid"] = sample["medicaid"].astype(float)
    fixed = [
        pd.get_dummies(sample["ym"], prefix="ym", drop_first=True, dtype=float),
        pd.get_dummies(sample["state_fips"].astype(str), prefix="state", drop_first=True, dtype=float),
    ]
    x = pd.concat([x] + fixed, axis=1)
    return x.to_numpy(float), x.columns.tolist()


def run_model(df: pd.DataFrame, sensitivity: str, outcome: str, cluster_col: str) -> dict[str, float | int | str]:
    sample = main_sample(df, sensitivity)
    x, names = design_matrix(sample)
    y = sample[outcome].astype(float).to_numpy()
    beta, se_hc1, se_cluster, n, g = weighted_ols_cluster(
        y,
        x,
        sample["weight"].astype(float).to_numpy(),
        sample[cluster_col].astype(str).to_numpy(),
    )
    idx = names.index("hcg_x_target_x_post")
    return {
        "sensitivity": sensitivity,
        "outcome": outcome,
        "cluster": cluster_col,
        "coef": float(beta[idx]),
        "se_hc1": float(se_hc1[idx]),
        "t_hc1": float(beta[idx] / se_hc1[idx]) if se_hc1[idx] > 0 else np.nan,
        "se_cluster": float(se_cluster[idx]),
        "t_cluster": float(beta[idx] / se_cluster[idx]) if se_cluster[idx] > 0 else np.nan,
        "n": n,
        "clusters": g,
    }


def support_and_raw(df: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    rows = []
    raw_rows = []
    outcomes = ["uninsured", "direct_purchase", "marketplace_flag", "subsidized_private", "market_or_subsidy", "private", "public", "medicaid"]
    for sens in ["main", "nondisabled", "no_medicaid", "broad_no_medicaid"]:
        s = main_sample(df, sens)
        rows.append(
            {
                "sensitivity": sens,
                "person_months": int(len(s)),
                "persons": persons(s["person_id"]),
                "states": persons(s["state_fips"]),
                "hcg_target_post_pm": int(len(s[s["hcg_state"].eq(1) & s["target_138_150"].eq(1) & s["post_2022"].eq(1)])),
                "hcg_target_post_persons": persons(
                    s.loc[s["hcg_state"].eq(1) & s["target_138_150"].eq(1) & s["post_2022"].eq(1), "person_id"]
                ),
                "sbm_target_post_pm": int(len(s[s["hcg_state"].eq(0) & s["target_138_150"].eq(1) & s["post_2022"].eq(1)])),
                "sbm_target_post_persons": persons(
                    s.loc[s["hcg_state"].eq(0) & s["target_138_150"].eq(1) & s["post_2022"].eq(1), "person_id"]
                ),
            }
        )
        for keys, g in s.groupby(["hcg_state", "target_138_150", "post_2022"], observed=True):
            row = {
                "sensitivity": sens,
                "hcg_state": int(keys[0]),
                "target_138_150": int(keys[1]),
                "post_2022": int(keys[2]),
                "person_months": int(len(g)),
                "persons": persons(g["person_id"]),
                "states": persons(g["state_fips"]),
            }
            for out in outcomes:
                row[out] = wmean(g[out], g["weight"])
            raw_rows.append(row)
    return pd.DataFrame(rows), pd.DataFrame(raw_rows)


def write_report(est: pd.DataFrame, support: pd.DataFrame, raw: pd.DataFrame) -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    est.to_csv(OUT / "low_income_sep_150fpl_estimates.csv", index=False)
    support.to_csv(OUT / "low_income_sep_150fpl_support.csv", index=False)
    raw.to_csv(OUT / "low_income_sep_150fpl_raw_cells.csv", index=False)

    def fmt(sens: str, outcome: str, cluster: str = "state_fips") -> str:
        r = est[(est["sensitivity"].eq(sens)) & (est["outcome"].eq(outcome)) & (est["cluster"].eq(cluster))]
        if r.empty:
            return "NA"
        row = r.iloc[0]
        return f"{row['coef']:.4f} ({cluster} t={row['t_cluster']:.2f})"

    main_support = support[support["sensitivity"].eq("main")].iloc[0]
    no_medicaid_support = support[support["sensitivity"].eq("no_medicaid")].iloc[0]
    broad_support = support[support["sensitivity"].eq("broad_no_medicaid")].iloc[0]

    lines = [
        "# Low-Income 150% FPL Marketplace SEP Fast Test",
        "",
        "## Question",
        "",
        "Did the 2022 low-income monthly Marketplace Special Enrollment Period for people at or below 150% FPL increase off-season Marketplace/direct-purchase coverage among adults just below the 150% FPL threshold?",
        "",
        "## Source Checks",
        "",
    ]
    lines += [f"- {s}" for s in SOURCES]
    lines += [
        "",
        "Policy logic: CMS made a low-income SEP available for consumers at or below 150% FPL, with HealthCare.gov online functionality live in March 2022. The issue is current again because CMS and the 2026-2027 rulemaking discuss removal/continued prohibition of this SEP after enhanced subsidy changes.",
        "",
        "## Design",
        "",
        "Unit: person-month.",
        "",
        "Main sample:",
        "",
        "- adults ages 26-64;",
        "- non-Medicare;",
        "- monthly FPL 138-200%;",
        "- target group 138-150% FPL;",
        "- comparison group 150-200% FPL;",
        "- off-season months March-October only;",
        "- pre years 2018-2019 and post years 2022-2023;",
        "- 2020 and 2021 excluded because they contain pandemic disruption, COVID SEP, and broad ARPA rollout;",
        "- states with overlapping SBM platform transitions excluded: KY, ME, NJ, NM, PA.",
        "",
        "Treatment contrast:",
        "",
        "- HealthCare.gov states versus stable full State-Based Marketplace states.",
        "- This is intentionally conservative because some SBMs may have adopted similar low-income SEP policies, which would attenuate the contrast.",
        "",
        "Key coefficient:",
        "",
        "- `HealthCare.gov state x 138-150% FPL target x post-2022`.",
        "",
        "Fixed effects and controls:",
        "",
        "- state fixed effects;",
        "- year-month fixed effects;",
        "- age, FPL, sex, race/ethnicity, disability, Medicaid.",
        "",
        "## Support",
        "",
        f"- Main sample: {int(main_support['person_months']):,} person-months; {int(main_support['persons']):,} persons; {int(main_support['states']):,} states.",
        f"- HealthCare.gov target-post cell: {int(main_support['hcg_target_post_pm']):,} person-months; {int(main_support['hcg_target_post_persons']):,} persons.",
        f"- Stable SBM target-post cell: {int(main_support['sbm_target_post_pm']):,} person-months; {int(main_support['sbm_target_post_persons']):,} persons.",
        f"- No-Medicaid sensitivity sample: {int(no_medicaid_support['person_months']):,} person-months; {int(no_medicaid_support['persons']):,} persons.",
        f"- Broad 100-150% no-Medicaid sensitivity sample: {int(broad_support['person_months']):,} person-months; {int(broad_support['persons']):,} persons.",
        "",
        "## Results",
        "",
        "Main sample, state-clustered:",
        "",
        f"- Uninsured: {fmt('main', 'uninsured')}.",
        f"- Direct purchase: {fmt('main', 'direct_purchase')}.",
        f"- Marketplace flag: {fmt('main', 'marketplace_flag')}.",
        f"- Subsidized private: {fmt('main', 'subsidized_private')}.",
        f"- Market/subsidy composite: {fmt('main', 'market_or_subsidy')}.",
        f"- Medicaid: {fmt('main', 'medicaid')}.",
        "",
        "No-Medicaid sensitivity, state-clustered:",
        "",
        f"- Uninsured: {fmt('no_medicaid', 'uninsured')}.",
        f"- Direct purchase: {fmt('no_medicaid', 'direct_purchase')}.",
        f"- Marketplace flag: {fmt('no_medicaid', 'marketplace_flag')}.",
        f"- Market/subsidy composite: {fmt('no_medicaid', 'market_or_subsidy')}.",
        "",
        "Broad 100-150% FPL no-Medicaid sensitivity, state-clustered:",
        "",
        f"- Uninsured: {fmt('broad_no_medicaid', 'uninsured')}.",
        f"- Direct purchase: {fmt('broad_no_medicaid', 'direct_purchase')}.",
        f"- Marketplace flag: {fmt('broad_no_medicaid', 'marketplace_flag')}.",
        f"- Market/subsidy composite: {fmt('broad_no_medicaid', 'market_or_subsidy')}.",
        "",
        "## Decision",
        "",
        "`150% FPL LOW-INCOME MARKETPLACE SEP: PLAUSIBLE POLICY GAP, BUT SIPP SCREEN IS NO-GO / APPENDIX ONLY`.",
        "",
        "Why:",
        "",
        "1. The policy question is current and real: the 150% FPL SEP was created as a low-income access tool and is now being removed/restricted in current rulemaking.",
        "2. The design is cleaner than generic ARPA low-income comparisons because it isolates off-season months and the 150% FPL threshold.",
        "3. But the usable threshold window is narrow, and Medicaid eligibility around 138% FPL creates contamination.",
        "4. The HealthCare.gov-versus-SBM treatment contrast is imperfect because state-based exchanges may have parallel policies or different outreach.",
        "5. The screen must show a large, clean direct-purchase/Marketplace effect to justify further work. The first-pass estimates do not clear that bar.",
        "",
        "## Artifacts",
        "",
        "- `script/11_idea_scan/36_low_income_sep_150fpl_test.py`",
        "- `report/72_low_income_sep_150fpl_test.md`",
        "- `result/idea_scan/low_income_sep_150fpl_estimates.csv`",
        "- `result/idea_scan/low_income_sep_150fpl_support.csv`",
        "- `result/idea_scan/low_income_sep_150fpl_raw_cells.csv`",
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
    for sens in ["main", "nondisabled", "no_medicaid", "broad_no_medicaid"]:
        for outcome in outcomes:
            rows.append(run_model(df, sens, outcome, "state_fips"))
            rows.append(run_model(df, sens, outcome, "person_id"))
    est = pd.DataFrame(rows)
    support, raw = support_and_raw(df)
    write_report(est, support, raw)
    print(f"Wrote {REPORT}")
    print(f"Wrote {OUT / 'low_income_sep_150fpl_estimates.csv'}")


if __name__ == "__main__":
    main()
