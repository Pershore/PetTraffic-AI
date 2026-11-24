import json
import tempfile
import unittest
from pathlib import Path

from agent.topic_history import parse_report, store_snapshot
from agent.topic_radar import fetch_topics
import threading
import time


REPORT = """# Pet traffic – kasdienių temų radaras
## Temos pagal surinktų antraščių skaičių
- **šunų priežiūra** – 8 antraščių
- **kačių priežiūra** – 5 antraščių
Unikalių straipsnių nuorodų: **11**
Temų užklausų be rezultatų: **2 iš 7**
"""


class TopicHistoryTests(unittest.TestCase):
    def test_extracts_topic_counts_without_article_content(self):
        item = parse_report(REPORT, "run-1", "2026-11-12T08:00:00Z")
        self.assertEqual(item["topic_counts"]["šunų priežiūra"], 8)
        self.assertEqual(item["unique_article_links"], 11)
        self.assertEqual(item["empty_topic_checks"], 2)
        self.assertEqual(item["total_topic_checks"], 7)
        self.assertNotIn("query", json.dumps(item).lower())
        self.assertNotIn("antraštės", json.dumps(item).lower())
        self.assertNotIn("https://", json.dumps(item))

    def test_stores_and_deduplicates_run(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            item = parse_report(REPORT, "run-1", "2026-11-12T08:00:00Z")
            path = store_snapshot(item, root)
            store_snapshot(item, root)
            saved = json.loads(path.read_text(encoding="utf-8"))
            self.assertEqual(len(saved["snapshots"]), 1)
            self.assertEqual(path.name, "2026-11-12.json")


class TopicRadarFetchTests(unittest.TestCase):
    def test_fetch_topics_uses_bounded_concurrency_and_preserves_order_and_partial_results(self):
        topics = [f"topic-{index}" for index in range(7)]
        lock = threading.Lock()
        three_started = threading.Event()
        active = 0
        peak = 0

        def fake_fetch(topic):
            nonlocal active, peak
            with lock:
                active += 1
                peak = max(peak, active)
                if active >= 3:
                    three_started.set()
            three_started.wait(timeout=1)
            time.sleep(0.005 if topic in ("topic-0", "topic-3") else 0.02)
            with lock:
                active -= 1
            if topic == "topic-3":
                return []
            return [{"title": topic, "link": topic}]

        results = fetch_topics(topics, fetcher=fake_fetch, max_workers=3)
        self.assertEqual(peak, 3)
        self.assertEqual(len(results), len(topics))
        self.assertEqual(results[0], [{"title": "topic-0", "link": "topic-0"}])
        self.assertEqual(results[3], [])
        self.assertEqual(results[6], [{"title": "topic-6", "link": "topic-6"}])

    def test_fetch_topics_handles_empty_input_and_rejects_invalid_worker_limit(self):
        self.assertEqual(fetch_topics([], fetcher=lambda topic: [], max_workers=3), [])
        with self.assertRaises(ValueError):
            fetch_topics(["topic"], fetcher=lambda topic: [], max_workers=0)


if __name__ == "__main__":
    unittest.main()
