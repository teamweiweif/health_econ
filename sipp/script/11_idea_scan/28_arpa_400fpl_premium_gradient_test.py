from __future__ import annotations

import importlib.util
from pathlib import Path

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "result" / "idea_scan"
REPORT = ROOT / "report" / "58_arpa_400fpl_premium_gradient_test.md"
EMP_SCRIPT = ROOT / "script" / "11_idea_scan" / "26_arpa_400fpl_employer_mechanism_test.py"
POLICY = OUT / "ptc_premium_policy_state_year.csv"


spec = importlib.util.spec_from_file_location("arpa400_emp", EMP_SCRIPT)
emp = importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(emp)


FIPS_TO_STATE = {
    "01": "AL",
    "02": "AK",
    "04": "AZ",
    "05": "AR",
    "06": "CA",
    "08": "CO",
    "09": "CT",
    "10": "DE",
    "11": "DC",
    "12": "FL",
    "13": "GA",
    "15": "HI",
    "16": "ID",
    "17": "IL",
    "18": "IN",
    "19": "IA",
    "20": "KS",
    "21": "KY",
    "22": "LA",
    "23": "ME",
    "24": "MD",
    "25": "MA",
    "26": "MI",
    "27": "MN",
    "28": "MS",
    "29": "MO",
    "30": "MT",
    "31": "NE",
    "32": "NV",
    "33": "NH",
    "34": "NJ",
    "35": "NM",
    "36": "NY",
    "37": "NC",
    "38": "ND",
    "39": "OH",
    "40": "OK",
    "41": "OR",
    "42": "PA",
    "44": "RI",
    "45": "SC",
    "46": "SD",
    "47": "TN",
    "48": "TX",
    "49": "UT",
    "50": "VT",
    "51": "VA",
    "53": "WA",
    "54": "WV",
    "55": "WI",
    "56": "WY",
}


OUTCOMES = [
    "uninsured",
    "any_coverage",
    "employer_private",
    "direct_purchase",
    "marketplace_flag",
    "market_or_subsidy",
    "private",
]


def wmean(y: pd.Series, w: pd.Series) -> float:
    mask = y.notna() & w.notna() & (w > 0)
    if not mask.any():
        return np.nan
    return float(np.average(y[mask].astype(float), weights=w[mask].astype(float)))


