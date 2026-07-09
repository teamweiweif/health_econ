from __future__ import annotations

import re
import warnings
from pathlib import Path
from typing import Any

from common import REPORT_DIR, RESULT_DIR, TEMP_DIR, append_log, ensure_dirs, write_csv

try:
    import pyreadstat
except ImportError:  # pragma: no cover - environment audit reports this elsewhere.
    pyreadstat = None


AUDIT_PATH = TEMP_DIR / "albania_existing_raw_wave_audit.csv"
SUMMARY_PATH = RESULT_DIR / "albania_existing_raw_wave_audit_summary.csv"
REPORT_PATH = REPORT_DIR / "albania_existing_raw_wave_audit.md"

WAVE_ROWS = [
    {
        "country": "Albania",
        "survey_name": "Living Standards Measurement Survey 2002",
        "wave": "2002",
        "idno": "ALB_2002_LSMS_v01_M",
        "archive_name": "lsms2002en.rar",
        "raw_root": TEMP_DIR / "raw_extracted" / "lsms2002en_4dbf0b087520" / "lsms2002en" / "Data_2002",
    },
    {
        "country": "Albania",
        "survey_name": "Living Standards Measurement Survey 2005",
        "wave": "2005",
        "idno": "ALB_2005_LSMS_v01_M",
        "archive_name": "lsms2005en.rar",
        "raw_root": TEMP_DIR / "raw_extracted" / "lsms2005en_1e7f1965c4a5" / "lsms2005en" / "Data_2005",
    },
    {
        "country": "Albania",
        "survey_name": "Living Standards Measurement Survey 2008",
        "wave": "2008",
        "idno": "ALB_2008_LSMS_v01_M",
        "archive_name": "lsms_2008_eng.rar",
        "raw_root": TEMP_DIR / "raw_extracted" / "lsms_2008_eng_a54110ab32b9" / "LSMS 2008_eng" / "Data_2008",
    },
    {
        "country": "Albania",
        "survey_name": "Living Standards Measurement Survey 2012",
        "wave": "2012",
        "idno": "ALB_2012_LSMS_v01_M_v01_A_PUF",
        "archive_name": "lsms_2012_eng.rar",
        "raw_root": TEMP_DIR / "raw_extracted" / "lsms_2012_eng_7631729d2caf" / "LSMS 2012_eng" / "Data_LSMS 2012",
    },
]

AUDIT_COLUMNS = [
    "country",
    "survey_name",
    "wave",
    "idno",
    "archive_path",
    "raw_root",
    "archive_present",
    "raw_root_present",
    "raw_tabular_files",
    "readable_raw_files",
    "read_failed_files",
    "raw_variable_rows",
    "schema_inventory_status",
    "existing_deep_audit_status",
    "consumption_signal_count",
    "oop_health_signal_count",
    "health_need_access_signal_count",
    "survey_design_signal_count",
    "timing_signal_count",
    "geography_signal_count",
    "gps_signal_count",
    "shock_signal_count",
    "consumption_examples",
    "oop_health_examples",
    "health_need_access_examples",
    "timing_examples",
    "geography_examples",
    "gps_examples",
    "shock_examples",
    "current_status",
    "promotion_status",
    "next_action",
]
SUMMARY_COLUMNS = ["metric", "value", "interpretation"]

