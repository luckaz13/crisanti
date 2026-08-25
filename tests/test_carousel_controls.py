import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class StableCarouselControlsTests(unittest.TestCase):
    def test_script_anchors_controls_to_first_measurable_slide(self):
        script = (ROOT / "js/gallery.js").read_text(encoding="utf-8")

        self.assertIn("function updateControlsAnchor()", script)
        self.assertIn("const anchorSlide = slides[0]", script)
        self.assertIn("controlsAnchorWidth", script)
        self.assertIn("--gallery-controls-top", script)

    def test_css_uses_anchor_on_desktop_and_preserves_mobile_flow(self):
        css = (ROOT / "css/style.css").read_text(encoding="utf-8")

        self.assertIn("top: var(--gallery-controls-top, 50%);", css)
        mobile = css[css.index("@media (max-width: 768px)") :]
        self.assertIn(".gallery-controls", mobile)
        self.assertIn("position: static;", mobile)
        self.assertIn("transform: none;", mobile)


if __name__ == "__main__":
    unittest.main()
