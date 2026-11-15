from pathlib import Path
import re
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
        self.assertRegex(html, re.compile(r'<meta\s+name=["\']robots["\']\s+content=["\'][^"\']*noindex', re.I))
        self.assertNotRegex(html, re.compile(r'<link\s+rel=["\']canonical', re.I))

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

    def test_dashboard_uses_newest_analytics_and_topic_snapshots(self):
        script = SCRIPT.read_text(encoding="utf-8")
        self.assertIn("function latestSnapshot(archive)", script)
        self.assertIn('const s=latestSnapshot(state.analytics)', script)
        self.assertIn("const gsc=s?.search_console_details", script)
        self.assertIn("const t=latestSnapshot(state.topics)", script)
        self.assertIn('Date.parse(snapshot.generated_at||"")', script)

    def test_dashboard_uses_lithuanian_day_boundaries_and_flags_incomplete_agent_results(self):
        script = SCRIPT.read_text(encoding="utf-8")
        self.assertIn("const localDateOf = value =>", script)
        self.assertIn("localDateOf(daily.created_at)!==localDate()", script)
        self.assertNotIn('latestEvent("control-center.yml","schedule")', script)
        self.assertNotIn("Kasdien 10:40 LT", script)
        self.assertIn("Po daily-suite / Lighthouse / Worker deploy", script)
        self.assertIn('core.status==="needs_evidence"||gaps>0||degraded', script)
        self.assertIn('["error","no data","invalid_json","invalid json","failed"]', script)

    def test_command_panel_exposes_only_owner_comment_commands(self):
        html = DASHBOARD.read_text(encoding="utf-8")
        script = SCRIPT.read_text(encoding="utf-8")
        for command in (
            "/pettraffic-run-daily-suite",
            "/pettraffic-sync-latest",
            "/pettraffic-run-control-center",
            "/pettraffic-run-lighthouse",
            "/pettraffic-run-site-check",
            "/pettraffic-run-connectivity",
            "/pettraffic-run-worker-diagnostics",
        ):
            with self.subTest(command=command):
                self.assertIn(command, html)
        self.assertIn('id="view-commands"', html)
        self.assertIn('href="https://github.com/Pershore/PetTraffic&#45;&#65;&#73;/issues/145#new_comment_field"', html)
        self.assertIn("data-copy-command", html)
        self.assertIn("navigator.clipboard.writeText", script)
        self.assertNotIn('method:"POST"', script)
        self.assertNotIn("createWorkflowDispatch", script)

    def test_dashboard_contains_no_secret_values_or_secret_headers(self):
        combined = DASHBOARD.read_text(encoding="utf-8") + SCRIPT.read_text(encoding="utf-8")
        self.assertNotRegex(combined, re.compile(r"\bAI\b"))
        for forbidden in ("GOOGLE_SERVICE_ACCOUNT_JSON", "CLOUDFLARE_API_TOKEN", "Authorization: Bearer"):
            self.assertNotIn(forbidden, combined)


if __name__ == "__main__":
    unittest.main()
