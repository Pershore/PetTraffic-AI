import json
import tempfile
import unittest
from pathlib import Path

from agent.recommendations import build_recommendations


def save(root: Path, category: str, day: str, snapshots: list[dict]) -> None:
    folder = root / category
    folder.mkdir(parents=True, exist_ok=True)
    (folder / f"{day}.json").write_text(
        json.dumps({"date": day, "snapshots": snapshots}), encoding="utf-8"
    )


class RecommendationTests(unittest.TestCase):
    def analytics(self, run_id: str, impressions: int = 0, clicks: int = 0) -> dict:
        return {
            "run_id": run_id,
            "generated_at": f"2026-11-{int(run_id[-1]) + 10:02d}T08:00:00Z",
            "ga4_status": "available",
            "search_console_status": "available",
            "search_console_period": f"2026-11-{int(run_id[-1]) + 1:02d} – 2026-11-{int(run_id[-1]) + 7:02d}",
            "metrics": {
                "sessions": 12,
                "organic_sessions_verified": None,
                "search_impressions": impressions,
                "search_clicks": clicks,
            },
        }

    def test_one_zero_period_is_only_a_baseline_observation(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            save(root, "analytics", "2026-11-11", [self.analytics("run-1")])
            items = build_recommendations(root)
            self.assertIn("search-visibility-baseline", [x["id"] for x in items])
            self.assertNotIn("search-visibility", [x["id"] for x in items])

    def test_two_zero_periods_create_visibility_recommendation(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            save(root, "analytics", "2026-11-11", [self.analytics("run-1")])
            save(root, "analytics", "2026-11-12", [self.analytics("run-2")])
            items = build_recommendations(root)
            self.assertIn("search-visibility", [x["id"] for x in items])


    def test_repeated_runs_for_same_reporting_period_are_not_independent(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            first = self.analytics("run-1")
            second = self.analytics("run-2")
            second["search_console_period"] = first["search_console_period"]
            save(root, "analytics", "2026-11-11", [first])
            save(root, "analytics", "2026-11-12", [second])
            items = build_recommendations(root)
            self.assertNotIn("search-visibility", [x["id"] for x in items])

    def test_automation_failure_creates_high_priority_recommendation(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            save(root, "control-center", "2026-11-12", [{
                "run_id": "run-1",
                "generated_at": "2026-11-12T10:00:00Z",
                "results": [{"name": "Analytics", "state": "failure"}],
            }])
            items = build_recommendations(root)
            problem = next(x for x in items if x["id"] == "automation-health")
            self.assertEqual(problem["priority"], "high")

    def test_missing_history_produces_baseline_not_claims(self):
        with tempfile.TemporaryDirectory() as directory:
            items = build_recommendations(Path(directory))
            ids = [x["id"] for x in items]
            self.assertIn("analytics-baseline", ids)
            self.assertIn("topic-baseline", ids)

    def test_unsubmitted_sitemap_creates_high_priority_recommendation(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            item = self.analytics("run-1", impressions=4, clicks=0)
            item["search_console_details"] = {
                "sitemap": {"status": "not_submitted"},
                "priority_url_inspections": [],
            }
            save(root, "analytics", "2026-11-11", [item])
            recommendations = build_recommendations(root)
            sitemap = next(x for x in recommendations if x["id"] == "sitemap-not-submitted")
            self.assertEqual(sitemap["priority"], "high")

    def test_sitemap_indexing_gap_creates_medium_recommendation(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            item = self.analytics("run-1", impressions=4, clicks=0)
            item["search_console_details"] = {
                "sitemap": {"status": "submitted", "submitted_urls": 7, "indexed_urls": 4},
                "priority_url_inspections": [],
            }
            save(root, "analytics", "2026-11-11", [item])
            recommendations = build_recommendations(root)
            gap = next(x for x in recommendations if x["id"] == "sitemap-indexing-gap")
            self.assertEqual(gap["priority"], "medium")

    def test_blocked_priority_url_creates_high_priority_recommendation(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            item = self.analytics("run-1", impressions=4, clicks=0)
            item["search_console_details"] = {
                "sitemap": {"status": "submitted"},
                "priority_url_inspections": [{
                    "url_path": "/important.html",
                    "verdict": "FAIL",
                    "coverage": "Blocked by robots.txt",
                    "robots_txt_state": "DISALLOWED",
                    "indexing_state": "BLOCKED_BY_ROBOTS_TXT",
                    "last_crawl": "Never",
                }],
            }
            save(root, "analytics", "2026-11-11", [item])
            recommendations = build_recommendations(root)
            blocked = next(x for x in recommendations if x["id"] == "priority-url-blocked")
            self.assertEqual(blocked["priority"], "high")


if __name__ == "__main__":
    unittest.main()
