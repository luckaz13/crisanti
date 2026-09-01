import json
import unittest
from pathlib import Path

from bs4 import BeautifulSoup

from tools.acervo.render_galleries import (
    apply_pt_editorial,
    clone_tabbed_gallery,
    load_series_editorial,
    render_master_taxi_synopsis,
    render_page,
    render_series_copy,
    render_slides,
    update_carousel,
)


def asset(path, title="Obra I"):
    return {
        "path": path,
        "filename": path.rsplit("/", 1)[-1],
        "caption": {
            "es": {"title": title, "year": "2025", "details": "Técnica mixta"},
            "pt": {"title": title, "year": "2025", "details": "Técnica mista"},
        },
        "alt": {"es": f"{title} — Fabio Crisanti", "pt": f"{title} — Fabio Crisanti"},
    }


class GalleryRenderingTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        root = Path(__file__).resolve().parents[1]
        cls.pages = {
            "pt": (root / "index.html").read_text(encoding="utf-8"),
            "es": (root / "es/index.html").read_text(encoding="utf-8"),
        }
        cls.manifest = json.loads((root / "data/acervo/manifest.json").read_text(encoding="utf-8"))
        cls.manifest["series_content"] = {}
        for name in (
            "editorial-seda-ensaios.json",
            "editorial-escultura-fotografia-moda.json",
            "editorial-laberintos-ninos.json",
            "editorial-proyectos-literatura.json",
        ):
            payload = json.loads((root / "data/acervo" / name).read_text(encoding="utf-8"))
            cls.manifest["series_content"].update(payload["series"])
        cls.pt_editorial = json.loads(
            (root / "data/acervo/editorial-literatura-critica.json").read_text(encoding="utf-8")
        )

    def render(self, language):
        editorial = self.pt_editorial if language == "pt" else None
        return render_page(self.pages[language], self.manifest, language, editorial)

    def test_loads_editorial_series_for_a_regenerated_manifest(self):
        manifest = {"assets": []}

        loaded = load_series_editorial(manifest, Path(__file__).resolve().parents[1] / "data/acervo")

        self.assertIn("Ensayos", loaded["series_content"])
        self.assertIn("Proyectos Especiales/Master Taxi", loaded["series_content"])
        self.assertIn("Literatura/Ficción/El Nombre", loaded["series_content"])

    def test_applies_portuguese_editorial_overrides_to_criticism(self):
        page = '''<section id="critica"><p class="literatura-intro">Spanish intro</p><article id="lit-example"><p class="literatura-excerpt">Spanish excerpt</p><div class="literatura-full"><p>Spanish body</p></div></article></section>'''
        editorial = {
            "intro": "Introdução em português.",
            "articles": {
                "lit-example": {
                    "excerpt": "Resumo em português.",
                    "paragraphs": ["Primeiro parágrafo.", "Segundo parágrafo."],
                }
            },
        }

        rendered = apply_pt_editorial(page, editorial)

        self.assertIn("Introdução em português.", rendered)
        self.assertIn("Resumo em português.", rendered)
        self.assertIn("Primeiro parágrafo.", rendered)
        self.assertIn("Segundo parágrafo.", rendered)
        self.assertNotIn("Spanish", rendered)

    def test_tab_script_synchronizes_editorial_copy(self):
        script = (Path(__file__).resolve().parents[1] / "js/gallery-tabs.js").read_text()

        self.assertIn("data-series-copy", script)
        self.assertIn("series-copy-display", script)

    def test_renders_manifest_order_and_published_paths(self):
        html = render_slides(
            [asset("img/Seda/SEDA/02.jpg", "Dois"), asset("img/Seda/SEDA/10.jpg", "Dez")],
            "pt",
            visible_captions=True,
        )

        self.assertLess(html.index("02.jpg"), html.index("10.jpg"))
        self.assertIn('src="img/images/Seda/SEDA/02.jpg"', html)
        self.assertIn("Técnica mista", html)

    def test_omits_visible_captions_for_fish(self):
        html = render_slides([asset("img/Peces/01.jpg", "Peixe 1")], "pt", visible_captions=False)

        self.assertNotIn("gallery-caption", html)
        self.assertIn('alt="Peixe 1 — Fabio Crisanti"', html)

    def test_spanish_page_uses_parent_relative_asset_paths(self):
        html = render_slides([asset("img/Peces/01.jpg")], "es", visible_captions=False)

        self.assertIn('src="../img/images/Peces/01.jpg"', html)

    def test_series_copy_is_bound_to_its_tab_target(self):
        html = render_series_copy(
            "ensayos-urubus",
            {"pt": ["Primeiro parágrafo.", "Segundo parágrafo."], "es": ["Primero."]},
            "pt",
        )

        self.assertIn('data-series-copy="ensayos-urubus"', html)
        self.assertIn("<p>Primeiro parágrafo.</p>", html)
        self.assertIn("<p>Segundo parágrafo.</p>", html)

    def test_long_series_copy_uses_accessible_expansion(self):
        html = render_series_copy("vlak", {"pt": ["Um", "Dois", "Três"]}, "pt")

        self.assertIn("<details", html)
        self.assertIn("Ler texto completo", html)

    def test_renders_structured_fiction_sections(self):
        content = {"sections": [{"title": {"pt": "Prólogo"}, "pt": ["Texto do prólogo."]}]}

        html = render_series_copy("ficcao-el-nombre", content, "pt")

        self.assertIn("<h4>Prólogo</h4>", html)
        self.assertIn("Texto do prólogo.", html)

    def test_updates_only_the_target_carousel_track(self):
        page = '<div id="gallery-carousel-target"><div class="gallery-track"><div>old</div></div></div><div id="other">keep</div>'

        rendered = update_carousel(page, "gallery-carousel-target", [asset("img/Seda/SEDA/01.jpg")], "pt", True)

        self.assertIn("img/images/Seda/SEDA/01.jpg", rendered)
        self.assertNotIn(">old<", rendered)
        self.assertIn('<div id="other">keep</div>', rendered)

    def test_clones_tabbed_gallery_with_hidden_accessible_panel(self):
        page = '''<section id="ensayos"><div class="gallery-tabs"><button class="gallery-tab" data-target="ensayos-base">Base</button></div><div id="gallery-carousel-ensayos-base" data-gallery-group="ensayos"><div class="gallery-track"></div></div></section>'''

        rendered = clone_tabbed_gallery(page, "ensayos", "ensayos-base", "ensayos-gatos", "Gatos", [asset("img/Ensayos/Gatos/01.jpg")], "pt")

        self.assertIn('data-target="ensayos-gatos"', rendered)
        self.assertIn('id="gallery-carousel-ensayos-gatos"', rendered)
        self.assertIn("hidden", rendered)
        self.assertIn("img/images/Ensayos/Gatos/01.jpg", rendered)

    def test_bilingual_standalone_vlak_keeps_video_then_17_manifest_images(self):
        for language in ("pt", "es"):
            with self.subTest(language=language):
                section = BeautifulSoup(self.render(language), "html.parser").find(id="juego-del-tren")
                slides = section.select(".gallery-track > .gallery-slide")
                self.assertIsNotNone(slides[0].select_one("video.gallery-video"))
                self.assertEqual(17, len(section.select(".gallery-slide .gallery-img")))

    def test_master_taxi_renders_synopsis_but_keeps_dinamica_document(self):
        panel = BeautifulSoup(self.render("pt"), "html.parser").find(
            id="gallery-carousel-proyectos-especiales-master-taxi"
        )

        self.assertIsNotNone(panel.select_one(".master-taxi-synopsis"))
        document_names = [node.get_text(" ", strip=True) for node in panel.select(".project-document__name")]
        self.assertTrue(any("Dinámica" in name for name in document_names))
        self.assertFalse(any("Sinópsis" in name for name in document_names))

    def test_master_taxi_synopsis_rendering_is_idempotent(self):
        page = '''<div id="panel"><div class="gallery-viewport"></div>
<section class="project-documents"><div class="project-documents__list">
<article class="project-document"><span class="project-document__name">Master Taxi Dinámica</span></article>
<article class="project-document"><span class="project-document__name">Master Taxi Sinópsis</span></article>
</div></section></div>'''
        content = {
            "title": {"pt": "Sinopse"},
            "sections": [{"title": {"pt": "O Jogo"}, "pt": ["Texto."]}],
        }
        first_soup = BeautifulSoup(page, "html.parser")
        render_master_taxi_synopsis(first_soup.find(id="panel"), content, "pt")
        first = str(first_soup)
        second_soup = BeautifulSoup(first, "html.parser")
        render_master_taxi_synopsis(second_soup.find(id="panel"), content, "pt")

        self.assertEqual(first, str(second_soup))

    def test_el_nombre_order_is_title_gallery_copy_and_preserves_flores(self):
        fiction = str(BeautifulSoup(self.render("pt"), "html.parser").find(id="ficcao"))

        self.assertIn('data-rendered-series-copy="ficcao-el-nombre"', fiction)
        title = fiction.index(">El Nombre<")
        gallery = fiction.index('id="gallery-carousel-ficcao-el-nombre"')
        copy = fiction.index('data-rendered-series-copy="ficcao-el-nombre"')
        self.assertLess(title, gallery)
        self.assertLess(gallery, copy)
        self.assertIn('id="gallery-carousel-ficcao-flores"', fiction)

    def test_approved_ensayos_and_laberintos_leads_are_rendered_in_both_languages(self):
        expected = {
            "pt": {
                "ensayos": "Séries de ensaios fotográficos que exploram o cotidiano, os gestos e as texturas do mundo ao redor — registros íntimos onde a câmera se torna instrumento de meditação visual.",
                "los-laberintos": "Sistemas visuais, quebra-cabeças e jogos conceituais. Os labirintos de nomear e numerar.",
            },
            "es": {
                "ensayos": "Series de ensayos fotográficos que exploran lo cotidiano, los gestos y las texturas del mundo que nos rodea — registros íntimos en los que la cámara se convierte en un instrumento de meditación visual.",
                "los-laberintos": "Sistemas visuales, puzles y juegos conceptuales. Los laberintos de nombrar y numerar.",
            },
        }
        for language, sections in expected.items():
            soup = BeautifulSoup(self.render(language), "html.parser")
            for section_id, copy in sections.items():
                with self.subTest(language=language, section=section_id):
                    self.assertEqual(copy, soup.find(id=section_id).select_one(".series-lead").get_text(strip=True))

    def test_approved_addis_and_spanish_criticism_corrections_are_rendered(self):
        for language in ("pt", "es"):
            with self.subTest(language=language):
                lead = BeautifulSoup(self.render(language), "html.parser").find(id="la-escultura").select_one(
                    ".series-lead"
                )
                self.assertNotIn("poétic", lead.get_text().casefold())
        criticism = BeautifulSoup(self.render("es"), "html.parser").find(id="critica")
        self.assertIn("en mi obra", criticism.select_one(".literatura-intro").get_text())
        self.assertNotIn("Em mi obra", criticism.select_one(".literatura-intro").get_text())

    def test_seis_animales_uses_readable_materials_from_its_ficha(self):
        for language, expected in (
            ("pt", "Materiais: Aço. Madeira. Espuma. Poliéster. Acrílicos. Aerógrafo. Papel machê. Lã."),
            ("es", "Materiales: Acero. Madera. Gomaespuma. Poliéster. Acrílicos. Aerógrafo. Cartapesta. Lana."),
        ):
            with self.subTest(language=language):
                section = BeautifulSoup(self.render(language), "html.parser").find(
                    id="gallery-carousel-los-ninos-seis-animales"
                )
                meta = section.select_one(".gallery-meta")
                self.assertIsNotNone(meta)
                self.assertEqual(expected, meta.get_text(strip=True))

    def test_regenerated_manifest_source_captions_are_localized_during_render(self):
        expected = {
            "pt": "Vista geral da série",
            "es": "Vista general de la seria",
        }
        for language, title in expected.items():
            with self.subTest(language=language):
                panel = BeautifulSoup(self.render(language), "html.parser").find(
                    id="gallery-carousel-seda"
                )
                rendered_title = panel.select_one(".gallery-title")
                self.assertIsNotNone(rendered_title)
                self.assertEqual(title, rendered_title.get_text(strip=True))


if __name__ == "__main__":
    unittest.main()
