from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[2]
PANEL = ROOT / "data" / "analysis_ready" / "sipp_2018_2024_person_month_panel.parquet"
OUT = ROOT / "result" / "idea_scan"
REPORT = ROOT / "report" / "24_no_surprises_act_fast_test.md"


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

# Commonwealth Fund table, "State Balance-Billing Protections, as of April 16, 2020":
# Comprehensive Approach (18 states).
COMPREHENSIVE_PRE_NSA = {
    "06",  # California
    "08",  # Colorado
    "09",  # Connecticut
    "12",  # Florida
    "13",  # Georgia
    "17",  # Illinois
    "23",  # Maine
    "24",  # Maryland
    "26",  # Michigan
    "33",  # New Hampshire
    "34",  # New Jersey
    "35",  # New Mexico
    "36",  # New York
    "39",  # Ohio
    "41",  # Oregon
    "48",  # Texas
    "51",  # Virginia
    "53",  # Washington
}

SOURCES = [
    "CMS, State Surprise Billing Laws and the No Surprises Act: https://www.cms.gov/files/document/nsa-state-laws.pdf",
    "KFF, No Surprises Act Implementation: What to Expect in 2022: https://www.kff.org/affordable-care-act/no-surprises-act-implementation-what-to-expect-in-2022/",
    "Commonwealth Fund, State Balance-Billing Protections as of April 16, 2020: https://www.commonwealthfund.org/sites/default/files/2021-03/Hoadley_state_balance_billing_protections_table_02052021.pdf",
]


def yes(s: pd.Series) -> pd.Series:
    return s.eq(1)


def clean_weight(df: pd.DataFrame) -> pd.Series:
    w = pd.to_numeric(df.get("WPFINWGT"), errors="coerce")
    w = w.where(w.gt(0), pd.to_numeric(df.get("TSSSAMT"), errors="coerce"))
    return w.where(w.gt(0), 1.0)


def wmean(y: pd.Series, w: pd.Series) -> float:
    mask = y.notna() & w.notna() & (w > 0)
    if not mask.any():
        return np.nan
    return float(np.average(y[mask].astype(float), weights=w[mask].astype(float)))


def wls_hc1(y: np.ndarray, x: np.ndarray, w: np.ndarray) -> tuple[np.ndarray, np.ndarray, int]:
    mask = np.isfinite(y) & np.isfinite(w) & (w > 0) & np.all(np.isfinite(x), axis=1)
    y = y[mask]
    x = x[mask]
    w = w[mask]
    if len(y) <= x.shape[1] + 5:
        return np.full(x.shape[1], np.nan), np.full(x.shape[1], np.nan), int(len(y))
    sw = np.sqrt(w / np.nanmean(w))
    xw = x * sw[:, None]
    yw = y * sw
    inv = np.linalg.pinv(xw.T @ xw)
    beta = inv @ (xw.T @ yw)
    resid = yw - xw @ beta
    meat = xw.T @ ((resid**2)[:, None] * xw)
    n, k = xw.shape
    cov = (n / max(n - k, 1)) * inv @ meat @ inv
    return beta, np.sqrt(np.diag(cov)), int(n)


