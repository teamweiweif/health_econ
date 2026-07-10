from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[2]
PANEL = ROOT / "data" / "analysis_ready" / "sipp_2018_2024_person_month_panel.parquet"
OUT = ROOT / "result" / "idea_scan"
REPORT = ROOT / "report" / "23_aca_market_governance_fast_test.md"


MANDATE_SOURCES = [
    "New Jersey Treasury Health Insurance Mandate: https://nj.gov/treasury/njhealthinsurancemandate/",
    "California Franchise Tax Board Health Care Mandate: https://www.ftb.ca.gov/file/personal/filing-situations/healthcare/estimator/",
    "Rhode Island Division of Taxation Health Insurance Mandate: https://tax.ri.gov/guidance/health-insurance-mandate",
]
SBM_SOURCES = [
    "CMS Health Insurance Exchanges 2025 Open Enrollment Report, footnote on state SBE transitions: https://www.cms.gov/files/document/health-insurance-exchanges-2025-open-enrollment-report.pdf",
    "KFF State Health Insurance Marketplace Types: https://www.kff.org/affordable-care-act/state-indicator/state-health-insurance-marketplace-types/",
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


def build_policy_state_year() -> pd.DataFrame:
    years = range(2017, 2024)
    rows = []
    mandate_adoption = {
        "34": 2019,  # New Jersey
        "06": 2020,  # California
        "44": 2020,  # Rhode Island
    }
    # CMS footnote: NJ/PA transitioned for 2021 coverage; KY/ME/NM for 2022 coverage.
    sbm_adoption = {
        "34": 2021,
        "42": 2021,
        "21": 2022,
        "23": 2022,
        "35": 2022,
    }
    # Remove states that were already state-based marketplaces before this transition window.
    preexisting_sbm = {"06", "08", "09", "11", "15", "16", "24", "25", "27", "36", "44", "50", "53"}
    mandate_excluded = {"11", "25", "50"}  # DC small/ambiguous here; MA legacy; VT no penalty.
    for state_fips, state_name in STATE_NAMES.items():
        for year in years:
            mandate_year = mandate_adoption.get(state_fips)
            sbm_year = sbm_adoption.get(state_fips)
            rows.append(
                {
                    "state_fips": state_fips,
                    "state_name": state_name,
                    "reference_year": year,
                    "mandate_adoption_year": mandate_year,
                    "mandate_new_state": int(mandate_year is not None),
                    "mandate_active": int(mandate_year is not None and year >= mandate_year),
                    "mandate_event_time": year - mandate_year if mandate_year is not None else np.nan,
                    "mandate_sample_state": int(state_fips not in mandate_excluded),
                    "sbm_adoption_year": sbm_year,
                    "sbm_transition_state": int(sbm_year is not None),
                    "sbm_active": int(sbm_year is not None and year >= sbm_year),
                    "sbm_event_time": year - sbm_year if sbm_year is not None else np.nan,
                    "sbm_risk_state": int(state_fips not in preexisting_sbm),
                }
            )
    return pd.DataFrame(rows)


def build_person_year() -> pd.DataFrame:
    cols = [
        "person_id",
        "person_month_key",
        "reference_year",
        "reference_month",
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
        "RPRITYPE2",
        "RMARKTPLACE",
        "EPRIEXCH1",
        "EPRIEXCH2",
        "EPRISUBS1",
        "EPRISUBS2",
        "EMDEXCH",
        "EMDSUBS",
        "TMDPAY",
        "TVISDOC",
        "TVISDENT",
        "THOSPNIT",
    ]
    df = pd.read_parquet(PANEL, columns=cols)
    df = df[df["reference_year"].between(2017, 2023)].copy()
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
    df["medicaid"] = yes(df["EMDMTH"]).astype(float)
    df["direct_market"] = (yes(df["RPRITYPE2"]) | yes(df["RMARKTPLACE"])).astype(float)
    df["exchange_subsidy"] = (
        yes(df["EPRIEXCH1"])
        | yes(df["EPRIEXCH2"])
        | yes(df["EPRISUBS1"])
        | yes(df["EPRISUBS2"])
        | yes(df["EMDEXCH"])
        | yes(df["EMDSUBS"])
    ).astype(float)
    df["oop_any"] = pd.to_numeric(df["TMDPAY"], errors="coerce").gt(0).astype(float)
    df["doctor_any"] = pd.to_numeric(df["TVISDOC"], errors="coerce").gt(0).astype(float)
    df["dental_any"] = pd.to_numeric(df["TVISDENT"], errors="coerce").gt(0).astype(float)
    df["hospital_any"] = pd.to_numeric(df["THOSPNIT"], errors="coerce").gt(0).astype(float)

    agg = (
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
            direct_market=("direct_market", "mean"),
            exchange_subsidy=("exchange_subsidy", "mean"),
            oop_any=("oop_any", "mean"),
            doctor_any=("doctor_any", "mean"),
            dental_any=("dental_any", "mean"),
            hospital_any=("hospital_any", "mean"),
        )
        .reset_index()
    )
    agg["healthy"] = agg["healthy"].ge(0.5).astype(int)
    agg["subsidy_income"] = agg["fpl"].between(1.38, 4.0, inclusive="both").astype(int)
    agg["middle_income"] = agg["fpl"].between(1.38, 6.0, inclusive="both").astype(int)
    agg["high_income"] = agg["fpl"].between(4.0, 6.0, inclusive="right").astype(int)
    return agg


