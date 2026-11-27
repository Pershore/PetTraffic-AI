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
        self.assertIn("Date.parse(run.created_at) >= dailySuiteScheduleAt.getTime()", workflow)
        self.assertIn('run.event === "schedule"', workflow)
        self.assertIn("This manual fallback is not schedule provenance", workflow)

    def test_plain_manual_daily_suite_does_not_suppress_owner_bridge(self):
        workflow = Path(".github/workflows/dispatch-daily-suite.yml").read_text(encoding="utf-8")
        daily_block = workflow.split('if (action === "daily-suite") {', 1)[1].split('if (action === "sync-latest") {', 1)[0]
        self.assertIn("A plain workflow_dispatch is not valid AI evidence", daily_block)
        self.assertIn('run.event === "workflow_dispatch"', daily_block)
        self.assertIn("run.display_title", daily_block)
        self.assertIn("Owner-approved fallback", daily_block)
        self.assertIn("bridge=(\\d+)", daily_block)
        self.assertNotIn("recentManualFallback", daily_block)
        self.assertNotIn("createdAt >= utcDayStart.getTime()", daily_block)

    def test_only_verified_owner_bridge_dispatch_suppresses_fallback(self):
        workflow = Path(".github/workflows/dispatch-daily-suite.yml").read_text(encoding="utf-8")
        daily_block = workflow.split('if (action === "daily-suite") {', 1)[1].split('if (action === "sync-latest") {', 1)[0]
        for expected in (
            "github.rest.actions.getWorkflowRun",
            "github.rest.issues.getComment",
            "bridge.workflow_id === 418997808",
            'bridge.event === "issue_comment"',
            'bridge.actor?.login === "Pershore"',
            'comment.user?.login === "Pershore"',
            '["Pershore", "github-actions[bot]"].includes(run.actor?.login)',
            "comment.body ||",
            "/pettraffic-run-daily-suite",
            "issueNumber === 145",
            "bridgeAt - commentAt <= 10 * 60 * 1000",
            "runAt - bridgeAt <= 10 * 60 * 1000",
            "validSequence",
            "recovery stopped to avoid an unsafe duplicate",
        ):
            with self.subTest(expected=expected):
                self.assertIn(expected, daily_block)
        self.assertIn('run.event === "schedule"', daily_block)
        self.assertIn('run.event === "workflow_dispatch"', daily_block)
        self.assertIn('run.status !== "completed" || run.conclusion === "success"', daily_block)

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

    def test_owner_bridge_fallback_runs_complete_evidence_recovery_chain(self):
        bridge = Path(".github/workflows/dispatch-daily-suite.yml").read_text(encoding="utf-8")
        daily_block = bridge.split('if (action === "daily-suite") {', 1)[1].split('if (action === "sync-latest") {', 1)[0]
        self.assertIn("timeout-minutes: 25", bridge)
        self.assertIn("recoveryDeadline = Date.now() + 24 * 60 * 1000", daily_block)
        self.assertIn("allowedWait = Math.min(timeoutMs", daily_block)
        for expected in (
            "waitForCompletion",
            'source_kind: "daily_suite"',
            'workflow_id: "control-center.yml"',
            'source_kind: "control_center"',
            'workflow_id: "worker-agent-diagnostics.yml"',
            "Control Center D1 snapshot sync",
            "read-only Worker agent diagnostics",
        ):
            with self.subTest(expected=expected):
                self.assertIn(expected, daily_block)
        self.assertIn('["analytics", "topic-radar", "live-check"]', daily_block)
        self.assertIn("Every stage completed successfully", daily_block)

        sync = Path(".github/workflows/sync-control-api.yml").read_text(encoding="utf-8")
        self.assertIn("- control_center", sync)
        self.assertIn('sourceKind === "control_center"', sync)
        self.assertIn("daily_suite_sync_run_id", sync)
        self.assertIn("validDailySync", sync)
        self.assertIn("Download manually dispatched Control Center artifact", sync)
        self.assertIn("Pet traffic central control center", sync)

    def test_owner_bridge_reuses_existing_control_center_sync_and_diagnostics_runs(self):
        bridge = Path(".github/workflows/dispatch-daily-suite.yml").read_text(encoding="utf-8")
        daily_block = bridge.split('if (action === "daily-suite") {', 1)[1].split('if (action === "sync-latest") {', 1)[0]
        self.assertIn('const eligibleControlEvents = ["workflow_dispatch", "workflow_run", "push", "schedule"];', daily_block)
        self.assertIn("eligibleControlEvents.includes(run.event)", daily_block)
        self.assertIn('run.head_branch === "main"', daily_block)
        self.assertIn('const controlSyncWorkflowRunTitle = "Sync workflow-run snapshot #" + controlRun.id;', daily_block)
        self.assertIn('run.event === "workflow_run" && run.display_title === controlSyncWorkflowRunTitle', daily_block)
        self.assertIn('const diagnosticsWorkflowRunTitle = "Read-only Worker diagnostics after sync #" + controlSync.id;', daily_block)
        self.assertIn('run.event === "workflow_run" && run.display_title === diagnosticsWorkflowRunTitle', daily_block)
        self.assertIn('run.display_title === "Sync PetTraffic snapshots to central API"', daily_block)
        self.assertIn('run.display_title === "Pet traffic read-only Worker agent diagnostics"', daily_block)
        self.assertIn("const automaticRunReuseWindowMs = 10 * 60 * 1000;", daily_block)
        self.assertEqual(daily_block.count("const automaticRunReuseWindowMs ="), 1)
        manual_match = daily_block.split("const manualMatch =", 1)[1].split("const workflowRunMatch", 1)[0]
        self.assertIn('run.display_title === "Pet traffic read-only Worker agent diagnostics"', manual_match)
        self.assertIn("Date.parse(run.created_at) <= controlSyncCompletedAt + automaticRunReuseWindowMs", manual_match)

        sync = Path(".github/workflows/sync-control-api.yml").read_text(encoding="utf-8")
        self.assertIn("format('Sync workflow-run snapshot #{0}', github.event.workflow_run.id)", sync)

        diagnostics = Path(".github/workflows/worker-agent-diagnostics.yml").read_text(encoding="utf-8")
        self.assertIn("format('Read-only Worker diagnostics after sync #{0}', github.event.workflow_run.id)", diagnostics)


    def test_owner_bridge_github_script_blocks_parse_as_javascript(self):
        import shutil
        import subprocess
        import textwrap

        node = shutil.which("node")
        if not node:
            self.skipTest("Node.js is not installed in this test environment.")

        for relative in (
            ".github/workflows/dispatch-daily-suite.yml",
            ".github/workflows/sync-control-api.yml",
        ):
            workflow = Path(relative).read_text(encoding="utf-8")
            lines = workflow.splitlines()
            for index, line in enumerate(lines):
                if line.strip() != "script: |":
                    continue
                script_lines = []
                for candidate in lines[index + 1:]:
                    if candidate.strip() and len(candidate) - len(candidate.lstrip()) < 12:
                        break
                    script_lines.append(candidate[12:] if candidate.startswith("            ") else "")
                script = textwrap.dedent("\n".join(script_lines))
                wrapped = "async function __workflow_script_check__() {\n" + script + "\n}\n"
                result = subprocess.run(
                    [node, "--check"],
                    input=wrapped,
                    text=True,
                    capture_output=True,
                    check=False,
                )
                with self.subTest(workflow=relative, script_line=index + 1):
                    self.assertEqual(result.returncode, 0, result.stderr or result.stdout)

if __name__ == "__main__":
    unittest.main()
