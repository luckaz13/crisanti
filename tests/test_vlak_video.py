import re
import subprocess
import unittest
from pathlib import Path

from bs4 import BeautifulSoup


ROOT = Path(__file__).resolve().parents[1]


class VlakVideoTests(unittest.TestCase):
    def _section(self, relative):
        soup = BeautifulSoup(
            (ROOT / relative).read_text(encoding="utf-8"), "html.parser"
        )
        return soup.find(id="juego-del-tren")

    def test_video_asset_is_the_provided_mp4(self):
        video = ROOT / "videos/vlak.mp4"
        self.assertTrue(video.is_file())
        self.assertEqual(24_103_420, video.stat().st_size)

    def test_selected_video_is_not_excluded_from_version_control(self):
        result = subprocess.run(
            ["git", "check-ignore", "-q", "videos/vlak.mp4"], cwd=ROOT
        )
        self.assertNotEqual(0, result.returncode)

    def test_bilingual_titles_are_reviewed(self):
        expected = {
            "index.html": "Vlak: O jogo do trem",
            "es/index.html": "Vlak: El juego del tren",
        }
        for relative, title in expected.items():
            with self.subTest(relative=relative):
                self.assertEqual(
                    title,
                    self._section(relative)
                    .select_one(".section-title")
                    .get_text(strip=True),
                )

    def test_video_is_first_slide_and_images_keep_their_order(self):
        expected_first_image = {
            "index.html": "img/images/Proyectos Especiales/Vlak/01.jpg",
            "es/index.html": "../img/images/Proyectos Especiales/Vlak/01.jpg",
        }
        for relative, first_image in expected_first_image.items():
            with self.subTest(relative=relative):
                section = self._section(relative)
                slides = section.select(".gallery-track > .gallery-slide")
                video = slides[0].select_one("video.gallery-video")
                self.assertIsNotNone(video)
                self.assertEqual(18, len(slides))
                self.assertEqual(17, len(section.select(".gallery-slide .gallery-img")))
                self.assertEqual(
                    first_image, slides[1].select_one(".gallery-img")["src"]
                )

    def test_video_has_manual_controls_and_no_static_autoplay_or_loop(self):
        expected_source = {
            "index.html": "videos/vlak.mp4",
            "es/index.html": "../videos/vlak.mp4",
        }
        for relative, source in expected_source.items():
            with self.subTest(relative=relative):
                video = self._section(relative).select_one("video.gallery-video")
                self.assertIsNotNone(video)
                self.assertEqual("", video.get("controls"))
                self.assertEqual("", video.get("muted"))
                self.assertEqual("", video.get("playsinline"))
                self.assertEqual("metadata", video.get("preload"))
                self.assertIsNone(video.get("autoplay"))
                self.assertIsNone(video.get("loop"))
                self.assertEqual(source, video.select_one("source")["src"])

    def test_video_declares_ten_second_start_time_in_both_languages(self):
        for relative in ("index.html", "es/index.html"):
            with self.subTest(relative=relative):
                video = self._section(relative).select_one("video.gallery-video")
                self.assertEqual("10", video.get("data-start-time"))

    def test_video_surface_is_scoped_and_uncropped(self):
        css = (ROOT / "css/style.css").read_text(encoding="utf-8")
        rule = re.search(r"\.gallery-video\s*\{([^}]+)\}", css)
        self.assertIsNotNone(rule)
        self.assertIn("aspect-ratio: 478 / 850;", rule.group(1))
        self.assertIn("object-fit: contain;", rule.group(1))
        self.assertIn("max-height: 78vh;", rule.group(1))

    def test_controller_requires_active_slide_and_visible_carousel(self):
        script = (ROOT / "js/gallery.js").read_text(encoding="utf-8")
        self.assertIn("function syncVideoPlayback()", script)
        self.assertIn("slideIndex === currentIndex", script)
        self.assertIn("carouselVisible", script)
        self.assertIn("document.visibilityState === 'visible'", script)
        self.assertIn("!video.ended", script)

    def test_controller_plays_safely_and_pauses_without_resetting(self):
        script = (ROOT / "js/gallery.js").read_text(encoding="utf-8")
        self.assertIn("video.play()", script)
        self.assertIn("playPromise.catch(() => {})", script)
        self.assertIn("video.pause()", script)
        self.assertNotIn("video.currentTime = 0", script)

    def test_controller_applies_configured_start_time_only_once(self):
        script = (ROOT / "js/gallery.js").read_text(encoding="utf-8")
        self.assertIn("function applyInitialVideoTime(video)", script)
        self.assertIn("video.dataset.startTimeApplied === 'true'", script)
        self.assertIn("video.currentTime = startTime;", script)
        self.assertIn("video.dataset.startTimeApplied = 'true';", script)
        self.assertIn("Math.abs(video.currentTime - startTime) < 0.25", script)
        self.assertIn("video.addEventListener('seeked', completeInitialSeek);", script)
        self.assertIn("video.addEventListener('progress', initializeVideo);", script)
        self.assertIn("video.addEventListener('canplay', initializeVideo);", script)
        self.assertIn("video.dataset.startTimePending === 'true'", script)
        self.assertIn("video.dataset.startTimePending = 'true';", script)
        self.assertIn("delete video.dataset.startTimePending;", script)
        self.assertIn("range.start(index) <= startTime", script)
        self.assertIn("range.end(index) >= startTime", script)
        self.assertIn(
            "video.addEventListener('loadedmetadata', initializeVideo, { once: true });",
            script,
        )
        sync = script[
            script.index("function syncVideoPlayback()") :
            script.index("function updateCarousel()")
        ]
        self.assertIn("applyInitialVideoTime(video);", sync)
        self.assertLess(
            sync.index("applyInitialVideoTime(video);"), sync.index("video.play()")
        )

    def test_controller_observes_viewport_and_syncs_after_navigation(self):
        script = (ROOT / "js/gallery.js").read_text(encoding="utf-8")
        self.assertIn("new IntersectionObserver", script)
        self.assertIn("visibilityObserver.observe(viewport)", script)
        self.assertIn("syncVideoPlayback();", script)


if __name__ == "__main__":
    unittest.main()
