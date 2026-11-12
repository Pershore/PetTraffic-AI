#!/usr/bin/env python3
"""Read-only aggregated GA4 snapshot for the separately authorised ARO Vet property."""
from __future__ import annotations

from datetime import date, timedelta
from pathlib import Path
from urllib.parse import quote
import json
import os
import sys

OUT = Path("reports/aro-vet-analytics-7d.md")


def post_json(session, url: str, body: dict) -> dict:
    response = session.post(url, json=body, timeout=30)
    if not response.ok:
        detail = response.text[:1000].replace("\\n", " ")
        raise RuntimeError(f"Google Analytics API HTTP {response.status_code}: {detail}")
    return response.json()


def report_rows(session, endpoint: str, start: date, end: date,
                metrics: list[str], dimensions: list[str] | None = None,
                limit: int = 10, total: bool = False) -> dict:
    body = {
        "dateRanges": [{"startDate": start.isoformat(), "endDate": end.isoformat()}],
        "metrics": [{"name": metric} for metric in metrics],
        "limit": limit,
    }
    if dimensions:
        body["dimensions"] = [{"name": dimension} for dimension in dimensions]
        body["orderBys"] = [{"metric": {"metricName": metrics[-1]}, "desc": True}]
    if total:
        body["metricAggregations"] = ["TOTAL"]
    return post_json(session, endpoint, body)


def metric_values(data: dict) -> dict[str, float]:
    headers = [item["name"] for item in data.get("metricHeaders", [])]
    rows = data.get("rows", [])
    values = rows[0].get("metricValues", []) if rows else []
    return {name: float(item.get("value", "0")) for name, item in zip(headers, values)}


def format_number(value: float) -> str:
    return f"{value:,.0f}".replace(",", " ")


def percent_change(current: float, previous: float) -> str:
    if previous == 0:
        return "nėra palyginimo bazės" if current == 0 else "naujas augimas (ankstesnis laikotarpis: 0)"
    return f"{(current - previous) / previous * 100:+.1f} %"


def build_report(session, property_id: str, today: date) -> str:
    end = today - timedelta(days=1)
    start = end - timedelta(days=6)
    previous_end = start - timedelta(days=1)
    previous_start = previous_end - timedelta(days=6)
    endpoint = (
        "https://analyticsdata.googleapis.com/v1beta/properties/"
        + quote(property_id, safe="")
        + ":runReport"
    )
    metrics = ["activeUsers", "newUsers", "sessions", "screenPageViews"]
    current_data = report_rows(session, endpoint, start, end, metrics, limit=1)
    previous_data = report_rows(session, endpoint, previous_start, previous_end, metrics, limit=1)
    current, previous = metric_values(current_data), metric_values(previous_data)

    lines = [
        "# ARO Vet – Google Analytics ataskaita",
        "",
        f"GA4 nuosavybės ID: {property_id}",
        f"Laikotarpis: {start} – {end}",
        f"Palyginimas: {previous_start} – {previous_end}",
        "",
        "## Pagrindiniai rodikliai",
        "",
        "| Rodiklis | Paskutinės 7 d. | Pokytis prieš ankstesnes 7 d. |",
        "|---|---:|---:|",
    ]
    labels = {
        "activeUsers": "Aktyvūs naudotojai",
        "newUsers": "Nauji naudotojai",
        "sessions": "Sesijos / apsilankymai",
        "screenPageViews": "Puslapių peržiūros",
    }
    for key, label in labels.items():
        now, old = current.get(key, 0), previous.get(key, 0)
        lines.append(f"| {label} | {format_number(now)} | {percent_change(now, old)} |")

    channels = report_rows(
        session, endpoint, start, end, ["sessions"],
        ["sessionDefaultChannelGroup"], limit=50, total=True,
    )
    lines += ["", "## Sesijos pagal kanalą", "", "| Kanalas | Sesijos |", "|---|---:|"]
    for row in channels.get("rows", []):
        channel = row.get("dimensionValues", [{}])[0].get("value", "Nežinomas")
        value = float(row.get("metricValues", [{}])[0].get("value", "0"))
        lines.append(f"| {channel} | {format_number(value)} |")
    if not channels.get("rows"):
        lines.append("| Duomenų nėra | – |")
    organic = sum(
        float(row.get("metricValues", [{}])[0].get("value", "0"))
        for row in channels.get("rows", [])
        if row.get("dimensionValues", [{}])[0].get("value") == "Organic Search"
    )
    lines += ["", f"Organinės paieškos sesijos: **{format_number(organic)}**", ""]

    pages = report_rows(session, endpoint, start, end, ["screenPageViews"], ["pagePath"], limit=10)
    lines += ["## Daugiausia peržiūrėti puslapiai", ""]
    if pages.get("rows"):
        for row in pages["rows"]:
            path = row.get("dimensionValues", [{}])[0].get("value", "/")
            views = float(row.get("metricValues", [{}])[0].get("value", "0"))
            lines.append(f"- {path} – {format_number(views)} peržiūrų")
    else:
        lines.append("_GA4 puslapių duomenų šiam laikotarpiui nėra._")

    lines += [
        "",
        "Pastaba: ataskaitoje naudojami tik agreguoti GA4 duomenys. "
        "Atskiri lankytojai ar jų asmens duomenys nerenkami.",
        "Ši ARO Vet ataskaita saugoma atskirai nuo Pet traffic analitikos.",
    ]
    return "\n".join(lines) + "\n"


def main() -> int:
    OUT.parent.mkdir(parents=True, exist_ok=True)
    raw = os.environ.get("GOOGLE_SERVICE_ACCOUNT_JSON", "").strip()
    property_id = os.environ.get("ARO_VET_GA4_PROPERTY_ID", "").strip()
    if not raw or not property_id:
        missing = [
            name for name, value in (
                ("GOOGLE_SERVICE_ACCOUNT_JSON", raw),
                ("ARO_VET_GA4_PROPERTY_ID", property_id),
            ) if not value
        ]
        OUT.write_text(
            "# ARO Vet – Google Analytics ataskaita\n\n"
            f"## Būsena: neprijungta\n\nTrūksta nustatymų: {', '.join(missing)}.\n",
            encoding="utf-8",
        )
        print("ARO Vet analytics configuration missing.", file=sys.stderr)
        return 1

    try:
        from google.oauth2 import service_account
        from google.auth.transport.requests import AuthorizedSession

        credentials = service_account.Credentials.from_service_account_info(
            json.loads(raw),
            scopes=["https://www.googleapis.com/auth/analytics.readonly"],
        )
        session = AuthorizedSession(credentials)
        OUT.write_text(build_report(session, property_id, date.today()), encoding="utf-8")
        print(f"ARO Vet analytics report created: {OUT}")
        return 0
    except Exception as exc:
        OUT.write_text(
            "# ARO Vet – Google Analytics ataskaita\n\n"
            f"## Būsena: klaida\n\nGoogle Analytics užklausa nepavyko: {type(exc).__name__}: {exc}\n",
            encoding="utf-8",
        )
        print(f"ARO Vet analytics error: {type(exc).__name__}: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
