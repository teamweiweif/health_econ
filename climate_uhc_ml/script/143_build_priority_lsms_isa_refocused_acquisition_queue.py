from __future__ import annotations

import csv
import re
from collections import Counter
from pathlib import Path
from typing import Any

from common import PROJECT_ROOT, REPORT_DIR, RESULT_DIR, TEMP_DIR, append_log, ensure_dirs, write_csv


WAVE_PLAN_PATH = RESULT_DIR / "priority_promotion_acquisition_wave_plan.csv"
ALIGNMENT_AUDIT_PATH = TEMP_DIR / "priority_lsms_isa_alignment_audit.csv"
REPLACEMENT_CANDIDATES_PATH = TEMP_DIR / "priority_lsms_isa_replacement_candidates.csv"
COUNTRY_SCREENING_PATH = TEMP_DIR / "country_wave_screening.csv"

REFOCUSED_PLAN_PATH = RESULT_DIR / "priority_lsms_isa_refocused_wave_plan.csv"
QUEUE_PATH = TEMP_DIR / "priority_lsms_isa_refocused_acquisition_queue.csv"
REQUIREMENT_MATRIX_PATH = TEMP_DIR / "priority_lsms_isa_refocused_requirement_matrix.csv"
SUMMARY_PATH = RESULT_DIR / "priority_lsms_isa_refocused_acquisition_summary.csv"
REPORT_PATH = REPORT_DIR / "priority_lsms_isa_refocused_acquisition_queue.md"

RAW_ROOT = TEMP_DIR / "raw_downloads"

REQUIRED_PRIORITY_COUNTRIES = {"Ethiopia", "Nigeria", "Malawi", "Tanzania", "Uganda"}
BACKUP_CANDIDATES_PER_OFF_FAMILY_COUNTRY = 3

PLAN_COLUMNS = [
    "refocused_rank",
    "original_acquisition_batch_rank",
    "batch_role",
    "country",
    "wave",
    "idno",
    "survey_name",
    "official_url",
    "local_target_folder",
    "current_survey_family",
    "refocused_selection_status",
    "supersedes_idno",
    "supersedes_survey_name",
    "replacement_reason",
    "metadata_feasibility_score",
    "metadata_requirement_score",
    "download_scope",
    "raw_package_status",
    "promotion_stop_rule",
]

QUEUE_COLUMNS = [
    "download_priority_order",
    "queue_role",
    "country",
    "wave",
    "idno",
    "survey_name",
    "official_get_microdata_url",
    "local_target_folder",
    "candidate_family",
    "alignment_priority",
    "metadata_feasibility_score",
    "metadata_requirement_score",
    "metadata_core_evidence_summary",
    "supersedes_idno",
    "current_plan_status",
    "download_scope",
    "raw_package_status",
    "next_manual_action",
    "post_download_commands",
    "handoff_readme",
]

REQUIREMENT_COLUMNS = [
    "download_priority_order",
    "queue_role",
    "country",
    "wave",
    "idno",
    "requirement",
    "metadata_status",
    "metadata_evidence_excerpt",
    "promotion_gate_status",
    "raw_review_action",
]

SUMMARY_COLUMNS = ["metric", "value", "interpretation"]

POST_DOWNLOAD_COMMANDS = [
    "python script/17_audit_raw_downloads.py",
    "python script/128_build_priority_archive_member_preflight.py",
    "python script/130_build_priority_raw_package_receipt_ledger.py",
    "python script/03_inspect_raw_schemas.py",
    "python script/29_build_raw_variable_verification_protocol.py",
    "python script/33_build_harmonization_recipe_gate.py",
    "python script/126_build_priority_raw_verification_workbook.py",
    "python script/129_build_priority_manual_verification_decision_gate.py",
    "python script/132_build_priority_analysis_dataset_synthesis_blueprint.py",
    "python script/134_build_priority_country_wave_promotion_packets.py",
    "python script/127_enforce_promoted_data_gate.py",
    "python script/36_build_direct_read_audit_bundle.py",
    "python script/14_validate_workspace.py",
]

