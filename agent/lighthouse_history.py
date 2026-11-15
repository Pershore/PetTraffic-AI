#!/usr/bin/env python3
"""Persist privacy-safe aggregate Lighthouse scores for the weekly review."""
from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlsplit
import glob
import json
import os
import re
import sys

HISTORY_ROOT = Path("reports/history/lighthouse")
CATEGORIES = ("performance", "accessibility", "best-practices", "seo")
VITALS = (
    ("first-contentful-paint", "fcp_ms"),
    ("largest-contentful-paint", "lcp_ms"),
    ("total-blocking-time", "tbt_ms"),
    ("cumulative-layout-shift", "cls"),
    ("speed-index", "speed_index_ms"),
)


def score(data: dict, category: str) -> int | None:
    value = data.get("categories", {}).get(category, {}).get("score")
    return round(value * 100) if isinstance(value, (int, float)) else None


def page_path(data: dict) -> str | None:
    raw = data.get("finalDisplayedUrl") or data.get("requestedUrl") or ""
    try:
        path = urlsplit(str(raw)).path
    except ValueError:
        return None
    return path[:300] if path.startswith("/") else None


def page_result(filename: str, data: dict) -> dict:
    name = Path(filename).name
    if name.endswith(".report.json"):
        name = name[:-len(".report.json")]
    page, separator, device = name.rpartition("-")
    if not separator:
        page, device = name, "unknown"
    audits = data.get("audits", {})
    vitals = {}
    for audit_key, output_key in VITALS:
        value = audits.get(audit_key, {}).get("numericValue")
        vitals[output_key] = round(value, 3) if isinstance(value, (int, float)) else None
    return {
        "page": page[:100],
        "device": device[:20],
        "path": page_path(data),
        "scores": {category: score(data, category) for category in CATEGORIES},
        "vitals": vitals,
    }


def build_snapshot(files: list[str], run_id: str, generated_at: str | None = None) -> dict:
    if not run_id:
        raise ValueError("run_id is required")
    pages = []
    for filename in sorted(files):
        data = json.loads(Path(filename).read_text(encoding="utf-8"))
        pages.append(page_result(filename, data))
    if not pages:
        raise ValueError("No Lighthouse JSON reports were found")
    return {
        "run_id": str(run_id),
        "generated_at": generated_at or datetime.now(timezone.utc).isoformat(),
        "page_count": len(pages),
        "pages": pages,
        "privacy": "Aggregate category scores and Core Web Vitals only; no full audit payloads.",
    }


def store_snapshot(snapshot: dict, history_root: Path = HISTORY_ROOT) -> Path:
    day = str(snapshot.get("generated_at", ""))[:10]
    if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", day):
        raise ValueError("generated_at must begin with an ISO date (YYYY-MM-DD)")
    run_id = str(snapshot.get("run_id", ""))
    if not run_id:
        raise ValueError("run_id is required")
    destination = history_root / f"{day}.json"
    document = {"date": day, "snapshots": []}
    if destination.exists():
        document = json.loads(destination.read_text(encoding="utf-8"))
        if document.get("date") != day or not isinstance(document.get("snapshots"), list):
            raise ValueError(f"Invalid Lighthouse history file: {destination}")
    if not any(str(item.get("run_id")) == run_id for item in document["snapshots"]):
        document["snapshots"].append(snapshot)
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(json.dumps(document, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return destination


def main() -> int:
    files = sorted(glob.glob("reports/*.report.json"))
    try:
        snapshot = build_snapshot(files, os.environ.get("GITHUB_RUN_ID", ""))
        path = store_snapshot(snapshot)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(f"Could not persist Lighthouse history: {type(exc).__name__}: {exc}", file=sys.stderr)
        return 1
    print(f"Archived aggregate Lighthouse snapshot: {path} ({snapshot['page_count']} pages)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
