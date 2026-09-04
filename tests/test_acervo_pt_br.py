import json
import tempfile
import unittest
from pathlib import Path

from bs4 import BeautifulSoup

from tools.acervo.audit_pt_br import audit_pt_br_html, find_spanish_residuals


ROOT = Path(__file__).resolve().parents[1]


class PtBrAuditTests(unittest.TestCase):
    def test_critica_editorial_covers_source_with_only_reviewed_merges(self):
        editorial = json.loads(
            (ROOT / "data/acervo/editorial-literatura-critica.json").read_text(
                encoding="utf-8"
            )
        )
        spanish = BeautifulSoup(
            (ROOT / "es/index.html").read_text(encoding="utf-8"), "html.parser"
        )

        source_counts = {
            article["id"]: len(article.select(".literatura-full p"))
            for article in spanish.select("#critica article[id]")
        }
        final_counts = {
            article_id: len(article["paragraphs"])
            for article_id, article in editorial["articles"].items()
        }
        expected_final_counts = {
            "lit-celso-ricardo": 16,
            "lit-el-nombre": 4,
            "lit-flores": 5,
            "lit-fotografia-y-escultura": 8,
            "lit-hugo-franca": 13,
            "lit-juliana-hoffmann": 15,
            "lit-mauricio-capellari": 8,
            "lit-mitica-gaya": 13,
        }

        self.assertEqual(86, sum(source_counts.values()))
        self.assertEqual(expected_final_counts, final_counts)
        self.assertEqual(82, sum(final_counts.values()))
        translated_texts = [editorial["intro"]]
        for article in editorial["articles"].values():
            self.assertEqual(article["excerpt"], article["paragraphs"][0])
            translated_texts.extend([article["excerpt"], *article["paragraphs"]])
        self.assertEqual([], find_spanish_residuals(translated_texts))

    def test_detects_spanish_exhibition_caption(self):
        findings = find_spanish_residuals(
            ["Las fotografía fueron tomadas de la serie del autor, expuesta en el Consulado."]
        )

        self.assertEqual(1, len(findings))
        self.assertIn("spanish-exhibition-caption", findings[0].rules)

    def test_detects_known_spanish_caption_phrases(self):
        findings = find_spanish_residuals(
            [
                "Vista general de la serie",
                "Boceto para vestido desde la serie Seda",
                "Materiales: Madera, Cartón y Acrílicos",
                "Acrílicos sobre papel de seda y collage",
            ]
        )

        self.assertEqual(4, len(findings))

    def test_detects_full_spanish_prose(self):
        findings = find_spanish_residuals(
            ["Así pendulamos entre una afectación patética y la degradación de la materia que intentamos registrar desde ella."]
        )

        self.assertEqual(1, len(findings))
        self.assertIn("spanish-prose", findings[0].rules)

    def test_allows_approved_original_titles_only(self):
        findings = find_spanish_residuals(
            ["El Calendario", "La Cocina", "El Teléfono", "Juego del Tren", "La Fuente y los Simios"]
        )

        self.assertEqual([], findings)

    def test_audits_visible_text_and_editorial_attributes(self):
        with tempfile.TemporaryDirectory() as directory:
            page = Path(directory) / "index.html"
            page.write_text(
                '<html lang="pt-BR"><body><h3>Vista general</h3><img alt="Boceto para obra"><script>"Materiales"</script></body></html>',
                encoding="utf-8",
            )

            report = audit_pt_br_html(page, scope_selector="body")

            self.assertEqual(2, len(report.findings))
            self.assertEqual([], report.outside_scope_findings)

    def test_separates_required_scope_from_preexisting_residuals(self):
        with tempfile.TemporaryDirectory() as directory:
            page = Path(directory) / "index.html"
            page.write_text(
                '<main><section id="critica"><p>Vista general</p></section>'
                '<section><img alt="Boceto para obra"></section></main>',
                encoding="utf-8",
            )

            report = audit_pt_br_html(page, scope_selector="#critica")

            self.assertEqual(["Vista general"], [item.text for item in report.findings])
            self.assertEqual(
                ["Boceto para obra"],
                [item.text for item in report.outside_scope_findings],
            )

    def test_portuguese_critica_has_no_unintended_spanish(self):
        report = audit_pt_br_html(ROOT / "index.html")

        self.assertEqual([], report.findings)
        self.assertEqual(
            [
                "2022 Colagem, papel de seda, acrílicos, corcho, yute.",
                "Gráficos descritivos de elementos del universo del cuento.",
                "Cuaderno 3 — 2022 Colagem, papel de seda, acrílicos, corcho, "
                "yute. — Fabio Crisanti",
                "Gráficos descritivos de elementos del universo del cuento. "
                "— Fabio Crisanti",
            ],
            [item.text for item in report.outside_scope_findings],
        )


if __name__ == "__main__":
    unittest.main()
