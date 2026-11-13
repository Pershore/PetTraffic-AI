import json
import tempfile
import unittest
from pathlib import Path
from agent.project_state import build_state, persist_state, render_markdown


class ProjectStateTests(unittest.TestCase):
    def control(self, results):
        return {"generated_at": "2026-11-13T10:45:00+00:00", "needs_attention": False, "results": results}

    def test_problem_takes_priority_and_becomes_next_action(self):
        state = build_state(self.control([
            {"name": "Analytics", "state": "success", "detail": "OK"},
            {"name": "Worker", "state": "failure", "detail": "D1 unavailable"},
        ]), {"recommendations": []}, "run-1", "abc123")
        self.assertEqual(state["overall_status"], "needs_attention")
        self.assertIn("Worker", state["next_action"])
        self.assertEqual(len(state["problems"]), 1)

    def test_agent_memory_status_is_preserved(self):
        agent = {"name": "AI agentai + control-core atmintis", "state": "success", "detail": "Atmintis išsaugota"}
        state = build_state(self.control([agent]), {"recommendations": [
            {"id": "r1", "priority": "medium", "title": "Review", "next_action": "Inspect"}
        ]}, "run-2", "def456")
        self.assertEqual(state["ai_agent_memory_check"]["state"], "success")
        self.assertEqual(state["overall_status"], "review_recommendations")

    def test_pending_check_does_not_become_success(self):
        state = build_state(self.control([
            {"name": "Lighthouse", "state": "waiting", "detail": "Not due"}
        ]), {"recommendations": []}, "run-3", "abc")
        self.assertEqual(state["overall_status"], "in_progress")
        self.assertEqual(len(state["pending_checks"]), 1)
        self.assertEqual(state["verified_processes"], [])

    def test_missing_results_are_rejected(self):
        with self.assertRaises(ValueError):
            build_state({"generated_at": "2026-11-13T10:00:00Z"}, {}, "run-4", "abc")

    def test_persists_daily_history_and_latest_recovery_files_idempotently(self):
        state = build_state(self.control([
            {"name": "Analytics", "state": "success", "detail": "OK"}
        ]), {"recommendations": []}, "run-5", "abc")
        with tempfile.TemporaryDirectory() as directory:
            history, latest_json, latest_md = persist_state(state, Path(directory))
            persist_state(state, Path(directory))
            data = json.loads(history.read_text(encoding="utf-8"))
            self.assertEqual(len(data["snapshots"]), 1)
            self.assertTrue(latest_json.exists())
            self.assertIn("Kitas veiksmas", latest_md.read_text(encoding="utf-8"))

    def test_markdown_contains_safety_boundaries(self):
        state = build_state(self.control([]), {"recommendations": []}, "run-6", "abc")
        markdown = render_markdown(state)
        self.assertIn("ARO Vet", markdown)
        self.assertIn("nepublikuoti", markdown)


if __name__ == "__main__":
    unittest.main()
