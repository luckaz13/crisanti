import tempfile
import unittest
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile

from tools.acervo.extract_documents import extract_docx, extract_pptx


WORD_XML = """<?xml version="1.0" encoding="UTF-8"?>
<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">
  <w:body>
    <w:p><w:r><w:t>Texto com acento: Emulsión</w:t></w:r></w:p>
    <w:tbl>
      <w:tr>
        <w:tc><w:p><w:r><w:t>01</w:t></w:r></w:p></w:tc>
        <w:tc><w:p><w:r><w:t>Obra I</w:t></w:r></w:p></w:tc>
      </w:tr>
      <w:tr>
        <w:tc><w:p><w:r><w:t>02</w:t></w:r></w:p></w:tc>
        <w:tc><w:p/></w:tc>
      </w:tr>
    </w:tbl>
  </w:body>
</w:document>
"""

SLIDE_XML = """<?xml version="1.0" encoding="UTF-8"?>
<p:sld xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main"
       xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main">
  <p:cSld><a:t>{text}</a:t></p:cSld>
</p:sld>
"""


class DocumentExtractionTests(unittest.TestCase):
    def test_docx_preserves_paragraphs_and_table_cells(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "ficha.docx"
            with ZipFile(path, "w", ZIP_DEFLATED) as archive:
                archive.writestr("word/document.xml", WORD_XML)

            result = extract_docx(path)

            self.assertEqual(result.status, "ok")
            self.assertIn("Texto com acento: Emulsión", result.paragraphs)
            self.assertEqual(result.tables, [[['01', 'Obra I'], ['02', '']]])

    def test_pptx_uses_numeric_slide_order(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "slides.pptx"
            with ZipFile(path, "w", ZIP_DEFLATED) as archive:
                archive.writestr("ppt/slides/slide10.xml", SLIDE_XML.format(text="Décimo"))
                archive.writestr("ppt/slides/slide2.xml", SLIDE_XML.format(text="Segundo"))
                archive.writestr("ppt/slides/slide1.xml", SLIDE_XML.format(text="Primeiro"))

            result = extract_pptx(path)

            self.assertEqual(result.status, "ok")
            self.assertEqual(result.slides, [["Primeiro"], ["Segundo"], ["Décimo"]])


if __name__ == "__main__":
    unittest.main()
