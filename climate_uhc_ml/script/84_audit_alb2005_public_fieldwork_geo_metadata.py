from __future__ import annotations

import csv
from pathlib import Path
from typing import Any

from common import REPORT_DIR, RESULT_DIR, TEMP_DIR, append_log, ensure_dirs, write_csv


IDNO = "ALB_2005_LSMS_v01_M"
COUNTRY = "Albania"
SURVEY_NAME = "Living Standards Measurement Survey 2005"

DDI_PATH = TEMP_DIR / "source_snapshots" / "first_batch_public_documentation" / "1_ALB_2005_LSMS_v01_M" / "metadata_ddi_xml.xml"
TIMING_GEO_SUMMARY_PATH = RESULT_DIR / "alb2005_timing_geography_exhaustive_summary.csv"
SOURCE_SEARCH_SUMMARY_PATH = RESULT_DIR / "alb2005_timing_geography_source_search_summary.csv"

AUDIT_PATH = TEMP_DIR / "alb2005_public_fieldwork_geo_metadata_audit.csv"
SUMMARY_PATH = RESULT_DIR / "alb2005_public_fieldwork_geo_metadata_summary.csv"
REPORT_PATH = REPORT_DIR / "alb2005_public_fieldwork_geo_metadata_audit.md"

DECISION = "blocked_public_metadata_not_household_climate_linkage_ready"

AUDIT_COLUMNS = [
    "evidence_id",
    "country",
    "idno",
    "survey_name",
    "evidence_domain",
    "claim_checked",
    "source_artifact",
    "source_line",
    "source_status",
    "evidence_text",
    "analysis_interpretation",
    "promotion_status",
    "required_next_evidence",
]
SUMMARY_COLUMNS = ["metric", "value", "interpretation"]


