from pathlib import Path
import re
import unittest

ROOT = Path(__file__).resolve().parents[1]
POLICY = "ARO Vet, pharmacy sections, product cards, affiliate links, advertising blocks, and ARO Vet-specific tracking must never appear in Pet traffic."

class CurrentProjectPolicyTests(unittest.TestCase):
    def test_canonical_project_instructions_prohibit_aro_vet_content(self):
        for relative in (
            "AGENTS.md",
            "docs/SESSION_START.md",
            "docs/PROJECT_MEMORY.md",
            "agent/EDITORIAL_STYLE.md",
            "agent/GROWTH_STRATEGY.md",
        ):
            with self.subTest(path=relative):
                self.assertIn(POLICY, (ROOT / relative).read_text(encoding="utf-8"))

    def test_public_site_contains_no_aro_vet_or_affiliate_elements(self):
        forbidden = re.compile(r"aro\\s*vet|arovetvaistine|affiliate", re.IGNORECASE)
        for path in (ROOT / "site").rglob("*"):
            if not path.is_file() or path.suffix.lower() not in {".html", ".js", ".css", ".xml", ".txt", ".svg"}:
                continue
            with self.subTest(path=str(path.relative_to(ROOT))):
                self.assertIsNone(forbidden.search(path.read_text(encoding="utf-8")))

if __name__ == "__main__":
    unittest.main()
