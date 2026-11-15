from pathlib import Path
import unittest
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
DASHBOARD = ROOT / "site" / "control" / "index.html"
SCRIPT = ROOT / "site" / "control" / "control.js"
SITEMAP = ROOT / "site" / "sitemap.xml"
REDIRECTS = ROOT / "site" / "_redirects"


class ControlDashboardTests(unittest.TestCase):
    def test_dashboard_is_explicitly_noindex_and_has_no_canonical(self):
        html = DASHBOARD.read_text(encoding="utf-8")
        self.assertIn('<meta name="robots" content="noindex,nofollow">', html)
        self.assertNotIn('rel="canonical"', html)

    def test_dashboard_is_not_in_public_sitemap(self):
        root = ET.parse(SITEMAP).getroot()
        urls = [node.text or "" for node in root.iter() if node.tag.endswith("loc")]
        self.assertFalse(any("/control/" in url or "/dashboard/" in url for url in urls))

    def test_requested_dashboard_url_rewrites_to_live_control_center(self):
        rules = REDIRECTS.read_text(encoding="utf-8").splitlines()
        self.assertIn("/dashboard /control/ 200", rules)
        self.assertIn("/dashboard/ /control/ 200", rules)
        self.assertTrue(DASHBOARD.is_file())

    def test_dashboard_uses_live_read_only_sources(self):
        script = SCRIPT.read_text(encoding="utf-8")
        self.assertIn("api.github.com/repos/", script)
        self.assertIn("/actions/runs?per_page=100", script)
        self.assertIn("/health", script)
        self.assertNotIn('method:"POST"', script)
        self.assertNotIn('method:"DELETE"', script)
        self.assertNotIn("createWorkflowDispatch", script)

    def test_dashboard_maps_live_sources_by_name(self):
        script = SCRIPT.read_text(encoding="utf-8")
        for source in (
            'runs: getJson(GH+"/actions/runs?per_page=100").then(x=>x.workflow_runs||[])',
            'prs: getJson(GH+"/pulls?state=open&per_page=50")',
            'commit: getJson(GH+"/commits/main")',
            'health: getJson(WORKER+"/health")',
            'site: fetch(SITE,{method:"HEAD",cache:"no-store"})',
            'analytics: loadAnalyticsArchive("analytics")',
            'topics: loadAnalyticsArchive("topic-radar")',
            'issue: getJson(GH+"/issues/145")',
        ):
            self.assertIn(source, script)
        self.assertIn("Object.keys(sources)", script)
        self.assertIn("state[sourceKeys[index]]=result.value", script)

    def test_dashboard_contains_no_secret_values_or_secret_headers(self):
        combined = DASHBOARD.read_text(encoding="utf-8") + SCRIPT.read_text(encoding="utf-8")
        self.assertNotIn("GOOGLE_SERVICE_ACCOUNT_JSON", combined)
        self.assertNotIn("CLOUDFLARE_API_TOKEN", combined)
        self.assertNotIn("Authorization: Bearer", combined)


if __name__ == "__main__":
    unittest.main()
