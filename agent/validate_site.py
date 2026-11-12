#!/usr/bin/env python3
"""Pet traffic static-site checks. Uses only Python's standard library."""
from __future__ import annotations

from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlparse
import json
import re
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
        self.image_errors: list[str] = []
        self.meta_properties: dict[str, list[str]] = {}
        self.jsonld_scripts: list[str] = []
        self.in_jsonld = False
        self.current_jsonld: list[str] = []
        self.target_blank_errors: list[str] = []
        self.live_status_ids: set[str] = set()

    def handle_starttag(self, tag: str, attrs) -> None:
        attrs = dict(attrs)
        if tag == "meta":
            property_name = (attrs.get("property") or "").lower()
            if property_name:
                self.meta_properties.setdefault(property_name, []).append((attrs.get("content") or "").strip())
        if tag == "script" and (attrs.get("type") or "").lower() == "application/ld+json":
            self.in_jsonld = True
            self.current_jsonld = []
        if tag == "a" and (attrs.get("target") or "").lower() == "_blank":
            rel_values = set((attrs.get("rel") or "").lower().split())
            if "noopener" not in rel_values:
                self.target_blank_errors.append("target=_blank link is missing rel=noopener")
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
            if attrs.get("role") == "status" and attrs.get("aria-live") == "polite":
                self.live_status_ids.add(attrs["id"])
        if tag == "img" and not attrs.get("alt", "").strip():
            self.image_errors.append("image is missing a descriptive alt attribute")
        for key in ("href", "src"):
            value = attrs.get(key)
            if value:
                self.links.append(value)

    def handle_endtag(self, tag: str) -> None:
        if tag == "title":
            self.in_title = False
        if tag == "script" and self.in_jsonld:
            self.jsonld_scripts.append("".join(self.current_jsonld).strip())
            self.in_jsonld = False
            self.current_jsonld = []

    def handle_data(self, data: str) -> None:
        if self.in_title:
            self.title_parts.append(data)
        if self.in_jsonld:
            self.current_jsonld.append(data)


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
            page_text = page.read_text(encoding="utf-8")
            parser.feed(page_text)
        except (OSError, UnicodeError) as exc:
            errors.append(f"{page.relative_to(ROOT)}: cannot read HTML: {exc}")
            continue
        parsed_pages[page.resolve()] = parser
        rel = page.relative_to(ROOT)
        if rel.as_posix() == "index.html" and "article-results-status" not in parser.live_status_ids:
            errors.append(f"{rel}: article search needs a polite live status region")
        related_blocks = re.findall(
            r'<div class="notice">\\s*<strong>Susiję straipsniai:</strong>(.*?)</div>',
            page_text, flags=re.IGNORECASE | re.DOTALL,
        )
        for block in related_blocks:
            related_hrefs = re.findall(r'\\bhref=["\\']([^"\\']+)["\\']', block, flags=re.IGNORECASE)
            if len(related_hrefs) != len(set(related_hrefs)):
                errors.append(f"{rel}: related-article block contains duplicate destinations")
        if parser.image_errors:
            errors.extend(f"{rel}: {message}" for message in parser.image_errors)
        if parser.target_blank_errors:
            errors.extend(f"{rel}: {message}" for message in parser.target_blank_errors)
        for index, raw_jsonld in enumerate(parser.jsonld_scripts, start=1):
            try:
                structured = json.loads(raw_jsonld)
            except json.JSONDecodeError as exc:
                errors.append(f"{rel}: invalid JSON-LD block {index}: {exc}")
                continue
            entries = structured if isinstance(structured, list) else [structured]
            for entry in entries:
                if not isinstance(entry, dict) or not entry.get("@type"):
                    errors.append(f"{rel}: JSON-LD block {index} must contain an object with @type")
                    continue
                context = entry.get("@context")
                if context not in ("https://schema.org", "http://schema.org") and not isinstance(context, (dict, list)):
                    errors.append(f"{rel}: JSON-LD block {index} is missing a valid schema.org @context")
        if "__CARDS__" in page_text:
            errors.append(f"{rel}: unresolved __CARDS__ template marker")
        if parser.lang != "lt":
            errors.append(f"{rel}: expected <html lang='lt'>")
        if not "".join(parser.title_parts).strip():
            errors.append(f"{rel}: missing or empty <title>")
        if parser.h1_count != 1:
            errors.append(f"{rel}: expected exactly one H1, found {parser.h1_count}")
        if not parser.descriptions or not parser.descriptions[0]:
            errors.append(f"{rel}: missing meta description")
        if len(parser.canonicals) != 1:
            errors.append(f"{rel}: expected exactly one canonical URL")
        elif urlparse(parser.canonicals[0]).scheme != "https" or urlparse(parser.canonicals[0]).netloc != urlparse(BASE_URL).netloc:
            errors.append(f"{rel}: canonical URL must use {BASE_URL}")
        else:
            expected_path = "/" if rel.as_posix() == "index.html" else "/" + rel.as_posix()
            expected_canonical = BASE_URL + expected_path
            if parser.canonicals[0] != expected_canonical:
                errors.append(f"{rel}: canonical URL should be {expected_canonical}")

        if rel.as_posix() == "index.html" or "articles" in rel.parts:
            for property_name in ("og:title", "og:description", "og:url", "og:image", "og:image:alt"):
                values = parser.meta_properties.get(property_name, [])
                if len(values) != 1 or not values[0]:
                    errors.append(f"{rel}: expected exactly one non-empty {property_name} metadata value")
            og_urls = parser.meta_properties.get("og:url", [])
            if parser.canonicals and og_urls != [parser.canonicals[0]]:
                errors.append(f"{rel}: og:url must match the canonical URL")
            og_images = parser.meta_properties.get("og:image", [])
            if og_images:
                image_url = urlparse(og_images[0])
                if image_url.scheme != "https" or image_url.netloc != urlparse(BASE_URL).netloc:
                    errors.append(f"{rel}: og:image must use an HTTPS Pet traffic asset URL")
                else:
                    image_path = ROOT / unquote(image_url.path.lstrip("/"))
                    if not image_path.exists():
                        errors.append(f"{rel}: og:image asset does not exist: {og_images[0]}")

    for page, parser in parsed_pages.items():
        for link in parser.links:
            parsed = urlparse(link)
            if parsed.scheme.lower() == "http":
                errors.append(f"{page.relative_to(ROOT)}: external link must use HTTPS: {link}")
            elif parsed.scheme and parsed.scheme.lower() not in {"https", "mailto", "tel"}:
                errors.append(f"{page.relative_to(ROOT)}: unsupported link scheme: {link}")
            elif parsed.netloc and not parsed.scheme:
                errors.append(f"{page.relative_to(ROOT)}: protocol-relative link must use HTTPS: {link}")
            target = local_target(page, link)
            if target is not None and not target.exists():
                errors.append(f"{page.relative_to(ROOT)}: broken local link or asset: {link}")
            if target is not None and parsed.fragment and target.suffix == ".html" and target.exists():
                target_parser = parsed_pages.get(target)
                if target_parser and unquote(parsed.fragment) not in target_parser.ids:
                    errors.append(f"{page.relative_to(ROOT)}: missing fragment #{parsed.fragment} in {target.relative_to(ROOT)}")

    # Guard against retired public branding and partner tracking returning.
    forbidden_patterns = {
        r"\bAI\b": "standalone AI label",
        r"ARO\s*Vet|arovetvaistine": "retired partner name",
        r"data-partner|partner_outbound_click": "retired partner tracking",
        r"aro-vet\.html|gargzdai-augintiniams": "retired partner page",
    }
    for public_file in ROOT.rglob("*"):
        if public_file.is_file() and public_file.suffix.lower() in {".html", ".js", ".css", ".svg", ".xml", ".txt"}:
            try:
                content = public_file.read_text(encoding="utf-8")
            except (OSError, UnicodeError) as exc:
                errors.append(f"{public_file.relative_to(ROOT)}: cannot inspect public file: {exc}")
                continue
            for pattern, label in forbidden_patterns.items():
                if re.search(pattern, content):
                    errors.append(f"{public_file.relative_to(ROOT)}: contains forbidden {label}")

    sitemap_urls: set[str] = set()
    sitemap_entries: list[str] = []
    sitemap = ROOT / "sitemap.xml"
    if not sitemap.exists():
        errors.append("Missing site/sitemap.xml")
    else:
        try:
            root = ET.parse(sitemap).getroot()
            ns = {"sm": "http://www.sitemaps.org/schemas/sitemap/0.9"}
            for loc in root.findall(".//sm:loc", ns):
                url = (loc.text or "").strip()
                parsed_url = urlparse(url)
                if parsed_url.scheme != "https" or parsed_url.netloc != urlparse(BASE_URL).netloc:
                    errors.append(f"sitemap.xml: URL outside canonical site: {url}")
                    continue
                if url in sitemap_entries:
                    errors.append(f"sitemap.xml: duplicate URL: {url}")
                sitemap_entries.append(url)
                sitemap_urls.add(url)
                path = unquote(parsed_url.path)
                target = ROOT / (path.lstrip("/") or "index.html")
                if path == "/":
                    target = ROOT / "index.html"
                elif path.endswith("/"):
                    target = ROOT / path.lstrip("/") / "index.html"
                if not target.exists():
                    errors.append(f"sitemap.xml: URL has no matching file: {url}")
        except ET.ParseError as exc:
            errors.append(f"sitemap.xml: invalid XML: {exc}")

    expected_sitemap_urls = {
        parser.canonicals[0]
        for parser in parsed_pages.values()
        if parser.canonicals
    }
    if sitemap_urls != expected_sitemap_urls:
        missing = sorted(expected_sitemap_urls - sitemap_urls)
        extra = sorted(sitemap_urls - expected_sitemap_urls)
        errors.append(f"sitemap.xml: URLs must exactly match canonical HTML pages (missing={missing}, extra={extra})")

    redirects = ROOT / "_redirects"
    redirect_map: dict[str, str] = {}
    if not redirects.exists():
        errors.append("Missing site/_redirects")
    else:
        for line_number, line in enumerate(redirects.read_text(encoding="utf-8").splitlines(), start=1):
            stripped = line.strip()
            if not stripped or stripped.startswith("#"):
                continue
            parts = stripped.split()
            if len(parts) != 3:
                errors.append(f"_redirects:{line_number}: expected source destination 301")
                continue
            source, destination, status = parts
            if not source.startswith("/") or not destination.startswith("/"):
                errors.append(f"_redirects:{line_number}: source and destination must be site paths")
                continue
            if status != "301":
                errors.append(f"_redirects:{line_number}: retired article redirects must use 301")
            if source in redirect_map:
                errors.append(f"_redirects:{line_number}: duplicate redirect source {source}")
            redirect_map[source] = destination
            source_path = ROOT / unquote(source.lstrip("/"))
            if source_path.exists():
                errors.append(f"_redirects:{line_number}: redirect source still exists as a published file: {source}")
            destination_path = ROOT / "index.html" if destination == "/" else ROOT / unquote(destination.lstrip("/"))
            if not destination_path.exists():
                errors.append(f"_redirects:{line_number}: destination file does not exist: {destination}")
            destination_url = BASE_URL + ("/" if destination == "/" else destination)
            if destination_url not in sitemap_urls:
                errors.append(f"_redirects:{line_number}: destination is not in sitemap.xml: {destination}")
        for source, destination in redirect_map.items():
            if destination in redirect_map:
                errors.append(f"_redirects: chained redirect is not allowed: {source} -> {destination}")

    robots = ROOT / "robots.txt"
    if not robots.exists():
        errors.append("Missing site/robots.txt")
    else:
        robots_content = robots.read_text(encoding="utf-8")
        expected_sitemap = BASE_URL + "/sitemap.xml"
        if not re.search(rf"(?im)^Sitemap:\s*{re.escape(expected_sitemap)}\s*$", robots_content):
            errors.append(f"robots.txt: expected Sitemap: {expected_sitemap}")

    backups = [p for p in ROOT.rglob("*") if p.is_file() and (p.suffix.lower() in {".bak", ".old", ".backup"} or p.name.endswith("~"))]
    for backup in backups:
        errors.append(f"Backup file must not be published inside site/: {backup.relative_to(ROOT)}")

    if errors:
        print("Pet traffic validation FAILED:")
        for error in errors:
            print(f" - {error}")
        return 1
    print(f"Pet traffic validation PASSED: {len(pages)} HTML pages, alt text, secure links, JSON-LD, canonical/OG metadata, sitemap, 301 redirects and robots.txt.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