def build_person_year() -> pd.DataFrame:
    cols = [
        "person_id",
        "person_month_key",
        "reference_year",
        "state_fips",
        "TAGE",
        "TFINCPOV",
        "EHLTSTAT",
        "WPFINWGT",
        "TSSSAMT",
        "RHLTHMTH",
        "RPRIMTH",
        "RPUBMTH",
        "TMDPAY",
        "TVISDOC",
        "TVISDENT",
        "THOSPNIT",
    ]
    df = pd.read_parquet(PANEL, columns=cols)
    df = df[df["reference_year"].between(2020, 2023)].copy()
    df["state_fips"] = df["state_fips"].astype(str).str.zfill(2)
    df["age"] = pd.to_numeric(df["TAGE"], errors="coerce")
    df["fpl"] = pd.to_numeric(df["TFINCPOV"], errors="coerce")
    df.loc[~df["fpl"].between(0, 20), "fpl"] = np.nan
    df["weight"] = clean_weight(df)
    df["healthy"] = pd.to_numeric(df["EHLTSTAT"], errors="coerce").between(1, 2).astype(float)
    df["any_coverage"] = yes(df["RHLTHMTH"]).astype(float)
    df["private"] = yes(df["RPRIMTH"]).astype(float)
    df["public"] = yes(df["RPUBMTH"]).astype(float)
    df["uninsured"] = df["RHLTHMTH"].eq(2).astype(float)
    oop = pd.to_numeric(df["TMDPAY"], errors="coerce")
    df["oop_amount"] = oop.where(oop.between(0, 200000))
    df["oop_any"] = df["oop_amount"].gt(0).astype(float)
    df["oop_gt_1000"] = df["oop_amount"].gt(1000).astype(float)
    df["oop_gt_2000"] = df["oop_amount"].gt(2000).astype(float)
    df["doctor_any"] = pd.to_numeric(df["TVISDOC"], errors="coerce").gt(0).astype(float)
    df["dental_any"] = pd.to_numeric(df["TVISDENT"], errors="coerce").gt(0).astype(float)
    df["hospital_any"] = pd.to_numeric(df["THOSPNIT"], errors="coerce").gt(0).astype(float)

    py = (
        df.groupby(["person_id", "state_fips", "reference_year"], observed=True)
        .agg(
            months=("person_month_key", "size"),
            weight=("weight", "mean"),
            age=("age", "mean"),
            fpl=("fpl", "median"),
            healthy=("healthy", "mean"),
            any_coverage=("any_coverage", "mean"),
            private=("private", "mean"),
            public=("public", "mean"),
            uninsured=("uninsured", "mean"),
            oop_amount=("oop_amount", "mean"),
            oop_any=("oop_any", "mean"),
            oop_gt_1000=("oop_gt_1000", "mean"),
            oop_gt_2000=("oop_gt_2000", "mean"),
            doctor_any=("doctor_any", "mean"),
            dental_any=("dental_any", "mean"),
            hospital_any=("hospital_any", "mean"),
        )
        .reset_index()
    )
    py["healthy"] = py["healthy"].ge(0.5).astype(int)
    py["log_oop"] = np.log1p(py["oop_amount"].clip(lower=0))
    py["care_user"] = ((py["doctor_any"] > 0) | (py["hospital_any"] > 0)).astype(int)
    py["private_dominant"] = py["private"].ge(0.5).astype(int)
    py["public_dominant"] = py["public"].ge(0.5).astype(int)
    py["comprehensive_pre_nsa"] = py["state_fips"].isin(COMPREHENSIVE_PRE_NSA).astype(int)
    py["no_comprehensive_pre_nsa"] = 1 - py["comprehensive_pre_nsa"]
    py["post_nsa"] = py["reference_year"].ge(2022).astype(int)
    py["nsa_new_protection"] = py["no_comprehensive_pre_nsa"] * py["post_nsa"]
    py["state_name"] = py["state_fips"].map(STATE_NAMES)
    return py


def estimate_static(data: pd.DataFrame, sample_mask: pd.Series, outcomes: list[str], model: str) -> pd.DataFrame:
    sample = data.loc[sample_mask].copy()
    rows = []
    for outcome in outcomes:
        d = sample[sample[outcome].notna() & sample["weight"].gt(0)].copy()
        x = pd.concat(
            [
                pd.Series(1.0, index=d.index, name="const"),
                d["nsa_new_protection"].astype(float),
                d["age"].astype(float),
                d["fpl"].astype(float).clip(0, 8).rename("fpl_clip"),
                d["healthy"].astype(float),
                pd.get_dummies(d["state_fips"], prefix="st", drop_first=True, dtype=float),
                pd.get_dummies(d["reference_year"].astype(str), prefix="yr", drop_first=True, dtype=float),
            ],
            axis=1,
        )
        beta, se, n = wls_hc1(d[outcome].to_numpy(dtype=float), x.to_numpy(dtype=float), d["weight"].to_numpy(dtype=float))
        b = pd.Series(beta, index=x.columns)
        s = pd.Series(se, index=x.columns)
        rows.append(
            {
                "model": model,
                "outcome": outcome,
                "term": "nsa_new_protection",
                "coef": b.get("nsa_new_protection", np.nan),
                "se": s.get("nsa_new_protection", np.nan),
                "t": b.get("nsa_new_protection", np.nan) / s.get("nsa_new_protection", np.nan)
                if s.get("nsa_new_protection", np.nan)
                else np.nan,
                "n_person_years": n,
                "n_persons": int(d["person_id"].nunique()),
                "n_states": int(d["state_fips"].nunique()),
                "weighted_mean": wmean(d[outcome], d["weight"]),
            }
        )
    return pd.DataFrame(rows)


