import json
import tempfile
import unittest
from pathlib import Path

from lighthouse_history import build_snapshot, store_snapshot


class LighthouseHistoryTests(unittest.TestCase):
    def test_archives_only_scores_and_core_vitals(self):
        with tempfile.TemporaryDirectory() as directory:
            report = Path(directory) / "home-mobile.report.json"
            report.write_text(json.dumps({
                "requestedUrl": "https://pettraffic-ai.pages.dev/articles/test.html?secret=no",
                "categories": {
                    "performance": {"score": 0.97},
                    "accessibility": {"score": 1},
                    "best-practices": {"score": 1},
                    "seo": {"score": 1},
                },
                "audits": {
                    "largest-contentful-paint": {"numericValue": 1800},
                    "total-blocking-time": {"numericValue": 120},
                    "cumulative-layout-shift": {"numericValue": 0.01},
                },
                "fullAuditPayload": {"private": "must not be copied"},
            }), encoding="utf-8")
            snapshot = build_snapshot(
                [str(report)], "run-123", "2026-11-16T12:00:00+00:00"
            )
            page = snapshot["pages"][0]
            self.assertEqual(page["path"], "/articles/test.html")
            self.assertEqual(page["device"], "mobile")
            self.assertEqual(page["scores"]["performance"], 97)
            self.assertEqual(page["vitals"]["lcp_ms"], 1800)
            serialized = json.dumps(snapshot)
            self.assertNotIn("fullAuditPayload", serialized)
            self.assertNotIn("secret=no", serialized)

    def test_persists_and_deduplicates_by_run_id(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            snapshot = {
                "run_id": "run-123",
                "generated_at": "2026-11-16T12:00:00+00:00",
                "page_count": 1,
                "pages": [],
            }
            path = store_snapshot(snapshot, root)
            store_snapshot(snapshot, root)
            saved = json.loads(path.read_text(encoding="utf-8"))
            self.assertEqual(path.name, "2026-11-16.json")
            self.assertEqual(len(saved["snapshots"]), 1)


if __name__ == "__main__":
    unittest.main()
