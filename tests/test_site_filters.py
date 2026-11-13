import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CSS = (ROOT / "site" / "assets" / "style.css").read_text(encoding="utf-8")
SCRIPT = (ROOT / "site" / "assets" / "site.js").read_text(encoding="utf-8")


class ArticleFilterVisibilityTests(unittest.TestCase):
    def test_hidden_article_cards_are_removed_from_layout(self):
        self.assertRegex(
            CSS,
            r"\.article-card\[hidden\]\s*\{\s*display\s*:\s*none\s*!important\s*;?\s*\}",
        )

    def test_search_updates_card_visibility_and_result_count(self):
        self.assertIn("card.hidden = !visible;", SCRIPT)
        self.assertIn("if (noResults) noResults.hidden = visibleCount > 0;", SCRIPT)
        self.assertIn("'Rodoma ' + visibleCount + ' iš ' + articleCards.length + ' straipsnių.'", SCRIPT)


if __name__ == "__main__":
    unittest.main()
