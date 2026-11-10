#!/usr/bin/env python3
"""Paprastas vietinių HTML nuorodų tikrintuvas. Be išorinių paketų."""
from pathlib import Path
from html.parser import HTMLParser
from urllib.parse import urlparse, unquote

ROOT = Path(__file__).resolve().parents[1] / "site"

class LinkParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.links = []
    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        for key in ("href", "src"):
            value = attrs.get(key)
            if value:
                self.links.append(value)

def main():
    errors = []
    for html in ROOT.rglob("*.html"):
        parser = LinkParser()
        parser.feed(html.read_text(encoding="utf-8"))
        for link in parser.links:
            if link.startswith(("http://", "https://", "mailto:", "tel:", "#", "data:")):
                continue
            path = unquote(urlparse(link).path)
            if not path:
                continue
            target = (ROOT / path.lstrip("/")) if path.startswith("/") else (html.parent / path)
            if not target.exists():
                errors.append((html.relative_to(ROOT), link))
    if errors:
        print("Galimos neveikiančios vietinės nuorodos:")
        for page, link in errors:
            print(f" - {page}: {link}")
        raise SystemExit(1)
    print("Vietinių HTML nuorodų patikra baigta. Nerasta trūkstamų tikslinių failų.")

if __name__ == "__main__":
    main()
