from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[2]
PANEL = ROOT / "data" / "analysis_ready" / "sipp_2018_2024_person_month_panel.parquet"
OUT = ROOT / "result" / "idea_scan"
REPORT = ROOT / "report" / "18_childless_eitc_fast_test.md"


def yes(s: pd.Series) -> pd.Series:
    return s.eq(1)


def persons(s: pd.Series) -> int:
    return int(s.dropna().nunique())


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


def read_monthly() -> pd.DataFrame:
    cols = [
        "SSUID",
        "SHHADID",
        "RFAMNUM",
        "person_id",
        "reference_year",
        "reference_month",
        "state_fips",
        "TAGE",
        "ESEX",
        "EEDUC",
        "WPFINWGT",
        "TSSSAMT",
        "RMESR",
        "RMWKWJB",
        "TPEARN",
        "TPTOTINC",
        "TFTOTINC",
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
    ]
    df = pd.read_parquet(PANEL, columns=cols)
    df = df[df["reference_year"].between(2018, 2023)].copy()
    df["state_fips"] = df["state_fips"].astype(str).str.zfill(2)
    df["age"] = pd.to_numeric(df["TAGE"], errors="coerce")
    df["family_key"] = (
        df["SSUID"].astype(str)
        + "|"
        + df["SHHADID"].astype(str)
        + "|"
        + df["RFAMNUM"].astype(str)
        + "|"
        + df["reference_year"].astype(str)
        + "|"
        + df["reference_month"].astype(str)
    )
    df["is_child_under19"] = df["age"].lt(19).astype("int8")
    fam_child = df.groupby("family_key", observed=True)["is_child_under19"].transform("max")
    df["family_has_child_under19"] = fam_child.eq(1)
    df["childless_family_month"] = ~df["family_has_child_under19"]
    df["employed_any_week"] = pd.to_numeric(df["RMWKWJB"], errors="coerce").gt(0) | pd.to_numeric(df["RMESR"], errors="coerce").between(1, 5)
    df["earnings"] = pd.to_numeric(df["TPEARN"], errors="coerce").where(lambda x: x.between(-100000, 100000))
    df["snap"] = yes(df["RSNAP_MNYN"])
    df["tanf"] = yes(df["RTANF_MNYN"])
    df["ssi"] = yes(df["RSSI_MNYN"])
    df["medicaid"] = yes(df["EMDMTH"])
    df["uninsured"] = df["RHLTHMTH"].eq(2)
    df["private"] = yes(df["RPRIMTH"])
    df["direct_purchase"] = yes(df["RPRITYPE2"])
    df["oop_any"] = pd.to_numeric(df["TMDPAY"], errors="coerce").gt(0)
    df["doctor_any"] = pd.to_numeric(df["TVISDOC"], errors="coerce").gt(0)
    df["weight"] = pd.to_numeric(df["WPFINWGT"], errors="coerce")
    df["weight"] = df["weight"].where(df["weight"].gt(0))
    return df


