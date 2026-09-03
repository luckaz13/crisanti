import json
import subprocess
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PROBE = ROOT / "tools/visual/gallery_layout_probe.mjs"
EPSILON = 2.0


def assert_rect_within(test_case, inner, outer, label):
    test_case.assertGreater(inner["width"], 0, label)
    test_case.assertGreater(inner["height"], 0, label)
    test_case.assertGreaterEqual(inner["left"], outer["left"] - EPSILON, label)
    test_case.assertLessEqual(inner["right"], outer["right"] + EPSILON, label)
    test_case.assertGreaterEqual(inner["top"], outer["top"] - EPSILON, label)
    test_case.assertLessEqual(inner["bottom"], outer["bottom"] + EPSILON, label)


class RenderedGalleryLayoutTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        completed = subprocess.run(
            ["node", str(PROBE)],
            cwd=ROOT,
            capture_output=True,
            text=True,
            timeout=50,
        )
        if completed.returncode != 0:
            raise RuntimeError(f"Gallery CDP probe failed:\n{completed.stderr}")
        cls.results = json.loads(completed.stdout)["results"]

    def test_visible_series_galleries_fit_their_sections_at_mobile_and_desktop(self):
        for result in self.results:
            viewport = result["viewport"]
            with self.subTest(viewport=viewport):
                self.assertGreaterEqual(len(result["initialGalleries"]), 10)
                for gallery in result["initialGalleries"]:
                    label = f'{viewport["width"]}px #{gallery["sectionId"]}'
                    self.assertEqual("clip", gallery["seriesOverflowX"], label)
                    self.assertEqual("visible", gallery["seriesOverflowY"], label)
                    assert_rect_within(self, gallery["gallery"], gallery["section"], label)
                    assert_rect_within(self, gallery["viewport"], gallery["section"], label)
                    if gallery["media"]:
                        self.assertTrue(gallery["mediaComplete"], label)
                        assert_rect_within(self, gallery["media"], gallery["viewport"], label)

    def test_cuadernos_orientations_render_uncropped_inside_the_viewport(self):
        for result in self.results:
            for orientation in ("cuadernosSquare", "cuadernosVertical", "cuadernosPanoramic"):
                slide = result[orientation]
                label = f'{result["viewport"]["width"]}px {orientation}'
                with self.subTest(label=label):
                    self.assertTrue(slide["complete"], label)
                    self.assertEqual("contain", slide["objectFit"], label)
                    assert_rect_within(self, slide["media"], slide["viewport"], label)
                    self.assertLessEqual(
                        abs(slide["naturalAspect"] - slide["renderedAspect"])
                        / slide["naturalAspect"],
                        0.03,
                        label,
                    )

    def test_vlak_video_fits_without_crop_or_internal_bands(self):
        for result in self.results:
            vlak = result["vlak"]
            label = f'{result["viewport"]["width"]}px Vlak'
            with self.subTest(label=label):
                self.assertTrue(vlak["complete"], label)
                self.assertEqual("contain", vlak["objectFit"], label)
                assert_rect_within(self, vlak["media"], vlak["viewport"], label)
                self.assertLessEqual(
                    abs(vlak["naturalAspect"] - vlak["renderedAspect"])
                    / vlak["naturalAspect"],
                    0.02,
                    label,
                )

    def test_peces_crossfades_in_place(self):
        for result in self.results:
            peces = result["peces"]
            with self.subTest(viewport=result["viewport"]):
                self.assertEqual(1, peces["activeIndex"])
                self.assertEqual("1", peces["activeOpacity"])
                self.assertEqual("0", peces["previousOpacity"])
                self.assertEqual("none", peces["trackTransform"])

    def test_mobile_lightbox_shows_loaded_artwork_and_legible_ficha(self):
        mobile = next(result for result in self.results if result["viewport"]["width"] == 390)
        lightbox = mobile["lightbox"]

        self.assertFalse(lightbox["hidden"])
        self.assertTrue(lightbox["imageComplete"])
        self.assertGreater(lightbox["imageNaturalWidth"], 0)
        self.assertGreater(lightbox["imageNaturalHeight"], 0)
        self.assertTrue(lightbox["captionText"])
        self.assertGreaterEqual(lightbox["captionContrast"], 4.5)
        self.assertGreater(lightbox["image"]["bottom"], 0)
        self.assertLess(lightbox["image"]["top"], lightbox["viewport"]["height"])
        self.assertGreater(lightbox["caption"]["bottom"], 0)
        self.assertLess(lightbox["caption"]["top"], lightbox["viewport"]["height"])


if __name__ == "__main__":
    unittest.main()
