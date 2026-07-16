from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[2]
PANEL = ROOT / "data" / "analysis_ready" / "sipp_2018_2024_person_month_panel.parquet"
OUT = ROOT / "result" / "idea_scan"
REPORT = ROOT / "report" / "14_pandemic_ui_early_exit_fast_test.md"


STATE = {
    "AL": "01",
    "AK": "02",
    "AZ": "04",
    "AR": "05",
    "CA": "06",
    "CO": "08",
    "CT": "09",
    "DE": "10",
    "DC": "11",
    "FL": "12",
    "GA": "13",
    "HI": "15",
    "ID": "16",
    "IL": "17",
    "IN": "18",
    "IA": "19",
    "KS": "20",
    "KY": "21",
    "LA": "22",
    "ME": "23",
    "MD": "24",
    "MA": "25",
    "MI": "26",
    "MN": "27",
    "MS": "28",
    "MO": "29",
    "MT": "30",
    "NE": "31",
    "NV": "32",
    "NH": "33",
    "NJ": "34",
    "NM": "35",
    "NY": "36",
    "NC": "37",
    "ND": "38",
    "OH": "39",
    "OK": "40",
    "OR": "41",
    "PA": "42",
    "RI": "44",
    "SC": "45",
    "SD": "46",
    "TN": "47",
    "TX": "48",
    "UT": "49",
    "VT": "50",
    "VA": "51",
    "WA": "53",
    "WV": "54",
    "WI": "55",
    "WY": "56",
}


# States that ended at least FPUC before the September 2021 federal expiration.
# This screen treats June 2021 as transition and uses July-August as the post period.
EARLY_EXIT_STATES = {
    "AL",
    "AK",
    "AZ",
    "AR",
    "FL",
    "GA",
    "ID",
    "IN",
    "IA",
    "LA",
    "MD",
    "MS",
    "MO",
    "MT",
    "NE",
    "NH",
    "ND",
    "OH",
    "OK",
    "SC",
    "SD",
    "TN",
    "TX",
    "UT",
    "WV",
    "WY",
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


def read_panel() -> pd.DataFrame:
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
        "EUC1MNYN",
        "EUC2MNYN",
        "EUC3MNYN",
        "RMESR",
        "RMWKWJB",
        "TPEARN",
        "TPTOTINC",
        "TFINCPOV",
        "TFCYINCPOV",
        "RSNAP_MNYN",
        "RTANF_MNYN",
        "RSSI_MNYN",
        "RHLTHMTH",
        "EMDMTH",
        "RPRIMTH",
        "RPRITYPE2",
        "TMDPAY",
        "TVISDOC",
        "TDAYSICK",
    ]
    df = pd.read_parquet(PANEL, columns=cols)
    df = df[df["reference_year"].eq(2021)].copy()
    df["state_fips"] = df["state_fips"].astype(str).str.zfill(2)
    df["age"] = pd.to_numeric(df["TAGE"], errors="coerce")
    df["prime_age"] = df["age"].between(25, 54, inclusive="both")
    df["weight"] = clean_weight(df)
    df["early_exit"] = df["state_fips"].isin({STATE[s] for s in EARLY_EXIT_STATES}).astype(int)
    df["pre"] = df["reference_month"].between(2, 5).astype(int)
    df["post"] = df["reference_month"].between(7, 8).astype(int)
    df["analysis_month"] = df["pre"].eq(1) | df["post"].eq(1)
    df["uc_any"] = yes(df["EUC1MNYN"]) | yes(df["EUC2MNYN"]) | yes(df["EUC3MNYN"])
    df["employed_any_week"] = pd.to_numeric(df["RMWKWJB"], errors="coerce").gt(0) | pd.to_numeric(df["RMESR"], errors="coerce").between(1, 5)
    df["no_job_all_month"] = pd.to_numeric(df["RMWKWJB"], errors="coerce").eq(0)
    df["looking_or_layoff_all_month"] = pd.to_numeric(df["RMESR"], errors="coerce").eq(6)
    df["earnings_positive"] = pd.to_numeric(df["TPEARN"], errors="coerce").gt(0)
    df["earnings"] = pd.to_numeric(df["TPEARN"], errors="coerce").where(lambda x: x.between(-100000, 100000))
    df["personal_income"] = pd.to_numeric(df["TPTOTINC"], errors="coerce").where(lambda x: x.between(-100000, 100000))
    df["snap"] = yes(df["RSNAP_MNYN"])
    df["tanf"] = yes(df["RTANF_MNYN"])
    df["ssi"] = yes(df["RSSI_MNYN"])
    df["medicaid"] = yes(df["EMDMTH"])
    df["uninsured"] = df["RHLTHMTH"].eq(2)
    df["private"] = yes(df["RPRIMTH"])
    df["direct_purchase"] = yes(df["RPRITYPE2"])
    df["oop_any"] = pd.to_numeric(df["TMDPAY"], errors="coerce").gt(0)
    df["doctor_any"] = pd.to_numeric(df["TVISDOC"], errors="coerce").gt(0)
    df["sick_days_any"] = pd.to_numeric(df["TDAYSICK"], errors="coerce").gt(0)
    pre = df[df["reference_month"].between(1, 5) & df["prime_age"]]
    risk = pre.groupby("person_id").agg(
        at_risk_uc=("uc_any", "max"),
        at_risk_nonemployment=("no_job_all_month", "max"),
        at_risk_layofflooking=("looking_or_layoff_all_month", "max"),
    )
    risk["at_risk_broad"] = risk[["at_risk_uc", "at_risk_nonemployment", "at_risk_layofflooking"]].any(axis=1)
    df = df.merge(risk.reset_index(), on="person_id", how="left")
    for col in ["at_risk_uc", "at_risk_nonemployment", "at_risk_layofflooking", "at_risk_broad"]:
        df[col] = df[col].fillna(False).astype(bool)
    return df


