from __future__ import annotations

import csv
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

from common import PROJECT_ROOT, REPORT_DIR, RESULT_DIR, TEMP_DIR, append_log, ensure_dirs, write_csv


QUEUE_PATH = TEMP_DIR / "priority_lsms_isa_refocused_acquisition_queue.csv"
PUBLIC_DOC_DATASET_PATH = TEMP_DIR / "priority_lsms_isa_public_documentation_dataset_receipt.csv"
PUBLIC_DOC_RESOURCE_PATH = TEMP_DIR / "priority_lsms_isa_public_documentation_receipt.csv"
VARIABLE_COVERAGE_PATH = TEMP_DIR / "priority_lsms_isa_requirement_variable_coverage.csv"
VARIABLE_MATRIX_PATH = TEMP_DIR / "priority_lsms_isa_variable_evidence_matrix.csv"
FILE_SHORTLIST_PATH = TEMP_DIR / "priority_lsms_isa_concept_file_shortlist.csv"
RAW_INTAKE_LEDGER_PATH = TEMP_DIR / "priority_lsms_isa_raw_package_intake_ledger.csv"
ARCHIVE_PREFLIGHT_PATH = TEMP_DIR / "priority_lsms_isa_archive_member_preflight.csv"
ARCHIVE_REQUIREMENT_PATH = TEMP_DIR / "priority_lsms_isa_archive_requirement_preflight.csv"
CLIMATE_PREFLIGHT_PATH = TEMP_DIR / "priority_climate_linkage_preflight.csv"
SYNTHESIS_JOIN_PATH = TEMP_DIR / "priority_analysis_dataset_join_plan.csv"
REGISTRY_PATH = RESULT_DIR / "promoted_country_wave_registry.csv"
MWI2004_ACCEPTANCE_DECISION_PATH = RESULT_DIR / "mwi2004_requirement_acceptance_decisions.csv"
MWI2004_CHIRPS_ROUTE_SUMMARY_PATH = RESULT_DIR / "mwi2004_chirps_admin2_route_policy_summary.csv"

PACKET_DIR = REPORT_DIR / "priority_lsms_isa_country_wave_promotion_packets"
INDEX_PATH = TEMP_DIR / "priority_lsms_isa_country_wave_promotion_packet_index.csv"
GATE_MATRIX_PATH = TEMP_DIR / "priority_lsms_isa_country_wave_promotion_packet_gate_matrix.csv"
ACTION_QUEUE_PATH = TEMP_DIR / "priority_lsms_isa_country_wave_promotion_packet_action_queue.csv"
SUMMARY_PATH = RESULT_DIR / "priority_lsms_isa_country_wave_promotion_packet_summary.csv"
REPORT_PATH = REPORT_DIR / "priority_lsms_isa_country_wave_promotion_packets.md"

REQUIREMENTS = [
    "household_person_keys",
    "weights_and_design",
    "consumption_or_income",
    "oop_health_expenditure",
    "health_need_and_access",
    "survey_timing",
    "climate_geography",
    "missing_codes_units_recall_skip_patterns",
]

INDEX_COLUMNS = [
    "download_priority_order",
    "queue_role",
    "country",
    "wave",
    "idno",
    "survey_name",
    "official_get_microdata_url",
    "local_target_folder",
    "public_documentation_status",
    "variable_evidence_status",
    "raw_package_status",
    "archive_preflight_status",
    "raw_value_verification_status",
    "financial_protection_status",
    "access_forgone_care_status",
    "climate_linkage_status",
    "analysis_synthesis_status",
    "promoted_registry_status",
    "packet_status",
    "failed_gate_count",
    "next_blocking_action",
    "packet_report",
    "raw_folder_handoff",
]

GATE_COLUMNS = [
    "download_priority_order",
    "queue_role",
    "country",
    "wave",
    "idno",
    "gate",
    "status",
    "evidence",
    "required_action",
]

