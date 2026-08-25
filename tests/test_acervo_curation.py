import unittest

from tools.acervo.curate import (
    apply_fichas,
    localize_caption,
    parse_caption,
    split_numbered_entries,
)


class NumberedFichaTests(unittest.TestCase):
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


if __name__ == "__main__":
    unittest.main()
