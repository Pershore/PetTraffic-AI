#!/usr/bin/env python3
"""Build a weekly Pet traffic growth review from existing privacy-safe history.

This report is intentionally deterministic: it adds no model/API calls and never
persists raw Search Console phrases or visitor-level information.
"""
from __future__ import annotations

from datetime import datetime, timedelta, timezone
from pathlib import Path
import json
import os
import re
import sys

HISTORY_ROOT = Path("reports/history")
OUT_MD = Path("reports/weekly-growth-review.md")
OUT_JSON = Path("reports/weekly-growth-review.json")
PRIORITY_ORDER = {"high": 0, "medium": 1, "low": 2, "info": 3}
THEME_LABELS = {
    "simptomai_ir_sveikata": "Simptomai ir sveikata",
    "maitinimas_ir_mityba": "Maitinimas ir mityba",
    "veterinarine_pagalba": "Veterinarinė pagalba",
    "prieziura_ir_higiena": "Priežiūra ir higiena",
    "auginimas_ir_elgsena": "Auginimas ir elgsena",
    "kita": "Kitos temos",
}


def parse_time(value: str | None) -> datetime | None:
    if not isinstance(value, str) or not value:
        return None
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None
    return parsed.replace(tzinfo=timezone.utc) if parsed.tzinfo is None else parsed.astimezone(timezone.utc)


def load_snapshots(category: str, history_root: Path = HISTORY_ROOT) -> list[dict]:
    snapshots = []
    folder = history_root / category
    if not folder.exists():
        return snapshots
    for path in sorted(folder.glob("*.json")):
        if path.name == "latest.json":
            continue
        try:
            document = json.loads(path.read_text(encoding="utf-8"))
            values = document.get("snapshots", [])
            if isinstance(values, list):
                snapshots.extend(item for item in values if isinstance(item, dict))
        except (OSError, ValueError, json.JSONDecodeError):
            continue
    return sorted(
        snapshots,
        key=lambda item: parse_time(item.get("generated_at")) or datetime.min.replace(tzinfo=timezone.utc),
    )


def latest_distinct_snapshot(
    snapshots: list[dict], period_key: str, current: dict | None
) -> dict | None:
    if not current:
        return None
    current_period = current.get(period_key)
    current_time = parse_time(current.get("generated_at"))
    if not current_period or not current_time:
        return None
    candidates = []
    for item in snapshots:
        item_time = parse_time(item.get("generated_at"))
        if item.get(period_key) == current_period or not item_time:
            continue
        age = (current_time - item_time).total_seconds() / 86400
        if 5 <= age <= 10:
            candidates.append((abs(age - 7), item_time, item))
    return min(candidates, key=lambda entry: (entry[0], -entry[1].timestamp()))[2] if candidates else None


def latest_snapshot_around_week_ago(snapshots: list[dict], current: dict | None) -> dict | None:
    if not current:
        return None
    current_time = parse_time(current.get("generated_at"))
    if not current_time:
        return None
    candidates = []
    for item in snapshots:
        item_time = parse_time(item.get("generated_at"))
        if not item_time or item_time >= current_time:
            continue
        age = (current_time - item_time).total_seconds() / 86400
        if 5 <= age <= 10:
            candidates.append((abs(age - 7), item_time, item))
    return min(candidates, key=lambda entry: (entry[0], -entry[1].timestamp()))[2] if candidates else None


def latest_per_utc_day(snapshots: list[dict], generated_at: datetime) -> list[dict]:
    recent = {}
    start = generated_at - timedelta(days=7)
    for item in snapshots:
        timestamp = parse_time(item.get("generated_at"))
        if timestamp and start < timestamp <= generated_at:
            day = timestamp.date().isoformat()
            if day not in recent or timestamp > (parse_time(recent[day].get("generated_at")) or timestamp):
                recent[day] = item
    return [recent[key] for key in sorted(recent)]


def safe_number(value) -> float | None:
    return float(value) if isinstance(value, (int, float)) else None


def fmt_number(value: float | int | None, decimals: int = 0) -> str:
    if value is None:
        return "duomenų nėra"
    if decimals:
        return f"{value:,.{decimals}f}".replace(",", " ").replace(".", ",")
    return f"{value:,.0f}".replace(",", " ")


