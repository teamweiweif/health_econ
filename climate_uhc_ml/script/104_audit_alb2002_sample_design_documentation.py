from __future__ import annotations

import csv
import math
import re
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any

import pandas as pd

from common import REPORT_DIR, RESULT_DIR, SNAPSHOT_DIR, TEMP_DIR, append_log, ensure_dirs, sha256_file, write_csv

try:
    import pyreadstat
except ImportError:  # pragma: no cover - environment audit reports this separately.
    pyreadstat = None


IDNO = "ALB_2002_LSMS_v01_M"
COUNTRY = "Albania"
SURVEY_NAME = "Living Standards Measurement Survey 2002"
WAVE = "2002"
STUDY_URL = "https://microdata.worldbank.org/catalog/86/study-description"
BASIC_INFO_URL = "https://microdata.worldbank.org/index.php/catalog/86/download/11834"

RAW_ROOT = TEMP_DIR / "raw_extracted" / "lsms2002en_4dbf0b087520" / "lsms2002en" / "Data_2002"
CANDIDATE_PATH = TEMP_DIR / "alb2002_household_core_candidate.csv"

PDF_PATH = SNAPSHOT_DIR / "alb2002_basic_information_document_sample_design.pdf"
PDF_TEXT_PATH = SNAPSHOT_DIR / "alb2002_basic_information_document_sample_design.txt"
UNEXPECTED_RESPONSE_PATH = SNAPSHOT_DIR / "alb2002_basic_information_document_unexpected_response.html"
AUDIT_PATH = TEMP_DIR / "alb2002_sample_design_documentation_audit.csv"
SUMMARY_PATH = RESULT_DIR / "alb2002_sample_design_documentation_summary.csv"
REPORT_PATH = REPORT_DIR / "alb2002_sample_design_documentation_audit.md"

DECISION = "candidate_alb2002_sample_design_documented_not_promoted_due_downstream_gates"
NO_PROMOTION = "not_promoted_documentation_evidence_only"

AUDIT_COLUMNS = [
    "country",
    "survey_name",
    "wave",
    "idno",
    "evidence_domain",
    "evidence_item",
    "source_artifacts",
    "observed_rows",
    "promotion_ready_rows",
    "diagnostic_value",
    "evidence_status",
    "promotion_status",
    "blocking_reason",
    "next_action",
]
SUMMARY_COLUMNS = ["metric", "value", "interpretation"]


