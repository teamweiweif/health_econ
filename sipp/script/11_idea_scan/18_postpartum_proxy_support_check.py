from __future__ import annotations

from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[2]
PANEL = ROOT / "data" / "analysis_ready" / "sipp_2018_2024_person_month_panel.parquet"
OUT = ROOT / "result" / "idea_scan"
REPORT = ROOT / "report" / "38_postpartum_proxy_support_check.md"


SOURCES = [
    "KFF Medicaid Postpartum Coverage Extension Tracker: https://www.kff.org/medicaid/medicaid-postpartum-coverage-extension-tracker/",
    "CMS SHO 21-007 on postpartum extension state plan option: https://www.medicaid.gov/federal-policy-guidance/downloads/sho21007.pdf",
    "CMS press release on postpartum coverage expansion: https://www.cms.gov/newsroom/press-releases/biden-harris-administration-announces-expansion-medicaid-postpartum-coverage-oklahoma-30-states-d-c",
    "ASPE Medicaid Postpartum Coverage Issue Brief: https://aspe.hhs.gov/sites/default/files/documents/a315d594ab2e6dfbb8ef3c2bfccfcc8f/Postpartum-Coverage-Issue-Brief.pdf",
]


def yes(s: pd.Series) -> pd.Series:
    return s.eq(1)


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    cols = [
        "SSUID",
        "PNUM",
        "SHHADID",
        "RFAMNUM",
        "person_id",
        "person_month_key",
        "reference_year",
        "reference_month",
        "state_fips",
        "TAGE",
        "ESEX",
        "TFINCPOV",
        "WPFINWGT",
        "TSSSAMT",
        "RHLTHMTH",
        "RPRIMTH",
        "RPUBMTH",
        "EMDMTH",
        "TVISDOC",
        "TMDPAY",
        "TDAYSICK",
    ]
    df = pd.read_parquet(PANEL, columns=cols)
    df = df[df["reference_year"].between(2017, 2023)].copy()
    df["state_fips"] = df["state_fips"].astype(str).str.zfill(2)
    df["age"] = pd.to_numeric(df["TAGE"], errors="coerce")
    df["female"] = df["ESEX"].eq(2)
    df["fpl"] = pd.to_numeric(df["TFINCPOV"], errors="coerce")
    df.loc[~df["fpl"].between(0, 20), "fpl"] = pd.NA
    df["infant_flag"] = df["age"].lt(1).fillna(False).astype("int8")

    family_month_keys = ["SSUID", "SHHADID", "RFAMNUM", "reference_year", "reference_month"]
    infant_family_month = (
        df.groupby(family_month_keys, observed=True)["infant_flag"].max().rename("family_infant_any").reset_index()
    )
    df = df.merge(infant_family_month, on=family_month_keys, how="left")
    df["postpartum_proxy_month"] = (
        df["female"] & df["age"].between(18, 44, inclusive="both") & df["family_infant_any"].eq(1)
    )
    df["low_income"] = df["fpl"].le(3)
    df["any_coverage"] = yes(df["RHLTHMTH"]).astype(float)
    df["uninsured"] = df["RHLTHMTH"].eq(2).astype(float)
    df["private"] = yes(df["RPRIMTH"]).astype(float)
    df["public"] = (yes(df["RPUBMTH"]) | yes(df["EMDMTH"])).astype(float)
    df["doctor_any"] = pd.to_numeric(df["TVISDOC"], errors="coerce").gt(0).astype(float)
    df["oop_any"] = pd.to_numeric(df["TMDPAY"], errors="coerce").gt(0).astype(float)
    df["sick_days"] = pd.to_numeric(df["TDAYSICK"], errors="coerce").where(lambda x: x.between(0, 365))

    py = (
        df[df["postpartum_proxy_month"]]
        .groupby(["person_id", "state_fips", "reference_year"], observed=True)
        .agg(
            months=("person_month_key", "size"),
            low_income=("low_income", "max"),
            fpl=("fpl", "median"),
            any_coverage=("any_coverage", "mean"),
            uninsured=("uninsured", "mean"),
            public=("public", "mean"),
            private=("private", "mean"),
            doctor_any=("doctor_any", "mean"),
            oop_any=("oop_any", "mean"),
            sick_days=("sick_days", "mean"),
        )
        .reset_index()
    )
    py["low_income"] = py["low_income"].astype(int)
    py["post_2022"] = py["reference_year"].ge(2022).astype(int)

    year_support = (
        py.groupby(["reference_year", "low_income"], observed=True)
        .agg(
            person_years=("person_id", "size"),
            persons=("person_id", "nunique"),
            states=("state_fips", "nunique"),
            mean_months=("months", "mean"),
            uninsured_mean=("uninsured", "mean"),
            public_mean=("public", "mean"),
        )
        .reset_index()
    )
    state_support = (
        py[py["low_income"].eq(1) & py["reference_year"].isin([2022, 2023])]
        .groupby(["state_fips", "reference_year"], observed=True)
        .agg(person_years=("person_id", "size"), persons=("person_id", "nunique"))
        .reset_index()
        .sort_values(["reference_year", "person_years"], ascending=[True, False])
    )
    upper = {
        "all_proxy_person_years": int(len(py)),
        "all_proxy_persons": int(py["person_id"].nunique()),
        "low_income_proxy_person_years": int(py["low_income"].sum()),
        "low_income_proxy_persons": int(py.loc[py["low_income"].eq(1), "person_id"].nunique()),
        "low_income_2022_person_years": int(
            len(py[py["low_income"].eq(1) & py["reference_year"].eq(2022)])
        ),
        "low_income_2023_person_years": int(
            len(py[py["low_income"].eq(1) & py["reference_year"].eq(2023)])
        ),
        "low_income_2022_2023_person_years": int(
            len(py[py["low_income"].eq(1) & py["reference_year"].isin([2022, 2023])])
        ),
        "states_with_low_income_2022_2023_support": int(state_support["state_fips"].nunique()),
        "max_single_state_year_support": int(state_support["person_years"].max()) if len(state_support) else 0,
    }
    upper_df = pd.DataFrame([upper])

    py.to_parquet(OUT / "postpartum_proxy_person_year_panel.parquet", index=False)
    year_support.to_csv(OUT / "postpartum_proxy_year_support.csv", index=False)
    state_support.to_csv(OUT / "postpartum_proxy_state_support.csv", index=False)
    upper_df.to_csv(OUT / "postpartum_proxy_upper_bound.csv", index=False)

    verdict = "NO-GO-SUPPORT"
    report = f"""# Postpartum Medicaid Extension Proxy Support Check

## Question

Can current compact SIPP support an adult maternal-coverage paper on 12-month postpartum Medicaid
extensions?

## Source Checks

{chr(10).join(f"- {s}" for s in SOURCES)}

The policy is substantively important: federal law historically required pregnancy-related Medicaid
coverage only through 60 days postpartum; ARPA created a state plan option for 12-month postpartum
coverage effective April 1, 2022, and the option was later made permanent.

## Compact-Parquet Feasibility

The compact 96-column parquet does not include the direct pregnancy/birth/leave variables needed for
a clean postpartum sample. Metadata confirms that variables such as `EBIRTHRSN3`, `EBIRTHRSN5`,
`TPREBIRTHINT`, and `TPSTBIRTHINT` exist in the broader SIPP metadata but are not in the compact
parquet.

This check therefore uses only a proxy:

- female;
- age 18-44;
- in a family-month with an infant age 0;
- low-income defined as FPL <= 300% for the main upper-bound support count.

This is an adult maternal-coverage proxy, not a child continuous-eligibility design.

## Support Upper Bound

- All proxy person-years, 2017-2023: {upper['all_proxy_person_years']:,}.
- All proxy persons: {upper['all_proxy_persons']:,}.
- Low-income proxy person-years, 2017-2023: {upper['low_income_proxy_person_years']:,}.
- Low-income proxy persons: {upper['low_income_proxy_persons']:,}.
- Low-income proxy person-years in 2022: {upper['low_income_2022_person_years']:,}.
- Low-income proxy person-years in 2023: {upper['low_income_2023_person_years']:,}.
- Low-income proxy person-years in 2022-2023 combined: {upper['low_income_2022_2023_person_years']:,}.
- States with any low-income 2022-2023 proxy support: {upper['states_with_low_income_2022_2023_support']:,}.
- Maximum support in any single state-year: {upper['max_single_state_year_support']:,}.

This is an upper-bound support check. Actual treated support after exact state adoption timing,
Medicaid-enrollment targeting, and postpartum-month restrictions would be smaller.

## Decision

`{verdict}`

The policy is important and adult-focused, but the current compact SIPP parquet is not adequate for
this paper:

- direct birth/pregnancy variables are not present in the compact parquet;
- the infant-in-family proxy is too coarse;
- low-income proxy support in the relevant 2022-2023 window is only
  {upper['low_income_2022_2023_person_years']:,} person-years;
- the largest single state-year has only {upper['max_single_state_year_support']:,} person-years;
- PHE continuous enrollment overlaps the early policy implementation period and would further mute
  coverage changes.

This should not be pursued from the current uploaded compact parquet. It could be revisited only
with a richer SIPP extract that includes pregnancy/birth variables and enough years after 2023.

## Artifacts

- `script/11_idea_scan/18_postpartum_proxy_support_check.py`
- `result/idea_scan/postpartum_proxy_person_year_panel.parquet`
- `result/idea_scan/postpartum_proxy_upper_bound.csv`
- `result/idea_scan/postpartum_proxy_year_support.csv`
- `result/idea_scan/postpartum_proxy_state_support.csv`
"""
    REPORT.write_text(report, encoding="utf-8")


if __name__ == "__main__":
    main()