def change_text(current: float | None, previous: float | None, *, percent: bool = True) -> str:
    if current is None or previous is None:
        return "nėra palyginimo duomenų"
    if previous == 0:
        return "0 %" if current == 0 else "nėra palyginimo bazės"
    if percent:
        return f"{(current - previous) / previous * 100:+.1f} %"
    return f"{current - previous:+.1f}"


def analytics_section(snapshots: list[dict]) -> dict:
    current = snapshots[-1] if snapshots else None
    previous_ga = latest_distinct_snapshot(snapshots, "ga4_period", current)
    previous_gsc = latest_distinct_snapshot(snapshots, "search_console_period", current)
    metrics = current.get("metrics", {}) if current else {}
    old_ga = previous_ga.get("metrics", {}) if previous_ga else {}
    old_gsc = previous_gsc.get("metrics", {}) if previous_gsc else {}

    ga4 = {
        "status": current.get("ga4_status", "unknown") if current else "missing",
        "period": current.get("ga4_period") if current else None,
        "baseline_period": previous_ga.get("ga4_period") if previous_ga else None,
        "generated_at": current.get("generated_at") if current else None,
        "metrics": {},
        "top_pages": current.get("ga4_top_pages", [])[:5] if current else [],
    }
    for key in ("active_users", "new_users", "sessions", "page_views", "organic_sessions_verified"):
        ga4["metrics"][key] = {
            "current": safe_number(metrics.get(key)),
            "previous": safe_number(old_ga.get(key)),
            "change": change_text(safe_number(metrics.get(key)), safe_number(old_ga.get(key))),
        }

    gsc = {
        "status": current.get("search_console_status", "unknown") if current else "missing",
        "period": current.get("search_console_period") if current else None,
        "baseline_period": previous_gsc.get("search_console_period") if previous_gsc else None,
        "generated_at": current.get("generated_at") if current else None,
        "metrics": {},
        "sitemap": current.get("search_console_details", {}).get("sitemap", {}) if current else {},
        "priority_url_inspections": current.get("search_console_details", {}).get("priority_url_inspections", []) if current else [],
        "intent_themes": current.get("search_intent_themes", {}) if current else {},
        "top_pages": current.get("search_console_top_pages", [])[:5] if current else [],
    }
    for key in ("search_impressions", "search_clicks", "search_ctr", "average_position"):
        gsc["metrics"][key] = {
            "current": safe_number(metrics.get(key)),
            "previous": safe_number(old_gsc.get(key)),
            "change": change_text(
                safe_number(metrics.get(key)),
                safe_number(old_gsc.get(key)),
                percent=key not in {"search_ctr", "average_position"},
            ),
        }
    if gsc["metrics"]["search_ctr"]["current"] is not None and gsc["metrics"]["search_ctr"]["previous"] is not None:
        current_ctr = gsc["metrics"]["search_ctr"]["current"]
        old_ctr_value = gsc["metrics"]["search_ctr"]["previous"]
        gsc["metrics"]["search_ctr"]["change"] = f"{(current_ctr - old_ctr_value) * 100:+.2f} proc. punkto"
    if gsc["metrics"]["average_position"]["current"] is not None and gsc["metrics"]["average_position"]["previous"] is not None:
        diff = gsc["metrics"]["average_position"]["current"] - gsc["metrics"]["average_position"]["previous"]
        gsc["metrics"]["average_position"]["change"] = f"{diff:+.1f} poz. ({'geriau' if diff < 0 else 'prasčiau' if diff > 0 else 'be pokyčio'})"
    return {"ga4": ga4, "search_console": gsc}


