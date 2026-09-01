import hashlib
import re
import unittest
from pathlib import Path

from tests.css_helpers import css_rule


ROOT = Path(__file__).resolve().parents[1]


def declarations(rule):
    return {
        name.strip(): value.strip()
        for name, value in re.findall(r"([\w-]+)\s*:\s*([^;]+);", rule)
    }


class BrandMarkStylesTests(unittest.TestCase):
    def test_fish_is_mirrored_and_height_driven(self):
        css = (ROOT / "css/style.css").read_text(encoding="utf-8")
        for selector in (".nav-logo-mark", ".footer-brand-mark__fish"):
            with self.subTest(selector=selector):
                rule = css_rule(css, selector)
                self.assertIn("height: var(--brand-mark-height);", rule)
                self.assertIn("width: auto;", rule)
                self.assertIn("max-width: none;", rule)
                self.assertIn("flex-shrink: 0;", rule)
                self.assertIn("scaleX(-1)", rule)

    def test_header_token_tracks_fc_line_box_at_each_header_scale(self):
        css = (ROOT / "css/style.css").read_text(encoding="utf-8")
        rule = css_rule(css, ".nav-logo")
        self.assertIn("--brand-mark-height: 1em;", rule)
        self.assertIn("font-size: 1.35rem;", rule)
        self.assertIn("align-items: center;", rule)
        self.assertIn("overflow: visible;", rule)

        open_header = re.search(
            r"\.site-header\s*:\s*not\(\s*\.scrolled\s*\)\s*\.nav-logo\s*\{([^{}]*)\}",
            css,
        )
        self.assertIsNotNone(open_header)
        self.assertRegex(open_header.group(1), r"font-size\s*:\s*3\.375rem\s*;")

        responsive_headers = re.findall(
            r"\.site-header\s*:\s*not\(\s*\.scrolled\s*\)\s*\.nav-logo\s*\{([^{}]*)\}",
            css,
        )
        self.assertGreaterEqual(len(responsive_headers), 2)
        responsive_header = responsive_headers[-1]
        self.assertRegex(responsive_header, r"font-size\s*:\s*clamp\(")
        self.assertNotIn("width", declarations(responsive_header))

    def test_footer_token_matches_fc_text_scale(self):
        css = (ROOT / "css/style.css").read_text(encoding="utf-8")
        footer = css_rule(css, ".footer-brand-mark")
        fc = css_rule(css, ".footer-brand-mark__text")
        fc_size = re.search(r"font-size\s*:\s*([^;]+);", fc)
        self.assertIsNotNone(fc_size)
        self.assertIn(f"--brand-mark-height: {fc_size.group(1).strip()};", footer)
        self.assertIn("align-items: center;", footer)
        self.assertIn("overflow: visible;", footer)

    def test_brand_rules_keep_color_filters_and_no_independent_width(self):
        css = (ROOT / "css/style.css").read_text(encoding="utf-8")
        self.assertIn("filter: brightness(0);", css_rule(css, ".nav-logo-mark"))
        self.assertIn("filter: brightness(0) invert(1);", css_rule(css, ".site-header:not(.scrolled) .nav-logo-mark"))
        self.assertIn("filter: brightness(0) invert(1);", css_rule(css, ".footer-brand-mark__fish"))
        for selector in (".nav-logo-mark", ".footer-brand-mark__fish"):
            self.assertEqual("auto", declarations(css_rule(css, selector))["width"])

    def test_header_mark_png_is_identical_in_source_and_published_tree(self):
        digest = "450e8d553fdc6c9a93f8726d9114a450ec47d132ee630eb25c9383b301f65e1b"
        source = ROOT / "img/Peces/03-header-mark.png"
        published = ROOT / "img/images/Peces/03-header-mark.png"
        for path in (source, published):
            with self.subTest(path=path):
                self.assertEqual(digest, hashlib.sha256(path.read_bytes()).hexdigest())

    def test_bilingual_pages_reference_existing_header_mark(self):
        pt = (ROOT / "index.html").read_text(encoding="utf-8")
        es = (ROOT / "es/index.html").read_text(encoding="utf-8")
        self.assertEqual(2, pt.count('src="img/Peces/03-header-mark.png"'))
        self.assertEqual(2, es.count('src="../img/Peces/03-header-mark.png"'))
        self.assertIn('src="img/images/Peces/03-header-mark.png"', pt)
        self.assertIn('src="../img/images/Peces/03-header-mark.png"', es)

    def test_open_header_does_not_override_mark_width(self):
        css = (ROOT / "css/style.css").read_text(encoding="utf-8")
        override = css_rule(css, ".site-header:not(.scrolled) .nav-logo-mark")
        self.assertNotIn("width", declarations(override))


if __name__ == "__main__":
    unittest.main()
