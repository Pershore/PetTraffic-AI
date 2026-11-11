#!/usr/bin/env python3
"""Read-only GA4 + Search Console snapshot for PetTraffic AI."""
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
            "# PetTraffic AI – 7 dienų analitika\n\n"
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
        lines = ["# PetTraffic AI – 7 dienų analitika", "",
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
                  f"- Sesijos: {totals.get('sessions','0')}",
                  f"- Puslapių peržiūros: {totals.get('screenPageViews','0')}", "",
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

        lines += ["", "## Reklamos nuorodų paspaudimai", ""]
        ad_body = {
            "dateRanges":[{"startDate":start_s,"endDate":end_s}],
            "dimensions":[{"name":"eventName"}],
            "metrics":[{"name":"eventCount"}],
            "dimensionFilter":{"filter":{
                "fieldName":"eventName",
                "stringFilter":{"matchType":"EXACT","value":"ad_click"}
            }},
            "limit":1
        }
        ad_resp = session.post(ga_url, json=ad_body, timeout=30)
        ad_resp.raise_for_status()
        ad_rows = ad_resp.json().get("rows", [])
        ad_clicks = (
            ad_rows[0].get("metricValues",[{}])[0].get("value","0")
            if ad_rows else "0"
        )
        lines.append(f"- Aro Vet reklamos nuorodų paspaudimai: {ad_clicks}")
        lines.append("_Paspaudimai nėra pardavimų ar komisinių pajamų įrodymas._")

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
        lines += ["", "Ataskaita apibendrina statistinius duomenis; atskiri lankytojai neidentifikuojami."]
        OUT.write_text("\n".join(lines)+"\n", encoding="utf-8")
        print(f"Analytics report created: {OUT}")
        return 0
    except Exception as exc:
        OUT.write_text("# PetTraffic AI – 7 dienų analitika\n\n"
                       "## Būsena: klaida\n\n"
                       f"Google API užklausa nepavyko: {type(exc).__name__}: {exc}\n",
                       encoding="utf-8")
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1

if __name__ == "__main__":
    raise SystemExit(main())
