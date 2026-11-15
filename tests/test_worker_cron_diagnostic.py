import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
WORKFLOW = (ROOT / ".github" / "workflows" / "worker-cron-diagnostic.yml").read_text(encoding="utf-8")
DEPLOY_WORKFLOW = (ROOT / ".github" / "workflows" / "deploy-control-api.yml").read_text(encoding="utf-8")
WRANGLER = (ROOT / "worker" / "wrangler.toml").read_text(encoding="utf-8")


class WorkerCronDiagnosticSecurityTests(unittest.TestCase):
    def test_cloudflare_token_is_scoped_to_schedule_api_step(self):
        cloudflare_helper = WORKFLOW.split("def get_cloudflare(url):", 1)[1].split("PY", 1)[0]
        self.assertIn('"Authorization": "Bearer " + token', cloudflare_helper)
        self.assertNotIn("get_public", WORKFLOW)
        self.assertNotIn("API_URL", WORKFLOW)
        self.assertIn("schedules = get_cloudflare(", WORKFLOW)
        self.assertIn('expected = {"*/15 * * * *", "20 10,11 * * *"}', WORKFLOW)
        self.assertIn("env:\n          CLOUDFLARE_API_TOKEN:", WORKFLOW)
        self.assertNotIn("wrangler@4 tail pettraffic-control-api", WORKFLOW)
        self.assertIn("agent/worker_heartbeat_check.py", WORKFLOW)
        self.assertIn("--timeout-seconds 1020", WORKFLOW)
        self.assertNotIn("CLOUDFLARE_API_TOKEN:", WORKFLOW.split("- name: Observe scheduled heartbeat", 1)[1])

    def test_diagnostics_run_after_successful_worker_deployment(self):
        self.assertIn('workflow_run:', WORKFLOW)
        self.assertIn('workflows: ["Deploy PetTraffic control API"]', WORKFLOW)
        self.assertIn("github.event.workflow_run.conclusion == 'success'", WORKFLOW)
        self.assertNotIn("    branches: [main]\n    paths:", WORKFLOW)

    def test_deploy_checks_actual_crons_after_deployment_not_before(self):
        self.assertIn("Worker Cron Trigger schedule API access", DEPLOY_WORKFLOW)
        self.assertIn("- name: Verify deployed Worker Cron schedules", DEPLOY_WORKFLOW)
        self.assertIn('expected = {"*/15 * * * *", "20 10,11 * * *"}', DEPLOY_WORKFLOW)
        self.assertEqual(DEPLOY_WORKFLOW.count('expected = {"*/15 * * * *", "20 10,11 * * *"}'), 1)
        self.assertIn('crons = ["*/15 * * * *", "20 10,11 * * *"]', WRANGLER)
        self.assertLess(DEPLOY_WORKFLOW.index("- name: Apply D1 migrations and deploy Worker"), DEPLOY_WORKFLOW.index("- name: Verify deployed Worker Cron schedules"))


if __name__ == "__main__":
    unittest.main()
