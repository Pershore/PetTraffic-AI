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

    def test_bridge_dispatches_only_the_existing_main_daily_suite(self):
        workflow = Path(".github/workflows/dispatch-daily-suite.yml").read_text(encoding="utf-8")
        self.assertIn('const workflow_id = "daily-suite.yml"', workflow)
        self.assertIn('ref: "main"', workflow)
        self.assertIn("github.rest.actions.createWorkflowDispatch", workflow)
        self.assertIn('["schedule", "workflow_dispatch"]', workflow)
        self.assertIn("20 * 60 * 60 * 1000", workflow)

    def test_bridge_does_not_reference_secrets_or_external_services(self):
        workflow = Path(".github/workflows/dispatch-daily-suite.yml").read_text(encoding="utf-8")
        self.assertNotIn("secrets.", workflow)
        self.assertNotIn("curl ", workflow)


if __name__ == "__main__":
    unittest.main()
