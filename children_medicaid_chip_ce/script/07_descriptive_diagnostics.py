from __future__ import annotations

import pandas as pd
import matplotlib.pyplot as plt

from project_utils import DATA, REPORT, RESULT, TEMP, append_audit


def main() -> None:
    panel = pd.read_parquet(DATA / "main_ddd_panel.parquet")
    panel["month"] = pd.to_datetime(panel["month"])
    panel["treatment_group"] = panel["newly_treated_any_child_ce"].fillna(0).map({1: "newly_treated", 0: "already_or_partly_compliant"})
    coverage = (
        panel.groupby(["group", "treatment_group"])
        .agg(
            rows=("enrollment", "size"),
            nonmissing_enrollment=("enrollment", "count"),
            states=("state_abbr", "nunique"),
            first_month=("month", "min"),
            last_month=("month", "max"),
            missing_rate=("enrollment", lambda s: float(s.isna().mean())),
        )
        .reset_index()
    )
    coverage.to_csv(RESULT / "source_coverage_table.csv", index=False)

    miss = (
        panel.groupby(["state_abbr", "group"])
        .agg(missing_enrollment=("enrollment", lambda s: int(s.isna().sum())), rows=("enrollment", "size"))
        .reset_index()
    )
    miss["missing_rate"] = miss["missing_enrollment"] / miss["rows"]
    miss.to_csv(RESULT / "missingness_by_state_group.csv", index=False)

    trend = (
        panel.groupby(["month", "group", "treatment_group"], as_index=False)["enrollment"]
        .mean()
        .dropna()
    )
    plt.figure(figsize=(11, 6))
    for (group, tg), sub in trend.groupby(["group", "treatment_group"]):
        plt.plot(sub["month"], sub["enrollment"] / 1_000_000, label=f"{group}: {tg}")
    plt.axvline(pd.Timestamp("2024-01-01"), color="black", linewidth=1, linestyle="--")
    plt.axvspan(pd.Timestamp("2023-04-01"), pd.Timestamp("2023-12-01"), color="gray", alpha=0.15)
    plt.ylabel("Mean enrollment, millions")
    plt.xlabel("Month")
    plt.title("Child and adult Medicaid/CHIP enrollment trends by CE treatment group")
    plt.legend(fontsize=8)
    plt.tight_layout()
    plt.savefig(RESULT / "descriptive_trends_child_adult.png", dpi=180)
    plt.close()

    gap = panel.pivot_table(index=["state_abbr", "month", "treatment_group"], columns="group", values="log_enrollment").reset_index()
    gap["child_adult_log_gap"] = gap["child"] - gap["adult"]
    gap_avg = gap.groupby(["month", "treatment_group"], as_index=False)["child_adult_log_gap"].mean()
    plt.figure(figsize=(11, 5))
    for tg, sub in gap_avg.groupby("treatment_group"):
        plt.plot(sub["month"], sub["child_adult_log_gap"], label=tg)
    plt.axvline(pd.Timestamp("2024-01-01"), color="black", linewidth=1, linestyle="--")
    plt.axvspan(pd.Timestamp("2023-04-01"), pd.Timestamp("2023-12-01"), color="gray", alpha=0.15)
    plt.ylabel("Mean log child-adult enrollment gap")
    plt.xlabel("Month")
    plt.title("Raw child-adult enrollment gap by treatment group")
    plt.legend()
    plt.tight_layout()
    plt.savefig(RESULT / "raw_child_adult_gap_by_treatment.png", dpi=180)
    plt.close()

    (TEMP / "iteration_notes.md").open("a", encoding="utf-8").write(
        "- Descriptive diagnostics: raw enrollment trends and child-adult log gaps were plotted. Gray band marks 2023-04 to 2023-12 unwinding transition.\n"
    )
    append_audit("descriptive diagnostics completed")
    print("descriptive diagnostics complete")


if __name__ == "__main__":
    main()
