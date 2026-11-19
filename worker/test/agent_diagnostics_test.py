from pathlib import Path
import json
import sys
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "worker" / "scripts"))

from agent_diagnostics import (
    build_diagnostics, classify_gap, render_markdown, _assert_read_only_meta,
    _load_source_events,
)


class WorkerAgentDiagnosticsTests(unittest.TestCase):
    def test_source_events_are_loaded_with_independent_kind_scoped_queries(self):
        calls = []
        sample = {
            "analytics_snapshot": [{"kind": "analytics_snapshot", "created_at": "2026-11-17T00:30:00Z", "run_id": "a1"}],
            "topic_snapshot": [{"kind": "topic_snapshot", "created_at": "2026-11-17T01:00:00Z", "run_id": "t1"}],
            "control_center_snapshot": [{"kind": "control_center_snapshot", "created_at": "2026-11-17T02:00:00Z", "run_id": "c1"}],
            "recommendation_snapshot": [{"kind": "recommendation_snapshot", "created_at": "2026-11-17T03:00:00Z", "run_id": "r1"}],
        }

        def fake_query(account, database, token, sql, params):
            calls.append((sql, params))
            return sample[params[0]]

        with patch("agent_diagnostics._query", side_effect=fake_query):
            events = _load_source_events("account", "database", "token", "2026-11-17")

        self.assertEqual(
            [params[0] for _, params in calls],
            ["analytics_snapshot", "topic_snapshot", "control_center_snapshot", "recommendation_snapshot"],
        )
        self.assertEqual([event["kind"] for event in events], [
            "analytics_snapshot", "topic_snapshot", "control_center_snapshot", "recommendation_snapshot"
        ])
        for sql, params in calls:
            self.assertIn("WHERE kind = ? AND created_at >= ? AND created_at < ?", sql)
            self.assertIn("ORDER BY created_at DESC LIMIT 100", sql)
            self.assertEqual(params[1], "2026-11-16T22:00:00+00:00")
            self.assertEqual(params[2], "2026-11-17T22:00:00+00:00")

    def test_source_event_counts_use_vilnius_calendar_date_not_utc_date_prefix(self):
        events = [
            {"kind": "analytics_snapshot", "created_at": "2026-11-16T22:30:00Z", "run_id": "analytics-after-midnight-lt"},
            {"kind": "topic_snapshot", "created_at": "2026-11-16T21:30:00Z", "run_id": "topic-before-midnight-lt"},
            {"kind": "control_center_snapshot", "created_at": "2026-11-17T20:30:00Z", "run_id": "control-today"},
            {"kind": "recommendation_snapshot", "created_at": "2026-11-17T22:30:00Z", "run_id": "recommendation-next-day-lt"},
        ]
        data = build_diagnostics("2026-11-17", None, None, None, events)
        self.assertEqual(data["source_events"]["analytics_snapshot"]["count_on_run_date"], 1)
        self.assertEqual(data["source_events"]["topic_snapshot"]["count_on_run_date"], 0)
        self.assertEqual(data["source_events"]["control_center_snapshot"]["count_on_run_date"], 1)
        self.assertEqual(data["source_events"]["recommendation_snapshot"]["count_on_run_date"], 0)

    def test_d1_query_requires_explicit_zero_write_metadata(self):
        self.assertIsNone(_assert_read_only_meta({"rows_written": 0}))
        with self.assertRaises(RuntimeError):
            _assert_read_only_meta({"rows_written": 1})
        with self.assertRaises(RuntimeError):
            _assert_read_only_meta({})

    def test_workflow_is_manual_or_post_sync_and_read_only(self):
        workflow = (ROOT / ".github" / "workflows" / "worker-agent-diagnostics.yml").read_text(encoding="utf-8")
        self.assertIn("workflow_dispatch:", workflow)
        self.assertIn('workflows: ["Sync PetTraffic snapshots to central API"]', workflow)
        self.assertNotIn('workflows: ["Pet traffic central control center"]', workflow)
        self.assertIn("types: [completed]", workflow)
        self.assertIn("branches: [main]", workflow)
        self.assertIn("github.event.workflow_run.conclusion == 'success'", workflow)
        self.assertIn("github.event.workflow_run.event == 'workflow_run'", workflow)
        self.assertIn("push:", workflow)
        self.assertIn("permissions:\n  contents: read", workflow)
        self.assertNotIn("contents: write", workflow)
        self.assertNotIn("wrangler deploy", workflow.lower())
        self.assertIn("SELECT-only requests", workflow)

    def test_model_json_failures_are_classified_without_echoing_model_text(self):
        self.assertEqual(classify_gap("Model response was incomplete JSON; this specialist result was not used."), "model_output_incomplete_json")
        self.assertEqual(classify_gap("Model response was not valid JSON; this specialist result was not used."), "model_output_malformed_json")
        self.assertEqual(classify_gap("Model response did not contain required fields."), "model_output_missing_fields")
        self.assertEqual(classify_gap("Model JSON did not contain the required status, findings, recommendations and evidence_gaps fields."), "model_output_missing_fields")

    def test_missing_and_no_data_gaps_match_worker_health_category(self):
        self.assertEqual(classify_gap("Missing metrics prevent a verified conclusion."), "insufficient_evidence")
        self.assertEqual(classify_gap("No data was available for the requested comparison."), "insufficient_evidence")

    def test_generic_english_evidence_and_source_gaps_match_worker_health_category(self):
        self.assertEqual(
            classify_gap("The source does not contain enough verifiable material for this conclusion."),
            "insufficient_evidence",
        )
        self.assertEqual(
            classify_gap("There is no evidence to verify the recommendation."),
            "insufficient_evidence",
        )

    def test_lithuanian_evidence_gaps_are_classified_without_echoing_text(self):
        cases = {
            "Nepakanka patikimų įrodymų šiai išvadai.": "insufficient_evidence",
            "Trūksta Search Console paieškos užklausų duomenų.": "search_console_data_missing",
            "Nėra patikimų paieškos apimčių pagal raktinius žodžius.": "search_volume_not_available",
            "Nepavyko pasiekti nurodyto šaltinio.": "source_unavailable",
            "Modelio JSON nepateikė privalomų laukų.": "model_output_missing_fields",
        }
        for message, expected in cases.items():
            with self.subTest(message=message):
                self.assertEqual(classify_gap(message), expected)
                self.assertNotEqual(classify_gap(message), message)

    def test_evidence_gaps_become_codes_and_free_text_is_never_returned(self):
        report = {
            "specialists": {
                "analytics": {"status": "needs_evidence", "evidence_gaps": ["No Search Console query rows were available for this period."]},
                "topics": {"status": "reviewed", "evidence_gaps": []},
                "technical-seo": {"status": "needs_evidence", "evidence_gaps": ["The control_center_snapshot source was unavailable."]},
                "content-review": {"status": "invalid_json", "evidence_gaps": ["Model response was incomplete JSON; this specialist result was not used."]},
            },
            "coordinator": {"status": "fallback", "evidence_gaps": ["Not enough verified evidence was available."], "recommendations": ["Do not publish without review."]},
            "data_quality": {"degraded_specialist_count": 1, "invalid_event_payload_count": 0},
        }
        data = build_diagnostics(
            "2026-11-16",
            {"status": "completed", "ai_calls": 5, "started_at": "2026-11-16T11:20:24.330Z", "completed_at": "2026-11-16T11:20:31.412Z", "report_json": json.dumps(report)},
            {"status": "needs_evidence", "created_at": "2026-11-16T11:20:31.068Z", "decision_json": json.dumps({"evidence_gaps": ["No Search Console query rows were available for this period."], "recommendations": ["Review search visibility."]})},
            {"updated_at": "2026-11-16T11:20:31.068Z", "value_json": json.dumps({"last_run_date": "2026-11-16", "last_status": "needs_evidence", "evidence_gaps": ["Not enough verified evidence was available."]})},
            [{"kind": "analytics_snapshot", "created_at": "2026-11-16T10:30:15Z", "run_id": "43849430626"}],
        )
        self.assertEqual(data["agent_run"]["status"], "completed")
        self.assertEqual(data["agent_run"]["ai_calls"], 5)
        self.assertEqual(data["specialists"]["content-review"]["evidence_gap_codes"], ["model_output_incomplete_json"])
        self.assertEqual(data["specialists"]["analytics"]["evidence_gap_codes"], ["search_console_data_missing"])
        self.assertEqual(data["specialists"]["technical-seo"]["evidence_gap_codes"], ["control_center_snapshot_missing"])
        self.assertEqual(data["source_events"]["analytics_snapshot"]["count_on_run_date"], 1)
        serialized = json.dumps(data, ensure_ascii=False)
        for private_text in ("Model response was incomplete JSON", "No Search Console query rows", "Do not publish"):
            self.assertNotIn(private_text, serialized)

    def test_missing_or_malformed_reports_remain_explicitly_unknown(self):
        data = build_diagnostics("2026-11-16", None, None, None, [])
        self.assertFalse(data["agent_run"]["present"])
        self.assertEqual(data["agent_run"]["report_json_status"], "missing_or_invalid")
        self.assertEqual(data["specialists"]["content-review"]["status"], "missing")
        self.assertFalse(data["control_core"]["present"])
        self.assertFalse(data["memory"]["present"])

    def test_diagnostic_markdown_contains_codes_and_metadata_only(self):
        data = build_diagnostics("2026-11-16", {"status": "completed", "ai_calls": 5, "report_json": "{}"}, None, None, [])
        text = render_markdown(data)
        self.assertIn("content-review", text)
        self.assertIn("specialist_report_missing", text)
        self.assertNotIn("report_json", text)
        self.assertNotIn("Model response was incomplete JSON", text)


if __name__ == "__main__":
    unittest.main()
