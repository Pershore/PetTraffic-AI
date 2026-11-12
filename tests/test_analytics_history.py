import json
import tempfile
import unittest
from pathlib import Path

from agent.analytics_history import parse_report, store_snapshot


REPORT = """# Pet traffic – lankomumo ataskaita
GA4 laikotarpis: 2026-11-05 – 2026-11-11

## Pagrindiniai rodikliai (GA4)
| Rodiklis | Paskutinės 7 d. | Pokytis |
|---|---:|---:|
| Aktyvūs naudotojai | 7 | +1 |
| Nauji naudotojai | 6 | +2 |
| Sesijos / apsilankymai | 14 | +3 |
| Puslapių peržiūros | 67 | +4 |
Organinės paieškos sesijos: **3**

## Google paieška (Search Console)
Laikotarpis: 2026-11-03 – 2026-11-09
| Rodiklis | Paskutinės 7 d. | Pokytis |
|---|---:|---:|
| Paieškos parodymai | 2502 | +100 |
| Paspaudimai | 123 | +5 |
| CTR | 4.9% | +0.2 |
| Vidutinė pozicija | 10.7 | -1 |
"""


class AnalyticsHistoryTests(unittest.TestCase):
    def test_extracts_only_aggregate_metrics(self):
        item = parse_report(REPORT, "run-1", "2026-11-12T08:00:00Z")
        self.assertEqual(item["ga4_status"], "available")
        self.assertEqual(item["metrics"]["active_users"], 7)
        self.assertEqual(item["metrics"]["page_views"], 67)
        self.assertEqual(item["metrics"]["search_impressions"], 2502)
        self.assertEqual(item["metrics"]["search_clicks"], 123)
        self.assertAlmostEqual(item["metrics"]["search_ctr"], 0.049)
        self.assertEqual(item["metrics"]["organic_sessions_verified"], 3)
        self.assertNotIn("query", json.dumps(item).lower())

    def test_marks_missing_metrics_as_null(self):
        item = parse_report("# Pet traffic\nBūsena: neprijungta", "run-2", "2026-11-12T08:00:00Z")
        self.assertEqual(item["ga4_status"], "not_connected")
        self.assertIsNone(item["metrics"]["sessions"])

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
