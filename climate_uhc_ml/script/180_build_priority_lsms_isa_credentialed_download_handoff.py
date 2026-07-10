from __future__ import annotations

import argparse
import csv
import hashlib
import http.cookiejar
import re
from email.message import Message
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

import requests

from common import PROJECT_ROOT, REPORT_DIR, RESULT_DIR, TEMP_DIR, append_log, ensure_dirs, write_csv


BOARD_PATH = TEMP_DIR / "priority_lsms_isa_manual_download_execution_board.csv"
SESSION_DIR = TEMP_DIR / "private"
COOKIE_PATH = SESSION_DIR / "worldbank_session_cookies.txt"
HEADER_PATH = SESSION_DIR / "worldbank_session_headers.txt"

PLAN_PATH = TEMP_DIR / "priority_lsms_isa_credentialed_download_handoff_plan.csv"
LOG_PATH = TEMP_DIR / "priority_lsms_isa_credentialed_download_handoff_log.csv"
SUMMARY_PATH = RESULT_DIR / "priority_lsms_isa_credentialed_download_handoff_summary.csv"
REPORT_PATH = REPORT_DIR / "priority_lsms_isa_credentialed_download_handoff.md"

USER_AGENT = "Codex climate_uhc_ml World Bank credentialed download handoff"
TIMEOUT = 90
MAX_PROBE_BYTES = 512 * 1024
RAW_CONTENT_HINTS = ("application/zip", "application/x-zip", "application/x-7z", "application/rar", "application/octet-stream")
RAW_SUFFIXES = {".zip", ".7z", ".rar", ".tar", ".gz", ".tgz", ".dta", ".sav", ".por", ".xpt", ".sas7bdat"}
HTML_HINTS = ("text/html", "application/xhtml")
GATE_HINTS = ("login", "log in", "sign in", "register", "terms", "data access agreement", "licensed", "request access")

PLAN_COLUMNS = [
    "download_rank",
    "country",
    "wave",
    "idno",
    "catalog_id",
    "official_get_microdata_url",
    "credentialed_download_url",
    "local_target_folder",
    "run_mode",
    "cookie_file_present",
    "header_file_present",
    "request_attempted",
    "response_classification",
    "http_status",
    "final_url",
    "content_type",
    "content_length_header",
    "content_disposition",
    "bytes_read_or_saved",
    "content_sha256_limited",
    "saved_path",
    "next_action",
    "data_write_gate_status",
    "modeling_gate_status",
]

