import json
import tempfile
import unittest
from pathlib import Path

from worker.scripts.build_event import build_events


class BuildEventTests(unittest.TestCase):
    def test_analytics_artifact_becomes_aggregate_event(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "analytics-7d.md").write_text(
                "# Analytics\nGA4 laikotarpis: 2026-11-05 – 2026-11-11\n"
                "## Pagrindiniai rodikliai (GA4)\n"
                "| Aktyvūs naudotojai | 7 |\n"
                "| Sesijos / apsilankymai | 14 |\n"
                "## Google paieška (Search Console)\n"
                "Laikotarpis: 2026-11-03 – 2026-11-09\n"
                "| Paieškos parodymai | 12 |\n"
                "| Paspaudimai | 2 |\n",
                encoding="utf-8",
            )
            events = build_events("Pet traffic analytics snapshot", root, "run-123")
            self.assertEqual(events[0]["kind"], "analytics_snapshot")
            self.assertEqual(events[0]["payload"]["run_id"], "run-123")
            self.assertEqual(events[0]["payload"]["metrics"]["sessions"], 14)

    def test_topic_artifact_stores_aggregates_not_headlines(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "topic-radar.md").write_text(
                "# Temų radaras\n- **Katės mityba** – 5 antraščių\n"
                "Unikalių straipsnių nuorodų: **4**\n"
                "Temų užklausų be rezultatų: **1 iš 7**\n",
                encoding="utf-8",
            )
            events = build_events("Pet traffic daily topic radar", root, "run-456")
            payload = events[0]["payload"]
            self.assertEqual(events[0]["kind"], "topic_snapshot")
            self.assertEqual(payload["topic_counts"]["Katės mityba"], 5)
            self.assertNotIn("headlines", payload)

    def test_control_center_and_recommendations_are_separate_events(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "control-center.json").write_text(json.dumps({
                "generated_at": "2026-11-12T10:00:00Z",
                "needs_attention": False,
                "results": [{"name": "Analytics", "state": "success", "detail": "OK", "url": None}],
            }), encoding="utf-8")
            (root / "recommendations.json").write_text(json.dumps({
                "generated_at": "2026-11-12T10:00:00Z",
                "recommendations": [{"id": "steady", "priority": "info", "title": "Monitor", "evidence": "No issue", "next_action": "Continue", "status": "monitor"}],
            }), encoding="utf-8")
            events = build_events("Pet traffic central control center", root, "run-789")
            self.assertEqual([event["kind"] for event in events], [
                "control_center_snapshot", "recommendation_snapshot"
            ])
            self.assertEqual(events[0]["payload"]["run_id"], "run-789")
            self.assertEqual(events[1]["payload"]["recommendations"][0]["id"], "steady")

    def test_unsupported_workflow_is_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            with self.assertRaises(ValueError):
                build_events("Other workflow", Path(directory), "run-x")


if __name__ == "__main__":
    unittest.main()
