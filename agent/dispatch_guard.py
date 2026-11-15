"""Validate the owner-only issue-comment command for a daily-suite fallback."""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

EXPECTED_ISSUE = 145
EXPECTED_USER = "Pershore"
EXPECTED_COMMAND = "/pettraffic-run-daily-suite"


def authorize_issue_comment(payload: Any) -> tuple[bool, str]:
    """Accept only a newly created exact command from the repository owner on issue #145."""
    if not isinstance(payload, dict) or payload.get("action") != "created":
        return False, "Ignored: event is not a newly created issue comment."

    issue = payload.get("issue")
    comment = payload.get("comment")
    if not isinstance(issue, dict) or not isinstance(comment, dict):
        return False, "Ignored: issue/comment payload is incomplete."

    if issue.get("number") != EXPECTED_ISSUE or "pull_request" in issue:
        return False, "Ignored: command is not on the designated issue."

    user = comment.get("user")
    if not isinstance(user, dict) or user.get("login") != EXPECTED_USER:
        return False, "Ignored: comment author is not the repository owner."

    if str(comment.get("body", "")).strip() != EXPECTED_COMMAND:
        return False, "Ignored: comment does not match the exact dispatch command."

    return True, "Authorized owner command; daily-suite dispatch may proceed."


def main() -> int:
    event_path = Path(os.environ["GITHUB_EVENT_PATH"])
    output_path = Path(os.environ["GITHUB_OUTPUT"])
    with event_path.open(encoding="utf-8") as stream:
        payload = json.load(stream)

    authorized, message = authorize_issue_comment(payload)
    with output_path.open("a", encoding="utf-8") as stream:
        stream.write(f"authorized={'true' if authorized else 'false'}\n")
    print(message)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
