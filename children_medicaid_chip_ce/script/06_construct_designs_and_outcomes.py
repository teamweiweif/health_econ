from __future__ import annotations

import pandas as pd

from project_utils import DATA, RESULT, TEMP, add_or_update_inventory, append_audit, save_parquet, sha256_file, source_row


def rel_month(month: pd.Timestamp) -> int:
    return (month.year - 2024) * 12 + (month.month - 1)


def main() -> None:
    enrollment = pd.read_parquet(DATA / "enrollment_state_group_month.parquet")
    policy = pd.read_parquet(DATA / "state_policy_month.parquet")
    renewal = pd.read_parquet(DATA / "renewal_state_month.parquet")
    enrollment["month"] = pd.to_datetime(enrollment["month"])
    policy["month"] = pd.to_datetime(policy["month"])
    renewal["month"] = pd.to_datetime(renewal["month"])
    panel = enrollment.merge(
        policy.drop(columns=["state"], errors="ignore"),
        on=["state_abbr", "state_fips", "month"],
        how="left",
        suffixes=("", "_policy"),
    )
    panel["post2024"] = (panel["month"] >= pd.Timestamp("2024-01-01")).astype(int)
    panel["event_month"] = panel["month"].map(rel_month)
    panel["ddd_any_newly_treated"] = (
        panel["newly_treated_any_child_ce"].fillna(0).astype(int)
        * panel["child_group"].astype(int)
        * panel["post2024"]
    )
    panel["ddd_medicaid_newly_treated"] = (
        panel["newly_treated_medicaid_child_ce"].fillna(0).astype(int)
        * panel["child_group"].astype(int)
        * panel["post2024"]
    )
    panel["ddd_partial_or_new"] = (
        ((panel["newly_treated_any_child_ce"].fillna(0).astype(int) == 1) | (panel["partial_pre2024_ce"].fillna(0).astype(int) == 1)).astype(int)
        * panel["child_group"].astype(int)
        * panel["post2024"]
    )
    renewal_small = renewal[
        [
            "state_abbr",
            "month",
            "renewals_due",
            "ex_parte_renewal_rate_due",
            "procedural_termination_rate_due",
            "procedural_termination_share",
            "pending_renewal_share",
        ]
    ].copy()
    panel = panel.merge(renewal_small, on=["state_abbr", "month"], how="left")
    panel["month"] = panel["month"].dt.strftime("%Y-%m-%d")
    save_parquet(panel, DATA / "main_ddd_panel.parquet")

    mechanism = renewal.merge(policy[["state_abbr", "month", "newly_treated_any_child_ce", "partial_pre2024_ce", "separate_chip_program"]], on=["state_abbr", "month"], how="left")
    mechanism["post2024"] = (mechanism["month"] >= pd.Timestamp("2024-01-01")).astype(int)
    mechanism["did_any_newly_treated"] = mechanism["newly_treated_any_child_ce"].fillna(0).astype(int) * mechanism["post2024"]
    mechanism["month"] = mechanism["month"].dt.strftime("%Y-%m-%d")
    save_parquet(mechanism, DATA / "mechanism_panel.parquet")

    acs_path = DATA / "acs_state_age_year.parquet"
    if acs_path.exists():
        acs = pd.read_parquet(acs_path)
        seed = policy.drop_duplicates("state_abbr")[["state_abbr", "newly_treated_any_child_ce", "partial_pre2024_ce", "separate_chip_program"]]
        acs = acs.merge(seed, on="state_abbr", how="left")
        acs["post2024"] = (acs["year"] >= 2024).astype(int)
        acs["ddd_any_newly_treated"] = acs["newly_treated_any_child_ce"].fillna(0).astype(int) * acs["child_group"].astype(int) * acs["post2024"]
        save_parquet(acs, DATA / "validation_panel.parquet")

    rows = [
        {
            "candidate_design": "Main child-vs-adult DDD using any-program newly treated states",
            "treatment_clarity": 4,
            "data_availability": 5,
            "outcome_proximity_to_policy": 4,
            "comparison_credibility": 4,
            "pretrend_performance": "",
            "robustness_to_unwinding_controls": 4,
            "interpretability": 5,
            "publication_novelty": 4,
            "risk_of_replicating_enrollment_only": 3,
            "final_rank": 1,
        },
        {
            "candidate_design": "Medicaid-only child-vs-adult DDD",
            "treatment_clarity": 4,
            "data_availability": 5,
            "outcome_proximity_to_policy": 3,
            "comparison_credibility": 4,
            "pretrend_performance": "",
            "robustness_to_unwinding_controls": 4,
            "interpretability": 4,
            "publication_novelty": 3,
            "risk_of_replicating_enrollment_only": 3,
            "final_rank": 2,
        },
        {
            "candidate_design": "CHIP-only DDD for separate CHIP states",
            "treatment_clarity": 3,
            "data_availability": 2,
            "outcome_proximity_to_policy": 4,
            "comparison_credibility": 3,
            "pretrend_performance": "",
            "robustness_to_unwinding_controls": 3,
            "interpretability": 3,
            "publication_novelty": 4,
            "risk_of_replicating_enrollment_only": 2,
            "final_rank": 5,
        },
        {
            "candidate_design": "Renewal-mechanism DID",
            "treatment_clarity": 3,
            "data_availability": 4,
            "outcome_proximity_to_policy": 5,
            "comparison_credibility": 2,
            "pretrend_performance": "",
            "robustness_to_unwinding_controls": 2,
            "interpretability": 4,
            "publication_novelty": 4,
            "risk_of_replicating_enrollment_only": 1,
            "final_rank": 3,
        },
        {
            "candidate_design": "ACS state-age-year DDD",
            "treatment_clarity": 4,
            "data_availability": 3,
            "outcome_proximity_to_policy": 3,
            "comparison_credibility": 3,
            "pretrend_performance": "",
            "robustness_to_unwinding_controls": 2,
            "interpretability": 4,
            "publication_novelty": 3,
            "risk_of_replicating_enrollment_only": 2,
            "final_rank": 4,
        },
    ]
    score = pd.DataFrame(rows)
    score.to_csv(RESULT / "design_tournament_scorecard.csv", index=False)
    md_lines = ["# Design Tournament Scorecard", ""]
    for _, row in score.iterrows():
        md_lines.append(f"## {row['final_rank']}. {row['candidate_design']}")
        md_lines.append(
            "Scores: "
            f"treatment clarity={row['treatment_clarity']}; "
            f"data availability={row['data_availability']}; "
            f"outcome proximity={row['outcome_proximity_to_policy']}; "
            f"comparison credibility={row['comparison_credibility']}; "
            f"unwinding robustness={row['robustness_to_unwinding_controls']}; "
            f"interpretability={row['interpretability']}; "
            f"publication novelty={row['publication_novelty']}; "
            f"enrollment-only risk={row['risk_of_replicating_enrollment_only']}."
        )
        md_lines.append("")
    (TEMP / "design_tournament_scorecard.md").write_text("\n".join(md_lines), encoding="utf-8")
    (TEMP / "rejected_designs.md").write_text(
        "# Rejected Or Downgraded Designs\n\n"
        "- Voluntary-adoption DID: rejected as primary because the 2024 policy is a federal mandate layered on prior state variation, not a clean voluntary adoption design.\n"
        "- Aggregate enrollment volatility as true churn: rejected because public state-month aggregate data do not observe individual exits and returns.\n"
        "- Renewal outcomes as child-specific causal outcomes: downgraded because CMS renewal data are generally state-level and not child-specific.\n"
        "- Causal ML: deferred because treatment timing, pretrends, and mechanism coherence must first pass simpler DDD diagnostics.\n"
        "- ACS as main design: downgraded because only 2024 is currently available as post-policy validation in the staged public tables.\n",
        encoding="utf-8",
    )
    add_or_update_inventory(
        [
            source_row(
                "constructed_main_ddd_panel",
                "CMS enrollment merged to constructed policy panel",
                DATA / "main_ddd_panel.parquet",
                period_covered=f"{panel['month'].min()} to {panel['month'].max()}",
                unit="state-group-month",
                row_count=len(panel),
                column_count=len(panel.columns),
                checksum=sha256_file(DATA / "main_ddd_panel.parquet"),
                notes="Core DDD panel.",
            ),
            source_row(
                "constructed_mechanism_panel",
                "CMS renewal merged to constructed policy panel",
                DATA / "mechanism_panel.parquet",
                period_covered=f"{mechanism['month'].min()} to {mechanism['month'].max()}",
                unit="state-month",
                row_count=len(mechanism),
                column_count=len(mechanism.columns),
                checksum=sha256_file(DATA / "mechanism_panel.parquet"),
                notes="State-level mechanism panel; not child-specific.",
            ),
        ]
    )
    append_audit("design and outcome panels constructed")
    print(f"main DDD panel rows={len(panel)} mechanism rows={len(mechanism)}")


if __name__ == "__main__":
    main()
