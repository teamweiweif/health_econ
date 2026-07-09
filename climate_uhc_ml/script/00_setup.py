from __future__ import annotations

from pathlib import Path

from common import PROJECT_ROOT, REPORT_DIR, RESULT_DIR, TEMP_DIR, append_log, ensure_dirs, write_csv


VARIABLE_MAP_COLUMNS = [
    "country",
    "survey_name",
    "wave",
    "idno",
    "file",
    "raw_variable",
    "raw_label",
    "harmonized_variable",
    "unit",
    "recall_period",
    "construction_rule",
    "quality_flag",
    "notes",
]


def write_if_missing(path: Path, content: str) -> None:
    if not path.exists():
        path.write_text(content, encoding="utf-8")


def main() -> None:
    ensure_dirs()

    write_if_missing(
        REPORT_DIR / "README.md",
        """# Climate UHC ML

This workspace studies whether climate shocks increase household-level universal health coverage (UHC) failure through financial hardship, forgone care, or both, and whether predictive or causal machine learning improves post-shock policy targeting.

Run the current reproducible pipeline from the project root:

```bash
python script/00_setup.py
python script/01_verify_sources.py
python script/01_inventory_surveys.py
```

Raw files are not stored in `data/`. Direct downloads and source snapshots belong in `temp/`; analysis-ready datasets belong in `data/`.
""",
    )

    placeholders = {
        "data_dictionary.md": "# Harmonized Data Dictionary\n\nStatus: not yet built. This file is populated after raw schema inspection and variable mapping.\n",
        "outcome_construction.md": "# Outcome Construction\n\nStatus: initialized by `script/01_verify_sources.py` with official definitions and formula shells.\n",
        "climate_linkage_audit.md": "# Climate Linkage Audit\n\nStatus: no climate extraction has been run yet. This file records planned sources, linkage rules, and later diagnostics.\n",
        "identification_audit.md": "# Identification Audit\n\nStatus: no causal claim is accepted until survey timing, geography, outcome construction, and placebo tests are available.\n",
        "modeling_report.md": "# Modeling Report\n\nStatus: no predictive, causal, or policy-learning models have been estimated yet.\n",
        "final_report.md": "# Final Report\n\nStatus: project is not complete. The current stage is premise verification and country-wave inventory.\n",
    }
    for filename, content in placeholders.items():
        write_if_missing(REPORT_DIR / filename, content)

    temp_files = {
        "audit_log.md": "# Audit Log\n\n",
        "iteration_notes.md": "# Iteration Notes\n\n",
        "rejected_designs.md": "# Rejected Designs\n\nNo rejected designs yet. Rejections must cite the exact data or identification failure.\n",
    }
    for filename, content in temp_files.items():
        write_if_missing(TEMP_DIR / filename, content)

    write_csv(
        TEMP_DIR / "manual_download_manifest.csv",
        [
            {
                "source_name": "DHS Program",
                "dataset": "DHS/MIS/AIS country surveys with GPS or health-care access modules",
                "official_url": "https://dhsprogram.com/data/",
                "files_needed": "household, individual, GPS cluster files where relevant",
                "reason": "free account and terms approval are normally required; use as secondary access sample unless OOP/consumption are available",
                "status": "manual registration likely required",
            },
            {
                "source_name": "UNICEF MICS",
                "dataset": "MICS country surveys with health-care access modules",
                "official_url": "https://mics.unicef.org/surveys",
                "files_needed": "household and individual microdata plus questionnaires/codebooks",
                "reason": "free login/terms may be required; usually lacks full consumption/OOP needed for SDG 3.8.2",
                "status": "manual registration likely required",
            },
        ],
        ["source_name", "dataset", "official_url", "files_needed", "reason", "status"],
    )

    for name in [
        "variable_map_consumption.csv",
        "variable_map_health_expenditure.csv",
        "variable_map_health_need_access.csv",
        "variable_map_geography.csv",
        "variable_map_survey_design.csv",
        "variable_map_demographics.csv",
        "variable_map_shocks.csv",
    ]:
        write_csv(TEMP_DIR / name, [], VARIABLE_MAP_COLUMNS)

    write_csv(
        RESULT_DIR / "design_scorecard.csv",
        [],
        [
            "design_id",
            "country_scope",
            "outcome",
            "exposure",
            "data_coverage",
            "outcome_validity",
            "exposure_precision",
            "sample_size",
            "event_rate",
            "climate_geography_linkage_quality",
            "identifying_variation",
            "placebo_credibility",
            "model_stability",
            "policy_relevance",
            "ml_usefulness",
            "journal_potential",
            "go_no_go",
            "reason",
        ],
    )

    append_log(TEMP_DIR / "audit_log.md", "Initialized project skeleton and required placeholder files.")
    print(f"Initialized {PROJECT_ROOT}")


if __name__ == "__main__":
    main()
