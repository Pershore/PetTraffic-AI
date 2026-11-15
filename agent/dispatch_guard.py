"""Validate owner-only issue-comment commands for bounded Pet traffic workflows."""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

EXPECTED_ISSUE = 145
EXPECTED_USER = "Pershore"
EXPECTED_COMMAND = "/pettraffic-run-daily-suite"
COMMAND_ACTIONS = {
    "/pettraffic-run-daily-suite": "daily-suite",
    "/pettraffic-sync-latest": "sync-latest",
    "/pettraffic-run-control-center": "control-center",
    "/pettraffic-run-lighthouse": "lighthouse",
    "/pettraffic-run-site-check": "site-check",
    "/pettraffic-run-connectivity": "connectivity",
    "/pettraffic-run-worker-diagnostics": "worker-diagnostics",
    "/pettraffic-enqueue-site-check": "task-check-site",
}


def validate_issue_comment(payload: Any) -> tuple[bool, str, str | None]:
    """Accept only exact commands from the repository owner on issue #145."""
    if not isinstance(payload, dict) or payload.get("action") != "created":
        return False, "Ignored: event is not a newly created issue comment.", None

    issue = payload.get("issue")
    comment = payload.get("comment")
    if not isinstance(issue, dict) or not isinstance(comment, dict):
        return False, "Ignored: issue/comment payload is incomplete.", None

    if issue.get("number") != EXPECTED_ISSUE or "pull_request" in issue:
        return False, "Ignored: command is not on the designated issue.", None

    user = comment.get("user")
    if not isinstance(user, dict) or user.get("login") != EXPECTED_USER:
        return False, "Ignored: comment author is not the repository owner.", None

    command = str(comment.get("body", "")).strip()
    action = COMMAND_ACTIONS.get(command)
    if action is None:
        return False, "Ignored: comment does not match an allowed exact command.", None

    return True, "Authorized owner command; bounded workflow dispatch may proceed.", action


def authorize_issue_comment(payload: Any) -> tuple[bool, str]:
    """Backward-compatible authorization result used by simple callers."""
    authorized, message, _ = validate_issue_comment(payload)
    return authorized, message


def main() -> int:
    event_path = Path(os.environ["GITHUB_EVENT_PATH"])
    output_path = Path(os.environ["GITHUB_OUTPUT"])
    with event_path.open(encoding="utf-8") as stream:
        payload = json.load(stream)

    authorized, message, action = validate_issue_comment(payload)
    with output_path.open("a", encoding="utf-8") as stream:
        stream.write(f"authorized={'true' if authorized else 'false'}\n")
        stream.write(f"action={action or ''}\n")
    print(message)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