def topic_section(snapshots: list[dict], now: datetime) -> dict:
    recent = latest_per_utc_day(snapshots, now)
    start = now - timedelta(days=7)
    previous = []
    for item in snapshots:
        timestamp = parse_time(item.get("generated_at"))
        if timestamp and now - timedelta(days=14) < timestamp <= start:
            previous.append(item)

    def totals(items: list[dict]) -> dict:
        counts: dict[str, int] = {}
        unique_links = 0
        for item in items:
            for topic, value in (item.get("topic_counts") or {}).items():
                if isinstance(value, (int, float)):
                    counts[topic] = counts.get(topic, 0) + int(value)
            links = item.get("unique_article_links")
            if isinstance(links, (int, float)):
                unique_links += int(links)
        return {"topic_counts": counts, "unique_article_links": unique_links}

    current_totals = totals(recent)
    old_totals = totals(previous)
    comparison = {
        topic: {"current": count, "previous": old_totals["topic_counts"].get(topic)}
        for topic, count in sorted(current_totals["topic_counts"].items(), key=lambda pair: (-pair[1], pair[0]))
    }
    return {
        "source": "Viešų naujienų RSS antraštės; ne Google paieškų apimtis.",
        "days_covered": len({str(item.get("generated_at", ""))[:10] for item in recent}),
        "latest_at": recent[-1].get("generated_at") if recent else None,
        "unique_article_links_sum": current_totals["unique_article_links"] if recent else None,
        "topic_counts": comparison,
    }


def lighthouse_section(snapshots: list[dict]) -> dict:
    current = snapshots[-1] if snapshots else None
    previous = latest_snapshot_around_week_ago(snapshots, current)
    pages = []
    for page in current.get("pages", []) if current else []:
        prior = next((
            item for item in (previous or {}).get("pages", [])
            if item.get("page") == page.get("page") and item.get("device") == page.get("device")
        ), {})
        scores = page.get("scores", {})
        prior_scores = prior.get("scores", {})
        pages.append({
            "page": page.get("page"),
            "device": page.get("device"),
            "path": page.get("path"),
            "scores": {
                key: {"current": scores.get(key), "previous": prior_scores.get(key)}
                for key in ("performance", "accessibility", "best-practices", "seo")
            },
            "vitals": page.get("vitals", {}),
        })
    return {
        "generated_at": current.get("generated_at") if current else None,
        "baseline_at": previous.get("generated_at") if previous else None,
        "pages": pages,
    }


def system_section(history_root: Path) -> dict:
    path = history_root / "project-state" / "latest.json"
    try:
        state = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        state = {}
    return {
        "generated_at": state.get("generated_at"),
        "overall_status": state.get("overall_status", "unknown"),
        "next_action": state.get("next_action"),
        "problems": [
            {"name": item.get("name"), "state": item.get("state"), "detail": item.get("detail")}
            for item in state.get("problems", [])[:5] if isinstance(item, dict)
        ],
        "pending_checks": [
            {"name": item.get("name"), "state": item.get("state"), "detail": item.get("detail")}
            for item in state.get("pending_checks", [])[:5] if isinstance(item, dict)
        ],
        "ai_agent_memory_check": state.get("ai_agent_memory_check"),
    }


def recommendation_section(snapshots: list[dict]) -> list[dict]:
    if not snapshots:
        return []
    latest = snapshots[-1]
    items = latest.get("recommendations", [])
    return sorted(
        [item for item in items if isinstance(item, dict)],
        key=lambda item: (PRIORITY_ORDER.get(str(item.get("priority", "info")), 4), str(item.get("title", ""))),
    )


