import unittest

from analytics_report import delta, fmt_gsc, gsc_metric, metric_aggregation_total


class AnalyticsReportTests(unittest.TestCase):
    def test_search_console_empty_rows_are_missing_not_zero(self):
        self.assertIsNone(gsc_metric({"rows": []}, "impressions"))
        self.assertEqual(fmt_gsc(gsc_metric({"rows": []}, "impressions")), "Duomenų nėra")

    def test_search_console_explicit_zero_is_preserved(self):
        self.assertEqual(gsc_metric({"rows": [{"impressions": 0}]}, "impressions"), 0.0)
        self.assertEqual(fmt_gsc(gsc_metric({"rows": [{"impressions": 0}]}, "impressions")), "0")

    def test_search_console_metric_reads_aggregate_row(self):
        data = {"rows": [{"clicks": 3, "impressions": 12, "ctr": 0.25}]}
        self.assertEqual(gsc_metric(data, "clicks"), 3.0)
        self.assertEqual(gsc_metric(data, "ctr"), 0.25)

    def test_ga4_total_aggregation_is_read_from_totals(self):
        data = {
            "metricHeaders": [{"name": "sessions"}],
            "totals": [{"metricValues": [{"value": "14"}]}],
            "rows": [],
        }
        self.assertEqual(metric_aggregation_total(data, "sessions"), 14.0)

    def test_ga4_total_aggregation_reads_reserved_total_row(self):
        data = {
            "metricHeaders": [{"name": "sessions"}],
            "rows": [
                {"dimensionValues": [{"value": "Direct"}], "metricValues": [{"value": "13"}]},
                {"dimensionValues": [{"value": "RESERVED_TOTAL"}], "metricValues": [{"value": "14"}]},
            ],
        }
        self.assertEqual(metric_aggregation_total(data, "sessions"), 14.0)

    def test_ga4_total_aggregation_missing_is_none(self):
        self.assertIsNone(metric_aggregation_total({"rows": []}, "sessions"))

    def test_delta_handles_zero_baseline(self):
        self.assertEqual(delta(0, 0), "nėra palyginimo bazės")
        self.assertEqual(delta(4, 0), "naujas augimas (ankstesnis laikotarpis: 0)")


if __name__ == "__main__":
    unittest.main()