def estimate(df: pd.DataFrame, sample_flag: str, outcome: str) -> dict:
    sample = df[df["prime_age"] & df["analysis_month"] & df[sample_flag]].copy()
    sample["post_period"] = sample["post"].astype(int)
    sample["early_x_post"] = sample["early_exit"] * sample["post_period"]
    state_fe = pd.get_dummies(sample["state_fips"], prefix="st", drop_first=True, dtype=float)
    month_fe = pd.get_dummies(sample["reference_month"].astype(str), prefix="m", drop_first=True, dtype=float)
    x = pd.concat(
        [
            pd.Series(1.0, index=sample.index, name="const"),
            sample[["early_x_post"]],
            state_fe,
            month_fe,
        ],
        axis=1,
    )
    y = sample[outcome].astype(float).to_numpy()
    beta, se = wls_hc1(y, x.to_numpy(float), sample["weight"].to_numpy(float))
    idx = list(x.columns).index("early_x_post")
    cell = (
        sample.groupby(["early_exit", "post_period"], observed=True)
        .agg(rows=("person_id", "size"), persons=("person_id", "nunique"), events=(outcome, "sum"), weight=("weight", "sum"))
        .reset_index()
    )
    value = {}
    for _, r in cell.iterrows():
        key = (int(r["early_exit"]), int(r["post_period"]))
        value[key] = wmean(
            sample.loc[(sample["early_exit"].eq(key[0])) & (sample["post_period"].eq(key[1])), outcome],
            sample.loc[(sample["early_exit"].eq(key[0])) & (sample["post_period"].eq(key[1])), "weight"],
        )
    return {
        "sample": sample_flag,
        "outcome": outcome,
        "coef_early_x_post": float(beta[idx]),
        "se_hc1": float(se[idx]),
        "t_stat": float(beta[idx] / se[idx]) if se[idx] > 0 else np.nan,
        "rows": int(len(sample)),
        "persons": persons(sample["person_id"]),
        "early_persons": persons(sample.loc[sample["early_exit"].eq(1), "person_id"]),
        "control_persons": persons(sample.loc[sample["early_exit"].eq(0), "person_id"]),
        "min_cell_persons": int(cell["persons"].min()) if not cell.empty else 0,
        "pre_early_mean_w": value.get((1, 0), np.nan),
        "post_early_mean_w": value.get((1, 1), np.nan),
        "pre_control_mean_w": value.get((0, 0), np.nan),
        "post_control_mean_w": value.get((0, 1), np.nan),
    }