CONCEPT_PATTERNS: dict[str, list[str]] = {
    "consumption": [
        r"\btotal consumption\b",
        r"\bconsumption aggregate\b",
        r"\btotcons\b",
        r"\bfood consumption\b",
        r"\bnon[- ]?food\b",
        r"\bexpenditure aggregate\b",
        r"\bwelfare aggregate\b",
    ],
    "oop_health": [
        r"\bhealth expenditure\b",
        r"\bmedical expenditure\b",
        r"\bout[- ]?of[- ]?pocket\b",
        r"\boop\b",
        r"\bamount paid\b",
        r"\bhospital cost\b",
        r"\bmedicine cost\b",
        r"\bhealth spending\b",
    ],
    "health_need_access": [
        r"\billness\b",
        r"\binjury\b",
        r"\bsick\b",
        r"\bhealth problem\b",
        r"\bsought care\b",
        r"\bseek care\b",
        r"\bvisited\b",
        r"\bconsult",
        r"\breason.*not\b",
        r"\bnot seek\b",
        r"\btoo expensive\b",
        r"\bdistance\b",
        r"\btransport\b",
    ],
    "survey_design": [
        r"\bhhid\b",
        r"\bhousehold id\b",
        r"\bpsu\b",
        r"\bcluster\b",
        r"\bstrat",
        r"\bweight\b",
        r"\bhousehold weight\b",
    ],
    "timing": [
        r"\binterview date\b",
        r"\bdate of interview\b",
        r"\binterview month\b",
        r"\bsurvey month\b",
        r"\bfieldwork\b",
    ],
    "geography": [
        r"\bregion\b",
        r"\bdistrict\b",
        r"\bcommune\b",
        r"\bmunicipality\b",
        r"\burban\b",
        r"\brural\b",
        r"\barea of residence\b",
    ],
    "gps": [
        r"\blatitude\b",
        r"\blongitude\b",
        r"\bgps\b",
        r"\bcoordinate\b",
        r"\bcoord\b",
    ],
    "shock": [
        r"\bshock\b",
        r"\bdrought\b",
        r"\bflood\b",
        r"\brain\b",
        r"\bweather\b",
        r"\bnatural disaster\b",
        r"\bcrop loss\b",
    ],
}