REQUIREMENTS = [
    ("household_person_keys", ["household ID", "person ID"]),
    ("weights_and_design", ["weights", "strata", "PSU/cluster"]),
    ("consumption_or_income", ["total consumption or income aggregate"]),
    ("oop_health_expenditure", ["OOP health expenditure"]),
    ("health_need_and_access", ["illness/injury/health need", "care-seeking", "reason for not seeking care"]),
    ("survey_timing", ["interview date", "interview month", "interview year"]),
    ("climate_geography", ["GPS or cluster coordinates", "admin1/admin2 geography"]),
    ("missing_codes_units_recall_skip_patterns", []),
]


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


def rel(path: Path) -> str:
    try:
        return str(path.relative_to(PROJECT_ROOT)).replace("\\", "/")
    except ValueError:
        return str(path).replace("\\", "/")


def compact(value: Any, limit: int = 180) -> str:
    text = " ".join(clean(value).split())
    return text if len(text) <= limit else text[: limit - 3] + "..."


def metadata_hit(value: Any) -> bool:
    text = clean(value).lower()
    return bool(text and not text.startswith("not found"))


def health_evidence_quality(requirement: str, evidence: str) -> str:
    text = evidence.lower()
    if requirement not in {"oop_health_expenditure", "health_need_and_access"}:
        return "specific"
    weak_terms = {
        "crop",
        "farm",
        "farmer",
        "cooperative",
        "livestock",
        "deworm",
        "tick",
        "animal",
        "parcel",
        "plot",
        "slaughter",
        "harvest",
        "fertilizer",
        "pesticide",
    }
    health_terms = {
        "health",
        "medical",
        "medicine",
        "doctor",
        "hospital",
        "clinic",
        "patient",
        "facility",
        "consultation",
        "drug",
        "illness",
        "injury",
        "sick",
        "care",
        "treatment",
        "transport",
        "distance",
    }
    has_health = any(term in text for term in health_terms)
    has_weak = any(term in text for term in weak_terms)
    if requirement == "oop_health_expenditure" and ("health expenditure" in text or "medical" in text or "medicine" in text or "hospital" in text or "clinic" in text):
        return "specific" if not has_weak else "weak"
    if has_health and not has_weak:
        return "specific"
    return "weak"


def official_get_microdata_url(url: str) -> str:
    text = clean(url)
    if not text:
        return ""
    if text.endswith("/get-microdata"):
        return text
    match = re.search(r"/catalog/(\d+)", text)
    if match:
        return f"https://microdata.worldbank.org/catalog/{match.group(1)}/get-microdata"
    return text


def raw_folder(idno: str) -> Path:
    return RAW_ROOT / clean(idno)


def raw_folder_rel(idno: str) -> str:
    return rel(raw_folder(idno)) + "/"


def screening_by_id() -> dict[str, dict[str, str]]:
    out: dict[str, dict[str, str]] = {}
    for row in read_csv_dicts(COUNTRY_SCREENING_PATH):
        idno = clean(row.get("idno"))
        if idno and idno not in out:
            out[idno] = row
    return out


def family_from_candidate(candidate: dict[str, str], fallback: str = "") -> str:
    return clean(candidate.get("candidate_family")) or fallback or "unknown"


def requirement_status(screening: dict[str, str], requirement: str, columns: list[str]) -> tuple[str, str, int]:
    if requirement == "missing_codes_units_recall_skip_patterns":
        return (
            "raw_review_required",
            "Public metadata cannot verify missing codes, skip patterns, units, and recall periods; inspect original raw files and documentation.",
            0,
        )
    evidence = [clean(screening.get(column)) for column in columns if metadata_hit(screening.get(column))]
    if evidence:
        evidence_text = compact(" | ".join(evidence), 220)
        if health_evidence_quality(requirement, evidence_text) == "weak":
            return "metadata_weak_or_proxy_raw_review_required", evidence_text, 0
        return "metadata_hit_raw_review_required", evidence_text, 1
    return "not_found_in_public_metadata_raw_review_required", "No public metadata hit; verify directly in original package and questionnaires.", 0


def metadata_requirement_score(screening: dict[str, str]) -> int:
    weights = {
        "household_person_keys": 1,
        "weights_and_design": 1,
        "consumption_or_income": 2,
        "oop_health_expenditure": 2,
        "health_need_and_access": 1,
        "survey_timing": 1,
        "climate_geography": 1,
    }
    score = 0
    for requirement, columns in REQUIREMENTS:
        if requirement == "missing_codes_units_recall_skip_patterns":
            continue
        status, _, hit = requirement_status(screening, requirement, columns)
        if hit and status.startswith("metadata_hit"):
            score += weights.get(requirement, 1)
    return score