def build_next_actions(system: dict, recommendations: list[dict], analytics: dict) -> list[dict]:
    actions = []
    seen = set()

    def add(priority: str, title: str, evidence: str, action: str) -> None:
        key = (title or "").strip().lower()
        if not key or key in seen or len(actions) >= 3:
            return
        seen.add(key)
        actions.append({
            "priority": priority,
            "title": title,
            "evidence": evidence,
            "action": action,
        })

    for problem in system.get("problems", []):
        add(
            "high", problem.get("name", "Automatizacijos problema"),
            problem.get("detail", "Valdymo centras nustatė problemą."),
            system.get("next_action") or "Taisyti tik įrodymais patvirtintą problemą.",
        )
    for item in recommendations:
        if len(actions) >= 3:
            break
        add(
            str(item.get("priority", "info")),
            str(item.get("title", "Rekomendacija")),
            str(item.get("evidence", "")),
            str(item.get("next_action", "")),
        )
    gsc_metrics = analytics.get("search_console", {}).get("metrics", {})
    impressions = (gsc_metrics.get("search_impressions") or {}).get("current")
    sitemap = analytics.get("search_console", {}).get("sitemap", {})
    if len(actions) < 3 and impressions == 0 and sitemap.get("is_pending") is True:
        add(
            "medium",
            "Patikrinti indeksavimo ir sitemap būklę",
            "Search Console paskutiniame prieinamame laikotarpyje nerodė parodymų, o sitemap dar laukė apdorojimo.",
            "Patikrinti prioritetinių URL indeksavimo būseną kitame duomenų cikle; sitemap pakartotinai neteikti, jei jis jau pateiktas.",
        )
    if len(actions) < 3 and analytics.get("ga4", {}).get("status") != "available":
        add(
            "high",
            "Atkurti GA4 duomenų rinkimą",
            f"GA4 būklė: {analytics.get('ga4', {}).get('status', 'unknown')}.",
            "Patikrinti tik skaitymo GA4 API prieigą; neinterpretuoti trūkstamų duomenų kaip nulio.",
        )
    return actions


def build_review(
    history_root: Path = HISTORY_ROOT,
    run_id: str = "local",
    generated_at: str | None = None,
) -> dict:
    timestamp = parse_time(generated_at) if generated_at else datetime.now(timezone.utc)
    if timestamp is None:
        raise ValueError("generated_at must be a valid ISO timestamp")
    if not run_id:
        raise ValueError("run_id is required")
    analytics_snapshots = load_snapshots("analytics", history_root)
    topic_snapshots = load_snapshots("topic-radar", history_root)
    lighthouse_snapshots = load_snapshots("lighthouse", history_root)
    control_snapshots = load_snapshots("control-center", history_root)
    recommendation_snapshots = load_snapshots("recommendations", history_root)
    analytics = analytics_section(analytics_snapshots)
    topics = topic_section(topic_snapshots, timestamp)
    lighthouse = lighthouse_section(lighthouse_snapshots)
    system = system_section(history_root)
    recommendations = recommendation_section(recommendation_snapshots)
    actions = build_next_actions(system, recommendations, analytics)
    coverage = {
        "analytics_latest": analytics.get("ga4", {}).get("generated_at"),
        "search_console_latest": analytics.get("search_console", {}).get("generated_at"),
        "topic_radar_latest": topics.get("latest_at"),
        "lighthouse_latest": lighthouse.get("generated_at"),
        "control_center_latest": control_snapshots[-1].get("generated_at") if control_snapshots else None,
        "project_state_latest": system.get("generated_at"),
        "topic_days_covered": topics.get("days_covered", 0),
    }
    return {
        "schema_version": 1,
        "run_id": str(run_id),
        "generated_at": timestamp.isoformat(),
        "reporting_window_days": 7,
        "analytics": analytics,
        "topics": topics,
        "lighthouse": lighthouse,
        "system": system,
        "recommendations": recommendations[:10],
        "next_actions": actions,
        "coverage": coverage,
        "method": "Deterministic analysis of existing aggregated history; no additional AI/API calls.",
        "privacy": "No visitor-level data or raw Search Console phrases are stored in this report.",
    }


