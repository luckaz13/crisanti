import json
import unittest
from pathlib import Path

from bs4 import BeautifulSoup

from tests.css_helpers import css_rule


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

    def test_critica_inherits_black_card_palette(self):
        css = (ROOT / "css/style.css").read_text(encoding="utf-8")
        self.assertNotIn("#critica .literatura-card {\n  background: #D4B38A", css)
        self.assertIn("background: #201E1C;", css_rule(css, ".literatura-card"))
        self.assertIn("color: #FFFFFF", css_rule(css, ".literatura-card h4,\n.literatura-card h3"))
        self.assertIn(
            "color: #F7F4EE",
            css_rule(css, ".literatura-card p,\n.literatura-excerpt,\n.literatura-full p"),
        )

    def test_critica_body_copy_meets_wcag_aa_contrast(self):
        def relative_luminance(hex_color):
            channels = [int(hex_color[i : i + 2], 16) / 255 for i in (1, 3, 5)]
            linear = [c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4 for c in channels]
            return 0.2126 * linear[0] + 0.7152 * linear[1] + 0.0722 * linear[2]

        foreground = relative_luminance("#F7F4EE")
        background = relative_luminance("#201E1C")
        contrast = (foreground + 0.05) / (background + 0.05)

        self.assertGreaterEqual(contrast, 4.5)

    def test_every_critica_article_has_pt_editorial_copy(self):
        data = json.loads(
            (ROOT / "data/acervo/editorial-literatura-critica.json").read_text(
                encoding="utf-8"
            )
        )
        soup = BeautifulSoup(
            (ROOT / "es/index.html").read_text(encoding="utf-8"), "html.parser"
        )
        ids = {article.get("id") for article in soup.select("#critica article[id]")}

        self.assertEqual(ids, set(data["articles"]))


if __name__ == "__main__":
    unittest.main()
