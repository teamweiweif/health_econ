from __future__ import annotations

import re
from pathlib import Path

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[2]
PANEL = ROOT / "data" / "analysis_ready" / "sipp_2018_2024_person_month_panel.parquet"
OUT = ROOT / "result" / "idea_scan"
REPORT = ROOT / "report" / "15_minimum_wage_spillover_fast_test.md"
DOL_HISTORY = "https://www.dol.gov/agencies/whd/state/minimum-wage/history"


STATE_TO_FIPS = {
    "Alabama": "01",
    "Alaska": "02",
    "Arizona": "04",
    "Arkansas": "05",
    "California": "06",
    "Colorado": "08",
    "Connecticut": "09",
    "Delaware": "10",
    "District of Columbia": "11",
    "Florida": "12",
    "Georgia": "13",
    "Hawaii": "15",
    "Idaho": "16",
    "Illinois": "17",
    "Indiana": "18",
    "Iowa": "19",
    "Kansas": "20",
    "Kentucky": "21",
    "Louisiana": "22",
    "Maine": "23",
    "Maryland": "24",
    "Massachusetts": "25",
    "Michigan": "26",
    "Minnesota": "27",
    "Mississippi": "28",
    "Missouri": "29",
    "Montana": "30",
    "Nebraska": "31",
    "Nevada": "32",
    "New Hampshire": "33",
    "New Jersey": "34",
    "New Mexico": "35",
    "New York": "36",
    "North Carolina": "37",
    "North Dakota": "38",
    "Ohio": "39",
    "Oklahoma": "40",
    "Oregon": "41",
    "Pennsylvania": "42",
    "Rhode Island": "44",
    "South Carolina": "45",
    "South Dakota": "46",
    "Tennessee": "47",
    "Texas": "48",
    "Utah": "49",
    "Vermont": "50",
    "Virginia": "51",
    "Washington": "53",
    "West Virginia": "54",
    "Wisconsin": "55",
    "Wyoming": "56",
}


def yes(s: pd.Series) -> pd.Series:
    return s.eq(1)


def clean_weight(df: pd.DataFrame) -> pd.Series:
    w = pd.to_numeric(df.get("WPFINWGT"), errors="coerce")
    return w.where(w.gt(0))


def persons(s: pd.Series) -> int:
    return int(s.dropna().nunique())


def wmean(y: pd.Series, w: pd.Series) -> float:
    mask = y.notna() & w.notna() & (w > 0)
    if not mask.any():
        return np.nan
    return float(np.average(y[mask].astype(float), weights=w[mask].astype(float)))


def parse_wage(value: object) -> float:
    if pd.isna(value):
        return np.nan
    text = str(value)
    if "..." in text or text.strip() in {"", "nan", "N.A."}:
        return np.nan
    nums = re.findall(r"\d+(?:\.\d+)?", text.replace("$", ""))
    if not nums:
        return np.nan
    # For ranges or firm-size variants, this screen uses the highest statewide value.
    return max(float(x) for x in nums)


def read_minimum_wage_policy() -> pd.DataFrame:
    tables = pd.read_html(DOL_HISTORY)
    raw = pd.concat(tables, axis=1)
    raw = raw.loc[:, ~raw.columns.duplicated()]
    raw = raw.rename(columns={"State or other jurisdiction": "state"})
    year_cols = [c for c in raw.columns if str(c).isdigit()]
    rows = []
    federal_row = raw[raw["state"].eq("Federal (FLSA)")].iloc[0]
    federal = {int(y): parse_wage(federal_row[y]) for y in year_cols}
    for _, r in raw.iterrows():
        state = r["state"]
        if state not in STATE_TO_FIPS:
            continue
        for y in year_cols:
            year = int(y)
            if year < 2017 or year > 2024:
                continue
            state_wage = parse_wage(r[y])
            floor = federal.get(year, 7.25)
            effective = max(state_wage if pd.notna(state_wage) else floor, floor)
            rows.append({"state": state, "state_fips": STATE_TO_FIPS[state], "year": year, "minimum_wage": effective})
    policy = pd.DataFrame(rows).sort_values(["state_fips", "year"])
    policy["mw_lag"] = policy.groupby("state_fips")["minimum_wage"].shift(1)
    policy["mw_change"] = policy["minimum_wage"] - policy["mw_lag"]
    policy["mw_increase"] = policy["mw_change"].clip(lower=0).fillna(0)
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
    n, k = xw.shape
    cov = (n / max(n - k, 1)) * inv @ meat @ inv
    return beta, np.sqrt(np.diag(cov))


