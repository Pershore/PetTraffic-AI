#!/usr/bin/env python3
"""Read-only, privacy-conscious GA4 + Search Console snapshot for Pet traffic."""
from __future__ import annotations

from datetime import date, timedelta
from pathlib import Path
from urllib.parse import quote
import json
import os
import sys

OUT = Path("reports/analytics-7d.md")


def api_post(session, url: str, body: dict) -> dict:
    response = session.post(url, json=body, timeout=30)
    response.raise_for_status()
    return response.json()


def ga_rows(session, url: str, start: date, end: date, metrics: list[str],
            dimensions: list[str] | None = None, limit: int = 10) -> dict:
    body = {
        "dateRanges": [{"startDate": start.isoformat(), "endDate": end.isoformat()}],
        "metrics": [{"name": name} for name in metrics],
        "limit": limit,
    }
    if dimensions:
        body["dimensions"] = [{"name": name} for name in dimensions]
    if dimensions and metrics:
        body["orderBys"] = [{"metric": {"metricName": metrics[-1]}, "desc": True}]
    return api_post(session, url, body)


def metric_totals(data: dict) -> dict[str, float]:
    headers = [item["name"] for item in data.get("metricHeaders", [])]
    rows = data.get("rows", [])
    values = rows[0].get("metricValues", []) if rows else []
    return {name: float(value.get("value", "0")) for name, value in zip(headers, values)}


def gsc_query(session, url: str, start: date, end: date,
              dimensions: list[str] | None = None, limit: int = 10) -> dict:
    body = {"startDate": start.isoformat(), "endDate": end.isoformat(), "rowLimit": limit}
    if dimensions:
        body["dimensions"] = dimensions
    return api_post(session, url, body)


def fmt(value: float) -> str:
    return f"{value:,.0f}".replace(",", " ")


def delta(current: float, previous: float) -> str:
    if previous == 0:
        return "nėra palyginimo bazės" if current == 0 else "naujas augimas (ankstesnis laikotarpis: 0)"
    change = (current - previous) / previous * 100
    return f"{change:+.1f} %"


