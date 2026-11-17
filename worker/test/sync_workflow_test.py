from pathlib import Path
import unittest


WORKFLOW_PATH = (
    Path(__file__).resolve().parents[2]
    / ".github"
    / "workflows"
    / "sync-control-api.yml"
)
DAILY_SUITE_WORKFLOW_ID = 418322987


class SyncWorkflowRoutingTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.workflow = WORKFLOW_PATH.read_text(encoding="utf-8")

    def test_daily_suite_detection_uses_stable_workflow_id(self):
        marker = f"github.event.workflow_run.workflow_id == {DAILY_SUITE_WORKFLOW_ID}"
        self.assertGreaterEqual(self.workflow.count(marker), 3)
        self.assertNotIn(
            "github.event.workflow_run.name == 'Pet traffic daily automation suite'",
            self.workflow,
        )
        self.assertNotIn(
            "github.event.workflow_run.name != 'Pet traffic daily automation suite'",
            self.workflow,
        )

    def test_dynamic_schedule_run_name_is_normalized_for_event_builder(self):
        expected = (
            "github.event.workflow_run.workflow_id == "
            f"{DAILY_SUITE_WORKFLOW_ID} && 'Pet traffic daily automation suite'"
        )
        self.assertIn(expected, self.workflow)

    def test_other_workflow_events_keep_their_own_artifact_mapping(self):
        self.assertIn(
            "github.event.workflow_run.name == 'Pet traffic analytics snapshot'",
            self.workflow,
        )
        self.assertIn(
            "github.event.workflow_run.name == 'Pet traffic daily topic radar'",
            self.workflow,
        )


if __name__ == "__main__":
    unittest.main()
