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
                self.assertIn('sleep "$attempt"', workflow)
                self.assertIn('if [ "$attempt" -eq 5 ]; then', workflow)
                self.assertIn('echo "::error::Could not push automation-history after 5 attempts."', workflow)


if __name__ == "__main__":
    unittest.main()
