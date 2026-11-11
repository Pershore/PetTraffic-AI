#!/usr/bin/env python3
"""Read-only GA4 + Search Console snapshot for Pet traffic."""
from __future__ import annotations
from datetime import date, timedelta
from pathlib import Path
from urllib.parse import quote
import json, os, sys

OUT = Path("reports/analytics-7d.md")

def main() -> int:
    OUT.parent.mkdir(parents=True, exist_ok=True)
    raw = os.environ.get("GOOGLE_SERVICE_ACCOUNT_JSON", "").strip()
    ga4_id = os.environ.get("GA4_PROPERTY_ID", "").strip()
    gsc_site = os.environ.get("GSC_SITE_URL", "").strip()
    if not raw or not ga4_id or not gsc_site:
        OUT.write_text(
            "# Pet traffic – 7 dienų analitika\n\n"
            "## Būsena: neprijungta\n\n"
            "Trūksta GitHub Actions nustatymų GOOGLE_SERVICE_ACCOUNT_JSON, "
            "GA4_PROPERTY_ID arba GSC_SITE_URL. Pridėjus paslaugos paskyros "
            "raktą ir suteikus jai skaitymo prieigą GA4 bei Search Console, "
            "ataskaita bus pildoma automatiškai. Ataskaita naudoja tik "
            "agreguotus duomenis ir neidentifikuoja atskirų lankytojų.\n",
            encoding="utf-8")
        print("Google analytics credentials missing; setup-needed report written.")
        return 0
    try:
        from google.oauth2 import service_account
        from google.auth.transport.requests import AuthorizedSession
        info = json.loads(raw)
        scopes = [
            "https://www.googleapis.com/auth/analytics.readonly",
            "https://www.googleapis.com/auth/webmasters.readonly"]
        creds = service_account.Credentials.from_service_account_info(info, scopes=scopes)
        session = AuthorizedSession(creds)
        end = date.today() - timedelta(days=1)
        start = end - timedelta(days=6)
        start_s, end_s = start.isoformat(), end.isoformat()
        lines = ["# Pet traffic – 7 dienų analitika", "",
                 f"Laikotarpis: {start_s} – {end_s}", "", "## GA4 – lankomumas", ""]
        ga_url = f"https://analyticsdata.googleapis.com/v1beta/properties/{quote(ga4_id, safe='')}:runReport"
        body = {"dateRanges":[{"startDate":start_s,"endDate":end_s}],
                "metrics":[{"name":"activeUsers"},{"name":"sessions"},{"name":"screenPageViews"}],
                "limit":1}
        resp = session.post(ga_url, json=body, timeout=30); resp.raise_for_status()
        data = resp.json()
        names = [m["name"] for m in data.get("metricHeaders", [])]
        vals = data.get("rows", [{}])[0].get("metricValues", [])
        totals = dict(zip(names, [v.get("value","0") for v in vals]))
        lines += [f"- Aktyvūs naudotojai: {totals.get('activeUsers','0')}",
                  f"- Sesijos iš visų kanalų: {totals.get('sessions','0')}",
                  f"- Puslapių peržiūros: {totals.get('screenPageViews','0')}", ""]

        channel_body = {
            "dateRanges":[{"startDate":start_s,"endDate":end_s}],
            "dimensions":[{"name":"sessionDefaultChannelGroup"}],
            "metrics":[{"name":"sessions"}],
            "orderBys":[{"metric":{"metricName":"sessions"},"desc":True}],
            "limit":10
        }
        channels = session.post(ga_url, json=channel_body, timeout=30)
        channels.raise_for_status()
        channel_rows = channels.json().get("rows", [])
        organic_sessions = 0
        lines += ["### Sesijos pagal kanalą", "",
                  "| Kanalas | Sesijos |", "|---|---:|"]
        if channel_rows:
            for row in channel_rows:
                channel = row.get("dimensionValues",[{}])[0].get("value","Nežinomas")
                sessions = row.get("metricValues",[{}])[0].get("value","0")
                lines.append(f"| {channel} | {sessions} |")
                if channel == "Organic Search":
                    organic_sessions = int(float(sessions))
        else:
            lines.append("| Duomenų nėra | 0 |")
        lines += [f"", f"Organinės paieškos sesijos: {organic_sessions}", "",
                  "### Daugiausia peržiūrėti puslapiai", ""]
        page_body = {"dateRanges":[{"startDate":start_s,"endDate":end_s}],
                     "dimensions":[{"name":"pagePath"}],
                     "metrics":[{"name":"screenPageViews"}],
                     "orderBys":[{"metric":{"metricName":"screenPageViews"},"desc":True}],
                     "limit":10}
        pages = session.post(ga_url, json=page_body, timeout=30); pages.raise_for_status()
        page_rows = pages.json().get("rows", [])
        if page_rows:
            for row in page_rows:
                path = row.get("dimensionValues",[{}])[0].get("value","/")
                views = row.get("metricValues",[{}])[0].get("value","0")
                lines.append(f"- {path} – {views} peržiūrų")
        else:
            lines.append("_Šiam laikotarpiui GA4 puslapių peržiūrų eilučių nepateikė._")

        lines += ["", "## Google Search Console – paieškos užklausos", ""]
        gsc_url = "https://searchconsole.googleapis.com/webmasters/v3/sites/" + quote(gsc_site, safe="") + "/searchAnalytics/query"
        gsc_body = {"startDate":start_s,"endDate":end_s,"dimensions":["query"],"rowLimit":10}
        gsc = session.post(gsc_url, json=gsc_body, timeout=30); gsc.raise_for_status()
        rows = gsc.json().get("rows", [])
        if rows:
            lines += ["| Užklausa | Paspaudimai | Parodymai | CTR | Vid. pozicija |",
                      "|---|---:|---:|---:|---:|"]
            for row in rows:
                q = row.get("keys",[""])[0]
                lines.append(f"| {q} | {row.get('clicks',0):.0f} | {row.get('impressions',0):.0f} | {row.get('ctr',0):.1%} | {row.get('position',0):.1f} |")
        else:
            lines.append("_Search Console šiam laikotarpiui užklausų eilučių nepateikė._")

        lines += ["", "### Daugiausia parodymų sulaukę puslapiai", ""]
        gsc_pages_body = {
            "startDate":start_s,
            "endDate":end_s,
            "dimensions":["page"],
            "rowLimit":10
        }
        gsc_pages = session.post(gsc_url, json=gsc_pages_body, timeout=30)
        gsc_pages.raise_for_status()
        page_rows = gsc_pages.json().get("rows", [])
        if page_rows:
            lines += ["| Puslapis | Paspaudimai | Parodymai | CTR | Vid. pozicija |",
                      "|---|---:|---:|---:|---:|"]
            for row in page_rows:
                page_url = row.get("keys",[""])[0].replace("|", "%7C")
                lines.append(
                    f"| {page_url} | {row.get('clicks',0):.0f} | "
                    f"{row.get('impressions',0):.0f} | {row.get('ctr',0):.1%} | "
                    f"{row.get('position',0):.1f} |"
                )
        else:
            lines.append("_Search Console puslapių eilučių nepateikė._")

        lines += ["", "Ataskaita apibendrina statistinius duomenis; atskiri lankytojai neidentifikuojami."]
        OUT.write_text("\n".join(lines)+"\n", encoding="utf-8")
        print(f"Analytics report created: {OUT}")
        return 0
    except Exception as exc:
        OUT.write_text("# Pet traffic – 7 dienų analitika\n\n"
                       "## Būsena: klaida\n\n"
                       f"Google API užklausa nepavyko: {type(exc).__name__}: {exc}\n",
                       encoding="utf-8")
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1

if __name__ == "__main__":
    raise SystemExit(main())
