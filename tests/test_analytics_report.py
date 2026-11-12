import unittest

from agent.analytics_report import channel_breakdown_status


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