def main() -> int:
    OUT.parent.mkdir(parents=True, exist_ok=True)
    raw = os.environ.get("GOOGLE_SERVICE_ACCOUNT_JSON", "").strip()
    ga4_id = os.environ.get("GA4_PROPERTY_ID", "").strip()
    gsc_site = os.environ.get("GSC_SITE_URL", "").strip()
    if not raw or not ga4_id or not gsc_site:
        missing = [name for name, value in (
            ("GOOGLE_SERVICE_ACCOUNT_JSON", raw),
            ("GA4_PROPERTY_ID", ga4_id),
            ("GSC_SITE_URL", gsc_site),
        ) if not value]
        OUT.write_text(
            "# Pet traffic – 7 dienų analitika\n\n"
            "## Būsena: neprijungta\n\n"
            f"Trūksta GitHub Actions nustatymų: {', '.join(missing)}. "
            "Prijunkite paslaugos paskyrą ir suteikite jai tik skaitymo prieigą GA4 bei Search Console. "
            "Jokių atskirų lankytojų duomenų ši ataskaita nerenka.\n",
            encoding="utf-8",
        )
        print("Analytics credentials or configuration missing.")
        return 0

    try:
        from google.oauth2 import service_account
        from google.auth.transport.requests import AuthorizedSession

        info = json.loads(raw)
        scopes = [
            "https://www.googleapis.com/auth/analytics.readonly",
            "https://www.googleapis.com/auth/webmasters.readonly",
        ]
        credentials = service_account.Credentials.from_service_account_info(info, scopes=scopes)
        session = AuthorizedSession(credentials)

        today = date.today()
        ga_end = today - timedelta(days=1)
        ga_start = ga_end - timedelta(days=6)
        ga_prev_end = ga_start - timedelta(days=1)
        ga_prev_start = ga_prev_end - timedelta(days=6)

        # Search Console data commonly arrives later than GA4 data; leave a three-day buffer.
        gsc_end = today - timedelta(days=3)
        gsc_start = gsc_end - timedelta(days=6)
        gsc_prev_end = gsc_start - timedelta(days=1)
        gsc_prev_start = gsc_prev_end - timedelta(days=6)

        ga_url = f"https://analyticsdata.googleapis.com/v1beta/properties/{quote(ga4_id, safe='')}:runReport"
        gsc_url = (
            "https://searchconsole.googleapis.com/webmasters/v3/sites/"
            + quote(gsc_site, safe="")
            + "/searchAnalytics/query"
        )

        ga_current = ga_rows(
            session, ga_url, ga_start, ga_end,
            ["activeUsers", "newUsers", "sessions", "screenPageViews"], limit=1,
        )
        ga_previous = ga_rows(
            session, ga_url, ga_prev_start, ga_prev_end,
            ["activeUsers", "newUsers", "sessions", "screenPageViews"], limit=1,
        )
        current = metric_totals(ga_current)
        previous = metric_totals(ga_previous)

        lines = [
            "# Pet traffic – lankomumo ataskaita",
            "",
            f"GA4 laikotarpis: {ga_start} – {ga_end}",
            f"Palyginimas: {ga_prev_start} – {ga_prev_end}",
            "",
            "## Pagrindiniai rodikliai (GA4)",
            "",
            "| Rodiklis | Paskutinės 7 d. | Pokytis prieš ankstesnes 7 d. |",
            "|---|---:|---:|",
        ]
        for key, label in (
            ("activeUsers", "Aktyvūs naudotojai"),
            ("newUsers", "Nauji naudotojai"),
            ("sessions", "Sesijos / apsilankymai"),
            ("screenPageViews", "Puslapių peržiūros"),
        ):
            lines.append(
                f"| {label} | {fmt(current.get(key, 0))} | "
                f"{delta(current.get(key, 0), previous.get(key, 0))} |"
            )

        channels = ga_rows(
            session, ga_url, ga_start, ga_end, ["sessions"],
            ["sessionDefaultChannelGroup"], limit=10,
        )
        lines += ["", "### Sesijos pagal kanalą", "", "| Kanalas | Sesijos |", "|---|---:|"]
        organic_sessions = 0.0
        for row in channels.get("rows", []):
            channel = row.get("dimensionValues", [{}])[0].get("value", "Nežinomas")
            value = float(row.get("metricValues", [{}])[0].get("value", "0"))
            lines.append(f"| {channel} | {fmt(value)} |")
            if channel == "Organic Search":
                organic_sessions = value
        if not channels.get("rows"):
            lines.append("| Duomenų nėra | – |")
        lines += ["", f"Organinės paieškos sesijos: **{fmt(organic_sessions)}**", ""]

        top_pages = ga_rows(
            session, ga_url, ga_start, ga_end, ["screenPageViews"], ["pagePath"], limit=10,
        )
        lines += ["### Daugiausia peržiūrėti puslapiai (GA4)", ""]
        if top_pages.get("rows"):
            for row in top_pages["rows"]:
                path = row.get("dimensionValues", [{}])[0].get("value", "/")
                views = float(row.get("metricValues", [{}])[0].get("value", "0"))
                lines.append(f"- {path} – {fmt(views)} peržiūrų")
        else:
            lines.append("_GA4 puslapių duomenų šiam laikotarpiui nėra._")

        # Search Console is optional: a permissions/API issue must not discard valid GA4 data.
        try:
            # Search Console uses its own, deliberately delayed reporting window.
            gsc_current = gsc_query(session, gsc_url, gsc_start, gsc_end)
            gsc_previous = gsc_query(session, gsc_url, gsc_prev_start, gsc_prev_end)
            gsc_now = (gsc_current.get("rows") or [{}])[0]
            gsc_old = (gsc_previous.get("rows") or [{}])[0]
            lines += [
                "",
                "## Google paieška (Search Console)",
                "",
                f"Laikotarpis: {gsc_start} – {gsc_end} (duomenys gali vėluoti kelias dienas).",
                "",
                "| Rodiklis | Paskutinės 7 d. | Pokytis prieš ankstesnes 7 d. |",
                "|---|---:|---:|",
            ]
            for key, label in (
                ("impressions", "Paieškos parodymai"),
                ("clicks", "Paspaudimai"),
            ):
                now_value = float(gsc_now.get(key, 0))
                old_value = float(gsc_old.get(key, 0))
                lines.append(f"| {label} | {fmt(now_value)} | {delta(now_value, old_value)} |")
            now_ctr = float(gsc_now.get("ctr", 0))
            old_ctr = float(gsc_old.get("ctr", 0))
            now_pos = float(gsc_now.get("position", 0))
            old_pos = float(gsc_old.get("position", 0))
            lines += [
                f"| CTR | {now_ctr:.1%} | {((now_ctr-old_ctr)*100):+.2f} proc. punkto |",
                f"| Vidutinė pozicija | {now_pos:.1f} | {now_pos-old_pos:+.1f} poz. |",
                "",
                "### Populiariausios Google paieškos užklausos",
                "",
            ]

            queries = gsc_query(session, gsc_url, gsc_start, gsc_end, ["query"], 10)
            if queries.get("rows"):
                lines += [
                    "| Užklausa | Paspaudimai | Parodymai | CTR | Pozicija |",
                    "|---|---:|---:|---:|---:|",
                ]
                for row in queries["rows"]:
                    query = row.get("keys", [""])[0].replace("|", "\\|")
                    lines.append(
                        f"| {query} | {fmt(float(row.get('clicks', 0)))} | "
                        f"{fmt(float(row.get('impressions', 0)))} | "
                        f"{float(row.get('ctr', 0)):.1%} | {float(row.get('position', 0)):.1f} |"
                    )
            else:
                lines.append("_Search Console užklausų eilučių nepateikė._")

            lines += ["", "### Puslapiai Google paieškoje", ""]
            pages = gsc_query(session, gsc_url, gsc_start, gsc_end, ["page"], 10)
            if pages.get("rows"):
                lines += [
                    "| Puslapis | Paspaudimai | Parodymai | CTR | Pozicija |",
                    "|---|---:|---:|---:|---:|",
                ]
                for row in pages["rows"]:
                    page_url = row.get("keys", [""])[0].replace("|", "%7C")
                    lines.append(
                        f"| {page_url} | {fmt(float(row.get('clicks', 0)))} | "
                        f"{fmt(float(row.get('impressions', 0)))} | "
                        f"{float(row.get('ctr', 0)):.1%} | {float(row.get('position', 0)):.1f} |"
                    )
            else:
                lines.append("_Search Console puslapių eilučių nepateikė._")

            lines += [
                "",
                "## Mokama reklama",
                "",
                "Mokamų reklamų parodymai ir paspaudimai: **nėra duomenų – Google Ads / Meta Ads paskyra neprijungta**.",
                "Google paieškos parodymai aukščiau nėra mokamų reklamų parodymai.",
                "",
                "Pastaba: aktyvūs naudotojai apytikriai rodo unikalius lankytojus, sesijos – apsilankymus, "
                "o puslapių peržiūros – atvertų puslapių skaičių. Search Console parodymai reiškia "
                "pasirodymus Google paieškos rezultatuose, ne apsilankymus svetainėje.",
                "",
                "Ataskaita naudoja tik agreguotus duomenis; atskiri lankytojai neidentifikuojami.",
            ]
        except Exception as gsc_exc:
            lines += [
                "",
                "## Google paieška (Search Console)",
                "",
                "Duomenų gauti nepavyko. GA4 ataskaita pateikta atskirai.",
                f"Techninė priežastis: {type(gsc_exc).__name__}: {gsc_exc}",
                "403 dažniausiai reiškia, kad paslaugos paskyra neturi teisės skaityti nurodytos nuosavybės arba Search Console API / projekto prieiga dar nesutvarkyta. Patikrinkite, ar Search Console API įjungta tame pačiame Google Cloud projekte, ar paslaugos paskyra pridėta būtent prie šios nuosavybės, ir ar GSC_SITE_URL tiksliai sutampa su nuosavybės adresu.",
            ]
            print(f"WARNING: Search Console unavailable: {type(gsc_exc).__name__}: {gsc_exc}", file=sys.stderr)

        OUT.write_text("\n".join(lines) + "\n", encoding="utf-8")
        print(f"Analytics report created: {OUT}")
        return 0
    except Exception as exc:
        OUT.write_text(
            "# Pet traffic – lankomumo ataskaita\n\n"
            "## Būsena: klaida\n\n"
            f"Google API užklausa nepavyko: {type(exc).__name__}: {exc}\n",
            encoding="utf-8",
        )
        print(f"ERROR: {type(exc).__name__}: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
