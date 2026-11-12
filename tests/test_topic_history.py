import json
import tempfile
import unittest
from pathlib import Path

from agent.topic_history import parse_report, store_snapshot


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
        self.assertEqual(item["empty_topic_queries"], 2)
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


if __name__ == "__main__":
    unittest.main()