def read_panel(policy: pd.DataFrame) -> pd.DataFrame:
    cols = [
        "person_id",
        "reference_year",
        "reference_month",
        "state_fips",
        "TAGE",
        "ESEX",
        "ERACE",
        "EORIGIN",
        "EEDUC",
        "WPFINWGT",
        "TSSSAMT",
        "RMESR",
        "RMWKWJB",
        "TPEARN",
        "TPTOTINC",
        "TFINCPOV",
        "RSNAP_MNYN",
        "RTANF_MNYN",
        "RSSI_MNYN",
        "RHLTHMTH",
        "EMDMTH",
        "RPRIMTH",
        "RPRITYPE2",
        "TMDPAY",
        "TVISDOC",
    ]
    df = pd.read_parquet(PANEL, columns=cols)
    df["state_fips"] = df["state_fips"].astype(str).str.zfill(2)
    df = df[df["reference_year"].between(2018, 2023)].copy()
    df = df.merge(policy.rename(columns={"year": "reference_year"}), on=["state_fips", "reference_year"], how="left")
    df["age"] = pd.to_numeric(df["TAGE"], errors="coerce")
    df["adult_19_64"] = df["age"].between(19, 64, inclusive="both")
    df["prime_25_54"] = df["age"].between(25, 54, inclusive="both")
    educ = pd.to_numeric(df["EEDUC"], errors="coerce")
    df["hs_or_less"] = educ.le(39)
    df["some_college_or_more"] = educ.ge(40)
    df["weight"] = clean_weight(df)
    df["employed_any_week"] = pd.to_numeric(df["RMWKWJB"], errors="coerce").gt(0) | pd.to_numeric(df["RMESR"], errors="coerce").between(1, 5)
    df["earnings"] = pd.to_numeric(df["TPEARN"], errors="coerce").where(lambda x: x.between(-100000, 100000))
    df["earnings_positive"] = df["earnings"].gt(0)
    weeks = pd.to_numeric(df["RMWKWJB"], errors="coerce")
    df["hourly_proxy"] = df["earnings"] / (weeks.clip(lower=1) * 40)
    df.loc[~df["hourly_proxy"].between(0, 200), "hourly_proxy"] = np.nan
    df["snap"] = yes(df["RSNAP_MNYN"])
    df["tanf"] = yes(df["RTANF_MNYN"])
    df["ssi"] = yes(df["RSSI_MNYN"])
    df["medicaid"] = yes(df["EMDMTH"])
    df["uninsured"] = df["RHLTHMTH"].eq(2)
    df["private"] = yes(df["RPRIMTH"])
    df["direct_purchase"] = yes(df["RPRITYPE2"])
    df["oop_any"] = pd.to_numeric(df["TMDPAY"], errors="coerce").gt(0)
    df["doctor_any"] = pd.to_numeric(df["TVISDOC"], errors="coerce").gt(0)
    df["low_educ_x_mw_increase"] = df["hs_or_less"].astype(int) * df["mw_increase"].fillna(0)
    return df


def estimate(df: pd.DataFrame, outcome: str, sample_name: str, sample_mask: pd.Series) -> dict:
    sample = df[df["adult_19_64"] & sample_mask & df["mw_increase"].notna() & df["EEDUC"].notna()].copy()
    state_fe = pd.get_dummies(sample["state_fips"], prefix="st", drop_first=True, dtype=float)
    year_fe = pd.get_dummies(sample["reference_year"].astype(str), prefix="yr", drop_first=True, dtype=float)
    x = pd.concat(
        [
            pd.Series(1.0, index=sample.index, name="const"),
            sample[["low_educ_x_mw_increase", "mw_increase"]],
            sample["hs_or_less"].astype(float).rename("hs_or_less"),
            state_fe,
            year_fe,
        ],
        axis=1,
    )
    y = sample[outcome].astype(float).to_numpy()
    beta, se = wls_hc1(y, x.to_numpy(float), sample["weight"].to_numpy(float))
    idx = list(x.columns).index("low_educ_x_mw_increase")
    treated = sample[sample["mw_increase"].gt(0) & sample["hs_or_less"]]
    exposed_controls = sample[sample["mw_increase"].eq(0) & sample["hs_or_less"]]
    return {
        "sample": sample_name,
        "outcome": outcome,
        "coef_low_educ_x_mw_increase": float(beta[idx]),
        "se_hc1": float(se[idx]),
        "t_stat": float(beta[idx] / se[idx]) if se[idx] > 0 else np.nan,
        "rows": int(len(sample)),
        "persons": persons(sample["person_id"]),
        "treated_low_educ_rows": int(len(treated)),
        "treated_low_educ_persons": persons(treated["person_id"]),
        "treated_low_educ_events": int(treated[outcome].sum()) if sample[outcome].dropna().isin([True, False, 0, 1]).all() else np.nan,
        "treated_low_educ_mean_w": wmean(treated[outcome], treated["weight"]),
        "control_low_educ_mean_w": wmean(exposed_controls[outcome], exposed_controls["weight"]),
    }


