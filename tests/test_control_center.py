import unittest
from datetime import datetime, timezone, timedelta
from agent.control_center import evaluate_workflow, render

class ControlCenterTests(unittest.TestCase):
    def setUp(self):
        self.now = datetime(2026, 11, 12, 10, 0, tzinfo=timezone.utc)

    def run_item(self, status="completed", conclusion="success", age_hours=2):
        created = self.now - timedelta(hours=age_hours)
        return {"created_at": created.isoformat().replace("+00:00", "Z"), "status": status, "conclusion": conclusion, "html_url": "https://github.com/example/run/1"}

    def test_successful_recent_run(self):
        self.assertEqual(evaluate_workflow("Analytics", [self.run_item()], self.now, 36)["state"], "success")

    def test_failed_run_is_failure(self):
        self.assertEqual(evaluate_workflow("Analytics", [self.run_item(conclusion="failure")], self.now, 36)["state"], "failure")

    def test_old_success_is_stale(self):
        self.assertEqual(evaluate_workflow("Analytics", [self.run_item(age_hours=40)], self.now, 36)["state"], "stale")

    def test_running_run_is_running(self):
        self.assertEqual(evaluate_workflow("Analytics", [self.run_item(status="in_progress", conclusion=None)], self.now, 36)["state"], "running")

    def test_no_runs_is_missing(self):
        self.assertEqual(evaluate_workflow("Analytics", [], self.now, 36)["state"], "missing")

    def test_report_highlights_failure(self):
        results = [evaluate_workflow("Analytics", [self.run_item(conclusion="failure")], self.now, 36)]
        report = render(results, self.now)
        self.assertIn("KLAIDA", report)
        self.assertIn("Skubu", report)

if __name__ == "__main__":
    unittest.main()
