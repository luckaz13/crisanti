import unittest

from tools.acervo.curate import (
    apply_fichas,
    localize_caption,
    localize_pt_text,
    parse_caption,
    split_numbered_entries,
)
from tools.acervo.localize_manifest_pt import localize_manifest_pt


class NumberedFichaTests(unittest.TestCase):
    def test_manifest_localization_updates_caption_and_alt_idempotently(self):
        manifest = {
            "assets": [
                {
                    "caption": {"pt": {"title": "Boceto", "details": "(Detalle)"}},
                    "alt": {"pt": "Boceto — (Detalle) — Fabio Crisanti"},
                }
            ]
        }

        once = localize_manifest_pt(manifest)
        twice = localize_manifest_pt(once)

        self.assertEqual("Esboço", once["assets"][0]["caption"]["pt"]["title"])
        self.assertEqual("Esboço — (Detalhe) — Fabio Crisanti", once["assets"][0]["alt"]["pt"])
        self.assertEqual(once, twice)

    def test_localizes_recurring_documentary_labels(self):
        cases = {
            "Vista general de la seria": "Vista geral da série",
            "(Detalle de rabiola)": "(Detalhe da rabiola)",
            'Boceto para vestido desde la serie "Seda"': 'Esboço para vestido da série "Seda"',
            "Retiro de tapa y página 1": "Verso da capa e página 1",
            "Páginas 28 y 29": "Páginas 28 e 29",
            "Contratapa": "Contracapa",
            "Tapa del cuaderno": "Capa do cuaderno",
            "ContratapaAcrílicos": "Contracapa. Acrílicos",
            "TapaAcrílicos": "Capa. Acrílicos",
            "Boceto tapa de caixa": "Esboço capa da caixa",
            "0.80mContratapa": "0.80mContracapa",
        }

        for source, expected in cases.items():
            with self.subTest(source=source):
                self.assertEqual(expected, localize_pt_text(source))

    def test_localizes_recurring_materials_and_techniques(self):
        source = "Materiales:AceroMaderaGomaespumaPoliesterAcrílicosAerógrafoCartapestaLana"

        localized = localize_pt_text(source)

        self.assertEqual(
            "Materiais:AçoMadeiraEspumaPoliésterAcrílicosAerógrafoPapel machêLã",
            localized,
        )

    def test_localizes_concatenated_sculpture_materials(self):
        source = "Papeles Metalizados: Cobre, Oro, Perla. CartapestaLienzo CrudoHilos de AlgodónCorcho"

        localized = localize_pt_text(source)

        self.assertEqual(
            "Papéis metalizados: Cobre, Ouro, Pérola. Papel machêTela cruaFios de AlgodãoCortiça",
            localized,
        )

    def test_localizes_photographic_and_editorial_descriptions(self):
        cases = {
            "Emulsión fotográfica sobre lienzo imprimado": "Emulsão fotográfica sobre tela preparada",
            "Imágenes del Calendario": "Imagens do Calendario",
            "Copias fotográficas tomadas de la serie Exilio": "Cópias fotográficas feitas a partir da série Exilio",
            "Acrílicos sobre papel de seda y collage. Diseño digital": "Acrílicos sobre papel de seda e colagem. Design digital",
        }

        for source, expected in cases.items():
            with self.subTest(source=source):
                self.assertEqual(expected, localize_pt_text(source))

    def test_splits_entries_without_treating_dimensions_as_numbers(self):
        text = (
            '01"Seda I"20210.30m x 0.50mAcrílico sobre papel de sedaCollage '
            '02"Seda II"20210.40m x 0.30mAcrílico sobre papel de seda'
        )

        self.assertEqual(
            split_numbered_entries(text),
            {
                "01": '"Seda I"20210.30m x 0.50mAcrílico sobre papel de sedaCollage',
                "02": '"Seda II"20210.40m x 0.30mAcrílico sobre papel de seda',
            },
        )

    def test_accepts_unquoted_entry_titles(self):
        self.assertEqual(
            split_numbered_entries("06Ideografía China I 07Ideografía China II"),
            {"06": "Ideografía China I", "07": "Ideografía China II"},
        )

    def test_splits_entry_number_joined_to_previous_year(self):
        self.assertEqual(
            split_numbered_entries('01“Emulsión 1”202502“Emulsión 2”2025'),
            {"01": '“Emulsión 1”2025', "02": '“Emulsión 2”2025'},
        )

    def test_parses_title_year_and_readable_metadata(self):
        caption = parse_caption(
            '“Huesos I”2025Toma directa con teléfono.Collage e intervención digital.'
        )

        self.assertEqual(caption["title"], "Huesos I")
        self.assertEqual(caption["year"], "2025")
        self.assertEqual(
            caption["details"],
            "Toma directa con teléfono. Collage e intervención digital.",
        )

    def test_separates_joined_dimensions_and_materials(self):
        caption = parse_caption(
            '"Seda I"20210.30m x 0.50mAcrílico sobre papel de sedaCollageBambú'
        )

        self.assertEqual(
            caption["details"],
            "0.30m x 0.50m. Acrílico sobre papel de seda. Collage. Bambú",
        )

    def test_applies_same_directory_ficha_by_filename_number(self):
        manifest = {
            "assets": [
                {
                    "path": "img/Ensayos/Gatos/01.jpg",
                    "filename": "01.jpg",
                    "caption": {"source": None, "es": None, "pt": None},
                }
            ]
        }
        documents = [
            {
                "path": "img/Ensayos/Gatos/Ficha Ensayos Gatos.docx",
                "paragraphs": ['01“Gatos I”2026Toma directa teléfono.'],
            }
        ]

        enriched = apply_fichas(manifest, documents)

        self.assertEqual(
            enriched["assets"][0]["caption"]["source"],
            {"title": "Gatos I", "year": "2026", "details": "Toma directa teléfono."},
        )

    def test_localizes_and_corrects_recurring_metadata(self):
        source = {
            "title": "Huesos I",
            "year": "2025",
            "details": "Toma directa teléfono. Collage e intervención digital.",
        }

        es, pt = localize_caption(source)

        self.assertEqual(es["title"], "Huesos I")
        self.assertEqual(
            es["details"],
            "Toma directa con teléfono. Collage e intervención digital.",
        )
        self.assertEqual(pt["title"], "Ossos I")
        self.assertEqual(
            pt["details"],
            "Captura direta com telefone. Colagem e intervenção digital.",
        )

    def test_corrects_mixed_portuguese_material_terms(self):
        source = {
            "title": "Seda X",
            "year": "2021",
            "details": "0.30m x 0.50m. Acrílico sobre papel de seda. Collage. Carimbo. Bambú.",
        }

        es, pt = localize_caption(source)

        self.assertIn("Collage. Sello. Bambú.", es["details"])
        self.assertIn("Colagem. Carimbo. Bambu.", pt["details"])

    def test_localizes_sculpture_techniques_and_locations(self):
        source = {
            "title": "Pez IV",
            "year": "2024",
            "details": "Materiales: Bambú. Poliester. Cemento de contacto. Algodón. Playa central de Garopaba, Brasil.",
        }

        es, pt = localize_caption(source)

        self.assertIn("Poliéster", es["details"])
        self.assertEqual(pt["title"], "Peixe IV")
        self.assertIn("Materiais: Bambu", pt["details"])
        self.assertIn("Praia central de Garopaba", pt["details"])

    def test_localizes_children_illustration_metadata(self):
        source = {"title": "Ilustración página 6", "year": None, "details": "Acrílicos sobre papel de seda y collage. Diseño digital"}

        _, pt = localize_caption(source)

        self.assertEqual(pt["title"], "Ilustração página 6")
        self.assertEqual(pt["details"], "Acrílicos sobre papel de seda e colagem. Design digital")


if __name__ == "__main__":
    unittest.main()
