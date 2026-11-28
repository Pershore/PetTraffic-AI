import unittest
import json
from unittest.mock import Mock, patch


from agent.analytics_report import aggregate_search_intents, api_post, channel_breakdown_status, metric_totals, gsc_metric


class SearchIntentPrivacyTests(unittest.TestCase):
    def test_aggregates_themes_without_returning_raw_phrases(self):
        rows = [
            {"keys": ["mano kates viduriavimas"], "clicks": 3, "impressions": 120, "position": 8.4},
            {"keys": ["geriausias maistas sunims"], "clicks": 2, "impressions": 80, "position": 6.0},
        ]
        result = aggregate_search_intents(rows)
        self.assertEqual(result["simptomai_ir_sveikata"]["rows"], 1)
        self.assertEqual(result["simptomai_ir_sveikata"]["impressions"], 120)
        self.assertEqual(result["maitinimas_ir_mityba"]["clicks"], 2)
        serialized = json.dumps(result, ensure_ascii=False).lower()
        self.assertNotIn("mano kates viduriavimas", serialized)
        self.assertNotIn("geriausias maistas sunims", serialized)


class AnalyticsApiPostTests(unittest.TestCase):
    def test_ga4_request_uses_25_second_timeout(self):
        response = Mock(ok=True, status_code=200)
        response.json.return_value = {"rows": []}
        session = Mock()
        session.post.return_value = response

        result = api_post(session, "https://analyticsdata.googleapis.com/test", {"limit": 1})

        self.assertEqual(result, {"rows": []})
        session.post.assert_called_once_with(
            "https://analyticsdata.googleapis.com/test",
            json={"limit": 1},
            timeout=25,
        )

    def test_read_timeout_still_retries_once(self):
        class ReadTimeout(Exception):
            pass

        response = Mock(ok=True, status_code=200)
        response.json.return_value = {"rows": []}
        session = Mock()
        session.post.side_effect = [ReadTimeout("slow"), response]

        with patch("agent.analytics_report.time.sleep") as sleep:
            result = api_post(session, "https://analyticsdata.googleapis.com/test", {"limit": 1})

        self.assertEqual(result, {"rows": []})
        self.assertEqual(session.post.call_count, 2)
        sleep.assert_called_once_with(3)


class ChannelBreakdownStatusTests(unittest.TestCase):
    def test_matching_totals_are_verified(self):
        verified, note = channel_breakdown_status(14, 14, 14)
        self.assertTrue(verified)
        self.assertIn("sutampa", note)

    def test_channel_rows_mismatch_marks_breakdown_unverified(self):
        verified, note = channel_breakdown_status(16, 14, 14)
        self.assertFalse(verified)
        self.assertIn("eilučių suma", note)

    def test_aggregate_mismatch_marks_breakdown_unverified(self):
        verified, note = channel_breakdown_status(14, 14, 15)
        self.assertFalse(verified)
        self.assertIn("bendros sesijų užklausos", note)

    def test_missing_aggregate_marks_breakdown_unverified(self):
        verified, note = channel_breakdown_status(14, None, 14)
        self.assertFalse(verified)
        self.assertIn("nepateikė", note)




class MissingMetricTests(unittest.TestCase):
    def test_ga4_empty_rows_are_unknown_not_zero(self):
        self.assertEqual(
            metric_totals({"metricHeaders":[{"name":"sessions"},{"name":"screenPageViews"}],"rows":[]}),
            {"sessions":None,"screenPageViews":None},
        )

    def test_ga4_explicit_api_zero_remains_zero(self):
        self.assertEqual(
            metric_totals({"metricHeaders":[{"name":"sessions"}],"rows":[{"metricValues":[{"value":"0"}]}]}),
            {"sessions":0.0},
        )

    def test_ga4_missing_metric_value_is_unknown(self):
        self.assertEqual(
            metric_totals({"metricHeaders":[{"name":"sessions"}],"rows":[{"metricValues":[{}]}]}),
            {"sessions":None},
        )

    def test_gsc_missing_row_or_metric_is_unknown_but_explicit_zero_is_zero(self):
        self.assertIsNone(gsc_metric({"rows":[]},"impressions"))
        self.assertIsNone(gsc_metric({"rows":[{}]},"impressions"))
        self.assertEqual(gsc_metric({"rows":[{"impressions":0}]},"impressions"),0.0)

    def test_channel_breakdown_cannot_verify_missing_overall_total_or_row(self):
        verified, note = channel_breakdown_status(0,0,None)
        self.assertFalse(verified)
        self.assertIn("bendro sesijų",note)
        verified, note = channel_breakdown_status(0,0,0,rows_complete=False)
        self.assertFalse(verified)
        self.assertIn("trūksta",note)

    def test_search_intent_aggregation_skips_incomplete_metric_rows(self):
        result=aggregate_search_intents([
            {"keys":["katė viduriuoja"],"clicks":0,"impressions":0,"position":0},
            {"keys":["šuo viduriuoja"],"clicks":None,"impressions":10,"position":8},
        ])
        self.assertEqual(result["simptomai_ir_sveikata"]["rows"],1)
        self.assertEqual(result["simptomai_ir_sveikata"]["impressions"],0)


if __name__ == "__main__":
    unittest.main()
