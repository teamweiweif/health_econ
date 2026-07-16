from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[2]
PANEL = ROOT / "data" / "analysis_ready" / "sipp_2018_2024_person_month_panel.parquet"
OUT = ROOT / "result" / "idea_scan"
REPORT = ROOT / "report" / "30_adult_medicaid_dental_fast_test.md"


SOURCES = [
    "Medicaid.gov Dental Care page: https://www.medicaid.gov/medicaid/benefits/dental-care",
    "Virginia DMAS adult dental benefit press release, July 1 2021: https://www.dmas.virginia.gov/media/3612/07-01-21-press-release-more-than-750000-medicaid-members-receive-adult-dental-benefit.pdf",
    "MaineCare covered benefits: https://www.maine.gov/dhhs/oms/mainecare-options/covered-services-benefits",
    "TennCare dental services: https://www.tn.gov/tenncare/members-applicants/dental-services.html",
    "New Hampshire Medicaid adult dental coverage: https://www.dhhs.nh.gov/nhsmiles",
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

# First full-year treatment coding. Partial-year start years are left as transition years.
DENTAL_ACTIVE_YEAR = {
    "51": 2022,  # Virginia comprehensive adult dental began July 1, 2021.
    "23": 2023,  # MaineCare comprehensive adult dental began July 1, 2022.
    "47": 2023,  # TennCare adult dental began January 1, 2023.
    "33": 2023,  # New Hampshire adult dental began April 1, 2023.
}


def yes(s: pd.Series) -> pd.Series:
    return s.eq(1)


def clean_weight(df: pd.DataFrame) -> pd.Series:
    w = pd.to_numeric(df.get("WPFINWGT"), errors="coerce")
    return w.where(w.gt(0))


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
        "EMDMTH",
        "RPUBTYPE2",
        "TMDPAY",
        "TVISDOC",
        "TVISDENT",
        "THOSPNIT",
        "TDAYSICK",
    ]
    df = pd.read_parquet(PANEL, columns=cols)
    df = df[df["reference_year"].between(2018, 2023)].copy()
    df["state_fips"] = df["state_fips"].astype(str).str.zfill(2)
    df["age"] = pd.to_numeric(df["TAGE"], errors="coerce")
    df["fpl"] = pd.to_numeric(df["TFINCPOV"], errors="coerce")
    df.loc[~df["fpl"].between(0, 20), "fpl"] = np.nan
    df["weight"] = clean_weight(df)
    df["healthy"] = pd.to_numeric(df["EHLTSTAT"], errors="coerce").between(1, 2).astype(float)
    df["any_coverage"] = yes(df["RHLTHMTH"]).astype(float)
    df["uninsured"] = df["RHLTHMTH"].eq(2).astype(float)
    df["private"] = yes(df["RPRIMTH"]).astype(float)
    df["public"] = yes(df["RPUBMTH"]).astype(float)
    df["medicaid"] = (yes(df["EMDMTH"]) | yes(df["RPUBTYPE2"])).astype(float)
    df["dental_visits"] = pd.to_numeric(df["TVISDENT"], errors="coerce").where(lambda x: x.between(0, 100))
    df["dental_any"] = df["dental_visits"].gt(0).astype(float)
    df["doctor_visits"] = pd.to_numeric(df["TVISDOC"], errors="coerce").where(lambda x: x.between(0, 200))
    df["doctor_any"] = df["doctor_visits"].gt(0).astype(float)
    df["hospital_nights"] = pd.to_numeric(df["THOSPNIT"], errors="coerce").where(lambda x: x.between(0, 365))
    df["hospital_any"] = df["hospital_nights"].gt(0).astype(float)
    df["oop_any"] = pd.to_numeric(df["TMDPAY"], errors="coerce").gt(0).astype(float)
    df["sick_days"] = pd.to_numeric(df["TDAYSICK"], errors="coerce").where(lambda x: x.between(0, 365))

    py = (
        df.groupby(["person_id", "state_fips", "reference_year"], observed=True)
        .agg(
            months=("person_month_key", "size"),
            weight=("weight", "mean"),
            age=("age", "mean"),
            fpl=("fpl", "median"),
            healthy=("healthy", "mean"),
            any_coverage=("any_coverage", "mean"),
            uninsured=("uninsured", "mean"),
            private=("private", "mean"),
            public=("public", "mean"),
            medicaid=("medicaid", "mean"),
            dental_visits=("dental_visits", "mean"),
            dental_any=("dental_any", "mean"),
            doctor_visits=("doctor_visits", "mean"),
            doctor_any=("doctor_any", "mean"),
            hospital_any=("hospital_any", "mean"),
            oop_any=("oop_any", "mean"),
            sick_days=("sick_days", "mean"),
        )
        .reset_index()
    )
    py["healthy"] = py["healthy"].ge(0.5).astype(int)
    py["dental_expansion_state"] = py["state_fips"].isin(DENTAL_ACTIVE_YEAR).astype(int)
    py["dental_active_year"] = py["state_fips"].map(DENTAL_ACTIVE_YEAR)
    py["dental_policy_active"] = (
        py["dental_active_year"].notna() & py["reference_year"].ge(py["dental_active_year"])
    ).astype(int)
    py["state_name"] = py["state_fips"].map(STATE_NAMES)
    return py