def evidence_summary(screening: dict[str, str]) -> str:
    pieces: list[str] = []
    for requirement, columns in REQUIREMENTS:
        if requirement == "missing_codes_units_recall_skip_patterns":
            continue
        status, _, hit = requirement_status(screening, requirement, columns)
        pieces.append(f"{requirement}={'hit' if hit and status.startswith('metadata_hit') else 'missing'}")
    return ";".join(pieces)


def candidate_sort_key(candidate: dict[str, str], screening: dict[str, str]) -> tuple[int, int, int, str]:
    year_match = re.search(r"(\d{4})", clean(candidate.get("wave")) + " " + clean(candidate.get("idno")))
    year = int(year_match.group(1)) if year_match else 0
    return (
        safe_int(candidate.get("feasibility_score")),
        metadata_requirement_score(screening),
        year,
        clean(candidate.get("idno")),
    )


def choose_replacements(
    candidates: list[dict[str, str]],
    screening_lookup: dict[str, dict[str, str]],
) -> tuple[dict[str, dict[str, str]], list[dict[str, str]]]:
    strong = [
        row for row in candidates
        if clean(row.get("candidate_role")) == "replace_current_core_wave"
        and clean(row.get("alignment_priority")) == "strong_lsms_isa_replacement"
        and clean(row.get("current_plan_status")) != "current_plan_wave"
    ]
    by_country: dict[str, list[dict[str, str]]] = {}
    for row in strong:
        by_country.setdefault(clean(row.get("country")), []).append(row)
    primary: dict[str, dict[str, str]] = {}
    backups: list[dict[str, str]] = []
    for country, rows in sorted(by_country.items()):
        ranked = sorted(
            rows,
            key=lambda row: candidate_sort_key(row, screening_lookup.get(clean(row.get("idno")), {})),
            reverse=True,
        )
        if ranked:
            primary[country] = ranked[0]
            backups.extend(ranked[1 : 1 + BACKUP_CANDIDATES_PER_OFF_FAMILY_COUNTRY])
    return primary, backups


def build_refocused_plan(
    wave_plan: list[dict[str, str]],
    alignment_by_id: dict[str, dict[str, str]],
    primary: dict[str, dict[str, str]],
    screening_lookup: dict[str, dict[str, str]],
) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    for row in sorted(wave_plan, key=lambda item: safe_int(item.get("acquisition_batch_rank"), 9999)):
        country = clean(row.get("country"))
        idno = clean(row.get("idno"))
        alignment = alignment_by_id.get(idno, {})
        selected = row.copy()
        status = clean(alignment.get("lsms_isa_alignment_status"))
        supersedes_idno = ""
        supersedes_name = ""
        replacement_reason = "Current campaign row retained."
        refocused_status = "selected_current_aligned_or_backup"
        if status.startswith("off_family") and country in primary:
            replacement = primary[country]
            supersedes_idno = idno
            supersedes_name = clean(row.get("survey_name"))
            selected = {
                "acquisition_batch_rank": clean(row.get("acquisition_batch_rank")),
                "batch_role": clean(row.get("batch_role")),
                "country": clean(replacement.get("country")),
                "wave": clean(replacement.get("wave")),
                "idno": clean(replacement.get("idno")),
                "survey_name": clean(replacement.get("survey_name")),
                "official_url": clean(replacement.get("official_url")),
            }
            refocused_status = "selected_replacement_for_off_family_core_wave"
            replacement_reason = (
                f"Replaces {supersedes_idno} because the current core wave is {clean(alignment.get('current_survey_family'))}; "
                f"replacement is {clean(replacement.get('candidate_family'))}."
            )
        selected_idno = clean(selected.get("idno"))
        screening = screening_lookup.get(selected_idno, {})
        family = clean(alignment.get("current_survey_family"))
        if selected_idno != idno:
            family = family_from_candidate(primary.get(country, {}), "")
        rows.append(
            {
                "refocused_rank": clean(row.get("acquisition_batch_rank")),
                "original_acquisition_batch_rank": clean(row.get("acquisition_batch_rank")),
                "batch_role": clean(selected.get("batch_role")),
                "country": clean(selected.get("country")),
                "wave": clean(selected.get("wave")),
                "idno": selected_idno,
                "survey_name": clean(selected.get("survey_name")),
                "official_url": official_get_microdata_url(clean(selected.get("official_url"))),
                "local_target_folder": raw_folder_rel(selected_idno),
                "current_survey_family": family,
                "refocused_selection_status": refocused_status,
                "supersedes_idno": supersedes_idno,
                "supersedes_survey_name": supersedes_name,
                "replacement_reason": replacement_reason,
                "metadata_feasibility_score": clean(screening.get("feasibility score from 0 to 5")),
                "metadata_requirement_score": str(metadata_requirement_score(screening)),
                "download_scope": "complete_official_raw_package_plus_all_documentation",
                "raw_package_status": "not_received_no_original_raw_package",
                "promotion_stop_rule": "Do not write into data/ until original package receipt, raw schema inspection, manual value/unit/key review, outcome readiness, and accepted CHIRPS/ERA5 linkage pass.",
            }
        )
    return rows


