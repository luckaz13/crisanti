import json
import re
import subprocess
import unittest
from pathlib import Path

from bs4 import BeautifulSoup


ROOT = Path(__file__).resolve().parents[1]


def css_declarations(css, selector):
    match = re.search(rf"{re.escape(selector)}\s*\{{([^}}]+)\}}", css)
    if not match:
        return {}
    return {
        name.strip(): value.strip()
        for name, value in re.findall(r"([\w-]+)\s*:\s*([^;]+);", match.group(1))
    }


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


class GalleryModesTests(unittest.TestCase):
    def test_only_peces_requests_crossfade(self):
        for page, carousel_id in (
            ("index.html", "gallery-carousel-peixes"),
            ("es/index.html", "gallery-carousel-peces"),
        ):
            with self.subTest(page=page):
                soup = BeautifulSoup(
                    (ROOT / page).read_text(encoding="utf-8"), "html.parser"
                )
                carousel = soup.find(id=carousel_id)
                self.assertEqual("crossfade", carousel.get("data-transition"))
                self.assertEqual(1, len(soup.select('[data-transition="crossfade"]')))

    def test_series_gallery_clips_only_the_horizontal_axis(self):
        css = (ROOT / "css/style.css").read_text(encoding="utf-8")
        declarations = css_declarations(css, ".series-gallery")

        self.assertEqual("clip", declarations.get("overflow-x"))
        self.assertEqual("visible", declarations.get("overflow-y"))

    def test_crossfade_stack_is_gated_until_javascript_initializes(self):
        script = (ROOT / "js/gallery.js").read_text(encoding="utf-8")
        css = (ROOT / "css/style.css").read_text(encoding="utf-8")
        initialized = '[data-carousel-initialized="true"]'

        crossfade_selectors = [
            selector.strip()
            for selector in re.findall(r"([^{}]+)\{", css)
            if '[data-transition="crossfade"]' in selector
            and (".gallery-track" in selector or ".gallery-slide" in selector)
        ]

        self.assertIn("carouselEl.dataset.transition === 'crossfade'", script)
        self.assertIn("slide.classList.toggle('is-active', isActive)", script)
        self.assertTrue(crossfade_selectors)
        self.assertTrue(
            all(initialized in selector for selector in crossfade_selectors),
            crossfade_selectors,
        )

    def test_no_javascript_keeps_first_peces_slide_visible(self):
        css = (ROOT / "css/style.css").read_text(encoding="utf-8")
        soup = BeautifulSoup(
            (ROOT / "es/index.html").read_text(encoding="utf-8"), "html.parser"
        )
        carousel = soup.find(id="gallery-carousel-peces")
        first_image = carousel.select_one(".gallery-slide .gallery-img")

        self.assertTrue(first_image.get("src"))
        self.assertEqual("flex", css_declarations(css, ".gallery-track").get("display"))

    def test_crossfade_defers_and_preloader_restores_sources_by_radius(self):
        script = (ROOT / "js/gallery.js").read_text(encoding="utf-8")
        for name in ("deferCrossfadeImages", "restoreImageSource", "preloadImage"):
            self.assertIn(f"function {name}(", script)
        functions = "\n".join(
            extract_js_function(script, name)
            for name in ("deferCrossfadeImages", "restoreImageSource", "preloadImage")
        )
        harness = f"""
{functions}
const probes = [];
global.Image = function Image() {{ probes.push(this); }};
function makeImage(src) {{
  const attributes = new Map([['src', src]]);
  return {{
    dataset: {{}},
    currentSrc: '',
    getAttribute(name) {{ return attributes.has(name) ? attributes.get(name) : null; }},
    setAttribute(name, value) {{ attributes.set(name, String(value)); }},
    removeAttribute(name) {{ attributes.delete(name); }},
    get src() {{ return this.getAttribute('src') || ''; }},
    set src(value) {{ this.setAttribute('src', value); }}
  }};
}}
const images = Array.from({{ length: 7 }}, (_, index) => makeImage(`${{index}}.jpg`));
const slides = images.map(img => ({{ querySelector: () => img }}));
deferCrossfadeImages(slides, 4);
const deferred = images.map(img => ({{ src: img.getAttribute('src'), dataSrc: img.dataset.src || null }}));
preloadImage(images[5]);
console.log(JSON.stringify({{
  deferred,
  restored: {{
    src: images[5].getAttribute('src'),
    dataSrc: images[5].dataset.src || null,
    preloaded: images[5].dataset.preloaded,
    loading: images[5].loading,
    probeSrc: probes[0] && probes[0].src
  }}
}}));
"""
        result = subprocess.run(
            ["node", "-e", harness],
            check=True,
            capture_output=True,
            text=True,
        )
        state = json.loads(result.stdout)

        self.assertEqual([f"{index}.jpg" for index in range(5)], [
            image["src"] for image in state["deferred"][:5]
        ])
        self.assertEqual([None, None], [
            image["src"] for image in state["deferred"][5:]
        ])
        self.assertEqual(["5.jpg", "6.jpg"], [
            image["dataSrc"] for image in state["deferred"][5:]
        ])
        self.assertEqual(
            {
                "src": "5.jpg",
                "dataSrc": None,
                "preloaded": "true",
                "loading": "eager",
                "probeSrc": "5.jpg",
            },
            state["restored"],
        )

    def test_crossfade_defers_sources_before_enabling_stack(self):
        script = (ROOT / "js/gallery.js").read_text(encoding="utf-8")

        self.assertIn("deferCrossfadeImages(slides, preloadRadius);", script)
        defer = script.index("deferCrossfadeImages(slides, preloadRadius);")
        initialize = script.index("carouselEl.dataset.carouselInitialized = 'true';")
        self.assertLess(defer, initialize)

    def test_reduced_motion_disables_crossfade_duration(self):
        css = (ROOT / "css/style.css").read_text(encoding="utf-8")
        reduced_motion = css[css.index("@media (prefers-reduced-motion: reduce)") :]

        self.assertIn('[data-carousel-initialized="true"] .gallery-slide', reduced_motion)
        self.assertIn("transition-duration: 0.01ms;", reduced_motion)

    def test_crossfade_uses_slow_transition_and_stable_max_height(self):
        css = (ROOT / "css/style.css").read_text(encoding="utf-8")
        script = (ROOT / "js/gallery.js").read_text(encoding="utf-8")

        self.assertRegex(
            css,
            r'\[data-transition="crossfade"\]\[data-carousel-initialized="true"\] \.gallery-slide\s*\{[^}]*transition:\s*opacity 2s',
        )
        height_fn = extract_js_function(script, "updateViewportHeight")
        self.assertIn("isCrossfade", height_fn)
        self.assertIn("Math.max", height_fn)
        self.assertIn("slides", height_fn)

    def test_ficcao_uses_compact_editorial_spacing(self):
        css = (ROOT / "css/style.css").read_text(encoding="utf-8")

        title = css_declarations(css, "#ficcao .literatura-work-title")
        tabs = css_declarations(css, "#ficcao .gallery-tabs")
        caption = css_declarations(css, "#ficcao .gallery-caption")
        overview = css_declarations(css, "#ficcao .literatura-fiction-overview")
        subsection = css_declarations(css, "#ficcao.literatura-subsection")

        self.assertEqual("0.75rem auto 1rem", title.get("margin"))
        self.assertEqual("0.75rem", tabs.get("margin-bottom"))
        self.assertEqual("0.5rem", tabs.get("padding-bottom"))
        self.assertEqual("0.75rem 1rem 0", caption.get("padding"))
        self.assertEqual("1rem", overview.get("margin-top"))
        self.assertEqual("1.5rem", subsection.get("margin-bottom"))

    def test_ficcao_tabs_keep_inactive_flores_visible_on_light_surface(self):
        css = (ROOT / "css/style.css").read_text(encoding="utf-8")
        tabs = css_declarations(css, "#ficcao .gallery-tab")
        active = css_declarations(css, "#ficcao .gallery-tab.active")

        self.assertEqual("#1A1714", tabs.get("color"))
        self.assertEqual("rgba(26, 23, 20, 0.08)", tabs.get("background"))
        self.assertEqual("#1A1714", active.get("background"))
        self.assertEqual("#F9F7F4", active.get("color"))


if __name__ == "__main__":
    unittest.main()
