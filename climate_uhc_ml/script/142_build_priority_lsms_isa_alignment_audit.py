from __future__ import annotations

import csv
import re
from collections import Counter
from pathlib import Path
from typing import Any

from common import PROJECT_ROOT, REPORT_DIR, RESULT_DIR, TEMP_DIR, append_log, ensure_dirs, write_csv


WAVE_PLAN_PATH = RESULT_DIR / "priority_promotion_acquisition_wave_plan.csv"
DOWNLOAD_PACKET_PATH = TEMP_DIR / "priority_download_execution_packet.csv"
MINIMUM_BUNDLES_PATH = TEMP_DIR / "minimum_viable_download_bundles.csv"
COUNTRY_SCREENING_PATH = TEMP_DIR / "country_wave_screening.csv"

AUDIT_PATH = TEMP_DIR / "priority_lsms_isa_alignment_audit.csv"
CANDIDATES_PATH = TEMP_DIR / "priority_lsms_isa_replacement_candidates.csv"
SUMMARY_PATH = RESULT_DIR / "priority_lsms_isa_alignment_summary.csv"
REPORT_PATH = REPORT_DIR / "priority_lsms_isa_alignment_audit.md"

RAW_ROOT = TEMP_DIR / "raw_downloads"

REQUIRED_PRIORITY_COUNTRIES = {"Ethiopia", "Nigeria", "Malawi", "Tanzania", "Uganda"}
OFF_FAMILY_COUNTRIES = {"Malawi", "Uganda"}

AUDIT_COLUMNS = [
    "acquisition_batch_rank",
    "batch_role",
    "country",
    "wave",
    "idno",
    "survey_name",
    "priority_country_required",
    "current_survey_family",
    "lsms_isa_alignment_status",
    "alignment_risk",
    "recommended_action",
    "recommended_replacement_search",
    "download_execution_status",
    "raw_receipt_status",
    "official_url",
    "handoff_readme",
]

CANDIDATE_COLUMNS = [
    "candidate_rank",
    "candidate_role",
    "country",
    "wave",
    "idno",
    "survey_name",
    "candidate_family",
    "alignment_priority",
    "feasibility_score",
    "source_artifact",
    "official_url",
    "current_plan_status",
    "why_candidate",
    "known_limitations",
    "download_action",
]

SUMMARY_COLUMNS = ["metric", "value", "interpretation"]


