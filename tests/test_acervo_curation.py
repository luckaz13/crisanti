import unittest

from tools.acervo.curate import apply_fichas, parse_caption, split_numbered_entries


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


if __name__ == "__main__":
    unittest.main()
