import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
WORKFLOW = (ROOT / ".github" / "workflows" / "worker-cron-diagnostic.yml").read_text(encoding="utf-8")


class WorkerCronDiagnosticSecurityTests(unittest.TestCase):
    def test_cloudflare_token_is_only_used_for_cloudflare_requests(self):
        cloudflare_helper = WORKFLOW.split("def get_cloudflare(url):", 1)[1].split("def get_public(url):", 1)[0]
        public_helper = WORKFLOW.split("def get_public(url):", 1)[1].split("schedules = get_cloudflare", 1)[0]
        self.assertIn('"Authorization": "Bearer " + token', cloudflare_helper)
        self.assertNotIn("Authorization", public_helper)
        self.assertIn('health = get_public(api_url + "/health")', WORKFLOW)


if __name__ == "__main__":
    unittest.main()