def queue_row_from_plan(row: dict[str, str]) -> dict[str, str]:
    if clean(row.get("refocused_selection_status")) == "selected_replacement_for_off_family_core_wave":
        role = "core_replacement_primary"
    elif clean(row.get("batch_role")) == "priority_10_wave_batch":
        role = "core_selected_lsms_isa_aligned"
    else:
        role = "sixth_country_backup_candidate"
    return {
        "download_priority_order": clean(row.get("refocused_rank")),
        "queue_role": role,
        "country": clean(row.get("country")),
        "wave": clean(row.get("wave")),
        "idno": clean(row.get("idno")),
        "survey_name": clean(row.get("survey_name")),
        "official_get_microdata_url": clean(row.get("official_url")),
        "local_target_folder": clean(row.get("local_target_folder")),
        "candidate_family": clean(row.get("current_survey_family")),
        "alignment_priority": "selected_refocused_core_or_backup",
        "metadata_feasibility_score": clean(row.get("metadata_feasibility_score")),
        "metadata_requirement_score": clean(row.get("metadata_requirement_score")),
        "metadata_core_evidence_summary": "",
        "supersedes_idno": clean(row.get("supersedes_idno")),
        "current_plan_status": "selected_in_refocused_plan",
        "download_scope": clean(row.get("download_scope")),
        "raw_package_status": clean(row.get("raw_package_status")),
        "next_manual_action": "Download the complete unchanged official package and all documentation through the official credentialed route.",
        "post_download_commands": "; ".join(POST_DOWNLOAD_COMMANDS),
        "handoff_readme": "",
    }


def queue_row_from_backup(candidate: dict[str, str], order: int, screening: dict[str, str]) -> dict[str, str]:
    idno = clean(candidate.get("idno"))
    return {
        "download_priority_order": str(order),
        "queue_role": "replacement_backup_wave",
        "country": clean(candidate.get("country")),
        "wave": clean(candidate.get("wave")),
        "idno": idno,
        "survey_name": clean(candidate.get("survey_name")),
        "official_get_microdata_url": official_get_microdata_url(clean(candidate.get("official_url"))),
        "local_target_folder": raw_folder_rel(idno),
        "candidate_family": clean(candidate.get("candidate_family")),
        "alignment_priority": clean(candidate.get("alignment_priority")),
        "metadata_feasibility_score": clean(candidate.get("feasibility_score")),
        "metadata_requirement_score": str(metadata_requirement_score(screening)),
        "metadata_core_evidence_summary": "",
        "supersedes_idno": "",
        "current_plan_status": "backup_not_selected_in_refocused_13_wave_plan",
        "download_scope": "complete_official_raw_package_plus_all_documentation_if_primary_replacement_fails_manual_review",
        "raw_package_status": "not_received_no_original_raw_package",
        "next_manual_action": "Keep as a credentialed backup if the primary replacement fails consumption, OOP, access, timing, or geography verification.",
        "post_download_commands": "; ".join(POST_DOWNLOAD_COMMANDS),
        "handoff_readme": "",
    }


