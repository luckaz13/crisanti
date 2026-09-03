import json
import os
import subprocess
import unittest
from pathlib import Path
from unittest.mock import patch


ROOT = Path(__file__).resolve().parents[1]
PROBE = ROOT / "tools/visual/gallery_layout_probe.mjs"
EPSILON = 2.0
EXPECTED_INITIALLY_HIDDEN_GALLERIES = 26
CHROMIUM_STARTUP_TIMEOUT_SECONDS = 15
CAPTURED_PROBE_TIMEOUT_SECONDS = 105
CLEANUP_RESERVE_SECONDS = 11
PROBE_PROCESS_TIMEOUT_SECONDS = 150
COMMON_GALLERY_IDS = {
    "gallery-carousel-seda",
    "gallery-carousel-seda-2024",
    "gallery-carousel-seda-bahia",
    "gallery-carousel-juego-del-tren",
    "gallery-carousel-ensayos-collagem",
    "gallery-carousel-ensayos-crema",
    "gallery-carousel-ensayos-el-telefono",
    "gallery-carousel-ensayos-gatos",
    "gallery-carousel-ensayos-la-cocina",
    "gallery-carousel-ensayos-perspectiva",
    "gallery-carousel-ensayos-siluetas",
    "gallery-carousel-ensayos-urubus",
    "gallery-carousel-la-escultura-addis-abbaba",
    "gallery-carousel-la-escultura-invierno",
    "gallery-carousel-la-escultura-invierno-iii",
    "gallery-carousel-la-escultura-pez-iii",
    "gallery-carousel-la-escultura-pez-iv",
    "gallery-carousel-la-escultura-soies-sauvages",
    "gallery-carousel-la-escultura-verde",
    "gallery-carousel-la-fotografia-cotidiano",
    "gallery-carousel-la-fotografia-exilio",
    "gallery-carousel-la-fotografia-luz-liquida",
    "gallery-carousel-la-moda",
    "gallery-carousel-los-laberintos-cadaver-exquisito",
    "gallery-carousel-los-laberintos-el-calendario",
    "gallery-carousel-los-laberintos-el-puzzle",
    "gallery-carousel-los-laberintos-la-papa",
    "gallery-carousel-los-laberintos-las-etiquetas",
    "gallery-carousel-los-laberintos-memory",
    "gallery-carousel-los-ninos-cosimo",
    "gallery-carousel-los-ninos-der-elefant",
    "gallery-carousel-los-ninos-el-ciervo",
    "gallery-carousel-los-ninos-seis-animales",
    "gallery-carousel-proyectos-especiales-la-fuente-y-los-simios",
    "gallery-carousel-proyectos-especiales-master-taxi",
    "gallery-carousel-proyectos-especiales-vlak",
    "gallery-carousel-ficcao-el-nombre",
    "gallery-carousel-ficcao-flores",
}
EXPECTED_GALLERY_IDS = {
    "pt": COMMON_GALLERY_IDS
    | {"gallery-carousel-peixes", "gallery-carousel-cadernos"},
    "es": COMMON_GALLERY_IDS
    | {"gallery-carousel-peces", "gallery-carousel-cuadernos"},
}


class ProbeCommandTests(unittest.TestCase):
    def test_run_command_times_out_and_terminates_its_child(self):
        script = f"""
import {{ runCommand }} from {PROBE.as_uri()!r};
try {{
  await runCommand(process.execPath, ['-e', 'setTimeout(() => {{}}, 5000)'], {{ timeoutMs: 25 }});
  process.exitCode = 1;
}} catch (error) {{
  if (!/timed out/.test(error.message)) throw error;
}}
"""
        completed = subprocess.run(
            ["node", "--input-type=module", "--eval", script],
            cwd=ROOT,
            capture_output=True,
            text=True,
            timeout=5,
        )

        self.assertEqual(0, completed.returncode, completed.stderr)

    def test_external_timeout_reserves_startup_probe_and_cleanup_budget(self):
        timing = read_probe_timing()
        self.assertGreaterEqual(PROBE_PROCESS_TIMEOUT_SECONDS, 150)
        self.assertEqual(CHROMIUM_STARTUP_TIMEOUT_SECONDS * 1000, timing["startupMs"])
        self.assertEqual(CAPTURED_PROBE_TIMEOUT_SECONDS * 1000, timing["capturedProbeMs"])
        self.assertEqual(CLEANUP_RESERVE_SECONDS * 1000, timing["cleanupReserveMs"])
        self.assertGreater(
            PROBE_PROCESS_TIMEOUT_SECONDS,
            CHROMIUM_STARTUP_TIMEOUT_SECONDS
            + CAPTURED_PROBE_TIMEOUT_SECONDS
            + CLEANUP_RESERVE_SECONDS,
        )

    def test_probe_subprocess_uses_the_documented_external_timeout(self):
        with patch("tests.test_gallery_rendered_layout.subprocess.run") as run:
            run_probe(["node", str(PROBE)])

        self.assertEqual(PROBE_PROCESS_TIMEOUT_SECONDS, run.call_args.kwargs["timeout"])


