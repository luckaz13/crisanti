import unittest
from pathlib import Path

from bs4 import BeautifulSoup


ROOT = Path(__file__).resolve().parents[1]


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

    def test_crossfade_stacks_slides_without_translating_track(self):
        script = (ROOT / "js/gallery.js").read_text(encoding="utf-8")
        css = (ROOT / "css/style.css").read_text(encoding="utf-8")

        self.assertIn("carouselEl.dataset.transition === 'crossfade'", script)
        self.assertIn("slide.classList.toggle('is-active', isActive)", script)
        self.assertIn('[data-transition="crossfade"] .gallery-track', css)
        self.assertIn('[data-transition="crossfade"] .gallery-slide', css)

    def test_reduced_motion_disables_crossfade_duration(self):
        css = (ROOT / "css/style.css").read_text(encoding="utf-8")
        reduced_motion = css[css.index("@media (prefers-reduced-motion: reduce)") :]

        self.assertIn('[data-transition="crossfade"] .gallery-slide', reduced_motion)
        self.assertIn("transition-duration: 0.01ms;", reduced_motion)


if __name__ == "__main__":
    unittest.main()
