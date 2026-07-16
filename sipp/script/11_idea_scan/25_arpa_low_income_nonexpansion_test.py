from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[2]
PANEL = ROOT / "data" / "analysis_ready" / "sipp_2018_2024_person_month_panel.parquet"
OUT = ROOT / "result" / "idea_scan"
REPORT = ROOT / "report" / "52_arpa_low_income_nonexpansion_test.md"


SOURCES = [
    "CMS American Rescue Plan and the Marketplace: https://www.cms.gov/newsroom/fact-sheets/american-rescue-plan-and-marketplace",
    "KFF Medicaid expansion status: https://www.kff.org/medicaid/status-of-state-medicaid-expansion-decisions/",
    "KFF enhanced PTC expiration premium-payment analysis: https://www.kff.org/affordable-care-act/aca-marketplace-premium-payments-would-more-than-double-on-average-next-year-if-enhanced-premium-tax-credits-expire/",
]


STABLE_NONEXPANSION = {
    "01": "Alabama",
    "12": "Florida",
    "13": "Georgia",
    "20": "Kansas",
    "28": "Mississippi",
    "45": "South Carolina",
    "47": "Tennessee",
    "48": "Texas",
    "55": "Wisconsin",
    "56": "Wyoming",
}

# Expansion timing changes or partial expansions make these poor controls for a fast screen.
EXCLUDE_STATES = {
    "29": "Missouri",
    "40": "Oklahoma",
    "46": "South Dakota",
    "37": "North Carolina",
}


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


def wls_cluster(
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
    g_count = len(uniques)
    if g_count > 1:
        meat *= (g_count / (g_count - 1)) * ((n - 1) / max(n - k, 1))
    cov = inv @ meat @ inv
    se_cluster = np.sqrt(np.where(np.diag(cov) >= 0, np.diag(cov), np.nan))
    return beta, se_hc1, se_cluster, int(n), int(g_count)


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
        "TMDPAY",
        "TVISDOC",
    ]
    df = pd.read_parquet(PANEL, columns=cols)
    df = df[df["reference_year"].between(2017, 2023)].copy()
    df["state_fips"] = df["state_fips"].astype(str).str.zfill(2)
    df = df[~df["state_fips"].isin(EXCLUDE_STATES)].copy()
    df["age"] = bounded_numeric(df["TAGE"], 0, 100)
    df["female"] = pd.to_numeric(df["ESEX"], errors="coerce").eq(2).astype(float)
    df["black"] = pd.to_numeric(df["ERACE"], errors="coerce").eq(2).astype(float)
    df["hispanic"] = yes(df["EHISPAN"]).astype(float)
    df["disabled"] = yes(df["RDIS"]).astype(float)
    df["fpl"] = bounded_numeric(df["TFINCPOV"], 0, 20)
    df["weight"] = clean_weight(df)
    df["month_id"] = df["reference_year"].astype(int) * 100 + df["reference_month"].astype(int)
    df["nonexpansion"] = df["state_fips"].isin(STABLE_NONEXPANSION).astype(int)
    df["target_100_150"] = df["fpl"].between(1.0, 1.5, inclusive="both").astype(int)
    df["post2021"] = df["reference_year"].ge(2021).astype(int)
    df["post_apr2021"] = df["month_id"].ge(202104).astype(int)
    df["nonexp_target_post"] = df["nonexpansion"] * df["target_100_150"] * df["post2021"]
    df["nonexp_target_post_apr"] = df["nonexpansion"] * df["target_100_150"] * df["post_apr2021"]
    df["state_year"] = df["state_fips"] + "_" + df["reference_year"].astype(str)
    df["state_target"] = df["state_fips"] + "_" + df["target_100_150"].astype(str)
    df["target_year"] = df["target_100_150"].astype(str) + "_" + df["reference_year"].astype(str)

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


def prep_sample(df: pd.DataFrame, age_min: int, post_term: str) -> tuple[pd.DataFrame, pd.DataFrame]:
    s = df[
        df["age"].between(age_min, 64, inclusive="both")
        & df["fpl"].between(1.0, 2.0, inclusive="both")
        & df["disabled"].ne(1)
        & yes(df["RPUBTYPE1"]).ne(True)
        & df["weight"].gt(0)
    ].copy()
    parts: list[pd.Series | pd.DataFrame] = [
        pd.Series(1.0, index=s.index, name="const"),
        s[post_term].astype(float).rename(post_term),
        s["age"].rename("age"),
        s["female"].rename("female"),
        s["black"].rename("black"),
        s["hispanic"].rename("hispanic"),
    ]
    for col in ["state_year", "state_target", "target_year", "reference_month"]:
        parts.append(pd.get_dummies(s[col].astype(str), prefix=col, drop_first=True, dtype=float))
    x = pd.concat(parts, axis=1)
    return s, x


