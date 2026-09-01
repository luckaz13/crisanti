import unittest
from pathlib import Path

from tests.css_helpers import css_rule


ROOT = Path(__file__).resolve().parents[1]


class BrandMarkStylesTests(unittest.TestCase):
    def test_fish_is_mirrored_and_height_driven(self):
        css = (ROOT / "css/style.css").read_text(encoding="utf-8")
        for selector in (".nav-logo-mark", ".footer-brand-mark__fish"):
            with self.subTest(selector=selector):
                rule = css_rule(css, selector)
                self.assertIn("height: var(--brand-mark-height);", rule)
                self.assertIn("width: auto;", rule)
                self.assertIn("flex-shrink: 0;", rule)
                self.assertIn("scaleX(-1)", rule)

    def test_brand_containers_define_shared_line_box_height(self):
        css = (ROOT / "css/style.css").read_text(encoding="utf-8")
        for selector in (".nav-logo", ".footer-brand-mark"):
            with self.subTest(selector=selector):
                rule = css_rule(css, selector)
                self.assertIn("--brand-mark-height: 1em;", rule)
                self.assertIn("align-items: center;", rule)
                self.assertIn("overflow: visible;", rule)

    def test_open_header_does_not_override_mark_width(self):
        css = (ROOT / "css/style.css").read_text(encoding="utf-8")
        self.assertNotIn(".site-header:not(.scrolled) .nav-logo-mark {\n    width:", css)


if __name__ == "__main__":
    unittest.main()
