from __future__ import annotations

import csv
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

from common import REPORT_DIR, RESULT_DIR, TEMP_DIR, append_log, ensure_dirs, write_csv


SCOPE_LOCK_PATH = RESULT_DIR / "priority_lsms_isa_dataset_scope_lock.csv"
UNLOCK_BOARD_PATH = RESULT_DIR / "priority_lsms_isa_minimum_batch_promotion_unlock_board.csv"
ENDPOINT_STATUS_PATH = TEMP_DIR / "priority_lsms_isa_minimum_batch_endpoint_dataset_status.csv"
RESOURCE_ROUTE_PATH = TEMP_DIR / "priority_lsms_isa_resource_download_route_probe.csv"
CREDENTIALED_PACKET_PATH = RESULT_DIR / "priority_lsms_isa_credentialed_fetch_command_packet.csv"
BROWSER_STARTER_PATH = RESULT_DIR / "priority_lsms_isa_browser_download_starter.csv"

ROUTE_DECISION_PATH = RESULT_DIR / "priority_lsms_isa_acquisition_route_decision.csv"
ROUTE_EVIDENCE_PATH = RESULT_DIR / "priority_lsms_isa_acquisition_route_evidence.csv"
SUMMARY_PATH = RESULT_DIR / "priority_lsms_isa_acquisition_route_decision_summary.csv"
REPORT_PATH = REPORT_DIR / "priority_lsms_isa_acquisition_route_decision.md"

PRIORITY_COUNTRIES = {"Ethiopia", "Nigeria", "Malawi", "Tanzania", "Uganda"}

DECISION_COLUMNS = [
    "download_rank",
    "country",
    "wave",
    "idno",
    "scope_role",
    "priority_country",
    "sixth_country_candidate",
    "target_file_count",
    "raw_like_file_count",
    "expected_full_file_rows",
    "expected_core_file_rows",
    "endpoint_refresh_status",
    "endpoint_get_microdata_gate_endpoints",
    "endpoint_raw_download_candidate_endpoints",
    "resource_route_rows",
    "resource_raw_payload_candidate_rows",
    "resource_access_gate_rows",
    "resource_http_error_rows",
    "cookie_file_present",
    "header_file_present",
    "credentialed_ready_to_probe",
    "browser_starter_status",
    "acquisition_route_decision",
    "route_decision_reason",
    "official_get_microdata_url",
    "credentialed_download_url",
    "local_target_folder",
    "browser_open_command",
    "prepare_target_folder_command",
    "open_target_folder_command",
    "python_probe_command",
    "python_execute_command",
    "post_download_runner_dry_run_command",
    "post_download_runner_execute_command",
    "post_download_validation_commands",
    "data_write_gate_status",
    "modeling_gate_status",
]

EVIDENCE_COLUMNS = [
    "idno",
    "evidence_source",
    "evidence_metric",
    "evidence_value",
    "interpretation",
]

SUMMARY_COLUMNS = ["metric", "value", "interpretation"]


