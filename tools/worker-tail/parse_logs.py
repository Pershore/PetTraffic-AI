#!/usr/bin/env python3
"""Summarize Wrangler tail JSON without printing request headers or payloads."""
from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any


def as_dict(value: Any) -> dict:
    return value if isinstance(value, dict) else {}


def event_type(entry: dict) -> str:
    raw_event = entry.get("event")
    if isinstance(raw_event, str):
        return raw_event
    event = as_dict(raw_event)
    workers = as_dict(entry.get("$workers")) or as_dict(entry.get("workers"))
    metadata = as_dict(entry.get("$metadata"))
    return str(
        workers.get("eventType")
        or workers.get("event_type")
        or metadata.get("eventType")
        or event.get("type")
        or entry.get("eventType")
        or ""
    )


def is_scheduled(entry: dict) -> bool:
    event = as_dict(entry.get("event"))
    scheduled = as_dict(
        event.get("scheduled")
        or event.get("scheduledEvent")
        or entry.get("scheduled")
    )
    kind = event_type(entry).lower()
    return (
        kind in {"scheduled", "cron"}
        or bool(event.get("cron") or event.get("scheduledTime") or event.get("scheduled_time"))
        or bool(scheduled.get("cron") or scheduled.get("scheduledTime") or scheduled.get("scheduled_time"))
    )


def load_entries(path: Path) -> list[dict]:
    entries: list[dict] = []
    for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
        try:
            item = json.loads(line)
        except json.JSONDecodeError:
            continue
        if isinstance(item, dict):
            entries.append(item)
    return entries


def summarize(entries: list[dict]) -> tuple[list[dict], list[dict]]:
    cron_entries = [entry for entry in entries if is_scheduled(entry)]
    failures = [
        entry
        for entry in cron_entries
        if as_dict(entry).get("exceptions")
        or str(as_dict(entry).get("outcome") or "").lower() in {"exception", "error", "failure"}
    ]
    return cron_entries, failures


def main() -> int:
    if len(sys.argv) != 2:
        print("Usage: parse_logs.py PATH")
        return 2
    path = Path(sys.argv[1])
    entries = load_entries(path)
    cron_entries, failures = summarize(entries)
    print(f"Total structured Worker invocations observed: {len(entries)}")
    print(f"Cron/scheduled invocations observed: {len(cron_entries)}")
    for entry in cron_entries[-10:]:
        event = as_dict(entry.get("event"))
        scheduled = as_dict(event.get("scheduled") or event.get("scheduledEvent") or entry.get("scheduled"))
        workers = as_dict(entry.get("$workers")) or as_dict(entry.get("workers"))
        print(json.dumps({
            "event_type": event_type(entry),
            "cron": event.get("cron") or event.get("schedule") or scheduled.get("cron"),
            "event_timestamp": entry.get("eventTimestamp") or entry.get("timestamp"),
            "outcome": entry.get("outcome") or workers.get("outcome"),
            "exceptions": len(entry.get("exceptions") or []) if isinstance(entry.get("exceptions") or [], list) else 1,
            "logs": len(entry.get("logs") or []) if isinstance(entry.get("logs") or [], list) else 0,
        }, ensure_ascii=False))
    if not cron_entries:
        print("Recent event shapes (keys only; values and headers omitted):")
        for entry in entries[-10:]:
            event = as_dict(entry.get("event"))
            workers = as_dict(entry.get("$workers")) or as_dict(entry.get("workers"))
            print(json.dumps({
                "top_keys": sorted(entry.keys()),
                "event_type": event_type(entry),
                "event_raw_type": type(entry.get("event")).__name__,
                "event_keys": sorted(event.keys()),
                "worker_keys": sorted(workers.keys()),
            }, ensure_ascii=False))
        print("No Cron Trigger invocation was observed during the 17-minute capture window.")
        return 1
    if failures:
        print(f"At least one Cron Trigger invocation reported an exception or failure ({len(failures)}).")
        return 1
    print("Cron Trigger invocation(s) observed without reported exceptions.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
