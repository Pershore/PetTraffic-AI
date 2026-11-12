#!/usr/bin/env python3
"""Read-only Search Console snapshot for the separately authorised ARO Vet property."""
from __future__ import annotations

from datetime import date, timedelta
from pathlib import Path
from urllib.parse import quote
import json
import os
import sys

OUT = Path("reports/aro-vet-search-console-7d.md")


def main() -> int:
    OUT.parent.mkdir(parents=True, exist_ok=True)
    raw = os.environ.get("GOOGLE_SERVICE_ACCOUNT_JSON", "").strip()
    site_url = os.environ.get("ARO_VET_GSC_SITE_URL", "").strip()
    if not raw or not site_url:
        missing = [
            name for name, value in (
                ("GOOGLE_SERVICE_ACCOUNT_JSON", raw),
                ("ARO_VET_GSC_SITE_URL", site_url),
            ) if not value
        ]
        OUT.write_text(
            "# ARO Vet – Google Search Console\n\n"
            f"## Būsena: neprijungta\n\nTrūksta nustatymų: {', '.join(missing)}.\n",
            encoding="utf-8",
        )
        print("ARO Vet Search Console configuration missing.", file=sys.stderr)
        return 1

    try:
        from google.oauth2 import service_account
        from google.auth.transport.requests import AuthorizedSession

        credentials = service_account.Credentials.from_service_account_info(
            json.loads(raw),
            scopes=["https://www.googleapis.com/auth/webmasters.readonly"],
        )
        session = AuthorizedSession(credentials)
        end = date.today() - timedelta(days=3)  # Search Console data has a reporting delay.
        start = end - timedelta(days=6)
        endpoint = (
            "https://searchconsole.googleapis.com/webmasters/v3/sites/"
            + quote(site_url, safe="")
            + "/searchAnalytics/query"
        )

        def query(dimensions: list[str] | None = None) -> list[dict]:
            body = {
                "startDate": start.isoformat(),
                "endDate": end.isoformat(),
                "rowLimit": 10,
            }
            if dimensions:
                body["dimensions"] = dimensions
            response = session.post(endpoint, json=body, timeout=30)
            if not response.ok:
                detail = response.text[:1200].replace("\n", " ")
                raise RuntimeError(
                    f"Search Console API HTTP {response.status_code}: {detail}"
                )
            return response.json().get("rows", [])

        totals = query()
        queries = query(["query"])
        pages = query(["page"])

        def metric(key: str) -> str:
            if not totals:
                return "Duomenų nėra"
            value = float(totals[0].get(key, 0))
            if key == "ctr":
                return f"{value:.1%}"
            if key == "position":
                return f"{value:.1f}"
            return f"{value:,.0f}".replace(",", " ")

        lines = [
            "# ARO Vet – Google Search Console ataskaita",
            "",
            f"Nuosavybė: {site_url}",
            f"Laikotarpis: {start} – {end} (paliktas 3 dienų duomenų vėlavimo rezervas)",
            "",
            "## Pagrindiniai rodikliai",
            "",
            "| Rodiklis | Reikšmė |",
            "|---|---:|",
            f"| Paieškos parodymai | {metric('impressions')} |",
            f"| Paspaudimai | {metric('clicks')} |",
            f"| CTR | {metric('ctr')} |",
            f"| Vidutinė pozicija | {metric('position')} |",
            "",
            "## Populiariausios Google paieškos užklausos",
            "",
        ]
        if queries:
            lines += [
                "| Užklausa | Paspaudimai | Parodymai | CTR | Pozicija |",
                "|---|---:|---:|---:|---:|",
            ]
            for row in queries:
                term = row.get("keys", [""])[0].replace("|", "\\|")
                lines.append(
                    f"| {term} | {float(row.get('clicks', 0)):.0f} | "
                    f"{float(row.get('impressions', 0)):.0f} | "
                    f"{float(row.get('ctr', 0)):.1%} | "
                    f"{float(row.get('position', 0)):.1f} |"
                )
        else:
            lines.append("_Google paieškos užklausų eilučių nėra._")

        lines += ["", "## Puslapiai Google paieškoje", ""]
        if pages:
            lines += [
                "| Puslapis | Paspaudimai | Parodymai | CTR | Pozicija |",
                "|---|---:|---:|---:|---:|",
            ]
            for row in pages:
                page = row.get("keys", [""])[0].replace("|", "%7C")
                lines.append(
                    f"| {page} | {float(row.get('clicks', 0)):.0f} | "
                    f"{float(row.get('impressions', 0)):.0f} | "
                    f"{float(row.get('ctr', 0)):.1%} | "
                    f"{float(row.get('position', 0)):.1f} |"
                )
        else:
            lines.append("_Google paieškos puslapių eilučių nėra._")

        lines += [
            "",
            "Pastaba: Search Console parodymai yra pasirodymai Google paieškoje, "
            "o ne apsilankymai svetainėje. Ataskaita naudoja tik agreguotus duomenis.",
        ]
        OUT.write_text("\n".join(lines) + "\n", encoding="utf-8")
        print(f"ARO Vet Search Console report created: {OUT}")
        return 0
    except Exception as exc:
        OUT.write_text(
            "# ARO Vet – Google Search Console ataskaita\n\n"
            "## Būsena: klaida\n\n"
            f"Google Search Console užklausa nepavyko: {type(exc).__name__}: {exc}\n",
            encoding="utf-8",
        )
        print(f"ARO Vet Search Console error: {type(exc).__name__}: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