def support(df: pd.DataFrame, policy: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    pol = policy[policy["year"].between(2018, 2023)].copy()
    pol["increase_gt_50c"] = pol["mw_increase"].ge(0.5)
    rows = []
    for y, g in pol.groupby("year"):
        rows.append(
            {
                "year": y,
                "states_with_any_increase": int(g["mw_increase"].gt(0).sum()),
                "states_with_50c_increase": int(g["increase_gt_50c"].sum()),
                "mean_increase": float(g.loc[g["mw_increase"].gt(0), "mw_increase"].mean()) if g["mw_increase"].gt(0).any() else 0.0,
            }
        )
    low = df[df["adult_19_64"] & df["hs_or_less"]]
    high = df[df["adult_19_64"] & df["some_college_or_more"]]
    sample_support = pd.DataFrame(
        [
            {
                "group": "adult_hs_or_less",
                "rows": int(len(low)),
                "persons": persons(low["person_id"]),
                "treated_rows_any_mw_increase": int(low["mw_increase"].gt(0).sum()),
                "treated_persons_any_mw_increase": persons(low.loc[low["mw_increase"].gt(0), "person_id"]),
                "snap_events": int(low["snap"].sum()),
                "medicaid_events": int(low["medicaid"].sum()),
                "uninsured_events": int(low["uninsured"].sum()),
            },
            {
                "group": "adult_some_college_plus",
                "rows": int(len(high)),
                "persons": persons(high["person_id"]),
                "treated_rows_any_mw_increase": int(high["mw_increase"].gt(0).sum()),
                "treated_persons_any_mw_increase": persons(high.loc[high["mw_increase"].gt(0), "person_id"]),
                "snap_events": int(high["snap"].sum()),
                "medicaid_events": int(high["medicaid"].sum()),
                "uninsured_events": int(high["uninsured"].sum()),
            },
        ]
    )
    return pd.DataFrame(rows), sample_support


def write_report(est: pd.DataFrame, year_support: pd.DataFrame, sample_support: pd.DataFrame) -> None:
    main = est[est["sample"].eq("adult_19_64")].copy()
    cols = ["outcome", "coef_low_educ_x_mw_increase", "se_hc1", "t_stat", "persons", "treated_low_educ_persons", "treated_low_educ_mean_w"]
    lines = ["| " + " | ".join(cols) + " |", "|" + "|".join(["---"] * len(cols)) + "|"]
    for _, r in main.sort_values("outcome").iterrows():
        vals = []
        for c in cols:
            v = r[c]
            vals.append(f"{v:.4f}" if isinstance(v, float) else str(v))
        lines.append("| " + " | ".join(vals) + " |")
    ys = ["| year | states any increase | states >= $0.50 | mean positive increase |", "|---:|---:|---:|---:|"]
    for _, r in year_support.iterrows():
        ys.append(f"| {int(r['year'])} | {int(r['states_with_any_increase'])} | {int(r['states_with_50c_increase'])} | {r['mean_increase']:.2f} |")
    ss = ["| group | persons | treated persons | SNAP events | Medicaid events | uninsured events |", "|---|---:|---:|---:|---:|---:|"]
    for _, r in sample_support.iterrows():
        ss.append(
            f"| {r['group']} | {int(r['persons'])} | {int(r['treated_persons_any_mw_increase'])} | {int(r['snap_events'])} | {int(r['medicaid_events'])} | {int(r['uninsured_events'])} |"
        )
    med = main.loc[main["outcome"].eq("medicaid")]
    snap = main.loc[main["outcome"].eq("snap")]
    if sample_support.loc[sample_support["group"].eq("adult_hs_or_less"), "treated_persons_any_mw_increase"].iloc[0] >= 10000:
        if (not med.empty and abs(med.iloc[0]["t_stat"]) >= 1.5) or (not snap.empty and abs(snap.iloc[0]["t_stat"]) >= 1.5):
            verdict = "LARGE-SUPPORT-NAIVE-SPILLOVER-SIGNAL-BUT-ID-WEAK"
        else:
            verdict = "LARGE-SUPPORT-BUT-SPILLOVER-WEAK"
    else:
        verdict = "SUPPORT-THIN"
    report = f"""# Minimum Wage Spillover Fast Test

## Verdict

`{verdict}`

This is feasible with the current SIPP parquet and official DOL policy data, but it is not yet a
top-field idea by itself. The minimum-wage employment/wage literature is crowded, and the uploaded
parquet lacks occupation, industry, and clean pre-policy hourly wages. The only possible SIPP
contribution is a safety-net and insurance spillover paper: do wage floors reduce Medicaid/SNAP
receipt, change uninsured risk, or alter medical financial exposure among exposed adults?

## Policy/Data Construction

- Source: U.S. Department of Labor historical state minimum wage table.
- Effective wage: max(state listed wage, federal floor); for ranges this fast screen uses the
  highest listed statewide value.
- Treatment intensity: annual state minimum-wage increase from the previous January.
- Exposure group: adults 19-64 with high school or less.
- Comparison group: adults with some college or more.
- Model: weighted individual-month DDD screen with state and year fixed effects. This is a screen,
  not a final clustered event-study design.
- Coefficient: `minimum wage increase x high-school-or-less`.

## Policy Support By Year

{chr(10).join(ys)}

## SIPP Support

{chr(10).join(ss)}

## Adult 19-64 Fast DDD Results

{chr(10).join(lines)}

## Interpretation

- Sample support is large.
- The identifying variation is real but broad; the standard errors here are screening standard
  errors, not final clustered inference. A publishable design would need a sharper exposure
  measure, ideally occupation/industry or pre-policy hourly wage. The uploaded parquet lacks those.
- If treated as a SIPP safety-net-spillover paper, this is a secondary candidate. It is weaker than
  the UI early-exit timing design and less directly tied to insurance than the PTC cliff.

## Next Checks

1. Add occupation/industry or baseline hourly-wage exposure if available in a richer SIPP extract.
2. Use event studies around states with large increases only.
3. Check SNAP/Medicaid crowd-out and uninsured effects with placebo high-education groups.
4. Do not headline ordinary wage/employment effects unless the contribution is explicitly tied to
   safety-net and insurance spillovers.

## Source Check

- U.S. Department of Labor historical state minimum wage table:
  https://www.dol.gov/agencies/whd/state/minimum-wage/history
- DOL current state minimum wage table:
  https://www.dol.gov/agencies/whd/minimum-wage/state

## Outputs

- `result/idea_scan/minimum_wage_policy_dol_history.csv`
- `result/idea_scan/minimum_wage_spillover_estimates.csv`
- `result/idea_scan/minimum_wage_spillover_year_support.csv`
- `result/idea_scan/minimum_wage_spillover_sample_support.csv`
"""
    REPORT.write_text(report, encoding="utf-8")


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    policy = read_minimum_wage_policy()
    df = read_panel(policy)
    outcomes = [
        "employed_any_week",
        "earnings_positive",
        "snap",
        "tanf",
        "ssi",
        "medicaid",
        "uninsured",
        "private",
        "direct_purchase",
        "oop_any",
        "doctor_any",
    ]
    rows = []
    masks = {
        "adult_19_64": df["adult_19_64"],
        "prime_25_54": df["prime_25_54"],
        "working_adults": df["adult_19_64"] & df["employed_any_week"],
    }
    for sample_name, mask in masks.items():
        for outcome in outcomes:
            rows.append(estimate(df, outcome, sample_name, mask))
    est = pd.DataFrame(rows)
    year_support, sample_support = support(df, policy)
    policy.to_csv(OUT / "minimum_wage_policy_dol_history.csv", index=False)
    est.to_csv(OUT / "minimum_wage_spillover_estimates.csv", index=False)
    year_support.to_csv(OUT / "minimum_wage_spillover_year_support.csv", index=False)
    sample_support.to_csv(OUT / "minimum_wage_spillover_sample_support.csv", index=False)
    write_report(est, year_support, sample_support)
    print(f"Wrote report to {REPORT}")


if __name__ == "__main__":
    main()
