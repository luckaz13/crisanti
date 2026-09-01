import unittest
from pathlib import Path

from tests.css_helpers import css_rule


ROOT = Path(__file__).resolve().parents[1]


class ArtworkSurfaceTests(unittest.TestCase):
    def test_every_artwork_surface_uses_three_pixel_mat(self):
        css = (ROOT / "css/style.css").read_text(encoding="utf-8")

        self.assertIn("--artwork-mat: 3px;", css)
        self.assertIn(
            "border: var(--artwork-mat) solid var(--artwork-outline);",
            css_rule(css, ".obra-img,\n.gallery-img,\n.lightbox-img"),
        )


if __name__ == "__main__":
    unittest.main()
