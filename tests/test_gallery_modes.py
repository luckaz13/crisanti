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


if __name__ == "__main__":
    unittest.main()
