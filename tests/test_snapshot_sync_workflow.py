from pathlib import Path
import unittest


class SnapshotSyncWorkflowTests(unittest.TestCase):
    def test_sync_accepts_a_validated_daily_suite_run_input(self):
        workflow = Path(".github/workflows/sync-control-api.yml").read_text(encoding="utf-8")
        self.assertIn("run-name: \"${{", workflow)
        self.assertIn("workflow_dispatch:", workflow)
        self.assertIn("source_run_id:", workflow)
        self.assertIn("run.workflow_id !== 418322987", workflow)
        self.assertIn('["schedule", "workflow_dispatch"].includes(run.event)', workflow)
        self.assertIn('run.head_branch !== "main"', workflow)
        self.assertIn('run.status !== "completed"', workflow)

    def test_owner_bridge_child_sync_accepts_only_active_or_successful_parent(self):
        workflow = Path(".github/workflows/sync-control-api.yml").read_text(encoding="utf-8")
        self.assertIn("const isVerifiedOwnerBridge = bridge =>", workflow)
        self.assertIn('bridge.status === "in_progress" && bridge.conclusion == null', workflow)
        self.assertIn('bridge.status === "completed" && bridge.conclusion === "success"', workflow)
        self.assertEqual(workflow.count("const validBridge = isVerifiedOwnerBridge(bridge);"), 2)
        self.assertIn('bridge.actor?.login === "Pershore"', workflow)
        self.assertIn('String(comment.body || "").trim() === "/pettraffic-run-daily-suite"', workflow)
        self.assertIn("bridgeAt >= commentAt", workflow)
        self.assertIn("sourceAt >= bridgeAt", workflow)

    def test_sync_requires_at_least_one_successful_data_job(self):
        workflow = Path(".github/workflows/sync-control-api.yml").read_text(encoding="utf-8")
        self.assertIn('["analytics", "topic-radar"].includes(job.name)', workflow)
        self.assertIn('job.conclusion === "success"', workflow)
        self.assertIn('core.setFailed("Source daily-suite run has no successful analytics or topic-radar artifact job.")', workflow)

    def test_sync_downloads_artifacts_from_validated_source_run(self):
        workflow = Path(".github/workflows/sync-control-api.yml").read_text(encoding="utf-8")
        self.assertIn("steps.suite-source.outputs.source_run_id", workflow)
        self.assertIn("pettraffic-analytics-7d", workflow)
        self.assertIn("pettraffic-topic-radar", workflow)
        self.assertIn("ACTIONS_ID_TOKEN_REQUEST_URL", workflow)
        self.assertIn("OK: D1 snapshot write/read verified.", workflow)


if __name__ == "__main__":
    unittest.main()
