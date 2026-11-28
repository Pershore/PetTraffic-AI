"""Tests for Cloudflare Pages extensionless canonical URLs."""

import unittest

from agent.validate_site import ROOT, canonical_public_path, local_target


class CanonicalCleanUrlTests(unittest.TestCase):
    def test_html_source_files_map_to_extensionless_public_paths(self):
        cases = {
            "index.html": "/",
            "about.html": "/about",
            "privacy.html": "/privacy",
            "articles/kada-kreiptis-i-veterinara.html": "/articles/kada-kreiptis-i-veterinara",
            "articles/kate-negali-pasislapinti-skubi-pagalba.html": "/articles/kate-negali-pasislapinti-skubi-pagalba",
        }
        for source, expected in cases.items():
            with self.subTest(source=source):
                self.assertEqual(canonical_public_path(source), expected)

    def test_extensionless_internal_links_resolve_to_source_html_files(self):
        cases = {
            "/about": ROOT / "about.html",
            "/privacy": ROOT / "privacy.html",
            "/articles/kate-viduriuoja-ka-daryti": ROOT / "articles" / "kate-viduriuoja-ka-daryti.html",
        }
        for url_path, expected_file in cases.items():
            with self.subTest(url_path=url_path):
                self.assertEqual(local_target(ROOT / "index.html", url_path), expected_file.resolve())

    def test_sitemap_lists_only_canonical_extensionless_html_routes(self):
        sitemap = (ROOT / "sitemap.xml").read_text(encoding="utf-8")
        self.assertNotIn(".html</loc>", sitemap)
        for route in ("/about", "/privacy", "/articles/kate-viduriuoja-ka-daryti"):
            self.assertIn(f"https://pettraffic-ai.pages.dev{route}</loc>", sitemap)


if __name__ == "__main__":
    unittest.main()