def read_csv_dicts(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        return []
    import csv

    with path.open(encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def compact_examples(values: list[str], limit: int = 12) -> str:
    out: list[str] = []
    seen: set[str] = set()
    for value in values:
        clean = " ".join(str(value).replace("\n", " ").split())
        if not clean or clean in seen:
            continue
        out.append(clean)
        seen.add(clean)
        if len(out) >= limit:
            break
    return "; ".join(out)


def concept_hits(variable_name: str, variable_label: str) -> list[str]:
    blob = f"{variable_name} {variable_label}".lower()
    hits: list[str] = []
    for concept, patterns in CONCEPT_PATTERNS.items():
        if any(re.search(pattern, blob) for pattern in patterns):
            hits.append(concept)
    return hits


def metadata_for_sav(path: Path) -> tuple[int, list[dict[str, str]], str]:
    if pyreadstat is None:
        return 0, [], "pyreadstat_not_available"
    try:
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            _, meta = pyreadstat.read_sav(str(path), metadataonly=True, apply_value_formats=False)
        labels = meta.column_labels or [""] * len(meta.column_names)
        variable_rows = [
            {
                "file_name": path.name,
                "variable_name": name,
                "variable_label": label or "",
            }
            for name, label in zip(meta.column_names, labels)
        ]
        return len(meta.column_names), variable_rows, "read_ok"
    except Exception as exc:  # pragma: no cover - raw-file issues are part of the audit.
        return 0, [], f"read_failed:{type(exc).__name__}"


def archive_path(idno: str, archive_name: str) -> Path:
    return TEMP_DIR / "raw_downloads" / idno / archive_name


def schema_inventory_ids() -> set[str]:
    rows = read_csv_dicts(TEMP_DIR / "raw_schema_inventory" / "schema_file_inventory.csv")
    return {row.get("idno", "") for row in rows if row.get("idno", "")}


def deep_audit_status(idno: str) -> str:
    legacy_timing_exists = (RESULT_DIR / "albania_legacy_questionnaire_timing_field_summary.csv").exists()
    if idno == "ALB_2002_LSMS_v01_M" and legacy_timing_exists and (RESULT_DIR / "alb2002_boundary_name_match_summary.csv").exists():
        return "deep_household_core_outcome_semantics_crosswalk_boundary_name_legacy_questionnaire_timing_audits_exist_timing_geography_observed_climate_blocked"
    if idno == "ALB_2002_LSMS_v01_M" and (RESULT_DIR / "alb2002_boundary_name_match_summary.csv").exists():
        return "deep_household_core_outcome_semantics_crosswalk_boundary_name_audits_exist_timing_geography_observed_climate_blocked"
    if idno == "ALB_2002_LSMS_v01_M" and (RESULT_DIR / "alb2002_outcome_semantics_raw_value_summary.csv").exists() and (RESULT_DIR / "alb2002_district_climate_crosswalk_summary.csv").exists():
        return "deep_household_core_outcome_semantics_crosswalk_audits_exist_timing_geography_observed_climate_blocked"
    if idno == "ALB_2002_LSMS_v01_M" and (RESULT_DIR / "alb2002_district_climate_crosswalk_summary.csv").exists():
        return "deep_household_core_outcome_crosswalk_audits_exist_timing_geography_observed_climate_blocked"
    if idno == "ALB_2002_LSMS_v01_M" and (RESULT_DIR / "alb2002_provisional_outcome_feasibility_summary.csv").exists():
        return "deep_household_core_and_provisional_outcome_audits_exist_timing_geography_observed_climate_crosswalk_pending"
    if idno == "ALB_2002_LSMS_v01_M" and (RESULT_DIR / "alb2002_household_core_candidate_summary.csv").exists():
        return "deep_household_core_audit_exists_timing_geography_observed_outcome_climate_crosswalk_pending"
    if idno == "ALB_2005_LSMS_v01_M" and legacy_timing_exists and (RESULT_DIR / "alb2005_outcome_semantics_raw_value_summary.csv").exists():
        return "deep_raw_value_core_outcome_semantics_timing_legacy_questionnaire_audits_exist"
    if idno == "ALB_2005_LSMS_v01_M" and (RESULT_DIR / "alb2005_outcome_semantics_raw_value_summary.csv").exists():
        return "deep_raw_value_core_outcome_semantics_timing_audits_exist"
    if idno == "ALB_2005_LSMS_v01_M" and (RESULT_DIR / "alb2005_household_core_candidate_summary.csv").exists():
        return "deep_raw_value_core_outcome_timing_audits_exist"
    if idno == "ALB_2008_LSMS_v01_M" and legacy_timing_exists and (RESULT_DIR / "alb2008_outcome_semantics_raw_value_summary.csv").exists():
        return "deep_household_core_outcome_semantics_timing_legacy_questionnaire_audits_exist_climate_blocked"
    if idno == "ALB_2008_LSMS_v01_M" and (RESULT_DIR / "alb2008_outcome_semantics_raw_value_summary.csv").exists():
        return "deep_household_core_outcome_semantics_timing_audits_exist_climate_blocked"
    if idno == "ALB_2008_LSMS_v01_M" and (RESULT_DIR / "alb2008_timing_geography_exhaustive_summary.csv").exists():
        return "deep_household_core_outcome_timing_audits_exist_climate_blocked"
    if idno == "ALB_2008_LSMS_v01_M" and (RESULT_DIR / "alb2008_provisional_outcome_feasibility_summary.csv").exists():
        return "deep_household_core_and_provisional_outcome_audits_exist_timing_still_pending"
    if idno == "ALB_2008_LSMS_v01_M" and (RESULT_DIR / "alb2008_household_core_candidate_summary.csv").exists():
        return "deep_household_core_audit_exists_outcome_timing_still_pending"
    if idno == "ALB_2012_LSMS_v01_M_v01_A_PUF" and (RESULT_DIR / "alb2012_questionnaire_timing_field_summary.csv").exists():
        return "deep_raw_core_outcome_semantics_questionnaire_timing_audits_exist_climate_blocked"
    if idno == "ALB_2012_LSMS_v01_M_v01_A_PUF" and (RESULT_DIR / "alb2012_outcome_semantics_raw_value_summary.csv").exists():
        return "deep_raw_core_outcome_semantics_timing_audits_exist_climate_blocked"
    if idno == "ALB_2012_LSMS_v01_M_v01_A_PUF" and (RESULT_DIR / "alb2012_timing_geography_exhaustive_summary.csv").exists():
        return "deep_raw_core_outcome_timing_audits_exist_climate_blocked"
    if idno == "ALB_2012_LSMS_v01_M_v01_A_PUF" and (RESULT_DIR / "alb2012_provisional_outcome_feasibility_summary.csv").exists():
        return "deep_raw_core_and_provisional_outcome_audits_exist_timing_geography_climate_blocked"
    if idno == "ALB_2012_LSMS_v01_M_v01_A_PUF" and (RESULT_DIR / "alb2012_raw_core_feasibility_summary.csv").exists():
        return "deep_raw_core_feasibility_audit_exists_timing_geography_climate_blocked"
    return "not_yet_deep_audited"


def build_rows() -> list[dict[str, str]]:
    schema_ids = schema_inventory_ids()
    rows: list[dict[str, str]] = []
    for wave in WAVE_ROWS:
        root = Path(wave["raw_root"])
        raw_files = sorted(root.glob("*.sav")) if root.exists() else []
        readable = 0
        failed = 0
        variable_count = 0
        concept_counts = {concept: 0 for concept in CONCEPT_PATTERNS}
        examples = {concept: [] for concept in CONCEPT_PATTERNS}
        for path in raw_files:
            count, variable_rows, status = metadata_for_sav(path)
            if status == "read_ok":
                readable += 1
                variable_count += count
            else:
                failed += 1
            for variable in variable_rows:
                hits = concept_hits(variable["variable_name"], variable["variable_label"])
                for hit in hits:
                    concept_counts[hit] += 1
                    examples[hit].append(f"{path.name}:{variable['variable_name']}={variable['variable_label']}")

        archive = archive_path(str(wave["idno"]), str(wave["archive_name"]))
        integrated = str(wave["idno"]) in schema_ids
        existing_audit = deep_audit_status(str(wave["idno"]))
        if not raw_files:
            current_status = "blocked_no_extracted_raw_files"
            next_action = "place or extract the raw archive before schema inspection"
        elif wave["idno"] == "ALB_2002_LSMS_v01_M" and existing_audit.startswith("deep_household_core_outcome_semantics_crosswalk_boundary_name"):
            current_status = "household_core_outcome_semantics_crosswalk_boundary_name_audited_timing_geography_observed_climate_blocked"
            next_action = "use existing ALB_2002 audits including report/alb2002_boundary_name_match_audit.md and report/albania_legacy_questionnaire_timing_field_audit.md; do not promote until manual OOP/access unit, recall, missing-code, skip-pattern, unmatched KORCE label, duplicate current-boundary names, district boundary polygons, historical crosswalk, no-GPS admin aggregation, and cross-wave comparability checks pass"
        elif wave["idno"] == "ALB_2002_LSMS_v01_M" and existing_audit.startswith("deep_household_core_outcome_semantics_crosswalk"):
            current_status = "household_core_outcome_semantics_crosswalk_audited_timing_geography_observed_climate_blocked"
            next_action = "use existing ALB_2002 audits; do not promote until manual OOP/access unit, recall, missing-code, skip-pattern, district boundary polygon, historical crosswalk, no-GPS admin aggregation, and cross-wave comparability checks pass"
        elif wave["idno"] == "ALB_2002_LSMS_v01_M" and existing_audit.startswith("deep_household_core_outcome_crosswalk"):
            current_status = "household_core_outcome_crosswalk_audited_timing_geography_observed_climate_blocked"
            next_action = "use existing ALB_2002 audits; do not promote until OOP/access semantics, units, skip patterns, district boundary polygons, historical crosswalk, no-GPS admin aggregation, and cross-wave comparability pass"
        elif wave["idno"] == "ALB_2002_LSMS_v01_M" and existing_audit.startswith("deep_household_core_and_provisional"):
            current_status = "household_core_and_provisional_outcome_audited_timing_geography_observed_climate_crosswalk_pending"
            next_action = "use existing ALB_2002 audits; do not promote until OOP/access semantics, units, skip patterns, district climate crosswalk, and cross-wave comparability pass"
        elif wave["idno"] == "ALB_2002_LSMS_v01_M" and existing_audit.startswith("deep_household_core"):
            current_status = "household_core_audited_timing_geography_observed_outcome_semantics_pending"
            next_action = "use report/alb2002_household_core_merge_audit.md, then run provisional outcome and district climate crosswalk audits before any recipe promotion"
        elif wave["idno"] == "ALB_2005_LSMS_v01_M" and existing_audit.startswith("deep_raw_value_core_outcome_semantics"):
            current_status = "documented_core_provisional_outcome_semantics_timing_audited_but_blocked"
            next_action = "use existing ALB_2005 audits including report/albania_legacy_questionnaire_timing_field_audit.md; do not promote until gift/payment-scope policy, OOP units, recall periods, missing-code semantics, skip patterns, merge keys, fieldwork timing, and full-coverage current-location geography pass"
        elif wave["idno"] == "ALB_2005_LSMS_v01_M":
            current_status = "audited_but_blocked_by_timing_geography_and_outcome_semantics"
            next_action = "use existing ALB_2005 audits; do not promote until timing/geography, OOP recall, units, and merge semantics pass"
        elif wave["idno"] == "ALB_2008_LSMS_v01_M" and existing_audit.startswith("deep_household_core_outcome_semantics"):
            current_status = "household_core_outcome_semantics_timing_audited_but_blocked_by_coarse_geography_no_interview_timing"
            next_action = "use existing ALB_2008 audits including report/albania_legacy_questionnaire_timing_field_audit.md; do not promote until interview timing, valid climate geography, OOP units, recall periods, missing-code semantics, skip patterns, gift/payment-scope policy, service-quality proxy interpretation, and cross-wave comparability pass"
        elif wave["idno"] == "ALB_2008_LSMS_v01_M" and existing_audit.startswith("deep_household_core_outcome_timing"):
            current_status = "household_core_outcome_timing_audited_but_blocked_by_coarse_geography_no_interview_timing"
            next_action = "use existing ALB_2008 audits; do not promote until interview timing, valid climate geography, OOP recall, and unit semantics pass"
        elif wave["idno"] == "ALB_2008_LSMS_v01_M" and existing_audit.startswith("deep_household_core_and_provisional"):
            current_status = "household_core_and_provisional_outcome_audited_but_blocked_by_timing_geography_recall_semantics"
            next_action = "use report/alb2008_household_core_merge_audit.md and report/alb2008_provisional_outcome_feasibility.md, then run timing/geography audit before any recipe promotion"
        elif wave["idno"] == "ALB_2008_LSMS_v01_M" and existing_audit.startswith("deep_household_core"):
            current_status = "household_core_audited_but_blocked_by_timing_geography_and_outcome_semantics"
            next_action = "use report/alb2008_household_core_merge_audit.md, then run wave-specific timing/geography and provisional outcome audits before any recipe promotion"
        elif wave["idno"] == "ALB_2012_LSMS_v01_M_v01_A_PUF" and existing_audit.startswith("deep_raw_core_outcome_semantics_questionnaire_timing"):
            current_status = "raw_core_outcome_semantics_questionnaire_timing_audited_but_blocked_by_no_raw_interview_timing_coarse_geography"
            next_action = "use report/alb2012_questionnaire_timing_field_audit.md with report/alb2012_raw_core_feasibility.md, report/alb2012_provisional_outcome_feasibility.md, report/alb2012_outcome_semantics_raw_value_audit.md, and report/alb2012_timing_geography_exhaustive_audit.md; do not promote until questionnaire timing fields are linked to raw household interview date/month values or official fieldwork-period metadata, valid climate geography, survey-design semantics, OOP/access values, missing codes, skip patterns, gift/payment-scope policy, service-quality proxy interpretation, and cross-wave comparability pass"
        elif wave["idno"] == "ALB_2012_LSMS_v01_M_v01_A_PUF" and existing_audit.startswith("deep_raw_core_outcome_semantics"):
            current_status = "raw_core_outcome_semantics_timing_audited_but_blocked_by_no_interview_timing_coarse_geography"
            next_action = "use report/alb2012_raw_core_feasibility.md, report/alb2012_provisional_outcome_feasibility.md, report/alb2012_outcome_semantics_raw_value_audit.md, and report/alb2012_timing_geography_exhaustive_audit.md; do not promote until interview timing, valid climate geography, survey-design semantics, OOP/access values, missing codes, skip patterns, gift/payment-scope policy, service-quality proxy interpretation, and cross-wave comparability pass"
        elif wave["idno"] == "ALB_2012_LSMS_v01_M_v01_A_PUF" and existing_audit.startswith("deep_raw_core_outcome_timing"):
            current_status = "raw_core_outcome_timing_audited_but_blocked_by_no_interview_timing_coarse_geography"
            next_action = "use report/alb2012_raw_core_feasibility.md, report/alb2012_provisional_outcome_feasibility.md, and report/alb2012_timing_geography_exhaustive_audit.md; do not promote until interview timing, valid climate geography, survey-design semantics, OOP/access values, skip patterns, and cross-wave comparability pass"
        elif wave["idno"] == "ALB_2012_LSMS_v01_M_v01_A_PUF" and existing_audit.startswith("deep_raw_core_and_provisional"):
            current_status = "raw_core_and_provisional_outcome_audited_but_blocked_by_no_interview_timing_coarse_geography"
            next_action = "use report/alb2012_raw_core_feasibility.md and report/alb2012_provisional_outcome_feasibility.md; do not promote until interview timing, valid climate geography, survey-design semantics, OOP/access values, skip patterns, and cross-wave comparability pass"
        elif wave["idno"] == "ALB_2012_LSMS_v01_M_v01_A_PUF" and existing_audit.startswith("deep_raw_core_feasibility"):
            current_status = "raw_core_feasibility_audited_but_blocked_by_no_interview_timing_coarse_geography"
            next_action = "use report/alb2012_raw_core_feasibility.md and then run provisional outcome feasibility; do not promote until interview timing, valid climate geography, survey-design semantics, OOP/access values, skip patterns, and cross-wave comparability pass"
        elif integrated:
            current_status = "schema_inventory_present_needs_wave_specific_value_key_audit"
            next_action = "run wave-specific merge/value/timing/geography audits before recipe consideration"
        else:
            current_status = "present_extracted_raw_files_not_integrated_into_core_gates"
            next_action = "add this wave to schema inventory or run a wave-specific raw schema/value/key/timing audit before any harmonization decision"

        rows.append(
            {
                "country": wave["country"],
                "survey_name": wave["survey_name"],
                "wave": wave["wave"],
                "idno": wave["idno"],
                "archive_path": str(archive.relative_to(TEMP_DIR.parent)).replace("\\", "/"),
                "raw_root": str(root.relative_to(TEMP_DIR.parent)).replace("\\", "/"),
                "archive_present": "1" if archive.exists() else "0",
                "raw_root_present": "1" if root.exists() else "0",
                "raw_tabular_files": str(len(raw_files)),
                "readable_raw_files": str(readable),
                "read_failed_files": str(failed),
                "raw_variable_rows": str(variable_count),
                "schema_inventory_status": "in_core_schema_inventory" if integrated else "not_in_core_schema_inventory",
                "existing_deep_audit_status": existing_audit,
                "consumption_signal_count": str(concept_counts["consumption"]),
                "oop_health_signal_count": str(concept_counts["oop_health"]),
                "health_need_access_signal_count": str(concept_counts["health_need_access"]),
                "survey_design_signal_count": str(concept_counts["survey_design"]),
                "timing_signal_count": str(concept_counts["timing"]),
                "geography_signal_count": str(concept_counts["geography"]),
                "gps_signal_count": str(concept_counts["gps"]),
                "shock_signal_count": str(concept_counts["shock"]),
                "consumption_examples": compact_examples(examples["consumption"]),
                "oop_health_examples": compact_examples(examples["oop_health"]),
                "health_need_access_examples": compact_examples(examples["health_need_access"]),
                "timing_examples": compact_examples(examples["timing"]),
                "geography_examples": compact_examples(examples["geography"]),
                "gps_examples": compact_examples(examples["gps"]),
                "shock_examples": compact_examples(examples["shock"]),
                "current_status": current_status,
                "promotion_status": "not_ready_existing_raw_wave_requires_wave_specific_audit",
                "next_action": next_action,
            }
        )
    return rows


def summary_row(metric: str, value: Any, interpretation: str) -> dict[str, str]:
    return {"metric": metric, "value": str(value), "interpretation": interpretation}


def build_summary(rows: list[dict[str, str]]) -> list[dict[str, str]]:
    return [
        summary_row("albania_existing_raw_wave_rows", len(rows), "Existing Albania LSMS wave rows audited."),
        summary_row("albania_existing_raw_wave_archive_present_rows", sum(1 for row in rows if row["archive_present"] == "1"), "Audited waves with raw archive present."),
        summary_row("albania_existing_raw_wave_extracted_rows", sum(1 for row in rows if row["raw_root_present"] == "1"), "Audited waves with extracted raw root present."),
        summary_row("albania_existing_raw_wave_unintegrated_rows", sum(1 for row in rows if row["schema_inventory_status"] == "not_in_core_schema_inventory"), "Audited waves present locally but not yet in the core schema inventory."),
        summary_row("albania_existing_raw_wave_deep_audited_rows", sum(1 for row in rows if row["existing_deep_audit_status"] != "not_yet_deep_audited"), "Audited waves with at least one existing deep raw/core audit layer."),
        summary_row("albania_existing_raw_wave_total_raw_tabular_files", sum(int(row["raw_tabular_files"]) for row in rows), "Total raw .sav files under audited Albania wave extraction roots."),
        summary_row("albania_existing_raw_wave_total_raw_variable_rows", sum(int(row["raw_variable_rows"]) for row in rows), "Total raw variables readable from audited Albania wave extraction roots."),
        summary_row("albania_existing_raw_wave_oop_signal_rows", sum(1 for row in rows if int(row["oop_health_signal_count"]) > 0), "Audited waves with at least one OOP/health-expenditure keyword signal."),
        summary_row("albania_existing_raw_wave_timing_signal_rows", sum(1 for row in rows if int(row["timing_signal_count"]) > 0), "Audited waves with apparent interview/fieldwork timing keyword signals."),
        summary_row("albania_existing_raw_wave_gps_signal_rows", sum(1 for row in rows if int(row["gps_signal_count"]) > 0), "Audited waves with GPS/coordinate keyword signals."),
        summary_row("albania_existing_raw_wave_harmonization_ready_rows", 0, "Existing Albania waves ready for harmonized data promotion after this audit."),
        summary_row("albania_existing_raw_wave_climate_linkage_ready_rows", 0, "Existing Albania waves ready for climate-linkage input promotion after this audit."),
        summary_row("albania_existing_raw_wave_current_decision", "present_raw_waves_require_wave_specific_schema_value_key_timing_audits", "Current decision for existing Albania raw waves."),
    ]


def markdown_rows(rows: list[dict[str, str]], columns: list[str], limit: int = 10) -> str:
    lines = ["| " + " | ".join(columns) + " |", "|" + "|".join("---" for _ in columns) + "|"]
    for row in rows[:limit]:
        values = []
        for column in columns:
            value = (row.get(column, "") or "").replace("|", "/")
            if len(value) > 120:
                value = value[:117] + "..."
            values.append(value)
        lines.append("| " + " | ".join(values) + " |")
    return "\n".join(lines)


def write_report(rows: list[dict[str, str]], summary: list[dict[str, str]]) -> None:
    summary_table = "\n".join(f"| {row['metric']} | {row['value']} | {row['interpretation']} |" for row in summary)
    REPORT_PATH.write_text(
        f"""# Existing Albania Raw Wave Audit

Status: local raw-wave utilization audit only. This report makes already-present Albania LSMS raw archives/extractions visible for future wave-specific auditing. It does not promote any wave into `data/`, does not construct harmonized outcomes, and does not construct climate linkage.

## Summary

| Metric | Value | Interpretation |
|---|---:|---|
{summary_table}

## Wave Rows

{markdown_rows(rows, ['idno', 'wave', 'archive_present', 'raw_tabular_files', 'raw_variable_rows', 'schema_inventory_status', 'current_status'], 10)}

## Concept Signal Counts

{markdown_rows(rows, ['idno', 'consumption_signal_count', 'oop_health_signal_count', 'health_need_access_signal_count', 'timing_signal_count', 'geography_signal_count', 'gps_signal_count', 'shock_signal_count'], 10)}

## Interpretation

- ALB_2002 now has temp household-core, provisional outcome, raw outcome-semantics, district crosswalk, and public boundary name-match diagnostics with observed interview date/month and district fields, but remains blocked by manual OOP/access unit, recall, missing-code, skip-pattern, unmatched KORCE label, duplicate current-boundary names, unverified district boundary polygons/historical crosswalk, no-GPS, and cross-wave comparability checks.
- ALB_2012 raw archives/extractions are present locally and now have temp raw-core, provisional outcome-feasibility, raw outcome-semantics, timing/geography, and questionnaire timing-field audits, but remain blocked because questionnaire timing fields are not verified raw household interview timing values; coarse prefecture/region-only geography, no GPS, OOP/access unit and recall review, gift/payment-scope policy, skip patterns, and service-quality proxy interpretation also remain unresolved.
- ALB_2008 has household-core, provisional outcome-feasibility, raw outcome-semantics, and timing/geography audits, but remains blocked by missing interview timing, coarse non-GPS geography, OOP units, recall periods, missing-code semantics, skip patterns, gift/payment-scope policy, service-quality proxy interpretation, and cross-wave comparability.
- ALB_2005 now has documented, household-core, provisional outcome, raw outcome-semantics, and timing/geography audits, but remains blocked by timing/geography, gift/payment-scope policy, OOP units, recall periods, missing-code semantics, skip patterns, merge keys, and cross-wave comparability.
- ALB_2002, ALB_2005, and ALB_2008 legacy `.xls` questionnaires are present, readable, and now have a timing/control field audit; the audit documents form-design evidence but does not promote any wave because raw household timing/geography and outcome-semantics gates remain unresolved.
- Keyword signals are triage evidence only. They do not verify units, recall periods, missing codes, merge keys, fieldwork timing, current geography, or comparability.
- Promotion-ready harmonized rows and climate-linkage-ready rows remain zero.

## Machine-Readable Outputs

- `temp/albania_existing_raw_wave_audit.csv`
- `result/albania_existing_raw_wave_audit_summary.csv`
""",
        encoding="utf-8",
    )


def main() -> None:
    ensure_dirs()
    rows = build_rows()
    summary = build_summary(rows)
    write_csv(AUDIT_PATH, rows, AUDIT_COLUMNS)
    write_csv(SUMMARY_PATH, summary, SUMMARY_COLUMNS)
    write_report(rows, summary)
    append_log(TEMP_DIR / "audit_log.md", f"Built existing Albania raw wave audit rows={len(rows)}.")
    print(f"Existing Albania raw wave audit rows={len(rows)}.")


if __name__ == "__main__":
    main()