def write_handoff(queue_row: dict[str, str], requirement_rows: list[dict[str, str]]) -> str:
    folder = raw_folder(queue_row.get("idno", ""))
    folder.mkdir(parents=True, exist_ok=True)
    path = folder / "_PRIORITY_LSMS_ISA_REFOCUSED_ACQUISITION.md"
    req_table = markdown_table(requirement_rows, ["requirement", "metadata_status", "promotion_gate_status"], 12)
    path.write_text(
        f"""# Priority LSMS-ISA Refocused Acquisition

Dataset: `{queue_row.get('idno', '')}` - {queue_row.get('country', '')} {queue_row.get('wave', '')}

Queue role: `{queue_row.get('queue_role', '')}`

Official get-microdata URL: {queue_row.get('official_get_microdata_url', '')}

Target folder: `{queue_row.get('local_target_folder', '')}`

Current raw status: `{queue_row.get('raw_package_status', '')}`

## Manual Download Scope

Download the complete unchanged official raw package plus all documentation.
Do not download only selected modules, and do not write anything into `data/`
until the promotion gates pass.

## Requirement Gate Snapshot

{req_table}

## Post-Download Commands

{chr(10).join(f'- `{command}`' for command in POST_DOWNLOAD_COMMANDS)}

## Stop Rule

Models remain blocked. This wave cannot enter the promoted registry until raw
receipt, schema inspection, value/unit/key review, outcome review, and
CHIRPS/ERA5 climate-linkage review all pass.
""",
        encoding="utf-8",
    )
    return rel(path)


def build_requirement_rows(queue_rows: list[dict[str, str]], screening_lookup: dict[str, dict[str, str]]) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    for queue_row in queue_rows:
        screening = screening_lookup.get(clean(queue_row.get("idno")), {})
        for requirement, columns in REQUIREMENTS:
            status, evidence, hit = requirement_status(screening, requirement, columns)
            rows.append(
                {
                    "download_priority_order": clean(queue_row.get("download_priority_order")),
                    "queue_role": clean(queue_row.get("queue_role")),
                    "country": clean(queue_row.get("country")),
                    "wave": clean(queue_row.get("wave")),
                    "idno": clean(queue_row.get("idno")),
                    "requirement": requirement,
                    "metadata_status": status,
                    "metadata_evidence_excerpt": evidence,
                    "promotion_gate_status": "blocked_pending_raw_review",
                    "raw_review_action": "Verify this requirement directly in the original raw package, questionnaires, codebooks, and value labels.",
                }
            )
    return rows


def build_queue(
    plan_rows: list[dict[str, str]],
    backups: list[dict[str, str]],
    screening_lookup: dict[str, dict[str, str]],
) -> tuple[list[dict[str, str]], list[dict[str, str]]]:
    queue_rows = [queue_row_from_plan(row) for row in plan_rows]
    next_order = len(queue_rows) + 1
    for candidate in backups:
        screening = screening_lookup.get(clean(candidate.get("idno")), {})
        queue_rows.append(queue_row_from_backup(candidate, next_order, screening))
        next_order += 1
    for row in queue_rows:
        screening = screening_lookup.get(clean(row.get("idno")), {})
        row["metadata_core_evidence_summary"] = evidence_summary(screening)
    requirement_rows = build_requirement_rows(queue_rows, screening_lookup)
    by_id: dict[str, list[dict[str, str]]] = {}
    for req in requirement_rows:
        by_id.setdefault(clean(req.get("idno")), []).append(req)
    for row in queue_rows:
        row["handoff_readme"] = write_handoff(row, by_id.get(clean(row.get("idno")), []))
    return queue_rows, requirement_rows


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