def read_csv_dicts(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        return []
    with path.open(encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def clean(value: Any) -> str:
    return "" if value is None else str(value).strip()


def safe_int(value: Any, default: int = 0) -> int:
    try:
        text = clean(value)
        return int(float(text)) if text else default
    except (TypeError, ValueError):
        return default


def compact_text(value: str, limit: int = 180) -> str:
    text = " ".join(clean(value).split())
    return text if len(text) <= limit else text[: limit - 3] + "..."


def rel(path: Path) -> str:
    try:
        return str(path.relative_to(PROJECT_ROOT)).replace("\\", "/")
    except ValueError:
        return str(path).replace("\\", "/")


def id_sort_key(idno: str) -> tuple[int, str]:
    match = re.search(r"(\d{4})", idno)
    year = int(match.group(1)) if match else 0
    return year, idno


def official_get_microdata_url(public_url: str) -> str:
    url = clean(public_url)
    if not url:
        return ""
    if url.endswith("/get-microdata"):
        return url
    match = re.search(r"/catalog/(\d+)", url)
    if match:
        return f"https://microdata.worldbank.org/catalog/{match.group(1)}/get-microdata"
    return url


def survey_family(country: str, idno: str, survey_name: str) -> str:
    text = f"{country} {idno} {survey_name}".lower()
    if "social assistance grants" in text or "sage" in text:
        return "non_lsms_social_protection_evaluation"
    if "marriage transitions" in text or "_mtm" in text:
        return "non_lsms_specialized_panel"
    if "general household survey" in text and "panel" in text:
        return "lsms_isa_general_household_panel"
    if "socio-economic panel" in text or "socioeconomic survey" in text:
        return "lsms_isa_socioeconomic_survey"
    if "uganda national panel survey" in text or "national panel survey" in text or "_unps" in text:
        return "lsms_isa_national_panel_survey"
    if "integrated household panel survey" in text or "_ihps" in text:
        return "lsms_isa_integrated_household_panel_survey"
    if "integrated household survey" in text or "_ihs" in text or "ihs-" in text:
        return "lsms_isa_integrated_household_survey"
    if "living standards measurement" in text or "living standards survey" in text or "_lsms" in text or "_lss" in text:
        return "lsms_living_standards_survey"
    if "household living standards" in text:
        return "lsms_living_standards_survey"
    if "household budget" in text or "household income" in text or "household expenditure" in text:
        return "household_budget_or_income_expenditure_survey"
    return "non_lsms_or_unknown_family"


def is_lsms_family(family: str) -> bool:
    return family.startswith("lsms_")


def alignment_status(row: dict[str, str], family: str) -> tuple[str, str, str, str]:
    country = clean(row.get("country"))
    batch_role = clean(row.get("batch_role"))
    if batch_role != "priority_10_wave_batch":
        return (
            "backup_not_core_five_country_requirement",
            "outside_core_scope",
            "Retain only as a sixth-country backup; do not use it to claim the five LSMS/ISA priority-country core is aligned.",
            "No replacement required unless backup country is promoted into the core sample.",
        )
    if country not in REQUIRED_PRIORITY_COUNTRIES:
        return (
            "non_required_core_country",
            "medium",
            "Review why this non-required country is in the core 10-wave campaign.",
            "Compare against the five required LSMS/ISA priority countries.",
        )
    if is_lsms_family(family):
        return (
            "aligned_lsms_isa_or_lsms_panel",
            "low",
            "Keep as a core candidate subject to raw package receipt, value/unit/key verification, and climate-linkage gates.",
            "No family replacement needed before credentialed download.",
        )
    if country == "Malawi":
        return (
            "off_family_needs_lsms_isa_replacement_or_augmentation",
            "high",
            "Do not treat the MTM specialized panel as the Malawi LSMS/ISA core wave. Replace or augment with Malawi IHS/IHPS before main downloads.",
            "Prefer Malawi Integrated Household Survey or Integrated Household Panel Survey candidates already in country_wave_screening.csv.",
        )
    if country == "Uganda":
        return (
            "off_family_needs_unps_lsms_isa_replacement_or_augmentation",
            "high",
            "Do not treat SAGE impact evaluation waves as the Uganda LSMS/ISA core wave. Replace or augment with Uganda UNPS before main downloads.",
            "Prefer Uganda National Panel Survey candidates already in country_wave_screening.csv.",
        )
    return (
        "off_family_needs_lsms_isa_replacement_or_augmentation",
        "high",
        "Do not treat this current core wave as LSMS/ISA aligned until a matching survey family is verified.",
        "Search country_wave_screening.csv and official World Bank metadata for an LSMS/ISA replacement.",
    )


def one_by_id(rows: list[dict[str, str]], field: str = "idno") -> dict[str, dict[str, str]]:
    out: dict[str, dict[str, str]] = {}
    for row in rows:
        key = clean(row.get(field))
        if key and key not in out:
            out[key] = row
    return out


def raw_folder_path(folder: str, idno: str) -> Path:
    folder_clean = clean(folder).replace("\\", "/").strip("/")
    if folder_clean.startswith("temp/raw_downloads/"):
        return PROJECT_ROOT / folder_clean
    if folder_clean:
        return RAW_ROOT / folder_clean
    return RAW_ROOT / idno


def markdown_table(rows: list[dict[str, str]], columns: list[str], limit: int = 30) -> str:
    lines = ["| " + " | ".join(columns) + " |", "|" + "|".join("---" for _ in columns) + "|"]
    for row in rows[:limit]:
        values = []
        for column in columns:
            value = clean(row.get(column)).replace("|", "/")
            if len(value) > 120:
                value = value[:117] + "..."
            values.append(value)
        lines.append("| " + " | ".join(values) + " |")
    return "\n".join(lines)


def write_handoff(audit_row: dict[str, str]) -> str:
    folder = raw_folder_path("", audit_row.get("idno", ""))
    folder.mkdir(parents=True, exist_ok=True)
    path = folder / "_PRIORITY_LSMS_ISA_ALIGNMENT_AUDIT.md"
    path.write_text(
        f"""# Priority LSMS-ISA Alignment Audit

Dataset: `{audit_row.get('idno', '')}` - {audit_row.get('country', '')} {audit_row.get('wave', '')}

Current family: `{audit_row.get('current_survey_family', '')}`

Alignment status: `{audit_row.get('lsms_isa_alignment_status', '')}`

Risk: `{audit_row.get('alignment_risk', '')}`

Recommended action: {audit_row.get('recommended_action', '')}

Replacement search: {audit_row.get('recommended_replacement_search', '')}

Guardrail: this audit does not promote any data and does not permit ML. Raw
package receipt, raw value review, outcome construction, and climate linkage
must pass before any country-wave is written into `data/`.
""",
        encoding="utf-8",
    )
    return rel(path)


def build_alignment_audit() -> list[dict[str, str]]:
    waves = read_csv_dicts(WAVE_PLAN_PATH)
    packets = one_by_id(read_csv_dicts(DOWNLOAD_PACKET_PATH))
    audit_rows: list[dict[str, str]] = []
    for wave in sorted(waves, key=lambda row: safe_int(row.get("acquisition_batch_rank"), 9999)):
        idno = clean(wave.get("idno"))
        country = clean(wave.get("country"))
        family = survey_family(country, idno, clean(wave.get("survey_name")))
        status_value, risk, action, replacement = alignment_status(wave, family)
        packet = packets.get(idno, {})
        audit_row = {
            "acquisition_batch_rank": clean(wave.get("acquisition_batch_rank")),
            "batch_role": clean(wave.get("batch_role")),
            "country": country,
            "wave": clean(wave.get("wave")),
            "idno": idno,
            "survey_name": clean(wave.get("survey_name")),
            "priority_country_required": "1" if country in REQUIRED_PRIORITY_COUNTRIES else "0",
            "current_survey_family": family,
            "lsms_isa_alignment_status": status_value,
            "alignment_risk": risk,
            "recommended_action": action,
            "recommended_replacement_search": replacement,
            "download_execution_status": clean(packet.get("download_execution_status")),
            "raw_receipt_status": clean(packet.get("raw_receipt_status")),
            "official_url": clean(wave.get("official_url")) or clean(packet.get("official_get_microdata_url")),
            "handoff_readme": "",
        }
        audit_row["handoff_readme"] = write_handoff(audit_row)
        audit_rows.append(audit_row)
    return audit_rows


def screening_candidate(row: dict[str, str]) -> dict[str, str]:
    country = clean(row.get("country"))
    idno = clean(row.get("idno"))
    survey_name = clean(row.get("survey name"))
    family = survey_family(country, idno, survey_name)
    return {
        "country": country,
        "wave": clean(row.get("wave/year")),
        "idno": idno,
        "survey_name": survey_name,
        "candidate_family": family,
        "feasibility_score": clean(row.get("feasibility score from 0 to 5")),
        "official_url": official_get_microdata_url(clean(row.get("public URL"))),
        "source_artifact": "temp/country_wave_screening.csv",
        "reason": clean(row.get("reason for pass/fail")),
    }


def bundle_candidate(row: dict[str, str]) -> dict[str, str]:
    country = clean(row.get("country"))
    idno = clean(row.get("idno"))
    survey_name = clean(row.get("survey_name"))
    family = survey_family(country, idno, survey_name)
    return {
        "country": country,
        "wave": clean(row.get("wave")),
        "idno": idno,
        "survey_name": survey_name,
        "candidate_family": family,
        "feasibility_score": "",
        "official_url": clean(row.get("official_url")),
        "source_artifact": "temp/minimum_viable_download_bundles.csv",
        "reason": clean(row.get("concepts_to_verify")),
    }


def candidate_priority(country: str, family: str, survey_name: str, idno: str) -> tuple[str, int]:
    text = f"{survey_name} {idno}".lower()
    if country == "Malawi" and (
        "_ihps" in text
        or "integrated household panel survey" in text
        or "_ihs" in text
        or "integrated household survey" in text
    ):
        return "strong_lsms_isa_replacement", 3
    if country == "Uganda" and ("_unps" in text or "national panel survey" in text):
        return "strong_lsms_isa_replacement", 3
    if is_lsms_family(family):
        return "strong_lsms_or_living_standards_replacement", 2
    return "weak_non_lsms_do_not_use_as_core", 0


def build_candidates(current_ids: set[str]) -> list[dict[str, str]]:
    raw_candidates: dict[str, dict[str, str]] = {}
    for row in read_csv_dicts(COUNTRY_SCREENING_PATH):
        candidate = screening_candidate(row)
        if candidate["country"] in OFF_FAMILY_COUNTRIES and candidate["idno"]:
            raw_candidates[candidate["idno"]] = candidate
    for row in read_csv_dicts(MINIMUM_BUNDLES_PATH):
        candidate = bundle_candidate(row)
        if candidate["country"] in OFF_FAMILY_COUNTRIES and candidate["idno"] and candidate["idno"] not in raw_candidates:
            raw_candidates[candidate["idno"]] = candidate

    rows: list[dict[str, str]] = []
    for candidate in raw_candidates.values():
        country = candidate["country"]
        idno = candidate["idno"]
        family = candidate["candidate_family"]
        priority_label, priority_score = candidate_priority(country, family, candidate["survey_name"], idno)
        if priority_score == 0 and idno not in current_ids:
            continue
        current_status = "current_plan_wave" if idno in current_ids else "not_currently_selected"
        if current_status == "current_plan_wave" and priority_score == 0:
            role = "current_off_family_do_not_use_as_core"
        elif priority_score >= 3:
            role = "replace_current_core_wave"
        else:
            role = "augmentation_or_backup_after_stronger_candidates"
        why = (
            "Matches the explicit LSMS/LSMS-ISA priority country requirement and is a better family match than the current off-family core wave."
            if priority_score >= 3
            else "Current selected off-family wave documents the problem but should not anchor the core sample."
            if role == "current_off_family_do_not_use_as_core"
            else "Potential living-standards style augmentation, but not first-choice for replacing the off-family core wave."
        )
        limitation = (
            "Still requires official raw package receipt, module-level file acceptance, value/unit/key review, outcome audit, and climate linkage."
            if priority_score > 0
            else "Not LSMS/ISA-aligned enough for the main five-country core without explicit redesign."
        )
        rows.append(
            {
                "candidate_rank": "",
                "candidate_role": role,
                "country": country,
                "wave": candidate["wave"],
                "idno": idno,
                "survey_name": candidate["survey_name"],
                "candidate_family": family,
                "alignment_priority": priority_label,
                "feasibility_score": candidate["feasibility_score"],
                "source_artifact": candidate["source_artifact"],
                "official_url": candidate["official_url"],
                "current_plan_status": current_status,
                "why_candidate": why,
                "known_limitations": limitation,
                "download_action": "Use the official get-microdata route and complete-package scope only after the alignment decision updates the priority campaign.",
            }
        )

    rows.sort(
        key=lambda row: (
            row["country"],
            -({"strong_lsms_isa_replacement": 3, "strong_lsms_or_living_standards_replacement": 2}.get(row["alignment_priority"], 0)),
            -safe_int(row.get("feasibility_score")),
            -id_sort_key(row.get("idno", ""))[0],
            row["idno"],
        )
    )
    for rank, row in enumerate(rows, start=1):
        row["candidate_rank"] = str(rank)
        row["why_candidate"] = compact_text(row["why_candidate"])
        row["known_limitations"] = compact_text(row["known_limitations"])
    return rows


def build_summary(audit_rows: list[dict[str, str]], candidate_rows: list[dict[str, str]]) -> list[dict[str, str]]:
    status_counts = Counter(row["lsms_isa_alignment_status"] for row in audit_rows)
    core_rows = [row for row in audit_rows if row["batch_role"] == "priority_10_wave_batch"]
    backup_rows = [row for row in audit_rows if row["batch_role"] != "priority_10_wave_batch"]
    required_core_countries = {row["country"] for row in core_rows if row["country"] in REQUIRED_PRIORITY_COUNTRIES}
    off_family_core = [row for row in core_rows if row["alignment_risk"] == "high"]
    strong_candidates = [row for row in candidate_rows if row["alignment_priority"] == "strong_lsms_isa_replacement" and row["current_plan_status"] != "current_plan_wave"]
    countries_with_strong = {row["country"] for row in strong_candidates}
    inventory_gap_countries = sorted({row["country"] for row in off_family_core} - countries_with_strong)

    rows = [
        {"metric": "priority_lsms_alignment_current_campaign_rows", "value": str(len(audit_rows)), "interpretation": "Current priority/backup campaign rows audited for LSMS/ISA alignment."},
        {"metric": "priority_lsms_alignment_core_priority_wave_rows", "value": str(len(core_rows)), "interpretation": "Core 10-wave campaign rows."},
        {"metric": "priority_lsms_alignment_backup_wave_rows", "value": str(len(backup_rows)), "interpretation": "Backup wave rows outside the five-country LSMS/ISA core requirement."},
        {"metric": "priority_lsms_alignment_required_priority_countries", "value": str(len(REQUIRED_PRIORITY_COUNTRIES)), "interpretation": "Required priority countries from the LSMS/ISA-centered goal."},
        {"metric": "priority_lsms_alignment_current_required_countries", "value": str(len(required_core_countries)), "interpretation": "Required priority countries represented in the current core campaign."},
        {"metric": "priority_lsms_alignment_aligned_core_wave_rows", "value": str(sum(1 for row in core_rows if row["lsms_isa_alignment_status"] == "aligned_lsms_isa_or_lsms_panel")), "interpretation": "Current core rows that are family-aligned with LSMS/ISA or LSMS-style panels."},
        {"metric": "priority_lsms_alignment_off_family_core_wave_rows", "value": str(len(off_family_core)), "interpretation": "Current core rows that should not be used as the LSMS/ISA main sample without replacement or augmentation."},
        {"metric": "priority_lsms_alignment_off_family_core_country_rows", "value": str(len({row["country"] for row in off_family_core})), "interpretation": "Core priority countries affected by off-family current waves."},
        {"metric": "priority_lsms_alignment_replacement_candidate_rows", "value": str(len(candidate_rows)), "interpretation": "Candidate rows found for replacing or documenting off-family Malawi/Uganda waves."},
        {"metric": "priority_lsms_alignment_strong_replacement_candidate_rows", "value": str(len(strong_candidates)), "interpretation": "Strong LSMS/ISA replacement candidates not already selected in the current campaign."},
        {"metric": "priority_lsms_alignment_inventory_gap_rows", "value": str(len(inventory_gap_countries)), "interpretation": "Off-family core countries without a strong LSMS/ISA replacement in the current screening inventory."},
        {"metric": "priority_lsms_alignment_inventory_gap_countries", "value": ";".join(inventory_gap_countries), "interpretation": "Countries requiring new inventory search if non-empty."},
        {"metric": "priority_lsms_alignment_handoff_readmes_written", "value": str(sum(1 for row in audit_rows if row.get("handoff_readme"))), "interpretation": "Per-wave alignment handoff files written under temp/raw_downloads."},
        {"metric": "priority_lsms_alignment_campaign_decision", "value": "needs_core_wave_replacement_before_manual_download_execution" if off_family_core else "core_wave_families_aligned", "interpretation": "Campaign-level family-alignment decision before credentialed downloads."},
        {"metric": "modeling_gate_status", "value": "blocked", "interpretation": "Models remain blocked until raw-backed promotion thresholds and accepted climate linkage pass."},
    ]
    for status_value, count in sorted(status_counts.items()):
        rows.append({"metric": f"priority_lsms_alignment_status_{status_value}", "value": str(count), "interpretation": "Current campaign row status count."})
    return rows


def write_report(audit_rows: list[dict[str, str]], candidate_rows: list[dict[str, str]], summary_rows: list[dict[str, str]]) -> None:
    high_risk = [row for row in audit_rows if row["alignment_risk"] == "high"]
    strong = [row for row in candidate_rows if row["alignment_priority"] == "strong_lsms_isa_replacement" and row["current_plan_status"] != "current_plan_wave"]
    summary_table = "\n".join(f"| {row['metric']} | {row['value']} | {row['interpretation']} |" for row in summary_rows)
    REPORT_PATH.write_text(
        f"""# Priority LSMS-ISA Alignment Audit

Status: fail-closed family-alignment audit for the current 13-wave
priority/backup campaign. This audit corrects the acquisition plan before
manual credentialed downloads by separating usable execution packets from
country-wave family suitability.

## Bottom Line

- The current campaign covers the five named priority countries, but two core
  country-waves are off-family for the LSMS/LSMS-ISA objective.
- Malawi is currently represented by MTM, a specialized panel, while stronger
  Malawi IHS/IHPS candidates are already present in the screening inventory.
- Uganda is currently represented by SAGE, a social-protection impact
  evaluation, while Uganda UNPS candidates are already present in the screening
  inventory.
- No raw data or promoted data were created. Modeling remains blocked.

## Summary

| Metric | Value | Interpretation |
|---|---:|---|
{summary_table}

## Current High-Risk Core Waves

{markdown_table(high_risk, ['acquisition_batch_rank', 'country', 'wave', 'idno', 'current_survey_family', 'lsms_isa_alignment_status', 'recommended_replacement_search'], 20) if high_risk else 'No high-risk core waves were found.'}

## Strong Replacement Candidates

{markdown_table(strong, ['candidate_rank', 'country', 'wave', 'idno', 'survey_name', 'feasibility_score', 'official_url'], 30) if strong else 'No strong replacement candidates were found in the current screening inventory.'}

## Full Campaign Audit

{markdown_table(audit_rows, ['acquisition_batch_rank', 'batch_role', 'country', 'wave', 'idno', 'current_survey_family', 'lsms_isa_alignment_status', 'alignment_risk'], 20)}

## Machine-Readable Outputs

- `temp/priority_lsms_isa_alignment_audit.csv`
- `temp/priority_lsms_isa_replacement_candidates.csv`
- `result/priority_lsms_isa_alignment_summary.csv`

## Guardrail

The 13 download packets remain useful as acquisition-control artifacts, but the
main core campaign should update Malawi and Uganda before manual download
execution. This artifact does not change the promoted-data registry and does
not authorize predictive ML, reduced-form estimation, causal ML, or policy
learning.
""",
        encoding="utf-8",
    )


def main() -> None:
    ensure_dirs()
    audit_rows = build_alignment_audit()
    current_ids = {row["idno"] for row in audit_rows if row.get("idno")}
    candidate_rows = build_candidates(current_ids)
    summary_rows = build_summary(audit_rows, candidate_rows)
    write_csv(AUDIT_PATH, audit_rows, AUDIT_COLUMNS)
    write_csv(CANDIDATES_PATH, candidate_rows, CANDIDATE_COLUMNS)
    write_csv(SUMMARY_PATH, summary_rows, SUMMARY_COLUMNS)
    write_report(audit_rows, candidate_rows, summary_rows)
    append_log(
        TEMP_DIR / "audit_log.md",
        f"Built priority LSMS-ISA alignment audit rows={len(audit_rows)} candidates={len(candidate_rows)}.",
    )
    print(f"Priority LSMS-ISA alignment audit rows={len(audit_rows)} candidates={len(candidate_rows)}.")


if __name__ == "__main__":
    main()
