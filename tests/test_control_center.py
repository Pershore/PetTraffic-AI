import unittest
import json
from unittest.mock import patch
from datetime import datetime, timezone, timedelta
from agent.control_center import WORKFLOWS, evaluate_workflow, evaluate_worker_health, evaluate_agent_orchestration, fetch_workflow_metadata, needs_attention, render

class ControlCenterTests(unittest.TestCase):
    def setUp(self):
        self.now = datetime(2026, 11, 12, 10, 0, tzinfo=timezone.utc)

    def run_item(self, status="completed", conclusion="success", age_hours=2):
        created = self.now - timedelta(hours=age_hours)
        return {"created_at": created.isoformat().replace("+00:00", "Z"), "status": status, "conclusion": conclusion, "html_url": "https://github.com/example/run/1"}

    def test_workflow_schedule_baseline_uses_last_file_commit(self):
        class FakeResponse:
            def __init__(self, payload):
                self.payload = payload
            def __enter__(self):
                return self
            def __exit__(self, *args):
                return False
            def read(self):
                return json.dumps(self.payload).encode("utf-8")

        responses = [
            FakeResponse({
                "state": "active",
                "updated_at": "2026-11-11T20:16:28Z",
            }),
            FakeResponse([{
                "commit": {
                    "committer": {"date": "2026-11-13T12:00:00Z"},
                    "author": {"date": "2026-11-13T11:59:00Z"},
                }
            }]),
        ]

        with patch("agent.control_center.urlopen", side_effect=responses) as mocked:
            result = fetch_workflow_metadata("analytics-snapshot.yml")

        self.assertEqual(result["state"], "active")
        self.assertEqual(result["updated_at"], "2026-11-13T12:00:00Z")
        self.assertEqual(mocked.call_count, 2)
        self.assertIn(".github%2Fworkflows%2Fanalytics-snapshot.yml", mocked.call_args_list[1].args[0].full_url)

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

    def test_agent_failure_is_reported_after_daily_cycle(self):
        now = datetime(2026, 11, 13, 9, 0, tzinfo=timezone.utc)  # 11:00 Vilnius
        result = evaluate_agent_orchestration({
            "agent_orchestration": {
                "run_date": "2026-11-13",
                "status": "failed",
                "ai_calls": 1,
                "error_code": "Unexpected_end_of_JSON_input",
            }
        }, now=now)
        self.assertEqual(result["state"], "failure")
        self.assertIn("Unexpected_end_of_JSON_input", result["detail"])

    def test_previous_failed_agent_run_waits_before_today_window(self):
        now = datetime(2026, 11, 14, 7, 0, tzinfo=timezone.utc)  # 09:00 Vilnius
        result = evaluate_agent_orchestration({
            "agent_orchestration": {
                "run_date": "2026-11-13",
                "status": "failed",
                "ai_calls": 1,
                "error_code": "old_failure",
            }
        }, now=now)
        self.assertEqual(result["state"], "waiting")
        self.assertFalse(needs_attention([result]))

    def test_missing_agent_run_warns_after_daily_window(self):
        now = datetime(2026, 11, 13, 9, 0, tzinfo=timezone.utc)
        result = evaluate_agent_orchestration({
            "agent_orchestration": {"status": "not_started"}
        }, now=now)
        self.assertEqual(result["state"], "warning")
        self.assertTrue(needs_attention([result]))

    def test_missing_agent_run_waits_before_daily_window(self):
        now = datetime(2026, 11, 13, 7, 0, tzinfo=timezone.utc)
        result = evaluate_agent_orchestration({
            "agent_orchestration": {"status": "not_started"}
        }, now=now)
        self.assertEqual(result["state"], "waiting")
        self.assertFalse(needs_attention([result]))

    def test_completed_agent_with_reviewed_memory_is_success(self):
        now = datetime(2026, 11, 13, 9, 0, tzinfo=timezone.utc)
        result = evaluate_agent_orchestration({
            "agent_orchestration": {"run_date": "2026-11-13", "status": "completed"},
            "control_core": {
                "status": "reviewed",
                "memory_status": "present",
                "recommendation_count": 3,
                "evidence_gap_count": 0,
            },
        }, now=now)
        self.assertEqual(result["state"], "success")
        self.assertIn("atmintis išsaugota", result["detail"])

    def test_completed_agent_with_evidence_gaps_is_warning(self):
        now = datetime(2026, 11, 13, 9, 0, tzinfo=timezone.utc)
        result = evaluate_agent_orchestration({
            "agent_orchestration": {"run_date": "2026-11-13", "status": "completed"},
            "control_core": {
                "status": "needs_evidence",
                "memory_status": "present",
                "recommendation_count": 2,
                "evidence_gap_count": 1,
            },
        }, now=now)
        self.assertEqual(result["state"], "warning")
        self.assertIn("trūksta įrodymų: 1", result["detail"])

    def test_completed_agent_without_memory_is_warning(self):
        now = datetime(2026, 11, 13, 9, 0, tzinfo=timezone.utc)
        result = evaluate_agent_orchestration({
            "agent_orchestration": {"run_date": "2026-11-13", "status": "completed"},
            "control_core": {"status": "reviewed", "memory_status": "missing"},
        }, now=now)
        self.assertEqual(result["state"], "warning")
        self.assertIn("atmintis neišsaugota", result["detail"])

    def test_recently_running_agent_is_reported_as_running(self):
        now = datetime(2026, 11, 13, 9, 0, tzinfo=timezone.utc)
        started = (now - timedelta(minutes=5)).isoformat()
        result = evaluate_agent_orchestration({
            "agent_orchestration": {
                "run_date": "2026-11-13",
                "status": "running",
                "started_at": started,
                "ai_calls": 2,
            }
        }, now=now)
        self.assertEqual(result["state"], "running")

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

    def test_missing_first_run_is_waiting_not_a_priority(self):
        result = evaluate_workflow("Temų radaras", [], self.now, 36)
        report = render([result], self.now)
        self.assertEqual(result["state"], "missing")
        self.assertIn("LAUKIAMA PIRMŲ CIKLŲ", report)
        self.assertNotIn("**Patikrinti:** Temų radaras", report)
        self.assertIn("Nerasta veiksmų reikalaujančių būsenų.", report)

    def test_missing_daily_first_run_before_schedule_grace_is_not_an_alert(self):
        now = datetime(2026, 11, 13, 6, 30, tzinfo=timezone.utc)
        schedule = {"frequency": "daily", "hour": 6, "minute": 17, "grace_minutes": 60}
        result = evaluate_workflow("Temų radaras", [], now, 36, schedule)
        self.assertEqual(result["state"], "missing")
        self.assertFalse(needs_attention([result]))

    def test_missing_daily_first_run_after_schedule_grace_is_an_alert(self):
        now = datetime(2026, 11, 13, 8, 10, tzinfo=timezone.utc)
        schedule = {"frequency": "daily", "hour": 6, "minute": 17, "grace_minutes": 60}
        result = evaluate_workflow("Temų radaras", [], now, 36, schedule)
        self.assertEqual(result["state"], "warning")
        self.assertTrue(needs_attention([result]))
        self.assertIn("06:17 UTC", result["detail"])

    def test_workflow_updated_after_daily_schedule_waits_for_next_cycle(self):
        now = datetime(2026, 11, 13, 11, 40, tzinfo=timezone.utc)
        schedule = {"frequency": "daily", "hour": 6, "minute": 43, "grace_minutes": 60}
        result = evaluate_workflow(
            "Analytics",
            [self.run_item()],
            now,
            36,
            schedule,
            workflow_updated_at="2026-11-13T09:18:00Z",
        )
        self.assertEqual(result["state"], "waiting")
        self.assertIn("po paskutinio suplanuoto laiko", result["detail"])
        self.assertFalse(needs_attention([result]))

    def test_workflow_updated_before_daily_schedule_still_requires_cycle(self):
        now = datetime(2026, 11, 13, 8, 10, tzinfo=timezone.utc)
        schedule = {"frequency": "daily", "hour": 6, "minute": 43, "grace_minutes": 60}
        result = evaluate_workflow(
            "Analytics",
            [self.run_item()],
            now,
            36,
            schedule,
            workflow_updated_at="2026-11-13T05:00:00Z",
        )
        self.assertEqual(result["state"], "warning")
        self.assertIn("2026-11-13 06:43 UTC", result["detail"])

    def test_disabled_workflow_is_reported(self):
        result = evaluate_workflow(
            "Analytics",
            [self.run_item()],
            self.now,
            36,
            workflow_state="disabled_inactivity",
        )
        self.assertEqual(result["state"], "warning")
        self.assertIn("disabled_inactivity", result["detail"])

    def test_previous_success_does_not_mask_a_missed_daily_cycle(self):
        now = datetime(2026, 11, 13, 8, 10, tzinfo=timezone.utc)
        previous = {
            "created_at": "2026-11-12T21:37:08Z",
            "event": "push",
            "status": "completed",
            "conclusion": "success",
            "html_url": "https://github.com/example/run/1",
        }
        schedule = {"frequency": "daily", "hour": 6, "minute": 43, "grace_minutes": 60}
        result = evaluate_workflow("Analytics", [previous], now, 36, schedule)
        self.assertEqual(result["state"], "warning")
        self.assertIn("2026-11-13 06:43 UTC", result["detail"])

    def test_recent_push_run_does_not_count_as_scheduled_cycle(self):
        now = datetime(2026, 11, 13, 8, 10, tzinfo=timezone.utc)
        pushed = {
            "created_at": "2026-11-13T08:05:00Z",
            "event": "push",
            "status": "completed",
            "conclusion": "success",
            "html_url": "https://github.com/example/run/push",
        }
        schedule = {"frequency": "daily", "hour": 6, "minute": 43, "grace_minutes": 60}
        result = evaluate_workflow("Analytics", [pushed], now, 36, schedule)
        self.assertEqual(result["state"], "warning")
        self.assertIn("Kiti paleidimo tipai", result["detail"])

    def test_current_schedule_run_counts_even_if_a_later_push_exists(self):
        now = datetime(2026, 11, 13, 8, 10, tzinfo=timezone.utc)
        scheduled = {
            "created_at": "2026-11-13T07:50:00Z",
            "event": "schedule",
            "status": "completed",
            "conclusion": "success",
            "html_url": "https://github.com/example/run/schedule",
        }
        pushed = {
            "created_at": "2026-11-13T08:05:00Z",
            "event": "push",
            "status": "completed",
            "conclusion": "success",
            "html_url": "https://github.com/example/run/push",
        }
        schedule = {"frequency": "daily", "hour": 6, "minute": 43, "grace_minutes": 60}
        result = evaluate_workflow("Analytics", [scheduled, pushed], now, 36, schedule)
        self.assertEqual(result["state"], "success")

    def test_success_after_scheduled_cycle_grace_is_current(self):
        now = datetime(2026, 11, 13, 8, 10, tzinfo=timezone.utc)
        current = {
            "created_at": "2026-11-13T07:50:00Z",
            "event": "schedule",
            "status": "completed",
            "conclusion": "success",
            "html_url": "https://github.com/example/run/2",
        }
        schedule = {"frequency": "daily", "hour": 6, "minute": 43, "grace_minutes": 60}
        result = evaluate_workflow("Analytics", [current], now, 36, schedule)
        self.assertEqual(result["state"], "success")

    def test_event_driven_workflow_missing_run_is_not_a_schedule_alert(self):
        result = evaluate_workflow("Centrinės API sinchronizavimas", [], self.now, 36, None)
        self.assertEqual(result["state"], "missing")
        self.assertFalse(needs_attention([result]))

    def test_weekly_missing_workflow_alerts_until_a_current_week_run_exists(self):
        before_monday_schedule = datetime(2026, 11, 16, 7, 30, tzinfo=timezone.utc)
        schedule = {"frequency": "weekly", "weekday": 0, "hour": 7, "minute": 20, "grace_minutes": 60}
        result = evaluate_workflow("Lighthouse", [], before_monday_schedule, 9 * 24, schedule)
        self.assertEqual(result["state"], "missing")
        self.assertFalse(needs_attention([result]))

        monday_after_grace = datetime(2026, 11, 16, 8, 30, tzinfo=timezone.utc)
        result = evaluate_workflow("Lighthouse", [], monday_after_grace, 9 * 24, schedule)
        self.assertEqual(result["state"], "warning")
        self.assertTrue(needs_attention([result]))

        friday = datetime(2026, 11, 20, 12, 0, tzinfo=timezone.utc)
        result = evaluate_workflow("Lighthouse", [], friday, 9 * 24, schedule)
        self.assertEqual(result["state"], "warning")
        self.assertTrue(needs_attention([result]))

    def test_success_and_running_do_not_alert(self):
        self.assertFalse(needs_attention([{"state": "success"}, {"state": "running"}]))

if __name__ == "__main__":
    unittest.main()