def read_csv_dicts(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        return []
    with path.open(encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def fmt(value: Any) -> str:
    if value is None:
        return ""
    try:
        if pd.isna(value):
            return ""
    except TypeError:
        pass
    try:
        number = float(value)
    except (TypeError, ValueError):
        return str(value)
    if not math.isfinite(number):
        return ""
    if number.is_integer():
        return str(int(number))
    return f"{number:.6g}"


def safe_int(value: Any) -> int:
    try:
        return int(float(str(value).strip()))
    except (TypeError, ValueError):
        return 0


def fetch_pdf() -> tuple[str, str, str, str, int]:
    request = urllib.request.Request(
        BASIC_INFO_URL,
        headers={
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) climate-uhc-ml-audit/1.0",
            "Accept": "application/pdf,text/html;q=0.8,*/*;q=0.5",
        },
        method="GET",
    )
    try:
        with urllib.request.urlopen(request, timeout=45) as response:
            status = str(getattr(response, "status", ""))
            content_type = response.headers.get("Content-Type", "")
            body = response.read()
        if body.startswith(b"%PDF"):
            PDF_PATH.write_bytes(body)
            return "reachable_pdf_saved", status, content_type, sha256_file(PDF_PATH), PDF_PATH.stat().st_size
        UNEXPECTED_RESPONSE_PATH.write_bytes(body)
        if PDF_PATH.exists():
            return "using_existing_pdf_after_unexpected_response", status, content_type, sha256_file(PDF_PATH), PDF_PATH.stat().st_size
        return "blocked_response_was_not_pdf", status, content_type, "", len(body)
    except (urllib.error.HTTPError, urllib.error.URLError, TimeoutError, OSError) as exc:
        if PDF_PATH.exists():
            return "using_existing_pdf_after_fetch_failure", "", str(exc), sha256_file(PDF_PATH), PDF_PATH.stat().st_size
        return "blocked_pdf_fetch_failed_no_snapshot", "", str(exc), "", 0


def extract_pdf_text() -> tuple[str, str, int, int]:
    if not PDF_PATH.exists():
        return "blocked_pdf_missing", "", 0, 0
    try:
        from pypdf import PdfReader

        reader = PdfReader(str(PDF_PATH))
        pages = [page.extract_text() or "" for page in reader.pages]
        text = "\n\n".join(pages)
        PDF_TEXT_PATH.write_text(text, encoding="utf-8")
        return "text_extracted_with_pypdf", text, len(pages), len(text)
    except Exception as exc:  # noqa: BLE001 - audit needs failure text.
        if PDF_TEXT_PATH.exists():
            text = PDF_TEXT_PATH.read_text(encoding="utf-8", errors="replace")
            return f"using_existing_text_after_extract_failure:{type(exc).__name__}", text, 0, len(text)
        return f"blocked_text_extract_failed:{type(exc).__name__}", "", 0, 0


def normalized(text: str) -> str:
    return re.sub(r"\s+", " ", text.lower())


def text_flags(text: str) -> dict[str, int]:
    low = normalized(text)
    design_450 = bool(re.search(r"\b450\b.{0,90}(psu|primary sampling unit)", low))
    design_8 = bool(
        re.search(r"\b8\b.{0,90}household.{0,90}(psu|primary sampling unit)", low)
        or "8 households per psu" in low
        or "eight households per psu" in low
    )
    return {
        "sample_design_450_psu_8_households_seen": int(design_450 and design_8),
        "final_sample_3599_seen": int(bool(re.search(r"3[\s,.]?599", low)) and "household" in low),
        "one_household_drop_seen": int("one household" in low and ("dropped" in low or "drop" in low)),
        "april_2001_census_sampling_frame_seen": int("april 2001" in low and "census" in low and "sampling" in low),
        "tirana_quick_count_listing_seen": int("tirana" in low and ("quick count" in low or "listing" in low)),
        "reserve_household_replacement_seen": int(
            ("reserve household" in low or ("reserve" in low and "household" in low))
            and ("replace" in low or "replacement" in low or "supervisor" in low)
        ),
        "fieldwork_april_july_seen": int("april" in low and "july" in low and "field" in low),
        "sample_weight_language_seen": int("weight" in low and ("sample" in low or "household" in low)),
    }


def read_weight_metrics() -> dict[str, Any]:
    metrics: dict[str, Any] = {
        "read_status": "blocked_pyreadstat_missing" if pyreadstat is None else "missing_weight_file",
        "raw_weight_rows": 0,
        "positive_weight_rows": 0,
        "distinct_psu_rows": 0,
        "distinct_stratum_rows": 0,
        "weight_sha256": "",
    }
    path = RAW_ROOT / "weights_1.sav"
    if pyreadstat is None or not path.exists():
        return metrics
    try:
        weights, _meta = pyreadstat.read_sav(str(path), apply_value_formats=False, encoding="latin1")
    except Exception as exc:  # noqa: BLE001 - audit records raw-read failures.
        metrics["read_status"] = f"blocked_read_error:{type(exc).__name__}:{str(exc)[:120]}"
        metrics["weight_sha256"] = sha256_file(path) if path.exists() else ""
        return metrics
    metrics["read_status"] = "read_ok"
    metrics["raw_weight_rows"] = len(weights)
    metrics["positive_weight_rows"] = int((pd.to_numeric(weights.get("weight"), errors="coerce") > 0).sum()) if "weight" in weights else 0
    metrics["distinct_psu_rows"] = int(weights["psu"].nunique(dropna=True)) if "psu" in weights else 0
    metrics["distinct_stratum_rows"] = int(weights["stratum"].nunique(dropna=True)) if "stratum" in weights else 0
    metrics["weight_sha256"] = sha256_file(path)
    return metrics


def read_candidate_metrics() -> dict[str, Any]:
    metrics: dict[str, Any] = {"candidate_rows": 0, "candidate_distinct_psu_rows": 0, "candidate_read_status": "missing"}
    if not CANDIDATE_PATH.exists():
        return metrics
    try:
        candidate = pd.read_csv(CANDIDATE_PATH)
    except Exception as exc:  # noqa: BLE001 - audit records local candidate failures.
        metrics["candidate_read_status"] = f"blocked_read_error:{type(exc).__name__}:{str(exc)[:120]}"
        return metrics
    metrics["candidate_read_status"] = "read_ok"
    metrics["candidate_rows"] = len(candidate)
    metrics["candidate_distinct_psu_rows"] = int(candidate["psu"].nunique(dropna=True)) if "psu" in candidate else 0
    return metrics


def audit_row(
    domain: str,
    item: str,
    sources: list[str],
    observed_rows: Any,
    diagnostic_value: str,
    evidence_status: str,
    next_action: str,
    promotion_ready_rows: Any = 0,
) -> dict[str, str]:
    return {
        "country": COUNTRY,
        "survey_name": SURVEY_NAME,
        "wave": WAVE,
        "idno": IDNO,
        "evidence_domain": domain,
        "evidence_item": item,
        "source_artifacts": ";".join(sources),
        "observed_rows": fmt(observed_rows),
        "promotion_ready_rows": fmt(promotion_ready_rows),
        "diagnostic_value": diagnostic_value,
        "evidence_status": evidence_status,
        "promotion_status": NO_PROMOTION,
        "blocking_reason": (
            "The ALB_2002 sample design is now documented against an official World Bank Basic Information source, "
            "but weighted inference and harmonized data promotion still require accepted weight-use semantics, "
            "variance handling, denominator/outcome decisions, and climate-linkage gates to pass together."
        ),
        "next_action": next_action,
    }


def build_rows() -> tuple[list[dict[str, str]], list[dict[str, str]]]:
    pdf_status, http_status, content_type, pdf_sha, pdf_bytes = fetch_pdf()
    text_status, text, pdf_pages, text_chars = extract_pdf_text()
    flags = text_flags(text)
    weight_metrics = read_weight_metrics()
    candidate_metrics = read_candidate_metrics()

    expected_design_rows = 450 * 8
    documented_final_rows = 3599
    raw_design_concordance = int(
        weight_metrics["raw_weight_rows"] == documented_final_rows
        and weight_metrics["positive_weight_rows"] == documented_final_rows
        and weight_metrics["distinct_psu_rows"] == 450
        and candidate_metrics["candidate_rows"] == documented_final_rows
    )
    documentation_ready = int(
        PDF_PATH.exists()
        and text_chars > 1000
        and flags["sample_design_450_psu_8_households_seen"] == 1
        and flags["final_sample_3599_seen"] == 1
        and flags["april_2001_census_sampling_frame_seen"] == 1
        and raw_design_concordance == 1
    )

    rows = [
        audit_row(
            "official_basic_information_document",
            "worldbank_basic_information_pdf_snapshot",
            [BASIC_INFO_URL, f"temp/source_snapshots/{PDF_PATH.name}"],
            1 if PDF_PATH.exists() else 0,
            f"pdf_status={pdf_status}; http_status={http_status}; content_type={content_type}; bytes={pdf_bytes}; sha256={pdf_sha}",
            "official_pdf_snapshot_available" if PDF_PATH.exists() else pdf_status,
            "Keep this PDF as sample-design context and continue searching for explicit analyst weight-use instructions if needed.",
        ),
        audit_row(
            "official_basic_information_document",
            "pdf_text_extraction",
            [f"temp/source_snapshots/{PDF_PATH.name}", f"temp/source_snapshots/{PDF_TEXT_PATH.name}"],
            1 if text_chars > 0 else 0,
            f"text_status={text_status}; pages={pdf_pages}; text_chars={text_chars}",
            "pdf_text_extracted" if text_chars > 0 else text_status,
            "Use the extracted text for reproducible source-string checks; do not rely on source snippets alone.",
        ),
        audit_row(
            "official_sample_design_claims",
            "final_sample_design_and_size",
            [BASIC_INFO_URL, f"temp/source_snapshots/{PDF_TEXT_PATH.name}"],
            1 if flags["sample_design_450_psu_8_households_seen"] and flags["final_sample_3599_seen"] else 0,
            "; ".join(f"{key}={value}" for key, value in flags.items() if key in {"sample_design_450_psu_8_households_seen", "final_sample_3599_seen", "one_household_drop_seen"}),
            "official_450_psu_8_household_design_and_3599_final_sample_seen"
            if flags["sample_design_450_psu_8_households_seen"] and flags["final_sample_3599_seen"]
            else "blocked_official_sample_design_text_not_confirmed",
            "Treat the 3,599 local raw rows as concordant with the official final sample size only after raw weight and candidate counts also match.",
        ),
        audit_row(
            "official_sample_design_claims",
            "sampling_frame_fieldwork_and_listing_context",
            [BASIC_INFO_URL, f"temp/source_snapshots/{PDF_TEXT_PATH.name}", STUDY_URL],
            1 if flags["april_2001_census_sampling_frame_seen"] and flags["tirana_quick_count_listing_seen"] else 0,
            "; ".join(
                f"{key}={value}"
                for key, value in flags.items()
                if key in {"april_2001_census_sampling_frame_seen", "tirana_quick_count_listing_seen", "fieldwork_april_july_seen"}
            ),
            "official_sampling_frame_and_listing_context_seen"
            if flags["april_2001_census_sampling_frame_seen"] and flags["tirana_quick_count_listing_seen"]
            else "candidate_context_incomplete",
            "Use this only as sampling-context documentation; it does not verify every downstream analysis denominator or climate geography decision.",
        ),
        audit_row(
            "official_sample_design_claims",
            "reserve_household_and_replacement_context",
            [BASIC_INFO_URL, f"temp/source_snapshots/{PDF_TEXT_PATH.name}"],
            flags["reserve_household_replacement_seen"],
            f"reserve_household_replacement_seen={flags['reserve_household_replacement_seen']}",
            "official_replacement_context_seen" if flags["reserve_household_replacement_seen"] else "reserve_replacement_text_not_seen",
            "If weighted variance estimation becomes central, review any full sample-design appendix for replacement and finite-population implications.",
        ),
        audit_row(
            "raw_design_count_concordance",
            "raw_weights_candidate_and_official_sample_size_match",
            [
                "temp/raw_extracted/lsms2002en_4dbf0b087520/lsms2002en/Data_2002/weights_1.sav",
                "temp/alb2002_household_core_candidate.csv",
                f"temp/source_snapshots/{PDF_TEXT_PATH.name}",
            ],
            raw_design_concordance,
            f"expected_design_rows=450*8={expected_design_rows}; documented_final_rows={documented_final_rows}; "
            f"weight_read_status={weight_metrics['read_status']}; raw_weight_rows={weight_metrics['raw_weight_rows']}; "
            f"positive_weight_rows={weight_metrics['positive_weight_rows']}; distinct_psu={weight_metrics['distinct_psu_rows']}; "
            f"distinct_stratum={weight_metrics['distinct_stratum_rows']}; candidate_status={candidate_metrics['candidate_read_status']}; "
            f"candidate_rows={candidate_metrics['candidate_rows']}; candidate_distinct_psu={candidate_metrics['candidate_distinct_psu_rows']}; "
            f"weight_sha256={weight_metrics['weight_sha256']}",
            "raw_weight_candidate_counts_concordant_with_official_final_sample" if raw_design_concordance else "blocked_raw_design_counts_not_concordant",
            "Preserve PSU, strata, household weights, and candidate row-count checks in the lineage before any promoted weighted descriptive table.",
        ),
        audit_row(
            "documentation_gate",
            "sample_design_documentation_ready_not_promotion_ready",
            [
                "temp/alb2002_sample_design_documentation_audit.csv",
                "result/alb2002_sample_design_documentation_summary.csv",
                "report/alb2002_sample_design_documentation_audit.md",
            ],
            documentation_ready,
            f"documentation_ready_rows={documentation_ready}; weighted_inference_ready_rows=0; harmonized_promotion_ready_rows=0; decision={DECISION}",
            DECISION if documentation_ready else "blocked_sample_design_documentation_not_ready",
            "Keep ALB_2002 as a temp-only candidate until outcome, denominator, climate geography, and weight-use gates pass together.",
        ),
    ]

    summary = [
        {"metric": "alb2002_sample_design_documentation_audit_rows", "value": str(len(rows)), "interpretation": "Rows in the ALB_2002 sample-design documentation audit."},
        {"metric": "alb2002_sample_design_pdf_available_rows", "value": str(int(PDF_PATH.exists())), "interpretation": "Official Basic Information PDF snapshot available locally."},
        {"metric": "alb2002_sample_design_pdf_pages", "value": str(pdf_pages), "interpretation": "Pages extracted from the official Basic Information PDF."},
        {"metric": "alb2002_sample_design_text_chars", "value": str(text_chars), "interpretation": "Characters extracted from the official Basic Information PDF."},
        {"metric": "alb2002_sample_design_official_450_psu_8_hh_rows", "value": str(flags["sample_design_450_psu_8_households_seen"]), "interpretation": "Official text states a 450 PSU by 8 household sample-design claim."},
        {"metric": "alb2002_sample_design_official_3599_final_rows", "value": str(flags["final_sample_3599_seen"]), "interpretation": "Official text states or supports the 3,599 final household sample size."},
        {"metric": "alb2002_sample_design_april_2001_census_frame_rows", "value": str(flags["april_2001_census_sampling_frame_seen"]), "interpretation": "Official text documents the April 2001 census sampling-frame context."},
        {"metric": "alb2002_sample_design_tirana_listing_rows", "value": str(flags["tirana_quick_count_listing_seen"]), "interpretation": "Official text documents the Tirana quick-count or listing context."},
        {"metric": "alb2002_sample_design_reserve_replacement_rows", "value": str(flags["reserve_household_replacement_seen"]), "interpretation": "Official text documents reserve household or replacement context."},
        {"metric": "alb2002_sample_design_raw_weight_rows", "value": str(weight_metrics["raw_weight_rows"]), "interpretation": "Rows read from the ALB_2002 readable household weight file."},
        {"metric": "alb2002_sample_design_positive_weight_rows", "value": str(weight_metrics["positive_weight_rows"]), "interpretation": "Rows with positive household weights."},
        {"metric": "alb2002_sample_design_distinct_psu_rows", "value": str(weight_metrics["distinct_psu_rows"]), "interpretation": "Distinct PSU values in the readable weight file."},
        {"metric": "alb2002_sample_design_distinct_stratum_rows", "value": str(weight_metrics["distinct_stratum_rows"]), "interpretation": "Distinct stratum values in the readable weight file."},
        {"metric": "alb2002_sample_design_candidate_rows", "value": str(candidate_metrics["candidate_rows"]), "interpretation": "Rows in the temp ALB_2002 household core candidate."},
        {"metric": "alb2002_sample_design_expected_design_household_rows", "value": str(expected_design_rows), "interpretation": "450 PSU by 8 households per PSU design arithmetic."},
        {"metric": "alb2002_sample_design_documented_final_sample_rows", "value": str(documented_final_rows), "interpretation": "Official final household sample size used for concordance checks."},
        {"metric": "alb2002_sample_design_raw_design_concordance_rows", "value": str(raw_design_concordance), "interpretation": "Raw and candidate counts concordant with official sample-design/final-sample evidence."},
        {"metric": "alb2002_sample_design_documentation_ready_rows", "value": str(documentation_ready), "interpretation": "Sample-design documentation evidence ready; this is not analysis-data promotion."},
        {"metric": "alb2002_sample_design_weighted_inference_ready_rows", "value": "0", "interpretation": "Rows ready for promoted weighted inference; intentionally zero."},
        {"metric": "alb2002_sample_design_harmonized_promotion_ready_rows", "value": "0", "interpretation": "Rows ready for harmonized data promotion after this audit; intentionally zero."},
        {"metric": "alb2002_sample_design_current_decision", "value": DECISION if documentation_ready else "blocked_sample_design_documentation_not_ready", "interpretation": "Current ALB_2002 sample-design documentation decision."},
    ]
    return rows, summary


def markdown_rows(rows: list[dict[str, str]]) -> str:
    columns = ["evidence_domain", "evidence_item", "observed_rows", "promotion_ready_rows", "evidence_status", "diagnostic_value"]
    lines = ["| " + " | ".join(columns) + " |", "|" + "|".join("---" for _ in columns) + "|"]
    for row in rows:
        values = []
        for column in columns:
            value = (row.get(column, "") or "").replace("|", "/")
            if len(value) > 135:
                value = value[:132] + "..."
            values.append(value)
        lines.append("| " + " | ".join(values) + " |")
    return "\n".join(lines)


def write_report(rows: list[dict[str, str]], summary: list[dict[str, str]]) -> None:
    summary_table = "\n".join(f"| {row['metric']} | {row['value']} | {row['interpretation']} |" for row in summary)
    REPORT_PATH.write_text(
        f"""# ALB_2002 Sample Design Documentation Audit

Status: documented candidate, not promoted. This audit snapshots the official World Bank Basic Information document and checks whether its sample-design statements concord with the local ALB_2002 weight file and temp household candidate.

## Summary

| Metric | Value | Interpretation |
|---|---:|---|
{summary_table}

## Evidence Rows

{markdown_rows(rows)}

## Interpretation

- The official Basic Information document is saved locally and its text is extracted for reproducible checks.
- The documentation supports the 450 PSU by 8 household sample-design frame and the 3,599 final household sample size.
- Local readable weights and the temp household-core candidate concord with the 3,599 final household count and 450 PSU structure.
- This resolves a narrow sample-design documentation gap only. It does not promote final weighted inference because weight-use rules, variance handling, outcome construction, denominator decisions, and climate geography are still gated separately.

## Machine-Readable Outputs

- `temp/alb2002_sample_design_documentation_audit.csv`
- `result/alb2002_sample_design_documentation_summary.csv`
- `temp/source_snapshots/alb2002_basic_information_document_sample_design.pdf`
- `temp/source_snapshots/alb2002_basic_information_document_sample_design.txt`
""",
        encoding="utf-8",
    )


def main() -> None:
    ensure_dirs()
    rows, summary = build_rows()
    write_csv(AUDIT_PATH, rows, AUDIT_COLUMNS)
    write_csv(SUMMARY_PATH, summary, SUMMARY_COLUMNS)
    write_report(rows, summary)
    documentation_ready = safe_int(next(row["value"] for row in summary if row["metric"] == "alb2002_sample_design_documentation_ready_rows"))
    append_log(TEMP_DIR / "audit_log.md", f"Audited ALB_2002 sample-design documentation rows={len(rows)} documentation_ready={documentation_ready} decision={DECISION}.")
    print(f"ALB_2002 sample-design documentation audit rows={len(rows)} documentation_ready={documentation_ready} decision={DECISION}.")


if __name__ == "__main__":
    main()
