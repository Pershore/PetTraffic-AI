import unittest
from summarize_lighthouse import build_summary, fmt_metric, insights

class LighthouseSummaryTests(unittest.TestCase):
    def test_formats_core_web_vitals(self):
        audits = {
            "largest-contentful-paint": {"numericValue": 1727.6},
            "total-blocking-time": {"numericValue": 853.8},
            "cumulative-layout-shift": {"numericValue": 0.01234},
        }
        self.assertEqual(fmt_metric(audits, "largest-contentful-paint", "s"), "1.73 s")
        self.assertEqual(fmt_metric(audits, "total-blocking-time", "ms"), "854 ms")
        self.assertEqual(fmt_metric(audits, "cumulative-layout-shift", ""), "0.012")

    def test_summary_includes_scores_and_mobile_diagnostics(self):
        data = {
            "categories": {
                "performance": {"score": 0.8},
                "accessibility": {"score": 1},
                "best-practices": {"score": 1},
                "seo": {"score": 1},
            },
            "audits": {
                "largest-contentful-paint": {"numericValue": 1700},
                "total-blocking-time": {"numericValue": 850},
                "cumulative-layout-shift": {"numericValue": 0.01},
                "mainthread-work-breakdown": {"details": {"items": [
                    {"groupLabel": "Other", "duration": 1500},
                    {"groupLabel": "Style & Layout", "duration": 620},
                ]}},
                "largest-contentful-paint-element": {"details": {"items": [
                    {"items": [{"node": {"nodeLabel": "Hero heading"}}]},
                    {"items": [{"phase": "Render Delay", "timing": 1100, "percent": "65%"}]},
                ]}},
                "render-blocking-resources": {
                    "title": "Eliminate render-blocking resources",
                    "details": {"overallSavingsMs": 110},
                },
                "long-tasks": {"details": {"items": [
                    {"duration": 396, "url": "Unattributable"},
                ]}},
            },
        }
        summary = build_summary([("home-mobile", data)])
        self.assertIn("| home-mobile | 80 | 100 | 100 | 100 |", summary)
        self.assertIn("TBT: 850 ms", summary)
        self.assertIn("LCP elementas:** Hero heading", summary)
        self.assertIn("Style & Layout 620 ms", summary)
        self.assertIn("110 ms", summary)
        self.assertIn("nepriskirta", summary)

    def test_insights_handles_missing_audits(self):
        self.assertIn("TBT: —", "\n".join(insights("page-mobile", {"audits": {}})))

if __name__ == "__main__":
    unittest.main()
