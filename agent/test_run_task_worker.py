"""Unit tests for the bounded read-only task runner."""
from __future__ import annotations

import sys
import unittest
from pathlib import Path

from run_task_worker import AGENT, SITE_CHECK_PAYLOAD, command_for_task

TASK_ID = "11111111-1111-4111-8111-111111111111"


class TaskCommandTests(unittest.TestCase):
    def test_public_site_check_maps_to_fixed_script(self) -> None:
        command = command_for_task({
            "id": TASK_ID,
            "type": "check_site",
            "assigned_agent": AGENT,
            "payload": SITE_CHECK_PAYLOAD,
        })
        self.assertEqual(command[0], sys.executable)
        self.assertEqual(Path(command[1]).name, "check_live_site.py")

    def test_task_payload_cannot_supply_an_arbitrary_command(self) -> None:
        with self.assertRaises(ValueError):
            command_for_task({
                "id": TASK_ID,
                "type": "check_site",
                "assigned_agent": AGENT,
                "payload": {"target": "public_site", "command": "rm -rf /"},
            })

    def test_other_task_types_are_rejected(self) -> None:
        with self.assertRaises(ValueError):
            command_for_task({
                "id": TASK_ID,
                "type": "review_content_facts",
                "assigned_agent": "content-review",
                "payload": {"target": "public_site"},
            })

    def test_invalid_task_id_is_rejected(self) -> None:
        with self.assertRaises(ValueError):
            command_for_task({
                "id": "../../etc/passwd",
                "type": "check_site",
                "assigned_agent": AGENT,
                "payload": SITE_CHECK_PAYLOAD,
            })


if __name__ == "__main__":
    unittest.main()
