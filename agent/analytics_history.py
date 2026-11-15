#!/usr/bin/env python3
"""Extract privacy-safe aggregate GA4 and Search Console metrics for history."""
from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
import json
import os
import re
import sys
from urllib.parse import urlsplit
import unicodedata

REPORT = Path("reports/analytics-7d.md")
HISTORY_ROOT = Path("reports/history/analytics")


def table_value(report: str, label: str) -> str | None:
    for line in report.splitlines():
        if line.strip().startswith("|"):
            cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
            if len(cells) >= 2 and cells[0] == label:
                return cells[1]
    return None


def number(value: str | None, percent: bool = False) -> float | None:
    if value is None or value.strip().lower() in {"", "–", "-", "duomenų nėra", "nepatvirtinta"}:
        return None
    cleaned = value.replace("%", "").replace(" ", "").replace(",", ".")
    match = re.search(r"-?\d+(?:\.\d+)?", cleaned)
    if not match:
        return None
    parsed = float(match.group())
    return parsed / 100 if percent else parsed


def page_path(value: str) -> str | None:
    """Keep only a public URL path; discard query strings and fragments."""
    raw = value.strip()
    if not raw:
        return None
    try:
        parsed = urlsplit(raw)
        path = parsed.path if parsed.scheme or parsed.netloc else raw.split("?", 1)[0].split("#", 1)[0]
    except ValueError:
        return None
    if not path.startswith("/"):
        return None
    return path[:300]


def parse_ga4_top_pages(report: str) -> list[dict]:
    marker = "### Daugiausia peržiūrėti puslapiai (GA4)"
    if marker not in report:
        return []
    section = report.split(marker, 1)[1].split("## Google paieška", 1)[0]
    pages = []
    for line in section.splitlines():
        match = re.match(r"^\s*-\s+(.+?)\s+–\s+([\d ]+)\s+peržiūrų\s*$", line)
        if not match:
            continue
        path = page_path(match.group(1))
        views = number(match.group(2))
        if path is not None and views is not None:
            pages.append({"path": path, "views": views})
    return pages[:10]


def fold_text(value: str) -> str:
    normalized = unicodedata.normalize("NFKD", value.casefold())
    return "".join(char for char in normalized if not unicodedata.combining(char))


def classify_search_intent(value: str) -> str:
    """Classify a phrase transiently; the phrase itself is never persisted."""
    folded = fold_text(value)
    patterns = (
        ("simptomai_ir_sveikata", r"viduri|vem|slapin|krauj|kos|niez|niez|skausm|simptom|alerg"),
        ("maitinimas_ir_mityba", r"maist|ed(al|el)|pasar|maitin|mityb|dieta|svor|skanest"),
        ("veterinarine_pagalba", r"veterinar|klinika|skubi|gydytoj|kada kreiptis|konsult"),
        ("prieziura_ir_higiena", r"prieziur|dant|kail|higien|aus|nag|kraik|maud"),
        ("auginimas_ir_elgsena", r"suniuk|kaciuk|veisle|augin|dres|elges|socializ"),
    )
    for category, pattern in patterns:
        if re.search(pattern, folded):
            return category
    return "kita"


def parse_search_intent_themes(report: str) -> dict:
    """Persist aggregate categories only; never store raw Search Console phrases."""
    marker = "### Populiariausios Google paieškos užklausos"
    if marker not in report:
        return {}
    section = report.split(marker, 1)[1].split("### Puslapiai Google paieškoje", 1)[0]
    groups: dict[str, dict] = {}
    for line in section.splitlines():
        stripped = line.strip()
        if not stripped.startswith("|"):
            continue
        cells = stripped.strip("|").rsplit("|", 4)
        if len(cells) != 5:
            continue
        phrase, clicks_raw, impressions_raw, ctr_raw, position_raw = [cell.strip() for cell in cells]
        if phrase in {"Užklausa", "---"} or set(phrase) <= {"-", ":"}:
            continue
        clicks = number(clicks_raw)
        impressions = number(impressions_raw)
        ctr = number(ctr_raw, percent=True)
        position = number(position_raw)
        if clicks is None or impressions is None:
            continue
        category = classify_search_intent(phrase)
        item = groups.setdefault(category, {
            "rows": 0, "clicks": 0.0, "impressions": 0.0,
            "position_impressions": 0.0, "ctr": None,
        })
        item["rows"] += 1
        item["clicks"] += clicks
        item["impressions"] += impressions
        if position is not None:
            item["position_impressions"] += position * impressions
    for item in groups.values():
        item["ctr"] = item["clicks"] / item["impressions"] if item["impressions"] else None
        item["average_position"] = (
            item["position_impressions"] / item["impressions"]
            if item["impressions"] else None
        )
        item.pop("position_impressions", None)
    return groups


def parse_search_console_top_pages(report: str) -> list[dict]:
    marker = "### Puslapiai Google paieškoje"
    if marker not in report:
        return []
    section = report.split(marker, 1)[1].split("### Svetainės žemėlapis", 1)[0]
    pages = []
    for line in section.splitlines():
        stripped = line.strip()
        if not stripped.startswith("|"):
            continue
        cells = stripped.strip("|").split("|")
        if len(cells) != 5 or cells[0].strip() in {"Puslapis", "---"}:
            continue
        path = page_path(cells[0].strip())
        clicks = number(cells[1])
        impressions = number(cells[2])
        ctr = number(cells[3], percent=True)
        position = number(cells[4])
        if path is not None and clicks is not None and impressions is not None:
            pages.append({
                "path": path, "clicks": clicks, "impressions": impressions,
                "ctr": ctr, "average_position": position,
            })
    return pages[:10]


