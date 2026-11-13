import json
import tempfile
import unittest
from pathlib import Path

from agent.analytics_history import parse_report, store_snapshot
from agent.analytics_report import api_post


REPORT = """# Pet traffic – lankomumo ataskaita
GA4 laikotarpis: 2026-11-05 – 2026-11-11

## Pagrindiniai rodikliai (GA4)
| Rodiklis | Paskutinės 7 d. | Pokytis |
|---|---:|---:|
| Aktyvūs naudotojai | 7 | +1 |
| Nauji naudotojai | 6 | +2 |
| Sesijos / apsilankymai | 14 | +3 |
| Puslapių peržiūros | 67 | +4 |
Organinės paieškos sesijos: **3**

## Google paieška (Search Console)
Laikotarpis: 2026-11-03 – 2026-11-09
| Rodiklis | Paskutinės 7 d. | Pokytis |
|---|---:|---:|
| Paieškos parodymai | 2502 | +100 |
| Paspaudimai | 123 | +5 |
| CTR | 4.9% | +0.2 |
| Vidutinė pozicija | 10.7 | -1 |

### Svetainės žemėlapis (Search Console)
- Būsena: **pateiktas** (https://pettraffic-ai.pages.dev/sitemap.xml)
- Paskutinį kartą pateiktas: 2026-11-12T08:00:00Z
- Google paskutinį kartą atsisiuntė: 2026-11-12T08:10:00Z
- URL pateikta / indeksuota: 7 / 4
- Laukia apdorojimo: ne

### Google indekso būklė (svarbiausi puslapiai)
| Puslapis | Būsena | Google paaiškinimas | Robots.txt | Indeksavimas | Paskutinis tikrinimas |
|---|---|---|---|---|---|
| / | PASS | URL is on Google | ALLOWED | INDEXED | 2026-11-11T10:00:00Z |
| /articles/example.html | FAIL | Crawled - currently not indexed | ALLOWED | NOT_INDEXED | 2026-11-11T10:05:00Z |

## Mokama reklama
"""


