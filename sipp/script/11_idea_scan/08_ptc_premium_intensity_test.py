from __future__ import annotations

import re
import time
import zipfile
from pathlib import Path

import numpy as np
import pandas as pd
import requests


ROOT = Path(__file__).resolve().parents[2]
PANEL = ROOT / "data" / "analysis_ready" / "sipp_2018_2024_person_month_panel.parquet"
TEMP = ROOT / "temp" / "aca_premium_puf"
OUT = ROOT / "result" / "idea_scan"
REPORT = ROOT / "report" / "20_ptc_premium_intensity_test.md"
CMS_PUF_PAGE = "https://www.cms.gov/marketplace/resources/data/public-use-files"


FIPS_TO_STATE = {
    "01": "AL", "02": "AK", "04": "AZ", "05": "AR", "06": "CA", "08": "CO",
    "09": "CT", "10": "DE", "11": "DC", "12": "FL", "13": "GA", "15": "HI",
    "16": "ID", "17": "IL", "18": "IN", "19": "IA", "20": "KS", "21": "KY",
    "22": "LA", "23": "ME", "24": "MD", "25": "MA", "26": "MI", "27": "MN",
    "28": "MS", "29": "MO", "30": "MT", "31": "NE", "32": "NV", "33": "NH",
    "34": "NJ", "35": "NM", "36": "NY", "37": "NC", "38": "ND", "39": "OH",
    "40": "OK", "41": "OR", "42": "PA", "44": "RI", "45": "SC", "46": "SD",
    "47": "TN", "48": "TX", "49": "UT", "50": "VT", "51": "VA", "53": "WA",
    "54": "WV", "55": "WI", "56": "WY",
}

FPL_SINGLE = {
    # HHS poverty guidelines, one-person household, 48 contiguous states/DC.
    2018: 12140,
    2019: 12490,
    2020: 12760,
    2021: 12880,
    2022: 13590,
    2023: 14580,
}
FPL_SINGLE_AK = {2018: 15180, 2019: 15600, 2020: 15950, 2021: 16090, 2022: 16990, 2023: 18210}
FPL_SINGLE_HI = {2018: 13960, 2019: 14380, 2020: 14680, 2021: 14820, 2022: 15630, 2023: 16770}


def yes(s: pd.Series) -> pd.Series:
    return s.eq(1)


def persons(s: pd.Series) -> int:
    return int(s.dropna().nunique())


def find_cms_urls() -> dict[tuple[int, str], str]:
    html = requests.get(CMS_PUF_PAGE, timeout=60).text
    urls = re.findall(r"https://download\.cms\.gov/marketplace-puf/[^\"]+", html)
    out: dict[tuple[int, str], str] = {}
    for url in urls:
        m = re.search(r"/(20\d{2})/([^/]+\.zip)", url)
        if not m:
            continue
        year = int(m.group(1))
        fname = m.group(2).lower()
        if year < 2018 or year > 2023:
            continue
        if fname == "rate-puf.zip":
            out[(year, "rate")] = url
        elif fname == "plan-attributes-puf.zip":
            out[(year, "plan")] = url
    return out


def download(url: str, dest: Path) -> None:
    if dest.exists() and dest.stat().st_size > 1000:
        return
    last_error: Exception | None = None
    for attempt in range(5):
        try:
            r = requests.get(url, timeout=180)
            r.raise_for_status()
            dest.write_bytes(r.content)
            return
        except Exception as exc:  # network resets are common on these ZIPs
            last_error = exc
            time.sleep(3 + attempt * 3)
    raise RuntimeError(f"Failed to download {url}: {last_error}")


def read_zip_csv(path: Path, usecols: list[str] | None = None) -> pd.DataFrame:
    with zipfile.ZipFile(path) as z:
        csv_name = [n for n in z.namelist() if n.lower().endswith(".csv")][0]
        for encoding in ["utf-8", "cp1252", "latin1"]:
            try:
                with z.open(csv_name) as f:
                    return pd.read_csv(f, usecols=usecols, low_memory=False, encoding=encoding)
            except UnicodeDecodeError:
                continue
        with z.open(csv_name) as f:
            return pd.read_csv(f, usecols=usecols, low_memory=False, encoding="latin1")