def estimate(s: pd.DataFrame, x: pd.DataFrame, term: str, outcomes: list[str], model: str) -> pd.DataFrame:
    x_np = x.to_numpy(dtype=float)
    w_np = s["weight"].to_numpy(dtype=float)
    cluster_np = s["state_fips"].to_numpy()
    rows = []
    for outcome in outcomes:
        beta, se_hc1, se_cluster, n, g = wls_cluster(s[outcome].to_numpy(dtype=float), x_np, w_np, cluster_np)
        b = pd.Series(beta, index=x.columns)
        hc1 = pd.Series(se_hc1, index=x.columns)
        cl = pd.Series(se_cluster, index=x.columns)
        rows.append(
            {
                "model": model,
                "outcome": outcome,
                "term": term,
                "coef": b.get(term, np.nan),
                "se_hc1": hc1.get(term, np.nan),
                "t_hc1": b.get(term, np.nan) / hc1.get(term, np.nan) if hc1.get(term, np.nan) > 0 else np.nan,
                "state_clustered_se": cl.get(term, np.nan),
                "state_clustered_t": b.get(term, np.nan) / cl.get(term, np.nan) if cl.get(term, np.nan) > 0 else np.nan,
                "n_person_months": n,
                "n_persons": int(s["person_id"].nunique()),
                "n_states": g,
                "weighted_mean": wmean(s[outcome], s["weight"]),
            }
        )
    return pd.DataFrame(rows)


def support(s: pd.DataFrame, model: str, term: str) -> pd.DataFrame:
    rows = []
    for nonexp in [0, 1]:
        for target in [0, 1]:
            for post in [0, 1]:
                g = s[s["nonexpansion"].eq(nonexp) & s["target_100_150"].eq(target) & s["post2021"].eq(post)]
                rows.append(
                    {
                        "model": model,
                        "nonexpansion": nonexp,
                        "target_100_150": target,
                        "post2021": post,
                        "person_months": int(len(g)),
                        "persons": int(g["person_id"].nunique()),
                        "uninsured": wmean(g["uninsured"], g["weight"]),
                        "direct_purchase": wmean(g["direct_purchase"], g["weight"]),
                        "marketplace_flag": wmean(g["marketplace_flag"], g["weight"]),
                        "market_or_subsidy": wmean(g["market_or_subsidy"], g["weight"]),
                    }
                )
    out = pd.DataFrame(rows)
    active = s[s[term].eq(1)]
    extra = pd.DataFrame(
        [
            {
                "model": model,
                "nonexpansion": "active_term",
                "target_100_150": "active_term",
                "post2021": "active_term",
                "person_months": int(len(active)),
                "persons": int(active["person_id"].nunique()),
                "uninsured": wmean(active["uninsured"], active["weight"]),
                "direct_purchase": wmean(active["direct_purchase"], active["weight"]),
                "marketplace_flag": wmean(active["marketplace_flag"], active["weight"]),
                "market_or_subsidy": wmean(active["market_or_subsidy"], active["weight"]),
            }
        ]
    )
    return pd.concat([out, extra], ignore_index=True)