def parse_report(report: str, run_id: str, generated_at: str | None = None) -> dict:
    if not run_id:
        raise ValueError("run_id is required")
    timestamp = generated_at or datetime.now(timezone.utc).isoformat()
    ga_period = re.search(r"^GA4 laikotarpis:\s*(.+)$", report, re.MULTILINE)
    gsc_period = re.search(r"^Laikotarpis:\s*(.+)$", report, re.MULTILINE)
    ga_present = "## Pagrindiniai rodikliai (GA4)" in report
    if "Būsena: neprijungta" in report:
        ga_status = "not_connected"
    elif "Būsena: klaida" in report:
        ga_status = "error"
    elif "GA4 duomenų gauti nepavyko" in report:
        ga_status = "unavailable"
    else:
        ga_status = "available" if ga_present else "unknown"

    if "Duomenų gauti nepavyko" in report:
        gsc_status = "unavailable"
    elif "## Google paieška (Search Console)" in report:
        gsc_status = "available"
    else:
        gsc_status = "unknown"

    organic = re.search(r"Organinės paieškos sesijos:\s*\*\*(\d[\d ]*)\*\*", report)
    metrics = {
        "active_users": number(table_value(report, "Aktyvūs naudotojai")),
        "new_users": number(table_value(report, "Nauji naudotojai")),
        "sessions": number(table_value(report, "Sesijos / apsilankymai")),
        "page_views": number(table_value(report, "Puslapių peržiūros")),
        "organic_sessions_verified": number(organic.group(1)) if organic else None,
        "search_impressions": number(table_value(report, "Paieškos parodymai")),
        "search_clicks": number(table_value(report, "Paspaudimai")),
        "search_ctr": number(table_value(report, "CTR"), percent=True),
        "average_position": number(table_value(report, "Vidutinė pozicija")),
    }
    return {
        "run_id": str(run_id),
        "generated_at": timestamp,
        "ga4_status": ga_status,
        "ga4_period": ga_period.group(1).strip() if ga_period else None,
        "search_console_status": gsc_status,
        "search_console_period": gsc_period.group(1).strip() if gsc_period else None,
        "search_console_details": {
            "sitemap": parse_sitemap_details(report),
            "priority_url_inspections": parse_priority_url_inspections(report),
        },
        "metrics": metrics,
        "ga4_top_pages": parse_ga4_top_pages(report),
        "search_intent_themes": parse_search_intent_themes(report),
        "search_console_top_pages": parse_search_console_top_pages(report),
    }


def parse_sitemap_details(report: str) -> dict:
    """Extract only aggregate sitemap processing metadata from the report."""
    marker = "### Svetainės žemėlapis (Search Console)"
    if marker not in report:
        return {"status": "unknown"}
    section = report.split(marker, 1)[1].split("### Google indekso būklė", 1)[0]
    if "**Nepateiktas:**" in section:
        status = "not_submitted"
    elif "Būsena: **pateiktas**" in section:
        status = "submitted"
    elif "Pateikimo būsenos patikrinti nepavyko" in section:
        status = "error"
    else:
        status = "unknown"

    path_match = re.search(r"(?:Būsena: \*\*pateiktas\*\*|\*\*Nepateiktas\*\*):? ?\(([^)]+)\)", section)
    submitted_match = re.search(r"Paskutinį kartą pateiktas:\s*([^\n]+)", section)
    downloaded_match = re.search(r"Google paskutinį kartą atsisiuntė:\s*([^\n]+)", section)
    counts_match = re.search(r"URL pateikta / indeksuota:\s*(\d+)\s*/\s*(\d+)", section)
    pending_match = re.search(r"Laukia apdorojimo:\s*(taip|ne)", section, re.IGNORECASE)
    return {
        "status": status,
        "path": path_match.group(1).strip() if path_match else None,
        "last_submitted": submitted_match.group(1).strip() if submitted_match else None,
        "last_downloaded": downloaded_match.group(1).strip() if downloaded_match else None,
        "submitted_urls": int(counts_match.group(1)) if counts_match else None,
        "indexed_urls": int(counts_match.group(2)) if counts_match else None,
        "is_pending": pending_match.group(1).lower() == "taip" if pending_match else None,
    }


def parse_priority_url_inspections(report: str) -> list[dict]:
    """Extract the small allow-listed priority URL index-state table."""
    marker = "### Google indekso būklė (svarbiausi puslapiai)"
    if marker not in report:
        return []
    section = report.split(marker, 1)[1].split("## Mokama reklama", 1)[0]
    inspections = []
    for line in section.splitlines():
        if not line.strip().startswith("|"):
            continue
        cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
        if len(cells) != 6 or cells[0] in {"Puslapis", "---"} or all(set(cell) <= {"-", ":"} for cell in cells):
            continue
        inspections.append({
            "url_path": cells[0],
            "verdict": cells[1],
            "coverage": cells[2],
            "robots_txt_state": cells[3],
            "indexing_state": cells[4],
            "last_crawl": cells[5],
        })
    return inspections


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
        print(f"Analytics report not found: {REPORT}", file=sys.stderr)
        return 1
    try:
        report = REPORT.read_text(encoding="utf-8")
        snapshot = parse_report(report, os.environ.get("GITHUB_RUN_ID", ""))
        path = store_snapshot(snapshot)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(f"Could not persist analytics history: {type(exc).__name__}: {exc}", file=sys.stderr)
        return 1
    print(f"Archived aggregate analytics snapshot: {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
