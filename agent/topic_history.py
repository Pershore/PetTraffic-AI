#!/usr/bin/env python3
"""Persist daily topic-radar aggregates without archiving article content."""
from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
import json
import os
import re
import sys

REPORT = Path("reports/topic-radar.md")
HISTORY_ROOT = Path("reports/history/topic-radar")


def parse_report(report: str, run_id: str, generated_at: str | None = None) -> dict:
    if not run_id:
        raise ValueError("run_id is required")
    counts = {}
    for line in report.splitlines():
        match = re.match(r"^- \*\*(.+?)\*\* – (\d+) antraščių$", line.strip())
        if match:
            counts[match.group(1)] = int(match.group(2))
    unique = re.search(r"Unikalių straipsnių nuorodų:\s*\*\*(\d+)\*\*", report)
    empty = re.search(r"Temų užklausų be rezultatų:\s*\*\*(\d+) iš (\d+)\*\*", report)
    timestamp = generated_at or datetime.now(timezone.utc).isoformat()
    return {
        "run_id": str(run_id),
        "generated_at": timestamp,
        "source": "Google News RSS public headlines; not Google search volume",
        "topic_counts": counts,
        "unique_article_links": int(unique.group(1)) if unique else None,
        "empty_topic_checks": int(empty.group(1)) if empty else None,
        "total_topic_checks": int(empty.group(2)) if empty else None,
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
            raise ValueError(f"Invalid history file: {destination}")
    if not any(str(item.get("run_id")) == run_id for item in document["snapshots"]):
        document["snapshots"].append(snapshot)
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(json.dumps(document, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return destination


def main() -> int:
    if not REPORT.exists():
        print(f"Topic-radar report not found: {REPORT}", file=sys.stderr)
        return 1
    try:
        report = REPORT.read_text(encoding="utf-8")
        snapshot = parse_report(report, os.environ.get("GITHUB_RUN_ID", ""))
        path = store_snapshot(snapshot)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(f"Could not persist topic-radar history: {type(exc).__name__}: {exc}", file=sys.stderr)
        return 1
    print(f"Archived topic-radar aggregate snapshot: {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
