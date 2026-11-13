#!/usr/bin/env python3
"""Read-only, privacy-conscious GA4 + Search Console snapshot for Pet traffic."""
from __future__ import annotations

from datetime import date, timedelta
from pathlib import Path
from urllib.parse import quote
import json
import os
import sys
import time
import xml.etree.ElementTree as ET

OUT = Path("reports/analytics-7d.md")


def api_post(session, url: str, body: dict) -> dict:
    # Google APIs occasionally return transient 5xx/429 responses or slow reads.
    # Retry once for those transport/server failures, but never retry permission errors.
    for attempt in range(2):
        try:
            response = session.post(url, json=body, timeout=45)
        except Exception as exc:
            retryable = exc.__class__.__name__ in {
                "ReadTimeout", "ConnectTimeout", "ConnectionError"
            }
            if retryable and attempt == 0:
                print(f"Temporary Google API transport error ({type(exc).__name__}); retrying once.", file=sys.stderr)
                time.sleep(3)
                continue
            raise
        if response.status_code in (429, 500, 502, 503, 504) and attempt == 0:
            print(f"Temporary Google API HTTP {response.status_code}; retrying once.", file=sys.stderr)
            time.sleep(3)
            continue
        if not response.ok:
            # Google APIs include a structured reason/message in the response body.
            # Keep it in the report so permission and API-activation failures can be distinguished.
            detail = response.text[:1200].replace("\\n", " ")
            raise RuntimeError(f"Google API HTTP {response.status_code}: {detail}")
        return response.json()
    raise RuntimeError("Google API request failed after retry.")


def ga_rows(session, url: str, start: date, end: date, metrics: list[str],
            dimensions: list[str] | None = None, limit: int = 10,
            metric_aggregations: list[str] | None = None) -> dict:
    body = {
        "dateRanges": [{"startDate": start.isoformat(), "endDate": end.isoformat()}],
        "metrics": [{"name": name} for name in metrics],
        "limit": limit,
    }
    if dimensions:
        body["dimensions"] = [{"name": name} for name in dimensions]
    if dimensions and metrics:
        body["orderBys"] = [{"metric": {"metricName": metrics[-1]}, "desc": True}]
    if metric_aggregations:
        body["metricAggregations"] = metric_aggregations
    return api_post(session, url, body)


def metric_totals(data: dict) -> dict[str, float]:
    headers = [item["name"] for item in data.get("metricHeaders", [])]
    rows = data.get("rows", [])
    values = rows[0].get("metricValues", []) if rows else []
    return {name: float(value.get("value", "0")) for name, value in zip(headers, values)}


def metric_aggregation_total(data: dict, metric_name: str) -> float | None:
    """Read GA4's explicit TOTAL aggregation, not a separately queried total."""
    rows = data.get("totals") or []
    if not rows:
        rows = [
            row for row in data.get("rows", [])
            if any(
                str(value.get("value", "")).startswith("RESERVED_TOTAL")
                for value in row.get("dimensionValues", [])
            )
        ]
    values = metric_totals({
        "metricHeaders": data.get("metricHeaders", []),
        "rows": rows[:1],
    })
    return values.get(metric_name)

def channel_breakdown_status(channel_sum: float, api_total: float | None,
                             overall_total: float) -> tuple[bool, str]:
    """Only trust channel-level metrics when both GA4 totals reconcile."""
    if api_total is None:
        return False, "GA4 nepateikė kanalų užklausos TOTAL agregato."
    if abs(channel_sum - api_total) > 0.01:
        return False, (
            f"kanalų eilučių suma ({fmt(channel_sum)}) nesutampa su "
            f"tos pačios užklausos TOTAL ({fmt(api_total)})"
        )
    if abs(api_total - overall_total) > 0.01:
        return False, (
            f"kanalų užklausos TOTAL ({fmt(api_total)}) skiriasi nuo "
            f"bendros sesijų užklausos ({fmt(overall_total)})"
        )
    return True, "kanalų suma sutampa su bendru GA4 sesijų skaičiumi."


def gsc_query(session, url: str, start: date, end: date,
              dimensions: list[str] | None = None, limit: int = 10) -> dict:
    body = {"startDate": start.isoformat(), "endDate": end.isoformat(), "rowLimit": limit}
    if dimensions:
        body["dimensions"] = dimensions
    return api_post(session, url, body)



def gsc_inspect(session, url: str, site_url: str) -> dict:
    endpoint = "https://searchconsole.googleapis.com/v1/urlInspection/index:inspect"
    return api_post(session, endpoint, {
        "inspectionUrl": url,
        "siteUrl": site_url,
        "languageCode": "lt",
    })


def gsc_sitemaps(session, site_url: str) -> list[dict]:
    endpoint = (
        "https://searchconsole.googleapis.com/webmasters/v3/sites/"
        + quote(site_url, safe="")
        + "/sitemaps"
    )
    response = session.get(endpoint, timeout=30)
    if not response.ok:
        detail = response.text[:1200].replace("\\n", " ")
        raise RuntimeError(f"Google API HTTP {response.status_code}: {detail}")
    return response.json().get("sitemap", [])


