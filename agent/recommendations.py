#!/usr/bin/env python3
"""Create conservative, evidence-linked PetTraffic recommendations from history."""
from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
import json
import os
import sys

HISTORY_ROOT = Path("reports/history")
OUT_MD = Path("reports/recommendations.md")
OUT_JSON = Path("reports/recommendations.json")


def load_snapshots(category: str, history_root: Path = HISTORY_ROOT) -> list[dict]:
    snapshots = []
    folder = history_root / category
    if not folder.exists():
        return snapshots
    for path in sorted(folder.glob("*.json")):
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
            snapshots.extend(item for item in data.get("snapshots", []) if isinstance(item, dict))
        except (OSError, ValueError, json.JSONDecodeError):
            continue
    return sorted(snapshots, key=lambda item: str(item.get("generated_at", "")))


def build_recommendations(history_root: Path = HISTORY_ROOT) -> list[dict]:
    recommendations: list[dict] = []
    analytics = load_snapshots("analytics", history_root)
    topics = load_snapshots("topic-radar", history_root)
    control = load_snapshots("control-center", history_root)

    def add(key: str, priority: str, title: str, evidence: str, action: str) -> None:
        recommendations.append({
            "id": key,
            "priority": priority,
            "title": title,
            "evidence": evidence,
            "next_action": action,
            "status": "monitor",
        })

    if not analytics:
        add(
            "analytics-baseline",
            "info",
            "Sukaupti analitikos pradinę bazę",
            "Istorijoje dar nėra GA4 / Search Console išrašų.",
            "Palikti kasdienį analitikos rinkimą veikti; išvadų apie augimą dar nedaryti.",
        )
    else:
        latest = analytics[-1]
        if latest.get("ga4_status") != "available":
            add(
                "ga4-connection",
                "high",
                "Patikrinti GA4 duomenų prieigą",
                f"Naujausio išrašo GA4 būsena: {latest.get('ga4_status', 'unknown')}.",
                "Patikrinti GA4 paslaugos paskyros skaitymo prieigą ir API atsakymą.",
            )
        if latest.get("search_console_status") != "available":
            add(
                "gsc-connection",
                "medium",
                "Patikrinti Search Console duomenų prieigą",
                f"Naujausio išrašo Search Console būsena: {latest.get('search_console_status', 'unknown')}.",
                "Patikrinti nuosavybės adresą, paslaugos paskyros teises ir Search Console API.",
            )

        # Repeated runs for the same Search Console reporting window are not
        # independent evidence. Keep only the latest snapshot for each period.
        valid_gsc_by_period = {}
        for item in analytics:
            if item.get("search_console_status") == "available" and isinstance(item.get("metrics"), dict):
                period = item.get("search_console_period") or str(item.get("generated_at", ""))[:10]
                valid_gsc_by_period[period] = item
        valid_gsc = sorted(
            valid_gsc_by_period.values(),
            key=lambda item: str(item.get("generated_at", "")),
        )
        if len(valid_gsc) >= 2:
            last_two = valid_gsc[-2:]
            zero_visibility = all(
                (item["metrics"].get("search_impressions") or 0) == 0
                and (item["metrics"].get("search_clicks") or 0) == 0
                for item in last_two
            )
            if zero_visibility:
                add(
                    "search-visibility",
                    "medium",
                    "Patikrinti Google paieškos matomumą",
                    "Dviejuose naujausiuose prieinamuose Search Console laikotarpiuose parodymai ir paspaudimai buvo nuliniai.",
                    "Patikrinti URL indeksavimo būseną, sitemap apdorojimą ir ar svarbiausi puslapiai prieinami Googlebot.",
                )
        elif valid_gsc:
            metrics = valid_gsc[-1].get("metrics", {})
            if (metrics.get("search_impressions") or 0) == 0 and (metrics.get("search_clicks") or 0) == 0:
                add(
                    "search-visibility-baseline",
                    "info",
                    "Dar rinkti Google paieškos duomenis",
                    "Viename Search Console laikotarpyje parodymai ir paspaudimai buvo nuliniai; vieno laikotarpio nepakanka tendencijai patvirtinti.",
                    "Palikti kasdienį rinkimą veikti ir palyginti kitą užbaigtą Search Console laikotarpį.",
                )

        details = latest.get("search_console_details", {})
        sitemap = details.get("sitemap", {})
        if sitemap.get("status") == "not_submitted":
            add(
                "sitemap-not-submitted",
                "high",
                "Pateikti svetainės žemėlapį Google",
                "Search Console nuosavybėje nerastas svetainės sitemap.xml pateikimas.",
                "Search Console pateikti https://pettraffic-ai.pages.dev/sitemap.xml ir kitame cikle patikrinti, ar Google jį atsisiuntė.",
            )
        elif sitemap.get("status") == "submitted":
            submitted = sitemap.get("submitted_urls")
            indexed = sitemap.get("indexed_urls")
            if isinstance(submitted, int) and isinstance(indexed, int) and submitted > indexed:
                add(
                    "sitemap-indexing-gap",
                    "medium",
                    "Patikrinti dar neindeksuotus sitemap URL",
                    f"Search Console nurodo {indexed} indeksuotų iš {submitted} pateiktų URL.",
                    "Peržiūrėti prioritetinių URL patikros rezultatus, canonical ir noindex signalus; indeksavimo skirtumo nelaikyti automatine klaida.",
                )
            elif sitemap.get("is_pending") is True:
                add(
                    "sitemap-processing",
                    "info",
                    "Stebėti Google sitemap apdorojimą",
                    "Search Console nurodo, kad sitemap dar laukia apdorojimo.",
                    "Pakartotinai patikrinti kitame cikle; sitemap pakartotinai neteikti, jei jis jau pateiktas.",
                )

        inspections = details.get("priority_url_inspections", [])
        if isinstance(inspections, list) and inspections:
            blocked = [
                item for item in inspections
                if item.get("robots_txt_state") == "DISALLOWED"
                or str(item.get("indexing_state", "")).startswith("BLOCKED_BY")
            ]
            not_indexed = [
                item for item in inspections
                if item not in blocked and (
                    item.get("verdict") in {"FAIL", "PARTIAL"}
                    or "currently not indexed" in str(item.get("coverage", "")).lower()
                    or item.get("indexing_state") == "NOT_INDEXED"
                )
            ]
            if blocked:
                paths = ", ".join(str(item.get("url_path", "/")) for item in blocked)
                add(
                    "priority-url-blocked",
                    "high",
                    "Pašalinti svarbių puslapių indeksavimo blokavimą",
                    f"Google patikroje blokuojami prioritetiniai URL: {paths}.",
                    "Patikrinti robots.txt, meta robots ir X-Robots-Tag; pakeitimus atlikti tik patvirtinus, kad puslapiai turi būti indeksuojami.",
                )
            elif not_indexed:
                paths = ", ".join(str(item.get("url_path", "/")) for item in not_indexed)
                add(
                    "priority-url-not-indexed",
                    "medium",
                    "Ištirti svarbius Google neindeksuojamus puslapius",
                    f"Google patikroje neindeksuojami arba nepatvirtinti prioritetiniai URL: {paths}.",
                    "Peržiūrėti puslapių turinio unikalumą, canonical, vidines nuorodas ir Search Console paaiškinimą; automatiškai nekeisti turinio.",
                )

        metrics = latest.get("metrics", {})
        if (metrics.get("sessions") or 0) > 0 and metrics.get("organic_sessions_verified") is None:
            add(
                "organic-attribution",
                "info",
                "Nežymėti organinių sesijų kaip patvirtintų",
                "GA4 kanalų išklotinė nepateikė patvirtintos sumos, todėl organinės sesijos nepatvirtintos.",
                "Naudoti bendrą sesijų skaičių; organinės paieškos dalį rodyti tik kai kanalų suma sutampa su GA4 TOTAL.",
            )

    if not topics:
        add(
            "topic-baseline",
            "info",
            "Sukaupti temų radaro bazę",
            "Dar nėra išsaugotų temų radaro įrašų.",
            "Palikti kasdienį RSS temų rinkimą veikti; antraščių skaičiaus nelaikyti paieškų paklausos matu.",
        )
    else:
        latest_topics = topics[-1]
        if (latest_topics.get("empty_topic_queries") or 0) > 0:
            add(
                "topic-rss-gaps",
                "low",
                "Stebėti tuščias temų RSS užklausas",
                f"Tuščių RSS temų užklausų: {latest_topics.get('empty_topic_queries')} iš {latest_topics.get('total_topic_queries')}.",
                "Patikrinti, ar tai laikinas Google News RSS rezultatų nebuvimas; nekurti temų paklausos išvadų iš šių skaičių.",
            )

    if control:
        failures = [
            f"{item.get('name')}: {item.get('state')}"
            for item in control[-1].get("results", [])
            if item.get("state") in {"failure", "api_error", "stale", "warning", "unknown"}
        ]
        if failures:
            add(
                "automation-health",
                "high",
                "Pašalinti automatizacijų būklės problemas",
                "; ".join(failures),
                "Atidaryti centrinio valdymo GitHub įspėjimą ir taisyti konkretaus proceso klaidą.",
            )

    if not recommendations:
        add(
            "steady-monitoring",
            "info",
            "Tęsti stebėseną",
            "Pagal turimą istoriją nenustatyta taisyklėmis patvirtintų problemų.",
            "Tęsti kasdienį rinkimą; automatinių svetainės pakeitimų nedaryti be patikrintų įrodymų.",
        )
    return recommendations