def assert_rect_within(test_case, inner, outer, label):
    test_case.assertGreater(inner["width"], 0, label)
    test_case.assertGreater(inner["height"], 0, label)
    test_case.assertGreaterEqual(inner["left"], outer["left"] - EPSILON, label)
    test_case.assertLessEqual(inner["right"], outer["right"] + EPSILON, label)
    test_case.assertGreaterEqual(inner["top"], outer["top"] - EPSILON, label)
    test_case.assertLessEqual(inner["bottom"], outer["bottom"] + EPSILON, label)


def assert_horizontal_within(test_case, inner, outer, label):
    test_case.assertGreater(inner["width"], 0, label)
    test_case.assertGreaterEqual(inner["left"], outer["left"] - EPSILON, label)
    test_case.assertLessEqual(inner["right"], outer["right"] + EPSILON, label)


def run_probe(command):
    return subprocess.run(
        command,
        cwd=ROOT,
        capture_output=True,
        text=True,
        timeout=PROBE_PROCESS_TIMEOUT_SECONDS,
    )


def read_probe_timing():
    script = f"""
import {{ PROBE_TIMING }} from {PROBE.as_uri()!r};
console.log(JSON.stringify(PROBE_TIMING));
"""
    completed = subprocess.run(
        ["node", "--input-type=module", "--eval", script],
        cwd=ROOT,
        capture_output=True,
        text=True,
        timeout=5,
        check=True,
    )
    return json.loads(completed.stdout)


class RenderedGalleryLayoutTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        command = ["node", str(PROBE)]
        capture_dir = os.environ.get("CRISANTI_CAPTURE_DIR")
        metrics_output = os.environ.get("CRISANTI_METRICS_OUTPUT")
        if capture_dir:
            command.extend(["--capture-dir", capture_dir])
        if metrics_output:
            command.extend(["--output", metrics_output])
        completed = run_probe(command)
        if completed.returncode != 0:
            raise RuntimeError(f"Gallery CDP probe failed:\n{completed.stderr}")
        payload = json.loads(completed.stdout)
        cls.results = payload["results"]
        cls.cleanup = payload["cleanup"]

    def test_probes_both_languages_at_mobile_and_desktop(self):
        combinations = {
            (result["language"], result["viewport"]["width"], result["viewport"]["height"])
            for result in self.results
        }
        self.assertEqual(
            {
                ("pt", 390, 844),
                ("pt", 1440, 1000),
                ("es", 390, 844),
                ("es", 1440, 1000),
            },
            combinations,
        )

    def test_every_gallery_is_measured_and_fits_without_overflow_masking(self):
        for result in self.results:
            viewport = result["viewport"]
            language = result["language"]
            galleries = result["galleries"]
            label = f'{language} {viewport["width"]}px'
            with self.subTest(label=label):
                self.assertEqual(40, len(galleries), label)
                self.assertEqual(
                    EXPECTED_GALLERY_IDS[language],
                    {gallery["carouselId"] for gallery in galleries},
                    label,
                )
                self.assertEqual(
                    EXPECTED_INITIALLY_HIDDEN_GALLERIES,
                    sum(gallery["initiallyHidden"] for gallery in galleries),
                    label,
                )
                self.assertTrue(result["pageGeometry"]["overflowMaskDisabled"], label)
                inner_width = result["pageGeometry"]["innerWidth"]
                self.assertEqual(viewport["width"], inner_width, label)
                self.assertEqual(inner_width, result["pageGeometry"]["bodyScrollWidth"], label)
                self.assertEqual(inner_width, result["pageGeometry"]["documentScrollWidth"], label)
                for gallery in galleries:
                    gallery_label = f'{label} #{gallery["carouselId"]}'
                    section_bounds = {
                        "left": 0,
                        "right": viewport["width"],
                        "top": gallery["section"]["top"],
                        "bottom": gallery["section"]["bottom"],
                        "width": viewport["width"],
                        "height": gallery["section"]["height"],
                    }
                    assert_horizontal_within(self, gallery["section"], section_bounds, gallery_label)
                    self.assertGreaterEqual(gallery["section"]["left"], 0, gallery_label)
                    self.assertLessEqual(gallery["section"]["right"], inner_width, gallery_label)
                    self.assertEqual(inner_width, gallery["bodyScrollWidth"], gallery_label)
                    self.assertEqual(inner_width, gallery["documentScrollWidth"], gallery_label)
                    assert_horizontal_within(self, gallery["gallery"], gallery["section"], gallery_label)
                    assert_horizontal_within(self, gallery["viewport"], gallery["section"], gallery_label)
                    self.assertTrue(gallery["mediaComplete"], gallery_label)
                    assert_horizontal_within(self, gallery["media"], gallery["section"], gallery_label)
                    assert_horizontal_within(self, gallery["media"], gallery["viewport"], gallery_label)

    def test_cuadernos_orientations_render_uncropped_in_both_languages(self):
        for result in self.results:
            for orientation in ("cuadernosSquare", "cuadernosVertical", "cuadernosPanoramic"):
                slide = result[orientation]
                label = f'{result["language"]} {result["viewport"]["width"]}px {orientation}'
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
            label = f'{result["language"]} {result["viewport"]["width"]}px Vlak'
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

    def test_peces_uses_a_real_normal_motion_crossfade(self):
        for result in self.results:
            peces = result["peces"]
            label = f'{result["language"]} {result["viewport"]["width"]}px Peces'
            with self.subTest(label=label):
                self.assertFalse(peces["reducedMotion"], label)
                self.assertIn("opacity", peces["transitionProperty"], label)
                self.assertGreaterEqual(peces["transitionDurationMs"], 1800, label)
                self.assertEqual(0, peces["beforeActiveIndex"], label)
                self.assertEqual(1, peces["afterActiveIndex"], label)
                self.assertEqual("1", peces["activeOpacity"], label)
                self.assertEqual("0", peces["previousOpacity"], label)
                self.assertEqual("none", peces["trackTransform"], label)

    def test_visual_content_contracts_are_recorded_for_every_surface(self):
        expected_headings = {"pt": "Sinopse de Master Taxi", "es": "Master Taxi Sinopsis"}
        for result in self.results:
            label = f'{result["language"]} {result["viewport"]["width"]}px'
            with self.subTest(label=label):
                self.assertEqual("FC", result["brands"]["header"]["text"], label)
                self.assertEqual("FC", result["brands"]["footer"]["text"], label)
                self.assertTrue(result["brands"]["header"]["markComplete"], label)
                self.assertTrue(result["brands"]["footer"]["markComplete"], label)

                timeline = result["timeline"]
                self.assertFalse(timeline["collapsed"]["expanded"], label)
                self.assertTrue(timeline["collapsed"]["contentHidden"], label)
                self.assertTrue(timeline["expanded"]["expanded"], label)
                self.assertFalse(timeline["expanded"]["contentHidden"], label)
                self.assertEqual(4, timeline["expanded"]["collapsibleItemCount"], label)

                critica = result["critica"]
                self.assertEqual(8, critica["cardCount"], label)
                self.assertEqual(["rgb(32, 30, 28)"], critica["backgroundColors"], label)

                master_taxi = result["masterTaxi"]
                self.assertTrue(master_taxi["panelVisible"], label)
                self.assertEqual(expected_headings[result["language"]], master_taxi["synopsisHeading"], label)
                self.assertEqual(10, master_taxi["synopsisParagraphCount"], label)
                self.assertEqual("Master Taxi Dinámica", master_taxi["documentName"], label)
                self.assertEqual(2, master_taxi["documentLinkCount"], label)

                self.assertTrue(result["laberintos"]["imageCapturedBeforeText"], label)
                self.assertEqual("El Nombre", result["fiction"]["elNombre"]["title"], label)
                self.assertTrue(result["fiction"]["elNombre"]["titleGalleryCopyOrder"], label)
                self.assertTrue(result["fiction"]["flores"]["panelPresent"], label)
                self.assertTrue(result["fiction"]["flores"]["templatePreserved"], label)

    def test_lightbox_shows_loaded_artwork_and_legible_ficha_everywhere(self):
        for result in self.results:
            lightbox = result["lightbox"]
            label = f'{result["language"]} {result["viewport"]["width"]}px lightbox'
            with self.subTest(label=label):
                self.assertFalse(lightbox["hidden"], label)
                self.assertTrue(lightbox["imageComplete"], label)
                self.assertGreater(lightbox["imageNaturalWidth"], 0, label)
                self.assertGreater(lightbox["imageNaturalHeight"], 0, label)
                self.assertTrue(lightbox["captionText"], label)
                self.assertGreaterEqual(lightbox["captionContrast"], 4.5, label)
                self.assertGreater(lightbox["image"]["bottom"], 0, label)
                self.assertLess(lightbox["image"]["top"], lightbox["viewport"]["height"], label)
                self.assertGreater(lightbox["caption"]["bottom"], 0, label)
                self.assertLess(lightbox["caption"]["top"], lightbox["viewport"]["height"], label)
                self.assertGreaterEqual(lightbox["caption"]["left"], 0, label)
                self.assertLessEqual(lightbox["caption"]["right"], lightbox["viewport"]["width"], label)
                self.assertGreaterEqual(lightbox["caption"]["top"], 0, label)
                self.assertLessEqual(lightbox["caption"]["bottom"], lightbox["viewport"]["height"], label)
                self.assertTrue(lightbox["contentIsScrollOwner"], label)
                self.assertTrue(lightbox["contentFocusable"], label)
                self.assertTrue(lightbox["closeFocusedBeforeContent"], label)
                self.assertTrue(lightbox["contentFocused"], label)

    def test_browser_and_profile_are_cleaned_up(self):
        self.assertTrue(self.cleanup["browserExited"])
        self.assertEqual([], self.cleanup["residualProcessIds"])
        self.assertTrue(self.cleanup["profileRemoved"])


if __name__ == "__main__":
    unittest.main()