def estimate_event(data: pd.DataFrame, sample_mask: pd.Series, outcomes: list[str], model: str) -> pd.DataFrame:
    sample = data.loc[sample_mask].copy()
    event_terms = []
    for year in [2020, 2022, 2023]:
        name = f"no_comp_x_year_{year}"
        sample[name] = sample["no_comprehensive_pre_nsa"].astype(float) * sample["reference_year"].eq(year).astype(float)
        event_terms.append(name)
    # 2021 is omitted. With only 2020-2023, this is a compact pre/post event check.
    rows = []
    for outcome in outcomes:
        d = sample[sample[outcome].notna() & sample["weight"].gt(0)].copy()
        x = pd.concat(
            [
                pd.Series(1.0, index=d.index, name="const"),
                d[event_terms],
                d["age"].astype(float),
                d["fpl"].astype(float).clip(0, 8).rename("fpl_clip"),
                d["healthy"].astype(float),
                pd.get_dummies(d["state_fips"], prefix="st", drop_first=True, dtype=float),
                pd.get_dummies(d["reference_year"].astype(str), prefix="yr", drop_first=True, dtype=float),
            ],
            axis=1,
        )
        beta, se, n = wls_hc1(d[outcome].to_numpy(dtype=float), x.to_numpy(dtype=float), d["weight"].to_numpy(dtype=float))
        b = pd.Series(beta, index=x.columns)
        s = pd.Series(se, index=x.columns)
        for year, term in zip([2020, 2022, 2023], event_terms):
            rows.append(
                {
                    "model": model,
                    "outcome": outcome,
                    "year_relative_to_2021": year - 2021,
                    "term": term,
                    "coef": b.get(term, np.nan),
                    "se": s.get(term, np.nan),
                    "t": b.get(term, np.nan) / s.get(term, np.nan) if s.get(term, np.nan) else np.nan,
                    "n_person_years": n,
                    "n_persons": int(d["person_id"].nunique()),
                    "n_states": int(d["state_fips"].nunique()),
                }
            )
    return pd.DataFrame(rows)


def support(data: pd.DataFrame) -> pd.DataFrame:
    masks = {
        "private_care_users_26_64": data["age"].between(26, 64, inclusive="both")
        & data["private_dominant"].eq(1)
        & data["care_user"].eq(1)
        & data["months"].ge(6),
        "private_hospital_users_26_64": data["age"].between(26, 64, inclusive="both")
        & data["private_dominant"].eq(1)
        & data["hospital_any"].gt(0)
        & data["months"].ge(6),
        "public_care_users_placebo_26_64": data["age"].between(26, 64, inclusive="both")
        & data["public_dominant"].eq(1)
        & data["care_user"].eq(1)
        & data["months"].ge(6),
    }
    rows = []
    for name, mask in masks.items():
        d = data.loc[mask]
        rows.append(
            {
                "sample": name,
                "person_years": int(len(d)),
                "persons": int(d["person_id"].nunique()),
                "states": int(d["state_fips"].nunique()),
                "no_comprehensive_pre_person_years": int(d["no_comprehensive_pre_nsa"].sum()),
                "post_new_protection_person_years": int(d["nsa_new_protection"].sum()),
                "mean_oop_amount": wmean(d["oop_amount"], d["weight"]),
                "mean_oop_gt_1000": wmean(d["oop_gt_1000"], d["weight"]),
            }
        )
    return pd.DataFrame(rows)


