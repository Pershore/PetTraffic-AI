#!/usr/bin/env python3
"""Write a concise Markdown summary from Lighthouse JSON reports."""
from __future__ import annotations

import glob
import json
import os
import sys
from pathlib import Path

CATEGORIES = ("performance", "accessibility", "best-practices", "seo")
LABELS = {
    "performance": "Performance",
    "accessibility": "Accessibility",
    "best-practices": "Best practices",
    "seo": "SEO",
}


def main() -> int:
    reports = sorted(glob.glob("reports/*.report.json"))
    if not reports:
        print("No Lighthouse JSON reports were created.", file=sys.stderr)
        return 1

    rows = []
    for filename in reports:
        try:
            data = json.loads(Path(filename).read_text(encoding="utf-8"))
            scores = data.get("categories", {})
            values = []
            for key in CATEGORIES:
                score = scores.get(key, {}).get("score")
                values.append("—" if score is None else str(round(score * 100)))
            rows.append((Path(filename).name.replace(".report.json", ""), values))
        except (OSError, json.JSONDecodeError, TypeError) as exc:
            print(f"Could not parse {filename}: {exc}", file=sys.stderr)
            return 1

    lines = [
        "## Lighthouse site audit",
        "",
        "Scores are out of 100. This first baseline records results without failing the build on fluctuating lab scores.",
        "",
        "| Page / device | Performance | Accessibility | Best practices | SEO |",
        "|---|---:|---:|---:|---:|",
    ]
    for name, values in rows:
        lines.append("| " + name + " | " + " | ".join(values) + " |")
    lines += [
        "",
        "Full HTML and JSON reports are attached to this workflow run as the `lighthouse-reports` artifact.",
        "Use repeated runs to establish a stable baseline before adding score thresholds.",
        "",
    ]
    summary_path = os.environ.get("GITHUB_STEP_SUMMARY")
    if summary_path:
        with open(summary_path, "a", encoding="utf-8") as output:
            output.write("\n".join(lines))
    print("\n".join(lines))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
