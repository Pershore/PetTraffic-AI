#!/usr/bin/env python3
"""Daily live-site health check using only the Python standard library."""
from __future__ import annotations

from html.parser import HTMLParser
from urllib.error import HTTPError, URLError
from urllib.parse import urljoin, urlparse
from urllib.request import Request, urlopen, HTTPRedirectHandler, build_opener
import sys
import xml.etree.ElementTree as ET

BASE = "https://pettraffic-ai.pages.dev"
TIMEOUT = 18
USER_AGENT = "PetTrafficSiteMonitor/1.0 (+https://pettraffic-ai.pages.dev/)"

try:
    from .validate_site import REQUIRED_RETIRED_ARTICLE_REDIRECTS
except ImportError:  # Running this file directly from the agent/ directory.
    from validate_site import REQUIRED_RETIRED_ARTICLE_REDIRECTS


class Links(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.values: list[str] = []

    def handle_starttag(self, tag: str, attrs) -> None:
        attrs = dict(attrs)
        for key in ("href", "src"):
            value = attrs.get(key)
            if value:
                self.values.append(value)


def fetch(url: str) -> tuple[int, str, str]:
    request = Request(url, headers={"User-Agent": USER_AGENT})
    try:
        with urlopen(request, timeout=TIMEOUT) as response:
            body = response.read(2_000_000).decode("utf-8", errors="replace")
            return response.status, body, response.geturl()
    except HTTPError as exc:
        body = exc.read(500_000).decode("utf-8", errors="replace")
        return exc.code, body, exc.geturl()
    except (URLError, TimeoutError, OSError) as exc:
        return 0, "", str(exc)


class NoRedirectHandler(HTTPRedirectHandler):
    """Return the first redirect response so the monitor can verify its status."""

    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


def fetch_redirect(url: str) -> tuple[int, str]:
    """Fetch one URL without following redirects; return HTTP status and Location."""
    request = Request(url, headers={"User-Agent": USER_AGENT})
    opener = build_opener(NoRedirectHandler())
    try:
        with opener.open(request, timeout=TIMEOUT) as response:
            return response.status, response.headers.get("Location", "")
    except HTTPError as exc:
        return exc.code, exc.headers.get("Location", "")
    except (URLError, TimeoutError, OSError):
        return 0, ""


def main() -> int:
    failures: list[str] = []
    warnings: list[str] = []
    checked: set[str] = set()
    pages = [
        BASE + "/",
        BASE + "/about",
        BASE + "/privacy",
        BASE + "/sitemap.xml",
        BASE + "/robots.txt",
    ]

    sitemap_status, sitemap_body, _ = fetch(BASE + "/sitemap.xml")
    if sitemap_status != 200:
        failures.append(f"sitemap.xml returned HTTP {sitemap_status}")
    else:
        try:
            root = ET.fromstring(sitemap_body)
            ns = {"sm": "http://www.sitemaps.org/schemas/sitemap/0.9"}
            for node in root.findall(".//sm:loc", ns):
                if node.text:
                    pages.append(node.text.strip())
        except ET.ParseError as exc:
            failures.append(f"sitemap.xml is invalid: {exc}")

    internal_links: set[str] = set()
    external_links: set[str] = set()
    for page_url in dict.fromkeys(pages):
        status, body, final_url = fetch(page_url)
        checked.add(page_url)
        if status != 200:
            failures.append(f"{page_url} returned HTTP {status}")
            continue
        if final_url != page_url:
            failures.append(f"Canonical sitemap page redirected to {final_url}: {page_url}")
        if not page_url.endswith((".xml", ".txt")):
            parser = Links()
            parser.feed(body)
            for raw in parser.values:
                absolute = urljoin(final_url, raw)
                parsed = urlparse(absolute)
                if parsed.scheme not in {"http", "https"}:
                    continue
                normalized = parsed._replace(fragment="").geturl()
                if parsed.netloc == urlparse(BASE).netloc:
                    internal_links.add(normalized)
                else:
                    external_links.add(normalized)

    for url in sorted(internal_links - checked):
        status, _, final_url = fetch(url)
        checked.add(url)
        if status != 200:
            failures.append(f"Internal link returned HTTP {status}: {url}")
        elif final_url != url:
            failures.append(f"Internal link is not canonical and redirects to {final_url}: {url}")

    for url in sorted(external_links):
        status, _, _ = fetch(url)
        if status == 0 or status >= 500:
            warnings.append(f"External source may be unavailable (HTTP {status}): {url}")
        elif status >= 400 and status not in {403, 429}:
            warnings.append(f"External source returned HTTP {status}: {url}")

    # Verify the deployed Cloudflare Pages redirects, not just the static file.
    for source, destination in REQUIRED_RETIRED_ARTICLE_REDIRECTS.items():
        source_url = BASE + source
        expected_location = BASE + ("/" if destination == "/" else destination)
        redirect_status, raw_location = fetch_redirect(source_url)
        actual_location = urljoin(source_url, raw_location) if raw_location else ""
        if redirect_status != 301:
            failures.append(f"Retired article URL should return HTTP 301, got {redirect_status}: {source}")
        elif actual_location != expected_location:
            failures.append(
                f"Retired article redirect points to {actual_location or 'no Location header'}, "
                f"expected {expected_location}: {source}"
            )

    missing_url = BASE + "/pettraffic-monitor-expected-404"
    missing_status, missing_body, _ = fetch(missing_url)
    if missing_status != 404:
        failures.append(f"Unknown URL should return HTTP 404, got {missing_status}")
    if "Puslapis nerastas" not in missing_body:
        failures.append("Custom 404 page text was not found")

    robots_status, robots_body, _ = fetch(BASE + "/robots.txt")
    if robots_status == 200 and BASE + "/sitemap.xml" not in robots_body:
        failures.append("robots.txt does not advertise the sitemap URL")

    print(f"Pet traffic live check: {len(checked)} internal URLs checked.")
    if warnings:
        print("\nExternal-link warnings (non-blocking):")
        for item in warnings:
            print(f" - {item}")
    if failures:
        print("\nLIVE SITE CHECK FAILED:")
        for item in failures:
            print(f" - {item}")
        return 1
    print("LIVE SITE CHECK PASSED: core pages, internal links, sitemap, robots.txt, 404 behavior and 20 permanent retired-article redirects.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
