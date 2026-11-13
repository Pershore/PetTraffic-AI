import unittest
import threading
import time
from datetime import date

from agent.analytics_report import ga_rows, gsc_query, gsc_inspect_many


class ReadTimeout(Exception):
    pass


class ConnectTimeout(Exception):
    pass


class FakeResponse:
    ok = True
    status_code = 200

    def __init__(self, data=None):
        self.data = data if data is not None else {"rows": []}

    def json(self):
        return self.data


class FakeSession:
    def __init__(self, failures=()):
        self.failures = list(failures)
        self.calls = 0
        self.timeouts = []

    def post(self, url, json, timeout):
        self.calls += 1
        self.timeouts.append(timeout)
        if self.failures:
            failure = self.failures.pop(0)
            raise failure
        return FakeResponse()


class AnalyticsTimeoutPolicyTests(unittest.TestCase):
    def test_ga4_report_does_not_retry_a_read_timeout(self):
        session = FakeSession([ReadTimeout("slow GA4 report")])
        with self.assertRaises(ReadTimeout):
            ga_rows(
                session,
                "https://analyticsdata.googleapis.com/v1beta/properties/123:runReport",
                date(2026, 11, 1),
                date(2026, 11, 7),
                ["sessions"],
            )
        self.assertEqual(session.calls, 1)
        self.assertEqual(session.timeouts, [15])

    def test_search_console_query_keeps_one_read_timeout_retry(self):
        session = FakeSession([ReadTimeout("temporary GSC delay")])
        result = gsc_query(
            session,
            "https://searchconsole.googleapis.com/query",
            date(2026, 11, 1),
            date(2026, 11, 7),
        )
        self.assertEqual(session.calls, 2)
        self.assertEqual(session.timeouts, [25, 25])
        self.assertEqual(result, {"rows": []})

    def test_priority_url_inspections_run_concurrently_and_isolate_failures(self):
        lock = threading.Lock()
        state = {"active": 0, "max_active": 0}

        class InspectionSession:
            def post(self, url, json, timeout):
                with lock:
                    state["active"] += 1
                    state["max_active"] = max(state["max_active"], state["active"])
                try:
                    time.sleep(0.05)
                    if json["inspectionUrl"].endswith("/slow-failure"):
                        raise ReadTimeout("one URL inspection timed out")
                    return FakeResponse({
                        "inspectionResult": {
                            "indexStatusResult": {"verdict": "PASS"}
                        }
                    })
                finally:
                    with lock:
                        state["active"] -= 1

            def close(self):
                return None

        urls = [
            "https://pettraffic-ai.pages.dev/",
            "https://pettraffic-ai.pages.dev/articles/one",
            "https://pettraffic-ai.pages.dev/articles/two",
            "https://pettraffic-ai.pages.dev/articles/slow-failure",
            "https://pettraffic-ai.pages.dev/articles/four",
        ]
        results = gsc_inspect_many(InspectionSession, urls, "https://pettraffic-ai.pages.dev/")
        self.assertGreater(state["max_active"], 1)
        self.assertEqual(results[urls[0]]["inspectionResult"]["indexStatusResult"]["verdict"], "PASS")
        self.assertIsInstance(results[urls[3]], ReadTimeout)
        self.assertEqual(len(results), len(urls))

    def test_ga4_report_still_retries_connection_timeout(self):
        session = FakeSession([ConnectTimeout("temporary connection failure")])
        result = ga_rows(
            session,
            "https://analyticsdata.googleapis.com/v1beta/properties/123:runReport",
            date(2026, 11, 1),
            date(2026, 11, 7),
            ["sessions"],
        )
        self.assertEqual(session.calls, 2)
        self.assertEqual(result, {"rows": []})


if __name__ == "__main__":
    unittest.main()
