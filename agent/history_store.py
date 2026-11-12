#!/usr/bin/env python3
"""Persist privacy-safe daily control-center snapshots in the repository."""
from __future__ import annotations

from pathlib import Path
import json
import os
import sys

SOURCE = Path("reports/control-center.json")
HISTORY_ROOT = Path("reports/history/control-center")


def store_snapshot(data: dict, run_id: str, history_root: Path = HISTORY_ROOT) -> Path:
    """Store one snapshot per run, grouped by UTC date; repeated runs are retained."""
    generated_at = str(data.get("generated_at", ""))
    if len(generated_at) < 10 or generated_at[4] != "-" or generated_at[7] != "-":
        raise ValueError("generated_at must begin with an ISO date (YYYY-MM-DD)")
    if not run_id:
        raise ValueError("run_id is required")

    day = generated_at[:10]
    destination = history_root / f"{day}.json"
    document = {"date": day, "snapshots": []}
    if destination.exists():
        document = json.loads(destination.read_text(encoding="utf-8"))
        if document.get("date") != day or not isinstance(document.get("snapshots"), list):
            raise ValueError(f"Invalid history file: {destination}")

    if any(str(item.get("run_id")) == str(run_id) for item in document["snapshots"]):
        return destination

    # Store only aggregate workflow health metadata; never secrets or visitor-level data.
    document["snapshots"].append({
        "run_id": str(run_id),
        "generated_at": generated_at,
        "needs_attention": bool(data.get("needs_attention", False)),
        "results": [
            {
                "name": str(item.get("name", "")),
                "state": str(item.get("state", "unknown")),
                "detail": str(item.get("detail", "")),
                "url": item.get("url"),
                "created_at": item.get("created_at"),
            }
            for item in data.get("results", [])
        ],
    })
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(
        json.dumps(document, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    return destination


def main() -> int:
    if not SOURCE.exists():
        print(f"Control-center JSON not found: {SOURCE}", file=sys.stderr)
        return 1
    try:
        data = json.loads(SOURCE.read_text(encoding="utf-8"))
        path = store_snapshot(data, os.environ.get("GITHUB_RUN_ID", ""))
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(f"Could not persist control-center history: {type(exc).__name__}: {exc}", file=sys.stderr)
        return 1
    print(f"Archived control-center snapshot: {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
