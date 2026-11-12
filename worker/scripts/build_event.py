#!/usr/bin/env python3
"""Build privacy-safe event payloads from existing GitHub Actions artifacts."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from agent.analytics_history import parse_report as parse_analytics_report
from agent.topic_history import parse_report as parse_topic_report


def find_file(root: Path, filename: str) -> Path:
    matches = sorted(root.rglob(filename))
    if not matches:
        raise FileNotFoundError(f"Artifact file not found: {filename}")
    return matches[0]


def control_payload(data: dict, run_id: str) -> dict:
    return {
        "run_id": str(run_id),
        "generated_at": data.get("generated_at"),
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
    }


def build_events(workflow_name: str, artifact_dir: Path, run_id: str) -> list[dict]:
    if not run_id:
        raise ValueError("run_id is required")
    if workflow_name == "Pet traffic analytics snapshot":
        report = find_file(artifact_dir, "analytics-7d.md").read_text(encoding="utf-8")
        snapshot = parse_analytics_report(report, run_id)
        return [{"kind": "analytics_snapshot", "payload": snapshot}]
    if workflow_name == "Pet traffic daily topic radar":
        report = find_file(artifact_dir, "topic-radar.md").read_text(encoding="utf-8")
        snapshot = parse_topic_report(report, run_id)
        return [{"kind": "topic_snapshot", "payload": snapshot}]
    if workflow_name == "Pet traffic central control center":
        control = json.loads(find_file(artifact_dir, "control-center.json").read_text(encoding="utf-8"))
        events = [{
            "kind": "control_center_snapshot",
            "payload": control_payload(control, run_id),
        }]
        recommendation_path = next(iter(sorted(artifact_dir.rglob("recommendations.json"))), None)
        if recommendation_path:
            recommendations = json.loads(recommendation_path.read_text(encoding="utf-8"))
            events.append({
                "kind": "recommendation_snapshot",
                "payload": {
                    "run_id": str(run_id),
                    "generated_at": recommendations.get("generated_at"),
                    "recommendations": recommendations.get("recommendations", []),
                },
            })
        return events
    raise ValueError(f"Unsupported workflow: {workflow_name}")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--workflow-name", required=True)
    parser.add_argument("--artifact-dir", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--run-id", required=True)
    args = parser.parse_args()
    events = build_events(args.workflow_name, args.artifact_dir, args.run_id)
    args.output_dir.mkdir(parents=True, exist_ok=True)
    for index, event in enumerate(events, start=1):
        path = args.output_dir / f"event-{index}.json"
        path.write_text(json.dumps(event, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Prepared {len(events)} privacy-filtered event(s).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
