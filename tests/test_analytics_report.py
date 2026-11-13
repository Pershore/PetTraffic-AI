import unittest
from unittest.mock import Mock, patch


from agent.analytics_report import api_post, channel_breakdown_status


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


if __name__ == "__main__":
    unittest.main()
