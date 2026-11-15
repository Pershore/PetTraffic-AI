"""Protect permanent redirects for the ten retired Pet traffic articles."""

from pathlib import Path
import unittest

from agent.validate_site import REQUIRED_RETIRED_ARTICLE_REDIRECTS

ROOT = Path(__file__).resolve().parents[1]
REDIRECTS = ROOT / "site" / "_redirects"


class RetiredArticleRedirectTests(unittest.TestCase):
    def test_all_retired_article_urls_keep_their_permanent_redirects(self):
        rules = {}
        for line in REDIRECTS.read_text(encoding="utf-8").splitlines():
            parts = line.split()
            if len(parts) == 3 and not line.lstrip().startswith("#"):
                rules[parts[0]] = (parts[1], parts[2])

        for source, destination in REQUIRED_RETIRED_ARTICLE_REDIRECTS.items():
            with self.subTest(source=source):
                self.assertEqual(rules.get(source), (destination, "301"))

    def test_exactly_twenty_retired_article_paths_are_guarded(self):
        self.assertEqual(len(REQUIRED_RETIRED_ARTICLE_REDIRECTS), 20)


if __name__ == "__main__":
    unittest.main()