def person_year(df: pd.DataFrame) -> pd.DataFrame:
    adults = df[df["age"].between(18, 29, inclusive="both")].copy()
    grouped = adults.groupby(["person_id", "reference_year"], observed=True)
    py = grouped.agg(
        age=("age", "max"),
        state_fips=("state_fips", lambda x: x.mode().iloc[0] if not x.mode().empty else x.iloc[0]),
        sex=("ESEX", "first"),
        educ=("EEDUC", "max"),
        months_observed=("reference_month", "nunique"),
        childless_months=("childless_family_month", "sum"),
        annual_earnings=("earnings", "sum"),
        annual_personal_income=("TPTOTINC", "sum"),
        annual_family_income=("TFTOTINC", "sum"),
        annual_fpl=("TFCYINCPOV", "median"),
        employed_months=("employed_any_week", "sum"),
        snap_any=("snap", "max"),
        tanf_any=("tanf", "max"),
        ssi_any=("ssi", "max"),
        medicaid_any=("medicaid", "max"),
        uninsured_any=("uninsured", "max"),
        uninsured_months=("uninsured", "sum"),
        private_any=("private", "max"),
        direct_purchase_any=("direct_purchase", "max"),
        oop_any=("oop_any", "max"),
        doctor_any=("doctor_any", "max"),
        weight=("weight", "mean"),
    ).reset_index()
    py["childless_share"] = py["childless_months"] / py["months_observed"].clip(lower=1)
    py["childless"] = py["childless_share"].ge(0.75)
    py["worker_low_income"] = py["annual_earnings"].between(1, 30000, inclusive="both")
    py["year2021"] = py["reference_year"].eq(2021).astype(int)
    py["age24"] = py["age"].eq(24).astype(int)
    py["age25"] = py["age"].eq(25).astype(int)
    py["age19_24"] = py["age"].between(19, 24, inclusive="both").astype(int)
    py["age25_29"] = py["age"].between(25, 29, inclusive="both").astype(int)
    py["treated_age24_2021"] = py["age24"] * py["year2021"]
    py["treated_age19_24_2021"] = py["age19_24"] * py["year2021"]
    py["employed_any_year"] = py["employed_months"].gt(0)
    py["employed_all_year"] = py["employed_months"].ge(10)
    py["log_earnings_plus1"] = np.log1p(py["annual_earnings"].clip(lower=0))
    return py


def estimate_age24(py: pd.DataFrame, outcome: str) -> dict:
    sample = py[
        py["childless"]
        & py["worker_low_income"]
        & py["age"].isin([24, 25])
        & py["reference_year"].between(2018, 2023)
    ].copy()
    year_fe = pd.get_dummies(sample["reference_year"].astype(str), prefix="yr", drop_first=True, dtype=float)
    state_fe = pd.get_dummies(sample["state_fips"], prefix="st", drop_first=True, dtype=float)
    x = pd.concat(
        [
            pd.Series(1.0, index=sample.index, name="const"),
            sample[["treated_age24_2021", "age24"]],
            year_fe,
            state_fe,
        ],
        axis=1,
    )
    beta, se = wls_hc1(sample[outcome].astype(float).to_numpy(), x.to_numpy(float), sample["weight"].to_numpy(float))
    idx = list(x.columns).index("treated_age24_2021")
    treated = sample[sample["treated_age24_2021"].eq(1)]
    return {
        "design": "age24_vs_age25",
        "outcome": outcome,
        "coef_treated_2021": float(beta[idx]),
        "se_hc1": float(se[idx]),
        "t_stat": float(beta[idx] / se[idx]) if se[idx] > 0 else np.nan,
        "rows": int(len(sample)),
        "persons": persons(sample["person_id"]),
        "treated_2021_persons": persons(treated["person_id"]),
        "age24_persons": persons(sample.loc[sample["age24"].eq(1), "person_id"]),
        "age25_persons": persons(sample.loc[sample["age25"].eq(1), "person_id"]),
    }


