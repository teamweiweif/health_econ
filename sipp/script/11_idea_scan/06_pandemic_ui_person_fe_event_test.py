from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[2]
PANEL = ROOT / "data" / "analysis_ready" / "sipp_2018_2024_person_month_panel.parquet"
OUT = ROOT / "result" / "idea_scan"
REPORT = ROOT / "report" / "17_pandemic_ui_person_fe_event_test.md"


STATE = {
    "AL": "01", "AK": "02", "AZ": "04", "AR": "05", "CA": "06", "CO": "08",
    "CT": "09", "DE": "10", "DC": "11", "FL": "12", "GA": "13", "HI": "15",
    "ID": "16", "IL": "17", "IN": "18", "IA": "19", "KS": "20", "KY": "21",
    "LA": "22", "ME": "23", "MD": "24", "MA": "25", "MI": "26", "MN": "27",
    "MS": "28", "MO": "29", "MT": "30", "NE": "31", "NV": "32", "NH": "33",
    "NJ": "34", "NM": "35", "NY": "36", "NC": "37", "ND": "38", "OH": "39",
    "OK": "40", "OR": "41", "PA": "42", "RI": "44", "SC": "45", "SD": "46",
    "TN": "47", "TX": "48", "UT": "49", "VT": "50", "VA": "51", "WA": "53",
    "WV": "54", "WI": "55", "WY": "56",
}

EARLY_EXIT_STATES = {
    "AL", "AK", "AZ", "AR", "FL", "GA", "ID", "IN", "IA", "LA", "MD",
    "MS", "MO", "MT", "NE", "NH", "ND", "OH", "OK", "SC", "SD", "TN",
    "TX", "UT", "WV", "WY",
}


def yes(s: pd.Series) -> pd.Series:
    return s.eq(1)


def persons(s: pd.Series) -> int:
    return int(s.dropna().nunique())


def read_panel() -> pd.DataFrame:
    cols = [
        "person_id", "reference_year", "reference_month", "state_fips", "TAGE",
        "EUC1MNYN", "EUC2MNYN", "EUC3MNYN", "RMESR", "RMWKWJB", "TPEARN",
        "RSNAP_MNYN", "RTANF_MNYN", "RSSI_MNYN", "RHLTHMTH", "EMDMTH",
        "RPRIMTH", "RPRITYPE2", "TMDPAY", "TVISDOC", "TDAYSICK",
    ]
    df = pd.read_parquet(PANEL, columns=cols)
    df = df[df["reference_year"].eq(2021)].copy()
    df["state_fips"] = df["state_fips"].astype(str).str.zfill(2)
    df["age"] = pd.to_numeric(df["TAGE"], errors="coerce")
    df["prime_age"] = df["age"].between(25, 54, inclusive="both")
    df["early_exit"] = df["state_fips"].isin({STATE[s] for s in EARLY_EXIT_STATES}).astype(int)
    df["uc_any"] = yes(df["EUC1MNYN"]) | yes(df["EUC2MNYN"]) | yes(df["EUC3MNYN"])
    df["employed_any_week"] = pd.to_numeric(df["RMWKWJB"], errors="coerce").gt(0) | pd.to_numeric(df["RMESR"], errors="coerce").between(1, 5)
    df["no_job_all_month"] = pd.to_numeric(df["RMWKWJB"], errors="coerce").eq(0)
    df["earnings_positive"] = pd.to_numeric(df["TPEARN"], errors="coerce").gt(0)
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

    pre = df[df["prime_age"] & df["reference_month"].between(1, 5)]
    risk = pre.groupby("person_id").agg(
        at_risk_uc=("uc_any", "max"),
        at_risk_nonemployment=("no_job_all_month", "max"),
    )
    risk["at_risk_broad"] = risk[["at_risk_uc", "at_risk_nonemployment"]].any(axis=1)
    df = df.merge(risk.reset_index(), on="person_id", how="left")
    for c in ["at_risk_uc", "at_risk_nonemployment", "at_risk_broad"]:
        df[c] = df[c].fillna(False).astype(bool)
    return df


def residualize_two_way(frame: pd.DataFrame, columns: list[str]) -> pd.DataFrame:
    """Unweighted two-way FE residualization by person and month."""
    r = frame[columns].astype(float).copy()
    for _ in range(50):
        old = r.to_numpy(copy=True)
        r = r - r.groupby(frame["person_id"]).transform("mean")
        r = r - r.groupby(frame["reference_month"]).transform("mean")
        if np.nanmax(np.abs(r.to_numpy() - old)) < 1e-10:
            break
    return r