SOURCE_EVIDENCE = [
    {
        "evidence_id": "fieldwork_period_ddi",
        "evidence_domain": "fieldwork_period",
        "claim_checked": "Public DDI gives the main 2005 LSMS fieldwork period and the October agriculture follow-up.",
        "needle": "The 2005 LSMS was in the field between May and early July",
        "analysis_interpretation": "Wave-level fieldwork window is source-verified, but this is not household-level interview date or month.",
        "promotion_status": "context_only_not_household_timing_ready",
        "required_next_evidence": "Verify household-level interview date/month, or define a defensible wave/admin timing assignment and exposure-window sensitivity plan.",
    },
    {
        "evidence_id": "fieldwork_start_ddi",
        "evidence_domain": "fieldwork_period",
        "claim_checked": "Public DDI reports household fieldwork started on May 3.",
        "needle": "The fieldwork started on May 3",
        "analysis_interpretation": "Wave start date is source-verified, but not enough to time each household's exposure window.",
        "promotion_status": "context_only_not_household_timing_ready",
        "required_next_evidence": "Find or derive household/admin interview timing before constructing lagged climate exposures.",
    },
    {
        "evidence_id": "enumeration_end_ddi",
        "evidence_domain": "fieldwork_period",
        "claim_checked": "Public DDI reports enumeration was finished by July 2005.",
        "needle": "All of the enumeration was finished by July 2005",
        "analysis_interpretation": "Wave end timing is source-verified, but the household row still lacks verified interview timing.",
        "promotion_status": "context_only_not_household_timing_ready",
        "required_next_evidence": "Verify nonmissing interview month/date or implement a reviewed fieldwork-window exposure sensitivity design.",
    },
    {
        "evidence_id": "price_questionnaire_parallel_ddi",
        "evidence_domain": "fieldwork_period",
        "claim_checked": "Public DDI says the price questionnaire was sent during May-July 2005 with the core questionnaire.",
        "needle": "sent out at the same time as the core questionnaire, that is, during May-July 2005",
        "analysis_interpretation": "Price-module timing supports the core fieldwork window but is not an individual household interview date.",
        "promotion_status": "context_only_not_household_timing_ready",
        "required_next_evidence": "Document whether any price/community timing fields can be linked to household rows without creating post hoc timing assumptions.",
    },
    {
        "evidence_id": "agriculture_october_followup_ddi",
        "evidence_domain": "fieldwork_period",
        "claim_checked": "Public DDI distinguishes the October agriculture module from the main household fieldwork.",
        "needle": "the agricultural module was sent out in the Fall 2005",
        "analysis_interpretation": "October is a module-specific follow-up for agricultural households, not the default core household interview month.",
        "promotion_status": "context_only_module_specific_not_core_timing_ready",
        "required_next_evidence": "Keep October separate from core timing unless a row-level agriculture follow-up analysis is explicitly built.",
    },
    {
        "evidence_id": "gps_recorded_ddi",
        "evidence_domain": "gps_metadata",
        "claim_checked": "Public DDI says longitude and latitude of each household were recorded using portable GPS devices.",
        "needle": "longitude and latitude of each household were also recorded using portable GPS devices",
        "analysis_interpretation": "The public metadata claims GPS collection, but the current extracted/raw-value audits have not verified coordinate variables and values.",
        "promotion_status": "public_metadata_claim_not_raw_coordinate_ready",
        "required_next_evidence": "Locate raw latitude/longitude variables or a permitted coordinate file, verify coverage, precision, and access restrictions.",
    },
    {
        "evidence_id": "gps_linkage_purpose_ddi",
        "evidence_domain": "gps_metadata",
        "claim_checked": "Public DDI says georeferencing was intended to enable spatial linkage.",
        "needle": "Geo-referencing will enable a more efficient spatial link",
        "analysis_interpretation": "The metadata supports climate-linkage relevance, but does not itself provide usable coordinates.",
        "promotion_status": "public_metadata_claim_not_raw_coordinate_ready",
        "required_next_evidence": "Verify actual coordinate values or a documented public/registered access path to coordinates.",
    },
    {
        "evidence_id": "sampling_frame_hierarchy_ddi",
        "evidence_domain": "sampling_geography",
        "claim_checked": "Public DDI describes Albania's 12 prefectures and districts.",
        "needle": "divided geographically into 12 Prefectures",
        "analysis_interpretation": "Administrative hierarchy is source-verified, but a joinable household/admin boundary key is still not accepted.",
        "promotion_status": "context_only_not_joinable_admin_ready",
        "required_next_evidence": "Confirm full-coverage current-location admin fields and a boundary/crosswalk source that matches the survey geography vintage.",
    },
    {
        "evidence_id": "ea_classification_ddi",
        "evidence_domain": "sampling_geography",
        "claim_checked": "Public DDI says EAs in the sampling frame were classified by prefecture, district, city, or commune.",
        "needle": "EAs in the frame are classified by Prefecture, District, City or Commune",
        "analysis_interpretation": "Sampling-frame geography exists in documentation, but the current household extract still has only partial usable geography.",
        "promotion_status": "context_only_not_joinable_admin_ready",
        "required_next_evidence": "Find row-level EA/admin fields with full coverage or an official crosswalk from survey codes to boundaries.",
    },
    {
        "evidence_id": "gps_training_ddi",
        "evidence_domain": "gps_metadata",
        "claim_checked": "Public DDI reports enumerator training covered GPS devices.",
        "needle": "training also covered logistics, the use of the GPS devices",
        "analysis_interpretation": "Training evidence corroborates GPS collection procedures but does not verify coordinate availability in the local raw files.",
        "promotion_status": "public_metadata_claim_not_raw_coordinate_ready",
        "required_next_evidence": "Inspect extracted modules or obtain the coordinate file before climate extraction.",
    },
]


