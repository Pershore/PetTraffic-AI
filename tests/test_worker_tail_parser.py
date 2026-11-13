import importlib.util
import json
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PARSER_PATH = ROOT / "tools" / "worker-tail" / "parse_logs.py"
SPEC = importlib.util.spec_from_file_location("worker_tail_parser", PARSER_PATH)
PARSER = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(PARSER)


class WorkerTailParserTests(unittest.TestCase):
    def test_string_event_type_does_not_crash_and_counts_scheduled_event(self):
        entry = {"event": "scheduled", "eventTimestamp": 123, "outcome": "ok"}
        self.assertTrue(PARSER.is_scheduled(entry))
        cron, failures = PARSER.summarize([entry])
        self.assertEqual(len(cron), 1)
        self.assertEqual(failures, [])

    def test_nested_scheduled_event_is_detected(self):
        entry = {"event": {"scheduled": {"cron": "*/15 * * * *", "scheduledTime": 123}}}
        self.assertTrue(PARSER.is_scheduled(entry))

    def test_fetch_event_is_not_counted_as_cron(self):
        entry = {"event": {"type": "fetch", "request": {"url": "https://example.test"}}}
        self.assertFalse(PARSER.is_scheduled(entry))

    def test_malformed_lines_are_ignored(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "tail.jsonl"
            path.write_text("not-json\n" + json.dumps({"event": "scheduled"}) + "\n", encoding="utf-8")
            entries = PARSER.load_entries(path)
        self.assertEqual(len(entries), 1)
        self.assertTrue(PARSER.is_scheduled(entries[0]))

    def test_failure_is_detected_without_printing_payload(self):
        entry = {"event": "scheduled", "outcome": "exception", "exceptions": [{"name": "Error"}]}
        cron, failures = PARSER.summarize([entry])
        self.assertEqual(len(cron), 1)
        self.assertEqual(len(failures), 1)


if __name__ == "__main__":
    unittest.main()
