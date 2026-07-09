from __future__ import annotations

import csv
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = PROJECT_ROOT / "data"
SCRIPT_DIR = PROJECT_ROOT / "script"
RESULT_DIR = PROJECT_ROOT / "result"
REPORT_DIR = PROJECT_ROOT / "report"
TEMP_DIR = PROJECT_ROOT / "temp"
SNAPSHOT_DIR = TEMP_DIR / "source_snapshots"


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def ensure_dirs() -> None:
    for path in [
        DATA_DIR,
        SCRIPT_DIR,
        RESULT_DIR,
        REPORT_DIR,
        TEMP_DIR,
        SNAPSHOT_DIR,
        TEMP_DIR / "raw_downloads",
        TEMP_DIR / "raw_schema_inventory",
        TEMP_DIR / "logs",
        TEMP_DIR / "api_cache",
    ]:
        path.mkdir(parents=True, exist_ok=True)


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def write_csv(path: Path, rows: Iterable[dict[str, Any]], fieldnames: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        for row in rows:
            writer.writerow({k: row.get(k, "") for k in fieldnames})


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, obj: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, ensure_ascii=False, indent=2), encoding="utf-8")


def append_log(path: Path, message: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as f:
        f.write(f"- {utc_now_iso()} - {message}\n")


def text_contains_any(text: str, needles: Iterable[str]) -> bool:
    low = text.lower()
    return any(n.lower() in low for n in needles)


def compact_text(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, str):
        return " ".join(value.split())
    if isinstance(value, list):
        return " ".join(compact_text(v) for v in value)
    if isinstance(value, dict):
        return " ".join(f"{k}: {compact_text(v)}" for k, v in value.items())
    return str(value)