def read_csv_dicts(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        return []
    with path.open(encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def metric_value(rows: list[dict[str, str]], metric: str, default: str = "0") -> str:
    return next((row.get("value", default) for row in rows if row.get("metric") == metric), default)


def safe_int(value: Any) -> int:
    try:
        return int(float(str(value).strip()))
    except (TypeError, ValueError):
        return 0


def rel(path: Path) -> str:
    try:
        return str(path.relative_to(TEMP_DIR.parent)).replace("\\", "/")
    except ValueError:
        return str(path).replace("\\", "/")


def read_lines(path: Path) -> list[str]:
    if not path.exists():
        return []
    return path.read_text(encoding="utf-8", errors="replace").splitlines()


def find_line(lines: list[str], needle: str) -> tuple[str, str, str]:
    needle_low = needle.lower()
    for idx, line in enumerate(lines, start=1):
        if needle_low in line.lower():
            return str(idx), "public_source_snippet_verified", " ".join(line.split())
    return "", "source_snippet_missing", ""


def evidence_row(spec: dict[str, str], ddi_lines: list[str]) -> dict[str, str]:
    source_line, source_status, evidence_text = find_line(ddi_lines, spec["needle"])
    return {
        "evidence_id": spec["evidence_id"],
        "country": COUNTRY,
        "idno": IDNO,
        "survey_name": SURVEY_NAME,
        "evidence_domain": spec["evidence_domain"],
        "claim_checked": spec["claim_checked"],
        "source_artifact": rel(DDI_PATH),
        "source_line": source_line,
        "source_status": source_status if DDI_PATH.exists() else "source_file_missing",
        "evidence_text": evidence_text,
        "analysis_interpretation": spec["analysis_interpretation"],
        "promotion_status": spec["promotion_status"],
        "required_next_evidence": spec["required_next_evidence"],
    }


def summary_row(metric: str, value: Any, interpretation: str) -> dict[str, str]:
    return {"metric": metric, "value": str(value), "interpretation": interpretation}


def build_audit() -> tuple[list[dict[str, str]], list[dict[str, str]]]:
    ddi_lines = read_lines(DDI_PATH)
    rows = [evidence_row(spec, ddi_lines) for spec in SOURCE_EVIDENCE]

    timing_summary = read_csv_dicts(TIMING_GEO_SUMMARY_PATH)
    source_search_summary = read_csv_dicts(SOURCE_SEARCH_SUMMARY_PATH)
    verified_rows = sum(1 for row in rows if row["source_status"] == "public_source_snippet_verified")
    missing_rows = sum(1 for row in rows if row["source_status"] != "public_source_snippet_verified")

    household_timing_verified = safe_int(metric_value(timing_summary, "alb2005_interview_timing_verified_rows"))
    raw_coordinate_rows = safe_int(metric_value(timing_summary, "alb2005_coordinate_candidate_rows"))
    full_geography_rows = safe_int(metric_value(timing_summary, "alb2005_geography_verified_full_coverage_rows"))
    climate_ready_rows = safe_int(metric_value(timing_summary, "alb2005_climate_linkage_ready_rows"))
    source_search_household_timing_ready = safe_int(metric_value(source_search_summary, "alb2005_timing_geography_source_search_interview_timing_ready_rows"))
    source_search_coordinate_rows = safe_int(metric_value(source_search_summary, "alb2005_timing_geography_source_search_coordinate_candidate_rows"))
    source_search_climate_ready = safe_int(metric_value(source_search_summary, "alb2005_timing_geography_source_search_climate_linkage_ready_rows"))

    summary = [
        summary_row("alb2005_public_fieldwork_geo_metadata_evidence_rows", len(rows), "Public fieldwork/geography metadata evidence rows audited from saved DDI XML."),
        summary_row("alb2005_public_fieldwork_geo_metadata_verified_source_rows", verified_rows, "Rows where the expected public-source snippet was found."),
        summary_row("alb2005_public_fieldwork_geo_metadata_source_missing_rows", missing_rows, "Rows where the expected public-source snippet or source file was missing."),
        summary_row("alb2005_public_fieldwork_geo_metadata_fieldwork_period_evidence_rows", sum(1 for row in rows if row["evidence_domain"] == "fieldwork_period"), "Rows documenting the wave-level fieldwork window or module-specific timing."),
        summary_row("alb2005_public_fieldwork_geo_metadata_gps_claim_rows", sum(1 for row in rows if row["evidence_domain"] == "gps_metadata"), "Rows documenting public metadata claims about GPS/georeferencing."),
        summary_row("alb2005_public_fieldwork_geo_metadata_sampling_geo_rows", sum(1 for row in rows if row["evidence_domain"] == "sampling_geography"), "Rows documenting public sampling/admin geography context."),
        summary_row("alb2005_public_fieldwork_geo_metadata_household_timing_verified_rows", household_timing_verified, "Verified row-level household timing rows from the raw timing/geography audit; must remain zero until timing is actually verified."),
        summary_row("alb2005_public_fieldwork_geo_metadata_raw_coordinate_value_rows", raw_coordinate_rows, "Verified raw coordinate candidate rows from the raw timing/geography audit; must remain zero until coordinate values are actually located."),
        summary_row("alb2005_public_fieldwork_geo_metadata_full_geography_rows", full_geography_rows, "Verified full-coverage row-level geography rows from the raw timing/geography audit."),
        summary_row("alb2005_public_fieldwork_geo_metadata_source_search_household_timing_ready_rows", source_search_household_timing_ready, "Timing-ready rows from the source-search audit."),
        summary_row("alb2005_public_fieldwork_geo_metadata_source_search_coordinate_rows", source_search_coordinate_rows, "Coordinate candidate rows from the source-search audit."),
        summary_row("alb2005_public_fieldwork_geo_metadata_source_search_climate_linkage_ready_rows", source_search_climate_ready, "Climate-linkage-ready rows from the source-search audit."),
        summary_row("alb2005_public_fieldwork_geo_metadata_climate_linkage_ready_rows", climate_ready_rows, "Rows ready for climate linkage after this metadata audit; intentionally zero."),
        summary_row("alb2005_public_fieldwork_geo_metadata_current_decision", DECISION, "Current fail-closed decision for public fieldwork/geography metadata."),
    ]
    return rows, summary


def markdown_rows(rows: list[dict[str, str]], columns: list[str]) -> str:
    lines = ["| " + " | ".join(columns) + " |", "|" + "|".join("---" for _ in columns) + "|"]
    for row in rows:
        values = []
        for column in columns:
            value = (row.get(column, "") or "").replace("|", "/")
            if len(value) > 125:
                value = value[:122] + "..."
            values.append(value)
        lines.append("| " + " | ".join(values) + " |")
    return "\n".join(lines)


def write_report(rows: list[dict[str, str]], summary: list[dict[str, str]]) -> None:
    summary_table = "\n".join(f"| {row['metric']} | {row['value']} | {row['interpretation']} |" for row in summary)
    REPORT_PATH.write_text(
        f"""# ALB_2005 Public Fieldwork and Geography Metadata Audit

Status: fail-closed public-metadata evidence audit. The saved World Bank DDI metadata confirms a May to early-July 2005 main fieldwork window, an October agriculture/community follow-up, sampling geography context, and a public claim that household longitude/latitude were recorded using GPS devices. This audit does not promote ALB_2005 to climate-linked data because row-level household interview timing and raw coordinate values remain unverified in the extracted files.

## Summary

| Metric | Value | Interpretation |
|---|---:|---|
{summary_table}

## Evidence Rows

{markdown_rows(rows, ['evidence_id', 'evidence_domain', 'source_line', 'source_status', 'promotion_status', 'analysis_interpretation'])}

## Interpretation

- Public metadata improves the source context for ALB_2005 timing and geography.
- The May to early-July fieldwork window is wave-level evidence, not household-level timing.
- The GPS statement is a public metadata claim, not verified coordinate values in the local raw files.
- October belongs to agriculture/community follow-up and must not be treated as the default core household interview month.
- Climate exposure extraction remains blocked until timing and geography are accepted through raw-value evidence or a reviewed sensitivity design.

## Machine-Readable Outputs

- `temp/alb2005_public_fieldwork_geo_metadata_audit.csv`
- `result/alb2005_public_fieldwork_geo_metadata_summary.csv`
""",
        encoding="utf-8",
    )


def main() -> None:
    ensure_dirs()
    rows, summary = build_audit()
    write_csv(AUDIT_PATH, rows, AUDIT_COLUMNS)
    write_csv(SUMMARY_PATH, summary, SUMMARY_COLUMNS)
    write_report(rows, summary)
    append_log(TEMP_DIR / "audit_log.md", f"Built ALB_2005 public fieldwork/geography metadata audit rows={len(rows)} decision={DECISION}.")
    print(f"ALB_2005 public fieldwork/geography metadata audit rows={len(rows)} decision={DECISION}.")


if __name__ == "__main__":
    main()