def build_summary(plan_rows: list[dict[str, str]], queue_rows: list[dict[str, str]], requirement_rows: list[dict[str, str]]) -> list[dict[str, str]]:
    core_rows = [row for row in plan_rows if row["batch_role"] == "priority_10_wave_batch"]
    role_counts = Counter(row["queue_role"] for row in queue_rows)
    requirement_counts = Counter(row["metadata_status"] for row in requirement_rows)
    selected_lsms_core = sum(1 for row in core_rows if clean(row.get("current_survey_family")).startswith("lsms_"))
    rows = [
        {"metric": "priority_lsms_refocused_wave_plan_rows", "value": str(len(plan_rows)), "interpretation": "Refocused selected wave-plan rows after replacing off-family core waves."},
        {"metric": "priority_lsms_refocused_core_wave_rows", "value": str(len(core_rows)), "interpretation": "Core priority wave rows in the refocused plan."},
        {"metric": "priority_lsms_refocused_core_required_countries", "value": str(len({row["country"] for row in core_rows if row["country"] in REQUIRED_PRIORITY_COUNTRIES})), "interpretation": "Required LSMS/ISA priority countries represented in the refocused core."},
        {"metric": "priority_lsms_refocused_core_lsms_aligned_rows", "value": str(selected_lsms_core), "interpretation": "Core rows in the refocused plan with LSMS/ISA or LSMS-style family alignment."},
        {"metric": "priority_lsms_refocused_replaced_off_family_core_rows", "value": str(sum(1 for row in plan_rows if row["refocused_selection_status"] == "selected_replacement_for_off_family_core_wave")), "interpretation": "Off-family current core rows replaced in the refocused plan."},
        {"metric": "priority_lsms_refocused_acquisition_queue_rows", "value": str(len(queue_rows)), "interpretation": "Selected and backup rows in the refocused manual acquisition queue."},
        {"metric": "priority_lsms_refocused_replacement_backup_rows", "value": str(role_counts.get("replacement_backup_wave", 0)), "interpretation": "Extra Malawi/Uganda LSMS/ISA backup waves queued if primary replacements fail manual review."},
        {"metric": "priority_lsms_refocused_requirement_rows", "value": str(len(requirement_rows)), "interpretation": "Requirement rows for selected and backup acquisition targets."},
        {"metric": "priority_lsms_refocused_requirement_metadata_hit_rows", "value": str(requirement_counts.get("metadata_hit_raw_review_required", 0)), "interpretation": "Requirement rows with public metadata evidence, still requiring raw review."},
        {"metric": "priority_lsms_refocused_requirement_weak_or_proxy_rows", "value": str(requirement_counts.get("metadata_weak_or_proxy_raw_review_required", 0)), "interpretation": "Requirement rows where public metadata may be a weak proxy or false positive and must be resolved from raw documentation."},
        {"metric": "priority_lsms_refocused_requirement_missing_or_raw_only_rows", "value": str(requirement_counts.get("not_found_in_public_metadata_raw_review_required", 0) + requirement_counts.get("raw_review_required", 0) + requirement_counts.get("metadata_weak_or_proxy_raw_review_required", 0)), "interpretation": "Requirement rows requiring raw package or documentation review because public metadata is missing, weak, or insufficient."},
        {"metric": "priority_lsms_refocused_raw_package_received_rows", "value": "0", "interpretation": "Refocused targets with original raw package receipt; still zero."},
        {"metric": "priority_lsms_refocused_handoff_readmes_written", "value": str(sum(1 for row in queue_rows if row.get("handoff_readme"))), "interpretation": "Per-wave refocused acquisition handoff files written."},
        {"metric": "priority_lsms_refocused_data_write_status", "value": "blocked_no_promoted_rows", "interpretation": "No refocused wave may write to data/ before all raw and climate gates pass."},
        {"metric": "modeling_gate_status", "value": "blocked", "interpretation": "Models remain blocked until raw-backed promotion thresholds and accepted climate linkage pass."},
    ]
    for role, count in sorted(role_counts.items()):
        rows.append({"metric": f"priority_lsms_refocused_queue_role_{role}", "value": str(count), "interpretation": "Refocused acquisition queue role count."})
    return rows