def render_markdown(review: dict) -> str:
    analytics = review["analytics"]
    ga4 = analytics["ga4"]
    gsc = analytics["search_console"]
    lines = [
        "# Pet traffic – savaitinė augimo ataskaita",
        "",
        f"- Sugeneruota: {review['generated_at']}",
        f"- Ataskaitos ID: {review['run_id']}",
        "- Metodas: esamų agreguotų duomenų deterministinė analizė; papildomų AI/API kvietimų nėra.",
        "",
        "## Svarbiausi atsakymai",
        "",
    ]
    if ga4["status"] == "available":
        sessions = ga4["metrics"]["sessions"]["current"]
        organic = ga4["metrics"]["organic_sessions_verified"]["current"]
        lines.append(
            f"- **Lankomumas:** {fmt_number(sessions)} sesijų per GA4 laikotarpį "
            f"({ga4['period'] or 'laikotarpis nenurodytas'}); pokytis {ga4['metrics']['sessions']['change']}."
        )
        lines.append(
            "- **Organinė paieška GA4:** "
            + (f"{fmt_number(organic)} patvirtintų sesijų." if organic is not None else "kanalų pasiskirstymas nepatvirtintas.")
        )
    else:
        lines.append(f"- **Lankomumas:** GA4 duomenys nepasiekiami arba jų nėra (būsena: {ga4['status']}).")
    if gsc["status"] == "available":
        lines.append(
            f"- **Google paieška:** {fmt_number(gsc['metrics']['search_impressions']['current'])} parodymų ir "
            f"{fmt_number(gsc['metrics']['search_clicks']['current'])} paspaudimų per {gsc['period'] or 'nenurodytą laikotarpį'}."
        )
    else:
        lines.append(f"- **Google paieška:** Search Console duomenys nepasiekiami arba jų nėra (būsena: {gsc['status']}).")
    lines.append(
        f"- **Techninė / automatizacijų būklė:** {review['system']['overall_status']} "
        f"(projekto būsena atnaujinta: {review['system']['generated_at'] or 'duomenų nėra'})."
    )
    lines += ["", "## GA4 – lankomumas", ""]
    lines.append(f"- Būsena: **{ga4['status']}**")
    lines.append(f"- Laikotarpis: {ga4['period'] or 'duomenų nėra'}")
    lines.append(f"- Palyginimo laikotarpis: {ga4['baseline_period'] or 'duomenų nėra'}")
    lines += ["", "| Rodiklis | Dabartinis 7 d. laikotarpis | Pokytis prieš ankstesnį palyginamą laikotarpį |", "|---|---:|---:|"]
    for key, label in (
        ("active_users", "Aktyvūs naudotojai"),
        ("new_users", "Nauji naudotojai"),
        ("sessions", "Sesijos"),
        ("page_views", "Puslapių peržiūros"),
        ("organic_sessions_verified", "Patvirtintos organinės sesijos"),
    ):
        item = ga4["metrics"][key]
        lines.append(f"| {label} | {fmt_number(item['current'])} | {item['change']} |")
    if ga4["top_pages"]:
        lines += ["", "### Daugiausia peržiūrėti puslapiai", "", "| Puslapis | Peržiūros |", "|---|---:|"]
        lines.extend(f"| {item['path']} | {fmt_number(item.get('views'))} |" for item in ga4["top_pages"])
    else:
        lines += ["", "GA4 populiariausių puslapių duomenų nėra."]
    lines += ["", "## Search Console – Google paieška", ""]
    lines.append(f"- Būsena: **{gsc['status']}**")
    lines.append(f"- Laikotarpis: {gsc['period'] or 'duomenų nėra'} (duomenys gali vėluoti kelias dienas).")
    lines.append(f"- Palyginimo laikotarpis: {gsc['baseline_period'] or 'duomenų nėra'}")
    lines += ["", "| Rodiklis | Dabartinis laikotarpis | Pokytis |", "|---|---:|---:|"]
    for key, label in (
        ("search_impressions", "Parodymai"),
        ("search_clicks", "Paspaudimai"),
        ("search_ctr", "CTR"),
        ("average_position", "Vidutinė pozicija"),
    ):
        item = gsc["metrics"][key]
        if key == "search_ctr":
            value = f"{item['current'] * 100:.2f} %" if item["current"] is not None else "duomenų nėra"
        else:
            value = fmt_number(item["current"], 1 if key == "average_position" else 0)
        lines.append(f"| {label} | {value} | {item['change']} |")
    sitemap = gsc.get("sitemap", {})
    lines += [
        "",
        f"- Sitemap: {sitemap.get('status', 'duomenų nėra')}; apdorojimas laukia: "
        + ("taip" if sitemap.get("is_pending") is True else "ne" if sitemap.get("is_pending") is False else "duomenų nėra"),
    ]
    if gsc["intent_themes"]:
        lines += [
            "",
            "### Apibendrintos paieškos temos",
            "",
            "Paieškos frazės klasifikuojamos tik atmintyje; saugomos tik suvestinės kategorijos, ne pats tekstas.",
            "",
            "| Tema | Frazų eilučių | Parodymai | Paspaudimai |",
            "|---|---:|---:|---:|",
        ]
        for key, item in sorted(gsc["intent_themes"].items(), key=lambda pair: (-pair[1].get("impressions", 0), pair[0])):
            lines.append(
                f"| {THEME_LABELS.get(key, key)} | {fmt_number(item.get('rows'))} | "
                f"{fmt_number(item.get('impressions'))} | {fmt_number(item.get('clicks'))} |"
            )
    else:
        lines += ["", "Apibendrintų paieškos temų duomenų nėra."]
    if gsc["top_pages"]:
        lines += ["", "### Puslapiai Google paieškoje", "", "| Puslapis | Paspaudimai | Parodymai | Pozicija |", "|---|---:|---:|---:|"]
        for item in gsc["top_pages"]:
            lines.append(
                f"| {item['path']} | {fmt_number(item.get('clicks'))} | "
                f"{fmt_number(item.get('impressions'))} | {fmt_number(item.get('average_position'), 1)} |"
            )
    lines += ["", "## Temų radaras – RSS signalai", ""]
    topic_data = review["topics"]
    lines.append(f"- Naujausio rinkimo data: {topic_data.get('latest_at') or 'duomenų nėra'}")
    lines.append(
        f"- Padengta dienų: {topic_data.get('days_covered', 0)} iš 7; unikalių nuorodų suma per surinktus dienos įrašus: "
        f"{fmt_number(topic_data.get('unique_article_links_sum'))}."
    )
    lines.append("- Tai viešų naujienų antraščių signalas, o ne Google paieškų apimtys ar paklausos matavimas.")
    if topic_data.get("topic_counts"):
        lines += ["", "| Tema | Antraštės per surinktas dienas |", "|---|---:|"]
        for key, item in list(topic_data["topic_counts"].items())[:7]:
            lines.append(f"| {key} | {fmt_number(item['current'])} |")
    else:
        lines += ["", "Temų radaro istorijos duomenų nėra."]
    lines += ["", "## Lighthouse – svetainės kokybė", ""]
    lighthouse = review["lighthouse"]
    lines.append(f"- Naujausias auditas: {lighthouse.get('generated_at') or 'duomenų nėra'}")
    lines.append(f"- Ankstesnis palyginamas auditas: {lighthouse.get('baseline_at') or 'duomenų nėra'}")
    if lighthouse["pages"]:
        lines += ["", "| Puslapis / įrenginys | Našumas | Prieinamumas | Praktika | SEO | LCP | TBT | CLS |", "|---|---:|---:|---:|---:|---:|---:|---:|"]
        for page in lighthouse["pages"]:
            scores = page["scores"]
            vitals = page["vitals"]
            lines.append(
                f"| {page['page']} / {page['device']} | "
                f"{fmt_number(scores['performance']['current'])} | "
                f"{fmt_number(scores['accessibility']['current'])} | "
                f"{fmt_number(scores['best-practices']['current'])} | "
                f"{fmt_number(scores['seo']['current'])} | "
                f"{fmt_number(vitals.get('lcp_ms'), 0)} ms | "
                f"{fmt_number(vitals.get('tbt_ms'), 0)} ms | {fmt_number(vitals.get('cls'), 3)} |"
            )
    else:
        lines.append("Lighthouse suvestinės istorijos dar nėra.")
    lines += ["", "## Automatizacijos ir AI agentai", ""]
    system = review["system"]
    lines.append(f"- Projekto būsena: **{system['overall_status']}**.")
    lines.append(f"- Paskutinis būsenos įrašas: {system.get('generated_at') or 'duomenų nėra'}.")
    if system.get("ai_agent_memory_check"):
        item = system["ai_agent_memory_check"]
        lines.append(f"- AI agentai / Control Core: **{item.get('state', 'unknown')}** – {item.get('detail', '')}")
    if system["problems"]:
        lines += ["", "### Aktyvios problemos", ""]
        lines.extend(f"- **{item.get('name')}** ({item.get('state')}): {item.get('detail')}" for item in system["problems"])
    else:
        lines += ["", "Patikrintoje paskutinėje Control Center suvestinėje problemų neužfiksuota."]
    if system["pending_checks"]:
        lines += ["", "### Laukiančios patikros", ""]
        lines.extend(f"- {item.get('name')}: {item.get('detail')}" for item in system["pending_checks"])
    lines += ["", "## Trys svarbiausi kiti veiksmai", ""]
    if review["next_actions"]:
        for index, item in enumerate(review["next_actions"], 1):
            lines += [
                f"{index}. **[{item['priority'].upper()}] {item['title']}**",
                f"   - Įrodymai: {item['evidence'] or 'Papildomi įrodymai dar renkami.'}",
                f"   - Veiksmas: {item['action'] or 'Peržiūrėti ir patvirtinti rekomendaciją.'}",
            ]
    else:
        lines.append("Pagal turimus duomenis nėra pakankamai įrodymų naujam veiksmui parinkti; tęsti matavimą.")
    lines += [
        "",
        "## Duomenų aprėptis ir ribos",
        "",
        f"- GA4 paskutinis duomenų rinkimas: {review['coverage']['analytics_latest'] or 'duomenų nėra'}.",
        f"- Search Console paskutinis duomenų rinkimas: {review['coverage']['search_console_latest'] or 'duomenų nėra'}.",
        f"- RSS temų radaro paskutinis duomenų rinkimas: {review['coverage']['topic_radar_latest'] or 'duomenų nėra'}.",
        f"- Lighthouse paskutinis duomenų rinkimas: {review['coverage']['lighthouse_latest'] or 'duomenų nėra'}.",
        f"- Control Center paskutinis įrašas: {review['coverage']['control_center_latest'] or 'duomenų nėra'}.",
        "",
        review["method"],
        review["privacy"],
        "Nulinė reikšmė rodoma tik tada, kai šaltinis ją tikrai pateikė. Trūkstamas / pasenęs šaltinis žymimas „duomenų nėra“ ir nėra interpretuojamas kaip nulis.",
        "Ataskaita yra analizės pagalbininkė, o ne leidimas keisti ar publikuoti viešą svetainės turinį.",
        "",
    ]
    return "\n".join(lines)