def estimate_static(
    data: pd.DataFrame,
    sample_mask: pd.Series,
    policy_col: str,
    interaction_col: str | None,
    outcomes: list[str],
    model_name: str,
) -> pd.DataFrame:
    sample = data.loc[sample_mask].copy()
    rows = []
    for outcome in outcomes:
        d = sample[sample[outcome].notna() & sample["weight"].gt(0)].copy()
        if d.empty:
            continue
        x_parts = [
            pd.Series(1.0, index=d.index, name="const"),
            d[policy_col].astype(float).rename(policy_col),
            d["age"].astype(float).rename("age"),
            d["fpl"].astype(float).clip(0, 8).rename("fpl_clip"),
        ]
        target_cols = [policy_col]
        if interaction_col is not None:
            interaction_name = f"{policy_col}_x_{interaction_col}"
            d[interaction_name] = d[policy_col].astype(float) * d[interaction_col].astype(float)
            x_parts.append(d[interaction_col].astype(float).rename(interaction_col))
            x_parts.append(d[interaction_name])
            target_cols.append(interaction_name)
        x_parts.append(pd.get_dummies(d["state_fips"], prefix="st", drop_first=True, dtype=float))
        x_parts.append(pd.get_dummies(d["reference_year"].astype(str), prefix="yr", drop_first=True, dtype=float))
        x = pd.concat(x_parts, axis=1)
        beta, se, n = wls_hc1(d[outcome].astype(float).to_numpy(), x.to_numpy(dtype=float), d["weight"].to_numpy(dtype=float))
        b = pd.Series(beta, index=x.columns)
        s = pd.Series(se, index=x.columns)
        for term in target_cols:
            rows.append(
                {
                    "model": model_name,
                    "outcome": outcome,
                    "term": term,
                    "coef": b.get(term, np.nan),
                    "se": s.get(term, np.nan),
                    "t": b.get(term, np.nan) / s.get(term, np.nan) if s.get(term, np.nan) else np.nan,
                    "n_person_years": n,
                    "n_persons": int(d["person_id"].nunique()),
                    "n_states": int(d["state_fips"].nunique()),
                    "weighted_mean": wmean(d[outcome], d["weight"]),
                }
            )
    return pd.DataFrame(rows)


def estimate_event(
    data: pd.DataFrame,
    sample_mask: pd.Series,
    event_time_col: str,
    treated_col: str,
    event_times: list[int],
    outcomes: list[str],
    model_name: str,
    omitted: int = -1,
) -> pd.DataFrame:
    sample = data.loc[sample_mask].copy()
    rows = []
    terms = []
    for e in event_times:
        if e == omitted:
            continue
        name = f"event_{e}"
        sample[name] = ((sample[treated_col] == 1) & (sample[event_time_col] == e)).astype(float)
        terms.append(name)
    for outcome in outcomes:
        d = sample[sample[outcome].notna() & sample["weight"].gt(0)].copy()
        x = pd.concat(
            [
                pd.Series(1.0, index=d.index, name="const"),
                d[terms],
                d["age"].astype(float).rename("age"),
                d["fpl"].astype(float).clip(0, 8).rename("fpl_clip"),
                pd.get_dummies(d["state_fips"], prefix="st", drop_first=True, dtype=float),
                pd.get_dummies(d["reference_year"].astype(str), prefix="yr", drop_first=True, dtype=float),
            ],
            axis=1,
        )
        beta, se, n = wls_hc1(d[outcome].astype(float).to_numpy(), x.to_numpy(dtype=float), d["weight"].to_numpy(dtype=float))
        b = pd.Series(beta, index=x.columns)
        s = pd.Series(se, index=x.columns)
        for e in event_times:
            if e == omitted:
                continue
            term = f"event_{e}"
            rows.append(
                {
                    "model": model_name,
                    "outcome": outcome,
                    "event_time": e,
                    "coef": b.get(term, np.nan),
                    "se": s.get(term, np.nan),
                    "t": b.get(term, np.nan) / s.get(term, np.nan) if s.get(term, np.nan) else np.nan,
                    "n_person_years": n,
                    "n_persons": int(d["person_id"].nunique()),
                    "n_states": int(d["state_fips"].nunique()),
                    "omitted_event_time": omitted,
                }
            )
    return pd.DataFrame(rows)


