from __future__ import annotations

import csv
import os
import unicodedata
from collections import defaultdict
from pathlib import Path
from typing import Any

from common import REPORT_DIR, TEMP_DIR, append_log, ensure_dirs, write_csv


TOP_N = int(os.environ.get("CLIMATE_UHC_REQUEST_PACKET_TOP_N", "20"))

ACTION_QUEUE_PATH = TEMP_DIR / "manual_access_action_queue.csv"
REPORT_PATH = REPORT_DIR / "raw_data_request_packet.md"
RAW_README_PATH = TEMP_DIR / "raw_downloads" / "README.md"

ACTION_COLUMNS = [
    "action_rank",
    "source_name",
    "account_or_access_url",
    "dataset_idno",
    "dataset",
    "official_url",
    "local_target_folder",
    "priority_score",
    "priority_reason",
    "key_modules_to_verify_first",
    "post_download_command",
    "notes",
]


def read_csv_dicts(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        return []
    with path.open(encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def safe_folder(text: str) -> str:
    keep = []
    for char in text:
        if char.isalnum() or char in {"-", "_", "."}:
            keep.append(char)
        else:
            keep.append("_")
    return "".join(keep).strip("_")[:120] or "manual_dataset"


def account_url(source_name: str, official_url: str) -> str:
    if source_name == "World Bank Microdata Library":
        return official_url
    if source_name == "DHS Program":
        return "https://dhsprogram.com/data/"
    if source_name == "UNICEF MICS":
        return "https://mics.unicef.org/surveys"
    return official_url


def checklist_by_idno(rows: list[dict[str, str]]) -> dict[str, list[dict[str, str]]]:
    grouped: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in rows:
        grouped[row.get("idno", "")].append(row)
    for values in grouped.values():
        values.sort(key=lambda row: (-int(row.get("candidate_variable_count") or 0), row.get("file_name", "")))
    return grouped


def module_summary(rows: list[dict[str, str]], limit: int = 8) -> str:
    if not rows:
        return ""
    pieces = []
    for row in rows[:limit]:
        pieces.append(f"{row.get('file_name', '')} [{row.get('candidate_categories', '')}]")
    return "; ".join(pieces)


def build_action_queue() -> list[dict[str, str]]:
    priority = read_csv_dicts(TEMP_DIR / "manual_download_priority.csv")
    checklist = checklist_by_idno(read_csv_dicts(TEMP_DIR / "manual_download_file_checklist.csv"))
    actions = []
    world_bank = [row for row in priority if row.get("source_name") == "World Bank Microdata Library"][:TOP_N]
    secondary = [row for row in priority if row.get("source_name") != "World Bank Microdata Library"]
    selected = world_bank + secondary
    for idx, row in enumerate(selected, start=1):
        idno = row.get("idno", "")
        folder = safe_folder(idno or row.get("source_name", "secondary_source"))
        modules = module_summary(checklist.get(idno, []))
        actions.append(
            {
                "action_rank": str(idx),
                "source_name": row.get("source_name", ""),
                "account_or_access_url": account_url(row.get("source_name", ""), row.get("official_url", "")),
                "dataset_idno": idno,
                "dataset": row.get("dataset", ""),
                "official_url": row.get("official_url", ""),
                "local_target_folder": f"temp/raw_downloads/{folder}/",
                "priority_score": row.get("priority_score", ""),
                "priority_reason": row.get("priority_reason", ""),
                "key_modules_to_verify_first": modules,
                "post_download_command": "powershell -ExecutionPolicy Bypass -File script/run_all.ps1",
                "notes": "Download full raw package and documentation where available; module list is only a first verification guide.",
            }
        )
    return actions


def markdown_table(rows: list[dict[str, str]], columns: list[str]) -> str:
    lines = ["| " + " | ".join(columns) + " |", "|" + "|".join("---" for _ in columns) + "|"]
    for row in rows:
        values = []
        for column in columns:
            value = ascii_safe(row.get(column, "")).replace("|", "/")
            if len(value) > 160:
                value = value[:157] + "..."
            values.append(value)
        lines.append("| " + " | ".join(values) + " |")
    return "\n".join(lines)


def ascii_safe(text: str) -> str:
    normalized = unicodedata.normalize("NFKD", text)
    return normalized.encode("ascii", "ignore").decode("ascii")


def write_packet(actions: list[dict[str, str]]) -> None:
    wb_actions = [row for row in actions if row["source_name"] == "World Bank Microdata Library"]
    secondary_actions = [row for row in actions if row["source_name"] != "World Bank Microdata Library"]
    public_doc_summary = read_csv_dicts(TEMP_DIR / "worldbank_access_gate_summary.csv")
    public_doc_rows = [
        {
            "dataset_idno": row.get("idno", ""),
            "saved_resource_count": row.get("saved_resource_count", ""),
            "access_gate_detected": row.get("access_gate_detected", ""),
        }
        for row in public_doc_summary[:20]
    ]
    lines = [
        "# Raw Data Request Packet",
        "",
        "Status: manual account, login, terms, or Data Access Agreement steps are the binding blocker for raw microdata. This packet is generated from the current priority queue and metadata-derived module checklist.",
        "",
        "## Immediate Action Queue",
        "",
        markdown_table(
            actions,
            ["action_rank", "source_name", "dataset_idno", "dataset", "account_or_access_url", "local_target_folder"],
        ),
        "",
        "## World Bank Request Text",
        "",
        "Use this text in any required project description or access request form, adapting only personal/contact details:",
        "",
        "```text",
        "I am requesting access to public/research-use household microdata for an academic empirical project on climate shocks, universal health coverage failure, and policy targeting. The analysis will use household consumption/income, out-of-pocket health expenditure, health-care access/need, survey design, interview timing, and geography variables where permitted. Raw files will be stored locally for reproducible analysis, will not be redistributed, and outputs will report only aggregate/statistical results in accordance with data-use terms. The project will not attempt to identify respondents and will document all source, variable, and harmonization decisions.",
        "```",
        "",
        "## Priority World Bank Downloads",
        "",
        markdown_table(
            wb_actions,
            ["action_rank", "dataset_idno", "official_url", "local_target_folder", "key_modules_to_verify_first"],
        ),
        "",
        "## Public Documentation Already Snapshotted",
        "",
        markdown_table(public_doc_rows, ["dataset_idno", "saved_resource_count", "access_gate_detected"])
        if public_doc_rows
        else "No public documentation snapshot has been run yet. Run `python script/16_snapshot_public_documentation.py` after `script/13_write_reports.py` creates `temp/manual_download_priority.csv`.",
        "",
        "## Secondary Access Sources",
        "",
        markdown_table(
            secondary_actions,
            ["action_rank", "source_name", "account_or_access_url", "dataset", "local_target_folder"],
        )
        if secondary_actions
        else "No secondary-source actions are currently selected.",
        "",
        "## After Download",
        "",
        "1. Place each downloaded raw archive or file in its target folder under `temp/raw_downloads/`.",
        "2. Keep original filenames and archives intact.",
        "3. Run `powershell -ExecutionPolicy Bypass -File script/run_all.ps1` from the project root.",
        "4. Inspect `temp/raw_schema_inventory/raw_file_inventory.csv`, `temp/raw_schema_inventory/raw_variable_catalog.csv`, `temp/harmonization_audit.csv`, and `result/workspace_validation_audit.csv`.",
        "5. Build `temp/harmonization_recipe.csv` only from verified raw variables, keys, labels, units, and recall periods.",
        "",
        "## Guardrails",
        "",
        "- Do not put raw files in `data/`.",
        "- Do not redistribute raw microdata.",
        "- Do not treat metadata-only variable hits as verified raw variables.",
        "- Do not construct SDG 3.8.2 until the discretionary-budget denominator is audited.",
        "- Do not run causal ML or policy learning until reduced-form and placebo gates pass.",
    ]
    REPORT_PATH.write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_raw_readme(actions: list[dict[str, str]]) -> None:
    lines = [
        "# Raw Downloads",
        "",
        "Place manually downloaded raw microdata files here. Do not place raw files in `data/`.",
        "",
        "Preferred target folders:",
        "",
    ]
    for row in actions:
        lines.append(f"- `{row['local_target_folder']}` for {row['dataset_idno'] or row['source_name']}")
    lines.extend(
        [
            "",
            "After adding files, run from the project root:",
            "",
            "```powershell",
            "powershell -ExecutionPolicy Bypass -File script/run_all.ps1",
            "```",
            "",
            "The pipeline will inspect raw schemas before any harmonized analytical dataset is written.",
        ]
    )
    RAW_README_PATH.parent.mkdir(parents=True, exist_ok=True)
    RAW_README_PATH.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    ensure_dirs()
    actions = build_action_queue()
    write_csv(ACTION_QUEUE_PATH, actions, ACTION_COLUMNS)
    write_packet(actions)
    write_raw_readme(actions)
    append_log(TEMP_DIR / "audit_log.md", f"Prepared manual raw-data request packet with {len(actions)} action rows.")
    print(f"Prepared manual raw-data request packet with {len(actions)} action rows.")


if __name__ == "__main__":
    main()
