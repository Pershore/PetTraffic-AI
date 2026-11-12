import unittest
from datetime import datetime, timezone, timedelta
from agent.control_center import WORKFLOWS, evaluate_workflow, evaluate_worker_health, needs_attention, render

class ControlCenterTests(unittest.TestCase):
    def setUp(self):
        self.now = datetime(2026, 11, 12, 10, 0, tzinfo=timezone.utc)

    def run_item(self, status="completed", conclusion="success", age_hours=2):
        created = self.now - timedelta(hours=age_hours)
        return {"created_at": created.isoformat().replace("+00:00", "Z"), "status": status, "conclusion": conclusion, "html_url": "https://github.com/example/run/1"}

    def test_worker_health_success_requires_recent_site_and_database_heartbeat(self):
        result = evaluate_worker_health({
            "ok": True,
            "database": "connected",
            "heartbeat": {
                "checked_at": self.now.isoformat(),
                "site_ok": True,
                "site_status": 200,
                "database_ok": True,
            },
        }, now=self.now)
        self.assertEqual(result["state"], "success")
        self.assertIn("heartbeat sėkmingas", result["detail"])

    def test_worker_health_warns_if_first_heartbeat_is_pending(self):
        result = evaluate_worker_health({
            "ok": True, "database": "connected", "heartbeat": None
        }, now=self.now)
        self.assertEqual(result["state"], "warning")

    def test_worker_health_detects_stale_heartbeat(self):
        stale = (self.now - timedelta(minutes=46)).isoformat()
        result = evaluate_worker_health({
            "ok": True,
            "database": "connected",
            "heartbeat": {
                "checked_at": stale,
                "site_ok": True,
                "site_status": 200,
                "database_ok": True,
            },
        }, now=self.now)
        self.assertEqual(result["state"], "failure")
        self.assertIn("stale", result["detail"])

    def test_worker_health_detects_failed_site_heartbeat(self):
        result = evaluate_worker_health({
            "ok": True,
            "database": "connected",
            "heartbeat": {
                "checked_at": self.now.isoformat(),
                "site_ok": False,
                "site_status": 503,
                "database_ok": True,
            },
        }, now=self.now)
        self.assertEqual(result["state"], "failure")
        self.assertIn("503", result["detail"])

    def test_worker_health_detects_disconnected_database(self):
        result = evaluate_worker_health({"ok": False, "database": "unavailable"})
        self.assertEqual(result["state"], "failure")

    def test_worker_health_rejects_non_object_json(self):
        result = evaluate_worker_health(["unexpected", "array"])
        self.assertEqual(result["state"], "failure")
        self.assertIn("invalid JSON", result["detail"])

    def test_worker_health_detects_http_errors(self):
        result = evaluate_worker_health({}, status_code=503)
        self.assertEqual(result["state"], "failure")
        self.assertIn("503", result["detail"])

    def test_control_api_sync_is_monitored(self):
        self.assertIn("sync-control-api.yml", [item[0] for item in WORKFLOWS])

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

    def test_actionable_state_needs_attention(self):
        self.assertTrue(needs_attention([{"state": "failure"}]))
        self.assertTrue(needs_attention([{"state": "stale"}]))

    def test_missing_first_run_does_not_create_false_alarm(self):
        self.assertFalse(needs_attention([{"state": "missing"}]))

    def test_success_and_running_do_not_alert(self):
        self.assertFalse(needs_attention([{"state": "success"}, {"state": "running"}]))

if __name__ == "__main__":
    unittest.main()
