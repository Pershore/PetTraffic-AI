from pathlib import Path
import unittest


class DailySuiteScheduleResilienceTests(unittest.TestCase):
    def setUp(self):
        self.workflow = Path(".github/workflows/daily-suite.yml").read_text(encoding="utf-8")

    def test_staggered_schedule_retries_preserve_the_original_workflow(self):
        self.assertIn('workflow_id: "daily-suite.yml"', self.workflow)
        self.assertIn('- cron: "10 6,8,10,11 * * *"', self.workflow)
        self.assertIn('event: "schedule"', self.workflow)

    def test_schedule_gate_runs_only_one_successful_suite_per_vilnius_day(self):
        gate = self.workflow.split("  schedule-gate:", 1)[1].split("  analytics:", 1)[0]
        self.assertIn('timeZone: "Europe/Vilnius"', gate)
        self.assertIn('run.conclusion === "success"', gate)
        self.assertIn('run.status === "completed"', gate)
        self.assertIn('run.id !== context.runId', gate)
        self.assertIn('core.setOutput("run_suite", alreadySucceeded ? "false" : "true")', gate)

    def test_manual_dispatch_is_not_suppressed_by_the_schedule_gate(self):
        gate = self.workflow.split("  schedule-gate:", 1)[1].split("  analytics:", 1)[0]
        self.assertIn('context.eventName !== "schedule"', gate)
        self.assertIn('core.setOutput("run_suite", "true")', gate)

    def test_all_data_jobs_wait_for_the_schedule_gate(self):
        for job in ("analytics", "topic-radar", "live-check"):
            with self.subTest(job=job):
                block = self.workflow.split(f"  {job}:", 1)[1]
                self.assertIn("needs: schedule-gate", block.split("  ", 1)[0] + block[:180])
                self.assertIn("needs.schedule-gate.outputs.run_suite == 'true'", block[:500])

    def test_schedule_retries_do_not_change_the_worker_provenance_or_manual_path(self):
        self.assertIn("workflow_dispatch:", self.workflow)
        self.assertIn("group: pettraffic-daily-suite", self.workflow)
        self.assertIn("cancel-in-progress: false", self.workflow)
        self.assertIn("schedule-gate.outputs.run_suite", self.workflow)


if __name__ == "__main__":
    unittest.main()
