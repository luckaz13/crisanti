import re
import unittest
from pathlib import Path

from bs4 import BeautifulSoup


ROOT = Path(__file__).resolve().parents[1]
ASSET_SUFFIX = "img/images/La Escultura/Addis Abbaba/02.jpg"


class ContactKiteImageTests(unittest.TestCase):
    def test_bilingual_contact_sections_use_selected_kite(self):
        for relative in ("index.html", "es/index.html"):
            with self.subTest(relative=relative):
                soup = BeautifulSoup(
                    (ROOT / relative).read_text(encoding="utf-8"), "html.parser"
                )
                contact = soup.find(id="contato")
                image = contact.select_one(".contato-img")
                self.assertTrue(image["src"].endswith(ASSET_SUFFIX))
                self.assertEqual("", image.get("alt"))
                self.assertEqual("true", image.parent.get("aria-hidden"))

    def test_contact_image_preserves_the_complete_artwork(self):
        css = (ROOT / "css/style.css").read_text(encoding="utf-8")
        rule = re.search(r"\.contato-img\s*\{([^}]+)\}", css)
        self.assertIsNotNone(rule)
        self.assertIn("aspect-ratio: 3/4;", rule.group(1))
        self.assertIn("object-fit: contain;", rule.group(1))

    def test_selected_asset_exists_in_canonical_collection(self):
        self.assertTrue((ROOT / ASSET_SUFFIX).is_file())


if __name__ == "__main__":
    unittest.main()