def add_fe(parts: list[pd.Series | pd.DataFrame], d: pd.DataFrame, fe_cols: list[str]) -> pd.DataFrame:
    for col in fe_cols:
        parts.append(pd.get_dummies(d[col].astype(str), prefix=col, drop_first=True, dtype=float))
    return pd.concat(parts, axis=1)


def estimate(
    d: pd.DataFrame,
    term: str,
    outcomes: list[str],
    model: str,
    controls: list[str],
    fe_cols: list[str],
) -> pd.DataFrame:
    rows = []
    for outcome in outcomes:
        s = d[d[outcome].notna() & d["weight"].gt(0)].copy()
        parts: list[pd.Series | pd.DataFrame] = [pd.Series(1.0, index=s.index, name="const"), s[term].astype(float)]
        for c in controls:
            parts.append(s[c].astype(float).rename(c))
        x = add_fe(parts, s, fe_cols)
        beta, se, n = wls_hc1(s[outcome].to_numpy(dtype=float), x.to_numpy(dtype=float), s["weight"].to_numpy(dtype=float))
        b = pd.Series(beta, index=x.columns)
        serr = pd.Series(se, index=x.columns)
        rows.append(
            {
                "model": model,
                "outcome": outcome,
                "term": term,
                "coef": b.get(term, np.nan),
                "se": serr.get(term, np.nan),
                "t": b.get(term, np.nan) / serr.get(term, np.nan) if serr.get(term, np.nan) else np.nan,
                "n_person_years": n,
                "n_persons": int(s["person_id"].nunique()),
                "n_states": int(s["state_fips"].nunique()),
                "weighted_mean": wmean(s[outcome], s["weight"]),
            }
        )
    return pd.DataFrame(rows)


def estimate_event(
    d: pd.DataFrame,
    exposure_col: str,
    years: list[int],
    omitted: int,
    outcomes: list[str],
    model: str,
    controls: list[str],
    fe_cols: list[str],
) -> pd.DataFrame:
    d = d.copy()
    terms = []
    for year in years:
        if year == omitted:
            continue
        term = f"{exposure_col}_x_{year}"
        d[term] = d[exposure_col].astype(float) * d["reference_year"].eq(year).astype(float)
        terms.append(term)
    rows = []
    for outcome in outcomes:
        s = d[d[outcome].notna() & d["weight"].gt(0)].copy()
        parts: list[pd.Series | pd.DataFrame] = [pd.Series(1.0, index=s.index, name="const"), s[terms]]
        for c in controls:
            parts.append(s[c].astype(float).rename(c))
        x = add_fe(parts, s, fe_cols)
        beta, se, n = wls_hc1(s[outcome].to_numpy(dtype=float), x.to_numpy(dtype=float), s["weight"].to_numpy(dtype=float))
        b = pd.Series(beta, index=x.columns)
        serr = pd.Series(se, index=x.columns)
        for year in years:
            if year == omitted:
                continue
            term = f"{exposure_col}_x_{year}"
            rows.append(
                {
                    "model": model,
                    "outcome": outcome,
                    "year": year,
                    "relative_to_omitted": year - omitted,
                    "term": term,
                    "coef": b.get(term, np.nan),
                    "se": serr.get(term, np.nan),
                    "t": b.get(term, np.nan) / serr.get(term, np.nan) if serr.get(term, np.nan) else np.nan,
                    "n_person_years": n,
                    "n_persons": int(s["person_id"].nunique()),
                    "n_states": int(s["state_fips"].nunique()),
                }
            )
    return pd.DataFrame(rows)


def estimate_leave_one(d: pd.DataFrame, outcomes: list[str]) -> pd.DataFrame:
    rows = []
    for state in DENTAL_ACTIVE_YEAR:
        dd = d[d["state_fips"].ne(state)].copy()
        if dd["dental_treat"].sum() == 0:
            continue
        est = estimate(
            dd,
            "dental_treat",
            outcomes,
            "adult_dental_pooled_leave_one",
            controls=["age", "fpl", "healthy"],
            fe_cols=["state_year", "state_target", "target_year"],
        )
        est.insert(1, "excluded_state", state)
        est.insert(2, "excluded_state_name", STATE_NAMES[state])
        rows.append(est)
    return pd.concat(rows, ignore_index=True) if rows else pd.DataFrame()


