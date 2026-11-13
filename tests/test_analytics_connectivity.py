import unittest
from unittest.mock import Mock, call

from agent.analytics_connectivity import check_api, check_ga4_grpc, check_ga4_realtime_grpc, check_ga4_web_stream, run_independent_checks


class ConnectivityCheckTests(unittest.TestCase):
    def test_successful_api_response(self):
        response = Mock(ok=True)
        response.json.return_value = {"rows": []}
        session = Mock()
        session.post.return_value = response

        ok, detail = check_api(session, "GA4", "https://example.test", {"metrics": []})

        self.assertTrue(ok)
        self.assertEqual(detail, "API request succeeded")
        session.post.assert_called_once()

    def test_http_error_is_reported_without_raising(self):
        response = Mock(ok=False, status_code=403, text="forbidden")
        session = Mock()
        session.post.return_value = response

        ok, detail = check_api(session, "Search Console", "https://example.test", {})

        self.assertFalse(ok)
        self.assertIn("HTTP 403", detail)

    def test_timeout_is_reported_without_raising(self):
        session = Mock()
        session.post.side_effect = TimeoutError("read timed out")

        ok, detail = check_api(session, "GA4", "https://example.test", {})

        self.assertFalse(ok)
        self.assertIn("TimeoutError", detail)

    def test_grpc_probe_uses_one_day_report_and_closes_client(self):
        response = Mock(row_count=1)
        client = Mock()
        client.run_report.return_value = response
        factory = Mock(return_value=client)

        from datetime import date
        ok, detail = check_ga4_grpc(factory, object(), "12345", date(2026, 11, 12), date(2026, 11, 12))

        self.assertTrue(ok)
        self.assertIn("row_count=1", detail)
        self.assertEqual(factory.call_args.kwargs["transport"], "grpc")
        self.assertEqual(client.run_report.call_args.kwargs["timeout"], 20)
        client.close.assert_called_once()

    def test_grpc_probe_reports_timeout_without_raising(self):
        from datetime import date
        client = Mock()
        client.run_report.side_effect = TimeoutError("gRPC timed out")
        factory = Mock(return_value=client)

        ok, detail = check_ga4_grpc(factory, object(), "12345", date(2026, 11, 12), date(2026, 11, 12))

        self.assertFalse(ok)
        self.assertIn("TimeoutError", detail)
        client.close.assert_called_once()

    def test_realtime_grpc_probe_calls_realtime_endpoint(self):
        from datetime import date
        client = Mock()
        client.run_realtime_report.return_value = Mock(row_count=1)
        factory = Mock(return_value=client)

        ok, detail = check_ga4_realtime_grpc(factory, object(), "12345")

        self.assertTrue(ok)
        self.assertIn("row_count=1", detail)
        self.assertEqual(factory.call_args.kwargs["transport"], "grpc")
        client.run_realtime_report.assert_called_once()
        self.assertEqual(client.run_realtime_report.call_args.kwargs["timeout"], 20)
        client.close.assert_called_once()

    def test_ga4_web_stream_matches_site_measurement_id(self):
        response = Mock(ok=True)
        response.json.return_value = {
            "dataStreams": [{
                "type": "WEB_DATA_STREAM",
                "webStreamData": {"measurementId": "G-19VR75D8BG"},
            }]
        }
        session = Mock()
        session.get.return_value = response

        ok, detail = check_ga4_web_stream(
            session, "https://admin.test/dataStreams", "G-19VR75D8BG"
        )

        self.assertTrue(ok)
        self.assertIn("matches", detail)

    def test_ga4_web_stream_detects_measurement_id_mismatch(self):
        response = Mock(ok=True)
        response.json.return_value = {
            "dataStreams": [{
                "type": "WEB_DATA_STREAM",
                "webStreamData": {"measurementId": "G-OTHER"},
            }]
        }
        session = Mock()
        session.get.return_value = response

        ok, detail = check_ga4_web_stream(
            session, "https://admin.test/dataStreams", "G-19VR75D8BG"
        )

        self.assertFalse(ok)
        self.assertIn("does not match", detail)

    def test_ga4_timeout_does_not_skip_search_console(self):
        success = Mock(ok=True)
        success.json.return_value = {"rows": []}
        session = Mock()
        session.post.side_effect = [TimeoutError("GA4 timed out"), success]

        results = run_independent_checks(
            session, "https://ga4.test", {}, "https://gsc.test", {}
        )

        self.assertFalse(results["GA4"][0])
        self.assertTrue(results["Search Console"][0])
        self.assertEqual(session.post.call_count, 2)
        self.assertEqual(
            [entry.args[0] for entry in session.post.call_args_list],
            ["https://ga4.test", "https://gsc.test"],
        )


if __name__ == "__main__":
    unittest.main()