def read_csv_dicts(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        return []
    with path.open(encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def clean(value: Any) -> str:
    if value is None:
        return ""
    return " ".join(str(value).split())


def safe_int(value: Any, default: int = 0) -> int:
    try:
        text = clean(value)
        return int(float(text)) if text else default
    except (TypeError, ValueError):
        return default


def by_id(rows: list[dict[str, str]]) -> dict[str, dict[str, str]]:
    return {clean(row.get("idno")): row for row in rows if clean(row.get("idno"))}


def resource_counts(rows: list[dict[str, str]]) -> dict[str, Counter[str]]:
    counters: dict[str, Counter[str]] = defaultdict(Counter)
    for row in rows:
        idno = clean(row.get("idno"))
        if not idno:
            continue
        counters[idno]["route_rows"] += 1
        counters[idno]["raw_payload_candidate_rows"] += 1 if clean(row.get("raw_payload_candidate")) == "1" else 0
        counters[idno]["access_gate_rows"] += 1 if clean(row.get("access_gate_detected")) == "1" or clean(row.get("route_classification")) == "resource_access_gate_or_terms_html" else 0
        counters[idno]["data_dictionary_html_rows"] += 1 if clean(row.get("data_dictionary_html_detected")) == "1" else 0
        counters[idno]["http_error_rows"] += 1 if clean(row.get("route_classification")) == "resource_http_error" else 0
        counters[idno]["request_failed_rows"] += 1 if clean(row.get("route_classification")) == "request_failed" else 0
    return counters


def decision_for(
    raw_like_count: int,
    target_file_count: int,
    endpoint_raw_candidates: int,
    resource_raw_candidates: int,
    cookie_present: str,
    header_present: str,
    starter_status: str,
) -> tuple[str, str]:
    if raw_like_count > 0 or target_file_count > 0:
        return (
            "local_files_present_run_post_download_validation",
            "Local non-generated files are present, so receipt/schema/value/semantics validation should run before any promotion.",
        )
    if endpoint_raw_candidates > 0 or resource_raw_candidates > 0:
        return (
            "public_raw_candidate_needs_terms_review",
            "A public route looked like a raw payload candidate, but official terms and complete-package receipt are still required before use.",
        )
    if cookie_present == "1" or header_present == "1":
        return (
            "credentialed_session_available_probe_download_route",
            "Local redacted session material is present, so the credentialed probe can be run without exporting credentials.",
        )
    if starter_status == "ready_for_browser_terms_acceptance":
        return (
            "browser_manual_terms_acceptance_required",
            "Official get-microdata and local target folder commands are ready, but raw files require login/terms acceptance or manual placement.",
        )
    return (
        "blocked_no_current_acquisition_route",
        "No local files, no accepted public raw route, no session material, and no browser starter evidence were found.",
    )


def evidence_row(idno: str, source: str, metric: str, value: Any, interpretation: str) -> dict[str, str]:
    return {
        "idno": idno,
        "evidence_source": source,
        "evidence_metric": metric,
        "evidence_value": str(value),
        "interpretation": interpretation,
    }


def build_outputs() -> tuple[list[dict[str, str]], list[dict[str, str]], list[dict[str, str]]]:
    scope_rows = [row for row in read_csv_dicts(SCOPE_LOCK_PATH) if clean(row.get("download_required")) == "1"]
    unlock_by_id = by_id(read_csv_dicts(UNLOCK_BOARD_PATH))
    endpoint_by_id = by_id(read_csv_dicts(ENDPOINT_STATUS_PATH))
    credentialed_by_id = by_id(read_csv_dicts(CREDENTIALED_PACKET_PATH))
    browser_by_id = by_id(read_csv_dicts(BROWSER_STARTER_PATH))
    route_by_id = resource_counts(read_csv_dicts(RESOURCE_ROUTE_PATH))

    decisions: list[dict[str, str]] = []
    evidence: list[dict[str, str]] = []
    for scope in sorted(scope_rows, key=lambda row: safe_int(row.get("scope_rank"), 9999)):
        idno = clean(scope.get("idno"))
        country = clean(scope.get("country"))
        unlock = unlock_by_id.get(idno, {})
        endpoint = endpoint_by_id.get(idno, {})
        credentialed = credentialed_by_id.get(idno, {})
        browser = browser_by_id.get(idno, {})
        route_counts = route_by_id.get(idno, Counter())

        target_file_count = safe_int(unlock.get("target_file_count"))
        raw_like_count = safe_int(scope.get("raw_like_file_count"))
        endpoint_raw_candidates = safe_int(endpoint.get("raw_download_candidate_endpoints"))
        resource_raw_candidates = safe_int(route_counts.get("raw_payload_candidate_rows"))
        cookie_present = clean(credentialed.get("cookie_file_present"))
        header_present = clean(credentialed.get("header_file_present"))
        starter_status = clean(browser.get("starter_status"))
        ready_to_probe = "1" if cookie_present == "1" or header_present == "1" else "0"
        decision, reason = decision_for(
            raw_like_count=raw_like_count,
            target_file_count=target_file_count,
            endpoint_raw_candidates=endpoint_raw_candidates,
            resource_raw_candidates=resource_raw_candidates,
            cookie_present=cookie_present,
            header_present=header_present,
            starter_status=starter_status,
        )

        decisions.append(
            {
                "download_rank": clean(browser.get("download_rank")) or clean(unlock.get("download_rank")) or clean(scope.get("scope_rank")),
                "country": country,
                "wave": clean(scope.get("wave")),
                "idno": idno,
                "scope_role": clean(scope.get("scope_role")),
                "priority_country": clean(scope.get("priority_country")),
                "sixth_country_candidate": "1" if country not in PRIORITY_COUNTRIES else "0",
                "target_file_count": str(target_file_count),
                "raw_like_file_count": str(raw_like_count),
                "expected_full_file_rows": clean(unlock.get("expected_full_file_rows")),
                "expected_core_file_rows": clean(browser.get("expected_core_file_rows")) or clean(unlock.get("expected_core_file_rows")),
                "endpoint_refresh_status": clean(endpoint.get("endpoint_refresh_status")),
                "endpoint_get_microdata_gate_endpoints": clean(endpoint.get("get_microdata_gate_endpoints")),
                "endpoint_raw_download_candidate_endpoints": str(endpoint_raw_candidates),
                "resource_route_rows": str(route_counts.get("route_rows", 0)),
                "resource_raw_payload_candidate_rows": str(resource_raw_candidates),
                "resource_access_gate_rows": str(route_counts.get("access_gate_rows", 0)),
                "resource_http_error_rows": str(route_counts.get("http_error_rows", 0)),
                "cookie_file_present": cookie_present,
                "header_file_present": header_present,
                "credentialed_ready_to_probe": ready_to_probe,
                "browser_starter_status": starter_status,
                "acquisition_route_decision": decision,
                "route_decision_reason": reason,
                "official_get_microdata_url": clean(scope.get("official_get_microdata_url")) or clean(browser.get("official_get_microdata_url")),
                "credentialed_download_url": clean(browser.get("credentialed_download_url")) or clean(credentialed.get("credentialed_download_url")),
                "local_target_folder": clean(scope.get("local_target_folder")) or clean(browser.get("local_target_folder")),
                "browser_open_command": clean(browser.get("browser_open_command")),
                "prepare_target_folder_command": clean(browser.get("prepare_target_folder_command")) or clean(credentialed.get("prepare_target_folder_command")),
                "open_target_folder_command": clean(browser.get("open_target_folder_command")),
                "python_probe_command": clean(browser.get("python_probe_command")) or clean(credentialed.get("python_probe_command")),
                "python_execute_command": clean(browser.get("python_execute_command")) or clean(credentialed.get("python_execute_command")),
                "post_download_runner_dry_run_command": clean(browser.get("post_download_runner_dry_run_command")),
                "post_download_runner_execute_command": clean(browser.get("post_download_runner_execute_command")),
                "post_download_validation_commands": clean(browser.get("post_download_validation_commands")) or clean(unlock.get("post_download_validation_commands")),
                "data_write_gate_status": "blocked_no_data_write",
                "modeling_gate_status": "blocked",
            }
        )

        evidence.extend(
            [
                evidence_row(idno, "scope_lock", "scope_role", clean(scope.get("scope_role")), "Role in the locked dataset-promotion scope."),
                evidence_row(idno, "scope_lock", "raw_like_file_count", raw_like_count, "Local raw-like file count from the scope/raw-presence evidence."),
                evidence_row(idno, "unlock_board", "target_file_count", target_file_count, "Non-generated files found in the target folder."),
                evidence_row(idno, "endpoint_refresh", "get_microdata_gate_endpoints", clean(endpoint.get("get_microdata_gate_endpoints")), "Official get-microdata endpoint access-gate evidence."),
                evidence_row(idno, "endpoint_refresh", "raw_download_candidate_endpoints", endpoint_raw_candidates, "Raw download candidate endpoints detected by endpoint refresh."),
                evidence_row(idno, "resource_route_probe", "resource_raw_payload_candidate_rows", resource_raw_candidates, "Resource-level route rows that looked like raw payload candidates."),
                evidence_row(idno, "resource_route_probe", "resource_access_gate_rows", route_counts.get("access_gate_rows", 0), "Resource-level route rows with access-gate evidence."),
                evidence_row(idno, "credentialed_packet", "cookie_file_present", cookie_present, "Redacted local cookie-file presence only; credential values are never exported."),
                evidence_row(idno, "credentialed_packet", "header_file_present", header_present, "Redacted local header-file presence only; header values are never exported."),
                evidence_row(idno, "browser_starter", "starter_status", starter_status, "Whether browser/manual terms acceptance commands are ready."),
            ]
        )

    summary = build_summary(decisions)
    return decisions, evidence, summary


def build_summary(decisions: list[dict[str, str]]) -> list[dict[str, str]]:
    status_counts = Counter(clean(row.get("acquisition_route_decision")) for row in decisions)
    countries = {clean(row.get("country")) for row in decisions if clean(row.get("country"))}
    return [
        {"metric": "acquisition_route_decision_rows", "value": str(len(decisions)), "interpretation": "Download-required waves with a consolidated acquisition-route decision."},
        {"metric": "acquisition_route_decision_country_rows", "value": str(len(countries)), "interpretation": "Countries covered by the download-required route decision rows."},
        {"metric": "acquisition_route_decision_priority_country_rows", "value": str(sum(1 for row in decisions if row.get("priority_country") == "1")), "interpretation": "Download-required rows from Ethiopia, Nigeria, Malawi, Tanzania, or Uganda."},
        {"metric": "acquisition_route_decision_sixth_country_rows", "value": str(sum(1 for row in decisions if row.get("sixth_country_candidate") == "1")), "interpretation": "Download-required rows that supply the sixth country."},
        {"metric": "acquisition_route_decision_local_files_present_rows", "value": str(sum(1 for row in decisions if safe_int(row.get("target_file_count")) > 0 or safe_int(row.get("raw_like_file_count")) > 0)), "interpretation": "Rows with local non-generated files ready for validation."},
        {"metric": "acquisition_route_decision_public_raw_candidate_rows", "value": str(sum(1 for row in decisions if safe_int(row.get("endpoint_raw_download_candidate_endpoints")) > 0 or safe_int(row.get("resource_raw_payload_candidate_rows")) > 0)), "interpretation": "Rows with public raw-route candidate evidence requiring terms review."},
        {"metric": "acquisition_route_decision_credentialed_probe_ready_rows", "value": str(sum(1 for row in decisions if row.get("credentialed_ready_to_probe") == "1")), "interpretation": "Rows with local redacted session material available for credentialed probing."},
        {"metric": "acquisition_route_decision_browser_manual_required_rows", "value": str(status_counts.get("browser_manual_terms_acceptance_required", 0)), "interpretation": "Rows whose current route is browser/manual terms acceptance and local file placement."},
        {"metric": "acquisition_route_decision_access_gate_rows", "value": str(sum(1 for row in decisions if safe_int(row.get("endpoint_get_microdata_gate_endpoints")) > 0 or safe_int(row.get("resource_access_gate_rows")) > 0)), "interpretation": "Rows with access-gate evidence from endpoint or resource-route probes."},
        {"metric": "acquisition_route_decision_expected_core_file_rows", "value": str(sum(safe_int(row.get("expected_core_file_rows")) for row in decisions)), "interpretation": "Expected core raw-file rows that will be checked after acquisition."},
        {"metric": "data_write_gate_status", "value": "blocked_no_data_write", "interpretation": "Route decision artifacts do not write promoted data."},
        {"metric": "modeling_gate_status", "value": "blocked", "interpretation": "No predictive, reduced-form, causal ML, or policy learning is opened."},
        *[
            {"metric": f"acquisition_route_decision_status_{status}", "value": str(count), "interpretation": "Acquisition route decision status count."}
            for status, count in sorted(status_counts.items())
        ],
    ]


def markdown_table(rows: list[dict[str, str]], columns: list[str], limit: int = 30) -> str:
    if not rows:
        return "_No rows._"
    lines = ["| " + " | ".join(columns) + " |", "| " + " | ".join("---" for _ in columns) + " |"]
    for row in rows[:limit]:
        values: list[str] = []
        for column in columns:
            value = clean(row.get(column)).replace("|", "/")
            if len(value) > 110:
                value = value[:107] + "..."
            values.append(value)
        lines.append("| " + " | ".join(values) + " |")
    if len(rows) > limit:
        lines.append("| " + " | ".join("..." for _ in columns) + " |")
    return "\n".join(lines)


def write_report(decisions: list[dict[str, str]], summary: list[dict[str, str]]) -> None:
    REPORT_PATH.write_text(
        f"""# Priority LSMS/ISA Acquisition Route Decision

Status: consolidated acquisition-route decision for the 10 download-required
waves in the locked LSMS/ISA dataset-promotion scope.

This artifact does not download, copy, extract, write promoted `data/`, expose
credentials, or run models. It merges official endpoint evidence, resource-
level route probes, redacted session-material presence, browser/manual starter
commands, local target-folder counts, and post-download validation commands.

## Summary

{markdown_table(summary, ['metric', 'value', 'interpretation'], 30)}

## Route Decisions

{markdown_table(decisions, ['download_rank', 'country', 'wave', 'idno', 'acquisition_route_decision', 'target_file_count', 'endpoint_get_microdata_gate_endpoints', 'resource_raw_payload_candidate_rows', 'credentialed_ready_to_probe', 'browser_starter_status'], 20)}

## Immediate Use

Rows with `browser_manual_terms_acceptance_required` should be handled by
opening the official get-microdata URL, accepting official World Bank terms,
placing the complete unchanged package under the listed target folder, and
then running the per-IDNO post-download validation runner.

Rows with local files present should run receipt, schema, value-profile,
semantics, timing/geography, climate-linkage, and promotion-packet gates before
any write into `data/`.

## Stop Rule

No row becomes analysis-ready from this route decision alone. Promotion still
requires complete official raw package receipt, value verification, accepted
outcome construction, survey timing/geography evidence, and CHIRPS or ERA5
climate-linkage acceptance.
""",
        encoding="utf-8",
    )


def main() -> None:
    ensure_dirs()
    decisions, evidence, summary = build_outputs()
    write_csv(ROUTE_DECISION_PATH, decisions, DECISION_COLUMNS)
    write_csv(ROUTE_EVIDENCE_PATH, evidence, EVIDENCE_COLUMNS)
    write_csv(SUMMARY_PATH, summary, SUMMARY_COLUMNS)
    write_report(decisions, summary)
    append_log(TEMP_DIR / "audit_log.md", f"Built priority LSMS/ISA acquisition route decision rows={len(decisions)}.")
    print(f"Priority LSMS/ISA acquisition route decision rows={len(decisions)} evidence_rows={len(evidence)}.")


if __name__ == "__main__":
    main()
