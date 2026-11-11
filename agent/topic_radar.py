#!/usr/bin/env python3
"""Daily Lithuanian pet-topic radar using public Google News RSS feeds.

This collects public headlines only. It does not identify visitors or claim
that headline counts equal Google search volume.
"""
from __future__ import annotations

from collections import defaultdict
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
from pathlib import Path
from urllib.parse import quote, urlsplit, urlunsplit
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
PER_TOPIC_LIMIT = 8


def clean_link(link: str) -> str:
    """Remove tracking query/fragment so the same article is counted once."""
    parts = urlsplit(link.strip())
    return urlunsplit((parts.scheme, parts.netloc, parts.path, "", ""))


def fetch(topic: str) -> list[dict[str, str]]:
    url = (
        "https://news.google.com/rss/search?q=" + quote(topic)
        + "+when%3A30d&hl=lt&gl=LT&ceid=LT%3Alt"
    )
    request = Request(url, headers={"User-Agent": "PetTrafficAI-TopicRadar/1.0"})
    try:
        with urlopen(request, timeout=20) as response:
            payload = response.read()
    except Exception as exc:
        print(f"WARNING: RSS nepavyko ({topic}): {type(exc).__name__}: {exc}")
        return []

    try:
        root = ET.fromstring(payload)
    except ET.ParseError:
        print(f"WARNING: netaisyklingas RSS ({topic})")
        return []

    items: list[dict[str, str]] = []
    for item in root.findall("./channel/item")[:PER_TOPIC_LIMIT]:
        title = html.unescape((item.findtext("title") or "").strip())
        link = clean_link(item.findtext("link") or "")
        source = (item.findtext("source") or "").strip()
        pub = (item.findtext("pubDate") or "").strip()
        if not title or not link:
            continue
        try:
            parsed = parsedate_to_datetime(pub)
            if parsed.tzinfo is None:
                parsed = parsed.replace(tzinfo=timezone.utc)
            published = parsed.astimezone(timezone.utc).strftime("%Y-%m-%d")
        except (TypeError, ValueError, OverflowError):
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

    unique: dict[str, dict[str, str | set[str]]] = {}
    topic_counts: dict[str, int] = {}
    failed_topics: list[str] = []

    for topic in TOPICS:
        entries = fetch(topic)
        topic_counts[topic] = len(entries)
        if not entries:
            failed_topics.append(topic)
        for entry in entries:
            key = entry["link"]
            if key not in unique:
                unique[key] = {
                    **entry,
                    "topics": {topic},
                }
            else:
                unique[key]["topics"].add(topic)  # type: ignore[union-attr]

    sections.extend(["## Temos pagal surinktų antraščių skaičių", ""])
    for topic, count in sorted(topic_counts.items(), key=lambda pair: (-pair[1], pair[0])):
        sections.append(f"- **{topic}** – {count} antraščių")

    sections.extend([
        "",
        f"Unikalių straipsnių nuorodų: **{len(unique)}**",
        f"Temų užklausų be rezultatų: **{len(failed_topics)} iš {len(TOPICS)}**",
        "",
        "## Surinktos antraštės (dubliuotos nuorodos sujungtos)",
        "",
    ])

    if not unique:
        sections.extend([
            "_Šį kartą negauta nė vienos RSS antraštės. Tai gali reikšti laikiną RSS paslaugos sutrikimą arba rezultatų nebuvimą._",
            "",
        ])

    for topic in TOPICS:
        matching = [
            entry for entry in unique.values()
            if topic in entry["topics"]  # type: ignore[operator]
        ]
        sections.extend([f"### {topic}", ""])
        if not matching:
            sections.extend(["_Šį kartą patikimų RSS rezultatų negauta._", ""])
            continue
        for entry in matching:
            source = f" — {entry['source']}" if entry["source"] else ""
            sections.append(
                f"- [{entry['title']}]({entry['link']}) "
                f"({entry['published']}{source})"
            )
        sections.append("")

    sections.extend([
        "## Kaip naudoti šią ataskaitą",
        "",
        "1. Ieškoti temų, kurios pasikartoja keliose paieškose, bet nelaikyti to paieškų paklausos matu.",
        "2. Pirmenybę teikti temoms, kurios sprendžia konkretų augintinio šeimininko klausimą.",
        "3. Pirminius veterinarinius teiginius tikrinti pagal klinikines gaires ir patikimus veterinarijos šaltinius.",
        "4. Prieš rengiant turinį patikrinti, ar tema jau nėra išsamiai aprašyta PetTraffic AI svetainėje.",
        "5. Prieš publikuojant redaguoti tekstą, patikrinti faktus, šaltinius ir nuorodas.",
        "",
        "Pastaba: antraščių skaičius nėra Google paieškų apimtis, lankytojų skaičius ar komercinio susidomėjimo įrodymas.",
    ])

    OUT.write_text("\n".join(sections) + "\n", encoding="utf-8")
    print(f"Topic radar created: {OUT} ({len(unique)} unique headlines)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
