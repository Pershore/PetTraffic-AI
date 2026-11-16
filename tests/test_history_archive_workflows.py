import unittest
from pathlib import Path


ARCHIVE_WORKFLOWS = (
    ".github/workflows/control-center.yml",
    ".github/workflows/daily-suite.yml",
    ".github/workflows/lighthouse-audit.yml",
    ".github/workflows/analytics-snapshot.yml",
    ".github/workflows/daily-topic-radar.yml",
    ".github/workflows/weekly-growth-review.yml",
)


class HistoryArchiveWorkflowTests(unittest.TestCase):
    def test_history_writers_retry_non_fast_forward_pushes(self):
        for relative_path in ARCHIVE_WORKFLOWS:
            with self.subTest(workflow=relative_path):
                workflow = Path(relative_path).read_text(encoding="utf-8")
                self.assertIn("for attempt in 1 2 3 4 5; do", workflow)
                self.assertIn("if git push origin automation-history; then", workflow)
                self.assertIn("git pull --rebase origin automation-history", workflow)
                self.assertIn("git archive FETCH_HEAD reports/history", workflow)
                self.assertIn("git checkout -B automation-history FETCH_HEAD", workflow)
                self.assertNotIn("git archive origin/automation-history", workflow)
                self.assertNotIn("git checkout -B automation-history origin/automation-history", workflow)
                self.assertIn('sleep "$attempt"', workflow)
                self.assertIn('if [ "$attempt" -eq 5 ]; then', workflow)
                self.assertIn('echo "::error::Could not push automation-history after 5 attempts."', workflow)

    def test_control_center_resolves_only_generated_latest_pointer_conflicts(self):
        workflow = Path(".github/workflows/control-center.yml").read_text(encoding="utf-8")
        self.assertIn('conflicts="$(git diff --name-only --diff-filter=U | sort)"', workflow)
        self.assertIn("reports/history/project-state/latest.md|reports/history/project-state/latest.json)", workflow)
        self.assertIn('git checkout --theirs -- "$path"', workflow)
        self.assertIn("GIT_EDITOR=true git rebase --continue", workflow)
        self.assertIn("git rebase --abort", workflow)
        self.assertIn("Unexpected automation-history conflict(s)", workflow)

        for relative_path in ARCHIVE_WORKFLOWS:
            if relative_path == ".github/workflows/control-center.yml":
                continue
            with self.subTest(workflow=relative_path):
                other_workflow = Path(relative_path).read_text(encoding="utf-8")
                self.assertNotIn("git checkout --theirs", other_workflow)


if __name__ == "__main__":
    unittest.main()