def estimate_leave_one(
    data: pd.DataFrame,
    sample_mask: pd.Series,
    policy_col: str,
    interaction_col: str | None,
    outcomes: list[str],
    model_name: str,
    treated_states: list[str],
) -> pd.DataFrame:
    rows = []
    for state in treated_states:
        dmask = sample_mask & data["state_fips"].ne(state)
        est = estimate_static(data, dmask, policy_col, interaction_col, outcomes, model_name)
        est.insert(1, "excluded_treated_state", state)
        est.insert(2, "excluded_treated_state_name", STATE_NAMES[state])
        rows.append(est)
    return pd.concat(rows, ignore_index=True)


def support_tables(data: pd.DataFrame) -> pd.DataFrame:
    rows = []
    masks = {
        "mandate_aca_relevant_138_600": (
            data["mandate_sample_state"].eq(1)
            & data["age"].between(26, 64, inclusive="both")
            & data["fpl"].between(1.38, 6.0, inclusive="both")
        ),
        "mandate_subsidy_income_138_400": (
            data["mandate_sample_state"].eq(1)
            & data["age"].between(26, 64, inclusive="both")
            & data["fpl"].between(1.38, 4.0, inclusive="both")
        ),
        "sbm_transition_risk_138_600": (
            data["sbm_risk_state"].eq(1)
            & data["age"].between(26, 64, inclusive="both")
            & data["fpl"].between(1.38, 6.0, inclusive="both")
        ),
        "sbm_transition_risk_138_400": (
            data["sbm_risk_state"].eq(1)
            & data["age"].between(26, 64, inclusive="both")
            & data["fpl"].between(1.38, 4.0, inclusive="both")
        ),
    }
    for name, mask in masks.items():
        d = data.loc[mask].copy()
        rows.append(
            {
                "sample": name,
                "person_years": int(len(d)),
                "persons": int(d["person_id"].nunique()),
                "states": int(d["state_fips"].nunique()),
                "treated_state_person_years_mandate": int(d.loc[d["mandate_new_state"].eq(1)].shape[0]),
                "active_person_years_mandate": int(d.loc[d["mandate_active"].eq(1)].shape[0]),
                "treated_state_person_years_sbm": int(d.loc[d["sbm_transition_state"].eq(1)].shape[0]),
                "active_person_years_sbm": int(d.loc[d["sbm_active"].eq(1)].shape[0]),
                "mean_uninsured": wmean(d["uninsured"], d["weight"]),
                "mean_direct_market": wmean(d["direct_market"], d["weight"]),
                "mean_exchange_subsidy": wmean(d["exchange_subsidy"], d["weight"]),
            }
        )
    return pd.DataFrame(rows)


def verdict(est: pd.DataFrame, event: pd.DataFrame, policy_col: str, model: str) -> str:
    piv = est[(est["model"] == model) & (est["term"] == policy_col)].set_index("outcome")
    uninsured = piv.loc["uninsured", "coef"] if "uninsured" in piv.index else np.nan
    uninsured_t = piv.loc["uninsured", "t"] if "uninsured" in piv.index else np.nan
    any_cov = piv.loc["any_coverage", "coef"] if "any_coverage" in piv.index else np.nan
    any_cov_t = piv.loc["any_coverage", "t"] if "any_coverage" in piv.index else np.nan
    direct = piv.loc["direct_market", "coef"] if "direct_market" in piv.index else np.nan
    direct_t = piv.loc["direct_market", "t"] if "direct_market" in piv.index else np.nan
    pre = event[(event["model"] == f"{model}_event") & (event["event_time"] <= -2)]
    max_pre = pre["coef"].abs().max() if not pre.empty else np.nan
    if np.isfinite(uninsured) and np.isfinite(any_cov) and uninsured < -0.005 and any_cov > 0.005:
        if (
            np.isfinite(direct)
            and direct > 0.003
            and min(abs(uninsured_t), abs(any_cov_t), abs(direct_t)) >= 1.96
            and (not np.isfinite(max_pre) or max_pre < 0.03)
        ):
            return "PROMISING-SIGNAL-BUT-NEEDS-FULL-EVENT-STUDY"
        if np.isfinite(direct) and direct > 0.003:
            return "WEAK-MECHANISM-SIGNAL-NOT-CLEAN-GO"
        return "COVERAGE-SIGNAL-BUT-MECHANISM-WEAK"
    return "NO-CLEAN-COVERAGE-SIGNAL"


