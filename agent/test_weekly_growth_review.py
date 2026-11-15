import json
import tempfile
import unittest
from pathlib import Path

from weekly_growth_review import build_review, render_markdown, persist_review


def save_category(root: Path, category: str, day: str, snapshots: list[dict]) -> None:
    folder = root / category
    folder.mkdir(parents=True, exist_ok=True)
    (folder / f"{day}.json").write_text(
        json.dumps({"date": day, "snapshots": snapshots}, ensure_ascii=False),
        encoding="utf-8",
    )


class WeeklyGrowthReviewTests(unittest.TestCase):
    def test_combines_sources_and_selects_three_evidence_based_actions(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            old_analytics = {
                "run_id": "old",
                "generated_at": "2026-11-09T18:00:00+00:00",
                "ga4_status": "available",
                "ga4_period": "2026-11-02 – 2026-11-08",
                "search_console_status": "available",
                "search_console_period": "2026-10-30 – 2026-11-05",
                "metrics": {
                    "active_users": 5, "new_users": 4, "sessions": 12, "page_views": 44,
                    "organic_sessions_verified": 0, "search_impressions": 700,
                    "search_clicks": 12, "search_ctr": 0.017, "average_position": 18.0,
                },
                "ga4_top_pages": [{"path": "/old.html", "views": 20}],
                "search_console_details": {"sitemap": {"status": "submitted", "is_pending": False}},
                "search_intent_themes": {},
                "search_console_top_pages": [],
            }
            current_analytics = {
                "run_id": "current",
                "generated_at": "2026-11-16T17:00:00+00:00",
                "ga4_status": "available",
                "ga4_period": "2026-11-09 – 2026-11-15",
                "search_console_status": "available",
                "search_console_period": "2026-11-06 – 2026-11-12",
                "metrics": {
                    "active_users": 9, "new_users": 7, "sessions": 24, "page_views": 88,
                    "organic_sessions_verified": None, "search_impressions": 1400,
                    "search_clicks": 30, "search_ctr": 0.021, "average_position": 15.5,
                },
                "ga4_top_pages": [{"path": "/articles/cate.html", "views": 50}],
                "search_console_details": {"sitemap": {"status": "submitted", "is_pending": True}},
                "search_intent_themes": {
                    "simptomai_ir_sveikata": {"rows": 3, "clicks": 8, "impressions": 800, "ctr": 0.01, "average_position": 10.2}
                },
                "search_console_top_pages": [
                    {"path": "/articles/cate.html", "clicks": 8, "impressions": 800, "ctr": 0.01, "average_position": 10.2}
                ],
            }
            save_category(root, "analytics", "2026-11-09", [old_analytics])
            save_category(root, "analytics", "2026-11-16", [current_analytics])

            topic = []
            for day in range(10, 17):
                topic.append({
                    "run_id": f"topic-{day}",
                    "generated_at": f"2026-11-{day:02d}T12:00:00+00:00",
                    "topic_counts": {"kačių priežiūra": 4, "augintinių mityba": 2},
                    "unique_article_links": 6,
                })
            save_category(root, "topic-radar", "2026-11-16", topic)
            old_lighthouse = {
                "run_id": "lh-old",
                "generated_at": "2026-11-09T10:00:00+00:00",
                "pages": [{
                    "page": "home", "device": "mobile", "path": "/",
                    "scores": {"performance": 90, "accessibility": 100, "best-practices": 100, "seo": 100},
                    "vitals": {"lcp_ms": 2200, "tbt_ms": 150, "cls": 0.02},
                }],
            }
            current_lighthouse = {
                "run_id": "lh-current",
                "generated_at": "2026-11-16T10:00:00+00:00",
                "pages": [{
                    "page": "home", "device": "mobile", "path": "/",
                    "scores": {"performance": 97, "accessibility": 100, "best-practices": 100, "seo": 100},
                    "vitals": {"lcp_ms": 1800, "tbt_ms": 100, "cls": 0.01},
                }],
            }
            save_category(root, "lighthouse", "2026-11-09", [old_lighthouse])
            save_category(root, "lighthouse", "2026-11-16", [current_lighthouse])
            save_category(root, "control-center", "2026-11-16", [{
                "run_id": "control", "generated_at": "2026-11-16T17:30:00+00:00",
                "results": [{"name": "Worker", "state": "success"}],
            }])
            save_category(root, "recommendations", "2026-11-16", [{
                "run_id": "recs",
                "generated_at": "2026-11-16T17:30:00+00:00",
                "recommendations": [{
                    "id": "indexing", "priority": "medium", "title": "Patikrinti indeksavimą",
                    "evidence": "Sitemap pending.", "next_action": "Peržiūrėti URL būsenas.",
                }],
            }])
            (root / "project-state").mkdir(parents=True)
            (root / "project-state" / "latest.json").write_text(json.dumps({
                "generated_at": "2026-11-16T17:30:00+00:00",
                "overall_status": "needs_attention",
                "next_action": "Atkurti AI agentų ciklą.",
                "problems": [{
                    "name": "AI agentai", "state": "stale", "detail": "Naujas ciklas dar nepatvirtintas."
                }],
                "pending_checks": [],
                "ai_agent_memory_check": {
                    "state": "stale", "detail": "Laukiama naujo ciklo."
                },
            }), encoding="utf-8")

            review = build_review(root, "weekly-1", "2026-11-16T18:30:00+00:00")
            markdown = render_markdown(review)
            self.assertEqual(review["analytics"]["ga4"]["metrics"]["sessions"]["current"], 24)
            self.assertEqual(review["analytics"]["ga4"]["metrics"]["sessions"]["change"], "+100.0 %")
            self.assertEqual(review["analytics"]["search_console"]["metrics"]["search_impressions"]["current"], 1400)
            self.assertEqual(review["topics"]["days_covered"], 7)
            self.assertEqual(review["lighthouse"]["pages"][0]["scores"]["performance"]["current"], 97)
            self.assertEqual(review["system"]["overall_status"], "needs_attention")
            self.assertEqual(review["next_actions"][0]["title"], "AI agentai")
            self.assertLessEqual(len(review["next_actions"]), 3)
            self.assertIn("kanalų pasiskirstymas nepatvirtintas", markdown)
            self.assertIn("ne Google paieškų apimtis", markdown)

    def test_missing_sources_are_not_reported_as_zero(self):
        with tempfile.TemporaryDirectory() as directory:
            review = build_review(Path(directory), "empty", "2026-11-16T18:30:00+00:00")
            markdown = render_markdown(review)
            self.assertEqual(review["analytics"]["ga4"]["status"], "missing")
            self.assertIsNone(review["analytics"]["ga4"]["metrics"]["sessions"]["current"])
            self.assertIn("duomenų nėra", markdown)
            self.assertNotIn("0 sesijų per GA4", markdown)
            self.assertEqual(review["topics"]["days_covered"], 0)
            self.assertEqual(review["lighthouse"]["pages"], [])

    def test_persists_markdown_latest_and_daily_snapshot(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            review = build_review(root, "report-1", "2026-11-16T18:30:00+00:00")
            markdown = render_markdown(review)
            daily, latest_json, latest_md = persist_review(review, markdown, root)
            persist_review(review, markdown, root)
            saved = json.loads(daily.read_text(encoding="utf-8"))
            self.assertEqual(len(saved["snapshots"]), 1)
            self.assertTrue(latest_json.exists())
            self.assertTrue(latest_md.exists())
            self.assertNotIn("query", latest_json.read_text(encoding="utf-8").lower())


if __name__ == "__main__":
    unittest.main()