ACTION_COLUMNS = [
    "action_rank",
    "download_priority_order",
    "queue_role",
    "country",
    "wave",
    "idno",
    "blocking_stage",
    "required_action",
    "local_target_folder",
    "official_url",
    "packet_report",
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


def csv_value(rows: list[dict[str, str]], metric: str, default: str = "") -> str:
    for row in rows:
        if clean(row.get("metric")) == metric:
            return clean(row.get("value")) or default
    return default


def rel(path: Path) -> str:
    try:
        return str(path.relative_to(PROJECT_ROOT)).replace("\\", "/")
    except ValueError:
        return str(path).replace("\\", "/")


def shorten(value: Any, limit: int = 180) -> str:
    text = " ".join(clean(value).split())
    if len(text) <= limit:
        return text
    return text[: limit - 3] + "..."


def by_id(rows: list[dict[str, str]], field: str = "idno") -> dict[str, list[dict[str, str]]]:
    out: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in rows:
        idno = clean(row.get(field))
        if idno:
            out[idno].append(row)
    return out


def one_by_id(rows: list[dict[str, str]], field: str = "idno") -> dict[str, dict[str, str]]:
    out: dict[str, dict[str, str]] = {}
    for row in rows:
        idno = clean(row.get(field))
        if idno and idno not in out:
            out[idno] = row
    return out


def compact(values: list[str], limit: int = 8) -> str:
    out: list[str] = []
    seen: set[str] = set()
    for value in values:
        item = shorten(value, 80)
        if item and item not in seen:
            out.append(item)
            seen.add(item)
        if len(out) >= limit:
            break
    return "; ".join(out)


def raw_folder_path(folder: str, idno: str) -> Path:
    folder_clean = clean(folder).replace("\\", "/").strip("/")
    if folder_clean:
        return PROJECT_ROOT / folder_clean
    return TEMP_DIR / "raw_downloads" / idno


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


def add_gate(
    rows: list[dict[str, str]],
    wave: dict[str, str],
    gate: str,
    passed: bool,
    evidence: str,
    required_action: str,
) -> None:
    rows.append(
        {
            "download_priority_order": clean(wave.get("download_priority_order")),
            "queue_role": clean(wave.get("queue_role")),
            "country": clean(wave.get("country")),
            "wave": clean(wave.get("wave")),
            "idno": clean(wave.get("idno")),
            "gate": gate,
            "status": "pass" if passed else "fail",
            "evidence": shorten(evidence, 260),
            "required_action": "" if passed else required_action,
        }
    )


def public_doc_ready(row: dict[str, str]) -> bool:
    status = clean(row.get("public_documentation_receipt_status"))
    return status.startswith("complete_") and not clean(row.get("missing_core_resource_types"))


def variable_evidence_ready(coverage_rows: list[dict[str, str]]) -> bool:
    if len(coverage_rows) < len(REQUIREMENTS):
        return False
    no_candidate = [row for row in coverage_rows if "no_candidate" in clean(row.get("coverage_status"))]
    candidate_rows = sum(safe_int(row.get("candidate_variable_rows")) for row in coverage_rows)
    return not no_candidate and candidate_rows > 0


def archive_ready(row: dict[str, str]) -> bool:
    return clean(row.get("archive_preflight_status")) == "ready_for_raw_receipt_schema_and_manual_review"


def raw_package_ready(intake: dict[str, str], public: dict[str, str], archive: dict[str, str]) -> bool:
    has_original_package = safe_int(intake.get("original_file_count")) > 0
    has_raw_container = safe_int(intake.get("archive_file_count")) > 0 or safe_int(intake.get("raw_tabular_file_count")) > 0
    has_public_docs = public_doc_ready(public)
    has_package_docs = safe_int(intake.get("documentation_file_count")) > 0 or safe_int(archive.get("archive_documentation_member_rows")) > 0
    return has_original_package and has_raw_container and archive_ready(archive) and (has_package_docs or has_public_docs)


def focused_requirement_verified(decision: dict[str, str]) -> bool:
    final_decision = clean(decision.get("final_verification_decision")).lower()
    return final_decision.startswith("raw_value_verified") or final_decision in {
        "final_verified",
        "manual_raw_value_verified",
        "verified_raw_value",
    }


def requirement_verified(
    coverage_rows: list[dict[str, str]],
    requirement: str,
    focused_decision: dict[str, str] | None = None,
) -> bool:
    if focused_decision and focused_requirement_verified(focused_decision):
        return True
    for row in coverage_rows:
        if clean(row.get("requirement")) == requirement:
            return clean(row.get("raw_value_verification_status")) in {
                "raw_value_verified",
                "verified_raw_value",
                "manual_raw_value_verified",
            }
    return False


def climate_ready(row: dict[str, str]) -> bool:
    return clean(row.get("accepted_chirps_era5_route_status")).startswith("accepted")


def synthesis_ready(row: dict[str, str]) -> bool:
    return clean(row.get("join_plan_status")) == "ready_for_promoted_dataset_build"


def registry_ready(row: dict[str, str]) -> bool:
    return clean(row.get("analysis_ready_status")) == "promoted_analysis_ready" and safe_int(row.get("rows")) > 0


def write_raw_handoff(wave: dict[str, str], packet_path: str, failed_count: int) -> str:
    folder = raw_folder_path(wave.get("local_target_folder", ""), wave.get("idno", ""))
    folder.mkdir(parents=True, exist_ok=True)
    path = folder / "_PRIORITY_LSMS_ISA_COUNTRY_WAVE_PROMOTION_PACKET.md"
    path.write_text(
        f"""# Priority LSMS-ISA Country-Wave Promotion Packet

Dataset: `{wave.get('idno', '')}` - {wave.get('country', '')} {wave.get('wave', '')}

Packet report: `{packet_path}`

Current status: blocked from `data/` promotion.

Failed gates: {failed_count}

Next required action: place the complete unchanged official raw package and
all documentation in this folder, then rerun the LSMS/ISA raw intake, archive
preflight, raw value verification, climate linkage, synthesis, registry, and
validation gates.
""",
        encoding="utf-8",
    )
    return rel(path)


def write_packet(
    wave: dict[str, str],
    index_row: dict[str, str],
    gates: list[dict[str, str]],
    public_resources: list[dict[str, str]],
    coverage_rows: list[dict[str, str]],
    shortlist_rows: list[dict[str, str]],
    variable_rows: list[dict[str, str]],
    archive_req_rows: list[dict[str, str]],
    acceptance_rows: list[dict[str, str]],
) -> str:
    PACKET_DIR.mkdir(parents=True, exist_ok=True)
    path = PACKET_DIR / f"{wave['idno']}.md"
    failed = [row for row in gates if row["status"] != "pass"]
    resources = [
        {
            "resource_type": row.get("resource_type", ""),
            "receipt_status": row.get("receipt_status", ""),
            "saved_path": row.get("saved_path", ""),
        }
        for row in public_resources[:12]
    ]
    coverage_preview = [
        {
            "requirement": row.get("requirement", ""),
            "coverage_status": row.get("coverage_status", ""),
            "candidate_variable_rows": row.get("candidate_variable_rows", ""),
            "strong_candidate_variable_rows": row.get("strong_candidate_variable_rows", ""),
            "raw_value_verification_status": row.get("raw_value_verification_status", ""),
        }
        for row in coverage_rows
    ]
    shortlist_preview = [
        {
            "requirement": row.get("requirement", ""),
            "file_name": row.get("file_name", ""),
            "candidate_variable_rows": row.get("candidate_variable_rows", ""),
            "top_variable_names": row.get("top_variable_names", ""),
        }
        for row in shortlist_rows[:16]
    ]
    variable_preview = [
        {
            "requirement": row.get("requirement", ""),
            "variable_name": row.get("variable_name", ""),
            "variable_label": row.get("variable_label", ""),
            "file_name": row.get("file_name", ""),
            "match_score": row.get("match_score", ""),
        }
        for row in variable_rows[:16]
    ]
    archive_preview = [
        {
            "requirement": row.get("requirement", ""),
            "metadata_status": row.get("metadata_status", ""),
            "requirement_preflight_status": row.get("requirement_preflight_status", ""),
        }
        for row in archive_req_rows[:12]
    ]
    acceptance_preview = [
        {
            "requirement": row.get("requirement", ""),
            "mechanical_raw_check_decision": row.get("mechanical_raw_check_decision", ""),
            "final_verification_decision": row.get("final_verification_decision", ""),
            "remaining_blocker": row.get("remaining_blocker", ""),
        }
        for row in acceptance_rows
    ]
    acceptance_section = ""
    if acceptance_preview:
        acceptance_section = f"""

## Focused Raw Acceptance Decisions

{markdown_table(acceptance_preview, ['requirement', 'mechanical_raw_check_decision', 'final_verification_decision', 'remaining_blocker'], 12)}
"""
    path.write_text(
        f"""# Priority LSMS-ISA Country-Wave Promotion Packet

Dataset: `{wave.get('idno', '')}` - {wave.get('country', '')} {wave.get('wave', '')}

Survey: {wave.get('survey_name', '')}

Official get-microdata URL: {wave.get('official_get_microdata_url', '')}

Target raw folder: `{wave.get('local_target_folder', '')}`

Current packet status: `{index_row.get('packet_status', '')}`

Analysis-ready status: `{index_row.get('promoted_registry_status', '')}`

Next blocking action: `{index_row.get('next_blocking_action', '')}`

## Gate Matrix

{markdown_table(gates, ['gate', 'status', 'evidence', 'required_action'], 30)}

## Requirement Variable Evidence

{markdown_table(coverage_preview, ['requirement', 'coverage_status', 'candidate_variable_rows', 'strong_candidate_variable_rows', 'raw_value_verification_status'], 12)}

## Official Public Documentation

{markdown_table(resources, ['resource_type', 'receipt_status', 'saved_path'], 12)}

## Concept File Shortlist

{markdown_table(shortlist_preview, ['requirement', 'file_name', 'candidate_variable_rows', 'top_variable_names'], 16)}

## Candidate Variable Preview

{markdown_table(variable_preview, ['requirement', 'variable_name', 'variable_label', 'file_name', 'match_score'], 16)}

## Archive/Direct-File Requirement Preflight

{markdown_table(archive_preview, ['requirement', 'metadata_status', 'requirement_preflight_status'], 12)}{acceptance_section}

## Stop Rule

This packet is a promotion-control artifact, not an analysis dataset. Do not
write this country-wave into `data/` until the complete original raw package,
all raw value/key/unit/skip-pattern checks, outcome gates, and an accepted
CHIRPS or ERA5 linkage route pass.

Failed gates currently blocking promotion: {len(failed)}.
""",
        encoding="utf-8",
    )
    return rel(path)


def build_outputs() -> tuple[list[dict[str, str]], list[dict[str, str]], list[dict[str, str]], list[dict[str, str]]]:
    queue_rows = read_csv_dicts(QUEUE_PATH)
    public_by_id = one_by_id(read_csv_dicts(PUBLIC_DOC_DATASET_PATH))
    public_resources_by_id = by_id(read_csv_dicts(PUBLIC_DOC_RESOURCE_PATH))
    coverage_by_id = by_id(read_csv_dicts(VARIABLE_COVERAGE_PATH))
    matrix_by_id = by_id(read_csv_dicts(VARIABLE_MATRIX_PATH))
    shortlist_by_id = by_id(read_csv_dicts(FILE_SHORTLIST_PATH))
    intake_by_id = one_by_id(read_csv_dicts(RAW_INTAKE_LEDGER_PATH))
    archive_by_id = one_by_id(read_csv_dicts(ARCHIVE_PREFLIGHT_PATH))
    archive_req_by_id = by_id(read_csv_dicts(ARCHIVE_REQUIREMENT_PATH))
    climate_by_id = one_by_id(read_csv_dicts(CLIMATE_PREFLIGHT_PATH))
    synthesis_by_id = one_by_id(read_csv_dicts(SYNTHESIS_JOIN_PATH))
    registry_by_id = one_by_id(read_csv_dicts(REGISTRY_PATH))
    acceptance_by_id = by_id(read_csv_dicts(MWI2004_ACCEPTANCE_DECISION_PATH))
    mwi2004_route_summary = read_csv_dicts(MWI2004_CHIRPS_ROUTE_SUMMARY_PATH)
    mwi2004_route_design_ready = csv_value(mwi2004_route_summary, "route_design_ready", "0") == "1"
    mwi2004_route_gate = csv_value(
        mwi2004_route_summary,
        "current_climate_linkage_gate_status",
        "route_preflight_ready_needs_extraction_validation",
    )

    index_rows: list[dict[str, str]] = []
    gate_rows: list[dict[str, str]] = []
    action_rows: list[dict[str, str]] = []

    for wave in queue_rows:
        idno = clean(wave.get("idno"))
        public = public_by_id.get(idno, {})
        coverage_rows = coverage_by_id.get(idno, [])
        matrix_rows = matrix_by_id.get(idno, [])
        shortlist_rows = shortlist_by_id.get(idno, [])
        intake = intake_by_id.get(idno, {})
        archive = archive_by_id.get(idno, {})
        acceptance_rows = acceptance_by_id.get(idno, [])
        acceptance_by_requirement = {
            clean(row.get("requirement")): row for row in acceptance_rows if clean(row.get("requirement"))
        }
        climate = climate_by_id.get(idno, {})
        if idno == "MWI_2004_IHS-II_v01_M" and mwi2004_route_design_ready:
            climate = {
                "accepted_chirps_era5_route_status": "not_accepted_extraction_and_validation_pending",
                "current_climate_linkage_gate_status": mwi2004_route_gate,
                "planned_geography_level": "district_adm2_month_chirps",
            }
        synthesis = synthesis_by_id.get(idno, {})
        registry = registry_by_id.get(idno, {})

        gates: list[dict[str, str]] = []
        public_ready = public_doc_ready(public)
        variable_ready = variable_evidence_ready(coverage_rows)
        raw_ready = raw_package_ready(intake, public, archive)
        archive_ok = archive_ready(archive)
        raw_verified_count = sum(
            1
            for requirement in REQUIREMENTS
            if requirement_verified(coverage_rows, requirement, acceptance_by_requirement.get(requirement))
        )
        all_requirements_verified = len(coverage_rows) >= len(REQUIREMENTS) and all(
            requirement_verified(coverage_rows, requirement, acceptance_by_requirement.get(requirement))
            for requirement in REQUIREMENTS
        )
        financial_ready = all(
            requirement_verified(coverage_rows, requirement, acceptance_by_requirement.get(requirement))
            for requirement in ["weights_and_design", "consumption_or_income", "oop_health_expenditure"]
        )
        access_ready = requirement_verified(
            coverage_rows,
            "health_need_and_access",
            acceptance_by_requirement.get("health_need_and_access"),
        )
        timing_geo_ready = all(
            requirement_verified(coverage_rows, requirement, acceptance_by_requirement.get(requirement))
            for requirement in ["survey_timing", "climate_geography"]
        )
        climate_ok = climate_ready(climate)
        synthesis_ok = synthesis_ready(synthesis)
        registry_ok = registry_ready(registry)

        add_gate(
            gates,
            wave,
            "official_public_documentation_receipt",
            public_ready,
            f"status={public.get('public_documentation_receipt_status', '')}; saved={public.get('saved_resource_types', '')}; missing_core={public.get('missing_core_resource_types', '')}",
            "Run the LSMS/ISA public documentation receipt and save all core public metadata/documentation resources.",
        )
        add_gate(
            gates,
            wave,
            "official_variable_evidence_coverage",
            variable_ready,
            f"coverage_rows={len(coverage_rows)}; matrix_rows={len(matrix_rows)}; shortlist_rows={len(shortlist_rows)}; no_candidate_rows={sum(1 for row in coverage_rows if 'no_candidate' in clean(row.get('coverage_status')))}",
            "Use official DDI/variable metadata to cover every promotion requirement before raw review.",
        )
        add_gate(
            gates,
            wave,
            "complete_original_raw_package",
            raw_ready,
            f"intake_status={intake.get('intake_acceptance_status', 'missing')}; original_files={intake.get('original_file_count', '0')}; archives={intake.get('archive_file_count', '0')}; raw_tabular={intake.get('raw_tabular_file_count', '0')}; package_docs={intake.get('documentation_file_count', '0')}; public_docs={public.get('public_documentation_receipt_status', 'missing')}; archive_status={archive.get('archive_preflight_status', 'missing')}",
            "Download/place the complete unchanged official raw package and all documentation in the target folder.",
        )
        add_gate(
            gates,
            wave,
            "archive_or_direct_file_preflight",
            archive_ok,
            f"status={archive.get('archive_preflight_status', 'missing')}; direct_raw={archive.get('direct_raw_tabular_file_rows', '0')}; direct_docs={archive.get('direct_documentation_file_rows', '0')}; archive_members={archive.get('archive_member_rows', '0')}",
            "Confirm readable archive/direct raw and documentation files before schema inspection.",
        )
        for requirement in REQUIREMENTS:
            row = next((item for item in coverage_rows if clean(item.get("requirement")) == requirement), {})
            decision = acceptance_by_requirement.get(requirement, {})
            focused_evidence = ""
            if decision:
                focused_evidence = (
                    f"; focused_decision={decision.get('mechanical_raw_check_decision', '')}"
                    f"; final={decision.get('final_verification_decision', '')}"
                    f"; blocker={decision.get('remaining_blocker', '')}"
                )
            add_gate(
                gates,
                wave,
                f"raw_value_verification_{requirement}",
                requirement_verified(coverage_rows, requirement, decision),
                f"metadata={row.get('coverage_status', 'missing')}; candidates={row.get('candidate_variable_rows', '0')}; files={row.get('candidate_file_rows', '0')}; raw_status={row.get('raw_value_verification_status', 'missing')}; top_files={row.get('top_file_names', '')}{focused_evidence}",
                decision.get("next_action")
                or "Verify this requirement against raw files, value labels, units, recall periods, skip patterns, and merge level.",
            )
        add_gate(
            gates,
            wave,
            "all_required_raw_values_verified",
            all_requirements_verified,
            f"verified_requirement_rows={raw_verified_count}/{len(coverage_rows)}",
            "Complete raw-backed verification for every required promotion requirement.",
        )
        add_gate(
            gates,
            wave,
            "financial_protection_inputs_ready",
            financial_ready,
            "requires verified weights/design, total consumption or income, and OOP health expenditure.",
            "Verify financial-protection inputs before CHE10/CHE25 or SDG 3.8.2 readiness can be claimed.",
        )
        add_gate(
            gates,
            wave,
            "access_forgone_care_inputs_ready",
            access_ready,
            "requires verified illness/need, care-seeking, and access-barrier raw variables.",
            "Verify illness/need and care-seeking/access variables before double-failure readiness can be claimed.",
        )
        add_gate(
            gates,
            wave,
            "timing_geography_ready_for_climate",
            timing_geo_ready,
            "requires verified survey timing and GPS/cluster/EA/admin geography.",
            "Verify timing and geography raw fields before accepting a climate linkage route.",
        )
        add_gate(
            gates,
            wave,
            "accepted_chirps_or_era5_linkage_route",
            climate_ok,
            f"accepted_route={climate.get('accepted_chirps_era5_route_status', 'missing')}; current_gate={climate.get('current_climate_linkage_gate_status', 'missing')}; planned_level={climate.get('planned_geography_level', '')}",
            "Download/extract CHIRPS ADM2 monthly rasters and validate units, spatial coverage, and lag windows."
            if clean(climate.get("current_climate_linkage_gate_status")) == "route_preflight_ready_needs_extraction_validation"
            else "Accept a CHIRPS or ERA5 route only after timing/geography verification passes.",
        )
        add_gate(
            gates,
            wave,
            "analysis_dataset_synthesis_ready",
            synthesis_ok,
            f"join_status={synthesis.get('join_plan_status', 'missing')}; ready_columns={synthesis.get('synthesis_ready_columns', '0')}; blocked_columns={synthesis.get('blocked_columns', '0')}",
            "Complete promoted household-climate schema and join review.",
        )
        add_gate(
            gates,
            wave,
            "promoted_registry_write_gate",
            registry_ok,
            f"registry_analysis_ready={registry.get('analysis_ready_status', 'missing')}; rows={registry.get('rows', '0')}",
            "Write to data/ only when the promoted registry marks this country-wave as analysis-ready with nonzero rows.",
        )

        failed = [row for row in gates if row["status"] != "pass"]
        if not raw_ready:
            next_action = "download_or_place_complete_original_raw_package"
            next_action_text = "Download/place the complete unchanged official raw package and all documentation in local_target_folder."
        elif not archive_ok:
            next_action = "confirm_archive_or_direct_raw_preflight"
            next_action_text = "Confirm readable archive/direct raw and documentation files, then rerun preflight."
        elif not all_requirements_verified:
            next_action = "complete_raw_value_key_unit_verification"
            next_action_text = "Verify merge keys, weights/design, consumption/income, OOP, access, timing, geography, missing codes, units, recall periods, and skip patterns."
        elif not climate_ok:
            if clean(climate.get("current_climate_linkage_gate_status")) == "route_preflight_ready_needs_extraction_validation":
                next_action = "extract_validate_chirps_adm2_exposures"
                next_action_text = "Download/extract CHIRPS ADM2 monthly rasters, validate coverage/units/lag windows, then decide whether the climate linkage route can be accepted."
            else:
                next_action = "accept_chirps_or_era5_linkage_route"
                next_action_text = "Accept a CHIRPS or ERA5 linkage route after raw timing/geography verification."
        elif not synthesis_ok:
            next_action = "complete_analysis_dataset_synthesis_join_review"
            next_action_text = "Complete the promoted household-climate schema and join review."
        elif not registry_ok:
            next_action = "refresh_promoted_registry_and_write_gate"
            next_action_text = "Refresh the promoted registry and data write gate after all upstream gates pass."
        else:
            next_action = "ready_for_promoted_dataset_write"
            next_action_text = "All packet gates pass; write promoted data via the controlled pipeline."

        index_row = {
            "download_priority_order": clean(wave.get("download_priority_order")),
            "queue_role": clean(wave.get("queue_role")),
            "country": clean(wave.get("country")),
            "wave": clean(wave.get("wave")),
            "idno": idno,
            "survey_name": clean(wave.get("survey_name")),
            "official_get_microdata_url": clean(wave.get("official_get_microdata_url")),
            "local_target_folder": clean(wave.get("local_target_folder")),
            "public_documentation_status": "ready_metadata_only" if public_ready else "blocked",
            "variable_evidence_status": "ready_metadata_only_raw_review_required" if variable_ready else "blocked",
            "raw_package_status": "raw_archive_plus_official_public_documentation_ready_for_raw_review" if raw_ready else clean(intake.get("raw_package_status")) or "missing",
            "archive_preflight_status": clean(archive.get("archive_preflight_status")) or "missing",
            "raw_value_verification_status": "all_verified" if all_requirements_verified else "blocked_not_raw_value_verified",
            "financial_protection_status": "ready" if financial_ready else "blocked",
            "access_forgone_care_status": "ready" if access_ready else "blocked",
            "climate_linkage_status": "ready" if climate_ok else "blocked",
            "analysis_synthesis_status": clean(synthesis.get("join_plan_status")) or "missing",
            "promoted_registry_status": clean(registry.get("analysis_ready_status")) or "not_promoted",
            "packet_status": "ready_for_promoted_dataset_write" if not failed else "blocked_fail_closed",
            "failed_gate_count": str(len(failed)),
            "next_blocking_action": next_action,
            "packet_report": "",
            "raw_folder_handoff": "",
        }
        packet_path = write_packet(
            wave,
            index_row,
            gates,
            public_resources_by_id.get(idno, []),
            coverage_rows,
            shortlist_rows,
            matrix_rows,
            archive_req_by_id.get(idno, []),
            acceptance_rows,
        )
        index_row["packet_report"] = packet_path
        index_row["raw_folder_handoff"] = write_raw_handoff(wave, packet_path, len(failed))
        index_rows.append(index_row)
        gate_rows.extend(gates)
        if failed:
            action_rows.append(
                {
                    "action_rank": "",
                    "download_priority_order": clean(wave.get("download_priority_order")),
                    "queue_role": clean(wave.get("queue_role")),
                    "country": clean(wave.get("country")),
                    "wave": clean(wave.get("wave")),
                    "idno": idno,
                    "blocking_stage": next_action,
                    "required_action": next_action_text,
                    "local_target_folder": clean(wave.get("local_target_folder")),
                    "official_url": clean(wave.get("official_get_microdata_url")),
                    "packet_report": packet_path,
                }
            )

    action_rows.sort(key=lambda row: safe_int(row.get("download_priority_order"), 999999))
    for rank, row in enumerate(action_rows, start=1):
        row["action_rank"] = str(rank)
    return index_rows, gate_rows, action_rows, build_summary(index_rows, gate_rows, action_rows)


def build_summary(
    index_rows: list[dict[str, str]],
    gate_rows: list[dict[str, str]],
    action_rows: list[dict[str, str]],
) -> list[dict[str, str]]:
    gate_counts = Counter(row["status"] for row in gate_rows)
    role_counts = Counter(row["queue_role"] for row in index_rows)
    packet_counts = Counter(row["packet_status"] for row in index_rows)
    action_counts = Counter(row["next_blocking_action"] for row in index_rows)
    rows = [
        {"metric": "priority_lsms_country_wave_packet_rows", "value": str(len(index_rows)), "interpretation": "Refocused LSMS/ISA country-wave promotion packets built."},
        {"metric": "priority_lsms_country_wave_packet_core_rows", "value": str(role_counts.get("core_selected_lsms_isa_aligned", 0) + role_counts.get("core_replacement_primary", 0)), "interpretation": "Core selected/refocused replacement packets."},
        {"metric": "priority_lsms_country_wave_packet_backup_rows", "value": str(role_counts.get("replacement_backup_wave", 0) + role_counts.get("sixth_country_backup_candidate", 0)), "interpretation": "Backup and sixth-country candidate packets."},
        {"metric": "priority_lsms_country_wave_packet_gate_rows", "value": str(len(gate_rows)), "interpretation": "Gate rows across LSMS/ISA promotion packets."},
        {"metric": "priority_lsms_country_wave_packet_passed_gate_rows", "value": str(gate_counts.get("pass", 0)), "interpretation": "Packet gates currently passing."},
        {"metric": "priority_lsms_country_wave_packet_failed_gate_rows", "value": str(gate_counts.get("fail", 0)), "interpretation": "Packet gates still blocking promotion."},
        {"metric": "priority_lsms_country_wave_packet_public_documentation_ready_rows", "value": str(sum(1 for row in index_rows if row["public_documentation_status"].startswith("ready"))), "interpretation": "Packets with complete public documentation receipt."},
        {"metric": "priority_lsms_country_wave_packet_variable_evidence_ready_rows", "value": str(sum(1 for row in index_rows if row["variable_evidence_status"].startswith("ready"))), "interpretation": "Packets with official variable evidence coverage ready for raw review."},
        {"metric": "priority_lsms_country_wave_packet_raw_package_ready_rows", "value": str(sum(1 for row in index_rows if row["next_blocking_action"] != "download_or_place_complete_original_raw_package")), "interpretation": "Packets with complete original raw package receipt and documentation."},
        {"metric": "priority_lsms_country_wave_packet_archive_preflight_ready_rows", "value": str(sum(1 for row in index_rows if row["archive_preflight_status"] == "ready_for_raw_receipt_schema_and_manual_review")), "interpretation": "Packets with readable archive/direct raw preflight."},
        {"metric": "priority_lsms_country_wave_packet_raw_value_verified_rows", "value": str(sum(1 for row in index_rows if row["raw_value_verification_status"] == "all_verified")), "interpretation": "Packets with all required raw values verified."},
        {"metric": "priority_lsms_country_wave_packet_financial_ready_rows", "value": str(sum(1 for row in index_rows if row["financial_protection_status"] == "ready")), "interpretation": "Packets ready for financial-protection outcomes."},
        {"metric": "priority_lsms_country_wave_packet_access_ready_rows", "value": str(sum(1 for row in index_rows if row["access_forgone_care_status"] == "ready")), "interpretation": "Packets ready for access/forgone-care outcomes."},
        {"metric": "priority_lsms_country_wave_packet_climate_ready_rows", "value": str(sum(1 for row in index_rows if row["climate_linkage_status"] == "ready")), "interpretation": "Packets with accepted CHIRPS/ERA5 climate-linkage route."},
        {"metric": "priority_lsms_country_wave_packet_analysis_synthesis_ready_rows", "value": str(sum(1 for row in index_rows if row["analysis_synthesis_status"] == "ready_for_promoted_dataset_build")), "interpretation": "Packets ready for promoted dataset synthesis."},
        {"metric": "priority_lsms_country_wave_packet_analysis_ready_rows", "value": str(sum(1 for row in index_rows if row["promoted_registry_status"] == "promoted_analysis_ready")), "interpretation": "Packets ready for promoted data writes."},
        {"metric": "priority_lsms_country_wave_packet_action_rows", "value": str(len(action_rows)), "interpretation": "Next blocking actions across LSMS/ISA packets."},
        {"metric": "priority_lsms_country_wave_packet_reports_written", "value": str(sum(1 for row in index_rows if row.get("packet_report"))), "interpretation": "Per-wave packet reports written."},
        {"metric": "priority_lsms_country_wave_packet_handoffs_written", "value": str(sum(1 for row in index_rows if row.get("raw_folder_handoff"))), "interpretation": "Per-wave raw-folder packet handoffs written."},
        {"metric": "priority_lsms_country_wave_packet_data_write_status", "value": "blocked_no_promoted_rows", "interpretation": "No LSMS/ISA country-wave may write to data/ from metadata-only packet evidence."},
        {"metric": "modeling_gate_status", "value": "blocked", "interpretation": "Models remain blocked until raw-backed promotion thresholds and accepted climate linkage pass."},
    ]
    for status, count in sorted(packet_counts.items()):
        rows.append({"metric": f"priority_lsms_country_wave_packet_status_{status}", "value": str(count), "interpretation": "Packet status count."})
    for action, count in sorted(action_counts.items()):
        rows.append({"metric": f"priority_lsms_country_wave_packet_next_action_{action}", "value": str(count), "interpretation": "Next blocking action count."})
    return rows


def write_report(
    index_rows: list[dict[str, str]],
    gate_rows: list[dict[str, str]],
    action_rows: list[dict[str, str]],
    summary_rows: list[dict[str, str]],
) -> None:
    summary_table = "\n".join(f"| {row['metric']} | {row['value']} | {row['interpretation']} |" for row in summary_rows)
    failing_gates = [row for row in gate_rows if row["status"] != "pass"]
    REPORT_PATH.write_text(
        f"""# Priority LSMS-ISA Country-Wave Promotion Packets

Status: 19-wave refocused LSMS/ISA promotion-control layer. These packets
connect public documentation, official variable evidence, raw intake, archive
preflight, value-verification requirements, climate linkage, synthesis, and
registry gates for each target country-wave.

This layer does not write data into `data/`; it is deliberately fail-closed
until complete original raw packages and raw value checks pass.

## Summary

| Metric | Value | Interpretation |
|---|---:|---|
{summary_table}

## Packet Index

{markdown_table(index_rows, ['download_priority_order', 'queue_role', 'idno', 'country', 'wave', 'public_documentation_status', 'variable_evidence_status', 'raw_package_status', 'archive_preflight_status', 'raw_value_verification_status', 'climate_linkage_status', 'packet_status', 'next_blocking_action'], 25)}

## Next Blocking Actions

{markdown_table(action_rows, ['action_rank', 'idno', 'blocking_stage', 'required_action', 'local_target_folder'], 25)}

## Failed Gate Preview

{markdown_table(failing_gates, ['download_priority_order', 'idno', 'gate', 'status', 'evidence', 'required_action'], 40)}

## Machine-Readable Outputs

- `temp/priority_lsms_isa_country_wave_promotion_packet_index.csv`
- `temp/priority_lsms_isa_country_wave_promotion_packet_gate_matrix.csv`
- `temp/priority_lsms_isa_country_wave_promotion_packet_action_queue.csv`
- `result/priority_lsms_isa_country_wave_promotion_packet_summary.csv`
- `report/priority_lsms_isa_country_wave_promotion_packets/`

## Guardrail

Public metadata coverage is not raw value verification. Every packet remains
blocked from promoted-data writes until complete raw packages, requirement-level
raw checks, and an accepted CHIRPS or ERA5 linkage route pass.
""",
        encoding="utf-8",
    )


def main() -> None:
    ensure_dirs()
    index_rows, gate_rows, action_rows, summary_rows = build_outputs()
    write_csv(INDEX_PATH, index_rows, INDEX_COLUMNS)
    write_csv(GATE_MATRIX_PATH, gate_rows, GATE_COLUMNS)
    write_csv(ACTION_QUEUE_PATH, action_rows, ACTION_COLUMNS)
    write_csv(SUMMARY_PATH, summary_rows, SUMMARY_COLUMNS)
    write_report(index_rows, gate_rows, action_rows, summary_rows)
    append_log(
        TEMP_DIR / "audit_log.md",
        f"Built priority LSMS-ISA country-wave promotion packets packets={len(index_rows)} gates={len(gate_rows)} actions={len(action_rows)}.",
    )
    print(f"Priority LSMS-ISA country-wave promotion packets rows={len(index_rows)} gates={len(gate_rows)}.")


if __name__ == "__main__":
    main()
