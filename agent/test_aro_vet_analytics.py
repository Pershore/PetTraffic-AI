import unittest
from datetime import date

from aro_vet_analytics import format_number, metric_values, percent_change, report_rows


class AroVetAnalyticsTests(unittest.TestCase):
    def test_metric_values_extracts_first_aggregate_row(self):
        data = {
            "metricHeaders": [{"name": "activeUsers"}, {"name": "sessions"}],
            "rows": [{"metricValues": [{"value": "12"}, {"value": "18"}]}],
        }
        self.assertEqual(metric_values(data), {"activeUsers": 12.0, "sessions": 18.0})

    def test_empty_metric_rows_return_empty_mapping(self):
        self.assertEqual(metric_values({"metricHeaders": [], "rows": []}), {})

    def test_number_format_uses_space_grouping(self):
        self.assertEqual(format_number(12345), "12 345")

    def test_percent_change_zero_baseline(self):
        self.assertEqual(percent_change(0, 0), "nėra palyginimo bazės")
        self.assertIn("naujas augimas", percent_change(2, 0))

    def test_percent_change_regular(self):
        self.assertEqual(percent_change(15, 10), "+50.0 %")

    def test_report_rows_builds_ga4_request(self):
        class Response:
            ok = True
            def json(self):
                return {"rows": []}
        class Session:
            def __init__(self):
                self.body = None
            def post(self, url, json, timeout):
                self.body = json
                return Response()
        session = Session()
        report_rows(session, "https://example.test", date(2026, 11, 1),
                    date(2026, 11, 7), ["sessions"], ["pagePath"], 5, True)
        self.assertEqual(session.body["limit"], 5)
        self.assertEqual(session.body["metricAggregations"], ["TOTAL"])
        self.assertEqual(session.body["dimensions"], [{"name": "pagePath"}])


if __name__ == "__main__":
    unittest.main()
