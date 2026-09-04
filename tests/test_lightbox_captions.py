import json
import subprocess
import unittest
from pathlib import Path

from tests.css_helpers import css_rule


ROOT = Path(__file__).resolve().parents[1]


def extract_js_function(script, name):
    start = script.index(f"function {name}(")
    opening_brace = script.index("{", start)
    depth = 0
    for index in range(opening_brace, len(script)):
        if script[index] == "{":
            depth += 1
        elif script[index] == "}":
            depth -= 1
            if depth == 0:
                return script[start : index + 1]
    raise AssertionError(f"Unclosed JavaScript function: {name}")


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

    def test_deferred_carousel_item_enters_lightbox_without_restoring_source(self):
        self.assertIn("function getCarouselItems(carouselEl)", self.script)
        function = extract_js_function(self.script, "getCarouselItems")
        harness = f"""
global.document = {{ baseURI: 'https://example.test/es/index.html' }};
const $$ = (_selector, carousel) => carousel.slides;
{function}
const attributes = new Map();
const image = {{
  alt: 'Pez diferido',
  dataset: {{ src: '../img/images/Peces/35.jpg', preserved: 'yes' }},
  getAttribute(name) {{ return attributes.has(name) ? attributes.get(name) : null; }},
  setAttribute(name, value) {{ attributes.set(name, String(value)); }},
  get src() {{ return this.getAttribute('src') || ''; }},
  set src(value) {{ this.setAttribute('src', value); }}
}};
const elements = {{
  '.gallery-img': image,
  '.gallery-title': {{ textContent: '  Pez XXXV  ' }},
  '.gallery-meta': {{ textContent: '  2026 · Acrílico  ' }},
  '.gallery-desc': {{ textContent: '  Serie Peces  ' }}
}};
const slide = {{
  dataset: {{ index: '34', date: '2026' }},
  querySelector(selector) {{ return elements[selector] || null; }}
}};
const before = {{ imageDataset: {{ ...image.dataset }}, slideDataset: {{ ...slide.dataset }} }};
const items = getCarouselItems({{ slides: [slide] }});
console.log(JSON.stringify({{
  items,
  srcAfter: image.getAttribute('src'),
  imageDatasetAfter: image.dataset,
  slideDatasetAfter: slide.dataset,
  before
}}));
"""
        result = subprocess.run(
            ["node", "-e", harness],
            check=True,
            capture_output=True,
            text=True,
        )
        state = json.loads(result.stdout)

        self.assertEqual(
            [
                {
                    "src": "https://example.test/img/images/Peces/35.jpg",
                    "alt": "Pez diferido",
                    "title": "Pez XXXV",
                    "serie": "",
                    "dims": "",
                    "meta": "2026 · Acrílico",
                    "desc": "Serie Peces",
                }
            ],
            state["items"],
        )
        self.assertIsNone(state["srcAfter"])
        self.assertEqual(state["before"]["imageDataset"], state["imageDatasetAfter"])
        self.assertEqual(state["before"]["slideDataset"], state["slideDatasetAfter"])

    def test_lightbox_caption_filters_missing_fields(self):
        self.assertIn(
            "[item.title, item.serie, item.dims, item.meta, item.desc].filter(Boolean).join(' · ')",
            self.script,
        )

    def test_mobile_lightbox_caption_remains_visible(self):
        self.assertNotIn(".lightbox-caption {\n    display: none;", self.css)
        self.assertIn("overflow-y: auto;", css_rule(self.css, ".lightbox-content"))
        self.assertIn("flex: 0 0 auto;", css_rule(self.css, ".lightbox-caption"))

    def test_dark_surface_copy_uses_light_foreground(self):
        consult = css_rule(self.css, ".lightbox-consult")
        self.assertIn("color: #F7F4EE", consult)
        self.assertIn("border-color: rgba(255, 255, 255, 0.65)", consult)
        self.assertIn("color: rgba(255,255,255,0.55)", css_rule(self.css, ".footer-copy"))

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
