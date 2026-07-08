from __future__ import annotations

import pandas as pd

try:
    from project_utils import DATA, RESULT, append_audit
except ModuleNotFoundError:
    from pathlib import Path
    import sys

    sys.path.append(str(Path(__file__).resolve().parent))
    from project_utils import DATA, RESULT, append_audit

from importlib.machinery import SourceFileLoader
from pathlib import Path

model_mod = SourceFileLoader("main_models", str(Path(__file__).resolve().parent / "08_main_models.py")).load_module()
fe_ols = model_mod.fe_ols
prepare_gap_panel = model_mod.prepare_gap_panel


def add_fes(panel: pd.DataFrame) -> pd.DataFrame:
    panel = panel.copy()
    panel["month"] = pd.to_datetime(panel["month"])
    panel["state_group_fe"] = panel["state_abbr"].astype(str) + "_" + panel["group"].astype(str)
    panel["state_month_fe"] = panel["state_abbr"].astype(str) + "_" + panel["month"].dt.strftime("%Y%m")
    panel["group_month_fe"] = panel["group"].astype(str) + "_" + panel["month"].dt.strftime("%Y%m")
    panel["state_fe"] = panel["state_abbr"].astype(str)
    panel["month_fe"] = panel["month"].dt.strftime("%Y%m")
    panel["year_fe"] = panel.get("year", pd.Series([""] * len(panel))).astype(str)
    return panel


def main() -> None:
    panel = prepare_gap_panel()
    fe_main = ["state_fe", "month_fe"]
    robustness = []
    windows = {
        "full_2019plus": panel,
        "exclude_unwinding_transition_2023_04_to_2023_12": panel[
            ~((panel["month"] >= pd.Timestamp("2023-04-01")) & (panel["month"] <= pd.Timestamp("2023-12-01")))
        ],
        "exclude_pandemic_2020_03_to_2022_12": panel[
            ~((panel["month"] >= pd.Timestamp("2020-03-01")) & (panel["month"] <= pd.Timestamp("2022-12-01")))
        ],
        "post_unwinding_pre_and_post_only": panel[
            (panel["month"] <= pd.Timestamp("2020-02-01")) | (panel["month"] >= pd.Timestamp("2024-01-01"))
        ],
    }
    for name, d in windows.items():
        res = fe_ols(d, "log_child_adult_gap", ["did_any_newly_treated"], fe_main, "state_abbr")
        rec = res.iloc[0].to_dict()
        rec["robustness_spec"] = name
        robustness.append(rec)
    pd.DataFrame(robustness).to_csv(RESULT / "robustness_summary.csv", index=False)

    loo = []
    for state in sorted(panel["state_abbr"].dropna().unique()):
        res = fe_ols(
            panel[panel["state_abbr"] != state],
            "log_child_adult_gap",
            ["did_any_newly_treated"],
            fe_main,
            "state_abbr",
        )
        rec = res.iloc[0].to_dict()
        rec["excluded_state"] = state
        loo.append(rec)
    pd.DataFrame(loo).to_csv(RESULT / "leave_one_state_out.csv", index=False)

    mech = pd.read_parquet(DATA / "mechanism_panel.parquet")
    mech["month"] = pd.to_datetime(mech["month"])
    mech = mech[mech["month"] >= pd.Timestamp("2023-03-01")].copy()
    mech["state_fe"] = mech["state_abbr"].astype(str)
    mech["month_fe"] = mech["month"].dt.strftime("%Y%m")
    mech_rows = []
    for outcome in [
        "ex_parte_renewal_rate_due",
        "procedural_termination_rate_due",
        "procedural_termination_share",
        "pending_renewal_share",
    ]:
        res = fe_ols(mech, outcome, ["did_any_newly_treated"], ["state_fe", "month_fe"], "state_abbr")
        res.insert(0, "mechanism_outcome", outcome)
        mech_rows.append(res)
    pd.concat(mech_rows, ignore_index=True).to_csv(RESULT / "renewal_mechanism_table.csv", index=False)

    acs_path = DATA / "validation_panel.parquet"
    if acs_path.exists():
        acs = pd.read_parquet(acs_path)
        acs["state_age_fe"] = acs["state_abbr"].astype(str) + "_" + acs["age_group"].astype(str)
        acs["state_year_fe"] = acs["state_abbr"].astype(str) + "_" + acs["year"].astype(str)
        acs["age_year_fe"] = acs["age_group"].astype(str) + "_" + acs["year"].astype(str)
        acs_rows = []
        for outcome in ["medicaid_percent", "public_insurance_percent", "uninsured_percent"]:
            res = fe_ols(acs, outcome, ["ddd_any_newly_treated"], ["state_age_fe", "state_year_fe", "age_year_fe"], "state_abbr")
            res.insert(0, "validation_outcome", outcome)
            acs_rows.append(res)
        pd.concat(acs_rows, ignore_index=True).to_csv(RESULT / "acs_validation_table.csv", index=False)
    else:
        pd.DataFrame().to_csv(RESULT / "acs_validation_table.csv", index=False)

    append_audit("robustness, leave-one-state-out, renewal mechanism, and ACS validation models attempted")
    print("robustness and falsification complete")


if __name__ == "__main__":
    main()
