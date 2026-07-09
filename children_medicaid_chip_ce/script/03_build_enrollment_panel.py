from __future__ import annotations

import pandas as pd

from project_utils import DATA, RAW, RESULT, STATE_ABBR_TO_FIPS, add_or_update_inventory, append_audit, clean_col, month_from_reporting_period, safe_div, save_parquet, sha256_file, source_row


def choose_best_version(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["version_rank"] = df["preliminary_or_updated"].map({"U": 2, "P": 1}).fillna(0)
    df["final_rank"] = df["final_report"].map({"Y": 1, "N": 0}).fillna(0)
    df = df.sort_values(["state_abbreviation", "reporting_period", "version_rank", "final_rank"])
    return df.groupby(["state_abbreviation", "reporting_period"], as_index=False).tail(1)


def main() -> None:
    files = sorted(RAW.glob("pi-dataset-*-release.csv"))
    if not files:
        raise FileNotFoundError("CMS PI enrollment CSV not found. Run script/01_acquire_sources.py first.")
    raw_path = files[0]
    df = pd.read_csv(raw_path)
    df.columns = [clean_col(c) for c in df.columns]
    df = choose_best_version(df)
    df["month"] = df["reporting_period"].map(month_from_reporting_period)
    df = df[df["month"] >= pd.Timestamp("2018-01-01")].copy()
    df["state_abbr"] = df["state_abbreviation"]
    df["state_fips"] = df["state_abbr"].map(STATE_ABBR_TO_FIPS)
    df["total_enrollment"] = pd.to_numeric(df["total_medicaid_and_chip_enrollment"], errors="coerce")
    df["total_medicaid_enrollment"] = pd.to_numeric(df["total_medicaid_enrollment"], errors="coerce")
    df["total_chip_enrollment"] = pd.to_numeric(df["total_chip_enrollment"], errors="coerce")
    df["child_enrollment"] = pd.to_numeric(df["medicaid_and_chip_child_enrollment"], errors="coerce")
    df["reported_adult_medicaid_enrollment"] = pd.to_numeric(df["total_adult_medicaid_enrollment"], errors="coerce")
    # The reported adult Medicaid field is only available in the later PI release months.
    # Use a consistent non-child Medicaid/CHIP proxy for the child-vs-adult design.
    df["adult_enrollment"] = df["total_enrollment"] - df["child_enrollment"]
    df["medicaid_expansion_status"] = df["state_expanded_medicaid"]

    long_rows = []
    for group, col in [("child", "child_enrollment"), ("adult", "adult_enrollment")]:
        g = df[
            [
                "state_name",
                "state_abbr",
                "state_fips",
                "month",
                "reporting_period",
                "preliminary_or_updated",
                "final_report",
                "medicaid_expansion_status",
                "total_enrollment",
                "total_medicaid_enrollment",
                "total_chip_enrollment",
                col,
            ]
        ].copy()
        g = g.rename(columns={col: "enrollment"})
        g["group"] = group
        long_rows.append(g)
    panel = pd.concat(long_rows, ignore_index=True)
    panel["child_group"] = (panel["group"] == "child").astype(int)
    panel["log_enrollment"] = panel["enrollment"].where(panel["enrollment"] > 0).map(lambda x: pd.NA if pd.isna(x) else __import__("math").log(x))
    panel = panel.sort_values(["state_abbr", "group", "month"])
    panel["enrollment_lag"] = panel.groupby(["state_abbr", "group"])["enrollment"].shift(1)
    panel["month_to_month_change"] = panel["enrollment"] - panel["enrollment_lag"]
    panel["month_to_month_pct_change"] = safe_div(panel["month_to_month_change"], panel["enrollment_lag"])
    panel["net_enrollment_loss_rate"] = (-panel["month_to_month_pct_change"]).where(panel["month_to_month_pct_change"] < 0, 0)
    panel["aggregate_instability_proxy"] = (
        panel.groupby(["state_abbr", "group"])["month_to_month_pct_change"]
        .transform(lambda s: s.abs().rolling(6, min_periods=3).mean())
    )
    wide = df[["state_abbr", "month", "child_enrollment", "adult_enrollment"]].copy()
    wide["child_adult_enrollment_ratio"] = safe_div(wide["child_enrollment"], wide["adult_enrollment"])
    panel = panel.merge(wide[["state_abbr", "month", "child_adult_enrollment_ratio"]], on=["state_abbr", "month"], how="left")
    panel["month"] = panel["month"].dt.strftime("%Y-%m-%d")
    save_parquet(panel, DATA / "enrollment_state_group_month.parquet")

    coverage = (
        panel.groupby(["group"])
        .agg(
            rows=("enrollment", "size"),
            nonmissing_enrollment=("enrollment", "count"),
            states=("state_abbr", "nunique"),
            first_month=("month", "min"),
            last_month=("month", "max"),
        )
        .reset_index()
    )
    coverage.to_csv(RESULT / "source_coverage_table.csv", index=False)
    add_or_update_inventory(
        [
            source_row(
                "constructed_enrollment_state_group_month",
                "CMS PI enrollment CSV",
                DATA / "enrollment_state_group_month.parquet",
                period_covered=f"{panel['month'].min()} to {panel['month'].max()}",
                unit="state-group-month",
                row_count=len(panel),
                column_count=len(panel.columns),
                checksum=sha256_file(DATA / "enrollment_state_group_month.parquet"),
                notes="Best report version selected by Updated over Preliminary. Adult comparison group is a consistent non-child proxy: total Medicaid/CHIP enrollment minus child enrollment, because the reported adult field is unavailable for earlier months.",
            )
        ]
    )
    append_audit("enrollment panel built with child and adult/non-child proxy groups")
    print(f"enrollment panel rows={len(panel)} months={panel['month'].min()}..{panel['month'].max()}")


if __name__ == "__main__":
    main()