def second_lowest(values: pd.Series) -> float:
    arr = np.sort(pd.to_numeric(values, errors="coerce").dropna().unique())
    if len(arr) == 0:
        return np.nan
    if len(arr) == 1:
        return float(arr[0])
    return float(arr[1])


def build_premium_policy() -> pd.DataFrame:
    TEMP.mkdir(parents=True, exist_ok=True)
    urls = find_cms_urls()
    all_rows = []
    for year in range(2018, 2024):
        rate_url = urls.get((year, "rate"), f"https://download.cms.gov/marketplace-puf/{year}/rate-puf.zip")
        plan_url = urls.get((year, "plan"), f"https://download.cms.gov/marketplace-puf/{year}/plan-attributes-puf.zip")
        rate_zip = TEMP / f"{year}_rate-puf.zip"
        plan_zip = TEMP / f"{year}_plan-attributes-puf.zip"
        download(rate_url, rate_zip)
        download(plan_url, plan_zip)

        plan_cols = ["BusinessYear", "StateCode", "StandardComponentId", "MarketCoverage", "DentalOnlyPlan", "MetalLevel"]
        rate_cols = ["BusinessYear", "StateCode", "PlanId", "RatingAreaId", "Age", "IndividualRate"]
        plan = read_zip_csv(plan_zip, usecols=plan_cols)
        plan = plan[
            plan["MarketCoverage"].astype(str).str.contains("Individual", case=False, na=False)
            & plan["DentalOnlyPlan"].astype(str).str.lower().isin(["no", "false", "nan"])
            & plan["MetalLevel"].astype(str).str.lower().eq("silver")
        ][["BusinessYear", "StateCode", "StandardComponentId"]].drop_duplicates()

        chunks = []
        with zipfile.ZipFile(rate_zip) as z:
            csv_name = [n for n in z.namelist() if n.lower().endswith(".csv")][0]
            for encoding in ["utf-8", "cp1252", "latin1"]:
                try:
                    with z.open(csv_name) as f:
                        for chunk in pd.read_csv(f, usecols=rate_cols, chunksize=500_000, low_memory=False, encoding=encoding):
                            chunk = chunk[chunk["Age"].astype(str).isin(["40", "60"])]
                            chunk["IndividualRate"] = pd.to_numeric(chunk["IndividualRate"], errors="coerce")
                            chunk = chunk.dropna(subset=["IndividualRate"])
                            chunks.append(chunk)
                    break
                except UnicodeDecodeError:
                    chunks = []
                    continue
        if not chunks:
            continue
        rate = pd.concat(chunks, ignore_index=True)
        merged = rate.merge(
            plan,
            left_on=["BusinessYear", "StateCode", "PlanId"],
            right_on=["BusinessYear", "StateCode", "StandardComponentId"],
            how="inner",
        )
        # Rate rows can repeat over quarterly effective dates; average plan/rating-area annual rate first.
        plan_ra = (
            merged.groupby(["BusinessYear", "StateCode", "RatingAreaId", "PlanId", "Age"], observed=True)["IndividualRate"]
            .mean()
            .reset_index()
        )
        slcsp_ra = (
            plan_ra.groupby(["BusinessYear", "StateCode", "RatingAreaId", "Age"], observed=True)["IndividualRate"]
            .apply(second_lowest)
            .reset_index(name="slcsp")
        )
        state = (
            slcsp_ra.groupby(["BusinessYear", "StateCode", "Age"], observed=True)
            .agg(
                slcsp_state_mean=("slcsp", "mean"),
                slcsp_state_median=("slcsp", "median"),
                rating_areas=("RatingAreaId", "nunique"),
            )
            .reset_index()
        )
        all_rows.append(state)

    policy_long = pd.concat(all_rows, ignore_index=True)
    policy = policy_long.pivot_table(
        index=["BusinessYear", "StateCode"],
        columns="Age",
        values=["slcsp_state_mean", "slcsp_state_median", "rating_areas"],
        aggfunc="first",
    )
    policy.columns = [f"{a}_age{b}" for a, b in policy.columns]
    policy = policy.reset_index().rename(columns={"BusinessYear": "reference_year", "StateCode": "state"})
    policy["fpl_single"] = policy.apply(
        lambda r: FPL_SINGLE_AK.get(int(r["reference_year"])) if r["state"] == "AK"
        else FPL_SINGLE_HI.get(int(r["reference_year"])) if r["state"] == "HI"
        else FPL_SINGLE.get(int(r["reference_year"])),
        axis=1,
    )
    income_400 = 4 * policy["fpl_single"]
    policy["gross_burden_age60_at400fpl"] = 12 * policy["slcsp_state_mean_age60"] / income_400
    policy["gross_burden_age40_at400fpl"] = 12 * policy["slcsp_state_mean_age40"] / income_400
    policy["gross_burden_excess_age60_over_8p5"] = (policy["gross_burden_age60_at400fpl"] - 0.085).clip(lower=0)
    pre = (
        policy[policy["reference_year"].between(2018, 2020)]
        .groupby("state", observed=True)["gross_burden_excess_age60_over_8p5"]
        .mean()
        .rename("pre_2021_age60_excess_burden")
        .reset_index()
    )
    med = pre["pre_2021_age60_excess_burden"].median()
    pre["high_pre_premium_burden"] = pre["pre_2021_age60_excess_burden"].ge(med).astype(int)
    policy = policy.merge(pre, on="state", how="left")
    return policy


