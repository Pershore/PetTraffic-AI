#!/usr/bin/env python3
"""Pet traffic static-site checks. Uses only Python's standard library."""
from __future__ import annotations

from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlparse
import sys
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1] / "site"
BASE_URL = "https://pettraffic-ai.pages.dev"


class PageParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.lang = None
        self.title_parts: list[str] = []
        self.in_title = False
        self.h1_count = 0
        self.descriptions: list[str] = []
        self.canonicals: list[str] = []
        self.ids: set[str] = set()
        self.links: list[str] = []

    def handle_starttag(self, tag: str, attrs) -> None:
        attrs = dict(attrs)
        if tag == "html":
            self.lang = attrs.get("lang")
        if tag == "title":
            self.in_title = True
        if tag == "h1":
            self.h1_count += 1
        if tag == "meta" and attrs.get("name", "").lower() == "description":
            self.descriptions.append(attrs.get("content", "").strip())
        if tag == "link" and attrs.get("rel", "").lower() == "canonical":
            self.canonicals.append(attrs.get("href", "").strip())
        if attrs.get("id"):
            self.ids.add(attrs["id"])
        for key in ("href", "src"):
            value = attrs.get(key)
            if value:
                self.links.append(value)

    def handle_endtag(self, tag: str) -> None:
        if tag == "title":
            self.in_title = False

    def handle_data(self, data: str) -> None:
        if self.in_title:
            self.title_parts.append(data)


def local_target(page: Path, link: str) -> Path | None:
    parsed = urlparse(link)
    if parsed.scheme or parsed.netloc or not parsed.path:
        return None
    path = unquote(parsed.path)
    if path.startswith("/"):
        target = ROOT / path.lstrip("/")
    else:
        target = page.parent / path
    if path.endswith("/"):
        target = target / "index.html"
    return target.resolve()


def main() -> int:
    errors: list[str] = []
    if not ROOT.is_dir():
        print(f"ERROR: site directory not found: {ROOT}")
        return 1

    pages = sorted(p for p in ROOT.rglob("*.html") if "assets" not in p.relative_to(ROOT).parts)
    if not pages:
        errors.append("No HTML pages found under site/")

    parsed_pages: dict[Path, PageParser] = {}
    for page in pages:
        parser = PageParser()
        try:
            parser.feed(page.read_text(encoding="utf-8"))
        except (OSError, UnicodeError) as exc:
            errors.append(f"{page.relative_to(ROOT)}: cannot read HTML: {exc}")
            continue
        parsed_pages[page.resolve()] = parser
        rel = page.relative_to(ROOT)
        if parser.lang != "lt":
            errors.append(f"{rel}: expected <html lang='lt'>")
        if not "".join(parser.title_parts).strip():
            errors.append(f"{rel}: missing or empty <title>")
        if parser.h1_count != 1:
            errors.append(f"{rel}: expected exactly one H1, found {parser.h1_count}")
        if not parser.descriptions or not parser.descriptions[0]:
            errors.append(f"{rel}: missing meta description")
        if len(parser.canonicals) != 1 or not parser.canonicals[0].startswith(BASE_URL):
            errors.append(f"{rel}: expected one canonical URL under {BASE_URL}")

    for page, parser in parsed_pages.items():
        for link in parser.links:
            parsed = urlparse(link)
            target = local_target(page, link)
            if target is not None and not target.exists():
                errors.append(f"{page.relative_to(ROOT)}: broken local link or asset: {link}")
            if target is not None and parsed.fragment and target.suffix == ".html" and target.exists():
                target_parser = parsed_pages.get(target)
                if target_parser and unquote(parsed.fragment) not in target_parser.ids:
                    errors.append(f"{page.relative_to(ROOT)}: missing fragment #{parsed.fragment} in {target.relative_to(ROOT)}")

    sitemap = ROOT / "sitemap.xml"
    if not sitemap.exists():
        errors.append("Missing site/sitemap.xml")
    else:
        try:
            root = ET.parse(sitemap).getroot()
            ns = {"sm": "http://www.sitemaps.org/schemas/sitemap/0.9"}
            for loc in root.findall(".//sm:loc", ns):
                url = (loc.text or "").strip()
                if not url.startswith(BASE_URL):
                    errors.append(f"sitemap.xml: URL outside canonical site: {url}")
                    continue
                path = unquote(urlparse(url).path)
                target = ROOT / (path.lstrip("/") or "index.html")
                if path == "/":
                    target = ROOT / "index.html"
                elif path.endswith("/"):
                    target = ROOT / path.lstrip("/") / "index.html"
                if not target.exists():
                    errors.append(f"sitemap.xml: URL has no matching file: {url}")
        except ET.ParseError as exc:
            errors.append(f"sitemap.xml: invalid XML: {exc}")

    robots = ROOT / "robots.txt"
    if not robots.exists() or "sitemap.xml" not in robots.read_text(encoding="utf-8").lower():
        errors.append("robots.txt: missing sitemap reference")

    backups = [p for p in ROOT.rglob("*") if p.is_file() and (p.suffix.lower() in {".bak", ".old", ".backup"} or p.name.endswith("~"))]
    for backup in backups:
        errors.append(f"Backup file must not be published inside site/: {backup.relative_to(ROOT)}")

    if errors:
        print("Pet traffic validation FAILED:")
        for error in errors:
            print(f" - {error}")
        return 1
    print(f"Pet traffic validation PASSED: {len(pages)} HTML pages, local links, SEO basics, sitemap and robots.txt.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