def build_sample(py: pd.DataFrame, target: str) -> pd.DataFrame:
    d = py[
        py["age"].between(21, 64, inclusive="both")
        & py["fpl"].between(0, 2.5, inclusive="both")
        & py["months"].ge(6)
    ].copy()
    if target == "medicaid":
        d["target_adult"] = d["medicaid"].ge(0.5).astype(int)
    elif target == "public":
        d["target_adult"] = d["public"].ge(0.5).astype(int)
    else:
        raise ValueError(target)
    d["dental_treat"] = d["dental_policy_active"] * d["target_adult"]
    d["state_year"] = d["state_fips"] + "_" + d["reference_year"].astype(str)
    d["state_target"] = d["state_fips"] + "_" + d["target_adult"].astype(str)
    d["target_year"] = d["target_adult"].astype(str) + "_" + d["reference_year"].astype(str)
    d["expansion_target"] = d["dental_expansion_state"] * d["target_adult"]
    return d


def support(sample_medicaid: pd.DataFrame, sample_public: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for name, d in [("medicaid_target", sample_medicaid), ("public_target", sample_public)]:
        treated_target = d[d["dental_expansion_state"].eq(1) & d["target_adult"].eq(1)]
        rows.append(
            {
                "sample": name,
                "person_years": int(len(d)),
                "persons": int(d["person_id"].nunique()),
                "states": int(d["state_fips"].nunique()),
                "target_person_years": int(d["target_adult"].sum()),
                "expansion_state_target_person_years": int(len(treated_target)),
                "active_treated_person_years": int(d["dental_treat"].sum()),
                "active_treated_persons": int(d.loc[d["dental_treat"].eq(1), "person_id"].nunique()),
                "weighted_mean_dental_visits": wmean(d["dental_visits"], d["weight"]),
                "weighted_mean_dental_any": wmean(d["dental_any"], d["weight"]),
                "weighted_mean_doctor_any": wmean(d["doctor_any"], d["weight"]),
            }
        )
    by_state = (
        sample_medicaid[
            sample_medicaid["dental_expansion_state"].eq(1)
            & sample_medicaid["target_adult"].eq(1)
        ]
        .groupby(["state_fips", "state_name", "reference_year"], observed=True)
        .agg(person_years=("person_id", "size"), persons=("person_id", "nunique"), dental_mean=("dental_visits", "mean"))
        .reset_index()
    )
    rows.append(
        {
            "sample": "expansion_state_medicaid_target_by_state_year_table_in_separate_csv",
            "person_years": int(by_state["person_years"].sum()),
            "persons": int(by_state["persons"].sum()),
            "states": int(by_state["state_fips"].nunique()),
            "target_person_years": np.nan,
            "expansion_state_target_person_years": np.nan,
            "active_treated_person_years": np.nan,
            "active_treated_persons": np.nan,
            "weighted_mean_dental_visits": np.nan,
            "weighted_mean_dental_any": np.nan,
            "weighted_mean_doctor_any": np.nan,
        }
    )
    by_state.to_csv(OUT / "adult_medicaid_dental_expansion_state_support.csv", index=False)
    return pd.DataFrame(rows)


def fmt(est: pd.DataFrame, model: str, outcomes: list[str]) -> str:
    d = est[est["model"].eq(model)].set_index("outcome")
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
    sample_medicaid = build_sample(py, "medicaid")
    sample_public = build_sample(py, "public")
    outcomes = ["dental_visits", "dental_any", "doctor_any", "hospital_any", "oop_any", "sick_days"]

    estimates = pd.concat(
        [
            estimate(
                sample_medicaid,
                "dental_treat",
                outcomes,
                "adult_dental_pooled_medicaid_target",
                controls=["age", "fpl", "healthy"],
                fe_cols=["state_year", "state_target", "target_year"],
            ),
            estimate(
                sample_public,
                "dental_treat",
                outcomes,
                "adult_dental_pooled_public_target",
                controls=["age", "fpl", "healthy"],
                fe_cols=["state_year", "state_target", "target_year"],
            ),
        ],
        ignore_index=True,
    )
    va_event = sample_medicaid.copy()
    va_event["va_target"] = va_event["state_fips"].eq("51").astype(int) * va_event["target_adult"]
    events = estimate_event(
        va_event,
        "va_target",
        [2018, 2019, 2020, 2021, 2022, 2023],
        2020,
        ["dental_visits", "dental_any", "doctor_any", "oop_any"],
        "virginia_adult_dental_event",
        controls=["age", "fpl", "healthy"],
        fe_cols=["state_year", "state_target", "target_year"],
    )
    leave_one = estimate_leave_one(sample_medicaid, ["dental_visits", "dental_any", "doctor_any", "oop_any"])
    sup = support(sample_medicaid, sample_public)

    py.to_parquet(OUT / "adult_medicaid_dental_person_year_panel.parquet", index=False)
    estimates.to_csv(OUT / "adult_medicaid_dental_estimates.csv", index=False)
    events.to_csv(OUT / "adult_medicaid_dental_event.csv", index=False)
    leave_one.to_csv(OUT / "adult_medicaid_dental_leave_one.csv", index=False)
    sup.to_csv(OUT / "adult_medicaid_dental_support.csv", index=False)

    med_s = sup[sup["sample"].eq("medicaid_target")].iloc[0]
    pub_s = sup[sup["sample"].eq("public_target")].iloc[0]
    med_est = estimates[
        (estimates["model"].eq("adult_dental_pooled_medicaid_target")) & (estimates["outcome"].eq("dental_visits"))
    ].iloc[0]
    med_any = estimates[
        (estimates["model"].eq("adult_dental_pooled_medicaid_target")) & (estimates["outcome"].eq("dental_any"))
    ].iloc[0]
    verdict = "NO-CLEAN-GO"
    if med_est["coef"] > 0.2 and med_any["coef"] > 0.03 and med_est["t"] > 1.5:
        verdict = "PROMISING-DENTAL-ACCESS-SIGNAL"
    elif med_est["coef"] > 0 and med_any["coef"] > 0:
        verdict = "DIRECTIONAL-BUT-WEAK"

    report = f"""# Adult Medicaid Dental Benefit Fast Test

## Question

Can current SIPP support an adult, non-child, non-unwinding paper on Medicaid adult dental benefit
expansions and dental care access?

## Source Checks

{chr(10).join(f"- {s}" for s in SOURCES)}

Policy coding:

- Virginia: comprehensive Medicaid adult dental benefit began July 1, 2021; first full-year active
  coding is 2022.
- Maine: MaineCare adult dental coverage began July 1, 2022; first full-year active coding is 2023.
- Tennessee: adult TennCare dental benefits began in 2023.
- New Hampshire: adult Medicaid dental benefit began April 1, 2023.

Michigan 2023 dental redesign is not coded as a clean new benefit in this screen because the official
source describes delivery/redesign rather than a clearly new adult benefit.

## Data Construction

- Source parquet: `data/analysis_ready/sipp_2018_2024_person_month_panel.parquet`.
- Unit: person-year collapsed from monthly rows.
- Sample: adults age 21-64, family income 0-250% FPL, at least six observed months.
- Primary target: Medicaid adult, measured by monthly Medicaid indicators in at least half of
  observed months.
- Secondary target: public-covered adult.
- Treatment: adult dental expansion state x active full-year x target adult.
- Fixed effects: state-year, state-target, target-year.

## Support

Medicaid-target sample:

- Person-years: {int(med_s['person_years']):,}.
- Persons: {int(med_s['persons']):,}.
- Target Medicaid adult person-years: {int(med_s['target_person_years']):,}.
- Expansion-state target person-years: {int(med_s['expansion_state_target_person_years']):,}.
- Active treated person-years: {int(med_s['active_treated_person_years']):,}.

Public-target sample:

- Person-years: {int(pub_s['person_years']):,}.
- Persons: {int(pub_s['persons']):,}.
- Target public adult person-years: {int(pub_s['target_person_years']):,}.
- Expansion-state target person-years: {int(pub_s['expansion_state_target_person_years']):,}.
- Active treated person-years: {int(pub_s['active_treated_person_years']):,}.

## Main Estimates

Medicaid target:

{fmt(estimates, 'adult_dental_pooled_medicaid_target', outcomes)}

Public target:

{fmt(estimates, 'adult_dental_pooled_public_target', outcomes)}

## Virginia Event Check

Virginia is the only treated state with enough post-policy support before the last observed year.
The event check estimates Virginia Medicaid-target differential coefficients by year, omitting 2020.

See `result/idea_scan/adult_medicaid_dental_event.csv`.

## Verdict

`{verdict}`

A clean GO would require:

- a positive effect on `dental_visits` and `dental_any`;
- no similar movement in placebo outcomes such as doctor visits;
- an event pattern concentrated after benefit implementation;
- enough treated-state support that the result is not a single-small-state artifact.

## Artifacts

- `script/11_idea_scan/14_adult_medicaid_dental_fast_test.py`
- `result/idea_scan/adult_medicaid_dental_person_year_panel.parquet`
- `result/idea_scan/adult_medicaid_dental_support.csv`
- `result/idea_scan/adult_medicaid_dental_expansion_state_support.csv`
- `result/idea_scan/adult_medicaid_dental_estimates.csv`
- `result/idea_scan/adult_medicaid_dental_event.csv`
- `result/idea_scan/adult_medicaid_dental_leave_one.csv`
"""
    REPORT.write_text(report, encoding="utf-8")


if __name__ == "__main__":
    main()