def priority_urls(site_url: str) -> list[str]:
    sitemap = Path("site/sitemap.xml")
    urls = [site_url]
    if sitemap.exists():
        try:
            root = ET.parse(sitemap).getroot()
            ns = {"sm": "http://www.sitemaps.org/schemas/sitemap/0.9"}
            article_urls = [
                node.text.strip() for node in root.findall("sm:url/sm:loc", ns)
                if node.text and "/articles/" in node.text
            ]
            urls.extend(article_urls)
        except (ET.ParseError, OSError):
            pass
    return list(dict.fromkeys(urls))[:10]


def gsc_metric(data: dict, key: str) -> float | None:
    """Return a Search Console metric only when Google supplied an aggregate row."""
    rows = data.get("rows") or []
    if not rows:
        return None
    return float(rows[0].get(key, 0))


def fmt_gsc(value: float | None) -> str:
    return "Duomenų nėra" if value is None else fmt(value)


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

        lines = [
            "# Pet traffic – lankomumo ataskaita",
            "",
            f"GA4 laikotarpis: {ga_start} – {ga_end}",
            f"Palyginimas: {ga_prev_start} – {ga_prev_end}",
        ]
        ga4_ok = False
        gsc_ok = False

        try:
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
            ga4_ok = True
    
            lines += [
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
                ["sessionDefaultChannelGroup"], limit=50, metric_aggregations=["TOTAL"],
            )
            lines += ["", "### Sesijos pagal kanalą", "", "| Kanalas | Sesijos |", "|---|---:|"]
            if channels.get("metadata", {}).get("dataLossFromOtherRow"):
                lines.append("_Dalis kanalų sujungta į „(other)“ dėl didelio dimensijos reikšmių skaičiaus._")
            if channels.get("metadata", {}).get("subjectToThresholding"):
                lines.append("_Google taiko duomenų slenkstį; kanalų suma gali nesutapti su bendru rodikliu._")
            organic_sessions = 0.0
            channel_sessions_total = 0.0
            for row in channels.get("rows", []):
                channel = row.get("dimensionValues", [{}])[0].get("value", "Nežinomas")
                value = float(row.get("metricValues", [{}])[0].get("value", "0"))
                lines.append(f"| {channel} | {fmt(value)} |")
                channel_sessions_total += value
                if channel == "Organic Search":
                    organic_sessions = value
            if not channels.get("rows"):
                lines.append("| Duomenų nėra | – |")
            total_sessions = current.get("sessions", 0.0)
            channel_api_total = metric_aggregation_total(channels, "sessions")
            channel_verified, channel_note = channel_breakdown_status(
                channel_sessions_total, channel_api_total, total_sessions
            )
            if channel_verified:
                lines += ["", f"Organinės paieškos sesijos: **{fmt(organic_sessions)}**", ""]
            else:
                lines += [
                    "",
                    "Organinės paieškos sesijos: **nepatvirtinta** – kanalų išklotinė nesutampa su bendru GA4 sesijų skaičiumi.",
                    f"Duomenų patikra: {channel_note}.",
                    "Kanalų lentelė ir organinės paieškos skaičius yra preliminarūs; jų nenaudokite kaip patvirtinto pasiskirstymo.",
                    "",
                ]
    
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
    
        except Exception as ga_exc:
            lines += [
                "",
                "## Pagrindiniai rodikliai (GA4)",
                "",
                (
                    "Papildomų GA4 išklotinių gauti nepavyko; pagrindiniai rodikliai išsaugoti."
                    if ga4_ok else
                    "GA4 duomenų gauti nepavyko; Search Console bus tikrinama atskirai."
                ),
                f"Techninė priežastis: {type(ga_exc).__name__}: {ga_exc}",
            ]
            print(f"WARNING: GA4 unavailable: {type(ga_exc).__name__}: {ga_exc}", file=sys.stderr)

        # Search Console is optional: a permissions/API issue must not discard valid GA4 data.
        try:
            # Search Console uses its own, deliberately delayed reporting window.
            gsc_current = gsc_query(session, gsc_url, gsc_start, gsc_end)
            gsc_previous = gsc_query(session, gsc_url, gsc_prev_start, gsc_prev_end)
            gsc_ok = True
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
                now_value = gsc_metric(gsc_current, key)
                old_value = gsc_metric(gsc_previous, key)
                change = delta(now_value, old_value) if now_value is not None and old_value is not None else "nėra duomenų palyginimui"
                lines.append(f"| {label} | {fmt_gsc(now_value)} | {change} |")
            now_ctr = gsc_metric(gsc_current, "ctr")
            old_ctr = gsc_metric(gsc_previous, "ctr")
            now_pos = gsc_metric(gsc_current, "position")
            old_pos = gsc_metric(gsc_previous, "position")
            ctr_change = f"{((now_ctr-old_ctr)*100):+.2f} proc. punkto" if now_ctr is not None and old_ctr is not None else "nėra duomenų palyginimui"
            pos_change = f"{now_pos-old_pos:+.1f} poz." if now_pos is not None and old_pos is not None else "nėra duomenų palyginimui"
            lines += [
                f"| CTR | {now_ctr:.1%} | {ctr_change} |" if now_ctr is not None else "| CTR | Duomenų nėra | nėra duomenų palyginimui |",
                f"| Vidutinė pozicija | {now_pos:.1f} | {pos_change} |" if now_pos is not None else "| Vidutinė pozicija | Duomenų nėra | nėra duomenų palyginimui |",
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

            lines += ["", "### Svetainės žemėlapis (Search Console)", ""]
            expected_sitemap = f"{gsc_site.rstrip('/')}/sitemap.xml"
            try:
                submitted_sitemaps = gsc_sitemaps(session, gsc_site)
                matching = [
                    item for item in submitted_sitemaps
                    if item.get("path", "").rstrip("/") == expected_sitemap.rstrip("/")
                ]
                if matching:
                    item = matching[0]
                    contents = item.get("contents", [])
                    lines.append(f"- Būsena: **pateiktas** ({item.get('path', expected_sitemap)})")
                    lines.append(f"- Paskutinį kartą pateiktas: {item.get('lastSubmitted', 'nenurodyta')}")
                    lines.append(f"- Google paskutinį kartą atsisiuntė: {item.get('lastDownloaded', 'dar nenurodyta')}")
                    if contents:
                        submitted_count = sum(int(part.get("submitted", 0)) for part in contents)
                        indexed_count = sum(int(part.get("indexed", 0)) for part in contents)
                        lines.append(f"- URL pateikta / indeksuota: {submitted_count} / {indexed_count}")
                    else:
                        lines.append("- URL pateikimo / indeksavimo skaičių Google dar nepateikė.")
                    lines.append(f"- Laukia apdorojimo: {'taip' if item.get('isPending') else 'ne'}")
                else:
                    lines.append(
                        f"- **Nepateiktas:** Search Console sąraše nerastas {expected_sitemap}"
                    )
                    lines.append("- Kitas veiksmas: pateikti šį sitemap Search Console sąsajoje.")
            except Exception as sitemap_exc:
                lines.append(
                    f"- Pateikimo būsenos patikrinti nepavyko: "
                    f"{type(sitemap_exc).__name__}: {str(sitemap_exc)[:180]}"
                )

            lines += ["", "### Google indekso būklė (svarbiausi puslapiai)", ""]
            lines += [
                "| Puslapis | Būsena | Google paaiškinimas | Robots.txt | Indeksavimas | Paskutinis tikrinimas |",
                "|---|---|---|---|---|---|",
            ]
            for inspected_url in priority_urls(gsc_site):
                try:
                    inspection = gsc_inspect(session, inspected_url, gsc_site).get("inspectionResult", {})
                    status = inspection.get("indexStatusResult", {})
                    path_label = inspected_url.replace(gsc_site.rstrip("/"), "") or "/"
                    coverage = status.get("coverageState", "Google duomenų dar nėra")
                    last_crawl = status.get("lastCrawlTime", "Dar netikrinta")
                    canonical = status.get("googleCanonical", "")
                    if canonical:
                        coverage += f" (Google canonical: {canonical})"
                    lines.append(
                        f"| {path_label} | {status.get('verdict', 'UNKNOWN')} | "
                        f"{coverage.replace('|', '/')} | {status.get('robotsTxtState', 'UNKNOWN')} | "
                        f"{status.get('indexingState', 'UNKNOWN')} | {last_crawl} |"
                    )
                except Exception as inspect_exc:
                    lines.append(
                        f"| {inspected_url} | Nepavyko patikrinti | "
                        f"{type(inspect_exc).__name__}: {str(inspect_exc)[:180].replace('|', '/')} | – | – | – |"
                    )

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
                (
                    "Papildomų Search Console išklotinių gauti nepavyko; pagrindiniai rodikliai išsaugoti."
                    if gsc_ok else
                    "Duomenų gauti nepavyko. GA4 ataskaita pateikta atskirai."
                ),
                f"Techninė priežastis: {type(gsc_exc).__name__}: {gsc_exc}",
                "403 dažniausiai reiškia, kad paslaugos paskyra neturi teisės skaityti nurodytos nuosavybės arba Search Console API / projekto prieiga dar nesutvarkyta. Patikrinkite, ar Search Console API įjungta tame pačiame Google Cloud projekte, ar paslaugos paskyra pridėta būtent prie šios nuosavybės, ir ar GSC_SITE_URL tiksliai sutampa su nuosavybės adresu.",
            ]
            print(f"WARNING: Search Console unavailable: {type(gsc_exc).__name__}: {gsc_exc}", file=sys.stderr)

        OUT.write_text("\n".join(lines) + "\n", encoding="utf-8")
        print(f"Analytics report created: {OUT}")
        # A partial report is a successful collection if either independent source worked.
        return 0 if ga4_ok or gsc_ok else 1
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
