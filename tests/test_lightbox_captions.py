import unittest
from pathlib import Path

from tests.css_helpers import css_rule


ROOT = Path(__file__).resolve().parents[1]


class LightboxCaptionTests(unittest.TestCase):
    def setUp(self):
        self.script = (ROOT / "js/main.js").read_text(encoding="utf-8")
        self.css = (ROOT / "css/style.css").read_text(encoding="utf-8")
        self.pt_html = (ROOT / "index.html").read_text(encoding="utf-8")
        self.es_html = (ROOT / "es/index.html").read_text(encoding="utf-8")

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

    def test_lightbox_scroll_region_is_keyboard_reachable_in_both_locales(self):
        self.assertIn(
            '<div aria-label="Detalhes da obra" class="lightbox-content" role="region" tabindex="0">',
            self.pt_html,
        )
        self.assertIn(
            '<div aria-label="Detalles de la obra" class="lightbox-content" role="region" tabindex="0">',
            self.es_html,
        )

    def test_open_resets_scroll_before_replacing_content_and_keeps_close_focus(self):
        self.assertIn("const lightboxContent = $('.lightbox-content');", self.script)
        self.assertIn("lightboxContent.scrollTop = 0;", self.script)
        self.assertLess(
            self.script.index("lightboxContent.scrollTop = 0;"),
            self.script.index("lbImg.src = item.src;"),
        )
        self.assertIn("lbClose.focus();", self.script)


if __name__ == "__main__":
    unittest.main()