def wls_cluster(
    y: np.ndarray, x: np.ndarray, w: np.ndarray, cluster: np.ndarray
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


def add_fe(parts: list[pd.Series | pd.DataFrame], s: pd.DataFrame, fe_cols: list[str]) -> pd.DataFrame:
    for col in fe_cols:
        parts.append(pd.get_dummies(s[col].astype(str), prefix=col, drop_first=True, dtype=float))
    return pd.concat(parts, axis=1)


def prepare_panel() -> pd.DataFrame:
    df = emp.read_augmented_panel()
    d = df.copy()
    d["state_fips"] = d["state_fips"].astype(str).str.zfill(2)
    d["state"] = d["state_fips"].map(FIPS_TO_STATE)
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
    d["above400"] = d["monthly_fpl"].gt(4.0).astype(float)
    d["running"] = d["monthly_fpl"] - 4.0
    d["older50"] = d["age"].between(50, 64, inclusive="both").astype(float)

    d["any_coverage"] = emp.yes(d["RHLTHMTH"]).astype(float)
    d["uninsured"] = d["RHLTHMTH"].eq(2).astype(float)
    d["private"] = emp.yes(d["RPRIMTH"]).astype(float)
    d["employer_private"] = emp.yes(d["RPRITYPE1"]).astype(float)
    d["direct_purchase"] = (emp.yes(d["RPRITYPE2"]) | emp.yes(d["RMARKTPLACE"])).astype(float)
    d["marketplace_flag"] = (
        emp.yes(d["RMARKTPLACE"]) | emp.yes(d["EPRIEXCH1"]) | emp.yes(d["EPRIEXCH2"]) | emp.yes(d["EMDEXCH"])
    ).astype(float)
    d["subsidized_private"] = (emp.yes(d["EPRISUBS1"]) | emp.yes(d["EPRISUBS2"]) | emp.yes(d["EMDSUBS"])).astype(float)
    d["market_or_subsidy"] = (
        d["direct_purchase"].eq(1) | d["marketplace_flag"].eq(1) | d["subsidized_private"].eq(1)
    ).astype(float)

    policy = pd.read_csv(POLICY)
    pre = policy[["state", "pre_2021_age60_excess_burden", "high_pre_premium_burden"]].drop_duplicates("state")
    d = d.merge(pre, on="state", how="left")
    return d


def sample(d: pd.DataFrame) -> pd.DataFrame:
    s = d[
        d["reference_year"].between(2018, 2023)
        & d["age"].between(26, 64, inclusive="both")
        & d["medicare"].ne(1)
        & d["monthly_fpl"].between(3.5, 4.5, inclusive="both")
        & d["pre_2021_age60_excess_burden"].notna()
        & d["weight"].gt(0)
    ].copy()
    s["post"] = s["post_year2021"].astype(float)
    s["above"] = s["above400"].astype(float)
    s["highpremium"] = s["high_pre_premium_burden"].astype(float)
    s["excess_burden"] = s["pre_2021_age60_excess_burden"].astype(float)
    s["excess_burden_std"] = (s["excess_burden"] - s["excess_burden"].mean()) / s["excess_burden"].std()
    s["above_post_high"] = s["above"] * s["post"] * s["highpremium"]
    s["above_post_excess"] = s["above"] * s["post"] * s["excess_burden_std"]
    s["above_post_older"] = s["above"] * s["post"] * s["older50"]
    s["above_post_high_older"] = s["above"] * s["post"] * s["highpremium"] * s["older50"]
    s["kernel"] = (1 - (s["running"].abs() / 0.5)).clip(lower=0)
    s["analysis_weight"] = s["weight"] * s["kernel"]
    return s


def estimate(s: pd.DataFrame, term: str, outcomes: list[str], model: str) -> pd.DataFrame:
    base_terms = [
        "above",
        "post",
        "highpremium",
        "older50",
        "above_post",
        "above_high",
        "post_high",
        "above_older",
        "post_older",
        "high_older",
        "running",
        "running_above",
        "running_post",
        "running_above_post",
    ]
    d = s.copy()
    d["above_post"] = d["above"] * d["post"]
    d["above_high"] = d["above"] * d["highpremium"]
    d["post_high"] = d["post"] * d["highpremium"]
    d["above_older"] = d["above"] * d["older50"]
    d["post_older"] = d["post"] * d["older50"]
    d["high_older"] = d["highpremium"] * d["older50"]
    d["running_above"] = d["running"] * d["above"]
    d["running_post"] = d["running"] * d["post"]
    d["running_above_post"] = d["running"] * d["above"] * d["post"]
    if term == "above_post_excess":
        d["above_excess"] = d["above"] * d["excess_burden_std"]
        d["post_excess"] = d["post"] * d["excess_burden_std"]
        base_terms = [t for t in base_terms if t not in {"highpremium", "above_high", "post_high", "high_older"}] + [
            "excess_burden_std",
            "above_excess",
            "post_excess",
        ]
    if term == "above_post_high_older":
        d["above_high_older"] = d["above"] * d["highpremium"] * d["older50"]
        d["post_high_older"] = d["post"] * d["highpremium"] * d["older50"]
        d["above_post_older"] = d["above"] * d["post"] * d["older50"]
        d["above_post_high"] = d["above"] * d["post"] * d["highpremium"]
        base_terms += ["above_high_older", "post_high_older", "above_post_older", "above_post_high"]

    parts: list[pd.Series | pd.DataFrame] = [pd.Series(1.0, index=d.index, name="const"), d[term].rename(term)]
    for c in base_terms:
        if c != term and c in d.columns:
            parts.append(d[c].astype(float).rename(c))
    for c in ["age", "female", "black", "hispanic", "disabled"]:
        parts.append(d[c].astype(float).rename(c))
    x = add_fe(parts, d, ["reference_year", "reference_month", "state_fips"])
    x_np = x.to_numpy(dtype=float)
    w_np = d["analysis_weight"].to_numpy(dtype=float)
    rows = []
    for outcome in outcomes:
        beta, se_hc1, se_cluster, n, g = wls_cluster(d[outcome].to_numpy(dtype=float), x_np, w_np, d["state_fips"].to_numpy())
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
                "n": n,
                "persons": int(d["person_id"].nunique()),
                "states": g,
                "weighted_mean": wmean(d[outcome], d["weight"]),
            }
        )
    return pd.DataFrame(rows)


