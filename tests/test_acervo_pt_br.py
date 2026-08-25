import tempfile
import unittest
from pathlib import Path

from tools.acervo.audit_pt_br import audit_pt_br_html, find_spanish_residuals


class PtBrAuditTests(unittest.TestCase):
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

            report = audit_pt_br_html(page)

            self.assertEqual(2, len(report.findings))


if __name__ == "__main__":
    unittest.main()
