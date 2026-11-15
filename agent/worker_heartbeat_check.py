#!/usr/bin/env python3
"""Verify a scheduled Worker invocation through a newly persisted D1 heartbeat."""
from __future__ import annotations

import argparse
import json
import sys
import time
from datetime import datetime, timezone
from urllib.request import Request, urlopen


def parse_health(payload: object) -> datetime:
    if not isinstance(payload, dict) or payload.get("ok") is not True:
        raise ValueError("Worker health did not confirm a healthy service.")
    if payload.get("database") != "connected" or payload.get("control_core_schema") != "connected":
        raise ValueError("Worker health did not confirm D1 and Control Core connectivity.")
    heartbeat = payload.get("heartbeat")
    if not isinstance(heartbeat, dict) or not isinstance(heartbeat.get("checked_at"), str):
        raise ValueError("Worker health did not return a persisted heartbeat timestamp.")
    if heartbeat.get("site_ok") is not True or heartbeat.get("database_ok") is not True:
        raise ValueError("The latest scheduled heartbeat did not confirm site and database health.")
    try:
        checked_at = datetime.fromisoformat(heartbeat["checked_at"].replace("Z", "+00:00"))
    except ValueError as exc:
        raise ValueError("Worker returned an invalid heartbeat timestamp.") from exc
    if checked_at.tzinfo is None:
        checked_at = checked_at.replace(tzinfo=timezone.utc)
    return checked_at.astimezone(timezone.utc)


def fetch_heartbeat(url: str, timeout: int = 15) -> datetime:
    request = Request(
        url,
        headers={
            "Accept": "application/json",
            "User-Agent": "PetTraffic-Worker-Cron-Diagnostic/1.0",
        },
    )
    with urlopen(request, timeout=timeout) as response:
        if response.status != 200:
            raise ValueError(f"Worker health returned HTTP {response.status}.")
        payload = json.loads(response.read().decode("utf-8"))
    return parse_health(payload)


def wait_for_heartbeat(
    url: str,
    timeout_seconds: int = 1020,
    poll_seconds: int = 30,
    fetcher=fetch_heartbeat,
    sleeper=time.sleep,
    clock=time.monotonic,
) -> tuple[datetime, datetime]:
    if timeout_seconds < 1 or poll_seconds < 1:
        raise ValueError("Timeout and polling interval must be positive.")
    baseline = fetcher(url)
    deadline = clock() + timeout_seconds
    while True:
        remaining = deadline - clock()
        if remaining <= 0:
            raise TimeoutError("No new scheduled D1 heartbeat was observed within the capture window.")
        sleeper(min(poll_seconds, remaining))
        current = fetcher(url)
        if current > baseline:
            return baseline, current


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--url", required=True, help="Public Worker /health URL.")
    parser.add_argument("--timeout-seconds", type=int, default=1020)
    parser.add_argument("--poll-seconds", type=int, default=30)
    args = parser.parse_args(argv)
    try:
        baseline, current = wait_for_heartbeat(
            args.url,
            timeout_seconds=args.timeout_seconds,
            poll_seconds=args.poll_seconds,
        )
    except (OSError, ValueError, TimeoutError) as exc:
        print(f"Worker cron heartbeat verification failed: {exc}", file=sys.stderr)
        return 1
    print(
        "Scheduled Worker heartbeat advanced; D1, Control Core schema, "
        f"site and database are healthy ({baseline.isoformat()} -> {current.isoformat()})."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
