import unittest
from pathlib import Path

from tests.css_helpers import css_rule


ROOT = Path(__file__).resolve().parents[1]


class LightboxCaptionTests(unittest.TestCase):
    def setUp(self):
        self.script = (ROOT / "js/main.js").read_text(encoding="utf-8")
        self.css = (ROOT / "css/style.css").read_text(encoding="utf-8")

    def test_carousel_items_collect_all_rendered_caption_fields(self):
        self.assertIn(
            "meta:  slide.querySelector('.gallery-meta')?.textContent?.trim() || ''",
            self.script,
        )
        self.assertIn(
            "desc:  slide.querySelector('.gallery-desc')?.textContent?.trim() || ''",
            self.script,
        )

    def test_lightbox_caption_filters_missing_fields(self):
        self.assertIn(
            "[item.title, item.serie, item.dims, item.meta, item.desc].filter(Boolean).join(' · ')",
            self.script,
        )

    def test_mobile_lightbox_caption_remains_visible(self):
        self.assertNotIn(".lightbox-caption {\n    display: none;", self.css)
        self.assertIn("overflow-y: auto;", css_rule(self.css, ".lightbox-content"))
        self.assertIn("flex: 0 0 auto;", css_rule(self.css, ".lightbox-caption"))


if __name__ == "__main__":
    unittest.main()
