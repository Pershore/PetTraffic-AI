from pathlib import Path
import unittest


class LighthouseScheduleResilienceTests(unittest.TestCase):
    def setUp(self):
        self.workflow = Path(".github/workflows/lighthouse-audit.yml").read_text(encoding="utf-8")

    def test_weekly_schedule_has_staggered_retries(self):
        self.assertIn('- cron: "27 7,9,11,13 * * 1"', self.workflow)
        self.assertIn('workflow_id: "lighthouse-audit.yml"', self.workflow)

    def test_schedule_gate_allows_only_one_successful_audit_per_vilnius_day(self):
        gate = self.workflow.split("  schedule-gate:", 1)[1].split("  lighthouse:", 1)[0]
        self.assertIn('timeZone: "Europe/Vilnius"', gate)
        self.assertIn('event: "schedule"', gate)
        self.assertIn('run.status === "completed"', gate)
        self.assertIn('run.conclusion === "success"', gate)
        self.assertIn('run.id !== context.runId', gate)
        self.assertIn('core.setOutput("run_suite", alreadySucceeded ? "false" : "true")', gate)

    def test_manual_and_push_audits_are_not_suppressed(self):
        gate = self.workflow.split("  schedule-gate:", 1)[1].split("  lighthouse:", 1)[0]
        self.assertIn('context.eventName !== "schedule"', gate)
        self.assertIn('core.setOutput("run_suite", "true")', gate)
        self.assertIn("workflow_dispatch:", self.workflow)
        self.assertIn("push:", self.workflow)

    def test_full_audit_waits_for_gate_and_running_retry_is_not_cancelled(self):
        lighthouse = self.workflow.split("  lighthouse:", 1)[1]
        self.assertIn("needs: schedule-gate", lighthouse[:180])
        self.assertIn("needs.schedule-gate.outputs.run_suite == 'true'", lighthouse[:250])
        self.assertIn("cancel-in-progress: false", self.workflow)


if __name__ == "__main__":
    unittest.main()