def fmt_coef(df: pd.DataFrame, model: str, term: str, outcomes: list[str]) -> str:
    d = df[(df["model"] == model) & (df["term"] == term)].set_index("outcome")
    lines = []
    for outcome in outcomes:
        if outcome not in d.index:
            continue
        r = d.loc[outcome]
        lines.append(f"- `{outcome}`: {r['coef']:+.4f}, se {r['se']:.4f}, t {r['t']:.2f}.")
    return "\n".join(lines)


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    policy = build_policy_state_year()
    person_year = build_person_year().merge(policy, on=["state_fips", "reference_year"], how="left")
    person_year.to_parquet(OUT / "aca_market_governance_person_year_panel.parquet", index=False)
    policy.to_csv(OUT / "aca_market_governance_policy_state_year.csv", index=False)

    outcomes = ["uninsured", "any_coverage", "direct_market", "exchange_subsidy", "private", "oop_any", "doctor_any"]
    mandate_sample = (
        person_year["mandate_sample_state"].eq(1)
        & person_year["age"].between(26, 64, inclusive="both")
        & person_year["fpl"].between(1.38, 6.0, inclusive="both")
        & person_year["months"].ge(6)
    )
    mandate_subsidy_sample = mandate_sample & person_year["fpl"].between(1.38, 4.0, inclusive="both")
    sbm_sample = (
        person_year["sbm_risk_state"].eq(1)
        & person_year["age"].between(26, 64, inclusive="both")
        & person_year["fpl"].between(1.38, 6.0, inclusive="both")
        & person_year["months"].ge(6)
    )
    sbm_subsidy_sample = sbm_sample & person_year["fpl"].between(1.38, 4.0, inclusive="both")

    mandate_est = pd.concat(
        [
            estimate_static(
                person_year,
                mandate_sample,
                "mandate_active",
                "healthy",
                outcomes,
                "mandate_138_600",
            ),
            estimate_static(
                person_year,
                mandate_subsidy_sample,
                "mandate_active",
                "healthy",
                outcomes,
                "mandate_138_400",
            ),
        ],
        ignore_index=True,
    )
    mandate_event = estimate_event(
        person_year,
        mandate_sample,
        "mandate_event_time",
        "mandate_new_state",
        [-2, -1, 0, 1, 2, 3],
        ["uninsured", "any_coverage", "direct_market", "exchange_subsidy"],
        "mandate_138_600_event",
    )
    sbm_est = pd.concat(
        [
            estimate_static(person_year, sbm_sample, "sbm_active", "subsidy_income", outcomes, "sbm_138_600"),
            estimate_static(
                person_year,
                sbm_subsidy_sample,
                "sbm_active",
                None,
                outcomes,
                "sbm_138_400",
            ),
        ],
        ignore_index=True,
    )
    sbm_event = estimate_event(
        person_year,
        sbm_sample,
        "sbm_event_time",
        "sbm_transition_state",
        [-3, -2, -1, 0, 1, 2],
        ["uninsured", "any_coverage", "direct_market", "exchange_subsidy"],
        "sbm_138_600_event",
    )
    leave_one = pd.concat(
        [
            estimate_leave_one(
                person_year,
                mandate_sample,
                "mandate_active",
                "healthy",
                ["uninsured", "any_coverage", "direct_market", "exchange_subsidy"],
                "mandate_138_600_leave_one",
                ["06", "34", "44"],
            ),
            estimate_leave_one(
                person_year,
                sbm_sample,
                "sbm_active",
                "subsidy_income",
                ["uninsured", "any_coverage", "direct_market", "exchange_subsidy"],
                "sbm_138_600_leave_one",
                ["21", "23", "34", "35", "42"],
            ),
        ],
        ignore_index=True,
    )
    support = support_tables(person_year)

    mandate_est.to_csv(OUT / "aca_market_governance_mandate_estimates.csv", index=False)
    mandate_event.to_csv(OUT / "aca_market_governance_mandate_event.csv", index=False)
    sbm_est.to_csv(OUT / "aca_market_governance_sbm_estimates.csv", index=False)
    sbm_event.to_csv(OUT / "aca_market_governance_sbm_event.csv", index=False)
    leave_one.to_csv(OUT / "aca_market_governance_leave_one.csv", index=False)
    support.to_csv(OUT / "aca_market_governance_support.csv", index=False)

    mandate_v = verdict(mandate_est, mandate_event, "mandate_active", "mandate_138_600")
    sbm_v = verdict(sbm_est, sbm_event, "sbm_active", "sbm_138_600")

    mandate_support = support[support["sample"].eq("mandate_aca_relevant_138_600")].iloc[0]
    sbm_support = support[support["sample"].eq("sbm_transition_risk_138_600")].iloc[0]
    report = f"""# ACA Market Governance Fast Test

## Question

Can current SIPP 2017-2023 reference-year data support a new adult, non-child, non-unwinding
paper around ACA market-governance policies?

This screen tests two policy shocks:

1. State individual mandate penalties after the federal penalty was set to zero.
2. State transitions from HealthCare.gov to full State-Based Marketplaces.

## Source Checks

Individual mandate policy coding:

{chr(10).join(f"- {s}" for s in MANDATE_SOURCES)}

State-Based Marketplace transition coding:

{chr(10).join(f"- {s}" for s in SBM_SOURCES)}

## Data Construction

- Source parquet: `data/analysis_ready/sipp_2018_2024_person_month_panel.parquet`.
- Collapsed to person-year from monthly observations.
- Sample: adults age 26-64 with family income 138-600% FPL and at least six observed months.
- Main outcomes: annual share of months uninsured, covered, direct-purchase/Marketplace, exchange/subsidized private, private, OOP any, and doctor visit any.
- Models: weighted linear probability screens with state and year fixed effects.
- Mandate heterogeneity: `mandate_active x healthy`, where healthy is excellent/very good health.
- SBM heterogeneity: `sbm_active x subsidy_income`, where subsidy-income is 138-400% FPL.

## Support

Mandate sample:

- Person-years: {int(mandate_support['person_years']):,}.
- Persons: {int(mandate_support['persons']):,}.
- States: {int(mandate_support['states']):,}.
- Treated-state person-years: {int(mandate_support['treated_state_person_years_mandate']):,}.
- Active mandate person-years: {int(mandate_support['active_person_years_mandate']):,}.

SBM transition sample:

- Person-years: {int(sbm_support['person_years']):,}.
- Persons: {int(sbm_support['persons']):,}.
- States: {int(sbm_support['states']):,}.
- Transition-state person-years: {int(sbm_support['treated_state_person_years_sbm']):,}.
- Active SBM person-years: {int(sbm_support['active_person_years_sbm']):,}.

## Static Estimates: State Individual Mandates

Main term: `mandate_active`, state/year FE, adults 26-64 and 138-600% FPL.

{fmt_coef(mandate_est, 'mandate_138_600', 'mandate_active', outcomes)}

Healthy-selection term: `mandate_active_x_healthy`.

{fmt_coef(mandate_est, 'mandate_138_600', 'mandate_active_x_healthy', outcomes)}

Verdict: `{mandate_v}`.

## Static Estimates: State-Based Marketplace Transitions

Main term: `sbm_active`, state/year FE, adults 26-64 and 138-600% FPL in the transition-risk state set.

{fmt_coef(sbm_est, 'sbm_138_600', 'sbm_active', outcomes)}

Subsidy-income term: `sbm_active_x_subsidy_income`.

{fmt_coef(sbm_est, 'sbm_138_600', 'sbm_active_x_subsidy_income', outcomes)}

Verdict: `{sbm_v}`.

## Interpretation

This is a fast screen, not a final paper design. A clean GO would require:

- signs aligned with the policy mechanism;
- enough treated support;
- no large pre-event deviations in the event coefficients;
- robustness to excluding states with overlapping ACA policies such as reinsurance and state subsidies.

## Artifacts

- `script/11_idea_scan/10_aca_market_governance_fast_test.py`
- `result/idea_scan/aca_market_governance_policy_state_year.csv`
- `result/idea_scan/aca_market_governance_person_year_panel.parquet`
- `result/idea_scan/aca_market_governance_support.csv`
- `result/idea_scan/aca_market_governance_mandate_estimates.csv`
- `result/idea_scan/aca_market_governance_mandate_event.csv`
- `result/idea_scan/aca_market_governance_sbm_estimates.csv`
- `result/idea_scan/aca_market_governance_sbm_event.csv`
- `result/idea_scan/aca_market_governance_leave_one.csv`
"""
    REPORT.write_text(report, encoding="utf-8")


if __name__ == "__main__":
    main()