LOG_COLUMNS = [
    "download_rank",
    "idno",
    "request_url",
    "request_attempted",
    "http_status",
    "response_classification",
    "bytes_read_or_saved",
    "content_sha256_limited",
    "saved_path",
    "error",
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


def catalog_id_from_url(url: str) -> str:
    match = re.search(r"/catalog/(\d+)", clean(url))
    return match.group(1) if match else ""


def download_url(catalog_id: str) -> str:
    return f"https://microdata.worldbank.org/catalog/{catalog_id}/download" if catalog_id else ""


def resolve_project_path(path_text: str) -> Path:
    text = clean(path_text).replace("\\", "/")
    path = Path(text)
    if path.is_absolute():
        return path
    return PROJECT_ROOT / text


def parse_headers_file(path: Path) -> dict[str, str]:
    if not path.exists():
        return {}
    headers: dict[str, str] = {}
    for line in path.read_text(encoding="utf-8", errors="ignore").splitlines():
        text = line.strip()
        if not text or text.startswith("#") or ":" not in text:
            continue
        key, value = text.split(":", 1)
        key = key.strip()
        value = value.strip()
        if not key or key.lower() in {"host", "content-length"}:
            continue
        headers[key] = value
    return headers


def load_cookie_file(session: requests.Session, path: Path) -> bool:
    if not path.exists():
        return False
    text = path.read_text(encoding="utf-8", errors="ignore").strip()
    if not text:
        return True
    if "Cookie:" in text or ("\t" not in text and "=" in text and ";" in text):
        cookie_line = text
        if "Cookie:" in cookie_line:
            cookie_line = cookie_line.split("Cookie:", 1)[1]
        for part in cookie_line.split(";"):
            if "=" not in part:
                continue
            key, value = part.split("=", 1)
            session.cookies.set(key.strip(), value.strip(), domain=".worldbank.org")
        return True
    jar = http.cookiejar.MozillaCookieJar(str(path))
    try:
        jar.load(ignore_discard=True, ignore_expires=True)
    except (http.cookiejar.LoadError, OSError):
        return True
    session.cookies.update(jar)
    return True


def make_session() -> tuple[requests.Session, bool, bool]:
    session = requests.Session()
    session.headers.update({"User-Agent": USER_AGENT})
    header_present = HEADER_PATH.exists()
    headers = parse_headers_file(HEADER_PATH)
    headers.pop("Cookie", None)
    headers.pop("cookie", None)
    session.headers.update(headers)
    cookie_present = load_cookie_file(session, COOKIE_PATH)
    return session, cookie_present, header_present


def sha256_bytes(content: bytes) -> str:
    return hashlib.sha256(content).hexdigest() if content else ""


def suffix_from_disposition(disposition: str) -> str:
    match = re.search(r'filename="?([^";]+)"?', disposition, flags=re.IGNORECASE)
    if not match:
        return ""
    return Path(match.group(1)).suffix.lower()


def filename_from_disposition(disposition: str) -> str:
    match = re.search(r'filename="?([^";]+)"?', disposition, flags=re.IGNORECASE)
    if not match:
        return ""
    return re.sub(r"[^A-Za-z0-9._-]+", "_", match.group(1)).strip("._")


def response_is_raw(url: str, content_type: str, disposition: str) -> bool:
    low_type = content_type.lower()
    low_disp = disposition.lower()
    parsed_suffix = Path(urlparse(url).path).suffix.lower()
    disp_suffix = suffix_from_disposition(disposition)
    return (
        parsed_suffix in RAW_SUFFIXES
        or disp_suffix in RAW_SUFFIXES
        or any(hint in low_type for hint in RAW_CONTENT_HINTS)
        or ("attachment" in low_disp and not any(hint in low_type for hint in HTML_HINTS))
    )


def classify_response(url: str, response: requests.Response, probe_content: bytes) -> str:
    content_type = response.headers.get("content-type", "")
    disposition = response.headers.get("content-disposition", "")
    if response.status_code >= 400:
        return "http_error_no_download"
    if response_is_raw(response.url or url, content_type, disposition):
        return "credentialed_raw_payload_detected"
    low_text = probe_content.decode(response.encoding or "utf-8", errors="replace").lower() if probe_content else ""
    if any(hint in content_type.lower() for hint in HTML_HINTS) and any(hint in low_text for hint in GATE_HINTS):
        return "access_gate_or_terms_html_returned"
    if any(hint in content_type.lower() for hint in HTML_HINTS):
        return "html_returned_not_raw_payload"
    if not probe_content:
        return "empty_response_no_download"
    return "non_raw_response_needs_manual_review"


def read_probe_content(response: requests.Response) -> tuple[bytes, int]:
    chunks: list[bytes] = []
    total = 0
    for chunk in response.iter_content(chunk_size=64 * 1024):
        if not chunk:
            continue
        remaining = MAX_PROBE_BYTES - total
        if remaining <= 0:
            break
        if len(chunk) > remaining:
            chunks.append(chunk[:remaining])
            total += remaining
            break
        chunks.append(chunk)
        total += len(chunk)
    content = b"".join(chunks)
    return content, len(content)


def safe_output_name(idno: str, response: requests.Response, url: str) -> str:
    from_disp = filename_from_disposition(response.headers.get("content-disposition", ""))
    if from_disp:
        return from_disp
    suffix = Path(urlparse(response.url or url).path).suffix.lower()
    if suffix not in RAW_SUFFIXES:
        content_type = response.headers.get("content-type", "").lower()
        suffix = ".zip" if "zip" in content_type else ".bin"
    return f"{idno}_worldbank_credentialed_download{suffix}"


def attempt_download(
    session: requests.Session,
    row: dict[str, str],
    mode: str,
    cookie_present: bool,
    header_present: bool,
) -> tuple[dict[str, str], dict[str, str]]:
    catalog_id = catalog_id_from_url(row.get("official_get_microdata_url", ""))
    url = download_url(catalog_id)
    base = {
        "download_rank": clean(row.get("download_rank")),
        "country": clean(row.get("country")),
        "wave": clean(row.get("wave")),
        "idno": clean(row.get("idno")),
        "catalog_id": catalog_id,
        "official_get_microdata_url": clean(row.get("official_get_microdata_url")),
        "credentialed_download_url": url,
        "local_target_folder": clean(row.get("local_target_folder")),
        "run_mode": mode,
        "cookie_file_present": "1" if cookie_present else "0",
        "header_file_present": "1" if header_present else "0",
        "request_attempted": "0",
        "response_classification": "",
        "http_status": "",
        "final_url": "",
        "content_type": "",
        "content_length_header": "",
        "content_disposition": "",
        "bytes_read_or_saved": "0",
        "content_sha256_limited": "",
        "saved_path": "",
        "next_action": "",
        "data_write_gate_status": "blocked_no_data_write",
        "modeling_gate_status": "blocked",
    }
    log = {
        "download_rank": base["download_rank"],
        "idno": base["idno"],
        "request_url": url,
        "request_attempted": "0",
        "http_status": "",
        "response_classification": "",
        "bytes_read_or_saved": "0",
        "content_sha256_limited": "",
        "saved_path": "",
        "error": "",
    }
    if not cookie_present and not header_present:
        base["response_classification"] = "blocked_missing_worldbank_session"
        base["next_action"] = "Create temp/private/worldbank_session_cookies.txt or temp/private/worldbank_session_headers.txt from a logged-in World Bank Microdata browser session, then rerun with --probe."
        log["response_classification"] = base["response_classification"]
        return base, log
    if mode == "dry_run":
        base["response_classification"] = "dry_run_session_present_not_attempted"
        base["next_action"] = "Run with --probe to test the credentialed /download response without saving raw files."
        log["response_classification"] = base["response_classification"]
        return base, log

    base["request_attempted"] = "1"
    log["request_attempted"] = "1"
    try:
        with session.get(url, stream=True, timeout=TIMEOUT, allow_redirects=True) as response:
            probe_content, read_bytes = read_probe_content(response)
            classification = classify_response(url, response, probe_content)
            base.update(
                {
                    "response_classification": classification,
                    "http_status": str(response.status_code),
                    "final_url": response.url,
                    "content_type": response.headers.get("content-type", ""),
                    "content_length_header": response.headers.get("content-length", ""),
                    "content_disposition": response.headers.get("content-disposition", ""),
                    "bytes_read_or_saved": str(read_bytes),
                    "content_sha256_limited": sha256_bytes(probe_content),
                }
            )
            if mode == "execute" and classification == "credentialed_raw_payload_detected":
                target = resolve_project_path(base["local_target_folder"])
                target.mkdir(parents=True, exist_ok=True)
                out_path = target / safe_output_name(base["idno"], response, url)
                with out_path.open("wb") as f:
                    f.write(probe_content)
                    for chunk in response.iter_content(chunk_size=1024 * 1024):
                        if chunk:
                            f.write(chunk)
                saved_bytes = out_path.stat().st_size
                base["bytes_read_or_saved"] = str(saved_bytes)
                base["saved_path"] = str(out_path.relative_to(PROJECT_ROOT)).replace("\\", "/")
                base["next_action"] = "Run scripts 177 and 178 dry-run, then execute post-download validation if the packet is ready."
            elif mode == "execute":
                base["next_action"] = "No raw payload saved. Complete/accept World Bank terms in browser or inspect the returned page, then retry."
            else:
                base["next_action"] = "Probe only; no raw payload saved. Use --execute only if the response classification is credentialed_raw_payload_detected."
    except requests.RequestException as exc:
        base["response_classification"] = "request_failed"
        base["next_action"] = "Retry after confirming session cookies/headers are current."
        log["error"] = str(exc)
    log.update(
        {
            "http_status": base["http_status"],
            "response_classification": base["response_classification"],
            "bytes_read_or_saved": base["bytes_read_or_saved"],
            "content_sha256_limited": base["content_sha256_limited"],
            "saved_path": base["saved_path"],
        }
    )
    return base, log


def summary_row(metric: str, value: Any, interpretation: str) -> dict[str, str]:
    return {"metric": metric, "value": str(value), "interpretation": interpretation}


def build_summary(plan_rows: list[dict[str, str]], mode: str, cookie_present: bool, header_present: bool) -> list[dict[str, str]]:
    def count_status(status: str) -> int:
        return sum(1 for row in plan_rows if row.get("response_classification") == status)

    saved_rows = [row for row in plan_rows if clean(row.get("saved_path"))]
    rows = [
        summary_row("credentialed_download_handoff_mode", mode, "Runner mode for this invocation."),
        summary_row("credentialed_download_handoff_rows", len(plan_rows), "Minimum-batch credentialed download handoff rows."),
        summary_row("credentialed_download_handoff_cookie_file_present", "1" if cookie_present else "0", "Whether temp/private/worldbank_session_cookies.txt exists and was loaded."),
        summary_row("credentialed_download_handoff_header_file_present", "1" if header_present else "0", "Whether temp/private/worldbank_session_headers.txt exists and was loaded."),
        summary_row("credentialed_download_handoff_request_attempted_rows", sum(1 for row in plan_rows if row.get("request_attempted") == "1"), "Rows where the credentialed download URL was requested."),
        summary_row("credentialed_download_handoff_raw_payload_detected_rows", count_status("credentialed_raw_payload_detected"), "Rows where response headers looked like a raw downloadable payload."),
        summary_row("credentialed_download_handoff_saved_raw_file_rows", len(saved_rows), "Rows where --execute saved a raw payload into the target folder."),
        summary_row("credentialed_download_handoff_missing_session_rows", count_status("blocked_missing_worldbank_session"), "Rows blocked because no local World Bank session file was present."),
        summary_row("credentialed_download_handoff_access_gate_rows", count_status("access_gate_or_terms_html_returned"), "Rows where World Bank still returned login/terms HTML."),
        summary_row("data_write_gate_status", "blocked_no_data_write", "Credentialed download handoff never writes promoted analysis data."),
        summary_row("modeling_gate_status", "blocked", "No predictive, reduced-form, causal ML, or policy learning until registry thresholds pass."),
    ]
    statuses = sorted({clean(row.get("response_classification")) for row in plan_rows if clean(row.get("response_classification"))})
    for status in statuses:
        rows.append(summary_row(f"credentialed_download_handoff_status_{status}", count_status(status), "Handoff row count by response classification."))
    return rows


def markdown_table(rows: list[dict[str, str]], columns: list[str], limit: int = 20) -> str:
    if not rows:
        return "_No rows._"
    lines = ["| " + " | ".join(columns) + " |", "| " + " | ".join("---" for _ in columns) + " |"]
    for row in rows[:limit]:
        lines.append("| " + " | ".join(clean(row.get(column)).replace("|", "/") for column in columns) + " |")
    if len(rows) > limit:
        lines.append("| " + " | ".join("..." for _ in columns) + " |")
    return "\n".join(lines)


def write_report(plan_rows: list[dict[str, str]], summary_rows: list[dict[str, str]]) -> None:
    metric = {row["metric"]: row["value"] for row in summary_rows}
    lines = [
        "# Priority LSMS-ISA Credentialed Download Handoff",
        "",
        "Status: local-only World Bank get-microdata session handoff. It can use",
        "`temp/private/worldbank_session_cookies.txt` or",
        "`temp/private/worldbank_session_headers.txt` from a browser session to probe",
        "the official `/download` routes for the 10 remaining minimum-batch packets.",
        "",
        "No credential values are written to this report. `temp/private/` is ignored by git.",
        "",
        "Default mode is dry-run. Use `--probe` to test authenticated responses without",
        "saving raw files. Use `--execute` only after the official terms have been accepted",
        "in the browser session; raw files are saved only when the response looks like a",
        "downloadable raw payload.",
        "",
        "It does not extract archives, write promoted `data/`, or run models.",
        "",
        "## Summary",
        "",
        f"- Mode: {metric.get('credentialed_download_handoff_mode', 'dry_run')}",
        f"- Rows: {metric.get('credentialed_download_handoff_rows', '0')}",
        f"- Cookie file present: {metric.get('credentialed_download_handoff_cookie_file_present', '0')}",
        f"- Header file present: {metric.get('credentialed_download_handoff_header_file_present', '0')}",
        f"- Requests attempted: {metric.get('credentialed_download_handoff_request_attempted_rows', '0')}",
        f"- Raw payload detected rows: {metric.get('credentialed_download_handoff_raw_payload_detected_rows', '0')}",
        f"- Saved raw file rows: {metric.get('credentialed_download_handoff_saved_raw_file_rows', '0')}",
        f"- Missing-session rows: {metric.get('credentialed_download_handoff_missing_session_rows', '0')}",
        f"- Access-gate rows: {metric.get('credentialed_download_handoff_access_gate_rows', '0')}",
        "",
        "## Handoff Plan",
        "",
        markdown_table(
            plan_rows,
            [
                "download_rank",
                "country",
                "wave",
                "idno",
                "run_mode",
                "request_attempted",
                "response_classification",
                "saved_path",
                "next_action",
            ],
            limit=20,
        ),
        "",
        "## Local Session Files",
        "",
        "- `temp/private/worldbank_session_cookies.txt`: Netscape cookies export or a raw `Cookie:` header from a logged-in World Bank Microdata browser session.",
        "- `temp/private/worldbank_session_headers.txt`: optional header lines such as `User-Agent: ...`; do not commit this file.",
        "",
        "## Commands",
        "",
        "```bash",
        "python script/180_build_priority_lsms_isa_credentialed_download_handoff.py",
        "python script/180_build_priority_lsms_isa_credentialed_download_handoff.py --probe",
        "python script/180_build_priority_lsms_isa_credentialed_download_handoff.py --execute",
        "```",
        "",
        "## Outputs",
        "",
        "- `temp/priority_lsms_isa_credentialed_download_handoff_plan.csv`",
        "- `temp/priority_lsms_isa_credentialed_download_handoff_log.csv`",
        "- `result/priority_lsms_isa_credentialed_download_handoff_summary.csv`",
        "",
        "## Stop Rule",
        "",
        "This handoff only helps acquire official raw packages. Promotion remains blocked",
        "until receipt, schema, value-profile, semantics, timing/geography, and climate",
        "linkage gates pass.",
    ]
    REPORT_PATH.write_text("\n".join(lines) + "\n", encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build or run a local World Bank credentialed download handoff.")
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--probe", action="store_true", help="Probe credentialed /download routes without saving raw files.")
    mode.add_argument("--execute", action="store_true", help="Save raw payloads when authenticated /download responses look like raw packages.")
    return parser.parse_args()


def main() -> None:
    ensure_dirs()
    args = parse_args()
    mode = "execute" if args.execute else "probe" if args.probe else "dry_run"
    board_rows = read_csv_dicts(BOARD_PATH)
    session, cookie_present, header_present = make_session()
    plan_rows: list[dict[str, str]] = []
    log_rows: list[dict[str, str]] = []
    for row in sorted(board_rows, key=lambda r: safe_int(r.get("download_rank"), 9999)):
        plan, log = attempt_download(session, row, mode, cookie_present, header_present)
        plan_rows.append(plan)
        log_rows.append(log)
    summary_rows = build_summary(plan_rows, mode, cookie_present, header_present)
    write_csv(PLAN_PATH, plan_rows, PLAN_COLUMNS)
    write_csv(LOG_PATH, log_rows, LOG_COLUMNS)
    write_csv(SUMMARY_PATH, summary_rows, SUMMARY_COLUMNS)
    write_report(plan_rows, summary_rows)
    append_log(TEMP_DIR / "audit_log.md", f"Built priority LSMS/ISA credentialed download handoff mode={mode} rows={len(plan_rows)}.")
    saved = sum(1 for row in plan_rows if clean(row.get("saved_path")))
    attempted = sum(1 for row in plan_rows if row.get("request_attempted") == "1")
    print(f"Priority LSMS/ISA credentialed download handoff complete: mode={mode}, attempted={attempted}, saved={saved}")


if __name__ == "__main__":
    main()
