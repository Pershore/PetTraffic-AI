#!/usr/bin/env python3
"""Summarize Lighthouse scores, Core Web Vitals and actionable diagnostics."""
from __future__ import annotations
import glob
import json
import os
import sys
from pathlib import Path

CATEGORIES = ("performance", "accessibility", "best-practices", "seo")
VITALS = (
    ("first-contentful-paint", "FCP", "s"),
    ("largest-contentful-paint", "LCP", "s"),
    ("total-blocking-time", "TBT", "ms"),
    ("cumulative-layout-shift", "CLS", ""),
    ("speed-index", "Speed Index", "s"),
)
OPPORTUNITIES = (
    "render-blocking-resources", "uses-responsive-images",
    "modern-image-formats", "unused-css-rules", "unused-javascript",
    "uses-text-compression", "uses-rel-preload", "server-response-time",
)

def fmt_metric(audits: dict, key: str, unit: str) -> str:
    value = audits.get(key, {}).get("numericValue")
    if value is None:
        return "—"
    if unit == "s":
        return f"{value / 1000:.2f} s"
    if unit == "ms":
        return f"{value:.0f} ms"
    return f"{value:.3f}"

def score_value(data: dict, key: str) -> str:
    score = data.get("categories", {}).get(key, {}).get("score")
    return "—" if score is None else str(round(score * 100))

def _lcp_node(audit: dict) -> str | None:
    for group in audit.get("details", {}).get("items", []):
        for item in group.get("items", []):
            node = item.get("node", {})
            label = node.get("nodeLabel") or node.get("snippet")
            if label:
                return str(label).strip().replace("\n", " ")[:110]
    return None

def insights(name: str, data: dict) -> list[str]:
    audits = data.get("audits", {})
    lines = [f"### {name}", ""]
    vitals = [f"{label}: {fmt_metric(audits, key, unit)}" for key, label, unit in VITALS]
    lines.append("- **Rodikliai:** " + " · ".join(vitals))

    mainthread = audits.get("mainthread-work-breakdown", {}).get("details", {}).get("items", [])
    if mainthread:
        largest = sorted(mainthread, key=lambda item: item.get("duration", 0), reverse=True)[:3]
        parts = [f"{item.get('groupLabel', item.get('group', 'Kita'))} {item.get('duration', 0):.0f} ms" for item in largest]
        lines.append("- **Pagrindinės gijos darbas:** " + "; ".join(parts))

    lcp_audit = audits.get("largest-contentful-paint-element", {})
    node = _lcp_node(lcp_audit)
    phases = []
    for group in lcp_audit.get("details", {}).get("items", []):
        for item in group.get("items", []):
            if item.get("phase") and item.get("timing") is not None:
                phases.append(f"{item['phase']} {item['timing']:.0f} ms ({item.get('percent', '?')})")
    if node:
        lines.append("- **LCP elementas:** " + node)
    if phases:
        lines.append("- **LCP etapai:** " + "; ".join(phases))

    opportunities = []
    for key in OPPORTUNITIES:
        audit = audits.get(key, {})
        details = audit.get("details", {})
        ms = details.get("overallSavingsMs") or 0
        byte_count = details.get("overallSavingsBytes") or 0
        if ms or byte_count:
            label = audit.get("title", key)
            savings = []
            if ms:
                savings.append(f"~{ms:.0f} ms")
            if byte_count:
                savings.append(f"~{byte_count / 1024:.0f} KiB")
            opportunities.append((ms + byte_count / 1000, label, ", ".join(savings)))
    for _, label, savings in sorted(opportunities, reverse=True)[:3]:
        lines.append(f"- **Galima optimizacija:** {label} – {savings}")

    long_tasks = audits.get("long-tasks", {}).get("details", {}).get("items", [])
    if long_tasks:
        top = sorted(long_tasks, key=lambda item: item.get("duration", 0), reverse=True)[:3]
        details = [f"{item.get('duration', 0):.0f} ms ({'nepriskirta' if item.get('url') == 'Unattributable' else 'puslapis'})" for item in top]
        lines.append("- **Ilgos užduotys:** " + "; ".join(details))
    lines.append("")
    return lines

def build_summary(reports: list[tuple[str, dict]]) -> str:
    lines = [
        "## Lighthouse svetainės auditas", "",
        "Balai pateikiami iš 100. Našumo balas gali svyruoti tarp paleidimų, todėl sprendimus grįskite ir Web Vitals bei konkrečiais diagnostikos duomenimis.", "",
        "| Puslapis / įrenginys | Našumas | Prieinamumas | Geriausia praktika | SEO |",
        "|---|---:|---:|---:|---:|",
    ]
    for name, data in reports:
        values = [score_value(data, key) for key in CATEGORIES]
        lines.append("| " + name + " | " + " | ".join(values) + " |")
    priority = [(name, data) for name, data in reports if name.endswith("-mobile") or score_value(data, "performance") not in {"—", "100"}]
    if priority:
        lines += ["", "## Veikimo diagnostika", ""]
        for name, data in priority:
            lines.extend(insights(name, data))
    lines += [
        "Pilnos HTML ir JSON ataskaitos saugomos šio vykdymo lighthouse-reports artefakte.",
        "Nekeiskite kodo vien pagal vieną svyruojantį balą: pirmiausia patikrinkite konkretų LCP/TBT/CLS rodiklį ir pakartokite matavimą.", "",
    ]
    return "\n".join(lines)

def main() -> int:
    filenames = sorted(glob.glob("reports/*.report.json"))
    if not filenames:
        print("No Lighthouse JSON reports were created.", file=sys.stderr)
        return 1
    reports = []
    for filename in filenames:
        try:
            data = json.loads(Path(filename).read_text(encoding="utf-8"))
            reports.append((Path(filename).name.replace(".report.json", ""), data))
        except (OSError, json.JSONDecodeError, TypeError) as exc:
            print(f"Could not parse {filename}: {exc}", file=sys.stderr)
            return 1
    summary = build_summary(reports)
    summary_path = os.environ.get("GITHUB_STEP_SUMMARY")
    if summary_path:
        with open(summary_path, "a", encoding="utf-8") as output:
            output.write(summary)
    print(summary)
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
