import unittest
import json
from unittest.mock import patch
from datetime import datetime, timezone, timedelta
from agent.control_center import WORKFLOWS, evaluate_workflow, evaluate_worker_health, evaluate_agent_orchestration, fetch_workflow_metadata, needs_attention, recovery_confirmed, render

class ControlCenterTests(unittest.TestCase):
    def test_daily_suite_jobs_run_on_direct_schedule_events(self):
        with open(".github/workflows/daily-suite.yml", encoding="utf-8") as stream:
            workflow = stream.read()
        self.assertIn("  topic-radar:\n    if: github.event_name == 'schedule' || github.event_name == 'workflow_dispatch'", workflow)
        self.assertIn("  live-check:\n    if: github.event_name == 'schedule' || github.event_name == 'workflow_dispatch'", workflow)
        self.assertNotIn("github.event.workflow_run.event == 'schedule'", workflow)

    def test_control_center_rechecks_after_worker_deployment(self):
        with open(".github/workflows/control-center.yml", encoding="utf-8") as stream:
            workflow = stream.read()
        self.assertIn('      - "Deploy PetTraffic control API"', workflow)
        self.assertIn("workflow_run:", workflow)

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
        self.assertFalse(recovery_confirmed([result]))

    def test_alert_recovery_requires_every_check_to_be_success(self):
        self.assertTrue(recovery_confirmed([{"state": "success"}, {"state": "success"}]))
        self.assertFalse(recovery_confirmed([{"state": "success"}, {"state": "waiting"}]))
        self.assertFalse(recovery_confirmed([{"state": "success"}, {"state": "running"}]))
        self.assertFalse(recovery_confirmed([{"state": "success"}, {"state": "missing"}]))
        self.assertFalse(recovery_confirmed([]))

    def test_workflow_closes_alert_only_after_confirmed_recovery(self):
        with open(".github/workflows/control-center.yml", encoding="utf-8") as stream:
            workflow = stream.read()
        self.assertIn("existing && data.recovery_confirmed === true", workflow)
        self.assertIn("No confirmed recovery", workflow)

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

    def test_cancelled_non_scheduled_run_does_not_mask_successful_daily_schedule(self):
        now = datetime(2026, 11, 13, 8, 10, tzinfo=timezone.utc)
        scheduled = {
            "created_at": "2026-11-13T07:50:00Z",
            "event": "schedule",
            "status": "completed",
            "conclusion": "success",
            "html_url": "https://github.com/example/run/schedule",
        }
        cancelled = {
            "created_at": "2026-11-13T08:05:00Z",
            "event": "workflow_run",
            "status": "completed",
            "conclusion": "cancelled",
            "html_url": "https://github.com/example/run/cancelled",
        }
        schedule = {"frequency": "daily", "hour": 6, "minute": 43, "grace_minutes": 60}
        result = evaluate_workflow("Analytics", [scheduled, cancelled], now, 36, schedule)
        self.assertEqual(result["state"], "success")

    def test_running_non_scheduled_run_does_not_hide_missed_daily_cycle(self):
        now = datetime(2026, 11, 13, 8, 10, tzinfo=timezone.utc)
        running = {
            "created_at": "2026-11-13T08:05:00Z",
            "event": "push",
            "status": "in_progress",
            "conclusion": None,
            "html_url": "https://github.com/example/run/push",
        }
        schedule = {"frequency": "daily", "hour": 6, "minute": 43, "grace_minutes": 60}
        result = evaluate_workflow("Analytics", [running], now, 36, schedule)
        self.assertEqual(result["state"], "warning")
        self.assertIn("suplanuotų paleidimų istorijoje nėra", result["detail"])

    def test_control_center_only_rechecks_after_daily_suite_and_weekly_or_worker_jobs(self):
        with open(".github/workflows/control-center.yml", encoding="utf-8") as stream:
            workflow = stream.read()
        self.assertIn('"Pet traffic daily automation suite"', workflow)
        self.assertIn('"Pet traffic Lighthouse audits"', workflow)
        self.assertIn('"Deploy PetTraffic control API"', workflow)
        self.assertNotIn('"Pet traffic analytics snapshot"', workflow)
        self.assertNotIn('"Pet traffic daily topic radar"', workflow)
        self.assertNotIn('"Pet traffic live-site monitor"', workflow)

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

    def test_daily_suite_is_the_monitored_schedule_source(self):
        self.assertIn("daily-suite.yml", [item[0] for item in WORKFLOWS])
        self.assertNotIn("analytics-snapshot.yml", [item[0] for item in WORKFLOWS])
        self.assertNotIn("daily-topic-radar.yml", [item[0] for item in WORKFLOWS])
        self.assertNotIn("live-site-monitor.yml", [item[0] for item in WORKFLOWS])

    def test_daily_suite_has_an_independent_direct_cron(self):
        with open(".github/workflows/daily-suite.yml", encoding="utf-8") as stream:
            workflow = stream.read()
        self.assertIn('    - cron: "10 6 * * *"', workflow)
        self.assertNotIn("workflow_run:", workflow)
        self.assertIn("github.event_name == 'schedule'", workflow)

    def test_snapshot_sync_uses_direct_schedule_event_for_daily_suite(self):
        with open(".github/workflows/sync-control-api.yml", encoding="utf-8") as stream:
            workflow = stream.read()
        self.assertIn('get("event", "")', workflow)
        self.assertIn('[[ "$event_name" == "schedule" ]]', workflow)
        self.assertNotIn("Scheduled daily suite from site-check #", workflow)

    def test_daily_suite_direct_schedule_counts_as_scheduled_run(self):
        now = datetime(2026, 11, 14, 8, 10, tzinfo=timezone.utc)
        scheduled = {
            "created_at": "2026-11-14T07:50:00Z",
            "event": "schedule",
            "status": "completed",
            "conclusion": "success",
            "html_url": "https://github.com/example/run/suite",
        }
        schedule = {"frequency": "daily", "hour": 6, "minute": 10, "grace_minutes": 60}
        result = evaluate_workflow("Daily suite", [scheduled], now, 36, schedule,
            workflow_updated_at="2026-11-14T05:00:00Z")
        self.assertEqual(result["state"], "success")

    def test_daily_suite_schedule_proxy_counts_as_scheduled_run(self):
        now = datetime(2026, 11, 14, 8, 10, tzinfo=timezone.utc)
        scheduled = {
            "created_at": "2026-11-14T07:50:00Z",
            "event": "workflow_run",
            "display_title": "Scheduled daily suite from site-check #123",
            "status": "completed",
            "conclusion": "success",
            "html_url": "https://github.com/example/run/suite",
        }
        schedule = {"frequency": "daily", "hour": 6, "minute": 10, "grace_minutes": 60}
        result = evaluate_workflow(
            "Daily suite", [scheduled], now, 36, schedule,
            workflow_updated_at="2026-11-14T05:00:00Z",
        )
        self.assertEqual(result["state"], "success")

    def test_non_scheduled_suite_run_does_not_count_as_daily_cycle(self):
        now = datetime(2026, 11, 14, 8, 10, tzinfo=timezone.utc)
        pushed = {
            "created_at": "2026-11-14T07:50:00Z",
            "event": "workflow_run",
            "display_title": "Non-scheduled site-check run #123",
            "status": "completed",
            "conclusion": "success",
            "html_url": "https://github.com/example/run/non-scheduled",
        }
        schedule = {"frequency": "daily", "hour": 5, "minute": 37, "grace_minutes": 60}
        result = evaluate_workflow("Daily suite", [pushed], now, 36, schedule)
        self.assertEqual(result["state"], "warning")
        self.assertIn("suplanuotų paleidimų istorijoje nėra", result["detail"])

    def test_suite_run_after_workflow_edit_counts_for_current_cycle(self):
        now = datetime(2026, 11, 14, 14, 0, tzinfo=timezone.utc)
        scheduled = {
            "created_at": "2026-11-14T13:00:00Z",
            "event": "workflow_run",
            "display_title": "Scheduled daily suite from site-check #123",
            "status": "completed",
            "conclusion": "success",
            "html_url": "https://github.com/example/run/suite",
        }
        schedule = {"frequency": "daily", "hour": 5, "minute": 37, "grace_minutes": 60}
        result = evaluate_workflow(
            "Daily suite", [scheduled], now, 36, schedule,
            workflow_updated_at="2026-11-14T12:00:00Z",
        )
        self.assertEqual(result["state"], "success")

    def test_daily_suite_waits_if_its_file_was_updated_after_due_and_no_run_exists(self):
        now = datetime(2026, 11, 14, 8, 0, tzinfo=timezone.utc)
        schedule = {"frequency": "daily", "hour": 5, "minute": 37, "grace_minutes": 60}
        result = evaluate_workflow(
            "Daily suite", [], now, 36, schedule,
            workflow_updated_at="2026-11-14T06:20:00Z",
        )
        self.assertEqual(result["state"], "waiting")
        self.assertIn("laukiama kito ciklo", result["detail"])

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