def render(recommendations: list[dict], generated_at: str) -> str:
    labels = {"high": "SKUBU", "medium": "VIDUTINIS", "low": "ŽEMAS", "info": "STEBĖTI"}
    lines = [
        "# PetTraffic – automatinės rekomendacijos",
        "",
        f"Atnaujinta: {generated_at}",
        "",
        "> Rekomendacijos sudaromos pagal sukauptus agreguotus duomenis ir techninių procesų būsenas. Tai nėra automatinis leidimas keisti ar publikuoti svetainės turinį.",
        "",
    ]
    for item in recommendations:
        lines.extend([
            f"## [{labels.get(item['priority'], item['priority'].upper())}] {item['title']}",
            "",
            f"**Įrodymai:** {item['evidence']}",
            "",
            f"**Kitas veiksmas:** {item['next_action']}",
            "",
        ])
    return "\n".join(lines)


def main() -> int:
    generated_at = datetime.now(timezone.utc).isoformat()
    run_id = os.environ.get("GITHUB_RUN_ID", "")
    if not run_id:
        print("GITHUB_RUN_ID is required.", file=sys.stderr)
        return 1
    recommendations = build_recommendations()
    document = {
        "generated_at": generated_at,
        "run_id": run_id,
        "recommendations": recommendations,
    }
    OUT_MD.parent.mkdir(parents=True, exist_ok=True)
    OUT_MD.write_text(render(recommendations, generated_at), encoding="utf-8")
    OUT_JSON.write_text(json.dumps(document, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    day = generated_at[:10]
    history_path = HISTORY_ROOT / "recommendations" / f"{day}.json"
    history = {"date": day, "snapshots": []}
    if history_path.exists():
        history = json.loads(history_path.read_text(encoding="utf-8"))
    if not any(str(item.get("run_id")) == run_id for item in history["snapshots"]):
        history["snapshots"].append(document)
    history_path.parent.mkdir(parents=True, exist_ok=True)
    history_path.write_text(json.dumps(history, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Generated {len(recommendations)} evidence-linked recommendations.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