def support(df: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for sample_flag in ["at_risk_uc", "at_risk_layofflooking", "at_risk_nonemployment", "at_risk_broad"]:
        sample = df[df["prime_age"] & df[sample_flag]]
        rows.append(
            {
                "sample": sample_flag,
                "persons": persons(sample["person_id"]),
                "early_persons": persons(sample.loc[sample["early_exit"].eq(1), "person_id"]),
                "control_persons": persons(sample.loc[sample["early_exit"].eq(0), "person_id"]),
                "uc_months": int(sample["uc_any"].sum()),
                "nonemployment_months": int(sample["no_job_all_month"].sum()),
                "analysis_rows": int((sample["analysis_month"]).sum()),
            }
        )
    return pd.DataFrame(rows)


def write_report(est: pd.DataFrame, sup: pd.DataFrame) -> None:
    primary = est[est["sample"].eq("at_risk_uc")].copy()
    main_outcomes = ["uc_any", "employed_any_week", "earnings_positive", "snap", "medicaid", "uninsured", "oop_any"]
    primary = primary[primary["outcome"].isin(main_outcomes)].sort_values("outcome")
    cols = ["outcome", "coef_early_x_post", "se_hc1", "t_stat", "persons", "early_persons", "control_persons", "min_cell_persons"]
    lines = ["| " + " | ".join(cols) + " |", "|" + "|".join(["---"] * len(cols)) + "|"]
    for _, r in primary.iterrows():
        vals = []
        for c in cols:
            v = r[c]
            vals.append(f"{v:.4f}" if isinstance(v, float) else str(v))
        lines.append("| " + " | ".join(vals) + " |")

    sup_lines = ["| sample | persons | early persons | control persons | UC months | analysis rows |", "|---|---:|---:|---:|---:|---:|"]
    for _, r in sup.iterrows():
        sup_lines.append(
            f"| {r['sample']} | {int(r['persons'])} | {int(r['early_persons'])} | {int(r['control_persons'])} | {int(r['uc_months'])} | {int(r['analysis_rows'])} |"
        )

    uc_row = primary.loc[primary["outcome"].eq("uc_any")]
    emp_row = primary.loc[primary["outcome"].eq("employed_any_week")]
    if not uc_row.empty and not emp_row.empty and primary["min_cell_persons"].min() >= 100:
        if (
            uc_row.iloc[0]["coef_early_x_post"] < -0.05
            and emp_row.iloc[0]["coef_early_x_post"] > 0
            and abs(uc_row.iloc[0]["t_stat"]) >= 1.65
            and abs(emp_row.iloc[0]["t_stat"]) >= 1.65
        ):
            verdict = "MECHANISM-SUPPORTED-BUT-LITERATURE-CROWDED"
        elif uc_row.iloc[0]["coef_early_x_post"] < 0 and emp_row.iloc[0]["coef_early_x_post"] > 0:
            verdict = "DIRECT-TIMING-BUT-LOW-POWER"
        else:
            verdict = "SUPPORT-YES-SIGNAL-MIXED"
    else:
        verdict = "SUPPORT-THIN"

    report = f"""# Pandemic UI Early Termination Fast Test

## Verdict

`{verdict}`

This is the clearest newly screened design for **direct policy timing** from the current parquet.
It is adult-focused, non-child, and non-unwinding. The drawback is that the primary SIPP UC-recipient
sample is small and the labor-supply effect is already studied using CPS, bank, and administrative
data. A SIPP paper would need to be about the insurance/safety-net/medical-financial spillovers of
UI withdrawal, not simply employment.

## Policy Design

In 2021, 26 states ended at least the federal $300 FPUC supplement before the national September
expiration. This screen compares early-exit states with states retaining benefits through the
federal expiration.

- Sample: prime-age adults 25-54 in reference year 2021.
- Primary at-risk group: people receiving unemployment compensation in January-May 2021.
- Pre period: February-May 2021.
- Transition month excluded: June 2021.
- Post period: July-August 2021.
- Model: weighted individual-month DiD with state and month fixed effects.

## Support

{chr(10).join(sup_lines)}

## Primary At-Risk UC Results

Coefficient is `early-exit state x post period`.

{chr(10).join(lines)}

## Interpretation

- This design has a clearer policy shock than the PTC-only screen, but weaker SIPP power.
- The SIPP novelty is not measuring employment alone. The contribution would be whether UI withdrawal
  caused substitution into SNAP/Medicaid, loss of private coverage, uninsured spells, or medical
  financial pressure.
- If the safety-net/insurance outcomes are null or unstable after full checks, this should be a no-go
  because the main employment question is already crowded.

## Next Checks

1. Re-estimate with person fixed effects for the at-risk panel.
2. Separate states ending all pandemic programs from states ending only FPUC.
3. Add event-study leads/lags from February-August 2021.
4. Test placebo early-exit assignment in 2019 and 2020 SIPP reference years if comparable monthly
   UC variables support it.
5. Keep outcomes focused on SIPP's comparative advantage: insurance, SNAP/TANF/SSI, medical OOP,
   and doctor use.

## Source Checks

- U.S. Department of Labor UIPL 14-21 Change 1 confirms no PUA/FPUC/PEUC/MEUC payments after
  September 6, 2021 under federal law:
  https://www.dol.gov/node/162738
- St. Louis Fed summarizes that 26 states stopped FPUC in June-July 2021:
  https://www.stlouisfed.org/on-the-economy/2022/apr/end-emergency-pandemic-unemployment-benefits-2021
- NBER WP 29575 / related paper documents the existing labor-supply literature and the crowded
  main employment question:
  https://www.nber.org/papers/w29575
- AEA Papers and Proceedings bank-data study reports UI receipt and employment effects after early
  withdrawal, underscoring why SIPP should target spillovers:
  https://www.aeaweb.org/articles?id=10.1257/pandp.20221009

## Outputs

- `result/idea_scan/pandemic_ui_early_exit_estimates.csv`
- `result/idea_scan/pandemic_ui_early_exit_support.csv`
"""
    REPORT.write_text(report, encoding="utf-8")


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    df = read_panel()
    outcomes = [
        "uc_any",
        "employed_any_week",
        "no_job_all_month",
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
        "sick_days_any",
    ]
    rows = []
    for sample_flag in ["at_risk_uc", "at_risk_layofflooking", "at_risk_nonemployment", "at_risk_broad"]:
        for outcome in outcomes:
            rows.append(estimate(df, sample_flag, outcome))
    est = pd.DataFrame(rows)
    sup = support(df)
    est.to_csv(OUT / "pandemic_ui_early_exit_estimates.csv", index=False)
    sup.to_csv(OUT / "pandemic_ui_early_exit_support.csv", index=False)
    write_report(est, sup)
    print(f"Wrote report to {REPORT}")


if __name__ == "__main__":
    main()
