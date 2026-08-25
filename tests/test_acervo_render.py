import unittest
from pathlib import Path

from tools.acervo.render_galleries import (
    clone_tabbed_gallery,
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


if __name__ == "__main__":
    unittest.main()
