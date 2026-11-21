from pathlib import Path
import unittest


class DispatchBridgeWorkflowTests(unittest.TestCase):
    def test_bridge_is_owner_only_and_issue_scoped(self):
        workflow = Path(".github/workflows/dispatch-daily-suite.yml").read_text(encoding="utf-8")
        self.assertIn("issue_comment:", workflow)
        self.assertIn("types: [created]", workflow)
        self.assertIn("github.event.issue.number == 145", workflow)
        self.assertIn("actions: write", workflow)
        self.assertIn("id-token: write", workflow)
        self.assertIn("python agent/dispatch_guard.py", workflow)
        self.assertIn("steps.guard.outputs.authorized == 'true'", workflow)
        self.assertIn("DISPATCH_ACTION", workflow)
        self.assertIn('action === "task-check-site"', workflow)
        self.assertIn('"run-readonly-tasks.yml"', workflow)
        self.assertNotIn("PETTRAFFIC_TASKS_ENABLED", workflow)

    def test_bridge_routes_only_fixed_workflows(self):
        workflow = Path(".github/workflows/dispatch-daily-suite.yml").read_text(encoding="utf-8")
        for action in ("daily-suite", "sync-latest", "control-center", "lighthouse", "site-check", "connectivity", "worker-diagnostics"):
            with self.subTest(action=action):
                self.assertIn(f'action === "{action}"', workflow)
        for workflow_id in ("daily-suite.yml", "sync-control-api.yml", "control-center.yml", "lighthouse-audit.yml", "site-check.yml", "analytics-connectivity.yml", "worker-cron-diagnostic.yml"):
            with self.subTest(workflow_id=workflow_id):
                self.assertIn(f'"{workflow_id}"', workflow)
        self.assertIn("github.rest.actions.createWorkflowDispatch", workflow)
        self.assertIn('ref: "main"', workflow)
        control_center = Path(".github/workflows/control-center.yml").read_text(encoding="utf-8")
        self.assertIn("workflow_dispatch:", control_center)
        lighthouse = Path(".github/workflows/lighthouse-audit.yml").read_text(encoding="utf-8")
        self.assertIn("workflow_dispatch:", lighthouse)

    def test_daily_suite_fallback_uses_current_day_schedule_cutoff(self):
        workflow = Path(".github/workflows/dispatch-daily-suite.yml").read_text(encoding="utf-8")
        self.assertIn("utcDayStart.setUTCHours(0, 0, 0, 0)", workflow)
        self.assertIn("dailySuiteScheduleAt.setUTCHours(6, 10, 0, 0)", workflow)
        self.assertIn("scheduleGraceEndsAt = dailySuiteScheduleAt.getTime() + 60 * 60 * 1000", workflow)
        self.assertIn("now < scheduleGraceEndsAt", workflow)
        self.assertIn("createdAt >= dailySuiteScheduleAt.getTime()", workflow)
        self.assertIn('run.event === "schedule"', workflow)
        self.assertIn('run.event === "workflow_dispatch"', workflow)
        self.assertIn("createdAt >= utcDayStart.getTime()", workflow)
        self.assertIn("This manual fallback is not schedule provenance", workflow)
        # A previous day's delayed schedule must not suppress today's fallback.
        self.assertNotIn('run.event === "schedule" &&\n                    Date.parse(run.created_at) >= manualCutoff', workflow)

    def test_bridge_has_deduplication_and_no_secrets_or_external_services(self):
        workflow = Path(".github/workflows/dispatch-daily-suite.yml").read_text(encoding="utf-8")
        self.assertIn("20 * 60 * 60 * 1000", workflow)  # retained for explicit sync-latest safety window
        self.assertIn("60 * 60 * 1000", workflow)
        self.assertIn("10 * 60 * 1000", workflow)
        self.assertIn("6 * 60 * 60 * 1000", workflow)
        self.assertIn("12 * 60 * 60 * 1000", workflow)
        self.assertNotIn("secrets.", workflow)
        self.assertNotIn("curl ", workflow)


    def test_control_center_bridge_has_one_trigger_path_and_deduplicates_all_run_events(self):
        bridge = Path(".github/workflows/dispatch-daily-suite.yml").read_text(encoding="utf-8")
        control_center_block = bridge.split('if (action === "control-center") {', 1)[1].split('if (action === "lighthouse") {', 1)[0]
        self.assertIn('["workflow_run", "workflow_dispatch", "schedule"].includes(run.event)', control_center_block)
        self.assertIn('run.status !== "completed" || run.conclusion === "success"', control_center_block)
        self.assertIn("github.rest.actions.createWorkflowDispatch", control_center_block)

        control_center = Path(".github/workflows/control-center.yml").read_text(encoding="utf-8")
        workflow_run_triggers = control_center.split("workflow_run:", 1)[1].split("push:", 1)[0]
        self.assertNotIn('"Pet traffic secure workflow dispatch"', workflow_run_triggers)
        self.assertIn('"Pet traffic daily automation suite"', workflow_run_triggers)
        self.assertIn('"Pet traffic Lighthouse audits"', workflow_run_triggers)
        self.assertIn('"Deploy PetTraffic control API"', workflow_run_triggers)
        self.assertIn("workflow_dispatch:", control_center)

if __name__ == "__main__":
    unittest.main()
