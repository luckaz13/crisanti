import unittest
from pathlib import Path

from bs4 import BeautifulSoup


ROOT = Path(__file__).resolve().parents[1]


class LaberintosHierarchyTests(unittest.TestCase):
    def test_bilingual_sections_opt_into_gallery_copy_layout(self):
        for relative in ("index.html", "es/index.html"):
            with self.subTest(relative=relative):
                soup = BeautifulSoup(
                    (ROOT / relative).read_text(encoding="utf-8"), "html.parser"
                )
                section = soup.find(id="los-laberintos")
                self.assertEqual("gallery", section.get("data-series-copy-layout"))

    def test_controller_mounts_active_title_and_copy_after_tabs(self):
        script = (ROOT / "js/gallery-tabs.js").read_text(encoding="utf-8")
        self.assertIn("section.dataset.seriesCopyLayout === 'gallery'", script)
        self.assertIn("tablist.insertAdjacentElement('afterend', display)", script)
        self.assertIn("title.className = 'series-copy-title'", script)
        self.assertIn("title.textContent = activeTab.textContent.trim()", script)
        self.assertIn(
            "display.appendChild(template.content.cloneNode(true))", script
        )

    def test_gallery_layout_keeps_general_lead_visible_without_specific_copy(self):
        script = (ROOT / "js/gallery-tabs.js").read_text(encoding="utf-8")
        self.assertIn("if (lead) lead.hidden = false", script)
        self.assertIn(
            "if (template) display.appendChild(template.content.cloneNode(true))",
            script,
        )


if __name__ == "__main__":
    unittest.main()
