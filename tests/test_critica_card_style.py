import re
import unittest
from pathlib import Path

from bs4 import BeautifulSoup


ROOT = Path(__file__).resolve().parents[1]


class CriticaCardStyleTests(unittest.TestCase):
    def test_bilingual_pages_share_the_critica_scope(self):
        for relative in ("index.html", "es/index.html"):
            with self.subTest(relative=relative):
                soup = BeautifulSoup(
                    (ROOT / relative).read_text(encoding="utf-8"), "html.parser"
                )
                critica = soup.find(id="critica")
                self.assertIsNotNone(critica)
                self.assertTrue(critica.select(".literatura-card"))

    def test_critica_cards_use_scoped_gold_surface_and_subtle_shadow(self):
        css = (ROOT / "css/style.css").read_text(encoding="utf-8")
        card_rule = re.search(r"#critica \.literatura-card\s*\{([^}]+)\}", css)
        self.assertIsNotNone(card_rule)
        declarations = card_rule.group(1)
        self.assertIn("background: #D4B38A;", declarations)
        self.assertIn("border: 1px solid rgba(26, 23, 20, 0.14);", declarations)
        self.assertIn(
            "box-shadow: 0 6px 18px rgba(26, 23, 20, 0.14);", declarations
        )

    def test_critica_card_copy_uses_dark_palette(self):
        css = (ROOT / "css/style.css").read_text(encoding="utf-8")
        self.assertIn("#critica .literatura-card h4", css)
        self.assertIn("#critica .literatura-card p", css)
        self.assertIn("color: #1A1714 !important;", css)


if __name__ == "__main__":
    unittest.main()
