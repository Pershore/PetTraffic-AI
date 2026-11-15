from pathlib import Path
import unittest


class DispatchBridgeWorkflowTests(unittest.TestCase):
    def test_bridge_is_owner_only_and_issue_scoped(self):
        workflow = Path(".github/workflows/dispatch-daily-suite.yml").read_text(encoding="utf-8")
        self.assertIn("issue_comment:", workflow)
        self.assertIn("types: [created]", workflow)
        self.assertIn("github.event.issue.number == 145", workflow)
        self.assertIn("actions: write", workflow)
        self.assertIn("python agent/dispatch_guard.py", workflow)
        self.assertIn("steps.guard.outputs.authorized == 'true'", workflow)
        self.assertIn("DISPATCH_ACTION", workflow)

    def test_bridge_routes_only_four_fixed_workflows(self):
        workflow = Path(".github/workflows/dispatch-daily-suite.yml").read_text(encoding="utf-8")
        for action in ("daily-suite", "sync-latest", "control-center", "lighthouse"):
            with self.subTest(action=action):
                self.assertIn(f'action === "{action}"', workflow)
        for workflow_id in ("daily-suite.yml", "sync-control-api.yml", "control-center.yml", "lighthouse-audit.yml"):
            with self.subTest(workflow_id=workflow_id):
                self.assertIn(f'"{workflow_id}"', workflow)
        self.assertIn("github.rest.actions.createWorkflowDispatch", workflow)
        self.assertIn('ref: "main"', workflow)
        control_center = Path(".github/workflows/control-center.yml").read_text(encoding="utf-8")
        self.assertIn("workflow_dispatch:", control_center)
        lighthouse = Path(".github/workflows/lighthouse-audit.yml").read_text(encoding="utf-8")
        self.assertIn("workflow_dispatch:", lighthouse)

    def test_bridge_has_deduplication_and_no_secrets_or_external_services(self):
        workflow = Path(".github/workflows/dispatch-daily-suite.yml").read_text(encoding="utf-8")
        self.assertIn("20 * 60 * 60 * 1000", workflow)
        self.assertIn("60 * 60 * 1000", workflow)
        self.assertNotIn("secrets.", workflow)
        self.assertNotIn("curl ", workflow)


if __name__ == "__main__":
    unittest.main()