def estimate_young(py: pd.DataFrame, outcome: str) -> dict:
    sample = py[
        py["childless"]
        & py["worker_low_income"]
        & py["age"].between(19, 29, inclusive="both")
        & py["reference_year"].between(2018, 2023)
    ].copy()
    year_fe = pd.get_dummies(sample["reference_year"].astype(str), prefix="yr", drop_first=True, dtype=float)
    age_fe = pd.get_dummies(sample["age"].astype(int).astype(str), prefix="age", drop_first=True, dtype=float)
    state_fe = pd.get_dummies(sample["state_fips"], prefix="st", drop_first=True, dtype=float)
    x = pd.concat(
        [
            pd.Series(1.0, index=sample.index, name="const"),
            sample[["treated_age19_24_2021", "age19_24"]],
            year_fe,
            age_fe,
            state_fe,
        ],
        axis=1,
    )
    beta, se = wls_hc1(sample[outcome].astype(float).to_numpy(), x.to_numpy(float), sample["weight"].to_numpy(float))
    idx = list(x.columns).index("treated_age19_24_2021")
    treated = sample[sample["treated_age19_24_2021"].eq(1)]
    return {
        "design": "age19_24_vs_age25_29",
        "outcome": outcome,
        "coef_treated_2021": float(beta[idx]),
        "se_hc1": float(se[idx]),
        "t_stat": float(beta[idx] / se[idx]) if se[idx] > 0 else np.nan,
        "rows": int(len(sample)),
        "persons": persons(sample["person_id"]),
        "treated_2021_persons": persons(treated["person_id"]),
        "age24_persons": persons(sample.loc[sample["age24"].eq(1), "person_id"]),
        "age25_persons": persons(sample.loc[sample["age25"].eq(1), "person_id"]),
    }