def write_report(plan_rows: list[dict[str, str]], queue_rows: list[dict[str, str]], requirement_rows: list[dict[str, str]], summary_rows: list[dict[str, str]]) -> None:
    replacements = [row for row in plan_rows if row["refocused_selection_status"] == "selected_replacement_for_off_family_core_wave"]
    backups = [row for row in queue_rows if row["queue_role"] == "replacement_backup_wave"]
    missing_requirements = [
        row for row in requirement_rows
        if row["metadata_status"] != "metadata_hit_raw_review_required"
        and row["requirement"] in {"consumption_or_income", "oop_health_expenditure", "survey_timing", "climate_geography"}
    ]
    summary_table = "\n".join(f"| {row['metric']} | {row['value']} | {row['interpretation']} |" for row in summary_rows)
    REPORT_PATH.write_text(
        f"""# Priority LSMS-ISA Refocused Acquisition Queue

Status: actionable metadata-only acquisition queue. This queue is the next
manual-download target list after the LSMS/ISA alignment audit found that
Malawi MTM and Uganda SAGE should not anchor the five-country core sample.

## Bottom Line

- The refocused 10-wave core keeps Ethiopia, Nigeria, and Tanzania as selected.
- Malawi MTM is replaced by the highest-scoring Malawi IHS/IHPS candidate.
- Uganda SAGE is replaced by the highest-scoring Uganda UNPS candidate.
- Extra Malawi/Uganda backup waves are queued in case primary replacements fail
  raw consumption, OOP, access, timing, or geography review.
- No raw packages are present and no data were promoted.

## Summary

| Metric | Value | Interpretation |
|---|---:|---|
{summary_table}

## Replacements

{markdown_table(replacements, ['refocused_rank', 'country', 'wave', 'idno', 'supersedes_idno', 'current_survey_family', 'metadata_feasibility_score', 'metadata_requirement_score'], 10)}

## Refocused Download Queue

{markdown_table(queue_rows, ['download_priority_order', 'queue_role', 'country', 'wave', 'idno', 'metadata_feasibility_score', 'metadata_requirement_score', 'official_get_microdata_url'], 25)}

## Replacement Backups

{markdown_table(backups, ['download_priority_order', 'country', 'wave', 'idno', 'metadata_feasibility_score', 'metadata_requirement_score', 'official_get_microdata_url'], 12) if backups else 'No replacement backup rows were added.'}

## High-Value Metadata Gaps To Check In Raw Packages

{markdown_table(missing_requirements, ['download_priority_order', 'country', 'idno', 'requirement', 'metadata_status', 'raw_review_action'], 30) if missing_requirements else 'No high-value metadata gaps were detected.'}

## Machine-Readable Outputs

- `result/priority_lsms_isa_refocused_wave_plan.csv`
- `temp/priority_lsms_isa_refocused_acquisition_queue.csv`
- `temp/priority_lsms_isa_refocused_requirement_matrix.csv`
- `result/priority_lsms_isa_refocused_acquisition_summary.csv`

## Guardrail

This queue replaces the off-family core download path but does not promote any
country-wave. Complete official raw packages, documentation, raw value review,
outcome review, and CHIRPS/ERA5 linkage review are still required before
anything can be written into `data/`.
""",
        encoding="utf-8",
    )


def main() -> None:
    ensure_dirs()
    wave_plan = read_csv_dicts(WAVE_PLAN_PATH)
    alignment_by_id = {clean(row.get("idno")): row for row in read_csv_dicts(ALIGNMENT_AUDIT_PATH)}
    candidates = read_csv_dicts(REPLACEMENT_CANDIDATES_PATH)
    screening_lookup = screening_by_id()
    primary, backups = choose_replacements(candidates, screening_lookup)
    plan_rows = build_refocused_plan(wave_plan, alignment_by_id, primary, screening_lookup)
    queue_rows, requirement_rows = build_queue(plan_rows, backups, screening_lookup)
    summary_rows = build_summary(plan_rows, queue_rows, requirement_rows)
    write_csv(REFOCUSED_PLAN_PATH, plan_rows, PLAN_COLUMNS)
    write_csv(QUEUE_PATH, queue_rows, QUEUE_COLUMNS)
    write_csv(REQUIREMENT_MATRIX_PATH, requirement_rows, REQUIREMENT_COLUMNS)
    write_csv(SUMMARY_PATH, summary_rows, SUMMARY_COLUMNS)
    write_report(plan_rows, queue_rows, requirement_rows, summary_rows)
    append_log(
        TEMP_DIR / "audit_log.md",
        f"Built priority LSMS-ISA refocused acquisition queue plan_rows={len(plan_rows)} queue_rows={len(queue_rows)} requirement_rows={len(requirement_rows)}.",
    )
    print(f"Priority LSMS-ISA refocused acquisition queue rows={len(queue_rows)} requirement_rows={len(requirement_rows)}.")


if __name__ == "__main__":
    main()
