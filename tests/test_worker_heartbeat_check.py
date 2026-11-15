import unittest
from datetime import datetime, timezone

from agent.worker_heartbeat_check import parse_health, wait_for_heartbeat


class WorkerHeartbeatCheckTests(unittest.TestCase):
    def payload(self, checked_at="2026-11-15T10:00:00Z"):
        return {
            "ok": True,
            "database": "connected",
            "control_core_schema": "connected",
            "heartbeat": {
                "checked_at": checked_at,
                "site_ok": True,
                "site_status": 200,
                "database_ok": True,
            },
        }

    def test_parse_health_returns_utc_timestamp(self):
        checked = parse_health(self.payload("2026-11-15T12:00:00+02:00"))
        self.assertEqual(checked, datetime(2026, 11, 15, 10, 0, tzinfo=timezone.utc))

    def test_rejects_disconnected_database(self):
        payload = self.payload()
        payload["database"] = "unavailable"
        with self.assertRaisesRegex(ValueError, "D1"):
            parse_health(payload)

    def test_rejects_failed_site_heartbeat(self):
        payload = self.payload()
        payload["heartbeat"]["site_ok"] = False
        with self.assertRaisesRegex(ValueError, "site"):
            parse_health(payload)

    def test_wait_returns_only_after_persisted_heartbeat_advances(self):
        values = iter([
            datetime(2026, 11, 15, 10, 0, tzinfo=timezone.utc),
            datetime(2026, 11, 15, 10, 15, tzinfo=timezone.utc),
        ])
        baseline, current = wait_for_heartbeat(
            "https://example.test/health",
            timeout_seconds=60,
            poll_seconds=30,
            fetcher=lambda _url: next(values),
            sleeper=lambda _seconds: None,
            clock=lambda: 0,
        )
        self.assertLess(baseline, current)

    def test_wait_times_out_if_heartbeat_does_not_advance(self):
        baseline = datetime(2026, 11, 15, 10, 0, tzinfo=timezone.utc)
        now = [0]
        def advance(seconds):
            now[0] += seconds
        with self.assertRaises(TimeoutError):
            wait_for_heartbeat(
                "https://example.test/health",
                timeout_seconds=30,
                poll_seconds=30,
                fetcher=lambda _url: baseline,
                sleeper=advance,
                clock=lambda: now[0],
            )


if __name__ == "__main__":
    unittest.main()
