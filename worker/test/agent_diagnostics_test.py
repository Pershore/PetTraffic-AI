from pathlib import Path
import json
import sys
import unittest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "worker" / "scripts"))

from agent_diagnostics import build_diagnostics, classify_gap, render_markdown, _assert_read_only_meta


class WorkerAgentDiagnosticsTests(unittest.TestCase):
    def test_d1_query_requires_explicit_zero_write_metadata(self):
        self.assertIsNone(_assert_read_only_meta({"rows_written": 0}))
        with self.assertRaises(RuntimeError):
            _assert_read_only_meta({"rows_written": 1})
        with self.assertRaises(RuntimeError):
            _assert_read_only_meta({})

    def test_workflow_is_manual_or_post_merge_and_read_only(self):
        workflow = (ROOT / ".github" / "workflows" / "worker-agent-diagnostics.yml").read_text(encoding="utf-8")
        self.assertIn("workflow_dispatch:", workflow)
        self.assertIn("push:", workflow)
        self.assertIn("permissions:\n  contents: read", workflow)
        self.assertNotIn("contents: write", workflow)
        self.assertNotIn("wrangler deploy", workflow.lower())
        self.assertIn("SELECT-only requests", workflow)

    def test_model_json_failures_are_classified_without_echoing_model_text(self):
        self.assertEqual(classify_gap("Model response was incomplete JSON; this specialist result was not used."), "model_output_incomplete_json")
        self.assertEqual(classify_gap("Model response was not valid JSON; this specialist result was not used."), "model_output_malformed_json")
        self.assertEqual(classify_gap("Model response did not contain required fields."), "model_output_missing_fields")

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