def support(py: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for label, mask in {
        "age24_vs_age25": py["childless"] & py["worker_low_income"] & py["age"].isin([24, 25]),
        "age19_24_vs_age25_29": py["childless"] & py["worker_low_income"] & py["age"].between(19, 29, inclusive="both"),
    }.items():
        s = py[mask]
        rows.append(
            {
                "design": label,
                "rows": int(len(s)),
                "persons": persons(s["person_id"]),
                "persons_2021": persons(s.loc[s["reference_year"].eq(2021), "person_id"]),
                "treated_2021_persons": persons(
                    s.loc[
                        s["reference_year"].eq(2021)
                        & ((s["age"].eq(24)) if label == "age24_vs_age25" else s["age"].between(19, 24)),
                        "person_id",
                    ]
                ),
                "median_annual_earnings": float(s["annual_earnings"].median()),
                "snap_any_events": int(s["snap_any"].sum()),
                "medicaid_any_events": int(s["medicaid_any"].sum()),
                "uninsured_any_events": int(s["uninsured_any"].sum()),
            }
        )
    return pd.DataFrame(rows)


def write_report(est: pd.DataFrame, sup: pd.DataFrame) -> None:
    main = est[est["design"].eq("age24_vs_age25")].copy()
    keep = ["employed_any_year", "employed_all_year", "log_earnings_plus1", "snap_any", "medicaid_any", "uninsured_any", "private_any", "oop_any"]
    main = main[main["outcome"].isin(keep)].sort_values("outcome")
    cols = ["outcome", "coef_treated_2021", "se_hc1", "t_stat", "persons", "treated_2021_persons"]
    lines = ["| " + " | ".join(cols) + " |", "|" + "|".join(["---"] * len(cols)) + "|"]
    for _, r in main.iterrows():
        vals = []
        for c in cols:
            v = r[c]
            vals.append(f"{v:.4f}" if isinstance(v, float) else str(v))
        lines.append("| " + " | ".join(vals) + " |")
    sup_lines = ["| design | persons | persons 2021 | treated 2021 persons | median earnings | SNAP events | Medicaid events | uninsured events |", "|---|---:|---:|---:|---:|---:|---:|---:|"]
    for _, r in sup.iterrows():
        sup_lines.append(
            f"| {r['design']} | {int(r['persons'])} | {int(r['persons_2021'])} | {int(r['treated_2021_persons'])} | {r['median_annual_earnings']:.0f} | {int(r['snap_any_events'])} | {int(r['medicaid_any_events'])} | {int(r['uninsured_any_events'])} |"
        )
    emp = main.loc[main["outcome"].eq("employed_any_year")]
    earn = main.loc[main["outcome"].eq("log_earnings_plus1")]
    if sup.loc[sup["design"].eq("age24_vs_age25"), "treated_2021_persons"].iloc[0] < 200:
        verdict = "SUPPORT-THIN"
    elif (not emp.empty and abs(emp.iloc[0]["t_stat"]) >= 1.5) or (not earn.empty and abs(earn.iloc[0]["t_stat"]) >= 1.5):
        verdict = "PROMISING-BUT-MEASUREMENT-LIMITED"
    else:
        verdict = "SUPPORT-YES-SIGNAL-WEAK"
    report = f"""# Childless EITC ARPA 2021 Fast Test

## Verdict

`{verdict}`

This is a genuinely adult, non-child, non-unwinding policy idea. The 2021 American Rescue Plan
temporarily expanded the childless EITC, including younger workers who were previously excluded.
The identification hook is age eligibility, especially the old age-25 threshold.

## Why It Is Interesting

- It is a tax-and-transfer policy with current relevance: the 2021 expansion expired, and proposals
  to expand the childless EITC remain active.
- It targets adults without qualifying children, matching the requested non-child direction.
- SIPP can observe employment, earnings, insurance, Medicaid/SNAP, and medical financial outcomes.

## Main Limitation

The uploaded parquet does **not** include actual EITC receipt, tax refunds, filing status, school
enrollment, or qualifying-child tax-unit construction. Childless status is approximated as living
in a family-month with no child under 19. The test below is therefore a reduced-form feasibility
screen, not a final tax-unit design.

## Support

{chr(10).join(sup_lines)}

## Primary Age-24 vs Age-25 Screen

Sample: childless low-income workers ages 24-25, 2018-2023. Treatment is age 24 in tax year 2021.
Age 24 is newly eligible in 2021 relative to the old childless EITC age-25 cutoff; age 25 is already
eligible but also affected by the larger 2021 credit, so this is conservative and imperfect.

{chr(10).join(lines)}

## Interpretation

- This is more innovative than age-26 or age-65 insurance thresholds.
- The policy shock is real and the sample is not tiny.
- It is not yet a clean top-field design because the current parquet lacks actual tax-unit and
  student-status variables.
- A stronger version needs richer SIPP variables or an IRS/SIPP-linked tax measure. Without that,
  this remains a promising concept rather than an immediate paper.

## Source Checks

- IRS EITC eligibility page:
  https://www.irs.gov/credits-deductions/individuals/earned-income-tax-credit/who-qualifies-for-the-earned-income-tax-credit-eitc
- Tax Policy Center summary of the ARPA childless EITC expansion:
  https://taxpolicycenter.org/publications/how-american-rescue-plans-temporary-eitc-expansion-impacted-workers-without-children
- CRS summary of ARPA 2021, including childless EITC age changes:
  https://www.everycrsreport.com/reports/R46680.html
- NBER working paper on expanded EITC for childless young adults:
  https://www.nber.org/system/files/working_papers/w32571/w32571.pdf

## Outputs

- `result/idea_scan/childless_eitc_person_year_panel.csv`
- `result/idea_scan/childless_eitc_fast_estimates.csv`
- `result/idea_scan/childless_eitc_support.csv`
"""
    REPORT.write_text(report, encoding="utf-8")


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    monthly = read_monthly()
    py = person_year(monthly)
    outcomes = [
        "employed_any_year",
        "employed_all_year",
        "log_earnings_plus1",
        "snap_any",
        "tanf_any",
        "ssi_any",
        "medicaid_any",
        "uninsured_any",
        "private_any",
        "direct_purchase_any",
        "oop_any",
        "doctor_any",
    ]
    rows = []
    for outcome in outcomes:
        rows.append(estimate_age24(py, outcome))
        rows.append(estimate_young(py, outcome))
    est = pd.DataFrame(rows)
    sup = support(py)
    py.to_csv(OUT / "childless_eitc_person_year_panel.csv", index=False)
    est.to_csv(OUT / "childless_eitc_fast_estimates.csv", index=False)
    sup.to_csv(OUT / "childless_eitc_support.csv", index=False)
    write_report(est, sup)
    print(f"Wrote report to {REPORT}")


if __name__ == "__main__":
    main()