def persist_review(review: dict, markdown: str, history_root: Path = HISTORY_ROOT) -> tuple[Path, Path, Path]:
    day = str(review.get("generated_at", ""))[:10]
    if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", day):
        raise ValueError("generated_at must begin with an ISO date (YYYY-MM-DD)")
    folder = history_root / "weekly-review"
    daily = folder / f"{day}.json"
    document = {"date": day, "snapshots": []}
    if daily.exists():
        document = json.loads(daily.read_text(encoding="utf-8"))
        if document.get("date") != day or not isinstance(document.get("snapshots"), list):
            raise ValueError(f"Invalid weekly review history file: {daily}")
    if not any(str(item.get("run_id")) == str(review["run_id"]) for item in document["snapshots"]):
        document["snapshots"].append(review)
    folder.mkdir(parents=True, exist_ok=True)
    daily.write_text(json.dumps(document, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    latest_json = folder / "latest.json"
    latest_md = folder / "latest.md"
    latest_json.write_text(json.dumps(review, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    latest_md.write_text(markdown, encoding="utf-8")
    return daily, latest_json, latest_md


def main() -> int:
    run_id = os.environ.get("GITHUB_RUN_ID", "")
    if not run_id:
        print("GITHUB_RUN_ID is required.", file=sys.stderr)
        return 1
    try:
        review = build_review(run_id=run_id)
        markdown = render_markdown(review)
        OUT_MD.parent.mkdir(parents=True, exist_ok=True)
        OUT_MD.write_text(markdown, encoding="utf-8")
        OUT_JSON.write_text(json.dumps(review, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        history_paths = persist_review(review, markdown)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(f"Could not build weekly growth review: {type(exc).__name__}: {exc}", file=sys.stderr)
        return 1
    print(f"Generated weekly growth review; archived: {', '.join(str(path) for path in history_paths)}")
    print(markdown)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
