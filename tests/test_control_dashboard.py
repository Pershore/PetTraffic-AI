from pathlib import Path
import re
import unittest
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
DASHBOARD = ROOT / "site" / "control" / "index.html"
SCRIPT = ROOT / "site" / "control" / "control.js"
SITEMAP = ROOT / "site" / "sitemap.xml"


class ControlDashboardTests(unittest.TestCase):
    def test_dashboard_is_explicitly_noindex_and_has_no_canonical(self):
        html = DASHBOARD.read_text(encoding="utf-8")
        self.assertRegex(html, re.compile(r'<meta\s+name=["\']robots["\']\s+content=["\'][^"\']*noindex', re.I))
        self.assertNotRegex(html, re.compile(r'<link\s+rel=["\']canonical', re.I))

    def test_dashboard_is_not_in_public_sitemap(self):
        root = ET.parse(SITEMAP).getroot()
        urls = [node.text or "" for node in root.iter() if node.tag.endswith("loc")]
        self.assertFalse(any("/control/" in url for url in urls))

    def test_dashboard_uses_live_read_only_sources(self):
        script = SCRIPT.read_text(encoding="utf-8")
        self.assertIn("api.github.com/repos/", script)
        self.assertIn("/actions/runs?per_page=100", script)
        self.assertIn("/health", script)
        self.assertNotIn("method:\"POST\"", script)
        self.assertNotIn("method:\"DELETE\"", script)
        self.assertNotIn("createWorkflowDispatch", script)

    def test_dashboard_contains_no_secret_values_or_secret_headers(self):
        combined = DASHBOARD.read_text(encoding="utf-8") + SCRIPT.read_text(encoding="utf-8")
        self.assertNotRegex(combined, re.compile(r"\bAI\b"))
        for forbidden in ("GOOGLE_SERVICE_ACCOUNT_JSON", "CLOUDFLARE_API_TOKEN", "Authorization: Bearer"):
            self.assertNotIn(forbidden, combined)


if __name__ == "__main__":
    unittest.main()
