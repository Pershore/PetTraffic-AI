#!/usr/bin/env python3
"""Daily live-site health check using only the Python standard library."""
from __future__ import annotations

from html.parser import HTMLParser
from urllib.error import HTTPError, URLError
from urllib.parse import urljoin, urlparse
from urllib.request import Request, urlopen
import sys
import xml.etree.ElementTree as ET

BASE = "https://pettraffic-ai.pages.dev"
TIMEOUT = 18
USER_AGENT = "PetTrafficSiteMonitor/1.0 (+https://pettraffic-ai.pages.dev/)"


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


def main() -> int:
    failures: list[str] = []
    warnings: list[str] = []
    checked: set[str] = set()
    pages = [
        BASE + "/",
        BASE + "/about.html",
        BASE + "/privacy.html",
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
        if page_url.endswith(".html") or page_url.endswith("/"):
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
        status, _, _ = fetch(url)
        checked.add(url)
        if status != 200:
            failures.append(f"Internal link returned HTTP {status}: {url}")

    for url in sorted(external_links):
        status, _, _ = fetch(url)
        if status == 0 or status >= 500:
            warnings.append(f"External source may be unavailable (HTTP {status}): {url}")
        elif status >= 400 and status not in {403, 429}:
            warnings.append(f"External source returned HTTP {status}: {url}")

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
    print("LIVE SITE CHECK PASSED: core pages, internal links, sitemap, robots.txt and 404 behavior.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
