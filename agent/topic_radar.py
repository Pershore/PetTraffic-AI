#!/usr/bin/env python3
"""Daily Lithuanian pet-topic radar using public Google News RSS feeds.

This script collects public article headlines only. It does not identify visitors,
collect personal data, or claim that headline volume equals search volume.
"""
from __future__ import annotations

from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
from pathlib import Path
from urllib.parse import quote
from urllib.request import Request, urlopen
import html
import xml.etree.ElementTree as ET

TOPICS = [
    "šunų priežiūra",
    "kačių priežiūra",
    "augintinių mityba",
    "šunų dantų priežiūra",
    "kačių dantų priežiūra",
    "augintinio ženklinimas registravimas Lietuva",
    "augintinio sveikata veterinaras",
]
OUT = Path("reports/topic-radar.md")


def fetch(topic: str) -> list[dict[str, str]]:
    query = quote(topic)
    url = (
        "https://news.google.com/rss/search?q=" + query
        + "+when%3A30d&hl=lt&gl=LT&ceid=LT%3Alt"
    )
    request = Request(url, headers={"User-Agent": "PetTrafficAI-TopicRadar/1.0"})
    try:
        with urlopen(request, timeout=20) as response:
            payload = response.read()
    except Exception as exc:
        print(f"WARNING: RSS nepavyko ({topic}): {exc}")
        return []

    try:
        root = ET.fromstring(payload)
    except ET.ParseError:
        print(f"WARNING: netaisyklingas RSS ({topic})")
        return []

    items = []
    for item in root.findall("./channel/item")[:8]:
        title = html.unescape((item.findtext("title") or "").strip())
        link = (item.findtext("link") or "").strip()
        source = (item.findtext("source") or "").strip()
        pub = (item.findtext("pubDate") or "").strip()
        if not title or not link:
            continue
        try:
            published = parsedate_to_datetime(pub).astimezone(timezone.utc).strftime("%Y-%m-%d")
        except Exception:
            published = "data nenurodyta"
        items.append({
            "title": title,
            "link": link,
            "source": source,
            "published": published,
        })
    return items


def main() -> int:
    OUT.parent.mkdir(parents=True, exist_ok=True)
    generated = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    sections = [
        "# PetTraffic AI – kasdienių temų radaras",
        "",
        f"Atnaujinta: {generated}",
        "",
        "> Tai viešų naujienų antraščių stebėsena, o ne Google paieškų apimčių ar svetainės lankytojų statistika. Prieš rengiant straipsnį būtina atskirai patikrinti pirminius šaltinius ir veterinarinius teiginius.",
        "",
    ]
    total = 0
    for topic in TOPICS:
        entries = fetch(topic)
        total += len(entries)
        sections.extend([f"## {topic}", ""])
        if not entries:
            sections.extend(["_Šį kartą patikimų RSS rezultatų negauta._", ""])
            continue
        for entry in entries:
            source = f" — {entry['source']}" if entry["source"] else ""
            sections.append(
                f"- [{entry['title']}]({entry['link']}) "
                f"({entry['published']}{source})"
            )
        sections.append("")
    sections.extend([
        "## Kaip naudoti šią ataskaitą",
        "",
        "1. Ieškoti pasikartojančių klausimų ir temų keliuose nepriklausomuose šaltiniuose.",
        "2. Pirmenybę teikti temoms, kurios sprendžia konkretų šeimininko klausimą.",
        "3. Veterinarinius patarimus tikrinti pagal klinikines gaires ir patikimus veterinarijos šaltinius.",
        "4. Prieš publikuojant patikrinti, ar tema jau nėra išsamiai aprašyta PetTraffic AI svetainėje.",
        "5. Nenaudoti antraščių skaičiaus kaip paieškos apimties ar lankytojų skaičiaus pakaitalo.",
        "",
        f"Rezultatų antraščių skaičius: **{total}**",
    ])
    OUT.write_text("\n".join(sections) + "\n", encoding="utf-8")
    print(f"Topic radar created: {OUT} ({total} headlines)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
