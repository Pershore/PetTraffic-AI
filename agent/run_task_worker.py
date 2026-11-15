#!/usr/bin/env python3
"""Claim and execute one explicitly allow-listed, read-only Pet traffic task."""
from __future__ import annotations

import json
import os
from pathlib import Path
import re
import subprocess
import sys
from datetime import datetime, timezone
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_API_URL = "https://pettraffic-control-api.pauliusgrubliauskis.workers.dev"
AUDIENCE = "pettraffic-control-api"
AGENT = "technical-seo"
SITE_CHECK_TASK = "check_site"
SITE_CHECK_PAYLOAD = {"target": "public_site"}
TASK_ID_PATTERN = re.compile(r"^[0-9a-f]{8}-[0-9a-f]{4}-[1-8][0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$", re.I)


def api_url() -> str:
    return os.environ.get("PETTRAFFIC_CONTROL_API_URL", DEFAULT_API_URL).rstrip("/")


def request_oidc_token() -> str:
    request_url = os.environ.get("ACTIONS_ID_TOKEN_REQUEST_URL", "")
    request_secret = os.environ.get("ACTIONS_ID_TOKEN_REQUEST_TOKEN", "")
    if not request_url or not request_secret:
        raise RuntimeError("GitHub Actions OIDC token request is unavailable.")
    separator = "&" if "?" in request_url else "?"
    request = Request(
        request_url + separator + urlencode({"audience": AUDIENCE}),
        headers={"Authorization": "Bearer " + request_secret, "Accept": "application/json"},
    )
    with urlopen(request, timeout=20) as response:
        payload = json.loads(response.read().decode("utf-8"))
    token = payload.get("value")
    if not isinstance(token, str) or not token:
        raise RuntimeError("GitHub did not return an OIDC identity token.")
    return token


def post_json(path: str, payload: dict, token: str) -> dict:
    request = Request(
        api_url() + path,
        data=json.dumps(payload, separators=(",", ":")).encode("utf-8"),
        headers={
            "Authorization": "Bearer " + token,
            "Content-Type": "application/json",
            "Accept": "application/json",
            "User-Agent": "PetTraffic-ReadOnly-TaskRunner/1.0",
        },
        method="POST",
    )
    try:
        with urlopen(request, timeout=30) as response:
            data = json.loads(response.read().decode("utf-8"))
    except HTTPError as exc:
        raise RuntimeError(f"Control API rejected the task request (HTTP {exc.code}).") from None
    except (URLError, TimeoutError, OSError) as exc:
        raise RuntimeError(f"Control API request failed ({type(exc).__name__}).") from None
    if not isinstance(data, dict):
        raise RuntimeError("Control API returned an invalid response.")
    return data


def get_json(path: str, token: str) -> dict:
    request = Request(
        api_url() + path,
        headers={
            "Authorization": "Bearer " + token,
            "Accept": "application/json",
            "User-Agent": "PetTraffic-ReadOnly-TaskRunner/1.0",
        },
        method="GET",
    )
    try:
        with urlopen(request, timeout=30) as response:
            data = json.loads(response.read().decode("utf-8"))
    except HTTPError as exc:
        raise RuntimeError(f"Control API readback failed (HTTP {exc.code}).") from None
    except (URLError, TimeoutError, OSError) as exc:
        raise RuntimeError(f"Control API readback failed ({type(exc).__name__}).") from None
    if not isinstance(data, dict):
        raise RuntimeError("Control API returned an invalid readback response.")
    return data


def command_for_task(task: object) -> list[str]:
    """Map one exact task schema to a fixed script; never execute task-supplied commands."""
    if not isinstance(task, dict):
        raise ValueError("Claimed task is not an object.")
    if task.get("type") != SITE_CHECK_TASK or task.get("assigned_agent") != AGENT:
        raise ValueError("Claimed task is not an allow-listed site check.")
    if task.get("payload") != SITE_CHECK_PAYLOAD:
        raise ValueError("Claimed task payload is not the exact public-site check schema.")
    task_id = task.get("id")
    if not isinstance(task_id, str) or not TASK_ID_PATTERN.fullmatch(task_id):
        raise ValueError("Claimed task ID is invalid.")
    return [sys.executable, str(ROOT / "agent" / "check_live_site.py")]


def execute_task(task: dict) -> tuple[int, str]:
    command = command_for_task(task)
    try:
        completed = subprocess.run(
            command,
            cwd=ROOT,
            capture_output=True,
            text=True,
            timeout=600,
            check=False,
        )
        output = (completed.stdout + "\n" + completed.stderr).strip()
        return completed.returncode, output[-3000:]
    except subprocess.TimeoutExpired:
        return 124, "The read-only site check exceeded its 600-second execution limit."
    except OSError as exc:
        return 127, f"The fixed site-check script could not start ({type(exc).__name__})."


def main() -> int:
    try:
        claim_token = request_oidc_token()
        claim = post_json("/v1/tasks/claim", {"agent": AGENT}, claim_token)
        task = claim.get("task")
        if task is None:
            print("No queued read-only site-check task.")
            return 0
        task_id = task.get("id") if isinstance(task, dict) else None
        if not isinstance(task_id, str) or not TASK_ID_PATTERN.fullmatch(task_id):
            raise RuntimeError("The claimed task did not contain a valid task ID.")

        try:
            exit_code, summary = execute_task(task)
        except ValueError as exc:
            exit_code, summary = 2, str(exc)

        # Request a fresh short-lived token in case the bounded check took several minutes.
        completion_token = request_oidc_token()
        completed = post_json(
            f"/v1/tasks/{task_id}/complete",
            {
                "agent": AGENT,
                "status": "completed" if exit_code == 0 else "failed",
                "result": {
                    "exit_code": exit_code,
                    "summary": summary[:3000],
                    "completed_at": datetime.now(timezone.utc).isoformat(),
                },
            },
            completion_token,
        )
        if completed.get("accepted") is not True:
            raise RuntimeError("Control API did not confirm task completion.")

        # Verify that the completion record is independently readable from D1.
        readback_token = request_oidc_token()
        readback = get_json(f"/v1/tasks/{task_id}", readback_token)
        stored_task = readback.get("task")
        if not isinstance(stored_task, dict):
            raise RuntimeError("D1 readback did not return the completed task.")
        expected_status = "completed" if exit_code == 0 else "failed"
        stored_result = stored_task.get("result")
        if (
            stored_task.get("id") != task_id
            or stored_task.get("status") != expected_status
            or not isinstance(stored_result, dict)
            or stored_result.get("exit_code") != exit_code
        ):
            raise RuntimeError("D1 readback did not match the task completion result.")

        print(f"Read-only task {task_id} completed; D1 readback verified (exit code {exit_code}).")
        print(summary)
        return 0 if exit_code == 0 else 1
    except (HTTPError, URLError, TimeoutError, OSError, ValueError, RuntimeError, json.JSONDecodeError) as exc:
        print(f"Read-only task runner failed: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