def fmt(df: pd.DataFrame, model: str, outcomes: list[str]) -> str:
    d = df[df["model"].eq(model)].set_index("outcome")
    lines = []
    for outcome in outcomes:
        if outcome not in d.index:
            continue
        r = d.loc[outcome]
        lines.append(f"- `{outcome}`: {r['coef']:+.4f}, se {r['se']:.4f}, t {r['t']:.2f}.")
    return "\n".join(lines)


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    py = build_person_year()
    py.to_parquet(OUT / "no_surprises_act_person_year_panel.parquet", index=False)

    outcomes = ["log_oop", "oop_any", "oop_gt_1000", "oop_gt_2000", "oop_amount", "doctor_any", "hospital_any"]
    private_care = (
        py["age"].between(26, 64, inclusive="both")
        & py["private_dominant"].eq(1)
        & py["care_user"].eq(1)
        & py["months"].ge(6)
    )
    private_hospital = (
        py["age"].between(26, 64, inclusive="both")
        & py["private_dominant"].eq(1)
        & py["hospital_any"].gt(0)
        & py["months"].ge(6)
    )
    public_placebo = (
        py["age"].between(26, 64, inclusive="both")
        & py["public_dominant"].eq(1)
        & py["care_user"].eq(1)
        & py["months"].ge(6)
    )

    est = pd.concat(
        [
            estimate_static(py, private_care, outcomes, "private_care_users"),
            estimate_static(py, private_hospital, outcomes, "private_hospital_users"),
            estimate_static(py, public_placebo, outcomes, "public_care_users_placebo"),
        ],
        ignore_index=True,
    )
    ev = pd.concat(
        [
            estimate_event(py, private_care, ["log_oop", "oop_gt_1000", "oop_amount"], "private_care_users_event"),
            estimate_event(py, private_hospital, ["log_oop", "oop_gt_1000", "oop_amount"], "private_hospital_users_event"),
        ],
        ignore_index=True,
    )
    sup = support(py)
    est.to_csv(OUT / "no_surprises_act_estimates.csv", index=False)
    ev.to_csv(OUT / "no_surprises_act_event.csv", index=False)
    sup.to_csv(OUT / "no_surprises_act_support.csv", index=False)

    priv = sup[sup["sample"].eq("private_care_users_26_64")].iloc[0]
    hosp = sup[sup["sample"].eq("private_hospital_users_26_64")].iloc[0]
    placebo = sup[sup["sample"].eq("public_care_users_placebo_26_64")].iloc[0]
    main = est[(est["model"].eq("private_care_users")) & (est["outcome"].eq("log_oop"))].iloc[0]
    high = est[(est["model"].eq("private_care_users")) & (est["outcome"].eq("oop_gt_1000"))].iloc[0]
    verdict = "NO-CLEAN-GO"
    if main["coef"] < -0.05 and abs(main["t"]) >= 1.96 and high["coef"] < 0:
        verdict = "PROMISING-FINANCIAL-PROTECTION-SIGNAL"
    elif main["coef"] < 0 and high["coef"] < 0:
        verdict = "WEAK-DIRECTIONAL-SIGNAL"

    report = f"""# No Surprises Act Fast Test

## Question

Can SIPP support a non-child, non-unwinding adult health-insurance paper on the No Surprises Act
and financial protection from medical bills?

Design idea: after the federal No Surprises Act took effect in 2022, privately insured adults in
states without comprehensive pre-existing balance-billing protections should receive a larger new
consumer-protection shock than privately insured adults in states that already had comprehensive
protections.

## Source Checks

{chr(10).join(f"- {s}" for s in SOURCES)}

## Policy Coding

Comprehensive pre-NSA state protections use the Commonwealth Fund table's "Comprehensive
Approach (18 states)" as of April 16, 2020. The treatment is:

`no comprehensive pre-NSA state protection x reference_year >= 2022`.

The estimation window is 2020-2023 to avoid pretending that earlier state-law adoption timing is
fully coded.

## Data and Samples

- Source parquet: `data/analysis_ready/sipp_2018_2024_person_month_panel.parquet`.
- Unit: person-year collapsed from monthly SIPP rows.
- Main sample: privately insured adults age 26-64 with any doctor or hospital use.
- Stronger exposure sample: privately insured adults age 26-64 with any hospital nights.
- Placebo sample: public-covered adult care users.
- Outcomes: log medical OOP, any OOP, OOP above 1000, OOP above 2000, OOP amount, doctor use, hospital use.

Support:

- Private care users: {int(priv['person_years']):,} person-years, {int(priv['persons']):,} persons, {int(priv['states']):,} states.
- Private hospital users: {int(hosp['person_years']):,} person-years, {int(hosp['persons']):,} persons, {int(hosp['states']):,} states.
- Public-care placebo: {int(placebo['person_years']):,} person-years, {int(placebo['persons']):,} persons, {int(placebo['states']):,} states.
- Main-sample post new-protection person-years: {int(priv['post_new_protection_person_years']):,}.

## Static Estimates

Main term: `nsa_new_protection`, with state and year fixed effects.

Private care users:

{fmt(est, 'private_care_users', outcomes)}

Private hospital users:

{fmt(est, 'private_hospital_users', outcomes)}

Public-care placebo:

{fmt(est, 'public_care_users_placebo', outcomes)}

## Verdict

`{verdict}`

Interpretation:

- A credible GO would require lower OOP in newly protected states after 2022, especially among
  privately insured hospital users, with no comparable placebo pattern among public-covered users.
- This screen cannot observe out-of-network bills, emergency department use, self-funded plan
  status, or whether a given bill was actually subject to the No Surprises Act.
- Therefore a statistically clean SIPP signal must be unusually strong before this can be treated as
  a main-paper idea.

## Artifacts

- `script/11_idea_scan/11_no_surprises_act_fast_test.py`
- `result/idea_scan/no_surprises_act_person_year_panel.parquet`
- `result/idea_scan/no_surprises_act_support.csv`
- `result/idea_scan/no_surprises_act_estimates.csv`
- `result/idea_scan/no_surprises_act_event.csv`
"""
    REPORT.write_text(report, encoding="utf-8")


if __name__ == "__main__":
    main()