def wls_hc1(y: np.ndarray, x: np.ndarray, w: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    mask = np.isfinite(y) & np.isfinite(w) & (w > 0) & np.all(np.isfinite(x), axis=1)
    y = y[mask]
    x = x[mask]
    w = w[mask]
    if len(y) <= x.shape[1] + 5:
        return np.full(x.shape[1], np.nan), np.full(x.shape[1], np.nan)
    sw = np.sqrt(w / np.nanmean(w))
    xw = x * sw[:, None]
    yw = y * sw
    inv = np.linalg.pinv(xw.T @ xw)
    beta = inv @ (xw.T @ yw)
    resid = yw - xw @ beta
    meat = xw.T @ ((resid**2)[:, None] * xw)
    n, k = x.shape
    cov = (n / max(n - k, 1)) * inv @ meat @ inv
    return beta, np.sqrt(np.diag(cov))


def read_sipp(policy: pd.DataFrame) -> pd.DataFrame:
    cols = [
        "person_id", "reference_year", "reference_month", "state_fips", "TAGE",
        "WPFINWGT", "TSSSAMT", "RHLTHMTH", "RPRITYPE2", "RMARKTPLACE",
        "RPRIMTH", "EPRIEXCH1", "EPRIEXCH2", "EPRISUBS1", "EPRISUBS2",
        "EMDEXCH", "EMDSUBS", "TFCYINCPOV", "TMDPAY", "TVISDOC", "RMWKWJB", "RMESR",
    ]
    df = pd.read_parquet(PANEL, columns=cols)
    df["state_fips"] = df["state_fips"].astype(str).str.zfill(2)
    df["state"] = df["state_fips"].map(FIPS_TO_STATE)
    df = df[df["reference_year"].between(2018, 2023)].copy()
    df = df.merge(policy, on=["reference_year", "state"], how="left")
    df["age"] = pd.to_numeric(df["TAGE"], errors="coerce")
    df["annual_fpl"] = pd.to_numeric(df["TFCYINCPOV"], errors="coerce")
    df.loc[(df["annual_fpl"] < 0) | (df["annual_fpl"] > 20), "annual_fpl"] = np.nan
    df["adult_26_64"] = df["age"].between(26, 64, inclusive="both")
    df["near_400"] = df["annual_fpl"].between(3.0, 5.0, inclusive="both")
    df["above400"] = df["annual_fpl"].gt(4.0).astype(int)
    df["post2021"] = df["reference_year"].ge(2021).astype(int)
    df["highpremium"] = df["high_pre_premium_burden"].fillna(0).astype(int)
    df["weight"] = pd.to_numeric(df["WPFINWGT"], errors="coerce")
    df["weight"] = df["weight"].where(df["weight"].gt(0), pd.to_numeric(df["TSSSAMT"], errors="coerce"))
    df["weight"] = df["weight"].where(df["weight"].gt(0), 1.0)
    df["direct_purchase"] = yes(df["RPRITYPE2"]) | yes(df["RMARKTPLACE"])
    df["marketplace"] = yes(df["RMARKTPLACE"]) | yes(df["EPRIEXCH1"]) | yes(df["EPRIEXCH2"]) | yes(df["EMDEXCH"])
    df["subsidized_private"] = yes(df["EPRISUBS1"]) | yes(df["EPRISUBS2"]) | yes(df["EMDSUBS"])
    df["market_or_subsidy"] = df["marketplace"] | df["subsidized_private"]
    df["uninsured"] = df["RHLTHMTH"].eq(2)
    df["any_coverage"] = yes(df["RHLTHMTH"])
    df["private"] = yes(df["RPRIMTH"])
    df["oop_any"] = pd.to_numeric(df["TMDPAY"], errors="coerce").gt(0)
    df["doctor_any"] = pd.to_numeric(df["TVISDOC"], errors="coerce").gt(0)
    df["working_any_week"] = pd.to_numeric(df["RMWKWJB"], errors="coerce").gt(0) | pd.to_numeric(df["RMESR"], errors="coerce").between(1, 5)
    return df


def estimate(df: pd.DataFrame, outcome: str) -> dict:
    sample = df[df["adult_26_64"] & df["near_400"] & df["pre_2021_age60_excess_burden"].notna()].copy()
    sample["post_x_above_x_high"] = sample["post2021"] * sample["above400"] * sample["highpremium"]
    sample["post_x_above"] = sample["post2021"] * sample["above400"]
    sample["post_x_high"] = sample["post2021"] * sample["highpremium"]
    sample["above_x_high"] = sample["above400"] * sample["highpremium"]
    state_fe = pd.get_dummies(sample["state"], prefix="st", drop_first=True, dtype=float)
    year_fe = pd.get_dummies(sample["reference_year"].astype(str), prefix="yr", drop_first=True, dtype=float)
    x = pd.concat(
        [
            pd.Series(1.0, index=sample.index, name="const"),
            sample[[
                "post_x_above_x_high",
                "post_x_above",
                "post_x_high",
                "above_x_high",
                "above400",
                "highpremium",
            ]],
            state_fe,
            year_fe,
        ],
        axis=1,
    )
    beta, se = wls_hc1(sample[outcome].astype(float).to_numpy(), x.to_numpy(float), sample["weight"].to_numpy(float))
    idx = list(x.columns).index("post_x_above_x_high")
    cells = sample.groupby(["post2021", "above400", "highpremium"], observed=True).agg(
        rows=("person_id", "size"), persons=("person_id", "nunique"), events=(outcome, "sum")
    ).reset_index()
    return {
        "outcome": outcome,
        "coef_post_x_above400_x_highpremium": float(beta[idx]),
        "se_hc1": float(se[idx]),
        "t_stat": float(beta[idx] / se[idx]) if se[idx] > 0 else np.nan,
        "rows": int(len(sample)),
        "persons": persons(sample["person_id"]),
        "states": int(sample["state"].nunique()),
        "min_cell_persons": int(cells["persons"].min()) if not cells.empty else 0,
        "min_cell_events": int(cells["events"].min()) if not cells.empty else 0,
    }


def support(df: pd.DataFrame, policy: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    sample = df[df["adult_26_64"] & df["near_400"] & df["pre_2021_age60_excess_burden"].notna()].copy()
    supp = sample.groupby(["post2021", "above400", "highpremium"], observed=True).agg(
        rows=("person_id", "size"),
        persons=("person_id", "nunique"),
        market_events=("market_or_subsidy", "sum"),
        uninsured_events=("uninsured", "sum"),
        states=("state", "nunique"),
    ).reset_index()
    states = policy.groupby("state", observed=True).agg(
        years=("reference_year", "nunique"),
        pre_2021_age60_excess_burden=("pre_2021_age60_excess_burden", "first"),
        high_pre_premium_burden=("high_pre_premium_burden", "first"),
        mean_age60_burden=("gross_burden_age60_at400fpl", "mean"),
        rating_areas=("rating_areas_age60", "max"),
    ).reset_index()
    return supp, states


def write_report(policy: pd.DataFrame, estimates: pd.DataFrame, supp: pd.DataFrame, states: pd.DataFrame) -> None:
    main = estimates[estimates["outcome"].isin(["market_or_subsidy", "direct_purchase", "uninsured", "any_coverage", "oop_any"])].sort_values("outcome")
    cols = ["outcome", "coef_post_x_above400_x_highpremium", "se_hc1", "t_stat", "persons", "states", "min_cell_persons"]
    lines = ["| " + " | ".join(cols) + " |", "|" + "|".join(["---"] * len(cols)) + "|"]
    for _, r in main.iterrows():
        vals = []
        for c in cols:
            v = r[c]
            vals.append(f"{v:.4f}" if isinstance(v, float) else str(v))
        lines.append("| " + " | ".join(vals) + " |")

    support_lines = ["| post | above400 | high premium | persons | market events | uninsured events | states |", "|---:|---:|---:|---:|---:|---:|---:|"]
    for _, r in supp.sort_values(["post2021", "above400", "highpremium"]).iterrows():
        support_lines.append(
            f"| {int(r['post2021'])} | {int(r['above400'])} | {int(r['highpremium'])} | {int(r['persons'])} | {int(r['market_events'])} | {int(r['uninsured_events'])} | {int(r['states'])} |"
        )
    m = main.loc[main["outcome"].eq("market_or_subsidy")]
    if m.empty:
        verdict = "INCOMPLETE"
    elif m.iloc[0]["min_cell_persons"] < 1000:
        verdict = "SUPPORT-THIN"
    elif abs(m.iloc[0]["t_stat"]) >= 1.5:
        verdict = "PREMIUM-INTENSITY-SIGNAL-PRESENT-BUT-CHECK-DIRECTION"
    else:
        verdict = "SUPPORT-YES-SIGNAL-WEAK"

    report = f"""# PTC 400% FPL Premium-Intensity Test

## Verdict

`{verdict}`

This test adds the missing policy-intensity layer to the leading ACA affordability idea using CMS
Exchange Public Use Files. It is still a state-level approximation because the uploaded SIPP parquet
does not contain county or rating area.

## Data Built

- CMS Exchange PUF years: 2018-2023.
- Files used: Rate-PUF and Plan Attributes PUF.
- Plan filter: individual-market, non-dental, silver plans.
- Premium proxy: unweighted state average of rating-area second-lowest silver premiums for ages
  40 and 60.
- Treatment intensity: pre-2021 age-60 gross benchmark burden at 400% FPL above the 8.5% ARPA cap.

PUF state coverage is incomplete by construction because CMS Exchange PUFs generally exclude states
whose State-Based Exchanges do not rely on the federal platform.

## Support Cells

{chr(10).join(support_lines)}

## Triple-Difference Screen

Sample: adults 26-64, annual family income 300-500% FPL, PUF-covered states, SIPP reference years
2018-2023. Coefficient is `post2021 x above400 x high_pre_premium_burden`.

{chr(10).join(lines)}

## Interpretation

- This is the first version that directly tests the premium-intensity idea rather than only the
  400% FPL cliff.
- If the high-premium interaction does not recover a coherent market/subsidy or uninsured pattern,
  then the PTC project remains conditional rather than clean.
- A paper-quality version still needs county/rating-area matching or benchmark premium data mapped
  to geography finer than state.

## Source Checks

- CMS Exchange PUF page:
  https://www.cms.gov/marketplace/resources/data/public-use-files
- CMS notes that Rate-PUF reports rates by age, tobacco, and geographic location, and Plan-PUF
  identifies plan attributes including metal level.

## Outputs

- `result/idea_scan/ptc_premium_policy_state_year.csv`
- `result/idea_scan/ptc_premium_state_support.csv`
- `result/idea_scan/ptc_premium_intensity_support.csv`
- `result/idea_scan/ptc_premium_intensity_estimates.csv`
"""
    REPORT.write_text(report, encoding="utf-8")


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    policy = build_premium_policy()
    policy.to_csv(OUT / "ptc_premium_policy_state_year.csv", index=False)
    df = read_sipp(policy)
    outcomes = [
        "direct_purchase",
        "marketplace",
        "subsidized_private",
        "market_or_subsidy",
        "uninsured",
        "any_coverage",
        "private",
        "oop_any",
        "doctor_any",
        "working_any_week",
    ]
    estimates = pd.DataFrame([estimate(df, out) for out in outcomes])
    supp, states = support(df, policy)
    estimates.to_csv(OUT / "ptc_premium_intensity_estimates.csv", index=False)
    supp.to_csv(OUT / "ptc_premium_intensity_support.csv", index=False)
    states.to_csv(OUT / "ptc_premium_state_support.csv", index=False)
    write_report(policy, estimates, supp, states)
    print(f"Wrote report to {REPORT}")


if __name__ == "__main__":
    main()