def support(s: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for post in [0, 1]:
        for above in [0, 1]:
            for high in [0, 1]:
                g = s[s["post"].eq(post) & s["above"].eq(above) & s["highpremium"].eq(high)]
                rows.append(
                    {
                        "post": post,
                        "above400": above,
                        "highpremium": high,
                        "person_months": int(len(g)),
                        "persons": int(g["person_id"].nunique()),
                        "states": int(g["state_fips"].nunique()),
                        "uninsured": wmean(g["uninsured"], g["weight"]),
                        "employer_private": wmean(g["employer_private"], g["weight"]),
                        "direct_purchase": wmean(g["direct_purchase"], g["weight"]),
                        "marketplace_flag": wmean(g["marketplace_flag"], g["weight"]),
                    }
                )
    return pd.DataFrame(rows)


def fmt(est: pd.DataFrame, model: str, outcomes: list[str]) -> str:
    d = est[est["model"].eq(model)].set_index("outcome")
    lines = []
    for outcome in outcomes:
        if outcome in d.index:
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
            vals.append(f"{v:.4f}" if isinstance(v, float) else str(v))
        lines.append("| " + " | ".join(vals) + " |")
    return "\n".join(lines)


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    panel = prepare_panel()
    s = sample(panel)
    estimates = pd.concat(
        [
            estimate(s, "above_post_high", OUTCOMES, "binary_high_premium_gradient"),
            estimate(s, "above_post_excess", OUTCOMES, "continuous_excess_burden_gradient"),
            estimate(s, "above_post_older", OUTCOMES, "older_age_gradient"),
            estimate(s, "above_post_high_older", OUTCOMES, "highpremium_older_quadruple"),
        ],
        ignore_index=True,
    )
    sup = support(s)
    estimates.to_csv(OUT / "arpa400_premium_gradient_estimates.csv", index=False)
    sup.to_csv(OUT / "arpa400_premium_gradient_support.csv", index=False)

    report = f"""# ARPA 400% FPL Premium/Age Gradient Test

## Purpose

This test asks whether the ARPA near-400% FPL response is stronger where the subsidy-cliff mechanism
should be strongest: high gross benchmark-premium states and older adults. It uses the augmented
SIPP panel with `RPRITYPE1` employer coverage and the existing CMS Exchange PUF state-year premium
policy file.

## Design

- Unit: person-month.
- Sample: age 26-64, non-Medicare, 350-450% monthly FPL, 2018-2023.
- Geography: states covered by CMS Exchange PUF premium files.
- Premium exposure: pre-2021 state age-60 SLCSP burden above 8.5% of 400% FPL income.
- Main term: above 400% FPL x post-2021 x high pre-premium-burden state.
- Additional tests: continuous premium burden, older age, and high-premium x older-age quadruple.
- FE: year, month, and state.
- SE: state-clustered.

## Support

{md_table(sup, ['post', 'above400', 'highpremium', 'person_months', 'persons', 'states', 'uninsured', 'employer_private', 'direct_purchase', 'marketplace_flag'])}

## Estimates

Binary high-premium gradient:

{fmt(estimates, 'binary_high_premium_gradient', OUTCOMES)}

Continuous excess-premium gradient:

{fmt(estimates, 'continuous_excess_burden_gradient', OUTCOMES)}

Older-age gradient:

{fmt(estimates, 'older_age_gradient', OUTCOMES)}

High-premium x older-age quadruple interaction:

{fmt(estimates, 'highpremium_older_quadruple', OUTCOMES)}

## Interpretation

A clean subsidy-cliff mechanism would predict lower uninsured and stronger Marketplace/direct
purchase gains in high-premium states and among older adults. If the high-premium interaction raises
Marketplace proxies but also raises uninsured, or if older adults do not respond, the current lead
should remain a policy-relevant private-coverage threshold response rather than a clean premium
cliff paper.

## Artifacts

- `script/11_idea_scan/28_arpa_400fpl_premium_gradient_test.py`
- `result/idea_scan/arpa400_premium_gradient_estimates.csv`
- `result/idea_scan/arpa400_premium_gradient_support.csv`
"""
    REPORT.write_text(report, encoding="utf-8")
    print(sup.to_string(index=False))
    print(estimates.to_string(index=False))


if __name__ == "__main__":
    main()
