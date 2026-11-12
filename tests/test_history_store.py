import json
import tempfile
import unittest
from pathlib import Path

from agent.history_store import store_snapshot


class HistoryStoreTests(unittest.TestCase):
    def test_stores_aggregate_snapshot_by_utc_day(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            data = {
                "generated_at": "2026-11-12T08:00:00+00:00",
                "needs_attention": True,
                "results": [{"name": "Analytics", "state": "failure", "detail": "failed"}],
            }
            path = store_snapshot(data, "run-1", root)
            saved = json.loads(path.read_text(encoding="utf-8"))
            self.assertEqual(path.name, "2026-11-12.json")
            self.assertEqual(saved["snapshots"][0]["run_id"], "run-1")
            self.assertEqual(saved["snapshots"][0]["results"][0]["state"], "failure")

    def test_is_idempotent_for_same_run_id(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            data = {"generated_at": "2026-11-12T08:00:00Z", "results": []}
            path = store_snapshot(data, "run-1", root)
            store_snapshot(data, "run-1", root)
            saved = json.loads(path.read_text(encoding="utf-8"))
            self.assertEqual(len(saved["snapshots"]), 1)

    def test_keeps_multiple_runs_on_same_day(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            data = {"generated_at": "2026-11-12T08:00:00Z", "results": []}
            path = store_snapshot(data, "run-1", root)
            store_snapshot(data, "run-2", root)
            saved = json.loads(path.read_text(encoding="utf-8"))
            self.assertEqual(len(saved["snapshots"]), 2)

    def test_rejects_invalid_date_or_missing_run_id(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            with self.assertRaises(ValueError):
                store_snapshot({"generated_at": "not-a-date"}, "run-1", root)
            with self.assertRaises(ValueError):
                store_snapshot({"generated_at": "2026-11-12T08:00:00Z"}, "", root)


if __name__ == "__main__":
    unittest.main()
