from __future__ import annotations

from pathlib import Path

from project_utils import DATA, REPORT, RESULT, ROOT, SCRIPT, TEMP, ensure_dirs, package_versions, write_json


def main() -> None:
    ensure_dirs()
    metadata = {
        "project": "children_medicaid_chip_ce",
        "root": str(ROOT),
        "directories": {
            "data": str(DATA.relative_to(ROOT)),
            "script": str(SCRIPT.relative_to(ROOT)),
            "result": str(RESULT.relative_to(ROOT)),
            "report": str(REPORT.relative_to(ROOT)),
            "temp": str(TEMP.relative_to(ROOT)),
        },
        "package_versions": package_versions(),
    }
    write_json(DATA / "analysis_metadata.json", metadata)
    for name in ["audit_log.md", "iteration_notes.md", "rejected_designs.md"]:
        p = TEMP / name
        if not p.exists():
            p.write_text(f"# {name.replace('_', ' ').replace('.md', '').title()}\n\n", encoding="utf-8")
    print("setup complete")


if __name__ == "__main__":
    main()