def fmt(est: pd.DataFrame, model: str, outcomes: list[str]) -> str:
    d = est[est["model"].eq(model)].set_index("outcome")
    lines = []
    for outcome in outcomes:
        if outcome not in d.index:
            continue
        r = d.loc[outcome]
        lines.append(
            f"- `{outcome}`: {r['coef']:+.4f}, state-clustered se {r['state_clustered_se']:.4f}, "
            f"t {r['state_clustered_t']:.2f}."
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
    s26, x26 = prep_sample(df, 26, "nonexp_target_post")
    s21, x21 = prep_sample(df, 21, "nonexp_target_post")
    s26_apr, x26_apr = prep_sample(df, 26, "nonexp_target_post_apr")

    estimates = pd.concat(
        [
            estimate(s26, x26, "nonexp_target_post", outcomes, "age26_64_postyear"),
            estimate(s21, x21, "nonexp_target_post", outcomes[:5], "age21_64_postyear"),
            estimate(s26_apr, x26_apr, "nonexp_target_post_apr", outcomes[:5], "age26_64_postapr2021"),
        ],
        ignore_index=True,
    )
    sup = pd.concat(
        [
            support(s26, "age26_64_postyear", "nonexp_target_post"),
            support(s21, "age21_64_postyear", "nonexp_target_post"),
        ],
        ignore_index=True,
    )
    estimates.to_csv(OUT / "arpa_low_income_nonexpansion_estimates.csv", index=False)
    sup.to_csv(OUT / "arpa_low_income_nonexpansion_support.csv", index=False)

    active = sup[(sup["model"].eq("age26_64_postyear")) & (sup["nonexpansion"].eq("active_term"))].iloc[0]
    pre_active = sup[
        (sup["model"].eq("age26_64_postyear"))
        & (sup["nonexpansion"].astype(str).eq("1"))
        & (sup["target_100_150"].astype(str).eq("1"))
        & (sup["post2021"].astype(str).eq("0"))
    ].iloc[0]
    main_unins = estimates[(estimates["model"].eq("age26_64_postyear")) & (estimates["outcome"].eq("uninsured"))].iloc[0]
    main_market = estimates[(estimates["model"].eq("age26_64_postyear")) & (estimates["outcome"].eq("market_or_subsidy"))].iloc[0]
    verdict = "NO-CLEAN-GO"
    if main_unins["coef"] < -0.015 and main_market["coef"] > 0.015:
        verdict = "POTENTIAL-BACKUP-GO"
    elif main_market["coef"] > 0:
        verdict = "DIRECTIONAL-MARKETPLACE-UPTAKE-BUT-WEAK-COVERAGE"

    report = f"""# ARPA Low-Income Non-Expansion Marketplace Test

## Question

Did ARPA's zero- or near-zero-premium Marketplace environment improve coverage among 100-150% FPL
adults in stable non-expansion states?

## Source Checks

{chr(10).join(f"- {s}" for s in SOURCES)}

Policy facts used here:

- CMS states that many households at 100-150% FPL would have $0 premium plans after ARPA.
- KFF tracks Medicaid expansion status and identifies the states that have not adopted expansion.
- KFF's 2026 enhanced-PTC expiration analysis again highlights low-income non-expansion-state
  Marketplace affordability as a live policy issue.

## Design

- Unit: person-month, SIPP 2017-2023.
- Main sample: age 26-64, non-Medicare, nondisabled adults, 100-200% FPL.
- Treated income band: 100-150% FPL.
- Comparison income band: 150-200% FPL.
- Treated geography: stable non-expansion states.
- Excluded states with expansion timing changes or partial expansion complications: Missouri,
  Oklahoma, South Dakota, North Carolina.
- Treatment: stable non-expansion x 100-150% FPL x post-2021.
- Fixed effects: state-year, state-target, target-year, calendar month.
- Standard errors: clustered by state.

## Support

Age 26-64 main sample:

- Pre-2021 stable non-expansion target person-months: {int(pre_active['person_months']):,}.
- Pre-2021 stable non-expansion target persons: {int(pre_active['persons']):,}.
- Post-2021 stable non-expansion target person-months: {int(active['person_months']):,}.
- Post-2021 stable non-expansion target persons: {int(active['persons']):,}.

Raw support and means:

{md_table(sup[sup['model'].eq('age26_64_postyear')], ['nonexpansion', 'target_100_150', 'post2021', 'person_months', 'persons', 'uninsured', 'direct_purchase', 'marketplace_flag', 'market_or_subsidy'])}

## Main Estimates

Age 26-64, post = 2021-2023:

{fmt(estimates, 'age26_64_postyear', outcomes)}

Age 21-64 sensitivity:

{fmt(estimates, 'age21_64_postyear', ['uninsured', 'any_coverage', 'direct_purchase', 'marketplace_flag', 'market_or_subsidy'])}

Age 26-64, post = April 2021 onward:

{fmt(estimates, 'age26_64_postapr2021', ['uninsured', 'any_coverage', 'direct_purchase', 'marketplace_flag', 'market_or_subsidy'])}

## Verdict

`{verdict}`

This is a useful backup idea only if the triple-difference recovers both Marketplace/direct-purchase
uptake and lower uninsured rates. If the market proxy rises without a clear uninsured decline, the
paper is weaker than the 400% FPL cliff design.

## Artifacts

- `script/11_idea_scan/25_arpa_low_income_nonexpansion_test.py`
- `result/idea_scan/arpa_low_income_nonexpansion_estimates.csv`
- `result/idea_scan/arpa_low_income_nonexpansion_support.csv`
"""
    REPORT.write_text(report, encoding="utf-8")
    print(verdict)
    print(sup.to_string(index=False))
    print(estimates.to_string(index=False))


if __name__ == "__main__":
    main()