class AnalyticsHistoryTests(unittest.TestCase):
    def test_extracts_only_aggregate_metrics(self):
        item = parse_report(REPORT, "run-1", "2026-11-12T08:00:00Z")
        self.assertEqual(item["ga4_status"], "available")
        self.assertEqual(item["metrics"]["active_users"], 7)
        self.assertEqual(item["metrics"]["page_views"], 67)
        self.assertEqual(item["metrics"]["search_impressions"], 2502)
        self.assertEqual(item["metrics"]["search_clicks"], 123)
        self.assertAlmostEqual(item["metrics"]["search_ctr"], 0.049)
        self.assertEqual(item["metrics"]["organic_sessions_verified"], 3)
        self.assertEqual(item["search_console_details"]["sitemap"]["status"], "submitted")
        self.assertEqual(item["search_console_details"]["sitemap"]["submitted_urls"], 7)
        self.assertEqual(item["search_console_details"]["sitemap"]["indexed_urls"], 4)
        self.assertEqual(len(item["search_console_details"]["priority_url_inspections"]), 2)
        self.assertEqual(item["search_console_details"]["priority_url_inspections"][1]["indexing_state"], "NOT_INDEXED")
        self.assertNotIn("query", json.dumps(item).lower())

    def test_marks_missing_metrics_as_null(self):
        item = parse_report("# Pet traffic\nBūsena: neprijungta", "run-2", "2026-11-12T08:00:00Z")
        self.assertEqual(item["ga4_status"], "not_connected")
        self.assertIsNone(item["metrics"]["sessions"])
        self.assertEqual(item["search_console_details"]["sitemap"]["status"], "unknown")
        self.assertEqual(item["search_console_details"]["priority_url_inspections"], [])

    def test_records_independent_ga4_and_search_console_statuses(self):
        partial = """# Pet traffic
GA4 laikotarpis: 2026-11-05 – 2026-11-11

## Pagrindiniai rodikliai (GA4)

GA4 duomenų gauti nepavyko; Search Console bus tikrinama atskirai.
Techninė priežastis: ReadTimeout: timed out

## Google paieška (Search Console)

Laikotarpis: 2026-11-03 – 2026-11-09

| Rodiklis | Paskutinės 7 d. | Pokytis |
|---|---:|---:|
| Paieškos parodymai | 120 | +10 |
| Paspaudimai | 8 | +2 |
"""
        item = parse_report(partial, "partial-run", "2026-11-13T08:00:00Z")
        self.assertEqual(item["ga4_status"], "unavailable")
        self.assertEqual(item["search_console_status"], "available")
        self.assertIsNone(item["metrics"]["sessions"])
        self.assertEqual(item["metrics"]["search_impressions"], 120)
        self.assertEqual(item["metrics"]["search_clicks"], 8)

    def test_records_ga4_when_search_console_is_unavailable(self):
        partial = """# Pet traffic
GA4 laikotarpis: 2026-11-05 – 2026-11-11

## Pagrindiniai rodikliai (GA4)
| Rodiklis | Paskutinės 7 d. | Pokytis |
|---|---:|---:|
| Sesijos / apsilankymai | 14 | +3 |

## Google paieška (Search Console)

Duomenų gauti nepavyko. GA4 ataskaita pateikta atskirai.
"""
        item = parse_report(partial, "partial-run-2", "2026-11-13T08:00:00Z")
        self.assertEqual(item["ga4_status"], "available")
        self.assertEqual(item["search_console_status"], "unavailable")
        self.assertEqual(item["metrics"]["sessions"], 14)
        self.assertIsNone(item["metrics"]["search_clicks"])

    def test_stores_and_deduplicates_run(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            item = parse_report(REPORT, "run-1", "2026-11-12T08:00:00Z")
            path = store_snapshot(item, root)
            store_snapshot(item, root)
            saved = json.loads(path.read_text(encoding="utf-8"))
            self.assertEqual(len(saved["snapshots"]), 1)
            self.assertEqual(path.name, "2026-11-12.json")



class ReadTimeout(Exception):
    pass


class FakeResponse:
    def __init__(self, status_code, payload=None, text=""):
        self.status_code = status_code
        self.ok = 200 <= status_code < 300
        self._payload = payload or {}
        self.text = text

    def json(self):
        return self._payload


class FakeSession:
    def __init__(self, outcomes):
        self.outcomes = list(outcomes)
        self.calls = 0

    def post(self, url, json, timeout):
        self.calls += 1
        outcome = self.outcomes.pop(0)
        if isinstance(outcome, Exception):
            raise outcome
        return outcome


class AnalyticsApiRetryTests(unittest.TestCase):
    def test_retries_one_transient_read_timeout(self):
        from unittest.mock import patch
        session = FakeSession([ReadTimeout("temporary timeout"), FakeResponse(200, {"ok": True})])
        with patch("agent.analytics_report.time.sleep") as sleep:
            result = api_post(session, "https://example.test", {"query": 1})
        self.assertEqual(result, {"ok": True})
        self.assertEqual(session.calls, 2)
        sleep.assert_called_once_with(3)

    def test_retries_one_transient_server_error(self):
        from unittest.mock import patch
        session = FakeSession([FakeResponse(503, text="temporarily unavailable"), FakeResponse(200, {"rows": []})])
        with patch("agent.analytics_report.time.sleep") as sleep:
            result = api_post(session, "https://example.test", {"query": 1})
        self.assertEqual(result, {"rows": []})
        self.assertEqual(session.calls, 2)
        sleep.assert_called_once_with(3)

    def test_does_not_retry_permission_errors(self):
        from unittest.mock import patch
        session = FakeSession([FakeResponse(403, text="forbidden"), FakeResponse(200, {"ok": True})])
        with patch("agent.analytics_report.time.sleep") as sleep:
            with self.assertRaisesRegex(RuntimeError, "Google API HTTP 403"):
                api_post(session, "https://example.test", {"query": 1})
        self.assertEqual(session.calls, 1)
        sleep.assert_not_called()


if __name__ == "__main__":
    unittest.main()