def ols_hc1(y: np.ndarray, x: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    mask = np.isfinite(y) & np.all(np.isfinite(x), axis=1)
    y = y[mask]
    x = x[mask]
    if len(y) <= x.shape[1] + 5:
        return np.full(x.shape[1], np.nan), np.full(x.shape[1], np.nan)
    inv = np.linalg.pinv(x.T @ x)
    beta = inv @ (x.T @ y)
    resid = y - x @ beta
    meat = x.T @ ((resid**2)[:, None] * x)
    n, k = x.shape
    cov = (n / max(n - k, 1)) * inv @ meat @ inv
    return beta, np.sqrt(np.diag(cov))


def event_study(df: pd.DataFrame, sample_flag: str, outcome: str) -> pd.DataFrame:
    sample = df[
        df["prime_age"]
        & df[sample_flag]
        & df["reference_month"].between(2, 8)
    ].copy()
    # May is the reference month; June is kept to diagnose transition-month behavior.
    months = [2, 3, 4, 6, 7, 8]
    xcols = []
    for m in months:
        c = f"early_x_m{m:02d}"
        sample[c] = sample["early_exit"] * sample["reference_month"].eq(m).astype(int)
        xcols.append(c)
    work_cols = [outcome] + xcols
    resid = residualize_two_way(sample[["person_id", "reference_month"] + work_cols], work_cols)
    beta, se = ols_hc1(resid[outcome].to_numpy(), resid[xcols].to_numpy())
    rows = []
    for i, m in enumerate(months):
        rows.append(
            {
                "sample": sample_flag,
                "outcome": outcome,
                "month": m,
                "reference_month": 5,
                "coef_vs_may": float(beta[i]),
                "se_hc1": float(se[i]),
                "t_stat": float(beta[i] / se[i]) if se[i] > 0 else np.nan,
                "rows": int(len(sample)),
                "persons": persons(sample["person_id"]),
                "early_persons": persons(sample.loc[sample["early_exit"].eq(1), "person_id"]),
                "control_persons": persons(sample.loc[sample["early_exit"].eq(0), "person_id"]),
            }
        )
    return pd.DataFrame(rows)


def did_from_event(est: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for (sample, outcome), g in est.groupby(["sample", "outcome"], observed=True):
        pre = g[g["month"].isin([2, 3, 4])]
        post = g[g["month"].isin([7, 8])]
        transition = g[g["month"].eq(6)]
        rows.append(
            {
                "sample": sample,
                "outcome": outcome,
                "pre_lead_mean_coef": float(pre["coef_vs_may"].mean()),
                "transition_june_coef": float(transition["coef_vs_may"].iloc[0]) if not transition.empty else np.nan,
                "post_mean_coef": float(post["coef_vs_may"].mean()),
                "max_abs_pre_lead_t": float(pre["t_stat"].abs().max()),
                "persons": int(g["persons"].iloc[0]),
                "early_persons": int(g["early_persons"].iloc[0]),
                "control_persons": int(g["control_persons"].iloc[0]),
            }
        )
    return pd.DataFrame(rows)


def write_report(est: pd.DataFrame, summary: pd.DataFrame) -> None:
    main_outcomes = ["uc_any", "employed_any_week", "earnings_positive", "snap", "medicaid", "uninsured", "oop_any"]
    main = summary[(summary["sample"].eq("at_risk_uc")) & (summary["outcome"].isin(main_outcomes))].sort_values("outcome")
    cols = ["outcome", "pre_lead_mean_coef", "transition_june_coef", "post_mean_coef", "max_abs_pre_lead_t", "persons", "early_persons"]
    lines = ["| " + " | ".join(cols) + " |", "|" + "|".join(["---"] * len(cols)) + "|"]
    for _, r in main.iterrows():
        vals = []
        for c in cols:
            v = r[c]
            vals.append(f"{v:.4f}" if isinstance(v, float) else str(v))
        lines.append("| " + " | ".join(vals) + " |")

    uc = main.loc[main["outcome"].eq("uc_any")]
    emp = main.loc[main["outcome"].eq("employed_any_week")]
    if uc.empty or emp.empty:
        verdict = "INCOMPLETE"
    elif abs(uc.iloc[0]["max_abs_pre_lead_t"]) > 2.0 or abs(emp.iloc[0]["max_abs_pre_lead_t"]) > 2.0:
        verdict = "PRETREND-CONCERNS"
    elif uc.iloc[0]["post_mean_coef"] < -0.03 and emp.iloc[0]["post_mean_coef"] > 0.02:
        verdict = "LOW-POWER-BUT-MECHANISM-COHERENT"
    else:
        verdict = "LOW-POWER-MIXED"

    report = f"""# Pandemic UI Person-FE Event Study Fast Check

## Verdict

`{verdict}`

This strengthens the UI early-termination screen by adding individual fixed effects and month
fixed effects. May 2021 is the reference month. February-April are pre leads, June is transition,
and July-August are post months.

## Primary UC At-Risk Summary

{chr(10).join(lines)}

## Interpretation

- This is a better design check than the earlier pooled DiD because it compares each person to
  themselves within 2021.
- The primary at-risk sample remains small: roughly 624 UC-recipient prime-age adults, with about
  183 in early-exit states.
- If pre leads are quiet and post signs remain coherent, this is a valid backup idea, but still
  not a top-field main paper unless the insurance/safety-net spillovers are much stronger than the
  employment literature's already-known result.

## Outputs

- `result/idea_scan/pandemic_ui_person_fe_event_estimates.csv`
- `result/idea_scan/pandemic_ui_person_fe_event_summary.csv`
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
    parts = []
    for sample_flag in ["at_risk_uc", "at_risk_nonemployment", "at_risk_broad"]:
        for outcome in outcomes:
            parts.append(event_study(df, sample_flag, outcome))
    est = pd.concat(parts, ignore_index=True)
    summary = did_from_event(est)
    est.to_csv(OUT / "pandemic_ui_person_fe_event_estimates.csv", index=False)
    summary.to_csv(OUT / "pandemic_ui_person_fe_event_summary.csv", index=False)
    write_report(est, summary)
    print(f"Wrote report to {REPORT}")


if __name__ == "__main__":
    main()
