import unittest
from unittest.mock import Mock, call

from agent.analytics_connectivity import check_api, run_independent_checks


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
