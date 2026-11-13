import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
WORKFLOW = (ROOT / ".github" / "workflows" / "worker-cron-diagnostic.yml").read_text(encoding="utf-8")


class WorkerCronDiagnosticSecurityTests(unittest.TestCase):
    def test_cloudflare_token_is_only_used_for_cloudflare_api_and_wrangler(self):
        cloudflare_helper = WORKFLOW.split("def get_cloudflare(url):", 1)[1].split("PY", 1)[0]
        self.assertIn('"Authorization": "Bearer " + token', cloudflare_helper)
        self.assertNotIn("get_public", WORKFLOW)
        self.assertNotIn("API_URL", WORKFLOW)
        self.assertIn("schedules = get_cloudflare(", WORKFLOW)
        self.assertIn('expected = {"*/15 * * * *", "20 7,8 * * *"}', WORKFLOW)
        self.assertIn("wrangler@4 tail pettraffic-control-api", WORKFLOW)


if __name__ == "__main__":
    unittest.main()
