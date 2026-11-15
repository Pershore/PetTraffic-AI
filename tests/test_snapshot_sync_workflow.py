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
