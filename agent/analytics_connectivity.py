#!/usr/bin/env python3
"""Independent, read-only connectivity checks for GA4 and Search Console."""
from __future__ import annotations

from datetime import date, timedelta
from pathlib import Path
from urllib.parse import quote
import json
import os
import sys

OUT = Path("reports/analytics-connectivity.md")


def check_api(session, name: str, url: str, body: dict) -> tuple[bool, str]:
    try:
        response = session.post(url, json=body, timeout=25)
        if not response.ok:
            detail = response.text[:500].replace("\n", " ")
            return False, f"HTTP {response.status_code}: {detail}"
        payload = response.json()
        if not isinstance(payload, dict):
            return False, "API returned an unexpected response format"
        return True, "API request succeeded"
    except Exception as exc:
        return False, f"{type(exc).__name__}: {str(exc)[:300]}"


def run_independent_checks(session, ga_url: str, ga_body: dict,
                           gsc_url: str, gsc_body: dict) -> dict[str, tuple[bool, str]]:
    """Run both APIs even if the first one fails or times out."""
    ga_result = check_api(session, "GA4", ga_url, ga_body)
    gsc_result = check_api(session, "Search Console", gsc_url, gsc_body)
    return {"GA4": ga_result, "Search Console": gsc_result}


def check_api_get(session, url: str) -> tuple[bool, str]:
    """Probe GA4 metadata without running a report query."""
    try:
        response = session.get(url, timeout=25)
        if not response.ok:
            detail = response.text[:500].replace("\\n", " ")
            return False, f"HTTP {response.status_code}: {detail}"
        payload = response.json()
        if not isinstance(payload, dict):
            return False, "API returned an unexpected response format"
        return True, "Metadata endpoint responded successfully"
    except Exception as exc:
        return False, f"{type(exc).__name__}: {str(exc)[:300]}"


def main() -> int:
    raw = os.environ.get("GOOGLE_SERVICE_ACCOUNT_JSON", "").strip()
    ga4_id = os.environ.get("GA4_PROPERTY_ID", "").strip()
    gsc_site = os.environ.get("GSC_SITE_URL", "").strip()
    if not raw or not ga4_id or not gsc_site:
        missing = [key for key, value in (
            ("GOOGLE_SERVICE_ACCOUNT_JSON", raw),
            ("GA4_PROPERTY_ID", ga4_id),
            ("GSC_SITE_URL", gsc_site),
        ) if not value]
        print("Missing configuration: " + ", ".join(missing), file=sys.stderr)
        return 2

    try:
        from google.oauth2 import service_account
        from google.auth.transport.requests import AuthorizedSession
        info = json.loads(raw)
        credentials = service_account.Credentials.from_service_account_info(
            info,
            scopes=[
                "https://www.googleapis.com/auth/analytics.readonly",
                "https://www.googleapis.com/auth/webmasters.readonly",
            ],
        )
        session = AuthorizedSession(credentials)
    except Exception as exc:
        OUT.parent.mkdir(parents=True, exist_ok=True)
        OUT.write_text(
            "# Google API connectivity\n\n"
            f"Authentication setup failed: {type(exc).__name__}: {str(exc)[:300]}\n",
            encoding="utf-8",
        )
        print(f"Authentication setup failed: {type(exc).__name__}", file=sys.stderr)
        return 1

    today = date.today()
    ga_end = today - timedelta(days=1)
    # Use the smallest possible date range to distinguish report-endpoint latency
    # from any cost associated with a multi-day reporting window.
    ga_start = ga_end
    gsc_end = today - timedelta(days=3)
    gsc_start = gsc_end - timedelta(days=6)

    ga_url = (
        "https://analyticsdata.googleapis.com/v1beta/properties/"
        + quote(ga4_id, safe="")
        + ":runReport"
    )
    ga_metadata_url = (
        "https://analyticsdata.googleapis.com/v1beta/properties/"
        + quote(ga4_id, safe="")
        + "/metadata"
    )
    gsc_url = (
        "https://searchconsole.googleapis.com/webmasters/v3/sites/"
        + quote(gsc_site, safe="")
        + "/searchAnalytics/query"
    )

    ga_metadata_ok, ga_metadata_message = check_api_get(session, ga_metadata_url)
    results = run_independent_checks(
        session,
        ga_url,
        {
            "dateRanges": [{"startDate": ga_start.isoformat(), "endDate": ga_end.isoformat()}],
            "metrics": [{"name": "sessions"}],
            "limit": 1,
        },
        gsc_url,
        {
            "startDate": gsc_start.isoformat(),
            "endDate": gsc_end.isoformat(),
            "rowLimit": 1,
        },
    )
    ga_ok, ga_message = results["GA4"]
    gsc_ok, gsc_message = results["Search Console"]

    lines = [
        "# Google API connectivity check",
        "",
        f"Checked: {date.today().isoformat()}",
        "",
        "| API check | Result | Detail |",
        "|---|---|---|",
        f"| GA4 metadata | {'OK' if ga_metadata_ok else 'FAILED'} | {ga_metadata_message.replace('|', '/')} |",
        f"| GA4 report (1 day) | {'OK' if ga_ok else 'FAILED'} | {ga_message.replace('|', '/')} |",
        f"| Search Console | {'OK' if gsc_ok else 'FAILED'} | {gsc_message.replace('|', '/')} |",
        "",
        "This check requests aggregate metrics only; it does not retrieve search query strings or individual visitor data.",
    ]
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("\n".join(lines))
    return 0 if ga_metadata_ok or ga_ok or gsc_ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
