import unittest

from agent.dispatch_guard import (
    COMMAND_ACTIONS,
    EXPECTED_COMMAND,
    authorize_issue_comment,
    validate_issue_comment,
)


def event(*, user="Pershore", issue=145, action="created", body=EXPECTED_COMMAND, pull_request=False):
    issue_payload = {"number": issue}
    if pull_request:
        issue_payload["pull_request"] = {"url": "https://api.github.com/repos/Pershore/PetTraffic-AI/pulls/1"}
    return {
        "action": action,
        "issue": issue_payload,
        "comment": {"body": body, "user": {"login": user}},
    }


class DispatchGuardTests(unittest.TestCase):
    def test_accepts_exact_owner_command_on_central_issue(self):
        allowed, _ = authorize_issue_comment(event())
        self.assertTrue(allowed)

    def test_maps_only_the_allowlisted_bounded_commands(self):
        expected = {
            "/pettraffic-run-daily-suite": "daily-suite",
            "/pettraffic-sync-latest": "sync-latest",
            "/pettraffic-run-control-center": "control-center",
            "/pettraffic-run-lighthouse": "lighthouse",
            "/pettraffic-run-site-check": "site-check",
            "/pettraffic-run-connectivity": "connectivity",
            "/pettraffic-run-worker-diagnostics": "worker-diagnostics",
            "/pettraffic-enqueue-site-check": "task-check-site",
        }
        self.assertEqual(COMMAND_ACTIONS, expected)
        for command, action in expected.items():
            with self.subTest(command=command):
                allowed, _, selected = validate_issue_comment(event(body=command))
                self.assertTrue(allowed)
                self.assertEqual(selected, action)

    def test_rejects_non_owner(self):
        allowed, _ = authorize_issue_comment(event(user="someone-else"))
        self.assertFalse(allowed)

    def test_rejects_other_issue(self):
        allowed, _ = authorize_issue_comment(event(issue=146))
        self.assertFalse(allowed)

    def test_rejects_pull_request_comment(self):
        allowed, _ = authorize_issue_comment(event(pull_request=True))
        self.assertFalse(allowed)

    def test_rejects_edited_or_deleted_comment(self):
        allowed, _ = authorize_issue_comment(event(action="edited"))
        self.assertFalse(allowed)

    def test_rejects_extra_text_and_near_matches(self):
        for body in (EXPECTED_COMMAND + " please", EXPECTED_COMMAND.upper(), "/run-daily-suite", "", "/pettraffic-run-worker"):
            with self.subTest(body=body):
                allowed, _ = authorize_issue_comment(event(body=body))
                self.assertFalse(allowed)

    def test_rejects_incomplete_payload(self):
        for payload in (None, {}, {"action": "created"}, {"action": "created", "issue": {}, "comment": {}}):
            with self.subTest(payload=payload):
                allowed, _ = authorize_issue_comment(payload)
                self.assertFalse(allowed)


if __name__ == "__main__":
    unittest.main()
